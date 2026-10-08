# Tasks: Scene state written by code (spec 010)

**Input**: [spec.md](spec.md), [plan.md](plan.md).

## Phase 1: Rules (wave R2-F)

- [x] T001 T-12-18 data in rules/data/pacing.yaml#details.scene_writes
- [x] T002 T-12-18 table and index row; 00.6.6a item 4, 12.11.9 steps 1 and 3, 12.4.8 step 8, 12.14.13 T1c, 12.3.1 position row; DL-12-77; decision log re-assembled; anchors; validator 0/0 (rules/_process/reports/R2-F-report.md)

## Phase 2: Store

- [x] T003 `PositionSet.band_drop` in engine/store/events.py and its reducer in engine/store/projection.py
- [x] T004 `expire_events` clears bands; `write_detail` supersedes an expired (cleared) slot, in engine/store/details.py

## Phase 3: US1 + US2 — writes

- [x] T005 Create engine/dm/scene_state.py: `beat_writes`, `response_values`, `write`, `lines`
- [x] T006 [US1] Call `beat_writes` in `world_step` before the NPC layer (engine/dm/world_step.py)
- [x] T007 [US2] Rolled activity as the `activity` detail; each response writes per T-12-18 (engine/dm/npc_layer.py)

## Phase 4: US3 — citable lines

- [x] T008 [US3] `ActivityEntry.slot`; `ensure_activities` rebuilds lines for whoever is present (engine/dm/adjudication.py, engine/dm/npc_layer.py)
- [x] T009 [US3] Render each slot (engine/dm/handles.py; engine/dm/roles/narrator.py); freshness skips scene slots
- [x] T010 [US3] Scene-slot writes back no change by themselves (engine/audit/claims.py `_SCENE_STATE_KEYS`)

## Phase 5: Tests and gates

- [x] T011 tests/engine/test_scene_state.py; existing tests updated for the `detail.activity` predicate
- [x] T012 Gates: full pytest, ruff, pyright, scripted long-horizon, live loop (≤ 25 narrated Haiku turns); results in implementation-results.md
