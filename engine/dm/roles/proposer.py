"""The Proposer (PR-12-10 rung 3, spec 008 part B): one small call that frames ONE typed candidate answer to an
ordinary question; the Oracle, not the model, settles whether the asked NPC knows it (00.12.7's proposal form).

    cand = propose(ctx, "Hilde Marsh (innkeeper)", "what are the roads like?", "roads", known=["..."])
    # {"kind": "ordinary_fact", "subject": ..., "predicate": ..., "value": ...} or None (no usable candidate)

Called only when the store and the knowledge pack are empty and the reach allows the rung. The packet is tiny: the
prompt, the asker's known lines and the question (no core rules, no cards, no scene view).
"""

from __future__ import annotations

from typing import Any

from engine.dm.context import TurnContext
from engine.dm.roles.prompts import load_prompt
from engine.dm.schemas import build_schema, defaults, schema_context
from engine.llm.base import Packet, Role, call_role


def propose(ctx: TurnContext, who: str, question: str, topic: str, gist: str, *,
            known: list[str]) -> dict[str, Any] | None:  # rule: PR-12-10
    sctx = schema_context(ctx.state, ctx.rules)
    schema = build_schema(Role.PROPOSER, sctx)
    view = "\n".join(["what they already know:", *(f"- {k}" for k in known)] if known else ["they know nothing "
                                                                                             "on record about it"])
    packet = Packet(instructions=load_prompt("proposer"), core="", cards=[], view=view, exchanges=[],
                    message=f"{who} is asked: {question}\ntopic: {topic} ({gist})")
    res = call_role(ctx.model, Role.PROPOSER, schema, packet, turn_id=ctx.turn_id, recorder=ctx.record_call,
                    default=lambda: defaults(Role.PROPOSER, sctx) or {})
    d = dict(res.data)
    if d.get("kind") != "ordinary_fact" or not all(str(d.get(k) or "").strip() for k in ("subject", "value")):
        return None
    return d


__all__ = ["propose"]
