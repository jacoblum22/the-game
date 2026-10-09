"""Spec 006 / 019: the passage judged by code (12.3.1, 12.3.1a, 12.14.13): parsing, code's sentence split with the
side list's speakers, tiers, the deterministic scans, coverage, the quote-mark check, and a whole turn."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from engine.audit.declare import (
    NewElement,
    Passage,
    SceneIndex,
    Sentence,
    coverage,
    first_person,
    parse_output,
    quote,
    scan_sentence,
    sentences_of,
    t2_delivered,
    tier_of,
    unquoted,
)
from engine.data.loader import load_rules
from engine.dm.turn import play_turn
from engine.llm.base import Role
from tests.engine.test_turn_adjudication import setup
from tests.engine.test_turn_narration import _must, calls, chk, claim, look_model, passage

RULES = load_rules()
IDX = SceneIndex(pc="pc.wren", aliases={"pc.wren": ["wren"], "npc.tam": ["tam harlan", "tam", "ferryman"],
                                        "npc.sela": ["sela vey", "sela"], "loc.dock": ["the night dock", "dock"]},
                 pronouns={"npc.tam": "m", "npc.sela": "f"}, numbers={"pc.wren": [3]},
                 facts={"fact.1": "npc.tam fare two silver"}, fact_subject={"fact.1": "npc.tam"},
                 handles={"R1": "you look over the quay", "R2": "a leather satchel lies by the post",
                          "R3": "Tam asks two silver for the fare"},
                 handle_entities={"R1": ["pc.wren"]}, sealed=["the smuggler's cache"])


def s(text: str, **kw: Any) -> Sentence:
    return Sentence(text=text, **kw)


def fails(sent: Sentence) -> list[str]:
    return [f.why for f in scan_sentence(sent, IDX, rules=RULES).failures]


def test_the_passage_is_split_by_code_with_speakers_from_the_side_list() -> None:
    """12.3.1: one passage; code splits it (quoted speech kept whole) and gives each sentence the speaker of the
    speech whose words it holds; a reported speech is found by its words; each new element sits on the sentence
    that names it."""
    p = parse_output({"passage": 'Tam looks up. "Two silver, and not a copper less." She tells you the ferry left at '
                                 'dawn. A coil of rope lies by the post.',
                      "speech": [{"speaker": "npc.tam", "words": "Two silver, and not a copper less.", "form": "direct"},
                                 {"speaker": "npc.sela", "words": "the ferry left at dawn", "form": "reported"},
                                 {"speaker": "none", "words": "  "}],
                      "new": [{"element_kind": "furniture", "name": "coil of rope"}], "covers": ["R1", "R1", "R3"]})
    assert p.covers == ["R1", "R3"] and len(p.speech) == 2
    sents, unplaced = sentences_of(p)
    assert [x.speaker for x in sents] == [None, "npc.tam", "npc.sela", None]
    assert [len(x.new) for x in sents] == [0, 0, 0, 1] and not unplaced
    assert all(x.refs == ["R1", "R3"] for x in sents)


def test_element_kind_fixes_the_tier() -> None:
    k = lambda kind, ordinary=True: tier_of(NewElement(element_kind=kind, name="x", ordinary=ordinary), RULES)  # noqa: E731
    assert [k("furniture"), k("feature"), k("person"), k("item"), k("document")] == ["T1a"] * 5
    assert k("knowledge") == "T1b"
    assert [k("clue"), k("hazard"), k("adversary")] == ["T2"] * 3
    assert k("person", ordinary=False) == "T2" and k("item", ordinary=False) == "T2"  # 12.14.13's question
    assert k("relic") == "T1a"  # an uncertain kind is T1a (R2-G, DL-12-80)


def test_a_t2_element_passes_only_when_a_covered_line_delivers_it() -> None:
    satchel = NewElement(element_kind="item", name="a leather satchel", ordinary=False)
    assert t2_delivered(satchel, s("A satchel lies there.", refs=["R2"]), IDX)
    assert not t2_delivered(satchel, s("A satchel lies there."), IDX)


def test_a_name_used_is_added_to_about_and_an_invented_one_fails() -> None:
    scan = scan_sentence(s("Tam Harlan nods to Sela."), IDX, rules=RULES)
    assert scan.added_about == ["npc.tam", "npc.sela"] and not scan.failures
    assert any("Brannoc" in w for w in fails(s("Tam says Brannoc took the boat.")))
    assert not fails(s("A boatman named Brannoc waits.", new=[NewElement(element_kind="person", name="Brannoc")]))
    assert not fails(s("\"Tide's turning,\" Tam says. \"Go now.\""))  # quoted sentence starts are not names


def test_numerals_against_quantities_and_covered_lines() -> None:
    assert fails(s("You count 12 arrows."))  # a digit is never prose (12.14.4)
    assert fails(s("Tam wants five silver for the crossing.", about=["npc.tam"]))
    assert not fails(s("Tam wants two silver for the crossing.", refs=["R3"]))  # the covered line holds it
    assert not fails(s("You have three arrows left.", about=["pc.wren"]))  # the PC's quantity
    assert not fails(s("Two gulls fight over a fish head."))  # a count of nothing the store keeps


def test_pronouns_are_no_longer_a_scan() -> None:
    """Spec 016: the pronoun of a certain subject is a precision check (claims.precision_checks, 12.3.2; tested in
    test_precision_checks.py), run with the sentence before; the scan neither fails nor logs it."""
    scan = scan_sentence(s("She leans on the pole.", about=["npc.tam"]), IDX, rules=RULES)
    assert not scan.failures and not scan.logged


def test_mechanics_and_sealed_content_fail() -> None:
    assert any("mechanics" in w for w in fails(s("Your Agility check succeeds.")))
    [f] = scan_sentence(s("You glimpse the smuggler's cache."), IDX, rules=RULES).failures
    assert f.fix == "cut"


def test_coverage_is_the_side_lists() -> None:
    assert coverage(Passage(text="You look.", covers=["R1"]), ["R1", "R3"]) == ["R3"]


def test_the_quote_mark_check_finds_speech_left_outside_quotes() -> None:
    """12.3.1a item 2: a direct speech whose words stand outside quote marks, and a first-person sentence in the
    narrator's voice (round 6: 232941 turn.16), are found; quoted speech and the second person pass."""
    p = Passage(text='Sevella shrugs. Nobody has stood at this gate asking after the child that I\'ve marked. '
                     '"Go on," she says. You walk on, and the road bends.',
                speech=[{"speaker": "npc.s", "words": "Go on,", "form": "direct"}])  # type: ignore[list-item]
    assert unquoted(p) == ["Nobody has stood at this gate asking after the child that I've marked."]
    q = Passage(text="Sevella shrugs. The gap is yours to use, so go. You nod.",
                speech=[{"speaker": "npc.s", "words": "The gap is yours to use, so go.", "form": "direct"}])  # type: ignore[list-item]
    assert unquoted(q) == ["The gap is yours to use, so go."]
    assert quote(q.text, unquoted(q)[0]) == 'Sevella shrugs. "The gap is yours to use, so go." You nod.'
    assert first_person('"I will," she says, and you follow her.') is None
    assert first_person("Within reach of my hand, the bar leans.") == "my"
    assert first_person("A sign says *a mine* in faded paint.") is None  # measured: "a mine" is a noun


