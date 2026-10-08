"""Playtest cluster C (20261008 talker/fighter): Talk answers, NPC repetition, speaker attribution, animals.

The "I don't know" runaround (PR-12-10, 12.10.6, DL-12-44), unchanged activity lines re-narrated every turn and an
engaged NPC still "fetching water" (12.14.11, 12.11.9), the wrong NPC answering (12.11.9 step 4), a dog given a
person's activity and looks, and three small ones (an old question replayed after a move, a Recall that delivered a
difficulty number, a pie never taken)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from engine.data.loader import load_rules
from engine.dm import answer as ans
from engine.dm.adjudication import AdjudicationRecord, BeatEntry, PartEntry
from engine.gen._seed_packs import pack_data
from engine.gen.case import cases
from engine.store.events import WORLD, Event
from tests.engine.test_answer import PC, ask, here, npc_with_pack, outside_topic, turn
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


def test_a_not_ordinary_candidate_is_routed_to_the_case(seeded: Any, monkeypatch: Any) -> None:
    """PR-12-10 step 4: code rejects a `not_ordinary` candidate and step 1's consequential route answers."""
    from engine.dm.roles import proposer

    case, core, _ = _incident(seeded)
    word = sorted(ans.words.content(seeded.state.meta["world.opening"]["inciting"]["text"]))[0]
    monkeypatch.setattr(proposer, "propose", lambda *a, **k: {"kind": "not_ordinary", "subject": f"the {word}",
                                                                 "predicate": "is", "value": "a clue"})
    a = ask(seeded, core, "what_happened", "And the other business, what was that?",
            topic=outside_topic(seeded, core))  # nothing in their pack or the store: rung 3 proposes
    assert a.pointer is None and case["nodes"][0]["fact"] in a.line, a


def test_the_pointer_names_someone_who_can_answer(seeded: Any) -> None:
    owner, item = npc_with_pack(seeded)
    topic = str(item["topic"])
    st = seeded.state
    asked = next(n for n in sorted(st.entities) if st.entities[n].kind == "npc" and n != owner
                 and not ans._can_answer(st, n, topic, None) and n in ans.base_pool(st, PC))
    a = ask(seeded, asked, "who_knows", f"who would know about {topic}?", topic=topic)
    assert a.pointer is not None and ans._can_answer(seeded.state, a.pointer, topic, None), a


def test_a_pointer_chain_is_capped_at_a_place_and_logged(seeded: Any) -> None:
    st = seeded.state
    haven = st.meta["world.region"]["haven"]
    topics = pack_data().CK["topics"]
    topic = next(t for t, v in topics.items() if f"{haven}.{v.get('kept_at')}" in st.entities)
    limit = int(load_rules().pacing["answer_ladder"]["repeat_pointer_limit"])
    people = ans.base_pool(st, PC)[: limit + 1]
    with turn(seeded) as ctx:  # `limit` people already said they did not know it and named someone
        idx = {f"{n}|what_like|{topic}": {"fact": None, "said": "does not know", "pointer": people[-1]}
               for n in people[:limit]}
        ctx.need_tx().add(Event.of("meta_set", source="test", rule_id="12.10.6", key=ans.INDEX, value=idx))
    with turn(seeded) as ctx:
        _, ref = ans.point(ctx, people[-1], topic, PC)
    assert seeded.state.entities[ref].kind == "place", ref  # the chain ends: no further person to chase
    assert seeded.rulings("answer.pointer_chain")  # PR-12-10 step 7: logged for review (DL-12-44)


