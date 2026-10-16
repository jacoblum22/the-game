# Autoloop, second set, block 1 (rounds 1-60): report

Three new games on K-2SO, 2026-10-16, with the DM on Sonnet 5.5 and Sonnet players (briefs in run.py):
- **cleric2**: Brannoc Ashdown, a human Life cleric, played carefully and kindly.
- **barbarian2**: Korvash Emberhide, a dragonborn barbarian, played boldly.
- **bard2**: Wren Ashgrove, a half-elf Lore bard, played as a trickster. Her companion is Kit, a fighter the DM
  meant to build but couldn't (see C3).

The first set's DM conversations stayed on the old PC, so its games couldn't go on and its leads (1B, 2A) were tested
here instead, on rounds they were never written against.

## What the fixes achieved
- **Code (four fixes, 274 tests pass):**
  - A turn that runs out of model calls is now asked for its reply. Before the fix the player saw no narration in
    2 of 180 rounds.
  - The companion choice format is now documented in change_party's description and in the refusal (11 refusals
    in one round before).
  - An API error is no longer shown as the DM's reply (7 rounds running before).
  - The player in the test games now sees a failed turn the way the terminal shows it.
- **Prompt: nothing kept.** Every idea tested this block was a null or made things worse (table below), so dm/prompt.md
  is unchanged.

## Numbers (metrics.py; cleric2 / barbarian2 / bard2)
- Median reply 1635 / 1568 / 1402 characters. Median turn 13.8 / 15.3 / 12.9 s, longest 87 / 54 / 85 s.
- Rounds with no reply: 2 / 0 / 0 (C1). Rounds showing an API error as the reply: 0 / 0 / 7 (C2). Refused calls:
  1 / 3 / 12 (C3 accounts for 11).
- Bold 0 / 0 / 1; bullets 2 / 0 / 1; headings 0.
- Notebook reads (`lore`, `recall`): **0 / 0 / 0**, against 73 / 70 / 74 writes.
- Conversation cut at 200k tokens: 0 / 1 / 0.

Readers (READ.md, one per game, whole block): 69 / 44 / 56 findings.

| category | cleric2 | barbarian2 | bard2 |
|---|---|---|---|
| contradiction | 16 | 13 | 13 |
| format | 19 | 7 | 15 |
| agency | 13 | 6 | 7 |
| clock | 6 | 6 | 3 |
| bookkeeping | 4 | 6 | 6 |
| rules | 3 | 1 | 2 |

Whole-story readers (READ_STORY.md, new) found 15 / 12 / 12. About a third of these were in rounds where the block
readers had found no contradiction. Examples:
- cleric2 R31: "five dead men to bring home", when only four bodies were on the cart.
- barbarian2 R18: Veshra's armed band waits at the border stones, though only Korvash and Gorrak knew of the deal.
- bard2 R15: Hale warns Osric about Wren before anyone could have told him.

Spot checks against the transcripts held: Hob's "I cannot leave it" at R14 after walking a mile from the lamp in
R5-9, and "two archers" in R7 against "three more" in R9.

## Problems, grouped by traced cause

### C1. A turn ran out of model calls (fixed, code)
- **What happened:** cleric2 R12 and R29 had no narration at all. The player read only dice and tracker lines while
  Cal died and the PC fell. With the PC unconscious, the DM ran the fight round after round inside one reply (about
  60 tool lines). The session file shows `max_turns_reached` at 40.
- **Made-up example:** any long fight the PC can't act in, such as a sleep spell on the PC with three foes left.
- **Fix (ddbedbb):** a failed turn after tool calls with no full reply is kept in the save (kind `failed`) and the DM
  is asked once: "Your turn stopped before you wrote your reply ... Write your full reply to it now."

