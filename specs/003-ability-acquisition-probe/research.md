# Phase 0 Research: Ability Acquisition Probe

Technical Context left no `NEEDS CLARIFICATION` markers — this feature reuses Feature 001/002's
proven architecture almost entirely, so this phase records the handful of real design decisions
made, not open unknowns.

## Decision: the pool's contents are hand-authored Python constants, not LLM-generated

**Rationale**: User Story 1 needs `resolve_ability_grant`'s gating/fill logic testable with
zero live API calls, and FR-006 requires the whole set to be small enough for a human reviewer
to enumerate in one sitting. Both requirements are satisfied trivially if the pool is a plain
Python constant; neither is guaranteed if an LLM generates it (variable size, unverifiable
without a live call, and no guarantee of staying within a human-legible bound).

**Alternatives considered**: generating the archetype/template pool via an LLM extraction call,
mirroring Feature 002's `scenario_pipeline.py` (rejected — that pipeline exists specifically to
generate rich, varied *scenario* content; this probe explicitly wants the opposite, a fixed,
tiny, controlled fixture to isolate whether the *mechanism* works, independent of content
quality or quantity).

## Decision: `ability_grants` is an additive field on `WorldState`, not a parallel store

**Rationale**: Matches the precedent Feature 002 already set for `resources`/`possessions`/
`status_flags` — a single source of truth the auditor can read alongside everything else it
already checks, rather than a second state file the auditor would need to separately load and
keep in sync.

**Alternatives considered**: a standalone `AbilityLog` file per session (rejected — more moving
parts, no benefit at this scale, and would require the auditor to reconcile two independently-
updated stores instead of one).

## Decision: extend `check_turn` with an optional `ability_grant` parameter, not a new audit function

**Rationale**: `check_turn` already does exactly the comparison this needs — narration versus a
structured fact about what changed this turn — and already has the `state_before`/`state_after`
plumbing (added during Feature 002's own T021 verification) to do it correctly. A parallel
`check_ability_grant` function would duplicate that logic and risk drifting out of sync with
fixes made to one but not the other.

**Alternatives considered**: a dedicated audit function (rejected as needless duplication);
folding ability-grant checking silently into the existing "fact" conflict type with no new
state_category (rejected — FR-004 and SC-003 both need grants attributed and reported
separately from ordinary state conflicts, which requires its own `state_category` value).

## Decision: three acquisition methods, mapped to genuinely distinct fill behavior

**Rationale**: FR-002 asks for a small, fixed set (target 3) with at least one guaranteed-pick
and one weighted-roll method. Three, not two, gives User Story 2's scripted scenarios something
real to distinguish (does the DM correctly map a *decisive* kill differently from a *narrow*
one), which is the actual thing that story is testing.

- **Decisive Kill** → guaranteed pick: always returns the source archetype's designated
  "signature" template.
- **Narrow Survival** → weighted roll, biased toward defensive/resilience-flavored templates in
  the archetype's pool.
- **Non-lethal Subdual** → weighted roll, biased toward utility/control-flavored templates,
  distinctly from Narrow Survival's weighting.

**Alternatives considered**: two methods only (guaranteed + one generic weighted roll) —
rejected as too thin to actually exercise the DM's judgment in mapping narrated fiction to a
method, which is exactly what User Story 2 needs live evidence for.

## Decision: scripted scenarios cover every archetype and every method at least once, not the full cross-product

**Rationale**: With 3-4 archetypes and 3 methods, a full cross-product is 9-12 combinations;
SC-004's cheap-by-design budget (under 50 live calls total) is easiest to protect by covering
the *set* of archetypes and the *set* of methods, not every pairing — this is a probe of
whether the mechanism holds at all, not a combinatorial coverage sweep.

**Alternatives considered**: full cross-product coverage (rejected — costs roughly 2-3x more
API calls for marginal additional confidence at this stage; worth doing later if this probe
finds a real problem worth isolating further, not upfront).

**Output**: All Technical Context items resolved above; no remaining `NEEDS CLARIFICATION`.
