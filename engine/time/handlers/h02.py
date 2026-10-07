"""Owner 02 handlers: character creation (engine/dm/creation). None built yet; each logs handler_skipped until registered here.

Register an implementation in this file with `@handler("<id>")` (see engine/time/handlers/__init__.py),
calling into the owning module; tag it `# rule: <rule id>`. The milestone that switches each one on is
in MILESTONE_HANDLERS.
"""

from __future__ import annotations

HANDLERS = (
    "h.02.creation_lock",  # M1
    "h.02.bent_offer",  # M1
    "h.02.open_slots",  # M1
)
