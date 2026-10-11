# Plan 032: dm-tools as the MVP engine

Read `spec.md` first (gaps G1-G13, FR-01..15, the gates). This file says where each piece goes and what it reuses.
Everything is a change to `engine/dm/dm_tools.py` (877 lines), one new module, and small edits elsewhere. Nothing in
the pipeline is deleted.

## Reuse map (find it, do not rebuild)

| Need | Existing piece (verified in the code) |
|---|---|
| Foe strikes, band moves, break free, stand | `world_step.foes_act`, `_foe_turn`, `conflict.foe_beat`, `check_end`, `able` |
| Fight start on a committed PC attack | `pipeline._attacks` + `conflict.start` (already runs inside `run_beats`; needs an entity target) |
| Hostile NPC starts a fight | `npc_layer.respond` row-1 path: `conflict.start(...)` then `_foe_turn` |
| Time per exchange, round, interrupt | `clock.beat_cost`, `scheduler.advance_time`, `world_step.beat_time` |
| Clock omens, fired triggers, exits/warnings | `world_step.clock_omens`, `fired_triggers`, `deliver_warnings` |
| Lead injection | `pacing.inject_lead` (code only), raised by `pacing.inconclusive_streak` at `beat_end` |
| Scene cut test, dead air | `scenes.cut_due`, `note_turn`, `note_cut`, `end_scene`, `start_scene` |
| People/creatures from prose | `mentions.write_mentions` (creature: `mind: animal`), `social.cast_described` (existing-or-group-or-walk-on) |
| Testimony records | `testimony.add_said` (+ `is_repeat`); journal `codex._told/_told_lines` already render them |
| Cards, pronouns | `packet.people_card`, `pronoun_words`; `audit.claims._pronoun_hit` (log-only use) |
| Cost menu validation | `frame.frame_check`, `roles/framer.default_frame/to_proposed`, `sctx.stakes_menus` |
| `/fix` | `dispute.settle_dispute`, `fixer.investigate`, `dispute.reframe` (uses `turn._env`) |
| Engine stored in the save | `game_created.config` (written by `Store.create(config=config.model_dump())`) |
| NPC-agency harness | `git show 3e94efe:evals/npc_agency.py` (404 lines) and `evals/baselines/npc_agency_round8.json` |

## The new turn (changes in bold)

```
store input (T1) -> [answer turn: _resume the OFFER] -> **world step if the exchange is complete (below)**
-> DM loop (tools, up to 6) -> **if the DM wrote a passage without calling tools, run the world step; if it
produced a fact, one more DM call writes the final passage with those facts** -> sync scene -> turn end (dying/wake)
-> **told records (said), log-only audits** -> render blocks (RESULT/OFFER/NOTE) -> save TurnRecord
```

"Complete exchange" = no open pause after the DM loop (an OFFER pause skips the world step, as in the pipeline,
`turn.py:196`). On the answer turn the world step runs right after `_resume`/`_harm_followups`, before the DM loop, so
the DM narrates the roll's result and the foe's reply in one passage.

### G1/G2/G5-world: `engine/dm/dm_world.py` (new, about 150 lines, lane W)

```python
def world_step(ctx, t, *, message) -> list[str]:   # facts for the DM, in plain words
    foes  = world_step.foes_act(ctx, rec, oof)      # reuses the pipeline's foe turn; RESULT lines go to oof
    time  = _exchange_time(ctx, rec, fought=bool(foes))   # beat_cost(mode) + beat_end + note_turn(quiet)
    omens = world_step.clock_omens / fired_triggers # record.omens, record.triggers
    lead  = inject_lead(tctx) if trigger_raised(st, "trg.lead_injection")
    cut   = scenes.cut_due(st, rules) in {time_jump, interrupt, conflict_end, dead_air}  # code only
    return facts   # "The beast strikes you and lands it: you are bloodied (Vitality 4 -> 1)." / "An hour passes." / ...
```

Not reused on purpose (they give orders or call models): `npcs_respond`/`npc_layer.respond` (table rows tell NPCs how
to act), `deliver_learning` (Reader parts), the Director model. The DM sees outcomes, not instructions.

- **Order of facts** matches `world_step.world_step`: foes, round/time, omens, triggers, lead.
- **Scene mode (trace first):** `_open_scene` takes `clock.mode_of(state.time.mode)`; the store's default `scene`
  reads as `free`, and `beat_cost(free)` is 0, which alone would keep the clock at hour 0. The phase traces what mode
  the pipeline's Director gives a place scene and gives dm-tools scenes `site` (conflict while a fight runs,
  `travel` while travelling). Assumption A1 holds only if that trace agrees.
- **Cut:** `end_scene(reason)` then the existing `_open_scene` next turn. Moods are held per scene, so a cut re-rolls
  `mood`. No agenda is written. The DM is told the reason as a fact ("The scene changed: time passed").
- **Cost:** in a fight one extra DM call per exchange (the re-ask). Outside a fight, none unless a fact was produced.

### G4: the resolver (lane T, `dm_tools.py`)

