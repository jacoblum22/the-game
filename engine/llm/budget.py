"""Model prices, per-call cost and the spending totals behind the between-turns budget warning.

research.md §4 and its sources list. Prices are USD per million tokens. A budget is a warning threshold,
never a limit (FR-039): nothing here raises or interrupts a turn.
"""

from __future__ import annotations

import logging
from datetime import UTC, date, datetime

from pydantic import BaseModel

from engine.llm.base import ModelCallRecord

log = logging.getLogger(__name__)


class Price(BaseModel):
    effective_from: date
    input_per_m: float
    cached_per_m: float
    output_per_m: float  # thinking tokens are billed at this rate too


# Newest entry whose effective_from ≤ the call date applies.
PRICES: dict[str, list[Price]] = {
    # Third-party trackers, 2026-10-07 (research.md sources): promo until 2026-12-31, doubles 2027-01-01.
    "gemini-3.8-flash": [
        Price(effective_from=date(2000, 1, 1), input_per_m=0.75, cached_per_m=0.075, output_per_m=3.75),
        Price(effective_from=date(2027, 1, 1), input_per_m=1.50, cached_per_m=0.15, output_per_m=7.50),
    ],
    # Fallbacks named in research.md R2 (cached rate assumed at 10% of input for Claude; not yet used).
    "claude-haiku-4-5": [Price(effective_from=date(2000, 1, 1), input_per_m=1.0, cached_per_m=0.1, output_per_m=5.0)],
    "claude-sonnet-5-5": [
        Price(effective_from=date(2000, 1, 1), input_per_m=2.0, cached_per_m=0.2, output_per_m=10.0)
    ],
    "gpt-oss-120b": [Price(effective_from=date(2000, 1, 1), input_per_m=0.15, cached_per_m=0.15, output_per_m=0.60)],
}

FREE_PROVIDERS = frozenset({"offline", "scripted", "replay"})


def price_for(model_id: str, on: date | None = None) -> Price | None:
    entries = PRICES.get(model_id)
    if not entries:
        return None
    day = on or datetime.now(UTC).date()
    current = [p for p in entries if p.effective_from <= day]
    return max(current, key=lambda p: p.effective_from) if current else entries[0]


def cost(record: ModelCallRecord, on: date | None = None) -> float:
    """USD for one call; 0 for offline, scripted and replayed calls and for unknown model ids (logged)."""
    if record.provider in FREE_PROVIDERS:
        return 0.0
    price = price_for(record.model_id, on)
    if price is None:
        log.warning("no price for model %r; cost recorded as 0", record.model_id)
        return 0.0
    usd = (
        record.tokens_in * price.input_per_m
        + record.tokens_in_cached * price.cached_per_m
        + (record.tokens_out + record.tokens_thinking) * price.output_per_m
    ) / 1_000_000
    return round(usd, 8)


class SpendTotals(BaseModel):
    """The shape of `game.spend()` (contracts/engine-api.md)."""

    turn_usd: float
    session_usd: float
    game_usd: float
    budget_usd: float | None


class SpendTracker:
    """Running totals per turn, session and game. `game_usd` seeds the total of an opened game."""

    def __init__(self, budget_usd: float | None = 2.00, *, game_usd: float = 0.0):
        self.budget_usd = budget_usd
        self.game_usd = game_usd
        self.session_usd = 0.0
        self.by_turn: dict[str | None, float] = {}
        self.last_turn: str | None = None

    def add(self, record: ModelCallRecord) -> None:
        usd = record.cost_usd
        self.by_turn[record.turn_id] = self.by_turn.get(record.turn_id, 0.0) + usd
        self.session_usd += usd
        self.game_usd += usd
        if record.turn_id is not None:
            self.last_turn = record.turn_id

    def turn_usd(self, turn_id: str | None = None) -> float:
        return self.by_turn.get(turn_id if turn_id is not None else self.last_turn, 0.0)

    def new_session(self) -> None:
        self.session_usd = 0.0

    def totals(self, turn_id: str | None = None) -> SpendTotals:
        return SpendTotals(
            turn_usd=round(self.turn_usd(turn_id), 6), session_usd=round(self.session_usd, 6),
            game_usd=round(self.game_usd, 6), budget_usd=self.budget_usd,
        )

    def over_budget(self, budget_usd: float | None = None) -> bool:
        # rule: FR-039 (a warning threshold, checked between turns; never a limit)
        limit = budget_usd if budget_usd is not None else self.budget_usd
        return limit is not None and self.session_usd >= limit

    def warning(self, budget_usd: float | None = None) -> str | None:
        """The between-turns notice text once spending passes the budget, else None."""
        if not self.over_budget(budget_usd):
            return None
        limit = budget_usd if budget_usd is not None else self.budget_usd
        return (
            f"This session has spent about ${self.session_usd:.2f} on model calls, past your "
            f"${limit:.2f} budget. Keep playing?"
        )
