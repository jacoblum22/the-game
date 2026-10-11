"""Shared fixtures for tests/engine."""

from __future__ import annotations

from typing import Any

import pytest


@pytest.fixture(autouse=True)
def _no_reach_refusal(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> None:
    """Spec 033 P3 (06.4.3): a melee attack on a target not engaged is refused. Only tests/engine/test_spec033_p3.py
    tests that rule; older tests propose attacks with no position on record, so the check is off for them."""
    if request.module.__name__.endswith("test_spec033_p3"):
        return
    from engine.dm import dm_tools

    def reach_ok(*args: Any, **kw: Any) -> str:
        return ""

    monkeypatch.setattr(dm_tools, "_reach", reach_ok)
