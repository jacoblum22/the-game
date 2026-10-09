# Round 5 analysis: after specs 017 and 018

Written 2026-10-09.

**Evidence:** talker run 20261008-232941 and fighter run 20261008-233000, on 0d3f8c1. Both runs use the Haiku
engine with a Sonnet player persona. Each is 15 turns, so treat every figure as roughly ±10 points.

## 1. Did the fixes work?

**Yes.** Every target came in at or near zero:

| Target | Result |
|---|---|
| NPC hedging | 1 instance (was about a third of lines) |
| "I don't know" turns | 1 |
| Walking in place | 0 |
| Wasted successes | 0 |
| Dropped message parts | 0 |
| Mismatched OFFER titles | 0 |

**What players said:** the OFFER and near-miss menus were "clear" in nearly every note. The openings and the
gate scene were called "vivid".

## 2. What remains

### T1. Testimony leaks into mechanics as raw text
- The fighter's Chance line read: `said will give no word out while you evine oakwell has a hand… on him`. A
  lever cited a `said` testimony fact, and the OFFER printed its raw value. The `/fix` didn't help (see T4).
- In the talker run, "settled that I will learn what he'd pay" / "settled between you" came from the
  `persuade_to` plain-words line leaking into fiction.

**Cause:** PR-12-12 (R2-H) says citing testimony as a lever is a trigger to *settle* it first. Spec 013 deferred
that to 015 and 016, and neither built it. Testimony therefore reaches the Framer and the OFFER as if it were an
ordinary fact, and is rendered without the "X said…" framing.

**Option:** build the deferred trigger. When a frame input or lever reads testimony, PR-12-12 settles it first.
Testimony is never rendered as a bare fact: it reads "Dunwen said she'll give no word". **Small and structural:**
it finishes S1 rather than adding anything new.

### T2. Willingness and success disagree
Examples:
- Talker: Lilett, listed on the character sheet as the PC's **friend**, denies the friendship, contradicts
  herself, and dodges ("that's all I give you"). The player: "it feels like a wall".
- Fighter: an intimidation roll **succeeded**, but she "still refused the word".

**Causes:**
- **The creation bond doesn't reach the NPC's standing.** This is P-036 again: the bond is stored on the sheet,
  but the NPC layer reads standing elsewhere.
- **The rules never say whether a successful roll overrides a refusal.** Code-decided willingness can veto a roll
  the player won, which makes the success feel empty.

**Option:**
1. Make the bond the standing's starting point. This is a bug.
2. Rule that **success is willingness**. Within its reach, a successful Talk or threat gets what was asked.
   Refusal is what *failure* looks like, or what happens before a roll is offered (the NPC won't even engage).
   This removes a hidden second check.

**Structural, and a rules decision.**

### T3. Repetition: one turn's narration is stitched from blind calls (revised after tracing the save)
Examples:
- "Mark me" ×5 from the captain;
- "the missing child" said three times;
- answers that keep restating the same facts.

**Traced in the talker save (turn 13).** The captain's answer was written by **three separate narrator calls**:
1. the first draft;
2. a repair call that *adds* a sentence (`"replaces": "add"`) because a must-name item, the answer to the
   direct question, wasn't covered;
3. a second repair call that also adds a sentence.

**The repair calls never see the draft they are adding to.** The first draft's lines are not in their packets.
Each one wrote "Sevella answers about the missing child" from scratch, each opening with the habit. In the talker
run this happened on **5 of 14 turns** (7 blind add calls). The fighter run had none.

**A second, smaller cause:** the habit is stored as a rule, `habit = says 'mark me' before anything important`.
Every answer counts as important.

The owner pushed back: a model that can see the conversation doesn't normally repeat a catchphrase every turn.
That was right. **A global freshness list would only have treated the symptom.**

**Options: one voice per turn.**
- **Repairs see the whole draft.** A repair revises the draft and returns it, instead of appending a free-standing
  sentence.
- **Repairs become rarer.** The coverage gap that triggers most of them (the direct question) should be met by the
  first draft, or rendered from the record.
- **Habits are phrased as occasional.**

Separately, people's descriptions still go out every turn so pronouns stay right. Send only the pronoun line on
later turns. The player's own line being echoed back is a spec 017 regression (speech carried across a pause gets
restated); patch it.

### T4. `/fix` outcomes are muddy
Examples:
- "You're right… it stays", which the player can't tell from "nothing changed";
- "taken back" alongside "nothing changed on record";
- a garbled OFFER line answered with "it stays" and then reprinted unchanged;
- a pronoun inconsistency (an NPC said "her"; the record says he/him) dismissed as "he/him on record".

**Cause:** the understanding step works, but the outcomes don't:
- **No category for display errors.** A garbled OFFER isn't a fiction fact, so it falls into "the player's
  reading wins and stays".
- **No outcome for "two sources disagree".** Testimony and the record can conflict, and the loop has no clear way
  to settle it.
- **No visible repair.**

**Options:**
- Add `display_error`: acknowledge it, re-render, and log it for the owner.
- For inconsistencies: pick the record (or settle by the rules), say plainly what is true now, and correct the
  speaker's testimony.
- Always end with a "Now:" line showing the corrected state.

**Medium.**

### T5. Combat feel
Fighter examples:
- a held NPC keeps hitting with her free hand;
- Vitality fell 6 → 1 in one hit, with **no low-Vitality warning** before the next roll;
- the narration played out a hit with no roll, then a redirect said the action couldn't be done;
- the hold seemed to add a penalty *against* the holder.

**What these are:**
- The "grappled" restriction is a rules gap. It belongs with the combat subsystems still missing (I-154,
  I-156).
- The low-Vitality warning is presentation.
- The narrate-then-redirect contradiction is an ordering bug.

### Patches
- **"Then:" line garbled into the third person** ("saying she will be pursued after whoever the face was").
  This is in 017's restatement handling.
- **The "Something wrong? Type /fix" hint repeats recap text.**
- **Pronouns in NPC speech about known people** (Sevella her/his). The precision check covers only the narrator's
  voice. A known person's stored pronoun is cheap and precise to check in speech too.

## 3. Structural or patch?

| Pattern | Size |
|---|---|
| T1: finish S1 (settle testimony before mechanics; render it as speech) | small, structural |
| T2: bond reaches standing (bug) + "success is willingness" (rule) | structural, **owner decision** |
| T3: one voice per turn (repairs see the draft; habits occasional) | structural; small |
| T4: `/fix` outcomes (display error, inconsistency, visible "Now:") | medium |
| T5: combat feel (grapple restriction, low-Vitality warning, ordering bug) | mixed; part of the known combat gaps |
| Patches (3) | small |

## 4. Suggested order
1. T2's rule decision.
2. T1 + T3 together (both are about what text the narrator gets and returns; T3 is the blind repair calls).
3. T4.
4. The patches.
5. T5, which can wait for the combat-subsystems work.
