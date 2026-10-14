"""Companions (owner, 2026-10-12): full-class sheets the DM runs, at most 2, standard array, at the PC's level, resting
with the party."""
import asyncio
import json

import pytest

from dm import create, play
from dm import mechanics as m
from tests.test_create import BRAKKA, WREN
from tests.test_levels import WREN_LEVELS, built, rec


def game(tmp_path, pc=None):
    g = play.Game({"sheet": pc or built(BRAKKA, [])}, tmp_path / "save.json")
    return g, {t.name: t.handler for t in g.tools()}


def call(tools, tool, **a):
    res = asyncio.run(tools[tool](a))
    return res["content"][0]["text"], bool(res.get("is_error"))


def test_join_status_and_save(tmp_path) -> None:
    g, t = game(tmp_path)
    text, err = call(t, "change_party", add=WREN)
    assert not err and "Wren joined the party" in text and "Their sheet:" in text
    assert g.companions[0]["companion"] is True
    status = g.status()
    assert "Companion Wren" in status and status.count("XP") == 1  # only the PC's
    assert json.loads((tmp_path / "save.json").read_text(encoding="utf-8"))["companions"][0]["name"] == "Wren"
    again = play.Game(json.loads((tmp_path / "save.json").read_text(encoding="utf-8")), tmp_path / "save.json")
    assert again.companions[0]["name"] == "Wren"
    assert "## Companion: Wren" in play.system_prompt(g.sheet | {"opening": "x"}, g.companions)


def test_join_refusals(tmp_path) -> None:
    g, t = game(tmp_path)
    assert call(t, "change_party", add=WREN | {"ability_method": "point_buy"})[1]
    assert "already called" in call(t, "change_party", add=WREN | {"name": "Brakka"})[0]
    assert call(t, "change_party", add=WREN)[1] is False
    assert "already called" in call(t, "change_party", add=WREN)[0]
    assert call(t, "change_party", add=BRAKKA | {"name": "Tor"})[1] is False
    text, err = call(t, "change_party", add=BRAKKA | {"name": "Ula"})
    assert err and "full" in text
    assert "Wren left" in call(t, "change_party", remove="wren")[0] and len(g.companions) == 1
    assert call(t, "change_party", remove="Brakka")[1]


def test_who(tmp_path) -> None:
    g, t = game(tmp_path)
    call(t, "change_party", add=WREN)
    text, err = call(t, "change_pc", who="Wren", damage=3)
    assert not err and text.startswith("Wren:")
    assert g.companions[0]["hp"]["current"] == g.companions[0]["hp"]["max"] - 3
    assert g.sheet["hp"]["current"] == g.sheet["hp"]["max"]
    assert "no party member" in call(t, "change_pc", who="Nobody", damage=1)[0]
    assert "no XP" in call(t, "change_pc", who="Wren", xp_gained=50)[0]
    assert "whole party" in call(t, "change_pc", who="Wren", short_rest=True)[0]


def test_party_rests(tmp_path) -> None:
    g, t = game(tmp_path)
    call(t, "change_time", set={"day": 1, "time": "08:00"})
    call(t, "change_party", add=WREN)
    call(t, "change_pc", who="Wren", spend_slot=1, damage=2)
    text, err = call(t, "change_pc", long_rest=True, companions={"Wren": {"prepare_spells": ["Sleep", "Shield"]}})
    assert not err and "Wren: long rest" in text and "Day 1, 4:00 PM" in text  # the clock moves once
    w = g.companions[0]
    assert w["hp"]["current"] == w["hp"]["max"] and w["spell_slots"]["1"]["left"] == w["spell_slots"]["1"]["max"]
    assert w["spellcasting"]["prepared"] == ["Sleep", "Shield"]
    # a companion at 0 HP doesn't block the party's long rest
    call(t, "change_pc", who="Wren", damage=99)
    call(t, "change_time", advance={"hours": 16})  # one long rest in 24 hours
    text, err = call(t, "change_pc", long_rest=True)
    assert not err and "Wren: no benefit" in text and g.companions[0]["hp"]["current"] == 0
    # a bad companion choice refuses the whole rest
    before = g.clock["now"]
    assert call(t, "change_pc", short_rest=True, companions={"Wren": {"prepare_spells": ["Sleep"]}})[1]
    assert g.clock["now"] == before


