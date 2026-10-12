"""The DM's rules lookup: the exact SRD 5.1 text for a spell, monster, condition, magic item, piece of equipment,
rules section, class (without its features), class feature or racial trait, from the dataset in dm/srd/.

The DM names what it wants. An exact name (case ignored) returns the entry; failing that, a name that differs only in
apostrophe style, hyphens or a plural "s" does. A name that starts several entries named "Name (...)" returns them all
("Wild Shape"). Otherwise the names that contain the words asked for are listed, so the DM can pick one.
"""

from __future__ import annotations

import re
from typing import Any

from dm import srd

KINDS = {"spell": "Spells", "monster": "Monsters", "condition": "Conditions", "magic_item": "Magic-Items",
         "equipment": "Equipment", "rule": "Rules", "feature": "Features", "trait": "Traits", "class": "Classes"}
_KIND_OF = {t: k for k, t in KINDS.items()} | {"Subclasses": "class"}
_ALSO = {"Classes": ["Subclasses"]}  # a subclass is found along with the classes
# the SRD's name for each subclass (the dataset's is shorter) and the heading of its spell list
_SUBCLASS = {"berserker": ("Path of the Berserker", ""), "lore": ("College of Lore", ""),
             "life": ("Life Domain", "Life Domain Spells"), "land": ("Circle of the Land", "Circle Spells"),
             "champion": ("Champion", ""), "open-hand": ("Way of the Open Hand", ""),
             "devotion": ("Oath of Devotion", "Oath of Devotion Spells"), "hunter": ("Hunter", ""), "thief": ("Thief", ""),
             "draconic": ("Draconic Bloodline", ""), "fiend": ("The Fiend", "Fiend Expanded Spells"),
             "evocation": ("School of Evocation", "")}


def lookup(name: str, kind: str = "") -> str:
    tables = [KINDS[kind]] if kind else list(KINDS.values())
    tables += [s for t in list(tables) for s in _ALSO.get(t, [])]
    key = name.strip().casefold()
    if not key:
        return "Give the name of what to look up."
    hits = _find(tables, key)
    if hits:
        out, features = [], {}
        for t, x in hits:
            if t == "Features":  # the same feature text at several levels or classes is shown once
                features.setdefault(_lines(x["desc"]), []).append(x)
            else:
                out.append(FORMAT[t](x))
        out += [_features(fs) for fs in features.values()]
        return "\n\n".join(out)
    words = key.split()
    near = [f"{x['name']} ({_KIND_OF[t]})" for t in tables for x in srd.table(t).values()
            if all(w in x["name"].casefold() for w in words)]
    # some rules sit inside a larger section (grappling is in Melee Attacks): name the sections whose text has it
    inside = [r["name"] for r in srd.table("Rules").values() if "Rules" in tables
              and all(w in (r.get("desc") or "").casefold() for w in words)]
    out = []
    if near:
        out.append("Names containing it: " + ", ".join(dict.fromkeys(near[:30])))
    if inside:
        out.append("Rules sections whose text mentions it: " + ", ".join(inside[:10]))
    if out:
        return f"No entry named {name!r}. " + " ".join(out)
    return f"No SRD entry named {name!r}" + (f" among {kind}s" if kind else "") + ". It may not be in the SRD."


def _names(t: str, x: dict[str, Any]) -> list[str]:
    return [x["index"], x["name"].casefold()] + ([_SUBCLASS[x["index"]][0].casefold()] if t == "Subclasses" else [])


def _norm(s: str) -> str:
    """Apostrophe style, hyphen or space, and a plural "s" don't matter."""
    s = re.sub(r"[\s-]+", " ", s.casefold().replace("’", "'")).strip()
    return s.removesuffix("s")


