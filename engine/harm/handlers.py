"""Registers ch.07's Milestone 1 boundary handlers with the time registry (engine/time/handlers).

Importing this module registers them (once; an id another module already registered is left alone). The owner
module `engine/time/handlers/h07.py` imports it so the scheduler finds them. Each adapter builds the harm
context from the scheduler's `TimeContext`, runs the handler and stages its events with `ctx.emit`.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from engine.harm.ctx import HarmCtx
from engine.harm.rest import h_07_lethal_scan, h_07_load_clear, h_07_natural_recovery, h_07_rest_recovery
from engine.harm.threshold import h_07_career_end
from engine.store.events import Event
from engine.time.handlers import HandlerResult, get, register

HandlerBody = Callable[[Any], list[Event]]


def adapt(handler_id: str, body: HandlerBody) -> Callable[[Any], HandlerResult]:
    """Wrap a `ctx -> events` handler for the scheduler: `TimeContext` has `tx` (for `mint`), not `mint`."""
    def run(tctx: Any) -> HandlerResult:
        ctx = HarmCtx(state=tctx.state, mint=tctx.tx.mint, rules=tctx.rules, rng=tctx.rng,
                      boundary=tctx.boundary, payload=dict(tctx.payload or {}))
        events = body(ctx)
        if events:
            tctx.emit(*events)
        return HandlerResult(summary=f"{handler_id}: {len(events)} event(s)")
    run.__name__ = handler_id.replace(".", "_")
    return run


H07: dict[str, HandlerBody] = {
    "h.07.rest_recovery": h_07_rest_recovery,  # rule: PR-07-8
    "h.07.natural_recovery": h_07_natural_recovery,  # rule: PR-07-10
    "h.07.load_clear": h_07_load_clear,  # rule: 07.2.6
    "h.07.lethal_scan": h_07_lethal_scan,  # rule: PR-07-4
    "h.07.career_end": h_07_career_end,  # rule: 07.11.6
}


def register_all(table: dict[str, HandlerBody]) -> list[str]:
    done = []
    for hid, body in table.items():
        if get(hid) is None:
            register(hid, adapt(hid, body))
            done.append(hid)
    return done


REGISTERED = register_all(H07)
