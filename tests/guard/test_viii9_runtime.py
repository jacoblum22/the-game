"""Spec 033 R12, the runtime half: the offline dm-tools game plays with the denylist patched in. Entries still `log`
are recorded, never raised (P0: all of them); a phase moves its entries to `raise` and the game must then not hit one.
Planted calls (C12) prove each entry fails with the constitution's VIII.9 and its inventory id."""

from __future__ import annotations

import json
import operator
import types
from pathlib import Path
from typing import Any

import pytest

from engine.resolve import conflict
from tests.guard import census
from tests.guard.viii9 import DENY, Entry, Guard, Viii9Violation, _resolve


def test_the_recorded_dm_tools_game_hits_no_raise_entry_and_the_guard_is_alive() -> None:
    g = census.play_recorded(Guard(mode="raise"))
    assert g.raised() == [], "\n".join(f"constitution VIII.9: {h['name']} ({h['inv']})" for h in g.raised()[:10])
    assert g.hits, "the guard recorded nothing: it is not patching"  # P0: every entry is still `log`


def test_every_deny_entry_resolves_and_has_a_known_phase() -> None:
    for name, e in DENY.items():
        _resolve(name)  # a rename in the engine fails here
        assert e.phase in ("P2a", "P2b", "P3", "P4", "P5") and e.mode in ("log", "raise"), name


def _planted(name: str, entry: Entry) -> Guard:
    return Guard(deny={name: Entry(entry.inv, entry.phase, "raise", entry.only_from, entry.scope)}, watch={},
                 mode="raise", record_reach=False)


def _touch(name: str) -> None:
    mod, attr, _ = _resolve(name)
    obj: Any = getattr(mod, attr)
    if isinstance(obj, types.FunctionType):
        obj()
    else:
        try:
            operator.contains(obj, "x")  # any use of a pattern, word list or table is a hit
        except TypeError:
            pass


@pytest.mark.parametrize("name", list(DENY))
def test_a_planted_call_fails_with_viii9_and_the_inventory_id(name: str) -> None:
    entry = DENY[name]
    if entry.only_from:
        pytest.skip("covered by test_only_from_lets_the_one_caller_through")
    g = _planted(name, entry)
    with g:
        g.turn_depth = g.shell_depth = 1  # as if inside a dm-tools turn
        with pytest.raises(Viii9Violation, match=r"constitution VIII\.9") as err:
            _touch(name)
    assert entry.inv in str(err.value) and g.raised()


def test_an_unarmed_hit_outside_a_dm_tools_turn_is_not_a_hit() -> None:
    name = "engine.dm.testimony.overlap"
    g = _planted(name, DENY[name])
    with g:
        _touch_safely(name)
    assert g.hits == []


def _touch_safely(name: str) -> None:
    try:
        _touch(name)
    except TypeError:  # the real function wants arguments; the guard let it through
        pass


def test_only_from_lets_the_one_caller_through_and_stops_every_other() -> None:
    name = "engine.resolve.conflict.start"
    e = Entry("A4 A5", "P2a", "raise", f"{__name__}.call_start")
    g = Guard(deny={name: e}, watch={}, mode="raise", record_reach=False)
    with g:
        g.turn_depth = 1
        with pytest.raises(TypeError):  # reached the real function (no args): passed the guard
            call_start()
        assert g.hits == []
        with pytest.raises(Viii9Violation, match=r"constitution VIII\.9.*A4 A5"):
            call_start_elsewhere()


def call_start() -> None:
    conflict.start()  # type: ignore[call-arg]


def call_start_elsewhere() -> None:
    conflict.start()  # type: ignore[call-arg]


def test_log_mode_writes_jsonl_and_never_raises(tmp_path: Path) -> None:
    name = "engine.dm.testimony.overlap"
    out = tmp_path / "hits.jsonl"
    e = Entry("M", "P4", "raise")
    g = Guard(deny={name: e}, watch={}, mode="log", jsonl=out, record_reach=False)
    with g:
        g.turn_depth = 1
        _touch_safely(name)
    rows = [json.loads(x) for x in out.read_text(encoding="utf-8").splitlines()]
    assert rows and rows[0]["name"] == name and rows[0]["mode"] == "log" and g.raised() == []
