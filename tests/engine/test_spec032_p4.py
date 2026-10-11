"""Spec 032 P4 (lane W): the world step of a dm-tools exchange. Cases F (the foe turn), T (time and the world) and
C (scene ends, now the DM's `end_scene` tool) of specs/032-dm-tools-mvp/cases.md, on the offline scripted DM."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from engine.dm import dm_tools, dm_world
from engine.dm.answer import held
from engine.game import Game
from engine.harm.dice import degree
from engine.resolve import conflict
from engine.resolve.frame import _defense
from engine.retrieve.scene import pc_id
from engine.store.clocks import create_clock
from engine.store.conditions import apply_condition
from engine.time import clock
from engine.world.common import fact
from engine.world.scenes import cast_present
from tests.engine.test_dm_tools import DM, change, in_turn, npc_here, to_play
from tests.engine.test_spec032_cases import FIX, RULES
from tests.engine.test_spec032_p3 import BEAST, roll

STRIKE = "foe "  # the foe strikes and breaks free through its own dice


def who(st: Any) -> str:
    return pc_id(st) or ""


def stats_of(game: Game, r: Any) -> dict[str, Any]:
    tr = game.store.turn(str(r.turn_id))
    assert tr is not None
    return dict(tr.screen["dm_tools"])


def rounds(game: Game) -> int:
    return clock.to_rounds(game.store.state.time.now)


def step(game: Game, *, beats: list[Any] | None = None, nat: int | None = None) -> tuple[list[str], Any]:
    """One world step in its own turn; `nat` fixes the foe's strike die. Returns (facts, the turn)."""
    box: dict[str, Any] = {}

    def go(ctx: Any, t: Any, tx: Any) -> list[str]:
        box["t"] = t
        t.beats = beats or []
        if nat is not None:
            real = ctx.rng.d
            ctx.rng.d = lambda sides, why="": nat if str(why).startswith(STRIKE) else real(sides, why)
        try:
            return dm_world.world_step(ctx, t)
        finally:
            if nat is not None:
                del ctx.rng.d

    return in_turn(game, go), box["t"]


def play(tmp: Path) -> tuple[Game, Any]:
    """A dm-tools game as its first turn leaves it: the place scene in `site` mode (dm_world.ensure_site)."""
    game, model = to_play(tmp)
    in_turn(game, lambda ctx, t, tx: dm_world.ensure_site(ctx))
    return game, model


def start_fight(game: Game, foe: str | None = None) -> str:
    foe = foe or npc_here(game)

    def go(ctx: Any, t: Any, tx: Any) -> bool:
        return conflict.start(ctx.time_ctx(), who(tx.state), [foe], "test")

    assert in_turn(game, go)
    return foe


def fighting(game: Game) -> bool:
    return bool(conflict.record(game.store.state))


def outcome(status: str) -> Any:
    return SimpleNamespace(status=status, entry=SimpleNamespace(beat_id="beat.x"))


# ------------------------------------------------------------------------------------------- F: the foe turn


def test_f1_to_f6_the_foe_turn_by_state(tmp_path: Path) -> None:
    game, _ = play(tmp_path)
    foe = start_fight(game)
    st = game.store.state
    # F3: not engaged, it closes one band (the seeded band is near)
    facts, t = step(game)
    assert len(t.stats["world"]["foe_turns"]) == 1 and ("moves toward" in facts[0] or "closes in" in facts[0])
    while conflict._band(game.store.state, foe, who(st)) != "engaged":
        step(game)
    # F4 a miss, F5 a hit, F6 a critical (one rung more)
    facts, _ = step(game, nat=1)
    assert any("misses" in f for f in facts) and not any("changed" in f.lower() for f in facts)
    line = conflict._line(RULES, game.store.state.entities[foe])
    guard = _defense(RULES, game.store.state, who(st), "agility", "deed.martial")
    hit = next(n for n in range(2, 20) if degree(n, int(line["atk"]), guard)[0] == "success")
    facts, _ = step(game, nat=hit)
    assert any("lands it" in f for f in facts) and any(f.startswith("What that changed") for f in facts)


