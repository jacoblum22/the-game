# Implementation results, P4 (the world step; lane W)

Base `38b5993` (P3). New `engine/dm/dm_world.py`; edited `engine/dm/dm_tools.py`, `engine/dm/roles/prompts/dm.md`, `evals/h2h_score.py`,
`evals/playtest.py` (stat keys), tests, and the dm replay recording (`offline_seed11_dmtools`; the pipeline recording is byte-equal).

## P4.1 Trace: the scene mode (assumption A1)
- The pipeline's Director gives a place scene `ns.mode or previous scene's mode or "free"` (`roles/director.py:116`); its prompt says "default the
  previous scene's mode, unsure: free"; the offline Director says `free`. The opening scene is `free`. `clock.beat_cost("free")` = (0, interval),
  so in `free` talk costs no time; the pipeline moves its clock only through listed durations, rests, travel and a model-chosen `site`.
- dm-tools: `_open_scene` took `clock.mode_of(state.time.mode)` (store default `scene` reads as `free`) so the clock stayed at round 0 (the fighter
  save's "afternoon", hour 0). Replayed: fresh game `(round 0, time.mode free, scene.mode free)`; after the first plain turn on the old code, 0.
- Decision: dm-tools place scenes run in `site` (an exchange = 1 interval = 10 minutes, 00.7.3), a fight in `conflict` (1 round per exchange), travel
  and rest set their own modes and `site` is put back by the next scene. `dm_world.ensure_site` switches the opening scene's *time mode* to `site` at
  the start of each turn (the `scene.mode` record of that one scene stays `free`; the code reads `state.time.mode`, never the record); later scenes
  open in `site` (`_open_scene`). A1 holds. Check: 2 plain exchanges after the first turn = +200 rounds (T12); 20 offline scripted turns = 3.17 hours.

## What was built
- `world_step(ctx, t)` (`dm_world.py`), once per exchange, never with a pause open: `foes_act` (the pipeline's foe turn, harm by code, RESULT lines to
  the player as before), `release_holds`, time (`beat_time` in conflict = a round; else one `beat_cost` per resolved beat or per plain exchange;
  a refused/question/withdrawn-only turn spends nothing), `beat_end` once for an exchange with no beat, `note_turn` (dead air, bookkeeping only),
  `clock_omens` (after time, so the interval it crosses ticks the clock), `fired_triggers`, and `inject_lead` when `trg.lead_injection` is raised.
  Returns the facts in plain words ("The officer strikes you and lands it: you are bloodied.", "What that changed: Vitality 4 -> 1", "An omen: ...",
  "A lead arrives, in the form: ...", "interrupted: ...", a lethal warning). Time passing alone is not a fact (the `Now:` line shows it).
- Wiring in `_run`: on an answer turn the world step runs right after `_resume`/`_harm_followups`, before the DM loop, and its facts go in the
  `WHAT JUST HAPPENED` lead (zero extra calls). On a free turn it runs after the DM loop; if it produced a fact and no pause is open, ONE more
  DM call (`_reask`, no tools) writes the final passage. No fact = no extra call (F20).
- Stats: `screen.dm_tools.world = {foe_turns: [{foe, did}], facts: [...], reasked: n}`, `scene_ends: [...]`, `moods: [...]`.
- FIGHT block in `situation()` (after `Now:`): foes with `state_words` and band, the character's state, and the rule in one line.
- `end_scene` tool (`why`): refused with a fight on, a pause open or no scene; otherwise `_open_scene` (scene_end handlers, per-scene resets such as
  held moods and dead air, new scene record). No cut rule anywhere. Travel (`_travel`, `_sync_scene`) and a time jump (a rest / breather / day or
  week boundary since the scene began, `dm_world.time_jumped`) still open a scene in code; the DM is told of the jump.
- Moods [owner ruling 2026-10-10]: `mood` tool is now `{npc, mood: open|guarded|closed, why}` and writes the held band (`answer._hold`), a memory it
  may change; no roll, no `T-12-19` lookup (`ceiling`, `_cell_words`, `_GRANT_RANK` deleted; stats keys `ceilings`/`ceiling_violations` replaced by
  `moods`). `_asks` logs `{npc, mood held, cost, granted}` as an observation (never a gate, no `willingness()` call so it no longer rolls a mood).
  The situation says "mood toward you: not set (decide it, record it with `mood`)" until the DM records one.
- dm.md: `mood`/`end_scene` described, the world-step paragraph, and the G7 sentence verbatim from the plan.

## Gate numbers (offline; the live runs are for the orchestrator)
- tests/engine/test_spec032_p4.py: 24 tests (F1-F26 by state, T1-T12, C1-C7 as `end_scene` cases, moods, FIGHT block); the three P4 xfail groups
  (F, T, C) were removed from `GROUPS` (8 xfail rows remain: P5 x4, P2/S, P6, P7 and the S row).
- Offline scripted game (20 turns, seed 11): 1.25 DM calls per turn (5 re-asks on 5 lead/omen facts), 3.17 game hours.
- A made-up `change fight` turn = 3 DM calls (tool step, draft, re-ask), 1 foe turn, `conflict_start` once; the fighter turn-9 call replayed:
  OFFER (0 foe turns while open), answer turn: `conflict_start` once, the beast (`mind: animal`) acts once that exchange.

## Not done / for the orchestrator
- P4.5's 5 live Haiku samples of the turn-11 context (k/5 proposing the roll) and P4.6's live fighter + talker runs: no `claude` CLI in this
  worktree. Commands (from the repo root, with the CLI on PATH): `py -3.12 -m evals.playtest --engine claude --player claude --dm-engine dm-tools --quick-setup --turns 15 --persona fighter`
  (then `--persona talker`), then `py -3.12 evals/h2h_score.py <the two saves>`: foe turns per fight exchange (target 1.0), hours advanced, extra calls per turn, tokens in.
- Deviation: a DM's `change fight` turn lets the foe act in the same turn (the pipeline's row-1 path does too); `_fight`'s tool text says so.
