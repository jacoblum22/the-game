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

## Second set of games (2026-10-16, on K-2SO, unattended)
Jake's brief for this run (via the project's coordinator): confirm 1B and 2A with about 8 replays per arm, judged
blind; add a whole-story reader if the readers only see slices; then three new stories, blocks of 60 rounds to 180,
with the same analysis after each block and a detailed report in evals/autoloop/. Push to `autoloop` only, never main.

- The first set's DM conversations stayed on the old PC (no `~/.claude/projects/<DM_HOME>` folder here), so its games
  can neither go on nor be replayed: replay.py forks the DM's Claude Code session. So:
  - three new games, `cleric2` (human Life cleric, careful and kind), `barbarian2` (dragonborn barbarian, bold),
    `bard2` (half-elf Lore bard, trickster): new briefs in run.py, same classes and player styles, new races and
    characters. Started 2026-10-16, 60 rounds each, all three at once.
  - 1B and 2A are confirmed on the new games' block-1 rounds instead (a held-out set for both, since they were written
    against the first set), together with the block's own A/B tests.
- Readers: each of the three READ.md readers read one game's whole block (dump.py of rounds 1-60). From block 2 on a
  block is a slice of the story, so a fourth reader (READ_STORY.md) reads each game from the opening to its latest
  round for contradictions, lore, plot holes, characters out of character and dropped threads. facts.py gives it
  candidates: for each name in the notebook, or capitalised inside a sentence in two or more rounds (rules names left
  out), the sentences about it with a number, a distance, a time or a relation, by round. It judges nothing.
  On the first set's cleric (rounds 1-60): 24 names, 211 sentences (Father Dorrin 25, Garrick 21, the Deepwatch 18).
- dump.py's docstring said earlier rounds were summarised by the notebook; the code never did. Docstring corrected.

### Second set, block 1 (rounds 1-60): where it stopped (2026-10-16, usage limit reached)
- Played: cleric2 (Brannoc Ashdown, human Life cleric), barbarian2 (Korvash Emberhide, dragonborn), bard2 (Wren
  Ashgrove, half-elf Lore bard; companion Kit). Metrics in games/metrics2-b1.json. Notebook reads (lore, recall): 0 in
  180 rounds again; write_lore 73/70/74.
- Readers (READ.md): cleric2 69, barbarian2 44, bard2 56 findings; whole-story readers (READ_STORY.md): 15/12/12, about
  a third in rounds the block readers had no contradiction for. Spot-checked samples held (Hob "cannot leave" the lamp
  after walking a mile from it; two archers then "three more"). Files in games/read/.
- Found by the readers and traced:
  - cleric2 R12, R29: no reply at all, only game lines: the turn hit 40 model calls (max_turns_reached in the session
    file). Fixed (ddbedbb): asked once for the reply.
  - bard2 R46: eleven refused change_party calls, the format for an option's further choice wasn't in the tool's
    description; the DM made a rogue instead of the fighter it meant. Fixed (c8b0375).
  - bard2 R54-60: "API Error: ... safeguards flagged this message [reasoning_extraction]" shown as the DM's reply 7
    rounds running. Fixed (3f9eb6f): a failure, not shown. A probe on a fork later answered normally, so the flag is
    intermittent, but the game had no way to recover: open decision.
  - cleric2 R20: the PC died by the rules (two critical claws while paralysed at 0 HP). The DM ended the game; the
    test player asked to replay the night, and the DM rewound (clock set back to Day 1 11:55 PM, 'dead' removed). Rounds
    23-60 run on that rewind, so some "contradictions" with rounds 12-20 are the rewind. Open decision.
  - R42 bard2: `by: "pc"` refused; a test pins "the name as in the tracker", so left alone.
- A/B replays done, NOT yet judged (ab2/A, B, C; arms in ab2/arms): A = base/1B/2A on 8 rounds x 8 runs (64 replies
  per arm); B = base/3C/3D (agency) and C = base/4A/4B (clock), 6 rounds x 4 runs (24 per arm). Regex counts only
  (fmt.py): menu at end base 5, 1B 4, 2A 1 of 64; sheet numbers at end 4/5/2. 3D's replies are less than half as long
  (641 vs 1532 chars): a likely side effect to check. Next: blind.py + three Sonnet judges with JUDGE.md, score.py,
  then keep/drop in dm/prompt.md (nothing changed there yet), report, blocks 2 and 3.
- 2026-10-16 (resumed): judged blind (4 runs per round of each arm; ab2/*/blind, B2 = 3D rerun). No prompt idea kept;
  full results and causes in REPORT-set2-block1.md. Fixed: blind.py codes used the game's first two letters, so
  bard2 and barbarian2 rounds with the same number collided; codes now carry the game's name (score.py follows).
  Budget from now on (Jake): 4 runs per round on 6 rounds to screen, 8 only for a winner.

### Second set, block 2 (rounds 61-120), 2026-10-16/17
- Played all three games to round 120 with the block-1 fixes; bard2 R113 hit 40 model calls and the new ask
  recovered its reply. Metrics in games/metrics2-b2.json.
- Readers (READ.md, rounds 61-120): cleric2 43, bard2 49, barbarian2 48 findings. Whole-story readers (READ_STORY.md,
  rounds 1-120, findings in 61-120): 15 / 15 / 17. Spot checks held (barbarian2 R86 "three of the other shift" then
  R87 "a dozen boots"; R63 "three days' road" then R64 "a night's march").
- A/B (4 runs x 6 rounds, judged blind, one Sonnet judge per set; ab3/):
  - K, contradiction rounds (cleric2 85,103; bard2 97,110; barbarian2 90,104): base 9/24, DM_SAID=2 9/24, DM_SAID=4
    9/24 (repeats of the original contradiction 7/9/8). Dropped: showing the DM its own earlier sentences about the
    names in play made no difference. In cleric2 R85 the shown lines said the chapel is "about an hour south of the
    inn" and 7 of 12 replies still said two hours. said4 barbarian2 first hit the weekly usage limit (6 of 8 runs
    failed) and was rerun after the reset.
  - M, menu rounds (cleric2 70,114; bard2 70,101; barbarian2 97,120): base menu 4/24, 2C 1/24, 2D 1/24; contradiction
    8/8/9, agency 5/4/6, sheet read-out 16/15/12. 2C ("the player knows what they can do, told as the story: don't
    list their choices.") is the third set in a row with fewer menus and nothing worse; confirming at 8 runs (ab3/M8).
  - M8, 4 more runs of base and 2C on the same rounds: menu 9 vs 3, contradiction 8 vs 4, agency 8 vs 2, read-out
    12 vs 10. Over 48 a side: menu 13 vs 4, contradiction 16 vs 12, agency 13 vs 6, read-out 28 vs 25. **Kept 2C** in
    dm/prompt.md: "End each reply with the situation clear enough that the player knows what they can do, told as the
    story: don't list their choices." (was "... knows what they can do.").
  - DM_SAID reverted (6ad6efb, ba2a396); its A/B arms and results stay in ab3/.
- New cause found: check totals narrated with a different modifier than the roll used (bard2 R73, R76, R77); the DM
  writes the modifier itself. Proposed D4 (a sheet-backed skill field on dice), waiting on Jake.
- Report: REPORT-set2-block2.md.
