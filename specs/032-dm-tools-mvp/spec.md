# Feature spec 032: the one-DM-with-tools engine becomes the MVP engine (close the 13 gaps, confirm, switch the default)

**Input**: owner decision 2026-10-10, option A (build the MVP on spec 031's `engine/dm/dm_tools.py`, not the multi-role
pipeline); `research_notes/Playtest round 2 solutions/EXPERIMENT-DM-WITH-TOOLS-RESULTS.md` ("Prototype gaps", the arm x
measure table); `specs/031-dm-with-tools/implementation-results.md`; constitution VIII (esp. VIII.1, 2, 4, 5, 6, 7);
rules 12.3.1b, 12.11.9, PR-12-1, 06.9.2, 00.7.3, 12.4.2, DL-12-138 (only measured checks block); spec 028 WIP
(`3e94efe:evals/npc_agency.py`); specs 021, 029 (testimony, `learned`).
**Status**: design only (slice 1). `cases.md`, `plan.md` (with its analysis section) and `tasks.md` sit beside this file.

## Principles that shape every fix (owner, binding)

1. **Code owns the spine only**: dice and odds, state (health, conditions, coin, items, positions, presence, time,
   clocks, advancement), the case graph and clue delivery. **The model owns language and judgment**: who answers,
   reactions, words.
