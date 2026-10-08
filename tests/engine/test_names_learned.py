"""12.10.2: an NPC's name reaches the narration only once the PC has learned it (P-069, P-070)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from engine.audit.claims import check_claims
from engine.audit.fallback import plain_fallback
from engine.data.loader import load_rules
from engine.dm.adjudication import AdjudicationRecord, BeatEntry
from engine.dm.codex import what_you_know
from engine.dm.packet import render_view, scene_setting, scene_view
from engine.dm.roles.checker import entity_lines
from engine.dm.roles.narrator import name_of
from engine.dm.turn import play_answer, play_turn
from engine.llm.base import Role
from engine.llm.offline import ScriptedModel
from engine.store.views import name_known
from tests.engine.test_turn_adjudication import QUIET_WORLD, beat, framer, reader, setup
from tests.engine.test_turn_narration import calls, chk, claim, narr
from tests.fixtures import scene_dock

RULES = load_rules()


@pytest.fixture(autouse=True)
def _stranger(monkeypatch: pytest.MonkeyPatch) -> None:
    """The ferryman as a walk-on the PC has not been introduced to (the seed and walk-ons carry this flag)."""
    make = scene_dock._entity

    def entity(tx: Any, kind: str, name: str, *, data: dict[str, Any], **kw: Any) -> str:
        flag = {"name_known": False} if name == "Tam Harlan" else {}
        return make(tx, kind, name, data={**data, **flag}, **kw)

    monkeypatch.setattr(scene_dock, "_entity", entity)


def test_the_narrator_sees_a_stranger_by_role_until_named(tmp_path: Path) -> None:
    dock, _ = setup(tmp_path, ScriptedModel({}))
    st = dock.state
    view, setting = render_view(scene_view(st)), scene_setting(st)
    assert "Tam Harlan" not in setting and "present: the ferryman" in setting
    assert "name: the ferryman" in view and "does not know their name" in view and "Tam Harlan" not in view
    assert "Sela Vey" in view  # an NPC without the flag is unchanged
    assert name_of(st, dock.ferryman) == "the ferryman"
    assert entity_lines(st, [dock.ferryman])[0].startswith(f"{dock.ferryman}: the ferryman, Tam Harlan")
    rec = AdjudicationRecord(pc=dock.pc)
    name = {"subject": dock.ferryman, "class": "identity", "predicate": "name", "value": "Tam Harlan"}
    assert check_claims([name], st, rec, [], rules=RULES)[0].verdict == "contradicted"


def test_asking_who_they_are_learns_the_name_and_the_check_keeps_it(tmp_path: Path) -> None:
    ask = "I ask the ferryman his name."
    talk = beat("ask the ferryman his name", "verb.talk", target="npc.tam_harlan", verbs=("ask",))
    text = '"Tam Harlan," the ferryman says. What do you do?'
    model = ScriptedModel({Role.READER: [reader("DECLARATION", ask, talk)], Role.FRAMER: [framer()],
                           Role.WORLD: [QUIET_WORLD]})
    dock, ctx = setup(tmp_path, model)
    assert play_turn(ctx, ask).adjudication.pause.kind == "offer"
    ctx.rng.faces = [19]  # type: ignore[attr-defined]
    model.push(Role.NARRATOR, narr(text))
    model.push(Role.CHECKER, chk(claim(0, "npc.tam_harlan", "identity", "name", "Tam Harlan")))
    out = play_answer(ctx, "commit")
    st = ctx.store.state
    assert name_known(st, dock.ferryman)
    assert "gives their name, in their own words: Tam Harlan" in calls(model, Role.NARRATOR)[0].message
    assert out.response.fiction == text and not out.response.flags.fallback_used
    assert "Tam Harlan" in render_view(scene_view(st))


def test_asking_a_third_partys_name_never_names_the_one_asked(tmp_path: Path) -> None:
    """P-113: "the name of the thief" put to the officer gave him his own name in his act; the narration then
    had him say it as the thief's, and the game took it as his. Only his own name or identity learns it."""
    from engine.dm.world_step import _ASKS_NAME

    ask = "I ask the ferryman his price for the name of the thief."
    talk = beat("ask the ferryman his price for the thief's name", "verb.talk", target="npc.tam_harlan",
                verbs=("ask",))
    model = ScriptedModel({Role.READER: [reader("DECLARATION", ask, talk)], Role.FRAMER: [framer()],
                           Role.WORLD: [QUIET_WORLD]})
    dock, ctx = setup(tmp_path, model)
    assert play_turn(ctx, ask).adjudication.pause.kind == "offer"
    ctx.rng.faces = [19]  # type: ignore[attr-defined]
    model.push(Role.NARRATOR, narr('"I don\'t know who took it," the ferryman says. What do you do?'))
    model.push(Role.CHECKER, chk())
    play_answer(ctx, "commit")
    assert not name_known(ctx.store.state, dock.ferryman)
    assert "gives their name" not in calls(model, Role.NARRATOR)[0].message
    for own in ("I ask the ferryman his name.", "What's your name?", "I ask her who she is.", "Who are you?",
                "I introduce myself."):
        assert _ASKS_NAME.search(own), own
    for other in ("the name of the thief", "his price for the thief's name", "why he gave me her name",
                  "I ask him who Lila Fairwick is"):
        assert not _ASKS_NAME.search(other), other


