"""Disputes and corrections (12.3.6, PR-12-4, DL-12-04): the player says the DM erred; the DM answers from the turn
log and the store, never from memory.

    text = dispute(ctx, "you said the gate was barred")          # engine/dm/context.py DisputeHandler
    res = settle_dispute(ctx, text, identify=my_reader)           # the full result (blocks, writes, choices)
    res = settle_dispute(ctx, text, identify=my_reader, choice="rewind")   # answer the reliance CHOICE

Which delivered claim the player means is judgement: `identify(ctx, text) -> DisputedClaim | None` is injected by
the turn loop (a model call); the default reads explicit ids, entity names and quantity names from the text. Every
answer is an OOF block; a correction writes only what PR-12-4 allows (a corrective `fact_set` or quantity change
for a record error; `writes_reverted` within the current scene for a rewind) plus the correction record and a
ruling with `review_flag: true`. Nothing is ever created from the player's memory alone (INV-9).
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Literal

from engine import ids
from engine.dm.oof import OofBlock, note_block
from engine.resolve.rulings import RulingRecord, log_ruling
from engine.store.db import REVERTIBLE, Rejected, Transaction
from engine.store.events import WORLD, Event
from engine.store.projection import WorldState

PLAYER_FACING = ("shown", "available")
Choice = Literal["rewind", "accept_forward", "keep"]
DisputeKind = Literal["unclear", "hidden", "not_said", "stands", "narration_error", "record_error", "ruling_stands",
                      "ruling_error"]


@dataclass
class DisputedClaim:
    """The delivered claim in question. `kind` fact: `subject`/`key` = a fact's subject and predicate; quantity:
    an entity and a quantity name; ruling: `frame_id` and the `missed_fact` the player says was left out."""

    kind: Literal["fact", "quantity", "ruling"] = "fact"
    subject: str = ""
    key: str = ""
    said: Any = None  # the value the narration delivered (as the player reports it)
    quote: str = ""  # the delivered words in question, searched for in the turn log
    turn_id: str | None = None  # the turn that delivered it (None: search the log)
    source: str | None = None  # a resolved source requiring `said` (frame, handler, oracle fact): a record error
    frame_id: str | None = None
    missed_fact: str | None = None


Identify = Callable[[Any, str], "DisputedClaim | None"]


@dataclass
class DisputeResult:
    kind: DisputeKind
    blocks: list[OofBlock]
    events: list[Event] = field(default_factory=list)  # staged by settle_dispute
    reverted: list[int] = field(default_factory=list)
    choices: list[dict[str, str]] = field(default_factory=list)  # the reliance CHOICE (pause point 9), if open
    claim: DisputedClaim | None = None
    correction: dict[str, Any] | None = None  # the correction record (12.3.4 step 4)

    @property
    def text(self) -> str:
        return "\n".join(b.text for b in self.blocks)


# ------------------------------------------------------------------------------------------- the turn log


def _turns(store: Any, before: str | None = None, limit: int = 50) -> list[Any]:
    """Turn records newest first (up to `limit`), optionally only those before `before`."""
    cut = (ids.parse_counter_id(before) or ("", 0))[1] if before else None
    ns = []
    for (t,) in store.conn.execute("SELECT turn_id FROM turns"):
        p = ids.parse_counter_id(t) if isinstance(t, str) else None
        if p and p[0] == ids.TURN and (cut is None or p[1] < cut):
            ns.append(p[1])
    out = [store.turn(ids.counter_id(ids.TURN, k)) for k in sorted(ns, reverse=True)[:limit]]
    return [t for t in out if t is not None]


def _delivered_in(store: Any, claim: DisputedClaim, current: str | None) -> Any:  # rule: 12.3.6
    """The turn record whose delivered narration carries the claim, or None (it was never said)."""
    quote = " ".join(claim.quote.lower().split())
    if claim.turn_id:
        tr = store.turn(claim.turn_id)
        if tr is None:
            return None
        return tr if not quote or quote in " ".join(tr.delivered_verbatim.lower().split()) else None
    if not quote:
        return None
    for tr in _turns(store, current):
        if quote in " ".join(tr.delivered_verbatim.lower().split()):
            return tr
    return None


def _relevant_exchange(store: Any, words: list[str], current: str | None) -> Any:
    """The latest play turn whose exchange mentions any of `words` (else the latest play turn). Engine turns (the
    opening, a session's open or close, an epilogue: input "(...)") hold where-you-stand lines, not exchanges."""
    turns = [tr for tr in _turns(store, current) if not tr.input_verbatim.startswith("(")]
    for tr in turns:
        hay = (tr.input_verbatim + " " + tr.delivered_verbatim).lower()
        if any(w and w.lower() in hay for w in words):
            return tr
    return turns[0] if turns else None


def _quote(tr: Any, n: int = 200) -> str:
    said = " ".join(tr.delivered_verbatim.split())
    return f"{tr.turn_id}: \"{said[:n]}{'…' if len(said) > n else ''}\""


# ------------------------------------------------------------------------------------------- the store side


def _name(state: WorldState, eid: str) -> str:
    if eid == WORLD:
        return "the world"
    e = state.entities.get(eid)
    return e.name if e is not None else eid


def _visible_entity(state: WorldState, eid: str) -> bool:
    if eid == WORLD:
        return True
    e = state.entities.get(eid)
    return e is not None and eid not in state.seals and e.visibility in PLAYER_FACING


def _store_value(state: WorldState, c: DisputedClaim) -> tuple[Any, bool, str | None]:
    """(value, player-facing?, fact id) for the claim's subject and key."""
    if c.kind == "quantity":
        q = state.quantities.get(c.subject, {}).get(c.key)
        if q is None:
            return None, _visible_entity(state, c.subject), None
        return q.current, q.visibility in PLAYER_FACING and _visible_entity(state, c.subject), None
    fid = state.current_fact_id(c.subject, c.key)
    if fid is None:
        return None, _visible_entity(state, c.subject), None
    f = state.facts[fid]
    ok = f.visibility in PLAYER_FACING and fid not in state.seals and _visible_entity(state, c.subject)
    return f.value, ok, fid


def _same(a: Any, b: Any) -> bool:
    if isinstance(a, str) or isinstance(b, str):
        return str(a).strip().lower() == str(b).strip().lower()
    return a == b


def _source_exists(store: Any, state: WorldState, source: str | None) -> bool:  # rule: 12.3.4
    """12.3.4 step 1: a record error only when the resolved source's id can be named (a frame, a fact, or an
    event source in the log)."""
    if not source:
        return False
    if source in state.frames or source in state.facts or source in state.superseded_facts:
        return True
    row = store.conn.execute("SELECT 1 FROM events WHERE source=? LIMIT 1", (source,)).fetchone()
    return row is not None


def _last_seq(store: Any, turn_id: str | None) -> int:
    """The last event of the turn that delivered the error (its narration came after its writes)."""
    if not turn_id:
        return 0
    row = store.conn.execute("SELECT MAX(seq) FROM events WHERE turn_id=?", (turn_id,)).fetchone()
    return int(row[0]) if row and row[0] is not None else 0


def _relying(state: WorldState, c: DisputedClaim, after_seq: int) -> list[str]:  # rule: 12.3.4
    """Reliance (12.3.4 step 3): this scene's committed frames since the error whose target, levers or snags rest on
    the claim, or whose declared method names it. Frames from earlier scenes are not in the projection."""
    out = []
    name = _name(state, c.subject).lower()
    for fid, fs in state.frames.items():
        if fs.committed_seq <= after_seq:
            continue
        beat = fs.frame.get("beat") or {}
        cites = [x.get("fact_id") for x in (fs.frame.get("levers") or []) + (fs.frame.get("snags") or [])
                 if isinstance(x, dict)]
        cited_subjects = {(state.facts[x].subject, state.facts[x].predicate) for x in cites if x in state.facts}
        words = f"{beat.get('method', '')} {beat.get('intent', '')} {beat.get('restatement', '')}".lower()
        if (beat.get("target") == c.subject or (c.subject, c.key) in cited_subjects
                or (name and name != c.subject and name in words)):
            out.append(fid)
    return out


# ------------------------------------------------------------------------------------------- writes


@contextmanager
def _tx(ctx: Any) -> Iterator[Transaction]:
    """The turn's open transaction, else a one-shot one."""
    if getattr(ctx, "tx", None) is not None:
        yield ctx.tx
        return
    with ctx.store.transaction(None) as tx:
        yield tx


def _log(tx: Transaction, ctx: Any, c: DisputedClaim | None, situation: str, record: dict[str, Any],
         frame_id: str | None = None) -> list[Event]:  # rule: PR-12-4
    """Step 7: the correction record (the corrections ledger, available) and a ruling with `review_flag: true`."""
    ledger = list(tx.state.meta.get("corrections") or []) + [record]
    evs = [Event.of("meta_set", source="correction", rule_id="12.3.4", key="corrections", value=ledger)]
    tx.add(evs[0])
    sig = f"correction:{c.subject}.{c.key}" if c and c.subject else f"correction:{frame_id or 'unknown'}"
    rr = RulingRecord(signature=sig, situation=situation[:300], frame_id=frame_id, kind="rule_conflict",
                      review_flag=True, tags=["correction", record.get("kind", "")],
                      facts_cited=[x for x in (record.get("fact_id"),) if x])
    ev = log_ruling(rr, tx.mint, store=ctx.store, staged=tx.events, rule_id="12.3.4")
    tx.add(ev)
    return [*evs, ev]


def _rewind(ctx: Any, tx: Transaction, from_seq: int, reason: str) -> list[int]:  # rule: 12.3.4
    """`revert_writes` of every revertible write from `from_seq`, never past the current scene's start (DL-12-04)."""
    scene = tx.state.scene
    if scene is None:
        return []
    start = max(from_seq, scene.started_seq + 1)
    done = set(tx.state.reverted)
    seqs = [e.seq for e in ctx.store.events(since=start - 1) if e.type in REVERTIBLE and e.seq not in done
            and e.seq is not None]
    if not seqs:
        return []
    tx.add(Event.of("writes_reverted", source="correction", rule_id="12.3.4", reverted=seqs, reason=reason))
    return seqs


def _record(c: DisputedClaim, *, turn_found: str | None, kind: str, form: str, reliance: list[str],
            store_value: Any, rewound: list[str], fact_id: str | None = None) -> dict[str, Any]:
    return {"turn_of_error": c.turn_id, "turn_found": turn_found, "found_by": "player",
            "claim": {"subject": c.subject, "key": c.key, "said": c.said, "quote": c.quote}, "store_value": store_value,
            "kind": kind, "form": form, "reliance": reliance, "rewound_beats": rewound, "refunds": [],
            "fact_id": fact_id}


# ------------------------------------------------------------------------------------------- default identify


_NUM = re.compile(r"(?<![\w.])(\d+)(?![\w.])")


def default_identify(ctx: Any, text: str) -> DisputedClaim | None:  # rule: 12.3.6
    """A deterministic reading for M1: explicit ids (`frame.N` + `fact.N` = a ruling dispute; `subject.predicate`
    of a current fact), else a shown quantity of a shown entity named in the text, with the first number as what was
    said. None when nothing can be pinned down (the turn loop's model reading replaces this)."""
    state: WorldState = ctx.state
    low = text.lower()
    turn = re.search(r"\bturn\.\d+\b", low)
    turn_id = turn.group(0) if turn else None
    frame = re.search(r"\bframe\.\d+\b", low)
    if frame:
        fact = re.search(r"\bfact\.\d+\b", low)
        return DisputedClaim(kind="ruling", frame_id=frame.group(0), missed_fact=fact.group(0) if fact else None,
                             turn_id=turn_id)
    for key, fid in state.fact_keys.items():
        subj, pred = key.split("|", 1)
        if f"{subj}.{pred}".lower() in low and state.facts[fid].visibility in PLAYER_FACING:
            quote = re.search(r"[\"“](.+?)[\"”]", text)
            return DisputedClaim(kind="fact", subject=subj, key=pred, turn_id=turn_id,
                                 quote=quote.group(1) if quote else "")
    num = _NUM.search(text)
    for eid, qs in state.quantities.items():
        if not _visible_entity(state, eid):
            continue
        for qname, q in qs.items():
            if q.visibility not in PLAYER_FACING:
                continue
            word = qname.replace("_", " ").lower()
            if word in low and (eid in low or _name(state, eid).lower() in low or state.entities[eid].kind == "pc"):
                return DisputedClaim(kind="quantity", subject=eid, key=qname, said=int(num.group(1)) if num else None,
                                     turn_id=turn_id)
    return None


# ------------------------------------------------------------------------------------------- the dispute


def _ruling(ctx: Any, c: DisputedClaim, choice: Choice | None) -> DisputeResult:  # rule: 12.3.6
    """A disputed ruling: show the frame and its cited facts; a missed established fact makes it a ruling error
    with reliance true for that beat."""
    state: WorldState = ctx.state
    fs = state.frames.get(c.frame_id or "")
    frame = fs.frame if fs else None
    committed = fs.committed_seq if fs else 0
    if frame is None:
        for ev in ctx.store.events(types=["frame_committed"]):
            if ev.payload.frame_id == c.frame_id:  # type: ignore[attr-defined]
                frame, committed = ev.payload.frame, int(ev.seq or 0)  # type: ignore[attr-defined]
    if frame is None:
        return DisputeResult("unclear", [note_block(f"No committed frame {c.frame_id or '(none named)'} on record.")],
                             claim=c)
    cited = [x.get("fact_id") for x in (frame.get("levers") or []) + (frame.get("snags") or []) if isinstance(x, dict)]
    summary = (f"{c.frame_id}: {frame.get('attribute')}, {frame.get('tier') or frame.get('dc_source')} DC "
               f"{frame.get('dc')}, stakes {frame.get('stakes')}, reach {frame.get('reach')}; cited: "
               f"{', '.join(x for x in cited if x) or 'nothing'}.")
    f = state.facts.get(c.missed_fact or "")
    missed = (f is not None and f.visibility in PLAYER_FACING and c.missed_fact not in cited
              and f.valid_from_seq < committed)
    if not missed:
        why = ("no fact was named" if not c.missed_fact else
               f"{c.missed_fact} is already cited" if c.missed_fact in cited else
               f"{c.missed_fact} is not an established fact on record before that frame")
        return DisputeResult("ruling_stands", [note_block(summary, "RULING", [f"The ruling stands: {why}."])], claim=c)
    assert f is not None
    in_scene = fs is not None
    desc = f"{c.missed_fact} ({f.subject}.{f.predicate} = {f.value}) was on record and the frame omitted it."
    if in_scene and choice is None:
        choices = [{"id": "accept_forward", "label": "accept the result as it stands"},
                   {"id": "rewind", "label": "rewind to before that beat and declare again"}]
        return DisputeResult("ruling_error", [note_block(desc, "CORRECTION", [summary]), note_block(
            "Accept the result as it stands, or rewind to before that beat?", "CHOICE",
            ["(a) accept forward · (b) rewind"])], choices=choices, claim=c)
    with _tx(ctx) as tx:
        start = len(tx.events)
        reverted: list[int] = []
        if in_scene and choice == "rewind":
            reverted = _rewind(ctx, tx, committed, f"ruling error in {c.frame_id}: {c.missed_fact} omitted")
            void = list(tx.state.meta.get("rolls_voided") or []) + [c.frame_id]
            tx.add(Event.of("meta_set", source="correction", rule_id="12.3.4", key="rolls_voided", value=void))
        rec = _record(c, turn_found=tx.turn_id, kind="ruling_error", form="oof_note", reliance=[c.frame_id or ""],
                      store_value=f.value, rewound=[c.frame_id or ""] if reverted else [], fact_id=c.missed_fact)
        _log(tx, ctx, c, desc, rec, frame_id=c.frame_id)
        evs = tx.events[start:]
    tail = ("Rewound to before that beat; its roll is void. Declare again." if reverted else
            "The result stands and is corrected forward." if in_scene else
            "That beat was in an earlier scene: corrected going forward. Logged.")
    return DisputeResult("ruling_error", [note_block(desc, "CORRECTION", [tail])], events=evs, reverted=reverted,
                         claim=c, correction=rec)


def settle_dispute(ctx: Any, text: str, *, identify: Identify | None = None,
                   choice: Choice | None = None) -> DisputeResult:  # rule: 12.3.6
    # rule: PR-12-4
    """12.3.6 / PR-12-4 from the turn log and the store. `ctx`: anything with `store`, `state`, optional `tx`
    (the turn's open transaction; else a one-shot transaction is used for any write)."""
    state: WorldState = ctx.state
    current = getattr(ctx, "turn_id", None)
    c = (identify or default_identify)(ctx, text)
    if c is None:
        tr = _relevant_exchange(ctx.store, [], current)
        rest = [f"From the turn log — {_quote(tr)}"] if tr else []
        return DisputeResult("unclear", [note_block(
            "Which statement, and when? Name what was said (and the turn if you can); I check it against the record.",
            "NOTE", rest)])
    if c.kind == "ruling":
        return _ruling(ctx, c, choice)
    what = f"{_name(state, c.subject)} {c.key.replace('_', ' ')}"
    value, facing, fact_id = _store_value(state, c)
    if not facing:  # 00.6.4: background and sealed state is never shown; the objection is logged for review
        with _tx(ctx) as tx:
            start = len(tx.events)
            rec = _record(c, turn_found=tx.turn_id, kind="unverified", form="oof_note", reliance=[], store_value=None,
                          rewound=[])
            _log(tx, ctx, c, f"player disputes {what}; not player-facing", rec)
            evs = tx.events[start:]
        return DisputeResult("hidden", [note_block(
            "Your character can't check that from here, so I can't show the record. Your objection is logged for "
            "review.", "UNKNOWN")], events=evs, claim=c, correction=rec)
    tr = _delivered_in(ctx.store, c, current)
    shown = "nothing on record" if value is None else str(value)
    if tr is None:  # rule: 12.3.6
        ex = _relevant_exchange(ctx.store, [c.quote, _name(state, c.subject)], current)
        rest = [f"From the turn log — {_quote(ex)}"] if ex else []
        return DisputeResult("not_said", [note_block(f"The record has {what}: {shown}. The narration never said "
                                                     "otherwise.", "NOTE", rest)], claim=c)
    c.turn_id = c.turn_id or tr.turn_id
    if c.said is None or _same(c.said, value):
        head = f"The record has {what}: {shown}." if c.said is None else f"The record agrees: {what} is {shown}."
        return DisputeResult("stands", [note_block(head, "NOTE", [f"As delivered — {_quote(tr)}"])], claim=c)
    # a mismatch the player has seen: PR-12-4
    if _source_exists(ctx.store, state, c.source):  # record error: a corrective write citing the source
        with _tx(ctx) as tx:
            start = len(tx.events)
            if c.kind == "quantity":
                q = tx.state.quantities[c.subject][c.key]
                tx.add(Event.of("quantity_changed", source="correction", rule_id="12.3.4", entity=c.subject,
                                quantity=c.key, delta=int(c.said) - q.current, new_value=int(c.said),
                                reason=f"correction: {c.source} resolved it"))
            else:
                cur = tx.state.facts[fact_id] if fact_id else None
                tx.add(Event.of("fact_set", {"source": "ruling"}, source="correction", rule_id="12.3.4",
                                fact_id=tx.mint(ids.FACT), subject=c.subject, predicate=c.key, value=c.said,
                                visibility=cur.visibility if cur else "shown", supersedes=fact_id))
            rec = _record(c, turn_found=tx.turn_id, kind="record_error", form="oof_note", reliance=[],
                          store_value=value, rewound=[], fact_id=fact_id)
            _log(tx, ctx, c, f"record error: {what} should be {c.said} per {c.source}", rec)
            evs = tx.events[start:]
        return DisputeResult("record_error", [note_block(
            f"The record was wrong: {what} is {c.said}, as {c.source} resolved it (it held {shown}).", "CORRECTION",
            ["Corrected and logged."])], events=evs, claim=c, correction=rec)
    # narration error: the store stands
    relying = _relying(state, c, _last_seq(ctx.store, c.turn_id))
    head = f"Earlier I said {what} was {c.said}; the record has {shown} (your record is right)."
    if relying and choice is None:  # pause point 9: keep, accept forward, or rewind (within the scene)
        choices = [{"id": "accept_forward", "label": "accept it as it stands"},
                   {"id": "rewind", "label": "rewind to before that beat and declare again"}]
        return DisputeResult("narration_error", [note_block(head, "CORRECTION", [f"You acted on it ({relying[0]})."]),
                                                 note_block("Accept it as it stands, or rewind to before that beat?",
                                                            "CHOICE", ["(a) accept forward · (b) rewind"])],
                             choices=choices, claim=c)
    with _tx(ctx) as tx:
        start = len(tx.events)
        reverted: list[int] = []
        if relying and choice == "rewind":
            first = min(state.frames[f].committed_seq for f in relying)
            # the stored DC written just before the frame (01.6.5) belongs to the beat too
            prev = ctx.store.event(first - 1)
            if prev is not None and prev.source in relying:
                first -= 1
            try:
                reverted = _rewind(ctx, tx, first, f"rewind: {what} was misnarrated in {c.turn_id}")
            except Rejected:
                reverted = []
            if reverted:
                void = list(tx.state.meta.get("rolls_voided") or []) + relying
                tx.add(Event.of("meta_set", source="correction", rule_id="12.3.4", key="rolls_voided", value=void))
        rec = _record(c, turn_found=tx.turn_id, kind="narration_error", form="oof_note", reliance=relying,
                      store_value=value, rewound=relying if reverted else [], fact_id=fact_id)
        _log(tx, ctx, c, f"narration error: {what} said {c.said}, store {shown}", rec)
        evs = tx.events[start:]
    if reverted:
        tail = "Rewound to before that beat; its roll is void. Declare again."
    elif relying:
        tail = ("The result stands, corrected around it. Logged." if choice != "rewind" else
                "That can't be rewound cleanly any more; corrected going forward. Logged.")
    else:
        # coarse: 12.3.4 (refunds for spends before the current scene are not computed in M1)
        tail = "You spent nothing because of it. Logged."
    return DisputeResult("narration_error", [note_block(head, "CORRECTION", [tail])], events=evs, reverted=reverted,
                         claim=c, correction=rec)


def dispute(ctx: Any, text: str, *, identify: Identify | None = None,
            choice: Choice | None = None) -> str:  # rule: 12.3.6
    """engine/dm/context.py `DisputeHandler`: the OOF answer text (one or more blocks)."""
    return settle_dispute(ctx, text, identify=identify, choice=choice).text


__all__ = ["DisputeResult", "DisputedClaim", "Identify", "default_identify", "dispute", "settle_dispute"]
