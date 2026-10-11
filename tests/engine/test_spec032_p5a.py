"""Spec 032 P5a: three traced bugs (pinned-trace). The PC's own words resolve to the PC (`_party`), a refusal from a
condition names the condition, and a footing hold is held by the opponent (the unit cases are in test_resolve_costs)."""

from __future__ import annotations

from pathlib import Path

import pytest

from engine.dm import dm_tools
from engine.retrieve.scene import pc_id
from engine.store.conditions import apply_condition
from tests.engine.test_dm_tools import change, engage, in_turn, npc_here, to_play
from tests.engine.test_spec032_p3 import roll, run


def test_the_literal_pc_is_the_pc(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    pc = pc_id(game.store.state) or ""
    before = set(game.store.state.entities)
    assert in_turn(game, lambda ctx, t, tx: dm_tools._party(ctx, t, "pc", person=True)) == pc
    assert in_turn(game, lambda ctx, t, tx: dm_tools._party(ctx, t, "pc")) == pc
    assert set(game.store.state.entities) == before  # no NPC called "pc"


@pytest.mark.parametrize("words", ["PC", "the pc", "you", "the player"])
def test_other_words_for_the_pc_are_words_not_the_pc(tmp_path: Path, words: str) -> None:
    """[spec 033 R6, C8] Only the literal `pc` (or the id or exact name) is the character: "you" in a person slot is a
    walk-on, logged `not_chosen:as` (P7 counts them)."""
    game, _ = to_play(tmp_path)
    pc = pc_id(game.store.state) or ""
    before = set(game.store.state.entities)
    got = in_turn(game, lambda ctx, t, tx: (dm_tools._party(ctx, t, words, person=True), t.stats["defaults"]))
    assert got[0] != pc and got[0] not in before and "not_chosen:as" in got[1]


def test_the_pcs_name_is_the_pc(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    pc = pc_id(game.store.state) or ""
    name = game.store.state.entities[pc].name
    assert in_turn(game, lambda ctx, t, tx: dm_tools._party(ctx, t, name, person=True)) == pc


def test_change_coin_to_pc_pays_the_pc(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    pc, npc = pc_id(game.store.state) or "", npc_here(game)
    before = set(game.store.state.entities)
    coin0 = game.store.state.quantities[pc]["coin"].current
    outs, _ = run(game, change(kind="coin", who=npc, to="pc", amount=1))
    assert outs[0].startswith("done"), outs
    assert game.store.state.quantities[pc]["coin"].current == coin0 + 1
    assert set(game.store.state.entities) == before


def test_a_refusal_from_a_condition_names_it(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    pc = pc_id(game.store.state) or ""
    foe = npc_here(game)
    with game.store.transaction("turn.900") as tx:  # the DM cannot pin the PC; a foe's hold does
        tx.add_all(apply_condition(tx.state, tx.mint, game.ctx.rules, pc, "cond.pinned",
                                   source={"entity": foe}).events)
    engage(game, foe)
    outs, _ = run(game, roll(target=foe))
    assert "pinned (cinst." in outs[0] and "forbids verb.strike" in outs[0], outs[0]
    assert "an active condition" not in outs[0]


def test_the_real_save_footing_cost_is_held_by_the_woman(tmp_path: Path) -> None:
    """dmtools-175211-fighter turn.4 (pinned-trace.md): S4 footing on a Move toward the woman made the PC hold itself."""
    import json

    from engine.resolve.costs import apply_cost
    from engine.resolve.roll import read_result
    from engine.resolve.types import Frame, RollResult
    from evals.feedback_corpus import CORPUS, open_at
    from tests.engine.test_spec032_cases import RULES

    save = CORPUS / "dmtools-175211-fighter.db.gz"
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    after = open_at(save, "turn.5", tmp_path / "a")  # holds the frame; the state before the cost is turn.4's
    rows = after.conn.execute("select payload from events where type='frame_committed' and turn_id='turn.4'")
    frame = Frame.model_validate(json.loads(next(iter(rows))[0])["frame"])
    after.close()
    before = open_at(save, "turn.4", tmp_path / "b")
    try:
        roll_ = RollResult(frame_id=frame.id or "frame.1", d20=1, total=3, margin=-7, base_degree="critical_failure",
                           degree="critical_failure", near_miss=False)
        rd = read_result(frame, roll_).model_copy(update={"cost_severity": "S4", "cost_choices": ["cost.footing"]})
        app = apply_cost(frame, rd, "cost.footing", state=before.state, rules=RULES, mint=lambda p: p)
        src = [e.payload.instance.source["entity"] for e in app.events]  # type: ignore[attr-defined]
        assert src == [frame.beat.target] and src != [frame.beat.actor]
        frame.beat.target = None  # no opponent: the row's other forms, no hold on the PC
        app = apply_cost(frame, rd, "cost.footing", state=before.state, rules=RULES, mint=lambda p: p)
        assert not app.events and app.deferred == {"footing": "move to next lower/worse place", "severity": "S4"}
    finally:
        before.close()
