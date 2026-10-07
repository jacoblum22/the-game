"""The Director role (S; contracts/model-calls.md S): scene structure from closed lists (12.4, PR-12-7, 12.6–12.8).

    d = direct(ctx, situation="scene start", player_message="I go looking for the ferryman.")
    d.cut_now, d.next_scene.place, d.push, d.lead
    start = frame_scene(ctx, d, reason="player_cut")    # move (places.move) / end_scene, then start_scene

Runs at scene start (a pending frame or no scene), when a cut may be due or the player moves on, and when
`trg.pacing_push` or `trg.lead_injection` is raised. Enums come from `engine.world.scenes.director_enums`;
scene tests, tension and every roll are code (`h.12.*`).
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from engine.dm.context import TurnContext
from engine.dm.packet import WATCHES, build_packet
from engine.dm.roles.prompts import load_prompt
from engine.dm.schemas import NONE, SchemaContext, build_schema, defaults, schema_context
from engine.llm.base import Role, call_role
from engine.retrieve.anchors import scene_situation_tags
from engine.retrieve.cards import load_cards_for
from engine.retrieve.triggers import get_active_triggers
from engine.store.projection import WorldState
from engine.world.common import WorldError
from engine.world.scenes import SceneStart, director_enums


class NextScene(BaseModel):
    mode: str | None = None
    place: str | None = None
    agenda: str = ""
    hoped_answer: str = ""
    pillar: str | None = None
    challenge_type: str | None = None
    cast: list[str] = Field(default_factory=list)


class DirectorDecision(BaseModel):
    cut_now: bool = False
    next_scene: NextScene = Field(default_factory=NextScene)
    push: str | None = None
    lead: dict[str, Any] | None = None
    push_raised: bool = False
    lead_fires: bool = False


def director_context(state: WorldState, rules: Any) -> SchemaContext:  # rule: 12.4.2
    """`schema_context` with the Director's enums from `director_enums` (places reachable or current, ...)."""
    enums = director_enums(state, rules)
    sctx = schema_context(state, rules, places=enums["places"], push_raised=enums["push_raised"],
                          lead_fires=enums["lead_fires"])
    upd = {k: v for k, v in enums.items() if k in SchemaContext.model_fields}
    return sctx.model_copy(update=upd)


def direct(ctx: TurnContext, *, situation: str, player_message: str = "", happened: str = "",
           quiet_turns: int | None = None) -> DirectorDecision:  # rule: PR-12-7
    """One Director call. `situation`: what the engine raised (scene start, a possible cut, a push, a lead)."""
    st = ctx.state
    sctx = director_context(st, ctx.rules)
    schema = build_schema(Role.DIRECTOR, sctx)
    triggers = get_active_triggers(st, ctx.rules)
    mode = st.scene.mode if st.scene else None
    cards = load_cards_for(Role.DIRECTOR, scene_situation_tags(st, ctx.rules), mode, triggers, rules=ctx.rules)
    msg = [f"RAISED: {situation}"]
    if happened:
        msg.append(f"THIS TURN: {happened}")
    msg.append(f'THE PLAYER\'S MESSAGE: "{player_message}"' if player_message else "THE PLAYER'S MESSAGE: (none)")
    packet = build_packet(Role.DIRECTOR, instructions=load_prompt("director"), cards=cards, view=st,
                          exchanges=[], message="\n".join(msg), triggers=triggers, quiet_turns=quiet_turns,
                          rules=ctx.rules)
    res = call_role(ctx.model, Role.DIRECTOR, schema, packet, turn_id=ctx.turn_id, recorder=ctx.record_call,
                    default=lambda: defaults(Role.DIRECTOR, sctx) or {"cut_now": False, "next_scene": {}})
    d = dict(res.data)
    ns = dict(d.get("next_scene") or {})
    ns["cast"] = [c for c in ns.get("cast") or [] if isinstance(c, str)]
    push = d.get("push")
    return DirectorDecision(cut_now=bool(d.get("cut_now")), next_scene=NextScene.model_validate(ns),
                            push=push if push not in (None, NONE) else None, lead=d.get("lead") or None,
                            push_raised=bool(sctx.push_options), lead_fires=bool(sctx.lead_routes))


def scene_header(state: WorldState) -> str:  # rule: 12.4.3
    """The scene header in words (place, time of day), for the record and the plain fallback."""
    sc = state.scene
    place = state.entities.get(sc.place_id) if sc and sc.place_id else None
    watch = state.time.now.watch
    when = WATCHES[watch] if 0 <= watch < len(WATCHES) else ""
    return ", ".join(x for x in (place.name if place else "", when) if x)


def frame_scene(ctx: TurnContext, d: DirectorDecision, *, reason: str, interrupt: bool = False,
                purpose_declared: bool = False) -> SceneStart:  # rule: PR-12-7
    """Close the current scene if still open (a move to another reachable place goes through
    `engine.world.places.move`, which ends it with `place_change`), then `start_scene` from `d.next_scene`."""
    from engine.world.places import location, move, reachable
    from engine.world.scenes import end_scene, start_scene

    tctx = ctx.time_ctx()
    st = ctx.state
    ns = d.next_scene
    here = location(st)
    if ns.place and here and ns.place != here and any(r.to == ns.place for r in reachable(st, here)):
        arrival = move(tctx, ns.place, end_scene=True)
        interrupt = interrupt or not arrival.arrived
    if ctx.state.scene is not None:
        end_scene(tctx, reason)
    st = ctx.state
    place = location(st) or ns.place or (st.last_scene.place_id if st.last_scene else None)
    previous = st.last_scene.mode if st.last_scene else None
    mode = ns.mode or previous or "free"
    cast = [c for c in ns.cast if c != "new_npc" and c in st.entities]  # TODO(new_npc): PR-12-5 generation
    try:
        return start_scene(tctx, place=place, mode=mode, agenda=ns.agenda, hoped_answer=ns.hoped_answer,
                           pillar=ns.pillar, challenge_type=ns.challenge_type, cast=cast, interrupt=interrupt,
                           purpose_declared=purpose_declared)
    except WorldError:
        return start_scene(tctx, place=place, mode="free", agenda=ns.agenda, hoped_answer=ns.hoped_answer,
                           cast=cast, interrupt=interrupt, purpose_declared=purpose_declared)


__all__ = ["DirectorDecision", "NextScene", "direct", "director_context", "frame_scene", "scene_header"]
