"""The continuity checker (dm/check.py) is off in the tests that don't test it: it would take a scripted model call."""
import pytest

from dm import check


@pytest.fixture(autouse=True)
def no_checker(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(check, "ENABLED", False)
