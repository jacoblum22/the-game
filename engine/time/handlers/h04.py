"""Owner 04 handlers: callings (M3). None built yet; each logs handler_skipped until registered here.

Register an implementation in this file with `@handler("<id>")` (see engine/time/handlers/__init__.py),
calling into the owning module; tag it `# rule: <rule id>`. The milestone that switches each one on is
in MILESTONE_HANDLERS.
"""

from __future__ import annotations

HANDLERS = (
    "h.04.recognition_pass",  # M3
    "h.04.standing_offers",  # M3
    "h.04.season_consolidation",  # M3
    "h.04.crisis_check",  # M3
    "h.04.provisional_check",  # M3
    "h.04.fraying_check",  # M3
)
