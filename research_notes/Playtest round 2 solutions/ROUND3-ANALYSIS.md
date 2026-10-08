# Round 3 analysis: where the redesign stands, and what the remaining problems are

Written 2026-10-09 after the second pair of persona playtests on the merged round-2 code.

**Evidence:**
- Four live runs: talker and fighter on 3dc52fd, then talker and fighter on a02f758.
- Every live narration gate run.
- The offline long-horizon harness.

**Caveats:**
- The engine model is Haiku, and the player is a Sonnet persona told to find fault.
- Each run is 15 turns, so treat every rate as roughly ±10 points.
- Nothing has run on Gemini yet.

## 1. Did we fix the original problems?

These are the themes from the first handoff (§6):

| Theme | Then | Now | Verdict |
|---|---|---|---|
| A. Store too thin for a truth-gated narrator | empty successes, vague places, nameless incidents | seed packs, reduced cases; 0 empty successes; recall 1.00 | **Fixed** |
| B. Narrator–checker loop reverse-engineers prose | 1.3% first-draft pass, 58% cut | declarations + "check less": 95% / 0% / 1.05 calls (live) | **Fixed** |
| C. NPC agency "forbidden unless sourced" | NPCs mute, every act needed an exception | NPCs act and speak by default | **Over-corrected**: the default layer now *prescribes* what they do and say (§3, S1–S2) |
| D. Models choose what code could | wrong gates, forceful framings | gate, necessity and DC computed; Reader 92/98 | **Fixed**; remaining errors are segmentation |
| E. No difficulty rubric | 10% success / 45% critical failure on a crowd | guardrails + rubric + sim; one modifier per beat | **Fixed** |
| F. Rules text on screen | "Mode: fallback — DC +5" | OFFER templates, number plus word, one menu convention | **Mostly**: still dense; "curt −2", "paid" |
| G. String-munged rendering | "You try to gerella is…" | typed renderer | **Mostly**: one new garble, in the `/fix` reply |
| H. Missing rules subsystems | combat, riding… | holds, knockout, aftermath added | **Partly**: morale, sides, surprise and reactions are still missing |
| Memory and consistency | drift, repetition, view grows | coarse state by code, scene cards, capped views, cache 0.86–0.97 | **Fixed for state**; *dialogue* repetition is new (§3, S1) |

**Direction: good.** The early complaints were "raw error", "garbled", "NPCs never speak" and "the setup
loops". The current ones are about *feel*: stiffness, repetition, runarounds, clutter. The mechanical spine
works.

## 2. Current problems

These are drawn from the notes of all four runs.

| # | Problem | Seen in |
|---|---|---|
| 1 | NPCs answer "I don't know …, but X would", and X doesn't know either (runaround) | both talkers (8 turns, then 2) |
| 2 | NPCs repeat their own lines ("Tibgit Lucky" ×4, "day wages" ×3, "too loud for the room") | talker re-run |
| 3 | An NPC names someone, then denies knowing them | talker re-run |
| 4 | Idle activity lines every turn (rug, basket, dog); officers beating rugs in a hall; activities swapped between NPCs | all four runs |
| 5 | NPCs interject unprompted, even with their back turned | talker re-run |
| 6 | Stilted refusals ("The local news is not mine to give") | talker 1 |
| 7 | `/fix` replies are generic or about the wrong thing ("vitality 18", "logged", "say which fact") | both re-runs |
| 8 | A success that says it took the purse leaves no purse | fighter re-run |
| 9 | A stale lever ("beating a rug +2" after he stopped) | fighter re-run |
| 10 | Pronoun flips (he/she, "his") | fighter re-run |
| 11 | Two-part actions lose a part (the punch); a demand turned into a grab | both fighters |
| 12 | Season contradiction (spring vs "the autumn harvest") | talker re-run |
| 13 | A knockout after one hit contradicts the status line | fighter re-run |
| 14 | OFFER jargon ("curt −2", "paid", the third-person fail text) | both re-runs |
| 15 | Wrong attribute offered (Might for a lift; Agility would be better) | fighter re-run |
| 16 | Framer re-asks (2 per run; 8 before cluster B) | both |

## 3. Structural causes

About **two-thirds of the current problems trace to four causes.** The rest are patches.

### S1. Dialogue is over-determined by code (problems 1, 2, 3, 5, 6)

**The cause.** The answer ladder (PR-12-10) and the NPC response rows (12.11.9) decide what an NPC says:
- "does not know X, but Y would";
- "asks the PC something";
- "wants a price first".

Each decision goes to the narrator as a *must-name* record line, and the narrator has to voice it. Several
problems follow from that:
- The prose is stiff ("I do not know the hiring in Sandcrag, Jora").
- Re-asking the same question returns the same record line, so the narrator says the same sentence again.
  Ask-twice consistency was meant to prevent contradiction, and it produces repetition instead.
- The ladder never sees what the NPC itself said last turn. So Nibwen can name Laendil and then "not know" him.
- Pointers are generated, not lived, so a pointer can lead to someone who has never heard of the subject.

**Why it's structural.** R2-G already ruled that dialogue is *testimony*, not world truth. We then kept the
machinery that treats each ordinary answer as world truth needing a source (the Oracle ratification, the
proposer role, the index). The two halves of the design disagree.

**Structural option: "characters speak freely; truth is settled lazily."**
- **The narrator voices NPCs in character.** It works from:
  - what the NPC knows: their knowledge pack, their records, their role, public news, and what they have
    already said;
  - their willingness: standing, request size, refusals;
  - the scene.
- **What they say is recorded as testimony** on the speaker. It feeds back next turn, so the NPC neither
  contradicts nor repeats itself.
- **Code still decides two consequential things:**
  - whether a clue or secret is revealed: case placements, which stay strict;
  - whether the NPC is *willing*: standing and the refusal roll, already in code.
