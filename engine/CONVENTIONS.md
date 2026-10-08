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
  Beat ids (minted by the Reader, created by no payload): the event column `beat_id` advances the `beat`
  counter, and the store keeps the high-water mark of mint-only prefixes (`db.MINT_ONLY` = beat; table `minted`,
  committed with the transaction), so a beat that writes nothing still never repeats, also after a reopen.

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
  `ModelCallRecord` = a `model_calls` row (columns of data-model.md §1 **plus `seq: int` and `attempt: int`**;
  the replay key is (turn_id, role, seq, attempt); `seq` is stored in `extra`, absent = 0).
  `request`/`response` are JSON dicts; `response = {"data": parsed|None, "text": raw|None, "error": str|None}`.
  `tokens_in` is UNCACHED input; `tokens_in_cached` separate; thinking billed as output. `call_id` is
  deterministic `call.<turn_id|pre>.<role>.<seq>.<attempt>`; `seq` = this role's call number in the turn (0, 1,
  2 …: several Framer beats, a "change", a redraft). `call_role` takes it from the recorder's `next_call_seq(
  turn_id, role)` (the recorder or, for a bound method, its owner: `TurnContext.record_call` → the context's
  `CallSequence`), else 0; pass `seq=` to force one. Always pass `recorder=ctx.record_call` in a turn.
- The one entry point for a role call:
  `call_role(model, role, schema, packet, *, turn_id=None, recorder=None, default=None, check=None, seq=None)
  -> CallResult`
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
  `engine.llm.replay.ReplayModel(records)` (alias `ReplayAdapter`; `ReplayModel.from_rows(store.model_calls())`,
  `record_from_row(row)`); `fill(..., turn_id, attempt, seq=0)` on every model;
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
- `engine.llm.gemini_schema`: `to_gemini(schema, *, level=0) -> dict`, `convert(...) -> Converted(schema,
  level, relaxed)`, `problems(schema) -> list[str]`. Converts our schemas to the subset Gemini's
  `response_json_schema` accepts (no `const`/`allOf`/`null` in enums; type unions → anyOf; oversized enums →
  described strings). Level 1 = no enums, level 2 = JSON mode with the schema in the instructions. Only the
  request uses the converted schema; `call_role` validates against the original.
- `engine.llm.gemini` also exposes `build_config`, `max_output_tokens(role, thinking)`, `extract_json`,
  `OUTPUT_TOKENS`, `THINKING_ALLOWANCE`. `max_output_tokens` includes thinking tokens. A 400 schema rejection
  relaxes the level for that role for the rest of the session; MAX_TOKENS truncation retries once at double
  the cap. The record's `request` carries `schema_level`, `schema_relaxed`, `schema_rejected`.
  `evals/gemini_smoke.py` is the owner-run live check (`--dry-run` sends nothing).
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
- **Seed packs** (spec 008 A; `engine.gen._seed_packs`, a draw-for-draw port of `12-world-seed.py#seed_packs`):
  `WorldSeed.record()` packs the record after step 13 on streams `keyed(seed, entity id, purpose)`: place `look`,
  `furniture`, `exits` (place data; `packet.scene_setting` shows the present place's); NPC `knowledge` (sealed field:
  PR-12-10 tells it) and `stance`; `documents` (things with a `text` fact at `at`); `walk_ons`; `seed_cases`.
  `check_seed` runs the 7 `#pack_requirements` rows after the 64 (a failing one re-runs from step 13).
  `seed_flow.write_world` -> `case.write_seeded` puts walk-ons, documents and meta `world.cases` in the store.
- **Reduced case** (`engine.gen.case`, PR-15-6 reduced profile): `reduced_case(reg, seed, option, place,
  lead_target, tag)`, `validate_case(case) -> [failures]`, `cases(state)`, `story_option(words)`,
  `case_covering(state, words)`, `case_for_question(tx, words, place, lead_target=None)` (on demand, writes),
  `pointer(case, node_id=None, asked=, state=)` (the core holder first), `mark_found(tx, case, node, placement,
  fact_id=)`, `audit_cases(tx, emit=)` (= `h.15.placement_audit`, live from M1), `world_rec(state)` (a region-record
  view of the store). Case records are never rendered.
- **Casting** (`engine.gen.cast`, 00.11.1 `cast`): `cast(state, role, *, scope, topic=None, asker=None, exclude=(),
  faction=None, gate=True) -> npc id | None`, `pointer_target(state, topic, *, scope, asker=None) -> (kind, ref)`,
  `base_pool(state, pc)` (the gate; `incident._people` is an alias), `alive`, `home_of`, `settlement_of`. Picks are
  keyed by the game seed and the question (the same question casts the same person).
