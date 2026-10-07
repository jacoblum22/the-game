"""Recharge and Focus recovery (05.4.6, 05.6.9; PR-05-4) and the h.05 M1 handlers."""

from __future__ import annotations

import pytest

from engine.abilities.recharge import (
    focus_gain,
    h_05_day_recharge,
    h_05_focus_recover,
    h_05_rest_recharge,
    h_05_scene_recharge,
    refreshed_by,
)
from engine.abilities.use import commit_use
from engine.harm.rest import rest_payload
from engine.store.events import Event
from tests.engine.test_harm_support import make_game, run

SWORN = "ab.sworn_purpose"  # per rest_long
PRESS = "ab.pressing_advantage"  # per scene_end
OFFICE = "ab.daily_office"  # per day


def test_refresh_ladder():
    assert refreshed_by("scene_end") == {"round", "conflict_end", "scene_end"}
    assert refreshed_by("rest_short") == {"round", "conflict_end", "scene_end", "rest_short"}
    assert "rest_long" in refreshed_by("rest_long") and "day" not in refreshed_by("rest_long")
    assert refreshed_by("day") == {"day"}


@pytest.mark.parametrize(("kind", "quality", "cur", "mx", "b", "s", "res", "want"), [
    ("breather", "full", 0, 6, 0, 0, False, 1), ("breather", "full", 0, 6, 2, 0, False, 0),
    ("breather", "full", 0, 6, 0, 0, True, 2), ("breather", "interrupted", 0, 6, 0, 0, True, 0),
    ("rest_short", "full", 0, 7, 0, 0, False, 4), ("rest_short", "partial", 0, 7, 0, 0, False, 2),
    ("rest_short", "interrupted", 0, 7, 0, 0, False, 1), ("rest_short", "full", 0, 7, 0, 2, False, 1),
    ("rest_long", "full", 0, 7, 0, 0, False, 7), ("rest_long", "partial", 0, 7, 0, 0, False, 6),
    ("rest_long", "interrupted", 0, 7, 0, 0, False, 2)])
def test_focus_by_rest(kind, quality, cur, mx, b, s, res, want):  # 05.6.9
    assert focus_gain(kind, quality, cur, mx, breathers_since_short=b, short_rests_today=s, resonant=res) == want


def _drain(store, n):
    with store.transaction() as tx:
        q = tx.state.quantities["pc.wren"]["focus"]
        tx.add(Event.of("quantity_changed", entity="pc.wren", quantity="focus", delta=-n, new_value=q.current - n,
                        reason="test"))


def test_breather_limit_and_short_rest_reset(tmp_path):
    store = make_game(tmp_path, focus=6)
    _drain(store, 6)
    p = rest_payload("breather", "full", "camp")
    for want in (1, 2, 2):
        run(store, h_05_focus_recover, boundary="breather", payload=p)
        assert store.state.quantities["pc.wren"]["focus"].current == want
    run(store, h_05_rest_recharge, boundary="rest_short", payload=rest_payload("rest_short", "full", "camp"))
    assert store.state.meta["pc.wren.breathers_since_short_rest"] == 0


def test_uses_refresh_by_boundary(tmp_path):
    store = make_game(tmp_path, focus=4, abilities=[SWORN, PRESS, OFFICE])
    for ab in (SWORN, PRESS, OFFICE):
        run(store, commit_use, "pc.wren", ab)

    def left(ab):
        return store.state.quantities["pc.wren"][f"uses.{ab}"].current

    run(store, h_05_scene_recharge, boundary="scene_end")
    assert (left(SWORN), left(PRESS), left(OFFICE)) == (0, 1, 0)
    run(store, h_05_rest_recharge, boundary="rest_long", payload=rest_payload("rest_long", "interrupted", "camp"))
    assert left(SWORN) == 0  # an interrupted rest refreshes nothing
    run(store, h_05_rest_recharge, boundary="rest_long", payload=rest_payload("rest_long", "partial", "camp"))
    assert left(SWORN) == 1 and left(OFFICE) == 0
    run(store, h_05_day_recharge, boundary="day")
    assert left(OFFICE) == 1
    assert store.rebuild() == store.state
