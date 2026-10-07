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
from engine.dm.narration import _mention_name
from engine.dm.packet import render_view, scene_setting
from engine.dm.turn import play_turn
from engine.llm.base import Role
from tests.engine.test_turn_adjudication import setup
from tests.engine.test_turn_narration import calls, chk, claim, look_model, narr

# "set the scene" turn: 5 sentences incl. the prompt; claims as the Checker returned them (turn 2, row 10)
RECORDED_SCENE = ("Morning light settles cold across the village. You stand where the tracks meet at the gate. "
                  "Behind you, woodsmoke rises thin from the rooftops of Ashgate. "
                  "Beyond the boundary pale, the north road lies open between rough banks, quiet under the early sky. "
                  "What do you do?")


def _scene_claims(dock: Any, hour: str) -> list[dict[str, Any]]:
    return [claim(0, "unknown", "location_time", "time_of_day", hour),  # the store's own hour: atmosphere may not contradict it
            claim(1, dock.pc, "position", "location", "where the tracks meet at the gate"),
            claim(2, "unknown", "existence", "woodsmoke", "rises thin from the rooftops of Ashgate"),
            claim(3, "unknown", "existence", "north road", "lies open between rough banks, quiet under the early sky")]


def test_recorded_scene_prose_survives_in_one_pass(tmp_path: Path) -> None:
    model = look_model(narrator=[narr(RECORDED_SCENE)])
    dock, ctx = setup(tmp_path, model)
    hour = ("morning", "afternoon", "evening", "night")[ctx.store.state.time.now.watch]
    model.push(Role.CHECKER, chk(*_scene_claims(dock, hour)))
    out = play_turn(ctx, "I look over the quay.")
    assert out.response.fiction == RECORDED_SCENE and not out.response.flags.fallback_used
    assert len(calls(model, Role.NARRATOR)) == 1 and len(calls(model, Role.CHECKER)) == 1  # was 6 on the opening
    names = {e.name for e in ctx.store.state.entities.values()}
    assert {"woodsmoke", "north road"} <= names  # written on mention at check time, not cut


@pytest.mark.parametrize("claim_args", [
    ("existence", "clue", "a scrap of paper that points to the smugglers' cache"),
    ("existence", "hidden door", "a hidden door behind the shelves with treasure behind it"),
    ("knowledge", "knows", "the old man knows about the cult"),
    ("existence", "trap", "a snare across the path"),
    ("existence", "bandit", "a bandit lurks by the road"),
])
def test_real_inventions_are_still_cut(tmp_path: Path, claim_args: tuple[str, str, str]) -> None:
    cls, predicate, value = claim_args
    model = look_model(narrator=[narr("The quay is quiet. Something is wrong here. What do you do?")])
    dock, ctx = setup(tmp_path, model)
    model.push(Role.CHECKER, chk(claim(1, "unknown", cls, predicate, value)))
    out = play_turn(ctx, "I look over the quay.")
    first = out.turn_record.draft_versions[0]["verdicts"][0]
    assert (first["verdict"], first["fix"]) == ("new_element", "cut"), first
    assert "Something is wrong here." not in out.response.fiction
    assert value not in {e.name for e in ctx.store.state.entities.values()}


def test_ordinary_unknown_element_is_written_not_cut() -> None:
    rules = load_rules()
    vs = check_claims([Claim.model_validate({"subject": "unknown", "class": "existence", "predicate": "woodsmoke",
                                             "value": "rises thin from the rooftops"})], _empty_state(), AdjudicationRecord(),
                      [], rules=rules)
    assert (vs[0].verdict, vs[0].fix) == ("new_element", "write_on_mention")


def test_unknown_subject_that_acts_or_changes_is_still_cut() -> None:
    cs = [{"subject": "unknown", "class": "action", "predicate": "spits", "value": "into the dust"},
          {"subject": "unknown", "class": "existence", "predicate": "door", "value": "swings open", "asserts_change": True}]
    vs = check_claims(cs, _empty_state(), AdjudicationRecord(), [], rules=load_rules())
    assert [(v.verdict, v.fix) for v in vs] == [("unsourced_change", "cut")] * 2


def test_redraft_names_claims_and_never_asks_for_shorter(tmp_path: Path) -> None:
    bad = "Tam Harlan, a woman, watches you. The fog lies low on the water. What do you do?"
    good = "Tam Harlan, a man, watches you. The fog lies low on the water. What do you do?"
    model = look_model(narrator=[narr(bad), narr(good)])
    dock, ctx = setup(tmp_path, model)
    model.push(Role.CHECKER, chk(claim(0, dock.ferryman, "identity", "gender", "woman")),
               chk(claim(0, dock.ferryman, "identity", "gender", "man")))
    out = play_turn(ctx, "I look over the quay.")
    assert out.response.fiction == good
    msg = calls(model, Role.NARRATOR)[1].message
    assert "Tam Harlan, a woman" in msg and "contradicted" in msg and "he/him" in msg
    low = msg.lower()
    assert "keep every other sentence" in low or "keep every passing sentence" in low
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


def test_mention_name_prefers_the_noun() -> None:
    mk = lambda **k: Claim.model_validate({"subject": "unknown", **k})  # noqa: E731
    assert _mention_name(mk(**{"class": "existence", "predicate": "woodsmoke", "value": "rises thin"})) == "woodsmoke"
    assert _mention_name(mk(**{"class": "existence", "predicate": "present", "value": "a traveler near the post"})) \
        == "a traveler near the post"


def _empty_state() -> Any:
    from engine.store.projection import WorldState

    return WorldState()