- `engine.dm.incident`: `incident_line(state)` (the incident case as the PC knows it), `start_knowledge(ctx, tx)`
  (I-149, at each character's opening), `settle_who` (story roles from the case, else casting; part B replaces it).

## engine/retrieve API (T019)
- `engine.retrieve.anchors`: `anchor_candidates(beat, state, rules) -> list[anchor_id]` (≤8; `beat` = a Reader
  beat dict/object: verb, intent_verbs, intent, method, license). Scores per `anchors.yaml#compile.retrieval`
  (intent verb 3 each, deed tag equal/ancestor 2, situation 1); the basic verb's anchor is always first; an
  anchor needs an intent-verb or deed match (situation alone never qualifies). Ties: specificity order, rule id.
  `anchor_menu(ids, rules) -> list[str]` (one line per anchor; pass as `notes=` to the Framer's packet),
  `verb_anchor(verb, rules)`, `mode_tags(mode, rules)` (pacing.yaml#modes), `natural_key(id)`.
- `engine.retrieve.cards`: `load_cards_for(role, situation_tags, mode, triggers, extra_ids, *, rules=None,
  index=None, cap=None) -> list[RuleCard]` (≤12 = `pacing.yaml#packet.max_loaded_cards`). Chosen under the cap
  in priority order: role cards (`ROLE_CARDS`) → active triggers' cards → `extra_ids` (anchor cards via
  `anchor_card_ids(anchors, rules)`, rulings, ability/licence data ids become cards) → situation cards (deeper
  tag first, explicit `Loads in` first, rule-id order; only `[J*]`/`[N]` rules and procedures); returned stable
  to volatile for prompt caching: role, situation, trigger, extra (DL-12-38). Checker and Interpret get no
  trigger or situation cards. `core_cards()` = 00.15.4 exactly (`CardIndex.core()`).
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
- `engine.retrieve.scene` (12.2.4 item 3; budgets `view_budget(rules)` = `pacing.yaml#packet.view_budget`, in
  `tokens(text)` ≈ chars/4): `scene_scope(state, budget=None)` ([pc, cast_present..., place, things at the
  place: those with written words always, the rest newest first within `things`]); `scene_facts(state,
  scope=None, *, focus=(), budget=None)` = pins (open commitments, written words, active NPC memories; never
  archived ones, 12.11.7) within `pinned`, then the rest ranked by salience + recency (per scene) + relevance
  (+2: subject/value in `focus`) + adjacency (+1) within `facts`; no `trg.*` flags. `focus_ids(state, text,
  target)` = the beat target + entities named in the message: pass the same ids to `schema_context(focus=)` and
  `build_packet(focus=)`. `cast_order(state, people, focus)` ranks the people present for a full profile (focus,
  most recent dealings, 12.6.6 weight); `also_here(labels, room, ids=True)` is the capped compact line for the
  rest (`view_budget.cast` / `cast_line`, R2-A2). `fit(rows, cost, room)`, `pc_id(state)`, `entity_names(state, ids)`. Packets and schema
  enums both use these, so fact ids offered in an enum are the ones the view shows.

## engine/dm packet + schemas API (T106, T026)
- `engine.dm.packet.build_packet(role, *, instructions, cards, view, exchanges, message, triggers=(),
  quiet_turns=None, notes=(), focus=(), rules=None, index=None) -> Packet`. `view`: a `WorldState` (→
  `scene_view` + `render_view`), a view dict, or a string. Core = the 00.15.4 cards only (identical on every
  call); the "Active triggers:" list (`render_triggers`) heads the view (DL-12-38). >12 cards
  raises `PacketError`; only the last 4 (`pacing.yaml#packet.verbatim_exchanges`) exchanges are kept;
  exchanges are strings or `(player, dm)` tuples. `notes` and `quiet_turns: N` lines follow the view.
- The view (`scene_view(state, focus=())`) is scene-scoped and token-budgeted per section
  (`pacing.yaml#packet.view_budget`): scope entities, pinned + ranked facts, active clocks (newest), other
  active threads and known cast (by 12.6.6 weight, then newest), ≤12 data keys per entity, values ≤160 chars.
  Entities render as
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
  Framer: both cost objects carry `source_fact` (nullable enum of the scene fact ids; dropped with no fact).
  `attribute` (01.6.1, as frame_check step 4 allows): the default first (the default anchor's attribute knob,
  else its verb's / the beat's verb's `attribute`, else the beat licence's), then knob deltas, the verbs'
  `alt_attributes`, the licence's attribute; every attribute when a verb is `by_method`/`by_license`, the
  licence has none fixed, or an anchor has neither verb nor knob. `schema_context` reads `beat.verb` and
  `beat.license`.

## engine/resolve API (T028–T037; the `[D]` steps of PR-01-1)
Records in `engine.resolve.types`: `Beat` (Reader beat + gate proposal: gate, verb, license, mode, method_class,
g4_fact/g4_test, would_be_license, fallback_license, traits, deed_tag, `declared_seq` = last seq before the
declaration; levers/snags/delta facts must be no newer), `ProposedFrame` (= FramerOutput + `trade`,
`attribute_tie`, `repetition_instance`; levers/snags are `LeverCite` or a bare fact id = Precision; `Obstacle`
adds `id` (stored-DC key), `defense` (attribute, or a named defense in `entity.data.defenses`, e.g. guard),
`defense_tag`, `entities`, `severity` (hazard); `CostDecl.source_fact` optional), `Frame`, `FrameRefusal(step,
field, reason; .message)`, `Odds`, `OfferPreview` (= OfferView), `RollResult`, `ReadResult`.
Entity data read: `data.attributes {attr: int}`, `data.competence {tag: int}` (or `[{tag, value}]`; PCs get the
`deed` floor from scales.yaml), `data.edge` (int), `data.defenses {name: int}`. Lethal context = a current fact
with predicate `lethal_context` (truthy), on any subject, recorded before the declaration (harm module writes it).
- `gate.check_gate(beat, *, state, rules, store=None, staged=(), mint=None, canon_impossible=(),
  alternatives=[RedirectOption]) -> GateDecision(gate, verb, license, mode, reason, fact_cited, redirect,
  precedent, events, .rolls_possible)`. Calls `find_rulings` first for G3/G4; with `mint` the `ruling_logged`
  (g3_redirect / g4; plus rule_conflict when no license covers it) is in `events`. Redirect: `missing` (id
  checked), `options` (≥1; crude fallback first), `acquisition_paths`. G4 test 4 (condition restricts) is
  answered from state whatever was proposed. An accepted fallback: `Beat(gate="G3", mode="fallback",
  fallback_license=<lic>, verb=<its fallback verb>)`.
- `frame.frame_check(proposed, beat, *, state, rules, gate=None, candidates=None, store=None, staged=()) ->
  Frame | FrameRefusal` (PR-01-2; pure, writes nothing; re-run with `trade` set for go big / play it safe).
  `offer_preview(frame)`, `legal_trades(frame)`, `auto_commit_allowed(frame)` (01.7.4),
  `commit_events(frame, "commit"|"auto", *, mint, state)` -> [stored-DC fact_set, frame_committed] (sets
  `frame.id`, `frame.offer_choice`). Stored DCs: fact on `world`, predicate `stored_dc_key(obstacle, anchor,
  dc_delta)`. Costs without `source_fact` must fit through state (`costs.structural_fit`: stakes source,
  listening clocks with `on: cost.time|cost.exposure`, carried items, quantities, target kind).
- `roll.roll_check(frame | frame_committed dict, rng, on_roll=None) -> RollResult` (refuses an uncommitted or
  illegal frame: `RollRefused`; `on_roll(res) -> True` rerolls once, e.g. fate). `read_result(frame, roll,
  take_success_at_cost=None|bool) -> ReadResult(delivered_reach, cost_severity, cost_choices)` (a near miss
  needs the choice). `degree`, `is_near_miss`, `delivered_reach`. `odds.odds(modifier, dc) -> Odds`.
- `costs.apply_cost(frame, read, menu_id, *, state, rules, mint, form=None, params={}, harm_hook=None, rng=None,
  mode="site") -> CostApplication(events, reach_delta, deferred, refused)`. `harm_hook(target, severity, *,
  lethal, harm_tags, frame_id) -> list[Event]` is engine/harm's; params: item (gear), observer/clock
  (exposure), clock (time; none -> `deferred={"advance_time": row}`), quantity (drain), target/obstacle/
  method_class (closed_door). `refused` = cannot land in full: pick the next candidate (01.13.1).
  `cost_severity(stakes, degree, success_at_cost=)`, `severity_previews(stakes)`.
- `oracle.ask_oracle(OracleQuestion(subject, predicate, odds, asker="dm"|<pc id>, qualifier, sealed, ...), *,
  state, rules, rng, mint, store=None, staged=(), free_cap=None) -> OracleResult(status answered|read|refused,
  shape, answer, d100, extreme, twist (= a but), qualifier, meaning, fact_id, precedent, events)`. Order of
  events: meaning `table_rolled`, `fact_set`s (answer, `<pred>.and`, `<pred>.but`), `oracle_answered` (event
  `source` = asker), `meta_set` `oracle.free_questions.<scene>` and `oracle.free_facts` (player questions only;
  frame_check enforces 01.15.8's free-fact lever caps from it). Over `free_cap` -> refused +
  `meta_set oracle.free_cap_hit.<scene>`. `shape_for(rules, rung, d100)`.
- `tables.roll_table(table_id, context, *, rules, state, rng, purpose=None) -> TableResult(entry, words, roll,
  sub, redrawn, events)`: dispatch rows by context (`meaning_kind`, `severity`), `*modifier` ints shift the
  roll (bounded by `modifier.total_clamp`), the total is clamped to `modifier.clamp` (tbl.npc_action: [1, 10],
  so `roll` is the clamped total), recency re-draws once (window `recency_window`, default 5). Stage `events`
  before rolling the same table again.
- `rulings.signature(anchor_id, deltas)`, `gate_signature`, `oracle_signature`, `find_rulings(store, sig,
  staged=())`, `precedent_for(found, differing_fact=None)`, `log_ruling(RulingRecord, mint, store=, staged=)
  -> Event` (skips an id already used: `ruling_logged` does not advance the `rul` counter).

## engine/harm API (T054, T065, T066)
Functions take `ctx` (anything with `state`, `mint`, `rules`; optional `rng`, `boundary`, `payload`):
`HarmCtx.of(tx, rules, rng)` (`engine/harm/ctx.py`). They return events (or a result with `.events`); the caller
stages them. Pass `writes=Writes(...)` to compose several calls in one overlay (stage `writes.events` once).
- **State** (`engine/harm/state.py`): facts on the character: `harm_state` (`harm_state.active|staggered|dying|
  dead`), `wound_load`, `dying_step`, `brink`, `down`, `defeated {manner}`, `lethal_key` (Key 1 of the fall),
  `career.ending` (`death|retirement|career_end`); quantities `vitality`, `fate`, `dread` (M2, optional).
  Readers: `harm_state`, `descriptor` (fresh/worn/bloodied/staggered/dying/down/dead), `wound_load`,
  `dying_step`, `brink`, `is_down`, `defeated_manner`, `endure_modifier` (data.attributes.endurance +
  data.endure_bonus), `attribute` (+ maim deltas `attribute_delta.<attr>`). Entity data read: `reduction`
  (int vs harm.physical, or {tag: n}), `resist`/`vulnerable` tags, `depth` (NPC), `defeat_disposition`,
  `objective`, `pace`, `attacks [{name, severity}]`/`max_severity`, `threat_advisory`, `lethal_context`,
  `hazard {severity, lethal_context}`, `can_bargain`, `want(s)`, `leader_want`.
- `apply.apply_harm(ctx, target, *, severity=|dealt=, harm_tags, source, frame_id, lethal=False, mode="lethal",
  no_reduction, periodic) -> HarmResult(events, amount, breakdown, wound, load, transition, obligations, lethal,
  lethal_refused, threshold, triggers, hooks)`. PR-07-1; `lethal` is re-tested (07.3.6) and refused/logged
  (`meta log.lethal_refused`). M1: wound load and Dying run in full; wound records are coarse (`log.coarse`).
  `res.threshold` -> call `threshold.open_threshold`. Also `restore_vitality(ctx, t, amount=|to=, reason,
  rule_id)` (stabilizes the Dying), `stabilize`, `heal` (2 per long rest, 07.8.9), `dying_check(ctx, t,
  natural=None)` (07.2.7; h.07.dying_check is M2, the M1 loop calls it at the PC's turn end), `status_block`,
  `harm_hook(ctx, source)` (resolve's `apply_cost(harm_hook=...)`).
- `lethal.py`: context fact `<source>.lethal_context` (non-entity source: `world.lethal_context:<source>`),
  value `{id: lc.<scene>.<source>, source, pc, cause, sign, effective_from, active, ...}`, None once ended.
  `warning_needed(state, pc)` -> `[LethalTrigger(pc, source, cause, detail)]`; `warning_block(rules, trig,
  source_name=, fate=, yield_text=, retreat_text=)` (the `[WARNING]` block); `record_warning(ctx, trig, sign=)`
  once delivered (effective from the next beat); `lethal_scan(state, frame) -> LethalVerdict(lethal, missing,
  context_id, offer_line)` with frame `{kind: pc|adversary|hazard|affliction, source, target, stakes, lethal,
  mode}`; `may_auto_commit(state, frame)` (False for a lethal frame); `danger_notice`, `active_triggers`.
- `exits.py`: `yield_answer(rules, state, pc, victor) -> YieldAnswer(accepted, terms, words, ...)`,
  `yield_pause(mint, ans)` (pause kind `yield_terms`), `commit_yield(ctx, pc, ans, term)`; `retreat_offer(state,
  rules, pc, route=, engaged=, hostiles=, barred=, left_behind=) -> RetreatOffer(legal, refusal, kind, choices,
  parting_blow, words)`, `commit_retreat(ctx, pc, off, choice)`; `run_disposition` (PR-07-7, coarse in M1).
- `threshold.py`: `open_threshold(ctx, pc, Situation(victor, bargainer, route, rout_clock, strikes, ...)) ->
  ThresholdOpen(events, menu, pause_id, text)` (pause kind `last_chance`, no default); `choose(ctx, pc, menu,
  option_id, pause_id=, via_gamble=None) -> Choice(events, gamble_offer, last_stand, advance_time, ending)`;
  `menu` may be the `Menu`, the open `last_chance` PauseRecord, or its detail: the stored menu is used, and the
  pause id / `via_gamble` come from the pause (resolve a pick with `choose(hctx, pc, pause, choice_id)`; never
  rebuild the menu from state). `resolve_gamble(ctx, pc, menu, natural=None)`; `finish_last_stand`; `confirm_voluntary_last_stand`; `write_death` (refuses with
  `DeathRefused` unless both keys hold; `meta pref.death.mode = retire` -> retirement); `ending_state(state,
  pc=None) -> None|"death"|"retirement"|"career_end"` (pc: `meta pc.active`, else the newest PC).
- **`last_chance` pause detail** (both pauses: the Threshold's and the Gamble's near-fail "choose a price"):
  `{"pc", "via_gamble": bool, "menu": {"pc", "situation": {victor, source_kind, bargainer, bargain_ask, route,
  companion_can_carry, rout_clock, maim_entry, strikes {option id: fact id}}, "options": [{id, name, order,
  available, reason, price, death, struck_by}] (every option in the rules' order, offered or not), "fate_cost",
  "maim": {entry, name, attribute, text}|null, "bargain": {bargainer, ask}|null, "gamble": {free, live, choose,
  death} (percent), "refused_strikes": [option id]}}`. The Threshold's pause also keeps the flat keys `fate_cost,
  maim, bargain, gamble, victor, struck`. The choices (`{id, label}`) are the offered options (the Gamble's:
  options 1-5). `menu_detail(menu)` / `menu_from_detail(pause | detail)` convert.
- `rest.py`: `rest_refusal(state, rules, pc, kind)`, `rest_duration(rules, kind)`, `best_quality`,
  `rest_quality(kind, site=, interruptions=, lost_intervals=, sleep_hours=, caps=)`, `rest_payload(kind,
  quality, site, treated=False, resters=None)` for `mark_boundary`; `rest_site`/`record_rest_site`; `treat(ctx,
  patient, reach=, what=, success=)`. Handlers (ctx -> events): `h_07_rest_recovery`, `h_07_natural_recovery`,
  `h_07_load_clear`, `h_07_lethal_scan` (raises `meta trg.lethal_warning` / `trg.danger_notice`),
  `threshold.h_07_career_end`. Registration: importing `engine.harm.handlers` registers them (adapting
  `TimeContext`); `engine/time/handlers/h07.py` should import it.
- Counters in meta: `<pc>.breathers_since_short_rest`, `<pc>.short_rests_today`, `<pc>.rest_long.last`,
  `<pc>.overdraws_since_long_rest`, `<pc>.healings_since_long_rest`, ... (`ctx.counter_key`).

## engine/abilities API (T067)
- Held abilities: `entity.data["abilities"]` (ids from abilities.yaml; rank 1 in M1). Focus: quantity `focus`
  (`focus.define_focus(eid, base=4, t_high=0, breadth=0)` at creation); Spent: fact `focus.spent`. Uses: quantity
  `uses.<ability id>` (defined at first use if absent).
- `use.check_use(state, rules, eid, ab_id, *, timing=None, flares=(), rider_used=False) -> UseCheck(ok, refusal,
  cost, uses_left, overdraw)` (05.4.1 order; nothing spent on refusal); `offer_view(...)` (PR-05-1 step 5);
  `commit_use(ctx, eid, ab_id, *, frame_id, flares=(), accept_overdraw=False) -> UseResult(events, cost,
  uses_left, spent, overdraw, hooks)`; `ability_cost(ab, flares=, relic=, adjust=, free=)`. During a Last
  Stand abilities cost 0.
- `focus.spend_focus`, `restore_focus`, `overdraw_price(state, rules, eid, shortfall)`, `apply_overdraw`,
  `push(ctx, eid, choice=reach|stakes|grit)`, `restore_focus_consumable` (4 per long rest).
- `recharge.py`: `refreshed_by(boundary)`, `focus_gain(...)`; handlers `h_05_scene_recharge`,
  `h_05_day_recharge`, `h_05_focus_recover`, `h_05_rest_recharge`; importing `engine.abilities.handlers`
  registers them (`engine/time/handlers/h05.py` should import it).

## engine/world API (T059, T060 deterministic half, T061, T062)
All writers take `ctx = TimeContext(tx, rules, rng)` and stage events (inside a running handler via `ctx.emit`);
readers take a `WorldState`. Errors: `engine.world.common.WorldError`. The PC is `common.active_pc(state)`
(`meta['pc.active']`, else the last PC). Rolls need `ctx.rng`.
- **Places** (`engine.world.places`): `seed_world_into_store(tx, world) -> {seed thread id: entity id}` at game
  creation: places (entity data = the 10.1.2 record; undiscovered ones sealed, gate `UNDISCOVERED_GATE`, slice =
  name when known), route links as facts `link.<route id>` on both ends (value {to, route, route_kind,
  travel_watches, terrain, known}; unknown ones sealed), factions, `faction_relation` relationships, the seed's
  clocks, threads as `thr.*` entities (data {seed_id, thread_kind, text, points_to, status}), the cast at their
  homes (wants/fears/refusals/secrets sealed); meta `world.region`, `world.names`, `world.peoples`,
  `world.threads`, `thread_list`. `put(tx, entity, place)`; `location(state, entity=None)`;
  `links(state, place)`, `reachable(state, from_place=None) -> [RouteLink(to, route, route_kind, length, unit,
  terrain, known, implicit)]` (implicit passages: building <-> settlement/siblings 1 interval, landmark <-> area
  1 hour); `is_discovered`, `cast_at(state, place)`, `entry_mode`. `move(ctx, to_place, end_scene=True) ->
  Arrival(place, name, place_kind, from_place, route, arrived, mode, discovered_now, cast_here, interrupt,
  remainder_rounds, narration, boundaries)`: ends the scene (`place_change`), `travel` mode for a route,
  `advance_time` by the length, then position + discovery (10.1.5) + entry mode. Interrupted: `arrived` False,
  finish with `continue_move(ctx, arrival)`.
- **Scenes** (`engine.world.scenes`): `start_scene(ctx, *, place, mode, agenda, hoped_answer="", pillar=None,
  challenge_type=None, cast=(), situation_tags=(), expected=None, purpose_declared=False, interrupt=False,
  thread=None) -> SceneStart(scene_id, record, test, push, narration)` (writes `scene_started`, marks
  `scene_start`: `h.12.scene_test`, `h.12.pacing_push`); `end_scene(ctx, reason, *, answered=None |
  "as_hoped" | "against_hope" | "answered", opposition_overcome=False) -> SceneEnd(scene_id, reason, tension,
  narration, chronicle_offer)` (marks `scene_end` while the scene is current, then `scene_ended`);
  `reopen_scene(ctx)`; `mark_agenda_answered(ctx, answered)`; `note_cut(ctx, "interrupt" | "player_cut")`;
  `note_turn(ctx, quiet=bool) -> dead air count`; `turn_is_quiet(input_classes, events)`;
  `cut_due(state, rules) -> str | None` (a `pacing.yaml#scenes.cut_triggers` id; `dead_air` = offer the cut);
  `current_scene`, `scene_info`, `cast_present`, `situation_tags`, `add_situation_tags`, `scene_test_result`,
  `agenda_answer`. `director_enums(state, rules)` -> dict keyed like `SchemaContext`'s Director fields plus
  `push_raised`, `lead_fires`; pass `places=`, `push_raised=`, `lead_fires=` to `schema_context`.
  Meta: `scene` {scene_id, expected, purpose_declared, interrupt, thread, untested, tags}, `scene_test`
  {scene_id, result expected|altered|interrupted|untested, roll, tension, adjustments | event}, `scene_agenda`,
  `scene_outcome`, `scene_cut`, `scene_push`, `dead_air`.
- **Social** (`engine.world.social`): `meet_npc(ctx, role, place, *, people=None, reuse=True) -> npc id`
  (roster match by role and place, else a walk-on with fixed name/pronouns/descriptors; on the cast list);
  `first_interaction(ctx, npc, modifiers=0) -> standing` (reaction roll, once); `standing(state, npc)`,
  `standing_effects(rules, value)`, `step_standing(ctx, npc, steps, reason, cap=None)`;
  `record_memory(ctx, npc, deed, valence, how="did", ..., apply_step=False, severity=None)` (committed at
  scene_end by `h.12.npc_memory`; at once outside a scene), `memories(state, npc, active_only=True)`,
  `memory_step(rules, valence, severity)`; `record_knowledge(ctx, knower, fact_id, how)`, `knows`;
  `promote_npc(ctx, npc, "recurring" | "principal")` writes later-depth fields as **facts** on the NPC (wants,
  fears, refusals, secrets sealed) — read NPC fields with `npc_field(state, npc, key)` (fact, else data);
  `patience`, `spend_patience`, `talk_closed`; `record_commitment(ctx, npc, by="npc"|"pc", act, due_day, ...)
  -> fact id`, `keep_commitment`, `commitments(state, status="open")`; lists: `cast_list(state)`,
  `thread_list(state)` (dicts with id, status, weight, points_to, ...), `set_thread_status`, `mark_progress`,
  `feature(ctx, ids)`, `protected_threads`. `LoggedSeedRng(rng, purpose)` adapts the game RNG to engine.gen.
- **Chronicle** (`engine.world.chronicle`): `chronicle_append(ctx, text, *, kind, entities=(), tags=(),
  scope="public", source="12.4.8", supersedes=None) -> "chr.<n>"` (<= 30 words; 11.12.1 kinds; 11.12.2
  occasions); `chronicle(state, include_superseded=False, entity=None, since_seq=0) -> [ChronicleEntry]`.
  Entries are facts on `world`, predicate `chronicle.<id>`. Scene-end offer: meta `chronicle_offer`.
- **Pacing** (`engine.world.pacing`): `tension(state, rules)`, `phase(state)` (meta `pacing.phase`, default
  build; the M2 intensity handler moves it), `tension_points(tx, rules)`, `random_event(ctx, source=) ->
  RandomEvent(focus, target, target_list, meaning, substituted)` (PR-12-6 steps 1-3; the World role interprets),
  `inject_lead(ctx, form_misfit=False) -> LeadInjection(rung, source_rung, source_id, thread, form, facts)`
  (PR-12-3: writes the lead fact + PC knowledge, resets the counter, lowers `trg.lead_injection`),
  `clock_trace(state, clock_id)`, `raise_push(ctx, reason)`, `rotation`, `overdue`, `mark_tried(ctx, thread,
  node)`. Triggers raised: `trg.lead_injection` (h.12.inconclusive_streak at 3 inconclusive beats),
  `trg.pacing_push` (consumed by h.12.pacing_push in BUILD).
- **Handlers** registered by `engine/world/handlers.py` (imported from h12.py/h15.py): h.12.scene_test,
  pacing_push, tension_update, inconclusive_streak, lead_audit, rotation_update, npc_memory, bookkeeping
  (12.4.8 steps 3 and 8); h.15.patience_reset, commitments_due (interrupts when a deal falls due unkept).

## engine/audit API and the adjudication record (T043–T047, T107)
- **Adjudication record** (`engine.dm.adjudication.AdjudicationRecord`, Pydantic, `.dump()` JSON): what T1–T6
  produced and all T7–T10 may narrate from. Fields: `turn_id`, `pc`, `parts` [`PartEntry(text, class, handled,
  beat_id)`], `beats` [`BeatEntry(beat_id, frame_id, part, actor, targets, verb, restatement, gate, gate_words,
  approach_words, difficulty_words, stakes, rolled, degree, near_miss, success_at_cost, reach, reach_words,
  costs [CostEntry(menu_id, severity, form)], harm [HarmEntry(target, words, condition_ids)], conditions (words),
  positions [PositionEntry(entity, words)], license)`], `oracle` [`OracleEntry(question, answer, fact_id, subject,
  predicate)`], `npc_actions` [`NpcActionEntry(npc, action, source: talk_outcome|want|refusal|table_row|behavior|
  clock|trigger|ally_reason|frame, source_ref, tags)`], `omens` [`OmenEntry(clock_id, stage, omen, completed,
  ticked)`], `scene` `SceneEntry(cut, ended, started, header)`, `writes` [`WriteRef(seq, type, entities, key)`],
  `triggers` (active trigger ids), `pause` `PauseEntry(kind, frame_id, prompt, options)`, `notes`. Fill `writes`
  with `rec.add_writes(appended_events)` (entities and key derived per event: quantity name, fact predicate,
  condition id, relationship kind, clock id). **Every write this turn must be added**: a change claim is
  supported only when a write backs it, and an NPC act only when `npc_actions`/`beats`/`omens` source it. Words
  only, no numbers (INV-3); strings in the record are what the plain fallback prints.
- `engine.audit.claims`: `Claim` (data-model §4; alias `class`, `sentence` accepts "3"), `Verdict(claim, verdict,
  store_value, fix, reason)`; `check_claims(claims, state_or_store, record, scene_ids, *, rules=None) ->
  list[Verdict]` (12.3.2: PC agency → leak via the sealed partition → `unknown` subject = cut, never an entity
  (an unknown subject whose text names an entity created this turn resolves to it) → per-class store comparison);
  `owed_blocks(triggers, response) -> ["[WARNING]", "[STATUS]"]` missing (counts as contradicted);
  `failing(verdicts)`; `OWED_BLOCKS`; spec 011: `check_claims(..., texts={sentence: words})` marks a claim whose
  subject the words do not make `certain` (12.3.1b item 4) `uncertain`; `blocking(c, v, rules)` (the closed
  list, narrator voice assumed); `relevant_item(text)`. Fixes: new_element → `write_on_mention` (a feature of the place) or `cut`;
  undetermined → `oracle` (or `cut` when nothing can settle it); contradicted/overreach → `redraft_to_store`;
  unsourced_change/pc_agency → `cut`; leak → `replace_with_slice` when the seal has a slice, else `cut`.
  PC `action` claims are judged by the Checker's `pc_words_or_feelings` flag only; an NPC `action` without
  `asserts_change` (an ongoing description) needs no source. Store conventions it reads: identity in
  `EntityRecord.data` (gender, pronouns, age, role, detail, demeanor, people, aliases) or facts; possession =
  an item's `data.holder|owner|carried_by|held_by` or fact `holder`, facts carries/holds/has/equipped/... on the
  holder, or a quantity; standing = relationship `<npc>|<pc>|standing`; harm = conditions, `harm_state`,
  `vitality`, `exists`. **Turn loop:** offer the Checker every id a claim may name (scene scope plus ids created
  this turn) and list the PC as `pc.x: Name, you, your` so pronoun claims resolve.
- `engine.audit.fallback`: `plain_fallback(record, *, names={id: name}, verdicts=()) -> FallbackResult(fiction,
  review_flag=True, owed_blocks, ruling: RulingRecord(kind="rule_conflict", review_flag=True))` (12.3.3: the scene
  header when this turn opened one, then every must-name item's rendered line from `engine.dm.handles`; ends "What
  do you do?" unless `record.pause`; the player's own words are never echoed); log it with `log_ruling(...)`.
- `engine.dm.handles` (spec 006): `items(record, names=) -> [RecordItem(handle "R1".., kind scene|beat|cost|harm|
  condition|position|learned|oracle|npc|activity|omen|note, must_name, entities, render, beat, index, text)]`, in
  `record_text` order. Must-name: an owed beat (a result, "no roll", or one that simply happened; not refused or
  paused), its costs, harm, conditions, positions and delivered items, Oracle answers, NPC responses, omens, and the
  notes in `MUST_NOTES` (incident, leads, "cannot make out", a rest taken). `render` is a statement built from typed
  fields (an Oracle answer through `render.relation(..., neg=)`), "" when none can be built.
- `engine.audit.declare` (spec 006, 12.3.1/12.3.1a/12.14.13): `DeclaredSentence(text, refs, about, new
  [NewElement(element_kind, name, ordinary, implied)], atmosphere)`; `parse_output(data)` reads either output shape
  (`sentences`, or `fiction` + `declarations` keyed "0".."29"); `tier_of(el, rules)` (element_tiers; not `ordinary`
  person/item/document -> T2; unknown kind -> T2); `mention_of(el)` (T1a -> a write_mentions entry);
  `SceneIndex.of(state, items)` (aliases, pronouns, quantities, facts, handles, known capitalised words, sealed
  names); `scan_sentence(s, idx, rules=, names=) -> SentenceScan(added_about, failures [Failure(why, fix
  cut|redraft|oracle, store_value)], undeclared_new)`; `coverage(sents, must) -> uncited handles`;
  `t2_delivered(el, s, idx)`. `claims.check_claims(..., cited={sentence: [RecordItem]})`: a claim restating a cited
  line about its subject, or an act of a subject a cited line names (or a present witness of a cited incident), is
  supported; `Verdict.incidental` marks an `undetermined` 12.3.2 writes as narrated; `beat_polarity(text, beat)`.
  `plain(text)` strips ids, snake_case and digits. Beat lines render from `actor`, `verb`, `targets` and the degree
  (never the restatement); an Oracle answer is its question verbatim, and only a yes to a statement-shaped one.
  `fact_sentence(state, fact, subject=None)` renders through `engine.text.render.relation`.
- `engine.text.render` (B P4, no dependency): `clause(subject_id_or_words, verb_phrase, obj=None, *, neg, tense,
  plural, names, pc)` (verb agreement for "you" / third person; the verb's first word must be in the closed `VERBS`
  list, else KeyError: add it there, never guess), `relation(subject, predicate, value=None, *, neg)` (the
  `RELATIONS` registry, else a predicate headed by a listed verb; a yes/no with no such verb is ''), `np(noun, n,
  definite=)`, `plural`, `article`, `who(eid, names=, pc=)`, `the_name`, `degree_words`, `DEGREE_WORDS`,
  `BEAT_VERBS` (Reader verb id -> phrase with / without a target), `sentence`. Model free text is never passed
  through it: quote it whole or leave it out.
- `engine.audit.screen`: `screen_draft(fiction, *, flags=checker["screen"], record, verdicts, safety,
  pause_blocks_text=[rendered OOF pause blocks], rules, names=entity names) -> ScreenResult(passed, reasons,
  screen)`; `screen` has exactly `TurnRecord.screen`'s keys. Also `mechanics_in_fiction(text, rules=, names=)`
  (12.14.4: digits, dice, rules phrases; attribute / DC tier / condition names only in rules forms or Title-case
  mid-sentence), `ends_on_prompt`, `numbered_options`, `pause_blocks(blocks) -> labels`.
- `engine.audit.safety` (separate from the Checker, FR-036): preferences are current facts `pref.safety.lines` /
  `pref.safety.veils` / `pref.safety.flags` on `player` (else `world`), value a list of topic strings or
  `{topic, tags}`. `safety_prefs(state)`, `safety_fact(SafetyEntry(kind, topic, tags), state, mint)` (append,
  supersedes), `screen_safety(draft, entries_or_state) -> SafetyResult(ok, cuts, veils, flags, reasons)` (line =
  cut; veil ok as one plain sentence ≤ 20 words; flag = pause with `flag_prompt(topic)`), `matches_line(text,
  entries)` (screen a table row or generator output before use), `handle_safety_part(text) -> SafetyResponse(
  pause, oof_line, reframing, chosen_by, options, record, ledger)` (12.5.7; `line: X` / `veil: X` records one).
- `engine.dm.mentions`: `write_mentions(mentions, *, tx, rules, rng, settle=None, place=None) ->
  MentionResult(created {name: id}, reused, refused, settled [Settled(entity, property, value, how, fact_id)],
  unsettled, seqs)` — stages the writes itself (add `seqs`' events to the record). Kinds written: npc, item,
  object, place (others refused → cut). Dedupe by name, alias, id tail (and role for NPCs): `find_existing`.
  NPC by description with no identity implied → `engine.world.social.meet_npc`; a proper name or implied
  identity → `walk_on` with the implied fields fixed (name, gender ⇄ pronouns), position, cast list. Unsettled
  properties: `settle(entity, prop)` if given, else table `tbl.<kind>_<prop>` / `tbl.<prop>`, else the Oracle
  (Even), each written as a fact.

## engine/dm turn API (T030, T038–T042: the adjudication pass T1–T6 and the PR-01-1 driver)
- **Context** (`engine.dm.context.TurnContext`): `TurnContext.for_store(store, model=, rules=None, rng=None,
  config={}, recorder=None)`; fields `store, rules, rng, model, recorder (default store.record_model_call), config
  (GameConfig dict: oracle_free_cap_per_scene, auto_commit), milestone, tx (open only during a turn), dispute
  (12.3.6 hook), call_ids, call_seq (CallSequence; `ctx.next_call_seq(turn_id, role)`)`. `ctx.state` (working state in a turn), `ctx.mint`, `ctx.time_ctx()`,
  `ctx.record_call` (pass as every role call's `recorder`), `ctx.auto_commit()` (meta `auto_commit`, else config).
- **Turn** (`engine.dm.turn`): `run_turn(ctx, message) -> AdjudicationResult`; `answer_pause(ctx, choice_id)` (a
  pick from the API; no Reader call; ValueError for a choice not on the open pause). `AdjudicationResult(turn_id,
  record: AdjudicationRecord, pause: PauseRecord|None, offer: OfferView dict|None, writes: [seq], oof: [{kind,
  text}] (OFFER/WARNING/REDIRECT/NEAR_MISS/LAST_CHANCE/NOTE blocks owed, rendered by 12.15), view (narrator view
  re-read after T6), turn_record: TurnRecord (saved: parts, beats, oracle_calls, pause, writes, model_calls),
  reader: ReaderResult|None)`. T1 saves the turn row (input verbatim) before the transaction; T2–T6 are one store
  transaction, so any exception before T6 writes nothing (the row stays: retry). The narration pass (T7–T12)
  completes the same TurnRecord with `store.save_turn`. A pause skips T5 (12.2.6: no time passes). Order in T4:
  SAFETY (stops the rest) → SESSION → DISPUTE → PENDING_ANSWER (resume) → OOF → FICTION_QUESTION (state, else
  `ask_oracle`; key = `ids.slug(predicate)` on the subject, so a settled key is read, never re-drawn) →
  DECLARATION (an open pause is first closed by 12.2.6's defaults). At the PC's turn end `dying_check` runs while
  Dying; a harm that opened the Threshold opens the `last_chance` pause (`open_threshold`).
- **Pipeline** (`engine.resolve.pipeline`): `PipelineEnv(tx, rules, rng, store, framer, pc, auto_commit, harm_hook,
  lethal=None, milestone)`; `run_beats(env, [BeatPlan(beat, intent_verbs)]) -> PipelineResult(outcomes
  [BeatOutcome(status resolved|no_roll|redirected|refused|paused|withdrawn|question, entry: BeatEntry, frame_id,
  oof)], pause, queued)` (≤3 beats, stops at the first pause); `resume(env, pause, choice)`;
  `close_by_default(env, pause)`; `harm_hook_for(env)` (apply_harm + HarmEntry; `env.threshold_due`);
  `harm_lethal_warning` (default `LethalCheck`); `evidence_event`, `challenge_band(dc)` (03.4.3); `offer_text`.
  `FramerFn(beat, candidates, *, gate, note=None) -> ProposedFrame`. Pause detail (`PauseRecord.detail`) holds
  `stage` (offer|warning|near_miss|redirect|clarify), `plan`, `queued`, `proposed`, `frame`, `roll`, `offer`
  (OfferView), `candidates`, `warned`; choice ids: offer `commit, change, withdraw, go_big, play_safe`; warning
  (kind `offer`) `continue, withdraw`; near_miss `failure, success_at_cost:<menu>`; redirect `accept:<licence>,
  other`; clarify none (free words). A lethal frame (or a Dire one against a 07.3.3 source) is preceded by the
  warning pause; after a warning the beat never auto-commits.
- **Roles** (`engine.dm.roles`): `reader.read_message(ctx, message, exchanges=) -> ReaderResult(parts,
  pending_answer, fact_questions, beats, clarifying_question, restatement, player_quantity, defaulted)`,
  `.plans(actor=, declared_seq=, mint=)`; `framer.framer_for(ctx) -> FramerFn` (its `check=` runs `frame_check`,
  so a refusal is re-asked once naming the step, then the default frame: first fitting cost by 01.13.1's order;
  `engine.dm.schemas` builds the cost `source_fact` and the 01.6.1 `attribute` enum);
  `world.npc_responses(ctx, happened) -> [WorldResponse(npc, want_engaged, refusal_engaged, tags)]`,
  `world.world_view(state)` (narrator view + present NPCs' standing, wants and refusals), `npc_motives`.
- **World step** (`engine.dm.world_step.world_step(ctx, record, beats=)`): NPCs by the default NPC layer
  (`engine.dm.npc_layer`, 12.11.9: `ensure_activities` writes each present NPC's `activity` fact once per scene and
  `record.activities`; `respond` picks each engaged/addressed NPC's response: a resolved Talk → a recorded refusal or
  want matched by tags (`event_tags` from the beat's verb, facets, target, `Beat.pressure`, the Framer's
  `Frame.asks`, topic words; `motive_tags` by refusal kind and want object, `social.yaml#event_tags`; a want's row
  by `want_row`: served 9/8, defeated 2/1, engaged 6, then the clamp; the World role only when no tag matches and
  the NPC has a want and a refusal, tag `world_fallback`; config `world_judge`) → `tbl.npc_action` by standing
  clamped to `tbl.npc_practice`'s rows; with nobody engaged and the crowd practice, `crowd_response` (a scene fact
  on the place plus an `NpcActionEntry` on the place); an addressed NPC always answers, a refusing
  source as "refuses, in their own voice (register, habit): ..."; meta `npc.spoken`), clock omens from this
  turn's `clock_ticked`, fired triggers (a pending `trg.lethal_warning` is delivered: block in `record.notes`),
  time per resolved beat by `beat_cost(scene mode)`.
- **Fixture** (`tests.fixtures.scene_dock.build_dock(tmp_path) -> DockScene(store, rules, rng, pc, ferryman, watch,
  place, clock, scene, facts)`): the dock at night (site mode), two NPCs with sealed wants/refusals, one public
  clock listening to exposure and time, Wren with two licences and `ab.soft_step`.

## engine/dm oof + codex + dispute API (T049, T073, T108)
- **OOF blocks** (`engine.dm.oof`, 12.15): every builder returns `engine.dm.response.OofBlock(kind, text)`, rendered
  from computed records only (OOF blocks carry the numbers; fiction never does, 12.14.4). `offer_block(frame |
  OfferPreview, *, rules=, fate=None, lethal_line=None, auto=False, costs_line=None)` (cli.md layout: approach and
  difficulty in words, `Success or better N% · critical failure N% · near miss N% (need N+ on the die).`, stakes with
  threatened/alternate cost in words, the lethal line directly under Stakes, reach, fate, numbered choices; secret,
  natural-20-only, mode-price and `OFFER — auto` variants); `offer_view(src, rules) -> OfferView` (exactly the
  engine-api fields); `offer_choices(src)` (commit, change, withdraw, go_big, play_safe); `near_miss_block(frame,
  roll, rules=)` + `near_miss_choices(frame)`; `redirect_block(GateDecision, state=, rules=)` (G3/G4, 12.15.5);
  `warning_block(rules, LethalTrigger, source_name=, fate=, yield_text=, retreat_text=)` and `status_block(rules,
  state, eid, exits=)` wrap engine/harm; `last_chance_block(Menu)` (threshold.menu_text); `clarify_block(q,
  assuming=False)`; `recap_block(state, since_seq=0, pc=None)` (12.5.3, state only); `note_block(text, label="NOTE",
  rest=())` (labels NOTE, CORRECTION, RULES, UNKNOWN, RULING, CHOICE, ...; kind NOTE); `seed_block(step)`,
  `create_block(text, n=, total=)`; `ordered(blocks)` (12.15 order, the pause block last); `name_of(rules, id)`.
- **Codex** (`engine.dm.codex`, 00.6.4): `codex(state, section=None, rules=None, *, cards=None) -> CodexView(section,
  text, data)`; sections `sheet` (default), `abilities`, `conditions`, `journal`, `threads`, `rules <id>` (a leading
  `/` is accepted). Reads `engine.store.views.codex_view` only (plus `descriptor` for the harm word); conditions whose
  data has `visible: false` are hidden; inventory = items/objects whose data or `holder`-type fact names the PC.
- **Disputes** (`engine.dm.dispute`, 12.3.6 / PR-12-4): `dispute(ctx, text, *, identify=None, choice=None) -> str`
  matches `TurnContext.dispute` (the turn loop should set `ctx.dispute = dispute`, or wrap it with a model-backed
  `identify`); `settle_dispute(...) -> DisputeResult(kind, blocks, events, reverted, choices, claim, correction)`.
  `identify(ctx, text) -> DisputedClaim(kind fact|quantity|ruling, subject, key, said, quote, turn_id, source,
  frame_id, missed_fact) | None` is the model's part; `default_identify` reads explicit ids and shown quantities.
  Kinds: unclear, hidden (not player-facing: `[UNKNOWN]`, never revealed, objection logged), not_said (store value +
  quoted exchange; no fact, INV-9), stands, record_error (corrective `fact_set`/`quantity_changed`, Event `source=
  "correction"`), narration_error (store stands; relying frames of this scene → `choices` accept_forward/rewind;
  call again with `choice="rewind"` to `writes_reverted` from the first relying beat, never before the scene start),
  ruling_stands, ruling_error. Every correction appends meta `corrections` (12.3.4 step 4 record) and logs a
  `ruling_logged` (`kind rule_conflict`, `review_flag: true`); a rewind also appends meta `rolls_voided`. Writes go
  to `ctx.tx` when open, else a one-shot transaction.

## engine/dm seed + creation API (T063, T064, T109)
- **Responses** (`engine.dm.response`): `Response(turn_id, phase seed|creation|play|ending, fiction, oof_blocks
  [OofBlock(kind, text)], pause: Pause | None, scene_ended, budget_notice, flags)`, `Pause(kind, prompt, choices
  [Choice(id, label)], default_choice, frame_summary, pause_id)`, `Pause.of(PauseRecord)`, `resp.text()`. OofKind adds
  SHEET and RULES (PR-02-6/PR-02-7). Contract-compatible with engine-api.md.
- **Interpret** (`engine.dm.roles.interpret`): `interpret(ctx, message, *, choices, block, classes=(),
  lines_and_veils=False, cards=("12.16.2",), exchanges=(), multi=False) -> InterpretResult(choice, own_words_class,
  own_words_text, lines_and_veils, picks, direct, defaulted)`. `direct_choice(message, choices, multi=)` maps a
  number, lone letter, option id or exact label (and "skip"/"" → `move_on`) without a model call.
- **Pauses for any flow** (`engine.dm.seed_flow`): `flow_tx(ctx)` (one transaction per answer; sets `ctx.tx`),
  `open_pause(tx, kind, prompt, choices, default, detail, rule) -> PauseRecord` (`pause_opened`; `detail["blocks"]`
  = the blocks shown with it, `detail["flow"]` = seed|creation), `close_pause(tx, rec, choice, by, words)`,
  `present_pause(rec, phase, extra=None) -> Response` (resume re-presents exactly the stored blocks + pause),
  `flow_of(state) -> "seed" | "creation" | None` (which flow owns the open pause: route `submit`/`answer` by it).
- **Seed** (`SeedFlow(ctx)`): `.start()` (mode question; or re-presents), `.present()`, `.submit(text)`,
  `.answer(choice_id)` (also `move_on`, `details`, `suggest`), `.seed() -> WorldSeed`. Mixed mode asks which
  questions (multi-pick by numbers), then each picked question; every step's `[SEED n/14]` summary is a pause
  `keep` / `veto:<question>` (or `veto` for a step without questions) when it rolled something, else shown and
  passed. `rebuild_seed(state)` replays `seed_answered` ops (`ws.mode`, `ws.pick`, `ws.q.*` with choice None =
  handed to the oracle, `ws.step.<n>`, `ws.veto.<n>`, `ws.check`; `ws.ran.<n>` records what a step rolled). After
  the check: `write_world(tx, world)` = `engine.world.places.seed_world_into_store` + meta `world.seed`,
  `world.tongues`, `world.pregens`, `world.opening`, `world.canon_impossible`, `world.keepers`; then creation
  opens in the same transaction. Meta `game.phase`: seed → creation → play.
- **Creation** (`engine.dm.creation`): `CreationFlow(ctx)`: `.begin(new=False)`, `.present()`, `.submit(text)`,
  `.answer(choice_id)`, `.draft() -> Draft`; `open_creation(ctx, blocks)` (inside an open tx); `new_character(ctx)`
  (closes an open non-creation pause, e.g. the ending menu, with `new_character`). Blocks (`creation_answered.block`):
  `c0` (+ `c0.taste`, `c0.limits`), `c1`, `c2.people`, `c2.rule`, `c3`..`c7`, `c8.drive|anchor|aspiration|true_thing`,
  `c9.name` ({name, pronouns}), `c9.pronouns`, `rm.pick`, `rm.name`; markers `start`, `birth`, `names`, `change`,
  `ready`. Pure helpers: `fold(state) -> Draft`, `sequence`, `build_record(draft, state, rules)`, `apply_birth`,
  `validate`, `sheet`, `default_placement`, `parse_name`, `parse_limits`, `parse_taste`, `suggest_names`.
- **The written PC** (on "begin"): entity `pc.<name>` data {attributes (7, incl. endurance), abilities, competence
  {tag: 2}, pronouns, people, upbringing, livelihood, rule, profile, deep, access}; quantities vitality (12 +
  Endurance), fate 1/3, dread 0/(8 + Resolve), coin, focus (`define_focus`, base = upbringing's focus_base);
  licences (lic.focus.push, trainings, tongues with grades); kit items as `item.*` entities + fact `carries` [ids];
  facts origin.people|upbringing|livelihood|rule, drive (commitment), bond.anchor, aspiration, true_thing,
  birth.knack|quirk|gift, birth.account, hooks; relationship to a pregen's anchor NPC; position at
  `world.opening.start.place`; meta `pc.active`, `pc.creation` and `<pc>.creation` {path, choices{block: {value,
  default}}, birth, open_slots, window "open", bent (BentState), manner}. Lines/veils: `pref.safety.lines|veils`
  facts (subject `player` if that entity exists, else `world`) via `engine.audit.safety.safety_fact`; plus
  `pref.lethality.acknowledged` on `world` when creation's opening (which states it) is answered.

## engine/dm narration API (T048, T050, T051, T060 Director half, PR-12-8)
- **Entry points** (`engine.dm.turn`): `play_turn(ctx, message) -> TurnOutcome` and `play_answer(ctx, choice_id) ->
  TurnOutcome` run T1–T6 (`run_turn` / `answer_pause`, unchanged) then T7–T12 (`engine.dm.narration.narrate_turn(ctx,
  adj, message)`). `TurnOutcome(response: engine.dm.response.Response, turn_record: TurnRecord (saved, complete per
  data-model §4), narration: NarrationResult(fiction, fallback_used, review_flag, skipped, draft_versions, verdicts,
  screen, created), adjudication: AdjudicationResult)`. T7–T12 are one transaction under the turn id (T8 mentions,
  the fallback's ruling, T12 counters/cut); a model error there raises and writes nothing after T6.
- **Loop** (`narrate_checked(ctx, record, *, player_message, purpose="turn"|"scene_open"|"opening"|"recap"|"epilogue",
  exchanges, pause_blocks, extra, fallback_text=None)`, needs `ctx.tx`; spec 006, spec 011 "check less"): declared
  sentences → per sentence, code only (12.3.1b): `scan_sentence` on the narrator's voice (`declare.voices`: quoted
  spans with a `speaker` are speech; unknown names, numerals, sealed strings fail; a pronoun clash is logged),
  the speech checks (`speaker` present and not the PC; `pc_quotes` beyond the player's message: `pc_agency`, cut),
  new elements by tier (T1a written on mention, logged when it cannot be; T1b by the Oracle; T2 in the narrator's
  voice cut unless a cited line delivers it; named only in speech: testimony, logged, never written; a clash with a
  stored detail logged unless the slot blocks: a held weapon, a coarse posture), safety, outcome words against
  cited beats (an uncited sentence: the turn's only rolled beat) → a cut-type failure is dropped by code; the
  rest and uncited must-name lines go in one narrow `Repair` call per round (only the failing sentences) → after
  `max_redrafts` rounds still-failing sentences are cut, uncited must-name items are stated by their rendered line
  (a `rule_conflict` ruling, `review_flag`), and the open prompt is restored only if repair cut it → the plain
  fallback when no drafted sentence passed → T10 `screen_draft` (recorded) → `_said` (`NarrationResult.said` →
  `TurnRecord.said` `{speaker, turn, words, about}`, never a fact; a stored unknown name heard: `learn_name(...,
  "heard")`) → `_sample`: on a sampled turn the Checker's diff and full extraction on the delivered sentences,
  `check_claims(texts=)` (an uncertain subject: `Verdict.uncertain`, `disposition` `no_verdict`), every claim to
  the claim log with `blocking_miss` (`claims.blocking`), never a cut or a write. `NarrationResult.claim_log` →
  `TurnRecord.claim_log` `{turn, sentence, class, verdict, store_value, ...}` (12.3.1b). Config `narrator_schema:
  "fiction"` selects the fallback output shape. `ModelInvalid` on the first draft falls back.
- An OFFER pause (stage offer) with nothing else in the record skips T7–T10: fiction = the beat's restatement, then
  the OFFER block (`skip_drafting`). OOF blocks: `turn_blocks(ctx, adj.oof, record, pause)` renders the open pause
  from its stored detail (`pause_blocks`: `oof.offer_block(Frame)`, `near_miss_block`, `clarify_block`, CHOICE notes)
  in place of the pipeline's one-line summary, labels the rest, moves `[WARNING` notes into WARNING blocks;
  `owed(ctx, record, text)` adds a missing `[STATUS]`; `oof.ordered` puts the pause block last.
- **Roles**: `roles.narrator.draft(ctx, record, *, player_message, exchanges, purpose, repair: Repair|None, extra,
  items=) -> NarratorDraft(sentences | repairs)` (THIS MESSAGE = `record_text(..., items=)`: one `- R3 MUST: ...`
  line per record item, in names, never ids; a repair adds `repair_text`; the schema's `refs` = handles + view fact
  ids, `about` = scene scope; `new` comes before `text` in the schema); `roles.checker.check_draft(ctx, fiction, *,
  player_message, created, exchanges, sentences, decls, items, full=False) -> CheckerOutput(sentences, claims,
  undeclared, unexpressed, screen, scene_ids)` — the diff audit (12.3.1, spec 009 B): its own prompt, the 12.3.1
  card only, view = `entity_lines` (`<id>: Name, aliases; here|not here|new this turn`, PC `pc.x: Name, you,
  your`; someone not here loses a label someone here has) over `checker_ids` (scene scope + spotlight + ids
  created this turn), message = `[n] sentence` lines each followed by `    declares: ...` (`declaration_words`:
  handles with their words, view facts via `render.relation`, `about`, `new`, `atmosphere`; withheld with
  `full=True`) then `THE PLAYER'S MESSAGE` (the offline Checker reads only the `[n]` lines). `claims` are only
  assertions beyond the declarations; `undeclared` (typed elements) are written by tier in `narration._audit`;
  `unexpressed` refs are logged only. `narration.audit_mode(ctx)` is `sampled` on 1 turn in
  `full_extraction_every` (the turn id's crc32), else `off` (DL-12-83; the skip gate is retired). The narrator
  schema's `speaker` enum is the present people, never the PC (`SchemaContext.speaker_ids`). `roles.director.direct(ctx, *, situation, player_message,
  happened, quiet_turns) -> DirectorDecision(cut_now, next_scene: NextScene, push, lead, push_raised, lead_fires)`
  (enums: `director_context` = `director_enums` folded into `schema_context`); `frame_scene(ctx, d, *, reason,
  interrupt, purpose_declared) -> SceneStart` (`places.move` to another reachable place, else `end_scene`, then
  `start_scene`); `scene_header(state)`.
- **Scenes in the loop**: after T5, `_director_step` asks the Director when the player moves on (`narration.moves_on`),
  a beat got a degree / a clock completed / an NPC refused, or `trg.lead_injection` is raised (then `inject_lead`
  runs and the lead goes in `record.notes`). A player's cut is framed in this turn; an answered agenda is marked
  (`mark_agenda_answered`). T12: `note_turn`, interrupt → `note_cut`, then `cut_due` → `end_scene` and meta
  `scene.frame_next` {reason, scene_id, turn_id}; the next turn frames the scene before T2 (Director with that
  message; after a dead-air cut a player who stays (`stays`) re-opens it). `Response.scene_ended` = ended, not yet
  framed.
- **Disputes / OOF**: DISPUTE parts go to `engine.dm.dispute.settle_dispute` (or an injected `ctx.dispute`); a
  reliance choice opens a `clarify` pause with `detail.stage == "dispute"`, answered by `settle_dispute(choice=)`.
  OOF rules questions and codex words answer from `engine.dm.codex`.
- **Sessions** (`engine.dm.session`, imported by turn.py so its handlers register; h12.py should import it too):
  `open_session(ctx) -> Response` (session_start, recap via the Narrator `purpose="recap"` from `recap_summary`
  through the checker (fallback: empty fiction), the RECAP block, the next-time note, the open pause re-shown; with
  no scene ever, `opening(ctx)`: the Director frames the first scene, the Narrator writes the opening from
  `world.opening`); `close_session(ctx, next_time=None)` (session_end, the pause stays, the next-time question, a
  where-you-stand line). Each saves a TurnRecord `(session open)` / `(opening)` / `(session close)`. Handlers:
  `h.12.session_open` (meta `session` {n, opened_seq, prefs}), `h.12.session_close` (meta `session.review` = flagged
  ruling ids, `closed_seq`), `h.12.mode_change` (meta `mode.loaded` {mode, tags, beat_cost}).

## engine/game.py, endings, opening (T069–T072, T109)
- **Game API** (`engine.game`, contracts/engine-api.md): `GameConfig(models={role: RoleModel}, offline=False,
  budget_usd_per_session=2.0, oracle_free_cap_per_scene=6, milestone=1)`, `.model()` (OfflineModel / GeminiModel;
  MissingKey before any file is written). `Game.new(path, config, seed=None, *, model=None) -> (Game, Response)`,
  `Game.open(path, config, *, model=None) -> (Game, Response)`, `submit(text)`, `answer(choice_id)`,
  `new_character()`, `dispute(text)`, `codex(section)`, `turn_record(id)`, `branch(label) -> "br.<slug>"` (a
  `branches` row + a file copy `<name> @ <label>.db`), `spend() -> SpendTotals`, `set_pref("budget_usd" | "autocommit",
  v)` (meta `pref.budget_usd` {usd} / `auto_commit`), `close()` (session close), `Game.replay(path, until_seq=None)
  -> ReplayResult(identical, divergence, events, inputs)`. `model=` injects a model (tests: ScriptedModel).
- Routing by `flow_of(state)`: seed / creation / `ending` (the ending menu) / `retire` (the retirement question);
  None → play (`play_turn` / `play_answer`). After creation writes the PC: `engine.dm.opening.begin_play`
  (= `session.opening`; meta `opening.pc` names who had one; `session.needs_opening(state)`). After every play step:
  `engine.dm.ending.ending_due(state)` → `run_epilogue`. Owed work runs before new input (`Game._settle_pending`):
  meta `narration_pending` (T7–T12 failed after T6: `engine.dm.turn.resume_narration`), a missing opening, an
  epilogue. Budget notice: once per session, never with a mid-turn pause open.
- **Inputs log**: every API call is a row of the game file's `game_inputs` table (kind, JSON arg, outcome), written
  before it runs; `Game.replay` re-drives a temporary copy from them (`open` rows close and reopen the copy) with
  `ReplayModel` over the stored `model_calls` and compares every event. On open, each (turn, role) call numbering
  continues from the file (`_prime_call_seq`), so call ids never repeat across sittings.
- **Endings** (`engine.dm.ending`): `ending_due`, `run_epilogue(ctx)` (PR-11-6 simple: `exists` fact, chronicle
  `death`/`retirement` entry, meta `legacy.<pc>`, `ending.done`, epilogue through `narrate_checked(purpose=
  "epilogue")`, pause kind `ending` with `new_character, new_world, quit`, detail flow `ending`), `answer_ending`,
  `present_ending`; retiring: `is_retire(text)` ("I retire"), `ask_retire` (pause kind clarify, flow `retire`,
  choices `retire, keep_playing`), `answer_retire` (fact `career.ending = retirement`).
- **Turn loop additions** (`engine.dm.turn`): `play_dispute(ctx, text)` (DISPUTE part, no Reader, no world step);
  declared rests (`rest_kind(message)`: breather / rest_short / rest_long) advance the rest's duration with its
  boundary mark (PR-07-8); the Gamble is rolled when chosen; a Last Stand ends in death at the end of the PC's next
  turn, and opens no new Threshold. `narration.pure_oof(record)`: only OOF parts and nothing in the fiction → empty
  fiction, no model call.
- `engine/gen/_data.py` pickles each parsed data file under `engine/gen/_cache/` keyed by the file's sha256.
  `h.02.creation_lock` and `h.02.open_slots` are built (`engine/time/handlers/h02.py`; the reminder is shown by
  `open_session`); `h.02.bent_offer` is not (logged as skipped).

## Player-facing polish (feature 004 polish pass)
- **Sanitizer** (`engine.dm.player_text`): `clean(text, rules, names)` (idempotent; strips section/code/chapter
  citations and backticks, names data ids from rules data or entity names, snake_case → words),
  `strip_citations`, `name_ids`, `display_name`, `humanize`, `entity_names(state)`, `clean_response(resp, rules,
  state)` (OOF blocks, pause prompt + labels, budget notice; fiction only in seed/creation). `Game._call` applies it
  to every Response; `codex()` cleans all but the rules section. Narrator fiction in play is never cleaned.
- `narration.shown_pause(pause, owned)`: blanks the prompt when the pause's block is already shown.
- `oof`: `offer_block` has no choice line and always says "If it goes wrong: …" in words; `redirect_block(dec,
  state=, rules=)` renders a stored GateDecision ("Not as tried: <why>", 1–3 alternatives, "To learn it: …");
  `redirect_options`, `near_miss_choices(frame, rules)` (successes first, then "Let it fail"), `when_words(ts)`,
  `short_text(text, limit)`.
- `pipeline.decision_json(dec)`: the GateDecision stored on redirect/refusal oof items and pause details
  (`"decision"`). A cost that cannot land records nothing (no "could not land" entry).
- `creation.plausible_name(name)` (02.9.6): a bare number or non-name re-asks the name with a NOTE.
- Director packet: a "PLACES (here first, then reachable):" section, one `- <id>: <name>` per place.
- CLI (`play/render.py`): `reflow` joins hard wraps; `strip_listing` drops a block's own copy of the choices;
  `choice_lines` prints `  N) label` once. A single in-range letter picks a choice; a bare number with no choices
  open is not sent.

## End-to-end and recorded games (T076, T077; second smoke fixes)
- **Scripted player** (`tests/e2e/driver.py`): `Driver.start(path, seed=, model=None, name=)` (mixed seed partly in
  words, quick start), `.play(n)`, `.settle(resp)`, `.travel()`, `.retire_and_continue()`, `.call(kind, arg)`;
  every pause kind first reached is closed and reopened (`Game.open`) and must come back equal (`.seen`,
  `.resumed`); `.packet_sizes()` + `trend()` measure rendered packets from `model_calls`.
  `tests/e2e/test_offline_game.py`: 60 turns in the default run, 500 turns with `--runslow` (or `RUN_SLOW=1`;
  the `slow` marker is registered in tests/conftest.py), and the lethal path (warning, last chance, death, new
  character) with a ScriptedModel.
- **Recorded games**: `Game.export_record(path) -> dict` (inputs, each call's response + `packet_digest`, an event
  digest each), `Game.replay_record(record, check_packets=True) -> ReplayResult`; `ReplayModel(records,
  check_packets=)` diverges when a packet's text changed (naming the `[SECTION]`s). Fixed games live in
  `tests/replay/games/*.json`; re-record with `python -m tests.replay.record_games` when a change is intended.
- Offline stand-in: the Framer names a stakes source when the act plainly risks one (attack someone present,
  a height, water, sneaking: `_stakes`), Moderate tier, cost forms in words; the World answers only the present NPCs
  an act engages; tbl.npc_action rows are worded differently when they repeat; the Director's agenda comes from
  the incident, the place headed for or an open thread.
- Turn loop: only NPCs present in the new scene act after a player's cut; a Down PC wakes after one interval
  (`engine.harm.apply.wake`, 07.2.9); "what are my options?" gets `turn.stuck_answer` ([LEADS], 12.8.5); claims
  that restate a record line their sentence cites (the inciting incident, a lead: spec 006) are supported;
  cost.exposure's observer defaults to someone present. Kit items are named from `base_items.yaml`.

## Plain setup wording (world seed + creation screens)
- **One table** (`engine/dm/text/setup.yaml`, read by `engine.dm.setup_text` as `T`): the player's wording for the
  seed (`seed.mode`, `seed.pick`, `seed.steps.<n>`, `seed.questions.<qid>.{prompt,pick,what,options,short}`,
  `ws.q.rulers` `options_by_tier`) and creation (`creation.blocks.<bid>.{title,prompt,lines,options,enter,footer}`,
  `creation.sheet`). Keys are the rules' ids; ids, recorded answers and events are unchanged. A missing entry falls
  back to the rules' sanitized text; `tests/engine/test_setup_text.py` lists every missing entry and any jargon.
- `T.pause_block(header, prompt, lines, choices, footer)` builds a pause block (lettered options; the CLI numbers
  them in place, `render.strip_listing(in_place=True)`); `T.footer(kind, enter)` is the one "how to answer" line
  (pick | pick_many | number | words). Pause `detail["orig"]` = {option id: rules label} where the plain one differs.
- `T.read_answer(ctx, message, rec, tag="[SEED]"|"[CREATE]", classes=, cards=, multi=, lines_and_veils=)`:
  `direct_choice` on the plain labels, else Interpret sees "plain (rules wording)" labels; same schema.
- **Seed recaps** (`engine.dm.seed_recap`): `recap(step, ws.st, ws.words) -> list[str]` (a few plain lines per step +
  who chose what); `rolled(step)` = re-rollable answers. `SeedStep.summary` (the rules' dump) is kept for the record.
  `AUTO` = `ws.q.hybrid_none` (one option) and `ws.q.relics_magic` (a rules setting): never asked, never re-rolled.
  Steps 10 and 11 (contents hidden) offer no re-roll. Headers: "World n of 14 · <title>",
  "Your character n of N · <title>".
- **Enter** (`play/cli.py Session.enter`): an open pause's `default_choice` is taken (echoed "(Keep it)", "(the dice
  decide)"); a seed/creation default that is not an option (`move_on`, c8.true_thing's `open`) is sent as `move_on`;
  creation c6 now carries `move_on` as its pause default. No default: nothing sent, except the name block, which
  says "Type a name for your character." The engine says the same for "skip"; "suggest" offers three names.

## Adjudication (spec 007; R2-C rules 00.12.3, 01.4.1, 01.6.5, 01.6.13, 12.15.2)
Supersedes the earlier notes on `Beat.gate` / `would_be_license` / `necessity`, the cli.md OFFER layout,
`offer_text`, TRADE_LABELS and Enter at an OFFER.
- **Reader** (12.2.2, DL-12-50): beats carry only `verb`, `target`, `against_will`, `uses_power`, `speech`, `shape`
  (`now` | `extended` | `queued` | `conditional`; only now/extended run this turn, the rest are restated as
  queued), `g4_fact`; parts carry `question_kind` + `topic` (the answer ladder's keys, spec 008).
  `reader.knowledge_parts(message)` routes "what do I know?" before the call. `Beat.asks`: a Talk beat asking a
  plain question. Each beat also carries `purpose` (`own_change` | `serves_another_act` | `free_activity`) and
  `pressure` (`none` | `request` | `threat` | `offer` | `plea` | `insistence`); `reader.normalise(data)` runs on
  the raw answer (engine and `evals/reader_live.py`): a bodily act (Move, Handle, Strike, Grapple, Force, not
  against anyone's will) that serves another act folds into it, a Move closing on the next against-will beat is its
  reach, 00.12.6's free acts drop (a look only with a casual word: `CASUAL`), and a Talk beat with pressure `none`
  in a message that asks is SPEECH (01.2.1, 01.2.2, 00.12.6, 15.3.10; policy B4/A4/C1).
- **Gate** (`engine.resolve.gate`): `compute_gate(verb, *, against_will, uses_power, speech, method, held, rules,
  reading, literacy_known)` is pure; `covering_verb` picks the card from the facets; `check_gate(beat, ...)` adds
  conditions, a cited G4 fact (or `canon_impossible`), accepted fallbacks and engine-set stretch/emulate.
- **Necessity** (`engine.resolve.necessity`): `necessity(beat, decision, state=, rules=)` before framing (plain
  reading, certain talk: `trivial`, no Framer call); `trivial_class(proposed, rules, verb)` after it;
  `parties_who_would_act(state, actor, beat)` backs the observer stakes source (else a cost must cite its fact).
- **Framer / frame_check**: obstacle `{kind: tier, obstacle_class, tier}` (class base from
  `basic_verbs.yaml#anchor.obstacle_classes`; `other` names the rung), `nudge_why`/`nudge` ("-1"/"0"/"+1")/
  `nudge_fact`, `request_size` for talk; `opposed_by(state, beat, verb)` forces the defense; the second cited
  Precision snag turns Protective; the 01.6.13 guard sets `Frame.guard` / `Frame.long_shot`;
  `Frame.alternatives` (`alternatives(...)`); costs narrowed by `costs.source_menus` (`stakes_cost_menus`).
- **OFFER** (`engine.dm.oof`): `offer_block(frame, rules=, fate=, lethal_line=, auto=)` is 12.15.2's template;
  `CHANCE_WORDS`, `SEVERITY_WORDS`, `REACH_WORDS`, `GLOSSARY` / `glossary(word)` (14.2.7); `offer_choices` labels
  Do it / Go big / Play it safe / Another way / Back off. The pause prompt is the restated beat.
- **Menu** (`play/render.py`): `menu_keys`, `enter_choice` (Do it, or None = show again on Dire / lethal / long
  shot and on near miss, redirect, last chance), `menu_line`; play-phase pauses print it instead of numbers; `?`
  explains a word. Digits still pick. Auto-commit defaults on (`resolution.yaml#auto_commit`), Safe frames only.

- **Spec 011 (R2-G):** I-159: on a tier obstacle with a nonzero nudge or class `other`, `frame._levers` turns every
  cited Precision snag Protective (one model-chosen modifier per beat, DL-01-29). I-160(a): the Framer's
  `reach_two_factors` (two unoffset factors or a total potency) routes the beat to G4 in `pipeline._frame` before
  the OFFER (`gate.zero_reach`: `missing_kind zero_reach`, a `g4` ruling, nothing spent; DL-01-33). The Framer's
  `asks` enum (`social.yaml#event_tags.asks`, Talk aimed at a person) is `ProposedFrame.asks` / `Frame.asks`.

## Memory: details, scene cards, spotlight, role views (spec 009 part A)
- **Details** (`engine.store.details`, 00.6.6a): a detail is the fact `detail.<slot>` with `persistence` (lasting |
  scene | beat; new `FactSet` field) and `certainty: narrated` when narration stated it. `write_detail(state, mint,
  eid, slot, value, *, source="narration", because=None)` -> `DetailWrite(outcome new|same|superseded|
  contradiction|refused, events, fact_id, prior)`: one value per slot; a change supersedes only with `because` (this
  turn's explaining record entry), else `contradiction` (nothing written); `scene`/`beat` slots from narration are
  refused. `active_details` (scene details, then every lasting one by salience, 2 for seeded, generated or
  corrected, then last use; the profile budget cuts the tail: no cap, spec 011), `expire_events` (12.4.8 step 8;
  `end_scene` stages them; also clears a place's `crowd_response`),
  `used_event(fact_ids)` (`details_used`: usage marks). Projection: `WorldState.details[eid][slot] = DetailRef(fact_id,
  last_used)`; a `None` value clears a slot.
- **Scene cards** (12.4.8 step 9): folded by the projection from each scene's events into
  `WorldState.scene_cards[scene_id]` (`SceneCard`: place, agenda, answer, times, cast, beats, facts, memories,
  threads), so `store.rebuild()` regenerates them. `engine.retrieve.episodes.cards_for(state, ids, k=2)` (ended scenes,
  overlap then recency), `card_lines(state, card)` (as the PC knows it). `session.recap_summary` lists them (12.5.3).
  Recency in `scene_facts` reads `scene_starts(state)` (the cards), not `scene`/`last_scene`.
- **Spotlight** (`engine.retrieve.scene`, 12.2.4): `alias_index(state)` -> (strong, weak) keys of PC-known names;
  `resolve_names(state, text)` (full names and aliases first; a lone given/family name only when unique and not
  inside a longer proper name); `spotlight(state, message, last_delivery, beat, k=None)`.
- **Role views** (`engine.dm.packet.view_for(role, state, ctx)`): `build_packet(role, view=WorldState, ...)` calls it
  with `view_ctx(message, exchanges, focus, beat)`; strings and dicts pass through. Narrator: no `MOTIVES` keys or
  predicates, spotlight as the PC knows it, at most 2 cards; Reader: names, PC licences and conditions, open pause;
  Framer: target and place records, their facts and the PC's; Director: threads, clocks, cast list, cards.
  World: `roles.world.world_view(state, happened)` = `view_for(Role.WORLD, ...)` plus motives.
- **Part B hookups** (spec 009 B): `details.slot_of(predicate, rules, kind)` (a word list to the closed slots);
  `mentions.profile_diff` on reuse (new: write `narrated`; same: no-op, listed in `details_used`; different:
  `contradictions` unless `write_mentions(..., because=)`), a created entity's look written to its slot; claims'
  `identity` reads `detail.<slot>`; `_settle` writes an incidental look as a lasting detail; `narration._mark_used`
  emits `details_used` at RECORD for cited `detail.*` facts and the details a sentence wrote or restated;
  `narrator.used_details(state, now, window)` feeds `freshness_lines(..., used=)` (the image 3-gram scan retired;
  the opening-clause and speech-opener scans stay as the backstop).
- **Promises** (`engine.dm.codex.promises(state, about)`, `promise_question`, `promise_subject`): the PC's open
  commitments, filtered through the alias index; `turn.oof_answer` routes "what did I promise X?" there.

## Answer ladder (spec 008 part B; PR-12-10, 12.10.8)
- **`engine.dm.answer`**: `ask(ctx, knower, question_kind, topic, text, rungs, pc=) -> Answer(said, line, fact_id,
  pointer)` answers one delivered question at RECORD (before the draft): the index (meta `answers.index`,
  `"<npc>|<kind>|<topic or entity>" -> {fact, said, pointer}`; a repeat rolls nothing), then "who is <role>" (own
  name; a named person; a story role -> the case graph, building the reduced case; else `cast_who`), a question about
  a case (`case_about`: the subject asked about or named, or its role's words) -> `_from_case` (a holder delivers
  and `deliver_node` marks it found; anyone else names the core holder), `what_want` -> the stance, then the rungs
  `rungs_for(rules, reach)` (`social.yaml#delivery.information.ladder_depth`): `store_hit`, `pack_hit` (the NPC's
  seeded pack, written as a `topic.<topic>.<pack fact>` fact the NPC knows), `ratify` (Role `proposer`, then the
  Oracle at `odds_for`; a "no" is the `knows_*` = false fact), `point` (casting via `pointer_target`; a walk-on made
  when no one and no place fits; never the case subject, never back to who pointed here). `volunteer` (Great+),
  `deliver_count(n, reach)` (T-01-6), `who_answer(ctx, text)` (the DM-side "who is X?", the PC as knower),
  `topic_of(state, topic, text)` (a null Reader topic is read from the words, else `local_news`).
- **Role `proposer`** (`engine.dm.roles.proposer.propose`): schema `{kind: ordinary_fact|not_ordinary, subject,
  predicate, value}`, default `not_ordinary` (no candidate); a bare packet (prompt, known lines, question; no core,
  no cards). Offline: a bland candidate on the topic.
- **Consumers**: `world_step.deliver_learning` returns one summary per learning beat (`{beat, verb, knower, speech,
  answers: [(fact id, pointer, line)]}`; the long-horizon harness's empty-success and ask-twice metrics read it).
  A Talk with no question part is a request (no ladder); Observe/Recall run `_look` (a search placement, the store
  ranking, the place's furniture, a pointer). SPEECH questions with no Talk beat are answered as the addressed NPC's
  act (`source: talk_outcome`, `source_ref: PR-12-10`) and that NPC skips the table. `npc_layer.talk_outcome`:
  "answers what you asked" or T-15-5's yes by reach.
