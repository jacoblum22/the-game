"""Spec 019's narration measures over recorded games (read-only), the I1 baselines' definitions:

    py -3.12 specs/019-holistic-narration/metrics.py <save.db> [<save.db> ...]

Per save and in total, over narrated turns (a turn whose record has a draft):
- stacked quotes: two quoted spans with only white space between them (`"..." "..."`), in the delivered fiction;
- echoed player lines: a quote (3+ content words) at least 80% made of that turn's player input;
- duplicated answers: two quotes in one turn's fiction sharing at least half their content words;
- first draft delivered: the turn's only version is its first draft (no revision, cut, rendered line or fallback);
- revision rate: turns with a repair or revision call;
- narrator calls per narrated turn (distinct calls, re-asks included);
- cut or fallback turns: a version of kind cut, render or fallback.
"""

from __future__ import annotations

import json
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from engine.audit import text as atx  # noqa: E402

_Q = re.compile(r"[\"“]([^\"”“]*)[\"”]")


def _fiction(text: str) -> str:
    """The delivered fiction without the out-of-fiction blocks and menus."""
    return "\n".join(ln for ln in (text or "").splitlines()
                     if not (ln.lstrip().startswith(("[", ">")) or ln[:1].isspace() or re.match(r"\d+\) ", ln)))


def turn_measures(fiction: str, player: str) -> dict[str, int]:
    spans = list(_Q.finditer(fiction))
    stacked = sum(1 for a, b in zip(spans, spans[1:], strict=False) if not fiction[a.end():b.start()].strip())
    quotes = [m.group(1) for m in spans]
    echoed = sum(1 for q in quotes if len(atx.content(q)) >= 3 and player and atx.covers(q, player, ratio=0.8))
    dup = 0
    for i, a in enumerate(quotes):
        ca = atx.content(a)
        if len(ca) < 3:
            continue
        if any(len(ca & atx.content(b)) >= 0.5 * min(len(ca), len(atx.content(b))) and len(atx.content(b)) >= 3
               for b in quotes[:i]):
            dup += 1
    return {"stacked": stacked, "echoed": echoed, "duplicated": dup}


def save_measures(path: Path) -> dict[str, float]:
    con = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
    calls: dict[str, int] = {}
    for tid, n in con.execute("select turn_id, count(distinct call_id) from model_calls where role='narrator' "
                              "group by turn_id"):
        calls[tid] = n
    out = {k: 0.0 for k in ("turns", "stacked", "stacked_turns", "echoed", "duplicated", "dup_turns", "first_draft",
                            "revised", "cut_or_fallback", "narrator_calls")}
    for tid, rec_json in con.execute("select turn_id, record from turns"):
        rec = json.loads(rec_json or "{}")
        versions = rec.get("draft_versions") or []
        if not versions or versions[0].get("kind") != "draft":
            continue
        kinds = [v.get("kind") for v in versions]
        m = turn_measures(_fiction(rec.get("delivered_verbatim") or ""), rec.get("input_verbatim") or "")
        out["turns"] += 1
        out["stacked"] += m["stacked"]
        out["stacked_turns"] += bool(m["stacked"])
        out["echoed"] += m["echoed"]
        out["duplicated"] += m["duplicated"]
        out["dup_turns"] += bool(m["duplicated"])
        out["first_draft"] += kinds == ["draft"]
        out["revised"] += any(k in ("repair", "revision") for k in kinds)
        out["cut_or_fallback"] += any(k in ("cut", "render", "fallback") for k in kinds)
        out["narrator_calls"] += calls.get(tid, 0)
    con.close()
    return out


def line(name: str, m: dict[str, float]) -> str:
    t = m["turns"] or 1
    return (f"{name}: {int(m['turns'])} narrated turns; stacked quotes {int(m['stacked'])} in {int(m['stacked_turns'])} "
            f"turns; echoed player lines {int(m['echoed'])}; duplicated answers {int(m['duplicated'])} in "
            f"{int(m['dup_turns'])} turns; first draft delivered {m['first_draft'] / t:.0%}; revised "
            f"{m['revised'] / t:.0%}; narrator calls/turn {m['narrator_calls'] / t:.2f}; cut or fallback "
            f"{m['cut_or_fallback'] / t:.0%}")


def main(argv: list[str]) -> int:
    total: dict[str, float] = {}
    for a in argv:
        m = save_measures(Path(a))
        print(line(Path(a).stem, m))
        for k, v in m.items():
            total[k] = total.get(k, 0) + v
    if len(argv) > 1:
        print(line("TOTAL", total))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
