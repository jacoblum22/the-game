"""Build a character sheet from choices, by the 2014 SRD rules and data (dm/srd.py).

`choices_for(race, class)` lists every choice the level-1 character needs, each with an id. `build(...)` checks a full
set of choices and works out the sheet in the same format as dm/characters/*.json, or returns every problem at once.
With `levels` (one record per level gained after 1st) it builds the sheet at level 1 + len(levels); `level_sets` lists
the choices a level's features need. The DM model talks the player through the choices; this code only checks them
and does the arithmetic.
"""

from __future__ import annotations

import copy
import math
import re
from collections import Counter
from typing import Any

from dm import srd
from dm.srd import Bad

ABILITIES = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
STANDARD_ARRAY = [15, 14, 13, 12, 10, 8]
POINT_COST = {8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9}
POINTS = 27
BACKGROUND = "acolyte"  # the only SRD background (owner, 2026-10-11)

# Level-1 spell rules the data keeps only in prose (2014 SRD class text).
CASTING = {  # class: (ability, how spells are chosen)
    "bard": ("CHA", "known"), "sorcerer": ("CHA", "known"), "warlock": ("CHA", "known"),
    "cleric": ("WIS", "prepared"), "druid": ("WIS", "prepared"), "wizard": ("INT", "spellbook"),
}
HALF_CASTING = {"paladin": ("CHA", "prepared"), "ranger": ("WIS", "known")}  # their spellcasting starts at 2nd level
CASTERS = CASTING | HALF_CASTING
SPELLBOOK_SIZE = 6  # wizard: six 1st-level wizard spells
BOOK_GAIN = 2  # wizard: two wizard spells added to the spellbook at every level after 1st
SECRETS = 2  # bard Magical Secrets ("Choose two spells from any class") and Lore's Additional Magical Secrets ("two spells")
TOME_CANTRIPS = 3  # Pact of the Tome: "choose three cantrips from any class's spell list"
ALWAYS_PREPARED = {"cleric": "domain", "paladin": "oath", "druid": "circle"}  # the subclass spells that are always prepared
RACE_CANTRIPS = {"infernal-legacy": ("thaumaturgy", "CHA")}  # tiefling: Thaumaturgy at 1st level
SUBCLASS_PROFS = {"life": ["heavy-armor"]}  # Life Domain: Bonus Proficiency
# The SRD Acolyte's gear the dataset leaves out: a prayer book or prayer wheel, 5 sticks of incense, vestments.
ACOLYTE_PRAYER = {"desc": "a prayer book or prayer wheel", "choose": 1, "type": "equipment", "from": {
    "option_set_type": "options_array",
    "options": [{"option_type": "string", "string": "Prayer book"}, {"option_type": "string", "string": "Prayer wheel"}]}}
ACOLYTE_ITEMS = {"Vestments": 1, "Stick of incense": 5}
# Ranger, Favored Enemy: "you also learn one language of your choice that is spoken by your favored enemies, if they
# speak one at all", and "Alternatively, you can select two races of humanoid". The data has neither.
ENEMY_FEATURE = "favored-enemy-1-type"
ENEMY_LANGUAGE_ID = f"feature.{ENEMY_FEATURE}.language"
ENEMY_RACES_ID = f"feature.{ENEMY_FEATURE}.humanoid-races"
ENEMY_RACES_TEXT = ("humanoid races: because 'humanoids' was chosen, name two races of humanoid as the favored enemies "
                    "(such as gnolls and orcs), as a list of two names")
SPELL_KEYS = ("cantrips", "spells", "secrets", "replace", "arcanum", "tome", "mastery", "signature")
RECORD_KEYS = {"hp", "asi", "choices", *SPELL_KEYS}  # a level record's fields
# The class table repeats a feature under a new name as it improves (Bardic Inspiration d6, d8, ...): only the newest
# is shown, with the choices made at every stage. The "-improvement-N" entries are placeholders for subclass features.
FAMILIES = [
    r"^(.*)-d(?:6|8|10|12)$", r"^(.*)-\d+-(?:die|dice|use|uses)$", r"^(.*)-cr-.*$",
    r"^(extra-attack|unarmored-movement|magical-secrets|rogue-expertise|bard-expertise|metamagic|domain-spells|circle-spells)-\d+$",
    r"^(favored-enemy|natural-explorer)-\d+-.*$", r"^(mystic-arcanum)-.*$",
]
NOT_SHOWN = re.compile(r"ability-score-improvement|-improvement-\d+$")


def _family(index: str) -> str:
    for pat in FAMILIES:
        if m := re.match(pat, index):
            return m.group(1)
    return index


def _at_level(by_level: dict[str, Any], level: int, default: Any = None) -> Any:
    """A value the data keeps by character level ({"1": "2d6", "6": "3d6", ...}): the one for the highest key <= level."""
    keys = [int(k) for k in by_level if int(k) <= level]
    return by_level[str(max(keys))] if keys else default


def _enemy_language() -> dict[str, Any]:
    langs = [{"option_type": "reference", "item": {"index": x["index"], "name": x["name"], "url": x["url"]}}
             for x in srd.table("Languages").values()]
    return {"desc": "one language spoken by your favored enemies, if they speak one at all. The code can't tell which "
                    "languages a type of creature speaks: the DM and the player decide which languages fit, or pick "
                    "the last option if they speak none",
            "choose": 1, "type": "language", "from": {
                "option_set_type": "options_array",
                "options": langs + [{"option_type": "string", "string": "None (they speak no language)"}]}}


def mod(score: int) -> int:
    return (score - 10) // 2


def signed(n: int) -> str:
    return f"+{n}" if n >= 0 else str(n)


# ---------- what has to be chosen ----------

# The Levels data leaves out the Circle of the Land druid's choice of land (2nd level) and its Circle Spells (3rd, 5th,
# 7th and 9th level); the Features table has them.
LEVEL_GAPS = {("land", 2): "circle-of-the-land", ("land", 3): "circle-spells-1", ("land", 5): "circle-spells-2",
              ("land", 7): "circle-spells-3", ("land", 9): "circle-spells-4"}


def level_features(cls: str, level: int) -> list[dict[str, Any]]:
    """The features the class and its (only SRD) subclass give at exactly this level."""
    L = srd.table("Levels")
    sc = srd.table("Classes")[cls]["subclasses"][0]["index"]
    rows = [L[f"{cls}-{level}"]] + ([L[f"{sc}-{level}"]] if f"{sc}-{level}" in L else [])
    out = [srd.ref(f) for row in rows for f in row["features"]]
    if gap := LEVEL_GAPS.get((sc, level)):
        out.append(srd.table("Features")[gap])
    return out


def has_asi(cls: str, level: int) -> bool:
    """Does this class level grant Ability Score Improvement?"""
    return any("ability-score-improvement" in f["index"] for f in level_features(cls, level))


def parts(race: str, cls: str, level: int = 1) -> dict[str, Any]:
    """Everything the data gives a character of this race and class at `level`: "level" is the class table row,
    "level1" the first row, "gained" every (level, feature) so far."""
    r = srd.find("Races", race)
    c = srd.find("Classes", cls)
    sub = srd.table("Subraces")[r["subraces"][0]["index"]] if r["subraces"] else None
    sc = srd.table("Subclasses")[c["subclasses"][0]["index"]]
    L = srd.table("Levels")
    gained = [(n, f) for n in range(1, level + 1) for f in level_features(c["index"], n)]
    has_sub = any(f"{sc['index']}-{n}" in L for n in range(1, level + 1))  # gained at its first level with features
    traits = [srd.ref(t) for t in r["traits"]] + ([srd.ref(t) for t in sub["racial_traits"]] if sub else [])
    return {"race": r, "subrace": sub, "class": c, "subclass": sc if has_sub else None, "level": L[f"{c['index']}-{level}"],
            "level1": L[f"{c['index']}-1"], "traits": traits, "gained": gained, "features": [f for _, f in gained],
            "background": srd.table("Backgrounds")[BACKGROUND]}


def _feature_sets(f: dict[str, Any]) -> list[tuple[str, str, dict[str, Any]]]:
    """(id, what it is, option set) for the choices one feature asks for."""
    out = [(f"feature.{f['index']}", f["name"], cs) for cs in (f.get("feature_specific") or {}).values()
           if isinstance(cs, dict) and "choose" in cs]
    if f["index"].startswith("favored-enemy-"):
        out.append((f"feature.{f['index']}.language", f"{f['name']} language", _enemy_language()))
    return out


def level_sets(cls: str, level: int) -> list[tuple[str, str, dict[str, Any]]]:
    """(id, what it is, option set) for every choice the features gained at this level ask for."""
    return [s for f in level_features(srd.find("Classes", cls)["index"], level) for s in _feature_sets(f)]


