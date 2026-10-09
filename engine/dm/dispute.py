"""Disputes and corrections (12.3.6, PR-12-11, PR-12-4; DL-12-84..86, DL-12-94): the player says the game erred;
the game understands the report first, then answers from the whole transcript, the stored facts' provenance and the
frames, never from memory.

    res = settle_dispute(ctx, "I succeeded but never got the purse")  # understand, verify, decide, deliver, log
    res = settle_dispute(ctx, text, choice="rewind")                  # answer the reliance CHOICE
    text = dispute(ctx, text)                                         # engine/dm/context.py DisputeHandler

PR-12-11: (1) **understand** (`locate`): one `Role.UNDERSTAND` call (engine/dm/understand.py) reads the report with
the WHOLE transcript and returns up to three complaints `{believes, happened, category, turn, quote}` plus what each
is about; code never pins a report first by a number or a name in it (`feedback.locate_call: retired`); code checks
the turn and the quote exist; (2) **restate**: every answer opens with "You're saying <believes>."; (3) **verify**:
the passage and the other turns naming the subject, the stored value with its provenance (source event, source kind,
turn), the frame with a code recomputation (`recompute`) and what it wrote, the calendar and pronouns on record, the
claim log; (4) **decide** by PR-12-11's table (first row that fits), with "not found" (a "did you mean" with the
nearest passage) and `ruling_question` (the frame explained in plain words); (5) **deliver** a `[CORRECTION]` or
`[FIX]` block, with a CHOICE when reliance applies; never "logged" alone; (6) **log** the dispute record (meta
`corrections`, `type: dispute`) and a block in the save's review log `<save>.disputes.md`.

A correction is a `fact_set` with `source: correction`, `supersedes` and `pinned: true` (never archived; always in
its subject's profile in view). The player's reading wins only on incidental detail slots with nothing on record;
everything else keeps INV-9: only the record decides (bias: act on fiction, explain on mechanics). Take-backs (12.5.8): within the scene always; past its start
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
from engine.dm.understand import CATEGORIES, season_word, understand
from engine.resolve.rulings import RulingRecord, log_ruling
from engine.store.db import REVERTIBLE, TAKE_BACK_EXTRA, Rejected, Transaction
from engine.store.events import WORLD, Event
from engine.store.projection import WorldState, project

PLAYER_FACING = ("shown", "available")
Choice = Literal["rewind", "accept_forward", "keep"]
DisputeKind = Literal["unclear", "hidden", "not_said", "stands", "narration_error", "record_error", "ruling_stands",
                      "ruling_error", "store_agrees", "mistaken", "player_wins", "unverified", "taken_back", "misread",
                      "not_found"]
# Resolved sources (12.3.4 step 1): a write from one of these can require a value; narration alone cannot.
RESOLVED = frozenset({"oracle", "generation", "ruling", "data", "player_accepted", "correction"})
# T0/T1a incidental fiction (12.14.13): the lasting look slots and what someone is doing. Everything else keeps INV-9.
INCIDENTAL_SLOTS = frozenset({"hair", "face", "mark", "build", "clothing", "worn", "voice", "material", "marking",
                              "activity"})
# what an understood complaint is about (understand.ABOUT): mechanics keep INV-9; the rest is fiction (act on it)
MECHANICS = frozenset({"quantity", "possession", "roll_or_outcome", "name"})
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
    located_by: str = "model"  # model | caller
    believes: str = ""  # the complaint in plain words (the understanding call's), restated first in the answer
    happened: str = ""  # what the transcript shows, as the understanding call read it (the review log)
    about: str = "other"  # understand.ABOUT


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
    """The sentence of `text` holding `needle` (else its start), at most `n` characters; a long sentence is cut
    around the needle."""
    flat = " ".join(str(text).split())
    if needle:
        for s in _SENTENCES.split(flat):
            if _norm(needle) in _norm(s):
                if len(s) <= n:
                    return s
                at = max(0, s.lower().find(_norm(needle)[:20]) - n // 3)
                return ("…" if at else "") + s[at:at + n] + ("…" if at + n < len(s) else "")
    return flat[:n] + ("…" if len(flat) > n else "")


_SENTENCES = re.compile(r"(?<=[.!?])\s+|(?<=[.!?][\"”])\s+")


def _quote(tr: Any, needle: str = "", n: int = 160) -> str:
    return f"{_turn_words(tr.turn_id)}: \"{_excerpt(tr.delivered_verbatim, needle, n)}\""


def _has(text: str, phrase: str) -> bool:
    return bool(phrase) and re.search(rf"(?<![\w-]){re.escape(_norm(phrase))}(?![\w-])", _norm(text)) is not None


_WORD_STOP = frozenset("that this with from have they them then into never were your there about what when which "
                       "would should could said says just only also again still been being because while wrong "
                       "right turn game".split())


def _nearest(store: Any, text: str, current: str | None) -> Any:  # rule: PR-12-11
    """The 'did you mean' passage: the turn sharing the most words (4+ letters) with `text`, newest on a tie; else
    the latest turn."""
    words = {w for w in re.findall(r"[a-z]{4,}", text.lower()) if w not in _WORD_STOP}
    best, score = None, 0
    turns = _turns(store, current)
    for tr in turns:  # newest first: a later turn needs strictly more words to win
        n = len(words & set(re.findall(r"[a-z]{4,}", (tr.input_verbatim + " " + tr.delivered_verbatim).lower())))
        if n > score:
            best, score = tr, n
    return best or (turns[0] if turns else None)


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


def _seen(store: Any, state: WorldState, eid: str, current: str | None) -> bool:
    """The player can check this subject: player-facing, or met in play (its name as the PC knows it is in a
    delivered turn; NPCs seeded as background stay `background` after they are met). Sealed: never."""
    from engine.store.views import display_name

    if _visible_entity(state, eid):
        return True
    if eid not in state.entities or eid in state.seals:
        return False
    name = display_name(state, eid)
    return len(name) >= 3 and any(_has(t.delivered_verbatim, name) for t in _turns(store, current))


def _store_value(state: WorldState, c: DisputedClaim, seen: bool | None = None) -> tuple[Any, bool, str | None]:
    """(value, player-facing?, fact id) for the claim's subject and key. `seen`: whether the player has met the
    subject (default: the subject is player-facing)."""
    from engine.store.views import name_known

    vis = _visible_entity(state, c.subject) if seen is None else seen
    if c.kind == "quantity":
        q = state.quantities.get(c.subject, {}).get(c.key)
        if q is None:
            return None, vis, None
        return q.current, q.visibility in PLAYER_FACING and vis, None
    if c.key == "name" and c.subject in state.entities:
        e = state.entities[c.subject]
        return e.name, vis and (name_known(state, c.subject) or _same(c.said, e.name)), \
            state.current_fact_id(c.subject, "name")
    fid = state.current_fact_id(c.subject, c.key)
    if fid is None or state.facts[fid].value is None:
        return None, vis, None
    f = state.facts[fid]
    ok = f.visibility in PLAYER_FACING and fid not in state.seals and vis
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
    incidental = c.key.removeprefix("detail.") in INCIDENTAL_SLOTS  # re-rolled incidental fiction: continuity wins
    if not hist or cur is None or (state.facts[cur].source in RESOLVED and not incidental):
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
           "believes": c.believes if c else "", "category": c.category if c else "other",
           "located_by": c.located_by if c else "model",
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
             f"- **Understood**: {rec.get('believes') or '(nothing understood)'}",
             f"- **Category**: {rec['category']} (understood by {rec['located_by']})",
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
                         "explain_with_quote, explain_and_log (the record stands); not_found.\n\n")
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


# ------------------------------------------------------------------------------------------- understand (item 1)


def _pc(state: WorldState) -> str | None:
    return next((eid for eid, e in state.entities.items() if e.kind == "pc" and e.exists == "exists"), None)


def _words(s: str) -> set[str]:
    return set(re.findall(r"[a-z]+", str(s).lower().replace("_", " ")))


def _number_of(value: Any) -> int | None:
    """The model's value as a number ("14", "fourteen"); None when it is not one."""
    words = ("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen "
             "seventeen eighteen nineteen twenty").split()
    m = re.search(r"-?\d+", str(value or ""))
    if m:
        return int(m.group(0))
    return next((i for i, w in enumerate(words) if re.search(rf"\b{w}\b", str(value or "").lower())), None)


