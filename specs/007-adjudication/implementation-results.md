# Implementation results: Adjudication (spec 007)

Branch `worktree-agent-a17c5ae17c441856e`, from `milestone-1-playable` 91fc837. Rules: the R2-C wave
(`rules/_process/reports/R2-C-report.md`). Commands are in [quickstart.md](quickstart.md); outputs are in
`evals/baselines/`.

## Gate table

| Gate | Target | Result | Status |
|---|---|---|---|
| Full suite (`pytest -q -p no:cacheprovider`) | passes | 1,557 passed, 4 skipped | PASS |
| ruff / pyright on touched files | clean | clean (pre-existing I001 in `claims.py`, `world_step.py`: not touched) | PASS |
| `check_gate` table: verb × facet × licence | every cell | 15 verbs × 8 facet sets × 3 holdings = 360 cases, plus 17 named gate cases | PASS |
| OFFER snapshots | ~20 frames | 20 canonical frames (`tests/engine/snapshots/offer_blocks.txt`) | PASS |
| No `S\d`, `DC`, `verb.`, `anchor`, `Mode:` in an OFFER | 0 | 0 over the 20 snapshots | PASS |
| Reader golden set, verb (Haiku, final run 4) | ≥ 95% | **85.7%** (78/91); baseline 72.1% | **MISS** |
| Reader golden set, computed gate (Haiku, final run 4) | ≥ 98% | **93.4%** (85/91); baseline 63.9% | **MISS** |
| Computed gate where the Reader's beat and verb match the label | — | 100.0% (61/61) | the gate itself makes no error |
| Negation pairs (22 lines): verb / gate | — | 95.5% / 100.0% | |
| Facets: against_will / uses_power / speech; question_kind | — | 93.2% / 100.0% / 87.7%; 82.4% | |
| Odds audit: non-Dire unopposed OFFERs with CF > S not labelled long shot | 0 | **0** of 483 frames (66 harsh frames, all labelled long shot; the guard converted a snag on 114) | PASS |
| Odds audit: frames with ≥ 3 distinct odds across the approach and its alternatives | report | 3.5% overall; Wren (uneven attributes) 10.6%; attacks on a person 24.4% | reported |
| Prompt word budgets | never grow | Reader 694 → 693, Framer 689 → 684 | PASS |

### Reader runs (each 91 Claude CLI calls on Haiku, owner's subscription; no API spend)

| Run | Change | verb | gate | answers |
|---|---|---|---|---|
| 1 | new schema and prompt | 75.8% | 90.1% | `reader_golden_haiku_run1.*` |
| 2 | prompt: SPEECH vs Talk, verb rows, facet negatives; the code pre-router in the plug | 82.4% | 90.1% | `_run2.*` |
| 3 | prompt: beat segmentation | 87.9% | 94.5% | `_run3.*` |
| 3, rescored | code: a lone conditional beat runs now; a Talk read as against-will is a Grapple | 91.2% | 96.7% | (same answers) |
| **4 (final)** | none (fresh sample of the final prompt and code) | **85.7%** | **93.4%** | `reader_golden_haiku.*` |

Run 3 rescored was tuned on the answers it is scored on; run 4 is the honest number. Run-to-run spread on the same
prompt is about ±3 points (one sample per line).

**Dominant error.** Beat segmentation, not the gate: which act is the scored "first beat" when a move or gesture
goes with words (g002, g004, g010, g031, g037: the label takes the Talk, the Reader the step), and SPEECH vs a Talk
beat for plain questions (g033, g041, g048, g061). 13 of the 19 verb/gate misses are these; every gate miss follows
a verb or beat-presence miss. The golden labels themselves disagree on this point in places (g002 vs g027), so a
two-stage Reader or a label review is the next step, not more prompt words. The Talk-as-Grapple rule fixed two
lines in run 3 and cost two in run 4 (g049 is a shove, g055 a held grip plus words).

## What was built

- Reader (12.2.2, DL-12-50): verb, target, `against_will` / `uses_power` / `speech`, shape (`now`, `extended`,
  `queued`, `conditional`), `question_kind` + `topic` on parts. "What do I know?" is routed by code before the call.
- `engine/resolve/gate.py`: `compute_gate` (pure) and `check_gate` (conditions, cited G4 fact, fallbacks).
- `engine/resolve/necessity.py`: certain talk and plain reading skip the Framer; trivial class does not roll;
  `parties_who_would_act`.
- Framer and `frame_check`: obstacle class + one cited nudge (never across the trivial line, never the same fact as
  a snag), social and attack beats on a person use the defense with 15.3.3's standing and request terms, one
  Precision snag, the 01.6.13 guard and long shot, alternatives, costs narrowed by `stakes_cost_menus`.
- Auto-commit: on by default, Safe frames only (never Risky, Dire, lethal, secret, long shot or mode-priced).
- OFFER: 12.15.2's template from `Frame` fields, chance as number + word, glossary behind `?`; one menu line for
  every play pause (`[Enter] …`, letters, `[?] Explain`); Enter on a Dire, lethal or long-shot OFFER and on other
  waiting pauses shows the pause again; Enter never backs off.

## Retired