def test_f1_f2_a_held_foe_breaks_free_and_a_prone_foe_stands(tmp_path: Path) -> None:
    game, model = play(tmp_path)
    foe = start_fight(game)
    pc = who(game.store.state)
    model.push(DM, {"foes": [{"foe": foe, "act": "break_free", "target": "", "nonlethal": False}]})  # [spec 033 D2]

    def hold(ctx: Any, t: Any, tx: Any) -> None:
        tx.add_all(apply_condition(tx.state, tx.mint, ctx.rules, foe, "cond.grabbed", source={"kind": "x", "entity": pc}).events)

    in_turn(game, hold)
    facts, _ = step(game, nat=20)
    assert "free" in facts[0]  # F1
    game2, _ = play(tmp_path / "b")
    foe2 = start_fight(game2)  # no pick: the default is the first legal row of beh.default_melee, which is `stand`

    def prone(ctx: Any, t: Any, tx: Any) -> None:
        tx.add_all(apply_condition(tx.state, tx.mint, ctx.rules, foe2, "cond.prone", source={"kind": "x"}).events)

    in_turn(game2, prone)
    facts, _ = step(game2)
    assert "feet" in facts[0]  # F2


def test_f7_to_f10_the_harm_ladder_ends_the_fight_or_opens_the_threshold(tmp_path: Path) -> None:
    game, _ = play(tmp_path)
    start_fight(game)
    pc = who(game.store.state)
    seen: list[str] = []
    for _ in range(12):
        step(game)  # closes in first
        if game.store.state.open_pause() is not None or not fighting(game):
            break
        facts, _ = step(game, nat=20)
        seen += facts
        if game.store.state.open_pause() is not None or not fighting(game):
            break
    st = game.store.state
    assert not fighting(game) or st.open_pause() is not None  # F8/F10: down ends the fight, or the threshold asks
    assert any(f.startswith("What that changed") for f in seen)  # F5/F7: the blows landed by code
    assert clock.mode_of(st.time.mode) != "conflict" or st.open_pause() is not None
    assert pc in st.entities


def test_f13_f18_a_foe_that_cannot_act_is_skipped_and_the_fight_ends(tmp_path: Path) -> None:
    game, _ = play(tmp_path)
    a = start_fight(game)

    def second(ctx: Any, t: Any, tx: Any) -> str:
        b = dm_tools._party(ctx, t, "the pale beast", as_="creature")
        assert b is not None
        conflict.start(ctx.time_ctx(), who(tx.state), [str(b)], "joins")
        return str(b)

    b = in_turn(game, second)
    assert set(conflict.record(game.store.state)["foes"]) == {a, b}

    def down(eid: str) -> Any:
        def go(ctx: Any, t: Any, tx: Any) -> None:
            tx.add(dm_tools._fact(tx, eid, "defeated", {"manner": "unconscious"}))
        return go

    in_turn(game, down(a))
    _, t = step(game)
    assert [x["foe"] for x in t.stats["world"]["foe_turns"]] == [b] and fighting(game)  # F13: only the able one acts
    in_turn(game, down(b))
    _, t = step(game)
    assert t.stats["world"]["foe_turns"] == [] and not fighting(game)  # F18: none able, conflict_end
    assert clock.mode_of(game.store.state.time.mode) == "site"  # the previous mode is back


def test_f14_f17_f19_f20_when_the_foe_does_not_act(tmp_path: Path) -> None:
    game, _ = play(tmp_path)
    # F20: no conflict, no foe turn
    facts, t = step(game)
    assert facts == [] and t.stats["world"]["foe_turns"] == []
    start_fight(game)
    # a refused or withdrawn beat spends nothing: no foe answers it (01.3.6); a spoken turn (no beat) does
    _, t = step(game, beats=[outcome("refused")])
    assert t.stats["world"]["foe_turns"] == []
    _, t = step(game)  # F14: the PC shouted (no beat): a turn is spent
    assert len(t.stats["world"]["foe_turns"]) == 1
    # F17: an open pause skips the world step entirely
    def pause(ctx: Any, t: Any, tx: Any) -> list[str]:
        out = dm_tools.tool(ctx, t, roll(verb="verb.strike", target=npc_here(game)))
        assert out.startswith("ROLL OFFERED")
        return dm_world.world_step(ctx, t)

    assert in_turn(game, pause) == []
    # F19: the PC down ends the fight and no blow follows
    pc = who(game.store.state)
    game3, _ = play(tmp_path / "c")
    start_fight(game3)

    def drop(ctx: Any, t: Any, tx: Any) -> None:
        tx.add(fact(tx, who(tx.state), "down", True, rule_id="07.1.3"))

    in_turn(game3, drop)
    step(game3)
    assert not fighting(game3) and pc


