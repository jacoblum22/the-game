"""Owner 10 handlers: exploration and travel (engine/world). None built yet; each logs handler_skipped until registered here.

Register an implementation in this file with `@handler("<id>")` (see engine/time/handlers/__init__.py),
calling into the owning module; tag it `# rule: <rule id>`. The milestone that switches each one on is
in MILESTONE_HANDLERS.
"""

from __future__ import annotations

HANDLERS = (
    "h.10.site_time",  # M1
    "h.10.light",  # M4
    "h.10.site_check",  # M4
    "h.10.travel_progress",  # M4
    "h.10.watch_check",  # M4
    "h.10.supply",  # M4
    "h.10.weather",  # M4
    "h.10.weather_regime",  # M4
    "h.10.venture",  # M4
    "h.10.site_exposure",  # M4
    "h.10.watch_exposure",  # M4
    "h.10.wayfinding",  # M4
    "h.10.site_recovery",  # M4
    "h.10.day_reset",  # M4
    "h.10.site_regrowth",  # M4
    "h.10.scene_frame",  # M1
)
