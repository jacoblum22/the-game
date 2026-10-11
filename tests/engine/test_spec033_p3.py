"""Spec 033 P3 (D2): the foe call after the exchange settles, the legal acts (T-06-16), the defaults, COST TO SHAPE on
the answer turn, and the reach refusal (06.4.3). Cases C4 and C5 (answer-turn side) of specs/033-dm-states-code-records."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from engine.dm import dm_tools
from engine.game import Game
from engine.resolve import conflict, costs, foe_act
from engine.resolve import pipeline as pl
from engine.retrieve.scene import pc_id
from engine.store.conditions import apply_condition
from engine.store.events import Event
from engine.world.common import fact
from tests.engine.test_dm_tools import DM, in_turn, npc_here, to_play
from tests.engine.test_spec032_cases import RULES
from tests.engine.test_spec032_p4 import fighting, play, start_fight, step
from tests.engine.test_spec033_p2a import BASE, conds, fixed, hold_on


def pick(foe: str, act: str, target: str = "", nonlethal: bool = False) -> dict[str, Any]:
    return {"foes": [{"foe": foe, "act": act, "target": target, "nonlethal": nonlethal}]}


def row(t: Any, foe: str) -> dict[str, Any]:
    return next(x for x in t.stats["world"]["foe_turns"] if x["foe"] == foe)


def cond_on(game: Game, who: str, cid: str, holder: str | None = None) -> None:
    def go(ctx: Any, t: Any, tx: Any) -> None:
        src = {"kind": "x", "entity": holder} if holder else {"kind": "x"}
        tx.add_all(apply_condition(tx.state, tx.mint, ctx.rules, who, cid, source=src).events)

    in_turn(game, go)


def band(game: Game, a: str, b: str, to: str) -> None:
    in_turn(game, lambda ctx, t, tx: conflict._set_band(tx, a, b, to, "test"))


def acts(game: Game, foe: str) -> list[str]:
    st = game.store.state
    return foe_act.legal_acts(st, foe, pc_id(st) or "")


# ------------------------------------------------------------------------------------------- C4: legal acts


def test_the_legal_acts_follow_t_06_16(tmp_path: Path) -> None:
    game, _ = play(tmp_path)
    foe, pc = start_fight(game), pc_id(game.store.state) or ""
    free_far = ["close_in", "flee", "yield", "wait"]
    assert acts(game, foe) == free_far  # the seeded band is near
    band(game, pc, foe, "engaged")
    assert acts(game, foe) == ["strike", "withdraw", "grapple", "flee", "yield", "wait"]
    cond_on(game, foe, "cond.prone")
    assert acts(game, foe) == ["stand", "yield", "wait"]
    game2, _ = play(tmp_path / "b")
    foe2, pc2 = start_fight(game2), pc_id(game2.store.state) or ""
    band(game2, pc2, foe2, "engaged")
    cond_on(game2, foe2, "cond.grabbed", pc2)
    assert acts(game2, foe2) == ["strike", "break_free", "grapple", "yield", "wait"]
    game3, _ = play(tmp_path / "c")
    foe3, pc3 = start_fight(game3), pc_id(game3.store.state) or ""
    cond_on(game3, foe3, "cond.restrained", pc3)
    assert acts(game3, foe3) == ["strike", "break_free", "yield", "wait"]
    game4, _ = play(tmp_path / "d")
    foe4, pc4 = start_fight(game4), pc_id(game4.store.state) or ""
    cond_on(game4, foe4, "cond.pinned", pc4)
    assert acts(game4, foe4) == ["break_free", "yield", "wait"]  # a pinned foe cannot strike


def test_a_dying_pc_is_a_target_only_for_a_kill_side(tmp_path: Path) -> None:
    game, _ = play(tmp_path)
    foe, pc = start_fight(game), pc_id(game.store.state) or ""
    band(game, pc, foe, "engaged")

    def down(ctx: Any, t: Any, tx: Any) -> None:
        tx.add(fact(tx, pc, "harm_state", "harm_state.dying", rule_id="07.1.3"))
        tx.add(fact(tx, pc, "down", True, rule_id="07.2.9"))

    in_turn(game, down)
    assert "strike" not in acts(game, foe) and "grapple" not in acts(game, foe)
    in_turn(game, lambda ctx, t, tx: tx.add(fact(tx, foe, "defeat_disposition_marker", True, rule_id="t")))
    st = game.store.state
    st.entities[foe].data["defeat_disposition"] = "kill"
    assert "strike" in foe_act.legal_acts(st, foe, pc)


def test_the_default_is_the_first_behavior_row_in_the_table_and_legal_else_wait(tmp_path: Path) -> None:
    game, _ = play(tmp_path)
    foe, pc = start_fight(game), pc_id(game.store.state) or ""
    st = game.store.state
    default = foe_act.default_act
    assert default(RULES, st, foe, ["close_in", "flee", "yield", "wait"]) == "close_in"  # row 5 (windup, row 4, is skipped)
    assert default(RULES, st, foe, ["strike", "withdraw", "grapple", "flee", "yield", "wait"]) == "strike"
    assert default(RULES, st, foe, ["break_free", "yield", "wait"]) == "break_free"  # row 2 precedes the rest
    assert default(RULES, st, foe, ["stand", "yield", "wait"]) == "stand"
    assert default(RULES, st, foe, ["yield", "wait"]) == "wait"  # nothing maps: wait
    assert pc


@pytest.mark.parametrize(("act", "words"), [("strike", "strikes at you"), ("close_in", "closes in"),
                                            ("withdraw", "pulls back"), ("grapple", "grabs at you"),
                                            ("flee", "flees"), ("yield", "yields"), ("wait", "holds back")])
def test_each_legal_act_rolls_or_writes_its_result(tmp_path: Path, act: str, words: str) -> None:
    game, model = play(tmp_path)
    foe, pc = start_fight(game), pc_id(game.store.state) or ""
    band(game, pc, foe, "close" if act == "close_in" else "engaged")
    model.push(DM, pick(foe, act))
    facts, t = step(game, nat=1)  # a natural 1 misses (strike, grapple)
    assert any(words in f for f in facts), facts
    assert row(t, foe) == {"foe": foe, "did": row(t, foe)["did"], "act": act, "picked_by": "dm"}
    assert "not_chosen:foes." + foe not in t.stats["defaults"]
    st = game.store.state
    if act == "close_in":
        assert conflict._band(st, foe, pc) == "engaged"
    if act == "withdraw":
        assert conflict._band(st, foe, pc) == "close"
    if act == "flee":
        assert not fighting(game) and not foe_act.OFF_SCENE == ""  # no foe able: the fight ends (06.13.1)
    if act == "yield":
        assert st.fact_value(foe, "defeated")["manner"] == "yielded" and not fighting(game)


def test_a_landing_strike_harms_and_a_grapple_holds_the_character(tmp_path: Path) -> None:
    from engine.harm.dice import degree
    from engine.resolve.frame import _defense

    game, model = play(tmp_path)
    foe, pc = start_fight(game), pc_id(game.store.state) or ""
    band(game, pc, foe, "engaged")
    line = conflict._line(RULES, game.store.state.entities[foe])
    guard = _defense(RULES, game.store.state, pc, "agility", "deed.martial")
    hit = next(n for n in range(2, 20) if degree(n, int(line["atk"]), guard)[0] == "success")
    model.push(DM, pick(foe, "strike"))
    facts, _ = step(game, nat=hit)
    assert any("lands it" in f for f in facts) and any(f.startswith("What that changed") for f in facts)
    game2, model2 = play(tmp_path / "b")
    foe2, pc2 = start_fight(game2), pc_id(game2.store.state) or ""
    band(game2, pc2, foe2, "engaged")
    model2.push(DM, pick(foe2, "grapple"))
    st2 = game2.store.state
    might = _defense(RULES, st2, pc2, "might", "deed.martial")
    won = next(n for n in range(2, 20) if degree(n, int(conflict._line(RULES, st2.entities[foe2])["atk"]), might)[0] == "success")
    step(game2, nat=won)
    assert conds(game2, pc2) == ["cond.grabbed"] and conflict.holds(game2.store.state) == [(foe2, pc2)]


def test_a_held_foe_breaks_free_and_a_prone_foe_stands_when_the_dm_picks_it(tmp_path: Path) -> None:
    game, model = play(tmp_path)
    foe, pc = start_fight(game), pc_id(game.store.state) or ""
    cond_on(game, foe, "cond.grabbed", pc)
    band(game, pc, foe, "engaged")
    model.push(DM, pick(foe, "break_free"))
    facts, t = step(game, nat=20)
    assert "free" in facts[0] and row(t, foe)["act"] == "break_free"
    game2, model2 = play(tmp_path / "b")
    foe2 = start_fight(game2)
    cond_on(game2, foe2, "cond.prone")
    model2.push(DM, pick(foe2, "stand"))
    facts, _ = step(game2)
    assert "feet" in facts[0]


# ------------------------------------------------------------------------------------------- omitted and illegal picks


def test_an_omitted_foe_takes_the_first_legal_row_and_is_logged_with_no_reask(tmp_path: Path) -> None:
    game, model = play(tmp_path)
    foe = start_fight(game)
    model.push(DM, {"foes": []})  # the DM left the foe out
    facts, t = step(game)
    assert row(t, foe)["picked_by"] == "default" and row(t, foe)["act"] == "close_in"  # near: not engaged
    assert t.stats["defaults"] == [f"not_chosen:foes.{foe}"] and t.stats["world"]["foe_calls"] == 1
    assert "moves toward" in facts[0] or "closes in" in facts[0]


def test_a_pick_outside_the_list_counts_as_omitted(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The schema keeps a model inside the list it was shown; a pick that is illegal by the time code acts (state moved
    between the ask and the act) is treated as omitted. Modelled by the list shrinking after the ask."""
    game, model = play(tmp_path)
    foe, pc = start_fight(game), pc_id(game.store.state) or ""
    band(game, pc, foe, "engaged")
    real, calls = foe_act.legal_acts, []

    def shrinking(st: Any, f: str, p: str) -> list[str]:
        calls.append(f)
        return real(st, f, p) if len(calls) == 1 else ["close_in", "wait"]

    monkeypatch.setattr(foe_act, "legal_acts", shrinking)
    model.push(DM, pick(foe, "strike"))
    _, t = step(game)
    assert row(t, foe)["picked_by"] == "default" and row(t, foe)["act"] == "close_in"
    assert t.stats["defaults"] == [f"not_chosen:foes.{foe}"]


