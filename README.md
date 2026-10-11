# The Game

A TTRPG run by an AI Dungeon Master. The DM model reads our own rules and follows them, and calls tools for the parts
that must be exact: rolls, damage and state. The rules are our own system, designed to be run by an AI.

Fresh start, 2026-10-11.
- `LESSONS.md`: what the first build taught us.
- `research_notes/` and `reports/`: the design research done before the first build.
- The first build (ruleset and engine) is archived under the git tags `archive/pre-reset/*`.

## Play
Requires Python 3.12 and a Claude login in Claude Code (the DM runs on it through the Claude Agent SDK).

    py -3.12 -m pip install -r requirements.txt
    py -3.12 -m dm.play fighter        # or rogue, wizard
    py -3.12 -m dm.play --resume saves/<file>.json

Tests: `py -3.12 -m pytest -q tests`
