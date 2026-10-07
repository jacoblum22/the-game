# The Game: Ruleset

`ruleset_version: 1.0.0` (versioning and save migration: 00.16.6)

This is the complete rules system for a classic-fantasy, open-sandbox TTRPG run by an AI Dungeon
Master. Its mechanics are hidden from the player. Death is real but always telegraphed. The ruleset
serves two goals: **the player can try anything**, and **the AI rules correctly**. Player-facing
complexity is deliberately not a constraint, because the AI carries the rules.

**Status: complete and verified (1.0.0).**
- **Authored:** every chapter, 00–16, is written and integrated. Chapter 13 is an optional example
  setting; no rule depends on it.
- **Validated:** the validator reports 0 errors and 0 warnings. Every rule card in chapters 00–12 and
  14–16 cites its basis.
- **Simulated:** balance claims are backed by seeded, deterministic simulations.
- **Verified:**
  - full consistency reads of every chapter;
  - a constitution audit (constitution v1.8.0 records the ruleset's resolutions);
  - an R5 completeness check;
  - a red team;
  - three paper playtests (newcomer, adversarial, long arc) in a generated world.
- **Issues:** every ledger issue is closed: 102 resolved, 4 accepted, 4 wontfix (setting-only). See
  "Issue status" below.

## Layout

| Path | What it is |
|---|---|
| `00-architecture.md` | How the system fits together: the rule-card format, state model, boundary/handler registry, retrieval (00.15), and the id prefix registry. **Start here for the build.** |
| `01-resolution.md` | The core roll, Oracle, judgment calls, and how freeform actions get a ruling |
| `02-character.md` | Character creation, attributes, peoples, livelihoods |
| `03-tags-and-evidence.md` | The tag vocabulary and the deed/evidence system that drives growth |
| `04-recognition-and-growth.md` | Callings and tiers, recognised from what the player actually does (emergent progression) |
| `05-abilities-focus-magic.md` | Abilities, Focus (the resource), and the arcane, divine and primal branches |
| `06-conflict.md` | Fights: actions, mastery, reactions, morale |
| `07-harm-recovery-death.md` | Wounds, injuries, afflictions, dying, legacy |
| `08-items-loot-crafting.md` | Items, the loot generator, crafting, economy |
| `09-adversaries.md` | Archetypes, templates, encounter budgets, behaviours |
| `10-exploration-travel-sites.md` | Travel, navigation, hazards, sites, encounter tables (PR-10-8 danger audit) |
| `11-living-world.md` | Factions, clocks, the world turn |
| `12-dm-procedures.md` | The AI DM's loop, claim checking, pacing, and the **world-seed procedure (12.16)** for starting a game with no setting |
| `13-starter-setting.md` | *Optional, unmaintained* example setting (the Thallen March). No rule depends on it. |
| `14-players-guide.md` | The Player's Guide (premise, how to play, session zero, quick sheet) and the **codex spec**: the player-facing reference layer and the preference record every chapter reads |
| `15-social-investigation-downtime.md` | Social contests, investigation, downtime |
| `16-companions-and-allies.md` | Companions, hirelings, allies |
| `data/*.yaml` | 56 machine-readable content and rules files: abilities, adversaries, tags, tables, and generator inputs. `data/SCHEMAS.md` defines them. Many are produced by generator scripts in `_process/simulation/`. Edit the generator, not the output. |
| `data/anchors.yaml` | Compiled retrieval anchors, built by `_process/simulation/12-compile_anchors.py` |
| `appendix/decision-log.md` | Every design decision and its reasoning (DL-CC-NN) |
| `appendix/traceability.md` | Constitution principle → rule mapping |
| `appendix/open-empirical-questions.md` | The 140 defaults that rest on judgment or simulation, each with the named test that would confirm it: the playtest agenda for the built game |
| `appendix/credits.md` | Designs consulted; no third-party text is reproduced |
| `tools/rq.py` | Rule lookup: print any rule card, section, table, procedure, example, decision or data entry by id |
| `_process/` | How the rules were made: briefs, research digests (R1–R7), the issue ledger, wave reports, and the simulations |

## Tooling

```
python _process/validate_ruleset.py                 # cross-file check: refs, ids, tags, YAML; expect 0 ERROR / 0 WARN
python _process/simulation/12-compile_anchors.py    # rebuild data/anchors.yaml after editing rule cards
python _process/simulation/12-world-seed.py         # generate a world seed (example: 12-world-seed-example.yaml)
python _process/simulation/10-word-audit.py         # encounter-table danger audit (PR-10-8)
python tools/rq.py <id> | --toc 06 | --refs <id>    # look up rules by id instead of reading chapters
python _process/simulation/integration-assemble-appendix.py  # rebuild decision log + traceability from appendix/fragments/
python _process/build-oeq-appendix.py               # rebuild appendix/open-empirical-questions.md
```

All simulations are seeded and deterministic. Each output file sits next to its script.

## Issue status (`_process/issue-ledger.md`)

All 110 issues are closed. Each row records its evidence and resolution.
- **Accepted (4):** I-010, I-012, I-014 and I-021. These are web citations that could not be fetched from
  the build environment; 38 of the 39 are backed by a research-digest citation
  (`_process/reports/verification-citations.md`).
- **Wontfix (4):** issues concerning only the optional ch.13 setting.

New issues found while building go into the same ledger. Rule changes follow 00.16.6, so a live save
migrates.

## For the build

What matters for the tech stack:
- **Rules are rule-cards for retrieval, not a prompt to load wholesale** (00.15). The engine retrieves
  cards by tag and anchor, from `data/anchors.yaml` and `tags.yaml`, and adapts them to the action.
- **Deterministic mechanics belong in code; judgment belongs to the model.** Rules are tagged [D]
  (deterministic), [J] (judgment) and [N] (narrative). Each chapter's "State touched" section lists
  the state the engine must hold.
- **Boundaries and handlers** (`data/boundaries.yaml`, 00.7) define what runs when: at each beat, round, conflict start
  and end, hour, day, interval, long rest, reflection and mode change. This is the engine's event loop.
- **Generators** (loot, birth, crafting, gifts, world seed) are table-driven from `data/`, so they can
  be ported to code directly from the YAML and the Python sims.
