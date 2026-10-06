# The Game: Ruleset (v1.0 release candidate)

This is the complete rules system for a classic-fantasy, open-sandbox TTRPG run by an AI Dungeon
Master. Its mechanics are hidden from the player. Death is real but always telegraphed. The ruleset
serves two goals: **the player can try anything**, and **the AI rules correctly**. Player-facing
complexity is deliberately not a constraint, because the AI carries the rules.

**Status:** the rules are complete enough to start building on.
- Every chapter is authored and integrated. The validator reports 0 errors and 0 warnings.
- Balance claims are backed by seeded simulations.
- Verification passed: completeness 175 of 189 checklist rows, plus a red team and a paper playtest.
- Remaining issues are listed below. None of them blocks building.

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
| `15-social-investigation-downtime.md` | Social contests, investigation, downtime |
| `16-companions-and-allies.md` | Companions, hirelings, allies |
| `data/*.yaml` | 56 machine-readable content and rules files: abilities, adversaries, tags, tables, and generator inputs. `data/SCHEMAS.md` defines them. Many are produced by generator scripts in `_process/simulation/`. Edit the generator, not the output. |
| `data/anchors.yaml` | Compiled retrieval anchors, built by `_process/simulation/12-compile_anchors.py` |
| `appendix/decision-log.md` | Every design decision and its reasoning (DL-CC-NN) |
| `appendix/traceability.md` | Constitution principle → rule mapping |
| `_process/` | How the rules were made: briefs, research digests (R1–R7), the issue ledger, wave reports, and the simulations |

Chapter 14 (the Player's Guide and the in-game codex spec) is not written. It is deferred until the
interface exists, because it is player-facing presentation rather than rules.

## Tooling

```
python _process/validate_ruleset.py                 # cross-file check: refs, ids, tags, YAML; expect 0 ERROR / 0 WARN
python _process/simulation/12-compile_anchors.py    # rebuild data/anchors.yaml after editing rule cards
python _process/simulation/12-world-seed.py         # generate a world seed (example: 12-world-seed-example.yaml)
python _process/simulation/10-word-audit.py         # encounter-table danger audit (PR-10-8)
```

All simulations are seeded and deterministic. Each output file sits next to its script.

## Known open issues (from `_process/issue-ledger.md`)

None of these blocks building. Each is a rules-text or tuning change that can land while the engine
is built. The ledger has the evidence and a proposed fix for every row.

**MAJOR**
- **I-037:** `power_band` is defined inconsistently. Ch.04 and 05 count provisional tiers; ch.07 counts only confirmed tiers. Pick one definition in 00.
- **I-038:** the free Oracle can be fished for +4 levers on every roll. It needs a per-scene cap or cost.
- **I-039:** contest band from faction tier lets a band-1 talker earn band-5 evidence from a minor functionary. Rate the deed by the individual's own band.
- **I-040:** the encounter danger audit assumes Guard 14, but a Guard 10 healer drops to 0 Vitality in roughly 21% of encounters. Audit against the actual party, or the weakest member.
- **I-041:** rematching the same foe daily farms evidence and loot. Add a per-creature or per-site diminishing lock.

**MINOR** (24 rows)
- **Tuning:** I-033 condition pricing, I-034 ch.04 pacing tables, I-036 wealth curve at P3, I-045 pacing vs the shipped tables, I-047 training licences.
- **Text consistency:** I-042 Wren's Vitality traces, I-043, I-044, I-046.
- **Rules gaps:**
  - I-048: one term makes a request certain.
  - I-051: urban play.
  - I-052 to I-062: playtest ambiguities.
- **Housekeeping:** I-049 versioning, I-050 credits.

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
