"""Owner 12 handlers: pacing and the DM loop (engine/dm). The Milestone 1 ones engine/world owns are registered by
engine/world/handlers.py (imported at the end); the rest log handler_skipped until registered here.

Register an implementation in this file with `@handler("<id>")` (see engine/time/handlers/__init__.py),
calling into the owning module; tag it `# rule: <rule id>`. The milestone that switches each one on is
in MILESTONE_HANDLERS.
"""

from __future__ import annotations

HANDLERS = (
    "h.12.inconclusive_streak",  # M1
    "h.12.intensity",  # M2
    "h.12.scene_test",  # M1
    "h.12.tension_update",  # M1
    "h.12.bookkeeping",  # M1
    "h.12.venture_bookkeeping",  # M4
    "h.12.session_open",  # M1
    "h.12.session_close",  # M1
    "h.12.mode_change",  # M1
    "h.12.pacing_push",  # M1
    "h.12.lead_audit",  # M1
    "h.12.intensity_scene",  # M2
    "h.12.rotation_update",  # M1
    "h.12.npc_memory",  # M1
)

# Registers the engine/world handlers listed in engine.world.handlers.H12.
from engine.world import handlers as _world  # noqa: E402,F401
