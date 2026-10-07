"""Rests and recovery (07.8; PR-07-8, PR-07-10) and ch.07's Milestone 1 boundary handlers.

    why = rest_refusal(state, "pc.wren", "rest_long")             # None, or the reason it cannot begin
    best = best_quality(state, "pc.wren", "rest_long", site="camp")  # shown before the rest (07.8.4)
    ...advance_time(the rest's duration); on interruptions, count them...
    q = rest_quality("rest_long", site="camp", interruptions=1, lost_intervals=4, sleep_hours=4)
    mark_boundary("rest_long", rest_payload("rest_long", q, "camp"))  # the time module marks it
    # handlers (phase 3): h_07_rest_recovery, then engine/abilities' h_05_focus_recover, h_05_rest_recharge

Handlers take a context with `state`, `mint`, `rules`, `boundary` and `payload` (the boundary event's payload)
and return events. A rest boundary's payload is `{quality, site, treated}` plus optional `resters` (entity ids;
default: every PC). Per-character counters live in meta (`<pc>.short_rests_today`,
`<pc>.breathers_since_short_rest`, `<pc>.rest_long.last`); h.05's handlers advance and reset them, and
h.07.rest_recovery runs before them (boundaries.yaml `before`), so both read the counts before this rest.
"""

from __future__ import annotations

import math
from typing import Any

from engine.harm import lethal as lethal_mod
from engine.harm.apply import restore_vitality, stabilize
from engine.harm.ctx import Writes, boundary_payload, counter_key
from engine.harm.state import DEAD, DYING, STAGGERED, VITALITY, brink, harm_state, pcs, wound_load
from engine.store.events import Event, Timestamp
from engine.store.projection import WorldState

REST_KINDS = ("breather", "rest_short", "rest_long")
QUALITIES = ("full", "partial", "interrupted")
SITES = ("haven", "camp", "rough")
INTERVALS_PER_HOUR = 6  # 00.7.1: an hour is six intervals (07.8.12: a short rest is six site checks)


def abs_watch(rules: Any, t: Timestamp) -> int:  # rule: 00.7.2
    """Watches since the start of year 1 (calendar.yaml: 4 seasons of 13 weeks of 7 days; 4 watches a day)."""
    cal = rules.doc("calendar")
    seasons = len(cal["seasons"])
    day = (((t.year - 1) * seasons + (t.season - 1)) * int(cal["weeks_per_season"]) + (t.week - 1)) \
        * int(cal["days_per_week"]) + (t.day - 1)
    return day * 4 + t.watch


def resters(ctx: Any) -> list[str]:
    p = boundary_payload(ctx)
    ids_ = p.get("resters") or p.get("entity")
    if isinstance(ids_, str):
        ids_ = [ids_]
    return [i for i in (ids_ or pcs(ctx.state)) if i in ctx.state.entities]


def rest_refusal(state: WorldState, rules: Any, pc: str, kind: str) -> str | None:  # rule: 07.8.1
    """Why this rest cannot begin now (07.8.1 needs; 00.7.2 long-rest spacing), or None."""
    if kind not in REST_KINDS:
        return f"unknown rest {kind}"
    hs = harm_state(state, pc)
    if hs == DEAD:
        return "the dead do not rest"
    if hs == DYING:
        return "a Dying character cannot rest: it must be stabilized first"
    if kind == "breather" and state.meta.get("conflict.in_progress"):
        return "no breather while a conflict is in progress"
    if kind == "rest_long":
        last = state.meta.get(counter_key(pc, "rest_long.last"))
        if last is not None:
            now = abs_watch(rules, state.time.now)
            if now // 4 == int(last) // 4:
                return "one long rest a day"
            if now - int(last) < 2:
                return "two watches must end between long rests"
    return None


