"""Build a level-1 character sheet from choices, by the 2014 SRD rules and data (dm/srd.py).

`choices_for(race, class)` lists every choice the character needs, each with an id. `build(...)` checks a full set
of choices and works out the sheet in the same format as dm/characters/*.json, or returns every problem at once.
The DM model talks the player through the choices; this code only checks them and does the arithmetic.
"""

from __future__ import annotations

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
SPELLBOOK_SIZE = 6  # wizard: six 1st-level wizard spells
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

def parts(race: str, cls: str) -> dict[str, Any]:
    r = srd.find("Races", race)
    c = srd.find("Classes", cls)
    sub = srd.table("Subraces")[r["subraces"][0]["index"]] if r["subraces"] else None
    sc = srd.table("Subclasses")[c["subclasses"][0]["index"]]
    lvl = srd.table("Levels")[f"{c['index']}-1"]
    sc_lvl = srd.table("Levels").get(f"{sc['index']}-1")  # only subclasses chosen at level 1 have one
    traits = [srd.ref(t) for t in r["traits"]] + ([srd.ref(t) for t in sub["racial_traits"]] if sub else [])
    feats = [srd.ref(f) for f in lvl["features"]] + ([srd.ref(f) for f in sc_lvl["features"]] if sc_lvl else [])
    return {"race": r, "subrace": sub, "class": c, "subclass": sc if sc_lvl else None, "level": lvl,
            "traits": traits, "features": feats, "background": srd.table("Backgrounds")[BACKGROUND]}


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
        for cs in (f.get("feature_specific") or {}).values():
            if isinstance(cs, dict) and "choose" in cs:
                out.append((f"feature.{f['index']}", f["name"], cs))
        if f["index"] == ENEMY_FEATURE:
            out.append((ENEMY_LANGUAGE_ID, f"{f['name']} language", _enemy_language()))
    for i, cs in enumerate(c["starting_equipment_options"], 1):
        out.append((f"class.equipment.{i}", f"{c['name']} equipment", cs))
    if b.get("language_options"):
        out.append(("background.languages", f"{b['name']} languages", b["language_options"]))
    for i, cs in enumerate(b["starting_equipment_options"], 1):
        out.append((f"background.equipment.{i}", f"{b['name']} equipment", cs))
    if b["index"] == "acolyte":
        out.append(("background.equipment.prayer", f"{b['name']} equipment", ACOLYTE_PRAYER))
    return out


def spell_rules(race: str, cls: str, scores: dict[str, int] | None = None) -> dict[str, Any] | None:
    p = parts(race, cls)
    c = p["class"]["index"]
    if c not in CASTING:
        return None
    sc = p["level"].get("spellcasting") or {}
    ability, how = CASTING[c]
    extra = [s["spell"]["index"] for s in (p["subclass"] or {}).get("spells", [])
             if any(q["index"] == f"{c}-1" for q in s["prerequisites"])]
    rules: dict[str, Any] = {"ability": ability, "how": how, "cantrips": sc.get("cantrips_known", 0), "class": c}
    if how == "known":
        rules["known"] = sc.get("spells_known", 0)
    if how == "spellbook":
        rules["spellbook"] = SPELLBOOK_SIZE
    if how in ("prepared", "spellbook") and scores:
        rules["prepared"] = max(1, mod(scores[ability]) + 1)
    if p["subclass"] and p["subclass"]["index"] == "life":
        rules["always_prepared"] = extra  # domain spells: always prepared, not counted
        extra = []
    rules["expanded"] = extra  # e.g. the Fiend's expanded spell list
    return rules


# ---------- building ----------

