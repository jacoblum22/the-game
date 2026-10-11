"""The typed intended change applied at RECORD (01.2.7; PR-01-3 step 5; `resolution.yaml#intended_change`).

    res = apply_change(tx, rules, beat, reach=2, pc="pc.wren")   # on a success (or a success at a cost) only
    tx.add_all(res.events); res.words      # "you hold the coin purse, taken from Murzak Red-Hand"
    res.refused                            # "the coin purse is not with Feney" (nothing written; the RESULT says it)
    plain(state, beat.change, actor=..., pc=...)   # "Taking: the coin purse, from Murzak Red-Hand" (01.2.6, OFFER)

Code writes what each kind's `applies` names: `take`/`give` the item's `holder` fact (reach 1: `contested_by`, a hand
on it); `open`/`close` the thing's `open` fact; `persuade_to` the person's `agreed` fact (reach 1: short of the cited factor; added to, never replacing, one on record);
`hide` `hidden_from`; `restrain` applies 06.5.2's ladder condition on the held one (`cond.grabbed` S1/S2,
`cond.restrained`, `cond.pinned`; its source the holder) and T-12-18's posture row is its face (engine/dm/scene_state.py);
`free` ends the hold (engine/resolve/conflict.py `end_hold`); `move_to`, `harm` and `learn` already have their writers
(PR-06-4 and 06.3.5, ch.06/07, 01.10): their words come from what those wrote. A failure applies nothing: the caller
never calls this then. `pay` is 01.11.2's price: a method consequence that hands coin over is a quantity write.

Before framing (DL-01-36): `already_true` (certain: no roll, no OFFER) and `needs_target` (ask "who?", never roll).
A slot may be an unnamed description ("the refugees", DL-12-97): the change is a scene fact on the scene's place.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any

from engine import ids
from engine.resolve.types import Beat, Change
from engine.store.events import EntityRecord, Event

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
    if not c.description or beat.stated is not None:  # [spec 033 R1] a stated beat names its person by id, never by words
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
    The actor already holds the item; the thing is already open/closed."""
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
    # persuade_to: whether an agreement on record covers the ask is judged on the typed goal by the Framer
    # (`already_agreed`, DL-01-45; pipeline `_agreed`), never by word overlap (retired: H2, Morga's narrower ask)
    return ""  # move_to: an approach is already no-roll open ground (the Move rubric) and ends beside (DL-12-98)


def agreed_covers(state: Any, beat: Beat, fact_id: str | None) -> str:  # rule: 01.2.7
    # rule: 01.4.1
    """The Framer's judgment that an agreement on record already covers this whole ask (DL-01-45: the same act, or a
    larger one containing it), checked by code: a current `agreed` fact of the person (never the actor) a
    `persuade_to` asks. Its words for the record, or ""."""
    f = state.facts.get(fact_id or "")
    c = beat.change
    if f is None or f.predicate != "agreed" or c is None or c.kind != "persuade_to" or f.subject == beat.actor \
            or state.current_fact_id(f.subject, "agreed") != f.id or f.subject not in (c.what, c.whom, beat.target):
        return ""
    return f"Agreed already by {_name(state, f.subject, None)}: {f.value}"


# DL-01-42: a goal the Reader left `none`, from the beat's verb when it has one plain goal (a look is `learn` on its
# target or the place; a Help carries the helped goal, which only the Reader knows, so it is not guessed)
_VERB_GOAL = {"verb.observe": "learn", "verb.recall": "learn", "verb.move": "move_to", "verb.exert": "move_to",
              "verb.strike": "harm", "verb.force": "harm", "verb.grapple": "restrain", "verb.sneak": "hide"}


