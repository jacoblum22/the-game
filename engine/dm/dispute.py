"""Disputes and corrections (12.3.6, PR-12-11, PR-12-4, 12.5.8; DL-12-105, DL-12-106; spec 022): the player says the
game erred; the Fixer investigates the record, code validates and applies what it proposes, and the answer reads
found → did → Now:.

    res = settle_dispute(ctx, "I paid for the round but the coin is still in my purse")
    res.text      # [CORRECTION] <what was found> / Done: … / Now: coin 11 (was 12)
    text = dispute(ctx, text)                                          # engine/dm/context.py DisputeHandler

PR-12-11: (1) one report, one snapshot: nothing is written until the investigation ends; (2-3) the Fixer
(engine/dm/fixer.py, `Role.FIXER`, its model set in config) reads the report and calls read-only tools for a bounded
number of steps, then returns every complaint with what it found and its proposals; (4) **code validates** each
proposal: a mechanical change needs evidence the tools returned (INV-9), sealed stays sealed (INV-10), a correction
never delivers a clue, quantities stay within their bounds (T-00-1), a take-back obeys 12.5.8's limit; a proposal
that fails is dropped and the answer says why; (5) the valid ones are applied together as `source: correction`
writes of the typed value, never the report's words; (6) the answer: what was found, what was done, then `Now:` with
each shown value that changed (12.15.9), never a silent restore; (7) the log: a dispute record per complaint in the
corrections ledger and one block per report in `saves/<campaign>.disputes.md`.

*Retires* (spec 022): the one-shot understanding call over the player-visible transcript (engine/dm/understand.py),
`_claim`'s fixed branches and the fixed outcome table, the pinned `correction.N` complaint text, complaints settled one
after another on a changing state, and the reliance CHOICE pause (a take-back is proposed and applied, with `Now:`).
*Retires* (spec 026; DL-12-117): `rerender` (re-showing a stored line could not change it) and explain-only at an
open OFFER: `reframe` withdraws the OFFER on screen (nothing spent) and runs gate, necessity and frame again with the
corrections; a take-back of the unrolled pending turn closes its OFFER. Any decision can be dry-run on a copy
(`preview`), which is how the Fixer checks the screen before anything is applied.
"""

from __future__ import annotations

import re
import sqlite3
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from engine import ids
from engine.dm.fixer import Investigation, investigate, name, pc_of, sheet, turn_no
from engine.dm.oof import FIX_HINT, OofBlock, note_block, when_words
from engine.resolve.rulings import RulingRecord, log_ruling
from engine.store.db import REVERTIBLE, TAKE_BACK_EXTRA, Rejected, Store, Transaction
from engine.store.events import WORLD, Event
from engine.store.projection import WorldState, project

PLAYER_FACING = ("shown", "available")
DisputeKind = Literal["explained", "corrected", "taken_back", "not_found"]
# T0/T1a incidental fiction (12.14.13): the lasting look slots and what someone is doing; a correction to one needs
# no evidence (the player's reading wins, 12.3.6 item 4). Every other key keeps INV-9: only the record decides.
INCIDENTAL_SLOTS = frozenset({"hair", "face", "mark", "build", "clothing", "worn", "voice", "material", "marking",
                              "activity", "manner"})
NO_EVIDENCE = ("explain", "reframe", "correct_testimony")  # a re-frame spends nothing: the gate and frame decide
REFRAMES = ("offer", "redirect", "warning")  # pauses with nothing rolled yet (12.5.8 item 1)
IDENTITY = ("name", "pronouns")  # entity data set at creation (12.11.1), never a corrective fact (spec 022)
CASE_PREDICATES = ("points_to.", "clue", "case.")  # the case graph and clue delivery (INV-10; PR-15-6); never
# `knows_`: no case writes it, and it blocked harmless facts ("Pell knows your rank", spec 026)
MAX_AMOUNT = 50
_ID = re.compile(r"\b(?:turn|frame|fact|said|rul|cinst)\.\d+\b")


@dataclass
class DisputedClaim:
    """One complaint as the Fixer read it (the review log; `turn.py` keeps the name)."""

    believes: str = ""
    category: str = "other"
    turn_id: str | None = None
    verdict: str = "unclear"
    found: str = ""
    done_kinds: list[str] = field(default_factory=list)  # the proposal kinds code applied for it


@dataclass
class DisputeResult:
    kind: DisputeKind
    blocks: list[OofBlock]
    events: list[Event] = field(default_factory=list)
    reverted: list[int] = field(default_factory=list)
    choices: list[dict[str, str]] = field(default_factory=list)  # retired: always empty (a take-back is applied)
    claim: DisputedClaim | None = None
    correction: dict[str, Any] | None = None
    record: dict[str, Any] | None = None
    claims: list[DisputedClaim] = field(default_factory=list)
    records: list[dict[str, Any]] = field(default_factory=list)
    outcomes: list[Any] = field(default_factory=list)  # a re-frame's beat outcomes (engine/resolve BeatOutcome)

    @property
    def text(self) -> str:
        return "\n".join(b.text for b in self.blocks)


# ------------------------------------------------------------------------------------------- the record


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


# ------------------------------------------------------------------------------------------- take-backs (12.5.8)


def _blocked(ctx: Any, from_seq: int, turn_id: str | None) -> str | None:  # rule: 12.5.8
    """12.5.8 item 3: why a take-back past the scene start may not reach `from_seq` (None: it may)."""
    tb = ctx.rules.pacing["corrections"]["take_back"]
    current = getattr(ctx, "turn_id", None)
    if current and turn_id and turn_no(current) - turn_no(turn_id) > int(tb["max_turns_back"]):
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


