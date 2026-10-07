"""The adjudication pass of the turn loop: PR-12-1 T1–T6 (state, no prose).

    ctx = TurnContext.for_store(store, model=OfflineModel())
    result = run_turn(ctx, "I slip past the watchman. Is the ferry running tonight?")
    result.record        # AdjudicationRecord: what T7–T10 narrate from (engine/dm/adjudication.py)
    result.pause         # the open pause (PauseRecord) or None; result.offer is its OfferView when an OFFER
    result.writes        # the seqs written this turn (one transaction, T6)
    result = answer_pause(ctx, "commit")           # a pick from the API (game.answer): resumes the paused beat

T1 stores the message verbatim before anything else (the turn row survives a failed turn); T2–T6 run inside one
store transaction, so a model failure before T6 (ModelUnavailable, ModelRefused, ...) writes nothing and the turn
can be retried. The narration pass (T7–T12) is built on top of the returned `AdjudicationResult`.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from engine import ids
from engine.dm.adjudication import AdjudicationRecord, BeatEntry, OracleEntry, PartEntry, PauseEntry
from engine.dm.context import TurnContext
from engine.dm.roles.framer import framer_for
from engine.dm.roles.reader import FactQuestion, ReaderResult, read_message
from engine.dm.world_step import world_step
from engine.resolve.oracle import OracleQuestion, ask_oracle
from engine.resolve.pipeline import (
    BeatOutcome,
    PipelineEnv,
    PipelineResult,
    close_by_default,
    harm_hook_for,
    resume,
    run_beats,
)
from engine.retrieve.scene import pc_id
from engine.retrieve.triggers import get_active_triggers
from engine.store.events import WORLD, Event, PauseRecord
from engine.store.records import Part, TurnRecord
from engine.store.views import narrator_view

ORDER = ("SAFETY", "SESSION", "DISPUTE", "PENDING_ANSWER", "OOF_QUESTION", "FICTION_QUESTION")  # 12.2.2 step 2
RULE_ID = re.compile(r"\b(PR-\d{2}-\d+|T-\d{2}-\d+|WE-\d{2}-\d+|\d{2}\.\d+(?:\.\d+)?)\b")


class AdjudicationResult(BaseModel):
    """What T1–T6 hand the narration pass."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    turn_id: str
    record: AdjudicationRecord
    pause: PauseRecord | None = None
    offer: dict[str, Any] | None = None  # the OfferView of an open OFFER (contracts/engine-api.md)
    writes: list[int] = Field(default_factory=list)
    oof: list[dict[str, str]] = Field(default_factory=list)  # {kind, text}: blocks owed (12.15), rendered later
    view: dict[str, Any] = Field(default_factory=dict)  # the narrator view re-read after T6 (12.2.10)
    turn_record: TurnRecord
    reader: ReaderResult | None = None


# ------------------------------------------------------------------------------------------- entry points


def run_turn(ctx: TurnContext, message: str) -> AdjudicationResult:  # rule: PR-12-1
    """T1–T6 for one player message."""
    return _turn(ctx, message, choice=None)


def answer_pause(ctx: TurnContext, choice_id: str) -> AdjudicationResult:  # rule: 12.2.6
    """A pick from the open pause's choices (game.answer): a PENDING_ANSWER turn with no Reader call."""
    pause = ctx.store.state.open_pause()
    if pause is None or not any(c.get("id") == choice_id for c in pause.choices):
        raise ValueError(f"{choice_id!r} is not a choice of the open pause")
    return _turn(ctx, choice_id, choice=choice_id)


