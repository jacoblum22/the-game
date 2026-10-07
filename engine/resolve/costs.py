"""The cost menu (01.13), cost severity (01.9.2, T-01-5) and applying the one due cost (PR-01-3 step 4).

    sev = cost_severity("risky", "failure")                                  # 'S2'
    bad = check_cost_decl(decl, role="threatened", state=..., rules=..., actor=..., stakes_source=...)
    app = apply_cost(frame, read, "cost.gear", state=tx.state, rules=rules, mint=tx.mint, params={"item": ...})
    tx.add_all(app.events)            # or app.refused: the cost cannot land in full -> the next candidate

Harm is not applied here: `cost.harm` calls `harm_hook(target, severity, *, lethal, harm_tags, frame_id) ->
list[Event]` (engine/harm plugs in; INV-6: `lethal` is the frame's flag). Time without a listening clock is
returned as `deferred` ({"advance_time": row}) for engine/time.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Mapping
from typing import Any, Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field

from engine import ids
from engine.data.loader import load_rules
from engine.resolve.types import CostDecl, Degree, Frame, ReadResult, Severity
from engine.rng import Rng
from engine.store.clocks import ClockError, tick_clock
from engine.store.conditions import apply_condition
from engine.store.events import WORLD, Event

SEVERITIES: tuple[Severity, ...] = ("S1", "S2", "S3", "S4", "S5")


class HarmHook(Protocol):
    def __call__(self, target: str, severity: str, *, lethal: bool, harm_tags: list[str],
                 frame_id: str | None) -> list[Event]: ...


def _rules(rules: Any) -> Any:
    return rules if rules is not None else load_rules()


def menu(rules: Any = None) -> dict[str, Any]:
    return {c["id"]: c for c in _rules(rules).resolution["cost_menu"]}


def cost_severity(stakes: str, deg: Degree, *, success_at_cost: bool = False,
                  rules: Any = None) -> Severity | None:  # rule: 01.9.2
    """T-01-5: the severity of the one cost due; None when nothing is due (any success; a Safe failure)."""
    if deg in ("success", "critical_success"):
        return None
    key = "near_miss_success_at_cost" if success_at_cost else deg
    for row in _rules(rules).resolution["read_costs"]:
        if row["stakes"] == stakes and row["degree"] == key:
            sev = row["severities"]
            return sev[0] if sev else None
    raise ValueError(f"no read_costs row for {stakes}/{key}")


def severity_previews(stakes: str, rules: Any = None) -> dict[str, Severity | None]:  # rule: 01.6.12
    """The cost previews for the OFFER: on failure, on a critical failure, on success at a cost."""
    return {"on_failure": cost_severity(stakes, "failure", rules=rules),
            "on_critical_failure": cost_severity(stakes, "critical_failure", rules=rules),
            "on_success_at_cost": cost_severity(stakes, "failure", success_at_cost=True, rules=rules)}


# ------------------------------------------------------------------------------------------- candidates


def _listening_clocks(state: Any, on: str) -> list[Any]:
    return [c for c in state.clocks.values()
            if c.status == "active" and any(str(r.get("on")) == on for r in c.tick_sources)]


def structural_fit(menu_id: str, *, state: Any, actor: str, stakes_source: str,
                   target: str | None = None) -> str | None:  # rule: 01.13.1
    """Without a cited source fact: the state that makes an entry a candidate, or None. (01.13.1: costs never
    come from nowhere; `fits_when` read through the stakes source and what the actor carries.)"""
    qs = state.quantities.get(actor, {})
    holds = [f for f in state.facts.values() if f.subject == actor and f.predicate in ("holds", "carries", "wields")]
    tgt = state.entities.get(target or "")
    checks: dict[str, bool] = {
        "cost.harm": stakes_source in ("hazard", "height_or_depth", "aware_opponent_or_observer"),
        "cost.footing": stakes_source in ("hazard", "height_or_depth", "aware_opponent_or_observer"),
        "cost.exposure": stakes_source in ("aware_opponent_or_observer", "listening_clock")
        or bool(_listening_clocks(state, "cost.exposure")),
        "cost.time": bool(_listening_clocks(state, "cost.time")) or stakes_source == "listening_clock",
        "cost.gear": bool(holds) or stakes_source == "damageable_item",
        "cost.drain": any(k in qs for k in ("focus", "supply", "ammunition", "light")) or stakes_source ==
        "consumed_resource",
        "cost.closed_door": stakes_source == "goodwill_or_trust" or (tgt is not None and tgt.kind in (
            "npc", "faction", "adversary", "companion")),
        "cost.twist": True,
        "cost.shortfall": True,
    }
    return f"{menu_id} fits through {stakes_source}" if checks.get(menu_id) else None


def check_cost_decl(decl: CostDecl | None, *, role: Literal["threatened", "alternate"], state: Any, rules: Any,
                    actor: str, stakes_source: str, target: str | None = None, declared_seq: int | None = None,
                    other: CostDecl | None = None) -> str | None:  # rule: 01.6.11
    """PR-01-2 step 10: the reason the declared cost is illegal, or None."""
    if decl is None:
        return f"no {role} cost declared"
    m = menu(rules)
    if decl.menu_id not in m:
        return f"unknown cost menu id {decl.menu_id!r}"
    if role == "threatened" and m[decl.menu_id].get("alternate_only"):
        return f"{decl.menu_id} is only ever an alternate (01.13.1)"
    if other is not None and other.menu_id == decl.menu_id:
        return "the alternate must be a different entry from the threatened cost"
    if decl.source_fact is not None:
        f = state.facts.get(decl.source_fact)
        if f is None:
            return f"{decl.menu_id} cites unknown fact {decl.source_fact!r}"
        if declared_seq is not None and f.valid_from_seq > declared_seq:
            return f"{decl.menu_id} cites {decl.source_fact}, established after the declaration"
        return None
    if structural_fit(decl.menu_id, state=state, actor=actor, stakes_source=stakes_source, target=target) is None:
        return f"{decl.menu_id}: no established source fits ({m[decl.menu_id]['fits_when']})"
    if decl.menu_id == "cost.twist":
        others = [k for k in m if k not in ("cost.twist", "cost.shortfall") and structural_fit(
            k, state=state, actor=actor, stakes_source=stakes_source, target=target)]
        if others:
            return f"cost.twist only when no other entry is a candidate ({', '.join(others)} fit)"
    return None


# ------------------------------------------------------------------------------------------- application


class CostApplication(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    menu_id: str
    severity: Severity | None
    form: str = ""
    events: list[Event] = Field(default_factory=list)
    reach_delta: int = 0  # cost.shortfall: delivered reach change (never below 1)
    deferred: dict[str, Any] | None = None  # work for another module (advance_time)
    refused: str | None = None


def _write(entry: Mapping[str, Any], sev: str) -> str:
    return str(((entry.get("forms") or {}).get(sev) or {}).get("write", ""))


def _fact_ev(state: Any, mint: Callable[[str], str], subject: str, predicate: str, value: Any,
             frame_id: str | None) -> Event:
    return Event.of("fact_set", {"source": "ruling"}, source=frame_id or "cost", rule_id="01.11.1",
                    fact_id=mint(ids.FACT), subject=subject, predicate=predicate, value=value, visibility="shown",
                    supersedes=state.current_fact_id(subject, predicate))


def _tick(state: Any, rules: Any, clock: str, on: str, sev: str, frame_id: str | None) -> list[Event]:
    return tick_clock(state, clock, on, severity=sev, units=rules.severity_units(),
                      source_ref=frame_id or on, rule_id="01.11.1").events


def _nearest_clock(state: Any, on: str) -> str | None:
    cs = sorted(_listening_clocks(state, on), key=lambda c: (c.segments - c.filled, c.id))
    return cs[0].id if cs else None


def apply_cost(frame: Frame, read: ReadResult, menu_id: str, *, state: Any, rules: Any,
               mint: Callable[[str], str], form: str | None = None, params: Mapping[str, Any] | None = None,
               harm_hook: HarmHook | None = None, rng: Rng | None = None,
               mode: str = "site") -> CostApplication:  # rule: PR-01-3
    """PR-01-3 step 4: validate the menu id (threatened, or the alternate on a success-at-cost), then write the
    entry's form at the READ severity. `refused` names why it cannot land in full (01.9.4)."""
    p = dict(params or {})
    sev = read.cost_severity
    app = CostApplication(menu_id=menu_id, severity=sev, form=form or "")
    if sev is None:
        app.refused = "no cost is due"
        return app
    if menu_id not in read.cost_choices:
        app.refused = f"{menu_id} is not the threatened cost (or the alternate on a success at a cost)"
        return app
    entry = menu(rules)[menu_id]
    if sev not in (entry.get("forms") or {}):
        app.refused = f"{menu_id} has no {sev} form"
        return app
    actor, fid = frame.beat.actor, frame.id
    write = _write(entry, sev)
    try:
        app.events, app.reach_delta, app.deferred = _apply(menu_id, sev, write, entry, frame, read, state, rules,
                                                           mint, form, p, harm_hook, rng, mode, actor, fid)
    except (CostRefused, ClockError) as e:
        app.events, app.refused = [], str(e)
    return app


