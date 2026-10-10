# R8-D1: every instruction code gives the narrator, and how often it is right

Read-only inventory, 2026-10-10, code at b6430a5. No code or data was touched. Scratch scripts live in the session scratchpad.

## 0. Method, denominators, caveats

- **Saves read (all `model_calls.request/response` for role `narrator`, plus `turns.record`):**
  - round 8: `playtest-20261010-013206-talker`, `-013226-fighter`, `-013246-explorer` (41 narrator calls);
  - round 7: `playtest-20261009-160602-talker`, `-160622-fighter`, `-160642-explorer` (44 narrator calls).
  - Total **85 narrator calls = 79 distinct turn ids**. Six repeats come from `/fix` or re-asked turns; every call is counted as one firing.
- **Parsing.** I split each packet's `ADJUDICATION RECORD` into lines. Every line was classified by its wording. "Fires" below means "appears in a packet", counted across the 85 calls.
- **Round-7 saves ran on pre-round-7-fix code** (spec 023-027 merged afterwards). A few line shapes differ from today's code: no `paused-pending` line, no `Except:` clause, Oracle lines still on. I say so where it matters.
- **"Right"** means a careful human DM, seeing the player's words, the Reader's `parts`/`restatement` and the other record lines, would agree. Three checks:
  - the line names the right person;
  - it does not contradict another line in the same packet;
  - it does not contradict the Reader's own reading.
- **I did not judge willingness values** (a die or a standing). I report whether the narration was coherent with them.
- **Obedience baseline.** All 145 MUST lines in the 85 packets were in the narrator's `covers` (0 omitted). No revision in these saves was caused by a missing MUST. So a wrong MUST line is always narrated.
  - Of the wrong NPC lines I read against the delivered prose, **every one was narrated as ordered**. That is about 14 lines, and it matches R8-I2's 9 of 9.

Class key:
- **S** = a spine fact code genuinely owns (roll result, state change, clue delivery, presence/position, willingness *value*).
- **I** = code's inference about language or judgment.
- **T** = mandatory texture or style.

---

## 1. The table

Code refs are `file:function:line`. `NL` = `engine/dm/npc_layer.py`, `NR` = `engine/dm/roles/narrator.py`, `H` = `engine/dm/handles.py`, `WS` = `engine/dm/world_step.py`.

### 1A. Record-item kinds (`H:items`, worded in `NR:_item_words`)

