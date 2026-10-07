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

from collections.abc import Callable, Iterable, Mapping
from typing import Any, get_args

from pydantic import BaseModel, Field

from engine.llm.base import Role
from engine.retrieve.anchors import verb_anchor
from engine.retrieve.scene import pc_id, scene_facts, scene_scope
from engine.store.events import EntityKind
from engine.store.projection import WorldState

Schema = dict[str, Any]

# Closed lists the rules state in prose (no data file carries them).
SHAPES = ("single", "sequential", "repeated", "bundled", "conditional", "extended")  # 01.2.2
GATES = ("G0", "G1", "G2", "G3", "G4")  # 01.3.1
NECESSITY = ("uncertain_and_costly", "riding", "trivial", "good_idea", "impossible", "take_the_time",
             "certain_with_cost")  # 01.4.1
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
    cast_ids: list[str] = Field(default_factory=list)
    lever_fact_ids: list[str] = Field(default_factory=list)
    stakes_sources: list[str] = Field(default_factory=list)
    cost_menu_ids: list[str] = Field(default_factory=list)
    alternate_cost_menu_ids: list[str] = Field(default_factory=list)
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
    # Narrator
    entity_kinds: list[str] = Field(default_factory=list)
    # Checker
    claim_classes: list[str] = Field(default_factory=list)
    sentence_ids: list[str] = Field(default_factory=list)


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
    })


