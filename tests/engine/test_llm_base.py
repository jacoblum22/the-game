"""engine/llm/base.py: schema validation, packets, records and the re-ask rule."""

from __future__ import annotations

from typing import Any

import pytest

from engine.llm.base import (
    CallResult,
    CallSequence,
    ModelCallRecord,
    ModelInvalid,
    ModelRefused,
    Outcome,
    Packet,
    Role,
    call_role,
    new_record,
    next_seq,
    schema_hash,
    validate,
)
from engine.llm.offline import ScriptedModel

SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "kind": {"enum": ["a", "b"]},
        "note": {"anyOf": [{"type": "string"}, {"type": "null"}]},
        "items": {"type": "array", "items": {"$ref": "#/$defs/Item"}, "maxItems": 2},
        "flag": {"type": "boolean"},
    },
    "required": ["kind", "note", "items", "flag"],
    "additionalProperties": False,
    "$defs": {
        "Item": {
            "type": "object",
            "properties": {"id": {"type": "string", "enum": ["x", "y"]}},
            "required": ["id"],
            "additionalProperties": False,
        }
    },
}
GOOD = {"kind": "a", "note": None, "items": [{"id": "x"}], "flag": True}


def test_validate_accepts_good_value() -> None:
    assert validate(GOOD, SCHEMA) == []


@pytest.mark.parametrize(
    ("value", "fragment"),
    [
        ({**GOOD, "kind": "c"}, "is not one of"),
        ({k: v for k, v in GOOD.items() if k != "flag"}, "missing required field 'flag'"),
        ({**GOOD, "extra": 1}, "unexpected field 'extra'"),
        ({**GOOD, "items": [{"id": "x"}] * 3}, "at most 2 items"),
        ({**GOOD, "items": [{"id": "z"}]}, "$.items[0].id"),
        ({**GOOD, "note": 3}, "expected"),
        ({**GOOD, "flag": 1}, "expected boolean"),
        ("not an object", "expected object"),
    ],
)
def test_validate_reports_failures(value: Any, fragment: str) -> None:
    errs = validate(value, SCHEMA)
    assert errs and any(fragment in e for e in errs), errs


def test_integer_excludes_bool() -> None:
    assert validate(True, {"type": "integer"})
    assert validate(3, {"type": "integer", "maximum": 2})
    assert validate(2, {"type": "integer", "maximum": 2}) == []


def test_schema_hash_is_canonical() -> None:
    a = {"type": "object", "properties": {"x": {"enum": ["1", "2"]}}}
    b = {"properties": {"x": {"enum": ["1", "2"]}}, "type": "object"}
    assert schema_hash(a) == schema_hash(b)
    assert schema_hash(a) != schema_hash({**a, "required": ["x"]})
    assert len(schema_hash(a)) == 64


def test_packet_order_and_reask() -> None:
    p = Packet(instructions="I", core="C", cards=["c1", "c2"], view="V", exchanges=["e1"], message="M")
    text = p.render()
    order = [text.index(s) for s in ("ROLE INSTRUCTIONS", "CORE RULES", "RULE CARDS", "NARRATOR VIEW",
                                    "RECENT EXCHANGES", "THIS MESSAGE")]
    assert order == sorted(order)
    assert "ROLE INSTRUCTIONS" not in p.render(include_instructions=False)
    r = p.with_reask(["$.kind: 'c' is not one of ['a', 'b']"])
    assert r.render().endswith("Answer again, following the schema exactly.")
    assert "'c' is not one of" in (r.reask or "") and r.message == "M"


def test_record_has_model_calls_columns() -> None:
    cols = {"call_id", "turn_id", "role", "provider", "model_id", "schema_hash", "request", "response",
            "tokens_in_cached", "tokens_in", "tokens_out", "tokens_thinking", "cost_usd", "latency_ms", "outcome"}
    assert cols <= set(ModelCallRecord.model_fields)
    rec = new_record(Role.READER, SCHEMA, provider="p", model_id="m", turn_id="t1", attempt=1)
    assert rec.schema_hash == schema_hash(SCHEMA) and rec.attempt == 1 and rec.outcome == Outcome.OK
    assert rec.call_id == "call.t1.reader.0.1"  # deterministic: replays list the same call ids
    assert rec.seq == 0 and new_record(Role.READER, SCHEMA, provider="p", model_id="m", turn_id=None, attempt=0,
                                       seq=2).call_id == "call.pre.reader.2.0"
    assert ModelCallRecord(role=Role.READER, provider="p", model_id="m", schema_hash="h").seq == 0  # old rows


def _run(model: ScriptedModel, **kw: Any) -> tuple[CallResult, list[ModelCallRecord]]:
    seen: list[ModelCallRecord] = []
    res = call_role(model, Role.FRAMER, SCHEMA, Packet(message="go"), turn_id="t1", recorder=seen.append, **kw)
    return res, seen


