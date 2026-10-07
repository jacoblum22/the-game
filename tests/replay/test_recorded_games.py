"""T077: fixed offline games recorded under tests/replay/games/ replay identically: the same inputs, with the
recorded model responses, ask the model exactly the recorded packets and write exactly the recorded events. A
failure means an engine change altered what the model is asked or what the game writes; if that is intended,
re-record with `python -m tests.replay.record_games`."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from engine.game import Game

GAMES = sorted((Path(__file__).resolve().parent / "games").glob("*.json"))


def test_there_is_a_recorded_game() -> None:
    assert GAMES, "no recorded game: python -m tests.replay.record_games"


@pytest.mark.parametrize("path", GAMES, ids=[p.stem for p in GAMES])
def test_recorded_game_replays_identically(path: Path) -> None:
    record = json.loads(path.read_text(encoding="utf-8"))
    res = Game.replay_record(record)
    assert res.identical, f"{res.divergence}\n(intended? re-record: python -m tests.replay.record_games)"
    assert res.inputs == len(record["inputs"]) and res.events == len(record["events"])


def test_a_changed_packet_is_detected() -> None:
    record = json.loads(GAMES[0].read_text(encoding="utf-8"))
    call = next(c for c in record["calls"] if c["role"] == "narrator" and c["turn_id"])
    call["request"]["packet_sha256"] = "0" * 64  # as if the engine had asked the narrator something else
    res = Game.replay_record(record)
    assert not res.identical and "packet changed" in (res.divergence or "")
