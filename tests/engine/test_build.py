"""Tests for the card compiler (T008) and the coverage report (T009). Never modifies rules/."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from engine.build import compile_cards as cc
from engine.build import coverage as cov


@pytest.fixture(scope="module")
def doc() -> dict:
    return cc.compile_cards()


@pytest.fixture(scope="module")
def index(doc: dict, tmp_path_factory: pytest.TempPathFactory) -> cc.CardIndex:
    out = tmp_path_factory.mktemp("cards") / "cards.json"
    cc.write_cards(doc, out)
    return cc.load_cards(out)


def test_compile_runs_ids_unique(doc: dict) -> None:
    ids = [c["id"] for c in doc["cards"]]
    assert len(ids) > 1000
    assert len(ids) == len(set(ids))
    assert not any(c["chapter"] == "13" for c in doc["cards"])
    assert {c["kind"] for c in doc["cards"]} == {"rule", "section", "table", "procedure", "example"}


def test_committed_cards_are_current() -> None:
    assert cc.OUT.exists(), "run python engine/build/compile_cards.py"
    assert not cc.is_stale(), "rules changed: run python engine/build/compile_cards.py"


def test_every_anchor_rule_resolves(index: cc.CardIndex) -> None:
    anchors = yaml.safe_load((cc.RULES / "data/anchors.yaml").read_text(encoding="utf-8"))["anchors"]
    rule_ids = {str(a["rule_id"]) for a in anchors if re.match(r"^\d{2}(\.\d+[a-z]?)+$", str(a["rule_id"]))}
    assert rule_ids
    missing = sorted(i for i in rule_ids if i not in index)
    assert not missing
    assert all(index.get(i).anchors for i in rule_ids)


def test_core_and_tags(index: cc.CardIndex) -> None:
    core = index.core()
    assert core and [c.id for c in core] == cc.CORE_IDS
    strike = index.get("06.4.3")
    assert "[D]" in strike.kinds and strike.trigger and strike.worst_case
    assert "situation.conflict" in strike.tags and not strike.tags_derived
    melee = {c.id for c in index.by_tag("situation.conflict.melee")}
    assert "06.4.3" in melee  # ancestor tag loads in the more specific situation
    assert "06.4.3" not in {c.id for c in index.by_tag("situation.social")}
    assert index.get("01.2.1").tokens > 0


def _copy_rules(dst: Path) -> Path:
    rules = dst / "rules"
    (rules / "data").mkdir(parents=True)
    for p in cc.source_files(cc.RULES):
        shutil.copy(p, rules / p.relative_to(cc.RULES))
    return rules


def test_check_detects_stale_hash(tmp_path: Path) -> None:
    rules = _copy_rules(tmp_path)
    out = tmp_path / "cards.json"
    args = ["--rules", str(rules), "--out", str(out)]
    assert cc.main(args + ["--check"]) == 1  # no cards.json yet
    assert cc.main(args) == 0
    assert cc.main(args + ["--check"]) == 0
    ch = rules / "01-resolution.md"
    ch.write_text(ch.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    script = Path(cc.__file__)
    run = subprocess.run([sys.executable, str(script), *args, "--check"], capture_output=True, text=True)
    assert run.returncode == 1 and "STALE" in run.stdout


def test_coverage_classifies(index: cc.CardIndex, tmp_path: Path) -> None:
    (tmp_path / "mod.py").write_text(
        "x = 1  # rule: 01.1.3, PR-01-1\ny = 2  # coarse: 06.4.3\nz = 3  # rule: 99.9.9\n", encoding="utf-8"
    )
    tags = cov.scan_tags(tmp_path)
    assert tags == {"rule": {"01.1.3", "PR-01-1", "99.9.9"}, "coarse": {"06.4.3"}}
    cards = list(index)
    status = cov.classify(cards, tags, milestone=1)
    assert status["01.1.3"] == "implemented" and status["PR-01-1"] == "implemented"
    assert status["06.4.3"] == "coarse"
    assert status["06.5.2"] == "deferred"  # ch.06 is Milestone 2
    assert status["14.1.1"] == "deferred"  # ch.14 is in no milestone
    assert cov.classify(cards, tags, milestone=2)["06.5.2"] != "deferred"
    judged = next(c for c in cards if c.kind == "rule" and c.chapter == "01" and c.model_judged)
    assert status[judged.id] == "model"
    text = cov.report(cards, tags, 1, "implemented")
    assert "99.9.9" in text and "01: 01.1.3 PR-01-1" in text
    assert len(text.splitlines()) < 30
