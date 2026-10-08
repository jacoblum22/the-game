# Tasks: Measurement harness

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md), [data-model.md](data-model.md),
[contracts/cli.md](contracts/cli.md). Tests are requested (spec FR-014, SC-004): fast ones in the default suite,
the full long-horizon run marked `slow`.

## Phase 1: Setup
- [X] T001 Create `evals/corpus/`, `evals/baselines/` and `tests/evals/__init__.py`

## Phase 2: Foundational
- [X] T002 Shared helpers in `evals/replay_bench.py`: `load_plug("mod:fn")`, `sections(packet_text)` (split on
  `^[NAME]$`), `sentence_key` (lower-cased `\w+` tokens, as `engine/dm/narration._key`)

## Phase 3: User Story 1 — Replay bench (P1) MVP
**Independent test**: `py -3.12 evals/replay_bench.py run` on a clean checkout equals
`evals/baselines/replay_bench.txt`; with stub plugs it prints a second column.
- [X] T003 [US1] `extract` in `evals/replay_bench.py`: copy each `saves/*.db` (with its -wal) to a temp dir and
  read the copy, so saves are never touched, build the data-model corpus (R1, R2); late = stamp ≥ 193000 on 20261007 or later;
  sample ≤ 150 first-draft narrator packets from late saves, seeded; write `evals/corpus/narration.json.gz`;
  fail if > 3 MB
- [X] T004 [US1] Recorded measures in `evals/replay_bench.py`: first-draft pass, delivered-as-drafted, cut
  turns, class instability (R3), narrator/checker/other calls per turn, Oracle yes/no/cut (R4), declared
  mentions vs unknown-subject claims per first draft, top failing (verdict, class) and `contradicted` by class
- [X] T005 [US1] `run` with `--narrator/--judge` plugs (R5, contract): `recorded_narrator`, `recorded_judge`
  built in; plugged measures: first-draft pass, sentences failing, undeclared-new per draft, errors
- [X] T006 [US1] Run `extract` on the owner's saves, commit corpus; run `run` > `evals/baselines/replay_bench.txt`
- [X] T007 [P] [US1] Tests in `tests/evals/test_harness.py`: corpus loads and ≤ 3 MB; recorded table equals the
  committed baseline; stub plugs `echo_narrator` / `pass_judge` (defined in the test module) run on 5 packets; a raising narrator counts as a failed draft

## Phase 4: User Story 2 — Reader golden set (P1)
**Independent test**: `py -3.12 evals/reader_golden.py` prints per-field accuracy for the recorded Reader with
no model call.
- [X] T008 [US2] Pull candidate lines (issue inputs P-004, P-023, P-024, P-031, P-038, P-064, P-115, P-122,
  P-123 and controls) from `evals/playtests/*.md`, with the recorded Reader answer from the matching save turn
- [X] T009 [US2] Hand-label ≥ 75 lines incl. ≥ 8 negated minimal pairs into `evals/reader_golden.jsonl`
  (fields per data-model; `question_kind` ∈ who_is, where_is, what_happened, what_like, what_want, who_knows,
  none)
- [X] T010 [US2] Scorer `evals/reader_golden.py` (contract): per-field accuracy with n scored, roll/no-roll
  collapse, misses; `recorded` plug default
- [X] T011 [US2] Baseline `evals/baselines/reader_golden.txt`
- [X] T012 [P] [US2] Tests: every line has all labels with legal values; the issue lines and ≥ 8 pairs are
  present; a perfect stub Reader scores 100%; a Reader missing a field shows "not scored"

## Phase 5: User Story 3 — Long horizon (P2)
**Independent test**: two runs with the same seed print identical summaries.
- [X] T013 [US3] Metric functions in `evals/longhorizon.py` (R9): novelty-4, prefix share, view tokens by role
  and section, contradictions per 100 narrated turns, recall precision/coverage
- [X] T014 [US3] Aged store (R8): synthetic scenes appended via `Store.append`, checkpoints 50/200/300 with a
  look and a recall probe, packet sizes per role
- [X] T015 [US3] Scripted player (R7): ~300 lines from templates (revisits, absent-NPC questions, recall
  probes, scuffles, reading notices) on `tests/e2e/driver.Driver`; `--model gemini` flag (R10)
- [X] T016 [US3] Baseline `evals/baselines/longhorizon.txt` (offline, seed 7)
- [X] T017 [P] [US3] Tests: metric unit checks; a 20-line scripted run and a 10-scene aged run (fast); full
  run marked `slow`

## Phase 6: Polish
- [X] T018 `specs/005-measurement-harness/implementation-results.md` with the baseline table, sizes, hooks
  needed from other lanes
- [X] T019 Gate: `ruff check .`, `pyright`, full pytest; `git diff --stat` shows only lane files

## Dependencies
T001 → T002 → US1 (T003 → T004 → T005 → T006, T007). US2 and US3 depend only on T001 and can run in parallel
with US1. T018–T019 last.

## Implementation strategy
US1 first (it carries Phase 2's gate numbers), then US2 (spec 008's gate), then US3.
