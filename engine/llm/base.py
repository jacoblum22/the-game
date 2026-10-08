"""Provider-neutral model interface: roles, packets, call records, schema validation and the re-ask rule.

contracts/model-calls.md: every role call is one structured-output request against a JSON Schema the engine
builds per turn. The engine re-validates every response; an invalid one is re-asked once naming the failure,
then the rule's default applies, else the call fails (`ModelInvalid`) and the turn writes nothing.
"""

from __future__ import annotations

import hashlib
import json
import time
from collections.abc import Callable, Mapping
from enum import StrEnum
from typing import Any, Protocol

from pydantic import BaseModel, Field


class Role(StrEnum):
    INTERPRET = "interpret"
    READER = "reader"
    FRAMER = "framer"
    WORLD = "world"
    DIRECTOR = "director"
    NARRATOR = "narrator"
    CHECKER = "checker"
    PROPOSER = "proposer"  # PR-12-10 rung 3: one typed candidate answer (spec 008 part B)
    LOCATOR = "locator"  # PR-12-11 step 1: which passage a player's report means (spec 012)


class Outcome(StrEnum):
    OK = "ok"
    INVALID_REASKED = "invalid_reasked"
    DEFAULTED = "defaulted"
    REFUSED = "refused"
    ERROR = "error"


class RoleModel(BaseModel):
    """One `GameConfig.models` entry (contracts/engine-api.md)."""

    provider: str = "gemini"
    model: str = "gemini-3.8-flash"
    thinking: str = "low"


class ModelCallRecord(BaseModel):
    """One row of `model_calls` (data-model.md §1), plus `seq` and `attempt` (the replay key is
    (turn_id, role, seq, attempt)).

    `seq` numbers the calls of one role within one turn (0, 1, 2 … in call order: several Framer beats, a
    "change", a Narrator redraft), so two calls of a role in a turn never share a key. Rows written before
    `seq` existed read as seq 0. `call_id` is deterministic (engine/ids.py: no uuid),
    `call.<turn_id|pre>.<role>.<seq>.<attempt>`, so a replayed turn record lists the same call ids.
    """

    call_id: str = ""
    turn_id: str | None = None
    role: Role
    seq: int = 0
    attempt: int = 0
    provider: str
    model_id: str
    schema_hash: str
    request: dict[str, Any] = Field(default_factory=dict)
    # {"data": parsed JSON or None, "text": raw text or None, "error": message or None}, plus "rejected": the
    # validation failures when `call_role` refused the response (absent on accepted rows and older rows)
    response: dict[str, Any] | None = None
    tokens_in_cached: int = 0
    tokens_in: int = 0  # uncached input tokens (prompt tokens minus cached)
    tokens_out: int = 0  # visible output tokens
    tokens_thinking: int = 0  # billed at the output rate
    cost_usd: float = 0.0
    latency_ms: int = 0
    outcome: Outcome = Outcome.OK


class CallResult(BaseModel):
    data: Any = None  # the parsed response (a dict once validated)
    record: ModelCallRecord
    attempts: int = 1
    defaulted: bool = False


# ---------------------------------------------------------------- errors (contracts/engine-api.md)


class ModelError(Exception):
    def __init__(self, message: str, record: ModelCallRecord | None = None):
        super().__init__(message)
        self.record = record


class ModelUnavailable(ModelError):
    """Provider error or timeout after retries; the turn rolls back and is retryable."""


class ModelRefused(ModelError):
    """Provider safety refusal; logged under moderation, never under consistency."""


class MissingKey(ModelError):
    """No GEMINI_API_KEY in the environment or .env."""


class ReplayDivergence(ModelError):
    """A replay asked for a call that was not recorded, or with a different schema."""


class ModelInvalid(ModelError):
    """The response failed validation twice and the field has no rule default; nothing is written."""


# ---------------------------------------------------------------- packet

