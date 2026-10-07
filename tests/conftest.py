"""Makes src/ importable from tests/ without packaging src as an installed module."""

import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def pytest_addoption(parser):  # type: ignore[no-untyped-def]
    parser.addoption("--runslow", action="store_true", default=False,
                     help="also run tests marked slow (e.g. the 500-turn offline game, T076)")


def pytest_configure(config):  # type: ignore[no-untyped-def]
    config.addinivalue_line("markers", "slow: long-running; skipped unless --runslow or RUN_SLOW=1 is given")


def pytest_collection_modifyitems(config, items):  # type: ignore[no-untyped-def]
    import os

    import pytest

    if config.getoption("--runslow") or os.environ.get("RUN_SLOW") == "1":
        return
    skip = pytest.mark.skip(reason="slow: run with --runslow (or RUN_SLOW=1)")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip)
