"""Owner 11 handlers: the living world (M6). None built yet; each logs handler_skipped until registered here.

Register an implementation in this file with `@handler("<id>")` (see engine/time/handlers/__init__.py),
calling into the owning module; tag it `# rule: <rule id>`. The milestone that switches each one on is
in MILESTONE_HANDLERS.
"""

from __future__ import annotations

HANDLERS = (
    "h.11.fallback_counters",  # M1
    "h.11.situation_timelines",  # M6
    "h.11.world_turn",  # M6
    "h.11.season_turn",  # M6
    "h.11.year_turn",  # M6
    "h.11.reckoning",  # M6
    "h.11.world_record",  # M6
    "h.11.moon",  # M6
    "h.11.festival",  # M6
)
