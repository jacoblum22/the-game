# Tasks: Typed intended change (spec 015)

**Input**: [spec.md](spec.md), [plan.md](plan.md). Tests are requested by the brief (gates).

## Phase 1: Foundational (the typed change)

- [x] T001 `Change` model and `Beat.change` in engine/resolve/types.py; `BeatEntry.change`, `.changed`, `.change_refused`, `.change_kind` in engine/dm/adjudication.py
- [x] T002 Reader schema `change {kind, what, whom}`, `SchemaContext.change_kinds` / `.change_ids` filled in `schema_context` in engine/dm/schemas.py
- [x] T003 `ReaderBeat.change` → `Beat.change` in `plans`; `log_changes` (<save>.changes.jsonl) in engine/dm/roles/reader.py, called inside `read_message` (it holds the scope ids)
- [x] T004 [P] Reader prompt section (kinds, slots, two changes are two beats) in engine/dm/roles/prompts/reader.md
- [x] T005 [P] Offline reader types a change by verb in engine/llm/offline.py

## Phase 2: US1 - a success changes the world (P1)

- [x] T006 [US1] engine/resolve/change.py: `holder_of`, `apply_change` per kind and reach, refusals with reasons
- [x] T007 [US1] Call `apply_change` from `_finish` (resolved) and `_no_roll` (reach 2); fill the BeatEntry change fields; RESULT change line in engine/resolve/pipeline.py and engine/dm/oof.py (`change_result_line`)
- [x] T008 [US1] T-12-18 fold: Grapple rows only for `restrain`/untyped, `restrain` on any verb, `free` clears the hold in engine/dm/scene_state.py
- [x] T009 [US1] Holder fact first in engine/dm/codex.py `_inventory` and engine/audit/claims.py `_Ctx.holder`

## Phase 3: US2 - the OFFER shows the change (P1)

- [x] T010 [US2] `offer_change_lines` (the change and a "Then:" line) in engine/dm/oof.py; `_offer` passes the queued acts in engine/resolve/pipeline.py

## Phase 4: US3 - the narration cites it (P1)

- [x] T011 [US3] Must-name `change` item in engine/dm/handles.py; narrator words in engine/dm/roles/narrator.py; `_beat_for` overlaps change words in engine/audit/claims.py

## Phase 5: US4 - lift attribute (P2)

- [x] T012 [US4] `lift_attribute` in `_frame_check` step 4 and `alternatives(attrs=)` in engine/resolve/frame.py

## Phase 6: US5 - knockout line (P2)

- [x] T013 [P] [US5] Staggered card wording in engine/harm/apply.py; wound load in the foe RESULT in engine/dm/world_step.py

## Phase 7: Tests, evals, gates

- [x] T014 tests/engine/test_intended_change.py: each kind on success and by reach; failure; purse from the save state; two-change message → two beats; lift attribute default; knockout status line; the Laya log line (kind enum ≤ 20 options, inputs present) [analyze: C1]
- [x] T015 Golden `change_kind` labels (01.2.7, before reading answers) in evals/reader_golden.jsonl and evals/reader_heldout.jsonl; scorer field in evals/reader_golden.py and evals/reader_live.py
- [x] T016 Full pytest, ruff, pyright; re-record replay (`py -3.12 -m tests.replay.record_games`); scripted long-horizon; Haiku golden + held-out; live fighter run; specs/015-intended-change/implementation-results.md; engine/CONVENTIONS.md section

## Dependencies

T001-T003 block everything; T006 blocks T007-T011; T012, T013, T015 are independent of US1-US3.
