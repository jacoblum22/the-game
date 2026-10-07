"""Using an ability (05.4; PR-05-1): validate in 05.4.1's order, cost by 05.6.3, show it at the OFFER, and on
commit spend Focus and one use (05.4.2). The resolver frames, rolls and applies the effects (steps 4, 7-8).

    chk = check_use(state, rules, "pc.wren", "ab.stone_skin", timing="beat")
    if not chk.ok: ...chk.refusal (nothing is spent; 01.3.6)...
    view = offer_view(state, rules, "pc.wren", "ab.stone_skin")          # literal text, cost, uses left
    res = commit_use(ctx, "pc.wren", "ab.stone_skin", frame_id="frame.3")
    tx.add_all(res.events)

The character's held abilities are `entity.data["abilities"]` (ability ids from creation; Milestone 1 holds
rank 1, the top-level fields of the abilities.yaml entry). A limited ability's uses are the quantity
`uses.<ability id>` (max = `limits.uses`), defined at the first use if creation did not define it.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

from engine.abilities.focus import OverdrawPrice, apply_overdraw, focus, is_spent, overdraw_price, spend_focus
from engine.harm.ctx import Writes
from engine.store.events import Event, Quantity
from engine.store.projection import WorldState

ACTIVATION_MAX = 6  # 05.6.3 step 7 (00.3.13)


def uses_key(ability_id: str) -> str:
    return f"uses.{ability_id}"


def held(state: WorldState, eid: str) -> list[str]:
    e = state.entities.get(eid)
    return [str(a) for a in (e.data.get("abilities") or ())] if e is not None else []


def uses_left(state: WorldState | Writes, rules: Any, eid: str, ability_id: str) -> int | None:
    """Uses remaining, or None for an unlimited ability (at will / Focus only)."""
    lim = rules.ability(ability_id).get("limits")
    if not lim:
        return None
    q = state.quantity(eid, uses_key(ability_id)) if isinstance(state, Writes) else \
        state.quantities.get(eid, {}).get(uses_key(ability_id))
    return q.current if q is not None else int(lim["uses"])


@dataclass
class Cost:
    total: int
    breakdown: list[tuple[str, int]] = field(default_factory=list)
    refusal: str | None = None


def ability_cost(ab: dict[str, Any], *, flares: int = 0, relic: bool = False, adjust: int = 0,
                 free: bool = False) -> Cost:  # rule: 05.6.3
    # rule: 05.6.2
    """05.6.3 in order: base, (emulate and stretch: M3), +1 per flare, +1 relic surcharge, adjust effects
    (reductions at most -1 and never below 1 from a base above 0; increases at most +2), above 6 not payable."""
    base = int((ab.get("cost") or {}).get("focus", 0))
    parts = [("base", base)]
    if flares:
        parts.append(("flares", flares))
    if relic:
        parts.append(("relic surcharge", 1))
    total = sum(n for _, n in parts)
    if adjust:
        adj = max(-1, min(2, adjust))
        if adj < 0 and base > 0:
            adj = max(adj, 1 - total)
        parts.append(("adjust", adj))
        total += adj
    if free:  # the Last Stand: abilities cost no Focus (07.5.9)
        parts.append(("last stand", -total))
        total = 0
    cost = Cost(total, parts)
    if total > ACTIVATION_MAX:
        biggest = max((p for p in parts if p[0] != "base"), key=lambda p: p[1], default=parts[0])
        cost.refusal = f"a cost of {total} is not payable (above {ACTIVATION_MAX}); drop the {biggest[0]}"
    return cost


@dataclass
class UseCheck:
    ok: bool
    ability_id: str
    refusal: str | None = None
    cost: Cost | None = None
    uses_left: int | None = None
    overdraw: OverdrawPrice | None = None  # the price the player must accept, when Focus falls short


def check_use(state: WorldState, rules: Any, eid: str, ability_id: str, *, timing: str | None = None,
              flares: Sequence[str] = (), rider_used: bool = False, relic: bool = False,
              adjust: int = 0) -> UseCheck:  # rule: 05.4.1
    # rule: 05.4.3
    # rule: 05.6.8
    # coarse: 05.4.4 — target legality (bands, conditions) is checked by the resolver at commitment.
    """Validate in order (05.4.1): held -> timing -> limitation -> uses -> exclusions -> Focus. The first failure
    is the refusal; nothing is spent."""
    def no(why: str, **kw: Any) -> UseCheck:
        return UseCheck(False, ability_id, why, **kw)

    if ability_id not in held(state, eid) or not rules.has(ability_id):  # (1) held
        return no("not held")
    ab = rules.ability(ability_id)
    if ab.get("activation") == "passive" or ab.get("timing") == "passive":
        return no("a passive ability is always on: there is nothing to activate")
    if timing is not None and ab.get("timing") != timing:  # (2) timing
        return no(f"its timing is {ab.get('timing')}, not {timing}")
    # (3) limitation clauses are prose that the resolver checks against the frame (targets, bands, conditions).
    left = uses_left(state, rules, eid, ability_id)  # (4) uses
    if left is not None and left < 1:
        per = (ab.get("limits") or {}).get("per")
        return no(f"no uses left (it returns at {per})", uses_left=0)
    if rider_used and ab.get("timing") == "rider":  # (5) one rider per beat (05.4.3)
        return no("one rider per beat: this beat already carries one")
    bad = [f for f in flares if f not in (ab.get("flares") or ())]
    if bad:
        return no(f"it cannot be flared {bad[0]}")
    if flares and is_spent(state, eid):
        return no("no flare while Spent (05.6.5)")
    if len(flares) > 1:
        return no("one flare per activation below master grade (05.6.8)")
    free = bool(state.fact_value(eid, "last_stand"))
    cost = ability_cost(ab, flares=len(flares), relic=relic, adjust=adjust, free=free)
    if cost.refusal:
        return no(cost.refusal, cost=cost, uses_left=left)
    q = focus(state, eid)  # (6) Focus
    have = q.current if q is not None else 0
    chk = UseCheck(True, ability_id, cost=cost, uses_left=left)
    if cost.total > have:
        if flares:
            return no("an overdraw cannot pay for a flare: drop the flare (05.6.6)", cost=cost, uses_left=left)
        price = overdraw_price(state, rules, eid, cost.total - have)
        if not price.ok:
            return no(f"not enough Focus ({have} of {cost.total}); {price.refusal}", cost=cost, uses_left=left)
        chk.overdraw = price
    return chk


def offer_view(state: WorldState, rules: Any, eid: str, ability_id: str, *, flares: Sequence[str] = ()) \
        -> dict[str, Any]:  # rule: PR-05-1
    """PR-05-1 step 5: the ability's literal text, the Focus cost and its breakdown, the uses left, any overdraw
    price. The resolver adds the odds, stakes and reach."""
    ab = rules.ability(ability_id)
    chk = check_use(state, rules, eid, ability_id, flares=flares)
    q = focus(state, eid)
    view: dict[str, Any] = {
        "ability_id": ability_id, "name": ab.get("name"), "text": ab.get("scope"), "limitation": ab.get("limitation"),
        "cost": chk.cost.total if chk.cost else None, "breakdown": chk.cost.breakdown if chk.cost else [],
        "focus": q.current if q is not None else 0, "uses_left": chk.uses_left,
        "per": (ab.get("limits") or {}).get("per"), "check": ab.get("check"), "refusal": chk.refusal}
    if chk.overdraw is not None:
        view["overdraw"] = {"shortfall": chk.overdraw.shortfall, "harm": chk.overdraw.severity,
                            "also": "one stack of exhausted until a long rest"}
    return view


@dataclass
class UseResult:
    events: list[Event]
    ability_id: str
    cost: int
    uses_left: int | None
    spent: bool
    overdraw: OverdrawPrice | None = None
    hooks: list[str] = field(default_factory=list)  # on_focus_spent (05.6.4) with the ability's first tag


def commit_use(ctx: Any, eid: str, ability_id: str, *, frame_id: str | None = None, timing: str | None = None,
               flares: Sequence[str] = (), accept_overdraw: bool = False, rider_used: bool = False,
               relic: bool = False, adjust: int = 0, writes: Writes | None = None) -> UseResult:  # rule: PR-05-1
    # rule: 05.4.2
    # rule: 05.4.8
    """PR-05-1 step 6, at the OFFER's commit: spend Focus (overdrawing the shortfall only when the player
    accepted the price) and one use; Spent if Focus is now 0. Raises ValueError with the refusal otherwise."""
    st: WorldState = ctx.state
    chk = check_use(st, ctx.rules, eid, ability_id, timing=timing, flares=flares, rider_used=rider_used,
                    relic=relic, adjust=adjust)
    if not chk.ok or chk.cost is None:
        raise ValueError(chk.refusal or "refused")
    if chk.overdraw is not None and not accept_overdraw:
        raise ValueError(f"needs an overdraw of {chk.overdraw.shortfall}: the player must accept its price")
    ab = ctx.rules.ability(ability_id)
    w = writes or Writes.of(ctx, source=frame_id or "use_ability")
    start = len(w.events)
    q = focus(w, eid)
    have = q.current if q is not None else 0
    pay = min(have, chk.cost.total)
    tag = str((ab.get("tags") or ["?"])[0])
    if pay:
        spend_focus(ctx, eid, pay, reason=f"{ability_id} ({tag})", frame_id=frame_id, writes=w)
    if chk.overdraw is not None:
        apply_overdraw(ctx, eid, chk.overdraw, frame_id=frame_id, writes=w)
        if (q2 := focus(w, eid)) is not None and q2.current == 0 and not is_spent(w, eid):
            w.fact(eid, "focus.spent", True, rule_id="05.6.6")
    left = chk.uses_left
    lim = ab.get("limits")
    if lim:
        key = uses_key(ability_id)
        if w.quantity(eid, key) is None:
            w.define(eid, key, Quantity(current=int(lim["uses"]), min=0, max=int(lim["uses"]), visibility="shown"),
                     reason=f"uses of {ability_id} ({lim['per']})", rule_id="05.4.6")
        w.add_quantity(eid, key, -1, reason=f"{ability_id} used", rule_id="05.4.2", frame_id=frame_id)
        left = (w.quantity(eid, key) or Quantity(current=0)).current
    res = UseResult(w.events[start:], ability_id, chk.cost.total, left, is_spent(w, eid), chk.overdraw)
    if chk.cost.total:
        res.hooks.append(f"on_focus_spent:{tag}:{chk.cost.total}")
    return res
