"""Creatures' turns run by code (Jake, 2026-10-19). The DM decides what each creature does (which attacks, at whom,
whether it leaves someone's reach) and sends the creatures' turns up to the next party member's in one call; the code
rolls each attack and its damage from the creature's SRD stat block and applies them. It stops wherever the rules give
a party member a reaction, and wherever an attack does more than damage, so the DM (and the player) decide there.
A creature attack used to take 3 or 4 model calls (attack roll | damage roll | record | next turn): 497 of the 1,527
fight calls in the autoloop games were a single roll.
"""

from __future__ import annotations

import copy
import re
from typing import Any

from dm import mechanics as m
from dm import srd

# Reactions a party member can have in the SRD, and what triggers them during a creature's turn. Counterspell is for
# spells, which the DM resolves itself; Feather Fall and Slow Fall are for falls.
REACTIONS = {
    "Opportunity Attack": "a creature it can see leaves its reach",
    "Protection": "a creature it can see attacks someone else within 5 feet of it (it must be wielding a shield)",
    "Cutting Words": "a creature it can see within 60 feet makes an attack roll",
    "Shield": "it is hit by an attack",
    "Uncanny Dodge": "an attacker it can see hits it with an attack",
    "Deflect Missiles": "it is hit by a ranged weapon attack",
    "Hellish Rebuke": "it is damaged by a creature it can see within 60 feet",
}
_RESIST = {"resistant": 0.5, "vulnerable": 2, "immune": 0}
RESIST_KINDS = tuple(_RESIST)


def reactions_of(s: dict[str, Any]) -> set[str]:
    """The reactions on a party member's sheet that it can use now (a slot or a use left)."""
    names = {f.split(":")[0].strip() for f in s.get("features", [])}
    out = {"Opportunity Attack"}
    if any(f.startswith("Fighting Style: Protection") for f in s.get("features", [])):
        out.add("Protection")
    for n in ("Uncanny Dodge", "Deflect Missiles"):
        if n in names:
            out.add(n)
    if "Cutting Words" in names and ((s.get("resources") or {}).get("Bardic Inspiration") or {}).get("left", 0) > 0:
        out.add("Cutting Words")
    spells = {k for k, how in m.sheet_spells(s).items() if how != "ritual"}
    if any(v.get("left", 0) > 0 for v in (s.get("spell_slots") or {}).values()):
        out |= spells & {"Shield", "Hellish Rebuke"}
    return out


def inspiration_die(s: dict[str, Any]) -> int:
    """The bard's Bardic Inspiration die (SRD bard table: d6, d8 at 5th, d10 at 10th, d12 at 15th)."""
    lv = s.get("level", 1)
    return 12 if lv >= 15 else 10 if lv >= 10 else 8 if lv >= 5 else 6


def rider(desc: str) -> str:
    """What an attack does on a hit beyond the damage in its data, as the stat block says it ("" if nothing)."""
    hit = desc.split("Hit:", 1)[1] if "Hit:" in desc else ""
    t = re.sub(r"\d+ \([^)]*\)( \w+)? damage", "", hit)
    t = re.sub(r",? or [^.]*?(two hands|two-handed|at range)[^.]*\.?", "", t)
    t = re.sub(r"\b(plus|and|damage|in melee)\b", "", t)
    return hit.strip() if re.search(r"[A-Za-z]{3,}", t) else ""


def damage_dice(d: dict[str, Any]) -> str:
    """One damage entry's dice. A versatile weapon is used one-handed unless the DM passes damage, as its stat block
    gives first; any other choice (lightning or thunder) is the DM's: "" here."""
    if d.get("damage_dice"):
        return d["damage_dice"]
    opts = (d.get("from") or {}).get("options", [])
    return next((o["damage_dice"] for o in opts if str(o.get("notes", "")).casefold() == "one handed"), "")


