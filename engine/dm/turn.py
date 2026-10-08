"""The adjudication pass of the turn loop: PR-12-1 T1–T6 (state, no prose).

    ctx = TurnContext.for_store(store, model=OfflineModel())
    result = run_turn(ctx, "I slip past the watchman. Is the ferry running tonight?")
    result.record        # AdjudicationRecord: what T7–T10 narrate from (engine/dm/adjudication.py)
    result.pause         # the open pause (PauseRecord) or None; result.offer is its OfferView when an OFFER
    result.writes        # the seqs written this turn (one transaction, T6)
    result = answer_pause(ctx, "commit")           # a pick from the API (game.answer): resumes the paused beat

    out = play_turn(ctx, "I slip past the watchman.")   # T1–T12: out.response is the delivered Response
    out = play_answer(ctx, "commit")                    # the same for a pick (engine/dm/narration.py does T7–T12)

T1 stores the message verbatim before anything else (the turn row survives a failed turn); T2–T6 run inside one
store transaction, so a model failure before T6 (ModelUnavailable, ModelRefused, ...) writes nothing and the turn
can be retried. The narration pass (T7–T12, engine/dm/narration.py) runs on the returned `AdjudicationResult`;
`play_turn` / `play_answer` run both and return a `TurnOutcome` (the delivered Response and the full TurnRecord).

Scenes (PR-12-7, PR-12-1 T12): a scene cut at T12 leaves `scene.frame_next`; the next turn's first step asks the
Director to frame the next scene (with the player's new message as the declared purpose) before T2. A cut the
player asks for in this message is framed in this turn, after T5 (the Director confirms `cut_now`).
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from engine import ids
from engine.dm.adjudication import AdjudicationRecord, BeatEntry, OracleEntry, PartEntry, PauseEntry
from engine.dm.context import TurnContext
from engine.dm.narration import FRAME_NEXT, TurnOutcome, moves_on, narrate_turn, stays
from engine.dm.roles import director as director_role
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
from engine.world.common import trigger_raised

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


def play_turn(ctx: TurnContext, message: str) -> TurnOutcome:  # rule: PR-12-1
    """The whole turn loop for one player message: T1–T6 (`run_turn`) then T7–T12 (`narrate_turn`)."""
    return _narrate(ctx, run_turn(ctx, message), message)


def play_answer(ctx: TurnContext, choice_id: str) -> TurnOutcome:  # rule: 12.2.6
    """`game.answer(choice_id)`: the pick (`answer_pause`) then the narration pass."""
    return _narrate(ctx, answer_pause(ctx, choice_id), choice_id)


def play_dispute(ctx: TurnContext, text: str) -> TurnOutcome:  # rule: 12.3.6
    """`game.dispute(text)` (the /fix command): a DISPUTE part with no Reader call (PR-12-4), then T7–T12. A
    reliance CHOICE (keep the result or rewind) opens a `clarify` pause answered by `play_answer`."""
    return _narrate(ctx, _turn(ctx, text, choice=None, dispute=True), text)


NARRATION_PENDING = "narration_pending"  # meta: T6 committed, T7–T12 failed; the next call re-runs them


def _narrate(ctx: TurnContext, adj: AdjudicationResult, message: str) -> TurnOutcome:  # rule: PR-12-1
    """T7–T12; when they fail after T6 committed (a model error), the turn's record is kept as meta
    `narration_pending` so the next call re-runs T7–T11 from the written state (contracts/engine-api.md Errors):
    the player never sees prose the store does not back."""
    try:
        return narrate_turn(ctx, adj, message)
    except Exception:
        pending = {"turn_id": adj.turn_id, "message": message, "record": adj.record.dump(),
                   "oof": list(adj.oof)}
        ctx.store.append([Event.of("meta_set", source="engine", rule_id="PR-12-1", key=NARRATION_PENDING,
                                   value=pending)], turn_id=adj.turn_id)
        raise


def resume_narration(ctx: TurnContext) -> TurnOutcome | None:  # rule: PR-12-1
    """Re-run T7–T12 for a turn whose narration failed after T6 (meta `narration_pending`); None when nothing is
    pending. Raises again (the meta stays) if the model fails again."""
    store = ctx.store
    pending = store.state.meta.get(NARRATION_PENDING)
    if not isinstance(pending, dict):
        return None
    turn_id = str(pending["turn_id"])
    rec = AdjudicationRecord.model_validate(pending["record"])
    pause = store.state.open_pause()
    tr = store.turn(turn_id) or TurnRecord(turn_id=turn_id, input_verbatim=str(pending.get("message") or ""))
    adj = AdjudicationResult(turn_id=turn_id, record=rec, pause=pause, writes=rec.write_seqs,
                             offer=pause.detail.get("offer") if pause is not None and pause.kind == "offer" else None,
                             oof=list(pending.get("oof") or []), view=narrator_view(store.state), turn_record=tr)
    out = narrate_turn(ctx, adj, str(pending.get("message") or ""))
    store.append([Event.of("meta_set", source="engine", rule_id="PR-12-1", key=NARRATION_PENDING, value=None)],
                 turn_id=turn_id)
    return out


def answer_pause(ctx: TurnContext, choice_id: str) -> AdjudicationResult:  # rule: 12.2.6
    """A pick from the open pause's choices (game.answer): a PENDING_ANSWER turn with no Reader call."""
    pause = ctx.store.state.open_pause()
    if pause is None or not any(c.get("id") == choice_id for c in pause.choices):
        raise ValueError(f"{choice_id!r} is not a choice of the open pause")
    return _turn(ctx, choice_id, choice=choice_id)


