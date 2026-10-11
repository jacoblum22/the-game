"""Head-to-head scoring (spec 032 FR-15): the headline numbers of the success gates from persona-run saves.

    py -3.12 evals/h2h_score.py <save.db> [...] [--findings evals/playtests]

Reads each save's `model_calls`, `turns.record.screen.dm_tools`, `events`, and (when found) the run's
`findings.jsonl` (`<stamp>-claude-<persona>[-tag].findings.jsonl`, for the /fix count). Prints one table, one column
per arm (pipeline / dm-tools, summed over the saves given), under 40 lines, then one line per save. The gates it
feeds: C1 tokens in, C2 latency, C4 /fix count, C7 leaks, C8 fights, C9 world, C10 refusals.
Contradictions (C3) are hand-counted and not computed here. C7 and the observed counts read the turn judge's cached
verdicts (`evals/turn_judge.py run <save>`), with their measured precision. Read-only; no model calls."""

from __future__ import annotations

import json
import re
import sqlite3
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from evals import turn_judge  # noqa: E402

PROSE_ONLY = "no one or nothing on record"  # dm_tools._id's refusal for a target that is only prose (G4)
FOE_LINE = re.compile(r"strikes (you|at you)|closes in|moves toward you|gets back to its feet|breaks free", re.I)


def _ro(path: Path) -> sqlite3.Connection:
    return sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)