def build(ch: dict[str, Any], rolled: list[int] | None = None) -> tuple[dict[str, Any] | None, list[str]]:
    """Returns (sheet, []) or (None, problems)."""
    errs: list[str] = []
    try:
        p = parts(ch.get("race", ""), ch.get("class", ""))
    except Bad as e:
        return None, [str(e)]
    r, sub, c, sc, b = p["race"], p["subrace"], p["class"], p["subclass"], p["background"]
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
    picks = ch.get("choices") or {}
    granted: list[dict[str, Any]] = []
    chosen: dict[str, list[dict[str, Any]]] = {}
    sets = choices_for(r["index"], c["index"])
    for cid, what, cs in sets:
        if cid not in picks:
            errs.append(f"choices.{cid}: missing ({what}, {srd.set_text(cs).splitlines()[0]})")
            continue
        try:
            got = srd.resolve(cs, picks[cid], f"choices.{cid}")
        except Bad as e:
            errs.append(str(e))
            continue
        chosen[cid] = got
        granted += got
    allowed_ids = {cid for cid, _, _ in sets}
    if any(g.get("text") == "humanoids" for g in chosen.get(f"feature.{ENEMY_FEATURE}", [])):
        allowed_ids.add(ENEMY_RACES_ID)  # 'select two races of humanoid'
        races = picks.get(ENEMY_RACES_ID)
        if (not isinstance(races, list) or len(races) != 2 or not all(isinstance(x, str) and x.strip() for x in races)
                or races[0].strip().casefold() == races[1].strip().casefold()):
            errs.append(f"choices.{ENEMY_RACES_ID}: missing or wrong ({ENEMY_RACES_TEXT})")
    extra_ids = set(picks) - allowed_ids
    if extra_ids:
        errs.append(f"choices: not needed for this character: {', '.join(sorted(extra_ids))}")

    # racial increases
    bonuses = [{"bonus": x["ability_score"]["name"], "n": x["bonus"]}
               for x in r["ability_bonuses"] + (sub["ability_bonuses"] if sub else [])]
    bonuses += [g for g in granted if "bonus" in g]
    if scores:
        for x in bonuses:
            scores[x["bonus"]] += x["n"]
    M = {a: mod(scores.get(a, 10)) for a in ABILITIES}
    prof = 2

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
    expertise: set[str] = set()
    for cid, got in chosen.items():
        if cid.startswith("feature.") and "expertise" in cid:
            for g in got:
                ref = P[g["index"]]["reference"]["index"] if g.get("kind") == "Proficiencies" else ""
                if g["index"] not in prof_ids:
                    errs.append(f"choices.{cid}: expertise needs a proficiency the character has ({P[g['index']]['name']})")
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

    # spells
    spells = _spells(ch, r["index"], c["index"], scores, chosen, errs)

    if errs:
        return None, errs
    sheet = _sheet(ch, name, p, scores, M, prof, prof_ids, skills, saves, expertise, items, chosen, spells)
    if b["index"] == "acolyte":  # items the dataset lacks are kept by name
        named = Counter(ACOLYTE_ITEMS) + Counter(g["text"] for g in chosen["background.equipment.prayer"])
        for n, q in named.items():
            sheet["items"][n] = sheet["items"].get(n, 0) + q
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


def _spells(ch: dict[str, Any], race: str, cls: str, scores: dict[str, int], chosen: dict[str, Any],
            errs: list[str]) -> dict[str, Any] | None:
    rules = spell_rules(race, cls, scores or None)
    given = {k: ch.get(k) for k in ("cantrips", "spells", "prepared") if ch.get(k)}
    if not rules:
        if given:
            errs.append(f"{', '.join(given)}: a level-1 {cls} has no spells")
        return None

    def check(key: str, names: Any, n: int, level: int, pool: list[str] | None = None, atmost: bool = False) -> list[str]:
        if not isinstance(names, list) or not (1 <= len(names) <= n if atmost else len(names) == n):
            errs.append(f"{key}: choose " + (f"1 to {n} (the most you can prepare)" if atmost else f"exactly {n}"))
            return []
        allowed = pool if pool is not None else [s["index"] for s in srd.class_spells(cls, level, rules["expanded"])]
        out = []
        for nm in names:
            try:
                s = srd.spell(nm)
            except Bad:
                errs.append(f"{key}: no SRD spell {nm!r}")
                continue
            if s["index"] not in allowed:
                errs.append(f"{key}: {s['name']} is not a level-{level} {cls} spell"
                            + (" in the spellbook" if pool is not None else ""))
            out.append(s["index"])
        if len(set(out)) != len(out):
            errs.append(f"{key}: a spell is listed twice")
        return out

    out: dict[str, Any] = {"rules": rules, "cantrips": check("cantrips", ch.get("cantrips"), rules["cantrips"], 0)}
    if rules["how"] == "known":
        out["known"] = check("spells", ch.get("spells"), rules["known"], 1)
    elif rules["how"] == "spellbook":
        out["spellbook"] = check("spells", ch.get("spells"), rules["spellbook"], 1)
        if "prepared" in rules:
            out["prepared"] = check("prepared", ch.get("prepared"), rules["prepared"], 1, out["spellbook"], atmost=True)
    elif "prepared" in rules:
        if ch.get("spells"):
            errs.append(f"spells: a {cls} prepares spells from the whole class list; use prepared")
        out["prepared"] = check("prepared", ch.get("prepared"), rules["prepared"], 1, atmost=True)
    return out


