"""Unit tests for src/resolution.py's pure degree-of-success calculation.

No network calls, no live model -- covers exactly the formula fixed in
specs/001-action-resolution-probe/research.md. Per tasks.md T007: normal
success/failure, critical success via both routes (threshold and nat 20),
critical failure via both routes (threshold and nat 1), and the exact
boundary cases.
"""

import pytest
from resolution import resolve


def test_normal_success():
    result = resolve(dc=15, modifier=2, roll=14)  # total 16, >=15, <25
    assert result.total == 16
    assert result.degree == "success"


def test_normal_failure():
    result = resolve(dc=15, modifier=2, roll=9)  # total 11, <15, >5
    assert result.total == 11
    assert result.degree == "failure"


def test_critical_success_via_threshold():
    result = resolve(dc=10, modifier=15, roll=15)  # total 30, well above dc+10=20
    assert result.total == 30
    assert result.degree == "critical_success"


def test_critical_success_via_natural_20_below_threshold():
    # roll=20, modifier=-10 -> total=10, well below dc+10=25, but nat 20 still applies
    result = resolve(dc=15, modifier=-10, roll=20)
    assert result.total == 10
    assert result.degree == "critical_success"


def test_critical_failure_via_threshold():
    result = resolve(dc=15, modifier=2, roll=3)  # total 5 == dc-10
    assert result.total == 5
    assert result.degree == "critical_failure"


def test_critical_failure_via_natural_1_above_threshold():
    # roll=1, modifier=+10 -> total=11, well above dc-10=5, but nat 1 still applies
    result = resolve(dc=15, modifier=10, roll=1)
    assert result.total == 11
    assert result.degree == "critical_failure"


def test_boundary_total_equals_dc_is_success():
    result = resolve(dc=15, modifier=2, roll=13)  # total exactly 15
    assert result.total == 15
    assert result.degree == "success"


def test_boundary_total_equals_dc_plus_10_is_critical_success():
    result = resolve(dc=15, modifier=10, roll=15)  # total exactly 25 == dc+10, roll != 20
    assert result.total == 25
    assert result.degree == "critical_success"


def test_boundary_total_equals_dc_minus_10_is_critical_failure():
    result = resolve(dc=15, modifier=0, roll=5)  # total exactly 5 == dc-10
    assert result.total == 5
    assert result.degree == "critical_failure"


def test_boundary_total_one_below_dc_is_failure_not_critical():
    result = resolve(dc=15, modifier=0, roll=6)  # total 6, dc-10=5, so 6 > 5 -> failure
    assert result.total == 6
    assert result.degree == "failure"


def test_invalid_roll_raises():
    with pytest.raises(ValueError):
        resolve(dc=15, modifier=0, roll=21)
    with pytest.raises(ValueError):
        resolve(dc=15, modifier=0, roll=0)


def test_random_roll_when_not_provided():
    result = resolve(dc=15, modifier=0)
    assert 1 <= result.roll <= 20
