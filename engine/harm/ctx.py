"""What harm and ability functions need from their caller, and the write overlay they build events with.

    ctx = HarmCtx(state=tx.state, mint=tx.mint, rules=rules, rng=rng)   # or HarmCtx.of(tx, rules, rng)
    res = apply_harm(ctx, "pc.wren", severity="S3", source="foe.wight", frame_id="frame.4")
    tx.add_all(res.events)

Every function here returns events; the caller stages them (engine/CONVENTIONS.md). Boundary handlers take any
object with `state`, `mint`, `rules` (and optionally `rng`, `boundary`, `payload`): the time registry's context
or a `HarmCtx`.

`Writes` is an overlay on the projection: a function that writes the same fact twice, or a fact and then reads it
back, sees its own unstaged writes, so `supersedes` chains and quantity deltas are right when the caller stages
the events in order.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from typing import Any, Protocol

from engine import ids
from engine.store.events import Event, Quantity
from engine.store.projection import WorldState


class Dice(Protocol):
    def d(self, sides: int, purpose: str, *, stream: str = "dice") -> int: ...


class Ctx(Protocol):
    state: WorldState
    rules: Any

    def mint(self, prefix: str) -> str: ...


@dataclass
class HarmCtx:
    state: WorldState
    mint: Callable[[str], str]
    rules: Any
    rng: Dice | None = None
    boundary: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def of(cls, tx: Any, rules: Any, rng: Dice | None = None, *, boundary: str | None = None,
           payload: dict[str, Any] | None = None) -> HarmCtx:
        return cls(state=tx.state, mint=tx.mint, rules=rules, rng=rng, boundary=boundary, payload=dict(payload or {}))


def rng_of(ctx: Any) -> Dice | None:
    return getattr(ctx, "rng", None)


def boundary_payload(ctx: Any) -> dict[str, Any]:
    p = getattr(ctx, "payload", None)
    return dict(p) if isinstance(p, dict) else {}


class Writes:
    """Builds events against the projection plus its own earlier, unstaged writes."""

    def __init__(self, state: WorldState, mint: Callable[[str], str], *, source: str = "engine") -> None:
        self.state = state
        self.mint = mint
        self.source = source
        self.events: list[Event] = []
        self._facts: dict[tuple[str, str], tuple[str, Any]] = {}
        self._qty: dict[tuple[str, str], Quantity] = {}
        self._meta: dict[str, Any] = {}

    @classmethod
    def of(cls, ctx: Any, *, source: str = "engine") -> Writes:
        return cls(ctx.state, ctx.mint, source=source)

    # -- facts
    def fact_value(self, subject: str, predicate: str, default: Any = None) -> Any:
        k = (subject, predicate)
        if k in self._facts:
            return self._facts[k][1]
        return self.state.fact_value(subject, predicate, default)

    def _current(self, subject: str, predicate: str) -> str | None:
        k = (subject, predicate)
        return self._facts[k][0] if k in self._facts else self.state.current_fact_id(subject, predicate)

    def fact(self, subject: str, predicate: str, value: Any, *, rule_id: str, kind: str = "fact",
             visibility: str = "shown", truth: str = "true", certainty: str = "established",
             only_if_changed: bool = True) -> str | None:
        """Write (or supersede) `subject.predicate`. Returns the fact id, or None when nothing changed."""
        if only_if_changed and self._current(subject, predicate) is not None \
                and self.fact_value(subject, predicate) == value:
            return None
        fid = self.mint(ids.FACT)
        self.events.append(Event.of(
            "fact_set", {"source": "data"}, source=self.source, rule_id=rule_id, fact_id=fid,
            subject=subject, predicate=predicate, value=value, kind=kind, visibility=visibility, truth=truth,
            certainty=certainty, supersedes=self._current(subject, predicate)))
        self._facts[(subject, predicate)] = (fid, value)
        return fid

    # -- quantities
    def quantity(self, entity: str, name: str) -> Quantity | None:
        k = (entity, name)
        if k in self._qty:
            return self._qty[k]
        q = self.state.quantities.get(entity, {}).get(name)
        return q.model_copy() if q is not None else None

    def define(self, entity: str, name: str, value: Quantity, *, reason: str, rule_id: str) -> None:
        self.events.append(Event.of("quantity_defined", source=self.source, rule_id=rule_id, entity=entity,
                                    quantity=name, value=value, reason=reason))
        self._qty[(entity, name)] = value.model_copy()

    def set_quantity(self, entity: str, name: str, value: int, *, reason: str, rule_id: str,
                     frame_id: str | None = None) -> int:
        """Set a quantity, clamped to its range (00.3). Returns the delta actually applied (0: no event)."""
        q = self.quantity(entity, name)
        if q is None:
            raise ValueError(f"{entity} has no quantity {name}")
        new = max(q.min, value if q.max is None else min(q.max, value))
        delta = new - q.current
        if delta == 0:
            return 0
        self.events.append(Event.of("quantity_changed", source=self.source, rule_id=rule_id, entity=entity,
                                    quantity=name, delta=delta, new_value=new, clamped=new != value,
                                    reason=reason, frame_id=frame_id))
        q.current = new
        self._qty[(entity, name)] = q
        return delta

    def add_quantity(self, entity: str, name: str, delta: int, *, reason: str, rule_id: str,
                     frame_id: str | None = None) -> int:
        q = self.quantity(entity, name)
        if q is None:
            raise ValueError(f"{entity} has no quantity {name}")
        return self.set_quantity(entity, name, q.current + delta, reason=reason, rule_id=rule_id, frame_id=frame_id)

    # -- meta (counters, triggers, logs)
    def meta_value(self, key: str, default: Any = None) -> Any:
        return self._meta[key] if key in self._meta else self.state.meta.get(key, default)

    def meta(self, key: str, value: Any, *, rule_id: str | None = None) -> None:
        self.events.append(Event.of("meta_set", source=self.source, rule_id=rule_id, key=key, value=value))
        self._meta[key] = value

    def log(self, kind: str, value: dict[str, Any], *, rule_id: str | None = None) -> None:
        """An audit record (`log.<kind>`): the harm event record, a refused lethal flag, a coarse outcome."""
        self.meta(f"log.{kind}", value, rule_id=rule_id)

    def coarse(self, rule_id: str, note: str, **detail: Any) -> None:
        """A rule the milestone runs coarsely: logged, never silently dropped (FR-026)."""
        self.log("coarse", {"rule_id": rule_id, "note": note, **detail}, rule_id=rule_id)

    def extend(self, events: Iterable[Event]) -> None:
        self.events.extend(events)


def counter_key(entity: str, name: str) -> str:
    """Meta key of a per-character counter (e.g. `pc.wren.breathers_since_short_rest`)."""
    return f"{entity}.{name}"
