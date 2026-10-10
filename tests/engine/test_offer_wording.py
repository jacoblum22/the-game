"""Spec 016: OFFER and RESULT wording (ROUND3-ANALYSIS problem 14; playtest 20261008-145410 talker notes 21-22,
20261008-145430 fighter 18 and 27-29). Snapshots: change them deliberately.

- "curt −2" named no one: each lever and snag says the fact in plain words, with whose it is;
- "a hindrance −2" for a yes/no fact: its words, negated;
- the fail text spoke of the player's character as "her" or "I": it says "you";
- "Paid: … (closed door, a setback)" read as bookkeeping: "It cost you: … — a setback."
"""

from __future__ import annotations

from pathlib import Path

import pytest

from engine.dm.adjudication import CostEntry
from engine.dm.oof import offer_block, result_block, to_player
from engine.resolve.types import Frame, RollResult
from tests.engine.test_resolve_frame import check
from tests.engine.test_resolve_scene import Scene


@pytest.fixture
def s(tmp_path: Path) -> Scene:
    sc = Scene.new(tmp_path)
    sc.add("npc", "Ysrion Leafward", attributes={"wits": 1, "agility": 1, "might": 2, "presence": 1})
    return sc


def test_offer_snapshot(s: Scene) -> None:
    npc = next(e for e in s.state.entities if e.startswith("npc."))
    curt = s.fact(npc, "detail.manner", "curt")
    rug = s.fact(npc, "detail.activity", "beating a rug")
    crowd = s.fact("world", "is_crowded_enough_to_move_unnoticed", False)
    pc_name = s.state.entities[s.pc].name
    f = check(s, levers=[rug], snags=[curt, crowd], stakes_source="consumed_resource",
              threatened_cost={"menu_id": "cost.drain", "form_intent": "I lose my footing and my breath"},
              alternate_cost={"menu_id": "cost.shortfall", "form_intent": f"{pc_name}'s offer is only half heard"},
              method_consequences=["my step close is noticed by the hall"])
    assert isinstance(f, Frame), f
    lines = [ln.strip() for ln in offer_block(f, rules=s.rules, fate=1, state=s.state).text.splitlines()]
    assert lines[1:6] == [
        "Chance: even — 50%   (Agility +3, experience +1, Ysrion is beating a rug +2, Ysrion is curt −2)",
        "If it works: what you wanted.   Very well (5%): more than you asked.",
        "If it fails: Danger: you lose your footing and your breath — serious.   Badly (5%): you lose your footing "
        "and your breath — grave.",  # the second snag raised the stakes (00.3.9(b))
        "Close call (15%): get it anyway and pay (your offer is only half heard), or fail.",
        "Whatever the roll: your step close is noticed by the hall",
    ], lines


def test_a_yes_no_fact_reads_as_its_words() -> None:
    from types import SimpleNamespace

    from engine.dm.oof import fact_short

    f = SimpleNamespace(value=False, predicate="is_crowded_enough_in_the_square_to_move_unnoticed",
                        visibility="shown", subject="loc.market")
    state = SimpleNamespace(facts={"fact.1": f}, seals={})
    assert fact_short(state, "fact.1") == "is not crowded enough in the square to move unnoticed"  # type: ignore[arg-type]


def test_to_player_addresses_the_player() -> None:
    assert to_player("I overbalance on the swing and my own footing goes") == \
        "you overbalance on the swing and your own footing goes"
    assert to_player("I'm thrown back, and it costs me the moment") == "you're thrown back, and it costs you the moment"
    assert to_player('Murzak snarls "I saw that"') == 'Murzak snarls "I saw that"'  # someone speaking: left whole


def test_result_price_line_snapshot(s: Scene) -> None:
    f = check(s, stakes_source="consumed_resource", threatened_cost={"menu_id": "cost.drain", "form_intent": "you tire"},
              alternate_cost={"menu_id": "cost.shortfall", "form_intent": "you get less"})
    assert isinstance(f, Frame)
    roll = RollResult(frame_id=None, d20=3, total=4, margin=-7, base_degree="failure", degree="failure",
                      near_miss=False)
    text = result_block(f, roll, costs=[CostEntry(menu_id="cost.closed_door", severity="S2",
                                                  form="Ysrion refuses to step away with me")]).text
    assert text.splitlines()[1].strip() == "It cost you: Ysrion refuses to step away with you — a setback."
    assert "Paid" not in text and "closed door" not in text
