"""I-127 / DL-12-37: atmosphere is never a claim, new furniture is written (not cut), redrafts never shrink prose.

The prose and claims in `RECORDED_*` are the model outputs saved in the owner's first playtest (`My World2`, the
"set the scene" turn and the opening), with the subject ids remapped to the dock fixture. Under the old check the
woodsmoke and north-road sentences were cut as "subject unknown"; they must now survive in a single narrator call.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from engine.audit.claims import Claim, check_claims
from engine.data.loader import load_rules
from engine.dm.adjudication import AdjudicationRecord
from engine.dm.packet import render_view, scene_setting
from engine.dm.turn import play_turn
from engine.llm.base import Role
from tests.engine.test_turn_adjudication import setup
from tests.engine.test_turn_narration import _decl, _must, calls, chk, claim, look_model, narr, rep

# "set the scene" turn: 5 sentences incl. the prompt; claims as the Checker returned them (turn 2, row 10)
RECORDED_SCENE = ("Morning light settles cold across the village. You stand where the tracks meet at the gate. "
                  "Behind you, woodsmoke rises thin from the rooftops of the village. "  # "Ashgate" was that world's: a name the dock world lacks fails 12.3.1a
                  "Beyond the boundary pale, the north road lies open between rough banks, quiet under the early sky. "
                  "What do you do?")


def _scene_claims(dock: Any, hour: str) -> list[dict[str, Any]]:
    return [claim(0, "unknown", "location_time", "time_of_day", hour),  # the store's own hour: atmosphere may not contradict it
            claim(1, dock.pc, "position", "location", "where the tracks meet at the gate"),
            claim(2, "unknown", "existence", "woodsmoke", "rises thin from the rooftops of the village"),
            claim(3, "unknown", "existence", "north road", "lies open between rough banks, quiet under the early sky")]


def _declared_scene(schema: Any, packet: Any) -> dict[str, Any]:
    """The recorded prose as declared sentences (spec 006): atmosphere flagged, the two features declared new."""
    from engine.audit.declare import split

    s = split(RECORDED_SCENE)
    feat = lambda n: [{"element_kind": "feature", "name": n, "ordinary": True, "implied": []}]  # noqa: E731
    return {"sentences": [_decl(s[0], atmosphere=True), _decl(s[1], _must(packet)),
                          _decl(s[2], new=feat("woodsmoke")), _decl(s[3], new=feat("north road")), _decl(s[4])]}


def test_recorded_scene_prose_survives_in_one_pass(tmp_path: Path) -> None:
    model = look_model(narrator=[_declared_scene])
    dock, ctx = setup(tmp_path, model)
    hour = ("morning", "afternoon", "evening", "night")[ctx.store.state.time.now.watch]
    model.push(Role.CHECKER, chk(*_scene_claims(dock, hour)))
    out = play_turn(ctx, "I look over the quay.")
    assert out.response.fiction == RECORDED_SCENE and not out.response.flags.fallback_used
    assert len(calls(model, Role.NARRATOR)) == 1  # was 6 on the opening
    assert len(calls(model, Role.CHECKER)) == 2  # turn.1 is a sampled turn: the diff and the full extraction, after
    # delivery, logged only (spec 011, DL-12-83)
    names = {e.name for e in ctx.store.state.entities.values()}
    assert {"woodsmoke", "north road"} <= names  # written on mention at check time, not cut


@pytest.mark.parametrize("kind,ordinary,value", [
    ("clue", True, "a scrap of paper that points to the smugglers' cache"),
    ("item", False, "a hidden door behind the shelves with treasure behind it"),
    ("person", False, "an old man who knows about the cult"),
    ("hazard", True, "a snare across the path"),
    ("adversary", True, "a bandit lurking by the road"),
])
def test_real_inventions_are_still_cut(tmp_path: Path, kind: str, ordinary: bool, value: str) -> None:
    """12.14.13: a declared T2 element (or one of no listed kind) no record line delivers is cut by code."""
    def draft(schema: Any, packet: Any) -> dict[str, Any]:
        new = [{"element_kind": kind, "name": value, "ordinary": ordinary, "implied": []}]
        return {"sentences": [_decl("The quay is quiet.", _must(packet)), _decl("Something is wrong here.", new=new),
                              _decl("What do you do?")]}
    model = look_model(narrator=[draft])
    dock, ctx = setup(tmp_path, model)
    model.push(Role.CHECKER, chk())
    out = play_turn(ctx, "I look over the quay.")
    assert out.turn_record.draft_versions[0]["checks"]["1"][0]["fix"] == "cut"
    assert out.response.fiction == "The quay is quiet. What do you do?"
    assert len(calls(model, Role.NARRATOR)) == 1  # a cut is code's, no repair call
    assert value not in {e.name for e in ctx.store.state.entities.values()}


def test_ordinary_unknown_element_is_written_not_cut() -> None:
    rules = load_rules()
    vs = check_claims([Claim.model_validate({"subject": "unknown", "class": "existence", "predicate": "woodsmoke",
                                             "value": "rises thin from the rooftops"})], _empty_state(), AdjudicationRecord(),
                      [], rules=rules)
    assert (vs[0].verdict, vs[0].fix) == ("new_element", "write_on_mention")


def test_unknown_subject_that_acts_or_changes_is_still_cut() -> None:
    cs = [{"subject": "unknown", "class": "action", "predicate": "spits", "value": "into the dust", "asserts_change": True},
          {"subject": "unknown", "class": "existence", "predicate": "door", "value": "swings open", "asserts_change": True}]
    vs = check_claims(cs, _empty_state(), AdjudicationRecord(), [], rules=load_rules())
    assert [(v.verdict, v.fix) for v in vs] == [("unsourced_change", "cut")] * 2


def test_redraft_names_claims_and_never_asks_for_shorter(tmp_path: Path) -> None:
    """A code-scan hit (an unknown name in the narrator's voice, 12.3.1b item 2.6) is redrafted with its reason."""
    bad = "Tam Harlan nods to Brannoc. The fog lies low on the water. What do you do?"
    good = "Tam Harlan nods to you. The fog lies low on the water. What do you do?"
    model = look_model(narrator=[narr(bad), lambda s, p: rep(0, "Tam Harlan nods to you.", _must(p))])
    dock, ctx = setup(tmp_path, model)
    out = play_turn(ctx, "I look over the quay.")
    assert out.response.fiction == good
    msg = calls(model, Role.NARRATOR)[1].message
    assert "Tam Harlan nods to Brannoc" in msg and "names 'Brannoc'" in msg
    low = msg.lower()
    assert "every other sentence of your draft stands as written" in low
    assert not any(w in low for w in ("shorten the", "simplify", "play it safe", "be safe")) or "do not shorten" in low


def test_scene_setting_gives_the_narrator_the_place_people_and_time(tmp_path: Path) -> None:
    model = look_model(narrator=[narr("The quay is quiet. What do you do?")])
    dock, ctx = setup(tmp_path, model)
    text = scene_setting(ctx.store.state)
    assert text.startswith("SCENE SETTING") and "- place:" in text and "- time:" in text
    assert "ids" not in text and "loc." not in text and "npc." not in text  # words, never ids
    model.push(Role.CHECKER, chk())
    play_turn(ctx, "I look over the quay.")
    assert "SCENE SETTING" in calls(model, Role.NARRATOR)[0].message


def test_descriptive_keys_are_not_lost_to_the_view_cap() -> None:
    data = {f"k{i:02d}": i for i in range(20)} | {"desc": "a village where two roads cross"}
    view = {"entities": [{"id": "loc.x", "name": "Ashgate", "data": data}]}
    assert "desc: a village where two roads cross" in render_view(view)


def _empty_state() -> Any:
    from engine.store.projection import WorldState

    return WorldState()
