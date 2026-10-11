# HANDOFF 032 (P1-P4, P5a, P5b, P6 done on branch spec032-base)
Owner rulings, 2026-10-10 (they override the spec docs; tagged `[owner ruling 2026-10-10]`):
- **Scene ends are the DM's call** (the `end_scene` tool; code only does the bookkeeping; travel and time jumps still open a scene).
- **Moods are decided by the DM** (the `mood` tool records them as memory; no roll and no ceiling grid).
- **Pushover is observed, not gated.** Principle: fix only what is seen in play.
Done earlier: P3 (`_party`, `change fight`, one revision then drop), P4 (`dm_world.py` world step, `end_scene`, FIGHT block), P5a (footing hold needs a holder; `pc` resolves to the PC; G4 refusals name the condition), P6 (`/fix` on dm-tools turns; live 8/9 understood).
Done P5b (`dm_tools.py`; tests `test_spec032_p5b.py` 50 cases; xfail groups J, Q, L, E5, I12 removed):
- **said:** required `said:[{npc,words}]` (cap 6, `[]` when no one spoke; the contract test needs required == properties, so scripted DM dicts need `"said": []`) in the DM schema -> `_told` -> `testimony.add_said` (about=[speaker], question unset). Dropped and logged in `told_dropped`: dead/absent/unknown speaker, words not in the passage (cover 0.8), repeat, a delivered clue. The PC's own words skip silently.
- **context:** per-person `carries:`, `state:` (non-fresh), `Not here:` (met = any scene card's cast; elsewhere/dead/gone), a PC `hurt:` line (staggered says the next blow wounds).
- **log-only** (`screen.dm_tools.log_only`, also `TurnRecord.claim_log`): `pronoun` (via `_pronoun_hit`), `absent_named`, `item_unbacked`. 0 hits on 72 real passages (`evals/baselines/log_only_032.md`), so precision is unmeasured; do not promote.
- **leak audit** drops every entity name token. TurnRecord now fills `said`, `claim_log`, `draft_versions`.
- `dm.md` and the schema changed: only `offline_seed11_dmtools` was re-recorded (offline `_dm` now quotes a line and lists it).
Left: P5.5 live (talker + explorer 15 turns on Haiku: told rows, log-only counts, tokens/turn vs P4); P7.
Traces: (1) staggered PC with no warning: `dm_tools._run` never calls `narration.owed`, so the `[STATUS]` exits card (07.3.7) the pipeline adds at narration.py:888 is never shown; fix is 3 lines in `_run`, left unfixed (outside lane C). (2) hall register: see the report (a POINTER clue + the DM's own earlier lines in RECENT CONVERSATION).
Traps:
1. Name-token removal leaves 7 of 8 incident kinds' core secrets (only a name) un-auditable (L3); a name-only secret needs a different check.
2. A harm-dead NPC stays in `People here` (exists still "exists"); the `state: dead` line is the only sign.
3. The world step runs once per exchange (`t.world_done`); a re-ask rebuilds `situation()` and replaces `said_raw`.
4. `_log_only` swallows its own exceptions (`check_failed`); keep it returning nothing.
5. Stats keys: `moods`, `scene_ends`, `world`, `said`, `told_dropped`, `log_only`. P6 imports `Turn`, `_env`, `_dm_loop`, `Outcome`, `HARM_OWNED`, `ENGINE`, `play_turn`, `enabled`.
6. Working-copy files are CRLF; scripted edits go through the Edit tool or a Python rewrite with `newline=""`; `pytest -q -q` hides the summary line.
7. `dm.md` or schema change means re-recording ONLY `offline_seed11_dmtools`.