def _find(tables: list[str], key: str) -> list[tuple[str, dict[str, Any]]]:
    """The entries an exact name (case ignored) matches, else those it matches under `_norm`; plus the entries named
    "Name (...)" when it is their start. A kind that has an exact entry keeps just that, except features ("Channel
    Divinity" is a Paladin feature and a Cleric one that comes in variants)."""
    every = [(t, x) for t in tables for x in srd.table(t).values()]
    hits = [(t, x) for t, x in every if key in _names(t, x)]
    n = _norm(key)
    if not hits:
        hits = [(t, x) for t, x in every if n in map(_norm, _names(t, x))]
    have = {t for t, _ in hits}
    for t, x in every:
        if ((t not in have or t == "Features") and " (" in x["name"] and _norm(x["name"].split(" (")[0]) == n
                and not any(x is h for _, h in hits)):
            hits.append((t, x))
    return hits


def _lines(x: Any) -> str:
    return "\n".join(x) if isinstance(x, list) else str(x or "")


def _spell(s: dict[str, Any]) -> str:
    lvl = "cantrip" if s["level"] == 0 else f"level {s['level']}"
    comp = ", ".join(s["components"]) + (f" ({s['material']})" if s.get("material") else "")
    tags = [t for t, on in (("ritual", s.get("ritual")), ("concentration", s.get("concentration"))) if on]
    return "\n".join([
        f"SPELL {s['name']}: {lvl} {s['school']['name'].lower()}" + (f" ({', '.join(tags)})" if tags else ""),
        f"Casting time {s['casting_time']}; range {s['range']}; components {comp}; duration {s['duration']}",
        "Classes: " + ", ".join(c["name"] for c in s["classes"]),
        _lines(s["desc"])] + ([f"At higher levels: {_lines(s['higher_level'])}"] if s.get("higher_level") else []))


def _usage(a: dict[str, Any]) -> str:
    u = a.get("usage") or {}
    if u.get("type") == "recharge on roll":
        return f" (recharge {u['min_value']}-6)"
    if u.get("times"):
        return f" ({u['times']}/{u['type'].replace('per ', '')})"
    if u.get("type"):
        return f" ({u['type']})"
    return ""


def _monster(m: dict[str, Any]) -> str:
    mod = lambda v: f"{v} ({(v - 10) // 2:+d})"
    ac = "; ".join(f"{a['value']}" + (f" ({a['type']}" + (": " + ", ".join(x["name"] for x in a["armor"])
                                                         if a.get("armor") else "") + ")" if a["type"] != "dex" else "")
                   for a in m["armor_class"])
    profs = ", ".join(f"{srd.short(p['proficiency']['name'])} +{p['value']}" for p in m.get("proficiencies", []))
    lines = [f"MONSTER {m['name']}: {m['size']} {m['type']}" + (f" ({m['subtype']})" if m.get("subtype") else "")
             + f", {m['alignment']}",
             f"AC {ac}; HP {m['hit_points']} ({m['hit_points_roll']}); speed "
             + ", ".join(f"{k} {v}" for k, v in m["speed"].items()),
             " ".join(f"{a} {mod(m[n])}" for a, n in (("STR", "strength"), ("DEX", "dexterity"), ("CON", "constitution"),
                                                     ("INT", "intelligence"), ("WIS", "wisdom"), ("CHA", "charisma")))]
    if profs:
        lines.append(f"Saves and skills: {profs}")
    for label, key in (("Damage vulnerabilities", "damage_vulnerabilities"), ("Damage resistances", "damage_resistances"),
                       ("Damage immunities", "damage_immunities")):
        if m.get(key):
            lines.append(f"{label}: {', '.join(m[key])}")
    if m.get("condition_immunities"):
        lines.append("Condition immunities: " + ", ".join(c["name"] for c in m["condition_immunities"]))
    lines.append("Senses: " + ", ".join(f"{k.replace('_', ' ')} {v}" for k, v in m["senses"].items())
                 + f"; languages: {m.get('languages') or 'none'}")
    lines.append(f"Challenge {m['challenge_rating']} ({m['xp']} XP); proficiency bonus +{m['proficiency_bonus']}")
    for title, key in (("Traits", "special_abilities"), ("Actions", "actions"), ("Bonus actions", "bonus_actions"),
                       ("Reactions", "reactions"), ("Legendary actions", "legendary_actions")):
        if m.get(key):
            lines.append(f"{title}:")
            lines += [f"- {a['name']}{_usage(a)}: {a['desc']}" for a in m[key]]
    return "\n".join(lines)