def _sheet(ch: dict[str, Any], name: str, p: dict[str, Any], scores: dict[str, int], M: dict[str, int], prof: int,
           prof_ids: set[str], skills: set[str], saves: set[str], expertise: set[str], items: Counter[str],
           chosen: dict[str, Any], spells: dict[str, Any] | None) -> dict[str, Any]:
    r, sub, c, sc, b, lvl = p["race"], p["subrace"], p["class"], p["subclass"], p["background"], p["level"]
    E, P = srd.table("Equipment"), srd.table("Proficiencies")
    trait_ids = {t["index"] for t in p["traits"]}
    feat_ids = {f["index"] for f in p["features"]}
    style = next((srd.table("Features")[g["index"]] for cid, got in chosen.items()
                  if cid == "feature.fighter-fighting-style" for g in got), None)
    style_id = style["index"].removeprefix("fighter-fighting-style-") if style else ""

    owned_prof = _owned_prof(prof_ids)

    # hit points
    hp = c["hit_die"] + M["CON"] + (1 if "dwarven-toughness" in trait_ids else 0) + (1 if "draconic-resilience" in feat_ids else 0)

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
    scored = [(v + (2 if shield and ok else 0) + (1 if style_id == "defense" and "no armor" not in n and "Unarmored" not in n
                                                    and "Resilience" not in n else 0), n, ok) for v, n, ok in options]
    ac, ac_note, ok = max(scored, key=lambda x: (x[0], not x[1].startswith("no armor")))  # a tie names the feature
    if shield and ok:
        ac_note += " + shield 2"
    if style_id == "defense" and armors and any(a["name"] in ac_note for a in armors):
        ac_note += " + Defense 1"
    speed = r["speed"]
    speed_note = f"{speed} ft"
    worn = next((a for a in armors if a["name"] in ac_note), None)
    if worn and worn.get("str_minimum", 0) > scores["STR"]:
        if r["index"] == "dwarf":
            speed_note += " (not reduced by heavy armor)"
        else:
            speed_note = f"{speed - 10} ft (heavy armor without STR {worn['str_minimum']})"
    if worn and worn.get("stealth_disadvantage"):
        ac_note += "; disadvantage on Stealth"

    # skills and saves
    sk_lines = []
    for s in srd.table("Skills").values():
        a = s["ability_score"]["name"]
        bonus = M[a] + (prof * (2 if s["index"] in expertise else 1) if s["index"] in skills else 0)
        mark = "**" if s["index"] in expertise else "*" if s["index"] in skills else ""
        sk_lines.append(f"{s['name']} {signed(bonus)}{mark}")
    perception = M["WIS"] + (prof * (2 if "perception" in expertise else 1) if "perception" in skills else 0)
    save_line = ", ".join(f"{a} {signed(M[a] + (prof if a in saves else 0))}{'*' if a in saves else ''}"
                          for a in ABILITIES)

    # attacks
    attacks = [_attack(E[i], M, prof, i in owned_prof, style_id, "martial-arts" in feat_ids) for i in items
               if E[i].get("weapon_category")]
    unarmed = max(M["STR"], M["DEX"]) if "martial-arts" in feat_ids else M["STR"]
    attacks.append(f"Unarmed strike: {signed(unarmed + prof)} to hit, " + (
        f"1d4{signed(max(M['STR'], M['DEX']))} bludgeoning (Martial Arts; DEX or STR)" if "martial-arts" in feat_ids
        else f"{max(0, 1 + M['STR'])} bludgeoning"))  # Damage Rolls: "never negative damage"

    # spellcasting
    spellcasting = None
    slots: dict[str, Any] = {}
    if spells:
        rules = spells["rules"]
        a = rules["ability"]
        dc, atk = 8 + prof + M[a], prof + M[a]
        cantrips = [srd.table("Spells")[s]["name"] for s in spells["cantrips"]]
        spellcasting = {"ability": a, "save_dc": dc, "attack_bonus": atk, "cantrips": cantrips, "class": c["index"],
                        "max_level": 1}
        for key in ("known", "spellbook", "prepared"):
            if key in spells:
                spellcasting[key] = [srd.table("Spells")[s]["name"] for s in spells[key]]
        if rules.get("always_prepared"):
            spellcasting["always_prepared"] = [srd.table("Spells")[s]["name"] for s in rules["always_prepared"]]
        if "prepared" in rules:
            spellcasting["prepare_count"] = rules["prepared"]
            spellcasting["prepare_from"] = "spellbook" if rules["how"] == "spellbook" else "class"
        spellcasting["notes"] = {
            "known": "Spells known are fixed until a level-up.",
            "prepared": f"Prepare up to {rules.get('prepared')} spells from the whole {c['name'].lower()} list after a long rest"
                        + (" (domain spells are always prepared and don't count)." if rules.get("always_prepared") else "."),
            "spellbook": f"Prepare up to {rules.get('prepared')} spells from the spellbook after a long rest. Ritual Casting: "
                         "a ritual spell in the spellbook can be cast as a ritual (10 minutes longer, no slot), prepared "
                         "or not.",
        }[rules["how"]]
        n = (lvl.get("spellcasting") or {}).get("spell_slots_level_1", 0)
        if n:
            slots["1"] = {"max": n, "left": n, "recharge": "short" if c["index"] == "warlock" else "long"}
        for s in spells["cantrips"]:
            line = _cantrip(srd.table("Spells")[s], dc, atk)
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
                dmg = ((bw.get("damage") or [{}])[0].get("damage_at_character_level") or {}).get("1", "2d6")
                area = bw.get("area_of_effect") or {}
                features.append(f"{anc['name']}: breath weapon {area.get('size', '')} ft {area.get('type', '')}, "
                                f"{(bw.get('dc') or {}).get('dc_type', {}).get('name', '')} save DC {8 + M['CON'] + prof}, "
                                f"{dmg} {(anc['trait_specific'].get('damage_type') or {}).get('name', '')} damage "
                                "(half on a success); resistance to that damage type")
    for f in p["features"]:
        if f["index"].startswith("spellcasting-"):
            continue
        line = f"{f['name']}: {' '.join(f['desc'])}"
        for cid, got in chosen.items():
            if cid == f"feature.{f['index']}":
                line += " CHOSEN: " + ", ".join(_grant_name(g) for g in got) + "."
        if f["index"] == ENEMY_FEATURE:
            if ENEMY_RACES_ID in (ch.get("choices") or {}):
                line += " Humanoid races: " + " and ".join(x.strip() for x in ch["choices"][ENEMY_RACES_ID]) + "."
            line += " Language learned: " + ", ".join(_grant_name(g) for g in chosen[ENEMY_LANGUAGE_ID]) + "."
        features.append(line)
    if style:
        features.append(f"{style['name']}: {' '.join(style['desc'])}")
    features.append(f"{b['feature']['name']} ({b['name']}): {' '.join(b['feature']['desc'])}")
    cs = lvl.get("class_specific") or {}
    if "rage" in feat_ids:
        resources["Rage"] = {"max": cs.get("rage_count", 2), "left": cs.get("rage_count", 2), "recharge": "long"}
    if any(i.startswith("bardic-inspiration") for i in feat_ids):
        n = max(1, M["CHA"])
        resources["Bardic Inspiration"] = {"max": n, "left": n, "recharge": "long"}
    if "second-wind" in feat_ids:
        resources["Second Wind"] = {"max": 1, "left": 1, "recharge": "short"}
    if "divine-sense" in feat_ids:
        n = max(0, 1 + M["CHA"])
        resources["Divine Sense"] = {"max": n, "left": n, "recharge": "long"}
    if "lay-on-hands" in feat_ids:
        resources["Lay on Hands"] = {"max": 5, "left": 5, "recharge": "long"}
    if "arcane-recovery" in feat_ids:
        resources["Arcane Recovery"] = {"max": 1, "left": 1, "recharge": "long"}
    if "breath-weapon" in trait_ids:
        resources["Breath Weapon"] = {"max": 1, "left": 1, "recharge": "short"}
    if "relentless-endurance" in trait_ids:
        resources["Relentless Endurance"] = {"max": 1, "left": 1, "recharge": "long"}

    langs = [x["name"] for x in r["languages"]] + [srd.table("Languages")[g["index"]]["name"]
                                                   for got in chosen.values() for g in got if g.get("kind") == "Languages"]
    if "dragon-ancestor" in feat_ids:  # "You can speak, read, and write Draconic."
        langs.append(srd.table("Languages")["draconic"]["name"])
    other_profs = sorted(P[i]["name"] for i in prof_ids if P[i]["type"] not in ("Skills", "Saving Throws"))
    race_name = sub["name"] if sub else r["name"]
    summary = f"{race_name} {c['name'].lower()} 1" + (f" ({sc['name']})" if sc else "") + f", {b['name'].lower()} background"
    sheet: dict[str, Any] = {
        "name": name, "summary": summary, "opening": "", "level": 1, "race": race_name, "class": c["name"],
        "subclass": sc["name"] if sc else None, "background": b["name"],
        "alignment": ch.get("alignment") or "", "personality": ch.get("personality") or "",
        "appearance": ch.get("appearance") or "",
        "ac": ac, "ac_note": ac_note, "ac_now": None, "speed": speed_note, "size": r["size"],
        "scores": scores,
        "abilities": {a: f"{scores[a]} ({signed(M[a])})" for a in ABILITIES},
        "proficiency_bonus": prof,
        "saving_throws": save_line + " (* proficient)",
        "skills": ", ".join(sk_lines) + " (* proficient, ** expertise)",
        "passive_perception": 10 + perception,
        "senses": "darkvision 60 ft" if "darkvision" in trait_ids else "normal",
        "languages": ", ".join(dict.fromkeys(langs)),
        "proficiencies": ", ".join(other_profs),
        "attacks": attacks, "features": features,
        "hp": {"max": hp, "current": hp, "temp": 0},
        "hit_dice": {"die": f"d{c['hit_die']}", "max": 1, "left": 1},
        "resources": resources, "conditions": [], "death_saves": {"successes": 0, "failures": 0}, "xp": 0,
        "coins_cp": int(b.get("starting_gold", {}).get("quantity", 0)) * 100,
        "items": {E[i]["name"]: n for i, n in items.items()},
    }
    if spellcasting:
        sheet["spellcasting"] = spellcasting
    if slots:
        sheet["spell_slots"] = slots
    return sheet


