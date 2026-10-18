"""Can Jev (TypeSafe's typed-decision model) catch the DM's contradictions? (Jake, 2026-10-18)
For each test round: the round's reply, the 10 rounds before it word for word, and the notebook entries the reply names
(as the notebook was before the round), and one yes/no question. Rounds with a confirmed contradiction finding
(games/read/causes) are the positives; rounds with no contradiction finding at all are the negatives. Nothing in the
game is changed. Needs AI_GATEWAY_API_KEY (Vercel AI Gateway) in the environment.
    PYTHONPATH=".;evals/autoloop" .venv/Scripts/python evals/autoloop/jev_check.py <negatives> <out.json>"""
import glob
import json
import os
import random
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import httpx
from metrics import GAMES

from dm import lore as notebook

N_NEG, OUT = int(sys.argv[1]), Path(sys.argv[2])
WINDOW, MAX_ENTRIES, MAX_CHARS = int(os.environ.get("JEV_WINDOW", 10)), 12, 100_000  # Jev's default limit is 64k tokens a request, 32k a question
URL, MODEL = "https://ai-gateway.vercel.sh/v1/evaluate", os.environ.get("JEV_MODEL", "typesafe-ai/jev")
QUESTION = ("Does the NEW REPLY state something that contradicts EARLIER PLAY or the NOTEBOOK, or contradicts itself? "
            "Look at numbers and counts, times, dates and ages, distances and travel times, places, who did or said "
            "what, and who has what. Something that changed because of events in play is not a contradiction, and "
            "neither is something new that doesn't clash with anything.")
HERE = Path(__file__).parent


def load(name: str) -> tuple[dict, list[list[dict]], dict[int, dict]]:
    meta = json.loads((GAMES / f"{name}.meta.json").read_text(encoding="utf-8"))
    save = json.loads((GAMES / Path(meta["save"]).name).read_text(encoding="utf-8"))
    states = {s["round"]: s for s in map(json.loads, open(GAMES / f"{name}.states.jsonl", encoding="utf-8"))}
    return meta, save, states


GAME = {g: load(g) for g in ("cleric2", "barbarian2", "bard2")}


def state(game: str, rnd: int) -> str:
    meta, save, states = GAME[game]
    t = save["transcript"]
    idx = [i for i, e in enumerate(t) if e["kind"] == "player" and i >= meta["play_starts"]][rnd - 1]
    turn = notebook.now(t[:idx + 1])
    reply = notebook.turn_text(t, turn)
    earlier = "\n\n".join(x for n in range(max(turn - WINDOW, 0), turn) if (x := notebook.turn_text(t, n)))
    lore, before = states[rnd]["lore"], t[:idx]
    entries = []
    for n in notebook.mentioned(lore, reply)[:MAX_ENTRIES]:
        try:
            entries.append(notebook.look(lore, [n], before))
        except Exception:  # noqa: BLE001
            pass
    s = (f"NOTEBOOK (the DM's notes, as they were before the new reply)\n" + "\n\n".join(entries)
         + f"\n\nEARLIER PLAY (the last {WINDOW} turns, word for word)\n{earlier}\n\nNEW REPLY\n{reply}")
    return s if len(s) <= MAX_CHARS else s[:MAX_CHARS // 3] + "\n[...]\n" + s[-2 * MAX_CHARS // 3:]


def ask(case: dict) -> dict:
    body = {"model": MODEL, "state": state(case["game"], case["round"]),
            "questions": {"contradiction": {"type": "boolean", "instructions": QUESTION}}}
    for attempt in range(4):
        try:
            r = httpx.post(URL, json=body, timeout=60,
                           headers={"Authorization": f"Bearer {os.environ['AI_GATEWAY_API_KEY']}"})
            if r.status_code == 200:
                a = r.json()["answers"]["contradiction"]
                return case | {"p": a.get("probability", a.get("noul")), "model": r.json().get("model"),
                               "tokens": r.json().get("usage", {}).get("inputTokens")}
            err = f"HTTP {r.status_code}: {r.text[:200]}"
            if r.status_code < 500 and r.status_code != 429:
                break
        except (httpx.HTTPError, KeyError, ValueError) as e:
            err = f"{type(e).__name__}: {e}"
    return case | {"error": err}


def cases() -> list[dict]:
    found = [json.loads(x) for f in glob.glob(str(HERE / "games/read/causes/*.in.jsonl")) for x in open(f, encoding="utf-8")]
    judged = {json.loads(x)["id"]: json.loads(x) for f in glob.glob(str(HERE / "games/read/causes/*.out.jsonl"))
              for x in open(f, encoding="utf-8") if x.strip()}
    pos = {}
    for d in found:
        j = judged[d["id"]]
        if j["valid"] != "no":
            k = (d["game"], d["round"])
            pos.setdefault(k, {"game": d["game"], "round": d["round"], "label": 1, "valid": [], "ids": []})
            pos[k]["valid"].append(j["valid"])
            pos[k]["ids"].append(d["id"])
    flagged = set()  # every round any reader called a contradiction, whatever the verdict: not a clean negative
    for g in GAME:
        for f in glob.glob(str(HERE / f"games/read/{g}-*.findings.txt")):
            for x in open(f, encoding="utf-8"):
                if x.startswith("{") and json.loads(x)["category"] == "contradiction":
                    flagged.add((g, json.loads(x)["round"]))
    clean = [{"game": g, "round": r, "label": 0} for g in GAME for r in range(WINDOW + 1, 181) if (g, r) not in flagged]
    return list(pos.values()) + random.Random(7).sample(clean, N_NEG)


def main() -> None:
    cs = cases()
    with ThreadPoolExecutor(8) as ex:
        res = list(ex.map(ask, cs))
    OUT.write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    ok = [r for r in res if r.get("p") is not None]
    print(f"{len(ok)} of {len(res)} answered; {sum(r.get('tokens') or 0 for r in ok)} input tokens; "
          f"errors: {sorted({r['error'][:80] for r in res if 'error' in r})}", file=sys.stderr)
    for cut in (0.3, 0.5, 0.7):
        tp = sum(r["p"] >= cut for r in ok if r["label"])
        fp = sum(r["p"] >= cut for r in ok if not r["label"])
        npos, nneg = sum(r["label"] for r in ok), sum(not r["label"] for r in ok)
        print(f"at {cut}: caught {tp} of {npos} contradiction rounds; flagged {fp} of {nneg} clean rounds", file=sys.stderr)


if __name__ == "__main__":
    main()
