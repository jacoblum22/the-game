"""The codex (P7; 00.6.4): the player's opt-in reference to their own character, read from the codex view only.

Only `shown` and `available` state appears; nothing sealed or background, ever. Sections (contracts/cli.md):

    codex(state)                       # the sheet
    codex(state, "abilities")          # also: conditions, journal, threads
    codex(state, "rules 01.7.1")       # a rule card by id (engine/build cards)
"""

from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel, Field

from engine.dm.player_text import second_person
from engine.store.projection import WorldState
from engine.store.views import codex_view
from engine.text.render import slug_words

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
    # a `holder` fact (what a take or give wrote, 01.2.7) wins over a kit item's data `owner`
    moved = {f["subject"] for f in cv["facts"].values() if f["predicate"] == "holder"}
    for e in cv["entities"].values():
        if e["kind"] not in ("item", "object") or e.get("exists", "exists") != "exists" or e["id"] in moved:
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


def hurt_line(state: WorldState, rules: Any = None) -> str:  # rule: 07.1.1
    """'How hurt am I?': the sheet's descriptor, Vitality and conditions in one line (P-101)."""
    from engine.harm.state import descriptor

    cv = codex_view(state)
    pc = _pc(state, cv)
    if pc is None:
        return ""
    vit = cv["quantities"].get(pc, {}).get("vitality")
    conds = " · ".join(f"{c['name']} ({c['severity']})" for c in _conditions(state, cv, pc, rules)) or "none"
    return (f"You are {descriptor(state, pc)}" + (f": Vitality {_qty(vit)}" if vit else "")
            + f". Conditions: {conds}.")


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
    """A fact value in words: a record's own words (`form`, `text`, `name`), a list joined, yes/no, else as is."""
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, dict):
        for key in ("form", "text", "name", "value"):
            if v.get(key):
                return str(v[key]).rstrip(".")
        return ", ".join(str(x) for x in v.values() if isinstance(x, str | int | float))
    if isinstance(v, list | tuple):
        return ", ".join(_value_words(x) for x in v)
    return str(v)


NOT_KNOWLEDGE = ("trg.", "link.", "pref.")
QUALIFIERS = (".but", ".and")  # an Oracle twist's qualifier rides on its answer's fact
HOW_SAID = {"seen": "", "rumor": " (a rumour: true or not, you cannot say)"}
STOP = {"the", "this", "that", "these", "those", "about", "so", "far", "already", "yet", "know", "what", "with",
        "and", "any", "anything", "who", "them", "him", "her", "it", "its", "of", "a", "an", "my", "our"}
# "what do I know about this place and what's going on here?" names nothing: it asks for the summary (live 029: the
# explorer got "Nothing on record about this place...")
GENERAL = {"place", "here", "there", "going", "aroun", "every", "happe", "thing", "situa", "town", "area", "local",
           "nearb", "world", "story"}  # stems (five letters)


