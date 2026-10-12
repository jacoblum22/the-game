"""Levelling up in play: the XP table, level_up_options / level_up with the merge of the live sheet, Fiendish Resilience,
rests, and the hand-made sheets' builds."""
import asyncio
import copy
import json
import re
from pathlib import Path

import pytest

from dm import create, play, srd
from dm import mechanics as m
from tests.test_create import BRAKKA, WREN
from tests.test_levels import (
    FIXED,
    LOCK,
    LOCK_LEVELS,
    PAL,
    STYLE,
    WREN_LEVELS,
    _blade,
    _sheet,
    built,
    rec,
)

CHAR = Path(__file__).parent.parent / "dm" / "characters"
CLASSES = list(srd.table("Classes"))


def hand(name: str) -> dict:
    return json.loads((CHAR / f"{name}.json").read_text(encoding="utf-8"))


def xp(sheet: dict, n: int) -> dict:
    return copy.deepcopy(sheet) | {"xp": n}


# ---------- the XP table ----------

def test_xp_table_is_the_srd_text() -> None:
    rows = re.findall(r"^\| ([\d,]+)\s*\| (\d+)\s*\|", srd.table("Rules")["beyond-1st-level"]["desc"], re.MULTILINE)
    assert {int(lvl): int(n.replace(",", "")) for n, lvl in rows if lvl != "1"} == m.XP_FOR_LEVEL and len(m.XP_FOR_LEVEL) == 19


def test_change_pc_says_when_the_xp_reaches_the_next_level() -> None:
    s = hand("fighter")  # level 1: level 2 at 300 XP
    s, text = m.change_pc(s, {"xp_gained": 299})
    assert text == ["XP +299: 299"] and "XP 299/300" in m.status(s)
    s, text = m.change_pc(s, {"xp_gained": 1})  # exactly 300
    assert text == ["XP +1: 300 - Brakka Ironvein can now go up to level 2 (XP 300): use level_up_options, then level_up"]
    _, text = m.change_pc(s, {"xp_gained": 5000})  # more than enough: still said, still about the next level only
    assert "can now go up to level 2" in text[0]
    old = {k: v for k, v in s.items() if k != "build"}  # an old save without a build record
    assert "no build record" in m.change_pc(old, {"xp_gained": 1})[1][0]
    twenty = hand("fighter") | {"level": 20, "xp": 355000}
    assert "can now go up" not in m.change_pc(twenty, {"xp_gained": 5})[1][0] and m.status(twenty).splitlines()[0].endswith("XP 355000")


# ---------- level_up_options and level_up: refusals ----------

def test_level_up_options_says_the_xp_and_works_before_it_is_there() -> None:
    s = hand("fighter")
    t = m.level_up_options(s)
    assert t.startswith("Brakka Ironvein has 0 XP; level 2 needs 300. NOT ENOUGH YET (300 more): level_up refuses") and "LEVEL UP:" in t
    assert m.level_up_options(xp(s, 300)).startswith("Brakka Ironvein has 300 XP; level 2 needs 300. Enough: ")
    with pytest.raises(m.Refused, match="no build record"):
        m.level_up_options({k: v for k, v in s.items() if k != "build"})
    s20 = _sheet("fighter", 20)
    assert s20["level"] == 20
    with pytest.raises(m.Refused, match="level 20, the highest level"):
        m.level_up_options(s20)


def test_level_up_refusals_change_nothing() -> None:
    s = hand("fighter")
    before = copy.deepcopy(s)
    with pytest.raises(m.Refused, match="level 2 needs 300 XP and Brakka Ironvein has 299"):
        m.level_up(xp(s, 299), FIXED)
    with pytest.raises(m.Refused, match="no build record"):
        m.level_up({k: v for k, v in xp(s, 300).items() if k != "build"}, FIXED)
    with pytest.raises(m.Refused, match="record: the level record"):
        m.level_up(xp(s, 300), "fixed")
    with pytest.raises(m.Refused, match="hp: ") as e:  # every problem, not the first
        m.level_up(xp(s, 300), {"hp": "lots", "asi": {"STR": 2}})
    assert "asi: this level does not grant Ability Score Improvement" in str(e.value) and "nothing changed" in str(e.value)
    assert s == before


# ---------- the merge ----------

