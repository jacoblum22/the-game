# Experiment results: one DM model with tools versus the pipeline

Run 2026-10-10 on commit bb35b77 (`milestone-1-playable`). Engine on Haiku, player on Sonnet, `--quick-setup`, 15 turns. Three personas (talker, fighter, explorer) were run once per arm, nine runs in all. Not committed.

## Verdict (plain words)
The cost question has a clear answer. One DM model with tools used about a third of the tokens and about 0.4x the model time per turn of today's pipeline (14.5k vs 45.4k tokens in per turn; 13.5 s vs 35.4 s). That is far inside the "no more than about 1.5x" limit; it is cheaper, not dearer. The quality question has no clear answer yet.

On the counts the tools arms did slightly better. They had fewer contradictions with the record (5 and 3 against 10 for the pipeline) and fewer `/fix` repairs (1 and 2 against 5). They also had no wrong speakers and no state corruption beyond two small slips. Voices were good, and NPC moods were respected: closed NPCs refused, and a priced NPC asked for a price.

But the prototype is thinner than the pipeline in ways the counts do not show:
- No time passes, so one run said "afternoon" at hour 0.
- Nothing NPCs say is written to the PC's knowledge, so the journal is thin.
- There was one dead-end turn (a promised roll that never appeared).
- Fights have no counter-strikes.
- Prose-only people cannot be targeted.

The data are three runs per arm, in different random worlds each time, and almost no costly asks came up, so the "pushover" measure could not discriminate. By the decision rule: the cost gate passes by a wide margin, the quality gate is "promising, not clear". My recommendation is not to switch yet. Fix the cheap gaps below, then run a second head-to-head that includes the seeded NPC scenes (`evals/npc_agency.py`, spec 028, not in this branch).

## Arm x measure (3 persona runs per arm; counted by hand with the rules below)
A = pipeline. B = dm-tools, secrets hidden. C = dm-tools, secrets visible.

