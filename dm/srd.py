"""The 2014 SRD 5.1 data: 5e-bits 5e-database, pinned copy in dm/srd/ (see dm/srd/SOURCE.md).

Choices in the data are option sets ({"choose": n, "from": ...}). `set_text` shows one with lettered options and
`resolve` checks a selection against it. A selection is a list of `choose` entries; each entry names an option by
its letter or its exact name (case ignored), or is {"option": <letter or name>, "picks": [...]} when the option
contains a further choice (for example "a martial weapon and a shield": picks = ["Longsword"]).
"""

from __future__ import annotations

import json
from functools import cache
from pathlib import Path
from typing import Any

DIR = Path(__file__).parent / "srd"
LETTERS = "abcdefghijklmnopqrstuvwxyz"
_TABLE = {"equipment": "Equipment", "equipment-categories": "Equipment-Categories", "proficiencies": "Proficiencies",
          "spells": "Spells", "traits": "Traits", "features": "Features", "skills": "Skills", "languages": "Languages",
          "ability-scores": "Ability-Scores", "races": "Races", "subraces": "Subraces", "classes": "Classes",
          "subclasses": "Subclasses", "magic-items": "Magic-Items"}


class Bad(Exception):
    """A selection the data doesn't allow; the message says what is allowed."""


@cache
def table(name: str) -> dict[str, dict[str, Any]]:
    out = {x["index"]: x for x in json.loads((DIR / f"5e-SRD-{name}.json").read_text(encoding="utf-8"))}
    gap = DIR / "gapfill" / f"5e-SRD-{name}.json"  # sections the dataset lacks, typed from the SRD (see SOURCE.md)
    if gap.exists():
        for x in json.loads(gap.read_text(encoding="utf-8")):
            if x["index"] in out:
                raise ValueError(f"gap-fill {name} entry {x['index']!r} is already in the dataset")
            out[x["index"]] = x
    return out


def find(name: str, s: str) -> dict[str, Any]:
    """An entry by its index or exact name (case ignored)."""
    t, key = table(name), str(s or "").strip().casefold()
    for x in t.values():
        if key in (x["index"], x["name"].casefold(), short(x["name"]).casefold()):
            return x
    raise Bad(f"no {name.lower().rstrip('s')} {s!r}; choose from: {', '.join(x['name'] for x in t.values())}")


def short(name: str) -> str:
    """'Skill: Athletics' -> 'Athletics', 'Fighting Style: Defense' -> 'Defense'."""
    return name.split(": ", 1)[-1]


def ref(r: dict[str, Any]) -> dict[str, Any]:
    """The data entry a {"index", "url"} reference points to."""
    kind = r["url"].split("/")[3]
    return table(_TABLE[kind])[r["index"]]


def ref_kind(r: dict[str, Any]) -> str:
    return _TABLE[r["url"].split("/")[3]]


# ---------- option sets ----------

def opt_label(o: Any) -> str:
    if isinstance(o, str):
        return o
    t = o["option_type"]
    if t == "reference":
        return o["item"]["name"]
    if t == "counted_reference":
        return f"{o['count']} × {o['of']['name']}" if o["count"] > 1 else o["of"]["name"]
    if t == "multiple":
        return " + ".join(opt_label(i) for i in o["items"])
    if t == "choice":
        c = o["choice"]
        return f"[choose {c['choose']}: {c.get('desc') or _from_label(c['from'])}]"
    if t == "ability_bonus":
        return f"{o['ability_score']['name']} +{o['bonus']}"
    if t == "string":
        return o["string"]
    if t == "ideal":
        return o["desc"]
    return t


def _from_label(f: dict[str, Any]) -> str:
    if f["option_set_type"] == "equipment_category":
        return f"any {f['equipment_category']['name']}"
    if f["option_set_type"] == "resource_list":
        return "any language"
    return " / ".join(opt_label(o) for o in f["options"])


def set_text(cs: dict[str, Any], title: str = "") -> str:
    f = cs["from"]
    head = f"{title}{': ' if title else ''}choose {cs['choose']}" + (f" ({cs['desc']})" if cs.get("desc") else "")
    if f["option_set_type"] == "options_array":
        return head + "\n" + "\n".join(f"  {LETTERS[i]}) {opt_label(o)}" for i, o in enumerate(f["options"]))
    if f["option_set_type"] == "equipment_category":
        cat = table("Equipment-Categories")[f["equipment_category"]["index"]]
        return head + f" from {cat['name']}: " + ", ".join(e["name"] for e in cat["equipment"])
    return head + " from: " + ", ".join(x["name"] for x in table("Languages").values())


