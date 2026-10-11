# Trace: no foe turns, and a second conflict_start (save 20261011-065929-fighter-dm-tools)
Read-only trace. Facts from the save (turns/events/model_calls), code at a6538a7.

## Symptom 2 first (it changes the picture): event 473 is NOT a restart inside a live fight
- Turn.2: strike #1 (call.turn.2.dm.0.0, `approach: "weapon techniques"`, starts_fight yes, fight_to close) -> `_attack_starts_fight` (dm_tools.py:734, 796) ->
  `_fight` (1335) -> `conflict.start`: events 441-444 (bands, Vitality 5, meta conflict), 451 (mode conflict), 453 `conflict_start`. THEN the license gate refused the strike
  (rulings 461-462). Tool output was "A fight begins ... NOT POSSIBLE AS PROPOSED (refused): no held license covers it (weapon techniques ...)". The DM retried with
  `approach: "plain"` (dm.1.0): paused offer, pause 463. The retry hit the live-fight early return (dm_tools.py:809-811): no event, no default logged. Turn.4 and turn.5 show the same retry.
- Turn.3 is the player's `/fix` (take_back, dispute.py `_take_back`->`_rewind` 195-212): event 464 `writes_reverted` [439,441,442,443,444,451]. That reverts the
  conflict meta (444), Vitality (443), bands (441,442) and mode.loaded (451). **The fight was undone at 464; "live from 453 to 499" is wrong.**
- Turn.4: the player redeclared; the DM called propose_roll; `_fight` started a fresh fight: 469-473 (same ids, Vitality 5 again, `previous:"free"`). Legit new start after a take-back.
- Turn.5 (second `/fix`, a re-offer, no revert) is the real "attack in a live fight" case: propose_roll with starts_fight yes/close, no new conflict event, no `not_chosen:fight.*`. The P8 guard held.
- Side defect (code bug): `_rewind` reverts only REVERTIBLE types when `take_back` is false (from_seq 433 > scene.started_seq); `time_advanced` (445, mode "conflict") stays
  (db.py:87-95). So after 464 `state.time.mode` is still "conflict" while `meta.conflict` is gone. Evidence: turn.4's first refused strike has NO "A fight begins" note, because
  `live = conflict.active(st)` (dm_tools.py:821, = mode test, conflict.py:31) was true; and `previous` became "free" (conflict.py:100: mode already conflict -> "free"), not "site".
  Effect here: the fight ended into mode `free` (509) and `site` came back only at 532. Class: code bug (take-back leaves time mode), minor here.
- Fight began on an action the gate then refused: `_attack_starts_fight` runs before `run_beats` (734 vs 763). Class: design gap. It was harmless only because the DM retried.
  The refusal text said nothing about the fight except the prefix note. The player saw "[REDIRECT] Not as tried" (transcript l.360, 412) above the offer; that is what both `/fix` calls were about.

## Symptom 1: why `foe_calls` is 0 on every turn
Gate order for a foe call: `_run` -> `_world` (dm_tools.py:335-347: skip if `t.world_done` or open pause) -> `world_step` (dm_world.py:38: skip if open pause; 42 `spent`) -> `_foes` (112: needs `conflict(st)`; 114 able foes; 120 counts the call).
| turn | path | result |
| 2,4,5 | propose_roll -> `t.paused`; `_run` line 152 `_world` | open pause -> `_world` returns [] at 339. No world step. |
| 3 | `/fix` (fixer calls only, `screen.dm_tools` = {fix:true}) | not a game turn; no DM, no world step |
| 6 | answer `go_big` -> `_resume` opens a second offer (event 491) | pause open -> line 139-140 `_world` returns [] at 339; steps 0 |
| 7 | answer `commit` -> `_resume` rolls: harm 8 vs Vitality 5 (495), dead (496-497) | pipeline.py:912 `check_end` -> `conflict_end` 499 inside `_resume`; then `_world` (140) -> `_foes` 112: `conflict(st)` is {} -> returns {}. |
- Cause: one settled exchange in the whole fight, and the PC's blow killed the only foe (S4 harm 8, foe Vitality 5), so no foe was left to act. Every other turn was a pause, a menu answer or a `/fix`.
  This is D2 working as ruled (foes act after the PC's result, not after a dead foe). Class: no bug in the foe gate; model/roll outcome plus an overcounting metric.
- Metric overcount: `h2h_score.py:49-68`: "exchange" = every turn between `conflict_start` and `conflict_end`; the save has no `round` boundaries, so the fallback counts all of turns 2-7 (6). Real settled exchanges: 1.
  "2 fights" = two `conflict_start` markers, one of them reverted. So "0 foe turns in 6 exchanges" reads as a gate failure but is 0 of 1.
- Not proven by this save: that the foe call works when the PC's roll fails (this fight never reached it). `test_a_second_and_third_attack_across_turns_leave_the_fight_alone` forces `failure` and pushes a foe response, so it does reach `_foes` on a miss.

## P8 tests (tests/engine/test_spec033_p8.py): why they miss it
- Live-fight tests (130-195) call `_attack_starts_fight` directly or force `roll_check` to "failure"; none has the roll kill the foe, so none covers "fight ends in the PC's roll, no foe call".
- None runs a take-back/`/fix` over a fight start, so none sees time mode stay "conflict" with no meta (live check uses `conflict.active`, the mode test).
- None covers a refused first strike after a fight start, then a retry (the refused-then-paused pair).

## Fix candidates (after the cause; not done)
1. Symptom 1: no engine change. Fix the score: count an exchange only when a roll resolved in a fight (`beats` with status resolved, or the `round` marks), and report "ended by the PC's blow". Add a test where the PC's roll kills the lone foe: expect `foe_calls == 0`, `conflict_end`, mode back.
2. Take-back: when `_rewind` reverts the `conflict` meta (or any `mode.loaded`), also restore `time.mode` (revert the mode's `time_advanced`, or have `conflict.active` read `meta.conflict` plus mode). Test: fight start -> take_back -> `conflict.active` False, `previous` right.
3. Fight-before-gate: start the fight after the gate passes (the roll is offered/resolved), or leave it and accept it (the DM can retry). Owner call; if kept, add the retry test.
4. The stale "[REDIRECT] Not as tried" above an offer (both `/fix` complaints): separate trace; the first-call refusal still writes rulings 461-462 that reach the player after the DM retries.
