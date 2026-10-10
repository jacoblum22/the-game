# Round 7 analysis: traced causes and structural fixes

Written 2026-10-09. Code under test: `milestone-1-playable` ed51aa7, with the round-6 fixes merged (R2-J, specs
019–022). Runs, all on Haiku (engine) with a Sonnet player, 15 turns each: talker `20261009-160602`, fighter
`20261009-160622` and explorer `20261009-160642`. The offline long-horizon run had 0 engine errors.

**Evidence:** three read-only traces in [round7-investigation/](round7-investigation/):
- I1: narration and text;
- I2: NPCs and dialogue;
- I3: mechanics, OFFERs and `/fix`.

Every cause below was traced through saves, model packets and responses, and code before any fix was written.

## 1. What the round-6 fixes achieved

| Target | Round 6 | Round 7 | Source |
|---|---|---|---|
| Stacked quotes | 21 in 10 turns | 1 (caused by joining sentences with spaces, see P1) | I1 |
| Echoed player lines / duplicated answers | 6 / 2 | 0 / 0 | I1 |
| First draft delivered / narrator calls per turn | 64% / 1.57 | 98% / 1.02 | I1 |
| Refusals stored as facts | 4 | 0 | I2 |
| Garbled testimony claims | 4 of 30 | 0 (but a different path garbles odds labels, T1) | I2, I3 |
| Testimony settled | 64% of turns | 3 in 35 turns (1 of 3 correct) | I2 |
| Found-clue repeats | several | 0, but **no clue was delivered at all** (T2) | I2 |
| Coin deducted when paid | never | 1 of 1 typed payment; 1 untyped deal with no price (T2) | I3 |
| `Now:` after a `/fix` restore | missing | 3 of 3 | I3 |
| `/fix` | 1 right / 6 unclear / 8 wrong of 15 | 1 right / 0 unclear / 2 wrong of 3; both misses caused by the tools (T7) | I3 |
| Goal rolled instead of method | 0 of 5 traced | every beat a single goal; 1 fold lost a gate (T5) | I3 |
| Holds, "Then:" lines | broken | not exercised: no fight and no multi-beat message in these runs | I3 |

**Measurement note:** the offline run's lower first-draft rate (64.9%) and novelty (0.64) come from the offline
stub. They predate spec 019. Live novelty-4 is 0.95–0.97, and novelty-4 cannot see a repeated motif (I1 §6).

## 2. Root-cause families

Each family has a plain summary, the playtest example, a made-up example that shows how far the problem reaches, and the fix in plain words. The traced evidence follows.

### T1. The game flips a coin for things it already knows
**In plain words.** When you act on a person, the game sometimes asks a yes/no dice roll (the "Oracle")
about that same person: "Is he paying attention?", "Can she read?", "Will he tell you?". The answer is rolled
instead of looked up, so it can contradict what the game already knows about them. The odds screen then counts the
rolled answer against you as a penalty.

**From the playtest** (fighter, inputs 21–27). Belie is the town scribe: her record says she can read. Before the
fighter asked her about the stolen list, a roll decided she can't. She said "I can't read a line of it", and the
next offer screen asked him to *persuade her to read it*, with her illiteracy as a −2. Earlier, a roll said Magby
"is not alert" to a pickpocket; the label came out as "is not not alert … while h −2".

**Another example (made up, to show the reach).** You ask the blacksmith to mend your sword. A roll decides "the
smith can't work iron", so he shrugs at his own anvil, and your offer to pay him shows "can't work iron −2". Or an
old friend you saved last week: a roll on "is she willing to help?" comes up no, and she turns you away. Anything
the game already knows about a person can be overwritten by a coin flip this way: their skills, their attitude,
what they'd agree to.

**The fix, plainly.** Every question has one owner. *Is the person willing?* → their attitude to you. *Can they do
it?* → their record and skills. *Something nobody has decided yet* → the content makers (T2). The coin flip only
answers open questions about the world ("is it raining at the pass?"), and a rolled answer is never a penalty on the
odds.