def test_level_up_to_the_pcs_level(tmp_path) -> None:
    # owner 2026-10-12: a companion is already at the PC's level when found: built up to it (the prepared list too) before
    # the player sees one line, them joining at that level
    g, t = game(tmp_path, built(BRAKKA, [rec()]))
    shown = len([e for e in g.transcript if e["kind"] == "tool"])
    call(t, "change_party", add=WREN)
    assert g.companions[0]["joining"] and g.transcript[-1]["kind"] == "call"
    text = call(t, "level_up_options", who="Wren")[0]
    assert "can be taken now" in text and "had this level before they joined" in text and "prepare_spells" in text
    assert "prepare_spells" in call(t, "level_up", who="Wren", record=WREN_LEVELS[0])[0]
    assert call(t, "level_up", who="Wren", record=WREN_LEVELS[0], prepare_spells=["Sleep", "Fireball"])[1]  # not in the book
    assert g.companions[0]["level"] == 1
    five = ["Mage Armor", "Magic Missile", "Shield", "Sleep", "Burning Hands"]
    text, err = call(t, "level_up", who="Wren", record=WREN_LEVELS[0], prepare_spells=five)
    assert not err and "unchanged for now" not in text and "prepared: " in text
    w = g.companions[0]
    assert w["level"] == 2 and w["companion"] is True and "joining" not in w and w["spellcasting"]["prepared"] == five
    assert [e["text"] for e in g.transcript if e["kind"] == "tool"][shown:] == ["party: Wren joined the party, " + w["summary"]]
    assert "Prepared spells (5 of 5): Mage Armor" in g.status()
    # a later level-up is the usual kind: the prepared list waits for a long rest
    assert "only for a companion who is joining" in call(t, "level_up", who="Wren", record=WREN_LEVELS[1], prepare_spells=five)[0]
    assert "NOT YET" in call(t, "level_up_options", who="Wren")[0]
    assert "waits until the PC" in call(t, "level_up", who="Wren", record=WREN_LEVELS[1])[0]


def test_fights(tmp_path) -> None:
    g, t = game(tmp_path)
    call(t, "change_party", add=WREN)
    text, err = call(t, "add_combatants", combatants=[{"name": "pc", "initiative": 12}, {"name": "wren", "initiative": 15},
                                                      {"name": "Goblin 1", "initiative": 10, "hp": 7, "ac": 15}])
    assert not err and "Wren (15)" in text
    call(t, "change_pc", who="Wren", damage=2)
    w = g.companions[0]
    assert f"Wren (companion, initiative 15): HP {w['hp']['current']}/{w['hp']['max']}, AC {w['ac']}" in g.status()
    assert "use change_pc with who" in call(t, "change_creature", name="Wren", damage=1)[0]
    assert call(t, "next_turn")[0].startswith("Round 1, now: Wren. Wren's turn: one action,")
    text, err = call(t, "change_party", remove="Wren")
    assert not err and "Wren removed from the fight" in text and "Wren" not in g.status()


def test_pc_level_up_names_companions_behind(tmp_path) -> None:
    _, t = game(tmp_path, built(BRAKKA, []) | {"xp": 300})
    call(t, "change_party", add=WREN)
    text, err = call(t, "level_up", record=rec())
    assert not err and "Companions now below the PC's level: Wren (level 1)" in text


