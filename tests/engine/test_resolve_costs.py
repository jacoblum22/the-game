"""engine/resolve/costs.py: T-01-5 severities, cost declarations, applying the one due cost (PR-01-3 step 4)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import pytest

from engine.resolve.costs import apply_cost, cost_severity, severity_previews
from engine.resolve.frame import frame_check
from engine.resolve.roll import read_result
from engine.resolve.types import Frame, ProposedFrame, RollResult
from engine.store.events import ClockRecord, Event
from tests.engine.test_resolve_scene import Scene


@pytest.mark.parametrize(("stakes", "deg", "sac", "want"), [
    ("safe", "failure", False, None), ("safe", "failure", True, "S1"), ("safe", "critical_failure", False, "S1"),
    ("risky", "failure", False, "S2"), ("risky", "failure", True, "S2"), ("risky", "critical_failure", False, "S3"),
    ("dire", "failure", False, "S3"), ("dire", "failure", True, "S3"), ("dire", "critical_failure", False, "S4"),
    ("dire", "success", False, None), ("dire", "critical_success", False, None),
])
def test_t_01_5(stakes: str, deg: str, sac: bool, want: str | None) -> None:
    assert cost_severity(stakes, deg, success_at_cost=sac) == want  # type: ignore[arg-type]


def test_previews() -> None:
    assert severity_previews("risky") == {"on_failure": "S2", "on_critical_failure": "S3", "on_success_at_cost": "S2"}


def _frame(s: Scene, **kw: object) -> Frame:
    p = {"anchor": "anc.01_18_4", "attribute": "agility", "obstacle": {"kind": "tier", "tier": "moderate"},
         "stakes_source": "consumed_resource", "threatened_cost": {"menu_id": "cost.drain"},  # 01.6.11
         "alternate_cost": {"menu_id": "cost.shortfall"}, **kw}
    f = frame_check(ProposedFrame(**p), s.beat(gate="G1", verb="verb.move"), state=s.state, rules=s.rules)
    assert isinstance(f, Frame), f
    f.id = "frame.1"
    return f


def _roll(d20: int, deg: str, near: bool) -> RollResult:
    return RollResult(frame_id="frame.1", d20=d20, total=0, margin=-1 if near else -5, base_degree=deg,  # type: ignore[arg-type]
                      degree=deg, near_miss=near)  # type: ignore[arg-type]


def test_drain_lands_in_full_or_refuses(tmp_path: Path) -> None:
    s = Scene.new(tmp_path)
    f = _frame(s)
    rd = read_result(f, _roll(5, "critical_failure", False))  # risky crit fail: S3 = 2 units
    with s.store.transaction() as tx:
        app = apply_cost(f, rd, "cost.drain", state=tx.state, rules=s.rules, mint=tx.mint)
        tx.add_all(app.events)
    assert app.refused is None and s.state.quantities[s.pc]["focus"].current == 2
    with s.store.transaction() as tx:
        tx.add_all(apply_cost(f, rd, "cost.drain", state=tx.state, rules=s.rules, mint=tx.mint).events)
    again = apply_cost(f, rd, "cost.drain", state=s.state, rules=s.rules, mint=lambda p: p)
    assert again.refused is not None and "in full" in again.refused


def test_only_the_declared_entries(tmp_path: Path) -> None:
    s = Scene.new(tmp_path)
    f = _frame(s)
    fail = read_result(f, _roll(8, "failure", True), take_success_at_cost=False)
    assert fail.cost_choices == ["cost.drain"]
    assert apply_cost(f, fail, "cost.shortfall", state=s.state, rules=s.rules, mint=lambda p: p).refused
    sac = read_result(f, _roll(8, "failure", True), take_success_at_cost=True)
    short = apply_cost(f, sac, "cost.shortfall", state=s.state, rules=s.rules, mint=lambda p: p)
    assert (short.refused, short.reach_delta, short.events) == (None, -1, [])
    ok = read_result(f, _roll(15, "success", False))
    assert apply_cost(f, ok, "cost.drain", state=s.state, rules=s.rules, mint=lambda p: p).refused == "no cost is due"


def test_harm_goes_through_the_hook(tmp_path: Path) -> None:
    s = Scene.new(tmp_path)
    s.fact("world", "barn.fire", True)
    f = _frame(s, stakes_source="hazard", threatened_cost={"menu_id": "cost.harm"})
    rd = read_result(f, _roll(3, "failure", False))
    assert apply_cost(f, rd, "cost.harm", state=s.state, rules=s.rules, mint=lambda p: p).refused
    got: list[object] = []

    def hook(target: str, severity: str, *, lethal: bool, harm_tags: list[str], frame_id: str | None) -> list[Event]:
        got.append((target, severity, lethal, harm_tags, frame_id))
        return []

    app = apply_cost(f, rd, "cost.harm", state=s.state, rules=s.rules, mint=lambda p: p, harm_hook=hook,
                     params={"harm_tags": ["harm.fire.flame"]})
    assert app.refused is None and got == [(s.pc, "S2", False, ["harm.fire.flame"], "frame.1")]


def test_exposure_and_time(tmp_path: Path) -> None:
    s = Scene.new(tmp_path)
    guard = s.add("npc", "Guard")
    s.apply([Event.of("clock_created", source="test", clock=ClockRecord(
        id="clk.alarm", name="alarm", kind="danger", segments=6,
        tick_sources=[{"on": "cost.exposure", "ticks": "U(severity)"}, {"on": "cost.time", "ticks": "U(severity)"}]))])
    f = _frame(s, stakes_source="listening_clock", threatened_cost={"menu_id": "cost.exposure"},
               alternate_cost={"menu_id": "cost.time"})
    rd = read_result(f, _roll(2, "critical_failure", False))  # S3
    with s.store.transaction() as tx:
        app = apply_cost(f, rd, "cost.exposure", state=tx.state, rules=s.rules, mint=tx.mint,
                         params={"observer": guard})
        tx.add_all(app.events)
    assert s.state.fact_value(guard, "alertness") == "alarmed" and s.state.clocks["clk.alarm"].filled == 2
    sac = read_result(f, _roll(9, "failure", True), take_success_at_cost=True)
    with s.store.transaction() as tx:
        tx.add_all(apply_cost(f, sac, "cost.time", state=tx.state, rules=s.rules, mint=tx.mint).events)
    assert s.state.clocks["clk.alarm"].filled == 3
    s2 = Scene.new(tmp_path / "b")
    f2 = _frame(s2, stakes_source="none", threatened_cost={"menu_id": "cost.time", "source_fact": s2.fact(
        "world", "night", "young")}, alternate_cost=None)
    rd2 = read_result(f2, _roll(1, "critical_failure", False))
    t = apply_cost(f2, rd2, "cost.time", state=s2.state, rules=s2.rules, mint=lambda p: p, mode="free")
    assert t.deferred == {"advance_time": {"intervals": 1}, "mode": "free"}


@pytest.mark.parametrize("sev", ["S1", "S2", "S3", "S4", "S5"])
@pytest.mark.parametrize("foe", [True, False])
@pytest.mark.parametrize("form", [None, "cond.grabbed", "cond.restrained", "cond.pinned", "cond.prone",
                                  "cond.off_balance", "cond.slowed"])
def test_footing_hold_needs_a_holder(tmp_path: Path, sev: str, foe: bool, form: str | None) -> None:
    """[verification: pinned-trace] a footing hold is held by the opponent; with none, the row's non-hold form."""
    s = Scene.new(tmp_path)
    npc = s.npc("Brute") if foe else None
    f = _frame(s)
    f.beat.target = npc
    rd = read_result(f, _roll(5, "failure", False)).model_copy(update={"cost_severity": sev,
                                                                       "cost_choices": ["cost.footing"]})
    app = apply_cost(f, rd, "cost.footing", state=s.state, rules=s.rules, mint=lambda p: p, form=form)
    for e in (e for e in app.events if e.type == "condition_applied"):
        inst = cast(Any, e.payload).instance
        hold = s.rules.condition(inst.condition_id).get("exclusion_group") == "hold"
        assert inst.source.get("entity") == (npc if hold else s.pc), (sev, form, inst.source)
    if app.deferred and "footing" in app.deferred and not foe:
        assert "cond.grabbed" not in app.deferred["footing"] and "opponent" not in app.deferred["footing"]


def test_footing_pinned_by_the_foe(tmp_path: Path) -> None:
    s = Scene.new(tmp_path)
    npc = s.npc("Brute")
    f = _frame(s)
    f.beat.target = npc
    rd = read_result(f, _roll(5, "failure", False)).model_copy(update={"cost_severity": "S4",
                                                                       "cost_choices": ["cost.footing"]})
    app = apply_cost(f, rd, "cost.footing", state=s.state, rules=s.rules, mint=lambda p: p)
    assert [cast(Any, e.payload).instance.source["entity"] for e in app.events] == [npc]
    f.beat.target = None
    app = apply_cost(f, rd, "cost.footing", state=s.state, rules=s.rules, mint=lambda p: p)
    assert not app.events and app.deferred == {"footing": "move to next lower/worse place", "severity": "S4"}