- **"I don't know" becomes the character's own choice.** It's rare and comes with a natural redirect.
- **Testimony becomes world truth only when it matters.** That happens when the player acts on it, cites it
  as a lever, or travels to the place named. At that moment it is settled: by the case if it's consequential;
  otherwise it's accepted, or settled at Likely odds. Spec 011 deferred exactly this "settle a said claim the
  player acts on".

**What it supersedes:**
- PR-12-10 rungs 2–4: knowledge-pack lookup, propose-and-ratify, the pointer;
- the `proposer` role;
- the answer index as a *speech* source (it stays as memory);
- the Talk response rows of the NPC layer;
- D1's T1b "Oracle settles ordinary knowledge". This needs owner sign-off: it loosens D1 the same way
  R2-G loosened checking.

**Risk.** NPCs say things that are false or inconsistent with the world. The mitigations:
- it is testimony (characters can be wrong);
- what they said is fed back, so they stay consistent with themselves;
- clues stay strict;
- the player can `/fix`.

### S2. Too much texture is mandatory (problems 4, 5, 9)

**The cause.** Code-generated texture is pushed to the narrator as content it must use:
- activities rolled from role × watch tables;
- detail slots;
- one response per present NPC per turn.

Hence the clutter, the same idle lines, odd fits (an officer beating a rug in a hall), and NPCs speaking out
of turn. Activity facts also become citable levers after they have gone stale. Cluster C hid unchanged
lines, which helps, but the cause is the rule that everything code writes is "record".

**Structural option: a must-name diet.**
- **Must-name only:**
  - the beat's outcome;
  - harm, conditions and quantities that changed;
  - the answer to a direct question;
  - a clue delivered;
  - a pause.
- **Optional material:** everything else (activities, posture, details, other NPCs' reactions). The
  narrator may use it, and no check requires it.
- **Activities:** rolled once per scene, from role-appropriate rows only. An activity ends when the NPC
  engages, and an ended activity can't be cited as a lever.
- **Non-addressed NPCs** respond only when the event concerns them (a matching tag), not every turn.

### S3. The feedback loop was built for precise disputes, not real complaints (problem 7)

**The cause.** The dispute machinery (12.3.6, `dispute.py`) was designed for exact claims ("you said 20
coins"). It pins with code first (numbers, names) and only then asks a model. Real reports are fuzzy:
- "the season is wrong";
- "I never got the purse";
- "Nero answered for the officer".

The code pinner grabbed an unrelated number ("vitality 18") and answered that, twice. Many reports are also
really *questions about a ruling* ("why didn't the success give me the purse?"). The loop then answers
"logged" or "say which fact is wrong". The scenario tests passed because they used precise, planted errors.

**Structural option: understand first, verify second.**
- **Understand first:** one model call turns the report into `{what the player believes, what happened,
  category, the turn}`, and says it back to the player in their own words.
- **Verify second:** code checks the record and the store.
- **Answer every report in plain language:**
  - "You're right, fixed: …";
  - "Here's why: the lift succeeded but the purse …";
  - "I can't find that; did you mean …?"
- **Bias toward acting on fiction and explaining on mechanics.**
- **Test against the real complaint corpus** we now have, the `/fix` lines from the re-runs, rather than
  only planted cases.

### S4. Successes don't carry a typed "what changes" (problems 8, 13, partly 11)

**The cause.** A beat's intended change (01.2.1) lives in prose: the Reader's intent and the restatement. Code
writes only the changes it knows about: harm, position (spec 010), knowledge (the ladder). "Take the purse"
succeeded, and nothing moved the purse. It's the same pattern as position before spec 010, which fixed one
case of it.

**Structural option.**
- Each beat carries a **typed intended change**: take or give *item*, move to *place*, open or close *thing*,
  learn *topic*, persuade *npc* to *act*, restrain or free *person*.
- Resolution **applies it on success** and the narration cites it.
- Spec 010's per-verb outcome table becomes one case of this.
- This also makes multi-part actions explicit: two changes become two beats, so the punch can't vanish.

### Patches (not structural)

- **Pronoun flips.** Pronoun checks were made log-only in "check less". A pronoun check on a *certain*
  subject is cheap and precise, so make it blocking again. **Lesson: "check less" should be decided by
  measured precision, not by claim class.**
- **The season.** The calendar line in the view should be prominent. Season words are a cheap code scan.
- **OFFER wording:** "curt −2", "paid", the third-person fail text.
- **Attribute choice** for lifting (Might vs Agility): rubric data.
- **The knockout status line.**
- **The remaining Framer re-asks.**
- **The `/fix` render garble**, folded into S3.

## 4. Recommendation

1. **S1 + S2 together, as one dialogue-and-texture redesign.** These are the main cause of how the game feels
   now. Rules revision: PR-12-10 shrinks to "clues by case, willingness by code, words by the narrator, truth
   lazily". 12.11.9 responds only when an event concerns an NPC. A must-name diet in 12.14.12. D1's T1b is
   loosened. **Owner sign-off needed.**
2. **S3, the feedback loop rebuilt as understand-then-verify,** tested on the real complaint corpus. It is the
   safety net that lets us keep loosening.
3. **S4, typed intended changes.**
4. **The patches**, batched.
5. **Then playtest:** two personas on Haiku, *and* one owner session on Gemini. That run is the first time
   anything has been measured on the target model.

**What not to do:** keep patching the ladder (pointer rules, chain limits, odds rungs). Each patch makes the
code-scripted dialogue a bit less bad, which is the same trap the first handoff warned about ("prompt-only
fixes are nearly exhausted; together they are a second, implicit rulebook"). The second rulebook has moved
from stopgaps into the NPC layer and the ladder.
