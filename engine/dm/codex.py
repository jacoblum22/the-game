"""The codex (P7; 00.6.4): the player's opt-in reference to their own character, read from the codex view only.

Only `shown` and `available` state appears; nothing sealed or background, ever. Sections (contracts/cli.md):

    codex(state)                       # the sheet
    codex(state, "abilities")          # also: conditions, journal, threads
    codex(state, "rules 01.7.1")       # a rule card by id (engine/build cards)
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from engine.store.projection import WorldState
from engine.store.views import codex_view

SECTIONS = ("sheet", "abilities", "conditions", "journal", "threads", "rules")
CORE_QUANTITIES = ("vitality", "focus", "fate", "dread")
HOLDER_KEYS = ("holder", "owner", "carried_by", "held_by")


class CodexView(BaseModel):
    """contracts/engine-api.md `game.codex(...)` result: the text the front end prints and the data it came from."""

    section: str
    text: str
    data: dict[str, Any] = Field(default_factory=dict)


# ------------------------------------------------------------------------------------------- helpers


def _name(rules: Any, data_id: str) -> str:
    from engine.dm.oof import name_of

    return name_of(rules, data_id)


def _entry(rules: Any, data_id: str) -> dict[str, Any]:
    if rules is None:
        return {}
    try:
        return dict(rules.get(data_id)) if rules.has(data_id) else {}
    except (KeyError, AttributeError, TypeError):
        return {}


def _pc(state: WorldState, cv: dict[str, Any]) -> str | None:
    from engine.world.common import active_pc

    pc = active_pc(state)
    return pc if pc in cv["entities"] else None


def _qty(q: dict[str, Any]) -> str:
    return f"{q['current']}/{q['max']}" if q.get("max") is not None else str(q["current"])


def _conditions(state: WorldState, cv: dict[str, Any], pc: str, rules: Any) -> list[dict[str, Any]]:
    out = []
    for c in cv["conditions"].values():
        if c["target"] != pc:
            continue
        d = _entry(rules, c["condition_id"])
        if d.get("visible") is False:  # a condition the bearer cannot perceive is not shown state
            continue
        out.append({"id": c["condition_id"], "name": _name(rules, c["condition_id"]), "severity": c["severity"],
                    "stacks": c.get("stacks", 1), "remaining": c.get("remaining", ""),
                    "about": str(d.get("intent") or "")})
    return out


def _abilities(cv: dict[str, Any], pc: str, rules: Any) -> list[dict[str, Any]]:
    data = cv["entities"][pc]["data"]
    qs = cv["quantities"].get(pc, {})
    out = []
    for ab in data.get("abilities") or []:
        ab_id = ab if isinstance(ab, str) else str(ab.get("id", ""))
        d = _entry(rules, ab_id)
        uses = qs.get(f"uses.{ab_id}")
        cost = d.get("cost") or {}
        ranks = d.get("ranks") or ()
        text = str(ranks[0].get("text", "")) if ranks and isinstance(ranks[0], dict) else str(d.get("scope") or "")
        out.append({"id": ab_id, "name": _name(rules, ab_id), "uses": _qty(uses) if uses else None,
                    "focus": cost.get("focus") if isinstance(cost, dict) else None, "timing": d.get("timing"),
                    "text": text})
    return out


def _inventory(cv: dict[str, Any], pc: str) -> list[str]:
    items = []
    for e in cv["entities"].values():
        if e["kind"] not in ("item", "object") or e.get("exists", "exists") != "exists":
            continue
        if any(e["data"].get(k) == pc for k in HOLDER_KEYS):
            items.append(e["name"])
    for f in cv["facts"].values():  # holder facts on the item (engine/audit claims convention)
        if f["predicate"] in HOLDER_KEYS and f["value"] == pc and f["subject"] in cv["entities"]:
            n = cv["entities"][f["subject"]]["name"]
            if n not in items:
                items.append(n)
    return items


# ------------------------------------------------------------------------------------------- sections


def sheet(state: WorldState, rules: Any = None) -> CodexView:  # rule: 00.6.4
    """The PC's shown and available state: attributes, Vitality, Focus, fate, conditions, licences, abilities with
    uses, inventory."""
    from engine.harm.state import descriptor

    cv = codex_view(state)
    pc = _pc(state, cv)
    if pc is None:
        return CodexView(section="sheet", text="[SHEET] No character yet.")
    e = cv["entities"][pc]
    qs = cv["quantities"].get(pc, {})
    attrs = e["data"].get("attributes") or {}
    lines = [f"[SHEET] {e['name']} — {descriptor(state, pc)}"]
    if attrs:
        lines.append("  Attributes: " + " · ".join(f"{_name(rules, a)} {v:+d}" if isinstance(v, int) else
                                                   f"{_name(rules, a)} {v}" for a, v in attrs.items()))
    core = [f"{n.capitalize() if n != 'fate' else n} {_qty(qs[n])}" for n in CORE_QUANTITIES if n in qs]
    if core:
        lines.append("  " + " · ".join(core))
    other = {n: q for n, q in qs.items() if n not in CORE_QUANTITIES and not n.startswith("uses.")}
    if other:
        lines.append("  Also: " + " · ".join(f"{n.replace('_', ' ')} {_qty(q)}" for n, q in other.items()))
    conds = _conditions(state, cv, pc, rules)
    lines.append("  Conditions: " + (" · ".join(f"{c['name']} ({c['severity']})" for c in conds) or "none"))
    lics = cv["licenses"].get(pc, [])
    if lics:
        lines.append("  Licences: " + " · ".join(f"{_name(rules, x['license_id'])} ({x['grade']})" for x in lics))
    abil = _abilities(cv, pc, rules)
    if abil:
        lines.append("  Abilities: " + " · ".join(a["name"] + (f" (uses {a['uses']})" if a["uses"] else "")
                                                  for a in abil))
    inv = _inventory(cv, pc)
    lines.append("  Carrying: " + (", ".join(inv) or "nothing listed"))
    data = {"pc": pc, "name": e["name"], "attributes": attrs, "quantities": qs, "conditions": conds,
            "licenses": lics, "abilities": abil, "inventory": inv}
    return CodexView(section="sheet", text="\n".join(lines), data=data)


def abilities(state: WorldState, rules: Any = None) -> CodexView:  # rule: 00.6.4
    """Each held ability: name, Focus cost, uses left, timing and its rank text."""
    cv = codex_view(state)
    pc = _pc(state, cv)
    if pc is None:
        return CodexView(section="abilities", text="[ABILITIES] No character yet.")
    abil = _abilities(cv, pc, rules)
    qs = cv["quantities"].get(pc, {})
    lines = ["[ABILITIES]" + (f" Focus {_qty(qs['focus'])}" if "focus" in qs else "")]
    for a in abil:
        price = [f"Focus {a['focus']}" if a["focus"] is not None else "", f"uses {a['uses']}" if a["uses"] else "",
                 str(a["timing"] or "")]
        lines.append(f"  {a['name']} ({' · '.join(p for p in price if p)}): {a['text']}".rstrip(": "))
    if not abil:
        lines.append("  none")
    return CodexView(section="abilities", text="\n".join(lines), data={"abilities": abil})


def conditions(state: WorldState, rules: Any = None) -> CodexView:  # rule: 00.6.4
    """The PC's visible conditions: name, severity, stacks, how long, and what it does."""
    cv = codex_view(state)
    pc = _pc(state, cv)
    conds = _conditions(state, cv, pc, rules) if pc else []
    lines = ["[CONDITIONS]"]
    for c in conds:
        stacks = f" ×{c['stacks']}" if c["stacks"] and c["stacks"] > 1 else ""
        lines.append(f"  {c['name']} ({c['severity']}{stacks}; {c['remaining']}): {c['about']}".rstrip(": "))
    if not conds:
        lines.append("  none")
    return CodexView(section="conditions", text="\n".join(lines), data={"conditions": conds})


