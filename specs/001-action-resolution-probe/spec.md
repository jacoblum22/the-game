# Feature Specification: Action Resolution Probe

**Feature Branch**: `001-action-resolution-probe`

**Created**: 2026-09-28

**Status**: Draft

**Input**: User description: "Build the smallest possible vertical slice to test whether the
AI Dungeon Master can reliably resolve a player's freeform action attempt using a deterministic
degree-of-success mechanic (Adopted Design Pattern P8), and correctly keep a small piece of
persisted state in sync with its own narration (Principle I; Patterns P3, P13). This is
explicitly a probe to learn what the AI is good/bad at, not a commitment to final game
mechanics — no character creation, combat encounters, or progression are in scope."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Resolve a single ambiguous player action (Priority: P1)

As a player, I describe an action in natural language to the AI Dungeon Master (e.g. "I try to
pick the lock" or "I attempt to persuade the guard"). The AI DM determines what's being
attempted, resolves it deterministically via a degree-of-success roll against a target number,
and narrates an outcome consistent with that computed result.

**Why this priority**: This is the single riskiest, least-proven capability the whole project
depends on (constitution Patterns P8 and P13 are explicitly marked as research-informed
recommendations, not yet exercised against a real feature). Nothing else in the project can be
meaningfully validated until this works at all.

**Independent Test**: Can be fully tested by giving the AI DM one freeform action description
and checking (a) it produces a computed degree-of-success result, and (b) its narration matches
that result — with no character creation, combat, or any other system involved.

**Acceptance Scenarios**:

1. **Given** a player describes a plausible action attempt with real stakes, **When** the AI DM
   resolves it, **Then** the system produces exactly one of four outcomes (critical success /
   success / failure / critical failure) computed from a roll against a stated target number,
   not an outcome chosen by free-form narrative judgment alone.
2. **Given** a computed outcome, **When** the AI DM narrates the result, **Then** the narration
   does not contradict the computed degree of success (e.g. it must not narrate unambiguous
   success after a computed failure).

---

### User Story 2 - Track state consistently across a short sequence of actions (Priority: P2)

As a player performing several actions in sequence within one session, I expect a small set of
numeric state (e.g. one tracked resource) to update correctly after each action, and to remain
consistent with what the narration says happened.

**Why this priority**: This is the second core open risk this project's research surfaced (state
drifting from narration — research pass three found only 46-58% consistency even with enforced
function-calling). Testing it depends on User Story 1 already working, so it is P2.

**Independent Test**: Can be tested by running at least 10 actions in one session and checking,
after each one, whether the persisted state matches what was narrated.

**Acceptance Scenarios**:

1. **Given** a character has a tracked resource at a known value, **When** an action's outcome
   implies a change to that resource, **Then** the system updates the persisted value by the
   correct amount and the narration reflects the same change.
2. **Given** a sequence of actions, **When** the session is reviewed afterward, **Then** every
   state change can be traced to the specific action and outcome that caused it.

---

### User Story 3 - Detect when narration and state disagree (Priority: P3)

As the project team evaluating this probe, we want any divergence between the system's
narration and its persisted state to be detectable, rather than passing silently.

**Why this priority**: Lower priority than getting resolution/state right in the first place,
but this is what actually produces the learning signal the probe exists for — without
detection, the project cannot measure the exact risk (Patterns P3/P13) it commissioned this
feature to test.

**Independent Test**: Can be tested by reviewing logged output after a session and confirming
any narration/state mismatch is identifiable from that log alone.

**Acceptance Scenarios**:

1. **Given** a completed session, **When** state and narration are compared against the logged
   output, **Then** any divergence between them is identifiable from that log alone, not from
   re-reading prose and guessing.

---

### Edge Cases

- What happens when a player's description has no clear stakes (pure roleplay/dialogue, e.g.
  "I say hello to the innkeeper")? The system MUST recognize this and narrate directly, without
  inventing a roll or target number.
