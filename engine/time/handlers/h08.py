"""Owner 08 handlers: items (M5). None built yet; each logs handler_skipped until registered here.

Register an implementation in this file with `@handler("<id>")` (see engine/time/handlers/__init__.py),
calling into the owning module; tag it `# rule: <rule id>`. The milestone that switches each one on is
in MILESTONE_HANDLERS.
"""

from __future__ import annotations

HANDLERS = (
    "h.08.upkeep",  # M5
    "h.08.markets",  # M5
    "h.08.durations",  # M1
    "h.08.craft_decay",  # M5
)
