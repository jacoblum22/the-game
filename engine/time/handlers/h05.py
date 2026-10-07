"""Owner 05 handlers: abilities and Focus (engine/abilities). None built yet; each logs handler_skipped until registered here.

Register an implementation in this file with `@handler("<id>")` (see engine/time/handlers/__init__.py),
calling into the owning module; tag it `# rule: <rule id>`. The milestone that switches each one on is
in MILESTONE_HANDLERS.
"""

from __future__ import annotations

HANDLERS = (
    "h.05.round_recharge",  # M2
    "h.05.conflict_recharge",  # M2
    "h.05.scene_recharge",  # M1
    "h.05.day_recharge",  # M1
    "h.05.focus_recover",  # M1
    "h.05.rest_recharge",  # M1
    "h.05.reslot",  # M3
    "h.05.reserve",  # M3
    "h.05.provisional_abilities",  # M3
)
