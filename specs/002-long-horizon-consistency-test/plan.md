# Implementation Plan: Long-Horizon Consistency Stress Test

**Branch**: `002-long-horizon-consistency-test` | **Date**: 2026-09-29 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/002-long-horizon-consistency-test/spec.md`, plus
[reports/Long horizon LLM narrative benchmarks.md](../../reports/Long%20horizon%20LLM%20narrative%20benchmarks.md),
the research this feature's design is directly built from.

## Summary

Build a synthetic scenario-construction pipeline (adapted from NCP-Bench's three-stage
extraction: trajectory → commitments → initial facts, with T=0 isolation), extend Feature
001's state model to a generic multi-category `WorldState`, add a scripted adversarial/natural
player persona, and extend Feature 001's `judge_consistency` into a full fact/commitment/
player-input conflict auditor — all reusing Feature 001's `roll_check`/`get_state`/
`update_state` tools unmodified. Output is a category-resolved degradation report (survival vs.
success, conflict type, state category, turn of first conflict), not a pass/fail gate.

## Technical Context

**Language/Version**: Python 3.11+ (unchanged from Feature 001)

**Primary Dependencies**: `google-genai` (unchanged from Feature 001 — same client, same
model). No new dependency is introduced; the extraction pipeline, player persona, and auditor
are all plain `generate_content` calls against the same SDK already in use.

**Storage**: Flat JSON files, extended in kind but not in mechanism from Feature 001: one seed
file per generated scenario (trajectory + commitments + initial `WorldState`), one session-log
file per run (reusing `SessionLog`'s shape, extended with `ConflictRecord`s and a
`SessionOutcome`). Still no database — the research gave no reason to introduce one at this
stage; state complexity is growing in breadth (more categories), not in a way that needs
relational storage.

**Testing**: `pytest` for the deterministic, structurally-checkable parts only — JSON-schema
validation of the pipeline's three extraction outputs (are required fields present, are
commitment/trajectory IDs unique and cross-referenced correctly), which is genuinely
deterministic even though the content generating them isn't. The isolation check, the conflict
auditor, and the full scenario→session pipeline are semantic/live-API concerns, verified via
the scripted harness (`tests/probe/run_long_horizon_test.py`), same split as Feature 001.

**Target Platform**: Local CLI, cross-platform (unchanged from Feature 001)

**Project Type**: Single project (unchanged)

**Performance Goals**: Not performance-sensitive in the traditional sense, but real API-call
volume is a first-class concern this time (see Constraints) — Feature 001 made roughly 1-3
calls per turn over 10 turns; this feature's full SC-002 target (5 runs × up to 50 turns × a
player-persona call + DM turn + auditor call per turn) could reach several hundred calls if
every run ran to the cap. Mitigated by (a) sequencing development to validate the pipeline on
1 scenario / 1 short run (turn cap ~15-20, matching where NCP-Bench found most failures happen
anyway) before scaling to the full 5-run/50-turn target, and (b) the research's own finding
that most runs will terminate early on a conflict, which bounds real-world cost below the
theoretical worst case.

**Constraints**: Single continuous run per session (no cross-session persistence, same scope
boundary as Feature 001); campaign outlines are original text, not copyrighted material;
real, billed API calls at meaningfully higher volume than Feature 001 — budget and pace runs
accordingly rather than launching the full SC-002 batch in one go.

**Scale/Scope**: 3 scenarios × up to 5+ runs for the spec's success criteria, each run up to a
50-turn cap (provisional, per spec.md's Assumptions) — still a foundation-pouring exercise, not
game content, but a real step up in both API surface and state complexity from Feature 001.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle / Pattern | Status | Notes |
|---|---|---|
| I. AI-Driven Mechanical Resolution | **Pass** | Unchanged from Feature 001 — still reused unmodified (FR-003). |
| II. Custom Ruleset by Design | **Pass** | No ruleset content is introduced by this feature at all. |
| III. Rule Flexibility (Base-Model Judgment by Default) | **Pass** | The player-persona and DM turns still use base-model judgment; the new auditor is a *measurement* tool (checking against an explicit fact ledger/commitments), not a gate that grants or denies the DM authority — it doesn't reintroduce the judge-gate question Principle III already resolved against for now. |
| IV. MVP Scope Discipline | **Pass** | Still single-player, text-based; no new scope creep. |
| V. Combinatorial Build Diversity | **N/A** | No character-build system touched. |
| VI. Mandatory Consolidation | **N/A** | No progression content added. |
| P8 Deterministic Degrees-of-Success | **Reused, not modified** | Still the same fixed formula from Feature 001. |
| P13 Three-Layer AI-GM Architecture | **Directly tested, at higher complexity** | This feature is *specifically* a deeper test of P13's tool-calls + externalized-state claim, under conditions (longer sessions, more state categories) P13 itself was worried about. |
| P3 Granular State Is Not the Risk | **Directly tested** | This feature's whole point is finding out whether the reconciliation layer P3 calls for actually holds as state grows — an open question, not assumed answered. |

No unjustified violations. One judgment call worth recording explicitly: the auditor built here
(extending `judge_consistency`) still shares a model family with the narrator, same limitation
Feature 001's `implementation-results.md` already flagged against Pattern P13's eventual
independent-judge requirement. This feature does not attempt to fix that — it's out of scope
per spec.md's Assumptions — so it is not a new violation, but worth restating so it isn't
mistaken for a resolved concern once this feature ships.

## Project Structure

### Documentation (this feature)

```text
specs/002-long-horizon-consistency-test/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── pipeline-prompts.md
├── spec.md               # Already written
└── checklists/
    └── requirements.md   # Already written
