---

description: "Task list for feature 002: Long-Horizon Consistency Stress Test"
---

# Tasks: Long-Horizon Consistency Stress Test

**Input**: Design documents from `specs/002-long-horizon-consistency-test/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/pipeline-prompts.md, quickstart.md

**Tests**: Included for the same reason as Feature 001 — plan.md's Technical Context names
`pytest` for the structurally-checkable parts (`test_scenario_schema.py`) as a required
deliverable, not optional practice.

**Organization**: Tasks are grouped by the three user stories in spec.md (P1/P2/P3), each
independently testable per its own Acceptance Scenarios.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependency on an incomplete task)
- **[Story]**: US1, US2, or US3, per spec.md
- File paths are exact, matching plan.md's Project Structure

## Path Conventions

Single project (unchanged from Feature 001): `src/`, `tests/unit/`, `tests/probe/` at
repository root. This feature adds new files to those same directories; it does not introduce
a new module boundary.

---

## Phase 1: Setup

- [X] T001 [P] Add `*.scenario.json` to `.gitignore` for generated scenario seed files — the same category of machine-generated, per-run artifact as Feature 001's `*.session.json` pattern

**Checkpoint**: No new dependencies to install (plan.md confirms `google-genai`/`pytest` are
reused unchanged) — Setup is intentionally this thin.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The generic state model, structural validators, the three-stage extraction calls,
the isolation check, the player persona, and the conflict auditor — the atomic pieces every
user story composes. No user story work can begin until this phase is complete.

- [X] T002 Implemented `TrajectoryNode`, `Commitment`, `WorldState`, `ConflictRecord`, `SessionOutcome` dataclasses in `src/world_state.py`. *Amended: added a `references: list[str]` field to `TrajectoryNode`/`Commitment` (data-model.md updated to match) — needed to make key-reference validation deterministic rather than fragile free-text parsing.*
- [X] T003 Implemented `validate_trajectory`, `validate_commitments`, `validate_world_state_references` in `src/world_state.py`.
- [X] T004 [P] Unit tests in `tests/unit/test_scenario_schema.py` — **12/12 passing** (24/24 total with Feature 001's suite).
- [X] T005 JSON load/save for `WorldState`/`SessionOutcome` in `src/world_state.py`.
- [X] T006 Implemented `extract_trajectory`/`extract_commitments`/`extract_initial_facts` in `src/scenario_pipeline.py`, using a new shared `dm_agent.call_json` helper (JSON output mode). **Executed live against Gemini and PASSED** end-to-end on a real campaign outline: 6-node trajectory, 5 commitments, and a fully-populated initial `WorldState`, all passing their respective validators on the first real run.
- [X] T007 Implemented `check_isolation` in `src/scenario_pipeline.py`. **Executed live**: correctly reported `isolated: True, violations: []` on the same real scenario.
- [X] T008 Implemented `next_action` in `src/player_agent.py`. **Executed live** for both modes on the same test prompt — adversarial persona proposed an exploit (removing door hinges instead of picking the lock), natural persona proposed a cautious, in-character action. Visibly different behavior per mode, as intended.
- [X] T009 Implemented `check_turn` in `src/auditor.py`. **Executed live** on a matched pair: a consistent narration correctly returned no conflict; a deliberately contradictory narration (door narrated as opening despite `status_flags.storeroom_locked: true`) was correctly caught as a `fact` conflict, category `status_flags`, with an accurate description.

**Checkpoint**: Foundation ready — every atomic piece (state model, validators, extraction
calls, isolation check, player persona, auditor) exists and is unit-tested where testable in
isolation (T004). User story implementation can now begin.

---

## Phase 3: User Story 1 - Construct a synthetic long-session scenario without playing real turns (Priority: P1) 🎯 MVP

**Goal**: Given a short campaign outline, produce a validated trajectory, commitment set, and
initial `WorldState` that passes the isolation check (spec.md FR-001, FR-002).

**Independent Test**: Given a short, original campaign outline, the pipeline produces a
trajectory, commitment set, and initial fact set, and an automated check confirms no fact
leaks future-trajectory knowledge — no long session needs to run yet to verify this story.

### Implementation for User Story 1

- [X] T010 [US1] Implemented `generate_scenario(outline)` in `src/scenario_pipeline.py`, with bounded retry (regenerating only the initial-facts stage, up to 2 extra attempts) on isolation failure, raising `IsolationViolationError` if still unisolated — a hard block, not a warning, per spec.md's Edge Cases.
- [X] T011 [P] [US1] Wrote 3 original outlines (outpost, lighthouse, archive) in `tests/probe/campaign_outlines.py`.
- [X] T012 [US1] Implemented the scenario-only verification mode in `tests/probe/run_long_horizon_test.py`. **Executed live — SC-001 fully PASSED on the first attempt, zero isolation retries needed**: outpost (6 nodes, 5 commitments), lighthouse (7 nodes, 5 commitments), archive (7 nodes, 5 commitments) — all isolated, all with sensibly populated resources/possessions/status_flags categories.

**Checkpoint**: User Story 1 is fully functional and testable independently — a validated,
isolation-checked synthetic scenario can be produced for real, for any of the 3 outlines,
before any turn-by-turn session logic exists.

---

## Phase 4: User Story 2 - Run real turns on top of the seeded scenario and detect conflicts (Priority: P2)

**Goal**: Run a real, live sequence of turns on a seeded scenario using Feature 001's
unmodified tool-calling architecture, driven by a scripted player persona, detecting
fact/commitment/player-input conflicts as they occur (spec.md FR-003 through FR-007).

**Independent Test**: Run one full scripted session, up to a turn cap or until a
conflict/termination event, and produce a turn-by-turn conflict log using only Feature 001's
existing tools plus the new auditor.

### Implementation for User Story 2

- [X] T013 [US2] Implemented `run_session()` in `tests/probe/run_long_horizon_test.py`, driving `player_agent.next_action()` straight into Feature 001's `dm_agent.run_turn()` (now accepting optional `tool_schemas`/`system_prompt` params, added non-breakingly — Feature 001's own callers are unaffected), then `auditor.check_turn()` each turn. *Amendment found during implementation, documented in contracts/pipeline-prompts.md: `roll_check`/`update_state` stayed byte-for-byte unmodified as FR-003 required, but two new tools (`update_resource`, `set_fact`) were added additively in `src/world_state.py` since `WorldState`'s extra categories had no way to be written under the original three.*
- [X] T014 [US2] Implemented termination logic + `SessionOutcome` construction + interval checkpoints. **Known, documented simplification**: `termination_reason` only distinguishes `conflict` vs. `turn_cap_reached` (no separate "natural ending" detector was built); `succeeded` checks achievement-commitment satisfaction, but the auditor only detects violations, not satisfactions, so `succeeded` is currently near-synonymous with `survived`. Found and fixed a real bug live: short runs (below the checkpoint interval) produced zero checkpoints, failing FR-008's requirement — fixed to always guarantee a final checkpoint.
- [X] T015 [P] [US2] Wired `--turns`/`--runs`/`--personas`/`--scenarios-only` into `run_long_horizon_test.py`, defaulting to `--turns 15 --runs 1 --personas natural`. **Executed live at `--turns 3 --runs 1`**: full session ran opening + 3 turns with the natural persona, zero conflicts, correct `SessionOutcome` serialized to disk.

**Checkpoint**: User Stories 1 and 2 both work independently — a full, real, tool-calling
session can run on a seeded scenario and produce a complete conflict log.

---

## Phase 5: User Story 3 - Report a category-resolved degradation profile, not a single pass/fail (Priority: P3)

**Goal**: Produce a summary report separating survival from success, broken down by conflict
type and seeded state category, at fixed checkpoints (spec.md FR-008).

**Independent Test**: Given one or more completed run logs, the report states
turn-of-first-conflict, conflict-type breakdown, and category attribution per run, plus
aggregate survival/success rates across runs.

### Implementation for User Story 3

- [ ] T016 [US3] Implement the aggregate report generator in `run_long_horizon_test.py`: per-run and aggregate survival/success rates, turn-of-first-conflict (and its normalized position), and a conflict-type × state-category breakdown table, per FR-008
- [ ] T017 [US3] Add the NCP-Bench baseline comparison to the report's output (SC-003): print this run's measured fact-conflict rate and turn-of-first-conflict alongside the cited published figures (40-68% fact-conflict rate among failing episodes, 42% survival at turn 20 for the best tested model), explicitly labeled as a comparison point, not a pass/fail gate
- [ ] T018 [P] [US3] Implement the SC-004 category-coverage check: across a batch of runs, verify at least one deliberate test action targeted each of the four seeded state categories (the additional numeric resource, possessions, position, status/existence) and that the resulting conflict-or-no-conflict outcome is correctly category-attributed for all four; flag in the report if any category was never exercised

**Checkpoint**: All three user stories are independently functional — the harness now produces
the category-resolved degradation profile this feature exists to generate, comparable directly
to the published benchmark literature.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T019 [P] Run quickstart.md Step 1 (scenario-only check) live against all 3 campaign outlines and confirm isolation-check results
- [ ] T020 Run quickstart.md Step 2 (one short ~15-20 turn run) live; verify the auditor and category-attribution logic behave sensibly before scaling up, per research.md's sequencing decision — fix any issues found here before T021, since this is deliberately the cheap checkpoint
- [ ] T021 Run quickstart.md Step 3 (the full SC-002 batch: 3 scenarios × 5+ runs mixing both persona conditions) live and record the actual results — survival/success rates, category breakdown, NCP-Bench comparison — in a new `specs/002-long-horizon-consistency-test/implementation-results.md`, explicitly comparing against Feature 001's `implementation-results.md` and the published benchmark figures; per plan.md's framing, most runs not reaching the turn cap intact is an expected, valid finding, not a failure to hide
- [ ] T022 [P] Confirm no new dependencies were actually introduced (plan.md's claim) by diffing `requirements.txt` before/after this feature's implementation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories.
- **User Stories (Phase 3-5)**: All depend on Foundational. US1 has no dependency on US2/US3.
  US2 depends on US1's `generate_scenario` existing (it needs a scenario to run turns on), but
  is independently testable once that exists. US3 depends on US2's session loop producing
  `SessionOutcome`/`ConflictRecord` data to report on, but is a pure analysis/reporting layer —
  it adds no new mechanics of its own.
- **Polish (Phase 6)**: Depends on all three user stories being complete. T020 specifically
  gates T021 (per research.md's sequencing decision) — do not launch the full batch before the
  short validation run has been checked.

### Parallel Opportunities

- T001 can run in parallel with anything (independent of code).
- T004 can run in parallel with T005 once T002/T003 exist (different files/concerns).
- T011 can run in parallel with T010 (writing outlines doesn't depend on the orchestrator
  function existing yet, though both are needed together for T012).
- T015 and T014 touch the same file (`run_long_horizon_test.py`) — not actually parallelizable
  with each other despite T015 being marked [P] (parallel with T013's different concern within
  the same file is still a same-file conflict in practice; treat T013→T014→T015 as sequential).
- T018 can run in parallel with T017 (different concerns within the same report, but
  independent logic).

---

## Parallel Example: Phase 2 (Foundational)

```bash
# Once T002/T003 (world_state.py) exist, these two can run together:
Task: "Unit tests for validators in tests/unit/test_scenario_schema.py"
Task: "JSON load/save for WorldState/SessionOutcome in src/world_state.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (Setup) and Phase 2 (Foundational) — the state model, validators,
   extraction calls, isolation check, player persona, and auditor.
