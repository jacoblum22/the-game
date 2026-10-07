"""The Checker role (C; contracts/model-calls.md C): extracts claims and screen flags from one draft. A separate call
with only its own prompt (FR-034): it never sees the Narrator's prompt, earlier drafts or reasoning.

    out = check_draft(ctx, "Tam Harlan steps aside. What do you do?", player_message="I wave him off.",
                      created=["npc.bessa_crane"])
    out.claims, out.screen        # Claims for engine.audit.claims.check_claims; flags for engine.audit.screen

THIS MESSAGE holds the draft with its sentences numbered from 0 (one per line, `[n] text`) and then the player's
message (lead decision). The view lists the ids a claim may name: the scene scope plus every id created this
turn, each as `<id>: <name>, <aliases>`; the PC as `pc.x: Name, you, your` so pronoun claims resolve.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Any

from pydantic import BaseModel, Field

from engine.audit.claims import Claim
from engine.dm.context import TurnContext
from engine.dm.packet import build_packet
from engine.dm.roles.prompts import load_prompt
from engine.dm.schemas import build_schema, schema_context
from engine.llm.base import Role, call_role
from engine.llm.offline import sentences as _sentences
from engine.retrieve.cards import load_cards_for
from engine.retrieve.scene import pc_id, scene_scope
from engine.store.projection import WorldState

ALIAS_KEYS = ("role", "aliases", "pronouns", "people", "detail")


class CheckerOutput(BaseModel):
    sentences: list[str] = Field(default_factory=list)
    claims: list[Claim] = Field(default_factory=list)
    screen: dict[str, Any] = Field(default_factory=dict)
    scene_ids: list[str] = Field(default_factory=list)
    call_id: str | None = None


def split_sentences(text: str) -> list[str]:  # rule: 12.3.1
    """The draft's sentences (quoted speech kept whole); numbered from 0 for the Checker."""
    return _sentences(text)


def checker_ids(state: WorldState, created: Iterable[str] = ()) -> list[str]:  # rule: 12.3.1
    """Every id a claim may name: the scene scope plus ids created this turn (that exist and are not sealed)."""
    out = list(scene_scope(state))
    for eid in created:
        if eid in state.entities and eid not in out and not (eid in state.seals and not state.seals[eid].slice):
            out.append(eid)
    return out


def entity_lines(state: WorldState, ids: Sequence[str]) -> list[str]:  # rule: 12.3.1
    """`<id>: <name>, <aliases>` per id; the PC as `pc.x: Name, you, your`. Sealed entities show only their slice."""
    pc = pc_id(state)
    lines: list[str] = []
    for eid in ids:
        e = state.entities.get(eid)
        if e is None:
            continue
        seal = state.seals.get(eid)
        if seal is not None:
            lines.append(f"{eid}: {seal.slice}")
            continue
        names = [e.name]
        if eid == pc:
            names += ["you", "your"]
        for k in ALIAS_KEYS:
            v = e.data.get(k)
            vals = v if isinstance(v, list) else [v]
            names += [str(x) for x in vals if isinstance(x, str) and x]
        lines.append(f"{eid}: " + ", ".join(dict.fromkeys(n for n in names if n)))
    return lines


def checker_message(sents: Sequence[str], player_message: str) -> str:  # rule: 12.3.1
    """The draft's sentences `[n] text` first, then the player's message (12.14.3's comparison)."""
    lines = [f"[{i}] {s}" for i, s in enumerate(sents)]
    lines.append("")
    lines.append(f'THE PLAYER\'S MESSAGE: "{player_message}"' if player_message else "THE PLAYER'S MESSAGE: (none)")
    return "\n".join(lines)


def check_draft(ctx: TurnContext, fiction: str, *, player_message: str = "", created: Iterable[str] = (),
                exchanges: Sequence[str | tuple[str, str]] = ()) -> CheckerOutput:  # rule: PR-12-2
    """One Checker call: the claims (12.3.1) and the screen flags. Raises ModelInvalid after a failed re-ask."""
    st = ctx.state
    sents = split_sentences(fiction)
    ids = checker_ids(st, created)
    sctx = schema_context(st, ctx.rules, draft_sentences=sents)
    sctx.scene_ids = ids
    schema = build_schema(Role.CHECKER, sctx)
    cards = load_cards_for(Role.CHECKER, (), None, (), rules=ctx.rules)
    packet = build_packet(Role.CHECKER, instructions=load_prompt("checker"), cards=cards,
                          view="\n".join(entity_lines(st, ids)), exchanges=list(exchanges),
                          message=checker_message(sents, player_message), rules=ctx.rules)
    res = call_role(ctx.model, Role.CHECKER, schema, packet, turn_id=ctx.turn_id, recorder=ctx.record_call)
    data = dict(res.data)
    claims = [Claim.model_validate(c) for c in data.get("claims") or [] if int(c.get("sentence", 0)) < len(sents)]
    return CheckerOutput(sentences=sents, claims=claims, screen=dict(data.get("screen") or {}), scene_ids=ids,
                         call_id=res.record.call_id)


__all__ = ["CheckerOutput", "check_draft", "checker_ids", "checker_message", "entity_lines", "split_sentences"]
