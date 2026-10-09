"""The World role (W; contracts/model-calls.md): which recorded motive, if any, drives each present NPC's response
(12.2.9). The role never chooses what an NPC does; engine/dm/world_step.py rolls `tbl.npc_action` with its context.

    view = world_view(state)                         # narrator view + the present NPCs' wants and refusals
    responses = npc_responses(ctx, happened="Wren slipped past the watchman (success).")

Lead decision: the World role's view is the narrator view plus the present NPCs' wants and refusals (text and ids).
Wants are sealed from the narrator, not from the World role, which decides NPC responses.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from engine.dm.context import TurnContext
from engine.dm.packet import build_packet, turn_exchanges, view_ctx, view_for
from engine.dm.roles.prompts import load_prompt
from engine.dm.schemas import _want_ids, build_schema, defaults, schema_context
from engine.llm.base import Role, call_role
from engine.retrieve.cards import load_cards_for
from engine.retrieve.triggers import get_active_triggers
from engine.store.projection import WorldState

NONE = "none"


class WorldResponse(BaseModel):
    npc: str
    want_engaged: str | None = None  # "<npc>/want.<n>"
    refusal_engaged: str | None = None  # "<npc>/refusal.<n>"
    tags: list[str] = Field(default_factory=list)


def _text(x: Any) -> str:
    if isinstance(x, dict):
        return str(x.get("text") or x.get("want") or x.get("refusal") or x)
    return str(x)


def npc_motives(state: WorldState, npc: str) -> dict[str, str]:
    """{"<npc>/want.<n>": text, "<npc>/refusal.<n>": text} from the NPC's record (a later depth's fact first)."""
    e = state.entities.get(npc)
    if e is None:
        return {}
    out: dict[str, str] = {}
    for key, kind in (("wants", "want"), ("refusals", "refusal")):
        v = state.fact_value(npc, key)
        items = v if isinstance(v, list) else (e.data.get(key) or [])
        for i, item in enumerate(items):
            out[f"{npc}/{kind}.{i + 1}"] = _text(item)
    return out


def present_npcs(state: WorldState) -> list[str]:  # rule: 12.4.1
    """The scene's NPCs: those framed in it and anyone positioned at its place since (one met mid-scene answers
    too; P-056)."""
    from engine.world.scenes import cast_present

    return [i for i in cast_present(state) if state.entities[i].kind in ("npc", "companion")]


def world_view(state: WorldState, happened: str = "") -> str:  # rule: 12.2.9
    # rule: 12.2.4
    """The World row of 12.2.4's per-role views (the full selection plus scene cards; `happened`, this turn's
    words, picks the spotlight) plus each present NPC's standing toward the PC and recorded motives."""
    lines = [view_for(Role.WORLD, state, view_ctx(happened))]
    npcs = present_npcs(state)
    pc = next((eid for eid, e in state.entities.items() if e.kind == "pc"), None)
    if npcs:
        lines.append("NPC motives (sealed from the narrator; yours to weigh):")
    for n in npcs:
        rel = state.relationships.get(f"{n}|{pc}|standing")
        lines.append(f"  {n}: {state.entities[n].name}; standing toward the PC: "
                     f"{rel.value if rel else 'not yet met'}")
        lines.extend(f"    {k}: {v}" for k, v in npc_motives(state, n).items())
    return "\n".join(lines)


def world_check(data: Any) -> list[str]:  # rule: 12.2.9
    """A want or refusal must belong to its NPC; one entry per NPC."""
    errs: list[str] = []
    seen: set[str] = set()
    for i, r in enumerate(data.get("responses") or []):
        npc = r.get("npc")
        if npc in seen:
            errs.append(f"responses[{i}]: {npc} appears twice")
        seen.add(npc)
        for key in ("want_engaged", "refusal_engaged"):
            v = r.get(key)
            if v not in (None, NONE) and not str(v).startswith(f"{npc}/"):
                errs.append(f"responses[{i}].{key}: {v} is not one of {npc}'s")
    return errs


def npc_responses(ctx: TurnContext, happened: str,
                  only: dict[str, list[str]] | None = None) -> list[WorldResponse]:  # rule: 12.2.9
    """One World call; [] when no NPC is present. `only` ({npc: candidate motive ids}) restricts the call to judging
    those candidates (the default NPC layer's tie-breaker, 12.11.9; spec 006 R6)."""
    st = ctx.state
    sctx = schema_context(st, ctx.rules)
    npcs = present_npcs(st) if only is None else [n for n in only if n in st.entities]
    if not npcs:
        return []
    if only is not None:
        ids = [m for ms in only.values() for m in ms]
        sctx = sctx.model_copy(update={"npc_ids": npcs, "want_ids": [m for m in ids if "/want." in m],
                                       "refusal_ids": [m for m in ids if "/refusal." in m]})
    elif sctx.npc_ids != npcs:  # the schema's cast is the framed one; an NPC met mid-scene answers too (P-056)
        motives = [_want_ids(st, n) for n in npcs]
        sctx = sctx.model_copy(update={"npc_ids": npcs, "want_ids": [w for m in motives for w in m[0]],
                                       "refusal_ids": [r for m in motives for r in m[1]]})
    schema = build_schema(Role.WORLD, sctx)
    triggers = get_active_triggers(st, ctx.rules)
    cards = load_cards_for(Role.WORLD, triggers=triggers, rules=ctx.rules)
    packet = build_packet(Role.WORLD, instructions=load_prompt("world"), cards=cards, view=world_view(st, happened),
                          exchanges=turn_exchanges(ctx, 1), message=happened, triggers=triggers, rules=ctx.rules)
    res = call_role(ctx.model, Role.WORLD, schema, packet, turn_id=ctx.turn_id, recorder=ctx.record_call,
                    default=lambda: defaults(Role.WORLD, sctx) or {"responses": []}, check=world_check)
    out = []
    for r in dict(res.data).get("responses") or []:
        out.append(WorldResponse(
            npc=r["npc"],
            want_engaged=r.get("want_engaged") if r.get("want_engaged") not in (None, NONE) else None,
            refusal_engaged=r.get("refusal_engaged") if r.get("refusal_engaged") not in (None, NONE) else None,
            tags=list((r.get("table_context") or {}).get("tags") or [])))
    return out
