"""The d20 checks ch.07 rolls itself (the dying check, the Gamble): no levers, snags or status (07.2.7, 07.5.10).

`degree` is 01.8.1's rule; engine/resolve owns the general check pipeline, and this is the same arithmetic for
the two resisted checks that take no declaration.
"""

from __future__ import annotations

from typing import Any

DEGREES = ("critical_failure", "failure", "success", "critical_success")


def degree(natural: int, modifier: int, dc: int) -> tuple[str, int]:  # rule: 01.8.1
    """(degree, margin) of `d20 + modifier` against `dc`."""
    margin = natural + modifier - dc
    i = 3 if margin >= 10 else 2 if margin >= 0 else 1 if margin > -10 else 0
    if natural == 20:
        i = min(3, i + 1)
    elif natural == 1:
        i = max(0, i - 1)
    return DEGREES[i], margin


def distribution(modifier: int, dc: int) -> dict[str, int]:  # rule: 01.8.1
    """Faces of the d20 (out of 20) per result, with `failure_within_3` split out of `failure` (the near band
    the dying check and the Gamble read; scales.yaml near_miss: margin -1..-3)."""
    out = {"critical_success": 0, "success": 0, "failure_within_3": 0, "failure": 0, "critical_failure": 0}
    for n in range(1, 21):
        d, m = degree(n, modifier, dc)
        out["failure_within_3" if d == "failure" and m >= -3 else d] += 1
    return out


def pct(faces: int) -> int:
    return faces * 5


def dc_of(rules: Any, tier: str) -> int:
    for r in rules.scales["obstacle_tiers"]["rungs"]:
        if r["id"] == tier and r.get("dc") is not None:
            return int(r["dc"])
    raise KeyError(f"no DC for tier {tier}")


def roll_d20(ctx: Any, purpose: str, natural: int | None = None) -> int:
    """The natural die: `natural` when the caller fixed it (a replayed or test roll), else `ctx.rng`."""
    if natural is not None:
        return natural
    rng = getattr(ctx, "rng", None)
    if rng is None:
        raise ValueError(f"{purpose}: no rng on the context and no fixed die")
    return int(rng.d(20, purpose))