def best_quality(state: WorldState, pc: str, kind: str, *, site: str, caps: list[str] | None = None) -> str:
    """The best a rest can be given the present facts, shown before it begins (07.8.4). `caps`: quality caps the
    caller knows of (no food or water today, weather S2+ unsheltered, medium or heavy armor for a long rest, an
    affliction at stage 2+, a haunt)."""  # rule: 07.8.4
    return "partial" if site == "rough" or caps else "full"


def within_allowance(kind: str, *, interruptions: int, lost_intervals: int = 0,
                     sleep_hours: int = 0) -> bool:  # rule: 07.8.3
    """Can an interrupted rest resume? breather never; short rest one interruption of at most 1 interval; long
    rest one of at most 1 hour with at least 4 hours of sleep served in all."""
    if interruptions == 0:
        return True
    if kind == "breather" or interruptions > 1:
        return False
    if kind == "rest_short":
        return lost_intervals <= 1
    return lost_intervals <= INTERVALS_PER_HOUR and sleep_hours >= 4


def rest_quality(kind: str, *, site: str, interruptions: int = 0, lost_intervals: int = 0, sleep_hours: int = 4,
                 caps: list[str] | None = None) -> str:  # rule: 07.8.4
    """Quality at completion, first match: interrupted (beyond the allowance), partial (resumed, rough site, a
    cap), full."""
    if not within_allowance(kind, interruptions=interruptions, lost_intervals=lost_intervals,
                            sleep_hours=sleep_hours):
        return "interrupted"
    if interruptions or site == "rough" or caps:
        return "partial"
    return "full"


def rest_payload(kind: str, quality: str, site: str, treated: bool = False,
                 resters: list[str] | None = None) -> dict[str, Any]:  # rule: PR-07-8
    """The rest boundary's payload (00.7.2; 07.8.1): `mark_boundary(kind, rest_payload(...))`."""
    if kind not in REST_KINDS or quality not in QUALITIES or site not in SITES:
        raise ValueError(f"bad rest payload {kind} {quality} {site}")
    p: dict[str, Any] = {"quality": quality, "site": site, "treated": treated}
    if resters:
        p["resters"] = list(resters)
    return p


def vitality_gain(kind: str, quality: str, current: int, maximum: int, *, breathers_since_short: int,
                  short_rests_today: int) -> int:  # rule: T-07-14
    """Vitality a rest restores (T-07-14), as the new value (never lower than `current`)."""
    def breather() -> int:
        return 0 if quality == "interrupted" or breathers_since_short >= 2 else 2

    if kind == "breather":
        add = breather()
    elif kind == "rest_short":
        if short_rests_today >= 2:
            add = 0 if quality == "interrupted" else 2  # later short rests restore as a breather
        else:
            add = {"full": math.ceil(maximum / 2), "partial": math.ceil(maximum / 4), "interrupted": 2}[quality]
    else:
        if quality == "full":
            return max(current, maximum)
        if quality == "partial":
            return max(current, math.ceil(3 * maximum / 4))
        add = math.ceil(maximum / 4)  # interrupted: as a partial short rest
    return current + add


def _exhausted(ctx: Any, w: Writes, eid: str, n: int) -> None:  # rule: 07.8.10
    for inst in [c for c in ctx.state.conditions_on(eid) if c.condition_id == "cond.exhausted"]:
        left = inst.stacks - n
        if left <= 0:
            w.extend([Event.of("condition_removed", source="h.07.rest_recovery", rule_id="07.8.5",
                               instance_id=inst.instance_id, reason="long rest")])
        else:
            w.extend([Event.of("condition_applied", source="h.07.rest_recovery", rule_id="07.8.5",
                               instance_id=inst.instance_id, target=eid, outcome="refreshed",
                               instance=inst.model_copy(update={"stacks": left}))])