SECTION_TITLES = {
    "instructions": "ROLE INSTRUCTIONS",
    "core": "CORE RULES",
    "cards": "RULE CARDS",
    "view": "NARRATOR VIEW",
    "exchanges": "RECENT EXCHANGES",
    "message": "THIS MESSAGE",
    "reask": "CORRECTION",
}


class Packet(BaseModel):
    """The model's input, stable sections first for prompt caching (contracts/model-calls.md, Packet order)."""

    instructions: str = ""
    core: str = ""
    cards: list[str] = Field(default_factory=list)  # ≤12 per call
    view: str = ""
    exchanges: list[str] = Field(default_factory=list)  # last 4, verbatim
    message: str = ""  # this message, verbatim (always last)
    reask: str | None = None  # set only on the re-ask attempt

    def sections(self, *, include_instructions: bool = True) -> list[tuple[str, str]]:
        body = [
            ("instructions", self.instructions if include_instructions else ""),
            ("core", self.core),
            ("cards", "\n\n".join(self.cards)),
            ("view", self.view),
            ("exchanges", "\n\n".join(self.exchanges)),
            ("message", self.message),
            ("reask", self.reask or ""),
        ]
        return [(k, v) for k, v in body if v.strip() or k == "message"]

    def render(self, *, include_instructions: bool = True) -> str:
        parts = [f"[{SECTION_TITLES[k]}]\n{v}" for k, v in self.sections(include_instructions=include_instructions)]
        return "\n\n".join(parts)

    def with_reask(self, failures: list[str]) -> Packet:
        shown = "; ".join(failures[:5]) + (f"; and {len(failures) - 5} more" if len(failures) > 5 else "")
        note = f"Your previous answer was rejected: {shown}. Answer again, following the schema exactly."
        return self.model_copy(update={"reask": note})


# ---------------------------------------------------------------- protocol


class StructuredModel(Protocol):
    provider: str

    def fill(
        self, role: Role, schema: dict[str, Any], packet: Packet, *, turn_id: str | None, attempt: int,
        seq: int = 0,
    ) -> CallResult:
        """One request. Returns the parsed response unvalidated; raises ModelUnavailable / ModelRefused."""
        ...


Recorder = Callable[[ModelCallRecord], None]


class CallSequence:
    """Hands out `seq` per (turn_id, role): 0, 1, 2 … in call order.

    Deterministic: a replay makes the same role calls in the same order, so it asks for the same keys.
    `call_role` finds one through its recorder: the recorder itself, or the object a bound-method recorder
    belongs to (`TurnContext.record_call` -> the TurnContext), when it has `next_call_seq(turn_id, role)`.
    """

    def __init__(self) -> None:
        self._next: dict[tuple[str | None, str], int] = {}

    def next_call_seq(self, turn_id: str | None, role: Role | str) -> int:
        key = (turn_id, Role(role).value)
        n = self._next.get(key, 0)
        self._next[key] = n + 1
        return n


def next_seq(recorder: Any, turn_id: str | None, role: Role) -> int:
    """The next `seq` from the recorder's sequence (see CallSequence); 0 when it has none."""
    for owner in (recorder, getattr(recorder, "__self__", None)):
        fn: Callable[[str | None, Role], int] | None = getattr(owner, "next_call_seq", None)
        if callable(fn):
            return int(fn(turn_id, role))
    return 0


