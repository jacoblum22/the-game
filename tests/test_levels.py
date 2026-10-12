"""Levels above 1: hand-worked sheets, refusals, and every class at every level."""
import copy
import re
from functools import cache

import pytest

from dm import create, srd
from dm import mechanics as m
from tests.autochar import auto_levels, build_any
from tests.test_create import BRAKKA, HILDA, WREN, ranger

FIXED = {"hp": "fixed"}
BG = {"background.languages": ["Giant", "Goblin"], "background.equipment.1": ["Amulet"],
      "background.equipment.prayer": ["Prayer book"]}


def human(cls: str, scores: list[int], **choices: object) -> dict:
    """A human (+1 to every score) with the standard array in STR DEX CON INT WIS CHA order."""
    return {"name": cls.title(), "race": "human", "class": cls, "ability_method": "standard_array",
            "base_scores": dict(zip(create.ABILITIES, scores)), "choices": {"race.languages": ["Elvish"]} | BG | choices}


# STR 10 DEX 15 CON 13 INT 12 WIS 14 CHA 8, +1 each: STR 11 (+0), DEX 16 (+3), CON 14 (+2), INT 13 (+1), WIS 15 (+2), CHA 9 (-1)
VEX = human("rogue", [10, 15, 13, 12, 14, 8], **{
    "class.proficiencies.1": ["Acrobatics", "Perception", "Sleight of Hand", "Stealth"],
    "feature.rogue-expertise-1": [{"option": "a", "picks": ["Stealth", "Perception"]}],
    "class.equipment.1": ["a"], "class.equipment.2": ["b"], "class.equipment.3": ["a"]})
# STR 15 DEX 13 CON 14 INT 8 WIS 10 CHA 12, +1 each: STR 16 (+3), DEX 14 (+2), CON 15 (+2), INT 9, WIS 11 (+0), CHA 13
GROG = human("barbarian", [15, 13, 14, 8, 10, 12], **{
    "class.proficiencies.1": ["Athletics", "Perception"], "class.equipment.1": ["a"], "class.equipment.2": ["a"]})
# STR 12 DEX 15 CON 13 INT 8 WIS 14 CHA 10, +1 each: STR 13 (+1), DEX 16 (+3), CON 14 (+2), INT 9, WIS 15 (+2), CHA 11
LIN = human("monk", [12, 15, 13, 8, 14, 10], **{
    "class.proficiencies.1": ["Acrobatics", "Stealth"], "class.proficiencies.2": [{"option": "a", "picks": ["Smith's Tools"]}],
    "class.equipment.1": ["a"], "class.equipment.2": ["b"]})


def built(ch: dict, levels: list, **kw) -> dict:
    sheet, errs = create.build(ch, None, levels, **kw)
    assert sheet, errs
    return sheet


def problems(levels: list, ch: dict = BRAKKA, **kw) -> str:
    sheet, errs = create.build(ch, None, levels, **kw)
    assert sheet is None
    return "\n".join(errs)


def attack(sheet: dict, name: str) -> str:
    return next(a for a in sheet["attacks"] if a.startswith(name))


def has(sheet: dict, name: str) -> bool:
    return any(f.startswith(name + ":") for f in sheet["features"])


def test_fighter_levels_2_to_4() -> None:
    # Brakka: Hill dwarf, CON 14 + 2 = 16 (+3), STR 15 (+2), WIS 14 (+2). Level 1: 10 + 3 + 1 (Dwarven Toughness) = 14.
    s2 = built(BRAKKA, [FIXED])  # fixed = 10 / 2 + 1 = 6; + CON 3 + toughness 1 = 10 -> 24
    assert (s2["level"], s2["hp"]["max"], s2["hp"]["current"], s2["proficiency_bonus"]) == (2, 24, 24, 2)
    assert s2["hit_dice"] == {"die": "d10", "max": 2, "left": 2}
    assert s2["resources"]["Action Surge"] == {"max": 1, "left": 1, "recharge": "short"}  # "once ... short or long rest"
    assert s2["summary"].startswith("Hill Dwarf fighter 2,") and s2["subclass"] is None and (s2["ac"], s2["ac_note"]) \
        == (18, "Chain Mail 16 + shield 2; disadvantage on Stealth")

    s3 = built(BRAKKA, [FIXED, {"hp": {"rolled": 7}}])  # rolled 7 + 3 + 1 = 11 -> 35
    assert (s3["hp"]["max"], s3["hit_dice"]["max"], s3["subclass"]) == (35, 3, "Champion")
    assert "(Champion)" in s3["summary"] and has(s3, "Improved Critical") and has(s3, "Martial Archetype")
    assert attack(s3, "Longsword").startswith("Longsword: +4 to hit, 1d8+4")  # STR 2 + prof 2, Dueling +2

    s4 = built(BRAKKA, [FIXED, {"hp": {"rolled": 7}}, {"hp": "fixed", "asi": {"STR": 2}}])  # STR 17 (+3); 6 + 3 + 1 -> 45
    assert (s4["scores"]["STR"], s4["hp"]["max"], s4["proficiency_bonus"], s4["ac"]) == (17, 45, 2, 18)
    assert attack(s4, "Longsword").startswith("Longsword: +5 to hit, 1d8+5")  # STR 3 + prof 2; 1d8 + 3 + 2 Dueling
    assert "1d10+3 two-handed" in attack(s4, "Longsword") and attack(s4, "Unarmed").endswith("4 bludgeoning")
    assert "level 4: STR +2" in "".join(s4["features"]) and s4["abilities"]["STR"] == "17 (+3)"
    assert s4["build"] == {"choices": BRAKKA, "rolled": None, "levels": [FIXED, {"hp": {"rolled": 7}},
                                                                         {"hp": "fixed", "asi": {"STR": 2}}]}

    # level 5: proficiency bonus 3 (Levels data), Extra Attack; level 7: Champion's Remarkable Athlete
    s5 = built(BRAKKA, s4["build"]["levels"] + [FIXED])  # 45 + 10 = 55
    assert (s5["hp"]["max"], s5["proficiency_bonus"]) == (55, 3) and has(s5, "Extra Attack")
    assert attack(s5, "Longsword").startswith("Longsword: +6 to hit, 1d8+5")  # STR 3 + prof 3
    assert s5["saving_throws"].startswith("STR +6*, DEX +0, CON +6*, INT -1, WIS +2, CHA +1")
    s7 = built(BRAKKA, s5["build"]["levels"] + [{"hp": "fixed", "asi": {"STR": 2}}, FIXED])  # STR 19 (+4), prof 3
    # Remarkable Athlete: half of 3 rounded up = 2 added to STR, DEX, CON checks without proficiency; not to INT
    assert "Acrobatics +2," in s7["skills"] and "Stealth +2," in s7["skills"] and "Arcana -1," in s7["skills"]
    assert "Athletics +7*" in s7["skills"] and "Remarkable Athlete: +2" in s7["skills"] and s7["passive_perception"] == 15


def test_con_increase_counts_for_every_level() -> None:
    # SRD Constitution: "as though you had the new modifier from 1st level". CON 16 -> 18 at level 4: +3 -> +4 for 4 levels
    base = [FIXED, {"hp": {"rolled": 7}}, {"hp": "fixed", "asi": {"STR": 2}}]
    s = built(BRAKKA, base[:2] + [{"hp": "fixed", "asi": {"CON": 2}}])
    # level 1: 10 + 4 + 1 = 15; level 2: 6 + 4 + 1 = 11; level 3: 7 + 4 + 1 = 12; level 4: 6 + 4 + 1 = 11
    assert s["hp"]["max"] == 15 + 11 + 12 + 11 == 49 == built(BRAKKA, base)["hp"]["max"] + 4
    split = built(BRAKKA, base[:2] + [{"hp": "fixed", "asi": {"CON": 1, "STR": 1}}])  # CON 17 (+3): no change
    assert split["hp"]["max"] == 45 and split["scores"]["CON"] == 17


def test_each_level_adds_at_least_1_hp() -> None:
    # house rule (owner; the SRD sets no minimum). CON 8 + 1 = 9 (-1), d12: level 1 12 - 1 = 11; rolled 1: 1 - 1 = 0 -> 1;
    # rolled 5: 5 - 1 = 4
    weak = GROG | {"base_scores": dict(zip(create.ABILITIES, [15, 13, 8, 14, 10, 12]))}
    assert built(weak, [{"hp": {"rolled": 1}}, {"hp": {"rolled": 5}}])["hp"]["max"] == 11 + 1 + 4


def test_rogue_to_3_and_6() -> None:
    # Vex: DEX 16 (+3), CON 14 (+2), WIS 15 (+2), INT 13 (+1). Level 1: 8 + 2 = 10; each fixed level 5 + 2 = 7
    s1 = built(VEX, [])
    assert (s1["hp"]["max"], s1["ac"], attack(s1, "Rapier")) == (10, 14, "Rapier: +5 to hit, 1d8+3 piercing (finesse)")
    s3 = built(VEX, [FIXED, FIXED])
    assert (s3["hp"]["max"], s3["subclass"], s3["proficiency_bonus"]) == (24, "Thief", 2)
    assert re.search(r"Sneak Attack: .* At level 3: the extra damage is 2d6\.", "".join(s3["features"]))
    assert has(s3, "Cunning Action") and has(s3, "Fast Hands") and has(s3, "Second-Story Work") and has(s3, "Roguish Archetype")
    # expertise at level 1 doubles the proficiency bonus: Stealth DEX 3 + 2 x 2 = 7, Perception WIS 2 + 4 = 6
    assert "Stealth +7**" in s3["skills"] and "Perception +6**" in s3["skills"] and "Acrobatics +5*" in s3["skills"]
    assert s3["passive_perception"] == 16

    # level 4 DEX +2 -> 18 (+4); level 5 Uncanny Dodge, Sneak Attack 3d6, proficiency 3; level 6 Expertise again
    levels = [FIXED, FIXED, {"hp": "fixed", "asi": {"DEX": 2}}, FIXED,
              {"hp": "fixed", "choices": {"feature.rogue-expertise-2": ["Acrobatics", "Sleight of Hand"]}}]
    s6 = built(VEX, levels)
    assert (s6["hp"]["max"], s6["proficiency_bonus"], s6["ac"]) == (45, 3, 15)  # 10 + 5 x 7; leather 11 + DEX 4
    assert has(s6, "Uncanny Dodge") and "At level 6: the extra damage is 3d6" in "".join(s6["features"])
    # DEX 4 + 3 x 2 = 10; WIS 2 + 6 = 8
    assert all(f"{k} +10**" in s6["skills"] for k in ("Acrobatics", "Sleight of Hand", "Stealth"))
    assert "Perception +8**" in s6["skills"] and s6["passive_perception"] == 18
    assert "Expertise:" in "".join(s6["features"]) and sum(f.startswith("Expertise:") for f in s6["features"]) == 1
    again = problems(levels[:4] + [{"hp": "fixed", "choices": {"feature.rogue-expertise-2": ["Stealth", "Acrobatics"]}}], VEX)
    assert "level 6: choices.feature.rogue-expertise-2: Skill: Stealth already has expertise" in again
    assert "needs a proficiency" in problems(levels[:4] + [{"hp": "fixed", "choices": {
        "feature.rogue-expertise-2": ["Arcana", "Acrobatics"]}}], VEX)
    assert "level 6: choices.feature.rogue-expertise-2: missing" in problems(levels[:4] + [FIXED], VEX)


