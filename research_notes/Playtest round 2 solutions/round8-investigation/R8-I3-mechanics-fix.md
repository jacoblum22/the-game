# R8-I3: mechanics, OFFERs and `/fix` (round 8, b6430a5)

This is a read-only trace of three saves: `playtest-20261010-013206-talker`, `-013226-fighter` and `-013246-explorer`.
- Transcript input `[N]` is `game_inputs.n = N+1`.
- A note written at `[N]` describes the screen produced by `[N-1]`.
- Rows are `model_calls.row_id`, and seq numbers are `events.seq`.

Fighter input-to-turn map:
- [17]=turn.2 and [18]=turn.3 (OFFER);
- [19]=turn.4 (go big) and [20]=turn.5 (/fix);
- [21]=turn.6 (OFFER), [22]=turn.7 (go big) and [23]=turn.8 (commit);
- [24]=turn.9, [25]=turn.10, [26]=turn.11 and [27]=turn.12 (kill);
- [28]=turn.13, [29]=turn.14 (/fix), [30]=turn.15 and [31]=turn.16.

Talker input-to-turn map: [21]=turn.6, [24]=turn.9, [26]=turn.11, [29]=turn.14, [30]=turn.15 and [31]=turn.16 (/fix).

## Summary: where the cause differs from the surface

