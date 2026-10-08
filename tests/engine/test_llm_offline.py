"""engine/llm/offline.py: the offline stand-in returns schema-valid output for every role, and ScriptedModel."""

from __future__ import annotations

import random
from typing import Any

import pytest

from engine.llm.base import Packet, Role, call_role, validate
from engine.llm.offline import (
    QUIET_TURNS_TO_CUT,
    OfflineModel,
    ScriptedModel,
    ScriptExhausted,
    conform,
    match_verb,
    sentences,
    verb_keywords,
)

# ---- schema builders shaped like contracts/model-calls.md (as T026 would emit them)


def enum(*vals: str) -> dict[str, Any]:
    return {"type": "string", "enum": list(vals)}


def nullable(node: dict[str, Any]) -> dict[str, Any]:
    return {"anyOf": [node, {"type": "null"}]}


def arr(items: dict[str, Any], max_items: int | None = None) -> dict[str, Any]:
    node: dict[str, Any] = {"type": "array", "items": items}
    if max_items is not None:
        node["maxItems"] = max_items
    return node


def obj(**props: dict[str, Any]) -> dict[str, Any]:
    return {"type": "object", "properties": props, "required": list(props), "additionalProperties": False}


STR = {"type": "string"}
BOOL = {"type": "boolean"}
VERBS = sorted(verb_keywords())
SCENE = ["npc.mara_voss", "npc.gate_guard", "place.salt_market"]
VIEW = "Scene at the Salt Market.\nPresent:\n- npc.mara_voss: Mara Voss, the fence\n- npc.gate_guard: name: Old Tam"

INTERPRET = obj(
    choice=enum("seed.mode.random", "seed.mode.guided", "seed.mode.custom", "own_words", "move_on", "details",
                "suggest"),
    own_words_class=nullable(enum("tone", "place", "people")),
    own_words_text=nullable(STR),
    lines_and_veils=arr(STR),
)
BEAT = obj(  # 12.2.2 decision 3 (DL-12-50): no gate, licence or necessity
    intent=STR, method=STR, assertion=nullable(STR), shape=enum("now", "extended", "queued", "conditional"),
    target=enum(*SCENE, "none"), verb=enum(*VERBS), against_will=BOOL, uses_power=BOOL, speech=BOOL,
    g4_fact=nullable(enum("fact.f1", "fact.f2")), intent_verbs=arr(STR),
)
READER = {
    **obj(
        parts=arr(obj(text=STR, **{"class": enum("SAFETY", "SESSION", "DISPUTE", "PENDING_ANSWER", "OOF_QUESTION",
                                               "FICTION_QUESTION", "DECLARATION", "SPEECH")},
                      question_kind=enum("none", "who_is", "where_is", "what_happened", "what_like", "what_want",
                                         "who_knows"), topic=nullable(STR))),
        pending_answer=nullable(enum("commit", "withdraw")),
        fact_questions=arr(obj(subject=enum(*SCENE), predicate=STR,
                               odds_rung=enum("certain", "likely", "even", "unlikely", "impossible"))),
        beats=arr({"$ref": "#/$defs/Beat"}, 3),
        clarifying_question=nullable(STR),
        restatement=STR,
    ),
    "$defs": {"Beat": BEAT},
}
COST = obj(menu_id=enum("cost.harm", "cost.gear", "cost.position"), form_intent=STR)
FRAMER = obj(
    anchor=enum("anchor.verb.strike", "anchor.verb.observe", "anchor.feint"),
    deltas=arr(obj(knob=enum("dc", "attribute"), delta=enum("opposed"), cites_fact=enum("fact.f1")), 2),
    attribute=enum("might", "agility", "wits"),
    deed_tag=enum("tag.combat", "tag.combat.melee"),
    traits=arr(enum("trait.action.strike")),
    obstacle=obj(kind=enum("tier", "opposed", "entity_defense"), tier=nullable(enum("easy", "standard", "hard")),
                 entity=nullable(enum("npc.gate_guard"))),
    levers=arr(enum("fact.f1", "fact.f2"), 2), snags=arr(enum("fact.f1", "fact.f2"), 2),
    stakes_source=enum("source.harm", "source.loss", "none"),
    stakes_heavy=BOOL, lethal=BOOL, reach_whole=BOOL, reach_one_factor=BOOL,
    threatened_cost=COST, alternate_cost=nullable(COST),
    method_consequences=arr(STR), secret=BOOL,
)
WORLD = obj(responses=arr(obj(
    npc=enum("npc.mara_voss", "npc.gate_guard"), want_engaged=enum("want.coin", "none"),
    refusal_engaged=enum("refusal.no_violence", "none"), table_context=obj(tags=arr(enum("tag.greedy", "tag.wary"))),
)))
DIRECTOR = obj(
    cut_now=BOOL,
    next_scene=obj(mode=enum("conflict", "site", "free", "travel", "downtime"),
                   place=enum("place.salt_market", "place.docks"), agenda=STR, hoped_answer=STR,
                   pillar=enum("pillar.combat", "pillar.social"), challenge_type=enum("ct.chase", "ct.puzzle"),
                   cast=arr(enum(*SCENE, "new_npc"))),
    push=enum("push.complication", "none"),
    lead=nullable(obj(thread=enum("thread.t1"), via=enum("via.rumor", "via.clue"))),
)
NARRATOR = obj(fiction=STR, mentions=arr(obj(kind=enum("npc", "item", "place"), name=STR,
                                             implied=arr(obj(predicate=STR, value=STR)), unsettled=arr(STR))))
