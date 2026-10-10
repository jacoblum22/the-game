# R8-I2: NPCs, dialogue, testimony and clues, traced to cause

This is a read-only investigation, dated 2026-10-10. The code under test is `milestone-1-playable` at b6430a5.

**Saves:**
- `playtest-20261010-013206-talker`
- `-013226-fighter`
- `-013246-explorer`

**Method.** Every claim below was checked against `turns.record`, `model_calls.request/response`, `events` and `rng_draws`. Each save was opened with `mode=ro`.
- Addressee resolution and "what do I know" were **re-run** against the projected state just before each turn: `npc_layer.named_in/described_in/spoken_with` and `codex.what_you_know`, imported from the worktree and fed `project(events < turn)`.
- The scratch scripts live outside the repo.

**Mapping.**
- Transcript input `[N]` is `turn.(N-15)`.
- A player note at `[N]` describes the screen that `[N-1]` produced.
- Turns undone by `/fix` (explorer turn.6 and turn.12; talker turn.15; fighter turn.3/4 and turn.13) keep their model calls in the save.

---

## Summary: where the cause differs from the surface reading

| # | Symptom | It looked like | Traced cause |
|---|---|---|---|
| 1 | The wrong person answers (explorer, twice) | The narrator picked the wrong speaker | **Code picked the speaker. The narrator obeyed.** Every narrator packet carried `R1 MUST: <wrong person> acts: answers what you asked`, together with that person's SPEAKER CARD. In all of these cases the **Reader's restatement named the right person** ("Ask the sellsword…", "Speech to Gribnik: …"). The Reader schema has no addressee field, so `npc_layer.addressed()` re-guesses the addressee with word heuristics. **6 of 17 speech-only answer turns went to the wrong person, and 1 more went to nobody.** The 6 are explorer turn.6, 12 and 16, and talker turn.9, 10 and 11. The player flagged two. A third (Isine at explorer [31]) went unnoticed. The talker's "Helian's voice carries from far away" is the same bug. |
| 2a | The ledger entry is never given (talker) | An evasive or stalling narrator | **Nothing existed to give, and code pointed the narrator at the wrong document.** (1) The "closed cart" lead (`thr.lead_2`) is a *situation lead*, and `hooks.terms_for` skips it (hooks.py:105). It has no terms, no knower and no content. (2) The gate log is a write-on-mention item with no text. (3) A licensed (G2) no-roll Observe stores the **licence** in `approach_words` (pipeline.py:406). `deliver_learning` looks for the verb in that string (world_step.py:166), so the read delivered nothing, not even "nothing more". (4) `_reading_lines` then picked the only "written" thing in scope, the **hire notice**, and told the narrator to quote it exactly. It did so 5 of 5 times the gate log was read; the narrator quoted it twice. |
| 2b | Helian says "read names I haven't been shown" | A willingness wall | **No wall.** She was willing (warm). No content exists for a watch roster. Her card's "knows: the gate logs everyone who comes in after dusk" invited a deflection to the book, under 12.14.2 "no unestablished details". |
| 2c | Gribnik repeats herself and dodges "where else could I go" | Model blandness | (1) The player's "what the quiet ones saw" came from **two turns that `/fix` undid**: Betric turn.6 and the guard at turn.12. The world never held it. (2) The speaker card cuts each "already said" line at 160 characters (`packet._short`). Her Vordun line was hidden, so she said it again. (3) "Where else": the packet held **no geography** apart from "The Long Downs". There were no neighbouring regions, sites or rumours, and her card has no roads topic. |
| 2d | The woman brushes the player off, then answers | A willingness wall that moved on payment | **Not willingness.** At turn.11 code had Helian as the addressee again. The woman, as the target of a move beat, was "engaged but not addressed". So she got a `tbl.npc_action` row in the *work* practice ("keeps working and pointedly ignores the PC", d10=1) as a MUST line. At turn.12 a paid Talk resolved, and she answered. **The three silvers were never paid**: coin stayed at 44, with no price record. |
| 3 | "What do I know" is thin | Model thinness | **No model is involved.** The answer is pure code (`codex.what_you_know`). Its `_about` helper resolves "the Long Downs" by name, which switches off word matching. NPC speech is never in the journal, so Betric's explanation of the banners and the winter is missing. The situation thread that holds "fell in a single bad winter" is matched only by its name, which is cut at 60 characters ("…fell in a s"). |
| 4 | The woman left abruptly when Helian spoke | A nice NPC beat | **An accident of two code errors.** At turn.9 the PC walked up to the woman to ask about the seam. Code made Helian the addressee, and she delivered the omen clue as a MUST line. The woman was "engaged, not addressed", so `tbl.npc_action` rolled for her in the *work* practice: d10=4 plus standing, giving row 6, "goes after something they want" (MUST). The narrator invented the causal link "At the captain's words…". The player liked it, but it cost the conversation (and see 2d). |
| 5 | Fighter: the "swung first" claim is spoken whatever the roll | Testimony settled regardless of the roll | **Working as designed.** It is the Framer's `method_consequences`, rendered as "Whatever the roll" by `oof.py:449` (rule 01.11.2: words said cannot be unsaid). The Reader's `assertion` went to the Framer as "context only, never a fact". No fact was settled and no testimony call was made. Out of lane: the OFFER head says "Persuade" for a threat. |

