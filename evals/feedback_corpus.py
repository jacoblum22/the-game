"""Specs 014, 022 and 026: the feedback loop (the Fixer, PR-12-11) scored on the screen the player sees after `/fix`.

    py -3.12 evals/feedback_corpus.py --set fresh --model sonnet --out evals/baselines/fixer_fresh_026.json  # headline
    py -3.12 evals/feedback_corpus.py --set round7 --model sonnet     # the 3 round-7 live disputes
    py -3.12 evals/feedback_corpus.py --set round6 --model sonnet     # the 15 round-6 live disputes (I3 §5)
    py -3.12 evals/feedback_corpus.py --model offline                 # the offline stand-in, no call
    py -3.12 evals/feedback_corpus.py --cached X.json --out X.json    # re-score a run's recorded answers, no call

Sets (`tests/fixtures/feedback_corpus/`): `fresh` (spec 026: 13 made-up and edge complaints, labelled before
implementation; the headline), `round7` (the round-7 live /fix reports), `round6` (the seven round-6 reports holding
I3 §5's 15 disputes), `heldout` (spec 022's 7), `corpus` (spec 014's 11) and `dmtools` (spec 032 P6: the head-to-head
dm-tools saves' complaints and made-up ones; a dm-tools save runs its own /fix turn, `play_dm_dispute`). Each report runs through the whole turn
loop (`play_dispute`, the /fix command) on its save cut back to just before it (`open_at`), with the given model as
the Fixer and `--engine-model` as the play roles (a re-frame calls the Framer), on a throwaway copy. Scored per
complaint: understood (category and turn as expected), the outcome class (`upheld`: the player is right; `stands`:
the record stands, explained; `not_found`), the corrections expected applied (`done`, any one), and the screen after
the /fix: each `screen.must` regex found, no `screen.must_not` regex found (DL-12-117: the scorer checks what the
player sees, not only the outcome class). auto: right (all of it), unclear (class right, a correction or a `must`
missing), wrong (class wrong, or the complaint still on screen). Claude models run through the Claude CLI (the owner's
subscription; no API spend). Every model answer is taped, so `--cached` replays a run exactly.
"""

from __future__ import annotations

import argparse
import gzip
import json
import re
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

CORPUS = ROOT / "tests" / "fixtures" / "feedback_corpus"
SETS = {"corpus": "corpus.json", "round6": "round6.json", "heldout": "heldout.json", "fresh": "fresh.json",
        "round7": "round7.json", "dmtools": "dmtools.json"}
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
    """What `settle_dispute` reads, without a turn loop: the store, its state, the rules, the model, the turn id."""

    def __init__(self, store: Any, rules: Any, model: Any, turn_id: str) -> None:
        self.store, self.rules, self.model, self.turn_id = store, rules, model, turn_id
        self.tx = None
        self.calls: list[Any] = []

    @property
    def state(self) -> Any:
        return self.store.state

    def record_call(self, rec: Any) -> None:
        self.calls.append(rec)


class Taped:
    """A model that keeps every answer it gives, in order, per role (`--cached` replays them)."""

    def __init__(self, inner: Any) -> None:
        self.inner, self.tape = inner, []
        self.provider = getattr(inner, "provider", "taped")

    def fill(self, role: Any, schema: dict[str, Any], packet: Any, *, turn_id: str | None, attempt: int,
             seq: int = 0) -> Any:
        res = self.inner.fill(role, schema, packet, turn_id=turn_id, attempt=attempt, seq=seq)
        self.tape.append({"role": role.value, "data": res.data})
        return res


UPHELD = {"correct", "take_back", "player_reading_wins", "upheld"}  # spec 014's outcome names, by class
STANDS = {"explain_with_quote", "explain_and_log", "stands"}


def _class(rec: dict[str, Any]) -> str:
    return "upheld" if rec.get("upheld") else "not_found" if rec.get("outcome") == "not_found" else "stands"


