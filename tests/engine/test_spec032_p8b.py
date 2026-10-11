"""Spec 032 P8b: fights and costs (cases.md section P8b; written before the fixes, none of it from the held-out set).

R start range (`change fight to=`), X exchange endings, K every foe action kind, C a scene with no scene
facts, I informational verbs, L the Changed line.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from engine import ids
from engine.dm import dm_tools
from engine.dm.context import TurnContext
from engine.dm.oof import changed_line
from engine.game import Game
from engine.harm.dice import degree
from engine.llm.offline import ScriptedModel
from engine.resolve import conflict, pipeline
from engine.resolve.frame import _defense
from engine.retrieve.scene import pc_id as _pc_id
from engine.store.conditions import apply_condition
from engine.store.events import EntityRecord, Event
from engine.time.scheduler import TimeContext
from engine.world.common import fact
from engine.world.scenes import cast_present, end_scene, start_scene
from engine.world.social import cast_described
from tests.engine.test_dm_tools import DM, change, engage, in_turn, npc_here
from tests.engine.test_spec032_cases import RULES
from tests.engine.test_spec032_p3 import roll
from tests.engine.test_spec032_p4 import play, rounds, start_fight, stats_of, step
from tests.fixtures.scene_dock import build_dock


def pc_id(st: Any) -> str:
    return _pc_id(st) or ""


def say(text: str = "Steel.") -> dict[str, Any]:
    return {"calls": [], "passage": text, "said": [], "asks": []}


def turn_with(*calls: dict[str, Any]) -> dict[str, Any]:
    return {"calls": list(calls), "passage": "You step in.", "said": [], "asks": []}


def band(game: Game, a: str, b: str) -> str | None:
    return conflict._band(game.store.state, a, b)


def settle(game: Game, model: Any, *, pick: str = "commit") -> list[dict[str, str]]:
    """Answer every open pause (`pick` when it is offered, else the first choice); the foe turns of all of them."""
    foes: list[dict[str, str]] = []
    for _ in range(6):
        pause = game.store.state.open_pause()
        if pause is None:
            break
        model.push(DM, say(), say(), say())
        ids_ = [c["id"] for c in pause.choices]
        r = game.answer(pick if pick in ids_ else ids_[0])
        foes += stats_of(game, r)["world"]["foe_turns"]
    return foes


def nat_for(want: str, atk: int, guard: int) -> int:
    return next(n for n in range(1, 21) if degree(n, atk, guard)[0] == want)


# ------------------------------------------------------------------------------------------- R: the start range


@pytest.mark.parametrize(("start", "words"), [("engaged", "strikes at you"), ("close", "closes in"),
                                              ("near", "moves toward"), ("far", "moves toward"),
                                              ("distant", "moves toward")])
def test_r1_r5_the_dm_sets_the_start_range_and_the_foe_acts_from_it(tmp_path: Path, start: str, words: str) -> None:
    game, _ = play(tmp_path)
    foe, pc = npc_here(game), pc_id(game.store.state)
    out = in_turn(game, lambda ctx, t, tx: dm_tools.tool(ctx, t, change(kind="fight", who=foe, to=start)))
    assert out.startswith("done") and f"range {start}" in out
    assert band(game, pc, foe) == start
    _, t = step(game, nat=1)  # a forced miss, so an engaged foe's blow does not move the numbers
    did = [x["did"] for x in t.stats["world"]["foe_turns"]]
    assert len(did) == 1 and words in did[0]


def test_r6_to_r9_default_unknown_running_and_capitalised(tmp_path: Path) -> None:
    game, _ = play(tmp_path)
    foe, pc = npc_here(game), pc_id(game.store.state)
    out = in_turn(game, lambda ctx, t, tx: dm_tools.tool(ctx, t, change(kind="fight", who=foe)))
    assert out.startswith("done") and band(game, pc, foe) == "near"  # R6: 06.3.9's default
    out = in_turn(game, lambda ctx, t, tx: dm_tools.tool(ctx, t, change(kind="fight", who=foe, to="engaged")))
    assert "already in the fight" in out and band(game, pc, foe) == "near"  # R8: the start only
    game2, _ = play(tmp_path / "b")
    foe2, pc2 = npc_here(game2), pc_id(game2.store.state)
    out = in_turn(game2, lambda ctx, t, tx: dm_tools.tool(ctx, t, change(kind="fight", who=foe2, to="across the moon")))
    assert out.startswith("done") and "not a range" in out and band(game2, pc2, foe2) == "near"  # R7: no refusal
    game3, _ = play(tmp_path / "c")
    foe3, pc3 = npc_here(game3), pc_id(game3.store.state)
    in_turn(game3, lambda ctx, t, tx: dm_tools.tool(ctx, t, change(kind="fight", who=foe3, to="Close")))
    assert band(game3, pc3, foe3) == "close"  # R9


# ------------------------------------------------------------------------------------------- X: how an exchange ends


def test_x1_to_x4_a_foe_acts_only_when_the_roll_is_settled(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    game, model = play(tmp_path)
    foe = start_fight(game)
    engage(game, foe)
    before = rounds(game)
    model.push(DM, turn_with(roll(verb="verb.strike", target=foe, fail_cost="cost.harm")))
    r = game.submit("I swing at her.")
    assert r.pause is not None and r.pause.kind == "offer"
    assert stats_of(game, r)["world"]["foe_turns"] == [] and rounds(game) == before  # X1: an open OFFER spends nothing
    model.push(DM, say(), say(), say())
    r = game.answer("go_big")  # X3: the same offer, shown again
    assert r.pause is not None and r.pause.kind == "offer"
    assert stats_of(game, r)["world"]["foe_turns"] == [] and rounds(game) == before
    real = pipeline.roll_check
    monkeypatch.setattr(pipeline, "roll_check", lambda f, rng, on_roll=None: real(f, rng, on_roll).model_copy(
        update={"degree": "failure", "base_degree": "failure", "margin": -1, "near_miss": True}))
    model.push(DM, say(), say(), say())
    r = game.answer("commit")
    assert r.pause is not None and r.pause.kind == "near_miss"  # X2: a menu is open
    assert stats_of(game, r)["world"]["foe_turns"] == [] and rounds(game) == before
    monkeypatch.undo()
    foes = settle(game, model)  # X4: the menu's answer settles it
    assert len(foes) == 1 and foes[0]["foe"] == foe and rounds(game) - before == 1


def test_x5_two_foes_answer_one_each(tmp_path: Path) -> None:
    game, _ = play(tmp_path)
    a, b = cast_present(game.store.state)[:2]
    pc = pc_id(game.store.state)
    assert in_turn(game, lambda ctx, t, tx: conflict.start(ctx.time_ctx(), pc, [a, b], "test"))
    _, t = step(game)
    assert sorted(x["foe"] for x in t.stats["world"]["foe_turns"]) == sorted([a, b])


# ------------------------------------------------------------------------------------------- K: every foe action kind


def one_turn(game: Game, nat: int | None = None, pick: tuple[str, str] | None = None) -> list[str]:
    """One foe's turn. `pick` = (foe, act): the DM's choice for it [spec 033 D2]; none = the DM omits it (the default)."""
    if pick is not None:
        game.ctx.model.push(DM, {"foes": [{"foe": pick[0], "act": pick[1], "target": "", "nonlethal": False}]})  # type: ignore[union-attr]
    _, t = step(game, nat=nat)
    did = [x["did"] for x in t.stats["world"]["foe_turns"]]
    assert len(did) == 1, did  # one foe, one act
    return did


def hold(game: Game, foe: str, cond: str) -> None:
    pc = pc_id(game.store.state)

    def go(ctx: Any, t: Any, tx: Any) -> None:
        src = {"kind": "x", "entity": pc} if cond == "cond.grabbed" else {"kind": "x"}
        tx.add_all(apply_condition(tx.state, tx.mint, ctx.rules, foe, cond, source=src).events)

    in_turn(game, go)


def test_k1_to_k3_a_held_foe_fails_succeeds_or_tears_free(tmp_path: Path) -> None:
    for i, (want, words) in enumerate([("failure", "cannot break it"), ("success", "breaks free of your hold"),
                                       ("critical_success", "off balance")]):
        game, _ = play(tmp_path / str(i))
        foe, pc = start_fight(game), pc_id(game.store.state)
        hold(game, foe, "cond.grabbed")
        st = game.store.state
        line = conflict._line(RULES, st.entities[foe])
        n = nat_for(want, int(line["atk"]), _defense(RULES, st, pc, "might", "deed.martial"))
        assert words in one_turn(game, n, (foe, "break_free"))[0], want  # the DM picks break free for the held foe


def test_k4_a_prone_foe_stands(tmp_path: Path) -> None:
    game, _ = play(tmp_path)
    hold(game, start_fight(game), "cond.prone")
    assert one_turn(game) == ["gets back to its feet"]


@pytest.mark.parametrize(("at", "words"), [("close", "closes in, now at arm's reach of you"), ("near", "moves toward you"),
                                           ("far", "moves toward you"), ("distant", "moves toward you")])
def test_k5_to_k8_a_foe_not_engaged_moves_one_band_nearer(tmp_path: Path, at: str, words: str) -> None:
    game, _ = play(tmp_path)
    foe, pc = start_fight(game), pc_id(game.store.state)
    in_turn(game, lambda ctx, t, tx: conflict._set_band(tx, pc, foe, at, "test"))
    assert one_turn(game) == [words]
    i = conflict.BANDS.index(at)
    assert band(game, pc, foe) == conflict.BANDS[i - 1]


def test_k9_to_k11_an_engaged_foe_misses_hits_or_hits_hard(tmp_path: Path) -> None:
    lost: dict[str, int] = {}
    for i, want in enumerate(["failure", "success", "critical_success"]):
        game, _ = play(tmp_path / str(i))
        foe, pc = start_fight(game), pc_id(game.store.state)
        in_turn(game, lambda ctx, t, tx, foe=foe, pc=pc: conflict._set_band(tx, pc, foe, "engaged", "test"))
        st = game.store.state
        v0 = st.quantities[pc]["vitality"].current
        n = nat_for(want, int(conflict._line(RULES, st.entities[foe])["atk"]),
                    _defense(RULES, st, pc, "agility", "deed.martial"))
        did = one_turn(game, n)[0]
        lost[want] = v0 - game.store.state.quantities[pc]["vitality"].current
        assert ("misses" in did) == (want == "failure"), did
    assert lost["failure"] == 0 and 0 < lost["success"] < lost["critical_success"], lost


def test_k12_a_downed_foe_gives_no_turn(tmp_path: Path) -> None:
    game, _ = play(tmp_path)
    foe = start_fight(game)
    in_turn(game, lambda ctx, t, tx: tx.add(fact(tx, foe, "defeated", {"manner": "unconscious"}, rule_id="07.1.3")))
    _, t = step(game)
    assert t.stats["world"]["foe_turns"] == []


# ------------------------------------------------------------------------------------------- C, I: costs in a bare scene


def bare(tmp: Path, *, clock: bool, fight: bool) -> tuple[TurnContext, Any]:
    """A place with no scene facts, the PC and one watchman in it (the held-out failure), a listening clock or not."""
    dock = build_dock(tmp, seed=8100)
    with dock.store.transaction("turn.0b") as tx:
        tctx = TimeContext(tx, dock.rules, dock.rng)
        if not clock:
            tx.add(Event.of("clock_ticked", source="p8b", rule_id="00.8.5", clock_id=dock.clock, source_ref="p8b",
                            amount=0, filled=0, status="voided"))
        place = ids.entity_id("place", "The Hollow", tx.state.entities)
        tx.add(Event.of("entity_created", source="p8b", rule_id="PR-12-5", entity=EntityRecord(
            id=place, kind="place", name="The Hollow", data={"place_kind": "landmark"})))
        tx.add(Event.of("position_set", source="p8b", rule_id="10.1.1", entity=dock.ferryman, location=dock.place))
        for e in (dock.pc, dock.watch):
            tx.add(Event.of("position_set", source="p8b", rule_id="10.1.1", entity=e, location=place))
        end_scene(tctx, "p8b")
        start_scene(tctx, place=place, mode="site", agenda="", cast=[dock.watch])
        if fight:
            conflict.start(tctx, dock.pc, [dock.watch], "p8b")
            conflict._set_band(tx, dock.pc, dock.watch, "engaged", "06.3.9")
    ctx = TurnContext.for_store(dock.store, model=ScriptedModel({}), rules=dock.rules, rng=dock.rng,
                                config={"world_judge": False, "engine": dm_tools.ENGINE})
    return ctx, dock


def propose(ctx: TurnContext, dock: Any, call: dict[str, Any]) -> tuple[str, str | None]:
    """(the tool's answer, the threatened cost of the OFFER it opened or None)."""
    with dock.store.transaction("turn.900") as tx:
        ctx.tx = tx
        try:
            from engine.dm.adjudication import AdjudicationRecord

            t = dm_tools.Turn(rec=AdjudicationRecord(turn_id="turn.900", pc=pc_id(tx.state)))
            t.env = dm_tools._env(ctx, t)
            out = dm_tools.tool(ctx, t, call)
        finally:
            ctx.tx = None
    pause = dock.store.state.open_pause()
    return out, (pause.detail["frame"]["threatened_cost"]["menu_id"] if pause is not None else None)


COSTS = ["cost.harm", "cost.footing", "cost.exposure", "cost.drain", "cost.time", "cost.gear", "cost.closed_door",
         "cost.twist", "cost.shortfall"]


@pytest.mark.parametrize("fc", COSTS)
def test_c1_to_c9_a_strike_in_a_scene_with_no_facts_is_offered(tmp_path: Path, fc: str) -> None:
    ctx, dock = bare(tmp_path, clock=True, fight=True)
    out, cost = propose(ctx, dock, roll(verb="verb.strike", target=dock.watch, fail_cost=fc))
    assert out.startswith("ROLL OFFERED"), out  # C10: never "cost.twist only when no other entry is a candidate"
    # the rules make each of these legal here; the twist and the shortfall never are (twist last, shortfall alternate)
    assert cost == (fc if fc not in ("cost.twist", "cost.shortfall") else "cost.harm")
    dock.store.close()


@pytest.mark.parametrize(("verb", "fc", "expect"), [
    ("verb.observe", "none", "cost.drain"), ("verb.observe", "cost.time", "cost.drain"),
    ("verb.observe", "cost.exposure", "cost.drain"), ("verb.observe", "cost.drain", "cost.drain"),
    ("verb.observe", "cost.harm", "cost.harm"),  # the DM's own choice, legal at a hazard: its call
    ("verb.recall", "none", "cost.drain"), ("verb.recall", "cost.time", "cost.drain"),
    ("verb.recall", "cost.exposure", "cost.drain"), ("verb.recall", "cost.drain", "cost.drain"),
    ("verb.recall", "cost.harm", "cost.harm")])
def test_i1_to_i10_a_failed_look_costs_effort_not_a_wound(tmp_path: Path, verb: str, fc: str, expect: str) -> None:
    ctx, dock = bare(tmp_path, clock=False, fight=False)  # no clock: time is not legal; no hostile: exposure is not
    out, cost = propose(ctx, dock, roll(verb=verb, target="", fail_cost=fc, how="study the ground", change_kind="learn"))
    assert out.startswith("ROLL OFFERED"), out
    assert cost == expect
    dock.store.close()


@pytest.mark.parametrize("verb", ["verb.observe", "verb.recall"])
def test_i11_with_a_listening_clock_the_look_costs_time(tmp_path: Path, verb: str) -> None:
    ctx, dock = bare(tmp_path, clock=True, fight=False)
    out, cost = propose(ctx, dock, roll(verb=verb, target="", fail_cost="none", how="study the ground"))
    assert out.startswith("ROLL OFFERED") and cost == "cost.time", (verb, out, cost)
    dock.store.close()


def test_i12_when_no_cost_of_the_list_is_legal_a_risky_look_is_a_safe_roll(tmp_path: Path,
                                                                           monkeypatch: pytest.MonkeyPatch) -> None:
    from engine.resolve import costs

    real = costs.structural_fit
    monkeypatch.setattr(costs, "structural_fit", lambda menu_id, **kw: None if menu_id in (
        "cost.drain", "cost.harm", "cost.footing", "cost.gear", "cost.exposure", "cost.time",
        "cost.closed_door") else real(menu_id, **kw))
    ctx, dock = bare(tmp_path, clock=False, fight=False)
    v0 = dock.store.state.quantities[dock.pc]["vitality"].current
    out, cost = propose(ctx, dock, roll(verb="verb.observe", target="", fail_cost="cost.time", how="study the ground"))
    assert cost is None and not out.startswith("NOT POSSIBLE"), out  # a Safe roll: made at once, nothing to pay
    assert dock.store.state.quantities[dock.pc]["vitality"].current == v0
    dock.store.close()


# ------------------------------------------------------------------------------------------- L: the Changed line

WORDS = ["fresh", "worn", "bloodied", "staggered", "down", "dying", "dead", "down and dying", "down, out cold"]


@pytest.mark.parametrize("word", WORDS)
def test_l1_to_l11_the_changed_line_says_who_is_in_what_state(tmp_path: Path, word: str, monkeypatch: pytest.MonkeyPatch) -> None:
    game, _ = play(tmp_path)
    st = game.store.state
    foe = npc_here(game)  # name not known to the player
    known = in_turn(game, lambda ctx, t, tx: cast_described(ctx.time_ctx(), "a tall stranger", str(st.scene.place_id if st.scene else "")))
    monkeypatch.setattr(conflict, "state_words", lambda s, e: word)
    pc = pc_id(game.store.state)

    def ev(eid: str, q: str = "vitality") -> Any:
        return SimpleNamespace(type="quantity_changed", payload=SimpleNamespace(entity=eid, quantity=q, new_value=3, delta=-2))

    assert changed_line(game.store.state, pc, [ev(foe)]) == f"Changed: your opponent is {word}"
    from engine.store.views import display_name, name_known
    name = display_name(game.store.state, known)  # the name as the PC knows it, never a rolled name it has not learned
    assert not name_known(game.store.state, known) and name != game.store.state.entities[known].name  # trace-name-mixup
    assert changed_line(game.store.state, pc, [ev(known)]) == f"Changed: {name} is {word}"
    both = changed_line(game.store.state, pc, [ev(pc), ev(known)])  # L10: the PC's numbers first, then the foe in words
    assert both.endswith(f" · {name} is {word}") and both.startswith("Changed: Vitality")
