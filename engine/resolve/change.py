"""The typed intended change applied at RECORD (01.2.7; PR-01-3 step 5; `resolution.yaml#intended_change`).

    res = apply_change(tx, rules, beat, reach=2, pc="pc.wren")   # on a success (or a success at a cost) only
    tx.add_all(res.events); res.words      # "you hold the coin purse, taken from Murzak Red-Hand"
    res.refused                            # "the coin purse is not with Feney" (nothing written; the RESULT says it)
    plain(state, beat.change, actor=..., pc=...)   # "Taking: the coin purse, from Murzak Red-Hand" (01.2.6, OFFER)

Code writes what each kind's `applies` names: `take`/`give` the item's `holder` fact (reach 1: `contested_by`, a hand
on it); `open`/`close` the thing's `open` fact; `persuade_to` the person's `agreed` fact (reach 1: a smaller part);
`hide` `hidden_from`; `restrain` applies 06.5.2's ladder condition on the held one (`cond.grabbed` S1/S2,
`cond.restrained`, `cond.pinned`; its source the holder) and T-12-18's posture row is its face (engine/dm/scene_state.py);
`free` ends the hold (engine/resolve/conflict.py `end_hold`); `move_to`, `harm` and `learn` already have their writers
(PR-06-4 and 06.3.5, ch.06/07, 01.10): their words come from what those wrote. A failure applies nothing: the caller
never calls this then. `pay` is 01.11.2's price: a method consequence that hands coin over is a quantity write.

Before framing (DL-01-36): `already_true` (certain: no roll, no OFFER) and `needs_target` (ask "who?", never roll).
A slot may be an unnamed description ("the refugees", DL-12-97): the change is a scene fact on the scene's place.
"""

from __future__ import annotations

import re
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
    if change.kind == "persuade_to" and what in (None, actor):  # never "Persuading: you" (talker run, input 20)
        what, whom = whom, None
    head = _name(state, what, pc) if what else (change.description or "as described")
    tail = f", {prep} {_name(state, whom, pc)}" if whom and prep and whom != actor else ""
    return f"{label}: {head}{tail}"


def _fact(tx: Any, beat: Beat, subject: str, predicate: str, value: Any, persistence: str | None = None) -> Event:
    return Event.of("fact_set", {"source": "ruling"}, source=beat.id, rule_id="01.2.7", fact_id=tx.mint(ids.FACT),
                    subject=subject, predicate=predicate, value=value, visibility="shown", persistence=persistence,
                    supersedes=tx.state.current_fact_id(subject, predicate))


def _person(state: Any, beat: Beat) -> str | None:  # rule: 01.2.7
    """The one a `persuade_to` asks: a person in either slot or the beat's target, never the actor (the talker run's
    "You agrees to ..."), else the one person in scope the description names (DL-12-97)."""
    c = beat.change or Change()
    for x in (c.what, c.whom, beat.target):
        if x and x != beat.actor and x in state.entities and state.entities[x].kind in PEOPLE:
            return x
    if not c.description:
        return None
    from engine.retrieve.scene import resolve_names, scene_scope

    here = set(scene_scope(state))
    named = [i for i in resolve_names(state, c.description)
             if i in here and i != beat.actor and state.entities[i].kind in PEOPLE]
    return named[0] if len(named) == 1 else None


def _thing(state: Any, beat: Beat) -> str | None:
    c = beat.change or Change()
    return next((x for x in (_id(c.what), beat.target) if x and x != beat.actor and x in state.entities), None)


def _act(beat: Beat) -> str:
    return (beat.intent or beat.method).strip().rstrip(".")


def already_true(state: Any, beat: Beat, *, pc: str | None = None) -> str:  # rule: 01.2.7
    # rule: 01.4.1
    """DL-01-36: the change already holds in the store, so it is certain (no roll, no OFFER); its words, or "".
    The actor already holds the item; the person already agreed to this act; the thing is already open/closed."""
    c = beat.change
    if c is None or c.kind == NONE:
        return ""
    actor = beat.actor
    what = _id(c.what)
    you = actor == pc
    if c.kind == "take" and what is not None and what in state.entities and holder_of(state, what) == actor:
        return f"{_name(state, actor, pc)} already {'have' if you else 'has'} {_name(state, what, pc)}"
    if c.kind in ("open", "close") and (t := _thing(state, beat)) is not None \
            and state.fact_value(t, "open") is (c.kind == "open"):
        return f"{_name(state, t, pc)} is already {'open' if c.kind == 'open' else 'closed'}"
    if c.kind == "persuade_to" and (p := _person(state, beat)) is not None:
        from engine.audit.text import covers

        done = state.fact_value(p, "agreed")
        act = _act(beat)  # the same act: each covers most of the other (a bigger ask is a new one)
        if isinstance(done, str) and not done.startswith("a smaller part") and covers(done, act, ratio=0.6) \
                and covers(act, done, ratio=0.6):
            return f"Agreed already by {_name(state, p, pc)}: {done}"
    return ""  # move_to: an approach is already no-roll open ground (the Move rubric) and ends beside (DL-12-98)


