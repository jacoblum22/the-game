"""`roll_table` (00.14.2; 12.6.7): roll a data table with RC-RNG, honouring context rows and recency.

    res = roll_table("tbl.meaning", {"meaning_kind": "action"}, rules=rules, state=tx.state, rng=rng)
    tx.add_all(res.events)          # table_rolled per table actually used (dispatcher and sub-tables)

Recency (12.6.7): a row drawn within the table's last `recency_window` draws (default 5) is re-drawn once; the
second draw stands. Stage a result's events before rolling the same table again (recency is read from state).
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from engine.rng import Rng
from engine.store.events import Event

DEFAULT_RECENCY_WINDOW = 5  # oracles.yaml header: recency_window default 5


class TableError(ValueError):
    pass


class TableResult(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    table_id: str
    roll: int | None
    row: dict[str, Any]
    entry: Any  # the row's `result`
    words: list[Any] = Field(default_factory=list)  # leaf results, in sub-table order (a meaning pair: 2 words)
    sub: list[TableResult] = Field(default_factory=list)
    redrawn: bool = False
    events: list[Event] = Field(default_factory=list)


def _thaw(x: Any) -> Any:
    if isinstance(x, Mapping):
        return {k: _thaw(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_thaw(v) for v in x]
    return x


def _context_row(table: Mapping[str, Any], context: Mapping[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
    # rule: 12.6.7
    """A context value that names a row (tbl.meaning's meaning_kind, tbl.twist's severity) selects it unrolled."""
    for key in table.get("context_filters") or ():
        v = context.get(key)
        if not isinstance(v, str):
            continue
        hits = [r for r in table["results"]
                if str(r.get("range")) == v or str(r.get("result", "")).lower().startswith(v.lower())]
        if len(hits) == 1:
            return _thaw(hits[0]), key
    return None, None


def _bounds(r: Any) -> tuple[float, float]:
    """A row's range: 'a-b', 'a', '00', [a, b], an int, 'N or less', 'N or more'."""
    if isinstance(r, int):
        return r, r
    if isinstance(r, (list, tuple)):
        return _bounds(r[0])[0], _bounds(r[-1])[1]
    t = str(r).strip()
    if m := re.fullmatch(r"(\d+) or less", t):
        return float("-inf"), int(m.group(1))
    if m := re.fullmatch(r"(\d+) or more", t):
        return int(m.group(1)), float("inf")
    a, _, b = t.partition("-")
    num = lambda x: 100 if x.strip() == "00" else int(x)  # noqa: E731
    return num(a), num(b or a)


def _modifier(table: Mapping[str, Any], context: Mapping[str, Any]) -> int:  # rule: 12.11.2
    """An int context value for a `*modifier` filter shifts the roll, clamped by the table's `total_clamp`."""
    mod = sum(int(v) for k, v in context.items()
              if k.endswith("modifier") and isinstance(v, int) and not isinstance(v, bool))
    clamp = (table.get("modifier") or {}).get("total_clamp") if isinstance(table.get("modifier"), Mapping) else None
    if clamp:
        mod = max(int(clamp[0]), min(int(clamp[1]), mod))
    return mod


def _draw(table: Mapping[str, Any], context: Mapping[str, Any], rng: Rng, purpose: str) -> tuple[int, dict[str, Any]]:
    roll = rng.roll_die(str(table["die"]), purpose, stream="tables", table_id=table.get("id")) + _modifier(table,
                                                                                                            context)
    for row in table["results"]:
        lo, hi = _bounds(row["range"])
        if lo <= roll <= hi:
            return roll, _thaw(row)
    raise TableError(f"{table.get('id')}: no row covers {roll}")


def roll_table(table_id: str, context: Mapping[str, Any] | None = None, *, rules: Any, state: Any, rng: Rng,
               purpose: str | None = None) -> TableResult:  # rule: 12.6.7
    """Roll `table_id` (any data table) and every sub-table its row names; `table_rolled` events included."""
    ctx = dict(context or {})
    table = rules.table(table_id)
    if table_id == "tbl.twist" and ctx.get("severity") == "S5" and ctx.get("pc_frame"):
        raise TableError("tbl.twist: S5 rows are legal only from world events (01.13.10)")
    row, used_key = _context_row(table, ctx)
    roll: int | None = None
    redrawn = False
    window = int(table.get("recency_window") or DEFAULT_RECENCY_WINDOW)
    recent = list(state.table_recency.get(table_id, [])) if table.get("recency") else []
    if row is None:
        if str(table.get("die")) == "none":
            raise TableError(f"{table_id}: no die and no context row ({list(table.get('context_filters') or [])})")
        why = purpose or f"roll_table {table_id}"
        roll, row = _draw(table, ctx, rng, why)
        if table.get("recency") and str(row.get("result")) in recent:
            roll, row = _draw(table, ctx, rng, why + " (recency re-draw)")
            redrawn = True
    entry = row.get("result")
    new_recent = ([*recent, str(entry)][-window:]) if table.get("recency") else []
    res = TableResult(table_id=table_id, roll=roll, row=row, entry=entry, redrawn=redrawn)
    res.events.append(Event.of("table_rolled", source="roll_table", rule_id="12.6.7", table_id=table_id,
                               context=_thaw(ctx), roll=roll, entry=entry, recency=new_recent))
    sub_ctx = {k: v for k, v in ctx.items() if k != used_key}
    for sub_id in row.get("sub_table") or ():
        sub = roll_table(sub_id, sub_ctx, rules=rules, state=state, rng=rng, purpose=purpose)
        res.sub.append(sub)
        res.events += sub.events
        res.words += sub.words
    if not row.get("sub_table"):
        res.words = [entry]
    return res
