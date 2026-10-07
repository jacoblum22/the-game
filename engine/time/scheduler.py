"""Advancing time and processing boundaries (PR-00-2; 00.7.4-00.7.9; T015).

    ctx = TimeContext(tx, rules, rng)                       # inside `with store.transaction(turn_id) as tx`
    res = advance_time(ctx, 5, "watch", "travel to Grey Keep", marks=[Mark("rest_long", rest_payload, after=..)])
    res.interrupt, res.remainder_rounds, res.narration      # halted? what is left? what to narrate (INV-2)
    mark_boundary(ctx, "scene_end")                         # an event boundary, now (00.7.2)
    set_mode(ctx, "site", "entered the barrow")             # 00.7.3; marks mode_change

Every boundary crossed runs every registered handler in phase order (00.7.5); simultaneous boundaries run
event boundaries first, then time boundaries smallest to largest (00.7.6); a skip runs every boundary it
crosses (00.7.7, INV-15). Events written, in order, per instant: `time_advanced` (from the previous instant to
this one, naming its boundaries), then per boundary `boundary_marked` and one `handler_ran` / `handler_skipped`
per registry row (after the handler's own events). An interrupt halts after the instant and writes a
zero-span `time_advanced` carrying `interrupt` and `remainder`.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from engine.data.loader import Rules
from engine.rng import Rng
from engine.store.db import Transaction
from engine.store.events import Event, Timestamp
from engine.store.projection import WorldState
from engine.time import clock
from engine.time import handlers as registry
from engine.time.handlers import HandlerResult

# 00.7.6: event boundaries at one instant run first, in this order. The rule orders conflict_end, scene_end,
# the rest completions, reflection and venture_end; the others are placed so that ends come before starts.
EVENT_ORDER: tuple[str, ...] = (
    "beat_end", "turn_end", "conflict_end", "scene_end", "breather", "rest_short", "rest_long", "reflection",
    "venture_end", "session_end", "venture_start", "mode_change", "scene_start", "conflict_start", "turn_start",
    "session_start",
)
REST_ORDER: tuple[str, ...] = ("breather", "rest_short", "rest_long")


class SchedulerError(RuntimeError):
    """A misuse of the scheduler or a handler breaking the registry contract."""


@dataclass
class TimeContext:
    """What a handler sees. `now`, `boundary`, `payload`, `phase` and `handler_id` are set by the scheduler
    for each handler call."""

    tx: Transaction
    rules: Rules
    rng: Rng | None = None
    milestone: int = 0  # 0: the game's milestone (game_created)
    now: Timestamp = field(default_factory=Timestamp)
    boundary: str = ""
    payload: dict[str, Any] = field(default_factory=dict)
    phase: int = 0
    handler_id: str = ""

    def __post_init__(self) -> None:
        if not self.milestone:
            game = self.tx.state.game
            self.milestone = game.milestone if game else 1
        self.now = self.tx.state.time.now

    @property
    def state(self) -> WorldState:
        return self.tx.state

    def emit(self, *events: Event) -> list[int]:
        """Stage events at the current boundary instant; `source` defaults to the running handler's id."""
        out = []
        for ev in events:
            upd: dict[str, Any] = {}
            if ev.game_time is None:
                upd["game_time"] = self.now
            if ev.source == "engine" and self.handler_id:
                upd["source"] = self.handler_id
            out.append(self.tx.add(ev.model_copy(update=upd) if upd else ev))
        return out


@dataclass(frozen=True)
class Mark:
    """An event boundary that falls inside an advance (a rest completing): `after` rounds from the start,
    None = at the target instant. Payload per 00.7.2 (rests: {quality, site, treated})."""

    boundary: str
    payload: Mapping[str, Any] = field(default_factory=dict)
    after: int | None = None


@dataclass
class HandlerOutcome:
    handler_id: str
    phase: int
    ran: bool
    summary: str = ""  # the result summary, or the skip reason
    milestone: int | None = None  # skipped: the milestone that builds it


@dataclass
class BoundaryResult:
    boundary: str
    at: Timestamp
    payload: dict[str, Any]
    handlers: list[HandlerOutcome] = field(default_factory=list)
    narration: list[str] = field(default_factory=list)
    effects: list[Mapping[str, Any]] = field(default_factory=list)
    interrupt: tuple[str, str] | None = None  # (handler id, reason)
    chained: list[tuple[str, dict[str, Any]]] = field(default_factory=list)  # event boundaries fired by handlers


@dataclass
class AdvanceResult:
    start: Timestamp
    target: Timestamp
    end: Timestamp  # where the clock stopped: the target, or the interrupting instant
    boundaries: list[BoundaryResult] = field(default_factory=list)
    interrupt: tuple[str, str] | None = None
    remainder_rounds: int = 0
    unfired: list[Mark] = field(default_factory=list)  # marks after the halt (a rest that did not complete)

    @property
    def halted_at(self) -> Timestamp | None:
        return self.end if self.interrupt else None

    @property
    def remainder(self) -> dict[str, int]:
        return clock.split(self.remainder_rounds)

    @property
    def narration(self) -> list[str]:
        """Everything handlers emitted for narration, in order (PR-00-2 step 5; the DM adds nothing, INV-2)."""
        return [n for b in self.boundaries for n in b.narration]


