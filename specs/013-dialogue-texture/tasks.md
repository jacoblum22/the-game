# Tasks: Dialogue and texture (spec 013)

Plan: [plan.md](plan.md). Item numbers = R2-H "Spec 013" checklist. Tests are requested by the brief.

## Phase 1: Setup
- [X] T001 Baseline full pytest on the worktree; record pass count in specs/013-dialogue-texture/implementation-results.md

## Phase 2: Foundational (blocks every story)
- [X] T002 New module engine/dm/testimony.py: said records (meta `npc.said`, ids `said.N`, `{speaker, turn, words, about, question, settled, fact}`), `said_by(state, npc)`, index helpers over meta `answers.index` (item 4)
- [X] T003 `answer.willingness(ctx, npc, record, beats)` in engine/dm/answer.py per PR-12-10 step 2, `willingness_by_row` from rules (item 2)

## Phase 3: US1 NPCs talk like people (P1)
- [X] T004 [US1] Retire the ladder in engine/dm/answer.py: delete `rungs_for`, `store_hit`, `pack_hit`, `ratify`, `point`, `_walk_on`, `_kept_at`, `_chain_logged`, `_pointer_said`, `_can_answer`, `_touches`, `ladder_owns`, `odds_for`, `public_local`, `_whereabouts`, the rung loop; ordinary route → willingness line; keep case route, casting, `volunteer` (item 1)
- [X] T005 [US1] engine/dm/world_step.py: `deliver_learning` / `_speech_answers` without rungs; `_look` without ratify/point; a question asked of no one present gets no line (item 1; edge case) [analyze: C1]
- [X] T006 [US1] engine/dm/turn.py: replace `ladder_owns` with a local speech filter (item 1)
- [X] T007 [US1] Delete engine/dm/roles/proposer.py, engine/dm/roles/prompts/proposer.md, `proposer_schema` in engine/dm/schemas.py; `Role.PROPOSER` → `Role.TESTIMONY` in engine/llm/base.py and engine/llm/offline.py (item 1)
- [X] T008 [US1] Remove `answer_ladder.repeat_pointer_limit` (rules/data/pacing.yaml) and `delivery.information.ladder_depth` (rules/data/social.yaml); validator 0/0 (item 1)
- [X] T009 [US1] `speaker_card` in engine/dm/packet.py; appended by `draft` in engine/dm/roles/narrator.py; `_speech_line` rewritten (item 3)

## Phase 4: US2 NPCs remember what they said (P1)
- [X] T010 [US2] engine/dm/narration.py `_said` writes said records + index; `_speech` adds `not_a_repeat` (`narration.freshness.said_overlap`) (item 4)

## Phase 5: US4 Only what matters is mandatory (P1)
- [X] T011 [US4] engine/dm/handles.py + engine/dm/roles/narrator.py: activities and `optional`-tagged NPC reactions leave the handle list; OPTIONAL MATERIAL section; retire `hide_stale`, `_set_aside`, `_mark_used` activity branch (item 6)
- [X] T012 [US4] engine/dm/npc_layer.py `ensure_activities` once per scene, own role cell else `other`; end on engagement in `respond` (item 7)
- [X] T013 [US4] engine/dm/npc_layer.py `addressed` = one addressee; `respond` responders = addressed ∪ targets ∪ concerned ∪ fight; concerned non-addressed → `optional`; speech/questions → willingness only (item 8)

## Phase 6: US3 Lazy settlement (P2)
- [X] T014 [US3] engine/dm/testimony.py `settle_triggered` (triggers a, c), claim call (`testimony_schema` in engine/dm/schemas.py, offline handler), routes, writes; `source: testimony` in engine/store/events.py; hook in engine/dm/turn.py before plans (item 5)
- [X] T015 [US3] Reader `rests_on`: schema field when unsettled said ids are in scope (engine/dm/schemas.py), Reader view lines (engine/dm/packet.py), parse (engine/dm/roles/reader.py) (item 5)

## Phase 7: Tests and polish
- [X] T016 tests/engine/test_dialogue_texture.py: said fed back (no contradiction / no repeat), settlement triggers, consequential via case only, must-name diet, activity once + ends on engagement, ended activity not a lever, bystander silent unless tag match (item 9)
- [X] T017 Delete/rewrite ladder tests in tests/engine/ (test_answer.py, test_talk_cluster_c.py, test_incident.py, test_npc_response_and_learning.py, test_names_learned.py, others the suite shows)
- [ ] T018 evals/longhorizon.py OEQ-12-25 counts; run `--mode scripted`
- [ ] T019 Re-record replay (`py -3.12 -m tests.replay.record_games`); full pytest; ruff + pyright on touched files
- [ ] T020 Live talker playtest (15 turns, Haiku); compare to the re-run baseline
- [ ] T021 engine/CONVENTIONS.md "Answer ladder" section rewritten; specs/013-dialogue-texture/implementation-results.md; commit

## Dependencies
T002-T003 → US1 → US2, US4 (parallel-able in principle, same files in practice: sequential) → US3 → Phase 7.
MVP: US1 + US2.
