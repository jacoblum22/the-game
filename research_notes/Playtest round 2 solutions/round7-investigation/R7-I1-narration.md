# R7-I1. Narration and text: traced to causes

Written 2026-10-09 on `milestone-1-playable` at ed51aa7. Read-only investigation.

**Data:** the three round-7 saves (talker 160602, fighter 160622, explorer 160642): 43 narrated turns, 44 narrator
calls; their transcripts, notes, `.disputes.md`; a fresh offline run (`evals/longhorizon.py --mode scripted
--lines 300 --keep`, identical numbers to `r7_longhorizon.txt`) whose store was kept for diagnosis; round-6 saves
(`playtest-20261008-*`) for like-for-like comparison. **Turn mapping:** in all three saves, transcript input *N* is
`turn.(N-15)`. A note filed "after typing [N]" describes the output shown after input *N* (and earlier ones).

**Method:** for every instance: delivered text, the narrator packet's sections (`ROLE INSTRUCTIONS`, `GUIDANCE`,
`NARRATOR VIEW`, `RECENT EXCHANGES`, `THIS MESSAGE`) and the response, the turn record (`draft_versions`,
`side_list`, `said`, `parts`), and the code path. Scratch scripts (`pkt.py`, `scan.py`, `motifs.py`, `attrib.py`,
`pauses.py`, `carry.py`) live in the session temp folder, not the repo.

## Summary

| # | Symptom | Actual cause | Model or scaffolding | Frequency |
|---|---|---|---|---|
| 1 | Same gesture or descriptor every turn | **Three code inputs plus self-copying.** (a) The seeded look (`detail`) and voice habit are printed raw in every packet, twice. (b) Habits are phrased as always-on ("while thinking", "calls everyone", "constantly"), and rule 12.11.3's "at most once per scene" never reaches the model. (c) The freshness marks (12.14.11) only track `detail.*` facts, and the seed never writes looks or habits as those, so the mechanism is inert: "Details stated lately" appeared in 5 of 44 packets, always one item. (d) The prompt's closing slot ("an unresolved image that plainly awaits a response") is filled with the scene's standing image, which is then copied forward from RECENT EXCHANGES. | Mostly scaffolding; the copy-forward is model behaviour that nothing counters | Habit shown in 16 of 21 speaking turns of habit-bearing NPCs (rule: once per scene). Kettle in 11 of 11 healer-house turns. A recurring motif in the last two sentences in 29 of 43 turns. |
| 2 | Speech attributed to the wrong person (explorer [20]/[21]) | The model wrote Morga's speech as its own paragraph with no tag, after the laborer's action. **Code then removed the paragraph break** (`narration._text` joins the split sentences with a space). The side list had it right (`speaker: npc.morga_embershield`). | Model (no tag) plus scaffolding (paragraphs flattened in 43 of 43 deliveries) | 1 clear misattribution; 1 more is the fighter opening's only stacked quote (see 5) |
| 3 | Narration ran ahead of a pause (talker [28]) | **Contradictory record lines, not model drift.** Pre-choice (turn.12): R1 MUST "result: failure (the world answers), a near miss" + "stop at the moment before [the pause]" + the generic answer line ("answers in quoted words… never end on waiting"). The model had him accept the round ("I'll not say no to it") and answer. Post-choice (turn.13): R1 "success at cost… never a refusal", R2 cost "he turns the round down", **R3 "refuses… the talk did not move them (failure)"**. R3 comes from a bug: `npc_layer.py:572-575` reads `degree == "failure"` and ignores `success_at_cost_taken`. | Scaffolding | 2 of 6 paused turns ran ahead (also fighter turn.5, a double negative). 1 of 1 near-miss resolution got a refusal on a success. |
| 4 | Failed roll still gave a full answer (talker [24]) | **Not a narration fault.** The roll was a separate DECLARATION ("help steady that cask"). The question was a separate SPEECH part, correctly answered willingly by a friend. The failure was narrated. The confusion comes from the auto OFFER, printed *after* the narration, titled "Help Hssaoo of the Hill Den" with "If it works: what you wanted". | Presentation (OFFER title), plus an easy, consequence-free roll (mechanics) | 1 instance |
| 5 | Template slips and lines from nowhere | **Code-authored narrative sentences in the packet.** "the matter at hand (the character knows): X brought the word." is in **44 of 44** narrator packets (`packet.py:398-401` from `incident.py:44`). The model voiced it at a new scene's framing (explorer turn.15) because the prompt asks for "the one impetus the record names". "the officer of The faithful of Alett" is a seeded role string (`_seed_steps.py:517`, `"officer of {}".format(faction name)`) that code orders the model to use verbatim ("call them '…', as every other screen does"). The opening's leads are MUST lines with seed-template text ("X is hiring, and asks no questions"; "…; folk say it is only the beginning"), delivered nearly verbatim in 3 of 3 openings. | Scaffolding | "brought the word" in 3 of 43 deliveries (8 in round 6); "officer of The" in 4; seed lead phrases in 3 of 3 openings |
| 6 | Offline: 64.9% first draft, 35.1% cut or render; novelty-4 0.64 vs 0.72 | **An offline-model artefact, and not new.** All 108 failures are draft → revision → render of must-name lines the offline stub never words: "X agrees to what was asked" (≥80), positions, lead arrivals. Spec 019's own base was 64.3%/35.7%. The drop from 89%/0.72 happened between `longhorizon_011` and `longhorizon_020_before` (specs 013–018), not in 019–022. Live novelty-4 is **0.95–0.97** in round 7 against 0.65–0.96 in round 6. | Offline stub | n/a |

