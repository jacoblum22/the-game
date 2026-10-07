"""Using an ability (05.4; PR-05-1) with Focus (05.6): validation order, costs, spend, Spent, overdraw, uses."""

from __future__ import annotations

import pytest

from engine.abilities.focus import (
    define_focus,
    focus_max,
    is_spent,
    push,
    restore_focus,
    restore_focus_consumable,
)
from engine.abilities.use import ability_cost, check_use, commit_use, offer_view
from engine.harm.ctx import Writes
from engine.store.events import Event
from tests.engine.test_harm_support import RULES, make_game, run, vit

LANCE = "ab.flame_lance"  # 1 Focus, at will, beat, flares
RIDER = "ab.measured_blow"  # 0 Focus, rider
SWORN = "ab.sworn_purpose"  # 0 Focus, once per long rest


def test_focus_max():
    assert [focus_max(4, t) for t in range(6)] == [4, 5, 6, 7, 8, 9]
    assert focus_max(5, 5, 3) == 12 and focus_max(5, 5, 9) == 12


def test_define_focus_event(tmp_path):
    store = make_game(tmp_path)
    store.append([define_focus("pc.wren", base=4, t_high=1)])
    q = store.state.quantities["pc.wren"]["focus"]
    assert (q.current, q.max) == (5, 5)


def test_cost_breakdown_and_cap():
    ab = RULES.ability(LANCE)
    assert ability_cost(ab).total == 1
    assert ability_cost(ab, flares=1, relic=True).total == 3
    assert ability_cost(ab, adjust=-3).total == 1  # never below 1 from a base above 0
    assert ability_cost(ab, adjust=5).total == 3  # increases at most +2
    big = ability_cost({"cost": {"focus": 4}}, flares=2, relic=True)
    assert big.total == 7 and big.refusal and "drop the flares" in big.refusal


def test_validation_order_and_refusals_spend_nothing(tmp_path):
    store = make_game(tmp_path, focus=2, abilities=[LANCE, RIDER])
    assert check_use(store.state, RULES, "pc.wren", "ab.firestorm").refusal == "not held"
    assert "timing" in (check_use(store.state, RULES, "pc.wren", LANCE, timing="rider").refusal or "")
    assert "one rider per beat" in (check_use(store.state, RULES, "pc.wren", RIDER, rider_used=True).refusal or "")
    assert "cannot be flared" in (check_use(store.state, RULES, "pc.wren", RIDER, flares=["far"]).refusal or "")
    with pytest.raises(ValueError):
        run(store, commit_use, "pc.wren", "ab.firestorm")
    assert store.state.quantities["pc.wren"]["focus"].current == 2


def test_commit_spends_focus_and_sets_spent(tmp_path):
    store = make_game(tmp_path, focus=2, abilities=[LANCE])
    view = offer_view(store.state, RULES, "pc.wren", LANCE)
    assert view["cost"] == 1 and view["text"] and view["uses_left"] is None
    res = run(store, commit_use, "pc.wren", LANCE, frame_id=None, flares=["hard"])
    assert res.cost == 2 and res.spent and is_spent(store.state, "pc.wren")
    assert res.hooks == ["on_focus_spent:" + RULES.ability(LANCE)["tags"][0] + ":2"]
    assert "no flare while Spent" in (check_use(store.state, RULES, "pc.wren", LANCE, flares=["hard"]).refusal or "")
    run(store, restore_focus, "pc.wren", amount=1, reason="test")
    assert not is_spent(store.state, "pc.wren")


def test_overdraw_needs_acceptance_and_costs_the_body(tmp_path):
    store = make_game(tmp_path, vitality=10, focus=1, abilities=[LANCE])
    run(store, commit_use, "pc.wren", LANCE)  # Focus 1 -> 0
    chk = check_use(store.state, RULES, "pc.wren", LANCE)
    assert chk.ok and chk.overdraw is not None and chk.overdraw.severity == "S2"
    with pytest.raises(ValueError, match="overdraw"):
        run(store, commit_use, "pc.wren", LANCE)
    res = run(store, commit_use, "pc.wren", LANCE, accept_overdraw=True)
    assert res.overdraw is not None and vit(store) == 7  # S2 = 3, no reduction
    assert any(c.condition_id == "cond.exhausted" for c in store.state.conditions_on("pc.wren"))
    assert store.state.meta["pc.wren.overdraws_since_long_rest"] == 1
    assert store.rebuild() == store.state


def test_overdraw_refused_when_it_would_reach_zero(tmp_path):
    store = make_game(tmp_path, vitality=3, focus=1, abilities=[LANCE])
    run(store, commit_use, "pc.wren", LANCE)
    chk = check_use(store.state, RULES, "pc.wren", LANCE)
    assert not chk.ok and "Vitality to 0" in (chk.refusal or "")


def test_limited_uses_are_counted(tmp_path):
    store = make_game(tmp_path, focus=4, abilities=[SWORN])
    res = run(store, commit_use, "pc.wren", SWORN)
    assert res.uses_left == 0 and store.state.quantities["pc.wren"]["uses.ab.sworn_purpose"].max == 1
    chk = check_use(store.state, RULES, "pc.wren", SWORN)
    assert not chk.ok and "rest_long" in (chk.refusal or "")


def test_last_stand_abilities_cost_no_focus(tmp_path):
    store = make_game(tmp_path, focus=0, abilities=[LANCE])
    with store.transaction() as tx:
        w = Writes(tx.state, tx.mint)
        w.fact("pc.wren", "last_stand", {"actions": 3}, rule_id="07.5.9")
        tx.add_all(w.events)
    assert run(store, commit_use, "pc.wren", LANCE).cost == 0


def test_push(tmp_path):
    store = make_game(tmp_path, focus=1)
    run(store, push, "pc.wren", choice="reach")
    assert store.state.quantities["pc.wren"]["focus"].current == 0
    with pytest.raises(ValueError):
        run(store, push, "pc.wren", choice="reach")


def test_consumables_restore_at_most_four_between_long_rests(tmp_path):
    store = make_game(tmp_path, focus=8)
    with store.transaction() as tx:
        tx.add(Event.of("quantity_changed", entity="pc.wren", quantity="focus", delta=-8, new_value=0, reason="t"))
    for want in (3, 4, 4):
        run(store, restore_focus_consumable, "pc.wren", 3, item="item.draught")
        assert store.state.quantities["pc.wren"]["focus"].current == want
