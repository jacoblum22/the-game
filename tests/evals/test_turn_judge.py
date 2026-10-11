"""Spec 033 phase E (R11, C11): the turn judge, its hand-verdict precision, and the two scorers that read it. Offline."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

import pytest

from evals import h2h_score, npc_agency, turn_judge


def _save(path: Path, *, rounds: bool = False) -> Path:
    db = sqlite3.connect(path)
    db.executescript(
        "create table events(seq integer, turn_id text, type text, payload text);"
        "create table turns(turn_id text, input_verbatim text, record text, delivered_verbatim text);"
        "create table model_calls(turn_id text, tokens_in int, tokens_in_cached int, latency_ms int);")

    def ev(seq: int, turn: str | None, ty: str, **p: Any) -> None:
        db.execute("insert into events values (?,?,?,?)", (seq, turn, ty, json.dumps(p)))

    ent = lambda i, kind, name, **d: {"id": i, "kind": kind, "name": name, "data": d}  # noqa: E731
    ev(1, None, "game_created", config={"engine": "dm-tools"})
    ev(2, None, "entity_created", entity=ent("pc.ana", "pc", "Ana"))
    ev(3, None, "entity_created", entity=ent("npc.bram", "npc", "Bram", pronouns="he/him", secrets=["Bram owes the reeve eleven crowns"]))
    ev(4, None, "entity_created", entity=ent("npc.mira", "npc", "Mira", pronouns="she/her"))
    for who, where in (("pc.ana", "loc.dock"), ("npc.bram", "loc.dock"), ("npc.mira", "loc.hall")):
        ev(5, None, "position_set", entity=who, location=where)
    ev(6, "turn.2", "relationship_set", a="npc.bram", b="pc.ana", kind="standing", value=2)
    ev(7, "turn.2", "handler_ran", name="noise")
    ev(8, "turn.3", "boundary_marked", boundary="conflict_start", payload={})
    if rounds:
        ev(9, "turn.3", "boundary_marked", boundary="round", payload={})
    db.execute("insert into turns values ('turn.1','(opening)','{}','You stand on the dock.')")
    rec = {"screen": {"dm_tools": {"tools": [{"tool": "ask", "out": "bram agrees for a price"}]}}, "said": [{"w": 1}]}
    db.execute("insert into turns values ('turn.2','Will you hide me?',?, 'Bram grins. \"Ten crowns.\"')", (json.dumps(rec),))
    db.execute("insert into turns values ('turn.3','I hit it',?, 'It strikes you.')", (json.dumps({"said": []}),))
    db.execute("insert into turns values ('turn.4','/fix typo','{}', 'Noted.')")
    db.execute("insert into turns values ('turn.5','(session close)','{}', 'Bye.')")
    db.commit()
    db.close()
    return path


def test_packet_cast_secrets_log(tmp_path: Path) -> None:
    s = turn_judge.Save(_save(tmp_path / "s.db"))
    assert s.eligible() == ["turn.2", "turn.3", "turn.4"]  # not the opening or the session close
    p = s.packet("turn.2")
    assert "PRESENT: Bram (he/him)" in p["cast"] and "ELSEWHERE: Mira (she/her)" in p["cast"]
    assert "eleven crowns" in p["secrets"] and "relationship_set" in p["log"] and "handler_ran" not in p["log"]
    assert "tool ask: bram agrees for a price" in p["log"] and "stand on the dock" in p["earlier"]


def test_offline_run_cache_and_rubric(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    save, cache = _save(tmp_path / "s.db"), tmp_path / "cache"
    res = turn_judge.run_save(save, n=2, seed=3, offline=True, cache_dir=cache,
                              fixtures={"turn.2": {"ask": "priced"}, "turn.3": {"ask": "priced"}})
    assert len(res) == 2 * len(turn_judge.MEASURES)  # two sampled turns, every measure
    assert all(v["label"] in ("none", "priced") for v in res.values()) and turn_judge.cached(save, cache, True) == res
    assert turn_judge.cached(save, cache) == {}  # the stand-in's file is never read as the judge's
    calls: list[str] = []
    monkeypatch.setattr(turn_judge, "verdict", lambda m, p, offline=False: calls.append(m) or {"label": "none", "why": ""})
    turn_judge.run_save(save, n=2, seed=3, offline=True, cache_dir=cache)
    assert calls == []  # everything cached
    monkeypatch.setattr(turn_judge, "rubric_hash", lambda: "changed")
    assert turn_judge.cached(save, cache, True) == {}  # a changed rubric drops the cache


def test_live_judge_rejects_unknown_label(monkeypatch: pytest.MonkeyPatch) -> None:
    import evals.playtest as pt

    seen: list[str] = []
    monkeypatch.setattr(pt, "ask_claude", lambda sys_, prompt, schema, model: (seen.append(prompt), ({"label": "bogus", "why": "x"}, {}))[1])
    out = turn_judge.live_judge("ask", {"player": "Hide me", "passage": "Ten crowns.", "log": ""})
    assert out["label"] == "none" and "THE PASSAGE:\nTen crowns." in seen[0] and "THE LOG:\n(none)" in seen[0]


def test_precision_unmeasured_until_twenty() -> None:
    hand = [{"measure": "leak", "judge": "leaked", "hand": "leaked" if i % 4 else "none"} for i in range(19)]
    assert turn_judge.precision("leak", hand) == "precision unmeasured (19 of 20 hand verdicts)"
    assert turn_judge.precision("ask", hand).startswith("precision unmeasured (0 of 20")
    hand.append({"measure": "leak", "judge": "leaked", "hand": "leaked"})
    assert turn_judge.precision("leak", hand) == "precision 0.75 (15/20 flagged confirmed, n=20 hand-checked)"
    only_none = [{"measure": "mood", "judge": "none", "hand": "none"}] * 20
    assert "no flagged turn" in turn_judge.precision("mood", only_none)


def test_priced_is_not_a_cave_in_the_report() -> None:
    vs = [{"label": "priced"}, {"label": "priced"}, {"label": "caved"}, {"label": "none"}]
    line = turn_judge.count_line("ask", vs, [])
    assert line.startswith("ask: 1 caved of 4 judged") and "priced 2" in line and "precision unmeasured" in line


def test_hand_file_and_template(tmp_path: Path) -> None:
    res = {"s": {"turn.2|leak": {"label": "leaked", "why": ""}, "turn.2|ask": {"label": "priced", "why": ""},
                 "turn.3|ask": {"label": "caved", "why": ""}}}
    t = tmp_path / "hand.yaml"
    t.write_text(turn_judge.template(res), encoding="utf-8")
    assert [(r["turn"], r["measure"]) for r in __import__("yaml").safe_load(t.read_text())["verdicts"]] == [
        ("turn.2", "leak"), ("turn.3", "ask")]  # flagged only; priced is not flagged
    assert turn_judge.load_hand(t) == []  # hand: null rows are not verdicts yet
    t.write_text(t.read_text().replace("hand: null", "hand: leaked", 1), encoding="utf-8")
    assert len(turn_judge.load_hand(t)) == 1


def test_h2h_reads_judge_and_trap_one(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(turn_judge, "CACHE_DIR", tmp_path / "cache")
    save = _save(tmp_path / "playtest-20261010-000000-fighter-dm-tools.db", rounds=True)
    plain = h2h_score.score_save(save)
    assert plain["judged_turns"] == 0 and plain["fight_exchanges"] == 1 and plain["told"] == 1  # round mark; said list
    fixture = {"turn.2": {"leak": "leaked", "ask": "priced", "mood": "uncaused"}}  # the judge's answers, stubbed
    monkeypatch.setattr(turn_judge, "verdict", lambda m, p, offline=False: turn_judge.offline_judge(m, p))
    turn_judge.run_save(save, n=5, fixtures=fixture)
    row = h2h_score.score_save(save)
    assert row["judged_turns"] == 3
    text = h2h_score.table([row])
    assert "| C7 leaks (judge, flagged turns) | - | 1 |" in text and "turn judge leak: precision unmeasured" in text
    assert "caved / priced / mood changes with no cause | - | 0 / 1 / 1 |" in text
    assert len(text.splitlines()) < 40


def test_npc_agency_priced_and_leak_judge() -> None:
    cell = npc_agency.CELLS[0]
    assert npc_agency.leaked(cell, "He says nothing of the debt.", offline=True) is False
    assert "priced" in npc_agency.LABELS and "conditional" not in npc_agency.LABELS
    assert npc_agency.violates("priced", "refuse") and not npc_agency.violates("priced", "partial_or_refuse")
    turns = [{"label": "priced", "ask": "a", "reply": "r", "in_character": False, "leak": False}]
    runs = [{"cell": "A3", "turns": turns}, {"cell": "A4", "turns": [dict(turns[0], label="granted")]}]  # A3 real, A4 big
    s = npc_agency.summarize(runs)
    assert (s["costly_asks"], s["costly_priced"]) == ("1/2", "1/2")  # the priced deal is not counted as a cave
