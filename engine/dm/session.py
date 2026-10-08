"""Sessions (PR-12-8; 12.5.2–12.5.4) and the first opening (12.16.16), plus the ch.12 handlers the DM loop owns:
`h.12.session_open`, `h.12.session_close`, `h.12.mode_change` (registered on import; engine/dm/turn.py imports
this module).

    resp = open_session(ctx)          # Game.open: recap from state via the Narrator (checked), SITUATION, the open pause
    resp = opening(ctx)               # after creation: frame the first scene at the inciting incident (12.16.16)
    resp = close_session(ctx, next_time="more of the smugglers")   # session_end, the next-time question, where the PC stands

Each runs in one transaction under its own turn id, saved as a TurnRecord (input in parentheses), so its model
calls have unique ids and the exchange is in the turn log. No time passes at a session boundary (00.7.9).
"""

from __future__ import annotations

import re
from typing import Any

from engine.audit.safety import safety_prefs
from engine.dm import oof
from engine.dm.adjudication import AdjudicationRecord, SceneEntry
from engine.dm.context import TurnContext
from engine.dm.response import Flags, OofBlock, Pause, Response
from engine.store.events import Event
from engine.store.projection import WorldState
from engine.store.records import TurnRecord
from engine.time.handlers import HandlerResult, handler
from engine.time.scheduler import TimeContext, mark_boundary
from engine.world.common import active_pc, meta, stage

SESSION = "session"  # meta {n, opened_seq, prefs, closed_seq}
NEXT_TIME = "session.next_time"  # 12.5.4 (3): shown at the next session's start; never a fact
REVIEW = "session.review"  # 12.12.4: ruling ids flagged for review this session
RECAP_SEQ = "recap.last_seq"
OPENED_PC = "opening.pc"  # the character whose opening has been told (a later PC gets its own)
SLOTS_REMINDER = "creation.open_slots.reminder"  # engine/time/handlers/h02.py (02.9.8)


# ------------------------------------------------------------------------------------------- handlers


@handler("h.12.session_open")
def h_session_open(ctx: TimeContext) -> HandlerResult:  # rule: 12.5.2
    """12.5.2 step 1: the preference record is re-read and applies from now on; the session is counted."""
    st = ctx.tx.state
    prev = st.meta.get(SESSION) or {}
    n = int(prev.get("n") or 0) + 1
    prefs = [p.model_dump() for p in safety_prefs(st)]
    stage(ctx, meta(SESSION, {"n": n, "opened_seq": st.last_seq, "prefs": prefs, "closed_seq": None}, "12.5.2"))
    return HandlerResult(summary=f"session {n} opened; {len(prefs)} safety preferences in force")


@handler("h.12.session_close")
def h_session_close(ctx: TimeContext) -> HandlerResult:  # rule: 12.5.4
    # rule: 12.12.4
    """12.5.4 step 2: the review list (rulings flagged `review_flag` this session, 12.12.4) is compiled."""
    st = ctx.tx.state
    sess = dict(st.meta.get(SESSION) or {})
    since = int(sess.get("opened_seq") or 0)
    store = getattr(ctx.tx, "store", None)
    evs = list(store.events(since=since, types=["ruling_logged"])) if store is not None else []
    evs += [e for e in ctx.tx.events if e.type == "ruling_logged"]
    flagged = []
    for e in evs:
        r: Any = getattr(e.payload, "ruling", None) or {}
        if isinstance(r, dict) and r.get("review_flag") and r.get("id") not in flagged:
            flagged.append(r.get("id"))
    sess["closed_seq"] = st.last_seq
    stage(ctx, meta(REVIEW, flagged, "12.12.4"), meta(SESSION, sess, "12.5.4"))
    return HandlerResult(summary=f"session closed; {len(flagged)} rulings for review")


