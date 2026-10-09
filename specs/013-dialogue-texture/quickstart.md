# Quickstart: validating spec 013

Windows, from the repo root, `PYTHONUTF8=1`.

1. `py -3.12 -m pytest -q -p no:cacheprovider` — full suite passes (new tests: `tests/engine/test_dialogue_texture.py`).
2. `uvx ruff check <touched files>`; `uvx pyright <touched files>`.
3. `py -3.12 -m tests.replay.record_games` — re-record the replay (packets changed on purpose).
4. `py -3.12 evals/longhorizon.py --mode scripted` — 0 engine errors; read the OEQ-12-25 counts.
5. Live, once: `py -3.12 evals/playtest.py --engine claude --player claude --engine-model haiku --persona talker --turns 15 --quick-setup`;
   count "I don't know" turns, verbatim NPC repeats, interjections; read the player notes.
