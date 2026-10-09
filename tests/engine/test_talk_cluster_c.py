"""Playtest cluster C (20261008 talker/fighter): Talk answers, NPC repetition, speaker attribution, animals.

The incident's question goes to its case (PR-12-10), an engaged NPC's activity ends (12.11.9, spec 013), the wrong
NPC answering (12.11.9 step 4), a dog given a person's activity and looks, and three small ones (an old question
replayed after a move, a Recall that delivered a difficulty number, a pie never taken). The runaround fixes of
cluster C (pointer rules) were retired with the ladder (spec 013, DL-12-90)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from engine.data.loader import load_rules
from engine.dm.adjudication import AdjudicationRecord, BeatEntry, PartEntry
from engine.gen.case import cases
from engine.store.events import WORLD, Event
from tests.engine.test_answer import PC, ask, here, turn
from tests.fixtures.seeded import seeded_store


@pytest.fixture()
def seeded(tmp_path: Path) -> Any:
    return seeded_store(tmp_path, 8)[0]


def _incident(store: Any) -> tuple[dict[str, Any], str, str]:
    """The opening's incident case, the core holder of its first node, and someone here who holds nothing."""
    case = next(c for c in cases(store.state).values() if c.get("trigger") == "incident")
    core = next(p["holder"] for p in case["nodes"][0]["placements"] if p.get("access") == "core")
    holders = {p["holder"] for n in case["nodes"] for p in n["placements"]}
    other = next(n for n in here(store) if n not in holders and n != case["solution"]["subject"]["id"])
    return case, core, other


# ------------------------------------------------------------------------------------------- 1. the runaround


def test_a_question_about_the_incident_goes_to_its_case(seeded: Any) -> None:
    """"What did the rider say before he died?" is the incident's own matter (a rider dies ... with a message): the
    holder tells it, never "I do not know, ask Fenwin" about local news."""
    case, core, other = _incident(seeded)
    text = str(seeded.state.meta["world.opening"]["inciting"]["text"])  # the incident in the asker's words
    b = ask(seeded, other, "what_happened", f"What do you know of it: {text}?", topic="local_news")
    assert b.pointer == core  # a non-holder names the holder, not whoever knows the local news
    a = ask(seeded, core, "what_happened", f"Tell me about it: {text}?")
    assert a.pointer is None and case["nodes"][0]["fact"] in a.line, a


def test_a_knowledge_question_to_the_one_asked_is_their_speech(seeded: Any) -> None:
    from engine.dm.turn import speech_owns

    npc = here(seeded)[0]
    st = seeded.state
    assert speech_owns(st, npc, "knows the details of the ambush at the fortress", [npc])
    assert not speech_owns(st, npc, "knows the details of the ambush", [])  # not asked: the Oracle's
    assert not speech_owns(st, npc, "is locked", [npc])


# ------------------------------------------------------------------------------------------- 5. a Recall


def test_a_recall_never_delivers_a_checks_difficulty(seeded: Any, monkeypatch: Any) -> None:
    from engine.dm.world_step import _look
    from engine.resolve import oracle

    monkeypatch.setattr(oracle, "shape_for", lambda *a: "no")
    with turn(seeded) as ctx:
        tx = ctx.need_tx()
        tx.add(Event.of("fact_set", {"source": "ruling"}, source="test", rule_id="01.4.1", fact_id=tx.mint("fact"),
                        subject=WORLD, predicate="dc.wren_recalls_the_ferryman", value=15, visibility="background"))
    e = BeatEntry(actor=PC, targets=[], restatement="Recall: what Wren recalls of the ferryman",
                  approach_words="verb.recall, intellect")
    with turn(seeded) as ctx:
        got = _look(ctx, e, "verb.recall", 2, PC, [])
    assert got and not any("15" in a.line or "recalls the ferryman" in a.line.lower() for a in got), got


# ------------------------------------------------------------------------------------------- 3. who answers


def _part(text: str, handled: str = "") -> PartEntry:
    return PartEntry.model_validate({"text": text, "class": "SPEECH", "handled": handled})


def _people(tmp_path: Path) -> tuple[Any, dict[str, str]]:
    from tests.fixtures.game import entity, new_store

    store = new_store(tmp_path)
    with store.transaction() as tx:
        for name, data in (("Nero Verent", {"role": "head of The Swanley Collegium", "name_known": True}),
                           ("Loran Longwell", {"role": "officer of The Swanley Collegium", "name_known": False}),
                           ("Nibwen Appleburrow", {"role": "neighbour", "name_known": False}),
                           ("Gribok", {"role": "dog at Nero's heel", "name_known": False})):
            tx.add(entity("npc", name, tx=tx, data=data))
    st = store.state
    return store, {e.name.split()[0]: e.id for e in st.entities.values()}


