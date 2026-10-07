"""Record the fixed offline games that `tests/replay/test_recorded_games.py` replays (T077).

    python -m tests.replay.record_games            # rewrites tests/replay/games/*.json

Re-record only when a change to what the model is asked (prompts, cards, views, schemas) or to the events a game
writes is intended; the replay test exists to catch such changes when they are not.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from engine.game import Game
from tests.e2e.driver import Driver

GAMES = Path(__file__).resolve().parent / "games"


def offline_seed11(path: Path) -> None:
    """Mixed seed, quick start, 20 turns of varied play with a resume at each new pause kind, retirement, a new
    character, 4 more turns."""
    d = Driver.start(path, seed=11)
    d.play(20)
    d.retire_and_continue()
    d.play(4)
    d.game.close()


RECIPES = {"offline_seed11": offline_seed11}


def record(name: str) -> Path:
    with tempfile.TemporaryDirectory(prefix="record-") as tmp:
        db = Path(tmp) / "g.db"
        RECIPES[name](db)
        rec = Game.export_record(db)
    out = GAMES / f"{name}.json"
    GAMES.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rec, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    return out


def main() -> None:
    for name in RECIPES:
        out = record(name)
        print(f"{out}: {out.stat().st_size // 1024} KiB")


if __name__ == "__main__":
    main()
