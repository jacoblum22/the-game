"""Conflict mode, the subset the engine runs (06.2.1, PR-06-1 steps 1-2, 06.4.3-06.4.4 harm, 06.9.2, 06.13.1).

    start(tctx, pc, ["npc.taman"], "a Strike (06.2.1)")   # conflict_start: foes listed, bands seeded, mode conflict
    res, words = strike_harm(tx, rules, rng, frame, delivered)   # a landed Strike's harm on its target
    words, res = foe_beat(tctx, rng, "npc.taman", pc)     # the foe's answer: stand, close, or strike (06.9.4)
    check_end(tctx, pc)                                   # 06.13.1 (a)/(d): conflict_end, the previous mode back

The record is `meta.conflict` {pc, foes, previous}. Not run here (follow-ups): sides' objectives and morale clocks
(06.11), surprise and the tempo order (06.2.2-06.2.4), reactions (06.6), a named NPC's PR-09-1 stat block (its
Vitality and line come from T-09-3's standard line for its band, its Guard is still computed by 06.4.1).
"""

from __future__ import annotations

import re
from typing import Any

from engine.store.events import Event, Quantity
from engine.time import clock
from engine.time.scheduler import TimeContext, mark_boundary, set_mode

KEY = "conflict"
FOES = ("npc", "adversary")
BANDS = ("engaged", "close", "near", "far", "distant")  # 06.3.2
NONLETHAL = re.compile(r"\b(?:non-?lethal|alive|knock\w* (?:\w+ )?out|subdue\w*|flat of|pommel|pull\w* (?:the|my|a|his|"
                       r"her) (?:blow|punch))\b", re.IGNORECASE)
UNARMED = re.compile(r"\b(?:punch\w*|kick\w*|fists?|elbow\w*|headbutt\w*|unarmed|bare hands?)\b", re.IGNORECASE)


def active(state: Any) -> bool:
    return clock.mode_of(state.time.mode) == "conflict"


def record(state: Any) -> dict[str, Any]:
    v = state.meta.get(KEY)
    return dict(v) if active(state) and isinstance(v, dict) else {}


def _line(rules: Any, ent: Any) -> dict[str, Any]:  # rule: T-09-3
    """The foe's line: a built adversary's calibrated line, else T-09-3's standard line for its band."""
    band = min(5, max(1, int(ent.data.get("threat_band") or ent.data.get("band") or 1)))
    std = dict(rules.doc("archetypes")["band_tables"]["standard"][band])
    return {**std, **((ent.data.get("calibration") or {}).get("line") or {})}


def ensure_vitality(tx: Any, rules: Any, eid: str) -> list[Event]:  # rule: 09.3.3
    # ponytail: a named NPC who fights gets T-09-3's standard Vitality for its band, not a PR-09-1 build (09 edge case)
    st = tx.state
    if st.quantities.get(eid, {}).get("vitality") is not None:
        return []
    vit = int(_line(rules, st.entities[eid])["vit"])
    evs = [Event.of("quantity_defined", source="06.2.1", rule_id="09.3.3", entity=eid, quantity="vitality",
                    value=Quantity(current=vit, min=0, max=vit, visibility="sealed"),
                    reason="the standard line for its band (T-09-3)")]
    tx.add_all(evs)
    return evs


def _here(st: Any, pc: str) -> str | None:
    pos = st.positions.get(pc)
    return (pos.location if pos else None) or (st.scene.place_id if st.scene else None)


def _band(st: Any, a: str, b: str) -> str | None:
    pos = st.positions.get(a)
    v = pos.band_to.get(b) if pos else None
    return str(v).removeprefix("band.") if v else None


def _set_band(tx: Any, a: str, b: str, band: str, rule_id: str) -> None:
    tx.add_all([Event.of("position_set", source="engine", rule_id=rule_id, entity=a, location=_here(tx.state, a),
                         band_to={b: band}),
                Event.of("position_set", source="engine", rule_id=rule_id, entity=b, band_to={a: band})])


