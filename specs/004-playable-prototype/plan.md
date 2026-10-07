# Implementation Plan: Playable Prototype

**Branch**: `004-playable-prototype` (work lands on `claude/project-thread-q2smmv`, based on
`integration-wave-swxsot`) | **Date**: 2026-10-07 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/004-playable-prototype/spec.md`, the ruleset in `rules/`
(v1.0 RC), and the earlier stack research on branch `claude/happy-franklin-ypo2wq`.

## Summary

Build the game as a prototype the owner can play from "new game" to the character's end, with no turn
limit, delivered in seven milestones. **Milestone 1 is the whole arc**: the world seed, character
creation, the opening, unlimited play across scenes and places, NPCs, the Oracle, risk with an offer before
every roll, harm, rest, death with a warning first, an epilogue, and quit/resume at any moment. Every
action goes through the one resolution pipeline (PR-01-1), so things whose full rules come later (round-by-
round fights, journeys, crafting) are still playable in Milestone 1, at the coarser grain the pipeline and
the rules' anchors give them. Milestones 2–7 add fights, growth, the road, items, the living world, and
companions/downtime/legacy.

The technical approach is unchanged from the research (research.md, Option A): a Python engine in which
**code drives the loop and the model fills typed forms**. At each `[J]` step the engine builds a JSON
Schema whose enums come from the rules and the current state, and asks a model role to fill it. Every
`[D]` step is code tagged with its rule id. Gemini 3.8 Flash fills every role, on one API key (owner
decision, 2026-10-07); the claim checker is a separate call that can move to another model family by
configuration (`TODO(CROSS_FAMILY_CHECKER)`). State is a SQLite event log per game. Milestone 1 is played
in a terminal; a web interface is a separate track after it.

## Technical Context

**Language/Version**: Python 3.11+ (matches `pyproject.toml` on `claude/project-thread-9ivqgo`)

**Primary Dependencies**: `pydantic` v2 (state objects, per-turn schemas), `PyYAML` (rules data),
`google-genai` 2.25.0 (already pinned; every model role), `pytest`. Nothing else in the engine. All
hash-pinned.

**Storage**: SQLite (standard library `sqlite3`, WAL), one file per game: append-only `events` table as
source of truth, in-memory typed projection, snapshots at scene ends, index tables for facts and rulings.
See [data-model.md](data-model.md).

**Testing**: pytest. Unit and golden tests (worked examples with fixed dice, generator parity with the
reference sims) and contract tests run with no network. Replay tests use recorded model outputs. Playtests
and persona runs are separate commands, never part of `pytest`.

**Target Platform**: a terminal on the owner's machine (Linux, macOS or Windows; `.env` with
`GEMINI_API_KEY`). Built and tested in the cloud container; played locally, via Remote Control when needed.

**Project Type**: Library (the engine) plus a terminal front end.

**Performance Goals**: offer shown within 5 s of a rolled declaration; a non-pausing turn within 10 s
(median); per-turn cost and latency flat over a 500-turn game (SC-002). Engine work under 50 ms per turn.

**Constraints**: no number from the model (INV-3); writes before prose (12.2.8); checker as a separate,
swappable call (P13, cross-family deferred); one API key; ≤12 cards plus core per call and only four
verbatim exchanges (00.15.4, 12.2.4); median ≤3¢ per turn; no turn caps, a player-set budget with
warnings only; `rules/` is read-only.

**Scale/Scope**: one player per game; games of thousands of turns (10⁵–10⁶ events); all 16 chapters by
Milestone 7; 105 boundary handlers (about 36 in Milestone 1); 129 anchors; 56 data files.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle / pattern | How this plan meets it | Status |
|---|---|---|
| I. AI-driven mechanical resolution | The model makes every judgment that sets something in motion; code runs only `[D]` steps, in the order PR-12-1 fixes. This matches 00-architecture's "Principle I, stated precisely". The constitution's wording now matches it | Pass (amended v2.0.0) |
| II. Custom ruleset | The engine implements `rules/` directly | Pass |
| III. Flexibility within bounds | Anchors with at most two knob deltas; precedent before any adaptation; ruling ledger with `review_flag` | Pass |
| IV. MVP scope | One player per game, text only | Pass |
| V. Closed primitives | Creation uses the rules' closed slots and pools (02, 05.2); abilities from the closed template grammar (05.3) | Pass (M1 creation; full in M3) |
| VI. Consolidation | Provisional status, picks and retirement come with growth (04.8, 05.12) in M3; no progression content is authored here | Pass (M3) |
| VII. Default-deny gate | GATE with G0–G4; licence ids are enums from the character's holdings | Pass |
| P1 layered variance | The birth draw (PR-02-4) and the Bent (PR-02-5) run in creation | Pass |
| P3 ambiguity, not granularity | Every judgment is a closed-list field with a stated default | Pass |
| P7 codex | Out-of-fiction lookups of the character's own state by visibility class (FR-011); presentation per ch.14 when it is written | Pass (plain text in M1) |
| P8 deterministic degrees | `roll_check` and the degree rule (01.8.1) in code | Pass |
| P13 three-layer split | Code owns mechanics; the event store owns state; the checker is a separate call with `unknown` abstention and code-computed verdicts; moderation separate from consistency. **The checker shares the narrator's family (Gemini)**, by owner decision | Deviation, recorded below |
| P16 / P17 | T10 "next step exists"; G3/G4 redirects; lead injection; compound questions per 01.10 | Pass |
| Technology Constraints: `TODO(TECH_STACK)` | Resolved by this plan; the stack is recorded in the constitution, with `TODO(CROSS_FAMILY_CHECKER)` open against P13 | Pass (amended v2.0.0) |

One recorded deviation (P13's different-family checker), justified under Complexity Tracking. Re-checked
after Phase 1 design: unchanged.

## How a game runs

```text
new game ── world seed (PR-12-9: mode, steps 1–13, [SEED n/14] summaries, seed check)
         ── creation (PR-02-7 quick start / PR-02-1 workshop / PR-02-3 ready-made; PR-02-4 birth; PR-02-6 finish)
         ── opening (12.16.16): session_start, a scene framed at the incident