def play_state(sheet: dict) -> dict:
    """A character mid-adventure: wounded, a condition, odd items, some money, spent features."""
    s, _ = m.change_pc(sheet, {"damage": 14, "conditions_added": ["poisoned"], "coin_change_gp": 7.5,
                               "items_gained": [{"item": "Ruby ring"}, {"item": "Rations (1 day)", "qty": 2}],
                               "use_resource": "Second Wind"})
    return m.change_pc(s, {"temp_hp": 3})[0]


def test_fighter_3_to_4_keeps_the_live_sheet() -> None:
    # Brakka: Hill dwarf, CON 16 (+3), d10 fixed 6, Dwarven Toughness +1: 10 per level, so 34 at level 3 and 44 at level 4
    s = built(BRAKKA, [FIXED, FIXED])
    s, _ = m.change_pc(s, {"use_resource": "Action Surge", "hit_dice_spent": 1})
    s = play_state(s) | {"xp": 2700}
    assert (s["hp"], s["hit_dice"]) == ({"max": 34, "current": 20, "temp": 3}, {"die": "d10", "max": 3, "left": 2})
    assert s["resources"]["Action Surge"]["left"] == 0 and s["resources"]["Second Wind"]["left"] == 0
    new, text = m.level_up(s, {"hp": "fixed", "asi": {"STR": 2}})
    assert new["level"] == 4 and new["hp"] == {"max": 44, "current": 30, "temp": 3}  # 20 + 10; temporary HP stay
    assert new["hit_dice"] == {"die": "d10", "max": 4, "left": 3}  # the new die is unspent
    # used features stay used (their maximum did not change)
    assert new["resources"]["Action Surge"]["left"] == 0 and new["resources"]["Second Wind"]["left"] == 0
    assert new["items"] == s["items"] and new["items"]["Ruby ring"] == 1 and new["coins_cp"] == 1500 + 750
    assert new["conditions"] == ["poisoned"] and new["death_saves"] == s["death_saves"] and new["xp"] == 2700
    assert new["name"] == "Brakka" and new["scores"]["STR"] == 17
    assert new["ac"] == 18 and new["attacks"][0].startswith("Longsword: +5 to hit, 1d8+5 slashing")  # armor and weapons carried
    assert "Level up done: Brakka is now Hill Dwarf fighter 4" in text and "HP 20/34 -> 30/44" in text
    assert "Ability scores: STR 15 -> 17" in text and "Features whose text changed" in text and "Second Wind" in text
    assert "enough for level 5" not in text
    # a character with the XP for two levels is told so
    assert "enough for level 5 too" in m.level_up(xp(s, 6500), {"hp": "fixed", "asi": {"STR": 2}})[1]


def test_a_character_at_zero_hp_stays_down() -> None:
    s = xp(built(BRAKKA, []), 300)
    s, _ = m.change_pc(s, {"damage": 20})  # 14 HP: down, not dead
    assert s["hp"]["current"] == 0 and "unconscious" in s["conditions"]
    new, _ = m.level_up(s, FIXED)
    assert new["hp"] == {"max": 24, "current": 0, "temp": 0} and "unconscious" in new["conditions"]


def test_wizard_4_to_5_keeps_the_prepared_list_the_spellbook_and_used_slots() -> None:
    # Wren: INT 18 (+4) at 4th level, CON +1, d6 fixed 4: 22 HP at level 4, 27 at 5. Slots 4/3 -> 4/3/2.
    s = built(WREN, WREN_LEVELS[:3])
    assert s["hp"]["max"] == 22 and s["spell_slots"]["2"]["max"] == 3 and "3" not in s["spell_slots"]
    live = ["Shield", "Magic Missile", "Thunderwave", "Misty Step"]  # differs from the list chosen at 1st level
    s, _ = m.change_pc(s, {"long_rest": True, "prepare_spells": live})
    s, _ = m.change_pc(s, {"spellbook_add": ["Mirror Image"], "spend_slot": 1, "damage": 5})
    s, _ = m.change_pc(s, {"spend_slot": 2, "xp_gained": 6500})
    assert s["spellcasting"]["spellbook"][-1] == "Mirror Image" and s["spell_slots"]["1"]["left"] == 3
    with pytest.raises(m.Refused, match="Mirror Image is already in the spellbook"):  # exactly 2 NEW spells per level
        m.level_up(s, rec(spells=["Mirror Image", "Fireball"]))
    new, text = m.level_up(s, WREN_LEVELS[3])  # Fireball, Fly
    sc = new["spellcasting"]
    assert sc["prepared"] == live and sc["prepare_count"] == 9  # the live list stays; INT 4 + level 5
    assert sc["spellbook"][-3:] == ["Fireball", "Fly", "Mirror Image"] and len(sc["spellbook"]) == 15
    assert {k: (v["left"], v["max"]) for k, v in new["spell_slots"].items()} == {"1": (3, 4), "2": (2, 3), "3": (2, 2)}
    assert new["hp"] == {"max": 27, "current": 22, "temp": 0} and new["hit_dice"]["left"] == 5
    assert "Spell slots now: level 1: 3/4, level 2: 2/3, level 3: 2/2" in text and "Spellbook: new Fireball, Fly" in text
    assert "Can prepare up to 9 spells (was 8)" in text and "Mirror Image" not in text
    # the prepared list belongs to the long rest
    assert m.change_pc(new, {"long_rest": True, "prepare_spells": ["Fireball"]})[0]["spellcasting"]["prepared"] == ["Fireball"]