def test_f16_f21_an_npc_or_a_creature_turns_on_the_pc_and_the_foe_strikes_in_the_same_turn(tmp_path: Path) -> None:
    game, model = play(tmp_path)
    who = npc_here(game)
    model.push(DM, {"calls": [change(kind="fight", who=who)], "passage": "He squares up to you.", "said": [], "asks": []},
               {"calls": [], "passage": "He squares up to you.", "said": [], "asks": []},
               {"foes": [{"foe": who, "act": "close_in", "target": "", "nonlethal": False}]},  # the foe call [spec 033 D2]
               {"calls": [], "passage": "He lunges; the blow is dealt.", "said": [], "asks": []})
    r = game.submit("I say something he does not like.")
    stats = stats_of(game, r)
    assert fighting(game) and len(stats["world"]["foe_turns"]) == 1 and stats["world"]["reasked"] == 1
    assert stats["model_calls"] == 4  # the tool step, the draft, the foe call, and the one re-ask; none more
    assert stats["world"]["foe_calls"] == 1 and stats["world"]["foe_turns"][0]["picked_by"] == "dm"
    assert r.fiction == "He lunges; the blow is dealt."
    # F21: a creature is a foe too
    game2, model2 = play(tmp_path / "b")
    model2.push(DM, {"calls": [change(kind="fight", who="the pale beast", **{"as": "creature"})], "passage": "It crouches.", "said": [], "asks": []},
                {"calls": [], "passage": "It crouches.", "said": [], "asks": []}, {"calls": [], "passage": "It springs.", "said": [], "asks": []})
    r = game2.submit("I wave at the pale beast.")
    assert BEAST in conflict.record(game2.store.state)["foes"]
    assert stats_of(game2, r)["world"]["foe_turns"][0]["foe"] == BEAST


def test_f11_the_fighter_save_replayed_offers_the_roll_and_code_starts_no_fight(tmp_path: Path) -> None:
    """The saved fighter turns 9 and 12 (REFUSED, no fight, `conflict_start_boundaries == 0` in the old save): on the
    code, the same call offers the roll and the answer resolves it. [spec 033 R2 A4: only the DM's `change fight`
    starts a fight, so the attack no longer starts one and no foe answers.]"""
    fx = json.loads(FIX.read_text(encoding="utf-8"))
    assert fx["conflict_start_boundaries"] == 0  # what the old code did
    game, model = play(tmp_path)
    call = roll(**json.loads(fx["turns"]["turn.9"]["tools"][0]["args"]), **{"as": "creature"})  # [spec 033 R6] the DM says it is a creature
    model.push(DM, {"calls": [call], "passage": "You gather yourself.", "said": [], "asks": []})
    r = game.submit("I strike the beast in the clearing.")
    assert r.pause is not None and r.pause.kind == "offer"
    assert stats_of(game, r)["world"]["foe_turns"] == []  # F17: nothing while the offer is open
    model.push(DM, {"calls": [], "passage": "Steel meets the beast.", "said": [], "asks": []})
    r = game.answer("commit")
    assert r.pause is None  # (seed 7: the roll resolves; no near miss)
    marks = [e for e in game.store.events(types=["boundary_marked"]) if e.payload.boundary == "conflict_start"]  # type: ignore[attr-defined]
    assert marks == [] and conflict.record(game.store.state) == {}  # [spec 033 R2] code starts no fight
    assert stats_of(game, r)["world"]["foe_turns"] == []


