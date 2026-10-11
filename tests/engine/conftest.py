"""Shared fixtures for tests/engine."""

from __future__ import annotations

from typing import Any

import pytest

# Older tests that propose a melee attack with no position on record. Each should state an engaged band (or a
# `change position` step) and leave this list; spec 033 P6 removes the rest.
NEEDS_NO_REACH_CHECK = ("test_spec032_p3", "test_spec032_p4", "test_spec032_p5a", "test_spec032_p8a",
                        "test_spec032_p8b")


@pytest.fixture(autouse=True)
def _no_reach_refusal(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> None:
    """Spec 033 P3 (06.4.3): a melee attack on a target not engaged is refused (tests/engine/test_spec033_p3.py tests
    that rule). The modules in NEEDS_NO_REACH_CHECK predate it and run with the check off."""
    if not request.module.__name__.endswith(NEEDS_NO_REACH_CHECK):
        return
    from engine.dm import dm_tools

    def reach_ok(*args: Any, **kw: Any) -> str:
        return ""

    monkeypatch.setattr(dm_tools, "_reach", reach_ok)
