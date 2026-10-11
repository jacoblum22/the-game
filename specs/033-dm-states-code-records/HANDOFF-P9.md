# HANDOFF 033 P9 (fixes from trace-no-foe-turns.md; base spec033-base)
Done (tests `tests/engine/test_spec033_p9.py` 4, `tests/evals/test_h2h_exchanges.py` 1; p8 tests unchanged and green):
1. Fight start after the gate: `_roll` (dm_tools.py) builds the beat first, reads `check_gate` (pure: no mint, no events), and only
   G1/G2 or an accepted fallback runs `_attack_starts_fight` then `_reach`. Refused/redirect => no fight, no band, no default;
   `run_beats` then gives the refusal. Order: gate -> fight -> reach -> offer. The beat id is minted after (no id burned on a refusal).
2. Take-back restores the time mode: `db.is_mode_switch` (time_advanced with a mode, to == from) is accepted by `Transaction._revert`
   and picked by `dispute._rewind` (the one place every take-back/rewind goes through). Boundary marks (`conflict_start`) are not reverted.
3. `evals/h2h_score.py`: fights = conflict_starts not reverted (its same-turn `conflict` meta_set or the mark in a writes_reverted);
   exchange = a turn in a live fight with a non-voided `frame_resolved` (or a `round` mark when the save has any); C8 row now
   "fights / exchanges / foe turns (fights ended by the PC's blow)". The fighter save 065929 reads 1 / 1 / 0 (1).
4. Item 4 traced, NOT fixed: `_roll` does `_take(t.rec, res, t.oof)` per call, so a refused call's REDIRECT item stays in `t.oof` for the
   whole turn; `turn_blocks` (narration.py:741) renders every item, and an `offer` pause pops only OFFER/WARNING (`_PAUSE_ITEM`), not REDIRECT.
   A later accepted call never removes it (and `rec.beats` keeps the refused entry). The fix needs "this call retries that one": same
   verb+target is a judgement about the story, not one small obvious change, so it is left for the owner (or a DM tool field `retry`).
Traps: a G3 with a crude fallback (redirect pause "Try it anyway") now starts NO fight at the first call, and `_resume` of
"accept" does not start one either (the blow lands with no fight, like starts_fight=no). Decide whether `_resume` should call
`_attack_starts_fight`. No new top-level function is reached in a dm-tools turn (reached.txt unchanged, census not re-run).
Gates: see final message (full pytest, ruff clean; pyright clean except the unresolved `pytest` import, same as p8 tests).
