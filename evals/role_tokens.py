"""Per-role input tokens from a store's recorded model calls (spec 020, F3: measure before and after).

    py -3.12 evals/role_tokens.py <game.db> [<game.db> ...]

For each role: calls, mean input tokens per call (characters / 4) and the mean per packet section, from
`model_calls.request.packet`. Run it on two stores of the same seeded script (`evals/longhorizon.py --mode scripted
--keep DIR`) to compare packet builders. The store is opened read-only.
"""

from __future__ import annotations

import json
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from evals.longhorizon import tokens  # noqa: E402
from evals.replay_bench import sections  # noqa: E402


def role_tokens(db: Path) -> dict[str, dict[str, float]]:
    """{role: {"calls": n, "total": mean tokens, <section>: mean tokens}} over every call's first attempt."""
    con = sqlite3.connect(f"file:{db.as_posix()}?immutable=1", uri=True)
    sums: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for role, req in con.execute("select role, request from model_calls where attempt = 0"):
        packet = (json.loads(req or "{}") or {}).get("packet") or ""
        s = sums[role]
        s["calls"] += 1
        s["total"] += tokens(packet)
        for name, text in sections(packet):
            s[name] += tokens(text)
    return {r: {k: (v if k == "calls" else v / s["calls"]) for k, v in s.items()} for r, s in sorted(sums.items())}


def main(argv: list[str]) -> int:
    for db in map(Path, argv):
        print(f"## {db.name}")
        for role, s in role_tokens(db).items():
            parts = ", ".join(f"{k} {v:.0f}" for k, v in s.items() if k not in ("calls", "total"))
            print(f"- {role}: {int(s['calls'])} calls, {s['total']:.0f} tokens per call ({parts})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
