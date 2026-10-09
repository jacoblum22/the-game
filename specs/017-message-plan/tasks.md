# Tasks: A message is a plan of beats (spec 017)

**Input**: [spec.md](spec.md). Tests are requested by the brief (gates).

- [x] T001 `BeatPlan.when`; `run_beats` re-checks before each beat (`_recheck`) and opens the `plan` pause (`_ask`);
  `resume` answers it and continues after a withdrawn beat; `own_line` (the beat's own clause) in
  engine/resolve/pipeline.py
- [x] T002 Every Reader beat in `plans` (with `when`), the single beat's line by `own_line` in
  engine/dm/roles/reader.py (single call sites)
- [x] T003 SPEECH carried in a pause's detail (`said`, `said_first`); the resuming or closing turn adds it to the
  record; a `plan` pause runs T5; reader.queued notes dropped (the plan holds them) in engine/dm/turn.py
- [x] T004 Fixtures cut from the real saves: tests/fixtures/plan_fighter_turn4.db.gz, plan_fighter_turn11.db.gz,
  plan_talker_turn14.db.gz
- [x] T005 Tests in tests/engine/test_message_plan.py: fighter turn 11 title and continue; fighter turn 4 "demand
  their story"; PC down asks; talker carters answered; existing test_pipeline three-beat test updated (01.2.3 confirm)
- [x] T006 engine/CONVENTIONS.md pipeline section; gates (suite, ruff, pyright, longhorizon scripted, live fighter)
