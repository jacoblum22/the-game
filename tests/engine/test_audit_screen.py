"""The T10 screen: mechanics in the fiction (12.14.4), the open prompt (12.14.9), and the combined flags."""

from __future__ import annotations

import pytest

from engine.audit.claims import Verdict
from engine.audit.safety import SafetyEntry, screen_safety
from engine.audit.screen import ends_on_prompt, mechanics_in_fiction, pause_blocks, screen_draft
from engine.dm.adjudication import AdjudicationRecord, PartEntry, PauseEntry

FLAGS = {"intent_acknowledged": True, "intent_substituted": False, "next_step_exists": True,
         "mechanics_in_fiction": [], "ends_on_prompt_or_one_pause": True}


@pytest.mark.parametrize("text", [
    "You need a 14 to make it.", "Make a Might check.", "The DC is high here.", "Roll a d20.",
    "You rolled high.", "Your roll comes up short.", "It is a success at cost.", "A near miss, then.",
    "You take a critical_success.", "Your Agility carries you.", "A Hard climb, this.", "You are Frightened now.",
    "That costs two HP.", "Your Vitality ebbs.", "cond.prone grips you.", "You gain a bonus.", "Severity S2 applies.",
    "You make a Wits check.", "It is a Very hard task.",
])
def test_mechanics_caught(text: str) -> None:
    assert mechanics_in_fiction(text), text


@pytest.mark.parametrize("text", [
    "You might slip past him.", "Her resolve hardens.", "A hard climb waits above the rope.",
    "Frightened eyes watch you from the stall.", "You check the door; it holds.", "A roll of cloth lies on the bench.",
    "The barrel rolls downhill.", "Your last two arrows rattle.", "The presence in the room feels heavy.",
    "Might is not the word for it.", "His wits are sharp.", "The stakes are high, and everyone knows it.",
    "Prone to gossip, the ferryman talks.", "You focus on the lock.", "Easy now, says the guard.",
])
def test_ordinary_prose_passes(text: str) -> None:
    assert mechanics_in_fiction(text) == [], mechanics_in_fiction(text)


def test_names_are_not_rules_words() -> None:
    assert mechanics_in_fiction("You reach the Broken Tower at last.") == ["Broken"]
    assert mechanics_in_fiction("You reach the Broken Tower at last.", names=["Broken Tower"]) == []


def test_prompt_and_pause_blocks() -> None:
    assert ends_on_prompt('The ferryman holds out his hand. "Do you pay?"')
    assert not ends_on_prompt("The ferryman holds out his hand.")
    assert pause_blocks(["[OFFER] Break the hasp\n  Mode: normal", "[WARNING] THIS CAN KILL YOU"]) == ["OFFER"]


def _record() -> AdjudicationRecord:
    return AdjudicationRecord(pc="pc.wren", parts=[PartEntry.model_validate({"text": "I ask Mara about the ledger.",
                                                                        "class": "SPEECH"})])


def test_screen_passes_a_good_draft() -> None:
    res = screen_draft("Mara taps the ledger and says nothing about it. What do you do?", flags=FLAGS,
                       record=_record())
    assert res.passed, res.reasons
    assert set(res.screen) == {"intent_acknowledged", "intent_substituted", "next_step_exists", "mechanics_in_fiction",
                               "ends_on_prompt_or_one_pause", "pc_agency_ok", "safety_ok"}


def test_screen_failures_name_their_rule() -> None:
    res = screen_draft("The rain falls. You need a 12 to win.", flags={**FLAGS, "ends_on_prompt_or_one_pause": False},
                       record=_record(), verdicts=[Verdict(claim=0, verdict="pc_agency", fix="cut")],
                       safety=screen_safety("The rain falls on a spider.", [SafetyEntry(kind="line", topic="spiders")]))
    text = " ".join(res.reasons)
    for rule in ("12.2.7", "12.14.4", "12.14.9", "12.14.3", "12.5.6"):
        assert rule in text
    assert not res.passed and res.screen["mechanics_in_fiction"] == ["12"]
    assert res.screen["safety_ok"] is False and res.screen["pc_agency_ok"] is False


def test_two_questions_each_need_an_answer() -> None:
    """P-080 (playtest 20261007-201338 breaker, input 28): "Who was the child's mother? And does Rakum have anything
    to do with the child?" was delivered with only the Rakum half; the parts were marked answered before the draft
    existed, so the screen never looked, and the shared word "child" covered both."""
    rec = AdjudicationRecord(parts=[
        PartEntry.model_validate({"text": "Who was the child's mother?", "class": "FICTION_QUESTION",
                                  "handled": "answered"}),
        PartEntry.model_validate({"text": "And does Rakum have anything to do with the child?",
                                  "class": "FICTION_QUESTION", "handled": "answered"}),
        PartEntry.model_validate({"text": "what are my options?", "class": "FICTION_QUESTION", "handled": "noted"})])
    half = screen_draft("You ask whether Rakum has any hand in the child's going. What do you ask her next?",
                        flags=FLAGS, record=rec)
    assert not half.passed and "child's mother" in half.reasons[0]
    both = screen_draft("You ask who the child's mother was; Rosie names none. You ask whether Rakum has any hand "
                        "in the child's going. What do you ask her next?", flags=FLAGS, record=rec)
    assert both.passed, both.reasons


def test_screen_flags_and_pause() -> None:
    rec = _record()
    rec.pause = PauseEntry(kind="offer")
    ok = screen_draft("Mara slides the ledger across.", flags={**FLAGS, "next_step_exists": False}, record=rec,
                      pause_blocks_text=["[OFFER] Read the ledger"])
    assert ok.passed, ok.reasons
    two = screen_draft("Mara slides the ledger across.", flags=FLAGS, record=rec,
                       pause_blocks_text=["[OFFER] a", "[CHOICE] b"])
    assert not two.passed
    sub = screen_draft("Mara slides the ledger across. What now?", flags={**FLAGS, "intent_substituted": True},
                       record=_record())
    assert not sub.passed and "12.2.7" in sub.reasons[0]
    listy = screen_draft("Mara waits.\n1. Pay her\n2. Leave\nWhat do you do?", flags=FLAGS, record=_record())
    assert not listy.passed
