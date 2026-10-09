# Tasks: The feedback loop, understand first, then verify (spec 014)

**Input**: [spec.md](spec.md), [plan.md](plan.md). Tests are part of the spec (SC-001..SC-003).

## Phase 1: Setup

- [x] T001 Corpus fixture: `tests/fixtures/feedback_corpus/corpus.json` (11 items: 8 `/fix` lines, 3 short forms) and 3 slim gzipped saves
- [x] T002 Harness `evals/feedback_corpus.py` (`open_at` cuts a save back to the report's turn; `score` = category+turn, outcome+plain answer)
- [x] T003 Before scores with spec 012 code: `evals/baselines/feedback_corpus_before_offline.json`, `evals/baselines/feedback_corpus_before_haiku.json`

## Phase 2: Foundational

- [x] T004 `Role.UNDERSTAND` replaces `Role.LOCATOR` in `engine/llm/base.py`, `engine/llm/gemini.py` (output cap), `evals/gemini_smoke.py`, `tests/contract/test_schemas.py` (sample message)
- [x] T005 New `engine/dm/understand.py`: `CATEGORIES` (= `pacing.yaml#feedback.categories`), `ABOUT`, `understand_schema(turn_ids, subject_ids)`, `default()`, `transcript(store, current, words, budget)`, `people(state, text)`, `understand(ctx, text) -> list[dict]`
- [x] T006 New prompt `engine/dm/roles/prompts/understand.md`; delete `engine/dm/roles/prompts/locator.md`
- [x] T007 `engine/dm/schemas.py` (spec 013's file, map entries only): delete `locator_schema`/`LOCATE_CATEGORIES`; `BUILDERS`/`DEFAULTS[Role.UNDERSTAND]` call `engine.dm.understand`
- [x] T008 Offline stand-in `_understand` in `engine/llm/offline.py` (replaces `_locator`): names/pronouns/season/number words in the report against the packet's people and transcript

## Phase 3: User Story 1 - understand and restate (P1)

**Independent test**: a fuzzy report gets "You're saying …" first and the right passage.

- [x] T009 [US1] `engine/dm/dispute.py`: delete `_NUM`, `_NUMBER_WORDS`, `_QUOTED`, `_STOP`, `_number`, `_named`, `_slot`, `_value_near`, `_claim_from`, `_pins`, `_candidates`, `_ask_locator`; `locate(ctx, text) -> list[DisputedClaim]` from the complaints (turn/quote verified, about/key/value mapped); `DisputedClaim` gains `believes`, `happened`, `about`
- [x] T010 [US1] `_done` restates `believes` first in the first block; record and review-log block gain `believes`
- [x] T011 [US1] `settle_dispute` answers each complaint (≤3), one CHOICE at most, combined `DisputeResult` (`claims`, first claim/record kept for callers)

## Phase 4: User Story 2 - verify and answer plainly (P1)

**Independent test**: spec 012's scenario tests plus the new rows.

- [x] T012 [US2] Not found row: nearest passage "did you mean" (`_nearest`) in `engine/dm/dispute.py`
- [x] T013 [US2] Ruling explanation: `_changes(store, state, frame_id, turn)` (what the beat wrote) and roll/degree/reach in plain words; open OFFER levers explained (INV-9) in `engine/dm/dispute.py`
- [x] T014 [US2] Pronoun and season rows (`_computed`) in `engine/dm/dispute.py`
- [x] T015 [US2] Incidental continuity: `activity` incidental; earlier version with the player's value → pinned correction; who_said_what/look with nothing on record → pinned `correction.<n>` (`player_reading_wins`) in `engine/dm/dispute.py`
- [x] T016 [US2] Remove bare "Logged." tails across `engine/dm/dispute.py` answers
- [x] T017 [US2] Check `default_identify` callers (tests use `identify=`) [analyze I1]; adapt `tests/engine/test_feedback_loop.py` and `tests/engine/test_dispute.py` (restatement first; same outcomes); new unit tests for not found, ruling explanation, season/pronoun, multi-complaint in `tests/engine/test_dispute.py`

## Phase 5: User Story 3 - measured on real complaints (P1)

- [x] T018 [US3] After scores: `evals/baselines/feedback_corpus_after_haiku.json` (and offline); below 9 in 10 understood, iterate `prompts/understand.md` and re-score [analyze C1]
- [x] T019 [US3] `tests/engine/test_feedback_corpus.py`: outcomes per item with the Haiku understanding replayed (ScriptedModel) from the after run

## Phase 6: Polish

- [x] T020 `engine/CONVENTIONS.md` feedback-loop section; `play/cli.py` checked (no change needed unless the live check shows one)
- [x] T021 Live check ≤ 10 turns, Haiku via Claude CLI, 3-4 corpus complaints re-planted; replies verbatim
- [x] T022 Gates: full pytest, `uvx ruff check`, `uvx pyright` on touched files; `specs/014-feedback-understand/implementation-results.md`; commit

## Dependencies

T004-T008 before US1; US1 before US2 (same file); US3 after US2. [P] none of note: most work is in `dispute.py`.
MVP: US1 + US2.
