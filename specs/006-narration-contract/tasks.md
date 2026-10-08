# Tasks: Narration contract and default NPC layer (spec 006)

Inputs: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md) (R1–R11), [data-model.md](data-model.md),
[contracts/narrator.md](contracts/narrator.md). Tests are requested by the spec's gates (SC-001).
Gate before each commit: full suite, `uvx ruff check` + `uvx pyright` on touched files.

## Phase 1: Setup

- [ ] T001 Rebuild stale `engine/build/cards.json` (`py -3.12 engine/build/compile_cards.py`; baseline 1177 passed after it)
- [ ] T002 Commit spec artifacts in `specs/006-narration-contract/`

## Phase 2: Foundational (blocks every story)

- [ ] T003 Record items with handles: `items(state, record, *, purpose, rules) -> list[RecordItem]` (R2; fields per data-model `RecordItem`) and `render` lines built from typed fields (R11) in `engine/dm/handles.py`
- [ ] T004 `record_text` writes `- R<n> <line>` for every item, guidance lines without a handle, in `engine/dm/roles/narrator.py`
- [ ] T005 Plain fallback renders every must-name item from `handles.items` (scene header only when a scene opened; "What do you do?" only without a pause) in `engine/audit/fallback.py`
- [ ] T006 Narrator schemas: `sentences` (refs enum = handles + view fact ids; about enum = scene scope; `new` items `{element_kind, name, ordinary, implied}`), fallback `fiction`+`declarations` (string index enum "0".."29"), and `repairs` (`replaces` enum = failing indices + `add`) in `engine/dm/schemas.py` (Narrator section only)

## Phase 3: US1 — declared sentences judged by code (P1)

Independent test: `tests/engine/test_declare.py` passes on built records; offline turns deliver first drafts.

- [ ] T007 [P] [US1] Tests: ref→claim judging with subject given, Checker subject override, name auto-add vs unknown proper name, numerals, pronouns, mechanics, sealed, atmosphere naming an NPC, coverage miss, the `fiction` fallback mode parsed to the same sentences in `tests/engine/test_declare.py`
- [ ] T008 [US1] `engine/audit/declare.py`: `DeclaredSentence`, `NewElement`, `parse_output(data, mode)`, `PacketIndex` (handles, facts, names/aliases, quantities, pronouns, seals) built from state or from packet text, scans (R4), `ref_claims` (R3), `coverage(sentences, items)`
- [ ] T009 [US1] `engine/audit/claims.py`: action claims sourced by a cited handle; claims restating a cited line supported (R3 (c)(d)); accept a `cited` map per sentence in `check_claims`
- [ ] T010 [US1] `engine/dm/roles/narrator.py`: `draft()` returns declared sentences (both modes); prompt `engine/dm/roles/prompts/narrator.md` rewritten for the sentences contract within 1000 words
- [ ] T011 [US1] `engine/dm/roles/checker.py`: `check_draft(..., sentences=, indices=)` keeps the narrator's split and indices
- [ ] T012 [US1] `engine/llm/offline.py`: offline narrator emits sentences citing the handle of each line it renders; repair answers drop failing sentences
- [ ] T013 [US1] `engine/dm/narration.py`: `judge_draft` (declarations + scans + Checker audit + `check_claims` + coverage + screen per sentence); coverage replaces the Checker's acknowledged/next-step flags

## Phase 4: US2 — tiers (P1)

Independent test: tier lookup and `undetermined` split tests.

- [ ] T014 [P] [US2] Tests: kind→tier table, non-ordinary person → T2, unknown kind → T2, T2 cited by a record line passes, incidental `undetermined` written as narrated, consequential goes to the Oracle in `tests/engine/test_declare.py`
- [ ] T015 [US2] Tier routing in `engine/audit/declare.py` (`tier_of`) and writing T1a via `write_mentions` (element_kind→mention kind) and T1b via the Oracle in `engine/dm/narration.py`
- [ ] T016 [US2] `undetermined` verdicts carry `incidental` (R5) in `engine/audit/claims.py`; narration writes incidental ones as facts (source `narration`) and asks the Oracle only for consequential ones

## Phase 5: US3 — default NPC layer (P1)

Independent test: `tests/engine/test_npc_layer.py` (determinism, addressed NPC always answers, voiced refusal, clamp, activity overwrite).