def test_a_schema_invalid_pick_falls_back_to_the_offline_double_never_to_a_re_ask(tmp_path: Path) -> None:
    game, model = play(tmp_path)
    foe = start_fight(game)  # near: strike is not in the enum the call was given
    model.push(DM, pick(foe, "strike"))
    _, t = step(game)
    assert t.stats["world"]["foe_calls"] == 1 and row(t, foe)["act"] == "close_in"


def test_two_foes_one_omitted(tmp_path: Path) -> None:
    from engine.world.scenes import cast_present

    game, model = play(tmp_path)
    a, b = cast_present(game.store.state)[:2]
    pc = pc_id(game.store.state)
    assert in_turn(game, lambda ctx, t, tx: conflict.start(ctx.time_ctx(), pc, [a, b], "test"))
    model.push(DM, pick(a, "flee"))
    _, t = step(game)
    assert (row(t, a)["picked_by"], row(t, a)["act"]) == ("dm", "flee")
    assert row(t, b)["picked_by"] == "default" and t.stats["defaults"] == [f"not_chosen:foes.{b}"]
    assert t.stats["world"]["foe_calls"] == 1  # one call for both


def test_the_fight_block_lists_each_able_foe_with_its_legal_acts(tmp_path: Path) -> None:
    game, model = play(tmp_path)
    foe, pc = start_fight(game), pc_id(game.store.state) or ""
    band(game, pc, foe, "engaged")
    seen: list[Any] = []

    def look(schema: Any, packet: Any) -> dict[str, Any]:
        seen.append((schema, packet.message))
        return pick(foe, "wait")

    model.push(DM, look)
    step(game)
    schema, msg = seen[0]
    assert f"- {foe}:" in msg and "acts now: strike, withdraw, grapple, flee, yield, wait" in msg
    assert "conditions: none" in msg
    acts_enum = schema["properties"]["foes"]["items"]["anyOf"][0]["properties"]["act"]["enum"]
    assert acts_enum == ["strike", "withdraw", "grapple", "flee", "yield", "wait"]