def choices_for(race: str, cls: str) -> list[tuple[str, str, dict[str, Any]]]:
    """(id, what it is, option set) for every choice this race and class need, besides scores and spells."""
    p, out = parts(race, cls), []
    r, c, b = p["race"], p["class"], p["background"]
    if r.get("ability_bonus_options"):
        out.append(("race.ability_bonuses", f"{r['name']} ability score increases", r["ability_bonus_options"]))
    if r.get("language_options"):
        out.append(("race.languages", f"{r['name']} extra language", r["language_options"]))
    if r.get("starting_proficiency_options"):
        out.append(("race.proficiencies", f"{r['name']} proficiencies", r["starting_proficiency_options"]))
    for t in p["traits"]:
        for key in ("proficiency_choices", "language_options"):
            if t.get(key):
                out.append((f"trait.{t['index']}", t["name"], t[key]))
        for cs in (t.get("trait_specific") or {}).values():
            if isinstance(cs, dict) and "choose" in cs:
                out.append((f"trait.{t['index']}", t["name"], cs))
    for i, cs in enumerate(c["proficiency_choices"], 1):
        out.append((f"class.proficiencies.{i}", f"{c['name']} proficiencies", cs))
    for f in p["features"]:
        out += _feature_sets(f)
    for i, cs in enumerate(c["starting_equipment_options"], 1):
        out.append((f"class.equipment.{i}", f"{c['name']} equipment", cs))
    if b.get("language_options"):
        out.append(("background.languages", f"{b['name']} languages", b["language_options"]))
    for i, cs in enumerate(b["starting_equipment_options"], 1):
        out.append((f"background.equipment.{i}", f"{b['name']} equipment", cs))
    if b["index"] == "acolyte":
        out.append(("background.equipment.prayer", f"{b['name']} equipment", ACOLYTE_PRAYER))
    return out


def slots_at(cls: str, level: int) -> dict[str, int]:
    """The class table's spell slots at this level, by spell level ({"1": 4, "2": 2}); a warlock has one level only."""
    sc = srd.table("Levels")[f"{cls}-{level}"].get("spellcasting") or {}
    return {str(k): sc[f"spell_slots_level_{k}"] for k in range(1, 10) if sc.get(f"spell_slots_level_{k}")}


def max_spell_level(cls: str, level: int) -> int:
    """The highest spell level the class can cast at this level (0: no spell slots yet)."""
    return max(map(int, slots_at(cls, level)), default=0)


def subclass_spells(sub: dict[str, Any] | None, level: int, land: str | None = None) -> list[str]:
    """The subclass's spells (indexes) whose prerequisites are met at this class level: Life domain, Devotion oath,
    Fiend expanded list, and the Circle of the Land spells of the chosen land (a Features index, or None)."""
    out: list[str] = []
    for s in (sub or {}).get("spells", []):
        pre = s["prerequisites"]
        if (all(q["type"] != "level" or int(q["index"].rsplit("-", 1)[1]) <= level for q in pre)
                and all(q["type"] != "feature" or q["index"] == land for q in pre) and s["spell"]["index"] not in out):
            out.append(s["spell"]["index"])
    return out


def spell_pool(cls: str, low: int, high: int, extra: list[str] | None = None) -> list[str]:
    """Indexes of the class's spells of spell level low..high (0 is cantrips), plus `extra` (a subclass's expanded
    list) of those levels."""
    return [i for i, s in srd.table("Spells").items() if low <= s["level"] <= high
            and (any(c["index"] == cls for c in s["classes"]) or i in (extra or []))]


def spell_rules(race: str, cls: str, scores: dict[str, int] | None = None, level: int = 1,
                land: str | None = None) -> dict[str, Any] | None:
    """How the class casts at this level: its ability, how spells are chosen, how many it has, its slots. None before
    the class has spell slots (a paladin or ranger at 1st level) or if it is not a spellcaster. `land` is the Circle of
    the Land druid's chosen land (a Features index)."""
    p = parts(race, cls, level)
    c = p["class"]["index"]
    slots = slots_at(c, level) if c in CASTERS else {}
    if not slots:
        return None
    sc = p["level"]["spellcasting"]
    ability, how = CASTERS[c]
    extra = subclass_spells(p["subclass"], level, land)
    bonus = 1 if any(f["index"] == "bonus-cantrip" for f in p["features"]) else 0  # Land druid: "one additional druid cantrip"
    rules: dict[str, Any] = {"ability": ability, "how": how, "cantrips": sc.get("cantrips_known", 0) + bonus, "class": c,
                             "level": level, "slots": slots, "max_level": max(map(int, slots))}
    if how == "known":
        rules["known"] = sc.get("spells_known", 0)
    if how == "spellbook":
        rules["spellbook"] = SPELLBOOK_SIZE + BOOK_GAIN * (level - 1)
    if how in ("prepared", "spellbook") and scores:
        # ability modifier + class level (cleric, druid, wizard) or half the paladin level rounded down; minimum of one
        rules["prepared"] = max(1, mod(scores[ability]) + (level // 2 if c == "paladin" else level))
    if how == "prepared" and extra:
        rules["always_prepared"] = extra  # domain, oath and circle spells: always prepared, not counted
        extra = []
    rules["expanded"] = extra  # e.g. the Fiend's expanded spell list
    return rules


def level_spell_needs(cls: str, level: int) -> dict[str, Any]:
    """What the record of a level above 1 has to say about spells, from the class table and the features gained then:
    "cantrips"/"spells" = how many to learn, "secrets" = Magical Secrets spells (from any class), "replace" = may
    swap a known spell, "arcanum" = the spell level of the Mystic Arcanum gained (0: none), "mastery"/"signature" =
    Wizard 18/20, "max_level" = the highest spell level castable then. Empty for a class that never casts."""
    if cls not in CASTERS:
        return {}
    L = srd.table("Levels")
    sp, before = L[f"{cls}-{level}"].get("spellcasting") or {}, L[f"{cls}-{level - 1}"].get("spellcasting") or {}
    feats = {f["index"] for f in level_features(cls, level)}
    how = CASTERS[cls][1]
    # Magical Secrets (10th, 14th, 18th): "included in the number in the Spells Known column"; Lore's Additional Magical
    # Secrets (6th): "don't count against the number of bard spells you know"
    counted = SECRETS if any(i.startswith("magical-secrets") for i in feats) else 0
    extra = SECRETS if "additional-magical-secrets" in feats else 0
    arcanum = next((int(m.group(1)) for i in feats if (m := re.match(r"mystic-arcanum-(\d)", i))), 0)
    return {"cantrips": sp.get("cantrips_known", 0) - before.get("cantrips_known", 0) + (1 if "bonus-cantrip" in feats else 0),
            "spells": BOOK_GAIN if how == "spellbook" else
            sp.get("spells_known", 0) - before.get("spells_known", 0) - counted if how == "known" else 0,
            "secrets": counted + extra, "secrets_counted": counted, "replace": how == "known", "arcanum": arcanum,
            "mastery": "spell-mastery" in feats, "signature": "signature-spell" in feats,
            "max_level": max_spell_level(cls, level)}


# ---------- building ----------

def _check_sets(sets: list[tuple[str, str, dict[str, Any]]], picks: dict[str, Any], pre: str,
                errs: list[str]) -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]]]:
    """Check the picks against option sets (`pre` starts every error). Returns (what each id granted, all grants)."""
    granted: list[dict[str, Any]] = []
    chosen: dict[str, list[dict[str, Any]]] = {}
    for cid, what, cs in sets:
        if cid not in picks:
            errs.append(f"{pre}choices.{cid}: missing ({what}, {srd.set_text(cs).splitlines()[0]})")
            continue
        try:
            got = srd.resolve(cs, picks[cid], f"{pre}choices.{cid}")
        except Bad as e:
            errs.append(str(e))
            continue
        chosen[cid] = got
        granted += got
    allowed_ids = {cid for cid, _, _ in sets}
    for cid, got in chosen.items():
        if re.fullmatch(r"feature\.favored-enemy-[\w-]+", cid) and any(g.get("text") == "humanoids" for g in got):
            allowed_ids.add(f"{cid}.humanoid-races")  # 'select two races of humanoid'
            races = picks.get(f"{cid}.humanoid-races")
            if (not isinstance(races, list) or len(races) != 2 or not all(isinstance(x, str) and x.strip() for x in races)
                    or races[0].strip().casefold() == races[1].strip().casefold()):
                errs.append(f"{pre}choices.{cid}.humanoid-races: missing or wrong ({ENEMY_RACES_TEXT})")
    extra_ids = set(picks) - allowed_ids
    if extra_ids:
        errs.append(f"{pre}choices: not needed for this character: {', '.join(sorted(extra_ids))}")
    return chosen, granted


def _check_asi(asi: Any, pre: str, scores: dict[str, int], errs: list[str]) -> None:
    """Ability Score Improvement: +2 to one score or +1 to two; no score above 20. Adds it to `scores` if it is fine."""
    if (not isinstance(asi, dict) or any(a not in ABILITIES or type(v) is not int for a, v in asi.items())
            or sorted(asi.values()) not in ([2], [1, 1])):
        errs.append(f'{pre}asi: one ability +2, e.g. {{"STR": 2}}, or two different abilities +1 each, e.g. '
                    f'{{"STR": 1, "CON": 1}} (abilities: {", ".join(ABILITIES)})')
        return
    over = [f"{a} would be {scores[a] + v}" for a, v in asi.items() if scores and scores[a] + v > 20]
    if over:
        errs.append(f"{pre}asi: no score can go above 20 ({'; '.join(over)})")
        return
    for a, v in asi.items():
        if scores:
            scores[a] += v


