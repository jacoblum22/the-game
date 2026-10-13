"""Play D&D 5e (2014, SRD) in the terminal with an AI DM.

    py -3.12 -m dm.play fighter            # or rogue, wizard
    py -3.12 -m dm.play new                # make a character with the DM first
    py -3.12 -m dm.play --resume saves/<file>.json

In play: type what your character does. /sheet shows your sheet, /quit saves and exits.
The DM runs through the Claude Code CLI on your Claude login (Claude Agent SDK).
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ResultMessage,
    TextBlock,
    create_sdk_mcp_server,
    tool,
)

from dm import create, lookup
from dm import mechanics as m

HERE = Path(__file__).parent
SAVES = HERE.parent / "saves"
MODEL = "claude-sonnet-5-5"
# The Claude Code program adds its own notes to every session. Run the DM outside any git repo (no git or worktree
# notes) and switch off the notes that have switches: the developer's memory, CLAUDE.md files, the token count and
# the mid-turn "the user hasn't heard from you in a while" nudge.
DM_HOME = Path.home() / "AppData" / "Local" / "the-game-dm"
DM_ENV = {"CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1", "CLAUDE_CODE_DISABLE_CLAUDE_MDS": "1",
          "CLAUDE_CODE_TOTAL_TOKENS_REMINDER": "off", "CLAUDE_CODE_DISABLE_GIT_INSTRUCTIONS": "1",
          "CLAUDE_CODE_SILENT_TURN_REMINDER": "0"}


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


def dm_options(cwd: str, **kw: Any) -> ClaudeAgentOptions:
    Path(cwd).mkdir(parents=True, exist_ok=True)
    return ClaudeAgentOptions(tools=[], setting_sources=[], strict_mcp_config=True, max_turns=40, cwd=cwd, env=DM_ENV, **kw)

_INT = {"type": "integer", "minimum": 0}
_ITEMS = {"type": "array", "items": {"type": "object", "properties": {"item": {"type": "string"},
                                                                      "qty": {"type": "integer", "minimum": 1}},
                                     "required": ["item"]}}
_NAMES = {"type": "array", "items": {"type": "string"}}
_WHO = {"type": "string", "description": "a companion's name; leave out for the player character"}


class Game:
    def __init__(self, data: dict[str, Any], path: Path) -> None:
        self.sheet: dict[str, Any] = data["sheet"]
        self.companions: list[dict[str, Any]] = data.get("companions", [])  # full sheets, at most 2 (owner 2026-10-12)
        self.fight: dict[str, Any] | None = data.get("fight")
        self.clock: dict[str, Any] = data.get("clock") or m.new_clock()  # saves from before 2026-10-12 have none
        self.session_id: str | None = data.get("session_id")
        self.transcript: list[dict[str, Any]] = data.get("transcript", [])
        self.model: str = data.get("model", MODEL)
        self.cwd: str = data.get("cwd", str(SAVES))  # where the DM's session lives; saves from before 2026-10-11 used saves/
        self.path = path

    def save(self) -> None:
        self.path.parent.mkdir(exist_ok=True)
        data = {"sheet": self.sheet, "companions": self.companions, "fight": self.fight, "clock": self.clock, "session_id": self.session_id, "model": self.model,
                "cwd": self.cwd, "transcript": self.transcript}
        self.path.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")

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
        rest = 8 * 3600 if a.get("long_rest") else 3600 if a.get("short_rest") else 0
        if i is not None:
            if rest:
                raise m.Refused("rests are the whole party's: pass short_rest or long_rest without who (companions' "
                              "end-of-rest choices go in companions)")
            if a.get("xp_gained"):
                raise m.Refused("companions have no XP: they are at the PC's level and level up when the PC does")
            self.companions[i], lines = m.change_pc(self.companions[i], a)
            return f"{self.companions[i]['name']}: " + "; ".join(lines)
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
        self.companions.append(sheet)
        return f"{sheet['name']} joined the party, {sheet['summary']}" + (
            f". The PC is level {self.sheet['level']}: level them up to it with level_up_options and level_up, who "
            f"{sheet['name']!r}" if self.sheet["level"] > 1 else "")

    # ---- tools: each runs a mechanics function, records the result, and tells the DM what happened ----

    def run(self, label: str, fn: Callable[[], str]) -> dict[str, Any]:
        try:
            text = fn()
        except m.Refused as e:
            self.transcript.append({"kind": "refused", "text": f"{label}: {e}"})
            return {"content": [{"type": "text", "text": f"REFUSED, nothing changed: {e}"}], "is_error": True}
        self.log("tool", f"{label}: {text}" if label != "dice" else text)
        self.save()
        return {"content": [{"type": "text", "text": text}]}

    def tools(self) -> list[Any]:
        @tool("roll", "Roll dice, e.g. 1d20+5 or 2d6+3. The player sees every roll.",
              {"type": "object", "properties": {
                  "dice": {"type": "string", "description": "dice expression, e.g. 1d20+4, 2d8+3, 1d4+1d6"},
                  "reason": {"type": "string", "description": "what the roll is for, e.g. 'Brakka's Athletics check, DC 15'"},
                  "mode": {"type": "string", "enum": ["normal", "advantage", "disadvantage"]}},
               "required": ["dice", "reason"]})
        async def roll(a: dict[str, Any]) -> dict[str, Any]:
            return self.run("dice", lambda: "dice " + m.roll_text(m.roll(a["dice"], a.get("mode") or "normal"), a["reason"]))

        @tool("change_pc", "Record a change to the sheet of the player character, or of a companion (who). Pass only the "
              "fields that change. A rest is the whole party's: pass it without who; it rests every companion too and "
              "moves the clock once. "
              "All-or-nothing: if any part is impossible, nothing is applied and the reason is returned. "
              "Rules you must apply yourself: a long rest needs the PC at 1 HP or more and only one long rest counts per "
              "24 hours (check the time; the tool can't); hit dice are spent at the end of a short rest, one per call.",
              {"type": "object", "properties": {
                  "who": _WHO,
                  "damage": _INT, "heal": _INT, "temp_hp": _INT,
                  "critical_hit": {"type": "boolean", "description": "the damage is from a critical hit (any hit on an unconscious "
                                   "PC from within 5 feet is one): at 0 HP that is two death save failures instead of one"},
                  "hit_dice_spent": {"type": "integer", "minimum": 0,
                                     "description": "1 = spend one hit die at the end of a short rest; the result says what to roll, "
                                     "then pass the total as heal. The player decides after each roll whether to spend another"},
                  "death_save_successes": _INT, "death_save_failures": _INT,
                  "spend_slot": {"type": "integer", "minimum": 1, "maximum": 9, "description": "spell slot level spent"},
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
                                 "end-of-rest choices, {name: {prepare_spells, resilience_type}}"}}})
        async def change_pc(a: dict[str, Any]) -> dict[str, Any]:
            return self.run("sheet", lambda: self.change_party_member(a))

        @tool("change_party", "A companion joins or leaves the party (the PC and at most 2 companions). add: the "
              "companion's full set of level-1 choices, in the form build_character takes (name, race, class, "
              "ability_method standard_array, base_scores, choices, cantrips, spells, prepared, alignment, personality, "
              "appearance); srd_options gives the ids. Then level_up them (who) to the PC's level. remove: a companion's "
              "name, when they leave or die.",
              {"type": "object", "properties": {"add": {"type": "object"}, "remove": {"type": "string"}}})
        async def change_party(a: dict[str, Any]) -> dict[str, Any]:
            res = self.run("party", lambda: self.change_party(a))
            if a.get("add") and not res.get("is_error"):
                res["content"][0]["text"] += "\n\nTheir sheet:\n" + sheet_text(self.companions[-1])
            return res

        @tool("srd_options", "What the SRD offers, for building a companion. No arguments: every race, class and the "
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
                                                           "record, in the form level_up_options ends with"}},
               "required": ["record"]})
        async def level_up(a: dict[str, Any]) -> dict[str, Any]:
            done: list[dict[str, Any]] = []

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
                    self.companions[i], text = m.level_up(self.companions[i], record, cap=self.sheet["level"])
                    done.append(self.companions[i])
                return text
            res = self.run("level up", go)
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
                  "remove": {"type": "boolean", "description": "take it out of the fight (dead, fled, knocked out)"}},
               "required": ["name"]})
        async def change_creature(a: dict[str, Any]) -> dict[str, Any]:
            def go() -> str:
                self.fight, text = m.change_creature(self.fight, a)
                return text
            return self.run("fight", go)

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

        _span = {k: _INT for k in ("days", "hours", "minutes", "seconds")}

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

        return [roll, change_pc, change_party, srd_options, level_up_options, level_up, add_combatants, change_creature,
                next_turn, end_fight, change_time, lookup_tool(record)]


def sheet_text(s: dict[str, Any]) -> str:
    lines = [f"{s['name']}: {s['summary']}",
             *(f"{k.capitalize()}: {s[k]}" for k in ("alignment", "personality", "appearance") if s.get(k)),
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


async def turn(client: ClaudeSDKClient, game: Game | Creation, text: str) -> None:
    await client.query(f"[Status now]\n{game.status()}\n\n{RULES_REMINDER}\n\n{text}" if isinstance(game, Game) else text)
    async for msg in client.receive_response():
        if isinstance(msg, AssistantMessage):
            for b in msg.content:
                if isinstance(b, TextBlock) and b.text.strip():
                    print("\n" + b.text.strip())
                    game.log("dm", b.text.strip())
        elif isinstance(msg, ResultMessage):
            game.session_id = msg.session_id
            if msg.is_error:
                print(f"\n[the DM call failed: {msg.result or msg.errors}]")
    game.save()


class Creation:
    """The DM talks the player through making a level-1 character; create.py checks the choices and does the math."""

    def __init__(self, path: Path) -> None:
        self.rolled: list[int] | None = None
        self.draft: dict[str, Any] | None = None
        self.done = False
        self.session_id: str | None = None
        self.transcript: list[dict[str, Any]] = []
        self.path = path

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
              "cantrips, spells (known or spellbook), prepared, and optional alignment, personality, appearance.",
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


async def create_character(model: str, path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Returns the finished sheet and the creation transcript, which the play save continues."""
    c = Creation(path)
    server = create_sdk_mcp_server("dm", tools=c.tools())
    opts = dm_options(
        str(DM_HOME), system_prompt=(HERE / "create_prompt.md").read_text(encoding="utf-8"), model=model,
        mcp_servers={"dm": server},
        allowed_tools=[f"mcp__dm__{n}" for n in ("srd_options", "roll_ability_scores", "build_character",
                                                 "finish_character", "lookup")])
    print("Character creation. Talk to the DM; /quit exits.")
    async with ClaudeSDKClient(options=opts) as client:
        await turn(client, c, "[Start] Greet the player and begin making their character.")
        while not c.done:
            line = (await asyncio.to_thread(input, "\n> ")).strip()
            if line == "/quit":
                sys.exit(0)
            if line:
                c.log("player", line)
                await turn(client, c, line)
    assert c.draft
    return c.draft, c.transcript


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