def run_item(item: dict[str, Any], model: Any, rules: Any, tmp: Path) -> dict[str, Any]:
    """One report through the whole turn loop (the /fix command) on its cut save: the screen after it, the
    complaints as logged, the tools used, and the model answers (taped)."""
    from engine.dm import dm_tools
    from engine.dm.context import TurnContext
    from engine.dm.dispute import play_dm_dispute
    from engine.dm.turn import play_dispute

    store = open_at(CORPUS / item["save"], item["turn"], tmp)
    taped = Taped(model)
    try:
        made = dict(next(store.events(types=["game_created"])).payload.config or {})  # type: ignore[attr-defined]
        ctx = TurnContext.for_store(store, model=taped, rules=rules,  # the save's engine (spec 032 FR-11)
                                    config={k: made[k] for k in ("engine", "dm_secrets") if made.get(k)})
        out = (play_dm_dispute if dm_tools.enabled(ctx) else play_dispute)(ctx, item["report"])
        recs = [r for r in store.state.meta.get("corrections") or [] if isinstance(r, dict)
                and r.get("type") == "dispute"]
        recs = [r for r in recs if r.get("report") == recs[-1].get("report")] if recs else []
        complaints = [{"believes": r["believes"], "category": r["category"], "turn": r["passage"]["turn"],
                       "verdict": r["verdict"], "class": _class(r), "outcome": r["outcome"], "done": r["done"],
                       "done_kinds": r.get("done_kinds", []), "not_done": r["not_done"]} for r in recs]
        first = complaints[0] if complaints else {}
        answer = "\n".join(b.text for b in out.response.oof_blocks if b.text.startswith(("[CORRECTION]", "[FIX]")))
        return {"id": item["id"], "category": first.get("category"), "turn": first.get("turn"),
                "outcome": first.get("outcome"), "kind": recs[0].get("outcome") if recs else None, "answer": answer,
                "screen": out.response.text(), "complaints": complaints,
                "tools": (recs[0] if recs else {}).get("evidence", []), "tape": taped.tape}
    finally:
        store.close()


def _match(exp: dict[str, Any], got: list[dict[str, Any]]) -> dict[str, Any] | None:
    """The answered complaint for an expected one: the same turn, else the same class, else none."""
    turns = exp["turn"] if isinstance(exp["turn"], list) else [exp["turn"]]
    return next((c for c in got if c["turn"] in turns), None) or next(
        (c for c in got if c["class"] == exp.get("class")), None)


def score(item: dict[str, Any], got: dict[str, Any]) -> dict[str, Any]:
    """Per expected complaint: understood (category and turn), class, corrections, and the screen after the /fix."""
    plain = not any(b in got["answer"] for b in BARE) and "Now:" in got["answer"]
    exps = item["expected"]["complaints"] if "complaints" in item["expected"] else [item["expected"]]
    scr = item["expected"].get("screen") or {}
    screen = got.get("screen") or got["answer"]
    after = screen.replace(got["answer"], "") if got["answer"] else screen  # what the answer leaves on screen
    missing = [rx for rx in scr.get("must", []) if not re.search(rx, screen)]
    still = [rx for rx in scr.get("must_not", []) if re.search(rx, after)]
    still += [rx for rx in scr.get("must_not_anywhere", []) if re.search(rx, screen)]
    rows = []
    used: list[int] = []
    for exp in exps:
        cls = exp.get("class") or ("upheld" if set(exp["outcome"]) & UPHELD else
                                   "not_found" if "not_found" in exp["outcome"] else "stands")
        classes = cls if isinstance(cls, list) else [cls]
        left = [c for k, c in enumerate(got["complaints"]) if k not in used] or got["complaints"]
        c = _match({**exp, "class": classes[0]}, left)
        if c is not None and c in got["complaints"]:
            used.append(got["complaints"].index(c))
        turns = exp["turn"] if isinstance(exp["turn"], list) else [exp["turn"]]
        understood = c is not None and c["turn"] in turns and (not exp.get("category") or c["category"] in exp["category"])
        ok = c is not None and c["class"] in classes and plain
        need = set(exp.get("done") or [])
        kinds_ok = not need or bool(need & set((c or {}).get("done_kinds", [])))  # any one of the expected kinds
        auto = ("wrong" if not ok or still else "right" if kinds_ok and not missing else "unclear")
        rows.append({"id": exp.get("id", item["id"]), "understood": understood, "outcome": ok, "screen_missing": missing,
                     "screen_still": still, "auto": auto})
    return {"understood": all(r["understood"] for r in rows), "outcome": all(r["outcome"] for r in rows),
            "complaints": rows}


