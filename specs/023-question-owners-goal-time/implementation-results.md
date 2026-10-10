# Spec 023 implementation results

Branch `worktree-agent-ae83fd342f600918a`: cases 8619d6e (committed before code), implementation c5d62f6, then the
merge of milestone-1-playable (spec 024; only the recorded replay conflicted, regenerated).

## Gates (real numbers)
| Gate | Result |
|---|---|
| Full suite (after merge) | 1856 passed, 4 skipped, 0 failed (baseline before work: 1804 passed, 4 skipped) |
| Replay | re-recorded (`offline_seed11`); 3 replay tests pass |
| ruff | 0 on touched files (4 pre-existing E741 in `evals/orchestration/resolve_rules_merge.py`, untouched) |
| pyright (touched files) | 0 errors (`turn.py:578` `cost_terms` error is pre-existing, unchanged) |
| Validator | 0 ERROR / 0 WARN (no rule text changed) |
| `longhorizon --mode scripted` | 0 engine errors |
| Labelled cases C1-C29 (+1 found live) | all pass (`tests/engine/test_spec023_cases.py`, 31 tests) |
| Real-save gates (round 7) | 7/7 pass (`tests/engine/test_spec023_saves.py`) |

Real-save gates: Belie's reading (no draw, nothing written, the Framer sees her Letters); "not not alert" (reads
"Magby is alert to a hand…"); fighter input 19 (the folded read meets Letters: G3); explorer input 28 (no OFFER, no
roll, time spent, take-the-time RESULT); explorer turn 10 (already agreed: no roll, fact.106 stands; the turn-4
willingness draw is never asked); talker input 28 (the close call never offers the closed door "he turns the round
down"); fighter inputs 24-25 (the Framer sees only the fallback's scope; recorded `hard` → DC 25, still rolls;
`moderate` → takes the time at Limited).

Case results: C1 ✓ C2 ✓ C3/C11 ✓ C4 ✓ C5 ×3 ✓ C6 ✓ C7 ✓ C8/C15 ✓ C9/C20 ✓ C10 ✓ (and the closed-door variant) C12 ✓
C13 ✓ C14 ✓ C16 ✓ C17 ✓ C18 ✓ C19 ✓ C21 ✓ C22 ✓ C23 ✓ (amended, below) C24 ✓ C25 ✓ C26 ✓ C27 ✓ C28 ✓ C29 ✓.
**C23 amended during implementation:** "an Unfriendly NPC watching → costly" first came from code's
`parties_who_would_act`; it contradicted the explorer t12 gate (an Unfriendly bystander, not the Framer's stakes
source). 01.6.9 makes the onlooker the Framer's judgment, so C23 now expects costly when the Framer names the
watcher, and take the time when it does not.

## Reader (Haiku, `evals/reader_live.py`; caches in `evals/baselines/spec023_{before,after}_*`)
| Set | verb | gate | change_kind | goals | question_kind |
|---|---|---|---|---|---|
| golden before → after | 82.4 → 85.7 | 92.3 → 94.5 | 87.1 → 93.8 | 82.4 → 87.9 | 84.6 → 84.6 |
| held-out | 86.5 → 89.2 | 86.5 → 91.9 | 100 → 94.7 | 86.5 → 89.2 | 91.9 → 94.6 |
| goal-shape | 88.6 → 85.7 | 97.1 → 97.1 | 93.3 → 93.3 | 97.1 → 97.1 | 85.7 → 80.0 |
| goal-shape held-out (after only; no cached before) | 92.9 | 100 | 75.0 | 85.7 | 100 |

What the change targets, counted on the same answers: fact questions 90 → 5; questions about a person's will,
ability, noticing or knowledge 30 → 0; content (wh-) questions 4 → 0; beats left `none` 10 → 2. An interim prompt
(run once, then trimmed to its word budget and re-run; numbers discarded) scored golden goals 81.3. Some golden
labels encode the old policy ("look around" = `none`), so part of the gain is the new policy agreeing with itself.
Side effect: legitimate embedded world facts are rarely asked now (before: "stacked barrels to hide behind", "the
wall has handholds"); the narrator states such incidental detail as narrated (constitution VIII).

## Live (explorer, Haiku engine, Sonnet player, 15 turns; `evals/playtests/20261009-204702-claude-explorer.md`)
- Rolls with nothing at stake: 0. One roll in the run (turn 9, edging to the crowd): Safe but costly (exposure cited
  to a crowd fact), auto-committed as 01.7.4 allows.
- Oracle facts about a target: 0 (no Oracle draws at all; the Reader sent no fact questions in 13 calls).
- Contradictory records: 0 (one `agreed` fact, Mago pours the ale).
- Garbled labels: 0 (`Chance: likely — 75% (Agility +3, Guile +1)`; no "+0", "practised", "not not").
- Found and fixed: the OFFER title "Go to the Golden Plough" while inside it (the Reader typed `move_to` the place
  here with the spot as description); `goal_line` now names the spot (test added).
- Not in this lane: no narration after the critical success (player [25]); the journal's "furniture 0" label.

## Retired
`_KNOWS_Q`, `speech_owns`, the `[:60]` slug cut, `fact_short`'s second negation, Oracle facts as snags, Oracle draws
about targets/people here/content; verb-only keys (`reads_writing` on Observe, `certain_talk` and the Reader's
`asks` on Talk, `secret` on any verb); rolled `change: none`; description-first titles; the hold-only 01.9.3 guard
(one check for every kind); the 60% word-overlap `already_true`; 0c15da2's forced fallback roll (DL-01-46,
provisional); rolling Safe sourceless frames; "+0", generic "practised", `reach_whole`/`reach_one_factor` (Limited
by default) and "a smaller part of it (…)".

## Hand-offs
- Rules: WE-01-2 branch B still draws the Oracle on the guard's own sister and cites it as a −2 snag, against
  01.15.1/01.15.8 (the test now asserts the refusal). `resolution.yaml#reach_flags.whole.tie_break: false` disagrees
  with 01.6.10's new Standard tie-break; the engine no longer reads `reach_flags`.
- Spec 024/026: the Framer's packet view carries no NPC licences (`packet.py`, `licenses: {}`); this spec adds a
  `target's record` line to the Framer's message instead. A shared people card (spec 026) should replace it.
- Narration: no narration after a critical-success RESULT (live [25]); codex "furniture 0" label.
- Golden set: relabel "look around" lines from `none` to `learn` (R2-K policy).

## Anti-pattern check (handoff §3.3)
Code authoring narrative truth: reduced (no d100 facts about people; no "a smaller part"). Over-triggering: Safe
sourceless frames no longer roll; Oracle answers never snags. Blind calls: the Framer sees the target's licences and
the fallback's own scope. Low-precision blocking: the 01.9.3 word lists only re-route the close-call price.
Mechanics as text: agreements are added, never overwritten. Test traps: cases committed before code; goal-shape
held-out run once, untuned.