### C2. An API error was shown as the DM's reply (fixed, code; recovery is open, D2)
- **What happened:** bard2 R54-60 showed this as the DM's reply 7 rounds running, just as the infiltration scene
  reached its payoff:

  > API Error: Sonnet 5.5's safeguards flagged this message (https://www.anthropic.com/legal/aup). ...
  > Details: `[reasoning_extraction]`

  Claude Code reports the error as its own message (model `<synthetic>`), and sdk.py passed it on as text.
- **Fix (3f9eb6f):** the error is now a failure: never shown, and kept in the save.
- **The flag comes and goes:** a probe on a fork of the game (probe.py) was flagged twice. A second probe on another
  fork got a normal reply, and the conversation cut that followed went through too.

### C3. The DM couldn't give a companion's further choice (fixed, code)
- **What happened:** bard2 R46, building Kit as a fighter. The DM tried eleven shapes for "a martial weapon"
  (`"a"`, `{"a": ["Longsword"]}`, `"class.equipment.2 > a martial weapon": "Longsword"`, ...). It then built Kit as
  a rogue instead.
- **Cause:** the format, `{option, picks}`, is described only on build_character, which the play DM doesn't have.
- **Fix (c8b0375):** change_party's description gives the format with an example, and the refusal says how to give
  the picks and lists the choices.

### C4. Contradictions with what was said in play (open; prompt ideas didn't help)
About 1 round in 4. Most are things said in play that never reached the notebook:
- **Who can be where:** Hob "cannot leave" the lamp (cleric2 R14) after walking to the barn in R5-9.
- **Counts:** two archers, then three more (barbarian2 R9); "forty small faces" against ninety-four children (R48).
- **Travel times:** the Throat a night's march (R3), then "a day and a half" (R23). Gorrak arrives the same day from
  three days' road (R57, sev 3).
- **Small physical facts:** Hob's lantern unlit, then giving flame (cleric2 R8, R13); the keys on the Foreman's chain,
  then in Hask's lap (barbarian2 R46).

The DM never reads its notebook: 0 `lore` or `recall` calls in 180 rounds, and none in the 64 replays told to
recall (1B).

### C5. Acting for the PC (open)
The DM writes the PC's feelings, conclusions and whole stretches of their speech:
- "you have the axe out of your head and your arms around her before you've decided to move" (barbarian2 R37)
- "Was he alone? Not at the end, you say" (cleric2 R48)
- "you sleep" (barbarian2 R47), when the player planned to lie awake for an ambush.

### C6. Format: menus at the end and sheet read-outs (open)
- "You could carry Cal now, rest here under the lamp's light until your strength returns, or ..." (cleric2 R14)
- "You have 13 of 14 hit points and 100 of 300 XP." (barbarian2 R22)
- Bullet lists in cleric2 R36-37 (a choice of spells).

### C7. Clock and time skips (open; prompt ideas made it worse)
- "When you leave, it is past noon" and "about half past eleven" in the same reply (cleric2 R40).
- The second-bell raid is logged at 6:08 PM (barbarian2 R41).
- A full day skipped after the player only hummed a verse (barbarian2 R34).

### C8. Bookkeeping (open, minor)
- Gifts and food never reach the sheet: bread and cheese (barbarian2 R1), the horn charm and goat meat (barbarian2
  R2, recorded only when the player asked in R15), apple slices (cleric2 R57).
- An item given away stays on the sheet: Osric's register copy (bard2 R23).

### C9. The PC died, and the DM rewound the story (open decision, D1)
- **What happened:** cleric2 R20, by the rules: two critical claws on a paralysed PC at 0 HP, then a failed death
  save. The DM ended the game ("The game ends here."). The test player thanked the DM and asked for "the same night
  replayed".
- **The rewind (R23):** the DM set the clock back to Day 1 11:55 PM, removed 'dead' through the condition list
  (whose refusal text tells how a spell that returns the dead is recorded), and wrote a REWIND note in the notebook.
- **Consequence:** rounds 23-60 run on the rewound night, so some contradictions with rounds 12-20 found there are
  the rewind.