**Two causes no one suspected surfaced in the same lane:**
- **(X1) One person cast as two or three people.** `social.cast_described` mints a new walk-on for each description it cannot match:
  - Fighter: "the freckled youth" exists as `lilwise_underhill` ("the challenger, who is more than they seem"), `erusse_…` and `aurard_de_morac`. Two of them stood in SCENE SETTING together for turn.8–12.
  - Group descriptions became one person, because `_GROUP` is anchored at the end of the string: "the people of Redcrag gathering to look at the sky" became one woman, "the quarrelling patrons of the Red Plough" one youth, "the guards at the door" one guard, and "Nibly's men" one man.
- **(X2) The incident's sealed challenger is not the person on stage.**
  - Explorer: the case solution is **Falbo, the sellsword**, while the walk-on youth issued the challenge.
  - Fighter: it is **Alred Millfield**, who sits at the hall, while three walk-ons played the challenger.
  - Delivering the explorer's withheld clue (1c) would have *contradicted* the scene.

---

## 1. The wrong person answers

### 1a. Explorer turn.6 ([21]): Betric answers a question put to the sellsword

**What the player saw.** "Betric's eyes leave the hearth and find you across the room… answers in a voice pitched to carry no further than your table." The sellsword said nothing.

**Model calls.**
| Call | Packet (THIS MESSAGE) | Response |
|---|---|---|
| reader | "I ask him what the old keeps were before the realm fell." | parts `[SPEECH what_like "…"]`, restatement **"Ask the sellsword what the old keeps were before the realm fell."** No addressee field exists. |
| clue | QUESTION + `1*: who the challenger is` (`*` = **Betric** holds it) | `about: none` |
| narrator | `R1 MUST: Betric Brightcote acts: answers what you asked, willingly…`, plus **SPEAKER CARD for Betric Brightcote**, plus "Nobody else present speaks or interjects" | Betric answers. The phrase "pitched to carry no further than your table" is the model squaring an impossible instruction with the scene. |

**Turn record.** `said[0].question = "npc.betric_brightcote|what_like|lore"`, and `draft_versions` has 1 draft with `covers: [R1]`.

**Code path.** `world_step._speech_answers` (world_step.py:209) calls `npc_layer.addressed()` (npc_layer.py:245). Re-run on the pre-turn state:
- `named_in = []`: "him" is not a name. The sellsword's `_names` are "Falbo Bramblewick", "the sellsword between contracts", "Falbo" and "**the contracts**" (the role's last word, npc_layer.py:168-180). "The sellsword" alone is not among them.
- `described_in = None`.
- `_TURNS_TO` is false.
- The fallback (npc_layer.py:269) picks the last person in `spoken_with = ['npc.betric_brightcote']`.

**Why spoken_with lacked the sellsword.** At turn.5 ("I step toward the sellsword and quietly ask him…") `addressed()` returned **nobody**:
- `named_in` was empty (as above).
- `described_in` tied: the youth and the sellsword each share 2 content words.
- `_TURNS_TO` matched "step toward the", which suppresses the fallback.

So turn.5 had no R-line and no card. The narrator chose the sellsword on its own and was right, but he was never written to `SPOKEN`.

### 1b. Explorer turn.12 ([27]): the door guard answers at Gribnik's desk, and the mud is pinned on the PC

- **Reader:** restatement **"Speech to Gribnik: you tell her you mean to walk the track…"**.
- **Narrator packet:**
  - `R1 MUST: the guards at the door acts: answers what you asked, willingly (… a warm listener)`.
  - SPEAKER CARD for "the guards at the door" with "knows: the guards at the door posted at the hall door". That is a degenerate fact line.
