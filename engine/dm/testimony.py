"""Testimony (12.3.1b, 12.10.8, PR-12-12; spec 013): what a character says is a `said` record on the speaker, fed
back on their speaker card, never a world fact until it matters.

    add_said(ctx, [{"speaker": "npc.nibwen", "words": "...", "about": [...], "question": "npc.nibwen|what_is|folk"}])
    said_by(state, "npc.nibwen", topic="folk")      # recent lines + every one on the topic (`answer_ladder.said_shown`)
    is_repeat(state, rules, "npc.nibwen", words)     # `not_a_repeat`: overlap above `narration.freshness.said_overlap`
    settle_triggered(ctx, reader, record)            # PR-12-12 triggers (a) and (c): settle once, before framing

Records live in meta `npc.said` {"n": int, "records": [{id, speaker, turn, words, about, question, settled, fact}]}.
The asked-and-answered index (meta `answers.index`, `"<npc>|<kind>|<topic>" -> {willingness, reason, said}`) is the
NPC's memory; it never supplies words.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from typing import Any

from engine import ids
from engine.audit import text as words
from engine.world.common import active_pc, fact, meta

SAID = "npc.said"
INDEX = "answers.index"
KEEP = 120  # ponytail: the newest records only; an archive if long games need older testimony
PEOPLE = ("npc", "companion", "adversary")


def records(state: Any) -> list[dict[str, Any]]:
    return list((state.meta.get(SAID) or {}).get("records") or [])


def open_records(state: Any, k: int = 8) -> list[dict[str, Any]]:  # rule: PR-12-12
    """The newest `k` unsettled `said` records: what the Reader may name as `rests_on`."""
    return [r for r in records(state) if r.get("settled") is None and r.get("speaker")][-k:]


def get(state: Any, said_id: str) -> dict[str, Any] | None:
    return next((r for r in records(state) if r["id"] == said_id), None)


def said_by(state: Any, npc: str, *, topic: str | None = None, about: str | None = None,
            k: int = 6) -> list[dict[str, Any]]:  # rule: PR-12-10
    """PR-12-10 step 3: the speaker's `k` most recent `said` records plus every one on the asked topic (the
    question's topic key, or the entity asked about), oldest first."""
    mine = [r for r in records(state) if r.get("speaker") == npc]
    on = [r for r in mine if (topic and str(r.get("question") or "").endswith(f"|{topic}"))
          or (about and (about in (r.get("about") or []) or str(r.get("question") or "").endswith(f"|{about}")))]
    keep = {r["id"] for r in [*mine[-k:], *on]}
    return [r for r in mine if r["id"] in keep]


def overlap(a: str, b: str) -> float:
    """The share of `a`'s content words already in `b` (0 when `a` has fewer than three)."""
    wa, wb = words.content(a), words.content(b)
    return len(wa & wb) / len(wa) if len(wa) >= 3 else 0.0


def is_repeat(state: Any, rules: Any, speaker: str | None, said: str) -> str | None:  # rule: 12.14.11
    # rule: 12.3.1b
    """`not_a_repeat` (`claim_check.speech_checks`): the speaker's own earlier line this one repeats (content-word
    overlap above `narration.freshness.said_overlap`), else None."""
    if not speaker:
        return None
    limit = float((((rules.pacing.get("narration") or {}).get("freshness") or {}).get("said_overlap")) or 0.6)
    return next((r["words"] for r in records(state)
                 if r.get("speaker") == speaker and overlap(said, r["words"]) > limit), None)


def add_said(ctx: Any, entries: Sequence[dict[str, Any]]) -> list[str]:  # rule: PR-12-10
    # rule: 12.3.1b
    """PR-12-10 step 5: each spoken line as a `said` record; the index entry of the question it answers gets its id.
    No world fact is written."""
    if not entries:
        return []
    tx = ctx.need_tx()
    cur = dict(tx.state.meta.get(SAID) or {})
    n, recs = int(cur.get("n") or 0), list(cur.get("records") or [])
    idx = dict(tx.state.meta.get(INDEX) or {})
    out = []
    for e in entries:
        n += 1
        sid = f"said.{n}"
        recs.append({"id": sid, "speaker": e.get("speaker"), "turn": e.get("turn") or ctx.turn_id,
                     "words": str(e.get("words") or ""), "about": list(e.get("about") or []),
                     "question": e.get("question"), "settled": None, "fact": None})
        q = e.get("question")
        if q and q in idx:
            idx[q] = {**idx[q], "said": [*(idx[q].get("said") or []), sid]}
        out.append(sid)
    tx.add(meta(SAID, {"n": n, "records": recs[-KEEP:]}, "PR-12-10"))
    if idx != (tx.state.meta.get(INDEX) or {}):
        tx.add(meta(INDEX, idx, "PR-12-10"))
    return out


