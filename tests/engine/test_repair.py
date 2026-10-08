"""Spec 006: per-sentence repair (12.3.3, PR-12-2 step 7). The basic cases (one sentence repaired, cuts by code,
two rounds then a cut, the plain fallback) are in test_narration_convergence.py and test_turn_narration.py; these
cover the rendered line and the open prompt."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from engine.dm.turn import play_turn
from engine.llm.base import Role
from tests.engine.test_turn_adjudication import setup
from tests.engine.test_turn_narration import _decl, _must, calls, chk, look_model, rep

WOMAN = "Tam Harlan looks over the quay with Brannoc."  # an unknown name: a blocking code-scan hit (spec 011)


def _rulings(dock: Any, turn_id: str) -> list[dict[str, Any]]:
    return [e.payload.ruling for e in dock.store.events(types=["ruling_logged"])  # type: ignore[attr-defined]
            if e.turn_id == turn_id]


def test_an_uncovered_must_name_line_is_stated_by_its_rendered_line(tmp_path: Path) -> None:
    """The only sentence citing the look fails twice: it is cut, the look is stated by code in its place, the
    passing sentence stays, and a rule_conflict ruling with review_flag is logged (no plain fallback)."""
    def draft(schema: Any, packet: Any) -> dict[str, Any]:
        return {"sentences": [_decl(WOMAN, _must(packet)), _decl("Fog lies low on the water.", atmosphere=True),
                              _decl("What do you do?")]}
    model = look_model(narrator=[draft, rep(0, WOMAN), rep(0, WOMAN)])
    dock, ctx = setup(tmp_path, model)
    out = play_turn(ctx, "I look over the quay.")
    r = out.response
    assert not r.flags.fallback_used and r.flags.review_flag
    assert r.fiction == ("You look around. It works. The Night Dock's ferry: moored at the far end of the quay. "
                         "Fog lies low on the water. What do you do?"), r.fiction  # in the cut sentence's place
    assert [v["kind"] for v in out.turn_record.draft_versions] == ["draft", "repair", "repair", "render"]
    assert any(x["kind"] == "rule_conflict" and x["review_flag"] for x in _rulings(dock, out.turn_record.turn_id))
    assert len(calls(model, Role.NARRATOR)) == 3  # the draft and two narrow repairs, never more


def test_the_open_prompt_is_restored_only_when_repair_cut_it(tmp_path: Path) -> None:
    bad_prompt = "Do you make a Might check?"
    def draft(schema: Any, packet: Any) -> dict[str, Any]:
        return {"sentences": [_decl("You look over the quay.", _must(packet)), _decl(bad_prompt)]}
    model = look_model(narrator=[draft, rep(1, bad_prompt), rep(1, bad_prompt)], checker=[chk()] * 3)
    dock, ctx = setup(tmp_path, model)
    out = play_turn(ctx, "I look over the quay.")
    assert out.response.fiction == "You look over the quay. What do you do?"  # 12.14.9, restored by code
    assert "12.14.4" not in str(out.turn_record.screen)


def test_a_draft_that_never_asked_gets_no_prompt_patched_in(tmp_path: Path) -> None:
    def draft(schema: Any, packet: Any) -> dict[str, Any]:
        return {"sentences": [_decl("You look over the quay.", _must(packet)),
                              _decl("The ferryman's lantern swings, and he waits for your word.")]}
    model = look_model(narrator=[draft], checker=[chk()])
    dock, ctx = setup(tmp_path, model)
    out = play_turn(ctx, "I look over the quay.")
    assert not out.response.fiction.endswith("What do you do?")  # an awaiting image is an open prompt (12.14.9)
