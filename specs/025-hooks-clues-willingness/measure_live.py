"""Spec 025's live measures over recorded games (read-only).

    py -3.12 specs/025-hooks-clues-willingness/measure_live.py <save.db> [<save.db> ...]

Per save: the clue judgment's calls and yes answers; case nodes found (clues delivered); the NPC answer lines the
narrator was given (willing / guarded / unwilling = a wall; code pointers); refusal loops (a pointer to someone who
had already refused the PC); accepted offers against typed deal prices (unpriced deals); and every topic two or more
speakers improvised on, with their words, to read for contradictions by hand.
"""

from __future__ import annotations

import json
import re
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

_LINE = re.compile(r"^- R\d+ MUST: (.+?) acts: (.*)$", re.M)
_PTR = re.compile(r"(?:names one person who would know: |, but )(.+?)(?: would\b|$)")


def measure(path: Path) -> list[str]:
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    out = [f"== {path.name}"]
    turns = [t for (t,) in con.execute("select turn_id from turns where turn_id like 'turn.%'")]
    clue = [json.loads(r or "{}").get("data", {}).get("about") for (r,) in
            con.execute("select response from model_calls where role='clue' and attempt=0")]
    cases = {}
    said: dict = {}
    for k, pl in con.execute("select json_extract(payload,'$.key'), payload from events where type='meta_set' "
                             "and json_extract(payload,'$.key') in ('world.cases','npc.said') order by seq"):
        v = json.loads(pl)["value"]
        if k == "world.cases":
            cases = v
        else:
            said = v
    found = [(c, n["id"]) for c, rec in cases.items() for n in rec["nodes"] if n.get("found")]
    lines: list[tuple[str, str, str]] = []
    for t in turns:
        row = con.execute("select request from model_calls where role='narrator' and turn_id=? order by row_id limit 1",
                          (t,)).fetchone()
        if row is None:
            continue
        msg = json.loads(row[0]).get("packet", "")
        msg = msg[msg.rfind("ADJUDICATION RECORD"):]
        lines += [(t, who, act) for who, act in _LINE.findall(msg)]
    ans = [x for x in lines if re.search(r"answers what you asked|refuses to answer|tells you|does not know|replies|"
                                         r"turns you away|remember", x[2])]
    walls = [x for x in ans if "refuses to answer" in x[2] or "turns you away" in x[2]]
    refused: dict[str, str] = {}
    loops = []
    for t, who, act in ans:
        m = _PTR.search(act)
        if m and m.group(1).strip() in refused:
            loops.append((t, who, m.group(1).strip()))
        if "refuses to answer" in act:
            refused.setdefault(who, t)
    offers = [x for x in lines if "takes what you offer" in x[2]]
    priced = [pl for (pl,) in con.execute("select payload from events where type='fact_set' and "
                                          "json_extract(payload,'$.predicate')='deal.price'")]
    out += [f"turns {len(turns)}; clue calls {len(clue)} (judged about a clue: {sum(a not in (None, 'none') for a in clue)})",
            f"clues delivered (case nodes found): {len(found)} {found}",
            f"NPC answer lines: {len(ans)}; willing {sum('willingly' in x[2] for x in ans)}, guarded "
            f"{sum('guardedly' in x[2] for x in ans)}, walls (refusals) {len(walls)}; code pointers "
            f"{sum(bool(_PTR.search(x[2])) for x in ans)}",
            f"refusal loops: {len(loops)} {loops}",
            f"accepted offers {len(offers)}; typed deal prices {len(priced)}; unpriced {max(0, len(offers) - len(priced))}"]
    for t, who, act in walls:
        out.append(f"  wall {t}: {who}: {act[:160]}")
    by_topic: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for r in (said or {}).get("records") or []:
        q = str(r.get("question") or "")
        if q:
            by_topic[q.rsplit("|", 1)[-1]].append((str(r.get("speaker")), str(r.get("words"))))
    shared = {k: v for k, v in by_topic.items() if len({s for s, _ in v}) >= 2}
    out.append(f"topics improvised on by 2+ speakers: {len(shared)} (read for contradictions)")
    for k, v in shared.items():
        out.append(f"  [{k}]")
        out += [f"    {s}: {w[:200]}" for s, w in v]
    return out


if __name__ == "__main__":
    for p in sys.argv[1:]:
        print("\n".join(measure(Path(p))))
