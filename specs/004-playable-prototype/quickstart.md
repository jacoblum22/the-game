# Quickstart: validating Milestone 1

## How to play (start here)

1. `pip install -r requirements.txt`
2. Put your key in a file named `.env` at the repo root: `GEMINI_API_KEY=...` (it is git-ignored).
3. Check the key and the request format once (about 1–2 cents; `--dry-run` sends nothing):
   `python evals/gemini_smoke.py`.
4. `python -m play new "My World"` starts a game: fourteen world questions, then your character, then
   play. Answer in your own words or pick a number; press Enter or type `skip` to let the dice decide.
5. Type what your character does in plain English. `/sheet`, `/journal`, `/turn`, `/spend` and `/quit`
   are the useful commands; `/quit` saves, and `python -m play continue` picks up where you stopped.

Add `--offline` to any command to play with the free stand-in model instead of Gemini. It checks that
the engine works; its prose is template text, not a real DM.

## Validation

How to prove the prototype plays start to finish once Milestone 1 is built. Commands refer to the layout in
[plan.md](plan.md) and the interfaces in [contracts/](contracts/). Later milestones add their own sections
here.

## Prerequisites

- Python 3.11+, `pip install -r requirements.txt -r requirements-dev.txt` (hash-pinned).
- For play: `GEMINI_API_KEY` in `.env` at the repo root (git-ignored, so it lives on the machine you play
  on). Offline validation needs no key.
- `rules/` from `main` (swxsot was merged there), unmodified.

## 1. Offline checks (free, run on every change)

```bash
python engine/build/compile_cards.py          # cards.json; fails if rules changed since the last build
python engine/build/coverage.py --milestone 1 # rule ids: implemented / coarse / deferred / model-judged
ruff check . && pyright && pytest             # unit, golden, parity, contract, replay, seeded-error tests
```

Expected:
- Golden tests reproduce the in-scope worked examples (WE-00-*, WE-01-*, ch.07's) with fixed dice; odds
  match T-01-3; Oracle thresholds match T-01-10.
- The world-seed port reproduces `rules/_process/simulation/12-world-seed.py` exactly on the same seed;
  the birth draw matches its reference output.
- The scheduler test confirms 00.7.6 ordering, that skipping time runs every crossed boundary (00.7.7), and
  that every handler id in `data/boundaries.yaml` is either live for the milestone or logged as skipped.
- The seeded-error suite reports checker recall and false-positive rate (SC-003: ≥90% recall, <10% false
  positives).
- Every recorded game under `tests/replay/` replays identically.

## 2. Play it

```bash
python -m play
```

Choose **New game** and play. A first game should cover, in whatever order the story takes you:

| Check | What should happen |
|---|---|
| World seed in mixed mode | You answer the questions you pick, the rest are rolled; each step shows a summary; you can veto a step once |
| Quick-start creation | Five questions; skipped ones take the stated default; a name is required |
| The opening | You start in the middle of an incident, with an open prompt |
| Talk and questions | No dice for small talk or plain questions; an unsettled fact asked twice gets the same answer |
| A risky action | An offer with odds, stakes and the threatened cost before any roll; withdraw costs nothing |
| Something you can't do | No pretending; a way forward is offered |
| A fight | Resolved beat by beat through offers; a lethal frame comes with a warning and a choice first |
| Getting hurt and resting | Harm shows in `/sheet`; a rest restores what ch.07 says |
| Moving on | Scenes cut and new ones open; going to another place in the region advances time |
| Quit mid-offer, then Continue | A recap, and the same offer still open |
| An ending | Death (after a warning), retirement or career end gives an epilogue and the choice of a new character in this world |

Then:

```bash
python -m play report "<save name>"   # per-turn classes, gates, degrees, verdicts, fallbacks, cost, latency
python -m play replay "<save name>"   # "identical"
```

## 3. Milestone 1 sign-off

Milestone 1 is done when (spec.md SC-001 to SC-011):
- three owner games of 150+ turns each, one played adversarially, show no delivered contradiction of stored
  state on review of sampled turns, including facts from more than 100 turns earlier; plain fallback under
  5% of turns;
- every death followed a warning and a choice; every unlicensed or impossible attempt got an alternative;
- quit and resume at any point restored the game exactly;
- offers showed within 5 s and plain turns finished within 10 s (median); cost and latency stayed flat over
  the game; median cost per turn ≤3¢;
- the owner says it plays as the actual game.

Write the numbers, failures and surprises to `specs/004-playable-prototype/implementation-results.md`.
