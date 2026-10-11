# HANDOFF 033 P5 (leads, witnesses, retire) on spec033-base (ac64bbf)
Done T050-T056. Code never creates a person or document for a lead or a witness on the tools path.
- Leads: `pacing.lead_candidates` (read-only; ties -> first unless `rng`), `lead_bookkeeping`, `lead_due`; `inject_lead` is the
  pipeline's, same event order. `dm_world._lead` tells "LEAD DUE: thread/source/form ... Nothing was added" (or "no open thread or
  source is on record") and resets the streak. A pending roll holds it: `world_step` returns [] under an open pause, the trigger stays.
- Witnesses: `case.short_of_sources(state)`; `dm_world._witness` (one call line in `world_step`) tells WITNESS NEEDED once per node
  per shortfall, only when the scene id changed since meta `witness_scene` (scene end, travel, time jump); meta `told_short` drops
  recovered nodes so a new shortfall is told again. h15 hook returns None under dm-tools (`state.game.config["engine"]`).
- Retire: `ending.retire_command` (exact `/retire`, casefold), `open_retire(tx)`, `ask_retire(ctx, withdraw=)`; `_end_game` opens
  it inside the DM turn (`t.paused`); `game._submit` on tools uses `retire_command`, `retire_choice/ending_choice(exact=True)`
  (None -> the question/menu shown again). `/retire` withdraws an offer/warning pause first (same two events as close_by_default);
  any other open question: "answer it first". Pipeline path untouched (`is_retire`, y/n words).
- 12.8.4: nothing outside `pacing` reads `fallback_queue`; `lead_audit` only marks stalled and queues, no bang is code-fired. Test.
- Guard: DENY `inject_lead`, `audit_cases`, `is_retire`, `_RETIRE` now `raise`; no `pending:P5` rows existed. reached.txt NOT committed.
- Gates: tests/engine/test_spec033_p5.py 29 passed; test_spec032_p4 T8 updated (LEAD DUE); guard 74 passed; ruff clean on engine/tests. Full pytest: the only failure is the `offline_seed11_dmtools` replay (LEAD DUE text differs); green after a local re-record (reverted, not committed).
Traps for P6/live: (1) `direct_choice` accepts the label head, so "yes"/"no" answer the retire question (exact label, kept).
(2) The LEAD form roll is a logged dice draw even when the DM ignores the lead; ties at a ladder rung pick the first, not a roll.
(3) `world_step` runs after the DM loop, so a lead/witness told in the same turn arrives via `_reask`; a scene opened by `_sync_scene`
after the world step is checked on the next exchange. (4) `end_game` leaves the turn's `_dm_loop` note saying "a roll is offered"
(P3's lane; text only). (5) `offline_seed11_dmtools` needs re-recording at merge (new `witness_scene`/`told_short` meta events).
(6) Live run watch: does the DM act on LEAD DUE/WITNESS NEEDED or ignore them (count per game); a `knows` id typo only gets a NOTE.
