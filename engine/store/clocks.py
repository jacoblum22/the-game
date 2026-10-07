"""Clocks (00.8; T017): create and tick, as functions that return events. They never write; the caller stages
the events (`tx.add_all(result.events)`).

    ev = create_clock(tx.state, template, name="Word reaches the Salt Guild", owner="12", rule_id="PR-12-7")
    res = tick_clock(tx.state, "clk.word_reaches_the_salt_guild", "cost.exposure", severity="S2",
                     units=rules.severity_units())
    tx.add_all(res.events); res.omen  # the narrator must render it this turn (00.8.4)
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Literal

from engine import ids
from engine.store.events import ClockRecord, Event
from engine.store.projection import WorldState

Stage = Literal["stirring", "building", "imminent"]
_TEMPLATE_DROP = {"id", "lifecycle", "basis", "notes", "tags", "filled", "status", "history", "name"}


class ClockError(ValueError):
    """A tick the clock does not allow (PR-00-3 step 1), or a bad clock definition."""


@dataclass
class TickResult:
    events: list[Event]
    clock_id: str
    amount: int
    filled: int
    stage: Stage | None = None
    omen: str | None = None  # text of the omen the narration must render (sensed/hidden clocks)
    completed: bool = False
    lethal_warning: bool = False  # raise ch.07's lethal-warning trigger (PR-00-3 step 3)
    interrupt: bool = False  # halt advance_time (00.7.8)
    completion_effects: list[Mapping[str, Any]] = field(default_factory=list)  # run as a depth-0 process
    pending_links: list[str] = field(default_factory=list)  # create:/unlock: link actions for the caller
    linked: list[TickResult] = field(default_factory=list)  # ticks fired by links (their events are in `events`)


def stage(filled: int, segments: int) -> Stage:
    """00.8.1 omen stages (scales.yaml clock_omen_stages)."""  # rule: 00.8.4
    if segments - filled <= max(1, segments // 4):
        return "imminent"
    if filled * 2 >= segments:
        return "building"
    return "stirring"


def create_clock(state: WorldState, template: Mapping[str, Any], *, name: str | None = None, owner: str = "",
                 rule_id: str = "00.8.1", races_with: str | None = None, source: str = "engine",
                 **overrides: Any) -> Event:  # rule: 00.8.1
    """`clock_created` for a new instance of `template` (a clock_template from data, or plain fields)."""
    fields = {k: v for k, v in template.items() if k not in _TEMPLATE_DROP}
    fields = _thaw(fields)
    fields.update(overrides)
    nm = name or str(template.get("name") or "")
    if not nm:
        raise ClockError("a clock needs a name (SG-24: the obstacle, never the method)")
    if fields.get("segments") not in (4, 6, 8, 12):
        raise ClockError(f"clock segments {fields.get('segments')!r} not in 4|6|8|12 (00.8.3)")
    if fields.get("visibility", "public") != "public":
        for st in ("stirring", "building", "imminent"):
            if len((fields.get("omens") or {}).get(st) or []) < 2:
                raise ClockError(f"a {fields.get('visibility')} clock needs >= 2 omens per stage (00.8.1)")
    on_complete = fields.get("on_complete") or {}
    lethal = bool(fields.pop("lethal", False)) or any(
        bool((e.get("params") or {}).get("lethal")) for e in on_complete.get("effects") or [])
    fields["races_with"] = races_with if races_with in state.clocks else None
    clock = ClockRecord(id=ids.clock_id(nm, state.clocks), name=nm, owner=owner, lethal=lethal,
                        created={"by": rule_id, "template": template.get("id")}, **fields)
    return Event.of("clock_created", source=source, rule_id=rule_id, clock=clock)


def tick_clock(state: WorldState, clock_id: str, on: str, *, reach: int | None = None,
               severity: str | None = None, units: Mapping[str, int] | None = None,
               row: Literal["source", "auto", "decay"] = "source", source_ref: str | None = None,
               rule_id: str = "PR-00-3") -> TickResult:  # rule: PR-00-3
    """Tick `clock_id` from the source `on` (a tick_sources `on`, or for row='auto'/'decay' a boundary id).
    `reach` (0..4) feeds 'delivered_reach'; `severity` + `units` (Rules.severity_units()) feed 'U(severity)'.
    The DM decided the source fired; this checks the clock lists it and computes the amount (00.8.2)."""
    return _tick(state, clock_id, on, reach, severity, units, row, source_ref or on, rule_id, set())


def _tick(state: WorldState, clock_id: str, on: str, reach: int | None, severity: str | None,
          units: Mapping[str, int] | None, row: str, source_ref: str, rule_id: str, seen: set[str],
          link_ticks: int | None = None) -> TickResult:
    c = state.clocks.get(clock_id)
    if c is None:
        raise ClockError(f"unknown clock {clock_id}")
    if c.status != "active":
        raise ClockError(f"clock {clock_id} is {c.status}")
    seen.add(clock_id)
    # 1. validate the source and compute the amount
    if link_ticks is not None:
        amount = link_ticks
    else:
        amount = _amount(c, on, row, reach, severity, units)
    # 2. apply, clamped; fill clocks never go down
    new = max(0, min(c.segments, c.filled + amount))
    if c.direction == "fill" and new < c.filled:
        new = c.filled
    delta = new - c.filled
    res = TickResult(events=[], clock_id=clock_id, amount=delta, filled=new)
    completed = new == c.segments and c.filled < c.segments
    # 3. omen for sensed and hidden clocks
    omen_key = None
    if c.visibility != "public" and delta != 0:
        res.stage = stage(new, c.segments)
        omen_key, res.omen = _omen(c, res.stage)
        res.lethal_warning = res.stage == "imminent" and c.lethal and not completed
    # 4. completion
    status = c.status
    voids: list[str] = []
    after = new
    if completed:
        res.completed = True
        on_complete = c.on_complete or {}
        res.completion_effects = list(on_complete.get("effects") or [])
        res.interrupt = bool(on_complete.get("interrupting"))
        then = on_complete.get("then", "close")
        status = {"close": "completed", "reset": "active", "void": "voided"}.get(then, "completed")
        after = 0 if then == "reset" else new
        if c.races_with and c.races_with in state.clocks and state.clocks[c.races_with].status == "active":
            voids.append(c.races_with)  # rule: 00.8.5
    res.filled = after
    if delta == 0 and not completed:
        return res  # nothing changed: no event
    res.events.append(Event.of("clock_ticked", source=source_ref, rule_id=rule_id, clock_id=clock_id,
                               source_ref=source_ref, amount=delta, filled=after, stage=res.stage,
                               omen_key=omen_key, completed=completed, status=status, voids=voids))
    # links fire in list order (00.8.6)
    for link in c.links:
        when = str(link.get("when", ""))
        hit = (when == "complete" and completed) or (
            when.startswith("reaches:") and int(when.split(":")[1]) == new and c.filled != new)
        if not hit:
            continue
        action = str(link.get("action", ""))
        kind, _, rest = action.partition(":")
        if kind == "tick":
            target, _, n = rest.rpartition(":")
            if target in seen or target not in state.clocks or state.clocks[target].status != "active":
                continue
            sub = _tick(state, target, f"link:{clock_id}", None, None, None, "link", f"link:{clock_id}", rule_id,
                        seen, link_ticks=int(n))
            res.linked.append(sub)
            res.events += sub.events
        elif kind == "void":
            if rest in state.clocks and rest not in voids and state.clocks[rest].status == "active":
                res.events.append(Event.of("clock_ticked", source=f"link:{clock_id}", rule_id="00.8.6",
                                           clock_id=rest, source_ref=f"link:{clock_id}", amount=0,
                                           filled=state.clocks[rest].filled, status="voided"))
        else:
            res.pending_links.append(action)
    return res


def _amount(c: ClockRecord, on: str, row: str, reach: int | None, severity: str | None,
            units: Mapping[str, int] | None) -> int:  # rule: 00.8.2
    if row == "source":
        rows = [r for r in c.tick_sources if str(r.get("on")) == on]
    else:
        listed = c.auto_ticks if row == "auto" else c.decay
        b = on.removeprefix("boundary:")
        rows = [r for r in listed if str(r.get("boundary")) == b]
    if not rows:
        raise ClockError(f"clock {c.id} does not list {row} {on!r} (PR-00-3 step 1)")
    ticks = rows[0].get("ticks")
    if isinstance(ticks, int):
        return ticks
    if ticks == "delivered_reach":
        if reach is None or not 0 <= reach <= 4:
            raise ClockError("delivered_reach ticks need reach 0..4 (00.3.15)")
        return reach
    if ticks == "U(severity)":
        if severity is None or units is None or severity not in units:
            raise ClockError("U(severity) ticks need a severity and the units table (00.3.11)")
        return int(units[severity])
    raise ClockError(f"clock {c.id}: unknown ticks {ticks!r}")


def _omen(c: ClockRecord, st: Stage) -> tuple[str | None, str | None]:
    entries = c.omens.get(st) or []
    if not entries:
        return None, None
    used = c.omens_used.get(st, [])
    if len(used) >= len(entries):
        used = []  # list exhausted: start again (the reducer clears it the same way)
    idx = next(i for i in range(len(entries)) if i not in used)
    return f"{st}:{idx}", entries[idx]


def _thaw(x: Any) -> Any:
    if isinstance(x, Mapping):
        return {k: _thaw(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_thaw(v) for v in x]
    return x
