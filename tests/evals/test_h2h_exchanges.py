"""Spec 033 P9: the scorer counts an exchange only where a roll resolved in a live fight, counts a fight a take-back
reverted as no fight, and names a fight the PC's blow ended before any foe call (trace-no-foe-turns.md)."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from evals import h2h_score


def _ev(db: sqlite3.Connection, seq: int, turn: str, typ: str, **p: object) -> None:
    db.execute("insert into events values (?,?,?,?)", (seq, turn, typ, json.dumps(p)))


def test_one_resolved_roll_is_one_exchange_and_the_reverted_fight_is_not_counted(tmp_path: Path) -> None:
    db = sqlite3.connect(tmp_path / "playtest-20261011-000000-fighter-dm-tools.db")
    db.executescript("create table events(seq integer, turn_id text, type text, payload text);"
                     "create table turns(turn_id text, input_verbatim text, record text, delivered_verbatim text);"
                     "create table model_calls(turn_id text, tokens_in int, tokens_in_cached int, latency_ms int);")
    _ev(db, 1, "turn.0", "game_created", config={"engine": "dm-tools"})
    _ev(db, 10, "turn.2", "meta_set", key="conflict", value={})
    _ev(db, 11, "turn.2", "boundary_marked", boundary="conflict_start")  # reverted by turn.3's take-back
    _ev(db, 12, "turn.3", "writes_reverted", reverted=[10])
    _ev(db, 20, "turn.4", "meta_set", key="conflict", value={})
    _ev(db, 21, "turn.4", "boundary_marked", boundary="conflict_start")
    _ev(db, 30, "turn.7", "boundary_marked", boundary="conflict_end")  # the blow killed the foe...
    _ev(db, 31, "turn.7", "frame_resolved", frame_id="f.1")  # ...its roll is written after the end
    _ev(db, 32, "turn.8", "frame_resolved", frame_id="f.2")  # outside the fight
    world = {"screen": {"dm_tools": {"world": {"foe_turns": [], "foe_calls": 0}}}}
    for n in range(8):
        db.execute("insert into turns values (?,?,?,?)", (f"turn.{n}", "(opening)" if n == 0 else "x", json.dumps(world), ""))
    db.commit()
    db.close()
    r = h2h_score.score_save(tmp_path / "playtest-20261011-000000-fighter-dm-tools.db")
    assert (r["fights"], r["fight_exchanges"], r["foe_turns"], r["pc_blow_fights"]) == (1, 1, 0, 1)
    assert "1 / 1 / 0 (1)" in h2h_score.table([r])
