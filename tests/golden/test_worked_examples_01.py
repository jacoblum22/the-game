"""Golden tests: the ch.00 and ch.01 worked examples, replayed through engine/resolve with fixed dice (T028).

Each test cites its example. Entities and facts are built to the example's stated numbers; where an example's
ids are illustrative (ch.05/09/13 own them) the nearest real data entry is used and noted. Examples whose steps
are not in engine/resolve (WE-00-1/2/5/6/7/8: time, generation, clocks, substrate, conditions, tags) are covered
by those modules' tests; WE-01-4/8 (bundled delivery, 01.10) and WE-01-12 (certain with cost) belong to the
pipeline driver.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from engine import ids
from engine.resolve.costs import apply_cost
from engine.resolve.frame import auto_commit_allowed, commit_events, frame_check, offer_preview, stored_dc_key
from engine.resolve.gate import RedirectOption, check_gate
from engine.resolve.odds import odds
from engine.resolve.oracle import OracleQuestion, ask_oracle
from engine.resolve.roll import RollRefused, read_result, roll_check
from engine.resolve.rulings import RulingRecord, find_rulings, log_ruling, signature
from engine.resolve.types import Beat, Frame, FrameRefusal, ProposedFrame
from engine.store.conditions import apply_condition
from engine.store.events import ClockRecord, Event
from tests.engine.test_resolve_scene import FixedRng, Scene

MOVE, SETUP, EXERT, TALK = "anc.01_18_4", "anc.01_18_16", "anc.01_18_11", "anc.01_18_7"
OBSERVE, STRIKE, SNEAK, FORCE, HANDLE, EVADE = (
    "anc.01_18_5", "anc.01_18_8", "anc.01_18_13", "anc.01_18_10", "anc.01_18_14", "anc.01_18_12")


def frame(s: Scene, beat: Beat, **p: Any) -> Frame:
    out = frame_check(ProposedFrame(**p), beat, state=s.state, rules=s.rules, store=s.store)
    assert not isinstance(out, FrameRefusal), out.message
    return out


def committed(s: Scene, f: Frame, choice: str = "commit") -> Frame:
    with s.store.transaction() as tx:
        tx.add_all(commit_events(f, choice, mint=tx.mint, state=tx.state))  # type: ignore[arg-type]
    return f


def numbers(f: Frame) -> tuple[int, int, int, int, int, int | None]:
    return (f.modifier.total, f.dc, f.odds.success_or_better, f.odds.critical_success, f.odds.critical_failure,
            f.odds.need)


def clock(s: Scene, cid: str, on: list[str], segments: int = 4, filled: int = 0) -> str:
    rec = ClockRecord(id=cid, name=cid, kind="danger", segments=segments, filled=filled,
                      tick_sources=[{"on": o, "ticks": "U(severity)"} for o in on])
    s.apply([Event.of("clock_created", source="test", clock=rec)])
    return cid


# ------------------------------------------------------------------------------------------- ch.00


def test_we_00_3_unlicensed_lockpick_redirected_by_fallback(tmp_path: Path) -> None:
    """WE-00-3: 'I pick the lock with my knife' -> G3; the license's crude fallback; ruling g3_redirect."""
    s = Scene.new(tmp_path)
    s.fact("world", "door_archive.lock_make", "guild")
    b = s.beat(intent="get through the archive door", method="pick the lock with my knife", gate="G1",
               verb="verb.force", deed_tag="deed.guile.thievery", assertion="it's just a cheap archive lock")
    with s.store.transaction() as tx:
        d = check_gate(b, state=tx.state, rules=s.rules, store=s.store, staged=tx.events, mint=tx.mint)
        tx.add_all(d.events)
    assert d.gate == "G3" and "picking a lock" in d.reason
    assert d.redirect is not None and d.redirect.missing == "lic.training.guile_thievery"
    fb = d.redirect.options[0]
    assert (fb.kind, fb.verb, fb.dc_shift, fb.reach_cap, fb.consequence) == (
        "fallback", "verb.force", 0, "standard", "trait.sense.loud")
    assert {p["type"] for p in d.redirect.acquisition_paths} >= {"mentor", "recognition"}
    rulings = find_rulings(s.store, "g3_redirect:lic.training.guile_thievery")
    assert [r.kind for r in rulings] == ["g3_redirect"]


