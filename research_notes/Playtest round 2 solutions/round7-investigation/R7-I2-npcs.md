# R7-I2: NPCs, dialogue and testimony, traced to cause

Read-only investigation, 2026-10-09. Code under test: `milestone-1-playable` at ed51aa7 (spec 020, 021 and 022 merged).
Saves: `playtest-20261009-160602-talker`, `-160622-fighter`, `-160642-explorer` (17 turn rows each). Scratch scripts
are outside the repo. Mapping: transcript input `[N]` = `turn.(N-15)`. A player note at `[N]` describes the screen
produced by `[N-1]`.

## Summary: where the cause differs from the surface reading

| # | Symptom | It looked like | Traced cause |
|---|---|---|---|
| 1a | Magby never says the job, the pay or the place (fighter [18–20]) | An evasive NPC / a held secret | **The content does not exist.** No generator authors the offer's terms. The "delivery list" is a T1a prop the narrator made out of the activity line "checking a delivery against a list". Three yes/no **Oracle** answers then asserted that the list names a worst place, but no step ever produced that place. The one refusal (turn.4) is a **table roll at Neutral** on a path that skips the "Neutral answers" rule, and it sits next to an Oracle "yes, he will name it". |
| 1b | Sellsword dodges (talker [26–27]) | Model choice | Turn.10: a willingness roll (d10=1, Wary). Turn.13: **success at a cost read as failure** (the `degree` field), so the record says both "never a refusal" and "refuses". Turn.9: a **misrouted code answer line** ("signed" matched the case subject "a **sign** of the rite"). |
| 1c | Morga won't produce the refugees; Roswen loops (explorer [21–25]) | Morga holding a secret | **The refugees are not an entity**, and they hold no clue placement. The Director's `new_npc` cast a random labourer instead. The Oracle answered "no" to *Morga's willingness*, while the same record says "Morga agrees". A want row then added a "they do not give…" suffix after a success. Roswen's refusal is a legitimate dice wall; the loop back to Morga is the model's redirect to the only other person in the room. |
| 1d | "Two NPCs in a row refused" (fighter [30]) | Over-strict willingness | Belie: **the Oracle overrode a stored licence**. She holds `lic.lang.letters` and is a "scribe and teacher of letters", but the Oracle rolled "can read: no" (d100=8 at *likely*). The officer: a legitimate dice wall (Wary, d10=2). |
| 2 | they → he flip (talker [28–29]) | A he slip | The store held **he/him** and every packet showed it 3–4 times. The **"they" lines were the drift** (5 of 6 passages), and `/fix` was right to say so. Contributing factors: code text binding *they/their* to the unnamed label, the narrator copying its own RECENT EXCHANGES, and a pronoun check that cannot see "they". |
| 3 | Price never named (fighter [31]; talker [24]–[25]) | Model vagueness | **No price exists to name.** An offer with no amount on a no-roll Talk has no Framer frame, so there is no consequence for `change.price()` to parse. The Reader made no beat for "Let me buy you a cup". |
| 4 | Promised people absent (carters, refugees) | Narration omission | **The Director cannot cast a description.** `next_scene.cast:["new_npc"]` → `meet_npc(role=None)` gives a random walk-on (a sellsword, a labourer). Testimony settlement wrote the refugees' location to `world`, where it affects nothing. Talker: the settlement trigger chose the **wrong said record**. |
| 5 | "Branine Brightford brought the word" at the temple (explorer [31]) | The lead or the Director | **The case.** `incident.incident_line` (incident.py:44) renders the **core clue holder** of node 1 as "X brought the word". `packet.py:399-401` puts it in **every** SCENE SETTING (44 of 44 narrator packets). The same line made Magby the employer in the fighter run. |