@contextmanager
def _tx(ctx: Any) -> Iterator[Transaction]:
    """The turn's open transaction, else a one-shot one."""
    if getattr(ctx, "tx", None) is not None:
        yield ctx.tx
        return
    with ctx.store.transaction(None) as tx:
        yield tx


# ------------------------------------------------------------------------------------------- validate and apply


def _evidence(p: dict[str, Any], inv: Investigation) -> str | None:  # rule: PR-12-11
    """INV-9 for a mechanical proposal: it cites record ids (turn, frame, fact, said, ruling) the tools returned. The
    reason it fails, or None."""
    cited = set(_ID.findall(" ".join([*(str(x) for x in p.get("evidence") or []), str(p.get("fact_id") or "")])))
    if not cited:
        return "it cites no record"
    unseen = sorted(c for c in cited if not re.search(rf"\b{re.escape(c)}\b", inv.seen))
    return f"{', '.join(unseen)} was not looked at" if unseen else None


def _what(state: WorldState, subject: str, predicate: str) -> str:
    key = predicate.removeprefix("detail.").replace("_", " ").replace(".", " ")
    if predicate.startswith("said."):
        return f"what {name(state, subject)} said"
    e = state.entities.get(subject)
    return f"your {key}" if e is not None and e.kind == "pc" else f"{name(state, subject)}'s {key}"


def _copies_report(value: str, text: str) -> bool:
    """A correction writes the typed value, never the complaint's words (PR-12-11 step 5)."""
    v = " ".join(value.lower().split())
    return len(v) > 30 and (v in " ".join(text.lower().split()) or len(v) > 80)


def _write(tx: Transaction, subject: str, predicate: str, value: Any, supersedes: str | None, rule_id: str,
           visibility: str = "shown") -> str:  # rule: 12.3.6
    fid = tx.mint(ids.FACT)
    tx.add(Event.of("fact_set", {"source": "correction"}, source="correction", rule_id=rule_id, fact_id=fid,
                    subject=subject, predicate=predicate, value=value, visibility=visibility, supersedes=supersedes,
                    pinned=value is not None))
    return fid


def _quantity(state: WorldState, pc: str | None, word: str) -> str | None:
    qs = state.quantities.get(pc or "", {})
    w = word.strip().lower().rstrip("s") or "?"
    return next((k for k, q in qs.items() if q.visibility in PLAYER_FACING and (k.startswith(w) or w.startswith(k))),
                None)


def _set_quantity(tx: Transaction, pc: str, q: str, new: int, reason: str) -> str | None:
    """A corrective quantity write within the quantity's bounds (T-00-1); the reason it fails, or None."""
    cur = tx.state.quantities[pc][q]
    if new < cur.min or (cur.max is not None and new > cur.max):
        return f"{q} {new} is outside {cur.min}..{cur.max if cur.max is not None else 'no limit'}"
    if new == cur.current:
        return f"{q} is already {new}"
    tx.add(Event.of("quantity_changed", source="correction", rule_id="12.3.4", entity=pc, quantity=q,
                    delta=new - cur.current, new_value=new, reason=reason))
    return None


def _value_as_of(ctx: Any, pc: str, q: str, turn_id: str) -> int | None:
    """The quantity's value at the end of `turn_id` (the store's write history, reverted writes skipped)."""
    n, value = turn_no(turn_id), None
    for e in ctx.store.events(types=["quantity_defined", "quantity_changed"]):
        p: Any = e.payload
        if p.entity != pc or p.quantity != q or e.seq in ctx.state.reverted:
            continue
        if e.turn_id and turn_no(e.turn_id) > n:
            break
        value = p.value.current if e.type == "quantity_defined" else p.new_value
    return value


def _take_back(ctx: Any, tx: Transaction, turn_id: str, reason: str) -> tuple[str | None, list[int]]:
    # rule: 12.5.8
    """Every write from the start of `turn_id` reverted (its rolls void) under 12.5.8's limit; (why not, reverted)."""
    row = ctx.store.conn.execute("SELECT MIN(seq) FROM events WHERE turn_id=?", (turn_id,)).fetchone()
    first = int(row[0]) if row and row[0] is not None else 0
    if not first:
        return f"{turn_id} wrote nothing", []
    ok, why = _can_rewind(ctx, first, turn_id)
    if not ok:
        return why, []
    try:
        seqs = _rewind(ctx, tx, first, reason)
    except Rejected as e:
        return f"later events depend on it ({e})", []
    closed = _withdraw_since(ctx, tx, first)  # an OFFER that turn (or a later one) opened goes with it (12.5.8 item 1)
    if not seqs and not closed:
        return "there was nothing left to undo", []
    if seqs:
        _void(tx, [str(getattr(e.payload, "frame_id", "")) for e in ctx.store.events(since=first - 1,
                                                                                     types=["frame_committed"])])
    return None, seqs


def _pending(ctx: Any, tx: Transaction, turn_id: str) -> bool:  # rule: 12.5.8
    """`turn_id` opened the OFFER (or redirect) on screen and rolled nothing: taking it back spends nothing (12.5.8
    item 1)."""
    pause = tx.state.open_pause()
    if not turn_id or pause is None or (pause.detail or {}).get("stage") not in REFRAMES:
        return False
    opened = next((e for e in ctx.store.events(types=["pause_opened"])
                   if getattr(e.payload, "pause_id", None) == pause.pause_id), None)
    return opened is not None and opened.turn_id == turn_id and not any(
        e.turn_id == turn_id for e in ctx.store.events(types=["frame_resolved"]))


def _withdraw_since(ctx: Any, tx: Transaction, first: int) -> bool:  # rule: 12.5.8
    """The open pause, when it was opened at or after `first`: withdrawn (nothing was rolled at an OFFER). A
    `pause_opened` is not a revertible write, so a take-back alone left the OFFER on screen."""
    pause = tx.state.open_pause()
    if pause is None or not any(getattr(e.payload, "pause_id", None) == pause.pause_id
                                for e in ctx.store.events(since=first - 1, types=["pause_opened"])):
        return False
    tx.add(Event.of("pause_closed", source="correction", rule_id="12.5.8", pause_id=pause.pause_id,
                    choice="withdraw", by="withdrawn"))
    return True


