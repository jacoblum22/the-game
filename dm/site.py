"""The browser version of the game: builds it into build/site/ and serves it over Tailscale.

    py -3.12 -m dm.site            # build and serve on this PC's Tailscale address, port 8766
    py -3.12 -m dm.site --build    # only build: build/site/ is the whole site, for any static host

The site is two files: the page (dm/page.html) and game.zip, the game's code and the SRD, which the page runs with
Pyodide. Nothing runs on the server: it only hands out the files."""

from __future__ import annotations

import argparse
import hashlib
import io
import subprocess
import sys
import zipfile
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).parent.parent
OUT = ROOT / "build" / "site"
LEFT_OUT = {"web.py", "web.html", "page.html", "site.py", "convert.py", "sdk.py"}  # the server, the page, the tools, the SDK


def build() -> None:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted((ROOT / "dm").rglob("*")):
            if p.is_file() and "__pycache__" not in p.parts and p.name not in LEFT_OUT:
                z.write(p, p.relative_to(ROOT).as_posix())
    data = buf.getvalue()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "game.zip").write_bytes(data)
    version = hashlib.sha1(data).hexdigest()[:10]  # a new name for each build, so no browser keeps an old one
    page = (ROOT / "dm" / "page.html").read_text(encoding="utf-8").replace("GAME_ZIP", f"game.zip?v={version}")
    (OUT / "index.html").write_text(page, encoding="utf-8")
    print(f"Built {OUT}: game.zip {len(data) // 1024} KB")


def main() -> None:
    ap = argparse.ArgumentParser(description="Build the browser version of the game, and serve it over Tailscale.")
    ap.add_argument("--build", action="store_true", help="only build")
    ap.add_argument("--port", type=int, default=8766)
    args = ap.parse_args()
    build()
    if args.build:
        return
    try:
        host = subprocess.run(["tailscale", "ip", "-4"], capture_output=True, text=True, check=True).stdout.split()[0]
    except (OSError, subprocess.CalledProcessError, IndexError):
        sys.exit("Couldn't get this PC's Tailscale address: is Tailscale running?")
    print(f"Open http://{host}:{args.port} on a device in your Tailscale network. Ctrl+C stops.")

    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self, *a: object) -> None:
            pass
    ThreadingHTTPServer((host, args.port), partial(Quiet, directory=str(OUT))).serve_forever()


if __name__ == "__main__":
    main()
