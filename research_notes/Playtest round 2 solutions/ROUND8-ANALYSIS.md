# Round 8 analysis: traced causes and proposed fixes

Written 2026-10-10. The code under test is `milestone-1-playable` b6430a5, with round 7's fixes merged: R2-K and
specs 023–027. Runs were on Haiku, with a Sonnet player and 15 turns each:
- talker `20261010-013206`;
- fighter `-013226`;
- explorer `-013246`.

The offline long-horizon run had 0 engine errors.

**Evidence:** [round8-investigation/](round8-investigation/) holds I1 (narration), I2 (NPCs) and I3 (mechanics and
`/fix`). Each cause below was traced through saves, model packets and code.

**The headline finding.** In **9 of 9** traced wrong outputs, the narrator was *obeying* a wrong "must say" line
that code had written. None began as a model error (I2 §9).

## 1. What round 7's fixes achieved

| Target | Round 7 | Round 8 |
|---|---|---|
| Oracle "facts" about a person, contradicting the record | 4 of 4 | **0** (0 Oracle questions in 32 Reader calls) |
| Refusals stored as facts / refusal loops / speakers contradicting each other | 0 / 3 loops / — | **0 / 0 / 0** |
| Habit and look pushes | habit in 16 of 21 turns | **0 pushes**. The repeated notice and "hands hover" have new causes (T1, P6) |
| Rolled beats with no goal | 3 of 7 | **0 of 7** |
| Rolls with nothing at stake | 4 of 7 | **2 of 5**. One is legal; one is a loophole (P4) |
| First draft delivered / narrator calls per turn | 98% / 1.02 | 86% measured. **About 100% once 5 false blocks are removed** (T5) / 1.14 |
| Paragraphs kept / real pronoun drift | lost in 43 of 43 | **36 of 36 / none** |
| Clues delivered | 0 of 38 questions | **1** (19 clue calls, 1 false positive). Limited by T2 and P9 |
| Deals paid | untyped | **0 of 3 paid** (T3) |
| `/fix` (right / unclear / wrong) | 1 / 0 / 2 of 3 | **3 / 1 / 2 of 6** (T4) |
| Superior orders a subordinate | open question | not tested: it never came up |

**"Revisit if" notes that fired** (owner rule):
- DL-01-39: OFFER titles misread;
- DL-01-40: a missed deduction;
- DL-01-44: a Safe, sourceless frame rolled;
- DL-12-103, -109, -110 and -114, and DL-15-42: content and addressee;
- DL-12-116, -117 and -123: `/fix`;
- DL-12-122, in substance: a same-place scene re-described.

Not fired: DL-12-118 (willingness walls).

## 2. Root-cause families

### T1. The game re-guesses what the Reader already understood, then forces its guess
**In plain words.** The Reader understands your message well: who you're talking to, what you're reading, that a
shove is meant to intimidate. But several later parts of the code ignore that and guess again, by matching words. Then
they hand the narrator a "must say" line built on the guess, and the narrator obeys.

**From the playtest:**
- **Explorer** ([21], [27]): you asked the sellsword, but code picked Betric (the word "walk" matched), so Betric
  answered from across the room. 6 of 17 speech-only turns went to the wrong person.
- **Talker** ([24]–[26]): "Wait, friend!" to a woman fell back to "whoever spoke last", so Helian shouted answers
  from the gate three times.
- **Fighter** ([18]–[24]): your intimidating shove was rewritten into a *grapple*. The narrator was told
  "restrained", so it wrote "pinning him". A fight started, and the youth hit you with no visible roll.
- **Talker:** you read the gate log; code quoted the hire notice instead (5 of 5).

**Another example (made up).**
- You ask the baker "how much for the loaf?" while the guard behind you is "eating bread", and the *guard* answers.
- "I push past the bouncer to talk to the owner" becomes a grapple, the bouncer is pinned and a brawl starts.
- You read the letter in your pocket and get the poster on the wall read to you.

Anything the Reader understood can be overruled this way: who, what, which one, and why.

**The fix, plainly.**
- The Reader's understanding is passed through as typed facts: who each line is addressed to, what is being read, and
  which person is the target.
- Code stops re-guessing. "Must say" lines are written only from those typed facts.
- A shove to intimidate stays talk with menace.

*Retires:*
- addressee word-matching and the "last spoke with" fallback (`npc_layer.addressed`);
- the Talk → Grapple rewrite (`gate.covering_verb`);
- the reading-line guesses;
- casting by description (it made one youth into three people).