@contextmanager
def _turn_ctx(ctx: Any, tx: Transaction) -> Iterator[Any]:
    """A TurnContext over this transaction (the pipeline's Framer is built from one), restored afterwards."""
    from engine.dm.context import TurnContext

    tc = ctx if isinstance(ctx, TurnContext) else TurnContext.for_store(ctx.store, model=ctx.model, rules=ctx.rules)
    old = tc.tx
    tc.tx = tx
    try:
        yield tc
    finally:
        tc.tx = old


def _reframe(ctx: Any, tx: Transaction, p: dict[str, Any], outcomes: list[Any]) -> tuple[str, str]:  # rule: PR-12-11
    # rule: 12.3.6
    # rule: 12.5.8
    """PR-12-11 step 3, 12.3.6 item 4 (DL-12-117): the OFFER on screen withdrawn (nothing was spent) and its beat run
    through gate, necessity and frame again, declared now so the corrections applied before it count. `fact_id`: a
    fact on record that makes the goal impossible (the gate refuses, G4). Never rolls (auto-commit off). A dm-tools
    game plays the DM's turn again instead (`_replay_dm`, spec 032 G11)."""
    from engine.dm import dm_tools
    from engine.dm.turn import _env
    from engine.resolve.pipeline import BeatPlan, run_beats

    pause = tx.state.open_pause()
    d = pause.detail if pause is not None else {}
    if pause is None or d.get("stage") not in REFRAMES or not d.get("plan"):
        return "not", "re-frame: no offer is waiting on screen (a rolled beat is taken back instead)"
    fid = str(p.get("fact_id") or "").strip()
    if fid and (fid not in tx.state.facts or fid in tx.state.seals or tx.state.facts[fid].value is None):
        return "not", f"re-frame: {fid} is not a fact on record"
    if fid and tx.state.facts[fid].source == "oracle":  # 01.15.1, 01.15.8: a coin flip never rules a goal out
        return "not", (f"re-frame: {fid} is a yes/no Oracle answer, never a reason a goal is impossible; what someone "
                       "can do is their record (their card)")
    tx.add(Event.of("pause_closed", source="correction", rule_id="12.5.8", pause_id=pause.pause_id,
                    choice="withdraw", by="withdrawn"))
    tx.add(Event.of("offer_logged", source="correction", rule_id="01.7.1", frame_id=None, shown_at=tx.state.time.now,
                    choice="withdraw"))
    plan = BeatPlan.model_validate(d["plan"])
    beat = plan.beat.model_copy(update={"declared_seq": tx.state.last_seq, "necessity": "uncertain_and_costly",
                                        **({"g4_fact": fid} if fid else {})})
    queued = [BeatPlan.model_validate(q) for q in d.get("queued") or []]
    note, left_out = framer_note(p.get("value"))
    with _turn_ctx(ctx, tx) as tc:
        if dm_tools.enabled(tc):
            what = beat.title or beat.restatement or beat.intent
            why = " (the note was not passed on: odds and rolls are the DM's to set)" if left_out else ""
            return _replay_dm(tc, tx, pause, what, note, fid, outcomes, why)
        env = _env(tc)
        env.auto_commit = False  # a /fix never rolls for the player
        env.framer_note = note
        env.said, env.said_first = list(d.get("said") or []), list(d.get("said_first") or [])
        res = run_beats(env, [plan.model_copy(update={"beat": beat}), *queued])
    outcomes += res.outcomes
    out = res.outcomes[0] if res.outcomes else None
    what = (out.entry.restatement if out is not None else "") or beat.restatement or beat.intent
    why = " (the note was not passed on: odds and rolls are the Framer's to set)" if left_out else ""
    if out is None:
        return "did", f"the offer for \"{what}\" is withdrawn; nothing was spent{why}"
    if out.status == "paused" and res.pause is not None and res.pause.detail.get("stage") == "offer":
        return "did", f"the offer for \"{what}\" is framed again with the record as it stands (below){why}"
    if out.status in ("refused", "redirected", "paused"):
        return "did", f"\"{what}\" is not possible as tried, and nothing was spent (below){why}"
    if out.status == "question":
        return "did", f"the offer for \"{what}\" is withdrawn: {out.entry.gate_words}{why}"
    return "did", f"\"{what}\" needs no roll after all (below){why}"


@dataclass
class Replayed:
    """A dm-tools turn played again by a re-frame (spec 032 G11): the DM's passage, the blocks and beats code owed
    it, and its stats (`screen.dm_tools`). Sits in `DisputeResult.outcomes` beside the pipeline's beat outcomes."""

    passage: str
    oof: list[dict[str, str]]
    beats: list[Any]
    stats: dict[str, Any]


class _NoClue:
    """A correction never delivers a clue (INV-10; spec 032 X22): the DM's `reveal_clue` calls are dropped before
    code sees them."""

    def __init__(self, inner: Any) -> None:
        self.inner = inner
        self.provider = getattr(inner, "provider", "noclue")

    def fill(self, role: Any, schema: dict[str, Any], packet: Any, *, turn_id: str | None, attempt: int,
             seq: int = 0) -> Any:
        res = self.inner.fill(role, schema, packet, turn_id=turn_id, attempt=attempt, seq=seq)
        data = res.data
        if isinstance(data, dict) and isinstance(data.get("calls"), list):
            keep = [c for c in data["calls"] if not (isinstance(c, dict) and c.get("tool") == "reveal_clue")]
            if len(keep) < len(data["calls"]):
                return res.model_copy(update={"data": {**data, "calls": keep}})
        return res