def test_barbarian_to_5() -> None:
    # Grog: after level 4's STR +1 CON +1: STR 17 (+3), DEX 14 (+2), CON 16 (+3). HP: 12 + 3, then 4 x (7 + 3)
    levels = [FIXED, FIXED, {"hp": "fixed", "asi": {"STR": 1, "CON": 1}}, FIXED]
    s = built(GROG, levels)
    assert (s["hp"]["max"], s["ac"], s["proficiency_bonus"], s["hit_dice"]["max"]) == (55, 15, 3, 5)  # AC 10 + 2 + 3
    assert s["resources"]["Rage"] == {"max": 3, "left": 3, "recharge": "long"}  # "3 at 3rd" (till 6th)
    assert s["subclass"] == "Berserker" and has(s, "Frenzy") and has(s, "Extra Attack") and has(s, "Reckless Attack")
    # Fast Movement: +10 ft while not in heavy armor
    assert s["speed"].startswith("40 ft") and "Fast Movement +10 ft" in s["speed"]
    # proficiency 3 on attacks (STR +3) and saves (STR, CON): +6
    assert attack(s, "Greataxe").startswith("Greataxe: +6 to hit, 1d12+3") and attack(s, "Handaxe").startswith("Handaxe: +6")
    assert s["saving_throws"].startswith("STR +6*, DEX +2, CON +6*, INT -1, WIS +0, CHA +1")
    assert "At level 5: rage damage bonus +2; 3 rages" in "".join(s["features"])
    s1 = built(GROG, [])
    assert s1["speed"] == "30 ft" and s1["resources"]["Rage"]["max"] == 2 and s1["hp"]["max"] == 14 == 12 + 2
    # Rage damage +3 from level 9, 4 rages from level 6 (the class table)
    s9 = built(GROG, auto_levels(GROG, 9))
    assert s9["resources"]["Rage"]["max"] == 4 and "rage damage bonus +3" in "".join(s9["features"])
    assert "Brutal Critical (1 die)" in "".join(s9["features"])


def test_barbarian_20_primal_champion() -> None:
    levels = auto_levels(GROG, 20)
    s19, s20 = built(GROG, levels[:-1]), built(GROG, levels)
    for a in ("STR", "CON"):  # "increase by 4. Your maximum for those scores is now 24."
        assert s20["scores"][a] == min(24, s19["scores"][a] + 4)
    assert s20["scores"]["STR"] > 20 or s20["scores"]["CON"] > 20
    assert "Rage" not in s20["resources"] and "unlimited rages" in "".join(s20["features"])  # the class table: unlimited
    assert has(s20, "Primal Champion") and "Brutal Critical (3 dice)" in "".join(s20["features"])


def test_monk_to_5() -> None:
    # Lin after level 4's DEX +1, WIS +1: DEX 17 (+3), WIS 16 (+3), CON 14 (+2). HP 8 + 2, then 4 x (5 + 2) = 38
    levels = [FIXED, FIXED, {"hp": "fixed", "asi": {"DEX": 1, "WIS": 1}}, FIXED]
    s = built(LIN, levels)
    assert (s["hp"]["max"], s["ac"], s["proficiency_bonus"]) == (38, 16, 3)  # AC 10 + 3 + 3, no armor
    assert s["resources"]["Ki"] == {"max": 5, "left": 5, "recharge": "short"}
    assert "At level 5: 5 ki points; ki save DC 14." in "".join(s["features"])  # 8 + 3 + 3
    assert "Martial Arts die d6" in "".join(s["features"])
    assert attack(s, "Unarmed strike") == "Unarmed strike: +6 to hit, 1d6+3 bludgeoning (Martial Arts; DEX or STR)"
    # Unarmored Movement: +10 ft at 2nd-5th level, only with no armor or shield
    assert s["speed"].startswith("40 ft") and "only while wearing no armor and wielding no shield" in s["speed"]
    assert "At level 5: speed +10 ft" in "".join(s["features"]) and has(s, "Extra Attack") and has(s, "Stunning Strike")
    assert s["subclass"] == "Open Hand" and has(s, "Open Hand Technique") and has(s, "Deflect Missiles")
    assert s["saving_throws"].startswith("STR +4*, DEX +6*") and attack(s, "Shortsword").startswith("Shortsword: +6 to hit, 1d6+3")
    # a monk weapon's die can be replaced by the Martial Arts die once that is bigger (d8 at level 11)
    s11 = built(LIN, auto_levels(LIN, 11))
    assert "Martial Arts: you can roll 1d8 in place of the weapon's damage" in attack(s11, "Shortsword")
    assert "Martial Arts" not in attack(s, "Shortsword")


def saves(sheet: dict) -> dict[str, bool]:
    return {x.split(" ")[0]: x.endswith("*") for x in sheet["saving_throws"].split(" (* proficient)")[0].split(", ")}


def skills(sheet: dict) -> dict[str, str]:
    return {x.rsplit(" ", 1)[0]: x.rsplit(" ", 1)[1] for x in sheet["skills"].split(" (* proficient")[0].split(", ")}


def test_saves_and_skills_features() -> None:
    # Diamond Soul (monk 14): "proficiency in all saving throws"; Slippery Mind (rogue 15): "proficiency in Wisdom saving throws"
    assert not all(saves(_sheet("monk", 13)).values()) and all(saves(_sheet("monk", 14)).values())
    assert not saves(_sheet("rogue", 14))["WIS"] and saves(_sheet("rogue", 15))["WIS"]
    assert sum(saves(_sheet("rogue", 15)).values()) == 3  # DEX, INT (class) and WIS
    # Jack of All Trades (bard 2): half the proficiency bonus (2 -> +1), rounded down, in skills without proficiency
    b1, b2 = _sheet("bard", 1), _sheet("bard", 2)
    for name, old in skills(b1).items():
        assert skills(b2)[name] == (old if old.endswith("*") else f"{int(old) + 1:+d}"), name
    assert "Jack of All Trades: +1" in b2["skills"] and "Jack of All Trades" not in b1["skills"]
    # a passive check is an ability check too (SRD Passive Checks: "10 + all modifiers that normally apply")
    assert b2["passive_perception"] == b1["passive_perception"] + (0 if skills(b1)["Perception"].endswith("*") else 1)
    b5 = _sheet("bard", 5)  # proficiency 3: half rounded down is still 1; at 7 it is 4 -> 2
    assert "Jack of All Trades: +1" in b5["skills"] and "Jack of All Trades: +2" in _sheet("bard", 9)["skills"]


@pytest.mark.parametrize(("cls", "level", "name", "expect"), [
    ("barbarian", 1, "Rage", (2, "long")), ("barbarian", 3, "Rage", (3, "long")), ("barbarian", 6, "Rage", (4, "long")),
    ("barbarian", 12, "Rage", (5, "long")), ("barbarian", 17, "Rage", (6, "long")), ("barbarian", 20, "Rage", None),
    ("fighter", 1, "Action Surge", None), ("fighter", 2, "Action Surge", (1, "short")),
    ("fighter", 17, "Action Surge", (2, "short")), ("fighter", 8, "Indomitable", None), ("fighter", 9, "Indomitable", (1, "long")),
    ("fighter", 13, "Indomitable", (2, "long")), ("fighter", 17, "Indomitable", (3, "long")),
    ("fighter", 20, "Second Wind", (1, "short")),
    ("monk", 2, "Ki", (2, "short")), ("monk", 10, "Ki", (10, "short")), ("monk", 20, "Ki", (20, "short")),
    ("monk", 5, "Wholeness of Body", None), ("monk", 6, "Wholeness of Body", (1, "long")),
    ("rogue", 19, "Stroke of Luck", None), ("rogue", 20, "Stroke of Luck", (1, "short")),
    ("paladin", 1, "Lay on Hands", (5, "long")), ("paladin", 7, "Lay on Hands", (35, "long")),
    ("paladin", 3, "Channel Divinity", (1, "short")), ("paladin", 13, "Cleansing Touch", None),
    ("paladin", 14, "Cleansing Touch", (1, "long")),
    ("cleric", 1, "Channel Divinity", None), ("cleric", 2, "Channel Divinity", (1, "short")),
    ("cleric", 6, "Channel Divinity", (2, "short")), ("cleric", 18, "Channel Divinity", (3, "short")),
    ("sorcerer", 1, "Sorcery Points", None), ("sorcerer", 2, "Sorcery Points", (2, "long")),
    ("sorcerer", 11, "Sorcery Points", (11, "long")), ("druid", 1, "Wild Shape", None), ("druid", 2, "Wild Shape", (2, "short")),
    ("druid", 20, "Wild Shape", None), ("druid", 2, "Natural Recovery", (1, "long")),
    ("warlock", 11, "Mystic Arcanum (6th level)", (1, "long")), ("warlock", 10, "Mystic Arcanum (6th level)", None),
    ("warlock", 17, "Mystic Arcanum (9th level)", (1, "long")), ("wizard", 9, "Arcane Recovery", (1, "long")),
])
def test_resources_by_level(cls: str, level: int, name: str, expect: tuple[int, str] | None) -> None:
    sheet = _sheet(cls, level)
    got = sheet["resources"].get(name)
    assert (None if got is None else (got["max"], got["recharge"])) == expect
    if got:
        assert got["left"] == got["max"]


def test_bardic_inspiration_and_lay_on_hands_follow_the_text() -> None:
    # Bardic Inspiration: CHA modifier (minimum once), long rest; Font of Inspiration (5th) adds the short rest
    for n, recharge in ((1, "long"), (4, "long"), (5, "short"), (20, "short")):
        s = _sheet("bard", n)
        assert s["resources"]["Bardic Inspiration"]["recharge"] == recharge
        assert s["resources"]["Bardic Inspiration"]["max"] == max(1, create.mod(s["scores"]["CHA"]))
    assert "Bardic Inspiration die d8" in "".join(_sheet("bard", 5)["features"])  # the class table
    assert "Bardic Inspiration (d12)" in "".join(_sheet("bard", 15)["features"])
    assert sum(f.startswith("Bardic Inspiration") for f in _sheet("bard", 15)["features"]) == 1  # not one per die
    assert "a pool of 35 hit points" in "".join(_sheet("paladin", 7)["features"])  # "your paladin level x 5"


@cache
def _auto(cls: str) -> tuple[dict, list]:
    ch = build_any("human", cls)[0]["build"]["choices"]
    return ch, auto_levels(ch, 20)


def _sheet(cls: str, level: int) -> dict:
    ch, levels = _auto(cls)
    return built(ch, levels[: level - 1])


def test_asi_levels_are_the_ones_the_class_text_names() -> None:
    for cls in srd.table("Classes"):
        text = " ".join(srd.table("Features")[f"{cls}-ability-score-improvement-1"]["desc"])
        named = {int(n) for n in re.findall(r"(\d+)(?:st|nd|rd|th)", text)}
        assert named == {n for n in range(1, 21) if create.has_asi(cls, n)}, cls


def test_refusals() -> None:
    assert "level 2: asi: this level does not grant Ability Score Improvement" in problems([{"hp": "fixed", "asi": {"STR": 2}}])
    assert "level 4: asi: missing" in problems([FIXED, FIXED, FIXED])
    assert "level 5: asi" not in problems([FIXED, FIXED, FIXED])
    assert "{\"rolled\": 1 to 10}" in problems([{"hp": {"rolled": 11}}]) and "11 is not on a d10" in problems([{"hp": {"rolled": 11}}])
    assert "level 2: hp" in problems([{"hp": {"rolled": 0}}]) and "level 2: hp" in problems([{}])
    assert "level 2: hp" in problems([{"hp": 6}]) and "level 2: hp" in problems([{"hp": {"rolled": "7"}}])
    asi = [FIXED, FIXED]  # a fighter: STR 15 -> 17 (level 4) -> 19 (level 6) -> 21 (level 8)
    up = [{"hp": "fixed", "asi": {"STR": 2}}, FIXED, {"hp": "fixed", "asi": {"STR": 2}}, FIXED]
    assert "level 8: asi: no score can go above 20 (STR would be 21)" in problems(asi + up + [{"hp": "fixed", "asi": {"STR": 2}}])
    assert built(BRAKKA, asi + up + [{"hp": "fixed", "asi": {"STR": 1, "DEX": 1}}])["scores"]["STR"] == 20
    for bad in ({"STR": 3}, {"STR": 1}, {"STR": 1, "DEX": 2}, {"STR": 1, "XXX": 1}, {}, {"STR": 0, "DEX": 2}, "STR", {"STR": True}):
        assert "level 4: asi: one ability +2" in problems([FIXED, FIXED, {"hp": "fixed", "asi": bad}]), bad
    assert "not a level-record field: bogus" in problems([{"hp": "fixed", "bogus": 1}])
    assert "level 2: spells: a fighter has no spells" in problems([{"hp": "fixed", "spells": ["Shield"]}])
    assert "choices: not needed for this character: feature.improved-critical" in problems(
        [FIXED, {"hp": "fixed", "choices": {"feature.improved-critical": ["x"]}}])
    # every problem at once, each with its level
    both = problems([{"hp": {"rolled": 12}}, {"hp": "fixed", "asi": {"STR": 2}}, FIXED])
    assert "level 2: hp" in both and "level 3: asi: this level does not" in both and "level 4: asi: missing" in both
    assert "levels: the highest level is 20" in problems([FIXED] * 20) and "levels: a list of level records" in problems("x")


