# Tasks 033: the DM states, code records

Phases, lanes, models and waves: `plan.md` section 5. Cases: `cases.md` (C1-C12). Every phase: run
`ruff check .`, `pyright` on changed files and the tests of its lane; the full pytest (`PYTHONUTF8=1`,
`-p no:cacheprovider`) before handing off; report new failures only. Each phase moves its own denylist entries in
`tests/guard/viii9.py` from `log` to `raise` and adds its cases to `tests/guard/games_033.py` as a separate function
(`def game_<phase>(...)`; P6 assembles). Tag code with `[spec 033 <phase>]`.

## P0 guard census (Sonnet, W1, lane `tests/guard/`)
- [x] T001 `tests/guard/viii9.py`: `DENY` table (plan 3, R12) with every inventory function and pattern of reach Y/A
  from both inventories, each with its inventory id and `only_from` (only `conflict.start` <- `dm_tools._fight`);
  patch helpers (functions raise; patterns and word lists swapped for raising stand-ins); `VIII9_GUARD` log/raise.
- [x] T002 `sys.setprofile` reach recorder (engine modules only) and a pytest fixture that plays
  `offline_seed11_dmtools` (the `tests/replay/record_games.py` recipe on a temp path) under it.
- [x] T003 Census: run it in log mode; write `specs/033-dm-states-code-records/reach-census.md` (at most 60 lines):
  which DENY entries are reached, by which tool path; settle the low-confidence items (D13 D14 D16 D19 D20 D46 D53 D54,
  `world_step.deliver_learning`, `oracle.positive`, `codex` search, `audit.text` primitives); list reached
  word-matchers the inventories missed, each assigned to a phase lane (else P6).
- [x] T004 Static scanner (`tests/guard/test_viii9_static.py`): AST rules of plan 3 R12; `viii9_allow.py` seeded with
  today's hits, each classed P, F, S or `pending:<phase>`; the test fails on any unlisted hit and (from P6) on any
  `pending`.
- [x] T005 Runtime test (`tests/guard/test_viii9_runtime.py`): in `raise` mode, entries still `log` are recorded,
  not raised; the test asserts no `raise` entry is hit. Planted-call tests for C12.
- [x] T006 HANDOFF-P0.md.

## P1 contract (Sonnet, W1, lane: `dm_tools.py` schema/intake/dispatch, `resolve/types.py`, `dm.md`, `llm/offline.py`)
- [x] T010 `schema_for`: the plan 2 table's fields (`as`, `force`, `weapon`, `reads`, `approach` enum from data,
  `fail_on`; step `foes[]` with the act enum, `cost_form`; change `name`, `as`, `knows`, kind `position`; tool
  `end_game`; `said[].as`). A test pins the schema to the contract table.