def _equipment(e: dict[str, Any]) -> str:
    cost = f"{e['cost']['quantity']} {e['cost']['unit']}" if e.get("cost") else "?"
    lines = [f"EQUIPMENT {e['name']} ({e['equipment_category']['name']}): cost {cost}"
             + (f", weight {e['weight']} lb" if e.get("weight") else "")]
    if e.get("damage"):
        rng = e.get("range") or {}
        lines.append(f"{e['category_range']} weapon: {e['damage']['damage_dice']} {e['damage']['damage_type']['name'].lower()}"
                     + (f", two-handed {e['two_handed_damage']['damage_dice']}" if e.get("two_handed_damage") else "")
                     + (f", range {rng['normal']}/{rng['long']}" if rng.get("long") else "")
                     + "; properties: " + (", ".join(p["name"] for p in e.get("properties", [])) or "none"))
    if e.get("armor_class"):
        ac = e["armor_class"]
        lines.append(f"{e['armor_category']} armor: AC {ac['base']}"
                     + (" + DEX" + (f" (max {ac['max_bonus']})" if ac.get("max_bonus") is not None else "")
                        if ac["dex_bonus"] else "")
                     + (f"; needs STR {e['str_minimum']}" if e.get("str_minimum") else "")
                     + ("; disadvantage on Stealth" if e.get("stealth_disadvantage") else ""))
    if e.get("contents"):
        lines.append("Contains: " + ", ".join(f"{c['quantity']} × {c['item']['name']}" for c in e["contents"]))
    if e.get("desc"):
        lines.append(_lines(e["desc"]))
    return "\n".join(lines)


def _features(fs: list[dict[str, Any]]) -> str:
    """Features with one text: 'Ability Score Improvement (Fighter level 4, 6, 8; Rogue level 4, 10)'. Variants of one
    feature ("Wild Shape (CR 1/4 ...)", "Wild Shape (CR 1/2 ...)") are named one after the other, in level order."""
    where: dict[str, list[str]] = {}
    for f in fs:
        who = f["class"]["name"] + (f" ({f['subclass']['name']})" if f.get("subclass") else "")
        where.setdefault(who, []).append(str(f["level"]))
    whos = "; ".join(f"{w} level {', '.join(lv)}" for w, lv in where.items())
    pre = f"Prerequisite: {', '.join(map(_prereq, fs[0]['prerequisites']))}\n" if fs[0].get("prerequisites") else ""
    return f"FEATURE {' / '.join(dict.fromkeys(f['name'] for f in fs))} ({whos}):\n{pre}{_lines(fs[0]['desc'])}"


def _prereq(p: dict[str, Any]) -> str:
    """An eldritch invocation's prerequisite, as the SRD words it: '15th level', 'Pact of the Chain feature'."""
    if p["type"] == "level":
        return f"{_ord(p['level'])} level"
    x = srd.ref({"index": p[p["type"]].rsplit("/", 1)[1], "url": p[p["type"]]})
    return f"{x['name'].lower()} cantrip" if p["type"] == "spell" else f"{x['name']} feature"  # the only spell is a cantrip


def _ord(n: int) -> str:
    return f"{n}{'th' if n % 100 in (11, 12, 13) else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


# ---------- classes ----------

def _lv(key: str, part: str = "class_specific") -> Any:
    """A column of the class table: that value of the Levels data, a dash when it is 0 or absent."""
    return lambda r: r.get(part, {}).get(key) or "—"


def _dice(key: str) -> Any:
    return lambda r: "{dice_count}d{dice_value}".format(**r["class_specific"][key])


def _pact(slot_level: bool) -> Any:
    """Warlock: the Spell Slots and Slot Level columns (all the slots are of one level)."""
    def col(r: dict[str, Any]) -> str:
        slots = {i: r["spellcasting"][f"spell_slots_level_{i}"] for i in range(1, 10)}
        i = next(i for i, n in slots.items() if n)
        return _ord(i) if slot_level else str(slots[i])
    return col