def test_warlock_4_to_5_keeps_the_used_pact_slot_across_the_level_change() -> None:
    s = built(LOCK, LOCK_LEVELS[:3])  # pact slots: two 2nd-level slots, which become two 3rd-level slots at 5th level
    assert s["spell_slots"] == {"2": {"max": 2, "left": 2, "recharge": "short"}}
    s, _ = m.change_pc(s, {"spend_slot": 2})
    new, text = m.level_up(xp(s, 6500), LOCK_LEVELS[3])
    assert new["spell_slots"] == {"3": {"max": 2, "left": 1, "recharge": "short"}} and "level 3: 1/2" in text
    full, _ = m.level_up(xp(built(LOCK, LOCK_LEVELS[:3]), 6500), LOCK_LEVELS[3])  # none used: both are full
    assert full["spell_slots"]["3"]["left"] == 2
    two_used, _ = m.change_pc(m.change_pc(s, {"spend_slot": 2})[0], {"damage": 1})
    assert m.level_up(xp(two_used, 6500), LOCK_LEVELS[3])[0]["spell_slots"]["3"]["left"] == 0


def test_paladin_1_to_2_gets_its_first_prepared_list_and_slots() -> None:
    s = xp(built(PAL, []), 300)
    assert "spellcasting" not in s
    first = ["Bless", "Cure Wounds", "Shield of Faith"]
    new, text = m.level_up(s, rec(choices=STYLE, prepared=first))
    assert new["spellcasting"]["prepared"] == first and new["spell_slots"]["1"] == {"max": 2, "left": 2, "recharge": "long"}
    assert "Prepared spells (the first list): Bless, Cure Wounds, Shield of Faith" in text
    # later levels keep whatever the player prepared after a long rest
    again, _ = m.change_pc(new, {"long_rest": True, "prepare_spells": ["Bless"]})
    assert m.level_up(xp(again, 900), FIXED)[0]["spellcasting"]["prepared"] == ["Bless"]


def test_new_counters_arrive_full_and_pools_keep_what_was_spent() -> None:
    # Lay on Hands is 5 x level: 12 of 15 left at 3rd level is 17 of 20 at 4th
    s = built(PAL, [rec(choices=STYLE, prepared=["Bless"]), FIXED])
    s, _ = m.change_pc(s, {"use_resource": "Lay on Hands", "resource_amount": 3})
    assert s["resources"]["Lay on Hands"] == {"max": 15, "left": 12, "recharge": "long"}
    new, _ = m.level_up(xp(s, 2700), rec(asi={"STR": 2}))
    assert new["resources"]["Lay on Hands"] == {"max": 20, "left": 17, "recharge": "long"}
    # Sneak Attack et al. are features, not counters; the rogue's 1st Action Surge is new at fighter 2nd level
    new, _ = m.level_up(xp(hand("fighter"), 300), FIXED)
    assert new["resources"]["Action Surge"] == {"max": 1, "left": 1, "recharge": "short"}


# ---------- Fiendish Resilience ----------

