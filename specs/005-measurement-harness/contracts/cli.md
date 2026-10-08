# Contract: harness commands and plugs

All commands run from the repo root with `PYTHONUTF8=1 py -3.12 …`, print a short summary, and exit 0.

## Replay bench — `evals/replay_bench.py`

```text
replay_bench.py extract [--saves DIR] [--late-from HHMMSS] [--max-packets 150]   # saves -> evals/corpus/
replay_bench.py run [--narrator MOD:FN] [--judge MOD:FN] [--limit N]           # corpus -> table
```

- `run` with no plugs prints the recorded baseline (all saves, late subset). With plugs it also prints the
  measures for the plugged pair on the corpus packets.
- `narrator(packet: dict[str, str]) -> dict` — `packet` maps section name to text; returns at least
  `{"fiction": str}`; may add `"mentions"` (declared new elements) and any schema fields.
- `judge(packet: dict[str, str], draft: dict) -> list[dict]` — one item per sentence:
  `{"text": str, "ok": bool, "cls": str | None, "undeclared_new": bool}`.
- A plug that raises on a packet counts as a failed first draft.

## Reader golden set — `evals/reader_golden.py`

```text
reader_golden.py [--reader MOD:FN | recorded]
```

- `reader(line: str, context: str) -> dict` with any subset of the label fields; missing fields are "not
  scored". Prints accuracy per field (n scored), the roll/no-roll collapse of necessity, and up to 10 misses.

## Long-horizon — `evals/longhorizon.py`

```text
longhorizon.py [--mode aged|scripted|both] [--seed 7] [--scenes 300] [--lines 300] [--model offline|gemini]
```

- Prints the R9 metric block per mode. `--model gemini` needs `GEMINI_API_KEY` and is owner-run.
