"""Owner 15 handlers: social (engine/dm, engine/world). The Milestone 1 ones engine/world owns are registered by
engine/world/handlers.py (imported at the end); the rest log handler_skipped until registered here.

Register an implementation in this file with `@handler("<id>")` (see engine/time/handlers/__init__.py),
calling into the owning module; tag it `# rule: <rule id>`. The milestone that switches each one on is
in MILESTONE_HANDLERS.
"""

from __future__ import annotations

from typing import Any

from engine.time.handlers import HandlerResult, handler

HANDLERS = (
    "h.15.downtime_day",  # M7
    "h.15.downtime_week",  # M7
    "h.15.member_standing",  # M6
    "h.15.commitments_due",  # M1
    "h.15.alertness_decay",  # M2
    "h.15.placement_audit",  # M1 for reduced cases (DL-15-38); full cases M6
    "h.15.patience_reset",  # M1
    "h.15.standing_week",  # M6
)


@handler("h.15.placement_audit")
def placement_audit(ctx: Any) -> HandlerResult | None:  # rule: 15.9.4
    """At scene end: every unfound necessary node of a reduced case keeps two live placements (reserve, then
    PR-15-7)."""
    from engine.gen.case import audit_cases

    placed = audit_cases(ctx.tx, emit=ctx.emit)
    return HandlerResult(summary="; ".join(placed)) if placed else None


# Registers the engine/world handlers listed in engine.world.handlers.H15.
from engine.world import handlers as _world  # noqa: E402,F401
