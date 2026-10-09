# Tasks: spec 020

## Phase 0 - Evidence and blind labels (before any model answer)
- [x] T001 Read handoff §2/§3/§6, ROUND6-PLAN F2/F3, constitution VIII, R2-J checklist, DL-01-37, I4, I3 §6.
- [x] T002 Policy B3'/B5'/D1'/E in `evals/reader_golden_POLICY.md`; relabel golden + held-out (`goals` on all lines).
- [x] T003 Goal-shape breadth set `evals/reader_goalshape.jsonl` (35 lines, 8 shapes; the 5 coercion messages verbatim).
- [x] T004 Scorer: `goals` field; `reader_live.py --set goalshape`.
- [x] T005 Before: per-role tokens on the seeded scripted run (`evals/role_tokens.py`); old Reader on the goal-shape set.

## Phase 1 - F2 Reader (US1, US2)
- [x] T010 [US1] `prompts/reader.md` §3 goal-first; `how` field; retire the act-split lines.
- [x] T011 [US1] `schemas.reader_schema` `how`; `ReaderBeat.how`, `Beat.how`; `plans()` passes it.
- [x] T012 [US1] `normalise` folds against-will method beats into their goal; tests.
- [x] T013 [US2] `read_message` keeps `how` only when verbatim; test.
- [x] T014 [US2] `oof.goal_line`; `offer_title`, `pipeline._then`, `_ask` use it; drop the OFFER change line; tests.

## Phase 2 - F3 Context (US3-US6)
- [x] T020 [US3] `cards.py` GUIDANCE + `guidance_digest`; `load_cards_for` without role/situation cards; delete
  `situation_cards`, `core_cards`; Framer 15.3.2 on Talk.
- [x] T021 [US3] `build_packet` core = digest; `llm/base.py` title GUIDANCE; prompts name GUIDANCE.
- [x] T022 [US4] Director 2 / World 1 exchanges (per-role keep in `build_packet`; fetched from the turn log).
- [x] T023 [US5] `identity_lines` in the narrator view and the testimony view; test.
- [x] T024 [US6] lead-line filter in the narrator and World views; test.

## Phase 3 - Gates
- [x] T030 Fix tests that pinned the old packet; full suite; re-record the replay; rebuild `cards.json` if needed.
- [x] T031 ruff + pyright on touched files; validator 0/0 (pacing comment).
- [x] T032 Long-horizon scripted 300: engine errors; view tokens; `role_tokens.py` after.
- [x] T033 Haiku: golden, held-out, goal-shape; coercion 5/5.
- [x] T034 Live fighter playtest ≤15 turns (Haiku engine, Sonnet player).
- [x] T035 `implementation-results.md`; anti-pattern check; commit.
