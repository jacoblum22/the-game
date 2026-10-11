# HANDOFF 032 (P1-P4 + P6 done, merged on branch spec032-base)
Owner rulings, 2026-10-10 (they override the spec docs; tagged `[owner ruling 2026-10-10]`):
- **Scene ends are the DM's call** (the `end_scene` tool; code only does the bookkeeping; travel and time jumps still open a scene).
- **Moods are decided by the DM** (the `mood` tool records them as memory; no roll and no ceiling grid).
- **Pushover is observed, not gated.** Principle: fix only what is seen in play.
Done:
- **P3:** the `_party` resolver for prose-only people and creatures; `change fight`; one revision then drop (`screen.dm_tools.dropped`); `fail_cost`; `Beat.title`; item echo.
- **P4:** `engine/dm/dm_world.py` (`world_step`: foe turn, time, omens, triggers, lead), `end_scene`, the FIGHT block (`_fight_block`), site-mode time (read `state.time.mode`, not `scene.mode`). Moods retired to DM memory.
- **P6:** dm-tools `/fix` via `dispute.play_dm_dispute`; a reframe re-runs `_dm_loop` with the Fixer's note (no clue, no world step); the Fixer sees `dm_log`, `cond_origins`, and `remove_fact cinst.N`.
Live (orchestrator, P3 and P4 code): fighter and talker runs, 0 crashes; time moves; about 20k tokens in and 2.4 calls per turn; no fight came up (the persona didn't attack).
Traced: a footing cost at S3+ makes a self-held `cond.pinned` (`costs.py:294-301`, source = the actor; old, Feature 004). Report: `research_notes/Playtest round 2 solutions/spec032-investigation/pinned-trace.md`.
Next, P5 (lane C, split into slices):
- **P5a:** the root fix in `costs.py` (a hold needs a real holder, the opponent; with none, use the row's non-hold form).
- **P5a also:** `_party` resolves "pc" to the PC (`change coin to="pc"` made an NPC "the pc").
- **P5a also:** the refusal text names the condition.
- **P5b:** the P5 tasks (`said` via `add_said`, carries, "Not here", log-only checks, leak audit tokens, empty dm turn records).
Not run yet: P6.4 (`evals/feedback_corpus.py --set dmtools --model sonnet`); the orchestrator runs it.
Traps:
1. The world step runs once per exchange (`t.world_done`); a re-ask rebuilds `situation()`.
2. `t.beats` must be extended wherever a tool resolves a beat.
3. Stats keys: `moods`, `scene_ends`, `world{foe_turns,facts,reasked}`.
4. A `dm.md` or schema change means re-recording ONLY `offline_seed11_dmtools`. The pipeline recording (which holds the Fixer schema and prompt) stays byte-equal.
5. P6 imports `Turn`, `_env`, `_dm_loop`, `Outcome`, `HARM_OWNED`, `ENGINE`, `play_turn` and `enabled` from `dm_tools`. Keep the names, and keep the `tools[]`/`dropped[]` shapes.
6. `dm_tools.py` is CRLF. Use the Edit tool or a script that keeps CRLF; never heredoc Python.
