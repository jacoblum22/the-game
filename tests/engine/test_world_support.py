"""Shared builders for the engine/world tests (a seeded world in a fresh game, a PC placed at the opening)."""

from __future__ import annotations

from functools import cache
from pathlib import Path
from typing import Any

from engine.data.loader import Rules, load_rules
from engine.gen.world_seed import SeededWorld, build_rolled
from engine.rng import Rng
from engine.store.db import Store
from engine.time.scheduler import TimeContext
from engine.world.places import put, seed_world_into_store
from tests.fixtures.game import entity, new_store


@cache
def world(seed: int) -> SeededWorld:
    return build_rolled(seed)


@cache
def rules() -> Rules:
    return load_rules()


class Game:
    """A store with a seeded world and the PC `pc.wren` at the opening place."""

    def __init__(self, tmp_path: Path, seed: int = 7, name: str = "game.db") -> None:
        self.world = world(seed)
        self.rules = rules()
        self.store: Store = new_store(tmp_path, name=name)
        self.rng = Rng.for_store(self.store)
        with self.store.transaction() as tx:
            self.threads = seed_world_into_store(tx, self.world)
            tx.add(entity("pc", "Wren", tx=tx, quantities={"vitality": (10, 0, 10)}))
            put(tx, "pc.wren", self.world.incident.place)
        self.pc = "pc.wren"

    def run(self, fn: Any, turn: str | None = None) -> Any:
        """Run `fn(ctx)` in one transaction and return its result."""
        with self.store.transaction(turn) as tx:
            return fn(TimeContext(tx, self.rules, self.rng))

    @property
    def state(self) -> Any:
        return self.store.state


def test_game_builds(tmp_path: Path) -> None:
    g = Game(tmp_path)
    assert g.state.positions["pc.wren"].location == g.world.incident.place
    assert g.store.rebuild() == g.state
