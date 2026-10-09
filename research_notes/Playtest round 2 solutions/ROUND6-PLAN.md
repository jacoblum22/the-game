# Round 6 plan: traced causes and structural fixes

Written 2026-10-09.

**Evidence:** four read-only investigations in [round6-investigation/](round6-investigation/):
- I1: narration and text;
- I2: NPCs and testimony;
- I3: combat and feedback;
- I4: context audit and model size.

They traced every remaining problem through the saves, the model calls and the code, before any fix was designed.

**Direction:** the owner's philosophy, being written into the constitution and 00-architecture in parallel:
- code owns the spine;
- the model owns language and judgment;
- checks are kept only where they are measured to be precise;
- truth only when it matters;
- whole over parts;
- remove friction before adding procedure;
- better context, not more rules;
- diagnose from evidence;
- the player is part of error correction.

## 1. What the traces changed

Most first diagnoses were incomplete or wrong. Model size was not the issue: Sonnet split goal from method on the
same 7 of 8 messages as Haiku (I4).

| Symptom | First guess | Traced cause |
|---|---|---|
| Rolled the grip, not the demand | the Reader misread | The Reader prompt ("two changes are two beats"), `normalise` (never folds an against-will beat) and golden-set policy B5 all *require* the split. All 5 single-goal coercion messages split by act; in 2, the goal was never rolled. |
| Garbled odds line from speech | testimony leaked unsettled | Settlement fires on **64% of turns** (`rests_on`). The testimony call sees no pronouns. `settle()` accepts a speaker's *own refusal* as a world fact, which the Framer then cites as a −2 snag. 4 of 30 claims were garbled; 17 of 26 lost their subject. |
| Friend treated as a stranger | the bond doesn't reach standing | Standing +2 was correct. The speaker card **skips `bond.`** fields, the scene line said "sly", and the narrator prompt says "write around names or kinship". |
| Talk "feels like a wall" | willingness too strict | Willingness said "willing" **19/19**. The dodges come from code-written answer lines that are wrong or empty, plus that prompt line, plus a quest-giver whose reaction roll ignores his seeded stance. |
| Pronoun flips | — | Absent people's pronouns are in **no** packet, and the precision check skips quoted speech. 5 of 9 checkable lines were flipped. |
| Player's line echoed | spec 017 regression | The answered-question check demanded an "answer" to a *statement*; the blind repair restated the player's line. All 8 such demands were wrong, and 4 echoed. |
| Garbled "Then:" | spec 017 | The OFFER prints the Reader's internal `method` field raw. |
| `/fix` hint repeated | engine | A harness artifact: the persona sees the last 9,000 characters. |
| NPCs repeating each other | blind repairs | Four causes: a found clue re-delivered by code; blind repairs; the lead line in every packet, with sentences copied from recent exchanges; `/fix` complaints fed back as NPC "knows:" lines. |
| "settled between you" | — | The narrator obeyed "say it plainly; it is done" about a line `change.py` built from the *player's goal*. |
| Held NPC keeps hitting | rules gap | The rules already limit a held foe. The engine never applies a hold *condition* (it writes only text), and `foe_beat` skips break-free. 8 of 13 foe hits landed while held. |
| No low-Vitality warning | missing warning | By the Stagger rule, no single blow drops a PC above 0, and STAGGERED fired on time. A `/fix` take-back then **silently** restored Vitality to 1. |
| Narrated hit, then refused | ordering | Stored refusals made the Framer call the act impossible, and code trusted it. The refused turn still gave the foe a free strike. The player's own chosen "another way" was re-framed as impossible. |
| Hold penalises the holder | — | A successful grip writes "straining against you" on the target. The rule "every hindering fact is a snag" turns it into −2 on later grips. 12 of 26 fight Framer calls carried this. |
| `/fix` muddy | missing categories | Of 15: **1 right, 6 right but unclear, 8 wrong.** Causes: complaint text pinned as a fact; multiple complaints settled one after another; coin, bond and position never looked up; a refused turn labelled "misread"; plus the display-error and testimony-vs-record gaps. |
| Every role buried in rules | — | Rule text is 70–87% of input. Situation cards are the same lowest-numbered 8, sorted by id. The Reader lacks the cards it needs. Director, World and Checker see **no** conversation, though their prompts say they do. |

## 2. Five cross-cutting causes

1. **Code authors narrative content that models must treat as true.** Refusals stored as facts, "straining" and
   "on guard" labels used as snags, complaint text pinned as facts, a goal restated as an agreement, wrong answer
   lines, re-delivered clues, the Reader's method printed raw, a lead line in every packet. This is the same
   "second rulebook", in a new form.
2. **Atomisation:** the sentence array, act-splitting, per-part "answered" checks, per-fact levers, complaints
   settled one by one.
3. **Over-triggering rules:** settlement on 64% of turns, a 6%-precision answered check, "every hindering fact is a
   snag", "every part must be answered".
