"""Why does the DM send its record calls before its reply? (Jake, 2026-10-18) One turn of a test game on the API, from
a fresh conversation (the game so far word for word, as after a cut), through the game's own turn(); then the shape of
each model call: its text and its tools. The key is read from the repo's .env and given to this client only.
    PYTHONPATH=".;evals/autoloop" .venv/Scripts/python evals/autoloop/order_bench.py <variant> <game> <rounds> [runs]
Variants: full (the game as it is), bare (a few lines of instructions, the same tools), and the ones in VARIANTS."""
import asyncio
import contextlib
import io
import json
import os
import sys
from pathlib import Path

import anthropic

from dm import lore as notebook
from dm import model, play

GAMES = Path(__file__).parent / "games"
ENV = Path(__file__).parents[2] / ".env"
KEY = next(x.split("=", 1)[1].strip().strip('"') for x in ENV.read_text(encoding="utf-8").splitlines()
           if x.startswith("ANTHROPIC_API_KEY="))
model._client = anthropic.AsyncAnthropic(api_key=KEY, max_retries=5)

BARE = ("You are the Dungeon Master of a solo game of D&D 5e. Narrate in the second person, and end each reply with "
        "what the character faces. Roll every die with `roll`. Keep the record with the tools: the clock "
        "(`change_time`), the notebook (`write_lore`), the character sheet (`change_pc`).\n\n"
        "The player sees only what you send with `reply`. A turn has at most two kinds of message. First, if you need "
        "them, the calls whose result you need: rolls, lookups, the notebook's `lore` and `recall`. Then one last "
        "message of calls together: `reply` with your whole reply to the player, and the calls that record it "
        "(`change_time`, `write_lore`, `change_pc`, `change_party`, `change_creature`). The game ends your turn once "
        "those calls have run.")


def game_at(name: str, rnd: int) -> tuple[play.Game, str]:
    meta = json.loads((GAMES / f"{name}.meta.json").read_text(encoding="utf-8"))
    save = json.loads((GAMES / Path(meta["save"]).name).read_text(encoding="utf-8"))
    st = {json.loads(x)["round"]: json.loads(x) for x in open(GAMES / f"{name}.states.jsonl", encoding="utf-8")}[rnd]
    t = save["transcript"]
    idx, line = [(i, e["text"]) for i, e in enumerate(t) if e["kind"] == "player" and i >= meta["play_starts"]][rnd - 1]
    g = play.Game({k: v for k, v in save.items() if k not in ("transcript", "lore", "clock", "session_id", "messages",
                                                                "story")} | {"backend": "api"}, Path(os.devnull))
    g.transcript = t[:idx]
    for k in ("sheet", "companions", "fight", "clock", "lore"):
        setattr(g, k, st[k])
    g.save = lambda: None
    return g, line


def shape(messages: list[dict], start: int) -> list[str]:
    out = []
    for m in messages[start:]:
        if m["role"] != "assistant":
            continue
        parts = [f"text{len(b['text'])}" if b["type"] == "text" else b["name"] for b in m["content"]
                 if b["type"] in ("text", "tool_use") and (b["type"] != "text" or b["text"].strip())]
        out.append(",".join(parts) or "-")
    return out


def verdict(steps: list[str], asks: int) -> str:
    last = steps[-1].split(",")
    rec = set(play.BOOKKEEPING)
    if asks:
        return "stub"
    if "reply" in last and set(last) <= rec | {"reply"} and not any(
            set(s.split(",")) & rec and "reply" not in s.split(",") for s in steps[:-1]):
        return "one"
    if len(last) > 1 and last[0].startswith("text") and int(last[0][4:]) >= play.FULL_REPLY and set(last[1:]) <= rec:
        return "one"
    if any(set(s.split(",")) & rec and not s.split(",")[0].startswith("text") for s in steps):
        return "record first"
    if not any(set(s.split(",")) & rec for s in steps):
        return "no record"
    return "other"


async def once(variant: str, name: str, rnd: int) -> dict:
    g, line = game_at(name, rnd)
    g.system = BARE if variant == "bare" else play.system_prompt(g.sheet, g.companions)
    g.log("player", line)
    g.messages = []
    start = len(g.transcript)
    await play.turn(g, f"[The player]\n{line}")
    asks = sum(e["kind"] == "stub" for e in g.transcript[start:])
    steps = shape(g.messages, 1)
    return {"round": rnd, "steps": steps, "asks": asks, "verdict": verdict(steps, asks)}


async def main() -> None:
    variant, name, rounds = sys.argv[1], sys.argv[2], [int(x) for x in sys.argv[3].split(",")]
    runs = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    if variant == "bare":
        play.RULES_REMINDER = ""
    sem = asyncio.Semaphore(4)

    async def one(r: int) -> dict:
        async with sem:
            try:
                return await once(variant, name, r)
            except Exception as e:  # noqa: BLE001
                return {"round": r, "error": f"{type(e).__name__}: {e}"[:300]}
    with contextlib.redirect_stdout(io.StringIO()):
        res = await asyncio.gather(*(one(r) for r in rounds for _ in range(runs)))
    for r in res:
        print(r["round"], r.get("verdict") or r.get("error"), " | ".join(r.get("steps", [])), file=sys.stderr)
    from collections import Counter
    print(variant, dict(Counter(r.get("verdict", "error") for r in res)), file=sys.stderr)


asyncio.run(main())
