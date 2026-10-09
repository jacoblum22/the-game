"""FRAME and OFFER computations (01.6, 01.7; PR-00-1 assembling a check; PR-01-2 `frame_check`).

    out = frame_check(proposed, beat, state=tx.state, rules=rules, gate=decision, candidates=anchor_ids)
    if isinstance(out, FrameRefusal): re-ask the Framer once with out.message
    view = offer_preview(out)                       # what 01.7.1 shows; never model text
    events = commit_events(out, "commit", mint=tx.mint, state=tx.state)   # stored DC + frame_committed

The model proposes (anchor, deltas, attribute, obstacle kind, levers, stakes and reach flags, costs); the engine
validates every id against state and data and computes the DC, modifier, odds and cost previews (INV-3).
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable, Sequence
from typing import Any, cast

from engine import ids
from engine.resolve.costs import (
    OBSERVER,
    check_cost_decl,
    established_stakes_sources,
    first_fitting_cost,
    severity_previews,
)
from engine.resolve.gate import GateDecision, check_gate
from engine.resolve.odds import odds
from engine.resolve.rulings import find_rulings, signature
from engine.resolve.types import (
    REACH_LADDER,
    STAKES_LADDER,
    Alternative,
    Beat,
    CostPreview,
    Frame,
    FrameRefusal,
    GateRecord,
    LeverCite,
    ModePrice,
    Modifier,
    Odds,
    OfferChoice,
    OfferPreview,
    ProposedFrame,
    ReachRung,
    StakesRung,
)
from engine.store.events import WORLD, Event

FREE_FACTS_KEY = "oracle.free_facts"
LETHAL_CONTEXT = "lethal_context"  # fact predicate recorded by the lethal warning (07; harm module)
FREE_FACT_ROLLS_PER_SCENE = 2  # 01.15.8 (b)
FREE_FACT_LEVERS_PER_ROLL = 1  # 01.15.8 (a)
LETHAL_COSTS = ("cost.harm", "cost.footing")  # 01.6.9 decision 3


class _Refuse(Exception):
    def __init__(self, step: int, field: str, reason: str) -> None:
        super().__init__(reason)
        self.refusal = FrameRefusal(step=step, field=field, reason=reason)


def _caps(rules: Any) -> Any:
    return rules.scales["check_modifier"]["caps"]


def _clamp(v: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, v))


# ------------------------------------------------------------------------------------------- lookups


def resolve_anchor(rules: Any, anchor: str) -> Any:  # rule: 01.5.1
    """An anchor card by `anc.*` id, or a basic verb id read as that verb's card."""
    if anchor in rules.anchors:
        return rules.anchor(anchor)
    for a in rules.anchors.values():
        if a.get("verb") == anchor and a.get("specificity") == "verb_card":
            return a
    raise _Refuse(3, "anchor", f"unknown anchor {anchor!r}")


def tag_chain(rules: Any, tag: str | None) -> list[str]:
    """The tag and its ancestors, ending at the root `deed`."""
    out: list[str] = []
    t = tag
    while t and t not in out:
        out.append(t)
        t = (rules.tags.get(t) or {}).get("parent")
    if "deed" not in out:
        out.append("deed")
    return out


def _competence_map(ent: Any) -> dict[str, int]:
    comp = ent.data.get("competence") or {}
    if isinstance(comp, dict):
        return {str(k): int(v) for k, v in comp.items()}
    return {str(c["tag"]): int(c["value"]) for c in comp if isinstance(c, dict) and "tag" in c}


def competence(rules: Any, ent: Any, tag: str | None) -> tuple[int, str | None]:  # rule: 00.3.6
    """The highest competence among the tag and its ancestors; a PC holds the floor at `deed`."""
    comp = _competence_map(ent)
    caps = _caps(rules)
    if ent.kind == "pc":
        floor = caps["competence_floor_pc"]
        comp[floor["tag"]] = max(comp.get(floor["tag"], 0), int(floor["value"]))
    best, best_tag = 0, None
    for t in tag_chain(rules, tag):
        if comp.get(t, 0) > best:
            best, best_tag = comp[t], t
    return min(best, int(caps["competence"]["max"])), best_tag


def attribute_value(ent: Any, attr: str) -> int:
    return int((ent.data.get("attributes") or {}).get(attr, 0))


_ATOM = re.compile(r"^(any|severity (is|in) .+|attribute (is|in) .+|verb (is|in) .+|the beat has trait\.[a-z_.]+)$")


def _atom_true(atom: str, sev: str, attr: str, verb: str | None, traits: Sequence[str]) -> bool | None:
    a = atom.strip()
    if a.startswith("per stack"):
        return True
    if not _ATOM.match(a):
        return None
    if a == "any":
        return True
    vals = re.findall(r"[A-Za-z0-9_.]+", a.split(" is ", 1)[-1] if " is " in a else a.split(" in ", 1)[-1])
    if a.startswith("severity"):
        return sev in vals
    if a.startswith("attribute"):
        return attr in vals
    if a.startswith("verb"):
        return verb in vals
    return a.split("has ", 1)[1] in traits


def status_applies(applies_when: str, sev: str, attr: str, verb: str | None,
                   traits: Sequence[str]) -> bool | None:  # rule: PR-00-1
    """Evaluate a status modifier's `applies_when` for the simple forms; None when it needs judgment."""
    atoms = [x for part in applies_when.split(";") for x in part.split(" and ")]
    results = [_atom_true(x, sev, attr, verb, traits) for x in atoms if x.strip()]
    if any(r is False for r in results):
        return False
    if any(r is None for r in results):
        return None
    return True


def status(rules: Any, state: Any, who: str, attr: str, verb: str | None, traits: Sequence[str],
           notes: list[str]) -> int:  # rule: PR-00-1
    """Step 5: the worst penalty (cap -4) and the best bonus (cap +2) of the active conditions."""
    caps = _caps(rules)["status"]
    worst, best = 0, 0
    for inst in state.conditions_on(who):
        try:
            cond = rules.condition(inst.condition_id)
        except Exception:  # noqa: BLE001
            continue
        for m in cond.get("modifies") or ():
            if m.get("effect_id") != "eff.status_modifier":
                continue
            prm = m.get("params") or {}
            ok = status_applies(str(prm.get("applies_when", "any")), inst.severity, attr, verb, traits)
            if ok is None:
                notes.append(f"status: {inst.condition_id} applies when {prm.get('applies_when')!r} (needs judgment)")
                continue
            if ok:
                amt = int(prm.get("amount", 0)) * (inst.stacks if "per stack" in str(prm.get("applies_when")) else 1)
                worst, best = min(worst, amt), max(best, amt)
    return max(int(caps["worst_penalty"]), worst) + min(int(caps["best_bonus"]), best)