**Shared causes:**
- **Code writes narrative sentences and descriptors into the packet as content.** This covers the habit and look lines, "brought the word", the lead templates, "officer of The …", and the "call them"/"their" templates. It is behind symptoms 1 and 5, and it feeds the pronoun drift (below).
- **Code destroys the model's paragraphing.** This is behind symptom 2 and the one stacked quote in symptom 5.
- **Record lines that contradict each other around a pause.** This is behind symptom 3.
- **Novelty-4 cannot see motif repetition.** Live novelty is 0.96 while players see the same image every turn. This is a measurement trap.

---

## Round-6 targets on the round-7 saves (`specs/019-holistic-narration/metrics.py`)

| Measure | Round 6, all 10 saves | Round 6 talker 232941 | **Round 7 (3 saves)** | talker / fighter / explorer |
|---|---|---|---|---|
| Narrated turns | 106 | 14 | **43** | 15 / 13 / 15 |
| Stacked quotes | 57 in 34 turns | 21 in 10 | **1 in 1** | 0 / 1 / 0 |
| Echoed player lines | 29 | 6 | **0** | 0 / 0 / 0 |
| Duplicated answers | 20 in 12 | 2 in 2 | **0** | 0 / 0 / 0 |
| First draft delivered | 82% | 64% | **98%** (42 of 43) | 100 / 92 / 100% |
| Revision rate | 17% | 36% | **2%** (1 of 43) | 0 / 8 / 0% |
| Narrator calls per narrated turn | 1.24 | 1.57 | **1.02** | 1.00 / 1.08 / 1.00 |
| Cut or fallback | 2% | 7% | **0%** | 0 / 0 / 0 |

Spec 019's targets hold live.

**The one stacked quote** (fighter turn.1) is a paragraph that code flattened. The model wrote the lead line "The Goldgate Circle is hiring…" as Magby's own paragraph (the side list says Magby). Joined with a space, it became `answer." "The Goldgate…`.

**The one revision** (fighter turn.16) was a **false positive** of the pronoun check. In `"That one's the worst of the lot," she says`, the check took the subject to be Magby (he/him), because "Magby's back is still turned" came just before. The revision then produced the awkward "The soldier off duty says it low and even". The pronoun check here was 0 of 1 real, and it blocks.

