"""The clue judgment (PR-12-10 step 1, 15.9.5; D2 A: DL-12-112, DL-15-40; spec 025): one small model call reads a
question put to an NPC beside the about lines of the open clues and names the one the question is about, or none.

    i = judge(ctx, "Did he have enemies?", [("who had cause to want him gone (the matter: ...)", True)])
    # 0: the first clue; None: not about any

The call sees no sealed content beyond the about lines (never a node's answer). Code then hands a held clue to the
narrator or points a non-holder to the holder (engine/dm/answer.py). Retires word-overlap case routing.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from engine.dm.schemas import CLUE_ITEMS

MAX_ITEMS = len(CLUE_ITEMS)


def message(question: str, items: Sequence[tuple[str, bool]]) -> str:
    lines = [f"{i + 1:d}{'*' if held else ''}: {about}" for i, (about, held) in enumerate(items[:MAX_ITEMS])]
    return "\n".join([f'THE QUESTION: "{question}"',
                      "OPEN CLUES (number: what a question must be about to reach it; * = this person holds it):",
                      *lines])


def judge(ctx: Any, question: str, items: Sequence[tuple[str, bool]]) -> int | None:  # rule: PR-12-10
    """The index of the clue the question is about, or None. `items`: (about line, held by the one asked), at most
    `MAX_ITEMS` (the held ones first)."""
    if not items or not question.strip():
        return None
    from engine.dm.packet import render_exchange, turn_exchanges
    from engine.dm.roles.prompts import load_prompt
    from engine.dm.schemas import build_schema, schema_context
    from engine.llm.base import Packet, Role, call_role

    st = ctx.need_tx().state
    ex = turn_exchanges(ctx, 1) if getattr(ctx, "store", None) is not None else []
    packet = Packet(instructions=load_prompt("clue"), core="", cards=[], view="",
                    exchanges=[render_exchange(x) for x in ex], message=message(question, items))
    res = call_role(ctx.model, Role.CLUE, build_schema(Role.CLUE, schema_context(st, ctx.rules)), packet,
                    turn_id=ctx.turn_id, recorder=ctx.record_call, default={"about": "none"})
    v = str((res.data or {}).get("about") or "none")
    n = int(v) if v.isdigit() else 0
    return n - 1 if 0 < n <= min(len(items), MAX_ITEMS) else None


__all__ = ["MAX_ITEMS", "judge", "message"]