def test_we_00_4_assembling_a_check(tmp_path: Path) -> None:
    """WE-00-4: break the hasp. +4 vs Moderate 15: 11+ 50/5/5, near miss 15; d20 9 -> near miss; S2 exposure."""
    s = Scene.new(tmp_path)
    bar = s.fact(s.pc, "holds", "obj.iron_bar_03")
    guards = s.fact("world", "keep.guards_awake", True)
    alarm = clock(s, "clk.keep_alarm", ["cost.exposure", "trait.sense.loud"])
    # the player's "the rain has rusted it": an Oracle question, Unlikely, d100 41 -> no (no lever)
    with s.store.transaction() as tx:
        o = ask_oracle(OracleQuestion(subject="world", predicate="door_archive.hasp.rusted", odds="unlikely",
                                      asker=s.pc), state=tx.state, rules=s.rules, rng=FixedRng([41]),
                       mint=tx.mint, store=s.store)
        tx.add_all(o.events)
    assert (o.shape, o.answer) == ("no", False)
    b = s.beat(intent="open the archive door", method="break the hasp", gate="G3", verb="verb.force",
               mode="fallback", fallback_license="lic.training.guile_thievery")
    f = frame(s, b, anchor=FORCE, attribute="might", deed_tag="deed.martial.athletics",
              obstacle={"kind": "tier", "id": "door_archive.hasp", "tier": "moderate"},
              levers=[{"fact_id": bar, "type": "precision"}], stakes_source="aware_opponent_or_observer",
              threatened_cost={"menu_id": "cost.exposure", "source_fact": guards},
              alternate_cost={"menu_id": "cost.gear", "source_fact": bar})
    assert (f.modifier.attribute, f.modifier.competence, f.modifier.edge, f.modifier.circumstance,
            f.modifier.status) == (1, 1, 0, 2, 0)
    assert numbers(f) == (4, 15, 50, 5, 5, 11) and f.odds.near_miss == 15
    assert (f.stakes, f.reach, f.dc_source, f.tier) == ("risky", "standard", "tier", "moderate")
    assert f.mode_price is not None and f.mode_price.mode == "fallback" and "trait.sense.loud" in f.method_consequences
    assert not auto_commit_allowed(f)  # a mode price always waits for an explicit commit (01.7.4)
    committed(s, f)
    assert s.state.fact_value("world", stored_dc_key("door_archive.hasp", FORCE)) == 15  # stored (01.6.5)
    r = roll_check(f, FixedRng([9]))
    assert (r.total, r.margin, r.degree, r.near_miss) == (13, -2, "failure", True)
    rd = read_result(f, r, take_success_at_cost=True)
    assert (rd.cost_severity, rd.delivered_reach, rd.cost_choices) == ("S2", 2, ["cost.exposure", "cost.gear"])
    with s.store.transaction() as tx:
        app = apply_cost(f, rd, "cost.exposure", state=tx.state, rules=s.rules, mint=tx.mint, params={"clock": alarm})
        tx.add_all(app.events)
    assert app.refused is None and s.state.clocks[alarm].filled == 1
    assert s.store.rebuild() == s.state


def test_we_00_9_precedent_reused(tmp_path: Path) -> None:
    """WE-00-9: the chain swing's ruling (Exert + dc + stakes) is found and reused at the millrace."""
    s = Scene.new(tmp_path)
    chain = s.fact("world", "gatehouse.chain", "hangs over the moat")
    sig = signature(EXERT, ["dc:tier re-derived for a tool-changed obstacle", "stakes:current"])
    with s.store.transaction() as tx:
        tx.add(log_ruling(RulingRecord(signature=sig, situation="swing on the gatehouse chain", kind="adaptation",
                                       facts_cited=[chain], frame_summary={"dc": 20, "stakes": "dire"}),
                          tx.mint, store=s.store, staged=tx.events))
    rope = s.fact("world", "mill.hoist_rope", "over the millrace")
    wet = s.fact("world", "mill.hoist_rope.wet", True)
    spear = s.fact(s.pc, "holds", "item.spear")
    b = s.beat(intent="cross the millrace", method="swing across on the hoist rope", gate="G1", verb="verb.exert")
    f = frame(s, b, anchor=EXERT, attribute="agility",
              deltas=[{"knob": "dc", "delta": "tier re-derived for a tool-changed obstacle", "cites_fact": rope},
                      {"knob": "stakes", "delta": "current", "cites_fact": rope}],
              obstacle={"kind": "tier", "id": "millrace", "tier": "hard"}, snags=[wet],
              stakes_source="hazard", stakes_heavy=True, threatened_cost={"menu_id": "cost.footing",
                                                                         "source_fact": rope},
              alternate_cost={"menu_id": "cost.gear", "source_fact": spear})
    assert f.signature == sig and f.precedent is not None and f.precedent.startswith("rul.")
    assert (f.dc, f.stakes, f.modifier.circumstance) == (20, "dire", -2)  # the wet rope is a snag, not a departure


# ------------------------------------------------------------------------------------------- ch.01


def _ogre_scene(tmp_path: Path) -> tuple[Scene, dict[str, str]]:
    s = Scene.new(tmp_path)
    ogre = s.add("adversary", "Ogre", attributes={"agility": 0, "might": 5, "wits": -1})
    k = {"ogre": ogre, "grit": s.fact("world", "courtyard.floor", "grit"),
         "engaged": s.fact(s.pc, "engaged_with", ogre), "size": s.fact(ogre, "size", "large"),
         "lethal": s.fact(ogre, "lethal_context", True), "spear": s.fact(s.pc, "holds", "item.spear")}
    return s, k


