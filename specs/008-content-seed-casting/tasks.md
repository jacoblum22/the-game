# Tasks: Content seed, casting and the reduced case (008 part A)

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md), [data-model.md](data-model.md),
[contracts/api.md](contracts/api.md). Tests are requested by the brief's gates.

## Phase 1: Setup

- [X] T001 Record the before-measurement: `evals/longhorizon.py --mode scripted --lines 300` view tokens (scratchpad)

## Phase 2: Foundational

- [X] T002 Port `keyed`, `place_type`, `role_key`, `in_haven`, `pick_n`, `fill_doc`, `walk_on` (seed-time), `lead_holder_place`, `make_document`, `cast_pick` to `engine/gen/_seed_packs.py` (reference lines 1445-1556, draw-for-draw)
- [X] T003 Port `reduced_case` and `validate_case` to `engine/gen/case.py` (reference 1557-1640; `investigation.yaml#reduced_case` numbers)

## Phase 3: US1 the opening has real material (P1)

- [X] T004 [US1] Port `pack_places`, `pack_npcs`, `seed_packs`, `check_packs` to `engine/gen/_seed_packs.py`
- [X] T005 [US1] Apply `seed_packs` in `WorldSeed.record()`; map pack failures to step 13 in `run_check` (`engine/gen/world_seed.py`)
- [X] T006 [US1] Run the 7 pack checks in `check_seed` (`engine/gen/_seed_check.py`)
- [X] T007 [US1] `write_world` writes walk-ons, documents (object + `text` fact + position) and meta `world.cases` (`engine/dm/seed_flow.py`); seal NPC `knowledge` (`engine/world/places.py` NPC_SEALED)
- [X] T008 [US1] `scene_setting` renders the present place's look, furniture and exits (`engine/dm/packet.py`)
- [X] T009 [P] [US1] Parity against the reference's packed record + packed check (`tests/golden/test_world_seed_parity.py`); seed-check unit tests and pack determinism (`tests/engine/test_seed_packs.py`)

## Phase 4: US2 the incident is a real case (P1)

- [X] T010 [US2] `case.py` store side: `cases`, `world_rec`, `story_option`, `case_covering`, `case_for_question`, `write_case`, `pointer` (core holder first), `mark_found`, `audit_case`
- [X] T011 [US2] Retire `bind_incident`/`SUBJECTS`; `incident_line` over the case; `settle_who` via case then cast (`engine/dm/incident.py`); call site in `engine/dm/session.py`
- [X] T012 [US2] `h.15.placement_audit` live in M1 (`engine/time/handlers/__init__.py`, `engine/time/handlers/h15.py`)
- [X] T013 [P] [US2] Tests: PR-15-6 validity, determinism, 30 openings valid with the core at the opening place, on-demand case, audit (`tests/engine/test_case.py`); rewrite `tests/engine/test_incident.py`

## Phase 5: US3 casting (P2)

- [X] T014 [US3] `engine/gen/cast.py`: `base_pool`, `cast`, `pointer_target` (`social.yaml#cast`)
- [X] T015 [P] [US3] Tests (`tests/engine/test_cast.py`)

## Phase 6: US4 local names, inexhaustible names (P2)

- [X] T016 [US4] `start_knowledge` (I-149) in `engine/dm/incident.py`, called at the opening
- [X] T017 [US4] `person_name` syllable fallback (`engine/gen/_seed_lib.py`)
- [X] T018 [P] [US4] Tests: local vs outsider names (`tests/engine/test_incident.py`); 300+ walk-ons of one people never raise (`tests/engine/test_gen_npc.py`)

## Phase 7: Polish

- [X] T019 Full suite, ruff, pyright; re-record replay games (`py -3.12 -m tests.replay.record_games`)
- [X] T020 After-measurement (long-horizon scripted, 320 lines); `CONVENTIONS.md` engine/gen section; `specs/008-content-seed-casting/implementation-results.md`; ledger rows if any

## Dependencies

T002-T003 before all stories; US1 (T004-T009) before US2's seed-time path (T011 reads the packed world);
US3 (T014) before T011's `settle_who` casting. US4 independent. Parallel: the test tasks marked [P].

## Strategy

MVP = US1 + US2 (the seed and its case); US3/US4 complete the brief. Commit after each phase.

---

# Tasks: part B, the answer ladder (PR-12-10)

- [X] T021 [US5] `engine/dm/answer.py`: index, tier route, store, pack, propose and ratify, pointer, volunteer, depth by reach
- [X] T022 [US5] Role `proposer`: base Role, schema + default, prompt, call module, offline heuristic, Gemini cap, cards, fixture, smoke list
- [X] T023 [US5] `world_step.deliver_learning` -> the ladder (Talk/Observe/Recall beats, SPEECH questions); retire `_talk_answers`, `_who_questions`, `_WHAT_ASKED`, `_NAME_OF`, `_WHO_ASKED`, `_ASKS_NAME`, `learn_names`, the concrete-thing notes, the thread and first-present fallbacks
- [X] T024 [US5] `npc_layer` Talk outcome wording by reach; skip SPEECH-answered NPCs
- [X] T025 [US6] Consequential route through the case graph; `mark_found` on delivery; Observe at a holder place/object/document; retire `incident.settle_who` (`turn._fiction_questions` -> `answer.who_answer`)
- [X] T026 [US5] `claims._learning_success` unreachable, `TODO(008-B retire)` (009-B's file: one line)
- [X] T027 [P] [US5] Offline Reader: question kinds on declared asks
- [X] T028 [P] [US5/US6] Tests `tests/engine/test_answer.py`: each rung, depth by reach, never-empty, ask-twice, does-not-know recorded, consequential routing, offline determinism, 30 seeded openings within 3 turns; update the retired paths' tests
- [X] T029 `evals/longhorizon.py`: empty-success rate, ask-twice consistency
- [X] T030 Full suite, ruff, pyright; re-record replay; long-horizon scripted; `implementation-results.md` part-B gate table; CONVENTIONS section
