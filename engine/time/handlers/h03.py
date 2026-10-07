"""Owner 03 handlers: evidence (M3). None built yet; each logs handler_skipped until registered here.

Register an implementation in this file with `@handler("<id>")` (see engine/time/handlers/__init__.py),
calling into the owning module; tag it `# rule: <rule id>`. The milestone that switches each one on is
in MILESTONE_HANDLERS.
"""

from __future__ import annotations

HANDLERS = (
    "h.03.antigrind_reset",  # M3
    "h.03.recency_update",  # M3
    "h.03.day_settle",  # M3
)
