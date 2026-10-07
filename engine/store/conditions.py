"""Conditions (00.9; T017): PR-00-5 applying a condition with 00.9.2 stacking, and removal. Functions return
events; the caller stages them.

    res = apply_condition(tx.state, tx.mint, rules, "npc.tam", "cond.frightened", severity="S2",
                          source={"entity": "pc.wren", "effect_id": None, "frame_id": "frame.3"})
    tx.add_all(res.events)
    res.outcome        # applied | refreshed | replaced | intensified | escalated | added | ignored | neutralized | immune
    res.must_narrate   # the condition is visible: the narration names it this turn (PR-00-5 step 6)
"""

from __future__ import annotations

import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any

from engine import ids
from engine.store.events import ConditionInstance, Event
from engine.store.projection import WorldState

Outcome = str
SEVERITIES = ("S1", "S2", "S3", "S4", "S5")
# Rounds per unit (00.7.1) for comparing numeric durations.
_ROUNDS = {"rounds": 1, "intervals": 100, "hours": 600, "watches": 3600, "days": 14400}
# Coarse order of the event-bounded durations, longer to the right (M1: used only to pick "the longer").
_ORDER = ["conflict", "scene", "until_rest:breather", "until_rest:rest_short", "until_rest:rest_long",
          "until_cleansed", "while", "permanent"]
_NUMERIC = re.compile(r"^(rounds|intervals|hours|watches|days):(\d+)$")


@dataclass
class ConditionResult:
    events: list[Event]
    outcome: Outcome
    instance_id: str | None = None
    on_apply: list[Mapping[str, Any]] = field(default_factory=list)  # effects to run (substrate, later)
    on_remove: list[Mapping[str, Any]] = field(default_factory=list)
    hooks: list[str] = field(default_factory=list)  # hooks to fire, subject to depth (00.10.8)
    must_narrate: bool = False
    removed: list[str] = field(default_factory=list)  # instance ids removed


def duration_rank(expr: str) -> tuple[int, int]:
    """Sort key: numeric durations by rounds, then the event-bounded forms in _ORDER."""
    m = _NUMERIC.match(expr)
    if m:
        return (0, int(m.group(2)) * _ROUNDS[m.group(1)])
    head = "while" if expr.startswith("while:") else expr
    return (1, _ORDER.index(head) if head in _ORDER else len(_ORDER))


def longer(a: str, b: str) -> str:
    return a if duration_rank(a) >= duration_rank(b) else b


def halve(expr: str) -> str:
    """Half a numeric duration, rounded down, minimum 1 unit; other forms are unchanged (00.9.3e)."""
    m = _NUMERIC.match(expr)
    return f"{m.group(1)}:{max(1, int(m.group(2)) // 2)}" if m else expr