def _turn(ctx: TurnContext, message: str, *, choice: str | None, dispute: bool = False) -> AdjudicationResult:
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
            elif dispute:
                rec.parts = [PartEntry.model_validate({"text": message, "class": "DISPUTE", "handled": "answered"})]
                _dispute(ctx, message, oof)
                beats = []
            else:
                _scene_open_step(ctx, rec, message)  # PR-12-7: frame a pending (or missing) scene first
                reader = read_message(ctx, message, exchanges=exchanges)  # T2
                rec.parts = [PartEntry.model_validate({"text": p.text, "class": p.cls}) for p in reader.parts]
                rec.triggers = [t.id for t in get_active_triggers(tx.state, ctx.rules)]  # T3 (cards: per role)
                beats = _adjudicate(ctx, rec, reader, message, oof)  # T4
            pause = tx.state.open_pause()
            if pause is None and not dispute:  # a dispute is out of fiction: no world step, no time
                world_step(ctx, rec, beats=beats)  # T5 (a pause jumps to T7: no world, no time)
                _turn_end(ctx, rec, oof)
                if choice is None:
                    _director_step(ctx, rec, message)  # lead injection, the player's cut, an answered agenda
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
            note = {"kind": "NOTE", "text": session_answer(ctx, part.text)}
            if note not in oof:  # two parts asking the same thing get one answer
                oof.append(note)
        elif part.cls == "DISPUTE":
            part.handled = "answered"
            _dispute(ctx, part.text, oof)
    if any(p.cls == "DISPUTE" for p in rec.parts) and tx.state.open_pause() is not None \
            and tx.state.open_pause().detail.get("stage") == "dispute":  # type: ignore[union-attr]
        _hold(rec)  # the reliance CHOICE (pause point 9) stops the rest
        return outcomes
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
            note = {"kind": "NOTE", "text": oof_answer(ctx, part.text)}
            if note not in oof:
                oof.append(note)
    _fiction_questions(ctx, rec, reader.fact_questions)
    for part in rec.parts:
        if part.cls == "FICTION_QUESTION":
            part.handled = "answered"
        elif part.cls == "SPEECH":
            part.handled = "answered"  # a free activity; whether an NPC answers is the NPC's (12.2.9)
    kind = rest_kind(message) if "DECLARATION" in classes and rec.pc else None
    held = tx.state.open_pause()
    if kind is not None and held is not None and held.detail.get("stage") in ("offer", "warning", "redirect",
                                                                              "near_miss"):
        res = close_by_default(_env(ctx), held)  # 12.2.6: the rest is a new declaration; the pause closes first
        _take(rec, res, oof, None)
        outcomes += res.outcomes
    if kind is not None and tx.state.open_pause() is None:
        _rest(ctx, rec, kind, oof)
        for p in rec.parts:
            if p.cls == "DECLARATION":
                p.handled = "resolved"
        return outcomes
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
    if pause.detail.get("stage") == "dispute":
        _dispute_choice(ctx, pause, choice, oof)
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