- What happens when a player describes an action that is clearly impossible given established
  state (e.g. "I fly away" with no established ability to fly)? The system MUST decline or
  redirect narratively rather than resolving it as a normal, grantable action (Principle III:
  the AI MUST NOT grant itself blanket authority to just allow anything).
- What happens when a player's action references something not yet established in the world
  (e.g. an NPC that hasn't been introduced)? The system MAY improvise minimal, consistent
  detail, but that improvised detail MUST then be logged as new state so later actions can be
  checked against it.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept a free-form natural-language description of a player's
  attempted action.
- **FR-002**: System MUST determine whether the described action requires a resolved outcome
  (a check) or is pure narration/roleplay with no stakes, and MUST NOT invent a roll or target
  number for the latter.
- **FR-003**: For an action requiring resolution, System MUST compute a target number and a
  degree-of-success outcome (critical success, success, failure, or critical failure) from a
  deterministic roll-versus-target calculation, not from free-form narrative judgment alone
  (Pattern P8).
- **FR-004**: System MUST narrate an outcome for a resolved action that is consistent with its
  own computed degree of success.
- **FR-005**: System MUST persist at least one piece of numeric character state (e.g. a single
  tracked resource) across multiple sequential actions within one session.
- **FR-006**: System MUST update persisted numeric state whenever an action's outcome implies a
  change, and MUST log the amount of change alongside the action that caused it.
- **FR-007**: System MUST make its computed outcome (roll, target number, resulting degree of
  success) available in a form a human reviewer can inspect separately from the narrated prose.
- **FR-008**: System MUST log, for each action in a session, enough information for a reviewer
  to independently check whether the narration matches the computed state change — this is the
  probe's actual measurement instrument, not an incidental log.

### Key Entities *(include if feature involves data)*

- **Player Action Attempt**: A natural-language description of what the player is trying to
  do, whether it requires resolution, and (if so) its target number, roll result, and resulting
  degree of success.
- **Resolution Outcome**: One of critical success / success / failure / critical failure, plus
  the narrated description of what happened as a result.
- **Character State**: A minimal set of tracked numeric values associated with the player's
  character (at least one resource), updated over the course of a session.
- **Session Log**: An ordered record of each action attempt, its resolution, and the resulting
  state changes, sufficient for a reviewer to check consistency after the fact.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Across a test session of at least 10 sequential action descriptions with clear
  stakes, the system produces a computed degree-of-success outcome — distinct from free-form
  narrative judgment — for 100% of them.
- **SC-002**: Across that same session, the number of instances where narration contradicts its
  own computed degree of success is measured and reported exactly (a rate of 0 is the target;
  this project's own research found comparable systems achieve only 46-58% consistency, so the
  measured rate — whatever it is — is the deliverable insight of this probe, not solely a
  pass/fail gate).
- **SC-003**: For every action in the session, a reviewer can determine solely from logged
  output whether the persisted state change matches the computed outcome, without needing to
  re-read narration and guess.
- **SC-004**: The system correctly declines to invent a roll for 100% of a deliberately-included
  set of stakes-free, pure-roleplay descriptions within the test session.

## Assumptions

- This is an exploratory probe, not a commitment to final game mechanics. The specific
  resolution numbers, resource name, and target-number formula used here are placeholders;
  exact numeric tuning is deferred to `/speckit-plan` per constitution Patterns P8/P9 and may
  change based on what this probe reveals.
- A single generic tracked resource stands in for whatever the eventual ruleset's real
  resources are; its specific name/meaning is not meant to be final.
- This probe covers one continuous session only; cross-session persistence, save/load, and
  multi-session continuity are out of scope for this feature.
- No character creation, combat encounters, NPCs with independent agency, or
  progression/leveling are in scope — this is the smallest slice that still exercises the AI
  DM's core resolution loop.
- The interface/modality used to run this probe (e.g. a raw chat session vs. a minimal harness)
  is an implementation detail deferred to `/speckit-plan`, not decided here.
- Falling short of SC-002's aspirational target still produces valid, useful learning for this
  project — that is the explicit purpose of framing this feature as a probe rather than a
  production feature.