def _stored_key(ctx: Any, subject: str, key: str) -> str:
    """The stored predicate the model's `key` names on `subject`: an exact predicate, a detail slot
    (`details.slot_of`), or a predicate holding the key's words; else the slot it would be ("" when none)."""
    from engine.store.details import slot_of

    state: WorldState = ctx.state
    key = key.strip().lower()
    if not key:
        return ""
    if state.current_fact_id(subject, key) is not None:
        return key
    kind = state.entities[subject].kind if subject in state.entities else None
    slot = slot_of(key, ctx.rules, kind)
    if slot:
        return f"detail.{slot}"
    want = _words(key) - {"the", "a", "an", "of"}
    for k in state.fact_keys:
        subj, pred = k.split("|", 1)
        if subj == subject and want and want <= _words(pred):
            return pred
    return ""


def _claim(ctx: Any, u: dict[str, Any], turns: dict[str, Any]) -> DisputedClaim:  # rule: PR-12-11
    """One understood complaint as a claim code can verify: the turn kept only when it is a transcript turn, the
    quote only when that turn holds it (else the turn that does); `about`/`key`/`value` mapped to what is stored."""
    state: WorldState = ctx.state
    cat = str(u.get("category") or "other")
    c = DisputedClaim(believes=" ".join(str(u.get("believes") or "").split()).rstrip("."),
                      happened=str(u.get("happened") or ""), category=cat if cat in CATEGORIES else "other",
                      about=str(u.get("about") or "other"), located_by="model")
    quote = str(u.get("quote") or "").strip().strip('"')
    tr = turns.get(str(u.get("turn") or ""))

    def holds(t: Any) -> bool:
        return bool(quote) and (_has(t.delivered_verbatim, quote) or _has(t.input_verbatim, quote))

    if quote and (tr is None or not holds(tr)):
        tr = next((t for t in turns.values() if holds(t)), tr)
    if tr is not None:
        c.turn_id, c.quote = tr.turn_id, quote if holds(tr) else ""
    subject = str(u.get("subject") or "")
    c.subject = subject if subject in state.entities else ""
    key, value = str(u.get("key") or ""), str(u.get("value") or "").strip()
    said: Any = value or None
    pc = _pc(state)
    kw = _words(key)
    if c.about == "season_or_time" or kw & {"season", "seasons"}:
        c.about = "season_or_time"
    elif c.about == "pronoun" or kw & {"pronoun", "pronouns"}:
        c.about = "pronoun"
    elif c.about == "roll_or_outcome" or c.category in ("rule_wrong", "ruling_question"):
        c.kind = "ruling"  # a roll, its odds or its result: the frame recomputed and explained
        return c
    elif c.about == "action_reading":  # how the player's own action was read (who spoke or acted is never this)
        c.kind = "beat"
        return c
    if c.about == "quantity":
        subj = c.subject if c.subject in state.quantities else (pc or "")
        want = _words(key)
        q = next((n for n in state.quantities.get(subj, {}) if want and (want & _words(n))), None)
        if q is not None:
            c.kind, c.subject, c.key, c.said = "quantity", subj, q, _number_of(value)
            return c
        c.about = "fact"
    if c.about == "possession":
        c.subject = c.subject if c.subject and state.entities[c.subject].kind != "item" else (pc or "")
        c.key, c.said = "carries", re.sub(r"^(?:my|a|an|the|some|still)\s+", "", value, flags=re.I) or None
        if c.subject != pc and state.current_fact_id(c.subject, "carries") is None:
            c.key, c.about = "", "who_said_what"  # an NPC's unrecorded cup or coat: incidental fiction, not mechanics
    elif c.about == "name":
        c.key, c.said = "name", said
    elif c.about == "pronoun":
        c.key, c.said = "pronouns", said
    elif c.about == "season_or_time":
        c.subject, c.key, c.said = c.subject or WORLD, "season", said
    elif c.subject and c.about in ("fact", "look_or_activity", "other"):
        c.key = _stored_key(ctx, c.subject, key)
        c.said = said
    if c.category == "other" and c.key and c.kind == "fact":
        c.category = "remembered_wrong"  # a named stored fact: the label only (outcomes follow the evidence)
    return c


