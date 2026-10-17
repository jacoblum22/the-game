"""Does the DM stop closing on a sheet read-out once its conversation no longer has any? (Jake, 2026-10-17)
A copy of a game's DM conversation as it is now, under a new session id, either as it is (control) or with every
"You have N of M hit points ..." sentence taken out (clean); then the same player lines in each. Nothing is saved.
    PYTHONPATH=. .venv/Scripts/python evals/autoloop/probe_strip.py <name> <runs per arm>
Prints, for each reply, whether the DM wrote the read-out (the game's strip records it as "trimmed")."""
import asyncio
import contextlib
import io
import json
import os
import sys
import uuid
from pathlib import Path

from dm import branch, play, sdk

GAMES = Path(__file__).parent / "games"
LINES = ["I take stock of where we are and what we still have to do.",
         "I talk quietly with Kit about what we do next.",
         "We go ahead with that plan."]


def copy_session(cwd: str, sid: str, clean: bool) -> tuple[str, int]:
    new = str(uuid.uuid4())
    out, n = [], 0
    for line in branch.session_file(cwd, sid).read_text(encoding="utf-8").splitlines():
        try:
            e = json.loads(line.replace(sid, new))
        except ValueError:
            continue
        msg = e.get("message")
        if clean and isinstance(msg, dict):
            c = msg.get("content")
            if isinstance(c, str):
                n += len(branch.STAT_LINE.findall(c))
                msg["content"] = branch.STAT_LINE.sub("", c)
            elif isinstance(c, list):
                for b in c:
                    if isinstance(b, dict) and b.get("type") == "text":
                        n += len(branch.STAT_LINE.findall(b["text"]))
                        b["text"] = branch.STAT_LINE.sub("", b["text"]).rstrip() or "(no reply)"
        out.append(json.dumps(e, ensure_ascii=False))
    branch.session_file(cwd, new).write_text("\n".join(out) + "\n", encoding="utf-8")
    return new, n


async def run(name: str, clean: bool) -> list[bool]:
    meta = json.loads((GAMES / f"{name}.meta.json").read_text(encoding="utf-8"))
    path = GAMES / Path(meta["save"]).name
    g = play.Game(json.loads(path.read_text(encoding="utf-8")), path)
    g.save = lambda: None
    g.system = play.system_prompt(g.sheet, g.companions)
    g.session_id, removed = copy_session(g.cwd, g.session_id, clean)
    g.sdk = sdk.Client(g.model, g.system, g.tools(), g.cwd, g.session_id)
    await g.sdk.open()
    wrote = []
    try:
        for line in LINES:
            g.log("player", line)
            start = len(g.transcript)
            await play.turn(g, f"[The player]\n{line}")
            wrote.append(any(e["kind"] == "trimmed" or (e["kind"] == "dm" and "hit points" in e["text"])
                             for e in g.transcript[start:]))
    finally:
        await g.sdk.close()
        branch.session_file(g.cwd, g.session_id).unlink(missing_ok=True)
    print(f"{'clean' if clean else 'control'} (removed {removed}): read-out written {wrote}", file=sys.stderr)
    return wrote


async def main(name: str, runs: int) -> None:
    res = await asyncio.gather(*(run(name, clean) for clean in (False, True) for _ in range(runs)))
    for arm, rs in (("control", res[:runs]), ("clean", res[runs:])):
        print(f"{arm}: {sum(map(sum, rs))} of {sum(map(len, rs))} replies closed on a read-out", file=sys.stderr)


if __name__ == "__main__":
    with contextlib.redirect_stdout(io.StringIO()):
        asyncio.run(main(sys.argv[1], int(sys.argv[2])))
