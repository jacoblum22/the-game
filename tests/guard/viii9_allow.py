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
        "_pronoun_hit:pattern:_OTHER_ANTECEDENT": ("pending:P4", "reached only from _log_only (R11)"),
        "_pronoun_hit:pattern:_PRONOUN_RE": ("pending:P4", "reached only from _log_only (R11)"),
        "_pronoun_hit:pattern:_TAG_RE": ("pending:P4", "reached only from _log_only (R11)"),
        "_pronoun_hit:words:_NOT_PEOPLE": ("pending:P4", "reached only from _log_only (R11)"),
        "_pronoun_hit:words:_PRONOUN": ("pending:P4", "reached only from _log_only (R11)"),
    },
    "engine.audit.declare": {
        "SceneIndex.of:re:findall": ("pending:P4", "reached only from _log_only (R11)"),
        "_gender:words:_GENDER": ("pending:P4", "reached only from _log_only (R11)"),
        "name_spans:re:escape": ("pending:P4", "reached only from _log_only (R11)"),
        "name_spans:re:finditer": ("pending:P4", "reached only from _log_only (R11)"),
    },
    "engine.audit.fallback": {
        "fact_sentence:pattern:_RAW": ("F", "sentence for a fact line"),
        "fact_sentence:re:sub": ("F", "sentence for a fact line"),
        "fact_sentence:words:_AUX": ("F", "sentence for a fact line"),
        "fact_sentence:words:_BOOL": ("F", "sentence for a fact line"),
        "fact_sentence:words:_IS_PREDS": ("F", "sentence for a fact line"),
    },
    "engine.audit.text": {
        "norm:pattern:_WORD": ("pending:P4", "D40 primitives; their dm-tools callers are P4's (_told, overlap, _log_only)"),
        "norm:re:sub": ("pending:P4", "D40 primitives; their dm-tools callers are P4's (_told, overlap, _log_only)"),
        "words:pattern:_WORD": ("pending:P4", "D40 primitives; their dm-tools callers are P4's (_told, overlap, _log_only)"),
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
        "_along:pattern:_PC_WORDS": ("pending:P4", "R6: `pc` literal"),
        "_along:re:split": ("P", "parses a code-made string (cost DSL, rule atom, table range, id, slug, list of ids)"),
        "_change:pattern:_ID_LIKE": ("P", "pattern over code-made ids"),
        "_change:words:CHANGES": ("P", "enum or table of code ids"),
        "_change:words:dm.turn.REST_WORDS": ("P", "enum or table of code ids"),
        "_change:words:resolve.change.PEOPLE": ("P", "enum or table of code ids"),
        "_condition:words:HARM_OWNED": ("P", "enum or table of code ids"),
        "_content:pattern:_WORD": ("pending:P4", "R11 measure, R6 identity or R8 testimony word matching"),
        "_give:words:resolve.change.PEOPLE": ("P", "enum or table of code ids"),
        "_give:words:resolve.change.THINGS": ("P", "enum or table of code ids"),
        "_held_mood:words:MOOD": ("P", "enum or table of code ids"),
        "_log_only:pattern:_GIVE": ("pending:P4", "R11 measure, R6 identity or R8 testimony word matching"),
        "_log_only:pattern:audit.claims._QUOTE_RE": ("pending:P4", "R11 measure, R6 identity or R8 testimony word matching"),
        "_log_only:re:escape": ("pending:P4", "R11 measure, R6 identity or R8 testimony word matching"),
        "_log_only:re:search": ("pending:P4", "R11 measure, R6 identity or R8 testimony word matching"),
        "_log_only:re:split": ("pending:P4", "R11 measure, R6 identity or R8 testimony word matching"),
        "_log_only:words:_MOVES": ("pending:P4", "R11 measure, R6 identity or R8 testimony word matching"),
        "_name_tokens:pattern:_WORD": ("pending:P4", "R11 measure, R6 identity or R8 testimony word matching"),
        "_party:pattern:_ID_LIKE": ("P", "pattern over code-made ids"),
        "_party:pattern:_NAME": ("pending:P4", "R6: `pc` literal, `as`"),
        "_party:pattern:_PC_WORDS": ("pending:P4", "R6: `pc` literal, `as`"),
        "_party:pattern:dm.npc_layer.ANIMAL": ("pending:P4", "R6: `pc` literal, `as`"),
        "_propose_roll:pattern:_ID_LIKE": ("P", "pattern over code-made ids"),
        "_squash:re:sub": ("pending:P4", "R11 measure, R6 identity or R8 testimony word matching"),
        "_told:pattern:_PC_WORDS": ("pending:P4", "R11 measure, R6 identity or R8 testimony word matching"),
        "_walk_on:pattern:_NAME": ("pending:P4", "R11 measure, R6 identity or R8 testimony word matching"),
        "_walk_on:pattern:dm.npc_layer.ANIMAL": ("pending:P4", "R11 measure, R6 identity or R8 testimony word matching"),
        "schema_for:words:AS_KINDS": ("P", "enum or table of code ids"),
        "schema_for:words:CHANGES": ("P", "enum or table of code ids"),
        "schema_for:words:COSTS": ("P", "enum or table of code ids"),
        "schema_for:words:FAIL_COSTS": ("P", "enum or table of code ids"),
        "schema_for:words:GRANTS": ("P", "enum or table of code ids"),
        "schema_for:words:STAKES": ("P", "enum or table of code ids"),
        "target_kinds:pattern:_PERSON_KIND": ("pending:P4", "R11 measure, R6 identity or R8 testimony word matching"),
        "target_kinds:pattern:_THING_KIND": ("pending:P4", "R11 measure, R6 identity or R8 testimony word matching"),
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
        "_npc:pattern:dm.npc_layer.ANIMAL": ("pending:P4", "R6: write_mentions / find_existing leave dm-tools"),
        "_npc:words:_GENDERS": ("pending:P4", "R6: write_mentions / find_existing leave dm-tools"),
        "_npc:words:_NPC_KEYS": ("pending:P4", "R6: write_mentions / find_existing leave dm-tools"),
        "_npc:words:_PRONOUNS": ("pending:P4", "R6: write_mentions / find_existing leave dm-tools"),
        "_one:words:MENTIONABLE": ("pending:P4", "R6: write_mentions / find_existing leave dm-tools"),
        "_proper:pattern:_ARTICLE": ("pending:P4", "R6: write_mentions / find_existing leave dm-tools"),
        "bare:pattern:_ARTICLE": ("pending:P4", "R6: write_mentions / find_existing leave dm-tools"),
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
        "price_line:words:COST_WORDS": ("F", "out-of-fiction text for the player's menus and lines"),
        "price_line:words:SEVERITY_WORDS": ("F", "out-of-fiction text for the player's menus and lines"),
        "redirect_block:words:_LEARN": ("F", "out-of-fiction text for the player's menus and lines"),
        "result_block:words:DEGREE_NAMES": ("F", "out-of-fiction text for the player's menus and lines"),
        "short_text:re:finditer": ("F", "out-of-fiction text for the player's menus and lines"),
        "short_text:re:split": ("F", "out-of-fiction text for the player's menus and lines"),
        "to_player:re:escape": ("F", "out-of-fiction text for the player's menus and lines"),
        "to_player:re:search": ("F", "out-of-fiction text for the player's menus and lines"),
        "to_player:re:sub": ("F", "out-of-fiction text for the player's menus and lines"),
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
        "clue_schema:words:CLUE_ITEMS": ("P", "enum or table of code ids"),
        "clue_schema:words:CLUE_PARTS": ("P", "enum or table of code ids"),
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
        "role_implies:pattern:_NEGATED": ("pending:P4", "census find: role words imply age and pronouns; `as` replaces it"),
        "role_implies:re:search": ("pending:P4", "census find: role words imply age and pronouns; `as` replaces it"),
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
        "_person:words:PEOPLE": ("pending:P2a", "R1: no goal from the verb, no name resolution"),
        "apply_change:words:PEOPLE": ("P", "enum or table of code ids"),
        "apply_change:words:THINGS": ("P", "enum or table of code ids"),
        "current_hold:words:HOLDS": ("P", "enum or table of code ids"),
        "holder_of:words:HOLDER_FACTS": ("P", "enum or table of code ids"),
        "holder_of:words:HOLDER_KEYS": ("P", "enum or table of code ids"),
        "needs_target:words:_ASK": ("P", "enum or table of code ids"),
        "plain:words:LABELS": ("F", "label text"),
        "things_held:words:THINGS": ("P", "enum or table of code ids"),
        "typed_goal:words:PEOPLE": ("pending:P2a", "R1: no goal from the verb, no name resolution"),
        "typed_goal:words:_VERB_GOAL": ("pending:P2a", "R1: no goal from the verb, no name resolution"),
    },
    "engine.resolve.conflict": {
        "end_hold:words:resolve.change.HOLDS": ("P", "enum or table of code ids"),
        "foe_beat:words:BANDS": ("pending:P3", "R3: the DM picks the foe's act"),
        "holds:words:resolve.change.HOLDS": ("P", "enum or table of code ids"),
        "strike_harm:pattern:NONLETHAL": ("pending:P2a", "R5: the DM's weapon and lethality"),
        "strike_harm:words:harm.apply.SEVERITIES": ("P", "enum or table of code ids"),
        "weapon:pattern:UNARMED": ("pending:P2a", "R5: the DM's weapon and lethality"),
        "weapon:re:escape": ("pending:P2a", "R5: the DM's weapon and lethality"),
        "weapon:re:search": ("pending:P2a", "R5: the DM's weapon and lethality"),
    },
    "engine.resolve.costs": {
        "_apply:re:findall": ("P", "parses a code-made string (cost DSL, rule atom, table range, id, slug, list of ids)"),
        "_apply:re:search": ("P", "parses a code-made string (cost DSL, rule atom, table range, id, slug, list of ids)"),
    },
    "engine.resolve.frame": {
        "_frame_check:words:resolve.types.STAKES_LADDER": ("P", "enum or table of code ids"),
        "_reach:words:resolve.types.REACH_LADDER": ("P", "enum or table of code ids"),
        "_stakes:words:resolve.types.STAKES_LADDER": ("P", "enum or table of code ids"),
        "alternatives:words:ATTACK_SIBLINGS": ("P", "enum or table of code ids"),
        "lift_attribute:re:search": ("pending:P2b", "R7: lift, attribute, reversal"),
        "lift_or_carry:pattern:_LIFT": ("pending:P2b", "R7: lift, attribute, reversal"),
        "lift_or_carry:words:_LIFT_VERBS": ("pending:P2b", "R7: lift, attribute, reversal"),
        "opposed_by:words:OPPOSED_VERBS": ("P", "enum or table of code ids"),
        "opposed_by:words:PEOPLE": ("P", "enum or table of code ids"),
        "reverses:words:_REVERSES": ("pending:P2b", "R7: lift, attribute, reversal"),
    },
    "engine.resolve.gate": {
        "compute_gate:pattern:_LIC": ("P", "pattern over code-made ids"),
        "forbidden_by_condition:re:match": ("P", "parses a code-made string (cost DSL, rule atom, table range, id, slug, list of ids)"),
        "reads_writing:pattern:LOOKS_AT": ("pending:P2b", "R7: reads / exclusion are DM fields"),
        "reads_writing:pattern:WRITING": ("pending:P2b", "R7: reads / exclusion are DM fields"),
        "reads_writing:pattern:retrieve.scene.READING": ("pending:P2b", "R7: reads / exclusion are DM fields"),
        "words:re:findall": ("pending:P2b", "R7: reads / exclusion are DM fields"),
        "words:words:_STOP": ("pending:P2b", "R7: reads / exclusion are DM fields"),
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
        "_cleanse:pattern:_FREEING": ("pending:P2a", "R1: positions come from the DM"),
        "_contact:pattern:_DOWN": ("pending:P2a", "R1: positions come from the DM"),
        "_contact:words:BANDS": ("pending:P2a", "R1: positions come from the DM"),
        "_contact:words:_BAND_WORDS": ("pending:P2a", "R1: positions come from the DM"),
        "_contact:words:_CREATURES": ("pending:P2a", "R1: positions come from the DM"),
        "_finish:words:CONTACT": ("P", "enum or table of code ids"),
        "_folded_hold:words:resolve.change.PEOPLE": ("P", "enum or table of code ids"),
        "_moved:words:BANDS": ("pending:P2a", "R1: positions come from the DM"),
        "_moved:words:_AWAY": ("pending:P2a", "R1: positions come from the DM"),
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
        "_intent_hits:re:escape": ("pending:P2b", "R10: the anchor is the verb's card id"),
        "_intent_hits:re:search": ("pending:P2b", "R10: the anchor is the verb's card id"),
        "_norm:re:sub": ("pending:P2b", "R10: the anchor is the verb's card id"),
        "natural_key:re:split": ("F", "sort key"),
    },
    "engine.retrieve.scene": {
        "_nameable:words:SPOT_KINDS": ("P", "enum or table of code ids"),
        "_norm:re:sub": ("pending:P2b", "R10: focus is ids"),
        "alias_index:words:CAST_KINDS": ("P", "enum or table of code ids"),
        "focus_ids:re:escape": ("pending:P2b", "R10: focus is ids"),
        "focus_ids:re:search": ("pending:P2b", "R10: focus is ids"),
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
