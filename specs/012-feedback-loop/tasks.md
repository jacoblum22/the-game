# Tasks: The player feedback loop (spec 012)

**Input**: [spec.md](spec.md), [plan.md](plan.md). Cn = R2-G checklist item n.

## Phase 1: Foundation (store and role)

- [X] T001 `FactSet.pinned`, `FactSet.source` += `correction`, `FactRecord.pinned`, `WritesReverted.take_back` in engine/store/events.py and engine/store/projection.py (C5, C6)
- [X] T002 The take-back revert: before the scene start and over `scene_started`/`scene_ended` when `take_back` (engine/store/db.py `_revert`) (C6)
- [X] T003 [P] `Role.LOCATOR`: engine/llm/base.py, engine/llm/gemini.py output tokens, engine/llm/offline.py heuristic, engine/dm/roles/prompts/locator.md (C2)

## Phase 2: US2 — check the record (P1)

- [X] T004 [US2] Whole-transcript `_turns`; `locate` (code pins + locator call) and code category in engine/dm/dispute.py (C2)
- [X] T005 [US2] `gather` (provenance, other mentions, frame, claim log) and `recompute` (DC, modifier, odds at the commit) in engine/dm/dispute.py (C3, C4)
- [X] T006 [US2] Decide by PR-12-11 (record error pinned write, narration error, store-agrees, explain with quote, player wins on incidental slots, INV-9 explain and log, misread take-back, ruling error) in engine/dm/dispute.py (C5)
- [X] T007 [US2] Take-back limit and blockers; `_rewind(take_back=)`; labels `[CORRECTION]` / `[FIX]` in engine/dm/dispute.py (C6, C7)
- [X] T008 [US2] Pinned facts always in their subject's profile: engine/dm/packet.py `scene_view`, `render_view`, `spot_lines` (C5)

## Phase 3: US1 — one obvious way to report (P1)

- [X] T009 [US1] `FIX_HINT`; CLI hint after the first play screen, HELP line (play/cli.py); glossary line (engine/dm/oof.py) (C1)
- [X] T010 [US1] `reader.possible_dispute` + hint NOTE in engine/dm/turn.py; Reader prompt DISPUTE examples in engine/dm/roles/prompts/reader.md (C1)

## Phase 4: US3 — the review log and the metric (P2)

- [X] T011 [US3] Dispute record in the corrections ledger + `<save>.disputes.md` block (engine/dm/dispute.py) (C8)
- [X] T012 [P] [US3] `dispute_lines` + `--fix-every` in evals/longhorizon.py, baseline line; persona line in evals/playtest.py (C9)

## Phase 5: Tests and gates

- [X] T013 tests/engine/test_feedback_loop.py: the 8 scenarios on a real offline game (shared fixture); tests/engine/test_dispute.py updated; CLI hint/glossary tests in tests/engine/test_cli.py
- [X] T014 engine/CONVENTIONS.md section; re-record tests/replay/games; full pytest, ruff, pyright
- [X] T015 Live check (≤ 10 turns, Haiku via the Claude CLI) with planted disputes; specs/012-feedback-loop/implementation-results.md

## Dependencies
T001-T003 first; T004-T008 in order; T009-T012 after T004; T013-T015 last.