4. **Wrong context:** missing what's needed (absent people's pronouns, bonds, conversation for three roles), padded
   with what isn't (core rules, id-sorted cards).
5. **Mechanics as text, not state:** a hold as words rather than a condition, a coin never deducted, a take-back
   that doesn't show what it restored.

## 3. Fixes

Each is structural, follows the philosophy, and names what it retires.

### F1. Holistic narration
Covers stacked quotes, echoes, duplicated answers, and part of the repetition.
- One passage, plus a passage-level side list: who said what (as words), new elements, record items covered.
- Blocking checks only where measured precise, run on the whole passage. At most one revision, which sees the
  whole draft.
- Add a check for **quote marks on speech**, which is cheap and precise.
- **Retire:** the sentence array, per-sentence judging and repair, coverage "add" calls, the answered-question
  check, and "every part answered" bookkeeping.

### F2. Goal-first Reader
Covers method rolled instead of goal, the empty successes, and "Thanks." treated as a question.
- Whole message in. Out: goals per target (what, toward whom, and how), plus out-of-character flags (question,
  `/fix`, safety, pending answer). Split only on different goals.
- Change all three places that enforce the split: the prompt, `normalise` (fold against-will acts into the goal
  they serve), and golden-set policy B5, relabelled by the rule *before* looking at answers.
- The OFFER title and "Then:" render from the typed goal, never the raw `method` field.
- **Test across all goal and method shapes**, scored on Haiku against golden and held-out sets:
  - force in service of words;
  - movement in service of an act;
  - an object as the method;
  - deception;
  - stealth;
  - two real goals in one message;
  - conversation only;
  - questions mixed with actions.

### F3. Context per role
Covers rule bloat, missing information and repetition sources.
- Drop the 10k core and the id-sorted situation cards. Give each role a short guidance digest for its own
  judgment. I4 estimates input falls about 73%.
- Add the conversation to Director, World and Checker.
- Include **pronouns and bonds of any person named or mentioned**, present or absent, in the narrator and the
  testimony call.
- Show the lead line when a lead is new or relevant, not in every packet.
- Remove the prompt line "write around names or kinship".

### F4. Code stops authoring narrative truth
Covers the testimony garble, the wall, double-counted refusals, and "settled between you".
- **Testimony** is stored as words plus speaker.
  - Settled only when the player *acts on a specific claim*: travelling to a place it names, citing it in a
    roll, or a mechanical input. Not on every reliance.
  - A speaker's refusal or opinion is never a world fact.
  - Settlement sees pronouns.
- **Scene-state labels** (straining, on guard, activity) are never levers or snags. Revise 01.6.8: only
  mechanically relevant hindering facts count.
- **Code-written answer lines** are emitted only when they carry a real fact or clue. A failed cast or lookup
  writes nothing (the narrator handles it in character). A clue already found is not re-delivered.
- **`change.py` summaries** go to the RESULT block, never to the narrator as "it is done".
- **Complaint text** is never stored as a fact.

### F5. Mechanics as state
Covers the held foe still hitting, coins, and the silent take-back.
- A hold is a **condition** on the foe. `foe_beat` runs break-free first and respects the hold's limits.
- Payments deduct coin.
- Every state restore (take-back, correction) prints a "Now:" line.

### F6. Feedback loop outcomes
Covers 8 of 15 wrong and 6 of 15 unclear.
- Settle multiple complaints together on one snapshot.
- New categories: display error, testimony vs record, and a refused turn (not "misread").
- Route coin, bond and position complaints to their lookups.
- Every outcome ends with "Now:".
- Never pin complaint text.

### F7. Small items
- The quest-giver's reaction roll respects his seeded stance.
- The harness shows the persona only new output.

## 4. Order and lanes

1. **Constitution and 00-architecture**, in progress now.
2. **One rules wave, R2-J:**
   - the Reader split test by goal (01.2.2, 01.2.7);
   - testimony settlement narrowed, with refusals never facts (PR-12-12);
   - hindering facts mechanical only (01.6.8);
   - holds as conditions (06.5.x);
   - feedback outcomes (PR-12-11);
   - role context (12.2.4, 00.15.4);
   - the narration passage schema (12.3.x, 12.14.12).
3. **Four engine specs.** The first two can run in parallel; the second two follow.

   | Spec | Covers | Lane |
   |---|---|---|
   | **019** | F1 + F4's narration side | `narration.py`, `narrator.py`, `claims.py` |
   | **020** | F2 + F3 | Reader, `packet.py`, `cards.py`, prompts |
   | **021** | F4's testimony and answer lines + pronouns and bond | `answer.py`, `npc_layer.py`, testimony |
   | **022** | F5 + F6 | `resolve/`, `dispute.py`, `understand.py` |

4. **Test:** two Haiku personas, plus the replay bench, plus golden and held-out sets on a goal-shape breadth set.
   Then Gemini, when the owner is ready.
