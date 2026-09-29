# Feature Specification: Long-Horizon Consistency Stress Test

**Feature Branch**: `002-long-horizon-consistency-test`

**Created**: 2026-09-29

**Status**: Draft

**Input**: User description: "Build a long-session state/memory stress test for the AI DM,
deliberately pushing session length and state breadth beyond what Feature 001 tested, using a
synthetically-constructed scenario (not 80+ real sequential turns) to find out where and how
our real tool-calling + externalized-state architecture breaks down before we build real game
mechanics on top of it. Directly informed by NCP-Bench and RPGBench's own construction and
evaluation methodology (see reports/Long horizon LLM narrative benchmarks.md)."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Construct a synthetic long-session scenario without playing real turns (Priority: P1)

As the project team, we generate a synthetic "story so far" — a trajectory, a set of typed
commitments, and an initial fact/state set — via a structured three-stage extraction pipeline
adapted from NCP-Bench, then convert that into a pre-seeded state file compatible with Feature
001's existing state machinery, so we get a realistic long-session starting condition without
paying for 80+ sequential real API turns just to reach one.

**Why this priority**: Everything else depends on this. Per the research (NCP-Bench,
RPGBench), synthetic construction is the field's actual standard, not a shortcut — but its
rigor depends entirely on strict isolation discipline during construction. A poorly-isolated
seed (one that leaks future knowledge) would make every downstream measurement meaningless.

**Independent Test**: Given a short campaign outline, the pipeline produces a trajectory
(ordered plot nodes), a commitment set (typed, each with explicit satisfaction/violation
conditions), and an initial fact set — and an automated check confirms no initial fact
references something that, per the trajectory, hasn't happened yet at the seed point (the
"T=0 Absolute Isolation Principle"). The resulting state loads correctly into Feature 001's
`CharacterState`/`SessionLog` structures (extended per FR-002).

**Acceptance Scenarios**:

1. **Given** a short, original campaign outline (not copyrighted source material), **When**
   the three-stage pipeline runs, **Then** it produces a trajectory, a commitment set, and an
   initial fact set as three distinct, explicitly-ordered extraction passes, each conditioned
   on the output of the previous one.
2. **Given** a generated initial fact set, **When** it is checked against the trajectory,
   **Then** no fact asserts knowledge of, or a state resulting from, any trajectory node whose
   `trigger_event` is scheduled to occur after the seed point.

---

### User Story 2 - Run real turns on top of the seeded scenario and detect conflicts (Priority: P2)

