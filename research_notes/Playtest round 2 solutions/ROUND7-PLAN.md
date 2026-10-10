# Round 7 plan: approved fixes

Written 2026-10-09, after owner review of [ROUND7-ANALYSIS.md](ROUND7-ANALYSIS.md). The evidence is in
`round7-investigation/`:
- traces I1–I3;
- history traces H1–H2;
- the research on improvised details, R1.

Every fix below is **owner-approved**. Each one names what it retires.

## Owner rulings (quote these in the DL entries)
- T1: "1 is good." T4: "4 seems good."
- **T2.** "It feels like potentially we could just let the LLM have people make up the amount, who posted it,
  where he was seen, etc. if it's not decided by a pre-existing fact, unless you think that could cause problems or
  something, in which case your solution seems good."
  - Then, after the research: the split approved ("I approve everything else you said").
  - The split: hooks get their pay, destination, issuer and people decided when they are created; characters
    improvise everything else as testimony.
- **T3.** "If it wants to mention the look or habit more than once, and it's aware that it already used it, then I
  think it's fine if it uses it more than once. I don't think we should prevent it or encourage it."
  - So: remove the pushes, and add no tracking.
- **T5:** the extended fix builds on round 6's goal-first rule, and does not undo it. Approved.
- **T6:** take the time comes back, decided on the Framer's typed stakes. Approved.
- **T7.** "the goal was to make slash fix work just like you… you seem to figure out what the problem is, and it
  seems like you're able to to potentially revert it if necessary." Approved: the redesign in §1, T7.
- **D2 (clues) and D3 (willingness):** "Yup, I approve of A for both of these."
- **Process.** "every fix must also pass made up cases, including cases specifically design to test edge cases.
  Revisit the revisit notes too."

## 1. Fixes

**T1. One owner per question.**
- An addressed NPC's *will* goes to willingness.
- Their *ability* goes to their record (licences, competences, role).
- *Unwritten content* goes to its maker (see T2).
- The yes/no Oracle answers only open questions about the world, never about the beat's own target.
- An Oracle answer is never a snag (01.6.8).
- Odds labels are plain words, never slugs.
- *Retires:* pre-frame Oracle questions about the target; `_KNOWS_Q`; Oracle booleans standing in for content; slug
  labels (`turn.py:421`, `oof.py:234`).

**T2. Hook terms are authored; everything else is improvised.**
- When a hook (lead, notice, offer, incident) is created, code also decides its key terms: the pay (from the fee
  tables, economy AI-6), the destination, the issuer and the people involved. These are written as unsealed
  knowledge on the cards of the people who'd know.
- Everything else is improvised in character and stored as testimony, settled only when the player acts on it.
- Guards:
  - a speaker sees what others said on the same topic;
  - a price spoken outside a hook uses the price band at settlement;
  - a place first heard in speech becomes a real site when the player travels there;
  - the Director can cast a *description* ("the carters") present in a scene.
- A deal carries a typed price.
- **D2 A:** a small model call judges whether a question to a clue holder is about the clue they hold. If yes, code
  hands the clue to the narrator to deliver.
- *Retires:* word-overlap case routing (`case_about`); random walk-ons for a stated purpose; the regex price from
  Framer prose; yes/no answers to what/where/how-much.

**T3. Stop pushing texture.**
- Looks and habits are background, never must-use.
- Habits are worded as occasional ("sometimes…").
- The freshness block no longer quotes images back.
- Refusal and answer lines don't require the habit (`npc_layer.py:491`).
- No code-written narrative sentences ("X brought the word"; verbatim faction labels). The data is given as data.
- Templates use the person's real pronouns.
- **No usage tracking, no gates.** Afterwards, measure repetition with the full conversation in view.
- *Retires:* `incident_line` in every SCENE SETTING; the raw `voice`/`detail` push; the habit exemption in 12.14.11
  as a forced callback; pronoun-neutral template strings.

**T4. One outcome.**
- One function gives the effective degree (success at a cost counts as success), and every reader uses it:
  `npc_layer.py:570`, `answer.py:271`, `scene_state.py:160` and the willingness or refusal voicing.
- A paused beat is unresolved in the narrator's record until the player chooses.
- *Retires:* degree-only checks; "a near miss" narrated before the choice.

**T5. The goal flows through.**
- Every rolled action carries its typed goal (no `change: none` on a rolled beat).
- Gates and checks key on the goal *and* its method, not the verb label. Reading writing needs Letters whether it is
  phrased as look or talk.
