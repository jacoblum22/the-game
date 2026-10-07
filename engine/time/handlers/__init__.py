"""The boundary-handler registry (00.7.4, T016, FR-026).

Every handler id in `rules/data/boundaries.yaml` belongs to exactly one milestone (MILESTONE_HANDLERS). The
scheduler runs a handler when it is live for the game's milestone AND a function is registered for it;
otherwise it logs `handler_skipped` ("not yet built", with the milestone that builds it). Handlers live in
the owner's module `hNN.py` here and may call into their domain module:

    @handler("h.07.rest_recovery")
    def rest_recovery(ctx: TimeContext) -> HandlerResult:   # (tag it with its rule id)
        res = engine.harm.rest.recover(ctx.state, ctx.rules, ctx.payload)
        ctx.emit(*res.events)                               # stamps the boundary instant and the handler id
        return HandlerResult(summary="vitality +3")

A handler never mutates state directly: it stages events with `ctx.emit` and returns a HandlerResult (or
None). Only a handler whose registry row has `interrupting` other than false may return an interrupt.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from engine.time.scheduler import TimeContext


@dataclass
class HandlerResult:
    summary: str = ""  # one line for the handler_ran event
    interrupt: str | None = None  # why advance_time must halt at this instant (00.7.8)
    narration: list[str] = field(default_factory=list)  # omens, rumors, traces to narrate (PR-00-2 step 5)
    chain: list[tuple[str, dict[str, Any]]] = field(default_factory=list)  # event boundaries fired at this instant
    effects: list[Mapping[str, Any]] = field(default_factory=list)  # completion / on_remove effects for the caller


HandlerFn = Callable[["TimeContext"], "HandlerResult | None"]

_REGISTRY: dict[str, HandlerFn] = {}


def handler(handler_id: str) -> Callable[[HandlerFn], HandlerFn]:
    """Register the decorated function as the implementation of `handler_id`."""
    def deco(fn: HandlerFn) -> HandlerFn:
        register(handler_id, fn)
        return fn
    return deco


def register(handler_id: str, fn: HandlerFn, *, replace: bool = False) -> None:
    if handler_id not in MILESTONE_OF:
        raise KeyError(f"{handler_id} is not a handler in boundaries.yaml / MILESTONE_HANDLERS")
    if handler_id in _REGISTRY and not replace:
        raise ValueError(f"{handler_id} is already registered")
    _REGISTRY[handler_id] = fn


def unregister(handler_id: str) -> None:
    """Tests only."""
    _REGISTRY.pop(handler_id, None)


def get(handler_id: str) -> HandlerFn | None:
    return _REGISTRY.get(handler_id)


def implemented() -> frozenset[str]:
    return frozenset(_REGISTRY)


# Which milestone switches each handler on: plan.md "## Milestones", column "Boundary handlers switched on",
# resolved against boundaries.yaml. Deviation: h.12.intensity_scene is M2, as tasks.md T068 says ("waits for
# M2"), although plan.md's M1 row reads "12 all but intensity and venture_bookkeeping".
MILESTONE_HANDLERS: dict[int, tuple[str, ...]] = {
    1: (  # Start to finish (34)
        "h.00.durations", "h.00.clock_auto", "h.00.reflection",
        "h.01.ruling_log", "h.01.scene_cleanup",
        "h.02.creation_lock", "h.02.bent_offer", "h.02.open_slots",
        "h.05.scene_recharge", "h.05.day_recharge", "h.05.focus_recover", "h.05.rest_recharge",
        "h.07.natural_recovery", "h.07.rest_recovery", "h.07.lethal_scan", "h.07.load_clear", "h.07.career_end",
        "h.08.durations",
        "h.10.site_time", "h.10.scene_frame",
        "h.11.fallback_counters",
        "h.12.inconclusive_streak", "h.12.scene_test", "h.12.tension_update", "h.12.bookkeeping",
        "h.12.session_open", "h.12.session_close", "h.12.mode_change", "h.12.pacing_push", "h.12.lead_audit",
        "h.12.rotation_update", "h.12.npc_memory",
        "h.15.patience_reset", "h.15.commitments_due",
    ),
    2: (  # Fights
        "h.05.round_recharge", "h.05.conflict_recharge",
        "h.06.turn_effects", "h.06.ongoing_harm", "h.06.diminishing_window", "h.06.tempo_setup",
        "h.06.clear_conflict_state", "h.06.chase_round", "h.06.objective_check",
        "h.07.after_conflict", "h.07.dying_check", "h.07.affliction_onset", "h.07.affliction_day",
        "h.07.fatigue", "h.07.curse_cycle",
        "h.12.intensity", "h.12.intensity_scene",
        "h.15.alertness_decay",
        "h.16.held_line",
    ),
    3: (  # Growth
        "h.03.antigrind_reset", "h.03.recency_update", "h.03.day_settle",
        "h.04.recognition_pass", "h.04.standing_offers", "h.04.season_consolidation", "h.04.crisis_check",
        "h.04.provisional_check", "h.04.fraying_check",
        "h.05.reslot", "h.05.reserve", "h.05.provisional_abilities",
        "h.07.vitality_max",
    ),
    4: (  # The road
        "h.10.light", "h.10.site_check", "h.10.travel_progress", "h.10.watch_check", "h.10.supply",
        "h.10.weather", "h.10.weather_regime", "h.10.venture", "h.10.site_exposure", "h.10.watch_exposure",
        "h.10.wayfinding", "h.10.site_recovery", "h.10.day_reset", "h.10.site_regrowth",
        "h.12.venture_bookkeeping",
    ),
    5: (  # Things
        "h.08.upkeep", "h.08.markets", "h.08.craft_decay",
    ),
    6: (  # The living world
        "h.11.situation_timelines", "h.11.world_turn", "h.11.season_turn", "h.11.year_turn", "h.11.reckoning",
        "h.11.world_record", "h.11.moon", "h.11.festival",
        "h.15.standing_week", "h.15.member_standing", "h.15.placement_audit",
    ),
    7: (  # Company, downtime, legacy
        "h.16.retinue_upkeep", "h.16.contract_term", "h.16.conflict_orders", "h.16.follower_offers",
        "h.16.season_growth", "h.16.venture_end", "h.16.loyalty_record",
        "h.15.downtime_day", "h.15.downtime_week",
        "h.00.reflection_if_downtime",
    ),
}
MILESTONE_OF: dict[str, int] = {h: m for m, hs in MILESTONE_HANDLERS.items() for h in hs}


def milestone_of(handler_id: str) -> int:
    """The milestone that builds `handler_id`."""
    return MILESTONE_OF[handler_id]


def live_handlers(milestone: int) -> frozenset[str]:
    """Handler ids switched on at `milestone` (all earlier milestones' too)."""
    return frozenset(h for h, m in MILESTONE_OF.items() if m <= milestone)


def runnable(handler_id: str, milestone: int) -> HandlerFn | None:
    """The function to run, or None when the handler must be logged as skipped (FR-026)."""
    if MILESTONE_OF.get(handler_id, 99) > milestone:
        return None
    return _REGISTRY.get(handler_id)


def check_registry(rules: Any) -> list[str]:
    """Problems between boundaries.yaml, MILESTONE_HANDLERS and the registered functions (empty = consistent)."""
    yaml_ids = [str(h["id"]) for h in rules.boundary_handlers()]
    listed = [h for hs in MILESTONE_HANDLERS.values() for h in hs]
    out = [f"{h}: listed in more than one milestone" for h in sorted({h for h in listed if listed.count(h) > 1})]
    out += [f"{h}: in boundaries.yaml but in no milestone" for h in sorted(set(yaml_ids) - set(listed))]
    out += [f"{h}: in MILESTONE_HANDLERS but not in boundaries.yaml" for h in sorted(set(listed) - set(yaml_ids))]
    return out


# The owner modules register their handlers on import (kept last: they import `handler` from here).
from engine.time.handlers import (  # noqa: E402
    h00,
    h01,
    h02,
    h03,
    h04,
    h05,
    h06,
    h07,
    h08,
    h10,
    h11,
    h12,
    h15,
    h16,
)

__all__ = ["HandlerResult", "HandlerFn", "handler", "register", "unregister", "get", "implemented",
           "MILESTONE_HANDLERS", "MILESTONE_OF", "milestone_of", "live_handlers", "runnable", "check_registry",
           "h00", "h01", "h02", "h03", "h04", "h05", "h06", "h07", "h08", "h10", "h11", "h12", "h15", "h16"]