def _turn(ctx: TurnContext, message: str, *, choice: str | None) -> AdjudicationResult:
    store = ctx.store
    turn_id = store.new_turn_id()
    store.save_turn(TurnRecord(turn_id=turn_id, input_verbatim=message))  # T1 (rule: 12.2.5)
    exchanges = recent_exchanges(store, turn_id)
    ctx.call_ids = []
    oof: list[dict[str, str]] = []
    reader: ReaderResult | None = None
    with store.transaction(turn_id) as tx:
        ctx.tx = tx
        try:
            pc = pc_id(tx.state)
            rec = AdjudicationRecord(turn_id=turn_id, pc=pc)
            if choice is not None:
                rec.parts = [PartEntry.model_validate({"text": choice, "class": "PENDING_ANSWER"})]
                beats = _adjudicate_answer(ctx, rec, choice, oof)
            else:
                reader = read_message(ctx, message, exchanges=exchanges)  # T2
                rec.parts = [PartEntry.model_validate({"text": p.text, "class": p.cls}) for p in reader.parts]
                rec.triggers = [t.id for t in get_active_triggers(tx.state, ctx.rules)]  # T3 (cards: per role)
                beats = _adjudicate(ctx, rec, reader, message, oof)  # T4
            pause = tx.state.open_pause()
            if pause is None:
                world_step(ctx, rec, beats=beats)  # T5 (a pause jumps to T7: no world, no time)
                _turn_end(ctx, rec, oof)
            events = list(tx.events)
        finally:
            ctx.tx = None
    # T6: committed in one transaction; re-read the narrator view (12.2.10)
    rec.add_writes(events)
    pause = store.state.open_pause()
    if pause is not None:
        rec.pause = PauseEntry(kind=pause.kind, frame_id=pause.frame_id, prompt=pause.prompt,
                               options=[c.get("id", "") for c in pause.choices])
    tr = TurnRecord(turn_id=turn_id, input_verbatim=message,
                    parts=[Part.model_validate({"text": p.text, "class": p.cls}) for p in rec.parts],
                    beats=[b.frame_id for b in rec.beats if b.frame_id],
                    oracle_calls=[e.seq for e in events if e.type == "oracle_answered" and e.seq is not None],
                    pause=({"kind": pause.kind, "frame_id": pause.frame_id,
                            "options": [c.get("id", "") for c in pause.choices]} if pause else None),
                    writes=rec.write_seqs, model_calls=list(ctx.call_ids))
    store.save_turn(tr)
    offer = pause.detail.get("offer") if pause is not None and pause.kind == "offer" else None
    return AdjudicationResult(turn_id=turn_id, record=rec, pause=pause, offer=offer, writes=rec.write_seqs, oof=oof,
                              view=narrator_view(store.state), turn_record=tr, reader=reader)


# ------------------------------------------------------------------------------------------- T4


def _env(ctx: TurnContext) -> PipelineEnv:
    tx = ctx.need_tx()
    env = PipelineEnv(tx=tx, rules=ctx.rules, rng=ctx.rng, store=ctx.store, framer=framer_for(ctx),
                      pc=pc_id(tx.state) or "", auto_commit=ctx.auto_commit(), milestone=ctx.milestone)
    env.harm_hook = harm_hook_for(env)
    return env


def _take(rec: AdjudicationRecord, res: PipelineResult, oof: list[dict[str, str]], part: int | None) -> None:
    for out in res.outcomes:
        out.entry.part = part
        rec.beats.append(out.entry)
        oof.extend(out.oof)
    if res.queued:
        rec.notes.append("queued for the next declaration (01.2.3): " + "; ".join(res.queued))


