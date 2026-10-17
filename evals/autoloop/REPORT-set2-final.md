# Autoloop, second set: block 3 (rounds 121-180) and final report

Three games, 180 rounds each, on K-2SO, 2026-10-16/17, with the DM on Sonnet 5.5. Block reports:
REPORT-set2-block1.md and REPORT-set2-block2.md. Everything is logged in LOG.md.

## Over the whole run
- **Kept, code (block 1, four fixes):**
  - A turn that runs out of model calls is asked for its reply. It recovered bard2 R113.
  - An API error is never shown as the DM's reply.
  - The companion choice format is now documented.
  - The test player sees a failed turn as the terminal shows it.
- **Kept, prompt (block 2, one line):** replies end "told as the story: don't list their choices." Over 48 blind
  replies a side, menus fell from 13 to 4. In play, menus at the end (regex) per 60 rounds went:

  | game | block 1 | block 2 | block 3 (with the line) |
  |---|---|---|---|
  | cleric2 | 4 | 2 | 0 |
  | barbarian2 | 2 | 10 | 2 |
  | bard2 | 10 | 2 | 1 |

- **Tested and dropped:**
  - 1B, recall before stating old facts (0 recall calls).
  - 2A, the sheet half of the end-of-reply line (more read-outs).
  - 3C and 3D, agency wordings (noise).
  - 4A and 4B, clock wordings (worse).
  - DM_SAID, the DM's own earlier sentences in the per-turn notes (9/9/9).
  - 5A and 5B, sheet read-out wordings (no change).
- **The problem that's left:** the DM contradicts what it said earlier in play. That was about 1 round in 4 in every
  block. Prompt wording and handing the facts back didn't move it.

## Block 3 numbers (metrics.py; cleric2 / barbarian2 / bard2)
- Median reply 1898 / 1669 / 1811 characters. Median turn 17.9 / 16.6 / 22.0 s.
- Refused calls 1 / 0 / 5. Failed calls 0 / 8 / 0. Rounds with no reply 0 / 5 / 0 (the safeguard flag, C2).
- Notebook reads 2 / 2 / 4, against 51 / 67 / 55 writes.
- Readers (READ.md, rounds 121-180): 49 / 43 / 53. Whole-story readers (rounds 61-180, findings in 121-180):
  15 / 19 / 16.

| category | cleric2 | barbarian2 | bard2 |
|---|---|---|---|
| contradiction | 10 | 9 | 22 |
| format | 20 | 10 | 9 |
| agency | 8 | 4 | 8 |
| rules | 4 | 5 | 5 |
| bookkeeping | 3 | 6 | 3 |
| thread | 1 | 5 | 1 |

Much of cleric2's and barbarian2's format count is the out-of-character talk after their PCs died (C9).

## Block 3 problems, by cause

### C9. The PC died in two of three games, and play can't make a new one (open, D1; top priority)
- **cleric2:** Brannoc died by the rules at R137 (Consume Life, then a critical Shock at 0 HP). The DM told the ending
  well. The test player asked to go on with a new character "years later" (Tamsin Vale, a druid). Play has no tool for
  a new PC, so from R141 Tamsin runs on Brannoc's sheet. Her Fog Cloud was refused ("Brannoc can't cast Fog Cloud",
  R149). The DM noted "The tool sheet is Brannoc's and refuses her spells, so the DM tracks her slots by hand", and
  checks used made-up modifiers (Insight +3, then +5).
- **barbarian2:** Korvash died at R144. The DM offered "I can start a new character in Harrowmere", then took it back
  ("My tools only add companions to an existing party", R145). It spent R145-149 explaining, with bold, bullets,
  numbered menus and tool names, and played the new PC on no sheet.
- With two deaths in 60 rounds, this is no longer a corner case. In the real game a player whose PC dies needs a
  clear path too.