def resolve(cs: dict[str, Any], sel: Any, where: str) -> list[dict[str, Any]]:
    """Check a selection against an option set. Returns what it grants, as a list of
    {"kind": table, "index", "count"} | {"bonus": ability, "n"} | {"text": str}. Raises Bad."""
    if isinstance(sel, (str, dict)):
        sel = [sel]
    if not isinstance(sel, list) or len(sel) != cs["choose"]:
        raise Bad(f"{where}: choose exactly {cs['choose']} (got {len(sel) if isinstance(sel, list) else 0})")
    f, out = cs["from"], []
    if f["option_set_type"] == "options_array":
        seen = set()
        for e in sel:
            name, picks = (e.get("option"), e.get("picks") or []) if isinstance(e, dict) else (e, [])
            i = _option_index(f["options"], str(name), where)
            if i in seen:
                raise Bad(f"{where}: {opt_label(f['options'][i])!r} chosen twice")
            seen.add(i)
            rest = list(picks)
            out += _grant(f["options"][i], rest, where)
            if rest:
                raise Bad(f"{where}: unused picks {rest} for {opt_label(f['options'][i])!r}")
        return out
    if f["option_set_type"] == "equipment_category":
        cat = table("Equipment-Categories")[f["equipment_category"]["index"]]
        for e in sel:
            item = _in_list(cat["equipment"], e, f"{where} ({cat['name']})")
            out.append({"kind": "Equipment", "index": item["index"], "count": 1})
        return out
    names = [x for x in table("Languages").values()]
    if len({str(e).casefold() for e in sel}) != len(sel):
        raise Bad(f"{where}: the same language chosen twice")
    for e in sel:
        lang = _in_list(names, e, f"{where} (languages)")
        out.append({"kind": "Languages", "index": lang["index"], "count": 1})
    return out


def _grant(o: Any, picks: list[Any], where: str) -> list[dict[str, Any]]:
    if isinstance(o, str):
        return [{"text": o}]
    t = o["option_type"]
    if t == "reference":
        return [{"kind": ref_kind(o["item"]), "index": o["item"]["index"], "count": 1}]
    if t == "counted_reference":
        return [{"kind": ref_kind(o["of"]), "index": o["of"]["index"], "count": o["count"]}]
    if t == "multiple":
        return [g for i in o["items"] for g in _grant(i, picks, where)]
    if t == "choice":
        c = o["choice"]
        take = [picks.pop(0) for _ in range(min(c["choose"], len(picks)))]
        return resolve(c, take, where + f" > {c.get('desc') or 'choice'}")
    if t == "ability_bonus":
        return [{"bonus": o["ability_score"]["name"], "n": o["bonus"]}]
    return [{"text": opt_label(o)}]


def _option_index(options: list[Any], name: str, where: str) -> int:
    key = name.strip().casefold()
    if len(key) == 1 and key in LETTERS[:len(options)]:
        return LETTERS.index(key)
    for i, o in enumerate(options):
        names = {opt_label(o).casefold(), short(opt_label(o)).casefold()}
        if isinstance(o, dict) and o.get("option_type") == "reference":
            names.add(o["item"]["index"])
        if key in names:
            return i
    raise Bad(f"{where}: no option {name!r}; options: " + "; ".join(f"{LETTERS[i]}) {opt_label(o)}"
                                                                    for i, o in enumerate(options)))


def _in_list(entries: list[dict[str, Any]], e: Any, where: str) -> dict[str, Any]:
    key = str(e).strip().casefold()
    for x in entries:
        if key in (x["index"], x["name"].casefold()):
            return x
    raise Bad(f"{where}: no {e!r}; choose from: {', '.join(x['name'] for x in entries)}")


# ---------- spells ----------

def class_spells(cls: str, level: int, extra: list[str] | None = None) -> list[dict[str, Any]]:
    """Spells of one level on a class's list, plus `extra` spell indexes (a subclass's expanded list)."""
    return [s for s in table("Spells").values() if s["level"] == level
            and (any(c["index"] == cls for c in s["classes"]) or s["index"] in (extra or []))]


def spell(name: str) -> dict[str, Any]:
    return find("Spells", name)
