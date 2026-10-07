"""engine/time/scheduler.py and the handler registry: PR-00-2, 00.7.5-00.7.8, FR-026."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

from engine.data.loader import Rules, load_rules
from engine.store.clocks import create_clock
from engine.store.conditions import apply_condition
from engine.store.db import Store
from engine.store.events import Event, Timestamp
from engine.time import clock
from engine.time import handlers as reg
from engine.time.handlers import HandlerResult
from engine.time.scheduler import (
    EVENT_ORDER,
    Mark,
    SchedulerError,
    TimeContext,
    advance_time,
    mark_boundary,
    order_instant,
    plan,
    set_mode,
)
from tests.fixtures.game import entity, new_store


@pytest.fixture(scope="module")
def rules() -> Rules:
    return load_rules()


@pytest.fixture
def store(tmp_path: Path) -> Store:
    return new_store(tmp_path)


@pytest.fixture
def temp_handlers() -> Iterator[list[str]]:
    """Handler ids registered by a test; unregistered afterwards."""
    added: list[str] = []
    yield added
    for h in added:
        reg.unregister(h)


def _set_time(store: Store, ts: Timestamp) -> None:
    with store.transaction() as tx:
        tx.add(Event.of("time_advanced", {"from": tx.state.time.now}, to=ts))


def _marked(store: Store, since: int = 0) -> list[tuple[int, str]]:
    return [(clock.to_rounds(e.game_time), e.payload.boundary)  # type: ignore[arg-type, attr-defined]
            for e in store.events(since, types=["boundary_marked"])]


# ------------------------------------------------------------------------------------------- registry


def test_registry_matches_boundaries_yaml(rules: Rules) -> None:
    assert reg.check_registry(rules) == []
    assert len(reg.MILESTONE_OF) == len(rules.boundary_handlers()) == 105
    assert len(reg.live_handlers(1)) == 34
    assert reg.live_handlers(7) == frozenset(reg.MILESTONE_OF)
    assert reg.implemented() <= reg.live_handlers(1)
    assert {"h.00.durations", "h.00.clock_auto", "h.00.reflection"} <= reg.implemented()
    owners = Counter(h.split(".")[1] for h in reg.MILESTONE_OF)
    for o in owners:  # each owner stub lists exactly its yaml block
        mod = getattr(reg, f"h{o}")
        assert set(mod.HANDLERS) == {h for h in reg.MILESTONE_OF if h.startswith(f"h.{o}.")}
    with pytest.raises(KeyError):
        reg.register("h.99.nope", lambda ctx: None)
    with pytest.raises(ValueError):
        reg.register("h.00.durations", lambda ctx: None)


def test_phase_order_and_before(rules: Rules) -> None:
    for b in ["rest_long", "scene_end", "interval", "day", "week", "season"]:
        rows = plan(rules, b)
        assert [int(r["phase"]) for r in rows] == sorted(int(r["phase"]) for r in rows)
    ids = [r["id"] for r in plan(rules, "rest_short")]
    assert ids.index("h.07.rest_recovery") < ids.index("h.05.focus_recover") < ids.index("h.05.rest_recharge")
    ivl = [r["id"] for r in plan(rules, "interval")]
    assert ivl.index("h.07.affliction_onset") < ivl.index("h.10.site_exposure")  # I-023
    assert ivl[:2] == ["h.00.durations", "h.08.durations"]  # wildcards run at every boundary


def test_order_instant_00_7_6() -> None:
    got = order_instant(["year", "day", "reflection", "interval", "venture_end", "rest_long", "scene_end",
                         "conflict_end", "watch"])
    assert got == ["conflict_end", "scene_end", "rest_long", "reflection", "venture_end", "interval", "watch",
                   "day", "year"]
    assert EVENT_ORDER.index("breather") < EVENT_ORDER.index("rest_short") < EVENT_ORDER.index("rest_long")


# ------------------------------------------------------------------------------------------- advancing


def test_simultaneous_boundaries_run_in_order(store: Store, rules: Rules) -> None:
    _set_time(store, Timestamp(week=1, day=7, watch=3))  # start of the night watch, last day of the week
    seq0 = store.last_seq
    with store.transaction() as tx:
        res = advance_time(TimeContext(tx, rules), 1, "watch", "sleep",
                           marks=[Mark("rest_long", {"quality": "full", "site": "haven", "treated": False})])
    dawn = clock.to_rounds(Timestamp(week=2, day=1))
    last = [b for r, b in _marked(store, seq0) if r == dawn]
    assert last == ["rest_long", "reflection", "interval", "hour", "watch", "day", "week"]
    assert store.state.time.now == Timestamp(week=2, day=1)
    assert res.interrupt is None and res.remainder_rounds == 0
    # each boundary runs all nine phases before the next begins
    evs = list(store.events(seq0, types=["boundary_marked", "handler_ran", "handler_skipped"]))
    cur, phases = "", []
    for e in evs:
        if e.type == "boundary_marked":
            assert phases == sorted(phases)
            cur, phases = e.payload.boundary, []  # type: ignore[attr-defined]
        else:
            assert e.payload.boundary == cur  # type: ignore[attr-defined]
            phases.append(e.payload.phase)  # type: ignore[attr-defined]
    assert store.rebuild() == store.state


def test_long_skip_fires_every_boundary_once_in_order(store: Store, rules: Rules) -> None:
    _set_time(store, Timestamp(week=1, day=3, watch=1, hour=2, interval=4, round=17))
    start = clock.to_rounds(store.state.time.now)
    seq0 = store.last_seq
    with store.transaction() as tx:
        res = advance_time(TimeContext(tx, rules), 3, "week", "downtime")
    end = start + 3 * clock.ROUNDS["week"]
    marked = _marked(store, seq0)
    assert len(marked) == len(set(marked))  # exactly once
    for unit in clock.TIME_UNITS[1:]:
        n = clock.ROUNDS[unit]
        expect = [r for r in range((start // n + 1) * n, end + 1, n)]
        assert [r for r, b in marked if b == unit] == expect
    assert Counter(b for _, b in marked) == {"interval": 3024, "hour": 504, "watch": 84, "day": 21, "week": 3}
    assert [r for r, _ in marked] == sorted(r for r, _ in marked)  # chronological
    assert "round" not in {b for _, b in marked}  # rounds are conflict-only
    assert store.state.time.now == clock.from_rounds(end)
    assert len(res.boundaries) == len(marked)
    steps = list(store.events(seq0, types=["time_advanced"]))
    assert steps[-1].payload.to == clock.from_rounds(end)  # type: ignore[attr-defined]


def test_every_registry_id_is_run_or_skipped(store: Store, rules: Rules) -> None:
    year = clock.ROUNDS["year"]
    _set_time(store, clock.from_rounds(year - 1))
    seq0 = store.last_seq
    with store.transaction() as tx:
        ctx = TimeContext(tx, rules)
        set_mode(ctx, "conflict", "a fight")
        advance_time(ctx, 1, "round", "round end")  # crosses round .. year at one instant
        for b in rules.boundaries["boundaries"]["event"]:
            if b not in ("reflection", "mode_change"):  # both fired above / below via their causes
                mark_boundary(ctx, b, {})
        mark_boundary(ctx, "reflection")
    logged = list(store.events(seq0, types=["handler_ran", "handler_skipped"]))
    seen = {e.payload.handler_id for e in logged}  # type: ignore[attr-defined]
    assert seen == set(reg.MILESTONE_OF)
    # per boundary: exactly the plan, once each
    by_b: dict[str, list[str]] = {}
    marks = Counter(b for _, b in _marked(store, seq0))
    for e in logged:
        by_b.setdefault(e.payload.boundary, []).append(e.payload.handler_id)  # type: ignore[attr-defined]
    for b, hs in by_b.items():
        assert hs == [r["id"] for r in plan(rules, b)] * marks[b], b
    for e in logged:
        if e.type == "handler_skipped":
            p: Any = e.payload
            assert p.reason == "not yet built"
            assert p.milestone == reg.milestone_of(p.handler_id)
            assert p.handler_id not in reg.implemented() or p.milestone > 1


def test_milestone_gating(store: Store, rules: Rules, temp_handlers: list[str]) -> None:
    calls: list[str] = []
    reg.register("h.07.dying_check", lambda ctx: calls.append(ctx.boundary) or HandlerResult(summary="ok"))
    temp_handlers.append("h.07.dying_check")
    with store.transaction() as tx:
        mark_boundary(TimeContext(tx, rules), "turn_end")  # milestone 1: M2 handler is skipped
        res = mark_boundary(TimeContext(tx, rules, milestone=2), "turn_end")
    assert calls == ["turn_end"]
    skipped = [e.payload for e in store.events(types=["handler_skipped"])]
    dc = [p for p in skipped if p.handler_id == "h.07.dying_check"]  # type: ignore[attr-defined]
    assert len(dc) == 1 and dc[0].milestone == 2  # type: ignore[attr-defined]
    assert [o for o in res[0].handlers if o.handler_id == "h.07.dying_check"][0].ran
    # live at M1 but not built: logged with milestone 1
    with store.transaction() as tx:
        out = mark_boundary(TimeContext(tx, rules), "rest_short")
    rr = [o for o in out[0].handlers if o.handler_id == "h.07.rest_recovery"][0]
    assert not rr.ran and rr.milestone == 1 and rr.summary == "not yet built"


# ------------------------------------------------------------------------------------------- interrupts


def _clock(tx: Any, name: str, boundary: str, segments: int = 4, *, interrupting: bool = True,
           start: int = 0) -> str:
    tpl = {"kind": "danger", "segments": segments, "auto_ticks": [{"boundary": boundary, "ticks": 1}],
           "on_complete": {"interrupting": interrupting, "effects": [{"op": "frame_scene"}]}}
    ev = create_clock(tx.state, tpl, name=name, owner="00", filled=start)
    tx.add(ev)
    return ev.payload.clock.id  # type: ignore[attr-defined]


def test_interrupt_halts_and_returns_remainder(store: Store, rules: Rules) -> None:
    with store.transaction() as tx:
        cid = _clock(tx, "The hunt closes in", "watch", start=2)
    seq0 = store.last_seq
    with store.transaction() as tx:
        res = advance_time(TimeContext(tx, rules), 5, "watch", "travel",
                           marks=[Mark("rest_long", {"quality": "full"}, after=4 * clock.ROUNDS["watch"])])
    assert res.interrupt == ("h.00.clock_auto", f"{cid} completed")
    assert res.end == Timestamp(watch=2) == store.state.time.now == res.halted_at
    assert res.remainder_rounds == 3 * clock.ROUNDS["watch"] and res.remainder == {"watch": 3}
    assert [m.boundary for m in res.unfired] == ["rest_long"]
    assert res.boundaries[-1].effects == [{"op": "frame_scene"}]
    # the interrupting boundary finished its later phases; nothing after the instant ran
    halt = clock.to_rounds(res.end)
    assert max(r for r, _ in _marked(store, seq0)) == halt
    watch_logs = [e.payload.phase for e in store.events(seq0, types=["handler_ran", "handler_skipped"])  # type: ignore[attr-defined]
                  if e.game_time == res.end and e.payload.boundary == "watch"]  # type: ignore[attr-defined]
    assert max(watch_logs) == 7  # h.10.watch_check (7) after h.00.clock_auto (5)
    last = list(store.events(seq0, types=["time_advanced"]))[-1].payload
    assert last.interrupt and last.remainder == {"watch": 3}  # type: ignore[attr-defined]
    # the remainder is not spent: resuming reaches the original target
    with store.transaction() as tx:
        again = advance_time(TimeContext(tx, rules), res.remainder_rounds, "round", "resume")
    assert again.end == res.target == store.state.time.now
    assert store.rebuild() == store.state


def test_interrupt_from_non_interrupting_handler_is_an_error(store: Store, rules: Rules,
                                                             temp_handlers: list[str]) -> None:
    reg.register("h.07.career_end", lambda ctx: HandlerResult(interrupt="boom"))
    temp_handlers.append("h.07.career_end")
    before = store.last_seq
    with pytest.raises(SchedulerError):
        with store.transaction() as tx:
            mark_boundary(TimeContext(tx, rules), "scene_end")
    assert store.last_seq == before  # rolled back, nothing written


def test_interrupting_handler_registered_by_owner(store: Store, rules: Rules, temp_handlers: list[str]) -> None:
    n = {"calls": 0}

    def watch_check(ctx: TimeContext) -> HandlerResult:
        n["calls"] += 1
        return HandlerResult(interrupt="encounter", narration=["a shape on the verge"]) if n["calls"] == 2 \
            else HandlerResult()
    reg.register("h.10.watch_check", watch_check)
    temp_handlers.append("h.10.watch_check")
    with store.transaction() as tx:
        res = advance_time(TimeContext(tx, rules, milestone=4), 5, "watch", "travel")
    assert res.interrupt == ("h.10.watch_check", "encounter")
    assert res.remainder == {"watch": 3} and res.narration == ["a shape on the verge"]


# ------------------------------------------------------------------------------------------- built handlers


def test_durations_expire(store: Store, rules: Rules) -> None:
    with store.transaction() as tx:
        tx.add(entity("pc", "Wren", tx=tx))
        a = apply_condition(tx.state, tx.mint, rules, "pc.wren", "cond.deafened", duration="hours:2")
        tx.add_all(a.events)
        b = apply_condition(tx.state, tx.mint, rules, "pc.wren", "cond.cursed", duration="rounds:3")
        tx.add_all(b.events)
        c = apply_condition(tx.state, tx.mint, rules, "pc.wren", "cond.charmed")  # scene
        tx.add_all(c.events)
        d = apply_condition(tx.state, tx.mint, rules, "pc.wren", "cond.exhausted", duration="until_rest:rest_short")
        tx.add_all(d.events)
    ids = {r.instance_id for r in (a, b, c, d)}
    assert len(ids) == 4 and set(store.state.conditions) == ids
    with store.transaction() as tx:
        res = advance_time(TimeContext(tx, rules), 1, "interval", "search")
    assert b.instance_id not in store.state.conditions  # rounds:3 ends at the first interval boundary
    assert any("cond.cursed ends" in n for n in res.narration)
    with store.transaction() as tx:
        advance_time(TimeContext(tx, rules), 5, "interval", "search")
    assert a.instance_id in store.state.conditions  # 1 hour elapsed of 2
    with store.transaction() as tx:
        ctx = TimeContext(tx, rules)
        advance_time(ctx, 1, "hour", "search")
        assert a.instance_id not in tx.state.conditions
        mark_boundary(ctx, "scene_end")
        assert c.instance_id not in tx.state.conditions
        mark_boundary(ctx, "breather")
        assert d.instance_id in tx.state.conditions  # a breather is shorter than the rest named
        mark_boundary(ctx, "rest_long")
        assert d.instance_id not in tx.state.conditions
    removed = list(store.events(types=["condition_removed"]))
    assert removed[0].game_time == Timestamp(interval=1) and removed[0].source == "h.00.durations"
    assert store.rebuild() == store.state


def test_clock_auto_ticks_and_decays(store: Store, rules: Rules) -> None:
    with store.transaction() as tx:
        cid = _clock(tx, "The tide rises", "hour", segments=8, interrupting=False)
        tpl = {"kind": "danger", "segments": 6, "decay": [{"boundary": "day", "ticks": -1}], "direction": "tug"}
        ev = create_clock(tx.state, tpl, name="Rumour fades", owner="00", filled=3)
        tx.add(ev)
        tug = ev.payload.clock.id  # type: ignore[attr-defined]
    with store.transaction() as tx:
        advance_time(TimeContext(tx, rules), 1, "day", "wait")
    assert store.state.clocks[cid].filled == 8 and store.state.clocks[cid].status == "completed"
    assert store.state.clocks[tug].filled == 2
    ran = [e.payload.result for e in store.events(types=["handler_ran"])  # type: ignore[attr-defined]
           if e.payload.handler_id == "h.00.clock_auto" and e.payload.result]  # type: ignore[attr-defined]
    assert len(ran) == 9  # 8 hourly ticks + 1 decay; no tick once completed
    assert store.rebuild() == store.state


def test_reflection_at_most_once_per_day(store: Store, rules: Rules) -> None:
    with store.transaction() as tx:
        ctx = TimeContext(tx, rules)
        first = mark_boundary(ctx, "rest_long", {"quality": "full"})
        second = mark_boundary(ctx, "rest_long", {"quality": "full"})
    assert [b.boundary for b in first] == ["rest_long", "reflection"]
    assert [b.boundary for b in second] == ["rest_long"]
    # a season boundary on a later day fires it again
    _set_time(store, clock.from_rounds(clock.ROUNDS["season"] - 100))
    with store.transaction() as tx:
        res = advance_time(TimeContext(tx, rules), 1, "interval", "wait")
    names = [b.boundary for b in res.boundaries]
    assert names == ["interval", "hour", "watch", "day", "week", "season", "reflection"]  # derived: after its cause


def test_mark_boundary_beat_counter_and_mode(store: Store, rules: Rules) -> None:
    with store.transaction() as tx:
        ctx = TimeContext(tx, rules)
        mark_boundary(ctx, "beat_end")
        mark_boundary(ctx, "beat_end")
        assert set_mode(ctx, "site", "entered the barrow")[0].boundary == "mode_change"
        assert set_mode(ctx, "site", "again") == []
        with pytest.raises(SchedulerError):
            mark_boundary(ctx, "day")  # time boundaries come only from advance_time
        with pytest.raises(SchedulerError):
            set_mode(ctx, "scene", "x")
    assert store.state.time.now.beat == 2 and store.state.time.mode == "site"
    assert clock.to_rounds(store.state.time.now) == 0  # event boundaries never move fictional time
    assert store.state.time.last_boundary["mode_change"] > store.state.time.last_boundary["beat_end"]