**The evidence:**
**Cause, traced** (I3 §1–2, §9 A; I2 §1, §7 B):
- Before framing, the Reader's fact questions about the beat's own target ("is he alert?", "can she read?",
  "will he name the place?") go to the blind d100 Oracle. Its answer is written as a fact.
- The Framer then cites that fact as a −2 snag.
- All 4 such answers in these runs contradicted something:
  - Belie is a scribe holding Letters, but the roll made her illiterate;
  - the Oracle said Magby "will name the place" while his NPC row refused;
  - in 4 records an agree line and a refuse line both stand.
- The odds label is the fact's slug, cut at 60 characters (`turn.py:421`) and negated again (`oof.py:234`).

**Symptoms it explains:**
- the garbled odds line ("is not not alert … while h −2");
- the OFFER to persuade Belie to read what she just said she can't;
- some of the dead-end NPCs;
- `/fix` dispute 1's explanation.

**Structural fix: one owner per question.**
- An addressed NPC's will goes to willingness.
- Their ability goes to their stored licences and competences.
- Content nobody has written goes to its generator (see T2), never to a yes/no roll.
- The Oracle answers only open questions about the world, never about the beat's own target.
- An Oracle answer is never a snag; 01.6.8 already allows only mechanical hindrances.

**Retires:** pre-frame Oracle questions about the target, the `_KNOWS_Q` word list, Oracle booleans standing in for
content, and slug labels in the odds breakdown.

### T2. The story promises things nobody ever writes, and clues can't be found
**In plain words.** When a lead says "someone is hiring" or "refugees came in", the game creates the hook but
not its details: what the job is, what it pays, where it is, who the refugees are and what happened to them. So the
people who should know have nothing to say, and they dodge. Separately, a clue is handed over only when your words
happen to share a word with the clue's description, which almost never happens.

**From the playtest.** The fighter chased "a delivery list that names the most dangerous place". For three turns
Magby kept saying "the name's written there", because no place was ever written. In the explorer's game, Morga was
meant to know the refugees' story; no story existed, the refugees never appeared in the room, and Roswen sent the
player back to Morga in a loop. Across all three games: 38 questions, 0 clues delivered.