## A/B tests (blind; three Sonnet judges with JUDGE.md; score.py)
- **Set A:** contradiction and menu rounds, 8 rounds × 4 runs judged = 32 replies per arm; 8 runs were replayed, kept
  for winners.
- **Set B:** agency rounds, 6 rounds × 4 runs = 24 per arm.
- **Set C:** clock rounds, 6 rounds × 4 runs = 24 per arm.

| arm | change | contradiction | agency | menu | sheet read-out | clock | verdict |
|---|---|---|---|---|---|---|---|
| base (A) | — | 9/32 | 11/32 | 6/32 | 7/32 | | |
| 1B | `recall` facts from more than a few turns ago before stating them | 10/32 | 10/32 | 6/32 | 7/32 | | dropped: 0 recall calls in 64 replays, no effect |
| 2A | end "told as the story: don't list their choices or read out the sheet's numbers" | 12/32 | 13/32 | **2/32** | 11/32 | | not kept: fewer menus (fmt.py: 1 vs 5 of 64), but more read-outs and contradictions |
| base (B) | — | 3/24 | 17/24 | 3/24 | 6/24 | | |
| 3C | feelings, conclusions and memories are the player's too | 2/24 | 14/24 | 2/24 | 3/24 | | dropped: within noise |
| 3D | don't play a scene past the player's action; stop where the character would act again | 1/24 | 16/24* | | | | dropped: no effect (8 vs 8 on cleric2; 8 vs 8 on the rerun rounds) |
| base (C) | — | 4/24 | 8/24 | 2/24 | 6/24 | 4/24 | |
| 4A | a time of day in the reply is the clock's | 11/24 | 11/24 | 3/24 | 6/24 | 11/24 | dropped: worse (more time talk, more errors) |
| 4B | don't move time past a moment the player could act in | 7/24 | 6/24 | 4/24 | 6/24 | 8/24 | dropped: worse clock |

\* 3D's first run on barbarian2 and bard2 hit last night's usage limit: all 12 replies were "You've hit your session
limit". Those 12 were rerun and judged in a separate packet with their base (ab2/B2): agency 8 vs 8, contradictions
0 vs 1.

Readings:
- With n=24-32 per arm, a difference of 3-4 is noise. The first set's apparent 1B win (2 vs 7) doesn't hold up.
- 2A is the only consistent effect across both sets: menus fall from 6 to 2, and earlier from 4 to 0. Its sheet
  half may be what backfires, so block 2 tests the menu half alone (2C).

## Decisions for Jake
- **D1. When the PC dies in a test game:**
  - (a) Start a new character (recommended): every story stays one continuous timeline the readers can check.
  - (b) Let the DM rewind if the player asks, as cleric2 did.
  - (c) Stop that game.

  In the real game, the DM rewinding at a player's request is yours to rule on too.
- **D2. When a turn is flagged by the safeguards:**
  - (a) Retry the call once automatically, then report it (recommended: the flag comes and goes, and a probe fork
    recovered).
  - (b) Retry once on a different model.
  - (c) Leave it to the player to send their line again (now the default: the turn fails and nothing is shown).
- **D3. The notebook is written and never read:**
  - (a) Accept it: notes come to the DM every turn anyway.
  - (b) Test a code change that gives the DM more of an entry's facts in the per-turn notes when the player's line
    names it (recommended for block 2; code gives facts, never orders).
  - (c) More prompt wording: it was tried twice, with no calls.

## Next (block 2, rounds 61-120)
- Same games and code, prompt unchanged. Check before play that bard2 continues (the safeguard flag).
- Ideas to screen:
  - menus: 2C, the menu half of 2A; and a second wording;
  - contradictions: the notes change in D3(b), code behind a switch for the A/B.
- Budget (Jake, 2026-10-16): screening at 4 runs per round on 6 rounds, 8 runs only for a winner.
