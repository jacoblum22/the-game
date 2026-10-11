# HANDOFF 033 P3 (foes and the answer turn) - FINAL
DONE: T040-T046 ticked (T042/T044 retired by D2/D3). Foe call `dm_world._foes` (DM picks each able foe's act from `foe_act.legal_acts`, T-06-16; code rolls it);
omitted/illegal pick -> `foe_act.default_act`, logged `not_chosen:foes.<id>`, no re-ask. `foe_turns` rows `{foe, did, act, picked_by}`, `stats.world.foe_calls`.
COST TO SHAPE (`_cost_block`) + `_footing` (apply_footing, logs `not_chosen:cost_form`). Reach refusal `_reach` in `_propose_roll` (skipped for change_kind move_to).
FOOTING ORDER FIXED: `_world` calls `_footing` before `world_step`; on an answer turn with a pending footing the lead's world step is skipped, so the DM loop picks
`cost_form`, then footing lands, then the foes act, then `_reask` (call order: DM answer with cost_form, foe call, final passage). Test `test_the_footing_lands_before_the_foe_acts`.
TESTS: `test_spec033_p3.py` 33 passed. Two former failures rewritten (pinned foe: state built with cond.pinned, FIGHT block lists `break_free, yield, wait`; push: callable pick reads the FIGHT block).
GATES: tests/engine 2185 passed; full pytest 2585 passed, 5 skipped, 2 xfailed (with the local reached.txt); guard 74 passed with a locally regenerated reached.txt (NOT committed; orchestrator regenerates). ruff clean (B023 fixed with default args).
pyright: only env noise (pydantic/pytest/yaml unresolved) on touched files; one real error fixed. `offline_seed11_dmtools.json` RE-RECORDED (extra foe call per fight exchange); `offline_seed11.json` byte-equal.
GUARD EDITS: `census.py` probe states `change position engaged` before the grapple (else 06.4.3 refuses it and hold code goes unreached); `viii9_allow.py`: + foe_act.legal_acts HOLDS, + frame._atom_true (_ATOM, re.findall), - conflict.foe_beat BANDS (no longer reached).
FOR P6: `tests/engine/conftest.py` still turns `_reach` off for 5 modules (NEEDS_NO_REACH_CHECK: test_spec032_p3, p4, p5a, p8a, p8b; ~25 tests propose melee with no recorded band). Give each an engaged band or a `change position` step, then delete the fixture.
TRAPS: the foe message shows the FIGHT block twice (SITUATION's plain one and the legal-acts one in the lead); read the last. The offline double replaces a schema-invalid pick (e.g. strike for a pinned foe), so picked_by is dm. Foe companions as targets have no band test. Reach: a None band is refused; reach weapons (spear at close) not yet allowed.
LIVE RUN: watch `not_chosen:foes.*` and `not_chosen:cost_form` counts (D3) and the strike share while engaged (D1/P7). One extra DM call per settled fight exchange (D2) plus the reask when the world produced facts.
P5 runs in `dm_world._lead/_witness`; P3 touched only `_foes` there and the header docstring.
