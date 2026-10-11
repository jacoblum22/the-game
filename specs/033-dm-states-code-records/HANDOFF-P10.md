# HANDOFF-P10 (item 28 closed, plus two of a name)
- Done 1: `dm_tools._accepted_attack` runs before `_resume` in `_run`. For an accepted redirect (`accept:...`) it calls
  `_attack_starts_fight` then `_reach` on the FALLBACK's verb, with `starts_fight`/`fight_to` read from the new
  `Stated.starts_fight/fight_to` (set in `_stated`). Blank/yes starts once, no starts none, a foe already in the fight resets nothing.
- Done 2: `propose_roll.retry_of` (schema, dm.md 795 words, offline `_dm` fills ""). `Turn.refused` maps tag -> the REDIRECT
  items a refused call wrote; the NOT POSSIBLE result ends `(refused call rN)`. An accepted call naming rN drops those
  items from `t.oof`; blank or unknown tag removes nothing and logs nothing.
- Done 3 (coordinator add-on): `_party` raises `Ambiguous` when an exact case-folded name has 2+ unsealed bearers; `tool()`
  turns it into `REFUSED: Two on record are called 'x': id (band, state), ... Use the id.` Nothing written (a walk-on made by
  an earlier slot of the same call is not undone). `_told` drops and logs the line. `new_npc` on a borne name still creates and says
  "Another is already called 'x'; use <id> for this one."
- Tests: `tests/engine/test_spec033_p10.py` (8), `test_spec033_p4.py` (two-of-a-name rewritten, new_npc collision).
- Traps: a fallback accepted at a RECORDED band out of reach cannot be refused mid-resume: the reach text goes into the DM's
  lead and the roll still runs. Only NOT POSSIBLE refusals that wrote a REDIRECT get a tag (early `REFUSED:` strings write none).
  `Stated` grew two fields: saved redirect pauses made before P10 read as "" (a blank, so yes).
  `_id` is unchanged (still returns the raw words for 2 matches); only `_party` refuses, so a `what`/`to` slot read by `_id` alone is not checked.
- Gates: see the final message (full pytest, guard 74 passed, census reached regenerated if it finished).
