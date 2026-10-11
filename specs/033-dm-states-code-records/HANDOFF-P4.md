# HANDOFF 033 P4 (people and testimony) - FINAL
DONE: T030-T034 ticked (T032's Strike/Grapple/Force reach refusal is NOT done: it lives in `_propose_roll`, P2a's lane).
Engine: `_party(…, as_=)` (exact id / `"pc"` / exact case-folded name that one non-sealed entity bears, else a walk-on by `as`; no `as` in a
person slot = they, logged `not_chosen:as`), `_walk_on(ctx, words, place, as_, name)` (never reuses; role = the DM's words as given),
`target_kinds`/`target_is_person` from `basic_verbs.yaml`, `_change` new_npc (`name`/`as`/`knows`), new_item `knows`, npc_leaves no `to` ->
`OFF_SCENE` (logged), `_fight` to/recorded band/near, `_knows` -> `gen/case.place_on`, `_told(ctx, t)` spine-only (a line is kept as given;
only an unknown/dead/gone/absent speaker goes to `told_dropped`), `_audit`/`_log_only`/`_name_tokens` etc. and stats `leaks`/`log_only` gone.
FOR P3: foes made in a fight/roll need `"as": "creature"` (else a person walk-on); a creature is re-found only by id or exact recorded name
(`the pale beast` -> `npc.the_pale_beast`). `fight` without `to` is accepted (near, logged), not refused.
FOR P5: `said` entries may carry `as`; `mood`/`reveal_clue`/`travel who` have NO `as` in the schema (P1): unknown words there = a they walk-on, logged.
Tests: new `tests/engine/test_spec033_p4.py` (37: C8 as x entry points, exact/partial/ambiguous/sealed names, `pc`, `you`, `name=`, same words once per
turn, never reuses, `knows` end to end for person and item, bad node told; C9 kept/dropped/walk-on). Rewrote `test_spec032_p8a.py` (p4 -> `as`; p8 ANIMAL
head-noun test deleted; passage-check asserts inverted; `_told` signature). Fixed p3 BEAST id and p4 f11/f13_f18/f16_f21 (`as: creature`).
GATES: full pytest 2516 passed, 5 skipped, 2 xfailed, 1 failed = `tests/guard/test_viii9_static` only because the COMMITTED `reached.txt` is stale;
with a locally regenerated one `tests/guard` = 75 passed, 1 skipped (reverted, not committed: orchestrator runs `py -3.12 -m tests.guard.census reached`).
ruff clean on touched files (repo-wide has old errors in evals/); pyright clean on touched engine files (old errors in test_spec032_p3 lines 196-383).
`offline_seed11_dmtools` replay passes: NOT re-recorded.
TRAPS: files CRLF (python edits need newline=''); python is `py -3.12`, PYTHONUTF8=1; a made-up id-shaped word (npc.hal) in a person slot or with `as`
becomes a walk-on with a rolled role, aliased in `t.aliases` for that turn only; next turn it is a NEW person unless the DM uses the returned id.
Touched `_propose_roll` minimally (passes `as_=c.get("as")` to `_party`; `change_what` fallback = DM's words): the P2a merge may conflict there.
