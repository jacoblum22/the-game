# I1. Narration and text: traced to causes

Written 2026-10-09 on `milestone-1-playable` (b9c4a1b). This is a read-only investigation.

**Data:** all 10 saves `saves/playtest-20261008-*.db` (106 narrated turns, 161 NPC speech sentences, 25 repair
calls), plus the transcripts and notes in `evals/playtests/20261008-*`. The two latest runs are talker 232941 and
fighter 233000. In the talker save, transcript input *N* is `turn.(N-15)`. A player note filed at input *N* describes
the output shown just before that input.

**Method:** each problem was traced from what the player saw, through the model call (`model_calls.request` packet
sections and `.response`) and the turn record (`draft_versions`, `parts`, `said`, `claim_log`), to the code path. The
scratch scripts (`dump.py`, `vers.py`, `pkt.py`, `scan.py`) live in the session temp folder, not in the repo.

## Summary

| # | Problem | Suspected cause | Actual cause | Model or scaffolding |
|---|---|---|---|---|
| 1 | Stacked, choppy dialogue | Sentence-array schema | **Confirmed.** 88% of the stacked quotes are already in the first draft. | Scaffolding (schema), plus model habit |
| 2 | The player's line echoed back | Spec 017 `said_first` | **Not 017.** A blind repair "answers" a *statement* (a SPEECH part with `question_kind: none`). The next turn's draft then imitates it. | Scaffolding first; the model copies it afterwards |
| 3 | "Then:" line garbled | 017 restatement | The OFFER prints the Reader's internal `method` field as written | Model (Reader paraphrase), printed raw by code |
| 4 | `/fix` hint repeats recap text | Hint renderer | **Not an engine fault.** The hint was printed once. The player harness shows a 9000-character window, and the opening and hint sat in its middle. | Harness artifact |
| 5 | NPCs repeat each other and earlier turns | Repairs, testimony or view | **All three, plus a fourth.** The answer route re-delivers an already-found clue. Blind repairs stitch turns. The open-threads lead line sits in every view. The model copies sentences from RECENT EXCHANGES. `/fix` complaints and `agreed` facts come back as NPC "knows". | Mostly scaffolding |
| 6 | "settled between you" | `persuade_to` plain-words line | **Confirmed and made more precise.** `change.py` builds "Agreed by X: <the PC's *intent*>", and `narrator.py:294` adds "say it plainly; it is done" | Scaffolding; the model complies literally |
| 7 | Other per-part and per-sentence harm | — | Coverage drove 28 of 30 repair targets, with 1–2 real catches in 21 unique items. Must-name and `_deliver` rendering never fired (0 of 106 turns). The only precision block was a false positive. 5 speech sentences went out **without quote marks**, and nothing checks for that. | Scaffolding |

---

## 1. Stacked, choppy dialogue

### Evidence
Talker 232941, turn.2 (input 17, note 18: "odd stacked quotes"). The delivered text:
> "Rrakaa Mud-Walker," he says. "Missing since last night, and that is all the word I hold of it." "The hour I can
> give you is last night, and no finer than that." "As for the trail, …" "Because the tracks go …" "Plain enough
> for any eye to follow," Belby says. "It runs past …" "Well? Will you walk …"

Each `"…" "…"` is the join between two `sentences[]` items that share the same `speaker`. In talker 145410, turn.14
draft, the other shape appears: every item carries its own tag ("says Garwen Deepwell" four times in one answer).

### Cause
- **The output shape.** `schemas.py:380–392` makes `sentences` an array of objects, each with a single `speaker`.
  The prompt (`prompts/narrator.md:44`) says each item is one sentence.
- **Quotes cannot cross items.** `declare.voices()` (`engine/audit/declare.py:246`) reads speech per item. An item
  with a speaker and no quote marks is read as *reported* speech, so every item has to open and close its own
  quotes.
- **Code concatenates the items.** `narration._text` / `declare.joined` join them with a single space.