`_id()` becomes `_party(ctx, t, raw, *, make=True)`: id -> exact name -> alias/role match (`mentions.find_existing`)
-> `mentions.write_mentions([Mention(name=raw, kind="npc"|creature)])` at the scene's place. Used by `_propose_roll`
(target, change_what, change_whom), `_mood`, `_reveal_clue`, `_change` (who/to). The creature test is
`npc_layer.is_animal`-style (the ANIMAL words) on the DM's noun phrase; a person is a walk-on with that role
(`cast_described`). The `propose_roll` refusal text for a target that is not here stays (spine). New `change
kind=fight` (who) for an NPC the DM has turn on the PC: `conflict.start(tctx, pc, [who], "the DM: X attacks")`
then the foe turn runs in the world step, so "nothing done to the PC without a roll" holds.

### G7: dead-end fix (no regex)

1. The foe is real (G4) so `conflict_start` fires. 2. The situation shows a fight block (below). 3. One sentence in
the prompt, as judgment guidance not an order about reactions: "Whatever the player declares in this message is
attempted in this turn. If it is uncertain and costly, propose the roll now and write only the lead-up; do not end
the passage on a chance still to come." 4. The measure is k/5 Haiku samples on the turn-11 context plus the
held-out fight items; no blocking check.

### G3: told records

Final-answer schema gains `said: [{npc, words}]` (max 6; verbatim from the passage; only what a person said to the
PC). `_told(ctx, t, said)` drops entries whose speaker is not an entity here and alive (spine) and calls
`testimony.add_said` with `question` unset. `situation()` never shows them back (the DM already has the
conversation); `recall` does (`_said_tool`). One extra output line per speaking NPC; no extra call.

### G5/G6/G9: context and log-only checks (lane C)

- `situation()`: per person here add `carries:`; add `Not here:` (people the PC met whose position is elsewhere or
  who are dead/gone, with place); add a `FIGHT` block when `conflict.active`: foes (name, pronouns, `state_words`),
  bands, the PC's harm state. These are facts. Keep the whole block under the current size (the situation is the
  main token cost; measure tokens before and after).