- **Code:** `described_in` returned `npc.tobett_bramblewick`. The player wrote "walk it" / "walk the track". The guard's `_looks` include her rolled activity "**walking** a patrol" (activity d6=5 at turn.10). Gribnik shares no word. `described_in` runs **before** `spoken_with` (which held Gribnik), so one incidental shared word outranked the conversation partner.
- **The mud.** Gribnik's mud appears only in RECENT EXCHANGES ("Mud has dried grey on her skirts"). Her SCENE SETTING line at turn.12 has no look (spec 027 shows a look only on first appearance). The model, made to voice the guard, gave the guard a reason to know about the walk and attached the mud to "you". This is a model slip under a code-forced wrong speaker.

### 1c. Explorer turn.16 ([31]): Isine answers. Unflagged.

- **Reader:** "Speech to Gribnik: thanks, then a question about the road to Stanwall".
- **Packet:** `R1 MUST: Isine Whitesmith acts: answers…`, plus Isine's card.
- **Code:** `described_in = npc.isine_whitesmith`. "Stanwall" in the question matched her role, "head of The council of **Stanwall**".
- The player did not notice. The note at [31] concerns turn.15.

### 1d. Talker turn.9, 10 and 11 ([24]–[26]): Helian answers questions put to the woman

| Turn | Player | Reader restatement | Code's addressee and lines |
|---|---|---|---|
| 9 | "Before I go, Captain, let me have a word with that bored woman… I'll step out and ask her what she makes of the seam." | "…to the bored silver-streaked woman, then ask her what she makes of the seam" | Helian. `R3 MUST: Helian Lanent acts: tells you what the omen shows: a sign of the cursed ground`. The woman gets `R4 MUST: … acts: goes after something they want`. |
| 10 | "Wait, friend! What was it you've been wanting? Tell me where you're headed…" | "Call out to the silver-haired woman on the road…" | Helian: R1 "answers what you asked", and R2 "**does not know the way on, but someone at The Still Ruins would**". |
| 11 | "I'll follow her… 'Friend, a moment!'" | "Follow the silver-streaked woman…" | Helian: R3 "replies, willingly". The woman: `R4 MUST: keeps working and pointedly ignores the PC`. |

**Why the code picked Helian each time.** The woman's entity is `npc.belo_applebottle`. Her label is "**the people of Redcrag gathering to look at the sky**" (see X1), so her `_names` are "Belo", "the people" and so on, and the player's "woman" or "friend" never names her. The word "woman" is in both women's `_looks` (from their pronouns), so `described_in` ties and returns None. The fallback is `spoken_with = [helian]`. "Captain," at turn.9 is not matched either: `_names` holds "the captain", and the vocative check only fires after an opening quote.

The player's notes record the effect without naming the cause:
- [27]: "Helian's shouted interjections from the gate feel a bit odd at that distance".
- [29] and [30]: "Helian's voice keeps carrying over from far away".

### Frequency (symptom 1)
| Save | Turns where an NPC answered speech | Speech-only (no Talk beat) | Wrong addressee | No addressee |
|---|---|---|---|---|
| Explorer | 9 | 10 | 3 (turn.6, 12, 16) | 1 (turn.5) |
| Talker | 10 | 7 | 3 (turn.9, 10, 11) | 0 |
| Fighter | 2 (Talk beats only) | 0 | 0 | 0 |
| **All** | **21** | **17** | **6 of 17 (35%)** | **1** |

- In all six wrong cases the Reader named the right person in its `restatement`.
- Every Talk beat that carried a typed `target` resolved correctly (talker turn.12–14; fighter turn.2, 9 and 15): **0 of 6 wrong**.
- The heuristic path is the cause. The model is not.

### Cause and structural fix

**Cause A.** The addressee is re-derived by code heuristics that **discard the Reader's understanding**. Those heuristics are word overlap with the label, role and activity (`described_in`), a role-head-noun alias guess (`_names`), a "turns elsewhere" regex, and last-spoken or first-present. In 3 of the 6 cases the deciding signal was one incidental shared word ("walk", "Stanwall", "woman" on both women). Distance is not modelled (see the `ponytail:` note at npc_layer.py:266).

**Fix.** Add a typed `addressee` to each SPEECH and question part in the Reader schema: an id from the present people the Reader already sees in NARRATOR VIEW, or `none` / `room`. Code only checks that the id is present. A move beat to a person followed by a question addresses that person.

**This retires:**
- `described_in`, `_looks`, `_TURNS_TO` and `_ADDRESS`;
- the `spoken_with` / `present[0]` fallback (P-056) and the role-head-noun alias;
- the "engaged but not addressed" state that causes 2d and symptom 4.

Keep `named_in` only for the offline stub.

---

## 2. Dodged answers and stalls: classification