def start(tctx: TimeContext, pc: str, foes: list[str], reason: str) -> bool:  # rule: 06.2.1
    # rule: PR-06-1
    """Mark `conflict_start` (or add joiners to a running one, 06.2.5): list the foes, give each Vitality, seed each
    band to the PC from the scene's positions, default `near` (06.3.9), and switch the time mode to conflict."""
    tx = tctx.tx
    st = tx.state
    foes = [f for f in foes if f != pc and f in st.entities and st.entities[f].kind in FOES]
    rec = record(st)
    new = [f for f in dict.fromkeys(foes) if f not in rec.get("foes", [])]
    if not new:
        return False
    for f in new:
        ensure_vitality(tx, tctx.rules, f)
        if _band(st, pc, f) is None:
            _set_band(tx, pc, f, "near", "06.3.9")
    # each foe's heaviest listed harm (its line's standard or heavy blow, T-09-3): what 07.3.3's severity row reads
    # for a foe with no `attacks` data of its own (a named NPC who fights)
    lines = {f: _line(tctx.rules, st.entities[f]) for f in new}
    sev = {**(rec.get("severity") or {}),
           **{f: f"S{max(int(ln['sev']), int(ln.get('heavy') or 0))}" for f, ln in lines.items()}}
    mode = clock.mode_of(st.time.mode)  # a scene framed in conflict mode has no mode of its own to go back to
    tx.add(Event.of("meta_set", source="engine", rule_id="06.2.1", key=KEY,
                    value={"pc": pc, "foes": [*rec.get("foes", []), *new], "severity": sev,
                           "previous": rec.get("previous") or (mode if mode != "conflict" else "free")}))
    if rec:
        return False
    set_mode(tctx, "conflict", reason)
    mark_boundary(tctx, "conflict_start", {"participants": [pc, *new], "reason": reason})
    return True


def able(st: Any, eid: str) -> bool:  # rule: 06.13.1
    """Able and willing to act: exists, not defeated or down, and still in the scene (one that left has fled)."""
    from engine.world.scenes import cast_present

    e = st.entities.get(eid)
    if e is None or e.exists != "exists" or st.fact_value(eid, "defeated") or st.fact_value(eid, "down"):
        return False
    return st.scene is None or eid in cast_present(st)


def check_end(tctx: TimeContext, pc: str) -> bool:  # rule: 06.13.1
    """(a) no foe able and willing, or (d) the PC down or dead: `conflict_end`, then the previous time mode."""
    from engine.harm.state import DEAD, harm_state, is_down

    st = tctx.tx.state
    rec = record(st)
    if not rec:
        return False
    if not (is_down(st, pc) or harm_state(st, pc) == DEAD) and any(able(st, f) for f in rec.get("foes", [])):
        return False
    mark_boundary(tctx, "conflict_end", {"foes": rec.get("foes", [])})
    # the record goes with the fight: a later scene framed in conflict mode must not revive these foes without a
    # conflict_start of its own (playtest 20261008-135049: the next scene's opener "resumed" the ended fight)
    tctx.tx.add(Event.of("meta_set", source="engine", rule_id="06.13.1", key=KEY, value=None))
    set_mode(tctx, str(rec.get("previous") or "free"), "the fight is over (06.13.1)")
    return True


# ------------------------------------------------------------------------------------------- harm


def weapon(rules: Any, st: Any, actor: str, text: str) -> dict[str, Any]:  # rule: 06.4.4
    """The weight of what the blow is struck with: a weapon named in the beat's words (the longest example that
    fits), else bare hands when the words say so, else the first weapon the actor carries, else unarmed."""
    weights = list(rules.doc("conflict")["weapon_weights"])
    named = sorted(((str(x).split("(")[0].strip(), w) for w in weights for x in w.get("examples") or ()),
                   key=lambda p: -len(p[0]))
    for ex, w in named:
        if ex and re.search(rf"\b{re.escape(ex)}s?\b", text, re.IGNORECASE):
            return w
    if not UNARMED.search(text):
        tags = {t for e in st.entities.values() if e.kind == "item" and e.data.get("owner") == actor for t in e.tags}
        for w in weights:
            if any(t == it or t.startswith(it + ".") for t in tags for it in w.get("item_tags") or ()):
                return w
    return next(w for w in weights if w["id"] == "unarmed")


