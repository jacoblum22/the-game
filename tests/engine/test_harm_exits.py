"""Yield and Retreat (07.4; PR-07-6), answered from state before the player commits."""

from __future__ import annotations

from engine.harm.apply import apply_harm
from engine.harm.exits import commit_retreat, commit_yield, retreat_offer, yield_answer, yield_pause
from engine.harm.state import defeated_manner
from engine.store.events import Event, PositionSet
from tests.engine.test_harm_support import RULES, make_game, run, vit

RIDERS = ("adversary", "Rider", {"defeat_disposition": "capture"}, 10)
WIGHT = ("adversary", "Wight", {"defeat_disposition": "kill"}, 18)
GHOUL = ("adversary", "Ghoul", {"defeat_disposition": "kill", "pace": 1, "attacks": [{"severity": "S2"}]}, 8)
HOUND = ("adversary", "Hound", {"defeat_disposition": "kill", "pace": 3, "attacks": [{"severity": "S3"}]}, 12)


def test_yield_accepted_with_terms(tmp_path):
    store = make_game(tmp_path, others=[RIDERS])
    ans = yield_answer(RULES, store.state, "pc.wren", "foe.rider")
    assert ans.accepted and ans.words == "accepted: they would take you prisoner"
    assert [t["id"] for t in ans.terms] == ["no_further_harm", "parole", "keep_one_thing", "spare_another",
                                            "send_word", "an_audience"]
    with store.transaction() as tx:
        tx.add(yield_pause(tx.mint, ans))
    pause = store.state.open_pause()
    assert pause is not None and pause.kind == "yield_terms"
    run(store, commit_yield, "pc.wren", ans, term="keep_one_thing")
    assert defeated_manner(store.state, "pc.wren") == "yielded"
    assert store.state.fact_value("foe.rider", "yield_term:pc.wren") == "keep_one_thing"
    assert store.state.fact_value("pc.wren", "setback.yielded")["term"] == "keep_one_thing"


def test_yield_refused_by_a_killer(tmp_path):
    store = make_game(tmp_path, others=[WIGHT])
    ans = yield_answer(RULES, store.state, "pc.wren", "foe.wight")
    assert not ans.accepted and ans.terms == [] and ans.words.startswith("not accepted")


def test_clean_retreat_from_slow_ghouls(tmp_path):  # WE-07-7 row 1
    store = make_game(tmp_path, vitality=5, vmax=13, pc_data={"pace": 2, "reduction": 1}, others=[GHOUL])
    off = retreat_offer(store.state, RULES, "pc.wren", route=True, engaged=["foe.ghoul"], left_behind=["satchel"])
    assert off.legal and off.kind == "clean" and off.parting_blow == {"source": "foe.ghoul", "severity": "S1"}
    run(store, commit_retreat, "pc.wren", off, "clean")
    assert vit(store) == 5  # Light (1), turned by the jack (1)
    assert store.state.fact_value("pc.wren", "left_behind:satchel") is True


def test_rout_from_a_faster_hound_ticks_a_grudge(tmp_path):  # WE-07-7 row 2
    store = make_game(tmp_path, vitality=5, vmax=13, pc_data={"pace": 2}, others=[HOUND])
    off = retreat_offer(store.state, RULES, "pc.wren", route=True)
    assert off.kind == "contested" and off.pursuers == ["foe.hound"]
    assert [c["id"] for c in off.choices] == ["run_for_it", "rout"]
    run(store, commit_retreat, "pc.wren", off, "rout")
    clock = next(c for c in store.state.clocks.values() if c.name == "They are not finished with you")
    assert clock.filled == 4 and clock.owner == "foe.hound"  # starts at 2, +2 (U(S3))
    assert store.state.fact_value("pc.wren", "setback.retreated")["severity"] == "S3"


def test_barred_door_makes_it_clean_and_cornered_is_illegal(tmp_path):  # WE-07-7 rows 3-4
    store = make_game(tmp_path, pc_data={"pace": 2}, others=[HOUND])
    assert retreat_offer(store.state, RULES, "pc.wren", route=True, barred=["foe.hound"]).kind == "clean"
    store.append([Event(type="position_set", payload=PositionSet(entity="pc.wren", flags_add=["flag.cornered"]))])
    off = retreat_offer(store.state, RULES, "pc.wren", route=True)
    assert not off.legal and "cornered" in (off.refusal or "")


def test_down_cannot_retreat(tmp_path):
    store = make_game(tmp_path, vitality=1, others=[HOUND])
    run(store, apply_harm, "pc.wren", dealt=1, source="foe.hound", mode="nonlethal")
    assert not retreat_offer(store.state, RULES, "pc.wren", route=True).legal
