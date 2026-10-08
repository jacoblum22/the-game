"""Disputes and corrections (12.3.6, PR-12-11, PR-12-4; DL-12-84..86): the player says the game erred; the game
answers from the whole transcript, the stored facts' provenance and the frames, never from memory.

    res = settle_dispute(ctx, "Nedwin's coat is grey, not blue")      # locate, gather, decide, deliver, log
    res = settle_dispute(ctx, text, choice="rewind")                  # answer the reliance CHOICE
    text = dispute(ctx, text)                                         # engine/dm/context.py DisputeHandler

PR-12-11: (1) **locate** (`locate`): code pins a turn id, a quote, a name, a number or a frame id against EVERY
turn; when the passage or the category is not pinned, one `Role.LOCATOR` call returns `{turn, quote, category}`
(plus the player's claim restated) and judges nothing; (2) **gather**: the passage and the other turns naming the
subject, the stored value with its provenance (source event, source kind, turn), the frame with a code
recomputation (`recompute`), the claim log; (3) **decide** by PR-12-11's table (first row that fits); (4)
**deliver** a `[CORRECTION]` or `[FIX]` block, with a CHOICE when reliance applies; (5) **log** the dispute record
(meta `corrections`, `type: dispute`) and a block in the save's review log `<save>.disputes.md`.

A correction is a `fact_set` with `source: correction`, `supersedes` and `pinned: true` (never archived; always in
its subject's profile in view). The player's reading wins only on incidental detail slots with nothing on record;
everything else keeps INV-9: only the record decides. Take-backs (12.5.8): within the scene always; past its start
when nothing irreversible followed and at most `corrections.take_back.max_turns_back` turns back.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal

from engine import ids
from engine.dm.oof import FIX_HINT, OofBlock, note_block, when_words
from engine.resolve.rulings import RulingRecord, log_ruling
from engine.store.db import REVERTIBLE, TAKE_BACK_EXTRA, Rejected, Transaction
from engine.store.events import WORLD, Event
from engine.store.projection import WorldState, project

PLAYER_FACING = ("shown", "available")
Choice = Literal["rewind", "accept_forward", "keep"]
DisputeKind = Literal["unclear", "hidden", "not_said", "stands", "narration_error", "record_error", "ruling_stands",
                      "ruling_error", "store_agrees", "mistaken", "player_wins", "unverified", "taken_back", "misread"]
CATEGORIES = ("remembered_wrong", "rule_wrong", "contradiction", "misread", "other")  # = schemas.LOCATE_CATEGORIES
# Resolved sources (12.3.4 step 1): a write from one of these can require a value; narration alone cannot.
RESOLVED = frozenset({"oracle", "generation", "ruling", "data", "player_accepted", "correction"})
# T0/T1a incidental fiction (12.14.13): the lasting look slots. Everything else keeps INV-9.
INCIDENTAL_SLOTS = frozenset({"hair", "face", "mark", "build", "clothing", "worn", "voice", "material", "marking"})
UPHELD = frozenset({"correct", "take_back", "player_reading_wins"})


@dataclass
class DisputedClaim:
    """What the report is about. `kind` fact: `subject`/`key` = a fact's subject and predicate; quantity: an entity
    and a quantity name; ruling: `frame_id` (+ `missed_fact`, a fact the player says was left out); beat: a misread
    beat in `turn_id`. `said` is the player's value (what they hold to be true), `quote` the transcript's words."""

    kind: Literal["fact", "quantity", "ruling", "beat"] = "fact"
    subject: str = ""
    key: str = ""
    said: Any = None
    quote: str = ""
    turn_id: str | None = None
    source: str | None = None  # a resolved source requiring `said` (frame, handler, oracle fact): a record error
    frame_id: str | None = None
    missed_fact: str | None = None
    category: str = "other"
    located_by: str = "code"  # code | model | caller


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
    record: dict[str, Any] | None = None  # the dispute record (12.3.6 item 6)

    @property
    def text(self) -> str:
        return "\n".join(b.text for b in self.blocks)


# ------------------------------------------------------------------------------------------- the transcript


def _turns(store: Any, before: str | None = None, limit: int | None = None) -> list[Any]:  # rule: 12.3.6
    """Turn records newest first: the WHOLE transcript (12.3.6 item 3), optionally only those before `before`."""
    cut = (ids.parse_counter_id(before) or ("", 0))[1] if before else None
    ns = []
    for (t,) in store.conn.execute("SELECT turn_id FROM turns"):
        p = ids.parse_counter_id(t) if isinstance(t, str) else None
        if p and p[0] == ids.TURN and (cut is None or p[1] < cut):
            ns.append(p[1])
    out = [store.turn(ids.counter_id(ids.TURN, k)) for k in sorted(ns, reverse=True)[:limit]]
    # a dispute's own turn (its input the report, its delivery the answer) is not the transcript being checked
    return [t for t in out if t is not None and not (t.parts and all(p.cls == "DISPUTE" for p in t.parts))]


def _norm(s: Any) -> str:
    return " ".join(re.sub(r"[“”\"]", "", str(s)).lower().split())


def _turn_no(turn_id: str | None) -> int:
    p = ids.parse_counter_id(turn_id) if turn_id else None
    return p[1] if p else 0


def _turn_words(turn_id: str | None) -> str:
    return f"turn {_turn_no(turn_id)}" if turn_id else "an earlier turn"


def _excerpt(text: str, needle: str = "", n: int = 160) -> str:
    """The sentence of `text` holding `needle` (else its start), at most `n` characters."""
    flat = " ".join(str(text).split())
    if needle:
        for s in re.split(r"(?<=[.!?])\s+", flat):
            if _norm(needle) in _norm(s):
                return s[:n] + ("…" if len(s) > n else "")
    return flat[:n] + ("…" if len(flat) > n else "")


def _quote(tr: Any, needle: str = "", n: int = 160) -> str:
    return f"{_turn_words(tr.turn_id)}: \"{_excerpt(tr.delivered_verbatim, needle, n)}\""


def _has(text: str, phrase: str) -> bool:
    return bool(phrase) and re.search(rf"(?<![\w-]){re.escape(_norm(phrase))}(?![\w-])", _norm(text)) is not None


def _relevant_exchange(store: Any, words: list[str], current: str | None) -> Any:
    """The latest play turn whose exchange mentions any of `words` (else the latest play turn). Engine turns (the
    opening, a session's open or close, an epilogue: input "(...)") hold where-you-stand lines, not exchanges."""
    turns = [tr for tr in _turns(store, current) if not tr.input_verbatim.startswith("(")]
    for tr in turns:
        hay = (tr.input_verbatim + " " + tr.delivered_verbatim).lower()
        if any(w and w.lower() in hay for w in words):
            return tr
    return turns[0] if turns else None


# ------------------------------------------------------------------------------------------- the store side


def _name(state: WorldState, eid: str) -> str:
    from engine.store.views import display_name

    if eid == WORLD:
        return "the world"
    return display_name(state, eid) if eid in state.entities else eid


def _names_of(state: WorldState, eid: str) -> list[str]:
    """For SEARCHING the transcript only (never shown): how the PC knows them, and the name the narration may have
    used."""
    e = state.entities.get(eid)
    return list(dict.fromkeys([_name(state, eid), *([e.name] if e is not None else [])]))


def _what(state: WorldState, c: DisputedClaim) -> str:
    key = c.key.removeprefix("detail.").replace("_", " ")
    e = state.entities.get(c.subject)
    if e is not None and e.kind == "pc":
        return f"your {key}"
    return f"{_name(state, c.subject)}'s {key}"


def _visible_entity(state: WorldState, eid: str) -> bool:
    if eid == WORLD:
        return True
    e = state.entities.get(eid)
    return e is not None and eid not in state.seals and e.visibility in PLAYER_FACING


def _store_value(state: WorldState, c: DisputedClaim) -> tuple[Any, bool, str | None]:
    """(value, player-facing?, fact id) for the claim's subject and key."""
    from engine.store.views import name_known

    if c.kind == "quantity":
        q = state.quantities.get(c.subject, {}).get(c.key)
        if q is None:
            return None, _visible_entity(state, c.subject), None
        return q.current, q.visibility in PLAYER_FACING and _visible_entity(state, c.subject), None
    if c.key == "name" and c.subject in state.entities:
        e = state.entities[c.subject]
        return e.name, _visible_entity(state, c.subject) and (name_known(state, c.subject) or _same(c.said, e.name)), \
            state.current_fact_id(c.subject, "name")
    fid = state.current_fact_id(c.subject, c.key)
    if fid is None or state.facts[fid].value is None:
        return None, _visible_entity(state, c.subject), None
    f = state.facts[fid]
    ok = f.visibility in PLAYER_FACING and fid not in state.seals and _visible_entity(state, c.subject)
    return f.value, ok, fid


def _same(a: Any, b: Any) -> bool:
    """The player's value and a stored or narrated one agree: equal numbers, or one phrase inside the other."""
    if a is None or b is None:
        return False
    if isinstance(a, int | float) or isinstance(b, int | float):
        try:
            return float(a) == float(b)
        except (TypeError, ValueError):
            return False
    x, y = (re.sub(r"^(?:a|an|the)\s+", "", _norm(v)).rstrip(".") for v in (a, b))
    return bool(x and y) and (x == y or _has(y, x) or _has(x, y))


def _provenance(store: Any, state: WorldState, c: DisputedClaim) -> dict[str, Any] | None:  # rule: 12.3.6
    """The current value's write: {fact_id, seq, source (kind), event_source, turn} (12.3.6 item 3)."""
    if c.kind == "quantity":
        evs = [e for e in store.events(types=["quantity_changed", "quantity_defined"])
               if getattr(e.payload, "entity", None) == c.subject and getattr(e.payload, "quantity", None) == c.key
               and e.seq not in state.reverted]
        if not evs:
            return None
        e = evs[-1]
        return {"fact_id": None, "seq": e.seq, "source": e.type, "event_source": e.source, "turn": e.turn_id,
                "value": getattr(e.payload, "new_value", None)}
    fid = state.current_fact_id(c.subject, c.key)
    if fid is None:
        return None
    f = state.facts[fid]
    ev = store.event(f.valid_from_seq)
    return {"fact_id": fid, "seq": f.valid_from_seq, "source": f.source, "event_source": ev.source if ev else None,
            "turn": ev.turn_id if ev else None, "value": f.value}


def _resolved_earlier(store: Any, state: WorldState, c: DisputedClaim) -> dict[str, Any] | None:  # rule: 12.3.4
    """12.3.4 step 1 for a fact: an earlier version holding the player's value from a resolved source, replaced by an
    unresolved (narration) write: the record was mis-entered. Its fact row, or None."""
    if c.kind != "fact" or c.said is None:
        return None
    cur = state.current_fact_id(c.subject, c.key)
    hist = store.fact_history(c.subject, c.key)
    if not hist or cur is None or state.facts[cur].source in RESOLVED:
        return None
    for row in reversed(hist[:-1]):
        if row["fact_id"] != cur and row["source"] in RESOLVED and _same(c.said, row["value"]):
            return row
    return None


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
    name = _name(state, c.subject).lower() if c.subject else ""
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


def _frame_event(store: Any, frame_id: str | None) -> Event | None:
    if not frame_id:
        return None
    return next((e for e in store.events(types=["frame_committed"])
                 if getattr(e.payload, "frame_id", None) == frame_id), None)


def _beat_start(store: Any, frame_id: str, committed: int) -> int:
    """The beat's first event: the stored DC written just before the frame (01.6.5) belongs to the beat too."""
    prev = store.event(committed - 1)
    return committed - 1 if prev is not None and prev.source == frame_id else committed


# ------------------------------------------------------------------------------------------- recompute (item 4)


def recompute(store: Any, rules: Any, frame: dict[str, Any], committed: int) -> list[str]:  # rule: 12.3.6
    # rule: PR-12-11
    """12.3.6 item 5: the frame's numbers recomputed by code from the rules data and the state just before its commit:
    the DC (a tier from `resolution.dc_tiers` plus the mode's shift; a stored DC from its fact), the modifier
    (attribute, competence, edge, status; the circumstance as recorded, its cited facts on record before the
    declaration) and the odds. Each difference as a line; [] = the frame stands. Opposed DCs are not recomputed."""
    from engine.resolve.frame import attribute_value, competence, fact_usable, status, stored_dc_key
    from engine.resolve.odds import odds

    st = project(store.events(until=committed - 1))
    beat = frame.get("beat") or {}
    actor = st.entities.get(str(beat.get("actor") or ""))
    if actor is None:
        return []
    out: list[str] = []
    shift = int((frame.get("mode_price") or {}).get("dc_shift") or 0)
    dc, src, tier = int(frame.get("dc") or 0), frame.get("dc_source"), frame.get("tier")
    want: int | None = None
    if src == "tier" and tier:
        row = next((t for t in rules.resolution["dc_tiers"] if t["id"] == tier), None)
        want = int(row["dc"]) + shift if row and row.get("dc") is not None else None
    elif src == "stored" and frame.get("obstacle_id"):
        delta = next((d.split(":", 1)[1] for d in frame.get("deltas") or [] if str(d).startswith("dc:")), None)
        fid = st.current_fact_id(WORLD, stored_dc_key(frame["obstacle_id"], frame.get("anchor") or "", delta))
        want = int(st.facts[fid].value) + shift if fid is not None else None
    if want is not None and want != dc:
        out.append(f"DC {dc}, but {src} {tier or 'DC'} gives {want}")
    caps = rules.scales["check_modifier"]["caps"]
    mod = frame.get("modifier") or {}
    attr = str(frame.get("attribute") or "")
    comp, _ = competence(rules, actor, frame.get("deed_tag"))
    edge = min(int(caps["edge"]["max"]), int(actor.data.get("edge", 0) or 0))
    sta = status(rules, st, actor.id, attr, beat.get("verb"), frame.get("traits") or [], [])
    base = min(int(caps["base_pc"]["max"] if actor.kind == "pc" else caps["base_non_pc"]["max"]),
               attribute_value(actor, attr) + comp + edge)
    total = max(int(caps["total"]["min"]), min(int(caps["total"]["max"]), base + int(mod.get("circumstance") or 0)
                                               + sta))
    if total != int(mod.get("total") or 0):
        out.append(f"modifier {int(mod.get('total') or 0):+d}, but the sheet gives {total:+d}")
    declared = int(beat.get("declared_seq") or committed - 1)
    for cite in [*(frame.get("levers") or []), *(frame.get("snags") or [])]:
        if isinstance(cite, dict) and not cite.get("engine") and not fact_usable(st, str(cite.get("fact_id")), declared):
            out.append(f"{cite.get('fact_id')} was cited but was not on record before the declaration")
    got = int((frame.get("odds") or {}).get("success_or_better") or 0)
    o = odds(total, want if want is not None else dc).success_or_better
    if o != got:
        out.append(f"odds {got}%, recomputed {o}%")
    return out


# ------------------------------------------------------------------------------------------- take-backs (item 6)


def _blocked(ctx: Any, from_seq: int, turn_id: str | None) -> str | None:  # rule: 12.5.8
    """12.5.8 item 3: why a take-back past the scene start may not reach `from_seq` (None: it may)."""
    tb = ctx.rules.pacing["corrections"]["take_back"]
    current = getattr(ctx, "turn_id", None)
    if current and turn_id and _turn_no(current) - _turn_no(turn_id) > int(tb["max_turns_back"]):
        return f"it is more than {tb['max_turns_back']} turns back"
    for e in ctx.store.events(since=from_seq - 1):
        p: Any = e.payload
        if e.type == "boundary_marked" and p.boundary in ("session_start", "session_end"):
            return "a session ended since"
        if e.type == "unsealed":
            return "something hidden was revealed since"
        if e.type == "clock_ticked" and p.completed:
            return "a clock completed since"
        if e.type == "fact_set" and (p.predicate in ("dying_step", "setback.dying_entered")
                                     or (p.predicate == "defeated" and "dead" in str(p.value))
                                     or (p.predicate == "exists" and p.value == "dead")):
            return "someone died or fell dying since"
    return None


def _can_rewind(ctx: Any, from_seq: int, turn_id: str | None) -> tuple[bool, str | None]:
    """(may rewind, why not): within the scene always; past its start under 12.5.8's take-back limit."""
    scene = ctx.state.scene
    if scene is None:
        return False, "there is no scene to go back into"
    if from_seq > scene.started_seq:
        return True, None
    why = _blocked(ctx, from_seq, turn_id)
    return why is None, why


def _rewind(ctx: Any, tx: Transaction, from_seq: int, reason: str) -> list[int]:  # rule: 12.3.4
    # rule: 12.5.8
    """`revert_writes` of every revertible write from `from_seq`. Past the scene start (a take-back the caller has
    cleared with `_can_rewind`) the scene change is reverted too, so the PC is back in the beat's scene."""
    scene = tx.state.scene
    if scene is None:
        return []
    take_back = from_seq <= scene.started_seq
    kinds = REVERTIBLE | TAKE_BACK_EXTRA if take_back else REVERTIBLE
    done = set(tx.state.reverted)
    seqs = [e.seq for e in ctx.store.events(since=from_seq - 1) if e.type in kinds and e.seq not in done
            and e.seq is not None and e.source != "correction"]  # the ledger and earlier corrections stay
    if not seqs:
        return []
    tx.add(Event.of("writes_reverted", source="correction", rule_id="12.5.8" if take_back else "12.3.4",
                    reverted=seqs, reason=reason, take_back=take_back))
    return seqs


def _void(tx: Transaction, frames: list[str]) -> None:
    void = list(tx.state.meta.get("rolls_voided") or []) + [f for f in frames if f]
    tx.add(Event.of("meta_set", source="correction", rule_id="12.5.8", key="rolls_voided", value=void))


# ------------------------------------------------------------------------------------------- writes and logs


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


def _record(c: DisputedClaim, *, turn_found: str | None, kind: str, form: str, reliance: list[str],
            store_value: Any, rewound: list[str], fact_id: str | None = None) -> dict[str, Any]:
    return {"turn_of_error": c.turn_id, "turn_found": turn_found, "found_by": "player",
            "claim": {"subject": c.subject, "key": c.key, "said": c.said, "quote": c.quote}, "store_value": store_value,
            "kind": kind, "form": form, "reliance": reliance, "rewound_beats": rewound, "refunds": [],
            "fact_id": fact_id}


def _correct(tx: Transaction, c: DisputedClaim, value: Any, supersedes: str | None, visibility: str = "shown") -> str:
    # rule: 12.3.6
    """The corrective write: `source: correction`, superseding the wrong value, pinned (never archived)."""
    fid = tx.mint(ids.FACT)
    tx.add(Event.of("fact_set", {"source": "correction"}, source="correction", rule_id="12.3.6", fact_id=fid,
                    subject=c.subject, predicate=c.key, value=value, visibility=visibility, supersedes=supersedes,
                    pinned=True))
    return fid


def review_log_path(store: Any) -> Any:
    """`saves/<campaign>.disputes.md`: beside the game file (12.3.6 item 6)."""
    path = getattr(store, "path", None)
    return path.with_name(f"{path.stem}.disputes.md") if path is not None else None


def _log_dispute(tx: Transaction, ctx: Any, text: str, c: DisputedClaim | None, *, outcome: str, answer: str,
                 evidence: list[str], writes: list[int], reverted: list[int]) -> dict[str, Any]:  # rule: 12.3.6
    """12.3.6 item 6: the dispute record in the corrections ledger and a block in the save's review log. A CHOICE
    still open logs `outcome: pending`; the answer replaces that record (same id)."""
    ledger = list(tx.state.meta.get("corrections") or [])
    disputes = [r for r in ledger if isinstance(r, dict) and r.get("type") == "dispute"]
    prior = next((r for r in reversed(disputes) if r.get("outcome") == "pending" and r.get("words") == text), None)
    did = prior["id"] if prior else f"dsp.{len(disputes) + 1}"
    rec = {"type": "dispute", "id": did, "time": when_words(tx.state.time.now), "turn": tx.turn_id, "words": text,
           "category": c.category if c else "other", "located_by": c.located_by if c else "code",
           "passage": {"turn": c.turn_id if c else None, "quote": c.quote if c else ""},
           "evidence": evidence, "outcome": outcome, "upheld": outcome in UPHELD, "writes": writes,
           "reverted": reverted}
    ledger = [rec if r is prior else r for r in ledger] if prior else [*ledger, rec]
    tx.add(Event.of("meta_set", source="correction", rule_id="12.3.6", key="corrections", value=ledger))
    _review_log(ctx.store, rec, answer, resolved=prior is not None)
    return rec


def _review_log(store: Any, rec: dict[str, Any], answer: str, *, resolved: bool) -> None:
    """One markdown block per dispute, newest last, for the owner to read. Wall-clock time lives only here (the
    event log keeps game time, so a replay is identical)."""
    path = review_log_path(store)
    if path is None:
        return
    now = datetime.now().strftime("%Y-%m-%d %H:%M")  # noqa: DTZ005 - the reader's local time; not game state
    head = f"## {rec['id']}{' (resolved)' if resolved else ''} · {rec['turn']} · {now} (game: {rec['time']})"
    p = rec["passage"]
    lines = [head, "", f"- **Player**: \"{rec['words']}\"",
             f"- **Category**: {rec['category']} (located by {rec['located_by']})",
             f"- **Passage**: {p['turn'] or 'none pinned'}" + (f": \"{p['quote']}\"" if p.get("quote") else ""),
             "- **Evidence**:", *(f"  - {e}" for e in rec["evidence"] or ["(none on record)"]),
             f"- **Outcome**: {rec['outcome']}" + (" (upheld)" if rec["upheld"] else ""),
             f"- **Writes**: {', '.join(map(str, rec['writes'])) or 'none'} · **Reverted**: "
             f"{', '.join(map(str, rec['reverted'])) or 'none'}",
             "- **Answer**:", *(f"  > {ln}" for ln in answer.splitlines()), "", ""]
    try:
        new = not path.exists()
        with path.open("a", encoding="utf-8") as fh:
            if new:
                fh.write(f"# Disputes: {path.stem.removesuffix('.disputes')}\n\nEvery /fix or reported error, newest "
                         "last (12.3.6 item 6). Outcomes: correct, take_back, player_reading_wins (upheld); "
                         "explain_with_quote, explain_and_log (the record stands).\n\n")
            fh.write("\n".join(lines))
    except OSError:  # the ledger record is the durable one; a read-only folder must not fail the turn
        pass


def dispute_stats(state: WorldState) -> dict[str, Any]:  # rule: 12.3.6
    """The disputes in the ledger: {all, upheld, by_category} (pacing.yaml#feedback.metric, OEQ-12-24)."""
    recs = [r for r in state.meta.get("corrections") or [] if isinstance(r, dict) and r.get("type") == "dispute"]
    by: dict[str, int] = {}
    for r in recs:
        by[str(r.get("category"))] = by.get(str(r.get("category")), 0) + 1
    return {"all": len(recs), "upheld": sum(1 for r in recs if r.get("upheld")), "by_category": by}


# ------------------------------------------------------------------------------------------- locate (item 2)


_NUM = re.compile(r"(?<![\w.])(\d+)(?![\w.])")
_NUMBER_WORDS = {w: i for i, w in enumerate(("zero one two three four five six seven eight nine ten eleven twelve "
                                             "thirteen fourteen fifteen sixteen seventeen eighteen nineteen "
                                             "twenty").split())}
_QUOTED = re.compile(r"[\"“](.+?)[\"”]")
_STOP = frozenset("the a an his her their my your its this that these those of and or to in on at is was were are "
                  "not but now no it he she they you i me we just only actually really said says".split())


def _number(text: str) -> int | None:
    m = _NUM.search(text)
    if m:
        return int(m.group(1))
    return next((v for w, v in _NUMBER_WORDS.items() if re.search(rf"\b{w}\b", text.lower())), None)


def _named(state: WorldState, text: str) -> list[str]:
    """Entities the report names (full name, alias, or a unique first name), in order of mention; visible only."""
    low = text.lower()
    keys: dict[str, set[str]] = {}
    for eid, e in state.entities.items():
        if not _visible_entity(state, eid) or e.kind in ("thread", "rumor", "clue"):
            continue
        names = {e.name, *(a for a in e.data.get("aliases") or [] if isinstance(a, str))}
        names |= {n.split()[0] for n in list(names) if " " in n and len(n.split()[0]) >= 4}
        for n in names:
            if len(n) >= 3:
                keys.setdefault(n.lower(), set()).add(eid)
    hits: list[tuple[int, str]] = []
    for key in sorted(keys, key=len, reverse=True):
        if len(keys[key]) != 1:
            continue
        m = re.search(rf"(?<![\w]){re.escape(key)}(?![\w])", low)
        if m:
            hits.append((m.start(), next(iter(keys[key]))))
            low = low[:m.start()] + " " * len(key) + low[m.end():]
    return list(dict.fromkeys(eid for _, eid in sorted(hits)))


def _slot(word: str, kind: str | None, rules: Any) -> str | None:
    from engine.store.details import slot_of

    return slot_of(word, rules, kind)


def _value_near(text: str, word: str) -> str | None:
    """The player's value for `word`: "<word> is/was <value>" or "<value> <word>"."""
    m = re.search(rf"\b{re.escape(word)}\b\s+(?:is|was|were|are|should be)\s+(?:actually\s+|really\s+)?"
                  r"([\w'-]+(?:\s+[\w'-]+){0,2}?)(?=\s*(?:[,.;!?]|$|\s(?:not|but|and|now|you|i|when|in|before|earlier|"
                  r"then|again|yesterday|today|at|on)\b))",
                  text, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    m = re.search(rf"((?:[\w'-]+\s+){{1,2}}){re.escape(word)}\b", text, re.IGNORECASE)
    if m:
        words = [w for w in m.group(1).split() if w.lower() not in _STOP and not w.lower().endswith("'s")
                 and not w[:1].isupper()]
        return " ".join(words) or None
    return None


def _claim_from(ctx: Any, text: str, subject_hint: str = "", key_hint: str = "", value_hint: str = "",
                ) -> DisputedClaim:
    """Code's reading of the report's claim: subject, key and the player's value (12.3.6; the locator fills gaps)."""
    state: WorldState = ctx.state
    low = text.lower()
    pc = next((eid for eid, e in state.entities.items() if e.kind == "pc" and e.exists == "exists"), None)
    for k, fid in state.fact_keys.items():  # an explicit `subject.predicate` (a front end, the turn record)
        subj, pred = k.split("|", 1)
        if f"{subj}.{pred}".lower() in low and state.facts[fid].visibility in PLAYER_FACING:
            return DisputedClaim(subject=subj, key=pred, said=_value_near(text, f"{subj}.{pred}"))
    named = _named(state, text) or (_named(state, subject_hint) if subject_hint else [])
    c = DisputedClaim()
    subjects = [*named, *([pc] if pc else [])]
    # a quantity of a named entity, or the PC's ("my vitality", "I had 3 torches")
    for eid in subjects:
        for qname, q in (state.quantities.get(eid) or {}).items():
            word = qname.replace("_", " ").lower()
            if q.visibility in PLAYER_FACING and re.search(rf"\b{re.escape(word)}s?\b", low + " " + key_hint.lower()):
                n = _number(text) if _number(text) is not None else _number(value_hint)
                return DisputedClaim(kind="quantity", subject=eid, key=qname, said=n)
    mine = bool(re.search(r"\b(?:i|my|me)\b", low))
    has = re.search(r"\b(?:i|my character)\s+(?:had|have|has|carry|carried|am carrying|was carrying|hold|held|own|"
                    r"still have|still had)\s+(.+?)(?=[,.;!?]|$|\s(?:but|and|not|you)\b)", low)
    if pc and has and all(state.entities[e].kind == "item" for e in named):  # a possession (mechanical, INV-9)
        said = re.sub(r"^(?:my|a|an|the|some|still)\s+", "", has.group(1).strip())
        return DisputedClaim(subject=pc, key="carries", said=said)
    for eid in named or ([pc] if pc and mine else []):
        kind = state.entities[eid].kind
        if re.search(r"\bname\b", low):
            m = re.search(r"\bname (?:is|was)\s+([A-Z][\w'-]+(?:\s+[A-Z][\w'-]+)*)", text)
            return DisputedClaim(subject=eid, key="name", said=m.group(1) if m else state.entities[eid].name)
        for w in [*re.findall(r"[a-z]+", low), *re.findall(r"[a-z]+", key_hint.lower())]:
            slot = _slot(w, kind, ctx.rules)
            if slot:
                said = _value_near(text, w) or value_hint or None
                if said and not _has(said, w):
                    said = f"{said} {w}"
                return DisputedClaim(subject=eid, key=f"detail.{slot}", said=said)
        for key, fid in state.fact_keys.items():
            subj, pred = key.split("|", 1)
            words = pred.replace("_", " ").replace(".", " ").lower()
            if subj == eid and len(words) > 3 and words in low and state.facts[fid].visibility in PLAYER_FACING:
                return DisputedClaim(subject=eid, key=pred, said=_value_near(text, words.split()[-1]) or None)
    if named:
        c.subject = named[0]
    return c


def _pins(ctx: Any, text: str, c: DisputedClaim, current: str | None) -> None:  # rule: PR-12-11
    """Step 1 `[D]`: a turn id, a frame id, a fact id or a quoted phrase pins the passage."""
    store = ctx.store
    low = text.lower()
    m = re.search(r"\bturn[ .#]?(\d+)\b", low)
    if m and store.turn(f"turn.{m.group(1)}") is not None:
        c.turn_id = f"turn.{m.group(1)}"
    frame = re.search(r"\bframe\.\d+\b", low)
    if frame:
        c.kind, c.frame_id, c.category = "ruling", frame.group(0), "rule_wrong"
        fact = re.search(r"\bfact\.\d+\b", low)
        c.missed_fact = fact.group(0) if fact else None
        ev = _frame_event(store, c.frame_id)
        c.turn_id = c.turn_id or (ev.turn_id if ev else None)
    q = _QUOTED.search(text)
    if q:
        c.quote = q.group(1).strip()
        if not c.turn_id:
            for tr in _turns(store, current):
                if _has(tr.delivered_verbatim, c.quote) or _has(tr.input_verbatim, c.quote):
                    c.turn_id = tr.turn_id
                    break


def _candidates(ctx: Any, c: DisputedClaim, text: str, current: str | None, k: int = 12) -> list[Any]:
    """The locate call's candidates: this scene's turns first, then turns anywhere that mention what the report
    names (whole transcript)."""
    store, state = ctx.store, ctx.state
    start = state.scene.started_seq if state.scene else 0
    turns = [tr for tr in _turns(store, current) if not tr.input_verbatim.startswith("(")]
    here = [tr for tr in turns if _last_seq(store, tr.turn_id) > start]
    words = [w for w in {*re.findall(r"[a-z]{4,}", text.lower()),
                         *(n.lower() for n in (_names_of(state, c.subject) if c.subject else []))} if w not in _STOP]
    hits = [tr for tr in turns if tr not in here
            and any(w in (tr.input_verbatim + " " + tr.delivered_verbatim).lower() for w in words)]
    return [*here[:k // 2], *hits][:k]


def _ask_locator(ctx: Any, text: str, cands: list[Any]) -> dict[str, Any]:  # rule: PR-12-11
    """Step 1 `[J:enum]`: one call reads the report and the candidate turns; returns {turn, quote, category} and
    the player's claim restated. It judges nothing else."""
    from engine.dm.roles.prompts import load_prompt
    from engine.dm.schemas import locator_schema
    from engine.llm.base import Packet, Role, call_role

    lines = [f'THE PLAYER\'S REPORT: "{" ".join(text.split())}"', "CANDIDATE TURNS (this scene first, then search "
             "hits):"]
    lines += [f'{tr.turn_id} | player: "{" ".join(tr.input_verbatim.split())[:160]}" | game: '
              f'"{" ".join(tr.delivered_verbatim.split())[:400]}"' for tr in cands]
    packet = Packet(instructions=load_prompt("locator"), core="", cards=[], view="", exchanges=[],
                    message="\n".join(lines))
    res = call_role(ctx.model, Role.LOCATOR, locator_schema([tr.turn_id for tr in cands]), packet,
                    turn_id=getattr(ctx, "turn_id", None), recorder=getattr(ctx, "record_call", None),
                    default={"turn": "none", "quote": "", "category": "other", "subject": "", "key": "",
                             "value": ""})
    return dict(res.data)


def locate(ctx: Any, text: str, *, model: bool = True) -> DisputedClaim | None:  # rule: PR-12-11
    # rule: 12.3.6
    """PR-12-11 step 1. Code first (`[D]`): ids, quotes and names against every turn, and the claim's subject, key
    and value. The category is code's only from structural markers (a frame or fact id: rule_wrong); otherwise, or
    when no passage is pinned, ONE locator call (`model=False`: code only). None: nothing to go on."""
    current = getattr(ctx, "turn_id", None)
    c = _claim_from(ctx, text)
    _pins(ctx, text, c, current)
    if c.kind == "fact" and c.subject and c.key and not c.turn_id:  # the latest turn saying the subject or value
        names = _names_of(ctx.state, c.subject)
        words = [c.key.removeprefix("detail."), *(w for w in re.findall(r"[a-z]{4,}", str(c.said or "").lower()))]
        for tr in _turns(ctx.store, current):
            hay = tr.delivered_verbatim
            if (c.said is not None and _has(hay, str(c.said))) or (any(_has(hay, n) for n in names) and any(
                    _has(hay, w) for w in words)):
                c.turn_id = tr.turn_id
                break
    if model and (c.turn_id is None or c.category == "other") and c.kind != "ruling":
        cands = _candidates(ctx, c, text, current)
        if cands:
            got = _ask_locator(ctx, text, cands)
            if got.get("category") in CATEGORIES:
                c.category = str(got["category"])
            if not c.turn_id and got.get("turn") in {tr.turn_id for tr in cands}:
                c.turn_id, c.located_by = str(got["turn"]), "model"
                tr = ctx.store.turn(c.turn_id)
                q = str(got.get("quote") or "").strip()
                if q and tr is not None and (_has(tr.delivered_verbatim, q) or _has(tr.input_verbatim, q)):
                    c.quote = c.quote or q  # the call's quote is kept only when the turn holds it
            if not c.key and (got.get("subject") or got.get("key")):
                filled = _claim_from(ctx, text, str(got.get("subject") or ""), str(got.get("key") or ""),
                                     str(got.get("value") or ""))
                if filled.key:
                    c.kind, c.subject, c.key, c.said = filled.kind, filled.subject, filled.key, filled.said
    if c.category == "other" and c.key and c.kind == "fact":
        c.category = "remembered_wrong"  # a named fact or name: the label only (outcomes follow the evidence)
    if c.category == "misread" and not c.key and c.kind != "ruling":
        c.kind = "beat"
    if not (c.turn_id or c.subject or c.frame_id):
        return None
    return c


def default_identify(ctx: Any, text: str) -> DisputedClaim | None:  # rule: 12.3.6
    """Code only (no model call): `locate(..., model=False)`."""
    return locate(ctx, text, model=False)


# ------------------------------------------------------------------------------------------- the outcomes


def _done(tx: Transaction, ctx: Any, text: str, c: DisputedClaim | None, kind: DisputeKind, blocks: list[OofBlock],
          *, outcome: str, evidence: list[str], start: int, reverted: list[int] | None = None,
          correction: dict[str, Any] | None = None, choices: list[dict[str, str]] | None = None) -> DisputeResult:
    """Every answer ends here: the dispute record and its review-log block (12.3.6 item 6), then the result."""
    writes = [e.seq for e in tx.events[start:] if e.seq is not None]
    answer = "\n".join(b.text for b in blocks)
    rec = _log_dispute(tx, ctx, text, c, outcome=outcome, answer=answer, evidence=evidence, writes=writes,
                       reverted=list(reverted or []))
    return DisputeResult(kind, blocks, events=tx.events[start:], reverted=list(reverted or []),
                         choices=list(choices or []), claim=c, correction=correction, record=rec)


def _evidence_fact(state: WorldState, prov: dict[str, Any] | None, c: DisputedClaim) -> list[str]:
    if prov is None:
        return [f"{c.subject} {c.key}: nothing on record"]
    return [f"{prov['fact_id'] + ' ' if prov.get('fact_id') else ''}{c.subject} {c.key} = {prov.get('value')!r} (source "
            f"{prov['source']}, event {prov['seq']} from {prov['event_source']}, {prov['turn']})"]


def _ruling(ctx: Any, text: str, c: DisputedClaim, choice: Choice | None) -> DisputeResult:  # rule: 12.3.6
    # rule: PR-12-11
    """A disputed ruling: recompute the frame (item 4) and check a fact the player says was left out. A difference
    is a ruling error with reliance true for that beat: accept forward, or take it back (within the scene, or past
    its start under 12.5.8's limit); otherwise the frame stands, shown with its numbers and cited facts."""
    state: WorldState = ctx.state
    ev = _frame_event(ctx.store, c.frame_id)
    if ev is None and c.turn_id:  # the passage's beat
        ev = next((e for e in ctx.store.events(types=["frame_committed"]) if e.turn_id == c.turn_id), None)
        c.frame_id = getattr(ev.payload, "frame_id", None) if ev else None
    with _tx(ctx) as tx:
        start = len(tx.events)
        if ev is None:
            return _done(tx, ctx, text, c, "unclear", [note_block(
                f"No committed frame {c.frame_id or 'in that turn'} on record: nothing was rolled there. Logged.",
                "FIX")], outcome="explain_and_log", evidence=["no frame_committed"], start=start)
        frame: dict[str, Any] = ev.payload.frame  # type: ignore[attr-defined]
        committed = int(ev.seq or 0)
        c.turn_id = c.turn_id or ev.turn_id
        cited = [x.get("fact_id") for x in (frame.get("levers") or []) + (frame.get("snags") or [])
                 if isinstance(x, dict)]
        pct = (frame.get("odds") or {}).get("success_or_better")
        summary = (f"{frame.get('attribute')}, {frame.get('tier') or frame.get('dc_source')} DC {frame.get('dc')}, "
                   f"modifier {int((frame.get('modifier') or {}).get('total') or 0):+d}"
                   + (f", {pct}% to succeed" if pct is not None else "") + f", stakes {frame.get('stakes')}, reach "
                   f"{frame.get('reach')}; cited: {', '.join(x for x in cited if x) or 'nothing'}")
        diffs = recompute(ctx.store, ctx.rules, frame, committed)
        f = state.facts.get(c.missed_fact or "")
        if (f is not None and f.visibility in PLAYER_FACING and c.missed_fact not in cited
                and f.valid_from_seq < committed):
            diffs.append(f"{c.missed_fact} ({f.subject} {f.predicate} = {f.value}) was on record and was left out")
        evidence = [f"{c.frame_id} ({ev.turn_id}, event {committed}): {summary}",
                    *(f"recomputed: {d}" for d in diffs or ["matches"])]
        if not diffs:
            why = (f"{c.missed_fact} is already cited" if c.missed_fact and c.missed_fact in cited else
                   f"{c.missed_fact} was not on record before that roll" if c.missed_fact else
                   "recomputed from the rules and the record, it comes out the same")
            return _done(tx, ctx, text, c, "ruling_stands", [note_block(
                f"That roll stands ({_turn_words(ev.turn_id)}): {summary}.", "FIX", [f"{why.capitalize()}. Logged."])],
                outcome="explain_with_quote", evidence=evidence, start=start)
        desc = f"The roll in {_turn_words(ev.turn_id)} was framed wrong: {'; '.join(diffs)}."
        first = _beat_start(ctx.store, c.frame_id or "", committed)
        ok, why_not = _can_rewind(ctx, first, ev.turn_id)
        if ok and choice is None:
            choices = [{"id": "accept_forward", "label": "accept the result as it stands"},
                       {"id": "rewind", "label": "take that beat back and declare again"}]
            return _done(tx, ctx, text, c, "ruling_error", [note_block(desc, "CORRECTION", [summary]), note_block(
                "Accept the result as it stands, or take that beat back?", "CHOICE",
                ["(a) accept forward · (b) take it back"])], outcome="pending", evidence=evidence, start=start,
                choices=choices)
        reverted: list[int] = []
        if ok and choice == "rewind":
            try:
                reverted = _rewind(ctx, tx, first, f"ruling error in {c.frame_id}: {'; '.join(diffs)}")
            except Rejected:
                reverted = []
            if reverted:
                _void(tx, [c.frame_id or ""])
        rec = _record(c, turn_found=tx.turn_id, kind="ruling_error", form="oof_note", reliance=[c.frame_id or ""],
                      store_value=None, rewound=[c.frame_id or ""] if reverted else [], fact_id=c.missed_fact)
        _log(tx, ctx, c, desc, rec, frame_id=c.frame_id)
        tail = ("Taken back: that beat is undone and its roll is void. Declare again." if reverted else
                "The result stands and is corrected going forward. Logged." if ok else
                f"It can't be taken back ({why_not}): corrected going forward. Logged.")
        return _done(tx, ctx, text, c, "ruling_error", [note_block(desc, "CORRECTION", [tail])],
                     outcome="take_back" if reverted else "correct", evidence=evidence, start=start,
                     reverted=reverted, correction=rec)


_STEM_STOP = frozenset("that this with from didn just only meant said what have they them then into never wanted "
                       "would were your there about something anything nothing want tried trying read thought "
                       "wasn doesn don".split())


def _stems(text: str) -> set[str]:
    return {w[:4] for w in re.findall(r"[a-z]{4,}", text.lower()) if w not in _STEM_STOP}


def _misread(ctx: Any, text: str, c: DisputedClaim) -> DisputeResult:  # rule: 12.5.8
    # rule: PR-12-11
    """PR-12-11's misread row (12.5.8 item 2): the beat resolved on a reading the player never saw (an auto-committed
    OFFER, or no roll at all) and the report's words are the player's own words at that turn, not the reading's:
    take it back (writes reverted, rolls void) and the player declares again. Otherwise the answer quotes both."""
    store = ctx.store
    tr = store.turn(c.turn_id) if c.turn_id else None
    with _tx(ctx) as tx:
        start = len(tx.events)
        if tr is None:
            return _done(tx, ctx, text, c, "unclear", [note_block(
                "Which action? Name the turn (/turn shows them) and I check how it was read.", "FIX")],
                outcome="explain_and_log", evidence=["no turn pinned"], start=start)
        frames = [e for e in store.events(types=["frame_committed"]) if e.turn_id == tr.turn_id]
        reading = " ".join(str((e.payload.frame.get("beat") or {}).get("restatement") or "")  # type: ignore[attr-defined]
                           for e in frames) or _excerpt(tr.delivered_verbatim, n=120)
        unseen = (any(e.payload.frame.get("offer_choice") == "auto" for e in frames)  # type: ignore[attr-defined]
                  or (not frames and bool(tr.writes)))
        support = (_stems(text) & _stems(tr.input_verbatim)) - _stems(reading)
        evidence = [f"{tr.turn_id} input: \"{tr.input_verbatim}\"", f"read as: \"{reading}\"",
                    f"OFFER shown: {'no' if unseen else 'yes'}", f"report words in the input, not the reading: "
                    f"{sorted(support) or 'none'}"]
        if not (unseen and support):
            why = ("the OFFER showed that reading before the roll" if not unseen else
                   "your words then match the reading")
            return _done(tx, ctx, text, c, "stands", [note_block(
                f"As recorded: {_turn_words(tr.turn_id)}, you wrote \"{tr.input_verbatim}\"; it was read as "
                f"\"{reading}\".", "FIX", [f"It stands: {why}. Logged."])],
                outcome="explain_with_quote", evidence=evidence, start=start)
        seqs = [s for s in tr.writes if s not in tx.state.reverted]
        first = min([*seqs, *(_beat_start(store, e.payload.frame_id, int(e.seq or 0))  # type: ignore[attr-defined]
                              for e in frames)], default=0)
        ok, why_not = _can_rewind(ctx, first, tr.turn_id) if first else (False, "it changed nothing")
        reverted: list[int] = []
        if ok:
            try:
                reverted = _rewind(ctx, tx, first, f"misread beat in {tr.turn_id}: {text[:120]}")
            except Rejected as e:
                ok, why_not = False, f"later events depend on it ({e})"
        if reverted:
            _void(tx, [str(e.payload.frame_id) for e in frames])  # type: ignore[attr-defined]
            rec = _record(c, turn_found=tx.turn_id, kind="misread", form="oof_note", reliance=[],
                          store_value=None, rewound=[str(e.payload.frame_id) for e in frames])  # type: ignore[attr-defined]
            _log(tx, ctx, c, f"misread beat in {tr.turn_id}", rec)
            return _done(tx, ctx, text, c, "taken_back", [note_block(
                f"Taken back: \"{reading}\" ({_turn_words(tr.turn_id)}) was a misreading; it is undone"
                + (" and its roll is void" if frames else "") + ".", "CORRECTION", ["Declare again."])],
                outcome="take_back", evidence=evidence, start=start, reverted=reverted, correction=rec)
        return _done(tx, ctx, text, c, "misread", [note_block(
            f"You're right that \"{reading}\" ({_turn_words(tr.turn_id)}) misread you, but it can't be taken back "
            f"({why_not}).", "CORRECTION", ["It stands; logged for review."])],
            outcome="explain_and_log", evidence=evidence, start=start)


def _said_in(store: Any, state: WorldState, c: DisputedClaim, current: str | None) -> Any:
    """The latest turn whose narration said the player's value about the subject (the passage first)."""
    if c.said is None:
        return None
    core = str(c.said)
    word = c.key.removeprefix("detail.")
    if c.key.startswith("detail.") and " " in core:
        core = core.rsplit(" ", 1)[0]  # "grey coat" -> "grey" (the narration may say "a coat of grey")
    names = _names_of(state, c.subject) if c.subject else []
    turns = _turns(store, current)
    if c.turn_id:
        turns = sorted(turns, key=lambda t: t.turn_id != c.turn_id)
    for tr in turns:
        hay = tr.delivered_verbatim
        if c.kind == "quantity":
            if _has(hay, str(c.said)) and _has(hay, c.key.replace("_", " ")):
                return tr
        elif _has(hay, core) and (not names or any(_has(hay, n) for n in names) or _has(hay, word)
                                  or tr.turn_id == c.turn_id or (c.quote and _has(hay, c.quote))):
            return tr
    return None


def _fact(ctx: Any, text: str, c: DisputedClaim, choice: Choice | None) -> DisputeResult:  # rule: PR-12-11
    # rule: 12.3.6
    """PR-12-11's table for a fact or a quantity, first row that fits (step 3)."""
    state: WorldState = ctx.state
    store = ctx.store
    current = getattr(ctx, "turn_id", None)
    what = _what(state, c)
    value, facing, fact_id = _store_value(state, c)
    prov = _provenance(store, state, c)
    evidence = _evidence_fact(state, prov, c)
    held = ""
    if c.key == "carries" and isinstance(value, list):  # a possession: the item the player names, if carried
        names = [state.entities[i].name if i in state.entities else str(i) for i in value]
        held = ", ".join(names)
        value = next((n for n in names if _same(c.said, n)), None)
        what = f"your {c.said}" if c.said else "what you carry"
    with _tx(ctx) as tx:
        start = len(tx.events)
        if not facing:  # 00.6.4: background and sealed state is never shown; the objection is logged for review
            rec = _record(c, turn_found=tx.turn_id, kind="unverified", form="oof_note", reliance=[], store_value=None,
                          rewound=[])
            _log(tx, ctx, c, f"player disputes {what}; not player-facing", rec)
            return _done(tx, ctx, text, c, "hidden", [note_block(
                "Your character can't check that from here, so I can't show the record. Your objection is logged for "
                "review.", "UNKNOWN")], outcome="explain_and_log", evidence=["not player-facing"], start=start,
                correction=rec)
        prov_tr = store.turn(prov["turn"]) if prov and prov.get("turn") else None
        said_tr = _said_in(store, state, c, current)
        if said_tr is not None:
            evidence.append(f"said in {said_tr.turn_id}: \"{_excerpt(said_tr.delivered_verbatim, str(c.said))}\"")
        names = _names_of(state, c.subject) if c.subject else []
        others = [tr.turn_id for tr in _turns(store, current) if any(_has(tr.delivered_verbatim, n) for n in names)][:8]
        if others:
            evidence.append("turns naming the subject: " + ", ".join(others))
        turns_seen = {c.turn_id, str(prov.get("turn")) if prov else None}  # spec 011's claim log, when present
        claims = [x for x in state.meta.get("claim_log") or [] if isinstance(x, dict) and x.get("turn") in turns_seen]
        evidence += [f"claim log {x.get('turn')}: {x.get('class')} {x.get('verdict')}: {x.get('sentence')}"
                     for x in claims[:4]]
        # row: a resolved source in the log requires the player's value -> record error (pinned corrective write)
        earlier = _resolved_earlier(store, state, c)
        if earlier is not None or (c.said is not None and _source_exists(store, state, c.source)
                                   and not _same(c.said, value)):
            src = earlier["source"] if earlier else c.source
            if c.kind == "quantity":
                q = tx.state.quantities[c.subject][c.key]
                tx.add(Event.of("quantity_changed", source="correction", rule_id="12.3.4", entity=c.subject,
                                quantity=c.key, delta=int(c.said) - q.current, new_value=int(c.said),
                                reason=f"correction: {c.source} resolved it"))
                new_id = None
            else:
                cur = tx.state.facts.get(fact_id or "")
                new_id = _correct(tx, c, c.said if earlier is None else earlier["value"], fact_id,
                                  cur.visibility if cur else "shown")
            ev_turn = store.event(int(earlier["valid_from_seq"])).turn_id if earlier else None
            seen = store.turn(ev_turn) if ev_turn else None
            evidence.append(f"resolved earlier: {earlier['fact_id']} = {earlier['value']!r} (source {src}, event "
                            f"{earlier['valid_from_seq']})" if earlier else f"resolved source: {c.source}")
            rec = _record(c, turn_found=tx.turn_id, kind="record_error", form="oof_note", reliance=[],
                          store_value=value, rewound=[], fact_id=new_id or fact_id)
            _log(tx, ctx, c, f"record error: {what} should be {c.said} per {src}", rec)
            where = f" ({_quote(seen, str(c.said))})" if seen is not None and _has(seen.delivered_verbatim,
                                                                                   str(c.said)) else ""
            return _done(tx, ctx, text, c, "record_error", [note_block(
                f"You're right: {what} is {c.said if earlier is None else earlier['value']}{where}; the record had "
                f"slipped to {value}.", "CORRECTION", ["Fixed; it stays."])],
                outcome="correct", evidence=evidence, start=start, correction=rec)
        if value is not None:
            shown = str(value)
            # the turn that set it, quoted where it says the value (a quantity's turn always: its numbers are OOF)
            says = prov_tr is not None and (_has(prov_tr.delivered_verbatim, shown) or (
                c.kind == "quantity" and prov_tr.delivered_verbatim.strip() != ""))
            src_line = (_quote(prov_tr, shown) if says else  # type: ignore[union-attr]
                        f"on record since {_turn_words(prov['turn'])}" if prov and prov.get("turn") else "on record")
            if c.said is None:  # nothing claimed: show what the record went by
                return _done(tx, ctx, text, c, "stands", [note_block(
                    f"As recorded: {what} is {shown} ({src_line}).", "FIX", ["Logged."])],
                    outcome="explain_with_quote", evidence=evidence, start=start)
            if _same(c.said, value):  # the store holds what the player says: narration error or omission
                if c.key == "name" and fact_id and said_tr is not None:
                    from engine.store.views import name_known

                    pc = next((e for e, x in state.entities.items() if x.kind == "pc" and x.exists == "exists"), None)
                    if pc and not name_known(state, c.subject):  # the name was told: the PC knows it now
                        tx.add(Event.of("knowledge_recorded", source="correction", rule_id="12.10.2", knower=pc,
                                        fact_id=fact_id, how="told"))
                said_where = (f" ({_quote(said_tr, str(c.said))})" if said_tr is not None else f" ({src_line})")
                rec = _record(c, turn_found=tx.turn_id, kind="narration_error", form="oof_note", reliance=[],
                              store_value=value, rewound=[], fact_id=fact_id)
                _log(tx, ctx, c, f"narration error or omission: {what} is {shown}", rec)
                head = (f"You're right: you carry {shown} (on record)." if c.key == "carries" else
                        f"You're right: {what} is {shown}{said_where}.")
                return _done(tx, ctx, text, c, "store_agrees", [note_block(head, "CORRECTION",
                    ["The record has it; the narration slipped. Logged."])],
                    outcome="correct", evidence=evidence, start=start, correction=rec)
            if said_tr is not None:  # the narration said the player's value, the store holds another: store wins
                c.turn_id = c.turn_id or said_tr.turn_id
                return _narration_error(ctx, tx, text, c, value, fact_id, choice, evidence, start)
            return _done(tx, ctx, text, c, "mistaken", [note_block(
                f"As recorded: {what} is {shown} ({src_line}).", "FIX",
                [f"{c.said} was never said. Logged."])],
                outcome="explain_with_quote", evidence=evidence, start=start)
        # nothing on record: uncertain evidence
        slot = c.key.removeprefix("detail.") if c.key.startswith("detail.") else ""
        if slot in INCIDENTAL_SLOTS and c.said is not None and c.kind == "fact":
            # incidental fiction (T0, T1a): the player's reading wins, as an Oracle "Certain" (00.6.7)
            new_id = _correct(tx, c, c.said, None)
            rec = _record(c, turn_found=tx.turn_id, kind="player_reading", form="oof_note", reliance=[],
                          store_value=None, rewound=[], fact_id=new_id)
            _log(tx, ctx, c, f"player's reading accepted: {what} is {c.said}", rec)
            return _done(tx, ctx, text, c, "player_wins", [note_block(
                f"You're right: {what} is {c.said}.", "CORRECTION", ["Fixed; it stays."])],
                outcome="player_reading_wins", evidence=evidence, start=start, correction=rec)
        # mechanics or consequential content, uncertain: the record decides (INV-9)
        rec = _record(c, turn_found=tx.turn_id, kind="unverified", form="oof_note", reliance=[], store_value=None,
                      rewound=[])
        _log(tx, ctx, c, f"unverified mechanical claim: {what} {c.said}", rec)
        held = held or (_holdings(state, c.subject) if c.subject else "")
        never = (f" and no turn says {c.said}" if c.said is not None and said_tr is None and c.key != "carries"
                 else f" ({_quote(said_tr, str(c.said))})" if said_tr is not None else "")
        return _done(tx, ctx, text, c, "unverified", [note_block(
            f"The record has nothing for {what}" + (f" (it holds: {held})" if held else "") + never + ".", "FIX",
            ["Without a record I can't change it; logged for review."])],
            outcome="explain_and_log", evidence=evidence, start=start, correction=rec)


def _holdings(state: WorldState, eid: str) -> str:
    """What the record holds that a mechanical claim could be about: the entity's shown quantities."""
    qs = state.quantities.get(eid) or {}
    return ", ".join(f"{k.replace('_', ' ')} {q.current}" for k, q in qs.items() if q.visibility in PLAYER_FACING)


def _narration_error(ctx: Any, tx: Transaction, text: str, c: DisputedClaim, value: Any, fact_id: str | None,
                     choice: Choice | None, evidence: list[str], start: int) -> DisputeResult:  # rule: 12.3.4
    """The narration said one thing and the store holds another: the store wins (12.3.4), with the reliance CHOICE
    for this scene's beats that rested on it."""
    state: WorldState = ctx.state
    what = _what(state, c)
    relying = _relying(state, c, _last_seq(ctx.store, c.turn_id))
    head = f"Earlier I said {what} was {c.said}; the record has {value}."
    if relying and choice is None:  # pause point 9: keep, accept forward, or rewind (within the scene)
        choices = [{"id": "accept_forward", "label": "accept it as it stands"},
                   {"id": "rewind", "label": "rewind to before that beat and declare again"}]
        return _done(tx, ctx, text, c, "narration_error", [
            note_block(head, "CORRECTION", [f"You acted on it ({_turn_words(c.turn_id)})."]),
            note_block("Accept it as it stands, or rewind to before that beat?", "CHOICE",
                       ["(a) accept forward · (b) rewind"])], outcome="pending", evidence=evidence, start=start,
            choices=choices)
    reverted: list[int] = []
    if relying and choice == "rewind":
        first = min(_beat_start(ctx.store, f, state.frames[f].committed_seq) for f in relying)
        try:
            reverted = _rewind(ctx, tx, first, f"rewind: {what} was misnarrated in {c.turn_id}")
        except Rejected:
            reverted = []
        if reverted:
            _void(tx, relying)
    rec = _record(c, turn_found=tx.turn_id, kind="narration_error", form="oof_note", reliance=relying,
                  store_value=value, rewound=relying if reverted else [], fact_id=fact_id)
    _log(tx, ctx, c, f"narration error: {what} said {c.said}, store {value}", rec)
    if reverted:
        tail = "Rewound to before that beat; its roll is void. Declare again."
    elif relying:
        tail = ("The result stands, corrected around it. Logged." if choice != "rewind" else
                "That can't be rewound cleanly any more; corrected going forward. Logged.")
    else:
        # coarse: 12.3.4 (refunds for spends before the current scene are not computed in M1)
        tail = "You spent nothing because of it. Logged."
    return _done(tx, ctx, text, c, "narration_error", [note_block(head, "CORRECTION", [tail])],
                 outcome="take_back" if reverted else "correct", evidence=evidence, start=start, reverted=reverted,
                 correction=rec)


def settle_dispute(ctx: Any, text: str, *, identify: Identify | None = None,
                   choice: Choice | None = None) -> DisputeResult:  # rule: 12.3.6
    # rule: PR-12-11
    """PR-12-11 from the whole transcript and the store. `ctx`: anything with `store`, `state`, `rules`, optional
    `tx` (the turn's open transaction; else a one-shot transaction), `model` and `record_call` (the locate call).
    `identify` (tests, a front end) replaces `locate`."""
    c = identify(ctx, text) if identify else locate(ctx, text, model=getattr(ctx, "model", None) is not None)
    if c is None:
        tr = _relevant_exchange(ctx.store, [], getattr(ctx, "turn_id", None))
        rest = [f"From the turn log — {_quote(tr)}"] if tr else []
        with _tx(ctx) as tx:
            return _done(tx, ctx, text, None, "unclear", [note_block(
                "Which statement, and when? Name what was said (and the turn if you can); I check it against the "
                "record.", "FIX", rest)], outcome="explain_and_log", evidence=["nothing pinned"],
                start=len(tx.events))
    if c.kind == "ruling" or (c.category == "rule_wrong" and c.turn_id and not c.key):
        return _ruling(ctx, text, c, choice)
    if c.kind == "beat":
        return _misread(ctx, text, c)
    if c.subject and c.key:
        return _fact(ctx, text, c, choice)
    tr = ctx.store.turn(c.turn_id) if c.turn_id else None
    with _tx(ctx) as tx:  # a passage but no fact or rule to check: quote it, log it
        return _done(tx, ctx, text, c, "not_said", [note_block(
            f"As recorded: {_quote(tr, c.quote)}." if tr else "I found nothing on record to check that against.",
            "FIX", ["Say which fact or roll is wrong (a name, a number, a frame) and I check it. Logged."])],
            outcome="explain_and_log", evidence=[f"passage {c.turn_id}" if tr else "no passage"],
            start=len(tx.events))


def dispute(ctx: Any, text: str, *, identify: Identify | None = None,
            choice: Choice | None = None) -> str:  # rule: 12.3.6
    """engine/dm/context.py `DisputeHandler`: the OOF answer text (one or more blocks)."""
    return settle_dispute(ctx, text, identify=identify, choice=choice).text


__all__ = ["CATEGORIES", "FIX_HINT", "DisputeResult", "DisputedClaim", "Identify", "default_identify", "dispute",
           "dispute_stats", "locate", "recompute", "review_log_path", "settle_dispute"]
