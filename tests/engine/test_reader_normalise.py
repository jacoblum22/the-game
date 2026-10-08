"""reader.normalise: code decides what the Reader marks (01.2.1, 01.2.2, 00.12.6, 12.2.2, 15.3.10)."""

from __future__ import annotations

from typing import Any

from engine.dm.roles.reader import normalise


def _beat(verb: str, purpose: str = "own_change", pressure: str = "none", **facets: Any) -> dict[str, Any]:
    return {"verb": verb, "method": verb.removeprefix("verb."), "purpose": purpose, "pressure": pressure,
            "against_will": False, "uses_power": False, **facets}


def _part(cls: str, kind: str = "none") -> dict[str, Any]:
    return {"text": "x", "class": cls, "question_kind": kind}


def _verbs(data: dict[str, Any]) -> list[str]:
    return [b["verb"] for b in normalise(data)["beats"]]


def test_a_supporting_step_folds_into_the_act_it_serves() -> None:
    out = normalise({"parts": [_part("DECLARATION")],
                     "beats": [_beat("verb.move", "serves_another_act"), _beat("verb.strike", against_will=True)]})
    assert [(b["verb"], b["method"]) for b in out["beats"]] == [("verb.strike", "move, strike")]


def test_a_gesture_that_serves_only_words_goes_and_a_lone_step_stays() -> None:
    words = [_part("DECLARATION"), _part("SPEECH", "who_is")]
    assert _verbs({"parts": words, "beats": [_beat("verb.move", "serves_another_act")]}) == []
    assert _verbs({"parts": [_part("DECLARATION")], "beats": [_beat("verb.move", "serves_another_act")]}) == [
        "verb.move"]
    assert _verbs({"parts": words, "beats": [_beat("verb.move")]}) == ["verb.move"]  # a destination of its own


def test_free_activities_are_no_beat_but_a_hold_against_the_will_is() -> None:
    parts = [_part("DECLARATION")]
    assert _verbs({"parts": parts, "beats": [_beat("verb.endure", "free_activity")]}) == []
    grab = _beat("verb.grapple", "serves_another_act", against_will=True)
    assert _verbs({"parts": [*parts, _part("SPEECH")], "beats": [grab]}) == ["verb.grapple"]


def test_only_the_rules_free_acts_and_bodily_acts_take_the_marks() -> None:
    parts = [_part("DECLARATION"), _part("SPEECH")]
    look = _beat("verb.observe", "free_activity")
    assert _verbs({"parts": parts, "beats": [look]}) == ["verb.observe"]  # a look is free only when casual
    assert _verbs({"parts": parts, "beats": [{**look, "method": "glance at the door"}]}) == []
    offer = _beat("verb.talk", "serves_another_act", pressure="offer")
    assert _verbs({"parts": parts, "beats": [offer]}) == ["verb.talk"]  # words are never a gesture
    assert _verbs({"parts": parts, "beats": [_beat("verb.talk", "free_activity", pressure="request")]}) == [
        "verb.talk"]


def test_a_step_that_closes_on_the_next_blow_is_its_reach() -> None:
    blow = _beat("verb.strike", against_will=True, target="npc.a")
    assert _verbs({"parts": [], "beats": [_beat("verb.move", target="npc.a"), blow]}) == ["verb.strike"]
    assert _verbs({"parts": [], "beats": [_beat("verb.move", target="place.gate"), blow]}) == [
        "verb.move", "verb.strike"]


def test_a_plain_question_read_as_talk_is_speech() -> None:
    out = normalise({"parts": [_part("DECLARATION", "who_is")], "beats": [_beat("verb.talk")]})
    assert out["beats"] == [] and out["parts"][0]["class"] == "SPEECH"
    threat = _beat("verb.talk", pressure="threat")
    assert _verbs({"parts": [_part("DECLARATION", "who_is")], "beats": [threat]}) == ["verb.talk"]
    # "I talk to Marard" asks nothing: the tie-break keeps it a Talk beat (12.2.2)
    assert _verbs({"parts": [_part("DECLARATION")], "beats": [_beat("verb.talk")]}) == ["verb.talk"]


def test_answers_without_the_marks_are_unchanged() -> None:
    data = {"parts": [_part("DECLARATION", "who_is")], "beats": [{"verb": "verb.talk", "method": "ask"}]}
    assert normalise(data) == data