def _known(state: WorldState, cv: dict[str, Any], pc: str | None) -> list[dict[str, Any]]:  # rule: 12.10.5
    """What the PC has learned, oldest first: their knowledge records (any `how`, rumours included) and the shown
    facts about the world the player has been told in play (narrated, or answered by the Oracle: `how` "seen").
    Codex view only, so nothing sealed or background; facts about the PC are the sheet's."""
    from engine.audit.fallback import fact_sentence
    from engine.dm.oof import short_text
    from engine.world.chronicle import PREFIX

    facts = cv["facts"]
    recs = state.knowledge.get(pc or "", {}) or {}
    seen = {fid for fid, f in facts.items() if f["visibility"] == "shown" and f["subject"] not in (pc, "world")}
    out: list[dict[str, Any]] = []
    at: dict[tuple[str, str], int] = {}
    for fid in sorted(set(recs) | seen, key=lambda i: state.facts[i].valid_from_seq if i in state.facts else 0):
        f = facts.get(fid)
        if (f is None or f["predicate"].startswith((*NOT_KNOWLEDGE, PREFIX))
                or f["predicate"].endswith(QUALIFIERS) or f["predicate"] == "name"):  # learned name: 12.10.2
            continue
        subj = cv["entities"].get(f["subject"], {}).get("name") if f["subject"] != "world" else "the world"
        if subj is None:  # about something the codex does not show
            continue
        ent = state.entities.get(f["subject"])
        if ent is not None and ent.kind == "thread":
            subj = short_text(ent.data.get("text") or subj)
        what = "a lead" if f["predicate"].startswith("lead.") else slug_words(f["predicate"])
        k = recs.get(fid)
        line = fact_sentence(state, state.facts[fid], subject=subj if f["subject"] != "world" else "")
        if not line:  # a settled question that reads as no statement ('coin named none yet: yes') is left out
            continue
        at[(f["subject"], f["predicate"])] = len(out)  # a later answer to the same thing replaces the earlier one
        out.append({"fact_id": fid, "subject": f["subject"], "about": subj, "what": what.strip(),
                    "value": f["value"], "how": k.how if k else "seen", "sentence": line})
    keep = set(at.values())
    return [k for i, k in enumerate(out) if i in keep]


def _known_line(k: dict[str, Any]) -> str:
    how = HOW_SAID.get(k["how"], f" ({k['how']})")
    return second_person(k["sentence"].rstrip(".") + how + ".")


def _stems(text: str) -> set[str]:
    return {w[:5] for w in re.findall(r"[a-z']+", text.lower().replace("'s", "")) if len(w) > 2 and w not in STOP}


def _self_lines(cv: dict[str, Any], pc: str, rules: Any) -> list[str]:
    """Who the PC is, as they know it: origin (a free Recall of what that life teaches, 12.10.5), drive, bond,
    aim and hooks (their creation answers)."""
    from engine.dm.oof import short_text

    mine: dict[str, Any] = {}
    for f in sorted((f for f in cv["facts"].values() if f["subject"] == pc), key=lambda f: f.get("valid_from_seq", 0)):
        mine[f["predicate"]] = f["value"]
    out = []
    origin = ("origin.livelihood", "origin.upbringing", "origin.people")
    life = [_name(rules, str(mine[k])) for k in origin if mine.get(k)]
    if life:
        out.append("Your life before this: " + " · ".join(life) + " (what that life teaches, you know)")
    if mine.get("drive"):
        out.append(f"What drives you: {_value_words(mine['drive'])}")
    bond = mine.get("bond.anchor")
    if isinstance(bond, dict) and bond.get("npc"):
        who = cv["entities"].get(str(bond["npc"]), {}).get("name") or ""
        if who:
            out.append(f"Who matters to you: {who}" + (f" ({bond['kind']})" if bond.get("kind") else ""))
    if mine.get("aspiration"):
        out.append(f"What you hope for: {_value_words(mine['aspiration'])}")
    hooks = mine.get("hooks")
    if isinstance(hooks, list) and hooks:
        out.append("Ties: " + "; ".join(second_person(short_text(str(h).split(": ", 1)[-1])) for h in hooks[:2]))
    return out


def _about(state: WorldState, ents: dict[str, Any], about: str, want: set[str]) -> tuple[list[str], bool]:
    # rule: 14.6.3
    """Who or what `about` names, among the entities the codex shows: through the alias index (full names win; a
    lone given or family name only when one person carries it), else the entities whose name and role hold every
    word asked ("the mill"), so "Joss Fenn" does not list Joss Dunmere and Pell Fenn."""
    from engine.retrieve.scene import resolve_names

    named = [i for i in resolve_names(state, about) if i in ents]
    if named:
        return named[:3], True
    return [i for i, e in ents.items() if want <= _stems(f"{e['name']} {e['data'].get('role') or ''}")][:3], False