def lethal_context_recorded(state: Any, declared_seq: int) -> bool:  # rule: 00.3.14
    """A `lethal_context` fact (the lethal warning, 07) established before the declaration."""
    return any(f.predicate == LETHAL_CONTEXT and f.value and f.valid_from_seq <= declared_seq
               for f in state.facts.values())


def fact_usable(state: Any, fact_id: str, declared_seq: int) -> bool:  # rule: PR-01-2
    """Step 7 (and step 3's cited facts): the fact exists and was established before the declaration."""
    f = state.facts.get(fact_id)
    return f is not None and f.valid_from_seq <= declared_seq


def rolling_tiers(rules: Any) -> list[str]:  # rule: T-01-2
    """The DC tiers that roll (a tier with no DC is no-roll or G4; step 6 refuses it)."""
    return [t["id"] for t in rules.resolution["dc_tiers"] if t.get("dc") is not None]


def stored_dc_key(obstacle: str, anchor: str, dc_delta: str | None = None) -> str:  # rule: 01.6.5
    """resolution.yaml#dc_tier_rules.stored_key: dc.<obstacle_id>.<anchor_id>[+dc:<delta>]."""
    return f"dc.{obstacle}.{anchor}" + (f"+dc:{dc_delta}" if dc_delta else "")


def verb_classes(rules: Any, verb: str | None) -> dict[str, str]:  # rule: 01.6.5
    """The verb card's obstacle classes and their base tiers (`basic_verbs.yaml` anchor.obstacle_classes; T-00-5's
    rubric column). A class whose base is not a tier (`by_hazard`) is left to `other`."""
    tiers = {t["id"] for t in rules.resolution["dc_tiers"]}
    entry = rules.basic_verbs.get(verb or "") or {}
    return {str(c["id"]): str(c["base"]) for c in (entry.get("anchor") or {}).get("obstacle_classes") or ()
            if str(c.get("base")) in tiers}


OPPOSED_VERBS = ("verb.talk", "verb.strike", "verb.grapple", "verb.force", "verb.setup")  # aimed at a person
PEOPLE = ("npc", "companion", "adversary", "pc")


def opposed_by(state: Any, beat: Beat, verb: str | None) -> list[str]:  # rule: 01.6.4
    """A social or attack beat aimed at a person is resisted by that person's defense, never a tier (00.3.8 source
    2, mandatory; 15.3.3 for talk)."""
    tgt = beat.target
    ent = state.entities.get(tgt or "")
    return [str(tgt)] if verb in OPPOSED_VERBS and ent is not None and ent.kind in PEOPLE and tgt != beat.actor else []


def _verb_entry(rules: Any, anchor: Any, beat: Beat) -> Any | None:
    v = anchor.get("verb") or beat.verb
    return rules.basic_verbs.get(v) if v else None


# ------------------------------------------------------------------------------------------- frame_check


def frame_check(proposed: ProposedFrame, beat: Beat, *, state: Any, rules: Any, gate: GateDecision | None = None,
                candidates: Iterable[str] | None = None, store: Any = None,
                staged: Sequence[Event] = ()) -> Frame | FrameRefusal:  # rule: PR-01-2
    """Validate the proposal and compute the frame (PR-00-1 inside), or refuse naming the failed step."""
    try:
        return _frame_check(proposed, beat, state, rules, gate, candidates, store, staged)
    except _Refuse as r:
        return r.refusal