| Instance | Willingness | Class | Evidence |
|---|---|---|---|
| Talker turn.4 ([19]): entry text never given | none (no NPC) | **Missing content + code misrouting** | The R1 beat has `approach: lic.lang.letters` and no learned line. The packet orders "the character reads the **hire notice**: quote its words exactly". The narrator quoted the notice and wrote "What it says about the cart is still waiting on your reading." |
| Talker turn.5 ([20]): "Read it out to me" | willing (warm) | **Missing content** | Helian: "The line speaks of the cart coming through after dusk… that is all I will swear to." The card holds nothing about the entry. The hire-notice line was injected again. |
| Talker turn.8 ([23]): "read their names there" | willing (warm) | **Missing content (+ an instruction that discourages invention)** | No roster exists. The card's "knows: the gate logs everyone who comes in after dusk" plus 12.14.2 in GUIDANCE led to a deflection to the book. Turn.7's hidden Observe on the earlier pages had failed (d20, "nothing about any cart"). |
| Explorer turn.14 ([29]): Gribnik repeats and gives nothing new on the "quiet ones" | willing (neutral) | **Missing content (from `/fix` reverts) + truncated said-lines** | The detail exists only in undone turns 6 and 12. `deliver_count(2, standard) = 1` dropped the second question, "what the ones who came back quiet actually saw". Here that had no effect, since no clue was at stake. |
| Explorer turn.15 ([30]): "where else a traveller might go" dodged | willing | **Wrong context (content exists, not shown)** | NARRATOR VIEW "not here" lists only `loc.long_downs`. Gribnik's trade topics are lore, faith and law. The world holds 3 neighbouring regions and 8 named dangerous places, none in the packet. She also repeats the Vordun pointer, which was hidden by the card cut "…then the fl…", and the card line "the harvest stores are lower" (on 15 of 29 speaker cards across the round). |
| Explorer turn.3 ([18]): Betric, "I can't tell you what he is… that's all I'll give you" | willing (neutral) | **Clue rule misapplied: a core clue withheld by a count cap** | Betric is the **core holder** of `who the challenger is`. Of the two question parts, `_speech_answers` passes `speech[:deliver_count(2, 2)]`, which is only "the banners" (world_step.py:220). The clue call never saw "and who the young man really is". |
| Talker turn.11 ([26]): "Not now. Go and stare at the sky" | — (not asked; table row) | **Code-written line from a wrong addressee** | `tbl.npc_action` rolled d10=1, clamped into work row 3 "keeps working and pointedly ignores the PC". |
| Explorer turn.8 ([23]): sellsword "Not today, and not from me" + Gribnik | **unwilling (Wary)** | **Willingness wall, as ruled (DL-12-118/119)** | Reaction 1+6, willingness d10=2. Pointer: "Gribnik of the Roof Clan, found at the hall". The player followed it and called it good ([24]–[25]). |

**Code paths:**
- `world_step.deliver_learning` (world_step.py:166) matches `v in e.approach_words`. `pipeline._no_roll` (pipeline.py:406) puts `dec.license` there for G2. So **every licensed no-roll Observe, Talk or Recall delivers nothing**: talker turn.3 and 4, explorer turn.2.
- `narrator._reading_lines` (narrator.py:223-273) builds `things` only from items with stored words or a "posted" name. The gate log is the beat's target but is excluded. `picked = things[:1]` when one thing is in view and a read verb or "what does it say" appears (narrator.py:238).
- `hooks.terms_for` (hooks.py:101-106): "only the hire lead is a job; the situation lead's place is its thread's `points_to`". The leads `thr.lead_2` "A closed cart on the road at night." (talker), "Two banners in the hall." (explorer) and "Hard words at the market." (fighter) have **no `world.hook_terms` entry and no knower** in any save.
- `packet.speaker_card` (packet.py:877-878) renders said records through `_short` (160 characters).

**Frequency.**
- Willingness walls: **1** in 3 runs.
- Dodges from missing content or context: **5**: talker turn.4, 5 and 8; explorer turn.14 and 15.
- Dodges from a code cap or misroute: **2**: explorer turn.3; talker turn.11.

So the owner's D3 ruling produced one wall, and it worked.

### Causes and structural fixes
- **Cause C (content void):** situation leads and incident bodies get no terms.
  - **Fix:** `terms_for` authors terms for **every** lead and incident kind, in the same shape as the hire lead: whose, what and where, as knower facts on the cards of the people who would know. For the cart that is the owner, the driver, where it went, and the log line's words. For the banners it is what they are. For the duel it is what was said and the grievance.
  - **Retires:** "the situation lead's place is its `points_to`", one-sentence leads, and the narrator's 12.14.2 deflections on hook questions.