def test_no_fighting_style_or_metamagic_twice() -> None:
    champion = auto_levels(BRAKKA, 9)  # Dueling at level 1
    style = "feature.additional-fighting-style"
    again = champion + [{"hp": "fixed", "choices": {style: ["Fighting Style: Dueling"]}}]
    assert "chosen twice: Fighting Style: Dueling" in problems(again)
    s = built(BRAKKA, champion + [{"hp": "fixed", "choices": {style: ["Fighting Style: Defense"]}}])
    assert s["ac"] == 19 and "+ Defense 1" in s["ac_note"]  # Chain Mail 16 + shield 2 + Defense 1
    assert "Fighting Style: Defense:" in "".join(s["features"]) and "Fighting Style: Dueling:" in "".join(s["features"])
    sorc, levels = _auto("sorcerer")
    first = levels[1]["choices"]["feature.metamagic-1"]  # level 3: two options; level 10 adds "another one"
    other = next(o for o in ("Metamagic: Quickened Spell", "Metamagic: Subtle Spell") if o not in first)
    until9 = levels[:8]
    level10 = levels[8]  # the sorcerer's own spells for the level, with other Metamagic picks
    assert "chosen twice" in problems(until9 + [level10 | {"choices": {"feature.metamagic-2": [first[0]]}}], sorc)
    s10 = built(sorc, until9 + [level10 | {"choices": {"feature.metamagic-2": [other]}}])
    assert sum(f.startswith("Metamagic:") and "CHOSEN" in f for f in s10["features"]) == 1  # one line, every stage's picks
    assert f"{first[0]}, {first[1]}. CHOSEN: {other}." in "".join(s10["features"])


def test_ranger_favored_enemy_and_terrain_at_6th_level() -> None:
    fe1, lang1 = "feature.favored-enemy-1-type", create.ENEMY_LANGUAGE_ID
    ch = ranger(**{fe1: ["Fiends"], lang1: ["Abyssal"]})
    until5 = auto_levels(ch, 5)
    fe2, terrain = "feature.favored-enemy-2-types", "feature.natural-explorer-2-terrain-types"
    six = {fe2: ["Humanoids"], fe2 + ".language": ["Orc"], fe2 + ".humanoid-races": ["gnolls", "orcs"], terrain: ["swamp"]}
    s = built(ch, until5 + [{"hp": "fixed", "choices": six}])
    text = "".join(s["features"])  # "You choose one additional favored enemy, as well as an associated language, at 6th"
    assert "CHOSEN: fiends. Language learned: Abyssal. CHOSEN: humanoids. Humanoid races: gnolls and orcs. "         "Language learned: Orc." in text
    assert "CHOSEN: swamp." in text and "Orc" in s["languages"].split(", ")
    assert sum(f.startswith("Favored Enemy") for f in s["features"]) == 1  # (2 types) replaces (1 type)
    assert "level 6: choices.feature.favored-enemy-2-types.humanoid-races: missing or wrong" in problems(
        until5 + [{"hp": "fixed", "choices": {k: v for k, v in six.items() if not k.endswith("races")}}], ch)
    assert "level 6: choices.feature.favored-enemy-2-types.language: missing" in problems(
        until5 + [{"hp": "fixed", "choices": {k: v for k, v in six.items() if not k.endswith("language")}}], ch)
    assert "not needed" in problems(until5 + [{"hp": "fixed", "choices": six | {fe2: ["Beasts"]}}], ch)


def test_carried_items_decide_armor_and_attacks() -> None:
    # Brakka now carries leather armor, a shield and a longsword (names in any case); a moon pie means nothing to the SRD
    carried = {"leather armor": 1, "Shield": 1, "LONGSWORD": 1, "Moon Pie": 2}
    s = built(BRAKKA, [FIXED], carried=carried)
    assert s["items"] == carried  # exactly what is carried
    assert (s["ac"], s["ac_note"]) == (13, "Leather Armor 11 + DEX 0 + shield 2")
    assert [a.split(":")[0] for a in s["attacks"]] == ["Longsword", "Unarmed strike"]  # no starting crossbow or javelins
    default = built(BRAKKA, [FIXED])
    assert default["ac"] == 18 and len(default["attacks"]) > 2 and "Moon Pie" not in default["items"]
    assert built(BRAKKA, [], carried={})["ac"] == 10 and built(BRAKKA, [], carried={})["items"] == {}
    assert "carried:" in problems([], carried={"Longsword": 0}) and "carried:" in problems([], carried=["Longsword"])  # type: ignore[arg-type]
    assert built(BRAKKA, [], carried={"Longsword": 1})["build"]["levels"] == []


def test_the_build_is_kept_whole() -> None:
    levels = [FIXED, {"hp": {"rolled": 7}}]
    sheet = built(BRAKKA, levels)
    sheet["build"]["levels"].append("changed")
    assert levels == [FIXED, {"hp": {"rolled": 7}}] and BRAKKA["choices"]["class.equipment.1"] == ["a"]
    assert built(BRAKKA, [])["build"] == {"choices": BRAKKA, "rolled": None, "levels": []}
    rolled = copy.deepcopy(BRAKKA) | {"ability_method": "rolled", "base_scores": dict(zip(create.ABILITIES, [9, 17, 12, 11, 7, 14]))}
    assert create.build(rolled, [17, 14, 12, 11, 9, 7], [FIXED])[0]["build"]["rolled"] == [17, 14, 12, 11, 9, 7]  # type: ignore[index]