def _value_words(v: Any) -> str:
    """A fact value in words: a record's own words (`form`, `text`, `name`), a list joined, else as is."""
    if isinstance(v, dict):
        for key in ("form", "text", "name", "value"):
            if v.get(key):
                return str(v[key]).rstrip(".")
        return ", ".join(str(x) for x in v.values() if isinstance(x, str | int | float))
    if isinstance(v, list | tuple):
        return ", ".join(_value_words(x) for x in v)
    return str(v)


def journal(state: WorldState, rules: Any = None, limit: int = 30) -> CodexView:  # rule: 11.12.4
    # rule: 00.6.4
    """The chronicle (player-facing entries) and what the character has learned (recorded knowledge of shown or
    available facts)."""
    from engine.dm.oof import short_text
    from engine.world.chronicle import PREFIX, chronicle

    cv = codex_view(state)
    pc = _pc(state, cv)
    facts = cv["facts"]
    entries = []
    for e in chronicle(state):
        fid = state.current_fact_id("world", PREFIX + e.id)
        if fid not in facts:
            continue
        if e.scope != "public" and not (pc and (e.scope == pc or (isinstance(e.scope, list) and pc in e.scope))):
            continue
        entries.append({"id": e.id, "time": e.time, "text": e.text})
    known = []
    for fid, k in (state.knowledge.get(pc or "", {}) or {}).items():
        f = facts.get(fid)
        if f is None or f["predicate"].startswith(("trg.", PREFIX)):
            continue
        subj = cv["entities"].get(f["subject"], {}).get("name") if f["subject"] != "world" else "the world"
        if subj is None:  # about something the codex does not show
            continue
        ent = state.entities.get(f["subject"])
        if ent is not None and ent.kind == "thread":
            subj = short_text(ent.data.get("text") or subj)
        what = "a lead" if f["predicate"].startswith("lead.") else f["predicate"].replace("_", " ").replace(".", " ")
        known.append({"fact_id": fid, "about": subj, "what": what, "value": f["value"], "how": k.how})
    lines = ["[JOURNAL]"]
    lines += [f"  {e['time']}: {e['text']}" for e in entries[-limit:]]
    if known:
        lines.append("  Known:")
        lines += [f"    {k['about']}: {k['what']} — {_value_words(k['value'])} ({k['how']})" for k in known[-limit:]]
    if len(lines) == 1:
        lines.append("  nothing yet")
    return CodexView(section="journal", text="\n".join(lines), data={"chronicle": entries, "known": known})


