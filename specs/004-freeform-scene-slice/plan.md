# Implementation Plan: Freeform Scene Slice

**Branch**: `004-freeform-scene-slice` (work lands on `claude/project-thread-q2smmv`, based on
`integration-wave-swxsot`) | **Date**: 2026-10-07 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/004-freeform-scene-slice/spec.md`, the ruleset in
`rules/` (v1.0 RC), and the earlier stack research on branch `claude/happy-franklin-ypo2wq`.

## Summary

Build the first slice of the real engine: one prepared scene in which a player's freeform messages go
through the full turn loop (PR-12-1, T1–T12) and resolution pipeline (PR-01-1), with an OFFER pause
before every roll, all state in an append-only event store, narration drafted only from the stored
record, and every draft checked claim by claim by a separate checker call before delivery.

The technical approach (research.md, Option A) is a Python engine in which **code drives the loop and
the model fills typed forms**. At each `[J]` step the engine builds a JSON Schema whose enums come from
the rules and the current state, and asks one of four model roles to fill it. Every `[D]` step (frame
computation, the roll, read, costs, writes, time, boundaries, claim verdicts) is code tagged with its
rule id. Gemini 3.8 Flash fills every role, on one API key (owner decision, 2026-10-07). The checker is
a separate, persona-free call that can move to another model family by configuration alone; the
cross-family requirement of P13 is deferred as `TODO(CROSS_FAMILY_CHECKER)`.
State is a SQLite event log per campaign. The interface is a terminal REPL over a session API that a
web app will later wrap.

## Technical Context

**Language/Version**: Python 3.11+ (matches `pyproject.toml` on `claude/project-thread-9ivqgo`)

**Primary Dependencies**: `pydantic` v2 (state objects, per-turn schemas), `PyYAML` (rules data),
`google-genai` 2.25.0 (already pinned; every model role), `pytest`. Nothing else in the engine. All pinned
with hashes (research.md, supply-chain note).

**Storage**: SQLite (standard library `sqlite3`, WAL), one file per campaign: append-only `events` table
as source of truth, in-memory typed projection, snapshot per `scene_end`, index tables for facts and
rulings. See [data-model.md](data-model.md).

**Testing**: pytest. Unit and golden tests (worked examples with fixed dice) and contract tests run with
no network. Replay tests use recorded model outputs. Live sessions are a separate, budget-capped command,
never part of `pytest`.

**Target Platform**: Linux or macOS terminal now (cloud container for building, Jake's machine for
playtesting); a Linux VPS later through the web app (research.md R10).

**Project Type**: Library (the engine) plus a CLI front end.

**Performance Goals**: offer shown within 5 s of a rolled declaration; a non-pausing turn delivered within
10 s (median, SC-007). Deterministic engine work under 50 ms per turn.

**Constraints**: no number from the model (INV-3); writes before prose (12.2.8); checker as a separate,
swappable call (P13, cross-family deferred); one API key (`GEMINI_API_KEY`); ≤12 cards plus core per call (00.15.4); median ≤3¢ per turn and a hard per-session cap
(SC-008, FR-027); `rules/` is read-only.

**Scale/Scope**: one scene, one PC, 1–3 NPCs, 15 basic verbs, the 129 anchors available for retrieval,
9 boundary handlers implemented of 105, sessions of up to ~50 turns.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle / pattern | How this plan meets it | Status |
|---|---|---|
| I. AI-driven mechanical resolution | The model makes every judgment that sets something in motion; code runs only `[D]` steps, in the order PR-12-1 fixes. This matches 00-architecture's "Principle I, stated precisely". The constitution's own wording is stricter; research.md R12 recommends aligning it. | Pass, with a wording amendment proposed |
| II. Custom ruleset | Engine implements `rules/` directly; no SRD | Pass |
| III. Flexibility within bounds | Anchors with at most two knob deltas, precedent lookup before any adaptation, ruling ledger with `review_flag` (00.15.5–6) | Pass |
| IV. MVP scope | Single player, text only | Pass |
| V. Closed primitives | Not exercised (no character building in the slice) | N/A |
| VI. Consolidation | Not exercised (no progression content added) | N/A |
| VII. Default-deny gate | GATE step with G0–G4 (00.12.3); licence ids are enums from the PC's holdings; G3/G4 never narrated as possible | Pass |
| P3 ambiguity, not granularity | All judgments are closed-list fields with stated defaults | Pass |
| P7 codex | Out of scope for the slice; the session API returns the codex view so the web app can render it | Deferred |
| P8 deterministic degrees | `roll_check` and the degree rule (01.8.1) in code | Pass |
| P13 three-layer split | Code owns mechanics; the event store owns state; the claim checker is a separate call with abstain via `unknown` subjects and code-computed verdicts; moderation separate from consistency. **The checker shares the narrator's family (Gemini)**, by owner decision for this slice | Deviation, recorded below as `TODO(CROSS_FAMILY_CHECKER)` |
| P16 no dead ends / P17 graduated reveal | T10 "next step exists" screen; G3/G4 redirects; compound questions resolved per 01.10 with declaration-order default | Pass |
| Technology Constraints: `TODO(TECH_STACK)` | Resolved by this plan; to be recorded in the constitution once Jake agrees | Pending owner approval |

One recorded deviation (P13's different-family checker), justified under Complexity Tracking. Re-checked
after Phase 1 design: unchanged.

## Turn flow

```text
player message
  │ T1  log verbatim                                    [code]
  │ T2+ A1 READ  ── classify parts; PARSE/GATE/NECESSITY per beat; fact questions + Oracle odds   [Gemini]
  │ T3  load: triggers, narrator view, cards (≤12 per call)                     [code]
  │ T4  per beat: gate checks, find_rulings, anchor candidates (≤8)            [code]
  │      A2 FRAME ── anchor, deltas, attribute, deed tag, obstacle, levers, snags,
  │                  stakes, lethal, reach, threatened + alternate cost, method consequences   [Gemini]
  │      frame_check (refuse → re-ask A2 once naming the failure)               [code]
  │      ── OFFER pause ── (or auto-commit, 01.7.4) ── player commits / changes / withdraws
  │      roll, read (near-miss pause), consequence, record, evidence, beat_end  [code]
  │ T5  W WORLD (only if an NPC must respond) ── want/refusal flags; engine rolls tbl.npc_action   [Gemini]
  │      clocks, triggers, advance_time / mark_boundary                         [code]
  │ T6  all writes committed as events; re-read narrator view                   [code]
  │ T7–8 B DRAFT ── prose + mention list → write on mention / settle unsettled  [Gemini]
  │ T9–10 C CHECK ── claims (subject ids constrained to the scene) + screen flags   [Gemini; TODO cross-family]
  │      check_claims verdicts; D REDRAFT ≤2 → else plain fallback              [code / Gemini]
  │ T11 deliver   T12 log verbatim, counters, scene cut if the question is answered   [code]