PROMISE = re.compile(r"\bwhat (?:did|have) (?:i|we) (?:\w+ )?(?:promised?|sworn?|swore|vowed?|owe)\b"
                     r"|\bwhat (?:do|did) i owe\b|\bmy (?:promises|oaths|vows)\b", re.I)


def promise_question(text: str) -> bool:
    """"What did I promise X?" (and owe, swear, vow): answered from stored commitments (15.7.6), not narrated."""
    return bool(PROMISE.search(text))


def promise_subject(text: str) -> str | None:
    """X in "what did I promise (to) X?", else None (every open promise)."""
    m = re.search(r"\b(?:promised?|sworn?|swore|vowed?|owe)\s+(?:to\s+)?(.+)", text, re.I)
    x = m.group(1).split("?")[0].strip(" .!,;:'\"") if m else ""
    return None if not x or x.lower() in ("anyone", "anybody", "them", "so far") else x


def promises(state: WorldState, about: str | None = None, rules: Any = None) -> CodexView:  # rule: 15.7.6
    # rule: 14.6.3
    """The PC's open commitments (15.7.6), those involving `about` when it names someone (alias index), as stored:
    the promise's words and whom it was made to. Codex view only."""
    cv = codex_view(state)
    pc = _pc(state, cv)
    ents = {i: e for i, e in cv["entities"].items() if i != pc}
    who = _about(state, ents, about, _stems(about))[0] if about else []
    rows = []
    for f in sorted((f for f in cv["facts"].values() if f["kind"] == "commitment"), key=lambda f: f["valid_from_seq"]):
        val = f["value"] if isinstance(f["value"], dict) else {"act": f["value"]}
        if val.get("status", "open") != "open" or val.get("by", "pc") != "pc":  # the PC's own obligations
            continue
        party = {f["subject"], *(str(v) for v in val.values() if isinstance(v, str))}
        if about and not party & set(who):  # asked about someone: only theirs (nobody resolved: none)
            continue
        to = next((cv["entities"][i]["name"] for i in (f["subject"], val.get("npc"))
                   if isinstance(i, str) and i in cv["entities"] and i != pc), "")
        rows.append(_value_words(val.get("act") or f["value"]) + (f" (to {to})" if to else ""))
    if not rows:
        whom = cv["entities"][who[0]]["name"] if who else about
        return CodexView(section="journal", data={"about": about, "promises": []}, text=(
            f"[JOURNAL] No open promise on record{f' to {whom}' if whom else ''}."))
    head = f"What you promised {cv['entities'][who[0]]['name']}:" if who else "Your open promises:"
    return CodexView(section="journal", text="\n".join([f"[JOURNAL] {head}", *(f"  You promised {r}." for r in rows)]),
                     data={"about": about, "promises": rows, "entities": who})


_SPLIT = re.compile(r"\s*(?:,|;|&|\band\b)\s*", re.I)


def _pieces(state: WorldState, about: str) -> list[str]:  # rule: 15.9.16
    """"X and Y" is two questions. A name that is itself one entity's full name ("Hall and Keep") is kept whole."""
    from engine.retrieve.scene import resolve_names

    have = _stems(about)
    for i in resolve_names(state, about):
        e = state.entities.get(i)
        if e is not None and have and have <= _stems(e.name):
            return [about]
    parts = [p.strip(" .!?'\"") for p in _SPLIT.split(about)]
    return [p for p in parts if _stems(p)] or [about]


def _fits(want: set[str], have: set[str]) -> bool:
    """A piece of the question is about a text when it shares its words: one for a one-word piece, else two."""
    return bool(want) and len(want & have) >= min(2, len(want))