def typed_goal(state: Any, beat: Beat) -> None:  # rule: 01.2.7
    """Every rolled beat carries a typed goal (DL-01-42): a beat typed `none` gets its verb's plain goal in place
    (words that press: `learn` for a question, else `persuade_to`). One still `none` is never framed as such: the
    pipeline asks what the player wants (01.2.4)."""
    c = beat.change
    if c is not None and c.kind != NONE:
        return
    tgt = _id(beat.target)
    place = state.scene.place_id if state.scene is not None else None
    kind = _VERB_GOAL.get(beat.verb or "")
    if kind is None and (beat.verb == "verb.talk" or beat.speech):  # an act asked for (a request, an offer, a plea)
        person = tgt is not None and tgt in state.entities and state.entities[tgt].kind in PEOPLE
        kind = "persuade_to" if person and beat.pressure in ("request", "offer", "plea") else "learn"
    what, whom = tgt, None
    if kind in ("learn", "move_to"):  # a look about, a climb or a step with nothing named: here
        what = tgt or place
    elif kind == "hide":
        what, whom = beat.actor, tgt
    elif kind == "restrain" and tgt is None:  # a Grapple at no one: breaking free of a hold
        kind, what = "free", beat.actor
    if kind is None or (what is None and kind != "hide"):
        return
    beat.change = Change(kind=kind, what=what, whom=whom, description=c.description if c is not None else None)


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


def _made(tx: Any, words: str) -> str:  # rule: 00.6.6
    """[spec 033 P11] A thing the DM named only in words: the item is made from those words (as a walk-on is), never
    matched against existing names (an exact id or name is read upstream). Returns its id."""
    eid = ids.entity_id("item", words, tx.state.entities)
    tx.add(Event.of("entity_created", source="engine", rule_id="00.6.6",
                    entity=EntityRecord(id=eid, kind="item", name=words, visibility="shown")))
    return eid


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


def hold(tx: Any, rules: Any, held: str, holder: str, reach: int, beat_id: str | None = None) -> list[Event]:
    # rule: 06.5.2
    """The hold applied at RECORD (DL-06-31): the ladder condition for `reach` (or one rung up when tightening) on
    `held`, its source `holder`. Events are returned for the caller to stage (apply_change stages its own)."""
    from engine.store.conditions import apply_condition

    cid, sev = LADDER[hold_level(reach, current_hold(tx.state, held, holder))]
    return apply_condition(tx.state, tx.mint, rules, held, cid, severity=sev, rule_id="06.5.2",
                           source={"entity": holder, "beat_id": beat_id}).events


DEAL = "deal.price"  # the price record's predicate, on the payee (15.7.1 item 3)


def deal_price(rules: Any, size: str | None, stated: int | None) -> int:  # rule: 15.7.1
    """15.7.1 item 3 (DL-15-42; PR-12-12's price guard): what a deal costs: the player's stated amount kept inside the
    price band of what is asked (request R1..R5 -> `economy.yaml#price_bands` 0..4), else that band's floor. A
    spoken figure outside the band never reaches the purse."""
    rung = int(str(size or "R1").lstrip("R") or 1)
    bands = {int(b["band"]): b for b in rules.doc("economy")["price_bands"]}
    b = bands.get(max(0, min(4, rung - 1)), bands[0])
    lo, hi = int(b["min"]), int(b["max"] if b["max"] is not None else b["min"])
    return max(lo, min(hi, int(stated))) if stated else lo


def pay_deal(tx: Any, payer: str, payee: str, amount: int, *, kind: str = "coin", due: str = "now",
             rule_id: str = "15.7.1") -> list[Event]:  # rule: 15.7.1
    """An agreed deal's price record `{payer, payee, kind, amount, due, paid}` on the payee, and its payment as a typed
    quantity change (01.11.2): never below 0 (what is not in the purse is not paid, and the record says so)."""
    from engine.world.common import fact

    q = tx.state.quantities.get(payer, {}).get(kind)
    have = q.current if q is not None else 0
    paid = min(amount, have) if have > 0 and due == "now" else 0
    evs = [fact(tx, payee, DEAL, {"payer": payer, "payee": payee, "kind": kind, "amount": amount, "due": due,
                                  "paid": paid}, rule_id=rule_id, source="ruling", visibility="shown")]
    if paid:
        evs.append(Event.of("quantity_changed", source="engine", rule_id="01.11.2", entity=payer, quantity=kind,
                            delta=-paid, new_value=have - paid, reason="a deal's price paid (15.7.1)"))
    tx.add_all(evs)
    return evs


