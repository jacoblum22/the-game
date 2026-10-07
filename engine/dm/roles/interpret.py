"""The Interpret role (contracts/model-calls.md I): map a player's answer onto one seed or creation block.

    res = interpret(ctx, "the hunter, I think", choices=pause.choices, block=block_text,
                    classes=livelihood_ids, cards=("PR-02-7", "02.2.4"))
    res.choice            # an option id, or own_words / move_on / details / suggest
    res.picks             # every option the player named by number ("1, 3"), for multi-pick blocks
    res.own_words_text    # the player's words, verbatim, when they answered in their own words

A number (or a lone letter, or an option's id or exact label) maps to the option directly, without a model call
(12.2.6: answering a pause by its option). Everything else is one Interpret call; the engine applies the result.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from typing import Any

from pydantic import BaseModel, Field

from engine.dm.context import TurnContext
from engine.dm.packet import build_packet
from engine.dm.response import Choice
from engine.dm.roles.prompts import load_prompt
from engine.dm.schemas import SPECIAL_CHOICES, SchemaContext, build_schema, defaults
from engine.llm.base import Role, call_role
from engine.retrieve.cards import load_cards_for

MOVE_ON = "move_on"
OWN_WORDS = "own_words"
DETAILS = "details"
SUGGEST = "suggest"
_SPLIT = re.compile(r"\s*(?:,|;|&|\band\b|\s)\s*")
_SKIP = {"", "skip", "move on", "next", "pass", "default", "you choose", "whatever", "doesn't matter"}


class InterpretResult(BaseModel):
    choice: str
    own_words_class: str | None = None
    own_words_text: str | None = None
    lines_and_veils: list[str] = Field(default_factory=list)
    picks: list[str] = Field(default_factory=list)  # several options named by number (multi-pick blocks)
    direct: bool = False  # mapped by the engine without a model call
    defaulted: bool = False  # the model failed twice: the block's default was taken (contracts/model-calls.md)
    answer: str | None = None  # with `details`: the model's short reply to the player's question


def _index(token: str, choices: Sequence[Choice]) -> str | None:
    t = token.strip().strip("().#").lower()
    if t.isdigit() and 1 <= int(t) <= len(choices):
        return choices[int(t) - 1].id
    if len(t) == 1 and t.isalpha() and ord(t) - 96 <= len(choices):
        return choices[ord(t) - 97].id
    return None


def direct_choice(message: str, choices: Sequence[Choice], *, multi: bool = False) -> list[str] | None:
    # rule: 12.2.6
    """The option(s) a typed number, lone letter, option id or exact label names; None when the words need
    reading. With `multi`, several numbers ("1, 3 and 4") name several options."""
    msg = message.strip()
    low = msg.lower().rstrip(".!")
    if low in _SKIP:
        return [MOVE_ON]
    for c in choices:
        if low == c.id.lower() or low == c.label.lower().strip():
            return [c.id]
    tokens = [t for t in _SPLIT.split(low) if t]
    if not tokens or (len(tokens) > 1 and not multi):
        return None
    picked = [_index(t, choices) for t in tokens]
    if any(p is None for p in picked):
        return None
    out: list[str] = []
    for p in picked:
        if p is not None and p not in out:
            out.append(p)
    return out


def interpret(ctx: TurnContext, message: str, *, choices: Sequence[Choice], block: str,
              classes: Sequence[str] = (), lines_and_veils: bool = False, cards: Sequence[str] = ("12.16.2",),
              exchanges: Sequence[Any] = (), multi: bool = False) -> InterpretResult:
    # rule: 12.16.2
    """Read the player's answer to one block. `choices` are the pause's choices as shown (numbered from 1);
    `classes` the own-words classification options (12.16.2, 02.2.4); `lines_and_veils` only at creation 1(b)."""
    hit = direct_choice(message, choices, multi=multi)
    if hit:
        return InterpretResult(choice=hit[0], picks=[h for h in hit if h not in SPECIAL_CHOICES], direct=True)
    options = [c.id for c in choices if c.id not in SPECIAL_CHOICES]
    sctx = SchemaContext(options=options, own_words_classes=list(classes), lines_and_veils=lines_and_veils)
    schema = build_schema(Role.INTERPRET, sctx)
    card_list = load_cards_for(Role.INTERPRET, extra_ids=[c for c in cards if c != "12.16.2"], rules=ctx.rules)
    shown = "\n".join(f"({i + 1}) {c.id}: {c.label}" for i, c in enumerate(choices))
    packet = build_packet(Role.INTERPRET, instructions=load_prompt("interpret"), cards=card_list,
                          view=f"options (number. id: label):\n{shown}", exchanges=[*exchanges, block],
                          message=message, rules=ctx.rules)
    res = call_role(ctx.model, Role.INTERPRET, schema, packet, turn_id=ctx.turn_id, recorder=ctx.record_call,
                    default=lambda: defaults(Role.INTERPRET, sctx) or {"choice": MOVE_ON})
    data = dict(res.data)
    choice = str(data.get("choice") or MOVE_ON)
    return InterpretResult(choice=choice, own_words_class=data.get("own_words_class"),
                           own_words_text=data.get("own_words_text"),
                           lines_and_veils=[str(x) for x in data.get("lines_and_veils") or []],
                           picks=[choice] if choice in options else [], defaulted=res.defaulted,
                           answer=(str(data["answer"]).strip() or None) if data.get("answer") else None)
