"""Spec 025, D2 A: precision and recall of the clue judgment (`Role.CLUE`) on the labelled set `clue_set.yaml`
(labelled before any run), on Claude through the CLI (`evals/playtest.py`'s model; no API spend).

    py -3.12 specs/025-hooks-clues-willingness/clue_eval.py --model haiku [--out clue_eval_haiku.txt]

Each item is judged exactly as the engine asks it (`engine/dm/roles/clue.py`: the clue prompt, the question, the
exchange when there is one, the open clue marked as held). Positive = "about the held clue".
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


def items() -> list[dict[str, str]]:
    data = yaml.safe_load((HERE / "clue_set.yaml").read_text(encoding="utf-8"))
    return [{"scenario": k, "about": s["about"], **{x: str(v) for x, v in it.items()}}
            for k, s in data["scenarios"].items() for it in s["items"]]


def judge(model: ClaudeModel, it: dict[str, str]) -> str:
    packet = Packet(instructions=load_prompt("clue"), core="", cards=[], view="",
                    exchanges=[it["exchange"]] if it.get("exchange") else [],
                    message=message(it["q"], [(it["about"], True)]))
    res = model.fill(Role.CLUE, clue_schema(None), packet, turn_id=None, attempt=0)  # type: ignore[arg-type]
    return "yes" if str(res.data.get("about")) == "1" else "no"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="haiku")
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    model = ClaudeModel(args.model)
    rows = items()
    with ThreadPoolExecutor(6) as pool:
        got = list(pool.map(lambda it: judge(model, it), rows))
    tp = sum(g == "yes" and r["label"] == "True" for g, r in zip(got, rows, strict=True))
    fp = sum(g == "yes" and r["label"] != "True" for g, r in zip(got, rows, strict=True))
    fn = sum(g == "no" and r["label"] == "True" for g, r in zip(got, rows, strict=True))
    lines = [f"clue judgment on {args.model}: {len(rows)} items ({sum(r['label'] == 'True' for r in rows)} yes)"]
    for g, r in zip(got, rows, strict=True):
        want = "yes" if r["label"] == "True" else "no"
        lines.append(f"{'ok ' if g == want else 'BAD'} {r['scenario']:16} want {want:3} got {g:3} | {r['q']}")
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    acc = sum(g == ("yes" if r["label"] == "True" else "no") for g, r in zip(got, rows, strict=True)) / len(rows)
    lines.append(f"precision {prec:.2f} ({tp}/{tp + fp}), recall {rec:.2f} ({tp}/{tp + fn}), accuracy {acc:.2f}")
    text = "\n".join(lines)
    print(text)
    if args.out:
        (HERE / args.out).write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
