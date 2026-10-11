"""Spec 033 P2b (cases C1.b, C1.c, C5 reversal, R7, R10): with `Beat.stated` set (the dm-tools DM stated the beat)
the gate, necessity, frame and anchors read its fields and ids, never the beat's words. The pipeline (stated None)
keeps its word readers, so each test also runs the same words without `stated`."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from engine.data.loader import load_rules
from engine.resolve.frame import lift_attribute, lift_or_carry, reverses
from engine.resolve.gate import active_effects, check_gate, compute_gate
from engine.resolve.necessity import necessity, plain_reading
from engine.resolve.types import Beat, Change, CostDecl, Stated
from engine.retrieve.anchors import anchor_candidates
from engine.retrieve.scene import focus_of
from tests.engine.test_reading import READER, UNLETTERED, WORDS, _game
from tests.engine.test_resolve_scene import Scene


def _approaches(rules: Any) -> list[tuple[str, dict[str, Any]]]:
    seen: dict[str, dict[str, Any]] = {}
    for v in rules.basic_verbs.values():
        for e in v.get("excludes") or ():
            seen.setdefault(str(e["what"]), e)
    return list(seen.items())


def test_each_approach_is_g3_naming_needs_and_its_licences_or_g2_when_held(tmp_path: Path) -> None:
    """C1.b: an `approach` is one `excludes` entry exactly; no licence held: G3 naming `needs` and every
    `covered_by` licence; one held: G2 under it. The beat's own words name nothing."""
    s = Scene.new(tmp_path)
    for what, e in _approaches(s.rules):
        d = check_gate(s.beat(verb="verb.handle", method="gently", stated=Stated(approach=what)), state=s.state,
                       rules=s.rules)
        assert d.gate == "G3", what
        assert str(e["needs"]) in d.reason, what
        assert all(lic in d.reason for lic in e.get("covered_by") or ()), what
        for lic in e.get("covered_by") or ():
            held = Scene.new(tmp_path / what.replace(" ", "_") / lic, pc_licenses=["lic.lang.common", lic])
            g = check_gate(held.beat(verb="verb.handle", method="gently", stated=Stated(approach=what)),
                           state=held.state, rules=held.rules)
            assert (g.gate, g.license) == ("G2", lic), (what, lic)


def test_plain_passes_whatever_the_words_say_and_an_unstated_beat_still_guesses(tmp_path: Path) -> None:
    s = Scene.new(tmp_path)
    words = {"method": "pick the lock on the cellar door", "intent": "get in"}
    plain = check_gate(s.beat(verb="verb.handle", stated=Stated(), **words), state=s.state, rules=s.rules)
    assert (plain.gate, plain.redirect) == ("G1", None)  # the DM said plain: the lock words decide nothing
    guessed = check_gate(s.beat(verb="verb.handle", **words), state=s.state, rules=s.rules)
    assert guessed.gate == "G3"  # the pipeline's word match is unchanged


def test_an_approach_from_another_verbs_list_is_accepted(tmp_path: Path) -> None:
    s = Scene.new(tmp_path, pc_licenses=["lic.lang.common", "lic.training.guile_thievery"])
    d = check_gate(s.beat(verb="verb.handle", stated=Stated(approach="picking a lock")), state=s.state, rules=s.rules)
    assert (d.gate, d.license) == ("G2", "lic.training.guile_thievery")  # Force's entry, on a Handle beat


def test_an_active_effect_covers_flight_and_none_covers_a_tongue_not_held(tmp_path: Path) -> None:
    s = Scene.new(tmp_path)
    rules = s.rules
    fly = "flying or teleporting"
    no = compute_gate("verb.move", rules=rules, approach=fly, effects=())
    assert no.gate == "G3" and "a license (movement_mode or spell)" in no.reason
    yes = compute_gate("verb.move", rules=rules, approach=fly, effects=("eff.movement_mode",))
    assert (yes.gate, yes.license) == ("G2", None) and "eff.movement_mode" in yes.reason
    # a tongue not held: no licence is listed, so G3 whatever is held, naming the need and its fallback
    talk = compute_gate("verb.talk", speech=True, rules=rules, approach="speaking a language not held",
                        held=["lic.lang.common"])
    assert talk.gate == "G3" and "fallback: gesture" in talk.reason and talk.license is None
    assert active_effects(s.state, rules, s.pc) == set()


@pytest.mark.parametrize("verb", ["verb.observe", "verb.handle", "verb.talk"])
def test_reads_needs_letters_once_literacy_is_on_record_whatever_the_words(tmp_path: Path, verb: str) -> None:
    """C1.c: `reads` true on observe, handle or talk is reading writing (02.4.6); `reads` false is the normal verb
    path even for words about a notice."""
    s = Scene.new(tmp_path)  # the common tongue, not letters
    d = check_gate(s.beat(verb=verb, method="look it over", stated=Stated(reads=True)), state=s.state, rules=s.rules)
    assert d.gate == "G3" and d.redirect is not None and d.redirect.missing == "lic.lang.letters"
    lettered = Scene.new(tmp_path / "l", pc_licenses=["lic.lang.common", "lic.lang.letters"])
    g = check_gate(lettered.beat(verb=verb, method="look it over", stated=Stated(reads=True)),
                   state=lettered.state, rules=lettered.rules)
    assert (g.gate, g.license) == ("G2", "lic.lang.letters")
    words = {"method": "read the notice on the board", "intent": "read the notice"}
    off = check_gate(s.beat(verb=verb, stated=Stated(reads=False), **words), state=s.state, rules=s.rules)
    assert off.gate != "G3"  # no word test promotes it
    bare = Scene.new(tmp_path / "b", pc_licenses=[])  # no tongues on record: literacy is not known to be lacking
    assert check_gate(bare.beat(verb=verb, stated=Stated(reads=True)), state=bare.state, rules=bare.rules).gate != "G3"


