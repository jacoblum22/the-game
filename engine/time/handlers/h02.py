"""Owner 02 handlers: character creation (engine/dm/creation).

Built: `h.02.creation_lock` (02.2.6) and `h.02.open_slots` (02.9.8), both at `reflection`.
Not built: `h.02.bent_offer` (02.6.5: drawing and presenting the Bent needs an offer pause flow of its own); it logs
`handler_skipped` until registered here.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from engine.time.handlers import HandlerResult, handler

if TYPE_CHECKING:
    from engine.time.scheduler import TimeContext

HANDLERS = (
    "h.02.creation_lock",  # M1
    "h.02.bent_offer",  # M1 (not built: logs handler_skipped)
    "h.02.open_slots",  # M1
)

REMINDER = "creation.open_slots.reminder"  # queued for the next session start (engine/dm/session.py shows it)
REMINDED = "creation.open_slots.session"  # the session a reminder was last queued in
STOP = "pref.open_slots.stop"  # the player said to stop asking


def _pcs(ctx: TimeContext) -> list[str]:
    return [eid for eid, e in ctx.tx.state.entities.items() if e.kind == "pc"]


@handler("h.02.creation_lock")
def h_creation_lock(ctx: TimeContext) -> HandlerResult | None:  # rule: 02.2.6
    """At the first reflection after creation the creation window closes: the choices become permanent and the
    fact `creation.locked` is written on the PC; a no-op afterwards."""
    from engine.world.common import fact, meta, stage

    locked = []
    for pc in _pcs(ctx):
        st = ctx.tx.state
        rec = st.meta.get(f"{pc}.creation")
        if not isinstance(rec, dict) or rec.get("window") != "open":
            continue
        new = {**rec, "window": "locked"}
        evs = [meta(f"{pc}.creation", new, "02.2.6"),
               fact(ctx.tx, pc, "creation.locked", True, rule_id="02.2.6", visibility="shown")]
        cur = st.meta.get("pc.creation")
        if isinstance(cur, dict) and cur.get("pc") == pc:
            evs.append(meta("pc.creation", {**cur, "window": "locked"}, "02.2.6"))
        stage(ctx, *evs)
        locked.append(pc)
    return HandlerResult(summary=f"creation window closed for {', '.join(locked)}") if locked else None


@handler("h.02.open_slots")
def h_open_slots(ctx: TimeContext) -> HandlerResult | None:  # rule: 02.9.8
    """Queue ONE out-of-fiction reminder of the still-open creation slots for the next session start; never more
    than one per session, never after the player said to stop asking."""
    from engine.world.common import active_pc, meta, stage

    st = ctx.tx.state
    pc = active_pc(st)
    if pc is None or st.meta.get(STOP):
        return None
    rec = st.meta.get(f"{pc}.creation")
    slots = [s for s in (rec or {}).get("open_slots") or [] if not st.fact_value(pc, s)] \
        if isinstance(rec, dict) else []
    session = int((st.meta.get("session") or {}).get("n") or 0)
    if not slots or st.meta.get(REMINDED) == session or st.meta.get(REMINDER):
        return None
    stage(ctx, meta(REMINDER, {"pc": pc, "slots": slots}, "02.9.8"), meta(REMINDED, session, "02.9.8"))
    return HandlerResult(summary=f"open creation slots reminder queued: {', '.join(slots)}")
