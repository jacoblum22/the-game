# Tasks: Check less (spec 011)

Spec: [spec.md](spec.md). Plan: [plan.md](plan.md). Item numbers are R2-G's spec 011 checklist.

## Phase 1: Setup

- [X] T001 Retire `details.max_active` and `claim_check.audit.skip_enabled` in rules/data/pacing.yaml (item 1)

## Phase 2: Foundational

- [X] T002 Remove `max_active`/`archived_details`; order lasting details by salience (correction = 2) then last use in engine/store/details.py and engine/retrieve/scene.py (item 1)
- [X] T003 Add `claim_log` and `said` to TurnRecord in engine/store/records.py; carry them from NarrationResult in engine/dm/narration.py::narrate_turn (items 2, 3)
- [X] T004 `DeclaredSentence.speaker`, `voices()`; `tier_of` unknown kind → T1a; scans on the narrator voice, pronoun clash logged in engine/audit/declare.py (items 2, 5, 6)

## Phase 3: US1 only critical narrator-voice errors block (P1)

- [X] T005 [US1] `certain()`, `blocking()`, `no_verdict`, `check_claims(texts=)` in engine/audit/claims.py (items 3, 4)
- [X] T006 [US1] Rewrite `_judge`: no per-turn audit; scans, polarity (undeclared: the only rolled beat), T2 narrator-voice only, T1a unwritable logged, echo logged, detail clashes logged except blocking slots; delete `_apply_writes`, `_settle` in engine/dm/narration.py (items 5–8)
- [X] T007 [US1] Tests: two swords, blocking classes block, non-blocking log only, T2 rule, clash logged in tests/engine/test_check_less.py

## Phase 4: US2 speech is testimony (P1)

- [X] T008 [US2] Narrator schema `speaker` (present people, `none` first) in engine/dm/schemas.py; prompt in engine/dm/roles/prompts/narrator.md; offline output in engine/llm/offline.py (item 2)
- [X] T009 [US2] Speech checks, PC-words `pc_agency`, `said` records, heard names in engine/dm/narration.py (item 2)
- [X] T010 [US2] Tests: said record not a fact, never truth-checked; PC-words caught in tests/engine/test_check_less.py

## Phase 5: US3 sampled audit (P1)

- [X] T011 [US3] `audit_mode` → sampled/off; `_sample` after delivery: diff + full Checker, `check_claims(texts=)`, claim log with `blocking_miss` in engine/dm/narration.py (items 1, 3)
- [X] T012 [US3] Update tests/engine/test_diff_audit.py (skip-gate test → sampled test) and any test reading the per-turn audit
- [X] T013 [US3] Metrics in evals/longhorizon.py::narration_loop (item 12)

## Phase 6: US4 resolution fixes (P2)

- [X] T014 [P] [US4] I-159 snag rule in engine/resolve/frame.py::_levers; test (item 9)
- [X] T015 [P] [US4] I-160(a): `reach_two_factors` in engine/resolve/types.py, engine/dm/schemas.py, engine/dm/roles/framer.py, prompt, offline; G4 route in engine/resolve/pipeline.py::_frame; test (item 10)

## Phase 7: US5 tags (P2)

- [X] T016 [US5] `Beat.pressure` (engine/resolve/types.py, engine/dm/roles/reader.py); Framer `asks` enum → `ProposedFrame.asks`/`Frame.asks` (item 11)
- [X] T017 [US5] `event_tags`, tag matching, rows, World fallback, crowd response in engine/dm/npc_layer.py (item 11)
- [X] T018 [US5] Tests: tag matching (refusal, served/defeated want), crowd response in tests/engine/test_check_less.py

## Phase 8: Polish

- [X] T019 engine/CONVENTIONS.md entries; recompile cards (engine/build/compile_cards.py); re-record replays
- [X] T020 Gates: full suite, ruff, pyright on touched files; rules validator 0 ERROR / 0 WARN (pacing.yaml changed); scripted offline long-horizon (0 errors); live ≤ 25 narrated turns
- [X] T021 specs/011-check-less/implementation-results.md

## Dependencies

T001–T004 before stories. US1 before US2/US3 (same file). US4 and US5 independent of US1–US3.
MVP: US1 + US3 (the gate relaxes and the audit stops gating).
