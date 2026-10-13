"""Companions (owner, 2026-10-12): full-class sheets the DM runs, at most 2, standard array, at the PC's level, resting
with the party."""
import asyncio
import json

from dm import play
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
    text, err = call(t, "change_pc", long_rest=True)
    assert not err and "Wren: no benefit" in text and g.companions[0]["hp"]["current"] == 0
    # a bad companion choice refuses the whole rest
    before = g.clock["now"]
    assert call(t, "change_pc", short_rest=True, companions={"Wren": {"prepare_spells": ["Sleep"]}})[1]
    assert g.clock["now"] == before


def test_level_up_to_the_pcs_level(tmp_path) -> None:
    g, t = game(tmp_path, built(BRAKKA, [rec()]))
    call(t, "change_party", add=WREN)
    assert "can be taken now" in call(t, "level_up_options", who="Wren")[0]
    err = call(t, "level_up", who="Wren", record=WREN_LEVELS[0])[1]
    assert not err and g.companions[0]["level"] == 2 and g.companions[0]["companion"] is True
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
    assert call(t, "next_turn")[0] == "Round 1, now: Wren."
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
              "prepared": ["Bless", "Cure Wounds", "Sanctuary", "Healing Word"]}
    assert built(dunmar, [])["name"] == "Dunmar"


def test_who_inside_the_record(tmp_path) -> None:
    g, t = game(tmp_path, built(BRAKKA, [rec()]))
    text = call(t, "change_party", add=WREN)[0]
    assert "without asking the player" in text and g.transcript[-1]["text"] == "party: Wren joined the party, " + g.companions[0]["summary"]
    assert not call(t, "level_up", record=WREN_LEVELS[0] | {"who": "Wren"})[1] and g.companions[0]["level"] == 2
