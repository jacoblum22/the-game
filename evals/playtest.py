"""Automated playtest: the real `python -m play` CLI and engine, with a simulated player typing the input.

No Gemini call and no API spend. The engine's model is either the free offline stand-in (`--engine offline`) or
Claude through the Claude Code CLI on the owner's subscription (`--engine claude`). The player is Claude in the
same way (`--player claude`) or a fixed script (`--player script`). Only the model is swapped: prompts, packets,
schemas, the claim check and every rule run exactly as in `python -m play`.

    py -3.12 evals/playtest.py --engine offline --player script --inputs 40     # free, no Claude at all
    py -3.12 evals/playtest.py --engine offline --player claude --inputs 40
    py -3.12 evals/playtest.py --engine claude --player claude --inputs 30

Writes saves/playtest-<stamp>.db and evals/playtests/<stamp>.md: the transcript, with the player's notes (what
confused or annoyed them) beside each line. The Claude CLI must be logged in once (`claude` then `/login`).
"""

from __future__ import annotations

import argparse
import glob
import io
import json
import os
import random
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engine.game import GameConfig  # noqa: E402
from engine.llm.base import CallResult, ModelUnavailable, Packet, Role, Stopwatch, new_record  # noqa: E402
from engine.llm.offline import conform  # noqa: E402
from play.cli import main as play_main  # noqa: E402

OUT = ROOT / "evals" / "playtests"
MAX_INLINE_SCHEMA = 24000  # Windows caps a command line near 32k chars; bigger schemas go in the prompt


def claude_bin() -> str:
    if os.environ.get("CLAUDE_BIN"):
        return os.environ["CLAUDE_BIN"]
    found = sorted(glob.glob(os.path.expandvars(r"%APPDATA%\Claude\claude-code\*\*\claude.exe")),
                   key=os.path.getmtime)
    if not found:
        raise SystemExit("no claude CLI found: set CLAUDE_BIN")
    return found[-1]


def ask_claude(system: str, prompt: str, schema: dict[str, Any], model: str) -> tuple[Any, dict[str, Any]]:
    """One headless Claude call returning JSON for `schema`. Runs in a temp dir so no project CLAUDE.md loads."""
    # no MCP servers, plugins, hooks or settings: halves the CLI's start-up (about 8 s to 4 s per call)
    cmd = [claude_bin(), "-p", "--output-format", "json", "--tools", "", "--no-session-persistence",
           "--strict-mcp-config", "--setting-sources", "project", "--model", model]
    schema_text = json.dumps(schema)
    if len(schema_text) <= MAX_INLINE_SCHEMA:
        cmd += ["--json-schema", schema_text]
    else:
        prompt += "\n\nAnswer with one JSON object only, no prose, valid for this JSON Schema:\n" + schema_text
    with tempfile.TemporaryDirectory() as tmp:
        sp = Path(tmp) / "system.md"
        sp.write_text(system, encoding="utf-8")
        cmd += ["--system-prompt-file", str(sp)]
        for attempt in range(3):
            proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True, encoding="utf-8", cwd=tmp,
                                  timeout=600)
            try:
                out = json.loads(proc.stdout)
            except json.JSONDecodeError:
                out = {"is_error": True, "result": (proc.stdout or proc.stderr)[-500:]}
            if not out.get("is_error"):
                break
            time.sleep(5 * (attempt + 1))
        else:
            raise ModelUnavailable(f"claude CLI: {out.get('result')}")
    data = out.get("structured_output")
    if data is None:
        text = str(out.get("result") or "").strip().removeprefix("```json").removeprefix("```").removesuffix("```")
        data = json.loads(text[text.find("{"): text.rfind("}") + 1])
    return data, out


class ClaudeModel:
    """`StructuredModel` over the Claude Code CLI. The packet is rendered exactly as for Gemini."""

    provider = "claude-cli"

    def __init__(self, model: str):
        self.model = model
        self.calls = 0

    def fill(self, role: Role, schema: dict[str, Any], packet: Packet, *, turn_id: str | None, attempt: int,
             seq: int = 0) -> CallResult:
        watch = Stopwatch()
        raw, meta = ask_claude(packet.instructions, packet.render(include_instructions=False), schema, self.model)
        data = conform(raw, schema, schema)  # the engine validates too; this only repairs enum spelling
        self.calls += 1
        usage = meta.get("usage") or {}
        rec = new_record(role, schema, provider=self.provider, model_id=self.model, turn_id=turn_id,
                         attempt=attempt, seq=seq, request={"attempt": attempt, "packet": packet.render()})
        rec = rec.model_copy(update={"response": {"data": data, "text": None, "error": None},
                                     "latency_ms": watch.ms(), "tokens_in": int(usage.get("input_tokens") or 0)
                                     + int(usage.get("cache_read_input_tokens") or 0),
                                     "tokens_out": int(usage.get("output_tokens") or 0)})
        return CallResult(data=data, record=rec)


