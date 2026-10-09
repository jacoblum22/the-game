# R7-I3: mechanics, OFFERs and `/fix` (round 7, ed51aa7)

Read-only trace of the saves `playtest-20261009-160602-talker`, `-160622-fighter` and `-160642-explorer`.
Transcript input `[N]` is `game_inputs.n = N+1`. A player note written at `[N]` describes the screen produced by `[N-1]`.

Input-to-turn map used below:
- fighter: [20]=turn.5, [21]=turn.6 (/fix), [22]=turn.7, [23]=turn.8, [24]=turn.9, [25]=turn.10, [26]=turn.11,
  [27]=turn.12 (/fix), [28]=turn.13;
- talker: [23]=turn.8, [27]=turn.12, [28]=turn.13, [29]=turn.14 (/fix);
- explorer: [25]=turn.10, [26]=turn.11, [27]=turn.12, [28]=turn.13.

## Summary: where the cause differs from the surface

1. **Neither the garbled modifier nor the impossible OFFER is a rendering or Framer bug at root. Both are Oracle
   facts.** In both cases the Reader asked a `fact_question` about the target's own state ("is not alert…",
   "can read…"). The blind World-Fact Oracle rolled a d100 on it and wrote a fact. The Framer then cited that fact
   as a −2 snag, because its prompt says "Every fitting hindering fact is a snag". Spec 021's "garbled claims
   4/31 → 0/23" measured testimony only. This path goes through `turn.py:_fiction_questions` and `oof.fact_short`,
   which spec 021 never touched.
2. **The Oracle contradicted the record.** Belie Greenwort is a "scribe and teacher of letters" who holds
   `lic.lang.letters` (entity_created, seq 222). The Oracle rolled 08 on "likely" and wrote `fact.113` "can read …
   = false". The narrator was then given `R2 MUST: … the answer is no` and had her say she can't read. The soldier
   is the mirror case: she has no Letters licence, the Oracle's question hit the free-question cap (seq 477), and
   she read the list.
3. **`/fix` could not have changed anything.** `rerender` only scans `frame_committed`, and both OFFERs were
   still pending. Even if it had found them, it re-runs the same `fact_short` on the same fact. The Fixer's
   `entity` tool shows no role and no licences, so it endorsed the false fact. No proposal kind can re-frame a
   pending OFFER.
4. **The rolls that shouldn't happen come mainly from rule 01.4.4 "take the time" never having been built.**
   `necessity()` never evaluates COSTLY. `take_the_time`, `good_idea` and `certain_with_cost` are named in
   `pipeline.py:45` but are assigned nowhere. 4 of 7 OFFERs were Safe frames, and Safe frames always roll.
5. **The near miss that "gave nothing" broke rule 01.9.3.** Its price ("he turns the round down") is the negation
   of the goal. The code guards against this only for holds.

---

## 1. Garbled odds modifier (fighter [20]→[21], turn.5)

**What the player saw:** `Chance: … 65% (Endurance +2, trained (thievery) +2, is not not alert to a hand reaching
into his coat pocket while h −2)`. The narration above it said "He does not feel it."

**Model calls (turn.5):**
- Reader (row 13): `fact_questions: [{subject: npc.magby_applefoot, predicate: "is not alert to a hand reaching into
  his coat pocket while he faces the fire", odds_rung: unlikely}]`. The beat is `verb.sneak / take`.
- Oracle (code, seq 411): d100 46 on "unlikely" gives **no**. `fact.106` is written with predicate
  `is_not_alert_to_a_hand_reaching_into_his_coat_pocket_while_h` (truncated at 60 characters, mid-word) and
  `value=false`. Meaning: Magby IS alert.
- Framer (row 14): `obstacle: opposed (Magby)` **and** `snags: ["fact.106"]`. Magby's awareness is counted twice:
  once as his opposed defense and once as a −2 snag.
- Narrator (row 15), THIS MESSAGE: `R2 MUST: question "is not alert … fire": the answer is no`. The narrator
  inverted the double negative ("He does not feel it. His shoulders stay exactly as they were."). The prose
  therefore contradicts the snag on the same screen.

**Code path:**
- `engine/dm/turn.py:421` runs `pred = ids.slug(q.predicate)[:60]`, which truncates mid-word.
- `engine/dm/oof.py:234` (`fact_short`): for `value False`, "is …" becomes "is not …". The predicate already
  contains "not", so the result is "is not not". There is no subject, because the subject is dropped for
  non-testimony facts.
