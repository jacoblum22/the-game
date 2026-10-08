"""Spec 007 (R2-C): the difficulty rubric and its guardrails in `frame_check`, and computed necessity.

00.3.8 / 01.6.5 (class base + one cited nudge), 00.3.9(b) / 01.6.8 (one cited Precision snag), 01.6.13 (the
critical-failure guard), 01.6.11 (a cost follows its stakes source), 01.6.4 / 15.3.3 (social and opposed beats use
the defense), 01.4.1 / 15.3.10 (necessity), 12.15.2 (alternatives)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from engine.resolve.frame import auto_commit_allowed, frame_check
from engine.resolve.gate import check_gate
from engine.resolve.necessity import ROLLS, necessity, parties_who_would_act, trivial_class
from engine.resolve.types import Beat, Frame, FrameRefusal, ProposedFrame
from tests.engine.test_resolve_scene import Scene
from tests.fixtures.scene_dock import build_dock

MOVE, TALK, STRIKE = "anc.01_18_4", "anc.01_18_7", "anc.01_18_8"


@pytest.fixture
def s(tmp_path: Path) -> Scene:
    return Scene.new(tmp_path, pc_attrs={"might": -1, "agility": 1, "endurance": 0, "wits": 0, "intellect": 0,
                                         "presence": 0, "resolve": 0})


def frame(s: Scene, beat: dict[str, Any] | None = None, **kw: Any) -> Frame | FrameRefusal:
    p: dict[str, Any] = {"anchor": MOVE, "attribute": "might", "stakes_source": "none",
                         "obstacle": {"kind": "tier", "id": "crowd", "obstacle_class": "crowd"},
                         "threatened_cost": {"menu_id": "cost.drain"}, **kw}
    b = s.beat(**{"verb": "verb.move", **(beat or {})})
    return frame_check(ProposedFrame(**p), b, state=s.state, rules=s.rules, store=s.store)


def ok(f: Frame | FrameRefusal) -> Frame:
    assert isinstance(f, Frame), f
    return f


def refused(f: Frame | FrameRefusal, text: str) -> None:
    assert isinstance(f, FrameRefusal) and text in f.reason, f


# ------------------------------------------------------------------------------------------- the rubric


def test_the_class_base_sets_the_tier(s: Scene) -> None:
    assert ok(frame(s)).tier == "easy"  # Move / crowd (T-00-5 everyday row)
    assert ok(frame(s, obstacle={"kind": "tier", "id": "x", "obstacle_class": "obstructed"})).tier == "moderate"
    refused(frame(s, obstacle={"kind": "tier", "id": "x", "obstacle_class": "sheer"}), "not one of verb.move")
    refused(frame(s, obstacle={"kind": "tier", "id": "x", "obstacle_class": "open_ground"}), "does not roll")
    other = ok(frame(s, obstacle={"kind": "tier", "id": "x", "obstacle_class": "other", "tier": "hard"}))
    assert (other.tier, other.obstacle_class) == ("hard", "other")  # no class fits: the rung itself


def test_a_nudge_is_one_rung_cited_never_across_the_trivial_line(s: Scene) -> None:
    lock = s.fact("world", "gate.make", "iron-bound, guild-made")
    ob = {"kind": "tier", "id": "x", "obstacle_class": "obstructed", "nudge": 1, "nudge_fact": lock,
          "nudge_why": "a guild-made barrier stays hard for anyone"}
    assert ok(frame(s, obstacle=ob)).tier == "hard"
    refused(frame(s, obstacle={**ob, "nudge_fact": None}), "cites an established intrinsic fact")
    refused(frame(s, obstacle={**ob, "nudge_why": ""}), "say why")
    refused(frame(s, obstacle={**ob, "obstacle_class": "crowd", "nudge": -1}), "never crosses the trivial line")
    refused(frame(s, obstacle={**ob, "obstacle_class": "other", "tier": "easy"}), "class other")


def test_a_nudge_and_a_snag_never_cite_the_same_fact(s: Scene) -> None:
    """The sim's double error (01-difficulty_rubric_sim-output.txt): one fact moves the odds once."""
    mud = s.fact("world", "quay.surface", "deep mud")
    ob = {"kind": "tier", "id": "x", "obstacle_class": "obstructed", "nudge": 1, "nudge_fact": mud,
          "nudge_why": "the mud is always there"}
    refused(frame(s, obstacle=ob, snags=[mud]), "one fact moves the odds once")


def test_one_cited_precision_snag_the_next_raises_the_stakes(s: Scene) -> None:
    a, b = s.fact("world", "crowd.density", "packed"), s.fact("world", "crowd.mood", "jostling")
    f = ok(frame(s, snags=[a, b], alternate_cost={"menu_id": "cost.shortfall"}))
    assert [x.type for x in f.snags] == ["precision", "protective"]
    assert f.modifier.circumstance == -2 and f.stakes == "risky"