```

Model call shapes are in [contracts/model-calls.md](contracts/model-calls.md).

## Project Structure

### Documentation (this feature)

```text
specs/004-freeform-scene-slice/
├── spec.md              # /speckit-specify output
├── plan.md              # this file
├── research.md          # Phase 0: stack options, decisions R1–R12, cost estimate
├── data-model.md        # Phase 1: events, state families in the slice, frame, turn record
├── quickstart.md        # Phase 1: how to validate the slice end to end
├── contracts/
│   ├── engine-api.md    # the session API the CLI (and later the web app) uses
│   ├── model-calls.md   # the five model roles: inputs, schemas, defaults
│   └── cli.md           # the terminal interface
├── checklists/requirements.md
└── tasks.md             # /speckit-tasks output (not created here)
```

### Source Code (repository root)

```text
engine/                        # new package; src/ (the probes) stays as-is for comparison
├── data/                      # RC-DATA: load rules/data/*.yaml, validate ids and enums
├── build/                     # compile_cards.py → cards.json; coverage.py (rule-id coverage report)
├── store/                     # RC-STORE, RC-LOG, RC-SEAL: events, projection, views, snapshots
├── rng.py                     # RC-RNG: named random.Random streams, every draw logged
├── time/                      # RC-SCHED: time ladder, modes, scheduler, handler registry
│   └── handlers/              # one module per owner chapter: h00.py, h01.py, h12.py, h15.py
├── resolve/                   # PR-01-1 [D] steps: gate checks, frame_check, roll, read, costs, oracle
├── retrieve/                  # RC-RETRIEVE: anchors (≤8), cards (≤12), triggers
├── audit/                     # RC-AUDIT: check_claims verdicts, plain fallback, T10 screen
├── dm/                        # PR-12-1 orchestrator; packets; per-turn schema builders
│   └── roles/                 # reader.py, framer.py, world.py, narrator.py, checker.py (+ prompts)
├── llm/                       # StructuredModel adapters: gemini.py, replay.py; budget (a second-family adapter later)
├── session.py                 # the session API (contracts/engine-api.md)
└── fixtures/                  # toll_bridge_scene.yaml, pc_prepared.yaml (validated against rules/data)

