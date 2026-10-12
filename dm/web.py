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
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).parent.parent
SAVES = ROOT / "saves"
CHARACTERS = ("fighter", "rogue", "wizard", "new")

lock = threading.Lock()
proc: subprocess.Popen[bytes] | None = None
out = ""  # everything the current (or last) game printed


def saves() -> list[str]:
    """Saves that can be continued, newest first (a save that stopped during character creation can't be)."""
    names = []
    for p in sorted(SAVES.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            if "sheet" in json.loads(p.read_text(encoding="utf-8")):
                names.append(p.name)
        except (OSError, ValueError):
            pass
    return names


def read(p: subprocess.Popen[bytes]) -> None:
    global out
    dec = codecs.getincrementaldecoder("utf-8")("replace")
    while chunk := p.stdout.read1(4096):  # type: ignore[union-attr]
        with lock:
            out += dec.decode(chunk)
    p.wait()
    with lock:
        out += f"\n\n[the game ended (exit code {p.returncode})]\n"


def start(args: list[str]) -> None:
    global proc, out
    out = f"$ py -m dm.play {' '.join(args)}\n"
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
            self.reply(PAGE, "text/html; charset=utf-8")
        elif self.path.startswith("/out"):
            with lock:
                running = proc is not None and proc.poll() is None
                self.reply(json.dumps({"text": out, "running": running, "saves": [] if running else saves()}))
        else:
            self.reply("{}", code=404)

    def do_POST(self) -> None:
        data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        with lock:
            running = proc is not None and proc.poll() is None
            if self.path == "/start" and not running:
                if data.get("character") in CHARACTERS:
                    start([data["character"]])
                elif data.get("save") in saves():  # only names from the list: never an arbitrary path
                    start(["--resume", str(SAVES / data["save"])])
                else:
                    return self.reply('{"error": "unknown game"}', code=400)
            elif self.path == "/in" and running:
                line = str(data.get("line", "")).replace("\r", "").replace("\n", " ")
                proc.stdin.write((line + "\n").encode())  # type: ignore[union-attr]
                proc.stdin.flush()  # type: ignore[union-attr]
            else:
                return self.reply('{"error": "not now"}', code=409)
        self.reply("{}")

    def log_message(self, *a: object) -> None:
        pass  # keep the console quiet: polls would flood it


PAGE = """<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Game</title>
<style>
  body { margin: 0; background: #111; color: #ddd; font: 15px/1.45 ui-monospace, Consolas, monospace;
         display: flex; flex-direction: column; height: 100dvh; }
  #out { flex: 1; overflow-y: auto; padding: 12px 16px; white-space: pre-wrap; word-wrap: break-word; }
  #start { padding: 12px 16px; border-top: 1px solid #333; }
  #start button { margin: 4px 4px 4px 0; }
  form { display: flex; gap: 8px; padding: 8px 16px 12px; border-top: 1px solid #333; }
  input { flex: 1; min-width: 0; font: inherit; font-size: 16px; padding: 8px; background: #222; color: #eee;
          border: 1px solid #444; border-radius: 6px; }
  button { font: inherit; padding: 8px 12px; background: #2a2a2a; color: #eee; border: 1px solid #555;
           border-radius: 6px; }
  select { font: inherit; font-size: 16px; max-width: 100%; background: #222; color: #eee; }
</style></head><body>
<div id="out"></div>
<div id="start" hidden>
  <div>New game:
    <button onclick="go({character:'fighter'})">Fighter</button><button onclick="go({character:'rogue'})">Rogue</button>
    <button onclick="go({character:'wizard'})">Wizard</button><button onclick="go({character:'new'})">New</button>
  </div>
  <div>Continue: <select id="saves"></select> <button onclick="go({save:saves.value})">Go</button></div>
</div>
<form id="form" hidden><input id="line" autocomplete="off" placeholder="type here, or /sheet, /quit">
  <button>Send</button></form>
<script>
const out = document.getElementById("out"), line = document.getElementById("line");
let shown = null, savesShown = "";
async function post(path, body) {
  await fetch(path, {method: "POST", body: JSON.stringify(body)});
  poll();
}
function go(body) { post("/start", body); }
document.getElementById("form").onsubmit = e => {
  e.preventDefault();
  post("/in", {line: line.value});
  line.value = "";
};
async function poll() {
  let r;
  try { r = await (await fetch("/out")).json(); } catch { return; }
  if (r.text !== shown) {
    const atEnd = out.scrollHeight - out.scrollTop - out.clientHeight < 80;
    out.textContent = shown = r.text;
    if (atEnd) out.scrollTop = out.scrollHeight;
  }
  document.getElementById("form").hidden = !r.running;
  document.getElementById("start").hidden = r.running;
  if (!r.running && r.saves.join() !== savesShown) {
    savesShown = r.saves.join();
    saves.innerHTML = r.saves.map(s => `<option>${s}</option>`).join("");
  }
}
poll();
setInterval(poll, 1500);
</script></body></html>"""


def main() -> None:
    ap = argparse.ArgumentParser(description="Play the terminal game from a web page over Tailscale.")
    ap.add_argument("--port", type=int, default=8000)
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
