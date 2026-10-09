"""apply_harm and the ladder (07.1-07.2; PR-07-1): clamps, descriptors, the Stagger rule, reduction, Down,
Dying, the Threshold, restoring Vitality, the dying check, the NPC ladder."""

from __future__ import annotations

from pathlib import Path

import pytest

from engine.harm import lethal
from engine.harm.apply import apply_harm, bucket, dying_check, receiver_amount, restore_vitality, status_block
from engine.harm.ctx import Writes
from engine.harm.state import (
    ACTIVE,
    DEAD,
    DYING,
    STAGGERED,
    View,
    brink,
    descriptor,
    dying_step,
    harm_state,
    wound_load,
)
from tests.engine.test_harm_support import RULES, FixedDice, make_game, next_beat, run, vit

WIGHT = ("adversary", "Wight", {"lethal_context": True, "defeat_disposition": "kill"}, 18)


def warned(tmp_path: Path, **kw):
    store = make_game(tmp_path, others=[WIGHT], **kw)
    trig = lethal.warning_needed(store.state, "pc.wren")[0]
    run(store, lethal.record_warning, trig, sign="frost on the grave-goods")
    next_beat(store)
    return store


def test_bucket_and_severity_values():
    assert [bucket(n) for n in (1, 2, 3, 4, 5, 7, 8, 11, 12, 30)] == \
        ["S1", "S1", "S2", "S2", "S3", "S3", "S4", "S4", "S5", "S5"]


def test_reduction_is_capped_at_4_and_physical_only():
    assert receiver_amount(RULES, {"reduction": 9}, 8, ["harm.physical.cut"], no_reduction=False,
                           reduction=None)[0] == 4
    assert receiver_amount(RULES, {"reduction": 1}, 5, ["harm.frost"], no_reduction=False, reduction=None)[0] == 5
    assert receiver_amount(RULES, {"reduction": 1}, 3, ["harm.physical"], no_reduction=False, reduction=None)[0] == 2
    assert receiver_amount(RULES, {"reduction": 3}, 8, ["harm.physical"], no_reduction=True, reduction=None)[0] == 8
    assert receiver_amount(RULES, {"resist": ["harm.fire"]}, 5, ["harm.fire"], no_reduction=False,
                           reduction=None)[0] == 2


def test_clamps_descriptors_and_stagger_discards_excess(tmp_path):
    store = make_game(tmp_path, vitality=13)
    assert descriptor(store.state, "pc.wren") == "fresh"
    run(store, apply_harm, "pc.wren", dealt=5, source="x")
    assert (vit(store), descriptor(store.state, "pc.wren")) == (8, "worn")
    res = run(store, apply_harm, "pc.wren", dealt=5, source="x")
    assert (vit(store), descriptor(store.state, "pc.wren")) == (3, "bloodied")
    assert "on_vitality_threshold:half" in res.hooks
    res = run(store, apply_harm, "pc.wren", severity="S5", source="x")  # 12 against 3: never below 0
    assert vit(store) == 0 and res.breakdown["discarded"] == 9
    assert res.transition == "staggered" and harm_state(store.state, "pc.wren") == STAGGERED
    assert wound_load(store.state, "pc.wren") == 0  # the staggering blow wounds nothing (07.2.3)
    assert "trg.exits" in res.triggers and any("[STATUS] STAGGERED" in o for o in res.obligations)
    assert store.rebuild() == store.state


def test_zero_harm_moves_nothing(tmp_path):
    store = make_game(tmp_path, pc_data={"reduction": 3})
    res = run(store, apply_harm, "pc.wren", severity="S2", harm_tags=["harm.physical"], source="x")
    assert res.amount == 0 and vit(store) == 13 and res.transition is None


def test_nonlethal_mode_at_zero_is_down_at_once(tmp_path):
    store = make_game(tmp_path, vitality=3)
    res = run(store, apply_harm, "pc.wren", dealt=5, source="x", mode="nonlethal")
    assert res.transition == "down" and descriptor(store.state, "pc.wren") == "down"
    conds = {c.condition_id for c in store.state.conditions_on("pc.wren")}
    assert {"cond.unconscious", "cond.prone"} <= conds
    # the ladder is frozen: more harm changes nothing
    res = run(store, apply_harm, "pc.wren", severity="S5", source="x", lethal=True)
    assert res.transition is None and harm_state(store.state, "pc.wren") == STAGGERED


def test_lethal_flag_without_context_is_refused_and_logged(tmp_path):
    store = make_game(tmp_path, vitality=1)
    run(store, apply_harm, "pc.wren", dealt=5, source="foe.x")
    res = run(store, apply_harm, "pc.wren", dealt=8, source="foe.x", lethal=True)
    assert res.lethal is False and res.lethal_refused and res.transition == "down"
    assert store.state.meta["log.lethal_refused"]["missing"].startswith("1:")


def test_warning_takes_effect_only_after_the_next_declaration(tmp_path):
    store = make_game(tmp_path, vitality=1, others=[WIGHT])
    trig = lethal.warning_needed(store.state, "pc.wren")[0]
    run(store, lethal.record_warning, trig, sign="a tell")
    run(store, apply_harm, "pc.wren", dealt=5, source="foe.wight", lethal=True)  # Staggered
    res = run(store, apply_harm, "pc.wren", dealt=8, source="foe.wight", lethal=True)  # same beat: not yet
    assert res.lethal is False and res.transition == "down"


