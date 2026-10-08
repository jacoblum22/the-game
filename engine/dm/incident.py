"""The opening incident as the character knows it, the names a local starts with, and "who is X?" (12.16.16, 12.10.2,
12.3.2).

    start_knowledge(ctx, tx)            # at a character's opening: a local knows the haven's names (I-149)
    incident_line(state)                # the incident's case as the PC knows it (scene setting, opening note)
    who = settle_who(ctx, "who the missing person is")   # (name in words, fact id) or None (not a who-question)

The incident is a reduced case built at seed time (`engine.gen.case`; DL-12-62): its subject, reporter and clues are
generated, never bound at the opening [I-145, I-148; the P-067 binding is retired]. Until the answer ladder
(PR-12-10, spec 008 part B) replaces it, `settle_who` answers a story role from the case behind it (building one on
demand when none is), and any other role by casting (00.11 `cast`), never by a uniform pick.
"""

from __future__ import annotations

import re
from typing import Any

from engine import ids
from engine.audit import text as words
from engine.gen.case import case_covering, case_for_question, cases, mark_found
from engine.gen.cast import base_pool, cast, home_of, settlement_of
from engine.store.events import WORLD, Event
from engine.world.common import active_pc, fact

# "who is X?" with X one of these (stems) is a person-role a roll may settle; any other who-question is the Oracle's
STORY_ROLES = words.content("missing enemy rival challenger stranger thief culprit killer messenger refugee arrival "
                            "behind responsible traitor taken kidnapper attacker")
WHO = re.compile(r"^\W*(?:[^:]{0,40}:\s*)?who(?:'s|\s+(?:is|was|are|were|took|has|had))?\s+(.+)", re.I)
NO_ONE = "no one you know"
# 12.16.11's haven officers a local knows by name (12.10.2, I-149): role words
OFFICERS = ("smith", "innkeeper", "captain", "healer", "herb-wife", "wise", "scribe")


def _people(state: Any, pc: str | None) -> list[str]:
    """The casting gate's exclusions (engine.gen.cast.base_pool); kept under this name for its callers."""
    return base_pool(state, pc)


def _incident_case(state: Any) -> dict[str, Any] | None:
    return next((c for c in cases(state).values() if c.get("trigger") == "incident"), None)


def incident_line(state: Any) -> str:  # rule: 12.16.16
    """The incident's case in words, as the PC knows it: who brought the word (the reporter at the opening place)
    and each necessary node the PC has been told."""
    from engine.store.views import display_name

    case = _incident_case(state)
    if case is None:
        return ""
    node1 = case["nodes"][0]
    sents = []
    for n in case["nodes"]:
        fid = n.get("fact_id")
        if n.get("found") and fid in state.knowledge.get(active_pc(state) or "", {}):
            sents.append(f"{n['fact'][0].upper()}{n['fact'][1:]}.")
    core = next((p for p in node1["placements"] if p["access"] == "core" and p["holder_kind"] == "person"), None)
    if core and core["holder"] in state.entities and core["holder"] not in state.seals:
        sents.append(f"{display_name(state, core['holder'])} brought the word.")
    return " ".join(sents)


