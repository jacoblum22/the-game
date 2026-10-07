"""Replay adapter: serves recorded responses so tests and replays never call a paid model.

contracts/model-calls.md, Recording and replay: the stored response for the same (turn_id, role, seq, attempt),
after checking the schema hash, so a replay detects when engine changes alter what the model is asked. `seq` is
the role's call number within the turn (several Framer calls in one turn); rows recorded before `seq` existed
read as seq 0.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable, Mapping
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

Key = tuple[str | None, str, int, int]
_SECTION = re.compile(r"(?m)^\[([A-Z][A-Z ]+)\]$")


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def packet_digest(rendered: str) -> dict[str, Any]:
    """What a recorded game keeps of a packet instead of its text: the sha256 of the whole rendered packet, its
    length, and a short hash per `[SECTION]` (so a divergence names the section that changed)."""
    parts = _SECTION.split(rendered)
    sections = {parts[i]: _sha(parts[i + 1])[:16] for i in range(1, len(parts) - 1, 2)}
    return {"packet_sha256": _sha(rendered), "packet_chars": len(rendered), "packet_sections": sections}


def _recorded_digest(request: Mapping[str, Any]) -> dict[str, Any] | None:
    if request.get("packet_sha256"):
        return dict(request)
    if isinstance(request.get("packet"), str):
        return packet_digest(request["packet"])
    return None


def record_from_row(row: Mapping[str, Any]) -> ModelCallRecord:
    """A `Store.model_calls()` row back to a record (fields the table has no column for, e.g. `seq`, are in
    `extra`)."""
    d = {k: v for k, v in row.items() if k not in ("row_id", "extra")}
    extra = row.get("extra") or {}
    d.update({k: v for k, v in extra.items() if k in ModelCallRecord.model_fields})
    d = {k: v for k, v in d.items() if v is not None or k in ("turn_id", "response")}
    return ModelCallRecord.model_validate(d)


class ReplayModel:
    """`StructuredModel` over recorded `ModelCallRecord`s (the `model_calls` rows of a game). With
    `check_packets`, a call whose rendered packet differs from the recorded one (its text, or its `packet_digest`)
    is a divergence too: the engine now asks the model something else."""

    provider = "replay"

    def __init__(self, records: Iterable[ModelCallRecord], *, check_packets: bool = False):
        self.check_packets = check_packets
        self.records: dict[Key, ModelCallRecord] = {}
        for rec in records:
            # A turn retried after an error records the same key again; the latest row wins.
            self.records[(rec.turn_id, Role(rec.role).value, rec.seq or 0, rec.attempt)] = rec

    @classmethod
    def from_rows(cls, rows: Iterable[Mapping[str, Any]], *, check_packets: bool = False) -> ReplayModel:
        """From `store.model_calls()` rows."""
        return cls((record_from_row(r) for r in rows), check_packets=check_packets)

    def fill(
        self, role: Role, schema: dict[str, Any], packet: Packet, *, turn_id: str | None, attempt: int,
        seq: int = 0,
    ) -> CallResult:
        where = f"turn={turn_id} role={role.value} seq={seq} attempt={attempt}"
        rec = self.records.get((turn_id, role.value, seq, attempt))
        if rec is None:
            raise ReplayDivergence(f"no recorded call for {where}")
        wanted = schema_hash(schema)
        if rec.schema_hash != wanted:
            raise ReplayDivergence(
                f"schema changed for {where}: recorded {rec.schema_hash[:12]}, now {wanted[:12]}"
            )
        if self.check_packets:
            self._check_packet(where, rec, packet)
        out = rec.model_copy(update={"provider": self.provider, "cost_usd": 0.0})
        response = rec.response or {}
        if rec.outcome == Outcome.REFUSED:
            raise ModelRefused(f"{role.value}: recorded refusal ({response.get('error')})", out)
        if response.get("data") is None and response.get("text") is None and response.get("error"):
            raise ModelUnavailable(f"{role.value}: recorded error ({response.get('error')})", out)
        return CallResult(data=response.get("data"), record=out)

    @staticmethod
    def _check_packet(where: str, rec: ModelCallRecord, packet: Packet) -> None:
        want = _recorded_digest(rec.request or {})
        if want is None:
            return
        now = packet_digest(packet.render())
        if now["packet_sha256"] == want["packet_sha256"]:
            return
        old, new = want.get("packet_sections") or {}, now["packet_sections"]
        changed = sorted(k for k in {*old, *new} if old.get(k) != new.get(k)) or ["(layout)"]
        raise ReplayDivergence(f"packet changed for {where}: sections {', '.join(changed)} "
                               f"({want.get('packet_chars')} -> {now['packet_chars']} chars)")


# Name used in research.md R3.
ReplayAdapter = ReplayModel
