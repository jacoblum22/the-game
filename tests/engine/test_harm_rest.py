"""Rests and recovery (07.8; PR-07-8, PR-07-10) and the M1 handlers h.07.rest_recovery, natural_recovery,
load_clear; through the scheduler with the registered handlers."""

from __future__ import annotations

import pytest

from engine.harm.apply import apply_harm, heal
from engine.harm.ctx import Writes
from engine.harm.rest import (
    abs_watch,
    h_07_load_clear,
    h_07_natural_recovery,
    h_07_rest_recovery,
    record_rest_site,
    rest_duration,
    rest_payload,
    rest_quality,
    rest_refusal,
    rest_site,
    treat,
    vitality_gain,
)
from engine.harm.state import ACTIVE, STAGGERED, brink, harm_state, wound_load
from engine.store.events import Event, Timestamp
from engine.time import handlers as registry
from engine.time.scheduler import TimeContext, mark_boundary
from tests.engine.test_harm_support import RULES, make_game, run, vit


@pytest.mark.parametrize(("kind", "quality", "cur", "mx", "b", "s", "want"), [
    ("breather", "full", 3, 12, 0, 0, 5), ("breather", "partial", 3, 12, 1, 0, 5), ("breather", "full", 3, 12, 2, 0, 3),
    ("breather", "interrupted", 3, 12, 0, 0, 3),
    ("rest_short", "full", 1, 13, 0, 0, 8), ("rest_short", "partial", 1, 13, 0, 0, 5),
    ("rest_short", "interrupted", 1, 13, 0, 0, 3), ("rest_short", "full", 1, 13, 0, 2, 3),
    ("rest_long", "full", 1, 7, 0, 0, 7), ("rest_long", "partial", 1, 7, 0, 0, 6),
    ("rest_long", "partial", 7, 8, 0, 0, 7), ("rest_long", "interrupted", 1, 7, 0, 0, 3)])
def test_vitality_by_rest(kind, quality, cur, mx, b, s, want):  # T-07-14
    assert vitality_gain(kind, quality, cur, mx, breathers_since_short=b, short_rests_today=s) == want


def test_quality_and_allowance():  # 07.8.3-07.8.4
    assert rest_quality("rest_long", site="camp") == "full"
    assert rest_quality("rest_long", site="rough") == "partial"
    assert rest_quality("rest_long", site="camp", interruptions=1, lost_intervals=1, sleep_hours=4) == "partial"
    assert rest_quality("rest_long", site="camp", interruptions=1, lost_intervals=7, sleep_hours=4) == "interrupted"
    assert rest_quality("breather", site="haven", interruptions=1) == "interrupted"
    assert rest_quality("rest_short", site="camp", interruptions=1, lost_intervals=1) == "partial"
    with pytest.raises(ValueError):
        rest_payload("rest_long", "great", "camp")


def test_rest_recovery_restores_and_clears_load(tmp_path):
    store = make_game(tmp_path, vitality=1, vmax=12)
    run(store, apply_harm, "pc.wren", dealt=5, source="x")
    run(store, apply_harm, "pc.wren", dealt=3, source="x")
    assert harm_state(store.state, "pc.wren") == STAGGERED and wound_load(store.state, "pc.wren") == 1
    run(store, h_07_rest_recovery, boundary="rest_short", payload=rest_payload("rest_short", "full", "camp"))
    assert vit(store) == 6 and harm_state(store.state, "pc.wren") == ACTIVE and wound_load(store.state, "pc.wren") == 0


def test_long_rest_sets_rested_today_and_spacing(tmp_path):
    store = make_game(tmp_path, vitality=1, vmax=7)
    run(store, h_07_rest_recovery, boundary="rest_long", payload=rest_payload("rest_long", "full", "camp"))
    assert vit(store) == 7 and store.state.fact_value("pc.wren", "rested_today") is True
    assert rest_refusal(store.state, RULES, "pc.wren", "rest_long") == "one long rest a day"
    with store.transaction() as tx:
        now = tx.state.time.now
        tx.add(Event.of("time_advanced", {"from": now}, to=now.model_copy(update={"day": now.day + 1})))
    assert rest_refusal(store.state, RULES, "pc.wren", "rest_long") is None