class CostRefused(ValueError):
    pass


def _apply(menu_id: str, sev: str, write: str, entry: Mapping[str, Any], frame: Frame, read: ReadResult,
           state: Any, rules: Any, mint: Callable[[str], str], form: str | None, p: dict[str, Any],
           harm_hook: HarmHook | None, rng: Rng | None, mode: str, actor: str,
           fid: str | None) -> tuple[list[Event], int, dict[str, Any] | None]:  # rule: 01.11.1
    if menu_id == "cost.harm":  # rule: 01.13.2
        if harm_hook is None:
            raise CostRefused("cost.harm needs the harm module (harm_hook)")
        return harm_hook(p.get("target", actor), sev, lethal=frame.lethal, harm_tags=list(p.get("harm_tags", [])),
                         frame_id=fid), 0, None
    if menu_id == "cost.drain":  # rule: 01.13.3
        n = int(m.group(1)) if (m := re.search(r"update_quantity\(-(\d+)\)", write)) else 1
        qs = state.quantities.get(actor, {})
        name = p.get("quantity") or next((k for k in ("focus", "supply", "ammunition", "light") if k in qs), None)
        if name is None or name not in qs:
            raise CostRefused("cost.drain: the actor has nothing of that kind to lose")
        q = qs[name]
        if q.current - n < q.min:
            raise CostRefused(f"cost.drain cannot land in full: {name} {q.current} - {n} < {q.min} (01.9.4)")
        return [Event.of("quantity_changed", source=fid or "cost", rule_id="01.13.3", entity=actor, quantity=name,
                         delta=-n, new_value=q.current - n, reason=f"cost.drain {sev}", frame_id=fid)], 0, None
    if menu_id == "cost.time":  # rule: 01.13.5
        clock = p.get("clock") or _nearest_clock(state, "cost.time")
        if clock is not None:
            return _tick(state, rules, clock, "cost.time", sev, fid), 0, None
        row = (rules.resolution["time_cost"].get(mode) or {}).get(sev)
        if not isinstance(row, Mapping):
            raise CostRefused(f"cost.time: no listening clock and no {mode} time row")
        return [], 0, {"advance_time": dict(row), "mode": mode}
    if menu_id == "cost.exposure":  # rule: 01.13.6
        return _exposure(sev, entry, state, rules, mint, p, actor, fid), 0, None
    if menu_id == "cost.gear":  # rule: 01.13.4
        item = p.get("item")
        if item is None or item not in state.entities:
            raise CostRefused("cost.gear needs the carried item (params.item)")
        pred, val = {"S1": ("location", p.get("place", "ground")), "S2": ("location", p.get("place", "left behind")),
                     "S3": ("condition", "damaged"), "S4": ("condition", "broken"),
                     "S5": ("exists", "destroyed")}[sev]
        return [_fact_ev(state, mint, item, pred, val, fid)], 0, None
    if menu_id == "cost.footing":  # rule: 01.13.7
        conds = re.findall(r"cond\.[a-z_]+", write)
        cond = form if form in conds else (conds[0] if conds and not form else None)
        if cond is None:  # a non-condition form (a slide, a flag lost, swept away): the caller writes it
            return [], 0, {"footing": write, "severity": sev}
        res = apply_condition(state, mint, rules, p.get("target", actor), cond, severity=sev,
                              source={"entity": actor, "frame_id": fid})
        return list(res.events), 0, None
    if menu_id == "cost.closed_door":  # rule: 01.13.9
        obstacle = p.get("obstacle") or frame.obstacle_id or frame.beat.target or "obstacle"
        until = "scene_end" if sev == "S1" else "superseding_fact"
        evs = [_fact_ev(state, mint, WORLD, f"closed.{obstacle}.{p.get('method_class', 'method')}", until, fid)]
        steps = {"S3": -1, "S4": -2, "S5": -2}.get(sev)
        tgt = p.get("target") or frame.beat.target
        if steps and tgt in state.entities:
            key = f"{tgt}|{actor}|standing"
            cur = state.relationships[key].value if key in state.relationships else 0
            evs.append(Event.of("relationship_set", source=fid or "cost", rule_id="01.13.9", a=tgt, b=actor,
                                kind="standing", steps=steps, new_value=cur + steps, reason=f"cost.closed_door {sev}"))
        return evs, 0, None
    if menu_id == "cost.shortfall":  # rule: 01.13.8
        if not read.success_at_cost_taken:
            raise CostRefused("cost.shortfall applies only to a success at a cost")
        n = int(m.group(1)) if (m := re.search(r"-(\d+)", write)) else 1
        return [], -min(n, max(0, read.delivered_reach - 1)), None
    if menu_id == "cost.twist":  # rule: 01.13.10
        if rng is None:
            raise CostRefused("cost.twist rolls tbl.twist: pass rng")
        from engine.resolve.tables import roll_table

        res = roll_table("tbl.twist", {"severity": sev, "pc_frame": True}, rules=rules, state=state, rng=rng,
                         purpose=f"cost.twist {sev} {fid or ''}".strip())
        return list(res.events), 0, {"twist": res.words, "severity": sev}
    raise CostRefused(f"unknown cost {menu_id}")


