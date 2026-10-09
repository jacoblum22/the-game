"""Answering a question (PR-12-10, 12.10.8; spec 013): the consequential route by the case, casting, and for
everything else a willingness line only (no store, pack, propose-and-ratify or pointer rung: DL-12-90); depth by
reach (T-01-6); the index remembers the willingness, so asking twice draws nothing."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import pytest

from engine.dm import answer as ans
from engine.dm.context import TurnContext
from engine.gen.case import cases
from engine.llm.offline import OfflineModel
from engine.store.events import Event
from tests.fixtures.seeded import seeded_store

PC = "pc.wren"


@contextmanager
def turn(store: Any, model: Any = None) -> Iterator[TurnContext]:
    ctx = TurnContext.for_store(store, model=model or OfflineModel())
    with store.transaction() as tx:
        ctx.tx = tx
        try:
            yield ctx
        finally:
            ctx.tx = None


def ask(store: Any, npc: str, kind: str, text: str, reach: int = 2, topic: str | None = None,
        model: Any = None) -> ans.Answer:
    with turn(store, model) as ctx:
        return ans.ask(ctx, npc, kind, topic, text, pc=PC)


def here(store: Any) -> list[str]:
    st = store.state
    place = st.positions[PC].location
    return sorted(i for i, p in st.positions.items() if p.location == place and i.startswith("npc."))


def npc_with_pack(store: Any) -> tuple[str, dict[str, Any]]:
    st = store.state
    for i, e in sorted(st.entities.items()):
        for k in e.data.get("knowledge") or [] if e.kind == "npc" else []:
            if k.get("text") and k.get("slot") == "trade":
                return i, k
    raise AssertionError("no packed NPC")


def outside_topic(store: Any, npc: str) -> str:
    """A topic neither in the NPC's pack nor among their role's topics (rung 3 asks at Unlikely)."""
    from engine.gen._seed_packs import pack_data, role_key

    ck = pack_data().CK
    e = store.state.entities[npc]
    mine = {k.get("topic") for k in e.data.get("knowledge") or []} | set(ck["by_role"][role_key(e.data)])
    return next(t for t in ck["topics"] if t not in mine and not ck["topics"][t].get("public"))


@pytest.fixture()
def seeded(tmp_path: Path) -> Any:
    return seeded_store(tmp_path, 8)[0]


# ------------------------------------------------------------------------------------------- depth, never empty


def test_depth_by_reach() -> None:
    assert [ans.deliver_count(3, r) for r in (0, 1, 2, 3, 4)] == [0, 1, 2, 3, 3]
    assert [ans.deliver_count(1, r) for r in (1, 2, 3)] == [1, 1, 1]  # one question: any success lands it
    assert ans.deliver_count(6, 1) == 2 and ans.deliver_count(5, 2) == 3


def test_volunteer_tells_a_pack_fact_unasked(seeded: Any) -> None:
    npc, _ = npc_with_pack(seeded)
    with turn(seeded) as ctx:
        extra = ans.volunteer(ctx, npc, PC)
    assert extra is not None and extra.fact_id in seeded.state.knowledge[PC]


def test_an_ordinary_question_is_a_willingness_line_never_a_pointer(seeded: Any) -> None:
    """PR-12-10 steps 2-4: no rung answers it; code gives willingness only and the narrator chooses the words."""
    from engine.gen._seed_packs import pack_data

    topics = list(pack_data().CK["topics"])
    people = here(seeded)
    facts = len(seeded.state.facts)
    for i, topic in enumerate(topics):
        npc = people[i % len(people)]
        a = ask(seeded, npc, ("what_like", "where_is", "who_knows")[i % 3], f"what about {topic}?", topic=topic)
        assert a.willingness in ("willing", "guarded", "unwilling") and a.pointer is None and a.fact_id is None
        assert "but" not in a.line.split('"')[-1] and "would" not in a.line.split('"')[-1]  # no "but X would"
    assert not [f for f in seeded.state.facts.values() if f.predicate.startswith(("points_to.", "knows_", "topic."))]
    assert len(seeded.state.facts) - facts < len(topics)  # no world fact per answer (standing rolls only)
    assert seeded.rebuild() == seeded.state


def test_ask_twice_keeps_the_willingness_and_rolls_nothing(seeded: Any) -> None:
    for npc in here(seeded):
        for kind, text, topic in (("what_like", "what are the roads like?", "roads"),
                                  ("who_is", "who is missing?", None), ("what_want", "what do you want?", None)):
            first = ask(seeded, npc, kind, text, topic=topic)
            draws = len(seeded.rng_draws())
            again = ask(seeded, npc, kind, text, topic=topic)
            assert (again.fact_id, again.line, again.pointer, again.willingness) == (
                first.fact_id, first.line, first.pointer, first.willingness)
            assert len(seeded.rng_draws()) == draws  # the index remembers; nothing is rolled twice


# ------------------------------------------------------------------------------------------- consequential


def test_a_story_role_goes_to_the_case_graph(seeded: Any) -> None:
    """"Who is missing?": a non-holder names the core holder; the holder delivers it and the node is found."""
    case = next(c for c in cases(seeded.state).values() if c["option"] == "missing") if any(
        c["option"] == "missing" for c in cases(seeded.state).values()) else None
    people = here(seeded)
    answers = {n: ask(seeded, n, "who_is", '"Who is missing?"') for n in people}
    case = case or next(c for c in cases(seeded.state).values() if c["option"] == "missing")
    core = next(p["holder"] for p in case["nodes"][0]["placements"] if p["access"] == "core")
    st = seeded.state
    for n, a in answers.items():
        if n == core:
            assert case["solution"]["subject"]["words"] in a.line and a.pointer is None
        else:
            assert a.pointer == core and "does not know who is missing" in a.line
    assert cases(st)[case["id"]]["nodes"][0]["found"] is True


def test_who_is_a_role_is_cast_and_the_dm_side_points_until_told(seeded: Any) -> None:
    with turn(seeded) as ctx:
        smith = ans.who_answer(ctx, "who is the smith")
        missing = ans.who_answer(ctx, "who is missing")
        assert ans.who_answer(ctx, "is the door locked") is None
    st = seeded.state
    assert smith is not None and st.facts[smith[1]].value in st.entities  # an existing person
    assert missing is not None and missing[0].startswith("no one has told you")  # the PC was not told


def test_a_search_at_a_holder_place_finds_the_node(seeded: Any) -> None:
    """15.9.5 / mark_found: node 2's core placement is a place searched (node 1 found first)."""
    from engine.dm.adjudication import AdjudicationRecord, BeatEntry
    from engine.dm.world_step import _look

    st = seeded.state
    case = next(c for c in cases(st).values() if c.get("trigger") == "incident")
    n1, n2 = case["nodes"]
    with turn(seeded) as ctx:
        ans.deliver_node(ctx, case, n1, None, PC)
    place = next(p for p in n2["placements"] if p["holder_kind"] == "place")["holder"]
    with turn(seeded) as ctx:
        ctx.need_tx().add(Event.of("position_set", source="test", rule_id="10.1.1", entity=PC, location=place))
    record = AdjudicationRecord(pc=PC)
    e = BeatEntry(actor=PC, targets=[], restatement="I search the place", approach_words="verb.observe, search")
    record.beats.append(e)
    with turn(seeded) as ctx:
        got = _look(ctx, e, "verb.observe", 2, PC, [])
    assert got and n2["fact"] in got[0].line
    assert cases(seeded.state)[case["id"]]["nodes"][1]["found"] is True