def test_dying_cannot_rest(tmp_path):
    store = make_game(tmp_path)
    with store.transaction() as tx:
        w = Writes(tx.state, tx.mint)
        w.fact("pc.wren", "harm_state", "harm_state.dying", rule_id="test")
        tx.add_all(w.events)
    assert "Dying" in (rest_refusal(store.state, RULES, "pc.wren", "breather") or "")


def test_daily_pass_heals_a_brink_wound_in_four_ticks(tmp_path):
    store = make_game(tmp_path)
    with store.transaction() as tx:
        w = Writes(tx.state, tx.mint)
        w.fact("pc.wren", "brink", 1, rule_id="test")
        tx.add_all(w.events)
    for day in range(4):
        with store.transaction() as tx:
            w = Writes(tx.state, tx.mint)
            w.fact("pc.wren", "rested_today", True, rule_id="test")
            tx.add_all(w.events)
        run(store, h_07_natural_recovery, boundary="day")
        assert store.state.fact_value("pc.wren", "rested_today") is False
        assert brink(store.state, "pc.wren") == (1 if day < 3 else 0)


def test_load_clear_at_scene_end(tmp_path):
    store = make_game(tmp_path, vitality=1)
    run(store, apply_harm, "pc.wren", dealt=1, source="x")
    run(store, apply_harm, "pc.wren", dealt=3, source="x")
    assert wound_load(store.state, "pc.wren") == 1
    run(store, h_07_load_clear, boundary="scene_end")
    assert wound_load(store.state, "pc.wren") == 0


@pytest.fixture
def registered():
    """The h.05/h.07 handlers registered for one test; the registry is restored after."""
    import engine.abilities.handlers as h05
    import engine.harm.handlers as h07
    ids_ = [*h07.H07, *h05.H05]
    before = {h: registry.get(h) for h in ids_}
    h07.register_all(h07.H07)
    h07.register_all(h05.H05)
    yield
    for h, fn in before.items():
        registry.unregister(h)
        if fn is not None:
            registry.register(h, fn)


def test_rest_through_the_scheduler(tmp_path, registered):
    assert registry.get("h.07.rest_recovery") is not None and registry.get("h.05.focus_recover") is not None
    store = make_game(tmp_path, vitality=2, vmax=12, focus=6)
    with store.transaction() as tx:
        tx.add(Event.of("quantity_changed", entity="pc.wren", quantity="focus", delta=-5, new_value=1,
                        reason="test"))
    with store.transaction() as tx:
        mark_boundary(TimeContext(tx=tx, rules=RULES), "rest_long", rest_payload("rest_long", "partial", "camp"))
    assert vit(store) == 9 and store.state.quantities["pc.wren"]["focus"].current == 5  # 3/4 of 12 and of 6
    ran = [e.payload.handler_id for e in store.events(types=["handler_ran"])]  # type: ignore[attr-defined]
    assert ran.index("h.07.rest_recovery") < ran.index("h.05.focus_recover")
    assert store.rebuild() == store.state


def test_timestamp_helper():
    assert abs_watch(RULES, Timestamp(day=2, watch=1)) - abs_watch(RULES, Timestamp()) == 5


def test_rest_duration_site_and_treat(tmp_path):
    assert rest_duration(RULES, "breather") == (1, "intervals") and rest_duration(RULES, "rest_long") == (1, "watches")
    store = make_game(tmp_path, vitality=3, vmax=12, others=[("place", "Ashford inn", {}, 0)])
    assert rest_site(store.state, "loc.ashford_inn") is None
    run(store, record_rest_site, "loc.ashford_inn", "haven")
    assert rest_site(store.state, "loc.ashford_inn") == "haven"
    run(store, treat, "pc.wren", reach=1)
    assert store.state.fact_value("pc.wren", "treated_today") is True and vit(store) == 3  # Treat restores none
    for want in (5, 7, 7):  # two healings between long rests, then nothing
        run(store, heal, "pc.wren", 2, source="ab.field_surgeon")
        assert vit(store) == want
