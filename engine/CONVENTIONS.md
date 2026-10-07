# Engine conventions (feature 004)

Shared rules for every module in `engine/`. Foundation sections (layout through tests) are maintained by the
foundation worker; other workers append a short section with their module's public API at the end.

## Layout and code rules
- Per plan.md: `engine/data` (rules data), `engine/store` (events, projection, views, clocks, conditions),
  `engine/rng.py`, `engine/ids.py`, `engine/time`, `engine/resolve`, `engine/harm`, `engine/gen`, `engine/dm`,
  `engine/llm`, ... Tests in `tests/engine/` (unit), `tests/golden/`, ... Nothing in `engine/` imports `src/`.
- Python 3.11+, typed, Pydantic v2 for records. ruff + pyright + pytest clean for every file you touch.
- **`# rule: <id>` tags.** Every deterministic (`[D]`) function carries a comment naming the rule it
  implements, on its `def` statement (any line of it) or the first line of the body:
  `def stage(...) -> Stage:  # rule: 00.8.4`. One id per tag;
  several tags are fine. `engine/build/coverage.py` reads them. Look ids up with `python rules/tools/rq.py <id>`.
- Numbers come only from code or `rules/data` (INV-3); no wall-clock time, no `uuid`, no unseeded `random`.

## Ids (`engine/ids.py`)
- Entities get **name ids**: `ids.entity_id(kind, name, taken=tx.state.entities)` -> `npc.tam_harlan`
  (`_2`, `_3` on a clash). Prefixes per kind: pc, npc, foe (adversary), ally (companion), item, loc (place),
  fac, thr, rum, clu, obj. Clock instances: `ids.clock_id(name, taken)` -> `clk.<slug>`.
- Everything else gets **counter ids** from the open transaction: `tx.mint("fact")` -> `fact.7`. Prefixes:
  `ids.FACT` fact, `FRAME` frame, `SCENE` scn, `TURN` turn, `CONDITION_INSTANCE` cinst, `EVIDENCE` evd,
  `RULING` rul, `PAUSE` pause, `BEAT` beat. Counters live in `WorldState.counters` and are advanced by the
  reducers from the ids an event *creates* (`Payload.creates`), so a replay mints the same ids and a reverted
  event's ids are never minted again. Turn ids: `store.new_turn_id()`. Event ids are the event `seq` (int).

## Rules data (`engine/data/loader.py`)
- `rules = load_rules()` -> `Rules` (once per process; YAML parsed once per rules version and pickled to
  `engine/data/_cache/`, so the first load takes ~20 s and later ones ~0.4 s). Fails loudly with
  `RulesDataError` on a parse error or a broken cross-reference (`validate(rules)` lists them).
- Entries are read-only `FrozenDict`s (a dict subclass) and tuples. Access: `rules.get(id)` (any data id),
  `rules.has(id)`, `rules.where(id)`, `rules.ids("cond")`, `rules.doc("travel")` (whole file); typed helpers
  `anchor(id)`, `anchors_for_rule(rule_id)`, `table(tbl_id)` (any file), `condition`, `license`, `ability`,
  `origin`, `kit`, `verb`, `attribute`, `archetype`, `adversary`, `effect`, `boundary_handlers()` (owner order,
  each with `owner`), `severity_units()`; whole files as properties: `resolution`, `harm`, `world_seed`,
  `gen_birth`, `pacing`, `social`, `scales`, `substrate`, `boundaries`, `last_chance`; `{id: entry}`
  collections (main list + owner-blocks): `oracles`, `origins`, `kits`, `licenses`, `abilities`, `conditions`,
  `basic_verbs`, `attributes`, `archetypes`, `adversaries`, `anchors`, `effects`, `tags`.
- `rules_hash()` / `rules.hash`: sha256 of the chapters + `rules/data` (the save stamp; FR-040).
- `KNOWN_DEFECTS` lists data files allowed not to parse (reported in `rules.broken`); empty now.

