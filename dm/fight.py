"""Creatures' and companions' turns run by code (Jake, 2026-10-19). The DM decides what each one does (which attacks,
at whom, whether it leaves someone's reach) and sends the turns up to the PC's in one call; the code rolls each attack
and its damage, from the creature's SRD stat block or the companion's sheet, applies resistances, and applies the
damage. The call also says which reactions the creatures and companions take, and the code takes them when they're
triggered (Jake: the call already decides everything but the player's choices). It stops for the player's reactions,
and where an attack does more than damage, so the DM (and the player) decide there.
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
RESIST_KINDS = ("resistant", "vulnerable", "immune", "normal")
DAMAGE_TYPES = ("acid", "bludgeoning", "cold", "fire", "force", "lightning", "necrotic", "piercing", "poison", "psychic",
                "radiant", "slashing", "thunder")
_WEAPON_TYPES = ("bludgeoning", "piercing", "slashing")
_DICE = r"\d+d\d+(?:[+-]\d+)?|\d+(?:[+-]\d+)?"


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


def crit_dice(expr: str) -> str:
    """Every die in a damage expression rolled twice: 2d4+2 -> 4d4+2."""
    return re.sub(r"(\d*)d(\d+)", lambda x: f"{2 * int(x.group(1) or 1)}d{x.group(2)}", expr)


def _types_in(text: str) -> list[str]:
    return [t for t in DAMAGE_TYPES if re.search(rf"\b{t}\b", text, re.I)]


def creature_resists(block: dict[str, Any], weapon: bool) -> tuple[dict[str, set[str]], list[str]]:
    """A stat block's damage resistances, immunities and vulnerabilities against this attack: {type: kinds}, and the
    ones that depend on something the code can't see (a magic weapon of a good creature), for the DM."""
    out: dict[str, set[str]] = {}
    unsure: list[str] = []
    for key, kind in (("damage_resistances", "resistant"), ("damage_immunities", "immune"),
                      ("damage_vulnerabilities", "vulnerable")):
        for s in block.get(key) or []:
            if re.search(r"\bfrom\b|aren't|\bspells\b", s):
                # "from nonmagical weapons (that aren't silvered)": a creature's or a companion's weapon attack is
                # taken as nonmagical; the DM overrides with target_resists for a magic or silvered weapon
                if not ("nonmagical" in s and weapon):
                    if "nonmagical" not in s:
                        unsure.append(f"{kind}: {s}")
                    continue
            for t in _types_in(s):
                out.setdefault(t, set()).add(kind)
    return out, unsure


def raging(s: dict[str, Any], clock: dict[str, Any]) -> bool:
    """A barbarian whose Rage timer is running (started when a Rage use is spent, or one the DM named for their rage,
    'Rage (Korvash)' in a replay), and who is conscious."""
    first = s["name"].split()[0].casefold()
    if s["hp"]["current"] <= 0 or not any(f.startswith("Rage:") for f in s.get("features", [])):
        return False
    if "raging" in {c.casefold() for c in s.get("conditions", [])}:
        return True  # the condition the barbarian2 game's DM added each time it spent Rage
    if clock.get("now") is None:
        return False
    return any(end > clock["now"] for n, end in (clock.get("timers") or {}).items()
               if re.search(r"\brage\b", n, re.I) and first in n.casefold())