CODEX_WORDS = {"sheet": ("sheet", "my stats", "my character"), "abilities": ("abilities", "ability", "powers"),
               "conditions": ("conditions", "condition", "status"), "journal": ("journal", "what do i know"),
               "threads": ("threads", "leads", "quests")}


STUCK_WORDS = ("what are my options", "my options", "what can i do", "what now", "what should i do", "i'm stuck",
               "i am stuck", "im stuck", "don't know what to do", "dont know what to do", "not sure what to do",
               "how do i start", "where do i start")
NEW_WORDS = ("new to this", "new here", "first time", "never played", "how do i play", "how does this work",
             "how does this game work")
HOW_TO_PLAY = ('You play by saying what your character does or says, in plain words: "I look around", "I ask the '
               'smith about the road", "I head for the heath". Ask what you see or who is here and the story '
               'answers. Type "what are my options?" for ideas, or "sheet" or "journal" to see your character.')
OOF_HELP = ('You can ask about a rule by its number, type "sheet", "abilities", "conditions" or "journal", ask '
            '"what are my options?", or just say what your character does.')


def stuck_answer(state: Any) -> str:  # rule: 12.8.5
    # coarse: 12.8.5 (leads from active threads, the people here and the places within reach; no lead injection when
    # state holds none)
    """[LEADS] two or three concrete ways forward drawn from state, closed with "or anything else" (12.15.10)."""
    from engine.dm.oof import short_text
    from engine.dm.player_text import entity_names, second_person
    from engine.world.places import location, reachable
    from engine.world.social import thread_list

    shown = entity_names(state)
    threads = sorted((t for t in thread_list(state) if t["status"] == "active" and t["id"] in shown),
                     key=lambda t: -int(t["weight"]))
    people = [shown[i] for i in (state.scene.cast_present if state.scene else [])
              if i in shown and state.entities[i].kind in ("npc", "companion")]
    here = location(state)
    places = [shown[x.to] for x in (reachable(state, here) if here else []) if x.to != here and x.to in shown]
    leads = [*(f"{short_text(second_person(t['text'] or t['name']))} (an open thread)" for t in threads[:1]),
             *(f"{p}, here with you" for p in people[:1]),
             *(f"{p}, within reach" for p in places[:1]),
             *(f"{short_text(second_person(t['text'] or t['name']))} (an open thread)" for t in threads[1:2])][:3]
    if not leads:
        return "[LEADS] Nothing pressing is on record yet: look around, or anything else you have in mind."
    return "[LEADS] Some ways forward — or anything else you have in mind:\n" + "\n".join(f"  • {x}" for x in leads)


def oof_answer(ctx: TurnContext, text: str) -> str:  # rule: 12.5.10
    """12.5.10: a rule id → its card (engine.dm.codex); a codex section by name; odds → the OFFER shows them;
    "what can I do?" → the stuck answer (12.8.5)."""
    from engine.dm.codex import codex

    m = RULE_ID.search(text)
    if m:
        return codex(ctx.state, f"rules {m.group(1)}", ctx.rules).text
    low = text.lower().replace("’", "'")
    if any(w in low for w in STUCK_WORDS):
        return stuck_answer(ctx.state)
    if any(w in low for w in NEW_WORDS):
        return HOW_TO_PLAY
    for section, words in CODEX_WORDS.items():
        if any(w in low for w in words):
            return codex(ctx.state, section, ctx.rules).text
    if any(w in low for w in ("odds", "chance", "what would it take", "dc", "roll")):
        return ("Declare what you try: the OFFER shows the odds, stakes and costs before anything is rolled, and "
                "withdrawing spends nothing (01.7.1).")
    return OOF_HELP


def session_answer(ctx: TurnContext, text: str) -> str:  # rule: 12.5.3
    low = text.lower()
    if "recap" in low or "where were we" in low:
        from engine.dm.oof import recap_block

        return recap_block(ctx.state).text
    if any(w in low for w in ("break", "pause", "stop for now", "end")):
        return "The game is saved at this point; pick up whenever you like (12.5.4)."
    if any(w in low for w in NEW_WORDS):
        return HOW_TO_PLAY
    return ('Say "recap" to hear where things stand, or "break" to stop for now (the game is saved); otherwise '
            "just say what your character does.")


