"""Typed id helpers. Ids are deterministic: no uuid, no clock time, so a replay mints the same ids.

Two kinds of runtime id:
- **name ids** for entities: ``<prefix>.<slug>`` (``npc.tam_harlan``), with ``_2``, ``_3``... on a clash.
- **counter ids** for everything else: ``<prefix>.<n>`` (``fact.12``, ``frame.3``, ``scn.2``). The counters live
  in the projection (``WorldState.counters``), are advanced by the reducers from the ids that events create, and
  so are rebuilt exactly from the event log. Mint them through ``Transaction.mint(prefix)``.

Event ids are the event's ``seq`` (an int, monotone, assigned by the store on append).
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Container, Mapping
from typing import NewType

EntityId = NewType("EntityId", str)
FactId = NewType("FactId", str)
FrameId = NewType("FrameId", str)
SceneId = NewType("SceneId", str)
TurnId = NewType("TurnId", str)
ClockId = NewType("ClockId", str)
InstanceId = NewType("InstanceId", str)
EventSeq = NewType("EventSeq", int)

# Counter-id prefixes. Data ids (00.16.2) never use these, except `scn.` which 00.16.2 reserves for scenes.
FACT = "fact"
FRAME = "frame"
SCENE = "scn"
TURN = "turn"
CONDITION_INSTANCE = "cinst"
EVIDENCE = "evd"
RULING = "rul"
PAUSE = "pause"
BEAT = "beat"

# Entity kind (00.6.2 Entity.kind) -> id prefix. 00.16.2 prefixes where they exist; `foe.` and `ally.` because
# `adv.` and `cmp.` are data templates, not instances.
ENTITY_PREFIX: Mapping[str, str] = {
    "pc": "pc",
    "npc": "npc",
    "adversary": "foe",
    "companion": "ally",
    "item": "item",
    "place": "loc",
    "faction": "fac",
    "thread": "thr",
    "rumor": "rum",
    "clue": "clu",
    "object": "obj",
}

_COUNTER_ID = re.compile(r"^([a-z_]+)\.(\d+)$")


def slug(text: str) -> str:
    """snake_case ASCII slug of a name (00.16.1): 'Tam Harlan' -> 'tam_harlan'."""
    norm = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-z0-9]+", "_", norm.lower()).strip("_")
    return s or "x"


def entity_id(kind: str, name: str, taken: Container[str]) -> EntityId:
    """A name id for a new entity of `kind`, unique against `taken` (ids already in the projection)."""
    base = f"{ENTITY_PREFIX[kind]}.{slug(name)}"
    candidate, n = base, 1
    while candidate in taken:
        n += 1
        candidate = f"{base}_{n}"
    return EntityId(candidate)


def clock_id(name: str, taken: Container[str]) -> ClockId:
    """`clk.<slug>` for a clock instance (00.8.1 example: clk.alarm_grey_keep), unique against `taken`."""
    base = f"clk.{slug(name)}"
    candidate, n = base, 1
    while candidate in taken:
        n += 1
        candidate = f"{base}_{n}"
    return ClockId(candidate)


def counter_id(prefix: str, n: int) -> str:
    return f"{prefix}.{n}"


def parse_counter_id(value: str) -> tuple[str, int] | None:
    """('fact', 12) for 'fact.12'; None for a name id."""
    m = _COUNTER_ID.match(value)
    return (m.group(1), int(m.group(2))) if m else None


class IdMint:
    """Mints counter ids on top of the projection's counters. One per transaction (see Store.transaction)."""

    def __init__(self, counters: Mapping[str, int]) -> None:
        self._base = counters
        self._local: dict[str, int] = {}

    def mint(self, prefix: str) -> str:
        n = max(self._base.get(prefix, 0), self._local.get(prefix, 0)) + 1
        self._local[prefix] = n
        return counter_id(prefix, n)
