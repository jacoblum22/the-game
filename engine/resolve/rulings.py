"""The ruling ledger (00.15.5) and the precedent rule (00.15.6; FR-022).

    sig = signature("anc.01_18_11", ["dc:tier_rederived", "stakes"])      # 'anc.01_18_11+dc:tier_rederived+stakes'
    found = find_rulings(store, sig, staged=tx.events)                     # before adapting, Oracle, G3/G4
    ev = log_ruling(RulingRecord(...), mint=tx.mint)                       # -> ruling_logged; tx.add(ev)

`find_rulings` reads the committed `rulings_idx` and, inside a transaction, the staged `ruling_logged` events
(the index is written at commit).
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from typing import Any, Literal

from pydantic import BaseModel, Field

from engine import ids
from engine.store.events import Event

RulingKind = Literal["adaptation", "oracle", "good_idea", "g4", "g3_redirect", "rule_conflict"]


class Precedent(BaseModel):
    status: Literal["new", "reused", "departed"] = "new"
    from_: str | None = Field(default=None, alias="from")
    differing_fact: str | None = None

    model_config = {"populate_by_name": True}


class RulingRecord(BaseModel):
    """00.15.5 RulingRecord. `id` is minted by `log_ruling` when empty."""

    id: str = ""
    time: dict[str, Any] | None = None
    frame_id: str | None = None
    signature: str
    situation: str
    facts_cited: list[str] = Field(default_factory=list)
    frame_summary: dict[str, Any] = Field(default_factory=dict)  # attribute, dc_source, dc, levers, snags, ...
    result: dict[str, Any] = Field(default_factory=dict)  # {degree, outcome}
    precedent: Precedent = Field(default_factory=Precedent)
    kind: RulingKind
    review_flag: bool = False
    tags: list[str] = Field(default_factory=list)


def _delta_str(d: Any) -> str:
    if isinstance(d, str):
        return d
    knob, delta = getattr(d, "knob", None), getattr(d, "delta", None)
    if knob is None and isinstance(d, dict):
        knob, delta = d.get("knob"), d.get("delta")
    return f"{knob}:{delta}" if delta else str(knob)


def signature(anchor_id: str, deltas: Iterable[Any] = ()) -> str:  # rule: 00.15.5
    """'<anchor_id>+<delta1>+<delta2>', deltas sorted; a delta is 'knob:value' (or 'knob')."""
    return "+".join([anchor_id, *sorted(_delta_str(d) for d in deltas)])


def gate_signature(kind: Literal["g3_redirect", "g4"], key: str) -> str:  # rule: 00.15.6
    """G3: keyed on the license that would cover the method (or the verb); G4: on the ruling-out fact/test."""
    return f"{kind}:{key}"


def oracle_signature(predicate: str, place_kind: str | None = None) -> str:  # rule: 00.15.6
    """Same kind of question (the predicate) in the same kind of place."""
    return f"oracle:{predicate}" + (f"@{place_kind}" if place_kind else "")


def find_rulings(store: Any, sig: str, *, staged: Sequence[Event] = ()) -> list[RulingRecord]:  # rule: 00.15.6
    """Every logged ruling with this signature, oldest first: committed (rulings_idx) then staged."""
    out: list[RulingRecord] = []
    seen: set[str] = set()
    if store is not None:
        for rid, seq in store.rulings(sig):
            ev = store.event(seq)
            if ev is not None and ev.type == "ruling_logged" and seq not in store.state.reverted:
                out.append(RulingRecord.model_validate(ev.payload_json()["ruling"]))
                seen.add(rid)
    for ev in staged:
        if ev.type == "ruling_logged":
            r = ev.payload_json()["ruling"]
            if r.get("signature") == sig and r.get("id") not in seen:
                out.append(RulingRecord.model_validate(r))
    return out


def precedent_for(found: Sequence[RulingRecord], differing_fact: str | None = None) -> Precedent:
    # rule: 00.15.6
    """Reuse the latest matching ruling unless a stated fact differs (named in `differing_fact`)."""
    if not found:
        return Precedent(status="new")
    return Precedent.model_validate({"status": "departed" if differing_fact else "reused", "from": found[-1].id,
                                     "differing_fact": differing_fact})


def _taken_ids(store: Any, staged: Sequence[Event]) -> set[str]:
    taken = {ev.payload_json()["ruling"]["id"] for ev in staged if ev.type == "ruling_logged"}
    if store is not None:
        taken |= {r[0] for r in store.conn.execute("SELECT ruling_id FROM rulings_idx")}
    return taken


def log_ruling(record: RulingRecord, mint: Callable[[str], str], *, store: Any = None,
               staged: Sequence[Event] = (), turn_id: str | None = None,
               rule_id: str = "00.15.5") -> Event:  # rule: 00.15.5
    """A `ruling_logged` event (the store indexes it by signature in rulings_idx on commit). Pass `store` and
    the staged events: `ruling_logged` does not advance the `rul` counter (its id is nested), so a minted id
    already used is skipped."""
    rec = record
    if not rec.id:
        taken = _taken_ids(store, staged)
        rid = mint(ids.RULING)
        while rid in taken:
            rid = mint(ids.RULING)
        rec = record.model_copy(update={"id": rid})
    return Event.of("ruling_logged", source=rec.frame_id or "engine", rule_id=rule_id, turn_id=turn_id,
                    ruling=rec.model_dump(mode="json", by_alias=True))
