"""Replay rounds of an autoloop game N times each: branch the DM's Claude Code conversation just before the round,
put the game back as it was (from the round's snapshot, or rebuilt), and send the same player line through the game's
own turn code. Nothing is written back. With PROMPT_MD, a changed prompt.md is used instead.
    py -3.12 evals/autoloop/replay.py <name> <rounds, e.g. 12,40> <runs> <out.json>"""
import asyncio
import contextlib
import io
import json
import os
import re
import sys
from pathlib import Path

from claude_agent_sdk import ClaudeSDKClient

from dm import lore as notebook
from dm import mechanics as m
from dm import play, sdk

GAMES = Path(__file__).parent / "games"
PROJECTS = Path.home() / ".claude" / "projects" / re.sub(r"[^A-Za-z0-9]", "-", str(sdk.DM_HOME))  # Claude Code's folder name
NAME, POINTS, RUNS, OUT = sys.argv[1], [int(x) for x in sys.argv[2].split(",")], int(sys.argv[3]), Path(sys.argv[4])
META = json.loads((GAMES / f"{NAME}.meta.json").read_text(encoding="utf-8"))
SAVE = json.loads((GAMES / Path(META["save"]).name).read_text(encoding="utf-8"))
STATES = {}
if (GAMES / f"{NAME}.states.jsonl").exists():
    for line in open(GAMES / f"{NAME}.states.jsonl", encoding="utf-8"):
        s = json.loads(line)
        STATES[s["round"]] = s
if os.environ.get("PROMPT_MD"):
    _sp, _alt = play.system_prompt, Path(os.environ["PROMPT_MD"]).read_text(encoding="utf-8")
    play.system_prompt = lambda sheet, comp: _alt + _sp(sheet, comp)[len((play.HERE / "prompt.md").read_text(encoding="utf-8")):]


async def no_cut(game: play.Game) -> None:
    return None
play.cut = no_cut


def player_lines() -> list[tuple[int, str]]:
    """(transcript index, text) of each round's player line, round 1 first."""
    t = SAVE["transcript"]
    return [(i, e["text"]) for i, e in enumerate(t) if e["kind"] == "player" and i >= META["play_starts"]]


def fork_point(turn: int, line: str) -> tuple[str, str, str]:
    """The Claude Code session holding this round's prompt, the entry to branch after, and the prompt."""
    for f in sorted(PROJECTS.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)[:400]:
        entries = [json.loads(x) for x in open(f, encoding="utf-8")]
        for i, e in enumerate(entries):
            c = e.get("message", {}).get("content") if isinstance(e.get("message"), dict) else None
            if e.get("type") == "user" and isinstance(c, str) and f"[The player]\n{line}" in c:
                return f.stem, next(x["uuid"] for x in reversed(entries[:i]) if x.get("uuid")), c
    raise LookupError(f"no session has the line of turn {turn}")


def state(k: int) -> tuple[play.Game, str, str, str]:
    idx, line = player_lines()[k - 1]
    g = play.Game({key: v for key, v in SAVE.items() if key not in ("transcript", "lore", "clock")}, Path(os.devnull))
    g.transcript = SAVE["transcript"][:idx]
    turn = notebook.now(g.transcript) + 1
    session, fork, prompt = fork_point(turn, line)
    if k in STATES:  # the game as it was, saved by run.py before the round
        for key in ("sheet", "companions", "fight", "clock", "lore"):
            setattr(g, key, STATES[k][key])
    else:  # rebuilt: the notebook from its calls, the clock from the prompt; sheet and fight are the save's latest
        g.lore = notebook.new()
        for i, e in enumerate(g.transcript):
            if e["kind"] == "call" and e["tool"] == "write_lore":
                g.lore, _ = notebook.write(g.lore, e["input"], notebook.now(g.transcript[:i]))
        day, hh, mm, ap = re.search(r"Time: Day (\d+), (\d+):(\d+)(?::\d+)? (AM|PM)", prompt).groups()
        g.clock, _ = m.change_time(m.new_clock(), {"set": {"day": int(day), "time": f"{int(hh) % 12 + (12 if ap == 'PM' else 0):02d}:{mm}"}})
    g.session_id = session
    return g, line, fork, session


async def once(k: int, n: int) -> dict:
    g, line, fork, session = state(k)
    g.save = lambda: None
    g.system = play.system_prompt(g.sheet, g.companions)
    c = sdk.Client(g.model, g.system, g.tools(), str(sdk.DM_HOME), session,
                   **({"done": g.one_step} if hasattr(g, "one_step") else {}))
    c.options.resume_session_at, c.options.fork_session = fork, True
    c.client = ClaudeSDKClient(options=c.options)
    g.sdk = c
    g.log("player", line)
    start = len(g.transcript)
    await c.open()
    try:
        await play.turn(g, f"[The player]\n{line}")
    finally:
        await c.close()
    return {"round": k, "run": n, "line": line, "session": c.session_id, "entries": [{"kind": e["kind"], "text": e.get("text") or e.get("tool"),
                                                             "input": e.get("input")} for e in g.transcript[start:]],
            "sheet": g.sheet, "clock": g.clock, "fight": g.fight}


async def main() -> None:
    sem = asyncio.Semaphore(2)

    async def one(k: int, n: int) -> dict:
        async with sem:
            try:
                return await once(k, n)
            except Exception as e:  # noqa: BLE001
                return {"round": k, "run": n, "error": f"{type(e).__name__}: {e}"}
    with contextlib.redirect_stdout(io.StringIO()):
        res = await asyncio.gather(*(one(k, n) for k in POINTS for n in range(RUNS)))
    OUT.write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"{len(res)} runs -> {OUT}", file=sys.stderr)

asyncio.run(main())