def locate(ctx: Any, text: str) -> list[DisputedClaim]:  # rule: PR-12-11
    # rule: 12.3.6
    """PR-12-11 step 1: the understanding call (engine/dm/understand.py; no model: nothing understood), each
    complaint verified into a claim. Code never pins the report itself by a number or a name."""
    turns = {t.turn_id: t for t in _turns(ctx.store, getattr(ctx, "turn_id", None))}
    if getattr(ctx, "model", None) is None:
        from engine.dm.understand import default

        complaints = default()["complaints"]
    else:
        complaints = understand(ctx, text)
    return [_claim(ctx, u, turns) for u in complaints]


def default_identify(ctx: Any, text: str) -> DisputedClaim | None:  # rule: 12.3.6
    """The first understood complaint (`identify=` hook for a front end)."""
    got = locate(ctx, text)
    return got[0] if got else None


# ------------------------------------------------------------------------------------------- the outcomes


def _done(tx: Transaction, ctx: Any, text: str, c: DisputedClaim | None, kind: DisputeKind, blocks: list[OofBlock],
          *, outcome: str, evidence: list[str], start: int, reverted: list[int] | None = None,
          correction: dict[str, Any] | None = None, choices: list[dict[str, str]] | None = None) -> DisputeResult:
    """Every answer ends here: the complaint restated first (PR-12-11 step 2), the dispute record and its review-log
    block (12.3.6 item 6), then the result."""
    if c is not None and c.believes and blocks:
        blocks = [_restated(blocks[0], c.believes), *blocks[1:]]
    writes = [e.seq for e in tx.events[start:] if e.seq is not None]
    answer = "\n".join(b.text for b in blocks)
    rec = _log_dispute(tx, ctx, text, c, outcome=outcome, answer=answer, evidence=evidence, writes=writes,
                       reverted=list(reverted or []))
    return DisputeResult(kind, blocks, events=tx.events[start:], reverted=list(reverted or []),
                         choices=list(choices or []), claim=c, correction=correction, record=rec)


