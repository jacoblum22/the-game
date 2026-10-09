"""Retrieval caps and determinism (T020): anchors (≤8), cards (≤12; guidance digests, spec 020), active triggers."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest

from engine.build.compile_cards import load_cards
from engine.data.loader import load_rules
from engine.llm.base import Role
from engine.retrieve.anchors import anchor_candidates, anchor_menu, natural_key, verb_anchor
from engine.retrieve.cards import GUIDANCE, guidance_digest, load_cards_for
from engine.retrieve.scene import _line_tokens, focus_ids, scene_facts, scene_scope, view_budget
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


def test_a_talk_beat_never_re_anchors_to_force(store: Store) -> None:
    """P-023/P-064: the Framer picks among candidates, so a Talk beat's candidates hold no Strike/Handle anchor."""
    beat = {"verb": "verb.talk", "intent_verbs": ["make", "force", "wound", "turn", "use"],
            "intent": "they give their names", "method": "shout at them to stop"}
    verbs = {RULES.anchors[a].get("verb") for a in anchor_candidates(beat, store.state, RULES)}
    assert verbs <= {None, "verb.talk", "verb.setup", "verb.sneak"}, verbs
    strike = anchor_candidates({**beat, "verb": "verb.strike"}, store.state, RULES)
    assert "verb.talk" not in {RULES.anchors[a].get("verb") for a in strike}


def test_situation_alone_does_not_make_a_candidate(store: Store) -> None:
    cands = anchor_candidates({"verb": None, "intent_verbs": [], "intent": ""}, store.state, RULES)
    assert cands == []


def test_natural_key_orders_rule_ids() -> None:
    assert sorted(["01.6.10", "01.6.9", "T-06-10", "T-06-9"], key=natural_key) == \
        ["01.6.9", "01.6.10", "T-06-9", "T-06-10"]


# ---------------------------------------------------------------- cards


def test_guidance_ids_exist_and_digests_are_short_and_stable() -> None:
    """12.2.4 item 1 (spec 020): each role's guidance is generated from its cards' J blocks, identical per call."""
    for role, ids in GUIDANCE.items():
        assert all(i in INDEX for i in ids), role
    reader = guidance_digest(Role.READER)
    assert "one beat per goal" in reader and "Verb covers" in reader and "persuade_to (person, act)" in reader
    assert "[revision:" not in reader and "*Retires:*" not in reader  # history, not guidance
    assert guidance_digest(Role.READER) is guidance_digest(Role.READER)  # cached: the cacheable prefix
    framer = guidance_digest(Role.FRAMER)
    assert "Decisions (J):" in framer and "Computation [D]:" not in framer  # the judgment, not code's arithmetic
    assert "T-12-7" in guidance_digest(Role.DIRECTOR) and "COVERS" in guidance_digest(Role.WORLD)
    assert guidance_digest(Role.TESTIMONY) == ""
    core = "\n".join(c.body for c in INDEX.core())
    assert all(len(guidance_digest(r)) < len(core) * 2 for r in GUIDANCE)


@pytest.mark.parametrize("role", list(Role))
def test_cards_are_capped_and_exclude_the_core(role: Role) -> None:
    triggers = list(TRIGGERS)  # every trigger at once
    extra = [c.id for c in INDEX if c.chapter == "06"][:30]
    cards = load_cards_for(role, triggers=triggers, extra_ids=extra, rules=RULES)
    ids = [c.id for c in cards]
    assert len(ids) <= 12 and len(ids) == len(set(ids))
    assert not set(ids) & {c.id for c in INDEX.core()}
    assert ids == [c.id for c in load_cards_for(role, triggers=triggers, extra_ids=extra, rules=RULES)]


def test_only_cards_code_knows_apply_triggers_then_extra() -> None:
    """12.2.4 item 2 (DL-12-104): no role cards and no situation cards by tag; the fired triggers' cards, then the
    extra ids, stable to volatile (DL-12-38)."""
    cards = [c.id for c in load_cards_for(Role.WORLD, ["situation.social"], "free", ["trg.lead_injection"],
                                          ["06.5.10"], rules=RULES)]
    assert cards == ["12.8.2", "PR-12-3", "06.5.10"]
    assert load_cards_for(Role.NARRATOR, ["situation.social"], "conflict", [], [], rules=RULES) == []


def test_checker_and_interpret_get_no_trigger_cards() -> None:
    for role in (Role.CHECKER, Role.INTERPRET):
        assert load_cards_for(role, triggers=["trg.exits"], rules=RULES) == []


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
    budget = view_budget(RULES)
    with store.transaction("turn.2") as tx:
        for i in range(100):
            tx.add(fact(tx, "pc.wren", f"note_{i}", "x", visibility="shown"))
        tx.add(entity("npc", "Off Stage", tx=tx))
        tx.add(fact(tx, "npc.off_stage", "secret", "y", visibility="shown"))
    s = store.state
    assert scene_scope(s) == ["pc.wren", "npc.mara_voss", "loc.salt_harbor"]
    facts = scene_facts(s)
    assert 10 < len(facts) < 100 and sum(_line_tokens(f) for f in facts) <= budget["facts"]  # tokens, not items
    assert all(f.subject in scene_scope(s) for f in facts)
    assert facts[0].predicate == "note_99"  # equal scores: newest first


def test_scene_facts_pins_and_ranking(store: Store) -> None:
    """12.2.4 item 3: pins are never ranked out; archived memories never shown (12.11.7); relevance and
    adjacency lift a fact; recency steps per scene, not per turn."""
    with store.transaction("turn.2") as tx:
        tx.add(entity("npc", "Tam Harlan", tx=tx))  # off stage
        tx.add(fact(tx, "npc.mara_voss", "memory.1", {"deed": "Wren lied", "salience": 2, "status": "archived"}))
        tx.add(fact(tx, "npc.mara_voss", "memory.2", {"deed": "Wren paid", "salience": 1, "status": "active"}))
        tx.add(fact(tx, "npc.tam_harlan", "commitment.x", {"npc": "npc.tam_harlan", "status": "open"},
                    kind="commitment"))
        tx.add(fact(tx, "npc.mara_voss", "commitment.y", {"npc": "npc.mara_voss", "status": "kept"},
                    kind="commitment"))
        tx.add(fact(tx, "npc.mara_voss", "mood", "sour"))
        tx.add(fact(tx, "pc.wren", "owes", "npc.mara_voss"))
        for i in range(100):  # newer filler that would crowd out a newest-first list
            tx.add(fact(tx, "pc.wren", f"note_{i}", "x"))
    s = store.state
    preds = [f.predicate for f in scene_facts(s)]
    assert preds[:2] == ["commitment.x", "memory.2"]  # pins first: the open commitment of an absent NPC too
    assert "memory.1" not in preds  # archived (12.11.7)
    assert preds[2] == "commitment.y" and preds[3] == "owes"  # salience 3; then adjacency (+1, names Mara)
    focused = [f.predicate for f in scene_facts(s, focus=focus_ids(s, "I ask Mara Voss about it"))]
    assert focused[2:5] == ["commitment.y", "owes", "mood"]  # relevance +2 for facts about or naming Mara
    assert focus_ids(s, "", "npc.tam_harlan") == ["npc.tam_harlan"]