@handler("h.12.mode_change")
def h_mode_change(ctx: TimeContext) -> HandlerResult:  # rule: 12.4.5
    """Load the new mode: its situation tags (the cards later packets load) and its time per beat (00.7.3)."""
    from engine.retrieve.anchors import mode_tags
    from engine.time.clock import beat_cost, mode_of

    to = mode_of(str((ctx.payload or {}).get("to") or ctx.tx.state.time.mode))
    amount, unit = beat_cost(to)
    stage(ctx, meta("mode.loaded", {"mode": to, "tags": mode_tags(to, ctx.rules), "beat_cost": [amount, unit]},
                    "12.4.5"))
    return HandlerResult(summary=f"mode {to}: {amount} {unit} per beat")


# ------------------------------------------------------------------------------------------- state summary


def _name(state: WorldState, eid: str | None) -> str:
    e = state.entities.get(eid or "")
    if e is None or eid in state.seals or e.visibility not in ("shown", "available"):
        return ""
    return e.name


def recap_summary(state: WorldState, *, since_seq: int = 0) -> list[str]:  # rule: 12.5.3
    """The recap's sources from state only (never earlier prose): chronicle since the last recap, active threads,
    the PC's place, condition and pressing clocks as shown, the last scene's agenda and its answer."""
    from engine.dm.packet import WATCHES
    from engine.harm.state import descriptor
    from engine.world.chronicle import chronicle
    from engine.world.places import location
    from engine.world.social import thread_list

    pc = active_pc(state)
    lines = ["STATE SUMMARY (the recap's only source):"]
    if pc:
        where = _name(state, location(state, pc))
        watch = WATCHES[state.time.now.watch] if 0 <= state.time.now.watch < len(WATCHES) else ""
        lines.append(f"- {state.entities[pc].name} is " + (f"at {where}, " if where else "") + f"in the {watch}")
        try:
            lines.append(f"- {state.entities[pc].name} looks {descriptor(state, pc)}")
        except Exception:  # noqa: BLE001 - a PC without harm state yet
            pass
    for c in state.clocks.values():
        if c.status == "active" and c.visibility != "hidden":
            lines.append(f"- pressing: {c.name}")
    for t in thread_list(state):
        if t["status"] == "active" and _name(state, t["id"]):
            lines.append(f"- an open thread: {t['name']}")
    for e in chronicle(state, since_seq=since_seq)[-6:]:
        if e.scope in ("public", pc or ""):
            lines.append(f"- earlier: {e.text}")
    last = state.scene or state.last_scene
    if last is not None and last.agenda:
        lines.append(f"- the last scene asked: {last.agenda}" + (" (answered)" if last.question_answered else ""))
    return lines


# ------------------------------------------------------------------------------------------- open, opening, close


def _save(ctx: TurnContext, turn_id: str, label: str, resp: Response, narr: Any = None) -> None:
    tr = TurnRecord(turn_id=turn_id, input_verbatim=label, delivered_verbatim=resp.text(),
                    model_calls=list(ctx.call_ids))
    if narr is not None:
        tr = tr.model_copy(update={"draft_versions": narr.draft_versions, "verdicts": narr.verdicts,
                                   "fallback_used": narr.fallback_used, "screen": narr.screen})
    ctx.store.save_turn(tr)


def _pause_blocks(ctx: TurnContext) -> tuple[list[OofBlock], Pause | None]:
    from engine.dm.narration import pause_blocks, shown_pause

    p = ctx.store.state.open_pause()
    if p is None:
        return [], None
    blocks = pause_blocks(ctx, p)
    return blocks, shown_pause(p, blocks)


def needs_opening(state: WorldState) -> bool:  # rule: 12.16.16
    """The active character has not had its opening yet (the first character: no scene ever; a later one: the
    opening was told for someone else)."""
    pc = active_pc(state)
    if pc is None:
        return False
    if state.meta.get(OPENED_PC) is not None:
        return state.meta.get(OPENED_PC) != pc
    return not state.meta.get("game.opened") and state.scene is None and state.last_scene is None