def threads(state: WorldState, rules: Any = None) -> CodexView:  # rule: 12.6.6
    # rule: 00.6.4
    """The thread list as the player may see it (thread entities the codex shows), active first."""
    from engine.world.social import thread_list

    cv = codex_view(state)
    rows = [t for t in thread_list(state) if t["id"] in cv["entities"]]
    rows.sort(key=lambda t: (t["status"] != "active", -t["weight"], t["id"]))
    lines = ["[THREADS]"]
    for t in rows:
        flag = " (stalled)" if t["stalled"] else ""
        text = f" — {t['text']}" if t["text"] and t["text"] != t["name"] else ""
        lines.append(f"  {t['name']} [{t['status']}]{flag}{text}")
    if not rows:
        lines.append("  none")
    data = [{k: t[k] for k in ("id", "name", "text", "status", "stalled")} for t in rows]
    return CodexView(section="threads", text="\n".join(lines), data={"threads": data})


def rule_card(rule_id: str, cards: Any = None) -> CodexView:  # rule: 12.5.10
    """`/rules <id>`: the rule card's body, for the player who wants to read it."""
    from engine.build.compile_cards import load_cards

    idx = cards or load_cards()
    rid = rule_id.strip()
    if not rid or rid not in idx:
        return CodexView(section="rules", text=f"[RULES] No rule card {rid or '(no id given)'}.")
    card = idx.get(rid)
    return CodexView(section="rules", text=f"[RULES] {card.id} {card.title}\n{card.body.strip()}",
                     data={"id": card.id, "title": card.title})


def codex(state: WorldState, section: str | None = None, rules: Any = None, *,
          cards: Any = None) -> CodexView:  # rule: 00.6.4
    """contracts/engine-api.md `game.codex(section)`: `sheet` (default), `abilities`, `conditions`, `journal`,
    `threads`, `rules <id>`. Shown and available state only; never sealed."""
    sec = (section or "sheet").strip().lstrip("/")
    head, _, arg = sec.partition(" ")
    head = head.lower()
    if head == "rules":
        return rule_card(arg, cards)
    fn = {"sheet": sheet, "abilities": abilities, "conditions": conditions, "journal": journal,
          "threads": threads}.get(head)
    if fn is None:
        return CodexView(section=head, text=f"[NOTE] Codex sections: {', '.join(SECTIONS)} (rules <id>).")
    return fn(state, rules)


__all__ = ["SECTIONS", "CodexView", "abilities", "codex", "conditions", "journal", "rule_card", "sheet", "threads"]
