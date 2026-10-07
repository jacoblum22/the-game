"""The place graph (10.1; T059): places as entities, route links as facts, reachability and moves.

    with store.transaction() as tx:
        seed_world_into_store(tx, world)                  # once, at game creation (world: SeededWorld)
        put(tx, pc, world.incident.place)                 # the opening places the PC
    links = reachable(store.state, "loc.ashen_march_ravenford")
    with store.transaction(turn) as tx:
        arrival = move(TimeContext(tx, rules, rng), "loc.ashen_march_sunken_meads")
        # arrival.arrived / .interrupt; frame the arrival scene from arrival.place, .mode, .cast_here

Storage. Every place is an `entity_created` (kind place) whose `data` is the 10.1.2 place record (without its
links). An undiscovered place is sealed with the gate "the PC arrives, or perceives it"; a rumored place
(known, undiscovered) keeps its name as the permitted slice (10.1.5). Each 10.1.3 route link is a fact on the
place it leaves from, predicate `link.<route id>`, value `{to, route, route_kind, travel_watches, terrain,
known}`, written for both directions; an unknown link is sealed. The seed's factions, threads, clocks and
cast are written too (threads as `thr.*` entities; NPCs at their home), plus the region's name tables and
peoples in meta (`world.names`, `world.peoples`) for later walk-ons.

Implicit links. The seed writes no links inside a settlement or to a landmark. A building is reached from its
settlement or a sibling building, and a landmark from its area, by an engine `passage` link
(`IMPLICIT_LINKS`: 1 interval, 10.1.3's passage length; 1 hour for a landmark, provisional).
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from engine import ids
from engine.gen.world_seed import SeededWorld
from engine.retrieve.anchors import natural_key
from engine.store.db import Transaction
from engine.store.events import ClockRecord, EntityRecord, Event
from engine.store.projection import WorldState
from engine.time import clock
from engine.time.scheduler import AdvanceResult, TimeContext, advance_time, set_mode
from engine.world.common import WorldError, active_pc, fact, meta, stage

UNDISCOVERED_GATE = "the PC arrives, or perceives it"  # 10.1.5
LINK = "link."  # fact predicate prefix for a route link
IMPLICIT_LINKS: dict[str, tuple[int, str]] = {"building": (1, "interval"), "landmark": (1, "hour")}
SITE_KINDS = ("site", "site_area")
NPC_SEALED = ("wants", "fears", "refusals", "secrets")  # 15.2.1: sealed until learned
_PLACE_SKIP = ("id", "name", "links")


class RouteLink(BaseModel):
    """A 10.1.3 link as the engine reads it (from a fact, or an implicit passage)."""

    to: str
    route: str
    route_kind: str
    length: int  # in `unit`
    unit: str = "watch"
    terrain: list[str] = Field(default_factory=list)
    known: bool = True
    implicit: bool = False


class Arrival(BaseModel):
    """What `move` returns: enough to frame the arrival scene (12.4.3) or the interrupt's scene."""

    place: str
    name: str
    place_kind: str
    from_place: str | None
    route: RouteLink
    arrived: bool
    mode: str  # the time mode on entry (T-10-1 / T-12-3)
    discovered_now: bool = False
    cast_here: list[str] = Field(default_factory=list)
    interrupt: tuple[str, str] | None = None
    remainder_rounds: int = 0
    narration: list[str] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=list)


# ------------------------------------------------------------------------------------------------ seeding


def _thread_id(seed_id: str, taken: Any) -> str:
    return ids.entity_id("thread", seed_id.replace(".", "_"), taken)