- `_new_item` echoes an existing same-named item held by a person here (a fact in the tool result).
- Log-only (in `screen.dm_tools.log_only`, each with `kind`, `text`): `pronoun` (via `_pronoun_hit` on the
  passage, not the pipeline's claim machinery), `absent_named`, `item_unbacked`. Precision is measured by hand on the
  labelled set in the phase; none blocks. A check that measures at or above `min_precision` is promoted in a later
  spec, not here.
- Leak audit: `_content()` drops every entity name token (all entities, display name and aliases) before the overlap.

### G8: OFFER words

`propose_roll` schema: `goal` = "the act in your own short words" (already free text), new `fail_cost`
(enum of the 9 `cost.*` ids, optional). `code_framer` uses `fail_cost` as the threatened cost when `frame_check`
accepts it, else today's `PREFERRED_COST` fallback. `Beat` gains an optional `title`; `oof.goal_line` returns it when
set (pipeline beats never set it, so the pipeline's titles do not change; replay unaffected). The `(nonlethal)`
marker stays in `method` only.

### G10: engine in the save

`Game.open`: `stored = created.payload.config`; `engine = stored.get("engine", "pipeline")`,
`dm_secrets = stored.get("dm_secrets", "hidden")` override the caller's config. `Game.new` stores what it was given.
`play/cli.py` gets `--engine` (new game only). **Trap:** when the default flips, an old save without the key must
read `pipeline`, so the code must not rely on `GameConfig`'s default when reading a store.

### G11: `/fix`

Findings to confirm in the phase (trace first): `Game._dispute -> turn.play_dispute -> _turn(dispute=True)` is
already engine-independent (no Reader), then `narrate_turn` (a Narrator call) writes the answer. What is pipeline-only:
`dispute.reframe` builds `turn._env(tc)` with the Framer model; the Fixer's `preview` and turn views read Reader
parts/beats, which a dm-tools turn does not have; the DM's tool log sits in `TurnRecord.screen["dm_tools"]`.
**Smallest correct way:** (1) Fixer tools (`fixer._search_tool`, the turn view) include the turn's `dm_tools.tools`
(tool, args, result) as evidence; (2) `dispute.reframe` takes the env from a hook: `dm_tools.code_framer` when
`engine == dm-tools`; (3) the dispute turn's `TurnRecord` carries `screen["dm_tools"] = {"fix": true}` so the harness
counts it; (4) the next DM turn sees the correction in the recent conversation and the Now line. No second `/fix`
implementation. If the trace shows the narration of the `/fix` answer needs Reader state, fall back to rendering the
answer from the found/did/Now blocks (`dispute` already produces them) without a Narrator call.

### G12/FR-13: Role.DM and the default

`Role.DM` in `engine/llm/base.py` plus `engine/game.py` `ROLE_IDS` (per-role model config for free), `schemas.py`
(`step_schema` is already the schema; register it as the DM role's), a `prompts/dm.md` (the PROMPT text moves out of
the code), `packet.py` (the DM packet = the current `_message`), and an offline heuristic in `llm/offline.py` that
takes a scripted plan (so offline e2e and the replay games run dm-tools turns). Contract tests
(`tests/contract/test_schemas.py`) gain the role. The calls move from `Role.NARRATOR` to `Role.DM`; every harness that
reads `role='narrator'` for dm-tools (xstats, h2h_score) is updated. The recorded replay games are pipeline-only and stay; one dm-tools
game is recorded for replay at the end of this phase (and re-recorded by any later phase that changes a DM packet).

The default flips in the last phase: `GameConfig.engine = "dm-tools"`; tests that rely on the pipeline default
(`tests/engine/test_game.py`, `tests/e2e/`, `tests/replay/`) get `engine="pipeline"` explicitly where they test the
pipeline, or run through the offline DM heuristic where they test the game.

### G13: the harness (lane E)

`evals/npc_agency.py` ported from `3e94efe` with: arm `dm-tools` (real `dm_tools.play_turn` on the dock fixture, the
DM on Haiku through `ask_claude`, mood pinned by `meta MOOD` as in the file) and arm `pipeline` (the file's `old` arm:
mood pinned through standing). The `ceiling`/`judgment` arms and the `ceiling_lines` config belong to unmerged spec
028 and are dropped. Judge, `violates`, `leaked`, `summarize`, `voice_distinctness` stay as written. The baseline JSON
is copied as is. `evals/h2h_score.py` (new, about 120 lines) reads the saves and prints the headline table: engine
turns, calls, tokens in/out, latency, `/fix` count, refusals, ceiling violations, leaks, told rows, hours advanced,
foe turns; and the 3-persona pairing. Hand-counted contradictions stay a human step with the results note's rules.

## Risks and how the plan answers them

| Risk | Answer |
|---|---|
| The re-ask after the world step doubles calls in fights | only in fights and only when a fact exists; measured in C1/C2 |
| `free` scene mode keeps the clock still | trace in phase 4; scenes default to `site` |
| A foe killing the PC through code violates "nothing without a roll"? | `foe_beat` is a d20 vs Guard roll with harm by `apply_harm` (INV-2); the lethal warning (`deliver_warnings`) and Threshold rules are reused unchanged |
| `said` costs output tokens | cap 6 entries, measured in C1 |
| Name-token removal hides real leaks | L2/L3 and the labelled set measure it; the audit stays log-only |
| Flip breaks tests that assume the pipeline default | the flip is the last task; the suite runs both ways before it lands |
| Replay fixtures | dm-tools packets change in phases 2-5; re-record at the end of each phase that changes a packet, and say so |

## Analysis (cross-artifact pass)

**Coverage.** FR-01 P3 R1-R33 | FR-02/03 P4 F1-F26 | FR-04/05 P4 T1-T12 C1-C7 | FR-06 P5 J1-J14 | FR-07 P3 I1-I11 |
FR-08 P4 (FIGHT block) + P5 (carries, Not here) Q1-Q8 | FR-09 P5 Q9-Q14 I12 L1-L6 | FR-10 P3 O1-O12 | FR-11 P2 S1-S12 |
FR-12 P6 X1-X22 | FR-13 P2 | FR-14 P7 | FR-15 P1/P7 N1-N16. Every gate C1-C11 has a producer (h2h_score, npc_agency,
longhorizon, heldout). No orphan tasks.

**Fixed in this pass.** Case series `P` renamed `Q` (clashed with phase names); stale case ranges in the spec aligned; the
replay sentence corrected (recorded games are pipeline-only); the change-kinds count includes `fight` (11).

**Unverified in this slice (each phase traces first; none is asserted as fact).**
1. Scene mode: `_open_scene` reads `clock.mode_of(state.time.mode)`; the store default reads as `free`, where `beat_cost`
   is 0. Whether the pipeline's Director gives place scenes `site` is untraced (P4.1).
2. Whether the DM can add `wound_*`/`unconscious` today (P3.4); the harm-ladder names in F7-F10.
3. What the Fixer's turn view and `dispute.preview` read from a dm-tools `TurnRecord` (P6.1); G11 is a hypothesis with a fallback.
4. Where role prompts live for `Role.DM` (P2.1).
5. The `pipeline` arm of `npc_agency` is the file's `old` arm; the `ceiling` arm needs spec 028's schema (not merged). If
   the arm does not run on this Reader schema, P1 records it and C5 uses dm-tools alone against the 5% trigger.
6. Whether a talk-only exchange counts as inconclusive for `inconclusive_streak` (it keys on written events); if not,
   record it as a known gap rather than adding machinery (P4.2).

**Risks.** The re-ask after the world step may fight the pause/answer ordering (escalate P4 to Opus if so). Token growth
from `carries:`, `Not here:`, FIGHT and `said` (P5 ceiling +10% over P4). C3 is hand-counted: same rules, same counter,
3 saves per arm. Samples are small; the report claims no more than the gates.
