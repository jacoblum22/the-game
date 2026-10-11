"""Spec 033 P3 (D2): what an adversary may do now, and doing the act the DM picked. The DM chooses (06.9.1); code lists
the legal acts (T-06-16), rolls the pick (06.9.2) and writes its result. Nothing here reads words or infers a choice.

    legal_acts(st, foe, pc)                         # T-06-16: the acts legal for the foe now, in table order
    default_act(rules, st, foe, pc, legal)          # the logged default: first behavior-list row that maps to a legal act
    act(tctx, rng, foe, pick, target, nonlethal)    # -> FoeDone(said, harm, pick, roll): conflict.foe_beat's pair + more
"""

from __future__ import annotations

from typing import Any, NamedTuple

from engine.resolve import conflict
from engine.resolve.change import HOLDS
from engine.time.scheduler import TimeContext

ACTS = ("strike", "close_in", "withdraw", "stand", "break_free", "grapple", "flee", "yield", "wait")  # T-06-16 columns
OFF_SCENE = "elsewhere"  # where a fled foe goes: off the scene (the same place `npc_leaves` with no place uses)
# `beh.*` default-list `do` text (conflict.yaml#default_behaviors, exact) -> the T-06-16 act; rows not here (break row,
# windup, flank, reload, aim, defend, cover) are outside the table and skipped. Exact keys of rule data, not prose.
_DO_ACT = {"break free": "break_free", "stand": "stand", "move toward it (withdraw first if engaged elsewhere)": "close_in",
           "move to engage the target": "close_in", "move to engage": "close_in", "strike the target": "strike",
           "strike": "strike", "strike (numbers apply)": "strike", "shoot the target": "strike", "grapple": "grapple"}


def holders(st: Any, foe: str) -> list[str]:  # rule: 06.5.2
    """Who holds `foe` (the source of each hold-ladder condition on it)."""
    return list(dict.fromkeys(str((i.source or {}).get("entity")) for i in st.conditions_on(foe)
                              if i.condition_id in HOLDS and (i.source or {}).get("entity") in st.entities))


def kills(st: Any, foe: str) -> bool:  # rule: 06.9.3
    """A `kill` side: its objective or defeat disposition is kill (07.6.1)."""
    d = st.entities[foe].data
    return "kill" in (d.get("objective"), d.get("defeat_disposition"))


def pc_open(st: Any, foe: str, pc: str) -> bool:  # rule: 06.9.3
    """The PC may be struck by `foe`: a Dying (or Down) PC only by a kill side."""
    from engine.harm.state import DEAD, DYING, harm_state, is_down

    return not (is_down(st, pc) or harm_state(st, pc) in (DYING, DEAD)) or kills(st, foe)


def legal_acts(st: Any, foe: str, pc: str) -> list[str]:  # rule: T-06-16
    """The acts legal for `foe` now (06.9.1), by its state after the PC's beat; none for one that cannot act."""
    held = {i.condition_id for i in st.conditions_on(foe) if i.condition_id in HOLDS}
    if "cond.pinned" in held:
        ok = ["break_free", "yield", "wait"]
    elif "cond.restrained" in held:
        ok = ["strike", "break_free", "yield", "wait"]  # ponytail: any weapon, not only a close-quarters one (C4)
    elif "cond.grabbed" in held:
        ok = ["strike", "break_free", "grapple", "yield", "wait"]
    elif any(i.condition_id == "cond.prone" for i in st.conditions_on(foe)):
        ok = ["stand", "yield", "wait"]
    elif (conflict._band(st, foe, pc) or "near") == "engaged":
        ok = ["strike", "withdraw", "grapple", "flee", "yield", "wait"]
    else:
        ok = ["close_in", "flee", "yield", "wait"]
    if not pc_open(st, foe, pc):  # 06.9.3: nothing to strike or grab
        ok = [a for a in ok if a not in ("strike", "grapple")]
    return ok


def default_act(rules: Any, st: Any, foe: str, legal: list[str]) -> str:  # rule: 06.9.4
    """The first row of the foe's default behavior list whose act is in T-06-16 and legal now, else `wait`. The rows'
    own `when` text is not evaluated: each mapped act is legal only in the state its `when` names."""
    role = str(st.entities[foe].data.get("default_behavior_role") or "melee")
    rows = next((b["priority_list"] for b in rules.doc("conflict")["default_behaviors"]
                 if b["id"] == f"beh.default_{role}"), [])
    return next((a for r in rows if (a := _DO_ACT.get(str(r["do"]))) in legal), "wait")


def _name(st: Any, eid: str) -> str:
    return str(st.entities[eid].name)