def test_the_addressed_npc_is_the_one_named_not_one_whose_title_shares_a_word(tmp_path: Path) -> None:
    from engine.dm.npc_layer import addressed, named_in

    store, p = _people(tmp_path)
    st = store.state
    present = list(p.values())
    assert named_in(st, "I walk over to the officer of The Swanley Collegium.", present) == [p["Loran"]]
    record = AdjudicationRecord(pc=None, parts=[_part("I thank Nero"),
                                                _part("Do you know the way to the hall, friend?")])
    said = 'I thank Nero and ask the neighbour with the crutch, "Do you know the way to the hall, friend?"'
    assert addressed(st, record, present, said)[0] == p["Nibwen"]  # the one asked, not the one thanked
    assert p["Gribok"] not in addressed(st, record, present, "I pat the dog at Nero's heel and speak to it.")


# ------------------------------------------------------------------------------------------- 4. animals


def test_a_dog_is_a_creature_never_a_person(tmp_path: Path) -> None:
    from engine.dm.mentions import write_mentions
    from engine.dm.npc_layer import is_animal
    from tests.fixtures.game import new_store

    store = new_store(tmp_path)
    with store.transaction() as tx:
        res = write_mentions([{"kind": "npc", "name": "the dog at Nero's heel",
                               "implied": [{"predicate": "state", "value": "always at her heel"}]}],
                             tx=tx, rules=load_rules(), rng=None)
    eid = next(iter(res.created.values()))
    e = store.state.entities[eid]
    assert e.data.get("mind") == "animal" and is_animal(store.state, eid)
    assert not {"people", "detail", "demeanor", "pronouns"} & set(e.data)  # no person's walk-on roll
    from engine.gen.cast import base_pool

    assert eid not in base_pool(store.state, None)  # never cast as one who would know


def test_a_horse_trader_is_a_person() -> None:
    from engine.dm.npc_layer import ANIMAL

    assert ANIMAL.match("dog at Nero's heel") and ANIMAL.match("old grey dog") and ANIMAL.match("dog")
    assert not ANIMAL.match("horse trader") and not ANIMAL.match("cat burglar")


# ------------------------------------------------------------------------------------------- 2. repeated lines


def test_an_engaged_npcs_activity_ends_and_activities_are_optional_material(tmp_path: Path) -> None:
    """Spec 013 (DL-12-92/93): the asked NPC's activity ends on engagement and is not re-rolled; the other's stays,
    rolled once; no activity is a record line (optional material, no handle)."""
    from engine.dm.handles import items
    from engine.dm.npc_layer import current_activity
    from engine.dm.roles.narrator import record_text
    from engine.dm.turn import play_turn
    from engine.llm.base import Role
    from engine.llm.offline import ScriptedModel
    from tests.engine.test_turn_adjudication import reader, setup

    ask_ = "Tam, is the ferry running tonight?"
    hello = '"Evening," I say.'
    dock, ctx = setup(tmp_path, ScriptedModel({Role.READER: [reader("FICTION_QUESTION", ask_),
                                                             reader("SPEECH", hello)]}), world_judge=False)
    watch_before = current_activity(dock.state, dock.watch)
    first = play_turn(ctx, ask_).adjudication.record
    acts = {a.npc: a.activity for a in first.activities if a.slot == "activity"}
    assert dock.ferryman not in acts and current_activity(dock.state, dock.ferryman) is None  # ended: Tam engaged
    assert not [it for it in items(first) if it.kind == "activity"]
    watch = current_activity(dock.state, dock.watch)
    assert watch and (watch_before is None or watch == watch_before)
    if dock.watch in acts:  # offered only the turn it is new (12.14.11): optional material
        assert "OPTIONAL MATERIAL" in record_text(dock.state, first)
    second = play_turn(ctx, hello).adjudication.record
    again = {a.npc: a.activity for a in second.activities if a.slot == "activity"}
    assert dock.watch not in again and dock.ferryman not in again  # unchanged: not offered again
    assert current_activity(dock.state, dock.watch) == watch and current_activity(dock.state, dock.ferryman) is None


# ------------------------------------------------------------------------------------------- 5. small ones


def test_a_question_left_behind_by_a_move_is_not_owed(tmp_path: Path) -> None:
    from engine.dm.narration import _unanswered

    parts = [_part('"Which way is the hall from here?"', "answered"), _part('"And is it a long walk?"', "answered")]
    record = AdjudicationRecord(pc=PC, parts=parts)
    assert _unanswered(record, "You cross into the hall.")
    record.scene.started = "scn.2"
    assert _unanswered(record, "You cross into the hall.") == []  # said to someone left behind: not replayed


def test_something_offered_with_a_talk_is_taken() -> None:
    from engine.dm.npc_layer import talk_outcome

    e = BeatEntry(restatement="Talk to the neighbour: offer the pie and ask about the ambush", learned=["x"])
    assert talk_outcome(e, True) == "takes what you offer and answers what you asked"
    assert talk_outcome(e) == "answers what you asked"