2. Complete Phase 3 (User Story 1) — a validated, isolation-checked scenario, for real, for any
   of 3 original outlines.
3. **Stop and validate**: this alone already answers whether the synthetic-construction half of
   the design (the part directly adapted from NCP-Bench) actually works for our own campaign
   material, before spending any budget on long live sessions.

### Incremental Delivery

1. Setup + Foundational → every atomic piece exists and is tested where testable in isolation.
2. US1 → synthetic scenario construction works for real, for 3 distinct outlines.
3. US2 → real turns run on top via Feature 001's unmodified tools, producing a real conflict
   log — the actual architectural question this feature exists to answer.
4. US3 → the category-resolved report that turns raw conflict logs into the deliverable
   insight, comparable to the published benchmark baselines.
5. Polish → the three-step quickstart validation (cheap check → short run → full batch), with
   the short run deliberately gating the expensive batch.

## Notes

- No cross-story file conflicts of concern: US1's `scenario_pipeline.py` additions, US2's
  session-loop additions to `run_long_horizon_test.py`, and US3's reporting additions to the
  same file are sequential concerns within a shared file, not independent work that could
  proceed out of order.
- This feature makes substantially more real, billed API calls than Feature 001 — the
  Polish phase's sequencing (T019 → T020 → T021) exists specifically to catch problems cheaply
  before the expensive full batch, and should not be collapsed into a single step.
- No game mechanics are introduced here, per spec.md's Assumptions — nothing in this task list
  should grow into ruleset/content work.