CHECKER = obj(
    claims=arr(obj(
        sentence={"type": "integer"}, subject=enum(*SCENE, "unknown"),
        **{"class": enum("existence", "identity", "quantity", "harm_condition", "position", "possession",
                         "location_time", "knowledge", "capability", "clock", "attitude", "outcome", "action",
                         "sealed")},
        predicate=STR, value=STR, asserts_change=BOOL, pc_words_or_feelings=BOOL,
    )),
    screen=obj(intent_acknowledged=BOOL, intent_substituted=BOOL, next_step_exists=BOOL,
               mechanics_in_fiction=arr(STR), ends_on_prompt_or_one_pause=BOOL),
)
SCHEMAS = {Role.INTERPRET: INTERPRET, Role.READER: READER, Role.FRAMER: FRAMER, Role.WORLD: WORLD,
           Role.DIRECTOR: DIRECTOR, Role.NARRATOR: NARRATOR, Role.CHECKER: CHECKER}

MODEL = OfflineModel()


def fill(role: Role, message: str = "", view: str = VIEW, **kw: Any) -> dict[str, Any]:
    res = MODEL.fill(role, SCHEMAS[role], Packet(message=message, view=view, **kw), turn_id="t1", attempt=0)
    assert validate(res.data, SCHEMAS[role]) == [], (role, res.data)
    assert res.record.provider == "offline" and res.record.cost_usd == 0
    return res.data


MESSAGES = [
    "", "skip", "2", "I attack the gate guard with my knife.", 'I tell Mara "Hand it over." Is she armed?',
    "How does the roll work?", "I climb the wall. I look around. I pick the lock. I run.", "random please",
    "The guard draws a sword. Mara Voss is bleeding at the gate. You feel afraid. Roll 3d6!",
    "commit", "success_at_cost", "quiet_turns: 5", "?!?", "\n\n", "I give 3 coins to Tam.",
]


@pytest.mark.parametrize("role", list(Role))
def test_every_role_is_schema_valid_for_any_message(role: Role) -> None:
    for msg in MESSAGES:
        fill(role, msg)
        fill(role, msg, view="")


def test_fuzz_conform_random_values_always_valid() -> None:
    rng = random.Random(4)
    junk: list[Any] = [None, 1, "x", True, [], {}, [1, "a"], {"a": 1}, 2.5, "none"]
    for schema in SCHEMAS.values():
        for _ in range(200):
            v = rng.choice(junk)
            assert validate(conform(v, schema, schema), schema) == []


def test_empty_enum_field_dropped_schema_still_valid() -> None:
    schema = obj(cut_now=BOOL, push=enum("none"))
    res = MODEL.fill(Role.DIRECTOR, schema, Packet(), turn_id=None, attempt=0)
    assert validate(res.data, schema) == []


def test_interpret_maps_numbers_words_and_skip() -> None:
    assert fill(Role.INTERPRET, "2")["choice"] == "seed.mode.guided"
    assert fill(Role.INTERPRET, "I'd like custom")["choice"] == "seed.mode.custom"
    assert fill(Role.INTERPRET, "")["choice"] == "move_on"
    assert fill(Role.INTERPRET, "skip")["choice"] == "move_on"
    assert fill(Role.INTERPRET, "surprise me")["choice"] == "suggest"
    out = fill(Role.INTERPRET, "A drowned city of bells")
    assert out["choice"] == "own_words" and out["own_words_text"] == "A drowned city of bells"


