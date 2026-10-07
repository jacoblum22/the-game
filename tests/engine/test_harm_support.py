"""Shared builders for the harm and ability tests (no tests here)."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

from engine import ids
from engine.data.loader import load_rules
from engine.harm.ctx import HarmCtx
from engine.store.db import Store
from engine.store.events import Event, SceneRecord
from tests.fixtures.game import entity, new_store

RULES = load_rules()


class FixedDice:
    """Dice that return the given naturals in order; `pick` rolls the table's die the same way."""

    def __init__(self, *rolls: int) -> None:
        self.rolls = list(rolls)
        self.calls: list[str] = []

    def d(self, sides: int, purpose: str, *, stream: str = "dice") -> int:
        self.calls.append(purpose)
        n = self.rolls.pop(0)
        assert 1 <= n <= sides, (n, sides, purpose)
        return n

    def pick(self, table: Any, purpose: str, *, stream: str = "tables") -> tuple[int, Any]:
        sides = int(str(table["die"]).removeprefix("d"))
        n = self.d(sides, purpose)
        for row in table["results"]:
            lo, _, hi = str(row["range"]).partition("-")
            if int(lo) <= n <= int(hi or lo):
                return n, row
        raise AssertionError(f"no row for {n}")


def ctx(tx: Any, rng: Any = None, *, boundary: str | None = None, payload: dict[str, Any] | None = None) -> HarmCtx:
    return HarmCtx.of(tx, RULES, rng, boundary=boundary, payload=payload)


def make_game(tmp_path: Path, *, vitality: int = 13, vmax: int | None = None, fate: int = 1, endurance: int = 2,
              focus: int | None = None, abilities: list[str] | None = None, pc_data: dict[str, Any] | None = None,
              others: Sequence[tuple[str, str, dict[str, Any], int]] = (), scene: bool = True) -> Store:
    """A game with PC Wren (Vitality `vitality`/`vmax`, fate, Endurance as the Endure modifier), optional
    Focus and abilities, other entities `(kind, name, data, vitality)`, and an open scene casting them."""
    store = new_store(tmp_path)
    with store.transaction() as tx:
        qs: dict[str, tuple[int, int, int | None]] = {"vitality": (vitality, 0, vmax or vitality), "fate": (fate, 0, 3)}
        if focus is not None:
            qs["focus"] = (focus, 0, focus)
        data = {"attributes": {"endurance": endurance}, "abilities": abilities or [], **(pc_data or {})}
        tx.add(entity("pc", "Wren", tx=tx, quantities=qs, data=data))
        cast = []
        for kind, name, d, v in others:
            ev = entity(kind, name, tx=tx, data=d, quantities={"vitality": (v, 0, v)} if v else None)
            tx.add(ev)
            cast.append(ev.payload.entity.id)  # type: ignore[attr-defined]
        if scene:
            sid = tx.mint(ids.SCENE)
            tx.add(Event.of("scene_started", scene_id=sid, scene=SceneRecord(scene_id=sid, cast_present=cast)))
    return store


def run(store: Store, fn: Callable[..., Any], *args: Any, rng: Any = None, boundary: str | None = None,
        payload: dict[str, Any] | None = None, **kw: Any) -> Any:
    """Call `fn(ctx, *args, **kw)` in a transaction and stage what it returns (`.events` or a list)."""
    with store.transaction() as tx:
        res = fn(ctx(tx, rng, boundary=boundary, payload=payload), *args, **kw)
        tx.add_all(res if isinstance(res, list) else res.events)
    return res


def next_beat(store: Store, n: int = 1) -> None:
    """The player declares: the beat counter moves on (07.3.5)."""
    with store.transaction() as tx:
        now = tx.state.time.now
        tx.add(Event.of("time_advanced", {"from": now}, to=now.model_copy(update={"beat": now.beat + n})))


def vit(store: Store, eid: str = "pc.wren") -> int:
    return store.state.quantities[eid]["vitality"].current
