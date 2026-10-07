"""Owner 07 handlers: harm and rests (engine/harm). None built yet; each logs handler_skipped until registered here.

Register an implementation in this file with `@handler("<id>")` (see engine/time/handlers/__init__.py),
calling into the owning module; tag it `# rule: <rule id>`. The milestone that switches each one on is
in MILESTONE_HANDLERS.
"""

from __future__ import annotations

HANDLERS = (
    "h.07.after_conflict",  # M2
    "h.07.affliction_onset",  # M2
    "h.07.fatigue",  # M2
    "h.07.natural_recovery",  # M1
    "h.07.rest_recovery",  # M1
    "h.07.dying_check",  # M2
    "h.07.lethal_scan",  # M1
    "h.07.load_clear",  # M1
    "h.07.affliction_day",  # M2
    "h.07.curse_cycle",  # M2
    "h.07.vitality_max",  # M3
    "h.07.career_end",  # M1
)
