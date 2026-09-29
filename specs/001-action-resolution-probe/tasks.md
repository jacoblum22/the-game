---

description: "Task list for feature 001: Action Resolution Probe"
---

# Tasks: Action Resolution Probe

**Input**: Design documents from `specs/001-action-resolution-probe/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/tools.md, quickstart.md

**Tests**: Included. `plan.md`'s Technical Context explicitly names `pytest` for `resolution.py`
as a required deliverable, not optional practice, so unit tests are generated for it.

**Organization**: Tasks are grouped by the three user stories in spec.md (P1/P2/P3), each
independently testable per its own Acceptance Scenarios.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependency on an incomplete task)
- **[Story]**: US1, US2, or US3, per spec.md
- File paths are exact, matching plan.md's Project Structure

## Path Conventions

Single project (per plan.md's Structure Decision): `src/`, `tests/unit/`, `tests/probe/` at
repository root.

---

## Phase 1: Setup

- [ ] T001 Create the project structure at repository root per plan.md's Project Structure: `src/`, `tests/unit/`, `tests/probe/`
- [ ] T002 Initialize Python dependencies in `requirements.txt` at repository root: `anthropic`, `pytest` (per plan.md's Primary Dependencies/Testing)
- [ ] T003 [P] Add `.env.example` at repository root documenting `ANTHROPIC_API_KEY` and a model-name environment variable, per research.md's "model is a runtime-configurable parameter" decision

**Checkpoint**: Repo structure and dependency list exist; nothing runnable yet.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The state model, deterministic resolution logic, tool boundary, and agent loop that
all three user stories depend on. No user story work can begin until this phase is complete.

- [ ] T004 Implement `CharacterState`, `ActionAttempt`, and `SessionLog` data structures in `src/state.py` per data-model.md's field lists, including the validation rule `0 <= resource_current <= resource_max`
- [ ] T005 Implement `SessionLog` JSON load/save functions in `src/state.py` (flat file per plan.md's Storage decision — no database)
- [ ] T006 [P] Implement the pure `resolve(dc, modifier)` function in `src/resolution.py` per research.md's exact formula: roll 1d20, total = roll + modifier; Critical Success if total >= dc+10 OR raw roll is a natural 20; Critical Failure if total <= dc-10 OR raw roll is a natural 1; otherwise Success if total >= dc, else Failure. No network calls, no I/O.
- [ ] T007 [P] Unit tests for `src/resolution.py` in `tests/unit/test_resolution.py` covering: a normal Success, a normal Failure, Critical Success via the +10 threshold, Critical Success via a natural 20 below threshold, Critical Failure via the -10 threshold, Critical Failure via a natural 1 above threshold, and the exact-boundary cases (total == dc, total == dc+10, total == dc-10)
- [ ] T008 Implement tool schemas and handler functions for `roll_check`, `get_state`, and `update_state` in `src/tools.py` per contracts/tools.md's exact input/output shapes, wrapping `resolution.py` and `state.py` — this module is the literal boundary between free narration and deterministic mechanics (Principle I, Pattern P13)
- [ ] T009 Implement `src/dm_agent.py`: an Anthropic API client wrapper that reads the model name from the environment variable added in T003, a system prompt encoding Pattern P8 (degrees-of-success as the default resolution), Pattern P12 (limitation/weakness/cost as distinct vocabulary), Pattern P16 (never leave a silent dead end), Pattern P17 (graduated information reveal for compound/bundled questions), and Principle III's resolved default (the model's own judgment for rule-breakdown situations, no separate gate) — and the tool-use loop wired to `src/tools.py`

**Checkpoint**: State model, resolution math, tool boundary, and agent loop all exist and are unit-tested where testable in isolation (T007). User story implementation can now begin.

---

## Phase 3: User Story 1 - Resolve a single ambiguous player action (Priority: P1) 🎯 MVP

**Goal**: Given one freeform action description, the AI DM produces a computed degree-of-success
and narrates an outcome consistent with it (spec.md FR-001 through FR-004).

**Independent Test**: Give the AI DM one freeform action description with real stakes and check
(a) it produces a computed degree via `roll_check`, and (b) its narration doesn't contradict
that degree — no character creation, combat, or other system involved.

### Implementation for User Story 1

- [ ] T010 [US1] Implement `src/main.py` as the CLI entry point: initialize a `CharacterState`, run one interactive turn loop reading player input and printing the DM's narration
- [ ] T011 [US1] In `dm_agent.py`'s system prompt, add the resolution-need classification instruction so the model recognizes stakes-free descriptions and does not call `roll_check` for them (FR-002)
- [ ] T012 [US1] Wire the tool-use loop so that, when resolution is needed, `roll_check` is called before narration is produced, and the narrated outcome must be stated consistently with the returned degree (FR-003, FR-004)
- [ ] T013 [P] [US1] Implement a minimal `tests/probe/run_scripted_session.py` that sends one fixed, real-stakes action description through the live loop, asserts a computed degree was produced, and logs the turn — covers spec.md's User Story 1 Acceptance Scenarios 1-2

**Checkpoint**: User Story 1 is fully functional and testable independently — a single action can be resolved end-to-end with real tool-calling.

---

## Phase 4: User Story 2 - Track state consistently across a short sequence (Priority: P2)

**Goal**: A tracked resource updates correctly and stays consistent with narration across at
least 10 sequential actions (FR-005 through FR-007).

**Independent Test**: Run a sequence of at least 10 actions in one session; after each one,
check whether the persisted state matches what was narrated.

### Implementation for User Story 2

- [ ] T014 [US2] Extend `dm_agent.py`'s system prompt/loop to call `get_state` before any turn where current state might matter, and `update_state` whenever an outcome implies a resource change (FR-005, FR-006)
- [ ] T015 [US2] Extend `SessionLog` in `src/state.py` to append one `ActionAttempt` per turn, including `state_before`/`state_after` snapshots, per data-model.md's field list and its validation note (state_after must equal state_before unless narration/degree implies otherwise)
- [ ] T016 [P] [US2] Extend `tests/probe/run_scripted_session.py` to run a fixed sequence of at least 10 actions — mirroring the turn variety already exercised in [probe-results.md](probe-results.md) (investigation, a compound question, a combat attempt, a time-pressure edge case) — and print the full per-turn log

**Checkpoint**: User Stories 1 and 2 both work independently — a full session's state stays traceable turn by turn.

---

## Phase 5: User Story 3 - Detect when narration and state disagree (Priority: P3)

**Goal**: Any divergence between narration and persisted state is identifiable from logged
output alone, not by re-reading prose and guessing (FR-008).

**Independent Test**: Review logged output after a session and confirm any mismatch is
identifiable from that log alone.

### Implementation for User Story 3

- [ ] T017 [US3] Implement a consistency-check function in `tests/probe/run_scripted_session.py` that computes SC-002 (count of turns where narration contradicts its own computed degree) and SC-003 (every state change traceable to a specific `update_state` call) from the session log
- [ ] T018 [US3] Implement the SC-004 check in the same script: confirm every stakes-free turn correctly skipped `roll_check`
- [ ] T019 [US3] Print a final summary (SC-001 through SC-004 results) at the end of `tests/probe/run_scripted_session.py`, matching the expected output documented in quickstart.md

**Checkpoint**: All three user stories are independently functional — the scripted harness now produces the automated SC-002 number the earlier relayed-chat probe could only estimate by hand.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T020 [P] Pin dependency versions in `requirements.txt` (`anthropic`, `pytest`)
- [ ] T021 [P] Add a short usage note in `src/main.py`'s module docstring cross-referencing quickstart.md
- [ ] T022 Run quickstart.md's full validation end-to-end (`pytest tests/unit`, one interactive session, the scripted harness) and record the actual SC-001 through SC-004 results in a new `specs/001-action-resolution-probe/implementation-results.md`, explicitly comparing against probe-results.md's earlier relayed-chat findings — per plan.md's framing, a worse result here is a valid finding, not a bug to hide

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories.
- **User Stories (Phase 3-5)**: All depend on Foundational. US1 has no dependency on US2/US3.
  US2 depends on US1's loop existing (T010-T012) since it extends the same turn loop, but is
  independently testable once extended. US3 depends on US2's per-turn logging (T015) to have
  anything to check, but is a pure analysis layer — it adds no new mechanics.
- **Polish (Phase 6)**: Depends on all three user stories being complete.

### Parallel Opportunities

- T006 and T007 can run in parallel with each other once T004/T005 exist (resolution.py has no
  dependency on state.py).
- T003 can run in parallel with T001/T002.
- T013, T016 are separate extensions of the same file (`run_scripted_session.py`) — not
  actually parallelizable with each other despite both touching a story-specific slice; treat
  as sequential in practice even though only T013 is marked [P] (parallel with T012 in a
  different file).
- T020 and T021 can run in parallel with each other.

---

## Parallel Example: Phase 2 (Foundational)

```bash
# Once T004/T005 (state.py) are done, these two can run together:
Task: "Implement resolve(dc, modifier) in src/resolution.py per research.md's formula"
Task: "Unit tests for src/resolution.py in tests/unit/test_resolution.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (Setup) and Phase 2 (Foundational) — this is the real engineering
   foundation: state model, resolution math, the tool boundary, the agent loop.
