# Spec 026 implementation results: `/fix` works the way an investigating engineer does (T7)

Branch `worktree-agent-a3f6f052f325d77c6`: cases 4aeb3f4 (committed before any code), fixture fix 8f2df8d and scorer
scope c3d26e7 (both before any Fixer model run), implementation 94e22cd, run 1 + the fixes it showed eb0f7a9, run 2,
then the merge of milestone-1-playable with spec 025 (54e9adf; only the recorded replay conflicted, regenerated).
Real numbers below; nothing faked.

## Headline: fresh held-out complaints, Sonnet as the Fixer, Haiku as the play roles
13 reports / 14 complaints, written and labelled before implementation (`tests/fixtures/feedback_corpus/fresh.json`),
scored on the screen the player sees after `/fix`.

| Run | auto (screen scorer) right / unclear / wrong | hand (I3's standard) right / unclear / wrong |
|---|---|---|
| **Run 1 (untuned, the headline)** `fixer_fresh_026_run1.json` | **13 / 0 / 1** | **12 / 2 / 0** |
| Run 2 (after the three fixes run 1 and round 7 showed) `fixer_fresh_026.json` | 11 / 0 / 3 | 12 / 1 / 1 |

Run 1 by case: f01 blind Tam at an open OFFER → refused by the gate (G4), no OFFER left; f02 garbled odds → fact
removed, re-framed 70%, no garble; f03 the clerk's Letters → fact removed, new OFFER without "can not read"; **f04
"the guard should know my rank" → unclear**: the re-framed OFFER now counts "rank: sergeant +2", but the Framer also
added a favour-sized request, so it is 65% again, and the answer said 55% (the dry run's Framer had answered
differently from the real one); f05 misread three turns back → turn 2 taken back, `Now: conditions none (was prone)`;
f06 fare twice → `Now: coin 8 (was 6)`; f07 the complaint is wrong → explained with Mira's words, nothing done; f08 two
complaints → both, refund and the slip; f09 narration only → acknowledged, nothing mechanical; f10 "50 more coin" →
refused plainly, coin unchanged; **f11 sealed → unclear**: the name never shown, but the answer said "the record holds
no leader at all" (it cannot see the sealed one); f12 a roll with nothing to win → no roll, Morga agrees; f13 "Cant is
on my sheet" → the same 5% OFFER, Letters explained.
Run 2: f04 still unclear (the same Framer offset); f09 auto-wrong but hand-right (the Fixer also found and refunded the
fare charged twice, which is true); **f12 wrong**: the re-frame's Framer (Haiku) framed the 75% OFFER again and the
answer claimed "without a roll". Both runs are reported; the headline is run 1, the only untuned one.

## Also reported
| Set | Before | After (run 1) | After (run 2) |
|---|---|---|---|
| Round-7 live disputes (3) | live: 1 right / 0 / 2 wrong | auto 3/0/0; hand **2/0/1** (dsp.2: re-framed Belie into a refusal *on* the Oracle "can not read") | auto 3/0/0; hand **3/0/0** (dsp.1: no −2, no garble, 75%; dsp.2: the fact removed, Belie's OFFER at 45% without "can not read"; pronouns: the "they" lines named the slip) |
| Round-6 disputes (15) | live: 1/6/8; spec 022 (tuned on them, outcome-class scorer): auto 9/6/0, hand 10/3/2 | auto 10/5/0 (hand: the 5 unclear are label kinds, not answers; 233000-d3 explained a blow a refused turn should not have cost: unclear) | auto 12/2/1 (232941-d2 auto-wrong: the friend bond explained as standing, not called a slip: hand unclear) |
| Live `/fix` (fighter, Haiku, 15 turns) | — | 1 report, **right**: "Ostdun says I'll have seen Belkin… never mentioned": investigated (turn, search, entity), answered "Ostdun's words were a slip", `Now:`; the player: "The /fix was acknowledged cleanly." | — |

Live run: `evals/playtests/20261009-220414-claude-fighter.md`, 33 inputs, exit 0; model calls: fixer 3 on **sonnet**
(look, decide, check the screen), every play role on **haiku**. It ran on the run-1 code.

## Gates
| Gate | Result |
|---|---|
| Full suite (after the merge with 025) | **1908 passed, 4 skipped, 0 failed** (baseline before work: 1856) |
| Replay | re-recorded after the packet change and again after the merge; 3 replay tests pass |
| Recorded Sonnet runs replay through code (`test_feedback_corpus.py`) | 23 reports (13 fresh, 3 round-7, 7 round-6) reproduce the same screen and score |
| ruff (touched files) | clean |
| pyright (touched files) | 0 new; `turn.py:579` (pre-existing, noted by 023) and the uvx env's missing pydantic |
| `validate_ruleset.py` | 0 ERROR / 0 WARN |
| `longhorizon.py --mode scripted` | 0 engine errors |

## What was built
- **One people card** (`packet.people_card`): name as known, pronouns, people, role (the PC: livelihood, upbringing),
  licences by name and grade ("Letters (reads and writes)", "Scribing (trained)", "speaks the Common tongue"),
  competences, stance, standing toward the PC, the PC's bond, station facts (rank, title, office) and memberships. The
  Reader, Framer (the target) and Narrator views print it in place of the raw data dump; the Fixer's `entity` tool and
  opening print the same card plus refusals marked hidden. Spec 023's `target's record` line is deleted.
  `speaker_card` (spec 025's) is untouched; its hook terms and "others have said" block stay as 025 left them.
- **What the Fixer sees**: plain-word facts in every tool (the Chance line's sentence, never a slug), the effective
  degree in turn listings (024 hand-off), the OFFER on screen marked OPEN NOW with its cited facts, `calls` (each play
  role's THIS MESSAGE, its view on request, its answer), `search` over the facts on record too.
- **Dry run and check**: `try` (proposals on a SQLite-backup copy, validation included, the screen returned), `replay`
  (a turn taken back on a copy and its words run through T1-T6 again). After deciding, the decision is always run on a
  copy and the Fixer is shown "THE SCREEN THE PLAYER WILL SEE AFTER YOUR REPAIR"; it keeps or revises (at most 2). The
  real application reuses that dry run's play-role answers, so what was checked is what is applied.
- **Re-frame and take back**: `reframe` withdraws the OFFER on screen (nothing spent), applies the other corrections
  first, and runs gate, necessity and frame again with the declaration moved to now (`fact_id`: a fact that makes the
  goal impossible → G4; never an Oracle answer). The result (new OFFER, refusal, or a no-roll result narrated from the
  declaration's words) is on the same screen. A take-back of the turn whose OFFER is open needs no evidence and closes
  that OFFER (before, a take-back reverted the writes and left the OFFER showing: `pause_opened` is not revertible).
- **Spine guards only**: unchanged INV-9 evidence, quantity bounds, sealed/clue trail, identity fields, take-back
  limit, never the report's words; plus "an Oracle answer never rules a goal out".
- **Scoring**: `feedback_corpus.py` runs each report through `play_dispute` (the whole turn loop) and scores the screen
  (`must`, `must_not` after the answer, `must_not_anywhere`), the class and the corrections; every model answer is
  taped so runs replay exactly. `evals/fix_scenarios.py` builds the four made-up saves.

## Retired
`rerender` and `_rerender` (→ `reframe`); explain-only at an open OFFER (→ re-frame or take back; prompt and 12.3.6
item 4); the entity tool's sheet as the person (→ the people card); raw predicate slugs in tools (→ plain facts);
023's `target's record` (→ the card); the fair-chance bar on taking back an unrolled turn; outcome-class scoring on
the tuning set (→ screen labels on held-out sets); `pacing.yaml#feedback.investigate.proposals: rerender_display`.

## Out-of-lane edits (one line each)
- `engine/dm/turn.py::_dispute`: a re-frame's beat outcomes join the dispute turn's record (where it is built).
- `engine/dm/roles/framer.py`, `prompts/framer.md`: `target_record` deleted; one prompt line points at the card.
- `rules/data/pacing.yaml`: the `feedback.investigate` keys this spec implements.
- Tests of 023/024 that read `target_record` or `role:` now read the card.

## Process notes (honest)
- Cases committed first (4aeb3f4). Two fixture/scorer corrections followed before any Fixer model run: the eel-market
  save (fixed dice broke the RNG log on load; the theft showed an OFFER the screen never showed) and the `must_not`
  scope (the answer restates the complaint). Labels' intent unchanged.
- One label miss found by hand: round-7 dsp.2 run 1 passed the screen regex ("can ?not read") while the REDIRECT
  said "can read … is False"; graded wrong by hand. The fix it showed (Oracle never a G4 reason) is in run 2.
- Run 2 is tuned on run 1's and round 7's findings; it is reported, not the headline.

## Anti-pattern check (handoff §3.3)
Code authoring narrative truth: a correction still writes typed values only; a re-framed refusal is the gate's, never
an Oracle answer. Atomisation: one snapshot, one answer, as before. Over-triggering: none added. Low-precision blocking:
the one new guard (Oracle fact as a G4 reason) is exact by source; the `knows_` clue-trail guard refused a harmless
"knows the rank" fact in run 2 (precision gap, noted below). Blind calls: removed (the Fixer reads the same card and the
roles' own inputs). Wrong context: plain words, not slugs. Mechanics as text: the take-back now closes its OFFER. Test
traps: held-out cases labelled first; the headline is the untuned run; the scorer checks the screen.

## Hand-offs
- **Gate (resolve)**: a G4 from a fact renders "Tam Harlan's detail eyes is milk-white…, as already settled" and "can
  read the writing… is False": the refusal words are a slug sentence (`gate.py` G4 reason + `_refused`).
- **Framer**: a cited rank lever (+2) was offset by a favour-sized request (R2) the Framer added, so "the guard should
  know my rank" re-framed to the same 65%; and on f12 Haiku re-framed "nothing at stake" as a 75% persuade. Whether a
  superior's order to a subordinate is a request at all is the Framer's call.
- **dispute guard**: `CASE_PREDICATES` includes `knows_`, which also blocks harmless knowledge facts ("Pell knows your
  rank"); narrow it to the case graph's own predicates.
- **025**: none needed; `speaker_card` was not replaced.

## Owner decision
Should `/fix` be able to rule "this needs no roll" itself? Today it can only re-frame; the Framer then decides the
stakes again, and twice (f04, f12 run 2) it framed the same odds the player disputed.
- (A) Keep it: the Fixer corrects facts and re-frames; the Framer owns stakes and odds. Simple; occasional repeats.
- (B) Add a `no_roll` correction: the Fixer may record an agreement or "nothing at stake" with evidence, and the
  re-frame then takes the time (01.4.4) without asking the Framer.
- (C) Let the Fixer pass a one-line note to the re-frame's Framer ("the target is his subordinate; his rank stands").

**Recommendation: C**: it keeps the Framer as the owner of odds (VIII.1), costs one line, and gives the re-frame the
context it lacked in both misses.