### C2. The safeguard flag ended a game (open, D2)
barbarian2's last six player lines (R175-180) were all flagged ("[reasoning_extraction]"): 8 failed calls. Nothing
was shown, as fixed, but the player lost five rounds, including a natural 20 on Insight, and R180 apologised out of
character instead of playing them. This is the second game to stick in the flag for several rounds in a row (bard2
R54-60 in block 1).

### C4. Contradictions (open)
They now run against the DM's own corrections. In bard2 R141 the DM stopped to correct itself: "I said Thornhallow was
a day's ride from the causeway. It isn't", two more days by wagon. At R156 it says "Thornhallow is a day's ride off"
again. Other examples:
- Pell's guards are six, then eight, then six (bard2).
- Greyshaft goes from three days away to about a day and a quarter (barbarian2).
- A prayer-book page credits the dead Brannoc with knowledge of an island he never set foot on, and the new
  character's whole arc rests on that clue (cleric2 R165, sev 3).

### C6. Sheet read-outs: a habit the conversation teaches itself (open)
bard2's closing paragraphs held sheet numbers in 0, 12 and 45 of each block's 60 rounds. By ten rounds the count was
1, 1, 1, 2, 3, 4 in rounds 61-120, then 1, 8, 9, 9, 10, 8. Nearly every reply came to end like this: "It's half past
ten at night on Day 16. You have 17 of 17 hit points, three slots, three Bardic Inspirations ... What does Wren do?"
(R146).

The A/B (6 rounds × 4 runs, regex counts) gave read-outs at the end of base 18/24, the pre-2C prompt 20/24, 5A ("say
a number from it only when it changed this turn") 18/24 and 5B ("or end on a tally of what they have") 18/24. So
the block 2 line didn't cause it, and no wording breaks it once the conversation is full of it. I didn't judge these
blind: every arm came out the same, and judging would have cost about as much as the replays. Nothing kept.

### C8. Bookkeeping and check totals (open, D4)
- More check totals told with a modifier other than the roll's, as in block 2.
- The DM narrates a check result against the dice. Deception 15 against Insight 11 "sees through it" (barbarian2
  R137). The dice say two of the rearguard fight, but none do (R171).
- A greataxe disarmed and never returned to the sheet (R143).

### Checked and rejected
- bard2 R153 "a second long rest inside 24 hours": the rests began 27 hours apart, and the tool was right.

## Decisions for Jake (D1 and D2 now matter most)
- **D1. When the PC dies:**
  - (a) In test games, the harness starts a new character in a new game (run.py, recommended): cheap, and every save
    stays one PC with one sheet.
  - (b) In the game itself, give play a way to make a new PC in the same world (creation run from play, keeping the
    notebook and companions). This is bigger, and a design call: what should a player whose PC dies be offered?
  - (c) Stop the test game at a death.

  Both deaths here were by the rules. Brannoc's ending (R138-139) is among the best writing in the run.
- **D2. A flagged turn:**
  - (a) Retry the call once automatically, then show a short in-game line saying the reply didn't come through
    (recommended).
  - (b) After two flagged turns in a row, cut the conversation (summary plus recent turns), which may clear it. bard2
    recovered after a cut in block 1.
- **D3. The notebook:** (a) accept that it's write-mostly (recommended; the DM_SAID test showed that handing facts back
  doesn't help).
- **D4. Check totals:** (a) a `skill`/`save` field on the dice tool that takes the modifier from the sheet
  (recommended).
- **D5. Usage:** (a) keep the 200k cut, or (b) test about 120k as its own A/B. The read-out habit in C6 suggests a
  shorter raw conversation may also carry fewer bad habits, which is one more reason to try (b).

## Suggested next steps
1. D1(a) in run.py, so test games survive deaths; and D2(a) in sdk.py/play.py, with tests.
2. Test D5(b) on replays: does a shorter cut change contradictions or read-outs?
3. D4(a) with tests, then one more block.