def h_07_rest_recovery(ctx: Any) -> list[Event]:  # rule: PR-07-8
    # rule: 07.8.5
    # coarse: 07.8.6
    """`h.07.rest_recovery` (breather, rest_short, rest_long; phase 3): T-07-14 and its second table."""
    kind = str(getattr(ctx, "boundary", "") or "")
    p = boundary_payload(ctx)
    quality, site = str(p.get("quality", "full")), str(p.get("site", "camp"))
    w = Writes.of(ctx, source="h.07.rest_recovery")
    for eid in resters(ctx):
        hs = harm_state(ctx.state, eid)
        v = ctx.state.quantities.get(eid, {}).get(VITALITY)
        if hs in (DEAD, DYING) or v is None:
            continue
        mx = v.max if v.max is not None else v.current
        new = vitality_gain(kind, quality, v.current, mx,
                            breathers_since_short=int(ctx.state.meta.get(counter_key(eid, "breathers_since_short_rest"),
                                                                         0)),
                            short_rests_today=int(ctx.state.meta.get(counter_key(eid, "short_rests_today"), 0)))
        if new > v.current or (hs == STAGGERED and new > 0):
            restore_vitality(ctx, eid, to=new, reason=f"{kind} ({quality})", rule_id="T-07-14", writes=w)
        if wound_load(w, eid):
            w.fact(eid, "wound_load", 0, rule_id="07.2.6")
        # coarse: T-07-14 — Light and Moderate wound records do not exist before M2; nothing to heal.
        if kind == "rest_long":
            if quality in ("full", "partial"):
                _exhausted(ctx, w, eid, 2 if quality == "full" and site == "haven" else 1)
                w.fact(eid, "rested_today", True, rule_id="T-07-15")
                if quality == "full" and w.quantity(eid, "dread") is not None:
                    w.add_quantity(eid, "dread", -1, reason="a full long rest", rule_id="07.11.7")
            w.meta(counter_key(eid, "rest_long.last"), abs_watch(ctx.rules, ctx.state.time.now), rule_id="00.7.2")
    return w.events


def h_07_natural_recovery(ctx: Any) -> list[Event]:  # rule: PR-07-10
    """`h.07.natural_recovery` (day, phase 3), Milestone 1 parts: brink wounds tick by T-07-15 (+1 for each of
    rested_today, treated_today, bed_rest_today; 4 to heal, one at a time); then the day's flags clear. Wound
    recovery clocks, scars and the 7-day rules come with wound records (M2)."""
    w = Writes.of(ctx, source="h.07.natural_recovery")
    st: WorldState = ctx.state
    for eid in [i for i, e in st.entities.items() if e.kind in ("pc", "companion")]:
        flags = [f for f in ("rested_today", "treated_today", "bed_rest_today") if st.fact_value(eid, f)]
        if brink(st, eid) > 0 and flags:  # rule: T-07-15
            # coarse: 07.8.7 — the brink wound's clk.back_from_the_brink is kept as the brink_progress count.
            prog = int(st.fact_value(eid, "brink_progress", 0) or 0) + len(flags)
            if prog >= 4:
                w.fact(eid, "brink", brink(st, eid) - 1, rule_id="07.8.7")
                prog = 0
            w.fact(eid, "brink_progress", prog, rule_id="07.8.7")
        for f in ("rested_today", "treated_today", "treat_closed_today", "bed_rest_today"):
            if st.fact_value(eid, f):
                w.fact(eid, f, False, rule_id="PR-07-10")
    return w.events


def h_07_load_clear(ctx: Any) -> list[Event]:  # rule: 07.2.6
    """`h.07.load_clear` (scene_end, phase 1): clear wound loads; end lethal contexts whose `ends` is scene_end
    (07.3.5). Also 07.2.10: a recurring or principal NPC left Dying dies at scene_end unless stabilized."""
    w = Writes.of(ctx, source="h.07.load_clear")
    st: WorldState = ctx.state
    for eid in st.entities:
        if wound_load(st, eid):
            w.fact(eid, "wound_load", 0, rule_id="07.2.6")
        if st.entities[eid].kind not in ("pc", "companion") and harm_state(st, eid) == DYING:  # rule: 07.2.10
            w.fact(eid, "harm_state", DEAD, rule_id="07.2.10")
            w.fact(eid, "defeated", {"manner": "dead"}, rule_id="07.2.10")
    lethal_mod.end_contexts(w, reason="scene_end")
    return w.events