def test_plain_reading_follows_the_field_and_the_tongue(tmp_path: Path) -> None:
    def beat(**kw: Any) -> Beat:
        return Beat(id="beat.1", actor="pc.wren", intent="know", method="look", target="obj.bill_on_the_gatepost",
                    verb="verb.observe", **kw)

    readable, unlettered = _game(tmp_path, READER, text=WORDS), _game(tmp_path / "u", UNLETTERED, text=WORDS)
    assert plain_reading(beat(stated=Stated(reads=True)), "verb.observe", readable.state)
    assert not plain_reading(beat(stated=Stated(reads=False)), "verb.observe", readable.state)  # words ignored
    assert not plain_reading(beat(stated=Stated(reads=True)), "verb.observe", unlettered.state)  # cannot_read
    unstated = Beat(id="beat.1", actor="pc.wren", intent="know what the bill says", method="read the bill",
                    target="obj.bill_on_the_gatepost", verb="verb.observe")
    assert plain_reading(unstated, "verb.observe", readable.state)  # the pipeline's word reading is unchanged
    dec = type("D", (), {"mode": "normal", "verb": "verb.observe"})()
    assert necessity(beat(stated=Stated(reads=True)), dec, state=readable.state, rules=load_rules()) == "trivial"


def test_a_stated_beat_lifts_by_a_take_only_and_keeps_the_dms_attribute(tmp_path: Path) -> None:
    s = Scene.new(tmp_path)
    st, rules = s.state, s.rules
    actor = st.entities[s.pc]  # Agility 3, Might 1, Endurance 1
    words: dict[str, Any] = {"intent": "get it", "method": "heave the chest onto the cart", "verb": "verb.exert"}
    assert lift_or_carry(rules, Beat(id="b", actor=s.pc, **words)) is not None  # the pipeline reads "heave"
    stated = Beat(id="b", actor=s.pc, stated=Stated(), **words)
    assert lift_or_carry(rules, stated) is None  # the DM's verb stands: no lift from the words
    take = Beat(id="b", actor=s.pc, stated=Stated(), change=Change(kind="take", what="item.x"), **words)
    spec = lift_or_carry(rules, take)
    assert spec is not None
    # the rubric's "heave -> might" is not read; the best odds (agility) win, the DM's own on a tie
    assert lift_attribute(spec, rules, st, take, actor, "might", 0) == "agility"
    pipeline = take.model_copy(update={"stated": None})
    assert lift_attribute(spec, rules, st, pipeline, actor, "agility", 0) == "might"


def test_a_stated_beat_reverses_by_cost_id_never_by_the_price_words(tmp_path: Path) -> None:
    """C5 reversal: `resolution.yaml#reverses_goal` lists the cost ids; the form's words decide nothing."""
    s = Scene.new(tmp_path)
    tam = s.npc("Tam Harlan")
    st, rules = s.state, s.rules

    def beat(kind: str, **kw: Any) -> Beat:
        return Beat(id="b", actor=s.pc, intent="x", method="y", target=tam, verb="verb.talk",
                    change=Change(kind=kind, what=tam), **kw)  # type: ignore[arg-type]

    door, twist = CostDecl(menu_id="cost.closed_door"), CostDecl(menu_id="cost.footing", form_intent="she twists free")
    for kind in ("persuade_to", "learn"):
        assert reverses(door, beat(kind, stated=Stated()), st, rules)
        assert not reverses(CostDecl(menu_id="cost.time"), beat(kind, stated=Stated()), st, rules)
    assert not reverses(door, beat("take", stated=Stated()), st, rules)  # no listing for the kind
    assert not reverses(twist, beat("restrain", stated=Stated()), st, rules)  # "twists free" is not read
    assert reverses(twist, beat("restrain"), st, rules)  # the pipeline still reads it
    assert not reverses(door, Beat(id="b", actor=s.pc, intent="x", method="y", verb="verb.talk",
                                   change=Change(kind="learn", what=tam), stated=Stated()), st, rules)  # no target


def test_anchor_candidates_key_a_stated_beat_by_its_verb_id_not_its_text(tmp_path: Path) -> None:
    s = Scene.new(tmp_path)
    plain = {"verb": "verb.talk", "intent": "persuade him", "method": "talk", "intent_verbs": ["talk"]}
    assert "anc.15_4_1" in anchor_candidates(plain, s.state, s.rules)  # "persuade" in the text keys it
    stated = anchor_candidates({**plain, "stated": Stated().model_dump()}, s.state, s.rules)
    assert "anc.15_4_1" not in stated and stated[0] == "anc.01_18_7"  # the verb's own anchor still leads


def test_focus_of_names_only_ids() -> None:
    b = Beat(id="b", actor="pc.w", intent="ask Tam Harlan about the ledger", method="ask", target="npc.tam",
             change=Change(kind="learn", what="obj.ledger", whom="npc.tam"))
    assert focus_of(b) == ["npc.tam", "obj.ledger"]
    assert focus_of(Beat(id="b", actor="pc.w", intent="look", method="look", target="none")) == []