The model then either tags every item or leaves the quotes stacked. Repairs make it worse: an "add" lands as yet
another closed quote (turn.2's "Because the tracks…" and "Plain enough…" both came from repairs).

### Frequency (all saves; delivered text)

| Measure | Value | Natural prose |
|---|---|---|
| NPC speech sentences / speaker runs | 161 / 90 (1.8 per run) | — |
| Quote spans per speaker run | 2.5 (3.9 in runs of 2+ sentences) | 1 |
| Speech tags per multi-sentence run | 1.9 (0.69 per sentence) | about 1 |
| Back-to-back `" "` joins | 57, in 34 of 106 turns (talker 232941: 21 in 10 of 14 turns) | 0 |
| Joins already present in the first draft | 50 of 57 (88%) | — |

Of the 38 multi-sentence runs in first drafts, 20 tag *every* sentence and 6 have no tag at all.

### Fit with the proposal
**Removes the cause.** A single passage lets one speech be one quote with one tag.

What it still needs:
- The side list must give, for each speech, `{speaker, words}`, where `words` is the exact quoted substring. Code
  then checks that every quoted span has a declared speaker.
- `_said` must store whole speeches. Today it joins the quote spans inside one item with a space, which produces
  "they already said" lines such as "Plain enough for any eye to follow, It runs…", and those go back into speaker
  cards.

---

## 2. The player's own line echoed back (talker 232941, notes 30–31)

### Evidence
**turn.14 (input 29).**
- The draft was 5 sentences and did not end on "?".
- `_acknowledged` flagged a part that is **not a question**: `SPEECH, question_kind none: "Captain, I'll be plain.
  The trail stops on the road past the last house."`
- Repair call row 46 was given only this (packet THIS MESSAGE):
  > `- part [SPEECH] "Captain, I'll be plain. …" (answered)` … `MISSING (add one sentence for each, replaces = add,
  > citing its handle): answer: Captain, I'll be plain. The trail stops on the road past the last house.`
- The packet contains none of the draft's sentences, and it contradicts itself ("(answered)" and also "MISSING
  answer").
- The model returned `{"replaces":"add","speaker":"none","text":"You meet his suspicious eyes across the chain and
  say, \"Captain, I'll be plain. …\""}`.
- `narration.py:526` places an add before the closing question only when the draft had one (`had_prompt`). There
  was none, so the add went at the very end, and **the passage ends on the player's own line.** The final screen
  still logged "12.14.9: does not end on an open prompt".

**turn.15 (input 30).**
- This was a single draft with no repair, and it opened: `You say, "Thank you, Captain. One more thing: …"`.
- RECENT EXCHANGES held turn.14's ending.
- The prompt licenses the move: `narrator.md:29` "Quote the PC only in the player's own words", and `:41`
  "Acknowledge what the player tried".
- FRESHNESS ruled out the last two NPC-led openings, which leaves "you say" as the easy opening. (That last point is
  a hypothesis.)

**Spec 017 (`said_first` / `_take` appending carried SPEECH parts):**
- In 232941 it carried nothing into turns 14–15, because there was no pause on turn.13 or turn.14.
- The only 017 carry-over that tried to restate speech is fighter 233000 turn.6, after "commit". The draft opened
  `You say, "Tell me the word, Dunwen. …"` from R4 (the queued speech beat).
- That was **cut** by the `pc_agency` check (`narration._speech`, `atx.covers(q, turn.player_message)`), because
  `player_message` was "commit". The words really were the player's (input 20). So the cut was a false positive,
  though a harmless one.

### Cause
The main cause is scaffolding:
- `screen._acknowledged` (`screen.py:152`) treats every SPEECH part as owing an answer (`ANSWERED_CLASSES`,
  `screen.py:26`), statements included.
- `narration._unanswered` (`:439`) turns that into `"answer: <player's words>"`.
- A blind add-repair has nothing to answer with, so it restates the line.

After that the model copies the pattern: the turn.15 draft imitated turn.14. Spec 017 is **not** the cause of the
echo the player saw. It only explains a separate false-positive `pc_agency` cut.

### Frequency
- Unique `answer:` items whose part is a statement (`question_kind none`): **8 of 21**, in 5 saves. All 8 are false
  positives, and 4 of them produced a PC echo ("You say, 'Thanks, friend.'", "'Fair enough,' you say", "You step up
  to Cora and ask her…", turn.14 above).
- Verbatim PC quotes delivered (a quote at least 80% made of a player part): **21 in 106 turns**. 18 came from first
  drafts (model habit) and 3 from repairs. Players complained only where the echo ended or opened the passage
  (232941 turns 14–15).

### Fit with the proposal
- **Removes the cause:** no per-part "answer" bookkeeping and no blind add.
- **Partly addresses the habit:** 18 draft echoes in 106 turns remain. They need:
  - a prompt line ("never restate the player's words; they just said them");
  - a passage-level blocking check that a quote is not at least 80% of this message's (or carried) player text.
    That is lexical and verbatim, so precision should be high, but measure it before it blocks.
- **Patch either way:** the `pc_agency` check should compare against the carried `said` words as well as the current
  message.

---

## 3. "Then:" line garbled (fighter 233000, note 18)

### Evidence
- turn.2 OFFER: `Then: demand she tell the word, saying she will be pursued after whoever the face was`.
- Reader call row 5 returned this for beat 2: `"method":"demand she tell the word, saying she will be pursued after
  whoever the face was"`. The player had typed "then I'm going after whoever it was".
- The intent was correct: "make Dunwen tell the word she says she has".
- `pipeline._then` (`pipeline.py:613`) prints `q.beat.method or q.beat.restatement` raw. `narration.py:705` does the
  same on a re-show.

### Cause
- **Model:** Haiku's Reader garbled the clause into a passive with the wrong subject.
- **Scaffolding:** the code displays an internal free-text field (`reader.md:35` defines `method` as "the act in the
  player's key words") without any check. It was chosen over `intent` in live run 015, because an intent reads as a
  promised outcome.
- Narration and spec 017 play no part.

### Frequency
17 distinct "Then:" lines across all transcripts. Two have voice errors:
- this one;
- "hiss a threat: one more swing and **I'll** break it", which slips into first person inside a second-person menu.

### Fit with the proposal
**Misses.** This is an OOF line, not narration. Fixes, in order of preference:
1. Print the player's own part text that the queued beat came from (`Then: "Tell me the word, then I'm going after
   whoever it was."`).
2. Otherwise, render from code: verb plus target.

---

## 4. "Something wrong? Type /fix" hint repeats recap text (talker 232941, note 23)

### Evidence
- The hint is printed once per session (`play/cli.py:418–420`, guarded by `hinted`). The only other place it
  appears is `turn.py:188`, after `possible_dispute`, and that did not fire in this run.
- The 232941 transcript shows the hint exactly once, after the opening (input 16). Nothing near input 23 has it.
- The player harness (`evals/playtest.py:182`) passes `text[-9000:]` as "THE TERMINAL SO FAR". When the window at
  input 23 is rebuilt, it starts in character creation and has the opening plus the hint at character 3674 of 9000.
  The player model attributed that older block to the newest output.
- The "recap" it saw is the opening's lead lines (levy, Whitcross hiring). Those really do recur later; see problem
  5.

### Cause
A harness artifact. There is no engine fault.

### Frequency
1 note in 17 runs. No engine output matches it.

### Fit with the proposal
**Not applicable.** For the harness, show only the output since the last input, with older text clearly marked. The
real repetition behind the note is the levy line, covered in problem 5.

---

## 5. NPCs repeating each other's facts, and the same facts across turns

There are four separate mechanisms.

### (a) Code re-delivers a clue that has already been found
**Evidence (232941, turn.5, input 20, notes 21–22).**
- The only record line was `R1 MUST: Lilett Mughill acts: tells you the way on: toward The Red Warren`.
- That fact had already been delivered at turn.3 (`R2 … the PC learns: You make out the way on: toward The Red
  Warren`). The case events show `clu.incident.missing.n2` with `found: True` from turn.3 onward (event 396).
- Lilett's speaker card holds nothing about Rrakaa. The only on-topic material in the packet is "public news: the
  incident itself: a child … missing since last night, and the trail leads out of the haven" and "the matter at
  hand". So she restated Belby's words: "A child, gone since last night, and the trail runs out past the last house…".

**Cause.**
- `answer._from_case` (`answer.py:175–186`) delivers a held placement without checking `node["found"]`.
- `open_node` returns the last node once every node is found.
- The pointer branch (`:189`) does check "the PC already has this lead". The delivery branch does not.
- The opening case has only 2 nodes (`gen/case.py:96–106`), so every NPC asked about the case can only repeat those
  2 facts.

**Frequency:** 1 of about 10 clue deliveries, and it is the instance the player named.

### (b) Blind repairs stitch the repetition into one turn
This is round 5's T3, confirmed across the save:

| Turn | What the repairs added |
|---|---|
| turn.2 | Two "trail" lines. One contradicts the draft ("Plain enough for any eye" against "word came off the lanes"; note 18). |
| turn.7 | Two adds that each re-name Sevella. Lilett says "Sevella" three times. The second add was cut by `not_a_repeat`, a self-inflicted catch. |
| turn.13 | Two adds, each "Mark me … a child gone since last night", taking the turn to three. |

The same pattern appears in other saves: 145410 t10, where Nibwen says "I don't know Laendil … Garwen would" three
times, and t14, where "Laendil is found at the smithy" appears three times.

### (c) Lead lines in the view, and the model copying its own sentences
**Evidence.**
- "Along the stalls the talk of the levy goes on, low and sour, and a cart wheel creaks somewhere behind the
  awnings" appears in turn.5 and again **verbatim** in turn.8 (refs `[]`).
- Levy talk also appears in turns 1, 4 and 7, so it is in 5 of 14 turns.
- Source: every NARRATOR VIEW carries `open threads: … thr.lead_2 The levy called; folk say it is only the
  beginning.` (`packet.py:409`), and RECENT EXCHANGES holds turn.5's sentence.

**Cause.**
- This has the same shape as the seeded look line found earlier: a lead line sits in every packet.
- On top of that the model copies from RECENT EXCHANGES.
- FRESHNESS (12.14.11) lists only openings.
- `not_a_repeat` checks only NPC speech against that NPC's own `said` records. Nothing checks for repeats in the
  narrator's voice.

**Frequency.** In the latest pair, 3 narrator-voice sentences repeat an earlier turn at 50% or more (4-gram
overlap), and one of them is a 100% copy. The early runs were much worse: 135029/135049 had more than 60, mostly
activity lines, since reduced by `fresh_lines`.

### (d) Feedback into speaker cards
**Evidence.** In packet.py, `speaker card` (`:534–541`) lists every shown fact whose *subject* is the NPC as
"knows:". So:
- the `/fix` "it stays" outcome wrote `fact.114 npc.sevella_de_belac correction.1 = "Lilett said she knew no one who
  keeps the Red Warren gate, then later named Sevella…"`;
- Sevella's card then read `knows: Sevella de Belac correction 1 Lilett said …`;
- at turn.13 Sevella said "Lilett Mughill wouldn't own to knowing me until she had to", a line invented from the
  player's complaint;
- `fact.103 agreed = learn what Belby would pay…` became Belby's "knows" in the same way;
- repaired duplicate lines (the four "Mark me" lines) become "they already said" lines, and the model keeps imitating
  them in turns 14 and 15.

### Fit with the proposal
**Partly addresses it.** It removes (b). It does not touch (a), (c) or (d). Each needs its own fix:
- **(a):** `_from_case` must not re-deliver a found node. The knower should answer in their own words or redirect.
  Longer term, the opening case needs more than 2 facts for NPCs to share.
- **(c):** send lead lines only when the turn touches them, as was done for the look line. Add a passage-level check
  for a narrator-voice sentence that is at least 0.8 a copy of one delivered in the last N turns (the turn.8 copy
  scores 1.0). Measure its precision before it blocks.
- **(d):** the speaker card must skip `source: correction` and `agreed.*` facts, and store whole speeches (see
  problem 1).

---

## 6. "settled between you" (talker 232941, notes 19–20)

### Evidence
turn.3 (input 18). Narrator call row 14 received:
> `R4 MUST: what changed (say it plainly; it is done): Agreed by Belby Haydale: learn what Belby would pay or give for
> Ysndil going looking for Rrakaa`

It returned the sentence `"It is settled between you that you will learn what Belby would pay or give for going
looking for Rrakaa."` (refs R4, fact.103). The narrator wrote this sentence itself. It was not a `_deliver` render: 0
render versions exist in any save.

### Cause
- `change.py:250–256` (`persuade_to`) builds `"Agreed by <who>: <_act(beat)>"`.
- `_act` (`change.py:131`) is the Reader's `intent`, which is the **PC's goal**, written about the PC. It is not an
  act the NPC agrees to do. "Agreed by Belby: learn what Belby would pay" means nothing.
- `narrator.py:294` wraps it as "what changed (say it plainly; it is done)", and must-name requires a sentence that
  cites it. The model did what it was told.
- The same words become `fact.103 agreed` and go into Belby's card on later turns.

The same mechanism also produced:
- 192926's OOF line "Now: You agrees to Ivas carries word…", the pre-018 wording that the player flagged;
- 192946 turn.7, where the refusal reason "the attempt worked, but this did not change (say why plainly): no one
  named to persuade" was narrated as "No one needed persuading, so the matter itself has not moved…".

### Frequency
7 `persuade_to` "agreed" lines in 106 turns. Of those, 1 leaked into the fiction and 1 garbled an OOF line. One more
reason string leaked from a refusal.

### Fit with the proposal
**Misses.** The narrator would still be told "say it plainly; it is done" about a nonsense line. What is needed:
- The `persuade_to` result must be the NPC's act in the NPC's voice ("Belby will name his sum once you agree to
  walk"). Take it from a Framer or Reader field written for that purpose, or from a template.
- Agreements and refusal reasons should not carry "say it plainly" imperatives.
- `agreed` facts should not be stored with intent text.

---

## 7. Repairs and the other per-part and per-sentence mechanisms

### Repairs
- 25 repair calls in 18 of 106 narrated turns.
- They had 30 targets: 28 `answer:` items (21 unique) and 2 sentence fixes.
- Judged by hand against the draft, the 21 unique items include:
  - **1 clear real catch:** 145410 t16, where "Is Laendil honest?" went unanswered. Even that repair echoed the PC's
    question.
  - **1 borderline:** 145410 t10, where the NPC deliberately deferred.
  - **19 false positives:** 8 statements or greetings, and 11 questions that the draft did answer in other words
    ("What makes you think the trail leaves town?" against "the word came to me off the lanes"; "Who here would?"
    against "Not one I'd name to you across this square").
- Because the check is lexical, repairs rarely satisfy it. **6** turns still showed "not answered" on the final
  screen after two rounds. That is the full `max_redrafts` cost, plus added redundancy.

### Other mechanisms

| Mechanism | Fired | Verdict |
|---|---|---|
| Must-name coverage of R-handles (`coverage`) | 0 missing-handle repairs | Never fired, so the self-reported refs were always complete |
| `_deliver` rendered lines | 0 render versions | Never fired |
| `_precision` blocking checks | 1 (192946 t9, season) | **False positive.** It flagged "it is the winter that drove us out… eight years back", which is speech about a past winter |
| `not_a_repeat` (speech) | 2 | Both plausible. One cleaned up a blind add |
| `pc_agency` cut | 1 (233000 t6) | False positive: the words were the player's own, carried by 017. Harmless, since it removed an echo |
| Indirect: "say it plainly" record lines narrated near-verbatim | 4 or more | Harmful ("You make out the way on: toward The Red Warren.", "settled between you", "You learn plainly that the neighbour does not know the local news…", "No one needed persuading") |
| **Unchecked: a speaker item with no quote marks** | **5 of 161 speech sentences, in 4 turns** | First-person speech delivered as bare narration (232941 t16: "Nobody has stood at this gate asking after the child that I've marked…") |

### Cause
The harm comes from coverage bookkeeping (lexical, about 6% precise) feeding blind add-repairs. The per-sentence
schema adds the unquoted-speech gap. The record lines carry "say it plainly" imperatives. The precision checks and
must-name coverage are not causing harm, but the one block that fired was a false positive.

### Fit with the proposal
**Removes most of it:**
- no per-part answers;
- one revision call that sees the whole draft;
- self-reported coverage, which is safe because must-name coverage never failed in 106 turns.

Blocking checks to keep or add, each passage-level, lexical and measured:
- `pc_agency`, with the carried words fixed;
- a PC-echo check;
- unquoted first-person speech in narrator voice;
- `not_a_repeat`;
- a narrator-voice copy of a recent sentence.

The season check should not block until its precision is measured (1 of 1 was false). Drop the "say it plainly"
wording from record lines; problem 6 shows what it does.

---

## What the proposal does and does not cover

| # | Proposal | Also needed |
|---|---|---|
| 1 Stacked dialogue | **Removes** | Side-list speeches as exact quoted substrings; `_said` stores whole speeches |
| 2 Echo | **Removes the main cause**; the draft habit remains | A "never restate the player" prompt line; a PC-echo blocking check; `pc_agency` aware of carried words |
| 3 "Then:" | **Misses** (OOF) | Print the player's own part text, or render from code |
| 4 `/fix` hint | **Not applicable** | Harness: show only the new output |
| 5 Repetition | **Partly** (removes stitching) | `_from_case` must not re-deliver a found node; lead lines only when relevant; narrator-voice copy check; speaker card skips correction and `agreed` facts |
| 6 "settled" | **Misses** | NPC-act words for `persuade_to`; no "say it plainly" on agreements or refusals |
| 7 Repairs | **Removes most** | Keep only measured high-precision blocks; add the unquoted-speech check |
