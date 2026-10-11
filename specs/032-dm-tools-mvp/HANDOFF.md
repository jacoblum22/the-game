# HANDOFF 032 (P1-P4 + P5a + P6 done, merged on branch spec032-base)
Owner rulings, 2026-10-10 (they override the spec docs; tagged `[owner ruling 2026-10-10]`):
- **Scene ends are the DM's call** (the `end_scene` tool; code only does the bookkeeping; travel and time jumps still open a scene).
- **Moods are decided by the DM** (the `mood` tool records them as memory; no roll and no ceiling grid).
- **Pushover is observed, not gated.** Principle: fix only what is seen in play.
Done:
- **P3:** the `_party` resolver for prose-only people and creatures; `change fight`; one revision then drop (`screen.dm_tools.dropped`); `fail_cost`; `Beat.title`; item echo.
- **P4:** `engine/dm/dm_world.py` (`world_step`: foe turn, time, omens, triggers, lead), `end_scene`, the FIGHT block (`_fight_block`), site-mode time (read `state.time.mode`, not `scene.mode`). Moods retired to DM memory.
- **P6:** dm-tools `/fix` via `dispute.play_dm_dispute`; a reframe re-runs `_dm_loop` with the Fixer's note (no clue, no world step); the Fixer sees `dm_log`, `cond_origins`, and `remove_fact cinst.N`.
Live (orchestrator, P3 and P4 code): fighter and talker runs, 0 crashes; time moves; about 20k tokens in and 2.4 calls per turn; no fight came up (the persona didn't attack).
Fixed (P5a, was: a footing cost at S3+ made a self-held `cond.pinned`): `costs.py` `cost.footing`: a hold (`exclusion_group: hold`: grabbed, restrained, pinned) is sourced to the opponent (`frame.defender or beat.target`, an npc or adversary); with none, the deferred non-hold forms are written (S4: "move to next lower/worse place"). The real save's turn.4 now pins the PC by the woman. Pipeline and dm-tools both go through `apply_cost`.
Fixed (P5a): `_party` maps pc / the pc / you / the player (any case) to the PC (no more NPC "the pc"). `gate.py` G4 reason is now "pinned (cinst.1) forbids verb.strike" (the player's REDIRECT already named the condition, via `oof._why`).
Gate (P5a): `test_resolve_costs.py` footing 70 cells + `test_spec032_p5a.py` 12, all green; ruff and pyright clean on touched files; full pytest exit 0 (about 2.5 h under machine load, not 3 min). No recording changed: the pipeline recording and `offline_seed11_dmtools` stay as they were.
Next, P5b (the rest of P5): `said` via `add_said`, `carries:`/`Not here:`, log-only checks, leak audit tokens, empty dm turn records.
P6.4 done (orchestrator): live /fix, Sonnet, 9 labelled: understood 8/9, outcome 8/9 (auto 7 right, 1 unclear, 1 wrong: dmo1, a "learn from" teacher) -> `evals/baselines/fixer_dmtools_032.json`.
Traps:
1. The world step runs once per exchange (`t.world_done`); a re-ask rebuilds `situation()`.
2. `t.beats` must be extended wherever a tool resolves a beat.
3. Stats keys: `moods`, `scene_ends`, `world{foe_turns,facts,reasked}`.
4. A `dm.md` or schema change means re-recording ONLY `offline_seed11_dmtools`. The pipeline recording (which holds the Fixer schema and prompt) stays byte-equal.
5. P6 imports `Turn`, `_env`, `_dm_loop`, `Outcome`, `HARM_OWNED`, `ENGINE`, `play_turn` and `enabled` from `dm_tools`. Keep the names, and keep the `tools[]`/`dropped[]` shapes.
6. Working-copy files are CRLF (autocrlf; the index is LF). The Edit tool writes LF, which git normalizes; never heredoc Python.
7. The DM cannot add a condition to the PC (`change condition_add` refuses); tests pin the PC with `apply_condition` in a transaction.
8. `pytest -q -q` hides the summary line: read the exit code.