# ------------------------------------------------------------------------------------------- PR-12-12


def _named(state: Any, r: dict[str, Any], eid: str) -> bool:
    e = state.entities.get(eid)
    return bool(e) and (eid in (r.get("about") or []) or bool(
        e.name and re.search(rf"\b{re.escape(e.name.lower())}\b", str(r.get("words") or "").lower())))


def _known_only_from_testimony(state: Any, pc: str, eid: str) -> bool:  # rule: PR-12-12
    """The PC knows `eid` only from what someone said: a person whose name they only heard, or a place no record of
    theirs is about."""
    e = state.entities[eid]
    known = state.knowledge.get(pc, {})
    if e.kind in PEOPLE:
        fid = state.current_fact_id(eid, "name")
        return fid is not None and fid in known and known[fid].how == "heard"
    if e.kind == "place":
        here = state.scene.place_id if state.scene else None
        return eid != here and not any(fid in state.facts and state.facts[fid].subject == eid for fid in known)
    return False


def triggered(state: Any, rests_on: str | None, targets: Sequence[str]) -> list[str]:  # rule: PR-12-12
    """PR-12-12 step 1, triggers (a) acted on and (c) travel, over the unsettled `said` records: the Reader's
    `rests_on`, or a beat's target (a person, or a place a Move or travel sets out for) that a `said` record names
    and the PC knows only from testimony. Hearing, repeating or asking about testimony settles nothing.
    ponytail: (b) a lever citing a `said` id and (d) a frame input are not derived (spec 015/016 own them)."""
    open_ = [r for r in records(state) if r.get("settled") is None]
    out = [r["id"] for r in open_ if r["id"] == rests_on]
    pc = active_pc(state)
    for t in targets:
        if pc is None or t not in state.entities or not _known_only_from_testimony(state, pc, t):
            continue
        out += [r["id"] for r in open_ if _named(state, r, t)][-1:]  # the latest line that named it
    return list(dict.fromkeys(out))


# 12.14.13's question ("would it help or hinder the PC beyond what any such place ordinarily offers?") as a word
# test on the stated claim. ponytail: a word list; a typed claim kind would replace it
_BEYOND = re.compile(r"\b(secret\w*|hidden|treasure\w*|hoard|weak(?:ness|\s+spot)|cure\w*|passage|tunnel|key|"
                     r"magic\w*|enchant\w*|cursed|haunted|ambush\w*|traitor|spy|smuggl\w*|vault|map)\b", re.I)


def _claim(ctx: Any, r: dict[str, Any]) -> dict[str, str]:  # rule: PR-12-12
    """Step 2: one `[J:enum]` call states the said words as `{subject, predicate, value}`; it judges nothing else."""
    from engine.dm.packet import identity_lines, name_line
    from engine.dm.roles.prompts import load_prompt
    from engine.dm.schemas import build_schema, schema_context
    from engine.llm.base import Packet, Role, call_role

    st = ctx.need_tx().state
    sctx = schema_context(st, ctx.rules)
    about = [a for a in r.get("about") or [] if a in st.entities and a not in st.seals]
    sctx = sctx.model_copy(update={"scene_ids": list(dict.fromkeys([*about, *sctx.scene_ids]))})
    schema = build_schema(Role.TESTIMONY, sctx)
    view = "\n".join(name_line(st, a) for a in about)
    # rule: 12.2.4
    # item 3: who the speaker and everyone the words name are (pronouns, bond), so "he" and "my sister" resolve (I2 §4)
    people = identity_lines(st, [r.get("speaker") or "", *about], str(r.get("words") or ""))
    if people:
        view += "\npeople named (name: pronouns; \"your\" means the player's character's):\n" + "\n".join(people)
    packet = Packet(instructions=load_prompt("testimony"), core="", cards=[], view=view, exchanges=[],
                    message=f"{name_line(st, r.get('speaker') or '')} said: \"{r['words']}\"")
    default = {"subject": about[0] if about else "world", "predicate": "is said to be", "value": r["words"][:160]}
    res = call_role(ctx.model, Role.TESTIMONY, schema, packet, turn_id=ctx.turn_id, recorder=ctx.record_call,
                    default=default)
    d = {k: str(res.data.get(k) or default[k]) for k in default}
    return d