def _frame_check(p: ProposedFrame, beat: Beat, state: Any, rules: Any, gate: GateDecision | None,
                 candidates: Iterable[str] | None, store: Any, staged: Sequence[Event]) -> Frame:  # rule: PR-01-2
    notes: list[str] = []
    declared = beat.declared_seq or state.last_seq
    limits = rules.resolution["limits"]
    # 1. the beat
    actor = state.entities.get(beat.actor)
    if actor is None:
        raise _Refuse(1, "beat.actor", f"unknown actor {beat.actor!r}")
    if beat.target and beat.target != "none" and beat.target not in state.entities:
        raise _Refuse(1, "beat.target", f"target {beat.target!r} is not a resolved entity id")
    if not beat.intent.strip() or not beat.method.strip():
        raise _Refuse(1, "beat", "the beat needs an intent and a method")
    # 2. the gate, and the mode price read from the license entry
    g = gate or check_gate(beat, state=state, rules=rules)
    if not g.rolls_possible:
        raise _Refuse(2, "gate", f"gate {g.gate} does not roll: {g.reason}")
    price = _mode_price(g, state, beat, rules)
    # 3. anchor and deltas
    anchor = resolve_anchor(rules, p.anchor)
    cands = list(candidates) if candidates is not None else None
    if cands is not None and anchor["id"] not in cands and p.anchor not in cands:
        raise _Refuse(3, "anchor", f"{anchor['id']} is not among the candidate anchors")
    deltas = _check_deltas(p, anchor, state, declared, int(limits["anchor_knob_changes"]))
    sig = signature(anchor["id"], deltas)
    found = find_rulings(store, sig, staged=staged) if deltas else []
    # 4. attribute (lower on a tie)
    attr, alt_attr = _check_attribute(p, anchor, beat, g, rules, actor, deltas)
    # 5. deed tag and competence
    if p.deed_tag and p.deed_tag != "deed" and p.deed_tag not in rules.tags:
        raise _Refuse(5, "deed_tag", f"unknown deed tag {p.deed_tag!r}")
    deed = p.deed_tag or beat.deed_tag
    comp, comp_tag = competence(rules, actor, deed)
    lift = lift_or_carry(rules, beat)  # DL-01-35: the one exception to the lower on a tie
    if lift is not None:
        attr, alt_attr = lift_attribute(lift, rules, state, beat, actor, attr, comp), None
    # 6. DC (stored, opposed, effect, rubric tier) plus the mode's dc_shift
    verb = g.verb or beat.verb or anchor.get("verb")
    dc, dc_source, tier, defender, stored_write = _dc(p, anchor, deltas, state, rules, notes, beat=beat, verb=verb,
                                                     declared=declared)
    if price is not None:
        dc += price.dc_shift
    # 7. levers and snags (at most one cited Precision snag: a further one is Protective, 00.3.9(b))
    levers, snags, circ = _levers(p, beat, state, rules, declared, limits)
    free = set(state.meta.get(FREE_FACTS_KEY, []))
    # 8. stakes and lethal
    stakes, lethal = _stakes(p, levers, snags, free, state, rules, declared)
    # rule: 01.6.9
    cited_party = p.stakes_source == OBSERVER and any(c is not None and c.source_fact for c in (
        p.threatened_cost, p.alternate_cost))  # the party named by a fact on record (guards awake on the wall)
    if p.stakes_source not in established_stakes_sources(state, rules, beat.actor, beat) and not cited_party:
        raise _Refuse(8, "stakes_source", f"{p.stakes_source}: not established (a running clock; a party who would "
                                          "act on a failure, present or cited by a cost's source fact, 01.4.1)")
    # 9. reach
    reach, factors = _reach(p, levers, snags, stakes, price)
    # 11. modifier
    caps = _caps(rules)
    a_val = attribute_value(actor, attr)
    edge = min(int(caps["edge"]["max"]), int(actor.data.get("edge", 0) or 0))
    st = status(rules, state, beat.actor, attr, beat.verb or anchor.get("verb"), p.traits or beat.traits, notes)
    base_max = int(caps["base_pc"]["max"] if actor.kind == "pc" else caps["base_non_pc"]["max"])
    base = min(base_max, a_val + comp + edge)
    lo, hi = int(caps["total"]["min"]), int(caps["total"]["max"])
    # 12. odds, and the critical-failure guard (01.6.13) before the costs, since it can raise the stakes
    o = odds(_clamp(base + circ + st, lo, hi), dc)
    guard, long_shot = None, False
    if _guarded(stakes, dc_source, p.secret) and o.critical_failure > max(5, o.success_or_better):
        snag = next((s for s in snags if s.type == "precision" and not s.engine), None)
        if snag is not None:  # rule: 01.6.13
            snags = [s.model_copy(update={"type": "protective"}) if s is snag else s for s in snags]
            circ = _clamp(circ + int(_caps(rules)["circumstance"]["lever_value"]), int(caps["circumstance"]["min"]),
                          int(caps["circumstance"]["max"]))
            stakes = cast(StakesRung, _step(STAKES_LADDER, stakes, 1))  # the guard's rung never sets lethal
            guard = f"{snag.fact_id} applies as Protective (critical-failure guard, 01.6.13)"
            o = odds(_clamp(base + circ + st, lo, hi), dc)
        long_shot = _guarded(stakes, dc_source, p.secret) and o.critical_failure > max(5, o.success_or_better)
    # 10. costs (with the final stakes); stakes the engine raised (a Protective snag, the guard) above a declared
    # Safe frame get the rule's first fitting alternate (01.13.1), since a Safe frame declares none
    if stakes != "safe" and p.alternate_cost is None and (guard or p.stakes_source == "none"):
        p = p.model_copy(update={"alternate_cost": first_fitting_cost(
            rules, role="alternate", other=p.threatened_cost, state=state, actor=beat.actor,
            stakes_source=p.stakes_source, target=beat.target if beat.target != "none" else None,
            declared_seq=declared)})
    tc, ac = _costs(p, beat, state, rules, stakes, declared)
    total = _clamp(base + circ + st, lo, hi)
    mod = Modifier(attribute=a_val, competence=comp, competence_tag=comp_tag, edge=edge, circumstance=circ,
                   status=st, total=total)
    base_odds = odds(_clamp(base + st, lo, hi), dc).success_or_better
    if o.only_natural_20:
        notes.append("only a natural 20, and at best a plain success")
    alts = alternatives(rules, state, actor, verb=verb, attribute=attr, comp=comp, edge=edge, circ=circ, status=st,
                        dc=dc, defender=defender, dc_source=dc_source,
                        attrs=list(lift["allowed"]) if lift is not None else None)
    consequences = list(p.method_consequences)
    if price is not None and price.consequence and price.consequence not in consequences:
        consequences.append(price.consequence)
    return Frame(beat=beat, gate=GateRecord.model_validate({"class": g.gate, "verb": g.verb or beat.verb,
                                                                   "license": g.license, "mode": g.mode}),
                 secret=p.secret, anchor=anchor["id"], deltas=deltas, signature=sig,
                 precedent=found[-1].id if found else None, attribute=attr, alternative_attribute=alt_attr,
                 deed_tag=deed, traits=list(p.traits or beat.traits), obstacle_id=p.obstacle.id, dc_source=dc_source,
                 tier=tier, defender=defender, dc=dc, mode_price=price, levers=levers, snags=snags, stakes=stakes,
                 lethal=lethal, reach=reach, reach_factors=factors, asks=p.asks, trade=p.trade, threatened_cost=tc,
                 alternate_cost=ac, method_consequences=consequences, modifier=mod, odds=o, base_odds=base_odds,
                 stored_dc_write=stored_write, notes=notes, obstacle_class=p.obstacle.obstacle_class,
                 nudge=p.obstacle.nudge, long_shot=long_shot, guard=guard, alternatives=alts)


_LIFT_VERBS = ("verb.exert", "verb.force", "verb.handle", "verb.sneak")
_LIFT = re.compile(r"\b(?:lift|carr(?:y|ies|ied|ying)|palm|pick\w* up|heave|haul|hoist)", re.IGNORECASE)


def lift_or_carry(rules: Any, beat: Beat) -> Any | None:  # rule: 01.6.1
    """`resolution.yaml#attribute_rubric.lift_or_carry` when it applies (DL-01-35): a beat whose typed change is
    `take`, or an Exert, Force, Handle or Sneak whose method lifts, carries or palms a thing; else None."""
    spec = (rules.resolution.get("attribute_rubric") or {}).get("lift_or_carry")
    if not spec:
        return None
    take = beat.change is not None and beat.change.kind == "take"
    lifts = beat.verb in _LIFT_VERBS and bool(_LIFT.search(f"{beat.method} {beat.intent}"))
    return spec if take or lifts else None


def lift_attribute(spec: Any, rules: Any, state: Any, beat: Beat, actor: Any, proposed: str,
                   comp: int) -> str:  # rule: 01.6.1
    """The method's words pick (heave: Might; palm, quick and quiet: Agility; carry far: Endurance); else the allowed
    attribute with the best computed odds, the proposed one kept on a tie (the OFFER lists the others)."""
    text = f"{beat.method} {beat.intent}"
    for attr, words in (spec.get("words") or {}).items():
        for w in words:
            if re.search(r"\b" + r"\w*\s+".join(map(re.escape, str(w).split())) + r"\w*", text, re.IGNORECASE):
                return str(attr)
    caps = _caps(rules)
    base_max = int(caps["base_pc"]["max"] if actor.kind == "pc" else caps["base_non_pc"]["max"])
    edge = min(int(caps["edge"]["max"]), int(actor.data.get("edge", 0) or 0))

    def score(a: str) -> int:
        return min(base_max, attribute_value(actor, a) + comp + edge) + status(
            rules, state, beat.actor, a, beat.verb, beat.traits, [])

    allowed = [str(a) for a in spec.get("allowed") or ()]
    best = max(score(a) for a in allowed)
    return proposed if proposed in allowed and score(proposed) == best else next(a for a in allowed if score(a) == best)