def _adjudicate(ctx: TurnContext, rec: AdjudicationRecord, reader: ReaderResult, message: str,
                oof: list[dict[str, str]]) -> list[BeatOutcome]:  # rule: 12.2.2
    """T4 in 12.2.2's handling order; stop at the first pause."""
    tx = ctx.need_tx()
    outcomes: list[BeatOutcome] = []
    classes = [p.cls for p in reader.parts]
    for part in rec.parts:  # SAFETY first: act on it before anything else (12.5.7)
        if part.cls == "SAFETY":
            _safety(ctx, rec, part, oof)
    if "SAFETY" in classes:
        for p in rec.parts:
            p.handled = p.handled or "held"
        return outcomes
    for part in rec.parts:
        if part.cls == "SESSION":
            part.handled = "answered"
            rec.notes.append(f"session move: {part.text} (12.5)")
            oof.append({"kind": "NOTE", "text": session_answer(ctx, part.text)})
        elif part.cls == "DISPUTE":
            part.handled = "answered"
            oof.append({"kind": "NOTE", "text": (ctx.dispute or default_dispute)(ctx, part.text)})
    pause = tx.state.open_pause()
    if pause is not None and reader.pending_answer and any(c.get("id") == reader.pending_answer
                                                           for c in pause.choices):
        env = _env(ctx)
        res = _resume(ctx, env, pause, reader.pending_answer, oof)
        _take(rec, res, oof, next((i for i, p in enumerate(rec.parts) if p.cls == "PENDING_ANSWER"), None))
        outcomes += res.outcomes
        for p in rec.parts:
            if p.cls == "PENDING_ANSWER":
                p.handled = "resolved"
        if tx.state.open_pause() is not None:
            _hold(rec)
            return outcomes
    for part in rec.parts:
        if part.cls == "OOF_QUESTION":
            part.handled = "answered"
            oof.append({"kind": "NOTE", "text": oof_answer(ctx, part.text)})
    _fiction_questions(ctx, rec, reader.fact_questions)
    for part in rec.parts:
        if part.cls == "FICTION_QUESTION":
            part.handled = "answered"
        elif part.cls == "SPEECH":
            part.handled = "answered"  # a free activity; whether an NPC answers is the NPC's (12.2.9)
    plans = reader.plans(actor=rec.pc or "", declared_seq=tx.state.last_seq, mint=tx.mint) if rec.pc else []
    if reader.clarifying_question and not plans:  # 01.2.4: at most one, and only when no reading can be assumed
        _clarify(ctx, reader.clarifying_question)
        _hold(rec)
        return outcomes
    if not plans:
        return outcomes
    if reader.clarifying_question:
        rec.notes.append(f"assumed reading (01.2.4): {reader.restatement}")
    env = _env(ctx)
    pause = tx.state.open_pause()
    if pause is not None:  # a new declaration with a pause open: 12.2.6's defaults
        res = close_by_default(env, pause)
        _take(rec, res, oof, None)
        outcomes += res.outcomes
    decl = next((i for i, p in enumerate(rec.parts) if p.cls == "DECLARATION"), None)
    res = run_beats(env, plans)
    _take(rec, res, oof, decl)
    outcomes += res.outcomes
    for p in rec.parts:
        if p.cls == "DECLARATION":
            p.handled = "paused" if res.pause else "resolved"
    _harm_followups(ctx, env, rec, oof)
    return outcomes


def _adjudicate_answer(ctx: TurnContext, rec: AdjudicationRecord, choice: str,
                       oof: list[dict[str, str]]) -> list[BeatOutcome]:
    pause = ctx.state.open_pause()
    assert pause is not None
    env = _env(ctx)
    res = _resume(ctx, env, pause, choice, oof)
    _take(rec, res, oof, 0)
    rec.parts[0].handled = "resolved"
    _harm_followups(ctx, env, rec, oof)
    return res.outcomes


def _resume(ctx: TurnContext, env: PipelineEnv, pause: PauseRecord, choice: str,
            oof: list[dict[str, str]]) -> PipelineResult:  # rule: 12.2.6
    if pause.kind == "last_chance":
        _last_chance(ctx, pause, choice, oof)
        return PipelineResult()
    return resume(env, pause, choice)


def _hold(rec: AdjudicationRecord) -> None:
    for p in rec.parts:
        if not p.handled:
            p.handled = "held"


def _clarify(ctx: TurnContext, question: str) -> None:  # rule: 01.2.4
    tx = ctx.need_tx()
    rec = PauseRecord(pause_id=tx.mint(ids.PAUSE), kind="clarify", prompt=question, choices=[], default_choice=None,
                      detail={"stage": "clarify", "plan": None})
    tx.add(Event.of("pause_opened", source="engine", rule_id="01.2.4", pause=rec))


# ------------------------------------------------------------------------------------------- questions