def _case_route(st: Any, subject: str, text: str) -> bool | None:  # rule: PR-12-12
    """Step 3's consequential tier: the claim touches a case (its subject, or most of a node's words) or a sealed
    fact. True when the case holds it, False when it does not; None when it is not consequential."""
    from engine.dm.answer import fact_words
    from engine.gen.case import cases

    have = words.content(text)
    for c in cases(st).values():
        sub = c["solution"]["subject"]
        nodes = [n for n in c["nodes"] if words.covers(n["fact"].split(":", 1)[-1], text, ratio=0.6)]
        if nodes:
            return True
        if subject == sub["id"] or have & words.content(sub["words"]):
            return False  # about the case's subject, and no node of it says so
    for f in st.facts.values():
        if (f.visibility == "sealed" or f.id in st.seals) and words.covers(fact_words(st, f), text, ratio=0.6):
            return True
    return None


def settle(ctx: Any, said_id: str, record: Any = None) -> str | None:  # rule: PR-12-12
    """Steps 2-4 for one unsettled `said` record: state the claim, route it (the case; the Oracle at Likely beyond
    the ordinary; else accepted), write a fact (`source: testimony | oracle`) or the speaker's error
    (`wrong_about`), and mark the record settled with the fact id. Never delivers a clue. Returns the fact id."""
    from engine.resolve.oracle import OracleQuestion, ask_oracle
    from engine.world.social import record_knowledge

    tx = ctx.need_tx()
    st = tx.state
    r = get(st, said_id)
    if r is None or r.get("settled") is not None:
        return None
    c = _claim(ctx, r)
    subject = c["subject"] if c["subject"] in st.entities else "world"
    text = f"{c['subject'] if subject == 'world' else st.entities[subject].name} {c['predicate']} {c['value']}"
    pred = ("said." + ids.slug(f"{c['predicate']} {c['value']}"))[:60]
    route, true = "accepted", True
    case = _case_route(st, subject, text)
    fid: str | None = None
    if case is not None:
        route, true = "case", case
    elif _BEYOND.search(text):
        res = ask_oracle(OracleQuestion(subject=subject, predicate=pred, question=f"Is it true that {text}?",
                                        odds="likely"), state=st, rules=ctx.rules, rng=ctx.rng, mint=tx.mint,
                         store=ctx.store, staged=tx.events)
        tx.add_all(res.events)
        route, true, fid = "oracle", res.answer is True, (res.fact_id if res.answer is True else None)
    speaker = r.get("speaker") or "world"
    if route == "case" and true:
        pass  # the case already holds it: nothing is written or told (a clue comes only by its placement, 15.9)
    elif true and fid is None:
        ev = fact(tx, subject, pred, c["value"], rule_id="PR-12-12", source="testimony", visibility="shown")
        tx.add(ev)
        fid = str(ev.payload.fact_id)  # type: ignore[attr-defined]
    elif not true:
        ev = fact(tx, speaker if speaker in st.entities else "world", "wrong_about", text, rule_id="PR-12-12",
                  source="ruling", visibility="shown")
        tx.add(ev)
        fid = str(ev.payload.fact_id)  # type: ignore[attr-defined]
    pc = active_pc(tx.state)
    if pc and fid and fid in tx.state.facts and fid not in tx.state.knowledge.get(pc, {}):
        record_knowledge(ctx.time_ctx(), pc, fid, "told")
    cur = dict(tx.state.meta.get(SAID) or {})
    recs = [dict(x, settled=bool(true), fact=fid, route=route) if x["id"] == said_id else x
            for x in cur.get("records") or []]
    tx.add(meta(SAID, {**cur, "records": recs}, "PR-12-12"))
    if record is not None:
        record.notes.append(f"testimony settled ({route}): {text} -> {'true' if true else 'false'}")
    return fid


def settle_triggered(ctx: Any, reader: Any, record: Any = None) -> list[str]:  # rule: PR-12-12
    """At T4, before the beats frame: settle every `said` record a trigger names, so a true claim is citable from
    this beat on (the words were said before the declaration, 01.6.8). Returns the `said` ids settled."""
    st = ctx.need_tx().state
    if not records(st):
        return []
    targets = [b.target for b in getattr(reader, "beats", []) if b.target and b.target != "none"]
    out = triggered(st, getattr(reader, "rests_on", None), targets)
    for sid in out:
        settle(ctx, sid, record)
    return out


__all__ = ["INDEX", "SAID", "add_said", "get", "is_repeat", "overlap", "records", "said_by", "settle",
           "settle_triggered", "triggered"]
