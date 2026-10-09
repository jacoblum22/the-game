# I2: NPC behaviour and testimony, traced to cause

Read-only investigation, 2026-10-09. Branch `milestone-1-playable` (b9c4a1b).

**Data.** Six saves carry `npc.said` testimony: 192926-talker, 192946-fighter, 214013-talker, 214033-fighter,
232941-talker and 233000-fighter. Together they hold 77 turn rows. The four earlier saves (135029, 135049, 145410,
145430) predate testimony. I also scanned all 17 `evals/playtests/20261008-*.md` transcripts for the speech-dodge
rate. Scratch scripts are outside the repo.

## Summary: where the suspected cause was wrong

| # | Suspected (ROUND5) | Traced cause |
|---|---|---|
| 1 | Testimony reaches the Framer unsettled; build the deferred settle trigger | It **was** settled. Settlement itself made the garbage: the Reader names `rests_on` on 64% of turns, the claim call is given ids but no pronouns, `settle()` accepts the speaker's own refusal as a world fact, the predicate slug repeats the value, and the label has no speaker. |
| 2 | P-036 again: the bond doesn't reach standing | Standing **is** +2 and willingness reads it. The bond never reaches the **narrator's speaker card**: `bond.` facts are skipped there. NPC speech is also exempt from the P-036 claim check. |
| 3 | Willingness code / refusals | Willingness was `willing` **19 of 19** times. The wall comes from (a) code answer lines with no content or the wrong content (casting "no one you know", misrouted questions, an agreement with no amount), (b) the narrator prompt's "don't assert names or kinship; write around it", and (c) a quest-giver who rolled Unfriendly. |
| 4 | Missing pronoun check in speech | The absent person's pronouns are **in no packet**: the not-here block, cast list, `also here` and speaker-card lines all omit them. The testimony call gets names only. |
| 5 | I-176 tags | The want and refusal tags engaged **0 times** in 6 runs. Bystander concern fired 4 times; 2 were false positives (the PC "Wila" matched NPC "Wila Hayfoot"). |

---

## 1. Testimony leaking into mechanics

### What the player saw
Fighter 233000, turn.8 OFFER (repeated on turns 9, 12 and 13):

```
Chance: unlikely — 40%   (Presence +3, practised +1, said will give no word out while you evine oakwell has a hand: pc.evine_oakwell has a hand on him −2)
```

### End to end
1. **Speech becomes a `said` record.** Turn.6's narrator wrote: Dunwen: "You'll get no word out of me with your hand on
   me, duck," `narration.py:603` → `testimony.add_said` stored it as `said.5` `{speaker: npc.dunwen_redmore, words}`.
   This step is correct; no fact is written.
2. **The Reader triggers settlement.** In turn.7 (model_calls row 15) the player threatens. The Reader packet's
   `TESTIMONY (unsettled; rests_on names the one the player's action relies on)` lists said.3 to said.5
   (`packet.py:249-256`), and the Reader returns `"rests_on":"said.5"`. The player's threat does not *rely* on
   Dunwen's statement; it works against it. `reader.md` has no rule for `rests_on`. That one header line and the
   schema enum (`schemas.py:230`) are its only guidance.
3. **The testimony call** (row 16, `testimony._claim`, `testimony.py:142-161`). The whole packet:
   ```
   [NARRATOR VIEW]
   npc.dunwen_redmore: Dunwen Redmore
   pc.evine_oakwell: Evine Oakwell
   [THIS MESSAGE]
   npc.dunwen_redmore: Dunwen Redmore said: "You'll get no word out of me with your hand on me, duck,"
   ```
   Response: `{"subject":"npc.dunwen_redmore","predicate":"will give no word out while","value":"pc.evine_oakwell has a hand on him"}`.
   - The prompt says "use its id from the view" for `subject`, and the view is `<id>: <name>`. The model put an id
     in `value` too (model behaviour, invited by the format).
   - The packet holds **no pronouns** (`name_line`, `packet.py:492`), so the model guessed "him" for Dunwen
     (gender woman). It did the same in turn.11 ("all **he** will reveal") and turn.14 ("**his** arm").