def crit_dice(expr: str) -> str:
    """Every die in a damage expression rolled twice: 2d4+2 -> 4d4+2."""
    return re.sub(r"(\d*)d(\d+)", lambda x: f"{2 * int(x.group(1) or 1)}d{x.group(2)}", expr)


class _Low:
    """Dice that always show 1: for checking that an expression can be read."""

    def randint(self, a: int, b: int) -> int:
        return a


class Stop(Exception):
    """The turn stops here: a reaction is possible, or something needs the DM. The message says what to do."""


class Turns:
    """One creature_turns call on a Game (dm/play.py)."""

    def __init__(self, game: Any, a: dict[str, Any]) -> None:
        self.g, self.a, self.lines = game, a, []
        self.p: dict[str, Any] | None = None  # the turn being played; kept in the tracker if it stops
        self.queue: list[dict[str, Any]] = []  # the turns sent after it, played on after a stop
        self.down: list[str] = []  # party members already at 0 HP when the turns were sent

    # ---- the party ----
    def party(self) -> dict[str, dict[str, Any]]:
        return {s["name"]: s for s in [self.g.sheet, *self.g.companions]}

    def member(self, name: str) -> dict[str, Any] | None:
        return self.party().get(name)

    def entry(self, name: str) -> dict[str, Any]:
        return m._find(self.g.fight, name)

    def name_of(self, name: Any) -> str:
        """A combatant's name as the tracker has it: 'pc' is the PC, and a party member's first name is theirs."""
        key = str(name or "").strip()
        if key.casefold() == "pc":
            return self.g.sheet["name"]
        return next((w for w in self.party() if key.casefold() in (w.casefold(), w.split()[0].casefold())), key)

    def can(self, who: str, reaction: str) -> bool:
        """`who`, a party member in the fight, can take `reaction` now."""
        s = self.member(who)
        if not s or reaction not in reactions_of(s):
            return False
        try:
            e = self.entry(who)
        except m.Refused:
            return False
        if "reaction" in e.get("used", []) or s["hp"]["current"] <= 0:
            return False
        return not set(s.get("conditions", [])) & (m.incapacitating() | {"dead", "unconscious"})

    def ask(self, who: str, reaction: str, what: str, how: str) -> None:
        pc = who == self.g.sheet["name"]
        raise Stop(f"STOPPED for a reaction: {what} {who} can use {reaction} ({REACTIONS[reaction]}). "
                   + (f"Ask the player whether {who.split()[0]} uses it, and end your reply there; nothing after this "
                      "has happened yet. " if pc else f"Decide as {who.split()[0]} whether they use it. ")
                   + f"If used: record it ({how}; uses reaction, by {who}). Then call creature_turns with resume: the "
                   "turns you sent go on from here, and it stops again if one of them can no longer happen as sent.")

    # ---- the creatures ----
    def stat_block(self, c: dict[str, Any]) -> dict[str, Any]:
        if not c.get("monster"):
            raise m.Refused(f"{c['name']} has no SRD stat block in the tracker: give its monster with add_combatants "
                            "(e.g. {name: 'Goblin 1', monster: 'Goblin', ...}), or resolve its turn with roll and the "
                            "other tools")
        return srd.find("Monsters", c["monster"])

    def attack_of(self, c: dict[str, Any], name: str) -> dict[str, Any]:
        block = self.stat_block(c)
        acts = [x for x in block.get("actions", []) if "attack_bonus" in x and "Attack" in x.get("desc", "")]
        for x in acts:
            if x["name"].casefold() == str(name).strip().casefold():
                return x
        raise m.Refused(f"{c['name']} ({block['name']}) has no attack {name!r}; its attacks: "
                        + (", ".join(x["name"] for x in acts) or "none"))

    def check(self, t: dict[str, Any]) -> None:
        """A turn as sent, before anything is rolled: refused whole if any part is impossible."""
        c = self.entry(t.get("name", ""))
        if c["pc"] or c.get("companion"):
            raise m.Refused(f"{c['name']} is in the party: creature_turns is for creatures; on a party member's turn, "
                            "stop and play it (or ask the player)")
        if c["hp"] <= 0:
            raise m.Refused(f"{c['name']} is at 0 HP: it has no turn (remove it with change_creature if it's out)")
        attacks = t.get("attacks") or []
        if len(attacks) > 1 and not any(x["name"] == "Multiattack" for x in self.stat_block(c).get("actions", [])):
            raise m.Refused(f"{c['name']} has no Multiattack: one attack with its action")
        t["leaves_reach_of"] = [self.name_of(w) for w in t.get("leaves_reach_of") or []]
        for x in attacks:
            atk = self.attack_of(c, x.get("attack", ""))
            x["target"] = self.name_of(x.get("target"))
            self.entry(x["target"])
            if x.get("mode", "normal") not in ("normal", "advantage", "disadvantage"):
                raise m.Refused("mode: normal, advantage or disadvantage")
            if x.get("target_resists") and x["target_resists"] not in _RESIST:
                raise m.Refused("target_resists: resistant, vulnerable or immune")
            if not x.get("damage") and not all(damage_dice(d) for d in atk.get("damage", [])):
                opts = [f"{o['damage_dice']}" + (f" ({o['notes']})" if o.get("notes") else f" {o['damage_type']['name']}")
                        for d in atk["damage"] if "from" in d for o in d["from"].get("options", []) if o.get("damage_dice")]
                fixed = [d["damage_dice"] for d in atk["damage"] if d.get("damage_dice")]
                raise m.Refused(f"{c['name']}'s {atk['name']} has a choice of damage: pass damage, all its dice in one "
                                f"expression ({' + '.join(fixed) + ' plus ' if fixed else ''}one of: {', '.join(opts)}; "
                                "e.g. 1d10+3)")
            if x.get("damage"):
                m.roll(x["damage"], rng=_Low())  # readable (no real dice spent)
        for w in t.get("leaves_reach_of") or []:
            self.entry(w)

    def run(self) -> str:
        f = self.g.fight
        if not f:
            raise m.Refused("no fight is on")
        turns = self.a.get("turns") or []
        pend = f.get("pending")
        if pend and "resume" not in self.a:
            raise m.Refused(f"{pend['name']}'s turn is stopped ({pend['why']}): call creature_turns with resume "
                            "({} if nothing changes)")
        if not pend and "resume" in self.a:
            raise m.Refused("nothing is stopped: leave out resume")
        if not pend and not turns:
            raise m.Refused("turns: the creatures' turns, in initiative order from the next one")
        # each turn must be the next combatant's: no party member's turn comes between them. With resume, turns
        # replace the ones still to come.
        order, i = f["order"], f["turn"]
        started = bool(turns) and not pend and i >= 0 and order[i]["name"] == turns[0].get("name") \
            and not order[i].get("used")  # its turn was started with next_turn
        for k, t in enumerate(turns):
            self.check(t)
            if k == 0 and started:
                continue
            i = (i + 1) % len(order)
            if order[i]["name"] != t["name"]:
                raise m.Refused(f"{order[i]['name']}'s turn comes next, not {t['name']}'s: send the creatures' turns in "
                                "initiative order, up to the next party member's")
        before = copy.deepcopy((self.g.sheet, self.g.companions, self.g.fight, self.g.clock))
        try:
            if pend:
                self.p = self.g.fight.pop("pending")
                self.queue, self.down = turns or self.p.pop("queue", []), self.p.pop("down", [])
                if turns:
                    self.down = [w for w, s in self.party().items() if s["hp"]["current"] <= 0]
                if self.p.get("turn"):
                    self.go(self.a.get("resume") or {})
            else:
                self.queue = list(turns)
                self.down = [w for w, s in self.party().items() if s["hp"]["current"] <= 0]
            k = 0
            while self.queue:
                t = self.queue[0]
                self.p = {"name": t["name"], "turn": None, "why": ""}
                if (why := self.changed(t)):
                    self.p["why"] = why
                    raise Stop(f"STOPPED before {t['name']}'s turn: {why}, so its turn can't go as you sent it. Decide "
                               "it again from the tracker as it is now, and call creature_turns with resume and the "
                               "creatures' turns from this one.")
                self.queue.pop(0)
                if not (k == 0 and started):
                    self.log("fight: " + self.g.advance_turn())
                k += 1
                self.p = {"name": t["name"], "turn": t, "attack": 0, "stage": "start", "why": "", "left": []}
                self.go({})
            self.p = None
            # The party member's turn is started by the DM's next_turn, as ever: when the code started it, the DM
            # called next_turn again and skipped a companion's turn (a replay, 2026-10-19).
            if self.g.fight:
                nxt = self.g.fight["order"][(self.g.fight["turn"] + 1) % len(self.g.fight["order"])]
                if nxt["pc"] or nxt.get("companion"):
                    self.lines.append(f"Next is {nxt['name']}'s turn: start it with next_turn.")
        except Stop as e:
            self.g.fight["pending"] = self.p | {"queue": self.queue, "down": self.down}
            self.lines.append(str(e))
        except (m.Refused, srd.Bad):
            self.g.sheet, self.g.companions, self.g.fight, self.g.clock = before
            raise
        return "\n".join(self.lines)

    def changed(self, t: dict[str, Any], attack: dict[str, Any] | None = None) -> str:
        """Why turn t (or one attack of it) can no longer happen as it was sent, or "": its creature is out, down or
        incapacitated, it isn't next, or a target is out of the fight or has dropped since."""
        order = self.g.fight["order"]
        c = next((x for x in order if x["name"] == t["name"]), None)
        if not c:
            return f"{t['name']} is no longer in the fight"
        if attack is None:
            nxt = order[(self.g.fight["turn"] + 1) % len(order)]
            if nxt["name"] != c["name"]:
                return f"{nxt['name']}'s turn comes next now"
        if c["hp"] <= 0:
            return f"{c['name']} is at 0 HP"
        if (cond := set(c.get("conditions", [])) & m.incapacitating()):
            return f"{c['name']} is {', '.join(sorted(cond))}"
        for x in [attack] if attack else t.get("attacks") or []:
            target = x["target"].strip()
            e = next((y for y in order if y["name"] == target), None)
            s = self.member(target)
            if not e:
                return f"{target} is no longer in the fight"
            if (s and s["hp"]["current"] <= 0 and target not in self.down) or (not s and e["hp"] <= 0):
                return f"{target} has dropped to 0 HP"
            if s and "dead" in s.get("conditions", []):
                return f"{target} is dead"
        return ""

    def go(self, resume: dict[str, Any]) -> None:
        """Play the turn in self.p from where it stopped: its move out of reach, then each attack."""
        p, t = self.p, self.p["turn"]
        if not any(x["name"] == t["name"] for x in self.g.fight["order"]):
            return  # taken out of the fight while it was stopped (an opportunity attack, say)
        c = self.entry(t["name"])
        attacks = t.get("attacks") or []
        if resume.get("skip_rest"):
            p["attack"], resume = len(attacks), {}
        if p["stage"] in ("start", "leave") and not t.get("after_attacks"):
            self.leave(t)
            p["stage"] = "start"
        while p["attack"] < len(attacks):
            if p["stage"] == "start" and (why := self.changed(t, attacks[p["attack"]])):
                p["why"] = why
                raise Stop(f"STOPPED in {c['name']}'s turn: {why}, so its {attacks[p['attack']]['attack']} at "
                           f"{attacks[p['attack']]['target']} can't go as you sent it. If it still acts, resolve the "
                           "rest of its turn with the other tools; then call creature_turns with resume {skip_rest: "
                           "true} (the turns after it go on as sent).")
            self.attack(c, attacks[p["attack"]], resume)
            resume = {}
            p.update(attack=p["attack"] + 1, stage="start", roll=None)
            if not any(x["name"] == c["name"] for x in self.g.fight["order"]):
                return  # it's out of the fight
        if attacks and "action" not in self.entry(c["name"]).get("used", []):
            self.g.fight, _ = m.use(self.g.fight, "action", c["name"])
        if t.get("after_attacks"):
            p["stage"] = "leave"
            self.leave(t)
        if t.get("note"):
            self.g.transcript.append({"kind": "call", "tool": "creature_turns", "input": {"name": t["name"], "note": t["note"]},
                                      "result": "", "error": False})

    def leave(self, t: dict[str, Any]) -> None:
        """Opportunity attacks as the creature leaves party members' reach."""
        p = self.p
        for w in t.get("leaves_reach_of") or []:
            if w in p["left"]:
                continue
            p["left"].append(w)
            if self.member(w) and self.can(w, "Opportunity Attack"):
                p["why"] = f"{t['name']} leaving {w}'s reach"
                self.ask(w, "Opportunity Attack", f"{t['name']} leaves {w}'s reach.",
                         "roll the attack and its damage, and change_creature")

    def attack(self, c: dict[str, Any], x: dict[str, Any], resume: dict[str, Any]) -> None:
        """One attack, from the stage it stopped at: start, roll (after Protection), rolled (after Cutting Words), hit
        (after Shield and the like), then after the damage: rebuke, rider, down."""
        p = self.p
        atk = self.attack_of(c, x["attack"])
        target = x["target"].strip()
        tm = self.member(target)
        ranged = bool(x.get("ranged")) or atk["desc"].startswith("Ranged")
        label = f"{c['name']}'s {atk['name']} at {target}"
        if p["stage"] == "start":
            p["stage"] = "roll"
            if tm:
                for w in self.party():
                    if w != target and self.can(w, "Protection"):
                        p["why"] = f"{label}, before the roll"
                        self.ask(w, "Protection", f"{c['name']} is about to attack {target} with its {atk['name']}.",
                                 "it imposes disadvantage: pass resume {mode: 'disadvantage'}")
        if p["stage"] == "roll":
            r = m.roll(f"1d20{atk['attack_bonus']:+d}", resume.get("mode") or x.get("mode") or "normal")
            p.update(stage="rolled", roll={"total": r["total"], "natural": r["natural"]})
            self.log("dice " + m.roll_text(r, f"{label} (AC {self.ac(target)})"))
            resume = {}
            if (w := self.cutting(target)):
                p["why"] = f"{label}, after the attack roll"
                self.ask(w, "Cutting Words", f"{c['name']}'s attack roll against {target} is {r['total']}, a hit "
                         f"against AC {self.ac(target)}.", "change_pc spending a Bardic Inspiration use; roll the die, "
                         "and pass resume {roll_change: minus the roll}")
        roll = p["roll"]
        if p["stage"] == "rolled":
            if resume.get("roll_change"):
                roll["total"] += int(resume["roll_change"])
                self.log(f"fight: {label}: the attack roll is now {roll['total']}")
            resume = {}
        crit = roll["natural"] == 20
        hit = crit or (roll["natural"] != 1 and roll["total"] >= self.ac(target))
        if p["stage"] == "rolled":
            if not hit:
                self.log(f"fight: {label}: a miss")
                return
            p["stage"] = "hit"
            ask = {"Shield": (not crit and roll["total"] < self.ac(target) + 5,
                              "change_pc cast Shield, with ac_set to the new AC"),
                   "Uncanny Dodge": (True, "pass resume {halve_damage: true}"),
                   "Deflect Missiles": (ranged, "roll 1d10 + DEX modifier + monk level, and pass resume "
                                                "{damage_reduction: the total}")}
            for reaction, (could, how) in ask.items():
                if tm and could and self.can(target, reaction):
                    p["why"] = f"{label}, a hit"
                    self.ask(target, reaction, f"{c['name']}'s {atk['name']} hits {target}: {roll['total']} against AC "
                             f"{self.ac(target)}{', a critical hit' if crit else ''}.", how)
        if p["stage"] == "hit":
            if not hit:
                self.log(f"fight: {label}: now a miss against AC {self.ac(target)}")
                return
            self.damage(c, atk, x, target, crit, ranged, label, resume)
            resume = {}
        if p["stage"] == "rebuke":
            p["stage"] = "rider"
            if tm and p.get("dealt") and self.can(target, "Hellish Rebuke"):
                p["why"] = f"{label}, after the damage"
                self.ask(target, "Hellish Rebuke", f"{target} took {p['dealt']} damage from {c['name']}.",
                         "change_pc cast Hellish Rebuke, roll its save and damage, and change_creature")
        if p["stage"] == "rider":
            p["stage"] = "down"
            if (more := rider(atk["desc"])):
                p["why"] = f"{label}: what its hit does beyond the damage"
                raise Stop(f"STOPPED: {c['name']}'s {atk['name']} hit {target}, and on a hit its stat block says: "
                           f"\"{more}\" Only the damage was applied. Resolve the rest by the rules (roll any save with "
                           "roll), then call creature_turns with resume, and the turns after it.")
        if p["stage"] == "down":
            p["stage"] = "done"
            note = p.get("note") or ""
            # A party member who drops stops the turns only if one sent still aims at them (changed())
            if tm and "concentrating on" in note:
                p["why"] = f"{target} must save for concentration"
                raise Stop(f"STOPPED: {target}: {note} Roll the concentration save (and end it on a failure), then "
                           "call creature_turns with resume: the turns you sent go on from here.")

    def damage(self, c: dict[str, Any], atk: dict[str, Any], x: dict[str, Any], target: str, crit: bool, ranged: bool,
               label: str, resume: dict[str, Any]) -> None:
        p, tm = self.p, self.member(target)
        down = set(tm.get("conditions", []) if tm else self.entry(target).get("conditions", []))
        if not ranged and not x.get("beyond_5ft") and down & {"paralyzed", "unconscious"}:
            crit = True  # SRD: a hit on a paralyzed or unconscious creature from within 5 feet is a critical hit
        total = 0
        for d in [x["damage"]] if x.get("damage") else [damage_dice(d) for d in atk.get("damage", [])]:
            r = m.roll(crit_dice(d) if crit else d)
            total += r["total"]
            self.log("dice " + m.roll_text(r, f"{label}: damage" + (" (critical hit)" if crit else "")))
        total = int(total * _RESIST.get(x.get("target_resists") or "", 1))
        if resume.get("halve_damage"):
            total //= 2
        total = max(0, total - int(resume.get("damage_reduction") or 0))
        if tm:
            text = self.g.change_party_member({"damage": total} | ({"critical_hit": True} if crit else {})
                                              | ({"who": target} if tm is not self.g.sheet else {}))
            self.log(f"sheet: {text}")
        else:
            self.g.fight, text = m.change_creature(self.g.fight, {"name": target, "damage": total})
            self.log(f"fight: {text}")
        p.update(stage="rebuke", dealt=total, note=text)

    def cutting(self, target: str) -> str | None:
        """A bard whose Cutting Words could turn this hit into a miss."""
        roll = self.p["roll"]
        for w, s in self.party().items():
            if not self.can(w, "Cutting Words"):
                continue
            ac = self.ac(target)
            hits = roll["natural"] != 1 and roll["natural"] != 20 and roll["total"] >= ac
            if hits and roll["total"] - inspiration_die(s) < ac:
                return w
        return None

    def ac(self, name: str) -> int:
        s = self.member(name)
        if s:
            return int((s.get("ac_now") or {}).get("value") or s["ac"])
        return self.entry(name)["ac"]

    def log(self, text: str) -> None:
        self.g.log("tool", text)
        self.lines.append(text)