2. Complete Phase 3 (User Story 1) — one action, resolved for real, with real tool-calling.
3. **Stop and validate**: run `tests/probe/run_scripted_session.py` in its T013 form against a
   single real action. This alone already answers the question this feature exists to test —
   does real tool-calling + narration consistency hold up outside a relayed chat — for the
   simplest case.

### Incremental Delivery

1. Setup + Foundational → foundation ready.
2. US1 → single-action resolution works for real → first genuine test of Pattern P13 beyond the
   relayed-chat probe.
3. US2 → state tracking across a real sequence → directly comparable to probe-results.md's
   13-turn session, but now automated instead of human-relayed.
4. US3 → the actual measurement instrument (SC-002/SC-003 as real numbers, not a self-report)
   this whole feature was built to produce.
5. Polish → pin dependencies, document, and run the full comparison against the earlier
   relayed-chat results.

## Notes

- No cross-story file conflicts: `main.py` (US1), `state.py`'s SessionLog extension (US2), and
  `run_scripted_session.py`'s analysis functions (US3) touch different concerns even where they
  share a file, so stories stay independently reviewable even though the file list overlaps.
- Commit after each phase checkpoint, consistent with how the constitution and spec commits
  were staged earlier in this project.
- This feature remains deliberately free of any game mechanics beyond the placeholder DC scale
  and one placeholder resource, per spec.md's Assumptions — nothing here should grow scope.