def start_knowledge(ctx: Any, tx: Any) -> list[str]:  # rule: 12.10.2
    """I-149 (DL-12-63): a PC whose anchor bond is placed in the haven is a local and starts knowing the names of the
    haven's officers (12.16.11) and of the heads of the factions seated there; an outsider knows none. Writes a
    `name` fact and the PC's knowledge record for each name not yet known. Returns the NPC ids named."""
    from engine.store.views import name_known

    st = tx.state
    pc = active_pc(st)
    haven = (st.meta.get("world.region") or {}).get("haven")
    bond = st.fact_value(pc, "bond.anchor") if pc else None
    if pc is None or haven is None or not bond:
        return []
    anchor = bond.get("npc") if isinstance(bond, dict) else None
    if anchor in st.entities and settlement_of(st, home_of(st, anchor)) != haven:
        return []  # the anchor lives elsewhere: an outsider (a text anchor is placed in the haven, 12.16.11)
    seated = {i for i, e in st.entities.items() if e.kind == "faction" and e.data.get("seat") == haven}
    named = []
    for i, e in st.entities.items():
        if e.kind != "npc" or e.exists != "exists" or i in st.seals or name_known(st, i):
            continue
        role = str(e.data.get("role") or "").lower()
        local = settlement_of(st, home_of(st, i)) == haven
        officer = any(w in role for w in OFFICERS) and (local or "wise" in role)
        head = role.startswith("head of") and bool(seated & set(e.data.get("member_of") or []))
        if not (officer or head):
            continue
        ev = fact(tx, i, "name", e.name, rule_id="12.10.2", source="data", visibility="shown")
        tx.add(ev)
        tx.add(Event.of("knowledge_recorded", source="engine", rule_id="12.10.2", knower=pc,
                        fact_id=ev.payload.fact_id, how="recalled"))  # type: ignore[attr-defined]
        named.append(i)
    return named


def settle_who(ctx: Any, text: str, *, asked: bool = False, exclude: tuple[str, ...] = ()) -> tuple[str, str] | None:
    # rule: 12.3.2
    """"Who is X?": a stored `who_is_*` fact answers it; else a story role is answered from the reduced case behind it
    (built now when none is, PR-15-6), and any other role (a Talk's, `asked`) by casting, else "no one you know".
    Anything else (not a who-question, not a person-role, a sealed fact): None, and the caller's Oracle asks it.
    `exclude` (the one answering) is never the answer."""
    m = WHO.match(text.replace("_", " "))
    if not m:
        return None
    role = m.group(1).strip(" ?.")
    tx = ctx.need_tx()
    st = tx.state
    for f in st.facts.values():
        if (f.subject == WORLD and f.predicate.startswith("who_is_") and f.visibility != "sealed"
                and f.id not in st.seals and st.current_fact_id(WORLD, f.predicate) == f.id
                and words.covers(f.predicate[7:].replace("_", " "), role)):
            return _name(st, f.value), f.id
    story = bool(words.content(role) & STORY_ROLES)
    if asked:
        if not words.content(role) or any((f.visibility == "sealed" or f.id in st.seals)
                                          and words.covers(f.predicate.replace("_", " "), role)
                                          for f in st.facts.values()):
            return None
    elif not story:
        return None
    pc = active_pc(st)
    here = home_of(st, pc) if pc in st.entities else None
    case = case_covering(st, role) or (case_for_question(tx, role, here) if story else None)
    if case is not None and case["solution"]["subject"]["id"] not in exclude:
        sub = case["solution"]["subject"]
        who: Any = sub["id"] if sub["id"] in st.entities else sub["words"]
        ev = fact(tx, WORLD, "who_is_" + ids.slug(role)[:50], who, rule_id="PR-15-6", visibility="shown")
        tx.add(ev)
        fid = ev.payload.fact_id  # type: ignore[attr-defined]
        mark_found(tx, case["id"], case["nodes"][0]["id"], fact_id=fid)
        return _name(st, who), fid
    who = cast(st, role, scope=here, exclude=exclude, gate=not story) or NO_ONE
    ev = fact(tx, WORLD, "who_is_" + ids.slug(role)[:50], who, rule_id="00.11.1", visibility="shown")
    tx.add(ev)
    return _name(st, who), ev.payload.fact_id  # type: ignore[attr-defined]


def _name(state: Any, v: Any) -> str:
    """The answer in words: a person's own name (being told who they are is how the PC learns it, 12.10.2)."""
    return state.entities[v].name if isinstance(v, str) and v in state.entities else str(v)


__all__ = ["NO_ONE", "incident_line", "settle_who", "start_knowledge"]
