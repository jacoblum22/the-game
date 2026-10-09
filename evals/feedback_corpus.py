"""Spec 014: the feedback loop scored on the real complaint corpus (PR-12-11; OEQ-12-26).

    py -3.12 evals/feedback_corpus.py --model haiku --out evals/baselines/feedback_corpus_after.json
    py -3.12 evals/feedback_corpus.py --model offline           # the offline stand-in, no call
    py -3.12 evals/feedback_corpus.py --cached X.json --out X.json   # re-score a run's understanding, no call

The corpus (`tests/fixtures/feedback_corpus/corpus.json`) is every `/fix` line of the two 20261008 persona re-runs
(talker 145410, fighter 145430), what the player's note says each was about, plus three short forms of the round-3
complaints. Each item runs on its save cut back to just before the report (`open_at`), through `settle_dispute`
with the given model, on a throwaway copy. Scored per item: the understanding (category and turn as expected) and
the outcome (the dispute record's outcome among the expected ones, and a plain answer: never "Say which fact" or
a bare "Logged."). Haiku runs through the Claude CLI (the owner's subscription; no API spend).
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
BARE = ("Say which fact or roll is wrong", "Which statement, and when?")


def load_corpus() -> list[dict[str, Any]]:
    return json.loads((CORPUS / "corpus.json").read_text(encoding="utf-8"))["items"]


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


def run_item(item: dict[str, Any], model: Any, rules: Any, tmp: Path) -> dict[str, Any]:
    from engine.dm.dispute import settle_dispute

    store = open_at(CORPUS / item["save"], item["turn"], tmp)
    try:
        ctx = Ctx(store, rules, model, item["turn"])
        res = settle_dispute(ctx, item["report"])
        claim = res.claim
        rec = res.record or {}
        return {"id": item["id"], "category": getattr(claim, "category", None),
                "turn": getattr(claim, "turn_id", None), "believes": getattr(claim, "believes", ""),
                "outcome": rec.get("outcome"), "kind": res.kind, "answer": res.text,
                "understood": [c.get("response") for c in (r.model_dump() for r in ctx.calls)]}
    finally:
        store.close()


def score(item: dict[str, Any], got: dict[str, Any]) -> dict[str, bool]:
    exp = item["expected"]
    turns = exp["turn"] if isinstance(exp["turn"], list) else [exp["turn"]]
    understood = got["category"] in exp["category"] and got["turn"] in turns
    plain = not any(b in got["answer"] for b in BARE) and got["answer"].strip() not in ("", "Logged.")
    outcome = got["outcome"] in exp["outcome"] and plain
    return {"understood": understood, "outcome": outcome}


def model_for(name: str) -> Any:
    if name == "offline":
        from engine.llm.offline import OfflineModel

        return OfflineModel()
    from evals.playtest import ClaudeModel

    return ClaudeModel(name)


def main() -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("--model", default="offline", help="offline, or a Claude CLI model (haiku)")
    ap.add_argument("--only", default="", help="comma-separated item ids")
    ap.add_argument("--out", default="", help="write the results as JSON here")
    ap.add_argument("--cached", default="", help="re-score with the understanding recorded in this results file")
    args = ap.parse_args()
    from engine.data.loader import load_rules
    from engine.llm.base import Role
    from engine.llm.offline import ScriptedModel

    rules = load_rules()
    items = [i for i in load_corpus() if not args.only or i["id"] in args.only.split(",")]
    cached = {r["id"]: r for r in json.loads(Path(args.cached).read_text(encoding="utf-8"))["results"]} \
        if args.cached else {}
    model = model_for(args.model)
    results = []
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        for item in items:
            if cached:
                data = next(u["data"] for u in cached[item["id"]]["understood"] if u and u.get("data"))
                model = ScriptedModel({Role.UNDERSTAND: [data]}, fallback=False)
            got = run_item(item, model, rules, Path(tmp))
            got["score"] = score(item, got)
            results.append(got)
            s = got["score"]
            print(f"{item['id']:<12} understood={'Y' if s['understood'] else 'n'} outcome={'Y' if s['outcome'] else 'n'}"
                  f"  ({got['category']}, {got['turn']}, {got['outcome']})")
    n = len(results)
    u = sum(r["score"]["understood"] for r in results)
    o = sum(r["score"]["outcome"] for r in results)
    print(f"understanding (category and turn): {u}/{n}; outcome: {o}/{n}")
    if args.out:
        label = f"{json.loads(Path(args.cached).read_text(encoding='utf-8'))['model']} (cached)" if cached else args.model
        Path(args.out).write_text(json.dumps({"model": label, "understood": u, "outcome": o, "n": n,
                                              "results": results}, indent=1, ensure_ascii=False) + "\n",
                                  encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