def _guarded(stakes: str, dc_source: str, secret: bool) -> bool:  # rule: 01.6.13
    """The guard applies to frames not Dire, not opposed (01.6.4 sources 2 and 3) and not secret."""
    return stakes != "dire" and dc_source not in ("opposed", "effect") and not secret


ATTACK_SIBLINGS = {"verb.strike": "strike instead", "verb.grapple": "grapple instead", "verb.force": "shove instead",
                   "verb.setup": "feint first"}  # 12.15.2 "sibling anchors" for an aimed attack (P-117)


def _attr_name(rules: Any, attr: str) -> str:
    try:
        return str(rules.attribute(attr).get("name") or attr.capitalize())
    except (KeyError, AttributeError):
        return attr.capitalize()


def alternatives(rules: Any, state: Any, actor: Any, *, verb: str | None, attribute: str, comp: int, edge: int,
                 circ: int, status: int, dc: int, defender: str | None, dc_source: str,
                 limit: int = 3, attrs: Sequence[str] | None = None) -> list[Alternative]:  # rule: 12.15.2
    """"Another way", computed with no model call: the same obstacle with each other attribute the verb allows
    (`attribute`, `alt_attributes`; `attrs` instead when a rubric names them, DL-01-35), and for an attack on a
    person the sibling verbs against that person's defense for each verb's `against`. Best chance first, at most
    `limit`.
    ponytail: the current competence is reused for every alternative; a per-verb deed tag would refine it."""
    caps = _caps(rules)
    base_max = int(caps["base_pc"]["max"] if actor.kind == "pc" else caps["base_non_pc"]["max"])
    lo, hi = int(caps["total"]["min"]), int(caps["total"]["max"])

    def chance(attr: str, target_dc: int) -> Odds:
        return odds(_clamp(min(base_max, attribute_value(actor, attr) + comp + edge) + circ + status, lo, hi),
                    target_dc)

    out: list[Alternative] = []
    entry = rules.basic_verbs.get(verb or "") or {}
    known = set(rules.attributes)
    named = list(attrs) if attrs is not None else [entry.get("attribute"),
                                                   *[x.get("attribute") for x in entry.get("alt_attributes") or ()]]
    for w in named:
        a = str(w or "").split(" ")[0]
        if a in known and a != attribute and all(x.attribute != a for x in out):
            o = chance(a, dc)
            out.append(Alternative(label=f"with {_attr_name(rules, a)}", verb=verb, attribute=a,
                                   chance=o.success_or_better, critical_failure=o.critical_failure))
    if dc_source == "opposed" and defender and verb in ATTACK_SIBLINGS and defender in state.entities:
        for v, label in ATTACK_SIBLINGS.items():
            ve = rules.basic_verbs.get(v) or {}
            a = str(ve.get("attribute") or "")
            a = a if a in known else "wits"  # a feint is by method: wits against wits (01.18 Setup)
            if v == verb:
                continue
            try:
                attrs = _defense_attrs(None, resolve_anchor(rules, v), rules)
            except _Refuse:
                continue
            d = max(_defense(rules, state, defender, x, None) for x in attrs)
            o = chance(a, d)
            out.append(Alternative(label=label, verb=v, attribute=a, chance=o.success_or_better,
                                   critical_failure=o.critical_failure))
    out.sort(key=lambda x: (-x.chance, x.critical_failure, x.label))
    return out[:limit]


def _mode_price(g: GateDecision, state: Any, beat: Beat, rules: Any) -> ModePrice | None:  # rule: 01.3.5
    if g.mode == "normal" or not g.license:
        return None
    lic = rules.license(g.license)
    if g.mode == "fallback":
        fb = lic.get("crude_fallback") or {}
        return ModePrice(mode="fallback", dc_shift=int(fb.get("dc_shift") or 0), reach_cap=fb.get("reach_cap"),
                         consequence=fb.get("consequence"), source=g.license)
    held = next((x for x in state.licenses.get(beat.actor, []) if x.license_id == g.license), None)
    if g.mode == "stretch":
        s = dict(lic.get("stretch") or {})
        s.update((s.get("by_grade") or {}).get(held.grade if held else "", {}) or {})
        return ModePrice(mode="stretch", dc_shift=int(s.get("dc_shift") or 0), focus_add=int(s.get("cost_add") or 0),
                         reach_cap=s.get("reach_cap"), source=g.license)
    e = lic.get("emulate") or rules.doc("licenses")["emulate_defaults"]
    return ModePrice(mode="emulate", dc_shift=int(e.get("dc_shift") or 0), focus_mult=int(e.get("cost_mult") or 1),
                     reach_cap=e.get("reach_cap"), source=g.license)


def _allowed_delta(delta: str, allowed: Sequence[Any]) -> bool:
    d = delta.strip().lower()
    for a in allowed:
        s = str(a).strip().lower()
        if d == s or d == s.split(" (")[0].strip() or s.startswith(d):
            return True
    return False


def _check_deltas(p: ProposedFrame, anchor: Any, state: Any, declared: int, limit: int) -> list[str]:
    # rule: 01.5.3
    if len(p.deltas) > limit:
        raise _Refuse(3, "deltas", f"{len(p.deltas)} knob changes; at most {limit} (re-anchor or split)")
    knobs = {k["knob"]: k for k in anchor.get("knobs") or ()}
    seen: set[str] = set()
    out: list[str] = []
    for d in p.deltas:
        if d.knob in seen:
            raise _Refuse(3, "deltas", f"knob {d.knob} changed twice")
        seen.add(d.knob)
        if d.knob not in knobs:
            raise _Refuse(3, "deltas", f"{anchor['id']} has no knob {d.knob!r}")
        if not _allowed_delta(d.delta, knobs[d.knob].get("allowed_deltas") or ()):
            raise _Refuse(3, "deltas", f"{d.delta!r} is not an allowed delta of {d.knob} on {anchor['id']}")
        if (d.cites_fact or "") not in state.facts:
            raise _Refuse(3, "deltas", f"knob {d.knob} cites no established fact ({d.cites_fact!r})")
        if not fact_usable(state, d.cites_fact or "", declared):
            raise _Refuse(3, "deltas", f"{d.cites_fact} was established after the declaration")
        out.append(f"{d.knob}:{d.delta}")
    return out


