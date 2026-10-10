"""Specs 014, 022 and 026: the Fixer on real and held-out complaints, code's half (PR-12-11 steps 4-7).

Each report of the fresh, round-7 and round-6 sets runs through the whole turn loop on its save cut back to just before
it, with every model answer of the committed Sonnet runs (evals/baselines/fixer_*_026.json: the Fixer on Sonnet, the
play roles on Haiku) replayed from its tape. The tools, the dry runs, validation, application and the screen are
code, so the replay must reproduce the recorded screen and score, every answer must end in `Now:`, and the report is
never pinned.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from engine.data.loader import load_rules
from evals.feedback_corpus import BARE, cached_model, load_corpus, run_item, score

BASE = Path(__file__).resolve().parents[2] / "evals" / "baselines"
RUNS = {s: {r["id"]: r for r in json.loads(p.read_text(encoding="utf-8"))["results"]}
        for s in ("fresh", "round7", "round6") if (p := BASE / f"fixer_{s}_026.json").exists()}
ITEMS = [(s, i) for s in RUNS for i in load_corpus(s) if i["id"] in RUNS[s]]


@pytest.mark.skipif(not ITEMS, reason="no recorded spec-026 runs")
@pytest.mark.parametrize(("which", "item"), ITEMS, ids=lambda x: x if isinstance(x, str) else x["id"])
def test_the_recorded_answers_replay_to_the_same_screen(which: str, item: dict[str, Any], tmp_path: Path) -> None:
    rec = RUNS[which][item["id"]]
    got = run_item(item, cached_model(rec), load_rules(), tmp_path)
    answer = got["answer"]
    assert answer.splitlines()[-1].strip().startswith("Now:") and not any(b in answer for b in BARE)
    assert item["report"] not in answer.split("Done:")[-1]
    assert got["tools"] == rec["tools"]  # the same investigation, read from the same snapshot
    assert got["screen"] == rec["screen"]  # the same repair, the same screen
    assert [r["auto"] for r in score(item, got)["complaints"]] == [r["auto"] for r in rec["score"]["complaints"]]