PERSONA = """You are playtesting a text tabletop RPG in a terminal, playing as its owner: someone who loves
tabletop RPGs, is new to this game, and wants a vivid world to act in. You read the game's latest output and
type the next line, as a real player would: short, in your own words, sometimes a number to pick a menu option,
sometimes empty to accept the default. Over the session try varied things: set-up choices, asking to set the
scene, looking around, talking to someone, asking "what are my options?", a risky action, travel, rest, and
asking what you know. If something the game says seems wrong, type /fix and say what, as a real player would.
Stay in character as a player, never as a tester. In `note`, say briefly and honestly
anything that confused, bored or annoyed you about the last output (thin description, a dead end, a broken
menu, repeated text, an error, rules jargon), or "" if it was fine. The note is about the newest output only
(after your last line); do not repeat complaints about earlier screens."""
PERSONAS = {
    "explorer": "This session you love exploring: ask to set the scene, look closely at places, travel to new ones, "
                "rest, and ask what you know about the land.",
    "talker": "This session you love talking: seek out people, ask them questions, persuade, bargain, and ask what "
              "you know about them.",
    "fighter": "This session you want danger: take risky actions, pick a fight when one is offered, push through "
               "warnings, and see how the odds screens work.",
    "breaker": "This session you are a curious, slightly chaotic player: give odd or ambiguous answers, misuse menus "
               "now and then, ask rules questions, ask for options, and change your mind.",
    "newcomer": "This session you are brand new to tabletop RPGs: you are unsure what to type, ask for help, keep "
                "answers short, and follow whatever the game suggests.",
}
PLAYER_SCHEMA = {"type": "object", "properties": {"say": {"type": "string"}, "note": {"type": "string"}},
                 "required": ["say", "note"], "additionalProperties": False}
SCRIPT = ["2", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "3", "1", "1", "1",
          "Could you set the scene?", "I look around the square.", "what are my options?",
          "I walk over to the smithy and greet the smith.", "Ask her what the omen in the sky means.",
          "what do I know?", "I climb the wall to get a better look at the road.", "1",
          "I head to the inn and ask the innkeeper about the ford.", "I rest for the night.", "",
          "I set out along the north road.", "I look for tracks.", "what are my options?", "I go back to town."]


class Player(io.TextIOBase):
    """stdin for the CLI: each readline() shows the player everything printed since, and returns their line."""

    def __init__(self, out: io.StringIO, kind: str, model: str, limit: int, persona: str = "explorer",
                 quick_setup: bool = False, seed: int = 0):
        self.out, self.kind, self.model, self.limit = out, kind, model, limit
        self.persona = PERSONA + "\n\n" + PERSONAS[persona]
        self.quick_setup = quick_setup
        self.pick = random.Random(seed)
        self.seen = 0
        self.lines: list[tuple[str, str, str]] = []  # (game output since last input, player line, note)
        self.play_inputs = 0  # inputs after "The story begins": the limit counts these

    def _setup_answer(self, new: str) -> str:
        """Quick setup: the dice build the world, then a random ready-made character, all defaults kept."""
        if "decide what the world is like" in new:
            return "2"
        if "How do you want to make your character" in new:
            return "3"
        if "A ready-made character" in new and "Pick one" in new:
            return str(self.pick.randint(1, 4))
        return ""  # Enter: keep the default

    def readline(self, size: int = -1) -> str:  # noqa: ARG002
        text = self.out.getvalue()
        new, self.seen = text[self.seen:], len(text)
        in_play = "The story begins." in text
        if in_play:
            self.play_inputs += 1
        if self.play_inputs > self.limit or len(self.lines) > self.limit + 60:
            self.lines.append((new, "(end of playtest)", ""))
            return ""
        if self.quick_setup and not in_play:
            say, note = self._setup_answer(new), ""
        elif self.kind == "script":
            say, note = SCRIPT[len(self.lines) % len(SCRIPT)], ""
        else:
            recent = text[-9000:]
            try:
                d, _ = ask_claude(self.persona, f"THE TERMINAL SO FAR (latest at the end):\n{recent}\n\nYour next line:",
                                  PLAYER_SCHEMA, self.model)
                say, note = str(d.get("say", "")).replace("\n", " ").strip(), str(d.get("note", "")).strip()
            except Exception as e:  # noqa: BLE001 - a player failure ends the run, it is not a game bug
                self.lines.append((new, "(player failed)", repr(e)))
                return ""
        self.lines.append((new, say, note))
        self.out.write(say + "\n")  # echo, as a terminal would, so the player sees what it typed
        self.seen = len(self.out.getvalue())
        print(f"[{len(self.lines)}] > {say}" + (f"   ({note})" if note else ""), flush=True)
        return say + "\n"


