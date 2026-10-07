"""engine/llm/replay.py: recorded responses are served by (turn_id, role, attempt) with a schema-hash check."""

from __future__ import annotations

from typing import Any

import pytest

from engine.llm.base import (
    ModelCallRecord,
    ModelRefused,
    ModelUnavailable,
    Outcome,
    Packet,
    ReplayDivergence,
    Role,
    call_role,
    new_record,
)
from engine.llm.offline import ScriptedModel
from engine.llm.replay import ReplayAdapter, ReplayModel

SCHEMA: dict[str, Any] = {"type": "object", "properties": {"x": {"enum": ["a", "b"]}}, "required": ["x"]}


def record_session() -> list[ModelCallRecord]:
    rows: list[ModelCallRecord] = []
    live = ScriptedModel({Role.READER: [{"x": "a"}], Role.FRAMER: [{"x": "nope"}, {"x": "b"}]}, fallback=False)
    call_role(live, Role.READER, SCHEMA, Packet(message="hi"), turn_id="t1", recorder=rows.append)
    call_role(live, Role.FRAMER, SCHEMA, Packet(message="hi"), turn_id="t1", recorder=rows.append)
    return rows


def test_replay_serves_same_answers_including_reask() -> None:
    rows = record_session()
    replay = ReplayModel(rows)
    seen: list[ModelCallRecord] = []
    assert call_role(replay, Role.READER, SCHEMA, Packet(), turn_id="t1", recorder=seen.append).data == {"x": "a"}
    res = call_role(replay, Role.FRAMER, SCHEMA, Packet(), turn_id="t1", recorder=seen.append)
    assert res.data == {"x": "b"} and res.attempts == 2
    assert all(r.provider == "replay" and r.cost_usd == 0 for r in seen)
    assert [r.outcome for r in seen] == [Outcome.OK, Outcome.INVALID_REASKED, Outcome.OK]
    assert ReplayAdapter is ReplayModel


def test_schema_change_is_divergence() -> None:
    replay = ReplayModel(record_session())
    changed = {**SCHEMA, "properties": {"x": {"enum": ["a", "b", "c"]}}}
    with pytest.raises(ReplayDivergence, match="schema changed"):
        replay.fill(Role.READER, changed, Packet(), turn_id="t1", attempt=0)


def test_unrecorded_call_is_divergence() -> None:
    replay = ReplayModel(record_session())
    with pytest.raises(ReplayDivergence, match="no recorded call"):
        replay.fill(Role.NARRATOR, SCHEMA, Packet(), turn_id="t1", attempt=0)
    with pytest.raises(ReplayDivergence):
        replay.fill(Role.READER, SCHEMA, Packet(), turn_id="t2", attempt=0)


def test_recorded_refusal_and_error_are_raised_again() -> None:
    base = new_record(Role.NARRATOR, SCHEMA, provider="gemini", model_id="gemini-3.8-flash", turn_id="t3", attempt=0)
    refused = base.model_copy(update={"outcome": Outcome.REFUSED,
                                      "response": {"data": None, "text": None, "error": "SAFETY"}})
    failed = base.model_copy(update={"role": Role.CHECKER, "outcome": Outcome.ERROR,
                                     "response": {"data": None, "text": None, "error": "HTTP 503"}})
    replay = ReplayModel([refused, failed])
    with pytest.raises(ModelRefused):
        replay.fill(Role.NARRATOR, SCHEMA, Packet(), turn_id="t3", attempt=0)
    with pytest.raises(ModelUnavailable):
        replay.fill(Role.CHECKER, SCHEMA, Packet(), turn_id="t3", attempt=0)


def test_latest_row_wins_for_a_retried_turn() -> None:
    first = new_record(Role.READER, SCHEMA, provider="gemini", model_id="m", turn_id="t1", attempt=0)
    first = first.model_copy(update={"outcome": Outcome.ERROR, "response": {"data": None, "text": None,
                                                                            "error": "HTTP 503"}})
    second = first.model_copy(update={"outcome": Outcome.OK, "response": {"data": {"x": "b"}, "text": "",
                                                                          "error": None}})
    replay = ReplayModel([first, second])
    assert replay.fill(Role.READER, SCHEMA, Packet(), turn_id="t1", attempt=0).data == {"x": "b"}
