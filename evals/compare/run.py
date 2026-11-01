"""One 20-round test game for the model comparison (Jake, 2026-11-01): a new game with the ready-made fighter, the DM on
the model given (Claude, or a model behind the gateway: dm/gateway.py), and a Sonnet player typing the lines. Every
model gets the same character, the same player brief and the same code. The continuity checker is on, and runs on the same
model as the DM, so the whole pipeline is compared. Every model call is logged with its tokens, so the cost is known afterwards.

    py -3 evals/compare/run.py <tag> <model> [<rounds, default 20>]
    e.g.  run.py sonnet claude-sonnet-5-5 | run.py qwen ali/qwen3.7-plus | run.py glm zai/glm-5.3

Keys: ANTHROPIC_API_KEY (the player, and a Claude DM) and DM_GATEWAY_KEY (the gateway) are read from the
environment, or from the .env in the repo's root (only these two names; never printed). Output, in evals/compare/out/:
<tag>.json (the save), <tag>.log (what the player saw), <tag>.calls.jsonl (one line per model call), <tag>.metrics.json.
"""
from __future__ import annotations

import asyncio
import contextlib
import json
import os
import statistics
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from dm import check, model, play  # noqa: E402

OUT = Path(__file__).parent / "out"
PLAYER_MODEL = "claude-sonnet-5-5"
# $ per million tokens: input, cache read, cache write, output. List prices read on 2026-11-01, not checked against
# a bill; the token counts in <tag>.calls.jsonl are the facts.
PRICES = {"claude-sonnet-5-5": (2.0, 0.10, 4.0, 10.0),  # cache write: the 1-hour kind, which the DM asks for
          "ali/qwen3.7-plus": (0.32, 0.03, 0.32, 1.28),  # no cache-write line is reported: written tokens count as input
          "zai/glm-5.3": (1.40, 0.26, 1.40, 4.40)}  # Z.AI's own price; other hosts of the open model charge less

PLAYER = """You are a human player in a solo D&D 5e game (2014 rules) run by a DM. {style}
Each message you get is what the DM just said (with any dice or game lines in brackets). Reply with only your next
line as the player, the way a real player types: one to three sentences, in character or describing what you do. No
narration of outcomes, no DM voice, no headings.
Care about continuity: every few turns refer back to a person, place, item, promise or detail from earlier in the game
by name. Now and then (every ten turns or so) ask the DM a short out-of-character question starting with "DM:" about
something established earlier (who someone was, what was said, your money or gear, a rule). Pursue the story's goals,
and make your own when there are none. Don't stall: if a scene is done, move on."""
STYLE = ("You play your fighter boldly but sensibly: you take on the town's trouble, talk to people and ask questions, "
         "fight when it comes and think about tactics, and use your features.")


def load_keys() -> None:
    """ANTHROPIC_API_KEY and DM_GATEWAY_KEY from the repo's .env, unless already set. Nothing else is read."""
    try:
        lines = (ROOT / ".env").read_text(encoding="utf-8").splitlines()
    except OSError:
        return
    for line in lines:
        name, _, value = line.partition("=")
        if name.strip() in ("ANTHROPIC_API_KEY", "DM_GATEWAY_KEY") and name.strip() not in os.environ:
            os.environ[name.strip()] = value.strip().strip('"').strip("'")


def shown(entries: list[dict[str, Any]]) -> str:
    """What the player saw: the DM's text and the game's lines (dice, sheet, clock)."""
    out = "\n\n".join(f"[{e['text']}]" if e["kind"] == "tool" else e["text"] for e in entries if e["kind"] in ("dm", "tool"))
    if any(e["kind"] == "failed" for e in entries) and not any(e["kind"] == "dm" for e in entries):
        out += "\n\n[the DM's reply didn't come through]"
    return out.strip()


def cost(usage: dict[str, int], name: str) -> float:
    i, r, w, o = PRICES.get(name, (0.0, 0.0, 0.0, 0.0))
    return (usage.get("input_tokens", 0) * i + usage.get("cache_read_input_tokens", 0) * r
            + usage.get("cache_creation_input_tokens", 0) * w + usage.get("output_tokens", 0) * o) / 1e6


def dm_count(out: Path, tag: str) -> int:
    """The DM's model calls so far (not the player's, not the checker's)."""
    return sum(json.loads(line)["role"] == "dm" for line in open(out / f"{tag}.calls.jsonl", encoding="utf-8"))


