# Worked examples for each step

Real examples from rounds 3–6 (2026-10-09), trimmed. Match their shape and tone. Full originals:
`research_notes/Playtest round 2 solutions/ROUND{3,4,5}-ANALYSIS.md`, `ROUND6-PLAN.md`, `round6-investigation/`.

---

## Step 2: collect symptoms (no diagnosis yet)

First record what the previous round's targets did, with numbers. Then list the symptoms as the player saw them.
Don't put a cause on any symptom yet.

> **What we set out to fix worked:**
>
> | Target | Before | Now |
> |---|---|---|
> | NPC hedging | about a third of lines | **1 instance** in the talker run |
> | Walking in place, wasted successes | several | **none** |
> | Dropped message parts, wrong offer titles | several | **none** |
>
> **Symptoms still showing (talker 20261008-232941, fighter 20261008-233000):**
> - The captain said "Mark me" five times. (talker, notes 29–31)
> - A friend listed on the character sheet denied the friendship. (talker, 24–25)
> - The odds line read "said will give no word out while you evine oakwell has a hand… on him". (fighter, 24–29)
> - An intimidation roll succeeded, but the NPC still refused. (fighter, 22)
> - `/fix` replied "it stays" and changed nothing visible. (both)

---

## Step 3: an investigator brief

The method lives in the `root-cause-investigator` agent type. The brief gives the area, the symptoms with run
stamps and input numbers, the fixes being considered, and the report path.

> Your problems: **NPC behaviour and testimony.**
> 1. **Testimony leaking into mechanics.** The fighter's (20261008-233000) Chance line read `said will give no word out while you evine oakwell has a hand… on him` (notes 24–29). Trace it end to end: how the NPC's speech became a stored fact (the `testimony` call), how the Framer cited it as a lever, and how the OFFER rendered it. Quantify testimony calls per run and how many triples are malformed.
> 2. **The PC's friend treated as a stranger** (talker 20261008-232941, notes 22–25). Trace where the creation bond is stored and why the narrator doesn't reflect it.
> …
>
> **Proposed fixes to test against:** testimony stored as words, settled only when the player acts on it; code decides only willingness and consequential reveals; fix the friend-bond bug. For each problem: removes the cause, partly, or misses it, and what would be needed instead.
>
> Report: `research_notes/Playtest round 2 solutions/round6-investigation/I2-npc-testimony.md`.

---

## Step 3 → 4: what traced findings look like

Each finding gives the symptom, the guess (if anyone made one), and the traced cause with its evidence and how
often it happens. This is what replaces guessing.

> | Symptom | First guess | Traced cause |
> |---|---|---|
> | Talk "feels like a wall" | willingness too strict | Willingness said "willing" **19/19**. The dodges came from code-written answer lines that were wrong or empty (`cast_who` "no one you know", misrouted questions), plus the narrator prompt line "write around names or kinship", plus a quest-giver whose reaction roll ignores his seeded stance. |
> | Held NPC keeps hitting | rules gap | The rules already limit a held foe. The engine never applies a hold *condition* (it writes only text), and `foe_beat` skips break-free. **8 of 13** foe hits landed while the foe was held. |
> | Rolled the grip, not the demand | Reader too small | Sonnet split the same 7 of 8 messages as Haiku. The Reader prompt ("two changes are two beats"), `normalise` (never folds against-will acts) and golden policy B5 all *require* the split. |

---

## Step 4: a family (a root cause, its symptoms, a structural fix, and what it retires)

> ### T1. Code authors narrative content that models must treat as true
> **Cause, traced:**
> - An NPC's refusal was stored as a world fact (`settle()` accepts the speaker's own refusal).
> - A successful grip writes "straining against you", which the snag rule turns into −2 on every later grip
>   (12 of 26 fight frames).
> - `change.py` restates the *player's goal* as an NPC agreement, and the narrator obeys "it is done".
> - Code-written answer lines carry nothing ("no one you know").
>
> **Symptoms it explains:** the garbled odds line; the refusal counted twice; the hold penalising the holder;
> "settled between you"; part of the "wall".
>
> **Structural fix:**
> - Speech is stored as words plus speaker, and settled only when the player acts on a specific claim. A
>   refusal or opinion is never a fact.
> - Scene labels are never levers. Only mechanical hindrances count.
> - Code writes an answer line only when it carries a real fact.
> - `change.py` summaries go to RESULT only.
>
> **Retires:** testimony triples on every line, the "every hindering fact is a snag" rule, and narrator
> instructions about code-built lines.

Another, shorter one (round 3):

> ### S1. Dialogue is over-determined by code
> **Cause:** the answer ladder and NPC response rows decide *what* an NPC says ("does not know X, but Y would").
> Each decision goes to the narrator as a must-name line it has to voice. Re-asking the same question returns the
> same line, and the ladder never sees what the NPC itself just said.
>
> **Symptoms:** "I do not know…" runarounds; verbatim repeats; an NPC naming someone and then denying them;
> stilted refusals.
>
> **Structural fix:** characters speak freely; truth is settled lazily. The narrator voices NPCs from what they
> know and what they've already said. Code decides only clue reveals and willingness.
>
> **Retires:** the ladder's speech rungs, the proposer role, and the Talk response rows.

**Patches**, kept separate from the families:

> - The `/fix` hint looked repeated, but that was a harness artifact: the persona sees the last 9,000 characters.
> - The garbled "Then:" line: the OFFER prints the Reader's raw `method` field. Render it from the typed goal.

---

## Step 5: a family in the owner's four-part format (round 7)