| Measure | A | B | C |
|---|---|---|---|
| Wrong speaker | 0 | 0 | 0 |
| Contradictions with the record or earlier narration | 10 (5 confirmed by the engine's own `/fix`) | 5 (1 confirmed) | 3 (1 confirmed) |
| Pushover (costly ask granted with no reason) | 0 counted | 0 counted (2 logged ceiling violations; 0 or 1 on re-check) | 0 counted (0 logged in the persona runs) |
| Clue facts the PC learned (case nodes + pointers) | 3 (1 node, 2 pointers) | 1 (1 node) | 6 (3 nodes, 3 pointers) |
| Secret leaks | not measurable (no audit in the pipeline) | 0 | 0 real (2 flagged, both false: the NPC's name plus the word "matter") |
| Needless rolls | 1 (auto-roll to "put down a purse") | 0 | 0 |
| Under-rolled fights (stakes resolved in prose) | 0 | 1 (plus 1 dead-end turn) | 1 |
| State errors | 1 (a "good while" passes for a glance; reversed by `/fix`) | 0 | 2 (bread and broth the PC never owned; a knife made with `new_item` instead of moved) |
| Repetition (4-gram motifs in 3 or more turns, names excluded) | 11 | 6 | 6 |
| Player-reported problems / real (my reading of the notes) | 32 / 21 | 23 / 12 | 25 / 11 |
| `/fix` reports | 5 | 1 | 2 |
| Model calls per engine turn | 3.12 | 1.71 | 1.98 |
| Tokens in / out per engine turn | 45.4k / 6.3k | 14.5k / 1.8k | 15.6k / 2.0k |
| Model latency per engine turn, mean (median, p90) | 35.4 s (31.0, 54.1) | 13.5 s (10.9, 21.8) | 15.2 s (13.5, 25.3) |
| Run wall time, three runs (includes the Sonnet player) | 11.2 / 12.7 / 10.5 min | 6.1 / 4.7 / 5.9 min | 7.7 / 5.1 / 5.9 min |

Counting rules, the same for every arm:
- **Wrong speaker:** an absent or dead person acts, or a present person answers a question put to someone else.
- **Contradiction:** narration contradicts the save (pronouns, item, time of day, presence, a recorded pointer) or earlier narration.
- **Needless roll:** an OFFER or roll where nothing was at stake.
- **State error:** coin, an item, a condition or a time cost with no source in the record.
- **Repetition:** a word 4-gram recurring in three or more turns, measured on prose paragraphs only.
- **Player problems:** I counted the notes in `findings.jsonl` that complain about something, then checked each against the transcript to see if it was real.

Pushover could not be measured fairly: the persona runs had almost no costly asks. The A column has no mood or ceiling log, so it was judged from transcripts only.

## Evidence for the counted items (brief; `[n]` is the player input number)
- **A contradictions (10).**
  - talker: [19] "it is her you want" for a he/him NPC (the engine's fix confirmed it); [18] the narration sends the PC to Kaarik while the recorded pointer is Greyby's Tower; [29] "tonight" in a morning scene.
  - fighter: [18] purse and boots "taken" though the record shows no transfer; [19] an "officer" who is not present; [22] "bare feet" again after the fix.
  - explorer: [17] the dead rider's hand moves; [20] "a street runs toward Goldcross" while in Goldcross; [21] the satchel's contents are in the record but never in the text; [31] a stray "the settle sits close to the fire".
- **B contradictions (5).**
  - talker: [27] "Kazain has not come down from the stairs" when he never went (fix confirmed); [19] "you asked loudly enough" after the PC murmured.
  - fighter: [19] "afternoon" while the record's hour is 0; [23] "You are hidden from view" with the cost "you are noticed" and prose saying the beast heard.
  - explorer: [28] Grimga "kept this name back" after saying he does not know it.
- **C contradictions (3).**
  - talker: [24] Tobbo says "take the bowl up to her" after the PC delivered it (fix confirmed).
  - fighter: Milby says he never opened the letter but knows it "has a count in it".
  - explorer: [28] and [31] "lamplight" in a grey morning.
- **Moods held (B and C).**
  - Closed NPCs refused (Heldis, Vorak, in the secrets runs).
  - A priced NPC priced the ask (Grimga asked for the book; Gerius asked for a signature).
- **Ceiling violations.** The two B-talker violations were Valas at turn 7 (price paid earlier, so it is arguable) and turn 15 ("partial" against "partial_or_refuse", not a real one).
- **Secrets arm.** The visible secrets did not leak. Milby, who is the secret recipient, acted keen to get the letter, which is the intended effect.
- **Dead-end turn.** B-fighter [26]: the narration ends "you have one chance" with no OFFER, and the next Enter said "Nothing is waiting".
- **Quality in the fights.**
  - A-fighter's `/fix` rounds were costly in play: the purse and boots, "bare feet", and a patron killed by default lethal harm.
  - The tools arms had a garbled "Changed: your opponent worn" line, shown twice in C-fighter.
- **Clue routing.** C-talker [18]: Ivette pointed to the Crypt of Oakmere when asked about "a face she knew". The clue judgment mapped the question to the wrong node. The pipeline shares this graph, so this is not specific to the tools arm.

## Cost and latency (sources)
- Calls, tokens and latency come from each save's `model_calls` rows. Tokens in include cache tokens. Latency is the sum of the model calls in a turn. The helper script was `xstats.py`/`xagg.py`, kept in the scratchpad (not committed).
- Counts cover the 40 to 41 engine turns per arm after the opening. The Sonnet `/fix` calls are excluded: 20 in A, 3 in B, 7 in C.
- Pipeline roles per turn in A: reader 35, narrator 40, framer 21, clue 17, director 9 and others over 40 turns. In B and C the one DM role does it all (about 1.7 to 2.0 calls, including the CLUE judgment).
- Cost per turn is about 0.3x in tokens and 0.4x in model time. No dollar figures were taken.
- All three arms ran at the same time per persona, so machine load was comparable. Wall times include the Sonnet player.
- **Scripted line runs (`longhorizon.py --mode scripted --lines 60 --model claude`):**
  - B and C finished with 0 engine errors. The harness flags `--model claude` and `--engine` worked.
  - Per engine turn: B 1.68 calls, 14.6k tokens in, 12.5 s; C 1.69 calls, 14.1k tokens in, 12.4 s. Both ran about 15 minutes.
  - **Arm A (pipeline) was skipped.** It had not finished after 46 minutes, so I stopped it on the owner's request. There is no scripted baseline.
  - The harness's pipeline-specific measures do not apply to dm-tools turns (it reports 2 to 3 "narrated" turns).
  - B: 8 leak flags, all false positives (the NPC's name plus common words); 5 sentences flipped Octette Vasac to "her" against the record's he/him; 1 refused `travel` (an unreachable place); 12 `recall` and 5 `state` calls (the tools do get used on long runs).
  - C: 0 leaks; 3 refused tool calls, all aimed at people who exist only in prose ("the carter at the well"); 1 logged ceiling violation (a "partial" grant against "partial_or_refuse", not a real one).
- The NPC-agency scenes (`evals/npc_agency.py`) are not in this branch, so they were not run.

## Qualitative read (and one good, one bad line per arm)
- **A, pipeline.** The prose is richer and the fight loop is the most complete: auto-rolls, the opponent striking back, and a status screen. The cost is slow turns, many repairs, and repeated beats (the patron "spends itself on the air" in 4 turns). The `/fix` loop did what it was for. It was often needed.
  - Good: "Fists, then, and not a coin of it... Nobody steps in, and nobody talks you out of it after."
  - Bad: the rider "dead" while "one gloved hand curls slowly across the stones toward the satchel".
- **B, tools, hidden.** Quick, and NPC voices are distinct and in character. It felt like a competent, slightly short-memory human DM, and it was weakest where the code had to hold a world together: stale time, a missing roll, a drifting detail.
  - Good: Valas, "Forty crowns, and a man of mine who took a crossbow bolt for his trouble and got nothing for it but a grave."
  - Bad: Magby, "Kazain has not yet come down from the stairs", when he never went.
- **C, tools, secrets visible.** The best-feeling scenes of the nine, with firm NPCs (a refusal with a reason, a priced favour) and the most clue progress. It also kept NPCs stonewalling and pointing at each other, which the players called "circling".
  - Good: Heldis, "Keep your ale, priest. I've been bought for silence before, and it never ended well for the one who bought me."
  - Bad: Tobbo sends the PC to take the bowl up to Agnes after the PC already did.

## Prototype gaps that hurt B and C
Cheap to fix:
- `propose_roll` and `mood` refuse targets that exist only in prose ("the beast", "the lead guard", "the carter at the well"). Auto-create a minimal NPC, or accept the DM's name.
- A narration that promises a roll but offers none (B-fighter [26]). Check for it in code and re-prompt once.
- Things NPCs tell the PC are not written to the PC's knowledge, so the journal is thin. Only clues and a `fact` call write there. Auto-record told names and statements.
- No time advance on ordinary turns. The record stayed at hour 0 while the narration moved to "afternoon". Add a small clock tick or tell the DM the time.
- No pronoun or presence check. A one-line code check against the record would have caught Octette's he/him flip and the "officer" who was absent.
- The leak audit overlaps on names plus common words (10 false flags). Drop the name tokens from the overlap.
- The OFFER title and framing: "Hurt the beast's lunge" and the stealth framing of a charge, where the DM's own words would do.
- Items arrive by assertion (bread, a knife). Route item moves through `give_item`.

Structural:
- No opposing turn in fights. The pipeline's NPC strikes back with harm each exchange; here only a failed roll on the PC hurts.
- No world step, Director or clocks, so scenes drift and nothing happens off-screen.
- No second-model check of the passage (Checker, Reader). Self-consistency rests on the one model.
- Case-graph routing (self-pointers, wrong-node pointers) belongs to spec 029 and affects both engines.
- The ceiling log depends on the DM listing its own `asks`.

## Recommendation against the decision rule
- **Cost (at most about 1.5x):** passed with a wide margin: 0.3x tokens and 0.4x time.
- **Clear quality win:** not shown. The tools arms were better on contradictions and `/fix` load and on NPC firmness, and worse on time, the journal and the fight loop. The sample is small, and the dice and worlds differed between runs.
- **Recommendation:** do not move to the new design yet. Treat it as a strong candidate. Fix the cheap gaps, add a code-side pronoun and presence check, and run a second head-to-head with the NPC-agency scenes and a mood-and-cost probe that guarantees costly asks. If the tools arm then holds its lead on contradictions and gaps stay small at about a third of the cost, the signal to move is there.

## Transcript files (evals/playtests/) by arm
- **A, pipeline**
  - `20261010-152037-claude-talker.md` and `.findings.jsonl`
  - `20261010-153203-claude-fighter.md` and `.findings.jsonl`
  - `20261010-154511-claude-explorer.md` and `.findings.jsonl`
- **B, dm-tools, secrets hidden**
  - `20261010-152037-claude-talker-dm-tools.md`
  - `20261010-153123-claude-fighter-dm-tools.md`
  - `20261010-153642-claude-explorer-dm-tools.md`
- **C, dm-tools, secrets visible**
  - `20261010-152037-claude-talker-dm-tools-secrets.md`
  - `20261010-153123-claude-fighter-dm-tools-secrets.md`
  - `20261010-153642-claude-explorer-dm-tools-secrets.md`

The saves are in `saves/playtest-<same stamp>-<persona>[-dm-tools[-secrets]].db`. The scripted-run stores for B and C were kept in the session scratchpad only.