def _check_record(rec: dict[str, Any], level: int, c: dict[str, Any], errs: list[str]) -> int | None:
    """The record's fields that need no ability scores. Returns the hit points the level's Hit Die (or the fixed value)
    gives, before Constitution; None if wrong."""
    pre = f"level {level}: "
    if extra := set(rec) - RECORD_KEYS:
        errs.append(f"{pre}not a level-record field: {', '.join(sorted(extra))} (fields: {', '.join(sorted(RECORD_KEYS))})")
    die, hp, got = c["hit_die"], rec.get("hp"), None
    if hp == "fixed":
        got = die // 2 + 1  # SRD class entries: "1d10 (or 6)"
    elif isinstance(hp, dict) and set(hp) == {"rolled"} and type(hp["rolled"]) is int and 1 <= hp["rolled"] <= die:
        got = hp["rolled"]
    else:
        errs.append(f'{pre}hp: "fixed" ({die // 2 + 1}) or {{"rolled": 1 to {die}}} (the d{die} result, before Constitution)'
                    + (f"; {hp['rolled']} is not on a d{die}" if isinstance(hp, dict) and type(hp.get("rolled")) is int else ""))
    asi = has_asi(c["index"], level)
    if asi and "asi" not in rec:
        errs.append(f"{pre}asi: missing (this level grants Ability Score Improvement)")
    elif "asi" in rec and not asi:
        errs.append(f"{pre}asi: this level does not grant Ability Score Improvement")
    return got  # the spell fields are checked by _spells


def build(ch: dict[str, Any], rolled: list[int] | None = None, levels: list[dict[str, Any]] | None = None,
          carried: dict[str, int] | None = None) -> tuple[dict[str, Any] | None, list[str]]:
    """Returns (sheet, []) or (None, problems). The sheet is at level 1 + len(levels): each level record is
    {"hp": "fixed" | {"rolled": n}, "asi": {...} at levels that grant it, "choices": {"feature.<index>": pick}}.
    `carried` ({item name: quantity}) replaces the starting gear for AC and attacks and becomes the sheet's items."""
    errs: list[str] = []
    levels = levels or []
    if not isinstance(levels, list) or not all(isinstance(x, dict) for x in levels):
        return None, ["levels: a list of level records, one per level gained after 1st"]
    if len(levels) > 19:
        return None, ["levels: the highest level is 20 (at most 19 level records)"]
    if carried is not None and not (isinstance(carried, dict) and all(isinstance(k, str) and type(v) is int and v >= 1
                                                                      for k, v in carried.items())):
        return None, ["carried: {item name: quantity}, quantities whole numbers of 1 or more"]
    N = 1 + len(levels)
    try:
        p = parts(ch.get("race", ""), ch.get("class", ""), N)
    except Bad as e:
        return None, [str(e)]
    r, sub, c, sc, b = p["race"], p["subrace"], p["class"], p["subclass"], p["background"]
    feat_ids = {f["index"] for f in p["features"]}
    name = str(ch.get("name") or "").strip()
    if not name:
        errs.append("name: the character needs a name")

    # ability scores
    base = ch.get("base_scores") or {}
    scores: dict[str, int] = {}
    if sorted(base) != sorted(ABILITIES) or not all(isinstance(v, int) for v in base.values()):
        errs.append(f"base_scores: give all six of {', '.join(ABILITIES)} as whole numbers, before racial increases")
    else:
        vals, method = list(base.values()), ch.get("ability_method")
        if method == "standard_array" and sorted(vals, reverse=True) != STANDARD_ARRAY:
            errs.append(f"base_scores: the standard array is exactly {STANDARD_ARRAY}, one each")
        elif method == "point_buy":
            if any(v not in POINT_COST for v in vals):
                errs.append("base_scores: point buy scores must be 8 to 15")
            elif sum(POINT_COST[v] for v in vals) > POINTS:
                errs.append(f"base_scores: point buy costs {sum(POINT_COST[v] for v in vals)} points; the budget is {POINTS} "
                            f"(costs: {POINT_COST})")
        elif method == "rolled":
            if not rolled:
                errs.append("base_scores: no scores have been rolled yet; use roll_ability_scores")
            elif sorted(vals) != sorted(rolled):
                errs.append(f"base_scores: must use the rolled scores {sorted(rolled, reverse=True)}, one each")
        elif method not in ("standard_array", "point_buy", "rolled"):
            errs.append("ability_method: standard_array, point_buy or rolled")
        scores = dict(base)

    # every option set
    sets = choices_for(r["index"], c["index"])  # the level-1 character's; each later level adds its features' own
    picks = dict(ch.get("choices") or {})  # every pick at every level: ids are unique (one per feature)
    chosen, granted = _check_sets(sets, picks, "", errs)

    # racial increases
    bonuses = [{"bonus": x["ability_score"]["name"], "n": x["bonus"]}
               for x in r["ability_bonuses"] + (sub["ability_bonuses"] if sub else [])]
    bonuses += [g for g in granted if "bonus" in g]
    if scores:
        for x in bonuses:
            scores[x["bonus"]] += x["n"]
    scores1 = dict(scores)  # the scores at 1st level: the prepared list chosen then is checked against them

    # the levels after 1st: hit points, Ability Score Improvement and the choices of the features gained
    hp_rolls: list[int] = []
    asi_log: list[str] = []
    pre_of: dict[str, str] = {}  # the error prefix of each later-level choice id
    level_chosen: list[dict[str, Any]] = []  # what each level's choices granted
    for i, rec in enumerate(levels):
        level = i + 2
        pre = f"level {level}: "
        level_chosen.append({})
        if (got := _check_record(rec, level, c, errs)) is not None:
            hp_rolls.append(got)
        if "asi" in rec and has_asi(c["index"], level):
            before = dict(scores)
            _check_asi(rec["asi"], pre, scores, errs)
            if scores != before:
                asi_log.append(f"level {level}: " + ", ".join(f"{a} +{v}" for a, v in rec["asi"].items()))
        rec_picks = rec.get("choices") or {}
        if not isinstance(rec_picks, dict):
            errs.append(f"{pre}choices: {{id: pick}} for the features gained at this level")
            continue
        got_chosen, got_granted = _check_sets(level_sets(c["index"], level), rec_picks, pre, errs)
        picks |= rec_picks
        level_chosen[-1] = got_chosen
        chosen |= got_chosen
        pre_of |= {cid: pre for cid in got_chosen}
        granted += got_granted
    if "primal-champion" in feat_ids and scores:  # "Your Strength and Constitution scores increase by 4. Your maximum ... 24."
        for a in ("STR", "CON"):
            scores[a] = min(24, scores[a] + 4)
    again = sorted(i for i, n in Counter(g["index"] for g in granted if g.get("kind") == "Features").items() if n > 1)
    if again:  # Fighting Style: "You can't take a Fighting Style option more than once"; Metamagic: "another one"
        errs.append("choices: chosen twice: " + ", ".join(srd.table("Features")[i]["name"] for i in again))
    M = {a: mod(scores.get(a, 10)) for a in ABILITIES}
    prof = p["level"]["prof_bonus"]

    # proficiencies
    prof_ids = {x["index"] for x in c["proficiencies"]}
    prof_ids |= {x["index"] for t in p["traits"] for x in t.get("proficiencies", [])}
    prof_ids |= {x["index"] for x in (r.get("starting_proficiencies") or [])}
    prof_ids |= {x["index"] for x in b["starting_proficiencies"]}
    prof_ids |= set(SUBCLASS_PROFS.get(sc["index"], []) if sc else [])
    P = srd.table("Proficiencies")
    chosen_profs = [g["index"] for cid, got in chosen.items() if "expertise" not in cid
                    for g in got if g.get("kind") == "Proficiencies"]
    # 2014: the same proficiency from two sources is replaced by another of the player's choice
    twice = sorted({i for i in chosen_profs if i in prof_ids or chosen_profs.count(i) > 1})
    if twice:
        errs.append(f"choices: {', '.join(P[i]['name'] for i in twice)} would be gained twice (it already comes from "
                    "race, class or background, or was chosen twice); choose a different option")
    prof_ids |= set(chosen_profs)
    # "(if proficient)" in an equipment option: only for items the character is proficient with
    owned = _owned_prof(prof_ids)
    for cid, _, cs in sets:
        if cid.startswith("class.equipment.") and "(if proficient)" in cs.get("desc", "") and cid in chosen:
            bits = re.split(r"\(([a-z])\) ", cs["desc"])[1:]  # ["a", "a mace or ", "b", "a warhammer (if proficient)"]
            text = dict(zip(bits[::2], bits[1::2]))
            for e in [picks[cid]] if isinstance(picks[cid], (str, dict)) else picks[cid]:
                name = e.get("option") if isinstance(e, dict) else e
                if "(if proficient)" in text[srd.LETTERS[srd._option_index(cs["from"]["options"], str(name), cid)]]:
                    for g in chosen[cid]:
                        if g.get("kind") == "Equipment" and g["index"] not in owned:
                            errs.append(f"choices.{cid}: {srd.table('Equipment')[g['index']]['name']} is only an option "
                                        "if the character is proficient with it, and this character is not; choose "
                                        "a different option")
    skills = {P[i]["reference"]["index"] for i in prof_ids if P[i]["type"] == "Skills"}
    saves = {P[i]["reference"]["index"].upper() for i in prof_ids if P[i]["type"] == "Saving Throws"}
    if "diamond-soul" in feat_ids:  # "proficiency in all saving throws"
        saves |= set(ABILITIES)
    if "slippery-mind" in feat_ids:  # "You gain proficiency in Wisdom saving throws."
        saves.add("WIS")
    expertise: set[str] = set()
    for cid, got in chosen.items():
        if cid.startswith("feature.") and "expertise" in cid:
            for g in got:
                ref = P[g["index"]]["reference"]["index"] if g.get("kind") == "Proficiencies" else ""
                if g["index"] not in prof_ids:
                    errs.append(f"{pre_of.get(cid, '')}choices.{cid}: expertise needs a proficiency the character has "
                                f"({P[g['index']]['name']})")
                elif (ref or g["index"]) in expertise:  # "choose two more of your proficiencies"
                    errs.append(f"{pre_of.get(cid, '')}choices.{cid}: {P[g['index']]['name']} already has expertise")
                expertise.add(ref or g["index"])

    # items
    items: Counter[str] = Counter()
    E = srd.table("Equipment")

    def add_item(index: str, n: int) -> None:
        it = E[index]
        if it.get("contents"):  # equipment packs are unpacked
            for x in it["contents"]:
                add_item(x["item"]["index"], x["quantity"] * n)
        else:
            items[index] += n

    for x in c["starting_equipment"] + b["starting_equipment"]:
        add_item(x["equipment"]["index"], x["quantity"])
    for g in granted:
        if g.get("kind") == "Equipment":
            add_item(g["index"], g["count"])
    if carried is not None:  # what the character has now: names matched to the SRD (case ignored), others ignored
        by_name = {e["name"].casefold(): i for i, e in E.items()}
        items = Counter()
        for nm, q in carried.items():
            if nm.strip().casefold() in by_name:
                items[by_name[nm.strip().casefold()]] += q

    # spells: the level-1 casting, then each level's record
    spells = _spells(ch, r["index"], c["index"], scores, scores1, chosen, level_chosen, levels, errs)

    if errs:
        return None, errs
    sheet = _sheet(ch, name, p, scores, M, prof, prof_ids, skills, saves, expertise, items, chosen, spells,
                   picks=picks, hp_rolls=hp_rolls, asi_log=asi_log)
    if carried is not None:
        sheet["items"] = dict(carried)
    elif b["index"] == "acolyte":  # items the dataset lacks are kept by name
        named = Counter(ACOLYTE_ITEMS) + Counter(g["text"] for g in chosen["background.equipment.prayer"])
        for n, q in named.items():
            sheet["items"][n] = sheet["items"].get(n, 0) + q
    sheet["build"] = copy.deepcopy({"choices": ch, "rolled": rolled, "levels": levels})
    return sheet, []


