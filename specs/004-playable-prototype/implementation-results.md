# Implementation results: Milestone 1 (overnight build, 2026-10-07)

Branch `claude/project-thread-q2smmv`, main merged in, no PR. No money was spent: every model call was
made with the free offline stand-in or with scripted test models. Nothing has been sent to Gemini yet.

## How to play

See the top of [quickstart.md](quickstart.md). In short:

1. Put `GEMINI_API_KEY=...` in `.env` at the repo root.
2. Run `python evals/gemini_smoke.py` once. It checks the key and each role's request (about 1–2 cents).
3. Start a game with `python -m play new "My World"`, and pick it up again later with
   `python -m play continue`.

Add `--offline` to play free with template prose.

## What works

- **The whole arc:**
  - the fourteen world-seed questions (12.16.2), answered with a number, your own words, or skip
  - character creation, quick start or full (PR-02-7), with a birth draw
  - the opening scene
  - open-ended play across scenes and places
  - harm, Down, death, retirement, the epilogue and a new character in the same world
- **The turn loop PR-12-1, T1–T12:**
  - Reader classifies the message.
  - Gate and necessity decide whether a roll happens.
  - The Oracle answers fact questions.
  - Framer and `frame_check` build the frame.
  - OFFER pause, then the roll, near miss and last chance, then costs.
  - World reactions, Director cuts, Narrator, then the claim check (14 classes, 8 verdicts, at most 2
    redrafts, then the plain fallback).
  - The safety screen runs separately.
- **Exact resume at every pause.** `/quit` is always safe. `continue` re-presents the open seed step,
  creation block, offer, near miss, last chance, redirect or ending, with a recap.
- **Replay.** Every model call is recorded. `python -m play replay <name>` rebuilds the game and checks
  that it comes out identical.
- **Codex commands:** `/sheet`, `/journal`, `/turn`, `/spend`, `/branch`, `/budget`, `/autocommit`,
  `/fix`.
- **Gemini adapter:**
  - Converts each schema to the subset Gemini accepts.
  - Caps output per role, counting thinking tokens.
  - Retries on truncation and on transient errors.
  - Falls back to a simpler schema if Gemini rejects one.
  - All of this is tested against the real SDK with a mocked transport.

## What is coarse in Milestone 1 (by design; later milestones build it)

- Fights, travel, items, growth, the living world and companions all go through the one action pipeline.
  Milestones 2 to 7 (tasks T083–T102) build them properly.
- 34 of 105 boundary handlers are live. The rest log `handler_skipped`, noting the milestone that builds
  them.
- Coverage is in [coverage-m1.md](coverage-m1.md): 306 ids implemented and 10 coarse. 342 ids in
  Milestone 1 chapters are not yet tagged anywhere and have not been triaged.

## Test numbers (offline)

- **Full suite:** 915 passed, 2 skipped (93 s), covering engine, golden, contract, seeded errors, e2e
  and replay. ruff and pyright are clean.
- **60-turn e2e game (default run):** 5.4 s to play, 4.7 s to replay, and the replay is identical.
- **500-turn e2e game (`--runslow`):** 43.8 s to play, 36.9 s to replay, 8657 events across 7 places.
  - Pauses reached: offer 193, redirect 19, near miss 15, retire 1, ending 1.
  - Each one was resumed after a close and reopen.
  - A scripted lethal path covers the warning, last chance, death, the epilogue and a new character.
- **Packet size over 500 turns:** flat for every role except the Director, which grows 12%. That is under
  the 25% test limit, but worth watching.
- **Recorded game:** `tests/replay/games/offline_seed11.json` replays identically. If a packet section
  changes, the test names it.
- **Speed:** a new game reaches its first prompt in about 0.7 s. A median offline turn takes 0.06 s.
  Live Gemini latency is unknown.

## Known issues

- **Untested live.** Gemini has never been called. Still unknown:
  - whether it accepts the converted schemas (fallbacks exist if not)
  - whether 3k thinking tokens is enough headroom
  - real cost per turn
  - how often safety blocks fire on violent prose
- **Offline prose is template text.** Use it to check the engine, not to judge the game:
  - Its NPC reactions are generic.
  - It cannot target "the nearest person".
  - Singing gets a stock reply.
- **Recap thread lines** can be cut off mid-sentence.
- **Journal wording** is clunky.
- **The turns table** stores `delivered_verbatim` before the player-text cleaning, so it can differ
  slightly from what was shown. A `/fix` quote of cleaned text may then miss.
- **Repeated NPC actions** are reworded rather than avoided. `tbl.npc_action` opts out of table
  recency, and changing that would be a rules change.
- **`.env.example`'s `GAME_DM_MODEL` is ignored.** The model comes from `GameConfig`.
- **Not done, owner-run and paid:** T078 (persona harness) and T079 (Gemini checker recall run).
- **Tooling branch `claude/project-thread-9ivqgo` is unmerged.** Merging it changes `.claude/` settings
  and hooks, so it was left for you to decide.
