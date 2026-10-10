"""Spec 005 measurement harness: the committed baselines reproduce, the plugs work, the metrics are right.

The full long-horizon run (about 75 s) is `slow`; the default suite plays a short aged and scripted run.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

import pytest

from evals import longhorizon as lh
from evals import reader_golden as rg
from evals import replay_bench as rb

BASELINES = Path(rb.ROOT) / "evals" / "baselines"


# ------------------------------------------------------------------------------------------------ plugs (also
# used by quickstart.md: `--narrator tests.evals.test_harness:echo_narrator --judge ...:pass_judge`)


def echo_narrator(packet: dict[str, Any]) -> dict[str, Any]:
    return {"fiction": "You wait.", "mentions": [{"name": "a bench", "kind": "object"}]}


def pass_judge(packet: dict[str, Any], draft: dict[str, Any]) -> list[dict[str, Any]]:
    return [{"text": draft["fiction"], "ok": True, "cls": None, "undeclared_new": False}]


def boom_narrator(packet: dict[str, Any]) -> dict[str, Any]:
    raise RuntimeError("no draft")


# ------------------------------------------------------------------------------------------------ bench


@pytest.fixture(scope="module")
def corpus() -> dict[str, Any]:
    return rb.load()


def test_corpus_is_small_and_complete(corpus: dict[str, Any]) -> None:
    assert rb.CORPUS.stat().st_size <= rb.MAX_BYTES
    assert corpus["packets"] and all(h in corpus["sections"] for p in corpus["packets"] for _, h in p["sections"])
    assert sum(1 for s in corpus["saves"].values() if s.get("late")) == 33  # B §1.2's population


def test_recorded_bench_reproduces_the_baseline(corpus: dict[str, Any]) -> None:
    assert rb.report(corpus).rstrip("\n") == (BASELINES / "replay_bench.txt").read_text(encoding="utf-8").rstrip("\n")


def test_plugged_pair_and_a_failing_plug(corpus: dict[str, Any]) -> None:
    items = rb.packet_items(corpus, 5)
    assert {"NARRATOR VIEW", "THIS MESSAGE", "_recorded"} <= set(items[0])
    m = rb.plugged_measures(items, echo_narrator, pass_judge)
    assert m["first-draft pass rate"].startswith("5/5") and m["plug errors"] == 0
    assert m["new elements per draft: declared, undeclared"] == "1.00, 0.00"
    m = rb.plugged_measures(items, boom_narrator, pass_judge)
    assert m["plug errors"] == 5 and m["first-draft pass rate"].startswith("0/5")
    assert "echo_narrator" in rb.report(corpus, "tests.evals.test_harness:echo_narrator", None, 3)


def test_the_spec_006_plug_runs_the_narration_loop(corpus: dict[str, Any]) -> None:
    """The new-contract plug: recorded packets rebuilt with handles, the offline narrator, the declaration judge
    and the repair loop's counters (the real-model run uses `evals.narration_plug:haiku`)."""
    from evals import narration_plug as plug

    items = rb.packet_items(corpus, 6)
    p = plug.Packet(items[0])
    assert p.handles and "MUST:" in p.message and "ADJUDICATION RECORD" in p.message
    m = rb.plugged_measures(items, plug.offline, plug.judge, workers=2)
    assert m["plug errors"] == 0
    assert {"turns with cut sentences", "narrator calls per turn", "turns with a rendered line"} <= set(m)


def test_instability_counts_only_rechecked_sentences() -> None:
    t = {"versions": [
        {"kind": "draft", "sents": ["a b", "c d"], "claims": [[0, "identity", False], [1, "position", False]]},
        {"kind": "cut", "sents": ["a b"], "claims": [[0, "action", False]]},
        {"kind": "redraft", "sents": ["a b", "e f"], "claims": [[0, "action", False]]},
    ]}
    assert rb.instability([t]) == (1, 1)  # "a b" re-checked once, its classes changed; the cut is skipped


# ------------------------------------------------------------------------------------------------ golden set


def test_golden_set_labels_are_legal_and_cover_the_issues() -> None:
    lines = rg.load()
    assert len(lines) >= 75 and len({g["id"] for g in lines}) == len(lines)
    verbs = set(rb.load_plug("engine.data.loader:load_rules")().basic_verbs)
    for g in lines:
        lab = g["labels"]
        assert set(lab) - {"goals_alt"} == set(rg.FIELDS), g["id"]  # goals_alt: other readings (policy E)
        assert lab["verb"] is None or lab["verb"] in verbs, g["id"]
        assert lab["gate"] in rg.GATES and lab["necessity"] in rg.NECESSITY, g["id"]
        assert lab["question_kind"] in rg.QUESTION_KINDS, g["id"]
        assert all(isinstance(lab[f], bool) for f in ("against_will", "uses_power", "speech")), g["id"]
        assert (lab["verb"] is None) == (lab["gate"] is None), g["id"]
        assert lab["necessity"] is None or lab["gate"] in ("G1", "G2"), g["id"]
    issues = {g["issue"] for g in lines if g["issue"]}
    assert {"P-004", "P-023", "P-024", "P-031", "P-038", "P-064", "P-115", "P-122", "P-123"} <= issues
    pairs: dict[str, list[str]] = {}
    for g in lines:
        if g["pair"]:
            pairs.setdefault(g["pair"], []).append(g["line"])
    assert len(pairs) >= 8 and all(len(v) == 2 and any("n't" in s for s in v) for v in pairs.values())


