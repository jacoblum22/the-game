# Quickstart: Measurement harness

Prerequisites: `py -3.12`, `pip install -r requirements-dev.txt`, `PYTHONUTF8=1` on Windows. No network.

1. **Bench baseline** — `py -3.12 evals/replay_bench.py run`
   Expect the six measures for "all" and "late"; compare with `evals/baselines/replay_bench.txt` (identical).
2. **Bench A/B slot** — `py -3.12 evals/replay_bench.py run --narrator tests.evals.test_harness:echo_narrator
   --judge tests.evals.test_harness:pass_judge --limit 20` prints a second column for the stub pair.
3. **Golden set** — `py -3.12 evals/reader_golden.py` scores today's recorded Reader; compare with
   `evals/baselines/reader_golden.txt`.
4. **Long horizon** — `py -3.12 evals/longhorizon.py --mode both` (several minutes); compare with
   `evals/baselines/longhorizon.txt`. Same seed → same numbers.
5. **Rebuild the corpus** (owner machine, needs `saves/`) — `py -3.12 evals/replay_bench.py extract`; then
   step 1 must still match.
6. **Tests** — `py -3.12 -m pytest -q -p no:cacheprovider tests/evals` (fast);
   add `--runslow` for the full long-horizon run.