def score_save(path: Path, findings_dir: Path | None = None) -> dict[str, Any]:
    """One save's raw counts. Engine turns are the player's inputs (not the opening or the session close)."""
    db = _ro(path)
    cfg = json.loads(db.execute("select payload from events where type='game_created'").fetchone()[0]).get("config", {})
    arm = str(cfg.get("engine") or "pipeline")  # a save with no `engine` key is a pipeline save (G10)
    turns = {t: (inp, rec, out) for t, inp, rec, out in db.execute(
        "select turn_id, input_verbatim, record, delivered_verbatim from turns "
        "where turn_id like 'turn.%' and input_verbatim not like '(%'")}
    calls = db.execute("select turn_id, count(*), sum(coalesce(tokens_in,0) + coalesce(tokens_in_cached,0)), "
                       "sum(coalesce(latency_ms,0)) from model_calls group by turn_id").fetchall()
    c = {t: (n, tin or 0, ms or 0) for t, n, tin, ms in calls if t in turns}
    dm = [((json.loads(rec or "{}").get("screen") or {}).get("dm_tools") or {}) for _, rec, _ in turns.values()]
    # [spec 033 R11] leaks, costly asks and mood changes come from the turn judge's cached verdicts (no keyword check)
    judged = turn_judge.cached(path)
    refusals = [r for d in dm for r in d.get("refusals") or []]
    # [spec 033 P9] fights: conflict_start .. conflict_end by turn, a start a take-back reverted left out (its writes_reverted
    # covers the same turn's `conflict` meta_set or the mark itself). An exchange is a turn inside a live fight with a
    # `round` mark when the save has any, else one where a roll RESOLVED (a `frame_resolved` whose frame was not voided):
    # a pause, a menu answer or a /fix note is not one. A fight that ended with no foe call or foe line was ended by the
    # PC's blow.
    rows = db.execute("select seq, turn_id, type, payload from events where type in ('boundary_marked', 'writes_reverted', "
                      "'frame_resolved') or (type='meta_set' and json_extract(payload,'$.key') in ('conflict','rolls_voided')) "
                      "order by seq").fetchall()
    reverted: set[int] = set()
    voided: set[str] = set()
    for _, _, typ, raw in rows:
        p = json.loads(raw)
        if typ == "writes_reverted":
            reverted |= set(p.get("reverted") or [])
        elif typ == "meta_set" and p.get("key") == "rolls_voided":
            voided = set(p.get("value") or [])
    resolved = {t for _, t, typ, raw in rows if typ == "frame_resolved" and json.loads(raw).get("frame_id") not in voided}
    rounds = {t for _, t, typ, raw in rows if typ == "boundary_marked" and json.loads(raw).get("boundary") == "round"}
    meta_at: dict[str, int] = {}  # the last `conflict` meta_set seen, by turn
    starts_by_turn: dict[str, int] = {}
    ends_by_turn: dict[str, int] = {}
    starts_n = 0
    for seq, t, typ, raw in rows:
        p = json.loads(raw)
        if typ == "meta_set" and p.get("key") == "conflict":
            meta_at[t] = seq
        elif typ == "boundary_marked" and p.get("boundary") == "conflict_start":
            if seq not in reverted and meta_at.get(t) not in reverted:
                starts_by_turn[t] = starts_by_turn.get(t, 0) + 1
                starts_n += 1
        elif typ == "boundary_marked" and p.get("boundary") == "conflict_end":
            ends_by_turn[t] = ends_by_turn.get(t, 0) + 1

    def foe_acted(t: str) -> bool:
        w = ((json.loads(turns[t][1] or "{}").get("screen") or {}).get("dm_tools") or {}).get("world", {})
        return bool(w.get("foe_turns") or w.get("foe_calls") or FOE_LINE.search(turns[t][2] or ""))

    fight: set[str] = set()
    ended_by_pc = 0
    cur: list[str] | None = None
    for t in turns:  # insertion order is turn order
        if starts_by_turn.get(t):
            cur = cur if cur is not None else []
        if cur is not None:
            cur.append(t)
            fight.add(t)
        if ends_by_turn.get(t) and cur is not None:
            ended_by_pc += not any(foe_acted(x) for x in cur)
            cur = None
    exchanges = fight & (rounds or resolved)
    foe_turns = sum(foe_acted(t) for t in fight)
    adv = [json.loads(p) for (p,) in db.execute("select payload from events where type='time_advanced'")]
    last = adv[-1]["to"] if adv else {}
    # [spec 032 trap 1] "told" = the said lines the DM listed (`screen.dm_tools.said`, else the record's `said`), not events
    told = sum(len(d.get("said") or json.loads(turns[t][1] or "{}").get("said") or []) for t, d in zip(turns, dm, strict=True))
    db.close()
    fix = None
    if findings_dir is not None:
        m = re.fullmatch(r"playtest-(\d{8}-\d{6})-(.+)", path.stem)
        f = findings_dir / f"{m.group(1)}-claude-{m.group(2)}.findings.jsonl" if m else None
        if f is not None and f.exists():
            rows = [json.loads(x) for x in f.read_text(encoding="utf-8").splitlines() if x.strip()]
            fix = sum(1 for r in rows if r.get("kind") == "player_note" and str(r.get("typed", "")).startswith("/fix"))
    return {"save": path.stem, "arm": arm, "turns": len(turns), "calls": sum(v[0] for v in c.values()),
            "tokens_in": sum(v[1] for v in c.values()), "latency_ms": sum(v[2] for v in c.values()),
            "timed_turns": len(c), "fix": fix, "refusals": len(refusals),
            "prose_refusals": sum(PROSE_ONLY in str(r.get("why", "")) for r in refusals),
            "judged": judged, "judged_turns": len({k.split("|")[0] for k in judged}),
            "fights": starts_n,
            "fight_exchanges": len(exchanges), "foe_turns": foe_turns, "pc_blow_fights": ended_by_pc,
            "time_moved": any(a["from"].get("hour") != a["to"].get("hour") or a["from"].get("day") != a["to"].get("day")
                              for a in adv),
            "interval_moved": any(a["from"].get("interval") != a["to"].get("interval") for a in adv), "last_time": f"d{last.get('day')} h{last.get('hour')} i{last.get('interval')}",
            "told": told}


def _sum(rows: list[dict[str, Any]], key: str) -> int:
    return sum(int(r[key] or 0) for r in rows)


def _judged(rows: list[dict[str, Any]], measure: str, label: str) -> int:
    return sum(v["label"] == label for r in rows for k, v in r["judged"].items() if k.endswith(f"|{measure}"))