play/
└── cli.py                     # terminal REPL (contracts/cli.md)

tests/
├── engine/                    # unit tests per module
├── golden/                    # WE-* worked examples with fixed dice; T-01-3, T-01-10 tables
├── contract/                  # schema builders vs recorded states and outputs
├── replay/                    # recorded sessions replay to identical events
└── seeded_errors/             # ≥40 drafts with known claim errors (SC-003)

evals/
├── personas.py                # honest / curious / adversarial players (port of Feature 002's harness)
└── run_live.py                # budget-capped live sessions → report
```

**Structure Decision**: a new top-level `engine/` package separates the real engine from the probes in
`src/`, which keep working as the comparison baseline. `play/` holds front ends (CLI now, web later),
which depend on `engine.session` only. `engine/` mirrors the 00.14.1 runtime capabilities, so each tool in
00.14.2 has an obvious home.

## Implementation phases (input for `/speckit-tasks`)

1. **Foundation (no model calls).** Data loader; event store and projection for the slice's state
   families; RNG streams; scene and PC fixtures validated against `rules/data`; card compiler and
   coverage report.
2. **Deterministic resolution.** `frame_check` (PR-00-1, PR-01-2), degree rule, odds enumeration, read,
   cost menu application, Oracle, `roll_table`, rulings ledger; golden tests from WE-01-* and T-01-3/10.
3. **Time and boundaries.** Time ladder and modes, scheduler with phases, ordering and interrupts, the
   nine slice handlers, deferred-handler logging; WE-00-1 and WE-00-5 as golden tests.
4. **Model layer.** Adapters (Gemini, replay), schema builders per role, budget cap,
   refusal handling; contract tests.
5. **Turn loop.** PR-12-1 orchestrator with pause points (OFFER, clarifying question, redirect, near
   miss), T5 world responses, T8 write-on-mention, T9 claim check with redraft cycle and plain fallback,
   T10 screen, scene start/end.
6. **Session and CLI.** Session API, save/resume mid-offer, replay, the REPL, `report` command.
7. **Evaluation.** Seeded-error set and checker recall; persona harness; three live sessions; results
   written to `specs/004-freeform-scene-slice/implementation-results.md`, as Features 001–003 did.

Each phase ends with ruff, pyright and pytest clean. If any phase changes something under `rules/` (it
should not), the rules validator runs first.

## Complexity Tracking

| Violation or added complexity | Why | Simpler or compliant alternative, and why not now |
|---|---|---|
| **P13 deviation:** the checker is Gemini, the narrator's family (`TODO(CROSS_FAMILY_CHECKER)`) | Owner decision (2026-10-07): one provider and one key while the slice is built | A second-family checker (gpt-oss on Groq, or Claude Haiku) is the compliant design and stays the target. Limits on the risk now: the checker is a separate call that never sees the narrator's prompt or reasoning; it only extracts claims, and the verdicts are code; its recall is measured on seeded errors (SC-003). **Revisit** before any playtest outside the developer, or sooner if recall misses the target. Switching is a config change plus one adapter |
| Event log plus projection instead of plain tables | Replay (FR-026), resume mid-offer (FR-025), `revert_writes` | Mutable tables lose the history replay and revert need |