def _dispute(ctx: TurnContext, text: str, oof: list[dict[str, str]]) -> None:  # rule: 12.3.6
    """12.3.6 through engine.dm.dispute (or an injected `ctx.dispute`); a reliance CHOICE becomes a pause
    (kind clarify, stage dispute) answered by `settle_dispute(..., choice=)`."""
    if ctx.dispute is not None:
        oof.append({"kind": "NOTE", "text": ctx.dispute(ctx, text)})
        return
    from engine.dm.dispute import settle_dispute

    res = settle_dispute(ctx, text)
    oof.extend({"kind": b.kind, "text": b.text} for b in res.blocks)
    if res.choices:
        tx = ctx.need_tx()
        rec = PauseRecord(pause_id=tx.mint(ids.PAUSE), kind="clarify", prompt=res.text.splitlines()[0] if res.text
                          else "Keep the result, or rewind?", choices=list(res.choices),
                          default_choice=res.choices[0]["id"], detail={"stage": "dispute", "text": text})
        tx.add(Event.of("pause_opened", source="engine", rule_id="12.3.4", pause=rec))


def _dispute_choice(ctx: TurnContext, pause: PauseRecord, choice: str, oof: list[dict[str, str]]) -> None:
    # rule: 12.3.4
    from engine.dm.dispute import settle_dispute

    tx = ctx.need_tx()
    tx.add(Event.of("pause_closed", source="player", rule_id="12.3.4", pause_id=pause.pause_id, choice=choice))
    res = settle_dispute(ctx, str(pause.detail.get("text") or ""), choice=choice)  # type: ignore[arg-type]
    oof.extend({"kind": b.kind, "text": b.text} for b in res.blocks)


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


# ------------------------------------------------------------------------------------------- rests

_REST = re.compile(r"\b(?:i|we|let'?s)\s+(?:\w+\s+){0,3}?(?:rest|sleep|make\s+camp|camp|bed\s+down|"
                   r"take\s+a\s+(?:breather|short\s+rest|long\s+rest|break)|catch\s+(?:my|our)\s+breath)\b"
                   r"(?!\s+of\b)", re.IGNORECASE)
_LONG = re.compile(r"\b(?:night|sleep|camp|bed\s+down|until\s+(?:dawn|morning)|long\s+rest|for\s+the\s+day)\b",
                   re.IGNORECASE)
_BREATHER = re.compile(r"\b(?:breather|catch\s+(?:my|our)\s+breath|a\s+moment|a\s+minute)\b", re.IGNORECASE)
REST_WORDS = {"breather": "a breather", "rest_short": "a short rest", "rest_long": "a long rest"}


def rest_kind(message: str) -> str | None:  # rule: 07.8.1
    """A declared rest and its kind (07.8.1: breather, short rest, long rest), or None."""
    if not _REST.search(message or ""):
        return None
    if _BREATHER.search(message):
        return "breather"
    return "rest_long" if _LONG.search(message) else "rest_short"


def _rest(ctx: TurnContext, rec: AdjudicationRecord, kind: str, oof: list[dict[str, str]]) -> None:  # rule: PR-07-8
    # coarse: 07.8.2 (the site from the place's kind when no rest_site is recorded: a settlement or building is a
    # haven, anywhere else a camp)
    """PR-07-8: refused when the rules forbid it now (07.8.1); else the rest's whole duration is advanced
    (00.7.2), its boundary marked at the end (handlers recover vitality, focus, uses); an interruption leaves the
    rest unfinished (the mark does not fire)."""
    from engine.harm.rest import best_quality, rest_duration, rest_payload, rest_refusal, rest_site
    from engine.time.scheduler import Mark, advance_time
    from engine.world.places import location, place_kind

    tx = ctx.need_tx()
    st = tx.state
    pc = rec.pc or ""
    why = rest_refusal(st, ctx.rules, pc, kind)
    words = REST_WORDS[kind]
    if why:
        rec.notes.append(f"{words} is not possible now: {why}")
        oof.append({"kind": "NOTE", "text": f"No rest yet: {why}."})
        return
    place = location(st, pc)
    site = rest_site(st, place) or ("haven" if place and place_kind(st, place) in ("settlement", "building")
                                    else "camp")
    quality = best_quality(st, pc, kind, site=site)
    amount, unit = rest_duration(ctx.rules, kind)
    unit = {"watches": "watch", "intervals": "interval", "hours": "hour", "rounds": "round"}.get(unit, unit)
    res = advance_time(ctx.time_ctx(), amount, unit, f"{kind} (07.8)",
                       marks=[Mark(kind, rest_payload(kind, quality, site))])
    if res.interrupt or res.unfired:
        rec.notes.append(f"{words} begins but is broken off before it is done")
        rec.notes.extend(n for n in res.narration if n)
        return
    rec.notes.append(f"the character takes {words}" + (" and wakes rested" if kind == "rest_long" else "")
                     + ("" if quality == "full" else " (a poor rest)"))


