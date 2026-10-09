"""Spec 006: the default NPC layer (12.11.9, DL-12-43): activities, practice, the response order, an addressed NPC
always answers, and a seeded replay gives the same responses."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from engine.data.loader import load_rules
from engine.dm.npc_layer import ACTIVITY, clamp_row, current_activity, role_key
from engine.dm.turn import play_turn
from engine.llm.base import Role
from engine.llm.offline import ScriptedModel
from engine.store.events import EntityRecord, Event
from tests.engine.test_turn_adjudication import reader, setup

RULES = load_rules()
ASK = "Tam, is the ferry running tonight?"
HELLO = '"Evening," I say.'


def _model(n: int = 1, msg: str = ASK, cls: str = "FICTION_QUESTION") -> ScriptedModel:
    return ScriptedModel({Role.READER: [reader(cls, msg)] * n})


def test_a_rolled_row_outside_the_practice_moves_to_the_nearest_toward_five() -> None:
    assert clamp_row(4, [2, 3, 5, 6], hostile=False) == 5  # 3 and 5 are equally near: toward 5
    assert clamp_row(10, [2, 3, 5, 7], hostile=False) == 7
    assert clamp_row(1, [2, 3, 5], hostile=False) == 2
    assert clamp_row(1, [2, 3, 5], hostile=True) == 1  # row 1 is legal everywhere at Hostile


def test_a_role_finds_its_activity_cell() -> None:
    assert role_key(RULES, "guard") == "guard"
    assert role_key(RULES, "smith") == "crafter"  # tbl.npc_role's "crafter (smith, weaver, ...)"
    assert role_key(RULES, "harbour watch") == "guard"  # "guard or watch"
    assert role_key(RULES, "lamplighter") == "other"


def test_every_present_npc_has_an_activity_rolled_once_and_the_engaged_one_ends(tmp_path: Path) -> None:
    """12.11.9 step 1 [revision: R2-H]: rolled once per scene for each present NPC; Tam, asked, engages and his
    activity ends (not re-rolled); the watch's stays."""
    from engine.dm.npc_layer import rolled_this_scene

    dock, ctx = setup(tmp_path, _model(2))
    out = play_turn(ctx, ASK)
    st = dock.state
    acts = {a.npc: a.activity for a in out.adjudication.record.activities if a.slot == ACTIVITY}
    assert set(rolled_this_scene(st)) == {dock.ferryman, dock.watch}
    assert set(acts) == {dock.watch} and all(acts.values()) and current_activity(st, dock.ferryman) is None
    assert current_activity(st, dock.watch) == acts[dock.watch]

    def rolls() -> int:
        return sum(1 for e in dock.store.events() if e.type == "fact_set" and e.source == "12.11.9")

    before = rolls()
    play_turn(ctx, ASK)  # held, not re-rolled (a response may overwrite it: T-12-18)
    assert rolls() == before


def test_an_addressed_npc_always_answers_and_a_refusal_is_voiced(tmp_path: Path) -> None:
    """Twelve seeds: Tam, asked by name, answers every time with one willingness line (PR-12-10 step 2); an
    unwilling answer is a refusal in his own voice, never a talk wording."""
    from engine.dm.context import TurnContext
    from tests.engine.test_turn_adjudication import D20
    from tests.fixtures.scene_dock import build_dock

    for seed in range(12):
        dock = build_dock(tmp_path / str(seed), seed=seed)
        ask = "Tam, what news from upriver?"  # touches none of his recorded wants or refusals: the table decides
        ctx = TurnContext(store=dock.store, rules=dock.rules, rng=D20.of(dock.store), model=_model(msg=ask),
                          config={"world_judge": False})
        rec = play_turn(ctx, ask).adjudication.record
        mine = [a for a in rec.npc_actions if a.npc == dock.ferryman]
        assert len(mine) == 1, (seed, rec.npc_actions)
        band = next(t.split(":", 1)[1] for t in mine[0].tags if t.startswith("willingness:"))
        assert mine[0].source_ref == "PR-12-10" and band in ("willing", "guarded", "unwilling")
        assert mine[0].action.startswith("refuses") == (band == "unwilling"), mine[0].action
        assert not any(w in mine[0].action for w in ("asks the PC something", "wants something first"))


def test_the_same_seed_gives_the_same_responses(tmp_path: Path) -> None:
    def run(where: Path) -> list[Any]:
        dock, ctx = setup(where, ScriptedModel({Role.READER: [reader("FICTION_QUESTION", ASK),
                                                              reader("SPEECH", HELLO)]}), world_judge=False)
        out = [play_turn(ctx, ASK), play_turn(ctx, HELLO)]
        return [[(a.npc, a.action, a.source_ref) for a in o.adjudication.record.npc_actions] +
                [(a.npc, a.activity) for a in o.adjudication.record.activities] for o in out]
    assert run(tmp_path / "a") == run(tmp_path / "b")


def test_greeting_then_conversation(tmp_path: Path) -> None:
    from engine.dm.npc_layer import practice_for, spoken_with

    dock, ctx = setup(tmp_path, _model(2), world_judge=False)
    first = play_turn(ctx, ASK).adjudication.record
    assert dock.ferryman in spoken_with(dock.state)  # the exchange is remembered: the next is a conversation
    assert practice_for(dock.state, first, dock.ferryman, [dock.ferryman]) == "conversation"


def test_the_world_role_is_asked_only_about_an_npc_with_recorded_motives(tmp_path: Path) -> None:
    model = _model(2, msg="Brother, a word?", cls="SPEECH")
    model.push(Role.WORLD, {"responses": []})
    dock, ctx = setup(tmp_path, model)
    with dock.store.transaction() as tx:  # a walk-on with no wants or refusals, the one spoken to
        tx.add(Event.of("entity_created", source="test", entity=EntityRecord(
            id="npc.brother", kind="npc", name="Brother Alwin", data={"role": "priest", "pronouns": "he/him"})))
        tx.add(Event.of("position_set", source="test", rule_id="10.1.1", entity="npc.brother", location=dock.place))
    rec = play_turn(ctx, "Brother, a word?").adjudication.record
    assert [a.npc for a in rec.npc_actions] == ["npc.brother"]
    assert not [r for r, _ in model.calls if r == Role.WORLD]  # no motive: no World call (12.2.9's flag unasked)