def seed_world_into_store(tx: Transaction, world: SeededWorld) -> dict[str, str]:  # rule: 12.16.1
    """Write the seeded region into the store (10.1; 12.16.8-12.16.11). Returns the seed-thread-id -> entity-id
    map (`lead.1` -> `thr.lead_1`)."""
    rec = world.record
    places = {p["id"]: p for p in rec["places"]}
    for p in rec["places"]:  # parents come before children in the seed's order
        tx.add(_place_event(p))
    for p in rec["places"]:
        for link in p.get("links", []):
            _write_links(tx, p["id"], link, places)
    for f in world.factions:
        tx.add(Event.of("entity_created", source="seed", rule_id="12.16.9", entity=EntityRecord(
            id=f.id, kind="faction", name=f.name, visibility="available",
            data={"tier": f.tier, "seat": f.seat, "temperament": f.temperament, "officers": f.officers})))
    for f in world.factions:
        for other, value in sorted(f.relations.items()):
            if other in tx.state.entities:
                tx.add(Event.of("relationship_set", source="seed", rule_id="12.16.9", a=f.id, b=other,
                                kind="faction_relation", value=value, new_value=value, reason="world seed"))
    for c in rec.get("clocks", []):
        if c["id"] not in tx.state.clocks:
            cr = ClockRecord.model_validate({k: v for k, v in c.items() if k in ClockRecord.model_fields})
            tx.add(Event.of("clock_created", source="seed", rule_id="12.16.10", clock=cr))
    thread_ids: dict[str, str] = {}
    for t in world.threads:
        thread_ids[t.id] = _thread_id(t.id, tx.state.entities)
        tx.add(Event.of("entity_created", source="seed", rule_id="12.16.12", entity=EntityRecord(
            id=thread_ids[t.id], kind="thread", name=t.text[:60], visibility="available",
            data={"seed_id": t.id, "thread_kind": t.kind, "text": t.text, "points_to": t.points_to,
                  "status": "active"})))
    for n in rec.get("npcs", []):
        tx.add_all(_npc_events(n, tx.state))
    tx.add(meta("world.region", {"id": world.region.id, "name": world.region.name, "haven": world.region.haven},
                "12.16.1", "seed"))
    tx.add(meta("world.names", rec.get("names", []), "12.16.7", "seed"))
    tx.add(meta("world.peoples", [p for p in rec.get("peoples", []) if p.get("present") != "absent"], "12.16.7",
                "seed"))
    tx.add(meta("world.threads", thread_ids, "12.16.12", "seed"))
    tx.add(meta("thread_list", {tid: 1 for tid in thread_ids.values()}, "12.6.6", "seed"))
    return thread_ids


def _place_event(p: dict[str, Any]) -> Event:  # rule: 10.1.2
    data = {k: v for k, v in p.items() if k not in _PLACE_SKIP}
    if p.get("discovered", True):
        rec = EntityRecord(id=p["id"], kind="place", name=p["name"], visibility="available", data=data)
        return Event.of("entity_created", source="seed", rule_id="10.1.2", entity=rec)
    rec = EntityRecord(id=p["id"], kind="place", name=p["name"], visibility="sealed", data=data)  # rule: 10.1.5
    slices = {"*": p["name"]} if p.get("known") else {}
    return Event.of("entity_created", source="seed", rule_id="10.1.5", entity=rec, slices=slices,
                    gate=UNDISCOVERED_GATE)


def _write_links(tx: Transaction, frm: str, link: dict[str, Any], places: dict[str, Any]) -> None:
    # rule: 10.1.3
    """Stage the link as written on `frm`, and the reverse link on its destination unless already written."""
    to = link["to"]
    for a, b in ((frm, to), (to, frm)):
        pred = LINK + link["route"]
        if tx.state.current_fact_id(a, pred) or a not in places:
            continue
        value = {"to": b, "route": link["route"], "route_kind": link["route_kind"],
                 "travel_watches": link["travel_watches"], "terrain": list(link.get("terrain") or []),
                 "known": bool(link.get("known", True))}
        vis = "available" if value["known"] else "sealed"
        tx.add(fact(tx, a, pred, value, rule_id="10.1.3", source="data", visibility=vis,
                    gate=None if value["known"] else UNDISCOVERED_GATE, event_source="seed"))