---

## 1. The same gesture or descriptor every turn

### Instances (all three saves; `motifs.py`)
- **Talker, Kerric** (turn.1–6, inputs 16–21):
  - finger-counting in 4 of 6 deliveries (turn.1–4), opening or closing each;
  - "the hire notice snaps/flutters in the draft" in 5 of 6;
  - "the seam over the eastern roofs" in 5 of 6.
- **Talker, the sellsword** (turn.9–13): the habit "whispers secrets far too loudly" in 5 of 5 of his turns ("speaking far too loudly for a secret", "louder than any secret deserves", "a rasp that still reaches you", "a rasp that still carries", "though it still carries"). The burn scar appears in 6 of 9 tavern turns.
- **Explorer, healer's house** (turn.3–14, 11 narrated): the kettle in **11 of 11**; Morga's burn scar or scarred hand in 6; the nickname ("my bird", "my duck") in 5 of 8 of Morga's speaking turns; the crutch in 9.
- **Fighter, the hall** (13 narrated):
  - the list's curling corner in 4 (turn.2, 3, 5, 15; turn.2 and turn.3 back to back, as noted at [19]);
  - Magby's stick or bad leg in 11 of 13;
  - Belie's "Mark me" in 3 of 3 of her speeches.
- **Habit-bearing NPCs overall:** the habit shows in **16 of 21** speaking turns. Rule 12.11.3 says "used at most once per scene so it stays a signature rather than a joke"; across these four NPC-scenes that allows 4.
- **The closing slot:** in 29 of 43 deliveries, the last two sentences hold one of the scene's recurring motifs. 28 of 43 do not end on a question, and the standing image is what fills that closing slot: "The kettle rattles on…", "the hire notice snaps in the draft…", "Her fingers resume their count".

### What the packet gave the model (talker turn.4, explorer turn.14 as examples)
- **The NARRATOR VIEW**, every turn, prints the entity record raw (`packet.py:_entity_lines`, about lines 476–495):
  - `voice: register=cold, habit=counts on their fingers while thinking`
  - `detail: a finely embroidered collar`
  - for Morga, `detail: a burn scar across one hand` and `voice: register=jovial, habit=calls everyone by a nickname`.

  The habit was in the view in 42 of 44 round-7 narrator packets. Round 6 is the same (22 of 22 in talker 232941), so this predates 019/020.
- **SCENE SETTING**, in "already described" mode, still lists each person with their look every turn (`packet.py:385`): `present: Morga Embershield, the healer (she/her, old, a burn scar across one hand, fearful)`.
- **Refusal record lines carry the habit inside a MUST line.** `npc_layer.py:491` `voiced_refusal` gives "refuses, in their own voice (jovial, whispers secrets far too loudly)" (talker turn.13). Fighter turn.4 has "(formal, speaks of themselves by name)", which produced Magby's odd "Magby Applefoot will not read it out…".
- **The kettle** comes from the place's seeded look on arrival: `look: a whitewashed sickroom, quiet except for a kettle` (explorer turn.3). From turn.4 on it is in no view or record line. It survives only through RECENT EXCHANGES, where every prior DM turn has it, and the model copies it forward. The list's corner, the broom and the back door are the same kind: a model-made image copied forward.
- **The talker's hire notice**: turn.4 alone also had a *reading* line ("the character reads the hire notice: quote its words exactly"). The player had not read anything. `READING` (`retrieve/scene.py:23`) matched "**what did they say**" in "Who did you ask, and what did they say?". That is a low-precision trigger, which then picks both notices because none was named (`narrator.py:213-214`, `(named or things)[:2]`).
- **The freshness line** (`narrator.py:379-400`) only names the last three *openings*. The model complies by moving the tic from the first sentence to the last.
- **"Details stated lately"** draws only on `state.details` (`narrator.py:468-485`), and `_mark_used` (`narration.py:593+`) marks only `detail.*` facts. The seed writes looks and habits as entity data, not as detail facts. The explorer save has *no* lasting `detail.*` facts, only scene-persistence activity and manner rows, which `used_details` skips. So the line appeared in 5 of 44 packets (talker turn.11–16, one item: "back door: state").
- **GUIDANCE** (about 9,900 characters) carries 12.14.2, 12.14.3, 12.14.13 and 00.6.6. It has nothing on freshness or the once-per-scene habit.
- **The role prompt** (`prompts/narrator.md:64-66`) says to end on "a situation-specific question … or an unresolved image that plainly awaits a response".