4. **Settlement writes a fact** (`testimony.settle`, `testimony.py:184-232`).
   - `_case_route` → None. `_BEYOND` → no match. Route: **accepted, true**.
   - The predicate is built as `("said." + slug(predicate + " " + value))[:60]` (line 199), which gives
     `said.will_give_no_word_out_while_pc_evine_oakwell_has_a_hand`. That is the value again inside the predicate,
     cut at 60 characters.
   - `fact(...)` gets `source="testimony"`, `visibility="shown"`, and no `said_by`/`said_turn`. PR-12-12 step 4
     requires both. Result: fact.103.
5. **The Framer cites it as a snag** (turn.7 row 17, turn.8 row 18). The Framer view lists
   `fact.103 about npc.dunwen_redmore: said.will_give_no_word_out_while_pc_evine_oakwell_has_a_hand = pc.evine_oakwell has a hand on him`.
   The turn.8 response has `"snags":["fact.103","fact.101"]`. Per framer.md, "Every fitting hindering fact is a snag",
   and code applies the first as −2. The Framer cited fact.103 again in turns 12 and 14, and cited fact.106 ("will
   share only part of the word…") in turn 12, where the second snag raises the stakes.
6. **The OFFER renders it** (`oof._breakdown` → `fact_short`, `oof.py:195-220`). The predicate is not `detail.`
   and the value is 48 characters or fewer, so the label is `f"{slug_words(pred)}: {value}"`. `slug_words`
   (`engine/text/render.py:159`) rewrites the token `pc` as "you", which produces "while **you evine oakwell** has a
   hand", followed by the raw value. Nothing names the speaker.

**Root cause.** Testimony *is* stored as words plus speaker and settled at a trigger, as designed. The garble comes
from scaffolding at settlement:
- an over-eager trigger: the Reader picks `rests_on` almost by default;
- a claim call without pronouns and with ids in its view;
- a speaker's statement about **their own willingness** accepted as world truth, then reused by the Framer as a −2
  snag. The NPC's refusal is counted twice: once by the NPC layer and once as a snag;
- a slug that repeats the value;
- a label with no attribution, because `said_by` is never written.

The model's own errors (the id in the value, the guessed pronoun) are both errors the packet invited.

### Frequency (6 saves)
| save | testimony calls | from Reader `rests_on` | malformed (raw id / wrong pronoun / question stored as a claim) | stored with subject `world` | Framer citations |
|---|---|---|---|---|---|
| 192926-talker | 10 | 10 | 0 | 6 of 10 facts | 0 |
| 192946-fighter | 4 | 3 (1 travel target) | 0 | 4 of 4 | 0 |
| 214013-talker | 3 | 3 | 0 | 1 of 1 | 0 |
| 214033-fighter | 2 | 2 | 0 | 1 of 1 | 0 |
| 232941-talker | 7 | 7 | 1 ("asks whether you will walk…", a question stored as a fact) | 5 of 6 | 0 |
| 233000-fighter | 5 | 5 | 3 (1 raw id, 3 wrong pronoun) | 0 of 4 | 4 (all snags) |
| **total** | **30** (~0.4 per turn) | **29 of 30** | **4 of 30 hard-garbled (13%)** | **17 of 26 facts (65%)** | **4** |

- **Trigger rate.** The Reader named `rests_on` in **27 of 42** calls where testimony was offered (64%), so
  "settle when acted on" in practice means "settle nearly every turn".
- **Other defects.**
  - 2 of 30 claims keep an unresolved "you".
  - 9 of 30 predicates are truncated at 60 characters.
  - A free-text subject becomes `world`, so the fact loses who it was about.
- **Speaker self-claims.** All 5 fighter claims are about the speaker herself: "has the word", "did not mark a face",
  "will give no word", "will share only part", "will reveal nothing more". Every Framer citation came from this
  kind of claim.

## 2. The PC's friend treated as a stranger (talker 232941)

### Evidence
- **The bond is stored and does reach standing.**
  - event 292 `fact.81 pc.ysndil… bond.anchor = {kind: friend, npc: npc.lilett_mughill}`;
  - event 297 `relationship_set npc.lilett_mughill→pc standing +2 reason "bond"` (the be20402 path,
    `creation.py write_character`).
  - Willingness reads it. Index entry `npc.lilett_mughill|what_want|arrivals`: `willing`, "a plain question to a
    friendly listener". The R1 lines in turns 7 and 8 say "willingly (a plain question to a friendly listener)".
- **The speaker card has no relationship.** Turn.8 narrator, row 30, `SPEAKER CARD for Lilett Mughill` holds:
  three `knows:` lines (Sevella; the faith of Evys; Syllorn), trade topics, public news, and "they already said".
  The card has no "your friend" and no standing. Cause: `packet.py:503` `_CARD_SKIP_PREFIX = (…, "bond.", …)`.
  The bond fact's subject is the PC anyway, and `speaker_card` only gathers facts the NPC knows or that are about
  the NPC (`packet.py:534-536`).
- **The rest of the packet points the other way.**
  - SCENE SETTING: `present: Lilett Mughill, the officer of … (she/her, middle-aged, a pronounced limp, sly)`.
    Demeanour "sly"; no relationship.
  - The only bond mention is buried among the PC's facts: `fact.81 about pc…: bond.anchor = kind=friend, npc=npc.lilett_mughill`.
  - The opening (turn.1) introduced her as a stranger: "watches you from under her brows".
- **What she said.** Turn.8, to "Is she [Sevella] a friend of yours?": "A friend is a word I keep for few, and I'll
  not stretch it for you." Single draft, no repair: it is the model's first output. The player read it as denying
  the friendship. In turn.13 Sevella then invents "Lilett Mughill wouldn't own to knowing me until she had to".
- **Why the P-036 fix doesn't catch it.** be20402 added the bond check to the *claim checker's relation claims*
  (`claims.py _identity`, `_BOND_WORDS`), which judges the narrator's voice. A denial in **speech** is testimony
  (12.3.1b) and is exempt. P-036 ("Narration says Edda is not your friend") was a narrator-voice line; this one is a
  quoted line.

**Root cause.** The bug did not regress. The fix covered standing and narrator-voice claims, but the speaking
model's frame never says the NPC is the PC's friend. The packet says "sly" and leaves the bond as a raw dict in
the PC's facts. That is a scaffolding cause; the model behaved plausibly for an NPC it was shown as a sly
stranger.

**Frequency.** 1 of 1 anchor-bond NPC who spoke in these runs (Lilett). Every talker run with a bonded NPC on stage
is exposed.

## 3. NPCs dodge and refuse: "talk feels like a wall"

### Willingness code is not it
- All **19** `answers.index` entries across the 6 saves are `willing`; there are 0 `guarded` and 0 `unwilling`.
- No narrator packet contains a refusal line ("refuses…", "turns you away", "bristles", "acts on a want").
- Belby is the one exception: `willing (unfriendly toward you)` — see cause (c).

### What the dodges actually were (232941, 40 `said` lines)
13 lines match a dodge pattern. Reading them by hand, 9 are real dodges and 4 are false positives (advice or
flavour).

| turn | NPC | line | cause |
|---|---|---|---|
| 3 | Belby | "Whose blood runs in the child is no business of this square… that is all I give you" | **Code routing.** "Is Rrakaa kin of yours?" was routed to the case (`answer._route` → `case_about`). The only answer line was `R5 Belby acts: does not know the way on, but someone at The Red Warren would`. Nothing answered the kin question, and the narrator wrote around kinship (narrator.md: "Invention slips in most with … kinship …; if the view does not hold such a thing, do not assert it; write around it"). |
| 3 | Belby | "Name it once you have said you'll walk, not before" | **Code record with no content.** `R4 Agreed by Belby Haydale: learn what Belby would pay or give…`. No amount exists anywhere, and counts are on the narrator's no-invention list. |
| 4 | Belby | "The sum is named when the tracks are found, and I will not name it in this square." | Same missing amount. Also: **standing −2 from a first-interaction reaction roll** (event 411, `tbl.npc_reaction 4+0`), even though Belby is the quest-giver with stance `helps` and demeanour `cheerful`. `answer.willingness` → `first_interaction(…)` passes no modifier from stance (`social.py:308`). The narrator prompt maps Unfriendly to "curt". |
| 6 | Lilett | "What blood runs in Belby's house is Belby's to tell" | The family question was a DECLARATION beat with no answer line; the narrator wrote around kinship. |
| 6 | Lilett | "No one I know keeps the gate at The Red Warren" | **Code.** `R2 Lilett acts: tells you who is keeps the gate at The Red Warren: no one you know`. `answer.cast_who` (`answer.py:372-384`) found no cast match, wrote the world fact `who_is_keeps_the_gate…` = `NO_ONE`, and made it a MUST line. In turn 8 her answer naming Sevella contradicts this, which led to the player's /fix. |
| 7 | Lilett | "Here? Not one I'd name to you across this square" | Narrator wrote around naming a new person. This was also the turn stitched by repair (T3: 4 drafts). |
| 8 | Lilett | "A friend is a word I keep for few…" | Problem 2 (no bond on the card). |
| 13 | Sevella | "…I'll not send men out on the Red Warren road for a rumour" | In character (suspicious). Fine. |
| 16 | Sevella | "I'll not put a name to a man I haven't seen" | Narrator wrote around naming. |

The same code paths appear in 192926:
- Turn 2: "Who are they?" (the strangers) was answered with `gives their name: Ivas Terier`, because
  `answer._SELF = ^(you|he|she|they…)` treats "they" as asking the knower's own name.
- Turn 10: `who is buying the oil…: no one you know` came from `NO_ONE` casting.
- Turn 11: "Then who would know?" was misrouted to `does not know what the omen shows, but Ivas Terier would`.

### Root causes, in order
1. **Code answer lines that are wrong or empty**: 7 instances across the 2 talker runs.
   - `cast_who` → `NO_ONE` (2);
   - case pointers on misrouted questions (2);
   - `_SELF` "they" (1);
   - an agreement with no content (1, which drove 2 dodges);
   - a question given no line at all (1).
   These are MUST lines. They answer a different question or say "no one", and the narrator has to voice them.
2. **The narrator prompt's anti-invention rule applied to speech.** It says not to assert names, kinship, counts or
   "what they know" that the view lacks. The speaker instruction says to answer "beyond [the card], plainly and with
   ordinary confidence". When the two clash, the model takes the safe side and dodges. All dodges were in first
   drafts (turns 3, 4, 6 and 8 each had a single draft), so this is not repair-induced.
3. **The quest-giver rolled Unfriendly.** The reaction roll ignores the NPC's seeded stance toward the incident.

### Frequency
- **Across 17 transcripts:** 49 of 643 quoted-speech segments match the dodge pattern (7.6%). The rate is 0–11% in
  most runs and 20% in 232941 (14 of 69).
- **Code answer lines that give no answer:** 4 of 30 NPC answer lines in the 6 saves. In 232941 alone, 3 of the 9
  real dodges trace to code lines and 4 to write-around.

## 4. NPC pronoun flips in speech

### Evidence
- **232941 turn.7** (narrator, row 25, first draft): Lilett: "Ask Sevella de Belac, I trust **her** more than anyone…".
  - Sevella is seeded `gender: man` (event 214).
  - In the packet, Sevella appears only in the `cast list: … npc.sevella_de_belac Sevella de Belac; …` and on
    Lilett's card as `knows: trusts Sevella de Belac more than anyone in Stanstead`. No pronouns appear.
  - In turn.8 (row 30), Sevella's not-here block is `npc.sevella_de_belac: Sevella de Belac (captain of the gate) /
    name: Sevella de Belac`, again without pronouns. By then the player's message also said "she", and the card's
    `they already said` list replays Lilett's own "her" twice.
- **The code.**
  - `spot_lines` (`packet.py:137-154`) emits name, role and up to 3 facts, never `pronouns` or `gender` (they are
    entity data, not facts).
  - The cast list and `also here` lines are name only.
  - Only *present* people get "(he/him, …)" on the SCENE SETTING line.
- **Later.** At the gate (turn.11) the narration used the record's "his", and the /fix was answered "he/him on
  record" (T4).
- **192926 turn.11.** Sylthas says Ivas Terier "since **he**'s the one…", but Ivas is seeded woman. In turn.13 the
  same speaker says "**she**'s standing there". Ivas was absent; the packet had her name only (R2 line, cast list,
  "matter at hand").
- **Fighter "him" / "his".** These come entirely from the testimony call (problem 1): 3 of 5 claims got Dunwen's
  pronoun wrong, and the Chance line carried "him" on 5 screens. The narrator's own prose in that run has 0
  masculine pronouns for Dunwen.
- **The Reader too.** 232941 turn.3 restatement: "Ask Belby what **she** would gain". The Reader packet did hold
  `pronouns: he/him`, so this one is model behaviour.
- **The checker.** The precision check `pronoun_certain_subject` strips quoted speech (`claims.py:1453`,
  `_QUOTE_RE.sub`), so nothing catches these.

**Root cause.** Scaffolding. The absent person's stored pronouns are visible in no packet, so the model infers them
from the name (Sevella reads as feminine), and its first guess is then fed back to it through `they already said`.

**Frequency.**
- In speech: 5 of 9 checkable lines (a line naming a gendered person with a single pronoun set) are flipped. All 5
  are about absent people.
- In testimony claims: 3 of 30 wrong.

## 5. Reaction tags and interjections (I-176)

- **Bystander reactions.** Packets carrying a `X, not addressed: …` line: **4 in 6 runs**.
  - 192926 turns 9 and 10: the priest **Wila Hayfoot** "moves off" and "goes after something they want". The
    Reader's restatement names the PC: "**Wila** walks to the carters' back table". `named_in` (given-name match)
    then fires `concerns_self` (`npc_layer.py event_tags`, last block). **False positive.**
  - 232941 turn.6: Belby "moves off". He was named in the player's question. Plausible.
  - 214013 turn.3: Tammund "offers a word of help unasked". He was the subject of the question. Plausible.
- **Want and refusal tag matching.** 0 engagements. Almost every NPC has data for it (20–22 per save with wants
  and refusals, e.g. Belby `refusal.past`, Lilett `refusal.master`). Even so, no `unwilling` from
  `willingness()`'s refusal-tag branch, and no `bristles` or `acts on a want` line appeared. Most refusal kinds
  map to the Framer's `asks` enum (`refusal.duty → asks_breach`), which only fires on a framed Talk with a request.
- **Interjections outside the tags.** 232941 turn.3: `R6 MUST: Lilett acts: offers a word of help unasked`.
  - The player only *looked* at her. The observe beat made her a target, so she joined `engaged` and got a
    `tbl.npc_action` roll at +2, which gave row 8, a MUST line.
  - This is the targets path in `respond()`, not I-176.
- **Narrator discipline.** Uncued interjections are rare: no packet without an optional reaction produced a
  bystander speaking. The prompt line "Nobody else present speaks or interjects unless…" is obeyed.

**Verdict.** On this sample the I-176 tags add nothing useful: 0 motive engagements, and 2 of 4 bystander firings
are false positives from name collision. Their only live effect is word-regex `concerns_*` topic tags and
`concerns_self`.

---

## Fit of the proposed structural solutions

### A. "Testimony stored as words plus speaker, converted only at settlement when acted on; never rendered as a bare fact; reads 'Dunwen said…'"
- **Problem 1: partly.** Words plus speaker with settlement at a trigger **already exists**
  (`testimony.py`, PR-12-12), and settlement is what produced the garble. "Never render as a bare fact" fixes the
  visible Chance line. The cause still needs:
  1. **A narrow trigger.**
     - `rests_on` only when the beat's target, method or destination is the claim's subject; code can check this
       against the `said` record's `about`.
     - A Reader rule that "argues against it", "asks about it" or "repeats it" is not relying on it.
     - Or drop `rests_on` entirely and keep only (c) travel and (b) cited.
  2. **No settling of a speaker's claim about their own willingness or intent.** "I won't tell you while…" is an
     NPC-layer stance, not a world fact. Route it to willingness, or make the Framer view exclude `said.*` facts
     whose subject is the speaker.
  3. **A better claim packet:** names with pronouns, no ids in the view. Keep the predicate and value separate
     instead of slugging them together, and write `said_by` and `said_turn` on the fact as PR-12-12 step 4
     requires.
  4. **Testimony labels rendered from the original words**, e.g. `Dunwen said "no word while you hold me" −2`,
     never via `slug_words`.
- **Problem 3: misses.** "No one I know keeps the gate" was a code `who_is_*` generation fact, not testimony.
- **Problem 4: misses.** It does not touch pronouns.

### B. "Code decides only willingness and consequential reveals; the narrator decides who else reacts; retire I-176"
- **Problem 5: removes the cause** of the false-positive bystander reactions, and drops dead weight that has never
  engaged.
  - Caveat: `answer.willingness` also uses the refusal tags to return `unwilling`. Keep a direct map from refusal
    kind to the Framer's `asks` enum (the model's own judgement), or let willingness ignore refusals except on
    framed requests.
  - The observe-target path (Lilett's R6) should also go to the narrator under B.
- **Problem 3: misses most of it.** Willingness is not the wall. The wall comes from the **consequential-reveal and
  casting code that B keeps**, plus the narrator prompt. Needed:
  1. `cast_who` with no match falls back to the ordinary willing answer instead of a MUST "no one you know".
  2. Case routing only when the question's topic matches a node (the kin question was answered with "the way on").
  3. Fix `_SELF` so "who are they" is not the knower's name.
  4. An agreement such as "learn what he'd pay" must produce a value or must not be a MUST line.
  5. The narrator prompt explicitly lets a willing NPC give plausible ordinary answers in speech (they are
     testimony), with new persons declared as walk-ons, instead of "write around it".
  6. The first-interaction reaction roll takes the seeded stance toward the PC's incident (a "helps" quest-giver
     should not start Unfriendly).
- **Problem 2: misses.** Who reacts is not the issue.
- **Problem 4: misses.**

### C. "Fix the friend-bond bug"
- **Problem 2: needed, but aimed at the wrong place** if it means standing. Standing is already +2. The fix is:
  1. A speaker-card line: "is your friend (your anchor bond); Friendly toward you". Drop `bond.` from
     `_CARD_SKIP_PREFIX` for the PC's bond with this NPC, or emit the line directly.
  2. The same tag on the present-NPC SCENE SETTING line, so a "sly" demeanour reads as sly *with others*.
  3. The opening introduces the anchor NPC as known to the PC.
  4. Optionally, extend the bond relation check to the bonded NPC's own speech about the relationship. A friend's
     denial is not ordinary testimony.

### Not covered by A, B or C: problem 4 (pronouns)
Needed:
- Pronouns on every person-name line any role sees: `name_line` (testimony, Reader TESTIMONY lines), `spot_lines`,
  `also here`, cast list entries, R-lines and speaker-card `knows:` lines that name a person. This costs a few
  tokens per name.
- The speech pronoun check for named, stored persons that ROUND5 already proposed.

Both are small patches with the cause precisely located.

## Code references
- `engine/dm/testimony.py:142-161` (`_claim`: no pronouns, id view), `:184-232` (`settle`: line 199 slug, line
  215 fact without `said_by`)
- `engine/dm/packet.py:249-256` (Reader TESTIMONY / `rests_on`), `:137-154` (`spot_lines` without pronouns),
  `:492` (`name_line`), `:502-560` (`speaker_card`, `_CARD_SKIP_PREFIX` has `bond.`)
- `engine/dm/oof.py:195-220` (`fact_short`), `:243-245` (snag labels); `engine/text/render.py:159` (`slug_words`
  pc→you)
- `engine/dm/answer.py:247-285` (`willingness`), `:336-384` (`_who`, `cast_who` → `NO_ONE`), `:42` (`_SELF`)
- `engine/world/social.py:308` (`first_interaction` ignores stance)
- `engine/dm/npc_layer.py:333-411` (`event_tags`, `concerned`), `:513-655` (`respond`)
- `engine/audit/claims.py:1453` (pronoun check strips speech); be20402 (P-036 fix scope)
- `engine/dm/roles/prompts/narrator.md:13-23` (anti-invention vs speak plainly)
