"""The opening incident's subject, bound to a person who already exists (12.16.16; I-145, P-067), and "who is X?"
settled among existing people (12.3.2: roll what settles it; 12.14.13: never a new person by mention).

    bind_incident(ctx, tx)                 # at the first opening: the missing person / challenger / ... = a seed NPC
    who = settle_who(ctx, "who the missing person is")   # (name in words, fact id) or None (not a who-question)

Everything written is a `fact_set` / `knowledge_recorded` / `meta_set` from the engine. What the incident hides
(why they went, what the challenger really is) is not invented here: it stays with the lead's record and the
NPC's own sealed fields.
"""

from __future__ import annotations

import re
from typing import Any

from engine import ids
from engine.audit import text as words
from engine.store.events import WORLD, Event
from engine.world.common import active_pc, fact, meta

INCIDENT = "incident.subject"  # meta {option, role, npc, reporter, witnesses, known: [fact ids the PC knows]}
STREAM = "incident"  # its own rng stream, so no other draw moves

# inciting option -> (the subject's role, who fits: haven | away | rulers | not_here)
SUBJECTS = {
    "missing": ("the missing person", "haven"),
    "refugees": ("the one who came in with the refugees", "away"),
    "duel": ("the challenger", "haven"),
    "dying_messenger": ("the one the dying rider's message is for", "not_here"),
    "offer": ("the one who offers the work", "rulers"),
}

# "who is X?" with X one of these (stems) is a person-role a roll may settle; any other who-question is the Oracle's
STORY_ROLES = words.content("missing enemy rival challenger stranger thief culprit killer messenger refugee arrival "
                            "behind responsible traitor taken kidnapper attacker")
WHO = re.compile(r"^\W*(?:[^:]{0,40}:\s*)?who(?:'s|\s+(?:is|was|are|were|took|has|had))?\s+(.+)", re.I)
NO_ONE = "no one you know"


def _settlement(state: Any, place: str | None) -> str | None:
    seen = set()
    while place and place in state.entities and place not in seen:
        seen.add(place)
        d = state.entities[place].data
        if d.get("place_kind") == "settlement":
            return place
        place = d.get("parent")
    return None


def _people(state: Any, pc: str | None) -> list[str]:
    """Existing NPCs a binding may name: not the PC, not the anchor bond (02.9.2), nothing sealed, no far power."""
    bond = state.fact_value(pc, "bond.anchor") if pc else None
    anchor = bond.get("npc") if isinstance(bond, dict) else None
    return sorted(i for i, e in state.entities.items()
                  if e.kind == "npc" and e.exists == "exists" and i != anchor and i not in state.seals
                  and not e.data.get("power"))


def _home(state: Any, npc: str) -> str | None:
    pos = state.positions.get(npc)
    return (pos.location if pos else None) or state.entities[npc].data.get("home")


def _fits(state: Any, npc: str, how: str, haven: str | None, start: str | None) -> bool:
    home = _home(state, npc)
    d = state.entities[npc].data
    if how == "haven":
        return _settlement(state, home) == haven
    if how == "away":
        return _settlement(state, home) != haven
    if how == "rulers":
        return any(str(f).endswith(".rulers") for f in d.get("member_of") or []) and d.get("depth") == "principal"
    return home != start  # not_here