def _fiction_questions(ctx: TurnContext, rec: AdjudicationRecord, questions: Sequence[FactQuestion]) -> None:
    # rule: 01.3.8
    """01.3.8: from state (the permitted slice), else the World-Fact Oracle (PR-01-4). A settled key is read,
    never re-asked (01.15.7), so the same question gets the same answer and no new draw."""
    tx = ctx.need_tx()
    pc = rec.pc or "dm"
    rungs = [r["id"] for r in ctx.rules.resolution["oracle"]["rungs"]]
    for q in questions:
        st = tx.state
        subject = q.subject if q.subject in st.entities else WORLD
        pred = ids.slug(q.predicate)[:60]
        fid = st.current_fact_id(subject, pred)
        if fid is not None and st.facts[fid].visibility != "sealed":
            rec.oracle.append(OracleEntry(question=q.predicate, answer=_yes_no(st.facts[fid].value), fact_id=fid,
                                          subject=subject, predicate=pred))
            continue
        odds = q.odds_rung if q.odds_rung and q.odds_rung in rungs else "even"
        res = ask_oracle(OracleQuestion(subject=subject, predicate=pred, question=q.predicate, odds=odds, asker=pc),
                         state=st, rules=ctx.rules, rng=ctx.rng, mint=tx.mint, store=ctx.store, staged=tx.events,
                         free_cap=ctx.free_cap)
        tx.add_all(res.events)
        if res.status == "refused":
            rec.notes.append(f"oracle: {res.reason}")
            continue
        words = _yes_no(res.answer)
        if res.twist:
            words += f", but {res.qualifier}"
        if res.extreme:
            words += ", and " + " ".join(str(w) for w in res.meaning)
        rec.oracle.append(OracleEntry(question=q.predicate, answer=words, fact_id=res.fact_id, subject=subject,
                                      predicate=pred))


def _yes_no(v: Any) -> str:
    if v is True:
        return "yes"
    if v is False:
        return "no"
    return str(v)


def oof_answer(ctx: TurnContext, text: str) -> str:  # rule: 12.5.10
    """12.5.10: a rule id → its text (first lines); odds → the OFFER shows them before anything is spent."""
    m = RULE_ID.search(text)
    if m:
        from engine.build.compile_cards import load_cards

        idx = load_cards()
        if m.group(1) in idx:
            card = idx.get(m.group(1))
            return f"{card.id} {card.title}: " + " ".join(card.body.split())[:400]
    low = text.lower()
    if any(w in low for w in ("odds", "chance", "what would it take", "dc", "roll")):
        return ("Declare what you try: the OFFER shows the odds, stakes and costs before anything is rolled, and "
                "withdrawing spends nothing (01.7.1).")
    return "Out-of-fiction question noted: the codex shows your sheet, abilities, conditions and journal (12.5.10)."


def session_answer(ctx: TurnContext, text: str) -> str:  # rule: 12.5.3
    low = text.lower()
    if "recap" in low or "where were we" in low:
        return "Recap: generated from the record (12.5.3)."
    if any(w in low for w in ("break", "pause", "stop for now", "end")):
        return "The game is saved at this point; pick up whenever you like (12.5.4)."
    return "Session move noted (12.5)."


def default_dispute(ctx: TurnContext, text: str) -> str:  # rule: 12.3.6
    """TODO(engine/audit dispute handling, PR-12-4/12.3.6): the full test (store vs narration). Here: quote the
    last exchange from the turn log, OOF, so the player sees exactly what was said; no fact is created (INV-9)."""
    last = recent_exchanges(ctx.store, ctx.turn_id or "", n=1)
    if not last:
        return "Nothing earlier in the turn log to check against."
    said, delivered = last[-1]
    return f"From the turn log — you: \"{said}\"; the DM: \"{delivered[:300]}\""