# ----------------------------------------------------------------------------------------- registry order

_PLANS: dict[tuple[str, str], list[Mapping[str, Any]]] = {}


def plan(rules: Rules, boundary: str) -> list[Mapping[str, Any]]:
    """The registry rows that run at `boundary`, in run order: phase, then owner chapter, then handler id,
    with `before` honored inside a phase (00.7.5)."""  # rule: 00.7.5
    key = (rules.hash, boundary)
    if key in _PLANS:
        return _PLANS[key]
    rows = []
    for h in rules.boundary_handlers():
        b = h["boundary"]
        if b == "*" or b == boundary or (not isinstance(b, str) and boundary in b):
            rows.append(h)
    rows.sort(key=lambda h: (int(h["phase"]), int(h["owner"]), str(h["id"])))
    for h in [r for r in rows if r.get("before")]:
        targets = [i for i, r in enumerate(rows) if r["id"] in h["before"] and r["phase"] == h["phase"]]
        if targets and rows.index(h) > min(targets):
            rows.remove(h)
            rows.insert(min(targets), h)
    _PLANS[key] = rows
    return rows


def all_boundaries(rules: Rules) -> tuple[list[str], list[str]]:
    """(time boundaries, event boundaries) from boundaries.yaml."""
    b = rules.boundaries["boundaries"]
    return list(b["time"]), list(b["event"])


def _event_rank(boundary: str) -> int:
    return EVENT_ORDER.index(boundary) if boundary in EVENT_ORDER else len(EVENT_ORDER)


def order_instant(names: Sequence[str]) -> list[str]:
    """Simultaneous boundaries in 00.7.6 order: event boundaries first, then time boundaries small to large."""
    # rule: 00.7.6
    ev = sorted((n for n in names if n not in clock.ROUNDS), key=_event_rank)
    tm = sorted((n for n in names if n in clock.ROUNDS), key=clock.TIME_UNITS.index)
    return ev + tm


# ------------------------------------------------------------------------------------------- dispatch


def _run_boundary(ctx: TimeContext, boundary: str, payload: Mapping[str, Any]) -> BoundaryResult:
    """One boundary: boundary_marked, then phases 1-9, each registry row run or logged as skipped."""
    # rule: PR-00-2
    res = BoundaryResult(boundary=boundary, at=ctx.now, payload=dict(payload))
    ctx.boundary, ctx.payload = boundary, dict(payload)
    ctx.handler_id = ""
    ctx.emit(Event.of("boundary_marked", source="time", rule_id="PR-00-2", boundary=boundary,
                      payload=dict(payload)))
    for row in plan(ctx.rules, boundary):
        hid, phase = str(row["id"]), int(row["phase"])
        fn = registry.runnable(hid, ctx.milestone)
        if fn is None:  # rule: 00.7.4
            ms = registry.milestone_of(hid)
            ctx.handler_id = ""
            ctx.emit(Event.of("handler_skipped", source=hid, rule_id="PR-00-2", handler_id=hid, boundary=boundary,
                              phase=phase, reason="not yet built", milestone=ms))
            res.handlers.append(HandlerOutcome(hid, phase, False, "not yet built", ms))
            continue
        ctx.handler_id, ctx.phase = hid, phase
        out = fn(ctx) or HandlerResult()
        ctx.handler_id = ""
        rule_id = str(row["rule_id"]) if row.get("rule_id") else "PR-00-2"
        ctx.emit(Event.of("handler_ran", source=hid, rule_id=rule_id, handler_id=hid, boundary=boundary, phase=phase,
                          result=out.summary))
        res.handlers.append(HandlerOutcome(hid, phase, True, out.summary))
        res.narration += out.narration
        res.effects += out.effects
        if out.interrupt:  # rule: 00.7.8
            if row.get("interrupting") is False:
                raise SchedulerError(f"{hid} raised an interrupt but is not interrupting in boundaries.yaml")
            if res.interrupt is None:
                res.interrupt = (hid, out.interrupt)
        res.chained += out.chain
    return res


def _run_instant(ctx: TimeContext, queue: list[tuple[str, Mapping[str, Any]]]) -> list[BoundaryResult]:
    """Run every boundary at the current instant, adding chained event boundaries (reflection) in 00.7.6
    order: a chained event boundary runs before any time boundary still queued."""  # rule: 00.7.6
    done: list[BoundaryResult] = []
    while queue:
        b, p = queue.pop(0)
        r = _run_boundary(ctx, b, p)
        done.append(r)
        for cb, cp in r.chained:
            _check_event(ctx.rules, cb)
            i = next((k for k, (qb, _) in enumerate(queue) if qb in clock.ROUNDS or _event_rank(qb) > _event_rank(cb)),
                     len(queue))
            queue.insert(i, (cb, cp))
    return done


def _check_event(rules: Rules, boundary: str) -> None:
    _, events = all_boundaries(rules)
    if boundary not in events:
        raise SchedulerError(f"{boundary!r} is not an event boundary (00.7.2; time boundaries come from advance_time)")


