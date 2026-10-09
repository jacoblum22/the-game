"""Specs 014 and 022: the feedback loop (the Fixer, PR-12-11) scored on real complaints (OEQ-12-26).

    py -3.12 evals/feedback_corpus.py --model sonnet --out evals/baselines/fixer_corpus_sonnet.json
    py -3.12 evals/feedback_corpus.py --set round6 --model sonnet     # the 15 round-6 live disputes (I3 §5)
    py -3.12 evals/feedback_corpus.py --set heldout --model sonnet    # held-out complaints, labelled before the run
    py -3.12 evals/feedback_corpus.py --model offline                 # the offline stand-in, no call
    py -3.12 evals/feedback_corpus.py --cached X.json --out X.json    # re-score a run's Fixer answers, no call

Sets (`tests/fixtures/feedback_corpus/`): `corpus` (spec 014: every `/fix` line of the two 20261008 persona re-runs
plus three short forms of round-3 complaints, one expected complaint each), `round6` (the seven round-6 reports
holding I3 §5's 15 disputes) and `heldout` (new complaints from other turns of the saves). Each report runs on its save
cut back to just before it (`open_at`), through `settle_dispute` with the given model as the Fixer, on a throwaway
copy. Scored per complaint: understood (category and turn as expected; the `corpus` set) and the outcome class:
`upheld` (the player is right: a correction, a take-back, or the record agrees and the narration slipped),
`stands` (the record stands, explained) or `not_found`; plus the corrections expected applied (`done` kinds), and
a plain answer ending in `Now:`. Claude models run through the Claude CLI (the owner's subscription; no API spend).
"""

from __future__ import annotations

import argparse
import gzip
import json
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

CORPUS = ROOT / "tests" / "fixtures" / "feedback_corpus"
SETS = {"corpus": "corpus.json", "round6": "round6.json", "heldout": "heldout.json"}
BARE = ("Say which fact or roll is wrong", "Which statement, and when?")


def load_corpus(which: str = "corpus") -> list[dict[str, Any]]:
    return json.loads((CORPUS / SETS[which]).read_text(encoding="utf-8"))["items"]


def _turn_n(turn_id: str | None) -> int:
    return int(str(turn_id).rsplit(".", 1)[1]) if turn_id and str(turn_id).startswith("turn.") else 0


def open_at(save: Path, turn: str, into: Path) -> Any:
    """A copy of `save` cut back to just before `turn` (events, turns, snapshots and indexes after it dropped)."""
    from engine.store.db import Store

    path = into / f"{save.name.split('.')[0]}-{turn}.db"
    with gzip.open(save, "rb") if save.suffix == ".gz" else save.open("rb") as src, path.open("wb") as dst:
        shutil.copyfileobj(src, dst)
    con = sqlite3.connect(path)
    n = _turn_n(turn)
    rows = con.execute("SELECT seq, turn_id FROM events ORDER BY seq").fetchall()
    first = next((s for s, t in rows if _turn_n(t) >= n), None)
    cut = (first - 1) if first is not None else rows[-1][0]
    con.executescript("DROP TRIGGER IF EXISTS events_no_delete; DROP TRIGGER IF EXISTS rng_no_delete;")
    con.execute("DELETE FROM events WHERE seq > ?", (cut,))
    con.execute("DELETE FROM snapshots WHERE seq > ?", (cut,))
    con.execute("DELETE FROM rng_draws WHERE event_seq > ?", (cut,))
    gone = [t for (t,) in con.execute("SELECT turn_id FROM turns") if _turn_n(t) >= n]
    con.executemany("DELETE FROM turns WHERE turn_id = ?", [(t,) for t in gone])
    con.commit()
    con.close()
    store = Store.open(path)  # recreates the triggers
    store.rebuild_indexes()
    return store


class Ctx:
    """What `settle_dispute` reads: the store, its state, the rules, the model, the report's own turn id."""

    def __init__(self, store: Any, rules: Any, model: Any, turn_id: str) -> None:
        self.store, self.rules, self.model, self.turn_id = store, rules, model, turn_id
        self.tx = None
        self.calls: list[Any] = []

    @property
    def state(self) -> Any:
        return self.store.state

    def record_call(self, rec: Any) -> None:
        self.calls.append(rec)


UPHELD = {"correct", "take_back", "player_reading_wins", "upheld"}  # spec 014's outcome names, by class
STANDS = {"explain_with_quote", "explain_and_log", "stands"}


def _class(rec: dict[str, Any]) -> str:
    return "upheld" if rec.get("upheld") else "not_found" if rec.get("outcome") == "not_found" else "stands"


