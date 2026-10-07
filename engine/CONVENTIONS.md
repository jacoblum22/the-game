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