def test_f22_f25_f26_the_foe_line_defaults_and_the_nonlethal_words(tmp_path: Path) -> None:
    """M1 runs `beh.default_melee` only (a ponytail comment in `foe_beat`): the ranged and mob defaults fall back to it."""
    assert {i for i in RULES.ids("beh.") if i.startswith("beh.default_")} == {
        "beh.default_melee", "beh.default_beast", "beh.default_mob", "beh.default_ranged"}
    assert "beh.default_melee" in (conflict.foe_beat.__doc__ or "")
    game, _ = play(tmp_path)  # F26: the DM's nonlethal flag reaches the words the harm rules read
    npc = npc_here(game)
    run_roll(game, roll(verb="verb.strike", target=npc, nonlethal=True))
    st = game.store.state
    assert st.open_pause() is not None  # [spec 033 R5] the flag rides in `stated`, the method text is not edited
    plan = st.open_pause().detail["plan"]  # type: ignore[union-attr]
    assert "(nonlethal)" not in json.dumps(plan) and plan["beat"]["stated"]["nonlethal"] is True


def run_roll(game: Game, call: dict[str, Any]) -> tuple[str, Any]:
    box: dict[str, Any] = {}

    def go(ctx: Any, t: Any, tx: Any) -> str:
        box["t"] = t
        return dm_tools.tool(ctx, t, call)

    return in_turn(game, go), box["t"]


# ------------------------------------------------------------------------------------------- T: time and the world


@pytest.mark.parametrize(("mode", "delta"), [("site", 100), ("free", 0), ("travel", 3600), ("downtime", 0)])
def test_t1_to_t4_a_plain_exchange_costs_its_modes_time(tmp_path: Path, mode: str, delta: int) -> None:
    game, _ = play(tmp_path)

    def set_it(ctx: Any, t: Any, tx: Any) -> None:
        from engine.time.scheduler import set_mode

        set_mode(ctx.time_ctx(), mode, "test")

    in_turn(game, set_it)
    before = rounds(game)
    step(game)
    assert rounds(game) - before == delta


def test_t5_a_fight_exchange_is_one_round(tmp_path: Path) -> None:
    game, _ = play(tmp_path)
    start_fight(game)
    before = rounds(game)
    step(game)
    assert rounds(game) - before == 1


def test_t6_an_interrupt_is_told_to_the_dm_and_cuts_nothing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    game, _ = play(tmp_path)
    scene = game.store.state.scene.scene_id  # type: ignore[union-attr]
    monkeypatch.setattr(dm_world, "advance_time", lambda *a, **k: SimpleNamespace(interrupt=("h.x", "a shout")))
    facts, _ = step(game)
    assert any("interrupted" in f and "a shout" in f for f in facts)
    assert game.store.state.scene.scene_id == scene  # type: ignore[union-attr]  # no code cut: the DM decides


def test_t7_a_clock_that_ticks_gives_its_omen_as_a_fact(tmp_path: Path) -> None:
    game, _ = play(tmp_path)

    def make(ctx: Any, t: Any, tx: Any) -> None:
        tpl = {"kind": "danger", "segments": 8, "visibility": "sensed", "auto_ticks": [{"boundary": "interval", "ticks": 1}],
               "omens": {s: [f"The {s} bell tolls.", f"The {s} bell tolls again."] for s in ("stirring", "building", "imminent")},
               "on_complete": {"interrupting": False, "effects": []}}
        tx.add(create_clock(tx.state, tpl, name="The bells", owner="00"))

    in_turn(game, make)
    facts, _ = step(game)
    assert any(f.startswith("An omen: The stirring bell tolls") for f in facts)


