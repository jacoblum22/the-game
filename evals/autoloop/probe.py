"""Send one player line to a copy of an autoloop game as it is now: the DM's conversation is forked at its end and
the save isn't written, so the game itself is untouched. For checking that a game can go on (e.g. after API errors).
    py -3.12 evals/autoloop/probe.py <name> "<player line>" """
import asyncio
import contextlib
import io
import json
import sys
from pathlib import Path

from claude_agent_sdk import ClaudeSDKClient

from dm import play, sdk

GAMES = Path(__file__).parent / "games"


async def main(name: str, line: str) -> None:
    meta = json.loads((GAMES / f"{name}.meta.json").read_text(encoding="utf-8"))
    path = GAMES / Path(meta["save"]).name
    g = play.Game(json.loads(path.read_text(encoding="utf-8")), path)
    g.save = lambda: None
    g.system = play.system_prompt(g.sheet, g.companions)
    c = sdk.Client(g.model, g.system, g.tools(), str(sdk.DM_HOME), g.session_id)
    c.options.fork_session = True
    c.client = ClaudeSDKClient(options=c.options)
    g.sdk = c
    g.log("player", line)
    start = len(g.transcript)
    await c.open()
    try:
        await play.turn(g, f"[The player]\n{line}")
    finally:
        await c.close()
    for e in g.transcript[start:]:
        print(f"[{e['kind']}] {(e.get('text') or e.get('tool') or '')[:600]}", file=sys.stderr)


if __name__ == "__main__":
    with contextlib.redirect_stdout(io.StringIO()):
        asyncio.run(main(sys.argv[1], sys.argv[2]))
