"""engine/llm/budget.py: prices, per-call cost and the between-turns warning (FR-039)."""

from __future__ import annotations

from datetime import date

import pytest

from engine.llm.base import ModelCallRecord, Role
from engine.llm.budget import SpendTracker, cost, price_for


def rec(provider: str = "gemini", model_id: str = "gemini-3.8-flash", *, turn: str | None = "t1",
        cached: int = 3000, new: int = 3000, out: int = 300, thinking: int = 100, usd: float = 0.0) -> ModelCallRecord:
    return ModelCallRecord(role=Role.READER, provider=provider, model_id=model_id, schema_hash="h", turn_id=turn,
                           tokens_in_cached=cached, tokens_in=new, tokens_out=out, tokens_thinking=thinking,
                           cost_usd=usd)


def test_reader_call_matches_research_estimate() -> None:
    # research.md §4: A1 Read 3k cached / 3k new / 0.4k out ≈ 0.40¢ now, 0.80¢ from 2027-01-01
    assert cost(rec(), on=date(2026, 10, 7)) == pytest.approx(0.003975)
    assert cost(rec(), on=date(2027, 1, 1)) == pytest.approx(0.00795)
    assert cost(rec(), on=date(2026, 12, 31)) == pytest.approx(0.003975)


def test_price_switch_date() -> None:
    before = price_for("gemini-3.8-flash", date(2026, 12, 31))
    after = price_for("gemini-3.8-flash", date(2027, 1, 1))
    assert before is not None and after is not None
    assert after.input_per_m == 2 * before.input_per_m and after.output_per_m == 2 * before.output_per_m


@pytest.mark.parametrize("provider", ["offline", "scripted", "replay"])
def test_free_providers(provider: str) -> None:
    assert cost(rec(provider=provider)) == 0.0


def test_unknown_model_costs_zero() -> None:
    assert cost(rec(model_id="mystery-model")) == 0.0


def test_tracker_totals_and_warning() -> None:
    t = SpendTracker(budget_usd=0.05, game_usd=1.0)
    t.add(rec(turn="t1", usd=0.02))
    t.add(rec(turn="t1", usd=0.01))
    assert t.turn_usd("t1") == pytest.approx(0.03) and t.warning() is None and not t.over_budget()
    t.add(rec(turn="t2", usd=0.03))
    totals = t.totals()
    assert totals.turn_usd == pytest.approx(0.03) and totals.session_usd == pytest.approx(0.06)
    assert totals.game_usd == pytest.approx(1.06) and totals.budget_usd == 0.05
    assert t.over_budget() and "Keep playing?" in (t.warning() or "")
    assert not t.over_budget(budget_usd=1.0)
    t.new_session()
    assert t.session_usd == 0 and not t.over_budget() and t.game_usd == pytest.approx(1.06)


def test_no_budget_never_warns() -> None:
    t = SpendTracker(budget_usd=None)
    t.add(rec(usd=100.0))
    assert not t.over_budget() and t.warning() is None