def test_we_01_1_sand_then_slide(tmp_path: Path) -> None:
    """WE-01-1: Setup +4 vs 10 (75%, crit 25%), d20 12 success; Move +8 vs 15 (70%, nm 15, cf 5), d20 4 near miss."""
    s, k = _ogre_scene(tmp_path)
    a = s.beat(id="beat.a", intent="blind the ogre", method="throw grit in its eyes", gate="G1",
               verb="verb.setup", target=k["ogre"])
    fa = frame(s, a, anchor=SETUP, attribute="agility",
               deltas=[{"knob": "condition", "delta": "cond.blinded", "cites_fact": k["grit"]}],
               obstacle={"kind": "opposed", "entity": k["ogre"], "defense": "agility"},
               stakes_source="none", threatened_cost={"menu_id": "cost.footing", "source_fact": k["engaged"]})
    assert numbers(fa) == (4, 10, 75, 25, 5, 6) and fa.stakes == "safe"
    assert fa.signature == f"{SETUP}+condition:cond.blinded"
    assert fa.threatened_cost.on_critical_failure == "S1" and fa.threatened_cost.on_failure is None
    committed(s, fa)
    ra = roll_check(fa, FixedRng([12]))
    assert (ra.total, ra.margin, ra.degree) == (16, 6, "success")
    setup = s.fact(s.pc, "setup.blind_ogre", 1)  # the Setup's fact (one use), created by beat A
    b = s.beat(id="beat.b", intent="reach the gate", method="slide between its legs", gate="G1", verb="verb.move",
               target=k["ogre"], shape="sequential")
    fb = frame(s, b, anchor=MOVE, attribute="agility", obstacle={"kind": "opposed", "entity": k["ogre"]},
               levers=[setup, k["size"]], stakes_source="aware_opponent_or_observer", stakes_heavy=True,
               threatened_cost={"menu_id": "cost.footing", "source_fact": k["engaged"]},
               alternate_cost={"menu_id": "cost.gear", "source_fact": k["spear"]})
    assert numbers(fb) == (8, 15, 70, 20, 5, 7) and fb.odds.near_miss == 15
    assert (fb.stakes, fb.lethal, fb.modifier.circumstance) == ("dire", False, 4)
    committed(s, fb)
    rb = roll_check(fb, FixedRng([4]))
    assert (rb.total, rb.margin, rb.degree, rb.near_miss) == (12, -3, "failure", True)
    rd = read_result(fb, rb, take_success_at_cost=True)
    assert rd.cost_severity == "S3"
    spear = s.add("item", "Spear")
    with s.store.transaction() as tx:
        app = apply_cost(fb, rd, "cost.gear", state=tx.state, rules=s.rules, mint=tx.mint, params={"item": spear})
        tx.add_all(app.events)
    assert s.state.fact_value(spear, "condition") == "damaged"
    # other branch: d20 1 -> 9, margin -6, natural 1 -> critical failure -> footing S4 (cond.pinned)
    rc = roll_check(fb, FixedRng([1]))
    assert (rc.total, rc.degree) == (9, "critical_failure")
    rd2 = read_result(fb, rc)
    with s.store.transaction() as tx:
        app = apply_cost(fb, rd2, "cost.footing", state=tx.state, rules=s.rules, mint=tx.mint, form="cond.pinned")
        tx.add_all(app.events)
    assert rd2.cost_severity == "S4" and any(c.condition_id == "cond.pinned" for c in s.state.conditions.values())
    assert s.store.rebuild() == s.state


def test_we_01_2_long_lost_sister(tmp_path: Path) -> None:
    """WE-01-2 both branches: Unlikely 41 -> no -> G4 for the belief, joke +1 vs 10 (60%) d20 9 -> 10 success;
    Unlikely 88 -> yes, and (meaning rolled) -> deceive -1 vs 11 (45%, crit failure 10%), d20 17 success."""
    s = Scene.new(tmp_path)
    tam = s.npc("Tam Harlan", attributes={"wits": 1, "resolve": 0})
    duty = s.fact(tam, "on_duty_at", "the keep gate")
    with s.store.transaction() as tx:
        o = ask_oracle(OracleQuestion(subject=tam, predicate="has_lost_sister", odds="unlikely", asker=s.pc),
                       state=tx.state, rules=s.rules, rng=FixedRng([41]), mint=tx.mint, store=s.store)
        tx.add_all(o.events)
    assert (o.shape, o.answer) == ("no", False) and o.fact_id is not None
    lie = s.beat(intent="be let into the keep", method="convince him I'm his long-lost sister", gate="G4",
                 g4_test="fact", g4_fact=o.fact_id, verb="verb.talk", target=tam,
                 traits=["trait.action.speech"])
    with s.store.transaction() as tx:
        d = check_gate(lie, state=tx.state, rules=s.rules, store=s.store, staged=tx.events, mint=tx.mint,
                       alternatives=[RedirectOption(kind="basic_verb", verb="verb.talk",
                                                    method="play it as a drunk's joke to get him talking")])
        tx.add_all(d.events)
    assert d.gate == "G4" and d.fact_cited == o.fact_id and d.redirect is not None
    assert d.redirect.options[0].verb == "verb.talk" and d.events[0].payload.ruling["kind"] == "g4"  # type: ignore[attr-defined]
    joke = s.beat(intent="learn when the watch changes", method="a drunk's joke", gate="G1", verb="verb.talk",
                  target=tam)
    f = frame(s, joke, anchor=TALK, attribute="presence", obstacle={"kind": "opposed", "entity": tam,
                                                                     "defense": "resolve"},
              stakes_source="goodwill_or_trust", threatened_cost={"menu_id": "cost.closed_door"},
              alternate_cost={"menu_id": "cost.exposure", "source_fact": duty})
    assert numbers(f) == (1, 10, 60, 10, 5, 9) and f.stakes == "risky"
    committed(s, f)
    r = roll_check(f, FixedRng([9]))
    assert (r.total, r.degree) == (10, "success")  # a tie goes to the actor
    # branch B: a fresh game; 88 is a double -> yes, and; the "and" is two tbl.meaning words
    s2 = Scene.new(tmp_path / "b")
    tam2 = s2.npc("Tam Harlan", attributes={"wits": 1, "resolve": 0})
    duty2 = s2.fact(tam2, "on_duty_at", "the keep gate")
    with s2.store.transaction() as tx:
        o2 = ask_oracle(OracleQuestion(subject=tam2, predicate="has_lost_sister", odds="unlikely", asker=s2.pc),
                        state=tx.state, rules=s2.rules, rng=FixedRng([88, 97, 44]), mint=tx.mint, store=s2.store)
        tx.add_all(o2.events)
    assert (o2.shape, o2.extreme, len(o2.meaning)) == ("yes_and", True, 2)
    assert s2.state.fact_value(tam2, "has_lost_sister.and") == o2.meaning
    deceive = s2.beat(intent="be let in", method="claim to be his lost sister", gate="G1", verb="verb.talk",
                      target=tam2)
    f2 = frame(s2, deceive, anchor=TALK, attribute="presence",
               obstacle={"kind": "opposed", "entity": tam2, "defense": "wits"}, snags=[o2.fact_id],
               stakes_source="aware_opponent_or_observer", stakes_heavy=True,
               threatened_cost={"menu_id": "cost.exposure", "source_fact": duty2},
               alternate_cost={"menu_id": "cost.closed_door"})
    assert numbers(f2) == (-1, 11, 45, 5, 10, 12) and f2.stakes == "dire"
    committed(s2, f2)
    assert roll_check(f2, FixedRng([17])).degree == "success"


