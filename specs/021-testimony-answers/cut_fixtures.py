"""Cut the round-6 saves into test fixtures (the 015/018 pattern): the save as it stood before a turn, events after
the cut removed, model calls dropped, gzipped into tests/fixtures/. Read-only on the saves (they are gitignored).

    py -3.12 specs/021-testimony-answers/cut_fixtures.py
"""

from __future__ import annotations

import gzip
import shutil
import sqlite3
import tempfile
from pathlib import Path

SAVES = Path("C:/Users/Nelly/Documents/the-game/saves")
OUT = Path(__file__).resolve().parents[2] / "tests" / "fixtures"
CUTS = [("playtest-20261008-233000-fighter.db", 7, "testimony_fighter_turn7.db.gz"),
        ("playtest-20261008-232941-talker.db", 6, "testimony_talker_turn6.db.gz"),
        ("playtest-20261008-232941-talker.db", 13, "testimony_talker_turn13.db.gz")]


def cut(save: str, turn: int, name: str) -> None:
    src = sqlite3.connect(f"file:{(SAVES / save).as_posix()}?mode=ro", uri=True)
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "cut.db"
        dst = sqlite3.connect(path)
        src.backup(dst)
        src.close()
        seq = dst.execute("SELECT MIN(seq) FROM events WHERE turn_id = ?", (f"turn.{turn}",)).fetchone()[0] - 1
        triggers = dst.execute("SELECT name, sql FROM sqlite_master WHERE type = 'trigger'").fetchall()
        for t, _ in triggers:  # the append-only guards: lifted on the copy for the cut, then restored
            dst.execute(f"DROP TRIGGER {t}")
        dst.execute("DELETE FROM events WHERE seq > ?", (seq,))
        dst.execute("DELETE FROM snapshots WHERE seq > ?", (seq,))
        dst.execute("DELETE FROM rng_draws WHERE event_seq > ?", (seq,))
        dst.execute("DELETE FROM facts_idx WHERE valid_from_seq > ?", (seq,))
        dst.execute("UPDATE facts_idx SET valid_to_seq = NULL WHERE valid_to_seq > ?", (seq,))
        dst.execute("DELETE FROM rulings_idx WHERE event_seq > ?", (seq,))
        dst.execute("DELETE FROM game_inputs WHERE seq_before >= ?", (seq,))
        dst.execute("DELETE FROM model_calls")
        turns = [r[0] for r in dst.execute("SELECT turn_id FROM turns")]
        for t in turns:
            if t.startswith("turn.") and int(t.split(".")[1]) >= turn:
                dst.execute("DELETE FROM turns WHERE turn_id = ?", (t,))
        for _, sql in triggers:
            dst.execute(sql)
        dst.commit()
        dst.execute("VACUUM")
        dst.close()
        with path.open("rb") as f, gzip.open(OUT / name, "wb") as g:
            shutil.copyfileobj(f, g)
    print(name, seq, (OUT / name).stat().st_size)


if __name__ == "__main__":
    for c in CUTS:
        cut(*c)