_SLOTS = lambda top: [(_ord(n), _lv(f"spell_slots_level_{n}", "spellcasting")) for n in range(1, top + 1)]
_CANTRIPS, _KNOWN = ("Cantrips Known", _lv("cantrips_known", "spellcasting")), ("Spells Known", _lv("spells_known", "spellcasting"))
# class -> the columns of its table before and after Features (headings as in the SRD), from the Levels data
_COLS: dict[str, tuple[list[Any], list[Any]]] = {
    "barbarian": ([], [("Rages", lambda r: "Unlimited" if r["class_specific"]["rage_count"] == 9999
                        else r["class_specific"]["rage_count"]),
                       ("Rage Damage", lambda r: f"+{r['class_specific']['rage_damage_bonus']}")]),
    "bard": ([], [_CANTRIPS, _KNOWN, *_SLOTS(9)]), "cleric": ([], [_CANTRIPS, *_SLOTS(9)]),
    "druid": ([], [_CANTRIPS, *_SLOTS(9)]), "fighter": ([], []),
    "monk": ([("Martial Arts", _dice("martial_arts")), ("Ki Points", _lv("ki_points")),
              ("Unarmored Movement", lambda r: f"+{r['class_specific']['unarmored_movement']} ft."
               if r["class_specific"]["unarmored_movement"] else "—")], []),
    "paladin": ([], _SLOTS(5)), "ranger": ([], [_KNOWN, *_SLOTS(5)]), "rogue": ([("Sneak Attack", _dice("sneak_attack"))], []),
    "sorcerer": ([("Sorcery Points", _lv("sorcery_points"))], [_CANTRIPS, _KNOWN, *_SLOTS(9)]),
    "warlock": ([], [_CANTRIPS, _KNOWN, ("Spell Slots", _pact(False)), ("Slot Level", _pact(True)),
                     ("Invocations Known", _lv("invocations_known"))]),
    "wizard": ([], [_CANTRIPS, *_SLOTS(9)]),
}


def _table(c: dict[str, Any]) -> str:
    """The class table: one row per level, the SRD's columns, the features as the dataset names them."""
    pre, post = _COLS[c["index"]]
    cols = [("Proficiency Bonus", lambda r: f"+{r['prof_bonus']}"), *pre,
            ("Features", lambda r: ", ".join(f["name"] for f in r["features"]) or "—"), *post]
    row = lambda *cells: "| " + " | ".join(map(str, cells)) + " |"
    levels = [srd.table("Levels")[f"{c['index']}-{n}"] for n in range(1, 21)]
    return "\n".join([row("Level", *(h for h, _ in cols))] + [row(_ord(r["level"]), *(f(r) for _, f in cols)) for r in levels])


def _spell_list(s: dict[str, Any]) -> str:
    """A subclass's spells by the class level they come at (the Fiend's, as in the SRD's table, by spell level);
    the Circle of the Land's by land."""
    groups: dict[tuple[str, str], list[str]] = {}
    for e in s["spells"]:
        lvl = next(int(p["index"].rsplit("-", 1)[1]) for p in e["prerequisites"] if p["type"] == "level")
        land = next((p["name"].split(": ")[1] for p in e["prerequisites"] if p["type"] == "feature"), "")
        sp = srd.ref(e["spell"])
        label = f"Spell level {_ord(sp['level'])}" if s["class"]["index"] == "warlock" else f"{s['class']['name']} level {lvl}"
        groups.setdefault((land, label), []).append(sp["name"])
    return "\n".join((f"{land} - " if land else "") + f"{label}: {', '.join(names)}" for (land, label), names in groups.items())


def _fill(scope: str, blocks: list[tuple[str, str, str]]) -> list[tuple[str, str, str]]:
    """Add the gap-fill sections of a class or subclass (`for` in dm/srd/gapfill/5e-SRD-Rules.json), each after the
    block its `after` names ("" is the start). A block is (name, heading, text)."""
    for g in srd.table("Rules").values():
        if g.get("for") == scope:
            head = g["name"].split(" (")[0]
            blocks.insert([k for k, _, _ in blocks].index(g["after"]) + 1 if g["after"] else 0, (head, head, g["desc"]))
    return blocks


def _subclass_blocks(s: dict[str, Any]) -> list[tuple[str, str, str]]:
    name, spells = _SUBCLASS[s["index"]]
    return _fill(s["index"], [(name, name, "\n\n".join(s["desc"]))] + ([(spells, spells, _spell_list(s))] if spells else []))