As the project team, we run a real, live sequence of turns — using Feature 001's actual
`roll_check`/`get_state`/`update_state` tool-calling architecture, unmodified — starting from
the pre-seeded state, driven by a scripted player persona (adversarial or natural, per
NCP-Bench's dual-condition design), and detect when narration contradicts a seeded fact, an
active commitment, or the player's own input.

**Why this priority**: This is the actual measurement this feature exists to produce — depends
on User Story 1's seed existing first.

**Independent Test**: Run one full scripted session, up to a defined turn cap or until a
conflict/termination event, and produce a turn-by-turn conflict log using only Feature 001's
existing tools plus the new auditor check (User Story 2 does not require User Story 3's
reporting layer to be independently verifiable — the raw log is itself inspectable).

**Acceptance Scenarios**:

1. **Given** a pre-seeded scenario from User Story 1, **When** a scripted adversarial-persona
   player drives a sequence of actions, **Then** each action is resolved through Feature 001's
   real tool-calling loop (not a new mechanism), and every turn is checked against the seeded
   fact ledger and active commitments for a conflict.
2. **Given** the same seeded scenario, **When** a scripted natural-persona (cooperative) player
   drives an equivalent-length sequence, **Then** the same conflict-checking applies, producing
   a comparable log for the two conditions.

---

### User Story 3 - Report a category-resolved degradation profile, not a single pass/fail (Priority: P3)

As the project team, we want a summary report that separates "survival" (no detected conflict
yet) from "success" (state and narration both correct *and* the story's tracked commitments
actually progressed), broken down by conflict type and by which seeded state category failed,
at fixed turn checkpoints rather than only at session end.

**Why this priority**: Lower priority than actually producing the data (User Stories 1-2), but
this is the deliverable insight — matching how NCP-Bench and RPGBench report results, and
matching Feature 001's own SC-002 precedent of reporting a measured rate rather than a single
gate.

**Independent Test**: Given a completed run's log (from User Story 2), the reporting step
outputs per-category conflict counts, the turn number and normalized position of first
conflict, and both a survival rate and a stricter success rate at fixed checkpoints.

**Acceptance Scenarios**:

1. **Given** one or more completed run logs, **When** the report is generated, **Then** it
   states, per run: turn-of-first-conflict (or none), conflict type breakdown (fact /
   commitment / player-input), and which seeded state category each conflict falls under.
2. **Given** multiple runs across both persona conditions, **When** the report aggregates
   them, **Then** it states separate survival and success rates per condition, comparable to
   the published NCP-Bench baseline figures cited in the research this feature is based on.

---

### Edge Cases

- What happens if the extraction pipeline itself produces an initial fact that leaks future
  trajectory knowledge (an isolation-principle violation)? The automated isolation check (User
  Story 1) MUST catch this before the seed is used for a real run, not after.
- What happens if the scripted player persona's action implies a state category that wasn't
  pre-seeded (e.g., referencing an item or fact never established)? The system MUST log this
  as an "unseeded category encountered" event distinct from a conflict, rather than crashing or
  silently inventing a resolution.
- What happens if the story reaches a natural terminal state (e.g., character death, a
  completed ending) before any checkpoint? This MUST be recorded as a distinct termination
  outcome, not conflated with a "conflict" — dying is not the same as the AI DM contradicting
  itself (mirrors NCP-Bench's Conflict/Survival/Success framing, where survival and success are
  about consistency, not about the story ending well or badly for the character).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST generate a synthetic scenario via a three-stage extraction pipeline:
  (1) trajectory — an ordered list of plot nodes, each with a `trigger_event` and an
  observable `key_delta`, respecting a point-of-view constraint so nothing the player-character
  couldn't plausibly know is included; (2) commitments — conditioned on the trajectory, typed
  as invariant/ordering/achievement, each with an explicit, machine-checkable
  satisfaction/violation condition, excluding static background color; (3) initial facts —
  conditioned on both prior stages, enforcing the T=0 Absolute Isolation Principle (positively
  asserting ignorance of anything not yet true, not merely omitting it).
- **FR-002**: System MUST convert generated initial facts into a pre-seeded state file
  compatible with Feature 001's `CharacterState`/`SessionLog` structures, extended with
  additional generic state categories beyond the single Vitality resource: at minimum one
  additional numeric resource that gets revised more than once per session, a
  possession/inventory-like flag set, a position/location fact, and a status/existence flag
  set (alive/dead/present/absent, introduced/not-yet-introduced) — these categories are
  required because research shows facts that change over time are the most fragile category,
  not static lore.
- **FR-003**: System MUST run real turns on top of the seeded state using Feature 001's
  existing tool-calling architecture (`roll_check`, `get_state`, `update_state`) without
  modification to those tools' contracts — this feature extends Feature 001, it does not
  replace or duplicate its mechanism.
- **FR-004**: System MUST drive the live turn sequence via a scripted player persona with at
  least two modes — adversarial (exploit-seeking, testing whether pressure accelerates
  failure) and natural (cooperative) — since research found persona condition changes
  commitment-conflict rate substantially but barely moves fact-conflict rate, itself a useful
  comparison point for our own architecture.
- **FR-005**: System MUST check each turn's narration against the seeded fact ledger and
  active commitments for conflicts, categorized as fact conflicts, commitment conflicts
  (ordering/invariant/achievement), or player-input conflicts, using an independent auditor
  check that extends Feature 001's `judge_consistency` pattern rather than introducing a new
  mechanism.
- **FR-006**: System MUST record, for each detected conflict, which seeded state category it
  falls under (the categories from FR-002), so category-level failure rates are computable
  after the fact, not just an aggregate count.
- **FR-007**: System MUST run each session up to a defined turn cap or until a
  conflict/termination event, whichever comes first, and MUST NOT treat reaching the cap as
  the sole success condition — per research, most current models fail well before typical
  session lengths, so the turn cap exists to bound cost, not to define "passing."
- **FR-008**: System MUST report, per run and in aggregate: turn number and normalized
  position of first conflict (if any); survival status (reached the cap or a natural
  termination without a detected conflict) as distinct from success status (survival AND all
  seeded achievement-type commitments satisfied); and a per-category, per-type conflict
  breakdown — reported at fixed intermediate checkpoints, not only at session end.

### Key Entities

- **Scenario Trajectory**: An ordered list of plot nodes, each with a trigger event, an
  observable state delta, and a point-of-view constraint.
- **Commitment**: A typed (invariant/ordering/achievement) rule with an explicit
  satisfaction condition and violation condition, anchored to the trajectory.
- **Seeded State**: An extension of Feature 001's `CharacterState`, adding a second
  numeric resource, possession flags, a position fact, and status/existence flags.
- **Conflict Record**: A turn number, conflict type, implicated state category, and a
  description, produced by the auditor check.
- **Session Outcome**: Survival (boolean), success (boolean), turn-of-first-conflict, and
  per-checkpoint summaries for one run.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The extraction pipeline produces a complete trajectory, commitment set, and
  initial-fact set for at least 3 distinct, original campaign outlines, and an automated
  isolation check confirms 0 future-knowledge leaks across all 3.
- **SC-002**: Across at least 5 full scripted runs (mixing adversarial and natural persona
  conditions), the system produces a complete report (turn-of-first-conflict, type breakdown,
  category breakdown) for 100% of runs, regardless of whether a given run "succeeded" —
  matching Feature 001's precedent that the measured rate is the deliverable insight, not
  solely a pass/fail gate.
- **SC-003**: The measured fact-conflict rate and turn-of-first-conflict for this
  architecture are explicitly reported alongside the published NCP-Bench baseline figures
  (e.g., 40-68% fact-conflict rate among failing episodes, 42% survival at turn 20 for the
  best tested model) as a point of comparison, not a pass/fail gate against those numbers.
- **SC-004**: At least one run includes a deliberate test action targeting each of the four
  seeded state categories (the additional numeric resource, possession, position,
  status/existence), and the resulting conflict-or-no-conflict outcome is correctly
  category-attributed in the report for all four.

## Assumptions

- This feature builds directly on Feature 001's code (`state.py`, `resolution.py`,
  `tools.py`, `dm_agent.py`), extending rather than replacing it — the research confirms our
  tool-calling architecture is worth stress-testing further, not that it needs to be redesigned.
- Campaign outline source material is original, invented text — not adapted from copyrighted
  works the way NCP-Bench uses movie synopses — since we're borrowing NCP-Bench's *method*,
  not its specific source material.
- A turn cap of 50 is a reasonable placeholder starting point (between NCP-Bench's finding
  that failure often starts well before turn 20 and its 100-turn ceiling), to be adjusted
  based on what this feature itself finds — explicitly provisional, not final.
- The scripted "adversarial vs. natural" player persona is itself a prompted LLM call, not a
  real human — this is an architecture stress test, not a human playtest, mirroring NCP-Bench's
  own construction.
- The per-turn auditor check extending `judge_consistency` shares a model family with the
  narrator in this feature, same as Feature 001's implementation-results.md already flagged —
  not the fully independent judge Pattern P13 eventually calls for. This is an accepted,
  documented limitation for this stage, not something this feature resolves.
- Real mechanics/character-build design (the actual ruleset, Pattern P5's emergent-acquisition
  system, etc.) remain explicitly out of scope — this feature tests architecture under
  synthetic pressure, not game content, continuing the project's established methodology of
  proving the foundation before building on it.
