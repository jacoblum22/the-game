"""Run the synthetic tests (owner, 2026-10-13): each case is the shared Mourhold campaign at one moment, plus the
player's lines. The DM plays them on the owner's version (the Agent SDK), as in a real game, and each run is written
out for reading: the save, and a plain dump of what the DM did. Nothing is scored here; the runs are read by hand.

    py -3.12 -m evals.synthetic.run                 every case
    py -3.12 -m evals.synthetic.run p09 p10-halran  cases whose id starts with any of these
    py -3.12 -m evals.synthetic.run --jobs 3        three at a time (default 2)
"""
import argparse
import asyncio
import contextlib
import io
import json
import re
import sys
import time
from pathlib import Path

from dm import lore as notebook
from dm import mechanics as m
from dm import play
from evals.synthetic.base import base_game

HERE = Path(__file__).parent
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿\U0001F000-\U0001F2FF]")


def load(name: str):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def game_for(case: dict, path: Path) -> play.Game:
    """The base campaign with the case's state (clock, sheet changes, a fight), then its 40 turns of history and
    notebook, the summary of them, and the case's recent turns word for word."""
    g = base_game(path)
    setup = case.get("setup", {})
    tools = {t.name: t.handler for t in g.tools()}
    if setup.get("clock"):
        g.clock, _ = m.change_time(g.clock, {"set": setup["clock"]})
    for name, args in [("change_pc", a) for a in setup.get("pc", [])] + [tuple(x) for x in setup.get("fight", [])]:
        res = asyncio.run(tools[name](args))
        assert not res.get("is_error"), (case["id"], res["content"][0]["text"])
    g.transcript = []  # the setup's tool lines aren't play
    for t in load("history.json"):
        if t.get("player"):
            g.log("player", t["player"])
        g.log("dm", t["dm"])
    for w in load("notebook.json"):
        g.lore, _ = notebook.write(g.lore, w["write"], w["turn"])
    story = (HERE / "story.txt").read_text(encoding="utf-8").strip()
    if case.get("story_extra"):  # what happened between the history and the case's recent turns
        story += " " + case["story_extra"]
    g.story = [{"turn": notebook.now(g.transcript), "text": story}]
    for t in case.get("recent", []):
        if t.get("player"):
            g.log("player", t["player"])
        for x in t.get("tools", []):
            g.log("tool", x)
        g.log("dm", t["dm"])
    for w in setup.get("lore", []):  # notebook writes made in those turns
        g.lore, _ = notebook.write(g.lore, w, notebook.now(g.transcript))
    g.save()
    return g


def facts(new: list[dict]) -> str:
    """What code can see at a glance; the reading decides what it means."""
    calls = [e for e in new if e["kind"] == "call"]
    tools = [e["text"] for e in new if e["kind"] == "tool"]
    said = [e["text"] for e in new if e["kind"] == "dm"]
    n = lambda pred: sum(1 for x in tools if pred(x))
    return "\n".join([
        f"rolls: {n(lambda x: x.startswith('dice '))}",
        (f"lookups: lore {sum(c['tool'] == 'lore' for c in calls)}, recall {sum(c['tool'] == 'recall' for c in calls)}, "
         f"rules {sum(c['tool'] == 'lookup' for c in calls)}"),
        f"notebook writes: {sum(c['tool'] == 'write_lore' for c in calls)}",
        f"clock changes: {n(lambda x: x.startswith('time: '))}",
        f"refused: {sum(e['kind'] == 'refused' for e in new)}",
        f"emoji in replies: {sum(len(EMOJI.findall(s)) for s in said)}",
        f"headings/bullets lines: {sum(1 for s in said for ln in s.splitlines() if re.match(r'\s*(#|[-*•] |\*\*[^*]+\*\*\s*$)', ln))}",
        f"reply words: {[len(s.split()) for s in said]}",
    ])


def dump(case: dict, g: play.Game, start: int) -> str:
    out = [f"# {case['id']} (problem {case['problem']}{', control' if case.get('control') else ''})",
           f"source: {case.get('source', '')}", f"pass: {case['pass']}", f"fail: {case['fail']}", "",
           facts(g.transcript[start:]), "", "## Play"]
    for e in g.transcript[start:]:
        if e["kind"] == "call":
            out.append(f"[hidden {e['tool']}] {json.dumps(e['input'], ensure_ascii=False)}\n  -> {e['result']}")
        elif e["kind"] == "tool":
            out.append(f"[{e['text']}]")
        elif e["kind"] == "refused":
            out.append(f"[REFUSED {e['text']}]")
        else:
            out.append(f"{e['kind'].upper()}: {e['text']}")
    return "\n\n".join(out)


async def run_case(case: dict, folder: Path) -> str:
    path = folder / f"{case['id']}.json"
    g = await asyncio.to_thread(game_for, case, path)  # game_for runs the tools with its own event loop
    start = len(g.transcript)
    s = play.Session(g.model, "sdk")
    t0 = time.time()
    try:
        await s.play(g)
        for line in case["player"]:
            await s.line(line)
    finally:
        await s.close()
    g.save()
    (folder / f"{case['id']}.txt").write_text(dump(case, g, start), encoding="utf-8")
    return f"{case['id']}: done in {time.time() - t0:.0f}s"


async def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("only", nargs="*")
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--build-only", action="store_true", help="build each case's save without playing")
    args = ap.parse_args()
    cases = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((HERE / "cases").glob("*.json"))]
    cases = [c for c in cases if not args.only or any(c["id"].startswith(o) for o in args.only)]
    folder = HERE / "runs" / time.strftime("%Y%m%d-%H%M%S")
    folder.mkdir(parents=True, exist_ok=True)
    if args.build_only:
        for c in cases:
            await asyncio.to_thread(game_for, c, folder / f"{c['id']}.json")
            print(f"{c['id']}: built")
        return
    sem = asyncio.Semaphore(args.jobs)

    async def one(c: dict) -> None:
        async with sem:
            try:
                note(await run_case(c, folder))
            except Exception as e:  # noqa: BLE001 - one broken case shouldn't stop the rest
                note(f"{c['id']}: FAILED {type(e).__name__}: {e}")
    with contextlib.redirect_stdout(io.StringIO()):  # the game prints as it plays; the dumps hold it all
        await asyncio.gather(*(one(c) for c in cases))
    note(f"runs in {folder}")


def note(text: str) -> None:
    print(text, file=sys.stderr, flush=True)


if __name__ == "__main__":
    asyncio.run(main())
