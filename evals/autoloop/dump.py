"""A block of an autoloop game as text, round by round, for reading: the player's line, the game's lines, the DM's
hidden notebook writes and lookups (marked), and the reply. Earlier rounds are summarised by the notebook only.
    py -3.12 evals/autoloop/dump.py <name> <first> <last> <out.txt>"""
import json
import sys
from pathlib import Path

from metrics import GAMES, rounds

name, first, last, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), Path(sys.argv[4])
meta = json.loads((GAMES / f"{name}.meta.json").read_text(encoding="utf-8"))
save = json.loads((GAMES / Path(meta["save"]).name).read_text(encoding="utf-8"))
t = save["transcript"]
lines = [f"CHARACTER: {save['sheet']['name']}, {save['sheet']['summary']}"]
opening = "\n\n".join(e["text"] for e in t[meta["play_starts"]:] if e["kind"] == "dm" and not any(
    x["kind"] == "player" for x in t[meta["play_starts"]:t.index(e)]))
if first == 1:
    lines.append("== OPENING ==\n" + opening)
for n, r in enumerate(rounds(t, meta["play_starts"])[first - 1:last], first):
    lines.append(f"\n== ROUND {n} ==")
    for e in r:
        k = e["kind"]
        if k == "player":
            lines.append(f"PLAYER: {e['text']}")
        elif k == "tool":
            lines.append(f"  [game] {e['text']}")
        elif k == "refused":
            lines.append(f"  [refused] {e['text']}")
        elif k == "call":
            lines.append(f"  [DM {e['tool']} (hidden)] {json.dumps(e.get('input'), ensure_ascii=False)[:400]}")
        elif k in ("stub", "hidden"):
            lines.append(f"  [{k}, not shown] {e['text']}")
        elif k == "dm":
            lines.append(f"DM: {e['text']}")
out.write_text("\n".join(lines), encoding="utf-8")
print(f"{out}: {len(lines)} lines")
