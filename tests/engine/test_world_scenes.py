"""Scenes (T060, deterministic half): start and end events, the scene test, counters, cut detection, the
Director's enums."""

from __future__ import annotations

from pathlib import Path

from engine.dm.schemas import SchemaContext, director_schema, schema_context
from engine.llm.base import validate
from engine.store.events import Event
from engine.time.scheduler import advance_time, mark_boundary
from engine.world import places, scenes
from engine.world.common import meta
from tests.engine.test_world_support import Game


def _start(g: Game, **kw: object) -> scenes.SceneStart:
    args = {"place": places.location(g.state), "mode": "free", "agenda": "Does the innkeeper talk?",
            "hoped_answer": "yes", "pillar": "social"} | kw
    return g.run(lambda ctx: scenes.start_scene(ctx, **args))  # type: ignore[arg-type]


def test_scene_start_and_end_write_events_and_run_handlers(tmp_path: Path) -> None:
    g = Game(tmp_path)
    seq0 = g.store.last_seq
    st = _start(g, expected="Wren finds the innkeeper behind the bar", purpose_declared=True)
    assert st.scene_id == "scn.1" and g.state.scene is not None and g.state.scene.scene_id == "scn.1"
    assert st.test["result"] in ("expected", "altered", "interrupted")
    assert set(scenes.cast_present(g.state)) >= {n.id for n in g.world.cast if n.home == g.world.incident.place}
    end = g.run(lambda ctx: scenes.end_scene(ctx, "agenda_answered", answered="as_hoped"))
    assert g.state.scene is None and g.state.last_scene and g.state.last_scene.ended_at is not None
    evs = list(g.store.events(since=seq0))
    types = [e.type for e in evs]
    assert types.index("scene_started") < types.index("scene_ended")
    marked = [e.payload_json()["boundary"] for e in evs if e.type == "boundary_marked"]
    assert "scene_start" in marked and "scene_end" in marked
    ran = {e.payload_json()["handler_id"] for e in evs if e.type == "handler_ran"}
    assert {"h.12.scene_test", "h.12.pacing_push", "h.12.tension_update", "h.12.lead_audit", "h.12.rotation_update",
            "h.12.npc_memory", "h.12.bookkeeping", "h.15.patience_reset"} <= ran
    # answered as hoped + a declared purpose tested expected: control points; tension falls (or holds on deviation)
    assert end.tension in (4, 5)
    assert g.store.rebuild() == g.state


def test_untested_scenes(tmp_path: Path) -> None:
    g = Game(tmp_path)
    assert _start(g, mode="conflict").test == {"scene_id": "scn.1", "result": "untested", "reason": "conflict"}
    g.run(lambda ctx: scenes.end_scene(ctx, "conflict_end"))
    st = _start(g)  # same place, no time passed: a direct continuation
    assert st.test["reason"] == "direct_continuation_under_one_interval"
    g.run(lambda ctx: scenes.end_scene(ctx, "player_cut"))
    assert _start(g, interrupt=True).test["reason"] == "interrupt_scene"


def test_scene_test_deviates_by_tension(tmp_path: Path) -> None:
    g = Game(tmp_path)
    seen = set()
    for i in range(30):
        g.run(lambda ctx: ctx.tx.add(meta("tension", 9, "test")))
        g.run(lambda ctx: advance_time(ctx, 1, "hour", "wait"))  # not a direct continuation
        st = _start(g, agenda=f"q{i}")
        t = st.test
        assert t["tension"] == 9
        dev = t["roll"] <= 6
        assert t["result"] == ("expected" if not dev else "altered" if t["roll"] % 2 else "interrupted")
        if t["result"] == "altered":
            assert t["adjustments"] and all(a != "two adjustments" for a in t["adjustments"])
        if t["result"] == "interrupted":
            assert t["event"]["focus"] and len(t["event"]["meaning"]) == 2
        seen.add(t["result"])
        g.run(lambda ctx: scenes.end_scene(ctx, "player_cut"))
    assert seen == {"expected", "altered", "interrupted"}
    assert g.store.rebuild() == g.state


