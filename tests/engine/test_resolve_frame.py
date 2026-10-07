"""engine/resolve/frame.py: frame_check refusals (PR-01-2, each names its step), computations, OFFER helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from engine.resolve.frame import (
    auto_commit_allowed,
    commit_events,
    frame_check,
    legal_trades,
    offer_preview,
    status_applies,
)
from engine.resolve.oracle import OracleQuestion, ask_oracle
from engine.resolve.types import Frame, FrameRefusal, ProposedFrame
from engine.store.conditions import apply_condition
from tests.engine.test_resolve_scene import FixedRng, Scene

MOVE, FORCE, OBSERVE = "anc.01_18_4", "anc.01_18_10", "anc.01_18_5"


@pytest.fixture
def s(tmp_path: Path) -> Scene:
    sc = Scene.new(tmp_path)
    sc.add("npc", "Guard", attributes={"wits": 1, "agility": 1, "might": 2})
    return sc


def _base(s: Scene, **kw: Any) -> dict[str, Any]:
    p: dict[str, Any] = {"anchor": MOVE, "attribute": "agility",
                         "obstacle": {"kind": "tier", "id": "wall", "tier": "moderate"}, "stakes_source": "none",
                         "threatened_cost": {"menu_id": "cost.drain"}}
    p.update(kw)
    return p


def check(s: Scene, beat_kw: dict[str, Any] | None = None, **kw: Any) -> Frame | FrameRefusal:
    b = s.beat(**{"gate": "G1", "verb": "verb.move", **(beat_kw or {})})
    return frame_check(ProposedFrame(**_base(s, **kw)), b, state=s.state, rules=s.rules, store=s.store)


def refused(out: Frame | FrameRefusal, step: int, text: str) -> None:
    assert isinstance(out, FrameRefusal), "expected a refusal"
    assert out.step == step and text in out.reason, out.message


def test_a_plain_frame(s: Scene) -> None:
    f = check(s)
    assert isinstance(f, Frame)
    assert (f.modifier.total, f.dc, f.odds.success_or_better, f.stakes, f.reach) == (4, 15, 50, "safe", "standard")
    assert f.stored_dc_write == {"subject": "world", "predicate": f"dc.wall.{MOVE}", "value": 15}
    assert f.base_odds == 50 and auto_commit_allowed(f)


def test_refusals_name_their_step(s: Scene) -> None:
    refused(check(s, {"actor": "pc.nobody"}), 1, "unknown actor")
    refused(check(s, {"target": "npc.nobody"}), 1, "target")
    refused(check(s, {"gate": "G3", "verb": "verb.move", "method": "fly"}), 2, "does not roll")
    refused(check(s, anchor="anc.nope"), 3, "unknown anchor")
    fid = s.fact("world", "ground", "difficult")
    many = [{"knob": "attribute", "delta": "might", "cites_fact": fid},
            {"knob": "action_cost", "delta": "+1 through difficult ground", "cites_fact": fid},
            {"knob": "targets", "delta": "a line of foes, each a snag", "cites_fact": fid}]
    refused(check(s, deltas=many), 3, "at most 2")
    refused(check(s, deltas=[{"knob": "harm_severity", "delta": "x", "cites_fact": fid}]), 3, "no knob")
    refused(check(s, deltas=[{"knob": "attribute", "delta": "wits", "cites_fact": fid}]), 3, "not an allowed delta")
    refused(check(s, deltas=[{"knob": "attribute", "delta": "might"}]), 3, "cites no established fact")
    refused(check(s, attribute="presence"), 4, "not allowed")
    refused(check(s, deed_tag="deed.nope"), 5, "unknown deed tag")
    refused(check(s, obstacle={"kind": "tier", "tier": "trivial"}), 6, "does not roll")
    refused(check(s, obstacle={"kind": "tier", "tier": "beyond"}), 6, "G4")
    refused(check(s, obstacle={"kind": "opposed", "entity": "npc.ghost"}), 6, "existing defender")
    refused(check(s, obstacle={"kind": "entity_defense", "entity": "npc.guard", "defense": "guard"}), 6,
            "no defense")
    refused(check(s, levers=["fact.404"]), 7, "not an established fact")
    refused(check(s, levers=[fid, fid]), 7, "cited twice")
    a, b, c = (s.fact("world", f"l{i}", True) for i in range(3))
    refused(check(s, levers=[a, b, c]), 7, "at most 2")
    refused(check(s, snags=[a, b, c]), 7, "at most 2")
    refused(check(s, stakes_source="vibes"), 8, "unknown stakes source")
    refused(check(s, lethal=True, stakes_source="hazard", stakes_heavy=True,
                  threatened_cost={"menu_id": "cost.harm"}, alternate_cost={"menu_id": "cost.footing"}), 8,
            "lethal_context")
    refused(check(s, stakes_source="hazard", stakes_heavy=True, trade="go_big", threatened_cost={"menu_id": "cost.harm"},
                  alternate_cost={"menu_id": "cost.footing"}), 8, "not allowed from dire")
    refused(check(s, obstacle={"kind": "tier", "tier": "moderate"}, reach_whole=False, stakes_source="hazard",
                  trade="play_it_safe", threatened_cost={"menu_id": "cost.harm"},
                  alternate_cost={"menu_id": "cost.footing"}), 9, "Limited")
    refused(check(s, threatened_cost={"menu_id": "cost.nope"}), 10, "unknown cost")
    refused(check(s, threatened_cost={"menu_id": "cost.shortfall"}), 10, "only ever an alternate")
    refused(check(s, threatened_cost={"menu_id": "cost.harm"}), 10, "no established source")
    refused(check(s, stakes_source="hazard", threatened_cost={"menu_id": "cost.harm"}), 10, "needs an alternate")
    refused(check(s, stakes_source="hazard", threatened_cost={"menu_id": "cost.harm"},
                  alternate_cost={"menu_id": "cost.harm"}), 10, "different entry")


def test_levers_must_predate_the_declaration(s: Scene) -> None:
    b = s.beat(gate="G1", verb="verb.move")
    late = s.fact("world", "rope", "here")
    out = frame_check(ProposedFrame(**_base(s, levers=[late])), b, state=s.state, rules=s.rules)
    refused(out, 7, "after the declaration")


def test_circumstance_cap_and_lever_types(s: Scene) -> None:
    a, b, c = (s.fact("world", f"l{i}", True) for i in range(3))
    f = check(s, levers=[a, {"fact_id": b, "type": "amplifying"}], snags=[{"fact_id": c, "type": "protective"}],
              stakes_source="hazard", threatened_cost={"menu_id": "cost.harm"},
              alternate_cost={"menu_id": "cost.footing"})
    assert isinstance(f, Frame)
    assert (f.modifier.circumstance, f.reach, f.stakes) == (2, "great", "dire")
    f2 = check(s, levers=[a, b], repetition_instance=3)
    assert isinstance(f2, Frame) and f2.modifier.circumstance == 0  # +4 levers, -4 repetition
    f3 = check(s, snags=[a, b], repetition_instance=3)
    assert isinstance(f3, Frame) and f3.modifier.circumstance == -4  # capped


def test_free_fact_lever_caps(s: Scene) -> None:
    facts = []
    for i in range(3):
        with s.store.transaction() as tx:
            r = ask_oracle(OracleQuestion(subject="world", predicate=f"free{i}", odds="likely", asker=s.pc),
                           state=tx.state, rules=s.rules, rng=FixedRng([50]), mint=tx.mint)
            tx.add_all(r.events)
        facts.append(r.fact_id)
    refused(check(s, levers=facts[:2]), 7, "at most one lever")
    for i in range(2):
        f = check(s, {"id": f"beat.{i}"}, levers=[facts[i]])
        assert isinstance(f, Frame)
        with s.store.transaction() as tx:
            tx.add_all(commit_events(f, "commit", mint=tx.mint, state=tx.state))
    refused(check(s, levers=[facts[2]]), 7, "Setup")


def test_free_fact_never_sheds_a_lethal_frame(s: Scene) -> None:
    s.fact("world", "lethal_context", True)
    with s.store.transaction() as tx:
        r = ask_oracle(OracleQuestion(subject="world", predicate="soft_ground", odds="likely", asker=s.pc),
                       state=tx.state, rules=s.rules, rng=FixedRng([50]), mint=tx.mint)
        tx.add_all(r.events)
    kw: dict[str, Any] = dict(stakes_source="height_or_depth", stakes_heavy=True, lethal=True,
                              threatened_cost={"menu_id": "cost.harm"}, alternate_cost={"menu_id": "cost.footing"})
    refused(check(s, levers=[{"fact_id": r.fact_id, "type": "protective"}], **kw), 7, "never the Protective")
    worked = s.fact("world", "rope_tied_off", True)
    f = check(s, levers=[{"fact_id": worked, "type": "protective"}], **kw)
    assert isinstance(f, Frame) and (f.stakes, f.lethal) == ("risky", False)


def test_status_from_conditions(s: Scene) -> None:
    with s.store.transaction() as tx:
        tx.add_all(apply_condition(tx.state, tx.mint, s.rules, s.pc, "cond.off_balance").events)
    f = check(s)
    assert isinstance(f, Frame) and f.modifier.status == -2  # off balance: Might/Agility checks
    g = check(s, {"verb": "verb.observe"}, anchor=OBSERVE, attribute="wits")
    assert isinstance(g, Frame) and g.modifier.status == 0
    assert status_applies("any", "S1", "wits", None, []) is True
    assert status_applies("severity in [S2, S3]", "S1", "wits", None, []) is False
    assert status_applies("the beat relies on sight (Strike, aimed working, opposed Move)", "S1", "x", None,
                          []) is None


def test_trades_and_offer_view(s: Scene) -> None:
    f = check(s, stakes_source="aware_opponent_or_observer", threatened_cost={"menu_id": "cost.drain"},
              alternate_cost={"menu_id": "cost.footing"})
    assert isinstance(f, Frame) and legal_trades(f) == ["go_big", "play_it_safe"]
    big = check(s, stakes_source="aware_opponent_or_observer", trade="go_big",
                threatened_cost={"menu_id": "cost.drain"}, alternate_cost={"menu_id": "cost.footing"})
    assert isinstance(big, Frame) and (big.stakes, big.reach, big.dc) == ("dire", "great", f.dc)
    assert legal_trades(big) == []
    v = offer_preview(f)
    assert v.odds == {"success_or_better_pct": 50, "critical_success_pct": 5, "critical_failure_pct": 5,
                      "near_miss_pct": 15}
    assert v.difficulty_words == "Moderate" and v.need == 11 and v.threatened_cost["severity_on_failure"] == "S2"
    secret = check(s, secret=True)
    assert isinstance(secret, Frame) and offer_preview(secret).difficulty_words == "hidden"
    assert not auto_commit_allowed(secret)


def test_stretch_price_from_the_entry(tmp_path: Path) -> None:
    s = Scene.new(tmp_path, pc_licenses=["lic.training.martial_blade"])
    b = s.beat(gate="G2", license="lic.training.martial_blade", mode="stretch", verb="verb.strike")
    p = ProposedFrame.model_validate({"anchor": "anc.01_18_8", "attribute": "might", "stakes_source": "none",
                                      "obstacle": {"kind": "tier", "id": "woodpile", "tier": "easy"},
                                      "threatened_cost": {"menu_id": "cost.drain"}})
    f = frame_check(p, b, state=s.state, rules=s.rules)
    assert isinstance(f, Frame) and f.mode_price is not None
    assert (f.dc, f.mode_price.focus_add, f.reach) == (15, 1, "limited")
    assert not auto_commit_allowed(f)


def test_commit_writes_the_stored_dc_once(s: Scene) -> None:
    f = check(s)
    assert isinstance(f, Frame)
    with s.store.transaction() as tx:
        tx.add_all(commit_events(f, "commit", mint=tx.mint, state=tx.state))
    assert f.id is not None and f.id in s.state.frames
    again = check(s)
    assert isinstance(again, Frame) and again.dc_source == "stored" and again.stored_dc_write is None
    with pytest.raises(ValueError):
        commit_events(again, "withdraw", mint=lambda p: p, state=s.state)  # type: ignore[arg-type]
    assert s.store.rebuild() == s.state