- [ ] T017 [P] [US3] Tests in `tests/engine/test_npc_layer.py`
- [ ] T018 [US3] `engine/dm/npc_layer.py`: `ensure_activities` (R7), `practice_for` (R8), `respond` (12.11.9 step 3 order, clamp toward 5, row 1 at Hostile), `voiced_refusal` (voice rolled on first answer), `addressed` (beats, parts naming them, the only NPC when the PC speaks)
- [ ] T019 [US3] `engine/dm/world_step.py::npcs_respond` calls the layer (Talk regexes untouched); `engine/dm/roles/world.py` becomes the candidate tie-breaker (R6); `engine/dm/roles/prompts/world.md` updated
- [ ] T020 [US3] Activities and responses become record items (handles) in `engine/dm/handles.py`; `ensure_activities` also runs before scene-opening narration in `engine/dm/narration.py`

## Phase 6: US4 — per-sentence repair (P2)

Independent test: `tests/engine/test_repair.py` with a scripted narrator.

- [ ] T021 [P] [US4] Tests: one failing sentence repaired, passing ones untouched and not re-sent; cut-type failures dropped without a call; two rounds then cut + rendered line + `rule_conflict`; no ruling when cuts alone keep coverage; plain fallback when nothing passed; prompt restored only if cut, in `tests/engine/test_repair.py`
- [ ] T022 [US4] Repair loop in `engine/dm/narration.py` (`narrate_checked` rewritten: draft → judge → cut/redraft per sentence → render → screen), narrow repair message in `engine/dm/roles/narrator.py`
- [ ] T023 [US4] Update existing narration tests that encoded retired behaviour (`tests/engine/test_narration_convergence.py`, `test_narration_i127.py`, `test_turn_narration.py`, `test_npc_response_and_learning.py`, seeded errors) to the new contract

## Phase 7: Measurement

- [ ] T024 `evals/narration_plug.py`: packet→new-contract packet, `haiku` narrator (Claude CLI, `evals/playtest.ask_claude`), `offline` narrator, `judge` (packet mode), repair simulation counting narrator calls and cuts; `evals/replay_bench.py` reports the four gate measures for plugs that return them
- [ ] T025 Run longhorizon scripted; run the replay plug on ≤ 80 packets with Haiku; save `evals/baselines/replay_006.txt`
- [ ] T026 Re-record replay fixtures (`py -3.12 -m tests.replay.record_games`)

## Phase 8: Retire (each only after its replacement passes)

- [ ] T027 Retire `_carry` / `_passed` / `_key` in `engine/dm/narration.py`
- [ ] T028 Retire the `pure_cut` / `keep_prompt` branches in `engine/dm/narration.py`
- [ ] T029 Retire the "What do you do?" patch-in (past-budget branch) in `engine/dm/narration.py`
- [ ] T030 Retire `_mention_name` / `_GENERIC_PREDICATES` in `engine/dm/narration.py`
- [ ] T031 Retire `_FORBIDDEN_NEW` keyword list (→ tier lookup) in `engine/audit/claims.py`
- [ ] T032 Retire `_DEEDS` / `_deed` in `engine/audit/claims.py`
- [ ] T033 Retire `_atmosphere` / `_reacts_to_incident` / `GIVEN_NOTES` / `_restates_given` in `engine/audit/claims.py`
- [ ] T034 Demote `_apply_writes` to a backstop (only undeclared unknown subjects) in `engine/dm/narration.py`
- [ ] T035 Retire `_settle` on incidental claims (consequential only) in `engine/dm/narration.py`
- [ ] T036 Retire the addressed-NPC speech exception in `_action`, `engine/audit/claims.py`
- [ ] T037 Retire the I-128 activity cutting (activity is a `position` claim against the activity line) in `engine/audit/claims.py`
- [ ] T038 Retire the World LLM call as the default path in `engine/dm/world_step.py`

## Phase 9: Polish

- [ ] T039 `engine/CONVENTIONS.md` narration/audit/NPC-layer sections updated
- [ ] T040 `specs/006-narration-contract/implementation-results.md` with the gate table; append to `research_notes/Playtest round 2 solutions/OVERNIGHT-LOG.md` is the orchestrator's (not done here)

## Dependencies

Phase 2 → US1 → US2 (needs the judge) → US4 (needs the judge); US3 depends only on Phase 2 (T020 on T003).
Measurement after US1–US4; Retire after Measurement shows the replacements pass; Polish last.

## Parallel examples

T007, T014, T017, T021 (test files) can be written in parallel; T018 (npc_layer) is independent of T008–T013.

## Strategy

MVP = Phase 2 + US1 + US4 (the contract and repair); US2 and US3 complete the gate. Retirements land last so
every replaced path has a passing replacement first.