**Another example (made up).** A notice says "Reward for the missing ferryman". You ask the ferry-keeper how much,
who posted it, where he was last seen. Nobody has decided any of it, so everyone hedges ("you'd have to ask
around"). You ask his widow "Did he have enemies?" She holds the clue "he owed the toll-keeper money", but your
question shares no word with "owed" or "toll-keeper", so she's never given it to say. Any mystery stalls the same
way, however well the player asks.

**The fix, plainly.** When a hook is made, also write its key facts (the job, the pay, the place, who's involved)
and give them to the people who'd know. Let the director bring in a group like "the carters". Decide whether a
question is about a clue by its meaning, not shared words (decision 2). Give deals a real price.

**The evidence:**
**Cause, traced** (I2 §1, §3–5, §7 A, C, D, E):
- Nothing generates the hook's terms. A lead says "someone is hiring" or "refugees came in", but no step writes the
  job, the pay, the place or the refugees' story. The fighter's "delivery list" grew from an activity line, and
  three yes/no Oracle answers then said it names "the worst place", which was never written.
- The Director can cast only a random new walk-on (`director.py:120`), so the carters and the refugees never appear.
- Clues are routed to an NPC by word overlap. In 38 questions, 0 clues were delivered. In the talker run, "signed"
  matched "a **sign** of the rite" and misrouted an answer line.
- Deals have no price field, so "worth your while" is never priced or charged.

**Symptoms it explains:** Magby's endless "the name's written there"; the Morga → Roswen → Morga loop; refugees and
carters absent; the price never named; part of the "wall" feeling; no clue progress in any run.

**Structural fix:**
- Lead and incident builders author the concrete terms when they create the hook (what, where, the pay, the people).
  They are written as unsealed knowledge on the offerer's card, so a willing NPC has something to say.
- The Director can cast a description ("the carters") present in a scene.
- Clue delivery is decided by judgment, not word overlap. See decision D2.
- Deals carry a typed price, so paying is a typed change.

**Retires:** Oracle booleans for content, word-overlap case routing (`case_about`'s one-word hit), random walk-ons
for a stated purpose, and the regex price parsed from Framer prose.

### T3. The game hands the narrator ready-made sentences, and it repeats them
**In plain words.** Some of what the narrator gets isn't facts but finished sentences and labels. Some
character notes, like a habit, are shown every single turn as if they always happen. The narrator tries to use
what it's given, so it keeps repeating them.

**From the playtest.** Kerric counted on his fingers in nearly every reply: his habit was shown in 16 of 21 turns
where he spoke. "Branine Brightford brought the word" was in every turn's input, and it finally leaked into the
explorer's temple scene from nowhere. The sellsword's notes said "call them…" although he's a he, so the narrator
drifted to "they".

**Another example (made up).** An innkeeper's note says "wipes the bar with a rag". Over ten turns she wipes the
bar ten times, even while her inn is on fire. A guild is given as "the officer of The Order of the Grey Hand", and
every mention repeats that exact clumsy phrase. Any fixed text we feed every turn becomes a verbal tic.

**The fix, plainly.** Give facts, not sentences. Offer a look or habit once per scene, then mark it as used. Write
habits as "sometimes". Templates use the person's real pronouns.

**The evidence:**
**Cause, traced** (I1 §1, §5; I2 §2, §5, §7 D, G):
- "X brought the word" is a code sentence built from the case's first clue holder, and it is in **44 of 44**
  narrator packets.
- Faction labels ("the officer of The faithful of Alett") are given to be repeated verbatim.
- Code text for unnamed NPCs says "call them" or "their morning work" even when the store says he/him. That is the
  code half of the sellsword's "they → he" drift. The store and every packet said he/him, so `/fix` was right.
- Every packet prints each NPC's look and habit as raw data. Habits are worded as always-on ("counts on his
  fingers"), the rule's "once per scene" never reaches the model, and freshness marks never cover looks or habits.
  The habit was shown in 16 of 21 speaking turns.

**Symptoms it explains:** the repeated finger-counting, kettle, burn scar and curling list corner (all with one
narrator call per turn, so not repairs); "Branine Brightford brought the word" from nowhere; the template slip; the
pronoun drift.

**Structural fix:**
- Facts, not sentences, for seeded narrative: the reporter, the leads and the faction come as data, and templates use
  the NPC's own pronouns.
- Texture is offered once per scene and tracked by code: a look or habit is offered, marked used, and then dropped
  for the scene; habits are phrased as occasional; closing images join the freshness marks.

**Retires:** `incident_line` in every SCENE SETTING, the verbatim faction label, raw `voice`/`detail` in the view, and
pronoun-neutral template strings.

### T4. "Succeed at a cost" gets read as a failure
**In plain words.** When a roll just misses, you can choose to succeed anyway at a price. Three parts of the
code look only at the raw roll ("failed") and ignore that choice, so the person still refuses after you've paid.
And before you choose, the narrator is already told "it failed", so it writes ahead of your decision.

**From the playtest** (talker, inputs 27–28). The talker offered to buy the sellsword a round, rolled a near miss,
and chose "succeed and pay". He paid a coin, and the sellsword turned the round down anyway. Before the choice, the
narration already had the sellsword reaching for the coin.

**Another example (made up).** You barely miss picking a lock and choose "succeed, but the guard hears you". The
lock opens, but the guard's reaction is computed as if you'd failed, so the door is described as still locked while
the guard comes running. Any near miss you accept can be undone this way.

**The fix, plainly.** One place decides how a roll turned out, and everything else asks it. A roll still waiting for
your choice isn't shown to the narrator as decided.

**The evidence:**
**Cause, traced** (I1 §3; I2 §7 F):
- When the player takes "succeed at a cost", three places check only the raw degree: `npc_layer.py:570`,
  `answer.py:271` and `scene_state.py:160`. They read the result as a failure and voice a refusal.
- A paused beat is already printed to the narrator as "result: failure, a near miss" before the player chooses.

**Symptoms it explains:**
- talker [28], where the narration ran ahead of the choice;
- the accepted near miss that turned into a refusal.

**Structural fix:**
- One outcome function, the effective degree, used everywhere.
- A paused beat is unresolved in the record until the choice is made.

**Retires:** degree-only checks, and "a near miss" as narrated result.

### T5. The "main goal first" fix stops halfway
**In plain words.** Round 6 taught the game to read "grab him and demand the key" as one goal: the demand.
But other parts still look at the *type* of action, or at nothing. The "can you read this?" check, the offer's
title and the rule that a price can't undo your win don't follow the goal.

**From the playtest** (fighter, input 19; talker, input 27). The fighter wrote "I read the list over his shoulder
and ask him the name". That became one talking action, so the reading check never ran (it only runs on "look"
actions), and he stole the list before learning he can't read. Three of seven offers recorded no goal at all, so
one title came out as "Talk to a coin on the table", and the near miss's price was the goal itself ("he turns you
down").

**Another example (made up).** "I sweet-talk the clerk and sneak a look at the ledger." The ledger is folded into
the talk, the reading check never fires, and a character who can't read reads the accounts fluently. Or "I shoulder
past the guard to reach the door" is recorded with no goal: you succeed, and nothing changes.

**The fix, plainly.** Every rolled action records its goal. Checks, titles and the "a price can't undo your win"
rule follow the goal, not the action type. A fallback ("just pick out the numbers") is judged on its own size.

**The evidence:**
**Cause, traced** (I3 §5–7, §9 C, E):
- Spec 020 folds methods into goals, but downstream code still keys on verb labels:
  - the literacy gate checks only `verb.observe`, so reading folded into a Talk beat met no gate, and the list was
    stolen before the "you can't read" moment;
  - `certain_talk` and secret frames are also keyed on verb labels.
- 3 of 7 rolled OFFERs had no typed goal (`change: none`), so:
  - the title came from a description ("Talk to a coin on the table");
  - no `Now:` was printed;
  - success had nothing to protect, and the near miss was priced with the goal's own refusal. That breaks 01.9.3; the
    code guards only holds.
- An accepted fallback re-sent the *whole* intent to the Framer, so its difficulty was counted twice (the 5% long
  shot).

**Symptoms it explains:**
- the theft-before-reading order;
- the flat near miss;
- the garbled title;
- the 5% shot with 55% "badly" for a nuisance.

**Structural fix:**
- Every rolled beat has a typed goal.
- Gates, titles and success protection key on the goal, not the verb: Letters on any `learn` from writing.
- The 01.9.3 check covers any price that reverses the goal against the same person.
- A fallback is framed on its own scope.

**Retires:** the verb-only gate keys, rolled `change: none`, description-first titles, and double-counted fallback
difficulty.

### T6. You roll for things with nothing at stake
**In plain words.** The rules say that when nothing bad can happen, you just take the time: no roll. That rule
was never built, so any action with some difficulty gets a dice screen.

**From the playtest** (explorer, inputs 25–29). Already seated with Morga, the explorer asked to sit and listen.
They got an offer screen ("you can't judge how hard this is") and then an opaque "hidden check made". 4 of the 7
offers in these games had nothing at stake.

**Another example (made up).** Searching your own empty room for a dropped ring, with no hurry: a 40% roll, and on
a failure you simply search again. Practising on a training dummy, or reading a book you own on a quiet evening, all
cost a roll and a screen for nothing.

**The fix, plainly.** Build the "take the time" rule: no risk, no roll, just say how long it takes.

**The evidence:**
**Cause, traced** (I3 §4, §9 B): rule 01.4.4 ("take the time": no roll when nothing is at stake) was scoped out of
spec 007 and never built. 4 of 7 OFFERs had nothing at stake, for example sitting down to listen while already
seated, or persuading someone who has already half-agreed.

**Symptoms it explains:**
- the needless rolls;
- the opaque "[RESULT] hidden check made";
- some of the "why do I need to roll?".

**Structural fix:** implement the COSTLY / take-the-time test in `necessity()`. No stakes means no roll, only the
time spent.

**Retires:** rolling every gated beat, and secret-check lines for beats with nothing at stake.

### T7. `/fix` can't see enough to fix things
**In plain words.** The new `/fix` investigates before acting, which works. But its tools don't show an NPC's
skills, it can only re-show results that were already rolled, and it can't rebuild an offer that's still waiting
for you.

**From the playtest** (fighter, inputs 27–28). The fighter reported "Belie can't read, but you want me to persuade
her to read". `/fix` agreed, but it couldn't see Belie's reading skill and couldn't rebuild the offer, so it showed
the same broken offer again.

**Another example (made up).** You report "the guard should know me, I'm a captain of the watch". `/fix` can see
the guard's attitude but not your rank, so it can only apologise and explain. Every complaint that hinges on a
skill, a rank, or an offer still on screen hits the same wall.

**The fix, plainly.** The tools read the whole record, skills included. Add "rebuild a waiting offer". Give the
fixer a short rules crib: holds, scene labels are never penalties, refusals are never facts.

**The evidence:**
**Cause, traced** (I3 §3):
- The Fixer's entity tool hides an NPC's role and licences, so it couldn't see that Belie can read.
- `rerender` looks only at rolled frames.
- No proposal can re-frame a pending OFFER.

Score: 1 right, 0 unclear, 2 wrong of 3. All 3 were tool limits, not Sonnet.

**Symptoms it explains:** "admitted it was wrong, then re-showed the same broken offer".

**Structural fix:**
- The tools read the whole record, licences included.
- Add a proposal to re-frame a pending OFFER.
- Add the short mechanics guidance block spec 022 asked for: holds, labels never penalties, refusals never facts, the
  Stagger rule.

**Retires:** the rerender-only-rolled limit.

## 3. Patches (one-off bugs)
- **P1. Deliver the passage as written.** `narration._text` joins the sentence split with spaces, which drops
  paragraph breaks in 43 of 43 deliveries. That caused the misattributed speech in explorer [20]/[21] (the model's
  side list was right) and the round's one stacked quote.
- **P2. OFFER wording:**
  - drop "+0" terms and the generic "practised";
  - on a Safe frame, say what failing badly costs ("failing badly (a nuisance): 55%");
  - set reach to limited only with a cited factor;
  - retire the "a smaller part of it (…)" template.
- **P3.** No willingness line when the player only greets or thanks; a spec-021 hand-off, still live.
- **P4.** `narrator._withheld`'s suffix goes only on refusals.
- **P5.** Small text fixes: "the any posted notice"; the notice signature separator; pronoun-check precision in
  narration tags (its one hit this round was wrong); the `READING` precision.
- **P6.** Demote offline narration metrics, or improve the offline stub's vocabulary, so they stop misleading.

## 4. Recommended order
1. **T1 + T5** (adjudication correctness: who answers, and the goal carried through). These are medium-sized, high
   impact, and remove the impossible OFFERs and the garbled odds.
2. **T3 + T4** (narration: facts not sentences, texture once per scene, one outcome function) plus P1.
3. **T6** (no roll without stakes), plus P2.
4. **T2** (authored hook terms, casting descriptions, clue delivery). The largest, and it needs D1 and D2 first.
5. **T7** (`/fix` tools), after T1, since T1 removes most of what it had to explain.

## 5. Decisions for the owner
- **D1. "What does the job pay?" when nothing in the game has decided it.**
  - A: when a hook is created, generators also decide its key terms (job, place, pay, who's involved).
  - B: the NPC answers in character, and it stays testimony until the player acts on it.
  - C: today's yes/no coin flips.

  *Recommended:* A for a hook's key terms, B for everything else. C is retired either way.
- **D2. How a clue gets delivered when you ask the right person.**
  - A: a small model call judges whether your question is about the clue that person holds; code then delivers it,
    so the secret stays in code.
  - B: the clue sits on the holder's card, the model reveals it when it fits, and code records it from the speech.
  - C: keep word matching, tightened.

  *Recommended:* A.
- **D3. An NPC refuses one question and then answers the next one fully.**
  - A: their willingness holds for the scene unless something changes it.
  - B: re-roll per topic, as today.
  - C: per topic, but a refusal always points to someone who would know.

  *Recommended:* A, with C's pointer when they refuse.

## 6. Owner follow-up (2026-10-09): history traces and T2 research

The owner approved T1 and T4. They asked for T5 to be explained more, which was done in the conversation, using the
same four-part format. They also asked why T3, T6 and T7 recurred when each was supposedly fixed, and how other
systems handle details nobody has decided (T2). Reports: `round7-investigation/R7-H1-repetition-history.md`,
`R7-H2-rolls-fix-history.md` and `R7-R1-improvised-details.md`.

- **T3, same cause, never fixed in general.** Each earlier fix covered one surface:
  - place looks (spec 018);
  - activities (013);
  - lead lines (020);
  - speech openers (P-078).

  People's looks and habits, "X brought the word" and the labels sit on surfaces no fix reached. There is also a
  regression: spec 009 B replaced the P-030 word scan with usage marks, but the seed never stores looks and habits
  where the marks can see them, so the marks fired 0 times in round 7. The rule 12.14.11 exempts "an NPC's recorded
  habit" as a callback, and the refusal line requires the habit (`npc_layer.py:491`). Two recorded "revisit if"
  conditions were met and not acted on: DL-12-99, and handoff §4 on speech habits.

  *Fix, this time:* one offer-once-per-scene gate for all standing texture, marked used when code offers it rather
  than by matching prose, with the habit exemptions removed. Keep a cheap repeated-image backstop that covers
  closings. Add a test that flags any packet line repeated word for word across a scene.
- **T6, a regression, not a rule never built.** Before spec 007, the Reader could mark a beat "take the time" and
  the roll was skipped: round-1 saves hold 65 no-roll successes. Spec 007 removed the field and chose not to compute
  "can failure cost anything?" in code; there have been 0 no-roll successes in 13 saves since. P-024 (the door) was
  fixed at the screen (auto-commit), not the roll. The explorer's half-answered persuasion is different: spec 018's
  "already agreed" check needs 60% word overlap both ways, so it missed the narrower ask.

  *Fix, this time:* code computes "no stakes source → no roll". "Already agreed" is judged against the typed goal,
  not by word overlap.
- **T7, measured on the wrong set.** Spec 022's 10/3/2 was scored on the disputes its prompt was tuned on. The
  held-out set scored 4/1/2 of 7. Only 1 of the 15 disputes concerned an open offer, and the scorer marked a wrong
  re-render right, because it checks only the outcome class. Since spec 014, complaints about an open offer only
  ever get an explanation.

  *Fix, this time:* the missing tools (licences, re-framing a waiting offer), scored on held-out live complaints that
  include open offers, with a scorer that checks the actual repaired output.
- **Shared lesson.** Each fix was fitted to the last round's cases and accepted on those cases alone. Proposed
  process change: every fix's gate includes made-up breadth cases (as in the families' "another example") plus a
  held-out set, and each round checks the recorded "revisit if" conditions.
- **T2 research.**
  - Tabletop practice (Apocalypse World, Blades, Ironsworn, the Three Clue Rule, GUMSHOE) improvises flavour around a
    small written core. AI game-masters report the same failure modes we would risk: narrated money then spent
    (Hidden Door), contradiction rates of 40–68% (NCP-Bench), and leaked secrets.
  - Our rules already forbid coin from narration (economy AI-6), and seeded notices already roll their issuer and
    contact.
  - *Recommended (Option 2):* code decides a hook's money, destination, issuer and people when the hook is created.
    The model improvises everything else as testimony. Each speaker sees what others said on the topic, a price
    outside a hook uses the price band, and a place first heard in speech gets a real site when the player travels
    there.
