"""Contract tests for the per-role schemas (T027; contracts/model-calls.md).

Every builder's schema is well-formed JSON Schema in the engine's subset, has no numeric field except
`player_quantity` (INV-3), and the offline model's output (and each role's default) validates against it.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from typing import Any

import pytest

from engine.data.loader import load_rules
from engine.dm.packet import build_packet
from engine.dm.schemas import BUILDERS, build_schema, defaults, numeric_fields, schema_context
from engine.llm.base import Role, call_role, schema_hash, validate
from engine.llm.offline import OfflineModel
from engine.retrieve.anchors import anchor_candidates, anchor_menu
from engine.retrieve.cards import anchor_card_ids, load_cards_for
from engine.retrieve.triggers import get_active_triggers
from engine.store.db import Store
from engine.store.events import Event, PauseRecord
from engine.store.projection import WorldState
from tests.fixtures.game import entity, new_store

RULES = load_rules()
BEAT = {"verb": "verb.talk", "intent_verbs": ["persuade"], "intent": "I persuade Mara Voss to talk",
        "method": "offer coin"}
MESSAGES = {
    Role.INTERPRET: "2",
    Role.READER: 'I climb onto the crates and ask Mara Voss where the boat went? "Talk," I say. I offer 5 coins.',
    Role.FRAMER: "I persuade Mara Voss to talk.",
    Role.WORLD: "I persuade Mara Voss to talk.",
    Role.DIRECTOR: "Let's go to the harbor.",
    Role.NARRATOR: "success_at_cost",
    Role.CHECKER: "Mara Voss draws a knife. She smiles at you. What do you do?",
    Role.TESTIMONY: "npc.mara_voss: Mara Voss said: \"The night boat leaves from the north pier.\"",
    Role.FIXER: "THE PLAYER'S REPORT: \"Mara's coat was grey\"\nPEOPLE IN VIEW:\nnpc.mara_voss: Mara Voss (she/her)\n"
                "INVESTIGATION SO FAR:\n[1] search('coat'):\nturn.3 (1/1 words) player: \"hi\" | Mara's blue coat.",
    Role.CLUE: "THE QUESTION: \"Did he have enemies?\"\nOPEN CLUES (number: what a question must be about to reach it; "
               "* = this person holds it):\n1*: who had cause to want the ferryman gone",
}

# The engine's JSON Schema subset (engine.llm.base.validate) plus annotation keywords.
KEYWORDS = {"type", "enum", "const", "properties", "required", "additionalProperties", "items", "minItems",
            "maxItems", "minLength", "maxLength", "minimum", "maximum", "anyOf", "oneOf", "allOf", "$ref", "$defs",
            "title", "description"}
TYPES = {"object", "array", "string", "boolean", "null", "integer", "number"}


def fact(tx, subject: str, predicate: str, value, **kw) -> Event:
    return Event.of("fact_set", {"source": "narration"}, fact_id=tx.mint("fact"), subject=subject,
                    predicate=predicate, value=value, supersedes=tx.state.current_fact_id(subject, predicate),
                    visibility="shown", **kw)


@pytest.fixture(scope="module")
def store(tmp_path_factory: pytest.TempPathFactory) -> Iterator[Store]:
    s = new_store(tmp_path_factory.mktemp("schemas"))
    with s.transaction("turn.1") as tx:
        tx.add(entity("pc", "Wren", tx=tx, quantities={"vitality": (10, 0, 10)}))
        tx.add(Event.of("license_granted", entity="pc.wren", license={"license_id": "lic.training.martial_blade"}))
        tx.add(entity("place", "Salt Harbor", tx=tx))
        tx.add(entity("place", "Old Mill", tx=tx))
        tx.add(entity("thread", "The Sunken Boat", tx=tx))
        tx.add(entity("npc", "Mara Voss", tx=tx, sealed={
            "wants": [{"text": "pay off her debt", "rank": 1}, {"text": "leave town", "rank": 2}],
            "refusals": [{"kind": "refusal.self", "text": "will not betray her brother"}]}))
        tx.add(entity("npc", "Tam Harlan", tx=tx))
        tx.add(fact(tx, "npc.mara_voss", "attitude", "wary"))
        tx.add(fact(tx, "loc.salt_harbor", "crates", "stacked high on the quay"))
        tx.add(fact(tx, "world", "trg.lead_injection", True, kind="flag"))
        sid = tx.mint("scn")
        tx.add(Event.of("scene_started", scene_id=sid, scene={
            "scene_id": sid, "place_id": "loc.salt_harbor", "cast_present": ["npc.mara_voss"], "mode": "free",
            "agenda": "find the boat", "situation_tags": ["situation.social"]}))
        tx.add(Event.of("pause_opened", pause=PauseRecord(
            pause_id=tx.mint("pause"), kind="offer", prompt="Roll?",
            choices=[{"id": "commit", "label": "Do it"}, {"id": "decline", "label": "Back off"}])))
    yield s
    s.close()


def ctx_for(state: WorldState, role: Role, **kw: Any):
    anchors = anchor_candidates(BEAT, state, RULES)
    return schema_context(state, RULES, message=MESSAGES[role], options=["seed.premise.a", "seed.premise.b"],
                          own_words_classes=["premise", "other"], lines_and_veils=True, anchors=anchors, beat=BEAT,
                          push_raised=True, lead_fires=True,
                          draft_sentences=["Mara Voss draws a knife.", "She smiles at you.", "What do you do?"], **kw)


def packet_for(state: WorldState, role: Role):
    trig = get_active_triggers(state, RULES)
    anchors = anchor_candidates(BEAT, state, RULES) if role is Role.FRAMER else []
    cards = load_cards_for(role, ["situation.social"], "free", trig, anchor_card_ids(anchors, RULES), rules=RULES)
    return build_packet(role, instructions=f"You are the {role.value}.", cards=cards, view=state,
                        exchanges=[], message=MESSAGES[role], triggers=trig, notes=anchor_menu(anchors, RULES),
                        quiet_turns=1, rules=RULES)


def structural_errors(node: Any, path: str = "$") -> list[str]:
    """Well-formedness in the subset: known keywords, known types, closed objects, non-empty unique enums."""
    errs: list[str] = []
    if not isinstance(node, Mapping):
        return [f"{path}: not an object"]
    errs += [f"{path}: unknown keyword {k}" for k in node if k not in KEYWORDS]
    t = node.get("type")
    types = t if isinstance(t, list) else [t] if t is not None else []
    errs += [f"{path}: bad type {x}" for x in types if x not in TYPES]
    if not types and not any(k in node for k in ("enum", "const", "anyOf", "oneOf", "allOf", "$ref")):
        errs.append(f"{path}: no type")
    if "enum" in node:
        vals = node["enum"]
        if not vals or len(vals) != len({repr(v) for v in vals}):
            errs.append(f"{path}: empty or repeated enum")
        for v in vals:
            if v is None and "null" not in types:
                errs.append(f"{path}: null in enum but not in type")
            elif v is not None and not isinstance(v, str):
                errs.append(f"{path}: non-string enum value {v!r}")
    if "object" in types:
        props = node.get("properties", {})
        if node.get("additionalProperties") is not False:
            errs.append(f"{path}: object not closed")
        if set(node.get("required", [])) != set(props):
            errs.append(f"{path}: required differs from properties")
        for k, sub in props.items():
            errs += structural_errors(sub, f"{path}.{k}")
    if "array" in types:
        if "items" not in node:
            errs.append(f"{path}: array without items")
        else:
            errs += structural_errors(node["items"], f"{path}[]")
    for key in ("anyOf", "oneOf", "allOf"):
        for i, sub in enumerate(node.get(key, [])):
            errs += structural_errors(sub, f"{path}<{key}{i}>")
    return errs


@pytest.mark.parametrize("role", list(Role))
def test_schema_is_well_formed_and_has_no_numeric_field(store: Store, role: Role) -> None:
    schema = build_schema(role, ctx_for(store.state, role))
    assert structural_errors(schema) == []
    assert validate({}, schema)  # a real constraint: the empty object is refused
    assert numeric_fields(schema) == []
    if role is Role.READER:
        assert schema["properties"]["player_quantity"] == {"type": ["integer", "null"]}
    else:
        assert "player_quantity" not in str(schema)


@pytest.mark.parametrize("role", list(Role))
def test_offline_output_and_defaults_validate(store: Store, role: Role) -> None:
    ctx = ctx_for(store.state, role)
    schema = build_schema(role, ctx)
    data = OfflineModel().fill(role, schema, packet_for(store.state, role), turn_id="turn.9", attempt=1).data
    assert validate(data, schema) == []
    default = defaults(role, ctx)
    if role in (Role.NARRATOR, Role.CHECKER):
        assert default is None
    else:
        assert default is not None and validate(default, schema) == []


@pytest.mark.parametrize("role", list(Role))
def test_schemas_are_deterministic(store: Store, role: Role) -> None:
    a = build_schema(role, ctx_for(store.state, role))
    b = build_schema(role, ctx_for(store.rebuild(), role))
    assert schema_hash(a) == schema_hash(b)


def test_enums_come_from_rules_and_state(store: Store) -> None:
    s = store.state
    reader = build_schema(Role.READER, ctx_for(s, Role.READER))["properties"]
    beat = reader["beats"]["items"]["properties"]
    assert reader["beats"]["maxItems"] == 3
    assert beat["target"]["enum"] == ["none", "pc.wren", "npc.mara_voss", "loc.salt_harbor"]
    assert "license" not in beat and "gate" not in beat and "necessity" not in beat  # computed (00.12.3, 01.4.1)
    assert set(beat) >= {"against_will", "uses_power", "speech", "shape"}  # 12.2.2 decision 3 (DL-12-50)
    assert len(beat["verb"]["enum"]) == 15
    assert reader["pending_answer"]["enum"] == ["commit", "decline", None]
    assert reader["fact_questions"]["items"]["properties"]["odds_rung"]["enum"][0] == "certain"
    assert set(beat["g4_fact"]["enum"]) == {"fact.1", "fact.2", None}  # scene facts; no trigger flag

    framer = build_schema(Role.FRAMER, ctx_for(s, Role.FRAMER))["properties"]
    assert framer["anchor"]["enum"][0] == "anc.01_18_7"  # Talk: the basic verb's anchor first
    assert "presence" in framer["attribute"]["enum"]
    assert "deed.influence" in framer["deed_tag"]["enum"] and "deed" in framer["deed_tag"]["enum"]
    stakes = framer["stakes"]["properties"]
    assert stakes["source"]["enum"][0] == "none"
    assert "cost.shortfall" not in stakes["threatened_cost"]["properties"]["menu_id"]["enum"]
    assert framer["levers"]["maxItems"] == 2 and framer["deltas"]["maxItems"] == 2

    world = build_schema(Role.WORLD, ctx_for(s, Role.WORLD))["properties"]["responses"]["items"]["properties"]
    assert world["npc"]["enum"] == ["npc.mara_voss"]
    assert world["want_engaged"]["enum"] == ["none", "npc.mara_voss/want.1", "npc.mara_voss/want.2"]
    assert world["refusal_engaged"]["enum"] == ["none", "npc.mara_voss/refusal.1"]

    director = build_schema(Role.DIRECTOR, ctx_for(s, Role.DIRECTOR))["properties"]
    nxt = director["next_scene"]["properties"]
    assert set(nxt["mode"]["enum"]) == {"conflict", "site", "free", "travel", "downtime"}
    assert nxt["place"]["enum"] == ["loc.salt_harbor", "loc.old_mill"]
    assert nxt["cast"]["items"]["enum"] == ["npc.mara_voss", "npc.tam_harlan", "new_npc"]
    assert director["push"]["enum"][0] == "none"
    assert director["lead"]["anyOf"][0]["properties"]["thread"]["enum"] == ["thr.the_sunken_boat"]

    checker = build_schema(Role.CHECKER, ctx_for(s, Role.CHECKER))["properties"]
    claim = checker["claims"]["items"]["properties"]
    assert claim["sentence"]["enum"] == ["0", "1", "2"]
    assert claim["subject"]["enum"][-1] == "unknown"
    assert "safety_spans" not in checker["screen"]["properties"]  # safety is separate (FR-036)
    assert set(checker["screen"]["properties"]) == {"intent_acknowledged", "intent_substituted", "next_step_exists",
                                                     "mechanics_in_fiction", "ends_on_prompt_or_one_pause"}


def test_pending_answer_is_offered_only_with_an_open_pause(store: Store, tmp_path: Any) -> None:
    """12.2.2: PENDING_ANSWER answers a pause point. With none open the `pending_answer` field is dropped, so the
    class was unsatisfiable (reader_check needs the field): the playtest Reader re-asked and defaulted."""
    def classes(props: dict[str, Any]) -> list[str]:
        return props["parts"]["items"]["properties"]["class"]["enum"]

    with_pause = build_schema(Role.READER, ctx_for(store.state, Role.READER))["properties"]
    assert "PENDING_ANSWER" in classes(with_pause) and "pending_answer" in with_pause
    s = new_store(tmp_path)
    try:
        none_open = build_schema(Role.READER, schema_context(s.state, RULES, message="Stay a while."))["properties"]
    finally:
        s.close()
    assert "PENDING_ANSWER" not in classes(none_open) and "pending_answer" not in none_open
    assert "DECLARATION" in classes(none_open)


def test_empty_enum_drops_the_field(store: Store) -> None:
    s = store.state
    ctx = schema_context(s, RULES, anchors=[])  # no anchors, no push, no lead, no options, no draft
    framer = build_schema(Role.FRAMER, ctx)["properties"]
    assert "anchor" not in framer and "deltas" not in framer and "attribute" not in framer
    director = build_schema(Role.DIRECTOR, ctx)["properties"]
    assert "push" not in director and "lead" not in director
    interpret = build_schema(Role.INTERPRET, ctx)
    assert "lines_and_veils" not in interpret["properties"]
    assert "own_words_class" not in interpret["properties"]
    checker = build_schema(Role.CHECKER, ctx)["properties"]["claims"]["items"]
    assert "sentence" not in checker["properties"] and "sentence" not in checker["required"]
    for role in BUILDERS:
        d = defaults(role, ctx)
        assert d is None or validate(d, build_schema(role, ctx)) == []


def test_framer_attribute_enum_follows_01_6_1_without_a_knob(store: Store) -> None:
    """Most anchors have no attribute knob: the enum comes from the verb (01.6.1), the licence, or opens up."""
    s = store.state

    def attrs(anchor: str, **beat: Any) -> tuple[list[str], str | None]:
        ctx = schema_context(s, RULES, anchors=[anchor], beat={"verb": None, "license": None, **beat})
        node = build_schema(Role.FRAMER, ctx)["properties"]["attribute"]
        d = defaults(Role.FRAMER, ctx)
        assert d is not None and validate(d, build_schema(Role.FRAMER, ctx)) == []
        return node["enum"], d["attribute"]

    assert attrs("anc.01_18_8") == (["might", "agility"], "might")  # Strike: verb attribute + alt, no knob
    assert attrs("anc.01_18_10") == (["might"], "might")  # Force: no alternative
    assert attrs("anc.01_18_4")[0] == ["agility", "might", "endurance"]  # Move: the knob default first
    assert set(attrs("anc.01_18_16")[0]) == set(RULES.attributes)  # Set up: by method
    assert set(attrs("anc.02_9_4")[0]) == set(RULES.attributes)  # no verb, no knob: the method decides
    assert attrs("anc.02_9_4", verb="verb.force") == (["might"], "might")  # ... else the beat's verb
    assert attrs("anc.02_9_4", license="lic.training.lore_history") == (["intellect"], "intellect")


def test_framer_costs_may_cite_a_scene_fact(store: Store) -> None:
    s = store.state
    framer = build_schema(Role.FRAMER, ctx_for(s, Role.FRAMER))["properties"]
    stakes = framer["stakes"]["properties"]
    src = stakes["threatened_cost"]["properties"]["source_fact"]
    assert src["type"] == ["string", "null"] and set(src["enum"]) == {"fact.1", "fact.2", None}
    assert stakes["alternate_cost"]["anyOf"][0]["properties"]["source_fact"] == src
    assert "source_fact" in stakes["threatened_cost"]["required"]
    d = defaults(Role.FRAMER, ctx_for(s, Role.FRAMER))
    assert d is not None and d["stakes"]["threatened_cost"]["source_fact"] is None
    bare = schema_context(s, RULES, anchors=["anc.01_18_7"], cost_menu_ids=["cost.twist"])
    bare.fact_ids = bare.lever_fact_ids = []
    bare_stakes = build_schema(Role.FRAMER, bare)["properties"]["stakes"]["properties"]
    assert "source_fact" not in bare_stakes["threatened_cost"]["properties"]


def branch(props: dict[str, Any], source: str) -> dict[str, Any]:
    """The Framer `stakes` branch whose `source` enum offers `source` (its properties)."""
    node = props["stakes"]
    return next(b["properties"] for b in node.get("anyOf", [node]) if source in b["properties"]["source"]["enum"])


def test_framer_stakes_pair_the_source_with_its_costs(tmp_path: Any) -> None:
    """Playtest 20261008 talker (and 44 refusals across the saves): the Framer wrote stakes `none` with cost.time,
    legal only through a listening clock, and an alternate exposure with no source. The source and its costs are
    one choice now, so an unpaired frame cannot be written."""
    from engine.resolve.types import Beat
    from engine.store.events import ClockRecord

    s = new_store(tmp_path)
    try:
        with s.transaction() as tx:
            tx.add(entity("pc", "Wren", tx=tx))
            tx.add(entity("place", "Salt Harbor", tx=tx))
            tx.add(Event.of("clock_created", source="test", clock=ClockRecord(
                id="clk.dusk", name="dusk", kind="danger", segments=4, tick_sources=[])))
            tx.add(fact(tx, "loc.salt_harbor", "crates", "stacked high on the quay"))
            sid = tx.mint("scn")
            tx.add(Event.of("scene_started", scene_id=sid, scene={
                "scene_id": sid, "place_id": "loc.salt_harbor", "cast_present": [], "mode": "free",
                "agenda": "find the boat"}))
        st = s.state
        pc = next(e for e, x in st.entities.items() if x.kind == "pc")
        beat = Beat(id="beat.1", actor=pc, intent="recall Fenwin", method="think back", verb="verb.recall",
                    target="none", declared_seq=st.last_seq)
        ctx = schema_context(st, RULES, anchors=["anc.01_18_6"], beat=beat)
        schema = build_schema(Role.FRAMER, ctx)
        p = schema["properties"]
        none, clock = branch(p, "none"), branch(p, "listening_clock")
        def uncited(cost: dict[str, Any]) -> list[str]:  # the menus offered without a source fact
            return [m for b in cost.get("anyOf", [cost]) if None in b["properties"]["source_fact"]["enum"]
                    for m in b["properties"]["menu_id"]["enum"]]

        assert "cost.time" not in uncited(none["threatened_cost"]) and "cost.time" in uncited(clock["threatened_cost"])
        assert clock["alternate_cost"].get("type") == "object" or "anyOf" in clock["alternate_cost"]  # Risky: required
        d = defaults(Role.FRAMER, ctx)
        assert d is not None and validate(d, schema) == []
        time = {"menu_id": "cost.time", "form_intent": "the light goes", "source_fact": None}
        assert validate({**d, "stakes": {"source": "none", "threatened_cost": time, "alternate_cost": None}}, schema)
        alt = {"menu_id": "cost.shortfall", "form_intent": "less of it", "source_fact": None}
        assert validate({**d, "stakes": {"source": "listening_clock", "threatened_cost": time,
                                         "alternate_cost": alt}}, schema) == []
        assert validate({**d, "stakes": {"source": "listening_clock", "threatened_cost": time,
                                         "alternate_cost": None}}, schema)
    finally:
        s.close()


def test_framer_offers_only_legal_choices(store: Store) -> None:
    """PR-01-2 steps 6, 7, 10 as enums: playtest Framers picked a no-roll tier, `opposed` without an entity,
    a lever established after the declaration, and costs with no source; none of those is offered now."""
    from engine.resolve.types import Beat

    s = store.state
    f1 = s.facts["fact.1"]
    beat = Beat(id="beat.1", actor="pc.wren", intent="persuade Mara", method="offer coin", verb="verb.talk",
                target="none", declared_seq=f1.valid_from_seq)
    schema = build_schema(Role.FRAMER, schema_context(s, RULES, anchors=anchor_candidates(BEAT, s, RULES),
                                                      beat=beat))
    p = schema["properties"]
    klass, tier, opposed = p["obstacle"]["anyOf"][:3]
    assert klass["properties"]["obstacle_class"]["enum"] == ["be_heard"]  # Talk's rubric class (01.6.5)
    assert tier["properties"]["obstacle_class"]["enum"] == ["other"]
    assert "trivial" not in tier["properties"]["tier"]["enum"] and "moderate" in tier["properties"]["tier"]["enum"]
    assert opposed["properties"]["entity"]["enum"] == ["npc.mara_voss"]
    keys = list(p)
    at = keys.index("obstacle")
    assert keys[at + 1:at + 4] == ["nudge_why", "nudge", "nudge_fact"]  # the why is written before the value
    later = [k for k, f in s.facts.items() if f.valid_from_seq > f1.valid_from_seq]
    assert later and not set(later) & set(p["levers"]["items"]["enum"])
    free, cited = branch(p, "none")["threatened_cost"]["anyOf"]
    # no clock runs: cost.time fits only with a cited source; Wren holds nothing, so twist is a candidate uncited;
    # harm follows from a hazard, never from no source (the pairing: 01.6.11)
    assert "cost.time" not in free["properties"]["menu_id"]["enum"] and "cost.twist" in free["properties"]["menu_id"][
        "enum"] and "cost.harm" not in free["properties"]["menu_id"]["enum"]
    hazard = branch(p, "hazard")["threatened_cost"]["anyOf"][0]["properties"]["menu_id"]["enum"]
    assert "cost.harm" in hazard and "cost.twist" not in hazard
    assert "cost.time" in cited["properties"]["menu_id"]["enum"] and "cost.twist" not in cited["properties"][
        "menu_id"]["enum"]
    assert all("listening_clock" not in b["properties"]["source"]["enum"] for b in p["stakes"]["anyOf"])
    assert None not in cited["properties"]["source_fact"]["enum"]
    d = defaults(Role.FRAMER, schema_context(s, RULES, anchors=anchor_candidates(BEAT, s, RULES), beat=beat))
    assert d is not None and validate(d, schema) == []
    for bad in ({"kind": "opposed", "obstacle_class": None, "tier": None, "entity": None},
                {"kind": "tier", "obstacle_class": "other", "tier": "trivial", "entity": None}):
        assert validate({**d, "obstacle": bad}, schema)
    time = {"menu_id": "cost.time", "form_intent": "", "source_fact": None}
    assert validate({**d, "stakes": {**d["stakes"], "threatened_cost": time}}, schema)


def test_defaults_follow_the_contract(store: Store) -> None:
    s = store.state
    reader = defaults(Role.READER, ctx_for(s, Role.READER))
    assert reader and reader["parts"] == [{"text": MESSAGES[Role.READER], "class": "DECLARATION",
                                           "question_kind": "none", "topic": None}]
    framer = defaults(Role.FRAMER, ctx_for(s, Role.FRAMER))
    assert framer and framer["anchor"] == "anc.01_18_7" and framer["attribute"] == "presence"
    # lane D P2: the default is class `other` at Easy (the Moderate default is retired)
    assert framer["stakes"]["source"] == "none" and framer["obstacle"] == {"kind": "tier", "obstacle_class": "other",
                                                                         "tier": "easy", "entity": None}
    director = defaults(Role.DIRECTOR, ctx_for(s, Role.DIRECTOR))
    assert director and director["next_scene"]["mode"] == "free" and director["push"] == "none"
    assert defaults(Role.INTERPRET, ctx_for(s, Role.INTERPRET))["choice"] == "move_on"  # type: ignore[index]


def test_call_role_end_to_end_with_offline_model(store: Store) -> None:
    s = store.state
    ctx = ctx_for(s, Role.READER)
    schema = build_schema(Role.READER, ctx)
    result = call_role(OfflineModel(), Role.READER, schema, packet_for(s, Role.READER), turn_id="turn.9",
                       default=defaults(Role.READER, ctx))
    assert not result.defaulted
    classes = [p["class"] for p in result.data["parts"]]
    assert "FICTION_QUESTION" in classes and "SPEECH" in classes
    assert result.data["player_quantity"] == 5
    assert result.data["beats"][0]["target"] == "none" or result.data["beats"][0]["target"] in ctx.scene_ids