- `oof.py:_breakdown` (256–270) prints `fact_short(...) −2`.

**Root cause.** The scaffolding, not the model:
- the Reader is allowed to ask the Oracle about the very thing the roll decides (the target's awareness);
- the predicate is stored as a negated, truncated slug, and the display negates it again;
- the narrator line hands a double negative to the model.

Anti-patterns: **code authoring narrative truth** (an Oracle d100 decides Magby's alertness), **over-triggering**
("every fitting hindering fact is a snag", `framer.md:26`) and **wrong context** (a slug as a label).

**Frequency.**
- Round 7 showed 2 snag labels in OFFER Chance lines. Both are Oracle facts, and both are wrong in substance
  (§1 and §2). 1 of the 2 is garbled in form.
- 3 of the 8 Oracle-written facts in play were truncated at 60 characters (fact.102, .106, .112).
- 4 of the 8 Oracle answers were about the beat's own target or outcome, and all 4 contradicted something:

| Fact | Question | Contradicted by |
|---|---|---|
| fact.103 | Magby "will name the place" = yes | narration: he refused, after a `tbl.npc_action` "escalates" roll |
| fact.106 | Magby "is not alert" = no | narration: "He does not feel it" |
| fact.113 | Belie "can read" = no | her `lic.lang.letters` |
| explorer fact.105 | Morga "is willing" = no | certain-talk `R2 MUST: Morga agrees` in the same packet (turn.4) |

**Structural fix.** The Reader's fact questions are for the world (things and places: "is there a rope"), never
for the beat's target person. Code drops any `fact_question` whose subject is the beat's target, or a person
present. That person's awareness, ability and willingness are the roll's or the NPC step's business; 12.10.8
`speech_owns` already does this for "knows" questions. Where a question survives, store the predicate positive
and whole (no `[:60]`), with a label sentence written at creation ("Magby is alert"), and let `fact_short` print
that label.
- **Retires:** fact_short's slug-negation branch for Oracle facts; snags authored by d100; double-negative
  `R MUST` lines.

## 2. OFFER contradicting the fiction (fighter [26], turn.11)

**What the player saw:** Belie says "I can't read that. Not a line of it." Directly below, the screen shows
`[OFFER] Persuade Belie Greenwort. 35% (Presence +2, practised +1, can not read the writing on the delivery list
−2) … If it fails: … she takes the request as a breach of trust`.

**Model calls (turn.11):**
- Reader (row 23): beat `talk / persuade_to`, intent "Belie Greenwort reads the delivery list for Balak", plus
  `fact_questions: [{npc.belie_greenwort, "can read the writing on the delivery list", likely}]`. The Reader's
  view showed `role: scribe and teacher of letters`. Choosing "likely" rather than "certain" is the model
  following `reader.md` §2: "between two: the one less favourable to the player's hope".
- Oracle (seq 452–453): d100 08 on "likely" (yes needs 26 or more) gives **no**. `fact.113 = false`. The Oracle
  call sees only the predicate and the odds. It never consults the sheet for licences:
  `oracle.py:130` short-circuits possession verbs (`_POSSESS`) only.
- Framer (row 24): given `role: scribe and teacher of letters` and `fact.113 … = False`, it frames a 35% Persuade
  with `snags: ["fact.113"]`. `framer.md` has no "the goal is impossible" exit. Its only zero-reach exit,
  `reach_two_factors`, which `pipeline.py:512` turns into a G4, is phrased in terms of potency, quality and scale.
- Narrator (row 25): `R2 MUST: question "can read the writing on the delivery list": the answer is no`. Belie's
  refusal is therefore **code-authored**.

**Turn record:** `beats: []` (paused), `said: [Belie: "Mark me, I can't read that…"]`, `claim_log: []`, one draft
with no verdicts. The record contains no check that the pending OFFER's goal is still possible after the
Oracle's write.

**Root cause.** Three things combine:
- a blind Oracle overrode a fact already on the sheet;
- the code asks the Oracle *before* framing, about the frame's own premise;
- the Framer's instruction turns any negating fact into a −2, not a refusal.

"Breach of trust" is a separate, honest Framer choice: `asks: asks_breach`, reading the employer's stolen list.

Anti-patterns: **blind model call** (the Oracle and the Reader lack NPC licences; the narrator view lists PC
licences only), **code authoring narrative truth**, **over-triggering** (snag rule).

**Frequency:** 1 of 7 OFFERs. Its mirror (the soldier reads without Letters) affected 1 certain-talk grant.

**Structural fix.**
1. Abilities on the sheet answer capability questions. Extend `ask_oracle` step 1/3 from possession to licences
   ("can read" maps to `lic.lang.letters`), and put NPC licences on the people cards the Reader and Framer see.
2. After framing, code checks the typed goal against the record. If a fact on record says the target cannot do
   the asked act, the beat is G4 before any OFFER (as `zero_reach` already does), with the fact cited.
   `framer.md` gains "a fact that makes the goal impossible is not a snag: set `blocks`".
- **Retires:** OFFERs whose snag negates their own goal; "every fitting hindering fact is a snag" as written.

## 3. `/fix` admitted it but changed nothing

### How a report runs now
1. `dispute.settle_dispute` calls `fixer.investigate`: Sonnet, with up to 3 tool calls per answer and a budget of
   6.
2. Each proposal goes through `_apply`.
3. The open pause is left untouched, so the game re-shows the same OFFER.

### Fighter dsp.1 (turn.6, about turn.5)
- **Tools used:** `turn(turn.6)`, `turn(turn.5)` and `recompute(turn.6)`. The last returned "no roll was
  committed", because it targeted the wrong turn and the frame was only pending.
- **Response (row 17):** verdict `player_right`, proposal `rerender turn.5`, with this reply:
  > "The record holds a note that Magby is not alert … The −2 is the ordinary penalty for picking a pocket with
  > Magby standing awake."

  Both halves are wrong. `fact.106 = false` means he IS alert, and the −2 is that Oracle fact, not an "ordinary
  penalty". Sonnet misread the double-negative slug the `turn` tool printed
  (`is_not_alert_…_while_h = false`).
- **Code:** `dispute.py:_rerender` (308–325) iterates only `frame_committed`. The OFFER was a `pause_opened`, so
  it returned "" and `_apply` reported "did" with nothing to show. Had it found the frame, it calls the same
  `_breakdown → fact_short` on the same fact and prints the same garble. Round 6 I3 §5 already warned of this:
  "Re-rendering … prints the same garble, because the garble is the stored fact." The disputes log says "explain
  (upheld) · writes none", while the correction event says `done_kinds: ["rerender"]`.
- **Grade: wrong.** The complaint was understood and acknowledged, but the explanation is false and there was no
  repair. The garble was re-shown at [21].

### Fighter dsp.2 (turn.12, about turn.11)
- **Tools used:** `turn(turn.12)`, `turn(turn.11)` and `entity(npc.belie_greenwort)`.
- **What the `entity` tool returned:** "sheet: state fresh · conditions none · holding nothing" plus 3 facts. It
  showed no role and no licences (`fixer.py:_entity_tool` 218–240 and `sheet` 106–129 print quantities,
  conditions and held items only).
- **Response (row 27):** verdict `partly`, `explain` only:
  > "the record has her as unable to read the writing … no amount of persuading can make her read it … you can
  > withdraw it at no cost".
- **What would have repaired it:** `remove_fact fact.113`, or `take_back turn.11`, which would void both the
  Oracle fact and the pending OFFER. The first needs the sheet the tool hides. The second is barred by the prompt
  ("only for a turn the player never had a fair chance at").
- **No proposal kind can re-frame or withdraw a pending OFFER** (`PROPOSALS`, `fixer.py:27`).
- **Grade: wrong.** The surface mismatch was diagnosed correctly, and the reply was clear and safe ("nothing
  spent"). But it ratified a false fact, which the narrator reused at [28] ("papers I can't read"), and left the
  broken OFFER in place.

### Talker dsp.1 (turn.14, about turn.12)
- **Tools used:** `entity`, `turn` and `said`. The record says he/him. The reply says plainly that the "they"
  lines were the slip, and ends with a `Now:` line.
- **Grade: right.**
- **Side cause the Fixer could not address:** the narrator packet's code-authored text primes "they":
  - `packet.py:484`: "the character does not know their name: call them "…" (… add how they look …) … until the
    record says they gave it";
  - the scene line: "call them "the sellsword between contracts", as every other screen does";
  - the SPEAKER CARD: "…a hedge only if they are cautious…".

  Narrator passages used they/them for the sellsword in turns 9–11, all-"they" despite `pronouns: he/him` on three
  lines of the same packet.

### Totals
**1 right, 0 right-but-unclear, 2 wrong**, out of 3 /fix reports in 3 runs. Round 6 had 1 right, 6 unclear and
8 wrong out of 15.
- **What spec 022 improved:** Sonnet understood all 3 complaints correctly. All 3 replies carried `Now:`, and no
  complaint text was pinned.
- **What remains:** every failure is the Fixer's tools or proposal set, not the model:
  - **(a)** `entity` hides role, licences and competence;
  - **(b)** `rerender` is a no-op by construction: pending frames are skipped, and the render is deterministic
    from the same fact;
  - **(c)** no kind re-frames a pending OFFER;
  - **(d)** the `turn` tool prints raw negated slugs.

**Structural fix.**
- Make the `entity` tool print the people card (role, licences, competence, refusals).
- Replace `rerender` with `reframe`: withdraw the open OFFER for free, apply any fact correction, re-run gate and
  frame, and show the new OFFER. For a pending, unrolled turn, allow `take_back` without the "never had a fair
  chance" bar, since nothing was spent.
- **Retires:** `rerender`, and the `_rerender` scan of committed frames.

## 4. Rolls that shouldn't happen

### Explorer [27]→[28] (turn.12/13): sit and listen
- **Reader (row 30):** `verb.observe`, `change.kind: none`, `purpose: own_change`.
- **Framer (row 31):** `tier easy`, `stakes.source: "none"` (Safe), `secret: true` (`framer.md`: "Unsure: true"),
  threatened cost `cost.time`.
- **Necessity:** `engine/resolve/necessity.py:85–93` returns `uncertain_and_costly` for every beat except a
  fallback, plain reading, certain talk, looking around the room you are in, or an already-true change.
  **COSTLY (01.4.1 decision 2) is never computed**, and 01.4.4 take the time is not implemented. `grep` finds
  `take_the_time` only in `pipeline.py:45`'s tuple.
- **Result:** after framing, only `trivial_class` and `_rides` skip the roll (`pipeline.py:517–527`). The roll
  was d20 1, a critical failure (seq 643), shown as `[RESULT] hidden check made.` That wording is 12.15.3's
  literal text (`oof.py:659`). It also hides the cost "a few minutes pass".
- **Seated?** The narration stopped before the PC sat ("The stool waits at your side"), as a pause requires. The
  player's "already seated" was their own declaration.

### Talker [23] (turn.8): the cask
- **Reader (row 20):** one beat, `verb.help`, `change none`, `purpose: serves_another_act`. The goal it served
  was SPEECH ("What have you heard about Morri…").
- **Folding:** `reader.py:_fold_methods` (65–91) folds a method only into a following *beat*. With a speech goal
  there is none, so the gesture stood alone.
- **Framer (row 21):** Safe and easy, so it auto-committed (`OFFER — auto`) and rolled a failure.
- **The answer was SPEECH and never depended on the roll,** so "failed but answered fully" is structurally
  correct. The roll itself was needless.

### Explorer [25] (turn.10): persuasion after a half-answer
- **Reader (row 26):** typed the ask as `persuade_to` with `speech: true`, but chose `verb.help`.
- **Certainty check:** `necessity.certain_talk` requires `verb == "verb.talk"`, so the 15.3.10 check never ran,
  and the Framer was not asked for `request_size`.
- **Inconsistency:** the same kind of ask at turn.4 (`verb.talk`) was certain (no roll; the NPC decided).
- **Pre-OFFER narration:** the SPEECH part ("are they resting in the house") was answered before the OFFER, as
  12.2.2 allows. That is the "half-answer" the player saw.

### Counts
- **4 of 7 OFFERs were Safe frames:** talker cask, talker round, explorer listen, and fighter read (a G3
  fallback, which always rolls by rule).
- **3 of 5 committed rolls were Safe:** cask, round and listen. Under 01.4.1 and 01.4.4 those three would be
  "take the time" or simply narrated.
- **1 of 7 OFFERs was a method roll (the cask).**

### Structural fix
After framing, apply 01.4.1 COSTLY in code. A frame whose `stakes.source` is `none` (Safe), with no clock
listening and a tier below Very hard, and which is not a fallback, takes the `take_the_time` reason: success at
Standard reach, twice the time, no OFFER. Key `certain_talk` on the typed change (`persuade_to`/`learn`,
`speech`, a present target), not on the verb label.
- **Retires:** most `OFFER — auto` rolls, needless secret Observes (and the "hidden check made" line for them),
  near misses on Safe frames, and the verb-label branch of the certainty test.

## 5. Odds and costs that feel off (fighter [24]→[25], turn.9)

**Frame (seq 447):**
- `wits +3, practised +1 = +4`; `tier hard` plus the G3 improvising `+5`, giving DC 25. That needs 21, so only a
  natural 20 succeeds (5%).
- Critical failure 55%. On a Safe frame its cost is S1, "a nuisance".

**Model call:** the Framer's THIS MESSAGE (row 21) carried the **un-rescoped intent**, "learn what the delivery
list says, including its most dangerous place and the road to it". Only the method was the fallback's ("pick out
numerals, seals…"). The Framer rated the whole reading job "hard", and code added the fallback's +5 on top. The
illiteracy is counted twice.

**Label:** `oof.py:283` prints "failing badly is likelier: 55%". The 01.6.13 long-shot label is correct by rule,
but on a Safe frame "badly" costs only S1, so the warning reads as alarm about a nuisance.

**Fix.**
- On an accepted fallback, THIS MESSAGE's intent is the fallback's own scope (what numerals and seals can tell),
  so the tier is judged on that.
- The REDIRECT computes and shows the fallback's odds before "Try it anyway".
- On Safe frames, the label names the severity ("failing badly (a nuisance): 55%").
- **Retires:** double-counted fallback difficulty.

## 6. Opaque result wording

| Where | Text | Source | Cause |
|---|---|---|---|
| explorer [28] | `[RESULT] hidden check made.` | `oof.py:659`, verbatim from rule 12.15.3 | The rule's text, plus a roll that should not have happened (§4). It also drops the paid time cost. |
| explorer [26] | `Now: Agreed by Morga Embershield: a smaller part of it (Morga lets Haley sit near the refugees and listen…)` | `resolve/change.py:320` | Code-authored "a smaller part of it (<the whole act>)" contradicts itself. Reach was limited only because the Framer set `reach_one_factor: true` with no factor cited (`framer.md:36`: "(tie: true)"). The narrator then invented the missing part ("Not the telling of it, though"). |
| talker [23] | `(Might +0, practised +1)` | `oof.py:_breakdown` 256–270 | Every attribute is printed even at +0, and generic `competence_tag: deed` is printed as "practised". The breakdown appeared in 5 of the 7 OFFERs. |
| talker [28] | accepted near miss: "Succeed, and pay: he turns the round down and the offer goes nowhere with him" | `oof.near_miss_choices` 584–594; `frame.py:837` | See below. |

**Talker [28] in detail:**
- **How the price was chosen.** A Safe frame keeps its alternate cost back until "go big" (`frame.py:837`). So
  the success-at-cost price is the threatened `cost.closed_door` on the same NPC, which negates the goal. This
  violates 01.9.3: "The cost may never negate the success."
- **The only guard is for holds.** `_UNDO`/`_sets_hold` (`frame.py`) protects holds and nothing else.
- **There was no typed goal to protect.** The Reader typed `change.kind: none` (row 30), so success applied
  nothing and printed no `Now:`. The record has `degree failure`, `success_at_cost_taken true` and a closed-door
  fact (seq 530, 533). The player paid 1 coin and got a refusal.
- **Frequency:** 1 of 1 near misses.
- **The garbled title.** "Talk to a coin on the table; cups called for" happens because `goal_line`
  (`oof.py:322`) prefers `change.description` over `beat.target` when the change is `none`.

**Fixes:**
- Generalise the 01.9.3 check: drop any SaC price whose cost menu reverses the typed goal against the same
  target (closed_door against the person of a `persuade_to`/`learn`/offer).
- Require a typed goal on every rolled beat (`change: none` was 3 of 7 OFFERs).
- Write `agreed` as the NPC's actual grant, not a code paraphrase.
- Set reach to limited only with a cited factor.
- Drop +0 terms and the generic "practised".
- **Retires:** the "a smaller part of it" template and the description-first title.

## 7. Ordering: stealing the list before learning you can't read (fighter [19]→[24])

- **[19], turn.4:** "I read the list over his shoulder. What's the name…". The Reader (row 10) folded the reading
  into one `verb.talk / learn` beat ("Several questions to one person are one beat"; the goal-first "what only
  serves a goal is its method").
- **Why no gate fired:** `gate.reads_writing` (`resolve/gate.py:354–364`) gates letters only for `verb.observe`,
  so the literacy check never ran.
- **What the narrator wrote instead:** "the crowded lines of the list come clear in the firelight".
- **The same turn's contradiction:** the Oracle's `fact.103` said Magby "will name the place" (yes), but a
  `tbl.npc_action` "escalates" roll had him refuse. These are two code-authored truths that contradict each
  other. This one is outside this area; it is noted for I2.
- **When the gate finally fired:** only at [23], when reading was its own Observe beat. By then the list had been
  stolen.
- **Fix:** gate letters on the method's words and the target's writing, whatever the verb (keyed on the typed
  `learn` from an item with writing). A reading method folded into a Talk beat then still meets the Letters gate,
  and the REDIRECT comes at [19].
- **Retires:** the verb-only gate key.

## 8. Round-6 targets, measured

| Target | Round 7 |
|---|---|
| Goal vs method rolls | 18 Reader outputs had beats, every one a single beat. 1 of 7 OFFERs rolled a method (the cask, with a SPEECH goal). There was 1 fold that lost a gate (§7). |
| "Then:" quality | **Not exercised**: 0 multi-beat messages in 3 runs, and 0 "Then:" lines. |
| Holds and foe hits while held | **None occurred**. There was no combat; the "fighter" played a thief. |
| Coin deductions | 1 deduction (talker turn.13, coin 44 → 43, "a price the method pays"), correct. 1 open payment with no amount: the soldier's `agreed` fact.116 says "in return for payment", with no sum, no debt and no deduction (fighter [31]: "price was never named"). This is **mechanics stored as text** again. The talker's two spoken offers ("buy the carters a round", "buy you a cup") were offers only and correctly cost nothing. |
| `Now:` lines | /fix: 3 of 3. RESULT: 2 of 5 committed rolls (the fighter's take, the explorer's agreed; the second has garbled wording, §6). The talker's round (`change none`) showed `Changed: coin` but no `Now:`. The secret roll showed nothing. |
| Garbled Chance labels | 1 of 2 snag labels garbled, and 2 of 2 wrong in substance (both Oracle facts). Not 0. |

## 9. Shared causes

- **A. The Reader's fact questions go to a blind Oracle about the beat's own target, before the frame.**
  Accounts for §1, §2, the misreadings in §3 dsp.1 and dsp.2, explorer turn.4 (two contradictory MUST lines:
  "Morga agrees" and "willing: no"), and fighter turn.4. 4 of 4 such answers contradicted the record, the roll or
  the narration. This is the round-6 "refusal stored as fact → snag" pattern, entering through a door spec 021
  did not close.
- **B. The 01.4.1 COSTLY / 01.4.4 take-the-time test was never implemented** (spec 007 FR-004 scoped it out).
  Accounts for §4, the secret RESULT in §6, and the near miss in §6.
- **C. Rolled beats with `change: none`** (3 of 7 OFFERs). They give no `Now:`, no protection of the success
  from its price, and a title built from a description.
- **D. The Fixer's tools are narrower than the record.** The entity card has no role or licences, `rerender`
  cannot change output, and no pending OFFER can be re-framed.
- **E. Verb labels gate behaviour that should key on the typed goal:** `certain_talk` (verb.talk), the literacy
  gate (verb.observe), and secret frames.
- **F. Code-authored instruction text primes the model:** "the answer is no" to a negated question; "call them"
  for a he/him NPC.

## 10. Anti-pattern checklist

| Anti-pattern | Instances |
|---|---|
| Code authoring narrative truth | Oracle d100 decides Belie's literacy and Magby's alertness; "a smaller part of it (…)"; certain-talk "agrees" beside an Oracle "no" |
| Over-triggering | "every fitting hindering fact is a snag"; Safe frames always roll; `secret` "Unsure: true"; reach "(tie: true)" |
| Blind model calls | the Oracle; the Fixer's `entity` tool; Reader and Framer people cards without licences |
| Wrong context | Framer intent not rescoped for the fallback; `turn` tool's negated slugs |
| Mechanics stored as text | the soldier's payment |
| Atomisation | not seen; the opposite happened (an over-fold, §7) |
| Low-precision blocking | not seen |
| Mandatory texture | not seen |
| Test traps | spec 021's garble metric covered testimony only |

No fix had been proposed. The structural fix for each cause, and what it retires, is given in its section above.
