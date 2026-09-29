# Feature Specification: Ability Acquisition Probe

**Feature Branch**: `003-ability-acquisition-probe`

**Created**: 2026-09-29

**Status**: Draft

**Input**: User description: "A small, scripted probe of just the source-gates-pool +
method-picks-fill ability-acquisition mechanism resolved by the fifth research pass (Pattern
P5's specific-ability-from-source-and-method flavor) — a handful of source archetypes mapping
to a handful of effect-templates, tested live to see whether the mechanism actually holds up
before any content gets authored at scale or the class-emergence/classifier layer (P5's other
flavor) gets built on top of it."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Validate the gating/fill mechanism deterministically, with zero live API cost (Priority: P1)

As the project team, we define a small, fixed set of source archetypes (each gating its own
small, bounded pool of effect-templates) and a small, fixed set of acquisition methods (each
mapping to a distinct fill mechanism — guaranteed pick, weighted/biased roll), then verify with
pure unit tests that the mechanism always resolves correctly: a given (source archetype,
acquisition method) pair always yields an effect template from that archetype's own pool, never
from another archetype's pool and never outside the fixed set.

**Why this priority**: Everything else depends on this being correct first. Per Pattern P5
(resolved by the fifth research pass), the entire point of the source-gates-pool /
method-picks-fill design is that it's deterministic and boundable — that claim should be
verified with cheap, fast, zero-cost unit tests before a single live API call is spent
wiring it into the real AI DM.

**Independent Test**: Given any (source archetype, acquisition method) pair from the fixed
probe set, a pure function returns an effect template, and an assertion confirms that template
belongs to the given source archetype's own pool — runnable entirely offline, no live model
calls.

**Acceptance Scenarios**:

1. **Given** a source archetype with a 3-template pool, **When** the mechanism resolves an
   acquisition with the "guaranteed pick" method, **Then** it deterministically returns the
   same, specific template every time for that exact input.
2. **Given** the same source archetype, **When** the mechanism resolves an acquisition with a
   "weighted/biased roll" method, **Then** it returns a template from that archetype's pool on
   every call, with the observed distribution across many calls matching the declared weights
   (not literally 50/50 or uniform unless declared as such).
3. **Given** two different source archetypes, **When** the mechanism resolves an acquisition
   for each, **Then** neither ever returns a template belonging to the other's pool.

---

### User Story 2 - Wire ability-granting into the real AI-DM tool-calling loop (Priority: P2)

As the project team, we add ability-granting as a new deterministic tool call within the
existing AI-DM tool-calling architecture (Feature 001/002's `roll_check` / `get_state` /
`update_state` / `update_resource` / `set_fact` pattern) — not something the narrating AI
decides freely in prose — and drive a handful of hand-scripted acquisition scenarios (a
decisive kill, a narrow survival, a non-lethal subdual, across each of the probe's source
archetypes) through the real, live model to see whether the DM correctly identifies the source
archetype and acquisition method implied by what actually happened, and calls the new tool with
the correct inputs.

**Why this priority**: This is the actual live-model risk this probe exists to test — depends
on User Story 1's mechanism existing and already being verified correct.

**Independent Test**: Run one scripted scenario (a specific narrated kill/acquisition event)
through the real tool-calling loop, and inspect the resulting tool-call log to confirm the
ability-grant tool was called with the source archetype and acquisition method that scenario
was actually designed to imply — independently checkable from the raw log, without needing User
Story 3's consistency-check layer.

**Acceptance Scenarios**:

1. **Given** a scripted player action narrating a decisive killing blow against a source
   belonging to a known archetype, **When** the DM resolves the turn, **Then** it calls the
   ability-grant tool with that archetype and the "guaranteed pick" acquisition method.
2. **Given** a scripted player action narrating a narrow, costly survival against the same
   archetype, **When** the DM resolves the turn, **Then** it calls the ability-grant tool with
   the same archetype but the "weighted/biased roll" acquisition method instead.
3. **Given** an action that does not clearly imply any of the probe's fixed source archetypes,
   **When** the DM resolves the turn, **Then** it does not call the ability-grant tool at all
   (per the Edge Case below), rather than inventing a new archetype or guessing.

---

### User Story 3 - Check narrated ability grants against the mechanically-determined result (Priority: P3)

As the project team, we extend the existing auditor pattern (`auditor.check_turn`, built for
Feature 002) to also check, for any turn that granted an ability, whether the DM's narration of
that grant is consistent with what the tool call actually returned — and run this check across
all of User Story 2's scripted scenarios to produce a measured consistency rate, the same way
Feature 001 and Feature 002 report a rate rather than a single pass/fail gate.

**Why this priority**: Lower priority than proving the mechanism and the tool-calling wiring
work at all, but this is the layer that actually answers "can we trust the DM not to
contradict what it just mechanically granted" — the question this whole probe exists to answer
before any real content or the class-emergence layer gets built on top of this mechanism.

**Independent Test**: Given a completed scripted scenario's narration and its logged
ability-grant tool call, the extended auditor check reports whether the narration accurately
reflects the granted effect (name, source, and any stated limitation) without needing to re-run
the scenario.

**Acceptance Scenarios**:

1. **Given** a turn where the ability-grant tool returned a specific effect template, **When**
   the auditor checks that turn's narration, **Then** it flags a conflict if the narration
   describes a different effect, a different source archetype, or contradicts the effect's
   stated limitation.
2. **Given** all of User Story 2's scripted scenarios have run, **When** the report is
   generated, **Then** it states the measured consistency rate across scenarios, broken out by
   source archetype and acquisition method — not collapsed into a single aggregate number.

---

### Edge Cases

- What happens when a narrated action doesn't clearly map to any of the probe's small, fixed
  source archetypes? The DM MUST NOT invent a new archetype or force a mapping to the nearest
  existing one — it MUST simply not grant an ability that turn, consistent with Pattern P5's
  requirement that the source pool stay closed and bounded rather than open-ended.
- What happens if a character has already been granted every template in a given source
  archetype's pool? A repeat acquisition against that same archetype MUST NOT crash or silently
  duplicate a template — the probe MUST define (and test) an explicit "pool exhausted" outcome.
- What happens when a single narrated action plausibly implies two different acquisition
  methods at once (e.g., a costly near-loss that still ends in a clean kill)? The probe MUST
  document which one deterministic tie-break rule applies, rather than leaving it to
  case-by-case model judgment.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST define a small, fixed set of source archetypes for this probe (target:
  3-4), each gating its own small, bounded pool of effect-templates (target: ~3 per archetype) —
  never an open-ended or per-entity-authored table, per Pattern P5.
- **FR-002**: System MUST define a small, fixed set of acquisition methods for this probe
  (target: 3), each mapping to a distinct, deterministic fill mechanism for selecting a template
  from a source archetype's gated pool (at minimum: one guaranteed-pick method and one
  weighted/biased-roll method).
