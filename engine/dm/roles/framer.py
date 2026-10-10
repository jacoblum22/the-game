"""The Framer role (A2; contracts/model-calls.md): ANCHOR and FRAME for one beat that rolls.

    propose = framer_for(ctx)                      # the pipeline's FramerFn
    proposed = propose(beat, candidates, gate=decision)          # a ProposedFrame frame_check accepts

The call's `check=` runs `frame_check` (PR-01-2) on the proposal, so a refusal is re-asked once naming the failed
step, then the rule's default frame applies (the basic verb's anchor, its default attribute, the defender's
defense for a social or attack beat, else class `other` at Easy; safe stakes, the first fitting cost by 01.13.1's
order). The Framer picks the obstacle class and at most one cited nudge; code computes the tier (01.6.5). A lethal claim refused only for want of a recorded lethal
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
from engine.dm.schemas import SchemaContext, build_schema, defaults, prune, schema_context
from engine.llm.base import Role, call_role
from engine.resolve.change import agreed_covers
from engine.resolve.costs import check_cost_decl
from engine.resolve.frame import frame_check
from engine.resolve.gate import GateDecision
from engine.resolve.necessity import trivial_class
from engine.resolve.types import Beat, CostDecl, Delta, LeverCite, Obstacle, ProposedFrame
from engine.retrieve.anchors import anchor_menu
from engine.retrieve.cards import TALK_CARD, anchor_card_ids, load_cards_for
from engine.retrieve.scene import focus_ids
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
    try:
        nudge = int(str(data.get("nudge") or "0").replace("+", ""))
    except ValueError:
        nudge = 0
    obstacle = Obstacle(kind=kind, tier=ob.get("tier") if kind == "tier" else None, entity=entity,
                        defense=defense, id=obstacle_id(beat) if kind == "tier" else None,
                        obstacle_class=ob.get("obstacle_class") if kind == "tier" else None,
                        nudge=nudge if kind == "tier" else 0, nudge_fact=data.get("nudge_fact"),
                        nudge_why=data.get("nudge_why"), request_size=data.get("request_size"))

    def cost(c: Any) -> CostDecl | None:
        if not c or not c.get("menu_id"):
            return None
        return CostDecl(menu_id=c["menu_id"], form_intent=c.get("form_intent") or "", source_fact=c.get("source_fact"))

    st = data.get("stakes") or data  # the paired `stakes` object; a record from before it had the three flat fields

    return ProposedFrame(
        anchor=data["anchor"], deltas=[Delta(**d) for d in data.get("deltas") or []],
        attribute=data["attribute"], deed_tag=data.get("deed_tag"), traits=list(data.get("traits") or []),
        obstacle=obstacle, levers=[LeverCite(fact_id=f) for f in data.get("levers") or []],
        snags=[LeverCite(fact_id=f) for f in data.get("snags") or []],
        stakes_source=st.get("source") or st.get("stakes_source") or NONE, stakes_heavy=bool(data.get("stakes_heavy")),
        lethal=bool(data.get("lethal")), reach_limit=data.get("reach_limit") or None,
        reach_two_factors=bool(data.get("reach_two_factors")),
        asks=str(data.get("asks") or NONE), threatened_cost=cost(st.get("threatened_cost")),
        alternate_cost=cost(st.get("alternate_cost")), method_consequences=list(data.get("method_consequences") or []),
        secret=bool(data.get("secret")), already_agreed=data.get("already_agreed") or None)


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
            d["stakes"] = {**(d.get("stakes") or {"source": NONE, "alternate_cost": None}), "threatened_cost": {"menu_id": m, "form_intent": "", "source_fact": None}}
            break
    return prune(d, schema)


def frame_texts(data: dict[str, Any]) -> list[str]:
    """The Framer's own words the OFFER shows: the two cost forms and the method's consequences."""
    st = data.get("stakes") or data
    out = [str((st.get(k) or {}).get("form_intent") or "") for k in ("threatened_cost", "alternate_cost")]
    return [t for t in [*out, *(str(x) for x in data.get("method_consequences") or [])] if t.strip()]


def pronoun_errors(data: dict[str, Any], state: WorldState, rules: Any) -> list[str]:  # rule: 12.3.2
    """12.3.2's pronoun precision check on the Framer's words (a re-ask, its redraft): a he/she that fits no one
    but the one person a text names (playtest 20261008-145430 fighter 28-29: "his weight" for Murzak, she/her;
    talker 21: "makes her unwelcome" for the PC beside Ysrion, he/him)."""
    from engine.audit.claims import precision_checks
    from engine.audit.declare import SceneIndex

    idx = SceneIndex.of(state)
    return [f"{t!r}: {h.why}; write the player's character as \"you\" (12.3.2)" for t in frame_texts(data)
            for h in precision_checks(t, idx=idx, rules=rules) if h.blocks]


def beat_message(beat: Beat, gate: GateDecision, note: str | None = None, state: WorldState | None = None) -> str:
    fallback = gate.mode == "fallback"  # 01.3.5 (DL-01-43): framed on its own scope, its shift added once by code
    lines = [f"beat: {beat.intent if fallback else beat.restatement or beat.intent}", f"intent: {beat.intent}",
             f"method: {beat.method}",
             f"gate: {gate.gate} ({gate.mode}) verb: {gate.verb or beat.verb or 'none'} "
             f"licence: {gate.license or 'none'}", f"target: {beat.target or 'none'}",
             f"against their will: {'yes' if beat.against_will else 'no'}"]
    c = beat.change
    if c is not None and c.kind != NONE:
        lines.append(f"goal: {c.kind} {' '.join(x for x in (c.what, c.whom, c.description) if x and x != NONE)}")
    if fallback:
        lines.append("an untrained fallback: rate only what this method itself can reach; code adds its shift")
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
        focus = focus_ids(st, beat.intent, beat.target)  # 12.2.4: the beat's target and whom it names rank higher
        sctx = schema_context(st, ctx.rules, anchors=candidates, beat=beat, message=beat.intent, focus=focus)
        schema = build_schema(Role.FRAMER, sctx)  # cost `source_fact` and the 01.6.1 `attribute` enum included
        triggers = get_active_triggers(st, ctx.rules)
        # 12.2.4 item 2: the cards code knows apply: the anchor candidates' and, on a Talk frame, 15.3.2 (request size)
        talk = [TALK_CARD] if (gate.verb or beat.verb) == "verb.talk" else []
        cards = load_cards_for(Role.FRAMER, triggers=triggers,
                               extra_ids=[*anchor_card_ids(candidates, ctx.rules), *talk], rules=ctx.rules)
        packet = build_packet(Role.FRAMER, instructions=load_prompt("framer"), cards=cards, view=st, exchanges=[],
                              message=beat_message(beat, gate, note, st), triggers=triggers,
                              notes=anchor_menu(candidates, ctx.rules), focus=focus, rules=ctx.rules)

        calls: list[bool] = []

        def check(data: Any) -> list[str]:  # rule: PR-01-2
            calls.append(True)
            try:
                p = to_proposed(data, beat, st)
            except (KeyError, ValueError) as e:
                return [f"malformed frame: {e}"]
            errs = []
            if p.obstacle.kind in ("opposed", "entity_defense") and not p.obstacle.entity:
                errs.append(f"obstacle kind {p.obstacle.kind} must set entity")
            if errs:
                return errs
            if trivial_class(p, ctx.rules, gate.verb or beat.verb) or agreed_covers(st, beat, p.already_agreed):
                return []  # a trivial class or an agreement on record: the pipeline resolves it without a roll
            out = frame_check(p, beat, state=st, rules=ctx.rules, gate=gate, candidates=candidates,
                              store=ctx.store, staged=ctx.need_tx().events)
            if hasattr(out, "step"):
                if getattr(out, "field", "") == "lethal" and "lethal_context" in getattr(out, "reason", ""):
                    return []  # the pipeline warns first (07.3.4)
                return [out.message]  # type: ignore[union-attr]
            # a pronoun slip is worth one redraft, never the default frame: raised on the first check only
            # ponytail: a schema failure on attempt 0 makes attempt 1 the first check; a slip there defaults
            return pronoun_errors(data, st, ctx.rules) if len(calls) == 1 else []

        res = call_role(ctx.model, Role.FRAMER, schema, packet, turn_id=ctx.turn_id, recorder=ctx.record_call,
                        default=lambda: default_frame(sctx, schema, beat, st, ctx.rules), check=check)
        return to_proposed(dict(res.data), beat, st)

    return propose
