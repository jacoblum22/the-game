"""T1c scene state written by code (00.6.6a item 4, 12.11.9; T-12-18 = `pacing.yaml#details.scene_writes`).

    beat_writes(ctx, record, beats)                     # after resolution: each resolved beat's slot writes
    write(ctx, record, npc, response_values(rules, "table_row", practice="fight", row=2), because="tbl.npc_action:2")
    record.activities = lines(state, pc, present)       # every present person's scene slots, as citable record lines

Every write goes through `write_detail` with `because` = the beat's frame (or beat) id or the response's source, so a
changed slot cites its explaining record entry (00.6.6a item 2). All are `scene` slots, cleared at scene end with the
range bands (12.4.8 step 8). The narrator cites the lines; it never improvises a posture, a hold or a band.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from engine.dm.adjudication import ActivityEntry, AdjudicationRecord
from engine.dm.context import TurnContext
from engine.resolve.pipeline import _BAND_WORDS, _DOWN
from engine.resolve.types import REACH_VALUE
from engine.store.details import current, write_detail

SLOTS = ("activity", "posture", "held", "manner")  # the person's scene slots, in the order the lines show them
RESOLVED = ("resolved", "no_roll")


def _spec(rules: Any) -> dict[str, Any]:
    return rules.pacing["details"]["scene_writes"]


def _name(state: Any, eid: str, pc: str | None) -> str:
    from engine.store.views import display_name
    from engine.text.render import the_name

    return "you" if eid == pc else the_name(display_name(state, eid))


def write(ctx: TurnContext, record: AdjudicationRecord, eid: str, values: Mapping[str, str], *, because: str,
          fill: Mapping[str, str] | None = None) -> None:  # rule: 00.6.6a
    """Write each slot's value on `eid` (a scene slot, `because` the explaining record entry); `{actor}`/`{target}`
    in a value are filled from `fill`, and a value naming a party that is not there is skipped."""
    tx_ = ctx.need_tx()
    start = len(tx_.events)
    for slot, value in values.items():
        v = str(value)
        for k, name in (fill or {}).items():
            v = v.replace("{" + k + "}", name)
        if "{" in v:
            continue
        tx_.add_all(write_detail(tx_.state, tx_.mint, eid, slot, v, source="ruling", because=because,
                                 rules=ctx.rules, visibility="shown").events)
    record.add_writes(tx_.events[start:])


def _band(e: Any) -> str:
    if e.degree is None or e.degree in ("success", "critical_success"):
        return "no_roll" if e.degree is None else e.degree
    return "success" if e.success_at_cost else e.degree


def beat_writes(ctx: TurnContext, record: AdjudicationRecord, beats: Sequence[Any]) -> None:  # rule: T-12-18
    """Each resolved beat's row of T-12-18 by verb, degree and delivered reach: the slots it sets on its actor and its
    target (people only)."""
    spec = _spec(ctx.rules)
    st = ctx.need_tx().state
    people = set(spec["who"])
    for b in beats:
        if b.status not in RESOLVED:
            continue
        e = b.entry
        rows = (spec["beats"].get(e.verb or "") or {}).get(spec["degree"].get(_band(e), ""), [])
        if not rows:
            continue
        reach = REACH_VALUE.get(e.reach or "standard", 2) if e.degree is not None else 2
        down = bool(_DOWN.search(f"{e.restatement} {e.approach_words}"))
        parties = {"actor": e.actor or record.pc,
                   "target": next((t for t in e.targets if t in st.entities and st.entities[t].kind in people), None)}
        fill = {k: _name(st, v, record.pc) for k, v in parties.items() if v}
        merged: dict[str, dict[str, str]] = {}
        for row in rows:
            if not int(row.get("reach_min", 0)) <= reach <= int(row.get("reach_max", 9)) or (row.get("down") and not down):
                continue
            for side in ("actor", "target"):
                if row.get(side) and parties[side]:
                    merged.setdefault(side, {}).update(row[side])
        for side, values in merged.items():
            eid = parties[side]
            if eid and eid in st.entities and st.entities[eid].kind in people:
                write(ctx, record, eid, values, because=e.frame_id or e.beat_id or "T-12-18", fill=fill)


LETS_GO = ("cond.unconscious", "cond.stunned")  # 06.5.2: a holder in either condition lets go


def _holds(rules: Any, st: Any, pc: str | None) -> list[tuple[str, str]]:
    """(holder, held) for every hold the scene state shows: a holder's `held` slot and the person whose posture is
    one of T-12-18's hold postures by that holder (the rows are the only writer of both)."""
    rows = _spec(rules)["beats"].get("verb.grapple", {}).get("success", [])
    postures = [str((r.get("target") or {}).get("posture") or "") for r in rows]
    out = []
    for holder in st.details:
        h = current(st, holder, "held")
        if h is None or not h.value:
            continue
        name = _name(st, holder, pc)
        for eid in st.details:
            p = current(st, eid, "posture")
            if eid != holder and p is not None and p.value in [x.replace("{actor}", name) for x in postures if x]:
                out.append((holder, eid))
    return out