**Shared causes** (each feeds more than one symptom):
- **(A) Content void**: 1a, 1c, 3, 4.
- **(B) Two authorities on one NPC's will:** the Oracle against the NPC layer (1a, 1c, 1d).
- **(C) A blind new-scene cast**: 1c, 4.
- **(D) `incident_line` in every packet**: 1a, 5.
- **(E) Low-precision case routing**: 1b, plus the held clues that were never delivered.

---

## 1. Evasive NPCs and dead ends

### 1a. Fighter: Magby (turn.2–4; notes [18]–[20]) and the soldier (turn.16)

**What the player saw.**
- "And the work pays well. Better than anything else…" (no job, no amount).
- "The name's written there."
- Then: "Magby Applefoot will not read it out… That is all you will have from him this morning."
- At turn.16 the soldier, now willing, reads the list but still names no place: "That one's the worst of the lot."

**Where the list came from.** The opening packet's OPTIONAL MATERIAL had "Magby Applefoot is checking a delivery
against a list". That is `tbl.npc_activity` texture. The narrator wrote "a delivery list in his other hand", and
write-on-mention created `item.delivery_list` as T1a (events 351–354, source `mention`). The opening R2 line, "the
inciting incident: a powerful person offers the character work, coin and a warning. **Magby Applefoot brought the
word**", made Magby the employer. He taps the list: "There's work for you… There's a warning in it too."

**What the case actually holds** (`world.cases`, event 250):
- `case.incident.offer`. Its solution is sealed: **"who makes the offer: Tobby Applefoot"**. Magby holds the core
  placement (`inquiry`).
- Node 2 is "the way on: toward the hall", the room the player is already standing in.
- Nothing anywhere holds what the job is, what it pays, or a place.
- `thr.lead_1` points to `clk.bright_weald.rulers.goal` ("the Kingsholt Company of Merchants: corner the salt trade").
  No packet carries that clock.

**Model calls.**

| Turn | Call | Packet (THIS MESSAGE) | Response |
|---|---|---|---|
| 2 | reader #5 | — | `fact_questions:[{subject: magby, predicate: "the work pays well", odds: even}]` |
| 2 | narrator #6 | R1 MUST: question "the work pays well": **the answer is yes**; R2 MUST: Magby answers willingly (a plain question to a neutral listener). The SPEAKER CARD lists 3 seeded `knows` items (Pipwise, Wikbit ×2) and public news. **No job, no pay, no faction goal.** | "And the work pays well. Better than anything else…" |
| 3 | reader #7 | — | FQ `item.delivery_list` "names one place where the danger is worse than at the others", odds *likely* |
| 3 | narrator #9 | R3 MUST: **the answer is yes**; R4: Magby answers willingly. The view's only content about the list is `fact.102 … = True`. | "The name's written there." The narrator cannot invent a consequential place: GUIDANCE 12.14.13 T2 and "Do not invent … what someone knows". |
| 4 | reader #10 | — | FQ magby "**will name the place** on the list and say how to reach it" (*likely*) |
| 4 | world #11 | beat only | no motive engaged |
| 4 | narrator #12 | R2 MUST: question "will name the place…": **the answer is yes**. R3 MUST: Magby **refuses**, in their own voice (formal, speaks of themselves by name): ends the talk and turns away… | The narrator honours R3: "Magby Applefoot will not read it out" (the third-person self-reference comes from the `voice.habit`). |
| 16 | narrator #35/#36 | R2: the soldier answers willingly. The view still has only boolean facts about the list. | A tautological answer with no name. |

**Code paths.**
- `turn.py:_fiction_questions` (411–449) sends every Reader `fact_question` to `ask_oracle` as a yes/no. A "where"
  or "how much" question becomes a boolean, and the boolean then asserts that content exists (`fact.102`, `fact.112`)
  without creating it.
- `speech_owns` (turn.py:456, `_KNOWS_Q` regex at 452) only diverts "knows / heard / saw" predicates to the NPC.
  "will name…" goes to the Oracle, which **settles Magby's willingness**.
