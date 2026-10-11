"""Spec 033 P6 (T070, C12): the guard that wraps the case games is alive, and every case id is played by a guarded module."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from engine.dm import testimony
from tests.guard.games_033 import CASES, GUARDED
from tests.guard.viii9 import DENY, Guard, Viii9Violation

CASES_MD = Path(__file__).resolve().parents[2] / "specs" / "033-dm-states-code-records" / "cases.md"


def test_the_fixture_arms_the_denylist_inside_a_dm_tools_turn(_viii9_guard: Guard | None) -> None:
    g = _viii9_guard
    assert g is not None and Path(__file__).stem in GUARDED
    assert all(e.mode == "raise" for e in DENY.values())  # P6: every entry raises
    g.turn_depth = 1  # as if inside a dm-tools turn
    try:
        with pytest.raises(Viii9Violation, match=r"constitution VIII\.9"):
            testimony.overlap("a", "b")
    finally:
        g.turn_depth = 0
        g.hits.clear()  # the planted hit is the test's, not the game's
    testimony.overlap("a", "b")  # outside a turn it is no hit


def test_every_case_section_is_played_by_a_guarded_module() -> None:
    sections = set(re.findall(r"^## (C\d+)\.", CASES_MD.read_text(encoding="utf-8"), re.M))
    played = {c.split(".")[0] for cs in CASES.values() for c in cs}
    assert sections - played == {"C11", "C12"}, "C11 is evals, C12 is tests/guard; the rest are games"
    here = Path(__file__).parent
    for mod, cases in CASES.items():
        src = (here / f"{mod}.py").read_text(encoding="utf-8")
        for c in cases:
            assert re.search(rf"\b{re.escape(c)}\b", src), f"{mod}.py names no {c}"
        assert mod in GUARDED
