# R8-I1. Narration and text: traced to causes (round 8, b6430a5)

Saves: `playtest-20261010-013206-talker`, `-013226-fighter`, `-013246-explorer` (opened read-only). Transcript input
`[NN]` maps to `turn.(NN-15)` in all three saves; a note at `[NN]` is about the output of the turn before it. Every
claim below was checked against `model_calls.request`/`.response` and `turns.record`. Scratch scripts are outside the
repo.

## Summary: the causes

| # | Symptom | Root cause (what actually happened) | Model or scaffolding | Frequency |
|---|---|---|---|---|
| 1 | The hire notice is quoted again and again | **This is not spec 027's description path.** The doc text was in the view only at the opening. The repeats come from `_reading_lines`, which tells the narrator to *"quote its words exactly"*. It **picked the wrong document**: the player was reading the **gate log**, which is not counted as a written thing (no `text` fact, and "log" is not in `_POSTED`). So the lone posted notice won on the "a read verb with one written thing in view" fallback. Two **lead injections** also pushed the already-delivered hiring hook as MUST notes. | Scaffolding | Code pushed the hiring in **7 of 14** talker turns. Quoted verbatim in 3 deliveries. The narrator obeyed the reading line in 2 of 4 turns. |
| 5 | A stall: "waiting on your reading" | Nothing owns what the gate log says. The log has no text, and the cart lead (`thr.lead_2`) has no authored terms, case or clue. Rule 12.14.13 forbids the narrator writing a clue. Yet `turn.py:316` stamps every FICTION_QUESTION "(answered)". The narrator had a MUST "to learn … what it says about the cart" with nothing to say. | Scaffolding (an impossible record) | turn.4, then deflections to the book at turn.5 and turn.8. The three empty reads also tripped the inconclusive streak, which fired the lead injection behind symptom 1. |
| 3 | Helian shouts from the gate | `npc_layer.addressed` had no name match, so it fell back to "last spoken with", which was Helian. "ask her", "Wait, friend!" and "Friend, a moment!" never resolve to the woman. Code then wrote MUST lines for Helian: clue delivery at turn.9, answers at turn.10 and turn.11. Her repeated gate-log line at turn.11 is a forced "replies" with nothing asked. Her own earlier gate-log line had dropped out of the 6-line "already said" window. | Scaffolding | 3 deliveries (turn.9–11). Five player notes cite them because the persona sees the last 9,000 characters. |
| — | Misattributed speech (round-7 target) | **The same cause as symptom 3.** `addressed()` uses regex and word overlap. On explorer turn.6 the fallback picked Betric. On turn.12 `described_in` matched one word ("walk" ~ the guard's "walking a patrol"). On turn.16 it matched "Stanwall". The narrator voiced exactly whom the MUST line named. | Scaffolding | **6 of 36** narrated turns (17%); 2 were disputed with `/fix` |
| 4 | Incoherent death | The record had two MUST lines: R2 "harm to the freckled youth: dead" and R4 "the freckled youth acts: **flees or takes cover**". `npc_layer.respond` gives a dead NPC a response row (the `person()` test has no harm check). The narrator reconciled the two: hit, then "dives … like a hare", then dead. R3 "position: you at arm's reach of **Aurard de Morac**" is code text with the true name (`pipeline.py:530`). The narrator did not leak it; the RESULT line did. | Scaffolding | 1 of 1 kill |
| 2 | "Hands hover" (Gribnik) | **No packet held any of it.** The pen, margin and hands are the narrator's own earlier closings, which it sees in RECENT EXCHANGES. Every record ends with "end by handing the moment back (12.14.9)", and 12.14.9 allows "an unresolved image". | Model, invited by a mandatory closing slot | Gribnik: 4 of 4 deliveries close on her hand, the page or the pen. Overall 18 of 36 deliveries end on an image. |
| 6 | A thin "what do I know" | `codex.what_you_know` is code only. `_about` returns on the first name match (the Long Downs region) and never searches threads: `thr.sit_long_downs_wound` holds "the winter". It never searches testimony either: Betric's banners and winter answer is a `said` record, and the journal never reads those. | Scaffolding | 1 of 1 |
| 7 | Jargon in RESULT and OFFER | Code strings: `pipeline.py:413` writes "· success · evidence as a no-roll success" (spec 023, T6); `oof.py:451` writes "Fate: 1 (no reroll: you won't see this die)" on a secret frame. | Scaffolding | 4 of 4 take-the-time RESULT lines; 1 secret OFFER |

**Causes that differ from what was suspected.**
1. Spec 027 did not miss documents. A *reading* bypasses it by design, and it is the reading detection that is
   wrong.
2. Symptoms 3 and 5, and the misattributions, are not narrator behaviour. They are **upstream MUST lines** built by
   code that guessed the wrong person, or that had no content to give.
3. The death narration is a **code MUST line telling a dead man to flee**.
4. All 5 of this round's revisions were **false positives** of blocking checks. The real first-draft rate is 100%.

**Shared causes.**
- **(A) Code-built MUST lines from low-precision guesses.** The reading target, the addressee, a response row for a
  dead NPC, and the lead-injection thread are each guessed by regex, word overlap or a fixed ladder while a typed
  answer already exists: the Reader's beat target, the Director's `lead.thread`, the harm state. A is behind symptoms
  1, 3, 4 and 5 and the misattributions.
- **(B) Content with no owner.** An unwritten document and an open lead with no terms give symptom 5. Through the
  inconclusive streak they also feed symptom 1.
- **(C) A harness artefact.** The persona sees the last 9,000 characters (`evals/playtest.py:182`), so older repeats
  are re-reported. This affects notes [24], [25], [27], [29] and [30].

---

## Round-7 targets on these saves

The numbers come from `specs/019-holistic-narration/metrics.py`, `specs/024-texture-outcome/measure.py` and hand
checks.

| Measure | Round 7 | **Round 8** | talker / fighter / explorer |
|---|---|---|---|
| Narrated turns | 43 | **36** | 14 / 9 / 13 |
| Paragraphs kept (every draft paragraph present in the delivery) | 0 of 43 | **36 of 36** | spec 024 P1 works |
| First draft delivered | 98% | **86%** (31 of 36) | 93 / 78 / 85% |
| Real first-draft rate (after removing false-positive blocks) | — | **100%** | 5 of 5 revisions were false or doubtful (see below) |
| Narrator calls per narrated turn | 1.02 | **1.14** (41 of 36) | 1.07 / 1.22 / 1.15; all extra calls are those revisions |
| Stacked quotes | 1 | 1 metric hit, 0 real | explorer turn.11 is one speaker continuing in a new paragraph |
| Code sentences or labels leaked | — | **2 minor** (+2 forced quotes) | "the sellsword between contracts" (explorer turn.2); "about her morning work" (explorer turn.9, the optional-material template); the forced notice quotes (talker turn.4, turn.7) |
| Pronoun drift in deliveries | — | **0 real** | the pronoun check blocked 3 times, 0 real: see the pronoun check below |
| Misattributed speech | 1 (model) | **6** (code) | talker turn.9, 10, 11; explorer turn.6, 12, 16 |
| Habit repeats per NPC | 16 of 21 | **all habit hits are stem false positives** | Falbo's "long tale" stems matched "a long walk" and "a long moment"; Gribnik's saint oath 1 of 4; Betric 1 of 2 |
| Look repeats per NPC | — | Ghazka: 1 of 1 speaking turn, **4 of 9** deliveries. Belo: 5 of 5. Helian: 2 of 7. Gribnik's mud: 1 of 4 | Ghazka: same-place scene re-openings (see the scene re-openings below). Belo: the look is her only usable handle (see Belo's label below) |
| Closing on an image, not a question | 28 of 43 | **18 of 36** | 14 end on a question, 4 on an NPC's words |
| Room re-described | — | fighter **4 of 9** (turn.1, 3, 6, 13) | each is a new Director scene in the same room |