- **Cause D (reading and learning keyed on strings):**
  - **Fix:** `deliver_learning` keys on the typed `BeatEntry.verb`, not `approach_words`. `_reading_lines` always includes the **beat's target**, using the existing "write the ordinary words such a thing carries and list them under `mentions` as implied `text`" path. A different document is quoted only when it is named or targeted.
  - **Retires:** the `v in approach_words` check, and the single-thing `_READ_VERB` fallback. That fallback also feeds I1's "hire notice repeated" complaint, a shared cause.
- **Cause B (count cap before the clue call):** T-01-6 `deliver_count` (a degree-of-success rule) is applied to a no-roll SPEECH *before* routing, so a later question never reaches the clue judgment.
  - **Fix:** run the clue judgment once per message, over all question parts, and let `deliver_count` cap only ordinary answers. This needs a DL-15-39 amendment.
  - **Retires:** order-dependent clue routing (first question asked wins) and the per-part clue call.
  - Do this only together with X2. Otherwise Betric would have said "the challenger is Falbo Bramblewick" while a different youth was shouting the challenge.
- **Cause E (wrong context for the speaker):**
  - **Fix:** show said lines whole (they are short), and give the card a "places this person knows" line: the region's neighbours and named sites, plus any rumour the person's pack holds.
  - **Retires:** the 160-character cut on said lines and the geography-free card.

---

## 3. "What do I know" is thin (explorer turn.4, [19]–[21])

**What the player saw.** "[JOURNAL] What you know about the Long Downs and the winter that brought the realm down: The Long Downs: a fallen realm: a kingdom broke two generations ago; its roads, keeps and heirs remain".

**Model calls: none.** The turn has no `model_calls` rows. `reader.py:189` pre-routes "what do I know" to `turn.knowledge_subject` and then to `codex.what_you_know` (codex.py:350).

**Re-run on the pre-turn state:**
| Query | Answer |
|---|---|
| "the Long Downs and the winter that brought the realm down" | 1 line (as shown) |
| "the winter that brought the realm down" | "Nothing on record about…" |
| "the banners" | "Two banners in the hall." (the lead text only) |

**Why:**
1. `_about` (codex.py:293-302) resolves "The Long Downs" by alias, which sets `named=True`. The known-fact filter then keeps only facts *about that entity*, so the "winter" words are ignored, and "X and Y" is never split.
2. The PC's knowledge holds **5 facts, all `seen`**: stair, slate, hearth, activity. What Betric *said* ("The banners are the old colours of the Long Downs, from before the winter that brought the realm down") is a `said` record. Under DL-12-102 it is unsettled testimony, and the journal never shows said records.
3. `thr.sit_long_downs_wound` ("…a realm that fell in a single bad winter…") is in the codex view, but is matched by `name`, which is cut at 60 characters ("…fell in a s").

**Frequency:** 1 of 1 "what do I know" questions in the round.

**Fix.**
- The journal gets a **"what you were told"** section: said records spoken to the PC, attributed ("Betric told you: …"), never stated as fact.
- It searches thread *text* and said words, and splits "X and Y".
- **Retires:** the name-only short-circuit for compound questions, thread-name matching, and a journal blind to dialogue. The owner's "dialogue is testimony" still holds, because the lines are attributed and not settled.

---

## 4. The talker's woman left when Helian spoke (turn.9, [24])

**Was it good or bad?** It was good on screen and bad in cause.

**Calls at turn.9:**
- Reader: a move beat with target `npc.belo_applebottle`, plus "ask her what she makes of the seam".
- Clue: the call ran for **Helian** (`1*`, Helian holds it) and returned `about: 1`.
- Framer: the move beat.
- Narrator packet: R3 Helian delivers the omen clue; `R4 MUST: the people of Redcrag gathering to look at the sky acts: goes after something they want`.

**Dice:**
- Reaction roll for belo: 5+6.
- `npc action npc.belo_applebottle (12.11.5)` d10=4, clamped to the *work* practice rows [2,3,5,6,7,8], giving row 6.

**Code path.** In `npc_layer.respond` (npc_layer.py:534ff) belo is in `engaged`, via the move-beat target, but not in `spoke_to`. So she falls to branch (c), the action table by standing in the "work" practice ("everyone at their own business"). The result is written as a MUST line.

**The causal link is the model's.** "At the captain's words the woman's bored set goes out of her shoulders." Nothing in the record ties her leaving to Helian.

**What it cost the player:**
- Turn.10: Helian answers for the woman, adding a false-positive clue pointer to the Still Ruins.
- Turn.11: another work-row brush-off.
- Turn.12–14: three silvers narrated as paid but never written.