def _replay_dm(tc: Any, tx: Transaction, pause: Any, what: str, note: str | None, fid: str, outcomes: list[Any],
               why: str) -> tuple[str, str]:  # rule: PR-12-11
    """Spec 032 G11, a re-frame on a dm-tools game: the OFFER is withdrawn (by the caller) and the DM plays that turn
    again: the player's own words, the Fixer's note, what the turn's other tool calls already did (kept); any new
    OFFER is framed by code (`dm_tools.code_framer`, no Framer call). Never rolls for the player; never a clue."""
    from engine.dm import dm_tools
    from engine.dm.adjudication import AdjudicationRecord
    from engine.dm.fixer import dm_log, plain_fact
    from engine.dm.turn import recent_exchanges

    opened = next((e for e in tc.store.events(types=["pause_opened"])
                   if getattr(e.payload, "pause_id", None) == pause.pause_id), None)
    tr = tc.store.turn(opened.turn_id) if opened is not None and opened.turn_id else None
    t = dm_tools.Turn(rec=AdjudicationRecord(turn_id=tx.turn_id or "", pc=pc_of(tx.state)))
    t.env = dm_tools._env(tc, t)
    t.env.auto_commit = False
    lead = "\n".join(x for x in [
        f'The player used /fix on the roll offered for "{what}". That offer is withdrawn; nothing was spent.',
        note and f"The game's investigator found: {note}",
        fid and f"On record, so it cannot work as tried: {plain_fact(tx.state, tx.state.facts[fid])}",
        "\n".join(dm_log(tr)[1:]) and "That turn's tool calls (what code did stays done; only the roll is "
                                      "withdrawn):\n" + "\n".join(dm_log(tr)[1:]),
        "Play the player's message again with this in mind: propose a roll only if one is still needed. A correction "
        "never gives a clue."] if x)
    model = tc.model
    tc.model = _NoClue(model)
    try:
        passage = dm_tools._dm_loop(tc, t, tr.input_verbatim if tr is not None else what,
                                    recent_exchanges(tc.store, tx.turn_id or "", n=6), lead)
    finally:
        tc.model = model
    # ponytail: no world step or time here (a /fix is out of fiction); the player's next turn takes them
    outcomes.append(Replayed(passage=passage, oof=t.oof, beats=list(t.rec.beats), stats={
        **t.stats, "tools": [{"tool": a, "args": b, "out": o[:300]} for a, b, o in t.log]}))
    if tx.state.open_pause() is not None:
        return "did", f"the offer for \"{what}\" is withdrawn and the turn played again with the record as it " \
                      f"stands (below){why}"
    return "did", f"the offer for \"{what}\" is withdrawn (nothing was spent) and the turn played again (below){why}"


NOTE_CHARS = 200
_ODDS =re.compile(r"\d|%|\b(?:odds|chances?|percent|dc|difficult\w*|rolls?|rolled|tiers?|modifiers?|bonus|penalty|"
                   r"easy|hard|trivial|certain|automatic\w*|guaranteed)\b", re.IGNORECASE)


def framer_note(value: Any) -> tuple[str | None, bool]:  # rule: PR-12-11
    """A re-frame's note for the Framer (DL-12-123): (the note, left out). One line, at most NOTE_CHARS; a note that
    states odds, a number or a roll is left out (the Framer owns the odds, VIII.1), and the re-frame still runs."""
    line = next((x.strip() for x in str(value or "").splitlines() if x.strip()), "")
    if not line:
        return None, False
    if _ODDS.search(line):
        return None, True
    return (line if len(line) <= NOTE_CHARS else line[: NOTE_CHARS - 1].rstrip() + "…"), False