# ------------------------------------------------------------------------------------------- harm, end of turn


def _harm_followups(ctx: TurnContext, env: PipelineEnv, rec: AdjudicationRecord,
                    oof: list[dict[str, str]]) -> None:  # rule: PR-07-5
    """A harm that opened the Threshold pauses on the last-chance menu (engine/harm/threshold.py)."""
    if not env.threshold_due or ctx.state.open_pause() is not None:
        return
    if ctx.state.fact_value(env.threshold_due[0], "last_stand"):
        return  # rule: 07.5.9 -- in a Last Stand no new Threshold opens: the stand ends in death at turn end
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
    """A last-chance pick, resolved from the menu stored in the pause (exactly the one shown)."""
    from engine.harm.ctx import HarmCtx
    from engine.harm.threshold import choose

    pc = str(pause.detail.get("pc") or pc_id(ctx.state) or "")
    hctx = HarmCtx(state=ctx.state, mint=ctx.mint, rules=ctx.rules, rng=ctx.rng)
    ch = choose(hctx, pc, pause, choice)
    ctx.need_tx().add_all(ch.events)
    oof.append({"kind": "LAST_CHANCE", "text": f"chosen: {choice}"})
    if ch.gamble_offer:
        _gamble(ctx, pc, pause, oof)


def _gamble(ctx: TurnContext, pc: str, pause: PauseRecord, oof: list[dict[str, str]]) -> None:  # rule: 07.5.10
    # coarse: 07.5.10 (the last-chance menu already shows the Gamble's odds; picking it is its confirmation, so no
    # second OFFER is opened before the roll)
    """The Gamble, rolled once it is chosen: free, alive, a price to choose (the near-fail pause), or death."""
    from engine.harm.ctx import HarmCtx
    from engine.harm.threshold import menu_from_detail, resolve_gamble

    hctx = HarmCtx(state=ctx.state, mint=ctx.mint, rules=ctx.rules, rng=ctx.rng)
    g = resolve_gamble(hctx, pc, menu_from_detail(pause))
    ctx.need_tx().add_all(g.events)
    words = {"free": "you walk away free", "live": "you live, overlooked", "choose": "it nearly fails: choose a price",
             "death": "it fails"}
    oof.append({"kind": "LAST_CHANCE", "text": f"The Gamble: {words.get(g.result, g.result)}."})


def _turn_end(ctx: TurnContext, rec: AdjudicationRecord, oof: list[dict[str, str]]) -> None:  # rule: 07.2.7
    """At the PC's turn end: the dying check while Dying (h.07.dying_check is M2; the M1 loop calls it)."""
    from engine.harm.apply import dying_check
    from engine.harm.ctx import HarmCtx
    from engine.harm.state import DYING, harm_state, is_down

    pc = rec.pc
    if pc and _finish_last_stand(ctx, rec, pc):
        return
    if pc and is_down(ctx.state, pc):
        _wake(ctx, rec, pc)
        return
    if not pc or harm_state(ctx.state, pc) != DYING:
        return
    res = dying_check(HarmCtx(state=ctx.state, mint=ctx.mint, rules=ctx.rules, rng=ctx.rng), pc)
    ctx.need_tx().add_all(res.events)
    rec.notes.append(f"dying check: {res.result}")
    if res.threshold:
        env = _env(ctx)
        env.threshold_due.append(pc)
        _harm_followups(ctx, env, rec, oof)


