"""The exact parts of the game: dice, the character sheet, the fight tracker.

The DM model decides everything; these functions only do what it asks, do the arithmetic, apply what the 2014
rules state as the result (0 HP, death saves, rests) and refuse impossible changes. They never decide story.
Every change is all-or-nothing: on any error nothing is applied.
"""

from __future__ import annotations

import copy
import random
import re
from typing import Any

_TERM = re.compile(r"\s*([+-])?\s*(?:(\d*)d(\d+)|(\d+))\s*", re.IGNORECASE)


class Refused(Exception):
    """A change the rules or the sheet don't allow. The message tells the DM what to do instead."""


# ---------- dice ----------

def roll(expr: str, mode: str = "normal", rng: random.Random | None = None) -> dict[str, Any]:
    """Roll a dice expression such as `1d20+5` or `2d6+1d4+3`. `advantage`/`disadvantage` roll the first d20 twice
    and keep the higher/lower. Returns the parts and the total."""
    rng = rng or random.Random()
    if mode not in ("normal", "advantage", "disadvantage"):
        raise Refused(f"mode must be normal, advantage or disadvantage, not {mode!r}")
    pos, parts, total, d20_done = 0, [], 0, False
    text = expr.strip()
    if not text:
        raise Refused("empty dice expression; use something like 1d20+3")
    while pos < len(text):
        m = _TERM.match(text, pos)
        if not m or m.end() == pos:
            raise Refused(f"can't read dice expression {expr!r}; use something like 1d20+3 or 2d6+2")
        sign = -1 if m.group(1) == "-" else 1
        if m.group(3):
            n, sides = int(m.group(2) or 1), int(m.group(3))
            if not (1 <= n <= 100 and 2 <= sides <= 1000):
                raise Refused(f"unreasonable dice {m.group(0).strip()!r}")
            if sides == 20 and n == 1 and mode != "normal" and not d20_done:
                pair = [rng.randint(1, 20), rng.randint(1, 20)]
                kept = max(pair) if mode == "advantage" else min(pair)
                parts.append({"dice": "1d20", "rolls": pair, "kept": kept, "sign": sign})
                total += sign * kept
                d20_done = True
            else:
                rolls = [rng.randint(1, sides) for _ in range(n)]
                parts.append({"dice": f"{n}d{sides}", "rolls": rolls, "sign": sign})
                total += sign * sum(rolls)
                if sides == 20 and n == 1:
                    d20_done = True
        else:
            parts.append({"flat": int(m.group(4)), "sign": sign})
            total += sign * int(m.group(4))
        pos = m.end()
    if mode != "normal" and not any("kept" in p for p in parts):
        raise Refused("advantage/disadvantage applies to a single d20 roll, e.g. 1d20+4")
    natural = next((p.get("kept", p["rolls"][0]) for p in parts if p.get("dice") == "1d20"), None)
    return {"expr": expr, "mode": mode, "parts": parts, "total": total, "natural": natural}


def roll_text(r: dict[str, Any], reason: str = "") -> str:
    bits = []
    for p in r["parts"]:
        sign = "-" if p["sign"] < 0 else "+"
        if "flat" in p:
            bits.append(f"{sign} {p['flat']}")
        elif "kept" in p:
            bits.append(f"{sign} {p['dice']} {p['rolls']}→{p['kept']}")
        else:
            bits.append(f"{sign} {p['dice']} {p['rolls']}")
    body = " ".join(bits).removeprefix("+ ")
    mode = f" ({r['mode']})" if r["mode"] != "normal" else ""
    nat = " (natural 20)" if r["natural"] == 20 else " (natural 1)" if r["natural"] == 1 else ""
    return f"{reason + ': ' if reason else ''}{r['expr']}{mode} = {body} = {r['total']}{nat}"


# ---------- coins ----------

def coins_text(cp: int) -> str:
    gp, rest = divmod(cp, 100)
    sp, cp = divmod(rest, 10)
    return " ".join(f"{v} {u}" for v, u in ((gp, "gp"), (sp, "sp"), (cp, "cp")) if v) or "0 gp"


# ---------- the character sheet ----------