def test_scorer_perfect_partial_and_recorded() -> None:
    lines = rg.load()
    by_line = {g["line"]: g["labels"] for g in lines}
    perfect = rg.score(lines, lambda line, ctx: dict(by_line[line]))
    assert "- verb: 100.0%" in perfect and "- question_kind: 100.0%" in perfect
    partial = rg.score(lines, lambda line, ctx: {"verb": by_line[line]["verb"]})
    assert "- gate: not scored" in partial
    assert rg.score(lines, None) == (BASELINES / "reader_golden.txt").read_text(encoding="utf-8").rstrip("\n")


# ------------------------------------------------------------------------------------------------ long horizon


def test_metrics() -> None:
    assert lh.novelty4(["the cat sat on the mat", "the cat sat on the mat"]) == 0.0
    assert lh.novelty4(["the cat sat on the mat", "a dog ran in the yard"]) == 1.0
    assert lh.prefix_share([("r", "abcd"), ("n", "zz"), ("r", "abxy")]) == {"r": 0.5}
    p, c = lh.recall_score("Ada Ashby's occupation is a tanner.\nAda Ashby has a green hood.",
                           ["a tanner", "sells charms against the fog"], ["a tanner"], "Ada Ashby")
    assert (p, c) == (0.5, 0.5)
    assert lh.recall_score("anything", [], [], "X") == (None, None)
    assert lh.growth({"VIEW": 100, "CORE": 50}, {"VIEW": 150, "CORE": 50}) == ["VIEW 100->150"]
    turns = [{"draft_versions": [{"kind": "draft", "sample": {}}],
              "claim_log": [{"class": "identity", "verdict": "contradicted", "source": "sample", "blocking_miss": False},
                            {"class": "quantity", "verdict": "contradicted", "source": "sample", "blocking_miss": True}]},
             {"draft_versions": [{"kind": "draft"}], "claim_log": []}, {"draft_versions": []}]
    n, by = lh.contradictions(turns)
    assert n == 2 and by == {"identity": 1, "quantity": 1}
    lines = lh.claim_log_lines(turns)  # spec 011 item 12
    assert "identity/contradicted 50.0" in lines[0] and "1 of 2 narrated turns sampled; blocking-list misses 1" in lines[1]


def test_short_runs_complete() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        aged = lh.run_aged(7, 6, "offline", Path(tmp))
        scripted = lh.run_scripted(7, 14, "offline", Path(tmp))
    assert any("view tokens at scene 6" in s and "narrator" in s for s in aged)
    assert any(s.startswith("- recall probes: 3;") for s in aged)
    # P6 (spec 024): offline narration lines are labelled stub plumbing, never reported as narration measures
    assert any(s.startswith("- [offline stub") and "novelty-4" in s for s in scripted)
    assert not any(s.startswith(("- novelty-4", "- narration loop")) for s in scripted)
    assert "- engine errors: 0" in scripted
    assert "- disputes per 100 narrated turns: 0.0 (upheld 0.0)" in scripted


def test_dispute_rate_per_100_narrated_turns() -> None:  # spec 012, OEQ-12-24
    line = lh.dispute_lines({"all": 3, "upheld": 1, "by_category": {"misread": 1, "remembered_wrong": 2}}, 60)
    assert line == "- disputes per 100 narrated turns: 5.0 (upheld 1.7) (misread 1, remembered_wrong 2)"
    with tempfile.TemporaryDirectory() as tmp:
        scripted = lh.run_scripted(7, 10, "offline", Path(tmp), fix_every=4)  # two planted /fix reports
    rate = next(s for s in scripted if s.startswith("- disputes per 100"))
    assert not rate.startswith("- disputes per 100 narrated turns: 0.0") and "- engine errors: 0" in scripted


@pytest.mark.slow
def test_full_long_horizon_reproduces_the_baseline(capsys: pytest.CaptureFixture[str]) -> None:
    assert lh.main([]) == 0
    assert capsys.readouterr().out == (BASELINES / "longhorizon.txt").read_text(encoding="utf-8")