# Features whose use lasts a set time (SRD): spending the use (change_pc use_resource) starts its timer, as casting a
# spell does, so the timer is never missed or misnamed (Jake, 2026-10-19: a replay's DM added "Rage (Korvash)" by hand
# and never spent the use).
FEATURE_TIMERS = {"Rage": lambda s: 60, "Wild Shape": lambda s: max(1, s.get("level", 1) // 2) * 3600}


def feature_timer(s: dict[str, Any], resource: str) -> tuple[str, int] | None:
    """The timer a feature's use starts: (name, seconds), or None."""
    f = FEATURE_TIMERS.get(resource)
    return (f"{s['name'].split()[0]}'s {resource}", f(s)) if f else None


def rage_damage(s: dict[str, Any]) -> int:
    """SRD barbarian table: rage damage +2, +3 at 9th level, +4 at 16th."""
    lv = s.get("level", 1)
    return 4 if lv >= 16 else 3 if lv >= 9 else 2


def member_resists(s: dict[str, Any], clock: dict[str, Any]) -> dict[str, dict[str, str]]:
    """A party member's damage resistances and immunities now: {type: {kind: where from}}. From the features on the
    sheet that name a damage type (Hellish Resistance, Dwarven Resilience, a dragonborn's ancestry), Rage while its
    timer runs, and petrified. A resistance from a spell or an item is the DM's to pass."""
    out: dict[str, dict[str, str]] = {}
    for f in s.get("features", []):
        name = f.split(":")[0].strip()
        if name == "Rage":
            continue
        for x in re.finditer(r"\b(resistan\w*|immun\w*) (?:to|against) ([^.;:]*?) damage\b(?! type)", f, re.I):
            for t in _types_in(x[2]):
                out.setdefault(t, {})["immune" if x[1].lower().startswith("immun") else "resistant"] = name
        if re.search(r"resistance to (?:that|this) damage type", f, re.I):
            for t in _types_in(f):
                out.setdefault(t, {})["resistant"] = name
    if raging(s, clock):
        for t in _WEAPON_TYPES:
            out.setdefault(t, {})["resistant"] = "Rage"
    if "petrified" in s.get("conditions", []):
        for t in DAMAGE_TYPES:
            out.setdefault(t, {})["resistant"] = "petrified"
    return out


def resisted(v: int, kinds: set[str]) -> int:
    """SRD Damage Resistance and Vulnerability: immunity none, resistance halved (rounded down), then vulnerability
    doubled; more than one instance counts once."""
    if "immune" in kinds:
        return 0
    if "resistant" in kinds:
        v //= 2
    return v * 2 if "vulnerable" in kinds else v


def sheet_attack(s: dict[str, Any], name: str) -> dict[str, Any]:
    """An attack from a party member's sheet line, such as 'Longsword: +5 to hit, 1d8+3 slashing; 1d10+3 two-handed
    (versatile)' or 'Fire Bolt (cantrip): +5 spell attack, 1d10 fire, range 120 feet'."""
    lines = s.get("attacks", [])
    key = str(name).strip().casefold()
    for line in lines:
        head, _, rest = line.partition(":")
        if key not in (head.strip().casefold(), head.split("(")[0].strip().casefold()):
            continue
        bonus = re.search(r"([+-]\d+) (to hit|spell attack)", rest)
        if not bonus:
            raise m.Refused(f"{s['name']}'s {head.strip()} makes no attack roll ({rest.strip()}): resolve it on their "
                            "turn with next_turn and roll")
        d = re.search(rf"(?:to hit|spell attack), ({_DICE}) (\w+)", rest)
        two = re.search(rf"; ({_DICE}) two-handed \(versatile\)", rest)
        spell = bonus[2] == "spell attack"
        typ = d[2].lower() if d and d[2].lower() in DAMAGE_TYPES else None
        return {"name": head.strip(), "bonus": int(bonus[1]), "dmg": [(d[1], typ)] if d and typ else [],
                "types": {typ} if typ else set(), "two_handed": two[1] if two else None,
                "ranged": bool(re.search(r"\brange\b", rest)) and "thrown" not in rest and "touch" not in rest,
                "weapon": not spell, "spell": spell, "rider": "", "line": line}
    raise m.Refused(f"{s['name']} has no attack {name!r} on their sheet; their attacks: "
                    + (", ".join(x.split(":")[0] for x in lines) or "none"))


def block_attack(block: dict[str, Any], who: str, name: str) -> dict[str, Any]:
    """An attack from a stat block. A versatile weapon is used one-handed unless the DM passes damage, as its stat
    block gives first; any other choice (lightning or thunder) is the DM's."""
    acts = [x for x in block.get("actions", []) if "attack_bonus" in x and "Attack" in x.get("desc", "")]
    atk = next((x for x in acts if x["name"].casefold() == str(name).strip().casefold()), None)
    if not atk:
        raise m.Refused(f"{who} ({block['name']}) has no attack {name!r}; its attacks: "
                        + (", ".join(x["name"] for x in acts) or "none"))
    dmg, choice, types = [], [], set()
    for d in atk.get("damage", []):
        if d.get("damage_dice"):
            t = ((d.get("damage_type") or {}).get("name") or "").lower() or None
            dmg.append((d["damage_dice"], t))
            types.add(t)
            continue
        opts = [o for o in (d.get("from") or {}).get("options", []) if o.get("damage_dice")]
        types |= {((o.get("damage_type") or {}).get("name") or "").lower() or None for o in opts}
        one = next((o for o in opts if str(o.get("notes", "")).casefold() == "one handed"), None)
        if one:
            dmg.append((one["damage_dice"], ((one.get("damage_type") or {}).get("name") or "").lower() or None))
        else:
            choice += [o["damage_dice"] + (f" ({o['notes']})" if o.get("notes") else
                                           f" {(o.get('damage_type') or {}).get('name', '')}") for o in opts]
    return {"name": atk["name"], "bonus": atk["attack_bonus"], "dmg": dmg, "choice": choice, "types": types,
            "ranged": atk["desc"].startswith("Ranged"), "weapon": "Weapon Attack" in atk["desc"],
            "spell": "Spell Attack" in atk["desc"], "rider": rider(atk["desc"]),
            "fixed": [x for x, _ in dmg]}


def extra_attacks(s: dict[str, Any]) -> int:
    """Attacks with the Attack action beyond the first: Extra Attack, or Extra Attack (2) and (3) for a fighter."""
    n = 0
    for f in s.get("features", []):
        if (x := re.match(r"Extra Attack(?: \((\d)\))?", f)):
            n = max(n, int(x[1] or 1))
    return n


class _Low:
    """Dice that always show 1: for checking that an expression can be read."""

    def randint(self, a: int, b: int) -> int:
        return a


class Stop(Exception):
    """The turns stop here: the player can take a reaction, or something needs the DM. The message says what to do."""


# The reactions a companion can take during these turns, written by the DM on the attack that triggers them (Jake,
# 2026-10-19: the call already decides what everyone but the player does, attack by attack, so it decides their
# reactions there too, with a condition only where it hangs on a roll the DM can't see yet). Hellish Rebuke (a save
# and damage of its own) isn't among them. An opportunity attack is written on the move (leaves_reach_of).
TAKE = ("Shield", "Uncanny Dodge", "Deflect Missiles", "Protection", "Cutting Words")
_OWN = ("Shield", "Uncanny Dodge", "Deflect Missiles")  # taken by the one attacked
_AFTER_DAMAGE = ("Uncanny Dodge", "Deflect Missiles")  # may wait for the damage: min_damage


def save_bonus(s: dict[str, Any], ability: str) -> int:
    """A saving throw bonus from the sheet's line 'STR -1, DEX +1, CON +2, ...'."""
    x = re.search(rf"\b{ability} ([+-]\d+)", str(s.get("saving_throws", "")))
    return int(x[1]) if x else 0


def _mode(*modes: str | None) -> str:
    """Advantage and disadvantage together cancel (SRD)."""
    got = {x for x in modes if x and x != "normal"}
    return "normal" if len(got) != 1 else got.pop()


class Turns:
    """One creature_turns call on a Game (dm/play.py)."""

    def __init__(self, game: Any, a: dict[str, Any]) -> None:
        self.g, self.a, self.lines = game, a, []
        self.p: dict[str, Any] | None = None  # the turn being played; kept in the tracker if it stops
        self.queue: list[dict[str, Any]] = []  # the turns sent after it, played on after a stop
        self.down: list[str] = []  # party members already at 0 HP when the turns were sent

    # ---- who's who ----
    def party(self) -> dict[str, dict[str, Any]]:
        return {s["name"]: s for s in [self.g.sheet, *self.g.companions]}

    def member(self, name: str) -> dict[str, Any] | None:
        return self.party().get(name)

    def entry(self, name: str) -> dict[str, Any]:
        return m._find(self.g.fight, name)

    def in_fight(self, name: str) -> bool:
        return any(x["name"] == name for x in self.g.fight["order"])

    def hp(self, name: str) -> int:
        s = self.member(name)
        return s["hp"]["current"] if s else self.entry(name)["hp"]

    def conditions(self, name: str) -> set[str]:
        s = self.member(name)
        return set((s if s else self.entry(name)).get("conditions", []))

    def pc(self) -> str:
        return self.g.sheet["name"]

    def name_of(self, name: Any) -> str:
        """A combatant's name as the tracker has it: 'pc' is the PC, and a party member's first name is theirs."""
        key = str(name or "").strip()
        if key.casefold() == "pc":
            return self.pc()
        return next((w for w in self.party() if key.casefold() in (w.casefold(), w.split()[0].casefold())), key)

    def can(self, who: str, reaction: str) -> bool:
        """`who`, a party member in the fight, can take `reaction` now."""
        s = self.member(who)
        if not s or reaction not in reactions_of(s):
            return False
        return self.can_react(who)

    def can_react(self, who: str) -> bool:
        """`who` is in the fight, has its reaction, is above 0 HP and isn't incapacitated."""
        if not self.in_fight(who):
            return False
        if "reaction" in self.entry(who).get("used", []) or self.hp(who) <= 0:
            return False
        return not self.conditions(who) & (m.incapacitating() | {"dead", "unconscious"})

    def declared(self, x: dict[str, Any], who: str, reaction: str) -> dict[str, Any] | None:
        """The reaction the call wrote on attack x for companion `who`, if they can take it now."""
        r = next((r for r in x.get("reactions") or [] if r["by"] == who and r["reaction"] == reaction), None)
        return r if r and who != self.pc() and self.can(who, reaction) else None

    def used_reaction(self, who: str) -> None:
        self.g.fight, _ = m.use(self.g.fight, "reaction", who)

    def ask(self, who: str, reaction: str, what: str, how: str) -> None:
        """The player's reaction: stop and ask."""
        raise Stop(f"STOPPED for a reaction: {what} {who} can use {reaction} ({REACTIONS[reaction]}). Ask the player "
                   f"whether {who.split()[0]} uses it, and end your reply there; nothing after this has happened yet. "
                   f"If used: record it ({how}; uses reaction, by {who}). Then call creature_turns with resume: the "
                   "turns you sent go on from here.")

    # ---- attacks ----
    def stat_block(self, c: dict[str, Any]) -> dict[str, Any]:
        if not c.get("monster"):
            raise m.Refused(f"{c['name']} has no SRD stat block in the tracker: give its monster with add_combatants "
                            "(e.g. {name: 'Goblin 1', monster: 'Goblin', ...}), or resolve its turn with roll and the "
                            "other tools")
        return srd.find("Monsters", c["monster"])

    def weapon(self, c: dict[str, Any], name: str) -> dict[str, Any]:
        """Attacker c's attack `name`: from its sheet (a companion) or its stat block (a creature)."""
        s = self.member(c["name"])
        return sheet_attack(s, name) if s else block_attack(self.stat_block(c), c["name"], name)

    def check_reactions(self, x: dict[str, Any]) -> None:
        """The companions' reactions written on attack x: who, which, and min_damage where it waits for the damage."""
        out = []
        for r in x.get("reactions") or []:
            by, what = self.name_of(r.get("by")), r.get("reaction")
            if by == self.pc():
                raise m.Refused("reactions: the PC's are the player's: leave them out (the turns stop to ask)")
            if not self.member(by):
                raise m.Refused(f"reactions: {by} isn't a companion (a creature's Parry the code takes itself)")
            if what not in TAKE:
                raise m.Refused(f"reactions: reaction is one of {', '.join(TAKE)}")
            if what in _OWN and by != x["target"]:
                raise m.Refused(f"reactions: {what} is taken by the one attacked ({x['target']}), not {by}")
            if what == "Protection" and by == x["target"]:
                raise m.Refused("reactions: Protection is for someone else being attacked")
            md = r.get("min_damage")
            if md is not None and (what not in _AFTER_DAMAGE or not isinstance(md, int) or md < 1):
                raise m.Refused("reactions: min_damage (a whole number) is only for " + " and ".join(_AFTER_DAMAGE))
            out.append({"by": by, "reaction": what} | ({"min_damage": md} if md else {}))
        x["reactions"] = out

    def check_leaves(self, t: dict[str, Any]) -> None:
        """leaves_reach_of: a name, or {name, opportunity_attack} for one who makes an opportunity attack."""
        out = []
        for w in t.get("leaves_reach_of") or []:
            name, oa = (self.name_of(w.get("name")), w.get("opportunity_attack")) if isinstance(w, dict) else \
                (self.name_of(w), None)
            e = self.entry(name)
            if oa and e["pc"]:
                raise m.Refused("leaves_reach_of: the PC's opportunity attack is the player's: leave out "
                                "opportunity_attack (the turns stop to ask)")
            out.append({"name": name, "opportunity_attack": self.weapon(e, oa)["name"] if oa else None})
        t["leaves_reach_of"] = out

    def check(self, t: dict[str, Any]) -> None:
        """A turn as sent, before anything is rolled: refused whole if any part is impossible."""
        c = self.entry(self.name_of(t.get("name", "")))
        t["name"] = c["name"]
        s = self.member(c["name"])
        attacks = t.get("attacks") or []
        if c["pc"]:
            raise m.Refused(f"{c['name']} is the PC: on the PC's turn, stop and ask the player what they do")
        if s:
            if s["hp"]["current"] <= 0:
                raise m.Refused(f"{c['name']} is at 0 HP: their turn is a death save; start it with next_turn and roll it")
            if (cond := set(s.get("conditions", [])) & m.incapacitating()):
                raise m.Refused(f"{c['name']} is {', '.join(sorted(cond))}: start their turn with next_turn")
            action = [x for x in attacks if not x.get("bonus_action")]
            most = 1 + extra_attacks(s)
            if len(action) > most:
                raise m.Refused(f"{c['name']} makes {most} attack{'s' if most > 1 else ''} with the Attack action")
        elif c["hp"] <= 0:
            raise m.Refused(f"{c['name']} is at 0 HP: it has no turn (remove it with change_creature if it's out)")
        elif len(attacks) > 1 and not any(x["name"] == "Multiattack" for x in self.stat_block(c).get("actions", [])):
            raise m.Refused(f"{c['name']} has no Multiattack: one attack with its action")
        self.check_leaves(t)
        for x in attacks:
            w = self.weapon(c, x.get("attack", ""))
            if s and w["spell"] and len(attacks) > 1:
                raise m.Refused(f"{c['name']}'s {w['name']} is a spell, cast with their action: no other attacks with it")
            x["target"] = self.name_of(x.get("target"))
            x["or_targets"] = [self.name_of(v) for v in x.get("or_targets") or []]
            for v in [x["target"], *x["or_targets"]]:
                self.entry(v)
            self.check_reactions(x)
            if x.get("mode", "normal") not in ("normal", "advantage", "disadvantage"):
                raise m.Refused("mode: normal, advantage or disadvantage")
            if x.get("target_resists") and x["target_resists"] not in RESIST_KINDS:
                raise m.Refused("target_resists: " + ", ".join(RESIST_KINDS))
            if not x.get("damage") and (w.get("choice") or not w["dmg"]):
                if s:
                    raise m.Refused(f"{c['name']}'s {w['name']} has no damage dice on their sheet ({w['line']}): pass "
                                    "damage")
                raise m.Refused(f"{c['name']}'s {w['name']} has a choice of damage: pass damage, all its dice in one "
                                f"expression ({' + '.join(w['fixed']) + ' plus ' if w['fixed'] else ''}one of: "
                                f"{', '.join(w['choice'])}; e.g. 1d10+3)")
            for k in ("damage", "extra_damage"):
                if x.get(k):
                    m.roll(self.typed(x[k])[0], rng=_Low())  # readable (no real dice spent)

    @staticmethod
    def typed(expr: str) -> tuple[str, str | None]:
        """'2d8 radiant' -> ('2d8', 'radiant'); '1d6' -> ('1d6', None)."""
        parts = str(expr).strip().rsplit(" ", 1)
        if len(parts) == 2 and parts[1].lower() in DAMAGE_TYPES:
            return parts[0].strip(), parts[1].lower()
        return str(expr).strip(), None

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
            raise m.Refused("turns: the turns in initiative order from the next one, up to the PC's")
        # each turn must be the next combatant's, up to the PC's. With resume, turns replace the ones still to come.
        order, i = f["order"], f["turn"]
        for t in turns:
            t["name"] = self.name_of(t.get("name", ""))
        started = bool(turns) and not pend and i >= 0 and order[i]["name"] == turns[0].get("name") \
            and not order[i].get("used")  # its turn was started with next_turn
        for k, t in enumerate(turns):
            self.check(t)
            if k == 0 and started:
                continue
            i = (i + 1) % len(order)
            if order[i]["name"] != t["name"]:
                raise m.Refused(f"{order[i]['name']}'s turn comes next, not {t['name']}'s: send the turns in initiative "
                                "order, up to the PC's")
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
                now = k == 0 and started
                self.p = {"name": t["name"], "turn": None, "why": ""}
                kind, why = self.turn_problem(t, now)
                if kind == "next":
                    self.p["why"] = why
                    raise Stop(f"STOPPED before {t['name']}'s turn: {why}. Decide the turns again from the tracker as it "
                               "is now, and call creature_turns with resume and the turns from the next one.")
                if kind == "down":
                    self.p["why"] = why
                    raise Stop(f"STOPPED before {t['name']}'s turn: {why}, so their turn is a death save. Start it with "
                               "next_turn and roll it; then call creature_turns with resume and the turns after it, or "
                               "resume and skip_rest if the PC's is next.")
                self.queue.pop(0)
                if kind == "gone":
                    self.log(f"fight: {why}: its turn is gone")
                    continue
                if not now:
                    self.log("fight: " + self.g.advance_turn())
                k += 1
                if kind == "out":
                    self.log(f"fight: {why}: its turn passes")
                    continue
                self.p = {"name": t["name"], "turn": t, "attack": 0, "stage": "start", "why": "", "left": []}
                self.go({})
            self.p = None
            # The PC's turn is started by the DM's next_turn, as ever: when the code started a party member's turn, the
            # DM called next_turn again and skipped it (a replay, 2026-10-19).
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

    def turn_problem(self, t: dict[str, Any], now: bool) -> tuple[str, str]:
        """Whether turn t can start: "" (it can); "gone" (out of the fight); "next" (someone else's turn comes
        first: the DM decides again); "down" (a companion at 0 HP: a death save); "out" (a creature at 0 HP or anyone
        incapacitated: its turn passes)."""
        order = self.g.fight["order"]
        c = next((x for x in order if x["name"] == t["name"]), None)
        if not c:
            return "gone", f"{t['name']} is no longer in the fight"
        at = order[self.g.fight["turn"] if now else (self.g.fight["turn"] + 1) % len(order)]
        if at["name"] != c["name"]:
            return "next", f"{at['name']}'s turn comes {'now' if now else 'next'}"
        if self.hp(c["name"]) <= 0:
            return ("down" if self.member(c["name"]) else "out"), f"{c['name']} is at 0 HP"
        if (cond := self.conditions(c["name"]) & m.incapacitating()):
            return "out", f"{c['name']} is {', '.join(sorted(cond))}"
        return "", ""

    def standing(self, name: str) -> bool:
        """`name` is in the fight and up: above 0 HP (or already down when the turns were sent), not dead."""
        if not self.in_fight(name):
            return False
        if self.member(name):
            return (self.hp(name) > 0 or name in self.down) and "dead" not in self.conditions(name)
        return self.hp(name) > 0

    def go(self, resume: dict[str, Any]) -> None:
        """Play the turn in self.p from where it stopped: its move out of reach, then each attack."""
        p, t = self.p, self.p["turn"]
        if not self.in_fight(t["name"]):
            return  # taken out of the fight while it was stopped (an opportunity attack, say)
        c = self.entry(t["name"])
        attacks = t.get("attacks") or []
        if resume.get("skip_rest"):
            p["attack"], resume = len(attacks), {}
        if p["stage"] in ("start", "leave") and not t.get("after_attacks"):
            self.leave(t)
            p["stage"] = "start"
        while p["attack"] < len(attacks):
            x = attacks[p["attack"]]
            if p["stage"] == "start":
                if not self.in_fight(c["name"]) or self.hp(c["name"]) <= 0 or \
                        self.conditions(c["name"]) & m.incapacitating():
                    self.log(f"fight: {c['name']} can't go on: the rest of its turn is lost")
                    return
                # a target that has dropped since: the next of or_targets still up; with none, it isn't made
                tgt = next((v for v in [x["target"], *x.get("or_targets", [])] if self.standing(v)), None)
                if not tgt:
                    self.log(f"fight: {c['name']}'s {x['attack']} isn't made: "
                             + ", ".join([x["target"], *x.get("or_targets", [])]) + " no longer up")
                    p.update(attack=p["attack"] + 1)
                    continue
                x["target"] = tgt
            self.attack(c, x, resume)
            resume = {}
            p.update(attack=p["attack"] + 1, stage="start", roll=None, halve=False, reduce=0, mode=None, dodge=None)
            if not self.in_fight(c["name"]):
                return  # it's out of the fight
        used = self.entry(c["name"]).get("used", [])
        if any(not x.get("bonus_action") for x in attacks) and "action" not in used:
            self.g.fight, _ = m.use(self.g.fight, "action", c["name"])
        if any(x.get("bonus_action") for x in attacks) and "bonus action" not in used:
            self.g.fight, _ = m.use(self.g.fight, "bonus action", c["name"])
        if t.get("after_attacks"):
            p["stage"] = "leave"
            self.leave(t)
        if t.get("note"):
            self.g.transcript.append({"kind": "call", "tool": "creature_turns", "input": {"name": t["name"], "note": t["note"]},
                                      "result": "", "error": False})

    def leave(self, t: dict[str, Any]) -> None:
        """Opportunity attacks as the mover leaves others' reach: the player's is asked; a companion's or a creature's
        is made where the call gives its opportunity_attack."""
        p = self.p
        for item in t.get("leaves_reach_of") or []:
            w, oa = item["name"], item.get("opportunity_attack")
            if w in p["left"]:
                continue
            p["left"].append(w)
            if not self.in_fight(t["name"]) or self.hp(t["name"]) <= 0:
                return
            if w == self.pc():
                if self.can(w, "Opportunity Attack"):
                    p["why"] = f"{t['name']} leaving {w}'s reach"
                    self.ask(w, "Opportunity Attack", f"{t['name']} leaves {w}'s reach.",
                             "roll the attack and its damage, and change_creature")
                continue
            if oa and self.can_react(w):
                self.strike(w, oa, t["name"])

    def strike(self, by: str, attack: str, target: str) -> None:
        """An opportunity attack, whole: roll, Parry for a creature, damage."""
        c, tm = self.entry(by), self.member(target)
        w = self.weapon(c, attack)
        label = f"{by}'s {w['name']} at {target} (an opportunity attack)"
        if not self.member(by) and tm:
            pc = self.pc()
            if self.can(pc, "Cutting Words") or (pc != target and self.can(pc, "Protection")):
                self.p["why"] = label
                raise Stop(f"STOPPED: {label}, and {pc} can use a reaction on it (Cutting Words or Protection). Ask "
                           "the player first and end your reply there; then resolve the attack yourself (roll it and "
                           f"its damage, record them; uses reaction, by {by}), and call creature_turns with resume.")
        self.used_reaction(by)
        r = m.roll(f"1d20{w['bonus']:+d}")
        roll = {"total": r["total"], "natural": r["natural"]}
        self.log("dice " + m.roll_text(r, f"{label} (AC {self.ac(target)})"))
        crit = roll["natural"] == 20
        hit = crit or (roll["natural"] != 1 and roll["total"] >= self.ac(target))
        if hit and not tm and self.parry(target, w["ranged"], crit, roll, label):
            hit = False
        if not hit:
            self.log(f"fight: {label}: a miss")
            return
        self.deal(c, w, {}, target, crit, w["ranged"], label, False, 0)

    def attack(self, c: dict[str, Any], x: dict[str, Any], resume: dict[str, Any]) -> None:
        """One attack, from the stage it stopped at: start, roll (after Protection), rolled (after Cutting Words), hit
        (after Shield and the like), then after the damage: rebuke, rider."""
        p = self.p
        w = self.weapon(c, x["attack"])
        target = x["target"].strip()
        tm = self.member(target)
        by_party = bool(self.member(c["name"]))
        ranged = bool(x.get("ranged")) or w["ranged"]
        label = f"{c['name']}'s {w['name']} at {target}"
        if p["stage"] == "start":
            p["stage"] = "roll"
            if tm and not by_party:
                guard = next((v for v in self.party() if v != target and self.declared(x, v, "Protection")), None)
                if guard:
                    self.used_reaction(guard)
                    p["mode"] = "disadvantage"
                    self.log(f"fight: {guard} uses Protection (their reaction): disadvantage on {label}")
                elif self.pc() != target and self.can(self.pc(), "Protection"):
                    p["why"] = f"{label}, before the roll"
                    self.ask(self.pc(), "Protection", f"{c['name']} is about to attack {target} with its {w['name']}.",
                             "it imposes disadvantage: pass resume {mode: 'disadvantage'}")
        if p["stage"] == "roll":
            r = m.roll(f"1d20{w['bonus']:+d}", _mode(resume.get("mode") or x.get("mode"), p.get("mode")))
            p.update(stage="rolled", roll={"total": r["total"], "natural": r["natural"]})
            self.log("dice " + m.roll_text(r, f"{label} (AC {self.ac(target)})"))
            resume = {}
            if not by_party:
                self.cutting_words(c, x, target, label)
        roll = p["roll"]
        if p["stage"] in ("rolled", "hit") and resume.get("roll_change"):  # Cutting Words, or a creature's reaction
            roll["total"] += int(resume["roll_change"])
            self.log(f"fight: {label}: the attack roll is now {roll['total']}")
        if p["stage"] == "rolled":
            resume = {}
        crit = roll["natural"] == 20
        hit = crit or (roll["natural"] != 1 and roll["total"] >= self.ac(target))
        if p["stage"] == "rolled":
            if not hit:
                self.log(f"fight: {label}: a miss")
                return
            p["stage"] = "hit"
            if tm and target != self.pc():
                p.update(self.defend(x, target, roll, crit, ranged, label))
            elif tm:
                ask = {"Shield": (not crit and roll["total"] < self.ac(target) + 5,
                                  "change_pc cast Shield, with ac_set to the new AC"),
                       "Uncanny Dodge": (True, "pass resume {halve_damage: true}"),
                       "Deflect Missiles": (ranged, "roll 1d10 + DEX modifier + monk level, and pass resume "
                                                    "{damage_reduction: the total}")}
                for reaction, (could, how) in ask.items():
                    if could and self.can(target, reaction):
                        p["why"] = f"{label}, a hit"
                        self.ask(target, reaction, f"{c['name']}'s {w['name']} hits {target}: {roll['total']} against "
                                 f"AC {self.ac(target)}{', a critical hit' if crit else ''}.", how)
            elif self.parry(target, ranged, crit, roll, label):
                return
            else:
                self.other_reaction(target, roll, crit, label)
        if p["stage"] == "hit":
            if not (crit or (roll["natural"] != 1 and roll["total"] >= self.ac(target))):
                self.log(f"fight: {label}: now a miss against AC {self.ac(target)}")
                return
            total, text = self.deal(c, w, x, target, crit, ranged, label,
                                    bool(resume.get("halve_damage") or p.get("halve")),
                                    int(resume.get("damage_reduction") or p.get("reduce") or 0), p.get("dodge"))
            p.update(stage="rebuke", dealt=total)
            resume = {}
        if p["stage"] == "rebuke":
            p["stage"] = "rider"
            if target == self.pc() and p.get("dealt") and self.can(target, "Hellish Rebuke"):
                p["why"] = f"{label}, after the damage"
                self.ask(target, "Hellish Rebuke", f"{target} took {p['dealt']} damage from {c['name']}.",
                         "change_pc cast Hellish Rebuke, roll its save and damage, and change_creature")
        if p["stage"] == "rider":
            p["stage"] = "done"
            if w["rider"]:
                p["why"] = f"{label}: what its hit does beyond the damage"
                raise Stop(f"STOPPED: {c['name']}'s {w['name']} hit {target}, and on a hit its stat block says: "
                           f"\"{w['rider']}\" Only the damage was applied. Resolve the rest by the rules (roll any save "
                           "with roll), then call creature_turns with resume: the turns you sent go on from here.")

    # ---- reactions taken by the code ----
    def defend(self, x: dict[str, Any], target: str, roll: dict[str, Any], crit: bool, ranged: bool,
               label: str) -> dict[str, Any]:
        """A companion hit by an attack takes the reaction the call wrote on it: Shield if it turns the hit into a miss,
        else Uncanny Dodge, else Deflect Missiles against a ranged attack. Returns halve / reduce for the damage, or
        dodge: the reaction to take once the damage is rolled, if it reaches min_damage."""
        ac = self.ac(target)
        if not crit and roll["total"] < ac + 5 and self.declared(x, target, "Shield"):
            s = self.member(target)
            lvl = min(int(k) for k, v in s["spell_slots"].items() if v.get("left", 0) > 0)
            try:
                text = self.g.change_party_member({"who": target, "cast": "Shield", "level": lvl, "ac_set": ac + 5,
                                                   "ac_reason": "Shield, until the start of their next turn"})
            except m.Refused as e:
                self.log(f"fight: {target} can't cast Shield: {e}")
            else:
                self.used_reaction(target)
                self.log(f"sheet: {text} (their reaction; ac_reset at the start of their next turn)")
                return {}
        for what in _AFTER_DAMAGE:
            if (d := self.declared(x, target, what)) and (ranged or what == "Uncanny Dodge"):
                if d.get("min_damage"):
                    return {"dodge": d}
                return self.dodge(target, what)
        return {}

    def dodge(self, target: str, what: str) -> dict[str, Any]:
        """Uncanny Dodge (the damage halved) or Deflect Missiles (reduced by 1d10 + DEX modifier + monk level)."""
        self.used_reaction(target)
        if what == "Uncanny Dodge":
            self.log(f"fight: {target} uses Uncanny Dodge (their reaction): the damage is halved")
            return {"halve": True}
        s = self.member(target)
        r = m.roll(f"1d10{(s['scores']['DEX'] - 10) // 2 + s['level']:+d}")
        self.log("dice " + m.roll_text(r, f"{target}'s Deflect Missiles (their reaction): damage reduced by"))
        return {"reduce": r["total"]}

    def cutting_words(self, c: dict[str, Any], x: dict[str, Any], target: str, label: str) -> None:
        """A bard whose Cutting Words could turn this hit into a miss: a companion the call says takes it does; the
        player is asked."""
        p, roll, ac = self.p, self.p["roll"], self.ac(target)
        if roll["natural"] in (1, 20) or roll["total"] < ac:
            return
        for w, s in self.party().items():
            if not self.can(w, "Cutting Words") or roll["total"] - inspiration_die(s) >= ac:
                continue
            if w == self.pc():
                p["why"] = f"{label}, after the attack roll"
                self.ask(w, "Cutting Words", f"{c['name']}'s attack roll against {target} is {roll['total']}, a hit "
                         f"against AC {ac}.", "change_pc spending a Bardic Inspiration use; roll the die, and pass "
                         "resume {roll_change: minus the roll}")
            if self.declared(x, w, "Cutting Words"):
                text = self.g.change_party_member({"who": w, "use_resource": "Bardic Inspiration"})
                r = m.roll(f"1d{inspiration_die(s)}")
                self.used_reaction(w)
                roll["total"] -= r["total"]
                self.log(f"sheet: {text}")
                self.log("dice " + m.roll_text(r, f"{w}'s Cutting Words (their reaction) on {label}: the roll is now "
                                               f"{roll['total']}"))
                return

    def parry(self, target: str, ranged: bool, crit: bool, roll: dict[str, Any], label: str) -> bool:
        """A creature with Parry ("adds 2 to its AC against one melee attack that would hit it") takes it when it turns
        the hit into a miss: always worth it. True if it did."""
        e = self.entry(target)
        if not e.get("monster") or not self.can_react(target) or ranged or crit:
            return False
        for r in self.stat_block(e).get("reactions") or []:
            n = re.search(r"adds (\d+) to its AC against one melee attack that would hit it", r.get("desc", ""))
            if n and roll["total"] < self.ac(target) + int(n[1]):
                self.used_reaction(target)
                self.log(f"fight: {target} uses {r['name']} (its reaction): AC {self.ac(target) + int(n[1])} against "
                         f"{label.split(' at ')[0]}, now a miss")
                return True
        return False

    def other_reaction(self, target: str, roll: dict[str, Any], crit: bool, label: str) -> None:
        """A creature hit, with a reaction about attacks or damage other than Parry: the DM decides."""
        e = self.entry(target)
        if not e.get("monster") or not self.can_react(target):
            return
        rs = [r for r in self.stat_block(e).get("reactions") or [] if not re.search(r"adds \d+ to its AC", r.get("desc", ""))
              and re.search(r"\b(attack|damage|hit)\b", r.get("desc", ""))]
        if rs:
            self.p["why"] = f"{label}, a hit"
            raise Stop(f"STOPPED for a reaction: {label} hits: {roll['total']} against AC {self.ac(target)}"
                       f"{', a critical hit' if crit else ''}. {target}'s stat block has the reaction "
                       + "; ".join(f"{r['name']}: {r['desc']}" for r in rs)
                       + f" Decide whether it takes it; if so, record it (uses reaction, by {target}) and resolve it. "
                       "Then call creature_turns with resume (roll_change, halve_damage or damage_reduction if it "
                       "changes this attack): the turns you sent go on from here.")

    # ---- damage ----
    def deal(self, c: dict[str, Any], w: dict[str, Any], x: dict[str, Any], target: str, crit: bool, ranged: bool,
             label: str, halve: bool, reduce: int, dodge: dict[str, Any] | None = None) -> tuple[int, str]:
        """Roll a hit's damage, apply resistances, and apply it; a concentrating party member saves. dodge: a
        companion's Uncanny Dodge or Deflect Missiles, taken if the damage rolled reaches its min_damage."""
        tm, attacker = self.member(target), self.member(c["name"])
        if not ranged and not x.get("beyond_5ft") and self.conditions(target) & {"paralyzed", "unconscious"}:
            crit = True  # SRD: a hit on a paralyzed or unconscious creature from within 5 feet is a critical hit
        if x.get("damage"):
            expr, typ = self.typed(x["damage"])
            parts = [(expr, typ or (next(iter(w["types"])) if len(w["types"]) == 1 else None))]
        else:
            parts = list(w["dmg"])
        if x.get("extra_damage"):
            expr, typ = self.typed(x["extra_damage"])
            parts.append((expr, typ or parts[0][1]))
        if attacker and raging(attacker, self.g.clock) and w["weapon"] and not ranged:
            parts[0] = (f"{parts[0][0]}+{rage_damage(attacker)}", parts[0][1])  # SRD Rage: melee weapon, Strength
        by_type: dict[str | None, int] = {}
        for expr, typ in parts:
            r = m.roll(crit_dice(expr) if crit else expr)
            by_type[typ] = by_type.get(typ, 0) + max(0, r["total"])
            self.log("dice " + m.roll_text(r, f"{label}: damage" + (f" ({typ})" if typ else "")
                                           + (" (critical hit)" if crit else "")))
        if dodge and sum(by_type.values()) >= dodge["min_damage"] and self.can(target, dodge["reaction"]):
            got = self.dodge(target, dodge["reaction"])
            halve, reduce = halve or got.get("halve", False), reduce + got.get("reduce", 0)
        if halve:
            by_type = {k: v // 2 for k, v in by_type.items()}
        for k in by_type:
            took = min(reduce, by_type[k])
            by_type[k], reduce = by_type[k] - took, reduce - took
        total = self.resist(target, w, x, by_type)
        if tm:
            text = self.g.change_party_member({"damage": total} | ({"critical_hit": True} if crit else {})
                                              | ({"who": target} if tm is not self.g.sheet else {}))
            self.log(f"sheet: {text}")
            self.concentration(target, total)
        else:
            self.g.fight, text = m.change_creature(self.g.fight, {"name": target, "damage": total})
            self.log(f"fight: {text}")
        return total, text

    def concentration(self, who: str, dmg: int) -> None:
        """SRD Concentration: damage calls for a Constitution save, DC 10 or half the damage if higher; at 0 HP
        (unconscious) or incapacitated it ends. The code rolls it, as the DM would."""
        s = self.member(who)
        on = s.get("concentration")
        if not on or dmg <= 0:
            return
        first = s["name"].split()[0]
        if s["hp"]["current"] > 0 and not set(s.get("conditions", [])) & (m.incapacitating() | {"dead"}):
            dc = max(10, dmg // 2)
            r = m.roll(f"1d20{save_bonus(s, 'CON'):+d}")
            held = r["total"] >= dc
            self.log("dice " + m.roll_text(r, f"{first}'s concentration on {on} (CON save, DC {dc})")
                     + (": it holds" if held else ": it's lost"))
            if held:
                return
        text = self.g.change_party_member({"concentration_end": True} | ({"who": who} if s is not self.g.sheet else {}))
        self.log(f"sheet: {text}")
        timer = f"{first}'s {on}"
        if timer in self.g.clock.get("timers", {}):
            self.g.clock, text = m.change_time(self.g.clock, {"remove_timer": timer})
            self.log(f"clock: {text}")

    def resist(self, target: str, w: dict[str, Any], x: dict[str, Any], by_type: dict[str | None, int]) -> int:
        """The damage after the target's resistances, immunities and vulnerabilities, each type on its own. The DM's
        target_resists, when passed, is used instead for the whole attack."""
        raw = sum(by_type.values())
        if (over := x.get("target_resists")):
            total = raw if over == "normal" else resisted(raw, {over})
            if over != "normal":
                self.log(f"fight: {target} is {over} to this damage: {raw} -> {total}")
            return total
        tm = self.member(target)
        unsure: list[str] = []
        if tm:
            found = member_resists(tm, self.g.clock)
            res = {t: set(v) for t, v in found.items()}
            why = {t: ", ".join(f"{k} ({src})" for k, src in v.items()) for t, v in found.items()}
        else:
            e = self.entry(target)
            res, unsure = creature_resists(self.stat_block(e), w["weapon"]) if e.get("monster") else ({}, [])
            why = {t: ", ".join(sorted(v)) for t, v in res.items()}
        total = 0
        for typ, v in by_type.items():
            if typ is None:
                if res:
                    self.log(f"fight: the damage type isn't known, so {target}'s resistances weren't applied: pass "
                             "target_resists if one applies")
                total += v
                continue
            after = resisted(v, res.get(typ, set()))
            if after != v:
                self.log(f"fight: {target} is {why[typ]} to {typ}: {v} -> {after}")
            total += after
        if unsure:
            self.log(f"fight: {target}'s stat block also has {'; '.join(unsure)}: not applied. If it applies, the "
                     "damage is wrong: correct it with change_creature")
        return total

    def ac(self, name: str) -> int:
        s = self.member(name)
        if s:
            return int((s.get("ac_now") or {}).get("value") or s["ac"])
        return self.entry(name)["ac"]

    def log(self, text: str) -> None:
        self.g.log("tool", text)
        self.lines.append(text)