def test_dunmar_keeps_his_name() -> None:
    # the DM's real call (2026-10-12): the "(if proficient)" equipment check overwrote the name with the last option
    dunmar = {"name": "Dunmar", "race": "Human", "class": "Cleric", "ability_method": "standard_array",
              "base_scores": {"STR": 8, "DEX": 10, "CON": 13, "INT": 12, "WIS": 15, "CHA": 14},
              "choices": {"race.languages": "a", "class.proficiencies.1": ["c", "d"], "class.equipment.1": "a",
                          "class.equipment.2": "b", "class.equipment.3": "a", "class.equipment.4": "a",
                          "class.equipment.5": "Emblem", "background.languages": ["Dwarvish", "Giant"],
                          "background.equipment.1": "Emblem", "background.equipment.prayer": "a"},
              "cantrips": ["Light", "Sacred Flame", "Thaumaturgy"], "spells": [],
              "prepared": ["Sanctuary", "Healing Word"]}
    assert built(dunmar, [])["name"] == "Dunmar"
    # his first call put his domain spells in the prepared list, using up two of his four (owner: refuse it)
    _, errs = create.build(dunmar | {"prepared": ["Bless", "Cure Wounds", "Sanctuary", "Healing Word"]}, None)
    assert "prepared: Bless is already always prepared" in "\n".join(errs)
    s = built(dunmar, [])
    assert "Prepared spells (2 of 4): Sanctuary, Healing Word" in m.status(s)
    with pytest.raises(m.Refused, match="Cure Wounds is already always prepared"):
        m.change_pc(s, {"long_rest": True, "prepare_spells": ["Cure Wounds", "Sanctuary"]})


def test_who_inside_the_record(tmp_path) -> None:
    g, t = game(tmp_path, built(BRAKKA, [rec()]))
    text = call(t, "change_party", add=WREN)[0]
    assert "without asking the player" in text and "Wren is being built" in g.transcript[-1]["result"]
    five = ["Mage Armor", "Magic Missile", "Shield", "Sleep", "Burning Hands"]
    assert not call(t, "level_up", record=WREN_LEVELS[0] | {"who": "Wren"}, prepare_spells=five)[1]
    assert g.companions[0]["level"] == 2


def test_uses_marks_and_reminds(tmp_path) -> None:
    """Actions, bonus actions and reactions (owner, 2026-10-13): marked in the tracker with a note, never refused."""
    g, t = game(tmp_path)
    assert "uses is for a fight" in call(t, "roll", dice="1d20+5", reason="attack", uses="action")[0]
    call(t, "add_combatants", combatants=[{"name": "pc", "initiative": 12},
                                          {"name": "Imp", "initiative": 15, "hp": 10, "ac": 13}])
    text, _ = call(t, "next_turn")
    assert "Imp's turn: one action, one bonus action if a feature or spell gives one, its movement" in text
    text, err = call(t, "change_creature", name="Imp", conditions_added=["polymorphed"], uses="action")
    assert not err and text.endswith("(Imp has used its action: no more actions this turn.)")
    assert "Imp (initiative 15): HP 10/10, AC 13, polymorphed; action used" in g.status()
    text, err = call(t, "roll", dice="1d20+5", reason="Stealth to hide", uses="action")
    assert not err and text.endswith("(Imp had already used its action: a second one needs a feature that allows it.)")
    before = len(g.transcript)
    assert "no combatant named" in call(t, "roll", dice="1d20", reason="x", uses="reaction", by="Goblin")[0]
    assert len(g.transcript) == before + 1 and g.transcript[-1]["kind"] == "refused"  # nothing rolled
    text, err = call(t, "change_pc", damage=2, uses="reaction", by="pc")
    assert "no combatant named" in text  # by: the name as in the tracker
    text, err = call(t, "change_pc", damage=2, uses="reaction", by=g.sheet["name"])
    assert not err and "until the start of its next turn" in text and "AC" in g.status()
    call(t, "next_turn")
    assert "reaction used" not in g.status() and "action used" in g.status()  # the PC's turn: its reaction is back
    call(t, "next_turn")
    assert "used" not in g.status()
    text, err = call(t, "change_pc", uses="action", conditions_added=[])  # a Dodge or Ready: only the action is spent
    assert not err and text.endswith("has used its action: no more actions this turn.") and "action used" in g.status()
