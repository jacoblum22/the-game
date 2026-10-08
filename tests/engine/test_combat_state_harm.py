"""Playtest 20261008-135049 (fighter), cluster A: combat state and harm. One test per problem, built from the save's
situation (a PC holding, then knifing, a band-4 named NPC in a market; the NPC's crutch hits back)."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

from engine.audit.claims import UNDECIDED, beat_polarity
from engine.dm.adjudication import AdjudicationRecord, BeatEntry, PauseEntry
from engine.dm.scene_state import beat_writes, release_holds
from engine.dm.world_step import exits, foes_act
from engine.harm.apply import apply_harm, go_down, wake
from engine.harm.ctx import HarmCtx, Writes
from engine.resolve.conflict import check_end, start
from engine.resolve.conflict import record as conflict
from engine.store.details import current
from engine.store.events import Event
from engine.time.scheduler import set_mode
from tests.engine.test_turn_adjudication import setup
from tests.fixtures.game import entity

SRC = {"entity": None, "frame_id": None, "effect_id": None}


def _hold(dock: Any, ctx: Any, rec: AdjudicationRecord) -> None:
    """The PC's hold on the ferryman: a Grapple at standard reach, both engaged (T-12-18's success row)."""
    beat = SimpleNamespace(status="resolved", entry=BeatEntry(
        frame_id="frame.1", actor=dock.pc, targets=[dock.ferryman], verb="verb.grapple", restatement="hold Tam",
        degree="failure", success_at_cost=True, reach="standard"))  # a near miss taken as success at a cost
    tx = ctx.need_tx()
    for a, b in ((dock.pc, dock.ferryman), (dock.ferryman, dock.pc)):
        tx.add(Event.of("position_set", rule_id="06.3.5", entity=a, band_to={b: "engaged"}))
    beat_writes(ctx, rec, [beat])


def _held(st: Any, dock: Any) -> tuple[Any, Any]:
    h, p = current(st, dock.pc, "held"), current(st, dock.ferryman, "posture")
    return (h.value if h else None), (p.value if p else None)


def test_a_hold_ends_when_its_holder_goes_down_or_is_moved_away(tmp_path: Path) -> None:
    """Problem 1: "held fast" outlived the grip. 06.5.2: the hold ends if the holder is moved away, or is stunned,
    unconscious or defeated; a held one may still act (her blows alone do not free her)."""
    dock, ctx = setup(tmp_path, None)
    with dock.store.transaction("turn.t") as tx:
        ctx.tx = tx
        rec = AdjudicationRecord(pc=dock.pc)
        _hold(dock, ctx, rec)
        assert _held(tx.state, dock)[1] == "held fast by you"  # a success at a cost is a success (01.9.3)
        release_holds(ctx, rec)
        assert _held(tx.state, dock)[1] == "held fast by you"  # nothing ended it
        hctx = HarmCtx.of(tx, dock.rules)
        w = Writes.of(hctx)
        go_down(hctx, w, dock.pc, cause="a blow", source=SRC)  # the holder is knocked out
        tx.add_all(w.events)
        release_holds(ctx, rec)
        assert _held(tx.state, dock) == (None, None)
        tx.add_all(wake(hctx, dock.pc))  # woken (its `defeated` record stays): a new hold is not undone
        _hold(dock, ctx, rec)
        release_holds(ctx, rec)
        assert _held(tx.state, dock)[1] == "held fast by you"
        ctx.tx = None
    dock2, ctx2 = setup(tmp_path / "b", None)
    with dock2.store.transaction("turn.t") as tx:
        ctx2.tx = tx
        rec = AdjudicationRecord(pc=dock2.pc)
        _hold(dock2, ctx2, rec)
        for a, b in ((dock2.pc, dock2.ferryman), (dock2.ferryman, dock2.pc)):  # she gets a stride away
            tx.add(Event.of("position_set", rule_id="06.9.4", entity=a, band_to={b: "close"}))
        release_holds(ctx2, rec)
        assert _held(tx.state, dock2) == (None, None)
        ctx2.tx = None


def test_an_npc_at_zero_is_out_of_the_fight_and_the_result_line_names_who_was_hit(tmp_path: Path) -> None:
    """Problem 2: the PC's "Vitality 4 → 0" printed under the NPC's strike read as the NPC's. A defeated NPC never
    acts again (06.13.1 able), and the last foe down ends the fight."""
    dock, ctx = setup(tmp_path, None)
    with dock.store.transaction("turn.t") as tx:
        ctx.tx = tx
        rec = AdjudicationRecord(pc=dock.pc)
        start(ctx.time_ctx(), dock.pc, [dock.ferryman], "the PC attacks (06.2.1)")
        for a, b in ((dock.pc, dock.ferryman), (dock.ferryman, dock.pc)):
            tx.add(Event.of("position_set", rule_id="06.3.5", entity=a, band_to={b: "engaged"}))
        oof: list[dict[str, str]] = []
        ctx.rng.d = lambda n, purpose: 19  # type: ignore[method-assign]  # the foe's blow lands
        assert foes_act(ctx, rec, oof) == [dock.ferryman]
        assert oof and oof[0]["text"].startswith("[RESULT] Tam Harlan strikes you · hit · Changed: Vitality 13 →")
        res = apply_harm(HarmCtx.of(tx, dock.rules), dock.ferryman, dealt=99, source=dock.pc)
        tx.add_all(res.events)
        assert res.transition in ("defeated", "dead") and tx.state.fact_value(dock.ferryman, "defeated")
        assert foes_act(ctx, rec, oof) == [] and not conflict(tx.state)  # it does not act; the fight is over
        ctx.tx = None


def test_ending_a_fight_clears_its_record_so_a_conflict_scene_does_not_resume_it(tmp_path: Path) -> None:
    """Problem 4: the PC was knocked out, the fight ended (07.2.9), the scene cut on conflict_end, and the next
    scene, framed in conflict mode, revived the old `meta.conflict`: the foe acted with no conflict_start."""
    dock, ctx = setup(tmp_path, None)
    with dock.store.transaction("turn.t") as tx:
        ctx.tx = tx
        tctx = ctx.time_ctx()
        start(tctx, dock.pc, [dock.ferryman], "the PC attacks (06.2.1)")
        hctx = HarmCtx.of(tx, dock.rules)
        w = Writes.of(hctx)
        go_down(hctx, w, dock.pc, cause="a blow", source=SRC)
        tx.add_all(w.events)
        assert check_end(tctx, dock.pc) and tx.state.meta.get("conflict") is None
        set_mode(tctx, "conflict", "a scene framed as a fight")  # the next scene's own mode
        assert conflict(tx.state) == {}  # nothing live until the PC (or a foe) starts one
        assert foes_act(ctx, AdjudicationRecord(pc=dock.pc), []) == []
        before = tx.state.time.last_boundary.get("conflict_start", 0)
        start(tctx, dock.pc, [dock.ferryman], "the PC attacks again (06.2.1)")
        assert tx.state.time.last_boundary.get("conflict_start", 0) > before  # a fight of its own
        assert conflict(tx.state)["previous"] == "free"  # not "conflict": the end returns to free mode
        ctx.tx = None


def test_a_band_four_npc_who_fights_is_warned_of_and_a_staggered_pc_is_shown_the_exits(tmp_path: Path) -> None:
    """Problem 3: a named NPC who fights takes T-09-3's line for its band; band 4 lists a heavy blow at S4 (the
    save's 12 → 4 was a critical: natural 18 + 10 against Guard, one rung up from S3), so 07.3.3's severity row
    is true and the warning is raised at conflict_start; Staggered raises the exits card (07.3.7)."""
    dock, ctx = setup(tmp_path, None)
    with dock.store.transaction("turn.t") as tx:
        ctx.tx = tx
        ev = entity("npc", "Eliia Terence", tx=tx, data={"band": 4, "depth": "principal"})
        tx.add(ev)
        eliia = ev.payload.entity.id  # type: ignore[attr-defined]
        tx.add(Event.of("position_set", source="test", rule_id="10.1.1", entity=eliia, location=dock.place))
        start(ctx.time_ctx(), dock.pc, [eliia], "the PC attacks (06.2.1)")
        assert conflict(tx.state)["severity"][eliia] == "S4"
        raised = tx.state.meta.get("trg.lethal_warning") or []
        assert [(t["source"], t["cause"]) for t in raised] == [(eliia, "severity")]
        rec = AdjudicationRecord(pc=dock.pc)
        res = apply_harm(HarmCtx.of(tx, dock.rules), dock.pc, dealt=99, source=eliia)
        tx.add_all(res.events)
        assert res.transition == "staggered"
        exits(ctx, rec)
        assert "trg.exits" in rec.triggers  # the narration owes the [STATUS] card
        ctx.tx = None


def test_a_knocked_out_pc_is_told_how_long_it_was_out_and_how_it_stands(tmp_path: Path) -> None:
    """Problem 3: waking from Down said nothing of the time or the PC's state."""
    from engine.dm.turn import _turn_end

    dock, ctx = setup(tmp_path, None)
    with dock.store.transaction("turn.t") as tx:
        ctx.tx = tx
        hctx = HarmCtx.of(tx, dock.rules)
        w = Writes.of(hctx)
        go_down(hctx, w, dock.pc, cause="a blow", source=SRC)
        tx.add_all(w.events)
        rec = AdjudicationRecord(pc=dock.pc)
        oof: list[dict[str, str]] = []
        _turn_end(ctx, rec, oof)
        assert [o["text"] for o in oof] == ["[RESULT] Down: out cold for 10 minutes · you come to where you fell · "
                                            "Now: Vitality 0 of 13 · staggered · prone · the fight is over"]
        assert "the fight is over" in rec.notes[-1]
        ctx.tx = None


def test_outcome_words_are_checked_against_the_degree_and_an_open_near_miss() -> None:
    """Problem 5: "the point stops a finger's width short" passed the outcome scan: the phrase was not a plain
    failure word, and at the near-miss pause the recorded degree (failure) agreed with it although the result was
    still the player's choice (01.9.3)."""
    sac = BeatEntry(frame_id="frame.3", restatement="stab her", rolled=True, degree="failure", near_miss=True,
                    success_at_cost=True)
    open_ = sac.model_copy(update={"success_at_cost": False})
    pause = PauseEntry(kind="near_miss", frame_id="frame.3")
    short = "The point stops a finger's width short of her side."
    assert beat_polarity(short, sac) == "failure"  # a success at a cost is a success
    assert beat_polarity(short, open_, pause) == UNDECIDED
    assert beat_polarity("The blade stops a finger's width from her.", open_, pause) == UNDECIDED
    assert beat_polarity("The blade hangs between you, and the moment holds.", open_, pause) is None
    assert beat_polarity(short, open_) is None  # the failure taken: a miss is right
