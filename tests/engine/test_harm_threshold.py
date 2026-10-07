"""The Threshold and the last-chance menu (07.5; PR-07-5), the Two-Key rule, endings."""

from __future__ import annotations

from pathlib import Path

import pytest

from engine.harm import lethal
from engine.harm.apply import apply_harm
from engine.harm.ctx import Writes
from engine.harm.state import ACTIVE, DEAD, brink, harm_state, wound_load
from engine.harm.threshold import (
    DeathRefused,
    Situation,
    build_menu,
    choose,
    ending_state,
    finish_last_stand,
    h_07_career_end,
    open_threshold,
    resolve_gamble,
    write_death,
)
from engine.store.events import Event
from tests.engine.test_harm_support import FixedDice, ctx, make_game, next_beat, run, vit

WIGHT = ("adversary", "Wight", {"lethal_context": True, "defeat_disposition": "kill"}, 18)
KING = ("npc", "Barrow King", {"can_bargain": True, "want": "the crown returned"}, 0)
SLAVER = ("adversary", "Slaver", {"lethal_context": True, "defeat_disposition": "capture"}, 10)


def at_threshold(tmp_path: Path, others=(WIGHT, KING), source: str = "foe.wight", **kw):
    store = make_game(tmp_path, vitality=1, vmax=13, others=list(others), **kw)
    run(store, lethal.record_warning, lethal.warning_needed(store.state, "pc.wren")[0], sign="a sign")
    next_beat(store)
    for dealt in (5, 8, 8, 5):
        res = run(store, apply_harm, "pc.wren", dealt=dealt, source=source, lethal=True)
    assert res.threshold
    return store


def test_menu_for_the_barrow_wight(tmp_path):
    store = at_threshold(tmp_path)
    sit = Situation(victor="foe.wight", maim_entry="inj.maim.lost_hand")
    op = run(store, open_threshold, "pc.wren", sit)
    offered = [o.id for o in op.menu.offered()]
    assert offered == ["lc.maimed", "lc.bargain", "lc.reprieve", "lc.last_stand", "lc.gamble", "lc.road_ends"]
    reasons = {o.id: o.reason for o in op.menu.options if not o.available}
    assert reasons["lc.captured"] == "the victor's disposition is kill"
    assert reasons["lc.left_for_dead"] == "kill makes sure"
    assert op.menu.bargain == {"bargainer": "npc.barrow_king", "ask": "the crown returned"}
    assert op.menu.gamble == {"free": 5, "live": 35, "choose": 15, "death": 45}  # Endure +2 against 15
    assert op.menu.maim and op.menu.maim["attribute"] == "agility"
    pause = store.state.open_pause()
    assert pause is not None and pause.kind == "last_chance" and pause.default_choice is None
    assert [c["id"] for c in pause.choices] == offered
    assert "THE THRESHOLD — you do not roll to die; you choose." in op.text
    assert store.state.fact_value("pc.wren", "setback.threshold") is not None


def test_no_death_write_without_both_keys(tmp_path):
    store = at_threshold(tmp_path)
    with store.transaction() as tx, pytest.raises(DeathRefused):
        write_death(ctx(tx), "pc.wren", key2="a")
    assert harm_state(store.state, "pc.wren") != DEAD


def test_bargain(tmp_path):
    store = at_threshold(tmp_path)
    op = run(store, open_threshold, "pc.wren", Situation(victor="foe.wight", maim_entry="inj.maim.lost_hand"))
    run(store, choose, "pc.wren", op.menu, "lc.bargain", pause_id=op.pause_id)
    assert harm_state(store.state, "pc.wren") == ACTIVE and vit(store) == 1
    assert brink(store.state, "pc.wren") == 1 and wound_load(store.state, "pc.wren") == 0
    assert store.state.fact_value("pc.wren", "deaths_debt")["ask"] == "the crown returned"
    assert any(c.name == "The debt comes due" for c in store.state.clocks.values())
    assert store.state.open_pause() is None
    assert store.rebuild() == store.state


def test_reprieve_costs_fate_and_no_brink(tmp_path):
    store = at_threshold(tmp_path)
    op = run(store, open_threshold, "pc.wren", Situation(victor="foe.wight", maim_entry="inj.maim.lost_hand"))
    run(store, choose, "pc.wren", op.menu, "lc.reprieve", pause_id=op.pause_id)
    assert vit(store) == 4 and brink(store.state, "pc.wren") == 0  # ceil(13 / 4)
    assert store.state.quantities["pc.wren"]["fate"].current == 0
    assert store.state.fact_value("pc.wren", "reprieves_taken") == 1