### Root cause
Round 5's diagnosis (T3: the repetition is blind repair calls, and "a model that can see the conversation doesn't normally repeat a catchphrase") is now **tested and falsified for the residue**. Round 7 has one call per turn and no repairs, and the repetition remains.

What remains is what code puts in front of the model every turn:
- a seeded look and an always-on habit, as raw data with no frequency guidance;
- a refusal line that requires the habit;
- a freshness mechanism whose inputs are never populated for these things;
- a prompt that asks for a closing image, whose most available material is last turn's closing image.

This is the **mandatory texture** and **wrong context** pattern again. It is not a regression: an image carry-over heuristic (two or more shared content bigrams with the previous delivery, quotes and names removed) gives round 6 74% (all saves) or 50% (latest pair), and round 7 57%.

### Structural fix
**Make the habit and look a once-per-scene, code-tracked offer, not standing data.**
1. Stop printing `voice` and `detail` in the view's entity block and in every `present:` line.
2. Offer the habit and look once per scene as OPTIONAL MATERIAL ("may use once this scene"). Mark it used when the delivered passage shows it, from the side list or a model-declared `used` field, not a prose scan.
3. Rephrase `tbl.npc_voice_habit` rows to be occasional ("now and then counts on her fingers").
4. Drop the habit from `voiced_refusal`'s record line (keep the register).
5. Teach the freshness line the **closing** image as well as the opening ("do not end the way these recent turns ended").

Separately, gate `READING` on a document being named or in focus.

**What it retires:**
- the raw `voice:` and `detail:` lines in the view;
- the look in `present:` after framing;
- the habit inside refusal record lines;
- `used_details`' dependence on `detail.*` facts that the seed never writes (or the seed writes them; either way, one usage mechanism);
- the opening-only freshness backstop.

---

## 2. Speech attributed to the wrong person (explorer [20], [21]; turn.4, input 19)

**What the player saw:** "…Beside the stove the laborer shifts his weight on his crutch and keeps grinning. "They're here, my bird, the whole lot of them…" Her burned hand tucks…"

**The model's response** (`call.turn.4.narrator.0.0`):
- passage: `"…keeps grinning.\n\n\"They're here, my bird, …\"\n\nHer burned hand tucks against her side…"`
- side list: `speech: [{speaker: npc.morga_embershield, words: "They're here, my bird…"}]`

The record and `said` are correct. The model relied on a paragraph break and a later "Her" instead of a tag. That is model behaviour against the prompt's "with one speech tag".

**Code path:**
- `narration._draft` → `declare.sentences_of(passage)` splits the passage into sentences;
- `_deliver` → `_text(final)` = `" ".join(...)` (`narration.py:445-446`, used at `:532`);
- `out.fiction = text`.

Every paragraph break is lost: **21 of 43 first drafts had paragraph breaks; 0 of 43 deliveries have any line break**. Spec 019 says code splits the passage "only to place a failure or a cut", but in fact the split is *always* the delivered text.

**Frequency:**
- 5 quotes open a paragraph with no tag in their first sentence. In 3 the previous paragraph is about the same speaker, which is harmless.
- 1 is a real misattribution (this one; the note at [21] refers back to it).
- 1 is the fighter opening's Goldgate line (symptom 5), which becomes a stacked quote once flattened.