def test_cut_detection(tmp_path: Path) -> None:
    g = Game(tmp_path)
    r = g.rules
    _start(g)
    assert scenes.cut_due(g.state, r) is None
    assert g.run(lambda ctx: scenes.note_turn(ctx, quiet=True)) == 1
    assert scenes.cut_due(g.state, r) is None
    g.run(lambda ctx: scenes.note_turn(ctx, quiet=True))
    assert scenes.cut_due(g.state, r) == "dead_air"
    g.run(lambda ctx: scenes.note_turn(ctx, quiet=False))
    assert scenes.cut_due(g.state, r) is None
    g.run(lambda ctx: scenes.note_cut(ctx, "player_cut"))
    assert scenes.cut_due(g.state, r) == "player_cut"
    g.run(lambda ctx: advance_time(ctx, 1, "hour", "talk"))
    assert scenes.cut_due(g.state, r) == "time_jump"
    g.run(lambda ctx: scenes.mark_agenda_answered(ctx, "against_hope"))
    assert scenes.cut_due(g.state, r) == "agenda_answered"
    g.run(lambda ctx: scenes.end_scene(ctx, "agenda_answered"))
    _start(g, agenda="next")
    g.run(lambda ctx: ctx.tx.add(Event.of("position_set", entity=g.pc, location=g.world.region.haven)))
    assert scenes.cut_due(g.state, r) == "place_change"


def test_conflict_end_cuts(tmp_path: Path) -> None:
    g = Game(tmp_path)
    _start(g, mode="conflict")
    g.run(lambda ctx: mark_boundary(ctx, "conflict_end"))
    assert scenes.cut_due(g.state, g.rules) == "conflict_end"


def test_turn_is_quiet() -> None:
    t = Event.of("time_advanced", {"from": {}}, to={}, boundaries=[])
    f = Event.of("fact_set", {"source": "narration"}, fact_id="fact.1", subject="world", predicate="p", value=1)
    assert scenes.turn_is_quiet(["SPEECH"], [t])
    assert not scenes.turn_is_quiet(["SPEECH"], [t, f])
    assert not scenes.turn_is_quiet(["DECLARATION"], [t])


def test_reopen_keeps_the_id(tmp_path: Path) -> None:
    g = Game(tmp_path)
    sid = _start(g).scene_id
    g.run(lambda ctx: scenes.end_scene(ctx, "agenda_answered"))
    assert g.run(scenes.reopen_scene) == sid
    assert g.state.scene is not None and g.state.scene.scene_id == sid
    assert g.store.rebuild() == g.state


def test_director_enums_fit_the_schema(tmp_path: Path) -> None:
    g = Game(tmp_path)
    _start(g)
    en = scenes.director_enums(g.state, g.rules)
    fields = set(SchemaContext.model_fields)
    assert {k for k in en if k not in ("push_raised", "lead_fires")} <= fields
    here = places.location(g.state)
    assert en["current_place"] == here and en["places"][0] == here
    assert set(en["places"][1:]) == {x.to for x in places.reachable(g.state, here)}
    assert en["challenge_types"][0] == "terrain" and "social" in en["pillars"]
    assert set(en["thread_ids"]) == set(g.threads.values())
    assert en["push_options"] == [] and en["lead_routes"] == []
    ctx = schema_context(g.state, g.rules, places=en["places"], push_raised=en["push_raised"],
                         lead_fires=en["lead_fires"])
    schema = director_schema(ctx)
    ok = {"cut_now": False, "next_scene": {"mode": "free", "place": en["places"][1], "agenda": "a", "hoped_answer": "",
                                           "pillar": "social", "challenge_type": None, "cast": []}}
    assert validate(ok, schema) == []
    bad = {**ok, "next_scene": {**ok["next_scene"], "place": "loc.nowhere"}}
    assert validate(bad, schema)
