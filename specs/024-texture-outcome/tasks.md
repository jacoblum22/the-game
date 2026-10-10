# Tasks 024

- [x] T1 Trace on copies of the round-7 saves: standing-line inventory; talker turn.12/13; explorer turn.4/5;
      fighter turn.1 (plan "Trace first").
- [x] T2 Write and label the made-up and edge cases (`cases.md`); commit before implementing.
- [ ] T3 [US2] `effective_degree` and `undecided` in `dm/adjudication.py`; readers: `npc_layer` (talk outcome,
      response rows), `answer.willingness`, `scene_state._band`, `world_step._ok`, `audit/claims` (`_beat_success`,
      `undecided` re-exported), `audit/fallback._beat_line`, `handles.items`, `roles/narrator` (beat line, reading).
- [ ] T4 [US2] Paused beat unresolved: `_beat_line` and the handle render carry no result; not owed; `_speech_line`
      says the paused ask's target has not answered yet.
- [ ] T5 [US1] Pronoun helpers in `packet.py`; fill in view background, `present:` lines, name-unknown lines, refusal,
      willingness, activity and response rows, NPC act lines.
- [ ] T6 [US1] `packet.py`: background line for look/manner/voice (habit occasional); `present:` look only when
      `full`; drop "call them" and "every other screen"; drop the incident line; news as gist; header wording.
- [ ] T7 [US1] `narrator.py`: delete freshness (`freshness_lines`, `_repeated_lines`, `_freshness`, `used_details`);
      lead notes as gist; impetus wording; optional-material wording; `narration.py`: delete `_mark_used` and
      `_Sent.used`. `prompts/narrator.md`: background line, impetus.
- [ ] T8 [US1] `npc_layer.voiced_refusal` without the habit; `incident_line` as data.
- [ ] T9 [US3] `narration._text(sents, source)`: the passage as written.
- [ ] T10 [US4] P4 `_withheld` on refusals only; P5 "any posted notice", READING precision, pronoun tag precision,
      notice separator (`world_seed.yaml`); P6 `longhorizon.py` labels.
- [ ] T11 Data: delete `habit_max_per_scene` and the retired freshness keys (`pacing.yaml`); pronoun-fill rule lines
      on the person tables (`oracles.yaml`); validator 0/0.
- [ ] T12 Tests: `tests/engine/test_spec024_cases.py` (every case in `cases.md`); update the freshness and texture
      tests that asserted the retired behaviour.
- [ ] T13 `replay_r7.py`: rebuild the round-7 talker and explorer narrator packets; C10, C24, C25.
- [ ] T14 Full suite, replay re-recorded, ruff, pyright, validator, `longhorizon --mode scripted`.
- [ ] T15 Live talker playtest (Haiku, player Sonnet, ≤15 turns); `measure.py`.
- [ ] T16 Merge milestone-1-playable, regenerate, full suite; `implementation-results.md`; hand-offs.

## Analyze (consistency check, done by hand)
- Every R2-K "Spec 024" build item maps to a task: `effective_degree` and its readers (T3), the paused beat (T4),
  looks and habits as background, not on every `present:` line (T6), habit rows "now and then" (data already, R2-K;
  rendered occasional in T6), refusal lines without the habit (T8), the incident and factions as data (T6, T8),
  templates with stored pronouns (T5), the repetition scan logged only (assumption 2: `measure.py`, T15), P1 (T9),
  P4-P6 (T10). Retire list → spec "Retired"; `habit_max_per_scene` and retired keys deleted (T11).
- Every R2-K "Spec 024" case is in `cases.md` (C1-C7) with 18 more (C8-C25), including the brief's seven required
  ones (C1/C8 fire, C2 guild label, C9 she/her unnamed, C10 accepted near miss then willingness, C11 paused beat,
  C12 two paragraphs two speakers, C13 habit across three scenes).
- Lane: every file touched is in the brief's lane or listed with a one-line justification in plan.md; `turn.py`,
  `engine/resolve/` and the generators get hand-off notes, not edits.
- Conflict check with the owner's T3 ruling: no task adds a counter, mark, gate or "once per scene" offer.
