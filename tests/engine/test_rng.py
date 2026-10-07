"""Named RNG streams: determinism, logging, resume equality (T018, RNG half)."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

import pytest

from engine.rng import Rng, RngDivergence, stream_seed
from engine.store.db import Store
from tests.fixtures.game import new_store


def _script(rng: Rng, n: int) -> list:
    out = []
    for i in range(n):
        out.append(rng.d(20, f"check {i}"))
        out.append(rng.d100(f"oracle {i}", stream="oracle"))
        out.append(rng.choice(["a", "b", "c"], f"name {i}", stream="gen", table_id="tbl.names"))
        out.append(rng.weighted({"x": 3, "y": 1, "z": 0}, f"pool {i}", stream="gen"))
    return out


def test_same_seed_same_draws() -> None:
    assert _script(Rng(42), 20) == _script(Rng(42), 20)
    assert _script(Rng(42), 20) != _script(Rng(43), 20)


def test_streams_are_independent() -> None:
    a, b = Rng(7), Rng(7)
    for _ in range(50):
        b.d(6, "noise", stream="gen")
    assert [a.d(20, "x") for _ in range(10)] == [b.d(20, "x") for _ in range(10)]
    assert stream_seed(7, "dice") != stream_seed(7, "gen")


def test_every_draw_is_logged_with_purpose(tmp_path: Path) -> None:
    store = new_store(tmp_path)
    rng = Rng.for_store(store)
    r = rng.d(20, "roll_check frame.1")
    v = rng.choice(["x", "y"], "pick a name", stream="gen", table_id="tbl.name_given")
    rows = store.rng_draws()
    assert [(d["stream"], d["purpose"], d["sides"], d["table_id"], d["result"]) for d in rows] == [
        ("dice", "roll_check frame.1", 20, None, r),
        ("gen", "pick a name", 2, "tbl.name_given", ["x", "y"].index(v) + 1),
    ]
    with pytest.raises(ValueError):
        rng.d(6, "")


def test_resume_draws_exactly_what_an_unbroken_game_would(tmp_path: Path) -> None:
    unbroken = Rng(1234)
    expected = _script(unbroken, 30)

    store = new_store(tmp_path)  # seed 1234
    first = _script(Rng.for_store(store), 12)
    store.close()
    resumed = Store.open(tmp_path / "game.db")
    rest = []
    rng = Rng.for_store(resumed)
    for i in range(12, 30):  # continue the same script
        rest.append(rng.d(20, f"check {i}"))
        rest.append(rng.d100(f"oracle {i}", stream="oracle"))
        rest.append(rng.choice(["a", "b", "c"], f"name {i}", stream="gen", table_id="tbl.names"))
        rest.append(rng.weighted({"x": 3, "y": 1, "z": 0}, f"pool {i}", stream="gen"))
    assert first + rest == expected


def test_draws_inside_a_rolled_back_transaction_are_undone(tmp_path: Path) -> None:
    store = new_store(tmp_path)
    rng = Rng.for_store(store)
    with pytest.raises(RuntimeError):
        with store.transaction():
            rng.d(20, "lost")
            raise RuntimeError
    with store.transaction():
        kept = rng.d(20, "kept")
    assert kept == Rng(1234).d(20, "first")
    assert [d["purpose"] for d in store.rng_draws()] == ["kept"]
    # and a resumed game agrees
    assert Rng.for_store(Store.open(store.path)).d(20, "next") == rng.d(20, "next")


def test_replay_detects_divergence() -> None:
    with pytest.raises(RngDivergence):
        Rng(1).replay([{"seq": 1, "stream": "dice", "sides": 1000000, "result": -1}])


def test_weighted_and_pick() -> None:
    rng = Rng(5)
    counts = Counter(rng.weighted([("a", 1), ("b", 3), ("never", 0)], "w") for _ in range(4000))
    assert counts["never"] == 0 and 2.5 < counts["b"] / counts["a"] < 3.6
    table = {"id": "tbl.t", "die": "d6", "results": [{"range": "1-3", "result": "low"}, {"range": "4", "result": "four"},
                                                     {"range": [5, 6], "result": "high"}]}
    seen = {rng.pick(table, "t")[1]["result"] for _ in range(200)}
    assert seen == {"low", "four", "high"}
    assert 2 <= rng.roll_die("2d6", "sum") <= 12
    with pytest.raises(ValueError):
        rng.weighted({"a": 0}, "zero")