def test_t8_t9_t10_beat_end_dead_air_and_the_lead(tmp_path: Path) -> None:
    game, _ = play(tmp_path)
    lead_at = None
    for n in range(1, 10):
        marks0 = len([e for e in game.store.events(types=["boundary_marked"]) if e.payload.boundary == "beat_end"])  # type: ignore[attr-defined]
        facts, _ = step(game)
        if n > 1:  # T9: dead air counts the quiet exchanges
            assert int(game.store.state.meta.get("dead_air") or 0) in (n, 0)
        marks1 = len([e for e in game.store.events(types=["boundary_marked"]) if e.payload.boundary == "beat_end"])  # type: ignore[attr-defined]
        assert marks1 - marks0 == 1  # T9: one beat end for a plain exchange
        if any(f.startswith("A lead arrives") for f in facts):
            lead_at = n
            break
    assert lead_at == RULES.pacing["lead_injection"]["threshold"]  # T8: raised by the streak, written by inject_lead
    assert int(game.store.state.meta.get("dead_air") or 0) == 0  # the lead wrote facts: not a quiet exchange (T9)
    # T10: a refused beat spends no time and writes no beat end
    before = rounds(game)
    step(game, beats=[outcome("refused")])
    assert rounds(game) == before


def test_t11_t12_a_paused_turn_spends_no_time_and_the_clock_moves_from_hour_zero(tmp_path: Path) -> None:
    game, model = play(tmp_path)
    t0 = rounds(game)
    model.push(DM, {"calls": [roll(verb="verb.exert", goal="climb the wall", how="hand over hand")], "passage": "You move.", "said": [], "asks": []})
    r = game.submit("I climb the wall.")
    assert r.pause is not None and rounds(game) == t0  # T11 (the first turn's mode switch costs nothing)
    assert clock.mode_of(game.store.state.time.mode) == "site"  # A1: a dm-tools place scene runs in site mode
    model.push(DM, {"calls": [], "passage": "It lands.", "said": [], "asks": []}, {"calls": [], "passage": "It lands.", "said": [], "asks": []})
    game.answer("commit")
    assert rounds(game) > t0  # the answer turn spends time
    t1 = rounds(game)
    for text in ("I ask about the road.", "I ask about the weather."):
        game.submit(text)
    assert rounds(game) - t1 >= 200  # T12: two plain exchanges, one interval each


# ------------------------------------------------------------------------------------------- C: scene ends are the DM's


def scene_id(game: Game) -> str:
    return game.store.state.scene.scene_id  # type: ignore[union-attr]


def test_c1_c5_c7_no_scene_is_cut_without_the_call(tmp_path: Path) -> None:
    game, _ = play(tmp_path)
    first = scene_id(game)
    for _ in range(5):  # the pipeline would offer a cut after two quiet turns (dead_air)
        step(game)
    assert scene_id(game) == first
    start_fight(game)
    npc = npc_here(game)
    for _ in range(3):
        step(game, nat=20)
    assert scene_id(game) == first or not fighting(game)  # a fight's end cuts nothing (C5)
    assert game.store.state.scene is not None and npc


def test_end_scene_ends_it_resets_the_scene_and_opens_the_next(tmp_path: Path) -> None:
    game, _ = play(tmp_path)
    npc = npc_here(game)
    first = scene_id(game)

    def go(ctx: Any, t: Any, tx: Any) -> list[str]:
        out = [dm_tools.tool(ctx, t, {"tool": "mood", "npc": npc, "mood": "guarded", "why": "wary of strangers"})]
        assert held(ctx.state, npc)["band"] == "guarded"  # type: ignore[index]
        out.append(dm_tools.tool(ctx, t, {"tool": "end_scene", "why": "the talk has run dry"}))
        return out

    outs = in_turn(game, go)
    assert outs[0].startswith("done") and outs[1].startswith("done")
    st = game.store.state
    assert scene_id(game) != first and st.scene.place_id == st.last_scene.place_id  # type: ignore[union-attr]
    assert st.last_scene.scene_id == first and st.scene.mode == "site"  # type: ignore[union-attr]
    assert held(st, npc) is None  # the per-scene reset: the mood is the DM's to set again
    assert int(st.meta.get("dead_air") or 0) == 0
    assert set(cast_present(st)) >= {npc}