def _attr_id(x: Any) -> str | None:
    s = str(x).strip().lower().split(" (")[0]
    return s if s in ("might", "agility", "endurance", "wits", "intellect", "presence", "resolve") else None


def _check_attribute(p: ProposedFrame, anchor: Any, beat: Beat, g: GateDecision, rules: Any, actor: Any,
                     deltas: list[str]) -> tuple[str, str | None]:  # rule: 01.6.1
    if p.attribute not in rules.attributes:
        raise _Refuse(4, "attribute", f"unknown attribute {p.attribute!r}")
    allowed: set[str] = set()
    open_ = False
    verb = _verb_entry(rules, anchor, beat)
    if verb is not None:
        for a in [verb.get("attribute"), *[x.get("attribute") for x in verb.get("alt_attributes") or ()]]:
            if a in ("by_method", "by_license"):
                open_ = True
            elif (aid := _attr_id(a)) is not None:
                allowed.add(aid)
    for k in anchor.get("knobs") or ():
        if k["knob"] == "attribute" and (aid := _attr_id(k.get("default"))) is not None:
            allowed.add(aid)
    if g.gate == "G2" and g.license:
        la = rules.license(g.license).get("attribute")
        if la in (None, "by_method"):
            open_ = True
        elif (aid := _attr_id(la)) is not None:
            allowed.add(aid)
    allowed |= {_attr_id(d.split(":", 1)[1]) or "" for d in deltas if d.startswith("attribute:")}
    if not allowed and verb is None:
        open_ = True  # a chapter-rule anchor with no attribute knob: the method decides
    for a in (p.attribute, p.attribute_tie):
        if a and not open_ and a not in allowed:
            raise _Refuse(4, "attribute", f"{a} is not allowed by {anchor['id']} ({sorted(allowed)}) without an "
                                          "attribute delta")
    if p.attribute_tie and p.attribute_tie != p.attribute:
        lower, higher = sorted([p.attribute, p.attribute_tie], key=lambda a: (attribute_value(actor, a), a))
        return lower, higher
    return p.attribute, None


def _defense(rules: Any, state: Any, who: str, attr: str, tag: str | None) -> int:  # rule: 01.6.4
    ent = state.entities[who]
    comp, _ = competence(rules, ent, tag) if tag else (0, None)
    edge = min(int(_caps(rules)["edge"]["max"]), int(ent.data.get("edge", 0) or 0))
    st = status(rules, state, who, attr, None, (), [])
    return 10 + attribute_value(ent, attr) + comp + edge + st


def _social_terms(rules: Any, state: Any, who: str, actor: str, size: str | None) -> int:  # rule: 15.3.3
    """The standing mod (T-15-1, from state; never met: Neutral) and the request-size mod (15.3.2)."""
    r = state.relationships.get(f"{who}|{actor}|standing")
    value = r.value if r else 0
    standing = next((int(x.get("dc_mod") or 0) for x in rules.social["standing_effects"]
                     if int(x["standing"]) == value), 0)
    request = next((int(x.get("dc_mod") or 0) for x in rules.social["request_sizes"] if x.get("rung") == size), 0)
    return standing + request


def _tier_step(rules: Any, base: str, nudge: int) -> str:  # rule: 01.6.5
    """base + nudge on the T-01-2 ladder; never across the trivial line, never off the rolling rungs."""
    ladder = [t["id"] for t in rules.resolution["dc_tiers"] if t.get("dc") is not None]
    if base not in ladder:
        raise _Refuse(6, "obstacle.obstacle_class", f"a {base} class does not roll (01.4.1)")
    i = ladder.index(base) + nudge
    if i < 0:
        raise _Refuse(6, "nudge", "a nudge never crosses the trivial line (01.6.5): a rolled class stays rolled")
    if i >= len(ladder):
        raise _Refuse(6, "nudge", f"no rung above {base}")
    return ladder[i]


def _check_nudge(ob: Any, p: ProposedFrame, state: Any, declared: int) -> None:  # rule: 01.6.5
    if not ob.nudge:
        return
    if abs(ob.nudge) > 1:
        raise _Refuse(6, "nudge", "one rung at most (01.6.5)")
    if ob.obstacle_class in (None, "other"):
        raise _Refuse(6, "nudge", "a nudge moves a class's base; with class other name the rung itself")
    if not ob.nudge_fact or not fact_usable(state, ob.nudge_fact, declared):
        raise _Refuse(6, "nudge_fact", "a nudge cites an established intrinsic fact (01.6.5)")
    if not (ob.nudge_why or "").strip():
        raise _Refuse(6, "nudge_why", "say why the fact is intrinsic before nudging (01.6.5)")
    if ob.nudge_fact in {c.fact_id for c in [*p.levers, *p.snags]}:
        # one fact is intrinsic (the tier) or situational (a lever or snag), never both: the same fact counted
        # twice is the sim's double-error case (01-difficulty_rubric_sim-output.txt)
        raise _Refuse(6, "nudge_fact", f"{ob.nudge_fact} is already a lever or snag; one fact moves the odds once")