def _owned_prof(prof_ids: set[str]) -> set[str]:
    """Equipment indexes the proficiencies cover: a proficiency points at an item or at a category of items."""
    owned: set[str] = set()
    for i in prof_ids:
        ref = srd.table("Proficiencies")[i]["reference"]
        if "/equipment-categories/" in ref["url"]:
            owned |= {e["index"] for e in srd.table("Equipment-Categories")[ref["index"]]["equipment"]}
        elif "/equipment/" in ref["url"]:
            owned.add(ref["index"])
    return owned


def _ordinal(n: int) -> str:
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def _check_names(key: str, names: Any, n: int, allowed: set[str], label: str, errs: list[str], atmost: bool = False,
                 taken: set[str] | None = None, have: str = "known") -> list[str]:
    """Spell names the player gave: exactly n (1 to n if `atmost`), each an SRD spell in `allowed` (`label` finishes
    "X is not ..."), none twice and none in `taken` ("X is already <have>"). Returns the valid ones, as indexes."""
    if not isinstance(names, list) or not (1 <= len(names) <= n if atmost else len(names) == n):
        errs.append(f"{key}: choose " + (f"1 to {n} (the most you can prepare)" if atmost else f"exactly {n}"))
        return []
    out, seen = [], []
    for nm in names:
        try:
            s = srd.spell(nm)
        except Bad:
            errs.append(f"{key}: no SRD spell {nm!r}")
            continue
        seen.append(s["index"])
        if s["index"] in (taken or ()):
            errs.append(f"{key}: {s['name']} is already {have}")
        elif s["index"] not in allowed:
            errs.append(f"{key}: {s['name']} is not {label}")
        else:
            out.append(s["index"])
    if len(set(seen)) != len(seen):
        errs.append(f"{key}: a spell is listed twice")
    return out


def _is_spell(name: str) -> bool:
    try:
        srd.spell(name)
    except Bad:
        return False
    return True


def _spells(ch: dict[str, Any], race: str, cls: str, scores: dict[str, int], scores1: dict[str, int],
            chosen: dict[str, Any], level_chosen: list[dict[str, Any]], levels: list[dict[str, Any]],
            errs: list[str]) -> dict[str, Any] | None:
    """The character's spells at level 1 + len(levels): the level-1 choices (cantrips, spells, prepared) checked against
    the 1st-level class text, then each level record's spell fields (`_level_spells`)."""
    rules1 = spell_rules(race, cls, scores1 or None)
    given = {k: ch.get(k) for k in ("cantrips", "spells", "prepared") if ch.get(k)}
    st: dict[str, Any] = {"cantrips": [], "known": [], "spellbook": [], "prepared": [], "secrets": [], "arcanum": {},
                          "tome": [], "mastery": [], "signature": []}
    if cls not in CASTERS:
        if given:
            errs.append(f"{', '.join(given)}: a level-1 {cls} has no spells")
        for i, rec in enumerate(levels):
            if keys := [k for k in SPELL_KEYS if rec.get(k)]:
                errs.append(f"level {i + 2}: {', '.join(keys)}: a {srd.table('Classes')[cls]['name'].lower()} has no spells")
        return None
    if not rules1:  # a paladin or ranger: the first spells come with the 2nd level
        if given:
            errs.append(f"{', '.join(given)}: a level-1 {cls} has no spells")
    else:
        def level1(level: int) -> set[str]:
            return set(spell_pool(cls, level, level, rules1["expanded"]))

        st["cantrips"] = _check_names("cantrips", ch.get("cantrips"), rules1["cantrips"], level1(0),
                                      f"a level-0 {cls} spell", errs)
        if rules1["how"] == "known":
            st["known"] = _check_names("spells", ch.get("spells"), rules1["known"], level1(1), f"a level-1 {cls} spell", errs)
        elif rules1["how"] == "spellbook":
            st["spellbook"] = _check_names("spells", ch.get("spells"), rules1["spellbook"], level1(1),
                                           f"a level-1 {cls} spell", errs)
            if "prepared" in rules1:
                st["prepared"] = _check_names("prepared", ch.get("prepared"), rules1["prepared"], set(st["spellbook"]),
                                              f"a level-1 {cls} spell in the spellbook", errs, atmost=True)
        elif "prepared" in rules1:
            if ch.get("spells"):
                errs.append(f"spells: a {cls} prepares spells from the whole class list; use prepared")
            st["prepared"] = _check_names("prepared", ch.get("prepared"), rules1["prepared"], level1(1),
                                          f"a level-1 {cls} spell", errs, atmost=True)
    for i, rec in enumerate(levels):
        _level_spells(rec, i + 2, cls, st, errs, level_chosen[i])
    land = next((g["index"] for g in chosen.get("feature.circle-of-the-land", [])), None)
    rules = spell_rules(race, cls, scores or None, 1 + len(levels), land)
    if not rules:
        return None
    out: dict[str, Any] = {"rules": rules, "cantrips": st["cantrips"], "secrets": st["secrets"], "arcanum": st["arcanum"],
                           "tome": st["tome"], "mastery": st["mastery"], "signature": st["signature"]}
    if rules["how"] == "known":
        out["known"] = st["known"]
    if rules["how"] == "spellbook":
        out["spellbook"] = st["spellbook"]
    if rules["how"] in ("spellbook", "prepared"):
        out["prepared"] = st["prepared"]  # the list chosen at 1st level; the live list belongs to the long rests
    return out


