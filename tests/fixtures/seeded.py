"""A game file holding a rolled, packed world seed (as `seed_flow.write_world` writes it) and the PC `pc.wren` at the
opening place, optionally with an anchor bond (02.9.2)."""

from __future__ import annotations

from functools import cache
from pathlib import Path
from typing import Any

from engine.dm.seed_flow import write_world
from engine.gen.world_seed import SeededWorld, build_rolled
from engine.store.db import Store
from engine.store.events import Event
from tests.fixtures.game import entity, new_store


@cache
def world(seed: int) -> SeededWorld:
    return build_rolled(seed)


def seeded_store(tmp_path: Path, seed: int, *, anchor: Any = None, name: str = "game.db") -> tuple[Store, SeededWorld]:
    store = new_store(tmp_path, seed=seed, name=name)
    w = world(seed)
    with store.transaction() as tx:
        write_world(tx, w)
        tx.add(entity("pc", "Wren", tx=tx, quantities={"vitality": (10, 0, 10)}))
        tx.add(Event.of("position_set", source="test", rule_id="10.1.1", entity="pc.wren", location=w.incident.place))
        if anchor is not None:
            tx.add(Event.of("fact_set", {"source": "player_accepted"}, source="test", rule_id="02.9.2",
                            fact_id=tx.mint("fact"), subject="pc.wren", predicate="bond.anchor", value=anchor))
    return store, w
