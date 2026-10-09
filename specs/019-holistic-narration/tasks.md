# Tasks: holistic narration (spec 019)

**Input**: [spec.md](spec.md), [plan.md](plan.md). Tests are gates (from the real save where possible).

## Phase 1: Measure first (US2)
- [x] T001 Baselines over the round-6 saves: `specs/019-holistic-narration/metrics.py` (I1's measures; reproduces
  I1's 57 stacked quotes in 34 turns)
- [x] T002 [US2][US4] Precision of the new and kept checks: `measure_checks.py` (first-person in the narrator's
  voice; outcome words over whole passages), `evals/precision_audit.py` (season words; the pronoun check on speech)

## Phase 2: The passage (US1, US4)
- [x] T003 [US1] engine/dm/schemas.py `narrator_schema` (passage + side list); retire the repair and fiction shapes
- [x] T004 [US1][US4] engine/audit/declare.py `Speech`, `Passage`, `Sentence`, `parse_output`, `sentences_of`,
  `coverage`, `unquoted`, `quote`, `first_person`

## Phase 3: The loop (US2, US3, US5)
- [x] T005 [US3] engine/dm/roles/narrator.py `Revision`, `revision_text`, `draft(revision=)`; drop `narrator_mode`
- [x] T006 [US2][US3] engine/dm/narration.py `_draft`, `_judge` over the passage, the one-revision loop, `_deliver`
  (cut, quote, render, prompt), `_said` whole speeches, `_mark_used` by scan; retire `MAX_REDRAFTS`,
  `_max_redrafts`, `_unanswered`, `_polarity`
- [x] T007 [US2] engine/audit/claims.py `passage_beat`, `outcome_words` as a precision check; rules/data/pacing.yaml
  measured `precision` for `season_words` and `outcome_words`; delete `max_redrafts`, `sentence_declaration`
- [x] T008 [US5] engine/audit/screen.py: retire `_acknowledged`

## Phase 4: F4's narration side (US6)
- [x] T009 [US6] engine/dm/handles.py `AGREED`, refused change not must-name; engine/dm/roles/narrator.py change and
  learned lines without "say it plainly"; engine/dm/roles/prompts/narrator.md (passage, speech in quotes, never
  restate the player, "write around it" removed)

## Phase 5: The audit and evals (US7)
- [x] T010 [US7] engine/dm/roles/checker.py `side_list_words`, last exchange only; prompts/checker.md; checker schema
  `unexpressed` passage-level
- [x] T011 evals/narration_plug.py `judge_passage`, one revision; evals/replay_bench.py revision count;
  engine/llm/offline.py narrator in the new shape

## Phase 6: Tests and gates
- [x] T012 tests/fixtures/round6_narration.json (`extract_fixture.py`, talker 232941 turns 2, 13, 14, 16);
  tests/engine/test_holistic_narration.py; existing narration tests moved to the passage shape
- [x] T013 Full pytest; ruff, pyright on touched files; re-record replay; offline long-horizon (scripted)
- [x] T014 Live talker on Haiku (15 turns); metrics against the I1 baselines
- [x] T015 implementation-results.md; commit

## Analyze (lean, before implementing)
| Id | Finding | Resolution |
|---|---|---|
| A1 | Checklist: "code scans over the whole passage" vs the cut removing "the offending sentence" (12.3.1) | Code splits the passage only to locate failures (assumption A1); the model writes one passage |
| A2 | Outcome words were "blocking item 1" yet unmeasured; passage-level they cannot be tied to a sentence's beat | Measured (T002): 1 of 10 real. Made a precision check that logs (VIII.2); `passage_beat` only when results agree (A2) |
| A3 | Checklist "rendered lines only as the last fallback, never instructions": the old repair showed `render` text in MISSING | The revision lists handles only ("not narrated: R1"); a test asserts the rendered words are absent |
| A4 | I1 suggests a PC-echo blocking check and a narrator-voice copy check, "measure before blocking" | Not added (A5): the cause (blind adds) is removed; the prompt line covers the habit; the echo is still logged. Measured live instead |
| A5 | `refs` to view fact ids fed detail usage marks (12.14.11) | Replaced by a code scan of stated details (A4); otherwise freshness would lose its marks |
| A6 | The "write around names or kinship" line is filed under 020 in the checklist but the file is in this lane | Removed here (the brief says so); 020 notified in the results |
| A7 | Coverage: every story has a task and a test | US1 test_declare + test_holistic_narration; US2 test_precision_checks; US3 test_repair, test_turn_narration; US4 test_repair, test_holistic_narration; US5 test_audit_screen, test_holistic_narration; US6 test_holistic_narration; US7 test_declare, test_diff_audit |

## Dependencies
T001-T002 before T007 (the precision values); T003-T004 before T005-T006; T012 after T006 and T009.
