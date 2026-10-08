"""Snapshots of the OFFER block (12.15.2's template, contracts/offer.md) for canonical frames, and the readability
check: no rendered block carries a severity code, a DC, a verb id, an anchor or a mode name (lane D P5 test).

    UPDATE_SNAPSHOTS=1 py -3.12 -m pytest tests/engine/test_offer_snapshots.py     # re-record after a wanted change
"""

from __future__ import annotations

import os
import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from engine.dm.oof import offer_block
from engine.resolve.frame import frame_check
from engine.resolve.types import Frame, ProposedFrame
from tests.engine.test_resolve_scene import Scene

SNAPSHOTS = Path(__file__).parent / "snapshots" / "offer_blocks.txt"
FORBIDDEN = re.compile(r"\bS\d\b|\bDC\b|verb\.|anchor|Mode:")
ANCHORS = {"verb.move": "anc.01_18_4", "verb.observe": "anc.01_18_5", "verb.recall": "anc.01_18_6",
           "verb.talk": "anc.01_18_7", "verb.strike": "anc.01_18_8", "verb.force": "anc.01_18_10",
           "verb.exert": "anc.01_18_11", "verb.handle": "anc.01_18_14"}


def _frame(s: Scene, verb: str, attribute: str, obstacle: dict[str, Any], beat: dict[str, Any] | None = None,
           **kw: Any) -> Frame:
    p: dict[str, Any] = {"anchor": ANCHORS[verb], "attribute": attribute, "stakes_source": "none",
                         "obstacle": {"kind": "tier", "id": "obs", **obstacle},
                         "threatened_cost": {"menu_id": "cost.drain", "form_intent": ""}, **kw}
    b = s.beat(**{"verb": verb, "intent": "do it", "restatement": kw.pop("_title", "You try it."), **(beat or {})})
    f = frame_check(ProposedFrame(**p), b, state=s.state, rules=s.rules, store=s.store)
    assert isinstance(f, Frame), f
    return f


RES = {"stakes_source": "consumed_resource", "alternate_cost": {"menu_id": "cost.shortfall", "form_intent":
                                                                   "you get only part of the way"}}