def test_fiendish_resilience() -> None:
    s10 = built(LOCK, _blade()[:9])
    assert s10["level"] == 10 and "Fiendish Resilience: no damage type chosen yet" in m.status(s10)
    with pytest.raises(m.Refused, match="together with short_rest or long_rest"):
        m.change_pc(s10, {"resilience_type": "Fire"})
    with pytest.raises(m.Refused, match="not an SRD damage type"):
        m.change_pc(s10, {"resilience_type": "Banana", "short_rest": True})
    with pytest.raises(m.Refused, match="doesn't have Fiendish Resilience"):
        m.change_pc(built(LOCK, _blade()[:8]), {"resilience_type": "Fire", "short_rest": True})  # 9th level
    s, text = m.change_pc(s10, {"resilience_type": "fire", "short_rest": True})
    assert s["resilience_type"] == "Fire" and "resistance to Fire damage" in text[-1] and "magical weapons or silver weapons" in text[-1]
    assert "Fiendish Resilience: resistance to Fire damage" in m.status(s)
    s, _ = m.change_pc(s, {"resilience_type": "Force", "long_rest": True})  # "a different one"; the text excludes no type
    assert s["resilience_type"] == "Force"
    # it stays when a rest passes without a new choice, and across a level-up
    s, _ = m.change_pc(s, {"short_rest": True, "xp_gained": 85000})
    assert s["resilience_type"] == "Force"
    new, _ = m.level_up(s, _blade()[9])
    assert new["level"] == 11 and new["resilience_type"] == "Force" and "resistance to Force damage" in m.status(new)
    assert {t["name"] for t in srd.table("Damage-Types").values()} >= {"Fire", "Force", "Psychic", "Radiant"}


# ---------- the sheet text ----------

def test_sheet_text_shows_what_the_later_levels_add() -> None:
    text = play.sheet_text(built(LOCK, _blade()))
    assert "Eldritch Invocations: Agonizing Blast, Armor of Shadows, Thirsting Blade, Mire the Mind, Ascendant Step, Lifedrinker" in text
    assert "Spells from invocations: Mage Armor (Armor of Shadows, at will, no spell slot)" in text
    assert "Mystic Arcanum: level 6: " in text and "Pact of the Tome cantrips" not in text  # LOCK's boon is the Blade here
    assert "Book of Ancient Secrets rituals" not in text and "senses: normal" in text
    tome = play.sheet_text(built(LOCK, LOCK_LEVELS))
    assert "Pact of the Tome cantrips (any class): Guidance, Sacred Flame, Light" in tome
    assert "Book of Ancient Secrets rituals (cast only as rituals): Find Familiar, Identify" in tome
    assert "Always prepared: Bless, Cure Wounds" in play.sheet_text(_sheet("cleric", 3))
    assert "Magical Secrets spells (any class): " in play.sheet_text(_sheet("bard", 10))
    wiz = play.sheet_text(_sheet("wizard", 18)) + play.sheet_text(_sheet("wizard", 20))
    assert "Spell Mastery: " in wiz and "Signature spells: " in wiz
    assert "Devil's Sight" in play.sheet_text(built(LOCK, [rec(spells=["Comprehend Languages"], invocations=["Devil's Sight", "Beast Speech"])]))


# ---------- rests ----------

@pytest.mark.parametrize("cls", CLASSES)
def test_every_counter_comes_back_on_the_rest_its_recharge_says(cls: str) -> None:
    s = copy.deepcopy(_sheet(cls, 20))
    for res in s["resources"].values():
        res["left"] = 0
    for slot in s.get("spell_slots", {}).values():
        slot["left"] = 0
    assert {r["recharge"] for r in s["resources"].values()} <= {"short", "long"}
    short, _ = m.change_pc(s, {"short_rest": True})
    for name, res in short["resources"].items():
        assert res["left"] == (res["max"] if res["recharge"] == "short" else 0), (cls, name)
    for slot in short.get("spell_slots", {}).values():
        assert slot["left"] == (slot["max"] if slot["recharge"] == "short" else 0), cls  # Pact Magic: a short rest
    long, _ = m.change_pc(s, {"long_rest": True})
    assert all(r["left"] == r["max"] for r in long["resources"].values()) and all(
        v["left"] == v["max"] for v in long.get("spell_slots", {}).values())


