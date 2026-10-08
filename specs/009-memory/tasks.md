# Tasks: Memory infrastructure (009 part A)

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md), [data-model.md](data-model.md),
[contracts/api.md](contracts/api.md). Tests are requested by the brief (unit tests per gate).

## Phase 1: Setup

- [ ] T001 Record the baselines: per-role packet sizes on the offline_seed11 recipe and `evals/longhorizon.py --mode aged` output, in specs/009-memory/implementation-results.md

## Phase 2: Foundational (store shape)

- [ ] T002 Add `narrated` to `FactSet.certainty`, an optional `persistence: Literal["lasting","scene","beat"] | None`, and a `DetailsUsed` payload (`fact_ids: list[str]`, type `details_used`) in engine/store/events.py
- [ ] T003 Add `FactRecord.persistence`, `WorldState.details` (entity -> slot -> `DetailRef{fact_id, last_used}`; `None` value removes) and the `details_used` reducer in engine/store/projection.py

## Phase 3: US1 — details stay stated (P1)

- [ ] T004 [US1] Create engine/store/details.py: `slots`, `write_detail` (new / same / superseded with `because` / contradiction / refused: unknown slot, unknown subject, a `scene`/`beat` slot from narration), `active_details` (cap `details.max_active` by salience 2 for generation/data sources else 1, then last use), `archived_details`, `expire_events`, `used_event`
- [ ] T005 [US1] Stage `expire_events` in `end_scene` before `scene_ended` (12.4.8 step 8) in engine/world/scenes.py
- [ ] T006 [US1] Ranked view: `scene` details salience 2, cleared (`None`) and `beat` details and archived lasting details never shown, in engine/retrieve/scene.py
- [ ] T007 [US1] Tests: writer outcomes, cap + archive (a `details_used` mark keeps a detail active), expiry, rebuild equality in tests/engine/test_memory.py

## Phase 4: US2 — scene cards (P1)

- [ ] T008 [US2] Fold scene cards in the projection (`WorldState.scene_cards`; data-model.md) in engine/store/projection.py
- [ ] T009 [US2] Recency over stored scene starts (current + cards) replacing scene/last_scene in engine/retrieve/scene.py
- [ ] T010 [US2] Create engine/retrieve/episodes.py: `cards_for(state, ids, k=2, before_seq=None)` (overlap, then recency), `card_lines(state, card)` (PC-known names; sealed facts and unknown names withheld)
- [ ] T011 [US2] Recap summary lists card lines for scenes since the last recap in engine/dm/session.py
- [ ] T012 [US2] Tests: cards regenerate identically from the log, `cards_for` order, recap reads cards, in tests/engine/test_memory.py

## Phase 5: US3 — spotlight (P1)

- [ ] T013 [US3] Alias index and `resolve_names` (full names first; weak given/family keys only when unique) in engine/retrieve/scene.py
- [ ] T014 [US3] `spotlight(state, message, last_delivery, beat, k)` in the 12.2.4 order, outside scope, seals respected, in engine/retrieve/scene.py
- [ ] T015 [US3] Journal "what do I know about X" through `resolve_names` in engine/dm/codex.py
- [ ] T016 [US3] Tests: order, K, seals, unknown names, full-name preference ("Joss Fenn"), journal, in tests/engine/test_memory.py

## Phase 6: US4 — per-role views (P2)

- [ ] T017 [US4] `scene_view` takes spotlight and cards; spotlight rendered as the PC knows it within `view_budget.spotlight`, cards (ended scenes only, so the current scene's verbatim window is never repeated) within `view_budget.scene_cards` in engine/dm/packet.py
- [ ] T018 [US4] `view_for(role, state, ctx)` per the 12.2.4 table; Narrator strips motive keys/predicates; `build_packet` uses it for a `WorldState` view (order and core unchanged); part-B TODOs named in engine/dm/packet.py
- [ ] T019 [US4] Tests: per-role section presence and the Narrator leak test over a seeded offline game in tests/engine/test_memory.py
- [ ] T020 [US4] Re-record the replay game (`py -3.12 -m tests.replay.record_games`) and measure per-role sizes after

## Phase 7: US5 — promises (P2)

- [ ] T021 [US5] `promise_question`, `promises(state, about)` from open commitments, via `resolve_names`, in engine/dm/codex.py
- [ ] T022 [US5] Route the promise question to `promises` in `oof_answer` and `_oof_shaped` in engine/dm/turn.py
- [ ] T023 [US5] Tests: two similarly named people, only the asked one's promise listed, in tests/engine/test_memory.py

## Phase 8: Polish

- [ ] T024a Aged harness: at each checkpoint also play a line naming an absent aged NPC (spotlight and cards on) and report its view tokens in evals/longhorizon.py
- [ ] T024 Run `evals/longhorizon.py --mode aged` and `--mode scripted`; record numbers in specs/009-memory/implementation-results.md
- [ ] T025 Engine conventions section for the new API in engine/CONVENTIONS.md; ledger row in rules/_process/issue-ledger.md
- [ ] T026 Gates: full pytest, ruff, pyright on touched files; recompile engine/build/cards.json if stale; commit

## Dependencies

T002–T003 block all stories. US1 → US2 (expiry precedes the card close in `end_scene`). US3 independent of US2.
US4 needs US2 (cards) and US3 (spotlight). US5 needs T013.
Parallel: T010 with T013–T014 (different files); T015 with T017.

## Strategy

MVP = Phases 2–3 (store primitives). Then cards, spotlight, views, promises; measure last.