| # | Item / source | What it says (real example) | Class | Fires (of 85 calls) / right | If it becomes a plain fact (S) or is removed so the narrator decides (I, T) |
|---|---|---|---|---|---|
| 1 | **scene** (`H:items` scene; `NR:_item_words` 297-301) | "a new scene opens: the healer's house, morning; frame it as the arrival the beats above led to (12.4.3)" | S + T tail | 16 (4 MUST arrival, 12 "frame it first"). 16/16 right: the scene did change. | Keep the header and place as fact. The tail "frame it first / as the arrival" is style (T). Removing it risks a missed arrival, but the scene-opening paragraph in `narrator.md` already says this. |
| 2 | **beat line**: restatement, `approach:`, `difficulty:`, `acting on:` (`NR:_beat_line` 88-118) | "beat: Shove the freckled youth in the chest and demand he take back his words; approach: verb.grapple, might; difficulty: opposed; acting on: the freckled youth" | S (the Reader's reading, passed through) | 46 (34 MUST, 12 optional). The line is a faithful copy. Its errors are the Reader's (R8 fighter t8: a shove read as `verb.grapple`, "Restrained"; see R8-I3). | Already a plain fact. Hygiene issue: raw ids (`verb.talk`, `lic.training.guile_streetwise`) reach the packet in 39 `approach:` and 19 `difficulty:` fields. |
| 3 | **`result:` / `no roll`** (`NR:_beat_line` 103-111) | "result: critical success (better than hoped)"; "no roll: take_the_time" | S | 11 results, 20 "no roll". 31/31 consistent with the roll block. | Keep as fact. Dice-owned. |
| 4 | **`delivered:`** (reach-ladder words, `NR:_beat_line` 114-116) | "delivered: standard: the listener does the reasonable thing asked"; "great: Restrained"; "limited: a small concession or one standing step"; "great: unnoticed and in position" | **I** (code's prose for what a success means) | 5. Right: 2 ("unnoticed", "limited"). Wrong: 1 ("Restrained" for a shove, which the narrator wrote as "pinning him"). Vacuous: 2 ("does the reasonable thing"). | Remove the prose. Keep the reach *rung* ("great") as a value and let the narrator render it. Risk: a success rendered too small or too large. The Reader's `goal` and the `change` line (row 13) already carry the content. |
| 5 | **`it worked: the one asked answers what was asked (never a refusal, a dodge or 'not now')`** (`NR:_beat_line` 119-121, T-15-5) | R7 talker t13, R8 fighter t2 | **I** | 2. 1 harmless (R8 fighter t2, a challenge; the youth repeated his words). 1 contradicted in the same packet (R7 talker t13: this line, plus cost "he turns the round down", plus R3 "refuses… (failure)"). Right 1/2. | Remove. The `change`/`Agreed by X` line says it worked. Risk: a Talk success narrated as a stonewall; the beat's `result: success` still says it worked. |
| 6 | **paused beat** "not resolved yet: the player chooses next… never the outcome" (`NR:_beat_line` 100-102) | R7 talker t12 | S (state: unresolved) worded as an order | 8 lines. In 2 turns the narrator still pre-answered: R8 talker t15, where the informant refused the paid walk *before* the roll and the OFFER then asked 50%. | Keep as the fact "pending: not rolled". It is the narrator's only guard against narrating a roll's outcome. |
| 7 | **`not done:`** gate words (`NR:_beat_line` 112-113) | "not done: withdrawn at the OFFER"; "Without lic.lang.letters this is beyond you as tried." | S | 3. 3/3 right. | Keep. |
| 8 | **cost** (`H:items` 98-101) | "cost paid: he turns the round down and the offer goes nowhere with him" | S (the Framer's cost form, stored before the roll) | 2. 2/2 are the stored form. R7 talker t13 clashes with rows 5 and 24 (the cost *is* a refusal). | Keep. |
| 9 | **harm** | "harm to the freckled youth who issued the challenge: dead" | S | 1. Right. Contradicted by row 27 (below). | Keep. |
| 10 | **condition** | n/a | S | 0 fires, not measured. | Keep. |
| 11 | **position** (`H:items`) | "position: you at arm's reach of Aurard de Morac" | S | 5. Right in kind. 1 leaks a name the PC never learned (X1, the minted twin). | Keep. The *distance of everyone else* is missing (see §3). |
| 12 | **learned** ("the PC learns: …") | n/a | S (clue delivery) | **0 fires in 85 calls.** Every clue delivery in these saves arrived as an `npc … acts:` line (rows 22). | Keep as the clue channel. It must carry the fact and who may say it. |
| 13 | **change** ("now so: …", "X agrees to what was asked") (`H:items` 124-130) | "the soldier off duty agrees to what was asked" | S (the Persuade result) | 7. 7/7 consistent with their rolls. R7 explorer t4 sits beside an Oracle "no" (row 14). | Keep. |
| 14 | **oracle** ("question "…": the answer is yes") | R7 explorer t10: "the refugees are resting somewhere in the house: the answer is yes, and chase a curse" | **I** (a model-invented yes/no, answered by dice, presented as truth) | R7 only: 8 (0 in R8). Of 5 checked, 2 contradict another line (R7 fighter t4: oracle "yes, will name the place" vs a table refusal; R7 explorer t4: "no" vs "agrees"), 1 produced invented lore ("Something's chasing them… A curse"), 2 harmless. Retired in R8 (0 Oracle calls). | Already off. Do not bring it back as a MUST. |
| 15 | **omen** | n/a | S | 0, not measured. | Keep. |
| 16 | **note: inciting incident + "reporter: X"** (`session.py:~245`) | "the inciting incident: a quarrel in the inn turns to a challenge… reporter: Betric Brightcote" | I (code names who tells it) + T | 6 (every opening). 6/6 used and fine. | Pass the incident as a fact and the present candidates. Let the narrator choose who tells it. Risk: none seen; the narrator did this unprompted in R8 explorer t1. |
| 17 | **note: "a lead to make noticeable"** (MUST) | "The hunters of Crowstead is hiring, and asks no questions" | S (lead delivery) + T (every lead named in the opening) | 12 (2 per opening, 6 openings). Grammar of 4 is broken ("X is hiring" used as a thread name). | Keep as lead facts. Hand the gist, not a sentence. Risk: a missed lead (the point of the MUST). |
| 18 | **note: "a lead arrives (form): it points toward X, through X"** | R8 talker t8 and t14: "it points toward The Crowbridge Circle is hiring, through The Crowbridge Circle is hiring" | S (director's injection), garbled | 2. Both turns were mid-conversation. The narrator had Helian say "Mark this, then. The notice on that board is the Crowbridge Circle's hand" (t8): a forced aside on an unrelated question. 2/2 delivered, 0/2 well-formed. | Keep as a fact with a clean source and target. |
| 19 | **note: "the scene opens interrupted: {raw dict}"** | R7 talker t7: `{'source': 'interrupted_scene', 'focus_roll': 94, …}` | S, but a raw Python dict in the packet | 1 (optional, so ignored). | Hygiene. |
| 20 | **activity** item kind (`NR:_item_words` 331-335, "say only this of it, never otherwise") | n/a | T | 0: `H:items` never builds this kind. Activities reach the narrator only as OPTIONAL MATERIAL (row 31). Dead code path. | n/a |

### 1B. NPC `acts:` lines (`record.npc_actions` → `H:items` kind `npc`; one channel for six different things)

| # | Source (code path) | What it says (real example) | Class | Fires / right | If a plain fact (S) / removed so the narrator decides (I) |
|---|---|---|---|---|---|
| 21 | **willingness line** `willing / guarded / unwilling` (`NL:respond` 606-614 → `ans.willingness` → `answer.WILL_WORDS`, `WS:answer_line` 199) | "Betric Brightcote acts: answers what you asked, willingly (a plain question to a neutral listener): in her own words, from what they know or have heard" | **S for the band** (a standing/roll value, held for the scene) **+ I for who** (`NL:addressed` 245-270 re-guesses the addressee from words) | 37 willing + 0 guarded + 5 unwilling. **Band: 5/5 unwilling lines coherent** (the narrator refused with a pointer or a closed door). **Addressee right 38 of 42 (90%).** The 4 wrong are all round 8: explorer t6, t12, t16 and talker t10. With the plain-speech row 22 (one more wrong, talker t11) the family is 40 of 45. In round 8, 17 of 22 right (77%); in round 7, 23 of 23 (players had named the NPC). In all 5 the Reader's `restatement` named the right person. | **Keep the band as a per-NPC fact** ("Betric: willing, neutral"). **Drop "who answers"**: the narrator picks the speaker from the Reader's target and the conversation. Evidence for that: see §4, where the narrator picked the right speaker in 14 of 14 calls that carried no NPC order, including R8 explorer t5, where code's `addressed()` returned nobody. Risk: NPCs too agreeable (§5). |
| 22 | **plain-speech reply** `replies, willingly` / `turns you away` (`NL:respond` 607-610) | "Helian Lanent acts: replies, willingly (a plain question to a warm listener)" | S band + I who | 3. 2 right (R7 explorer t13 thanks, t16 greeting); 1 wrong (R8 talker t11: Helian "replies" to a call aimed at the woman, and the narrator wrote Helian's voice "over the chain" while the PC was up the road). | As row 21. |
| 23 | **fact-answer / pointer / name** (`answer.ask` → `WS:_speech_answers` 209 → `answer_line`) | "the sellsword acts: does not know what the omen shows, but Kerric Hartsmith would"; "Roswen Tumbottle acts: gives their name"; "refuses… and names one person who would know: Gribnik of the Roof Clan, found at the hall" | **I** (which clue route fires, for which question) over S (the case graph's content) | 5. Right 2: the name (R7 explorer t7) and the Gribnik pointer inside a refusal (R8 explorer t8). Wrong 3: R7 talker t9 (asked "Have you signed with Morri's Wolves?", the order was the omen, because the part was `what_happened`); R8 talker t9 (the omen clue delivered by the wrong speaker, Helian, to a question put to the woman); R8 talker t10 (an invented "someone at The Still Ruins would" for "where are you headed", wrong speaker too). | Make the clue a **delivery fact** ("the PC learns: X; known to: A, B"), not an NPC act. The narrator chooses who voices it. Risk: a missed delivery, because nothing obliges anyone to say it. Keep the MUST on the *fact*, not the speaker. |
| 24 | **talk_outcome "agrees to what you ask"** (`NL:talk_outcome` 486, `respond` 596-604) | R8 fighter t2: the PC's "Say it to my face" challenge became "the challenger acts: agrees to what you ask" | I | 1. Right in effect, wrong in wording (nobody asked for anything). | Replace with the `Agreed by X: <goal>` change line (row 13). |
| 25 | **voiced refusal** from a talk failure or table row 2-3 (`NL:voiced_refusal` 494) | R7 talker t13: "refuses, in their own voice…: the talk did not move them (failure)" **in the same packet as** "it worked: …never a refusal" and "success at cost"; R7 fighter t4: "ends the talk and turns away" for a trivial no-roll press, beside Oracle "will name the place: yes" | I | 2. **0 right.** The narrator followed the refusal both times; the player noted "Magby keeps dodging… feels like a dead end" (R7 fighter [20]). | Remove. A refusal that matters is a recorded refusal (row 26) or a failed roll (row 3). |
| 26 | **recorded refusal** "bristles: will not harm a child or an innocent" (`NL:respond` 631-637; tags from `event_tags`) | R7 fighter t7: the PC picks Magby's pocket with a **critical success, "unnoticed and in position"**; the packet also says "Magby Applefoot acts: bristles: will not harm a child or an innocent"; the narrator wrote "Magby's shoulders lift… He bristles at nothing you can see" | I (a low-precision tag match: the pocket-pick was tagged `harms`) | 1 MUST + 4 optional bystander versions (row 30). **0/1 right** (contradicts "unnoticed"). | Pass the refusal as an NPC fact ("Magby: will not harm an innocent"), not an act. The narrator can then use it when it applies. Risk: none seen. |
| 27 | **recorded want** "acts on a want: recover their freedom; gives part of what was asked; they do not give the PC what was asked" (`NL:respond` 638-646) | R7 explorer t11 (the beat said "success… Agreed: a smaller part") | I | 1. Self-contradictory string; the narrator ignored the "want" deed and wrote a partial yes. 0/1 right as written; harmless in effect. | As row 26. Risk of fact form: narrator invents the want's deed. A rule line "do not act a want unless a record line does" covers it. |
| 28 | **practice table row** (`tbl.npc_action` d10 + standing, clamped by `tbl.npc_practice`; `NL:respond` 647-667) | R8 talker t9: the bored woman "acts: goes after something they want"; t11: "keeps working and pointedly ignores the PC"; R8 fighter t12: the youth, **dead** (R2 "harm… dead"), "acts: flees or takes cover"; R7 fighter t15: "greets warmly and listens" | I (a die turned into a deed) | 4 MUST. **1 right** (R7 f15). Wrong 3. Narrator obeyed all: t9 "shoulders away up the road, quick and purposeful, after something she has plainly been wanting", invented the causal link "At the captain's words…"; t11 "Not now. Go and stare at the sky"; t12 "dives into the shadow like a hare… He is dead" (the player: "confusing"). **Persisted as state**: the t11 row wrote `detail.manner = "pointedly ignoring you"` as a scene fact (`events` seq 512, `source tbl.npc_action:3`), live until t14. | Remove. This is the clearest wrong class: it fires without looking at the NPC's actual state (dead, mid-conversation, wrong person). If the owner wants NPC initiative, it must come from a record line that names a *state change* (e.g. a departure), not from a table gist. |
| 29 | **foe behaviour** (`WS:_foe_turn` 74; `beh.default_melee`) | "the freckled youth acts: strikes at you and misses"; "strikes you and lands it: you are worn" | S (dice + Vitality change; conflict mode) | 3 (R8 fighter t8, t9, plus a repeat). 3/3 are engine events with RESULT blocks. The player noted "hit landed without any roll… shown as pinned, then suddenly free" [25]; that is R8-I3's misread-grapple, not this line. | Keep as a fact ("the youth struck: hit, you are worn"). |
| 30 | **optional bystander reaction** (`NL:respond` tags `optional`; `NR:optional_material` 343-358) | "Ghazka Who Came Back, not addressed: bristles: will not harm a child or an innocent (a brief deed at most; no words unless it says so)" | I | 5 (R7 fighter t7 hedge-mage, t13 Magby "offers a word of help unasked"; R7 explorer t7 Morga; R8 fighter t8, t12 Ghazka). **Used by the narrator: 0 of 5.** Plausible: 2 of 5 (Ghazka). Wrong/irrelevant: hedge-mage (the pocket-pick was unnoticed); Magby on a *withdraw*; Morga. | Remove. Zero cost: it was never used. |
| 31 | **optional activity** (`NL:ensure_activities` 94-127, a d6 pair on `tbl.npc_activity` by role × watch) | "the people of Redcrag gathering to look at the sky is on an errand"; "the quarrelling patrons of the Red Plough is going about his morning work"; "Betric Brightcote is stirring a pot of porridge" | T / I | 58 lines. 37 (64%) are vacuous ("going about their morning work", "on an errand", "talking with a neighbour"). Of the 21 specific lines, 16 used. Group entities get one person's activity. Persisted as `detail.activity` facts ("on an errand" for a crowd looking at the sky). | Remove the vacuous; let the narrator describe the room from the view. Keep any specific activity the Reader or a record line wrote. Risk: bland rooms; the narrator already dresses rooms freely. |
| 32 | **response-writes** (`scene_state.response_values` / `write`, `pacing.yaml details.scene_writes`) | `detail.manner = "pointedly ignoring you"` | I stored as state | 1 observed (row 28). | Do not write inferred reactions as facts. |
| 33 | **`_withheld` suffix on every refusal** (`NR:_withheld` 127-142) | "…; the PC does not get what was asked: show it plainly and visibly (a word, a shake of the head, a hand lifted for not now, a turn back to other business) so the player knows not to wait for an answer; the reason shows only from this…: manner: stern; standing toward the PC: wary" | **T** (a gesture menu) | 8 firings (3 `unwilling`, 2 voiced, 1 want; some repeats). **8 of 8 delivered prose contain a lifted hand or palm** ("lift one hand… palm out" ×4 in R7, "lifts one hand… palm toward you" R8) or "turns his back". | Remove the gesture list. Keep the principle ("make the refusal plain so the player knows not to wait") in `narrator.md`. Risk: an ambiguous refusal; mitigated by the willingness fact. |

### 1C. Standing guidance lines added to the packet

| # | Source | What it says | Class | Fires / right | If removed / made fact |
|---|---|---|---|---|---|
| 34 | **`_speech_line`** (`NR:_speech_line` 145-178) | "the one the PC addressed answers in quoted words…; Nobody else present speaks or interjects unless the optional material gives them a reaction. Never write that their words are lost…; never end on waiting for them to speak" | **I + T** | 65 of 85. 56 sit with an NPC order. **9 have no NPC order** (5 pause turns, 1 scene move, R7 fighter t13 "withdraw", R8 fighter t15, R8 explorer t5). On the 5 pause turns it tells the narrator not to "end on waiting" while the pause rule says to stop at the pause (round 7 had no `Except:` clause). In the 5 wrong-addressee turns it reinforced the wrong person ("the one the PC addressed"). | Reduce to style (quote speech; speaker card first). Delete "the one addressed answers" and "nobody else interjects". Risk: extra speakers. At present, with no order, the narrator added none (§4). |
| 35 | **pending** ("X has not answered what the paused beat asks…") (`NR:_speech_line` 163-168) | | S | 3 (round 8). 3/3 right. | Keep as the fact "unanswered". |
| 36 | **`_reading_lines`** (`NR:_reading_lines` 223-274) | "the character reads the hire notice: quote its words exactly, in quotation marks: …" | **I** (which written thing the words refer to), S text | 6 quote-lines in 6 packets + 1 "cannot read" (R7 fighter t1, "the any posted notice"). **Quote-lines: 0 of 6 right**: R7 talker t4 (a question to the captain), and R8 talker t3, t3, t4, t5, t7, where the PC read the **gate log** and the code quoted the **hire notice** (R8-I2 §2a). The narrator quoted it twice, and the player noted "same hire-notice paragraph… repeated". | Give the facts ("the gate log: contents unknown / the hire notice says…; the PC can/cannot read"); drop "quote exactly". Risk: invented text for the log, so the log needs real content or a stated "nothing more". |
| 37 | **end-handback** `- end by handing the moment back (12.14.9)` (`NR:record_text` 391-392) | | T | 63 of 85. Passages end in `?` in 22 of 63 (35%); the rest end on an image. Player notes: "narration keeps ending on the same 'hands hover' beat"; "the question at the end is a bit open-ended". | Remove; `narrator.md` already says it. |
| 38 | **pause stop** `- the turn stops at a pause: stop at the moment before it` | | S | 6 (round 7). Fine. | Keep. |
| 39 | **lethal warning** | | S | 0. | Keep. |
| 40 | **purpose line + length ceiling** (`PURPOSE_LINES`, `Length: at most N words`) | | T | 85. | Style; keep or move to the prompt. |
| 41 | **record header** "narrate exactly this, no better and no worse… narrate every line marked MUST" and the `MUST` flags (`NR:record_text` 373-381) | | I / T (an obligation) | 145 MUST lines. 145 of 145 covered. Of those, **about 14 were wrong** and narrated anyway. | Narrow MUST to dice results, state changes and clue deliveries. |
| 42 | **SCENE SETTING header** "people here act only as the record says" (`packet.py` 595-598) | | **I** | 85 of 85. | This sentence forbids the very judgment the owner wants to restore. |
| 43 | **SPEAKER CARD header** "answer from this first; beyond it, plainly, with ordinary confidence; a hedge only if…; never open by saying their own name" (`packet.speaker_card`) | | T | 61 cards. | Style. Card contents (`knows`, `said`, `public news`) are S. |
| 44 | **`narrator.md` standing lines** | "NPCs act only as the record says: each response is a record line. You choose their words and manner, never their deeds or whether they agree"; "OPTIONAL MATERIAL… sparingly"; "Voice standing as behaviour: Hostile, open enmity…"; "A refusal is spoken in their own voice, never silence"; "The one addressed answers from their SPEAKER CARD, within their willingness"; "Narrate every record line marked MUST… Acknowledge what the player tried" | I (first, fourth-last) + T | Present in 85 of 85. | The first line is the structural switch: replace with "an NPC reacts in character to the facts you are given; you may add speech and gesture, not state changes". |
| 45 | **`(answered)` mark** on every SPEECH part (`turn.py:319`; set unconditionally) | `- part [SPEECH] "…" (answered)` | I (claims code answered it) | 98 of 160 part lines. 6 of 54 SPEECH turns have no NPC order. R8 explorer t5 shows `(answered)` with no answer given; the narrator answered anyway. | Remove the mark. |
| 46 | **naming order** `call them "the sellsword between contracts", as every other screen does` (scene `present:`) | | T | in every scene packet. | Style. |

---

## 2. Summary counts

**Kinds listed: 46 rows** (15 + 5 + 19 + 6 + 1 dead path).

| Class | Kinds | Rows |
|---|---|---|
| **S** (pure spine) | 15 | 2, 3, 6, 7, 8, 9, 10, 11, 12, 13, 15, 29, 35, 38, 39 |
| **S + T/I** (a fact worded as an order, or with an order's tail) | 5 | 1, 17, 18, 19, 21 (the band half; its "who" half is I) |
| **I** (code's inference) | 19 | 4, 5, 14, 16, 22, 23, 24, 25, 26, 27, 28, 30, 32, 34, 36, 41, 42, 44, 45 |
| **T** (texture or style) | 6 | 31, 33, 37, 40, 43, 46 |
| dead path | 1 | 20 |

Of the 19 I-class kinds, 9 sit on the NPC channel (rows 22-28, 30, 32; row 21 adds an I half) and 10 are item prose, notes or standing guidance (rows 4, 5, 14, 16, 34, 36, 41, 42, 44, 45).

**Precision of the I-class orders** (calls, 85 total; "right" per §0):

| I-class order | Fires | Right | Precision |
|---|---|---|---|
| Willingness / plain-speech lines: addressee only | 45 | 40 | 89% (R8 alone: 17/22 = 77%; R7: 23/23) |
| Fact-answer / pointer / name | 5 | 2 | 40% |
| Talk "agrees" (24) + voiced refusal (25) | 3 | 1 | 33% |
| Practice table row (28) | 4 | 1 | 25% |
| Recorded refusal "bristles" (26) + want (27) | 2 | 0 | 0% |
| Optional bystander reaction (30) | 5 | 2 plausible, 0 used | 40% (and unused) |
| Reading quote orders (36) | 6 | 0 | 0% |
| `delivered:` prose (4) + `it worked` (5) | 7 | 3 | 43% |
| Oracle MUSTs (14, R7 only) | 8 (5 checked) | 3 of 5 | 60% |

- **All "reaction" orders together** (rows 24-28 and the fact-answer and bystander rows; everything except the addressee/band line): **24 fires, 8 right (33%)**.
- **Addressee/band lines** (the high-volume one): **89% right**. But where it is wrong, it is wrong in the worst way: 5 wrong, with the wrong NPC's speaker card attached.
- **No sampled I-class order was ever refused by the narrator.** The narrator is obedient; the quality of its output equals the quality of the order.


---

## 3. Spine facts the narrator must still receive, and in what form

| Fact | Form needed | Evidence for why |
|---|---|---|
| Roll results per beat (degree, near miss, success at cost, no roll) | `result:` value; `pending` while a pause holds | Rows 3, 6. The one pre-answer in R8 talker t15 happened where no `pending` line applied. |
| Costs, harm, conditions, holds, who holds what | Typed lines as now (rows 8, 9, 10, 13) | 0 contradictions found among them. |
| Persuade/Talk result and what it changed | `Agreed by X: <the PC's goal>`; the narrator renders the NPC's yielding | Row 13: 7/7 right. |
| **Who is present, where, and how far** | A `present:` list plus **distance bands for everyone**, not only the PC's own range | R8 talker t9-t11: "Helian's voice carries from the gate" while the PC stood beside the woman up the road. The narrator needed a fact it did not have: "Helian: at the gate, not within earshot of the road." `lines()` builds position bands, but `fresh_lines` drops position slots after scene start (`NL:fresh_lines` 130-140). |
| **Willingness values** | One line per **present NPC**: band + reason ("Betric: willing, a plain question to a neutral listener"; "the sellsword: wary, will refuse this topic") | Rows 21-22: 5 of 5 refusals coherent. Give it for everyone so the narrator picks the speaker, not code. Persist as now (per scene, DL-12-118). |
| **Clue deliveries** | A delivery fact ("the PC learns: X") plus **who may say it** (the knowers present). Required (MUST) on the *fact* | Row 23: 3 of 5 wrong because the order named the speaker. Row 12: 0 `learned` lines, because the NPC-act channel was used instead. |
| Pointers ("who would know") | A fact: "A knows this and is found at the hall" | Row 23: the right one (Gribnik) was narrated well. |
| Recorded refusals and wants | NPC data facts, not acts | Rows 26-27: 0 of 2 right as acts. |
| Foe attacks (hit, miss, Vitality change) | As now | Row 29: 3 of 3 are engine events. |
| Scene and time change; lead and incident facts | Header + the lead's gist, cleanly formed | Rows 1, 17, 18. |
| Reading: what written things exist, their text, whether the PC can read them | Per-item facts, not an order to quote | Row 36: 0 of 6. |
| Standing / manner of each NPC toward the PC | A value ("friendly"), not a behaviour sentence | `narrator.md` already maps standing to behaviour. |

---

## 4. What the narrator does when code gives it no order

I compared the narrator's `speech` speakers with the NPC orders in the same packet.

- **14 of 85 calls have a speech passage but no NPC `acts:` line.** They are openings (6), pause turns (5: R7 talker t12, fighter t11, explorer t10, t12, R8 talker t15) and 3 others (R7 fighter t13 "withdraw", R8 fighter t15, R8 explorer t5).
- In all **14** the narrator picked a sensible speaker. The clearest case is **R8 explorer t5**: `addressed()` returned nobody. The player wrote "I step toward the sellsword and quietly ask him…", and the narrator, with the Reader's restatement and RECENT EXCHANGES, had the **sellsword** answer. It was correct, and the answer was good.
- In the 6 wrong-addressee turns of R8-I2 (5 here plus the talker t9 clue) the Reader's `restatement` named the right person every time. I cannot prove the narrator would have picked right in those 6 (it was never left to), but it did in all 14 turns where it was left to.
- Caveat: I have no packet where code withheld the willingness fact for a hostile NPC, so "NPCs too agreeable" is untested (§5).
- One scaffolding artefact (not a code order): R8 talker t15 attributes the informant's speech to `npc.fenine_hartbrook`, a market-square person. The new scene's closed `speech` enum did not contain the informant, so the narrator had to pick one. It is the closed list of speakers (built from the packet), not the narrator's choice.

---

## 5. Risks if the I-class orders are removed or turned into facts

- **NPCs too agreeable.** The model's default is cooperative. In the no-order calls it answered helpfully (R8 explorer t5) but it also refused a paid ask before the roll (R8 talker t15) and wrote its own refusals well. I have no sample of a hostile NPC without an order. Mitigation: the willingness *value* stays a fact for every present NPC.
- **Narrator inventing deeds.** Without row 28, the narrator may have NPCs leave, attack or flee. `narrator.md` already says "never their deeds"; keep a version: speech and gesture only; a state change needs a record line. Test trap: the player liked the woman rushing off (talker [28]), which was a code accident that created a story beat. Whether to allow initiative is a design choice, not a defect of this change.
- **A missed clue delivery.** Today a clue is delivered because a MUST line names a speaker. If the clue becomes a fact with no named speaker, nothing *makes* an NPC say it. Keep the MUST on the delivery fact (the narrator must narrate that the PC learns X, from any knower present).
- **Two NPCs speak at once.** Not seen in any no-order call (§4), but the "nobody else interjects" line has never been absent. Watch it.
- **Wrong or missing speaker attribution** for the `speech` side list: the closed enum depends on `present_npcs`. That list must be right (X1: minted twins).
- **Test traps.** A test that asserts "the addressee has an `acts:` line" would fail under the change. Rows 20, 34 and 45 are the likely places.

---

## 6. Causes shared across rows

1. **One channel, `record.npc_actions`, carries six kinds of thing:** willingness (S), clue delivery (S), table rows (I), wants and refusals (I), foe attacks (S), bystander reactions (I). All are rendered as `X acts: …`, all MUST except the bystander ones. The narrator cannot tell a die from a deduction.
2. **MUST coverage turns every wrong line into required prose** (145/145 covered, no revision for omission).
3. **Re-guessing the Reader.** Rows 21-23 and 34 rest on `NL:addressed`, which ignores the Reader's restatement. In the 6 wrong cases the restatement was right.
4. **Inferred reactions stored as state** (rows 28, 31, 32): `detail.manner`, `detail.activity`, `crowd_response` live as scene facts, so a wrong guess outlives its turn.
5. **State-blind rules** (rows 26, 28): a refusal tag matched a pocket-pick; a table row fired for a dead man; a dice reaction fired for the wrong person.
6. **Mandatory texture** (rows 31, 33, 37): all 8 refusals contain the same gesture; 64% of activity lines say nothing.

## 7. Anti-pattern check (handoff §3.3)

- **Code authoring narrative truth:** rows 4, 5, 14, 16, 22-28, 31, 36.
- **Low-precision blocking/ordering checks:** rows 26 (a `harms` tag on a pocket-pick), 36 (word overlap picks the notice), 23 (`what_happened` matches the omen).
- **Over-triggering:** rows 28, 30, 31 fire every turn the NPC is "engaged" or present.
- **Mechanics stored as text:** row 32, plus `detail.activity` on a crowd.
- **Blind calls:** the narrator is asked to write NPC speech with no view of the Reader's own `addressee` (there is none).
- **Mandatory texture:** rows 17, 33, 37.
- **Test traps:** §5.

## 8. Files read

`engine/dm/handles.py`; `engine/dm/roles/narrator.py`; `engine/dm/roles/prompts/narrator.md`; `engine/dm/npc_layer.py`; `engine/dm/answer.py` (willingness, `WILL_WORDS`); `engine/dm/world_step.py` (`deliver_learning`, `answer_line`, `_speech_answers`, `_foe_turn`); `engine/dm/scene_state.py`; `engine/dm/turn.py` (parts marks, lead injection); `engine/dm/session.py` (opening notes); `engine/dm/packet.py` (`speaker_card`, scene setting); `rules` `tbl.npc_action`, `tbl.npc_practice`. Saves: the six listed in §0. Prior reports: `R8-I2-npcs.md` §1, §9; `ROUND8-ANALYSIS.md`.
