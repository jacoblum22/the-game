"""Spec 006 / 019: the one revision and what code does after it (12.3.3, PR-12-2 step 6). The basic cases (the
revision sees the whole draft, cuts by code, the plain fallback) are in test_narration_convergence.py and
test_turn_narration.py; these cover the rendered line, the open prompt and the quote marks."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from engine.dm.turn import play_turn
from engine.llm.base import Role
from tests.engine.test_turn_adjudication import setup
from tests.engine.test_turn_narration import _must, calls, chk, look_model, narr, passage

LOOK = ("You look around. It works. The Night Dock's ferry: moored at the far end of the quay.")


def _rulings(dock: Any, turn_id: str) -> list[dict[str, Any]]:
    return [e.payload.ruling for e in dock.store.events(types=["ruling_logged"])  # type: ignore[attr-defined]
            if e.turn_id == turn_id]


def test_an_uncovered_must_name_line_is_stated_by_its_rendered_line(tmp_path: Path) -> None:
    """The side list never covers the look, in the draft or the revision: code states it by its rendered line
    before the closing question, and logs a rule_conflict ruling with review_flag (no plain fallback). The
    revision is told the handle, never the rendered line (12.3.3: rendered lines are never instructions)."""
    model = look_model(narrator=[narr("Fog lies low on the water. What do you do?", cite=False)] * 2)
    dock, ctx = setup(tmp_path, model)
    out = play_turn(ctx, "I look over the quay.")
    r = out.response
    assert not r.flags.fallback_used and r.flags.review_flag
    assert r.fiction == f"Fog lies low on the water. {LOOK} What do you do?", r.fiction
    assert [v["kind"] for v in out.turn_record.draft_versions] == ["draft", "revision", "render"]
    assert any(x["kind"] == "rule_conflict" and x["review_flag"] for x in _rulings(dock, out.turn_record.turn_id))
    revision = calls(model, Role.NARRATOR)[1].message.split("A REVISION", 1)[1]
    assert "not narrated: R1" in revision and "It works" not in revision
    assert len(calls(model, Role.NARRATOR)) == 2  # the draft and one revision, never more


def test_the_open_prompt_is_restored_only_when_a_cut_removed_it(tmp_path: Path) -> None:
    text = "You look over the quay. Do you make a Might check?"
    model = look_model(narrator=[narr(text), narr(text)], checker=[chk()] * 3)
    dock, ctx = setup(tmp_path, model)
    out = play_turn(ctx, "I look over the quay.")
    assert out.response.fiction == "You look over the quay. What do you do?"  # 12.14.9, restored by code
    assert "12.14.4" not in str(out.turn_record.screen)


def test_a_draft_that_never_asked_gets_no_prompt_patched_in(tmp_path: Path) -> None:
    model = look_model(narrator=[narr("You look over the quay. The ferryman's lantern swings, and he waits for your "
                                      "word.")], checker=[chk()])
    dock, ctx = setup(tmp_path, model)
    out = play_turn(ctx, "I look over the quay.")
    assert not out.response.fiction.endswith("What do you do?")  # an awaiting image is an open prompt (12.14.9)


def test_speech_left_unquoted_is_revised_then_quoted_by_code(tmp_path: Path) -> None:
    """12.3.1a item 2 (round 6, 232941 turn.16): first-person words in the narrator's voice go to the one revision;
    left unquoted again, code quotes the exact words. Nothing is cut."""
    bare = "Nobody has stood at this gate asking after the child that I've marked."
    text = f"You look over the quay. Tam Harlan squints at you. {bare} What do you do?"
    model = look_model(narrator=[narr(text)] * 2, checker=[chk()] * 2)
    dock, ctx = setup(tmp_path, model)
    out = play_turn(ctx, "I look over the quay.")
    assert out.response.fiction == f'You look over the quay. Tam Harlan squints at you. "{bare}" What do you do?'
    revision = calls(model, Role.NARRATOR)[1].message
    assert f'speech outside quote marks: "{bare}"' in revision
    assert [v["kind"] for v in out.turn_record.draft_versions] == ["draft", "revision", "cut"]
    assert out.turn_record.draft_versions[-1]["quoted"] == [bare]


def test_a_cut_alone_needs_no_revision(tmp_path: Path) -> None:
    """12.3.3: a failure whose fix is a cut (sealed content, a T2 element no record line delivers) is cut by code;
    with nothing else failing, no revision call is made."""
    def draft(schema: Any, packet: Any) -> dict[str, Any]:
        clue = {"element_kind": "clue", "name": "a scrap of paper naming the smugglers", "ordinary": True, "implied": []}
        return passage("You look over the quay. A scrap of paper naming the smugglers lies by the post. "
                       "What do you do?", _must(packet), new=[clue])
    model = look_model(narrator=[draft], checker=[chk()])
    dock, ctx = setup(tmp_path, model)
    out = play_turn(ctx, "I look over the quay.")
    assert out.response.fiction == "You look over the quay. What do you do?"
    assert len(calls(model, Role.NARRATOR)) == 1