def apply_change(tx: Any, rules: Any, beat: Beat, reach: int, *, pc: str | None = None,
                 limit: str | None = None) -> ChangeResult:
    # rule: 01.2.7
    # rule: PR-01-3
    """Apply the beat's change at the delivered `reach` (1 partial, 2+ whole; 3-4 the kind's extra, which only
    `restrain` has). Events are added to `tx`. A change code cannot apply is refused with the reason. `limit`: the
    factor a Limited frame cited (what a partial `persuade_to` does not grant)."""
    c = beat.change
    if (c is None or c.kind == NONE) and beat.stated is None and beat.verb == "verb.grapple" \
            and beat.target in tx.state.entities \
            and tx.state.entities[beat.target].kind in PEOPLE:  # an untyped Grapple keeps hold (06.5.2's Decision;
        # a stated Grapple holds only when the DM states `change_kind=restrain`, spec 033 A12)
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
    k = c.kind
    if what is None and k in ("take", "give") and c.description:  # [spec 033 P11] named in words: make it
        what = _made(tx, c.description)
        st = tx.state
    w = _name(st, what, pc)
    res = ChangeResult()
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
        # reach 1: the act short of the factor the frame cited (01.6.10, DL-12-121; retires "a smaller part of it")
        part = act if reach >= 2 else f"{act}, but not {limit}" if limit else f"{act}, in part"
        if who is None and c.description:  # "the refugees" (DL-12-97)
            return _described(tx, beat, "agreed", f"{c.description}: {part}", f"Agreed by {c.description}: {part}")
        if who is None:
            return ChangeResult(refused="no one named to persuade")
        before = st.fact_value(who, "agreed")  # DL-01-45: a roll never replaces or shrinks an agreement on record
        keep = isinstance(before, str) and before and before != part and not (  # a partial of this act grows
            reach >= 2 and before.startswith(f"{act},"))
        value = f"{before}; and {part}" if keep else part
        res.events.append(_fact(tx, beat, who, "agreed", value))
        res.words = f"Agreed by {_name(st, who, pc)}: {part}"  # no verb to agree ("You agrees to ...", talker run)
    elif k == "hide":
        hidden = what or actor
        res.events.append(_fact(tx, beat, hidden, "hidden_from", whom or "everyone"))
        res.words = f"{_name(st, hidden, pc)} {'are' if hidden == pc else 'is'} hidden from " + (
            _name(st, whom, pc) if whom else "view")
    elif k == "restrain":  # the hold is a condition (06.5.2; DL-06-31); T-12-18's posture row is its face
        if what is None or st.entities[what].kind not in PEOPLE:
            return ChangeResult(refused="no one named to restrain")
        level = hold_level(reach, current_hold(st, what, actor))
        res.events += hold(tx, rules, what, actor, reach, beat.id)
        res.words = f"{w} {'held fast' if level <= 2 else 'restrained' if level == 3 else 'pinned'} by " \
                    f"{_name(st, actor, pc)}"
    elif k == "free":
        if beat.stated is not None:  # [spec 033 R1] the DM's `free`: the holds on the freed one end
            from engine.resolve.conflict import end_hold, holds

            for holder, held in holds(st):
                if held == (what or actor):
                    end_hold(tx, rules, holder, held, "breaks free (06.5.2)")
        res.words = f"the hold on {_name(st, what or actor, pc)} ends"
    elif k == "make":
        return ChangeResult(refused="making or mending things is not built yet (ch.08)")
    tx.add_all(res.events)
    return res


__all__ = ["HOLDS", "LADDER", "ChangeResult", "agreed_covers", "already_true", "apply_change", "current_hold", "hold", "hold_level",
           "holder_of", "kinds", "needs_target", "pay_deal", "deal_price", "DEAL", "plain", "things_held",
           "typed_goal"]