def open_session(ctx: TurnContext) -> Response:  # rule: PR-12-8
    # rule: 12.5.2
    """PR-12-8 open: `mark_boundary(session_start)` → recap from state through the Narrator and the checker
    (12.5.3; fallback: the RECAP block alone) → SITUATION (the RECAP block) → a pending pause re-shown → the
    next-time note. With no scene yet and no opening given, this is the first opening (`opening`)."""
    from engine.dm.narration import narrate_checked

    st = ctx.store.state
    if needs_opening(st):
        return opening(ctx)
    store = ctx.store
    turn_id = store.new_turn_id()
    ctx.call_ids = []
    since = int(st.meta.get(RECAP_SEQ) or 0)
    reminder: Any = None
    with store.transaction(turn_id) as tx:
        ctx.tx = tx
        try:
            mark_boundary(ctx.time_ctx(), "session_start", {})
            rec = AdjudicationRecord(turn_id=turn_id, pc=active_pc(tx.state))
            narr = narrate_checked(ctx, rec, purpose="recap", extra=recap_summary(tx.state, since_seq=since),
                                   fallback_text="")
            tx.add(Event.of("meta_set", source="engine", rule_id="12.5.3", key=RECAP_SEQ, value=tx.state.last_seq))
            reminder = tx.state.meta.get(SLOTS_REMINDER)
            if reminder:  # h.02.open_slots queued it (02.9.8): shown once, at this session start
                tx.add(Event.of("meta_set", source="engine", rule_id="02.9.8", key=SLOTS_REMINDER, value=None))
        finally:
            ctx.tx = None
    st = store.state
    blocks = [oof.recap_block(st, since_seq=since)]
    if isinstance(reminder, dict) and reminder.get("slots"):
        slots = ", ".join(str(x).replace("_", " ") for x in reminder["slots"])
        blocks.append(oof.note_block(f"Still open from your character's creation: {slots}. Tell me whenever you "
                                     "like, or say so if you'd rather I stopped asking.", "SESSION"))
    note = st.meta.get(NEXT_TIME)
    if note:
        blocks.append(oof.note_block(f"Last time you wanted to focus on: {note}", "SESSION"))
    pblocks, pause = _pause_blocks(ctx)
    resp = Response(turn_id=turn_id, phase="play", fiction=narr.fiction, oof_blocks=oof.ordered([*blocks, *pblocks]),
                    pause=pause, flags=Flags(fallback_used=narr.fallback_used, review_flag=narr.review_flag))
    _save(ctx, turn_id, "(session open)", resp, narr)
    return resp


