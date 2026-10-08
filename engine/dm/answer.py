"""Answering a question (PR-12-10, 12.10.8; spec 008 part B): the answer comes from code at RECORD, before the
draft, never from the narration.

    a = ask(ctx, npc, "where_is", topic, "where does the north road go?", rungs_for(rules, reach), pc=pc)
    a.line      # the record line the narration must say ("Hilde Marsh tells you: ...")
    a.fact_id   # the fact told (or the pointer's fact); the asked-and-answered index keeps it
    who = who_answer(ctx, "who is missing")      # the DM-side "who is X?" (a FICTION_QUESTION): (words, fact id)

Order (PR-12-10): 1. the index `(npc|kind|topic)` (meta `answers.index`); the tier route: "who is <role>" (a story
role -> the case graph, building the reduced case when none is behind it; any other role -> casting), a question
about a case -> the case graph (a holder delivers its placement and the node is found; anyone else names the holder
of the node's core placement), "what do you want" -> the NPC's stance, "who would know" -> the pointer; ordinary
knowledge -> 2. the store (what the NPC knows, their own facts, public facts about what was asked), 3. the knowledge
pack (12.16.11), 4. propose and ratify (`roles/proposer.py`; the Oracle at 12.10.6(d)'s odds), 5. the pointer
(casting: a person, else the topic's place, else a walk-on made there). Depth by reach (`rungs_for`); never empty.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from engine import ids
from engine.audit import text as words
from engine.gen._seed_packs import pack_data, role_key
from engine.gen.case import case_covering, case_for_question, cases, mark_found, pointer, story_option
from engine.gen.cast import alive, cast, home_of, pointer_target, settlement_of
from engine.store.events import WORLD
from engine.world.common import active_pc, fact, meta
from engine.world.social import learn_name, record_knowledge

INDEX = "answers.index"  # meta {"<npc>|<question_kind>|<topic>": {"fact", "said", "pointer"}} (12.10.6(e))
NO_ONE = "no one you know"
# "who is X?" with X one of these (stems) is a story role: the case graph answers it (PR-12-10 step 1)
STORY_ROLES = words.content("missing enemy rival challenger stranger thief culprit killer messenger refugee arrival "
                            "behind responsible traitor taken kidnapper attacker")
_WHO = re.compile(r"\bwho(?:'s|’s|\s+(is|was|are|were|took|has|had|did|sent|would|might|could))?\s+([^?!.;,\"”]+)",
                  re.IGNORECASE)
_SELF = re.compile(r"^(?:you|he|she|they|your(?: own)? name)\b", re.IGNORECASE)  # asked of the one answering
_OWN_NAME = re.compile(r"\b(?:your|his|her|their)(?: own)? name\b", re.IGNORECASE)  # never "the name of X" (P-113)
PEOPLE = ("npc", "companion", "adversary")
# facts that are bookkeeping, not answers (rung 1 never tells them)
_SKIP = ("activity", "voice", "exists", "harm_state", "stance.said", "name")
_SKIP_PREFIX = ("knows_", "points_to.", "trg.", "detail.", "asked_", "who_is_", "case.", "bond.")


@dataclass
class Answer:
    said: str  # the knower's act in words, after their name ("tells you: ...", "does not know ..., but ... would")
    line: str  # the record line (BeatEntry.learned or the NPC's act)
    fact_id: str | None = None
    pointer: str | None = None  # who or where the knower named instead (a pointer answer)


def deliver_count(n: int, reach: int) -> int:  # rule: T-01-6
    """DL-01-12: of N items, Limited max(1, N // 3); Standard ceil(N / 2); Great N (ponytail: no Exceptional bonus)."""
    if n <= 0 or reach <= 0:
        return 0
    return {1: max(1, n // 3), 2: -(-n // 2)}.get(reach, n)


def rungs_for(rules: Any, reach: int) -> list[str]:  # rule: PR-12-10
    """`social.yaml#delivery.information.ladder_depth` (step 6): the rungs a delivered reach runs."""
    depth = rules.social["delivery"]["information"]["ladder_depth"]
    return list(depth.get(max(1, min(4, reach))) or depth[2])


def name(st: Any, eid: str | None) -> str:
    """The entity as the narration may call it (`name_of`), with an article for a description."""
    from engine.dm.roles.narrator import name_of

    if not eid:
        return "someone"
    n = name_of(st, eid)
    return f"the {n}" if n[:1].islower() and not n.startswith(("the ", "a ", "an ", "your ")) else n


def _cap(s: str) -> str:
    return s[:1].upper() + s[1:]


# ------------------------------------------------------------------------------------------- the index


def _key(knower: str, kind: str, topic: str) -> str:
    return f"{knower}|{kind}|{topic}"


def _remember(ctx: Any, key: str, a: Answer) -> Answer:  # rule: 12.10.6
    tx = ctx.need_tx()
    idx = dict(tx.state.meta.get(INDEX) or {})
    idx[key] = {"fact": a.fact_id, "said": a.said, "pointer": a.pointer}
    tx.add(meta(INDEX, idx, "12.10.6"))
    return a


def _tell(ctx: Any, pc: str, fid: str | None, how: str = "told") -> None:
    st = ctx.need_tx().state
    if fid and fid in st.facts and fid not in st.knowledge.get(pc, {}):
        record_knowledge(ctx.time_ctx(), pc, fid, how)


def _write(ctx: Any, subject: str, predicate: str, value: Any, *, rule: str, source: str = "ruling") -> str:
    """The current fact (subject, predicate) when it already holds `value`, else a new one."""
    tx = ctx.need_tx()
    cur = tx.state.current_fact_id(subject, predicate)
    if cur is not None and tx.state.facts[cur].value == value:
        return cur
    ev = fact(tx, subject, predicate, value, rule_id=rule, source=source, visibility="shown")
    tx.add(ev)
    return str(ev.payload.fact_id)  # type: ignore[attr-defined]


# ------------------------------------------------------------------------------------------- topics


def topic_of(st: Any, topic: str | None, text: str, knower: str | None = None) -> tuple[str, str | None]:
    # rule: 12.2.2
    """(topic key, entity asked about). The Reader's topic is an entity id or a closed topic key; an entity resolves
    by `common_knowledge.entity_topics`; a null topic is read from the question's words (names first, then the
    topic keys and gists), else `local_news`."""
    ck = pack_data().CK
    if topic in ck["topics"]:
        return str(topic), None
    about = topic if topic in st.entities and topic != knower else None
    if about is None:
        from engine.retrieve.scene import resolve_names

        have = words.content(text)  # a name word, never a stop word ("who" in "Brugra Who Came Back")
        about = next((i for i in resolve_names(st, text) if i not in (knower, active_pc(st))
                      and have & words.content(st.entities[i].name)), None)
    if about is not None:
        e = st.entities[about]
        haven = (st.meta.get("world.region") or {}).get("haven")
        if e.kind == "place":
            kind = "place_in_settlement" if settlement_of(st, about) == haven else "place_beyond"
        elif e.kind == "object":
            kind = "document" if e.data.get("document") else "item"
        else:
            kind = {"faction": "faction", "adversary": "creature"}.get(e.kind, "npc")
        return str((ck["entity_topics"].get(kind) or ["folk"])[0]), about
    have = words.content(text)
    best, score = "local_news", 0
    for k, t in ck["topics"].items():
        s = len(have & words.content(f"{k.replace('_', ' ')} {t['gist']}"))
        if s > score:
            best, score = str(k), s
    return best, None


def _gist(topic: str, about: str | None, st: Any) -> str:
    return name(st, about) if about else topic.replace("_", " ")


# ------------------------------------------------------------------------------------------- the pointer


def _walk_on(ctx: Any, role: str, topic: str, where: str | None) -> str | None:  # rule: 12.11.1
    """`#cast.empty_pool.who_would_know`'s last resort: a walk-on with the role made at the settlement."""
    from engine.gen._seed_packs import walk_on
    from engine.gen.case import world_rec, write_seeded

    tx = ctx.need_tx()
    reg = world_rec(tx.state)
    if not where or not reg["names"]:
        return None
    seed = (tx.state.meta.get("world.seed") or {}).get("seed")
    n = walk_on(reg, seed, f"ptr_{topic}_{where}", role, where)
    write_seeded(tx, reg, source="engine")
    return str(n["id"]) if n["id"] in tx.state.entities else None


def point(ctx: Any, knower: str, topic: str, pc: str, *, about: str | None = None) -> tuple[str, str]:
    # rule: PR-12-10
    """Step 5: who would know `topic`, by casting (never the first person present, never one the narration made up):
    a person, else the topic's place, else a walk-on made there. Anyone who already sent the PC to `knower` on this
    topic is not sent back to (DL-12-44's chain). Returns (fact id of the pointer, the pointed id)."""
    tx = ctx.need_tx()
    st = tx.state
    here = home_of(st, pc) or (st.scene.place_id if st.scene else None)
    back = {k.split("|", 1)[0] for k, v in (st.meta.get(INDEX) or {}).items()
            if k.endswith(f"|{about or topic}") and v.get("pointer") == knower}
    subjects = {c["solution"]["subject"]["id"] for c in cases(st).values()}  # never the missing one themself
    kind, ref = pointer_target(st, topic, scope=here, asker=knower, exclude=back | subjects | {pc})
    if kind == "walk_on":
        where = settlement_of(st, here) or (st.meta.get("world.region") or {}).get("haven")
        ref = _walk_on(ctx, ref, topic, where) or where or here or ""
        kind = "person" if ref in st.entities and st.entities[ref].kind == "npc" else "place"
    if kind == "person" and ref in st.entities:
        learn_name(ctx.time_ctx(), pc, ref, "told")  # being told who would know is being told who they are
    fid = _write(ctx, knower, f"points_to.{ids.slug(about or topic)}"[:60], ref, rule="PR-12-10")
    _tell(ctx, pc, fid)
    return fid, ref


def _pointer_said(st: Any, ref: str, what: str, first: bool) -> str:
    dont = "do not know" if first else "does not know"
    if ref in st.entities and st.entities[ref].kind in PEOPLE:
        return f"{dont} {what}, but {name(st, ref)} would"
    return f"{dont} {what}, but someone at {name(st, ref)} would" if ref else f"{dont} {what}"


# ------------------------------------------------------------------------------------------- the case graph


def open_node(case: dict[str, Any], who: bool) -> dict[str, Any]:
    """The node a question reaches: "who is <role>" asks node 1; anything else the first unfound necessary node
    whose predecessors are found (15.9.5's prerequisites), else the last one."""
    nodes = [n for n in case["nodes"] if n["necessary"]]
    if who:
        return nodes[0]
    for i, n in enumerate(nodes):
        if not n.get("found"):
            return n if all(m.get("found") for m in nodes[:i]) else nodes[i - 1]
    return nodes[-1]


def deliver_node(ctx: Any, case: dict[str, Any], node: dict[str, Any], placement: str | None, pc: str,
                 how: str = "told") -> str:  # rule: 15.9.5
    """A placement's content reaches the PC: the node's fact (a person subject's `who_is_*` fact names them, so the
    name is learned, 12.10.2), the PC's knowledge record, and the node found (`mark_found`)."""
    st = ctx.need_tx().state
    sub = case["solution"]["subject"]
    if node is case["nodes"][0] and sub["id"] in st.entities:
        role = node["fact"].split(":", 1)[0]
        fid = _write(ctx, WORLD, ("who_is_" + ids.slug(role))[:58], sub["id"], rule="PR-15-6", source="generation")
    else:
        fid = _write(ctx, WORLD, f"case.{ids.slug(node['id'])}"[:60], node["fact"], rule="PR-15-6",
                     source="generation")
    _tell(ctx, pc, fid, how)
    mark_found(ctx.need_tx(), case["id"], node["id"], placement, fact_id=fid)
    return fid


def _from_case(ctx: Any, knower: str, case: dict[str, Any], who: bool, pc: str, first: bool) -> Answer:
    # rule: PR-12-10
    """The consequential route: a holder of a live placement on the node delivers it; anyone else does not know and
    names the holder of the node's core placement (the one that cannot fail), else of a live one."""
    st = ctx.need_tx().state
    node = open_node(case, who)
    held = next((p for p in node["placements"] if p["holder"] == knower and p.get("status") != "lost"), None)
    if held is not None or (node.get("found") and knower == pc and node.get("fact_id") in st.knowledge.get(pc, {})):
        fid = deliver_node(ctx, case, node, held["id"] if held else None, pc)
        said = f"{'remember' if first else 'tells you'} {node['fact']}"
        return Answer(said, "", fid)
    what = node["fact"].split(":", 1)[0]
    ref = pointer(case, node["id"], asked=knower, state=st)
    if ref is None:
        fid, ref = point(ctx, knower, "local_news", pc)
    else:
        if ref not in st.entities:  # a trace left at a place: the place
            p = next(p for p in node["placements"] if p["holder"] == ref)
            ref = p.get("at") or ref
        elif st.entities[ref].kind != "place" and st.entities[ref].kind not in PEOPLE:  # a document or thing
            ref = home_of(st, ref) or ref
        if ref in st.entities and st.entities[ref].kind in PEOPLE:
            learn_name(ctx.time_ctx(), pc, ref, "told")
        fid = _write(ctx, knower, f"points_to.{ids.slug(node['id'])}"[:60], ref, rule="PR-12-10")
        _tell(ctx, pc, fid)
    return Answer(_pointer_said(st, ref, what, first), "", fid, ref)


def case_about(st: Any, text: str, about: str | None) -> dict[str, Any] | None:  # rule: PR-12-10
    """The case a question is about: its subject asked about or named, or most of its story role's words used ("where
    did the missing child go?")."""
    have = words.content(text)
    for c in cases(st).values():
        sub = c["solution"]["subject"]
        if about == sub["id"] or have & words.content(sub["words"]) or words.covers(sub["role"], text, ratio=0.6):
            return c
    return None


# ------------------------------------------------------------------------------------------- ordinary rungs


def fact_words(st: Any, f: Any) -> str:
    who = name(st, f.subject) if f.subject in st.entities else ""
    value = {True: "yes", False: "no"}.get(f.value, f.value) if isinstance(f.value, bool) else f.value
    return f"{who} {f.predicate.replace('_', ' ').replace('.', ' ')} {value}"


def _sentence(st: Any, f: Any) -> str:
    from engine.audit.fallback import fact_sentence

    if f.predicate.startswith("topic.") and isinstance(f.value, str):
        return f.value
    return fact_sentence(st, f).rstrip(".")


def _usable(st: Any, f: Any, pc: str) -> bool:
    return (isinstance(f.value, str | bool | int | float) and f.visibility != "sealed" and f.id not in st.seals
            and f.subject not in st.seals and f.subject != pc and f.predicate not in _SKIP
            and not f.predicate.startswith(_SKIP_PREFIX) and not f.predicate.endswith((".but", ".and"))
            and st.current_fact_id(f.subject, f.predicate) == f.id)


def store_hit(st: Any, knower: str, topic: str, about: str | None, text: str, pc: str) -> str | None:
    # rule: PR-12-10
    """Rung 1: what the knower knows (records written in play), their own facts and the public facts about what was
    asked (12.10.6 (a)-(c)), ranked by relevance (the topic, the entity asked about, shared words); news first."""
    known = st.knowledge.get(knower, {})
    pool = set(known) | {f.id for f in st.facts.values()
                         if f.subject == knower or (about and f.subject == about and f.visibility == "shown")}
    names = " ".join(st.entities[i].name for i in (knower, pc, about) if i and i in st.entities)
    asked = words.content(text) - words.content(names)
    best: tuple[int, int, str] | None = None
    for fid in pool:
        f = st.facts.get(fid)
        if f is None or not _usable(st, f, pc) or not _sentence(st, f):
            continue
        s = 3 * f.predicate.startswith(f"topic.{topic}.") + 2 * (about is not None and f.subject == about) \
            + len(asked & words.content(fact_words(st, f)))
        if s and (best is None or (s, fid not in st.knowledge.get(pc, {})) > best[:2]):
            best = (s, fid not in st.knowledge.get(pc, {}), fid)
    return best[2] if best else None


def _whereabouts(ctx: Any, knower: str, about: str | None) -> str | None:  # rule: 12.10.6
    """A public fact in the knower's scope (12.10.6(c), `folk`): where a person of their settlement lives, where a
    place lies."""
    st = ctx.need_tx().state
    if about is None or about in st.seals or not alive(st, about):
        return None
    e = st.entities[about]
    if e.kind == "place":
        parent = e.data.get("parent")
        return _write(ctx, about, "lies_in", st.entities[parent].name, rule="12.10.6", source="data") \
            if parent in st.entities else None
    home = home_of(st, about)
    if e.kind == "npc" and home in st.entities and settlement_of(st, home) == settlement_of(st, home_of(st, knower)):
        return _write(ctx, about, "found_at", st.entities[home].name, rule="12.10.6", source="data")
    return None


def pack_hit(ctx: Any, knower: str, topic: str, about: str | None, pc: str) -> str | None:  # rule: 12.16.11
    """Rung 2: the knower's seeded knowledge pack on the topic (or about the entity asked), one the PC has not been
    told first; written as a fact (`source: data`) the knower knows."""
    st = ctx.need_tx().state
    # ponytail: a rumor item carries no text (its row is in the region's rumor table, not in the store): untold
    items = [k for k in st.entities[knower].data.get("knowledge") or []
             if k.get("text") and (k.get("topic") == topic or (about and k.get("about") == about))]
    best = None
    for k in items:
        fid = st.current_fact_id(k.get("about") or WORLD, f"topic.{k['topic']}.{ids.slug(k['fact'])}"[:60])
        if fid is None or fid not in st.knowledge.get(pc, {}):
            best = k
            break
    best = best or (items[0] if items else None)
    if best is None:
        return None
    fid = _write(ctx, best.get("about") or WORLD, f"topic.{best['topic']}.{ids.slug(best['fact'])}"[:60],
                 best["text"], rule="12.16.11", source="data")
    if fid not in st.knowledge.get(knower, {}):
        record_knowledge(ctx.time_ctx(), knower, fid, "recalled")
    return fid


def odds_for(st: Any, knower: str, topic: str) -> str:  # rule: 12.10.6
    """12.10.6(d) via `social.yaml#common_knowledge`: a role topic Likely; a public topic of a local Likely; else
    Unlikely. Fixed before the roll (00.12.7)."""
    ck = pack_data().CK
    e = st.entities[knower]
    rk = role_key({"role": e.data.get("role")})
    haven = (st.meta.get("world.region") or {}).get("haven")
    if topic in ck["by_role"].get(rk, []):
        return str(ck["odds"]["on_role_topic"])
    if (ck["topics"].get(topic) or {}).get("public") and haven and settlement_of(st, home_of(st, knower)) == haven:
        return str(ck["odds"]["public_local"])
    return str(ck["odds"]["other"])


def _touches(st: Any, said: str) -> dict[str, Any] | None | bool:
    """A candidate that touches a case node (its subject's words, or most of a node's words): that case; one that
    covers a sealed fact: True; else None (PR-12-10 step 4's code check)."""
    have = words.content(said)
    for c in cases(st).values():
        if have & words.content(c["solution"]["subject"]["words"]) or any(
                words.covers(n["fact"].split(":", 1)[-1], said, ratio=0.6) for n in c["nodes"]):
            return c
    for f in st.facts.values():
        if (f.visibility == "sealed" or f.id in st.seals) and words.covers(fact_words(st, f), said, ratio=0.6):
            return True
    return None


def ratify(ctx: Any, knower: str, topic: str, text: str, pc: str) -> tuple[str | None, Any]:  # rule: PR-12-10
    """Rung 4 of the procedure (propose and ratify): one typed candidate from the Proposer, checked by code, then
    the Oracle asks "Does <NPC> know that <candidate>?" at the odds fixed first. Returns (fact id told, None) on a
    yes; (None, None) on a no (the `knows_*` = false fact is the "does not know" record); (None, case) when the
    candidate touched a case (the consequential route answers instead)."""
    from engine.dm.roles.proposer import propose
    from engine.resolve.oracle import OracleQuestion, ask_oracle

    tx = ctx.need_tx()
    st = tx.state
    ck = pack_data().CK
    e = st.entities[knower]
    pack = [str(k["text"]) for k in e.data.get("knowledge") or [] if k.get("text")]
    cand = propose(ctx, f"{name(st, knower)} ({e.data.get('role') or e.kind})", text, topic,
                   str((ck["topics"].get(topic) or {}).get("gist") or topic), known=pack)
    if cand is None:
        return None, None
    said = " ".join(str(cand[k]).strip() for k in ("subject", "predicate", "value")).rstrip(".")
    hit = _touches(st, said)
    if isinstance(hit, dict):
        return None, hit
    if hit:
        return None, None
    pred = f"topic.{topic}.{ids.slug(str(cand['subject']))}"[:60]
    cur = st.current_fact_id(WORLD, pred)
    if cur is not None:  # the world already settled it: the question is only whether they know it
        said = _sentence(st, st.facts[cur])
    res = ask_oracle(OracleQuestion(subject=knower, predicate=("knows_" + ids.slug(said))[:60],
                                    question=f"Does {name(st, knower)} know that {said}?", odds=odds_for(st, knower, topic)),
                     state=st, rules=ctx.rules, rng=ctx.rng, mint=tx.mint, store=ctx.store, staged=tx.events)
    tx.add_all(res.events)
    if res.answer is not True:
        return None, None
    fid = cur or _write(ctx, WORLD, pred, said, rule="PR-12-10", source="oracle")
    if fid not in st.knowledge.get(knower, {}):
        record_knowledge(ctx.time_ctx(), knower, fid, "recalled")
    return fid, None


# ------------------------------------------------------------------------------------------- the ladder


def ask(ctx: Any, knower: str, kind: str, topic: str | None, text: str, rungs: Sequence[str], *,
        pc: str) -> Answer:  # rule: PR-12-10
    """One delivered question put to `knower` (an NPC), answered at the depth `rungs` allows; never empty."""
    st = ctx.need_tx().state
    if kind == "who_is" and re.search(r"\b(?:would|might|could)\s+know\b", text, re.IGNORECASE):
        kind = "who_knows"  # "who around here would know ...?" asks for a pointer, not a person in a role
    key_topic, about = topic_of(st, topic, text, knower)
    key = _key(knower, kind, about or key_topic)
    hit = (st.meta.get(INDEX) or {}).get(key)
    k_name = _cap(name(st, knower))
    if hit:  # step 1: the same fact, or the same "does not know" and pointer
        _tell(ctx, pc, hit.get("fact"))
        return Answer(hit["said"], f"{k_name} {hit['said']}", hit.get("fact"), hit.get("pointer"))
    a = _route(ctx, knower, kind, key_topic, about, text, rungs, pc, topic)
    a.line = f"{k_name} {a.said}"
    return _remember(ctx, key, a)


def _route(ctx: Any, knower: str, kind: str, topic: str, about: str | None, text: str, rungs: Sequence[str],
           pc: str, given: str | None = None) -> Answer:
    st = ctx.need_tx().state
    if kind == "who_is" or about == knower or _OWN_NAME.search(text):
        a = _who(ctx, knower, text, about, pc, given)
        if a is not None:
            return a
    case = case_about(st, text, about)
    if case is not None:
        return _from_case(ctx, knower, case, False, pc, False)
    if kind == "what_want":
        stance = st.entities[knower].data.get("stance") or {}
        if stance.get("why"):
            toward = "the trouble" if stance.get("toward") == "incident" else str(stance.get("toward") or "it")
            fid = _write(ctx, knower, "stance.said", f"{stance.get('stance')}: {stance['why']}", rule="12.11.4",
                         source="data")
            _tell(ctx, pc, fid)
            return Answer(f"tells you where they stand on {toward}: {_why(stance)}", "", fid)
    what = f"about {_gist(topic, about, st)}"
    if kind != "who_knows":
        for rung in rungs:
            fid = None
            if rung == "store":
                fid = (_whereabouts(ctx, knower, about) if kind == "where_is" else None) or store_hit(
                    st, knower, topic, about, text, pc)
            elif rung == "pack":
                fid = pack_hit(ctx, knower, topic, about, pc)
            elif rung == "propose_and_ratify" and st.entities[knower].kind in PEOPLE:
                fid, touched = ratify(ctx, knower, topic, text, pc)
                if touched is not None:
                    return _from_case(ctx, knower, touched, False, pc, False)
            if fid is not None:
                _tell(ctx, pc, fid)
                return Answer(f"tells you: {_sentence(st, st.facts[fid])}", "", fid)
    fid, ref = point(ctx, knower, topic, pc, about=about)  # step 5: "I don't know" and a real lead (DL-12-44)
    return Answer(_pointer_said(st, ref, what, False), "", fid, ref)


def _role_words(text: str) -> str | None:
    m = _WHO.search(text.replace("_", " "))
    return m.group(2).strip(" ?.") if m else None


def _who_verb(text: str) -> str:
    m = _WHO.search(text.replace("_", " "))
    return (m.group(1) or "is").lower() if m else "is"


def _who(ctx: Any, knower: str, text: str, about: str | None, pc: str, given: str | None = None
         ) -> Answer | None:  # rule: PR-12-10
    """"Who is <role>?": their own name (12.10.2); a person asked about by name; a story role -> the case graph (the
    reduced case built now when none is behind it); any other role -> casting, else "no one you know"."""
    st = ctx.need_tx().state
    role = _role_words(text) or ""
    if about == knower or _SELF.match(role) or (not role and _OWN_NAME.search(text)):
        if st.entities[knower].kind not in PEOPLE:
            return None
        learn_name(ctx.time_ctx(), pc, knower, "told")
        return Answer(f"gives their name, in their own words: {st.entities[knower].name}", "",
                      st.current_fact_id(knower, "name"))
    asked = words.content(role)  # "who is Bran?" names them; "who is the old enemy?" does not name Old Power
    named = about is not None and (about == given or bool(asked) and asked <= words.content(st.entities[about].name))
    if about is not None and named and st.entities[about].kind == "npc" and about not in st.seals:
        learn_name(ctx.time_ctx(), pc, about, "told")
        return Answer(f"tells you who that is: {st.entities[about].name}", "", st.current_fact_id(about, "name"))
    if not words.content(role):
        return None
    found = who_case(ctx, role, pc)
    if found is not None:
        return _from_case(ctx, knower, found, True, pc, False)
    fid, who = cast_who(ctx, role, story=bool(words.content(role) & STORY_ROLES), exclude=(knower,))
    _tell(ctx, pc, fid)
    return Answer(f"tells you who {_who_verb(text)} {role}: {who}", "", fid)


def who_case(ctx: Any, role: str, pc: str) -> dict[str, Any] | None:  # rule: PR-12-10
    """The case behind a story-role question, built now (PR-15-6's reduced profile, DL-15-38) when none is."""
    st = ctx.need_tx().state
    if not (words.content(role) & STORY_ROLES or story_option(role)):
        return None
    here = home_of(st, pc) if pc in st.entities else None
    return case_covering(st, role) or case_for_question(ctx.need_tx(), role, here)


def cast_who(ctx: Any, role: str, *, story: bool, exclude: Sequence[str] = ()) -> tuple[str, str]:  # rule: 00.11.1
    """"Who is <role>?" (not a story role a case answers): a stored `who_is_*` fact, else an existing person by
    casting (`social.yaml#cast`), else "no one you know"; written as a fact. Returns (fact id, the answer in words)."""
    st = ctx.need_tx().state
    pred = ("who_is_" + ids.slug(role))[:57]
    cur = st.current_fact_id(WORLD, pred)
    if cur is None:
        pc = active_pc(st)
        here = home_of(st, pc) if pc in st.entities else None
        who = cast(st, role, scope=here, exclude=exclude, gate=not story) or NO_ONE
        cur = _write(ctx, WORLD, pred, who, rule="00.11.1", source="generation")
    v = st.facts[cur].value
    return cur, (st.entities[v].name if isinstance(v, str) and v in st.entities else str(v))


def who_answer(ctx: Any, text: str) -> tuple[str, str] | None:  # rule: PR-12-10
    """A "who is X?" put to the DM (a FICTION_QUESTION, 01.3.8): the PC is the knower. A story role is answered from
    the case only when the PC has been told it, else with who would know (the core holder); any other role by
    casting. None when the text is not a who-question (the caller's Oracle asks it)."""
    role = _role_words(text)
    if not role or not words.content(role) or _SELF.match(role):
        return None
    st = ctx.need_tx().state
    pc = active_pc(st)
    if pc is None:
        return None
    case = who_case(ctx, role, pc)
    if case is not None:
        a = _from_case(ctx, pc, case, True, pc, True)
        if a.pointer is None:
            v = st.facts[a.fact_id].value if a.fact_id else None
            return (st.entities[v].name if isinstance(v, str) and v in st.entities else str(v)), str(a.fact_id)
        return f"no one has told you; {name(st, a.pointer)} would know", str(a.fact_id)
    fid, who = cast_who(ctx, role, story=bool(words.content(role) & STORY_ROLES))
    _tell(ctx, pc, fid)
    return who, fid


# the seed's stance reasons that are bookkeeping, in the words the NPC would use (12.16.11's stance)
_WHY = {"holds a placement of the incident's case": "they know something of it and want it settled",
        "of the threat faction": "they would rather you left it alone"}


def _why(stance: dict[str, Any]) -> str:
    return _WHY.get(str(stance["why"]), str(stance["why"]))


def volunteer(ctx: Any, knower: str, pc: str) -> Answer | None:  # rule: T-15-5
    """Great reach or better: one extra the NPC chooses from their record (a tie or another pack fact the PC has
    not heard, else their stance), told unasked."""
    st = ctx.need_tx().state
    e = st.entities.get(knower)
    if e is None or e.kind not in PEOPLE:
        return None
    for k in sorted((k for k in e.data.get("knowledge") or [] if k.get("text")), key=lambda k: k.get("slot") != "tie"):
        fid = st.current_fact_id(k.get("about") or WORLD, f"topic.{k['topic']}.{ids.slug(k['fact'])}"[:60])
        if fid is None or fid not in st.knowledge.get(pc, {}):
            fid = pack_hit(ctx, knower, str(k["topic"]), k.get("about"), pc)
            if fid is not None:
                _tell(ctx, pc, fid)
                said = f"adds, unasked: {_sentence(st, st.facts[fid])}"
                return Answer(said, f"{_cap(name(st, knower))} {said}", fid)
    stance = e.data.get("stance") or {}
    if stance.get("why") and st.current_fact_id(knower, "stance.said") is None:
        fid = _write(ctx, knower, "stance.said", f"{stance.get('stance')}: {stance['why']}", rule="12.11.4",
                     source="data")
        _tell(ctx, pc, fid)
        said = f"lets slip where they stand: {_why(stance)}"
        return Answer(said, f"{_cap(name(st, knower))} {said}", fid)
    return None


__all__ = ["INDEX", "NO_ONE", "STORY_ROLES", "Answer", "ask", "case_about", "cast_who", "deliver_count",
           "deliver_node", "name", "odds_for", "pack_hit", "point", "ratify", "rungs_for", "store_hit", "topic_of",
           "volunteer", "who_answer"]