def _attack(w: dict[str, Any], M: dict[str, int], prof: int, proficient: bool, style: str, monk: bool) -> str:
    props = [x["index"] for x in w.get("properties", [])]
    ranged = w["weapon_range"] == "Ranged"
    a = M["DEX"] if ranged else M["STR"]
    if "finesse" in props or (monk and ("monk" in props or w["index"] == "shortsword")):
        a = max(M["STR"], M["DEX"])
    hit = a + (prof if proficient else 0) + (2 if ranged and style == "archery" else 0)
    dice = w["damage"]["damage_dice"] if w.get("damage") else "1"
    dtype = w["damage"]["damage_type"]["name"].lower() if w.get("damage") else ""
    duel = 2 if style == "dueling" and not ranged and "two-handed" not in props else 0
    line = f"{w['name']}: {signed(hit)} to hit, {dice}{signed(a + duel) if a + duel else ''} {dtype}"
    if duel:
        line += " (Dueling +2 included: one-handed, no other weapon)"
    if w.get("two_handed_damage"):
        line += f"; {w['two_handed_damage']['damage_dice']}{signed(a) if a else ''} two-handed"
    rng = w.get("throw_range") if "thrown" in props else w.get("range") if ranged else None
    if rng:
        line += f"; range {rng['normal']}/{rng.get('long', rng['normal'])}"
    shown = [x for x in props if x not in ("monk",)]
    if shown:
        line += f" ({', '.join(shown)})"
    if not proficient:
        line += " [not proficient]"
    return line


def _cantrip(s: dict[str, Any], dc: int, atk: int) -> str:
    dmg = s.get("damage") or {}
    if isinstance(dmg, list):
        dmg = dmg[0] if dmg else {}
    lvl = (dmg.get("damage_at_character_level") or {}).get("1")
    if not lvl:
        return ""
    dtype = (dmg.get("damage_type") or {}).get("name", "").lower()
    if s.get("attack_type"):
        how = f"{signed(atk)} spell attack"
    elif s.get("dc"):
        how = f"{s['dc']['dc_type']['name']} save DC {dc}"
    else:
        how = "automatic"
    return f"{s['name']} (cantrip): {how}, {lvl} {dtype}, range {s['range']}"


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
