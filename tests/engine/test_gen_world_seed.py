"""The world seed as a stepped procedure (T055, PR-12-9): steps, summaries, vetoes, modes, own words, the check."""

from __future__ import annotations

from typing import Any

import pytest

from engine.gen import world_seed as W
from engine.gen.world_seed import ORACLE, SeedError, WorldSeed, build_rolled


def run_steps(ws: WorldSeed, upto: int = 13) -> list[W.SeedStep]:
    return [ws.run_step() for _ in range(ws.next_step, upto + 1)]


def test_stepped_run_equals_the_rolled_path() -> None:
    ws = WorldSeed.from_seed(11, mode="oracle")
    out = run_steps(ws)
    assert [s.n for s in out] == list(range(1, 14))
    assert ws.record() == build_rolled(11).record


def test_summaries_are_seed_blocks_and_withhold_sealed_parts() -> None:
    ws = WorldSeed.from_seed(3, mode="oracle")
    out = run_steps(ws)
    for s in out:
        assert s.summary.startswith(f"[SEED {s.n:d}/14] ")
    reg = ws.record()
    text = "\n".join(s.summary for s in out)
    for f in reg["factions"]["instances"]:
        assert f["goal"]["text"] not in text                        # faction goals are sealed
    for p in reg["places"]:
        if p["site"]:
            assert p["site"]["objective"]["text"] not in text        # site objectives are sealed
    assert "sec." not in text and "keeps" not in text                 # secrets and the powers' truths
    assert "partial" not in out[10].summary and "false" not in out[10].summary   # rumor truths are sealed


def test_veto_rerolls_once_and_keeps_other_answers() -> None:
    ws = WorldSeed.from_seed(5, mode="oracle")
    run_steps(ws, 7)
    before = {a.question: a.answer for a in ws.history[-1].answers}
    v = ws.veto("ws.q.rulers")
    after = {a.question: a.answer for a in v.answers}
    assert v.vetoed and v.n == 7
    assert after["ws.q.fourth_faction"] == before["ws.q.fourth_faction"]
    assert [a.source for a in v.answers] == ["oracle", "oracle"]
    with pytest.raises(SeedError):
        ws.veto()
    run_steps(ws)
    assert all(c.ok for c in ws.run_check())
    # the answer log holds the vetoed step once, with its new answers
    log = ws.record()["seed"]["answers"]
    assert [a["question"] for a in log].count("ws.q.rulers") == 1
    assert next(a for a in log if a["question"] == "ws.q.rulers")["answer"] == after["ws.q.rulers"]


def test_veto_of_a_whole_step_and_of_an_engine_only_step() -> None:
    ws = WorldSeed.from_seed(8, mode="oracle")
    run_steps(ws, 2)
    ws.veto()                                       # every oracle answer of step 2 rolled again
    run_steps(ws, 8)
    ws.veto()                                       # step 8 asks nothing: its engine draws are rolled again
    run_steps(ws)
    assert all(c.ok for c in ws.run_check())


def test_veto_refuses_a_player_answer() -> None:
    ws = WorldSeed.from_seed(9, mode="mixed")
    ws.answer("ws.q.wound", "long_winter")
    ws.run_step()
    with pytest.raises(SeedError):
        ws.veto("ws.q.wound")
    v = ws.veto("ws.q.climate")
    assert {a.question: a.source for a in v.answers} == {"ws.q.wound": "player", "ws.q.climate": "oracle"}


def test_modes() -> None:
    with pytest.raises(SeedError):
        WorldSeed.from_seed(1, mode="oracle").answer("ws.q.wound", "long_winter")
    g = WorldSeed.from_seed(1, mode="guided")
    with pytest.raises(SeedError, match="ws.q.wound"):
        g.run_step()
    g.answer("ws.q.wound", "long_winter")
    g.answer("ws.q.climate", ORACLE)               # the player hands this one to the oracle
    s = g.run_step()
    assert {a.question: a.source for a in s.answers} == {"ws.q.wound": "player", "ws.q.climate": "oracle"}
    with pytest.raises(SeedError):
        g.answer("ws.q.climate", "arid")            # its step has run


def test_own_words_are_kept_as_description() -> None:
    ws = WorldSeed.from_seed(2, mode="mixed")
    words = "only the old families do magic"
    ws.answer("ws.q.arcane_source", "order_only", words=words)
    run_steps(ws)
    reg = ws.record()
    fact = next(f for f in reg["canon"]["facts"] if f["id"] == "canon.arcane_source")
    assert fact["value"] == "order_only" and fact["text"] == words
    assert next(a for a in reg["seed"]["answers"] if a["question"] == "ws.q.arcane_source")["words"] == words
    assert ws.history[1].answers[3].source == "player_words"


def test_world_views_and_place_graph() -> None:
    w = WorldSeed.from_seed(4, mode="oracle").run_all()
    assert w.check and all(c.ok for c in w.check)
    ids = {p.id for p in w.places}
    assert w.region.haven in ids and w.incident.place in ids
    assert all(r.a in ids and r.b in ids and r.watches >= 1 for r in w.routes)
    assert len({r.id for r in w.routes}) == len(w.routes)
    adj: dict[str, set[str]] = {}
    for r in w.routes:
        adj.setdefault(r.a, set()).add(r.b)
        adj.setdefault(r.b, set()).add(r.a)
    seen, todo = set(), [w.region.haven]
    while todo:
        x = todo.pop()
        if x not in seen:
            seen.add(x)
            todo += adj.get(x, set())
    assert {p.id for p in w.places if p.kind in ("area", "site")} <= seen
    assert len(w.incident.leads) == 3 and len([t for t in w.threads if t.kind == "situation"]) == 2
    assert all(n.pronouns and n.gender for n in w.cast)
    dumped: dict[str, Any] = w.model_dump()
    assert "goal" not in dumped["factions"][0]


def test_a_failed_check_reruns_the_step_that_writes_the_key(monkeypatch: pytest.MonkeyPatch) -> None:
    real = W.check_seed
    calls = {"n": 0}

    def flaky(reg: dict[str, Any]) -> list[tuple[str, bool, str]]:
        calls["n"] += 1
        res = real(reg)
        if calls["n"] == 1:
            return [(r, False if r == "ws.req.11_calendar" else ok, n) for r, ok, n in res]
        return res

    monkeypatch.setattr(W, "check_seed", flaky)
    ws = WorldSeed.from_seed(6, mode="oracle")
    run_steps(ws)
    months = ws.record()["calendar"]["months"]
    res = ws.run_check()
    assert all(c.ok for c in res) and calls["n"] == 2
    assert ws.history[-1].n == 14 and "re-run" in ws.history[-1].summary
    assert "steps 12-13 re-run" in ws.history[-1].summary            # the calendar is step 12's key
    assert isinstance(months, list)


def test_questions_list_options() -> None:
    qs = W.questions(1)
    assert [q["id"] for q in qs] == ["ws.q.wound", "ws.q.climate"]
    assert "long_winter" in qs[0]["options"] and "temperate" in qs[1]["options"]
