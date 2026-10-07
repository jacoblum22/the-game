"""Golden tests from ch.07's worked examples, with fixed dice (T054). Milestone 1 runs wounds coarsely (no wound
records, so no maximum-Vitality penalties; PR-07-2 is M2) and does not track dread (M2): where a figure in the
example comes from a wound record or dread, the test says so and checks the M1 figure the rules give without it.

WE-07-3 (a poison's stages) and WE-07-6 (bleeding out; a dread break) are M2 (afflictions, companions, dread).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from engine.abilities.recharge import h_05_focus_recover
from engine.harm import lethal
from engine.harm.apply import apply_harm, dying_check, status_block
from engine.harm.ctx import Writes
from engine.harm.exits import commit_retreat, commit_yield, retreat_offer, yield_answer
from engine.harm.rest import h_07_natural_recovery, h_07_rest_recovery, rest_payload, rest_quality
from engine.harm.state import (
    ACTIVE,
    DYING,
    STAGGERED,
    View,
    brink,
    defeated_manner,
    descriptor,
    dying_step,
    harm_state,
    wound_load,
)
from engine.harm.threshold import DeathRefused, Situation, choose, open_threshold, write_death
from engine.store.events import Event, PositionSet
from tests.engine.test_harm_support import RULES, FixedDice, ctx, make_game, next_beat, run, vit

WIGHT = ("adversary", "Barrow-wight", {"threat_advisory": "lethal", "lethal_context": True,
                                        "defeat_disposition": "kill", "attacks": [{"name": "grave-touch",
                                                                                    "severity": "S3"}]}, 18)
KING = ("npc", "Barrow King", {"can_bargain": True, "want": "return the crown of the Ninefold Barrow to its head"}, 0)
WREN = {"reduction": 1, "attributes": {"endurance": 2, "agility": 3}}  # a padded jack; Endure +2; Agility +3


def frost(store, dealt: int, lethal_: bool = True):
    return run(store, apply_harm, "pc.wren", dealt=dealt, harm_tags=["harm.frost"], source="foe.barrow_wight",
               lethal=lethal_)


def barrow(tmp_path: Path, *, warn: bool = True):
    store = make_game(tmp_path, vitality=13, fate=1, pc_data=WREN, others=[WIGHT, KING])
    if warn:
        trig = lethal.warning_needed(store.state, "pc.wren")
        assert [(t.source, t.cause) for t in trig] == [("foe.barrow_wight", "advisory")]  # the first true cause
        text = lethal.warning_block(RULES, trig[0], source_name="the barrow-wight", fate=1,
                                    yield_text="not accepted (it does not understand quarter)",
                                    retreat_text="clean: it is slower than you; nothing to pay")
        assert text.splitlines()[0] == ("[WARNING] THIS CAN KILL YOU — the barrow-wight. "
                                        "As things stand you are unlikely to win this.")
        run(store, lethal.record_warning, trig[0], sign="Frost creeps across the grave-goods toward your boots")
    next_beat(store)  # Wren's first declaration: the context is effective from here
    return store


def test_we_07_1_the_ninefold_barrow(tmp_path):
    store = barrow(tmp_path)
    # Rounds 1-2: frost is not reduced by the jack.
    frost(store, 5)
    assert (vit(store), descriptor(store.state, "pc.wren")) == (8, "worn")
    frost(store, 5)
    assert (vit(store), descriptor(store.state, "pc.wren")) == (3, "bloodied")
    res = frost(store, 5)
    assert vit(store) == 0 and res.breakdown["discarded"] == 2 and harm_state(store.state, "pc.wren") == STAGGERED
    assert "at wound load 3 you fall to Dying. Load 0/3." in (status_block(RULES, View(store.state), "pc.wren") or "")
    # Round 3: a Heavy wound (load 2), then a natural 20: one rung heavier, S4 = 8: load 5 -> Dying 1.
    assert frost(store, 5).load == 2
    res = frost(store, 8)
    assert res.transition == "dying" and dying_step(store.state, "pc.wren") == 1
    assert any("you need 8 or better; 65%" in o for o in res.obligations)
    # Round 4: the dying check d20 5 + 2 = 7 against 10: a failure by 3 -> holds; a hit -> Dying 2.
    assert run(store, dying_check, "pc.wren", rng=FixedDice(5)).result == "holds"
    frost(store, 5)
    assert dying_step(store.state, "pc.wren") == 2
    # Round 5: d20 9 + 2 = 11 against 15: a failure by 4 -> Dying 3; a hit -> the Threshold.
    assert run(store, dying_check, "pc.wren", rng=FixedDice(9)).result == "step_up"
    res = frost(store, 5)
    assert res.threshold and dying_step(store.state, "pc.wren") == 3 and harm_state(store.state, "pc.wren") == DYING
    # The menu. She is cornered in the niche; no companion. Maim: tbl.wound_site d12 2 (arm), d2 1 (Lost hand).
    store.append([Event(type="position_set", payload=PositionSet(entity="pc.wren", flags_add=["flag.cornered"]))])
    op = run(store, open_threshold, "pc.wren", Situation(victor="foe.barrow_wight"), rng=FixedDice(2, 1))
    by = {o.id: o for o in op.menu.options}
    assert [o.id for o in op.menu.offered()] == ["lc.maimed", "lc.bargain", "lc.reprieve", "lc.last_stand",
                                                 "lc.gamble", "lc.road_ends"]
    assert not by["lc.captured"].available and not by["lc.left_for_dead"].available and not by["lc.rout"].available
    assert op.menu.maim == {"entry": "inj.maim.lost_hand", "name": "Lost hand", "attribute": "agility",
                            "text": "Agility -1 (else Might). No method that needs two hands."}
    # (the example stands her at Vitality 2, a quarter of her wound-lowered maximum 7; M1 has no wound penalty)
    assert "you stand at Vitality 4" in by["lc.maimed"].price
    assert op.menu.bargain == {"bargainer": "npc.barrow_king",
                               "ask": "return the crown of the Ninefold Barrow to its head"}
    assert by["lc.reprieve"].price == "fate 1 of 1; you stand at Vitality 4"
    assert op.menu.gamble == {"free": 5, "live": 35, "choose": 15, "death": 45}
    assert sum(1 for o in op.menu.offered() if not o.death) == 4
    # The two keys: Key 1 holds, Key 2 does not: the engine refuses a death write.
    assert store.state.fact_value("pc.wren", "lethal_key", "").startswith("lc.")
    with store.transaction() as tx, pytest.raises(DeathRefused):
        write_death(ctx(tx), "pc.wren", key2="a")
    # The choice: the Bargain.
    run(store, choose, "pc.wren", op.menu, "lc.bargain", pause_id=op.pause_id)
    assert harm_state(store.state, "pc.wren") == ACTIVE and vit(store) == 1  # stabilized, Vitality 1
    assert brink(store.state, "pc.wren") == 1 and wound_load(store.state, "pc.wren") == 0
    assert any(c.name == "The debt comes due" and c.filled == 0 and c.segments == 8
               for c in store.state.clocks.values())
    assert store.state.open_pause() is None and store.rebuild() == store.state


def test_we_07_1_boundary_the_reprieve(tmp_path):
    store = barrow(tmp_path)
    for d in (5, 5, 5, 5, 8):
        frost(store, d)
    for n in (5, 9):
        run(store, dying_check, "pc.wren", rng=FixedDice(n))
        frost(store, 5)
    op = run(store, open_threshold, "pc.wren", Situation(victor="foe.barrow_wight", maim_entry="inj.maim.lost_hand"))
    run(store, choose, "pc.wren", op.menu, "lc.reprieve", pause_id=op.pause_id)
    assert store.state.quantities["pc.wren"]["fate"].current == 0 and brink(store.state, "pc.wren") == 0
    assert wound_load(store.state, "pc.wren") == 0 and harm_state(store.state, "pc.wren") == ACTIVE
    assert store.state.fact_value("pc.wren", "reprieves_taken") == 1  # the next costs 2


def test_we_07_1_other_side_no_key_1(tmp_path):
    store = barrow(tmp_path, warn=False)
    for d in (5, 5, 5, 5):
        frost(store, d)
    res = frost(store, 8)
    assert res.lethal is False and res.transition == "down" and defeated_manner(store.state, "pc.wren") == "down"


def test_we_07_2_the_tarn_bridge(tmp_path):
    store = make_game(tmp_path, vitality=4, vmax=12, pc_data=WREN)
    # The fall: S4 crush, no reduction, lethal: true asked and refused (no context): 8 -> 0, excess 4 discarded.
    res = run(store, apply_harm, "pc.wren", severity="S4", harm_tags=["harm.physical.crush"], source="haz.bridge",
              lethal=True, no_reduction=True)
    assert res.lethal is False and res.lethal_refused and res.amount == 8 and res.breakdown["discarded"] == 4
    assert harm_state(store.state, "pc.wren") == STAGGERED
    # The river: 5 (the weight of water: no reduction) -> Heavy, load 2.
    res = run(store, apply_harm, "pc.wren", dealt=5, source="haz.river", no_reduction=True)
    assert res.load == 2
    # A periodic tick, a critical failure one rung heavier: 8 -> load 5, not lethal -> Down; no record.
    res = run(store, apply_harm, "pc.wren", dealt=8, source="haz.river", no_reduction=True, periodic=True)
    assert res.transition == "down" and res.wound == {"severity": "S4", "load": 3, "record": None}


def test_we_07_2_boundary_had_she_looked(tmp_path):
    bridge = ("object", "Tarn bridge", {"hazard": {"severity": "S4", "lethal_context": True}}, 0)
    store = make_game(tmp_path, vitality=4, vmax=12, pc_data=WREN, others=[bridge])
    trig = lethal.warning_needed(store.state, "pc.wren")[0]
    assert trig.cause == "severity"
    text = lethal.warning_block(RULES, trig, source_name="the bridge over the Tarn: a forty-foot drop", fate=1,
                                yield_text="—", retreat_text="—")
    assert text.startswith("[WARNING] THIS CAN KILL YOU — the bridge over the Tarn: a forty-foot drop. "
                           "A Grievous danger.")
    run(store, lethal.record_warning, trig, sign="the gorge drops away sixty feet")
    next_beat(store)
    res = run(store, apply_harm, "pc.wren", severity="S4", source="obj.tarn_bridge", lethal=True, no_reduction=True)
    assert res.lethal and vit(store) == 0 and res.transition == "staggered"  # even warned, the fall alone cannot kill


def test_we_07_4_taken_in_the_reeds(tmp_path):
    rider = {"defeat_disposition": "capture", "threat_advisory": "hard", "lethal_context": False}
    store = make_game(tmp_path, vitality=2, vmax=12, pc_data=WREN,
                      others=[("adversary", "Guild rider", rider, 10)])
    assert lethal.warning_needed(store.state, "pc.wren") == []
    assert lethal.danger_notice(store.state, "pc.wren", "foe.guild_rider", "being taken alive by the Guild") == \
        "[WARNING] A hard fight — you may well lose this. Losing here means being taken alive by the Guild."
    run(store, apply_harm, "pc.wren", severity="S2", harm_tags=["harm.physical.cut"], source="foe.guild_rider")
    assert "you go Down. Load 0/3." in (status_block(RULES, View(store.state), "pc.wren") or "")
    ans = yield_answer(RULES, store.state, "pc.wren", "foe.guild_rider")
    assert ans.accepted and "keep_one_thing" in [t["id"] for t in ans.terms]
    run(store, commit_yield, "pc.wren", ans, term="keep_one_thing")
    assert defeated_manner(store.state, "pc.wren") == "yielded"


def test_we_07_4_boundary_fought_to_the_end(tmp_path):
    store = make_game(tmp_path, vitality=1, vmax=12, pc_data=WREN,
                      others=[("adversary", "Guild rider", {"defeat_disposition": "capture"}, 10)])
    run(store, apply_harm, "pc.wren", dealt=1, source="foe.guild_rider", no_reduction=True)  # Staggered
    results = [run(store, apply_harm, "pc.wren", severity="S2", harm_tags=["harm.physical.cut"],
                   source="foe.guild_rider") for _ in range(3)]
    assert [r.amount for r in results] == [2, 2, 2]  # a soldier's sword (S2, 3) through the jack: Light
    assert results[-1].transition == "down" and wound_load(store.state, "pc.wren") == 3


@pytest.mark.parametrize(("branch", "interruptions", "lost", "quality", "vitality", "focus", "rested"), [
    ("A travelers", 0, 0, "full", 7, 6, True), ("B robbers", 1, 4, "partial", 6, 5, True),
    ("C chased them", 1, 7, "interrupted", 3, 2, None)])
def test_we_07_5_a_broken_night(tmp_path, branch, interruptions, lost, quality, vitality, focus, rested):
    store = make_game(tmp_path, vitality=1, vmax=7, focus=6, pc_data=WREN)
    with store.transaction() as tx:
        tx.add(Event.of("quantity_changed", entity="pc.wren", quantity="focus", delta=-6, new_value=0, reason="t"))
    q = rest_quality("rest_long", site="camp", interruptions=interruptions, lost_intervals=lost, sleep_hours=4)
    assert q == quality, branch
    p = rest_payload("rest_long", q, "camp")
    run(store, h_07_rest_recovery, boundary="rest_long", payload=p)
    run(store, h_05_focus_recover, boundary="rest_long", payload=p)
    assert vit(store) == vitality and store.state.quantities["pc.wren"]["focus"].current == focus
    assert store.state.fact_value("pc.wren", "rested_today") == rested


def test_we_07_5_the_days_after_brink_on_the_road(tmp_path):
    store = make_game(tmp_path, pc_data=WREN)
    with store.transaction() as tx:
        w = Writes(tx.state, tx.mint)
        w.fact("pc.wren", "brink", 1, rule_id="07.2.8")
        tx.add_all(w.events)
    for day in range(1, 5):  # a long rest each night on the road: +1 a day, healed on day 4
        run(store, h_07_rest_recovery, boundary="rest_long", payload=rest_payload("rest_long", "full", "camp"))
        run(store, h_07_natural_recovery, boundary="day")
        assert brink(store.state, "pc.wren") == (0 if day == 4 else 1)


def test_we_07_7_three_ways_out_of_a_cellar(tmp_path):
    ghoul = ("adversary", "Ghoul", {"defeat_disposition": "kill", "pace": 1, "attacks": [{"severity": "S2"}]}, 8)
    hound = ("adversary", "Cinder hound", {"defeat_disposition": "kill", "pace": 3,
                                            "attacks": [{"severity": "S3"}]}, 12)
    store = make_game(tmp_path, vitality=5, vmax=12, pc_data={**WREN, "pace": 2}, others=[ghoul, hound])
    off = retreat_offer(store.state, RULES, "pc.wren", route=True, engaged=["foe.ghoul"], hostiles=["foe.ghoul"],
                        left_behind=["satchel"])
    assert off.kind == "clean" and off.parting_blow == {"source": "foe.ghoul", "severity": "S1"}
    run(store, commit_retreat, "pc.wren", off, "clean")
    assert vit(store) == 5  # Light, which the jack turns (0)
    off = retreat_offer(store.state, RULES, "pc.wren", route=True, hostiles=["foe.cinder_hound"])
    assert [c["id"] for c in off.choices] == ["run_for_it", "rout"]
    off = retreat_offer(store.state, RULES, "pc.wren", route=True, hostiles=["foe.cinder_hound"],
                        barred=["foe.cinder_hound"])
    assert off.kind == "clean"
    store.append([Event(type="position_set", payload=PositionSet(entity="pc.wren", flags_add=["flag.cornered"]))])
    assert not retreat_offer(store.state, RULES, "pc.wren", route=True).legal
