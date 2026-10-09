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

### T1. The yes/no Oracle answers questions that something else already owns
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

### T2. The world promises content that nothing writes, and clues can't be reached
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

### T3. Code still writes story text the narrator repeats
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

### T4. One outcome is read three ways
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

### T5. Goal-first stops at the Reader
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

### T6. Rolls with nothing at stake
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

### T7. `/fix` can't see or change enough
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
