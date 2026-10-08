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


def test_a_ch15_anchor_names_its_defense_in_the_dc_knob(s: Scene) -> None:
    """ch.15 anchors have no verb: the `dc` knob carries the defense (15.4.1 Resolve, Wits by delta; 15.6.1 mask
    = a presence defense). The Framer schema has no `defense` field, so without this every opposed social frame
    was refused ("name the defense attribute")."""
    from engine.resolve.frame import _defense_attrs

    persuade, insight = s.rules.anchors["anc.15_4_1"], s.rules.anchors["anc.15_6_1"]
    assert _defense_attrs(None, persuade, s.rules) == ["resolve"]
    assert _defense_attrs(None, persuade, s.rules, "Wits") == ["wits"]
    assert _defense_attrs(None, insight, s.rules) == ["presence"]
    assert _defense_attrs(None, s.rules.anchors[MOVE], s.rules) == ["might", "agility"]  # verb text, unchanged


def test_a_ch06_conflict_anchor_is_resisted_like_its_beats_verb(s: Scene) -> None:
    """Playtest 20261008 fighter, 8 Framer calls: Strike (conflict frame) anc.06_4_3 has no verb and a null `dc`
    knob, so every attack framed on it was refused "name the defense attribute" (a field the schema does not have)
    and fell to the default frame. The beat's own verb names the defense."""
    from engine.resolve.frame import _defense_attrs

    conflict, strike = s.rules.anchors["anc.06_4_3"], s.rules.anchors["anc.01_18_8"]
    assert _defense_attrs(None, conflict, s.rules, verb="verb.strike") == _defense_attrs(None, strike, s.rules)
    f = check(s, {"verb": "verb.strike", "target": "npc.guard", "against_will": True}, anchor="anc.06_4_3",
              attribute="might", obstacle={"kind": "opposed", "entity": "npc.guard"})
    assert not (isinstance(f, FrameRefusal) and f.field == "obstacle.defense"), f


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


def test_a_cost_form_never_undoes_the_beats_own_success(s: Scene) -> None:
    """Playtest 20261008 fighter 19-22 (01.9.3: a cost never negates a success): a grapple taken as success at a
    cost paid "she pulls her sleeve free ... as she tears away", so the narration had her both held and gone. A
    cost form on a person acted on against their will may not undo the act; the Framer is re-asked."""
    grab = {"verb": "verb.grapple", "target": "npc.guard", "against_will": True}
    kw: dict[str, Any] = {"anchor": "anc.01_18_9", "attribute": "might",
                          "obstacle": {"kind": "opposed", "entity": "npc.guard"}}
    for undo in ("She pulls her sleeve free of your grip and you stumble as she tears away",
                 "She refuses to be held and walks off", "your grip on her slips and you go down"):
        refused(check(s, grab, threatened_cost={"menu_id": "cost.drain", "form_intent": undo}, **kw), 10,
                "never undoes")
        refused(check(s, grab, stakes_source="consumed_resource", threatened_cost={"menu_id": "cost.drain"},
                      alternate_cost={"menu_id": "cost.shortfall", "form_intent": undo}, **kw), 10, "never undoes")
    ok = check(s, grab, threatened_cost={"menu_id": "cost.drain", "form_intent": "the struggle leaves you winded"},
               **kw)
    assert isinstance(ok, Frame), ok
    away = check(s, threatened_cost={"menu_id": "cost.drain", "form_intent": "you slip free of the mud, spent"})
    assert isinstance(away, Frame)  # no one acted on: nothing to undo


def test_stakes_raised_by_a_snag_get_the_rules_alternate(s: Scene) -> None:
    """Playtest saves: 7 Framer refusals "a risky frame needs an alternate cost" on frames declared Safe (source
    none, so no alternate offered) that a second, Protective snag raised to Risky (00.3.9(b)). The engine raised
    the stakes, so it supplies 01.13.1's first fitting alternate, as the critical-failure guard already did."""
    a, b = s.fact("world", "mud", "deep"), s.fact("world", "wind", "gusting")
    f = check(s, snags=[a, b])
    assert isinstance(f, Frame), f
    assert f.stakes == "risky" and f.alternate_cost is not None


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
    f3 = check(s, snags=[a, b], repetition_instance=3, alternate_cost={"menu_id": "cost.shortfall"})
    assert isinstance(f3, Frame) and f3.modifier.circumstance == -4  # capped
    # 00.3.9(b): one cited Precision snag; the second hindering fact raises the stakes instead
    assert [x.type for x in f3.snags if not x.engine] == ["precision", "protective"] and f3.stakes == "risky"


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
    f = check(s, stakes_source="consumed_resource", threatened_cost={"menu_id": "cost.drain"},
              alternate_cost={"menu_id": "cost.shortfall"})
    assert isinstance(f, Frame) and legal_trades(f) == ["go_big", "play_it_safe"]
    big = check(s, stakes_source="consumed_resource", trade="go_big",
                threatened_cost={"menu_id": "cost.drain"}, alternate_cost={"menu_id": "cost.shortfall"})
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
