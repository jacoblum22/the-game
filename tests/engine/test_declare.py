"""Spec 006: declared sentences judged by code (12.3.1, 12.3.1a, 12.14.13): parsing, tiers, the deterministic
scans, coverage, and a whole turn in each output shape."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from engine.audit.declare import (
    DeclaredSentence,
    NewElement,
    SceneIndex,
    coverage,
    parse_output,
    scan_sentence,
    t2_delivered,
    tier_of,
)
from engine.data.loader import load_rules
from engine.dm.turn import play_turn
from engine.llm.base import Role
from engine.llm.offline import OfflineModel
from tests.engine.test_turn_adjudication import setup
from tests.engine.test_turn_narration import _decl, _must, calls, chk, claim, look_model

RULES = load_rules()
IDX = SceneIndex(pc="pc.wren", aliases={"pc.wren": ["wren"], "npc.tam": ["tam harlan", "tam", "ferryman"],
                                        "npc.sela": ["sela vey", "sela"], "loc.dock": ["the night dock", "dock"]},
                 pronouns={"npc.tam": "m", "npc.sela": "f"}, numbers={"pc.wren": [3]},
                 facts={"fact.1": "npc.tam fare two silver"}, fact_subject={"fact.1": "npc.tam"},
                 handles={"R1": "you look over the quay", "R2": "a leather satchel lies by the post"},
                 handle_entities={"R1": ["pc.wren"]}, sealed=["the smuggler's cache"])


def s(text: str, **kw: Any) -> DeclaredSentence:
    return DeclaredSentence(text=text, **kw)


def fails(sent: DeclaredSentence) -> list[str]:
    return [f.why for f in scan_sentence(sent, IDX, rules=RULES).failures]


def test_both_output_shapes_parse_to_the_same_sentences() -> None:
    a = parse_output({"sentences": [_decl("Fog lies low.", atmosphere=True), _decl("Tam waits.", ["R1"])]})
    b = parse_output({"fiction": "Fog lies low. Tam waits.",
                      "declarations": [{"sentence": "0", "atmosphere": True}, {"sentence": "1", "refs": ["R1"]}]})
    assert [(x.text, x.refs, x.atmosphere) for x in a] == [(x.text, x.refs, x.atmosphere) for x in b]


def test_element_kind_fixes_the_tier() -> None:
    k = lambda kind, ordinary=True: tier_of(NewElement(element_kind=kind, name="x", ordinary=ordinary), RULES)  # noqa: E731
    assert [k("furniture"), k("feature"), k("person"), k("item"), k("document")] == ["T1a"] * 5
    assert k("knowledge") == "T1b"
    assert [k("clue"), k("hazard"), k("adversary")] == ["T2"] * 3
    assert k("person", ordinary=False) == "T2" and k("item", ordinary=False) == "T2"  # 12.14.13's question
    assert k("relic") == "T2"  # an uncertain kind is T2


def test_a_t2_element_passes_only_when_a_cited_line_delivers_it() -> None:
    satchel = NewElement(element_kind="item", name="a leather satchel", ordinary=False)
    assert t2_delivered(satchel, s("A satchel lies there.", refs=["R2"]), IDX)
    assert not t2_delivered(satchel, s("A satchel lies there."), IDX)


def test_a_name_used_but_not_declared_is_added_to_about_and_an_invented_one_fails() -> None:
    scan = scan_sentence(s("Tam Harlan nods to Sela."), IDX, rules=RULES)
    assert scan.added_about == ["npc.tam", "npc.sela"] and not scan.failures
    assert any("Brannoc" in w for w in fails(s("Tam says Brannoc took the boat.", about=["npc.tam"])))
    assert not fails(s("A boatman named Brannoc waits.", new=[NewElement(element_kind="person", name="Brannoc")]))
    assert not fails(s("\"Tide's turning,\" Tam says. \"Go now.\""))  # quoted sentence starts are not names


def test_numerals_against_quantities_and_cited_values() -> None:
    assert fails(s("You count 12 arrows."))  # a digit is never prose (12.14.4)
    assert fails(s("Tam wants five silver for the crossing.", about=["npc.tam"]))
    assert not fails(s("Tam wants two silver for the crossing.", refs=["fact.1"]))  # the cited fact holds it
    assert not fails(s("You have three arrows left.", about=["pc.wren"]))  # the PC's quantity
    assert not fails(s("Two gulls fight over a fish head."))  # a count of nothing the store keeps


def test_pronouns_against_the_one_person_the_sentence_is_about() -> None:
    assert fails(s("She leans on the pole.", about=["npc.tam"]))
    assert not fails(s("He leans on the pole.", about=["npc.tam"]))
    assert not fails(s("She watches him.", about=["npc.tam", "npc.sela"]))  # two people: not judged


def test_mechanics_and_sealed_content_fail() -> None:
    assert any("mechanics" in w for w in fails(s("Your Agility check succeeds.")))
    [f] = scan_sentence(s("You glimpse the smuggler's cache."), IDX, rules=RULES).failures
    assert f.fix == "cut"


def test_an_atmosphere_sentence_naming_someone_is_declared_by_its_names() -> None:
    scan = scan_sentence(s("Sela's lantern swings in the fog.", atmosphere=True), IDX, rules=RULES)
    assert scan.added_about == ["npc.sela"]  # 12.3.1a item 2: it names someone, so it is not atmosphere


def test_coverage_lists_the_must_name_lines_no_sentence_cites() -> None:
    sents = [s("You look.", refs=["R1"]), s("The fog is thick.", atmosphere=True)]
    assert coverage(sents, ["R1", "R3"]) == ["R3"]


def test_a_declared_turn_passes_on_the_first_draft(tmp_path: Path) -> None:
    """The whole loop: every sentence declared, every MUST line cited, nothing for the audit: one narrator call."""
    def draft(schema: Any, packet: Any) -> dict[str, Any]:
        return {"sentences": [_decl("You look over the quay.", _must(packet)),
                              _decl("Fog lies low on the black water.", atmosphere=True),
                              _decl("A coil of rope hangs by the bollard.",
                                    new=[{"element_kind": "furniture", "name": "coil of rope", "ordinary": True,
                                          "implied": [{"predicate": "location", "value": "by the bollard"}]}]),
                              _decl("What do you do?")]}
    model = look_model(narrator=[draft], checker=[chk()])
    dock, ctx = setup(tmp_path, model)
    out = play_turn(ctx, "I look over the quay.")
    assert not out.response.flags.fallback_used and not out.response.flags.review_flag
    assert len(calls(model, Role.NARRATOR)) == 1
    assert [v["kind"] for v in out.turn_record.draft_versions] == ["draft"]
    rope = next(e for e in dock.state.entities.values() if e.name == "coil of rope")
    assert dock.state.fact_value(rope.id, "location") == "by the bollard"  # T1a: written as narrated


def test_the_audit_takes_the_declared_subject_not_its_guess(tmp_path: Path) -> None:
    """12.3.1: subject given, never guessed. The Checker read "he" as the watch; the sentence is about Tam."""
    def draft(schema: Any, packet: Any) -> dict[str, Any]:
        return {"sentences": [_decl("He mends a net by the post.", _must(packet), about=["npc.tam_harlan"]),
                              _decl("What do you do?")]}
    model = look_model(narrator=[draft])
    dock, ctx = setup(tmp_path, model)
    model.push(Role.CHECKER, chk(claim(0, dock.watch, "identity", "gender", "man")))
    out = play_turn(ctx, "I look over the quay.")
    v = out.turn_record.draft_versions[0]["claims"][0]
    assert v["subject"] == dock.ferryman and out.response.fiction.startswith("He mends a net")


def test_the_fiction_fallback_shape_plays_a_turn(tmp_path: Path) -> None:
    dock, ctx = setup(tmp_path, OfflineModel(), narrator_schema="fiction")
    out = play_turn(ctx, "I look over the quay.")
    assert out.response.fiction and not out.response.flags.fallback_used
    req = dock.store.model_calls(out.turn_record.turn_id)
    narr = [c for c in req if c["role"] == "narrator"]
    assert narr and "declarations" in str(narr[0]["response"])
