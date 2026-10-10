"""The opening incident as the character knows it and the names a local starts with (12.16.16, 12.10.2).

    start_knowledge(ctx, tx)            # at a character's opening: a local knows the haven's names (I-149)
    incident_line(state)                # the incident's case as data, as the PC knows it (the opening note)

The incident is a reduced case built at seed time (`engine.gen.case`; DL-12-62): its subject, reporter and clues are
generated, never bound at the opening [I-145, I-148; the P-067 binding is retired]. "Who is X?" is the answer
ladder's (engine/dm/answer.py, PR-12-10): a story role from the case graph, any other role by casting.
"""

from __future__ import annotations

from typing import Any

from engine.gen.case import cases
from engine.gen.cast import home_of, settlement_of
from engine.store.events import Event
from engine.world.common import active_pc, fact

# 12.16.11's haven officers a local knows by name (12.10.2, I-149): role words
OFFICERS = ("smith", "innkeeper", "captain", "healer", "herb-wife", "wise", "scribe")


def _incident_case(state: Any) -> dict[str, Any] | None:
    return next((c for c in cases(state).values() if c.get("trigger") == "incident"), None)


def incident_line(state: Any) -> str:  # rule: 12.16.16
    """The incident's case as data, as the PC knows it (12.16.16 "data, not sentences"; DL-12-114): `reporter:` the
    person at the opening place who holds its first clue, and `known:` each necessary node the PC has been told.
    Fields for the opening note only, never a sentence in every scene setting ("X brought the word", retired)."""
    from engine.store.views import display_name

    case = _incident_case(state)
    if case is None:
        return ""
    node1 = case["nodes"][0]
    fields = []
    core = next((p for p in node1["placements"] if p["access"] == "core" and p["holder_kind"] == "person"), None)
    if core and core["holder"] in state.entities and core["holder"] not in state.seals:
        fields.append(f"reporter: {display_name(state, core['holder'])}")
    known = [str(n["fact"]) for n in case["nodes"]
             if n.get("found") and n.get("fact_id") in state.knowledge.get(active_pc(state) or "", {})]
    if known:
        fields.append("known: " + "; ".join(known))
    return "; ".join(fields)


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


__all__ = ["incident_line", "start_knowledge"]
