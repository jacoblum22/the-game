# Autonomous improvement loop (owner, 2026-10-14)

The owner's brief: 3 games in parallel with different classes and races, 60 rounds each, then find what went wrong
with numbers, two ideas per weakness, build and A/B test each like before (replays), keep only what improves things
with no side effects (or with a fix for the side effect), then 60 more rounds of the same games, the same loop, and
60 more: 180 rounds per game. Then a report: what was found, what was fixed, the metrics, what's still wrong.

## Setup
- Branch `autoloop`, worktree `.claude/worktrees/autoloop`, cut from main at 624e3a8. Not pushed. The owner's server
  (port 8765) runs from the nostalgic-dewdney worktree on main and is untouched.
- Games: `py -3.12 evals/autoloop/run.py <cleric|barbarian|bard> <rounds>` from the worktree, PYTHONPATH = worktree.
  Character made by the DM with a Sonnet player (brief in run.py), then rounds; a second run continues the same save
  and the same player conversation. Saves and meta (turn times, player session) in evals/autoloop/games/ (ignored).
- Players: cleric careful and kind; barbarian bold, fights; bard curious trickster, tests rules edges.
- A/B replays: scratchpad replay.py / probe.py, ported here as needed; 2 DMs at a time (the machine ran out of memory
  with 12). Fix wording must not be tailored to the test case (memory: no-test-tailored-fixes).
- A round = one player line and the DM's reply. Creation and the opening don't count.

## Rounds 1-60
(in progress)