def cases(s: Scene) -> dict[str, Callable[[], Frame]]:
    guard = s.npc("Guard", attributes={"wits": 1, "resolve": 1, "agility": 1, "might": 2})
    packed = s.fact("world", "crowd.density", "packed")
    jostle = s.fact("world", "crowd.mood", "jostling")
    rope = s.fact("world", "rope.state", "knotted")
    make = s.fact("world", "lock.make", "guild-made")
    s.fact("world", "lethal_context", True)
    talk = {"verb": "verb.talk", "target": guard, "speech": True}
    hit = {"verb": "verb.strike", "target": guard, "against_will": True}
    return {
        "move_crowd": lambda: _frame(s, "verb.move", "agility", {"obstacle_class": "crowd"}),
        "move_crowd_one_snag": lambda: _frame(s, "verb.move", "might", {"obstacle_class": "crowd"}, snags=[packed]),
        "move_crowd_two_snags": lambda: _frame(s, "verb.move", "might", {"obstacle_class": "crowd"},
                                               snags=[packed, jostle], **RES),
        "move_obstructed_guarded": lambda: _frame(s, "verb.move", "might", {"obstacle_class": "obstructed"},
                                                  snags=[packed]),
        "observe_deliberate": lambda: _frame(s, "verb.observe", "wits", {"obstacle_class": "deliberate_concealment"}),
        "observe_secret": lambda: _frame(s, "verb.observe", "wits", {"obstacle_class": "faint_trail"}, secret=True),
        "recall_trade": lambda: _frame(s, "verb.recall", "intellect", {"obstacle_class": "trade_knowledge"}),
        "exert_climb_lever": lambda: _frame(s, "verb.exert", "might", {"obstacle_class": "hard_climb"},
                                            levers=[rope], **RES),
        "exert_gap_dire": lambda: _frame(s, "verb.exert", "agility", {"obstacle_class": "gap_leap"},
                                         stakes_source="height_or_depth", stakes_heavy=True,
                                         threatened_cost={"menu_id": "cost.harm", "form_intent": "a long fall"},
                                         alternate_cost={"menu_id": "cost.footing", "form_intent": "you slip"}),
        "exert_gap_lethal": lambda: _frame(s, "verb.exert", "agility", {"obstacle_class": "gap_leap"},
                                           stakes_source="height_or_depth", stakes_heavy=True, lethal=True,
                                           threatened_cost={"menu_id": "cost.harm", "form_intent": "a long fall"},
                                           alternate_cost={"menu_id": "cost.footing", "form_intent": "you slip"}),
        "force_reinforced_nudge": lambda: _frame(s, "verb.force", "might", {
            "obstacle_class": "sound_fitting", "nudge": 1, "nudge_fact": make,
            "nudge_why": "a guild-made lock stays hard"}),
        "force_flimsy_go_big": lambda: _frame(s, "verb.force", "might", {"obstacle_class": "flimsy"}, trade="go_big",
                                              alternate_cost={"menu_id": "cost.shortfall"}),
        "handle_awkward": lambda: _frame(s, "verb.handle", "agility", {"obstacle_class": "awkward"},
                                         method_consequences=["noisy"]),
        "strike_small_object": lambda: _frame(s, "verb.strike", "agility", {"obstacle_class": "small_or_far_object"}),
        "other_hard": lambda: _frame(s, "verb.move", "agility", {"obstacle_class": "other", "tier": "hard"}),
        "other_legendary_long_shot": lambda: _frame(s, "verb.move", "might",
                                                    {"obstacle_class": "other", "tier": "legendary"}),
        "talk_r2": lambda: _frame(s, "verb.talk", "presence", {"kind": "opposed", "entity": guard,
                                                               "request_size": "R2"}, beat=talk,
                                  stakes_source="goodwill_or_trust",
                                  threatened_cost={"menu_id": "cost.closed_door", "form_intent": ""},
                                  alternate_cost={"menu_id": "cost.shortfall", "form_intent": "he gives half"}),
        "talk_r4": lambda: _frame(s, "verb.talk", "presence", {"kind": "opposed", "entity": guard,
                                                               "request_size": "R4"}, beat=talk),
        "strike_guard": lambda: _frame(s, "verb.strike", "might", {"kind": "opposed", "entity": guard}, beat=hit),
        "fallback_mode": lambda: _frame(s, "verb.force", "might", {"obstacle_class": "sound_fitting"},
                                        beat={"mode": "fallback", "fallback_license": "lic.training.guile_thievery",
                                              "method": "force the lock crudely"}),
    }


@pytest.fixture(scope="module")
def rendered(tmp_path_factory: pytest.TempPathFactory) -> dict[str, str]:
    s = Scene.new(tmp_path_factory.mktemp("offers"))
    return {name: offer_block(make(), rules=s.rules, fate=1).text for name, make in cases(s).items()}


def _snapshot(blocks: dict[str, str]) -> str:
    return "\n\n".join(f"== {k}\n{v}" for k, v in blocks.items()) + "\n"


def test_offer_snapshots(rendered: dict[str, str]) -> None:
    assert len(rendered) >= 20
    text = _snapshot(rendered)
    if os.environ.get("UPDATE_SNAPSHOTS") or not SNAPSHOTS.exists():
        SNAPSHOTS.parent.mkdir(exist_ok=True)
        SNAPSHOTS.write_text(text, encoding="utf-8")
    assert text == SNAPSHOTS.read_text(encoding="utf-8")


def test_no_rule_text_reaches_the_player(rendered: dict[str, str]) -> None:
    for name, text in rendered.items():
        assert not FORBIDDEN.search(text), (name, FORBIDDEN.search(text), text)


def test_the_variants_read_as_the_template_says(rendered: dict[str, str]) -> None:
    assert "Chance: you can't judge how hard this is." in rendered["observe_secret"]
    assert "Chance: long shot — " in rendered["other_legendary_long_shot"]
    assert "Another way:" in rendered["other_legendary_long_shot"]
    assert "If it fails: Danger: " in rendered["exert_gap_dire"]
    assert "You're improvising without training: " in rendered["fallback_mode"]
    assert "a hindrance −2" in rendered["move_crowd_one_snag"]
    assert rendered["move_crowd_two_snags"].count("a hindrance −2") == 1  # the second hindrance raised the stakes
