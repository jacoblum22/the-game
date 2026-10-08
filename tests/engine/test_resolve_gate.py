"""engine/resolve/gate.py: the computed gate (00.12.3 `[D]`), G4 from state, the PR-01-5 redirect, rulings (FR-022)."""

from __future__ import annotations

from pathlib import Path

from engine.resolve.gate import check_gate, excluded_by, held_license, would_be_license
from engine.resolve.rulings import find_rulings
from engine.store.conditions import apply_condition
from engine.store.events import Event, LicenseInstance
from tests.engine.test_resolve_scene import Scene


def test_a_basic_verb_is_g1_and_a_knack_never_gates(tmp_path: Path) -> None:
    """P-122, P-031: a threat or a gentle question is Talk's own act; nothing the Reader says moves it to G3."""
    s = Scene.new(tmp_path)
    for verb, method in (("verb.talk", "slam a fist and demand the price"),
                         ("verb.talk", "speak to Evred in a gentle, pressing tone"),
                         ("verb.recall", "call to mind what he knows of the land around Hawkham"),
                         ("verb.force", "shove the cart into the doorway")):
        d = check_gate(s.beat(verb=verb, method=method), state=s.state, rules=s.rules)
        assert (d.gate, d.verb, d.redirect) == ("G1", verb, None), d.reason


def test_the_facets_choose_the_card(tmp_path: Path) -> None:
    """P-023 / P-064: "gently turn the child's face" is not a Grapple; a raised fist with words is Talk."""
    s = Scene.new(tmp_path)
    gentle = check_gate(s.beat(verb="verb.grapple", method="gently turn the child's face"), state=s.state,
                        rules=s.rules)
    assert gentle.verb == "verb.handle"
    asked = check_gate(s.beat(verb="verb.grapple", speech=True, method="ask for the ledger"), state=s.state,
                       rules=s.rules)
    assert asked.verb == "verb.talk"
    grab = check_gate(s.beat(verb="verb.grapple", against_will=True, method="grab the ledger"), state=s.state,
                      rules=s.rules)
    assert grab.verb == "verb.grapple"


def test_excludes_match_a_literal_mention(tmp_path: Path) -> None:
    s = Scene.new(tmp_path)
    force = s.rules.verb("verb.force")
    ex = excluded_by(force, "I pick the lock")
    assert ex is not None and ex["what"] == "picking a lock"
    assert excluded_by(force, "I break the lock") is None


def test_an_excluded_method_needs_its_license(tmp_path: Path) -> None:
    s = Scene.new(tmp_path)
    d = check_gate(s.beat(verb="verb.handle", method="pick the lock on the cellar door"), state=s.state,
                   rules=s.rules)  # Handle read it, Force's excludes name it
    assert d.gate == "G3" and d.redirect is not None and d.redirect.missing == "lic.training.guile_thievery"
    held = Scene.new(tmp_path / "held", pc_licenses=["lic.lang.common", "lic.training.guile_thievery"])
    d2 = check_gate(held.beat(verb="verb.handle", method="pick the lock"), state=held.state, rules=held.rules)
    assert (d2.gate, d2.license) == ("G2", "lic.training.guile_thievery")


def test_a_power_needs_a_held_technique(tmp_path: Path) -> None:
    s = Scene.new(tmp_path)
    d = check_gate(s.beat(verb="verb.observe", uses_power=True, method="use my witch-sight to see the spirits"),
                   state=s.state, rules=s.rules)
    assert d.gate == "G3" and d.redirect is not None
    mind = Scene.new(tmp_path / "mind", pc_licenses=["lic.lang.common", "lic.training.arcane_mind"])
    d2 = check_gate(mind.beat(verb="verb.observe", uses_power=True, method="read his surface thoughts"),
                    state=mind.state, rules=mind.rules)
    assert (d2.gate, d2.license) == ("G2", "lic.training.arcane_mind")


def test_a_held_trained_form_is_g2(tmp_path: Path) -> None:
    """A hunter holding Tracking is never redirected to learn it (playtest 20261007-155118); a persuader's talk
    is licensed."""
    s = Scene.new(tmp_path, pc_licenses=["lic.lang.common", "lic.training.wilds_tracking",
                                         "lic.training.influence_persuasion"])
    obs = check_gate(s.beat(verb="verb.observe", method="follow fresh, plain tracks"), state=s.state, rules=s.rules)
    assert (obs.gate, obs.license, obs.redirect) == ("G2", "lic.training.wilds_tracking", None)
    talk = check_gate(s.beat(verb="verb.talk", speech=True, method="talk him round"), state=s.state, rules=s.rules)
    assert (talk.gate, talk.license) == ("G2", "lic.training.influence_persuasion")