def table(rows: list[dict[str, Any]]) -> str:
    hand = turn_judge.load_hand()
    arms = {a: [r for r in rows if r["arm"] == a] for a in ("pipeline", "dm-tools")}

    def per(a: list[dict[str, Any]], key: str, div: str = "timed_turns") -> str:
        d = _sum(a, div)
        return f"{_sum(a, key) / d:,.0f}" if d else "-"

    def col(label: str, f: Any) -> str:
        return f"| {label} | " + " | ".join(f(a) if a else "-" for a in arms.values()) + " |"

    ratio = ""
    if all(arms.values()):
        p, d = arms["pipeline"], arms["dm-tools"]
        tin = (_sum(d, "tokens_in") / max(1, _sum(d, "timed_turns"))) / max(1e-9, _sum(p, "tokens_in") / max(1, _sum(p, "timed_turns")))
        lat = (_sum(d, "latency_ms") / max(1, _sum(d, "timed_turns"))) / max(1e-9, _sum(p, "latency_ms") / max(1, _sum(p, "timed_turns")))
        ratio = f"C1 tokens-in ratio dm-tools/pipeline {tin:.2f} (gate <= 0.6); C2 latency ratio {lat:.2f} (gate <= 0.7)"
    out = ["| measure | pipeline | dm-tools |", "|---|---|---|",
           col("saves / engine turns", lambda a: f"{len(a)} / {_sum(a, 'turns')}"),
           col("C1 tokens in per turn", lambda a: per(a, "tokens_in")),
           col("C2 model latency (s) per turn", lambda a: f"{_sum(a, 'latency_ms') / 1000 / max(1, _sum(a, 'timed_turns')):.1f}"),
           col("model calls per turn", lambda a: f"{_sum(a, 'calls') / max(1, _sum(a, 'timed_turns')):.1f}"),
           col("C4 /fix reports (findings)", lambda a: "n/a" if any(r["fix"] is None for r in a) else str(_sum(a, "fix"))),
           col("turn judge: turns judged", lambda a: str(_sum(a, "judged_turns"))),
           col("observed (no gate): costly asks caved / priced / mood changes with no cause",
               lambda a: f"{_judged(a, 'ask', 'caved')} / {_judged(a, 'ask', 'priced')} / {_judged(a, 'mood', 'uncaused')}"),
           col("C7 leaks (judge, flagged turns)", lambda a: str(_judged(a, "leak", "leaked"))),
           col("pronoun slips / absent person speaks (judge)",
               lambda a: f"{_judged(a, 'pronoun', 'slip')} / {_judged(a, 'absent', 'absent_speaks')}"),
           col("C8 fights / exchanges / foe turns (fights ended by the PC's blow)",
               lambda a: f"{_sum(a, 'fights')} / {_sum(a, 'fight_exchanges')} / {_sum(a, 'foe_turns')} ({_sum(a, 'pc_blow_fights')})"),
           col("C8/C10 refused tool calls (aimed at prose-only)", lambda a: f"{_sum(a, 'refusals')} ({_sum(a, 'prose_refusals')})"),
           col("C9 saves where hour/day moved, interval moved / 'told' rows",
               lambda a: f"{sum(r['time_moved'] for r in a)}, {sum(r['interval_moved'] for r in a)} of {len(a)} / {_sum(a, 'told')}")]
    return "\n".join(out + ([ratio] if ratio else []) +
                     ["C3 contradictions: hand-counted, not computed",
                      "foe turns: dm_tools.world.foe_turns when logged, else a foe line in the delivered text (approx)",
                      "judge counts are over sampled turns, read from the cache (evals/turn_judge.py run <save>); "
                      "0 judged means not judged"] +
                     [f"turn judge {m}: {turn_judge.precision(m, hand)}" for m in turn_judge.MEASURES] +
                     [f"- {r['save']} [{r['arm']}]: {r['turns']} turns, end {r['last_time']}" for r in rows])


def main(argv: list[str]) -> int:
    fdir = Path(argv[argv.index("--findings") + 1]) if "--findings" in argv else None
    saves = [Path(a) for i, a in enumerate(argv) if not a.startswith("--") and (i == 0 or argv[i - 1] != "--findings")]
    if not saves:
        print(__doc__)
        return 2
    print(table([score_save(p, fdir) for p in saves]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
