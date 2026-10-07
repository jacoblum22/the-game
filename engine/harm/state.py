"""Reading a character's harm state (07.1). Harm states, wound load, dying step, brink, Down and `defeated` are
plain facts on the character (subject = the entity id), written by engine/harm only:

    harm_state      "harm_state.active" | ".staggered" | ".dying" | ".dead"   (07.1.3; absent = from Vitality)
    wound_load      int (07.2.6)          dying_step   0..3 (07.2.7)          brink   int (07.2.8)
    down            bool (07.2.9)         defeated     {"manner": ...} | None (00.17.1 Q15)

Vitality is the quantity `vitality`; Focus is `focus` (engine/abilities). Readers take anything with
`fact_value(subject, predicate, default)` and `quantity(entity, name)`: a `WorldState` (through `View`) or the
`Writes` overlay, so a procedure reads its own unstaged writes.
"""

from __future__ import annotations

from typing import Any, Protocol

from engine.store.events import Quantity
from engine.store.projection import WorldState

ACTIVE, STAGGERED, DYING, DEAD = ("harm_state.active", "harm_state.staggered", "harm_state.dying",
                                  "harm_state.dead")
LADDER_KINDS = ("pc", "companion")  # the full ladder and the keys (07.3.6 test 3); others use 07.2.10
VITALITY = "vitality"


class Reader(Protocol):
    state: WorldState

    def fact_value(self, subject: str, predicate: str, default: Any = None) -> Any: ...

    def quantity(self, entity: str, name: str) -> Quantity | None: ...


class View:
    """A `Reader` over a bare projection."""

    def __init__(self, state: WorldState) -> None:
        self.state = state

    def fact_value(self, subject: str, predicate: str, default: Any = None) -> Any:
        return self.state.fact_value(subject, predicate, default)

    def quantity(self, entity: str, name: str) -> Quantity | None:
        return self.state.quantities.get(entity, {}).get(name)


def reader(x: WorldState | Reader) -> Reader:
    return View(x) if isinstance(x, WorldState) else x


def kind_of(state: WorldState, eid: str) -> str:
    e = state.entities.get(eid)
    return e.kind if e is not None else ""


def on_ladder(state: WorldState, eid: str) -> bool:
    return kind_of(state, eid) in LADDER_KINDS


def vitality(r: WorldState | Reader, eid: str) -> Quantity | None:
    # coarse: 07.1.2 — the maximum is set at creation (02); h.07.vitality_max recomputes it from M3.
    return reader(r).quantity(eid, VITALITY)


def harm_state(r: WorldState | Reader, eid: str) -> str:  # rule: 07.1.3
    rd = reader(r)
    hs = rd.fact_value(eid, "harm_state")
    if hs:
        return str(hs)
    v = rd.quantity(eid, VITALITY)
    return STAGGERED if v is not None and v.current <= 0 else ACTIVE


def wound_load(r: WorldState | Reader, eid: str) -> int:
    return int(reader(r).fact_value(eid, "wound_load", 0) or 0)


def dying_step(r: WorldState | Reader, eid: str) -> int:
    return int(reader(r).fact_value(eid, "dying_step", 0) or 0)


def brink(r: WorldState | Reader, eid: str) -> int:
    return int(reader(r).fact_value(eid, "brink", 0) or 0)


def is_down(r: WorldState | Reader, eid: str) -> bool:
    return bool(reader(r).fact_value(eid, "down", False))


def defeated_manner(r: WorldState | Reader, eid: str) -> str | None:
    d = reader(r).fact_value(eid, "defeated")
    return str(d.get("manner")) if isinstance(d, dict) and d.get("manner") else None


def bloodied(current: int, maximum: int) -> bool:  # rule: 07.1.4
    return 0 < current and current * 2 <= maximum


def descriptor(r: WorldState | Reader, eid: str) -> str:  # rule: 07.1.1
    """The word the player sees: fresh, worn, bloodied, staggered, dying, down, dead."""
    rd = reader(r)
    hs = harm_state(rd, eid)
    if hs == DEAD:
        return "dead"
    if is_down(rd, eid):
        return "down"
    if hs == DYING:
        return "dying"
    v = rd.quantity(eid, VITALITY)
    if v is None:
        return "fresh"
    if hs == STAGGERED or v.current <= 0:
        return "staggered"
    mx = v.max if v.max is not None else v.current
    if v.current >= mx:
        return "fresh"
    return "bloodied" if bloodied(v.current, mx) else "worn"


def descriptor_words(rules: Any, word: str) -> list[str]:  # rule: 07.1.1
    for d in rules.harm["descriptors"]:
        if d["id"] == word:
            return list(d["words"])
    return []


def attribute(state: WorldState, eid: str, name: str) -> int:
    """An attribute modifier: the entity's `data.attributes[name]` plus any maim deltas (07.7.4)."""
    e = state.entities.get(eid)
    base = int(((e.data.get("attributes") or {}).get(name, 0)) if e else 0)
    return base + int(state.fact_value(eid, f"attribute_delta.{name}", 0) or 0)


def endure_modifier(state: WorldState, eid: str) -> int:  # rule: 07.2.7
    """`Endurance + competence + edge` for the dying check and the Gamble. M1: Endurance plus the entity's
    `data.endure_bonus` (competence and edge from licences are the resolver's; creation may store the sum)."""
    e = state.entities.get(eid)
    bonus = int(e.data.get("endure_bonus", 0)) if e else 0
    return attribute(state, eid, "endurance") + bonus


def fate(state: WorldState, eid: str) -> int:
    q = state.quantities.get(eid, {}).get("fate")
    return q.current if q is not None else 0


def pcs(state: WorldState) -> list[str]:
    return [i for i, e in state.entities.items() if e.kind == "pc"]