def _entity_lines(ents: dict[str, Any], hits: list[str], named: bool, known: list[dict[str, Any]], want: set[str],
                  cv: dict[str, Any], pc: str, rules: Any) -> list[str]:
    """What the codex shows of the entities a piece names, then the known facts about them (or, for a piece naming no
    entity, the known facts that share its words), then what the PC's own life says of them."""
    from engine.dm.oof import short_text

    lines: list[str] = []
    for e in (ents[i] for i in hits):
        if e["kind"] == "thread":  # a thread's name is its text cut at 60 characters: show the whole sentence
            lines.append(second_person(short_text(str(e["data"].get("text") or e["name"]), 160)) + ".")
            continue
        role, desc = e["data"].get("role"), _value_words(e["data"].get("desc") or "")
        lines.append(e["name"] + (f" ({role})" if isinstance(role, str) and role else "") +
                     (f": {desc}" if desc and desc.lower() != e["name"].lower() else ""))
    lines += [_known_line(k) for k in known  # a named person: what is known about them, not every word match
              if k["subject"] in hits or (not named and _fits(want, _stems(f"{k['what']} {_value_words(k['value'])}")))
              ][-12:]
    lines += [x for x in _self_lines(cv, pc, rules) if any(ents[i]["name"] in x for i in hits)]
    return lines


def _thread_lines(ents: dict[str, Any], want: set[str], hits: list[str]) -> list[str]:
    """Threads (the wound, a situation, a lead) whose **text** shares the words asked; a thread is matched by what it
    says, not by its name (which is its text cut at 60 characters)."""
    from engine.dm.oof import short_text

    return [second_person(short_text(str(e["data"].get("text") or e["name"]), 160)) + "."
            for i, e in ents.items() if e["kind"] == "thread" and i not in hits
            and _fits(want, _stems(str(e["data"].get("text") or "")))]


def _told(state: WorldState, pc: str | None) -> list[dict[str, Any]]:  # rule: 15.9.16
    """The `said` records spoken to the PC (what people said, not what is true): everyone's but the PC's own."""
    from engine.dm.testimony import records

    return [r for r in records(state) if r.get("words") and r.get("speaker") in state.entities
            and r.get("speaker") != pc]


def _told_about(state: WorldState, said: list[dict[str, Any]], hits: list[str], want: set[str]) -> list[dict[str, Any]]:
    """Said records on a piece of the question: about a named entity, spoken by one, or sharing its words."""
    return [r for r in said if set(r.get("about") or []) & set(hits) or r.get("speaker") in hits
            or _fits(want, _stems(str(r["words"])))]


def _told_lines(state: WorldState, told: list[dict[str, Any]]) -> list[str]:  # rule: 15.9.16
    """"What you were told", each line attributed to who said it (and where, when it was noted); testimony, never
    settled as fact (DL-12-102)."""
    from engine.dm.oof import short_text
    from engine.store.views import display_name

    if not told:
        return []
    out = ["What you were told (what people said; whether it is true, you cannot say):"]
    for r in told:
        at = state.entities.get(r.get("place") or "")
        day = r.get("day")
        when = f"day {day[1]} of week {day[0]}" if isinstance(day, list) and len(day) >= 2 else ""
        where = f" ({', '.join(x for x in ((f'at {at.name}' if at is not None else ''), when) if x)})" \
            if at is not None or when else ""
        out.append(f"  {display_name(state, r['speaker'])} told you: \"{short_text(str(r['words']), 220)}\"{where}")
    return [f"  {x}" for x in out]


