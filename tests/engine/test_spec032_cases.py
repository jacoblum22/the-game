"""Spec 032 cases (specs/032-dm-tools-mvp/cases.md): the data tables the cases are enumerated from, walked so a
changed data file fails loudly; the traced fighter-save facts; the held-out set's hash; and one strict xfail per
case group for the phases that build it (the phase that builds a group replaces its xfail with real tests)."""

from __future__ import annotations

import hashlib
import json
import typing
from pathlib import Path
from typing import Any

import pytest
import yaml

from engine.data.loader import load_rules
from engine.dm import dm_tools
from engine.dm.dispute import DisputeKind
from engine.dm.schemas import QUESTION_KINDS
from engine.gen import hooks
from engine.time import clock
from evals import npc_agency

SPEC = Path(__file__).resolve().parents[2] / "specs" / "032-dm-tools-mvp"
FIX = Path(__file__).resolve().parents[1] / "fixtures" / "spec032_fighter_turns.json"
RULES = load_rules()

FOE_OUTCOMES = ("held_breaks_free", "prone_stands", "not_engaged_closes", "miss", "hit", "critical_hit")  # F1-F6
PRONOUN_SETS = ("she/her", "he/him", "they/them", "it")  # Q1-Q4
TURN_STATES = ("plain_talk", "offer_open", "rolled_resolved", "change_calls", "reveal_clue")  # X1-X5


# ------------------------------------------------------------------------------------ the enumerations


def test_enumerated_tables_have_their_counted_lengths() -> None:
    assert len(RULES.ids("verb.")) == 15  # R1-R15
    assert len(dm_tools.CHANGES) == 11  # R24-R34: the 10 kinds plus `fight` (P3)
    assert len(RULES.ids("cond.")) == 33  # K1-K33
    assert len(RULES.ids("cost.")) == 9  # O1-O9
    assert len(FOE_OUTCOMES) == 6 and len([i for i in RULES.ids("beh.") if i.startswith("beh.default_")]) == 4  # F1-F6, F22-F25
    assert len(RULES.ids("adv.")) == 156  # F21
    assert len(RULES.pacing["scenes"]["cut_triggers"]) == 7 and RULES.pacing["scenes"]["dead_air_turns"] == 2  # C1-C7
    assert len(clock.MODES) == 5  # T1-T5
    assert len(npc_agency.CELLS) == 12 and len(npc_agency.REPEATS) == 4  # N1-N16
    assert len(QUESTION_KINDS) == 7  # J1-J7
    assert len(PRONOUN_SETS) == 4  # Q1-Q4
    assert len(typing.get_args(DisputeKind)) == 4
    assert len(TURN_STATES) * 4 == 20  # X1-X20
    assert len(hooks.kinds()["incident"]) == 8  # E5


def test_the_nine_cost_ids_are_the_menu() -> None:
    assert sorted(i.removeprefix("cost.") for i in RULES.ids("cost.")) == [
        "closed_door", "drain", "exposure", "footing", "gear", "harm", "shortfall", "time", "twist"]


def test_twelve_cells_are_three_moods_by_four_costs() -> None:
    assert {(c["mood"], c["cost"]) for c in npc_agency.CELLS} == {(m, k) for m in ("open", "guarded", "closed")
                                                                  for k in ("none", "small", "real", "big")}
    rows = {r["range"]: r["by_cost"] for r in RULES.table("tbl.npc_ceiling")["results"]}
    for c in npc_agency.CELLS:  # the harness reads T-12-19's cell as an observation; dm-tools no longer uses it
        assert npc_agency.GRID[c["mood"]][c["cost"]] == rows[c["mood"]][c["cost"]]


# ------------------------------------------------------------------------------------ the traced save (P1.6)


def _fixture() -> dict[str, Any]:
    return json.loads(FIX.read_text(encoding="utf-8"))


def test_fighter_save_was_refused_on_prose_only_targets_and_started_no_fight() -> None:
    """The traced facts of save playtest-20261010-153123-fighter-dm-tools (turns 9, 11, 12), as recorded. P3 flipped
    the acceptance (test_spec032_p3.py::test_r16: the same calls now roll); P4 flipped the last one: this is what the OLD
    code did (no conflict_start); test_spec032_p4.py::test_f11 replays the call and the fight starts."""
    fx = _fixture()["turns"]
    for turn, target in (("turn.9", "the beast in the clearing"), ("turn.12", "the pale beast")):
        first = fx[turn]["tools"][0]
        assert first["tool"] == "propose_roll" and target in first["args"]
        assert first["out"].startswith("REFUSED: no one or nothing on record")  # what the old code did
        assert len(fx[turn]["refusals"]) == 1
        assert "target" not in json.loads(fx[turn]["tools"][1]["args"])  # the retry dropped the target
    assert fx["turn.11"]["tools"] == []  # the dead end: a three-act message and zero tool calls
    assert _fixture()["conflict_start_boundaries"] == 0


# ------------------------------------------------------------------------------------ the held-out set (P1.4)


def _heldout_text() -> str:
    return (SPEC / "heldout.yaml").read_text(encoding="utf-8")


def test_heldout_is_24_items_with_the_stated_mix_and_an_unchanged_body() -> None:
    text = _heldout_text()
    head, body = text.split("\nitems:\n", 1)
    stated = next(ln.split(":", 1)[1].strip() for ln in head.splitlines() if ln.startswith("body_sha256:"))
    items = yaml.safe_load("items:\n" + body)["items"]
    kinds = [i["kind"] for i in items]
    assert len(items) == 24 and len({i["id"] for i in items}) == 24
    assert {k: kinds.count(k) for k in set(kinds)} == {"prose_target": 6, "fight_exchange": 6, "said": 5, "said_edge": 1,
                                                       "presence": 3, "pronoun": 3}
    assert all(i.get("pass") and i.get("check") for i in items)
    # the hash pins the labels: a later phase that edits an item (tunes on the set) fails here, and P7 says it is spent
    assert hashlib.sha256(body.encode("utf-8")).hexdigest() == stated


# ------------------------------------------------------------------------------------ later phases: one xfail each

GROUPS = [
    ("J1-J14 said/told reaches the journal", "P5"),
    ("Q1-Q14 presence and pronouns", "P5"),
    ("L1-L6 leak audit without name tokens", "P5"),
    ("E5 sealed secrets outside the clue rule (per incident kind)", "P5"),
    ("I12 log-only: item named in the passage with no change call", "P5"),
    ("S1-S12 resuming keeps the engine", "P2"),
    ("X1-X22 /fix on dm-tools turns", "P6"),
    ("N1-N16 NPC agency after the fixes", "P7"),
]


@pytest.mark.xfail(strict=True, reason="built by a later phase; replace this with the group's real tests")
@pytest.mark.parametrize(("group", "phase"), GROUPS, ids=[g.split()[0] for g, _ in GROUPS])
def test_case_group_built(group: str, phase: str) -> None:
    pytest.fail(f"{group}: not built yet (phase {phase})")