- **FR-003**: System MUST expose ability-granting as a new deterministic tool call within the
  existing AI-DM tool-calling architecture, reusing Feature 001/002's `ToolHandlers` /
  `WorldStateToolHandlers` pattern rather than introducing a new mechanism, and MUST NOT let the
  narrating AI decide a granted effect's identity in prose.
- **FR-004**: System MUST record, for every granted ability, which source archetype and
  acquisition method produced it, so the mechanism's actual live behavior is auditable from the
  session log alone (matching Feature 001's `ActionAttempt` / Feature 002's `ConflictRecord`
  logging discipline).
- **FR-005**: System MUST extend the existing auditor pattern to check a turn's narration
  against its own ability-grant tool call result, classifying a mismatch as a conflict the same
  way Feature 002's auditor already classifies fact/commitment/player-input conflicts.
- **FR-006**: The complete set of source archetypes, acquisition methods, and effect-templates
  used for this probe MUST be small enough to be fully enumerated and reasoned about by a human
  reviewer in one sitting — this feature is explicitly a probe of the mechanism, not a
  content-authoring pass for the eventual real game.
- **FR-007**: System MUST NOT implement the class/archetype-emergence flavor of Pattern P5 (the
  classifier-based mechanism) as part of this feature — that flavor explicitly depends on this
  probe's combinatorial ability-slot mechanism existing and being validated first.

### Key Entities

- **Source Archetype**: A small, fixed category (e.g. Beast, Elemental) that an encountered or
  defeated source belongs to; gates a small, bounded pool of Effect Templates.
- **Acquisition Method**: A small, fixed category describing how a source was defeated or
  acquired (e.g. a decisive kill, a narrow survival); determines which fill mechanism selects a
  template from the gated pool.
- **Effect Template**: One concrete, nameable grantable effect, belonging to exactly one Source
  Archetype's pool.
- **Ability Grant**: A record of one granted Effect Template, including which Source Archetype
  and Acquisition Method produced it and at which turn — the unit the auditor check in User
  Story 3 operates on.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Across every (source archetype, acquisition method) pair in the probe's fixed
  set, the deterministic mechanism returns a template from the correct archetype's pool 100% of
  the time, verified by unit tests with zero live API calls.
- **SC-002**: Across at least one scripted live scenario per source archetype and per
  acquisition method (covering every pair at least once), the real tool-calling pipeline calls
  the ability-grant tool with the source archetype and acquisition method that scenario was
  designed to imply.
- **SC-003**: Across those same scripted scenarios, the measured narration/grant consistency
  rate (per User Story 3's extended auditor check) is reported broken out by source archetype
  and acquisition method — reported as a measured rate, not evaluated against a pass/fail
  threshold, matching this project's existing precedent (Feature 001/002) of treating the
  measured rate itself as the deliverable insight.
- **SC-004**: The full live validation pass (User Story 2 plus User Story 3 combined) completes
  within a small number of real API calls (target: under 50), keeping this probe cheap enough
  to run without a separate budget check, consistent with its purpose as a narrow mechanism
  probe, not a content or long-horizon stress test.

## Assumptions

- This probe intentionally uses a tiny, throwaway set of source archetypes, acquisition
  methods, and effect-templates chosen only to exercise the mechanism — none of this content is
  intended to survive into the eventual real game's actual class/ability content.
- This probe builds directly on Feature 001's tool-calling architecture and Feature 002's
  `WorldState`/auditor extensions, reusing rather than replacing them, consistent with how
  Feature 002 reused Feature 001's `roll_check`/`get_state`/`update_state` without modification.
- Pattern P5's class/archetype-emergence flavor (the calibrated classifier, the derived
  narrative label, the three-valued grant/offer/abstain policy) is explicitly out of scope here
  — it is a separate future feature that depends on this probe's mechanism being validated
  first, per this project's stated practice of validating narrow slices before building on top
  of them.
- Single-player scope (already established in the constitution) applies; no party/spotlight
  concerns are in scope for this probe.
