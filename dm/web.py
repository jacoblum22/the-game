"""The terminal game in a web page, for playing from a phone over Tailscale.

    py -3.12 -m dm.web

Runs `dm.play` exactly as the terminal would and passes its text back and forth: the page shows what the game
prints and sends what you type. One game at a time. Listens only on this PC's Tailscale address."""

from __future__ import annotations

import argparse
import codecs
import json
import os
import socket
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).parent.parent
SAVES = ROOT / "saves"
CHARACTERS = ("fighter", "rogue", "wizard", "new")

lock = threading.Lock()
proc: subprocess.Popen[bytes] | None = None
out = ""  # everything the current (or last) game printed


def saves() -> list[dict[str, str]]:
    """Saves that can be continued, newest first (a save that stopped during character creation can't be)."""
    found = []
    for p in sorted(SAVES.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if "sheet" in data:
            when = time.strftime("%b %d, %I:%M %p", time.localtime(p.stat().st_mtime)).replace(" 0", " ")
            found.append({"file": p.name, "name": data["sheet"]["name"], "when": when})
    return found


def read(p: subprocess.Popen[bytes]) -> None:
    global out
    dec = codecs.getincrementaldecoder("utf-8")("replace")
    while chunk := p.stdout.read1(4096):  # type: ignore[union-attr]
        with lock:
            out += dec.decode(chunk)
    p.wait()
    with lock:
        out += f"\n\n[the game ended (exit code {p.returncode})]\n"


def history(save: Path) -> str:
    """The game so far, from the save, in the shape the terminal printed it. Continuing a save prints only the DM's
    last reply, so that one is left out here."""
    t = json.loads(save.read_text(encoding="utf-8"))["transcript"]
    last = max((i for i, e in enumerate(t) if e["kind"] == "dm"), default=-1)
    text = ""
    for i, e in enumerate(t):
        if e["kind"] == "dm" and i != last:
            text += f"\n{e['text']}\n"
        elif e["kind"] == "player":
            text += f"\n> {e['text']}\n"
        elif e["kind"] == "tool":
            text += f"  [{e['text']}]\n"
        elif e["kind"] == "call" and e["tool"] == "roll_ability_scores" and not e["error"]:
            text += f"  [{e['result']}]\n"
    return text


def start(args: list[str]) -> None:
    global proc, out
    out = history(Path(args[1])) if args[0] == "--resume" else ""
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUNBUFFERED": "1"}
    proc = subprocess.Popen([sys.executable, "-u", "-m", "dm.play", *args], cwd=ROOT, env=env,
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    threading.Thread(target=read, args=(proc,), daemon=True).start()


class Handler(BaseHTTPRequestHandler):
    def reply(self, body: bytes | str, kind: str = "application/json", code: int = 200) -> None:
        body = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/":
            self.reply((ROOT / "dm" / "web.html").read_bytes(), "text/html; charset=utf-8")
        elif self.path.startswith("/out"):
            with lock:
                running = proc is not None and proc.poll() is None
                self.reply(json.dumps({"text": out, "running": running, "saves": [] if running else saves()}))
        else:
            self.reply("{}", code=404)

    def do_POST(self) -> None:
        global out
        data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        with lock:
            running = proc is not None and proc.poll() is None
            if self.path == "/start" and not running:
                if data.get("character") in CHARACTERS:
                    start([data["character"]])
                elif data.get("save") in [s["file"] for s in saves()]:  # only names from the list: never an arbitrary path
                    start(["--resume", str(SAVES / data["save"])])
                else:
                    return self.reply('{"error": "unknown game"}', code=400)
            elif self.path == "/in" and running:
                line = str(data.get("line", "")).replace("\r", "").replace("\n", " ")
                out += line + "\n"  # a terminal echoes what you type; a pipe doesn't
                proc.stdin.write((line + "\n").encode())  # type: ignore[union-attr]
                proc.stdin.flush()  # type: ignore[union-attr]
            else:
                return self.reply('{"error": "not now"}', code=409)
        self.reply("{}")

    def log_message(self, *a: object) -> None:
        pass  # keep the console quiet: polls would flood it


def main() -> None:
    ap = argparse.ArgumentParser(description="Play the terminal game from a web page over Tailscale.")
    ap.add_argument("--port", type=int, default=8765)
    port = ap.parse_args().port
    try:
        host = subprocess.run(["tailscale", "ip", "-4"], capture_output=True, text=True, check=True).stdout.split()[0]
    except (OSError, subprocess.CalledProcessError, IndexError):
        sys.exit("Couldn't get this PC's Tailscale address: is Tailscale running?")
    name = socket.gethostname().lower()
    print(f"Open http://{name}:{port} (or http://{host}:{port}) on a device in your Tailscale network. Ctrl+C stops.")
    ThreadingHTTPServer((host, port), Handler).serve_forever()


if __name__ == "__main__":
    main()
