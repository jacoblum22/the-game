# Feature spec 023: one owner per question (T1), the goal flows through (T5), take the time (T6), OFFER wording (P2)

**Input**: `rules/_process/reports/R2-K-report.md`, "Engine checklist: Spec 023"; ROUND7-PLAN T1, T5, T6, P2 (all
owner-approved 2026-10-09; T1: "1 is good."; process: "every fix must also pass made up cases, including cases
specifically design to test edge cases"); ROUND7-ANALYSIS §2 T1/T5/T6 and §6; traces R7-I3 §1-2, §4-7, §9 and R7-H2 T6.
Rules cited: 01.15.1, 01.15.8, 01.3.1, 01.6.8, 12.6.1, T-12-4, PR-12-1 T4; 01.2.7, 01.3.5, 01.4.7, 01.9.3, 02.4.6,
15.3.10, 12.15.2; 01.4.1, 01.4.4, 01.7.4, 12.15.3; 01.6.10. Decisions: DL-01-41..47, DL-12-108, DL-12-121, DL-15-41.
Data: `resolution.yaml#take_the_time`, `#auto_commit.only_when_costly`, `#intended_change.before_framing`;
`pacing.yaml#dm_questions`.
**Owner direction** (constitution VIII): code owns the spine (dice, the roll test, the record), the model owns
judgment (what a goal is, whether an ask is covered by an agreement). Prefer deleting machinery.
**Parallel lane**: spec 024 (narration inputs, one outcome) owns `packet.py`, `narrator.py`, `narration.py`,
`npc_layer.py`, `answer.py`, `scene_state.py`. Anything needed there is a hand-off.

## User stories

### US1 - One owner per question (T1; 01.15.1, 01.15.8, 01.6.8, 12.6.1, T-12-4, PR-12-1 T4)
A fact question (the Reader's, from a FICTION_QUESTION or a fact a declaration leans on) goes to the yes/no Oracle
only when it is an open question about the world. Code drops a question whose subject is a beat's target, a person
present or the PC (their will is willingness, their ability is their record, their noticing is the roll) and a
question about unwritten content (what / where / how much / who): the narrator answers it in words as testimony. An
Oracle answer is stored positive and whole (no 60-character cut; "is not alert" is asked as "is alert" at the mirrored
odds) and its label is a plain sentence. An Oracle answer is never a snag: the Framer is not offered one, and
`frame_check` refuses one. Retires the pre-frame Oracle question about the target and `_KNOWS_Q`/`speech_owns`.

### US2 - The goal flows through (T5; 01.2.7, 01.3.1, 01.3.5, 01.4.7, 01.9.3, 02.4.6, 15.3.10, 12.15.2)
- Every rolled beat carries a typed goal: a beat still typed `none` gets its verb's plain goal (a look is `learn` on
  its target or the place, a Move `move_to`, a Talk `learn` or `persuade_to`, a Strike `harm`, a Sneak `hide`); a beat
  whose goal still cannot be typed is asked about, never framed as `none`.
- The Letters gate keys on the goal and its method: any `learn` (or look) whose method reads writing, whatever the
  verb. Asking someone else to read is their act, not the PC's.
- Certain talk (15.3.10) keys on the words (`speech`) and the goal (`persuade_to`/`learn`), not `verb.talk`.
- A secret frame needs a `learn` goal.
- 01.9.3 generalised: a price that reverses the typed goal against the same target (a closed door on the person a
  `persuade_to`/`learn` presses; a form that undoes a take, an open, a hold) is never offered as the success-at-a-cost
  price; a non-reversing price is offered instead.
- An accepted fallback is framed on its own scope (its method is the intent the Framer rates); its shift is added once.
- The OFFER title never comes from a description first.

### US3 - Take the time (T6; 01.4.1, 01.4.4, 01.7.4, 12.15.3; DL-01-44, DL-01-46 provisional, DL-01-47)
After framing, code computes COSTLY on the typed frame for every verb. Not costly: Safe stakes (source `none`, no
snag raised them), no threatened or alternate cost sourced to a fact (a time cost counts only with a clock
listening), no clock listening to time or exposure, no party who would act on a failure (01.4.1), no contest (no
opposed or defense obstacle), outside a conflict, not lethal, and a final DC below Very hard. Then: no OFFER, no roll,
success at Standard (a fallback at its reach cap), twice the mode's time through `advance_time`, evidence as a no-roll
success, and a RESULT that says how long it took (never "hidden check made"). A frame whose source is `none` but which
names a sourced cost is costly, and the disagreement is noted on the frame. "Already agreed" is the Framer's judgment
on the typed goal (`already_agreed`: an `agreed` fact of this person that covers the whole ask): no roll, the record
unchanged. A roll never replaces or shrinks an agreement on record. Retires the 60% word-overlap `already_true` and the
forced roll on every accepted fallback (0c15da2).

### US4 - OFFER wording (P2; 12.15.2, 01.6.10; DL-12-121)
No term worth 0; competence named by its tag (the PC's floor under the frame's deed tag), never "practised"; a Safe
frame says a plain failure loses nothing and states failing badly's cost and chance; Limited reach only with a cited
factor (the Framer's `reach_limit`), which the OFFER names. Retires "a smaller part of it (…)".

## Labelled cases (written and committed before implementation)
Seed cases from the R2-K checklist, then this spec's own. Each becomes a test in `tests/engine/test_spec023_cases.py`.

| # | Label | Case | Expected |
|---|---|---|---|
| C1 | made-up | Ask the blacksmith to mend a sword; the Reader also asks "can the smith work iron?" | no Oracle draw; no "can't work iron −2" snag possible |
| C2 | made-up | An old friend saved last week is asked for help; the Reader asks "is she willing to help?" | no Oracle draw (willingness answers) |
| C3 | made-up | "I sweet-talk the clerk and sneak a look at the ledger", PC without Letters, folded into one Talk beat or split | the reading meets the Letters gate (G3) either way |
| C4 | made-up | "I shoulder past the guard to reach the door", Reader left `change: none` | typed `move_to`; never framed as `none` |
| C5 | made-up | Searching your own empty room for a ring; practising on a dummy; reading your own book at leisure | no OFFER, no roll, time charged, take-the-time RESULT |
| C6 | edge | Framer: `stakes.source: none` but `closed_door` sourced to an NPC fact | costly: an OFFER; disagreement noted |
| C7 | edge | A take-the-time candidate at Very hard; a fallback whose +10 lands at Very hard | both roll |
| C8 | edge | Morga agreed to "hear the refugees"; "sit and listen" asked; then a larger ask with a limited success | first: no roll; second: both agreements stand |
| C9 | edge | The player's own "is there a rope in the loft?" | Oracle allowed; never a snag; a lever next beat |
| C10 | edge | Lock-pick near miss priced "the guard hears you" vs "the lock jams shut again" | the first is a success-at-cost price; the second is not offered as one |
| C11 | made-up | "I sweet-talk the clerk and peek at the ledger" (a look word, no "read") | gated (look + writing) |
| C12 | made-up | "I tell the guard a joke and slip past", Sneak typed `none` | typed `hide`; never rolled `none` |
| C13 | made-up | The player asks "Can the smith work iron?" with the smith present (FICTION_QUESTION) | no Oracle; the narrator answers from the record |
| C14 | made-up | "I ask Belie to read the list for me" (her act, `persuade_to`) by a PC without Letters | no Letters gate on the PC |
| C15 | edge | A smaller ask of someone who already agreed, Framer cites the agreement | no roll; the agreement fact unchanged |
| C16 | edge | Negated world question "is the gate not barred?" | asked and stored as "is barred" at mirrored odds; label plain, never "not not" |
| C17 | edge | An accepted fallback, alone, nothing at stake, Moderate +5 | takes the time at Limited, consequence kept; the Framer rated the fallback's own scope |
| C18 | edge (adversarial) | Framer marks a `persuade_to` frame `secret` | not secret |
| C19 | edge (adversarial) | Reader sends "how much does the job pay" to the Oracle | dropped (content) |
| C20 | edge (adversarial) | Framer cites an Oracle fact as a snag; another as a lever | snag refused; lever allowed |
| C21 | edge | A plain question to a Neutral NPC labelled `verb.help` with `speech` | certain (no roll) |
| C22 | edge | A Safe, sourceless frame in a conflict | rolls |
| C23 | edge | A Safe frame with an Unfriendly NPC watching | costly (a party would act): rolls |
| C24 | edge | Limited reach without a cited factor; with one | Standard; Limited and the OFFER names it |
| C25 | edge | OFFER with attribute 0 and the PC's floor competence | no "+0", no "practised" |
| C26 | edge | Take the time on a secret frame | no "hidden check made"; the time line |
| C27 | edge | Searching your room while a clock listens to time | rolls |
| C28 | edge | Safe frame whose only cost is `cost.time` cited to an unrelated place fact (explorer t12) | takes the time |
| C29 | edge | A Safe frame that stays costly (a contest) with auto-commit on | auto-commits as before (01.7.4) |

Real-save gates (round 7, `tests/fixtures/round7/`): Belie's reading (no Oracle fact against her Letters); the "not
not alert" label; fighter input 19 (the Letters gate fires on the folded read); explorer input 28 (no roll for sitting
to listen); the explorer's half-answered persuasion (already agreed, the agreement kept); talker input 28 (the near
miss never prices the goal's reversal); fighter inputs 24-25 (the fallback's scope and its shift counted once).