def _level_spells(rec: dict[str, Any], L: int, cls: str, st: dict[str, Any], errs: list[str],
                  picked: dict[str, Any]) -> None:
    """Check the spell fields of the record of level L against the class text and apply them to `st`, the spells so far.
    `picked` is what the level's feature choices granted (Pact of the Tome gives cantrips)."""
    pre = f"level {L}: "
    need = level_spell_needs(cls, L)
    top, how = need["max_level"], CASTERS[cls][1]
    sub = srd.table("Subclasses")[srd.table("Classes")[cls]["subclasses"][0]["index"]]
    extra = subclass_spells(sub, L) if how == "known" else []  # the Fiend's expanded spell list
    spells = srd.table("Spells")
    prior = list(st["known"])

    def holds() -> set[str]:
        return set(st["known"]) | set(st["cantrips"])

    # Cantrips Known column (a Land druid's Bonus Cantrip is one more at 2nd level)
    if need["cantrips"]:
        st["cantrips"] += _check_names(f"{pre}cantrips", rec.get("cantrips"), need["cantrips"], set(spell_pool(cls, 0, 0)),
                                       f"a {cls} cantrip", errs, taken=holds())
    elif rec.get("cantrips"):
        errs.append(f"{pre}cantrips: no new cantrips at this level (the Cantrips Known column doesn't go up)")

    # new spells: known casters learn the rise of the Spells Known column (spell level no higher than their slots);
    # a wizard adds two wizard spells to the spellbook
    if how == "spellbook":
        st["spellbook"] += _check_names(f"{pre}spells", rec.get("spells"), need["spells"], set(spell_pool(cls, 1, top)),
                                        f"a wizard spell of level 1 to {top}", errs, taken=set(st["spellbook"]),
                                        have="in the spellbook")
    elif need["spells"]:
        st["known"] += _check_names(f"{pre}spells", rec.get("spells"), need["spells"], set(spell_pool(cls, 1, top, extra)),
                                    f"a {cls} spell of level 1 to {top}", errs, taken=holds())
    elif rec.get("spells"):
        errs.append(f"{pre}spells: " + (
            f"a {cls} prepares spells from the whole class list, so there are no spells to learn" if how == "prepared" else
            "no new spells known at this level" + (" (the new Spells Known are the Magical Secrets: use secrets)"
                                                   if need["secrets_counted"] else " (the Spells Known column doesn't go up)")))

    # Magical Secrets: two spells "from any class" of a level you can cast "or a cantrip", bard spells for you
    if need["secrets"]:
        names = _check_names(f"{pre}secrets", rec.get("secrets"), need["secrets"],
                             {i for i, s in spells.items() if s["level"] <= top}, f"a spell of level {top} or lower",
                             errs, taken=holds())
        st["known"] += names
        st["secrets"] += names
    elif rec.get("secrets"):
        errs.append(f"{pre}secrets: only bards get Magical Secrets (Lore bards at 6th level, every bard at 10th, 14th and "
                    "18th), and not at this level")

    # replacing one known spell when a level is gained (bard, ranger, sorcerer, warlock)
    if rec.get("replace"):
        rep = rec["replace"]
        if not need["replace"]:
            errs.append(f"{pre}replace: a {cls} doesn't replace known spells (only bards, rangers, sorcerers and warlocks)")
        elif not (isinstance(rep, dict) and set(rep) == {"from", "to"} and all(isinstance(v, str) for v in rep.values())):
            errs.append(f'{pre}replace: {{"from": "<a spell you know>", "to": "<a {cls} spell>"}}')
        elif not _is_spell(rep["from"]) or not _is_spell(rep["to"]):
            errs.append(f"{pre}replace: no SRD spell {rep['from'] if not _is_spell(rep['from']) else rep['to']!r}")
        else:
            old, new = srd.spell(rep["from"]), srd.spell(rep["to"])
            if old["index"] not in prior:
                errs.append(f"{pre}replace: {old['name']} is not one of the spells you know "
                            f"({', '.join(spells[i]['name'] for i in prior) or 'none yet'})")
            elif new["index"] not in spell_pool(cls, 1, top, extra):
                errs.append(f"{pre}replace: {new['name']} is not a {cls} spell of level 1 to {top}")
            elif new["index"] in holds():
                errs.append(f"{pre}replace: {new['name']} is already known")
            else:
                st["known"][st["known"].index(old["index"])] = new["index"]

    # Mystic Arcanum: one spell of the arcanum's level from the warlock list
    if need["arcanum"]:
        lv, name = need["arcanum"], rec.get("arcanum")
        if not isinstance(name, str) or not _is_spell(name):
            errs.append(f"{pre}arcanum: the name of one {_ordinal(lv)}-level {cls} spell (Mystic Arcanum)")
        elif (s := srd.spell(name))["index"] not in spell_pool(cls, lv, lv, extra):
            errs.append(f"{pre}arcanum: {s['name']} is not a {_ordinal(lv)}-level {cls} spell")
        else:
            st["arcanum"][str(lv)] = s["index"]
    elif rec.get("arcanum"):
        errs.append(f"{pre}arcanum: Mystic Arcanum comes to a warlock at 11th, 13th, 15th and 17th level")

    # Pact of the Tome: "choose three cantrips from any class's spell list"
    if any(g.get("index") == "pact-of-the-tome" for g in picked.get("feature.pact-boon", [])):
        st["tome"] += _check_names(f"{pre}tome", rec.get("tome"), TOME_CANTRIPS, {i for i, s in spells.items() if s["level"] == 0},
                                   "a cantrip", errs)
    elif rec.get("tome"):
        errs.append(f"{pre}tome: only when Pact of the Tome is chosen at this level (three cantrips from any class)")

    # Wizard: Spell Mastery "Choose a 1st-level wizard spell and a 2nd-level wizard spell that are in your spellbook";
    # Signature Spell "Choose two 3rd-level wizard spells in your spellbook"
    for key, levels_wanted, feature in (("mastery", [1, 2], "Spell Mastery"), ("signature", [3, 3], "Signature Spell")):
        if not need[key]:
            if rec.get(key):
                errs.append(f"{pre}{key}: only a wizard at {'18th' if key == 'mastery' else '20th'} level ({feature})")
            continue
        names, book = rec.get(key), set(st["spellbook"])
        wanted = " and ".join(f"a {_ordinal(n)}-level wizard spell" for n in levels_wanted) if key == "mastery" \
            else "two 3rd-level wizard spells"
        if not (isinstance(names, list) and len(names) == 2 and all(isinstance(x, str) and _is_spell(x) for x in names)):
            errs.append(f"{pre}{key}: {wanted} that are in your spellbook, as a list of two names")
            continue
        found = [srd.spell(x) for x in names]
        if sorted(s["level"] for s in found) != levels_wanted or len({s["index"] for s in found}) != 2:
            errs.append(f"{pre}{key}: {feature} needs {wanted}, not {' and '.join(s['name'] for s in found)}")
        elif missing := [s["name"] for s in found if s["index"] not in book]:
            errs.append(f"{pre}{key}: {', '.join(missing)} must be in your spellbook")
        else:
            st[key] = [s["index"] for s in found]


