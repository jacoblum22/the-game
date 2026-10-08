# Implementation Plan: Measurement harness

**Branch**: `005-measurement-harness` | **Date**: 2026-10-08 | **Spec**: [spec.md](spec.md)

## Summary

Three offline instruments plus their committed baselines (spec Stories 1–3). The bench and the golden scorer
read committed data only; the long-horizon harness drives the real engine through the existing e2e `Driver`
(`tests/e2e/driver.py`) with the offline model. Decisions are in [research.md](research.md); file shapes in
[data-model.md](data-model.md); command lines and plug signatures in [contracts/cli.md](contracts/cli.md).

## Technical Context

**Language/Version**: Python 3.12 (`py -3.12`), stdlib only beyond what the engine already uses.
**Primary Dependencies**: the engine package (read-only use: `Game`, `Store`, `OfflineModel`, `GameConfig`),
`tests/e2e/driver.py` for setup and pause handling.
**Storage**: gzip JSON corpus under `evals/corpus/`; plain JSONL golden set; text baselines.
**Testing**: pytest; fast tests in `tests/evals/`, the full long-horizon run marked `slow`.
**Target Platform**: Windows dev machine and cloud sessions (no network needed).
**Project Type**: CLI scripts under `evals/`.
**Performance Goals**: bench + golden scorer < 2 min together; harness tests add < 15 s to the default suite.
**Constraints**: no API spend; no engine or rules edits (lane rule); corpus ≤ 3 MB.
**Scale/Scope**: ~1,170 recorded turns, ≤ 150 packets, ~80 golden lines, 300 scripted lines, 300 aged scenes.

## Constitution Check

| Principle | Effect on this feature | Status |
|---|---|---|
| I. AI-driven mechanical resolution | Measures the split between model judgment and code; changes neither | Pass |
| II. Custom ruleset | No rules change | Pass |
| III. Bounded flexibility | Golden set labels follow 01.3.1/01.4.1 as written | Pass |
| IV. MVP scope | Single-player text only | Pass |
| V. Closed primitives | Not touched | Pass |
| VI. Consolidation | Harness is additive tooling, not progression content; it retires nothing but adds no content | Pass |
| VII. Default-deny gate | Golden set measures the gate (G1/G3) the principle requires | Pass |
| Technology constraints | Gemini stays the model; offline default, Gemini behind a flag; Claude CLI not used | Pass |

Post-design re-check: unchanged, no violations.

## Project Structure

```text
specs/005-measurement-harness/  spec.md plan.md research.md data-model.md quickstart.md contracts/cli.md
                                tasks.md implementation-results.md
evals/
├── replay_bench.py        # extract (saves → corpus) and run (corpus → B §1.2 table; pluggable narrator/judge)
├── reader_golden.py       # scorer: any Reader by import path; `recorded` plug = today's Haiku answers
├── reader_golden.jsonl    # ~80 hand-labelled lines
├── longhorizon.py         # aged store + scripted player + metrics
├── corpus/narration.json.gz
└── baselines/             # replay_bench.txt, reader_golden.txt, longhorizon.txt
tests/evals/test_harness.py
```

**Structure Decision**: flat scripts in the existing `evals/` package, one module per instrument, matching
`evals/playtest.py`. `evals/playtest.py` is not modified.

## Complexity Tracking

None.
