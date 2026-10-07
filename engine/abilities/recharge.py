"""Uses and recharge (05.4.6), Focus recovery by rest (05.6.9; PR-05-4), and ch.05's Milestone 1 boundary
handlers: h.05.scene_recharge, h.05.day_recharge, h.05.focus_recover, h.05.rest_recharge.

Handlers take a context with `state`, `mint`, `rules`, `boundary` and `payload` and return events (see
engine/harm/rest.py; the rest payload is `{quality, site, treated}`, optionally `resters` and `resonant`).
Counters (meta, `<pc>.<name>`): breathers_since_short_rest, short_rests_today, generated_this_scene,
overdraws_since_long_rest, healings_since_long_rest, restored_by_consumables_since_long_rest.
"""

from __future__ import annotations

import math
from typing import Any

from engine.abilities.focus import FOCUS, restore_focus
from engine.abilities.use import uses_key
from engine.harm.ctx import Writes, counter_key
from engine.harm.rest import resters
from engine.harm.state import DEAD, harm_state, pcs
from engine.store.events import Event
from engine.store.projection import WorldState

LADDER = ("round", "conflict_end", "scene_end", "rest_short", "rest_long")  # abilities.yaml#refresh_ladder


def refreshed_by(boundary: str) -> set[str]:  # rule: 05.4.6
    """The `per` values a boundary refreshes: everything at or below it on the ladder; `day` only at dawn."""
    if boundary == "day":
        return {"day"}
    if boundary in LADDER:
        return set(LADDER[: LADDER.index(boundary) + 1])
    return set()


def refresh_uses(ctx: Any, w: Writes, eid: str, boundary: str) -> int:  # rule: 05.4.6
    """Refill every defined `uses.<id>` whose ability's `per` the boundary refreshes. Returns how many."""
    pers = refreshed_by(boundary)
    n = 0
    for name, q in list(ctx.state.quantities.get(eid, {}).items()):
        if not name.startswith("uses.") or q.max is None or q.current >= q.max:
            continue
        ab_id = name.removeprefix("uses.")
        per = (ctx.rules.ability(ab_id).get("limits") or {}).get("per") if ctx.rules.has(ab_id) else None
        if per in pers:
            w.set_quantity(eid, uses_key(ab_id), q.max, reason=f"{boundary} refresh", rule_id="05.4.6")
            n += 1
    return n


def _reset(w: Writes, eid: str, name: str, rule_id: str) -> None:
    key = counter_key(eid, name)
    if w.meta_value(key, 0):
        w.meta(key, 0, rule_id=rule_id)


def _bump(w: Writes, eid: str, name: str, rule_id: str) -> None:
    key = counter_key(eid, name)
    w.meta(key, int(w.meta_value(key, 0) or 0) + 1, rule_id=rule_id)


def _characters(state: WorldState) -> list[str]:
    return [p for p in pcs(state) if harm_state(state, p) != DEAD]


def h_05_scene_recharge(ctx: Any) -> list[Event]:  # rule: 05.4.6
    # coarse: 05.6.10 — only the per-scene generation counter; the family triggers come with callings (M3).
    """`h.05.scene_recharge` (scene_end, phase 3): refresh per round/conflict/scene uses; reset
    generated_this_scene (05.6.10). Scene-duration ability effects are effect instances (M2)."""
    w = Writes.of(ctx, source="h.05.scene_recharge")
    for eid in _characters(ctx.state):
        refresh_uses(ctx, w, eid, "scene_end")
        _reset(w, eid, "generated_this_scene", "05.6.10")
    return w.events


def h_05_day_recharge(ctx: Any) -> list[Event]:  # rule: 05.6.9
    """`h.05.day_recharge` (day, phase 3): refresh per-day uses; reset short_rests_today."""
    w = Writes.of(ctx, source="h.05.day_recharge")
    for eid in _characters(ctx.state):
        refresh_uses(ctx, w, eid, "day")
        _reset(w, eid, "short_rests_today", "05.6.9")
    return w.events


def focus_gain(kind: str, quality: str, current: int, maximum: int, *, breathers_since_short: int,
               short_rests_today: int, resonant: bool = False) -> int:  # rule: 05.6.9
    """Focus after a rest (05.6.9's table), as the new value before the clamp to the maximum."""
    def as_breather() -> int:
        return 0 if quality == "interrupted" or breathers_since_short >= 2 else 1

    if kind == "breather":
        add = as_breather()
    elif kind == "rest_short":
        if short_rests_today >= 2:
            add = 0 if quality == "interrupted" else 1
        else:
            add = {"full": math.ceil(maximum / 2), "partial": math.ceil(maximum / 4), "interrupted": 1}[quality]
    else:
        if quality == "full":
            return maximum
        if quality == "partial":
            return max(current, math.ceil(3 * maximum / 4))
        add = math.ceil(maximum / 4)  # interrupted: as a partial short rest
    if resonant and kind in ("breather", "rest_short") and quality != "interrupted":
        add += 1  # a resonant place (05.6.9)
    return current + add


def h_05_focus_recover(ctx: Any) -> list[Event]:  # rule: PR-05-4
    """`h.05.focus_recover` (breather, rest_short, rest_long; phase 3, after h.07.rest_recovery): PR-05-4 step 2,
    then count the rest toward the breather and short-rest limits."""
    kind = str(getattr(ctx, "boundary", "") or "")
    p = ctx.payload if isinstance(getattr(ctx, "payload", None), dict) else {}
    quality = str(p.get("quality", "full"))
    w = Writes.of(ctx, source="h.05.focus_recover")
    for eid in resters(ctx):
        q = ctx.state.quantities.get(eid, {}).get(FOCUS)
        if q is None or harm_state(ctx.state, eid) == DEAD:
            continue
        new = focus_gain(kind, quality, q.current, q.max if q.max is not None else q.current,
                         breathers_since_short=int(ctx.state.meta.get(counter_key(eid, "breathers_since_short_rest"),
                                                                      0) or 0),
                         short_rests_today=int(ctx.state.meta.get(counter_key(eid, "short_rests_today"), 0) or 0),
                         resonant=bool(p.get("resonant")))
        restore_focus(ctx, eid, to=new, reason=f"{kind} ({quality})", rule_id="05.6.9", writes=w)
        if quality != "interrupted" and kind == "breather":
            _bump(w, eid, "breathers_since_short_rest", "05.6.9")
        elif quality != "interrupted" and kind == "rest_short":
            _bump(w, eid, "short_rests_today", "05.6.9")
    return w.events


def h_05_rest_recharge(ctx: Any) -> list[Event]:  # rule: PR-05-4
    """`h.05.rest_recharge` (rest_short, rest_long; phase 3): PR-05-4 steps 3-4. An interrupted rest refreshes
    nothing; rest_short resets breathers_since_short_rest; rest_long resets the long-rest counters."""
    kind = str(getattr(ctx, "boundary", "") or "")
    p = ctx.payload if isinstance(getattr(ctx, "payload", None), dict) else {}
    w = Writes.of(ctx, source="h.05.rest_recharge")
    for eid in resters(ctx):
        if harm_state(ctx.state, eid) == DEAD:
            continue
        if p.get("quality") != "interrupted":
            refresh_uses(ctx, w, eid, kind)
        if kind == "rest_short":
            _reset(w, eid, "breathers_since_short_rest", "05.6.9")
        elif kind == "rest_long":
            for c in ("healings_since_long_rest", "overdraws_since_long_rest",
                      "restored_by_consumables_since_long_rest"):
                _reset(w, eid, c, "05.6.6")
    return w.events