```

### Source Code (repository root)

```text
src/
├── resolution.py     # Unchanged (Feature 001)
├── state.py          # Unchanged (Feature 001) -- CharacterState/ActionAttempt/SessionLog stay as-is
├── tools.py           # Unchanged (Feature 001) -- roll_check/get_state/update_state stay as-is
├── dm_agent.py         # Unchanged in its tool-use loop; judge_consistency is called BY the new
│                       # auditor.py rather than modified in place
├── main.py             # Unchanged
├── world_state.py       # NEW: WorldState (generic multi-category state extending
│                       # CharacterState's concept), Trajectory, Commitment, ConflictRecord,
│                       # SessionOutcome dataclasses, plus flat-JSON load/save for each
├── scenario_pipeline.py # NEW: the three-stage extraction pipeline (trajectory -> commitments
│                       # -> initial facts) plus the isolation check, each a generate_content
│                       # call using prompt templates adapted from NCP-Bench's public prompts
├── player_agent.py      # NEW: scripted adversarial/natural player-persona turn generator
│                       # (a generate_content call producing the next player action string)
└── auditor.py            # NEW: extends dm_agent.judge_consistency into a full conflict
                        # checker -- classifies a turn's narration against the fact ledger
                        # and active commitments as fact / commitment / player-input conflict
                        # or no conflict, with a category attribution (FR-006)

tests/
├── unit/
│   ├── test_resolution.py         # Unchanged (Feature 001)
│   └── test_scenario_schema.py    # NEW: deterministic structural validation of pipeline
│                                   # output shape (required fields, unique/cross-referenced
│                                   # IDs) -- not the semantic content, which isn't
│                                   # unit-testable
└── probe/
    ├── run_scripted_session.py    # Unchanged (Feature 001)
    └── run_long_horizon_test.py    # NEW: generates scenarios via scenario_pipeline, runs
                                    # persona-driven sessions via player_agent + the existing
                                    # dm_agent loop, checks each turn via auditor, and prints
                                    # the FR-008 report
```

**Structure Decision**: Single project (Option 1), extending Feature 001's existing `src/`/
`tests/` layout rather than introducing a new module boundary or service split.

## Complexity Tracking

*No violations to justify — table intentionally left empty.*
