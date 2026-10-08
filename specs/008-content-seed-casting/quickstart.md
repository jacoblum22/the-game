# Quickstart: validating 008 part A

```powershell
$env:PYTHONUTF8=1
py -3.12 -m pytest -q -p no:cacheprovider tests/engine/test_seed_packs.py tests/engine/test_case.py tests/engine/test_cast.py tests/golden/test_world_seed_parity.py
py -3.12 -m pytest -q -p no:cacheprovider          # full suite
py -3.12 evals/longhorizon.py --mode scripted --lines 320   # no "names exhausted"; view tokens per role
uvx ruff check engine tests ; uvx pyright <touched files>
```

Expected: parity = reference packed record on the parity seeds; 30/30 openings with a valid incident case whose
core placement is at the opening place; same seed -> same packs and case; the scripted run reports 0 engine
errors from names. Packet deltas are recorded in `implementation-results.md`.
