"""Levels above 1: hand-worked sheets, refusals, and every class at every level."""
import copy
import re
from functools import cache

import pytest

from dm import create, srd
from tests.autochar import auto_levels, build_any
from tests.test_create import BRAKKA, ranger

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
    assert "chosen twice" in problems(until9 + [{"hp": "fixed", "choices": {"feature.metamagic-2": [first[0]]}}], sorc)
    s10 = built(sorc, until9 + [{"hp": "fixed", "choices": {"feature.metamagic-2": [other]}}])
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


@pytest.mark.parametrize("cls", ["bard", "cleric", "druid", "paladin", "ranger", "sorcerer", "warlock", "wizard"])
def test_casters_still_build_at_every_level(cls: str) -> None:
    # slice 2 gives them their spells; until then the level-1 casting stays and nothing crashes
    ch, levels = _auto(cls)
    c = srd.table("Classes")[cls]
    for n in range(2, 21):
        s = built(ch, levels[: n - 1])
        assert s["level"] == n and s["hit_dice"]["max"] == n
        draconic = n if cls == "sorcerer" else 0  # Draconic Resilience: +1 per level
        assert s["hp"]["max"] == c["hit_die"] + (n - 1) * (c["hit_die"] // 2 + 1) + n * create.mod(s["scores"]["CON"]) + draconic
