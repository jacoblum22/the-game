"""Gemini adapter (google-genai 2.25.0): one structured-output request per role call.

research.md R3. The schema goes in `response_json_schema`, converted to the subset Gemini accepts
(`engine.llm.gemini_schema`; the engine still validates against the original in `call_role`). Thinking is
always set explicitly (`thinking_level` for Gemini 3 models; `minimal` only where the model supports it). The
role instructions go in the system instruction and the rest of the packet, stable sections first, is one user
turn. `max_output_tokens` is per role and includes the thinking allowance (Gemini counts thought tokens
against it). Automatic function calling is disabled (no tools; it also silences the SDK's AFC warning).

Robustness (what a real response can look like): JSON in the text parts, possibly fenced or with stray prose
around it, else `response.parsed`; no candidates; a MAX_TOKENS cut (one retry at double the cap, usage of both
requests summed); a 400 from the server (the schema is resent looser: level 1 = enums as described strings,
level 2 = JSON mode with the schema in the instructions; a role that needed a looser level starts there for
the rest of the session); 408/429/5xx and network errors are retried with backoff, then `ModelUnavailable`;
safety blocks raise `ModelRefused`. Tests inject a fake client; nothing here is called without a real key.
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable, Mapping
from typing import Any

import httpx
from google.genai import errors, types

from engine.llm import budget
from engine.llm.base import (
    CallResult,
    MissingKey,
    ModelCallRecord,
    ModelRefused,
    ModelUnavailable,
    Outcome,
    Packet,
    Role,
    RoleModel,
    Stopwatch,
    new_record,
)
from engine.llm.env import get_key
from engine.llm.gemini_schema import convert

DEFAULT_MODEL = RoleModel()

_LEVELS = {
    "minimal": types.ThinkingLevel.MINIMAL,
    "low": types.ThinkingLevel.LOW,
    "medium": types.ThinkingLevel.MEDIUM,
    "high": types.ThinkingLevel.HIGH,
}
# Gemini 3 models that accept `minimal` (ai.google.dev gemini-3 guide); gemini-3.8-flash returns an error for
# it (its model page: "Thinking: low, medium, high"), so everything else gets `low` instead.
_MINIMAL_OK = ("gemini-3-flash", "gemini-3.1-flash-lite", "gemini-3-flash-lite")
# Pre-Gemini-3 models take a token budget instead of a level.
_BUDGETS = {"minimal": 0, "low": 1024, "medium": 8192, "high": 24576}

# Visible output per role (tokens), before the thinking allowance.
OUTPUT_TOKENS: dict[Role, int] = {
    Role.INTERPRET: 400,
    Role.READER: 800,
    Role.FRAMER: 1000,
    Role.WORLD: 600,
    Role.DIRECTOR: 600,
    Role.NARRATOR: 1200,
    Role.CHECKER: 1500,
    Role.PROPOSER: 200,
    Role.LOCATOR: 200,
}
# Thought tokens count against max_output_tokens (ai.google.dev "Token limits and max_output_tokens"); the cap
# is only a runaway guard, so it is generous. Levels are relative allowances, not guarantees.
THINKING_ALLOWANCE = {"minimal": 1024, "low": 3072, "medium": 8192, "high": 16384}
MAX_OUTPUT_CEILING = 32768  # the MAX_TOKENS retry doubles the cap up to this

_RETRY_CODES = {408, 429}
_SAFETY_FINISH = {
    types.FinishReason.SAFETY,
    types.FinishReason.PROHIBITED_CONTENT,
    types.FinishReason.BLOCKLIST,
    types.FinishReason.SPII,
    types.FinishReason.IMAGE_SAFETY,
}
LOOSEST = 2  # schema levels: 0 faithful, 1 loose enums, 2 JSON mode with the schema in the instructions


def thinking_config(model_id: str, level: str) -> types.ThinkingConfig:
    level = level.lower()
    if model_id.startswith("gemini-3"):
        if level == "minimal" and not model_id.startswith(_MINIMAL_OK):
            level = "low"
        return types.ThinkingConfig(thinking_level=_LEVELS.get(level, types.ThinkingLevel.LOW))
    return types.ThinkingConfig(thinking_budget=_BUDGETS.get(level, 1024))


def max_output_tokens(role: Role, thinking: str) -> int:
    return OUTPUT_TOKENS.get(role, 600) + THINKING_ALLOWANCE.get(thinking.lower(), THINKING_ALLOWANCE["low"])


def build_config(
    role: Role, schema: dict[str, Any], packet: Packet, cfg: RoleModel, *, level: int = 0,
    max_tokens: int | None = None,
) -> tuple[types.GenerateContentConfig, list[str]]:
    """The request config for one call at schema `level`, and the notes naming what the schema relaxed."""
    instructions = packet.instructions or ""
    if level >= LOOSEST:
        notes = ["schema sent as text (JSON mode)"]
        shown = json.dumps(convert(schema, level=1).schema, ensure_ascii=False)
        instructions = (f"{instructions}\n\n" if instructions else "") + (
            "Answer with one JSON object, and nothing else, that matches this JSON Schema exactly "
            f"(every listed field present):\n{shown}"
        )
        schema_arg: dict[str, Any] | None = None
    else:
        conv = convert(schema, level=level)
        notes, schema_arg = conv.relaxed, conv.schema
    config = types.GenerateContentConfig(
        system_instruction=instructions or None,
        response_mime_type="application/json",
        response_json_schema=schema_arg,
        thinking_config=thinking_config(cfg.model, cfg.thinking),
        max_output_tokens=max_tokens or max_output_tokens(role, cfg.thinking),
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )
    return config, notes


class GeminiModel:
    """`StructuredModel` over google-genai. `models` maps each role to its pinned model and thinking level."""

    provider = "gemini"

    def __init__(
        self,
        models: Mapping[Role, RoleModel] | None = None,
        *,
        client: Any = None,
        api_key: str | None = None,
        max_retries: int = 3,
        backoff_s: float = 1.0,
        timeout_s: float = 90.0,
        sleep: Callable[[float], None] = time.sleep,
    ):
        self.models = dict(models or {})
        self.max_retries = max_retries
        self.backoff_s = backoff_s
        self.sleep = sleep
        self.schema_level: dict[Role, int] = {}  # a role whose schema the server rejected starts looser
        if client is None:
            key = api_key or get_key()
            if not key:
                raise MissingKey("GEMINI_API_KEY is not set in the environment or in .env at the repo root")
            from google import genai

            client = genai.Client(api_key=key, http_options=types.HttpOptions(timeout=int(timeout_s * 1000)))
        self.client = client

    def role_model(self, role: Role) -> RoleModel:
        return self.models.get(role, DEFAULT_MODEL)

    def fill(
        self, role: Role, schema: dict[str, Any], packet: Packet, *, turn_id: str | None, attempt: int,
        seq: int = 0,
    ) -> CallResult:
        cfg = self.role_model(role)
        contents = packet.render(include_instructions=False)
        cap = max_output_tokens(role, cfg.thinking)
        record = new_record(
            role, schema, provider=self.provider, model_id=cfg.model, turn_id=turn_id, attempt=attempt, seq=seq,
            request={
                "model": cfg.model, "thinking": cfg.thinking, "attempt": attempt,
                "system_instruction": packet.instructions, "contents": contents, "schema": schema,
                "max_output_tokens": cap,
            },
        )
        watch = Stopwatch()
        level = self.schema_level.get(role, 0)
        rejected: list[str] = []
        usage: list[Any] = []
        while True:
            config, notes = build_config(role, schema, packet, cfg, level=level, max_tokens=cap)
            try:
                response = self._generate(cfg.model, contents, config, record, watch, usage, rejected)
            except _Rejected as exc:
                rejected.append(f"level {level}: {exc}")
                if level >= LOOSEST:
                    raise self._unavailable(record, watch, usage, "; ".join(rejected)) from None
                level += 1
                continue
            usage.append(getattr(response, "usage_metadata", None))
            if _finish(response) == types.FinishReason.MAX_TOKENS and _parse(response)[0] is None \
                    and cap < MAX_OUTPUT_CEILING:
                cap = min(cap * 2, MAX_OUTPUT_CEILING)  # truncated mid-JSON: once more with room
                config, notes = build_config(role, schema, packet, cfg, level=level, max_tokens=cap)
                try:
                    response = self._generate(cfg.model, contents, config, record, watch, usage, rejected)
                except _Rejected as exc:  # keep the cut-off answer; call_role re-asks it
                    rejected.append(f"level {level} (retry at {cap} tokens): {exc}")
                else:
                    usage.append(getattr(response, "usage_metadata", None))
            break
        if level:
            self.schema_level[role] = level
        extra: dict[str, Any] = {"max_output_tokens": cap}
        if level:
            extra["schema_level"] = level
        if notes:
            extra["schema_relaxed"] = notes
        if rejected:
            extra["schema_rejected"] = rejected
        record = _with_usage(record.model_copy(update={"request": {**record.request, **extra}}), usage, watch.ms())
        reason = _refusal(response)
        if reason:
            rec = record.model_copy(
                update={"outcome": Outcome.REFUSED, "response": {"data": None, "text": None, "error": reason}}
            )
            raise ModelRefused(f"{role.value}: provider refused ({reason})", rec)
        data, text = _parse(response)
        error = None if data is not None else _why_empty(response, text)
        record = record.model_copy(update={"response": {"data": data, "text": text, "error": error}})
        return CallResult(data=data, record=record)

    def _generate(
        self, model_id: str, contents: str, config: types.GenerateContentConfig, record: ModelCallRecord,
        watch: Stopwatch, usage: list[Any], rejected: list[str],
    ) -> Any:
        last = ""
        for i in range(self.max_retries + 1):
            try:
                return self.client.models.generate_content(model=model_id, contents=contents, config=config)
            except errors.APIError as exc:
                last = f"HTTP {exc.code}: {exc.message or exc.status or ''}".strip()
                if exc.code == 400 and "api key" not in last.lower():  # a bad key is a 400 too: no step-down
                    raise _Rejected(last) from exc
                if not (exc.code in _RETRY_CODES or exc.code >= 500):
                    break
            except (httpx.HTTPError, TimeoutError, ConnectionError) as exc:
                last = f"{type(exc).__name__}: {exc}"
            if i < self.max_retries:
                self.sleep(self.backoff_s * 2**i)
        raise self._unavailable(record, watch, usage, "; ".join([*rejected, last]))

    def _unavailable(self, record: ModelCallRecord, watch: Stopwatch, usage: list[Any], error: str) -> ModelUnavailable:
        rec = _with_usage(record, usage, watch.ms()).model_copy(
            update={"outcome": Outcome.ERROR, "response": {"data": None, "text": None, "error": error}}
        )
        return ModelUnavailable(f"{record.role.value}: model unavailable ({error})", rec)


class _Rejected(Exception):
    """A 400 from the server (bad request: usually the schema); `fill` resends it looser."""


# ---------------------------------------------------------------- response reading


def _count(usage: Any, name: str) -> int:
    return int(getattr(usage, name, None) or 0) if usage is not None else 0


def _with_usage(record: ModelCallRecord, usages: list[Any], latency_ms: int) -> ModelCallRecord:
    """Token counts summed over every request this call made (usage field names verified in 2.25.0 types.py).

    `prompt_token_count` includes cached tokens; `candidates_token_count` excludes thoughts."""
    cached = sum(_count(u, "cached_content_token_count") for u in usages)
    prompt = sum(_count(u, "prompt_token_count") for u in usages)
    rec = record.model_copy(
        update={
            "tokens_in_cached": cached,
            "tokens_in": max(prompt - cached, 0),
            "tokens_out": sum(_count(u, "candidates_token_count") for u in usages),
            "tokens_thinking": sum(_count(u, "thoughts_token_count") for u in usages),
            "latency_ms": latency_ms,
        }
    )
    return rec.model_copy(update={"cost_usd": budget.cost(rec)})


def _candidate(response: Any) -> Any:
    candidates = getattr(response, "candidates", None) or []
    return candidates[0] if candidates else None


def _finish(response: Any) -> Any:
    cand = _candidate(response)
    return getattr(cand, "finish_reason", None) if cand is not None else None


def _refusal(response: Any) -> str | None:
    feedback = getattr(response, "prompt_feedback", None)
    block = getattr(feedback, "block_reason", None) if feedback else None
    if block:
        return f"prompt blocked: {getattr(block, 'value', block)}"
    finish = _finish(response)
    if finish in _SAFETY_FINISH:
        return f"response blocked: {getattr(finish, 'value', finish)}"
    return None


def _text(response: Any) -> str:
    """Concatenate the first candidate's non-thought text parts."""
    cand = _candidate(response)
    content = getattr(cand, "content", None) if cand is not None else None
    parts = (getattr(content, "parts", None) or []) if content is not None else []
    return "".join(p.text for p in parts if getattr(p, "text", None) and not getattr(p, "thought", False))


