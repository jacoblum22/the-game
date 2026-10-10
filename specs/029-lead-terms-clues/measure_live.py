"""Spec 029's live measures over recorded games (read-only).

    py -3.12 specs/029-lead-terms-clues/measure_live.py <save.db> [<save.db> ...]

Per save: the clue judgment's calls (one per message with questions), how many judged a clue; case nodes found
(clues delivered) and the learned lines the narrator was given ("the PC learns: ..."); the hook terms written at the
seed (kinds, people and documents made); stalls in the delivered fiction (a lead with nothing behind it: "waiting on
your reading", "nothing behind", "cannot say"); and the journal's answers to "what do I know".
"""

from __future__ import annotations

import json
import re
import sqlite3
import sys
from pathlib import Path

STALL = re.compile(r"waiting on your reading|nothing behind|nothing more to|has nothing|no (?:one|man|woman) can say|"
                   r"cannot say|can't say|couldn't say|could not say|do(?:es)? not know|don't know|doesn't know|"
                   r"nothing on record", re.I)
LEARNS = re.compile(r"the PC learns: (.+)")


def measure(path: Path) -> list[str]:
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    out = [f"== {path.name}"]
    cols = [r[1] for r in con.execute("pragma table_info(turns)")]
    turns = [dict(zip(cols, r, strict=True)) for r in con.execute("select * from turns where turn_id like 'turn.%'")]
    calls = list(con.execute("select turn_id, response from model_calls where role='clue' and attempt=0"))
    per_turn: dict[str, int] = {}
    for t, _ in calls:
        per_turn[t] = per_turn.get(t, 0) + 1
    yes = sum(1 for _, r in calls if str(json.loads(r or "{}").get("data", {}).get("about")) not in ("none", "None"))
    out.append(f"clue judgment: {len(calls)} calls over {len(per_turn)} messages (max {max(per_turn.values(), default=0)} "
               f"per message); {yes} judged about a clue")
    cases: dict = {}
    terms: dict = {}
    for k, pl in con.execute("select json_extract(payload,'$.key'), payload from events where type='meta_set' and "
                             "json_extract(payload,'$.key') in ('world.cases','world.hook_terms') order by seq"):
        v = json.loads(pl)["value"]
        if k == "world.cases":
            cases = v
        else:
            terms = v
    found = [(c, n["id"], n.get("fact")) for c, rec in cases.items() for n in rec["nodes"] if n.get("found")]
    out.append(f"clues delivered (case nodes found): {len(found)}: {[f[2] for f in found]}")
    fam: dict[str, int] = {}
    for t in terms.values():
        fam[t.get("family", "?")] = fam.get(t.get("family", "?"), 0) + 1
    out.append(f"hook terms at the seed and in play: {sum(fam.values())} {fam}")
    learned: list[tuple[str, str]] = []
    for t in turns:
        row = con.execute("select request from model_calls where role='narrator' and turn_id=? order by row_id limit 1",
                          (t["turn_id"],)).fetchone()
        if row is None:
            continue
        pk = json.loads(row[0]).get("packet", "")
        learned += [(t["turn_id"], x) for x in LEARNS.findall(pk[pk.rfind("ADJUDICATION RECORD"):])]
    out.append(f"learned lines given to the narrator: {len(learned)}")
    out += [f"  {t}: {x[:130]}" for t, x in learned]
    stalls = [(t["turn_id"], m.group(0)) for t in turns for m in STALL.finditer(str(t["delivered_verbatim"] or ""))]
    out.append(f"possible stalls in the delivered fiction (read by hand): {len(stalls)}")
    out += [f"  {t}: ...{m}..." for t, m in stalls[:14]]
    jr = [t for t in turns if re.search(r"what do i know|my journal|what have i learned", str(t["input_verbatim"]), re.I)]
    out.append(f"journal questions: {len(jr)}")
    for t in jr:
        out.append(f"  {t['turn_id']} {str(t['input_verbatim'])[:100]!r} -> {str(t['delivered_verbatim'])[:900]}")
    con.close()
    return out


if __name__ == "__main__":
    for p in sys.argv[1:]:
        print("\n".join(measure(Path(p))))