`gate.py` "G1 before G3" and "G2 before G3" passes and `_plain_form_of`; `reader_check`'s G2 rule; the Reader's
`gate`, `license`, `would_be_license`, `necessity` fields and prompt lines (gate, would-be licence, gentle touch,
necessity); `_plain_reading`; `_knowledge_parts` as a post-pass (now a pre-router); costs.py's "observer is a
judgement call" ponytail; the Framer's tier and snag tie-break lines and the Moderate default;
`plain_offer_words`, `_fix_pronouns`, `_fact_words`, `_difficulty_phrase`, `TRADE_LABELS`, `offer_text`.

## Deferred and deviations

- The answer ladder that consumes `question_kind` / `topic` is spec 008.
- Lever and snag facts are named generically in the OFFER ("a hindrance −2"): a typed fact label is a later change.
- `extended` kept as a fourth Reader shape (progress clocks, P-082); 12.2.2 lists three (ledger I-160 b).
- G4 by zero reach has no proposer any more (I-160 a); 15.3.10's hesitation test is not read by code (I-160 c).
- The open sim finding: `frame_check` refuses a nudge and a snag that cite the same fact (within 01.6.5), which
  does not lower the measured 35-point bound for two different wrong facts. The rule change that would (one
  model-chosen modifier per beat) is ledger row I-159, not made.
- `engine/build/cards.json` rebuilt (stale after the R2-C rules; the build test failed at baseline).
- Replay `tests/replay/games/offline_seed11.json` re-recorded twice (Reader and Framer packets changed on purpose).

## Ledger rows added

I-159 (the double-error bound, owner decision), I-160 (computed-gate gaps a–d). Renumber at merge if spec 006
took the same ids.

## Follow-up: Reader beat normalisation (2026-10-08)

Scored against the policy-consistent labels (`evals/reader_golden_POLICY.md`). Every number is one fresh Haiku run
(Claude CLI, owner's subscription), one sample per line; spread between runs of the same prompt is about ±3 points.

**Held-out set first.** `evals/reader_heldout.jsonl` (37 lines: gestures with words, moves with a destination,
casual and deliberate looks, plain questions to wary and friendly NPCs, 5 negation pairs) was labelled by the policy
and committed (f071f69) before any code change. `py -3.12 evals/reader_live.py --set heldout`.

**Change.** Code decides what the model marks (DL-12-50):
- schema: each beat gets `purpose` (`own_change` | `serves_another_act` | `free_activity`) and `pressure`
  (`none` | `request` | `threat` | `offer` | `plea` | `insistence`);
- `reader.normalise` on the raw answer (engine and harness): a bodily act serving another act folds into it
  (01.2.1, 01.2.2; B4), a Move closing on the next against-will beat is its reach, 00.12.6's free acts drop (a look
  only with a casual word, A4), a Talk beat with pressure `none` in a message that asks is SPEECH (15.3.10; C1).
  A beat against someone's will or using a power always stays (B5). Talk, Observe, Recall, Sneak never serve;
- prompt: the two fields, Grapple covers snatching a held item, Handle no longer "taking a thing gently"; 693 →
  692 words.

| Set | Run | verb | gate | facets aw / power / speech | question_kind | pairs verb / gate |
|---|---|---|---|---|---|---|
| golden (91) | run 4, before (`_run4`) | 83.5% | 91.2% | 92.5 / 100 / 95.5% | 85.7% | 95.5 / 100% |
| golden | run 5, first fix (`_run5`) | 73.6% | 85.7% | 89.7 / 100 / 91.4% | 89.0% | 81.8 / 86.4% |
| golden | **run 6, final** (`reader_golden_haiku.*`) | **92.3%** (84) | **97.8%** (89) | 93.9 / 100 / 97.0% | 87.9% | 90.9 / 100% |
| held-out (37) | before (`_before`) | 86.5% | 86.5% | 100 / 100 / 100% | 81.1% | 90.0 / 90.0% |
| held-out | first fix (`_run1`) | 94.6% | 94.6% | 100 / 100 / 100% | 89.2% | 90.0 / 90.0% |
| held-out | **final** (`reader_heldout_haiku.*`) | **91.9%** (34) | **91.9%** (34) | 100 / 100 / 100% | 86.5% | 100 / 100% |

Run 5 showed Haiku marking deliberate looks and pressing Talk beats as free or serving (g001, g016, g035, g011,
g013, g043); the code guards (only 00.12.6's acts are free, only bodily acts serve, the reach rule) and two prompt
words were written from the golden misses. They also fix one held-out miss seen in the first held-out run (h034, a
close watch marked free), so the held-out set was re-run fresh after the change. Nothing was changed after the
final held-out run.

**Targets missed** (95% verb, 98% gate). Golden misses: beat order on menace lines (g003, g004: the step or the
threat read first), the gentle face turn (g010) and the turn to the woman (g037) folded where the label wants Talk
and Observe, and verb picks unrelated to segmentation (g058, g071 knock as Strike, g080 Handle vs Sneak). Held-out
misses are all casual looks the model marks `own_change` (h015 "glance", h016 "without making a show of it", h019
"take in the room"): the code drops a look only when the model marks it free. Next step (not done, it would be
tuned on held-out): let the player's casual words decide A4 in code whatever the mark, then label a fresh held-out
set. `test_build.py::test_committed_cards_are_current` fails in this worktree only (core.autocrlf checks out
`rules/data/anchors.yaml` with CRLF, so the tree hash differs); no rules file was touched.
