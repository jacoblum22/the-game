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
Characters (all chose the acolyte background): Brunhilde Stonehearth, hill dwarf Life cleric (companion Garrick
Thorne, human ranger, joined ~R47); Grukka Ironhide, half-orc barbarian; Vesper Thorne, tiefling Lore bard. Cleric and
bard reached level 2. The conversation was cut (summarised) once, at R58 (cleric) and R57 (barbarian).

### Metrics (metrics.py, fmt.py; per game cleric / barbarian / bard, 60 rounds each)
- Lost replies (stubs re-asked) 0/0/0; text hidden after a late call 0/0/0; refused tool calls 2/5/3.
- Bold 0/17/0 (all HP or status numbers); bullets 1/3/0; headings 0.
- Menu of choices ending the reply (regex) 10/3/2; sheet numbers in the last paragraph 15/37/3.
- Notebook reads (lore/recall): 0/0/0 in 180 rounds. Rules lookups 11/25/12. Median turn 12-15 s, max ~65 s.
- Two rounds showed a stray note above the reply ("Miss. Next.", "Both hit (15 meets AC 15).").

### Read by three Sonnet agents (READ.md), checked by hand on samples
150 findings: format 45, contradiction 37, agency 19, rules 15, clock 10, pacing 7, npc 6, bookkeeping 6, other 4,
thread 2. Spot-checked contradictions all held (six watchmen vs "the watch's twenty"; the Deepwatch keeps copies of
every hold's ledgers vs the Naming "lost with the holds"; the toll-house "a mile out" vs "a few hours away").
Nearly all contradictions came before the conversation was cut: the facts were in the DM's context.

### Weaknesses
1. Contradictions with what was established (37, about 1 in 5 rounds; worse late in a long arc): where people were,
   who knows what, distances and travel times, counts, who did what in the past. The notebook is never read.
2. Agency (19): the DM writes the PC's words in big moments, gives them memories, feelings and dreams, or takes an
   action (handing over a weapon) the player didn't take.
3. Out-of-game talk (45 format): menus at the end, rules explanations, sheet read-outs, bold numbers (barbarian).
4. Rules (15) and clock (10): mixed; a second long rest within 24 hours (cleric R51, after refusing it twice); an
   ally attacking with no initiative or turn; time jumps not in the story.
5. Code bugs found: conditions matched by case ("Unconscious" never removed); a use-only call (Dodge, Ready) refused
   as "nothing to change"; a note before tool calls shown above the reply.

### Fixed in code (tests pass, 271)
- Conditions matched whatever their case (8693350). Use-only call marks the action (70d2604). A short note before
  tool calls isn't shown (3fdf39a). One long rest in 24 hours, checked by the clock (da0ddf2, aa4f08b).

### Prompt ideas, A/B by replay (10 rounds x 4 runs per arm; rounds with a block-1 contradiction or agency problem)
Rounds: bard 27, 35, 40, 45; barbarian 32, 46; cleric 43, 53, 56, 59.
- 1A contradictions: the existing check line names what to check (where people and things are, who knows what,
  distances and travel times, numbers, names, the order of past events).
- 1B contradictions: if the reply says something about a person, place or event from more than a few turns ago,
  `recall` it first and check its notebook entries.
- 2A out-of-game: "End each reply with the situation clear..." gains "told as the story: don't list their choices or
  read out the sheet's numbers".
- 2B out-of-game: that sentence removed.
- 3A agency: "says, thinks and does" becomes "says, thinks, feels, remembers and does".
- 3B agency: "When the player says what their character does, narrate how it turns out; don't add words, deeds or
  feelings of the character's own that the player didn't give."
Caveat: block 1 has no snapshots, so a replay's sheet and fight tracker are the end of the game's (a later level, a
fight not yet begun). In some runs the DM stops to sort that out (bullets, "nothing to change" refusals). The artifact
is the same in every arm, so arms can be compared, but absolute format counts from these replays mean little; kept
ideas are measured again in block 2's play. Cleric R59 couldn't be replayed (first message after the cut): 9 rounds,
36 replies per arm.

Results (blind, judged by three Sonnet agents; ab1/; score.py ab1/blind, fmt.py ab1/replays), replies of 36:

| arm | contradiction | repeats the original | acts for the PC | menu at end |
|---|---|---|---|---|
| base | 7 | 3 | 9 | 4 |
| 1A | 4 | 0 | 12 | 4 |
| 1B | 2 | 1 | 9 | 5 |
| 2A | 8 | 1 | 13 | 0 |
| 2B | 8 | 1 | 8 | 5 |
| 3A | 5 | 0 | 11 | 2 |
| 3B | 10 | 5 | 15 | 2 |

Preliminary, not yet decided: the counts are small. 1B is the best lead for contradictions (2 vs 7); 2A removes
menus (0 vs 4) but needs a check that it costs nothing elsewhere; 3B made acting for the PC worse (15 vs 9) and is
dropped; 3A did nothing measurable. Most acting-for-the-PC comes from two cleric rounds (R53: 4 of 4 in every arm).
Next: confirm 1B and 2A with more runs, then block 2.

## Continuing on another machine
- Game saves, meta and the readers' files are in games/ (no longer ignored); save paths are resolved inside games/.
- Continuing a game (run.py) and replaying (replay.py) also need the Claude Code conversations, which live outside the
  repo: the DM's in ~/.claude/projects/<DM_HOME mangled>/ and the player's in ~/.claude/projects/<games dir mangled>/
  (session ids: the save's session_id and meta's player_session; pre-cut DM sessions c12bf076 cleric, b19f0b2a
  barbarian). Not committed. What a game does without them hasn't been checked.
- The save's `cwd` (DM_HOME) is stored as ~/AppData/Local/the-game-dm and expanded on load, so it carries over as is.
- 2026-10-16: took Windows usernames out of the repo (Jake's request, before it might go public). Meta `save` is
  now just the file name, save `cwd` is ~/..., replay.py derives the DM's projects folder from DM_HOME, and
  synthetic/BRIEF.md no longer names local paths. No DM behaviour change. Tests: 271 passed.
