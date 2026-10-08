"""The Framer role (A2; contracts/model-calls.md): ANCHOR and FRAME for one beat that rolls.

    propose = framer_for(ctx)                      # the pipeline's FramerFn
    proposed = propose(beat, candidates, gate=decision)          # a ProposedFrame frame_check accepts

The call's `check=` runs `frame_check` (PR-01-2) on the proposal, so a refusal is re-asked once naming the failed
step, then the rule's default frame applies (the basic verb's anchor, its default attribute, a Moderate tier,
safe stakes, the first fitting cost by 01.13.1's order). A lethal claim refused only for want of a recorded lethal
context passes the check: the pipeline then gives the lethal warning first (07.3.4).

Schema seam (lead decision (a)): `engine.dm.schemas.framer_schema` gives the cost objects a nullable `source_fact`
enum of the scene's fact ids, so a cost can cite its source (without one, `frame_check` needs the state to fit it
structurally), and builds the `attribute` enum per 01.6.1 (knobs, the verb's attributes, the licence's).
"""

from __future__ import annotations

from typing import Any

from engine import ids
from engine.dm.context import TurnContext
from engine.dm.packet import build_packet
from engine.dm.roles.prompts import load_prompt
from engine.dm.schemas import SchemaContext, build_schema, defaults, schema_context
from engine.llm.base import Role, call_role
from engine.resolve.costs import check_cost_decl, uncited_by_stakes
from engine.resolve.frame import frame_check
from engine.resolve.gate import GateDecision
from engine.resolve.types import Beat, CostDecl, Delta, LeverCite, Obstacle, ProposedFrame
from engine.retrieve.anchors import anchor_menu, scene_situation_tags
from engine.retrieve.cards import anchor_card_ids, load_cards_for
from engine.retrieve.triggers import get_active_triggers
from engine.store.projection import WorldState

NONE = "none"
Schema = dict[str, Any]


def obstacle_id(beat: Beat) -> str:
    """The obstacle's identity for its stored DC (01.6.5): the target, else the intent's words."""
    return beat.target if beat.target and beat.target != NONE else ids.slug(beat.intent)[:40]


def to_proposed(data: dict[str, Any], beat: Beat, state: WorldState) -> ProposedFrame:
    """FramerOutput → ProposedFrame (bare lever fact ids read as Precision; lead decision (b))."""
    ob = data.get("obstacle") or {}
    kind = ob.get("kind") or "tier"
    entity = ob.get("entity")
    defense = None
    if kind == "entity_defense" and entity in state.entities:  # the entity's named defense (01.6.4)
        defense = next(iter(state.entities[entity].data.get("defenses") or {}), None)
    obstacle = Obstacle(kind=kind, tier=ob.get("tier") if kind == "tier" else None, entity=entity,
                        defense=defense, id=obstacle_id(beat) if kind == "tier" else None)

    def cost(c: Any) -> CostDecl | None:
        if not c or not c.get("menu_id"):
            return None
        return CostDecl(menu_id=c["menu_id"], form_intent=c.get("form_intent") or "", source_fact=c.get("source_fact"))

    return ProposedFrame(
        anchor=data["anchor"], deltas=[Delta(**d) for d in data.get("deltas") or []],
        attribute=data["attribute"], deed_tag=data.get("deed_tag"), traits=list(data.get("traits") or []),
        obstacle=obstacle, levers=[LeverCite(fact_id=f) for f in data.get("levers") or []],
        snags=[LeverCite(fact_id=f) for f in data.get("snags") or []],
        stakes_source=data.get("stakes_source") or NONE, stakes_heavy=bool(data.get("stakes_heavy")),
        lethal=bool(data.get("lethal")), reach_whole=bool(data.get("reach_whole")),
        reach_one_factor=bool(data.get("reach_one_factor")), threatened_cost=cost(data.get("threatened_cost")),
        alternate_cost=cost(data.get("alternate_cost")), method_consequences=list(data.get("method_consequences") or []),
        secret=bool(data.get("secret")))


