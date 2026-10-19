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

### Second set, block 3 (rounds 121-180), 2026-10-17
- Played with 2C. barbarian2's last 6 rounds (its player lines 179-184) were all refused by the safeguards
  ("[reasoning_extraction]"), 8 failed calls: nothing shown, as fixed in block 1, but the game can't go on (D2).
- Regex counts in play (fmt.py on the saves; menu at end per 60 rounds, block 2 → block 3): cleric2 2 → 0,
  barbarian2 10 → 2, bard2 2 → 1. Sheet numbers in the last paragraph: 2 → 1, 3 → 2, **12 → 45** in bard2. By ten
  rounds, bard2's read-outs were 1, 1, 1, 2, 3, 4 in rounds 61-120 (rising before 2C), then 1, 8, 9, 9, 10, 8: a
  closing status line nearly every reply ("It's half past ten at night on Day 16. You have 17 of 17 hit points, three
  slots, three Bardic Inspirations ... What does Wren do?", R146). To test: is it 2C, or a habit the conversation
  taught itself?
- cleric2: Brannoc died by the rules at R137 (Consume Life, then a critical Shock at 0 HP: three failures). The DM
  told the ending (R138-139); the test player asked to play on with a new character, Tamsin Vale, a human druid,
  "years later" (R140). Play has no way to make a new PC, so from R141 the DM ran Tamsin on Brannoc's sheet: her
  Fog Cloud was refused ("Brannoc can't cast Fog Cloud", R149), and her slots are kept by hand in the notebook ("The
  tool sheet is Brannoc's and refuses her spells, so the DM tracks her slots by hand"). Cleric2 rounds 141-180 are on
  the wrong sheet; this is D1 again, with a cost.
- barbarian2: Korvash died at R144. The DM offered "I can start a new character in Harrowmere", then in R145-149
  said it couldn't ("My tools only add companions to an existing party"), with bold, bullets and numbered menus and
  tool talk, and played the new PC (Grunna) on no sheet. Both deaths in block 3 end the same way: D1 is now the top
  open decision.
- Readers (READ.md, rounds 121-180): cleric2 49, barbarian2 43, bard2 53 findings. Checked and rejected: bard2 R153
  "a second long rest inside 24 hours" (the rest before began Day 15 ~8 PM, this one Day 16 11:25 PM: 27 h apart; the
  tool is right).
- A/B on bard2's closing status lines (ab4/S; rounds 126, 146, 156, 161, 166, 176; 4 runs each), arms: base (2C),
  pre2C (block 2's prompt), 5A (after "Plain text.": "The player sees their sheet whenever they ask: say a number
  from it only when it changed this turn."), 5B (2C plus "or end on a tally of what they have"). fmt.py, sheet
  numbers in the last paragraph: base 18/24, pre2C 20/24, 5A 18/24, 5B 18/24. Menus 0/2/1/0. Not judged blind: every
  arm is the same, so there is nothing to tell apart and judging would cost about as much as the replays. Reading:
  2C didn't cause it (the old prompt does it as much), and no wording breaks it once the conversation is full of it.
  Nothing kept.
- Final report: REPORT-set2-final.md.

### After the second set: going back, edits, a new PC (2026-10-17, Jake's design)
- Going back (dm/branch.py): a snapshot before each player line (sheet, companions, fight, clock, where the
  conversation stood; the notebook is rebuilt from write_lore calls). /redo <turn> [line] forks into a new save,
  leaving the old one as it was: the SDK session is forked at that point (resume_session_at), the API conversation
  cut there, or, after a cut since, opened with the turns so far word for word. /edit <text> rewrites the DM's
  latest reply in the transcript (the old text kept as kind "edited") and in its conversation (SDK: the session
  file, then a reconnect). The sheet, clock and notebook stay. Buttons in dm/web.html and dm/page.html: ↺ on each of
  the player's lines, and "Edit the DM's reply". Checked live on the SDK: after an edit the DM answered from the
  edited text; a fork had a new session without the old line, and the source session file was unchanged.
- The closing status line: a sentence "You have N of M hit points ..." in the reply's last paragraph is taken out
  of the reply and the conversation (kind "trimmed"), unless the player's line asked about their sheet. On the
  second set's saves it would have fired 48 / 1 / 1 times (bard2 / cleric2 / barbarian2).
- New PC after a death: new_pc (build, show, then confirm with an opening) and roll_ability_scores, refused unless
  the PC is dead and no fight is on. The old sheet goes to past_pcs; the instructions are rebuilt next turn. One line
  in dm/prompt.md: "If the PC dies, the player may go on in this world with a new character: make it with them with
  `new_pc`. The player can also go back to before a line of theirs and play on from there; that's theirs to do, not
  yours." Not yet tried live by the DM.
- No rules files touched (rules/ holds only process notes; there's no rules validator in this repo).

## Cleaned-history probe (Jake, 2026-10-17)
- evals/autoloop/probe_strip.py: bard2's DM conversation as it is now, copied twice; one copy with every "You have N of
  M hit points" sentence taken out (21 in the live conversation, the rest were before the cuts), one untouched. Same 3
  player lines, 2 runs each. Untouched: 5 of 6 replies closed on a read-out. Cleaned: 3 of 6. Both arms wrote one on
  the first line ("I take stock of where we are..."), which invites it. Lines 2-3: 3 of 4 untouched, 1 of 4 cleaned.
  Cleaning the history helps but doesn't stop it; the code strip stays the fix.

## Causes of the set 2 contradictions (Jake, 2026-10-17)
- evals/autoloop/context.py prints what the DM had at a round: its conversation (word for word, or only the summary),
  the notes shown, and the notebook as it was. CAUSES.md: six Sonnet readers sorted the 118 contradiction findings;
  out files in games/read/causes/. 1 not a contradiction, 22 doubtful.
- Where the earlier fact was: still in the conversation word for word in 108; only in a summary, or lost, in 7. In the
  notebook right in 43, both versions in 12, wrong in 2, not at all in 60; shown in the notes in only 18. Distance from
  the earlier fact: same reply 19, 1-3 rounds 37, 4-20 rounds 42, more 20.
- Kinds: restated a scene detail differently (counts, positions, who holds what) 37; made up something new that clashes
  31; worked out a sum wrong (days, distances, ages) 14; both sides in one reply 14; went back to a fact it had
  corrected 3; claimed a tool it lacks 1; other 17 (narration against its own dice or tracker, loose wording).
- So it isn't memory loss: the fact was nearly always in front of it, mostly from the last few rounds.

## Jev as a contradiction check (Jake, 2026-10-18)
- evals/autoloop/jev_check.py: one yes/no question to Jev (TypeSafe, via Vercel AI Gateway) per round: the reply, the
  turns before it word for word, and the notebook entries the reply names. 105 rounds with a contradiction finding
  (not ruled out by the cause readers) against 150 rounds no reader flagged. Results in games/read/causes/jev*.json.
- Near chance every time (AUC: 0.5 is a coin flip, 1.0 perfect): jev (1.13) 0.59, jev-1.14.0 0.60, jev-1.14.0 with
  3 turns instead of 10 0.61. Best trade-off seen: 1.14 at 0.5 caught 16 of 105 and flagged 14 of 150 clean rounds.
  About 6.7M input tokens in all, roughly $0.28. Not usable for this; not built into the game.

## #1, notebook writes that answer back (Jake, 2026-10-18): not kept
- A notebook write returned, to the DM only, what the notebook said before the write about the entry written and the
  names in its new text (up to 4 entries, 1500 characters each, once a turn, not the party's): dm/lore.py answer().
- A/B, evals/autoloop/ab5: 6 rounds where the notebook had the right fact and the DM wrote to it before its reply
  (cleric2 143, 152; barbarian2 81, 90; bard2 97, 127), 4 runs each, base with NO_ANSWER=1, blind Sonnet judges (JUDGE.md).
- Contradictions 9 of 24 with answers, 4 of 24 without; repeats of the original 2 vs 1; acting for the PC 8 vs 4.
  Small numbers, but no sign it helps. Some of the new ones repeat what the notebook itself said (Reedholm "half a
  day"; Hale "only ever the go-between"). Not given 8 runs. The change is committed, then reverted in the next commit.

## A model as a contradiction check (Jake, 2026-10-18)
- evals/autoloop/haiku_check.py: the same rounds and state as jev_check.py, one call each through the API key in the
  repo's .env (given to the client only, never to the environment). Results in games/read/causes/{haiku,sonnet,sonnet-sev}.json.
- Haiku 5.5 (yes/no + quote): caught 42 of 105 contradiction rounds, but its quote matched the readers' finding in
  only 18; flagged 49 of 149 clean rounds. Too weak.
- Sonnet 5.5 (yes/no): caught 104 of 105 and flagged 56 of 60 clean rounds; it flags any nitpick.
- Sonnet 5.5 with a severity per problem, acting on 2+: caught 71 of 105, flagged 28 of 60 clean rounds. A sample of
  those 28 looks about half real (misses by the readers: the Foreman's terms changing a turn later, a distance that
  shrank) and half nitpicks or misreadings. Severity 3 alone: 4 of 105.
- Cost about $11 in all (Haiku $0.50, the two Sonnet runs about $5 each). Nothing built into the game.
- 1 to 5 scale with an example per level, plus a fix per problem: 'text' with a replacement, or 'dm' when the sheet,
  fight, clock or notebook must change (haiku_check.py `five`; games/read/causes/sonnet-five.json). Acting on 3+:
  caught 47 of 105, flagged 14 of 60 clean (2+: 92 and 41; 4+: 4 and 2; nothing got 5). 71 of 73 quotes at 3+ are the
  reply's exact words, so code could swap them. It chose 'text' for 68 of 73 and 'dm' for 5; sampled replacements
  read well, but some 'text' fixes paper over a time or count problem instead of sending it to the DM. About $5.6.
- By topic (Haiku labelled each reader finding and each checker problem; games/read/causes/topics.json): time is the
  biggest real group (29 of 105) and the biggest false-flag source (8 of the 14 clean flags at 3+). Count, distance,
  place and items are rarely flagged on clean rounds even at 2, while identity and deeds at 2 are as often wrong as right.
  Acting at 2+ but 3+ for time/identity/deeds: caught 79 of 105, flagged 23 of 60 (3+ alone: 47 and 14). Tuned on the
  same rounds, so it needs fresh rounds to confirm.
- Hand labels replace the Haiku ones (topics-hand.txt; 101 of 458 problems have two topics; topic_cutoffs.py).
  Share of problems that are a reader's finding, by score: at 1 almost none in any topic; at 2 items 53%, count 39%,
  mechanics 37%, but deeds, place and identity 10-12%; at 3 most topics 40-60%, mechanics 0 of 7. Best per-topic
  cutoffs (count, place, items, status, mechanics 2+; distance, deeds, identity 3+; time 4+) fit 74 of 105 and 17
  of 60, but leave-one-round-out gives 61 of 105 and 20 of 60, against 47 and 14 for flat 3+ (also LOO). Counting
  only catches on the readers' own line: 44 of 105 against 28. Under the rule, 66 of the 128 kept problems touch
  time, items or mechanics and would go back to the DM; the checker itself said 'dm' for 6.
- Fourth try (`quote`): the earlier line copied word for word (code checks it is in the context), a checklist (dice,
  HP and spell lines; counts and times in one reply; deals and orders), score 3+ for anything that changes the
  player's choices or makes a plan impossible, and the checker's own topics. Leave-one-out per topic: caught 62 of 105,
  flagged 14 of 60 (last try 61 and 20); flat 3+: 42 and 7 (last 47 and 14). The quote check itself drops little (23 of
  395; 2 of its 11 dropped at 2+ were real): the prompt does most of the work. Of the 10 clean rounds the fitted rule
  flags, I judge 8 or 9 real misses by the readers. One wasted run (~$5) before fixing the mode switch. quote_cutoffs.py.

## Reply and bookkeeping in one model call (Jake, 2026-10-18)
- Code: a model call whose tools are all bookkeeping (change_time, write_lore, change_pc, change_party,
  change_creature), made with a full reply and with no error, ends the turn: in the API loop, and in Claude Code by a
  PostToolUse hook that stops it. Prompt: rolls and lookups first, then the reply with the bookkeeping after it in the
  same message (replaces "all tool calls first", Jake's call). Bookkeeping after the reply no longer gets the LATE
  note. 288 tests pass; checked live that Claude Code stops and the next turn goes on.
- Replay A/B, 6 ordinary rounds (none mid-fight) x 4 runs (ab6): model calls per round 2.75 old, 2.54 new; with the
  order also in the per-turn reminder 2.63. The DM kept its old order (bookkeeping, then the reply in a call of its own)
  in 19 to 22 of 24 runs, and never combined after a roll: these games have 180 rounds of the old habit behind them.
  When it did put the reply first, the turn took 1 call. Quality not judged: too few runs changed. Untested on a new game.
- Checker with a 5-turn window (JEV_WINDOW=5, `quote`; sonnet-quote-w5.json): input 1.64M against 2.53M for 10 turns
  (35% less; the notebook entries and the reply stay). Leave-one-out per topic: caught 71 of 105, flagged 19 of 60
  (10 turns: 62 and 14); flat 3+: 44 and 5 (10 turns: 42 and 7). No worse, so 5 turns. About $0.025 a check.
- Cut at 60k keeping 5 turns (was 200k and 20; b049d52). New 15-round test game bard3 to see both changes from turn 1.
- bard3, a new 15-round game with both changes: the reply first and its bookkeeping in the same call in 5 of 15
  rounds (1 call each). In 10 of 15 the DM made the bookkeeping first and then wrote only a closing line ("What does
  Pip do?"), a stub, so the game asked for the full reply: one more query each. The order cost more, not less, when
  the DM got it wrong. After a roll it never wrote the reply first. No cut: the conversation grew about 3k a round
  (19k to 58k), so 60k is reached near round 16; the cut is untested.
- Prompt made explicit (one last message: the whole reply, then its record calls; never the calls first, after a roll
  too; a reply drafted in thinking isn't written) and the per-turn reminder to match. Replay of 6 bard3 rounds x 2:
  still 8 of 12 stubs (record calls first, then a closing line, then the game's ask for the full reply); 1 of 12 did it
  in one call. The prompt alone doesn't move the habit.
- Cause found (order_bench.py; a minimal API bench of four tools and four lines of instructions): with nothing to roll,
  Sonnet sent the reply and its record in one message 5 of 5; after a roll result, 0 of 5, with thinking on or off,
  step-by-step instructions, or a note in the roll's result. Opus the same; Haiku 4 of 5. Its thinking shows it
  drafting the reply, making the record calls, then writing the closing text alone: once working through tool
  results, the text that ends its turn comes last, in its own message. Not the prompt's length, history or Claude Code.
- Fix: the reply is a tool (`reply`), sent with the record calls as calls together; text outside it is never shown, a
  second reply is refused, and a reply by the tool is whole however short (no stub ask). Prompt and reminder say so.
  Minimal bench 10 of 10 in one message; full prompt on the API from a fresh conversation 13 of 14 (was 0 of 8);
  Claude Code replay of 6 bard3 rounds x 2, mid-game with the old habit behind it: 12 of 12, all after a roll, no stubs,
  replies 1,026 to 1,503 characters. 290 tests pass. The reply now comes whole, not word by word.

## Creatures' turns run by code (Jake, 2026-10-19)
- Where fight calls went (Claude Code session files of the autoloop games): 1,527 of 5,225 model calls were in fights,
  median 16 a fight; 497 were a single roll (an attack roll read before its damage roll). Of ~500 creature turns, ~40%
  a plain attack, ~10% a spell or special action, ~45% no roll (moving, fleeing, talking, down).
- `creature_turns` (dm/fight.py): the DM sends every creature's turn up to the next party member's in one call
  (attacks and targets, whom it moves away from); the code rolls each attack from the SRD stat block (`monster`, now
  given in add_combatants), damage only on a hit, doubled dice on a crit and on a melee hit on a paralyzed or
  unconscious target, and applies it. It stops where a party member can react (opportunity attack, Protection, Cutting
  Words, Shield and Cutting Words only when they could turn a hit into a miss, Uncanny Dodge, Deflect Missiles,
  Hellish Rebuke), where a hit does more than damage, and for a concentration save. After a stop, resume plays on the
  turns sent; before each turn and attack it checks they can still happen (creature in, up, not incapacitated, next;
  target in and not dropped since the turns were sent), else hands just that turn back. No standing orders (Jake: skip
  for now). A versatile weapon is one-handed unless damage is passed; resistances are the DM's to pass. The DM starts
  party members' turns with next_turn (when the code did, a replay skipped a companion's turn).
- Replay A/B of fight-start rounds (ab7; base c28d3ff): 10 rounds x 2 runs each arm (rounds before ~80 have no session
  to branch from). Model calls per round 10.2 old, 6.0 new (-41%). Refusals in the new arm were mostly a choice of
  damage (versatile weapons, since defaulted) and 'pc' as a target name (since accepted). Read through: attacks,
  crits and damage right; a raging barbarian's resistance was not passed once (the tool now says to). Not measured:
  mid-fight rounds (their trackers have no monster).
- run.py: the test player gets strict_mcp_config: it had passed on a claude.ai connector sign-in notice in its line.
