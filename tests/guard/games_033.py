"""Spec 033 P6 (T070): every `cases.md` row runs under the VIII.9 guard in raise mode.

The rows already live as dm-tools games in the phases' test modules (`GUARDED`). `tests/engine/conftest.py` plays each
test of those modules inside `Guard(mode="raise")` and fails the test if the game reached a denylisted function.
Case ids map to the module that plays them (`CASES`); `tests/engine/test_spec033_guard.py` checks each id is named in its module and
that the module is guarded, so a case dropped from the games fails by name.
"""

from __future__ import annotations

# module (under tests/engine) -> the cases.md sections its games play
CASES: dict[str, tuple[str, ...]] = {
    "test_spec032_p8a": ("C1.a",),  # every verb x a person, a creature, a thing
    "test_spec033_p2a": ("C1.d", "C1.e", "C1.f", "C1.g", "C2", "C3", "C5"),
    "test_stated_gate": ("C1.b", "C1.c", "C5"),
    "test_spec033_p3": ("C4", "C5"),
    "test_spec033_p4": ("C8", "C9"),
    "test_spec033_p5": ("C6", "C7", "C10"),
}

# also guarded: the older dm-tools games (the 032 cases and engine tests), which must stay clean too
GUARDED: tuple[str, ...] = (*CASES, "test_spec033_p1", "test_spec033_guard", "test_dm_tools", "test_spec032_cases",
                            "test_spec032_engine", "test_spec032_p3", "test_spec032_p4", "test_spec032_p5a",
                            "test_spec032_p5b", "test_spec032_p6", "test_spec032_p8b")