def _npc_events(n: dict[str, Any], state: WorldState) -> list[Event]:  # rule: 12.16.11
    data = {k: v for k, v in n.items() if k not in ("id", "name", "exists", "standing_to_pc")}
    sealed = [k for k in NPC_SEALED if data.get(k)]
    rec = EntityRecord(id=n["id"], kind="npc", name=n["name"], visibility="background",
                       exists=n.get("exists", "exists"), sealed_fields=sealed, data=data)
    out = [Event.of("entity_created", source="seed", rule_id="12.16.11", entity=rec,
                    gate="learned in play (15.2.1)" if sealed else None)]
    home = n.get("home")
    if home in state.entities:
        out.append(Event.of("position_set", source="seed", rule_id="12.16.11", entity=n["id"], location=home))
    return out


def put(tx: Transaction, entity: str, place: str) -> int:
    # rule: 10.1.1
    """Place an entity (the PC at the opening, an NPC) at a place node."""
    if place not in tx.state.entities or tx.state.entities[place].kind != "place":
        raise WorldError(f"{place} is not a place")
    return tx.add(Event.of("position_set", rule_id="10.1.1", entity=entity, location=place))


# -------------------------------------------------------------------------------------------- reading


def place_kind(state: WorldState, place: str) -> str:
    e = state.entities.get(place)
    return str(e.data.get("place_kind", "")) if e else ""


def location(state: WorldState, entity: str | None = None) -> str | None:
    """Where `entity` (default: the active PC) is."""
    eid = entity or active_pc(state)
    pos = state.positions.get(eid) if eid else None
    return pos.location if pos else None


def is_discovered(state: WorldState, place: str) -> bool:  # rule: 10.1.5
    v = state.fact_value(place, "discovered")
    if v is not None:
        return bool(v)
    e = state.entities.get(place)
    return bool(e and e.data.get("discovered", True))


def links(state: WorldState, place: str) -> list[RouteLink]:  # rule: 10.1.3
    """Every link leaving `place`, known or not, explicit ones first, by route id."""
    out = []
    for fid in sorted(state.facts):
        f = state.facts[fid]
        if f.subject == place and f.predicate.startswith(LINK) and isinstance(f.value, dict):
            v = f.value
            out.append(RouteLink(to=v["to"], route=v["route"], route_kind=v["route_kind"],
                                 length=int(v["travel_watches"]), unit="watch", terrain=list(v.get("terrain") or []),
                                 known=bool(v.get("known", True))))
    out.sort(key=lambda x: natural_key(x.route))
    return out + _implicit_links(state, place)


def _implicit_links(state: WorldState, place: str) -> list[RouteLink]:
    """Passages the seed does not write: building <-> its settlement and its siblings; landmark <-> its area."""
    e = state.entities.get(place)
    if e is None:
        return []
    kind, parent = e.data.get("place_kind"), e.data.get("parent")
    out: list[RouteLink] = []

    def add(to: str, child_kind: str) -> None:
        n, unit = IMPLICIT_LINKS[child_kind]
        out.append(RouteLink(to=to, route=f"passage.{place}.{to}", route_kind="passage", length=n, unit=unit,
                             implicit=True))

    if kind in IMPLICIT_LINKS and parent in state.entities:
        add(parent, kind)
    for oid, o in state.entities.items():
        if o.kind != "place" or oid == place:
            continue
        ok, op = o.data.get("place_kind"), o.data.get("parent")
        if op == place and ok in IMPLICIT_LINKS:
            add(oid, ok)
        elif kind == "building" and ok == "building" and op == parent:
            add(oid, "building")
    return out


def reachable(state: WorldState, from_place: str | None = None) -> list[RouteLink]:  # rule: 10.1.3
    """Links the PC can take from `from_place` (default: where the PC is): known links to existing places."""
    src = from_place or location(state)
    if src is None:
        return []
    seen: set[str] = set()
    out = []
    for link in links(state, src):
        if link.known and link.to in state.entities and link.to not in seen:
            seen.add(link.to)
            out.append(link)
    return out


