"""Spec 019: print each narrated turn of a save (read-only): input, draft version kinds, what failed, the revision,
the delivered fiction and the side list's speech. For reading a live run.

    py -3.12 specs/019-holistic-narration/show_turns.py <save.db>
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path


def main(argv: list[str]) -> int:
    con = sqlite3.connect(f"file:{Path(argv[0]).as_posix()}?mode=ro", uri=True)
    for tid, rec_json in con.execute("select turn_id, record from turns"):
        rec = json.loads(rec_json or "{}")
        dv = rec.get("draft_versions") or []
        if not dv:
            continue
        print(f"== {tid} {[v.get('kind') for v in dv]} | {str(rec.get('input_verbatim') or '')[:160]}")
        for v in dv:
            fails = [f"{i}: {f['why']}" for i, fs in (v.get("checks") or {}).items() for f in fs]
            extra = fails + [f"missing {h}" for h in v.get("missing") or []] + \
                [f"unquoted {w[:80]}" for w in v.get("unquoted") or []] + [f"quoted {w[:60]}" for w in v.get("quoted") or []]
            if extra:
                print(f"   [{v.get('kind')}] " + " | ".join(extra))
            if v.get("kind") == "revision":
                print(f"   revision: {v.get('text', '')[:400]}")
        speech = (dv[-1].get("side_list") or dv[0].get("side_list") or {}).get("speech") or []
        print("   speech: " + " || ".join(f"{s.get('speaker')}: {s.get('words', '')[:70]}" for s in speech))
        print("   " + str(rec.get("delivered_verbatim") or "").replace("\n", "\n   ")[:1600])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