def test_a_passage_with_its_side_list_passes_on_the_first_draft(tmp_path: Path) -> None:
    """The whole loop: every MUST line covered, nothing for the audit: one narrator call, the rope written."""
    def draft(schema: Any, packet: Any) -> dict[str, Any]:
        return passage("You look over the quay. Fog lies low on the black water. A coil of rope hangs by the "
                       "bollard. What do you do?", _must(packet),
                       new=[{"element_kind": "furniture", "name": "coil of rope", "ordinary": True,
                             "implied": [{"predicate": "location", "value": "by the bollard"}]}])
    model = look_model(narrator=[draft], checker=[chk()])
    dock, ctx = setup(tmp_path, model)
    out = play_turn(ctx, "I look over the quay.")
    assert not out.response.flags.fallback_used and not out.response.flags.review_flag
    assert len(calls(model, Role.NARRATOR)) == 1
    assert [v["kind"] for v in out.turn_record.draft_versions] == ["draft"]
    rope = next(e for e in dock.state.entities.values() if e.name == "coil of rope")
    assert dock.state.fact_value(rope.id, "location") == "by the bollard"  # T1a: written as narrated


def test_the_audit_never_judges_a_guessed_subject(tmp_path: Path) -> None:
    """12.3.1b item 4 (DL-12-82): the Checker read "he" as the watch; with two people present "he" is not a
    certain subject, so the sampled claim takes no verdict and the sentence stands."""
    model = look_model(narrator=[lambda schema, packet: passage("He mends a net by the post. What do you do?",
                                                                 _must(packet))])
    dock, ctx = setup(tmp_path, model)
    model.push(Role.CHECKER, chk(), chk(claim(0, dock.watch, "identity", "gender", "woman")))
    out = play_turn(ctx, "I look over the quay.")  # turn.1: sampled
    [e] = [e for e in out.turn_record.claim_log if e.get("source") == "sample"]
    assert e["verdict"] == "no_verdict" and out.response.fiction.startswith("He mends a net")


def test_the_audit_reads_the_side_list_and_the_last_exchange(tmp_path: Path) -> None:
    """12.3.1 / 12.2.4: the sampled audit sees the passage's sentences, its side list in words (speech, covered
    lines) and the last exchange only."""
    model = look_model()
    dock, ctx = setup(tmp_path, model)
    model.push(Role.NARRATOR, lambda schema, packet: passage(
        'You look over the quay. "Fog\'s in," Tam says. What do you do?', _must(packet),
        speech=[{"speaker": dock.ferryman, "words": "Fog's in,", "form": "direct"}]))
    model.push(Role.CHECKER, chk(), chk())
    play_turn(ctx, "I look over the quay.")  # turn.1: sampled
    diff, full = calls(model, Role.CHECKER)
    assert "[1] \"Fog's in,\" Tam says." in diff.message and "THE SIDE LIST:" in diff.message
    assert "covers R1:" in diff.message and "THE SIDE LIST:" not in full.message