- The 01.9.3 check covers any success-at-a-cost price that reverses the goal against the same target.
- A fallback is framed on its own scope.
- *Retires:* verb-only gate keys (`gate.reads_writing`, `certain_talk`, secret frames keyed on verbs);
  description-first OFFER titles; double-counted fallback difficulty.

**T6. Take the time.**
- When the Framer's typed frame has no stakes source and no failure cost, there is no roll: the action succeeds at
  Standard and the time is charged (01.4.4), for every verb.
- Code checks that `stakes.source: none` agrees with the frame's own costs.
- "Already agreed" is judged against the typed goal, so a smaller ask than an agreement on record is already true,
  and a roll never shrinks an existing agreement.
- Settle the fallback-forces-a-roll question (0c15da2) under 01.4.4.
- Safe auto-commit stays only for Safe frames that remain costly.
- *Retires:* the verb- and case-specific carve-outs where one general test covers them; the 60% word-overlap
  `already_true`.

**T7. `/fix` works the way an investigating engineer does.**
- It sees everything the play roles see: one shared people card (role, licences, stance, bonds), facts in plain
  words, and that turn's model inputs and outputs.
- It can **dry-run** a correction: re-run gate, necessity and frame, or the turn, with the fix, and look at the
  result before applying it.
- It can rebuild an OFFER still on screen (`reframe`), and take back an unrolled pending turn.
- It checks what the player will see after the repair, and iterates within a bounded budget.
- It gets a short mechanics digest: holds; labels never penalties; refusals never facts; Stagger; a capability on the
  sheet outranks an Oracle fact.
- Code guards only the spine: no conjured coin; sealed stays sealed; mechanical changes need evidence.
- *Scored on fresh, real complaints*, including disputes at an open OFFER, by a scorer that checks the repaired
  screen.
- *Retires:* `rerender` (it can't change output); "explain only" for an open OFFER; scoring on the tuning set.

**D3 A. Willingness holds for the scene.**
- An NPC's willingness is decided when the conversation starts and holds for the scene.
- It changes only on an event: payment, threat, insult, or a won persuasion roll.
- A refusal always points to someone new who would know, never back to someone who already refused.
- Willingness never overrides clue rules (T2 / D2).
- *Retires:* per-topic willingness re-rolls.

**Patches:**
- P1: deliver the passage as written, keeping its paragraphs (`narration._text`).
- P2: OFFER wording:
  - no "+0" or generic "practised";
  - on a Safe frame, say what failing badly costs;
  - reach limited only with a cited factor;
  - retire the "a smaller part of it" template.
- P3: no willingness line on a plain greeting or thanks.
- P4: `_withheld`'s suffix only on refusals.
- P5: small text fixes (the "any posted notice" grammar, the notice separator, pronoun-check precision in tags,
  `READING` precision).
- P6: demote offline narration metrics.

**Process** (in the playtest-round skill):
- every spec writes and labels made-up and edge cases before implementing, and is accepted on them plus a held-out
  set;
- each round re-checks the "Revisit if" notes.

## 2. Order and lanes

1. **One rules wave, R2-K**, covering T1–T7, D2, D3 and the patches that touch rules.
2. **Engine specs, at most 2 in parallel:**

| Spec | Covers | Lane |
|---|---|---|
| **023** | T1 + T5 + T6 + P2 (adjudication) | `engine/resolve/` (gate, necessity, frame, pipeline, change), `turn.py`'s fiction questions, `oof.py`, Reader and Framer prompts as needed |
| **024** | T3 + T4 + P1, P4, P5, P6 (narration inputs and outcome) | `packet.py`, `narrator.py`, `narration.py`, `npc_layer.py` voicing lines, `answer.py` degree, `scene_state.py`, `incident.py` text, NPC template tables |
| **025** | T2 + D2 + D3 + P3 (content and talk) | `engine/gen/` (hooks, `case.py`), `answer.py` routing, `npc_layer.py` willingness, `world/social.py`, `director.py`, the testimony guards |
| **026** | T7 (the `/fix` redesign) | `fixer.py`, `dispute.py`, the fixer tools and prompt, `evals/feedback_corpus.py` |

023 and 024 run first. 025 and 026 follow: 026 after 023, since T1 removes most of what `/fix` had to repair.
