"""Per-role JSON Schemas for the model calls (contracts/model-calls.md; T026).

    ctx = schema_context(state, rules, anchors=cands, beat=beat, message=text)   # enums for this call
    schema = build_schema(Role.FRAMER, ctx)          # or framer_schema(ctx), reader_schema(ctx), ...
    result = call_role(model, Role.FRAMER, schema, packet, default=defaults(Role.FRAMER, ctx))

Every enum is filled from the rules and the current state; an empty enum list drops its field from the schema
(and from `required`). No schema has a numeric field except the Reader's `player_quantity` (the player's own
stated number, 01.1.4; INV-3). Every object is closed (`additionalProperties: false`) and lists every
property as required; optional values are nullable instead. Where a value may be `none`, `none` is the first
enum option (the conservative pick of a schema-repairing model).

Deviations from the contract, both forced by "no numeric field": the Checker's `Claim.sentence` (an int in
data-model.md §4) is a string enum of sentence indices ("0", "1", ...) built from the draft; World want and
refusal ids are `<npc id>/want.<n>` / `<npc id>/refusal.<n>` (NPC wants carry no ids in the record), one
enum across the present NPCs.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from typing import Any, get_args

from pydantic import BaseModel, Field

from engine.llm.base import Role
from engine.resolve.costs import OBSERVER, uncited_by_stakes
from engine.resolve.frame import fact_usable, opposed_by, rolling_tiers, verb_classes
from engine.resolve.gate import covering_verb
from engine.retrieve.anchors import verb_anchor
from engine.retrieve.scene import pc_id, scene_facts, scene_scope
from engine.store.events import EntityKind
from engine.store.projection import WorldState

Schema = dict[str, Any]

# Closed lists the rules state in prose (no data file carries them).
BEAT_SHAPES = ("now", "extended", "queued", "conditional")  # 12.2.2 decision 3 (I-146c); extended: 01.2.2 (P-082)
QUESTION_KINDS = ("none", "who_is", "where_is", "what_happened", "what_like", "what_want", "who_knows")  # 12.2.2
# 01.2.1/01.2.2: a step or gesture with no change of its own is part of the act it serves; 00.12.6: free activities
BEAT_PURPOSES = ("own_change", "serves_another_act", "free_activity")
# 15.3.10 / 12.2.2: what moves a listener beyond a plain question (none: the words are SPEECH)
TALK_PRESSURES = ("none", "request", "threat", "offer", "plea", "insistence")
NUDGES = ("0", "-1", "+1")  # 01.6.5: one rung at most; strings, never a numeric field (INV-3)
REQUEST_SIZES = ("R1", "R2", "R3", "R4", "R5")  # 15.3.2
SPECIAL_CHOICES = ("own_words", "move_on", "details", "suggest")  # contracts/model-calls.md I
OBSTACLE_KINDS = ("tier", "opposed", "entity_defense")  # 01.6.3
MODE_PILLAR = {"conflict": "conflict", "site": "exploration", "travel": "travel", "downtime": "downtime",
               "free": "social"}  # 12.9.1: the pillar a scene's mode implies when nothing else decides
NONE = "none"


class SchemaContext(BaseModel):
    """Everything the builders read. `schema_context` fills it from state and rules; tests may build it directly."""

    message: str = ""  # the player's message (Reader default)
    # Interpret
    options: list[str] = Field(default_factory=list)
    own_words_classes: list[str] = Field(default_factory=list)
    lines_and_veils: bool = False  # creation step 1(b) only
    # shared state enums
    scene_ids: list[str] = Field(default_factory=list)
    fact_ids: list[str] = Field(default_factory=list)
    pc_licences: list[str] = Field(default_factory=list)
    licences: list[str] = Field(default_factory=list)  # every licence id in data (a G3's would-be licence)
    reachable_places: list[str] = Field(default_factory=list)  # places a Move can head for (10.1.3)
    pending_choice_ids: list[str] = Field(default_factory=list)
    # Reader (rules)
    input_classes: list[str] = Field(default_factory=list)
    oracle_rungs: list[str] = Field(default_factory=list)
    verbs: list[str] = Field(default_factory=list)
    # Framer
    anchor_ids: list[str] = Field(default_factory=list)
    default_anchor: str | None = None
    knobs: list[str] = Field(default_factory=list)
    deltas: list[str] = Field(default_factory=list)
    attributes: list[str] = Field(default_factory=list)
    default_attribute: str | None = None
    deed_tags: list[str] = Field(default_factory=list)
    traits: list[str] = Field(default_factory=list)
    dc_tiers: list[str] = Field(default_factory=list)
    obstacle_classes: list[str] = Field(default_factory=list)  # the beat's verb's rubric classes (01.6.5)
    opposed_ids: list[str] = Field(default_factory=list)  # a social or attack beat's defender: no tier (01.6.4)
    social: bool = False  # a Talk aimed at a person: the 15.3.3 DC, with a request size
    asks_tags: list[str] = Field(default_factory=list)  # social.yaml#event_tags.asks (12.11.9; I-176)
    cast_ids: list[str] = Field(default_factory=list)
    defender_ids: list[str] = Field(default_factory=list)  # present entities with a named defense (01.6.4)
    lever_fact_ids: list[str] = Field(default_factory=list)
    stakes_sources: list[str] = Field(default_factory=list)
    cost_menu_ids: list[str] = Field(default_factory=list)
    alternate_cost_menu_ids: list[str] = Field(default_factory=list)
    # PR-01-2 step 10: entries legal without a cited source fact (costs.uncited_candidates); None = unrestricted
    cost_uncited_ids: list[str] | None = None
    cost_tie_order: list[str] = Field(default_factory=list)
    reach_tie_whole: bool = False
    reach_tie_one_factor: bool = True
    # World
    npc_ids: list[str] = Field(default_factory=list)
    want_ids: list[str] = Field(default_factory=list)
    refusal_ids: list[str] = Field(default_factory=list)
    npc_action_tags: list[str] = Field(default_factory=list)
    # Director
    modes: list[str] = Field(default_factory=list)
    previous_mode: str | None = None
    places: list[str] = Field(default_factory=list)
    current_place: str | None = None
    pillars: list[str] = Field(default_factory=list)
    challenge_types: list[str] = Field(default_factory=list)
    known_ids: list[str] = Field(default_factory=list)
    push_options: list[str] = Field(default_factory=list)  # empty unless trg.pacing_push is raised
    thread_ids: list[str] = Field(default_factory=list)
    lead_routes: list[str] = Field(default_factory=list)  # empty unless trg.lead_injection fires
    # Narrator (spec 006: declared sentences, 12.3.1)
    entity_kinds: list[str] = Field(default_factory=list)
    narrator_refs: list[str] = Field(default_factory=list)  # this turn's record handles, then the view's fact ids
    element_kinds: list[str] = Field(default_factory=list)  # pacing.yaml#claim_check.element_tiers keys
    speaker_ids: list[str] = Field(default_factory=list)  # 12.3.1b: present people who may speak (never the PC)
    narrator_mode: str = "sentences"  # "sentences" | "fiction" (the fallback shape, B risk 2)
    repair_ids: list[str] = Field(default_factory=list)  # failing sentence indices ("3") for a repair call
    repair: bool = False  # a narrow repair call (12.3.3): replacements only
    # Checker
    claim_classes: list[str] = Field(default_factory=list)
    sentence_ids: list[str] = Field(default_factory=list)
    checker_refs: list[str] = Field(default_factory=list)  # what the draft's sentences declare (refs, about ids)


# ---------------------------------------------------------------- schema helpers


def enum(values: Iterable[Any], *, nullable: bool = False, first: str | None = None) -> Schema | None:
    """A string enum (deduplicated, order kept); None when there are no values (the field is dropped).
    `first` (e.g. "none") is put first and does not by itself keep the field."""
    vals = [str(v) for v in dict.fromkeys(values) if v is not None and str(v) != first]
    if not vals and first is None:
        return None
    if first is not None:
        vals.insert(0, first)
    if nullable:
        return {"type": ["string", "null"], "enum": [*vals, None]}
    return {"type": "string", "enum": vals}


def obj(props: Mapping[str, Schema | None]) -> Schema:
    """A closed object whose present properties are all required; None properties are dropped."""
    kept = {k: v for k, v in props.items() if v is not None}
    return {"type": "object", "properties": kept, "required": list(kept), "additionalProperties": False}


def arr(items: Schema | None, *, max_items: int | None = None) -> Schema | None:
    if items is None:
        return None
    out: Schema = {"type": "array", "items": items}
    if max_items is not None:
        out["maxItems"] = max_items
    return out


def nullable(node: Schema) -> Schema:
    return {"anyOf": [node, {"type": "null"}]}


STR: Schema = {"type": "string"}
STR_OR_NULL: Schema = {"type": ["string", "null"]}
BOOL: Schema = {"type": "boolean"}
STRS: Schema = {"type": "array", "items": STR}


# ---------------------------------------------------------------- builders


def interpret_schema(ctx: SchemaContext) -> Schema:  # rule: 12.16.2
    return obj({
        "choice": enum([*ctx.options, *SPECIAL_CHOICES]),
        "own_words_class": enum(ctx.own_words_classes, nullable=True),
        "own_words_text": STR_OR_NULL,
        "lines_and_veils": STRS if ctx.lines_and_veils else None,
        "answer": STR_OR_NULL,  # with `details`: a short reply to the player's question
    })


def reader_schema(ctx: SchemaContext) -> Schema:  # rule: 12.2.2
    # DL-12-50: the verb, target, three method facets and the shape; the gate, the licence, the would-be licence and
    # the roll test are computed (00.12.3, PR-01-5, 01.4.1)
    beat = obj({
        "intent": STR,
        "method": STR,
        "purpose": enum(BEAT_PURPOSES),  # code folds and drops (reader.normalise_beats)
        "assertion": STR_OR_NULL,
        "shape": enum(BEAT_SHAPES),
        "target": enum([*ctx.scene_ids, *ctx.reachable_places], first=NONE),
        "verb": enum(ctx.verbs),
        "pressure": enum(TALK_PRESSURES),
        "against_will": BOOL,
        "uses_power": BOOL,
        "speech": BOOL,
        "g4_fact": enum(ctx.fact_ids, nullable=True),
        "intent_verbs": STRS,
    })
    return obj({
        "parts": arr(obj({"text": STR, "class": enum(ctx.input_classes), "question_kind": enum(QUESTION_KINDS),
                          "topic": STR_OR_NULL})),
        "pending_answer": enum(ctx.pending_choice_ids, nullable=True),
        "fact_questions": arr(obj({
            "subject": enum(ctx.scene_ids),
            "predicate": STR,
            "odds_rung": enum(ctx.oracle_rungs),
        })),
        "beats": arr(beat, max_items=3),  # 01.2.3
        "clarifying_question": STR_OR_NULL,  # 01.2.4
        "restatement": STR,  # 01.2.6
        "player_quantity": {"type": ["integer", "null"]},  # 01.1.4: the only numeric field (INV-3)
    })


NULL: Schema = {"type": "null"}


def _one_of(branches: list[Schema]) -> Schema:
    return branches[0] if len(branches) == 1 else {"anyOf": branches}


def _cost(menu: list[str], facts: list[str], uncited: list[str] | None = None) -> Schema:
    # 01.13.1 / lead decision (a): a cost may cite the scene fact that is its source (frame_check needs either
    # the citation or a structural fit through state); dropped when the scene has no fact. With `uncited`
    # (PR-01-2 step 10, costs.uncited_candidates): an entry outside it must cite a source fact, and cost.twist
    # is offered only when it is itself a candidate.
    if uncited is None:
        return obj({"menu_id": enum(menu), "form_intent": STR, "source_fact": enum(facts, nullable=True)})
    free = [m for m in menu if m in uncited]
    cited = [m for m in menu if m not in free and m != "cost.twist"] if facts else []
    out = [obj({"menu_id": enum(free), "form_intent": STR, "source_fact": enum(facts, nullable=True)})] if free else []
    if cited:
        out.append(obj({"menu_id": enum(cited), "form_intent": STR, "source_fact": enum(facts)}))
    return _one_of(out or [obj({"menu_id": enum(menu), "form_intent": STR})])


def _obstacle(ctx: SchemaContext) -> Schema:  # rule: 00.3.8
    # rule: 01.6.5
    """The DC's source as a choice (00.3.8): the verb's obstacle class (its base sets the tier; `other` names the
    rung by T-01-2), or an opposed / entity-defense obstacle naming its entity. A social or attack beat aimed at a
    creature (`opposed_ids`) offers only its defense (01.6.4: never a tier)."""
    out: list[Schema] = []
    defenders = ctx.defender_ids
    if ctx.opposed_ids:
        out.append(obj({"kind": enum(["opposed"]), "obstacle_class": NULL, "tier": NULL,
                        "entity": enum(ctx.opposed_ids)}))
        defenders = [d for d in defenders if d in ctx.opposed_ids]
    else:
        if ctx.obstacle_classes:
            out.append(obj({"kind": enum(["tier"]), "obstacle_class": enum(ctx.obstacle_classes), "tier": NULL,
                            "entity": NULL}))
        out.append(obj({"kind": enum(["tier"]), "obstacle_class": enum(["other"]), "tier": enum(ctx.dc_tiers),
                        "entity": NULL}))
        if ctx.cast_ids:
            out.append(obj({"kind": enum(["opposed"]), "obstacle_class": NULL, "tier": NULL,
                            "entity": enum(ctx.cast_ids)}))
    if defenders:
        out.append(obj({"kind": enum(["entity_defense"]), "obstacle_class": NULL, "tier": NULL,
                        "entity": enum(defenders)}))
    return _one_of(out)


def framer_schema(ctx: SchemaContext) -> Schema:  # rule: 01.5.1
    facts = ctx.lever_fact_ids  # PR-01-2 steps 3, 7, 10: only facts established before the declaration
    delta = obj({"knob": enum(ctx.knobs), "delta": enum(ctx.deltas), "cites_fact": enum(facts)})
    return obj({
        "anchor": enum(ctx.anchor_ids),
        "deltas": arr(delta, max_items=2) if ctx.deltas else None,  # 01.5.3: two changes at most
        "attribute": enum(ctx.attributes),
        "deed_tag": enum(ctx.deed_tags),
        "traits": arr(enum(ctx.traits)),
        "obstacle": _obstacle(ctx),
        # 01.6.5: one rung at most, the why written before the value, citing an intrinsic fact
        "nudge_why": STR_OR_NULL if ctx.obstacle_classes and not ctx.opposed_ids else None,
        "nudge": enum(NUDGES) if ctx.obstacle_classes and not ctx.opposed_ids else None,
        "nudge_fact": enum(facts, nullable=True) if ctx.obstacle_classes and not ctx.opposed_ids else None,
        "request_size": enum(REQUEST_SIZES) if ctx.social else None,  # 15.3.2: what the talk asks for
        "levers": arr(enum(facts), max_items=2),  # 01.6.8
        "snags": arr(enum(facts), max_items=2),
        "stakes_source": enum(ctx.stakes_sources, first=NONE),  # 01.6.9
        "stakes_heavy": BOOL,
        "lethal": BOOL,
        "reach_whole": BOOL,  # 01.6.10
        "reach_one_factor": BOOL,
        "reach_two_factors": BOOL,  # 01.6.10 decision 2: two unoffset, or a total potency -> G4 (I-160a)
        "asks": enum(ctx.asks_tags, first=NONE) if ctx.social else None,  # 12.11.9 step 3(b): the request's tag
        "threatened_cost": _cost(ctx.cost_menu_ids, facts, ctx.cost_uncited_ids),  # 01.6.11, 01.13.1
        "alternate_cost": nullable(_cost(ctx.alternate_cost_menu_ids or ctx.cost_menu_ids, facts,
                                         ctx.cost_uncited_ids)),
        "method_consequences": STRS,
        "secret": BOOL,
    })


def world_schema(ctx: SchemaContext) -> Schema:  # rule: 12.11.5
    return obj({"responses": arr(obj({
        "npc": enum(ctx.npc_ids),
        "want_engaged": enum(ctx.want_ids, first=NONE),
        "refusal_engaged": enum(ctx.refusal_ids, first=NONE),
        "table_context": obj({"tags": arr(enum(ctx.npc_action_tags))}),
    })) if ctx.npc_ids else None})


def director_schema(ctx: SchemaContext) -> Schema:  # rule: 12.4.2
    lead = None
    if ctx.lead_routes:
        lead = nullable(obj({"thread": enum(ctx.thread_ids), "via": enum(ctx.lead_routes)}))
    return obj({
        "cut_now": BOOL,
        "next_scene": obj({
            "mode": enum(ctx.modes),
            "place": enum(ctx.places),
            "agenda": STR,
            "hoped_answer": STR,  # 12.6.3
            "pillar": enum(ctx.pillars),  # 12.9.1
            "challenge_type": enum(ctx.challenge_types, nullable=True),  # T-12-7; null without opposition
            "cast": arr(enum([*ctx.known_ids, "new_npc"])),
        }),
        "push": enum(ctx.push_options, first=NONE) if ctx.push_options else None,  # 12.7.4
        "lead": lead,  # 12.8.2
    })


MAX_SENTENCE_INDEX = 30  # the fallback shape's sentence keys "0".."29" (a string enum: INV-3)


def _declaration(ctx: SchemaContext, text: bool = False) -> dict[str, Schema | None]:  # rule: 12.3.1
    """The declaration fields; with `text`, the sentence's `text` goes after `new` (spec 009 B: the new elements are
    listed before the sentence is written, so what it introduces is planned, then said)."""
    return {
        "refs": arr(enum(ctx.narrator_refs)) if ctx.narrator_refs else None,
        "about": arr(enum(ctx.scene_ids)) if ctx.scene_ids else None,
        "new": arr(obj({
            "element_kind": enum(ctx.element_kinds),
            "name": STR,
            "ordinary": BOOL,
            "implied": arr(obj({"predicate": STR, "value": STR})),
        })),
        **({"text": STR} if text else {}),
        "atmosphere": BOOL,
        "speaker": enum(ctx.speaker_ids, first=NONE),  # 12.3.1b item 1: whose words the quotes are; never the PC
    }


def narrator_schema(ctx: SchemaContext) -> Schema:  # rule: 12.3.1
    """Declared sentences (12.3.1 source 1); `narrator_mode` "fiction" is the fallback shape: the prose whole, with
    declarations keyed by sentence index. A repair call (`repair_ids`) returns replacements only (12.3.3)."""
    if ctx.repair or ctx.repair_ids:
        return obj({"repairs": arr(obj({"replaces": enum([*ctx.repair_ids, "add"]), **_declaration(ctx, True)}))})
    if ctx.narrator_mode == "fiction":
        return obj({"fiction": STR, "declarations": arr(obj({
            "sentence": enum([str(i) for i in range(MAX_SENTENCE_INDEX)]), **_declaration(ctx)}))})
    return obj({"sentences": arr(obj(_declaration(ctx, True)))})


def checker_schema(ctx: SchemaContext) -> Schema:  # rule: 12.3.1
    """The diff audit (12.3.1 source 2, DL-12-71): `claims` are only assertions beyond a sentence's declarations;
    `undeclared` the addressable things a sentence introduces that it does not declare, typed by kind (written by
    their tier, 12.14.13); `unexpressed` the declarations a sentence does not say (or says otherwise)."""
    sent = enum(ctx.sentence_ids)
    claim = obj({
        "sentence": sent,
        "subject": enum([*ctx.scene_ids, "unknown"]),
        "class": enum(ctx.claim_classes),
        "predicate": STR,
        "value": STR,
        "asserts_change": BOOL,
        "pc_words_or_feelings": BOOL,
    })
    refs = enum(ctx.checker_refs)
    return obj({
        "claims": arr(claim),
        "undeclared": arr(obj({"sentence": sent, "element_kind": enum(ctx.element_kinds), "name": STR,
                               "ordinary": BOOL})) if ctx.element_kinds else None,
        "unexpressed": arr(obj({"sentence": sent, "ref": refs, "says_otherwise": BOOL})) if refs else None,
        "screen": obj({  # no safety field: the safety screen is separate (FR-036)
            "intent_acknowledged": BOOL,
            "intent_substituted": BOOL,
            "next_step_exists": BOOL,
            "mechanics_in_fiction": STRS,
            "ends_on_prompt_or_one_pause": BOOL,
        }),
    })


CANDIDATE_KINDS = ("ordinary_fact", "not_ordinary")  # PR-12-10 step 4: only an ordinary fact may be ratified


def proposer_schema(ctx: SchemaContext) -> Schema:  # rule: PR-12-10
    """Rung 3's one typed candidate `{kind, subject, predicate, value}` (12.10.8; 00.12.7's proposal form)."""
    return obj({"kind": enum(CANDIDATE_KINDS), "subject": STR, "predicate": STR, "value": STR})


LOCATE_CATEGORIES = ("remembered_wrong", "rule_wrong", "contradiction", "misread", "other")  # 12.3.6 item 2


def locator_schema(turns: Sequence[str] | None = None) -> Schema:  # rule: PR-12-11
    """Step 1's call: `{turn, quote, category}` plus the player's claim restated (`subject`, `key`, `value`); `turn`
    is one of the candidate turns or `none` (spec 012)."""
    turn = enum([*turns, "none"]) if turns is not None else STR
    return obj({"turn": turn, "quote": STR, "category": enum(LOCATE_CATEGORIES), "subject": STR, "key": STR,
                "value": STR})


BUILDERS: dict[Role, Callable[[SchemaContext], Schema]] = {
    Role.INTERPRET: interpret_schema,
    Role.READER: reader_schema,
    Role.FRAMER: framer_schema,
    Role.WORLD: world_schema,
    Role.DIRECTOR: director_schema,
    Role.NARRATOR: narrator_schema,
    Role.CHECKER: checker_schema,
    Role.PROPOSER: proposer_schema,
    Role.LOCATOR: lambda ctx: locator_schema(),
}


def build_schema(role: Role, ctx: SchemaContext) -> Schema:
    return BUILDERS[role](ctx)


# ---------------------------------------------------------------- defaults


def _first(options: list[str], *preferred: str | None) -> str | None:
    for p in preferred:
        if p is not None and p in options:
            return p
    return options[0] if options else None


def prune(value: Any, node: Mapping[str, Any]) -> Any:
    """Drop object keys the schema does not have (fields dropped for empty enums)."""
    if isinstance(value, dict):
        sub = node
        if "anyOf" in node:
            sub = next((o for o in node["anyOf"] if o.get("type") == "object"), node)
        props = sub.get("properties")
        if props is None:
            return value
        return {k: prune(v, props[k]) for k, v in value.items() if k in props}
    if isinstance(value, list) and "items" in node:
        return [prune(v, node["items"]) for v in value]
    return value


def defaults(role: Role, ctx: SchemaContext) -> dict[str, Any] | None:  # rule: 12.2.2
    """The contract's per-field defaults as one response, valid against `build_schema(role, ctx)`.

    None for the Narrator and the Checker: they have no rule default (the turn errors, or the engine's plain
    fallback runs, 12.3.3).
    """
    if role in (Role.NARRATOR, Role.CHECKER):
        return None
    value = DEFAULTS[role](ctx)
    return prune(value, build_schema(role, ctx))


def _interpret_default(ctx: SchemaContext) -> dict[str, Any]:
    # move_on: the block's default answer applies (12.16.2, PR-02-7)
    return {"choice": "move_on", "own_words_class": None, "own_words_text": None, "lines_and_veils": [],
            "answer": None}


def _reader_default(ctx: SchemaContext) -> dict[str, Any]:
    # 12.2.2: SPEECH vs DECLARATION ties go to DECLARATION; no beats are guessed
    return {
        "parts": [{"text": ctx.message, "class": "DECLARATION", "question_kind": "none", "topic": None}]
        if ctx.message.strip() else [],
        "pending_answer": None, "fact_questions": [], "beats": [], "clarifying_question": None,
        "restatement": ctx.message, "player_quantity": None,
    }


def _framer_default(ctx: SchemaContext) -> dict[str, Any]:
    # 00.15.3: the basic verb's anchor; 01.6.1: the anchor's default attribute; stakes none -> safe; the obstacle:
    # the defender's defense for a social or attack beat (01.6.4), else class `other` at Easy (lane D P2)
    free = [m for m in ctx.cost_menu_ids if ctx.cost_uncited_ids is None or m in ctx.cost_uncited_ids]
    menu = _first(free or ctx.cost_menu_ids, *ctx.cost_tie_order)
    obstacle = ({"kind": "opposed", "obstacle_class": None, "tier": None, "entity": ctx.opposed_ids[0]}
                if ctx.opposed_ids else
                {"kind": "tier", "obstacle_class": "other", "tier": _first(ctx.dc_tiers, "easy"), "entity": None})
    return {
        "anchor": _first(ctx.anchor_ids, ctx.default_anchor),
        "deltas": [],
        "attribute": _first(ctx.attributes, ctx.default_attribute),
        "deed_tag": _first(ctx.deed_tags),
        "traits": [],
        "obstacle": obstacle,
        "nudge_why": None, "nudge": "0", "nudge_fact": None, "request_size": "R2",
        "levers": [], "snags": [],
        "stakes_source": NONE, "stakes_heavy": False, "lethal": False,
        "reach_whole": ctx.reach_tie_whole, "reach_one_factor": ctx.reach_tie_one_factor,
        "reach_two_factors": False, "asks": NONE,
        "threatened_cost": {"menu_id": menu, "form_intent": "", "source_fact": None},
        "alternate_cost": None,
        "method_consequences": [], "secret": False,
    }


def _world_default(ctx: SchemaContext) -> dict[str, Any]:
    return {"responses": [{"npc": n, "want_engaged": NONE, "refusal_engaged": NONE, "table_context": {"tags": []}}
                          for n in ctx.npc_ids]}


def _director_default(ctx: SchemaContext) -> dict[str, Any]:
    # 12.4: previous scene's mode, unsure -> free; the pillar the mode implies
    mode = _first(ctx.modes, ctx.previous_mode, "free")
    return {
        "cut_now": False,
        "next_scene": {
            "mode": mode, "place": _first(ctx.places, ctx.current_place), "agenda": "", "hoped_answer": "",
            "pillar": _first(ctx.pillars, MODE_PILLAR.get(mode or "")), "challenge_type": None, "cast": [],
        },
        "push": NONE, "lead": None,
    }


DEFAULTS: dict[Role, Callable[[SchemaContext], dict[str, Any]]] = {
    Role.INTERPRET: _interpret_default,
    Role.READER: _reader_default,
    Role.FRAMER: _framer_default,
    Role.WORLD: _world_default,
    Role.DIRECTOR: _director_default,
    # no candidate: the ladder goes on to the pointer (PR-12-10 step 5)
    Role.PROPOSER: lambda ctx: {"kind": "not_ordinary", "subject": "", "predicate": "", "value": ""},
    # no passage found: the dispute is answered "which statement?" and logged (PR-12-11 step 1)
    Role.LOCATOR: lambda ctx: {"turn": "none", "quote": "", "category": "other", "subject": "", "key": "",
                               "value": ""},
}


# ---------------------------------------------------------------- context from state and rules


def _ancestors(tag: str) -> list[str]:
    parts = tag.split(".")
    return [".".join(parts[:i]) for i in range(len(parts), 0, -1)]


def _anchor_enums(anchor_ids: list[str], rules: Any) -> dict[str, list[str]]:  # rule: 01.5.3
    knobs: list[str] = []
    deltas: list[str] = []
    attrs: list[str] = []
    deeds: list[str] = []
    known_attrs = set(rules.attributes)
    for aid in anchor_ids:
        a = rules.anchors.get(aid, {})
        for k in a.get("knobs", []):
            knobs.append(str(k.get("knob")))
            deltas.extend(str(d) for d in k.get("allowed_deltas", []) or [])
            if k.get("knob") == "attribute":
                for word in [k.get("default"), *(k.get("allowed_deltas", []) or [])]:
                    first = str(word or "").split(" ")[0].strip().lower()
                    if first in known_attrs:
                        attrs.append(first)
        for t in a.get("deed_tags", []):
            deeds.extend(_ancestors(str(t)))
    return {k: list(dict.fromkeys(v)) for k, v in
            {"knobs": knobs, "deltas": deltas, "attributes": attrs, "deed_tags": deeds}.items()}


def _reachable(state: Any) -> list[str]:  # rule: 10.1.3
    from engine.world.places import reachable

    try:
        return [x.to for x in reachable(state)]
    except Exception:  # noqa: BLE001 - no PC position yet: nowhere to head for
        return []


def _verb_attribute(anchor_id: str | None, rules: Any) -> str | None:
    if not anchor_id:
        return None
    for k in rules.anchors.get(anchor_id, {}).get("knobs", []):
        if k.get("knob") == "attribute":
            return str(k.get("default") or "").split(" ")[0].lower() or None
    return None


def _attr_word(x: Any, known: Iterable[str]) -> str | None:
    word = str(x or "").strip().lower().split(" (")[0].split(" ")[0]
    return word if word in known else None


def _attribute_options(anchor_ids: list[str], verb: str | None, licence: str | None, knob_attrs: list[str],
                       rules: Any) -> tuple[list[str], str | None]:  # rule: 01.6.1
    """(options, default) for the Framer's `attribute` enum, as frame_check (step 4) allows them: each candidate
    anchor's attribute knob (default and deltas), its verb's `attribute` + `alt_attributes` (the anchor's verb,
    else the beat's), and the licence's `attribute`. `by_method`/`by_license`, a licence with no fixed attribute,
    or an anchor with no verb and no attribute knob open the list to every attribute (the method decides).
    The default is the default anchor's knob default, else its verb's (or the beat's verb's) attribute."""
    known = list(rules.attributes)
    allowed: list[str] = []
    open_ = bare = False
    defaults: list[str | None] = []
    for aid in anchor_ids or [None]:
        a = rules.anchors.get(aid, {}) if aid else {}
        v = a.get("verb") or verb
        entry = rules.basic_verbs.get(v) if v else None
        knob = next((k for k in a.get("knobs", []) if k.get("knob") == "attribute"), None)
        if knob is not None:
            defaults.append(_attr_word(knob.get("default"), known))
        if entry is None:
            bare = bare or knob is None
            continue
        words = [entry.get("attribute"), *[x.get("attribute") for x in entry.get("alt_attributes") or ()]]
        for w in words:
            if w in ("by_method", "by_license"):
                open_ = True
            elif (aw := _attr_word(w, known)) is not None:
                allowed.append(aw)
        defaults.append(_attr_word(words[0], known))
    fixed = None
    if licence:
        la = (rules.licenses.get(licence) or {}).get("attribute")
        if la in (None, "by_method"):
            open_ = True
        elif (fixed := _attr_word(la, known)) is not None:
            allowed.append(fixed)
            defaults.append(fixed)
    open_ = open_ or (bare and fixed is None)
    default = next((d for d in defaults if d), None)
    options: list[str] = list(dict.fromkeys([*([default] if default else []), *knob_attrs, *allowed,
                                             *(known if open_ else [])]))
    return options or [str(a) for a in known], default


def fitting_cost_menus(rules: Any, fact_ids: list[str]) -> tuple[list[str], list[str]]:  # rule: 01.13.1
    """(threatened, alternate) cost menu ids. Every entry but the twist needs an established source to cite
    (cost_selection: "each citing a fact id of its source"), so with no scene facts only the twist fits;
    `alternate_only` entries (the shortfall) are never the threatened cost."""
    threatened: list[str] = []
    alternate: list[str] = []
    for c in rules.resolution.get("cost_menu", []):
        always = str(c.get("fits_when", "")).startswith("always")
        if not (always or fact_ids):
            continue
        alternate.append(c["id"])
        if not c.get("alternate_only"):
            threatened.append(c["id"])
    return threatened, alternate


def _want_ids(state: WorldState, npc: str) -> tuple[list[str], list[str]]:
    data = state.entities[npc].data
    # a promoted NPC's wants/refusals are later facts (engine.world.social.npc_field); else the creation record
    def _list(key: str) -> list[Any]:  # a non-list fact (an old save's Oracle yes/no) falls back to the record
        v = state.fact_value(npc, key)
        return v if isinstance(v, list) else (data.get(key) or [])

    wants_v, refusals_v = _list("wants"), _list("refusals")
    wants = [f"{npc}/want.{i + 1}" for i, _ in enumerate(wants_v)]
    refusals = [f"{npc}/refusal.{i + 1}" for i, _ in enumerate(refusals_v)]
    return wants, refusals


def _visible(state: WorldState, eid: str) -> bool:
    seal = state.seals.get(eid)
    return seal is None or bool(seal.slice)


def schema_context(  # rule: 12.2.4
    state: WorldState,
    rules: Any,
    *,
    message: str = "",
    options: Iterable[str] = (),
    own_words_classes: Iterable[str] = (),
    lines_and_veils: bool = False,
    anchors: Iterable[str] = (),
    beat: Any = None,
    lever_fact_ids: Iterable[str] | None = None,
    cost_menu_ids: Iterable[str] | None = None,
    places: Iterable[str] | None = None,
    push_raised: bool = False,
    lead_fires: bool = False,
    draft_sentences: Iterable[str] = (),
    focus: Iterable[str] = (),
) -> SchemaContext:
    """The enums for this call, from the rules and the current state (scene-scoped; bounded). `focus` must be
    the ids the call's `build_packet` got, so the fact enum is the view's facts."""
    scope = scene_scope(state)
    facts = [f.id for f in scene_facts(state, scope, focus=focus)]
    pc = pc_id(state)
    pause = state.open_pause()
    anchor_ids = list(dict.fromkeys(anchors))
    verb = (beat.get("verb") if isinstance(beat, Mapping) else getattr(beat, "verb", None)) if beat else None
    licence = (beat.get("license") if isinstance(beat, Mapping) else getattr(beat, "license", None)) if beat else None
    default_anchor = verb_anchor(verb, rules) if verb else None
    if default_anchor not in anchor_ids:
        default_anchor = anchor_ids[0] if anchor_ids else None
    ae = _anchor_enums(anchor_ids, rules)
    ordered = [default_anchor, *[a for a in anchor_ids if a != default_anchor]] if default_anchor else anchor_ids
    attributes, default_attribute = (_attribute_options(ordered, verb, licence, ae["attributes"], rules)
                                     if anchor_ids else (ae["attributes"], None))
    threatened, alternate = fitting_cost_menus(rules, facts)
    uncited = None
    usable = facts
    sources = list(rules.resolution.get("stakes_flags", {}).get("source", {}).get("sources", []))
    ob_classes: list[str] = []
    opposed: list[str] = []
    social = False
    if beat is not None and not isinstance(beat, Mapping) and getattr(beat, "actor", None):  # the Framer's beat
        tgt = beat.target if beat.target and beat.target != NONE else None
        cv = covering_verb(beat.verb, against_will=beat.against_will, speech=beat.speech)
        ob_classes = list(verb_classes(rules, cv))
        opposed = opposed_by(state, beat, cv)
        social = bool(opposed) and cv == "verb.talk"
        by = uncited_by_stakes(state=state, rules=rules, actor=beat.actor, target=tgt, beat=beat)  # steps 8, 10
        # an onlooker who would act: present (computed), or named by a cited source fact (frame_check)
        sources = [s for s in sources if s in by or s == OBSERVER]
        uncited = [m for m in dict.fromkeys(m for ms in by.values() for m in ms) if m != "cost.twist"
                   or m in by[NONE]]
        usable = [f for f in facts if fact_usable(state, f, beat.declared_seq or state.last_seq)]
    if cost_menu_ids is not None:
        threatened = list(cost_menu_ids)
        alternate = list(dict.fromkeys([*threatened, *alternate]))
    res = rules.resolution
    pacing = rules.pacing
    cast = [i for i in (state.scene.cast_present if state.scene else []) if i in state.entities]
    npcs = [i for i in cast if state.entities[i].kind in ("npc", "companion")]
    wants: list[str] = []
    refusals: list[str] = []
    for n in npcs:
        w, r = _want_ids(state, n)
        wants.extend(w)
        refusals.extend(r)
    npc_table = rules.table("tbl.npc_action")
    tags = [str(t) for row in npc_table.get("results", []) for t in row.get("tags", []) or []]

    def by_kind(*kinds: str) -> list[str]:
        return [eid for eid, e in state.entities.items() if e.kind in kinds and _visible(state, eid)]

    reach = res.get("reach_flags", {})
    last = state.scene or state.last_scene
    pending = [c["id"] for c in pause.choices if "id" in c] if pause else []
    # 12.2.2: PENDING_ANSWER answers a pause point; with none open (no `pending_answer` field) it is not offered
    classes = [c for c in pacing.get("input_classes", []) if pending or c != "PENDING_ANSWER"]
    return SchemaContext(
        message=message,
        options=list(options),
        own_words_classes=list(own_words_classes),
        lines_and_veils=lines_and_veils,
        scene_ids=scope,
        fact_ids=facts,
        pc_licences=[x.license_id for x in state.licenses.get(pc, [])] if pc else [],
        licences=list(rules.licenses),
        reachable_places=_reachable(state),
        pending_choice_ids=pending,
        input_classes=classes,
        oracle_rungs=[r["id"] for r in res.get("oracle", {}).get("rungs", [])],
        verbs=list(rules.basic_verbs),
        anchor_ids=anchor_ids,
        default_anchor=default_anchor,
        knobs=ae["knobs"],
        deltas=ae["deltas"],
        attributes=attributes,
        default_attribute=_verb_attribute(default_anchor, rules) or default_attribute,
        deed_tags=ae["deed_tags"],
        traits=list(res.get("traits", {})),
        dc_tiers=rolling_tiers(rules),
        obstacle_classes=ob_classes,
        opposed_ids=opposed,
        social=social,
        asks_tags=[str(t) for t in (rules.social.get("event_tags") or {}).get("asks") or []],
        cast_ids=cast,
        defender_ids=[i for i in cast if (state.entities[i].data.get("defenses") or {})],
        lever_fact_ids=list(lever_fact_ids) if lever_fact_ids is not None else usable,
        stakes_sources=sources,
        cost_menu_ids=threatened,
        alternate_cost_menu_ids=alternate,
        cost_uncited_ids=uncited,
        cost_tie_order=list(res.get("cost_selection", {}).get("tie_order", [])),
        reach_tie_whole=bool(reach.get("whole", {}).get("tie_break", False)),
        reach_tie_one_factor=bool(reach.get("one_factor", {}).get("tie_break", True)),
        npc_ids=npcs,
        want_ids=wants,
        refusal_ids=refusals,
        npc_action_tags=list(dict.fromkeys(tags)),
        modes=[m["to"] for m in pacing.get("modes", []) if m.get("to") != "previous"],
        previous_mode=last.mode if last else None,
        places=list(places) if places is not None else by_kind("place"),
        current_place=state.scene.place_id if state.scene else None,
        pillars=list(pacing.get("rotation", {}).get("pillars", [])),
        challenge_types=[c["id"] for c in pacing.get("rotation", {}).get("challenge_types", [])],
        known_ids=by_kind("npc", "companion", "adversary", "faction"),
        push_options=list(pacing.get("push", {}).get("candidates", [])) if push_raised else [],
        thread_ids=by_kind("thread"),
        lead_routes=list(pacing.get("lead_injection", {}).get("source_ladder", [])) if lead_fires else [],
        entity_kinds=[k for k in get_args(EntityKind) if k != "pc"],
        element_kinds=list((pacing.get("claim_check") or {}).get("element_tiers") or {}),
        speaker_ids=[i for i in cast if i != pc and state.entities[i].kind in ("npc", "companion", "adversary")],
        narrator_refs=list(facts),
        claim_classes=list(pacing.get("claim_check", {}).get("classes", [])),
        sentence_ids=[str(i) for i, _ in enumerate(draft_sentences)],
    )


NUMERIC_ALLOWED = ("player_quantity",)


def numeric_fields(schema: Mapping[str, Any], path: str = "$") -> list[str]:
    """Paths of numeric fields (INV-3 check): integer/number types or numeric bounds outside `player_quantity`."""
    found: list[str] = []
    t = schema.get("type")
    types = t if isinstance(t, list) else [t]
    if any(x in ("integer", "number") for x in types) or "minimum" in schema or "maximum" in schema:
        found.append(path)
    for k, sub in schema.get("properties", {}).items():
        if k in NUMERIC_ALLOWED:
            continue
        found.extend(numeric_fields(sub, f"{path}.{k}"))
    if isinstance(schema.get("items"), Mapping):
        found.extend(numeric_fields(schema["items"], f"{path}[]"))
    for key in ("anyOf", "oneOf", "allOf"):
        for i, sub in enumerate(schema.get(key, [])):
            found.extend(numeric_fields(sub, f"{path}<{key}{i}>"))
    return found
