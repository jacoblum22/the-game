"""evals/reader_live.py: the golden set's scored fields come from the Reader's verb and facets through the computed
gate, with holdings read from the context string (no model call here)."""

from __future__ import annotations

from evals.reader_live import labels_from, schema


def _answer(verb: str, **facets: bool) -> dict[str, object]:
    beat = {"intent": "x", "method": "read the notice", "shape": "now", "verb": verb, "against_will": False,
            "uses_power": False, "speech": False, **facets}
    return {"parts": [{"text": "x", "class": "DECLARATION", "question_kind": "where_is"}], "beats": [beat]}


def test_gate_is_computed_from_the_context_holdings() -> None:
    held = labels_from(_answer("verb.observe"), "I read the notice.", "Board; PC holds lic.lang.letters")
    assert (held["verb"], held["gate"], held["question_kind"]) == ("verb.observe", "G2", "where_is")
    lacks = labels_from(_answer("verb.observe"), "I read the notice.", "Post; PC does not hold lic.lang.letters")
    assert lacks["gate"] == "G3"
    gentle = labels_from(_answer("verb.grapple", speech=True), "x", "licences: none relevant")
    assert (gentle["verb"], gentle["gate"]) == ("verb.talk", "G1")  # the facets choose the card
    assert labels_from({"parts": [], "beats": []}, "x", "")["gate"] is None


def test_the_schema_is_the_readers() -> None:
    beat = schema()["properties"]["beats"]["items"]["properties"]
    assert {"against_will", "uses_power", "speech", "shape"} <= set(beat) and "gate" not in beat