def release_holds(ctx: TurnContext, record: AdjudicationRecord) -> None:  # rule: 06.5.2
    """06.5.2: "the hold also ends if the holder lets go, is moved away, or is stunned, unconscious or defeated" (and
    a held one who is down or gone is held by no one). Clears the holder's `held` and the held one's posture, so no
    line keeps saying "held fast" after the grip is gone (playtest 20261008-135049)."""
    from engine.harm.state import DEAD, LADDER_KINDS, harm_state, is_down
    from engine.resolve.conflict import _band

    tx_ = ctx.need_tx()
    st = tx_.state
    start = len(tx_.events)

    def out(eid: str) -> bool:  # a PC's `defeated` outlives its waking (07.2.9): its own ladder says it
        e = st.entities.get(eid)
        return (e is None or e.exists != "exists" or is_down(st, eid) or harm_state(st, eid) == DEAD
                or (e.kind not in LADDER_KINDS and bool(st.fact_value(eid, "defeated")))
                or any(c.condition_id in LETS_GO for c in st.conditions_on(eid)))

    for holder, held in _holds(ctx.rules, st, record.pc):
        band = _band(st, holder, held) or _band(st, held, holder)
        if not (out(holder) or out(held) or (band is not None and band != "engaged")):
            continue
        for eid, slot in ((holder, "held"), (held, "posture")):
            tx_.add_all(write_detail(tx_.state, tx_.mint, eid, slot, None, source="ruling", because="06.5.2",
                                     rules=ctx.rules, visibility="shown").events)
    record.add_writes(tx_.events[start:])


def response_values(rules: Any, source: str, *, practice: str | None = None, row: int | None = None,
                    degree: str | None = None) -> dict[str, str]:  # rule: T-12-18
    """An NPC response's activity and manner (12.11.9 step 3): a resolved Talk by its degree, a refusal, a want, or a
    `tbl.npc_action` row (the practice's row replaces the generic one whole). Empty: the activity holds."""
    r = _spec(rules)["responses"]
    if source == "talk_outcome":
        return dict(r["talk"]["failure" if degree in ("failure", "critical_failure") else "success"])
    if source in ("refusal", "want"):
        return dict(r[source])
    if source == "table_row" and row is not None:
        own = r["by_practice"].get(practice or "", {})
        return dict(own[str(row)] if str(row) in own else r["rows"].get(str(row), {}))
    return {}


def lines(state: Any, pc: str | None, present: Sequence[str]) -> list[ActivityEntry]:  # rule: T-12-18
    """The scene state the narration may cite: each present person's (the PC's too) current scene slots, and each
    present NPC's range band to the PC when one is held (T-12-11's words)."""
    out: list[ActivityEntry] = []
    for eid in [*([pc] if pc else []), *present]:
        for slot in SLOTS:
            f = current(state, eid, slot)
            if f is not None and f.value:
                out.append(ActivityEntry(npc=eid, slot=slot, activity=str(f.value)))
    for npc in present:
        mine, theirs = state.positions.get(npc), state.positions.get(pc) if pc else None
        band = (mine.band_to.get(pc) if mine and pc else None) or (theirs.band_to.get(npc) if theirs else None)
        band = str(band or "").removeprefix("band.")
        if band in _BAND_WORDS:
            out.append(ActivityEntry(npc=npc, slot="position", activity=f"{_BAND_WORDS[band]} you"))
    return out


__all__ = ["SLOTS", "beat_writes", "lines", "release_holds", "response_values", "write"]
