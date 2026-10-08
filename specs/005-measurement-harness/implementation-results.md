# Implementation results: Measurement harness (spec 005)

Engine at `milestone-1-playable` 0dd4b7d. Every number below is reproduced by the commands in
[quickstart.md](quickstart.md); the full outputs are in `evals/baselines/`.

## Baseline table (gates for specs 006–009)

### Narration (replay bench, recorded; B §1.2 population = 33 late runs)

| Measure | Late runs (B's cut) | All 74 saves | B §1.2 said | Phase 2 gate |
|---|---|---|---|---|
| First-draft pass rate | 5/374 (1.3%) | 13/845 (1.5%) | 1.4% (4/294) | > 50% |
| Delivered as first drafted | 3/374 (0.8%) | 9/845 (1.1%) | 3/374 | |
| Turns with cut sentences | 217/374 (58.0%) | 481/845 (56.9%) | 56% | < 15% |
| Checker class instability, unchanged sentences | 845/2,684 (31.5%) | 1,771/5,498 (32.2%) | 33% | |
| Narrator calls per turn (per narrated turn) | 1.81 (2.53) | 1.90 (2.63) | 1.81 | ≤ 1.2 |
| Checker / other calls per turn | 1.61 / 1.47 | 1.62 / 1.40 | 1.61 / 1.52 | |
| Oracle asks on drafted details / "no" → redraft | 713 / 342 | 1,410 / 676 | 713 / 342 | |
| New elements per first draft: declared / undeclared | 0.94 / 2.88 | 1.32 / 4.00 | 0.86 / 2.1 | undeclared < 0.3 |
| Fallback turns | 21/374 (5.6%) | 117/845 (13.8%) | ≈ 4% | ≤ 4% |
| Packet subset (150 packets): pass / failing sentences | 2/150 (1.3%) / 657 of 1,484 (44.3%) | | | A/B column |

Differences from B: "first draft" here is the first *checked* version (a mention redraft comes first in 80
turns), so the denominator is 374 rather than 294. The undeclared count includes every unknown-subject claim
in the first checked draft.

### Reader (golden set, today's recorded Haiku answers, 61 of 91 lines have one)

| Field | Accuracy | Phase 2 gate |
|---|---|---|
| verb | 72.1% (44/61) | ≥ 95% |
| gate | 63.9% (39/61) | ≥ 98% |
| necessity / roll vs no roll | 70.5% / 81.8% (44) | |
| issue lines P-004…P-123: verb / gate | 50.0% / 35.7% (14) | |
| facets, question_kind | not produced by today's Reader | |

The recorded answers predate the round-1 prompt fixes for some lines (P-031, P-122, P-123), so this is the
Reader as played, not the Reader at 0dd4b7d. A live re-run needs a model (`--reader`).

### Long horizon (offline model, seed 7)

| Metric | Value |
|---|---|
| Narrator packet / view tokens at aged scene 50 → 200 → 300 | 15,210 / 1,295 → 15,926 / 1,576 → 16,572 / 1,992 |
| Sections growing > 10% (scene 50 → 300) | NARRATOR VIEW 1,295→1,992; RECENT EXCHANGES 67→555; THIS MESSAGE 406→583 |
| Recall probes (aged): precision / coverage | 0.46 / 0.67 (oldest 1.00, middle 0.50, newest 0.50) |
| Promise probes (aged): coverage | 0.00 (3 probes) |
| Scripted: contradictions per 100 narrated turns | 0.0 (offline Checker) |
| Scripted: novelty-4 over the previous 10 deliveries | 0.33 |
| Scripted: narrator packet / view tokens at line 50 / 200 / 300 | 16,287 / 1,781; 15,555 / 1,171; 19,135 / 4,050 |
| Cached-prefix share | reader 0.96, checker 0.94, narrator 0.91, world 0.73, framer 0.72, director 0.43 |
| Engine errors in 300 lines | 7 ("names exhausted" from line 224) |

## Committed (sizes)
- `evals/replay_bench.py`, `evals/reader_golden.py`, `evals/longhorizon.py`.
- `evals/corpus/narration.json.gz`, 960 KB: 845 narrated turns from 74 saves, 150 first-draft narrator packets
  (sections stored once), the recorded draft, claims and verdicts.
- `evals/reader_golden.jsonl`, 44 KB: 91 lines: 14 issue lines, 47 transcript controls, 11 negated minimal pairs, 8 constructed controls.
- `evals/baselines/*.txt` (6 KB total). `tests/evals/test_harness.py`: 8 fast tests (about 6 s) and 1 slow test.

## Findings for other lanes (no engine edits were made)
1. **`engine/gen/_seed_lib.py` raises "names exhausted"** after about 220 scripted lines (each scene framed on
   travel casts new NPCs). Every later travel fails.
2. **Journal lookup by name is partial-name matching.** "What do I know about Joss Fenn?" lists Joss Dunmere,
   Pell Fenn and Joss Elkin and omits Joss Fenn (synthesis §7, "first-name matching" → alias index, A P2).
3. **"What did I promise X?" is not answered from commitments** (0 of 3 probes).
4. **The narrator view grows with store age** (+54% from scene 50 to 300): this is the SC-002 gap A P3
   targets.
5. **No 12.4.8 scene-end sweep exists**, so contradictions come from verdicts only. Offline Talk writes no PC
   knowledge, so the scripted recall probes are unscorable offline (0 of 25 scored). They need Gemini (D9).
6. Pre-existing on the base: `ruff check .` reports 10 errors in `engine/`, `play/` and `tests/engine/`, and
   `pyright` reports 17. The harness files are clean.
