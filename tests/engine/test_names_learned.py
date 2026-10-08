"""12.10.2: an NPC's name reaches the narration only once the PC has learned it (P-069, P-070)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from engine.audit.claims import check_claims
from engine.audit.fallback import _you
from engine.data.loader import load_rules
from engine.dm.adjudication import AdjudicationRecord
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


def test_the_journal_lists_only_people_introduced(tmp_path: Path) -> None:
    dock, _ = setup(tmp_path, ScriptedModel({}))
    text = what_you_know(dock.state, rules=RULES).text
    assert "Tam Harlan" not in text


def test_a_second_verb_after_and_is_second_person() -> None:
    """Breaker turn 26: 'You cross the timber yard to the doors and goes out into the lane'."""
    out = _you("Lorard crosses the timber yard to the doors and goes out into the lane", ["Lorard"], [])
    assert out == "you cross the timber yard to the doors and go out into the lane"
    assert _you("Lorard watches the cart and the dogs", ["Lorard"], []) == "you watch the cart and the dogs"


def test_seeded_people_and_walk_ons_are_strangers_until_introduced(tmp_path: Path) -> None:
    """P-069/P-070: the seed's people and a walk-on met mid-scene are named to neither narrator nor journal."""
    from engine.world.social import learn_name, meet_npc
    from tests.engine.test_world_support import Game

    g = Game(tmp_path)
    walk_on = g.run(lambda ctx: meet_npc(ctx, "ferryman", g.world.incident.place, reuse=False))
    st = g.state
    npcs = [e for e in st.entities.values() if e.kind == "npc" and e.id not in st.seals]
    assert npcs and not any(name_known(st, e.id) for e in npcs)
    view = render_view(scene_view(st)) + scene_setting(st) + what_you_know(st, rules=RULES).text
    assert not [e.name for e in npcs if e.name in view]
    assert name_of(st, walk_on) == "the ferryman"
    g.run(lambda ctx: learn_name(ctx, g.pc, walk_on))
    st = g.state
    assert name_of(st, walk_on) == st.entities[walk_on].name
    assert st.entities[walk_on].name in what_you_know(st, rules=RULES).text  # met and introduced