def opening(ctx: TurnContext) -> Response:  # rule: 12.16.16
    """The first opening: `session_start`, the first scene framed by the Director at the incident's place
    (`world.opening`), then the Narrator's opening through the checker (fallback: the record's plain sentences)."""
    from engine.dm.narration import narrate_checked
    from engine.dm.roles.director import direct, frame_scene, scene_header

    store = ctx.store
    turn_id = store.new_turn_id()
    ctx.call_ids = []
    op = dict(store.state.meta.get("world.opening") or {})
    inciting = str((op.get("inciting") or {}).get("text") or "")
    with store.transaction(turn_id) as tx:
        ctx.tx = tx
        try:
            mark_boundary(ctx.time_ctx(), "session_start", {})
            rec = AdjudicationRecord(turn_id=turn_id, pc=active_pc(tx.state))
            later = tx.state.meta.get(OPENED_PC) not in (None, rec.pc)  # a new character in the same world
            if not later and inciting:  # the incident's person is someone who exists (I-145, P-067)
                from engine.dm.incident import bind_incident, incident_line

                bind_incident(ctx, tx)
                who = incident_line(tx.state)
                inciting = f"{inciting}. {who.rstrip('.')}" if who else inciting
            if later and tx.state.scene is not None:
                from engine.world.scenes import end_scene

                end_scene(ctx.time_ctx(), "new_character")  # the last character's scene closes first
            if tx.state.scene is None:
                d = direct(ctx, situation=("a new character enters the story (12.16.16): frame their first scene"
                                           if later else "the first opening (12.16.16): frame the inciting "
                                           "incident in the haven") + (f": {inciting}" if inciting else ""))
                start = frame_scene(ctx, d, reason="opening")
                rec.scene = SceneEntry(started=start.scene_id, header=scene_header(ctx.state))
            if inciting:
                rec.notes.append(f"the inciting incident: {inciting}")
            for lead in op.get("leads") or []:
                text = (lead.get("text") or lead.get("lead")) if isinstance(lead, dict) else lead
                if text and not str(text).startswith("the incident itself"):  # the incident is noted above
                    rec.notes.append(f"a lead to make noticeable: {text}")
            narr = narrate_checked(ctx, rec, purpose="opening")
            tx.add(Event.of("meta_set", source="engine", rule_id="12.16.16", key="game.opened", value=turn_id))
            tx.add(Event.of("meta_set", source="engine", rule_id="12.16.16", key=OPENED_PC, value=rec.pc))
        finally:
            ctx.tx = None
    pblocks, pause = _pause_blocks(ctx)
    resp = Response(turn_id=turn_id, phase="play", fiction=narr.fiction, oof_blocks=oof.ordered(pblocks), pause=pause,
                    flags=Flags(fallback_used=narr.fallback_used, review_flag=narr.review_flag))
    _save(ctx, turn_id, "(opening)", resp, narr)
    return resp


def where_line(state: WorldState) -> str:  # rule: 12.5.4
    """12.5.4 step 4: one line naming where the PC stands."""
    from engine.dm.packet import WATCHES
    from engine.world.places import location

    pc = active_pc(state)
    if pc is None:
        return "No character in play."
    where = _name(state, location(state, pc))
    watch = WATCHES[state.time.now.watch] if 0 <= state.time.now.watch < len(WATCHES) else ""
    open_pause = state.open_pause()
    # the open choice by what it is about, in words (its prompt can carry the frame's mechanics: those are in the
    # OFFER block that is shown again on return)
    about = re.split(r"[:;(]", open_pause.prompt)[0].strip().rstrip(".") if open_pause and open_pause.prompt else ""
    tail = f"; your choice is still open: {about}" if about else ""
    return f"{state.entities[pc].name}: " + (f"at {where}, " if where else "") + f"{watch}{tail}."


def close_session(ctx: TurnContext, next_time: str | None = None) -> Response:  # rule: PR-12-8
    # rule: 12.5.4
    """PR-12-8 close: an open OFFER (or any pause) stays open and is re-shown next session; `session_end` runs
    `h.12.session_close`; the next-time question (its answer, when given, is stored as a note, never a fact);
    one line of where the PC stands. No time passes."""
    store = ctx.store
    turn_id = store.new_turn_id()
    ctx.call_ids = []
    with store.transaction(turn_id) as tx:
        ctx.tx = tx
        try:
            mark_boundary(ctx.time_ctx(), "session_end", {})
            if next_time:
                tx.add(Event.of("meta_set", source="player", rule_id="12.5.4", key=NEXT_TIME, value=next_time))
        finally:
            ctx.tx = None
    st = store.state
    blocks = [oof.note_block("Anything you want to focus on next time?", "SESSION"), oof.note_block(where_line(st))]
    pause = st.open_pause()
    resp = Response(turn_id=turn_id, phase="play", oof_blocks=oof.ordered(blocks),
                    pause=Pause.of(pause) if pause is not None else None)
    _save(ctx, turn_id, "(session close)", resp)
    return resp


__all__ = ["OPENED_PC", "close_session", "h_mode_change", "h_session_close", "h_session_open", "needs_opening",
           "open_session", "opening", "recap_summary", "where_line"]