def bind_incident(ctx: Any, tx: Any) -> dict[str, Any] | None:  # rule: 12.16.16
    """Bind the opening incident's subject to an existing NPC drawn by the seeded rng, write it as facts, give two
    locals partial knowledge (who last saw them, where they were heading), and tell the PC what the reporter
    told them. Returns the binding (also `meta[INCIDENT]`), or None when the incident has no person behind it."""
    st = tx.state
    if st.meta.get(INCIDENT):
        return st.meta[INCIDENT]
    op = st.meta.get("world.opening") or {}
    inc = op.get("inciting") or {}
    spec = SUBJECTS.get(str(inc.get("option") or ""))
    if spec is None:
        return None
    role, how = spec
    pc = active_pc(st)
    start = (op.get("start") or {}).get("place")
    haven = _settlement(st, start)
    people = _people(st, pc)
    fit = [n for n in people if _fits(st, n, how, haven, start)] or [n for n in people if how != "haven"
                                                                     or _settlement(st, _home(st, n)) == haven]
    if not fit:
        return None
    rng = ctx.rng
    who = rng.choice(fit, f"incident subject: {role}", stream=STREAM)
    target = next((ld.get("points_to") for ld in op.get("leads") or [] if isinstance(ld, dict)
                   and str(ld.get("lead", "")).startswith("the incident itself")), None)
    target = target if target in st.entities and st.entities[target].kind == "place" else None
    locals_ = [n for n in people if n != who and _settlement(st, _home(st, n)) == haven]
    picked: list[str] = []
    for purpose in ("reporter", "witness", "witness"):
        pool = [n for n in locals_ if n not in picked]
        if pool:
            picked.append(rng.choice(pool, f"incident {purpose}: {role}", stream=STREAM))
    reporter, witnesses = (picked[0] if picked else None), picked[1:]

    def put(subject: str, predicate: str, value: Any, vis: str = "shown", knowers: tuple[str | None, ...] = ()) -> str:
        ev = fact(tx, subject, predicate, value, rule_id="12.16.16", visibility=vis)
        tx.add(ev)
        fid = ev.payload.fact_id  # type: ignore[attr-defined]
        for k in knowers:
            if k:
                tx.add(Event.of("knowledge_recorded", source="engine", rule_id="12.16.16", knower=k, fact_id=fid,
                                how="told" if k == pc else "witnessed"))
        return fid

    opt = inc["option"]
    known = [put(WORLD, "who_is_" + ids.slug(role.removeprefix("the "))[:50], who, knowers=(pc, reporter))]
    if opt == "missing":
        known.append(put(who, "is_missing", True, knowers=(pc, reporter, *witnesses)))
        home = _home(st, who)
        if home in st.entities and witnesses:  # where they were last seen: the first witness saw it
            put(who, "was_last_seen_at", home, "background", knowers=(witnesses[0],))
        if target and len(witnesses) > 1:  # which way they went: the trail out of the haven (the lead's target)
            put(who, "was_seen_heading_toward", target, "background", knowers=(witnesses[1],))
    elif opt == "refugees":
        known.append(put(who, "is_among_the_refugees", True, knowers=(pc, reporter)))
        if target:
            known.append(put(who, "tells_of", target, knowers=(pc, reporter)))
    elif opt == "duel":
        known.append(put(who, "is_the_challenger", True, knowers=(pc, reporter)))
    elif opt == "dying_messenger":
        known.append(put(who, "is_the_one_the_dying_rider_asked_for", True, knowers=(pc, reporter)))
    elif opt == "offer":
        known.append(put(who, "offers_the_pc_work_and_a_warning", True, knowers=(pc,)))
    rec = {"option": opt, "role": role, "npc": who, "reporter": reporter, "witnesses": witnesses, "known": known}
    tx.add(meta(INCIDENT, rec, "12.16.16"))
    return rec


def incident_line(state: Any) -> str:
    """The incident's subject in words, as the PC knows it (for the opening's record and the scene setting)."""
    from engine.audit.fallback import fact_sentence
    from engine.dm.roles.narrator import name_of

    rec = state.meta.get(INCIDENT) or {}
    pc = active_pc(state)
    sents = [s for fid in rec.get("known") or [] if fid in state.facts
             and fid in state.knowledge.get(pc or "", {})
             and state.current_fact_id(state.facts[fid].subject, state.facts[fid].predicate) == fid
             and (s := fact_sentence(state, state.facts[fid])) and not s.lower().startswith("who ")]
    if rec.get("reporter") and sents:
        sents.append(f"{name_of(state, rec['reporter'])} brought the word.")
    return " ".join(sents)


def settle_who(ctx: Any, text: str) -> tuple[str, str] | None:  # rule: 12.3.2
    """"Who is X?": an existing binding answers it; else, when X is a person-role (STORY_ROLES), one existing NPC is
    rolled among the fitting ones and written (`who_is_<x>`), or "no one you know" when none fits. Anything else
    (not a who-question, not a person-role): None, and the caller's Oracle asks it as before."""
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
    if not words.content(role) & STORY_ROLES:
        return None
    pc = active_pc(st)
    fit = _people(st, pc)
    # ponytail: every existing NPC fits any person-role; filter by faction or standing if picks read as arbitrary
    who = ctx.rng.choice(fit, f"who is {role}", stream=STREAM) if fit else NO_ONE
    ev = fact(tx, WORLD, "who_is_" + ids.slug(role)[:50], who, rule_id="12.3.2", visibility="shown")
    tx.add(ev)
    return _name(st, who), ev.payload.fact_id  # type: ignore[attr-defined]


def _name(state: Any, v: Any) -> str:
    from engine.dm.roles.narrator import name_of

    return name_of(state, v) if isinstance(v, str) and v in state.entities else str(v)


__all__ = ["INCIDENT", "NO_ONE", "bind_incident", "incident_line", "settle_who"]
