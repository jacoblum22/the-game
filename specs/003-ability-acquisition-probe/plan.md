# Implementation Plan: Ability Acquisition Probe

**Branch**: `003-ability-acquisition-probe` | **Date**: 2026-09-29 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/003-ability-acquisition-probe/spec.md`, plus
[reports/Emergent power acquisition mechanisms.md](../../reports/Emergent%20power%20acquisition%20mechanisms.md)
and Pattern P5 in `.specify/memory/constitution.md`, which this feature directly implements the
first (specific-ability-from-source-and-method) flavor of.

## Summary

Add a small, hand-authored, fully-enumerable pool of source archetypes and effect templates
plus a small set of acquisition methods, each mapping to a distinct deterministic fill
mechanism (guaranteed pick or weighted/biased roll) — all plain Python, zero LLM involvement in
the pool's *contents*. Expose granting an ability as a new deterministic tool call on top of
Feature 001/002's existing tool-calling architecture, so the narrating AI decides *when* to
call it and supplies *which* source archetype and acquisition method a narrated event implies,
but never decides *which effect* gets granted — that stays owned by the deterministic
`resolve_ability_grant` function. Extend Feature 002's auditor to catch the DM's narration
contradicting what it just mechanically granted. Validate with a handful of scripted live
scenarios, not a long session — this is a mechanism probe, not a long-horizon or content-scale
test.

## Technical Context

**Language/Version**: Python 3.11+ (unchanged from Feature 001/002)

**Primary Dependencies**: `google-genai` (unchanged). No new dependency — the new tool follows
the exact same `WorldStateToolHandlers`/tool-schema pattern Feature 002 already established for
`update_resource`/`set_fact`.

**Storage**: Flat JSON, extended in kind from Feature 002: `WorldState` gains one new additive
field (`ability_grants`), following the same non-breaking-extension precedent Feature 002 used
for its own additions. No database — the research gave no reason to introduce one, and this
probe's entire pool is small enough to live as a Python constant, not even a data file.

**Testing**: `pytest` for the deterministic parts (User Story 1 — `resolve_ability_grant`'s
gating and fill-mechanism logic), same split as Feature 001/002: pure logic gets a fast,
zero-cost unit test; live-model behavior (User Stories 2-3) is verified via a scripted probe
harness, not unit tests.

**Target Platform**: Local CLI, cross-platform (unchanged).

**Project Type**: Single project (unchanged).

**Performance Goals**: Deliberately small — SC-004 targets under 50 live API calls for the
*entire* live validation pass (User Stories 2 and 3 combined), roughly an order of magnitude
below even Feature 002's smallest (12-turn) verification runs. This is by design: the point of
a probe is to be cheap enough to re-run freely while iterating, not to stress-test scale.

**Constraints**: The probe's source archetypes, acquisition methods, and effect templates are
explicitly throwaway content for testing the mechanism (per spec.md's Assumptions), not
material intended to survive into the real game; reuses `roll_check`/`get_state`/
`update_state`/`update_resource`/`set_fact` unmodified, per FR-003.

**Scale/Scope**: 3-4 source archetypes × ~3 effect templates each (9-12 templates total), 3
acquisition methods, covering every archetype at least once and every method at least once
across the scripted scenario set (not the full archetype × method cross-product, which would
cost more than this probe's cheap-by-design goal justifies).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle / Pattern | Status | Notes |
|---|---|---|
| I. AI-Driven Mechanical Resolution | **Pass** | Same reading already established by `roll_check`/`update_state` in Feature 001: the AI decides *to* call `grant_ability` and supplies which archetype/method a narrated event implies, but the tool's own code — not the AI narrating in prose — deterministically decides which effect template results. |
| II. Custom Ruleset by Design | **Pass** | A purpose-built mechanic, not an adapted SRD system; the whole point is a small, closed set an AI adjudicator can track exactly. |
| III. Rule Flexibility (Base-Model Judgment by Default) | **Pass** | Mapping a narrated event to one of the fixed source archetypes/acquisition methods is exactly the kind of judgment call Principle III already governs (base-model judgment, no separate judge-gate) — this feature doesn't introduce a new gate for that mapping, and explicitly does not build the class-emergence classifier (FR-007), which is the piece that would actually need one. |
| IV. MVP Scope Discipline | **Pass** | Single-player, text-based, unchanged. |
| V. Combinatorial Build Diversity via Closed Primitives | **Pass** | This feature is a direct, minimal implementation of Principle V's required shape: fixed slots (source archetypes) × fixed option pools (effect templates), recombined via acquisition method — not an open-ended list. |
| VI. Mandatory Consolidation of Aging Content | **N/A, with a caveat** | The probe's content is explicitly throwaway (spec.md Assumptions), so there's nothing here that needs a retirement mechanism yet. This is *not* a resolved answer for Principle VI in general — once a future feature authors the real, permanent class/effect content, that feature MUST address consolidation properly; this probe's exemption doesn't carry forward. |
| P5 Emergent-by-History Power Acquisition | **Directly implements (first flavor only)** | Builds exactly the source-gates-pool + method-picks-fill mechanism the fifth research pass resolved. Explicitly does not implement the class/archetype-emergence flavor (the classifier, the derived label, the three-valued policy) — FR-007 rules it out of scope; that remains a separate future feature depending on this one. |
| P6 Named Composite Bonuses | **N/A** | No effect-combination/stacking behavior is in scope here — this probe covers acquisition only, not how multiple granted effects interact once held. |
| P13 Three-Layer AI-GM Architecture | **Reused, extended** | The new tool follows the same deterministic-tool-calls-own-mechanics split; the auditor extension (User Story 3) directly reuses Feature 002's `check_turn`, adding one more thing it checks rather than a parallel mechanism. |
| P3 Granular State Is Not the Risk | **Directly satisfied** | `ability_grants` is new tracked state, but User Story 3's auditor extension is exactly the reconciliation layer P3 requires alongside any new granular state — not added as an afterthought. |

No unjustified violations.

## Project Structure

### Documentation (this feature)

```text
specs/003-ability-acquisition-probe/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md         # Phase 1 output
├── quickstart.md         # Phase 1 output
├── contracts/
│   └── tools.md          # Phase 1 output
├── spec.md               # Already written
└── checklists/
    └── requirements.md   # Already written
