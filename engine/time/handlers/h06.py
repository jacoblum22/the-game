"""Owner 06 handlers: conflict (M2). None built yet; each logs handler_skipped until registered here.

Register an implementation in this file with `@handler("<id>")` (see engine/time/handlers/__init__.py),
calling into the owning module; tag it `# rule: <rule id>`. The milestone that switches each one on is
in MILESTONE_HANDLERS.
"""

from __future__ import annotations

HANDLERS = (
    "h.06.turn_effects",  # M2
    "h.06.ongoing_harm",  # M2
    "h.06.diminishing_window",  # M2
    "h.06.tempo_setup",  # M2
    "h.06.clear_conflict_state",  # M2
    "h.06.chase_round",  # M2
    "h.06.objective_check",  # M2
)