def _apply(ctx: Any, tx: Transaction, text: str, p: dict[str, Any], inv: Investigation,  # noqa: PLR0911, PLR0912
           reverted: list[int], outcomes: list[Any]) -> tuple[str, str]:  # one branch per proposal kind
    # rule: PR-12-11
    """PR-12-11 steps 4-5 for one proposal: ("did", words) when it was validated and applied, else ("not", why)."""
    st = tx.state
    pc = pc_of(st)
    kind = str(p.get("kind") or "")
    if kind == "explain":
        return "did", ""
    turn = str(p.get("turn") or "")
    turn_id = ids.counter_id(ids.TURN, int(m.group(0))) if (m := re.search(r"\d+", turn)) else ""
    pending = kind == "take_back" and _pending(ctx, tx, turn_id)  # an unrolled turn: nothing spent, nothing to prove
    if kind not in NO_EVIDENCE and not pending and (why := _evidence(p, inv)):
        return "not", f"{kind.replace('_', ' ')}: {why}, so the record stands (INV-9)"
    if kind == "reframe":
        return _reframe(ctx, tx, p, outcomes)
    if kind == "take_back":
        if not turn_id or ctx.store.turn(turn_id) is None:
            return "not", "take back: no such turn"
        why, seqs = _take_back(ctx, tx, turn_id, f"report: take back {turn_id}")
        if why:
            return "not", f"take back {turn_id}: {why}"
        reverted += seqs
        if pending and not seqs:
            return "did", (f"took back turn {turn_no(turn_id)}: its offer is withdrawn and nothing was spent "
                           "(declare again)")
        return "did", (f"took back turn {turn_no(turn_id)}: everything it changed is undone and its roll is void "
                       "(an offer it opened or closed is gone: declare again)")
    if kind in ("refund", "deduct", "restore"):
        q = _quantity(st, pc, str(p.get("quantity") or ""))
        if pc is None or q is None:
            return "not", f"{kind}: no shown quantity called {p.get('quantity')!r}"
        cur = st.quantities[pc][q].current
        if kind == "restore":
            new = _value_as_of(ctx, pc, q, turn_id) if turn_id else None
            if new is None:
                return "not", f"restore: no {q} on record at {turn or 'that turn'}"
        else:
            amount = int(m.group(0)) if (m := re.search(r"\d+", str(p.get("amount") or ""))) else 0
            if not 0 < amount <= MAX_AMOUNT:
                return "not", f"{kind}: {amount} is not an amount between 1 and {MAX_AMOUNT}"
            new = cur + amount if kind == "refund" else cur - amount
        if why := _set_quantity(tx, pc, q, new, f"correction ({kind}): {_flat(text, 100)}"):
            return "not", f"{kind}: {why}"
        return "did", f"your {q} {cur} → {new}"
    if kind in ("remove_fact", "correct_testimony"):
        fid = str(p.get("fact_id") or "")
        f = st.facts.get(fid)
        if f is None or st.current_fact_id(f.subject, f.predicate) != fid or fid in st.seals or f.subject in st.seals:
            return "not", f"{kind.replace('_', ' ')}: {fid or 'no fact'} is not a current fact you can see"
        if kind == "correct_testimony" and f.source != "testimony":
            return "not", f"correct testimony: {fid} was not settled from what someone said"
        if f.predicate.startswith(CASE_PREDICATES):
            return "not", f"{kind.replace('_', ' ')}: {fid} is part of the mystery's clue trail, which only play changes"
        value = str(p.get("value") or "").strip() if kind == "correct_testimony" else ""
        if value and _copies_report(value, text):
            return "not", "correct testimony: the new words must be the corrected value, not the report"
        from engine.dm.fixer import plain_fact

        said = plain_fact(st, f)  # before the write: the fact as the player read it
        _write(tx, f.subject, f.predicate, value or None, fid, "PR-12-12" if kind == "correct_testimony" else "12.3.6")
        what = _what(st, f.subject, f.predicate)
        if f.source == "testimony":
            return "did", (f"{what} is reworded on record: \"{value}\"" if value else
                           f"{what} (\"{_flat(f.value, 80)}\") is their words again, not a settled fact")
        return "did", f"\"{_flat(said, 120)}\" is no longer on record"
    if kind == "remove_condition":  # spec 032 P6: a wrong condition off the sheet (a footing cost's self-held pin)
        return _remove_condition(st, tx, p, text, ctx.rules)
    if kind == "set_fact":
        from engine.dm.fixer import resolve
        from engine.store.details import slot_of

        subject = resolve(st, str(p.get("subject") or ""))
        if subject is None:
            return "not", f"set fact: no one or nothing on record called {p.get('subject')!r}"
        e = st.entities[subject]
        if e.kind == "clue" or subject in st.seals:
            return "not", "set fact: a correction never delivers a clue or a sealed thing"
        key = str(p.get("key") or "").strip()
        slot = slot_of(key, ctx.rules, e.kind) if key else None
        pred = f"detail.{slot}" if slot else key
        value = str(p.get("value") or "").strip()
        if not pred or pred.startswith(("correction", "said.", "trg.", "log.")) or not value:
            return "not", "set fact: it needs a property and its value"
        if pred in IDENTITY or pred.startswith(CASE_PREDICATES):  # identity is entity data; clues are the spine
            held = ((e.name if pred == "name" else e.data.get("pronouns") or "not set") if pred in IDENTITY
                    else "the clue trail")
            return "not", f"set fact: {name(st, subject)}'s {pred} is fixed on record ({held}); the narration follows it"
        if _copies_report(value, text):
            return "not", "set fact: the value must be the corrected value, not the report's words"
        if slot not in INCIDENTAL_SLOTS and (why := _evidence(p, inv)):  # incidental fiction goes the player's way
            return "not", f"set fact: {why}, so the record stands (INV-9)"
        cur = st.current_fact_id(subject, pred)
        vis = st.facts[cur].visibility if cur in st.facts else "shown"
        _write(tx, subject, pred, value, cur, "12.3.6", visibility=vis)
        return "did", f"{_what(st, subject, pred)} is {value} on record"
    return "not", f"{kind}: not a correction the game makes"


def _remove_condition(st: WorldState, tx: Transaction, p: dict[str, Any], text: str,
                      rules: Any) -> tuple[str, str]:
    # rule: PR-12-11
    """`remove_condition` (spec 032 P6): `key` a `cinst.N`, or a condition id or name on `subject` (default the PC);
    evidence was checked by the caller (INV-9). A wound or unconsciousness is the harm ladder's, never removed here."""
    from engine.dm.dm_tools import HARM_OWNED
    from engine.dm.fixer import _cond_name, resolve

    key = str(p.get("key") or "").strip()
    who = resolve(st, str(p.get("subject") or "")) if p.get("subject") else pc_of(st)
    if key in st.conditions:
        inst = st.conditions[key]
    else:
        want = key.lower().removeprefix("cond.").replace(" ", "_")
        inst = next((c for c in st.conditions_on(who or "") if want and want in (
            c.condition_id.removeprefix("cond."), _cond_name(rules, c.condition_id).replace(" ", "_"))), None)
    if inst is None or inst.target in st.seals:
        return "not", f"remove condition: no condition {key!r} on record" + (f" on {name(st, who)}" if who else "")
    if inst.condition_id in HARM_OWNED:
        return "not", "remove condition: a wound goes with Vitality; restore it or take the turn back"
    tx.add(Event.of("condition_removed", source="correction", rule_id="12.3.6", instance_id=inst.instance_id,
                    reason=f"correction: {_flat(text, 100)}"))
    whose = "you are" if inst.target == pc_of(st) else f"{name(st, inst.target)} is"
    return "did", f"{whose} no longer {_cond_name(rules, inst.condition_id)}"


