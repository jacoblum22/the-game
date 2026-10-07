"""Owner 00 handlers: durations, automatic clock ticks, reflection (T-00-9).

Built here: h.00.durations (conditions; effect instances arrive with M2), h.00.clock_auto, h.00.reflection.
Not yet built: h.00.reflection_if_downtime (M7, downtime).
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from engine.store.clocks import tick_clock
from engine.store.conditions import remove_condition
from engine.time import clock
from engine.time.handlers import HandlerResult, handler

if TYPE_CHECKING:
    from engine.time.scheduler import TimeContext

HANDLERS = ("h.00.durations", "h.00.clock_auto", "h.00.reflection", "h.00.reflection_if_downtime")

_NUMERIC = re.compile(r"^(rounds|intervals|hours|watches|days):(\d+)$")
_RESTS = ("breather", "rest_short", "rest_long")  # a longer rest also ends an until_rest of a shorter one


def expired(remaining: str, applied_at_rounds: int | None, now_rounds: int, boundary: str) -> bool:
    """Does a `remaining` duration form (substrate.yaml#duration_forms) end at this boundary instant?
    Numeric forms end at the first boundary at or after their length has elapsed (checked at every boundary,
    so a `rounds:N` condition still ends when time is skipped by the interval); `scene`, `conflict` and
    `until_rest:<type>` end at their boundary; `uses:N`, `while:`, `until_cleansed` and `permanent` are
    not ended by time."""  # rule: 06.7.3
    m = _NUMERIC.match(remaining)
    if m:
        if applied_at_rounds is None:
            return False
        return now_rounds - applied_at_rounds >= int(m.group(2)) * clock.ROUNDS[clock.unit_of(m.group(1))]
    if remaining == "scene":
        return boundary == "scene_end"
    if remaining == "conflict":
        return boundary == "conflict_end"
    if remaining.startswith("until_rest:") and boundary in _RESTS:
        need = remaining.split(":", 1)[1]
        return need in _RESTS and _RESTS.index(boundary) >= _RESTS.index(need)
    return False


@handler("h.00.durations")
def durations(ctx: TimeContext) -> HandlerResult:
    """Phase 1 expire: end condition instances whose duration has run out (00.7.5, 05.4.5)."""  # rule: 00.7.5
    now = clock.to_rounds(ctx.now)
    gone: list[str] = []
    out = HandlerResult()
    for iid in sorted(ctx.state.conditions):
        inst = ctx.state.conditions[iid]
        at = clock.to_rounds(inst.applied_at) if inst.applied_at else None
        if not expired(inst.remaining, at, now, ctx.boundary):
            continue
        res = remove_condition(ctx.state, ctx.rules, iid, f"duration {inst.remaining} ended at {ctx.boundary}",
                               rule_id="06.7.3")
        ctx.emit(*res.events)
        gone.append(iid)
        out.effects += res.on_remove
        if ctx.rules.condition(inst.condition_id).get("visible"):  # rule: PR-00-5
            out.narration.append(f"{inst.condition_id} ends on {inst.target}")
    out.summary = f"expired {', '.join(gone)}" if gone else ""
    return out


@handler("h.00.clock_auto")
def clock_auto(ctx: TimeContext) -> HandlerResult:
    """Phase 5 clocks: every active clock's auto_ticks and decay rows for this boundary (PR-00-2 step 2)."""
    # rule: PR-00-3
    out = HandlerResult()
    ticked: list[str] = []
    for cid in sorted(ctx.state.clocks):
        for row in ("auto", "decay"):
            c = ctx.state.clocks[cid]
            listed = c.auto_ticks if row == "auto" else c.decay
            if c.status != "active" or not any(str(r.get("boundary")) == ctx.boundary for r in listed):
                continue
            res = tick_clock(ctx.state, cid, ctx.boundary, row=row, units=ctx.rules.severity_units(),  # type: ignore[arg-type]
                             source_ref=f"h.00.clock_auto@{ctx.boundary}")
            ctx.emit(*res.events)
            if res.events:
                ticked.append(f"{cid} {res.amount:+d}")
            for r in [res, *res.linked]:
                if r.omen:
                    out.narration.append(r.omen)
                if r.lethal_warning:
                    out.narration.append(f"lethal_warning:{r.clock_id}")
                out.effects += r.completion_effects
                if r.interrupt and out.interrupt is None:
                    out.interrupt = f"{r.clock_id} completed"
    out.summary = "; ".join(ticked)
    return out


@handler("h.00.reflection")
def reflection(ctx: TimeContext) -> HandlerResult:
    """On rest_long and season: fire the reflection event boundary, at most once per day (00.7.2)."""
    # rule: 00.7.2
    last = ctx.state.time.last_boundary.get("reflection")
    if last is not None:
        ev = next((e for e in ctx.tx.events if e.seq == last), None) or ctx.tx.store.event(last)
        if ev is not None and ev.game_time is not None and clock.day_index(ev.game_time) == clock.day_index(ctx.now):
            return HandlerResult(summary="reflection already fired today")
    return HandlerResult(summary="reflection", chain=[("reflection", {"cause": ctx.boundary})])