def _blocks(blocks: list[tuple[str, str, str]]) -> str:
    return "\n\n".join(f"{head}:\n{text}" for _, head, text in blocks)


def _subclass(s: dict[str, Any]) -> str:
    first, *rest = _subclass_blocks(s)  # the first block is the subclass's own text
    return "\n\n".join([f"SUBCLASS {first[1]} ({s['class']['name']}: {s['subclass_flavor']}):\n{first[2]}"]
                       + ([_blocks(rest)] if rest else []))


def _class(c: dict[str, Any]) -> str:
    """A class's rules text without its features (the table's Features column names them; each is looked up by name):
    hit points, proficiencies, equipment, the table, spellcasting, the SRD subclass."""
    magic = "Pact Magic" if c["index"] == "warlock" else "Spellcasting"
    blocks = [(f"The {c['name']}", f"The {c['name']}", _table(c))]
    blocks += [(i["name"], f"{magic}: {i['name']}", "\n\n".join(i["desc"])) for i in c.get("spellcasting", {}).get("info", [])]
    for r in c["subclasses"]:
        blocks += _subclass_blocks(srd.table("Subclasses")[r["index"]])
    return f"CLASS {c['name']} (without its features; the table names them, look each one up):\n{_blocks(_fill(c['index'], blocks))}"


def _trait(t: dict[str, Any]) -> str:
    who = ", ".join(r["name"] for r in t.get("races", []) + t.get("subraces", []))
    return f"TRAIT {t['name']} ({who}):\n{_lines(t['desc'])}"


def _rule(r: dict[str, Any], linked: bool = True) -> str:
    """One level only: a section brought in by a procedure's steps comes without its own linked sections, so a
    lookup never recurses or chains (a linked section that is itself a procedure still shows its steps)."""
    text = f"RULE {r['name']}:\n" + (_lines(r["desc"]) if r.get("desc") else "Sections: " + ", ".join(
        c["name"] for c in r.get("children", [])))
    named = _step_rules(r) if linked else []
    if named:
        text += "\n\nThe rules sections these steps name, in full:\n\n" + "\n\n".join(_rule(x, False) for x in named)
    return text


_STEP = re.compile(r"^\s*\d+\.\s+(.+)$", re.MULTILINE)
_SMALL = {"a", "an", "and", "or", "the", "of", "to", "in", "on", "with"}


def _step_rules(r: dict[str, Any]) -> list[dict[str, Any]]:
    """A procedure (a section written as numbered steps) comes with every other rules section a step names, in step
    order, so the rule for each step is in front of the DM when it runs the procedure. A section is named when all
    its words appear in one step ("Determine surprise" names Surprise). Whole chapters (no text of their own) aren't."""
    steps = [s.casefold() for s in _STEP.findall(_lines(r.get("desc")))]
    if not steps:
        return []
    found: list[tuple[int, dict[str, Any]]] = []
    for x in srd.table("Rules").values():
        words = [w for w in re.findall(r"[a-z']+", x["name"].casefold()) if w not in _SMALL]
        # ponytail: a one-word plural name ("Spells", a magic-item section) is a plain noun in step text, so it's skipped
        if not x.get("desc") or x["name"] == r["name"] or not words or (len(words) == 1 and words[0].endswith("s")):
            continue
        at = next((i for i, s in enumerate(steps) if all(re.search(rf"\b{re.escape(w)}\b", s) for w in words)), None)
        if at is not None:
            found.append((at, x))
    return [x for _, x in sorted(found, key=lambda f: f[0])]


FORMAT = {
    "Spells": _spell, "Monsters": _monster, "Equipment": _equipment, "Features": lambda f: _features([f]), "Traits": _trait,
    "Conditions": lambda c: f"CONDITION {c['name']}:\n{_lines(c['desc'])}",
    "Magic-Items": lambda i: f"MAGIC ITEM {i['name']} ({i['rarity']['name']}):\n{_lines(i['desc'])}",
    "Rules": _rule, "Classes": _class, "Subclasses": _subclass,
}
