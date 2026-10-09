# Round 4 analysis: after the round-3 structural fixes

Written 2026-10-09.

**Evidence:**
- talker run 20261008-192926 and fighter run 20261008-192946, both on a6b1480 (specs 013–016 merged);
- the typed-change log `saves/*.changes.jsonl`;
- the earlier rounds, for comparison.

**Caveats:**
- The engine runs on Haiku and the player is a Sonnet persona told to find fault.
- Each run is 15 turns, so treat every figure as roughly ±10 points.
- Nothing has run on Gemini yet.

## 1. Did round 3 work?

**Yes, clearly.** For the first time, many player notes are positive:
- "Good opening scene."
- "The gate scene itself is vivid."
- "The odds screens were clear and the Go big option worked as described."
- "The fixes worked, though."
- "Ivas now says she brought the word herself, which fits my earlier fix."

| Round-3 target | Before | Now |
|---|---|---|
| Talk turns ending "I don't know" (runarounds) | 8/15, then 2/15 | **1/15**, a plausible one ("what the Circle wants with the roads") |
| NPCs repeating their own lines verbatim | Tibgit ×4, day wages ×3 | **0** |
| An NPC naming someone, then denying them | yes | **not seen** |
| `/fix` understood | "vitality 18", "logged" | **2/2 understood in each run, with corrections kept** |
| Idle activity lines every turn | every run | **gone** (scenery repetition is a different problem; see R6) |
| Purse taken but not delivered | yes | the take now applies (seen live: "Take the coin back"); see R5 for the new edge |

## 2. What remains

Across both runs there are about 20 complaints. They group into **five structural patterns** plus a few patches.

### R1. NPCs hedge too much ("I could not say", "I only hear it", "folk say")
Both runs. NPCs now answer, but wrapped in uncertainty, so the player gets little to act on.

**Cause:** R2-H's ruling "beyond what its card holds, an NPC answers from hearsay or a guess". Haiku reads this
as "always hedge".

**This is a calibration of S1, not a new wound.** Under lazy settlement, an NPC's ordinary claims are testimony
whatever its tone. Hedging protects nothing and only costs usefulness.

**Option:** NPCs speak plainly about ordinary things. A hedge is a characterisation choice (a cautious or
gossipy NPC), not the default. This is a small rules wording change plus one prompt line.

### R2. Groups aren't things you can talk to (the refugees, the carters, a queue)
- Fighter: "persuade the refugees to show themselves" was logged as `persuade_to`, `whom: none` (turns 4 and 7).
  A critical success then gave "no one named to persuade".
- Talker: "I asked the other carters…" was skipped.
- Earlier rounds: the queue and crowd problems (Hoba answered for people in a queue).

**Cause:** the entity model has individuals, while players constantly address groups. With no entity, the beat
has no target, the change is refused, and that part of the action is dropped or wasted.

**Option:** a **group entity**: a collective with a role, a count and a stance. A spokesperson is chosen by
casting when individual speech is needed. Groups can be addressed, persuaded and frightened, and members can be
split out on demand. Crowd responses (12.11.9) attach to groups.

**Structural.** It touches the cast and seed, the Reader's target scope, the change slots and the NPC layer.

### R3. Looking for someone or something not yet on stage becomes walking in place
Fighter: four turns of "go looking for the refugees" / "round the bend and keep searching", each typed as
`move_to` toward the town the PC is already in. The result was "a few strides short" over and over, with no
progress. Two rolls were automatic for walking, and the same scenery (smoke, mud) was repeated.

**Cause:** there is no **find** procedure. Searching for an absent person or place falls through to Move. Move
needs a target in scope, and the people being sought don't exist as entities until they are found.

**Option:** a `find` (seek) beat, covering searching an area for a named or described target:
- the target comes from the case or casting, or is generated when found (lazy, like the rest);
- one roll or none, depending on difficulty;
- the result is "found, and here they are" (the target placed in scope) or "not here; a lead".

