# Implementation results 032 / P2: Role.DM and the engine stored in the save

Lanes R + G. Branch `worktree-agent-ac8191e55446db9fc` (from `worktree-agent-afa629b34a41df390`, 8b238eb).

## Done
- `Role.DM = "dm"` (`engine/llm/base.py`); `DM_ROLE = Role.DM`; the prompt moved to `engine/dm/roles/prompts/dm.md`
  (budget 800 words); `GameConfig.models` gets a `dm` slot automatically (`ROLE_IDS`); Gemini output cap 1500.
- Schema: `dm_tools.schema_for(verbs, kinds, final)` is the one builder; `step_schema(ctx, final)` calls it and
  `schemas.BUILDERS[Role.DM]` calls it with `sorted(ctx.verbs)` (same order as `rules.ids`; a test asserts the two
  schemas are equal). `defaults(Role.DM)` is the empty step. `NUMERIC_ALLOWED` gained `amount` (the coin change).
- Offline heuristic `_dm` (`engine/llm/offline.py`): one `propose_roll` for a strike/grapple/force act aimed at the
  first person listed, only on a fresh turn with a call left; otherwise a talk passage ending "What do you do?".
- `Game.open` and `Game._redrive` use `saved_engine(config, stored)`: the save's `engine`/`dm_secrets` win, a missing
  key is `pipeline`/`hidden`. `play new --engine {pipeline,dm-tools}` (new games only).
- Harness: `evals/longhorizon.py` reads `narrator` or `dm` packets; `evals/playtest.py` adds `dm_per_turn`.
  `tests/e2e/driver.py` reads no role (nothing to change). New recording `tests/replay/games/offline_seed11_dmtools.json`
  (recipe in `tests/replay/record_games.py`); the pipeline recording `offline_seed11.json` is untouched and replays.

## Cases
S1-S9 (3x3 matrix, plus the secrets arm 3x2), S10 (open OFFER resumes into dm-tools; the answer's calls are all `dm`),
S11 (`Game.replay` after reopens, identical), S12 (reopened with a default and a pipeline caller, stays dm-tools): all in
`tests/engine/test_spec032_engine.py` (29 tests). Deviation: the real fighter save is not in the repo, so S12 uses a
scripted dm-tools save. The "default flips" trap is tested directly on `saved_engine` with a dm-tools-default config.

## Gates
See HANDOFF.md for the numbers (pytest, ruff, pyright).

## Not done / for later phases
- `/fix` on dm-tools (P6): `Game._answer` still sends a dispute answer to the pipeline's `play_answer`.
- Re-recording `offline_seed11.json` would only change its `created.config` (the new `dm` model slot); not needed.
- Pre-existing, untouched: ruff E741/I001 in `evals/orchestration/`, `evals/precision_audit.py`; pyright errors in
  `evals/playtest.py` (78, 315) and, without `--pythonpath`, unresolved `pydantic`.