def test_we_01_3_burning_barn(tmp_path: Path) -> None:
    """WE-01-3: round 1 Observe +1 vs Easy 10 (60%); round 2 Handle +1 vs 11 (55%); round 3 Move +2 vs 15 (40%)
    with choking (status -2); the trough as Protective lever takes the lethal Dire frame to Risky, not lethal."""
    s = Scene.new(tmp_path)
    smoke = s.fact("world", "barn.smoke", "thick")
    s.fact("world", "lethal_context", True)  # the roof groaned: the lethal warning is on record
    roof = clock(s, "clk.barn_roof", ["cost.time"])
    f1 = frame(s, s.beat(intent="find the horse", method="search the barn", gate="G1", verb="verb.observe"),
               anchor=OBSERVE, attribute="wits", obstacle={"kind": "tier", "id": "barn.horse", "tier": "easy"},
               snags=[smoke], stakes_source="listening_clock", stakes_heavy=True,
               threatened_cost={"menu_id": "cost.time"}, alternate_cost={"menu_id": "cost.exposure"})
    assert numbers(f1)[:3] == (1, 10, 60) and (f1.stakes, f1.lethal) == ("dire", False)
    horse = s.add("npc", "Horse", attributes={"resolve": 1})
    cloak = s.fact(s.pc, "cloak_over", horse)
    f2 = frame(s, s.beat(intent="lead the horse", method="calm it and lead it", gate="G1", verb="verb.handle",
                         target=horse),
               anchor=HANDLE, attribute="presence", deltas=[{"knob": "dc", "delta": "opposed (animals)",
                                                             "cites_fact": cloak}],
               obstacle={"kind": "opposed", "entity": horse, "defense": "resolve"}, levers=[cloak], snags=[smoke],
               stakes_source="listening_clock", stakes_heavy=True, threatened_cost={"menu_id": "cost.time"},
               alternate_cost={"menu_id": "cost.exposure"})
    assert numbers(f2)[:4] == (1, 11, 55, 5)
    with s.store.transaction() as tx:
        tx.add_all(apply_condition(tx.state, tx.mint, s.rules, s.pc, "cond.choking").events)
    doorway = s.fact("world", "barn.doorway", "the way in")
    trough = s.fact("world", "barn.trough", "by the door")
    b3 = s.beat(intent="get out", method="run through the burning doorway", gate="G1", verb="verb.move")
    base = dict(anchor=MOVE, attribute="agility", obstacle={"kind": "tier", "id": "barn.doorway", "tier": "moderate"},
                levers=[doorway], snags=[smoke], stakes_source="hazard", stakes_heavy=True, lethal=True,
                threatened_cost={"menu_id": "cost.harm"}, alternate_cost={"menu_id": "cost.time"})
    lethal = frame(s, b3, **base)
    assert (lethal.modifier.status, lethal.modifier.total, lethal.stakes, lethal.lethal) == (-2, 2, "dire", True)
    assert offer_preview(lethal).lethal and not auto_commit_allowed(lethal)
    safer = frame(s, b3, **{**base, "levers": [doorway, {"fact_id": trough, "type": "protective"}]})
    assert (safer.stakes, safer.lethal, safer.odds.success_or_better, safer.odds.need) == ("risky", False, 40, 13)
    assert safer.threatened_cost.on_failure == "S2"
    committed(s, safer)
    assert roll_check(safer, FixedRng([15])).degree == "success"
    assert s.state.clocks[roof].filled == 0


def test_we_01_5_pole_vault(tmp_path: Path) -> None:
    """WE-01-5: the climb is stored Moderate 15; the vault re-derives the tier (Hard 20) under a new key;
    +6 vs 20 (35%), d20 13 -> 19 near miss -> alternate cost.gear S2 (the spear left outside)."""
    s = Scene.new(tmp_path)
    climb_key = stored_dc_key("wall_north", EXERT)
    s.fact("world", climb_key, 15, source="ruling")
    spear_item = s.add("item", "Spear")
    spear = s.fact(s.pc, "holds", spear_item)
    ground = s.fact("world", "wall_north.approach", "open ground")
    patrol = clock(s, "clk.patrol", ["cost.time"], filled=2)
    climb = frame(s, s.beat(intent="get over the wall", method="climb it", gate="G1", verb="verb.exert"),
                  anchor=EXERT, attribute="might", obstacle={"kind": "tier", "id": "wall_north", "tier": "moderate"},
                  stakes_source="listening_clock", threatened_cost={"menu_id": "cost.time"},
                  alternate_cost={"menu_id": "cost.gear", "source_fact": spear})
    assert (climb.dc_source, numbers(climb)[:3], climb.stored_dc_write) == ("stored", (2, 15, 40), None)
    vault = s.beat(intent="get over the wall", method="pole-vault with my spear", gate="G1", verb="verb.exert")
    f = frame(s, vault, anchor=EXERT, attribute="agility",
              deltas=[{"knob": "dc", "delta": "tier re-derived for a tool-changed obstacle", "cites_fact": spear}],
              obstacle={"kind": "tier", "id": "wall_north", "tier": "hard"}, levers=[ground],
              stakes_source="height_or_depth", threatened_cost={"menu_id": "cost.harm"},
              alternate_cost={"menu_id": "cost.gear", "source_fact": spear})
    assert numbers(f)[:3] == (6, 20, 35) and f.odds.need == 14 and f.stakes == "risky"
    assert f.stored_dc_write is not None and f.stored_dc_write["predicate"] == stored_dc_key(
        "wall_north", EXERT, "tier re-derived for a tool-changed obstacle")
    committed(s, f)
    r = roll_check(f, FixedRng([13]))
    assert (r.total, r.margin, r.near_miss) == (19, -1, True)
    rd = read_result(f, r, take_success_at_cost=True)
    with s.store.transaction() as tx:
        app = apply_cost(f, rd, "cost.gear", state=tx.state, rules=s.rules, mint=tx.mint,
                         params={"item": spear_item, "place": "outside wall_north"})
        tx.add_all(app.events)
    assert s.state.fact_value(spear_item, "location") == "outside wall_north" and rd.delivered_reach == 2
    assert s.state.clocks[patrol].filled == 2


