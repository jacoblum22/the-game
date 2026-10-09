"""Spec 019: how precise would the new passage-level checks be? Read-only over recorded games' delivered fiction.

    py -3.12 specs/019-holistic-narration/measure_checks.py <save.db> [...]

- `first_person`: a first-person word ("I", "my", "we", ...) in the narrator's voice (outside quote marks) of a
  delivered sentence: the quote-mark check's second half (12.3.1a item 2). Every hit is printed for judging.
"""

from __future__ import annotations

import json
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from engine.audit.claims import beat_polarity, passage_beat  # noqa: E402
from engine.audit.declare import first_person  # noqa: E402
from engine.dm.adjudication import BeatEntry  # noqa: E402
from engine.llm.offline import sentences  # noqa: E402

_Q = re.compile(r"[\"“][^\"”“]*[\"”]")


def _fiction(text: str) -> str:
    return "\n".join(ln for ln in (text or "").splitlines()
                     if not (ln.lstrip().startswith(("[", ">")) or ln[:1].isspace() or re.match(r"\d+\) ", ln)))


_DEGREE = {"critical success": "critical_success", "critical failure": "critical_failure", "success": "success",
           "failure": "failure", "success at cost": "success"}


def _beats(request: str) -> list[BeatEntry]:
    """The turn's beats from its first narrator packet's record lines (`beat: ...; result: <degree>`)."""
    out = []
    for m in re.finditer(r"(?m)^- (?:R\d+(?: MUST)?: )?beat: (.*)$", request):
        line = m.group(1)
        res = re.search(r"result: ([a-z ]+)", line)
        deg = _DEGREE.get(res.group(1).split(" (")[0].strip().removesuffix(", a near miss").strip()) if res else None
        out.append(BeatEntry(restatement="", degree=deg, success_at_cost="success at cost" in line,
                             gate_words="no roll" if "no roll" in line and not deg else ""))
    return out


def main(argv: list[str]) -> int:
    n = hits = pol = 0
    for a in argv:
        con = sqlite3.connect(f"file:{Path(a).as_posix()}?mode=ro", uri=True)
        try:
            rows = list(con.execute("select turn_id, delivered_verbatim from turns"))
            reqs = {}
            for tid, req in con.execute("select turn_id, request from model_calls where role='narrator' "
                                        "order by row_id"):
                reqs.setdefault(tid, str((json.loads(req or "{}") or {}).get("packet") or ""))
        except sqlite3.Error:
            continue
        for tid, d in rows:
            beat = passage_beat(_beats(reqs.get(tid, "")))
            for s in sentences(_fiction(d or "")):
                n += 1
                w = first_person(s)
                if w:
                    hits += 1
                    print(f"- first_person {Path(a).stem.removeprefix('playtest-')} {tid} {w!r}: {s[:220]!r}")
                deg = beat_polarity(_Q.sub(" ", s), beat) if beat is not None else None
                if deg:
                    pol += 1
                    print(f"- polarity {Path(a).stem.removeprefix('playtest-')} {tid} ({deg}): {s[:220]!r}")
    print(f"sentences {n}; first-person hits {hits}; passage polarity hits {pol}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