1. **The "Persuade" shove is typed correctly. Code then turns it into a Grapple, and most of the fighter's other
   complaints come from that.**
   - Under 01.2.2 goal-first, the Reader's `persuade_to` (goal: he takes back his words; method: the shove) is right.
     The Framer correctly anchored Talk with **Might** ("physical menace", 01.18.7).
   - But `gate.covering_verb` (`gate.py:172-174`) rewrites *every* against-will Talk to `verb.grapple`. That one
     rewrite causes four things:
     - the alternatives become "shove instead (60%)" on a shove;
     - the grapple reach ladder hands the narrator "delivered: great: **Restrained**", so it wrote "pinning him",
       although no hold condition exists;
     - committing the beat starts a fight (06.2.1 via `_attacks`, from grapple's `trait.action.attack`);
     - the youth, now a foe, strikes in the same turn he "takes it back", and lands a hit the next turn with no die
       shown.
2. **"Presence +3 vanished" is also rules-correct but invisible.**
   - The attribute became Might, which is 0, and the P2 rule prints no zero term. So the Chance line shows only
     "(Influence +1)".
   - The DC also changed (12 → 10) because the target was **a different entity**.
3. **The fighter's freckled youth was generated three times**: a halfling `npc.lilwise_underhill`, then an elf
   `npc.erusse_…`, then a human `npc.aurard_de_morac`.
   - Each Director scene cut cast the *description* "the freckled youth who issued the challenge" as a new walk-on.
   - The /fix take-back deleted the second one, so the third was born.
   - "Aurard de Morac dead" is a name leak in `oof.changed_line` (`oof.py:663`), which bypasses `name_known`.
   - The "dives like a hare, then dead" was **code-authored**: `npc_layer.respond` rolled `tbl.npc_action` for the
     corpse ("R4 MUST: … acts: flees or takes cover"). The Fixer blamed the narrator.
4. **"Persuade the market square" is a chain of three code causes, not a Reader slip.**
   - Take the time charges **2 intervals (20 minutes) in free mode** (`pipeline.py:409`; the rule says twice the
     activity's own duration). Three charges made a one-hour scene, which ended on `time_jump`.
   - The Director's new scene at the market dropped the woman.
   - The Reader had no person to target, and `goal_line` printed the place slot.
   - Her silvers were never deducted: 44 coins before and after (DL-01-40 fired).
5. **The page-turn roll** happened because a Safe, sourceless frame's critical-failure-only gear cost cited a
   *narrated binding* ("scuffed at the corners"), and `necessity.costly` counts any cited cost.
6. **`/fix`: 3 right, 1 unclear and 2 wrong, out of 6 complaint items (5 reports).**
   - Both open-OFFER complaints ended in a take-back with no re-framed OFFER. `reframe` re-runs the Framer only, but
     the complaint lived in the Reader's typed goal and slots.
   - Fighter dsp.1 was wrong on the rule (it contradicts 01.2.2), and it misread the people card's "Push (trained)"
     (a Focus spend, `lic.focus.push`) as training in shoving.

---

## Symptom 1: a shove labelled "Persuade"; the odds changed (fighter [18]–[24])

**What the player saw.**
- turn.3: `[OFFER] Persuade the freckled youth who issued the challenge: shove him in the chest. … 60% (Influence +1)
  … Another way: feint first (65%) · shove instead (60%) · strike instead (60%)`.
- After the /fix take-back, turn.6 showed the same title with `(Martial +1)`, 60%.
- Notes [19], [20], [22], [23] and [24] (5 of the 14 fighter notes) name the "Persuade" heading. [20] is a /fix.

**Model calls.**

| Call | Output |
|---|---|
| Reader, row 10 (turn.3) | `verb.talk`, `change persuade_to what=npc.erusse…`, `description: null`, `against_will: true`, `pressure: threat`, `how: "shove him in the chest"`, `intent: "The challenger takes back what he said about the old healer."` |
| Reader, row 19 (turn.6) | the same, now with `description: "his challenge words taken back"` and target `npc.aurard_de_morac` |
| Framer, row 11 (turn.3) | anchor `anc.01_18_7` (Talk), **attribute `might`**, `deed_tag deed.influence`, opposed, stakes source aware observer, `cost.closed_door` |
| Framer, row 20 (turn.6) | anchor Talk, `might`, **`deed.martial`** |
| Framer THIS MESSAGE, both turns | `gate: G1 (normal) verb: verb.grapple` |

**Turn records.** The frames (seq 430, 473 and 489) all carry `gate.verb: verb.grapple`, `modifier {attribute 0,
competence 1}`, DC 10 and odds 60. turn.2's frame (seq 349) has `presence 3 + competence 1` against DC 12, with
`defender npc.lilwise_underhill`, a different entity.

**Code path.**
- `engine/resolve/gate.py:covering_verb` (172–174): `if against_will: return "verb.grapple" if verb == "verb.talk"`.
  It is called from `gate.py:227` and `schemas.py:760`.
- Title: `engine/dm/oof.py:goal_line` (351–352). For `persuade_to` it builds `"Persuade " + person` and drops the
  act. The method words follow.
- The Chance line comes from `oof.py:_breakdown`, which drops zero terms (12.15.2 P2: "no term worth 0 is printed").
- Alternatives: `frame.py:393` `ATTACK_SIBLINGS[gate verb]` gives feint, shove and strike, because the gate verb is
  grapple.

**Is a shove in service of words "persuade"?**
- **Yes.** 01.2.2 gives this exact pattern: "I pin him to the wall and demand…" is one beat of the goal's kind, its
  method force.
- Might for physical menace is 01.18.7's own knob.
- The player is still right that the *screen* is wrong:
  - "Persuade" names the change kind (a social category). It does not name what the player wants: *he takes back his
    words*.
  - The act slot of `persuade_to (person, act)` is never printed.
  - The attribute that replaced Presence is never named.
- The title should read **"Make the freckled youth take back his words: shove him in the chest."** For a request, it
  would read "Get X to …".

**Why the odds moved.**
- Presence +3 → Might 0 is the Framer applying 01.18.7's physical-menace knob correctly. It is hidden because the
  zero term isn't printed.
- 01.6.1 says the OFFER names the method that would use the higher attribute. The alternatives line did not, because
  it was built from grapple's attack siblings.
- On the sellsword OFFER (turn.16), where the gate verb stayed Talk, the line correctly offers "with Presence (75%)".
- Influence → Martial is the Framer's deed-tag choice (01.6.2, by method). The value is the same +1 floor.
- DC 12 → 10 is a different person entity (see symptom 4).

**Cause.**
- Scaffolding, not the model: code-authored mechanics (the covering-verb rewrite) and a title renderer that drops
  the goal's act.
- Anti-patterns:
  - **code authoring narrative truth**: a verb rewrite the Framer never chose;
  - **wrong context**: zero terms are hidden, so a changed attribute is invisible.

**Frequency.**
- 6 of 6 `persuade_to` OFFERs in the three runs are titled "Persuade <who>" with the act dropped:
  - fighter turn.2, 3, 6, 13 and 16;
  - talker turn.15.
- 5 of the 6 are threats or force, not requests.
- The Reader left the act slot empty in 3 of 6 (`description: null`). The act was only in `intent`.
- 2 of 7 Talk beats were against-will, and both were rewritten to Grapple.

**Structural fix.**
- (a) Give `persuade_to` a required `act` slot (a verb phrase), and render the title from it: "Make/Get <person>
  <act>: <method>". *Retires* the bare "Persuade" title and the act-less slot rendering (DL-01-39).
- (b) Always print the attribute's name in the Chance line, even at 0 ("Might 0, Influence +1"). Build the
  alternatives from the anchor's own `alt_attributes`, not from the gate verb's attack siblings. *Retires* "no +0"
  for the attribute term only.
- (c) Delete `covering_verb`'s Talk → Grapple branch (see symptom 3).

## Symptom 2: the "Go big" screen repeated; confirming twice (fighter [19], [22], [26])

**What the player saw.**
- Each `b` printed `[NOTE] You go big…` followed by the full OFFER again: 17–20 lines and about 190 words.
- The menu then changed to `[Enter] Show this again [d] Do it`.
- 3 of 3 go-big trades did this, and each needed a second key.
- At [19] the player also says "I'm unsure what Go big will change".

**Code path.**
- `pipeline.py:_answer_offer` (731–755) re-runs `_checked`, which produces a new `_offer` (the whole block).
- `play/render.py:enter_choice` (183–191): on a Dire frame, Enter is "Show this again". Going big from Risky always
  makes the frame Dire.
- The one-line trade explanations ("Go big: if it works you get more; if it fails it costs more; same chance") exist
  only in the `?` glossary (`oof.py:110`). They are never printed on the OFFER, although 12.15.2 says "The trades,
  one line each".

**Cause.** Mostly rule-plus-render.
- 01.7.3 re-shows the OFFER only for "Risky to Dire in a scene with `lethal_context`", but the code re-shows it
  always.
- 12.15.2's Dire rule then makes Enter non-committal.
- The trade line that would have told the player what changes is missing.

**Frequency.** 3 of 3 go-bigs, and 3 of the 10 fighter OFFER screens. 4 of the 10 screens repeat an earlier OFFER:
3 go-bigs and 1 post-/fix.

**Structural fix.**
- Print the 12.15.2 trade one-liners on the first OFFER.
- Make `[b]` "Go big and do it" a commit variant, except where 01.7.3 actually requires a re-show (lethal context).
- When a re-show is required, print only the lines that changed.
- *Retires* the unconditional re-show and the second confirmation.

## Symptom 3: a hit with no roll or warning after he "took it back"; shown pinned, then free (fighter [23]–[24])

**What the player saw.**
- turn.8 narration: "He swings at you with a wild fist… Your weight stays on him, pinning him where he stands…
  'Fine… I take it back.'"
- turn.9: the PC talks to the sellsword, and `[RESULT] the freckled youth who issued the challenge strikes you · hit ·
  Changed: Vitality 12 → 9`.

**Narrator packet (row 23, turn.8), THIS MESSAGE.**
```
- R1 MUST: beat: Shove the freckled youth …; approach: verb.grapple, might; difficulty: opposed; result: success;
  delivered: great: Restrained; acting on: the freckled youth who issued the challenge
- R2 MUST: position: you at arm's reach of Aurard de Morac
- R3 MUST: the freckled youth who issued the challenge agrees to what was asked
- R4 MUST: the freckled youth who issued the challenge acts: strikes at you and misses
```

**Events.**
- seq 494–495: `conflict_start`, "the PC attacks (06.2.1)", at commit.
- No `condition_*` event exists in any of the three saves: no hold was ever applied.
- Foe d20s: rng 67 = 1 (miss, turn.8) and rng 68 = 9 (hit, turn.9, seq 546). Neither die was shown.

**Code path.**
- `covering_verb` makes the beat a Grapple.
- `pipeline.py:_attacks` (797–804) sees grapple's `trait.action.attack`, and `_roll` then starts the conflict (808–812).
- `pipeline.py:_reach_words` (1068–1074) takes the reach ladder from `frame.gate.verb` (grapple), not from the
  anchor (Talk). Rung 3 is `cond.restrained`, which the narrator line prints as "Restrained".
- `scene_state.beat_writes` (85–87) correctly writes no hold posture, because no hold exists. So "pinned" exists only
  in the narration.
- `world_step.foes_act` → `conflict.foe_beat` (240–275) has no test for a foe who just agreed to the PC's demand.
  Morale, `h.06.*`, is "not yet built" (seq 497, 500). The foe acts every spent turn.
- `world_step._foe_turn` prints "strikes you · hit" with no die.
- Because the approach is `verb.grapple`, the narrator's "it worked: the one asked answers" line (`narrator.py:119`)
  and `npc_layer`'s talk-outcome branch (`"talk" in approach_words`) are both skipped for a persuasion that
  succeeded.

**Cause.**
- Scaffolding: the Talk → Grapple rewrite made a persuasion into an attack and a hold that never existed.
  - **Mechanics stored as text**: "Restrained" was given as a word, with no condition.
  - **Code authoring narrative truth**: R4's swing in the same beat as the agreement.
- The "suddenly free" is not a broken-hold bug. There was never a hold, so `foe_beat`'s break-free branch was never
  reached.

**Frequency.** 1 conflict in 3 runs, started by 1 of 2 against-will Talks (the other, turn.3, was taken back before
commit). There were 2 foe strikes (1 miss, 1 hit), both after an agreement, and 0 hit while a real hold was on.

**Structural fix.**
- (a) Remove the against-will Talk → Grapple rewrite. A shove for words is Talk with Might, and the shove is a method
  consequence. A real hold is typed `restrain`.
- (b) Take reach words from the frame's anchor, never the gate verb.
- (c) An agreement written on a foe this beat ends that foe's part in the conflict (or 06.11's morale, when built).
  A started fight gets a one-line notice, and a foe's strike shows its die.
- *Retires:* `covering_verb`'s Talk branch, ladder words without their condition, and the silent conflict start.

## Symptom 4: "Aurard de Morac dead" (fighter [27]–[28])

**Who it is.** `npc.aurard_de_morac` is the third instance of the freckled youth:

| Seq | Turn | Created by | Entity |
|---|---|---|---|
| 317 | turn.1 | npc_generation | `npc.lilwise_underhill`, a halfling with "freckles across a sunburnt face", labelled "the challenger, who is more than they seem" |
| 410 | turn.3 | Director row 9, `cast_described: ["the freckled youth who issued the challenge"]` | `npc.erusse_of_the_seven_springs`, an elf |
| 448 | turn.6 | Director row 18 | `npc.aurard_de_morac`, a human |

- `npc.erusse_of_the_seven_springs` was reverted by the /fix take-back of turn.3, which is why the third was created.
- The Director's view lists only cast-list people, never present walk-ons, so it re-described an existing person.
  This is I2's area; the mechanics consequence is that the DC and the defender changed.

**Was the right entity killed?** Yes, in the sense that it was the frame's target (frame.3, `obstacle npc.aurard…`)
and the youth the narrator had voiced since turn.6. `npc.lilwise_underhill`, the original "challenger", is still alive
and present.

**What RESULT printed.** `oof.py:changed_line` 662–664:
`name = _ent_name(state, eid) or (… if name_known(…) else "your opponent")`.
- `_ent_name` returns the raw name for any visible entity, so the `name_known` guard is dead code.
- The narrator packet's position line also carries it ("R2/R3 MUST: position: you at arm's reach of Aurard de
  Morac").

**The death narration.** Narrator row 30, turn.12:
`R2 MUST: harm … dead` and then `R4 MUST: the freckled youth … acts: flees or takes cover`.
- `npc_layer.respond`'s `person()` (561–563) has no down or dead filter. After the conflict ended, the corpse was
  "engaged" as a target, got a reaction roll (rng 70–71) and `tbl.npc_action` row 2 (rng 72).
- That wrote `fact.131` "taking cover" and `fact.132` "frightened".
- The next scene rolled him an activity, "on an errand" (fact.143).
- The narrator obeyed a MUST.

**Anti-patterns:** **code authoring narrative truth** (a table row for the dead) and an identity leak.

**Frequency.** 1 kill and 1 leak. Every non-PC Vitality change goes through `changed_line`, so every visible NPC's real
name would leak on a hurt.

**Structural fix.**
- (a) `changed_line` uses `display_name`, the PC-knowledge name.
- (b) `respond` and `ensure_activities` skip anyone `is_down` or dead.
- (c) Director casting resolves a description against the people present before it generates anyone.
- *Retires:* the dead `name_known` branch, rows for the dead, and duplicate walk-ons.

## Symptom 5: needless or odd rolls (talker)

### 5a. "You can't judge how hard this is" for turning a page (talker [21]→[22], turn.6)

- Reader (row 18): `verb.observe`, `learn what=item.gate_log`, `description: null`, `how: "Turn the page back"`.
- Framer (row 19): Research anchor, `easy`, `stakes.source: none`, `secret: true`, and threatened cost `cost.gear`
  ("pages fray") **with `source_fact: fact.99`**. fact.99 is `item.gate_log binding = "thick, leather-covered,
  scuffed at the corners"`, a narrated detail (seq 382).
- `necessity.costly` (`necessity.py:146-147`) counts "a cost cited to a fact" even when the cost fires only on a
  critical failure (a Safe frame names one by 01.6.11). So the beat counted as COSTLY, rolled, and was secret.
- The Framer was pushed to cite a fact by 01.13.1: "an entry with no citable source is not a candidate".
- Title: "Learn about the gate log: Turn the page back." The goal ("whether the cart came through before") was lost to
  the slot.
- **Cause:** a low-precision COSTLY test, plus an instruction that forces a citation. This is **over-triggering**.
  - DL-01-44 fired: a Safe, sourceless, retryable frame rolled.
- **Fix:** in `costly`, ignore a Safe frame's threatened cost (it is critical-failure-only by 01.6.11). A cited cost
  counts only on Risky or Dire. *Retires* the cited-cost loophole.

### 5b. "The offer's target reads 'the market square'"; the coin confusion (talker [30]→[31], turn.15)

The chain:
1. The woman is `npc.belo_applebottle`, shown to the Reader as **"the people of Redcrag gathering to look at the
   sky"**, a crowd label (rows 35, 38 and 41). At turn.14 the Reader could not link "the silver-haired woman" to it
   and set `target none`.
2. Three take-the-time beats each charged **2 intervals = 20 minutes** (seq 434/443, 479/488 and 545/554):
   - turn.9, stepping out to her;
   - turn.11, following her;
   - turn.14, a paid question.
   `pipeline.py:_no_roll` (409–411) uses `"interval"` for every mode except travel and downtime. 01.4.4 says free mode
   costs "twice the activity's listed duration", which for words is seconds.
3. That came to one hour, so `scenes._time_jumped` ended scn.1 (seq 591/623, `time_jump`). The Director started scn.2
   *at the market* with the cast `[npc.morri_deepforge]` only (seq 639). The woman left the view.
4. Reader row 47: `persuade_to what=loc.high_hundred_redcrag.market`, `target none`, with the woman only in
   `description`.
5. `goal_line` printed "Persuade the market square".

**Coin.**
- The fiction took two silvers (turn.12 and turn.14), but the sheet shows `coin 44` before and after. There are no
  coin events in the save.
- `npc_layer.respond` reaches `pay_deal` (599–602) only in the `talks` branch. That branch comes *after*
  `if npc in answered: pass` (588). A paid **question** is answered by PR-12-10 first, so the deal is never paid.
- The /fix `Now:` line showed coin 44.
- This is **mechanics stored as text**. DL-01-40 fired ("a missed deduction is an engine bug").

**Frequency.**
- 4 of 4 take-the-time beats charged 20 minutes (talker 3, explorer 1, a look around a taproom). One of them broke a
  scene.
- 2 of 2 paid answers went unpaid.

**Fix.**
- (a) Take the time in free mode charges twice the activity's own time, as 01.4.4 says (minutes for talk).
- (b) The Reader's people card uses an individual's label, never a crowd description.
- (c) A `pressure: offer` with a `player_quantity` pays at RECORD, whatever path answers (01.11.2).
- (d) `persuade_to` with a place in the person slot is refused at the schema.
- *Retires:* the interval default and the answer-path bypass of deals.

## Symptom 6: jargon and long screens

| What | Count | Where it comes from |
|---|---|---|
| `[RESULT] no roll (take the time: a good while passes) · success · evidence as a no-roll success` | 4 | **Rule-authored**: 12.15.3 prescribes the "evidence as a no-roll success" wording (I-054), and `pipeline.py:412` prints it literally |
| `Fate: 1 (no reroll: you won't see this die)` | 1 | `oof.py:451` |
| `Fate: 1 (you may spend one…)` | 11 OFFERs | `oof.py:451` |
| /fix `Done: took back turn N` | 4 of 4 take-backs | Internal turn numbers the player never saw |

- OFFER length: 12 screens, median 18 lines and about 175 words (fighter 135–204).
  - Every Risky OFFER prints its failure clause twice, word for word, once for "fails" and once for "Badly"
    (`oof.py:offer_block`, `_cost_clause` used twice).
  - 9 of 12 have 1–2 "Whatever the roll" lines that only restate the declared act ("the mace is swung at the youth's
    ribs whatever the roll"). This is **mandatory texture**: framer.md:44 asks for consequences without 01.11.2's
    closed-source test.
- **Fix:**
  - Drop the evidence clause from the player screen (keep it in the log), and amend 12.15.3.
  - Print "Badly (5%): worse, serious".
  - Drop method consequences that are the act itself (01.11.2(d)'s test).
  - Show fate only when it can be spent.
  - Print player input numbers, not turn ids.

## Symptom 7: after a /fix take-back, nothing re-established the scene (fighter [20]→[21])

- After every take-back (4 of 4), the screen ends at `[CORRECTION] … Done: took back turn N … Now:`.
  - Spec 026 assumption 3 runs no narration on a dispute turn.
  - The last passage on screen, turn.3's "the push is already on its way…", is now void, but nothing says where
    things stand.
- The take-back also reverted generated people and scenes (seq 410–438: `npc.erusse…`, scn.2). The redeclaration
  therefore produced a new scene (scn.3, mode `conflict`, chosen by Director row 18) and a new youth with a new name
  and people.
- **Cause:** a silent take-back, which is **mechanics stored as text** in the handoff's own words.
- **Fix:**
  - After a take-back, one narrator call (or the last surviving passage) re-states the restored scene in a sentence or
    two.
  - A take-back keeps the `entity_created` writes for people already shown on screen.
- *Retires:* "declare again" blind, and regenerated people.

## Symptom 8: persuasion right after a killing; "'swung first' is spoken whatever the roll" (fighter [28]–[30])

- Reader row 32: `persuade_to`, `pressure threat`, intent "No one in the room takes the dead youth's side". That is a
  correct goal.
- The odd feeling is symptom 1's title again ("Persuade the people in the silent room…"). It should read "Make the
  room stay out of it".
- The "whatever the roll" line is Framer row 33's method consequence. It is rules-legal (the words are said), but
  it adds nothing: symptom 6's mandatory texture.
- **A separate bug:**
  - The beat has `target none`, and the Framer's defender was a freshly generated `npc.samie_honeyburrow`.
  - `change._person` (112–126) then resolved the description through `resolve_names` to **Ghazka**.
  - So the RESULT read "Agreed by Ghazka Who Came Back: No one in the room… but not the whole room: one voice…".
  - This is a low-precision name match: the agreement was written on the wrong person (fact.144).
- **Fix:** a description with no single present match takes the DL-12-97 `_described` path, and never a fuzzy name.

## Symptom 9: a superior ordering a subordinate (spec 027 f04)

**It did not recur:** 0 superior-to-subordinate asks occurred in the three runs, so the open question is untested.

The nearest sibling is that every non-request pressure is typed `persuade_to` and titled "Persuade" (5 of 6). The
act-slot title in symptom 1 would also give f04 a truthful title ("Get the guard to open the gate").

---

## `/fix` scores (spec 026's after-screen standard, graded as in R7-I3)

| # | Run, item | Complaint | What the Fixer did | After-screen | Grade |
|---|---|---|---|---|---|
| 1 | talker dsp.1 (5 calls) | "Persuade the market square" | Re-framed with a note; the dry run still said "Persuade the market square" (row 53); then took back turn.15 | The honest CORRECTION; "declare again, aimed at her" | **Unclear.** The surface is right, but the cause (the woman was dropped from the scene and labelled as a crowd) is untouched, so a redeclaration would mis-target again. The unpaid silvers were not noticed. |
| 2 | fighter dsp.1 (5 calls) | Shove as "Persuade"; Presence +3 gone | 1: take_back, refused by validation ("turn.3 was not looked at"); 2: reframe with the note "frame the shove as a physical action", which came back the same; 3: take_back | CORRECTION with no scene | **Wrong.** It contradicts 01.2.2 ("should not have been judged as persuasion"). "You are trained in Push" misreads `lic.focus.push` (a Focus spend; the card prints "Push (trained)" unglossed). It never explains Might. The take-back created duplicate youth #3. |
| 3 | fighter dsp.2 (4 calls, shared) | The unknown name in RESULT | Explained: the bookkeeping name is a display slip | The explanation, then the OFFER re-shown | **Right.** It is accurate and nothing needed repair (the code bug remains). |
| 4 | fighter dsp.3 (shared) | "Dives like a hare, then dead" | Explained it as "the narration slipping, not a separate event" | The explanation | **Wrong.** The `calls` tool showed `R4 MUST: … flees or takes cover`. The cause was code (`respond` on a corpse), and fact.131/132 stay on record. The player accepted it. |
| 5 | explorer dsp.1 (4 calls) | Betric answered for the sellsword | take_back turn.6 | The CORRECTION; the redeclaration was answered by the sellsword ([23] note: "fixed properly") | **Right.** The repair worked. The cause was code's addressee pick (R1 MUST "Betric … answers"), not "the narration", so the explanation is partly misattributed. |
| 6 | explorer dsp.2 (4 calls) | The guard answered for Gribnik | take_back turn.12 | The redeclaration was answered by Gribnik | **Right.** The same misattribution: code's `R1 MUST: the guards at the door acts: answers`. |

**Totals:**
- 3 right, 1 unclear and 2 wrong, out of 6 items. Round 7 had 1 right and 2 wrong out of 3.
- 2 of 2 open-OFFER complaints ended without a re-framed OFFER.
- 4 of 4 take-backs left no scene on screen.

**Shared Fixer causes:**
- (a) `reframe` re-runs gate, necessity and frame on the *same Reader beat*, and the spec 027 note goes to the Framer
  only. So a complaint about the goal, slot or title can never change via a re-frame. Both open-OFFER complaints
  were of this kind.
- (b) The mechanics digest has no goal-first line (01.2.2) and no attribute knob (01.18.7: Might for menace).
- (c) The people card prints licence names without what they do ("Push (trained)").
- (d) The Fixer attributes MUST lines to "the narration" (3 of 3 narration-side items).

**Fix:**
- `reframe` may re-run the Reader with the note, so the typed goal and slots can change.
- Add 01.2.2 and 01.18.7 to the digest.
- The people card glosses Focus licences ("Push: spend Focus for reach").
- The `calls` tool marks MUST lines as code-authored.

## Round-7 targets, measured

| Target | Round 8 | Note |
|---|---|---|
| Rolls with nothing at stake | **2 of 5** committed rolls | Fighter frame.1 (Safe, contested, "nothing lost"; legal under 01.4.1) and talker turn.7 (the cited-cost loophole, §5a). Round 7: 3 of 5. |
| Oracle facts about a target | **0** | 0 `fact_questions` in 32 Reader calls; 0 Oracle events. |
| Garbled labels | **6** | "Persuade the market square"; "Learn about the gate log: Turn the page back."; "shove instead (60%)" on a shove; "Agreed by Ghazka…" for the room; "Changed: Aurard de Morac dead"; frame.1 "pay (your gear suffers)" (an empty `form_intent`, `first_fitting_cost` substituted). 0 snag slugs. |
| Verb-keyed gate misses | **3** | 2 against-will Talks keyed as Grapple (§3). Explorer turn.2 "look around the taproom" was gated G2 `lic.training.influence_etiquette` (`gate._plain_cover`: a held licence whose crude-fallback verb is Observe). |
| Rolled beats with no typed goal | **0 of 7** framed beats | — |
| Near-miss prices that reverse the goal | **0** | No near miss rolled; 0 of 6 close-call prices reverse their goal. |
| Holds, and hits while held | **0 holds, 0 hits while held** | 1 narrated "pin" with no condition, and 2 foe strikes after an agreement (§3). |

## "Revisit if" conditions that fired

| Entry | Status | Evidence |
|---|---|---|
| DL-01-39 | **Fired** | OFFER titles misread more than once per run (fighter: 5 notes over 2 distinct OFFERs; talker: 1) |
| DL-01-40 | **Fired** | A missed deduction (the talker's silvers, §5b) |
| DL-01-44 | **Fired** | A Safe, sourceless, retryable frame rolled (talker turn.6, §5a) |
| DL-12-116 | **Fired** | 3 of 6 right, below 5 of 7; a repair hinged on a field the Fixer could not read (Push) |
| DL-12-117 | **Fired** | Both open-OFFER complaints answered without a re-framed OFFER |
| DL-12-123 | **Fired** (letter) | A re-frame given a note repeated the disputed 60% OFFER. Here this was correct (the note was wrong); the real gap is §/fix (a) |
| DL-06-16 | Arguably | Adversaries "behaving stupidly": attacked after yielding, and a corpse took cover. The cause is code, not list length, so the DL's remedy does not fit |
| DL-01-43 | Not by the letter | The gate ran, but Talk's downstream checks (the talk outcome and the "it worked" line) keyed on `verb.talk` and were skipped |
| DL-06-31 | Not fired | No condition existed; a narrated pin is the textual variant |
| DL-01-13, -14, -47 | Not fired | — |

## Shared causes across symptoms

1. **`covering_verb`'s Talk → Grapple rewrite** affects symptoms 1, 3 and 8: the alternatives, "Restrained", the
   conflict, the foe strikes and the skipped Talk lines.
2. **Take the time charging intervals in free mode**, plus the scene's time-jump. This affects §5b and caused the
   talker's /fix.
3. **Director casting by description, with no match to the people present**, plus a take-back that reverts
   generation. This affects symptoms 1 (DC 12 → 10), 4 and 7.
4. **`goal_line` rendering persuade_to without its act.** This affects symptoms 1, 8 and 9, and the talker's
   "market square".
5. **`npc_layer.respond` gating on path order, not on state.** This affects the corpse's action (§4), the unpaid
   deals (§5b) and the wrong agreer (§8).
6. **The Fixer cannot change Reader-owned typing.** This affects both open-OFFER disputes.