def _flat(s: Any, n: int) -> str:
    t = " ".join(str(s).split())
    return t if len(t) <= n else t[:n] + "…"


# a take-back first: the rest apply after it; a re-frame last, so the corrections before it count in the new frame
ORDER = {"take_back": 0, "restore": 1, "refund": 1, "deduct": 1, "reframe": 3}


def now_line(before: dict[str, str], after: dict[str, str]) -> str:  # rule: 12.5.8
    """12.15.9's `Now:` (DL-12-106): each shown value the report changed or restored, with what it was; when nothing
    changed, the sheet as it stands, so a restore is never silent and a mistaken belief is answered by the record."""
    changed = [f"{k} {v} (was {before.get(k, 'none')})" for k, v in after.items() if before.get(k) != v]
    if changed:
        return "Now: " + " · ".join(changed) + "."
    keep = [f"{k} {v}" for k, v in after.items() if k not in ("conditions", "holding") or v not in ("none", "nothing")]
    return "Now: nothing on your sheet changed: " + " · ".join(k for k in keep if not k.startswith("holding")) + "."


# ------------------------------------------------------------------------------------------- the report


def settle_dispute(ctx: Any, text: str, **_: Any) -> DisputeResult:  # rule: 12.3.6
    # rule: PR-12-11
    """PR-12-11 from the store. `ctx`: anything with `store`, `state`, `rules`, optional `tx` (the turn's open
    transaction; else a one-shot one), `model` (the Fixer's, routed by role) and `record_call`."""
    inv = investigate(ctx, text)  # one snapshot: nothing is written while the Fixer looks (dry runs use a copy)
    with _tx(ctx) as tx, _as_checked(ctx, inv):
        return _settle(ctx, tx, text, inv)


def _settle(ctx: Any, tx: Transaction, text: str, inv: Investigation, *, log: bool = True) -> DisputeResult:
    # rule: PR-12-11
    """PR-12-11 steps 4-6 on `tx`: every proposal validated and applied together, then the answer (found → Done /
    Not done → `Now:`); step 7's log when `log` (never for a dry run)."""
    start = len(tx.events)
    pc = pc_of(tx.state)
    before = sheet(tx.state, ctx.rules, pc)
    claims: list[DisputedClaim] = []
    results: list[tuple[list[str], list[str]]] = []
    reverted: list[int] = []
    outcomes: list[Any] = []
    todo = sorted(((i, j, p) for i, c in enumerate(inv.complaints)
                   for j, p in enumerate(c.get("proposals") or []) if isinstance(p, dict)),
                  key=lambda x: (ORDER.get(str(x[2].get("kind")), 2), x[0], x[1]))
    did: dict[int, list[str]] = {}
    nots: dict[int, list[str]] = {}
    kinds: dict[int, list[str]] = {}
    for i, _j, p in todo:
        status, words = _apply(ctx, tx, text, p, inv, reverted, outcomes)
        if words:
            (did if status == "did" else nots).setdefault(i, []).append(words)
        if status == "did":
            kinds.setdefault(i, []).append(str(p.get("kind")))
    for i, c in enumerate(inv.complaints):
        t = str(c.get("turn") or "")
        claims.append(DisputedClaim(believes=str(c.get("believes") or ""), category=str(c.get("category") or "other"),
                                    turn_id=ids.counter_id(ids.TURN, int(m.group(0)))
                                    if (m := re.search(r"\d+", t)) else None,
                                    verdict=str(c.get("verdict") or "unclear"), found=str(c.get("found") or ""),
                                    done_kinds=kinds.get(i, [])))
        results.append((did.get(i, []), nots.get(i, [])))
    after = sheet(tx.state, ctx.rules, pc)
    writes = [e.seq for e in tx.events[start:] if e.seq is not None]
    lines: list[str] = []
    for c, (done, refused) in zip(claims, results, strict=True):
        lines.append(c.found.strip() or "I can't pin that down from the record; say it again with the turn "
                     "number (/turn N shows a turn).")
        if done:
            lines.append("Done: " + "; ".join(done) + ".")
        lines += [f"Not done: {w}." for w in refused]
    lines.append(now_line(before, after))
    label = "CORRECTION" if writes else "FIX"
    block = note_block(lines[0], label, lines[1:])
    kind: DisputeKind = ("taken_back" if reverted else "corrected" if writes else
                         "not_found" if all(c.verdict == "unclear" and not c.found for c in claims) else "explained")
    records = _log(tx, ctx, text, inv, claims, results, kind=kind, answer=block.text, writes=writes,
                   reverted=reverted) if log else []
    if writes and log:
        rr = RulingRecord(signature=f"correction:{records[0]['report']}", situation=_flat(text, 300),
                          kind="rule_conflict", review_flag=True, tags=["correction", kind])
        tx.add(log_ruling(rr, tx.mint, store=ctx.store, staged=tx.events, rule_id="12.3.4"))
    return DisputeResult(kind, [block], events=tx.events[start:], reverted=reverted,
                         claim=claims[0] if claims else None, record=records[0] if records else None,
                         claims=claims, records=records, outcomes=outcomes,
                         correction={"writes": writes, "reverted": reverted} if writes else None)


# ------------------------------------------------------------------------------------------- dry runs (DL-12-117)


@contextmanager
def sandbox(ctx: Any) -> Iterator[Any]:  # rule: PR-12-11
    """A throwaway copy of the game (SQLite backup into a temp file) and a TurnContext on it, no transaction open;
    the play roles' model is the same routed model. Nothing done there reaches the real save.
    ponytail: copies the committed save only; a dispute turn stages nothing before the investigation"""
    from engine.dm.context import TurnContext

    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        path = Path(tmp) / "dry-run.db"
        dst = sqlite3.connect(path)
        try:
            ctx.store.conn.backup(dst)
        finally:
            dst.close()
        store = Store.open(path)
        try:
            yield TurnContext.for_store(store, model=getattr(ctx, "model", None), rules=ctx.rules,  # type: ignore[arg-type]
                                        config=getattr(ctx, "config", None))
        finally:
            store.close()


