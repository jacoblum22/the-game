# The Game

A TTRPG run by an AI Dungeon Master. The DM model follows the rules and calls tools for the parts that must be
exact: rolls, damage and state. For the MVP the rules are D&D 5e (2014, SRD 5.1 content only); a system of our own,
designed for an AI DM, may replace it later. See `PLAN.md`.

Fresh start, 2026-10-11.
- `LESSONS.md`: what the first build taught us.
- `research_notes/` and `reports/`: the design research done before the first build.
- The first build (ruleset and engine) is archived under the git tags `archive/pre-reset/*`.

## Play
Requires Python 3.12 and an Anthropic API key in the `ANTHROPIC_API_KEY` environment variable (the DM runs on
the Anthropic API). A save from before the switch to the API is converted once with
`py -3.12 -m dm.convert saves/<file>.json`.

    py -3.12 -m pip install -r requirements.txt
    py -3.12 -m dm.play fighter        # or rogue, wizard
    py -3.12 -m dm.play new            # make your own character with the DM first
    py -3.12 -m dm.play --resume saves/<file>.json

Tests: `py -3.12 -m pytest -q tests`
