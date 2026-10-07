"""engine/resolve/roll.py: the degree rule (01.8.1), near miss (01.8.2), roll_check, delivered reach (01.9.1)."""

from __future__ import annotations

from pathlib import Path

import pytest

from engine.resolve.roll import RollRefused, check_rollable, degree, delivered_reach, is_near_miss, roll_check
from engine.rng import Rng
from tests.engine.test_resolve_scene import FixedRng


@pytest.mark.parametrize(("d20", "mod", "dc", "want"), [
    (10, 0, 10, "success"),            # a tie goes to the actor
    (9, 0, 10, "failure"),
    (20, 0, 10, "critical_success"),   # margin +10
    (19, 0, 10, "success"),
    (20, 0, 20, "critical_success"),   # success stepped up
    (20, 0, 30, "failure"),            # crit failure stepped up: only a failure (CT-5)
    (20, 5, 30, "success"),            # only a natural 20, and at best a plain success
    (1, 0, 10, "critical_failure"),    # failure stepped down
    (1, 9, 10, "failure"),             # success stepped down (a near miss)
    (1, 20, 10, "success"),            # critical success stepped down
    (5, 0, 15, "critical_failure"),    # margin -10
    (6, 0, 15, "failure"),
])
def test_degree_rule(d20: int, mod: int, dc: int, want: str) -> None:
    assert degree(d20, mod, dc) == want


def test_near_miss_band() -> None:
    assert is_near_miss("failure", -3) and is_near_miss("failure", -1) and is_near_miss("failure", 0)
    assert not is_near_miss("failure", -4) and not is_near_miss("critical_failure", -2)
    assert not is_near_miss("success", -1)


def _frame(**kw: object) -> dict[str, object]:
    f: dict[str, object] = {"id": "frame.1", "gate": {"class": "G1", "verb": "verb.move", "mode": "normal"},
                            "stakes": "risky", "lethal": False, "modifier": {"total": 4}, "dc": 15,
                            "offer_choice": "commit"}
    f.update(kw)
    return f


@pytest.mark.parametrize("bad", [
    {"offer_choice": None}, {"offer_choice": "withdraw"}, {"gate": {"class": "G3", "mode": "normal"}},
    {"gate": {"class": "G4"}}, {"gate": {"class": "G2", "license": None}}, {"stakes": None},
    {"lethal": True, "stakes": "risky"}, {"lethal": True, "stakes": "dire", "offer_choice": "auto"},
])
def test_roll_check_refuses_uncommitted_or_illegal(bad: dict[str, object]) -> None:
    with pytest.raises(RollRefused):
        check_rollable(_frame(**bad))


def test_roll_check_draws_one_d20_with_a_purpose(tmp_path: Path) -> None:
    rng = FixedRng([11])
    r = roll_check(_frame(), rng)
    assert (r.d20, r.total, r.margin, r.degree, r.near_miss) == (11, 15, 0, "success", False)
    assert rng.drawn == [("roll_check frame.1", 20, 11)]
    r2 = roll_check(_frame(), FixedRng([9]))
    assert (r2.margin, r2.near_miss) == (-2, True)


def test_roll_check_reroll_once_only() -> None:
    calls: list[int] = []

    def always(res: object) -> bool:
        calls.append(1)
        return True

    r = roll_check(_frame(), FixedRng([2, 3]), on_roll=always)
    assert (r.d20, r.rerolled_from, len(calls)) == (3, [2], 1)


def test_roll_check_is_seeded() -> None:
    a = [roll_check(_frame(), Rng(7)).d20 for _ in range(3)]
    rng = Rng(7)
    assert a[0] == roll_check(_frame(), rng).d20


@pytest.mark.parametrize(("framed", "deg", "sac", "want"), [
    ("standard", "critical_success", False, 3), ("great", "critical_success", False, 4),
    ("limited", "success", False, 1), ("standard", "failure", True, 2), ("standard", "failure", False, 0),
    ("great", "critical_failure", False, 0),
])
def test_delivered_reach(framed: str, deg: str, sac: bool, want: int) -> None:
    assert delivered_reach(framed, deg, sac) == want  # type: ignore[arg-type]