def _sheet(ch: dict[str, Any], name: str, p: dict[str, Any], scores: dict[str, int], M: dict[str, int], prof: int,
           prof_ids: set[str], skills: set[str], saves: set[str], expertise: set[str], items: Counter[str],
           chosen: dict[str, Any], spells: dict[str, Any] | None, picks: dict[str, Any], hp_rolls: list[int],
           asi_log: list[str]) -> dict[str, Any]:
    r, sub, c, sc, b, lvl = p["race"], p["subrace"], p["class"], p["subclass"], p["background"], p["level"]
    E, P = srd.table("Equipment"), srd.table("Proficiencies")
    N = lvl["level"]
    trait_ids = {t["index"] for t in p["traits"]}
    feat_ids = {f["index"] for f in p["features"]}
    cs = lvl.get("class_specific") or {}
    # fighting styles chosen so far (Fighter, Paladin, Ranger, and the Champion's second one)
    styles = {g["index"].split("fighting-style-", 1)[1] for got in chosen.values() for g in got
              if g.get("kind") == "Features" and "fighting-style-" in g["index"]}

    owned_prof = _owned_prof(prof_ids)

    # hit points: the Hit Die at 1st level, then each level's roll (or the fixed value); Constitution (as it is now)
    # for every level, and +1 per level from Dwarven Toughness and Draconic Resilience
    hp = (c["hit_die"] + sum(hp_rolls) + N * (M["CON"] + (1 if "dwarven-toughness" in trait_ids else 0)
                                                   + (1 if "draconic-resilience" in feat_ids else 0)))

    # armor class: the best the character can wear from what they carry
    armors = [E[i] for i in items if E[i].get("armor_category") in ("Light", "Medium", "Heavy") and i in owned_prof]
    shield = "shield" in items and "shield" in owned_prof
    options = [(10 + M["DEX"], "no armor: 10 + DEX", True)]
    if "barbarian-unarmored-defense" in feat_ids:
        options.append((10 + M["DEX"] + M["CON"], "Unarmored Defense: 10 + DEX + CON", True))
    if "monk-unarmored-defense" in feat_ids:
        options.append((10 + M["DEX"] + M["WIS"], "Unarmored Defense: 10 + DEX + WIS (no shield)", False))
    if "draconic-resilience" in feat_ids:
        options.append((13 + M["DEX"], "Draconic Resilience: 13 + DEX", True))
    for a in armors:
        ac = a["armor_class"]
        dex = min(M["DEX"], ac["max_bonus"]) if ac.get("max_bonus") is not None else M["DEX"]
        options.append((ac["base"] + (dex if ac["dex_bonus"] else 0),
                        f"{a['name']} {ac['base']}" + (f" + DEX {dex}" if ac["dex_bonus"] else ""), True))
    scored = [(v + (2 if shield and ok else 0) + (1 if "defense" in styles and "no armor" not in n and "Unarmored" not in n
                                                    and "Resilience" not in n else 0), n, ok) for v, n, ok in options]
    ac, ac_note, ok = max(scored, key=lambda x: (x[0], not x[1].startswith("no armor")))  # a tie names the feature
    if shield and ok:
        ac_note += " + shield 2"
    if "defense" in styles and armors and any(a["name"] in ac_note for a in armors):
        ac_note += " + Defense 1"
    worn = next((a for a in armors if a["name"] in ac_note), None)
    speed, speed_notes = r["speed"], []
    if worn and worn.get("str_minimum", 0) > scores["STR"]:
        if r["index"] == "dwarf":
            speed_notes.append("not reduced by heavy armor")
        else:
            speed -= 10
            speed_notes.append(f"heavy armor without STR {worn['str_minimum']}")
    if worn and worn.get("stealth_disadvantage"):
        ac_note += "; disadvantage on Stealth"
    if "fast-movement" in feat_ids and not (worn and worn.get("armor_category") == "Heavy"):
        speed += 10  # Fast Movement: "your speed increases by 10 feet while you aren't wearing heavy armor"
        speed_notes.append("includes Fast Movement +10 ft, which applies only while not wearing heavy armor")
    if cs.get("unarmored_movement") and not worn and not (shield and ok):
        speed += cs["unarmored_movement"]  # "your speed increases by 10 feet while you are not wearing armor or wielding a shield"
        speed_notes.append(f"includes Unarmored Movement +{cs['unarmored_movement']} ft, which applies only while "
                           "wearing no armor and wielding no shield")
    speed_note = f"{speed} ft" + (f" ({'; '.join(speed_notes)})" if speed_notes else "")

    # skills and saves
    # Jack of All Trades: "half your proficiency bonus, rounded down, to any ability check ... that doesn't already
    # include your proficiency bonus"; Remarkable Athlete: half, rounded up, to Strength, Dexterity or Constitution checks
    joat = prof // 2 if "jack-of-all-trades" in feat_ids else 0
    athlete = (prof + 1) // 2 if "remarkable-athlete" in feat_ids else 0

    def half(ability: str) -> int:
        return joat or (athlete if ability in ("STR", "DEX", "CON") else 0)

    sk_lines = []
    for s in srd.table("Skills").values():
        a = s["ability_score"]["name"]
        bonus = M[a] + (prof * (2 if s["index"] in expertise else 1) if s["index"] in skills else half(a))
        mark = "**" if s["index"] in expertise else "*" if s["index"] in skills else ""
        sk_lines.append(f"{s['name']} {signed(bonus)}{mark}")
    perception = M["WIS"] + (prof * (2 if "perception" in expertise else 1) if "perception" in skills else half("WIS"))
    skill_note = ""
    if joat:
        skill_note += (f" Jack of All Trades: +{joat} (half your proficiency bonus, rounded down) is included in every skill "
                       "you aren't proficient in; add it to any other ability check that doesn't use your proficiency "
                       "bonus (initiative, a plain ability check).")
    if athlete:
        skill_note += (f" Remarkable Athlete: +{athlete} (half your proficiency bonus, rounded up) is included in every "
                       "Strength, Dexterity and Constitution skill you aren't proficient in; add it to any other "
                       "Strength, Dexterity or Constitution check that doesn't use your proficiency bonus (initiative, "
                       "a plain ability check).")
    save_line = ", ".join(f"{a} {signed(M[a] + (prof if a in saves else 0))}{'*' if a in saves else ''}"
                          for a in ABILITIES)

    # attacks
    martial = (cs["martial_arts"]["dice_count"], cs["martial_arts"]["dice_value"]) if "martial-arts" in feat_ids else None
    attacks = [_attack(E[i], M, prof, i in owned_prof, styles, martial) for i in items if E[i].get("weapon_category")]
    unarmed = max(M["STR"], M["DEX"]) if martial else M["STR"]
    attacks.append(f"Unarmed strike: {signed(unarmed + prof)} to hit, " + (
        f"{martial[0]}d{martial[1]}{signed(max(M['STR'], M['DEX']))} bludgeoning (Martial Arts; DEX or STR)" if martial
        else f"{max(0, 1 + M['STR'])} bludgeoning"))  # Damage Rolls: "never negative damage"

    # spellcasting
    spellcasting = None
    slots: dict[str, Any] = {}
    if spells:
        rules = spells["rules"]
        a = rules["ability"]
        dc, atk = 8 + prof + M[a], prof + M[a]
        SP = srd.table("Spells")
        cantrips = [SP[s]["name"] for s in spells["cantrips"]]
        spellcasting = {"ability": a, "save_dc": dc, "attack_bonus": atk, "cantrips": cantrips, "class": c["index"],
                        "max_level": rules["max_level"]}
        for key in ("known", "spellbook", "prepared"):
            if key in spells:
                spellcasting[key] = [SP[s]["name"] for s in spells[key]]
        always = list(rules.get("always_prepared", [])) + spells["signature"]  # Signature Spell: always prepared
        if always:
            spellcasting["always_prepared"] = [SP[s]["name"] for s in always]
        if "prepared" in rules:
            spellcasting["prepare_count"] = rules["prepared"]
            spellcasting["prepare_from"] = "spellbook" if rules["how"] == "spellbook" else "class"
        if spells["secrets"]:
            spellcasting["magical_secrets"] = [SP[s]["name"] for s in spells["secrets"]]  # bard spells for you, any class
        if spells["arcanum"]:
            spellcasting["arcanum"] = {lv: SP[s]["name"] for lv, s in spells["arcanum"].items()}  # spell level: spell
        if spells["tome"]:
            spellcasting["tome_cantrips"] = [SP[s]["name"] for s in spells["tome"]]
        if spells["mastery"]:
            spellcasting["spell_mastery"] = [SP[s]["name"] for s in spells["mastery"]]
        if spells["signature"]:
            spellcasting["signature_spells"] = [SP[s]["name"] for s in spells["signature"]]
        classname = c["name"].lower()
        spellcasting["notes"] = {
            "known": "Spells known are fixed until a level-up." + (
                " Pact Magic: all your spell slots are the same level (the slot level on the sheet); a spell of a lower "
                "level is cast with such a slot, at the slot's level. Your slots come back on a short or long rest."
                if classname == "warlock" else ""),
            "prepared": f"Prepare up to {rules.get('prepared')} spells from the whole {classname} list after a long rest"
                        + (f" ({ALWAYS_PREPARED[c['index']]} spells are always prepared and don't count)."
                           if rules.get("always_prepared") else ".")
                        + ("" if spells.get("prepared") else " None are prepared yet: prepare them when a long rest "
                           "finishes."),
            "spellbook": f"Prepare up to {rules.get('prepared')} spells from the spellbook after a long rest. Ritual Casting: "
                         "a ritual spell in the spellbook can be cast as a ritual (10 minutes longer, no slot), prepared "
                         "or not.",
        }[rules["how"]]
        for lv, n in rules["slots"].items():  # the class table's slots at this level; Pact Magic comes back on a short rest
            slots[lv] = {"max": n, "left": n, "recharge": "short" if c["index"] == "warlock" else "long"}
        every = list(dict.fromkeys(spells["cantrips"] + spells["tome"] + [s for s in spells["secrets"] if SP[s]["level"] == 0]))
        for s in every:
            line = _cantrip(SP[s], dc, atk, N)
            if line:
                attacks.append(line)
    extra_cantrips = []
    for t, (spell_id, a) in RACE_CANTRIPS.items():
        if t in trait_ids:
            extra_cantrips.append(f"{srd.table('Spells')[spell_id]['name']} ({r['name']}, {a})")
    for cid, got in chosen.items():
        if cid == "trait.high-elf-cantrip":
            extra_cantrips += [f"{srd.table('Spells')[g['index']]['name']} (High Elf, INT)" for g in got]
    if extra_cantrips:
        spellcasting = spellcasting or {}
        spellcasting["racial_cantrips"] = extra_cantrips

    # features and counters
    features, resources = [], {}
    for t in p["traits"]:
        if t["index"] in ("darkvision",):
            continue
        features.append(f"{t['name']}: {' '.join(t['desc'])}")
    for cid, got in chosen.items():
        if cid.startswith("trait.draconic-ancestry"):
            for g in got:
                anc = srd.table("Traits")[g["index"]]
                bw = (anc.get("trait_specific") or {}).get("breath_weapon") or {}
                dmg = _at_level(((bw.get("damage") or [{}])[0].get("damage_at_character_level") or {}), N, "2d6")
                area = bw.get("area_of_effect") or {}
                features.append(f"{anc['name']}: breath weapon {area.get('size', '')} ft {area.get('type', '')}, "
                                f"{(bw.get('dc') or {}).get('dc_type', {}).get('name', '')} save DC {8 + M['CON'] + prof}, "
                                f"{dmg} {(anc['trait_specific'].get('damage_type') or {}).get('name', '')} damage "
                                "(half on a success); resistance to that damage type")

    def note(f: dict[str, Any]) -> str:
        """What was chosen for one feature."""
        out = ""
        if got := chosen.get(f"feature.{f['index']}"):
            out += " CHOSEN: " + ", ".join(_grant_name(g) for g in got) + "."
        if f["index"].startswith("favored-enemy-"):
            if (rid := f"feature.{f['index']}.humanoid-races") in picks:
                out += " Humanoid races: " + " and ".join(x.strip() for x in picks[rid]) + "."
            out += " Language learned: " + ", ".join(_grant_name(g) for g in chosen[f"feature.{f['index']}.language"]) + "."
        return out

    families: dict[str, list[dict[str, Any]]] = {}
    for _, f in p["gained"]:
        if not f["index"].startswith("spellcasting-") and not NOT_SHOWN.search(f["index"]):
            families.setdefault(_family(f["index"]), []).append(f)
    for fs in families.values():
        f = fs[-1]  # the newest stage, with the choices made at every stage
        features.append(f"{f['name']}: {' '.join(f['desc'])}" + "".join(note(m) for m in fs)
                        + (_at_this_level(f["index"], cs, N, M, prof) if N > 1 else ""))
    for cid, got in chosen.items():  # the option a choice picked, when its text says more than the feature's
        parent = srd.table("Features").get(cid.removeprefix("feature."))
        for g in got:
            if g.get("kind") == "Features" and (parent is None or srd.table("Features")[g["index"]]["desc"] != parent["desc"]):
                opt = srd.table("Features")[g["index"]]
                features.append(f"{opt['name']}: {' '.join(opt['desc'])}")
    if asi_log:
        features.append("Ability Score Improvements taken: " + "; ".join(asi_log) + ".")
    features.append(f"{b['feature']['name']} ({b['name']}): {' '.join(b['feature']['desc'])}")
    resources.update(_resources(feat_ids, trait_ids, cs, N, M))
    for sp in (spells or {}).get("signature", []):  # "you can cast each of them once at 3rd level without expending a spell slot"
        resources[f"Signature Spell: {srd.table('Spells')[sp]['name']}"] = {"max": 1, "left": 1, "recharge": "short"}

    langs = [x["name"] for x in r["languages"]] + [srd.table("Languages")[g["index"]]["name"]
                                                   for got in chosen.values() for g in got if g.get("kind") == "Languages"]
    if "dragon-ancestor" in feat_ids:  # "You can speak, read, and write Draconic."
        langs.append(srd.table("Languages")["draconic"]["name"])
    other_profs = sorted(P[i]["name"] for i in prof_ids if P[i]["type"] not in ("Skills", "Saving Throws"))
    race_name = sub["name"] if sub else r["name"]
    summary = f"{race_name} {c['name'].lower()} {N}" + (f" ({sc['name']})" if sc else "") + f", {b['name'].lower()} background"
    sheet: dict[str, Any] = {
        "name": name, "summary": summary, "opening": "", "level": N, "race": race_name, "class": c["name"],
        "subclass": sc["name"] if sc else None, "background": b["name"],
        "alignment": ch.get("alignment") or "", "personality": ch.get("personality") or "",
        "appearance": ch.get("appearance") or "",
        "ac": ac, "ac_note": ac_note, "ac_now": None, "speed": speed_note, "size": r["size"],
        "scores": scores,
        "abilities": {a: f"{scores[a]} ({signed(M[a])})" for a in ABILITIES},
        "proficiency_bonus": prof,
        "saving_throws": save_line + " (* proficient)",
        "skills": ", ".join(sk_lines) + " (* proficient, ** expertise)" + skill_note,
        "passive_perception": 10 + perception,
        "senses": "darkvision 60 ft" if "darkvision" in trait_ids else "normal",
        "languages": ", ".join(dict.fromkeys(langs)),
        "proficiencies": ", ".join(other_profs),
        "attacks": attacks, "features": features,
        "hp": {"max": hp, "current": hp, "temp": 0},
        "hit_dice": {"die": f"d{c['hit_die']}", "max": N, "left": N},
        "resources": resources, "conditions": [], "death_saves": {"successes": 0, "failures": 0}, "xp": 0,
        "coins_cp": int(b.get("starting_gold", {}).get("quantity", 0)) * 100,
        "items": {E[i]["name"]: n for i, n in items.items()},
    }
    if spellcasting:
        sheet["spellcasting"] = spellcasting
    if slots:
        sheet["spell_slots"] = slots
    return sheet