**The pronoun check** (`pronoun_certain_subject`, `claims.py:1474`) blocked 3 times, all false:
- fighter turn.6: "the iron rings on **his** fingers" (the youth);
- fighter turn.9: "drawing **his** arm back" (the youth);
- explorer turn.1: "over **his** cup" (the sellsword).

Each time the subject it chose was the last *named* she/her person (Ghazka or Betric). People known only by a
description are invisible to its index. This was also the cause in round 7 (0 of 1). Its config entry has **no
`precision`**, so it blocks (`claims.py:1468`, `blocks = measured is None or …`), although `min_precision: 0.95`
(pacing.yaml:94) says to log only when below.

**The repeat check** (`not_a_repeat`, `narration.py:356–366`) blocked twice:
- talker turn.3: "Nibly taught me the pike before he taught me the book". This is not a repeat. A short line that
  shares names gives a high overlap.
- explorer turn.8: a callback to "staring at rings". This is doubtful.

It also **missed** the one real repeat (talker turn.11's gate-log line, overlap about 0.45 < 0.6).

**The scene re-openings** (DL-12-99/122): fighter had 4 scenes in one room. The Director cut on "agenda answered"
with no change of place. `narrator.py:476` sets `full = purpose != "turn"`, so each `scene_open` re-sends the full
SCENE SETTING: look, furniture and everyone's look (`packet.py:626`). That gave "grey light … shutters … chalked
prices" 4 of 9 times, and "(she/her, old, one clouded eye, bored)" on Ghazka's `present:` line.

**Belo's label:** Belo is one woman labelled "the people of Redcrag gathering to look at the sky" (a crowd label).
The narrator has to call her by her look, "the woman with silver-streaked hair". That is not texture. It is a casting
or label issue for the NPC lane.

---

## 1. The hire notice repeated (talker)

**What the player saw.** The notice was quoted verbatim:
- in the opening;
- at [19], turn.4: "…its words carry plainly from where you stand: "WANTED: able hands…"";
- at [22], turn.7: the same.

Helian paraphrases it at turn.8. The woman mentions "his notices" at turn.13 and turn.14. Notes:
- [20]: "I got the notice repeated instead";
- [23]: "for the third time" (correct: 3 verbatim);
- [24], [25]: "nearly every reply". There were no notice quotes after turn.8. Both outputs before those notes still
  had turn.7's quote in the persona's 9,000-character window.

**The packets.**

| turn | `doc.lead_3` text in NARRATOR VIEW? | Line in THIS MESSAGE | Delivered |
|---|---|---|---|
| 1 (opening) | **yes** (fact.72: the first appearance, as spec 027 intends) | R4 MUST "a lead to make noticeable: The Crowbridge Circle is hiring" | quoted (the narrator's choice, fine) |
| 3 | no | `- the character reads the hire notice: quote its words exactly, in quotation marks: "WANTED: …"` | not quoted |
| 4 | no | same | **quoted** |
| 5 | no | same | not quoted |
| 7 | no | same | **quoted** |
| 8 | no | R2 MUST "note: a lead arrives (A plea for help…): it points toward The Crowbridge Circle is hiring, through The Crowbridge Circle is hiring" | Helian: "the Circle is hiring" |
| 14 | no | R3 MUST "a lead arrives (An offer…): it points toward The Crowbridge Circle is hiring, through The Crowbridge Circle is hiring" | "His name sits at the foot of the hire notices" |

In each of turns 3, 4, 5 and 7 the player was reading the **gate log**. At turn.4 R1 reads "acting on: gate log";
at turn.7, "Read the earlier nights in the gate log".

**The code path.** `engine/dm/roles/narrator.py:_reading_lines` (lines 223–273):
- `things` (line 228) holds only scene objects with a stored `text` or a `_POSTED` name: notice, bill, board…; no
  log, book, ledger or register. So `item.gate_log` is not a written thing, and the beat's target (line 235) is
  dropped.
- Word hits on "hire"/"notice" are 0. Then line 238 applies:
  `picked = named or (things[:1] if len(things) == 1 and _READ_VERB.search(asked) else [])`. "read", "what does it
  say" and "what it says" match, so the one notice is picked, and line 261 writes "quote its words exactly". This is
  the fallback that spec 027 H8 left in place.

**The lead injection** (`engine/dm/turn.py:983–991`, `engine/world/pacing.py:234–300`). The three empty reads
(turn.3, 4, 7) each counted as inconclusive, which raised `trg.lead_injection` (event 419). At turn.8 the Director
answered `"lead":{"thread":"thr.lead_2"}`: the closed cart, which the player was chasing. `inject_lead` ignores that
and runs its own `source_ladder`. "Other active thread by weight" picked `thr.lead_3`, the hiring the PC already knew.
The note template doubles it ("toward X, through X").

**Cause.** Scaffolding. A low-precision reading detector writes code-authored text the model must quote. A blind
code ladder overrides a typed Director choice and re-pushes a delivered hook. The model obeyed MUST and "exactly"
lines, and ignored the reading line twice.

**Structural fix.**
- **Reading follows the beat's typed target.** If the Reader's beat acts on a thing, that thing is what is read. When
  it has no stored words, the existing else-branch fires ("write the ordinary words… never words that point toward
  anything hidden"). Delete the `_POSTED`, `_READ_VERB` and `_SAYS` matching, the name-word hits and the
  "one in view" fallback. *Retires* about 20 lines of regex and the guess.
- **The lead injection uses the Director's `lead.thread`.** Fall back to the ladder only when it gives none, and
  never pick a thread the PC already knows. Write the note as data (the thread, the form), not "toward X, through
  X". *Retires* the code thread pick on a turn where the Director has already chosen.

---

## 5. The stall: "waiting on your reading" (talker turn.4, then turn.5 and turn.8)

**What the player saw.** At [19], turn.4: "The line in the log is short. What it says about the cart is still waiting
on your reading. What does the entry tell you?" Notes [20] and [21]. At turn.8 Helian says "Read their names there"
(note [24]: "names I haven't been shown").

**The packet** (turn.4, narrator row 15) contains:
- `R1 MUST: beat: Fenwin looks at the last entry … to learn who signed it and what it says about the cart; approach:
  lic.lang.letters; no roll: trivial; acting on: gate log`;
- the parts `"Who signed it," (answered)` and `"what does it say about the cart?" (answered)`;
- the wrong reading line (the notice).

The view's `item.gate_log` holds only `binding` and `location`. `thr.lead_2` "A closed cart on the road at night" has
**no hook terms**: `facts_idx` holds `topic.hook.terms` only for `thr.lead_3`. There is no case and no clue
placement, and the clue judge's open clues list only the omen. The guidance in the packet (12.14.13) makes a clue
toward an open thread T2, "generators only".

**The code path.** `turn.py:314–317` stamps every FICTION_QUESTION `"answered"` whether or not anything answered it.
`hooks.terms_for` writes terms only for incident cases (offer, missing, refugees), so an opening lead like "a closed
cart" is a sentence with nothing behind it.

**Cause.** Scaffolding: an impossible record. The model was told to deliver an answer it was forbidden to invent, and
had none. Its stall is the least-bad reading.

**Structural fix.**
- **Every lead gets terms when it is made**, as T2 already does for hooks: whose cart, which way, who saw it. Write
  them as knowledge on the people *and documents* that would hold them, such as the gate log's entry.
- With the reading fix above, a read of the log returns those words.
- Stop stamping a FICTION_QUESTION "answered" when no line answers it.

*Retires:* the leads that are bare sentences, and a false "(answered)".

---

## 3. A voice carrying from too far away (talker turn.9–11)

**What the player saw.** At turn.9 Helian's verdict on the omen is called across the crowd. At turn.10 she answers
"Wait, friend!", which was shouted at the departing woman. At turn.11 she lifts her voice over the chain with "The
gate logs everyone who comes through after dusk…" while the PC is up the road. Notes [27], [29] and [30]. Turns 12–15
have no Helian line: the later notes are the 9,000-character window.

**The packets:**
- turn.9: `R3 MUST: Helian Lanent acts: tells you what the omen shows: a sign of the cursed ground`. This is the
  D2-A clue delivery. The clue judge (row 26) saw "I'll step out and ask her what she makes of the seam", with
  Helian's clue starred as "this person". **It is not told who "this person" is**, nor that "her" is someone else.
- turn.10: `R1 MUST: Helian Lanent acts: answers what you asked` and `R2 MUST: … does not know the way on, but
  someone at The Still Ruins would`.
- turn.11: `R3 MUST: Helian Lanent acts: replies, willingly … in her own words`. Nothing was asked of her. Her card
  lists "knows: the gate logs everyone who comes in after dusk" first. Her "already said" list (`packet.py:840`,
  `said_shown: 6`) no longer shows her turn.2 gate-log line, so the narrator recited the card's first fact.

**The code path.** `engine/dm/npc_layer.py:addressed` (245–271). I rebuilt the state before each turn read-only and
ran its pieces:

| turn | `named_in` | `described_in` | `_TURNS_TO` | spoken_with | result |
|---|---|---|---|---|---|
| talker 9 / 10 / 11 | [] | None ("woman" ties Helian and Belo) | no | [Helian] | **fallback line 268–269 → Helian** |
| explorer 5 | [] (the sellsword's handle is "the contracts", from `_names` line 175) | None (tie) | **yes** ("step toward the") | [Betric] | nobody addressed; the sellsword never enters spoken_with |
| explorer 6 "I ask him…" | [] | None | no | [Betric] | **fallback → Betric** |
| explorer 12 "I tell her…" | [] | **the guards** (1 shared word: "walk" ~ "walking a patrol") | no | — | **the guard answers**; the narrator also moved Gribnik's mud onto the PC |
| explorer 16 "I thank her and ask…" | [] | **Isine** (1 shared word: "stanwall") | no | — | **Isine answers** a question put to Gribnik |

Pronouns ("him", "her") and vocatives ("friend") are never resolved against the conversation. "Present" is the whole
scene's cast, with no nearness: the gate scene covers the gatehouse, the chain and the road. The code says so itself:
`# ponytail: nearness and who would answer are not modelled`.

**Cause.** Scaffolding. Wrong context reaches a low-precision guess, which becomes MUST lines. The narrator followed
them faithfully. `measure.py` reports 0 attribution candidates because it checks the prose against the side list,
which is right; the error is upstream. This is a measurement trap.

**Structural fix (NPC lane).** The Reader names the addressee: one id from the present cast, or `none`, on each
SPEECH or FICTION_QUESTION part. It already sees the conversation and writes "Call out to the silver-haired woman".
Then delete `named_in`, `described_in`, `_TURNS_TO`, `_ADDRESS`, `_VOCATIVE` and the last-spoken fallback, and give
the clue judge the addressee. *Retires* about 90 lines of regex and word overlap, and with them 6 of the 6
misattributions.

---

## 4. Incoherent death narration (fighter turn.12; narration side)

**What the player saw.** "Your mace … takes the freckled youth square in the ribs … he throws himself sideways, down
into the settle's shadow, the way a hunted hare goes to ground … He is dead." `[RESULT] … Changed: Aurard de Morac
dead`. Notes [28] and [29].

**The packet** (row 30): `R1 MUST: … result: critical success`, `R2 MUST: harm to the freckled youth…: dead`, `R3 MUST:
position: you at arm's reach of Aurard de Morac`, **`R4 MUST: the freckled youth who issued the challenge acts: flees
or takes cover`**. The view already holds `fact.127 harm_state.dead` and, beside it, `fact.131 activity = taking
cover`, `fact.132 manner = frightened` for the same corpse.

**The code path:**
- `npc_layer.respond`: `person()` at line 567 checks the kind only. `cast_present` keeps anything that `exists`,
  including a corpse. The fight practice gives the defeated row 2, "flees or takes cover" (`oracles.yaml:2496`), and
  `scene_state.write` stores it as his activity.
- R3 comes from `pipeline.py:530`, `f"{_BAND_WORDS[band]} {ent.name}"`, which is the raw name, not `display_name`.
  The same raw-name path exists in `oof.changed_line` (`_ent_name` before the `name_known` test).

The view also carries two entities for one person: `npc.lilwise_underhill` "the challenger, who is more than they
seem" and `npc.aurard_de_morac` "the freckled youth". That is for the mechanics investigator.

**Cause.** Scaffolding: two contradictory MUST lines. The model wrote both in order.

**Structural fix.**
- One guard: a person whose harm state is dead or out of the fight does not respond (skip in `respond`), and gets no
  scene-state write.
- Position words carry the id, and the narrator layer names it, or use `display_name`.

*Retires:* the corpse's flee row and the code text with a sealed name.

---

## 2. The same closing beat (explorer, Gribnik)

**What the player saw.** In 4 of 4 Gribnik deliveries the closing is her hand, the page or the pen:
- turn.10: "taps the margin … and waits";
- turn.11: "Her finger stops on the margin";
- turn.14: "Her fingers hover over the pen";
- turn.15: "her hand drifting toward the pen … the pen still in her fingers, and she waits".

The pen-in-tray image appears in 4 of 4 and "grey light from the high window" in 3.

**The packets** (rows 32, 35, 45, 48). There is no pen, margin, hand or window in any view or record. Gribnik's
background line is "manner: kindly; voice: terse, now and then swears…". Her look was shown only on her first turn,
as spec 027 intends. The only source is the narrator's own earlier passages in RECENT EXCHANGES. Every record ends
with `- end by handing the moment back (12.14.9)`, and the role prompt allows "a situation-specific question … or an
unresolved image that plainly awaits a response".

**Cause.** Model behaviour. When the NPC has just answered, the model fills the mandatory closing slot with the
listener's waiting gesture, copied from its last closing. The packets pushed nothing.

**Fix, within the owner's stance (no tracking, no prevention).**
- Accept it, or delete the per-record "end by handing the moment back" line, and drop "or an unresolved image" from
  12.14.9.
- A passage may end on the NPC's last words or a question. An NPC's answer already hands the moment back.

*Retires:* one mandatory line in every packet. Then measure the closings again; do not track them.

---

## 6. A thin "what do I know" (explorer turn.4)

**What the player saw.** One line: "The Long Downs: a fallen realm: a kingdom broke two generations ago…". Notes
[20] and [21].

**The code path.** No model call. `engine/dm/codex.py:what_you_know` (350–383). `_about` (293–303) returns
`(['loc.long_downs'], named=True)` on the alias match and stops. The thread `thr.sit_long_downs_wound` ("…a realm
that fell in a single bad winter…", visible in the codex) is never searched. Betric's turn.3 answer ("The banners are
the old colours of the Long Downs, from before the winter…") is a `said` record, and the journal reads none.

**Cause.** Scaffolding: a code-authored answer from a subset of what the PC knows (wrong context).

**Fix.**
- Include every codex thread, and every `said` record, whose text matches the asked words. Label the `said` records
  as hearsay ("Betric told you: …").
- Drop the first-name short-circuit.

*Retires:* the named-only path. No model call is needed.

---

## 7. Jargon in RESULT and OFFER lines

- `engine/resolve/pipeline.py:413`: `[RESULT] no roll (take the time: …) · success · evidence as a no-roll success`.
  This is in all 4 take-the-time RESULT lines: talker turn.9, 11 and 14, and explorer turn.2. Notes [18] (explorer)
  and [26] (talker).
- `engine/dm/oof.py:451`: `Fate: 1 (no reroll: you won't see this die)` on the secret frame at talker turn.6, with
  "Chance: you can't judge how hard this is" for turning a page (note [22]).

**Fix.**
- Delete "· success · evidence as a no-roll success". Keep "[RESULT] no roll: a good while passes".
- Omit the Fate line when it cannot be spent.

*Retires* text only.

---

## "Revisit if" conditions (DL-12)

| DL | Condition | Status on round 8 |
|---|---|---|
| **DL-12-99** setting once | scenery-repetition complaints persist | **Not fired by a complaint. Latent:** the fighter room was re-described 4 of 9 times because same-place scene cuts count as arrivals (`narrator.py:476`). The recorded remedy (quoting back phrases) is ruled out by the owner. **Instead:** key "full" setting to a change of place, not a new scene id. |
| **DL-12-113** texture is background | a look or habit in more than 1 of 3 of a person's speaking turns, or players report it | **Technically met, but not texture.** Belo 5 of 5: her look is her only handle under a crowd label. Ghazka 4 of 9 deliveries, via the scene re-openings. Habit hits are all stem false positives. No player reported a look or habit. |
| **DL-12-114** no code sentences | a code-written sentence or label verbatim in narration | **Fired (minor):** "the sellsword between contracts" (explorer turn.2) and "about her morning work" (explorer turn.9). Also code text with a sealed name in R3 (`pipeline.py:530`), and the forced "quote exactly" notice. |
| **DL-12-122** setting once for people and things | a look or description recurs in more than 1 of 3 of its turns, or players report a person or thing met with no look | **Fired in substance.** The notice text was reported. Its cause is the reading path, which is exempt by design and has the wrong target, not the description gate. Ghazka's look recurred through scene re-openings. |
| DL-12-123 `/fix` note | a re-frame given a note repeats the disputed odds | **Near (other lane).** Talker: "Framing it again left the same label". Fighter [20]: "A fresh framing came back with the same wrong reading". The *reading* repeated, not the odds. |
| DL-12-124 an auto RESULT above the passage | read as a spoiler | Not fired (fighter turn.2, no complaint). |
| DL-12-125 the gate's name | gate and feature confused | Not fired. The talker's place desc is "the gate, by the crossroads cross", which is odd but caused no confusion. |
| DL-12-103 code answer lines | an NPC withholds an ordinary needed answer more than once per run | Borderline: Helian's "Read their names there" (turn.8), with the empty log as the cause. |
| DL-12-101 holistic narration | a blocking error class reaches players more than once per run | Not fired. The opposite problem: 5 blocks, all false or doubtful. |

---

## Anti-pattern check (handoff §3.3)

| Anti-pattern | Seen as |
|---|---|
| **Code authoring narrative truth** | "quote its words exactly" for the wrong document; "(answered)" with no answer; "acts: flees" for a corpse; "it points toward X, through X"; a raw true name in R3; "evidence as a no-roll success" |
| **Over-triggering rules** | The lead injection fired from three "inconclusive" empty reads, and re-pushed a known hook |
| **Low-precision checks that block** | `pronoun_certain_subject` 0 of 3 (it has no `precision`, so it blocks); `not_a_repeat` 0–1 of 2, and missed the real repeat |
| **Blind model calls** | The clue judge is not told who was asked; the Director's lead pick is computed and then ignored |
| **Wrong context** | Addressee by regex and word overlap; the journal ignores threads and testimony; the "already said" window drops a speaker's own earlier line |
| **Mandatory texture** | Not pushed this round, which is a spec 024/027 win. What remains is the mandatory closing slot (symptom 2) and full setting on same-place scene cuts |
| **Test and measurement traps** | The 9,000-character persona window inflates "every reply" notes; `measure.py`'s attribution scan cannot see upstream misattribution; the habit stems produce false positives ("long tale") |

## Structural fixes, ranked (none were proposed)

| Fix | Removes | Retires |
|---|---|---|
| **The Reader names the addressee** (an id or none, per part); the clue judge gets it | Symptom 3; 6 of 6 misattributions | `named_in`, `described_in`, `_TURNS_TO`, `_ADDRESS`, `_VOCATIVE`, the last-spoken fallback |
| **Reading follows the beat's target** (else-branch for unwritten things) | Symptom 1's main path; half of symptom 5 | `_POSTED`, `_READ_VERB`, `_SAYS`, the one-in-view fallback |
| **Every lead gets terms when made**, held by the people and documents that would know | The rest of symptom 5; the empty-read inconclusive streak | Leads that are bare sentences; the false "(answered)" |
| **The lead injection takes the Director's `lead.thread`**, never a known thread | The re-pushed hiring (turn.8, turn.14) | The code ladder's pick when the Director has chosen; the "toward X, through X" template |
| **A dead or out NPC does not respond**; position words through `display_name` | Symptom 4 (narration side) | The corpse's flee row; the raw name in the record |
| **Blocking checks demoted** (set `precision` on `pronoun_certain_subject`; `not_a_repeat` logs only) | 5 of 5 needless revisions; first-draft rate back to about 100% | Two blocking checks |
| **Setting once keyed to a change of place** | The room and looks re-described on same-place scene cuts | — (one condition) |
| **The journal searches threads and testimony** | Symptom 6 | The named-only short-circuit |
| **RESULT and Fate wording** | Symptom 7 | The "evidence" and "no reroll" strings |
| Optional: drop the per-record "end by handing the moment back" line and "unresolved image" | Symptom 2's slot (do not track it) | One mandatory line per packet |
| Harness: give the persona the latest reply clearly separated, or mark older text as seen | Inflated repeat notes | — |
