"""Unblind the judges' verdicts (blind.py's key.json + judge*.jsonl in the same folder): per arm, how many replies had
a contradiction, repeated the original one, acted for the PC, ended in a menu, read out the sheet or ended
unclearly (JUDGE.md); and per round.
    py -3.12 evals/autoloop/score.py <blind folder>"""
import json
import sys
from collections import defaultdict
from pathlib import Path

d = Path(sys.argv[1])
key = json.loads((d / "key.json").read_text(encoding="utf-8"))
tot: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
per: dict[tuple[str, str], list[int]] = defaultdict(lambda: [0, 0, 0])
for f in d.glob("judge*.jsonl"):
    for line in f.read_text(encoding="utf-8").splitlines():
        if not line.strip().startswith("{"):
            continue
        v = json.loads(line)
        arm, rnd = key[v["code"]], v["code"].split("-")[0]
        t = tot[arm]
        t["n"] += 1
        for k in ("contradiction", "repeats_original", "agency", "menu", "sheet_readout", "unclear_end"):
            if k in v:
                t[k] += int(v.get(k) or 0)
        p = per[(rnd, arm)]
        p[0] += 1
        p[1] += int(v.get("contradiction") or 0)
        p[2] += int(v.get("agency") or 0)
for arm in sorted(tot):
    print(arm, dict(tot[arm]))
print("\nper round: replies / contradictions / agency")
for rnd in sorted({r for r, _ in per}):
    print(rnd, "  ".join(f"{a}:{'/'.join(map(str, per[(rnd, a)]))}" for a in sorted(tot) if (rnd, a) in per))