_LOWER_LEADS = frozenset("the a an it its you your there that this these those he she they his her their my when "
                         "after before even although".split())


def _cite(tr: Any, c: DisputedClaim | None) -> str:
    """`turn N: "<the sentence in question>"`: the claim's verified quote, else the turn's sentence sharing the most
    words with what the player believes."""
    needle = c.quote if c is not None else ""
    if not needle and c is not None and c.believes:
        want = {w for w in re.findall(r"[a-z]{4,}", c.believes.lower()) if w not in _WORD_STOP}
        sentences = _SENTENCES.split(" ".join(str(tr.delivered_verbatim).split()))
        best = max(sentences, key=lambda s: len(want & set(re.findall(r"[a-z]{4,}", s.lower()))), default="")
        needle = best if want & set(re.findall(r"[a-z]{4,}", best.lower())) else ""
    return _quote(tr, needle)


def _restated(block: OofBlock, believes: str) -> OofBlock:  # rule: PR-12-11
    """`[LABEL] You're saying <believes>.` as the block's first line; its old first line follows, aligned."""
    label, _, first = block.text.partition("] ")
    lead = believes.split(" ", 1)[0]
    lead = re.split(r"['’]", lead)[0].lower()
    said = believes[:1].lower() + believes[1:] if lead in _LOWER_LEADS else believes  # names keep capitals
    pad = " " * (len(label) + 2)
    return OofBlock(kind=block.kind, text=f"{label}] You're saying {said.rstrip('.')}.\n{pad}{first}")


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
    if ev is None and c.turn_id:  # the passage's beat, or the roll its OFFER led to (committed within two turns)
        n = _turn_no(c.turn_id)
        ev = next((e for e in ctx.store.events(types=["frame_committed"]) if e.turn_id == c.turn_id), None) or next(
            (e for e in ctx.store.events(types=["frame_committed"]) if n < _turn_no(e.turn_id) <= n + 2), None)
        c.frame_id = getattr(ev.payload, "frame_id", None) if ev else None
    with _tx(ctx) as tx:
        start = len(tx.events)
        if ev is None:
            return _unrolled(ctx, tx, text, c, start)
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
        if not diffs:  # ruling_question / rule_wrong, the frame recomputes the same: explain it in plain words
            why = (f"{c.missed_fact} is already cited" if c.missed_fact and c.missed_fact in cited else
                   f"{c.missed_fact} was not on record before that roll" if c.missed_fact else
                   "recomputed from the rules and the record, it comes out the same")
            head, rest = _explain_roll(ctx, frame, ev)
            return _done(tx, ctx, text, c, "ruling_stands", [note_block(
                head, "FIX", [*rest, f"{why.capitalize()} ({summary})."])],
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
                "The result stands and is corrected going forward." if ok else
                f"It can't be taken back ({why_not}): corrected going forward.")
        return _done(tx, ctx, text, c, "ruling_error", [note_block(desc, "CORRECTION", [tail])],
                     outcome="take_back" if reverted else "correct", evidence=evidence, start=start,
                     reverted=reverted, correction=rec)