def test_the_critical_failure_guard_converts_then_labels_a_long_shot(s: Scene) -> None:
    """01.6.13's example: Might −1, trained +1 (here deed +1), pushing through a crowd with a hindrance."""
    a = s.fact("world", "crowd.density", "packed")
    f = ok(frame(s, obstacle={"kind": "tier", "id": "x", "obstacle_class": "obstructed"}, snags=[a]))
    # moderate, −2: 10 vs DC 15 would show critical failure 45% above success 10%: the snag goes Protective
    assert f.guard and [x.type for x in f.snags] == ["protective"] and f.stakes == "risky"
    assert f.odds.critical_failure <= max(5, f.odds.success_or_better) or f.long_shot
    hard = ok(frame(s, obstacle={"kind": "tier", "id": "y", "obstacle_class": "other", "tier": "very_hard"}))
    assert hard.long_shot and hard.odds.critical_failure > hard.odds.success_or_better
    assert not auto_commit_allowed(hard)  # never auto-committed (01.7.4)
    assert hard.alternatives  # the best computed alternative is offered first (12.15.2)


def test_the_guard_does_not_touch_dire_secret_or_opposed_frames(s: Scene) -> None:
    secret = ok(frame(s, obstacle={"kind": "tier", "id": "y", "obstacle_class": "other", "tier": "very_hard"},
                      secret=True))
    assert not secret.long_shot and secret.guard is None


# ------------------------------------------------------------------------------------------- opposed and social


def test_social_and_attack_beats_on_a_person_use_the_defense(s: Scene) -> None:
    guard = s.npc("Guard", attributes={"wits": 1, "resolve": 1, "agility": 1, "might": 2})
    talk = {"verb": "verb.talk", "target": guard, "speech": True}
    refused(frame(s, talk, anchor=TALK, attribute="presence"), "never a tier")
    r2 = ok(frame(s, talk, anchor=TALK, attribute="presence",
                  obstacle={"kind": "opposed", "entity": guard, "request_size": "R2"}))
    r4 = ok(frame(s, talk, anchor=TALK, attribute="presence",
                  obstacle={"kind": "opposed", "entity": guard, "request_size": "R4"}))
    assert r2.dc_source == "opposed" and r4.dc - r2.dc == 6  # request mods R2 +2, R4 +8 (15.3.2)
    hit = ok(frame(s, {"verb": "verb.strike", "target": guard, "against_will": True}, anchor=STRIKE,
                   obstacle={"kind": "opposed", "entity": guard}))
    labels = [a.label for a in hit.alternatives]
    assert {"grapple instead", "shove instead"} & set(labels)  # P-117: approaches carry their own odds
    assert len({a.chance for a in hit.alternatives} | {hit.odds.success_or_better}) >= 2


# ------------------------------------------------------------------------------------------- costs follow sources


def test_a_cost_follows_its_stakes_source(s: Scene) -> None:
    refused(frame(s, stakes_source="goodwill_or_trust", threatened_cost={"menu_id": "cost.harm"},
                  alternate_cost={"menu_id": "cost.shortfall"}), "does not follow from stakes source")
    ok(frame(s, stakes_source="consumed_resource", threatened_cost={"menu_id": "cost.drain"},
             alternate_cost={"menu_id": "cost.shortfall"}))


def test_auto_commit_is_safe_only(s: Scene) -> None:
    safe = ok(frame(s, attribute="agility"))
    assert safe.stakes == "safe" and safe.odds.success_or_better >= 50 and auto_commit_allowed(safe)
    risky = ok(frame(s, attribute="agility", stakes_source="consumed_resource",
                     alternate_cost={"menu_id": "cost.shortfall"}))
    assert risky.stakes == "risky" and not auto_commit_allowed(risky)  # DL-01-32: never Risky


# ------------------------------------------------------------------------------------------- necessity


def _beat(dock: Any, **kw: Any) -> Beat:
    return Beat(**{"id": "beat.1", "actor": dock.pc, "intent": "x", "method": "x",
                   "declared_seq": dock.state.last_seq, **kw})


def test_a_plain_question_to_a_neutral_person_is_certain(tmp_path: Path) -> None:
    dock = build_dock(tmp_path)
    st, rules = dock.state, dock.rules
    ask = _beat(dock, verb="verb.talk", target=dock.ferryman, speech=True, asks=True, method="ask the fare")
    assert necessity(ask, check_gate(ask, state=st, rules=rules), state=st, rules=rules) == "trivial"
    push = ask.model_copy(update={"asks": False})  # a request, not a plain question: the Framer frames it
    assert necessity(push, check_gate(push, state=st, rules=rules), state=st, rules=rules) == ROLLS


def test_an_onlooker_counts_only_if_they_would_act(tmp_path: Path) -> None:
    dock = build_dock(tmp_path)
    st = dock.state
    assert parties_who_would_act(st, dock.pc) == []  # Neutral townsfolk: mere presence is not a source
    sneak = _beat(dock, verb="verb.sneak")
    assert set(parties_who_would_act(st, dock.pc, sneak)) == {dock.ferryman, dock.watch}  # being seen is the cost
    shove = _beat(dock, verb="verb.force", target=dock.watch, against_will=True)
    assert parties_who_would_act(st, dock.pc, shove) == [dock.watch]


def test_a_trivial_class_does_not_roll(s: Scene) -> None:
    p = ProposedFrame(anchor=MOVE, attribute="agility",
                      obstacle={"kind": "tier", "obstacle_class": "open_ground"})  # type: ignore[arg-type]
    assert trivial_class(p, s.rules, "verb.move")
    assert not trivial_class(p.model_copy(update={"obstacle": p.obstacle.model_copy(
        update={"obstacle_class": "crowd"})}), s.rules, "verb.move")