def test_maimed(tmp_path):
    store = at_threshold(tmp_path)
    op = run(store, open_threshold, "pc.wren", Situation(victor="foe.wight", maim_entry="inj.maim.lost_hand"))
    run(store, choose, "pc.wren", op.menu, "lc.maimed", pause_id=op.pause_id)
    assert vit(store) == 4 and store.state.fact_value("pc.wren", "attribute_delta.agility") == -1
    assert store.state.fact_value("pc.wren", "maims")[0]["entry"] == "inj.maim.lost_hand"


def test_last_stand_then_death(tmp_path):
    store = at_threshold(tmp_path)
    op = run(store, open_threshold, "pc.wren", Situation(victor="foe.wight", maim_entry="inj.maim.lost_hand"))
    ch = run(store, choose, "pc.wren", op.menu, "lc.last_stand", pause_id=op.pause_id)
    assert ch.last_stand and ending_state(store.state) is None
    run(store, finish_last_stand, "pc.wren", witnesses=["npc.barrow_king"])
    assert harm_state(store.state, "pc.wren") == DEAD and ending_state(store.state) == "death"


@pytest.mark.parametrize(("natural", "result", "ending"), [
    (20, "free", None), (13, "live", None), (10, "choose", None), (9, "death", "death"), (1, "death", "death")])
def test_gamble(tmp_path, natural, result, ending):
    store = at_threshold(tmp_path)
    op = run(store, open_threshold, "pc.wren", Situation(victor="foe.wight", maim_entry="inj.maim.lost_hand"))
    ch = run(store, choose, "pc.wren", op.menu, "lc.gamble", pause_id=op.pause_id)
    assert ch.gamble_offer and ch.gamble_offer["auto_commit"] is False and ch.gamble_offer["lethal"]
    g = run(store, resolve_gamble, "pc.wren", op.menu, rng=FixedDice(natural))
    assert g.result == result and ending_state(store.state) == ending
    if result == "choose":
        assert [c["id"] for c in g.choices] == ["lc.maimed", "lc.bargain"]
        run(store, choose, "pc.wren", op.menu, "lc.maimed", pause_id=g.pause_id, via_gamble=True)
        assert vit(store) == 4 and store.state.open_pause() is None


def test_retire_mode_turns_death_into_the_road_ends(tmp_path):
    store = at_threshold(tmp_path)
    store.append([Event.of("meta_set", key="pref.death.mode", value="retire")])
    op = run(store, open_threshold, "pc.wren", Situation(victor="foe.wight", maim_entry="inj.maim.lost_hand"))
    run(store, choose, "pc.wren", op.menu, "lc.gamble", pause_id=op.pause_id)
    run(store, resolve_gamble, "pc.wren", op.menu, rng=FixedDice(2))
    assert harm_state(store.state, "pc.wren") != DEAD and ending_state(store.state) == "retirement"


def test_captured_and_road_ends(tmp_path):
    store = at_threshold(tmp_path, others=(SLAVER,), source="foe.slaver")
    op = run(store, open_threshold, "pc.wren", Situation(victor="foe.slaver", maim_entry="inj.maim.lost_hand"))
    ids_ = [o.id for o in op.menu.offered()]
    assert "lc.captured" in ids_ and "lc.left_for_dead" in ids_ and "lc.bargain" not in ids_
    run(store, choose, "pc.wren", op.menu, "lc.road_ends", pause_id=op.pause_id)
    assert ending_state(store.state) == "retirement" and vit(store) == 1


def test_strikes_need_a_fact_and_keep_the_menu_valid(tmp_path):
    store = at_threshold(tmp_path, others=(SLAVER,), source="foe.slaver")
    with store.transaction() as tx:
        w = Writes(tx.state, tx.mint)
        fid = w.fact("foe.slaver", "quarter_refused", True, rule_id="test")
        tx.add_all(w.events)
    assert fid is not None
    with store.transaction() as tx:
        menu = build_menu(ctx(tx), "pc.wren", Situation(victor="foe.slaver", maim_entry="inj.maim.lost_hand",
                                                        strikes={"lc.captured": fid, "lc.maimed": fid,
                                                                 "lc.left_for_dead": "fact.999"}))
    by = {o.id: o for o in menu.options}
    assert by["lc.captured"].struck_by == fid
    assert by["lc.maimed"].available  # empty struck_when list: the strike is refused
    assert by["lc.left_for_dead"].available  # no such fact: refused
    assert set(menu.refused_strikes) == {"lc.maimed", "lc.left_for_dead"}


def test_career_end_handler(tmp_path):
    store = make_game(tmp_path)
    with store.transaction() as tx:
        w = Writes(tx.state, tx.mint)
        w.fact("pc.wren", "career_end", True, rule_id="07.11.6")
        tx.add_all(w.events)
    assert ending_state(store.state) is None
    run(store, h_07_career_end, boundary="scene_end")
    assert ending_state(store.state) == "career_end"