play     ── turn after turn (below), no limit
         ── scenes framed and cut (PR-12-7); time advances by mode; boundaries run their handlers
         ── moving between places on the place graph; rests; NPCs generated on first meeting
end      ── death (after the warning and a choice), retirement or career end
         ── epilogue from the record; new character in this world, or a new world
any time ── quit / resume (12.5 recap), codex lookups, budget warnings between turns
```

### One turn

```text
player message
  │ T1  log verbatim                                                            [code]
  │ T2+ A1 READ ── classify parts; PARSE/GATE/NECESSITY per beat; fact questions + Oracle odds   [Gemini]
  │ T3  load: triggers, narrator view, cards (≤12 per call)                     [code]
  │ T4  per beat: gate checks, find_rulings, anchor candidates (≤8)             [code]
  │      A2 FRAME ── anchor, deltas, attribute, deed tag, obstacle, levers, snags,
  │                  stakes, lethal, reach, threatened + alternate cost, method consequences    [Gemini]
  │      frame_check (refuse → re-ask A2 once naming the failure)               [code]
  │      ── OFFER pause ── (or auto-commit, 01.7.4) ── commit / change / withdraw / trade
  │      roll, read (near-miss pause), consequence, harm (07), record, evidence, beat_end   [code]
  │ T5  W WORLD (only if someone must respond) ── wants/refusals; engine rolls tbl.npc_action   [Gemini]
  │      clocks, triggers, advance_time / mark_boundary                         [code]
  │      S DIRECT (scene start/cut, pacing push, lead injection) ── closed-list choices        [Gemini]
  │ T6  all writes committed as events; re-read narrator view                   [code]
  │ T7–8 B DRAFT ── prose + mention list → write on mention / settle unsettled  [Gemini]
  │ T9–10 C CHECK ── claims (subjects constrained to the scene) + screen flags  [Gemini; TODO cross-family]
  │      check_claims verdicts; D REDRAFT ≤2 → else plain fallback              [code / Gemini]
  │ T11 deliver   T12 log verbatim, counters, scene cut if the question is answered   [code]