def model_for(name: str, engine: str = "haiku") -> Any:
    """The Fixer on `name` and the play roles on `engine` (a re-frame calls the Framer), as a live game routes them."""
    from engine.llm.base import Role, Routed

    if name == "offline":
        from engine.llm.offline import OfflineModel

        return OfflineModel()
    from evals.playtest import ClaudeModel

    return Routed(ClaudeModel(engine), {Role.FIXER: ClaudeModel(name)})


def cached_model(rec: dict[str, Any]) -> Any:
    """A run's taped answers served back per role, in order (no call)."""
    from engine.llm.base import Role
    from engine.llm.offline import ScriptedModel

    by: dict[Role, list[Any]] = {}
    for t in rec.get("tape") or []:
        by.setdefault(Role(t["role"]), []).append(t["data"])
    return ScriptedModel(by, fallback=False)


def main() -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("--model", default="offline", help="offline, or the Fixer's Claude CLI model (sonnet)")
    ap.add_argument("--engine-model", default="haiku", help="the play roles' Claude CLI model (a re-frame's Framer)")
    ap.add_argument("--set", default="corpus", choices=sorted(SETS))
    ap.add_argument("--only", default="", help="comma-separated item ids")
    ap.add_argument("--out", default="", help="write the results as JSON here")
    ap.add_argument("--cached", default="", help="re-score with the model answers taped in this results file")
    args = ap.parse_args()
    from engine.data.loader import load_rules

    rules = load_rules()
    items = [i for i in load_corpus(args.set) if not args.only or i["id"] in args.only.split(",")]
    cached = {r["id"]: r for r in json.loads(Path(args.cached).read_text(encoding="utf-8"))["results"]} \
        if args.cached else {}
    model = None if cached else model_for(args.model, args.engine_model)
    results = []
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        for item in items:
            got = run_item(item, cached_model(cached[item["id"]]) if cached else model, rules, Path(tmp))
            got["score"] = score(item, got)
            results.append(got)
            for r in got["score"]["complaints"]:
                print(f"{r['id']:<16} understood={'Y' if r['understood'] else 'n'} outcome={'Y' if r['outcome'] else 'n'}"
                      f" auto={r['auto']:<7} ({got['kind']}; {len(got['tools'])} tools)"
                      + (f" missing={r['screen_missing']}" if r["screen_missing"] else "")
                      + (f" STILL={r['screen_still']}" if r["screen_still"] else ""))
    rows = [r for g in results for r in g["score"]["complaints"]]
    n = len(rows)
    u = sum(r["understood"] for r in rows)
    o = sum(r["outcome"] for r in rows)
    auto = {k: sum(r["auto"] == k for r in rows) for k in ("right", "unclear", "wrong")}
    print(f"complaints {n}: understood {u}/{n}; outcome class {o}/{n}; auto {auto}")
    if args.out:
        label = f"{json.loads(Path(args.cached).read_text(encoding='utf-8'))['model']} (cached)" if cached else \
            f"{args.model} (play roles: {args.engine_model})"
        Path(args.out).write_text(json.dumps({"model": label, "set": args.set, "understood": u, "outcome": o, "n": n,
                                              "auto": auto, "results": results}, indent=1, ensure_ascii=False) + "\n",
                                  encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
