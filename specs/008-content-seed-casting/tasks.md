# Tasks: Content seed, casting and the reduced case (008 part A)

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md), [data-model.md](data-model.md),
[contracts/api.md](contracts/api.md). Tests are requested by the brief's gates.

## Phase 1: Setup

- [ ] T001 Record the before-measurement: `evals/longhorizon.py --mode scripted --lines 300` view tokens (scratchpad)

## Phase 2: Foundational

- [ ] T002 Port `keyed`, `place_type`, `role_key`, `in_haven`, `pick_n`, `fill_doc`, `walk_on` (seed-time), `lead_holder_place`, `make_document`, `cast_pick` to `engine/gen/_seed_packs.py` (reference lines 1445-1556, draw-for-draw)
- [ ] T003 Port `reduced_case` and `validate_case` to `engine/gen/case.py` (reference 1557-1640; `investigation.yaml#reduced_case` numbers)

## Phase 3: US1 the opening has real material (P1)

- [ ] T004 [US1] Port `pack_places`, `pack_npcs`, `seed_packs`, `check_packs` to `engine/gen/_seed_packs.py`
- [ ] T005 [US1] Apply `seed_packs` in `WorldSeed.record()`; map pack failures to step 13 in `run_check` (`engine/gen/world_seed.py`)
- [ ] T006 [US1] Run the 7 pack checks in `check_seed` (`engine/gen/_seed_check.py`)
- [ ] T007 [US1] `write_world` writes walk-ons, documents (object + `text` fact + position) and meta `world.cases` (`engine/dm/seed_flow.py`); seal NPC `knowledge` (`engine/world/places.py` NPC_SEALED)
- [ ] T008 [US1] `scene_setting` renders the present place's look, furniture and exits (`engine/dm/packet.py`)
- [ ] T009 [P] [US1] Parity against the reference's packed record + packed check (`tests/golden/test_world_seed_parity.py`); seed-check unit tests and pack determinism (`tests/engine/test_seed_packs.py`)

## Phase 4: US2 the incident is a real case (P1)

- [ ] T010 [US2] `case.py` store side: `cases`, `world_rec`, `story_option`, `case_covering`, `case_for_question`, `write_case`, `pointer` (core holder first), `mark_found`, `audit_case`
- [ ] T011 [US2] Retire `bind_incident`/`SUBJECTS`; `incident_line` over the case; `settle_who` via case then cast (`engine/dm/incident.py`); call site in `engine/dm/session.py`
- [ ] T012 [US2] `h.15.placement_audit` live in M1 (`engine/time/handlers/__init__.py`, `engine/time/handlers/h15.py`)
- [ ] T013 [P] [US2] Tests: PR-15-6 validity, determinism, 30 openings valid with the core at the opening place, on-demand case, audit (`tests/engine/test_case.py`); rewrite `tests/engine/test_incident.py`

## Phase 5: US3 casting (P2)

- [ ] T014 [US3] `engine/gen/cast.py`: `base_pool`, `cast`, `pointer_target` (`social.yaml#cast`)
- [ ] T015 [P] [US3] Tests (`tests/engine/test_cast.py`)

## Phase 6: US4 local names, inexhaustible names (P2)

- [ ] T016 [US4] `start_knowledge` (I-149) in `engine/dm/incident.py`, called at the opening
- [ ] T017 [US4] `person_name` syllable fallback (`engine/gen/_seed_lib.py`)
- [ ] T018 [P] [US4] Tests: local vs outsider names (`tests/engine/test_incident.py`); 300+ walk-ons of one people never raise (`tests/engine/test_gen_npc.py`)

## Phase 7: Polish

- [ ] T019 Full suite, ruff, pyright; re-record replay games (`py -3.12 -m tests.replay.record_games`)
- [ ] T020 After-measurement (long-horizon scripted, 320 lines); `CONVENTIONS.md` engine/gen section; `specs/008-content-seed-casting/implementation-results.md`; ledger rows if any

## Dependencies

T002-T003 before all stories; US1 (T004-T009) before US2's seed-time path (T011 reads the packed world);
US3 (T014) before T011's `settle_who` casting. US4 independent. Parallel: the test tasks marked [P].

## Strategy

MVP = US1 + US2 (the seed and its case); US3/US4 complete the brief. Commit after each phase.