```

### Source Code (repository root)

```text
src/
├── resolution.py      # Unchanged (Feature 001)
├── state.py            # Unchanged (Feature 001)
├── tools.py             # Unchanged (Feature 001) -- roll_check/get_state/update_state stay as-is
├── dm_agent.py           # Unchanged
├── main.py               # Unchanged
├── world_state.py        # EXTENDED (Feature 002's file): WorldState gains one new additive
│                         # field, ability_grants: list[AbilityGrant]; WorldStateToolHandlers
│                         # gains grant_ability(); EXTRA_TOOL_SCHEMAS gains its tool schema.
│                         # update_resource/set_fact/roll_check/update_state stay byte-for-byte
│                         # unmodified, same discipline Feature 002 already used for its own
│                         # additions.
├── ability_pool.py        # NEW: SOURCE_ARCHETYPES, ACQUISITION_METHODS, EffectTemplate,
│                         # AbilityGrant dataclasses, and the pure, zero-API
│                         # resolve_ability_grant(source_archetype, acquisition_method) ->
│                         # EffectTemplate function -- User Story 1 lives entirely here.
└── auditor.py             # EXTENDED (Feature 002's file): check_turn gains an optional
                          # ability_grant parameter; ConflictRecord.state_category gains an
                          # "abilities" value. check_isolation/existing conflict-type logic
                          # stays unmodified.

tests/
├── unit/
│   ├── test_resolution.py           # Unchanged
│   ├── test_scenario_schema.py       # Unchanged
│   ├── test_scenario_pipeline.py     # Unchanged
│   └── test_ability_pool.py          # NEW: pure tests of resolve_ability_grant's gating and
│                                     # fill-mechanism logic (User Story 1) -- zero API calls
└── probe/
    ├── run_scripted_session.py       # Unchanged
    ├── run_long_horizon_test.py       # Unchanged
    └── run_ability_acquisition_probe.py  # NEW: drives the small scripted scenario set (User
                                          # Stories 2-3) through the real dm_agent loop, checks
                                          # each ability-grant turn via the extended auditor,
                                          # and reports SC-002/SC-003's results
```

**Structure Decision**: Single project (Option 1), extending Feature 001/002's existing `src/`/
`tests/` layout — same as Feature 002's own decision, no new module boundary introduced.

## Complexity Tracking

*No violations to justify — table intentionally left empty.*