class FoeDone(NamedTuple):
    """What a foe's act came to [spec 033 P11]: its words, the harm (a landed strike's HarmResult) or None, the act
    picked, and the roll of a strike or grapple (`d20`, `total`, the target's `guard`; None for the rest). The roll is
    recorded here and not displayed: world_step decides whether a foe's roll shows (06.9.6)."""

    said: str
    harm: Any
    pick: str
    roll: dict[str, int] | None


def act(tctx: TimeContext, rng: Any, foe: str, pick: str, target: str, nonlethal: bool = False) -> FoeDone:
    roll: dict[str, int] = {}
    said, harm = _act(tctx, rng, foe, pick, target, nonlethal, roll)
    return FoeDone(said, harm, pick, roll or None)


def _act(tctx: TimeContext, rng: Any, foe: str, pick: str, target: str, nonlethal: bool,
         roll: dict[str, int]) -> tuple[str, Any]:  # rule: 06.9.2
    """Do `pick` (legal; the caller checked) against `target`: the words of what the foe did, and the harm (a landed
    strike's HarmResult) or None. Each roll is the foe's own line against the target's defense (06.9.2); a strike or
    grapple leaves its roll in `roll`."""
    from engine.harm.apply import apply_harm, shift
    from engine.harm.ctx import HarmCtx
    from engine.harm.dice import degree
    from engine.harm.lethal import effective
    from engine.resolve.frame import _defense
    from engine.store.conditions import remove_condition

    tx, rules = tctx.tx, tctx.rules
    st = tx.state
    pc = st.entities[target]
    you = "you" if pc.kind == "pc" else _name(st, target)
    line = conflict._line(rules, st.entities[foe])
    if pick == "wait":
        return "holds back, watching", None
    if pick == "yield":
        from engine.world.common import fact

        tx.add(fact(tx, foe, "defeated", {"manner": "yielded", "victor": target}, rule_id="06.11.7", source="ruling",
                    visibility="shown"))
        return "throws down its guard and yields", None
    if pick == "flee":
        from engine.store.events import Event

        tx.add(Event.of("position_set", source="engine", rule_id="06.12.1", entity=foe, location=OFF_SCENE))
        return "turns and flees the scene", None
    if pick == "stand":
        prone = [c for c in st.conditions_on(foe) if c.condition_id == "cond.prone"]
        tx.add_all(remove_condition(st, rules, prone[0].instance_id, "stands (06.9.4)", rule_id="06.9.4").events)
        return "gets back to its feet", None
    if pick == "break_free":
        return conflict._break_free(tctx, rng, foe, holders(st, foe)[0]), None
    band = conflict._band(st, foe, target) or "near"
    i = conflict.BANDS.index(band) if band in conflict.BANDS else 2
    if pick == "close_in":
        to = conflict.BANDS[max(0, i - 1)]
        conflict._set_band(tx, foe, target, to, "06.9.4")
        return (f"closes in, now at arm's reach of {you}" if to == "engaged" else f"moves toward {you}"), None
    if pick == "withdraw":
        conflict._set_band(tx, foe, target, conflict.BANDS[min(len(conflict.BANDS) - 1, i + 1)], "06.12.1")
        return f"pulls back from {you}", None
    if pick == "grapple":
        from engine.resolve.change import hold

        natural = int(rng.d(20, f"foe grapple {foe} (06.5.2)"))
        grip = _defense(rules, st, target, "might", "deed.martial")
        deg, _ = degree(natural, int(line["atk"]), grip)
        roll.update(d20=natural, total=natural + int(line["atk"]), guard=int(grip))
        if deg not in ("success", "critical_success"):
            return f"grabs at {you} and misses", None
        tx.add_all(hold(tx, rules, target, foe, 3 if deg == "critical_success" else 2))
        return f"seizes {you} in a hold", None
    # strike
    guard = _defense(rules, st, target, "agility", "deed.martial")
    natural = int(rng.d(20, f"foe strike {foe} (06.9.2)"))
    deg, _ = degree(natural, int(line["atk"]), guard)
    roll.update(d20=natural, total=natural + int(line["atk"]), guard=int(guard))
    if deg not in ("success", "critical_success"):
        return f"strikes at {you} and misses", None
    sev = f"S{int(line['sev'])}"
    sev = (shift(sev, 1) or sev) if deg == "critical_success" else sev
    res = apply_harm(HarmCtx.of(tx, rules, rng), target, severity=sev, harm_tags=["harm.physical"], source=foe,
                     lethal=effective(st, foe) is not None, mode="nonlethal" if nonlethal else "lethal")
    tx.add_all(res.events)
    return f"strikes {you} and lands it: {'you are' if pc.kind == 'pc' else _name(st, target) + ' is'} " \
           f"{conflict.state_words(st, target)}", res
