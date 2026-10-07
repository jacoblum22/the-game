"""The safety screen (12.5.6) and the SAFETY part (12.5.7): lines cut, veils summarized, flags paused."""

from __future__ import annotations

from pathlib import Path

from engine.audit.safety import (
    SafetyEntry,
    flag_prompt,
    handle_safety_part,
    matches_line,
    safety_fact,
    safety_prefs,
    screen_safety,
)
from tests.fixtures.game import new_store

LINES = [SafetyEntry(kind="line", topic="spiders"), SafetyEntry(kind="line", topic="harm to children"),
         SafetyEntry(kind="veil", topic="torture", tags=["theme.cruelty.torture"]),
         SafetyEntry(kind="flag", topic="drowning")]


def test_lines_cut_and_ordinary_text_passes() -> None:
    res = screen_safety("A Spider drops from the beam. The lamp gutters.", LINES)
    assert not res.ok and [h.sentence for h in res.cuts] == [0]
    assert not screen_safety("Spiderwebs hang in the corners.", LINES).ok
    assert screen_safety("The lamp gutters. Rain on the roof. What do you do?", LINES).ok
    assert not screen_safety("They bring harm to the child.", LINES).ok  # stems and irregular plurals
    assert screen_safety("The children laugh in the square.", LINES).ok  # a topic needs all its words


def test_veils_summarized_not_shown() -> None:
    assert screen_safety("The interrogation, torture and all, lasts until dawn.", LINES).ok
    detailed = screen_safety("They begin the torture. The torture goes on and on, every cut described.", LINES)
    assert not detailed.ok and len(detailed.veils) == 2


def test_flags_are_reported_not_cut() -> None:
    res = screen_safety("The river rises; drowning is a real fear here.", LINES)
    assert res.ok and res.flags and res.review
    assert flag_prompt("drowning") == "[FLAG] This touches drowning. Continue, veil it, or steer away?"


def test_matches_line_for_table_rows() -> None:
    assert matches_line("a nest of giant spiders", LINES) is LINES[0]
    assert matches_line("a nest of rats", LINES) is None


def test_prefs_from_facts(tmp_path: Path) -> None:
    store = new_store(tmp_path)
    with store.transaction() as tx:
        tx.add(safety_fact(SafetyEntry(kind="line", topic="spiders", tags=["creature.spider"]), tx.state, tx.mint))
    with store.transaction() as tx:
        tx.add(safety_fact(SafetyEntry(kind="veil", topic="torture"), tx.state, tx.mint))
        tx.add(safety_fact(SafetyEntry(kind="line", topic="drowning"), tx.state, tx.mint))
    prefs = safety_prefs(store.state)
    assert [(p.kind, p.topic) for p in prefs] == [("line", "spiders"), ("line", "drowning"), ("veil", "torture")]
    assert not screen_safety("A spider.", store.state).ok
    assert store.rebuild() == store.state


def test_handle_safety_part() -> None:
    r = handle_safety_part("skip this, it's too much")
    assert r.pause and r.oof_line == "[OK] Adjusting. (Say how, or I'll reframe it.)"
    assert r.reframing == "reframe" and r.chosen_by == "default" and r.record is None
    r2 = handle_safety_part("adjust: refocus please. line: drowning")
    assert r2.reframing == "refocus" and r2.chosen_by == "player"
    assert r2.record == SafetyEntry(kind="line", topic="drowning")
    assert r2.ledger["kind"] == "adjust"
