---

description: "Task list for feature 003: Ability Acquisition Probe"
---

# Tasks: Ability Acquisition Probe

**Input**: Design documents from `specs/003-ability-acquisition-probe/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/tools.md, quickstart.md

**Tests**: Included for the same reason as Feature 001/002 — plan.md's Technical Context names
`pytest` for the deterministic parts (`test_ability_pool.py`) as a required deliverable, and
User Story 1's whole point is that this is testable with zero live API calls.

**Organization**: Tasks are grouped by the three user stories in spec.md (P1/P2/P3), each
independently testable per its own Acceptance Scenarios.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependency on an incomplete task)
- **[Story]**: US1, US2, or US3, per spec.md
- File paths are exact, matching plan.md's Project Structure

## Path Conventions

Single project (unchanged from Feature 001/002): `src/`, `tests/unit/`, `tests/probe/` at
repository root. This feature adds new files to those same directories and extends two existing
ones (`world_state.py`, `auditor.py`); it does not introduce a new module boundary.

---

## Phase 1: Setup

- [X] T001 Confirm the existing Feature 001/002 environment still works: `pytest tests/unit/`
  passes and `GEMINI_API_KEY` is set, per quickstart.md's Prerequisites — no new dependencies
  are added by this feature (plan.md's Technical Context), so Setup is intentionally this thin.
  **Confirmed**: 31/31 existing tests pass, `.env` present.

**Checkpoint**: No new dependencies to install — confirmed reused environment is ready.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The data shapes every user story needs to exist before it can be built or tested —
the dataclasses themselves, and the two additive extensions to Feature 002's existing state
model. No user story work can begin until this phase is complete.

- [X] T002 [P] Define `SourceArchetype`, `AcquisitionMethod`, `EffectTemplate`, and
  `AbilityGrant` dataclasses in `src/ability_pool.py`, per data-model.md's field tables —
  `EffectTemplate.flavor_bias` MUST be one of `"defensive"`, `"utility"`, `"offensive"`;
  `EffectTemplate.is_signature` MUST be `True` for exactly one template per archetype's pool
  (data-model.md's Validation note).
- [X] T003 [P] Extend `WorldState` in `src/world_state.py` with the new additive field
  `ability_grants: list[AbilityGrant] = field(default_factory=list)` — every other field stays
  byte-for-byte unmodified, same discipline Feature 002 already used for its own additions.
- [X] T004 [P] Extend `ConflictRecord`'s `state_category` type in `src/world_state.py` (or
  wherever the `StateCategory` literal is defined) to add the new value `"abilities"` alongside
  the existing `character_resource`/`resources`/`possessions`/`position`/`status_flags` values.

**Checkpoint**: Foundation ready — the data shapes exist for User Story 1 to test against and
User Stories 2-3 to build on.

---

## Phase 3: User Story 1 - Validate the gating/fill mechanism deterministically, with zero live API cost (Priority: P1) 🎯 MVP

**Goal**: A pure, deterministic function that always resolves a (source archetype, acquisition
method) pair to an effect template from the *correct* archetype's own bounded pool — proven with
unit tests alone, no live model involved.

**Independent Test**: Per spec.md — given any (source archetype, acquisition method) pair from
the fixed probe set, `resolve_ability_grant` returns a template belonging to that archetype's
own pool, runnable entirely offline.

### Implementation for User Story 1

- [X] T005 [US1] Author the fixed `SOURCE_ARCHETYPES` pool in `src/ability_pool.py`: four
  archetypes (`"beast"`, `"elemental_fire"`, `"undead"`, `"construct"`), each with exactly three
  `EffectTemplate`s covering all three `flavor_bias` values once per archetype (one
  `"defensive"`, one `"utility"`, one `"offensive"`), with exactly one `is_signature: True` per
  archetype:
  - `beast`: Thick Hide (defensive, signature), Keen Scent (utility), Savage Claws (offensive)
  - `elemental_fire`: Heat Resistance (defensive), Molten Touch (utility), Ember Burst
    (offensive, signature)
  - `undead`: Deathly Resilience (defensive), Whispers of the Dead (utility), Grave Chill
    (offensive, signature)
  - `construct`: Iron Frame (defensive, signature), Precise Calibration (utility), Overclock
    Strike (offensive)

  Each template needs a `description` stating its effect and an explicit limitation or cost
  (Pattern P12's vocabulary) — e.g. Overclock Strike's cost is a brief self-stagger next turn.
- [X] T006 [US1] Author the fixed `ACQUISITION_METHODS` constant in `src/ability_pool.py`:
  `"decisive_kill"` → `fill_mechanism: "guaranteed"`; `"narrow_survival"` →
  `fill_mechanism: "weighted"`, biased toward `flavor_bias: "defensive"`;
  `"non_lethal_subdual"` → `fill_mechanism: "weighted"`, biased toward `flavor_bias: "utility"`
  — per research.md's acquisition-method decision.
- [X] T007 [US1] Implement `resolve_ability_grant(source_archetype: str, acquisition_method:
  str) -> EffectTemplate` in `src/ability_pool.py`: look up the archetype's pool (raise if the
  archetype isn't in `SOURCE_ARCHETYPES`, per contracts/tools.md's validation-failure
  contract), then apply the acquisition method's fill mechanism — `"guaranteed"` always returns
  the pool's `is_signature` template; `"weighted"` performs a biased random selection favoring
  the declared `flavor_bias` without ever excluding the other templates entirely (so the
  distribution is a genuine bias, not a disguised guarantee).
- [X] T008 [P] [US1] Unit tests in `tests/unit/test_ability_pool.py`, per spec.md's three
  Acceptance Scenarios: (1) `"decisive_kill"` deterministically returns the same signature
  template on repeated calls; (2) a `"weighted"` method's observed distribution across many
  calls (e.g. 200+) favors its declared `flavor_bias` without ever returning a template outside
  the archetype's own pool; (3) no archetype's resolution ever returns a template belonging to
  a different archetype's pool, checked across every archetype. **7/7 passing** (38/38 total
  with the existing suite).

**Checkpoint**: At this point, User Story 1 is fully functional and testable independently —
`pytest tests/unit/test_ability_pool.py` passes with zero live API calls, satisfying SC-001.
**Confirmed.**

---

## Phase 4: User Story 2 - Wire ability-granting into the real AI-DM tool-calling loop (Priority: P2)

**Goal**: A new deterministic tool, `grant_ability`, callable by the real narrating AI within
the existing tool-calling architecture, correctly invoked with the source archetype and
acquisition method a scripted scenario's narrated event actually implies.

**Independent Test**: Per spec.md — run one scripted scenario through the real tool-calling
loop and inspect the resulting tool-call log to confirm `grant_ability` was called with the
archetype/method that scenario was designed to imply.

### Implementation for User Story 2

- [X] T009 [US2] Add the `grant_ability` tool schema to `src/world_state.py`'s
  `EXTRA_TOOL_SCHEMAS` list, per contracts/tools.md's Input contract (`source_archetype`,
  `acquisition_method`, `reason`, all required strings).
- [X] T010 [US2] Add `grant_ability(source_archetype: str, acquisition_method: str, reason:
  str) -> dict` to `WorldStateToolHandlers` in `src/world_state.py` (depends on T007): calls
  `ability_pool.resolve_ability_grant`, appends a new `AbilityGrant` to
  `self.world_state.ability_grants`, and returns the granted `EffectTemplate`'s `template_id`,
  `name`, `description`, and `flavor_bias`, per contracts/tools.md's Output contract. Wire it
  into `WorldStateToolHandlers.dispatch()` alongside the existing four tools. *Amended: added a
  `current_turn` instance attribute the calling harness sets before each turn, since
  `AbilityGrant.turn_number` needs a value but the model shouldn't have to track/supply turn
  numbers itself.* Smoke-tested directly: correct template returned and recorded.
- [X] T011 [US2] Write the six scripted acquisition scenarios (as plain Python data, mirroring
  `tests/probe/campaign_outlines.py`'s style) in `tests/probe/ability_acquisition_scenarios.py`,
  covering all four source archetypes and all three acquisition methods at least once each, per
  research.md's coverage decision:
  1. `beast` + `decisive_kill` — a decisive final blow
  2. `beast` + `narrow_survival` — barely dodging away, bloodied
  3. `elemental_fire` + `non_lethal_subdual` — smothering the flame wisp's core intact
  4. `elemental_fire` + `decisive_kill` — driving a blade through its core
  5. `undead` + `narrow_survival` — scrambling back from its chilling claws, badly shaken
  6. `construct` + `non_lethal_subdual` — disabling its joints without shattering the frame

  **Found live, first attempt**: the original scenarios scripted `action` as narrating the
  kill itself ("I drive my spear through its chest, dropping it instantly"). The DM correctly
  followed Pattern P8 (real-stakes actions get rolled, never just narrated into success) and
  rolled a critical failure, correctly narrating the *player* getting mauled instead —
  `grant_ability` correctly wasn't called, since the kill genuinely didn't happen. The
  mechanism worked exactly right; the scenario's premise was wrong. Fixed by putting the
  kill/acquisition already-settled, past-tense, in `context`, with `action` a genuine no-stakes
  follow-up — this is what actually isolates "does the DM map an established event onto
  grant_ability's categories correctly" from "did a fresh roll happen to succeed."
- [X] T012 [US2] Implement `tests/probe/run_ability_acquisition_probe.py`'s scenario-running
  core: drive each scripted scenario through `dm_agent.run_turn` (reusing the existing
  tool-calling loop, `COMBINED_TOOL_SCHEMAS` extended with the new tool per T009), log every
  tool call (mirroring `run_long_horizon_test.py`'s `log()` helper), and report whether
  `grant_ability` was called with the archetype/method each scenario was designed to imply.
  Support `--scenarios N` to run a subset, per quickstart.md's Step 2. **Executed live** after
  T011's fix: 6/6 scenarios called `grant_ability` with the exact correct archetype and method —
  SC-002 fully satisfied.

**Checkpoint**: At this point, User Stories 1 AND 2 both work independently — running the probe
harness shows correct tool-call wiring for at least one scenario, satisfying SC-002's per-scenario
requirement. **Confirmed, and exceeded (6/6, not just one).**

---

## Phase 5: User Story 3 - Check narrated ability grants against the mechanically-determined result (Priority: P3)

**Goal**: The DM's narration of a granted ability is checked against what the tool call actually
returned, and the full scripted scenario set produces a measured, category-broken-out
consistency rate — the deliverable insight, not a pass/fail gate.

**Independent Test**: Per spec.md — given a completed scenario's narration and its logged
`AbilityGrant`, the extended auditor check reports whether the narration accurately reflects the
granted effect, without needing to re-run the scenario.

### Implementation for User Story 3

- [X] T013 [US3] Add the optional `ability_grant: AbilityGrant | None = None` parameter to
  `auditor.check_turn` in `src/auditor.py` (depends on T002, T003), per contracts/tools.md: when
  not `None`, extend the existing narration-vs-state prompt to also check the narration against
  the granted `EffectTemplate`'s `name`, `description`, and any stated limitation, reporting a
  mismatch with `conflict_type: "fact"` and `state_category: "abilities"` (depends on T004) —
  reusing `check_turn`'s existing comparison logic, not a parallel mechanism.
- [X] T014 [US3] Wire the extended auditor check into
  `tests/probe/run_ability_acquisition_probe.py` (depends on T012, T013): after each scenario
  that called `grant_ability`, pass the resulting `AbilityGrant` to `check_turn` and record the
  result.
- [X] T015 [US3] Implement the SC-002/SC-003 report in
  `tests/probe/run_ability_acquisition_probe.py`: per-scenario tool-call correctness (US2) and
  the measured narration/grant consistency rate, broken out by source archetype and by
  acquisition method — not collapsed into one aggregate number, per spec.md's SC-003 and
  quickstart.md's Step 3.

**Checkpoint**: All user stories now independently functional — the full scripted set produces
the complete report described in quickstart.md's Step 3. **Confirmed, executed live**: 6/6
scenarios correct (SC-002), and the auditor extension found one genuine, real conflict — the
`elemental_fire_non_lethal_subdual` scenario's narration invented an unstated extra weakness
("extreme cold shocks you more harshly than normal") beyond what the granted Heat Resistance
ability actually says ("no protection against cold" is neutral, not an active penalty). A
measured 5/6 (83%) narration/grant consistency rate — reported as the finding, not treated as a
bug to silently fix, per this project's established practice.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Confirm the probe actually holds up live, within its own stated budget, and record
the result honestly per this project's established practice.

- [X] T016 [P] Confirm via `git diff` that `requirements.txt` has zero changes across this
  feature's implementation, per plan.md's Technical Context claim (same check Feature 002's
  T022 already performed for itself). **Confirmed**: `git diff --stat requirements.txt` is
  empty.
- [X] T017 Run quickstart.md's Step 1-3 live, in order (unit tests, one scenario, then the full
  six-scenario set), and record the actual results — the per-scenario tool-call correctness,
  the measured consistency rate by archetype and method, and the total live API call count
  against SC-004's under-50 target — in a new
  `specs/003-ability-acquisition-probe/implementation-results.md`, following Feature 001/002's
  precedent of reporting the measured rate as the deliverable insight, not a pass/fail gate, and
  documenting any bug found along the way rather than silently fixing it. **Done** — see
  [implementation-results.md](implementation-results.md): SC-001 through SC-004 all
  satisfied, one real narration/grant conflict found and reported (5/6, 83% consistency), one
  real scripted-scenario design bug found and fixed along the way (documented, not hidden).

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories.
- **User Stories (Phase 3-5)**: All depend on Foundational. US1 has no dependency on US2/US3.
  US2 depends on US1's `resolve_ability_grant` existing (T007) — it needs a mechanism to wire
  into the tool, but is independently testable once that exists. US3 depends on US2's tool
  wiring (T010) producing real `AbilityGrant` records to check against, but is a pure
  audit/reporting layer — it adds no new acquisition mechanics of its own.
- **Polish (Phase 6)**: Depends on all three user stories being complete.

### Parallel Opportunities

- T002, T003, T004 can all run in parallel (different concerns within `world_state.py`/
  `ability_pool.py`, no dependency on each other).
- T008 (unit tests) can run in parallel with nothing else in US1, since it depends on T005-T007
  all being complete first — it's the last task in that story, not a parallel one.
- T016 can run in parallel with T017 (an independent check, not a dependency of the live run).

---

## Parallel Example: Foundational Phase

```bash
# Launch T002, T003, T004 together — different concerns, no shared dependency:
Task: "Define SourceArchetype, AcquisitionMethod, EffectTemplate, AbilityGrant dataclasses in src/ability_pool.py"
Task: "Extend WorldState with ability_grants field in src/world_state.py"
Task: "Extend ConflictRecord's state_category with 'abilities' in src/world_state.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: `pytest tests/unit/test_ability_pool.py` passes, zero live API calls
   spent — this alone already answers whether the core mechanism (Pattern P5's first flavor) is
   sound before a single dollar is spent wiring it into the live DM.

### Incremental Delivery

1. Complete Setup + Foundational → data shapes ready
2. Add User Story 1 → validate offline → the mechanism itself is proven
3. Add User Story 2 → validate live, one scenario at a time → tool wiring is proven
4. Add User Story 3 → validate live, full scenario set → narration consistency is measured
5. Polish → the live budget claim (SC-004) and the full report are confirmed and recorded

## Notes

- [P] tasks = different files or independent concerns, no dependency on an incomplete task
- [Story] label maps task to specific user story for traceability
- This feature's entire live-API footprint is scoped to Phase 4 (User Story 2) and Phase 5
  (User Story 3)'s scenario runs, plus Phase 6's confirmation run — Phases 1-3 spend nothing
- Commit after each phase, not each task — matches Feature 001/002's own granularity