### T2. Leads still arrive half-written
**In plain words.** Round 7 gave job offers and notices their pay, place and people. The other kinds of lead ("a
closed cart came in", "banners in the hall") still have nothing behind them, and neither does the opening incident.
"What do I know?" lists names, but not what people told you.

**From the playtest.**
- Talker [19]–[23]: you asked what the gate log's entry says. Nothing owns its contents, so the game stalled ("waiting
  on your reading") and still marked the question answered.
- Fighter: the challenger in the sealed case is not the youth on stage.
- Explorer [19]–[21]: "what do I know" gave one line, ignoring the winter and the banners.

**Another example (made up).** A rumour says "the miller's daughter went missing". You ask around who saw her last,
and nobody can say anything definite. Your journal remembers "the miller's daughter", but not that the baker said she
left with a tinker. Any lead that isn't a job or a notice behaves like this.

**Why it recurred.** It is the pattern you warned about. The round-7 fix covered the lead kinds round 7 happened to
show, and our made-up cases were the same kinds. *Process fix:* breadth cases are now enumerated from every kind the
game's data has, not imagined (added to the skill).

**The fix, plainly.**
- Every lead and incident kind gets its key terms when made, held by the people and papers that would know.
- The incident's actor is the person on stage.
- The journal shows "what you were told", with who said it.

*Retires:* one-sentence leads; the false "answered"; the journal's name-only lookup.

### T3. NPC reactions run down a checklist without checking what's true now
**In plain words.** After your action, code walks each NPC through a fixed list of reactions. It never checks
whether they are alive, whether money changed hands, or who actually agreed.

**From the playtest.**
- Fighter [27]: the youth had just been killed, and he still got a must-say line, "flees or takes cover". So he "dives
  into the shadow like a hare, then is dead".
- Talker: you paid silvers for answers three times. Each payment was skipped because that talk also asked a question,
  and your coin stayed at 44.

**Another example (made up).**
- You knock out a guard, and the next turn he "shrugs and returns to his post".
- You buy the table a round while asking about the road, and no coin leaves your purse.
- A merchant you just robbed "greets you warmly".

**The fix, plainly.**
- Reactions check the state first: alive and conscious, present, what was paid and what was agreed.
- A payment is part of the action you took, not an item on the reaction checklist.

*Retires:* reactions gated by the checklist's order.

### T4. `/fix` can rebuild the odds, but not how your message was read
**In plain words.** `/fix` now investigates and rebuilds offers, which works: it was right in 3 of 6, up from 1 of 3.
But a rebuild only re-runs the odds. It can't change how your message was read: the goal, the target or the title.
After undoing a turn, it doesn't show the scene again. It also blames "the narration" for lines that code forced.

**From the playtest.**
- Fighter [19]–[21]: you complained that a shove was labelled "Persuade". `/fix` rebuilt it twice with the same
  result, then undid the turn. The undo created a third copy of the youth, and no scene was re-shown, so you were
  "redeclaring blind".

**Another example (made up).** "I asked the captain, not the clerk." `/fix` can't change who was addressed, so the
rebuilt answer comes from the clerk again.

**The fix, plainly.**
- A rebuild can re-read your message with the fix's note.
- An undo re-shows the scene.
- Its tools mark which lines code forced.
- Its rules crib adds "goal first" and what each skill does ("Push (trained)" is a Focus spend, not shoving).

*Retires:* the odds-only rebuild.

### T5. Two checks still force rewrites while almost never being right
**In plain words.** Only checks that are reliably right may force a rewrite (our principle). Two still do: the pronoun
check was right 0 of 3 times, and the repeat check 0–1 of 2. All 5 rewrites this round were false alarms.

**From the playtest.** All 5 revisions in round 8 were false blocks, so the real first-draft rate is about 100%, not
86%.

**Another example (made up).** "They argued by the well" about a crowd is flagged because the nearest named NPC is
he/him.

**The fix, plainly.**
- A check without a measured precision only logs, and code enforces that, so no check can quietly block again.

*Retires:* the two blocking checks.

## 3. Patches (one-off bugs)
- **P1.** The result line leaked an unlearned name ("Aurard de Morac dead"). The `name_known` check is skipped in
  `oof.changed_line`.
- **P2.** "Take the time" charges 20-minute intervals in free play. Three of them ended the scene on the hour and
  dropped the woman you were talking to ("Persuade the market square"). Charge minutes only.
- **P3.** An OFFER title for a persuade goal omits the act. Title it from the act ("Get her to tell you about the
  cart").
- **P4.** A Safe frame became "costly" because its cost cited a *narrated* detail ("scuffed binding"), so turning a
  page rolled. Only mechanical costs count.
- **P5.** The lead injection ignores the Director's pick and re-pushes a known hook.
- **P6.** Remove the mandatory "end by handing the moment back" line in every packet. Its slot drives the repeated
  closings ("hands hover"). This is your "stop pushing" rule, not tracking.
- **P7.** Apply "setting once" on a scene cut at the same place too (the room was re-described 4 of 9 times).
- **P8.** RESULT and Fate wording: "evidence as a no-roll success" and "no reroll".
- **P9.** One clue judgment per message: the question cap dropped Betric's clue before the clue check saw it.
- **P10.** Harness: the persona should see only new output. It sees the last 9,000 characters, which inflated "every
  reply" notes. This was round 6's F7 and never built.

## 4. Recommended order
1. **T1 + T3 together** (one spec: both live in the NPC response path). They cause 9 of 9 traced wrong outputs.
2. **T2 + P9** (leads and incidents with terms, the journal, clue routing), alongside 1.
3. **T4 + T5 + the remaining patches.**

## 5. Decisions
- **None new.** Every fix follows rulings you've already made: the Reader owns reading, code owns state, and only
  precise checks block.
- Still open from before: the superior's order to a subordinate. It never came up this round.