@pytest.mark.parametrize("cls", ["barbarian", "fighter", "monk", "rogue"])
def test_every_noncaster_builds_at_every_level(cls: str) -> None:
    ch, levels = _auto(cls)
    c = srd.table("Classes")[cls]
    for n in range(2, 21):
        s = built(ch, levels[: n - 1])
        row = srd.table("Levels")[f"{cls}-{n}"]
        assert (s["level"], s["proficiency_bonus"], s["hit_dice"]["max"]) == (n, row["prof_bonus"], n)
        # hit points: the Hit Die at level 1, the fixed value after, CON (as it is at the end) for every level
        assert s["hp"]["max"] == c["hit_die"] + (n - 1) * (c["hit_die"] // 2 + 1) + n * create.mod(s["scores"]["CON"]), n
        top = 24 if cls == "barbarian" and n == 20 else 20  # Primal Champion
        assert all(v <= (top if a in ("STR", "CON") else 20) for a, v in s["scores"].items())
    assert s["build"]["levels"] == levels and s["level"] == 20


@pytest.mark.parametrize("cls", sorted(srd.table("Classes")))
def test_every_feature_of_the_level_is_on_the_sheet(cls: str) -> None:
    ch, levels = _auto(cls)
    for n in range(1, 21):
        s = built(ch, levels[: n - 1])
        for f in create.level_features(cls, n):
            if not f["index"].startswith("spellcasting-") and not create.NOT_SHOWN.search(f["index"]):
                assert any(x.startswith(f["name"] + ":") for x in s["features"]), (n, f["name"])


# ---------- spellcasting ----------

def rec(**kw: object) -> dict:
    """A level record with fixed hit points and the given fields."""
    return {"hp": "fixed"} | kw


def sc(sheet: dict) -> dict:
    return sheet["spellcasting"]


def slot_table(sheet: dict) -> dict[str, tuple[int, int, str]]:
    return {k: (v["max"], v["left"], v["recharge"]) for k, v in sheet["spell_slots"].items()}


def without(record: dict, *keys: str) -> dict:
    return {k: v for k, v in record.items() if k not in keys}


# Wren: elf wizard, INT 15 + 1 (High Elf) = 16 (+3), CON 13 (+1), d6. Level 1 HP 6 + 1 = 7; each fixed level 4 + 1 = 5.
WREN_LEVELS = [
    rec(spells=["Thunderwave", "Identify"]),                                          # 2: spellbook 6 + 2
    rec(spells=["Invisibility", "Misty Step"]),                                       # 3: 2nd-level slots: 2nd-level spells
    rec(asi={"INT": 2}, cantrips=["Ray of Frost"], spells=["Hold Person", "Web"]),    # 4: INT 18 (+4); the 4th cantrip
    rec(spells=["Fireball", "Fly"]),                                                  # 5: 3rd-level slots: 3rd-level spells
]


def test_wizard_to_3_and_5() -> None:
    s1 = built(WREN, [])
    assert sc(s1)["max_level"] == 1 and "Fire Bolt (cantrip): +5 spell attack, 1d10 fire" in "".join(s1["attacks"])
    s3 = built(WREN, WREN_LEVELS[:2])
    # Wizard table at 3: four 1st-level and two 2nd-level slots
    assert slot_table(s3) == {"1": (4, 4, "long"), "2": (2, 2, "long")} and sc(s3)["max_level"] == 2
    assert (s3["level"], s3["hp"]["max"], s3["proficiency_bonus"]) == (3, 17, 2)  # 7 + 2 x 5
    # spellbook 6 + 2 + 2 = 10; prepare INT 3 + wizard level 3 = 6; DC 8 + 2 + 3 = 13, attack 2 + 3 = +5
    assert len(sc(s3)["spellbook"]) == 10 and sc(s3)["spellbook"][-2:] == ["Invisibility", "Misty Step"]
    assert (sc(s3)["prepare_count"], sc(s3)["save_dc"], sc(s3)["attack_bonus"]) == (6, 13, 5)
    assert sc(s3)["prepared"] == WREN["prepared"]  # the list chosen at 1st level; changing it takes a long rest
    assert sc(s3)["cantrips"] == ["Fire Bolt", "Mage Hand", "Light"]
    assert "Fire Bolt (cantrip): +5 spell attack, 1d10 fire" in "".join(s3["attacks"])  # still 1d10 below level 5
    assert sc(s3)["racial_cantrips"] == ["Prestidigitation (High Elf, INT)"]

    s5 = built(WREN, WREN_LEVELS)
    # slots at 5: 4 / 3 / 2; INT 18 (+4), proficiency 3: DC 8 + 3 + 4 = 15, attack +7; prepare 4 + 5 = 9; spellbook 6 + 4 x 2 = 14
    assert slot_table(s5) == {"1": (4, 4, "long"), "2": (3, 3, "long"), "3": (2, 2, "long")} and sc(s5)["max_level"] == 3
    assert (sc(s5)["prepare_count"], sc(s5)["save_dc"], sc(s5)["attack_bonus"], len(sc(s5)["spellbook"])) == (9, 15, 7, 14)
    assert "Fire Bolt (cantrip): +7 spell attack, 2d10 fire" in "".join(s5["attacks"])  # 2d10 from 5th level
    assert sc(s5)["cantrips"] == ["Fire Bolt", "Mage Hand", "Light", "Ray of Frost"]
    assert "Ray of Frost (cantrip): +7 spell attack, 2d8 cold" in "".join(s5["attacks"])
    assert "Fireball" in sc(s5)["spellbook"] and s5["resources"]["Arcane Recovery"]["max"] == 1
    assert s5["build"]["levels"] == WREN_LEVELS


def test_a_wizard_prepares_and_copies_spells_up_to_the_highest_slot_level() -> None:
    s5 = built(WREN, WREN_LEVELS)
    nine = ["Fireball", "Fly", "Web", "Hold Person", "Shield", "Sleep", "Misty Step", "Magic Missile", "Mage Armor"]
    w, _ = m.change_pc(s5, {"long_rest": True, "prepare_spells": nine})
    assert w["spellcasting"]["prepared"] == nine
    with pytest.raises(m.Refused, match="prepare 1 to 9"):
        m.change_pc(w, {"long_rest": True, "prepare_spells": [*nine, "Thunderwave"]})
    with pytest.raises(m.Refused, match="level 4"):
        m.change_pc(w, {"spellbook_add": ["Dimension Door"]})  # no 4th-level slots yet
    w, _ = m.change_pc(w, {"spellbook_add": ["Haste"]})
    assert w["spellcasting"]["spellbook"][-1] == "Haste"
    with pytest.raises(m.Refused, match="level 1-2"):
        m.change_pc(built(WREN, WREN_LEVELS[:2]), {"spellbook_add": ["Haste"]})


def test_wizard_refusals() -> None:
    first = WREN_LEVELS[0]["spells"]
    assert "level 2: spells: choose exactly 2" in problems([rec(spells=["Thunderwave"])], WREN)
    assert "level 2: spells: choose exactly 2" in problems([rec(spells=[*first, "Sleep"])], WREN)
    assert "level 2: spells: choose exactly 2" in problems([rec()], WREN)
    # not above the highest spell level there are slots for (1st at wizard level 2, 2nd at level 3)
    assert "level 2: spells: Invisibility is not a wizard spell of level 1 to 1" in problems(
        [rec(spells=["Thunderwave", "Invisibility"])], WREN)
    assert "level 3: spells: Fireball is not a wizard spell of level 1 to 2" in problems(
        [WREN_LEVELS[0], rec(spells=["Fireball", "Misty Step"])], WREN)
    assert "level 2: spells: Cure Wounds is not a wizard spell" in problems([rec(spells=["Thunderwave", "Cure Wounds"])], WREN)
    assert "level 2: spells: Sleep is already in the spellbook" in problems([rec(spells=["Thunderwave", "Sleep"])], WREN)
    assert "level 2: spells: a spell is listed twice" in problems([rec(spells=["Thunderwave", "Thunderwave"])], WREN)
    assert "level 2: spells: no SRD spell 'Zork'" in problems([rec(spells=["Thunderwave", "Zork"])], WREN)
    assert "level 2: cantrips: no new cantrips at this level" in problems([rec(spells=first, cantrips=["Light"])], WREN)
    ray = rec(asi={"INT": 2}, spells=["Web", "Hold Person"])
    assert "level 4: cantrips: choose exactly 1" in problems([*WREN_LEVELS[:2], ray], WREN)
    assert "level 4: cantrips: Fire Bolt is already known" in problems([*WREN_LEVELS[:2], ray | {"cantrips": ["Fire Bolt"]}], WREN)
    assert "level 4: cantrips: Cure Wounds is not a wizard cantrip" in problems([*WREN_LEVELS[:2], ray | {"cantrips": ["Cure Wounds"]}], WREN)
    assert "level 2: replace: a wizard doesn't replace known spells" in problems(
        [rec(spells=first, replace={"from": "Sleep", "to": "Shield"})], WREN)
    assert "level 2: secrets: only bards get Magical Secrets" in problems([rec(spells=first, secrets=["Shield", "Sleep"])], WREN)
    assert "level 2: arcanum: Mystic Arcanum comes to a warlock" in problems([rec(spells=first, arcanum="Fly")], WREN)
    assert "level 2: tome: only when Pact of the Tome" in problems([rec(spells=first, tome=["Light"] * 3)], WREN)
    both = problems([rec(spells=["Thunderwave"]), rec(spells=["Fireball", "Fly"])], WREN)  # every problem at once
    assert "level 2: spells: choose exactly 2" in both and "level 3: spells: Fireball is not" in both
    # the prepared list chosen at 1st level is checked against the 1st-level spellbook
    assert "prepared: Fireball is not a level-1 wizard spell in the spellbook" in problems(WREN_LEVELS[:2], WREN | {"prepared": ["Fireball"]})


def test_wizard_spell_mastery_and_signature_spells() -> None:
    ch, levels = _auto("wizard")
    s17 = built(ch, levels[:16])
    assert len(sc(s17)["spellbook"]) == 6 + 2 * 16  # two spells at each of 16 levels
    # 18th level, Spell Mastery: "Choose a 1st-level wizard spell and a 2nd-level wizard spell that are in your spellbook"
    l18, first_two = levels[16], levels[16]["mastery"]
    s18 = built(ch, levels[:17])
    assert sc(s18)["spell_mastery"] == first_two and [srd.spell(x)["level"] for x in first_two] == [1, 2]
    low, high = first_two
    assert "level 18: mastery: Spell Mastery needs a 1st-level wizard spell and a 2nd-level wizard spell" in problems(
        [*levels[:16], l18 | {"mastery": [low, low]}], ch)
    assert "level 18: mastery: Spell Mastery needs" in problems([*levels[:16], l18 | {"mastery": ["Fireball", high]}], ch)
    assert "level 18: mastery: a 1st-level wizard spell and a 2nd-level" in problems([*levels[:16], l18 | {"mastery": [low]}], ch)
    assert "level 18: mastery: a 1st-level wizard spell and a 2nd-level" in problems([*levels[:16], without(l18, "mastery")], ch)
    book = sc(s18)["spellbook"]
    missing = next(s["name"] for s in srd.table("Spells").values() if s["level"] == 2 and s["name"] not in book
                   and any(c["index"] == "wizard" for c in s["classes"]))
    assert f"level 18: mastery: {missing} must be in your spellbook" in problems([*levels[:16], l18 | {"mastery": [low, missing]}], ch)
    assert "level 17: mastery: only a wizard at 18th level" in problems([*levels[:15], levels[15] | {"mastery": first_two}], ch)
    # 20th level, Signature Spell: "Choose two 3rd-level wizard spells in your spellbook as your signature spells. You always
    # have these spells prepared, they don't count against the number of spells you have prepared"
    s20 = built(ch, levels)
    sig = sc(s20)["signature_spells"]
    assert len(sig) == 2 and set(sig) <= set(sc(s20)["always_prepared"]) and all(srd.spell(x)["level"] == 3 for x in sig)
    assert {k: v for k, v in s20["resources"].items() if k.startswith("Signature")} == {
        f"Signature Spell: {x}": {"max": 1, "left": 1, "recharge": "short"} for x in sig}
    assert "level 20: signature: Signature Spell needs two 3rd-level wizard spells" in problems(
        [*levels[:18], levels[18] | {"signature": [sig[0], "Shield"]}], ch)
    assert "level 20: signature: two 3rd-level wizard spells that are in your spellbook" in problems(
        [*levels[:18], without(levels[18], "signature")], ch)
    assert "level 19: signature: only a wizard at 20th level" in problems([*levels[:17], levels[17] | {"signature": sig}], ch)
    w, _ = m.change_pc(s20, {"long_rest": True, "prepare_spells": [*sig, book[0]]})
    assert w["spellcasting"]["prepared"] == [book[0]]  # the signature spells are not counted or listed as prepared


def test_cleric_with_the_life_domain_to_3_and_5() -> None:
    # Hilda: WIS 15 + 1 = 16 (+3), CON 14 + 2 = 16 (+3), dwarf, d8: level 1 HP 8 + 3 + 1 = 12; each fixed level 5 + 3 + 1 = 9
    s3 = built(HILDA, [FIXED, FIXED])
    assert s3["hp"]["max"] == 30 and s3["resources"]["Channel Divinity"] == {"max": 1, "left": 1, "recharge": "short"}
    # the SRD's example: a 3rd-level cleric has four 1st-level and two 2nd-level slots; "With a Wisdom of 16 ... six spells"
    assert slot_table(s3) == {"1": (4, 4, "long"), "2": (2, 2, "long")}
    assert (sc(s3)["prepare_count"], sc(s3)["max_level"], sc(s3)["save_dc"]) == (6, 2, 13)  # DC 8 + 2 + 3
    # domain spells are always prepared and don't count: Bless, Cure Wounds (1st level); Lesser Restoration, Spiritual Weapon (3rd)
    assert sc(s3)["always_prepared"] == ["Bless", "Cure Wounds", "Lesser Restoration", "Spiritual Weapon"]
    assert sc(s3)["prepared"] == HILDA["prepared"] and "domain spells are always prepared" in sc(s3)["notes"]
    assert sc(built(HILDA, [FIXED]))["always_prepared"] == ["Bless", "Cure Wounds"]
    s5 = built(HILDA, [FIXED, FIXED, rec(asi={"WIS": 2}, cantrips=["Light"]), FIXED])  # level 4: WIS 18 (+4), a 4th cantrip
    assert sc(s5)["always_prepared"][4:] == ["Beacon of Hope", "Revivify"] and sc(s5)["prepare_count"] == 4 + 5
    assert slot_table(s5) == {"1": (4, 4, "long"), "2": (3, 3, "long"), "3": (2, 2, "long")} and len(sc(s5)["cantrips"]) == 4
    w, _ = m.change_pc(s3, {"long_rest": True, "prepare_spells": ["Aid", "Hold Person", "Guiding Bolt", "Healing Word",
                                                                    "Shield of Faith", "Sanctuary"]})
    assert len(w["spellcasting"]["prepared"]) == 6
    with pytest.raises(m.Refused, match="level 1-2"):
        m.change_pc(s3, {"long_rest": True, "prepare_spells": ["Spirit Guardians"]})  # 3rd-level spell at cleric level 3
    assert "level 3: spells: a cleric prepares spells from the whole class list" in problems([FIXED, rec(spells=["Bless"])], HILDA)
    assert "level 3: replace: a cleric doesn't replace" in problems([FIXED, rec(replace={"from": "Bless", "to": "Aid"})], HILDA)
    assert "level 4: cantrips: choose exactly 1" in problems([FIXED, FIXED, rec(asi={"WIS": 2})], HILDA)


SORC = human("sorcerer", [8, 14, 13, 10, 12, 15], **{
    "class.proficiencies.1": ["Arcana", "Deception"], "feature.dragon-ancestor": ["a"], "class.equipment.1": ["a"],
    "class.equipment.2": ["a"], "class.equipment.3": ["a"]}) | {
    "cantrips": ["Fire Bolt", "Light", "Mage Hand", "Prestidigitation"], "spells": ["Burning Hands", "Sleep"]}
META = {"feature.metamagic-1": ["Metamagic: Quickened Spell", "Metamagic: Subtle Spell"]}


def test_sorcerer_to_3_with_a_replacement() -> None:
    # CHA 15 + 1 = 16 (+3), CON 13 + 1 = 14 (+2), d6, Draconic Resilience +1 per level: level 1 HP 6 + 2 + 1 = 9; each fixed level 4 + 2 + 1 = 7
    s1 = built(SORC, [])
    assert (s1["hp"]["max"], slot_table(s1), sc(s1)["known"]) == (9, {"1": (2, 2, "long")}, ["Burning Hands", "Sleep"])
    levels = [rec(spells=["Shield"]),                                                                  # 2: known 3
              rec(spells=["Misty Step"], replace={"from": "Sleep", "to": "Magic Missile"}, choices=META)]  # 3: known 4
    s2, s3 = built(SORC, levels[:1]), built(SORC, levels)
    assert sc(s2)["known"] == ["Burning Hands", "Sleep", "Shield"] and slot_table(s2) == {"1": (3, 3, "long")}
    # Sorcerer table at 3: 4 cantrips, 4 spells known, slots 4 / 2
    assert sc(s3)["known"] == ["Burning Hands", "Magic Missile", "Shield", "Misty Step"]  # Sleep swapped out in place
    assert slot_table(s3) == {"1": (4, 4, "long"), "2": (2, 2, "long")} and len(sc(s3)["cantrips"]) == 4
    assert s3["hp"]["max"] == 23 and (sc(s3)["save_dc"], sc(s3)["attack_bonus"]) == (13, 5)  # 9 + 2 x 7; 8 + 2 + 3; 2 + 3
    assert "prepare_count" not in sc(s3) and s3["resources"]["Sorcery Points"]["max"] == 3
    # a replacement at 2nd level of a spell known since 1st, with the new spell alongside
    swap = built(SORC, [rec(spells=["Shield"], replace={"from": "Burning Hands", "to": "Thunderwave"})])
    assert sc(swap)["known"] == ["Thunderwave", "Sleep", "Shield"]
    third = rec(spells=["Misty Step"], choices=META)
    for bad, why in (({"from": "Fireball", "to": "Shield"}, "Fireball is not one of the spells you know"),
                     ({"from": "Sleep", "to": "Burning Hands"}, "Burning Hands is already known"),
                     ({"from": "Sleep", "to": "Cure Wounds"}, "Cure Wounds is not a sorcerer spell of level 1 to 2"),
                     ({"from": "Sleep", "to": "Fireball"}, "Fireball is not a sorcerer spell of level 1 to 2"),
                     ({"from": "Sleep", "to": "Fire Bolt"}, "Fire Bolt is not a sorcerer spell of level 1 to 2"),
                     ({"from": "Sleep"}, 'replace: {"from"'), ("Sleep", 'replace: {"from"'),
                     ({"from": "Zork", "to": "Shield"}, "no SRD spell 'Zork'")):
        assert why in problems([levels[0], third | {"replace": bad}], SORC), bad
    assert "level 2: spells: choose exactly 1" in problems([rec()], SORC)
    assert "level 2: spells: choose exactly 1" in problems([rec(spells=["Shield", "Mage Armor"])], SORC)
    assert "level 2: spells: Misty Step is not a sorcerer spell of level 1 to 1" in problems([rec(spells=["Misty Step"])], SORC)
    assert "level 2: cantrips: no new cantrips" in problems([rec(spells=["Shield"], cantrips=["Light"])], SORC)
    assert "level 4: cantrips: choose exactly 1" in problems([*levels, rec(asi={"CHA": 2}, spells=["Fly"])], SORC)  # fifth cantrip
    assert "level 4: spells: Fly is not a sorcerer spell of level 1 to 2" in problems(
        [*levels, rec(asi={"CHA": 2}, spells=["Fly"], cantrips=["Ray of Frost"])], SORC)


LOCK = human("warlock", [8, 14, 13, 10, 12, 15], **{
    "class.proficiencies.1": ["Arcana", "Deception"], "class.equipment.1": ["a"], "class.equipment.2": ["a"],
    "class.equipment.3": ["a"], "class.equipment.4": ["Dagger"]}) | {
    "cantrips": ["Eldritch Blast", "Minor Illusion"], "spells": ["Charm Person", "Hellish Rebuke"]}
TOME = {"feature.pact-boon": ["Pact of the Tome"]}
INV2 = ["Armor of Shadows", "Beast Speech"]  # no prerequisites, no effect on the Eldritch Blast line
LOCK_LEVELS = [
    rec(spells=["Comprehend Languages"], invocations=INV2),                            # 2: known 3; two 1st-level slots; 2 invocations
    rec(spells=["Misty Step"], choices=TOME, tome=["Guidance", "Sacred Flame", "Light"]),  # 3: known 4; two 2nd-level slots
    rec(asi={"CHA": 2}, cantrips=["Chill Touch"], spells=["Scorching Ray"]),           # 4: CHA 18 (+4); 3 cantrips; known 5
    rec(spells=["Fireball"], invocations=["Book of Ancient Secrets"], rituals=["Find Familiar", "Identify"]),  # 5: known 6; 3 invocations
]


def test_warlock_pact_magic_to_5() -> None:
    # Warlock table: 1st level one 1st-level slot; 2nd two 1st-level; 3rd two 2nd-level; 5th two 3rd-level slots
    assert slot_table(built(LOCK, [])) == {"1": (1, 1, "short")}
    assert slot_table(built(LOCK, LOCK_LEVELS[:1])) == {"1": (2, 2, "short")}
    s3 = built(LOCK, LOCK_LEVELS[:2])
    assert slot_table(s3) == {"2": (2, 2, "short")} and sc(s3)["max_level"] == 2 and len(sc(s3)["known"]) == 4
    assert sc(s3)["tome_cantrips"] == ["Guidance", "Sacred Flame", "Light"] and len(sc(s3)["cantrips"]) == 2
    s5 = built(LOCK, LOCK_LEVELS)
    # CHA 15 + 1 + 2 = 18 (+4), proficiency 3: DC 8 + 3 + 4 = 15, attack +7
    assert slot_table(s5) == {"3": (2, 2, "short")} and sc(s5)["max_level"] == 3
    assert (sc(s5)["save_dc"], sc(s5)["attack_bonus"]) == (15, 7)
    assert sc(s5)["known"] == ["Charm Person", "Hellish Rebuke", "Comprehend Languages", "Misty Step", "Scorching Ray", "Fireball"]
    assert sc(s5)["cantrips"] == ["Eldritch Blast", "Minor Illusion", "Chill Touch"]  # Fireball and Scorching Ray: Fiend's list
    text = "".join(s5["attacks"])
    assert "Eldritch Blast (cantrip): +7 spell attack, 1d10 force per beam, 2 beams" in text  # "two beams at 5th level"
    assert "Sacred Flame (cantrip): DEX save DC 15, 2d8 radiant" in text and "Chill Touch (cantrip): +7 spell attack, 2d8 necrotic" in text
    assert "Eldritch Blast (cantrip): +6 spell attack, 1d10 force, range" in "".join(built(LOCK, LOCK_LEVELS[:3])["attacks"])  # 1 beam
    assert "prepare_count" not in sc(s5) and "short or long rest" in sc(s5)["notes"]
    # pact slots come back on a short rest
    w, _ = m.change_pc(s5, {"spend_slot": 3})
    assert w["spell_slots"]["3"]["left"] == 1
    w, _ = m.change_pc(w, {"short_rest": True})
    assert w["spell_slots"]["3"]["left"] == 2
    # a spell must be of a level no higher than the slot level ("Slot Level column"); the Fiend's list adds to the choices
    four = rec(asi={"CHA": 2}, cantrips=["Chill Touch"])
    assert "level 4: spells: Fireball is not a warlock spell of level 1 to 2" in problems(
        [*LOCK_LEVELS[:2], four | {"spells": ["Fireball"]}], LOCK)
    assert "level 5: spells: Magic Missile is not a warlock spell of level 1 to 3" in problems(
        [*LOCK_LEVELS[:3], rec(spells=["Magic Missile"])], LOCK)
    assert "level 2: spells: Misty Step is not a warlock spell of level 1 to 1" in problems([rec(spells=["Misty Step"])], LOCK)
    assert "Burning Hands" in sc(built(LOCK, [rec(spells=["Burning Hands"], invocations=INV2)]))["known"]  # the Fiend's list, 1st level
    # Pact of the Tome: "choose three cantrips from any class's spell list", only when it is the pact chosen
    third = LOCK_LEVELS[1]
    assert "level 3: tome: choose exactly 3" in problems([LOCK_LEVELS[0], third | {"tome": ["Guidance"]}], LOCK)
    assert "level 3: tome: Fireball is not a cantrip" in problems([LOCK_LEVELS[0], third | {"tome": ["Guidance", "Light", "Fireball"]}], LOCK)
    assert "level 3: tome: choose exactly 3" in problems([LOCK_LEVELS[0], without(third, "tome")], LOCK)
    assert "level 3: tome: only when Pact of the Tome" in problems(
        [LOCK_LEVELS[0], third | {"choices": {"feature.pact-boon": ["Pact of the Chain"]}}], LOCK)
    assert has(built(LOCK, [LOCK_LEVELS[0], without(third, "tome") | {"choices": {"feature.pact-boon": ["Pact of the Chain"]}}]),
               "Pact of the Chain")


def test_warlock_mystic_arcanum_at_11_13_15_17() -> None:
    ch, levels = _auto("warlock")
    s11, s17 = built(ch, levels[:10]), built(ch, levels[:16])
    assert list(sc(s11)["arcanum"]) == ["6"] and list(sc(s17)["arcanum"]) == ["6", "7", "8", "9"]
    assert [srd.spell(v)["level"] for v in sc(s17)["arcanum"].values()] == [6, 7, 8, 9]
    # Warlock table at 11: three 5th-level slots, 11 spells known (the arcanum spells are not among them)
    assert slot_table(s11) == {"5": (3, 3, "short")} and len(sc(s11)["known"]) == 11
    assert s11["resources"]["Mystic Arcanum (6th level)"] == {"max": 1, "left": 1, "recharge": "long"}
    r11 = levels[9]
    assert "level 11: arcanum: the name of one 6th-level warlock spell" in problems([*levels[:9], without(r11, "arcanum")], ch)
    assert "level 11: arcanum: Fireball is not a 6th-level warlock spell" in problems([*levels[:9], r11 | {"arcanum": "Fireball"}], ch)
    assert "level 11: arcanum: Etherealness is not a 6th-level warlock spell" in problems(
        [*levels[:9], r11 | {"arcanum": "Etherealness"}], ch)
    assert "level 12: arcanum: Mystic Arcanum comes to a warlock at 11th, 13th, 15th and 17th level" in problems(
        [*levels[:10], levels[10] | {"arcanum": "Circle of Death"}], ch)


PAL = human("paladin", [15, 10, 13, 8, 12, 14], **{
    "class.proficiencies.1": ["Athletics", "Intimidation"], "class.equipment.1": [{"option": "a", "picks": ["Longsword"]}],
    "class.equipment.2": ["a"], "class.equipment.3": ["a"], "class.equipment.4": ["Amulet"]})
STYLE = {"feature.paladin-fighting-style": ["Defense"]}


def test_paladin_casts_from_level_2() -> None:
    # STR 16, CON 14, CHA 14 + 1 = 15 (+2). No spells at 1st level.
    assert "spellcasting" not in built(PAL, []) and "spell_slots" not in built(PAL, [])
    first = ["Bless", "Cure Wounds", "Shield of Faith"]
    levels = [rec(choices=STYLE, prepared=first), FIXED, rec(asi={"STR": 2}), FIXED]
    s2 = built(PAL, levels[:1])
    assert slot_table(s2) == {"1": (2, 2, "long")} and sc(s2)["max_level"] == 1 and sc(s2)["cantrips"] == []
    # prepare: CHA +2 + half of level 2 = 1 -> 3; DC 8 + 2 + 2 = 12; attack +4; the first list is chosen at the level-up (owner)
    assert (sc(s2)["prepare_count"], sc(s2)["save_dc"], sc(s2)["attack_bonus"], sc(s2)["prepared"]) == (3, 12, 4, first)
    assert sc(built(PAL, [rec(choices=STYLE, prepared=["Bless"])]))["prepared"] == ["Bless"]  # 1 to 3
    for bad, why in (([], "prepared: choose 1 to 3"), ([*first, "Heroism"], "prepared: choose 1 to 3"),
                     (["Aid"], "prepared: Aid is not a paladin spell of level 1 to 1"),
                     (["Fire Bolt"], "prepared: Fire Bolt is not a paladin spell")):
        assert f"level 2: {why}" in problems([rec(choices=STYLE, prepared=bad)], PAL), bad
    assert sc(built(PAL, levels[:2]))["prepared"] == first  # kept at 3rd level
    assert "level 3: prepared: the prepared list changes when a long rest finishes" in problems(
        [levels[0], rec(prepared=["Bless"])], PAL)
    w, _ = m.change_pc(s2, {"long_rest": True, "prepare_spells": ["Bless", "Cure Wounds", "Shield of Faith"]})
    assert w["spellcasting"]["prepared"] == ["Bless", "Cure Wounds", "Shield of Faith"]
    with pytest.raises(m.Refused, match="prepare 1 to 3"):
        m.change_pc(s2, {"long_rest": True, "prepare_spells": ["Bless", "Cure Wounds", "Shield of Faith", "Heroism"]})
    with pytest.raises(m.Refused, match="level 1-1"):
        m.change_pc(s2, {"long_rest": True, "prepare_spells": ["Aid"]})
    # Oath of Devotion at 3: Protection from Evil and Good, Sanctuary, always prepared; still 3 to prepare (half of 3 = 1)
    s3 = built(PAL, levels[:2])
    assert sc(s3)["always_prepared"] == ["Protection from Evil and Good", "Sanctuary"] and sc(s3)["prepare_count"] == 3
    s5 = built(PAL, levels)
    assert s5["level"] == 5
    # the SRD's example: a 5th-level paladin has four 1st-level and two 2nd-level slots; "With a Charisma of 14 ... four spells"
    assert slot_table(s5) == {"1": (4, 4, "long"), "2": (2, 2, "long")} and sc(s5)["prepare_count"] == 2 + 2
    assert sc(s5)["always_prepared"][2:] == ["Lesser Restoration", "Zone of Truth"] and sc(s5)["max_level"] == 2
    assert "oath spells are always prepared" in sc(s5)["notes"]
    assert "level 2: spells: a paladin prepares spells from the whole class list" in problems([rec(choices=STYLE, spells=["Bless"])], PAL)
    assert "level 2: cantrips: no new cantrips" in problems([rec(choices=STYLE, cantrips=["Light"])], PAL)
    assert "level 2: replace: a paladin doesn't replace" in problems([rec(choices=STYLE, replace={"from": "Bless", "to": "Aid"})], PAL)


def test_ranger_casts_from_level_2() -> None:
    base = ranger()
    assert "spellcasting" not in built(base, [])
    auto = auto_levels(base, 5)
    first = without(auto[0], "spells", "replace") | {"spells": ["Hunter's Mark", "Cure Wounds"]}
    r2 = built(base, [first])
    # Ranger table at 2: two spells known, two 1st-level slots; no cantrips
    assert sc(r2)["known"] == ["Hunter's Mark", "Cure Wounds"] and slot_table(r2) == {"1": (2, 2, "long")}
    assert sc(r2)["cantrips"] == [] and "prepare_count" not in sc(r2) and sc(r2)["max_level"] == 1
    assert (sc(r2)["save_dc"], sc(r2)["attack_bonus"]) == (10, 2)  # WIS 10 + 1 = 11 (+0): DC 8 + 2 + 0, attack 2 + 0
    assert "level 2: spells: choose exactly 2" in problems([without(first, "spells") | {"spells": ["Hunter's Mark"]}], base)
    assert "level 2: spells: Bless is not a ranger spell" in problems([first | {"spells": ["Hunter's Mark", "Bless"]}], base)
    assert "level 2: spells: Pass Without Trace is not a ranger spell of level 1 to 1" in problems(
        [first | {"spells": ["Hunter's Mark", "Pass Without Trace"]}], base)
    assert "level 2: replace: Hunter's Mark is not one of the spells you know (none yet)" in problems(
        [first | {"replace": {"from": "Hunter's Mark", "to": "Jump"}}], base)
    assert "level 2: cantrips: no new cantrips" in problems([first | {"cantrips": ["Light"]}], base)
    # 3rd level: one more known, three 1st-level slots; 5th level: four 1st-level and two 2nd-level slots, 4 known
    r3 = built(base, [first, auto[1] | {"spells": ["Longstrider"]}])
    assert sc(r3)["known"][-1] == "Longstrider" and len(sc(r3)["known"]) == 3 and slot_table(r3) == {"1": (3, 3, "long")}
    r5 = built(base, [first, auto[1] | {"spells": ["Longstrider"]}, without(auto[2], "replace", "spells"),
                      without(auto[3], "replace") | {"spells": ["Pass Without Trace"]}])  # records for levels 2 to 5
    assert len(sc(r5)["known"]) == 4 and slot_table(r5) == {"1": (4, 4, "long"), "2": (2, 2, "long")}
    # a ranger replaces too: Hunter's Mark for Jump when gaining a level
    swapped = built(base, [first, auto[1] | {"spells": ["Longstrider"], "replace": {"from": "Hunter's Mark", "to": "Jump"}}])
    assert sc(swapped)["known"] == ["Jump", "Cure Wounds", "Longstrider"]


def test_bard_magical_secrets() -> None:
    ch, levels = _auto("bard")
    s5, s6, s9, s10, s18 = (built(ch, levels[: n - 1]) for n in (5, 6, 9, 10, 18))
    assert len(sc(s5)["known"]) == 8                                    # Bard table at 5
    # Lore bard 6th level, Additional Magical Secrets: two spells that "don't count against the number of bard spells you know"
    assert len(sc(s6)["known"]) == 9 + 2 and len(sc(s6)["magical_secrets"]) == 2
    assert len(sc(s9)["known"]) == 12 + 2 and len(sc(s9)["magical_secrets"]) == 2
    # 10th level, Magical Secrets: the table goes 12 -> 14 and the two chosen "are included in the number in the Spells Known column"
    assert len(sc(s10)["known"]) == 14 + 2 and len(sc(s10)["magical_secrets"]) == 4
    assert slot_table(s10) == {"1": (4, 4, "long"), "2": (3, 3, "long"), "3": (3, 3, "long"), "4": (3, 3, "long"),
                               "5": (2, 2, "long")} and sc(s10)["max_level"] == 5 and len(sc(s10)["cantrips"]) == 4
    assert len(sc(s18)["known"]) == 22 + 2 and len(sc(built(ch, levels[:17]))["magical_secrets"]) == 8  # 2 + 2 + 2 + 2 by 18th
    r10, before = levels[8], levels[:8]
    s = built(ch, [*before, r10 | {"secrets": ["Fireball", "Cone of Cold"]}])  # a 3rd-level and a 5th-level spell of other classes
    assert sc(s)["magical_secrets"][-2:] == ["Fireball", "Cone of Cold"] and {"Fireball", "Cone of Cold"} <= set(sc(s)["known"])
    assert "level 10: secrets: Chain Lightning is not a spell of level 5 or lower" in problems(
        [*before, r10 | {"secrets": ["Fireball", "Chain Lightning"]}], ch)
    assert "level 10: secrets: choose exactly 2" in problems([*before, r10 | {"secrets": ["Fireball"]}], ch)
    assert "level 10: secrets: choose exactly 2" in problems([*before, without(r10, "secrets")], ch)
    taken = sc(s9)["known"][4]
    assert f"level 10: secrets: {taken} is already known" in problems([*before, r10 | {"secrets": ["Fireball", taken]}], ch)
    assert "level 10: spells: no new spells known at this level (the new Spells Known are the Magical Secrets" in problems(
        [*before, r10 | {"spells": ["Bane"]}], ch)
    # "or a cantrip": it counts as a bard spell known, not as a bard cantrip
    c = built(ch, [*before, r10 | {"secrets": ["Fireball", "Fire Bolt"]}])
    assert "Fire Bolt" in sc(c)["known"] and "Fire Bolt" not in sc(c)["cantrips"] and "Fire Bolt (cantrip)" in "".join(c["attacks"])
    for n in (2, 4, 5, 9, 11, 17):  # only where the class table names them: Lore 6th, every bard 10th, 14th and 18th
        wrong = [*levels[: n - 2], levels[n - 2] | {"secrets": ["Fireball", "Cone of Cold"]}]
        assert f"level {n}: secrets: only bards get Magical Secrets" in problems(wrong, ch)
    assert "level 6: secrets: choose exactly 2" in problems([*levels[:4], without(levels[4], "secrets")], ch)
    assert "level 6: secrets: Cone of Cold is not a spell of level 3 or lower" in problems(
        [*levels[:4], levels[4] | {"secrets": ["Fireball", "Cone of Cold"]}], ch)
    # replacing a bard spell: "choose one of the bard spells you know and replace it with another spell from the bard spell list"
    known3 = sc(built(ch, levels[:2]))["known"]
    assert "level 3: replace: Fireball is not a bard spell of level 1 to 2" in problems(
        [levels[0], without(levels[1], "replace") | {"replace": {"from": known3[0], "to": "Fireball"}}], ch)


def test_druid_land_circle_spells_and_bonus_cantrip() -> None:
    ch, levels = _auto("druid")
    s1, s2, s3 = built(ch, []), built(ch, levels[:1]), built(ch, levels[:2])
    assert len(sc(s1)["cantrips"]) == 2 and len(sc(s2)["cantrips"]) == 3  # Bonus Cantrip: "one additional druid cantrip"
    assert "Circle of the Land" in "".join(s2["features"]) and "always_prepared" not in sc(s2)
    assert "level 2: cantrips: choose exactly 1" in problems([without(levels[0], "cantrips")], ch)
    # Circle Spells by the land: arctic Hold Person + Spike Growth at 3rd level, forest Barkskin + Spider Climb
    arctic = levels[0] | {"choices": {"feature.circle-of-the-land": ["Circle of the Land: Arctic"]}}
    forest = levels[0] | {"choices": {"feature.circle-of-the-land": ["Circle of the Land: Forest"]}}
    assert sc(built(ch, [arctic, levels[1]]))["always_prepared"] == ["Hold Person", "Spike Growth"]
    assert sc(built(ch, [forest, levels[1]]))["always_prepared"] == ["Barkskin", "Spider Climb"]
    assert "circle spells are always prepared" in sc(s3)["notes"]
    s9 = built(ch, [forest, *levels[1:8]])
    assert sc(s9)["always_prepared"] == ["Barkskin", "Spider Climb", "Call Lightning", "Plant Growth", "Divination",
                                         "Freedom of Movement", "Commune With Nature", "Tree Stride"]
    assert slot_table(s9)["5"] == (1, 1, "long") and sc(s9)["prepare_count"] == max(1, create.mod(s9["scores"]["WIS"]) + 9)
    assert "Circle Spells" in "".join(s9["features"]) and "CHOSEN" in next(f for f in s9["features"] if f.startswith("Circle of the Land"))


def test_cantrip_damage_and_breath_weapon_follow_the_character_level() -> None:
    # Fire Bolt: 1d10 at 1st level, 2d10 at 5th, 3d10 at 11th, 4d10 at 17th
    ch, levels = _auto("sorcerer")
    for n, dice in ((1, "1d10"), (4, "1d10"), (5, "2d10"), (10, "2d10"), (11, "3d10"), (16, "3d10"), (17, "4d10")):
        bolt = next(a for a in built(ch, levels[: n - 1])["attacks"] if a.startswith("Fire Bolt"))
        assert f", {dice} fire," in bolt, n
    # Dragonborn breath weapon: 2d6, 3d6 at 6th, 4d6 at 11th, 5d6 at 16th level; save DC 8 + CON modifier + proficiency bonus
    dch = build_any("dragonborn", "fighter")[0]["build"]["choices"]
    dlevels = auto_levels(dch, 16)
    for n, dice in ((1, "2d6"), (5, "2d6"), (6, "3d6"), (10, "3d6"), (11, "4d6"), (15, "4d6"), (16, "5d6")):
        s = built(dch, dlevels[: n - 1])
        line = next(f for f in s["features"] if ": breath weapon" in f)
        assert f"{8 + create.mod(s['scores']['CON']) + s['proficiency_bonus']}, {dice} " in line, n


@pytest.mark.parametrize("cls", ["bard", "cleric", "druid", "paladin", "ranger", "sorcerer", "warlock", "wizard"])
def test_every_caster_builds_at_every_level_by_the_class_table(cls: str) -> None:
    ch, levels = _auto(cls)
    c, L = srd.table("Classes")[cls], srd.table("Levels")
    for n in range(2, 21):
        s = built(ch, levels[: n - 1])
        spell = L[f"{cls}-{n}"]["spellcasting"]
        assert s["level"] == n and s["hit_dice"]["max"] == n and s["proficiency_bonus"] == L[f"{cls}-{n}"]["prof_bonus"]
        draconic = n if cls == "sorcerer" else 0  # Draconic Resilience: +1 per level
        assert s["hp"]["max"] == c["hit_die"] + (n - 1) * (c["hit_die"] // 2 + 1) + n * create.mod(s["scores"]["CON"]) + draconic
        got = sc(s)
        want = {str(k): spell[f"spell_slots_level_{k}"] for k in range(1, 10) if spell.get(f"spell_slots_level_{k}")}
        assert {k: v["max"] for k, v in s["spell_slots"].items()} == want and got["max_level"] == max(map(int, want))
        assert all(v["left"] == v["max"] and v["recharge"] == ("short" if cls == "warlock" else "long")
                   for v in s["spell_slots"].values())
        assert len(got["cantrips"]) == spell.get("cantrips_known", 0) + (1 if cls == "druid" else 0), n  # Land: Bonus Cantrip
        lore = 2 if cls == "bard" and n >= 6 else 0  # Additional Magical Secrets don't count against the number known
        if cls in ("bard", "ranger", "sorcerer", "warlock"):
            assert len(got["known"]) == spell["spells_known"] + lore, n
        assert all(srd.spell(x)["level"] <= got["max_level"] for x in got.get("known", []) + got.get("spellbook", []))
        if cls == "wizard":
            assert len(got["spellbook"]) == 6 + 2 * (n - 1)
        if cls in ("cleric", "druid", "wizard"):  # ability modifier + class level
            ability = {"cleric": "WIS", "druid": "WIS", "wizard": "INT"}[cls]
            assert got["prepare_count"] == max(1, create.mod(s["scores"][ability]) + n)
        if cls == "paladin":  # Charisma modifier + half the paladin level, rounded down
            assert got["prepare_count"] == max(1, create.mod(s["scores"]["CHA"]) + n // 2)
        assert len(got.get("arcanum", {})) == (sum(n >= lv for lv in (11, 13, 15, 17)) if cls == "warlock" else 0), n
    assert s["build"]["levels"] == levels and s["level"] == 20


# ---------- later-level choices: Eldritch Invocations, College of Lore, Life domain ----------

def test_invocations_known_column_is_the_pdfs_not_the_datas() -> None:
    # SRD 5.1 pdf, Warlock table: 2nd-4th 2, 5th-6th 3, 7th-8th 4, 9th-11th 5, 12th-14th 6, 15th-17th 7, 18th-20th 8
    assert create.INVOCATIONS_KNOWN == [0, 2, 2, 2, 3, 3, 4, 4, 5, 5, 5, 6, 6, 6, 7, 7, 7, 8, 8, 8]
    assert [create.invocation_needs(n)["learn"] for n in range(2, 21)] == [2, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0]


def test_every_invocation_is_handled_as_its_text_says() -> None:
    invs = {i: f for i, f in srd.table("Features").items() if i.startswith(create.INVOCATION_PREFIX)}
    assert len(invs) == 32 and len(srd.table("Features")["eldritch-invocations"]["feature_specific"]["invocations"]) == 32
    for i, f in invs.items():
        text, key = " ".join(f["desc"]), i.removeprefix(create.INVOCATION_PREFIX)
        assert (key in create.INVOCATION_SPELLS) == ("You can cast " in text), key  # a spell the invocation gives
        if key in create.INVOCATION_SPELLS:
            spell, how = create.INVOCATION_SPELLS[key]
            assert srd.table("Spells")[spell]["name"].lower() in text.lower(), key
            assert (how == "once") == ("once using a warlock spell slot" in text), key
    assert sum(how == "once" for _, how in create.INVOCATION_SPELLS.values()) == 7 and len(create.INVOCATION_SPELLS) == 19


# Pact of the Blade warlock (LOCK: CHA 15 + 1 = 16 (+3), CON 14 (+2)), invocations by the Invocations Known column
BLADE = {"feature.pact-boon": ["Pact of the Blade"]}
BLADE_LEVELS = [
    rec(spells=["Comprehend Languages"], invocations=["Agonizing Blast", "Armor of Shadows"]),  # 2: 2 invocations
    rec(spells=["Misty Step"], choices=BLADE),                                                    # 3: still 2
    rec(asi={"CHA": 2}, cantrips=["Chill Touch"], spells=["Scorching Ray"]),                      # 4: CHA 18 (+4); still 2
    rec(spells=["Fireball"], invocations=["Thirsting Blade"]),                                    # 5: 3
]


@cache
def _blade() -> list:
    """Levels 2-12: the hand-made 2-5, then generated spells, with the invocations of this test."""
    taken = {7: ["Mire the Mind"], 9: ["Ascendant Step"], 12: ["Lifedrinker"]}  # the rises at 7, 9 and 12
    out = []
    for n, r in enumerate(auto_levels(LOCK, 12, start=BLADE_LEVELS), 2):
        if n > 5:
            r = without(r, *create.INVOCATION_KEYS) | ({"invocations": taken[n]} if n in taken else {})
        out.append(r | ({"asi": {"CON": 2}} if n == 8 else {"asi": {"CHA": 2}} if n == 12 else {}))
    return out


def test_warlock_invocations_to_5_and_12() -> None:
    levels = _blade()
    # Invocations Known: 2 (2nd-4th level), 3 (5th, 6th), 4 (7th, 8th), 5 (9th-11th), 6 (12th)
    assert [len(sc(built(LOCK, levels[: n - 1]))["invocations"]) for n in range(2, 13)] == [2, 2, 2, 3, 3, 4, 4, 5, 5, 5, 6]
    s2, s4, s5 = (built(LOCK, levels[: n - 1]) for n in (2, 4, 5))
    # Eldritch Blast: Agonizing Blast adds CHA to each hit. Level 2: CHA +3, proficiency 2: +5 to hit, 1d10+3
    assert attack(s2, "Eldritch Blast") == ("Eldritch Blast (cantrip): +5 spell attack, 1d10+3 force, range 120 feet "
                                            "(Agonizing Blast included)")
    # level 4: CHA 18 (+4), proficiency 2: +6; level 5: proficiency 3: +7, two beams (each hit adds +4)
    assert attack(s4, "Eldritch Blast") == ("Eldritch Blast (cantrip): +6 spell attack, 1d10+4 force, range 120 feet "
                                            "(Agonizing Blast included)")
    assert attack(s5, "Eldritch Blast") == ("Eldritch Blast (cantrip): +7 spell attack, 1d10+4 force per beam, 2 beams, each "
                                            "with its own attack roll, range 120 feet (Agonizing Blast included)")
    assert sc(s5)["invocations"] == ["Agonizing Blast", "Armor of Shadows", "Thirsting Blade"]
    assert "On the Eldritch Blast line: +4 is included" in next(f for f in s5["features"] if "Agonizing Blast:" in f)
    assert has(s5, "Eldritch Invocation: Thirsting Blade") and has(s5, "Pact of the Blade")
    assert sc(s5)["invocation_spells"] == ["Mage Armor (Armor of Shadows, at will, no spell slot)"] and not s5["resources"]
    # level 12: proficiency 4, CHA 20 (+5): +9 to hit, spell save DC 8 + 4 + 5 = 17; three beams from 11th level; Warlock table
    # at 12: three 5th-level slots
    s12 = built(LOCK, levels)
    assert sc(s12)["invocations"] == ["Agonizing Blast", "Armor of Shadows", "Thirsting Blade", "Mire the Mind", "Ascendant Step",
                                      "Lifedrinker"]
    assert attack(s12, "Eldritch Blast").startswith("Eldritch Blast (cantrip): +9 spell attack, 1d10+5 force per beam, 3 beams")
    assert (sc(s12)["save_dc"], slot_table(s12)) == (17, {"5": (3, 3, "short")})
    # "You can cast slow once using a warlock spell slot. You can't do so again until you finish a long rest."
    assert s12["resources"]["Mire the Mind (Slow)"] == {"max": 1, "left": 1, "recharge": "long"}
    assert sorted(s12["resources"]) == ["Dark One's Own Luck", "Mire the Mind (Slow)", "Mystic Arcanum (6th level)"]
    assert "Levitate (Ascendant Step, at will, no spell slot)" in sc(s12)["invocation_spells"]
    assert "Slow (Mire the Mind, once per long rest, using a warlock spell slot)" in sc(s12)["invocation_spells"]
    # Lifedrinker: extra necrotic damage equal to the CHA modifier (minimum 1) = 5
    assert "Extra necrotic damage on your pact weapon's hit: 5." in next(f for f in s12["features"] if "Lifedrinker:" in f)
    assert s12["build"]["levels"] == levels


def test_eldritch_spear_and_the_other_numbers_the_sheet_computes() -> None:
    two = rec(spells=["Comprehend Languages"], invocations=["Eldritch Spear", "Devil's Sight"])
    s = built(LOCK, [two])
    # "its range is 300 feet"; no Agonizing Blast, so the damage is the spell's own
    assert attack(s, "Eldritch Blast") == "Eldritch Blast (cantrip): +5 spell attack, 1d10 force, range 300 feet (Eldritch Spear)"
    assert s["senses"] == "Devil's Sight: see normally in magical and nonmagical darkness to 120 ft"
    # Beguiling Influence: proficiency in Deception and Persuasion. CHA +3 + proficiency 2 = +5
    free = LOCK | {"choices": LOCK["choices"] | {"class.proficiencies.1": ["Arcana", "History"]}}
    one = rec(spells=["Comprehend Languages"], invocations=["Beguiling Influence", "Armor of Shadows"])
    b = built(free, [one])
    assert skills(b)["Deception"] == "+5*" and skills(b)["Persuasion"] == "+5*" and skills(b)["Arcana"].endswith("*")
    assert skills(built(free, []))["Deception"] == "+3"
    # the character already has Deception (LOCK chose it): the same proficiency twice
    assert "Beguiling Influence would gain Skill: Deception twice" in problems([one], LOCK)


def test_invocation_prerequisites_counts_and_duplicates() -> None:
    two = rec(spells=["Comprehend Languages"])
    ok2 = ["Armor of Shadows", "Beast Speech"]

    def at2(*names: str, ch: dict = LOCK) -> str:
        return problems([two | {"invocations": list(names)}], ch)

    # a level prerequisite refers to the warlock level
    assert "level 2: invocations: Mire the Mind needs warlock level 5 (this is level 2)" in at2("Armor of Shadows", "Mire the Mind")
    # a Pact Boon prerequisite: the boon comes at 3rd level, so at 2nd none is chosen yet
    assert "level 2: invocations: Book of Ancient Secrets needs Pact of the Tome" in at2("Armor of Shadows", "Book of Ancient Secrets")
    assert "Voice of the Chain Master needs Pact of the Chain" in at2("Armor of Shadows", "Voice of the Chain Master")
    # a spell prerequisite: the Eldritch Blast cantrip
    nobl = LOCK | {"cantrips": ["Minor Illusion", "Prestidigitation"]}
    assert "level 2: invocations: Agonizing Blast needs the Eldritch Blast cantrip" in at2("Agonizing Blast", "Beast Speech", ch=nobl)
    assert "Repelling Blast needs the Eldritch Blast cantrip" in at2("Armor of Shadows", "Repelling Blast", ch=nobl)
    # level and boon together (Thirsting Blade: 5th level and Pact of the Blade), at 5th level with the Tome
    up3 = LOCK_LEVELS[:3]
    five = rec(spells=["Fireball"])
    assert "level 5: invocations: Thirsting Blade needs Pact of the Blade" in problems(
        [*up3, five | {"invocations": ["Thirsting Blade"]}], LOCK)
    assert "level 5: invocations: Voice of the Chain Master needs Pact of the Chain" in problems(
        [*up3, five | {"invocations": ["Voice of the Chain Master"]}], LOCK)
    assert "Lifedrinker needs warlock level 12 (this is level 5)" in problems([*up3, five | {"invocations": ["Lifedrinker"]}], LOCK)
    assert "Witch Sight needs warlock level 15" in problems([*up3, five | {"invocations": ["Witch Sight"]}], LOCK)
    # Eldritch Blast known as one of the Tome's cantrips counts as knowing the cantrip: refused at 2nd, allowed at 5th
    tome_eb = [two | {"invocations": ok2}, LOCK_LEVELS[1] | {"tome": ["Eldritch Blast", "Guidance", "Light"]}, LOCK_LEVELS[2]]
    assert sc(built(nobl, [*tome_eb, five | {"invocations": ["Eldritch Spear"]}]))["invocations"] == [*ok2, "Eldritch Spear"]
    # exactly the rise of the Invocations Known column, no duplicates
    assert "level 2: invocations: choose exactly 2" in at2("Armor of Shadows") and "level 2: invocations: choose exactly 2" in at2()
    assert "level 2: invocations: choose exactly 2" in at2("Armor of Shadows", "Beast Speech", "Eldritch Sight")
    assert "level 2: invocations: Armor of Shadows is already known" in at2("Armor of Shadows", "Armor of Shadows")
    assert "level 2: invocations: no Eldritch Invocation 'Zork'" in at2("Armor of Shadows", "Zork")
    assert "level 3: invocations: no new invocations at this level" in problems(
        [LOCK_LEVELS[0], LOCK_LEVELS[1] | {"invocations": ["Eldritch Sight"]}], LOCK)
    assert "level 5: invocations: Armor of Shadows is already known" in problems(
        [*up3, five | {"invocations": ["Armor of Shadows"]}], LOCK)
    assert "level 5: invocations: choose exactly 1" in problems([*up3, five], LOCK)
    # every problem at once
    both = at2("Mire the Mind", "Book of Ancient Secrets")
    assert "Mire the Mind needs warlock level 5" in both and "Book of Ancient Secrets needs Pact of the Tome" in both
    # only a warlock; names by index or with the "Eldritch Invocation: " start work too
    assert "level 2: invocations: only a warlock gets Eldritch Invocations" in problems([rec(invocations=ok2)])
    assert "level 2: invocations, rituals: only a warlock" in problems(
        [rec(spells=WREN_LEVELS[0]["spells"], invocations=ok2, rituals=ok2)], WREN)
    names = ["Eldritch Invocation: Armor of Shadows", "eldritch-invocation-beast-speech"]
    assert sc(built(LOCK, [two | {"invocations": names}]))["invocations"] == ok2


def test_replacing_an_invocation_at_a_level_up() -> None:
    # "when you gain a level in this class, you can choose one of the invocations you know and replace it with another
    # invocation that you could learn at that level" (3rd level: the Tome is chosen then, so the Book qualifies)
    first, third = LOCK_LEVELS[0], LOCK_LEVELS[1]
    swap = {"from": "Beast Speech", "to": "Eldritch Sight"}
    s = built(LOCK, [first, third | {"replace_invocation": swap}])
    assert sc(s)["invocations"] == ["Armor of Shadows", "Eldritch Sight"]  # in place
    assert "Detect Magic (Eldritch Sight, at will, no spell slot)" in sc(s)["invocation_spells"] and len(sc(s)["invocation_spells"]) == 2
    book = {"from": "Beast Speech", "to": "Book of Ancient Secrets"}
    s = built(LOCK, [first, third | {"replace_invocation": book, "rituals": ["Alarm", "Identify"]}])
    assert sc(s)["invocations"] == ["Armor of Shadows", "Book of Ancient Secrets"] and sc(s)["book_rituals"] == ["Alarm", "Identify"]
    assert "level 3: rituals: choose exactly 2" in problems([first, third | {"replace_invocation": book}], LOCK)
    unknown = "'Mire the Mind' is not one of the invocations you know (Armor of Shadows, Beast Speech)"
    for bad, why in (({"from": "Mire the Mind", "to": "Eldritch Sight"}, unknown),
                     ({"from": "Beast Speech", "to": "Mire the Mind"}, "Mire the Mind needs warlock level 5 (this is level 3)"),
                     ({"from": "Beast Speech", "to": "Armor of Shadows"}, "Armor of Shadows is already known"),
                     ({"from": "Beast Speech", "to": "Beast Speech"}, "Beast Speech is already known"),
                     ({"from": "Beast Speech", "to": "Voice of the Chain Master"}, "needs Pact of the Chain"),
                     ({"from": "Beast Speech", "to": "Zork"}, "no Eldritch Invocation 'Zork'"),
                     ({"from": "Beast Speech"}, 'replace_invocation: {"from"'), ("Beast Speech", 'replace_invocation: {"from"')):
        assert why in problems([first, third | {"replace_invocation": bad}], LOCK), bad
    # a level that gains one: the new one is not yet known, so it can't be the one replaced, nor chosen twice
    five = LOCK_LEVELS[3] | {"invocations": ["Eldritch Sight"]}
    assert "'Eldritch Sight' is not one of the invocations you know" in problems(
        [*LOCK_LEVELS[:3], five | {"replace_invocation": {"from": "Eldritch Sight", "to": "Misty Visions"}}], LOCK)
    assert "Eldritch Sight is already known" in problems(
        [*LOCK_LEVELS[:3], five | {"replace_invocation": {"from": "Beast Speech", "to": "Eldritch Sight"}}], LOCK)
    # replacing the Book drops its rituals (level 5 learns it; a 6th level replaces it)
    six = auto_levels(LOCK, 6, start=LOCK_LEVELS)[4]
    s6 = built(LOCK, [*LOCK_LEVELS, without(six, *create.INVOCATION_KEYS) | {
        "replace_invocation": {"from": "Book of Ancient Secrets", "to": "Eldritch Sight"}}])
    assert "book_rituals" not in sc(s6) and sc(s6)["invocations"] == ["Armor of Shadows", "Beast Speech", "Eldritch Sight"]


def test_book_of_ancient_secrets_rituals() -> None:
    s5 = built(LOCK, LOCK_LEVELS)
    # "Choose two 1st-level spells that have the ritual tag from any class's spell list" (they don't count as spells known)
    assert sc(s5)["book_rituals"] == ["Find Familiar", "Identify"] and len(sc(s5)["known"]) == 6
    assert "Find Familiar" not in sc(s5)["known"] and has(s5, "Eldritch Invocation: Book of Ancient Secrets")
    up3, five = LOCK_LEVELS[:3], LOCK_LEVELS[3]
    wrong = {"Bless": "Bless is not a 1st-level spell with the ritual tag",
             "Augury": "Augury is not a 1st-level spell with the ritual tag",  # a ritual, but 2nd level
             "Zork": "no SRD spell 'Zork'"}
    for name, why in wrong.items():
        assert f"level 5: rituals: {why}" in problems([*up3, five | {"rituals": ["Find Familiar", name]}], LOCK), name
    assert "level 5: rituals: choose exactly 2" in problems([*up3, without(five, "rituals")], LOCK)
    assert "level 5: rituals: choose exactly 2" in problems([*up3, five | {"rituals": ["Alarm"]}], LOCK)
    assert "level 5: rituals: a spell is listed twice" in problems([*up3, five | {"rituals": ["Alarm", "Alarm"]}], LOCK)
    # from any class's list: Alarm (ranger, wizard), Speak with Animals (bard, druid, ranger)
    got = built(LOCK, [*up3, five | {"rituals": ["Alarm", "Speak with Animals"]}])
    assert sc(got)["book_rituals"] == ["Alarm", "Speak with Animals"]
    assert "level 3: rituals: only when Book of Ancient Secrets is learned" in problems(
        [LOCK_LEVELS[0], LOCK_LEVELS[1] | {"rituals": ["Alarm", "Identify"]}], LOCK)
    # Adding rituals found later (spell level up to half the warlock level, 2 hours and 50 gp per spell level) is play, not
    # a level-up choice: nothing in the record.


def test_lore_bard_bonus_proficiencies_and_later_expertise() -> None:
    ch, levels = _auto("bard")
    s2 = built(ch, levels[:1])
    have = {k for k, v in skills(s2).items() if v.endswith("*")}
    new = [k for k in ("Arcana", "History", "Nature", "Religion", "Survival", "Medicine", "Stealth") if k not in have][:3]
    lore = "feature.bonus-proficiencies"
    r3 = levels[1] | {"choices": levels[1]["choices"] | {lore: new}}
    s3 = built(ch, [levels[0], r3])
    # "you gain proficiency with three skills of your choice": level 3 proficiency bonus 2 + the ability modifier
    ability = {k: srd.table("Skills")[k.lower().replace(" ", "-")]["ability_score"]["name"] for k in new}
    for k in new:
        assert skills(s3)[k] == f"{create.mod(s3['scores'][ability[k]]) + 2:+d}*", k
    now = {k for k, v in skills(s3).items() if v.endswith("*")}
    assert now == have | set(new) and len(now) == len(have) + 3
    assert "CHOSEN: " + ", ".join(f"Skill: {k}" for k in new) in next(f for f in s3["features"] if f.startswith("Bonus Proficiencies"))
    # exactly three, none already proficient, none twice
    assert f"level 3: choices.{lore}: choose exactly 3" in problems(
        [levels[0], r3 | {"choices": r3["choices"] | {lore: new[:2]}}], ch)
    assert f"level 3: choices.{lore}: missing" in problems(
        [levels[0], levels[1] | {"choices": without(levels[1]["choices"], lore)}], ch)
    owned = min(have)
    assert f"Skill: {owned} would be gained twice" in problems(
        [levels[0], r3 | {"choices": r3["choices"] | {lore: [owned, *new[:2]]}}], ch)
    assert f"'Skill: {new[0]}' chosen twice" in problems(
        [levels[0], r3 | {"choices": r3["choices"] | {lore: [new[0], new[0], new[1]]}}], ch)
    # Expertise at 10th level (proficiency 4) on a bonus skill: 2 x 4 + the ability modifier
    r10 = levels[8] | {"choices": levels[8]["choices"] | {"feature.bard-expertise-2": new[:2]}}
    s10 = built(ch, [levels[0], r3, *levels[2:8], r10])
    for k in new[:2]:
        assert skills(s10)[k] == f"{create.mod(s10['scores'][ability[k]]) + 8:+d}**", k
    # expertise still needs a proficiency: a skill that is neither class, background nor Lore is refused
    other = next(k for k in ("Arcana", "History", "Nature", "Religion", "Survival", "Medicine") if k not in have and k not in new)
    bad = r10 | {"choices": r10["choices"] | {"feature.bard-expertise-2": [new[0], other]}}
    assert "needs a proficiency the character has" in problems([levels[0], r3, *levels[2:8], bad], ch)
    # the bonus skills are not asked of other classes
    assert not [cid for cid, _, _ in create.level_sets("rogue", 3) if "bonus-proficiencies" in cid]


def test_life_domain_gets_guardian_of_faith_at_7() -> None:
    # SRD Life Domain Spells table: 7th level Death Ward, Guardian of Faith (the data lacks the second)
    levels = auto_levels(HILDA, 9)
    s6, s7, s9 = (built(HILDA, levels[: n - 1]) for n in (6, 7, 9))
    assert sc(s6)["always_prepared"][-2:] == ["Beacon of Hope", "Revivify"]
    assert sc(s7)["always_prepared"] == ["Bless", "Cure Wounds", "Lesser Restoration", "Spiritual Weapon", "Beacon of Hope",
                                         "Revivify", "Death Ward", "Guardian of Faith"]
    assert sc(s9)["always_prepared"][-4:] == ["Death Ward", "Guardian of Faith", "Mass Cure Wounds", "Raise Dead"]
    assert create.subclass_spells(srd.table("Subclasses")["life"], 6) == [
        "bless", "cure-wounds", "lesser-restoration", "spiritual-weapon", "beacon-of-hope", "revivify"]