def _dc(p: ProposedFrame, anchor: Any, deltas: list[str], state: Any, rules: Any, notes: list[str], *,
        beat: Beat, verb: str | None,
        declared: int) -> tuple[int, Any, str | None, str | None, dict[str, Any] | None]:  # rule: 01.6.4
    ob = p.obstacle
    opp = opposed_by(state, beat, verb)
    if opp and ob.kind not in ("opposed", "entity_defense"):  # rule: 00.3.8
        raise _Refuse(6, "obstacle", f"{verb} aimed at {opp[0]} is resisted by their defense, never a tier (01.6.4)")
    dc_delta = next((d.split(":", 1)[1] for d in deltas if d.startswith("dc:")), None)
    key = stored_dc_key(ob.id, anchor["id"], dc_delta) if ob.id else None
    # 1. stored DC
    if key is not None and (fid := state.current_fact_id(WORLD, key)) is not None:
        return int(state.facts[fid].value), "stored", None, None, None
    if ob.kind == "stored":
        raise _Refuse(6, "obstacle", f"no stored DC {key!r}")
    # 2. opposed defense: the highest among the defenders
    if ob.kind in ("opposed", "entity_defense"):
        who = ob.entities or ([ob.entity] if ob.entity else [])
        if not who or any(w not in state.entities for w in who):
            raise _Refuse(6, "obstacle", f"opposed obstacle needs existing defender ids, got {who}")
        if ob.kind == "entity_defense":
            vals = []
            for w in who:
                d = (state.entities[w].data.get("defenses") or {}).get(ob.defense or "")
                if d is None:
                    raise _Refuse(6, "obstacle", f"{w} has no defense {ob.defense!r}")
                vals.append((int(d), w))
            dc, w = max(vals)
            return dc, "opposed", None, w, None
        attrs = _defense_attrs(ob.defense, anchor, rules, dc_delta, verb)
        vals = [(_defense(rules, state, w, a, ob.defense_tag), w) for w in who for a in attrs]
        dc, w = max(vals)
        if verb == "verb.talk" and state.entities[w].kind in ("npc", "companion", "adversary"):  # rule: 15.3.3
            dc += _social_terms(rules, state, w, beat.actor, ob.request_size)  # none named: R1 (+0)
        return dc, "opposed", None, w, None
    # 3. effect DC
    if ob.kind == "effect":
        if ob.severity:
            tier = next(s["hazard_tier"] for s in rules.scales["severity"] if s["id"] == ob.severity)
            return _tier_dc(rules, tier), "effect", tier, None, None
        if ob.entity and ob.entity in state.entities and ob.defense:
            ent = state.entities[ob.entity]
            comp, _ = competence(rules, ent, ob.defense_tag) if ob.defense_tag else (0, None)
            edge = min(int(_caps(rules)["edge"]["max"]), int(ent.data.get("edge", 0) or 0))
            return 10 + attribute_value(ent, ob.defense) + comp + edge, "effect", None, ob.entity, None
        raise _Refuse(6, "obstacle", "an effect DC needs a hazard severity or a source entity and attribute")
    # 4. rubric tier (00.3.8 source 3): the class's base plus at most one cited nudge; class `other`: the rung
    _check_nudge(ob, p, state, declared)
    tier_id = ob.tier
    if ob.obstacle_class and ob.obstacle_class != "other":
        classes = verb_classes(rules, verb)
        if ob.obstacle_class not in classes:
            raise _Refuse(6, "obstacle.obstacle_class", f"{ob.obstacle_class!r} is not one of {verb}'s classes "
                                                         f"({', '.join(classes) or 'none'}; else other)")
        tier_id = _tier_step(rules, classes[ob.obstacle_class], ob.nudge)
    if not tier_id:
        raise _Refuse(6, "obstacle", "a tiered obstacle needs a class, or class other with a tier")
    dc = _tier_dc(rules, tier_id)
    ob = ob.model_copy(update={"tier": tier_id})
    write = {"subject": WORLD, "predicate": key, "value": dc} if key else None
    if key is None:
        notes.append("tiered DC not stored: the obstacle has no id")
    return dc, "tier", ob.tier, None, write


# 15.6.1: "DC = mask = 10 + Presence + competence (guile.deception) + ...": a presence defense
_DC_KNOB_DEFENSE = {"mask": "presence"}


def _defense_attrs(defense: str | None, anchor: Any, rules: Any, dc_delta: str | None = None,
                   verb: str | None = None) -> list[str]:
    own = rules.basic_verbs.get(anchor.get("verb") or "")
    text = str((own or {}).get("anchor", {}).get("against", "")) if own else ""
    if not own:  # a ch.15 anchor has no verb: its `dc` knob names the defense (15.4.1 "default Resolve")
        knob = next((k for k in anchor.get("knobs") or () if k.get("knob") == "dc"), {})
        word = str(dc_delta or knob.get("default") or "").strip().lower()
        text = _DC_KNOB_DEFENSE.get(word, word)
        if not text and verb in rules.basic_verbs:  # a ch.06 conflict anchor (Strike, anc.06_4_3): the beat's verb
            text = str(rules.basic_verbs[verb].get("anchor", {}).get("against", ""))  # [fix: playtest 20261008 B]
    named = [a for a in ("might", "agility", "endurance", "wits", "intellect", "presence", "resolve") if a in text]
    if defense:
        if defense not in rules.attributes:
            raise _Refuse(6, "obstacle.defense", f"unknown defense attribute {defense!r}")
        if named and defense not in named:
            raise _Refuse(6, "obstacle.defense", f"{anchor['id']} is resisted with {named}, not {defense}")
        return [defense]
    if not named:
        raise _Refuse(6, "obstacle.defense", "name the defense attribute")
    return named if "higher" in text else named[:1]


def _tier_dc(rules: Any, tier: str) -> int:  # rule: T-01-2
    for t in rules.resolution["dc_tiers"]:
        if t["id"] == tier:
            if t.get("dc") is None:
                raise _Refuse(6, "obstacle.tier", f"tier {tier} does not roll ({'G4' if t.get('gate') else 'no roll'})")
            return int(t["dc"])
    raise _Refuse(6, "obstacle.tier", f"unknown tier {tier!r}")


def _levers(p: ProposedFrame, beat: Beat, state: Any, rules: Any, declared: int,
            limits: Any) -> tuple[list[LeverCite], list[LeverCite], int]:  # rule: 01.6.8
    caps = _caps(rules)["circumstance"]
    if len(p.levers) > int(limits["levers_cited"]):
        raise _Refuse(7, "levers", f"{len(p.levers)} levers; at most {limits['levers_cited']}")
    cited_snags = [s for s in p.snags if not s.engine]
    if len(cited_snags) > int(limits["snags_cited"]):
        raise _Refuse(7, "snags", f"{len(cited_snags)} snags; at most {limits['snags_cited']}")
    seen: set[str] = set()
    for c in [*p.levers, *cited_snags]:
        if c.fact_id in seen:
            raise _Refuse(7, "levers", f"{c.fact_id} cited twice (one fact, one lever)")
        seen.add(c.fact_id)
        if c.fact_id not in state.facts:
            raise _Refuse(7, "levers", f"{c.fact_id} is not an established fact")
        if not fact_usable(state, c.fact_id, declared):
            raise _Refuse(7, "levers", f"{c.fact_id} was established after the declaration (usable next beat)")
    # free facts (01.15.8)
    free = set(state.meta.get(FREE_FACTS_KEY, []))
    free_here = [c for c in p.levers if c.fact_id in free]
    if len(free_here) > FREE_FACT_LEVERS_PER_ROLL:  # rule: 01.15.8
        raise _Refuse(7, "levers", "at most one lever a roll may cite a free fact (01.15.8)")
    if free_here and _free_fact_rolls(state, beat.actor, free) >= FREE_FACT_ROLLS_PER_SCENE:
        raise _Refuse(7, "levers", f"free facts were levers on {FREE_FACT_ROLLS_PER_SCENE} rolls this scene: "
                                   f"{free_here[0].fact_id} must be worked by a Setup (01.15.8)")
    # 00.3.9(b), 01.6.8: at most one cited Precision snag; a further fitting hindering fact applies as Protective
    cap = int(rules.resolution.get("frame_guards", {}).get("cited_precision_snags_max", 1))
    prec = [s for s in cited_snags if s.type == "precision"]
    cited_snags = [s.model_copy(update={"type": "protective"}) if s in prec[cap:] else s for s in cited_snags]
    ob = p.obstacle
    if ob.kind == "tier" and (ob.nudge or ob.obstacle_class == "other"):  # rule: 01.6.8
        # I-159, DL-01-29: one model-chosen modifier per beat. A nudged or class `other` tier already carries it,
        # so a cited Precision snag is refused as such and applies as Protective (stakes +1 each, clamped)
        cited_snags = [s.model_copy(update={"type": "protective"}) if s.type == "precision" else s
                       for s in cited_snags]
    snags = list(cited_snags)
    rep = list(rules.resolution["repetition"]["engine_snags_by_instance"])
    rep_val = int(rep[min(p.repetition_instance, len(rep)) - 1])
    if rep_val:  # rule: 01.14.3
        snags.append(LeverCite(fact_id=f"repeat.{beat.actor}.{beat.parent_beat or beat.id}.{p.repetition_instance}",
                               type="precision", engine=True))
    lv = int(caps["lever_value"])
    circ = lv * sum(1 for c in p.levers if c.type == "precision")
    circ -= lv * sum(1 for c in cited_snags if c.type == "precision")
    circ += rep_val
    return list(p.levers), snags, _clamp(circ, int(caps["min"]), int(caps["max"]))