def screen(sx: Any, res: DisputeResult) -> str:  # rule: PR-12-11
    """What the player sees after the repair: the answer, any refusal or result a re-frame produced, and the pause
    then open (the re-framed OFFER, or the one still waiting), rendered as the turn renders it."""
    from engine.dm.narration import pause_blocks

    parts = [res.text]
    parts += [out.passage for out in res.outcomes if isinstance(out, Replayed) and out.passage]
    parts += [o["text"] for out in res.outcomes for o in out.oof if o.get("kind") in ("REDIRECT", "RESULT", "NOTE")]
    pause = sx.state.open_pause()
    if pause is not None:
        parts += [b.text for b in pause_blocks(sx, pause)]
    return "\n".join(parts)


class _Tape:
    """The play roles' answers in a dry run, kept so the real application gives the same ones (`_Again`): the screen
    the Fixer checked is the screen the player gets (a re-frame's Framer could otherwise answer differently)."""

    def __init__(self, inner: Any) -> None:
        self.inner, self.answers = inner, []
        self.provider = getattr(inner, "provider", "tape")

    def fill(self, role: Any, schema: dict[str, Any], packet: Any, *, turn_id: str | None, attempt: int,
             seq: int = 0) -> Any:
        res = self.inner.fill(role, schema, packet, turn_id=turn_id, attempt=attempt, seq=seq)
        self.answers.append((role, res.data))
        return res


class _Again:
    """Serves a dry run's taped answers, role by role and in order, then the real model."""

    def __init__(self, answers: list[tuple[Any, Any]], inner: Any) -> None:
        self.answers, self.inner = list(answers), inner
        self.provider = getattr(inner, "provider", "again")

    def fill(self, role: Any, schema: dict[str, Any], packet: Any, *, turn_id: str | None, attempt: int,
             seq: int = 0) -> Any:
        from engine.llm.offline import ScriptedModel

        k = next((i for i, (r, _) in enumerate(self.answers) if r == role), None)
        if k is None:
            return self.inner.fill(role, schema, packet, turn_id=turn_id, attempt=attempt, seq=seq)
        _, data = self.answers.pop(k)
        return ScriptedModel({role: [data]}, fallback=False).fill(role, schema, packet, turn_id=turn_id,
                                                                  attempt=attempt, seq=seq)


@contextmanager
def _as_checked(ctx: Any, inv: Investigation) -> Iterator[None]:
    """The decision applied for real is the one the Fixer last saw on the screen: its play-role answers are reused."""
    model = getattr(ctx, "model", None)
    if not inv.tape or inv.previewed != inv.complaints or model is None:
        yield
        return
    ctx.model = _Again(inv.tape, model)
    try:
        yield
    finally:
        ctx.model = model


def preview(ctx: Any, text: str, complaints: list[dict[str, Any]], calls: list[tuple[str, str, str]],
            tape: list[Any] | None = None) -> str:
    # rule: PR-12-11
    """PR-12-11 steps 4 and 6 (DL-12-117): a decision applied on a copy, validation included, and the screen the
    player would then see. The real game is untouched. `tape`, when given, receives the play roles' answers."""
    with sandbox(ctx) as sx, sx.store.transaction(getattr(ctx, "turn_id", None)) as tx:
        sx.tx = tx
        taped = _Tape(sx.model)
        sx.model = taped  # type: ignore[assignment]
        try:
            return screen(sx, _settle(sx, tx, text, Investigation(complaints=complaints, calls=list(calls)),
                                      log=False))
        finally:
            sx.tx = None
            if tape is not None:
                tape[:] = [a for a in taped.answers if getattr(a[0], "value", a[0]) != "fixer"]


def dispute(ctx: Any, text: str, **_: Any) -> str:  # rule: 12.3.6
    """engine/dm/context.py `DisputeHandler`: the OOF answer text."""
    return settle_dispute(ctx, text).text


def play_dm_dispute(ctx: Any, text: str) -> Any:  # rule: 12.3.6
    # rule: PR-12-11
    """`/fix` on a dm-tools game (spec 032 G11): the same investigation and repair (`settle_dispute`) in a turn of its
    own, marked `screen.dm_tools.fix`. No Narrator call: the answer is its blocks, and a re-frame's prose is the DM's
    passage (`_replay_dm`). Returns `dm_tools.Outcome`."""
    from engine.dm import oof as oofm
    from engine.dm.adjudication import AdjudicationRecord, PartEntry
    from engine.dm.dm_tools import Outcome
    from engine.dm.narration import shown_pause, turn_blocks
    from engine.dm.response import Flags, Response
    from engine.harm.threshold import ending_state
    from engine.store.records import Part, TurnRecord

    store = ctx.store
    turn_id = store.new_turn_id()
    store.save_turn(TurnRecord(turn_id=turn_id, input_verbatim=text))
    ctx.call_ids = []
    with store.transaction(turn_id) as tx:
        ctx.tx = tx
        try:
            rec = AdjudicationRecord(turn_id=turn_id, pc=pc_of(tx.state))
            res = settle_dispute(ctx, text)
            events = list(tx.events)
        finally:
            ctx.tx = None
    rec.add_writes(events)
    again = [o for o in res.outcomes if isinstance(o, Replayed)]
    rec.parts = [PartEntry.model_validate({"text": text, "class": "DISPUTE", "handled": "answered"})]
    rec.beats = [b for o in again for b in o.beats]
    st = store.state
    pause = st.open_pause()
    blocks, owned = turn_blocks(ctx, [*({"kind": b.kind, "text": b.text} for b in res.blocks),
                                      *(i for o in again for i in o.oof)], rec, pause)
    resp = Response(turn_id=turn_id, phase="ending" if ending_state(st) else "play",
                    fiction="\n\n".join(o.passage.strip() for o in again if o.passage.strip()),
                    oof_blocks=oofm.ordered(blocks), pause=shown_pause(pause, owned) if pause is not None else None,
                    flags=Flags())
    calls = store.model_calls(turn_id)
    stats = {**(again[-1].stats if again else {}), "fix": True, "kind": res.kind, "model_calls": len(calls),
             "tokens_in": sum(int(c.get("tokens_in") or 0) for c in calls),
             "tokens_out": sum(int(c.get("tokens_out") or 0) for c in calls),
             "latency_ms": sum(int(c.get("latency_ms") or 0) for c in calls)}
    tr = TurnRecord(turn_id=turn_id, input_verbatim=text, parts=[Part.model_validate({"text": text, "class": "DISPUTE"})],
                    writes=rec.write_seqs, beats=[b.frame_id for b in rec.beats if b.frame_id],
                    delivered_verbatim=resp.text(), model_calls=list(ctx.call_ids), screen={"dm_tools": stats},
                    cost_usd=float(sum(c.get("cost_usd") or 0.0 for c in calls)), latency_ms=int(stats["latency_ms"]),
                    pause=({"kind": pause.kind, "frame_id": pause.frame_id,
                            "options": [c.get("id", "") for c in pause.choices]} if pause is not None else None))
    store.save_turn(tr)
    return Outcome(response=resp, turn_record=tr)


