"""Pacing (T062): tension, the inconclusive streak and lead injection, the push, random events, rotation and the
live-lead audit."""

from __future__ import annotations

from pathlib import Path

from engine.retrieve.triggers import get_active_triggers
from engine.store.events import Event
from engine.time.scheduler import mark_boundary
from engine.world import pacing, places, scenes, social
from engine.world.common import meta
from tests.engine.test_world_support import Game


def _scene(g: Game, **kw: object) -> scenes.SceneStart:
    args = {"place": places.location(g.state), "mode": "free", "agenda": "Does it work?", "hoped_answer": "yes"} | kw
    return g.run(lambda ctx: scenes.start_scene(ctx, **args))  # type: ignore[arg-type]


def test_tension_rises_on_chaos_and_clamps(tmp_path: Path) -> None:
    g = Game(tmp_path)
    assert pacing.tension(g.state, g.rules) == 5
    for want in (6, 7, 8, 9, 9):
        _scene(g, mode="conflict")  # untested: no scene-test points
        g.run(lambda ctx: scenes.end_scene(ctx, "agenda_answered", answered="against_hope"))
        assert pacing.tension(g.state, g.rules) == want
    _scene(g, mode="conflict")
    chaos, control = g.run(lambda ctx: pacing.tension_points(ctx.tx, ctx.rules))
    assert chaos == [] and control == []
    g.run(lambda ctx: scenes.end_scene(ctx, "player_cut"))  # a tie holds
    assert pacing.tension(g.state, g.rules) == 9


def test_tension_reads_costs_and_standing_from_the_scene_log(tmp_path: Path) -> None:
    g = Game(tmp_path)
    _scene(g, mode="conflict")
    nid = g.world.cast[-1].id

    def writes(ctx: object) -> None:
        tx = ctx.tx  # type: ignore[attr-defined]
        tx.add(Event.of("frame_committed", frame_id="frame.1", frame={"verb": "verb.talk"}))
        tx.add(Event.of("frame_resolved", frame_id="frame.1", degree="failure",
                        costs=[{"menu_id": "cost.harm", "severity": "S3", "form": "x"}]))
        tx.add(Event.of("relationship_set", a=nid, b=g.pc, kind="standing", value=0, new_value=0, reason="t"))
        tx.add(Event.of("relationship_set", a=nid, b=g.pc, kind="standing", steps=1, new_value=1, reason="t"))
    g.run(writes)
    chaos, control = g.run(lambda ctx: pacing.tension_points(ctx.tx, ctx.rules))
    rules = g.rules.pacing["tension"]["rules"]
    assert chaos == [rules["chaos_points"][2]] and control == [rules["control_points"][4]]


def test_inconclusive_streak_raises_lead_injection_and_injection_resets(tmp_path: Path) -> None:
    g = Game(tmp_path)
    _scene(g, mode="conflict")
    for n in (1, 2):
        g.run(lambda ctx: mark_boundary(ctx, "beat_end"))
        assert g.state.meta["inconclusive"]["count"] == n
    g.run(lambda ctx: ctx.tx.add(Event.of("position_set", entity=g.pc, location=places.location(ctx.tx.state))))
    g.run(lambda ctx: mark_boundary(ctx, "beat_end"))
    assert g.state.meta["inconclusive"]["count"] == 0  # a position change is conclusive
    for _ in range(3):
        g.run(lambda ctx: mark_boundary(ctx, "beat_end"))
    assert "trg.lead_injection" in [t.id for t in get_active_triggers(g.state)]
    en = scenes.director_enums(g.state, g.rules)
    assert en["lead_fires"] and en["lead_routes"][0] == "unfound_clue_of_scene_thread"
    lead = g.run(pacing.inject_lead)
    assert lead.source_rung == "unfound_clue_of_other_active_thread_by_weight"  # the seed's lead threads
    assert lead.thread in g.threads.values() and lead.form and lead.facts
    assert g.state.knowledge[g.pc][lead.facts[0]].how
    assert "trg.lead_injection" not in [t.id for t in get_active_triggers(g.state)]
    assert g.state.meta["inconclusive"]["count"] == 0
    assert g.store.rebuild() == g.state


def test_lead_injection_falls_through_to_a_clock_trace(tmp_path: Path) -> None:
    g = Game(tmp_path)
    _scene(g, mode="conflict")
    for t in g.threads.values():  # no thread leads left
        g.run(lambda ctx, t=t: social.set_thread_status(ctx, t, "resolved"))
    lead = g.run(pacing.inject_lead)
    assert lead.source_rung == "most_advanced_opposition_clock_omen_as_trace"
    assert lead.source_id in g.state.clocks
    assert pacing.clock_trace(g.state, lead.source_id)


def test_pacing_push_fires_at_scene_start(tmp_path: Path) -> None:
    g = Game(tmp_path)
    g.run(lambda ctx: pacing.raise_push(ctx, "flatline"))
    assert scenes.director_enums(g.state, g.rules)["push_options"] == list(g.rules.pacing["push"]["candidates"])
    st = _scene(g)
    assert st.push is not None and st.push["candidate"] == "tbl.vignette" and st.push["entry"]
    assert "trg.pacing_push" not in [t.id for t in get_active_triggers(g.state)]
    g.run(lambda ctx: scenes.end_scene(ctx, "player_cut"))
    g.run(lambda ctx: ctx.tx.add_all([meta("pacing.phase", "peak", "test")]))
    g.run(lambda ctx: pacing.raise_push(ctx, "flatline"))
    assert _scene(g, mode="conflict").push is None  # PEAK holds the push


def test_random_event_focus_target_and_phase(tmp_path: Path) -> None:
    g = Game(tmp_path)
    _scene(g, mode="conflict")
    foci = set()
    for _ in range(40):
        ev = g.run(lambda ctx: pacing.random_event(ctx, source="interrupted_scene"))
        foci.add(ev.focus)
        assert len(ev.meaning) == 2
        if ev.target_list == "thread":
            assert ev.target in g.threads.values()
        if ev.target_list == "cast":
            assert ev.target in social.cast_list(g.state)
        assert not (ev.focus == "NPC action" and ev.target is None)
    assert "new NPC" in foci  # the empty cast list reads as a new NPC
    g.run(lambda ctx: ctx.tx.add(meta("pacing.phase", "relax", "test")))
    for _ in range(40):
        ev = g.run(lambda ctx: pacing.random_event(ctx, source="interrupted_scene"))
        assert ev.focus not in ("PC complication", "thread complicates")


def test_rotation_and_lead_audit(tmp_path: Path) -> None:
    g = Game(tmp_path)
    _scene(g, pillar="social", challenge_type="mystery")
    g.run(lambda ctx: scenes.end_scene(ctx, "player_cut"))
    rot = pacing.rotation(g.state, g.rules)
    assert rot["pillar"]["social"] == 0 and rot["pillar"]["travel"] == 2
    assert rot["challenge_type"]["mystery"] == 0
    # a thread whose node has been tried, with no clue and no fallback, stalls
    thr = next(iter(g.threads.values()))
    node = g.state.entities[thr].data["points_to"]
    _scene(g, agenda="again")
    g.run(lambda ctx: pacing.mark_tried(ctx, thr, node))
    g.run(lambda ctx: scenes.end_scene(ctx, "player_cut"))
    assert g.state.fact_value(thr, "stalled") is True
    assert thr in g.state.meta["fallback_queue"]
    assert g.store.rebuild() == g.state