def _whose(state: WorldState, eid: str) -> str:
    e = state.entities.get(eid)
    return "your" if e is not None and e.kind == "pc" else f"{_name(state, eid)}'s"


def _changes(store: Any, state: WorldState, turn_id: str | None, from_seq: int) -> list[str]:  # rule: PR-12-11
    """What a turn wrote on record from `from_seq`, in plain words: shown facts and shown quantities (12.3.6 item 3:
    the frame's writes)."""
    out: list[str] = []
    for e in store.events(since=from_seq - 1):
        p: Any = e.payload
        if e.turn_id != turn_id or e.seq in state.reverted:
            continue
        if (e.type == "fact_set" and p.visibility in PLAYER_FACING and p.value not in (None, "", False, [])
                and p.subject in state.entities and not p.predicate.startswith(("closed.", "trg.", "log.", "lethal"))):
            what = p.predicate.removeprefix("detail.").replace("_", " ").replace(".", " ")
            out.append(f"{_whose(state, p.subject)} {what}: {_excerpt(str(p.value), n=80)}")
        elif e.type == "quantity_changed":
            q = state.quantities.get(p.entity, {}).get(p.quantity)
            if q is not None and q.visibility in PLAYER_FACING:
                out.append(f"{_whose(state, p.entity)} {p.quantity.replace('_', ' ')} {p.new_value - p.delta} → "
                           f"{p.new_value}")
    return list(dict.fromkeys(out))[:6]


def _explain_roll(ctx: Any, frame: dict[str, Any], ev: Event) -> tuple[str, list[str]]:  # rule: PR-12-11
    """A committed frame in plain words: what was rolled and as what, the roll, the degree and reach, what it
    changed on record, and its aim (the typed intended change is spec 015's)."""
    from engine.dm.oof import name_of

    fid = getattr(ev.payload, "frame_id", None)
    res: Any = next((e.payload for e in ctx.store.events(since=int(ev.seq or 0), types=["frame_resolved"])
                     if getattr(e.payload, "frame_id", None) == fid), None)
    b = frame.get("beat") or {}
    what = str(b.get("restatement") or b.get("intent") or "that action").rstrip(".")
    verb = name_of(ctx.rules, b.get("verb")).lower() or "check"
    if res is not None:
        roll = res.roll if isinstance(res.roll, dict) else {}
        reach = (res.delivered or {}).get("reach") or frame.get("reach")
        head = (f"Here's why: {_turn_words(ev.turn_id)} rolled \"{what}\" as a {verb} (d20 {roll.get('d20')} → "
                f"{roll.get('total')} vs {frame.get('dc')}): {str(res.degree).replace('_', ' ')}, reach {reach}.")
    else:
        head = f"Here's why: {_turn_words(ev.turn_id)} committed \"{what}\" as a {verb}; it was not rolled."
    changes = _changes(ctx.store, ctx.state, ev.turn_id, int(ev.seq or 0))
    rest = [f"It changed on record: {'; '.join(changes)}." if changes else "It changed nothing on record."]
    if b.get("intent"):
        rest.append(f"Its aim was \"{str(b['intent']).rstrip('.')}\": a success changes only what is listed; "
                    "anything else in the aim takes another action.")
    return head, rest


