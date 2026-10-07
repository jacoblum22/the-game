# Tasks: Playable Prototype

**Input**: Design documents from `specs/004-playable-prototype/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/ (engine-api, model-calls, cli),
quickstart.md

**Tests**: Requested by the spec (golden worked examples, generator parity, replay, seeded-error recall:
SC-003, SC-005, SC-008), so each phase carries its tests. No test may call a paid model: every test runs
on the offline or replay adapter.

**Revisions**: tasks T106–T109 were added after `/speckit-analyze` (2026-10-07) and sit in the phase where
they run; T065 moved into Phase 3.

**Organization**: Grouped by user story. US1–US3 are all P1 and together form Milestone 1. US2 (the
resolution pipeline) and US3 (narration and the claim check) are built first against a fixture scene,
because US1 (the game from new game to ending) is made of them. US4–US9 are Milestones 2–7, listed as
phases with coarser tasks; each gets its own detailed pass of `/speckit-tasks` when its milestone starts.

**Rules lookups**: read rules by id only: `python rules/tools/rq.py <id>`. Never read a whole chapter.
`rules/` is read-only for this feature.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no dependency on an unfinished task)
- **[Story]**: US1–US9 from spec.md

## Path Conventions

`engine/` (the engine package), `play/` (front ends), `tests/` (pytest), `evals/` (paid runs, never in
pytest), at the repository root, as in plan.md "Project Structure". `src/` (the probes) is left untouched.

---

## Phase 1: Setup

**Purpose**: Project skeleton and tooling.

- [x] T001 Add `pyproject.toml` (ruff, pyright, pytest config scoped to `engine/`, `play/` and the new test folders so the probes' existing issues do not block) and `requirements-dev.txt` (ruff 0.16.10, pyright 1.1.414). The owner's tooling branch `claude/project-thread-9ivqgo` also changes `.claude/` settings and hooks, so it is left for the owner to merge
- [x] T002 Add `pydantic>=2` and `PyYAML` to `requirements.txt` (keep `google-genai==2.25.0`); add `python-dotenv`-free `.env` loading (a 10-line reader in `engine/llm/env.py`, no new dependency)
- [x] T003 [P] Create the package skeleton with `__init__.py` files per plan.md: `engine/{data,build,store,time,time/handlers,resolve,harm,abilities,gen,world,retrieve,audit,dm,dm/roles,llm}`, `play/`, `tests/{engine,golden,contract,replay,seeded_errors,fixtures}`, `evals/`
- [x] T004 [P] Add `saves/` and `*.db` to `.gitignore`
- [x] T005 [P] Add `engine/ids.py`: typed id helpers (entity, fact, frame, scene, turn, event ids), monotone id generation from the event store's counter (no uuid randomness, so replays are identical)

---

## Phase 2: Foundational (blocks every story)

**Purpose**: Data, store, dice, time, retrieval and the model layer. No story work starts before this.

### Rules data

- [x] T006 Implement `engine/data/loader.py`: load every `rules/data/*.yaml` once into typed, read-only structures keyed by id; follow `rules/data/SCHEMAS.md`; fail loudly on unknown ids and enums; expose `Rules` with accessors (`anchor(id)`, `table(id)`, `boundary_handlers()`, `resolution`, `oracles`, `harm`, `world_seed`, `gen_birth`, `origins`, `kits`, `licenses`, `abilities`, `conditions`, `pacing`, `social`, `last_chance`, `basic_verbs`, `attributes`, `archetypes`, `adversaries`)
- [x] T007 [P] Test that every data file loads and every cross-reference resolves in `tests/engine/test_data_loader.py`
- [x] T008 Implement the card compiler `engine/build/compile_cards.py`: split the chapter files into rule cards per 00.15.2 (id, title, tags, [D]/[J] marks, "Loads in:" lines, body), write `engine/build/cards.json`, and record the rules tree hash so a rules change forces a rebuild; use `rules/tools/rq.py`'s parser rather than a new one where possible
- [x] T009 [P] Implement `engine/build/coverage.py --milestone N`: list every rule id as implemented / coarse / deferred / model-judged from `# rule: <id>` tags in `engine/` and the milestone table in plan.md; print a summary, not a dump

### Store, RNG and time

- [x] T010 Implement `engine/store/db.py`: SQLite (WAL) schema exactly as data-model.md §1 (`events`, `rng_draws`, `turns`, `model_calls`, `snapshots`, `facts_idx`, `rulings_idx`, `branches`); `events` is append-only ("never updated or deleted"); a turn's events commit in one transaction; a `game_created` event stamps engine version, rules hash and milestone (FR-040)
- [x] T011 Implement `engine/store/events.py`: a Pydantic payload model for every event type in data-model.md §2; "an event that fails validation is never appended"
- [x] T012 Implement `engine/store/projection.py`: `WorldState` (data-model.md §3) built by pure reducers per event type; families not in M1 (tally, effect_instance, offer) are stubs that raise; snapshots at `scene_end` and on save; rebuild from events must equal the live projection
- [x] T013 Implement `engine/store/views.py`: `narrator`, `codex` and `audit` views (00.6.4, 00.6.5); sealed fields replaced by permitted slices in the narrator view (INV-10); `facts_idx` queries are bi-temporal (`valid_from_seq`/`valid_to_seq`)
- [x] T014 [P] Implement `engine/rng.py`: named `random.Random` streams seeded from the game seed; every draw logged to `rng_draws` with its purpose; `d(sides)`, `d100()`, `pick(table)` helpers
- [x] T015 Implement the time ladder and modes in `engine/time/clock.py` (00.7.1 timestamp, 00.7.3 modes) and `advance_time` / `mark_boundary` (PR-00-2) in `engine/time/scheduler.py`: phases and ordering from `rules/data/boundaries.yaml` (00.7.6), skipping time runs every crossed boundary (00.7.7), interrupts
- [x] T016 Implement the handler registry `engine/time/handlers/__init__.py`: handlers register by id; every id in `boundaries.yaml` that is not live for the current milestone logs `handler_skipped` with "not yet built" and the milestone that builds it (FR-026)
- [x] T017 [P] Implement clocks (PR-00-3) and conditions (PR-00-5, 00.9 stacking) in `engine/store/clocks.py` and `engine/store/conditions.py`
- [x] T018 [P] Tests for the store, projection rebuild, views (no sealed field in the narrator view), RNG logging and scheduler ordering in `tests/engine/test_store.py`, `tests/engine/test_rng.py`, `tests/engine/test_scheduler.py`

### Retrieval

- [x] T019 Implement `engine/retrieve/anchors.py` (≤8 candidates from `anchors.yaml` by verb, intent verbs and tags), `engine/retrieve/cards.py` (≤12 cards per call plus the always-loaded core, 00.15.4), `engine/retrieve/triggers.py` (`get_active_triggers`); deterministic ordering
- [x] T020 [P] Tests for retrieval caps and determinism in `tests/engine/test_retrieve.py`

### Model layer

- [x] T021 Implement `engine/llm/base.py`: `StructuredModel` protocol (`fill(role, schema, packet) -> dict`), the re-ask-once-then-default rule from contracts/model-calls.md, `ModelUnavailable`, `ModelRefused`, `MissingKey`; every call recorded in `model_calls` with tokens, cost and latency
- [x] T022 Implement `engine/llm/gemini.py`: google-genai 2.25.0 client, `response_mime_type="application/json"` with the per-turn JSON Schema, `thinking_level` low, implicit-cache-friendly packet order, retries; key from `GEMINI_API_KEY` in the environment or `.env` (MissingKey otherwise); check the SDK's current parameter names with Context7 before writing; never called by tests
- [x] T023 [P] Implement `engine/llm/replay.py`: serve the stored response for the same `(turn_id, role, attempt)` and verify `schema_hash`; `ReplayDivergence` on mismatch
- [x] T024 [P] Implement `engine/llm/offline.py` exactly as contracts/model-calls.md "Offline stand-in" (per-role heuristics, heuristic claim extractor) plus `ScriptedModel` (a per-role response queue for tests). Used by tests, the persona harness and `python -m play --offline`; never presented as the real game
- [x] T025 [P] Implement `engine/llm/budget.py`: price table per model id (research.md §4), per-turn / session / game totals, the between-turns warning (FR-039); never interrupts a turn
- [x] T106 Implement `engine/dm/packet.py`: the one packet builder every role uses, in the order of contracts/model-calls.md (role instructions → core → ≤12 cards → narrator view → last 4 exchanges → this message); a test that packet size does not grow with turn count (FR-029, SC-002) in `tests/engine/test_packet.py`
- [x] T026 Implement the per-role schema builders in `engine/dm/schemas.py` exactly as contracts/model-calls.md (Interpret, Reader, Framer, World, Director, Narrator, Checker): enums built from the rules and the state; "an empty list means the field is dropped from the schema"; "No schema contains a numeric field except `player_quantity`"
- [x] T027 [P] Contract tests: every builder's schema is valid JSON Schema, contains no numeric field (INV-3), and the offline model's output validates against it, in `tests/contract/test_schemas.py`

**Checkpoint**: data, store, time, retrieval and models work on their own; `ruff`, `pyright`, `pytest` clean.

---

## Phase 3: User Story 2 — Attempt anything and see it resolved honestly (P1, Milestone 1)

**Goal**: one player message in a fixture scene goes through T1–T6 with every PR-01-1 step, the OFFER pause
and honest rolls.

**Independent Test**: in the fixture scene, a risky declaration shows an offer with computed odds before any
roll; commit, change, withdraw and trade behave per 01.7; small talk and a trivial act roll nothing; an
unsettled fact is settled once by the Oracle and stays settled; an unlicensed and an impossible attempt are
redirected with an alternative and spend nothing.

### Tests for User Story 2

- [x] T028 [P] [US2] Golden tests from WE-00-* and WE-01-* with fixed dice in `tests/golden/test_worked_examples_01.py` (list the examples with `rq.py --toc 01` and `--find WE-01`)
- [x] T029 [P] [US2] Odds table parity with T-01-3 and Oracle thresholds with T-01-10 in `tests/golden/test_odds_oracle.py` (the cited `odds01.py` and `oracle01.py` sims are missing from the repo; test against the tables themselves)
- [ ] T030 [P] [US2] Fixture scene and character in `tests/fixtures/scene_dock.py`: a dock at night, two NPCs with wants and refusals, one scene clock, a PC with two licences and one starting ability

### Implementation for User Story 2

- [x] T031 [P] [US2] Implement the degree rule (01.8.1), `roll_check`, near miss (01.9.3) and reach in `engine/resolve/roll.py`
- [x] T032 [P] [US2] Implement odds (T-01-3) in `engine/resolve/odds.py`
- [x] T033 [P] [US2] Implement the Oracle (PR-01-4, T-01-10) with extremes and twists, the engine-side free-question cap per scene (`oracle_free_cap_per_scene`, I-038 stopgap, logged) in `engine/resolve/oracle.py`; `roll_table` with recency in `engine/resolve/tables.py`
- [x] T034 [US2] Implement GATE G0–G4 checks against holdings and `covers`/`excludes` (01.3, PR-01-5 redirect) in `engine/resolve/gate.py`
- [x] T035 [US2] Implement `frame_check` (PR-00-1, PR-01-2): DC from tier or opposition, modifier, odds, cost previews, lever and snag validity (≤2 each, must exist, not too recent), deltas ≤2 citing facts; refuse naming the failure, in `engine/resolve/frame.py`
- [x] T036 [US2] Implement the cost menu, threatened and alternate costs and their application (PR-01-3) in `engine/resolve/costs.py`
- [x] T037 [US2] Implement rulings: `find_rulings` by signature before any adaptation, Oracle call, Good Idea or G3/G4 decision (FR-022; wired into T033 and T034) and `log_ruling` (00.15.5–00.15.6) in `engine/resolve/rulings.py`
- [x] T065 [US2] Implement harm (PR-07-1 `apply_harm`, harm states 07.1–07.2), the lethal scan and warning (PR-07-4: a lethal frame is never auto-committed and follows the warning), yield and retreat (PR-07-6), the Threshold (PR-07-5) and last chance (`last_chance.yaml`), death and career end, in `engine/harm/` (built in Phase 3 because the pipeline's CONSEQUENCE step and auto-commit need it)
- [ ] T038 [US2] Implement the pipeline driver PR-01-1 (PARSE → GATE → NECESSITY → ANCHOR → FRAME → OFFER → ROLL → READ → DELIVER → CONSEQUENCE → RECORD) per beat, ≤3 beats, stopping at the first pause, with the offer choices commit / change / withdraw / go big / play safe (01.7) and auto-commit (01.7.4; a lethal frame is never auto-committed and always follows the warning), in `engine/resolve/pipeline.py`
- [ ] T039 [US2] Implement the Reader (A1) and Framer (A2) roles: prompts and packet assembly per contracts/model-calls.md in `engine/dm/roles/reader.py`, `engine/dm/roles/framer.py`, prompts in `engine/dm/roles/prompts/`
- [ ] T040 [US2] Implement T1–T6 of PR-12-1 in `engine/dm/turn.py`: log verbatim, classify (SAFETY first), load, adjudicate (SESSION, DISPUTE, OOF answered; FICTION_QUESTION via state → canon → Oracle; DECLARATION via the pipeline; PENDING_ANSWER resumes), world (T5, see T041), write (evidence by PR-03-1 recorded, tallies deferred to M3)
- [ ] T041 [US2] Implement T5 WORLD: the World role (NPC wants/refusals → engine rolls `tbl.npc_action`), clocks and omens, fired triggers, time and boundaries, in `engine/dm/world_step.py` and `engine/dm/roles/world.py`
- [ ] T042 [US2] Loop tests on the fixture with the offline model: offer before roll, withdraw spends nothing, a settled fact stays settled, G3/G4 give an alternative and spend nothing, no roll for talk, in `tests/engine/test_turn_adjudication.py`

**Checkpoint**: US2 works in the fixture scene with the offline model.

---

## Phase 4: User Story 3 — The narration never invents or contradicts the record (P1, Milestone 1)

**Goal**: T7–T12: draft from the record, write on mention, claim check with ≤2 redrafts then the plain
fallback, the T10 screen, deliver and record.

**Independent Test**: the seeded-error set is caught at ≥90% recall with <10% false positives (offline
extraction for the test; the Gemini checker's recall is measured in `evals/`); a 150-turn offline game has
no delivered contradiction of stored state.

### Tests for User Story 3

- [ ] T043 [P] [US3] Build ≥40 seeded-error drafts (≥3 per verdict) with their expected verdicts as data in `tests/seeded_errors/cases.yaml`, and a test that `check_claims` returns the expected verdict for each given the extracted claims, in `tests/seeded_errors/test_verdicts.py`

### Implementation for User Story 3

- [ ] T044 [US3] Implement `check_claims` (12.3.2, `[D]`): the 14 claim classes and 8 verdicts from data-model.md §4, with fixes `write_on_mention | oracle | redraft_to_store | cut | replace_with_slice`; "`subject: unknown` never creates an entity", in `engine/audit/claims.py`
- [ ] T045 [US3] Implement the plain fallback (12.3.3) built from the adjudication record only, in `engine/audit/fallback.py`
- [ ] T046 [US3] Implement the T10 screen checks (12.2.7, 01.11.4, 12.5.6, 12.14.3, 12.14.4, 12.14.9) combining code checks with the Checker's flags, in `engine/audit/screen.py`
- [ ] T107 [US3] Implement the separate safety screen (FR-036): the SAFETY part class handled first at T2 (12.5), and a code check of every draft against the player's lines and veils (12.5.6), in `engine/audit/safety.py`; not part of the Checker call
- [ ] T047 [US3] Implement write-on-mention (PR-00-7, 00.6.6): record each mention with only what the draft implies, settle unsettled properties via Oracle or tables, NPCs via PR-12-5, in `engine/dm/mentions.py`
- [ ] T048 [US3] Implement the Narrator (B/D) and Checker (C) roles in `engine/dm/roles/narrator.py` and `engine/dm/roles/checker.py`; the Checker never sees the narrator's prompt or reasoning (FR-034)
- [ ] T049 [US3] Implement OOF block rendering from state (12.15: OFFER, STATUS, WARNING, REDIRECT, CLARIFY, NEAR_MISS, LAST_CHANCE, RECAP, NOTE) in `engine/dm/oof.py`; fiction carries no numbers or rules words (12.14.4)
- [ ] T050 [US3] Implement T7–T12 in `engine/dm/turn.py` (an OFFER pause with nothing resolved before it skips drafting and checking and delivers the restatement plus the OFFER block): draft, mention, check, ≤2 redrafts, fallback with `review_flag`, screen, deliver, record the `TurnRecord` (data-model.md §4), counters, scene cut marking
- [ ] T051 [US3] Narration-pass tests with the offline model and injected bad drafts: contradiction → redraft to store, unsourced change → cut, two failures → fallback, in `tests/engine/test_turn_narration.py`

**Checkpoint**: a full turn T1–T12 runs in the fixture scene; replay of a recorded fixture game is identical.

---

## Phase 5: User Story 1 — Start a new game and play it to the end (P1, Milestone 1) 🎯 MVP

**Goal**: the actual game from "new game" to an ending, unlimited turns, quit and resume at any point.

**Independent Test**: quickstart.md §2 checklist, first with `--offline`, then by the owner with Gemini.

### Tests for User Story 1

- [x] T052 [P] [US1] World-seed parity: the port reproduces `rules/_process/simulation/12-world-seed.py` exactly on the same seed, in `tests/golden/test_world_seed_parity.py`
- [x] T053 [P] [US1] Birth-draw parity with `gen_birth` reference output, in `tests/golden/test_birth_parity.py`
- [x] T054 [P] [US1] ch.07 worked examples (harm, warning, Threshold, rests) with fixed dice, in `tests/golden/test_worked_examples_07.py`

### Generators

- [x] T055 [P] [US1] Port the world seed (PR-12-9, 12.16) to `engine/gen/world_seed.py`: modes guided / oracle / mixed, steps 1–13, `[SEED n/14]` summaries, one veto per step, the seed check; output the region, place graph, factions-in-brief, threads and the incident
- [x] T056 [P] [US1] Port the birth draw (PR-02-4, `data/gen_birth.yaml`) and the Bent (PR-02-5) to `engine/gen/birth.py`
- [x] T057 [P] [US1] Implement NPC generation and first meeting (PR-12-5): name, pronouns and descriptors fixed at creation, wants and refusals, in `engine/gen/npc.py`
- [x] T058 [P] [US1] Implement improvised adversaries (PR-09-2) in `engine/gen/adversary.py`

### World

- [x] T059 [US1] Implement the place graph (10.1: places, routes, lengths) built from the world seed, and moves that advance time by route length and frame a scene on arrival, in `engine/world/places.py`
- [ ] T060 [US1] Implement scenes (PR-12-7 start and end, the scene record in data-model.md §4, scene tests and counters `h.12.*`) and the Director role (S) in `engine/world/scenes.py` and `engine/dm/roles/director.py`
- [x] T061 [P] [US1] Implement NPC social records (standing, memories, `h.12.npc_memory`) and the chronicle (11.12) in `engine/world/social.py` and `engine/world/chronicle.py`
- [x] T062 [P] [US1] Implement pacing (12.6–12.8): tension, dead air, push, lead injection (PR-12-3), random events (PR-12-6), in `engine/world/pacing.py`

### Character, harm and abilities

- [ ] T063 [US1] Implement creation (PR-02-7 conversation with `[CREATE n/N]` blocks; PR-02-1 workshop, PR-02-2 fast path, PR-02-3 ready-made; PR-02-6 finish: validate, write, show) with the Interpret role, in `engine/dm/creation.py` and `engine/dm/roles/interpret.py`; skipped steps take the stated default; a name is required
- [ ] T064 [US1] Implement the seed flow with the Interpret role in `engine/dm/seed_flow.py`
- [x] T066 [P] [US1] Implement rests (PR-07-8), natural and rest recovery and the daily pass (PR-07-10, M1 parts) in `engine/harm/rest.py`
- [x] T067 [P] [US1] Implement ability use (PR-05-1), Focus and recharge at scene, day and rest (PR-05-4) in `engine/abilities/`
- [ ] T068 [US1] Implement the M1 boundary handlers (plan.md milestone table, about 36) in `engine/time/handlers/h00.py` … `h15.py` (`h.12.intensity_scene` waits for M2), each tagged with its handler id and rule id

### The game around the loop

- [ ] T069 [US1] Implement the opening (12.16.16, PR-12-8 session open): a scene framed at the incident with an open prompt, in `engine/dm/opening.py`
- [ ] T070 [US1] Implement endings: death after the warning, retirement, career end → the epilogue (PR-11-6, simple) from the record → new character in this world or a new world, in `engine/dm/ending.py`
- [ ] T109 [US1] Persist every pause as `pause_opened`/`pause_closed` and every seed and creation answer as `seed_answered`/`creation_answered` (data-model.md §2) so resume re-presents exactly what was open
- [ ] T071 [US1] Implement resume (12.5 recap from the record, then whatever was open: a seed step, a creation step, an offer) and session close (PR-12-8) in `engine/dm/session.py`
- [ ] T072 [US1] Implement the game API exactly as contracts/engine-api.md (`Game.new`, `Game.open`, `submit`, `answer`, `codex`, `new_character`, `turn_record`, `branch`, `spend`, `Game.replay`; `Response`, `Pause`, `OfferView`; errors) in `engine/game.py`; "There is no turn limit, scene limit or session limit anywhere in the API (FR-012)"
- [ ] T073 [US1] Implement codex lookups (shown and available state only, 00.6.4; `rules <id>` prints the card; `journal` and `threads` from the chronicle and recorded knowledge) in `engine/dm/codex.py`
- [ ] T108 [US1] Implement disputes and corrections (12.3.6, PR-12-4): `revert_writes` scoped to the current scene (DL-12-04) and a recorded correction, in `engine/dm/dispute.py`

### Terminal front end

- [ ] T074 [US1] Implement `python -m play` per contracts/cli.md in `play/cli.py` and `play/__main__.py`: menu (New game, Continue, Replay, Report, Quit), command-line equivalents, pause choices by number, slash commands (including `/budget` and `/autocommit`), the between-turns budget prompt, `--offline` flag for the stand-in model, saves in `saves/<name>.db`
- [ ] T075 [US1] Implement `python -m play report <name>` and `replay <name>` in `play/report.py`

### Whole-game tests

- [ ] T076 [US1] Offline end-to-end test: new game (mixed seed) → quick-start creation → 500 turns across scenes and places with a scripted player (talk, risky acts, a fight, a rest, a move, a quit/resume mid-offer) → an ending → epilogue → new character, asserting no exceptions, no turn limit, flat packet size, exact resume at every pause kind and identical replay, in `tests/replay/test_full_game_offline.py`
- [ ] T077 [US1] Record a fixed offline game under `tests/replay/games/` and test it replays identically

**Checkpoint**: Milestone 1 is playable start to finish with `--offline`; ready for the owner's Gemini playtest.

---

## Phase 6: Milestone 1 polish and evaluation

- [ ] T078 [P] Port Feature 002's persona harness to `evals/personas.py` and `evals/run_persona.py` (honest, curious, adversarial); budgeted, Gemini only when run by the owner; offline by default
- [ ] T079 [P] Gemini checker recall run over the seeded-error drafts (paid, owner-run) in `evals/checker_recall.py`; pass gate ≥90% recall, <10% false positives (SC-003)
- [ ] T080 Run `engine/build/coverage.py --milestone 1` and commit its summary to `specs/004-playable-prototype/coverage-m1.md`
- [ ] T081 Write the owner's how-to-play note at the top of `specs/004-playable-prototype/quickstart.md` (key in `.env`, `python -m play`, `--offline`)
- [ ] T082 Write `specs/004-playable-prototype/implementation-results.md`: what works, what is coarse, known issues, offline test numbers; owner playtest results are added after SC-004 games

---

## Phase 7: User Story 4 — Fights, round by round (P2, Milestone 2)

- [ ] T083 [US4] `/speckit-tasks` detail pass for Milestone 2 (ch.06, 09, the rest of 07) appended here
- [ ] T084 [US4] Rounds, tempo, action pool, positions and bands, attacks and defenses, reactions (PR-06-1 … PR-06-10) in `engine/conflict/`
- [ ] T085 [US4] Adversary build from archetypes and bands with behaviours (PR-09-1, PR-09-3, PR-09-5 … PR-09-8) in `engine/gen/adversary.py`
- [ ] T086 [US4] Wounds, dying, afflictions, dread (PR-07-2, PR-07-3, PR-07-9, PR-07-11) in `engine/harm/`; M2 handlers switched on
- [ ] T087 [US4] Conflict golden tests against `06-conflict-sim.py`, `09-adversary-sim.py`, `07-harm-sim.py`

## Phase 8: User Story 5 — Growing from what I actually do (P3, Milestone 3)

- [ ] T088 [US5] Detail pass for Milestone 3 (ch.03, 04, 05, 15.11)
- [ ] T089 [US5] Evidence settlement and tallies (PR-03-1 … PR-03-6) in `engine/growth/evidence.py`
- [ ] T090 [US5] Recognition, offers, picks, provisional status, consolidation (PR-04-1 … PR-04-9) in `engine/growth/recognition.py`
- [ ] T091 [US5] Full abilities, stretching, emulating, rites, miscast, learning (PR-05-2 … PR-05-8) in `engine/abilities/`; training licences (PR-15-8)

## Phase 9: User Story 6 — The road and the dungeon (P4, Milestone 4)

- [ ] T092 [US6] Detail pass for Milestone 4 (ch.10)
- [ ] T093 [US6] Journeys by the watch, navigation, supply, light, weather, the time-tick check, encounters (PR-10-2 … PR-10-5) in `engine/world/travel.py`
- [ ] T094 [US6] Sites, hazards, traps (PR-10-6, PR-10-7, PR-10-9) in `engine/world/sites.py`; parity with `10-sim10_*.py`

## Phase 10: User Story 7 — Things worth having (P5, Milestone 5)

- [ ] T095 [US7] Detail pass for Milestone 5 (ch.08)
- [ ] T096 [US7] Loot, item abilities, crafting, buying and selling, identifying, repair (PR-08-1 … PR-08-9) in `engine/items/` and `engine/gen/`; parity with `08-loot-sim.py`, `08-craft-sim.py`

## Phase 11: User Story 8 — A world that moves without me (P6, Milestone 6)

- [ ] T097 [US8] Detail pass for Milestone 6 (ch.11, 15.5–15.9)
- [ ] T098 [US8] Factions and the World Turn, the Season Turn, hooks, rumours (PR-11-1 … PR-11-8) in `engine/world/living.py`; parity with `11-world-sim.py`
- [ ] T099 [US8] Social and investigation procedures (PR-15-1 … PR-15-7) in `engine/social/`

## Phase 12: User Story 9 — Companions, downtime and legacy (P7, Milestone 7)

- [ ] T100 [US9] Detail pass for Milestone 7 (ch.16, 15.10, 15.12–15.13, 11.13, 07 legacy)
- [ ] T101 [US9] Allies, loyalty, the held line, ally death (PR-16-1 … PR-16-12) in `engine/company/`
- [ ] T102 [US9] The downtime week (PR-15-9), long projects, full retirement and legacy in `engine/downtime/`

## Phase 13: Cross-cutting (after Milestone 1, any time)

- [ ] T103 [P] `TODO(CROSS_FAMILY_CHECKER)`: second-family checker adapter, before anyone but the owner plays
- [ ] T104 [P] Web front end (FastAPI + htmx + SSE) in `play/web/` over the same game API
- [ ] T105 [P] Hosting notes for remote players (one SQLite file per game, Principle IV)

---

## Dependencies & Execution Order

- **Setup (T001–T005)** → **Foundational (T006–T027)** → **US2 (T028–T042)** → **US3 (T043–T051)** →
  **US1 (T052–T077)** → **Polish (T078–T082)**. Milestones 2–7 follow in order; each starts with its detail
  pass and must keep saved M1 games loading (FR-040).
- Inside Foundational: T006 before everything that reads rules; T010–T012 before T013, T015–T017; T021
  before T022–T025; T026 needs T006 and T012.
- Inside US1: generators (T055–T058) and harm/abilities (T065–T067) are independent of each other; the
  game API (T072) needs T063–T071; the CLI (T074) needs T072.

## Parallel Opportunities

- Foundational: data and card compiler (T006–T009), store and time (T010–T018), model layer (T021–T027)
  are three separate workstreams once T006 exists.
- US2: T028–T033 in parallel; T034–T038 in order.
- US1: the four generators, harm, rests and abilities all in parallel.

## Implementation Strategy

1. **Milestone 1 first (US2 → US3 → US1).** Stop and validate with the offline end-to-end test (T076),
   then hand to the owner for a Gemini playtest (quickstart.md §2–3).
2. **Coarse, honest, logged.** Anything a later milestone builds is handled by the pipeline's anchors or
   skipped with a `handler_skipped` event, never faked.
3. **Each later milestone** starts with a `/speckit-tasks` detail pass, adds modules, and ends with an
   owner playtest and a results note.

## Notes

- Every `[D]` function carries a `# rule: <id>` comment; coverage.py reads them.
- No test calls a paid model. `evals/` runs are owner-run and budgeted.
- Commit after each task group with ruff, pyright and pytest clean.
