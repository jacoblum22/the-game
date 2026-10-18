"""Play D&D 5e (2014, SRD) in the terminal with an AI DM.

    py -3.12 -m dm.play fighter            # or rogue, wizard
    py -3.12 -m dm.play new                # make a character with the DM first
    py -3.12 -m dm.play --resume saves/<file>.json

In play: type what your character does. /sheet shows your sheet, /quit saves and exits. /back lists your lines;
/redo <turn> [line] goes back to just before one (sent again, or changed) in a new save; /edit <text> rewrites the
DM's latest reply (dm/branch.py).
The DM runs on the Anthropic API, with the key in the ANTHROPIC_API_KEY environment variable.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from dm import branch, create, lookup, model
from dm import lore as notebook
from dm import mechanics as m
from dm.model import Tool, tool

HERE = Path(__file__).parent
SAVES = HERE.parent / "saves"
MODEL = "claude-sonnet-5-5"
on_save: Callable[[Path, str], None] = lambda path, text: None  # the browser page sets it: it keeps saves itself


def lookup_tool(record: Callable[[dict[str, Any], str], None]) -> Any:
    """The rules lookup, shared by creation and play. `record` keeps the call and its result in the transcript."""
    @tool("lookup", "Look up the exact SRD 5.1 text of a spell, monster stat block, condition, magic item, piece of "
          "equipment, rules section, class feature or racial trait, by its name. A class (kind \"class\") gives its "
          "rules other than its features: hit points, proficiencies, equipment, the level table and the spellcasting "
          "rules; a subclass name (Life Domain, The Fiend) gives its text and spell list. If there's no entry by that "
          "name, the names and rules sections that contain it are listed.",
          {"type": "object", "properties": {
              "name": {"type": "string", "description": "e.g. Goblin, Shield, Grappled, Cover, Longsword, Sneak Attack"},
              "kind": {"type": "string", "enum": list(lookup.KINDS), "description": "optional: only this kind"}},
           "required": ["name"]})
    async def lookup_(a: dict[str, Any]) -> dict[str, Any]:
        text = lookup.lookup(a.get("name") or "", a.get("kind") or "")
        record(a, text)
        return {"content": [{"type": "text", "text": text}]}
    return lookup_


_INT = {"type": "integer", "minimum": 0}
_ITEMS = {"type": "array", "items": {"type": "object", "properties": {"item": {"type": "string"},
                                                                      "qty": {"type": "integer", "minimum": 1}},
                                     "required": ["item"]}}
_NAMES = {"type": "array", "items": {"type": "string"}}
_WHO = {"type": "string", "description": "a companion's name; leave out for the player character"}
# a fight's action economy (owner, 2026-10-13): marked in the tracker, with a reminder, never refused
_USES = {"uses": {"type": "string", "enum": list(m.USES), "description": "in a fight: what this spends, e.g. the "
                  "attack roll of an Attack action is the action; the tracker marks it until that combatant's next turn"},
         "by": {"type": "string", "description": "with uses: the combatant, exactly as in the tracker, when it isn't "
                "the one whose turn it is (a reaction, for example)"}}



def home_relative(path: str) -> str:
    """A path under the home folder as ~/..., so a save names no user."""
    try:
        return "~/" + Path(path).relative_to(Path.home()).as_posix()
    except ValueError:
        return path


class Game:
    def __init__(self, data: dict[str, Any], path: Path) -> None:
        self.sheet: dict[str, Any] = data["sheet"]
        self.companions: list[dict[str, Any]] = data.get("companions", [])  # full sheets, at most 2 (owner 2026-10-12)
        self.fight: dict[str, Any] | None = data.get("fight")
        self.clock: dict[str, Any] = data.get("clock") or m.new_clock()  # saves from before 2026-10-12 have none
        self.transcript: list[dict[str, Any]] = data.get("transcript", [])
        self.lore: dict[str, Any] = data.get("lore") or notebook.new()  # the DM's notebook (dm/lore.py), hidden from the player
        self.model: str = data.get("model", MODEL)
        self.system = ""  # the DM's instructions, written when play starts
        # The conversation is cut short when it gets long (owner, 2026-10-13): each cut keeps the DM's own summary of
        # the game up to that turn, newest last, hidden from the player; the new conversation opens with it.
        self.story: list[dict[str, Any]] = data.get("story", [])
        self.size = 0  # the conversation's length after the last model call, in tokens
        self.path = path
        # Two ways to run the DM (owner, 2026-10-13): "api", the API with a key, the conversation kept here in the save
        # (the browser version); "sdk", the owner's own, on their Claude login, the conversation in Claude Code's
        # session file (dm/sdk.py). Saves from before the API have a session id and no backend.
        self.backend: str = data.get("backend") or ("sdk" if data.get("session_id") else "api")
        self.messages: list[dict[str, Any]] = data.get("messages", [])
        self.session_id: str | None = data.get("session_id")
        # an SDK save's session folder; saves from before 2026-10-11 used saves/. Kept as ~/... in the save so it carries
        # no username and works on another machine.
        self.cwd: str = str(Path(os.path.expanduser(data.get("cwd", str(SAVES)))))
        self.sdk: Any = None  # the open SDK client while an SDK game is played
        # Going back (dm/branch.py, owner 2026-10-17): a snapshot before each of the player's lines. A fork's SDK
        # conversation starts from its source's session at fork_at; an API fork from after a cut opens a new
        # conversation with the turns so far (rebuild).
        self.snapshots: list[dict[str, Any]] = data.get("snapshots", [])
        self.fork_at: str | None = data.get("fork_at")
        self.rebuild: bool = bool(data.get("rebuild"))
        self.past_pcs: list[dict[str, Any]] = data.get("past_pcs", [])  # earlier PCs, after a death (new_pc)
        self.new_rolled: list[int] | None = data.get("new_rolled")  # a new PC's rolled scores, until it's made
        self.reply_len = 0  # this turn: how much of the DM's reply is written, and whether a tool was called after it
        self.late = False
        self.answered: set[str] = set()  # this turn: the entries notebook writes have answered with (notebook.answer)

    def save(self) -> None:
        self.path.parent.mkdir(exist_ok=True)
        data = {"sheet": self.sheet, "companions": self.companions, "fight": self.fight, "clock": self.clock, "model": self.model,
                "transcript": self.transcript, "lore": self.lore, "backend": self.backend,
                "story": self.story, "snapshots": self.snapshots, "past_pcs": self.past_pcs}
        data |= {"new_rolled": self.new_rolled} if self.new_rolled else {}
        data |= ({"session_id": self.session_id, "cwd": home_relative(self.cwd)} if self.backend == "sdk" else {"messages": self.messages})
        data |= ({"fork_at": self.fork_at} if self.fork_at else {}) | ({"rebuild": True} if self.rebuild else {})
        text = json.dumps(data, indent=1, ensure_ascii=False)
        self.path.write_text(text, encoding="utf-8")
        on_save(self.path, text)

    def log(self, kind: str, text: str) -> None:
        self.transcript.append({"kind": kind, "text": text})
        if kind == "tool":
            print(f"  [{text}]")

    def status(self) -> str:
        return (m.clock_text(self.clock) + "\n" + m.status(self.sheet)
                + "".join(f"\n\nCompanion {c['name']}, {c['summary']}:\n" + m.status(c) for c in self.companions)
                + "\n" + m.fight_text(self.fight, self.sheet, self.companions))

    def member(self, who: Any) -> int | None:
        """The companion `who` names (index), or None for the PC (no `who`, or the PC's name). Raises Refused."""
        if not who:
            return None
        key = str(who).strip().casefold()
        for i, s in enumerate([self.sheet, *self.companions]):
            if key in (s["name"].casefold(), s["name"].split()[0].casefold()):
                return i - 1 if i else None
        raise m.Refused(f"who: no party member called {who!r}; the party is "
                      + ", ".join(s["name"] for s in [self.sheet, *self.companions]))

    def change_party_member(self, a: dict[str, Any]) -> str:
        """change_pc for the PC or a companion (`who`). A rest is the whole party's: the clock moves once, and each
        companion rests too, with its own end-of-rest choices from `companions`."""
        a = dict(a)
        i = self.member(a.pop("who", None))
        spell = {k: a.pop(k) for k in ("cast", "level", "ritual", "no_slot") if k in a}
        clock, lines = self.clock, []
        if spell:
            if not spell.get("cast"):
                raise m.Refused("level, ritual and no_slot go with cast (the spell's name)")
            if a.get("spend_slot") or a.get("concentration_start") or a.get("long_rest") or a.get("short_rest"):
                raise m.Refused("cast spends its own slot and starts its own concentration, and a rest is a call of its "
                                "own: leave out spend_slot, concentration_start and rests")
            slot, conc, clock, lines = m.cast(self.sheet if i is None else self.companions[i], self.clock, spell)
            a |= {"spend_slot": slot, "concentration_start": conc}
        if not spell or any(a.values()):
            lines.append(self._change_member(i, a))
        if spell:  # a cast comes without a rest, so the clock is only the cast's
            self.clock = clock
        return "; ".join(lines)

    def _change_member(self, i: int | None, a: dict[str, Any]) -> str:
        rest = 8 * 3600 if a.get("long_rest") else 3600 if a.get("short_rest") else 0
        if i is not None:
            if rest:
                raise m.Refused("rests are the whole party's: pass short_rest or long_rest without who (companions' "
                              "end-of-rest choices go in companions)")
            if a.get("xp_gained"):
                raise m.Refused("companions have no XP: they are at the PC's level and level up when the PC does")
            self.companions[i], lines = m.change_pc(self.companions[i], a)
            return f"{self.companions[i]['name']}: " + "; ".join(lines)
        last, now = self.sheet.get("last_long_rest"), self.clock["now"]
        if a.get("long_rest") and now is not None and last is not None and now + rest - last < m.DAY:
            # SRD: "A character can't benefit from more than one long rest in a 24-hour period" (autoloop, 2026-10-14)
            raise m.Refused(f"one long rest in 24 hours: the last finished {m.when(last)}, so the next can finish "
                            f"{m.when(last + m.DAY)} at the earliest. A short rest is allowed")
        choices = a.pop("companions", None) or {}
        if choices and not rest:
            raise m.Refused("companions: end-of-rest choices, only together with short_rest or long_rest")
        named = {self.member(k): v for k, v in choices.items()}  # refuses an unknown name
        if None in named:
            raise m.Refused("companions: name companions here; the PC's own choices go in the call's other fields")
        sheet, lines = m.change_pc(self.sheet, a)
        party = list(self.companions)
        for j, c in enumerate(party):
            if a.get("long_rest") and ("dead" in c["conditions"] or c["hp"]["current"] < 1):
                lines.append(f"{c['name']}: no benefit from the long rest (0 hit points)")
                continue
            if rest:
                ch = {k: v for k, v in (named.get(j) or {}).items() if k in ("prepare_spells", "resilience_type")}
                party[j], more = m.change_pc(c, ch | {"long_rest": bool(a.get("long_rest")),
                                                       "short_rest": bool(a.get("short_rest"))})
                lines.append(f"{c['name']}: " + "; ".join(more))
        self.sheet, self.companions = sheet, party
        self.clock = m.advance(self.clock, rest)
        if a.get("long_rest") and self.clock["now"] is not None:
            self.sheet["last_long_rest"] = self.clock["now"]
        if rest and self.clock["now"] is not None:
            lines.append(f"{m.span(rest)} later: {m.when(self.clock['now'])}")
        return "; ".join(lines)

    def change_party(self, a: dict[str, Any]) -> str:
        if a.get("remove"):
            i = self.member(a["remove"])
            if i is None:
                raise m.Refused("remove: the PC can't leave the party")
            name = self.companions[i]["name"]
            note = ""
            if self.fight and any(c["name"] == name for c in self.fight["order"]):
                self.fight, note = m.change_creature(self.fight, {"name": name, "remove": True})
                note = "; " + note
            del self.companions[i]
            return f"{name} left the party{note}"
        ch = a.get("add")
        if not isinstance(ch, dict):
            raise m.Refused("pass add (a companion's full set of choices) or remove (a companion's name)")
        if len(self.companions) >= 2:
            raise m.Refused("the party is full: the PC and at most 2 companions")
        if ch.get("ability_method") != "standard_array":
            raise m.Refused("companions use the standard array: ability_method standard_array")
        name = str(ch.get("name") or "").strip()
        taken = False
        if name:
            try:
                self.member(name)
                taken = True
            except m.Refused:
                pass
        if taken:
            raise m.Refused(f"name: someone in the party is already called {name!r}")
        sheet, errs = create.build(ch, None)
        if not sheet:
            raise m.Refused("NOT BUILT, nothing changed. Problems:\n- " + "\n- ".join(errs))
        sheet["companion"] = True
        if sheet["level"] < self.sheet["level"]:
            sheet["joining"] = True  # at the PC's level in the story: built up to it before the player sees them join
        self.companions.append(sheet)
        if sheet.get("joining"):
            return f"{sheet['name']} is being built: {sheet['summary']} so far"
        return f"{sheet['name']} joined the party, {sheet['summary']}"

    # A new PC after the old one dies (owner, 2026-10-17): the game goes on in the same world, with its notebook, clock
    # and companions. Two autoloop PCs died in 60 rounds; with no way to make a new sheet the DM played one on the dead
    # PC's sheet, and the other on none.
    def _dead(self) -> None:
        if "dead" not in self.sheet["conditions"]:
            raise m.Refused(f"only when the PC is dead: {self.sheet['name']} isn't")
        if self.fight:
            raise m.Refused("end the fight first (end_fight)")

    def roll_new_scores(self) -> str:
        self._dead()
        if self.new_rolled:
            raise m.Refused(f"already rolled: {self.new_rolled}; scores are rolled once")
        lines, rolled = [], []
        for _ in range(6):
            dice = sorted(m.roll("4d6")["parts"][0]["rolls"], reverse=True)
            rolled.append(sum(dice[:3]))
            lines.append(f"4d6 {dice} drop {dice[3]} = {rolled[-1]}")
        self.new_rolled = rolled
        return "ability scores rolled: " + "; ".join(lines) + f". Scores: {rolled}"

    def new_pc(self, a: dict[str, Any]) -> str:
        self._dead()
        ch = a.get("character")
        if not isinstance(ch, dict):
            raise m.Refused("pass character: the new PC's full set of level-1 choices")
        sheet, errs = create.build(ch, self.new_rolled)
        if not sheet:
            raise m.Refused("NOT BUILT, nothing changed. Problems:\n- " + "\n- ".join(errs))
        if not a.get("confirm"):
            return ("BUILT, nothing changed yet. Show the player this sheet and ask for a yes, then call again with the "
                    "same character, confirm true and the opening:\n" + sheet_text(sheet) + "\n" + m.status(sheet))
        opening = str(a.get("opening") or "").strip()
        if not opening:
            raise m.Refused("the opening is empty: where the new character is, why, and how they come into the story")
        sheet["opening"] = opening
        self.past_pcs.append({**self.sheet, "turn_ended": notebook.now(self.transcript)})
        old, self.sheet, self.new_rolled = self.sheet["name"], sheet, None
        return f"{sheet['name']}, {sheet['summary']}, is the player's character now, in {old}'s place"

    # ---- tools: each runs a mechanics function, records the result, and tells the DM what happened ----

    def run(self, label: str, fn: Callable[[], str], hidden: bool = False, inp: dict[str, Any] | None = None) -> dict[str, Any]:
        try:
            text = fn()
        except m.Refused as e:
            self.transcript.append({"kind": "refused", "text": f"{label}: {e}"})
            return {"content": [{"type": "text", "text": f"REFUSED, nothing changed: {e}"}], "is_error": True}
        if hidden:  # recorded, not shown to the player
            self.transcript.append({"kind": "call", "tool": label, "input": inp or {}, "result": text, "error": False})
        else:
            self.log("tool", f"{label}: {text}" if label != "dice" else text)
        self.save()
        return {"content": [{"type": "text", "text": text}]}

    def using(self, a: dict[str, Any], fn: Callable[[dict[str, Any]], str]) -> Callable[[], str]:
        """A roll or change that may spend an action (`uses`, `by`): the fight's mark and note go with it, all or
        nothing."""
        a = dict(a)
        what, by = a.pop("uses", None), a.pop("by", None)

        def go() -> str:
            if not what:
                return fn(a)
            f, note = m.use(self.fight, what, by)  # a wrong uses refuses before anything is rolled or changed
            if not any(v for k, v in a.items() if k not in ("who", "name")):  # only the use: a Dodge, Dash or Ready
                self.fight = f
                return note.strip(" ()")
            text = fn(a)
            try:
                self.fight, note = m.use(self.fight, what, by)
            except m.Refused:  # the change took the combatant out of the fight
                pass
            return text + note
        return go

    def tools(self) -> list[Any]:
        _span = {k: _INT for k in ("days", "hours", "minutes", "seconds")}

        @tool("roll", "Roll dice, e.g. 1d20+5 or 2d6+3. The player sees every roll.",
              {"type": "object", "properties": {
                  "dice": {"type": "string", "description": "dice expression, e.g. 1d20+4, 2d8+3, 1d4+1d6"},
                  "reason": {"type": "string", "description": "what the roll is for, e.g. 'Brakka's Athletics check, DC 15'"},
                  "mode": {"type": "string", "enum": ["normal", "advantage", "disadvantage"]}, **_USES},
               "required": ["dice", "reason"]})
        async def roll(a: dict[str, Any]) -> dict[str, Any]:
            return self.run("dice", self.using(a, lambda a: "dice " + m.roll_text(m.roll(a["dice"], a.get("mode") or "normal"),
                                                                                  a["reason"])))

        @tool("change_pc", "Record a change to the sheet of the player character, or of a companion (who). Pass only the "
              "fields that change. A rest is the whole party's: pass it without who; it rests every companion too and "
              "moves the clock once. "
              "All-or-nothing: if any part is impossible, nothing is applied and the reason is returned. "
              "A long rest needs the PC at 1 HP or more and only one long rest counts per 24 hours (the tool checks both, "
              "the second by the clock); hit dice are spent at the end of a short rest, one per call.",
              {"type": "object", "properties": {
                  "who": _WHO,
                  "damage": _INT, "heal": _INT, "temp_hp": _INT,
                  "critical_hit": {"type": "boolean", "description": "the damage is from a critical hit (any hit on an unconscious "
                                   "PC from within 5 feet is one): at 0 HP that is two death save failures instead of one"},
                  "hit_dice_spent": {"type": "integer", "minimum": 0,
                                     "description": "1 = spend one hit die at the end of a short rest; the result says what to roll, "
                                     "then pass the total as heal. The player decides after each roll whether to spend another"},
                  # how many to add (owner, 2026-10-14): the DM had passed the new total, and a second failure made three
                  "death_save_successes": {**_INT, "description": "how many to add, not the new total: 1 for a successful "
                                           "death saving throw"},
                  "death_save_failures": {**_INT, "description": "how many to add, not the new total: 1 for a failed death "
                                          "saving throw, 2 for a natural 1. Damage at 0 HP adds its own failures"},
                  "cast": {"type": "string", "description": "a spell the character casts, e.g. Bless. One call does it all: "
                           "it spends the slot (level), moves the clock on by a casting time of minutes or hours, starts a "
                           "timer for the spell's duration at that level (the clock must be set), and starts concentration "
                           "if the spell needs it. Can go with other fields, not a rest"},
                  "level": {"type": "integer", "minimum": 1, "maximum": 9, "description": "with cast: the spell slot "
                            "level used (the spell's level or higher); leave out for a cantrip or a ritual"},
                  "ritual": {"type": "boolean", "description": "with cast: cast as a ritual (no slot; 10 minutes "
                             "longer, put on the clock)"},
                  "no_slot": {"type": "string", "description": "with cast: the spell is cast without a slot, and from "
                              "what, e.g. 'spell scroll', 'Mystic Arcanum' (record that use with use_resource)"},
                  "concentration_start": {"type": "string", "description": "a spell the character concentrates on, "
                                          "when not through cast (cast starts it itself)"},
                  "concentration_end": {"type": "boolean", "description": "the character's concentration ends (a "
                                        "failed save, incapacitated, the spell ended); its timer is separate"},
                  "spend_slot": {"type": "integer", "minimum": 1, "maximum": 9, "description": "a spell slot spent "
                                 "without casting a spell, e.g. Divine Smite; for a spell use cast"},
                  "restore_slot": {"type": "integer", "minimum": 1, "maximum": 9},
                  "use_resource": {"type": "string", "description": "a feature name exactly as on the sheet, e.g. Second Wind"},
                  "restore_resource": {"type": "string"},
                  "resource_amount": {"type": "integer", "minimum": 1,
                                      "description": "how much of a pool to use or restore (e.g. Lay on Hands HP); default 1"},
                  "prepare_spells": {**_NAMES, "description": "the new prepared list; only together with long_rest"},
                  "spellbook_add": {**_NAMES, "description": "wizard: spells copied into the spellbook (record the gold too)"},
                  "ac_set": {"type": "integer", "minimum": 0, "description": "the PC's AC from now on, e.g. after Mage Armor"},
                  "ac_reason": {"type": "string", "description": "what sets it, e.g. 'Mage Armor: 13 + DEX'"},
                  "ac_reset": {"type": "boolean", "description": "AC back to the sheet's normal value"},
                  "items_gained": _ITEMS, "items_lost": _ITEMS,
                  "coin_change_gp": {"type": "number", "description": "money gained (+) or spent (-), in gp; 0.1 = 1 sp"},
                  "conditions_added": _NAMES, "conditions_removed": _NAMES,
                  "xp_gained": _INT,
                  "resilience_type": {"type": "string", "description": "Fiend warlock of 10th level (Fiendish Resilience): the "
                                      "damage type the player chooses when a rest finishes; only together with short_rest or long_rest"},
                  "short_rest": {"type": "boolean"}, "long_rest": {"type": "boolean"},
                  "companions": {"type": "object", "description": "only with short_rest or long_rest: each companion's own "
                                 "end-of-rest choices, {name: {prepare_spells, resilience_type}}"}, **_USES}})
        async def change_pc(a: dict[str, Any]) -> dict[str, Any]:
            return self.run("sheet", self.using(a, self.change_party_member))

        @tool("change_party", "A companion joins or leaves the party (the PC and at most 2 companions). add: the "
              "companion's full set of level-1 choices, in the form build_character takes (name, race, class, "
              "ability_method standard_array, base_scores, choices, cantrips, spells, prepared, alignment, personality, "
              "appearance); srd_options gives the ids. choices is {id: [entries]}, each entry an option letter or "
              "exact name, or {option, picks} for an option with a further choice ({\"option\": \"a\", \"picks\": "
              "[\"Longsword\"]}). Then level_up them (who) to the PC's level. remove: a companion's "
              "name, when they leave or die.",
              {"type": "object", "properties": {"add": {"type": "object"}, "remove": {"type": "string"}}})
        async def change_party(a: dict[str, Any]) -> dict[str, Any]:
            res = self.run("party", lambda: self.change_party(a), hidden=bool(a.get("add")) and self.sheet["level"] > 1)
            if a.get("add") and not res.get("is_error"):
                c = self.companions[-1]
                if c.get("joining"):  # the player sees nothing until they are at the PC's level
                    res["content"][0]["text"] += (
                        f"\n\nThe PC is level {self.sheet['level']}, and so is {c['name']}: they had these levels before "
                        f"they joined. Build them up to it now with level_up_options and level_up, who {c['name']!r}, making "
                        "every choice yourself (hit points too), without asking the player. The player sees them join "
                        "when the last level is taken.")
                res["content"][0]["text"] += "\n\nTheir sheet:\n" + sheet_text(c)
            return res

        @tool("new_pc", "Only after the PC has died, if the player wants to go on in this world with a new character: "
              "the world, notebook, clock and companions carry on. Make it with the player as character creation does: "
              "race, class, ability scores (standard_array, point_buy, or rolled with roll_ability_scores), the class's "
              "and race's choices, equipment, spells, then name, personality and their past; srd_options gives the "
              "ids. character: the full set of level-1 choices, in the form change_party's add takes. Without "
              "confirm, the sheet is built and shown to you, and nothing changes: show it to the player and ask for a "
              "yes. Then call again with the same character, confirm true, and opening: a paragraph on where they "
              "are, why, and how they come into the story. They start at level 1.",
              {"type": "object", "properties": {"character": {"type": "object"}, "confirm": {"type": "boolean"},
                                                "opening": {"type": "string"}}, "required": ["character"]})
        async def new_pc(a: dict[str, Any]) -> dict[str, Any]:
            return self.run("new character", lambda: self.new_pc(a), hidden=not a.get("confirm"), inp=a)

        @tool("roll_ability_scores", "Only for a new PC after a death (new_pc), if the player wants to roll: 4d6, drop "
              "the lowest, six times. Once per character; the player sees every die.", {"type": "object", "properties": {}})
        async def roll_ability_scores(a: dict[str, Any]) -> dict[str, Any]:
            return self.run("dice", self.roll_new_scores)

        @tool("srd_options", "What the SRD offers, for building a companion or a new PC. No arguments: every race, class and the "
              "background. race only: that race in full. class only: that class in full. race and class: every choice "
              "that character needs, with ids, options and spell lists.",
              {"type": "object", "properties": {"race": {"type": "string"}, "class": {"type": "string"}}})
        async def srd_options(a: dict[str, Any]) -> dict[str, Any]:
            try:
                text, error = create.options_text(a.get("race") or "", a.get("class") or ""), False
            except create.Bad as e:
                text, error = str(e), True
            self.transcript.append({"kind": "call", "tool": "srd_options", "input": a, "result": text, "error": error})
            self.save()
            return {"content": [{"type": "text", "text": text}]} | ({"is_error": True} if error else {})

        @tool("level_up_options", "Everything the next level gives a character and every choice made at it "
              "(hit points, features, ability score improvement, spells, invocations), with the skeleton of the level record "
              "to send to level_up. The first line says the XP now and the XP the level needs; a companion (who) has no XP "
              "and is at the PC's level.",
              {"type": "object", "properties": {"who": _WHO}})
        async def level_up_options(a: dict[str, Any]) -> dict[str, Any]:
            try:
                i = self.member(a.get("who"))
                text = (m.level_up_options(self.sheet) if i is None
                        else m.level_up_options(self.companions[i], cap=self.sheet["level"]))
                if i is not None and self.companions[i].get("joining"):
                    c = self.companions[i]
                    text = (f"{c['name']} is joining the party: they had this level before they joined. Make every choice "
                            "yourself, without asking the player (the text below is written for a level-up with the player)"
                            + (", and pass prepare_spells beside the record: the spells they have prepared at this level"
                               if "prepare_count" in (c.get("spellcasting") or {}) else "") + ".\n\n" + text)
                error = False
            except m.Refused as e:
                text, error = str(e), True
            self.transcript.append({"kind": "call", "tool": "level_up_options", "input": a, "result": text, "error": error})
            self.save()
            return {"content": [{"type": "text", "text": text}]} | ({"is_error": True} if error else {})

        @tool("level_up", "Take the next level, once the XP is there and the player has made every choice level_up_options "
              "lists: send the level record. One level per call. All-or-nothing: if the record has any problem, every "
              "problem is returned and nothing changes. On success the sheet is rebuilt at the new level; current HP rises "
              "by the maximum's rise, and the new spell slots and feature uses are usable at once. For a companion, pass who "
              "(beside record): a companion has no XP and takes levels up to the PC's level.",
              {"type": "object", "properties": {"who": _WHO, "record": {"type": "object", "description": "the level "
                                                           "record, in the form level_up_options ends with"},
                                                "prepare_spells": {**_NAMES, "description": "only for a companion who is "
                                                                   "joining: the spells they have prepared at this level"}},
               "required": ["record"]})
        async def level_up(a: dict[str, Any]) -> dict[str, Any]:
            done: list[dict[str, Any]] = []
            try:
                joining = self.companions[self.member(a.get("who"))].get("joining")
            except (m.Refused, TypeError):
                joining = False  # the PC (index None), or a name go() refuses

            def go() -> str:
                record = a.get("record")
                who = a.get("who") or (record.pop("who", None) if isinstance(record, dict) else None)  # seen inside record
                i = self.member(who)
                if i is None:
                    self.sheet, text = m.level_up(self.sheet, record)
                    done.append(self.sheet)
                    behind = [f"{c['name']} (level {c['level']})" for c in self.companions if c["level"] < self.sheet["level"]]
                    if behind:
                        text += "\nCompanions now below the PC's level: " + ", ".join(behind)
                else:
                    c = self.companions[i]
                    if c.get("joining") and "prepare_count" in (c.get("spellcasting") or {}) and not a.get("prepare_spells"):
                        raise m.Refused("prepare_spells: a joining companion had this level already, so pass the spells "
                                        "they have prepared at it, beside the record")
                    if a.get("prepare_spells") and not c.get("joining"):
                        raise m.Refused("prepare_spells: only for a companion who is joining; the prepared list changes "
                                        "when a long rest finishes")
                    new, text = m.level_up(c, record, cap=self.sheet["level"])
                    if c.get("joining"):
                        text = text.replace("; the list changes after a long rest, so the prepared spells are unchanged "
                                            "for now", "")
                        if a.get("prepare_spells"):
                            text += "\n" + m._prepare(new, a["prepare_spells"], True)
                        if new["level"] < self.sheet["level"]:
                            new["joining"] = True
                    self.companions[i] = new
                    done.append(new)
                return text
            res = self.run("level up", go, hidden=bool(joining))
            if joining and done and not done[0].get("joining"):
                self.log("tool", f"party: {done[0]['name']} joined the party, {done[0]['summary']}")
                self.save()
            if done:  # the sheet in the DM's instructions was written at the old level
                res["content"][0]["text"] += ("\n\nThe sheet now (it replaces the one in your instructions):\n" + sheet_text(done[0]))
            return res

        @tool("add_combatants", "Start a fight, or add arrivals to the current one, once their initiative is rolled. The PC is "
              "the combatant named 'pc' and a companion the combatant with their name (their HP lives on their sheets); every "
              "creature needs a distinct name, hp and ac.",
              {"type": "object", "properties": {"combatants": {"type": "array", "items": {
                  "type": "object", "properties": {"name": {"type": "string"}, "initiative": {"type": "integer"},
                                                   "hp": {"type": "integer"}, "ac": {"type": "integer"}},
                  "required": ["name", "initiative"]}}}, "required": ["combatants"]})
        async def add_combatants(a: dict[str, Any]) -> dict[str, Any]:
            def go() -> str:
                self.fight, text = m.add_combatants(self.fight, self.sheet["name"], a["combatants"],
                                                     tuple(c["name"] for c in self.companions))
                return text
            return self.run("fight", go)

        @tool("change_creature", "Damage, heal, add or remove conditions on a creature in the fight, or remove it.",
              {"type": "object", "properties": {
                  "name": {"type": "string", "description": "exactly as in the tracker"},
                  "damage": _INT, "heal": _INT, "conditions_added": _NAMES, "conditions_removed": _NAMES,
                  "remove": {"type": "boolean", "description": "take it out of the fight (dead, fled, knocked out)"},
                  **_USES},
               "required": ["name"]})
        async def change_creature(a: dict[str, Any]) -> dict[str, Any]:
            def go(a: dict[str, Any]) -> str:
                self.fight, text = m.change_creature(self.fight, a)
                return text
            return self.run("fight", self.using(a, go))

        @tool("next_turn", "Start the next combatant's turn in initiative order (after add_combatants, the first "
              "combatant's) and show whose turn it is.",
              {"type": "object", "properties": {}})
        async def next_turn(a: dict[str, Any]) -> dict[str, Any]:
            def go() -> str:
                was = self.fight["round"] if self.fight else 0
                self.fight, text = m.next_turn(self.fight)
                if self.fight["round"] > was > 0:  # a round is 6 seconds; end_fight counts the last one
                    self.clock = m.advance(self.clock, 6)
                return text
            return self.run("fight", go)

        @tool("end_fight", "End the current fight.", {"type": "object", "properties": {}})
        async def end_fight(a: dict[str, Any]) -> dict[str, Any]:
            def go() -> str:
                rounds = self.fight["round"] if self.fight else 0
                self.fight, text = m.end_fight(self.fight)
                self.clock = m.advance(self.clock, 6)
                if self.clock["now"] is not None:
                    text += f" {m.span(rounds * 6)} of fighting; now {m.when(self.clock['now'])}."
                return text
            return self.run("fight", go)

        @tool("change_time", "The game clock and timers. Set the time once at the start (and to correct it), and move it on "
              "whenever time passes outside fights and rests (travel, searching, waiting, talking). Fights (6 seconds a "
              "round, counted as rounds start and when the fight ends), short rests (1 hour) and long rests (8 hours) move it "
              "by themselves. A timer counts down with the clock, e.g. a torch (1 hour) or a spell's duration; it doesn't "
              "end anything by itself and stays, shown as run out, until you remove it.",
              {"type": "object", "properties": {
                  "set": {"type": "object", "properties": {"day": {"type": "integer", "minimum": 1},
                                                           "time": {"type": "string", "description": "24-hour, e.g. 17:40"}},
                          "required": ["time"]},
                  "advance": {"type": "object", "properties": _span},
                  "add_timer": {"type": "object", "properties": {"name": {"type": "string", "description": "e.g. Torch (Brakka's)"},
                                                                 **_span}, "required": ["name"]},
                  "remove_timer": {"type": "string", "description": "a timer's name, exactly as in the status"}}})
        async def change_time(a: dict[str, Any]) -> dict[str, Any]:
            def go() -> str:
                self.clock, text = m.change_time(self.clock, a)
                return text
            return self.run("time", go)

        def record(a: dict[str, Any], text: str) -> None:
            self.transcript.append({"kind": "call", "tool": "lookup", "input": a, "result": text})
            self.save()

        # ---- the notebook (dm/lore.py): hidden from the player, recorded in the transcript as calls ----
        _texts = {"type": "array", "items": {"type": "string"}}

        @tool("write_lore", "Your notebook, hidden from the player: write down the world as you say it. An entry is a "
              "person, place, group, creature, item, event, god, legend... with a description and relationships "
              "(bullets; [[links]] to other entries; one bullet is one fact, and it shows on every entry it mentions). "
              "Every part is stamped with the turn. One call can: create an entry (create, kind, description, "
              "other_names, relationships); or change one (entry, with any of kind, description (rewrites it), "
              "add_to_description (keeps the old part), add_relationships, add_other_names, remove_other_names, "
              "rename); or change_relationship (its number, with text); or remove_relationship; or merge one entry "
              "into another (merge, into). A name or other name belongs to one entry only. An entry of kind quest (a "
              "goal the party has taken on) or lead (a rumour or hook not taken up) is shown at the top of every "
              "message while its status is open; with entry, status done or dropped ends that.",
              {"type": "object", "properties": {
                  "create": {"type": "string", "description": "a new entry's name, e.g. Vessa"},
                  "entry": {"type": "string", "description": "an existing entry, by its name or another name"},
                  "kind": {"type": "string", "description": "e.g. person, place, group, creature, item, event, god, legend"},
                  "other_names": {**_texts, "description": "with create: other names it goes by, e.g. the Fence"},
                  "description": {"type": "string", "description": "what it is; with entry: rewrites the whole description"},
                  "add_to_description": {"type": "string", "description": "with entry: added after the description, "
                                         "which is kept with its own turn"},
                  "relationships": {**_texts, "description": "with create: bullets, e.g. 'runs the [[Thieves Guild]] "
                                    "from the back of the [[Copper Kettle]]'"},
                  "add_relationships": {**_texts, "description": "with entry: more bullets"},
                  "add_other_names": _texts, "remove_other_names": _texts,
                  "rename": {"type": "string", "description": "with entry: its new name (the old one stays as an other name)"},
                  "change_relationship": {"type": "integer", "description": "a relationship's number, e.g. 7 for [7]"},
                  "text": {"type": "string", "description": "with change_relationship: its new wording"},
                  "remove_relationship": {"type": "integer"},
                  "status": {"type": "string", "enum": list(notebook.STATUSES), "description": "with entry: a quest's "
                             "or lead's, e.g. done when it's achieved; a new one is open"},
                  "merge": {"type": "string", "description": "an entry that turns out to be the same as into"},
                  "into": {"type": "string"}}})
        async def write_lore(a: dict[str, Any]) -> dict[str, Any]:
            before = self.lore

            def go() -> str:
                self.lore, text = notebook.write(self.lore, a, notebook.now(self.transcript))
                return text
            res = self.run("write_lore", go, hidden=True, inp=a)
            if not res.get("is_error"):  # the player sees that it happened, not what was written (owner, 2026-10-13)
                self.log("tool", notebook.shown(self.lore, a))
                party = {e for p in (self.sheet["name"], *(c["name"] for c in self.companions))
                         for e in (notebook.find(before, p), notebook.find(before, p.split()[0])) if e}
                said, names = notebook.answer(before, a, self.transcript, party | self.answered)
                self.answered |= set(names)
                if said:  # to the DM only
                    res["content"][0]["text"] += "\n\n" + said
                self.save()
            return res

        @tool("lore", "Look in your notebook. One name: the entry in full (description, when it was last mentioned in "
              "play, its relationships: those with something from the last turns first, then newest first, 10 at a "
              "time). Two names: how they're connected, directly or through one other entry.",
              {"type": "object", "properties": {
                  "names": {**_texts, "description": "one entry, or two"},
                  "page": {"type": "integer", "minimum": 1, "description": "the next 10 relationships: 2, 3..."}},
               "required": ["names"]})
        async def lore(a: dict[str, Any]) -> dict[str, Any]:
            return self.run("lore", lambda: notebook.look(self.lore, a.get("names") or [], self.transcript,
                                                           a.get("page") or 1), hidden=True, inp=a)

        @tool("recall", "Search the game so far, for what was actually said. search: one word, phrase or notebook "
              "entry (an entry finds its other names too), newest first; two: only the turns where both come up. "
              "turn: that turn word for word.",
              {"type": "object", "properties": {
                  "search": {**_texts, "description": "e.g. ['silver key'], ['Vessa', 'Thieves Guild']"},
                  "turn": {"type": "integer", "minimum": 0},
                  "page": {"type": "integer", "minimum": 1}}})
        async def recall(a: dict[str, Any]) -> dict[str, Any]:
            return self.run("recall", lambda: notebook.recall(self.lore, self.transcript, a.get("search"), a.get("turn"),
                                                              a.get("page") or 1), hidden=True, inp=a)

        return [self.after_reply(t) for t in (
            roll, change_pc, change_party, new_pc, roll_ability_scores, srd_options, level_up_options, level_up, add_combatants, change_creature,
            next_turn, end_fight, change_time, lookup_tool(record), write_lore, lore, recall)]

    def after_reply(self, t: Tool) -> Tool:
        """A tool called after the DM has written a full reply (owner, 2026-10-14): the call still counts, but a roll
        is refused (nothing it decides can be told), and what the DM writes after it is held back (turn()). The DM
        had been adding notes about the late call ("The clock now reads 5:57 PM") or writing its reply twice."""
        async def handler(a: dict[str, Any]) -> dict[str, Any]:
            if self.reply_len < FULL_REPLY:
                return await t.handler(a)
            self.late = True
            if t.name == "roll":
                self.transcript.append({"kind": "refused", "text": f"dice: called after the reply: {a.get('reason', '')}"})
                return {"content": [{"type": "text", "text": "REFUSED, nothing rolled: " + LATE}], "is_error": True}
            out = await t.handler(a)
            return out | {"content": [*out["content"], {"type": "text", "text": LATE}]}
        return Tool(t.name, t.description, t.input_schema, handler)


def sheet_text(s: dict[str, Any]) -> str:
    p = s.get("personality")
    about = ([f"Traits: {' '.join(p['traits'])}"] if p.get("traits") else []) + [
        f"{k.capitalize()}: {p[k]}" for k in ("ideal", "bond", "flaw") if p.get(k)] if isinstance(p, dict) else (
        [f"Personality: {p}"] if p else [])
    lines = [f"{s['name']}: {s['summary']}", *([f"Alignment: {s['alignment']}"] if s.get("alignment") else []), *about,
             *([f"Appearance: {s['appearance']}"] if s.get("appearance") else []),
             f"AC {s['ac']} ({s['ac_note']}); speed {s['speed']}; proficiency bonus +{s['proficiency_bonus']}",
             "Abilities: " + ", ".join(f"{k} {v}" for k, v in s["abilities"].items()),
             f"Saving throws: {s['saving_throws']}", f"Skills: {s['skills']}",
             f"Passive Perception {s['passive_perception']}; senses: {s['senses']}",
             f"Languages: {s['languages']}", f"Proficiencies: {s['proficiencies']}",
             "Attacks:", *(f"- {x}" for x in s["attacks"])]
    sp = s.get("spellcasting") or {}
    if sp.get("ability"):
        lines += [f"Spellcasting ({sp['ability']}): save DC {sp['save_dc']}, spell attack +{sp['attack_bonus']}",
                  "Cantrips: " + ", ".join(sp["cantrips"])]
        if sp.get("known"):
            lines.append("Spells known: " + ", ".join(sp["known"]))
        lines.append(sp["notes"] + (" Prepared spells and the spellbook are in the status." if "prepared" in sp else ""))
        lines += [f"{label}: " + ", ".join(sp[key]) for key, label in (
            ("always_prepared", "Always prepared"), ("magical_secrets", "Magical Secrets spells (any class)"),
            ("tome_cantrips", "Pact of the Tome cantrips (any class)"), ("spell_mastery", "Spell Mastery"),
            ("signature_spells", "Signature spells"), ("invocations", "Eldritch Invocations"),
            ("invocation_spells", "Spells from invocations"), ("book_rituals", "Book of Ancient Secrets rituals (cast only as rituals)"))
            if sp.get(key)]
        if sp.get("arcanum"):
            lines.append("Mystic Arcanum: " + ", ".join(f"level {lv}: {name}" for lv, name in sp["arcanum"].items()))
    if sp.get("racial_cantrips"):
        lines.append("Racial cantrips: " + ", ".join(sp["racial_cantrips"]))
    lines += ["Features:", *(f"- {x}" for x in s["features"])]
    return "\n".join(lines)


def system_prompt(sheet: dict[str, Any], companions: list[dict[str, Any]]) -> str:
    return ((HERE / "prompt.md").read_text(encoding="utf-8")
            + "\n\n## The player's character\n" + sheet_text(sheet)
            + "".join(f"\n\n## Companion: {c['name']}\n" + sheet_text(c) for c in companions)
            + "\n\n## The opening\n" + sheet["opening"])


# sent with every play turn, after the status (owner, 2026-10-11): the DM went from memory despite the prompt
RULES_REMINDER = (
    "[Rules] Follow the SRD rules to the letter, every step of every procedure. Never go from memory: before you use a "
    "spell (cantrips too), a creature's stat block, a condition, a feature, a trait or a rules section, its exact SRD "
    "text must already be in this conversation from a lookup. If it isn't, look it up first.")


# The DM's reply is held until its turn is over (owner, 2026-10-14). A reply under FULL_REPLY characters after tool
# calls is a stub ("Both are recorded on your sheet."): the DM drafted the answer in its thinking, made its calls, and
# never wrote it. The stub is replaced by asking once for the full reply. In 312 turns of play every reply with tool
# calls under 300 characters was a stub, and the shortest good one was 389.
FULL_REPLY = 300
LATE = ("Your reply has already gone to the player as written; nothing you write after it will be shown. Make all "
        "your tool calls before your reply.")
STUB_ASK = ('[Not from the player] Your reply this turn was only: "{}". Nothing has been shown to the player yet. '
            "Write your full reply to their last message now; it replaces that line.")
# A turn can stop before the reply is written (autoloop, 2026-10-16): a fight run on while the PC lay unconscious used
# up the 40 model calls of a reply, and the player saw only dice and tracker lines (2 of 180 rounds). The DM is asked
# once for the reply.
CUT_SHORT_ASK = ("[Not from the player] Your turn stopped before you wrote your reply ({}). The player has seen only "
                 "the game's lines since their last message. Write your full reply to it now.")


async def turn(game: Game | Creation, text: str) -> None:
    held: list[str] = []
    mark = [0]  # the transcript's length when text was last held

    def said(t: str) -> None:
        if isinstance(game, Creation):
            print("\n" + t)
            game.log("dm", t)
        elif game.late:  # written after a late tool call: kept in the save, never shown
            game.log("hidden", t)
        else:
            # Short text followed by tool calls was a note to itself, not the reply ("Miss. Next."; 2 in 180 rounds)
            if held and any(e["kind"] in ("tool", "call", "refused") for e in game.transcript[mark[0]:]):
                game.log("stub", "\n\n".join(held))  # kept in the save, never shown
                held.clear()
                game.reply_len = 0
            held.append(t)
            game.reply_len += len(t)
            mark[0] = len(game.transcript)
    if isinstance(game, Game):
        game.reply_len, game.late, game.answered = 0, False, set()
        # The instructions hold the full sheets: after a level-up, or a companion joining or leaving, they are built
        # again (owner, 2026-10-13), and the owner's version reconnects to carry them. The whole conversation is then
        # read at full price once.
        system = system_prompt(game.sheet, game.companions)
        if system != game.system:
            game.system = system
            if game.sdk:
                await reconnect(game)
        party = (game.sheet["name"], *(c["name"] for c in game.companions))
        game.lore, notes = notebook.notes(game.lore, game.transcript, party)
        text = f"[Status now]\n{game.status()}\n\n{notes}\n\n{RULES_REMINDER}\n\n{text}"
        if (game.story or game.rebuild) and not (game.session_id if game.sdk else game.messages):
            text = so_far(game) + "\n\n" + text  # a new conversation after a cut, or a fork from before one
    start = len(game.transcript)
    edits: list[tuple[str, str]] = []  # (old, new) text the DM's conversation takes back: a trimmed status line
    failed = await ask(game, text, said)
    if isinstance(game, Game):
        tools = any(e["kind"] in ("tool", "call", "refused") for e in game.transcript[start:])
        if failed:
            game.log("failed", failed)  # kept in the save, never shown
        if failed and tools and game.reply_len < FULL_REPLY:
            if held:
                game.log("stub", "\n\n".join(held))
            held[:], game.reply_len = [], 0
            failed = await ask(game, CUT_SHORT_ASK.format(failed), said)
            if failed:
                game.log("failed", failed)
        elif not failed and tools and game.reply_len < FULL_REPLY:
            stub = "\n\n".join(held)
            game.log("stub", stub)  # kept in the save, never shown
            held[:], game.reply_len = [], 0
            failed = await ask(game, STUB_ASK.format(stub), said)
        player = next((e["text"] for e in reversed(game.transcript) if e["kind"] == "player"), "")
        trimmed = ""
        if held:
            new, trimmed = branch.without_stat_line(held[-1], player)
            if trimmed:
                edits.append((held[-1], new))
                held[-1] = new
        for t in held:
            print("\n" + t)
            game.log("dm", t)
        if trimmed:
            game.log("trimmed", trimmed)  # kept in the save, never shown
    if failed:
        print(f"\n[the DM call failed: {failed}]")
    if edits and isinstance(game, Game):
        await edit_conversation(game, edits)
    game.save()
    if isinstance(game, Game) and not failed and game.size >= CUT_AT:
        await cut(game)


async def ask(game: Game | Creation, text: str, on_text: Callable[[str], None]) -> str | None:
    """One message to the DM, and its whole reply. Returns None, or why the call failed."""
    if game.sdk:  # the owner's own version, on their Claude login (dm/sdk.py)
        failed = await game.sdk.respond(text, on_text)
        if getattr(game, "fork_at", None) and game.sdk.session_id != game.session_id:
            game.fork_at = None  # the fork is made: from now on it's a conversation of its own
        game.session_id, game.size = game.sdk.session_id, game.sdk.size
        return failed
    return await model.respond(game.model, game.system, game.tools(), game.messages, text, on_text, game.save,
                               lambda n: setattr(game, "size", n))


# Cutting the conversation short (owner, 2026-10-13): once it reaches CUT_AT tokens, the DM writes the story so far up
# to the last KEEP turns, and a new conversation starts with that summary and those turns word for word. The notebook
# and recall are unchanged; what was looked up before the cut is looked up again when it's needed.
CUT_AT = 200_000
KEEP = 20

SUMMARY_ASK = (
    "[Not from the player: your notes, which the player never sees] This conversation is about to be cut short. The "
    "next one will start with what you write now, then turns {first} to {last} word for word, then the player's next "
    "message. Everything else in this conversation will be gone: earlier turns, lookups and tool results (the "
    "notebook stays as it is, and the instructions and sheets come as they do now).\n\n"
    "Write the story so far, from the start of the game to the end of turn {end}: what happened, in order, with the "
    "names, numbers and words that may matter again; where things stand at the end of turn {end}; what each "
    "character who matters knows, wants, promised or owes; the open threads and plans; and what you've decided "
    "that hasn't come out in play yet, so you keep it the same. Plain text, no tools, nothing to the player.")


def so_far(game: Game) -> str:
    """The opening of a conversation after a cut: the DM's summary, and the turns after it word for word, up to the
    player's line now being sent. With no summary yet (a fork from before the first cut), every turn word for word."""
    now = notebook.now(game.transcript)
    end = game.story[-1]["turn"] if game.story else -1
    turns = "\n\n".join(t for n in range(end + 1, now) if (t := notebook.turn_text(game.transcript, n)))
    if not game.story:
        return f"[The game so far, word for word: turns 0 to {now - 1}]\n{turns}"
    return (f"[The story so far: your own summary of turns 0 to {end}, written when the conversation was cut short]\n"
            f"{game.story[-1]['text']}\n\n[Turns {end + 1} to {now - 1}, word for word]\n{turns}")


async def reconnect(game: Game) -> None:
    """An SDK game's Claude Code conversation, opened again: after its instructions changed or its session file was
    edited (Claude Code keeps the conversation in memory while it's open)."""
    from dm import sdk  # here: the browser has no Agent SDK
    await game.sdk.close()
    game.sdk = sdk.Client(game.model, game.system, game.tools(), game.cwd, game.session_id, game.fork_at)
    await game.sdk.open()


async def edit_conversation(game: Game, pairs: list[tuple[str, str]]) -> None:
    """The DM's conversation takes each old text back for its new one (dm/branch.py)."""
    branch.edit_conversation(game, pairs)
    if game.sdk:
        await reconnect(game)


async def cut(game: Game) -> None:
    """Ask the DM for the story so far, then start a new conversation. If that fails, nothing changes, and the next
    turn tries again."""
    last = notebook.now(game.transcript)
    end = last - KEEP
    if end < 0:
        return
    parts: list[str] = []
    failed = await ask(game, SUMMARY_ASK.format(first=end + 1, last=last, end=end), parts.append)
    summary = "\n\n".join(parts).strip()
    if failed or not summary:
        print(f"\n[the conversation couldn't be shortened: {failed or 'no summary'}; trying again next turn]")
        return
    game.story.append({"turn": end, "text": summary})
    game.log("tool", f"conversation shortened: the DM's summary of turns 0 to {end}, then turns {end + 1} to {last}")
    if game.sdk:
        from dm import sdk  # here: the browser has no Agent SDK
        await game.sdk.close()
        game.session_id = None
        game.sdk = sdk.Client(game.model, game.system, game.tools(), game.cwd, None)
        await game.sdk.open()
    else:
        game.messages = []
    game.size = 0
    game.save()


class Creation:
    """The DM talks the player through making a level-1 character; create.py checks the choices and does the math."""

    def __init__(self, path: Path) -> None:
        self.rolled: list[int] | None = None
        self.draft: dict[str, Any] | None = None
        self.done = False
        self.messages: list[dict[str, Any]] = []
        self.transcript: list[dict[str, Any]] = []
        self.path = path
        self.model = MODEL
        self.system = (HERE / "create_prompt.md").read_text(encoding="utf-8")
        self.backend = "api"
        self.session_id: str | None = None
        self.sdk: Any = None

    def log(self, kind: str, text: str) -> None:
        self.transcript.append({"kind": kind, "text": text})

    def save(self) -> None:  # creation can't be resumed; the save keeps its transcript, and play continues the file
        self.path.write_text(json.dumps({"creation_only": True, "transcript": self.transcript}, indent=1,
                                        ensure_ascii=False), encoding="utf-8")

    def tools(self) -> list[Any]:
        def answer(name: str, a: dict[str, Any], text: str, error: bool = False, show: str = "") -> dict[str, Any]:
            """Record the call and its full result, so creation can be traced later."""
            self.transcript.append({"kind": "call", "tool": name, "input": a, "result": text, "error": error})
            if show:
                print(f"  [{show}]")
            self.save()
            return {"content": [{"type": "text", "text": text}]} | ({"is_error": True} if error else {})

        @tool("srd_options", "What the SRD offers. No arguments: every race, class and the background. race only: that "
              "race in full. class only: that class in full. race and class: every choice that character needs, "
              "with ids, options and spell lists.",
              {"type": "object", "properties": {"race": {"type": "string"}, "class": {"type": "string"}}})
        async def srd_options(a: dict[str, Any]) -> dict[str, Any]:
            try:
                return answer("srd_options", a, create.options_text(a.get("race") or "", a.get("class") or ""))
            except create.Bad as e:
                return answer("srd_options", a, str(e), True)

        @tool("roll_ability_scores", "Roll the six ability scores: 4d6, drop the lowest, six times. Once per "
              "character; the player sees every die.", {"type": "object", "properties": {}})
        async def roll_ability_scores(a: dict[str, Any]) -> dict[str, Any]:
            if self.rolled:
                return answer("roll_ability_scores", a, f"already rolled: {self.rolled}; scores are rolled once", True)
            lines, rolled = [], []
            for _ in range(6):
                dice = sorted(m.roll("4d6")["parts"][0]["rolls"], reverse=True)
                rolled.append(sum(dice[:3]))
                lines.append(f"4d6 {dice} drop {dice[3]} = {rolled[-1]}")
            self.rolled = rolled
            text = "ability scores rolled: " + "; ".join(lines) + f". Scores: {rolled}"
            return answer("roll_ability_scores", a, text, show=text)

        @tool("build_character", "Check a full set of choices and work out the sheet. Returns the sheet, or every "
              "problem at once. Fields: name, race, class, ability_method (standard_array, point_buy or rolled), "
              "base_scores {STR..CHA} before racial increases, choices {id: [entries]} with the ids from srd_options "
              "(each entry an option letter or exact name, or {option, picks} for an option with a further choice), "
              "cantrips, spells (known or spellbook), prepared, and optional alignment, personality (text, or {traits: "
              "[...], ideal, bond, flaw}), appearance.",
              {"type": "object", "properties": {"character": {"type": "object"}}, "required": ["character"]})
        async def build_character(a: dict[str, Any]) -> dict[str, Any]:
            sheet, errs = create.build(a["character"], self.rolled)
            if not sheet:
                return answer("build_character", a, "NOT BUILT. Problems:\n- " + "\n- ".join(errs), True)
            self.draft = sheet
            return answer("build_character", a, "BUILT. Show the player this sheet and ask for a yes before "
                          "finish_character:\n" + sheet_text(sheet) + "\n" + m.status(sheet),
                          show=f"built {sheet['name']}, {sheet['summary']}")

        @tool("finish_character", "After the player has said yes to the built sheet: write the one-paragraph "
              "opening that starts their adventure. Play begins with it.",
              {"type": "object", "properties": {"opening": {"type": "string"}}, "required": ["opening"]})
        async def finish_character(a: dict[str, Any]) -> dict[str, Any]:
            if not self.draft:
                return answer("finish_character", a, "no character built yet: use build_character", True)
            if not str(a.get("opening") or "").strip():
                return answer("finish_character", a, "the opening is empty", True)
            self.draft["opening"] = a["opening"].strip()
            self.done = True
            # asking for silence after a tool call made the model repeat the call (8 of 16 replays); one exact line: 0 of 16
            return answer("finish_character", a, 'Done. Now reply with exactly this line and nothing else: '
                          '"Your character is complete."')

        def record(a: dict[str, Any], text: str) -> None:
            answer("lookup", a, text)

        return [srd_options, roll_ability_scores, build_character, finish_character, lookup_tool(record)]


def new_save(stem: str) -> Path:
    """A save file no other game has: two games started in the same second get stem.json and stem-2.json. The file
    is created here, so a second game can't pick the same name before the first one's first save."""
    SAVES.mkdir(exist_ok=True)
    n = 1
    while True:
        path = SAVES / (f"{stem}-{n}.json" if n > 1 else f"{stem}.json")
        try:
            path.open("x").close()
            return path
        except FileExistsError:
            n += 1



class Session:
    """One game, fed one line at a time. The terminal and the browser page both drive it: what the game says is
    printed, and the player's lines come in through line(). backend: "sdk" (the owner's own, on their Claude login)
    or "api" (an API key; the browser's)."""

    def __init__(self, model_name: str = MODEL, backend: str = "api") -> None:
        self.model = model_name
        self.backend = backend
        self.game: Game | None = None
        self.creation: Creation | None = None

    async def connect(self, g: Game | Creation) -> None:
        """An SDK game talks to one Claude Code conversation for as long as it's played."""
        if g.backend != "sdk":
            return
        from dm import sdk  # here: the browser has no Agent SDK
        if isinstance(g, Game) and not g.session_id:
            g.cwd = str(sdk.DM_HOME)
        g.sdk = sdk.Client(g.model, g.system, g.tools(), g.cwd if isinstance(g, Game) else str(sdk.DM_HOME),
                           g.session_id, getattr(g, "fork_at", None))
        await g.sdk.open()

    async def close(self) -> None:
        for g in (self.creation, self.game):
            if g and g.sdk:
                await g.sdk.close()
                g.sdk = None

    async def new(self, character: str) -> None:
        """character: fighter, rogue or wizard (ready-made), or new (made with the DM first)."""
        stamp = time.strftime("%Y%m%d-%H%M%S")
        if character == "new":
            self.creation = Creation(new_save(f"new-{stamp}"))  # one file: creation, then play
            self.creation.model, self.creation.backend = self.model, self.backend
            await self.connect(self.creation)
            print("Character creation. Talk to the DM; /quit exits.")
            await turn(self.creation, "[Start] Greet the player and begin making their character.")
            return
        sheet = json.loads((HERE / "characters" / f"{character}.json").read_text(encoding="utf-8"))
        name = sheet["name"].split()[0].lower()
        await self.play(Game({"sheet": sheet, "model": self.model, "backend": self.backend}, new_save(f"{name}-{stamp}")))

    async def play(self, game: Game, show_last: bool = True) -> None:
        await self.close()
        self.game, self.creation = game, None
        game.system = system_prompt(game.sheet, game.companions)
        await self.connect(game)
        print(f"{game.sheet['name']}, {game.sheet['summary']}. Saving to {game.path}. /sheet shows your sheet, "
              "/back lets you go back, /quit exits.")
        if game.messages or game.session_id or game.story or game.rebuild:
            last = next((t["text"] for t in reversed(game.transcript) if t["kind"] == "dm"), "")
            if show_last:
                print("\n" + last)
        else:
            await turn(game, "[Start] Begin the session. Begin with a short introduction before the first scene: a few "
                             "sentences on the world and region, who the character is and how they came to be here. "
                             "Then open the scene and ask what "
                             f"{game.sheet['name'].split()[0]} does.")

    async def line(self, line: str) -> bool:
        """The player's line. False once the game is over (the player quit)."""
        line = line.strip()
        if not line:
            return True
        if c := self.creation:
            if line == "/quit":
                await self.close()
                return False
            c.log("player", line)
            await turn(c, line)
            if c.done:
                assert c.draft
                await self.play(Game({"sheet": c.draft, "model": c.model, "transcript": c.transcript,
                                      "backend": c.backend}, c.path))
            return True
        game = self.game
        assert game
        if line == "/quit":
            game.save()
            await self.close()
            print(f"Saved. Continue with: py -3.12 -m dm.play --resume {game.path}")
            return False
        if line == "/sheet":
            print(sheet_report(game))
            return True
        if line == "/back" or line.startswith(("/redo", "/edit")):
            await self.back(game, line)
            return True
        game.snapshots.append(branch.snapshot(game))
        game.log("player", line)
        await turn(game, f"[The player]\n{line}")
        return True

    async def back(self, game: Game, line: str) -> None:
        """Going back (dm/branch.py). /back lists the lines you can send again. /redo <turn> [line]: the game as it
        was just before your line of that turn, in a new save, and that line sent again (or the one given instead).
        /edit <text>: the DM's latest reply becomes text (\\n for a new paragraph), and the DM reads it from now on;
        what the reply did to the sheet, clock and notebook stays."""
        cmd, _, rest = line.partition(" ")
        if cmd == "/back":
            found = branch.lines(game)
            print("\n".join(f"  {t}: {x}" for t, x in found[-20:]) or "  nothing yet")
            print("/redo <turn> sends that line again (/redo <turn> <new line> sends a different one), in a new save; "
                  "/edit <text> rewrites the DM's latest reply.")
            return
        if cmd == "/edit":
            try:
                pairs = branch.edit_transcript(game, rest.replace("\\n", "\n"))
            except LookupError as e:
                print(f"[{e}]")
                return
            await edit_conversation(game, pairs)
            game.save()
            # the web pages redraw the reply from the first line on (dm/web.html, page.html)
            print("[the DM's reply, as you edited it:]")
            print("\n" + pairs[0][1])
            print("\n[the DM reads your version from now on; the sheet, clock and notebook stay as they are]")
            return
        num, _, new = rest.strip().partition(" ")
        try:
            data = branch.fork_data(game, int(num))
        except (LookupError, ValueError) as e:
            print(f"[{e if isinstance(e, LookupError) else 'which turn? /back lists them'}]")
            return
        again = new.strip() or next(x for t, x in branch.lines(game) if t == int(num))
        game.save()
        fork = Game(data, new_save(f"{game.path.stem.split('-fork')[0]}-fork"))
        print(f"[going back to turn {num}; {game.path.name} stays as it was]")
        await self.play(fork, show_last=False)
        print("\n> " + again)  # as if typed: the web pages show it as the player's line
        await self.line(again)


def sheet_report(game: Game) -> str:
    """What /sheet shows: the PC's part as before (the web page lays it out as one card); companions after it."""
    return (sheet_text(game.sheet) + "\n" + m.clock_text(game.clock) + "\n" + m.status(game.sheet) + "\n"
            + m.fight_text(game.fight, game.sheet, game.companions)
            + "".join(f"\n\nCompanion {sheet_text(c)}\n{m.status(c)}" for c in game.companions))


def resumable(data: dict[str, Any], backend: str = "") -> str:
    """Why a save can't be continued, or "" if it can. backend: the only one this player can run, if that matters
    (the browser page runs only API saves)."""
    if "sheet" not in data:
        return "that save stopped during character creation, which can't be resumed; start again with new"
    kind = data.get("backend") or ("sdk" if data.get("session_id") else "api")
    if backend and kind != backend:
        return ("that save runs on the owner's own version (the Agent SDK); to play it here, convert it first with "
                "py -3.12 -m dm.convert <save>")
    return ""


def history(data: dict[str, Any]) -> str:
    """The game so far, from a save, in the shape the terminal printed it. Continuing a save prints only the DM's
    last reply, so that one is left out here."""
    t = data.get("transcript", [])
    last = max((i for i, e in enumerate(t) if e["kind"] == "dm"), default=-1)
    text = ""
    for i, e in enumerate(t):
        if e["kind"] == "dm" and i != last:
            text += f"\n{e['text']}\n"
        elif e["kind"] == "player":
            text += f"\n> {e['text']}\n"
        elif e["kind"] == "tool":
            text += f"  [{e['text']}]\n"
        elif e["kind"] == "call" and e["tool"] == "roll_ability_scores" and not e["error"]:
            text += f"  [{e['result']}]\n"
    return text


async def main() -> None:
    ap = argparse.ArgumentParser(description="Play with the AI DM.")
    ap.add_argument("character", nargs="?", choices=("fighter", "rogue", "wizard", "new"))
    ap.add_argument("--resume", type=Path, help="a save file to continue")
    ap.add_argument("--model", default=MODEL)
    ap.add_argument("--api", action="store_true", help="a new game on the API (ANTHROPIC_API_KEY) instead of your "
                                                       "Claude login; a save carries on the way it was started")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    session = Session(args.model, "api" if args.api else "sdk")
    if args.resume:
        data = json.loads(args.resume.read_text(encoding="utf-8"))
        if why := resumable(data):
            ap.error(why)
        await session.play(Game(data, args.resume))
    elif args.character:
        await session.new(args.character)
    else:
        ap.error("pick a character (fighter, rogue, wizard), make one (new), or --resume a save")
    while await session.line(await asyncio.to_thread(input, "\n> ")):
        pass


if __name__ == "__main__":
    asyncio.run(main())
