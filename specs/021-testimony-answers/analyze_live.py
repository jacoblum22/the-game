"""Spec 021: read a playtest save (read-only) for the live gate: wall/dodge answers, refusals stored as facts,
pronoun flips on checkable lines, found-clue repeats, settlements.

    py -3.12 specs/021-testimony-answers/analyze_live.py <save.db> [<save.db> ...]

Checkable line (I2 §4): a `said` line that names exactly one other stored person with recorded pronouns and uses
pronouns of one set only (he or she) and no other person; flipped when that set contradicts the record.
"""

from __future__ import annotations

import json
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).parent))

from measure import before_turn, events  # noqa: E402

from engine.dm import testimony as tm  # noqa: E402
from engine.retrieve.scene import resolve_names  # noqa: E402

DODGE = re.compile(r"\b(no business|not mine to|won'?t (?:say|tell|name)|I'?ll not (?:say|name|tell)|can'?t say|"
                   r"couldn'?t say|I don'?t know|not one I'?d|no one I know|keep (?:it|that) to myself|"
                   r"not (?:in|across) this square)\b", re.I)
HE, SHE = re.compile(r"\b(he|him|his|himself)\b", re.I), re.compile(r"\b(she|her|hers|herself)\b", re.I)


def analyze(path: Path) -> None:
    c = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
    c.row_factory = sqlite3.Row
    evs = events(c)
    last = max((int(t[0].split(".")[1]) for t in c.execute("SELECT turn_id FROM turns") if t[0].startswith("turn.")), default=0)
    st = before_turn(evs, c, "turn.99999")
    recs = tm.records(st)
    print(f"# {path.name}: turns {c.execute('SELECT COUNT(*) FROM turns').fetchone()[0]} (last {last}), "
          f"said lines {len(recs)}")
    settled = [r for r in recs if r.get("settled") is not None]
    print(f"- settlements: {len(settled)}: " + "; ".join(f"{r['id']} {r.get('route')} -> {r.get('fact')}"
                                                          for r in settled))
    facts = [f for f in st.facts.values() if f.source == "testimony"]
    own = [f for f in facts if re.match(r"^(?:said.)?(will|won|would|refuse)", f.predicate)]
    print(f"- testimony facts {len(facts)}; refusals or intentions stored as facts: {len(own)} "
          + "; ".join(f"{f.predicate}={f.value}" for f in facts))
    noone = [f.id for f in st.facts.values() if str(f.value) == "no one you know"]
    print(f"- 'no one you know' facts: {len(noone)}")
    dodges = [(r["turn"], r["words"]) for r in recs if DODGE.search(r["words"])]
    print(f"- dodge-pattern lines: {len(dodges)} of {len(recs)}")
    for t, w in dodges:
        print(f"    {t}: {w[:140]}")
    checkable = flipped = 0
    for r in recs:
        named = [i for i in resolve_names(st, r["words"]) if i != r["speaker"] and i in st.entities
                 and st.entities[i].kind in ("npc", "companion") and st.entities[i].data.get("pronouns")]
        he, she = bool(HE.search(r["words"])), bool(SHE.search(r["words"]))
        if len(named) != 1 or he == she:
            continue
        p = str(st.entities[named[0]].data["pronouns"])
        if not p.startswith(("he", "she")):
            continue
        checkable += 1
        bad = (p.startswith("she") and he) or (p.startswith("he/") and she)
        flipped += bad
        if bad:
            print(f"    flip {r['turn']}: {st.entities[named[0]].name} ({p}): {r['words'][:120]}")
    print(f"- pronoun flips on checkable lines: {flipped} of {checkable}")
    seen: dict[str, int] = {}
    for row in c.execute("SELECT turn_id, request FROM model_calls WHERE role = 'narrator' AND attempt = 0"):
        req = json.loads(row["request"] or "{}")
        for ln in str(req.get("packet") or "").splitlines():
            m = re.match(r"- R\d+ MUST: (.*)", ln.strip())
            for case in (st.meta.get("world.cases") or {}).values():
                for n in case["nodes"]:
                    if m and n["fact"] in m.group(1):
                        seen[n["fact"]] = seen.get(n["fact"], 0) + 1
    print(f"- case facts on MUST lines: {seen}; repeats {sum(v - 1 for v in seen.values())}")


if __name__ == "__main__":
    for a in sys.argv[1:]:
        analyze(Path(a))