def test_reader_classifies_and_gates() -> None:
    out = fill(Role.READER, 'I tell Mara "Hand it over." Is Mara armed? How do rules for rolls work?')
    classes = [p["class"] for p in out["parts"]]
    assert classes == ["SPEECH", "FICTION_QUESTION", "OOF_QUESTION"]
    assert out["fact_questions"][0]["subject"] == "npc.mara_voss"
    assert out["fact_questions"][0]["odds_rung"] == "even"

    held = VIEW + "\nHeld licences: lic.lockpicking: pick the lock, open locks"
    out = fill(Role.READER, "I attack the gate guard. I look around. I pick the lock. I sing.", view=held)
    assert len(out["beats"]) == 3  # 01.2.3
    attack, look, lock = out["beats"]
    # 12.2.2 decision 3: verb, target and facets only; the gate and the roll test are computed (00.12.3, 01.4.1)
    assert attack["verb"] == "verb.strike" and attack["against_will"] and attack["target"] == "npc.gate_guard"
    assert look["verb"] == "verb.observe" and not look["against_will"] and "gate" not in look
    assert lock["verb"] == "verb.force" and "license" not in lock  # Force's excludes name lockpicking
    assert out["restatement"].startswith("You attack")


def test_reader_pending_answer() -> None:
    out = fill(Role.READER, "commit")
    assert out["pending_answer"] == "commit" and out["parts"][0]["class"] == "PENDING_ANSWER"


def test_reader_unknown_act_defaults_to_g3() -> None:
    out = fill(Role.READER, "I transmute it into gold with a spell.")
    assert out["beats"][0]["uses_power"]  # the computed gate redirects it (G3) unless a technique is held


def test_verb_table_covers_fifteen_basic_verbs() -> None:
    assert len(VERBS) == 15
    assert match_verb("I shove the cart into the doorway") == ("verb.force", ["shove"])


def test_framer_defaults() -> None:
    out = fill(Role.FRAMER, "beat: verb.strike at the guard")
    assert out["anchor"] == "anchor.verb.strike" and out["attribute"] == "might"
    assert out["obstacle"]["tier"] == "standard"
    assert out["stakes_source"] == "source.harm" and out["threatened_cost"]["menu_id"] == "cost.harm"
    assert out["alternate_cost"]["menu_id"] == "cost.gear"


def test_world_answers_only_the_npcs_engaged() -> None:
    # 12.2.9: an NPC responds to what this turn's acts engage; a look around engages no one
    assert fill(Role.WORLD, "player: I look around. (DECLARATION)\nbeat: You look around -> no roll")["responses"] == []
    named = fill(Role.WORLD, "player: I wave at Old Tam. (DECLARATION)\nbeat: You wave at Old Tam -> no roll")
    assert [r["npc"] for r in named["responses"]] == ["npc.gate_guard"]
    spoke = fill(Role.WORLD, 'player: "Evening." (SPEECH)')
    assert [r["npc"] for r in spoke["responses"]] == ["npc.mara_voss"]
    assert all(r["table_context"]["tags"] == [] for r in spoke["responses"])  # no 'threat' tag unless earned


def test_director_cuts_after_quiet_turns() -> None:
    assert fill(Role.DIRECTOR, view=f"quiet_turns: {QUIET_TURNS_TO_CUT}")["cut_now"] is True
    out = fill(Role.DIRECTOR, view="quiet_turns: 1")
    assert out["cut_now"] is False and out["next_scene"]["mode"] == "free" and out["push"] == "none"
    assert fill(Role.DIRECTOR, view="")["cut_now"] is False


RECORD = ("Narrate this turn from the record.\nADJUDICATION RECORD (narrate exactly this, no better and no worse):\n"
          '- part [DECLARATION] "I climb the wall."\n- part [SPEECH] "\\"Hold the rope, Mara.\\""\n'
          "- beat: You climb the wall; approach: Exert; result: success at cost (it works, and the cost is paid)\n"
          "- end by handing the moment back (12.14.9)")


def test_director_cuts_to_the_named_reachable_place() -> None:
    places = "PLACES (here first, then reachable):\n- place.salt_market: the Salt Market\n- place.docks: the docks\n"
    out = fill(Role.DIRECTOR, places + 'THE PLAYER\'S MESSAGE: "I head down to the docks."', view="")
    assert out["cut_now"] is True and out["next_scene"]["place"] == "place.docks"
    assert out["next_scene"]["cast"] == ["new_npc"]  # someone to meet there
    stay = fill(Role.DIRECTOR, places + 'THE PLAYER\'S MESSAGE: "I look at the docks."', view="")
    assert stay["cut_now"] is False