**Structural fix:** deliver the passage as written. Keep paragraphs, and apply cuts and code-quoting in place within the original text, using the split only as an index into it. A pure code fix that removes half the cause.

For the other half, a check against the side list: "a direct speech whose sentence has no tag and whose previous sentence's subject is a different present person". Measure its precision before letting it block; it would have caught 1 real case and 0 false ones here. Otherwise keep it as a logged audit.

**What it retires:** `_text`/`declare.joined` as the source of the delivered fiction.

---

## 3. Narration ran ahead of a pause (talker [28]; turn.12 and turn.13)

### Pre-choice, turn.12 (input 27, "set a coin… call for a cup… why wouldn't you walk the barrow track?")
**What the packet's THIS MESSAGE held:**
- `part [DECLARATION] "I set a coin on the table and call for a cup for each of us." (paused)`
- `R1 MUST: beat: Set a coin … offering the sellsword a round; approach: verb.talk, presence; difficulty: opposed; result: failure (the world answers), a near miss` (`narrator.py:99-102`: the degree is written even though the outcome waits on the choice)
- the generic answer line (`narrator.py:147-162`, `_speech_line`, emitted whenever a SPEECH part exists, pause or not): "the one the PC addressed answers in quoted words… never end on waiting for them to speak"
- `- the turn stops at a pause (near_miss): stop at the moment before it` (`narrator.py:353-355`)

**What the model wrote:** "Still on, friend, and **I'll not say no to it**." It also gave a full answer about the barrow track, and "his fingers hover over [the coin]". That is an acceptance of the round, the very thing the roll was deciding.

### Post-choice, turn.13 (input 28, `a` = succeed at a cost)
**What the packet held:**
- `R1 MUST: … result: success at cost (it works…); it worked: the one asked answers what was asked (never a refusal, a dodge or 'not now')`
- `R2 MUST: cost paid: he turns the round down and the offer goes nowhere with him`
- `R3 MUST: the sellsword … acts: refuses, in their own voice (jovial, whispers secrets far too loudly): the talk did not move them (failure)`

**Events:** `frame_resolved {"degree":"failure","near_miss":true,"success_at_cost_taken":true}`.

**Cause of R3:** `npc_layer.py:572-575` takes `degree = b.entry.degree` and calls `voiced_refusal` when it is `failure`, never consulting `success_at_cost`. `answer.py:271` has the same blind spot. The model followed R2 and R3: "Keep your round, friend. I'll not drink on it." That contradicts turn.12's acceptance.

The cost itself ("turns the round down") *is* the failure, so success at a cost bought nothing (the note at [29]: "no new information, flat"). That is a cost-menu problem for the mechanics investigator.

### Other paused turns (6 in all; `pauses.py`)
- **Fighter turn.5** (pickpocket, OFFER):
  - The record has `R2 MUST: question "is not alert to a hand reaching into his coat pocket while he faces the fire": the answer is no` (`narrator.py:295`). That is a Framer-phrased negative plus an Oracle "no".
  - The model read it as "not alert" and wrote "He does not feel it. His shoulders stay exactly as they were." That narrates the roll's success before the roll.
  - The OFFER shows the same text as "is not not alert … −2" (the /fix at [21]).
- **Explorer turn.10 and fighter turn.11:** an NPC answered an Oracle MUST line before a persuasion OFFER on a related ask. The narration was faithful; the OFFER contradicted it (fighter: persuading Belie, who cannot read, to read). That belongs to the Framer and OFFER.
- **Explorer turn.12:** fine.

**Root cause:** **contradictory record lines**, not model drift:
- an outcome word on an undecided beat;
- an answer obligation that ignores the pause;
- an NPC reaction computed from the pre-choice degree;
- a negative proposition with a yes/no answer.

**Frequency:**
- 2 of 6 paused turns ran ahead;
- 1 of 1 near-miss resolution delivered a refusal for a success;
- 1 negative Oracle line, mis-narrated.

