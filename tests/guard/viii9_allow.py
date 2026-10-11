"""Spec 033 P0: the reviewed allow-list of the static VIII.9 guard (tests/guard/test_viii9_static.py).

Every place a function reachable from a dm-tools turn reads text with words (a `re` call, a module-level compiled
pattern, a module-level list of three or more string literals) is listed here once, keyed
`module -> "function:rule:name"`, with a class and a reason:

    P  parses a code-made string: an id, a rule atom, the cost DSL, a table range; or a table or enum of code ids
    F  formats text for the player or the DM; it decides nothing about the story
    S  keyword search that lists candidates; the DM model judges, a match never decides
    pending:<phase>  a word matcher or a guess that the named spec 033 phase removes (P2a P2b P3 P4 P5)

Constitution VIII.9 (code never deduces the story) allows P, F and S. From P6 (`STRICT = True`) any `pending` fails.
A phase that removes the code also removes its entries here: an entry the scanner no longer finds is stale and fails.
New code that reads words must be listed with a class, or (better) not exist.
"""

from __future__ import annotations

STRICT = False  # P6 sets this True: no `pending:*` entry may remain

ALLOW: dict[str, dict[str, tuple[str, str]]] = {
    "engine.abilities.recharge": {
        "refreshed_by:words:LADDER": ("P", "enum or table of code ids"),
    },
    "engine.audit.claims": {
    },
    "engine.audit.declare": {
    },
    "engine.audit.fallback": {
        "fact_sentence:pattern:_RAW": ("F", "sentence for a fact line"),
        "fact_sentence:re:sub": ("F", "sentence for a fact line"),
        "fact_sentence:words:_AUX": ("F", "sentence for a fact line"),
        "fact_sentence:words:_BOOL": ("F", "sentence for a fact line"),
        "fact_sentence:words:_IS_PREDS": ("F", "sentence for a fact line"),
    },
    "engine.audit.text": {
    },
    "engine.data.loader": {
        "Rules.collection:words:_MAIN_KEY": ("P", "enum or table of code ids"),
    },
    "engine.dm.codex": {
        "_known:words:NOT_KNOWLEDGE": ("S", "recall: lists what the record holds; the DM judges"),
        "_pieces:pattern:_SPLIT": ("S", "recall: lists what the record holds; the DM judges"),
        "_stems:re:findall": ("S", "recall: lists what the record holds; the DM judges"),
        "_stems:words:STOP": ("S", "recall: lists what the record holds; the DM judges"),
        "what_you_know:words:GENERAL": ("S", "recall: lists what the record holds; the DM judges"),
    },
    "engine.dm.dm_tools": {
        "_along:re:split": ("P", "parses a code-made string (cost DSL, rule atom, table range, id, slug, list of ids)"),
        "_change:pattern:_ID_LIKE": ("P", "pattern over code-made ids"),
        "_change:words:CHANGES": ("P", "enum or table of code ids"),
        "_change:words:dm.turn.REST_WORDS": ("P", "enum or table of code ids"),
        "_condition:words:HARM_OWNED": ("P", "enum or table of code ids"),
        "_give:words:resolve.change.PEOPLE": ("P", "enum or table of code ids"),
        "_give:words:resolve.change.THINGS": ("P", "enum or table of code ids"),
        "_held_mood:words:MOOD": ("P", "enum or table of code ids"),
        "_walk_on:pattern:_ID_LIKE": ("P", "pattern over code-made ids"),
        "_walk_on:words:PRONOUNS": ("P", "enum or table of code ids"),
        "schema_for:words:AS_KINDS": ("P", "enum or table of code ids"),
        "schema_for:words:CHANGES": ("P", "enum or table of code ids"),
        "schema_for:words:COSTS": ("P", "enum or table of code ids"),
        "schema_for:words:FAIL_COSTS": ("P", "enum or table of code ids"),
        "schema_for:words:GRANTS": ("P", "enum or table of code ids"),
        "schema_for:words:STAKES": ("P", "enum or table of code ids"),
    },
    "engine.dm.dm_world": {
        "time_jumped:words:JUMPS": ("P", "enum or table of code ids"),
        "world_step:words:IDLE": ("P", "enum or table of code ids"),
    },
    "engine.dm.fixer": {
        "_entity_tool:words:retrieve.scene.CAST_KINDS": ("P", "enum or table of code ids"),
        "_names:pattern:_ENTITY_ID": ("P", "pattern over code-made ids"),
        "_search_tool:re:findall": ("S", "recall: keyword search over the record; the DM judges"),
        "_search_tool:re:split": ("S", "recall: keyword search over the record; the DM judges"),
        "visible:words:SKIP_PREDICATES": ("P", "enum or table of code ids"),
    },
    "engine.dm.mentions": {
    },
    "engine.dm.narration": {
        "_for_beat:re:sub": ("F", "block layout for the player"),
        "_for_beat:words:_PER_BEAT": ("F", "block layout for the player"),
        "turn_blocks:words:_PAUSE_ITEM": ("F", "block layout for the player"),
    },
    "engine.dm.oof": {
        "_chance_line:words:SEVERITY_WORDS": ("F", "out-of-fiction text for the player's menus and lines"),
        "_cost_clause:words:COST_WORDS": ("F", "out-of-fiction text for the player's menus and lines"),
        "_price:words:SEVERITY_WORDS": ("F", "out-of-fiction text for the player's menus and lines"),
        "changed_line:words:_SHOWN_QTY": ("F", "out-of-fiction text for the player's menus and lines"),
        "fact_short:pattern:_DATA_ID": ("F", "out-of-fiction text for the player's menus and lines"),
        "fact_short:re:sub": ("F", "out-of-fiction text for the player's menus and lines"),
        "fact_short:words:_DETAIL_VERB": ("F", "out-of-fiction text for the player's menus and lines"),
        "fact_short:words:_PEOPLE": ("F", "out-of-fiction text for the player's menus and lines"),
        "goal_line:words:_GOAL": ("F", "out-of-fiction text for the player's menus and lines"),
        "goal_line:words:_PEOPLE": ("F", "out-of-fiction text for the player's menus and lines"),
        "goal_line:words:_PREP": ("F", "out-of-fiction text for the player's menus and lines"),
        "goal_line:words:_VERB_GOAL": ("F", "out-of-fiction text for the player's menus and lines"),
        "offer_block:pattern:_DATA_ID": ("F", "out-of-fiction text for the player's menus and lines"),
        "offer_block:words:MODE_WORDS": ("F", "out-of-fiction text for the player's menus and lines"),
        "offer_block:words:REACH_WORDS": ("F", "out-of-fiction text for the player's menus and lines"),
        "offer_block:words:SEVERITY_WORDS": ("F", "out-of-fiction text for the player's menus and lines"),
        "offer_choices:words:OFFER_LABELS": ("F", "out-of-fiction text for the player's menus and lines"),
        "ordered:words:_ORDER": ("F", "out-of-fiction text for the player's menus and lines"),
        "player_words:pattern:_BOOKKEEPING": ("F", "out-of-fiction text for the player's menus and lines"),
        "player_words:pattern:_META": ("F", "out-of-fiction text for the player's menus and lines"),
        "player_words:re:split": ("F", "out-of-fiction text for the player's menus and lines"),
        "result_block:words:DEGREE_NAMES": ("F", "out-of-fiction text for the player's menus and lines"),
        "short_text:re:finditer": ("F", "out-of-fiction text for the player's menus and lines"),
        "short_text:re:split": ("F", "out-of-fiction text for the player's menus and lines"),
    },
    "engine.dm.packet": {
        "people_card:words:_STATION": ("F", "packet card text"),
    },
    "engine.dm.player_text": {
        "second_person:pattern:_SUBJ_VERB": ("F", "second-person rewrite of shown text"),
        "second_person:pattern:_SUBJ_VERB_PC": ("F", "second-person rewrite of shown text"),
        "second_person:re:sub": ("F", "second-person rewrite of shown text"),
    },
    "engine.dm.schemas": {
        "framer_schema:words:NUDGES": ("P", "enum or table of code ids"),
        "framer_schema:words:REQUEST_SIZES": ("P", "enum or table of code ids"),
    },
    "engine.dm.turn": {
        "_rest:words:REST_WORDS": ("P", "enum or table of code ids"),
    },
    "engine.gen._seed_lib": {
        "slug:re:sub": ("P", "parses a code-made string (cost DSL, rule atom, table range, id, slug, list of ids)"),
    },
    "engine.gen.hooks": {
        "_Builder.entry:re:sub": ("F", "template fill of generated lead text"),
        "_Tok.fill:re:sub": ("F", "template fill of generated lead text"),
    },
    "engine.gen.npc": {
    },
    "engine.harm.apply": {
        "shift:words:SEVERITIES": ("P", "enum or table of code ids"),
    },
    "engine.harm.dice": {
        "degree:words:DEGREES": ("P", "enum or table of code ids"),
    },
    "engine.harm.rest": {
        "rest_payload:words:QUALITIES": ("P", "enum or table of code ids"),
        "rest_payload:words:REST_KINDS": ("P", "enum or table of code ids"),
        "rest_payload:words:SITES": ("P", "enum or table of code ids"),
        "rest_refusal:words:REST_KINDS": ("P", "enum or table of code ids"),
        "rest_site:words:SITES": ("P", "enum or table of code ids"),
    },
    "engine.ids": {
        "entity_id:words:ENTITY_PREFIX": ("P", "enum or table of code ids"),
        "parse_counter_id:pattern:_COUNTER_ID": ("P", "pattern over code-made ids"),
        "slug:re:sub": ("P", "parses a code-made string (cost DSL, rule atom, table range, id, slug, list of ids)"),
    },
    "engine.llm.base": {
        "Packet.render:words:SECTION_TITLES": ("P", "enum or table of code ids"),
        "_check:words:_TYPES": ("P", "enum or table of code ids"),
    },
    "engine.resolve.change": {
        "_person:words:PEOPLE": ("P", "enum or table of code ids"),
        "apply_change:words:PEOPLE": ("P", "enum or table of code ids"),
        "apply_change:words:THINGS": ("P", "enum or table of code ids"),
        "current_hold:words:HOLDS": ("P", "enum or table of code ids"),
        "holder_of:words:HOLDER_FACTS": ("P", "enum or table of code ids"),
        "holder_of:words:HOLDER_KEYS": ("P", "enum or table of code ids"),
        "needs_target:words:_ASK": ("P", "enum or table of code ids"),
        "plain:words:LABELS": ("F", "label text"),
        "things_held:words:THINGS": ("P", "enum or table of code ids"),
    },
    "engine.resolve.conflict": {
        "end_hold:words:resolve.change.HOLDS": ("P", "enum or table of code ids"),
        "holds:words:resolve.change.HOLDS": ("P", "enum or table of code ids"),
        "strike_harm:words:harm.apply.SEVERITIES": ("P", "enum or table of code ids"),
    },
    "engine.resolve.costs": {
        "_apply:re:findall": ("P", "parses a code-made string (cost DSL, rule atom, table range, id, slug, list of ids)"),
        "_apply:re:search": ("P", "parses a code-made string (cost DSL, rule atom, table range, id, slug, list of ids)"),
    },
    "engine.resolve.foe_act": {
        "legal_acts:words:resolve.change.HOLDS": ("P", "enum or table of code ids"),
    },
    "engine.resolve.frame": {
        "_atom_true:pattern:_ATOM": ("P", "parses a code-made string (cost DSL, rule atom, table range, id, slug, list of ids)"),
        "_atom_true:re:findall": ("P", "parses a code-made string (cost DSL, rule atom, table range, id, slug, list of ids)"),
        "_frame_check:words:resolve.types.STAKES_LADDER": ("P", "enum or table of code ids"),
        "_reach:words:resolve.types.REACH_LADDER": ("P", "enum or table of code ids"),
        "_stakes:words:resolve.types.STAKES_LADDER": ("P", "enum or table of code ids"),
        "alternatives:words:ATTACK_SIBLINGS": ("P", "enum or table of code ids"),
        "opposed_by:words:OPPOSED_VERBS": ("P", "enum or table of code ids"),
        "opposed_by:words:PEOPLE": ("P", "enum or table of code ids"),
    },
    "engine.resolve.gate": {
        "compute_gate:pattern:_LIC": ("P", "pattern over code-made ids"),
        "forbidden_by_condition:re:match": ("P", "parses a code-made string (cost DSL, rule atom, table range, id, slug, list of ids)"),
    },
    "engine.resolve.necessity": {
        "_present:words:PEOPLE": ("P", "enum or table of code ids"),
        "certain_talk:words:SOCIAL_GOALS": ("P", "enum or table of code ids"),
        "costly:words:PEOPLE": ("P", "enum or table of code ids"),
        "parties_who_would_act:words:PEOPLE": ("P", "enum or table of code ids"),
    },
    "engine.resolve.oracle": {
        "positive:pattern:_NEG": ("F", "reached only by oof.fact_short (a label); the oracle question path is not a turn"),
        "positive:re:sub": ("F", "reached only by oof.fact_short (a label); the oracle question path is not a turn"),
    },
    "engine.resolve.pipeline": {
        "_able:words:_CREATURES": ("P", "enum or table of code ids"),
        "_finish:words:CONTACT": ("P", "enum or table of code ids"),
        "_force_ladder:words:BANDS": ("P", "enum or table of code ids"),
        "_force_ladder:words:_BAND_WORDS": ("P", "enum or table of code ids"),
        "_force_ladder:words:_CREATURES": ("P", "enum or table of code ids"),
        "_folded_hold:words:resolve.change.PEOPLE": ("P", "enum or table of code ids"),
        "_no_roll:words:NO_ROLL_EVIDENCE": ("P", "enum or table of code ids"),
        "_no_roll:words:resolve.types.REACH_VALUE": ("P", "enum or table of code ids"),
        "_progress:words:resolve.types.REACH_VALUE": ("P", "enum or table of code ids"),
        "_span_words:words:time.clock.ROUNDS": ("P", "enum or table of code ids"),
        "band_words:words:_BAND_WORDS": ("P", "enum or table of code ids"),
    },
    "engine.resolve.roll": {
        "degree:words:resolve.types.DEGREES": ("P", "enum or table of code ids"),
        "delivered_reach:words:resolve.types.REACH_VALUE": ("P", "enum or table of code ids"),
    },
    "engine.resolve.tables": {
        "_bounds:re:fullmatch": ("P", "parses a code-made string (cost DSL, rule atom, table range, id, slug, list of ids)"),
    },
    "engine.retrieve.anchors": {
        "natural_key:re:split": ("F", "sort key"),
    },
    "engine.retrieve.scene": {
        "_nameable:words:SPOT_KINDS": ("P", "enum or table of code ids"),
        "_norm:re:sub": ("S", "recall: the codex search names candidates; the DM judges"),
        "alias_index:words:CAST_KINDS": ("P", "enum or table of code ids"),
        "resolve_names:pattern:_PROPER_RUN": ("S", "recall: the codex search names candidates; the DM judges"),
        "resolve_names:re:escape": ("S", "recall: the codex search names candidates; the DM judges"),
        "resolve_names:re:finditer": ("S", "recall: the codex search names candidates; the DM judges"),
        "resolve_names:pattern:_PROPER_RUN": ("pending:P2b", "R10: focus is ids"),
        "resolve_names:re:escape": ("pending:P2b", "R10: focus is ids"),
        "resolve_names:re:finditer": ("pending:P2b", "R10: focus is ids"),
        "scene_facts:words:WRITTEN": ("P", "enum or table of code ids"),
        "written_words:words:WRITTEN": ("P", "enum or table of code ids"),
    },
    "engine.store.conditions": {
        "apply_condition:words:SEVERITIES": ("P", "enum or table of code ids"),
    },
    "engine.store.db": {
        "Store.record_model_call:words:MODEL_CALL_COLUMNS": ("P", "enum or table of code ids"),
    },
    "engine.store.events": {
        "Event._payload:words:PAYLOADS": ("P", "enum or table of code ids"),
    },
    "engine.store.projection": {
        "_position_set:words:_CAST_KINDS": ("P", "enum or table of code ids"),
        "_scene_started:words:_CAST_KINDS": ("P", "enum or table of code ids"),
        "apply_inplace:words:_CARD_EVENTS": ("P", "enum or table of code ids"),
    },
    "engine.store.views": {
        "_scoped:words:_ENTITY_KEYED": ("P", "enum or table of code ids"),
    },
    "engine.text.render": {
        "_verb:words:_MODALS": ("F", "grammar for rendered lines"),
        "forms:words:_IRREGULAR": ("F", "grammar for rendered lines"),
        "forms:words:_MODALS": ("F", "grammar for rendered lines"),
        "relation:words:OMITTED": ("F", "grammar for rendered lines"),
        "relation:words:RELATIONS": ("F", "grammar for rendered lines"),
        "slug_words:re:sub": ("F", "grammar for rendered lines"),
        "who:pattern:_ID": ("F", "grammar for rendered lines"),
    },
    "engine.time.clock": {
        "crossings:words:ROUNDS": ("P", "enum or table of code ids"),
        "crossings:words:TIME_UNITS": ("P", "enum or table of code ids"),
        "day_index:words:ROUNDS": ("P", "enum or table of code ids"),
        "from_rounds:words:ROUNDS": ("P", "enum or table of code ids"),
        "to_rounds:words:ROUNDS": ("P", "enum or table of code ids"),
        "unit_of:words:ROUNDS": ("P", "enum or table of code ids"),
        "unit_of:words:TIME_UNITS": ("P", "enum or table of code ids"),
    },
    "engine.time.handlers.h00": {
        "expired:pattern:_NUMERIC": ("P", "pattern over code-made ids"),
        "expired:words:_RESTS": ("P", "enum or table of code ids"),
    },
    "engine.time.scheduler": {
        "_event_rank:words:EVENT_ORDER": ("P", "enum or table of code ids"),
    },
    "engine.world.pacing": {
        "_reach_value:words:resolve.types.REACH_VALUE": ("P", "enum or table of code ids"),
    },
    "engine.world.scenes": {
        "turn_is_quiet:words:_NOT_WRITES": ("P", "enum or table of code ids"),
    },
    "engine.world.social": {
        "meet_npc:words:_PRESENCE_WEIGHT": ("P", "enum or table of code ids"),
    },
}

PHASES = ("P2a", "P2b", "P3", "P4", "P5")


def flat() -> dict[str, tuple[str, str]]:
    """`module:function:rule:name` -> (class, reason)."""
    return {f"{mod}:{k}": v for mod, entries in ALLOW.items() for k, v in entries.items()}
