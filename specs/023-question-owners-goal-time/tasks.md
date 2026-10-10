# Tasks 023

- [x] T1 Trace the round-7 causes on the saves (plan "Trace first").
- [x] T2 Write and label the made-up and edge cases (C1-C29) and the 7 real-save gates; commit before code (8619d6e).
- [x] T3 [US1] `not_oracle` + `_fiction_questions` (targets, people here, the PC's own record, content); delete
      `_KNOWS_Q`/`speech_owns` and the `[:60]` cut; `oracle.positive`/`MIRROR`.
- [x] T4 [US1] Oracle facts never snags: `frame._levers` refusal; `schemas.snag_fact_ids`; Framer prompt line.
- [x] T5 [US1] `fact_short`: subject named, one negation.
- [x] T6 [US2] `change.typed_goal`; `pipeline` asks instead of framing a costly `none` goal; `_moves` on `move_to`.
- [x] T7 [US2] `gate.reads_writing` on the goal and the method's words; `certain_talk` and the Reader's `asks` on
      `speech`; `secret` only on `learn`.
- [x] T8 [US2] 01.9.3: `frame.reverses`, success-at-cost prices filtered in `_costs`, `read_result`,
      `near_miss_choices`; `first_fitting_cost(exclude=)`.
- [x] T9 [US2] Fallback on its own scope (`_answer_redirect`, `beat_message`); retire the forced roll.
- [x] T10 [US3] `necessity.costly`; take the time in `_checked`/`_no_roll` (time, RESULT, evidence, reach cap).
- [x] T11 [US3] `already_agreed` (schema, prompt, `agreed_covers`); `apply_change` adds agreements; delete the 60%
      overlap.
- [x] T12 [US4] OFFER wording (`_breakdown`, `_chance_line`, `offer_block`); `reach_limit` replaces
      `reach_whole`/`reach_one_factor` (types, schema, framer, offline stub).
- [x] T13 Reader prompt (§2 fact questions, §3 `none`); Framer prompt; both within their word budgets.
- [x] T14 Tests: `test_spec023_cases.py`, `test_spec023_saves.py` (+ round-7 fixtures); update tests that encoded
      retired behaviour; re-record OFFER snapshots and the replay games.
- [x] T15 Reader live on Haiku: before and after on golden, held-out, goal-shape; goal-shape held-out after.
- [x] T16 Gates: suite, ruff, pyright, validator, longhorizon scripted; live explorer playtest.
- [x] T17 Merge milestone-1-playable, regenerate, full suite; `implementation-results.md`.

## Analyze (consistency check, done by hand)
- Every R2-K "Spec 023" build item maps to a task: fact-question drop (T3), Oracle fact positive/plain/never a snag
  (T3-T5), typed goal on rolled beats (T6), goal-keyed gates (T7), 01.9.3 (T8), fallback scope (T9), COSTLY/take
  the time with the stakes check and time charged (T10), typed already-agreed and no shrinking (T11), auto-commit
  only for costly Safe frames (T10: not-costly frames never reach `_offer`), OFFER wording (T12). Retire list →
  spec "Retired".
- Inconsistency found and fixed: spec US3 first listed "no party who would act" as a code test; it contradicted the
  explorer t12 gate and 01.6.9, so C23 and US3 were amended (the Framer's stakes source owns the onlooker).
- `resolution.yaml` unchanged: `take_the_time`, `auto_commit.only_when_costly` and
  `intended_change.before_framing` already say what was built; `reach_flags` tie-breaks are no longer read.
- No task touches spec 024's files (`packet.py`, `narrator.py`, `narration.py`, `npc_layer.py`, `answer.py`,
  `scene_state.py`).