def report(path: Path, args: argparse.Namespace, player: Player, engine: Any, save: Path, secs: float) -> None:
    lines = [f"# Playtest {path.stem}", "",
             f"engine: {args.engine}; player: {args.player}; inputs: {len(player.lines)}; "
             f"engine model calls: {getattr(engine, 'calls', 'n/a')}; {secs / 60:.1f} min; save: `{save.name}`", "",
             "## Player notes", ""]
    notes = [(i, s, n) for i, (_, s, n) in enumerate(player.lines, 1) if n]
    lines += [f"- [{i}] after typing `{s}`: {n}" for i, s, n in notes] or ["- none"]
    lines += ["", "## Transcript", ""]
    for i, (out, say, note) in enumerate(player.lines, 1):
        lines += ["```text", out.rstrip(), "```", f"**[{i}] player:** `{say}`" + (f"  \n*note: {note}*" if note else ""), ""]
    path.write_text("\n".join(lines), encoding="utf-8")


LEAK_MARKERS = ("Traceback", "validation error", "Error:", "Exception", "pydantic", "KeyError", "TypeError",
                "ValueError", "AttributeError", "Input should be")


def write_findings(path: Path, player: Player, save: Path, code: int) -> int:
    """Machine-readable findings for triage: leaked errors, fallbacks, redrafts and their failing claims, model-call
    failures, repeated output, the exit code, and every player note."""
    import sqlite3

    rows: list[dict[str, Any]] = []
    for i, (out, say, note) in enumerate(player.lines, 1):
        hits = [m for m in LEAK_MARKERS if m in out]
        if hits:
            line = next((ln for ln in out.splitlines() if any(m in ln for m in hits)), "")
            rows.append({"kind": "leaked_error", "input": i, "markers": hits, "line": line[:300]})
        if i > 1 and out.strip() and out.strip() == player.lines[i - 2][0].strip():
            rows.append({"kind": "repeated_output", "input": i, "text": out.strip()[:200]})
        if note:
            rows.append({"kind": "player_note", "input": i, "typed": say, "note": note})
    if code != 0:
        rows.append({"kind": "exit_code", "code": code})
    if save.exists():
        db = sqlite3.connect(f"file:{save.as_posix()}?mode=ro", uri=True)
        for tid, inp, fb, rec in db.execute("select turn_id, input_verbatim, fallback_used, record from turns"):
            r = json.loads(rec or "{}")
            versions = r.get("draft_versions") or []
            redrafts = sum(1 for v in versions if v.get("kind") == "redraft")
            fails = [f"{v.get('verdict')}: {v.get('reason', '')}"[:160] for dv in versions
                     for v in dv.get("verdicts") or [] if v.get("verdict") != "supported"]
            if fb or redrafts:
                rows.append({"kind": "fallback" if fb else "redraft", "turn": tid, "input": inp[:120],
                             "redrafts": redrafts, "failing": fails[:8],
                             "reasons": [x for dv in versions for x in dv.get("reasons") or []][:4]})
        for role, outcome, n in db.execute("select role, outcome, count(*) from model_calls where outcome != 'ok' "
                                           "group by role, outcome"):
            rows.append({"kind": "model_call_failure", "role": role, "outcome": outcome, "count": n})
        calls = dict(db.execute("select role, count(*) from model_calls group by role").fetchall())
        turns = db.execute("select count(*) from turns").fetchone()[0]
        rows.append({"kind": "stats", "turns": turns, "calls": calls,
                     "narrator_per_turn": round(calls.get("narrator", 0) / turns, 2) if turns else None})
        db.close()
    path.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    return len(rows)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", choices=("offline", "claude"), default="offline")
    ap.add_argument("--player", choices=("script", "claude"), default="script")
    ap.add_argument("--turns", type=int, default=15, help="player inputs after the story begins")
    ap.add_argument("--quick-setup", action="store_true", help="script world-building and a ready-made character")
    ap.add_argument("--engine-model", default="haiku")
    ap.add_argument("--player-model", default="sonnet")
    ap.add_argument("--persona", choices=sorted(PERSONAS), default="explorer")
    ap.add_argument("--out", type=Path, default=OUT, help="where transcripts and findings go")
    ap.add_argument("--saves", type=Path, default=ROOT / "saves")
    args = ap.parse_args()

    stamp = time.strftime("%Y%m%d-%H%M%S")
    name = f"playtest-{stamp}-{args.persona}"
    engine = ClaudeModel(args.engine_model) if args.engine == "claude" else None

    class Config(GameConfig):
        def model(self) -> Any:  # only the model differs from `python -m play`
            return engine if engine is not None else super().model()

    out = io.StringIO()
    player = Player(out, args.player, args.player_model, args.turns, args.persona, args.quick_setup,
                    seed=int(stamp.replace("-", "")))
    start = time.time()
    args.saves.mkdir(parents=True, exist_ok=True)
    code = play_main(["new", name], stdin=player, stdout=out, saves=args.saves,
                     config=lambda _offline: Config(offline=args.engine == "offline"))
    player.lines.append((out.getvalue()[player.seen:], f"(exit {code})", ""))
    args.out.mkdir(parents=True, exist_ok=True)
    path = args.out / f"{stamp}-{args.engine}-{args.persona}.md"
    save = args.saves / f"{name}.db"
    report(path, args, player, engine, save, time.time() - start)
    n = write_findings(path.with_suffix(".findings.jsonl"), player, save, code)
    print(f"report: {path}  (exit {code}, {len(player.lines)} inputs, {n} findings)")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
