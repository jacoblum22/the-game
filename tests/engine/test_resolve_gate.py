"""engine/resolve/gate.py: G0-G4 against holdings and data (01.3), the PR-01-5 redirect, rulings (FR-022)."""

from __future__ import annotations

from pathlib import Path

from engine.resolve.gate import check_gate, excluded_by, held_license, would_be_license
from engine.resolve.rulings import find_rulings
from engine.store.conditions import apply_condition
from engine.store.events import Event, LicenseInstance
from tests.engine.test_resolve_scene import Scene


def test_g0_passes_through(tmp_path: Path) -> None:
    s = Scene.new(tmp_path)
    assert check_gate(s.beat(gate="G0"), state=s.state, rules=s.rules).gate == "G0"


def test_g1_needs_a_real_verb_and_its_covers(tmp_path: Path) -> None:
    s = Scene.new(tmp_path)
    ok = check_gate(s.beat(gate="G1", verb="verb.force", method="shove the cart into the doorway",
                           method_class="shove"), state=s.state, rules=s.rules)
    assert (ok.gate, ok.verb) == ("G1", "verb.force")
    bad_verb = check_gate(s.beat(gate="G1", verb="verb.fly"), state=s.state, rules=s.rules)
    assert bad_verb.gate == "G3" and "unknown basic verb" in bad_verb.reason
    bad_class = check_gate(s.beat(gate="G1", verb="verb.force", method_class="lockpicking"), state=s.state,
                           rules=s.rules)
    assert bad_class.gate == "G3" and bad_class.redirect is not None and bad_class.redirect.options


def test_excludes_match_a_literal_mention(tmp_path: Path) -> None:
    s = Scene.new(tmp_path)
    force = s.rules.verb("verb.force")
    ex = excluded_by(force, "I pick the lock")
    assert ex is not None and ex["what"] == "picking a lock"
    assert excluded_by(force, "I break the lock") is None


def test_g2_needs_the_license_held(tmp_path: Path) -> None:
    s = Scene.new(tmp_path, pc_licenses=["lic.lang.common", "lic.training.guile_thievery"])
    b = s.beat(gate="G2", license="lic.training.guile_thievery", method="pick the lock", verb="verb.handle")
    assert check_gate(b, state=s.state, rules=s.rules).gate == "G2"
    lacks = check_gate(s.beat(gate="G2", license="lic.training.arcane_fire", method="cast"), state=s.state,
                       rules=s.rules)
    assert lacks.gate == "G3" and "not held" in lacks.reason and lacks.redirect is not None
    assert lacks.redirect.missing == "lic.training.arcane_fire"
    s.apply([Event.of("license_revoked", source="test", entity=s.pc, license_id="x", reason="noop")])
    assert held_license(s.state, s.pc, "lic.training.guile_thievery") is not None
    stretch = check_gate(s.beat(gate="G2", license="lic.lang.common", mode="stretch"), state=s.state, rules=s.rules)
    assert stretch.gate == "G3" and "no stretch" in stretch.reason  # languages declare no stretch


def test_expired_license_is_not_held(tmp_path: Path) -> None:
    s = Scene.new(tmp_path)
    s.apply([Event.of("license_granted", source="test", entity=s.pc,
                      license=LicenseInstance(license_id="lic.training.guile_thievery", expires="scene_end"))])
    assert held_license(s.state, s.pc, "lic.training.guile_thievery") is None


def test_g4_from_condition_overrides_the_proposal(tmp_path: Path) -> None:
    s = Scene.new(tmp_path)
    with s.store.transaction() as tx:
        tx.add_all(apply_condition(tx.state, tx.mint, s.rules, s.pc, "cond.choking").events)
    b = s.beat(gate="G1", verb="verb.talk", traits=["trait.action.speech"], method="shout for help")
    d = check_gate(b, state=s.state, rules=s.rules)
    assert d.gate == "G4" and d.redirect is not None and d.redirect.missing_kind == "condition"
    assert d.redirect.options and d.redirect.options[0].verb != "verb.talk"


def test_g4_fact_must_exist(tmp_path: Path) -> None:
    s = Scene.new(tmp_path)
    d = check_gate(s.beat(gate="G4", g4_test="fact", g4_fact="fact.999", verb="verb.talk"), state=s.state,
                   rules=s.rules)
    assert d.gate == "G1" and "default false" in d.reason  # falls through and rolls
    canon = check_gate(s.beat(gate="G4", g4_test="canon", g4_fact="canon.no_mortal_flight"), state=s.state,
                       rules=s.rules, canon_impossible=["canon.no_mortal_flight"])
    assert canon.gate == "G4"