def extract_json(text: str) -> Any:
    """The JSON value in `text`: plain, inside a ``` fence, or the first {...} with prose around it; else None."""
    s = text.strip()
    if not s:
        return None
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        pass
    if s.startswith("```"):
        body = s.split("\n", 1)[1] if "\n" in s else s[3:]
        body = body.rsplit("```", 1)[0] if "```" in body else body
        try:
            return json.loads(body.strip())
        except json.JSONDecodeError:
            pass
    start = s.find("{")
    if start >= 0:
        try:
            return json.JSONDecoder().raw_decode(s[start:])[0]
        except json.JSONDecodeError:
            pass
    return None


def _parse(response: Any) -> tuple[Any, str | None]:
    """(parsed JSON or None, raw text or None)."""
    text = _text(response)
    data = extract_json(text) if text else None
    if data is None:
        parsed = getattr(response, "parsed", None)
        if isinstance(parsed, dict | list):
            data = parsed
    return data, text or None


def _why_empty(response: Any, text: str | None) -> str:
    if _candidate(response) is None:
        return "no candidates in the response"
    finish = _finish(response)
    name = getattr(finish, "value", finish)
    if finish == types.FinishReason.MAX_TOKENS:
        return "output cut off at max_output_tokens (MAX_TOKENS)"
    if not text:
        return f"empty response (finish reason {name})"
    return f"response is not JSON (finish reason {name})"
