# Contract: Terminal interface (slice only)

`python -m play.cli` over the session API. Plain stdin/stdout, no dependencies.

## Commands

| Command | Effect |
|---|---|
| `python -m play.cli new --scene engine/fixtures/toll_bridge_scene.yaml --pc engine/fixtures/pc_prepared.yaml --seed 7 --campaign runs/bridge.db` | New session; prints the opening |
| `python -m play.cli open runs/bridge.db` | Resume, including an open pause |
| `python -m play.cli replay runs/bridge.db` | Replay with recorded model outputs; prints "identical" or the first divergence |
| `python -m play.cli report runs/bridge.db` | Per-turn table: classes, gate, degree, verdicts, fallback, cost, latency; session totals |

Flags on `new`/`open`: `--cap 1.00` (USD), `--auto-commit`, `--replay`.

## In-session input

- Any text is a player message (`session.submit`).
- At a pause, a number picks the listed choice (`session.answer`); free text is still accepted and goes
  through T2 as a PENDING_ANSWER or a new declaration (12.2.6).
- Slash commands (out of fiction, never sent to a model): `/sheet` (codex view), `/turn [n]` (turn
  record), `/save [label]`, `/quit`, `/spend`.

## Output layout

```text
<fiction paragraph(s)>

[OFFER] Climb the rail and drop onto the barge — Agility, a hard obstacle.
        Success or better 55% · critical failure 5% · near miss 10%.
        Stakes: risky. If it goes wrong: a jarring fall (harm). Or instead: you're seen (exposure).
  1) Commit   2) Change approach   3) Withdraw   4) Go big   5) Play it safe
> 
```

Fiction carries no numbers or rules words (12.14.4); numbers appear only inside OOF blocks (12.15).
After each turn a dim status line shows `turn cost · session cost / cap`.
