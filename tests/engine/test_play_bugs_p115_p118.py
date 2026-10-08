"""Playtest bugs P-115 (a dropped Recall's line labels a Talk), P-116 (a foe's landed strike cut from the prose),
P-118 (the one asked about the warning answers, not someone else)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from engine import ids
from engine.audit.claims import check_claims
from engine.data.loader import load_rules
from engine.dm.adjudication import AdjudicationRecord, OracleEntry
from engine.dm.roles.reader import Part, ReaderBeat, ReaderResult, _knowledge_parts
from engine.store.events import Event, SceneRecord
from tests.fixtures.game import entity, new_store


@pytest.fixture(scope="module")
def rules() -> Any:
    return load_rules()


def _store(tmp_path: Path) -> Any:
    store = new_store(tmp_path)
    with store.transaction("turn.0") as tx:
        tx.add(entity("pc", "Wren", tx=tx, quantities={"vitality": (14, 0, 14)}))
        tx.add(entity("place", "Hall", tx=tx))
        tx.add(entity("npc", "Mara Voss", tx=tx))
        tx.add(entity("npc", "Borga Ironhammer", tx=tx))
        sid = tx.mint(ids.SCENE)
        tx.add(Event.of("scene_started", scene_id=sid, scene=SceneRecord(
            scene_id=sid, place_id="loc.hall", cast_present=["npc.mara_voss", "npc.borga_ironhammer"])))
    return store


def test_p115_kept_talk_is_not_labelled_as_the_dropped_recall() -> None:
    out = ReaderResult(
        parts=[Part.model_validate({"class": "FICTION_QUESTION", "text": "What do I know about the token you wear?"}),
               Part.model_validate({"class": "DECLARATION", "text": "Tell me what the niche held."})],
        beats=[ReaderBeat(intent="Learn what the token signifies", method="Recall it", verb="verb.recall",
                          target="npc.mara_voss"),
               ReaderBeat(intent="Get her to say what the niche held", method="Speak aloud", verb="verb.talk",
                          target="npc.mara_voss")],
        restatement="Recall: what the PC knows of the token. Then: speak to her about the niche.")
    _knowledge_parts(out, "pc.wren")
    [plan] = out.plans(actor="pc.wren", declared_seq=0, mint=lambda k: f"{k}.1")
    assert plan.beat.verb == "verb.talk"
    assert plan.beat.restatement == "Get her to say what the niche held"


def test_p116_harm_written_this_turn_backs_the_strike_in_any_words(tmp_path: Path, rules: Any) -> None:
    store = _store(tmp_path)
    claim = {"subject": "pc.wren", "class": "harm_condition", "predicate": "struck",
             "value": "knuckles catch under the ribs", "asserts_change": True}
    [v] = check_claims([claim], store.state, AdjudicationRecord(), ["pc.wren"], rules=rules)
    assert v.fix == "cut"  # no harm this turn: nothing to show
    with store.transaction("turn.1") as tx:
        seq = tx.add(Event.of("quantity_changed", entity="pc.wren", quantity="vitality", delta=-3, new_value=11,
                              reason="the farmer strikes"))
    rec = AdjudicationRecord()
    rec.add_writes([store.event(seq)])  # type: ignore[list-item]
    [v] = check_claims([claim], store.state, rec, ["pc.wren"], rules=rules)
    assert v.verdict == "supported"


def test_p118_the_one_the_question_is_about_answers(tmp_path: Path, rules: Any) -> None:
    store = _store(tmp_path)
    rec = AdjudicationRecord(oracle=[OracleEntry(question="the warning she offers: what it says",
                                                 answer="yes, but lesser", subject="npc.mara_voss")])
    said = {"class": "action", "predicate": "says", "value": "there is a warning, a lesser one",
            "asserts_change": True}
    mara, borga = check_claims([{**said, "subject": "npc.mara_voss"}, {**said, "subject": "npc.borga_ironhammer"}],
                               store.state, rec, ["npc.mara_voss"], rules=rules)
    assert mara.verdict == "supported"
    assert borga.verdict == "unsourced_change"