def test_g3_redirect_logs_and_finds_precedent(tmp_path: Path) -> None:
    s = Scene.new(tmp_path)
    b = s.beat(gate="G1", verb="verb.force", method="pick the lock", deed_tag="deed.guile.thievery")
    for _ in range(2):
        with s.store.transaction() as tx:
            d = check_gate(b, state=tx.state, rules=s.rules, store=s.store, staged=tx.events, mint=tx.mint)
            tx.add_all(d.events)
    assert len(d.precedent) == 1 and d.events[0].payload.ruling["precedent"]["status"] == "reused"  # type: ignore[attr-defined]
    found = find_rulings(s.store, "g3_redirect:lic.training.guile_thievery")
    assert len({r.id for r in found}) == 2  # distinct ids across transactions


def test_g3_with_no_license_in_data_names_the_branch(tmp_path: Path) -> None:
    s = Scene.new(tmp_path)
    b = s.beat(gate="G3", method="xyzzy plugh", intent="qwv", deed_tag="deed.arcane")
    assert would_be_license(b, s.rules) is None
    with s.store.transaction() as tx:
        d = check_gate(b, state=tx.state, rules=s.rules, store=s.store, staged=tx.events, mint=tx.mint)
        tx.add_all(d.events)
    assert d.redirect is not None and d.redirect.missing_kind == "deed_branch" and d.redirect.options
    kinds = [e.payload.ruling["kind"] for e in d.events]  # type: ignore[attr-defined]
    assert kinds == ["g3_redirect", "rule_conflict"]


def test_accepted_fallback_rolls(tmp_path: Path) -> None:
    s = Scene.new(tmp_path)
    b = s.beat(gate="G3", mode="fallback", fallback_license="lic.training.guile_thievery", verb="verb.force")
    d = check_gate(b, state=s.state, rules=s.rules)
    assert (d.gate, d.mode, d.license, d.rolls_possible) == ("G3", "fallback", "lic.training.guile_thievery", True)
    wrong = check_gate(s.beat(gate="G3", mode="fallback", fallback_license="lic.training.guile_thievery",
                              verb="verb.talk"), state=s.state, rules=s.rules)
    assert not wrong.rolls_possible


def test_proposed_g3_on_a_held_license_is_g2(tmp_path: Path) -> None:
    """01.3.1 first match wins: a hunter holding lic.training.wilds_tracking is never redirected to learn it
    (playtest 20261007-155118), neither on the Reader's G3 proposal nor on an accepted fallback."""
    s = Scene.new(tmp_path)
    s.apply([Event.of("license_granted", source="test", entity=s.pc,
                      license=LicenseInstance(license_id="lic.training.wilds_tracking"))])
    for b in (s.beat(gate="G3", verb="verb.observe", method="follow fresh, plain tracks",
                     would_be_license="lic.training.wilds_tracking"),
              s.beat(gate="G3", mode="fallback", fallback_license="lic.training.wilds_tracking", verb="verb.observe")):
        d = check_gate(b, state=s.state, rules=s.rules)
        assert (d.gate, d.mode, d.license, d.redirect) == ("G2", "normal", "lic.training.wilds_tracking", None)
    stretch = check_gate(s.beat(gate="G3", mode="stretch", would_be_license="lic.training.wilds_tracking"),
                         state=s.state, rules=s.rules)
    assert stretch.gate == "G3"  # a stretch the license does not declare is still G3 (01.3.5)


def test_basic_verb_g3_without_a_licence_is_g1(tmp_path: Path) -> None:
    """01.3.1 first match: G1 before G3. The Reader's G3 on Talk / Recall naming no licence it needs is the
    verb's own act (playtests 20261007-170200 Stonesense, -170204 arcane mind); a named licence keeps the G3."""
    s = Scene.new(tmp_path)
    for verb, method in (("verb.talk", "speaks to Evred again in a gentle, pressing tone, asking what is wrong"),
                         ("verb.recall", "calls to mind what he knows of the land around Hawkham")):
        d = check_gate(s.beat(gate="G3", verb=verb, method=method), state=s.state, rules=s.rules)
        assert (d.gate, d.redirect) == ("G1", None), d.reason
    named = check_gate(s.beat(gate="G3", verb="verb.handle", method="open the lock with arcane force",
                              would_be_license="lic.training.arcane_alteration"), state=s.state, rules=s.rules)
    assert named.gate == "G3" and named.redirect is not None
    assert named.redirect.missing == "lic.training.arcane_alteration"
    excluded = check_gate(s.beat(gate="G3", verb="verb.force", method="pick the lock"), state=s.state, rules=s.rules)
    assert excluded.gate == "G3" and "excludes" in excluded.reason