def test_we_01_6_emulate_and_no_fallback(tmp_path: Path) -> None:
    """WE-01-6. A: no arcane license, crude_fallback none -> G3, still an option and a path. B: Ash emulates
    (G2 emulate: DC 13 + 5 = 18; +5 -> 13+ 40%; Focus x2; Limited); near miss; drain cannot land (Focus 0) so
    the threatened harm lands through the harm hook."""
    s = Scene.new(tmp_path)
    a = s.beat(intent="cast the spell I saw", method="cast the flame spell the hedge-witch cast", uses_power=True,
               verb="verb.observe")  # 00.12.3: a supernatural technique, no technique held -> G3, computed
    d = check_gate(a, state=s.state, rules=s.rules,
                   alternatives=[RedirectOption(kind="basic_verb", verb="verb.observe",
                                                method="fix what you saw before it fades")])
    assert d.gate == "G3" and d.redirect is not None
    assert [o.kind for o in d.redirect.options] == ["basic_verb"] and d.redirect.acquisition_paths
    ash = s.add("pc", "Ash", attributes={"intellect": 3}, competence={"deed.arcane.fire": 2},
                licenses=["lic.training.arcane_fire"], quantities={"focus": (0, 0, 4), "vitality": (12, 0, 12)})
    cultist = s.npc("Cultist", attributes={"agility": 3})
    b = s.beat(actor=ash, intent="lash the cultist", method="the flame whip I saw cast", gate="G2",
               license="lic.training.arcane_fire", mode="emulate", target=cultist)
    g = check_gate(b, state=s.state, rules=s.rules)
    assert (g.gate, g.mode) == ("G2", "emulate")
    f = frame(s, b, anchor=STRIKE, attribute="intellect", deed_tag="deed.arcane.fire",
              obstacle={"kind": "opposed", "entity": cultist, "defense": "agility"},
              stakes_source="hazard", threatened_cost={"menu_id": "cost.harm"},
              alternate_cost={"menu_id": "cost.drain"})
    assert numbers(f)[:3] == (5, 18, 40) and f.odds.need == 13
    assert f.mode_price is not None and (f.mode_price.dc_shift, f.mode_price.focus_mult) == (5, 2)
    assert f.reach == "limited" and f.stakes == "risky"
    committed(s, f)
    r = roll_check(f, FixedRng([12]))
    assert (r.total, r.margin, r.near_miss) == (17, -1, True)
    rd = read_result(f, r, take_success_at_cost=True)
    seen: list[tuple[str, str, bool]] = []

    def harm_hook(target: str, severity: str, *, lethal: bool, harm_tags: list[str],
                  frame_id: str | None) -> list[Event]:
        seen.append((target, severity, lethal))
        return []

    with s.store.transaction() as tx:
        drain = apply_cost(f, rd, "cost.drain", state=tx.state, rules=s.rules, mint=tx.mint)
        harm = apply_cost(f, rd, "cost.harm", state=tx.state, rules=s.rules, mint=tx.mint, harm_hook=harm_hook)
    assert drain.refused is not None and "cannot land in full" in drain.refused
    assert harm.refused is None and seen == [(ash, "S2", False)] and rd.delivered_reach == 1


def test_we_01_7_repetition_throttle(tmp_path: Path) -> None:
    """WE-01-7: three shots at Guard 16 with +5: 11+ (50%), 13+ (40%), 15+ (30%); at least one hit 79%."""
    s = Scene.new(tmp_path, pc_competence={"deed.martial.archery": 2})
    beast = s.add("adversary", "Creature", defenses={"guard": 16})
    pcts = []
    for k in (1, 2, 3):
        f = frame(s, s.beat(intent="kill it", method="shoot it", gate="G1", verb="verb.strike", target=beast,
                            shape="repeated"),
                  anchor=STRIKE, attribute="agility", deed_tag="deed.martial.archery", repetition_instance=k,
                  obstacle={"kind": "entity_defense", "entity": beast, "defense": "guard"}, stakes_source="none",
                  threatened_cost={"menu_id": "cost.drain"})
        pcts.append((f.odds.need, f.odds.success_or_better))
        assert len([x for x in f.snags if x.engine]) == (0 if k == 1 else 1)
    assert pcts == [(11, 50), (13, 40), (15, 30)]
    miss = 1.0
    for _, p in pcts:
        miss *= 1 - p / 100
    assert round(100 * (1 - miss)) == 79


