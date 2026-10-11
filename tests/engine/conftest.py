"""Shared fixtures for tests/engine."""

from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

import pytest

from tests.guard.games_033 import GUARDED
from tests.guard.viii9 import Guard


@pytest.fixture(scope="module")
def _viii9_guard(request: pytest.FixtureRequest) -> Iterator[Guard | None]:
    """Spec 033 R12: the dm-tools games of the modules in GUARDED run with the denylist raising (patched once)."""
    if request.module.__name__.rsplit(".", 1)[-1] not in GUARDED:
        yield None
        return
    out = os.environ.get("VIII9_REACH_FILE")  # `py -m tests.guard.census reached` collects what the games reach
    with Guard(mode="raise", record_reach=bool(out)) as g:
        yield g
    if out:
        from tests.guard.census import reach_lines

        with Path(out).open("a", encoding="utf-8") as fh:
            fh.writelines(f"{x}\n" for x in sorted(reach_lines(g)))


@pytest.fixture(autouse=True)
def _viii9(_viii9_guard: Guard | None) -> Iterator[None]:
    """A hit inside a dm-tools turn fails the test that played it (`dm_tools.tool` swallows the exception)."""
    before = len(_viii9_guard.hits) if _viii9_guard else 0
    yield
    if _viii9_guard is not None:
        new = [h for h in _viii9_guard.hits[before:] if h["mode"] == "raise"]
        assert not new, "\n".join(f"constitution VIII.9: {h['name']} ({h['inv']}) via {h['path']}" for h in new[:8])