# ------------------------------------------------------------------------------------------- determinism, openings


def _script(tmp_path: Path, name: str) -> list[tuple[str | None, str | None, str, str | None]]:
    store, _ = seeded_store(tmp_path, 8, name=name)
    out = []
    for npc in here(store):
        for kind, text in (("who_is", "who is missing?"), ("what_like", "what are prices like?"),
                           ("what_happened", "what happened here?"), ("who_knows", "who would know the roads?")):
            a = ask(store, npc, kind, text, reach=3)
            out.append((a.fact_id, a.pointer, a.line, a.willingness))
    return out


def test_deterministic_with_the_offline_model(tmp_path: Path) -> None:
    assert _script(tmp_path, "a.db") == _script(tmp_path, "b.db")


def turns_to_learn(store: Any, rng: Any) -> int:
    """'Who is missing?' asked at the opening place by a PC who knows no holder (12-answer_ladder_sim's part C):
    each turn asks one person; a pointer to someone elsewhere costs a turn to go there."""
    st = store.state
    place = st.positions[PC].location
    subjects = {c["solution"]["subject"]["id"] for c in cases(st).values()}
    asked = rng.choice([n for n in here(store) if n not in subjects])
    for t in range(1, 7):
        st = store.state
        if st.positions.get(asked) is not None and st.positions[asked].location != place \
                and st.positions[PC].location != st.positions[asked].location:
            with turn(store) as ctx:  # going to them takes this turn
                ctx.need_tx().add(Event.of("position_set", source="test", rule_id="10.1.1", entity=PC,
                                           location=st.positions[asked].location))
            continue
        a = ask(store, asked, "who_is", '"Who is missing?"')
        if a.pointer is None:
            return t
        asked = a.pointer
    return 99


def test_who_is_missing_is_answered_within_3_turns_in_30_openings(tmp_path: Path) -> None:
    import random

    rng = random.Random(12010)
    turns = [turns_to_learn(seeded_store(tmp_path, s, name=f"s{s}.db")[0], rng) for s in range(1, 31)]
    assert sum(t <= 3 for t in turns) == 30, turns
