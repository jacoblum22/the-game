# Implementation results: spec 006 (narration contract + default NPC layer)

Branch `worktree-agent-a8fed8017034eb06e`, merged with `milestone-1-playable` (specs 007, 008-A, 009-A).
Outputs: `evals/baselines/replay_006.txt`, `live_narration_006_before.txt`, `live_narration_006.txt`,
`longhorizon_006.txt`.

## Gate table

| Gate | Baseline | Target | Replay, 80 recorded packets, Haiku (packet judge) | Live loop, 21 narrated turns, Haiku narrator + Checker (store judge) |
|---|---|---|---|---|
| First-draft pass rate | 1.3% (same 80: 0/80) | > 50% | **76/80 (95.0%)** | 2/21 (9.5%) before audit fixes → **7/21 (33.3%)** |
| Turns with cut sentences | 58% | < 15% | **0/80 (0%)** | 81.0% → **52.4%** (cut, rendered line or fallback) |
| Narrator calls per turn | 1.81 | ≤ 1.2 | **1.05** | 1.81 → **1.67** |
| Undeclared new elements per draft | 2.88 | (< 0.3 is spec 009's) | code-found 0.00; **Checker audit 3.11**; undeclared names code resolved 5.42 | audit claims on undeclared subjects 3.10 per turn |
| Full suite | 1177 | passes | **1619 passed**, 4 skipped | |
| Long horizon, offline scripted | 0.0 contradictions / 100 | no worse | **0.0**; engine errors 16, all "names exhausted" (known, spec 008; 7 before) | |

**The replay passes; the live loop does not.** The replay judges declarations against the packet (DL-12-42); it
has no store, so the Checker audit's verdicts cannot run there. In the live loop, 42 of 47 first-draft failures
came from the audit (Checker claims judged against the store): `contradicted` position/identity/existence,
`unsourced_change` position ("turns to you", "a step back"), `new_element` for the Checker's `clock`/`sealed`
labels on figurative prose ("it is only the beginning", "more than they seem"). 5 came from code scans (4
pronoun, 1 undelivered clue). Several were genuine narrator errors (an NPC's pronoun, describing absent people).
Spec 009's diff-mode Checker targets exactly this class. Live sample is small (21 turns).

Caveat: the replay plug's view-fact regex missed indented `fact.N` lines, so the 80-packet run offered the
narrator no fact ids to cite (fixed after the run; not re-run, to stay in the 80-packet budget). This made the
numeral scan stricter, not looser.

## Retired
`_carry`; `pure_cut`/`keep_prompt`; the past-budget "What do you do?" patch-in (the prompt is restored only when
repair cut it); `_mention_name`/`_GENERIC_PREDICATES`; `_FORBIDDEN_NEW` (tier lookup); `_DEEDS`;
`_atmosphere`/`_reacts_to_incident`/`GIVEN_NOTES`/`_restates_given` (cited record lines); `_settle` on incidental
claims; the addressed-NPC speech exception; activity cutting (activity lines); `settle_who` on the narration path;
the fallback's echo of the player's words; the World call as the default (it judges only recorded motives).
`_apply_writes` stays as the backstop (ledger I-175).

## Deferred
Diff-mode Checker and skipping it (009); crowd-practice responses (I-176); detail slots (009); `TODO(009-B)`
view hookups in world.py/checker.py; a prose A/B of the `fiction` fallback shape (built, tested offline, not run
on a model).

## speckit-analyze
Fixed before implementing: FR-012 vs research R6 wording; Principle I note on the incidental/consequential split;
a test for the fallback shape.