def default_frame(sctx: SchemaContext, schema: Schema, beat: Beat, state: WorldState, rules: Any) -> dict[str, Any]:
    # rule: 01.13.1
    """The rule's default frame, with the threatened cost the first entry (01.13.1 tie order) that fits."""
    d: dict[str, Any] = dict(defaults(Role.FRAMER, sctx) or {})
    if not d.get("attribute"):
        d["attribute"] = schema["properties"]["attribute"]["enum"][0]
    order = [m for m in dict.fromkeys([*sctx.cost_tie_order, *sctx.cost_menu_ids]) if m in sctx.cost_menu_ids]
    for m in order:
        why = check_cost_decl(CostDecl(menu_id=m), role="threatened", state=state, rules=rules, actor=beat.actor,
                              stakes_source=NONE, target=beat.target, declared_seq=beat.declared_seq or None)
        if why is None:
            d["threatened_cost"] = {"menu_id": m, "form_intent": ""}
            break
    if "source_fact" in str(schema["properties"].get("threatened_cost")):
        d["threatened_cost"] = {**d["threatened_cost"], "source_fact": None}
    return d


def cost_note(beat: Beat, state: WorldState, rules: Any) -> str:  # rule: PR-01-2
    """Step 10 in words where the schema cannot pair two fields: which stakes sources let a cost go uncited."""
    tgt = beat.target if beat.target and beat.target != NONE else None
    by = uncited_by_stakes(state=state, rules=rules, actor=beat.actor, target=tgt)
    need = {m: [s for s, ms in by.items() if m in ms] for m in dict.fromkeys(m for ms in by.values() for m in ms)
            if m not in by[NONE] and m != "cost.twist"}
    lines = [f"{m} needs stakes_source {' or '.join(ss)}" for m, ss in need.items()]
    lines.append("cost.twist only with stakes_source none" if "cost.twist" in by[NONE] else "cost.twist: never")
    return "costs without a source_fact: " + "; ".join(lines)


def beat_message(beat: Beat, gate: GateDecision, note: str | None = None) -> str:
    lines = [f"beat: {beat.restatement or beat.intent}", f"intent: {beat.intent}", f"method: {beat.method}",
             f"gate: {gate.gate} ({gate.mode}) verb: {gate.verb or beat.verb or 'none'} "
             f"licence: {gate.license or 'none'}", f"target: {beat.target or 'none'}"]
    if beat.assertion:
        lines.append(f"assertion (context only, never a fact): {beat.assertion}")
    if note:
        lines.append(note)
    return "\n".join(lines)


def framer_for(ctx: TurnContext) -> Any:
    """The pipeline's `FramerFn` over this turn's context."""

    def propose(beat: Beat, candidates: list[str], *, gate: GateDecision, note: str | None = None) -> ProposedFrame:
        # rule: 01.5.1
        st = ctx.state
        sctx = schema_context(st, ctx.rules, anchors=candidates, beat=beat, message=beat.intent)
        schema = build_schema(Role.FRAMER, sctx)  # cost `source_fact` and the 01.6.1 `attribute` enum included
        triggers = get_active_triggers(st, ctx.rules)
        mode = st.scene.mode if st.scene else None
        cards = load_cards_for(Role.FRAMER, scene_situation_tags(st, ctx.rules), mode, triggers,
                               anchor_card_ids(candidates, ctx.rules), rules=ctx.rules)
        packet = build_packet(Role.FRAMER, instructions=load_prompt("framer"), cards=cards, view=st, exchanges=[],
                              message=beat_message(beat, gate, "\n".join(filter(None, [note, cost_note(
                                  beat, st, ctx.rules)]))), triggers=triggers,
                              notes=anchor_menu(candidates, ctx.rules), rules=ctx.rules)

        def check(data: Any) -> list[str]:  # rule: PR-01-2
            try:
                p = to_proposed(data, beat, st)
            except (KeyError, ValueError) as e:
                return [f"malformed frame: {e}"]
            errs = []
            if p.obstacle.kind in ("opposed", "entity_defense") and not p.obstacle.entity:
                errs.append(f"obstacle kind {p.obstacle.kind} must set entity")
            if errs:
                return errs
            out = frame_check(p, beat, state=st, rules=ctx.rules, gate=gate, candidates=candidates,
                              store=ctx.store, staged=ctx.need_tx().events)
            if hasattr(out, "step"):
                if getattr(out, "field", "") == "lethal" and "lethal_context" in getattr(out, "reason", ""):
                    return []  # the pipeline warns first (07.3.4)
                return [out.message]  # type: ignore[union-attr]
            return []

        res = call_role(ctx.model, Role.FRAMER, schema, packet, turn_id=ctx.turn_id, recorder=ctx.record_call,
                        default=lambda: default_frame(sctx, schema, beat, st, ctx.rules), check=check)
        return to_proposed(dict(res.data), beat, st)

    return propose