def test_we_01_9_chandelier_rope(tmp_path: Path) -> None:
    """WE-01-9: Strike with two knobs (object tier, object state) -> Hard 20, +5 -> 15+ (30%), d20 18 success;
    the captain Evades an S3 hazard: effect DC Hard 20, +6 -> 14+ (35%), d20 9 -> 15 failure."""
    s = Scene.new(tmp_path, pc_competence={"deed.martial.archery": 2})
    rope = s.fact("world", "hall.chandelier_rope", "holds the iron wheel over the table")
    hesk = s.npc("Captain Hesk", attributes={"agility": 2}, competence={"deed.martial": 4}, defenses={"guard": 16})
    s.fact(hesk, "aware_of", s.pc)
    bow = s.fact(s.pc, "holds", "item.bow")
    f = frame(s, s.beat(intent="drop the chandelier on the captain", method="shoot the rope", gate="G1",
                        verb="verb.strike"),
              anchor=STRIKE, attribute="agility", deed_tag="deed.martial.archery",
              deltas=[{"knob": "dc", "delta": "object tier", "cites_fact": rope},
                      {"knob": "reach_unit", "delta": "object state", "cites_fact": rope}],
              obstacle={"kind": "tier", "id": "hall.chandelier_rope", "tier": "hard"},
              stakes_source="aware_opponent_or_observer", threatened_cost={"menu_id": "cost.exposure"},
              alternate_cost={"menu_id": "cost.gear", "source_fact": bow})
    assert numbers(f)[:3] == (5, 20, 30) and f.odds.need == 15
    assert f.signature == f"{STRIKE}+dc:object tier+reach_unit:object state"
    direct = frame(s, s.beat(intent="hurt the captain", method="shoot him", gate="G1", verb="verb.strike",
                             target=hesk),
                   anchor=STRIKE, attribute="agility", deed_tag="deed.martial.archery",
                   obstacle={"kind": "entity_defense", "entity": hesk, "defense": "guard"}, stakes_source="none",
                   threatened_cost={"menu_id": "cost.drain"})
    assert (direct.odds.need, direct.odds.success_or_better) == (11, 50)
    committed(s, f)
    assert roll_check(f, FixedRng([18])).degree == "success"
    ev = frame(s, s.beat(actor=hesk, intent="get clear", method="dive aside", gate="G1", verb="verb.evade",
                         declared=False),
               anchor=EVADE, attribute="agility", deed_tag="deed.martial.athletics",
               obstacle={"kind": "effect", "severity": "S3"}, stakes_source="hazard", stakes_heavy=True,
               threatened_cost={"menu_id": "cost.harm"}, alternate_cost={"menu_id": "cost.footing"})
    assert (ev.dc_source, ev.dc, ev.modifier.total, ev.odds.need, ev.odds.success_or_better) == (
        "effect", 20, 6, 14, 35)
    committed(s, ev)
    r = roll_check(ev, FixedRng([9]))
    assert (r.total, r.degree, r.near_miss) == (15, "failure", False)


def test_we_01_10_play_dead_then_torch(tmp_path: Path) -> None:
    """WE-01-10: playing dead is G4 (zero reach); intimidation ties Presence/Might -> the lower (Presence), OFFER
    names Might; the charge: +4 vs 13, Limited, Dire and lethal (never auto-committed); d20 9 -> 13 success."""
    s = Scene.new(tmp_path)
    pack = s.add("adversary", "Wolf Pack", attributes={"resolve": 1}, defenses={"intimidation": 13})
    lethal_ctx = s.fact(pack, "lethal_context", True)
    torch = s.fact(s.pc, "holds", "a lit torch")
    # R2-C: no role proposes a gate class; the Reader cites the fact that rules the method out (00.12.3). The
    # example's zero-reach test (two effect factors) has no proposer since the Reader shrank: the fact stands in.
    scent = s.fact(pack, "hunts_by", "scent: a still body fools no wolf")
    dead = s.beat(intent="the wolves lose interest", method="play dead", g4_fact=scent, target=pack)
    with s.store.transaction() as tx:
        d = check_gate(dead, state=tx.state, rules=s.rules, store=s.store, staged=tx.events, mint=tx.mint,
                       alternatives=[RedirectOption(kind="basic_verb", verb="verb.talk",
                                                    method="fire and a show of size")])
        tx.add_all(d.events)
    assert d.gate == "G4" and d.redirect is not None and d.redirect.options[0].verb == "verb.talk"
    roar = s.beat(intent="drive the wolves off", method="wave the torch and roar", gate="G1", verb="verb.talk",
                  target=pack)
    kw: dict[str, Any] = dict(anchor=TALK, obstacle={"kind": "entity_defense", "entity": pack,
                                                       "defense": "intimidation"},
                              stakes_source="aware_opponent_or_observer", stakes_heavy=True, lethal=True,
                              reach_one_factor=True,  # 01.6.11: harm from the pack, cited
                              threatened_cost={"menu_id": "cost.harm", "source_fact": lethal_ctx},
                              alternate_cost={"menu_id": "cost.footing"})
    tie = frame(s, roar, attribute="might", attribute_tie="presence", **kw)
    assert (tie.attribute, tie.alternative_attribute) == ("presence", "might")
    charge = s.beat(intent="drive the wolves off", method="charge them swinging the torch", gate="G1",
                    verb="verb.talk", target=pack)
    f = frame(s, charge, attribute="might", levers=[torch], **kw)
    assert numbers(f)[:3] == (4, 13, 60) and (f.reach, f.stakes, f.lethal) == ("limited", "dire", True)
    assert not auto_commit_allowed(f)
    with pytest.raises(ValueError):
        commit_events(f, "auto", mint=lambda p: f"{p}.x", state=s.state)
    committed(s, f)
    assert roll_check(f, FixedRng([9])).degree == "success"