def _free_fact_rolls(state: Any, actor: str, free: set[str]) -> int:
    n = 0
    for fs in state.frames.values():
        f = fs.frame
        if (f.get("beat") or {}).get("actor") == actor and any(lv.get("fact_id") in free for lv in f.get("levers", [])):
            n += 1
    return n


def _step(ladder: Sequence[str], rung: str, steps: int) -> str:
    return ladder[_clamp(ladder.index(rung) + steps, 0, len(ladder) - 1)]


def _stakes(p: ProposedFrame, levers: list[LeverCite], snags: list[LeverCite], free: set[str], state: Any,
            rules: Any, declared: int) -> tuple[StakesRung, bool]:  # rule: 01.6.9
    flags = rules.resolution["stakes_flags"]
    if p.stakes_source != "none" and p.stakes_source not in flags["source"]["sources"]:
        raise _Refuse(8, "stakes_source", f"unknown stakes source {p.stakes_source!r}")
    base: StakesRung = "safe" if p.stakes_source == "none" else ("dire" if p.stakes_heavy else "risky")
    if p.lethal:
        if not lethal_context_recorded(state, declared):
            raise _Refuse(8, "lethal", "lethal without lethal_context recorded before the declaration (00.3.14)")
        if p.threatened_cost is None or p.threatened_cost.menu_id not in LETHAL_COSTS:
            raise _Refuse(8, "lethal", "lethal only when the threatened cost is cost.harm or cost.footing")
    prot = [c for c in levers if c.type == "protective"]
    after_levers = _step(STAKES_LADDER, base, -len(prot) + sum(1 for c in snags if c.type == "protective"))
    if p.lethal and base == "dire" and after_levers != "dire" and any(c.fact_id in free for c in prot):
        raise _Refuse(7, "levers", "a free fact is never the Protective lever that takes a lethal frame below Dire "
                                   "(01.15.8)")
    trade = {t["id"]: t for t in rules.resolution["trades"]}.get(p.trade)
    rung = after_levers
    if trade is not None:  # rule: 01.7.3
        forb = trade.get("forbidden_from") or {}
        if forb.get("stakes") == rung:
            raise _Refuse(8, "trade", f"{p.trade} is not allowed from {rung}")
        rung = _step(STAKES_LADDER, rung, int(trade["stakes_steps"]))
    stakes: StakesRung = rung  # type: ignore[assignment]
    return stakes, bool(p.lethal and stakes == "dire")


def _reach(p: ProposedFrame, levers: list[LeverCite], snags: list[LeverCite], stakes: str,
           price: ModePrice | None) -> tuple[ReachRung, list[str]]:  # rule: 01.6.10
    factors: list[str] = []
    rung = "standard"
    if not p.reach_whole:
        rung, factors = "limited", [*factors, "not the whole intent"]
    if p.reach_one_factor:
        rung, factors = "limited", [*factors, "one effect factor against"]
    amp = sum(1 for c in levers if c.type == "amplifying") - sum(1 for c in snags if c.type == "amplifying")
    if amp:
        rung = _step(REACH_LADDER, rung, amp)
        factors.append(f"amplifying {amp:+d}")
    if p.trade == "go_big":
        rung = _step(REACH_LADDER, rung, 1)
        factors.append("go big +1")
    elif p.trade == "play_it_safe":
        if rung == "limited":
            raise _Refuse(9, "trade", "play it safe is not allowed from Limited reach")
        rung = _step(REACH_LADDER, rung, -1)
        factors.append("play it safe -1")
    if price is not None and price.reach_cap and REACH_LADDER.index(rung) > REACH_LADDER.index(price.reach_cap):
        rung = price.reach_cap
        factors.append(f"{price.mode} cap {price.reach_cap}")
    reach: ReachRung = rung  # type: ignore[assignment]
    return reach, factors


# 01.9.3 "a consequence never negates a success": a price paid on success at a cost cannot be the person acted on
# getting loose (playtest 20261008: a grapple "succeeded" and paid "she tears away", so the hold was both set and
# gone). ponytail: a closed list of escape phrasings; a typed `form_subject` field would replace it if forms drift
_UNDO = re.compile(
    r"\b(?:break|breaks|broke|pull|pulls|pulled|tear|tears|tore|wrench|wrenches|wrenched|twist|twists|twisted|"
    r"slip|slips|slipped|get|gets|got|wriggle|wriggles|wriggled|squirm|squirms|squirmed)\s+(?:\S+\s+){0,3}?"
    r"(?:free|away|loose|clear)\b"
    r"|\b(?:escape[sd]?|walk(?:s|ed)? (?:off|away)|refuses? to be held|(?:grip|hold) (?:on \S+ )?(?:slips|breaks|fails)"
    r"|lose (?:your|the) (?:grip|hold))\b", re.I)


def _sets_hold(beat: Beat, state: Any) -> bool:  # rule: 01.9.3
    """The beat's own success is a hold on its target: a grapple against their will by an actor who holds no one
    yet (T-12-18's `held` slot). Losing a hold set earlier is a price like any other: it undoes nothing this beat
    did (playtest 20261008-145430: a lift and a punch "while holding her" were re-asked for "she twists free")."""
    from engine.store.details import current

    if beat.verb != "verb.grapple" or not beat.against_will or beat.target in (None, "none"):
        return False
    held = current(state, beat.actor, "held") if state is not None and hasattr(state, "details") else None
    return held is None or not held.value