def _wake(ctx: TurnContext, rec: AdjudicationRecord, pc: str) -> None:  # rule: 07.2.9
    # coarse: 07.6 (no victor in Milestone 1 takes a Down PC: nothing runs a disposition, so it wakes after an interval)
    """The PC went Down (a non-lethal fall, 07.2.9): out cold for one interval, then it wakes where it fell,
    Staggered, with its wounds. Without this the ladder stays frozen and every later harm is discarded."""
    from engine.harm.apply import wake
    from engine.harm.ctx import HarmCtx
    from engine.time.scheduler import advance_time

    advance_time(ctx.time_ctx(), 1, "interval", "down: out cold for an interval (07.2.9)")
    ctx.need_tx().add_all(wake(HarmCtx(state=ctx.state, mint=ctx.mint, rules=ctx.rules, rng=ctx.rng), pc))
    rec.notes.append("the character blacks out, and comes to a while later where they fell, staggered and hurt")


def _finish_last_stand(ctx: TurnContext, rec: AdjudicationRecord, pc: str) -> bool:  # rule: 07.5.9
    # coarse: 07.5.9 (the Last Stand is the PC's next whole turn after choosing it, not three counted actions)
    """The Last Stand chosen on an earlier turn ends when this turn of the PC's ends: death (both keys)."""
    from engine.harm.ctx import HarmCtx
    from engine.harm.state import DEAD, harm_state
    from engine.harm.threshold import DeathRefused, finish_last_stand

    tx = ctx.need_tx()
    if not ctx.state.fact_value(pc, "last_stand") or harm_state(ctx.state, pc) == DEAD:
        return False
    if any(e.type == "fact_set" and getattr(e.payload, "predicate", None) == "last_stand" for e in tx.events):
        return False  # chosen this turn: the stand is the next turn
    try:
        tx.add_all(finish_last_stand(HarmCtx(state=ctx.state, mint=ctx.mint, rules=ctx.rules, rng=ctx.rng), pc))
    except DeathRefused as exc:
        rec.notes.append(f"the last stand ends, and yet the record refuses a death: {exc}")
        return True
    rec.notes.append("the last stand is over: the character falls, and does not rise again")
    return True


# ------------------------------------------------------------------------------------------- scenes


def _scene_entry(ctx: TurnContext, rec: AdjudicationRecord, start: Any, *, ended: str | None) -> None:
    from engine.dm.adjudication import SceneEntry

    rec.scene = SceneEntry(cut=ended is not None, ended=ended, started=start.scene_id,
                           header=director_role.scene_header(ctx.state))
    push = start.push or {}
    if push.get("entry"):
        rec.notes.append(f"the scene's impetus (12.4.3): {push['entry']}")
    test = start.test or {}
    if test.get("result") in ("altered", "interrupted"):
        what = test.get("event") or "; ".join(str(a) for a in test.get("adjustments") or [])
        rec.notes.append(f"the scene opens {test['result']}" + (f": {what}" if what else ""))
    rec.notes += [n for n in start.narration if n]


def _scene_open_step(ctx: TurnContext, rec: AdjudicationRecord, message: str) -> None:  # rule: PR-12-7
    """Before T2: frame the scene a T12 cut left pending (the player's new message is its declared purpose), or
    one when there is none; after a dead-air cut a player who stays re-opens the last scene (12.4.2 (7))."""
    from engine.world.scenes import reopen_scene

    tx = ctx.need_tx()
    st = tx.state
    pending = st.meta.get(FRAME_NEXT)
    if st.scene is not None or pc_id(st) is None:
        if pending:
            tx.add(Event.of("meta_set", source="engine", rule_id="PR-12-7", key=FRAME_NEXT, value=None))
        return
    clear = Event.of("meta_set", source="engine", rule_id="PR-12-7", key=FRAME_NEXT, value=None)
    if isinstance(pending, dict) and pending.get("reason") == "dead_air" and stays(message) and st.last_scene:
        reopen_scene(ctx.time_ctx())
        tx.add(clear)
        rec.notes.append("you stay: the scene goes on (12.4.2)")
        return
    reason = pending.get("reason") if isinstance(pending, dict) else "no scene"
    d = director_role.direct(ctx, situation=f"scene start: frame the next scene (after: {reason})",
                             player_message=message)
    start = director_role.frame_scene(ctx, d, reason=str(reason), interrupt=reason == "interrupt",
                                      purpose_declared=bool(message.strip()))
    if pending:
        tx.add(clear)
    _scene_entry(ctx, rec, start, ended=None)