The owner asked for this after round 7: "a little more detail in the T1-7, maybe put them in simpler language, and
give the example from the play test and a separate example that you make up designed to show the breadth of the
problem". Every family in the phone update, and at the top of each family in the analysis, takes this shape:

> ### T1. The game flips a coin for things it already knows
> **In plain words.** When you act on a person, the game sometimes asks a yes/no dice roll about that same person:
> "Is he paying attention?", "Can she read?", "Will he tell you?". The answer is rolled instead of looked up, so it
> can contradict what the game already knows about them. The odds screen then counts the rolled answer against you.
>
> **From the playtest** (fighter, inputs 21–27). Belie is the town scribe: her record says she can read. A roll
> decided she can't. She said "I can't read a line of it", and the next offer screen asked him to *persuade her to
> read it*, with her illiteracy as a −2.
>
> **Another example (made up).** You ask the blacksmith to mend your sword. A roll decides "the smith can't work
> iron", so he shrugs at his own anvil, and your offer to pay him shows "can't work iron −2". Or an old friend you
> saved last week: a roll on "is she willing?" comes up no, and she turns you away. Anything the game already knows
> about a person (skills, attitude, what they'd agree to) can be overwritten by a coin flip this way.
>
> **The fix, plainly.** Every question has one owner: willing → their attitude to you; able → their record; not yet
> decided → the content makers. The coin flip only answers open questions about the world, and a rolled answer is
> never a penalty. *Retires:* pre-roll questions about the target and coin-flip "facts" on the odds screen.

**Why each part is there:**
- The plain words are the cause as a player would describe it. The mechanism is named ("a yes/no dice roll"); the
  module (`ask_oracle`) is not.
- The playtest example proves it happened, and the owner can find it in the transcript.
- The made-up example is a *different* person or situation. The owner judges a fix by how much it covers, and one
  instance can't show that. Close it with a sentence that generalises.
- The fix says what changes *in play* first, then what it retires.

**Too thin** (the round-6 style, now replaced):

> - **T1. Code writes story content the model must treat as true.** The garbled odds line, "settled between you".
>   *Fix:* code only writes real facts.

It names symptoms the owner hasn't seen, uses our jargon ("story content", "real facts"), and gives no example of
what goes wrong in play.

---

## Step 5: owner update, in plain words

**The round summary** (short, for a phone). The families below are in the old, too-thin style; use the four-part
format above instead:

> **What we set out to fix worked:** hedging went from a third of lines to 1 instance; walking in place and wasted
> successes went to 0.
>
> **What's left: four families** (each traced; full write-up in ROUND6-PLAN.md):
> - **T1. Code writes story content the model must treat as true.** The garbled odds line, the double-counted
>   refusal, "settled between you". *Fix:* speech stays speech until the player acts on it, and code only writes
>   real facts.
> - **T2. Things are broken into pieces.** One-sentence-at-a-time narration gives choppy quotes and blind repairs.
>   *Fix:* the narrator writes one passage.
> - …
>
> **My suggested order:** T2 first (it changes how text is produced, and some patches may vanish), then T1, then
> the `/fix` work.
>
> **Your decision:** one, below.

**A decision, explained as a concrete situation:**

> **"Vault the table and stab him": one roll or two?**
> The new goal-first rule folds methods into the goal's roll, but the combat rules give some moves their own roll.
> - **A (taken for now):** the vault keeps its own roll, then the stab is always rolled too. It fixes the bug we
>   traced without touching combat.
> - **B:** one roll for the stab, made riskier by the vault.
> - **C:** like B, and a successful vault also gives the stab a bonus.
>
> *My take:* B fits "whole over parts" better. A is the cautious choice. Keep A now and revisit with the combat
> work. **Nothing is blocked either way.**

---

## When the owner pushes back: re-trace, don't defend

> **Owner:** "I feel like even if I told an LLM 'talk like a pirate, he likes to say mark me' it wouldn't say it
> word for word every round, assuming it can see the conversation."
>
> **Response (after tracing the save):** "Your intuition was right. In turn 13 the captain's answer was written by
> **three separate model calls**: the first draft plus two repair calls that each *added* a sentence. The repair
> calls never saw the draft (I checked their inputs). A global freshness list would have treated the symptom. The
> real fix is one voice per turn."

Better still: trace *before* proposing anything, so this exchange never needs to happen.

---

## Steps 6–7: the "real gates" in a spec brief

> **Gates:**
> - Full suite passes. Add tests from the real saves: the fighter's four-turn walking loop becomes one approach;
>   "persuade the refugees" applies to the description.
> - Live: one talker and one fighter run, 15 turns, Haiku. Report hedges per NPC line, walking-in-place loops,
>   wasted successes, and scenery repeats, against the baseline.
> - If you tune a prompt on the golden set, report a fresh run on the held-out set as well. **Report real numbers;
>   if a target is missed, say so and name the dominant remaining error.**

And an honest result, as a spec agent reported it:

> Run 3 rescored was tuned on the answers it is scored on. Run 4 is the honest number: verb **85.7%** (target 95),
> computed gate **93.4%** (target 98).

---

## Step 8: a merge commit message

```
Merge spec 011 check less (narrator-voice blocking list, dialogue as said testimony, certain-subject verdicts, sampled audit)

Live (19 narrated turns, Haiku): first draft 42.1 -> 94.7%, cut turns 26.3 -> 0.0%, narrator calls 1.37 -> 1.05: all three live targets met (sample +/-10 pts). Suite 1691 passed; validator 0/0; ruff clean.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```