**Structural fix:**
1. **A paused beat has no result in THIS MESSAGE.** `_beat_line` writes "not resolved yet: the player chooses next" for a near miss too, and keeps "the near miss" for the OOF block only.
2. **`_speech_line` is suppressed for the NPC the paused beat targets**, or replaced by "they have not answered yet".
3. **Every NPC reaction reads one resolved-outcome function** that knows `success_at_cost_taken`, not the raw `degree`. Fix `npc_layer.py:572-575` and `answer.py:271`.
4. **Oracle lines are rendered as the resulting proposition** ("Magby is alert to a hand in his coat"), or the Framer is asked for positive propositions only.

**What it retires:** "a near miss" as a narrated result; the unconditional answer line; degree-only refusal; "question …: the answer is no".

---

## 4. A failed roll still gave a full answer (talker [24]; turn.8, input 23)

**What the record held:**
- the parts: `SPEECH "Hssaoo!"`, `DECLARATION "Let me buy the carters a round."`, `SPEECH "What have you heard about Morri Flinthelm and the Wolves?" (answered)`;
- `R1 MUST: beat: Cross to Hssaoo and help steady the cask; approach: verb.help, might; difficulty: easy; result: failure`;
- `R2 MUST: Hssaoo … answers what you asked, willingly (a plain question to a friendly listener)`.

**What the narration did:** it delivered both. The cask "shudders out of your grip", and the friend answers. The roll gated only the help. **This is correct by the rules (one beat per goal) and is not a narration fault.**

**What misled the player** is the `[OFFER — auto] Help Hssaoo of the Hill Den`, with "If it works: what you wanted", printed after the narration. It is titled by verb and target, not by the beat's own words ("help steady the cask"). The roll itself is an easy help with no stakes; that is for the mechanics investigator.

**Fix (patch):** title auto OFFERs from the beat's own sentence (017's `own_line`), so the label says "Steady the cask with Hssaoo".

---

## 5. Template slips and lines from nowhere

### Explorer [31] (turn.15, input 30, framing the temple)
**What the packet held:**
- THIS MESSAGE purpose line: "frame the new scene… **the one impetus the record names**";
- the record has only R1 (the move) and R2 (the scene opens);
- SCENE SETTING ends with `- the matter at hand (the character knows): Branine Brightford brought the word.`

**What the model wrote:** "Branine Brightford brought the word, and Edys Wellwell is the one you came to find." Branine is at the gate, three scenes back. **The model obeyed the only impetus-shaped line it had.**

**Code:** `packet.py:398-401` adds `incident_line()` (`incident.py:44`: `f"{display_name(...)} brought the word."`) to SCENE SETTING on **every** narrator call: 44 of 44 in round 7, and 24 of 32 in round-6 talker 232941 and fighter 233000.

**Delivered:**
- round 7: talker turn.1, explorer turn.1 and turn.15;
- round 6: 8 deliveries, several in NPC speech ("since he's the one who brought the word").

### "the officer of The faithful of Alett" (explorer turn.15; fighter turn.1, 10, 14: "the officer of The Kingsholt Company of Merchants")
**Source:** `_seed_steps.py:517` builds the role as `"officer of {}".format(fac["name"])`, with faction names stored as "The faithful of Alett". The packet then orders the model to use the label verbatim, twice:
- `packet.py:388`: `call them "the officer of The faithful of Alett", as every other screen does`;
- `packet.py:484`: "call them … (the words every other screen uses…)".

It also appears in OPTIONAL MATERIAL ("the officer of The faithful of Alett is on an errand").

### Fighter [17]/[18] (the opening, turn.1)
**What the record held:**
- `R2 MUST: note: the inciting incident: a powerful person offers the character work, coin and a warning. Magby Applefoot brought the word`
- `R3 MUST: note: a lead to make noticeable: A mother asking at every door; folk say it is only the beginning.`
- `R4 MUST: … The Goldgate Circle is hiring, and asks no questions`