def test_the_journal_lists_only_people_introduced(tmp_path: Path) -> None:
    dock, _ = setup(tmp_path, ScriptedModel({}))
    text = what_you_know(dock.state, rules=RULES).text
    assert "Tam Harlan" not in text


def test_a_second_verb_after_and_is_second_person() -> None:
    """Breaker turn 26: 'You cross the timber yard to the doors and goes out into the lane'. The beat line is now
    rendered from the Reader's verb and target (B P4), so the restatement's second verb is never re-conjugated."""
    rec = AdjudicationRecord(pc="pc.lorard", beats=[BeatEntry(
        restatement="Lorard crosses the timber yard to the doors and goes out into the lane", actor="pc.lorard",
        verb="verb.move", targets=["loc.lane"], gate="G1", gate_words="no roll: trivial")])
    fb = plain_fallback(rec, names={"pc.lorard": "Lorard", "loc.lane": "the lane"}).fiction
    assert fb == "You move toward the lane. It works. What do you do?"


def test_setup_named_people_are_known_and_a_walk_on_is_the_figure(tmp_path: Path) -> None:
    """P-069/P-070: the people setup step 8 named are known from the start; the rest of the seed's people and a
    walk-on met mid-scene are named to neither narrator nor journal until introduced."""
    from engine.dm.mentions import write_mentions
    from engine.gen.world_seed import headline_people
    from engine.world.social import learn_name
    from tests.engine.test_world_support import Game

    g = Game(tmp_path)
    rec = g.world.record
    rulers = next(f["name"] for f in rec["factions"]["instances"] if f["id"].endswith(".rulers"))
    headline = {n["id"] for n in headline_people(rec["npcs"], rulers)}
    assert len(headline) == 4
    with g.store.transaction() as tx:
        figure = write_mentions([{"kind": "npc", "name": "the figure"}], tx=tx, rules=RULES,
                                rng=g.rng).created["the figure"]
    st = g.state
    view = render_view(scene_view(st))
    assert all(st.entities[i].name in view for i in headline)  # step 8 named them: the PC, a local, knows them
    others = [e for e in st.entities.values() if e.kind == "npc" and e.id not in headline and e.id not in st.seals]
    assert others and not any(name_known(st, e.id) for e in others)
    text = view + scene_setting(st) + what_you_know(st, rules=RULES).text
    assert not [e.name for e in others if e.name in text]
    assert name_of(st, figure) == "the figure"
    g.run(lambda ctx: learn_name(ctx, g.pc, figure))
    st = g.state
    assert name_of(st, figure) == st.entities[figure].name
    assert st.entities[figure].name in what_you_know(st, rules=RULES).text  # met and introduced