def reader_schema(ctx: SchemaContext) -> Schema:  # rule: 12.2.2
    beat = obj({
        "intent": STR,
        "method": STR,
        "assertion": STR_OR_NULL,
        "shape": enum(SHAPES),
        "target": enum(ctx.scene_ids, first=NONE),
        "verb": enum(ctx.verbs),
        "license": enum(ctx.pc_licences, first=NONE),
        "gate": enum(GATES),
        "g4_fact": enum(ctx.fact_ids, nullable=True),
        "necessity": enum(NECESSITY),
        "intent_verbs": STRS,
    })
    return obj({
        "parts": arr(obj({"text": STR, "class": enum(ctx.input_classes)})),
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


def _cost(menu: list[str], facts: list[str]) -> Schema:
    # 01.13.1 / lead decision (a): a cost may cite the scene fact that is its source (frame_check needs either
    # the citation or a structural fit through state); dropped when the scene has no fact
    return obj({"menu_id": enum(menu), "form_intent": STR, "source_fact": enum(facts, nullable=True)})


def framer_schema(ctx: SchemaContext) -> Schema:  # rule: 01.5.1
    facts = ctx.fact_ids
    delta = obj({"knob": enum(ctx.knobs), "delta": enum(ctx.deltas), "cites_fact": enum(facts)})
    return obj({
        "anchor": enum(ctx.anchor_ids),
        "deltas": arr(delta, max_items=2) if ctx.deltas else None,  # 01.5.3: two changes at most
        "attribute": enum(ctx.attributes),
        "deed_tag": enum(ctx.deed_tags),
        "traits": arr(enum(ctx.traits)),
        "obstacle": obj({
            "kind": enum(OBSTACLE_KINDS),
            "tier": enum(ctx.dc_tiers, nullable=True),
            "entity": enum(ctx.cast_ids, nullable=True),
        }),
        "levers": arr(enum(ctx.lever_fact_ids), max_items=2),  # 01.6.8
        "snags": arr(enum(facts), max_items=2),
        "stakes_source": enum(ctx.stakes_sources, first=NONE),  # 01.6.9
        "stakes_heavy": BOOL,
        "lethal": BOOL,
        "reach_whole": BOOL,  # 01.6.10
        "reach_one_factor": BOOL,
        "threatened_cost": _cost(ctx.cost_menu_ids, facts),  # 01.6.11, 01.13.1
        "alternate_cost": nullable(_cost(ctx.alternate_cost_menu_ids or ctx.cost_menu_ids, facts)),
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


def narrator_schema(ctx: SchemaContext) -> Schema:  # rule: 00.6.6
    return obj({
        "fiction": STR,
        "mentions": arr(obj({
            "kind": enum(ctx.entity_kinds),
            "name": STR,
            "implied": arr(obj({"predicate": STR, "value": STR})),
            "unsettled": STRS,
        })),
    })


def checker_schema(ctx: SchemaContext) -> Schema:  # rule: 12.3.1
    claim = obj({
        "sentence": enum(ctx.sentence_ids),
        "subject": enum([*ctx.scene_ids, "unknown"]),
        "class": enum(ctx.claim_classes),
        "predicate": STR,
        "value": STR,
        "asserts_change": BOOL,
        "pc_words_or_feelings": BOOL,
    })
    return obj({
        "claims": arr(claim),
        "screen": obj({  # no safety field: the safety screen is separate (FR-036)
            "intent_acknowledged": BOOL,
            "intent_substituted": BOOL,
            "next_step_exists": BOOL,
            "mechanics_in_fiction": STRS,
            "ends_on_prompt_or_one_pause": BOOL,
        }),
    })


BUILDERS: dict[Role, Callable[[SchemaContext], Schema]] = {
    Role.INTERPRET: interpret_schema,
    Role.READER: reader_schema,
    Role.FRAMER: framer_schema,
    Role.WORLD: world_schema,
    Role.DIRECTOR: director_schema,
    Role.NARRATOR: narrator_schema,
    Role.CHECKER: checker_schema,
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
    return {"choice": "move_on", "own_words_class": None, "own_words_text": None, "lines_and_veils": []}


def _reader_default(ctx: SchemaContext) -> dict[str, Any]:
    # 12.2.2: SPEECH vs DECLARATION ties go to DECLARATION; no beats are guessed
    return {
        "parts": [{"text": ctx.message, "class": "DECLARATION"}] if ctx.message.strip() else [],
        "pending_answer": None, "fact_questions": [], "beats": [], "clarifying_question": None,
        "restatement": ctx.message, "player_quantity": None,
    }


def _framer_default(ctx: SchemaContext) -> dict[str, Any]:
    # 00.15.3: the basic verb's anchor; 01.6.1: the anchor's default attribute; stakes none -> safe
    tier = _first(ctx.dc_tiers, "moderate")
    menu = _first(ctx.cost_menu_ids, *ctx.cost_tie_order)
    return {
        "anchor": _first(ctx.anchor_ids, ctx.default_anchor),
        "deltas": [],
        "attribute": _first(ctx.attributes, ctx.default_attribute),
        "deed_tag": _first(ctx.deed_tags),
        "traits": [],
        "obstacle": {"kind": "tier", "tier": tier, "entity": None},
        "levers": [], "snags": [],
        "stakes_source": NONE, "stakes_heavy": False, "lethal": False,
        "reach_whole": ctx.reach_tie_whole, "reach_one_factor": ctx.reach_tie_one_factor,
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
    wants_v = state.fact_value(npc, "wants") or data.get("wants", []) or []
    refusals_v = state.fact_value(npc, "refusals") or data.get("refusals", []) or []
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
) -> SchemaContext:
    """The enums for this call, from the rules and the current state (scene-scoped; bounded)."""
    scope = scene_scope(state)
    facts = [f.id for f in scene_facts(state, scope)]
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
    return SchemaContext(
        message=message,
        options=list(options),
        own_words_classes=list(own_words_classes),
        lines_and_veils=lines_and_veils,
        scene_ids=scope,
        fact_ids=facts,
        pc_licences=[x.license_id for x in state.licenses.get(pc, [])] if pc else [],
        pending_choice_ids=[c["id"] for c in pause.choices if "id" in c] if pause else [],
        input_classes=list(pacing.get("input_classes", [])),
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
        dc_tiers=[t["id"] for t in res.get("dc_tiers", [])],
        cast_ids=cast,
        lever_fact_ids=list(lever_fact_ids) if lever_fact_ids is not None else facts,
        stakes_sources=list(res.get("stakes_flags", {}).get("source", {}).get("sources", [])),
        cost_menu_ids=threatened,
        alternate_cost_menu_ids=alternate,
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