async def main() -> None:
    ap = argparse.ArgumentParser(description="Play with the AI DM.")
    ap.add_argument("character", nargs="?", choices=("fighter", "rogue", "wizard", "new"))
    ap.add_argument("--resume", type=Path, help="a save file to continue")
    ap.add_argument("--model", default=MODEL)
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    stamp = time.strftime("%Y%m%d-%H%M%S")
    if args.resume:
        data = json.loads(args.resume.read_text(encoding="utf-8"))
        if "sheet" not in data:
            ap.error("that save stopped during character creation, which can't be resumed; start again with new")
        game = Game(data, args.resume)
    elif args.character == "new":
        path = new_save(f"new-{stamp}")  # one file: creation, then play
        sheet, transcript = await create_character(args.model, path)
        game = Game({"sheet": sheet, "model": args.model, "transcript": transcript, "cwd": str(DM_HOME)}, path)
    elif args.character:
        sheet = json.loads((HERE / "characters" / f"{args.character}.json").read_text(encoding="utf-8"))
        name = sheet["name"].split()[0].lower()
        game = Game({"sheet": sheet, "model": args.model, "cwd": str(DM_HOME)}, new_save(f"{name}-{stamp}"))
    else:
        ap.error("pick a character (fighter, rogue, wizard), make one (new), or --resume a save")

    server = create_sdk_mcp_server("dm", tools=game.tools())
    SAVES.mkdir(exist_ok=True)
    opts = dm_options(
        game.cwd, system_prompt=system_prompt(game.sheet, game.companions), model=game.model, mcp_servers={"dm": server},
        allowed_tools=[f"mcp__dm__{n}" for n in ("roll", "change_pc", "change_party", "srd_options", "level_up_options", "level_up",
                                                 "add_combatants",
                                                 "change_creature", "next_turn", "end_fight", "change_time", "lookup")],
        resume=game.session_id)
    print(f"{game.sheet['name']}, {game.sheet['summary']}. Saving to {game.path}. /sheet shows your sheet, /quit exits.")
    async with ClaudeSDKClient(options=opts) as client:
        if game.session_id:
            last = next((t["text"] for t in reversed(game.transcript) if t["kind"] == "dm"), "")
            print("\n" + last)
        else:
            await turn(client, game, "[Start] Begin the session: set the opening scene for the player, then ask what "
                                     f"{game.sheet['name'].split()[0]} does.")
        while True:
            line = (await asyncio.to_thread(input, "\n> ")).strip()
            if not line:
                continue
            if line == "/quit":
                game.save()
                print(f"Saved. Continue with: py -3.12 -m dm.play --resume {game.path}")
                return
            if line == "/sheet":
                # the PC's part as before (the web page lays it out as one card); companions after it
                print(sheet_text(game.sheet) + "\n" + m.clock_text(game.clock) + "\n" + m.status(game.sheet) + "\n"
                      + m.fight_text(game.fight, game.sheet, game.companions)
                      + "".join(f"\n\nCompanion {sheet_text(c)}\n{m.status(c)}" for c in game.companions))
                continue
            game.log("player", line)
            await turn(client, game, f"[The player]\n{line}")


if __name__ == "__main__":
    asyncio.run(main())