def run_item(item: dict[str, Any], model: Any, rules: Any, tmp: Path) -> dict[str, Any]:
    from engine.dm.dispute import settle_dispute

    store = open_at(CORPUS / item["save"], item["turn"], tmp)
    try:
        ctx = Ctx(store, rules, model, item["turn"])
        res = settle_dispute(ctx, item["report"])
        complaints = [{"believes": r["believes"], "category": r["category"], "turn": r["passage"]["turn"],
                       "verdict": r["verdict"], "class": _class(r), "outcome": r["outcome"], "done": r["done"],
                       "done_kinds": r.get("done_kinds", []),
                       "not_done": r["not_done"]} for r in res.records]
        first = complaints[0] if complaints else {}
        return {"id": item["id"], "category": first.get("category"), "turn": first.get("turn"),
                "outcome": first.get("outcome"), "kind": res.kind, "answer": res.text, "complaints": complaints,
                "tools": (res.record or {}).get("evidence", []),
                "understood": [c.get("response") for c in (r.model_dump() for r in ctx.calls)]}
    finally:
        store.close()


def _match(exp: dict[str, Any], got: list[dict[str, Any]]) -> dict[str, Any] | None:
    """The answered complaint for an expected one: the same turn, else the same class, else none."""
    turns = exp["turn"] if isinstance(exp["turn"], list) else [exp["turn"]]
    return next((c for c in got if c["turn"] in turns), None) or next(
        (c for c in got if c["class"] == exp.get("class")), None)


def score(item: dict[str, Any], got: dict[str, Any]) -> dict[str, Any]:
    """Per expected complaint: understood (category and turn), class (upheld / stands / not_found as expected), and
    `auto`: right (class and every expected correction applied), unclear (class right, a correction missing), wrong."""
    plain = not any(b in got["answer"] for b in BARE) and "Now:" in got["answer"]
    exps = item["expected"]["complaints"] if "complaints" in item["expected"] else [item["expected"]]
    rows = []
    for exp in exps:
        cls = exp.get("class") or ("upheld" if set(exp["outcome"]) & UPHELD else
                                   "not_found" if "not_found" in exp["outcome"] else "stands")
        classes = cls if isinstance(cls, list) else [cls]
        c = _match({**exp, "class": classes[0]}, got["complaints"])
        turns = exp["turn"] if isinstance(exp["turn"], list) else [exp["turn"]]
        understood = c is not None and c["turn"] in turns and (not exp.get("category") or c["category"] in exp["category"])
        ok = c is not None and c["class"] in classes and plain
        need = set(exp.get("done") or [])
        kinds_ok = not need or bool(need & set((c or {}).get("done_kinds", [])))  # any one of the expected kinds
        rows.append({"id": exp.get("id", item["id"]), "understood": understood, "outcome": ok,
                     "auto": "right" if ok and kinds_ok else "unclear" if ok else "wrong"})
    return {"understood": all(r["understood"] for r in rows), "outcome": all(r["outcome"] for r in rows),
            "complaints": rows}


def model_for(name: str) -> Any:
    if name == "offline":
        from engine.llm.offline import OfflineModel

        return OfflineModel()
    from evals.playtest import ClaudeModel

    return ClaudeModel(name)


def main() -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("--model", default="offline", help="offline, or a Claude CLI model (sonnet)")
    ap.add_argument("--set", default="corpus", choices=sorted(SETS))
    ap.add_argument("--only", default="", help="comma-separated item ids")
    ap.add_argument("--out", default="", help="write the results as JSON here")
    ap.add_argument("--cached", default="", help="re-score with the Fixer answers recorded in this results file")
    args = ap.parse_args()
    from engine.data.loader import load_rules
    from engine.llm.base import Role
    from engine.llm.offline import ScriptedModel

    rules = load_rules()
    items = [i for i in load_corpus(args.set) if not args.only or i["id"] in args.only.split(",")]
    cached = {r["id"]: r for r in json.loads(Path(args.cached).read_text(encoding="utf-8"))["results"]} \
        if args.cached else {}
    model = model_for(args.model)
    results = []
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        for item in items:
            if cached:
                data = [u["data"] for u in cached[item["id"]]["understood"] if u and u.get("data") is not None]
                model = ScriptedModel({Role.FIXER: data}, fallback=False)
            got = run_item(item, model, rules, Path(tmp))
            got["score"] = score(item, got)
            results.append(got)
            for r in got["score"]["complaints"]:
                print(f"{r['id']:<14} understood={'Y' if r['understood'] else 'n'} outcome={'Y' if r['outcome'] else 'n'}"
                      f" auto={r['auto']:<7} ({got['kind']}; {len(got['tools'])} tools)")
    rows = [r for g in results for r in g["score"]["complaints"]]
    n = len(rows)
    u = sum(r["understood"] for r in rows)
    o = sum(r["outcome"] for r in rows)
    auto = {k: sum(r["auto"] == k for r in rows) for k in ("right", "unclear", "wrong")}
    print(f"complaints {n}: understood {u}/{n}; outcome class {o}/{n}; auto {auto}")
    if args.out:
        label = f"{json.loads(Path(args.cached).read_text(encoding='utf-8'))['model']} (cached)" if cached else args.model
        Path(args.out).write_text(json.dumps({"model": label, "set": args.set, "understood": u, "outcome": o, "n": n,
                                              "auto": auto, "results": results}, indent=1, ensure_ascii=False) + "\n",
                                  encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
