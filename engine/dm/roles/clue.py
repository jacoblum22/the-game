"""The clue judgment (PR-12-10 step 1, 15.9.5; D2 A: DL-12-112, DL-15-40; P9: DL-15-45; specs 025 and 029): one small
model call reads **a whole message's** questions to an NPC beside the about lines of the open clues and names the one
the message is about, and which question asks it, or none.

    i, part = judge(ctx, ["What are the banners?", "And who is the young man really?"],
                    [("who the challenger is (the matter: ...)", True)])
    # (0, 1): the first clue, asked by the second question;  (None, None): not about any

One call per message, whatever the number of parts (round 8: the cap dropped Betric's clue before a per-part check
saw it). The call sees no sealed content beyond the about lines (never a node's answer). Code then hands a held clue to
the narrator as a learned fact or points a non-holder to the holder (engine/dm/answer.py). Retires word-overlap case
routing (spec 025) and per-part calls (spec 029).
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from engine.dm.schemas import CLUE_ITEMS, CLUE_PARTS

MAX_ITEMS = len(CLUE_ITEMS)
MAX_PARTS = len(CLUE_PARTS)


def message(questions: str | Sequence[str], items: Sequence[tuple[str, bool]]) -> str:
    qs = [questions] if isinstance(questions, str) else list(questions)[:MAX_PARTS]
    lines = [f"{i + 1:d}{'*' if held else ''}: {about}" for i, (about, held) in enumerate(items[:MAX_ITEMS])]
    head = ([f'THE QUESTION: "{qs[0]}"'] if len(qs) == 1 else
            ["THE QUESTIONS (one message; the clue counts if any one of them is about it):",
             *(f'Q{i + 1:d}: "{q}"' for i, q in enumerate(qs))])
    return "\n".join([*head, "OPEN CLUES (number: what a question must be about to reach it; * = this person holds it):",
                      *lines])


def judge(ctx: Any, questions: str | Sequence[str], items: Sequence[tuple[str, bool]]
          ) -> tuple[int | None, int | None]:  # rule: PR-12-10
    """(the index of the clue the message is about, the index of the question that asks it), or (None, None).
    `items`: (about line, held by the one asked), at most `MAX_ITEMS` (the held ones first). The question index is
    None when the model does not say which, or the message has one question."""
    qs = [questions] if isinstance(questions, str) else [q for q in questions if q.strip()]
    if not items or not qs:
        return None, None
    from engine.dm.packet import render_exchange, turn_exchanges
    from engine.dm.roles.prompts import load_prompt
    from engine.dm.schemas import build_schema, schema_context
    from engine.llm.base import Packet, Role, call_role

    st = ctx.need_tx().state
    ex = turn_exchanges(ctx, 1) if getattr(ctx, "store", None) is not None else []
    packet = Packet(instructions=load_prompt("clue"), core="", cards=[], view="",
                    exchanges=[render_exchange(x) for x in ex], message=message(qs, items))
    res = call_role(ctx.model, Role.CLUE, build_schema(Role.CLUE, schema_context(st, ctx.rules)), packet,
                    turn_id=ctx.turn_id, recorder=ctx.record_call, default={"about": "none", "part": "none"})
    v = str((res.data or {}).get("about") or "none")
    n = int(v) if v.isdigit() else 0
    if not 0 < n <= min(len(items), MAX_ITEMS):
        return None, None
    p = str((res.data or {}).get("part") or "none")
    part = int(p) - 1 if p.isdigit() and 0 < int(p) <= min(len(qs), MAX_PARTS) else None
    return n - 1, (0 if part is None and len(qs) == 1 else part)


__all__ = ["MAX_ITEMS", "MAX_PARTS", "judge", "message"]
