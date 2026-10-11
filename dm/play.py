"""Play D&D 5e (2014, SRD) in the terminal with an AI DM.

    py -3.12 -m dm.play fighter            # or rogue, wizard
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
from pathlib import Path
from typing import Any, Callable

from claude_agent_sdk import (AssistantMessage, ClaudeAgentOptions, ClaudeSDKClient, ResultMessage, TextBlock,
                              create_sdk_mcp_server, tool)

from dm import mechanics as m

HERE = Path(__file__).parent
SAVES = HERE.parent / "saves"
MODEL = "claude-sonnet-5-5"

_INT = {"type": "integer", "minimum": 0}
_ITEMS = {"type": "array", "items": {"type": "object", "properties": {"item": {"type": "string"},
                                                                      "qty": {"type": "integer", "minimum": 1}},
                                     "required": ["item"]}}
_NAMES = {"type": "array", "items": {"type": "string"}}


class Game:
    def __init__(self, data: dict[str, Any], path: Path) -> None:
        self.sheet: dict[str, Any] = data["sheet"]
        self.fight: dict[str, Any] | None = data.get("fight")
        self.session_id: str | None = data.get("session_id")
        self.transcript: list[dict[str, str]] = data.get("transcript", [])
        self.model: str = data.get("model", MODEL)
        self.path = path

    def save(self) -> None:
        self.path.parent.mkdir(exist_ok=True)
        data = {"sheet": self.sheet, "fight": self.fight, "session_id": self.session_id, "model": self.model,
                "transcript": self.transcript}
        self.path.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")

    def log(self, kind: str, text: str) -> None:
        self.transcript.append({"kind": kind, "text": text})
        if kind == "tool":
            print(f"  [{text}]")

    def status(self) -> str:
        return m.status(self.sheet) + "\n" + m.fight_text(self.fight, self.sheet)

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

        @tool("change_pc", "Record a change to the player character's sheet. Pass only the fields that change. "
              "All-or-nothing: if any part is impossible, nothing is applied and the reason is returned.",
              {"type": "object", "properties": {
                  "damage": _INT, "heal": _INT, "temp_hp": _INT,
                  "hit_dice_spent": _INT, "death_save_successes": _INT, "death_save_failures": _INT,
                  "spend_slot": {"type": "integer", "minimum": 1, "maximum": 9, "description": "spell slot level spent"},
                  "restore_slot": {"type": "integer", "minimum": 1, "maximum": 9},
                  "use_resource": {"type": "string", "description": "a feature name exactly as on the sheet, e.g. Second Wind"},
                  "restore_resource": {"type": "string"},
                  "items_gained": _ITEMS, "items_lost": _ITEMS,
                  "coin_change_gp": {"type": "number", "description": "money gained (+) or spent (-), in gp; 0.1 = 1 sp"},
                  "conditions_added": _NAMES, "conditions_removed": _NAMES,
                  "xp_gained": _INT,
                  "short_rest": {"type": "boolean"}, "long_rest": {"type": "boolean"}}})
        async def change_pc(a: dict[str, Any]) -> dict[str, Any]:
            def go() -> str:
                self.sheet, lines = m.change_pc(self.sheet, a)
                return "; ".join(lines)
            return self.run("sheet", go)

        @tool("add_combatants", "Start a fight, or add arrivals to the current one. Roll initiative first. The PC is "
              "the combatant named 'pc'; every creature needs a distinct name, hp and ac.",
              {"type": "object", "properties": {"combatants": {"type": "array", "items": {
                  "type": "object", "properties": {"name": {"type": "string"}, "initiative": {"type": "integer"},
                                                   "hp": {"type": "integer"}, "ac": {"type": "integer"}},
                  "required": ["name", "initiative"]}}}, "required": ["combatants"]})
        async def add_combatants(a: dict[str, Any]) -> dict[str, Any]:
            def go() -> str:
                self.fight, text = m.add_combatants(self.fight, self.sheet["name"], a["combatants"])
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

        @tool("next_turn", "Move the fight to the next combatant in initiative order and show whose turn it is.",
              {"type": "object", "properties": {}})
        async def next_turn(a: dict[str, Any]) -> dict[str, Any]:
            def go() -> str:
                self.fight, text = m.next_turn(self.fight)
                return text
            return self.run("fight", go)

        @tool("end_fight", "End the current fight.", {"type": "object", "properties": {}})
        async def end_fight(a: dict[str, Any]) -> dict[str, Any]:
            def go() -> str:
                self.fight, text = m.end_fight(self.fight)
                return text
            return self.run("fight", go)

        return [roll, change_pc, add_combatants, change_creature, next_turn, end_fight]


def sheet_text(s: dict[str, Any]) -> str:
    lines = [f"{s['name']}: {s['summary']}",
             f"AC {s['ac']} ({s['ac_note']}); speed {s['speed']}; proficiency bonus +{s['proficiency_bonus']}",
             "Abilities: " + ", ".join(f"{k} {v}" for k, v in s["abilities"].items()),
             f"Saving throws: {s['saving_throws']}", f"Skills: {s['skills']}",
             f"Passive Perception {s['passive_perception']}; senses: {s['senses']}",
             f"Languages: {s['languages']}", f"Proficiencies: {s['proficiencies']}",
             "Attacks:", *(f"- {x}" for x in s["attacks"])]
    sp = s.get("spellcasting")
    if sp:
        lines += [f"Spellcasting ({sp['ability']}): save DC {sp['save_dc']}, spell attack +{sp['attack_bonus']}",
                  "Cantrips: " + ", ".join(sp["cantrips"]), "Spellbook: " + ", ".join(sp["spellbook"]),
                  "Prepared: " + ", ".join(sp["prepared"]), sp["notes"]]
    lines += ["Features:", *(f"- {x}" for x in s["features"])]
    return "\n".join(lines)


def system_prompt(sheet: dict[str, Any]) -> str:
    return ((HERE / "prompt.md").read_text(encoding="utf-8")
            + "\n\n## The player's character\n" + sheet_text(sheet)
            + "\n\n## The opening\n" + sheet["opening"])


async def turn(client: ClaudeSDKClient, game: Game, text: str) -> None:
    await client.query(f"[Status now]\n{game.status()}\n\n{text}")
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


async def main() -> None:
    ap = argparse.ArgumentParser(description="Play with the AI DM.")
    ap.add_argument("character", nargs="?", choices=("fighter", "rogue", "wizard"))
    ap.add_argument("--resume", type=Path, help="a save file to continue")
    ap.add_argument("--model", default=MODEL)
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    if args.resume:
        game = Game(json.loads(args.resume.read_text(encoding="utf-8")), args.resume)
    elif args.character:
        sheet = json.loads((HERE / "characters" / f"{args.character}.json").read_text(encoding="utf-8"))
        name = sheet["name"].split()[0].lower()
        game = Game({"sheet": sheet, "model": args.model}, SAVES / f"{name}-{time.strftime('%Y%m%d-%H%M%S')}.json")
    else:
        ap.error("pick a character (fighter, rogue, wizard) or --resume a save")

    server = create_sdk_mcp_server("dm", tools=game.tools())
    SAVES.mkdir(exist_ok=True)
    opts = ClaudeAgentOptions(
        system_prompt=system_prompt(game.sheet), model=game.model, tools=[], mcp_servers={"dm": server},
        allowed_tools=[f"mcp__dm__{n}" for n in ("roll", "change_pc", "add_combatants", "change_creature",
                                                 "next_turn", "end_fight")],
        setting_sources=[], strict_mcp_config=True, max_turns=40, cwd=str(SAVES), resume=game.session_id)
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
                print(sheet_text(game.sheet) + "\n" + game.status())
                continue
            game.log("player", line)
            await turn(client, game, f"[The player]\n{line}")


if __name__ == "__main__":
    asyncio.run(main())
