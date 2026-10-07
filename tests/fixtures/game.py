"""Builders for tests that need a game on disk. See engine/CONVENTIONS.md "Tests".

    store = new_store(tmp_path)                       # a fresh game file with game_created (seed 1234)
    with store.transaction("turn.1") as tx:
        tx.add(entity("pc", "Wren", quantities={"vitality": (10, 0, 10)}, tx=tx))
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from engine import ids
from engine.store.db import Store
from engine.store.events import EntityRecord, Event, Quantity

TEST_RULES_HASH = "test-rules-hash"


def new_store(tmp_path: Path, seed: int = 1234, name: str = "game.db", milestone: int = 1) -> Store:
    """A new game in `tmp_path` (no rules hashing: the stamp is TEST_RULES_HASH)."""
    return Store.create(tmp_path / name, seed=seed, milestone=milestone, config={"test": True},
                        rules_hash=TEST_RULES_HASH)


def entity(kind: str, name: str, *, tx: Any, visibility: str = "shown", sealed: dict[str, Any] | None = None,
           slices: dict[str, str] | None = None, data: dict[str, Any] | None = None,
           quantities: dict[str, tuple[int, int, int | None]] | None = None, gate: str | None = None) -> Event:
    """An entity_created event. `sealed` adds sealed data fields; `quantities` maps name -> (current, min, max)."""
    eid = ids.entity_id(kind, name, tx.state.entities)
    fields = {**(data or {}), **(sealed or {})}
    rec = EntityRecord(id=eid, kind=kind, name=name, visibility=visibility,  # type: ignore[arg-type]
                       sealed_fields=sorted(sealed or {}), data=fields)
    qs = {k: Quantity(current=c, min=lo, max=hi) for k, (c, lo, hi) in (quantities or {}).items()}
    return Event.of("entity_created", source="test", rule_id="00.14.2", entity=rec, quantities=qs,
                    slices=slices or {}, gate=gate)