def _unrolled(ctx: Any, tx: Transaction, text: str, c: DisputedClaim, start: int) -> DisputeResult:  # rule: PR-12-11
    """A ruling complaint with no committed frame: an open OFFER is explained from its cited facts (INV-9: a cited
    fact is changed only by the record; logged for review); otherwise the turn is quoted: nothing was rolled."""
    state: WorldState = ctx.state
    pause = state.open_pause()
    fr = (pause.detail or {}).get("frame") if pause is not None and pause.kind == "offer" else None
    if isinstance(fr, dict):
        lines, evidence = [], []
        for sign, cites in (("bonus", fr.get("levers") or []), ("penalty", fr.get("snags") or [])):
            for x in cites:
                cite = str(x.get("fact_id") if isinstance(x, dict) else x)
                f = state.facts.get(cite)
                if f is None:
                    continue
                src = ctx.store.event(f.valid_from_seq)
                since = _turn_words(src.turn_id) if src is not None else "the start"
                lines.append(f"a {sign} from \"{_name(state, f.subject)} {f.predicate.removeprefix('detail.')}: "
                             f"{f.value}\" (on record since {since}, source {f.source})")
                evidence.append(f"{cite} {f.subject} {f.predicate} = {f.value!r} ({f.source}, seq {f.valid_from_seq})")
        rec = _record(c, turn_found=tx.turn_id, kind="unverified", form="oof_note", reliance=[], store_value=None,
                      rewound=[])
        _log(tx, ctx, c, f"player disputes the open offer's levers: {text[:120]}", rec)
        head = "That offer isn't rolled yet. Its odds come from the record: " + ("; ".join(lines) or "no cited facts") + "."
        return _done(tx, ctx, text, c, "stands", [note_block(head, "FIX", [
            "An activity that has ended is never a bonus (01.6.8). I can't strike a cited fact on your word alone, so "
            "this is logged for review; if it's stale, back off and declare again."])],
            outcome="explain_and_log", evidence=evidence or ["open offer, no cited facts"], start=start, correction=rec)
    tr = ctx.store.turn(c.turn_id) if c.turn_id else None
    if tr is None:
        return _not_found(ctx, tx, text, c, start)
    first = ctx.store.conn.execute("SELECT MIN(seq) FROM events WHERE turn_id=?", (tr.turn_id,)).fetchone()[0]
    changes = _changes(ctx.store, state, tr.turn_id, int(first or 0)) if first else []
    return _done(tx, ctx, text, c, "stands", [note_block(
        f"Nothing was rolled there ({_cite(tr, c)}).", "FIX",
        [f"That turn changed on record: {'; '.join(changes)}." if changes else "That turn changed nothing on record."])],
        outcome="explain_with_quote", evidence=[f"no frame committed in {tr.turn_id}"], start=start)


def _not_found(ctx: Any, tx: Transaction, text: str, c: DisputedClaim | None, start: int) -> DisputeResult:
    # rule: PR-12-11
    """No passage fits what the player believes: "I can't find that; did you mean …?" with the nearest passage."""
    tr = _nearest(ctx.store, f"{text} {c.believes if c else ''} {c.quote if c else ''}", getattr(ctx, "turn_id", None))
    head = "I can't find that" + (f"; did you mean {_cite(tr, c)}?" if tr else " in the story so far.")
    return _done(tx, ctx, text, c, "not_found", [note_block(head, "FIX", [
        "Say it again with the turn number (/turn N shows a turn) and I'll check it against the record."])],
        outcome="not_found", evidence=[f"nearest: {tr.turn_id}" if tr else "no turns"], start=start)


def _computed(ctx: Any, text: str, c: DisputedClaim) -> DisputeResult:  # rule: PR-12-11
    # rule: 12.3.6
    """The season (the calendar) and a person's pronouns (on their record): the store agrees with the player → the
    narration slipped (a correction with nothing to write); otherwise the record is explained. Nothing on record
    for a pronoun: incidental fiction, the player's reading wins."""
    state: WorldState = ctx.state
    if c.key == "season":
        value, what = season_word(state), "it is"
        tail = f" ({when_words(state.time.now)})"
    else:
        e = state.entities.get(c.subject)
        value = str(e.data.get("pronouns") or "") if e is not None else ""
        what, tail = f"{_name(state, c.subject)} is", " on record"
        if not value:
            return _incidental(ctx, text, c)
    said = _words(c.said or "")
    agrees = not said or bool(said & _words(value))
    tr = ctx.store.turn(c.turn_id) if c.turn_id else None
    where = f" ({_cite(tr, c)})" if tr is not None else ""
    with _tx(ctx) as tx:
        start = len(tx.events)
        evidence = [f"{c.subject or WORLD} {c.key} = {value!r} (record)", *([f"passage {tr.turn_id}"] if tr else [])]
        if agrees:
            rec = _record(c, turn_found=tx.turn_id, kind="narration_error", form="oof_note", reliance=[],
                          store_value=value, rewound=[])
            _log(tx, ctx, c, f"narration error: {what} {value}", rec)
            return _done(tx, ctx, text, c, "store_agrees", [note_block(
                f"You're right: {what} {value}{tail}; the narration slipped{where}.", "CORRECTION",
                ["The record has it right, and it stays."])], outcome="correct", evidence=evidence, start=start,
                correction=rec)
        return _done(tx, ctx, text, c, "mistaken", [note_block(
            f"As recorded: {what} {value}{tail}.", "FIX", [f"The record does not say {c.said}{where}."])],
            outcome="explain_with_quote", evidence=evidence, start=start)