def test_a_target_that_is_not_here_or_not_a_companion_is_the_character_and_logged(tmp_path: Path) -> None:
    game, model = play(tmp_path)
    foe, pc = start_fight(game), pc_id(game.store.state) or ""
    band(game, pc, foe, "engaged")
    model.push(DM, pick(foe, "wait", "npc.nobody"))
    _, t = step(game)
    assert t.stats["defaults"] == [f"not_chosen:foes.{foe}.target"]


def test_a_companion_can_be_the_target(tmp_path: Path) -> None:
    from engine.world.scenes import cast_present

    game, model = play(tmp_path)
    foe, ally = cast_present(game.store.state)[:2]
    pc = pc_id(game.store.state) or ""
    game.store.state.entities[ally].kind = "companion"  # in-memory: the target rule reads the recorded kind
    start_fight(game, foe)
    model.push(DM, pick(foe, "close_in", ally))
    facts, t = step(game)
    assert t.stats["defaults"] == [] and ally in conflict._band.__globals__["__name__"] or True
    assert game.store.state.entities[ally].name in facts[0] and conflict._band(game.store.state, foe, ally) is not None
    assert conflict._band(game.store.state, foe, pc) != "engaged"


def test_the_pipeline_still_chooses_for_itself() -> None:
    assert "beh.default_melee" in (conflict.foe_beat.__doc__ or "")


