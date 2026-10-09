# Tasks: round-4 engine fixes (spec 018)

**Input**: [spec.md](spec.md), [plan.md](plan.md). Tests are gates (one per story, from the saves where possible).

## Phase 1: Wording (US1, US6.1)
- [x] T001 [US1] Plain speech + no self-introduction: engine/dm/packet.py `speaker_card`, engine/dm/roles/narrator.py `_speech_line`, engine/dm/answer.py `WILL_WORDS`

## Phase 2: The change (US2, US4, US6.3)
- [x] T002 [US2] `Change.description` in engine/resolve/types.py; `description` in `change_schema` (engine/dm/schemas.py); Reader prompt line (engine/dm/roles/prompts/reader.md); Laya log field (engine/dm/roles/reader.py)
- [x] T003 [US2][US6.3] engine/resolve/change.py: `_person` (never the actor; description names one person), description scene fact for persuade_to/open/close, "Agreed by" words, `plain()` shows the description
- [x] T004 [US2] engine/store/details.py `expire_events`: clear every current scene-persistence fact (replaces the crowd_response case)
- [x] T005 [US4] engine/resolve/change.py `already_true`, `needs_target`; `apply_change` returns already-true words; engine/resolve/necessity.py trivial when already true; engine/resolve/pipeline.py `_start` asks "who?" (G0) before NECESSITY

## Phase 3: Movement (US3)
- [x] T006 [US3] engine/resolve/necessity.py: a Move to the place here → trivial (`looks_here`, no would-act party). The approach itself needed no necessity code: the Framer's Move rubric already gives open ground a `trivial` base and an obstacle (the bakery queue) a rolled class, so only `_moved` changed (implement note)
- [x] T007 [US3] engine/resolve/pipeline.py `_moved` (engaged outside a conflict at reach 2+; no "still in"), `band_words`; engine/dm/scene_state.py `lines` uses it
- [x] T008 [US3] Travel: engine/dm/narration.py `narrate_turn` purpose `scene_open` on a scene start; engine/dm/handles.py scene line after the beats on a mid-turn cut, must-name; engine/dm/roles/narrator.py `PURPOSE_LINES["scene_open"]`

## Phase 4: Setting once (US5)
- [x] T009 [US5] engine/dm/packet.py `scene_setting(full=)`; engine/dm/roles/narrator.py `draft` passes it

## Phase 5: Speech check (US6.2)
- [x] T010 [US6] engine/audit/declare.py `pc_quotes` (quotes beside "you say" under an NPC speaker); engine/dm/narration.py `_speech` drops them from the NPC's spans

## Phase 6: Tests, evals, gates
- [x] T011 Fixtures tests/fixtures/fighter_lane_turn5.db.gz (turn 4's travel created the lane object in its narration, so the cut is before turn 5; travel is tested on the talker's walk to the inn) and tests/fixtures/talker_ivas_turn5.db.gz (truncated saves); tests/engine/test_round4_fixes.py: the four-turn loop → one approach; persuade the refugees on a description; redundant persuade certain; look line once; plain-words grammar; "Fair enough" caught; speaker card plain; travel narrates as scene_open; "who?" before framing
- [x] T012 Full pytest; ruff, pyright on touched files; re-record replay; scripted long-horizon (novelty-4); live talker + fighter on Haiku; engine/CONVENTIONS.md section; specs/018-round4-engine-fixes/implementation-results.md; commit

## Analyze (lean, before implementing)
| Id | Finding | Resolution |
|---|---|---|
| A1 | Checklist item 3 asks the Reader to type "look for" as Observe; tasks only guard in code | T006 also adds one Reader prompt line ("looking for someone not here is Observe, never move_to the place you are in") |
| A2 | Item 5 says "list look/furniture under optional material"; plan drops them for a one-line "already described" note | Deliberate: listing them every turn is what repeated; the note is the usage mark. Recorded in results |
| A3 | Item 6 "optional cheap scan" for self-introduction | Skipped (optional); prompt lines only. Revisit if DL-12-100's condition fires |
| A4 | Item 2 "consequential: case placement or casting picks the individual" | `learn` (the clue-bearing kind) already routes through answer.py's case route; for persuade/open a single name match in scope is the lazy pick. No casting call added |
| A5 | Constitution VII (default-deny gate) | "who?" and `trivial` both run after GATE in `_start`; the gate is untouched |
| A6 | Coverage | Every story has a task and a test in T011; no task without a story |

## Dependencies
T002 before T003-T005; T005 and T006 both edit `necessity()` (do together); T011 after T001-T010.
