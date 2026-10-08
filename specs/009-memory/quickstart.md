# Quickstart: validating 009 part A

```powershell
$env:PYTHONUTF8=1
py -3.12 -m pytest -q -p no:cacheprovider tests/engine/test_memory.py     # writer, cap, expiry, cards, spotlight, views, leak
py -3.12 -m pytest -q -p no:cacheprovider                                  # full suite (~3 min)
py -3.12 evals/longhorizon.py --mode aged       # Narrator view ≤ 10% growth 50 -> 300; recall and promise coverage
py -3.12 evals/longhorizon.py --mode scripted   # engine errors: 0
uvx ruff check engine evals tests ; uvx pyright <touched files>
```

Expected: all green; aged-mode numbers recorded in `implementation-results.md` against the baseline
(coverage 0.67, promise 0.00).
