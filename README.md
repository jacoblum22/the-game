# The Game

A TTRPG run by an AI Dungeon Master. The DM model follows the rules and calls tools for the parts that must be
exact: rolls, damage and state. For the MVP the rules are D&D 5e (2014, SRD 5.1 content only); a system of our own,
designed for an AI DM, may replace it later. See `PLAN.md`.

Fresh start, 2026-10-11.
- `LESSONS.md`: what the first build taught us.
- `research_notes/` and `reports/`: the design research done before the first build.
- The first build (ruleset and engine) is archived under the git tags `archive/pre-reset/*`.

## Play
Requires Python 3.12. Two ways to run the DM, the same game either way:
- your own, on your Claude login in Claude Code (the Claude Agent SDK): the terminal and `dm.web`, the default;
- on the Anthropic API with a key (`ANTHROPIC_API_KEY`): `--api` in the terminal, and the browser version
  (`py -3.12 -m dm.site`), where each player brings their own key.

A save carries on the way it was started. `py -3.12 -m dm.convert saves/<file>.json` moves an SDK save to the API.

    py -3.12 -m pip install -r requirements.txt
    py -3.12 -m dm.play fighter        # or rogue, wizard
    py -3.12 -m dm.play new            # make your own character with the DM first
    py -3.12 -m dm.play --resume saves/<file>.json

Tests: `py -3.12 -m pytest -q tests`
