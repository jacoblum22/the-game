"""Spec 029, P9: precision and recall of the clue judgment (`Role.CLUE`) per **message**, on spec 025's labelled set
(single questions, `clue_set.yaml`) and this spec's labelled multi-part set (`clue_set_multi.yaml`), both labelled
before any run, on Claude through the CLI (`evals/playtest.py`'s model; no API spend).

    py -3.12 specs/029-lead-terms-clues/clue_eval_multi.py --model haiku [--out clue_eval_multi_haiku.txt]

Each message is judged exactly as the engine asks it (`engine/dm/roles/clue.py`: the clue prompt, the questions, the
open clue marked as held). Positive = "about the held clue". For the multi set the question that asks it (`part`) is
also scored.
"""

from __future__ import annotations

import argparse
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from engine.dm.roles.clue import message  # noqa: E402
from engine.dm.roles.prompts import load_prompt  # noqa: E402
from engine.dm.schemas import clue_schema  # noqa: E402
from engine.llm.base import Packet, Role  # noqa: E402
from evals.playtest import ClaudeModel  # noqa: E402

HERE = Path(__file__).parent
OLD = ROOT / "specs/025-hooks-clues-willingness/clue_set.yaml"


def load(path: Path, multi: bool) -> list[dict]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    rows = []
    for k, s in data["scenarios"].items():
        for it in s["items"]:
            qs = [str(q) for q in it["qs"]] if multi else [str(it["q"])]
            rows.append({"set": "multi" if multi else "single", "scenario": k, "about": s["about"], "qs": qs,
                         "exchange": str(it.get("exchange") or ""), "yes": it["label"] is True,
                         "part": str(it.get("part", "none")) if multi else "none"})
    return rows


def judge(model: ClaudeModel, it: dict) -> tuple[bool, str]:
    packet = Packet(instructions=load_prompt("clue"), core="", cards=[], view="",
                    exchanges=[it["exchange"]] if it["exchange"] else [],
                    message=message(it["qs"], [(it["about"], True)]))
    res = model.fill(Role.CLUE, clue_schema(None), packet, turn_id=None, attempt=0)  # type: ignore[arg-type]
    return str(res.data.get("about")) == "1", str(res.data.get("part") or "none")


def score(rows: list[dict], got: list[tuple[bool, str]], name: str) -> list[str]:
    tp = sum(g[0] and r["yes"] for g, r in zip(got, rows, strict=True))
    fp = sum(g[0] and not r["yes"] for g, r in zip(got, rows, strict=True))
    fn = sum((not g[0]) and r["yes"] for g, r in zip(got, rows, strict=True))
    ok = sum(g[0] == r["yes"] for g, r in zip(got, rows, strict=True))
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    out = [f"{name}: {len(rows)} messages ({sum(r['yes'] for r in rows)} yes): precision {prec:.2f} ({tp}/{tp + fp}), "
           f"recall {rec:.2f} ({tp}/{tp + fn}), accuracy {ok / len(rows):.2f}"]
    if name == "multi":
        hit = [g[1] == r["part"] for g, r in zip(got, rows, strict=True) if g[0] and r["yes"]]
        out.append(f"multi: the question that asks it named correctly on {sum(hit)}/{len(hit)} caught messages")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="haiku")
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    model = ClaudeModel(args.model)
    sets = {"single": load(OLD, False), "multi": load(HERE / "clue_set_multi.yaml", True)}
    lines = [f"clue judgment per message on {args.model}"]
    allrows: list[dict] = []
    allgot: list[tuple[bool, str]] = []
    for name, rows in sets.items():
        with ThreadPoolExecutor(6) as pool:
            got = list(pool.map(lambda it: judge(model, it), rows))
        for g, r in zip(got, rows, strict=True):
            mark = "ok " if g[0] == r["yes"] else "BAD"
            part = f" part {g[1]} (want {r['part']})" if name == "multi" else ""
            lines.append(f"{mark} {name:6} {r['scenario']:16} want {'yes' if r['yes'] else 'no ':3} got "
                         f"{'yes' if g[0] else 'no ':3}{part} | {' / '.join(r['qs'])}")
        lines += score(rows, got, name)
        allrows += rows
        allgot += got
    lines += score(allrows, allgot, "all")
    text = "\n".join(lines)
    print(text)
    if args.out:
        (HERE / args.out).write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
