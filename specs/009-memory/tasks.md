# Tasks: Memory infrastructure (009 part A)

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md), [data-model.md](data-model.md),
[contracts/api.md](contracts/api.md). Tests are requested by the brief (unit tests per gate).

## Phase 1: Setup

- [x] T001 Record the baselines: per-role packet sizes on the offline_seed11 recipe and `evals/longhorizon.py --mode aged` output, in specs/009-memory/implementation-results.md

## Phase 2: Foundational (store shape)

- [x] T002 Add `narrated` to `FactSet.certainty`, an optional `persistence: Literal["lasting","scene","beat"] | None`, and a `DetailsUsed` payload (`fact_ids: list[str]`, type `details_used`) in engine/store/events.py
- [x] T003 Add `FactRecord.persistence`, `WorldState.details` (entity -> slot -> `DetailRef{fact_id, last_used}`; `None` value removes) and the `details_used` reducer in engine/store/projection.py

## Phase 3: US1 — details stay stated (P1)

- [x] T004 [US1] Create engine/store/details.py: `slots`, `write_detail` (new / same / superseded with `because` / contradiction / refused: unknown slot, unknown subject, a `scene`/`beat` slot from narration), `active_details` (cap `details.max_active` by salience 2 for generation/data sources else 1, then last use), `archived_details`, `expire_events`, `used_event`
- [x] T005 [US1] Stage `expire_events` in `end_scene` before `scene_ended` (12.4.8 step 8) in engine/world/scenes.py
- [x] T006 [US1] Ranked view: `scene` details salience 2, cleared (`None`) and `beat` details and archived lasting details never shown, in engine/retrieve/scene.py
- [x] T007 [US1] Tests: writer outcomes, cap + archive (a `details_used` mark keeps a detail active), expiry, rebuild equality in tests/engine/test_memory.py

## Phase 4: US2 — scene cards (P1)

- [x] T008 [US2] Fold scene cards in the projection (`WorldState.scene_cards`; data-model.md) in engine/store/projection.py
- [x] T009 [US2] Recency over stored scene starts (current + cards) replacing scene/last_scene in engine/retrieve/scene.py
- [x] T010 [US2] Create engine/retrieve/episodes.py: `cards_for(state, ids, k=2, before_seq=None)` (overlap, then recency), `card_lines(state, card)` (PC-known names; sealed facts and unknown names withheld)
- [x] T011 [US2] Recap summary lists card lines for scenes since the last recap in engine/dm/session.py
- [x] T012 [US2] Tests: cards regenerate identically from the log, `cards_for` order, recap reads cards, in tests/engine/test_memory.py

## Phase 5: US3 — spotlight (P1)

- [x] T013 [US3] Alias index and `resolve_names` (full names first; weak given/family keys only when unique) in engine/retrieve/scene.py
- [x] T014 [US3] `spotlight(state, message, last_delivery, beat, k)` in the 12.2.4 order, outside scope, seals respected, in engine/retrieve/scene.py
- [x] T015 [US3] Journal "what do I know about X" through `resolve_names` in engine/dm/codex.py
- [x] T016 [US3] Tests: order, K, seals, unknown names, full-name preference ("Joss Fenn"), journal, in tests/engine/test_memory.py

## Phase 6: US4 — per-role views (P2)

- [x] T017 [US4] `scene_view` takes spotlight and cards; spotlight rendered as the PC knows it within `view_budget.spotlight`, cards (ended scenes only, so the current scene's verbatim window is never repeated) within `view_budget.scene_cards` in engine/dm/packet.py
- [x] T018 [US4] `view_for(role, state, ctx)` per the 12.2.4 table; Narrator strips motive keys/predicates; `build_packet` uses it for a `WorldState` view (order and core unchanged); part-B TODOs named in engine/dm/packet.py
- [x] T019 [US4] Tests: per-role section presence and the Narrator leak test over a seeded offline game in tests/engine/test_memory.py
- [x] T020 [US4] Re-record the replay game (`py -3.12 -m tests.replay.record_games`) and measure per-role sizes after

## Phase 7: US5 — promises (P2)

- [x] T021 [US5] `promise_question`, `promises(state, about)` from open commitments, via `resolve_names`, in engine/dm/codex.py
- [x] T022 [US5] Route the promise question to `promises` in `oof_answer` and `_oof_shaped` in engine/dm/turn.py
- [x] T023 [US5] Tests: two similarly named people, only the asked one's promise listed, in tests/engine/test_memory.py

## Phase 8: Polish

- [x] T024a Aged harness: at each checkpoint also play a line naming an absent aged NPC (spotlight and cards on) and report its view tokens in evals/longhorizon.py
- [x] T024 Run `evals/longhorizon.py --mode aged` and `--mode scripted`; record numbers in specs/009-memory/implementation-results.md
- [x] T025 Engine conventions section for the new API in engine/CONVENTIONS.md; ledger row in rules/_process/issue-ledger.md
- [x] T026 Gates: full pytest, ruff, pyright on touched files; recompile engine/build/cards.json if stale; commit

## Dependencies

T002–T003 block all stories. US1 → US2 (expiry precedes the card close in `end_scene`). US3 independent of US2.
US4 needs US2 (cards) and US3 (spotlight). US5 needs T013.
Parallel: T010 with T013–T014 (different files); T015 with T017.

## Strategy

MVP = Phases 2–3 (store primitives). Then cards, spotlight, views, promises; measure last.

## Part B: diff-mode Checker and narration hookups

- [x] T030 [US6] Diff-mode `checker_schema` (`claims`, `undeclared`, `unexpressed`) in engine/dm/schemas.py
- [x] T031 [US6] Declarations in words, scope-tagged ids, spotlight in `checker_ids`, `full=` in engine/dm/roles/checker.py
- [x] T032 [US6] Shorter diff prompt (budget 550) in engine/dm/roles/prompts/checker.md
- [x] T033 [US6] `audit_mode` (skip disabled; 1-in-10 sampler built) and `_audit` in engine/dm/narration.py
- [x] T034 [US6] Figurative clock/sealed, no-id claims, gesture-in-place in engine/audit/claims.py and narration.py
- [x] T035 [US7] Undeclared elements written by tier; narrator `new` before `text`; one prompt line
- [x] T036 [US8] Profile diff on reuse (`profile_diff`), created looks into slots, `slot_of`
- [x] T037 [US8] Identity claims read `detail.<slot>`; incidental looks written as details (`_settle`)
- [x] T038 [US8] `details_used` at RECORD; freshness from `last_used`; image 3-gram scan retired
- [x] T039 `world_view` -> `view_for(Role.WORLD, …)`; TODO(009-B) removed from packet.py
- [x] T040 Offline scripted action contradictions: shared labels name the one here (SceneIndex, entity lines)
- [x] T041 Tests in tests/engine/test_diff_audit.py and test_turn_narration.py (freshness)
- [x] T042 Gates: full pytest, ruff, pyright; scripted harness; live loop (≤ 25 narrated Haiku turns); results