def test_narrator_words_the_record_and_uses_only_view_names() -> None:
    out = fill(Role.NARRATOR, RECORD + "\nroll 14 vs 12", view="npc.mara_voss: Mara Voss\n  name: Mara Voss")
    fiction = out["fiction"]
    assert fiction.startswith("You climb the wall. It works, but not cleanly.")
    assert "Mara Voss hears you out" in fiction  # speech gets a reply from a present NPC, by name
    assert not any(ch.isdigit() for ch in fiction) and fiction.endswith("?") and out["mentions"] == []
    bare = fill(Role.NARRATOR, "anything", view="")["fiction"]
    assert "Mara" not in bare and not any(ch.isdigit() for ch in bare)
    # a question gets an answer-shaped line; a roll-less beat never claims a degree
    q = fill(Role.NARRATOR, '- question "Is the gate barred?": the answer is no\n'
                            "- beat: You wait by the door; no roll: no roll: trivial")["fiction"]
    assert "No, it is not so." in q and "better than" not in q and "You wait by the door." in q
    look = fill(Role.NARRATOR, "- beat: You look around; no roll: no roll: trivial",
                view="scene: scn.1 at loc.dock; mode free\nloc.dock: the dock\n  desc: wet planks\n"
                     "npc.mara_voss: Mara Voss")["fiction"]
    assert look == "You look around. You take in the dock: wet planks. Mara Voss is here. What do you do?"


def test_checker_extracts_claims_and_screen() -> None:
    draft = "The guard draws a sword. Mara Voss is bleeding at the gate. Rain falls. You feel afraid. Roll 3d6!"
    out = fill(Role.CHECKER, draft)
    subjects = [(c["sentence"], c["subject"]) for c in out["claims"]]
    assert subjects == [(0, "npc.gate_guard"), (1, "npc.mara_voss")]
    assert out["claims"][0]["class"] == "possession" and out["claims"][0]["asserts_change"] is True
    assert out["claims"][1]["class"] == "harm_condition"
    screen = out["screen"]
    assert "3d6" in "".join(screen["mechanics_in_fiction"]) or "3" in screen["mechanics_in_fiction"]
    assert screen["ends_on_prompt_or_one_pause"] is False
    clean = fill(Role.CHECKER, "Mara Voss waits by the stall. What do you do?")["screen"]
    assert clean["ends_on_prompt_or_one_pause"] and clean["next_step_exists"] and clean["mechanics_in_fiction"] == []


def test_sentences_keep_quotes_whole() -> None:
    assert sentences('"Stop. Now." I raise a hand. Who goes there?') == ['"Stop. Now."', "I raise a hand.",
                                                                       "Who goes there?"]
    assert sentences('"Wait," I say. Then I go.') == ['"Wait," I say.', "Then I go."]


def test_scripted_queue_fallback_and_exhaustion() -> None:
    model = ScriptedModel({Role.NARRATOR: [{"fiction": "Bad 7 draft", "mentions": []}]})
    first = call_role(model, Role.NARRATOR, NARRATOR, Packet())
    assert first.data["fiction"] == "Bad 7 draft" and first.record.provider == "scripted"
    second = call_role(model, Role.NARRATOR, NARRATOR, Packet(view="npc.old_tam: Old Tam",
                                                              message='- part [SPEECH] "Evening."'))
    assert "Old Tam" in second.data["fiction"]  # fell back to OfflineModel
    model.push(Role.CHECKER, lambda schema, packet: {"claims": [], "screen": {}})
    assert model.fill(Role.CHECKER, CHECKER, Packet(), turn_id=None, attempt=0).data["claims"] == []
    strict = ScriptedModel(fallback=False)
    with pytest.raises(ScriptExhausted):
        strict.fill(Role.READER, READER, Packet(), turn_id=None, attempt=0)
    assert len(model.calls) == 3


def test_pydantic_generated_schema_round_trips() -> None:
    from typing import Literal

    from pydantic import BaseModel

    class Part(BaseModel):
        text: str
        kind: Literal["DECLARATION", "SPEECH", "FICTION_QUESTION"]

    class Beat(BaseModel):
        verb: Literal["verb.strike", "verb.observe"]
        gate: Literal["G1", "G3"]

    class Out(BaseModel):
        parts: list[Part]
        pending_answer: Literal["commit", "withdraw"] | None
        restatement: str
        beats: list[Beat]

    schema = Out.model_json_schema()
    assert "$defs" in schema
    res = MODEL.fill(Role.READER, schema, Packet(message="I look around."), turn_id=None, attempt=0)
    assert validate(res.data, schema) == []
    parsed = Out.model_validate(res.data)
    assert parsed.beats[0].verb == "verb.observe" and parsed.pending_answer is None