def test_call_role_ok_first_time() -> None:
    res, seen = _run(ScriptedModel({Role.FRAMER: [GOOD]}, fallback=False))
    assert res.data == GOOD and res.attempts == 1 and not res.defaulted
    assert [r.outcome for r in seen] == [Outcome.OK]


def test_call_role_reasks_once_naming_failure() -> None:
    model = ScriptedModel({Role.FRAMER: [{**GOOD, "kind": "zzz"}, GOOD]}, fallback=False)
    res, seen = _run(model)
    assert res.data == GOOD and res.attempts == 2
    assert [r.outcome for r in seen] == [Outcome.INVALID_REASKED, Outcome.OK]
    assert [r.attempt for r in seen] == [0, 1]
    assert "zzz" in (model.calls[1][1].reask or "")


def test_call_role_default_after_second_failure() -> None:
    model = ScriptedModel({Role.FRAMER: [None, {"kind": "q"}]}, fallback=False)
    res, seen = _run(model, default=lambda: {"kind": "b"})
    assert res.defaulted and res.data == {"kind": "b"}
    assert [r.outcome for r in seen] == [Outcome.INVALID_REASKED, Outcome.DEFAULTED]
    assert "not valid JSON" in (model.calls[1][1].reask or "")


def test_call_role_raises_without_default() -> None:
    seen: list[ModelCallRecord] = []
    model = ScriptedModel({Role.FRAMER: [{}, {}]}, fallback=False)
    with pytest.raises(ModelInvalid) as info:
        call_role(model, Role.FRAMER, SCHEMA, Packet(), recorder=seen.append)
    assert info.value.record is not None and seen[-1].outcome == Outcome.ERROR


def test_call_role_check_hook_counts_as_failure() -> None:
    model = ScriptedModel({Role.FRAMER: [GOOD, {**GOOD, "kind": "b"}]}, fallback=False)
    res, _ = _run(model, check=lambda d: ["kind a is not allowed here"] if d["kind"] == "a" else [])
    assert res.data["kind"] == "b" and "kind a is not allowed" in (model.calls[1][1].reask or "")


def test_refusal_is_recorded_and_raised() -> None:
    rec = new_record(Role.FRAMER, SCHEMA, provider="gemini", model_id="m", turn_id="t1", attempt=0)
    rec = rec.model_copy(update={"outcome": Outcome.REFUSED})
    model = ScriptedModel({Role.FRAMER: [ModelRefused("blocked", rec)]}, fallback=False)
    seen: list[ModelCallRecord] = []
    with pytest.raises(ModelRefused):
        call_role(model, Role.FRAMER, SCHEMA, Packet(), recorder=seen.append)
    assert [r.outcome for r in seen] == [Outcome.REFUSED]


def test_call_role_numbers_calls_per_turn_and_role() -> None:
    """Two calls of one role in a turn get seq 0 and 1 (distinct call ids); another role or turn starts at 0."""
    seq = CallSequence()
    seen: list[ModelCallRecord] = []

    class Rec:
        next_call_seq = seq.next_call_seq

        def __call__(self, rec: ModelCallRecord) -> None:
            seen.append(rec)

    model = ScriptedModel({Role.FRAMER: [GOOD, {}, GOOD, GOOD], Role.READER: [GOOD]}, fallback=False)
    rec = Rec()
    call_role(model, Role.FRAMER, SCHEMA, Packet(), turn_id="t1", recorder=rec)
    call_role(model, Role.FRAMER, SCHEMA, Packet(), turn_id="t1", recorder=rec)  # re-asked once
    call_role(model, Role.READER, SCHEMA, Packet(), turn_id="t1", recorder=rec)
    call_role(model, Role.FRAMER, SCHEMA, Packet(), turn_id="t2", recorder=rec)
    assert [(r.turn_id, r.role.value, r.seq, r.attempt) for r in seen] == [
        ("t1", "framer", 0, 0), ("t1", "framer", 1, 0), ("t1", "framer", 1, 1), ("t1", "reader", 0, 0),
        ("t2", "framer", 0, 0)]
    assert seen[1].call_id == "call.t1.framer.1.0" and len({r.call_id for r in seen}) == 5
    # a bound-method recorder finds the sequence on its owner (TurnContext.record_call)
    assert next_seq(Rec().__call__, "t1", Role.FRAMER) == 2 and next_seq(seen.append, "t1", Role.FRAMER) == 0
    model.push(Role.READER, GOOD)
    res = call_role(model, Role.READER, SCHEMA, Packet(), turn_id="t9", recorder=seen.append, seq=4)
    assert res.record.seq == 4 and res.record.call_id == "call.t9.reader.4.0"