def h_07_lethal_scan(ctx: Any) -> list[Event]:  # rule: PR-07-4
    """`h.07.lethal_scan` (scene_start, conflict_start; phase 7): raise `trg.lethal_warning` for each source whose
    07.3.3 row is true and has no context yet, and `trg.danger_notice` for hard fights (07.3.8). The DM delivers
    them this turn (PR-07-4); `lethal.record_warning` writes the context once shown."""
    w = Writes.of(ctx, source="h.07.lethal_scan")
    st: WorldState = ctx.state
    pending: list[dict[str, Any]] = []
    notices: list[str] = []
    for pc in pcs(st):
        if harm_state(st, pc) == DEAD:
            continue
        for t in lethal_mod.warning_needed(st, pc):
            pending.append({"pc": pc, "source": t.source, "cause": t.cause, "detail": t.detail})
        for src in lethal_mod.scene_sources(st):
            if st.entities[src].data.get("threat_advisory") == "hard" and not any(
                    x["source"] == src for x in pending):
                notices.append(src)
    if pending != (st.meta.get("trg.lethal_warning") or []):
        w.meta("trg.lethal_warning", pending, rule_id="07.3.3")
    if notices != (st.meta.get("trg.danger_notice") or []):
        w.meta("trg.danger_notice", notices, rule_id="07.3.8")
    return w.events


def rest_duration(rules: Any, kind: str) -> tuple[int, str]:  # rule: 07.8.12
    """The time a rest costs (00.7.2; harm.yaml#rests): `advance_time` it in full before the boundary is marked;
    nothing restores without spending it."""
    for r in rules.harm["rests"]:
        if r["id"] == kind:
            unit, _, n = str(r["duration"]).partition(":")
            return int(n), unit
    raise ValueError(f"unknown rest {kind}")


def rest_site(state: WorldState, place: str | None) -> str | None:  # rule: 07.8.2
    """The place's recorded `rest_site` (a lookup once written), else None: the DM's rung, uncertain -> worse."""
    v = state.fact_value(place, "rest_site") if place else None
    return str(v) if v in SITES else None


def record_rest_site(ctx: Any, place: str, site: str) -> list[Event]:  # rule: 07.8.2
    if site not in SITES:
        raise ValueError(f"rest site {site!r}")
    w = Writes.of(ctx, source="07.8.2")
    w.fact(place, "rest_site", site, rule_id="07.8.2")
    return w.events


def treat(ctx: Any, patient: str, *, reach: int, what: str = "wounds", success: bool = True,
          writes: Writes | None = None) -> list[Event]:  # rule: 07.8.8
    """The state writes of a resolved Treat beat (the resolver frames and rolls it). Wounds, reach >= 1: the
    patient is `treated_today` (its brink wound ticks at dawn); a failure closes the day's treatment. First aid on
    the Dying: success stabilizes (07.2.7). Treat restores no Vitality (07.8.9 d)."""
    w = writes or Writes.of(ctx, source="07.8.8")
    start = len(w.events)
    if what == "dying":
        if success and harm_state(w, patient) == DYING:
            stabilize(ctx, patient, writes=w)
    elif what == "wounds":
        if success and reach >= 1:
            w.fact(patient, "treated_today", True, rule_id="07.8.8")
        elif not success:
            w.fact(patient, "treat_closed_today", True, rule_id="07.8.8")
        # coarse: 07.8.8 — per-wound treatment, Moderate healing and clock ticks wait for wound records (M2).
    else:
        w.coarse("07.8.8", "treating an affliction waits for afflictions (M2)", entity=patient)
    return w.events[start:]