def _time_event(ctx: TimeContext, frm: Timestamp, to: Timestamp, boundaries: list[str], reason: str, *,
                interrupt: str | None = None, remainder: dict[str, int] | None = None,
                mode: str | None = None) -> None:
    ev = Event.of("time_advanced", {"from": frm}, source=reason or "time", rule_id="PR-00-2", to=to,
                  boundaries=boundaries, interrupt=interrupt, remainder=remainder, mode=mode)
    ctx.handler_id = ""
    ctx.tx.add(ev.model_copy(update={"game_time": frm}))
    ctx.now = to


def advance_time(ctx: TimeContext, amount: int, unit: str, reason: str, *, marks: Sequence[Mark] = (),
                 mode: str | None = None) -> AdvanceResult:
    """PR-00-2 `advance_time`: move the game clock `amount` units forward, running every boundary crossed
    (and every `marks` event boundary at its instant) in chronological and 00.7.6 order. Halts after the
    instant where a handler interrupts (00.7.8) and returns the remainder; the remainder is not spent.
    `mode` switches the time mode first (set_mode)."""  # rule: PR-00-2
    if amount < 0:
        raise SchedulerError("advance_time never runs backward")
    if mode is not None:
        set_mode(ctx, mode, reason)
    start = ctx.tx.state.time.now
    ctx.now = start
    start_r = clock.to_rounds(start)
    span = amount * clock.ROUNDS[clock.unit_of(unit)]
    end_r = start_r + span
    target = clock.from_rounds(end_r, beat=start.beat)
    result = AdvanceResult(start=start, target=target, end=target)
    if span == 0:
        if marks:
            raise SchedulerError("marks inside a zero-length advance: use mark_boundary")
        return result

    # 1. every instant in (start, end]: time boundaries crossed plus marked event boundaries (00.7.7)
    at: dict[int, list[tuple[str, Mapping[str, Any]]]] = {}
    for m in marks:
        _check_event(ctx.rules, m.boundary)
        off = span if m.after is None else m.after
        if not 0 < off <= span:
            raise SchedulerError(f"mark {m.boundary} at {off} rounds is outside the advance (0, {span}]")
        at.setdefault(start_r + off, []).append((m.boundary, m.payload))
    in_conflict = clock.mode_of(ctx.tx.state.time.mode) == "conflict"
    for r, names in clock.crossings(start_r, end_r, rounds=in_conflict):
        at.setdefault(r, []).extend((n, {}) for n in names)

    # 2-3. run each instant; halt after an interrupting one
    prev = start
    for r in sorted(at):
        items = at[r]
        names = order_instant([n for n, _ in items])
        payloads: dict[str, list[Mapping[str, Any]]] = {}
        for n, p in items:
            payloads.setdefault(n, []).append(p)
        queue = [(n, payloads[n].pop(0)) for n in names]
        ts = clock.from_rounds(r, beat=start.beat)
        _time_event(ctx, prev, ts, names, reason)
        prev = ts
        done = _run_instant(ctx, queue)
        result.boundaries += done
        hit = next((b.interrupt for b in done if b.interrupt), None)
        if hit:
            result.interrupt = hit
            result.end = ts
            result.remainder_rounds = end_r - r
            result.unfired = [m for m in marks if start_r + (span if m.after is None else m.after) > r]
            _time_event(ctx, ts, ts, [], reason, interrupt=f"{hit[0]}: {hit[1]}",
                        remainder=clock.split(result.remainder_rounds))
            return result
    # 4. no interrupt: the clock reaches the target
    if clock.to_rounds(prev) != end_r:
        _time_event(ctx, prev, target, [], reason)
    return result


def mark_boundary(ctx: TimeContext, boundary: str, payload: Mapping[str, Any] | None = None) -> list[BoundaryResult]:
    """PR-00-2 `mark_boundary`: fire an event boundary now (00.7.2), with any boundaries its handlers chain
    (reflection). Fictional time does not move; `beat_end` advances the beat counter (00.7.1). An interrupt
    is reported on the returned BoundaryResult."""  # rule: PR-00-2
    _check_event(ctx.rules, boundary)
    now = ctx.tx.state.time.now
    ctx.now = now
    if boundary == "beat_end":  # rule: 00.7.1
        _time_event(ctx, now, now.model_copy(update={"beat": now.beat + 1}), ["beat_end"], "beat_end")
    return _run_instant(ctx, [(boundary, dict(payload or {}))])


def set_mode(ctx: TimeContext, mode: str, reason: str) -> list[BoundaryResult]:
    """Switch the time mode (00.7.3) and mark `mode_change`. No-op when the mode is unchanged."""  # rule: 00.7.3
    if mode not in clock.MODES:
        raise SchedulerError(f"unknown time mode {mode!r} (00.7.3: {', '.join(clock.MODES)})")
    old = ctx.tx.state.time.mode
    if old == mode:
        return []
    now = ctx.tx.state.time.now
    ctx.now = now
    _time_event(ctx, now, now, ["mode_change"], reason, mode=mode)
    return _run_instant(ctx, [("mode_change", {"from": clock.mode_of(old), "to": mode})])
