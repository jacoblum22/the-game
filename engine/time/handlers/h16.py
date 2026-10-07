"""Owner 16 handlers: allies and downtime (M7). None built yet; each logs handler_skipped until registered here.

Register an implementation in this file with `@handler("<id>")` (see engine/time/handlers/__init__.py),
calling into the owning module; tag it `# rule: <rule id>`. The milestone that switches each one on is
in MILESTONE_HANDLERS.
"""

from __future__ import annotations

HANDLERS = (
    "h.16.retinue_upkeep",  # M7
    "h.16.contract_term",  # M7
    "h.16.conflict_orders",  # M7
    "h.16.follower_offers",  # M7
    "h.16.season_growth",  # M7
    "h.16.venture_end",  # M7
    "h.16.held_line",  # M2
    "h.16.loyalty_record",  # M7
)