```

Seed and creation answers use an **Interpret** role (classify the player's own words onto the step's
options, 12.16.2, PR-02-7); epilogues and recaps use the Narrator from the record. Model call shapes are in
[contracts/model-calls.md](contracts/model-calls.md).

## Milestones

Each milestone ends with a playable game from new game to ending, a playtest by the owner, and a results
note. Handlers not yet built are logged as skipped (FR-026); `engine/build/coverage.py` reports per milestone
which rule ids are implemented, coarse (handled by the pipeline's anchor), deferred, or left to the model.

| Milestone | Adds | Chapters / procedures | Boundary handlers switched on |
|---|---|---|---|
| **M1 Start to finish** | World seed, creation, opening, unlimited turns, scenes and pacing, place-graph moves, NPC generation and social record, Oracle and tables, starting abilities and Focus, harm states, lethal warning, yield/retreat, Threshold and last chance, rests and recovery, death and a simple epilogue, codex lookups, save/resume/replay, budget | 12 (all but venture bookkeeping), 01, 02, 00, 07.1–07.5 and 07.8, 05.4 and 05.6, 09.2 (improvised foes), 10.1, 15.1–15.4, 11.12 (chronicle), 11.13 (epilogue, simple) | about 36: 00 durations, clock_auto, reflection; 01 all; 02 all; 05 scene/day recharge, focus_recover, rest_recharge; 07 natural/rest recovery, lethal_scan, load_clear, career_end; 08 durations; 10 site_time, scene_frame; 11 fallback_counters; 12 all but intensity and venture_bookkeeping; 15 patience_reset, commitments_due |
| **M2 Fights** | Rounds, tempo, action pool, positions and bands, attacks and defenses, reactions, conditions, morale, escape and chases; adversaries from archetypes and bands with behaviours; wounds, marks, afflictions, dread | 06, 09, the rest of 07 | 05 round/conflict recharge; 06 all; 07 after_conflict, dying_check, affliction_*, fatigue, curse_cycle; 12 intensity; 15 alertness_decay; 16 held_line (allies come in M7) |
| **M3 Growth** | Evidence settlement and tallies, recognition passes, callings and tiers, offers, picks, provisional status and consolidation; full abilities, magic, rites; training licences | 03, 04, 05, 15.11 | 03 all; 04 all; 05 reslot, reserve, provisional_abilities; 07 vitality_max |
| **M4 The road** | Journeys by the watch, navigation, roles, supply, light, weather, the time-tick check, encounters; sites, hazards, traps | 10 | 10 all; 12 venture_bookkeeping |
| **M5 Things** | Loot, buying and selling, crafting, gifts, carrying, identification, mounts and vessels | 08 | 08 upkeep, markets, craft_decay |
| **M6 The living world** | Factions and the World Turn, situations, threads and hooks, rumours, reputation, institutions, the calendar; deception, investigation, negotiation, social conflict | 11, 15.5–15.9 | 11 all; 15 standing_week, member_standing, placement_audit |
| **M7 Company, downtime, legacy** | Allies, loyalty, breaking points; the downtime week and long projects; full retirement and legacy | 16, 15.10, 15.12–15.13, 11.13, 07 legacy | 16 all; 15 downtime_*; 00 reflection_if_downtime |

**What "coarse" means in M1, by example.** A fight is a sequence of ordinary rolled beats (Strike, Evade,
Force anchors) against an adversary improvised by PR-09-2, with harm applied by `apply_harm` and the lethal
warning before any lethal frame. Leaving town for the next settlement advances time by the route's length
on the place graph and frames a scene on arrival, with the travel handlers logged as not yet built. A spell
attempt by a character without magic is a G3 redirect, as it is in every milestone.

### Inside Milestone 1 (input for `/speckit-tasks`)

1. **Foundation.** Data loader and validation of `rules/data`; event store, projection, views and snapshots;
   RNG streams; card compiler and coverage report.
2. **Deterministic resolution.** `frame_check` (PR-00-1, PR-01-2), degree rule, odds (T-01-3), read, cost
   menu, Oracle (T-01-10), `roll_table`, rulings; `apply_harm` and harm states (PR-07-1); rests (PR-07-8);
   golden tests from WE-00-*, WE-01-*, and ch.07's examples.
3. **Time and boundaries.** Time ladder and modes, scheduler (phases, ordering, interrupts, skipping time
   runs everything), the M1 handlers, skipped-handler logging.
4. **Generators.** World seed (port of `12-world-seed.py`, exact parity on the same seed), birth draw
   (`gen_birth`), NPC generation (PR-12-5), improvised adversaries (PR-09-2).
5. **Model layer.** Gemini and replay adapters, per-role schema builders, budget tracking, refusal handling;
   contract tests.
6. **Turn loop.** PR-12-1 with every in-scope pause point, T5 world responses, scene direction and pacing,
   write-on-mention, the claim check with redrafts and the plain fallback, the T10 screen. Built first
   against a test scene and test character (fixtures), then wired to the real start.
7. **The game around the loop.** New game → seed → creation → opening; place-graph moves; abilities and
   Focus; the lethal warning, Threshold and last chance; death or retirement → epilogue → continue the world;
   recap on resume; codex lookups.
8. **Terminal front end.** Main menu (new game, continue, replay, report), the play screen, pause choices,
   slash commands.
9. **Evaluation.** Seeded-error set and checker recall; persona harness; owner playtests; results in
   `specs/004-playable-prototype/implementation-results.md`.

Each step ends with ruff, pyright and pytest clean.

## Project Structure

### Documentation (this feature)

```text
specs/004-playable-prototype/
├── spec.md              # /speckit-specify output
├── plan.md              # this file
├── research.md          # Phase 0: stack options, decisions R1–R12, cost estimate
├── data-model.md        # Phase 1: events, state families, records the engine adds
├── quickstart.md        # Phase 1: how to validate Milestone 1 end to end
├── contracts/
│   ├── engine-api.md    # the game API the terminal (and later the web app) uses
│   ├── model-calls.md   # the model roles: inputs, schemas, defaults
│   └── cli.md           # the terminal interface
├── checklists/requirements.md
└── tasks.md             # /speckit-tasks output (not created here)
```

### Source Code (repository root)

```text
engine/                        # new package; src/ (the probes) stays as-is for comparison
├── data/                      # RC-DATA: load rules/data/*.yaml, validate ids and enums
├── build/                     # compile_cards.py → cards.json; coverage.py (per-milestone rule coverage)
├── store/                     # RC-STORE, RC-LOG, RC-SEAL: events, projection, views, snapshots
├── rng.py                     # RC-RNG: named random.Random streams, every draw logged
├── time/                      # RC-SCHED: time ladder, modes, scheduler, handler registry
│   └── handlers/              # one module per owner chapter: h00.py … h16.py
├── resolve/                   # PR-01-1 [D] steps: gate, frame_check, roll, read, costs, oracle, rulings
├── harm/                      # ch.07: apply_harm, harm states, warnings, threshold, rests (grows in M2)
├── abilities/                 # ch.05: use, Focus, recharge (grows in M3)
├── gen/                       # generators: world_seed, birth, npc, adversary (loot, gift, craft in M5)
├── world/                     # place graph, scenes, NPC social records, chronicle, threads (grows in M4/M6)
├── retrieve/                  # RC-RETRIEVE: anchors (≤8), cards (≤12), triggers
├── audit/                     # RC-AUDIT: check_claims verdicts, plain fallback, T10 screen; safety.py (separate)
├── dm/                        # PR-12-1 orchestrator (turn.py), packet.py, schemas.py, seed/creation/opening/ending/session
│   └── roles/                 # interpret, reader, framer, world, director, narrator, checker (+ prompts)
├── llm/                       # StructuredModel adapters: gemini.py, replay.py, offline.py (free stand-in); budget; env
├── ids.py                     # deterministic ids from the event counter
└── game.py                    # the game API (contracts/engine-api.md)

