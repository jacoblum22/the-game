"""engine/time/clock.py: the 00.7.1 ladder arithmetic, crossing detection and the 00.7.3 modes."""

from __future__ import annotations

import pytest

from engine.time import clock
from engine.time.clock import ROUNDS, TIME_UNITS, Timestamp


def test_ladder_lengths() -> None:
    assert ROUNDS["interval"] == 100 * ROUNDS["round"]
    assert ROUNDS["hour"] == 6 * ROUNDS["interval"]
    assert ROUNDS["watch"] == 6 * ROUNDS["hour"]
    assert ROUNDS["day"] == 4 * ROUNDS["watch"]
    assert ROUNDS["week"] == 7 * ROUNDS["day"]
    assert ROUNDS["season"] == 13 * ROUNDS["week"] == 91 * ROUNDS["day"]
    assert ROUNDS["year"] == 4 * ROUNDS["season"] == 364 * ROUNDS["day"]


def test_round_trip_and_ranges() -> None:
    assert clock.to_rounds(Timestamp()) == 0
    for n in (0, 1, 99, 100, 14_399, 14_400, 100_799, 1_310_400, 5_241_599, 5_241_600, 12_345_678):
        ts = clock.from_rounds(n, beat=3)
        clock.validate(ts)
        assert clock.to_rounds(ts) == n and ts.beat == 3
    last = clock.from_rounds(ROUNDS["year"] - 1)
    assert (last.season, last.week, last.day, last.watch, last.hour, last.interval, last.round) == (4, 13, 7, 3, 5, 5, 99)
    with pytest.raises(ValueError):
        clock.validate(Timestamp(watch=4))
    with pytest.raises(ValueError):
        clock.validate(Timestamp(day=0))


def test_advance_by_every_unit_and_alias() -> None:
    ts = Timestamp(beat=7)
    for u in TIME_UNITS:
        assert clock.to_rounds(clock.advance(ts, 2, u)) == 2 * ROUNDS[u]
        assert clock.advance(ts, 2, u + "s") == clock.advance(ts, 2, u)
    assert clock.advance(ts, 1, "day").beat == 7
    assert clock.advance(Timestamp(week=3, day=7), 1, "day") == Timestamp(week=4, day=1)
    with pytest.raises(ValueError):
        clock.advance(ts, -1, "hour")
    with pytest.raises(ValueError):
        clock.unit_of("action")  # part of a turn, no fixed length


@pytest.mark.parametrize("unit", TIME_UNITS)
def test_crossing_detection_on_every_unit(unit: str) -> None:
    n = ROUNDS[unit]
    start = 3 * n - 1  # one round before the third boundary of this unit
    rounds = unit == "round"
    hits = [(r, names) for r, names in clock.crossings(start - (0 if rounds else 99), start + 1, rounds=rounds)
            if unit in names]
    assert [r for r, _ in hits] == [3 * n]
    assert clock.crossed(start, start + 1, unit) == 1
    assert clock.crossed(3 * n, 3 * n + n - 1, unit) == 0  # the start instant itself is not crossed
    assert clock.crossed(0, 5 * n, unit) == 5


def test_crossings_order_and_rounds_only_in_conflict() -> None:
    year = ROUNDS["year"]
    got = dict(clock.crossings(year - 100, year))
    assert got == {year: ["interval", "hour", "watch", "day", "week", "season", "year"]}
    got_r = list(clock.crossings(year - 2, year, rounds=True))
    assert got_r == [(year - 1, ["round"]), (year, ["round", "interval", "hour", "watch", "day", "week", "season", "year"])]
    # outside conflict an advance of 250 rounds crosses intervals only at their multiples
    assert [r for r, _ in clock.crossings(50, 300)] == [100, 200, 300]


def test_split_and_day_index() -> None:
    assert clock.split(ROUNDS["watch"] * 2 + ROUNDS["interval"]) == {"watch": 2, "interval": 1}
    assert clock.split(ROUNDS["week"]) == {"day": 7}
    assert clock.split(0) == {}
    assert clock.day_index(Timestamp(week=2, day=1, watch=3)) == 7


def test_modes_and_beat_cost() -> None:
    assert set(clock.MODES) == {"conflict", "site", "free", "travel", "downtime"}
    assert clock.mode_of("scene") == "free" and clock.mode_of(None) == "free" and clock.mode_of("site") == "site"
    assert clock.beat_cost("conflict") == (0, "round")
    assert clock.beat_cost("site") == (1, "interval")
    assert clock.beat_cost("site", significant=False) == (0, "interval")
    assert clock.beat_cost("site", listed=(2, "intervals")) == (2, "interval")
    assert clock.beat_cost("free") == (0, "interval")
    assert clock.beat_cost("free", listed=(1, "hour")) == (1, "hour")
    assert clock.beat_cost("travel") == (1, "watch")
    assert clock.beat_cost("downtime", listed=(3, "days")) == (3, "day")


def test_fmt() -> None:
    assert clock.fmt(Timestamp(week=3, day=7, beat=12)) == "Y1 S1 W3 D7 morning +0h 0i r0 (beat 12)"
