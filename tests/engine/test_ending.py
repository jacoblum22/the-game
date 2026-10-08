"""Endings (T070; FR-009; 11.13; PR-11-6 simple): death only after the warning and the Threshold, the epilogue,
the ending menu (resumable), a new character in the same world, and retiring by choice."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from engine import ids
from engine.dm.ending import ending_choice, is_retire, retire_choice
from engine.dm.response import Response
from engine.game import Game, GameConfig
from engine.harm.state import DEAD, harm_state
from engine.harm.threshold import ending_state
from engine.llm.base import Role
from engine.llm.offline import ScriptedModel
from engine.store.events import EntityRecord, Event, SceneRecord
from engine.world.places import location
from tests.engine.test_game import quick_start, seed_oracle, settle
from tests.engine.test_turn_adjudication import beat, framer, reader

OFFLINE = GameConfig(offline=True)
LETHAL = {"stakes_source": "aware_opponent_or_observer", "stakes_heavy": True, "lethal": True,
          "obstacle": {"kind": "entity_defense", "obstacle_class": None, "tier": None, "entity": "foe.wight"},
          "threatened_cost": {"menu_id": "cost.harm", "form_intent": "its claws", "source_fact": None},
          "alternate_cost": {"menu_id": "cost.footing", "form_intent": "you slip", "source_fact": None}}
STRIKE = beat("hack at the wight", "verb.strike", target="foe.wight", verbs=("hack",), against_will=True)


def wight_scene(game: Game) -> None:
    """A lethal foe in a new conflict scene where the PC stands (test set-up, not play)."""
    store = game.store
    pc = store.state.meta["pc.active"]
    with store.transaction() as tx:
        tx.add(Event.of("entity_created", source="test", entity=EntityRecord(
            id="foe.wight", kind="adversary", name="the wight",
            data={"threat_advisory": "lethal", "lethal_context": True, "defeat_disposition": "kill",
                  "attributes": {"agility": 2}, "defenses": {"guard": 40},
                  "attacks": [{"name": "claw", "severity": "S4"}]})))
        sc = tx.state.scene
        assert sc is not None
        # 01.6.11: harm from an aware party cites the fact that it is armed and hostile
        tx.add(Event.of("fact_set", {"source": "oracle"}, source="dm", rule_id="01.15.5", fact_id=tx.mint("fact"),
                        subject="foe.wight", predicate="wields", value="claws", visibility="shown"))
        tx.add(Event.of("scene_ended", source="test", scene_id=sc.scene_id, reason="test"))
        sid = tx.mint(ids.SCENE)
        tx.add(Event.of("scene_started", source="test", scene_id=sid, scene=SceneRecord(
            scene_id=sid, place_id=location(tx.state, pc), mode="conflict", cast_present=["foe.wight"],
            started_seq=tx.state.last_seq)))


def lethal(game: Game) -> dict[str, Any]:
    """LETHAL citing the wight's claws: harm from an aware party cites that it is armed and hostile (01.6.11)."""
    claws = next(f.id for f in game.store.state.facts.values() if f.subject == "foe.wight" and f.predicate == "wields")
    return {**LETHAL, "threatened_cost": {**LETHAL["threatened_cost"], "source_fact": claws}}


def attack(game: Game, model: ScriptedModel) -> tuple[Response, list[str]]:
    """One lethal attack; returns the last response and every choice id the step offered (in order)."""
    model.push(Role.READER, reader("DECLARATION", "I hack at the wight.", STRIKE))
    model.push(Role.FRAMER, framer(**lethal(game)))
    r = game.submit("I hack at the wight.")
    seen: list[str] = []
    for _ in range(4):
        if r.pause is None or r.pause.kind != "offer":
            break
        ids_ = [c.id for c in r.pause.choices]
        seen += ids_
        r = game.answer("continue" if "continue" in ids_ else "commit")
    return r, seen


