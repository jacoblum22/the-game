"""Spec 019: cut the round-6 talker turns I1 names out of the real save into a small test fixture (read-only).

    py -3.12 specs/019-holistic-narration/extract_fixture.py C:/Users/Nelly/Documents/the-game/saves/playtest-20261008-232941-talker.db

Per turn: the first narrator packet's NARRATOR VIEW and THIS MESSAGE, the first draft as the model returned it
(declared sentences), the delivered text, the player's input, and each draft version's kind. Written to
tests/fixtures/round6_narration.json (the saves are gitignored, so the test cannot read them).
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from evals.replay_bench import sections  # noqa: E402

TURNS = {
    "turn.2": "stacked quotes: two of the four back-to-back quotes came from blind add-repairs (I1 §1, §5b)",
    "turn.13": "duplicated answer: two add-repairs each said 'Mark me ... a child gone since last night' (I1 §5b)",
    "turn.14": "echoed player line: the answered check demanded an answer to a statement; the blind add restated "
               "the player's line and ended the passage on it (I1 §2)",
    "turn.16": "speech left unquoted: first-person words in the narrator's voice (I1 §7)",
}


def main(argv: list[str]) -> int:
    path = Path(argv[0])
    con = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
    out = []
    for tid, why in TURNS.items():
        rec = json.loads(con.execute("select record from turns where turn_id=?", (tid,)).fetchone()[0])
        req, resp = con.execute("select request, response from model_calls where turn_id=? and role='narrator' "
                                "order by row_id limit 1", (tid,)).fetchone()
        sec = dict(sections(str(json.loads(req)["packet"])))
        data = json.loads(resp)["data"]
        out.append({"save": path.stem, "turn": tid, "why": why, "input": rec.get("input_verbatim") or "",
                    "NARRATOR VIEW": sec.get("NARRATOR VIEW", ""), "THIS MESSAGE": sec.get("THIS MESSAGE", ""),
                    "first_draft": [{"text": s["text"], "speaker": s.get("speaker")} for s in data["sentences"]],
                    "versions": [v.get("kind") for v in rec.get("draft_versions") or []],
                    "delivered": rec.get("delivered_verbatim") or ""})
    dest = ROOT / "tests" / "fixtures" / "round6_narration.json"
    dest.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{dest}: {len(out)} turns, {dest.stat().st_size // 1024} KiB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
