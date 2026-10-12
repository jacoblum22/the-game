"""The DM's rules lookup: the exact SRD 5.1 text for a spell, monster, condition, magic item, piece of equipment,
rules section, class feature or racial trait, from the dataset in dm/srd/.

The DM names what it wants. An exact name (case ignored) returns the entry; otherwise the names that contain the
words asked for are listed, so the DM can pick one.
"""

from __future__ import annotations

import re
from typing import Any

from dm import srd

KINDS = {"spell": "Spells", "monster": "Monsters", "condition": "Conditions", "magic_item": "Magic-Items",
         "equipment": "Equipment", "rule": "Rules", "feature": "Features", "trait": "Traits"}
_KIND_OF = {t: k for k, t in KINDS.items()}


def lookup(name: str, kind: str = "") -> str:
    tables = [KINDS[kind]] if kind else list(KINDS.values())
    key = name.strip().casefold()
    if not key:
        return "Give the name of what to look up."
    hits = [(t, x) for t in tables for x in srd.table(t).values() if key in (x["index"], x["name"].casefold())]
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
    """Features with one name and one text: 'Ability Score Improvement (Fighter level 4, 6, 8; Rogue level 4, 10)'."""
    where: dict[str, list[str]] = {}
    for f in fs:
        who = f["class"]["name"] + (f" ({f['subclass']['name']})" if f.get("subclass") else "")
        where.setdefault(who, []).append(str(f["level"]))
    whos = "; ".join(f"{w} level {', '.join(lv)}" for w, lv in where.items())
    return f"FEATURE {fs[0]['name']} ({whos}):\n{_lines(fs[0]['desc'])}"


def _trait(t: dict[str, Any]) -> str:
    who = ", ".join(r["name"] for r in t.get("races", []) + t.get("subraces", []))
    return f"TRAIT {t['name']} ({who}):\n{_lines(t['desc'])}"


def _rule(r: dict[str, Any]) -> str:
    text = f"RULE {r['name']}:\n" + (_lines(r["desc"]) if r.get("desc") else "Sections: " + ", ".join(
        c["name"] for c in r.get("children", [])))
    linked = _step_rules(r)
    if linked:
        text += "\n\nThe rules sections these steps name, in full:\n\n" + "\n\n".join(_rule(x) for x in linked)
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
    "Rules": _rule,
}