def cast_at(state: WorldState, place: str) -> list[str]:
    """NPCs and companions positioned at `place` who still exist."""
    return [eid for eid, pos in state.positions.items()
            if pos.location == place and eid in state.entities
            and state.entities[eid].kind in ("npc", "companion", "adversary")
            and state.entities[eid].exists == "exists"]


def entry_mode(state: WorldState, place: str) -> str:  # rule: T-12-3
    """The time mode on entering `place` (T-10-1): a site is `site`; anything else after a move is `free`."""
    return "site" if place_kind(state, place) in SITE_KINDS else "free"


# ----------------------------------------------------------------------------------------------- moving


def move(ctx: TimeContext, to_place: str, *, end_scene: bool = True) -> Arrival:  # rule: 10.1.3
    """Move the PC along a reachable link: end the current scene (place change, 12.4.2 (2)), switch to `travel`
    for a route (T-12-3), advance time by the link's length (PR-00-2; ch.10's travel handlers are M4 and log as
    skipped), then arrive: position, discovery (10.1.5) and the entry mode. On an interrupt the PC has not
    arrived: `arrived` is False and `continue_move(ctx, arrival)` finishes the journey later."""
    state = ctx.tx.state
    pc = active_pc(state)
    if pc is None:
        raise WorldError("no PC to move")
    here = location(state, pc)
    link = next((x for x in reachable(state, here) if x.to == to_place), None)
    if link is None:
        raise WorldError(f"{to_place} is not reachable from {here}")
    if end_scene and state.scene is not None:
        from engine.world.scenes import end_scene as _end
        _end(ctx, "place_change")
    mode = "travel" if not link.implicit else None
    res = advance_time(ctx, link.length, link.unit, f"travel to {to_place} by {link.route}", mode=mode)
    arrival = _arrival(ctx, pc, here, link, res)
    if res.interrupt is None:
        _arrive(ctx, pc, arrival)
    return arrival


def continue_move(ctx: TimeContext, arrival: Arrival) -> Arrival:
    """Finish a move an interrupt halted: advance the remainder, then arrive (or halt again)."""
    if arrival.arrived:
        return arrival
    pc = active_pc(ctx.tx.state)
    assert pc is not None
    res = advance_time(ctx, arrival.remainder_rounds, "round", f"travel to {arrival.place} (resumed)")
    out = _arrival(ctx, pc, arrival.from_place, arrival.route, res)
    if res.interrupt is None:
        _arrive(ctx, pc, out)
    return out


def _arrival(ctx: TimeContext, pc: str, here: str | None, link: RouteLink, res: AdvanceResult) -> Arrival:
    state = ctx.tx.state
    e = state.entities[link.to]
    return Arrival(place=link.to, name=e.name, place_kind=str(e.data.get("place_kind", "")), from_place=here,
                   route=link, arrived=res.interrupt is None, mode=entry_mode(state, link.to),
                   interrupt=res.interrupt, remainder_rounds=res.remainder_rounds, narration=res.narration,
                   boundaries=[b.boundary for b in res.boundaries])


def _arrive(ctx: TimeContext, pc: str, arrival: Arrival) -> None:  # rule: 10.1.5
    tx = ctx.tx
    place = arrival.place
    stage(ctx, Event.of("position_set", rule_id="10.1.1", entity=pc, location=place))
    if not is_discovered(tx.state, place):
        if place in tx.state.seals:
            stage(ctx, Event.of("unsealed", rule_id="10.1.5", ref=place, via="arrived", visibility="available"))
        stage(ctx, fact(tx, place, "discovered", True, rule_id="10.1.5", source="data", visibility="available"))
        arrival.discovered_now = True
    if clock.mode_of(tx.state.time.mode) != arrival.mode:
        set_mode(ctx, arrival.mode, f"arrived at {place}")
    arrival.cast_here = cast_at(tx.state, place)