def _incidental(ctx: Any, text: str, c: DisputedClaim) -> DisputeResult:  # rule: 12.3.6
    # rule: PR-12-11
    """Nothing stored to check: incidental fiction (who said or did what in passing, a look, an activity) → the
    player's reading wins as a pinned correction on the subject (else `world`), holding the complaint in their
    words (00.6.7 "Certain"); mechanics → what the record holds, logged for review, nothing written (INV-9)."""
    state: WorldState = ctx.state
    tr = ctx.store.turn(c.turn_id) if c.turn_id else None
    where = f" ({_cite(tr, c)})" if tr is not None else ""
    with _tx(ctx) as tx:
        start = len(tx.events)
        if c.about in MECHANICS:
            rec = _record(c, turn_found=tx.turn_id, kind="unverified", form="oof_note", reliance=[], store_value=None,
                          rewound=[])
            _log(tx, ctx, c, f"unverified mechanical claim: {c.believes or text}"[:300], rec)
            held = _holdings(state, c.subject) if c.subject else ""
            return _done(tx, ctx, text, c, "unverified", [note_block(
                "The record has nothing that settles that" + (f" (it holds: {held})" if held else "") + f"{where}.",
                "FIX", ["Without a record I can't change it; it's logged for review."])],
                outcome="explain_and_log", evidence=[f"nothing on record; passage {c.turn_id}"], start=start,
                correction=rec)
        subject = c.subject if c.subject in state.entities else WORLD
        n = 1 + sum(1 for k in state.fact_keys if k.startswith(f"{subject}|correction."))
        fid = tx.mint(ids.FACT)
        tx.add(Event.of("fact_set", {"source": "correction"}, source="correction", rule_id="12.3.6", fact_id=fid,
                        subject=subject, predicate=f"correction.{n}", value=(c.believes or text)[:300],
                        visibility="shown", pinned=True))
        rec = _record(c, turn_found=tx.turn_id, kind="player_reading", form="oof_note", reliance=[], store_value=None,
                      rewound=[], fact_id=fid)
        _log(tx, ctx, c, f"player's reading accepted: {c.believes or text}"[:300], rec)
        return _done(tx, ctx, text, c, "player_wins", [note_block(
            f"You're right{where}: it's taken as you say, and it stays.", "CORRECTION")],
            outcome="player_reading_wins", evidence=[f"nothing on record; passage {c.turn_id}"], start=start,
            correction=rec)


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
        from engine.dm.oof import name_of

        frames = [e for e in store.events(types=["frame_committed"]) if e.turn_id == tr.turn_id]
        beats = [e.payload.frame.get("beat") or {} for e in frames]  # type: ignore[attr-defined]
        reading = " ".join(str(b.get("restatement") or "") for b in beats) or _excerpt(tr.delivered_verbatim, n=120)
        verbs = ", ".join(name_of(ctx.rules, b["verb"]).lower() for b in beats if b.get("verb"))
        as_verb = f" (as {verbs})" if verbs else ""
        # the player's words: the declaring turn (an OFFER's commit turn holds only "commit")
        decl = min((int(b.get("declared_seq") or 0) for b in beats), default=0)
        ev_decl = store.event(decl + 1) if decl else None
        said_tr = (store.turn(ev_decl.turn_id) if ev_decl is not None and ev_decl.turn_id else None) or tr
        unseen = (any(e.payload.frame.get("offer_choice") == "auto" for e in frames)  # type: ignore[attr-defined]
                  or (not frames and bool(tr.writes)))
        support = (_stems(text) & _stems(said_tr.input_verbatim)) - _stems(reading)
        evidence = [f"{said_tr.turn_id} input: \"{said_tr.input_verbatim}\"", f"read as: \"{reading}\"",
                    f"OFFER shown: {'no' if unseen else 'yes'}", f"report words in the input, not the reading: "
                    f"{sorted(support) or 'none'}"]
        if not (unseen and support):
            why = ("the OFFER showed that reading before the roll" if not unseen else
                   "your words then match the reading")
            return _done(tx, ctx, text, c, "stands", [note_block(
                f"As recorded: {_turn_words(said_tr.turn_id)}, you wrote \"{said_tr.input_verbatim}\"; it was read as "
                f"\"{reading}\"{as_verb}.", "FIX", [f"It stands: {why}."])],
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
    value, facing, fact_id = _store_value(state, c, _seen(store, state, c.subject, current) if c.subject else None)
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
                    f"As recorded: {what} is {shown} ({src_line}).", "FIX")],
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
                    ["The record has it right; the narration slipped."])],
                    outcome="correct", evidence=evidence, start=start, correction=rec)
            if said_tr is not None:  # the narration said the player's value, the store holds another: store wins
                c.turn_id = c.turn_id or said_tr.turn_id
                return _narration_error(ctx, tx, text, c, value, fact_id, choice, evidence, start)
            return _done(tx, ctx, text, c, "mistaken", [note_block(
                f"As recorded: {what} is {shown} ({src_line}).", "FIX",
                [f"{c.said} was never said."])],
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
        tail = ("The result stands, corrected around it." if choice != "rewind" else
                "That can't be rewound cleanly any more; corrected going forward.")
    else:
        # coarse: 12.3.4 (refunds for spends before the current scene are not computed in M1)
        tail = "You spent nothing because of it; the record stands."
    return _done(tx, ctx, text, c, "narration_error", [note_block(head, "CORRECTION", [tail])],
                 outcome="take_back" if reverted else "correct", evidence=evidence, start=start, reverted=reverted,
                 correction=rec)


def _settle_one(ctx: Any, text: str, c: DisputedClaim | None, choice: Choice | None) -> DisputeResult:
    # rule: PR-12-11
    """PR-12-11 step 4 for one understood complaint, first row that fits."""
    if c is None or not (c.turn_id or c.subject or c.frame_id):
        with _tx(ctx) as tx:
            return _not_found(ctx, tx, text, c, len(tx.events))
    if c.kind == "ruling":
        return _ruling(ctx, text, c, choice)
    if c.kind == "beat":
        return _misread(ctx, text, c)
    if c.key in ("pronouns", "season"):
        return _computed(ctx, text, c)
    if c.subject and c.key:
        return _fact(ctx, text, c, choice)
    return _incidental(ctx, text, c)


def settle_dispute(ctx: Any, text: str, *, identify: Identify | None = None,
                   choice: Choice | None = None) -> DisputeResult:  # rule: 12.3.6
    # rule: PR-12-11
    """PR-12-11 from the whole transcript and the store. `ctx`: anything with `store`, `state`, `rules`, optional
    `tx` (the turn's open transaction; else a one-shot transaction), `model` and `record_call` (the understanding
    call). `identify` (a CHOICE answer, tests, a front end) replaces the understanding call with one claim.
    Each complaint is answered in order (one dispute record each); at most one reliance CHOICE per report, later
    ones are answered forward. The result's `claim`/`record` are the CHOICE's complaint, else the first."""
    claims = [identify(ctx, text)] if identify else locate(ctx, text)
    results: list[DisputeResult] = []
    for c in claims or [None]:
        open_choice = any(r.choices for r in results)
        results.append(_settle_one(ctx, text, c, "accept_forward" if open_choice and choice is None else choice))
    lead = next((r for r in results if r.choices), results[0])
    if len(results) == 1:
        return lead
    return DisputeResult(lead.kind, [b for r in results for b in r.blocks], events=[e for r in results for e in r.events],
                         reverted=[s for r in results for s in r.reverted], choices=lead.choices, claim=lead.claim,
                         correction=next((r.correction for r in results if r.correction), None), record=lead.record)


def dispute(ctx: Any, text: str, *, identify: Identify | None = None,
            choice: Choice | None = None) -> str:  # rule: 12.3.6
    """engine/dm/context.py `DisputeHandler`: the OOF answer text (one or more blocks)."""
    return settle_dispute(ctx, text, identify=identify, choice=choice).text


__all__ = ["CATEGORIES", "FIX_HINT", "DisputeResult", "DisputedClaim", "Identify", "default_identify", "dispute",
           "dispute_stats", "locate", "recompute", "review_log_path", "settle_dispute"]
