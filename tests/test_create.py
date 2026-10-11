"""Character creation: hand-worked sheets, refusals, every race x class, and the play-tool changes it needs."""
import copy
import json
from pathlib import Path

import pytest

from dm import create, srd
from dm import mechanics as m
from tests.autochar import build_any

ARRAY = dict(zip(create.ABILITIES, [15, 10, 14, 8, 13, 12]))  # STR DEX CON INT WIS CHA

BRAKKA = {"name": "Brakka", "race": "dwarf", "class": "fighter", "ability_method": "standard_array", "base_scores": ARRAY,
          "choices": {"trait.tool-proficiency": ["Smith's Tools"], "class.proficiencies.1": ["Athletics", "Perception"],
                      "feature.fighter-fighting-style": ["Dueling"], "class.equipment.1": ["a"],
                      "class.equipment.2": [{"option": "a", "picks": ["Longsword"]}], "class.equipment.3": ["a"],
                      "class.equipment.4": ["b"], "background.languages": ["Giant", "Goblin"],
                      "background.equipment.1": ["Amulet"], "background.equipment.prayer": ["Prayer book"]}}

WREN = {"name": "Wren", "race": "elf", "class": "wizard", "ability_method": "standard_array",
        "base_scores": dict(zip(create.ABILITIES, [8, 14, 13, 15, 12, 10])),
        "choices": {"trait.high-elf-cantrip": ["Prestidigitation"], "trait.extra-language": ["Draconic"],
                    "class.proficiencies.1": ["Arcana", "Investigation"], "class.equipment.1": ["a"],
                    "class.equipment.2": ["a"], "class.equipment.3": ["a"], "background.languages": ["Celestial", "Giant"],
                    "background.equipment.1": ["Emblem"], "background.equipment.prayer": ["b"]},
        "cantrips": ["Fire Bolt", "Mage Hand", "Light"],
        "spells": ["Burning Hands", "Detect Magic", "Mage Armor", "Magic Missile", "Shield", "Sleep"],
        "prepared": ["Mage Armor", "Magic Missile", "Shield", "Sleep"]}

HILDA = {"name": "Hilda", "race": "dwarf", "class": "cleric", "ability_method": "point_buy",
         "base_scores": {"STR": 13, "DEX": 10, "CON": 14, "INT": 8, "WIS": 15, "CHA": 10},  # 5+2+7+0+9+2 = 25
         "choices": {"trait.tool-proficiency": ["a"], "class.proficiencies.1": ["Medicine", "History"],
                     "class.equipment.1": ["Warhammer"], "class.equipment.2": ["Chain Mail"], "class.equipment.3": ["a"],
                     "class.equipment.4": ["a"], "class.equipment.5": ["Reliquary"],
                     "background.languages": ["Celestial", "Giant"], "background.equipment.1": ["Amulet"], "background.equipment.prayer": ["a"]},
         "cantrips": ["Sacred Flame", "Guidance", "Spare the Dying"],
         "prepared": ["Guiding Bolt", "Healing Word", "Shield of Faith", "Sanctuary"]}


def built(ch: dict, rolled: list[int] | None = None) -> dict:
    sheet, errs = create.build(ch, rolled)
    assert sheet, errs
    return sheet


def problems(ch: dict, **changes) -> str:
    ch = copy.deepcopy(ch) | changes
    sheet, errs = create.build(ch)
    assert sheet is None
    return "\n".join(errs)


def test_fighter_matches_the_hand_made_sheet() -> None:
    s = built(BRAKKA)
    assert (s["ac"], s["hp"]["max"], s["passive_perception"]) == (18, 14, 14)  # chain 16 + shield; 10+3+1 toughness
    assert s["attacks"][0].startswith("Longsword: +4 to hit, 1d8+4")  # Dueling +2
    assert "Athletics +4*" in s["skills"] and "Insight +4*" in s["skills"] and "Religion +1*" in s["skills"]
    assert s["resources"]["Second Wind"]["recharge"] == "short" and s["coins_cp"] == 1500
    # the Acolyte's gear, including what the dataset lacks; an explorer's pack adds no vestments or incense
    assert {k: s["items"].get(k) for k in ("Vestments", "Stick of incense", "Prayer book", "Clothes, common", "Pouch")} \
        == {"Vestments": 1, "Stick of incense": 5, "Prayer book": 1, "Clothes, common": 1, "Pouch": 1}
    assert "Prayer wheel" in built(WREN)["items"]
    assert "Heavy Armor" in create.options_text("dwarf", "cleric")  # granted by the Life Domain, shown up front