# ------------------------------------------------------------------------------------------- the log (item 6)


def _log(tx: Transaction, ctx: Any, text: str, inv: Investigation, claims: list[DisputedClaim],
         results: list[tuple[list[str], list[str]]], *, kind: str, answer: str, writes: list[int],
         reverted: list[int]) -> list[dict[str, Any]]:  # rule: 12.3.6
    """12.3.6 item 6: one dispute record per complaint (sharing the report's id) in the corrections ledger, and one
    block per report in the save's review log, with the tool calls made (PR-12-11 step 7)."""
    ledger = list(tx.state.meta.get("corrections") or [])
    n = sum(1 for r in ledger if isinstance(r, dict) and r.get("type") == "dispute")
    report = f"rep.{1 + len({r.get('report') for r in ledger if isinstance(r, dict) and r.get('report')})}"
    tools = [f"{t}({a!r})" for t, a, _ in inv.calls]
    recs = []
    for k, (c, (done, refused)) in enumerate(zip(claims, results, strict=True)):
        outcome = "take_back" if reverted and done else "correct" if done else "not_found" if not c.found else "explain"
        recs.append({"type": "dispute", "id": f"dsp.{n + k + 1}", "report": report, "time": when_words(tx.state.time.now),
                     "turn": tx.turn_id, "words": text, "believes": c.believes, "category": c.category,
                     "verdict": c.verdict, "passage": {"turn": c.turn_id}, "found": c.found, "evidence": tools,
                     "done": done, "done_kinds": c.done_kinds, "not_done": refused, "outcome": outcome,
                     "upheld": c.verdict in ("player_right", "partly") or bool(done), "writes": writes,
                     "reverted": reverted})
    tx.add(Event.of("meta_set", source="correction", rule_id="12.3.6", key="corrections", value=[*ledger, *recs]))
    _review_log(ctx.store, report, recs, tools, inv, answer, kind)
    return recs


def review_log_path(store: Any) -> Any:
    """`saves/<campaign>.disputes.md`: beside the game file (12.3.6 item 6)."""
    path = getattr(store, "path", None)
    return path.with_name(f"{path.stem}.disputes.md") if path is not None else None


def _review_log(store: Any, report: str, recs: list[dict[str, Any]], tools: list[str], inv: Investigation,
                answer: str, kind: str) -> None:
    """One markdown block per report, newest last, for the owner to read. Wall-clock time lives only here."""
    path = review_log_path(store)
    if path is None or not recs:
        return
    now = datetime.now().strftime("%Y-%m-%d %H:%M")  # noqa: DTZ005 - the reader's local time; not game state
    r0 = recs[0]
    lines = [f"## {report} ({', '.join(r['id'] for r in recs)}) · {r0['turn']} · {now} (game: {r0['time']})", "",
             f"- **Player**: \"{r0['words']}\"", f"- **Investigated**: {'; '.join(tools) or 'nothing'}"]
    for r in recs:
        lines += [f"- **{r['id']}** ({r['category']}, {r['verdict']}, {r['passage']['turn'] or 'no turn'}): "
                  f"{r['believes'] or '(not understood)'}", f"  - found: {r['found']}",
                  *(f"  - done: {d}" for d in r["done"]), *(f"  - not done: {d}" for d in r["not_done"]),
                  f"  - outcome: {r['outcome']}{' (upheld)' if r['upheld'] else ''}"]
    lines += [f"- **Result**: {kind} · writes {', '.join(map(str, r0['writes'])) or 'none'} · reverted "
              f"{', '.join(map(str, r0['reverted'])) or 'none'}", "- **Answer**:",
              *(f"  > {ln}" for ln in answer.splitlines()), "", ""]
    try:
        new = not path.exists()
        with path.open("a", encoding="utf-8") as fh:
            if new:
                fh.write(f"# Disputes: {path.stem.removesuffix('.disputes')}\n\nEvery /fix or reported error, newest "
                         "last (12.3.6 item 6; PR-12-11: the Fixer's investigation, what it found, what code applied, "
                         "Now:).\n\n")
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


__all__ = ["FIX_HINT", "DisputeResult", "DisputedClaim", "dispute", "dispute_stats", "now_line", "recompute",
           "review_log_path", "settle_dispute"]