def apply_condition(state: WorldState, mint: Callable[[str], str], rules: Any, target: str, condition_id: str,
                    *, severity: str | None = None, duration: str | None = None,
                    source: Mapping[str, Any] | None = None, rule_id: str = "PR-00-5") -> ConditionResult:
    """PR-00-5. `mint` is `tx.mint`; `rules` is a loaded `Rules`."""  # rule: PR-00-5
    cdef = rules.condition(condition_id)
    if target not in state.entities:
        raise ValueError(f"unknown target {target}")
    events: list[Event] = []
    active = state.conditions_on(target)
    src = dict(source or {})

    # 1. neutralizes (00.9.1, 00.9.3d)
    mine = set(cdef.get("neutralizes") or ())
    cancelled = [i for i in active if i.condition_id in mine]
    blocked = any(condition_id in (rules.condition(i.condition_id).get("neutralizes") or ()) for i in active)
    if cancelled or blocked:
        res = ConditionResult(events=[], outcome="neutralized")
        for inst in cancelled:
            res.events.append(_removed(inst.instance_id, f"neutralized by {condition_id}", rule_id))
            res.removed.append(inst.instance_id)
            res.on_remove += list(rules.condition(inst.condition_id).get("on_remove") or ())
        return res

    # 2. diminishing returns (00.9.3e)
    dur = duration or str(cdef["duration"])
    dim = cdef.get("diminishing")
    group = None
    if dim:
        group = dim.get("group") or condition_id
        count = _applications(state, target, group, dim.get("window", "scene"))
        if count >= int(dim["immune_after"]):
            return ConditionResult(events=[], outcome="immune")
        if count >= int(dim["halve_after"]):
            dur = halve(dur)

    sev = severity if (severity and cdef.get("severity_variable")) else str(cdef["severity"])
    if sev not in SEVERITIES:
        raise ValueError(f"severity {sev!r}")
    same = [i for i in active if i.condition_id == condition_id]
    stacking = cdef["stacking"]
    max_stacks = int(cdef.get("max_stacks") or 1)

    def emit(inst: ConditionInstance, outcome: str) -> ConditionResult:
        events.append(Event.of("condition_applied", source=str(src.get("frame_id") or src.get("entity") or "engine"),
                               rule_id=rule_id, instance_id=inst.instance_id, target=target, instance=inst,
                               outcome=outcome, diminishing_group=group))
        return ConditionResult(events=events, outcome=outcome, instance_id=inst.instance_id,
                               on_apply=list(cdef.get("on_apply") or ()), hooks=["on_condition_applied"],
                               must_narrate=bool(cdef.get("visible")))

    def refreshed(old: ConditionInstance, dur: str) -> ConditionInstance:
        # rule: 00.9.2 refresh: the longer of old and new. A new duration at least as long as the old one
        # restarts the clock now (applied_at is stamped by the projection); a shorter one leaves the old
        # instance as it is (approximation: the old instance's elapsed time is not subtracted).
        if longer(old.remaining, dur) == dur:
            return old.model_copy(update={"remaining": dur, "applied_at": None})
        return old

    def new_instance(stacks: int = 1) -> ConditionInstance:
        return ConditionInstance(instance_id=mint(ids.CONDITION_INSTANCE), condition_id=condition_id, target=target,
                                 severity=sev, stacks=stacks, remaining=dur, source=src,  # type: ignore[arg-type]
                                 exclusion_group=cdef.get("exclusion_group"),
                                 priority_rank=int(cdef.get("priority_rank") or 0))

    # 3. stacking (00.9.2)
    if not same or (stacking == "independent" and len(same) < max_stacks):
        return emit(new_instance(), "applied" if not same else "added")
    old = same[0]
    if stacking in ("unique", "independent"):
        return ConditionResult(events=[], outcome="ignored", instance_id=old.instance_id)
    if stacking == "refresh":
        return emit(refreshed(old, dur), "refreshed")
    if stacking == "replace_stronger":
        if SEVERITIES.index(sev) > SEVERITIES.index(old.severity):
            return emit(old.model_copy(update={"severity": sev, "remaining": dur, "source": src, "applied_at": None}), "replaced")
        if sev == old.severity:
            return emit(refreshed(old, dur), "refreshed")
        return ConditionResult(events=[], outcome="ignored", instance_id=old.instance_id)
    if stacking == "intensify":
        return emit(old.model_copy(update={"stacks": min(max_stacks, old.stacks + 1), "remaining": dur, "applied_at": None}),
                    "intensified")
    if stacking == "escalate":
        esc = cdef["escalates_to"]
        stacks = old.stacks + 1
        if stacks < int(esc["at_stacks"]):
            return emit(old.model_copy(update={"stacks": stacks, "remaining": dur}), "intensified")
        removal = _removed(old.instance_id, f"escalated to {esc['condition']}", rule_id)
        rest = state.model_copy()
        rest.conditions = {k: v for k, v in state.conditions.items() if k != old.instance_id}
        sub = apply_condition(rest, mint, rules, target, esc["condition"], source=src, rule_id=rule_id)
        sub.events = [removal, *sub.events]
        sub.removed.insert(0, old.instance_id)
        sub.outcome = "escalated" if sub.instance_id else sub.outcome
        return sub
    raise ValueError(f"{condition_id}: unknown stacking {stacking!r}")


def remove_condition(state: WorldState, rules: Any, instance_id: str, reason: str,
                     rule_id: str = "00.9") -> ConditionResult:  # rule: 00.9.1
    inst = state.conditions.get(instance_id)
    if inst is None:
        raise ValueError(f"no condition instance {instance_id}")
    cdef = rules.condition(inst.condition_id)
    return ConditionResult(events=[_removed(instance_id, reason, rule_id)], outcome="removed",
                           instance_id=instance_id, on_remove=list(cdef.get("on_remove") or ()),
                           removed=[instance_id])


def active_conditions(state: WorldState, target: str) -> list[ConditionInstance]:
    """The target's instances with exclusion groups resolved: only the highest priority_rank in a group is
    active; the rest are suppressed but keep their durations (00.9.3c, PR-00-5 step 4)."""  # rule: 00.9.3
    out: list[ConditionInstance] = []
    best: dict[str, ConditionInstance] = {}
    for inst in state.conditions_on(target):
        g = inst.exclusion_group
        if g is None:
            out.append(inst)
        elif g not in best or inst.priority_rank > best[g].priority_rank:
            best[g] = inst
    return out + list(best.values())


def _removed(instance_id: str, reason: str, rule_id: str) -> Event:
    return Event.of("condition_removed", source="engine", rule_id=rule_id, instance_id=instance_id, reason=reason)


def _applications(state: WorldState, target: str, group: str, window: str) -> int:
    start = state.scene.started_seq if state.scene else 0
    if window == "conflict":  # M1 has no conflicts: the window is the scene unless a conflict started in it
        start = max(start, state.time.last_boundary.get("conflict_start", 0))
    return sum(1 for a in state.applications if a.target == target and a.group == group and a.seq >= start)