def test_wizard() -> None:
    s = built(WREN)  # DEX 16, INT 16 after High Elf
    sc = s["spellcasting"]
    assert (s["hp"]["max"], s["ac"], sc["save_dc"], sc["attack_bonus"], sc["prepare_count"]) == (7, 13, 13, 5, 4)
    assert len(sc["spellbook"]) == 6 and sc["racial_cantrips"] == ["Prestidigitation (High Elf, INT)"]
    assert s["spell_slots"] == {"1": {"max": 2, "left": 2, "recharge": "long"}}


def test_life_cleric() -> None:
    s = built(HILDA)  # WIS 16, CON 16: HP 8+3+1; heavy armor from the Life Domain
    sc = s["spellcasting"]
    assert (s["hp"]["max"], s["ac"], sc["save_dc"], sc["prepare_count"]) == (12, 18, 13, 4)
    assert sc["always_prepared"] == ["Bless", "Cure Wounds"]


def test_refusals() -> None:
    assert "budget is 27" in problems(HILDA, base_scores={"STR": 15, "DEX": 15, "CON": 15, "INT": 10, "WIS": 8, "CHA": 8})
    assert "no option 'Athletics'" in problems(WREN, choices=WREN["choices"] | {"class.proficiencies.1": ["Athletics", "Arcana"]})
    assert "choose exactly 6" in problems(WREN, spells=WREN["spells"] + ["Thunderwave"])
    assert "not a level-1 wizard spell in the spellbook" in problems(WREN, prepared=["Thunderwave", "Sleep", "Shield", "Mage Armor"])
    assert "gained twice" in problems(HILDA, choices=HILDA["choices"] | {"class.proficiencies.1": ["Insight", "History"]})
    assert "no scores have been rolled" in problems(BRAKKA, ability_method="rolled")
    ok = copy.deepcopy(BRAKKA) | {"ability_method": "rolled", "base_scores": dict(zip(create.ABILITIES, [9, 17, 12, 11, 7, 14]))}
    assert built(ok, [17, 14, 12, 11, 9, 7])["scores"]["DEX"] == 17


def test_every_race_and_class_builds() -> None:
    bad = {}
    for r in srd.table("Races"):
        for c in srd.table("Classes"):
            sheet, errs = build_any(r, c)
            if not sheet:
                bad[(r, c)] = errs
    # the test helper picks Insight for both the half-elf and the bard; refusing that is correct
    assert all(all("gained twice" in e for e in errs) for errs in bad.values()) and len(bad) <= 1, bad


def test_play_tool_changes() -> None:
    w = built(WREN)
    w, _ = m.change_pc(w, {"ac_set": 16, "ac_reason": "Mage Armor: 13 + DEX"})
    assert "AC 16 (Mage Armor" in m.status(w)
    w, _ = m.change_pc(w, {"ac_reset": True})
    assert w["ac_now"] is None
    with pytest.raises(m.Refused):
        m.change_pc(w, {"prepare_spells": ["Sleep"]})  # only with a long rest
    with pytest.raises(m.Refused):
        m.change_pc(w, {"long_rest": True, "prepare_spells": ["Thunderwave"]})  # not in the spellbook
    w, _ = m.change_pc(w, {"spellbook_add": ["Thunderwave"], "coin_change_gp": -15})
    w, _ = m.change_pc(w, {"long_rest": True, "prepare_spells": ["Thunderwave", "Shield"]})
    assert w["spellcasting"]["prepared"] == ["Thunderwave", "Shield"]
    with pytest.raises(m.Refused):
        m.change_pc(w, {"spellbook_add": ["Cure Wounds"]})  # not a wizard spell

    warlock = build_any("tiefling", "warlock")[0]
    assert warlock
    warlock, _ = m.change_pc(warlock, {"spend_slot": 1})
    warlock, _ = m.change_pc(warlock, {"short_rest": True})
    assert warlock["spell_slots"]["1"]["left"] == warlock["spell_slots"]["1"]["max"]

    paladin = build_any("human", "paladin")[0]
    assert paladin
    paladin, _ = m.change_pc(paladin, {"use_resource": "Lay on Hands", "resource_amount": 3})
    assert paladin["resources"]["Lay on Hands"]["left"] == 2
    with pytest.raises(m.Refused):
        m.change_pc(paladin, {"use_resource": "Lay on Hands", "resource_amount": 3})


def test_hand_made_wizard_prepares_from_its_spellbook() -> None:
    w = json.loads((Path(__file__).parent.parent / "dm" / "characters" / "wizard.json").read_text(encoding="utf-8"))
    w, _ = m.change_pc(w, {"long_rest": True, "prepare_spells": ["Burning Hands", "Detect Magic", "Shield", "Sleep"]})
    assert "Prepared spells: Burning Hands" in m.status(w)