def test_we_01_11_river_spirit(tmp_path: Path) -> None:
    """WE-01-11: Unlikely; 62 -> no -> Talk to the river is G4 (fact); 83 -> plain yes (outside 76-80, not a
    double) -> Talk +1 vs 16: 15+ (30%), Limited by scale, Dire."""
    s = Scene.new(tmp_path)
    with s.store.transaction() as tx:
        o = ask_oracle(OracleQuestion(subject="world", predicate="river_ash.spirit", odds="unlikely", asker=s.pc),
                       state=tx.state, rules=s.rules, rng=FixedRng([62]), mint=tx.mint, store=s.store)
        tx.add_all(o.events)
    assert (o.shape, o.answer) == ("no", False)
    d = check_gate(s.beat(intent="cross the river", method="ask the river to calm", gate="G4", g4_test="fact",
                          g4_fact=o.fact_id), state=s.state, rules=s.rules)
    assert d.gate == "G4" and d.fact_cited == o.fact_id
    s2 = Scene.new(tmp_path / "b")
    with s2.store.transaction() as tx:
        o2 = ask_oracle(OracleQuestion(subject="world", predicate="river_ash.spirit", odds="unlikely", asker=s2.pc),
                        state=tx.state, rules=s2.rules, rng=FixedRng([83]), mint=tx.mint, store=s2.store)
        tx.add_all(o2.events)
    assert (o2.shape, o2.extreme, o2.twist) == ("yes", False, False)
    spirit = s2.npc("River Spirit", attributes={"resolve": 4}, competence={"deed.influence": 2})
    f = frame(s2, s2.beat(intent="calm the river", method="heartfelt speech", gate="G1", verb="verb.talk",
                          target=spirit),
              anchor=TALK, attribute="presence",
              obstacle={"kind": "opposed", "entity": spirit, "defense": "resolve", "defense_tag": "deed.influence"},
              reach_one_factor=True, stakes_source="goodwill_or_trust", stakes_heavy=True,
              threatened_cost={"menu_id": "cost.closed_door"},
              alternate_cost={"menu_id": "cost.time", "source_fact": o2.fact_id})
    assert numbers(f)[:3] == (1, 16, 30) and (f.reach, f.stakes) == ("limited", "dire")


def test_we_01_13_back_door(tmp_path: Path) -> None:
    """WE-01-13: Likely; 34 -> plain yes; Sneak +6 vs the highest notice 11: 5+ (80%), d20 6 -> 12 success.
    Other branch: 22 -> a double -> no, and (meaning rolled)."""
    s = Scene.new(tmp_path)
    t1 = s.npc("Thug One", attributes={"wits": 1})
    t2 = s.npc("Thug Two", attributes={"wits": 0})
    arguing = s.fact(t1, "arguing_with", t2)
    with s.store.transaction() as tx:
        o = ask_oracle(OracleQuestion(subject="world", predicate="inn.back_door", odds="likely", asker=s.pc),
                       state=tx.state, rules=s.rules, rng=FixedRng([34]), mint=tx.mint, store=s.store)
        tx.add_all(o.events)
    assert o.shape == "yes"
    f = frame(s, s.beat(intent="slip out", method="sneak out the back while they argue", gate="G1",
                        verb="verb.sneak", shape="conditional"),
              anchor=SNEAK, attribute="agility", obstacle={"kind": "opposed", "entities": [t1, t2], "defense": "wits"},
              levers=[arguing], stakes_source="aware_opponent_or_observer",
              threatened_cost={"menu_id": "cost.exposure", "source_fact": arguing},
              alternate_cost={"menu_id": "cost.time", "source_fact": arguing})
    assert numbers(f)[:3] == (6, 11, 80) and f.odds.need == 5 and f.defender == t1
    assert f.stakes == "risky" and not auto_commit_allowed(f)  # DL-01-32: a Risky frame never auto-commits
    committed(s, f)
    assert roll_check(f, FixedRng([6])).total == 12
    s2 = Scene.new(tmp_path / "b")
    with s2.store.transaction() as tx:
        o2 = ask_oracle(OracleQuestion(subject="world", predicate="inn.back_door", odds="likely", asker=s2.pc),
                        state=tx.state, rules=s2.rules, rng=FixedRng([22, 5, 60]), mint=tx.mint, store=s2.store)
        tx.add_all(o2.events)
    assert (o2.shape, o2.answer, o2.extreme) == ("no_and", False, True) and len(o2.meaning) == 2


def test_we_01_14_i_kill_it(tmp_path: Path) -> None:
    """WE-01-14: the kill is an assertion; Strike +4 vs Guard 13: 9+ (60%); d20 1 -> 5 critical failure ->
    the threatened footing at S3."""
    s = Scene.new(tmp_path)
    hound = s.add("adversary", "Hound", defenses={"guard": 13})
    jaws = s.fact(hound, "engaged_with", s.pc)
    f = frame(s, s.beat(intent="the hound dead", method="stab it", assertion="through the heart and kill it",
                        gate="G1", verb="verb.strike", target=hound),
              anchor=STRIKE, attribute="agility", obstacle={"kind": "entity_defense", "entity": hound,
                                                            "defense": "guard"},
              stakes_source="aware_opponent_or_observer", threatened_cost={"menu_id": "cost.footing",
                                                                           "source_fact": jaws},
              alternate_cost={"menu_id": "cost.harm", "source_fact": jaws})  # 01.6.11: an armed party, cited
    assert numbers(f)[:3] == (4, 13, 60) and f.odds.need == 9
    committed(s, f)
    r = roll_check(f, FixedRng([1]))
    assert (r.total, r.degree) == (5, "critical_failure")
    assert read_result(f, r).cost_severity == "S3"


def test_we_01_16_elven_runes(tmp_path: Path) -> None:
    """WE-01-16: a persuasive assertion; reading an unknown script is Observe's exclude; no language held -> G3.
    (The example's lic.lang.elvish_script is illustrative; data's lic.lang.elvish is used, whose fallback is
    gesture and tone.) The offered alternative, read the stone, frames Observe +3 vs Easy 10, Limited."""
    s = Scene.new(tmp_path)
    s.fact("world", "shrine.inscription.script", "elvish_old")
    b = s.beat(intent="read the inscription", method="reading an unknown script: the old elven runes",
               verb="verb.observe", assertion="I'm a hunter, I read signs all day")  # the tongue is found by code
    d = check_gate(b, state=s.state, rules=s.rules, alternatives=[
        RedirectOption(kind="basic_verb", verb="verb.observe", method="read the carving's placement and wear")])
    assert d.gate == "G3" and d.redirect is not None and d.redirect.missing == "lic.lang.elvish"
    assert [o.kind for o in d.redirect.options] == ["fallback", "basic_verb"]
    f = frame(s, s.beat(intent="learn what the stone says", method="read the carving's placement and wear",
                        gate="G1", verb="verb.observe"),
              anchor=OBSERVE, attribute="wits", obstacle={"kind": "tier", "id": "shrine.inscription", "tier": "easy"},
              reach_whole=False, stakes_source="none", threatened_cost={"menu_id": "cost.drain"})
    assert numbers(f)[:3] == (3, 10, 70) and f.reach == "limited"