def _safety(ctx: TurnContext, rec: AdjudicationRecord, part: PartEntry, oof: list[dict[str, str]]) -> None:
    # rule: 12.5.7
    from engine.audit.safety import handle_safety_part, safety_fact

    tx = ctx.need_tx()
    resp = handle_safety_part(part.text)
    part.handled = "answered"
    oof.append({"kind": "NOTE", "text": resp.oof_line})
    rec.notes.append(f"safety: adjust by {resp.reframing} ({resp.chosen_by})")
    if resp.record is not None:
        tx.add(safety_fact(resp.record, tx.state, tx.mint))
    ledger = list(tx.state.meta.get("safety.ledger") or [])
    tx.add(Event.of("meta_set", source="player", rule_id="12.3.7", key="safety.ledger", value=[*ledger, resp.ledger]))


# ------------------------------------------------------------------------------------------- harm, end of turn


def _harm_followups(ctx: TurnContext, env: PipelineEnv, rec: AdjudicationRecord,
                    oof: list[dict[str, str]]) -> None:  # rule: PR-07-5
    """A harm that opened the Threshold pauses on the last-chance menu (engine/harm/threshold.py)."""
    if not env.threshold_due or ctx.state.open_pause() is not None:
        return
    from engine.harm.ctx import HarmCtx
    from engine.harm.threshold import Situation, open_threshold

    pc = env.threshold_due[0]
    victor = next((b.targets[0] for b in reversed(rec.beats) if b.targets), None)
    op = open_threshold(HarmCtx(state=ctx.state, mint=ctx.mint, rules=ctx.rules, rng=ctx.rng), pc,
                        Situation(victor=victor))
    ctx.need_tx().add_all(op.events)
    oof.append({"kind": "LAST_CHANCE", "text": op.text})


def _last_chance(ctx: TurnContext, pause: PauseRecord, choice: str, oof: list[dict[str, str]]) -> None:
    # rule: PR-07-5
    """A last-chance pick: the menu is rebuilt from state (TODO(engine/harm/threshold.py): persist the menu or
    the Situation in the pause detail, so a resumed game rebuilds exactly the one shown)."""
    from engine.harm.ctx import HarmCtx
    from engine.harm.threshold import Situation, build_menu, choose

    pc = pc_id(ctx.state) or ""
    hctx = HarmCtx(state=ctx.state, mint=ctx.mint, rules=ctx.rules, rng=ctx.rng)
    menu = build_menu(hctx, pc, Situation(victor=pause.detail.get("victor")))
    ch = choose(hctx, pc, menu, choice, pause_id=pause.pause_id)
    ctx.need_tx().add_all(ch.events)
    oof.append({"kind": "LAST_CHANCE", "text": f"chosen: {choice}"})


def _turn_end(ctx: TurnContext, rec: AdjudicationRecord, oof: list[dict[str, str]]) -> None:  # rule: 07.2.7
    """At the PC's turn end: the dying check while Dying (h.07.dying_check is M2; the M1 loop calls it)."""
    from engine.harm.apply import dying_check
    from engine.harm.ctx import HarmCtx
    from engine.harm.state import DYING, harm_state

    pc = rec.pc
    if not pc or harm_state(ctx.state, pc) != DYING:
        return
    res = dying_check(HarmCtx(state=ctx.state, mint=ctx.mint, rules=ctx.rules, rng=ctx.rng), pc)
    ctx.need_tx().add_all(res.events)
    rec.notes.append(f"dying check: {res.result}")
    if res.threshold:
        env = _env(ctx)
        env.threshold_due.append(pc)
        _harm_followups(ctx, env, rec, oof)


# ------------------------------------------------------------------------------------------- the turn log


def recent_exchanges(store: Any, turn_id: str, n: int = 4) -> list[tuple[str, str]]:  # rule: 12.2.4
    """The last `n` exchanges before `turn_id`, verbatim, oldest first (from the turn log)."""
    parsed = ids.parse_counter_id(turn_id) if turn_id else None
    if not parsed:
        return []
    out: list[tuple[str, str]] = []
    for k in range(parsed[1] - 1, 0, -1):
        tr = store.turn(ids.counter_id(ids.TURN, k))
        if tr is not None:
            out.append((tr.input_verbatim, tr.delivered_verbatim))
        if len(out) >= n:
            break
    return list(reversed(out))


__all__ = ["AdjudicationResult", "BeatEntry", "answer_pause", "recent_exchanges", "run_turn"]
