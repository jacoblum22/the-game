"""Experiment (Jake, 2026-11-02): does one short "think less" note in the DM's instructions cut the thinking time?
Replays 8 turns of a saved game (dm.branch.fork_data), each twice with the same model and settings: A as it is, B with the
note added to the DM's system prompt (here, in the model.send wrapper; no code path of the game changes).

    py -3 evals/compare/thinkless.py <save.json> <calls-tag, e.g. dslow> <model> [<out file, default out/thinkless.json>]
Env as for the game: DM_GATEWAY_PASS_REASONING=1 (so the thinking is returned), DM_GATEWAY_PARAMS, DM_GATEWAY_CHECK_PARAMS.
"""
from __future__ import annotations

import asyncio
import contextlib
import json
import re
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from dm import branch, check, model, play  # noqa: E402
from evals.compare.run import OUT, load_keys  # noqa: E402

NOTE = ("Keep your private reasoning short. Decide quickly what happens, and do not draft or re-plan the reply in your "
        "reasoning; write the scene directly.")
# planning voice in the visible reply ("We need to", "Let me think", "Plan:" ...): a hint to look at, not a verdict
LEAK = re.compile(r"\b(we need to|i need to|let me (think|plan|figure)|the user (wants|says)|the player (wants|says)|plan:|draft:)", re.I)


def pick(rounds: list[dict[str, Any]]) -> list[int]:
    """The 4 rounds that took longest, and 4 typical ones spread over the game (round numbers)."""
    slow = [r["round"] for r in sorted(rounds, key=lambda r: -r["seconds"])[:4]]
    rest = [r["round"] for r in rounds if r["round"] not in slow]
    return sorted(slow) + [rest[int(i * (len(rest) - 1) / 3)] for i in range(4)]


async def replay(game: play.Game, turn: int, line: str, dm_model: str, note: bool, tmp: Path) -> dict[str, Any]:
    stats: list[dict[str, Any]] = []
    real_send = model.send

    async def logged(request: dict[str, Any]) -> dict[str, Any]:
        sys_ = str(request.get("system", ""))
        if sys_.startswith("You are a human player") or sys_.startswith(check.SYSTEM):
            return await real_send(request)  # the checker runs as in the pipeline, with no note
        if note:
            request = {**request, "system": request["system"] + "\n\n" + NOTE}
        t0 = time.time()
        reply = await real_send(request)
        think = sum(len(b.get("thinking", "")) for b in reply["content"] if b.get("type") == "thinking")
        stats.append({"seconds": round(time.time() - t0, 1), "thinking_chars": think,
                      "output_tokens": (reply.get("usage") or {}).get("output_tokens", 0)})
        return reply
    model.send = logged
    try:
        fork = play.Game(branch.fork_data(game, turn), tmp / f"t{turn}{'B' if note else 'A'}.json")
        s = play.Session(dm_model, "api")
        with open(tmp / "out.log", "a", encoding="utf-8") as log, contextlib.redirect_stdout(log):
            await s.play(fork, show_last=False)
            n0 = len(fork.transcript)
            await s.line(line)
        new = fork.transcript[n0:]
    finally:
        model.send = real_send
    reply = "\n\n".join(e["text"] for e in new if e["kind"] == "dm")
    return {"dm_calls": len(stats), "dm_seconds": round(sum(c["seconds"] for c in stats), 1), "slowest_call": max((c["seconds"] for c in stats), default=0),
            "thinking_chars": sum(c["thinking_chars"] for c in stats), "output_tokens": sum(c["output_tokens"] for c in stats),
            "reply_chars": len(reply), "tools": [e["tool"] for e in new if e["kind"] == "call"],
            "refused": sum(e["kind"] == "refused" for e in new), "failed": sum(e["kind"] == "failed" for e in new),
            "stubs": sum(e["kind"] == "stub" for e in new), "leak_hint": bool(LEAK.search(reply)), "reply_head": reply[:300]}


async def main(save: str, tag: str, dm_model: str, outfile: Path) -> None:
    load_keys()
    check.ENABLED, check.CHECK_MODEL = True, dm_model
    game = play.Game(json.loads(Path(save).read_text(encoding="utf-8")), Path(save))
    rounds = json.loads((OUT / f"{tag}.metrics.json").read_text(encoding="utf-8"))["rounds"]
    lines = dict(enumerate((t for t in branch.lines(game)), 1))  # the player's n-th line = round n
    results: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        play.SAVES = tmp
        for rnd in pick(rounds):
            turn, line = lines[rnd]
            row: dict[str, Any] = {"round": rnd, "turn": turn, "original_seconds": rounds[rnd - 1]["seconds"], "line": line}
            for name, note in (("A", False), ("B", True)):  # one after the other, never in parallel
                row[name] = await replay(game, turn, line, dm_model, note, tmp)
                print(rnd, name, {k: row[name][k] for k in ("dm_seconds", "thinking_chars", "reply_chars", "leak_hint")}, flush=True)
            results.append(row)
            outfile.write_text(json.dumps(results, indent=1, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1], sys.argv[2], sys.argv[3], Path(sys.argv[4]) if len(sys.argv) > 4 else OUT / "thinkless.json"))