play/
├── __main__.py                # python -m play
├── cli.py                     # terminal front end (contracts/cli.md); play/web/ later
└── report.py                  # report and replay commands

tests/
├── engine/                    # unit tests per module
├── golden/                    # worked examples with fixed dice; T-01-3, T-01-10; generator parity
├── contract/                  # schema builders vs recorded states and outputs
├── replay/                    # recorded games replay to identical events
├── seeded_errors/             # ≥40 drafts with known claim errors (SC-003)
└── fixtures/                  # a test scene and test character for loop tests

evals/
├── personas.py                # honest / curious / adversarial players (port of Feature 002's harness)
└── run_persona.py             # budgeted persona games → report
```

**Structure Decision**: a new top-level `engine/` package separates the real engine from the probes in
`src/`, which keep working as a comparison baseline. `play/` holds front ends, which depend only on
`engine.game`. `engine/` mirrors the 00.14.1 runtime capabilities plus one package per rules area that
grows across milestones, so each milestone mostly adds modules rather than reworking them.

## Complexity Tracking

| Violation or added complexity | Why | Simpler or compliant alternative, and why not now |
|---|---|---|
| **P13 deviation:** the checker is Gemini, the narrator's family (`TODO(CROSS_FAMILY_CHECKER)`) | Owner decision (2026-10-07): one provider and one key | A second-family checker (gpt-oss on Groq, or Claude Haiku) is the compliant design and stays the target. Limits on the risk now: the checker is a separate call that never sees the narrator's prompt or reasoning; it only extracts claims and the verdicts are code; its recall is measured on seeded errors (SC-003). **Revisit** before anyone but the owner plays, or sooner if recall misses the target. Switching is a config change plus one adapter |
| Event log plus projection instead of plain tables | Unlimited games need exact resume (FR-010), replay (FR-038) and `revert_writes` | Mutable tables lose the history that replay, revert and long-game debugging need |
| Seven milestones of coarse-then-full systems | The owner wants the whole game playable now, and the full rules are about 1,500 deterministic rules | Building every chapter before the first playable game would delay play by months and test nothing end to end until the end |