def test_staggered_load_three_under_lethal_enters_dying(tmp_path):
    store = warned(tmp_path, vitality=1)
    run(store, apply_harm, "pc.wren", dealt=5, source="foe.wight", lethal=True)
    res = run(store, apply_harm, "pc.wren", dealt=5, source="foe.wight", lethal=True)
    assert res.load == 2 and res.transition is None and res.wound == {"severity": "S3", "load": 2, "record": None}
    assert store.state.meta["log.coarse"]["rule_id"] == "PR-07-2"
    res = run(store, apply_harm, "pc.wren", dealt=3, source="foe.wight", lethal=True)
    assert res.transition == "dying" and dying_step(store.state, "pc.wren") == 1
    assert store.state.fact_value("pc.wren", "lethal_key", None).startswith("lc.")
    assert any(c.condition_id == "cond.prone" for c in store.state.conditions_on("pc.wren"))
    assert any("[STATUS] DYING 1 of 3" in o and "8 or better; 65%" in o for o in res.obligations)


def test_dying_steps_and_the_threshold(tmp_path):
    store = warned(tmp_path, vitality=1, pc_data={})
    run(store, apply_harm, "pc.wren", dealt=5, source="foe.wight", lethal=True)
    run(store, apply_harm, "pc.wren", dealt=8, source="foe.wight", lethal=True)  # Grievous: load 3 -> Dying 1
    assert harm_state(store.state, "pc.wren") == DYING
    run(store, apply_harm, "pc.wren", dealt=2, source="foe.wight")  # non-lethal: recorded and discarded
    assert dying_step(store.state, "pc.wren") == 1
    run(store, apply_harm, "pc.wren", dealt=5, source="foe.wight", lethal=True)
    assert dying_step(store.state, "pc.wren") == 2
    res = run(store, apply_harm, "pc.wren", dealt=8, source="foe.wight", lethal=True)  # S4: +2 -> past 3
    assert res.threshold and dying_step(store.state, "pc.wren") == 3
    assert harm_state(store.state, "pc.wren") == DYING  # never dead from harm


def test_brink_raises_the_entry_step(tmp_path):
    store = warned(tmp_path, vitality=1)
    with store.transaction() as tx:
        w = Writes(tx.state, tx.mint)
        w.fact("pc.wren", "brink", 2, rule_id="test")
        tx.add_all(w.events)
    run(store, apply_harm, "pc.wren", dealt=5, source="foe.wight", lethal=True)
    run(store, apply_harm, "pc.wren", dealt=8, source="foe.wight", lethal=True)
    assert dying_step(store.state, "pc.wren") == 3


def test_restoring_vitality_stabilizes_with_a_brink_wound(tmp_path):
    store = warned(tmp_path, vitality=1, vmax=13)
    run(store, apply_harm, "pc.wren", dealt=5, source="foe.wight", lethal=True)
    run(store, apply_harm, "pc.wren", dealt=8, source="foe.wight", lethal=True)
    run(store, restore_vitality, "pc.wren", amount=3, reason="draught", rule_id="07.2.7")
    assert harm_state(store.state, "pc.wren") == ACTIVE and vit(store) == 3
    assert dying_step(store.state, "pc.wren") == 0 and brink(store.state, "pc.wren") == 1
    assert wound_load(store.state, "pc.wren") == 3  # the load stays until a rest or scene_end


@pytest.mark.parametrize(("natural", "result", "step"), [
    (20, "stabilized", 0), (8, "stabilized", 0), (5, "holds", 1), (4, "step_up", 2), (1, "step_up", 3)])
def test_dying_check_at_step_one(tmp_path, natural, result, step):
    store = warned(tmp_path, vitality=1)
    run(store, apply_harm, "pc.wren", dealt=5, source="foe.wight", lethal=True)
    run(store, apply_harm, "pc.wren", dealt=8, source="foe.wight", lethal=True)
    chk = run(store, dying_check, "pc.wren", rng=FixedDice(natural))
    assert (chk.result, dying_step(store.state, "pc.wren")) == (result, step)


def test_npc_ladder(tmp_path):
    store = make_game(tmp_path, others=[("adversary", "Rabble", {}, 4), ("npc", "Captain", {"depth": "principal"}, 4),
                                        ("npc", "Guard", {}, 4)])
    assert run(store, apply_harm, "foe.rabble", dealt=9, source="pc.wren").transition == "dead"
    assert harm_state(store.state, "foe.rabble") == DEAD
    assert run(store, apply_harm, "npc.captain", dealt=9, source="pc.wren").transition == "defeated"
    assert run(store, apply_harm, "npc.guard", dealt=9, source="pc.wren", mode="nonlethal").transition == \
        "unconscious"


def test_status_block_without_context_says_down(tmp_path):
    store = make_game(tmp_path, vitality=1)
    run(store, apply_harm, "pc.wren", dealt=5, source="x")
    block = status_block(RULES, View(store.state), "pc.wren")
    assert block is not None and "you go Down. Load 0/3;" in block
