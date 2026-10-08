"""The reduced case (PR-15-6 reduced profile, 15.9.4; DL-15-38, DL-12-62): validity, the seeded incident over 30
openings, determinism, the on-demand builder, the pointer, and the placement audit in Milestone 1."""

from __future__ import annotations

import copy
from pathlib import Path

from engine.gen.case import (
    audit_cases,
    case_covering,
    case_for_question,
    cases,
    pointer,
    reduced_case,
    story_option,
    validate_case,
)
from engine.store.events import Event
from engine.time.handlers import runnable
from tests.fixtures.seeded import seeded_store, world


def test_thirty_openings_validate_with_the_core_clue_at_the_opening_place() -> None:
    for seed in range(1, 31):
        reg = world(seed).record
        case = next(c for c in reg["seed_cases"] if c["trigger"] == "incident")
        assert validate_case(case) == [], seed
        core = next(p for p in case["nodes"][0]["placements"] if p["access"] == "core")
        everyone = {n["id"]: n for n in reg["npcs"] + reg.get("walk_ons", [])}
        assert core["at"] == case["opening_place"] == reg["opening"]["start"]["place"]
        assert everyone[core["holder"]]["home"] == case["opening_place"], seed  # someone who is there holds it


def test_in_the_store_the_core_holder_stands_at_the_opening_place(tmp_path: Path) -> None:
    for seed in range(1, 31):
        store, w = seeded_store(tmp_path / str(seed), seed)
        st = store.state
        case = cases(st)[st.meta["world.opening"]["case"]]
        core = next(p for p in case["nodes"][0]["placements"] if p["access"] == "core")
        assert st.positions[core["holder"]].location == w.incident.place, seed


def test_validity_rules_fail_as_15_9_4_says() -> None:
    good = world(21).record["seed_cases"][0]

    def bad(fn) -> list[str]:  # type: ignore[no-untyped-def]
        c = copy.deepcopy(good)
        fn(c)
        return validate_case(c)

    assert any("placements" in x for x in bad(lambda c: c["nodes"][0]["placements"].pop()))
    assert any("reserve" in x for x in bad(lambda c: c["nodes"][1].update(reserve=[])))
    assert "no core placement at the opening place" in bad(lambda c: c.update(opening_place="loc.elsewhere"))
    assert any("methods" in x for x in bad(lambda c: [p.update(method="inquiry") for p in c["nodes"][0]["placements"]]))
    assert any("nodes" in x for x in bad(lambda c: c["nodes"].pop()))
    assert bad(lambda c: c.update(fallbacks=[])) == ["fallbacks"]


def test_same_seed_same_case() -> None:
    reg_a, reg_b = copy.deepcopy(world(5).record), copy.deepcopy(world(5).record)
    a = reduced_case(reg_a, 5, "missing", reg_a["opening"]["start"]["place"], "loc.x", tag="forced")
    b = reduced_case(reg_b, 5, "missing", reg_b["opening"]["start"]["place"], "loc.x", tag="forced")
    assert a == b and validate_case(a) == []


def test_pointer_names_the_core_holder_first() -> None:
    case = world(21).record["seed_cases"][0]
    n1 = case["nodes"][0]
    core = next(p["holder"] for p in n1["placements"] if p["access"] == "core")
    witness = n1["placements"][1]["holder"]
    assert pointer(case, n1["id"], asked=witness) == core
    assert pointer(case, n1["id"], asked=core) == witness  # the core holder asked: the next live holder


def test_story_options() -> None:
    assert story_option("who the missing person is") == "missing"
    assert story_option("the challenger") == "duel"
    assert story_option("the old enemy") is None


def test_a_story_role_question_with_no_case_builds_one(tmp_path: Path) -> None:
    store, w = seeded_store(tmp_path, 1)  # an alarm: no person behind the incident
    place = w.incident.place
    with store.transaction() as tx:
        assert case_covering(tx.state, "who is missing") is None
        case = case_for_question(tx, "who is missing", place)
    assert case is not None and validate_case(case) == []
    assert case["opening_place"] == place and case["id"] in cases(store.state)
    st = store.state
    core = next(p for p in case["nodes"][0]["placements"] if p["access"] == "core")
    assert core["holder"] in st.entities and core["at"] == place
    subject = case["solution"]["subject"]["id"]
    assert subject in st.entities and subject not in st.positions
    with store.transaction() as tx:
        assert case_for_question(tx, "who is the missing child", place) == case  # the same case answers again
    assert store.rebuild() == store.state


def test_placement_audit_places_the_reserve_then_a_generic_witness(tmp_path: Path) -> None:
    assert runnable("h.15.placement_audit", 1) is not None  # live in Milestone 1 (DL-15-38)
    store, w = seeded_store(tmp_path, 21)
    case = w.record["seed_cases"][0]
    n1 = case["nodes"][0]
    people = [p["holder"] for p in n1["placements"] if p["holder_kind"] == "person"]
    with store.transaction() as tx:
        assert audit_cases(tx) == []  # three live placements per node: nothing to do
    with store.transaction() as tx:
        for h in people:  # both people holding node 1 die (as ending.py records it): one live placement is left
            tx.add(Event.of("fact_set", {"source": "ruling"}, source="test", rule_id="t", fact_id=tx.mint("fact"),
                            subject=h, predicate="exists", value="dead"))
        placed = audit_cases(tx)
    assert len(placed) == 1 and "reserve" in placed[0]  # the notice and the reserve witness: two live again
    reserve = cases(store.state)[case["id"]]["nodes"][0]["placements"][-1]["holder"]
    assert reserve in store.state.entities and reserve in store.state.positions
    with store.transaction() as tx:  # the reserve witness leaves too: the reserve is spent, so PR-15-7
        tx.add(Event.of("fact_set", {"source": "ruling"}, source="test", rule_id="t", fact_id=tx.mint("fact"),
                        subject=reserve, predicate="exists", value="departed"))
        placed = audit_cases(tx)
    assert len(placed) == 1 and "PR-15-7" in placed[0]
    people.append(reserve)
    node = cases(store.state)[case["id"]]["nodes"][0]
    live = [p for p in node["placements"] if p["holder"] not in people]
    assert len(live) >= 2 and all(p["holder"] in store.state.entities for p in live if p["holder_kind"] == "person")