def test_recharge_values_follow_the_feature_texts() -> None:
    sheets = [_sheet(c, 20) for c in CLASSES] + [built(LOCK, _blade())]
    got = {n: r["recharge"] for s in sheets for n, r in s["resources"].items()}
    # "until you finish a short or long rest" (Channel Divinity, Action Surge, Second Wind, Ki, Signature Spell, Wild Shape)
    # and "long rest" (Rage, Indomitable, Lay on Hands, Sorcery Points, Arcane Recovery, Mystic Arcanum, ...)
    for name in ("Action Surge", "Second Wind", "Ki", "Channel Divinity", "Wild Shape", "Dark One's Own Luck", "Stroke of Luck"):
        assert got.get(name, "short") == "short", name
    for name in ("Indomitable", "Lay on Hands", "Sorcery Points", "Arcane Recovery", "Natural Recovery", "Cleansing Touch"):
        assert got.get(name, "long") == "long", name
    assert all(v == "long" for n, v in got.items() if n.startswith("Mystic Arcanum") or "(Slow)" in n)
    assert all(v == "short" for n, v in got.items() if n.startswith("Signature Spell"))


# ---------- the hand-made sheets ----------

@pytest.mark.parametrize("name", ["fighter", "rogue", "wizard"])
def test_each_hand_made_sheet_is_reproduced_by_its_build(name: str) -> None:
    h = hand(name)
    b = h["build"]
    s, errs = create.build(b["choices"], b["rolled"], b["levels"], carried=h["items"])
    assert s, errs
    for key in ("level", "hp", "hit_dice", "ac", "scores", "abilities", "proficiency_bonus", "saving_throws", "skills",
                "passive_perception", "senses", "resources", "coins_cp", "items", "name", "race", "class", "background"):
        assert s[key] == h[key] or key == "race" and s[key].lower() == h[key].lower(), key
    to_hit = lambda a: re.search(r"[+-]\d+ to hit, \S+ \w+", a)[0]  # the numbers; the wording of the hand-made lines is its own
    if name != "wizard":
        assert to_hit(s["attacks"][0]) == to_hit(h["attacks"][0])
    if name == "wizard":
        sc, hc = s["spellcasting"], h["spellcasting"]
        assert all(sc[k] == hc[k] for k in ("ability", "save_dc", "attack_bonus", "cantrips", "spellbook", "prepared", "prepare_count"))
        assert {k: v["max"] for k, v in s["spell_slots"].items()} == {k: v["max"] for k, v in h["spell_slots"].items()}


@pytest.mark.parametrize("name, levelled, ac", [("fighter", FIXED, 18), ("rogue", FIXED, 14),
                                                ("wizard", rec(spells=["Thunderwave", "Identify"]), 11)])
def test_each_hand_made_sheet_levels_up(name: str, levelled: dict, ac: int) -> None:
    h = hand(name)
    new, text = m.level_up(xp(h, 300), levelled)
    assert new["level"] == 2 and new["ac"] == ac and new["items"] == h["items"] and new["name"] == h["name"]
    assert new["opening"] == h["opening"] and any(a.split(":")[0] in ("Longsword", "Rapier", "Quarterstaff") for a in new["attacks"])
    assert m.status(new).startswith("HP ") and "Level up done" in text


def test_the_play_tools_drive_a_level_up(tmp_path: Path) -> None:
    game = play.Game({"sheet": hand("wizard")}, tmp_path / "save.json")
    tools = {t.name: t.handler for t in game.tools()}

    def call(name: str, **args: object) -> tuple[str, bool]:
        res = asyncio.run(tools[name](args))
        return res["content"][0]["text"], bool(res.get("is_error"))

    text, error = call("level_up_options")
    assert not error and text.startswith("Wren Fennimore has 0 XP; level 2 needs 300. NOT ENOUGH YET")
    text, error = call("level_up", record={"hp": "fixed"})
    assert error and text.startswith("REFUSED, nothing changed: level 2 needs 300 XP") and game.sheet["level"] == 1
    assert "can now go up to level 2" in call("change_pc", xp_gained=300)[0]
    text, error = call("level_up", record={"hp": "fixed", "spells": ["Thunderwave"]})
    assert error and "spells: choose exactly 2" in text and game.sheet["level"] == 1
    text, error = call("level_up", record={"hp": "fixed", "spells": ["Thunderwave", "Identify"]})
    assert not error and "Level up done" in text and "The sheet now (it replaces the one in your instructions):" in text
    assert game.sheet["level"] == 2 and json.loads((tmp_path / "save.json").read_text(encoding="utf-8"))["sheet"]["level"] == 2
    assert "level 3 needs 900" in call("level_up_options")[0]
