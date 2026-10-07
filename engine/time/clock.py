"""The time ladder (00.7.1) and the time modes (00.7.3): timestamp arithmetic and crossing detection.

The timestamp model is the store's `Timestamp` (engine/store/events.py), re-exported here; this module owns
its arithmetic. Fields nest exactly as the ladder does:

    year >= 1 | season 1..4 | week 1..13 (in the season) | day 1..7 (in the week) | watch 0..3 (0 morning,
    1 afternoon, 2 evening, 3 night) | hour 0..5 (in the watch) | interval 0..5 (in the hour) | round 0..99
    (in the interval) | beat (monotone counter, not a length of time)

Epoch (absolute round 0) is year 1, season 1, week 1, day 1, dawn. A day runs dawn to dawn.

    ts = advance(now, 3, "watch")
    crossed = list(crossings(to_rounds(now), to_rounds(ts)))   # [(round, ["interval", "hour", ...]), ...]
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Literal, get_args

from engine.store.events import Timestamp

__all__ = ["Timestamp", "TimeMode", "MODES", "TIME_UNITS", "ROUNDS", "WATCHES", "unit_of", "to_rounds",
           "from_rounds", "advance", "crossings", "crossed", "split", "mode_of", "beat_cost", "day_index", "fmt",
           "validate"]

# 00.7.1: the ladder, smallest to largest. `action` is part of a turn and has no fixed length (ch.06).
TIME_UNITS: tuple[str, ...] = ("round", "interval", "hour", "watch", "day", "week", "season", "year")
ROUNDS: dict[str, int] = {  # rule: 00.7.1
    "round": 1,
    "interval": 100,  # 10 minutes = 100 rounds of 6 s
    "hour": 600,  # 6 intervals
    "watch": 3_600,  # 6 hours
    "day": 14_400,  # 4 watches
    "week": 100_800,  # 7 days
    "season": 1_310_400,  # 13 weeks = 91 days
    "year": 5_241_600,  # 4 seasons = 364 days
}
WATCHES: tuple[str, ...] = ("morning", "afternoon", "evening", "night")
_ALIASES = {u + "s": u for u in TIME_UNITS}  # duration forms use plurals ("hours:2", substrate.yaml)

TimeMode = Literal["conflict", "site", "free", "travel", "downtime"]
MODES: tuple[str, ...] = get_args(TimeMode)


def unit_of(name: str) -> str:
    """'hours' -> 'hour'. Raises ValueError for anything not on the ladder (including 'action')."""
    u = _ALIASES.get(name, name)
    if u not in ROUNDS:
        raise ValueError(f"{name!r} is not a time unit with a length (00.7.1: {', '.join(TIME_UNITS)})")
    return u


def validate(ts: Timestamp) -> Timestamp:
    """Raise ValueError when a field is out of its ladder range."""  # rule: 00.7.1
    ranges = {"season": (1, 4), "week": (1, 13), "day": (1, 7), "watch": (0, 3), "hour": (0, 5),
              "interval": (0, 5), "round": (0, 99)}
    if ts.year < 1 or ts.beat < 0:
        raise ValueError(f"bad timestamp {ts}")
    for f, (lo, hi) in ranges.items():
        if not lo <= getattr(ts, f) <= hi:
            raise ValueError(f"timestamp {f}={getattr(ts, f)} outside {lo}..{hi} (00.7.1)")
    return ts


def to_rounds(ts: Timestamp) -> int:
    """Absolute rounds since the epoch (the beat counter is not time and is ignored)."""  # rule: 00.7.1
    return ((ts.year - 1) * ROUNDS["year"] + (ts.season - 1) * ROUNDS["season"] + (ts.week - 1) * ROUNDS["week"]
            + (ts.day - 1) * ROUNDS["day"] + ts.watch * ROUNDS["watch"] + ts.hour * ROUNDS["hour"]
            + ts.interval * ROUNDS["interval"] + ts.round)


def from_rounds(n: int, beat: int = 0) -> Timestamp:
    """The timestamp `n` rounds after the epoch."""  # rule: 00.7.1
    if n < 0:
        raise ValueError("time before the epoch")
    year, r = divmod(n, ROUNDS["year"])
    season, r = divmod(r, ROUNDS["season"])
    week, r = divmod(r, ROUNDS["week"])
    day, r = divmod(r, ROUNDS["day"])
    watch, r = divmod(r, ROUNDS["watch"])
    hour, r = divmod(r, ROUNDS["hour"])
    interval, rnd = divmod(r, ROUNDS["interval"])
    return Timestamp(year=year + 1, season=season + 1, week=week + 1, day=day + 1, watch=watch, hour=hour,
                     interval=interval, round=rnd, beat=beat)


def advance(ts: Timestamp, amount: int, unit: str) -> Timestamp:
    """`ts` moved forward by `amount` units (time never runs backward); the beat counter is kept."""
    if amount < 0:
        raise ValueError("time never runs backward (00.7.7)")
    return from_rounds(to_rounds(ts) + amount * ROUNDS[unit_of(unit)], beat=ts.beat)


def crossings(start: int, end: int, *, rounds: bool = False) -> Iterator[tuple[int, list[str]]]:
    """Every instant in (start, end] (absolute rounds) where a time boundary falls, in chronological order,
    with the boundaries at that instant smallest unit first (00.7.6). `round` boundaries are crossed only when
    `rounds` is true: the round is a conflict-only unit (00.7.1), so outside conflict mode the smallest
    boundary crossed is the interval."""  # rule: 00.7.7
    step = ROUNDS["round"] if rounds else ROUNDS["interval"]
    first = (start // step + 1) * step
    units = TIME_UNITS if rounds else TIME_UNITS[1:]
    for r in range(first, end + 1, step):
        yield r, [u for u in units if r % ROUNDS[u] == 0]


def crossed(start: int, end: int, unit: str) -> int:
    """How many `unit` boundaries fall in (start, end]."""  # rule: 00.7.7
    n = ROUNDS[unit_of(unit)]
    return max(0, end // n - start // n)


def split(rounds: int) -> dict[str, int]:
    """A span as whole ladder units, largest first, zero parts dropped: 7300 -> {'watch': 2, 'interval': 1}.
    Weeks and larger are left as days, so a remainder reads the way travel and downtime count it."""
    out: dict[str, int] = {}
    for u in ("day", "watch", "hour", "interval", "round"):
        q, rounds = divmod(rounds, ROUNDS[u])
        if q:
            out[u] = q
    return out


def day_index(ts: Timestamp) -> int:
    """Days since the epoch (a day runs dawn to dawn)."""  # rule: 00.7.1
    return to_rounds(ts) // ROUNDS["day"]


def mode_of(value: str | None) -> TimeMode:
    """A stored mode as a 00.7.3 mode; anything else (none set yet, the store's default 'scene') is `free`,
    the rule's default when uncertain."""  # rule: 00.7.3
    return value if value in MODES else "free"  # type: ignore[return-value]


def beat_cost(mode: str, *, significant: bool = True, listed: tuple[int, str] | None = None) -> tuple[int, str]:
    """Time one beat consumes in `mode` (00.7.3), as (amount, unit).

    conflict: 0 (time advances one round at each round's end, marked by the conflict loop); site: 1 interval
    for a significant beat, 0 otherwise (a listed activity duration overrides, 10.13.5); free: the activity's
    listed duration, unlisted 0; travel: 1 watch per travel activity; downtime: the listed duration (days)."""
    # rule: 00.7.3
    m = mode_of(mode)
    if m == "conflict":
        return (0, "round")
    if listed is not None:
        return (listed[0], unit_of(listed[1]))
    if m == "site":
        return (1, "interval") if significant else (0, "interval")
    if m == "travel":
        return (1, "watch")
    if m == "downtime":
        return (0, "day")
    return (0, "interval")


def fmt(ts: Timestamp) -> str:
    """'Y1 S1 W3 D7 morning +2h 3i r0 (beat 12)'."""
    return (f"Y{ts.year} S{ts.season} W{ts.week} D{ts.day} {WATCHES[ts.watch]} +{ts.hour}h {ts.interval}i "
            f"r{ts.round} (beat {ts.beat})")
