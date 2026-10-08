# Quickstart: validating spec 007

All commands from the repo root, `PYTHONUTF8=1` set.

1. Unit and snapshot tests:
   `py -3.12 -m pytest -q -p no:cacheprovider tests/engine/test_gate_table.py tests/engine/test_necessity.py
   tests/engine/test_offer_snapshots.py`
2. Full suite: `py -3.12 -m pytest -q -p no:cacheprovider` (about 3 minutes).
3. Reader golden set, live on Claude Haiku (91 calls, about 15–20 minutes; answers cached):
   `py -3.12 evals/reader_golden.py --reader evals.reader_golden:haiku`
   Re-score from the cache without calls: `py -3.12 evals/reader_golden.py --reader evals.reader_golden:cached`.
   Expect: verb ≥ 95%, computed gate ≥ 98%, the negation pairs listed separately.
4. Odds audit: `py -3.12 evals/reader_golden.py --audit` prints, over the golden set's rolled beats framed with
   the rubric, the count of non-Dire unopposed OFFERs with critical failure above success (expect 0 unlabelled)
   and the share with ≥ 3 distinct alternative odds.
5. Lint: `uvx ruff check <touched files>`, `uvx pyright <touched files>`.
