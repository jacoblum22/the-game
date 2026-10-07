"""Registers the ch.12 and ch.15 Milestone 1 boundary handlers that engine/world owns.

Imported by `engine/time/handlers/h12.py` and `h15.py`, so the scheduler finds them. The bodies live in the
world modules and are imported when a handler runs (the world modules import the scheduler, which imports the
registry, which imports this module).
"""

from __future__ import annotations

from engine.time.handlers import HandlerResult, handler


@handler("h.12.scene_test")
def _scene_test(ctx: object) -> HandlerResult:  # rule: 12.4.4
    from engine.world.scenes import run_scene_test
    return run_scene_test(ctx)  # type: ignore[arg-type]


@handler("h.12.pacing_push")
def _pacing_push(ctx: object) -> HandlerResult:  # rule: 12.7.4
    from engine.world.pacing import pacing_push
    return pacing_push(ctx)  # type: ignore[arg-type]


@handler("h.12.tension_update")
def _tension_update(ctx: object) -> HandlerResult:  # rule: 12.6.3
    from engine.world.pacing import tension_update
    return tension_update(ctx)  # type: ignore[arg-type]


@handler("h.12.inconclusive_streak")
def _inconclusive_streak(ctx: object) -> HandlerResult:  # rule: 12.8.1
    from engine.world.pacing import inconclusive_streak
    return inconclusive_streak(ctx)  # type: ignore[arg-type]


@handler("h.12.lead_audit")
def _lead_audit(ctx: object) -> HandlerResult:  # rule: 12.8.4
    from engine.world.pacing import lead_audit
    return lead_audit(ctx)  # type: ignore[arg-type]


@handler("h.12.rotation_update")
def _rotation_update(ctx: object) -> HandlerResult:  # rule: 12.9.1
    from engine.world.pacing import rotation_update
    return rotation_update(ctx)  # type: ignore[arg-type]


@handler("h.12.npc_memory")
def _npc_memory(ctx: object) -> HandlerResult:  # rule: 12.11.7
    from engine.world.social import commit_memories
    return commit_memories(ctx)  # type: ignore[arg-type]


@handler("h.12.bookkeeping")
def _bookkeeping(ctx: object) -> HandlerResult:  # rule: 12.4.8
    """12.4.8's steps this handler owns: step 3 (the cast and thread lists) and step 8 (the chronicle line offered
    when the scene answered a thread's agenda). Steps 1, 2, 5, 6 and 7 are their own handlers; step 4 (the
    claim sweep) is the DM layer's."""
    from engine.time.scheduler import TimeContext
    from engine.world.chronicle import scene_offer
    from engine.world.common import meta, stage
    from engine.world.social import update_lists
    assert isinstance(ctx, TimeContext)
    lists = update_lists(ctx, ctx.rules)
    offer = scene_offer(ctx.tx.state)
    if offer:
        stage(ctx, meta("chronicle_offer", offer, "12.4.8"))
    return HandlerResult(summary=f"{lists}; chronicle offer {'yes' if offer else 'no'}")


@handler("h.15.patience_reset")
def _patience_reset(ctx: object) -> HandlerResult:  # rule: 15.2.6
    from engine.world.social import patience_reset
    return patience_reset(ctx)  # type: ignore[arg-type]


@handler("h.15.commitments_due")
def _commitments_due(ctx: object) -> HandlerResult:  # rule: 15.7.6
    from engine.world.social import commitments_due
    return commitments_due(ctx)  # type: ignore[arg-type]



# The handler ids this module registers (engine/time/handlers/h12.py and h15.py list them).
H12 = ("h.12.scene_test", "h.12.pacing_push", "h.12.tension_update", "h.12.inconclusive_streak", "h.12.lead_audit",
       "h.12.rotation_update", "h.12.npc_memory", "h.12.bookkeeping")
H15 = ("h.15.patience_reset", "h.15.commitments_due")
