# Implementation results: spec 019 (holistic narration: F1, plus F4's narration side)

Scope: `rules/_process/reports/R2-J-report.md`, "Spec 019"; DL-12-101, DL-01-39, DL-12-103; rules 12.3.1, 12.3.1a,
12.3.1b, 12.3.3, PR-12-2, 12.2.7, 12.14.12, 01.2.7 item 3. Spec-kit lean: [spec.md](spec.md), [plan.md](plan.md),
[tasks.md](tasks.md) (with the analyze table; no clarify, assumptions A1-A7 in spec.md). Engine API:
`engine/CONVENTIONS.md`, last section. Branch base: `milestone-1-playable` f9d5221.

## What was built
- **One passage + side list** (`schemas.narrator_schema`): `{passage, speech[{speaker, words, form}], new[], covers[]}`.
  Code splits the passage (quote-aware) only to place a failure or a cut (`declare.sentences_of`).
- **Checks over the whole passage**: the code scans, speech checks, tiers and precision checks per sentence of the
  split; coverage from `covers`; the **quote-mark check** (`declare.unquoted`: a direct speech outside quotes, a
  first-person sentence in the narrator's voice).
- **At most one revision** (`claim_check.max_revisions`), the same packet plus "A REVISION", the whole draft and each
  failure in words (handles only for uncovered lines; rendered lines never sent). A cut alone needs no revision.
  After it: cut what fails, **code quotes** what is still unquoted, rendered lines for uncovered must-name items
  (last resort), the fallback when nothing survives.
- **`said` = whole speeches**: one record per side-list speech found in the delivered text.
- **F4 narration side**: `handles.AGREED`: "Agreed by X: <goal>" reaches the narrator as "X agrees to what was
  asked" (rendered "X agrees."); the full line stays in RESULT. A refused change is citable, not must-name. No record
  line says "say it plainly" or "it is done". Narrator prompt: "write around it" (names, kinship) removed; added "one
  speech per quote run", "spoken words inside quote marks", "never restate the player's words".
- **Checker audit** (sampled, logs only): numbered sentences of the delivered passage, side list in words, last
  exchange only; `unexpressed` is passage-level.
- **`pc_agency`** compares quoted PC words with the player's message plus parts a pause carried (I1 §2 patch).

## Retired, and what supersedes each
| Retired | Superseded by |
|---|---|
| Sentence array; per-sentence `refs`, `about`, `atmosphere`, `speaker`; the "fiction" fallback shape | The passage and side list (`covers`, `speech`, `new`); `about` found by the name scan |
| Per-sentence judging and narrow repair (`MAX_REDRAFTS`, `_max_redrafts`, `Repair`, `repair_text`, add/replace) | One revision that sees the whole draft (`Revision`, `revision_text`) |
| Coverage "add" repair calls | Side-list coverage; an uncovered line goes to the revision, then its rendered line |
| `screen._acknowledged`, `narration._unanswered` ("every part answered") | Nothing: the narrator reads the whole message (12.2.7 item 1); the Checker flag remains |
| `checker.declaration_words` | `checker.side_list_words` |
| Record lines "say it plainly; it is done" / "say why plainly"; the goal-as-agreement line | State lines ("now so", "X agrees to what was asked"); RESULT keeps the words |
| Outcome words as a blocking per-sentence check | `outcome_words` precision check, logs (measured 0.1) |
| Data `claim_check.max_redrafts`, `sentence_declaration` | `max_revisions`, `passage_side_list` (already in data) |

## Measurements (precision, VIII.2)
| Check | Corpus | Result | Now |
|---|---|---|---|
| First-person in the narrator's voice | 5802 delivered sentences, rounds 2-6 | 9/9 real ("a mine" noun excluded after 2 false) | blocks (revision, then code quotes) |
| Outcome words over a whole passage | same | 1/10 real ("a finger's width from" read as a miss) | `precision: 0.1`, logs |
| `season_words` | 3235 first-draft sentences | 1/2 real | `precision: 0.5`, logs |
| Pronoun check on speech | same | 0/5 real (speaker speaks of an absent man) | stays off in speech |
Files: `measure_checks.txt`, `evals/baselines/precision_audit.txt`.

## Gate table
| Gate | Result |
|---|---|
| Full suite | **1786 passed, 4 skipped** (was 1779 + 7 new) |
| ruff (touched files) | clean (repo-wide: 4 pre-existing errors in `evals/orchestration/resolve_rules_merge.py`, untouched) |
| pyright (touched files, py3.12) | 0 errors |
| Rules validator | 0 ERROR / 0 WARN |
| Replay re-recorded | `tests/replay/games/offline_seed11.json` |
| Offline long-horizon, scripted 300 lines | **0 engine errors**; first draft 64.3% (base 64.3%), cut/render 35.7% (base 35.7%: the offline narrator never words "agrees"/lead/position lines), narrator calls/turn **1.36 (base 1.71)**, novelty-4 0.64 (0.65) |
| Real-save tests (talker 232941 turns 2, 13, 14, 16) | turns 2/13/14's first drafts need no revision (their repairs came from the retired check); turn 16's three unquoted speeches found and quoted; turn 14's change line now "agrees to what was asked" |
| Live talker, Haiku, 15 inputs (persona on Sonnet, the harness default) | see below |
| Live long-horizon `--lines 12 --model claude-narration` | 14 narrated, 0 engine errors |

## Live results against the round-6 baselines (I1; talker 232941)
| Measure | Round 6 talker 232941 | Round 6, all 10 saves | Live talker 20261009-142708 | Live long-horizon (12 lines) |
|---|---|---|---|---|
| Narrated turns | 14 | 106 | 13 | 14 |
| Stacked quotes (`"…" "…"`) | 21 in 10 turns | 57 in 34 | **0** | 0 |
| Echoed player lines | 6 | 29 | **0** | 0 |
| Duplicated answers | 2 in 2 turns | 20 in 12 | **0** | 0 |
| First draft delivered | 64% | 82% | **100%** | 100% |
| Revision rate | 36% | 17% | **0%** | 0% |
| Narrator calls per narrated turn | 1.57 | 1.24 | **1.00** | 1.00 |
| Cut or fallback turns | 7% | 2% | **0%** | 0% |
27 live narrated turns (budget 35). Metrics by `metrics.py` (same definitions both sides; the stacked count
reproduces I1's 57/34). Caveat: n is small (±10 points), and with no failure live, **the revision path ran only
offline** (tests and the offline long-horizon).

## Anti-pattern check (handoff §3.3)
- *Code authoring narrative truth*: removed the "it is done" record lines and the goal-as-agreement line; rendered
  lines are only a last resort and never shown to the model. Code quoting unquoted words changes punctuation, not
  content.
- *Atomisation*: the model writes one passage; code's sentence split is bookkeeping for cuts (A1). Speech is stored
  whole.
- *Low-precision checks that block*: season and outcome words measured and demoted; the pronoun check kept out of
  speech; the only new blocking check measured 9/9.
- *Blind model calls*: the revision sees the whole draft and packet.

## Hand-off notes
- **020**: `prompts/narrator.md` still says "The packet holds CORE RULES and RULE CARDS"; edit it when the core goes.
  With "write around it" gone, the narrator needs 020's identity lines (pronouns, `bond.`) for everyone named.
  Live: the OFFER printed Framer internals ("the height citation (fact.73) is unverified", "Moving to: the ford" for a
  ladder; player /fix at input 19).
- **021**: live input 28-31: the pay figure was never stated. Trace: the record had an Oracle yes/no ("the finished
  pay line states a sum in coin: yes") instead of a value, and the speaker card's "knows:" carried a `/fix` complaint
  ("correction 1 ... never gives the sum") and an `agreed` fact holding the player's goal (I1 §5d). `change.py` still
  stores `agreed` with the goal text. Also Mara's flat refusals (inputs 18, 22-23).
- **Merge**: regenerate the replay; `pacing.yaml` changed only under `claim_check`.

## Owner decision (default taken)
Outcome words against the beat's result were a blocking scan; measured over whole passages they are 1 in 10 right.
Options: (a) log only, re-measure each round (taken; VIII.2); (b) block only for one rolled beat and a sentence about
"you", after re-measuring; (c) drop the scan. Recommendation: (a).

## Files outside the lane (one line each)
- `engine/llm/offline.py`: the offline narrator answers the new schema, and writes second person (its "I ..." restatements would trip the first-person check).
- `evals/precision_audit.py`, `evals/baselines/precision_audit.txt`: the measuring tool for the checklist's precision items.
- `evals/longhorizon.py`: counts revision calls as narrator calls.
- `engine/CONVENTIONS.md`: a spec-019 section so the conventions do not describe the retired API.
- Existing tests of the retired shapes (moved to the passage); `tests/fixtures/round6_narration.json`; `tests/replay/games/offline_seed11.json` (regenerated).