def _at_this_level(fid: str, cs: dict[str, Any], N: int, M: dict[str, int], prof: int) -> str:
    """The numbers a feature's text leaves to the class table, at character level N (class_specific in the data)."""
    now = f" At level {N}: "
    if fid == "rage":
        n = cs["rage_count"]
        return (f"{now}rage damage bonus +{cs['rage_damage_bonus']}; "
                + (f"{n} rages" if n < 100 else "unlimited rages") + " before a long rest.")
    if fid == "sneak-attack":
        return f"{now}the extra damage is {cs['sneak_attack']['dice_count']}d{cs['sneak_attack']['dice_value']}."
    if fid == "martial-arts":
        return f"{now}Martial Arts die d{cs['martial_arts']['dice_value']}."
    if fid.startswith("bardic-inspiration"):
        return f"{now}Bardic Inspiration die d{cs['bardic_inspiration_die']}."
    if fid.startswith("song-of-rest"):
        return f"{now}extra 1d{cs['song_of_rest_die']} hit points."
    if fid.startswith("unarmored-movement"):
        return f"{now}speed +{cs['unarmored_movement']} ft."
    if fid == "ki":
        return f"{now}{cs['ki_points']} ki points; ki save DC {8 + prof + M['WIS']}."
    if fid == "font-of-magic":
        return f"{now}{cs['sorcery_points']} sorcery points."
    if fid == "flexible-casting-creating-spell-slots":
        return now + ", ".join(f"a level-{x['spell_slot_level']} slot costs {x['sorcery_point_cost']} points"
                               for x in cs["creating_spell_slots"]) + "."
    if fid == "lay-on-hands":
        return f"{now}a pool of {5 * N} hit points."
    if fid == "aura-of-protection":
        return f"{now}aura range {cs['aura_range']} ft; bonus to saving throws +{max(1, M['CHA'])}."
    if fid in ("aura-of-devotion", "aura-of-courage"):
        return f"{now}aura range {cs['aura_range']} ft."
    if fid == "arcane-recovery":
        return f"{now}recover slots with a combined level of up to {cs['arcane_recovery_levels']}."
    if fid == "natural-recovery":
        return f"{now}recover slots with a combined level of up to {math.ceil(N / 2)}."
    if fid == "second-wind":
        return f"{now}1d10 + {N} hit points."
    if fid == "channel-divinity-preserve-life":
        return f"{now}{5 * N} hit points to divide."
    if fid == "wholeness-of-body":
        return f"{now}{3 * N} hit points."
    if fid.startswith("wild-shape"):
        return f"{now}up to {N // 2} hours in a beast shape."
    if fid == "primal-champion":
        return " Already included in your ability scores."
    return ""


def _resources(feat_ids: set[str], trait_ids: set[str], cs: dict[str, Any], N: int, M: dict[str, int]) -> dict[str, Any]:
    """The counters of everything with limited uses: max and what restores it (from the class table or the feature's text)."""
    res: dict[str, Any] = {}

    def add(name: str, n: int, recharge: str) -> None:
        res[name] = {"max": n, "left": n, "recharge": recharge}

    if "rage" in feat_ids and cs["rage_count"] < 100:  # 20th level: unlimited (the class table)
        add("Rage", cs["rage_count"], "long")
    if any(i.startswith("bardic-inspiration") for i in feat_ids):  # Font of Inspiration: short or long rest
        add("Bardic Inspiration", max(1, M["CHA"]), "short" if "font-of-inspiration" in feat_ids else "long")
    if "second-wind" in feat_ids:
        add("Second Wind", 1, "short")
    if cs.get("action_surges"):
        add("Action Surge", cs["action_surges"], "short")
    if cs.get("indomitable_uses"):
        add("Indomitable", cs["indomitable_uses"], "long")
    if "ki" in feat_ids:
        add("Ki", cs["ki_points"], "short")
    if "wholeness-of-body" in feat_ids:
        add("Wholeness of Body", 1, "long")
    if "font-of-magic" in feat_ids:
        add("Sorcery Points", cs["sorcery_points"], "long")
    if any(i.startswith("channel-divinity-") and i.endswith("-rest") for i in feat_ids):  # cleric
        add("Channel Divinity", cs["channel_divinity_charges"], "short")
    if "channel-divinity" in feat_ids:  # paladin: "You must then finish a short or long rest to use your Channel Divinity again"
        add("Channel Divinity", 1, "short")
    if any(i.startswith("wild-shape") for i in feat_ids) and "archdruid" not in feat_ids:  # Archdruid: unlimited
        add("Wild Shape", 2, "short")
    if "natural-recovery" in feat_ids:
        add("Natural Recovery", 1, "long")
    if "divine-sense" in feat_ids:
        add("Divine Sense", max(0, 1 + M["CHA"]), "long")
    if "lay-on-hands" in feat_ids:
        add("Lay on Hands", 5 * N, "long")
    if "cleansing-touch" in feat_ids:
        add("Cleansing Touch", max(1, M["CHA"]), "long")
    if "stroke-of-luck" in feat_ids:
        add("Stroke of Luck", 1, "short")
    if "dark-ones-own-luck" in feat_ids:
        add("Dark One's Own Luck", 1, "short")
    if "hurl-through-hell" in feat_ids:
        add("Hurl Through Hell", 1, "long")
    if "eldritch-master" in feat_ids:
        add("Eldritch Master", 1, "long")
    for lv in (6, 7, 8, 9):  # one arcanum spell per level, each once per long rest
        if cs.get(f"mystic_arcanum_level_{lv}"):
            add(f"Mystic Arcanum ({lv}th level)", 1, "long")
    if "arcane-recovery" in feat_ids:
        add("Arcane Recovery", 1, "long")
    if "breath-weapon" in trait_ids:
        add("Breath Weapon", 1, "short")
    if "relentless-endurance" in trait_ids:
        add("Relentless Endurance", 1, "long")
    if "infernal-legacy" in trait_ids:  # 3rd level: hellish rebuke once; 5th level: darkness once
        if N >= 3:
            add("Hellish Rebuke (Infernal Legacy)", 1, "long")
        if N >= 5:
            add("Darkness (Infernal Legacy)", 1, "long")
    return res


