"""List every repair round in the given saves: the failing sentence + reason, missing items, and what came back.
Usage: repairs.py <save.db> [...]"""
import json
import sqlite3
import sys

for path in sys.argv[1:]:
    db = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    print(f"\n######## {path.split('/')[-1]}")
    for tid, inp, rec in db.execute("select turn_id, input_verbatim, record from turns order by rowid"):
        r = json.loads(rec or "{}")
        vers = r.get("draft_versions") or []
        reps = [v for v in vers if v.get("kind") == "repair"]
        if not reps:
            continue
        print(f"\n== {tid} | player: {inp[:150]!r}")
        prev = vers[0]
        for v in vers[1:]:
            if v.get("kind") != "repair":
                prev = v
                continue
            psents = [s.get("text", "") for s in prev.get("sentences", [])]
            for fx in v.get("fixes") or []:
                idx = fx.split("]", 1)[0].lstrip("[")
                orig = psents[int(idx)] if idx.isdigit() and int(idx) < len(psents) else "?"
                print(f"   FIX  sentence: {orig[:170]!r}\n        reason: {fx.split(']', 1)[1].strip()[:200]}")
            for m in v.get("missing") or []:
                print(f"   MISSING: {m[:200]}")
            new = [s.get("text", "") for s in v.get("sentences", [])]
            added = [t for t in new if t not in psents]
            for t in added:
                print(f"   -> new/changed: {t[:170]!r}")
            prev = v
        print(f"   DELIVERED: {(r.get('delivered_verbatim') or '')[:260]!r}")
