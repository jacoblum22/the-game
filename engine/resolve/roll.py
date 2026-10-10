"""ROLL and READ (01.8, 01.9; PR-01-3 steps 1-2): the degree rule, near miss, `roll_check`, delivered reach.

    res = roll_check(frame, rng)                          # refuses an uncommitted frame (00.13.2)
    read = read_result(frame, res, take_success_at_cost=True)
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from engine.resolve.types import DEGREES, REACH_VALUE, Degree, Frame, ReadResult, RollResult
from engine.rng import Rng

CRITICAL_BAND = 10  # resolution.yaml#degree_rule.critical_band (asserted equal in the tests)
NEAR_MISS_MIN = -3  # resolution.yaml#near_miss.min
D20 = 20


class RollRefused(ValueError):
    """roll_check refuses a frame that is not committed or breaks a frame invariant (00.13.2)."""


def base_degree(margin: int) -> Degree:  # rule: 01.8.1
    """Step 1: the degree by margin alone."""
    if margin >= CRITICAL_BAND:
        return "critical_success"
    if margin >= 0:
        return "success"
    if margin > -CRITICAL_BAND:
        return "failure"
    return "critical_failure"


def degree(d20: int, modifier: int, dc: int) -> Degree:  # rule: 01.8.1
    """The degree rule: margin bands, then a natural 20 one step up and a natural 1 one step down."""
    d = base_degree(d20 + modifier - dc)
    i = DEGREES.index(d)
    if d20 == D20:
        i = max(0, i - 1)
    elif d20 == 1:
        i = min(len(DEGREES) - 1, i + 1)
    return DEGREES[i]


def is_near_miss(deg: Degree, margin: int) -> bool:  # rule: 01.8.2
    """A final failure with margin >= -3 (includes a success a natural 1 stepped down)."""
    return deg == "failure" and margin >= NEAR_MISS_MIN


def _frame_fields(frame: Frame | Mapping[str, Any]) -> tuple[str | None, int, int, str | None, dict[str, Any]]:
    f = frame.record() if isinstance(frame, Frame) else dict(frame)
    total = int(f["modifier"]["total"])
    return f.get("id"), total, int(f["dc"]), f.get("offer_choice"), f


def check_rollable(frame: Frame | Mapping[str, Any]) -> None:  # rule: 00.13.2
    """The 00.13.2 invariants roll_check enforces; raises RollRefused naming the failure."""
    _, _, _, choice, f = _frame_fields(frame)
    gate = f.get("gate") or {}
    cls, mode = gate.get("class"), gate.get("mode")
    if cls not in ("G1", "G2", "G3"):
        raise RollRefused(f"gate {cls} never rolls")
    if cls == "G1" and not gate.get("verb"):
        raise RollRefused("G1 frame without a verb id")
    if cls == "G2" and not gate.get("license"):
        raise RollRefused("G2 frame without a license id")
    if cls == "G3" and mode != "fallback":
        raise RollRefused("G3 frame without an accepted crude fallback")
    if f.get("stakes") not in ("safe", "risky", "dire"):
        raise RollRefused("stakes rung unset")
    if f.get("lethal") and f.get("stakes") != "dire":
        raise RollRefused("lethal is legal only at Dire")
    if choice not in ("commit", "auto"):
        raise RollRefused(f"offer choice is {choice!r}: the frame is not committed (01.1.3)")
    if choice == "auto" and f.get("lethal"):
        raise RollRefused("a lethal frame is never auto-committed (01.7.4)")


def roll_check(frame: Frame | Mapping[str, Any], rng: Rng,
               on_roll: Callable[[RollResult], bool] | None = None) -> RollResult:  # rule: PR-01-3
    """Roll d20 for a committed frame; `on_roll` (fate reroll, 01.16.3) may ask for one reroll before the degree
    is final; returns total, margin, degree and near miss."""
    check_rollable(frame)
    fid, total_mod, dc, _, _ = _frame_fields(frame)
    rolled: list[int] = []
    face = rng.d(D20, f"roll_check {fid or 'frame'}")
    while True:
        total = face + total_mod
        margin = total - dc
        deg = degree(face, total_mod, dc)
        res = RollResult(frame_id=fid, d20=face, total=total, margin=margin, base_degree=base_degree(margin),
                         degree=deg, near_miss=is_near_miss(deg, margin), rerolled_from=list(rolled))
        if on_roll is None or rolled or not on_roll(res):
            return res
        rolled.append(face)
        face = rng.d(D20, f"roll_check {fid or 'frame'} reroll")


def delivered_reach(framed: str | int, deg: Degree, success_at_cost_taken: bool = False) -> int:  # rule: 01.9.1
    """T-01-4: critical success = framed + 1 (max 4); success or success-at-cost = framed; else 0."""
    r = framed if isinstance(framed, int) else REACH_VALUE[framed]
    if deg == "critical_success":
        return min(4, r + 1)
    if deg == "success" or (deg == "failure" and success_at_cost_taken):
        return r
    return 0


def read_result(frame: Frame, roll: RollResult, take_success_at_cost: bool | None = None) -> ReadResult:
    # rule: PR-01-3
    """READ: on a near miss the player's choice (01.9.3) is required; delivered reach (T-01-4) and the one cost
    due (T-01-5) with the menu ids it may come from."""
    from engine.resolve.costs import cost_severity  # costs imports nothing from here

    if roll.near_miss and take_success_at_cost is None:
        raise ValueError("near miss: the player's choice (failure or success at a cost) is required (01.9.3)")
    sac = bool(roll.near_miss and take_success_at_cost)
    reach = delivered_reach(frame.reach, roll.degree, sac)
    sev = cost_severity(frame.stakes, roll.degree, success_at_cost=sac)
    choices: list[str] = []
    if sev is not None:
        choices = [frame.threatened_cost.menu_id]
        if sac:  # 01.9.3 (DL-01-43): a price that reverses the goal carries no success-at-cost severity
            choices = [c.menu_id for c in (frame.threatened_cost, frame.alternate_cost)
                       if c is not None and c.on_success_at_cost] or choices
    return ReadResult(degree=roll.degree, near_miss=roll.near_miss, success_at_cost_taken=sac,
                      delivered_reach=reach,
                      cost_severity=sev, cost_choices=choices)