This PC cannot read ("the character cannot read the any posted notice", itself a code grammar slip). So the leads could not sit on a notice, and the model put them in mouths verbatim: Magby "The Goldgate Circle is hiring, and it asks no questions." (its own paragraph, then flattened into a stacked quote), and Belie "A mother has been asking at every door in Hartwell. Folk say it is only the beginning. Mark me."

**The same seed templates in every opening:**
- "…; folk say it is only the beginning" (`_seed_steps.py:787`) was delivered in **3 of 3** openings;
- "X is hiring, and asks no questions" (`:859`) is in all three;
- the talker's notice text ends "…at the market square. The Mereham Wolves" with no separator (the note at [17]).

**"Dropped" at [18]:** after turn.2 the leads leave the view (spec 020: lead line only when relevant), which is fine. But the incident itself ("work, coin and a warning") has no content in the store: no job and no pay. Magby's later answers had nothing to say. R3 on turn.3 is an Oracle yes ("names one place where the danger is worse: yes") with no value, which gives the evasive "The name's written there" and the list-corner loop. This is the round-6 hand-off pattern (a yes/no instead of a value) and belongs to the NPC and content investigator.

### Root cause
**Code authoring narrative truth.** The engine writes sentences meant for the player (the incident reporter, lead texts, faction-role labels) and ships them as content lines the model must or may repeat. The model repeats them faithfully, in the wrong place.

### Structural fix
**Facts, not sentences.**
- The incident's reporter becomes a view fact (`incident.reported_by = npc.x`), shown on the opening and in the journal, not a SCENE SETTING sentence on every turn.
- Leads reach the opening as lead *facts* (who, what, where), and the model words them. Drop "folk say it is only the beginning".
- Unnamed-person labels are built from a role noun plus a lower-cased faction short name ("a Kingsholt officer", "an officer of the faithful"), and the "call them" instruction allows natural variation after the first mention.

**What it retires:** `incident_line` in `scene_setting`; the seeded lead sentences as MUST text; the "every other screen" verbatim-label rule.

---

## 6. Offline: first draft 64.9%, cut or render 35.1%, novelty-4 0.64

**Reproduced:** the offline run on ed51aa7 gives 200 of 308 (64.9%) first drafts, 108 of 308 cut or render, 1.35 calls per turn and novelty-4 0.64. These match `r7_longhorizon.txt`.

**The kept store:**
- **All 108** non-first-draft turns are `draft → revision → render`. There are no cuts or fallbacks.
- The uncovered must-name items: "X agrees to what was asked" (the healer 18, the guard 12, the beggar 12, the merchant 10, …; at least 80 of the items), "position: you at arm's reach of …", and "note: a lead arrives …".
- The offline narrator (`engine/llm/offline.py`) is a template stub. It echoes record lines ("Grak Three-Scar answers what you asked, willingly (the talk moved them), and in their own words.") and has no wording for these lines. Its revision does not change that, so code renders the line.
- **Spec 019 reported the same:** 64.3% (base 64.3%), "the offline narrator never words agrees/lead/position lines".

**When it changed:**

| Baseline | First draft | Novelty-4 | Calls per turn |
|---|---|---|---|
| `longhorizon_011` | 86.4% | 0.73 | 1.27 |
| `longhorizon_final_overnight` | 89.1% | 0.72 | 1.22 |
| `longhorizon_020_before` (pre-019) | 64.3% | 0.65 | 1.71 |
| `_020_merged` | 64.3% | 0.64 | 1.36 |
| `_021` | 64.3% | 0.64 | 1.36 |
| r7 | 64.9% | 0.64 | 1.35 |

So the step happened in specs 013–018. Spec 015, typed change with `agreed` lines and must-name, is the likely one; it is the only one of them that touched `offline.py`. 019–022 moved nothing but the call count (down).

**Novelty-4 offline** measures how varied the record lines are that the stub echoes, not prose. The first drafts alone score 0.57 against 0.59 for the final versions in the store, so the rendered lines are not what pulls it down.