def test_we_01_17_failure_costs_time(tmp_path: Path) -> None:
    """WE-01-17: Observe +3 vs stored Moderate 15; Risky; d20 5 -> 8 failure -> cost.time S2: clock +1."""
    s = Scene.new(tmp_path)
    s.fact("world", stored_dc_key("reading_room", OBSERVE), 15, source="ruling")
    archivist = clock(s, "clk.archivist_returns", ["cost.time"], segments=4)
    f = frame(s, s.beat(intent="find the Harlan ledger", method="search the shelves", gate="G1",
                        verb="verb.observe"),
              anchor=OBSERVE, attribute="wits", obstacle={"kind": "tier", "id": "reading_room", "tier": "moderate"},
              stakes_source="listening_clock", threatened_cost={"menu_id": "cost.time"},
              alternate_cost={"menu_id": "cost.exposure"})
    assert (f.dc_source, numbers(f)[:3]) == ("stored", (3, 15, 45))
    committed(s, f)
    r = roll_check(f, FixedRng([5]))
    rd = read_result(f, r)
    assert (r.total, r.degree, rd.cost_severity, rd.delivered_reach) == (8, "failure", "S2", 0)
    with s.store.transaction() as tx:
        tx.add_all(apply_cost(f, rd, "cost.time", state=tx.state, rules=s.rules, mint=tx.mint).events)
    assert s.state.clocks[archivist].filled == 1


def test_we_01_18_one_rung_error() -> None:
    """WE-01-18: a one-rung error at +5 moves Moderate 55% to Hard 30%."""
    assert (odds(5, 15).success_or_better, odds(5, 20).success_or_better) == (55, 30)


def test_we_01_19_fate_reroll(tmp_path: Path) -> None:
    """WE-01-19: Force +2 vs Hard 20, Dire and lethal; d20 3 -> 5 critical failure; the fate reroll (on_roll)
    -> 18 -> 20 success. Kept: footing S4 (swept away: a non-condition form, deferred)."""
    s = Scene.new(tmp_path)
    s.fact("world", "lethal_context", True)
    sluice = s.fact("world", "sluice.water_rising", True)
    f = frame(s, s.beat(intent="open the sluice", method="force the jammed gate", gate="G1", verb="verb.force"),
              anchor=FORCE, attribute="might", obstacle={"kind": "tier", "id": "sluice_gate", "tier": "hard"},
              stakes_source="hazard", stakes_heavy=True, lethal=True,
              threatened_cost={"menu_id": "cost.footing", "source_fact": sluice},
              alternate_cost={"menu_id": "cost.time", "source_fact": sluice})
    assert numbers(f)[:2] == (2, 20) and f.lethal
    committed(s, f)
    rerolled = roll_check(f, FixedRng([3, 18]), on_roll=lambda r: r.degree == "critical_failure")
    assert (rerolled.d20, rerolled.total, rerolled.degree, rerolled.rerolled_from) == (18, 20, "success", [3])
    kept = roll_check(f, FixedRng([3]), on_roll=lambda r: False)
    assert (kept.total, kept.margin, kept.degree) == (5, -15, "critical_failure")
    rd = read_result(f, kept)
    assert rd.cost_severity == "S4"
    app = apply_cost(f, rd, "cost.footing", state=s.state, rules=s.rules, mint=lambda p: f"{p}.99",
                     form="move to next lower place")
    assert app.refused is None and app.deferred is not None and app.events == []


def test_we_01_20_group_and_help(tmp_path: Path) -> None:
    """WE-01-20: all-must uses Oda's base +1; Wren's Help is one Precision lever -> +3 vs 12: 9+ (60%)."""
    s = Scene.new(tmp_path)
    oda = s.add("companion", "Oda", attributes={"agility": 0}, competence={"deed": 1})
    sentry = s.npc("Sentry", attributes={"wits": 2})
    s.fact(sentry, "watching", "the camp")
    helped = s.fact(s.pc, "help.picks_the_moment", oda)
    f = frame(s, s.beat(actor=oda, intent="pass the camp unseen", method="sneak past together", gate="G1",
                        verb="verb.sneak"),
              anchor=SNEAK, attribute="agility", obstacle={"kind": "opposed", "entity": sentry, "defense": "wits"},
              levers=[helped], stakes_source="aware_opponent_or_observer",
              threatened_cost={"menu_id": "cost.exposure"}, alternate_cost={"menu_id": "cost.time",
                                                                          "source_fact": helped})
    assert numbers(f)[:3] == (3, 12, 60) and f.odds.need == 9


def test_offer_never_rolls_uncommitted(tmp_path: Path) -> None:
    """01.1.3 / 00.13.2: no roll without a committed frame."""
    s, k = _ogre_scene(tmp_path)
    f = frame(s, s.beat(intent="x", method="slide", gate="G1", verb="verb.move", target=k["ogre"]), anchor=MOVE,
              attribute="agility", obstacle={"kind": "opposed", "entity": k["ogre"]}, stakes_source="none",
              threatened_cost={"menu_id": "cost.footing", "source_fact": k["engaged"]})
    with pytest.raises(RollRefused):
        roll_check(f, FixedRng([10]))
    assert ids.FRAME == "frame"