def test_a_local_never_denies_public_news_the_pc_was_told(seeded: Any, monkeypatch: Any) -> None:
    from engine.resolve import oracle

    monkeypatch.setattr(oracle, "shape_for", lambda *a: "no")
    st = seeded.state
    local = next(n for n in here(seeded) if ans.public_local(st, n, "local_news"))
    with turn(seeded) as ctx:
        tx = ctx.need_tx()
        fid = tx.mint("fact")
        tx.add(Event.of("fact_set", {"source": "oracle"}, source="test", rule_id="PR-12-10", fact_id=fid,
                        subject=WORLD, predicate="topic.local_news.the_ford", value="the ford washed out last night",
                        visibility="shown"))
        tx.add(Event.of("knowledge_recorded", source="test", rule_id="12.10.6", knower=PC, fact_id=fid, how="told"))
    a = ask(seeded, local, "what_happened", "What happened to the ford?", topic="local_news")
    assert a.fact_id == fid and a.pointer is None, a


def test_a_particular_question_is_not_answered_by_any_fact_on_its_topic(seeded: Any) -> None:
    """"What's the word on the ambush at the fortress?" filed under local news: the festival gossip in their pack is
    not its answer (Fenwin, talker 29)."""
    owner, item = npc_with_pack(seeded)
    topic = str(item["topic"])
    a = ask(seeded, owner, "what_happened", "What's the word on the ambush at the fortress?", reach=1,
            topic="the ambush at the fortress")
    assert item["text"] not in a.line, a
    b = ask(seeded, owner, "what_like", f"what do you hear about {topic.replace('_', ' ')}?", reach=1, topic=topic)
    assert item["text"] in b.line, b  # asked about the topic itself, the pack answers


def test_a_pack_topic_is_asked_at_the_role_odds(seeded: Any) -> None:
    owner, item = npc_with_pack(seeded)
    ck = pack_data().CK
    assert ans.odds_for(seeded.state, owner, str(item["topic"])) == ck["odds"]["on_role_topic"]


def test_a_knowledge_question_to_the_one_asked_is_the_ladders(seeded: Any) -> None:
    npc = here(seeded)[0]
    st = seeded.state
    assert ans.ladder_owns(st, npc, "knows the details of the ambush at the fortress", [npc])
    assert not ans.ladder_owns(st, npc, "knows the details of the ambush", [])  # not asked: the Oracle's
    assert not ans.ladder_owns(st, npc, "is locked", [npc])


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
    assert eid not in ans.base_pool(store.state, None)  # never cast as one who would know


def test_a_horse_trader_is_a_person() -> None:
    from engine.dm.npc_layer import ANIMAL

    assert ANIMAL.match("dog at Nero's heel") and ANIMAL.match("old grey dog") and ANIMAL.match("dog")
    assert not ANIMAL.match("horse trader") and not ANIMAL.match("cat burglar")


# ------------------------------------------------------------------------------------------- 2. repeated lines


def test_unchanged_lines_are_not_shown_again_and_an_engaged_npc_left_off_their_activity(tmp_path: Path) -> None:
    from engine.dm.handles import items
    from engine.dm.roles.narrator import record_text
    from engine.dm.turn import play_turn
    from engine.llm.base import Role
    from engine.llm.offline import ScriptedModel
    from tests.engine.test_turn_adjudication import reader, setup

    ask_ = "Tam, is the ferry running tonight?"
    hello = '"Evening," I say.'
    dock, ctx = setup(tmp_path, ScriptedModel({Role.READER: [reader("FICTION_QUESTION", ask_),
                                                             reader("SPEECH", hello)]}), world_judge=False)
    first = play_turn(ctx, ask_).adjudication.record
    acts = {a.npc: a for a in first.activities if a.slot == "activity"}
    assert acts[dock.ferryman].hidden == "engaged" and not acts[dock.watch].hidden  # Tam is being asked
    assert "has left off" in record_text(dock.state, first) and "Tam" in record_text(dock.state, first)
    second = play_turn(ctx, hello).adjudication.record
    watch = next(a for a in second.activities if a.npc == dock.watch and a.slot == "activity")
    assert watch.hidden == "stale"  # unchanged since last turn: not a line to narrate again (12.14.11)
    assert not [it for it in items(second) if it.kind == "activity" and it.text == watch.activity]


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