**Live novelty-4** is 0.968, 0.945 and 0.960 for the three round-7 saves. Round 6 ranged from 0.65 to 0.99 (232941 talker 0.92, 233000 fighter 0.95).

**Verdict:** an offline-model artefact. No live narration path changed.

The real problem is that the offline gate cannot detect a narration regression. Either teach the stub the three line families, which would restore about 89% as a working baseline, or stop reporting offline first-draft and novelty as narration measures. Novelty-4 also misses symptom 1 entirely: it is 0.96 live while players see the same image every turn. **Measure motif carry-over** instead, for example the bigram carry-over in `carry.py`, or the share of deliveries restating a seeded look or habit within a scene.

---

## Also seen (narration-adjacent, for other lanes)
**Pronoun drift** (talker, the sellsword, the /fix at [29]):
- The packet gives "he/him" in 4 places per turn, but surrounds the person with code-written singular *they*: "call them …", "does not know **their** name", "add how **they** look", "young (in **their** teens)", "going about **their** morning work", "refuses, in **their** own voice".
- The model used "they" in 4 of 5 of his turns.
- The pronoun check never flags *they*. Code templates should use the person's pronouns.
- Same family as symptom 5.

**The /fix explanation:** the Fixer's reply ("the 'they' lines were the slip") was right, but nothing changes the next turn's packet.

## Anti-pattern check (handoff §3.3)

| Anti-pattern | Seen here |
|---|---|
| **Code authoring narrative truth** | "X brought the word" in every packet; lead sentences as MUST text; the "officer of The …" verbatim label; code-written singular *they*; "question '…is not alert…': the answer is no"; the habit inside a refusal MUST line |
| **Atomisation** | The sentence split is still the delivered text, so paragraphs are lost (spec 019's "split only for cuts" is not true of delivery) |
| **Over-triggering rules** | `READING` matching "what did they say"; the answer line on every SPEECH part, even under a pause |
| **Low-precision checks that block** | The pronoun check's one blocking hit was false (fighter turn.16), and its revision made the prose worse |
| **Blind model calls** | None found (one call per turn; the revision saw the draft) |
| **Wrong context** | Look and habit raw in every view; the matter-at-hand line in every SCENE SETTING; a reading line for two unread notices |
| **Mechanics stored as text** | The near-miss outcome written as "result: failure" before the choice; the NPC reaction computed from the raw degree (ignores `success_at_cost_taken`) |
| **Mandatory texture** | Always-on habits, the refusal line's habit, the closing "unresolved image" slot |
| **Test and measurement traps** | Offline first-draft and novelty measure the stub's vocabulary; novelty-4 cannot see motif repetition |

## Fixes, ranked

| Fix | Removes | Retires |
|---|---|---|
| **A. Deliver the passage as written** (paragraphs kept; cuts and quoting applied in place) | Symptom 2's code half; the stacked quote | `_text`/`joined` as delivery |
| **B. Facts, not sentences, for seeded narrative** (incident reporter, leads, faction labels, pronoun-correct templates) | Symptom 5; pronoun drift's code half | `incident_line` in SCENE SETTING; lead MUST text; the "every other screen" verbatim label |
| **C. Once-per-scene texture, tracked by code** (look and habit offered once, marked used; habits rephrased as occasional; closing images in freshness) | Most of symptom 1 | Raw `voice`/`detail` in view and `present:`; the habit in refusal lines; detail-only usage marks |
| **D. One outcome function and no result before a choice** (paused beats unresolved; answer line suppressed for the paused target; NPC reaction reads success at a cost; Oracle lines as propositions) | Symptom 3 | "a near miss" as narrated result; degree-only refusal; yes/no on negatives |
| Patches | the `READING` precision; the auto-OFFER title from the beat's sentence (symptom 4); the "the any posted notice" grammar; the notice signature separator; pronoun-check precision in narration tags; offline stub vocabulary, or demoting offline narration metrics | — |
