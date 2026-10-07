"""Focus (05.6): the pool, paying, Spent, overdraw and push. Focus is the quantity `focus` on the character;
Spent is the fact `focus.spent`; counters are meta keys `<pc>.<counter>` (engine/harm/ctx.counter_key).

    tx.add(define_focus("pc.wren", base=4))                       # creation: focus.max = base + T_high + breadth
    tx.add_all(spend_focus(ctx, "pc.wren", 2, reason="ab.x"))     # 05.6.4; Spent at 0 (05.6.5)
    price = overdraw_price(state, rules, "pc.wren", shortfall=1)  # 05.6.6: S2 strain, an exhausted stack
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from engine.harm.apply import apply_harm, severity_harm
from engine.harm.ctx import Writes, counter_key
from engine.harm.state import DYING, STAGGERED, VITALITY, harm_state
from engine.store.conditions import apply_condition
from engine.store.events import Event, Quantity
from engine.store.projection import WorldState

FOCUS = "focus"
SPENT = "focus.spent"
CAP = 12  # 05.6.1


def focus_max(base: int = 4, t_high: int = 0, breadth: int = 0) -> int:  # rule: 05.6.1
    """base (3..5, set at creation) + the highest confirmed calling tier + breadth (at most 3), clamped to 12."""
    return min(CAP, base + max(0, t_high) + max(0, min(3, breadth)))


def define_focus(eid: str, *, base: int = 4, t_high: int = 0, breadth: int = 0) -> Event:  # rule: 05.6.1
    """The `focus` quantity for a new character, full."""
    mx = focus_max(base, t_high, breadth)
    return Event.of("quantity_defined", source="05.6.1", rule_id="05.6.1", entity=eid, quantity=FOCUS,
                    value=Quantity(current=mx, min=0, max=mx), reason="focus pool (05.6.1)")


def focus(state: WorldState | Writes, eid: str) -> Quantity | None:
    if isinstance(state, Writes):
        return state.quantity(eid, FOCUS)
    return state.quantities.get(eid, {}).get(FOCUS)


def is_spent(state: WorldState | Writes, eid: str) -> bool:  # rule: 05.6.5
    return bool(state.fact_value(eid, SPENT, False))


def _spent_flag(w: Writes, eid: str) -> None:  # rule: 05.6.5
    q = w.quantity(eid, FOCUS)
    if q is None:
        return
    if q.current == 0 and not is_spent(w, eid):
        w.fact(eid, SPENT, True, rule_id="05.6.5")
    elif q.current >= 1 and is_spent(w, eid):
        w.fact(eid, SPENT, False, rule_id="05.6.5")


def spend_focus(ctx: Any, eid: str, n: int, *, reason: str, frame_id: str | None = None,
                writes: Writes | None = None) -> list[Event]:  # rule: 05.6.4
    """`update_quantity(focus, -n)`: never below 0 (an unpayable spend is refused, ValueError)."""
    w = writes or Writes.of(ctx, source="05.6.4")
    start = len(w.events)
    q = w.quantity(eid, FOCUS)
    if n <= 0:
        return []
    if q is None or q.current < n:
        raise ValueError(f"{eid} cannot pay {n} Focus")
    w.add_quantity(eid, FOCUS, -n, reason=reason, rule_id="05.6.4", frame_id=frame_id)
    _spent_flag(w, eid)
    return w.events[start:]


def restore_focus(ctx: Any, eid: str, *, amount: int | None = None, to: int | None = None, reason: str,
                  rule_id: str = "05.6.9", writes: Writes | None = None) -> list[Event]:  # rule: 05.6.9
    """Raise Focus by `amount` or to `to` (never lowering), clamped to the maximum; Spent ends at 1 or more."""
    w = writes or Writes.of(ctx, source=rule_id)
    start = len(w.events)
    q = w.quantity(eid, FOCUS)
    if q is None:
        return []
    new = q.current + amount if amount is not None else max(q.current, to if to is not None else q.current)
    w.set_quantity(eid, FOCUS, new, reason=reason, rule_id=rule_id)
    _spent_flag(w, eid)
    return w.events[start:]


@dataclass
class OverdrawPrice:
    shortfall: int
    severity: str | None = None
    harm: int = 0
    refusal: str | None = None

    @property
    def ok(self) -> bool:
        return self.refusal is None


def overdraw_price(state: WorldState, rules: Any, eid: str, shortfall: int) -> OverdrawPrice:
    """05.6.6: a shortfall of 1/2/3 deals S2/S3/S4 `harm.mind.strain` (no reduction, lethal: false) and one
    `cond.exhausted` stack. Refused above 3, past three overdraws since the long rest, when Staggered or Dying,
    or when it would bring Vitality to 0."""  # rule: 05.6.6
    o = rules.doc("abilities")["focus"]["overdraw"]
    if shortfall > 3 or shortfall < 1:
        return OverdrawPrice(shortfall, refusal="a shortfall above 3 Focus is not payable")
    sev = str(o["harm_by_shortfall"][shortfall])
    harm = severity_harm(rules, sev)
    price = OverdrawPrice(shortfall, sev, harm)
    v = state.quantities.get(eid, {}).get(VITALITY)
    if harm_state(state, eid) in (STAGGERED, DYING):
        price.refusal = "a Staggered or Dying character cannot overdraw"
    elif int(state.meta.get(counter_key(eid, "overdraws_since_long_rest"), 0) or 0) >= int(o["max_between_long_rests"]):
        price.refusal = "three overdraws already since the last long rest"
    elif v is None or v.current - harm <= 0:
        price.refusal = "the overdraw would bring Vitality to 0"
    return price


def apply_overdraw(ctx: Any, eid: str, price: OverdrawPrice, *, frame_id: str | None = None,
                   writes: Writes | None = None) -> list[Event]:  # rule: 05.6.6
    """Pay an accepted overdraw: the strain through apply_harm and one exhausted stack; count it."""
    if not price.ok or price.severity is None:
        raise ValueError(price.refusal or "no overdraw price")
    w = writes or Writes.of(ctx, source="05.6.6")
    start = len(w.events)
    apply_harm(ctx, eid, severity=price.severity, harm_tags=["harm.mind.strain"], source=eid, frame_id=frame_id,
               lethal=False, no_reduction=True, writes=w)
    w.extend(apply_condition(ctx.state, w.mint, ctx.rules, eid, "cond.exhausted", duration="until_rest:rest_long",
                             source={"entity": eid, "effect_id": None, "frame_id": frame_id},
                             rule_id="05.6.6").events)
    key = counter_key(eid, "overdraws_since_long_rest")
    w.meta(key, int(w.meta_value(key, 0) or 0) + 1, rule_id="05.6.6")
    return w.events[start:]


def push(ctx: Any, eid: str, *, choice: str, frame_id: str | None = None,
         writes: Writes | None = None) -> list[Event]:  # rule: 05.6.7
    """Spend 1 Focus on one's own declared, rolled beat: `reach` (+1 rung), `stakes` (-1 rung) or `grit`. Not while
    Spent; once per beat and the competence test are the resolver's (it knows the beat). Returns the spend."""
    if choice not in ("reach", "stakes", "grit"):
        raise ValueError(f"push choice {choice!r}")
    if is_spent(ctx.state if writes is None else writes, eid):
        raise ValueError("no push while Spent (05.6.5)")
    return spend_focus(ctx, eid, 1, reason=f"push ({choice})", frame_id=frame_id, writes=writes)


def restore_focus_consumable(ctx: Any, eid: str, n: int, *, item: str,
                             writes: Writes | None = None) -> list[Event]:  # rule: 05.6.11
    """`eff.restore {quantity: focus}` from an item: at most 4 Focus between long rests from consumables; past it
    a draught restores nothing (the codex says so before it is drunk)."""
    w = writes or Writes.of(ctx, source=item)
    start = len(w.events)
    key = counter_key(eid, "restored_by_consumables_since_long_rest")
    used = int(w.meta_value(key, 0) or 0)
    q = w.quantity(eid, FOCUS)
    give = max(0, min(n, 4 - used, (q.max or 0) - q.current if q is not None else 0))
    if give:
        restore_focus(ctx, eid, amount=give, reason=f"{item} (+{give})", rule_id="05.6.11", writes=w)
        w.meta(key, used + give, rule_id="05.6.11")
    return w.events[start:]
