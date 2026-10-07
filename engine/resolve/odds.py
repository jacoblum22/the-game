"""Odds for the OFFER (T-01-3; 01.6.12; PR-01-2 step 12): exhaustive enumeration of the twenty d20 faces."""

from __future__ import annotations

from engine.resolve.roll import D20, degree, is_near_miss
from engine.resolve.types import Odds

FACE_PCT = 100 // D20  # each face is 5%


def odds(modifier: int, dc: int) -> Odds:  # rule: T-01-3
    """Success-or-better, critical success, success, failure, critical failure and near-miss percentages;
    `need` is the lowest face from which every higher face succeeds; `only_natural_20` when 20 + total < DC."""
    counts = {"critical_success": 0, "success": 0, "failure": 0, "critical_failure": 0}
    near = 0
    ok_faces: list[int] = []
    for face in range(1, D20 + 1):
        d = degree(face, modifier, dc)
        counts[d] += 1
        if is_near_miss(d, face + modifier - dc):
            near += 1
        if d in ("critical_success", "success"):
            ok_faces.append(face)
    need = None
    for face in range(D20, 0, -1):  # the contiguous run of successes ending at 20
        if face not in ok_faces:
            break
        need = face
    return Odds(success_or_better=(counts["critical_success"] + counts["success"]) * FACE_PCT,
                critical_success=counts["critical_success"] * FACE_PCT, success=counts["success"] * FACE_PCT,
                failure=counts["failure"] * FACE_PCT, critical_failure=counts["critical_failure"] * FACE_PCT,
                near_miss=near * FACE_PCT, need=need, only_natural_20=D20 + modifier < dc)
