"""Fixes from the second offline smoke game: reach notes in words, the offline Framer's stakes, World reactions
only from the NPCs present and engaged, kit item names, the scene agenda in the recap, and the opening's inciting
incident surviving the claim check."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from engine.audit.claims import check_claims
from engine.data.loader import load_rules
from engine.dm.adjudication import AdjudicationRecord, BeatEntry
from engine.dm.creation import _item_name
from engine.dm.roles.narrator import record_text
from engine.llm.base import Packet, Role
from engine.llm.offline import OfflineModel, ScriptedModel, _npc_act, _reach_sentence, enum_at
from engine.store.projection import WorldState
from engine.world.places import location, reachable
from tests.engine.test_game import to_play

RULES = load_rules()
SOURCES = ["aware_opponent_or_observer", "hazard", "height_or_depth", "listening_clock", "damageable_item",
           "goodwill_or_trust", "consumed_resource"]
MENUS = ["cost.harm", "cost.footing", "cost.exposure", "cost.gear", "cost.twist", "cost.shortfall"]


def _framer_schema() -> dict[str, Any]:
    def enum(*v: str) -> dict[str, Any]:
        return {"type": "string", "enum": list(v)}

    cost = {"type": "object", "properties": {"menu_id": enum(*MENUS), "form_intent": {"type": "string"}}}
    return {"type": "object", "properties": {
        "anchor": enum("anc.01_18_11", "anc.01_18_8"), "attribute": enum("might", "agility"),
        "obstacle": {"type": "object", "properties": {"kind": enum("tier"), "tier": enum("easy", "moderate", "hard"),
                                                      "entity": {"type": ["string", "null"]}}},
        "stakes": {"type": "object", "properties": {"source": enum("none", *SOURCES), "threatened_cost": cost,
                                                     "alternate_cost": cost}}}}


def _frame(beat: str, verb: str, target: str = "none", view: str = "") -> dict[str, Any]:
    msg = (f"beat: {beat}\nintent: {beat}\nmethod: {beat}\ngate: G1 (normal) verb: verb.{verb} licence: none\n"
           f"target: {target}")
    out = OfflineModel().propose(Role.FRAMER, _framer_schema(), Packet(message=msg, view=view))
    return {**out, **out["stakes"]}  # the paired stakes choice, read flat below


# ------------------------------------------------------------------------------------------- 1. reach in words


def test_reach_note_is_a_sentence_not_a_raw_ladder_line() -> None:
    assert _reach_sentence("limited: partway (half the height, a ledge)") == "You get partway: half the height, a ledge."
    assert _reach_sentence("standard: the whole distance") == ""  # what was intended: the result line says it
    assert _reach_sentence("limited: cond.grabbed S1 (held)") == ""  # ids and numbers stay out of fiction
    assert _reach_sentence("great: more than asked (help, information, a favor)").startswith("Better than that")


def _fiction(out: dict) -> str:  # type: ignore[type-arg]
    return str(out["passage"])


def test_record_line_gives_the_reach_rung_and_words_without_ids() -> None:
    rec = AdjudicationRecord(turn_id="turn.1", pc="pc.wren")
    rec.beats = [BeatEntry(beat_id="beat.1", restatement="You climb the wall", degree="success", reach="limited",
                           reach_words=["partway (half the height, a ledge)"]),
                 BeatEntry(beat_id="beat.2", restatement="You grab him", degree="success", reach="standard",
                           reach_words=["cond.grabbed S2"])]
    text = record_text(WorldState(), rec, rules=RULES)
    assert "delivered: limited: partway (half the height, a ledge)" in text
    assert "S2" not in text and "cond." not in text
    fiction = _fiction(OfflineModel().propose(Role.NARRATOR, {"type": "object"}, Packet(message=text)))
    assert "You get partway: half the height, a ledge." in fiction and "Partway (" not in fiction


# ------------------------------------------------------------------------------------------- 2. stakes


def test_offline_framer_names_what_the_act_plainly_risks() -> None:
    climb = _frame("You climb onto the roof", "exert")
    assert climb["source"] == "height_or_depth" and climb["threatened_cost"]["menu_id"] == "cost.harm"
    assert climb["alternate_cost"]["menu_id"] == "cost.shortfall" and climb["obstacle"]["tier"] == "moderate"
    hit = _frame("You attack the guard", "strike", target="npc.guard")
    # harm from an aware party needs the cited fact that they are armed (01.6.11): the offline Framer threatens footing
    assert hit["source"] == "aware_opponent_or_observer" and hit["threatened_cost"]["menu_id"] == "cost.footing"
    sneak = _frame("You sneak past the watch", "sneak")
    assert sneak["source"] == "aware_opponent_or_observer"
    assert sneak["threatened_cost"]["menu_id"] == "cost.exposure"
    assert _frame("You lift the crate", "exert")["source"] == "none"  # nothing plainly at risk: Safe
    assert _frame("You swing at the air", "strike")["source"] == "none"  # no one present to hit back


def test_a_climb_in_play_is_offered_as_risky(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path, OfflineModel(), seed=11)
    r = game.submit("I climb the wall.")
    assert r.pause is not None and r.pause.kind == "offer"
    offer = next(b.text for b in r.oof_blocks if b.kind == "OFFER")
    assert "— a setback." in offer and "a setback that fits the moment" not in offer  # risky: S2 in words


# ------------------------------------------------------------------------------------------- 3. the world


def test_npc_row_is_worded_differently_when_it_repeats() -> None:
    first = _npc_act("Corwen", "offers partial help", "")
    again = _npc_act("Corwen", "offers partial help", f"You ask. {first} What do you do?")
    assert first == "Corwen offers partial help." and again != first and "help" in again


def test_only_npcs_present_after_a_cut_act(tmp_path: Path) -> None:
    model = ScriptedModel()
    game, _ = to_play(tmp_path, model, seed=11)
    st = game.store.state
    assert st.scene is not None
    left = [st.entities[n].name for n in st.scene.cast_present if st.entities[n].kind == "npc"]
    assert left
    here = location(game.store.state)
    dest = next(x.to for x in reachable(game.store.state, here) if x.to != here)

    def everyone(schema: dict[str, Any], packet: Any) -> dict[str, Any]:  # every NPC still here reacts
        return {"responses": [{"npc": n, "want_engaged": "none", "refusal_engaged": "none",
                               "table_context": {"tags": []}} for n in enum_at(schema, "responses", "[]", "npc")]}

    model.push(Role.WORLD, everyone)
    r = game.submit(f"I head to {game.store.state.entities[dest].name}.")
    assert location(game.store.state) == dest
    st = game.store.state
    assert st.scene is not None
    gone = [n for n in left if n not in {st.entities[i].name for i in st.scene.cast_present}]
    assert gone and not any(n in r.fiction for n in gone)


def test_a_look_around_draws_no_npc_reaction(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path, OfflineModel(), seed=11)
    r = game.submit("I look around.")
    assert " is here." in r.fiction or " are here." in r.fiction  # everyone positioned here is present (P-095)
    assert not any(w in r.fiction for w in ("offers", "helps", "withdraws", "asks you", "threat"))


# ------------------------------------------------------------------------------------------- 4. sheet, recap


def test_kit_items_take_their_base_item_names() -> None:
    assert _item_name("item.shield.light", rules=RULES) == "round shield"
    assert _item_name("item.tool.light", rules=RULES) == "torches"
    assert _item_name("item.tool.container", "pack and bedroll", RULES) == "pack and bedroll"
    assert _item_name("item.shield.light") == "light"  # no rules: the tag's last segment


def test_sheet_lists_each_item_once_by_name_and_recap_has_no_placeholder(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path, OfflineModel(), seed=11)
    carrying = next(ln for ln in game.codex("sheet").text.splitlines() if "Carrying:" in ln)
    items = carrying.split(":", 1)[1].split(", ")
    assert len(items) == len(set(items)) and "round shield" in items
    game.close()
    from engine.game import Game, GameConfig

    game, r = Game.open(tmp_path / "g.db", GameConfig(offline=True), model=OfflineModel())
    recap = next(b.text for b in r.oof_blocks if b.kind == "RECAP")
    assert "follow the most pressing open thread" not in recap
    assert "Scene: What comes of it: " in recap  # the opening scene's question, from the incident


# ------------------------------------------------------------------------------------------- 5. the opening


def test_claim_restating_the_records_incident_is_supported() -> None:
    rec = AdjudicationRecord(turn_id="turn.1", pc="pc.wren")
    rec.notes = ["the inciting incident: a rider dies in the market with a message for someone who is not there"]
    claim = {"sentence": 1, "subject": "unknown", "class": "harm_condition", "predicate": "dies",
             "value": "in the market with a message for someone who is not there", "asserts_change": True}
    from engine.dm.handles import items

    cited = {1: items(rec, names={})}  # spec 006: the sentence cites the incident's line
    assert check_claims([claim], WorldState(), rec, rules=RULES, cited=cited)[0].verdict == "supported"
    other = {**claim, "predicate": "stabs", "value": "the mayor with a knife in the hall"}
    assert check_claims([other], WorldState(), rec, rules=RULES, cited=cited)[0].verdict != "supported"


def test_opening_keeps_the_inciting_incident_and_offers_the_leads(tmp_path: Path) -> None:
    game, r = to_play(tmp_path, OfflineModel(), seed=11)
    incident = game.store.state.meta["world.opening"]["inciting"]["text"]
    assert incident[:1].upper() + incident[1:] in r.fiction
    narr = [row for row in game.store.model_calls(r.turn_id) if row["role"] == "narrator"]
    packet = str(narr[-1]["request"])
    assert "a lead to make noticeable:" in packet and "a lead to make noticeable: the incident itself" not in packet


def test_offline_framer_changes_approach_when_asked() -> None:
    msg = ("beat: You climb the wall\nintent: x\nmethod: x\ngate: G1 (normal) verb: verb.exert licence: none\n"
           "target: none\nThe player chose CHANGE at the OFFER: propose a different approach")
    out = OfflineModel().propose(Role.FRAMER, _framer_schema(), Packet(message=msg))
    assert out["attribute"] == "agility"  # not the verb's default (might) again


def test_offline_narrator_words_a_refused_rest() -> None:
    msg = "ADJUDICATION RECORD:\n- note: a long rest is not possible now: one long rest a day"
    fiction = _fiction(OfflineModel().propose(Role.NARRATOR, {"type": "object"}, Packet(message=msg)))
    assert fiction == "There is no rest to be had yet. What do you do?"


def test_seed_texts_speak_to_the_player_as_you() -> None:
    from engine.dm.player_text import clean, second_person

    assert second_person("a stranger asks after the PC by name") == "a stranger asks after you by name"
    assert second_person("a powerful person offers the character work") == "a powerful person offers you work"
    assert second_person("The PC is hunted; the character's vow") == "You are hunted; your vow"
    assert second_person("the character sheet") == "the character sheet"
    # clean() (every OOF block) changes only "the PC": engine text may name "the character" on purpose
    assert clean("the character's vow, for the PC's sister") == "the character's vow, for your sister"
