"""The lethal warning (07.3; PR-07-4): trigger rows, the block, contexts, the lethal frame, never auto-commit."""

from __future__ import annotations

from engine.harm import lethal
from engine.harm.rest import h_07_lethal_scan, h_07_load_clear
from tests.engine.test_harm_support import RULES, make_game, next_beat, run

WIGHT = ("adversary", "Wight", {"threat_advisory": "lethal", "lethal_context": True, "defeat_disposition": "kill"}, 18)
ROBBER = ("adversary", "Robber", {"defeat_disposition": "rob", "attacks": [{"name": "cudgel", "severity": "S2"}]}, 6)
TROLL = ("adversary", "Troll", {"defeat_disposition": "drive_off", "attacks": [{"name": "maul", "severity": "S4"}]}, 30)
RIDER = ("adversary", "Rider", {"defeat_disposition": "capture", "threat_advisory": "hard"}, 10)


def test_rows_first_true_cause_and_no_row_for_robbers(tmp_path):
    store = make_game(tmp_path, others=[WIGHT, ROBBER, TROLL])
    got = {(t.source, t.cause) for t in lethal.lethal_rows(store.state, "pc.wren")}
    assert got == {("foe.wight", "advisory"), ("foe.troll", "severity")}


def test_warning_block_text(tmp_path):
    store = make_game(tmp_path, others=[WIGHT])
    trig = lethal.warning_needed(store.state, "pc.wren")[0]
    text = lethal.warning_block(RULES, trig, source_name="the barrow-wight", fate=1,
                                yield_text="not accepted", retreat_text="clean: nothing to pay")
    assert text.startswith("[WARNING] THIS CAN KILL YOU — the barrow-wight. As things stand you are unlikely to win")
    assert "From your next action on, falling here can mean Dying. Fate: 1." in text
    assert "Exits now: Yield — not accepted · Retreat — clean: nothing to pay" in text
    troll = lethal.LethalTrigger("pc.wren", "foe.troll", "severity", {"severity": "S4"})
    assert lethal.cause_line(RULES, troll) == "A Grievous danger."


def test_record_warning_then_effective_after_next_declaration(tmp_path):
    store = make_game(tmp_path, others=[WIGHT])
    run(store, h_07_lethal_scan, boundary="scene_start")
    assert [t["source"] for t in lethal.active_triggers(store.state)] == ["foe.wight"]
    trig = lethal.warning_needed(store.state, "pc.wren")[0]
    run(store, lethal.record_warning, trig, sign="frost creeps")
    assert lethal.active_triggers(store.state) == []
    assert lethal.warning_needed(store.state, "pc.wren") == []
    c = lethal.context(store.state, "foe.wight")
    assert c is not None and c["id"].startswith("lc.") and c["cause"] == "advisory"
    assert lethal.effective(store.state, "foe.wight") is None
    frame = {"kind": "adversary", "source": "foe.wight", "target": "pc.wren", "mode": "lethal"}
    assert lethal.lethal_scan(store.state, frame).lethal is False
    next_beat(store)
    v = lethal.lethal_scan(store.state, frame)
    assert v.lethal and v.offer_line and v.offer_line.startswith("THIS CAN KILL YOU — Wight")
    assert lethal.may_auto_commit(store.state, frame) is False


def test_lethal_frame_tests(tmp_path):
    store = make_game(tmp_path, others=[WIGHT, ROBBER])
    trig = lethal.warning_needed(store.state, "pc.wren")[0]
    run(store, lethal.record_warning, trig, sign="frost")
    next_beat(store)
    pc_frame = {"kind": "pc", "source": "foe.wight", "target": "pc.wren", "stakes": "risky", "lethal": True}
    def missing(**kw) -> str:
        return str(lethal.lethal_scan(store.state, {**pc_frame, **kw}).missing)

    assert missing().startswith("2:")
    assert lethal.lethal_scan(store.state, {**pc_frame, "stakes": "dire"}).lethal
    assert missing(source="foe.robber", stakes="dire").startswith("1:")
    assert missing(target="foe.robber").startswith("3:")
    assert lethal.may_auto_commit(store.state, {**pc_frame, "source": "foe.robber"}) is True


def test_contexts_end_at_scene_end(tmp_path):
    store = make_game(tmp_path, others=[WIGHT])
    run(store, lethal.record_warning, lethal.warning_needed(store.state, "pc.wren")[0], sign="frost")
    run(store, h_07_load_clear, boundary="scene_end")
    assert store.state.fact_value("foe.wight", "lethal_context", "absent") is None
    assert lethal.context(store.state, "foe.wight") is None


def test_danger_notice_for_a_hard_fight(tmp_path):
    store = make_game(tmp_path, others=[RIDER])
    assert lethal.warning_needed(store.state, "pc.wren") == []
    line = lethal.danger_notice(store.state, "pc.wren", "foe.rider", "being taken alive by the Guild")
    assert line == "[WARNING] A hard fight — you may well lose this. Losing here means being taken alive by the Guild."
    run(store, h_07_lethal_scan, boundary="scene_start")
    assert store.state.meta["trg.danger_notice"] == ["foe.rider"]
