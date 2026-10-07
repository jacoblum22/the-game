"""Small helpers the engine/world modules share: staging events, the active PC, meta and trigger writes."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING, Any

from engine.store.events import WORLD, Event
from engine.store.projection import WorldState

if TYPE_CHECKING:
    from engine.store.db import Store, Transaction
    from engine.time.scheduler import TimeContext


class WorldError(RuntimeError):
    """A misuse of the world API (no scene to end, an unreachable place, no RNG for a roll)."""


def stage(ctx: TimeContext, *events: Event) -> list[int]:
    """Stage events: through `ctx.emit` inside a running handler (stamps the boundary instant and the handler
    id), else straight into the transaction (stamped with the current game time)."""
    if ctx.handler_id:
        return ctx.emit(*events)
    return ctx.tx.add_all(events)


def active_pc(state: WorldState) -> str | None:
    """The PC being played: `meta['pc.active']`, else the most recently created PC (as engine/harm reads it)."""
    p = state.meta.get("pc.active")
    if isinstance(p, str) and p in state.entities:
        return p
    pcs = [eid for eid, e in state.entities.items() if e.kind == "pc"]
    return pcs[-1] if pcs else None


def meta(key: str, value: Any, rule_id: str, source: str = "engine") -> Event:
    return Event.of("meta_set", source=source, rule_id=rule_id, key=key, value=value)


def fact(tx: Transaction, subject: str, predicate: str, value: Any, *, rule_id: str, kind: str = "fact",
         source: str = "generation", visibility: str = "background", gate: str | None = None,
         event_source: str = "engine") -> Event:
    """A fact_set that supersedes the current (subject, predicate) fact, if any."""
    return Event.of("fact_set", {"source": source}, source=event_source, rule_id=rule_id,
                    fact_id=tx.mint("fact"), subject=subject, predicate=predicate, value=value, kind=kind,
                    visibility=visibility, gate=gate, supersedes=tx.state.current_fact_id(subject, predicate))


def raise_trigger(tx: Transaction, trigger: str, params: dict[str, Any] | None, *, rule_id: str,
                  subject: str = WORLD) -> Event:
    """A raised trigger is a current `trg.*` flag fact (engine/retrieve/triggers.py); a falsy value lowers it."""
    return fact(tx, subject, trigger, params or True, rule_id=rule_id, kind="flag", source="ruling")


def lower_trigger(tx: Transaction, trigger: str, *, rule_id: str, subject: str = WORLD) -> list[Event]:
    if not tx.state.fact_value(subject, trigger):
        return []
    return [fact(tx, subject, trigger, False, rule_id=rule_id, kind="flag", source="ruling")]


def trigger_raised(state: WorldState, trigger: str, subject: str = WORLD) -> bool:
    return bool(state.fact_value(subject, trigger))


def severity_rank(sev: Any) -> int:
    """'S3' -> 3; anything else 0."""
    s = str(sev or "")
    return int(s[1:]) if len(s) == 2 and s[0] == "S" and s[1].isdigit() else 0


def scene_number(scene_id: str | None) -> int:
    """'scn.7' -> 7 (0 for none)."""
    if not scene_id:
        return 0
    tail = scene_id.rsplit(".", 1)[-1]
    return int(tail) if tail.isdigit() else 0


def scene_events(tx: Transaction, since_seq: int) -> list[Event]:
    """Committed and staged events with seq >= `since_seq` (the current scene's log when given its start)."""
    store: Store = tx.store
    out = list(store.events(since=since_seq - 1)) if since_seq <= store.last_seq else []
    seen = {e.seq for e in out}
    out += [e for e in tx.events if e.seq not in seen and (e.seq or 0) >= since_seq]
    reverted = set(tx.state.reverted)
    return [e for e in out if e.seq not in reverted]


def ids_of(events: Iterable[Event], etype: str) -> list[Any]:
    return [e.payload for e in events if e.type == etype]
