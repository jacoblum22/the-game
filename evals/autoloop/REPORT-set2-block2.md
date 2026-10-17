# Autoloop, second set, block 2 (rounds 61-120): report

The same three games (cleric2, barbarian2, bard2), played from round 61 to 120 with block 1's four code fixes and
dm/prompt.md unchanged. 2026-10-16/17, DM on Sonnet 5.5.

## What changed
- **Prompt: one wording kept** (2C, the menu half of block 1's 2A). The end-of-reply rule now reads "End each reply
  with the situation clear enough that the player knows what they can do, told as the story: don't list their
  choices." Judged blind over 48 replies a side: menus at the end **13 → 4**, nothing worse (table below).
- **Code: nothing new kept.** The notebook trial (DM_SAID: show the DM its own earlier sentences about the names in
  play) made no difference and was reverted (6ad6efb, ba2a396). 274 tests pass.
- **Block 1's fixes held:** bard2 R113 ran out of model calls (40), and the new ask got its reply. No API error
  reached the player.

## Numbers (metrics.py; cleric2 / barbarian2 / bard2)
- Median reply 1644 / 2044 / 1681 characters (block 1: 1635 / 1568 / 1402). Median turn 15.5 / 20.4 / 23.0 s,
  longest 101 / 157 / 171 s. Turns and replies are getting longer as the conversations grow.
- Refused calls 3 / 4 / 8. Bullets 1 / 0 / 1; bold and headings 0. Conversation cut at 200k tokens: 2 in each game.
- Notebook reads: **0 / 2 / 9** (`lore`, `recall`), the first the DM has made in either set, against 50 / 63 / 70 writes.

Readers (READ.md, rounds 61-120): 43 / 48 / 49 findings. Whole-story readers (READ_STORY.md, rounds 1-120, findings in
61-120): 15 / 17 / 15.

| category | cleric2 | barbarian2 | bard2 |
|---|---|---|---|
| contradiction | 6 | 17 | 12 |
| format | 15 | 2 | 8 |
| agency | 7 | 10 | 2 |
| bookkeeping | 2 | 5 | 13 |
| clock | 7 | 2 | 3 |
| rules | 1 | 4 | 5 |
| pacing | 2 | 5 | 2 |

Spot checks against the transcripts held: barbarian2 R86 "the three of the other shift are coming up", then R87 "a
dozen boots pouring in"; R63 "Greyshaft is three days' road", then R64 "a night's march away".

## Problems, grouped by traced cause

### C4. Contradictions with what was said in play (open; the code trial didn't help)
Still the biggest problem, worst in the barbarian's long prison-and-escape arc. The whole-story readers show it
building across blocks:
- **Travel times drift:** Greyshaft is three days from the Throat, then a night's march (R64), then "Dreg walked the
  road beside you for three days" (R88) for a march of under two days.
- **Counts drift:** three guards become a dozen (R86-87); forty spears march on after ten deserted (R104, R115).
- **Characters' pasts are retold:** Tessa "couldn't even climb to the cairn" (R37), then "has been to the Goat's Throat
  on a dozen nights alone" (R107, sev 3). Elowen's arrival is told two ways (bard2 R105, sev 3).
- **Small facts in a scene:** a lamp moved out of reach is snatched off the desk (R80-81); a spear taken from Tessa's
  knees lies across them again (R82-83).

**The trial:** for the names in the last turns, the per-turn notes added the DM's own latest earlier sentences about
them. It made no difference: contradictions 9 / 9 / 9 of 24 (base, 2 sentences a name, 4 a name). In cleric2 R85 the
notes the DM got said the chapel is "about an hour south of the inn", and 7 of its 12 replies still said two hours.
Putting the right fact in front of the DM isn't enough on its own when the DM is improvising a new distance.

### C6. Format (prompt fix kept for menus; sheet read-outs open)
- Menus: "Here are the options", a numbered list of three with AC, DC and concentration maths (cleric2 R63, sev 3);
  "you can begin the duel by roaring your rage at him, or by speaking first" (barbarian2 R120). 2C is kept for these.
- Sheet read-outs: "You are at 1 hit point, but you stand at 300 experience, which is enough to rise to second
  level" (barbarian2 R97). Judges flagged them in about half of all replies in every arm, and no wording has helped yet.

### C5. Acting for the PC (open)
- The player wrote "I whip my head back, spit the gag clear" and the reply has "the gag hangs in your teeth"
  (barbarian2 R94, sev 3).
- In the replays, replies walk the PC somewhere new that the player never chose (down the cellar stair, down to the
  stones).

### C10. The knocked-out-and-captured loop (new, pacing)
barbarian2 R70, R76, R87: Korvash charges, drops to 0 HP, stabilises, regains 1 HP after 1d4 hours and wakes up
captured, with a time jump each time. Each step is by the rules and the bold player keeps charging, so the cause is
the DM always choosing capture. Noted, not tested; it may not recur outside this arc.

### C8. Bookkeeping (open; one cause is new)
- **New cause: check totals told wrong.** The DM writes its own modifier into the dice roll and then narrates with a
  different one. "Your Perception check was a 16" when the game line shows 14 + 1 = 15, and the roll's own reason
  says "sheet Perception +2" (bard2 R76). Also R73 (an 8 told for a 7) and R77 (12 for 11). See D4.
- Items and money still slip: a copper given to Pip is never deducted (R82); the room's payment is never taken (R102).
- Bardic Inspiration uses miscounted when the companion spends a stored die (R89, R93).
- Song of Rest healing applied twice (R114).

### C7. Clock (open)
cleric2 has 7 findings. In the replays, times like "twenty to seven" appear when the game clock still says 6:20 AM
(cleric2 R70).

### Minor
- bard2 R102: two refusals removing "exhaustion" when the sheet had "Exhaustion 1". The DM fixed it on its third
  call. The condition list doesn't model exhaustion levels; left alone.
- cleric2 R105-106: the DM offered a change of prepared spells mid-day, and the tool refused (correctly, by the rules).

## A/B tests (blind; one Sonnet judge per set with JUDGE.md; score.py)

| set | arm | change | n | contradiction | agency | menu | sheet read-out |
|---|---|---|---|---|---|---|---|
| K (contradiction rounds) | base | — | 24 | 9 | 2 | 0 | 17 |
| | said2 | the DM's 2 latest earlier sentences per name in play (8 in all) | 24 | 9 | 4 | 0 | 15 |
| | said4 | 4 per name (16 in all) | 24 | 9 | 2 | 1 | 17 |
| M (menu rounds) | base | — | 24 | 8 | 5 | 4 | 16 |
| | 2C | "... told as the story: don't list their choices." | 24 | 8 | 4 | 1 | 15 |
| | 2D | "... Leave the choosing to them: end on the moment, not on a list of what they might do." | 24 | 9 | 6 | 1 | 12 |
| M8 (4 more runs) | base | — | 24 | 8 | 8 | 9 | 12 |
| | 2C | | 24 | 4 | 2 | 3 | 10 |

- Rounds: K = cleric2 85, 103; bard2 97, 110; barbarian2 90, 104. M = cleric2 70, 114; bard2 70, 101; barbarian2 97, 120.
- **2C over 48 replies:** menu 4 vs 13, contradiction 12 vs 16, agency 6 vs 13, read-out 25 vs 28. **Kept:** this is
  the third set in a row where this half of the wording cut menus (block 1 2A: 2 vs 6; first set: 0 vs 4). 2A's other
  half, about sheet numbers, is the part that raised read-outs and is not included. 2D cut menus equally at 4 runs;
  2C went forward because it was tested twice before.
- One said4 arm hit the weekly usage limit (6 of 8 runs failed) and was rerun after the reset, before judging.

## Decisions for Jake
D1-D3 from block 1 are still open, with the same defaults: a dead PC in a test game is not handled specially, a
flagged turn is not retried, and the notebook stays as it is. D3 now has an answer from the test: putting the DM's
earlier words in front of it didn't help, so I'd drop (b) and take (a).

- **D4. Check totals:** the DM writes the modifier into each roll itself and gets it wrong now and then.
  - (a) Give the dice tool an optional `skill` (or `save`) field that takes the modifier from the sheet, so the game
    line and the sheet always agree (recommended: code gives the fact, and the DM still chooses what to roll).
  - (b) Leave it: 3 rounds in 60, each off by one.
- **D5. Usage:** the DM's conversation is cut at 200k tokens, and every model call re-reads it. Turns now take 15-23 s
  and replays cost more each block.
  - (a) Keep 200k for block 3 (recommended for now, so block 3 is comparable with blocks 1 and 2).
  - (b) Cut at about 120k: cheaper on every call, but the DM remembers less of the raw conversation. Worth its own
    test.

## Next (block 3, rounds 121-180)
- Play with 2C in dm/prompt.md, then the same reading and analysis.
- Ideas to screen at 4 runs × 6 rounds: sheet read-outs (a wording that keeps numbers out of the closing paragraph
  only); D4(a) if Jake agrees.
