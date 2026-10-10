"""T060 (Director half): the Director role's enums, call and scene framing (PR-12-7) on the dock fixture."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from engine.dm.roles.director import direct, director_context, frame_scene, scene_header
from engine.dm.schemas import build_schema, prune
from engine.llm.base import Role
from engine.llm.offline import ScriptedModel, enum_at
from engine.world.common import raise_trigger
from tests.engine.test_turn_adjudication import setup


def answer(place: str, *, cut: bool = False, push: str | None = None, **ns: Any) -> Any:
    def fill(schema: dict[str, Any], packet: Any) -> dict[str, Any]:
        nxt = {"mode": "site", "place": place, "agenda": "Does the ferryman talk?", "hoped_answer": "yes",
               "pillar": enum_at(schema, "next_scene", "pillar")[0], "challenge_type": None, "cast": [],
               "cast_described": []}
        nxt.update(ns)
        return prune({"cut_now": cut, "next_scene": nxt, "push": push or "none", "lead": None}, schema)

    return fill


def test_director_enums_come_from_the_world(tmp_path: Path) -> None:
    dock, ctx = setup(tmp_path, ScriptedModel())
    sctx = director_context(dock.state, dock.rules)
    assert sctx.places[0] == dock.place and sctx.current_place == dock.place
    assert "site" in sctx.modes and sctx.previous_mode == "site" and dock.ferryman in sctx.known_ids
    schema = build_schema(Role.DIRECTOR, sctx)
    assert "push" not in schema["properties"] and "lead" not in schema["properties"]  # nothing raised


def test_direct_reads_the_decision_and_sends_the_quiet_count(tmp_path: Path) -> None:
    model = ScriptedModel()
    dock, ctx = setup(tmp_path, model)
    model.push(Role.DIRECTOR, answer(dock.place, cut=True, cast=[dock.ferryman]))
    with dock.store.transaction("turn.1") as tx:
        ctx.tx = tx
        d = direct(ctx, situation="a possible cut", player_message="I leave.", quiet_turns=2)
        ctx.tx = None
    assert d.cut_now and d.next_scene.place == dock.place and d.next_scene.cast == [dock.ferryman]
    packet = model.calls[0][1]
    assert "quiet_turns: 2" in packet.view and 'THE PLAYER\'S MESSAGE: "I leave."' in packet.message


def test_push_is_offered_only_when_raised(tmp_path: Path) -> None:
    model = ScriptedModel()
    dock, ctx = setup(tmp_path, model)
    with dock.store.transaction() as tx:
        tx.add(raise_trigger(tx, "trg.pacing_push", {"reason": "flatline"}, rule_id="12.7.2"))
    sctx = director_context(dock.state, dock.rules)
    assert sctx.push_options
    model.push(Role.DIRECTOR, answer(dock.place, push=sctx.push_options[0]))
    with dock.store.transaction("turn.1") as tx:
        ctx.tx = tx
        d = direct(ctx, situation="scene start")
        ctx.tx = None
    assert d.push_raised and d.push == sctx.push_options[0]


def test_frame_scene_ends_the_current_scene_and_starts_the_next(tmp_path: Path) -> None:
    model = ScriptedModel()
    dock, ctx = setup(tmp_path, model)
    model.push(Role.DIRECTOR, answer(dock.place, cut=True, cast=[dock.ferryman], agenda="Who rows tonight?"))
    with dock.store.transaction("turn.1") as tx:
        ctx.tx = tx
        d = direct(ctx, situation="a cut")
        start = frame_scene(ctx, d, reason="player_cut")
        header = scene_header(ctx.state)
        ctx.tx = None
    st = dock.state
    assert st.scene is not None and st.scene.scene_id == start.scene_id != dock.scene
    assert st.last_scene is not None and st.last_scene.scene_id == dock.scene
    assert st.scene.agenda == "Who rows tonight?" and dock.ferryman in st.scene.cast_present
    assert header.startswith("The Night Dock")
    types = [e.type for e in dock.store.events() if e.turn_id == "turn.1"]
    assert types.index("scene_ended") < types.index("scene_started")
    assert dock.store.rebuild() == dock.state
