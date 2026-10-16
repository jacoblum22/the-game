"""Blind packets for judging replay replies: per round, the three rounds before it (as dump.py writes them), what the
readers found there, and every arm's replies shuffled under codes. The key (code -> arm) is written separately.
    py -3.12 evals/autoloop/blind.py <replay folder> <out folder> [block, e.g. 61-120; default 1-60]"""
import json
import random
import re
import sys
from collections import defaultdict
from pathlib import Path

READ = Path(__file__).parent / "games" / "read"
src, out = Path(sys.argv[1]), Path(sys.argv[2])
BLOCK = sys.argv[3] if len(sys.argv) > 3 else "1-60"
out.mkdir(exist_ok=True)
by_round: dict[tuple[str, int], list[tuple[str, dict]]] = defaultdict(list)
for f in sorted(src.glob("*.json")):
    arm, game = f.stem.split("-")
    for r in json.loads(f.read_text(encoding="utf-8")):
        if "error" not in r:
            by_round[(game, r["round"])].append((arm, r))
key = {}
rng = random.Random(7)
for (game, k), runs in sorted(by_round.items()):
    dump = (READ / f"{game}-{BLOCK}.txt").read_text(encoding="utf-8")
    parts = re.split(r"\n(?=== ROUND \d+ ==)", dump)
    before = [p for p in parts if (m := re.match(r"== ROUND (\d+) ==", p)) and k - 3 <= int(m.group(1)) < k]
    found = [x for x in (READ / f"{game}-{BLOCK}.findings.txt").read_text(encoding="utf-8").splitlines()
             if x.startswith("{") and json.loads(x)["round"] == k]
    rng.shuffle(runs)
    lines = [f"GAME {game}, ROUND {k}", "", "THE THREE ROUNDS BEFORE (the original game):", *before, "",
             "WHAT READERS FOUND WRONG IN THE ORIGINAL REPLY TO THIS ROUND (the established facts it broke):", *found, "",
             f"THE PLAYER'S LINE THIS ROUND: {runs[0][1]['line']}", ""]
    for i, (arm, r) in enumerate(runs, 1):
        code = f"{game[:2]}{k}-{i:02d}"
        key[code] = arm
        reply = "\n\n".join(e["text"] for e in r["entries"] if e["kind"] == "dm" and e["text"])
        calls = [f"{e['text']}: {json.dumps(e.get('input'), ensure_ascii=False)[:200]}" for e in r["entries"] if e["kind"] == "call"]
        lines += [f"=== REPLY {code} ===", *(f"  [hidden call] {c}" for c in calls), reply, ""]
    (out / f"{game}-{k}.txt").write_text("\n".join(lines), encoding="utf-8")
(out / "key.json").write_text(json.dumps(key, indent=0), encoding="utf-8")
print(f"{len(by_round)} rounds, {len(key)} replies -> {out}")
