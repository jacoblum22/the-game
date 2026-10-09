"""The five single-goal coercion messages of round 6 (I3 §6), re-read in their recorded live context (spec 020, SC-1).

    py -3.12 evals/reader_coercion.py --mode before   # the recorded packet as sent then (old prompt, core, cards)
    py -3.12 evals/reader_coercion.py --mode after    # same view, exchanges and message; today's prompt and guidance
    py -3.12 evals/reader_coercion.py --mode after --cached

Each turn's Reader packet is read from the playtest save (read-only). `after` keeps its NARRATOR VIEW, RECENT
EXCHANGES and THIS MESSAGE and replaces the instructions, core and cards with today's Reader prompt and guidance
digest. The answer goes through today's `normalise`; a line passes when it leaves exactly one now-beat, the words'
goal (`learn` or `persuade_to`), under a computed gate that rolls (G1); `against_will` is reported (turn.5 keeps an
existing grip, B6). Answers are cached per mode.
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engine.data.loader import load_rules  # noqa: E402
from engine.dm.roles.prompts import load_prompt  # noqa: E402
from engine.dm.roles.reader import normalise, now_beats  # noqa: E402
from engine.dm.schemas import SchemaContext, build_schema  # noqa: E402
from engine.llm.base import Role  # noqa: E402
from engine.resolve.gate import compute_gate  # noqa: E402

SAVES = Path(r"C:\Users\Nelly\Documents\the-game\saves")
TURNS = [("playtest-20261008-233000-fighter.db", "turn.2"), ("playtest-20261008-233000-fighter.db", "turn.5"),
         ("playtest-20261008-233000-fighter.db", "turn.7"), ("playtest-20261008-233000-fighter.db", "turn.11"),
         ("playtest-20261008-135049-fighter.db", "turn.2")]
TITLES = ("ROLE INSTRUCTIONS", "CORE RULES", "RULE CARDS", "NARRATOR VIEW", "RECENT EXCHANGES", "THIS MESSAGE")
_HEAD = re.compile(r"^\[(" + "|".join(TITLES) + r")\]\n", re.M)
RULES = load_rules()
DEMAND = ("learn", "persuade_to")  # the words' goal: tell (learn) or do (persuade_to)


def recorded(db: str, turn: str) -> dict[str, str]:
    con = sqlite3.connect(f"file:{(SAVES / db).as_posix()}?immutable=1", uri=True)
    row = con.execute("select request from model_calls where turn_id = ? and role = 'reader' and attempt = 0 "
                      "order by row_id limit 1", (turn,)).fetchone()
    packet = json.loads(row[0])["packet"]
    parts = _HEAD.split(packet)
    return {parts[i]: parts[i + 1].rstrip("\n") for i in range(1, len(parts) - 1, 2)}


def schema(view: str) -> dict[str, Any]:
    ids = list(dict.fromkeys(re.findall(r"(?m)^([a-z]+\.[\w.]+): ", view)))
    res, pacing = RULES.resolution, RULES.pacing
    ctx = SchemaContext(input_classes=[c for c in pacing["input_classes"] if c != "PENDING_ANSWER"],
                        oracle_rungs=[r["id"] for r in res["oracle"]["rungs"]], verbs=list(RULES.basic_verbs),
                        change_kinds=list(res["intended_change"]["kinds"]), scene_ids=ids, change_ids=ids)
    return build_schema(Role.READER, ctx)


def request(sec: dict[str, str], mode: str) -> tuple[str, str]:
    """(instructions, body) for one mode."""
    if mode == "before":
        body = [(k, sec[k]) for k in TITLES[1:] if k in sec]
        return sec["ROLE INSTRUCTIONS"], "\n\n".join(f"[{k}]\n{v}" for k, v in body)
    from engine.retrieve.cards import guidance_digest

    body = [("GUIDANCE", guidance_digest(Role.READER))] + [(k, sec[k]) for k in TITLES[3:] if k in sec]
    return load_prompt("reader"), "\n\n".join(f"[{k}]\n{v}" for k, v in body)


def verdict(data: dict[str, Any]) -> tuple[bool, str]:
    beats = now_beats(normalise(dict(data)).get("beats", []))
    kinds = [(b.get("change") or {}).get("kind") for b in beats]
    if len(beats) != 1:
        return False, f"{len(beats)} now-beats {kinds}"
    b = beats[0]
    c = compute_gate(b.get("verb"), against_will=bool(b.get("against_will")), uses_power=bool(b.get("uses_power")),
                     speech=bool(b.get("speech")), method=f"{b.get('method')} {b.get('intent')}", held=[], rules=RULES)
    ok = kinds[0] in DEMAND and c.gate == "G1"
    return ok, f"1 now-beat {kinds[0]}, {c.verb}, gate {c.gate}, against_will {bool(b.get('against_will'))}"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").split("\n")[0])
    ap.add_argument("--mode", choices=("before", "after"), default="after")
    ap.add_argument("--model", default="haiku")
    ap.add_argument("--cached", action="store_true")
    args = ap.parse_args(argv)
    cache = ROOT / "evals" / "baselines" / f"reader_coercion_{args.mode}_{args.model}.jsonl"
    done = {r["key"]: r["answer"] for r in map(json.loads, cache.read_text(encoding="utf-8").splitlines())} \
        if cache.exists() else {}
    passed = 0
    for db, turn in TURNS:
        key = f"{db}#{turn}"
        sec = recorded(db, turn)
        if key not in done and not args.cached:
            from evals.playtest import ask_claude

            ins, body = request(sec, args.mode)
            done[key], _ = ask_claude(ins, body, schema(sec.get("NARRATOR VIEW", "")), args.model)
            with cache.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps({"key": key, "answer": done[key]}) + "\n")
        ok, why = verdict(done[key])
        passed += ok
        print(f"- {key}: {'PASS' if ok else 'FAIL'} ({why}) :: {sec['THIS MESSAGE'][:70]}")
    print(f"{args.mode}: {passed}/{len(TURNS)} single-goal coercion messages give one rolled goal beat")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