def test_reading_needs_letters_once_literacy_is_on_record(tmp_path: Path) -> None:
    s = Scene.new(tmp_path)  # holds the common tongue, not letters
    d = check_gate(s.beat(verb="verb.observe", method="read the notice"), state=s.state, rules=s.rules)
    assert d.gate == "G3" and d.redirect is not None and d.redirect.missing == "lic.lang.letters"
    assert d.redirect.options[0].kind == "fallback"  # pick out numerals and seals (letters' crude fallback)
    lettered = Scene.new(tmp_path / "l", pc_licenses=["lic.lang.common", "lic.lang.letters"])
    d2 = check_gate(lettered.beat(verb="verb.observe", method="read the notice"), state=lettered.state,
                    rules=lettered.rules)
    assert (d2.gate, d2.license) == ("G2", "lic.lang.letters")
    bare = Scene.new(tmp_path / "b", pc_licenses=[])  # no tongues recorded: literacy is not known to be lacking
    assert check_gate(bare.beat(verb="verb.observe", method="read the notice"), state=bare.state,
                      rules=bare.rules).gate == "G1"


def test_expired_license_is_not_held(tmp_path: Path) -> None:
    s = Scene.new(tmp_path)
    s.apply([Event.of("license_granted", source="test", entity=s.pc,
                      license=LicenseInstance(license_id="lic.training.guile_thievery", expires="scene_end"))])
    assert held_license(s.state, s.pc, "lic.training.guile_thievery") is None


def test_g4_from_condition(tmp_path: Path) -> None:
    s = Scene.new(tmp_path)
    with s.store.transaction() as tx:
        tx.add_all(apply_condition(tx.state, tx.mint, s.rules, s.pc, "cond.choking").events)
    b = s.beat(verb="verb.talk", traits=["trait.action.speech"], method="shout for help")
    d = check_gate(b, state=s.state, rules=s.rules)
    assert d.gate == "G4" and d.redirect is not None and d.redirect.missing_kind == "condition"
    assert d.redirect.options and d.redirect.options[0].verb != "verb.talk"


def test_g4_fact_must_exist(tmp_path: Path) -> None:
    s = Scene.new(tmp_path)
    assert check_gate(s.beat(g4_fact="fact.999", verb="verb.talk"), state=s.state, rules=s.rules).gate == "G1"
    fid = s.fact("world", "bridge.state", "collapsed")
    d = check_gate(s.beat(g4_fact=fid, verb="verb.move"), state=s.state, rules=s.rules)
    assert d.gate == "G4" and d.fact_cited == fid


def test_g3_redirect_logs_and_finds_precedent(tmp_path: Path) -> None:
    s = Scene.new(tmp_path)
    b = s.beat(verb="verb.force", method="pick the lock", deed_tag="deed.guile.thievery")
    for _ in range(2):
        with s.store.transaction() as tx:
            d = check_gate(b, state=tx.state, rules=s.rules, store=s.store, staged=tx.events, mint=tx.mint)
            tx.add_all(d.events)
    assert len(d.precedent) == 1 and d.events[0].payload.ruling["precedent"]["status"] == "reused"  # type: ignore[attr-defined]
    found = find_rulings(s.store, "g3_redirect:lic.training.guile_thievery")
    assert len({r.id for r in found}) == 2  # distinct ids across transactions


def test_g3_with_no_license_in_data_names_the_branch(tmp_path: Path) -> None:
    s = Scene.new(tmp_path)
    b = s.beat(verb="verb.observe", uses_power=True, method="xyzzy plugh", intent="qwv", deed_tag="deed.arcane")
    assert would_be_license(b.method, s.rules) is None
    with s.store.transaction() as tx:
        d = check_gate(b, state=tx.state, rules=s.rules, store=s.store, staged=tx.events, mint=tx.mint)
        tx.add_all(d.events)
    assert d.redirect is not None and d.redirect.missing_kind == "deed_branch" and d.redirect.options
    kinds = [e.payload.ruling["kind"] for e in d.events]  # type: ignore[attr-defined]
    assert kinds == ["g3_redirect", "rule_conflict"]


def test_accepted_fallback_rolls(tmp_path: Path) -> None:
    s = Scene.new(tmp_path)
    b = s.beat(mode="fallback", fallback_license="lic.training.guile_thievery", verb="verb.force")
    d = check_gate(b, state=s.state, rules=s.rules)
    assert (d.gate, d.mode, d.license, d.rolls_possible) == ("G3", "fallback", "lic.training.guile_thievery", True)


def test_stretch_needs_a_declared_stretch(tmp_path: Path) -> None:
    s = Scene.new(tmp_path)
    d = check_gate(s.beat(license="lic.lang.common", mode="stretch", verb="verb.talk"), state=s.state, rules=s.rules)
    assert d.mode == "normal"  # languages declare no stretch: computed as the plain act