async def play_game(tag: str, dm_model: str, rounds: int, out: Path = OUT) -> dict[str, Any]:
    out.mkdir(parents=True, exist_ok=True)
    calls = open(out / f"{tag}.calls.jsonl", "w", encoding="utf-8")
    real_send, real_check_model = model.send, check.CHECK_MODEL

    async def logged(request: dict[str, Any]) -> dict[str, Any]:
        sys_ = str(request.get("system", ""))
        role = "player" if sys_.startswith("You are a human player") else "check" if sys_ == check.SYSTEM else "dm"
        t0 = time.time()
        reply = await real_send(request)
        calls.write(json.dumps({"role": role, "model": request["model"], "seconds": round(time.time() - t0, 1),
                                "usage": reply.get("usage"), "stop": reply.get("stop_reason")}) + "\n")
        calls.flush()
        return reply
    model.send = logged
    check.ENABLED = True  # the whole pipeline, the continuity checker included, on the same model as the DM (Jake)
    check.CHECK_MODEL = dm_model
    play.SAVES = out
    history: list[dict[str, Any]] = []

    async def player_line(said: str) -> str:
        history.append({"role": "user", "content": said})
        reply = await model.send({"model": PLAYER_MODEL, "max_tokens": 2000, "system": PLAYER.format(style=STYLE),
                                  "messages": history, "output_config": {"effort": "low"},
                                  "cache_control": {"type": "ephemeral"}})
        line = "".join(b["text"] for b in reply["content"] if b["type"] == "text").strip()
        history.append({"role": "assistant", "content": line or "I look around."})
        return line or "I look around."

    rounds_out: list[dict[str, Any]] = []
    failures = 0
    s = play.Session(dm_model, "api")
    try:
        with open(out / f"{tag}.log", "w", encoding="utf-8") as log, contextlib.redirect_stdout(log):
            await s.new("fighter")  # the opening turn: the DM's first reply
            g = s.game
            assert g
            seen = 0
            for n in range(1, rounds + 1):
                said = shown(g.transcript[seen:])
                line = await player_line(said)
                print(f"\n\n>>>>>> round {n}, the player: {line}\n", flush=True)
                seen, n_calls, t0 = len(g.transcript), dm_count(out, tag), time.time()
                await s.line(line)
                new = g.transcript[seen:]
                dm_calls = dm_count(out, tag) - n_calls
                rounds_out.append({
                    "round": n, "seconds": round(time.time() - t0, 1), "dm_calls": dm_calls,
                    "refused": sum(e["kind"] == "refused" for e in new), "failed": sum(e["kind"] == "failed" for e in new),
                    "stubs": sum(e["kind"] == "stub" for e in new),
                    "reply_chars": sum(len(e["text"]) for e in new if e["kind"] == "dm"),
                    "tools": [e["tool"] for e in new if e["kind"] == "call"]})
                failures += any(e["kind"] == "failed" for e in new)
                (out / f"{tag}.metrics.json").write_text(json.dumps({"rounds": rounds_out}, indent=1), encoding="utf-8")
                if failures >= 3:
                    print("\n[stopped: three rounds failed]")
                    break
            g.save()
    finally:
        await s.close()
        calls.close()
        model.send, check.CHECK_MODEL = real_send, real_check_model
    return summary(tag, dm_model, rounds_out, out)


def summary(tag: str, dm_model: str, rounds_out: list[dict[str, Any]], out: Path) -> dict[str, Any]:
    tot: dict[str, dict[str, float]] = {}
    for line in open(out / f"{tag}.calls.jsonl", encoding="utf-8"):
        c = json.loads(line)
        u = c.get("usage") or {}
        t = tot.setdefault(c["role"], {"calls": 0, "input": 0, "cache_read": 0, "cache_write": 0, "output": 0, "usd": 0.0})
        t["calls"] += 1
        t["input"] += u.get("input_tokens", 0)
        t["cache_read"] += u.get("cache_read_input_tokens", 0)
        t["cache_write"] += u.get("cache_creation_input_tokens", 0)
        t["output"] += u.get("output_tokens", 0)
        t["usd"] += cost(u, c["model"])
    n = max(len(rounds_out), 1)
    res = {"tag": tag, "model": dm_model, "rounds": len(rounds_out), "totals": tot,
           "dm_calls_per_round_median": statistics.median([r["dm_calls"] for r in rounds_out] or [0]),
           "refused": sum(r["refused"] for r in rounds_out), "failed": sum(r["failed"] for r in rounds_out),
           "stubs": sum(r["stubs"] for r in rounds_out),
           "dm_usd_per_round": round(tot.get("dm", {}).get("usd", 0) / n, 4),
           "all_usd_per_round": round(sum(t["usd"] for t in tot.values()) / n, 4)}
    (out / f"{tag}.metrics.json").write_text(json.dumps({"summary": res, "rounds": rounds_out}, indent=1), encoding="utf-8")
    return res


if __name__ == "__main__":
    load_keys()
    r = asyncio.run(play_game(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 20))
    print(json.dumps(r, indent=1))
