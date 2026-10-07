"""T052: the engine's world seed reproduces `rules/_process/simulation/12-world-seed.py` exactly on the same seed.

The reference script is imported (it is slow to load: about 20 s, once per module) and its `build_seed` and
`check_seed` are compared with the port's on several seeds, in oracle mode and in its own guided run.
"""

from __future__ import annotations

from types import ModuleType
from typing import Any

import pytest

from engine.gen._seed_check import check_seed
from engine.gen.build_tables import load_module
from engine.gen.world_seed import build_answered, build_rolled

SEEDS = [1, 2, 7, 42, 1001, 1002, 1003, 1077, 1150, 1200]
# the reference's own guided run (12-world-seed.py main(): seed 2, these answers, the rest by the oracle)
GUIDED = {"ws.q.wound": "long_winter", "ws.q.climate": "northern", "ws.q.magic_level": "rare", "ws.q.keeper_count": "2",
          "ws.q.keepers": ["kf.hearth", "kf.death"], "ws.q.bargainer": "death_keeper", "ws.q.haven_tier": "village",
          "ws.q.haven_site": "hill", "ws.q.rulers": "org.clan.family", "ws.q.inciting": "refugees",
          "ws.q.month_names": "named", "ws.q.extra_impossible": ["no_teleport"], "ws.q.second_tongue": "old_tongue",
          "ws.q.arcane_source": "order_only"}


@pytest.fixture(scope="module")
def ref() -> ModuleType:
    return load_module("ws12_reference", "12-world-seed.py")


def plain(x: Any) -> Any:
    """OrderedDicts and tuples to dicts and lists, so the comparison is structural."""
    if isinstance(x, dict):
        return {k: plain(v) for k, v in x.items()}
    if isinstance(x, list | tuple):
        return [plain(v) for v in x]
    return x


def first_diff(a: Any, b: Any, path: str = "") -> str | None:
    if isinstance(a, dict) and isinstance(b, dict):
        if list(a) != list(b):
            return f"{path}: keys {list(a)} vs {list(b)}"
        for k in a:
            d = first_diff(a[k], b[k], f"{path}/{k}")
            if d:
                return d
        return None
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return f"{path}: {len(a):d} vs {len(b):d} items"
        for i, (x, y) in enumerate(zip(a, b, strict=True)):
            d = first_diff(x, y, f"{path}[{i:d}]")
            if d:
                return d
        return None
    if type(a) is not type(b) or a != b:
        return f"{path}: {a!r} vs {b!r}"
    return None


@pytest.mark.parametrize("seed", SEEDS)
def test_rolled_seed_matches_reference(ref: ModuleType, seed: int) -> None:
    want = plain(ref.build_seed(seed))
    got = plain(build_rolled(seed).record)
    assert first_diff(want, got) is None


def test_guided_run_matches_reference(ref: ModuleType) -> None:
    want = plain(ref.build_seed(2, GUIDED))
    world = build_answered(2, GUIDED)
    assert first_diff(want, plain(world.record)) is None
    assert {a.question for a in world.answers if a.source == "player"} == set(GUIDED)


@pytest.mark.parametrize("seed", [1, 1001])
def test_seed_check_matches_reference(ref: ModuleType, seed: int) -> None:
    reg = build_rolled(seed).record
    want = [tuple(r) for r in ref.check_seed(plain(ref.build_seed(seed)))]
    got = check_seed(reg)
    assert got == want
    assert all(ok for _, ok, _ in got), [r for r in got if not r[1]]