## Retired
- Pre-frame Oracle questions about the target or a person present; `_KNOWS_Q`, `speech_owns`; Oracle booleans for
  content; the 60-character slug cut (`turn.py:421`); the slug negation (`oof.py:234`); Oracle facts as snags.
- Verb-only keys: `reads_writing` on `verb.observe`, `certain_talk` on `verb.talk`, the Reader's `asks` on
  `verb.talk`, `secret` on any verb; rolled `change: none`; description-first titles.
- The 60% word-overlap `already_true`; the forced roll on every accepted fallback; the hold-only 01.9.3 guard (now
  one check for every kind); rolling every gated beat.
- "+0" terms, generic "practised", Limited by default (`reach_whole`/`reach_one_factor`), "a smaller part of it (…)".

## Assumptions (no clarify step)
1. "Sourced cost": a threatened or alternate cost citing a fact, except `cost.time`, which is costly only while a clock
   listens (taking the time already pays the time; explorer t12 cited an unrelated place fact for it).
2. "A clock listening": an active clock with a `cost.time` or `cost.exposure` tick source (the same test
   `structural_fit` uses).
3. The mode's time: travel 2 watches, downtime 2 days, otherwise 2 intervals.
4. Already agreed is judged by the Framer (it already sees the person's facts) and checked by code (the fact must be
   an `agreed` fact on the beat's person); code no longer matches words.
5. A new agreement is added to the one on record ("A; and B"), never replacing it (one `agreed` fact per person).
6. The PC's competence floor (`deed`, +1) is named by the frame's deed tag ("Blades +1"), else "experience +1".
7. The Framer's view gains the target's record (role and licences) through the beat message (`framer.py`), since
   `packet.py` is spec 024's lane.
