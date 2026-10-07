"""Views of the projection (`get_state`, 00.14.2 #8; T013). Plain JSON-ready dicts.

- `audit_view(state)`: everything.
- `narrator_view(state)`: what the narrator (and every packet builder) may see. Sealed items are replaced by their
  permitted slice, or dropped when they have none; a fact's `truth` is never included; hidden clocks are dropped
  and sensed clocks carry no fill (00.8.4). INV-10.
- `codex_view(state)`: shown and available state only (00.6.4); nothing sealed or background.

`scope` narrows the entity-keyed families to the listed entity ids (e.g. the scene's cast).
Bi-temporal fact queries over the whole history are `Store.fact(subject, predicate, at_seq)`; `fact()` below
answers from the projection for the current value.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Literal

from engine.store.projection import WorldState

ViewName = Literal["narrator", "codex", "audit"]
PLAYER_FACING = ("shown", "available")


def fact(state: WorldState, subject: str, predicate: str) -> Any:
    """The current value of (subject, predicate), or None."""
    return state.fact_value(subject, predicate)


def view(state: WorldState, name: ViewName, scope: Iterable[str] | None = None) -> dict[str, Any]:
    return {"narrator": narrator_view, "codex": codex_view, "audit": audit_view}[name](state, scope)


def audit_view(state: WorldState, scope: Iterable[str] | None = None) -> dict[str, Any]:
    out = state.model_dump(mode="json")
    return _scoped(out, scope)


def narrator_view(state: WorldState, scope: Iterable[str] | None = None) -> dict[str, Any]:  # rule: 00.6.5
    seals = state.seals
    entities: dict[str, Any] = {}
    for eid, e in state.entities.items():
        if eid in seals:
            if seals[eid].slice:
                entities[eid] = {"id": eid, "kind": e.kind, "slice": seals[eid].slice}
            continue
        d = e.model_dump(mode="json", exclude={"sealed_fields", "data"})
        data = {}
        for k, v in e.data.items():
            ref = f"{eid}#{k}"
            if ref in seals or k in e.sealed_fields:
                if ref in seals and seals[ref].slice:
                    data[k] = {"slice": seals[ref].slice}
                continue
            data[k] = v
        d["data"] = data
        entities[eid] = d
    visible = set(entities)
    facts = {}
    for fid, f in state.facts.items():
        if fid in seals or f.visibility == "sealed" or (f.subject in state.entities and f.subject not in visible):
            continue
        facts[fid] = f.model_dump(mode="json", exclude={"truth"})
    clocks = {}
    for cid, c in state.clocks.items():  # rule: 00.8.4
        if c.visibility == "hidden":
            continue
        d = {"id": cid, "name": c.name, "kind": c.kind, "visibility": c.visibility, "status": c.status}
        if c.visibility == "public":
            d |= {"filled": c.filled, "segments": c.segments}
        clocks[cid] = d
    out = {
        "time": state.time.model_dump(mode="json", exclude={"last_boundary"}),
        "scene": state.scene.model_dump(mode="json") if state.scene else None,
        "entities": entities,
        "quantities": {k: _dump(v) for k, v in state.quantities.items() if k in visible},
        "facts": facts,
        "relationships": {k: r.model_dump(mode="json") for k, r in state.relationships.items()
                          if r.a in visible and r.b in visible},
        "positions": {k: _dump(v) for k, v in state.positions.items() if k in visible},
        "knowledge": {k: {f: _dump(e) for f, e in v.items() if f in facts} for k, v in state.knowledge.items()
                      if k in visible},
        "clocks": clocks,
        "conditions": {k: _dump(c) for k, c in state.conditions.items() if c.target in visible},
        "licenses": {k: [_dump(x) for x in v] for k, v in state.licenses.items() if k in visible},
        "commitments": [fid for fid, f in facts.items() if f["kind"] == "commitment"],
        "meta": dict(state.meta),
        "open_pause": _dump(state.open_pause()) if state.open_pause() else None,
    }
    return _scoped(out, scope)


def codex_view(state: WorldState, scope: Iterable[str] | None = None) -> dict[str, Any]:  # rule: 00.6.4
    seals = state.seals
    entities: dict[str, Any] = {}
    for eid, e in state.entities.items():
        if eid in seals or e.visibility not in PLAYER_FACING:
            continue
        d = e.model_dump(mode="json", exclude={"sealed_fields", "data"})
        d["data"] = {k: v for k, v in e.data.items() if f"{eid}#{k}" not in seals and k not in e.sealed_fields}
        entities[eid] = d
    visible = set(entities)
    facts = {fid: f.model_dump(mode="json", exclude={"truth"}) for fid, f in state.facts.items()
             if f.visibility in PLAYER_FACING and fid not in seals}
    clocks = {}
    for cid, c in state.clocks.items():
        if c.visibility == "public":
            clocks[cid] = {"id": cid, "name": c.name, "filled": c.filled, "segments": c.segments, "status": c.status}
        elif c.visibility == "sensed":
            clocks[cid] = {"id": cid, "name": c.name, "status": c.status}
    out = {
        "time": state.time.now.model_dump(mode="json"),
        "entities": entities,
        "quantities": {k: {n: _dump(q) for n, q in v.items() if q.visibility in PLAYER_FACING}
                       for k, v in state.quantities.items() if k in visible},
        "facts": facts,
        "clocks": clocks,
        "conditions": {k: _dump(c) for k, c in state.conditions.items() if c.target in visible},
        "licenses": {k: [_dump(x) for x in v] for k, v in state.licenses.items() if k in visible},
        "positions": {k: _dump(v) for k, v in state.positions.items() if k in visible},
    }
    return _scoped(out, scope)


def _dump(x: Any) -> Any:
    if isinstance(x, dict):
        return {k: _dump(v) for k, v in x.items()}
    return x.model_dump(mode="json") if hasattr(x, "model_dump") else x


_ENTITY_KEYED = ("entities", "quantities", "positions", "knowledge", "licenses")


def _scoped(out: dict[str, Any], scope: Iterable[str] | None) -> dict[str, Any]:
    if scope is None:
        return out
    keep = set(scope)
    for fam in _ENTITY_KEYED:
        if isinstance(out.get(fam), dict):
            out[fam] = {k: v for k, v in out[fam].items() if k in keep}
    if isinstance(out.get("facts"), dict):
        out["facts"] = {k: f for k, f in out["facts"].items() if f["subject"] in keep}
    if isinstance(out.get("conditions"), dict):
        out["conditions"] = {k: c for k, c in out["conditions"].items() if c["target"] in keep}
    return out
