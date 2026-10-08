"""The computed gate as a table (00.12.3; lane D P1 test 3): every basic verb × the eight facet combinations ×
three holdings (none, the verb's trained form, a technique license). Pure: no state."""

from __future__ import annotations

import itertools

import pytest

from engine.data.loader import load_rules
from engine.resolve.gate import compute_gate, covering_verb

RULES = load_rules()
VERBS = list(RULES.basic_verbs)
FACETS = list(itertools.product((False, True), repeat=3))  # against_will, uses_power, speech


def trained_form(verb: str | None) -> str | None:
    """A training license whose crude fallback is this verb (its trained form), lowest price first."""
    fits = [lid for lid, e in RULES.licenses.items() if e.get("kind") == "training"
            and isinstance(e.get("crude_fallback"), dict) and e["crude_fallback"].get("verb") == verb]
    return min(fits, key=lambda x: int(RULES.license(x)["crude_fallback"].get("dc_shift") or 0)) if fits else None


TECHNIQUE = "lic.training.arcane_mind"  # no crude fallback: a power


@pytest.mark.parametrize("verb", VERBS)
@pytest.mark.parametrize("facets", FACETS, ids=lambda f: "aw{:d}up{:d}sp{:d}".format(*f))
@pytest.mark.parametrize("holding", ["none", "trained", "technique"])
def test_gate_table(verb: str, facets: tuple[bool, bool, bool], holding: str) -> None:
    aw, up, sp = facets
    cv = covering_verb(verb, against_will=aw, speech=sp)
    form = trained_form(cv)
    held = {"none": [], "trained": [form] if form else [], "technique": [TECHNIQUE]}[holding]
    c = compute_gate(verb, against_will=aw, uses_power=up, speech=sp, method="do the thing", held=held, rules=RULES)
    assert c.verb == cv
    if not up:  # a basic act: G1, or G2 when its trained form is held; never a redirect
        assert c.gate == ("G2" if holding == "trained" and form else "G1"), c.reason
        assert c.license == (form if c.gate == "G2" else None)
    elif holding == "technique":  # a power with a held technique license
        assert (c.gate, c.license) == ("G2", TECHNIQUE)
    else:  # a power with no technique held: redirected, never narrated as possible (VII)
        assert c.gate == "G3", c.reason


def test_covering_verb_rows() -> None:
    assert covering_verb("verb.grapple", against_will=False, speech=False) == "verb.handle"
    assert covering_verb("verb.grapple", against_will=False, speech=True) == "verb.talk"
    assert covering_verb("verb.grapple", against_will=True, speech=True) == "verb.grapple"
    assert covering_verb("verb.strike", against_will=False, speech=True) == "verb.talk"
    assert covering_verb("verb.strike", against_will=False, speech=False) == "verb.strike"  # shooting a target
    assert covering_verb("verb.force", against_will=False, speech=False) == "verb.force"  # breaking a crate


@pytest.mark.parametrize("method,need", [("pick the lock", "lic.training.guile_thievery"),
                                         ("read the notice", "lic.lang.letters")])
def test_needs_name_the_license(method: str, need: str) -> None:
    c = compute_gate("verb.observe" if "read" in method else "verb.handle", method=method, rules=RULES,
                     reading="read" in method, literacy_known=True)
    assert (c.gate, c.license) == ("G3", need)
    held = compute_gate("verb.observe" if "read" in method else "verb.handle", method=method, rules=RULES,
                        reading="read" in method, literacy_known=True, held=[need])
    assert (held.gate, held.license) == ("G2", need)