def what_you_know(state: WorldState, about: str | None = None, rules: Any = None) -> CodexView:  # rule: 14.6.3
    # rule: 15.9.16
    """"What do I know (about X)?" (14.6.3, 12.5.10): the journal filtered to X; with no X, a short summary of who
    the PC is, the land any local knows, leads and rumours, and the people met. Codex view only: nothing sealed,
    background or unlearned. Nothing known says so, and how to find out (ask, look, or Recall, 01.18.6)."""
    from engine.world.places import location

    cv = codex_view(state)
    pc = _pc(state, cv)
    if pc is None:
        return CodexView(section="journal", text="[JOURNAL] No character yet.")
    known = _known(state, cv, pc)
    ents = {i: e for i, e in cv["entities"].items() if i != pc}
    want = _stems(about or "")
    if about and want and not want <= {"mysel", "me", "chara"} | GENERAL:
        # 15.9.16 (DL-15-46): the lookup searches thread text, said records and knowledge records, never names alone;
        # "X and Y" is split, and a name that resolves does not stop the search (round 8: the winter and the banners)
        lines: list[str] = []
        told: list[dict[str, Any]] = []
        hit_ids: list[str] = []
        said = _told(state, pc)
        for piece in _pieces(state, about):
            pw = _stems(piece)
            hits, named = _about(state, ents, piece, pw)
            hit_ids += [h for h in hits if h not in hit_ids]
            new = _entity_lines(ents, hits, named, known, pw, cv, pc, rules) + _thread_lines(ents, pw, hits)
            lines += [x for x in new if x not in lines]
            told += [r for r in _told_about(state, said, hits, pw) if r not in told]
        if not lines and not told:
            return CodexView(section="journal", data={"about": about, "known": []}, text=(
                f"[JOURNAL] Nothing on record about {about}: your character doesn't know anything about that yet. "
                "To find out, ask someone who might know, go and look, or say you try to remember (a Recall roll, "
                "for what your upbringing or trade would have taught you)."))
        body = [f"  {x}" for x in lines] + _told_lines(state, told[-8:])
        return CodexView(section="journal", text="\n".join([f"[JOURNAL] What you know about {about}:"] + body),
                         data={"about": about, "entities": hit_ids, "told": [r["id"] for r in told[-8:]]})
    lines = _self_lines(cv, pc, rules)
    here = location(state)
    home = state.entities[here].data.get("settlement_scope") if here in state.entities else None
    for i, e in ents.items():
        if e["kind"] == "place" and e["data"].get("desc") and (e["data"].get("place_kind") == "region" or i == home):
            lines.append(f"{e['name']}: {_value_words(e['data']['desc'])} (as anyone here knows)")
    lines += [_known_line(k) for k in known if k["how"] != "seen"][-6:]
    met = [e["name"] for i, e in ents.items() if e["kind"] in ("npc", "companion") and e["visibility"] == "shown"
           and not e.get("name_unknown")  # 12.10.2: met means introduced; strangers seen are not listed
           and (any(k["subject"] == i for k in known) or e["data"].get("name_known") is False)]
    if met:
        lines.append("People you have met: " + ", ".join(met[-8:]))
    lines.append('Ask "what do I know about <someone or something>?" for the details, or type "journal" for '
                 "everything you have noted.")
    told = _told(state, pc)[-4:]
    return CodexView(section="journal", text="\n".join(["[JOURNAL] What you know:"] + [f"  {x}" for x in lines]
                                                       + _told_lines(state, told)),
                     data={"known": known, "told": [r["id"] for r in told]})


def journal(state: WorldState, rules: Any = None, limit: int = 30) -> CodexView:  # rule: 11.12.4
    # rule: 00.6.4
    """The chronicle (player-facing entries) and what the character has learned (recorded knowledge of shown or
    available facts)."""
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
    known = _known(state, cv, pc)
    lines = ["[JOURNAL]"]
    lines += [f"  {e['time']}: {e['text']}" for e in entries[-limit:]]
    if known:
        lines.append("  Known:")
        lines += [f"    {_known_line(k)}" for k in known[-limit:]]
    told = _told(state, pc)[-limit:]
    lines += _told_lines(state, told)
    if len(lines) == 1:
        lines.append("  nothing yet")
    return CodexView(section="journal", text="\n".join(lines),
                     data={"chronicle": entries, "known": known, "told": [r["id"] for r in told]})


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
        lines.append(second_person(f"  {t['name']} [{t['status']}]{flag}{text}"))
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


__all__ = ["SECTIONS", "CodexView", "abilities", "codex", "conditions", "journal", "rule_card", "sheet", "threads",
           "what_you_know"]