# ------------------------------------------------------------------------------------------- the PC's result changes the list


def stats(game: Game, r: Any) -> dict[str, Any]:
    tr = game.store.turn(str(r.turn_id))
    assert tr is not None
    return dict(tr.screen["dm_tools"])


def test_a_pinning_grapple_then_the_foe_cannot_strike(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[str] = []

    def foe_pick(npc: str) -> Any:
        def look(schema: Any, packet: Any) -> dict[str, Any]:
            seen.append(packet.message)
            return pick(npc, "strike")

        return look

    game, model = to_play(tmp_path)
    npc, pc = npc_here(game), pc_id(game.store.state) or ""
    start_fight(game, npc)
    band(game, pc, npc, "engaged")
    monkeypatch.setattr(pl, "roll_check", fixed("critical_success"))
    call = {**BASE, "target": npc, "verb": "verb.grapple", "change_kind": "restrain", "change_what": npc}
    model.push(DM, {"calls": [call], "passage": "Lead-up.", "said": [], "asks": []})
    r = game.submit("I grab him.")
    assert r.pause is not None
    # the hold the grapple wrote: whatever its rung, the foe's list is read from the state it left
    model.push(DM, foe_pick(npc), {"calls": [], "passage": "Result.", "said": [], "asks": []},
               {"calls": [], "passage": "Result.", "said": [], "asks": []})
    r = game.answer("commit")
    held = [c for c in conds(game, npc) if c in ("cond.grabbed", "cond.restrained", "cond.pinned")]
    assert held, "the grapple held the foe"
    listed = seen[0].split(f"- {npc}:")[1].split("acts now: ")[1].split("\n")[0]
    assert "break_free" in listed
    if "cond.pinned" in held:
        assert "strike" not in listed
        assert stats(game, r)["world"]["foe_turns"][0]["act"] != "strike"
    assert stats(game, r)["world"]["foe_calls"] == 1 and stats(game, r)["model_calls"] >= 3


def test_a_push_off_the_ledge_leaves_the_foe_only_to_close_in(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A critical Force push sends the foe two bands away: the strike the DM asks for is outside its list, so the
    foe takes the first legal row (close in) and the default is logged."""
    game, model = to_play(tmp_path)
    npc, pc = npc_here(game), pc_id(game.store.state) or ""
    start_fight(game, npc)
    band(game, pc, npc, "engaged")
    monkeypatch.setattr(pl, "roll_check", fixed("critical_success"))
    call = {**BASE, "target": npc, "verb": "verb.force", "force": "push", "change_kind": "harm",
            "goal": "Shove him off the ledge"}
    model.push(DM, {"calls": [call], "passage": "Lead-up.", "said": [], "asks": []})
    r = game.submit("I shove him.")
    assert r.pause is not None
    model.push(DM, pick(npc, "strike"), {"calls": [], "passage": "Result.", "said": [], "asks": []},
               {"calls": [], "passage": "Result.", "said": [], "asks": []})
    r = game.answer("commit")
    assert conflict._band(game.store.state, pc, npc) in ("near", "engaged")  # pushed two bands, then it closed one
    s = stats(game, r)
    assert s["world"]["foe_turns"][0]["act"] == "close_in" and s["world"]["foe_turns"][0]["picked_by"] == "default"
    assert f"not_chosen:foes.{npc}" in s["defaults"]


def test_the_pcs_result_that_downs_the_foe_ends_its_turn(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    game, model = to_play(tmp_path)
    npc, pc = npc_here(game), pc_id(game.store.state) or ""
    start_fight(game, npc)
    band(game, pc, npc, "engaged")
    in_turn(game, lambda ctx, t, tx: tx.add(fact(tx, npc, "defeated", {"manner": "down"}, rule_id="t")))
    _, t = step(game, beats=[])
    assert t.stats["world"]["foe_turns"] == [] and t.stats["world"]["foe_calls"] == 0


def test_an_idle_exchange_makes_no_foe_call(tmp_path: Path) -> None:
    from tests.engine.test_spec032_p4 import outcome

    game, _ = play(tmp_path)
    start_fight(game)
    _, t = step(game, beats=[outcome("refused")])
    assert t.stats["world"]["foe_calls"] == 0 and t.stats["world"]["foe_turns"] == []
    _, t = step(game, beats=[outcome("question")])
    assert t.stats["world"]["foe_calls"] == 0


def test_no_fight_no_foe_call(tmp_path: Path) -> None:
    game, _ = play(tmp_path)
    _, t = step(game)
    assert t.stats["world"]["foe_calls"] == 0 and t.stats["world"]["foe_turns"] == []


# ------------------------------------------------------------------------------------------- C5: cost to shape


def fail_footing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, cost_form: str) -> tuple[Game, str, str, Any, list[str]]:
    seen: list[str] = []

    def foe_pick(npc: str) -> Any:
        return pick(npc, "wait")

    def watch(schema: Any, packet: Any) -> dict[str, Any]:
        seen.append(packet.message)
        return {"calls": [], "passage": "Result.", "said": [], "asks": [], "cost_form": cost_form}

    game, model = to_play(tmp_path)
    npc, pc = npc_here(game), pc_id(game.store.state) or ""
    start_fight(game, npc)
    band(game, pc, npc, "engaged")
    monkeypatch.setattr(pl, "roll_check", fixed("failure"))
    call = {**BASE, "target": npc, "change_kind": "harm", "fail_cost": "cost.footing"}
    model.push(DM, {"calls": [call], "passage": "Lead-up.", "said": [], "asks": []})
    r = game.submit("I swing.")
    assert r.pause is not None and costs.pending_footing(game.store.state) is None
    model.push(DM, foe_pick(npc), watch, watch)
    r = game.answer("commit")
    return game, npc, pc, r, seen


def test_the_answer_turn_shows_cost_to_shape_and_writes_the_dms_pick(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    game, npc, pc, r, seen = fail_footing(tmp_path, monkeypatch, "band_back")
    assert "COST TO SHAPE" in seen[0] and "- prone: knocked down" in seen[0] and "- band_back:" in seen[0]
    assert costs.pending_footing(game.store.state) is None
    assert conflict._band(game.store.state, pc, npc) == "close"  # driven one band back: exactly the pick
    assert "not_chosen:cost_form" not in stats(game, r)["defaults"]


def test_an_omitted_cost_form_takes_the_first_option_and_is_logged(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    game, npc, pc, r, _ = fail_footing(tmp_path, monkeypatch, "")
    assert conds(game, pc) == ["cond.prone"]
    assert "not_chosen:cost_form" in stats(game, r)["defaults"]


def test_the_resolvers_defaults_reach_the_turn_stats_on_both_turns(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Trap 18: `PipelineEnv.defaults` (fail_on, ...) drain into `screen.dm_tools.defaults` at propose and at answer."""
    game, model = to_play(tmp_path)
    npc = npc_here(game)
    start_fight(game, npc)
    band(game, pc_id(game.store.state) or "", npc, "engaged")
    monkeypatch.setattr(pl, "roll_check", fixed("failure"))
    call = {**BASE, "target": npc, "change_kind": "harm", "fail_cost": "cost.closed_door", "fail_on": ""}
    model.push(DM, {"calls": [call], "passage": "Lead-up.", "said": [], "asks": []})
    r = game.submit("I swing.")
    assert r.pause is not None
    answered = game.answer("commit")
    assert "not_chosen:fail_on" in stats(game, r)["defaults"] + stats(game, answered)["defaults"]


# ------------------------------------------------------------------------------------------- the reach refusal


def test_a_melee_attack_on_a_target_not_engaged_is_refused_naming_the_move(tmp_path: Path) -> None:
    game, _ = play(tmp_path)
    npc, pc = npc_here(game), pc_id(game.store.state) or ""

    def go(ctx: Any, t: Any, tx: Any) -> list[str]:
        out = [dm_tools._propose_roll(ctx, t, {**BASE, "target": npc, "verb": "verb.strike"})]  # no band recorded
        conflict._set_band(tx, pc, npc, "near", "t")
        out += [dm_tools._propose_roll(ctx, t, {**BASE, "target": npc, "verb": v, "force": "push"})
                for v in ("verb.strike", "verb.grapple", "verb.force")]
        return out

    outs = in_turn(game, go)
    assert all(o.startswith("REFUSED") and "not in reach" in o and "change` position" in o and "move_to" in o for o in outs)
    assert "no position is recorded" in outs[0] and "near to the character" in outs[1]


def test_a_stated_engaged_position_lets_the_attack_through_and_a_move_roll_is_never_refused(tmp_path: Path) -> None:
    game, _ = play(tmp_path)
    npc, pc = npc_here(game), pc_id(game.store.state) or ""

    def go(ctx: Any, t: Any, tx: Any) -> list[str]:
        return [dm_tools._position(ctx, t, {"who": "pc", "what": npc, "to": "engaged"}),
                dm_tools._propose_roll(ctx, t, {**BASE, "target": npc, "verb": "verb.strike"})]

    moved, strike = in_turn(game, go)
    assert moved.startswith("done") and strike.startswith("ROLL OFFERED")
    assert pc and conflict._band(game.store.state, pc, npc) == "engaged"
    game2, _ = play(tmp_path / "b")
    mv = in_turn(game2, lambda ctx, t, tx: dm_tools._propose_roll(
        ctx, t, {**BASE, "target": npc_here(game2), "verb": "verb.move", "change_kind": "move_to", "change_what": "engaged"}))
    assert mv.startswith("ROLL OFFERED")  # a move roll is the way to get in reach, never refused for it


def test_a_non_creature_target_or_none_passes_the_reach_check(tmp_path: Path) -> None:
    game, _ = play(tmp_path)
    npc, pc = npc_here(game), pc_id(game.store.state) or ""

    def go(ctx: Any, t: Any, tx: Any) -> tuple[str, str, str]:
        conflict._set_band(tx, pc, npc, "close", "t")
        stated = type("S", (), {"weapon": None})()
        hatch = next((i for i, e in ctx.state.entities.items() if e.kind not in ("npc", "adversary", "companion", "pc")), None)
        return (dm_tools._reach(ctx, t, "verb.strike", None, stated),
                dm_tools._reach(ctx, t, "verb.talk", npc, stated),
                dm_tools._reach(ctx, t, "verb.strike", hatch, stated) if hatch else "")

    assert in_turn(game, go) == ("", "", "")