def to_threshold(tmp_path: Path) -> tuple[Game, Response]:
    """Play a PC into a hopeless fight (a defense no mortal roll beats) until the Threshold's menu opens."""
    model = ScriptedModel()
    game, r = Game.new(tmp_path / "g.db", OFFLINE, seed=5, model=model)
    r = quick_start(game, seed_oracle(game, r))
    assert r.phase == "play"
    wight_scene(game)
    first: list[str] = []
    for i in range(12):
        r, seen = attack(game, model)
        first = seen if i == 0 else first
        if r.pause is not None and r.pause.kind == "last_chance":
            break
    assert first[:2] == ["continue", "withdraw"]  # the lethal warning came first (07.3), before any offer
    assert r.pause is not None and r.pause.kind == "last_chance"
    st = game.store.state
    pc = st.meta["pc.active"]
    assert st.fact_value(pc, "lethal_key") and ending_state(st) is None  # Key 1 holds; nobody is dead yet
    return game, r


def test_death_after_warning_and_threshold_then_epilogue_and_a_new_character(tmp_path: Path) -> None:
    game, r = to_threshold(tmp_path)
    model = game.model
    assert isinstance(model, ScriptedModel)
    st = game.store.state
    pc = st.meta["pc.active"]
    r = game.answer("lc.last_stand")
    assert r.phase == "play" and ending_state(game.store.state) is None  # the stand is the next turn
    model.push(Role.READER, reader("DECLARATION", "I hack at the wight.", STRIKE))
    model.push(Role.FRAMER, framer(**LETHAL))
    r = settle(game, game.submit("I fight on."))
    st = game.store.state
    assert harm_state(st, pc) == DEAD and ending_state(st) == "death"
    assert r.phase == "ending" and r.pause is not None and r.pause.kind == "ending"
    assert [c.id for c in r.pause.choices] == ["new_character", "new_world", "quit"]
    assert r.oof_blocks[-1].kind == "EPILOGUE" and "is dead" in r.oof_blocks[-1].text
    assert st.meta[f"legacy.{pc}"]["ending"] == "remembered" and st.fact_value(pc, "exists") == "dead"
    assert st.meta["game.phase"] == "ending"
    assert game.turn_record(r.turn_id or "").input_verbatim == "(epilogue)"  # type: ignore[union-attr]

    game.close()  # quit at the ending menu
    game, back = Game.open(tmp_path / "g.db", OFFLINE, model=model)
    assert back.phase == "ending" and back.pause == r.pause and back.oof_blocks[-1] == r.oof_blocks[-1]
    assert game.submit("hmm").pause == r.pause  # words that pick nothing: the menu again
    r = game.new_character()
    assert r.phase == "creation" and r.pause is not None and r.pause.kind == "create_step"
    r = quick_start(game, r, name="Ash, he/him")
    st = game.store.state
    new_pc = st.meta["pc.active"]
    assert r.phase == "play" and new_pc != pc and st.entities[new_pc].name == "Ash"
    assert st.meta["opening.pc"] == new_pc and st.scene is not None and r.fiction
    assert ending_state(st) is None and "foe.wight" in st.entities  # the same world
    assert game.store.rebuild() == game.store.state
    game.close()


def test_retiring_by_choice(tmp_path: Path) -> None:
    game, r = Game.new(tmp_path / "g.db", OFFLINE, seed=3, model=ScriptedModel())
    r = quick_start(game, seed_oracle(game, r))
    r = game.submit("I retire.")
    assert r.pause is not None and r.pause.kind == "clarify" and [c.id for c in r.pause.choices] == [
        "retire", "keep_playing"]
    r = game.answer("keep_playing")
    assert r.phase == "play" and r.pause is None and ending_state(game.store.state) is None
    r = game.submit("I want to retire my character")
    game.close()  # quit at the question: it comes back
    game, back = Game.open(tmp_path / "g.db", OFFLINE)
    assert back.pause == r.pause
    r = game.submit("yes")
    st = game.store.state
    assert ending_state(st) == "retirement" and r.phase == "ending" and r.pause is not None
    assert st.meta[f"legacy.{st.meta['pc.active']}"]["ending"] == "retire_to_a_life"
    game.close()
    assert Game.replay(tmp_path / "g.db").identical


def test_answer_parsers() -> None:
    assert is_retire("I retire.") and is_retire("I'd like to retire") and is_retire("retire my character")
    assert not is_retire("The old soldier retired years ago.")
    assert retire_choice("1") == "retire" and retire_choice("2") == "keep_playing" and retire_choice("no") == (
        "keep_playing")
    assert ending_choice("1") == "new_character" and ending_choice("a new world please") == "new_world"
    assert ending_choice("quit") == "quit" and ending_choice("hmm") is None
