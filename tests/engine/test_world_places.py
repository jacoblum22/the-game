"""The place graph (T059): seeding, reachability, moves that advance time and fire boundaries."""

from __future__ import annotations

from collections import deque
from pathlib import Path

import pytest

from engine.time import clock
from engine.world import places, scenes
from engine.world.common import WorldError
from tests.engine.test_world_support import Game


@pytest.mark.parametrize("seed", [7, 1, 42])
def test_graph_loads_and_is_connected(tmp_path: Path, seed: int) -> None:
    g = Game(tmp_path, seed)
    st = g.state
    for p in g.world.places:
        assert st.entities[p.id].kind == "place"
        assert st.entities[p.id].data["place_kind"] == p.kind
    for r in g.world.routes:  # every route is a link fact both ways
        assert st.current_fact_id(r.a, places.LINK + r.id) and st.current_fact_id(r.b, places.LINK + r.id)
        assert st.fact_value(r.a, places.LINK + r.id)["travel_watches"] == r.watches
    # breadth-first over known links from the haven reaches every place a known route touches
    haven = g.world.region.haven
    seen, todo = {haven}, deque([haven])
    while todo:
        for link in places.reachable(st, todo.popleft()):
            if link.to not in seen:
                seen.add(link.to)
                todo.append(link.to)
    known_ends = {x for r in g.world.routes if r.known for x in (r.a, r.b)}
    assert known_ends <= seen
    assert g.world.incident.place in seen
    assert g.store.rebuild() == st
    # threads, factions, clocks and the cast are in the store
    assert {st.entities[t].kind for t in g.threads.values()} == {"thread"}
    assert all(f.id in st.entities for f in g.world.factions)
    assert all(c["id"] in st.clocks for c in g.world.record["clocks"])
    assert all(n.id in st.entities for n in g.world.cast)


def test_undiscovered_place_is_sealed_with_a_name_slice(tmp_path: Path) -> None:
    g = Game(tmp_path)
    hidden = [p for p in g.world.places if not p.discovered]
    assert hidden
    for p in hidden:
        seal = g.state.seals[p.id]
        assert seal.gate == places.UNDISCOVERED_GATE
        assert seal.slice == (p.name if p.known else None)
        assert not places.is_discovered(g.state, p.id)


def test_reachable_includes_buildings_and_unknown_routes_are_not(tmp_path: Path) -> None:
    g = Game(tmp_path)
    haven = g.world.region.haven
    ids = {x.to: x for x in places.reachable(g.state, haven)}
    buildings = [p.id for p in g.world.places if p.kind == "building" and p.parent == haven]
    assert set(buildings) <= set(ids)
    assert all(ids[b].route_kind == "passage" and ids[b].unit == "interval" for b in buildings)
    unknown = [r for r in g.world.routes if not r.known]
    assert unknown
    for r in unknown:
        assert r.id not in {x.route for x in places.reachable(g.state, r.a)}
        assert g.state.current_fact_id(r.a, places.LINK + r.id) in g.state.seals


def test_move_advances_time_by_route_and_fires_boundaries(tmp_path: Path) -> None:
    g = Game(tmp_path)
    haven = g.world.region.haven
    g.run(lambda ctx: places.move(ctx, haven))  # out of the inn: a one-interval passage
    route = next(x for x in places.reachable(g.state, haven) if x.unit == "watch")
    before = clock.to_rounds(g.state.time.now)
    seq0 = g.store.last_seq
    a = g.run(lambda ctx: places.move(ctx, route.to))
    assert a.arrived and a.place == route.to and a.route.route == route.route
    assert clock.to_rounds(g.state.time.now) - before == route.length * clock.ROUNDS["watch"]
    assert g.state.positions[g.pc].location == route.to
    assert "watch" in a.boundaries
    evs = list(g.store.events(since=seq0))
    assert any(e.type == "boundary_marked" and e.payload_json()["boundary"] == "mode_change" for e in evs)  # travel, then free
    skipped = {e.payload_json()["handler_id"] for e in evs if e.type == "handler_skipped"}
    assert "h.10.travel_progress" in skipped  # ch.10's travel handlers are Milestone 4
    assert clock.mode_of(g.state.time.mode) == a.mode == "free"
    assert g.store.rebuild() == g.state


def test_move_ends_the_scene_and_discovers(tmp_path: Path) -> None:
    g = Game(tmp_path)
    haven = g.world.region.haven
    g.run(lambda ctx: places.move(ctx, haven))
    # walk until a reachable undiscovered place is in sight
    target = None
    for _ in range(4):
        here = places.location(g.state)
        target = next((x.to for x in places.reachable(g.state, here) if not places.is_discovered(g.state, x.to)), None)
        if target:
            break
        nxt = next(x.to for x in places.reachable(g.state, here) if x.unit == "watch")
        g.run(lambda ctx, n=nxt: places.move(ctx, n))
    assert target is not None
    g.run(lambda ctx: scenes.start_scene(ctx, place=places.location(ctx.tx.state), mode="free", agenda="Go?"))
    a = g.run(lambda ctx: places.move(ctx, target))
    assert a.discovered_now and places.is_discovered(g.state, target)
    assert target not in g.state.seals
    assert g.state.scene is None and g.state.last_scene is not None
    ended = list(g.store.events(types=["scene_ended"]))[-1]
    assert ended.payload_json()["reason"] == "place_change"


def test_move_refuses_an_unreachable_place(tmp_path: Path) -> None:
    g = Game(tmp_path)
    far = next(p.id for p in g.world.places if p.ring == 5)
    with pytest.raises(WorldError):
        g.run(lambda ctx: places.move(ctx, far))