## Event store (`engine/store/`)
- `Store.create(path, *, seed, milestone=1, config={}, rules_hash=None)` writes the schema and the
  `game_created` event (seed, engine version, rules hash, milestone, config). `Store.open(path)` resumes from the
  latest snapshot plus later events. One SQLite file (WAL) per game; tables exactly data-model.md §1, plus
  `model_calls.attempt`/`extra`/`row_id`, `facts_idx.fact_id`, `turns.record`.
- **Events** (`engine/store/events.py`): `Event.of(type, {payload fields named like event columns}, *,
  source=, rule_id=, turn_id=, beat_id=, **payload)`. Payload models validate at construction; `PAYLOADS`
  maps type -> model. Fact payloads use `{"source": ...}` in the positional dict (the fact's source enum).
  Data-model §2 types plus `quantity_defined`, `license_granted`, `license_revoked`; `tally_settled`,
  `effect_applied/expired`, `offer_created/resolved` are reserved and raise `NotBuiltYet`.
- **Writing.** Only inside a transaction:
  `with store.transaction(turn_id) as tx: seq = tx.add(event)` (`tx.add_all`, `tx.mint`, `tx.peek_seq()`,
  `tx.state`). `tx.add` runs `payload.check(tx.state)` (every id named must exist or be created earlier in the
  same transaction; raises `Rejected`, nothing staged), stamps `turn_id` and `game_time` (current game time)
  and reduces the event in. The block commits in one SQLite transaction; any exception writes nothing and
  restores the RNG. `store.append(events)` is a one-shot transaction. Never UPDATE/DELETE `events` (triggers
  abort). `writes_reverted` re-folds the projection without the reverted seqs (current scene only, DL-12-04).
- **Reading.** `store.state` (the `WorldState` projection; staged events included while a transaction is
  open), `store.events(since=0, until=None, types=None)`, `store.event(seq)`, `store.rebuild()` (from events
  only), `store.fact(subject, predicate, at_seq=None)` (bi-temporal, from `facts_idx`), `store.fact_history`,
  `store.rulings(signature)`, `store.rng_draws()`, `store.model_calls(turn_id)` (latest row per call_id),
  `store.turn(turn_id)`. `WorldState` helpers: `current_fact_id`, `fact_value`, `open_pause()` (what resume
  re-presents), `conditions_on(target)`. Facts about no entity use subject `"world"` (`events.WORLD`).
- **Side tables.** `store.record_model_call(rec)` (any object with `.model_dump()`; written at once, so
  failed turns keep their cost), `store.save_turn(TurnRecord)` (insert or replace; `engine/store/records.py`),
  `store.snapshot()` (also automatic after `scene_ended`).
- **Reducers** (`engine/store/projection.py`): `REDUCERS[type](state, event, payload)` mutate in place;
  `apply(state, ev)` and `fold(state, evs)` are the pure wrappers; `project(events)` rebuilds. A reducer
  never reads rules data, the RNG or the clock: put every computed number in the payload.
- **Views** (`engine/store/views.py`): `narrator_view(state, scope=None)` (sealed items replaced by their
  permitted slice or dropped; no fact `truth`; hidden clocks dropped, sensed clocks without fill; INV-10),
  `codex_view` (shown/available only), `audit_view` (everything), `view(state, name, scope)`. Packet
  builders read only the narrator view. Seal refs: `"<entity>"`, `"<entity>#<data key>"`, `"<fact_id>"`.
- **Clocks** (`engine/store/clocks.py`): `create_clock(state, template, name=, owner=, races_with=)` ->
  `clock_created` event; `tick_clock(state, clock_id, on, reach=, severity=, units=rules.severity_units(),
  row="source"|"auto"|"decay")` -> `TickResult(events, stage, omen, completed, lethal_warning, interrupt,
  completion_effects, pending_links)`. PR-00-3; refuses an unlisted source (`ClockError`).
- **Conditions** (`engine/store/conditions.py`): `apply_condition(state, tx.mint, rules, target, cond_id,
  severity=, duration=, source=)` -> `ConditionResult(events, outcome, instance_id, on_apply, hooks,
  must_narrate, removed)` (PR-00-5 with 00.9.2 stacking, neutralizes, diminishing);
  `remove_condition(state, rules, instance_id, reason)`; `active_conditions(state, target)` (exclusion groups).
- These functions return events; the caller stages them: `tx.add_all(result.events)`.

## RNG (`engine/rng.py`)
- `rng = Rng.for_store(store)`: seeded from `game_created`, replays `rng_draws` (resume draws exactly what an
  unbroken game would), attached so a rolled-back transaction un-draws. Named streams, seeded by
  sha256(f"{seed}:{stream}"): `dice` (checks, default), `oracle`, `tables`, `gen`, `seed`, `npc`.
- `rng.d(sides, purpose)`, `rng.d100(purpose)`, `rng.choice(seq, purpose, table_id=)`,
  `rng.weighted({value: weight} | [(value, weight)], purpose)`, `rng.roll_die("2d6", purpose)`,
  `rng.pick(table, purpose)` -> `(roll, row)` for a data table. Every draw needs a purpose and is logged
  (stream, purpose, sides, table_id, result). Never use `random` directly.

## Tests
- Build a game in a temp dir: `from tests.fixtures.game import new_store, entity`;
  `store = new_store(tmp_path)` (seed 1234, rules hash stamp `TEST_RULES_HASH`), then
  `with store.transaction() as tx: tx.add(entity("pc", "Wren", tx=tx, quantities={"vitality": (10, 0, 10)}))`.
  `load_rules()` is cheap after the first run (disk cache). No network, no paid model in tests.
- Check rebuild equality in any test that writes many events: `assert store.rebuild() == store.state`.

## engine/llm API (T021–T025)
Contract: `specs/004-playable-prototype/contracts/model-calls.md`. Nothing in `engine/llm` imports the store.

- `engine.llm.base`: `Role` (interpret, reader, framer, world, director, narrator, checker); `Outcome`
  (ok, invalid_reasked, defaulted, refused, error); `RoleModel(provider, model, thinking)` = one
  `GameConfig.models` entry; `Packet(instructions, core, cards: list[str], view, exchanges: list[str], message)`
  with `.render()` (stable sections first; the player's message is always `packet.message`);
  `ModelCallRecord` = a `model_calls` row (columns of data-model.md §1 **plus `attempt: int`**, the replay key).
  `request`/`response` are JSON dicts; `response = {"data": parsed|None, "text": raw|None, "error": str|None}`.
  `tokens_in` is UNCACHED input; `tokens_in_cached` separate; thinking billed as output. `call_id` is
  deterministic `call.<turn_id|pre>.<role>.<attempt>` (not unique across a retried turn: latest row wins).
- The one entry point for a role call:
  `call_role(model, role, schema, packet, *, turn_id=None, recorder=None, default=None, check=None) -> CallResult`
  → `CallResult(data: dict, record, attempts, defaulted)`. Validates against `schema`, re-asks once naming
  the failure, then `default` (dict or zero-arg callable) else raises `ModelInvalid`. `check(data) -> list[str]`
  adds caller-side failures (counted like schema failures). `recorder(rec)` gets EVERY call (also refused/
  failed ones) — pass `store.record_model_call`.
- Errors (all `ModelError`, with `.record`): `ModelUnavailable`, `ModelRefused`, `MissingKey`,
  `ReplayDivergence`, `ModelInvalid`.
- `validate(value, schema) -> list[str]`, `schema_hash(schema) -> str` (sha256 of canonical JSON).
  Validator subset: type, enum, const, properties, required, additionalProperties, items, min/maxItems,
  min/maxLength, minimum/maximum, anyOf/oneOf/allOf, local `$ref` (`#/$defs/..`). Pydantic
  `model_json_schema()` output works.
- Models (all implement `StructuredModel.fill(role, schema, packet, *, turn_id, attempt) -> CallResult`,
  unvalidated): `engine.llm.gemini.GeminiModel(models: dict[Role, RoleModel] | None, *, client=None, ...)`
  (raises `MissingKey` at construction with no key; tests inject a fake `client`);
  `engine.llm.replay.ReplayModel(records)` (alias `ReplayAdapter`);
  `engine.llm.offline.OfflineModel()`; `engine.llm.offline.ScriptedModel({Role: [data | Exception |
  callable(schema, packet)]}, fallback=True)` with `.push(role, *items)` and `.calls`.
- Offline hints the DM layer can put in the packet: Director cuts when the packet contains
  `quiet_turns: N` with N ≥ `QUIET_TURNS_TO_CUT` (3). Narrator names come from `name: X` lines in
  `packet.view` (else capitalised phrases there). Entity aliases for Reader/Checker matching come from the id
  itself and text after the id on any packet line (`npc.mara_voss: Mara Voss, the fence`). The Narrator's
  degree words are found in `packet.message` (`success_at_cost`, `near_miss`, ...). The Checker reads the
  draft from `packet.message`.
- `engine.llm.budget`: `cost(record, on=None) -> float` (offline/scripted/replay = 0; gemini-3.8-flash promo
  until 2026-12-31, doubled from 2027-01-01); `SpendTracker(budget_usd=2.0, *, game_usd=0.0)` with
  `.add(rec)`, `.totals(turn_id=None) -> SpendTotals(turn_usd, session_usd, game_usd, budget_usd)`
  (= `game.spend()`), `.over_budget(budget_usd=None)`, `.warning() -> str | None`, `.new_session()`.
  `GeminiModel` fills `record.cost_usd`; never raises over budget.
## engine/build (cards and coverage)
- `from engine.build.compile_cards import load_cards` → `CardIndex`: `get(id) -> RuleCard` (KeyError if missing), `by_tag(tag)` (also returns cards tagged with a parent tag or `any`), `core()` (00.15.4 strict: T-12-1, T-00-1, 00.12.3, 00.3.9, 00.3.14, 00.3.15), iteration, `in`.
- `RuleCard` (frozen): 00.15.2 fields + kind, chapter, section, file, lines, tokens (~len/4), body, `tags_derived`, `.model_judged`.
- 16 ch.01 cards are tagged `core` ("Loads in: core") but are not in `core()`; retrieval decides.
- Rebuild: `python engine/build/compile_cards.py` (`--check` exits 1 when stale). Coverage: `python engine/build/coverage.py --milestone 1 [--list to-build]`; tags are `# rule: <id>` and `# coarse: <id>` comments.

## engine/time API (T015, T016)
- **Clock** (`engine/time/clock.py`): `Timestamp` is the store's (re-exported). Fields nest like the ladder: season
  1..4, week 1..13, day 1..7, watch 0..3 (morning..night), hour 0..5 *within the watch*, interval 0..5, round
  0..99; epoch = Y1 S1 W1 D1 dawn. `to_rounds(ts)`, `from_rounds(n, beat=)`, `advance(ts, n, unit)` (units or
  plurals: "hours"), `crossings(start, end, rounds=False)`, `crossed(start, end, unit)`, `split(rounds)` ->
  {"watch": 2, ...}, `day_index(ts)`, `fmt(ts)`. Modes: `MODES`, `mode_of(state.time.mode)` (anything not a
  00.7.3 mode, e.g. the store default "scene", reads as `free`), `beat_cost(mode, significant=, listed=)`.
- **Scheduler** (`engine/time/scheduler.py`), always inside a transaction: `ctx = TimeContext(tx, rules, rng)`
  (milestone defaults to the game's). `advance_time(ctx, amount, unit, reason, marks=[Mark("rest_long",
  payload, after=rounds|None)], mode=None) -> AdvanceResult(start, target, end, boundaries, interrupt,
  remainder_rounds, unfired; .remainder, .halted_at, .narration)`. `mark_boundary(ctx, boundary, payload)`
  -> `list[BoundaryResult]` (event boundaries only; `beat_end` bumps the beat counter). `set_mode(ctx, mode,
  reason)` (the only way to change `state.time.mode`; marks `mode_change`). Rests: ch.07 advances the rest's
  length with a `Mark` for the completion (an interrupt before it lands in `unfired`). Resume after an
  interrupt with `advance_time(ctx, res.remainder_rounds, "round", ...)`.
- Round boundaries are crossed only in `conflict` mode (round is conflict-only, 00.7.1). On an interrupt the
  scheduler finishes every boundary at that instant (not only the interrupting one), so no boundary is lost.
- **Handlers** (`engine/time/handlers/`): write yours in the owner's stub `hNN.py` with
  `@handler("h.NN.x")`, `def fn(ctx: TimeContext) -> HandlerResult | None`; stage events with `ctx.emit(*events)`
  (stamps the boundary instant and the handler id as source); read `ctx.state`, `ctx.boundary`, `ctx.payload`,
  `ctx.now`. `HandlerResult(summary, interrupt, narration, chain=[(event boundary, payload)], effects)`. Only
  rows whose `interrupting` is not false may interrupt. `MILESTONE_HANDLERS` / `live_handlers(m)` /
  `milestone_of(id)`; a handler not live or not registered logs `handler_skipped` each time it would run.
  Built: `h.00.durations` (conditions: numeric, scene, conflict, until_rest), `h.00.clock_auto`, `h.00.reflection`.

## engine/gen API (T055–T058)
- Generators take `rng: SeedRng` (`engine/gen/_rng.py`; `random.Random(seed)` reproduces the reference sims). Data via `engine/gen/_data.load(name)` (plain dicts).
- `engine.gen.world_seed`: `WorldSeed.from_seed(seed, mode)`; `.answer(qid, value, words=None)` (`ORACLE` hands a question to the oracle), `.missing()`, `.run_step() -> SeedStep(n, name, rule, answers, summary "[SEED n/14] …", vetoed)`, `.veto(question=None)` (once per step), `.run_check()`, `.world() -> SeededWorld`, `.run_all()`, `.next_step`; `questions(n)`. `SeededWorld`: seed, mode, answers, region, places, routes (id, a, b, kind, watches, terrain, known), factions (brief, sealed parts out), cast [NPC], threads, incident (with leads), check, record.
- `engine.gen.birth`: `source_tags(...)`, `circumstance_for(...)`, `birth_draw(rng, src, circumstance, recent=(), element=None) -> BirthDraw` (caller applies effects); `bent_offer(...)`, `answer_bent(state, "accept"|"defer"|"forgo", ...)`.
- `engine.gen.npc`: `walk_on(rng, role=, home=, people=, name_tables=, given_used=, existing_ids=, member_of=, role_tags=) -> NPC`; `promote_recurring`, `promote_principal`, `reaction_roll(rng, modifiers=0, faction_status=None) -> Reaction`; `NPC.from_record(seed_npc)`.
- `engine.gen.adversary`: `improvise(archetype, band, role, variant="standard", name=, adv_id=) -> ImprovisedAdversary` (PR-09-2; single creatures only in M1).
- Precomputed M2 numbers in `engine/gen/data/*.json` (rebuild: `python -m engine.gen.build_tables`).

## engine/retrieve API (T019)
- `engine.retrieve.anchors`: `anchor_candidates(beat, state, rules) -> list[anchor_id]` (≤8; `beat` = a Reader
  beat dict/object: verb, intent_verbs, intent, method, license). Scores per `anchors.yaml#compile.retrieval`
  (intent verb 3 each, deed tag equal/ancestor 2, situation 1); the basic verb's anchor is always first; an
  anchor needs an intent-verb or deed match (situation alone never qualifies). Ties: specificity order, rule id.
  `anchor_menu(ids, rules) -> list[str]` (one line per anchor; pass as `notes=` to the Framer's packet),
  `verb_anchor(verb, rules)`, `mode_tags(mode, rules)` (pacing.yaml#modes), `natural_key(id)`.
- `engine.retrieve.cards`: `load_cards_for(role, situation_tags, mode, triggers, extra_ids, *, rules=None,
  index=None, cap=None) -> list[RuleCard]` (≤12 = `pacing.yaml#packet.max_loaded_cards`). Order: role cards
  (`ROLE_CARDS`) → active triggers' cards → `extra_ids` (anchor cards via `anchor_card_ids(anchors, rules)`,
  rulings, ability/licence data ids become cards) → situation cards (deeper tag first, explicit `Loads in`
  first, rule-id order; only `[J*]`/`[N]` rules and procedures). Checker and Interpret get no trigger or
  situation cards. `core_cards()` = 00.15.4 exactly (`CardIndex.core()`).
  **Decision:** the ch.01 cards tagged `Loads in: core` are NOT core: 00.15.4 says "only these travel with
  every turn". They are the Reader's/Framer's role cards and count toward the 12. Role cards whose marks are
  all `[D]` (01.2.3, 01.2.6, 01.6.4, 01.6.7) are dropped (code runs them; research R5); 01.6.6/01.6.7 are not
  Framer fields. So the Framer has 11 role cards + 1 slot; it sees its anchors through `anchor_menu`.
- `engine.retrieve.triggers`: `get_active_triggers(state, rules=None, *, raised=()) -> list[ActiveTrigger]`
  (id, group, rule_id, cards, subject, fact_id, params; `.line()`), ordered per 12.2.3 groups.
  **To raise a trigger:** write a current fact whose predicate is the trigger id, `kind="flag"`, value `True`
  or a params dict, on `world` or the entity it concerns; lower it by superseding with `False`. Or pass ids
  raised only for this turn in `raised`. `TRIGGERS` registry (every `trg.*` the rules name, plus engine ids
  `trg.safety_flag` 12.5.6, `trg.interrupt` 00.7.8, `trg.clock_stage` 00.8.4 for 12.2.3 groups 1, 2, 4);
  `trigger_cards(active)`.
- `engine.retrieve.scene`: `scene_scope(state)` ([pc, cast_present..., place]), `scene_facts(state, scope=None,
  limit=40)` (narrator-visible, newest first, no `trg.*` flags), `pc_id(state)`, `entity_names(state, ids)`.
  Packets and schema enums both use these, so fact ids offered in an enum are the ones the view shows.

## engine/dm packet + schemas API (T106, T026)
- `engine.dm.packet.build_packet(role, *, instructions, cards, view, exchanges, message, triggers=(),
  quiet_turns=None, notes=(), rules=None, index=None) -> Packet`. `view`: a `WorldState` (→ `scene_view` +
  `render_view`), a view dict, or a string. Core = the 00.15.4 cards + "Active triggers:" list. >12 cards
  raises `PacketError`; only the last 4 (`pacing.yaml#packet.verbatim_exchanges`) exchanges are kept;
  exchanges are strings or `(player, dm)` tuples. `notes` and `quiet_turns: N` lines follow the view.
- The view (`scene_view(state)`) is scene-scoped and capped: scope entities, ≤40 scene facts, ≤8 active
  clocks, ≤8 other threads, ≤12 other cast, ≤12 data keys per entity, values ≤160 chars. Entities render as
  `<id>: <name>` then `  name: <name>`; facts as `<fact id> about <subject>: <predicate> = <value>`.
- `engine.dm.schemas`: `ctx = schema_context(state, rules, *, message="", options=(), own_words_classes=(),
  lines_and_veils=False, anchors=(), beat=None, lever_fact_ids=None, cost_menu_ids=None, places=None,
  push_raised=False, lead_fires=False, draft_sentences=())` → `SchemaContext` (plain lists; tests may build it
  directly). `build_schema(role, ctx)` / `interpret_schema` … `checker_schema`; `defaults(role, ctx)` (valid
  against the schema; None for Narrator and Checker: no rule default); `numeric_fields(schema)` (INV-3 check);
  `fitting_cost_menus(rules, fact_ids)`.
- Schema shape: every object closed, all properties required, optional values nullable; empty enum → field
  dropped; `none` is the first option where allowed. Only numeric field: Reader `player_quantity` (top level).
  Deviations: Checker `Claim.sentence` is a string enum "0".."n-1" (convert with `int()`); World want/refusal
  ids are `<npc>/want.<n>` and `<npc>/refusal.<n>` (1-based, index into the NPC's `data.wants`/`refusals`),
  one enum across NPCs (check ownership in a `check=`). `push` exists only when `push_raised`, `lead` only
  when `lead_fires`. Cost menus: with no scene fact only `cost.twist` fits; `cost.shortfall` is alternate-only.