def state_words(st: Any, eid: str) -> str:  # rule: 07.1.1
    """How a hurt creature looks, in words (never a number): fresh, worn, bloodied, staggered, down, dying, dead."""
    from engine.harm.state import descriptor

    d = st.fact_value(eid, "defeated")
    if isinstance(d, dict):
        return {"dead": "dead", "dying": "down and dying", "unconscious": "down, out cold"}.get(
            str(d.get("manner")), "down")
    return descriptor(st, eid)


def strike_harm(tx: Any, rules: Any, rng: Any, frame: Any, delivered: int) -> tuple[Any, str]:  # rule: 06.4.3
    # rule: PR-06-3
    """A landed Strike: the weapon's base severity shifted by (delivered reach - 2) rungs, then `apply_harm` on
    the target in the harm mode the words ask for (lethal unless the player said otherwise, 06.4.8)."""
    from engine.harm.apply import SEVERITIES, apply_harm, shift
    from engine.harm.ctx import HarmCtx

    # ponytail: no dealer-side pass (06.4.6), mastery (06.4.5) or called shots; harm.physical only
    beat = frame.beat
    text = f"{beat.method} {beat.intent}"
    w = weapon(rules, tx.state, beat.actor, text)
    sev = shift(str(w["base_severity"]), delivered - 2) or (SEVERITIES[0] if delivered < 2 else SEVERITIES[-1])
    ensure_vitality(tx, rules, beat.target)
    res = apply_harm(HarmCtx.of(tx, rules, rng), beat.target, severity=sev, harm_tags=["harm.physical"],
                     source=beat.actor, frame_id=frame.id, lethal=frame.lethal,
                     mode="nonlethal" if NONLETHAL.search(text) else "lethal")
    tx.add_all(res.events)
    return res, state_words(tx.state, beat.target)


def foe_beat(tctx: TimeContext, rng: Any, foe: str, pc: str) -> tuple[str, Any]:  # rule: 06.9.2
    # rule: 06.9.4
    """The foe's beat by `beh.default_melee`: prone -> stand; not engaged with the PC -> move one band toward;
    else Strike: d20 + its line's attack against the PC's Guard (06.4.1), its line's severity on a hit (one
    rung more on a critical), harm applied by the engine (INV-2). Returns (what it did, in words; the harm)."""
    from engine.harm.apply import apply_harm, shift
    from engine.harm.ctx import HarmCtx
    from engine.harm.dice import degree
    from engine.harm.lethal import effective
    from engine.resolve.frame import _defense
    from engine.store.conditions import remove_condition

    # ponytail: melee row only (no break/windup/flank/ranged rows, no Fend or reactions); one beat per round
    tx, rules = tctx.tx, tctx.rules
    st = tx.state
    prone = [c for c in st.conditions_on(foe) if c.condition_id == "cond.prone"]
    if prone:
        tx.add_all(remove_condition(st, rules, prone[0].instance_id, "stands (06.9.4)", rule_id="06.9.4").events)
        return "gets back to its feet", None
    band = _band(st, foe, pc) or "near"
    if band != "engaged":
        to = BANDS[max(0, BANDS.index(band) - 1)] if band in BANDS else "close"
        _set_band(tx, foe, pc, to, "06.9.4")
        return ("closes in, now at arm's reach of you" if to == "engaged" else "moves toward you"), None
    line = _line(rules, st.entities[foe])
    guard = _defense(rules, st, pc, "agility", "deed.martial")
    natural = int(rng.d(20, f"foe strike {foe} (06.9.2)"))
    deg, _ = degree(natural, int(line["atk"]), guard)
    if deg not in ("success", "critical_success"):
        return "strikes at you and misses", None
    sev = f"S{int(line['sev'])}"
    sev = (shift(sev, 1) or sev) if deg == "critical_success" else sev
    res = apply_harm(HarmCtx.of(tx, rules, rng), pc, severity=sev, harm_tags=["harm.physical"], source=foe,
                     lethal=effective(st, foe) is not None)
    tx.add_all(res.events)
    return f"strikes you and lands it: you are {state_words(st, pc)}", res
