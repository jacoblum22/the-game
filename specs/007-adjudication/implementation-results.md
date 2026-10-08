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
