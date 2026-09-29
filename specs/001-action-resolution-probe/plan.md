# Implementation Plan: Action Resolution Probe

**Branch**: `001-action-resolution-probe` | **Date**: 2026-09-28 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-action-resolution-probe/spec.md`, plus
[probe-results.md](probe-results.md), the results of an earlier relayed-chat session that
already validated the core resolution logic informally and surfaced Patterns P16/P17.

## Summary

Build the smallest real implementation that exercises the AI DM's core resolution loop with
actual tool-calling and actual externalized state (Patterns P8, P13) — replacing the earlier
relayed-chat probe's human-in-the-loop simulation with real code. Scope is unchanged from
spec.md: one character, one tracked resource, freeform action descriptions resolved via a
deterministic degree-of-success roll, no character creation, no combat encounters, no
progression. This is deliberately the smallest possible slice, not a production architecture —
every choice below is picked to be cheap to change later, not to be permanently correct.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: `google-genai` (Google's Gen AI SDK, used for real tool-use/function
calling — no MCP for this feature; MCP's interoperability-across-clients value doesn't apply to
a single-process script and can be added later if it ever matters). *Amended during
implementation from the originally-planned Anthropic SDK — see research.md's amendment note;
only `src/dm_agent.py` changed as a result, confirming the "cheap to reverse" property this
decision was chosen for.*

**Storage**: A flat JSON session-log file (no database) — sufficient for one continuous session
per spec.md's Assumptions; cross-session persistence is explicitly out of scope

**Testing**: `pytest` for the deterministic resolution/degree-of-success calculation (a pure
function, fully unit-testable with no API calls); a separate scripted harness (not a unit test)
drives a real multi-turn session against the live API and computes the SC-002/SC-003 consistency
metrics automatically, replacing the human relay the earlier probe used

**Target Platform**: Local CLI, cross-platform (developed on Windows)

**Project Type**: Single project — CLI script, no frontend/backend split

**Performance Goals**: Not performance-sensitive; no hard targets. Loose expectation: a single
turn resolves within a few seconds under normal API latency

**Constraints**: Single continuous session only; no auth, no multiplayer, no persistence beyond
the session log file; model is a configurable parameter (env var), not hardcoded, so swapping it
later touches configuration, not code

**Scale/Scope**: Tiny by design — one character, one resource, on the order of 10-20 actions per
run, a handful of runs total. This is a foundation-pouring exercise, not game content.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle / Pattern | Status | Notes |
|---|---|---|
| I. AI-Driven Mechanical Resolution | **Pass** | The model calls the roll tool itself, as part of its own turn — this is the AI directing a tool it invokes, not an external engine dictating to it from outside its control. |
| II. Custom Ruleset by Design | **Pass** | The DC scale and degree thresholds are this project's own choice (informed by, not copied from, PF2e), not an adapted SRD. |
| III. Rule Flexibility (Base-Model Judgment by Default) | **Pass** | No judge-gate is built for this feature, consistent with the resolved default; the system prompt encodes the constraining patterns (P12/P16/P17) instead. |
| IV. MVP Scope Discipline | **Pass** | Single-player, text-based, CLI. |
| V. Combinatorial Build Diversity | **N/A** | No character-build system is exercised by this feature. |
| VI. Mandatory Consolidation | **N/A** | No progression content is added by this feature. |
| P8 Deterministic Degrees-of-Success | **Directly implemented** | The actual subject of this feature. |
| P13 Three-Layer AI-GM Architecture | **Partially implemented** | Tool-calls + externalized state: yes. Judge-gate: intentionally omitted per Principle III's current resolution — not a violation, a documented default. |
| P16 / P17 | **Encoded in system prompt** | Behavioral rules, not architecture — the DM's instructions must state them explicitly, same as the relayed probe's subagent prompt did. |

No unjustified violations. Complexity Tracking section below is empty by design.

## Project Structure

### Documentation (this feature)

```text
specs/001-action-resolution-probe/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md         # Phase 1 output
├── contracts/            # Phase 1 output
│   └── tools.md
├── spec.md               # Already written
├── probe-results.md      # Already written (earlier relayed-chat session)
└── checklists/
    └── requirements.md   # Already written
```

### Source Code (repository root)

```text
src/
├── resolution.py    # Pure function: roll + degree-of-success calculation. No API calls,
│                    # no I/O -- this is the one piece that must be fully deterministic and
│                    # unit-testable in isolation.
├── state.py         # Character state model + session-log read/write (flat JSON file).
├── tools.py          # Tool schemas + handler functions exposed to the model, wrapping
│                    # resolution.py and state.py -- this module IS the P13 boundary between
│                    # free-form narration and deterministic mechanics.
├── dm_agent.py       # Gemini API client wrapper: system prompt (encodes P8/P12/P16/P17
│                    # and Principle III's base-model-judgment default), tool-use loop.
└── main.py           # CLI entry point for an interactive session.

tests/
├── unit/
│   └── test_resolution.py       # Unit tests for the pure resolution function -- no network.
└── probe/
    └── run_scripted_session.py  # Drives a real multi-turn session against the live API with
                                  # a fixed sequence of action descriptions, logs every turn,
                                  # and computes the SC-002/SC-003 consistency metrics without
                                  # a human relay.
```

**Structure Decision**: Single project (Option 1). No web/mobile split applies; this is a CLI
script plus a scripted verification harness.

## Complexity Tracking

*No violations to justify — table intentionally left empty.*