def test_end_scene_is_refused_in_a_fight_or_under_an_offer(tmp_path: Path) -> None:
    game, _ = play(tmp_path)
    start_fight(game)
    out = in_turn(game, lambda ctx, t, tx: dm_tools.tool(ctx, t, {"tool": "end_scene", "why": "x"}))
    assert out.startswith("REFUSED") and "fight" in out
    game2, _ = play(tmp_path / "b")

    def go(ctx: Any, t: Any, tx: Any) -> str:
        dm_tools.tool(ctx, t, roll(verb="verb.strike", target=npc_here(game2)))
        return dm_tools.tool(ctx, t, {"tool": "end_scene", "why": "x"})

    assert in_turn(game2, go).startswith("REFUSED: a roll is offered")


def test_c3_a_rest_is_a_time_jump_and_opens_a_scene(tmp_path: Path) -> None:
    game, _ = play(tmp_path)
    first = scene_id(game)

    def go(ctx: Any, t: Any, tx: Any) -> list[str]:
        out = dm_tools.tool(ctx, t, change(kind="rest", what="rest_short"))
        assert out.startswith("done"), out
        return dm_tools._world(ctx, t)

    facts = in_turn(game, go)
    assert scene_id(game) != first and any("Time has jumped" in f for f in facts)


def test_c2_c6_travel_opens_exactly_one_scene(tmp_path: Path) -> None:
    game, _ = play(tmp_path)
    first = scene_id(game)
    place = game.store.state.scene.place_id  # type: ignore[union-attr]
    from engine.world.places import reachable

    to = next(x.to for x in reachable(game.store.state, place) if x.to != place)
    out = in_turn(game, lambda ctx, t, tx: dm_tools.tool(ctx, t, change(kind="travel", to=to)))
    assert out.startswith("done")
    ends = [e for e in game.store.events(types=["scene_ended"])]
    assert scene_id(game) != first and len([e for e in ends if e.payload.scene_id == first]) == 1  # type: ignore[attr-defined]


# ------------------------------------------------------------------------------------------- moods: no roll, no ceiling


def test_mood_is_the_dms_call_a_memory_with_no_roll_and_no_ceiling(tmp_path: Path) -> None:
    game, model = play(tmp_path)
    npc = npc_here(game)

    def go(ctx: Any, t: Any, tx: Any) -> list[str]:
        first = dm_tools.tool(ctx, t, {"tool": "mood", "npc": npc, "mood": "closed", "why": "he lost a son to soldiers"})
        again = dm_tools.tool(ctx, t, {"tool": "mood", "npc": npc, "mood": "open", "why": "she paid his debt"})
        bad = dm_tools.tool(ctx, t, {"tool": "mood", "npc": npc, "mood": "furious", "why": ""})
        return [first, again, bad, dm_tools.situation(ctx), json.dumps(t.stats["moods"])]

    first, again, bad, sit, moods = in_turn(game, go)
    assert first.startswith("done") and "closed" in first and "ceiling" not in first and "at most" not in first
    assert again.startswith("done") and bad.startswith("REFUSED: mood is one of")
    assert "mood toward you: open (she paid his debt)" in sit
    assert json.loads(moods)[1]["was"] == "closed"
    assert "ask_cost" not in json.dumps(dm_tools.step_schema(game.ctx, final=False))
    # the grants the DM lists are observations: logged with the mood held, nothing is gated
    model.push(DM, {"calls": [], "passage": "He nods.", "said": [], "asks": [{"npc": npc, "cost": "big", "granted": "help"}]})
    r = game.submit("Will you hide me from the watch?")
    asks = stats_of(game, r)["asks"]
    assert asks[0]["granted"] == "help" and asks[0]["cost"] == "big" and "ceiling" not in asks[0]
    assert "ceilings" not in stats_of(game, r)


def test_the_situation_shows_the_fight(tmp_path: Path) -> None:
    game, _ = play(tmp_path)
    assert "FIGHT" not in in_turn(game, lambda ctx, t, tx: dm_tools.situation(ctx))
    foe = start_fight(game)
    sit = in_turn(game, lambda ctx, t, tx: dm_tools.situation(ctx))
    assert "FIGHT: a fight is on" in sit and f"- {foe}:" in sit and "- the character is" in sit
