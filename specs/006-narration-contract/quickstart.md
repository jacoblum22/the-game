# Quickstart: validating spec 006

```bash
export PYTHONUTF8=1
py -3.12 -m pytest -q -p no:cacheprovider                       # SC-001 (about 3-4 min)
py -3.12 -m pytest -q tests/engine/test_declare.py tests/engine/test_npc_layer.py tests/engine/test_repair.py
py -3.12 evals/longhorizon.py --mode scripted                    # SC-002; compare with evals/baselines/longhorizon.txt
py -3.12 evals/replay_bench.py run --narrator evals.narration_plug:haiku --judge evals.narration_plug:judge --limit 80
                                                                 # SC-003..006 (Claude CLI logged in; ~30-45 min)
py -3.12 evals/replay_bench.py run --narrator evals.narration_plug:offline --judge evals.narration_plug:judge
                                                                 # free smoke of the plug path
```

Expected: suite green; scripted run with 0 contradictions per 100 turns; the replay section "Packets:
evals.narration_plug:haiku + …" prints pass rate, cut turns, narrator calls per turn and undeclared new per
draft. Results go to `specs/006-narration-contract/implementation-results.md` and
`evals/baselines/replay_006.txt`.
