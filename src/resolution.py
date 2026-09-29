"""Deterministic degree-of-success resolution (Pattern P8 / research.md's fixed formula).

No network calls, no I/O -- this is the one piece of the system that must be fully
deterministic and unit-testable in isolation (plan.md's Testing decision). The model
never computes a roll or a degree itself; it only ever receives what this module produces,
via the roll_check tool in src/tools.py.

Formula (research.md):
    total = roll + modifier
    critical_success  if total >= dc + 10  OR  roll == 20
    critical_failure  if total <= dc - 10  OR  roll == 1
    success           if total >= dc   (and not already critical_success)
    failure           if total < dc    (and not already critical_failure)
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Optional

from state import Degree


@dataclass
class ResolutionResult:
    roll: int
    modifier: int
    total: int
    degree: Degree


def resolve(dc: int, modifier: int, roll: Optional[int] = None) -> ResolutionResult:
    """Compute a degree-of-success result.

    Args:
        dc: The target number to beat.
        modifier: Flat modifier added to the raw roll.
        roll: The raw d20 result. Pass an explicit value for deterministic testing;
            omitted in real play, where it's rolled here.

    Returns:
        A ResolutionResult with the raw roll, modifier, total, and computed degree.
    """
    if roll is None:
        roll = random.randint(1, 20)
    if not 1 <= roll <= 20:
        raise ValueError(f"roll must be between 1 and 20, got {roll}")

    total = roll + modifier

    if total >= dc + 10 or roll == 20:
        degree: Degree = "critical_success"
    elif total <= dc - 10 or roll == 1:
        degree = "critical_failure"
    elif total >= dc:
        degree = "success"
    else:
        degree = "failure"

    return ResolutionResult(roll=roll, modifier=modifier, total=total, degree=degree)