**Verdict.** NPC agency is welcome when it comes from a stored want with a cause. Here it came from a work-practice dice row aimed at the person the PC was walking up to question. That only happened because code thought the PC was talking to someone else.

**Fix.** Cause A's typed addressee makes her addressed. The `tbl.npc_action` rows then apply only to true bystanders, tagged optional. This **retires** "engaged but not addressed".

---

## 5. Fighter: "the 'swung first' claim is spoken whatever the roll" (turn.13/15, [28]–[30])

- **Reader:** `assertion: "He swung first."`, `pressure: threat`, `verb.talk`, `persuade_to`.
- **Framer packet:** "assertion (context only, never a fact): He swung first." The Framer returned `method_consequences: ["Your loud claim that he swung first is spoken aloud in the room and cannot be unsaid.", "The mace held up is seen by everyone in the room."]`.
- **OFFER:** `oof.py:444-449` renders these as "Whatever the roll:" (12.15.2 / 01.11.2).

**Testimony.** No testimony call was made, and no `fact_set` mentions "swung" outside the frame records. Oracle calls: 0.

**Verdict.** This is correct by rule. Out of lane: the OFFER heads a threat "Persuade" (also [19]–[24]).

**X1 is visible in this run.** The youth exists as two entities in SCENE SETTING from turn.8 to turn.12 ("the freckled youth who issued the challenge" and "the challenger, who is more than they seem"). The RESULT line printed "Agreed by the challenger, who is more than they seem". The player's "he was shown as still pinned, then suddenly free" ([25]) and "Aurard de Morac dead, a name I never heard" ([28]) fit two or three records for one youth. `/fix` called the name "a display slip". It is in fact a third entity (`aurard_de_morac`, created at turn.6).

---

## 6. Extra causes in this lane

### X1. `cast_described` mints people from descriptions (social.py:254-292)
- `_GROUP = r"(?:[^s]s|folk|people|men|…)$"` is tested against the **end** of the bare label. "people of Redcrag gathering to look at the sky", "quarrelling patrons of the Red Plough", "guards at the door" and "Nibly's men, somewhere in the market square" all fail it, so each became **one** walk-on carrying a group label as its role.
- `find_existing` fails on a free description of someone already present. Fighter results:
  - "the challenger, who is more than they seem" became `lilwise` (turn.1);
  - "the freckled youth who issued the challenge" became `erusse` (turn.3, given iron rings) and then `aurard` (turn.6);
  - "the old healer with the satchel strap" became `gribka`, while `rosbo` already carried the healer's satchel.

**Effects:** the wrong addressee (1d), the label leaking verbatim into code text, and the pinned/free youth.

**Fix.** The Director returns typed casting: an existing present id, or `new` with `{group: bool, role}`. It already sees the cast list with ids. **This retires** the `_GROUP` regex and description matching.

### X2. The incident's subject is never bound to the person on stage (gen/case.py:55-63)
- `reduced_case` casts the duel's subject from the local NPCs: Falbo the sellsword in the explorer, Alred Millfield at the hall in the fighter.
- The opening record line only says "a quarrel in the inn turns to a challenge, and the challenger is more than they seem". So the narrator, and in the fighter the Director, staged a *different* person as the challenger.
- The explorer's core clue "who the challenger is: Falbo Bramblewick" would contradict the scene if delivered.

**Fix.** For an on-stage incident, the subject entity is cast into the opening scene **by id**, under its unnamed label, in the incident's role. The sealed field is the identity behind the visible person. **This retires** the Director or narrator inventing the incident's actor.

### X3. Payment is skipped when a paid Talk also asks (npc_layer.py:588 / 602)
- `deliver_learning` runs first (world_step.py:51) and writes the PR-12-10 answer line.
- `respond()` then hits `if npc in answered: pass` and never reaches the `talks` branch, where `pay_deal` lives.
- Talker turn.12–14: `player_quantity = 1` each time, no price record, coin 44 to 44, while the narration says "it vanishes into her sleeve". The player believed two silvers were taken ([31] note).
- Explorer turn.9: "leave a coin for his cup" was narrated, not written (coin stays 180).

**Fix.** Pay the price as a consequence of the resolved offer beat in the pipeline, not inside the NPC response choice. A gift is a typed change from the Reader's quantity. **This retires** payment depending on which response branch fires.

**Test trap.** Spec 025's C19 "buy you a cup" and its live run were a request *without* a question, so this path was never exercised.

---

## 7. Round-7 targets, measured

**Clue calls (9 / 1 / 9 = 19):**