def schema_hash(schema: Mapping[str, Any]) -> str:
    """sha256 of the schema's canonical JSON (sorted keys, no whitespace)."""
    canon = json.dumps(schema, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


def call_id(turn_id: str | None, role: Role, attempt: int, seq: int = 0) -> str:
    return f"call.{turn_id or 'pre'}.{role.value}.{seq}.{attempt}"


def new_record(
    role: Role, schema: Mapping[str, Any], *, provider: str, model_id: str, turn_id: str | None, attempt: int,
    request: dict[str, Any] | None = None, seq: int = 0,
) -> ModelCallRecord:
    return ModelCallRecord(
        call_id=call_id(turn_id, role, attempt, seq), turn_id=turn_id, role=role, seq=seq, attempt=attempt,
        provider=provider, model_id=model_id, schema_hash=schema_hash(schema), request=request or {},
    )


def _stamp(rec: ModelCallRecord, seq: int) -> ModelCallRecord:
    """Make sure a model's record carries the call's `seq` (and the matching call_id)."""
    want = call_id(rec.turn_id, Role(rec.role), rec.attempt, seq)
    if rec.seq == seq and rec.call_id == want:
        return rec
    return rec.model_copy(update={"seq": seq, "call_id": want})


class Stopwatch:
    def __init__(self) -> None:
        self.t0 = time.perf_counter()

    def ms(self) -> int:
        return int((time.perf_counter() - self.t0) * 1000)


# ---------------------------------------------------------------- JSON Schema subset


def resolve(node: Any, root: Mapping[str, Any]) -> dict[str, Any]:
    """Follow local `$ref`s (`#/$defs/X`, `#/definitions/X`)."""
    seen = 0
    while isinstance(node, Mapping) and "$ref" in node:
        ref = node["$ref"]
        if not isinstance(ref, str) or not ref.startswith("#/"):
            raise ValueError(f"unsupported $ref {ref!r}")
        target: Any = root
        for part in ref[2:].split("/"):
            target = target[part.replace("~1", "/").replace("~0", "~")]
        extra = {k: v for k, v in node.items() if k != "$ref"}
        node = {**target, **extra} if extra else target
        seen += 1
        if seen > 50:
            raise ValueError("$ref cycle")
    return dict(node) if isinstance(node, Mapping) else {}


_TYPES: dict[str, Callable[[Any], bool]] = {
    "object": lambda v: isinstance(v, dict),
    "array": lambda v: isinstance(v, list),
    "string": lambda v: isinstance(v, str),
    "boolean": lambda v: isinstance(v, bool),
    "null": lambda v: v is None,
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: isinstance(v, int | float) and not isinstance(v, bool),
}


def _short(options: list[Any]) -> str:
    head = ", ".join(repr(o) for o in options[:10])
    return f"[{head}{', …' if len(options) > 10 else ''}]"


def _check(v: Any, node: Any, root: Mapping[str, Any], path: str, errs: list[str]) -> None:
    node = resolve(node, root)
    if "const" in node and v != node["const"]:
        errs.append(f"{path}: must be {node['const']!r}")
        return
    if "enum" in node and v not in node["enum"]:
        errs.append(f"{path}: {v!r} is not one of {_short(list(node['enum']))}")
        return
    for key in ("anyOf", "oneOf"):
        if key in node:
            results = []
            for opt in node[key]:
                sub: list[str] = []
                _check(v, opt, root, path, sub)
                results.append(sub)
            passing = sum(1 for r in results if not r)
            if passing == 0:
                errs.extend(min(results, key=len))
                return
            if key == "oneOf" and passing > 1:
                errs.append(f"{path}: matches more than one allowed form")
                return
    for opt in node.get("allOf", []):
        _check(v, opt, root, path, errs)
    t = node.get("type")
    if t is not None:
        types = t if isinstance(t, list) else [t]
        if not any(_TYPES.get(x, lambda _v: True)(v) for x in types):
            errs.append(f"{path}: expected {'/'.join(types)}, got {type(v).__name__}")
            return
    if isinstance(v, dict):
        props = node.get("properties", {})
        for k in node.get("required", []):
            if k not in v:
                errs.append(f"{path}: missing required field {k!r}")
        extra = node.get("additionalProperties", True)
        for k, item in v.items():
            if k in props:
                _check(item, props[k], root, f"{path}.{k}", errs)
            elif extra is False:
                errs.append(f"{path}: unexpected field {k!r}")
            elif isinstance(extra, Mapping):
                _check(item, extra, root, f"{path}.{k}", errs)
    elif isinstance(v, list):
        if "maxItems" in node and len(v) > node["maxItems"]:
            errs.append(f"{path}: at most {node['maxItems']} items, got {len(v)}")
        if "minItems" in node and len(v) < node["minItems"]:
            errs.append(f"{path}: at least {node['minItems']} items, got {len(v)}")
        if "items" in node:
            for i, item in enumerate(v):
                _check(item, node["items"], root, f"{path}[{i}]", errs)
    elif isinstance(v, str):
        if "maxLength" in node and len(v) > node["maxLength"]:
            errs.append(f"{path}: longer than {node['maxLength']} characters")
        if "minLength" in node and len(v) < node["minLength"]:
            errs.append(f"{path}: shorter than {node['minLength']} characters")
    elif isinstance(v, int | float) and not isinstance(v, bool):
        if "minimum" in node and v < node["minimum"]:
            errs.append(f"{path}: below minimum {node['minimum']}")
        if "maximum" in node and v > node["maximum"]:
            errs.append(f"{path}: above maximum {node['maximum']}")


def validate(value: Any, schema: Mapping[str, Any]) -> list[str]:
    """Errors for `value` against the JSON Schema subset the engine builds; [] when valid.

    Supported: type (incl. lists), enum, const, properties, required, additionalProperties, items,
    minItems/maxItems, min/maxLength, minimum/maximum, anyOf, oneOf, allOf, local $ref.
    """
    errs: list[str] = []
    _check(value, schema, schema, "$", errs)
    return errs


# ---------------------------------------------------------------- the re-ask rule


def call_role(
    model: StructuredModel,
    role: Role,
    schema: dict[str, Any],
    packet: Packet,
    *,
    turn_id: str | None = None,
    recorder: Recorder | None = None,
    default: Mapping[str, Any] | Callable[[], Mapping[str, Any]] | None = None,
    check: Callable[[Any], list[str]] | None = None,
    seq: int | None = None,
) -> CallResult:
    """Ask, validate, re-ask once naming the failure, then the default, else ModelInvalid.

    rule: PR-01-2 (one re-ask naming the failure); contracts/model-calls.md (then the rule's default).
    `check` adds caller-side failures (e.g. an id that must exist) to the schema validation.
    Every call, including refused and failed ones, goes to `recorder`. `seq` (this role's call number in the
    turn) defaults to the recorder's `next_call_seq` (CallSequence), else 0.
    """
    if seq is None:
        seq = next_seq(recorder, turn_id, role)

    def emit(rec: ModelCallRecord) -> None:
        if recorder is not None:
            recorder(rec)

    current = packet
    for attempt in (0, 1):
        try:
            res = model.fill(role, schema, current, turn_id=turn_id, attempt=attempt, seq=seq)
        except ModelError as exc:
            if exc.record is not None:
                exc.record = _stamp(exc.record, seq)
                emit(exc.record)
            raise
        res = res.model_copy(update={"record": _stamp(res.record, seq)})
        errs = ["the response was not valid JSON"] if res.data is None else validate(res.data, schema)
        if not errs and check is not None:
            errs = check(res.data)
        if not errs:
            rec = res.record.model_copy(update={"outcome": Outcome.OK})
            emit(rec)
            return CallResult(data=res.data, record=rec, attempts=attempt + 1)
        # why it was refused, for every provider (a key old rows simply lack)
        rejected = {"response": {**(res.record.response or {}), "rejected": list(errs)}}
        if attempt == 0:
            emit(res.record.model_copy(update={"outcome": Outcome.INVALID_REASKED, **rejected}))
            current = packet.with_reask(errs)
            continue
        if default is not None:
            rec = res.record.model_copy(update={"outcome": Outcome.DEFAULTED, **rejected})
            emit(rec)
            data = dict(default() if callable(default) else default)
            return CallResult(data=data, record=rec, attempts=2, defaulted=True)
        rec = res.record.model_copy(update={"outcome": Outcome.ERROR, **rejected})
        emit(rec)
        raise ModelInvalid(f"{role.value}: invalid after one re-ask: {'; '.join(errs[:5])}", rec)
    raise AssertionError("unreachable")