- [x] T011 `resolve/types.py`: `Stated` (plan 1) and `Beat.stated: Stated | None = None`; `_propose_roll` fills it
  (validation of enums only; behavior is the later phases'). REFUSED for Force without `force`, an unknown
  `approach`, a `weapon` the actor does not hold.
- [x] T012 Dispatch stubs: `end_game` and `change position` return "not available yet" until P5/P2a wire them
  (`position` is wired here if trivial: one `position_set` event; then P2a only adds the reach refusal).
- [x] T013 `dm.md` = `contracts/dm.md.draft` (edit for anything the schema changed; at most 800 words; a test counts).
- [x] T014 Offline DM heuristic (`llm/offline.py` `Role.DM`): emits the new fields where its acts need them (fight
  `to`, `foes` with a strike while a FIGHT block is shown, `as` for words). Re-record `offline_seed11_dmtools` only.
- [x] T015 HANDOFF-P1.md.

## R rules (Opus, W1, lane `rules/`; follow CLAUDE.md's rules conventions; the orchestrator commits)
- [ ] T090 06.9.1 rewritten (plan 4) with the retired rationale and its watch measure; 06.9.3, 06.9.4 as guidance and
  the legality table (`cases.md` C4).
- [ ] T091 06.3.9 (the DM states the start range); 01.13.7 (the form is the DM's pick after the roll, among those that
  can land; the options table of C5).
- [ ] T092 PR-12-3 and 15.9.4 under the DM engine: tell, never spawn; 11.13.1: `/retire` or the DM's call.
- [ ] T093 `basic_verbs.yaml`: `target_kinds` per verb (C1 table) and `covered_by` licence ids per `excludes`
  entry; through the generator if one exists (re-run, diff).
- [ ] T094 `resolution.yaml#reverses_goal` (persuade_to, learn -> cost.closed_door on the same person; others none).
- [ ] T095 DL entry in `appendix/fragments/DL-CC.md`; re-assemble decision-log and traceability; anchors recompiled.
- [ ] T096 `validate_ruleset.py` 0 ERROR / 0 WARN; wave report appended.
- [ ] T097 HANDOFF-R.md.

## E measures (Sonnet, W1, lane `evals/`, `tests/evals/`)
- [x] T060 `evals/turn_judge.py`: seeded sample of turns per save; one Haiku call per turn and measure with the fixed
  rubric (plan 3 R11); JSON verdicts cached per (save, turn, measure); offline stand-in for tests.
- [x] T061 `evals/baselines/turn_judge_hand.yaml` format and the precision report (`count (p, n)`; "precision
  unmeasured" under 20).
- [x] T062 `npc_agency.py`: M10 from the judge (delete `leaked`); the ask rubric labels priced deals `priced`.
- [x] T063 `h2h_score.py`: C7 from the judge; read `round` boundaries and `screen.dm_tools.said` (032 trap 1).
- [x] T064 Tests (offline) and HANDOFF-E.md.

## P2a resolve: positions, contact, fight start, costs (Sonnet, W2, lane: `pipeline.py`, `change.py`, `conflict.py`, `costs.py`)
- [x] T020 `pipeline._finish`: stated beats skip `_moved`/`_contact`; `_stated_position` writes `stated.position` on
  success (C1.d).
- [x] T021 Force ladder from `stated.force` (C2); no `_DOWN`.
- [x] T022 `change.apply_change`: no untyped Grapple restrain and no `_person` name resolution for stated beats
  (C1.g); `change_kind=free` ends the actor's hold.
- [x] T023 `_cleanse` without `_FREEING` for stated beats.
- [x] T024 RESULT line: `entry.positions` words from the stated band or Force result (formatting only).
- [x] T025 `_roll`: no `conflict.start` for stated beats (R2).
- [x] T026 `conflict.strike_harm(weapon=, mode=)`, `weapon_of(rules, st, item)`; no `NONLETHAL`/`UNARMED` for stated
  beats (C1.e, C1.f).
- [x] T027 `_consequence`: params from `stated.fail_on` (no `_cost_params`); REFUSED data for missing sources (C5).
- [x] T028 `costs`: footing with no form on a stated beat returns the deferred options; `footing_options`,
  `apply_footing` (C5 options table).
- [x] T029 Tests C1.d-g, C2, C3 (engine side), C5; move P2a's DENY entries to `raise`; HANDOFF-P2a.md.

## P2b resolve: gate, necessity, frame, anchors (Sonnet, W2, lane: `gate.py`, `necessity.py`, `frame.py`, `retrieve/anchors.py`, `retrieve/scene.py`)
- [x] T035 `gate.check_gate`/`compute_gate`: stated `reads`, `approach` (exact entry), `covered_by` (C1.b, C1.c).
- [x] T036 `necessity.plain_reading` from `stated.reads`.
- [x] T037 `frame`: lift by take only plus the DM's attribute; `reverses` structural plus `reverses_goal`; `_fitted`
  no-op for stated beats.
- [x] T038 Anchors: a helper the code framer uses (`[verb_anchor]`); `retrieve/scene.focus_of(beat)` ids only.
- [x] T039 Tests C1.b, C1.c, C5 reversal; DENY entries to `raise`; HANDOFF-P2b.md.

## P4 people and testimony (Sonnet, W2, lane: `dm_tools.py` identity/testimony/measures/change kinds; `world/social.py`; `gen/case.py` `place_on`)
- [x] T030 `_party`/`_walk_on`/`target_kinds` per plan 3 R6; `"pc"` literal; `as` defaults from data (C8).
- [x] T031 `meet_npc(..., pronouns=, name=)`; creature walk-ons without `ANIMAL`.
- [x] T032 `_change`: `new_npc` (`name`, `as`, `knows` via `gen/case.place_on`), `new_item knows`, `npc_leaves`
  without a first-reachable default, `fight` requires `to`; the Strike/Grapple/Force reach refusal in
  `_propose_roll` from `conflict._band` (C3; NOT done in P4, left to P2a: `_propose_roll` is its lane); twin advice by
  exact name (C3, C7 placement, C8).
- [x] T033 `_told` spine-only (C9).
- [x] T034 Delete `_audit`, `_log_only`, `_content`, `_name_tokens` and their stats; `code_framer` focus and anchors
  from T038's helpers (if P2b has not merged, ids inline). Tests C8, C9; DENY to `raise`; re-record
  `offline_seed11_dmtools`; HANDOFF-P4.md.

## P3 foes and the answer turn (Sonnet, W3, lane: `resolve/foe_act.py`, `dm_world.py` foe part, `dm_tools.py` turn flow)
- [x] T040 `resolve/foe_act.py`: `legal_acts`, `foe_act` (C4 table), reusing `foe_beat`'s pieces and `change.hold`.
- [x] T041 FIGHT block: per foe id, band, conditions, state words, legal acts.
- [x] T042 `foes` intake: last step's list; stored in the pause `detail["foes"]` when a roll pauses; run by (retired by D2: the foe call `dm_world._foes` runs after the exchange settles)
  `dm_world.world_step` in place of `ws.foes_act`; lapses reported; `check_end`.
- [x] T043 COST TO SHAPE on the answer turn from P2a's deferred options; `cost_form` applied by `apply_footing`.
- [x] T044 One re-ask for missing picks (foes and cost form together), then wait / nothing, logged in (retired by D2/D3: no re-ask; omitted or illegal picks default and log `not_chosen:foes.<id>`)
  `stats.world.missing_picks`.
- [x] T045 Stats: `foe_turns` rows carry `picked_by: dm|lapsed|waited`.
- [x] T046 Tests C4, C5 (answer-turn side); DENY (`foe_beat`, `foes_act`) to `raise`; HANDOFF-P3.md.

## P5 leads, witnesses, retire (Sonnet, W3 parallel with P3, lane per plan 5)
- [x] T050 `pacing.lead_candidates` (read-only) and the bookkeeping half of `inject_lead` (lower trigger, reset
  streak, log) as its own function.
- [x] T051 `dm_world._lead` tells (C6); `inject_lead` unreached.
- [x] T052 `gen/case.short_of_sources` (read-only half of `audit_cases`); the h15 hook skips `audit_cases` under
  dm-tools.
- [x] T053 `dm_world._witness`: WITNESS NEEDED once per node (meta `told_short`), at scene end and after travel.
- [x] T054 Tests C6, C7 (the `knows` placement path is P4's; test it end to end here).
- [x] T055 `game._submit` under dm-tools: exact `/retire`; `dm_tools._end_game` opens `ask_retire`; menu answers by id
  or number (C10). `tests/e2e/driver.py` `retire_and_continue` uses `/retire` for dm-tools games.
- [x] T056 DENY (`inject_lead`, `audit_cases`, `is_retire` under dm-tools) to `raise`; HANDOFF-P5.md.

## P6 guard strict and gates (Sonnet, W4, lane `tests/guard/` plus fixes for guard hits)
- [x] T070 Assemble `games_033.py` from the phases' game functions; every `cases.md` row runs under the guard.
- [x] T071 All DENY entries `raise`; no `pending` allow-list entries; review every allow-list reason (P, F, S only).
- [x] T072 Planted-failure tests (C12) green.
- [x] T073 Re-record `offline_seed11_dmtools`; full pytest, ruff, pyright; `validate_ruleset.py` 0/0.
- [x] T074 Prompt word count test (at most 800) and the schema-vs-contract test green.
- [x] T075 Pipeline unchanged: the pipeline recordings and tests pass untouched (R13). HANDOFF.md.

## P7 re-check (orchestrator runs live; Sonnet scores; W5)
- [ ] T080 Live: fresh talker, fighter, explorer personas on dm-tools (Haiku engine, Sonnet player), `VIII9_GUARD=log`.
- [ ] T081 Score: h2h (032's C1-C10 columns), foe-act mix (picked, lapsed, waited; strike share while engaged; waits
  and yields while unhurt), refusals per turn by field, missing picks, told lines dropped.
- [ ] T082 `turn_judge` over the three saves; the orchestrator or owner fills 20 hand verdicts per measure.
- [ ] T083 Guard hits from the live JSONL (must be 0).
- [ ] T084 `implementation-results-P7.md`, verdict and gate table first, against SC5.

## P8 fixes from live check 1 (Sonnet; lane `engine/dm/dm_tools.py`, `dm.md`, `engine/llm/offline.py`, tests) [owner ruling 2026-10-11]
- [x] T090 `propose_roll` `starts_fight` / `fight_to`: a Strike, Grapple or Force at an able npc/adversary starts the fight through `_fight` before the reach check; a live fight with the target in it ignores both; defaults `not_chosen:fight.starts`, `not_chosen:fight.to`.
- [x] T091 Reach: an unrecorded band takes the weapon's first band (`not_chosen:position`); a recorded band out of reach is refused with one exact `change kind=position` call.
- [x] T092 `_position` refuses who==what, a `what` that is not pc or an entity id, and a `to` that is neither a band nor a place id, each with one example; plain schema descriptions.
- [x] T093 `new_npc` `name` = the short name; `not_chosen:name`; result ends "Use <id> for them from now on."
- [x] T094 dm.md (at most 800 words), offline `_dm`, tests (`test_spec033_p8.py`), dmtools replay re-recorded, `reached.txt` regenerated.

## P9 fixes from the no-foe-turns trace (Sonnet; lane `engine/dm/dm_tools.py`, `dispute.py`, `store/db.py`, `evals/h2h_score.py`, tests)
- [x] T095 Fight start after the gate: `_roll` pre-reads `check_gate` (no writes); only G1/G2/accepted-fallback starts the fight and checks reach; a refused strike writes no fight, band or default.
- [x] T096 Take-back reverts the time mode: `_rewind` and `Transaction._revert` accept a pure mode switch (`db.is_mode_switch`: time_advanced with a mode and no time moved).
- [x] T097 `h2h_score`: exchange = a turn in a live fight with a resolved roll (or a `round` mark); reverted fight starts are not fights; "(fights ended by the PC's blow)" in the C8 row.
- [x] T098 Item 4 traced, not fixed (see HANDOFF-P9.md).

## P11 fixes from live check 3 (Sonnet; lane `costs.py`, `change.py`, `world_step._foe_turn`, `foe_act.py`, tests)
- [x] T110 `cost.time` in conflict mode with no listening clock: the time row lookup refuses (`CostRefused`, existing fallback) instead of crashing; `listening_clock` is an established stakes source only when an active clock lists `cost.time` or `cost.exposure`.
- [x] T111 `take` / `give` of a thing the DM named only in words make the item from the DM words (`change._made`); no "Not applied".
- [x] T112 Every foe act shows one RESULT line in words (miss, hold, move); `foe_act.act` returns `FoeDone(said, harm, pick, roll)`; the roll shows only via `world_step.SHOW_FOE_ROLL` (off).