| Run | Verdict | Count | Correct? |
|---|---|---|---|
| Talker | none | 7 (turn.2 ×2 "whose cart / which way", turn.3 Nibly, turn.10 "what you've been wanting", turn.12, 13 and 14 Circle/Nibly) | 7 of 7 right: the cart and the Circle are not case content |
| Talker | yes | turn.9 "what she makes of the seam" → omen | right, but delivered by the **wrong speaker** (Helian; the PC asked the woman) |
| Talker | yes | turn.10 "where you're headed in such a hurry" → "the way on" | **false positive.** It produced Helian's pointer "someone at The Still Ruins would" |
| Fighter | none | 1 | right |
| Explorer | none | 9 | 9 of 9 right on what the call *saw* |

- **Missed upstream:** the explorer's turn.3 "who the young man really is", put to the core holder, never reached a call (Cause B). The fighter's challenger was never asked of a holder.
- **Clues delivered:** 1 node in total: talker omen n1, plus 1 pointer for n2. Explorer 0; fighter 0.
- **Live precision of "yes":** 1 of 2. **System recall on holder questions:** 1 of 2.

**Other targets:**
- **Refusal loops:** 0.
- **Willingness walls:** 1 (explorer sellsword, with a pointer, followed by the player). The talker's brush-off is a table row, not a wall.
- **Unpriced or unpaid deals:** 3 of 3 talker deals unpaid with no price record, plus 1 narrated gift unwritten (explorer). Cause X3.
- **Contradicting improvised details:**
  - Topics with 2 or more speakers were consistent: the cart (Helian, the woman); the keeps (Betric, undone; Gribnik); "came back quiet".
  - The identity contradictions were code-made: X1 (two entities for one youth) and X2 (the sealed challenger is not the person on stage).
  - The "mud on your skirts" slip was undone.
  - Isine called "the Stanwall road" a day's walk while the PC stood in Stanwall. That is the player's mistaken question answered by the wrong speaker.
- **Oracle facts about a target:** 0. There were 0 Oracle calls in all three runs.
- **Refusals stored as facts:** 0. The single testimony call (explorer turn.9) took "Gribnik keeps the letters at the hall" from the sellsword's refusal, not the refusal itself.

---

## 8. "Revisit if" conditions

| Entry | Condition | Status |
|---|---|---|
| **DL-15-42** (typed deal price) | "a deal in a playtest is agreed with no price record, or a payment is narrated but not written" | **FIRED.** Talker turn.12–14 (3 silvers, no record, coin unchanged); explorer turn.9 (coin left, not written). Cause X3. |
| **DL-12-109** (hook terms) | "a hook question (pay, place, issuer, who) answered by a dodge…" | **FIRED.** "Whose cart?" (talker turn.2, 5 and 8) was answered by "I have not learned whose cart it was" and "read their names there". The situation lead has no terms at all (hooks.py:105). The fighter's "what exactly did he say" ([18]) is the same: the duel carries a reporter only. |
| **DL-12-103** (code answer lines) | "an NPC withholds an ordinary answer the player needed more than once per run with no line from code" | **FIRED.** Talker turn.4, 5 and 8 (the entry and the roster). |
| **DL-12-119** (refusal pointer; clue rules) | "…a reachable core clue is withheld by a rolled band" | **Not literally** (no band was involved). In substance yes: explorer turn.3's core clue was withheld by `deliver_count`. Recommend widening the condition to "withheld by any code cap". |
| **DL-12-110** (Director casts a description) | "a lead or a player's stated purpose names a group that the Director cannot bring into the scene" | **FIRED.** "Nibly's men" (talker turn.15), "the people of Redcrag…", "the quarrelling patrons…" and "the guards at the door" each became one person. Duplicates as well (X1). |
| **DL-12-114** (no code sentences or labels) | "a code-written sentence or label shows up verbatim in narration" | **FIRED (labels).** "the sellsword between contracts" appears in explorer narration [17] (the player noticed). "the challenger, who is more than they seem" appears in the fighter RESULT line ([30]). |
| **DL-12-112 / DL-15-40** (clue judgment) | precision or recall below 0.9 on the made-up set | Not re-measured. Live signal: "yes" precision 1 of 2 and system recall 1 of 2. Add multi-part questions ("X, and who is Y?") to the made-up set. |
| **DL-12-118** (willingness holds; owner D3) | walls that never move; a band change with no event; walls reported despite pointers | **Not fired.** One wall, with a pointer, followed. The woman's turn from brush-off to answer was a table row and then a paid Talk, both listed events. |
| DL-12-102 (testimony settlement) | the player acts on testimony uncaught more than once per run | Not fired. |
| DL-12-120 (greeting or thanks) | a greeting produces a refusal | Not fired ("I thank her" parts drew no line). |
| DL-15-39 (bundled questions) | "talker personas report Standard Talks as stingy" | Near: [21] "the last two replies dodged my question". The traced cause, though, was missing content plus Cause B, not the half rule itself. |

