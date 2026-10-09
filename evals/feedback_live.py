"""Spec 014 live check: corpus complaints re-planted in the real game with Haiku as the engine model.

    py -3.12 evals/feedback_live.py --model haiku        # 4 turns, Claude CLI (the owner's subscription)

Each report is sent through `Game` on its corpus save cut back to just before the report: `/fix` reports through
`Game.dispute`, a plain-words one through `Game.submit` (the live Reader classifies it as a DISPUTE). Prints each
reply verbatim and the model calls made.
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from evals.feedback_corpus import CORPUS, open_at  # noqa: E402

PLANTS = [  # (save, turn, how, report)
    ("20261008-145430-fighter.db.gz", "turn.6", "fix", "I succeeded but never got the purse"),
    ("20261008-145410-talker.db.gz", "turn.3", "fix",
     "the season is wrong: it's spring but he talked about the autumn harvest"),
    ("20261008-145430-fighter.db.gz", "turn.13", "fix",
     "The offer calls Murzak \"his\" weight, but Murzak Red-Hand has been \"her\" the whole scene."),
    ("20261008-135029-talker.db.gz", "turn.6", "submit",
     "Wait, that's wrong: Nero answered for the officer. I asked the officer, not Nero."),
]


def main() -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("--model", default="haiku")
    args = ap.parse_args()
    from engine.game import Game
    from evals.playtest import ClaudeModel
    from tests.e2e.driver import OFFLINE

    model = ClaudeModel(args.model)
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        for save, turn, how, report in PLANTS:
            store = open_at(CORPUS / save, turn, Path(tmp))
            path = store.path
            store.close()
            g, _ = Game.open(path, OFFLINE, model=model)
            before = model.calls
            r = g.dispute(report) if how == "fix" else g.submit(report)
            print(f"### {save} @ {turn} ({'/fix' if how == 'fix' else 'plain words'}): {report}")
            print(r.text())
            print(f"(model calls: {model.calls - before})\n")
            g.close()
    print(f"total model calls: {model.calls}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
