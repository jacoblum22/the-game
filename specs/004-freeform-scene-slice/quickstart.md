# Quickstart: validating the freeform scene slice

How to prove the slice works once it is built. Commands refer to the layout in [plan.md](plan.md) and
the interfaces in [contracts/](contracts/).

## Prerequisites

- Python 3.11+, `pip install -r requirements.txt -r requirements-dev.txt` (hash-pinned).
- For live runs only: `GEMINI_API_KEY` in `.env` at the repo root (the prototype's loader already reads
  it; `.env` is git-ignored, so it lives on the machine that runs live sessions). Offline validation needs
  no keys.
- `rules/` from `integration-wave-swxsot`, unmodified.

## 1. Offline checks (free, run on every change)

```bash
python engine/build/compile_cards.py          # cards.json; fails if rules changed since the last build
python engine/build/coverage.py               # rule ids: implemented / deferred / model-judged
ruff check . && pyright && pytest             # unit, golden, contract, replay, seeded-error tests
```

Expected:
- Golden tests reproduce WE-00-1, WE-00-4, WE-01-2 (both branches) and the other in-scope worked
  examples with fixed dice; odds match T-01-3 for every modifier/DC pair; Oracle thresholds match T-01-10.
- The scheduler test confirms 00.7.6 ordering and that every handler id in `data/boundaries.yaml` is
  either implemented or logged as deferred.
- The seeded-error suite reports checker recall and false-positive rate from recorded checker outputs
  (SC-003 target: ≥90% recall, <10% false positives).
- Replay tests: every recorded session under `tests/replay/sessions/` replays identically (SC-006).

## 2. One live scene (costs cents)

```bash
python -m play.cli new --scene engine/fixtures/toll_bridge_scene.yaml \
  --pc engine/fixtures/pc_prepared.yaml --seed 7 --campaign runs/bridge.db --cap 0.50
```

Play these in order and check each result:

| # | Type this | Expect |
|---|---|---|
| 1 | `Evening. Is this the toll bridge?` | SPEECH plus a question; no roll; the keeper answers in the fiction |
| 2 | `Is the barge crewed?` | Oracle settles it once (`/turn` shows the odds rung and d100); asking again gets the same answer |
| 3 | `I cast a spell to open the gate.` | G3: not narrated as possible; a basic alternative and an acquisition path offered; nothing spent |
| 4 | `I wait for him to look away, then climb the rail and drop onto the barge.` | OFFER with approach, odds, stakes, threatened and alternate cost; no roll yet |
| 5 | `2` (change approach), then a new method | a fresh OFFER |
| 6 | `1` (commit) | one roll; the outcome matches the degree; any cost appears in `/sheet` and `/turn` |
| 7 | `There's obviously a rope tied to the rail, I use it.` | the rope is an assertion, not a fact; no lever from it unless the scene holds one |
| 8 | `wait, you said the gate was open` | answered from the turn record |
| 9 | play until the scene's question is answered | `scene_end` handlers run; skipped handlers listed in `/turn` |

Then:

```bash
python -m play.cli report runs/bridge.db     # verdict rates, fallback rate, cost and latency per turn
python -m play.cli replay runs/bridge.db     # "identical"
python -m play.cli open runs/bridge.db       # resumes where you stopped, including an open OFFER
```

## 3. Evaluation runs (budget-capped)

```bash
python evals/run_live.py --persona honest --turns 25 --cap 1.00
python evals/run_live.py --persona curious --turns 25 --cap 1.00
python evals/run_live.py --persona adversarial --turns 25 --cap 1.00
```

Each writes a report next to its session file. The slice passes when, across the three runs plus one
human-played session (spec.md SC-001 to SC-009):
- every frame's numbers come from the engine and every rolled beat had an offer or a legal auto-commit;
- human review finds no delivered contradiction of stored state; the plain fallback is under 5% of turns;
- every G3/G4 response offers an alternative;
- the offer shows within 5 s and non-pausing turns finish within 10 s (median);
- median cost per turn is at most 3¢ and no run exceeds its cap.

Write the numbers, failures and surprises to `specs/004-freeform-scene-slice/implementation-results.md`.