_ASK = {"persuade_to": ("who", "persuade"), "restrain": ("who", "hold"), "take": ("what", "take"),
        "give": ("what", "give"), "open": ("what", "open"), "close": ("what", "close")}


def needs_target(state: Any, beat: Beat) -> str:  # rule: 01.2.5
    # rule: 01.2.7
    """DL-01-36: a change that needs a person or thing and names none (no id, no target, no description) is asked
    about before framing, never rolled: the question's words, or ""."""
    c = beat.change
    if c is None or c.kind not in _ASK or c.description:
        return ""
    ok = _person(state, beat) if c.kind == "persuade_to" else _thing(state, beat) or _id(c.whom)
    if ok:
        return ""
    q, verb = _ASK[c.kind]
    return f"ask the player {q} they mean: nothing here was named to {verb}"


def _described(tx: Any, beat: Beat, kind: str, value: Any, words: str) -> ChangeResult:  # rule: 01.2.7
    """DL-12-97: a change on an unnamed description is a scene fact on the scene's place (cleared at scene end)."""
    st = tx.state
    place = st.scene.place_id if st.scene is not None else None
    if not place:
        return ChangeResult(refused=f"{(beat.change or Change()).description} is not here")
    desc = str((beat.change or Change()).description)
    ev = _fact(tx, beat, place, f"{kind}.{ids.slug(desc)[:40]}", value, persistence="scene")
    tx.add(ev)
    return ChangeResult(words=words, events=[ev])


# 06.5.2's ladder by the delivered reach: rung -> (condition, severity); the rungs share `exclusion_group: hold`
LADDER: dict[int, tuple[str, str | None]] = {1: ("cond.grabbed", "S1"), 2: ("cond.grabbed", "S2"),
                                             3: ("cond.restrained", None), 4: ("cond.pinned", None)}
HOLDS = ("cond.grabbed", "cond.restrained", "cond.pinned")


def current_hold(state: Any, held: str, holder: str | None = None) -> int:  # rule: 06.5.2
    """The rung of the hold on `held` (by `holder`, else by anyone); 0 when not held."""
    def rung(i: Any) -> int:
        return next((k for k, (c, s) in LADDER.items() if c == i.condition_id and s in (None, i.severity)), 0)

    return max((rung(i) for i in state.conditions_on(held) if i.condition_id in HOLDS
                and (holder is None or (i.source or {}).get("entity") == holder)), default=0)


def hold_level(reach: int, held: int) -> int:  # rule: 06.5.2
    """The rung a hold lands on: the delivered reach's, or one step above the holder's existing hold (tightening)."""
    return min(4, max(1, reach, held + 1 if held else 0))


_PAID = re.compile(r"\b(?:spent|paid|pays|handed over|hands over|changes hands|set (?:down )?on|laid (?:down )?on|"
                   r"left (?:on|with)|on the (?:table|counter|bar|trestle))\b", re.IGNORECASE)
_COIN = re.compile(r"\b(?:(\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s+)?(?:[a-z]+\s+)?"
                   r"(?:coins?|silver|copper|gold pieces?)\b", re.IGNORECASE)
_NUM = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}


def price(consequence: str) -> int:  # rule: 01.11.2
    """The coin a method consequence hands over (01.11.2's price: a round, a bribe, a fee), else 0. An offer of coin is
    no payment: the words must say the coin changed hands (spent, paid, set on the table)."""
    # ponytail: read from the Framer's declared consequence (3 of 3 payments, 0 of 4 offers in the round-5/6 saves);
    # a typed `price` field on the Framer's schema when it is next opened
    m = _COIN.search(consequence)
    if m is None or not _PAID.search(consequence):
        return 0
    n = (m.group(1) or "").lower()
    return int(n) if n.isdigit() else _NUM.get(n, 1)