---

## 9. Shared causes

- **(S1) The Reader's reading is thrown away and re-guessed in code.** This covers the addressee (A), the target versus group or person (X1), and which questions are routed (B). It feeds symptoms 1, 2c (explorer turn.3), 2d and 4, and the talker's interjections.
- **(S2) Content voids at hook and incident creation (C, X2).** These feed symptoms 2a and 2b, the fighter's "vague challenge" ([18]), and the latent contradiction of the challenger's identity.
- **(S3) The narrator obeys code-written MUST lines that are wrong.** "Betric acts: answers", "the guards… answers", "Isine… answers", "reads the hire notice", and the table rows "goes after something / ignores the PC". **Of the 9 wrong outputs traced in symptoms 1, 2 and 4, none began as a model error.** Two model slips sat on top of code-forced wrong speakers: the mud, and the "pitched to carry" line.

---

## 10. Anti-pattern check (handoff §3.3)

- **Code authoring narrative truth:**
  - `R4 MUST` work-practice table rows on the person being approached (symptom 4, turn.11);
  - "quote its words exactly" for a document nobody was reading;
  - a code-chosen speaker as a MUST.
- **Atomisation:**
  - the clue call per *part*, which sees only the part text ("ask her what the dangers are");
  - `deliver_count` slicing parts before routing.
- **Over-triggering rules:**
  - T-01-6 applied to no-roll speech;
  - the hire-notice reading line in 5 of 5 gate-log turns.
- **Low-precision checks (deciding, not blocking):**
  - `described_in` word overlap and the `_names` role head noun;
  - `_TURNS_TO`;
  - the end-anchored `_GROUP` regex;
  - `v in approach_words`;
  - the single-thing `_READ_VERB` fallback.
- **Blind calls:**
  - the Director's `cast_described` returns strings, not ids;
  - the clue call cannot see the other questions in the same message.
- **Wrong context:**
  - said lines cut at 160 characters;
  - no geography for "where else";
  - group labels on single people;
  - a journal blind to dialogue;
  - Gribnik's mud absent from SCENE SETTING when another speaker was forced.
- **Mechanics stored as text:**
  - the verb carried in the `approach_words` string;
  - payment buried in a response branch.
- **Mandatory texture:** "the harvest stores are lower than anyone likes" is on 15 of 29 speaker cards and was voiced twice.
- **Test traps:**
  - spec 025's deal case and live run had no question in the paid Talk;
  - its clue set had no multi-part question.

---

## 11. Fixes and what each retires

| Cause | Structural fix | Retires |
|---|---|---|
| A: addressee by heuristics | The Reader returns a typed `addressee` id per speech or question part. A move-then-ask addresses the move's target. | `described_in`, `_looks`, `_TURNS_TO`, `_ADDRESS`, the `spoken_with` / `present[0]` fallback, the role-head-noun alias, "engaged but not addressed" |
| B: count cap before clue routing | One clue judgment per message over all question parts. `deliver_count` caps ordinary answers only. Amend DL-15-39. | per-part clue calls; first-question-wins routing |
| C: content voids | `terms_for` authors terms for every lead and incident kind (who, what, where, words), on the knowers' cards | one-sentence leads; reporter-only incidents; 12.14.2 deflections on hook questions |
| D: reading and learning on strings | Learning keyed on the typed verb. The reading line covers the beat's target, using the existing write-on-mention text path. | `v in approach_words`; the single-written-thing fallback (also I1's repeated notice) |
| E: speaker-card context | Said lines shown whole; a "places this person knows" line | the 160-character cut; geography-free cards |
| X1: casting from descriptions | The Director returns `{id}` or `{new, group, role}` | the `_GROUP` regex; description matching; duplicate people |
| X2: incident subject not on stage | The subject entity is cast in the opening by id, in the incident's role, with its identity sealed | the narrator or Director inventing the incident's actor |
| X3: unpaid deals | The price is paid as the resolved offer beat's consequence in the pipeline; gifts come from the Reader's quantity | payment inside `respond()`'s branch order |
| Journal | A "what you were told" section (attributed said records); search over thread text; split "X and Y" | the name-only short-circuit; thread-name matching |

**Order.** Fix X2 before or with B. Otherwise the first routed challenger clue contradicts the scene.