def _costs(p: ProposedFrame, beat: Beat, state: Any, rules: Any, stakes: str,
           declared: int) -> tuple[CostPreview, CostPreview | None]:  # rule: 01.6.11
    kw = dict(state=state, rules=rules, actor=beat.actor, stakes_source=p.stakes_source,
              target=beat.target if beat.target != "none" else None, declared_seq=declared)
    bad = check_cost_decl(p.threatened_cost, role="threatened", **kw)  # type: ignore[arg-type]
    if bad:
        raise _Refuse(10, "threatened_cost", bad)
    if _sets_hold(beat, state):  # rule: 01.9.3
        # a form in which the held one gets loose would undo the beat's own success: its words are dropped (the screen
        # names the cost's plain words) rather than the frame refused, so no Framer choice can force a re-ask
        p = p.model_copy(update={k: c.model_copy(update={"form_intent": ""}) for k in ("threatened_cost",
                                                                                     "alternate_cost")
                                 if (c := getattr(p, k)) is not None and _UNDO.search(c.form_intent or "")})
    if stakes in ("risky", "dire") and p.alternate_cost is None:
        raise _Refuse(10, "alternate_cost", f"a {stakes} frame needs an alternate cost (01.6.11)")
    alt = p.alternate_cost if stakes != "safe" else None  # a safe frame's alternate waits for go big (01.7.3)
    if alt is not None:
        bad = check_cost_decl(alt, role="alternate", other=p.threatened_cost, **kw)  # type: ignore[arg-type]
        if bad:
            raise _Refuse(10, "alternate_cost", bad)
    prev = severity_previews(stakes, rules)
    assert p.threatened_cost is not None
    tc = CostPreview(**_fitted(p.threatened_cost, rules).model_dump(), **prev)  # type: ignore[arg-type]
    ac = None
    if alt is not None:
        ac = CostPreview(**_fitted(alt, rules).model_dump(), on_success_at_cost=prev["on_success_at_cost"])
    return tc, ac


def _fitted(cost: Any, rules: Any) -> Any:  # rule: 01.13.1
    """A form that only repeats the cost menu's example words is no form for this scene: blank, so the screen names
    the menu entry alone (P-083)."""
    try:
        examples = {str((f or {}).get("text") or "").strip().lower()
                    for f in (rules.get(cost.menu_id).get("forms") or {}).values()}
    except (KeyError, AttributeError, TypeError):
        return cost
    form = (cost.form_intent or "").strip().lower().rstrip(".")
    return cost.model_copy(update={"form_intent": ""}) if form and form in examples else cost


# ------------------------------------------------------------------------------------------- OFFER


def legal_trades(frame: Frame) -> list[str]:  # rule: 01.7.3
    """The trades the player may still make (once per beat; re-run frame_check with `trade` set)."""
    if frame.trade != "none":
        return []
    out = []
    if frame.stakes != "dire":
        out.append("go_big")
    if frame.stakes != "safe" and frame.reach != "limited":
        out.append("play_it_safe")
    return out


def auto_commit_allowed(frame: Frame) -> bool:  # rule: 01.7.4
    """Safe (worst cost S1), not lethal, not secret, not a long shot, no mode price, success-or-better >= 50%.
    A Risky, Dire or lethal frame never auto-commits (DL-01-32)."""
    return (frame.stakes == "safe" and not frame.lethal and not frame.secret and not frame.long_shot
            and frame.mode_price is None and frame.odds.success_or_better >= 50)


def offer_preview(frame: Frame, rules: Any = None) -> OfferPreview:  # rule: 01.7.1
    """contracts/engine-api.md OfferView, built from the computed frame only."""
    words = frame.tier.replace("_", " ").capitalize() if frame.tier else {
        "stored": "stored", "opposed": "their defense", "effect": "the effect's strength"}.get(frame.dc_source, "")
    if frame.dc_source == "stored":
        words = "stored"
    tc = frame.threatened_cost
    return OfferPreview(
        restated_beat=frame.beat.restatement or frame.beat.intent,
        approach={"verb": frame.gate.verb, "attribute": frame.attribute, "license": frame.gate.license},
        difficulty_words="hidden" if frame.secret else words, dc_source="hidden" if frame.secret else frame.dc_source,
        need=None if frame.secret else frame.odds.need,
        odds={"success_or_better_pct": frame.odds.success_or_better,
              "critical_success_pct": frame.odds.critical_success,
              "critical_failure_pct": frame.odds.critical_failure, "near_miss_pct": frame.odds.near_miss},
        stakes=frame.stakes, lethal=frame.lethal,
        threatened_cost={"menu_id": tc.menu_id, "form": tc.form_intent, "severity_on_failure": tc.on_failure,
                         "severity_on_critical_failure": tc.on_critical_failure},
        alternate_cost=({"menu_id": frame.alternate_cost.menu_id, "form": frame.alternate_cost.form_intent}
                        if frame.alternate_cost else None),
        reach=frame.reach, mode_price=frame.mode_price.model_dump() if frame.mode_price else None,
        alternative_attribute=frame.alternative_attribute, only_natural_20=frame.odds.only_natural_20,
        trades=legal_trades(frame), long_shot=frame.long_shot)


def commit_events(frame: Frame, choice: OfferChoice, *, mint: Callable[[str], str], state: Any,
                  turn_id: str | None = None) -> list[Event]:  # rule: 00.13.2
    """The stored DC write (a tiered obstacle, 01.6.5) and `frame_committed`; sets `frame.id`."""
    if choice not in ("commit", "auto"):
        raise ValueError(f"a frame is committed only by commit or auto, not {choice!r}")
    if choice == "auto" and not auto_commit_allowed(frame):
        raise ValueError("this frame may not be auto-committed (01.7.4)")
    frame.id = frame.id or mint(ids.FRAME)
    frame.offer_choice = choice
    evs: list[Event] = []
    w = frame.stored_dc_write
    if w and state.current_fact_id(w["subject"], w["predicate"]) is None:
        evs.append(Event.of("fact_set", {"source": "ruling"}, source=frame.id, rule_id="01.6.5", turn_id=turn_id,
                            fact_id=mint(ids.FACT), subject=w["subject"], predicate=w["predicate"], value=w["value"],
                            visibility="background"))
    evs.append(Event.of("frame_committed", source=frame.id, rule_id="00.13.2", turn_id=turn_id,
                        beat_id=frame.beat.id, frame_id=frame.id, frame=frame.record()))
    return evs