def _exposure(sev: str, entry: Mapping[str, Any], state: Any, rules: Any, mint: Callable[[str], str],
              p: dict[str, Any], actor: str, fid: str | None) -> list[Event]:  # rule: 01.13.6
    ladder = list(entry.get("alertness_ladder") or ["unaware", "suspicious", "alert", "alarmed"])
    evs: list[Event] = []
    observer = p.get("observer")
    clock = p.get("clock") or _nearest_clock(state, "cost.exposure")
    if observer is None and clock is None:
        raise CostRefused("cost.exposure needs an observer or a listening clock")
    if observer is not None:
        if observer not in state.entities:
            raise CostRefused(f"unknown observer {observer}")
        cur = state.fact_value(observer, "alertness", ladder[0])
        i = ladder.index(cur) if cur in ladder else 0
        floor = {"S1": 0, "S2": ladder.index("alert"), "S3": len(ladder) - 1}.get(sev, len(ladder) - 1)
        new = ladder[min(len(ladder) - 1, max(i + 1, floor))]
        evs.append(_fact_ev(state, mint, observer, "alertness", new, fid))
    if sev in ("S3", "S4", "S5") and actor in state.positions and "flag.hidden" in state.positions[actor].flags:
        evs.append(Event.of("position_set", source=fid or "cost", rule_id="01.13.6", entity=actor,
                            flags_remove=["flag.hidden"]))
    if clock is not None:
        evs += _tick(state, rules, clock, "cost.exposure", sev, fid)
    return evs
