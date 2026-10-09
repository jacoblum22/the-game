"""Specs 014 and 022: the Fixer on real complaints, code's half (PR-12-11 steps 4-7).

Each report of the round-6 and held-out sets runs on its save cut back to just before it, with the Fixer answers
Sonnet gave in the committed runs (evals/baselines/fixer_*_sonnet.json) replayed by a ScriptedModel. The tools,
validation and application are code, so every answer must end in `Now:`, never pin the report, and refuse what
the record does not allow (identity fields, the clue trail).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from engine.data.loader import load_rules
from engine.llm.base import Role
from engine.llm.offline import ScriptedModel
from evals.feedback_corpus import BARE, load_corpus, run_item

BASE = Path(__file__).resolve().parents[2] / "evals" / "baselines"
RUNS = {s: {r["id"]: r for r in json.loads((BASE / f"fixer_{s}_sonnet.json").read_text(encoding="utf-8"))["results"]}
        for s in ("round6", "heldout")}
ITEMS = [(s, i) for s in RUNS for i in load_corpus(s)]


@pytest.mark.parametrize(("which", "item"), ITEMS, ids=lambda x: x if isinstance(x, str) else x["id"])
def test_the_recorded_fixer_answers_replay_through_code(which: str, item: dict[str, Any], tmp_path: Path) -> None:
    rec = RUNS[which][item["id"]]
    script = [u["data"] for u in rec["understood"] if u and u.get("data") is not None]
    got = run_item(item, ScriptedModel({Role.FIXER: script}, fallback=False), load_rules(), tmp_path)
    answer = got["answer"]
    assert answer.splitlines()[-1].strip().startswith("Now:") and not any(b in answer for b in BARE)
    assert item["report"] not in answer.split("Done:")[-1]
    assert got["tools"] == rec["tools"]  # the same investigation, read from the same snapshot
    if item["id"] == "232941-t12":  # Sonnet proposed overwriting the captain's pronouns: identity is not a fact
        assert "Not done: set fact: Sevella de Belac's pronouns is fixed on record" in answer
    if item["id"] == "192926-t12":  # ... and removing the carter's pointer to Ivas: the clue trail is the spine
        assert "is part of the mystery's clue trail" in answer
