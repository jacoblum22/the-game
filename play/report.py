"""`python -m play report <name>` and `python -m play replay <name>` (T075).

    report(path, print)            # per-turn classes, gates, degrees, verdicts, fallbacks, cost, latency; totals
    replay(path, print, Game)      # "identical", or the first divergence

The report reads the store's `turns` and `model_calls` tables and the turn's `frame_committed` /
`frame_resolved` events; it never calls a model.
"""

from __future__ import annotations

import json
import statistics
from collections import Counter
from collections.abc import Callable
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

Say = Callable[[str], None]


class TurnLine(BaseModel):
    turn_id: str
    classes: list[str] = Field(default_factory=list)
    gates: list[str] = Field(default_factory=list)
    degrees: list[str] = Field(default_factory=list)
    verdicts: dict[str, int] = Field(default_factory=dict)
    fallback: bool = False
    calls: int = 0
    cost_usd: float = 0.0
    latency_ms: int = 0


class Totals(BaseModel):
    turns: int = 0
    fallback_rate: float = 0.0
    median_cost_usd: float = 0.0
    median_latency_ms: float = 0.0
    total_cost_usd: float = 0.0
    model_calls: int = 0
    outcomes: dict[str, int] = Field(default_factory=dict)


def _turn_key(turn_id: str) -> tuple[int, str]:
    tail = turn_id.rsplit(".", 1)[-1]
    return (int(tail), turn_id) if tail.isdigit() else (1 << 30, turn_id)


def turn_lines(store: Any) -> list[TurnLine]:
    """One line per recorded turn, in turn order."""
    conn = store.conn
    lines: dict[str, TurnLine] = {}
    for r in conn.execute("SELECT turn_id, parts, verdicts, fallback_used, cost_usd, latency_ms FROM turns"):
        parts = json.loads(r["parts"] or "[]")
        verdicts = Counter(str(v.get("verdict", "?")) for v in json.loads(r["verdicts"] or "[]"))
        lines[r["turn_id"]] = TurnLine(turn_id=r["turn_id"], classes=[str(p.get("class", "?")) for p in parts],
                                       verdicts=dict(verdicts), fallback=bool(r["fallback_used"]),
                                       cost_usd=float(r["cost_usd"] or 0.0), latency_ms=int(r["latency_ms"] or 0))
    for r in conn.execute("SELECT turn_id, type, payload FROM events WHERE type IN ('frame_committed',"
                          " 'frame_resolved') AND turn_id IS NOT NULL ORDER BY seq"):
        line = lines.get(r["turn_id"])
        if line is None:
            continue
        p = json.loads(r["payload"])
        if r["type"] == "frame_committed":
            line.gates.append(str((p.get("frame") or {}).get("gate", {}).get("class", "?")))
        else:
            line.degrees.append("near_miss" if p.get("near_miss") else str(p.get("degree") or "-"))
    calls: dict[str, list[dict[str, Any]]] = {}
    for c in store.model_calls():
        calls.setdefault(c.get("turn_id") or "", []).append(c)
    for tid, line in lines.items():
        rows = calls.get(tid, [])
        line.calls = len(rows)
        line.cost_usd = line.cost_usd or sum(float(c.get("cost_usd") or 0.0) for c in rows)
        line.latency_ms = line.latency_ms or sum(int(c.get("latency_ms") or 0) for c in rows)
    return [lines[t] for t in sorted(lines, key=_turn_key)]


def totals(lines: list[TurnLine], calls: list[dict[str, Any]]) -> Totals:
    if not lines:
        return Totals(model_calls=len(calls))
    return Totals(turns=len(lines), fallback_rate=sum(ln.fallback for ln in lines) / len(lines),
                  median_cost_usd=statistics.median(ln.cost_usd for ln in lines),
                  median_latency_ms=statistics.median(ln.latency_ms for ln in lines),
                  total_cost_usd=sum(float(c.get("cost_usd") or 0.0) for c in calls),
                  model_calls=len(calls), outcomes=dict(Counter(str(c.get("outcome")) for c in calls)))


def _cell(items: list[str] | dict[str, int]) -> str:
    if isinstance(items, dict):
        return ",".join(f"{k}x{v}" for k, v in items.items()) or "-"
    return ",".join(items) or "-"


def render(lines: list[TurnLine], tot: Totals, title: str) -> str:
    out = [f"Report: {title}", "",
           f"{'turn':<10} {'classes':<28} {'gates':<10} {'degrees':<26} {'verdicts':<22} fb {'calls':>5} "
           f"{'cost $':>9} {'ms':>7}"]
    for ln in lines:
        out.append(f"{ln.turn_id:<10} {_cell(ln.classes):<28} {_cell(ln.gates):<10} {_cell(ln.degrees):<26} "
                   f"{_cell(ln.verdicts):<22} {'Y' if ln.fallback else '-':<2} {ln.calls:>5} {ln.cost_usd:>9.4f} "
                   f"{ln.latency_ms:>7}")
    out += ["", f"Turns: {tot.turns} | fallback rate {tot.fallback_rate:.1%} | median cost ${tot.median_cost_usd:.4f}"
            f" | median latency {tot.median_latency_ms:.0f} ms",
            f"Model calls: {tot.model_calls} ({_cell(tot.outcomes)}) | total cost ${tot.total_cost_usd:.4f}"]
    return "\n".join(out)


def report(path: Path, say: Say) -> int:
    from engine.store.db import Store

    store = Store.open(path)
    try:
        lines = turn_lines(store)
        say(render(lines, totals(lines, store.model_calls()), Path(path).stem))
    finally:
        store.close()
    return 0


def replay(path: Path, say: Say, game_cls: Any) -> int:
    """Rebuild the game from its events with the recorded model outputs; "identical" or the first divergence."""
    from engine.llm.base import ReplayDivergence

    try:
        result = game_cls.replay(path)
    except ReplayDivergence as e:
        say(f"Diverged: {e}")
        return 1
    divergence = next((getattr(result, k) for k in ("divergence", "first_divergence") if getattr(result, k, None)),
                      None)
    identical = getattr(result, "identical", divergence is None)
    if identical and divergence is None:
        say(f"Replay of {Path(path).stem}: identical.")
        return 0
    say(f"Replay of {Path(path).stem} diverged: {divergence if divergence is not None else result}")
    return 1
