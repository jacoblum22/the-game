"""The typed intended change applied at RECORD (01.2.7; PR-01-3 step 5; `resolution.yaml#intended_change`).

    res = apply_change(tx, rules, beat, reach=2, pc="pc.wren")   # on a success (or a success at a cost) only
    tx.add_all(res.events); res.words      # "you hold the coin purse, taken from Murzak Red-Hand"
    res.refused                            # "the coin purse is not with Feney" (nothing written; the RESULT says it)
    plain(state, beat.change, actor=..., pc=...)   # "Taking: the coin purse, from Murzak Red-Hand" (01.2.6, OFFER)

Code writes what each kind's `applies` names: `take`/`give` the item's `holder` fact (reach 1: `contested_by`, a hand
on it); `open`/`close` the thing's `open` fact; `persuade_to` the person's `agreed` fact (reach 1: a smaller part);
`hide` `hidden_from`. `restrain`/`free` are T-12-18's slots (engine/dm/scene_state.py, at the world step); `move_to`,
`harm` and `learn` already have their writers (PR-06-4 and 06.3.5, ch.06/07, 01.10): their words come from what those
wrote. A failure applies nothing: the caller never calls this then.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any

from engine import ids
from engine.resolve.types import Beat, Change
from engine.store.events import Event

NONE = "none"
HOLDER_FACTS = ("holder", "carried_on", "held_by", "carried_by")  # the change writes `holder`; narration wrote the rest
HOLDER_KEYS = ("holder", "owner", "carried_by", "held_by")  # entity data (a starting kit's `owner`)
THINGS = ("item", "object", "clue")
PEOPLE = ("pc", "npc", "companion", "adversary")
OWN_WRITERS = ("move_to", "harm", "learn")  # applied by their own rules; the change line cites what they wrote
LABELS = {"take": ("Taking", "from"), "give": ("Giving", "to"), "move_to": ("Moving to", "with"),
          "open": ("Opening", ""), "close": ("Closing", ""), "learn": ("Learning", ""),
          "persuade_to": ("Persuading", ""), "restrain": ("Restraining", ""), "free": ("Freeing", ""),
          "harm": ("Harming", ""), "hide": ("Hiding", "from"), "make": ("Making", "from")}


@dataclass
class ChangeResult:
    words: str = ""  # what was applied, in words ("" for none, or for a kind whose own writer's line says it)
    refused: str = ""  # why it was not applied (01.2.7 item 2)
    events: list[Event] = field(default_factory=list)


def kinds(rules: Any) -> list[str]:  # rule: 01.2.7
    return list(rules.resolution["intended_change"]["kinds"])


def holder_of(state: Any, item: str) -> str | None:  # rule: 01.2.7
    """Who holds `item`: its current `holder` fact (what a change wrote) before a narrated `carried_on` / `held_by`,
    then its data keys (a kit item's `owner`)."""
    for p in HOLDER_FACTS:
        v = state.fact_value(item, p)
        if isinstance(v, str) and v in state.entities:
            return v
    e = state.entities.get(item)
    for k in HOLDER_KEYS if e is not None else ():
        v = e.data.get(k)  # type: ignore[union-attr]
        if isinstance(v, str):
            return v
    return None


def things_held(state: Any, people: Iterable[str]) -> list[str]:  # rule: 01.2.7
    """The things the given people hold (slot ids for a `take` or `give`: the PC's kit, Murzak's purse)."""
    who = set(people)
    return [eid for eid, e in state.entities.items()
            if e.kind in THINGS and e.exists == "exists" and holder_of(state, eid) in who]


def _id(x: str | None) -> str | None:
    return x if x not in (None, "", NONE) else None


def _name(state: Any, eid: str | None, pc: str | None) -> str:
    from engine.store.views import display_name
    from engine.text.render import the_name

    if eid is None:
        return "someone"
    if eid == pc:
        return "you"
    return the_name(display_name(state, eid)) if eid in state.entities else eid.split(".", 1)[-1].replace("_", " ")


def plain(state: Any, change: Change | None, *, actor: str | None = None, pc: str | None = None) -> str:
    # rule: 01.2.6
    """The typed change in plain words for the OFFER and the record ("Taking: the coin purse, from Murzak
    Red-Hand"); "" for none."""
    if change is None or change.kind == NONE or change.kind not in LABELS:
        return ""
    label, prep = LABELS[change.kind]
    what, whom = _id(change.what), _id(change.whom)
    head = _name(state, what, pc) if what else "as described"
    tail = f", {prep} {_name(state, whom, pc)}" if whom and prep and whom != actor else ""
    return f"{label}: {head}{tail}"


def _fact(tx: Any, beat: Beat, subject: str, predicate: str, value: Any) -> Event:
    return Event.of("fact_set", {"source": "ruling"}, source=beat.id, rule_id="01.2.7", fact_id=tx.mint(ids.FACT),
                    subject=subject, predicate=predicate, value=value, visibility="shown",
                    supersedes=tx.state.current_fact_id(subject, predicate))


def apply_change(tx: Any, rules: Any, beat: Beat, reach: int, *, pc: str | None = None) -> ChangeResult:
    # rule: 01.2.7
    # rule: PR-01-3
    """Apply the beat's change at the delivered `reach` (1 partial, 2+ whole; 3-4 the kind's extra, which only
    `restrain` has). Events are added to `tx`. A change code cannot apply is refused with the reason."""
    c = beat.change
    if c is None or c.kind == NONE or reach < 1:
        return ChangeResult()
    st = tx.state
    actor = beat.actor
    what, whom = _id(c.what), _id(c.whom)
    for slot in (what, whom):
        if slot is not None and slot not in st.entities:
            return ChangeResult(refused=f"{_name(st, slot, pc)} is not in the record")
    w = _name(st, what, pc)
    res = ChangeResult()
    k = c.kind
    if k == "take":
        if what is None or st.entities[what].kind not in THINGS:
            return ChangeResult(refused="nothing on record by that name to take")
        held = holder_of(st, what)
        if held == actor:
            return ChangeResult(refused=f"{_name(st, actor, pc)} already {'have' if actor == pc else 'has'} {w}")
        if whom is not None and held is not None and held != whom:
            return ChangeResult(refused=f"{w} is not with {_name(st, whom, pc)}")
        src = held or whom
        if reach == 1:
            res.events.append(_fact(tx, beat, what, "contested_by", actor))
            res.words = f"{_name(st, actor, pc)} {'have' if actor == pc else 'has'} a hand on {w}, still contested" + (
                f" by {_name(st, src, pc)}" if src else "")
        else:
            res.events.append(_fact(tx, beat, what, "holder", actor))
            if st.current_fact_id(what, "contested_by") is not None:
                res.events.append(_fact(tx, beat, what, "contested_by", None))
            res.words = f"{_name(st, actor, pc)} {'hold' if actor == pc else 'holds'} {w}" + (
                f", taken from {_name(st, src, pc)}" if src else "")
    elif k == "give":
        if what is None or st.entities[what].kind not in THINGS:
            return ChangeResult(refused="nothing on record by that name to give")
        held = holder_of(st, what)
        if held not in (None, actor):
            return ChangeResult(refused=f"{w} is not {'yours' if actor == pc else 'theirs'} to give")
        if whom is None or st.entities[whom].kind not in PEOPLE:
            return ChangeResult(refused="no one named to give it to")
        res.events.append(_fact(tx, beat, what, "holder", whom))
        res.words = f"{_name(st, whom, pc)} {'hold' if whom == pc else 'holds'} {w} now"
    elif k in ("open", "close"):
        if what is None:
            return ChangeResult(refused=f"nothing on record by that name to {k}")
        res.events.append(_fact(tx, beat, what, "open", k == "open"))
        res.words = f"{w} is {'open' if k == 'open' else 'closed'} now"
    elif k == "persuade_to":
        what = next((x for x in (what, whom, beat.target) if x and x in st.entities and st.entities[x].kind in PEOPLE),
                    None)  # the person may come in either slot (live run 015), else the beat's target
        if what is None:
            return ChangeResult(refused="no one named to persuade")
        w = _name(st, what, pc)
        act = (beat.intent or beat.method).strip().rstrip(".")
        part = act if reach >= 2 else f"a smaller part of it ({act})"
        res.events.append(_fact(tx, beat, what, "agreed", part))
        res.words = f"{w} agrees to {part}"
    elif k == "hide":
        hidden = what or actor
        res.events.append(_fact(tx, beat, hidden, "hidden_from", whom or "everyone"))
        res.words = f"{_name(st, hidden, pc)} {'are' if hidden == pc else 'is'} hidden from " + (
            _name(st, whom, pc) if whom else "view")
    elif k == "restrain":  # the slots are T-12-18's (scene_state.beat_writes); here only their words
        if what is None or st.entities[what].kind not in PEOPLE:
            return ChangeResult(refused="no one named to restrain")
        res.words = f"{w} {'held fast' if reach <= 2 else 'restrained' if reach == 3 else 'pinned'} by " \
                    f"{_name(st, actor, pc)}"
    elif k == "free":
        res.words = f"the hold on {_name(st, what or actor, pc)} ends"
    elif k == "make":
        return ChangeResult(refused="making or mending things is not built yet (ch.08)")
    tx.add_all(res.events)
    return res


__all__ = ["ChangeResult", "apply_change", "holder_of", "kinds", "plain", "things_held"]