def _heads_for(st: Any, rec: AdjudicationRecord) -> str | None:  # rule: 10.1.3
    """The reachable place another than here that a resolved Move beat this turn headed for (travel)."""
    from engine.world.places import location, reachable

    here = location(st)
    ways = {x.to for x in reachable(st, here)} if here else set()
    for b in rec.beats:
        done = b.degree in ("success", "critical_success") or b.success_at_cost or             b.gate_words.startswith("no roll")
        if done and b.approach_words.startswith("verb.move") and b.targets and b.targets[0] != here and b.targets[0] in ways:
            return b.targets[0]
    return None


def _director_step(ctx: TurnContext, rec: AdjudicationRecord, message: str) -> None:  # rule: 12.4.2
    # rule: 12.8.2
    """After T5: ask the Director when the player moves on, something settled this turn could answer the scene's
    question, or a lead injection fired. A lead is written now (PR-12-3) so this turn narrates it; the player's
    own cut is framed now (PR-12-1 T12); an answered agenda is marked and cut at T12."""
    from engine.world.pacing import inject_lead
    from engine.world.scenes import mark_agenda_answered, note_cut

    st = ctx.state
    if st.scene is None or rec.scene.started == st.scene.scene_id:
        return
    dest = _heads_for(st, rec)
    moving = moves_on(message) or dest is not None
    lead = trigger_raised(st, "trg.lead_injection")
    settled = any(b.degree for b in rec.beats) or any(o.completed for o in rec.omens) \
        or any(a.source == "refusal" for a in rec.npc_actions)
    if not (moving or lead or settled):
        return
    from engine.dm.world_step import happened_text

    situation = "; ".join(x for x in ("the player may be moving on" if moving else "",
                                      "a lead injection fired" if lead else "",
                                      "something settled this turn: is the scene's question answered?"
                                      if settled else "") if x)
    d = director_role.direct(ctx, situation=situation, player_message=message, happened=happened_text(rec),
                             quiet_turns=int(st.meta.get("dead_air") or 0))
    if dest is not None:  # 12.4.2 (2): a place change ends the scene; the player named where (10.1.3)
        d.cut_now = True
        d.next_scene.place = dest
    tctx = ctx.time_ctx()
    if lead:
        try:
            inj = inject_lead(tctx)
        except Exception as exc:  # noqa: BLE001 - no eligible source: logged, the counter stays for next time
            rec.notes.append(f"lead injection held: {exc}")
        else:
            names = {i: ctx.state.entities[i].name for i in (inj.source_id, inj.thread) if i in ctx.state.entities}
            rec.notes.append(f"a lead arrives ({inj.form}): it points toward "
                             f"{names.get(inj.thread or '', 'an open thread')}"
                             + (f", through {names[inj.source_id]}" if inj.source_id in names else ""))
    if not d.cut_now:
        return
    if moving:
        old = ctx.state.scene.scene_id if ctx.state.scene else None
        note_cut(tctx, "player_cut")
        start = director_role.frame_scene(ctx, d, reason="player_cut", purpose_declared=True)
        _scene_entry(ctx, rec, start, ended=old)
        if ctx.state.scene is not None and ctx.state.scene.scene_id != old:  # rule: 12.2.9
            # the record narrates the new scene first: only the people present in it act in it
            here = set(ctx.state.scene.cast_present)
            rec.npc_actions = [a for a in rec.npc_actions if a.npc in here]
    elif settled:
        mark_agenda_answered(tctx, "answered")


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


__all__ = ["NARRATION_PENDING", "AdjudicationResult", "BeatEntry", "answer_pause", "play_answer", "play_dispute",
           "play_turn", "recent_exchanges", "resume_narration", "run_turn"]

from engine.dm import session as _session  # noqa: E402,F401  (registers h.12.session_open/close, mode_change)
