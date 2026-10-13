"""Character creation: hand-worked sheets, refusals, every race x class, and the play-tool changes it needs."""
import copy
import json
from pathlib import Path

import pytest

from dm import create, srd
from dm import mechanics as m
from tests.autochar import build_any, character

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
    assert "Prepared spells (4 of 4): Burning Hands" in m.status(w)


def test_games_started_in_the_same_second_get_separate_saves(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from dm import play
    monkeypatch.setattr(play, "SAVES", tmp_path)
    names = [play.new_save("wren-20261011-161351").name for _ in range(3)]
    assert names == ["wren-20261011-161351.json", "wren-20261011-161351-2.json", "wren-20261011-161351-3.json"]


def test_draconic_sorcerer_speaks_draconic() -> None:
    # Dragon Ancestor: "You can speak, read, and write Draconic."
    sheet = build_any("human", "sorcerer")[0]
    assert sheet and "Draconic" in sheet["languages"].split(", ")
    dragonborn = build_any("dragonborn", "sorcerer")[0]  # already speaks it: listed once
    assert dragonborn and dragonborn["languages"].split(", ").count("Draconic") == 1


def ranger(**choices: object) -> dict:
    """A human ranger from autochar's choices (the first shift that builds; some first picks collide with the
    background's skills), with `choices` replacing or adding to them."""
    ch = next(c for c in (character("human", "ranger", n) for n in range(40)) if create.build(c)[0])
    return ch | {"choices": ch["choices"] | choices}


def unarmed(sheet: dict) -> str:
    return next(a for a in sheet["attacks"] if a.startswith("Unarmed strike"))


def test_ranger_favored_enemy_language_and_humanoid_races() -> None:
    fe, lang, races = "feature.favored-enemy-1-type", create.ENEMY_LANGUAGE_ID, create.ENEMY_RACES_ID
    s = built(ranger(**{fe: ["Fiends"], lang: ["Abyssal"]}))
    assert "Abyssal" in s["languages"].split(", ") and "Language learned: Abyssal." in "".join(s["features"])
    assert "Abyssal" in create.options_text("human", "ranger") and races in create.options_text("human", "ranger")
    none = built(ranger(**{fe: ["Beasts"], lang: ["None (they speak no language)"]}))
    assert none["languages"] == built(ranger(**{fe: ["Beasts"], lang: ["Common"]}))["languages"]
    no_lang = ranger(**{fe: ["Fiends"]})
    del no_lang["choices"][lang]
    assert f"choices.{lang}: missing" in problems(no_lang)
    # "humanoids" means two races of humanoid
    assert races in problems(ranger(**{fe: ["Humanoids"], lang: ["Orc"]}))
    for bad in (["gnolls"], ["gnolls", "Gnolls"], ["gnolls", ""], "gnolls and orcs"):
        assert races in problems(ranger(**{fe: ["Humanoids"], lang: ["Orc"], races: bad}))
    h = built(ranger(**{fe: ["Humanoids"], lang: ["Orc"], races: ["gnolls", "orcs"]}))
    assert "Humanoid races: gnolls and orcs." in "".join(h["features"])
    assert "not needed" in problems(ranger(**{fe: ["Undead"], lang: ["Common"], races: ["gnolls", "orcs"]}))


def test_cleric_warhammer_needs_proficiency() -> None:
    human = copy.deepcopy(HILDA) | {"race": "human"}  # a human cleric has simple weapons only
    human["choices"] = {k: v for k, v in HILDA["choices"].items() if k != "trait.tool-proficiency"} | {
        "race.languages": ["Elvish"]}
    assert "Warhammer is only an option if the character is proficient" in problems(human)
    assert built(human | {"choices": human["choices"] | {"class.equipment.1": ["Mace"]}})["items"]["Mace"] == 1
    assert "Warhammer" in built(HILDA)["items"]  # the dwarf's Dwarven Combat Training covers it


def test_unarmed_strike_damage_is_never_negative() -> None:
    # Melee Attacks: 1 + Strength modifier; Damage Rolls: "it is possible to deal 0 damage, but never negative damage"
    assert unarmed(built(WREN)).endswith("0 bludgeoning")  # STR 8 (-1): 1 - 1 = 0
    weak = WREN | {"ability_method": "rolled", "base_scores": WREN["base_scores"] | {"STR": 6}}  # STR 6 (-2): 1 - 2 = -1
    assert unarmed(built(weak, [6, 14, 13, 15, 12, 10])).endswith("0 bludgeoning")
    assert unarmed(built(BRAKKA)).endswith("3 bludgeoning")  # STR 15 (+2)


def test_prepared_spells_are_a_maximum() -> None:
    # Wizard, cleric and druid: "a number of ... spells equal to your ... modifier + your ... level (minimum of one spell)"
    assert built(WREN | {"prepared": ["Shield"]})["spellcasting"]["prepared"] == ["Shield"]
    assert built(HILDA | {"prepared": ["Command"]})["spellcasting"]["prepared"] == ["Command"]
    assert "Bless is already always prepared" in problems(HILDA, prepared=["Bless"])
    for ch in (WREN, HILDA):
        assert "1 to 4" in problems(ch, prepared=[])
        assert "1 to 4" in problems(ch, prepared=(ch["prepared"] + ["Detect Magic"] if ch is WREN else ch["prepared"] + ["Command"]))
    assert "choose exactly 6" in problems(WREN, spells=WREN["spells"][:5])  # the spellbook stays exact
    assert "choose exactly 3" in problems(WREN, cantrips=["Fire Bolt"])  # so do cantrips


def test_personality_as_text_or_four_parts() -> None:
    """The Acolyte's four parts are kept apart and shown on their own lines; plain text still works."""
    from dm import play
    four = {"traits": ["I idolize a hero of my faith. "], "ideal": "Aspiration.", "bond": "", "flaw": "Too hard on myself."}
    s = built(BRAKKA | {"personality": four, "opening": ""})
    assert s["personality"] == {"traits": ["I idolize a hero of my faith."], "ideal": "Aspiration.",
                                "flaw": "Too hard on myself."}
    text = play.sheet_text(s)
    assert "\nTraits: I idolize a hero of my faith.\nIdeal: Aspiration.\nFlaw: Too hard on myself.\n" in text
    assert "{" not in text.split("AC ")[0] and "Personality" not in text
    assert "\nPersonality: Gruff.\n" in play.sheet_text(built(BRAKKA | {"personality": "Gruff."}))
    assert "personality: text, or" in problems(BRAKKA, personality={"mood": "grim"})
    assert "personality: text, or" in problems(BRAKKA, personality=["a"])