def pay(tx: Any, consequences: Iterable[str], payer: str | None) -> list[Event]:  # rule: 01.11.2
    """01.11.2 (DL-01-40): the coin the method hands over leaves the payer's `coin` at RECORD, whatever the degree;
    never below 0 (what is not in the purse is not paid)."""
    q = tx.state.quantities.get(payer or "", {}).get("coin")
    amount = sum(price(c) for c in consequences)
    if q is None or amount <= 0 or q.current <= 0:
        return []
    paid = min(amount, q.current)
    ev = Event.of("quantity_changed", source="engine", rule_id="01.11.2", entity=payer, quantity="coin", delta=-paid,
                  new_value=q.current - paid, reason="a price the method pays (01.11.2)")
    tx.add(ev)
    return [ev]


def apply_change(tx: Any, rules: Any, beat: Beat, reach: int, *, pc: str | None = None) -> ChangeResult:
    # rule: 01.2.7
    # rule: PR-01-3
    """Apply the beat's change at the delivered `reach` (1 partial, 2+ whole; 3-4 the kind's extra, which only
    `restrain` has). Events are added to `tx`. A change code cannot apply is refused with the reason."""
    c = beat.change
    if (c is None or c.kind == NONE) and beat.verb == "verb.grapple" and beat.target in tx.state.entities \
            and tx.state.entities[beat.target].kind in PEOPLE:  # an untyped Grapple keeps hold (06.5.2's Decision)
        c = beat.change = Change(kind="restrain", what=beat.target)
    if c is None or c.kind == NONE or reach < 1:
        return ChangeResult()
    st = tx.state
    actor = beat.actor
    what, whom = _id(c.what), _id(c.whom)
    for slot in (what, whom):
        if slot is not None and slot not in st.entities:
            return ChangeResult(refused=f"{_name(st, slot, pc)} is not in the record")
    already = already_true(st, beat, pc=pc)
    if already:  # certain, nothing to write (DL-01-36)
        return ChangeResult(words=already)
    w = _name(st, what, pc)
    res = ChangeResult()
    k = c.kind
    if k == "take":
        if what is None or st.entities[what].kind not in THINGS:
            return ChangeResult(refused="nothing on record by that name to take")
        held = holder_of(st, what)
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
        thing = _thing(st, beat)
        state_word = "open" if k == "open" else "closed"
        if thing is None and c.description:
            return _described(tx, beat, "open", k == "open", f"{c.description}: {state_word} now")
        if thing is None:
            return ChangeResult(refused=f"nothing on record by that name to {k}")
        res.events.append(_fact(tx, beat, thing, "open", k == "open"))
        res.words = f"{_name(st, thing, pc)} is {state_word} now"
    elif k == "persuade_to":
        who = _person(st, beat)  # either slot or the beat's target (live run 015), never the actor
        act = _act(beat)
        part = act if reach >= 2 else f"a smaller part of it ({act})"
        if who is None and c.description:  # "the refugees" (DL-12-97)
            return _described(tx, beat, "agreed", f"{c.description}: {part}", f"Agreed by {c.description}: {part}")
        if who is None:
            return ChangeResult(refused="no one named to persuade")
        res.events.append(_fact(tx, beat, who, "agreed", part))
        res.words = f"Agreed by {_name(st, who, pc)}: {part}"  # no verb to agree ("You agrees to ...", talker run)
    elif k == "hide":
        hidden = what or actor
        res.events.append(_fact(tx, beat, hidden, "hidden_from", whom or "everyone"))
        res.words = f"{_name(st, hidden, pc)} {'are' if hidden == pc else 'is'} hidden from " + (
            _name(st, whom, pc) if whom else "view")
    elif k == "restrain":  # the hold is a condition (06.5.2; DL-06-31); T-12-18's posture row is its face
        if what is None or st.entities[what].kind not in PEOPLE:
            return ChangeResult(refused="no one named to restrain")
        from engine.store.conditions import apply_condition

        level = hold_level(reach, current_hold(st, what, actor))
        cid, sev = LADDER[level]
        res.events += apply_condition(st, tx.mint, rules, what, cid, severity=sev, rule_id="06.5.2",
                                      source={"entity": actor, "beat_id": beat.id}).events
        res.words = f"{w} {'held fast' if level <= 2 else 'restrained' if level == 3 else 'pinned'} by " \
                    f"{_name(st, actor, pc)}"
    elif k == "free":
        res.words = f"the hold on {_name(st, what or actor, pc)} ends"
    elif k == "make":
        return ChangeResult(refused="making or mending things is not built yet (ch.08)")
    tx.add_all(res.events)
    return res


__all__ = ["HOLDS", "LADDER", "ChangeResult", "already_true", "apply_change", "current_hold", "hold_level",
           "holder_of", "kinds", "needs_target", "pay", "plain", "price", "things_held"]