Moving within a scene toward someone present should be one beat with no roll unless something obstructs it.
Spec 015 deferred `move_to`'s one-band-per-Move step, and this replaces that limitation. Travel between places
should narrate the arrival; the "street to hall with no travel" jump was the old P-098 again.

**Structural.**

### R4. The rest of a message after a pause gets lost
- Fighter: "…then demand their story" was dropped.
- Fighter turn 11: "Sheathe the sword. Then walk… Then force a way in" produced an OFFER titled "Sheathe the
  sword" that described forcing the door.
- Talker: "asked the other carters" was skipped and the player moved to the gate.

**Cause:** when a beat pauses (an OFFER, or a near miss), the message's remaining parts are queued, but they
aren't reliably resumed or answered afterwards. The title, restatement and change can also come from different
beats.

**Option:** a message is a **plan of beats** whose state is kept across pauses. After a pause resolves, the plan
continues, or the player is asked "still want to … ?". Each OFFER takes its title, change and odds from **its
own** beat.

**Structural, but contained** to the pipeline's plan and queue handling.

### R5. Successes with nothing to deliver
Examples:
- the critical success with "no one named to persuade" (R2);
- talker: "learn what the carters know" succeeded with nothing, and someone else answered in their place;
- a coin spent on a round with no result;
- "persuade Ivas", rolled at 60% after she had already agreed.

**Cause:** a change's applicability is checked only *after* the roll. D P5's rule "never offer a roll whose
success has nothing to deliver" was never enforced. Agreement already recorded (`agreed` from an earlier
`persuade_to`) isn't consulted before framing.

**Option:** validate before framing:
- a change with no valid target is resolved first (ask "who?", or route via R2/R3);
- a change already true is certain, with no roll;
- a `give` of payment attaches to the request it is paying for.

**Medium**, and largely dissolved once R2 and R3 exist.

### R6. The narrator repeats its own scenery (smoke, mud, voices, "marks unreadable")
Both runs.

**Cause:** freshness covers stored details and NPC lines, but not the narrator's own atmospheric phrasing.

**Option:** feed the last few deliveries' distinctive phrases back as "already said", which is cheap. The scene
itself also needs to change; R3's walking in place made this worse.

**Small to medium.**

### Patches (not structural)
- **"You agrees to Ivas carries word…":** the `persuade_to` plain-words renderer gets subject/verb agreement wrong.
- **An NPC opens by reciting her own name and title:** speaker-card content is leaking into speech.
- **The player's words put in their mouth twice ("Fair enough"):** the PC-agency check missed it, probably because
  it was attributed as speech.
- **Pronoun mismatch across scenes** (the carter's pronoun for Ivas). Check that 016's pronoun-in-setting covers
  absent people who are mentioned.
- **The roll display "d20 15 → 17 vs 10" confused the player;** the "[OFFER — auto]" label is jargon.
- **After a `/fix` that was accepted,** nothing on screen showed the repair and there was no recap of the scene.
- **The "Declare again" prompt** gives no recap.

## 3. Which are structural?

| Pattern | Size | Notes |
|---|---|---|
| R2 groups | structural | the biggest new gap; feeds R5 |
| R3 find/seek and movement granularity | structural | fixes walking in place, automatic walking rolls and travel jumps |
| R4 the message as a plan across pauses | contained structural | fixes dropped parts and mismatched OFFER titles |
| R5 deliverability before framing | medium | mostly follows from R2 and R3, plus an "already true means certain" check |
| R1 hedging | calibration | a wording change |
| R6 scenery repetition | small to medium | |
| Patches (7) | small | |

**Recommendation:**
1. R1 now; it's cheap.
2. R2 + R3 + R5 together, as one "targets that aren't individuals or aren't here yet" design.
3. R4.
4. R6 and the patches, batched.

Then playtest again, and run one owner session on **Gemini**, which is now overdue: every number so far is from
Haiku.
