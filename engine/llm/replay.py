"""Replay adapter: serves recorded responses so tests and replays never call a paid model.

contracts/model-calls.md, Recording and replay: the stored response for the same (turn_id, role, attempt),
after checking the schema hash, so a replay detects when engine changes alter what the model is asked.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from engine.llm.base import (
    CallResult,
    ModelCallRecord,
    ModelRefused,
    ModelUnavailable,
    Outcome,
    Packet,
    ReplayDivergence,
    Role,
    schema_hash,
)

Key = tuple[str | None, str, int]


class ReplayModel:
    """`StructuredModel` over recorded `ModelCallRecord`s (the `model_calls` rows of a game)."""

    provider = "replay"

    def __init__(self, records: Iterable[ModelCallRecord]):
        self.records: dict[Key, ModelCallRecord] = {}
        for rec in records:
            # A turn retried after an error records the same key again; the latest row wins.
            self.records[(rec.turn_id, Role(rec.role).value, rec.attempt)] = rec

    def fill(
        self, role: Role, schema: dict[str, Any], packet: Packet, *, turn_id: str | None, attempt: int
    ) -> CallResult:
        key = (turn_id, role.value, attempt)
        rec = self.records.get(key)
        if rec is None:
            raise ReplayDivergence(f"no recorded call for turn={turn_id} role={role.value} attempt={attempt}")
        wanted = schema_hash(schema)
        if rec.schema_hash != wanted:
            raise ReplayDivergence(
                f"schema changed for turn={turn_id} role={role.value} attempt={attempt}: "
                f"recorded {rec.schema_hash[:12]}, now {wanted[:12]}"
            )
        out = rec.model_copy(update={"provider": self.provider, "cost_usd": 0.0})
        response = rec.response or {}
        if rec.outcome == Outcome.REFUSED:
            raise ModelRefused(f"{role.value}: recorded refusal ({response.get('error')})", out)
        if response.get("data") is None and response.get("text") is None and response.get("error"):
            raise ModelUnavailable(f"{role.value}: recorded error ({response.get('error')})", out)
        return CallResult(data=response.get("data"), record=out)


# Name used in research.md R3.
ReplayAdapter = ReplayModel
