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
from typing import Any

from engine import ids
from engine.resolve.costs import check_cost_decl, established_stakes_sources, severity_previews
from engine.resolve.gate import GateDecision, check_gate
from engine.resolve.odds import odds
from engine.resolve.rulings import find_rulings, signature
from engine.resolve.types import (
    REACH_LADDER,
    STAKES_LADDER,
    Beat,
    CostPreview,
    Frame,
    FrameRefusal,
    GateRecord,
    LeverCite,
    ModePrice,
    Modifier,
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
    # 6. DC (stored, opposed, effect, tier) plus the mode's dc_shift
    dc, dc_source, tier, defender, stored_write = _dc(p, anchor, deltas, state, rules, notes)
    if price is not None:
        dc += price.dc_shift
    # 7. levers and snags
    levers, snags, circ = _levers(p, beat, state, rules, declared, limits)
    free = set(state.meta.get(FREE_FACTS_KEY, []))
    # 8. stakes and lethal
    if p.stakes_source == "listening_clock" and p.stakes_source not in established_stakes_sources(
            state, rules, beat.actor):  # rule: 01.6.9
        raise _Refuse(8, "stakes_source", "listening_clock: no clock is running")
    stakes, lethal = _stakes(p, levers, snags, free, state, rules, declared)
    # 9. reach
    reach, factors = _reach(p, levers, snags, stakes, price)
    # 10. costs
    tc, ac = _costs(p, beat, state, rules, stakes, declared)
    # 11. modifier
    caps = _caps(rules)
    a_val = attribute_value(actor, attr)
    edge = min(int(caps["edge"]["max"]), int(actor.data.get("edge", 0) or 0))
    st = status(rules, state, beat.actor, attr, beat.verb or anchor.get("verb"), p.traits or beat.traits, notes)
    base_max = int(caps["base_pc"]["max"] if actor.kind == "pc" else caps["base_non_pc"]["max"])
    base = min(base_max, a_val + comp + edge)
    lo, hi = int(caps["total"]["min"]), int(caps["total"]["max"])
    total = _clamp(base + circ + st, lo, hi)
    mod = Modifier(attribute=a_val, competence=comp, competence_tag=comp_tag, edge=edge, circumstance=circ,
                   status=st, total=total)
    # 12. odds
    o = odds(total, dc)
    base_odds = odds(_clamp(base + st, lo, hi), dc).success_or_better
    if o.only_natural_20:
        notes.append("only a natural 20, and at best a plain success")
    consequences = list(p.method_consequences)
    if price is not None and price.consequence and price.consequence not in consequences:
        consequences.append(price.consequence)
    return Frame(beat=beat, gate=GateRecord.model_validate({"class": g.gate, "verb": g.verb or beat.verb,
                                                                   "license": g.license, "mode": g.mode}),
                 secret=p.secret, anchor=anchor["id"], deltas=deltas, signature=sig,
                 precedent=found[-1].id if found else None, attribute=attr, alternative_attribute=alt_attr,
                 deed_tag=deed, traits=list(p.traits or beat.traits), obstacle_id=p.obstacle.id, dc_source=dc_source,
                 tier=tier, defender=defender, dc=dc, mode_price=price, levers=levers, snags=snags, stakes=stakes,
                 lethal=lethal, reach=reach, reach_factors=factors, trade=p.trade, threatened_cost=tc,
                 alternate_cost=ac, method_consequences=consequences, modifier=mod, odds=o, base_odds=base_odds,
                 stored_dc_write=stored_write, notes=notes)


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


def _dc(p: ProposedFrame, anchor: Any, deltas: list[str], state: Any, rules: Any,
        notes: list[str]) -> tuple[int, Any, str | None, str | None, dict[str, Any] | None]:  # rule: 01.6.4
    ob = p.obstacle
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
        attrs = _defense_attrs(ob.defense, anchor, rules, dc_delta)
        vals = [(_defense(rules, state, w, a, ob.defense_tag), w) for w in who for a in attrs]
        dc, w = max(vals)
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
    # 4. tier
    if not ob.tier:
        raise _Refuse(6, "obstacle", "a tiered obstacle needs a tier")
    dc = _tier_dc(rules, ob.tier)
    write = {"subject": WORLD, "predicate": key, "value": dc} if key else None
    if key is None:
        notes.append("tiered DC not stored: the obstacle has no id")
    return dc, "tier", ob.tier, None, write


# 15.6.1: "DC = mask = 10 + Presence + competence (guile.deception) + ...": a presence defense
_DC_KNOB_DEFENSE = {"mask": "presence"}


def _defense_attrs(defense: str | None, anchor: Any, rules: Any, dc_delta: str | None = None) -> list[str]:
    verb = rules.basic_verbs.get(anchor.get("verb") or "")
    text = str((verb or {}).get("anchor", {}).get("against", "")) if verb else ""
    if not verb:  # a ch.15 anchor has no verb: its `dc` knob names the defense (15.4.1 "default Resolve")
        knob = next((k for k in anchor.get("knobs") or () if k.get("knob") == "dc"), {})
        word = str(dc_delta or knob.get("default") or "").strip().lower()
        text = _DC_KNOB_DEFENSE.get(word, word)
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


def _costs(p: ProposedFrame, beat: Beat, state: Any, rules: Any, stakes: str,
           declared: int) -> tuple[CostPreview, CostPreview | None]:  # rule: 01.6.11
    kw = dict(state=state, rules=rules, actor=beat.actor, stakes_source=p.stakes_source,
              target=beat.target if beat.target != "none" else None, declared_seq=declared)
    bad = check_cost_decl(p.threatened_cost, role="threatened", **kw)  # type: ignore[arg-type]
    if bad:
        raise _Refuse(10, "threatened_cost", bad)
    if stakes in ("risky", "dire") and p.alternate_cost is None:
        raise _Refuse(10, "alternate_cost", f"a {stakes} frame needs an alternate cost (01.6.11)")
    if p.alternate_cost is not None:
        bad = check_cost_decl(p.alternate_cost, role="alternate", other=p.threatened_cost, **kw)  # type: ignore[arg-type]
        if bad:
            raise _Refuse(10, "alternate_cost", bad)
    prev = severity_previews(stakes, rules)
    assert p.threatened_cost is not None
    tc = CostPreview(**p.threatened_cost.model_dump(), **prev)  # type: ignore[arg-type]
    ac = None
    if p.alternate_cost is not None:
        ac = CostPreview(**p.alternate_cost.model_dump(), on_success_at_cost=prev["on_success_at_cost"])
    return tc, ac


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
    """Safe or Risky, not lethal, not secret, no mode price, success-or-better >= 50%."""
    return (frame.stakes in ("safe", "risky") and not frame.lethal and not frame.secret
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
        trades=legal_trades(frame))


_CITED_FACT = re.compile(r"\s*\((?:source:\s*)?fact\.\d+\)")  # "(source: fact.203)": the words already say it
_CITING = re.compile(r",?\s*\b(?:citing|per|source(?: is)?:?)\s+fact\.\d+", re.IGNORECASE)  # "…, citing fact.144"
_BARE_FACT = re.compile(r"\bfact\.\d+\b")
_OOF_TAIL = re.compile(r"\s*\b(?:out of fiction|OOF)\s*:.*$", re.IGNORECASE | re.DOTALL)
_PAREN = re.compile(r"\s*\([^()]*\)")
_PRONOUNS = {"he": ("he", "him", "his", "himself"), "she": ("she", "her", "hers", "herself")}
_NOT_A_NOUN = frozenset("a an the to of in on at for from with by and or but as if so that this it is was "
                        "when while than then nothing anything something everything away back up down off out "
                        "too again alone here there what how why where who into over".split())


def _pron_set(entity: Any) -> str | None:
    p = str((getattr(entity, "data", None) or {}).get("pronouns") or "").lower()
    return p.split("/")[0] if p.split("/")[0] in _PRONOUNS else None


def _fix_pronouns(text: str, want: str) -> str:
    """Swap the other set's pronouns for `want`'s ("her" before a noun is possessive)."""
    wrong = "she" if want == "he" else "he"
    subj, obj, poss, refl = _PRONOUNS[want]
    wsubj, wobj, wposs, wrefl = _PRONOUNS[wrong]

    def sub(m: re.Match[str]) -> str:
        w, nxt = m.group(1), m.group(2) or ""
        lw = w.lower()
        if lw == wsubj:
            out = subj
        elif lw == wrefl:
            out = refl
        elif want == "he" and lw == "her":
            out = "his" if nxt and nxt.lower() not in _NOT_A_NOUN else "him"
        elif want == "he" and lw == "hers":
            out = "his"
        elif lw == wobj:
            out = obj
        else:  # "his" -> "her"
            out = poss if want == "he" else "her"
        return (out[:1].upper() + out[1:]) if w[:1].isupper() else out

    words = "|".join(sorted({wsubj, wobj, wposs, wrefl}, key=len, reverse=True))
    return re.sub(rf"\b({words})\b(?=(?:\s+([A-Za-z']+))?)", sub, text, flags=re.IGNORECASE)


def _fact_words(state: Any, fid: str) -> str:
    f = state.facts.get(fid) if state is not None else None
    settled = "what is already settled"
    if f is None or f.visibility not in ("shown", "available"):
        return settled
    if isinstance(f.value, dict):  # a structured value (a bond: {"kind": "friend", "npc": ...}) in words, or dropped
        ent = state.entities.get(str(f.value.get("npc") or f.value.get("entity") or ""))
        if ent is None or not getattr(ent, "name", ""):
            return settled
        kind = f.value.get("kind")
        return f"your {str(kind).replace('_', ' ')} {ent.name}" if kind and f.subject.startswith("pc.") else ent.name
    if isinstance(f.value, list) or "." in f.predicate:  # a list, or a dotted predicate id: no plain words
        return settled
    pred = f.predicate.replace("_", " ").strip()
    if len(f.predicate) >= 60:  # a slug cut at 60 (engine/dm/turn.py, narration.py): never show a cut word
        pred = pred.rsplit(" ", 1)[0]
    # a false or empty fact is never negated in words ("not no one is watching ..."): the plain phrase stands
    return pred if f.value is True else f"{pred}: {f.value}" if f.value not in (False, None) else settled


def plain_offer_words(frame: Frame, state: Any) -> Frame:  # rule: 12.14.4
    """The model-written words the OFFER shows (the restated beat, the cost forms) without ids or internals: a
    cited fact id is dropped (the form already says it in words), a bare one becomes the fact's words; the
    restatement loses its asides and any "out of fiction" tail; the actor's pronouns are the store's.
    ponytail: pronouns are fixed only for a he/she actor and only when no one else present uses the other set."""
    actor = state.entities.get(frame.beat.actor) if state is not None else None
    want = _pron_set(actor)
    if want and state.scene is not None:
        others = [state.entities.get(i) for i in [*state.scene.cast_present, frame.beat.target or ""]
                  if i and i != frame.beat.actor]
        if any(_pron_set(e) not in (None, want) for e in others):
            want = None

    def plain(text: str, beat: bool = False) -> str:
        t = _CITING.sub("", _CITED_FACT.sub("", text or ""))
        t = _BARE_FACT.sub(lambda m: _fact_words(state, m.group(0)), t)
        if beat:
            t = _PAREN.sub("", _OOF_TAIL.sub("", t)).strip()
        return _fix_pronouns(t, want) if want else t

    frame.beat.restatement = plain(frame.beat.restatement, beat=True)
    for cost in (frame.threatened_cost, frame.alternate_cost):
        if cost is not None:
            cost.form_intent = plain(cost.form_intent)
    return frame


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
