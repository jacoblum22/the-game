"""Spec 014: the real complaint corpus, code's half (PR-12-11 steps 2-5).

Each corpus item (tests/fixtures/feedback_corpus) runs on its save cut back to just before the report, with the
understanding the live model (Haiku) gave in the committed after run (evals/baselines/feedback_corpus_after_haiku.json)
replayed by a ScriptedModel. Verification and the outcome are code, so they must reproduce the recorded run, and every
answer must restate the complaint and end in a plain answer.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from engine.data.loader import load_rules
from engine.llm.base import Role
from engine.llm.offline import ScriptedModel
from evals.feedback_corpus import BARE, load_corpus, run_item, score

AFTER = Path(__file__).resolve().parents[2] / "evals" / "baselines" / "feedback_corpus_after_haiku.json"
RECORDED = {r["id"]: r for r in json.loads(AFTER.read_text(encoding="utf-8"))["results"]}


@pytest.mark.parametrize("item", load_corpus(), ids=lambda i: i["id"])
def test_corpus_item_reproduces_the_recorded_outcome(item: dict[str, Any], tmp_path: Path) -> None:
    rec = RECORDED[item["id"]]
    data = next(u["data"] for u in rec["understood"] if u and u.get("data"))
    model = ScriptedModel({Role.UNDERSTAND: [data]}, fallback=False)
    got = run_item(item, model, load_rules(), tmp_path)
    assert (got["category"], got["turn"], got["outcome"]) == (rec["category"], rec["turn"], rec["outcome"]), got["answer"]
    assert got["answer"].split("] ", 1)[1].startswith("You're saying "), got["answer"]
    assert not any(b in got["answer"] for b in BARE) and "Logged." not in got["answer"]
    assert score(item, got) == rec["score"]