def _attack(w: dict[str, Any], M: dict[str, int], prof: int, proficient: bool, styles: set[str],
            martial: tuple[int, int] | None) -> str:
    props = [x["index"] for x in w.get("properties", [])]
    ranged = w["weapon_range"] == "Ranged"
    a = M["DEX"] if ranged else M["STR"]
    monk_weapon = bool(martial) and ("monk" in props or w["index"] == "shortsword")
    if "finesse" in props or monk_weapon:
        a = max(M["STR"], M["DEX"])
    hit = a + (prof if proficient else 0) + (2 if ranged and "archery" in styles else 0)
    dice = w["damage"]["damage_dice"] if w.get("damage") else "1"
    dtype = w["damage"]["damage_type"]["name"].lower() if w.get("damage") else ""
    duel = 2 if "dueling" in styles and not ranged and "two-handed" not in props else 0
    line = f"{w['name']}: {signed(hit)} to hit, {dice}{signed(a + duel) if a + duel else ''} {dtype}"
    if duel:
        line += " (Dueling +2 included: one-handed, no other weapon)"
    if w.get("two_handed_damage"):
        line += f"; {w['two_handed_damage']['damage_dice']}{signed(a) if a else ''} two-handed"
    rng = w.get("throw_range") if "thrown" in props else w.get("range") if ranged else None
    if rng:
        line += f"; range {rng['normal']}/{rng.get('long', rng['normal'])}"
    if monk_weapon and martial and w.get("damage") and martial[1] > int(dice.split("d")[-1]):
        # Martial Arts: "You can roll a d4 in place of the normal damage of your unarmed strike or monk weapon"
        line += f"; Martial Arts: you can roll {martial[0]}d{martial[1]} in place of the weapon's damage"
    shown = [x for x in props if x not in ("monk",)]
    if shown:
        line += f" ({', '.join(shown)})"
    if not proficient:
        line += " [not proficient]"
    return line


def _cantrip(s: dict[str, Any], dc: int, atk: int, level: int = 1) -> str:
    """A damage cantrip's line at this character level (damage_at_character_level in the data)."""
    dmg = s.get("damage") or {}
    if isinstance(dmg, list):
        dmg = dmg[0] if dmg else {}
    lvl = _at_level(dmg.get("damage_at_character_level") or {}, level)
    if not lvl:
        return ""
    dtype = (dmg.get("damage_type") or {}).get("name", "").lower()
    if s.get("attack_type"):
        how = f"{signed(atk)} spell attack"
    elif s.get("dc"):
        how = f"{s['dc']['dc_type']['name']} save DC {dc}"
    else:
        how = "automatic"
    beams = ""
    if s["index"] == "eldritch-blast":  # "two beams at 5th level, three beams at 11th level, and four beams at 17th level"
        n = 1 + (level >= 5) + (level >= 11) + (level >= 17)
        beams = f" per beam, {n} beams, each with its own attack roll" if n > 1 else ""
    return f"{s['name']} (cantrip): {how}, {lvl} {dtype}{beams}, range {s['range']}"


def _grant_name(g: dict[str, Any]) -> str:
    if "text" in g:
        return g["text"]
    if "bonus" in g:
        return f"{g['bonus']} +{g['n']}"
    return srd.table(g["kind"])[g["index"]]["name"]


# ---------- what the DM shows the player ----------

METHODS = (f"Ability scores, three ways (from the Player's Handbook; the SRD has no method): "
           f"standard_array = {STANDARD_ARRAY}, one each; point_buy = scores 8-15 bought with {POINTS} points, "
           f"costs {POINT_COST}; rolled = 4d6 drop the lowest, six times (roll_ability_scores, once). "
           "Racial increases come on top.")


def _bonus_text(bonuses: list[dict[str, Any]]) -> str:
    return ", ".join(f"{b['ability_score']['name']} +{b['bonus']}" for b in bonuses)


def options_text(race: str = "", cls: str = "") -> str:
    """Everything the player chooses from. No race or class: the overview. One: its details. Both: every choice."""
    if race and cls:
        p = parts(race, cls)
        lines = [(f"Choices for a {(p['subrace'] or p['race'])['name']} {p['class']['name']} with the "
                  f"{p['background']['name']} background. Put each in build_character's choices under its id."), METHODS]
        r, sub, c, sc, b = p["race"], p["subrace"], p["class"], p["subclass"], p["background"]
        P = srd.table("Proficiencies")
        auto = [x["index"] for x in c["proficiencies"] + (r.get("starting_proficiencies") or []) + b["starting_proficiencies"]]
        auto += [x["index"] for t in p["traits"] for x in t.get("proficiencies", [])]
        auto += SUBCLASS_PROFS.get(sc["index"], []) if sc else []
        lines.append("Comes automatically (no choice needed):")
        lines.append("- Proficiencies: " + ", ".join(dict.fromkeys(P[i]["name"] for i in auto)))
        lines.append(f"- Ability increases: {_bonus_text(r['ability_bonuses'] + (sub['ability_bonuses'] if sub else []))}"
                     f"; speed {r['speed']} ft; languages " + ", ".join(x["name"] for x in r["languages"]))
        lines.append("- Racial traits: " + ", ".join(t["name"] for t in p["traits"]))
        lines.append("- Level-1 features: " + ", ".join(f["name"] for f in p["features"])
                     + (f" (subclass: {sc['name']})" if sc else ""))
        lines.append(f"- {b['name']}: feature {b['feature']['name']}; 15 gp; common clothes, a pouch, vestments, "
                     "5 sticks of incense")
        for cid, what, cs in choices_for(race, cls):
            lines.append(srd.set_text(cs, f"[{cid}] {what}"))
            if cid == f"feature.{ENEMY_FEATURE}":
                lines.append(f"  [{ENEMY_RACES_ID}] only if 'humanoids' is chosen: {ENEMY_RACES_TEXT}")
        sr = spell_rules(race, cls)
        if sr:
            lines.append(f"Spells ({sr['ability']}): cantrips = {sr['cantrips']} from the {sr['class']} cantrips"
                         + (f"; spells = {sr['known']} level-1 spells known" if "known" in sr else "")
                         + (f"; spells = {sr['spellbook']} level-1 wizard spells for the spellbook, prepared = "
                            f"up to INT modifier + 1 of them (the most; minimum of one)" if "spellbook" in sr else "")
                         + ("; prepared = up to WIS modifier + 1 (the most; minimum of one) level-1 spells from the whole list"
                            if sr["how"] == "prepared" else "")
                         + (f"; always prepared: {', '.join(srd.table('Spells')[s]['name'] for s in sr['always_prepared'])}"
                            if sr.get("always_prepared") else ""))
            lines.append("Cantrips: " + ", ".join(s["name"] for s in srd.class_spells(sr["class"], 0)))
            lines.append("Level-1 spells: " + ", ".join(s["name"] + (" (ritual)" if s.get("ritual") else "")
                                                       for s in srd.class_spells(sr["class"], 1, sr["expanded"])))
        b = p["background"]
        for key in ("personality_traits", "ideals", "bonds", "flaws"):
            if b.get(key):
                lines.append(srd.set_text(b[key], f"{b['name']} {key.replace('_', ' ')} (suggestions, optional)"))
        return "\n".join(lines)
    if race:
        r = srd.find("Races", race)
        sub = srd.table("Subraces")[r["subraces"][0]["index"]] if r["subraces"] else None
        lines = [f"{r['name']}: {_bonus_text(r['ability_bonuses'])}; speed {r['speed']} ft; {r['size']}. {r['language_desc']}"]
        if sub:
            lines.append(f"Subrace {sub['name']} (the only one in the SRD): {_bonus_text(sub['ability_bonuses'])}. {sub['desc']}")
        traits = [srd.ref(t) for t in r["traits"]] + ([srd.ref(t) for t in sub["racial_traits"]] if sub else [])
        lines += [f"- {t['name']}: {' '.join(t['desc'])}" for t in traits]
        return "\n".join(lines)
    if cls:
        c = srd.find("Classes", cls)
        lvl = srd.table("Levels")[f"{c['index']}-1"]
        sc = srd.table("Subclasses")[c["subclasses"][0]["index"]]
        lines = [f"{c['name']}: hit die d{c['hit_die']}; saving throws "
                 + ", ".join(x["name"] for x in c["saving_throws"]) + "; proficiencies "
                 + ", ".join(x["name"] for x in c["proficiencies"] if x["index"].split("-")[0] != "saving"),
                 "Level-1 features:"]
        lines += [f"- {srd.ref(f)['name']}: {' '.join(srd.ref(f)['desc'])}" for f in lvl["features"]]
        sc_lvl = srd.table("Levels").get(f"{sc['index']}-1")
        lines.append(f"Subclass (the only one in the SRD): {sc['name']}, "
                     + ("chosen at level 1: " + "; ".join(f"{srd.ref(f)['name']}: {' '.join(srd.ref(f)['desc'])}"
                                                         for f in sc_lvl["features"]) if sc_lvl else "chosen at a later level"))
        return "\n".join(lines)
    lines = ["Races (SRD):"]
    for r in srd.table("Races").values():
        sub = srd.table("Subraces")[r["subraces"][0]["index"]] if r["subraces"] else None
        lines.append(f"- {r['name']}" + (f" ({sub['name']})" if sub else "") + ": "
                     + _bonus_text(r["ability_bonuses"] + (sub["ability_bonuses"] if sub else []))
                     + (" + two others +1 (player's choice)" if r.get("ability_bonus_options") else "")
                     + f"; speed {r['speed']}; " + ", ".join(t["name"] for t in r["traits"]
                                                              + (sub["racial_traits"] if sub else [])))
    lines.append("Classes (SRD):")
    for c in srd.table("Classes").values():
        lines.append(f"- {c['name']}: d{c['hit_die']} hit die; saves "
                     + ", ".join(x["name"] for x in c["saving_throws"])
                     + ("; casts spells from level 1" if c["index"] in CASTING else ""))
    b = srd.table("Backgrounds")[BACKGROUND]
    lines.append(f"Background: {b['name']} (the only one in the SRD): "
                 + ", ".join(srd.short(x["name"]) for x in b["starting_proficiencies"])
                 + f", two extra languages; feature {b['feature']['name']}.")
    lines.append(METHODS)
    return "\n".join(lines)