2. **Facts, never orders**: code tells the DM what is true (a foe struck, an hour passed, a clock ticked, who is
   here, a person's pronouns). It never tells the DM how someone reacts or what to say. No forced texture.
3. **Enforce only spine facts**: alive and present; item owned; coin from a real source; no sealed secret given
   outside the clue rule; nothing done to the PC without a roll. A breach gets **one revision**, then the action is
   **dropped and logged**. Every other check is **log-only** unless its precision is measured (DL-12-138).
4. **Better context, not more rules. Reuse the pipeline's pieces; delete rather than add.**

## The gaps, and the one-line decision for each

Evidence for each is in the results note; the two traced here are G1/G4/G7 (below).

| # | Gap | Decision (detail in `plan.md`) |
|---|---|---|
| G1 | Fights: foes never strike back | After each exchange in a fight, run the pipeline's foe turn (`world_step.foes_act`, `conflict.foe_beat`) **in code**, before the DM writes the passage; the DM is handed the result as a fact. |
| G2 | Time and the world do not move | A code step around the DM turn (not a tool): per-exchange time cost by the scene's mode (`clock.beat_cost`, `scheduler.advance_time`), then the clocks' omens, fired triggers, lead injection (`pacing.inject_lead`) and the scene cut (`scenes.cut_due`) are handed to the DM as facts. No Director model call. |
| G3 | What NPCs tell the PC never reaches the journal | The DM's final answer lists what each person said (`said`: person, words); code writes `testimony.add_said` records. Testimony, not fact; the journal (`codex._told`) already shows them attributed. |
| G4 | People who exist only in prose cannot be targeted | One resolver for every tool argument: id, then exact name, then `mentions.write_mentions` (creates a minimal NPC or a creature marked `mind: animal`, positioned here). |
| G5 | Items arrive by assertion | Item moves go through `change give_item`; the situation lists what each person carries and what lies loose; a `new_item` that duplicates a thing someone holds echoes that as a fact. A passage that hands over an item with no change call is **logged** (measured, not blocking). |
| G6 | Pronouns and presence | The DM sees pronouns on every card (already) and a short "not here" line for people the PC has met who are elsewhere. Presence is enforced in the tools (`_acting`, already). A pronoun check (`audit.claims._pronoun_hit`) runs **log-only**. |
| G7 | "Promised a roll, none came" | Traced (below). Fix: fight facts in the situation (G1/G4 make the foe real) and one sentence of judgment guidance: a declared act is attempted this turn, not deferred to the next. No regex check. |
| G8 | OFFER title and framing | The OFFER title is the DM's own short act words; the failure cost is **chosen by the DM from the 9 `cost.*` menu ids** and validated by `frame_check`, replacing the code's verb-to-cost guess. |
| G9 | Leak audit false flags | Drop every entity's name tokens from the overlap. It stays a measure, never a block. |
| G10 | Resuming a save drops its engine | `game_created.config` already stores it; `Game.open` reads it. A missing key means `pipeline`. |
| G11 | `/fix` ignores dm-tools turns | Smallest correct way: keep `/fix` engine-agnostic (the Fixer reads the store and turn log); give it the dm-tools turn's tool log as evidence and make its `reframe` use the code framer when the game is dm-tools. |
| G12 | Default engine | `GameConfig.engine` becomes `"dm-tools"` in the **last** slice, only after the confirming test passes. The pipeline stays selectable (`--engine pipeline`). |
| G13 | Confirming harness | Port `evals/npc_agency.py` and its baseline; the 12 mood x cost cells guarantee costly asks, so the pushover rate and ceiling violations are measurable. Lean scoring script for the headline numbers. |

### Trace of the traced gaps (fighter save `playtest-20261010-153123-fighter-dm-tools.db`, 16 turns)

- **No fight ever started.** The save has no `conflict_start` boundary. In turns 9 and 12 the DM's first `propose_roll`
  named "the beast in the clearing" / "the pale beast" and was `REFUSED: no one or nothing on record`. It re-proposed
  with no target. `pipeline._attacks` needs an entity target, so no conflict was recorded, so `foes_act` (had it run)
  had nothing to act on. The beast was never an entity. Harm came only from failed rolls on the PC (Vitality 12 to 4).
- **The dead end (turn 11, transcript [26]).** The player's message declared three acts: roll away, scramble for
  the mace, swing again. The DM made **zero tool calls** and wrote a passage that resolved the first part in prose
  (the jaws "close on empty mud") and ended "you have one chance to reach the haft ... before it commits again". The
  next Enter had no OFFER because none was ever proposed. The model was given the conversation and the PC sheet
  (Vitality 4, bloodied) but **no fact that a fight was on, who the foe was, or that it was about to act**, and its
  prompt says "end on something the player can act on" and "write only the lead-up" without saying that a declared
  act is attempted now. Cause: missing context plus the prompt's lead-up wording, not a code defect. No regex check.

## User stories (each independently testable; priority order is the slice order)

### US1 - A fight is a fight (G4, G1, G7, G8) - priority 1
The player attacks "the beast" that exists only in the DM's prose. The target is made real, a conflict starts when
the attack is committed, each exchange the foe acts by its behavior row and the PC's harm is applied by code, the
DM narrates it, and the OFFER reads in the DM's words.
- **Accept**: the fighter save's turns 9-15 replayed on the new code give a `conflict_start`, one foe turn per
  exchange, and no refused `propose_roll`; cases F1-F26, R1-R33, O1-O12 (`cases.md`).

### US2 - The world moves (G2) - priority 1
Ordinary exchanges cost time by the scene's mode; clocks tick and show omens; a lead arrives after the
inconclusive streak; a scene ends when 12.4.2 says so. The DM's "Now:" line moves, so "afternoon at hour 0" cannot
happen unless the DM writes against a plainly stated fact.
- **Accept**: T1-T12, C1-C7; a 20-exchange talk run advances the clock by the scene mode's cost per exchange.

### US3 - The journal shows what you were told (G3) - priority 2
What a person says to the PC is a `said` record, attributed in "what you were told". Nothing becomes a world
fact.
- **Accept**: J1-J14; the talker save's NPC lines appear in `codex` with their speaker.

### US4 - The DM's words about things are backed by the record (G5, G6, G9) - priority 2
Items, presence and pronouns reach the DM as facts; moves go through tools; leaks are measured without name noise.
- **Accept**: I1-I12, Q1-Q14, L1-L6, E1-E8.

### US5 - Saves keep their engine; `/fix` works on either (G10, G11) - priority 1
- **Accept**: S1-S12, X1-X22.

### US6 - The default switch is earned (G12, G13) - priority 1
A second head-to-head, with the seeded NPC scenes, decides. If the gates below hold the default flips; otherwise
the report says which gate failed and the default does not move.

## Functional requirements

- **FR-01** A `propose_roll`, `mood`, `reveal_clue` or `change` argument naming a person or creature that is not an
  entity resolves through one resolver (id, exact name, `mentions.write_mentions`). It never returns "no one on
  record" for a description of someone present. Absent, dead or down entities are still refused (spine).
- **FR-02** When a PC attack on a foe is committed, the conflict starts exactly as in the pipeline (`_attacks`,
  `conflict.start`). Each non-paused exchange while a conflict runs: every able foe takes its beat (`foe_beat`), harm
  is applied by code, `check_end` runs, and a round is advanced (`beat_time`). The RESULT lines reach the player
  through the existing `oof` blocks and the DM through its tool log.
- **FR-03** The foe turn and the world step run **before the DM writes the passage** of the same exchange. A turn
  that paused on an OFFER runs them on the answer turn, after `_resume`. Cost: at most one extra DM call, only when
  the world step produced a fact.
- **FR-04** Each exchange that is not a pure out-of-fiction turn advances time by `clock.beat_cost(mode,
  significant=True)`, marks `beat_end`, and counts dead air (`scenes.note_turn`). An interrupt from `advance_time`
  is a fact for the DM.
- **FR-05** After the time step, code gathers: clock omens (`world_step.clock_omens`), fired triggers
  (`fired_triggers`), a due lead injection (`inject_lead`, written as the pipeline writes it), and a due cut
  (`cut_due`). These are given to the DM as plain facts (what ticked, what arrived, why the scene ended). A cut
  ends the scene and opens the next at the PC's place with no agenda.
- **FR-06** The DM's final answer has a `said` list (person, words). Code writes each as a `said` record with place
  and day; an entry whose speaker is absent, dead or unknown is dropped and logged (spine: presence).
- **FR-07** `new_item` returns, as a fact, any existing item of the same name held by a person here. `give_item`,
  `coin` and the other refusals keep today's rules (item owned; coin from a real source).
- **FR-08** The situation shows, per person here: card (with pronouns), mood, and what they carry; plus a "Not here:"
  line (people the PC has met who are elsewhere or gone, with where). A running fight shows the foes, their
  condition words and the PC's harm state.
- **FR-09** Log-only checks, each reported in `screen.dm_tools` and never blocking: pronoun mismatch on a named
  person's sentence; a named person who is neither here nor in the recent conversation; an item handed over in the
  passage with no change call; the leak overlap (name tokens removed). Each is given a measured precision on the
  labelled sets before any is promoted (DL-12-138).
- **FR-10** The OFFER title is the DM's `goal` words (a short act phrase); the typed change still decides the
  mechanics. The failure cost comes from the DM's `fail_cost` (one of the 9 menu ids) when `frame_check` accepts
  it, else the first acceptable source as today.
- **FR-11** `Game.open` uses the save's stored `engine` and `dm_secrets` (missing means `pipeline` and `hidden`); an
  explicit override is only for a new game.
- **FR-12** `/fix` on a dm-tools game: the Fixer's tools show the turn's DM tool log; a `reframe` of an open OFFER
  uses the code framer; the correction turn is recorded the same way for both engines.
- **FR-13** The DM role is its own `Role.DM` (schema, prompt, packet, offline heuristic, contract test), so the
  offline stand-in and replay run dm-tools turns for real and a per-role model can be configured.
- **FR-14** The default flips only in the last slice; `--engine pipeline` stays.
- **FR-15** `evals/npc_agency.py` runs the 12 cells (+4 repeat probes) on both arms and prints the headline table;
  `evals/h2h_score.py` prints the persona-run headline numbers from the saves.

## Acceptance (owner rule, binding on every phase)

1. Each fix passes **made-up cases** and **deliberate edge cases** plus the **save it came from**, written in
   `cases.md` before the code. Breadth cases are **enumerated from the data** (15 verbs, 10 DM change kinds (11 with the new `fight`), 33
   conditions, 9 cost ids, 6 foe outcomes, 7 cut triggers, 12 mood x cost cells, 4 pronoun sets), never imagined.
2. A **held-out set**, labelled in phase 1 *before any fix and before looking at model answers*, is run only in the
   last phase. No phase tunes on it.
3. Real numbers in each phase's `implementation-results.md`; a fail is reported as a fail.
4. Full `pytest` green; the replay re-recorded if a packet changed (and said so); `ruff check .` and `pyright` clean;
   validator 0/0 if any rule file changed.
5. No new blocking check without a measured precision of at least `pacing.yaml#claim_check.min_precision`.

## Success criteria (the confirming test, last phase; Haiku engine, Sonnet player, `--quick-setup`)

Headline numbers first. The default flips only if **all** hold; each is a number printed by the scoring scripts.

| Gate | Measure | Pass |
|---|---|---|
| C1 cost | tokens in per engine turn, dm-tools / pipeline | at most 0.6 |
| C2 speed | model latency per engine turn, dm-tools / pipeline | at most 0.7 |
| C3 contradictions | hand-counted per the results note's rules, 3 personas x 15 turns | dm-tools at most the pipeline's count |
| C4 `/fix` load | `/fix` reports per run | dm-tools at most the pipeline's |
| C5 pushover | npc_agency: grants above the T-12-19 cell, 12 cells + repeats | at most 5% (OEQ-12-28's own trigger) and not above the pipeline arm |
| C6 mood held | in-character refusals; repeat-ask caving | not worse than the pipeline arm |
| C7 leaks | real secret leaks (names excluded) | 0 |
| C8 fights | foe turns per fight exchange (fighter run) | 1.0 each exchange while a foe is able; 0 prose-only targets refused |
| C9 world | clock hour advances on a 15-turn talker run; journal "told" rows | more than 0; at least one per NPC answer that carried information |
| C10 stability | longhorizon scripted, 60 lines, dm-tools only | 0 engine errors, 0 refused tool calls aimed at prose-only people |
| C11 held-out | the labelled held-out set | at least 80% pass (set in phase 1; not lowered later) |

The pipeline scripted run (46+ minutes) is skipped; C10 is a stability gate, not a comparison.

## Key entities (nothing new in the store)

`said` records (meta `npc.said`), `learned` facts, entities made by `mentions.write_mentions`, the conflict record,
`TurnRecord.screen["dm_tools"]` (grows: `world`, `said`, `told_dropped`, `log_only`), `game_created.config.engine`.

## Assumptions (recorded instead of clarifying; flagged in HANDOFF for the owner)

- A1 **One significant exchange = one beat** of time in the scene's mode (site: one interval; conflict: one round).
- A2 **No Director model call** in dm-tools. Scene cuts are code-only (conflict_end, time_jump, interrupt, place
  change, dead air). `agenda_answered` and `player_cut` have no meaning without an agenda; the DM's `travel` is the
  player's cut.
- A3 The **DM lists what was said** (`said`) rather than code parsing quotations. The DM can omit one; that costs a
  thinner journal, never a wrong fact.
- A4 Prose-only creatures are made as the pipeline makes them (`mind: animal`), not as human walk-ons.
- A5 The confirming run uses **Haiku** as in the first head-to-head. The constitution's Gemini Flash caution
  (VIII, "trust is model-dependent") is a follow-up smoke, not a gate here.
- A6 Pipeline code stays; no deletion of the Reader, Framer model, Director, Checker in this spec.
- A7 Old saves without a stored engine are pipeline saves.
- A8 `/fix` stays a Sonnet Fixer on the shared record; it is not rewritten.
- A9 The gate numbers in C1-C11 are my proposal (owner to confirm; see HANDOFF).

## Out of scope

Spec 029's case-graph routing (wrong-node pointers, self-pointers); a second-model Checker; Gemini Flash validation;
deleting the pipeline; the `ask` listing weakness of the ceiling log (the DM still lists its own `asks`).