def change_pc(sheet: dict[str, Any], ch: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """Apply a change to the PC's sheet. Returns (new sheet, lines saying what changed). Raises Refused."""
    s = copy.deepcopy(sheet)
    hp, out = s["hp"], []

    def _int(key: str) -> int:
        v = ch.get(key) or 0
        if not isinstance(v, int) or v < 0:
            raise Refused(f"{key} must be a whole number of 0 or more")
        return v

    if ch.get("long_rest"):
        # SRD Long Rest: "a character must have at least 1 hit point at the start of the rest to gain its benefits".
        # The code can't know the "no more than one long rest in a 24-hour period" limit; the DM checks that.
        if "dead" in s["conditions"] or hp["current"] < 1:
            raise Refused("a long rest gives no benefit to a character with 0 hit points (or dead): "
                          "they need at least 1 hit point at the start of the rest. Heal them first")
        hp["current"], hp["temp"] = hp["max"], 0
        for slot in s.get("spell_slots", {}).values():
            slot["left"] = slot["max"]
        for res in s.get("resources", {}).values():
            res["left"] = res["max"]
        hd = s["hit_dice"]
        hd["left"] = min(hd["max"], hd["left"] + max(1, hd["max"] // 2))
        s["death_saves"] = {"successes": 0, "failures": 0}
        out.append("long rest: HP, spell slots and features restored; hit dice regained")
    if ch.get("short_rest"):
        back = [n for n, r in s.get("resources", {}).items() if r["recharge"] == "short" and r["left"] < r["max"]]
        for n in back:
            s["resources"][n]["left"] = s["resources"][n]["max"]
        for lvl, slot in s.get("spell_slots", {}).items():
            if slot.get("recharge") == "short" and slot["left"] < slot["max"]:
                slot["left"] = slot["max"]
                back.append(f"level-{lvl} spell slots")
        out.append("short rest" + (f": {', '.join(back)} restored" if back else ""))

    n = _int("hit_dice_spent")
    if n:
        # SRD Short Rest: the player rolls each Hit Die and adds CON; "can decide to spend an additional Hit Die after each roll".
        if n > 1:
            raise Refused("spend hit dice one at a time: for each one the player rolls it and adds their CON modifier, "
                          "and decides whether to spend another only after seeing that roll")
        if s["hit_dice"]["left"] < 1:
            raise Refused(f"no hit dice left (0/{s['hit_dice']['max']})")
        s["hit_dice"]["left"] -= 1
        out.append(f"spent 1 hit die ({s['hit_dice']['left']}/{s['hit_dice']['max']} left): roll 1{s['hit_dice']['die']} and add "
                   f"the CON modifier (CON {s['abilities']['CON']}), then pass the total as heal; the player "
                   "decides whether to spend another after the roll")

    temp = _int("temp_hp")
    if temp:
        if temp > hp["temp"]:
            out.append(f"temporary HP {hp['temp']} → {temp} (temporary HP don't stack; the higher is kept)")
            hp["temp"] = temp
        else:
            out.append(f"temporary HP stay {hp['temp']} (the new {temp} is not higher; they don't stack)")

    dmg = _int("damage")
    if dmg:
        was = hp["current"]
        absorbed = min(hp["temp"], dmg)
        hp["temp"] -= absorbed
        left = dmg - absorbed
        if was == 0 and left >= hp["max"]:
            _add(s, "dead")
            out.append(f"took {dmg} damage at 0 HP, at least max HP {hp['max']}: the character dies")
        elif was == 0 and left:
            # SRD: damage at 0 HP is one death save failure, two if from a critical hit; it also ends 'stable'.
            n = 2 if ch.get("critical_hit") else 1
            s["death_saves"]["failures"] = min(3, s["death_saves"]["failures"] + n)
            out.append(f"took {dmg} damage at 0 HP: {'two death save failures (critical hit)' if n == 2 else 'one death save failure'}")
            if "stable" in s["conditions"]:
                _remove(s, "stable")
                out.append("no longer stable: death saving throws start again")
        else:
            hp["current"] = max(0, was - left)
            out.append(f"took {dmg} damage" + (f" ({absorbed} absorbed by temporary HP)" if absorbed else "")
                       + f": HP {was} → {hp['current']}")
            if hp["current"] == 0:
                over = left - was
                if over >= hp["max"]:
                    _add(s, "dead")
                    out.append(f"massive damage: {over} left over ≥ max HP {hp['max']}: the character dies")
                else:
                    _add(s, "unconscious")
                    out.append("at 0 HP: unconscious; make death saving throws on each of their turns")

    heal = _int("heal")
    if heal:
        if "dead" in s["conditions"]:
            raise Refused("the character is dead; ordinary healing doesn't work. A spell or effect that returns the dead to life "
                          "is recorded by removing the 'dead' condition (conditions_removed), then healing")
        was = hp["current"]
        hp["current"] = min(hp["max"], was + heal)
        out.append(f"healed {heal}: HP {was} → {hp['current']}")
        if was == 0 and hp["current"] > 0:
            s["death_saves"] = {"successes": 0, "failures": 0}
            _remove(s, "unconscious")
            _remove(s, "stable")
            out.append("conscious again; death saves reset")

    for kind in ("successes", "failures"):
        n = _int(f"death_save_{kind}")
        if n:
            if hp["current"] > 0:
                raise Refused("death saves are only made at 0 HP")
            if "dead" in s["conditions"]:
                raise Refused("the character is dead; no death saves")
            if "stable" in s["conditions"]:
                raise Refused("the character is stable and doesn't make death saving throws "
                              "(they start again only if the character takes damage)")
            s["death_saves"][kind] = min(3, s["death_saves"][kind] + n)
            out.append(f"death save {kind}: {s['death_saves'][kind]}/3")
    if s["death_saves"]["failures"] >= 3 and "dead" not in s["conditions"]:
        _add(s, "dead")
        out.append("three death save failures: the character dies")
    elif s["death_saves"]["successes"] >= 3 and "stable" not in s["conditions"] and hp["current"] == 0:
        _add(s, "stable")
        s["death_saves"] = {"successes": 0, "failures": 0}  # SRD: both counts reset when you become stable
        out.append("three death save successes: stable (unconscious at 0 HP, no death saves; regains 1 HP after 1d4 hours "
                   "unless healed); death save counts reset")

    for key, delta in (("spend_slot", -1), ("restore_slot", 1)):
        lvl = ch.get(key)
        if lvl:
            slot = s.get("spell_slots", {}).get(str(lvl))
            if not slot:
                raise Refused(f"no level-{lvl} spell slots on this sheet")
            if delta < 0 and slot["left"] == 0:
                raise Refused(f"no level-{lvl} spell slots left (0/{slot['max']})")
            if delta > 0 and slot["left"] == slot["max"]:
                raise Refused(f"level-{lvl} slots are already full")
            slot["left"] += delta
            out.append(f"level-{lvl} spell slots: {slot['left']}/{slot['max']}")

    amount = ch.get("resource_amount") or 1
    if not isinstance(amount, int) or amount < 1:
        raise Refused("resource_amount must be a whole number of 1 or more")
    for key, sign in (("use_resource", -1), ("restore_resource", 1)):
        name = ch.get(key)
        if name:
            res = s.get("resources", {}).get(name)
            if not res:
                raise Refused(f"no resource {name!r}; the sheet has: {', '.join(s.get('resources', {})) or 'none'}")
            if sign < 0 and res["left"] < amount:
                raise Refused(f"{name} has {res['left']}/{res['max']} left; it comes back on a {res['recharge']} rest")
            res["left"] = min(res["max"], res["left"] + sign * amount)
            out.append(f"{name}: {res['left']}/{res['max']}")

    for it in ch.get("items_lost") or []:
        name, qty = it["item"], int(it.get("qty", 1))  # not `or 1`: an explicit 0 must be refused, not turned into 1
        if qty < 1:
            raise Refused("each lost item needs a quantity of 1 or more")
        have = s["items"].get(name, 0)
        if have < qty:
            raise Refused(f"the character has {have} × {name!r}; items on the sheet: {', '.join(s['items'])}")
        s["items"][name] = have - qty
        if not s["items"][name]:
            del s["items"][name]
        out.append(f"lost {qty} × {name}")
    for it in ch.get("items_gained") or []:
        name, qty = it["item"].strip(), int(it.get("qty") or 1)
        if not name or qty < 1:
            raise Refused("each gained item needs a name and a quantity of 1 or more")
        s["items"][name] = s["items"].get(name, 0) + qty
        out.append(f"gained {qty} × {name}")

    gp = ch.get("coin_change_gp") or 0
    if gp:
        cp = round(gp * 100)
        if s["coins_cp"] + cp < 0:
            raise Refused(f"not enough money: the character has {coins_text(s['coins_cp'])}")
        s["coins_cp"] += cp
        out.append(f"money {'+' if cp > 0 else '-'}{coins_text(abs(cp))}: now {coins_text(s['coins_cp'])}")

    for c in ch.get("conditions_added") or []:
        _add(s, c)
        out.append(f"condition added: {c}")
        if c == "stable":  # e.g. first aid (DC 10 Wisdom (Medicine)): SRD resets both counts on becoming stable
            s["death_saves"] = {"successes": 0, "failures": 0}
    for c in ch.get("conditions_removed") or []:
        if c not in s["conditions"]:
            raise Refused(f"condition {c!r} is not on the sheet; conditions now: {', '.join(s['conditions']) or 'none'}")
        _remove(s, c)
        if c == "dead":  # a revival starts fresh, so 3 old failures don't kill the character again on the next change
            s["death_saves"] = {"successes": 0, "failures": 0}
        out.append(f"condition removed: {c}")

    if ch.get("prepare_spells") is not None:
        out.append(_prepare(s, ch["prepare_spells"], bool(ch.get("long_rest"))))
    for name in ch.get("spellbook_add") or []:
        out.append(_spellbook_add(s, name))
    if ch.get("ac_reset"):
        s["ac_now"] = None
        out.append(f"AC back to {s['ac']}")
    if ch.get("ac_set") is not None:
        v, why = ch["ac_set"], str(ch.get("ac_reason") or "").strip()
        if not isinstance(v, int) or v < 0 or not why:
            raise Refused("ac_set needs a whole number and ac_reason (what sets it, e.g. 'Mage Armor: 13 + DEX')")
        s["ac_now"] = {"value": v, "reason": why}
        out.append(f"AC now {v} ({why})")

    xp = _int("xp_gained")
    if xp:
        s["xp"] += xp
        out.append(f"XP +{xp}: {s['xp']}")

    if not out:
        raise Refused("nothing to change: pass at least one field")
    return s, out


def _max_slot_level(s: dict[str, Any]) -> int:
    return max((int(k) for k, v in s.get("spell_slots", {}).items() if v["max"]), default=0)


def _srd_spell(name: str) -> dict[str, Any]:
    from dm import srd

    try:
        return srd.spell(name)
    except srd.Bad:
        raise Refused(f"no SRD spell {name!r}") from None


def _prepare(s: dict[str, Any], names: list[str], long_rest: bool) -> str:
    sc = s.get("spellcasting") or {}
    if "prepare_count" not in sc:
        raise Refused("this character doesn't prepare spells")
    if not long_rest:
        raise Refused("prepared spells change when a long rest finishes: pass prepare_spells together with long_rest")
    always, picked = set(sc.get("always_prepared", [])), []
    for n in names:
        sp = _srd_spell(n)
        if sp["name"] in always or sp["name"] in picked:
            continue
        if sc["prepare_from"] == "spellbook":
            if sp["name"] not in sc["spellbook"]:
                raise Refused(f"{sp['name']} is not in the spellbook: {', '.join(sc['spellbook'])}")
        elif not any(c["index"] == sc["class"] for c in sp["classes"]):
            raise Refused(f"{sp['name']} is not on the {sc['class']} spell list")
        if not 1 <= sp["level"] <= _max_slot_level(s):
            raise Refused(f"{sp['name']} is level {sp['level']}; prepared spells are level 1-{_max_slot_level(s)}")
        picked.append(sp["name"])
    if not 1 <= len(picked) <= sc["prepare_count"]:
        raise Refused(f"prepare 1 to {sc['prepare_count']} spells (always-prepared spells don't count)")
    sc["prepared"] = picked
    return "prepared: " + ", ".join(picked)


def _spellbook_add(s: dict[str, Any], name: str) -> str:
    sc = s.get("spellcasting") or {}
    if "spellbook" not in sc:
        raise Refused("only a wizard has a spellbook")
    sp = _srd_spell(name)
    if not any(c["index"] == "wizard" for c in sp["classes"]):
        raise Refused(f"{sp['name']} is not a wizard spell")
    if not 1 <= sp["level"] <= _max_slot_level(s):
        raise Refused(f"{sp['name']} is level {sp['level']}; a wizard can copy spells of level 1-{_max_slot_level(s)}")
    if sp["name"] in sc["spellbook"]:
        raise Refused(f"{sp['name']} is already in the spellbook")
    sc["spellbook"].append(sp["name"])
    return f"{sp['name']} copied into the spellbook (record the cost: 50 gp and 2 hours per spell level)"


def _add(s: dict[str, Any], c: str) -> None:
    if c not in s["conditions"]:
        s["conditions"].append(c)


def _remove(s: dict[str, Any], c: str) -> None:
    if c in s["conditions"]:
        s["conditions"].remove(c)


def status(s: dict[str, Any]) -> str:
    """What changes during play, for the DM every turn and for the player on request."""
    hp = s["hp"]
    lines = [f"HP {hp['current']}/{hp['max']}" + (f" (+{hp['temp']} temporary)" if hp["temp"] else "")
             + f" · AC {ac_text(s)} · hit dice {s['hit_dice']['left']}/{s['hit_dice']['max']} {s['hit_dice']['die']}"
             + f" · XP {s['xp']}"]
    if s.get("spell_slots"):
        lines.append("Spell slots: " + ", ".join(f"level {k}: {v['left']}/{v['max']}" for k, v in s["spell_slots"].items()))
    sc = s.get("spellcasting") or {}
    if sc.get("prepared") is not None:
        lines.append("Prepared spells: " + (", ".join(sc.get("always_prepared", []) + sc["prepared"]) or "none"))
    if sc.get("spellbook"):
        lines.append("Spellbook: " + ", ".join(sc["spellbook"]))
    if s.get("resources"):
        lines.append("Features: " + ", ".join(f"{k} {v['left']}/{v['max']} ({v['recharge']} rest)"
                                              for k, v in s["resources"].items()))
    lines.append("Conditions: " + (", ".join(s["conditions"]) or "none"))
    ds = s["death_saves"]
    if hp["current"] == 0 and "dead" in s["conditions"]:
        lines.append("Dead: no death saves")
    elif hp["current"] == 0 and "stable" in s["conditions"]:
        lines.append("Stable at 0 HP: no death saves unless it takes damage")
    elif hp["current"] == 0:
        lines.append(f"Death saves: {ds['successes']} successes, {ds['failures']} failures")
    lines.append("Money: " + coins_text(s["coins_cp"]))
    lines.append("Items: " + ", ".join(f"{n}" + (f" ×{q}" if q > 1 else "") for n, q in s["items"].items()))
    return "\n".join(lines)


def ac_text(s: dict[str, Any]) -> str:
    now = s.get("ac_now")
    return f"{now['value']} ({now['reason']}; normally {s['ac']})" if now else str(s["ac"])


# ---------- the fight tracker ----------

def add_combatants(fight: dict[str, Any] | None, pc_name: str, combatants: list[dict[str, Any]]) -> tuple[dict[str, Any], str]:
    """Start a fight or add arrivals. Each combatant: name, initiative, and (not for the PC) hp and ac. The PC is
    the entry named `pc`. Order is by initiative, highest first; ties keep the order given (the DM settles ties).
    A new fight starts with nobody's turn yet (turn -1): the first next_turn starts the first combatant's turn."""
    f = copy.deepcopy(fight) if fight else {"round": 1, "turn": -1, "order": []}
    names = {c["name"] for c in f["order"]}
    new = []
    for c in combatants:
        name = str(c.get("name", "")).strip()
        is_pc = name.lower() == "pc" or name == pc_name
        name = pc_name if is_pc else name
        if not name or name in names:
            raise Refused(f"each combatant needs a unique name; already in the fight: {', '.join(names) or 'nobody'}")
        if not isinstance(c.get("initiative"), int):
            raise Refused(f"{name} needs an initiative total (roll it first)")
        if not is_pc and not (isinstance(c.get("hp"), int) and c["hp"] > 0 and isinstance(c.get("ac"), int)):
            raise Refused(f"{name} needs hp (above 0) and ac from its stat block")
        names.add(name)
        new.append({"name": name, "initiative": c["initiative"], "pc": is_pc, "hp": c.get("hp"), "max_hp": c.get("hp"),
                    "ac": c.get("ac"), "conditions": []})
    current = f["order"][f["turn"]]["name"] if f["turn"] >= 0 else None
    f["order"] = sorted(f["order"] + new, key=lambda c: -c["initiative"])  # stable: ties keep the given order
    if current:
        f["turn"] = next(i for i, c in enumerate(f["order"]) if c["name"] == current)
    return f, ("Fight started. " if not fight else "Added to the fight. ") + "Order: " + order_text(f) + (
        ". Nobody has had a turn yet: next_turn starts the first one." if f["turn"] < 0 else "")


def change_creature(fight: dict[str, Any] | None, ch: dict[str, Any]) -> tuple[dict[str, Any], str]:
    if not fight:
        raise Refused("no fight is on; start one with add_combatants")
    f = copy.deepcopy(fight)
    c = _find(f, ch.get("name", ""))
    if c["pc"]:
        raise Refused("the PC's HP and conditions live on the character sheet: use change_pc")
    out = []
    if ch.get("remove"):
        i = f["order"].index(c)
        del f["order"][i]
        if i <= f["turn"]:
            f["turn"] -= 1  # next_turn then lands on whoever came after it
        return f, f"{c['name']} removed from the fight. Order: {order_text(f)}"
    for key in ("damage", "heal"):
        v = ch.get(key) or 0
        if not isinstance(v, int) or v < 0:
            raise Refused(f"{key} must be a whole number of 0 or more")
    if ch.get("damage"):
        was = c["hp"]
        c["hp"] = max(0, was - ch["damage"])
        out.append(f"{c['name']} took {ch['damage']}: HP {was} → {c['hp']}" + (" (0 HP)" if not c["hp"] else ""))
    if ch.get("heal"):
        was = c["hp"]
        c["hp"] = min(c["max_hp"], was + ch["heal"])
        out.append(f"{c['name']} healed {ch['heal']}: HP {was} → {c['hp']}")
    for cond in ch.get("conditions_added") or []:
        if cond not in c["conditions"]:
            c["conditions"].append(cond)
        out.append(f"{c['name']}: {cond}")
    for cond in ch.get("conditions_removed") or []:
        if cond not in c["conditions"]:
            raise Refused(f"{c['name']} doesn't have {cond!r}; it has: {', '.join(c['conditions']) or 'none'}")
        c["conditions"].remove(cond)
        out.append(f"{c['name']}: no longer {cond}")
    if not out:
        raise Refused("nothing to change: pass damage, heal, conditions or remove")
    return f, "; ".join(out)


def next_turn(fight: dict[str, Any] | None) -> tuple[dict[str, Any], str]:
    if not fight or not fight["order"]:
        raise Refused("no fight is on")
    f = copy.deepcopy(fight)
    f["turn"] += 1
    if f["turn"] >= len(f["order"]):
        f["turn"], f["round"] = 0, f["round"] + 1
    c = f["order"][f["turn"]]
    return f, f"Round {f['round']}, now: {c['name']}." + ("" if c["pc"] else f" {_creature_text(c)}")


def fight_text(f: dict[str, Any] | None, pc_sheet: dict[str, Any]) -> str:
    if not f:
        return "No fight is on."
    lines = [f"FIGHT, round {f['round']}. In initiative order (→ = whose turn it is"
             + ("; nobody's yet, next_turn starts the first" if f["turn"] < 0 else "") + "):"]
    for i, c in enumerate(f["order"]):
        mark = "→" if i == f["turn"] else " "
        if c["pc"]:
            lines.append(f"{mark} {c['name']} (the PC, initiative {c['initiative']}): HP {pc_sheet['hp']['current']}/"
                         f"{pc_sheet['hp']['max']}, AC {(pc_sheet.get('ac_now') or {}).get('value', pc_sheet['ac'])}")
        else:
            lines.append(f"{mark} {_creature_text(c)}")
    return "\n".join(lines)


def end_fight(fight: dict[str, Any] | None) -> tuple[None, str]:
    if not fight:
        raise Refused("no fight is on")
    return None, f"Fight over after {fight['round']} round(s)."


def order_text(f: dict[str, Any]) -> str:
    return ", ".join(f"{c['name']} ({c['initiative']})" for c in f["order"])


def _creature_text(c: dict[str, Any]) -> str:
    cond = f", {', '.join(c['conditions'])}" if c["conditions"] else ""
    return f"{c['name']} (initiative {c['initiative']}): HP {c['hp']}/{c['max_hp']}, AC {c['ac']}{cond}"


def _find(f: dict[str, Any], name: str) -> dict[str, Any]:
    for c in f["order"]:
        if c["name"] == name.strip():
            return c
    raise Refused(f"no combatant named {name!r}; in the fight: {', '.join(c['name'] for c in f['order'])}")