- The turn.4 refusal comes from the beat's approach, `lic.training.guile_streetwise`, which is not a "talk" approach.
  So `npc_layer._speech_only` (508) is false, and `respond` falls to branch (c), the table by standing (619–634):
  - `tbl.npc_action` d10=1 at standing 0 (reaction 2d6 = 2+6 = 8, Neutral; event 405), clamped to row 2;
  - `refuses = is_addressed and asked and row in REFUSING_ROWS` (634);
  - but `answer.willingness` (250–285) says **Neutral or warmer → willing** (15.3.10). The same NPC answered
    willingly in turns 2–3 by that path and refused in turn 4 by the other.

**Root cause.** Scaffolding, not model behaviour:
- (A) the "offer" incident and its lead carry no terms, and the Oracle's yes/no stands in for wh-answers;
- (D) "Magby brought the word" casts the core clue holder as the employer;
- (B) the Oracle settled the NPC's willingness, and the table path skipped the Neutral-answers rule.

The narrator's evasions are the correct reading of a packet with nothing in it. It is told not to invent consequential
places.

### 1b. Talker: the sellsword (turn.9–13; notes [25]–[28])

| Turn | Record line (narrator packet) | Source | What it did |
|---|---|---|---|
| 9 (#25) | R1 MUST: "the sellsword between contracts acts: **does not know what the omen shows, but Kerric Hartsmith would**" | `answer.ask` → `_route` → `case_about` (answer.py:211–230). `words.content("Have you signed with Morri's Wolves…")` = {**sign**, morri, thought, wolv}; the case subject words = {**sign**, rite}. A one-word hit at line 225. `_from_case` gives the non-holder's pointer and writes `fact.111 points_to…=kerric`. | A non-sequitur ("The seam? … Kerric Hartsmith would know"). It contradicts Kerric's own "Nobody in Shepfield can tell you what it is" (player note [25]). **Code-authored content, misrouted.** |
| 10 (#27) | R1 MUST: refuses to answer what you asked (wary toward you) | Reaction 1+4 = 5 → Wary (stance `indifferent`, so not bounded). `answer.willingness` → table d10=1 → `unwilling` (rng seq 31). | A legitimate dice wall. |
| 11 (#29) | R1 MUST: answers… willingly (wary toward you) | A new topic key, so a new willingness roll: d10=10 (seq 32). | Full answer (Hungry Meads, Lonely Barrow). |
| 13 (#33) | R1 MUST: "result: success at cost… **it worked: the one asked answers what was asked (never a refusal…)**"; R2 MUST: cost paid: "he turns the round down and the offer goes nowhere with him"; R3 MUST: "**refuses**… the talk did not move them (**failure**)" | `frame_resolved` (event 533): `"degree":"failure","near_miss":true,"success_at_cost_taken":true`. `npc_layer.py:570-574` reads `b.entry.degree` = failure and voices a refusal. The same misreading is at `answer.py:271` and `scene_state.py:160`. The Framer's cost form *is* the refusal. | The player chose "succeed and pay" and got a flat refusal: "Keep your round… Not for a cup, not for any coin." **A code bug** plus a cost whose form undoes the success. |

"Never gives a name": the player never asked it. The view line "never by a name … until the record says they gave
it" (P-095, `packet.py:484`) forbids volunteering a name. This is design, not a dodge. A warm or bought-a-drink NPC
introducing themselves would need a rule change.

### 1c. Explorer: Morga, Roswen and the refugees (turn.3–13; notes [19]–[25])

**The case** (`case.incident.refugees`):
- Node 1: "who leads the refugees: Vorri Stonebeard". Placements: **Branine** (core, the gate), Nibwen (hall), a
  notice (temple).
- Node 2: "the way on: toward The Lonely Keep". Placements: the place itself, Branmund (inn), an object (gate).
- **The refugees themselves are no entity and hold no placement.**

**Chain.**
1. **turn.2** (narrator #7). Branine is asked "what he knows about the refugees and where they are now". He is the
   core holder, but `case_about` sees {refuge} ∩ incident words = 1 < `need=2`, and the role coverage is 0.5 < 0.6.
   So the question is not routed; he answers "willingly" from nothing. The narrator invents, in his voice, "They're up
   at the healer's house" (T1b testimony, legitimate).
2. **turn.3**:
   - the move triggers settlement (testimony #9); the claim `{subject:"the refugees", predicate:"are up at",
     value:"the healer's house"}` becomes `fact.99` with **subject `world`**;
   - Director #11: `next_scene.cast:["new_npc"]`, agenda "Is the refugees' story true?";
   - `director.py:117-120` → `meet_npc(tctx, None, place)` → **the labourer (Roswen)**;
   - present: the labourer and Morga (her home). No refugees.
3. **turn.4** (narrator #14), a contradictory record:
   - R2 MUST: "Morga Embershield **agrees** to what was asked" (a trivial persuasion beat, no roll);
   - R3 MUST: question "**is willing to let Haley hear the refugees' story directly**": the answer is **no** (Oracle,
     even, d100=42; `speech_owns` misses "is willing");
   - the narrator reconciles them: "I'll say yes to telling you … But I'll not put them in front of you."
4. **turn.5**: Morga "willing", but no story is authored anywhere (the incident text is "a story nobody believes").
   "Worse than anything this gate has ever turned away." This is content void (A).
5. **turn.8** (narrator #24): Roswen refuses. Reaction 2+1 = 3 → Unfriendly; willingness d10=4 at −2 (rng 42–44). A
   legitimate dice wall. The narrator's redirect "Go and ask Morga" is model choice: she is the only other person
   present, and the prompt asks for a natural redirect. That made the loop.
6. **turn.10/11**:
   - the Oracle answers "the refugees are resting somewhere in the house: **yes, and chase a curse**". The extreme
     meaning words are appended raw at turn.py:446-447, and the narrator turned them into "Something's chasing them… a
     curse";
   - the persuasion succeeds (R2 "agrees"). The beat is `verb.help`, not talk, so the NPC layer also takes branch (b):
     want row 8, "gives part of what was asked";
   - `narrator._withheld` (narrator.py:126-145) appends "**they do not give the PC what was asked**" because the
     action starts with "acts on" (`WITHHOLDING`), even though row 8 is not a refusing row. Hence "Not the telling of
     it, though."
7. **turn.12/13**: "sit near the refugees": an observe beat with **target none** (no entity). A hidden roll, then a
   critical failure, and the refugees "move on". They are never seen.
8. **turn.13–16**:
   - Morga's narrator redirect is to Edys, who holds no placement;
   - Edys's greeting-only turn gets "replies, willingly", and she recites her card's `knows` items ("the watch answers
     to the faithful of Osard", "a new roof…"). This is the spec-021 hand-off, still open.

**Root cause.** Case or clue design:
- the incident's group is not instantiated;
- the one real holder (Branine) was asked directly but the word matcher did not route the question;
- (C) the blind new-scene cast;
- (B) Oracle willingness against the NPC layer, and the withholding suffix on a non-refusing row.

The model's only independent choice was the Roswen → Morga redirect.

### 1d. Fighter: "two NPCs in a row refused" ([30])

- **Belie, turn.11** (narrator #25): R2 MUST: question "can read the writing on the delivery list": the answer is
  **no** (Oracle *likely*, d100=8, event 453).
  - Her entity holds `lic.lang.letters`, and her role is "scribe and teacher of letters". The Reader packet showed the
    role (reader #23, line 25) and still chose *likely*.
  - `_fiction_questions` never consults the NPC's licences.
  - The "no" then became a −2 snag on a Persuade OFFER (the `/fix` at [27]).
- **The officer, turn.14** (#31): reaction 3+3 = 6 → Wary (stance `wary`); willingness d10=2 → `unwilling`
  (rng 30–32). A legitimate wall.

### Frequency (symptom 1)
NPC-response turns (a record line "X acts"): talker 12, fighter 7, explorer 10, **29 in total**.

| Withholding cause | Turns | Count |
|---|---|---|
| Code withholding line, legitimate dice (Wary/Unfriendly reaction + willingness d10) | talker t10, fighter t14, explorer t8 | 3 |
| Code withholding line, scaffolding-made | fighter t4 (table path at Neutral), talker t13 (degree misread), explorer t11 (suffix on want row 8) | 3 |
| Oracle "no" on an NPC's will or ability, contradicting the NPC layer or the store | explorer t4, fighter t11 | 2 |
| Willing, but the content does not exist | fighter t2 (no amount), t3, t16; explorer t5 | 4 |
| Misrouted code answer line | talker t9 | 1 |
| Card recital on a greeting | explorer t16 | 1 |
| **Total** | | **14 of 29 (48%)** |

- Of the 14, **3 are design-intended dice** and **0 are an unprompted model dodge**.
- **Contradictory records** (an agree / yes / "it worked" line plus a refuse / no line for the same NPC in one
  record): **4** (fighter t4, talker t13, explorer t4, explorer t11).
- Oracle questions about an addressed NPC's will or ability: **3 of 8** Oracle questions (38%).

---

## 2. Pronoun flip (talker [28]–[29])

**Store.** `npc.dilie_hayburrow` "the sellsword between contracts": `pronouns: he/him`, gender man, from the moment
of casting (turn.7).

**Every narrator packet** that included him (#19, 25, 27, 29, 32, 33) showed he/him in 3–4 places:
- the view's `pronouns: he/him`;
- "people here or named: the sellsword between contracts: he/him";
- the SPEAKER CARD header "(he/him)";
- SCENE SETTING "present: … (he/him, young (in their teens), …)".

**Prose** (6 passages with a pronoun for him):

| Turn | Pronoun used |
|---|---|
| t7 | "as **they** glance up" (first mention) |
| t9 | they |
| t10 | they |
| t11 | they |
| t12 | **he / his** (the only correct one) |
| t13 | they |

The `/fix` (fixer #34–35) checked the entity and said "the record has … he/him, so 'he' … correct and the 'they'
lines were the slip". That is **correct**.

**Why "they".** This is model drift, primed by scaffolding text:
1. Code strings bind *they/them/their* to the unnamed label:
   - `packet.py:484` "the character does not know their name: call **them** '…' (… how **they** look…)";
   - `packet.py:388` "call **them** '…'";
   - the activity line "the sellsword between contracts is going about **their** morning work" (from
     `oracles.yaml:2467`, `tbl.npc_activity`);
   - the age string "young (in **their** teens)".
2. Once t7 said "they", RECENT EXCHANGES carried 1, then 2, then 3 "they" passages verbatim. The model followed its
   own prose over the card.
3. The precision check `claims._pronoun_hit` only knows he/she (`_PRONOUN`, claims.py:1332). "They" for a he/him
   subject is invisible, so no redraft happened.
4. The upheld `/fix` writes nothing the narrator sees (021 skips `correction.*` on the card), so the drift could
   continue.

**Evidence quality.** This is n=1 and the evidence is a correlation. The farmer, the soldier and the officer are also
unnamed with "call them", and were narrated correctly. The sellsword is the **only** unnamed NPC whose activity line
pairs his label with "their". Kerric and Edys had the same activity string, but they are named and were narrated
correctly.

**Frequency.**
- Narrator voice: 1 of 20+ narrated NPCs; 5 of 6 passages for that NPC.
- Checkable `said` lines (021 analyzer): talker 1/6, fighter 0/1, explorer 0/3. The talker "flip" is a **false
  positive**: "a man … he" in Hssaoo's line. **True: 0/10.**

---

## 3. A price never named

- **Fighter turn.15** (reader #32; narrator #33):
  - the beat is `verb.talk`, `pressure: offer`, `player_quantity: null`, approach `guile_streetwise`, **no roll:
    trivial**;
  - with no frame there is no Framer, so there is no method consequence, so `change.price()` (change.py:232) parses
    nothing;
  - the record line is "the soldier off duty agrees to what was asked" (narrator.py:292);
  - the narrator, told not to invent counts, wrote "for the price you're talking about". No coin moved (coin 66
    throughout).
- **Talker turn.9/10**:
  - "Let me buy you a cup." / "Your cup's on me." are DECLARATION parts with **no beat** (reader #24, #26: `beats: []`)
    and no handled marker in the record, so nothing was bought or priced;
  - in turn.11 the sellsword asks "Is the round still on offer, or was that only the bait?";
  - the only coin moved (turn.13, 44 → 43) came from the Framer's free-text consequence "The coin is spent on the
    round", regex-parsed as 1.
- **The incident's pay** (Magby "pays well"; the Wolves' "good coin") is a yes/no Oracle fact or nothing. See (A).

**Root cause.** Mechanics stored as text: price exists only as words in a Framer consequence, so a no-roll offer has
no price at all. The Reader also drops trivial purchases (model behaviour, with no structural fallback: an unhandled
DECLARATION is passed through silently). **Frequency:** 3 of 3 payment offers in these runs were never priced; 1
became a 1-coin deduction after a roll.

---

## 4. People the lead promised are absent

| Run | Promise | Trace |
|---|---|---|
| Talker [23] | Kerric (t4): "the carters at the Sleeping Barrel would [know], if you buy them a cup" | Director #18: agenda "What do the carters at the Sleeping Barrel know of the omen?", `cast:["new_npc"]` → `meet_npc(role=None)` → the sellsword. The present list is the farmer, Hssaoo (his inn) and the sellsword. **No carters.** Settlement on the move (testimony #16) took `testimony.triggered` → "the latest line that named it" (testimony.py:141). That was Kerric's t6 Pipwise line (it mentions the Sleeping Barrel), not the t4 carters line. So `fact.97` "Pipwise is blood kin of Kerric" was settled, and **the carters claim was never settled.** |
| Explorer [19], [24], [25] | Branine (t2): "They're up at the healer's house" | Settled as `fact.99` subject `world`. Director #11 `cast:["new_npc"]` → the labourer. The refugees are neither an entity nor a placement, so nothing can present them (1c). |

**Root cause.**
- (C) The Director's cast schema (`schemas.py:352`) allows only existing ids or `new_npc`, and `director.py:120`
  passes `role=None`. The agenda's group cannot be cast, even though 12.14.13 already allows "an unnamed description
  of people present ('the refugees')" as T1a.
- Settled testimony about a group's location changes no presence.
- Wrong-record settlement: a low-precision "latest mention" heuristic.

**Frequency:** 2 of 2 scene changes made to find a promised group (2 of 4 non-opening scene changes overall).

---

## 5. "Branine Brightford brought the word" (explorer [31]): where the content comes from

- **Source: the case, not the lead and not the Director.**
  - `incident.incident_line` (incident.py:29-45) takes **node 1's core placement holder** and writes "<holder>
    brought the word."
  - `packet.scene_setting` (packet.py:399-401) adds "- the matter at hand (the character knows): Branine Brightford
    brought the word." to every SCENE SETTING.
- The Director's turn.15 decision (#39) is agenda "Does Haley find Edys Wellwell at the temple of Alett?", cast `[]`.
  It does not mention Branine.
- At a new-scene frame, the THIS MESSAGE instruction asks for "the one impetus the record names". The narrator took
  this line as that impetus and echoed it at the temple.
- **Semantic error.** The core holder is the person who *knows the sealed answer* ("who leads the refugees"). They
  are not necessarily the reporter. In the fighter run the same line made Magby (holder of "who makes the offer:
  Tobby") the one making the offer (see 1a).
- **Frequency:**
  - present in **44 of 44** narrator packets (15 talker, 14 fighter, 15 explorer);
  - echoed in prose at 3 openings (expected) and at **1 of 2 non-opening scene frames** (explorer t15);
  - shapes the employer's identity in 1 of 3 runs.
  - This is the catalogue's "a lead line in every packet" (wrong context) and "code authoring narrative truth".

---

## 6. Round-6 targets, measured

| Target | 021 live | **Round 7 (3 runs)** | Note |
|---|---|---|---|
| Refusals or intentions stored as facts | 0 | **0** of 3 settlements | Held. |
| Testimony settlement rate (per Reader turn) | 13% (offline) | **3/35 = 9%** (t 1/13, f 0/9, e 2/13) | Correct target **1/3**. 1 wrong record (latest-mention heuristic), 1 subject lost to `world` (a group with no entity). |
| Garbled claims (id, question, flipped pronoun) | 0/23 | **0/3** | |
| Dodge / "wall" per NPC line | 1/26 (regex) | Regex: 3/63 said lines, **all false positives** ("I won't say no", "I'll say yes to telling"). Record level: **6/29** NPC-response turns carried a code withholding line; **14/29** unsatisfying for any reason (table in §1). | The 021 DODGE regex has low precision; measure on record lines instead. |
| Found-clue repeats | 0 | **0**, but **0 case nodes were delivered in all 3 runs** | Case routing: **0 true hits out of 38 question parts; 1 false hit** (talker t9). It missed direct questions to core holders 4 times: Kerric t2 and t5 (the seam), Branine t2, Magby t2. |
| Pronoun flips on checkable lines | 0/6 | **0/10** true (analyzer 1/10, a false positive) | The real flip was in the narrator's voice (§2). It is not a "checkable said line", and no check covers "they". |

---

## 7. Causes, structural fixes, and what each retires

**No fix was proposed before this investigation.** For each cause: the minimal structural change, what it removes,
and what it retires.

**A. Content void: incident and lead terms never authored, and yes/no Oracle answers standing in for wh-answers**
(1a, 1c, 3, 4).
- *Fix:*
  - The incident and lead builders (`engine/gen/case.py`, `world_seed.yaml` options) author the concrete terms:
    - for `offer`: what the work is (from the `lead_to` clock), where (a region site), and the pay (a price-band
      table);
    - for `refugees`: the story (from the solution and the way on), and the group as an entity or description at a
      place.
  - These are written as **unsealed T1 knowledge on the offerer's or reporter's card**, so the willing NPC has
    something to say.
  - A Reader wh-question ("where / what / how much") on something no one has authored goes to that generator or to
    the case, **never** to the yes/no Oracle.
- *Retires:* Oracle booleans that assert unwritten content (`fact.102`, `fact.112`); the narrator's tautological
  answers.

**B. Two authorities on an addressed NPC** (1a, 1c, 1d).
- *Fix:*
  - One owner per question. Any Reader fact question whose subject is an NPC the PC is addressing goes to
    `answer.willingness` (for will) or to the NPC's stored licences and competences (for ability). It is never sent
    to `ask_oracle`. Today `speech_owns` checks a word list (`_KNOWS_Q`); it should test subject + addressed.
  - Every `verb.talk` beat uses the willingness path, whatever approach licence the Framer chose, so Neutral+ is
    always willing.
- *Retires:* `_KNOWS_Q`; branch (c) for talk-verb beats; contradictory record pairs.

**C. A blind new-scene cast; inert group settlement** (1c, 4).
- *Fix:*
  - `next_scene.cast` accepts a **description** ("the carters", "the refugees"). It is cast as an unnamed T1a
    description present in the scene (12.14.13 already allows this), or as `meet_npc(role=<words>)`.
  - Settled testimony that places a description at a place makes it present on arrival.
  - Settlement chooses the record whose *claim* matches the trigger, not the latest mention.
- *Retires:* `meet_npc(role=None)` for a stated purpose; `[-1:]` latest-mention selection.

**D. `incident_line` in every packet** (1a, 5).
- *Fix:* name the reporter only as the case defines one (a `reporter` field). Give the matter line only in the opening
  and the journal, or only in scenes at the incident's place.
- *Retires:* "the matter at hand" in all SCENE SETTINGs; core holder = reporter.

**E. Word-overlap case routing** (1b; clues never delivered).
- *Fix:* put the held, still-sealed node on the **holder's speaker card** as a gated item ("you know: what the omen
  shows — tell it if asked about it, within your willingness"). Delivery is then recorded from the speech, as
  testimony already is. Alternatively, have one `[J:enum]` call decide "is this question about node X?" with the node
  words and the incident text in view.
- *Retires:* `case_about`'s one-word subject hit and `need=2` incident overlap; code-written pointer lines to
  non-holders.

**F. Degree and suffix bugs** (1b, 1c). These are direct code fixes.
- Read an effective degree (`success_at_cost_taken` → success) at `npc_layer.py:570`, `answer.py:271` and
  `scene_state.py:160`.
- In `narrator._withheld`, add the suffix only for `REFUSING_ROWS` and refusals, not for every "acts on".
- *Retires:* the "success at a cost = refusal" contradiction.

**G. Generic-they text for unnamed NPCs** (2).
- *Fix:* render code text with the NPC's own pronouns ("call him '…'", "going about his morning work", "young (in his
  teens)"). After an upheld pronoun dispute, give the narrator a one-line note. Do **not** add a "they" check: it would
  have low precision, because "they" is plural too.
- *Retires:* the pronoun-neutral strings in `tbl.npc_activity` / age tables and in `packet.py:388,484`.

**H. Unpriced offers** (3).
- *Fix:* add a typed price. When a beat's pressure is `offer` with no `player_quantity`, the NPC's response names a
  price from a table (want row 4 "wants something before going on"). The OFFER or agreement carries it, and payment is
  a typed change.
- *Retires:* the `_PAID` / `_COIN` regex price parsed from Framer prose (mechanics as text).

**I. Greeting → willingness line → card recital** (the spec-021 hand-off, still live: explorer t16, 1 of 2 "replies"
lines).
- *Fix:* as 021 proposed. No willingness line without a question part, and the card header says its items are
  background.

**Design, not a bug:** the 3 dice walls. Wary or Unfriendly first reactions plus per-topic willingness re-rolls (the
sellsword refused at t10 and answered fully at t11) feel arbitrary. If walls should feel motivated, the refusal could
carry a code-supplied pointer to a real holder, so the redirect does not loop.

## Anti-pattern check (handoff §3.3)

| Anti-pattern | Where it appeared |
|---|---|
| Code authoring narrative truth | `incident_line` (44/44 packets); the misrouted pointer line (t9); Oracle booleans asserting unwritten content; extreme-meaning words appended raw ("and chase a curse"); "Magby bristles: will not harm a child or an innocent" at a pickpocket (`refusal.innocent` matched the theft, fighter t7). |
| Over-triggering rules | The `WITHHOLDING` prefix "acts on". |
| Low-precision checks | `case_about` word overlap; testimony's latest-mention record pick; the 021 DODGE regex; a pronoun check blind to "they". |
| Blind model calls | The Director's cast cannot express the group the agenda names. |
| Wrong context | The matter line in every packet. |
| Mechanics stored as text | Price; and NPC ability asked of the Oracle despite a stored licence. |
| Mandatory texture | Indirect: an activity line became the session's central prop. |
