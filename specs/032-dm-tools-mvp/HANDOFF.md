# HANDOFF 032 (slice 2: P2 done; branch worktree-agent-ac8191e55446db9fc, from 8b238eb)
Done P2 (R+G): Role.DM ("dm"; prompt engine/dm/roles/prompts/dm.md; one schema builder `dm_tools.schema_for`, also
registered in schemas.BUILDERS; offline heuristic `_dm`: talk, or one propose_roll for strike/grapple/force at a person);
`saved_engine()` in game.py makes Game.open/_redrive take engine+dm_secrets from the save (missing = pipeline/hidden);
`play new --engine`; recording tests/replay/games/offline_seed11_dmtools.json; cases S1-S12 in
tests/engine/test_spec032_engine.py (29 tests). Details: implementation-results-P2.md.
Gates: pytest 2071 passed, 4 skipped (was 2032+4); ruff clean on touched files (5 old errors in evals/orchestration,
precision_audit untouched); pyright 0 errors on touched files (use --pythonpath <py3.12 exe> or pydantic is unresolved).
MERGE: P1 (lane E) runs in parallel on another branch. Merge both into one base before P3. My evals edits are tiny
(longhorizon.py role in (narrator, dm); playtest.py dm_per_turn; gemini_smoke.py Role.DM) so conflicts are unlikely.
Next: P3 (lane T): tools make the DM's words real; trace the REFUSEDs first. dm_tools.py is shared by P3-P5, in order.
Traps: (1) any new Role needs: prompt .md, WORD_BUDGET, BUILDERS+DEFAULTS, gemini OUTPUT_TOKENS, cards GUIDANCE,
offline ROLE_HEURISTICS, a gemini fixture json, contract MESSAGES, test_llm_offline SCHEMAS, gemini_smoke.
(2) A packet/prompt change to DM calls breaks only the dm recording: re-record with `python -m tests.replay.record_games`
(do NOT re-record offline_seed11.json; it only differs by the new `dm` model slot in its config). (3) Schema field named
`amount` is exempt from the INV-3 numeric check (NUMERIC_ALLOWED); any other number in the DM schema fails the contract.
(4) Game._answer still routes a dispute answer to the pipeline's play_answer (P6). (5) Edits via Python heredocs turn
`\n` into real newlines: use the Edit tool for any string with escapes.
