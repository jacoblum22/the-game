"""Parity with the canonical tables (T029): odds against every cell of T-01-3, Oracle shapes against T-01-10.

The tables' cited sims (`odds01.py`, `oracle01.py`) are not in the repo, so the tests read the tables themselves
(through rules/tools/rq.py, so a rules change is picked up) and the data they cite (resolution.yaml).
"""

from __future__ import annotations

import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pytest

from engine.data.loader import load_rules
from engine.resolve.odds import odds
from engine.resolve.oracle import shape_for
from engine.resolve.roll import CRITICAL_BAND, NEAR_MISS_MIN

ROOT = Path(__file__).resolve().parents[2]
SHAPES = ["yes_and", "yes", "yes_but", "no_but", "no", "no_and"]


def _rq(rule_id: str) -> str:
    out = subprocess.run([sys.executable, str(ROOT / "rules/tools/rq.py"), rule_id], capture_output=True, text=True,
                         check=True, cwd=ROOT)
    return out.stdout


def _t013() -> list[tuple[int, int, list[int]]]:
    """(modifier, DC, [success-or-better, crit success, success, failure, crit failure, near miss]) per cell."""
    txt = _rq("T-01-3")
    header = next(line for line in txt.splitlines() if line.startswith("| Mod"))
    dcs = [int(x) for x in re.findall(r"(\d+)\s*\|", header)]
    cells = []
    for line in txt.splitlines():
        m = re.match(r"\|\s*([+−-]\d+)\s*\|(.*)\|\s*$", line)
        if not m:
            continue
        mod = int(m.group(1).replace("−", "-"))
        for dc, cell in zip(dcs, m.group(2).split("|"), strict=True):
            cells.append((mod, dc, [int(x) for x in re.findall(r"\d+", cell)]))
    return cells


CELLS = _t013()


def test_t_01_3_is_the_whole_table() -> None:
    assert len(CELLS) == 19 * 5 and {c[1] for c in CELLS} == {10, 15, 20, 25, 30}
    assert {c[0] for c in CELLS} == set(range(-2, 17))


@pytest.mark.parametrize(("mod", "dc", "want"), CELLS, ids=[f"{m:+d}vs{d}" for m, d, _ in CELLS])
def test_odds_parity_t_01_3(mod: int, dc: int, want: list[int]) -> None:
    o = odds(mod, dc)
    assert [o.success_or_better, o.critical_success, o.success, o.failure, o.critical_failure, o.near_miss] == want


def test_odds_constants_match_data() -> None:
    r = load_rules()
    assert CRITICAL_BAND == r.resolution["degree_rule"]["critical_band"]
    assert NEAR_MISS_MIN == r.resolution["near_miss"]["min"]
    assert [t["dc"] for t in r.resolution["dc_tiers"] if t.get("dc")] == [10, 15, 20, 25, 30]


def test_calibration_targets_ct_1_to_ct_6() -> None:
    """T-01-3's calibration proof, recomputed."""
    s = lambda m, dc: odds(m, dc).success_or_better  # noqa: E731
    assert s(2, 10) >= 60
    assert 50 <= s(5, 15) <= 65 and 30 <= s(1, 15) <= 40
    assert 25 <= s(5, 20) <= 35 and 45 <= s(9, 20) <= 55
    assert s(5, 25) <= 10 and 35 <= s(12, 25) <= 45
    assert 20 <= s(14, 30) <= 30
    for m in range(-8, 10):
        o = odds(m, 30)
        assert o.need in (20, None) and (o.success_or_better <= 5)
    for m in range(-8, 17):
        for dc in (10, 15, 20, 25, 30):
            o = odds(m, dc)
            if o.success_or_better >= 50:
                assert o.critical_failure <= 5


def test_only_natural_20_flag() -> None:
    o = odds(5, 30)
    assert o.only_natural_20 and o.success_or_better == 5 and o.critical_success == 0 and o.need == 20
    assert odds(0, 30).success_or_better == 0 and odds(0, 30).need is None  # the stepped-up crit fail is a failure


def _t0110() -> dict[str, tuple[int, list[int]]]:
    out = {}
    for line in _rq("T-01-10").splitlines():
        m = re.match(r"\|\s*(Likely|Even|Unlikely|Remote)\s*\|\s*(\d+)\+\s*\|(.*)\|\s*$", line)
        if m:
            out[m.group(1).lower()] = (int(m.group(2)), [int(x) for x in m.group(3).split("|")])
    return out


def test_oracle_parity_t_01_10() -> None:
    """Every rung: the threshold and the faces per shape (yes-and, yes, yes-but, no-but, no, no-and, total yes)."""
    r = load_rules()
    table = _t0110()
    assert set(table) == {"likely", "even", "unlikely", "remote"}
    for rung, (yes_on, want) in table.items():
        assert next(x for x in r.resolution["oracle"]["rungs"] if x["id"] == rung)["yes_on"] == yes_on
        c = Counter(shape_for(r, rung, d) for d in range(1, 101))
        got = [c[s] for s in SHAPES]
        assert [*got, c["yes_and"] + c["yes"] + c["yes_but"]] == want, rung
        assert got == list(r.resolution["oracle"]["odds_faces"][rung])


def test_oracle_shape_edges() -> None:
    r = load_rules()
    assert shape_for(r, "unlikely", 83) == "yes"  # WE-01-11: not in 76-80, not a double
    assert [shape_for(r, "unlikely", d) for d in (76, 80, 81, 71, 75, 70)] == [
        "yes_but", "yes_but", "yes", "no_but", "no_but", "no"]
    assert shape_for(r, "likely", 22) == "no_and" and shape_for(r, "likely", 100) == "yes_and"
    assert shape_for(r, "remote", 99) == "yes_and" and shape_for(r, "remote", 88) == "no_and"
