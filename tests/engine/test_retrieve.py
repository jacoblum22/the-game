"""Retrieval caps and determinism (T020): anchors (≤8), cards (≤12 plus the core), active triggers."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest

from engine.build.compile_cards import load_cards
from engine.data.loader import load_rules
from engine.llm.base import Role
from engine.retrieve.anchors import anchor_candidates, anchor_menu, natural_key, verb_anchor
from engine.retrieve.cards import ROLE_CARDS, load_cards_for, role_cards, situation_cards
from engine.retrieve.scene import MAX_SCENE_FACTS, scene_facts, scene_scope
from engine.retrieve.triggers import TRIGGERS, get_active_triggers, trigger_cards
from engine.store.db import Store
from engine.store.events import Event
from tests.fixtures.game import entity, new_store

RULES = load_rules()
INDEX = load_cards()


def fact(tx, subject: str, predicate: str, value, **kw) -> Event:
    return Event.of("fact_set", {"source": kw.pop("source", "narration")}, fact_id=tx.mint("fact"), subject=subject,
                    predicate=predicate, value=value, supersedes=tx.state.current_fact_id(subject, predicate), **kw)


def start_scene(tx, place: str, cast: list[str], mode: str = "free", tags: list[str] | None = None) -> Event:
    sid = tx.mint("scn")
    return Event.of("scene_started", scene_id=sid, scene={"scene_id": sid, "place_id": place, "cast_present": cast,
                                                          "mode": mode, "situation_tags": tags or []})


@pytest.fixture
def store(tmp_path: Path) -> Iterator[Store]:
    s = new_store(tmp_path)
    with s.transaction("turn.1") as tx:
        tx.add(entity("pc", "Wren", tx=tx, quantities={"vitality": (10, 0, 10)}))
        tx.add(entity("place", "Salt Harbor", tx=tx))
        tx.add(entity("npc", "Mara Voss", tx=tx))
        tx.add(start_scene(tx, "loc.salt_harbor", ["npc.mara_voss"], mode="conflict",
                           tags=["situation.conflict.chase"]))
    yield s
    s.close()


# ---------------------------------------------------------------- anchors

BEATS = [
    {"verb": "verb.move", "intent_verbs": ["dash", "get past"], "intent": "I dash past the guard", "method": "run"},
    {"verb": "verb.talk", "intent_verbs": ["persuade"], "intent": "I persuade Mara", "method": "talk"},
    {"verb": "verb.setup", "intent_verbs": ["throw sand"], "intent": "I throw sand in its eyes", "method": "sand"},
    {"verb": "verb.observe", "intent_verbs": ["search", "look for"], "intent": "I search the room"},
    {"verb": None, "intent_verbs": [], "intent": "I wait"},
]


@pytest.mark.parametrize("beat", BEATS)
def test_anchor_candidates_are_capped_deterministic_and_default_first(store: Store, beat) -> None:
    first = anchor_candidates(beat, store.state, RULES)
    assert first == anchor_candidates(dict(reversed(list(beat.items()))), store.state, RULES)
    assert len(first) <= 8 and len(first) == len(set(first))
    assert all(a in RULES.anchors for a in first)
    default = verb_anchor(beat["verb"], RULES)
    if default:
        assert first[0] == default  # 00.15.3: the basic verb's anchor is always a candidate (the default)


def test_anchor_candidates_find_the_specific_ruling(store: Store) -> None:
    cands = anchor_candidates(BEATS[2], store.state, RULES)
    assert "anc.06_t9_01" in cands  # T-06-9 row 1: throw sand in its eyes
    assert anchor_menu(cands, RULES)[0].startswith(cands[0] + ":")


def test_situation_alone_does_not_make_a_candidate(store: Store) -> None:
    cands = anchor_candidates({"verb": None, "intent_verbs": [], "intent": ""}, store.state, RULES)
    assert cands == []


def test_natural_key_orders_rule_ids() -> None:
    assert sorted(["01.6.10", "01.6.9", "T-06-10", "T-06-9"], key=natural_key) == \
        ["01.6.9", "01.6.10", "T-06-9", "T-06-10"]


# ---------------------------------------------------------------- cards


def test_role_card_ids_exist_and_d_only_cards_are_dropped() -> None:
    for role, ids in ROLE_CARDS.items():
        assert all(i in INDEX for i in ids), role
    reader = [c.id for c in role_cards(Role.READER)]
    assert "01.2.3" not in reader and "01.2.6" not in reader  # [D] only: run by code
    assert reader[0] == "12.2.2"


@pytest.mark.parametrize("role", list(Role))
def test_cards_are_capped_and_exclude_the_core(role: Role) -> None:
    triggers = list(TRIGGERS)  # every trigger at once
    extra = [c.id for c in INDEX if c.chapter == "06"][:30]
    cards = load_cards_for(role, ["situation.conflict.chase", "situation.social"], "conflict", triggers, extra,
                           rules=RULES)
    ids = [c.id for c in cards]
    assert len(ids) <= 12 and len(ids) == len(set(ids))
    assert not set(ids) & {c.id for c in INDEX.core()}
    assert ids == [c.id for c in load_cards_for(role, ["situation.conflict.chase", "situation.social"], "conflict",
                                                triggers, extra, rules=RULES)]


def test_priority_role_then_triggers_then_extra_then_situation() -> None:
    cards = [c.id for c in load_cards_for(Role.WORLD, ["situation.social"], None, ["trg.lead_injection"],
                                          ["06.5.10"], rules=RULES)]
    roles = [c.id for c in role_cards(Role.WORLD)]
    assert cards[: len(roles)] == roles
    assert cards[len(roles): len(roles) + 3] == ["12.8.2", "PR-12-3", "06.5.10"]
    rest = cards[len(roles) + 3:]
    assert rest and rest == [c.id for c in situation_cards(["situation.social"])][: len(rest)]


def test_checker_and_interpret_get_no_scene_cards() -> None:
    for role in (Role.CHECKER, Role.INTERPRET):
        ids = [c.id for c in load_cards_for(role, ["situation.conflict"], "conflict", ["trg.exits"], [], rules=RULES)]
        assert ids == [c.id for c in role_cards(role)]


def test_mode_loads_its_situation_cards() -> None:
    by_mode = load_cards_for(Role.NARRATOR, [], "conflict", [], [], rules=RULES)
    assert len(by_mode) > len(role_cards(Role.NARRATOR))
    assert len(load_cards_for(Role.NARRATOR, [], None, [], [], rules=RULES)) == len(role_cards(Role.NARRATOR))


def test_situation_cards_are_most_specific_first() -> None:
    cards = situation_cards(["situation.conflict.chase"])
    chase = [i for i, c in enumerate(cards) if "situation.conflict.chase" in c.tags]
    plain = [i for i, c in enumerate(cards) if "situation.conflict.chase" not in c.tags]
    assert chase and plain and max(chase) < min(plain)
    assert all(c.kind in ("rule", "procedure") for c in cards)


# ---------------------------------------------------------------- triggers


def test_trigger_registry_cards_exist() -> None:
    for t in TRIGGERS.values():
        assert t.cards and all(c in INDEX for c in t.cards), t.id


def test_active_triggers_come_from_flags_in_12_2_3_order(store: Store) -> None:
    with store.transaction("turn.2") as tx:
        tx.add(fact(tx, "world", "trg.pacing_push", True, kind="flag"))
        tx.add(fact(tx, "pc.wren", "trg.exits", {"cause": "staggered"}, kind="flag"))
        tx.add(fact(tx, "world", "trg.lead_injection", True, kind="flag"))
        tx.add(fact(tx, "world", "trg.11.flashpoint", False, kind="flag"))  # lowered
    active = get_active_triggers(store.state, RULES, raised=["trg.safety_flag", "trg.lead_injection"])
    assert [t.id for t in active] == ["trg.safety_flag", "trg.exits", "trg.lead_injection", "trg.pacing_push"]
    exits = active[1]
    assert exits.subject == "pc.wren" and exits.params == {"cause": "staggered"}
    assert "trg.exits on pc.wren" in exits.line()
    assert trigger_cards(active)[:2] == ["12.5.6", "07.3.7"]
    assert get_active_triggers(store.state) == get_active_triggers(store.rebuild())


# ---------------------------------------------------------------- scene slice


def test_scene_slice_is_bounded(store: Store) -> None:
    with store.transaction("turn.2") as tx:
        for i in range(MAX_SCENE_FACTS + 25):
            tx.add(fact(tx, "pc.wren", f"note_{i}", "x", visibility="shown"))
        tx.add(entity("npc", "Off Stage", tx=tx))
        tx.add(fact(tx, "npc.off_stage", "secret", "y", visibility="shown"))
    s = store.state
    assert scene_scope(s) == ["pc.wren", "npc.mara_voss", "loc.salt_harbor"]
    facts = scene_facts(s)
    assert len(facts) == MAX_SCENE_FACTS
    assert all(f.subject in scene_scope(s) for f in facts)
    assert facts[0].predicate == f"note_{MAX_SCENE_FACTS + 24}"  # newest first
