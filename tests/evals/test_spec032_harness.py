"""Spec 032 P1: the measuring tools run end to end offline (no model call), and the scorer reads a save."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from evals import h2h_score, npc_agency


def _save(path: Path, engine: str | None, *, refusal: str = "") -> Path:
    db = sqlite3.connect(path)
    db.executescript(
        "create table events(seq integer, turn_id text, type text, payload text);"
        "create table turns(turn_id text, input_verbatim text, record text, delivered_verbatim text);"
        "create table model_calls(turn_id text, tokens_in int, tokens_in_cached int, latency_ms int);")
    cfg = {"config": {"engine": engine} if engine else {}}
    db.execute("insert into events values (1,'turn.0','game_created',?)", (json.dumps(cfg),))
    db.execute("insert into events values (2,'turn.1','boundary_marked',?)",
               (json.dumps({"boundary": "conflict_start", "payload": {}}),))
    db.execute("insert into events values (3,'turn.1','time_advanced',?)",
               (json.dumps({"from": {"day": 1, "hour": 0}, "to": {"day": 1, "hour": 1}}),))
    dm = {"screen": {"dm_tools": {"refusals": [{"why": refusal}] if refusal else [], "leaks": []}}}
    db.execute("insert into turns values ('turn.0','(opening)','{}','')")
    db.execute("insert into turns values ('turn.1','I hit it',?, 'It strikes you.')", (json.dumps(dm),))
    db.execute("insert into model_calls values ('turn.1', 100, 20, 2000)")
    db.commit()
    db.close()
    return path


def test_scorer_reads_both_arms(tmp_path: Path) -> None:
    a = h2h_score.score_save(_save(tmp_path / "playtest-20261010-000000-fighter.db", None))
    b = h2h_score.score_save(_save(tmp_path / "playtest-20261010-000001-fighter-dm-tools.db", "dm-tools",
                                   refusal="REFUSED: no one or nothing on record called 'x'"))
    assert (a["arm"], a["turns"], a["tokens_in"], a["latency_ms"]) == ("pipeline", 1, 120, 2000)
    assert (b["arm"], b["prose_refusals"], b["fights"], b["foe_turns"], b["time_moved"]) == ("dm-tools", 1, 1, 1, True)
    text = h2h_score.table([a, b])
    assert len(text.splitlines()) < 40 and "C1 tokens-in ratio dm-tools/pipeline 1.00" in text


def test_npc_agency_offline_end_to_end(tmp_path: Path) -> None:
    """Both arms play all 12 cells (4 with 3 turns: 20 replies) on stand-ins and the report prints the table."""
    for arm in npc_agency.ARMS:
        assert npc_agency.cmd_ab(arm, tmp_path, offline=True) == 0
        runs = json.loads((tmp_path / f"{arm}.json").read_text(encoding="utf-8"))
        assert [r["cell"] for r in runs] == [c["id"] for c in npc_agency.CELLS]
        assert sum(len(r["turns"]) for r in runs) == 20
    assert npc_agency.cmd_report(tmp_path, voice=False) == 0


def test_npc_agency_tables_and_baseline() -> None:
    assert len(npc_agency.CELLS) == 12 and len(npc_agency.REPEATS) == 4
    assert {(c["mood"], c["cost"]) for c in npc_agency.CELLS} == {(m, k) for m in npc_agency.GRID for k in npc_agency.GRID["open"]}
    base = json.loads((Path(npc_agency.ROOT) / "evals/baselines/npc_agency_round8.json").read_text(encoding="utf-8"))
    assert len(base) == 19 and {"band", "label", "passage"} <= set(base[0])
