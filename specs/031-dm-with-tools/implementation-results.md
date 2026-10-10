# Spec 031: one DM model with tools (prototype), implementation results

**Status:** the prototype is built behind a flag, and the default engine is untouched. The smoke tests passed with no
crashes. The head-to-head is **not** run here; a separate agent runs it with the commands below.

The plan is `research_notes/Playtest round 2 solutions/EXPERIMENT-DM-WITH-TOOLS.md` (approved 2026-10-10). The
governing rule is constitution VIII: code owns the spine, and the model owns language and judgment.

## What was built

| Piece | Where |
|---|---|
| The engine flag: `GameConfig.engine = "pipeline"` (the default) or `"dm-tools"`. `GameConfig.dm_secrets = "hidden"` (the default) or `"visible"`. | `engine/game.py` |
| Engine selection: `Game._engine()` routes `submit` and `answer` to `engine.dm.dm_tools` or `engine.dm.turn`. The answer to a `/fix` CHOICE always goes to the pipeline. | `engine/game.py` |
| The DM role: one model, a bounded tool loop, then the passage. | `engine/dm/dm_tools.py` (about 800 lines) |
| Harness flags: `playtest.py --dm-engine dm-tools --dm-secrets visible`; `longhorizon.py --engine dm-tools --dm-secrets visible --model claude`. The findings file gains a `turn_costs` row (both engines) and a `dm_tools` row. | `evals/playtest.py`, `evals/longhorizon.py`, `tests/e2e/driver.py` |
| Tests (6) | `tests/engine/test_dm_tools.py` |

### The turn

1. The input is stored verbatim (T1). One store transaction is opened.
2. An open OFFER plus new words: the OFFER is withdrawn by default (12.2.6, `close_by_default`), and the DM is told.
3. With no scene open, code opens one at the PC's place. There is no Director and no agenda.
4. The DM loop runs: at most **6 tool calls** per turn, **3 per answer**. The answer that has no calls is the passage.
   The DM sees:
   - the situation: the time, the place, the PC's people card, sheet and items, and who is here (the people card,
     plus the mood when it is already rolled);
   - the exits, the open threads and the scene;
   - the last 6 exchanges and the player's message;
   - the tool results so far.
5. A `propose_roll` that needs a roll opens the code-rendered **OFFER** and stops the loop. The passage is the lead-up
   only. The next `game.answer(...)` resolves the roll with code (`resolve()`: the roll, the near miss, the cost, the
   harm). The DM then narrates the result. A near miss or last chance shows its menu first.
6. After the loop:
   - the scene follows the PC: a PC whose place differs from the scene's gets a new scene;
   - the turn-end harm steps run (dying, waking, Threshold);
   - the leak audit runs;
   - the RESULT, OFFER and NOTE blocks are rendered by the existing `turn_blocks`.
7. The `TurnRecord.screen["dm_tools"]` record stores, per turn:
   - tool calls with their arguments and outputs;
   - DM steps, model calls, tokens and latency;
   - refusals and rolls;
   - moods and ceilings, asks and ceiling violations;
   - clues and leaks.

### Tools

| Tool | What code does (reused) |
|---|---|
| `propose_roll` | The DM gives a goal, verb, target, method, attribute, difficulty, why the outcome is uncertain, the stakes, a nonlethal flag and the typed change. Code builds a `Beat` and runs `resolve/pipeline.run_beats`, which covers the gate, necessity (01.4.1), take-the-time (01.4.4), the frame, the OFFER, the auto-roll for Safe, harm and the change. The **Framer model is replaced by a code framer**: `roles/framer.default_frame`, adjusted by the DM's attribute, difficulty tier and stakes. For stakes, it picks the first 01.6.9 stakes source that `frame_check` accepts; a fight risks harm first and a sneak risks being noticed. With nothing at stake, there's no roll. |
| `state` | The PC's sheet, items and conditions (`fixer.sheet_line`), an entity (`fixer._entity_tool`: card plus visible facts), "here", and the time. |
| `change` | `coin`, `give_item`, `new_item`, `condition_add` / `condition_remove` (`store/conditions`), `npc_leaves`, `new_npc` (`social.meet_npc`), `travel` (`places.move` plus a new scene), `rest` (`turn._rest`, PR-07-8) and `fact`. It **refuses only** these: an unknown entity; someone dead, down or not here acting; an item the giver doesn't hold; coin from no source; a payer without the coin. The refusal comes back as `REFUSED: <reason>`. An NPC with no purse on record pays "from their own means". |
| `recall` | `fixer._search_tool` (past turns and record facts), `fixer._said_tool` (testimony), `codex.what_you_know`. |
| `reveal_clue` | Spec 029's `answer.clue_judgment` (one CLUE call) and `answer._from_case`. Returns the clue to deliver (written as a learned fact), a pointer to the holder, or nothing. |
| `mood` | `answer.willingness`: rolled once per scene and held (D3), mapped willing to open, guarded to guarded, unwilling to closed. The T-12-19 cell comes from `oracles.yaml#tbl.npc_ceiling`. Both are given as facts. The final answer's `asks` list is compared with the ceiling, and a grant above the cell is **logged** as a violation, never blocked. |

**The secrets arm.** `dm_secrets=visible` adds `PRIVATE` lines under each present person:
- the unfound case nodes whose placement they hold (the full fact);
- whether they are a case's subject.

The default is hidden. In both arms, a passage that repeats at least 60% of a secret's content words, when no clue
tool delivered it, is logged as a leak.

**Kept:** the store and events, the dice, OFFER and RESULT rendering, `/fix`, the seed, casting, creation, the
opening, advancement and endings.

**Bypassed in this engine (not deleted):**
- the Reader, the Framer model, the Director (except the opening, which is unchanged), World and the Checker;
- narrator record lines, `npc_layer` and the answer ladder.

**DM model calls are logged under `Role.NARRATOR`.** A new `Role.DM` would need a schema, prompt, packet and offline
heuristic for each role in the contract tests. Add it if the design is kept.

## Gates

1. **The suite:** **2032 passed, 4 skipped** (the baseline before this work was 2026 passed, 4 skipped; the new tests
   add 6). The default engine is unchanged: `GameConfig().engine == "pipeline"`. The long-horizon baseline test is
   untouched, because the header is unchanged for the pipeline.
2. **New tests** (`tests/engine/test_dm_tools.py`):
   - the spine refusals: coin from no source, overspending, an unknown item, an item not owned, and a dead NPC paying,
     leaving or answering;
   - the OFFER pause round trip (OFFER, commit, near miss if rolled, DM narration, `frame_resolved`);
   - `reveal_clue` delivers a held clue, and the PC's knowledge is written;
   - the secrets arm (hidden by default, visible lines, a leak logged);
   - the OFFER title comes from the DM's words, never "here";
   - the default engine.
3. **Smoke tests:** Haiku engine, Sonnet player, `--quick-setup`, 10 play inputs each. All runs exited 0, with no
   leaked errors, no model-call failures and no repeated output. Runs 1 and 2 drove fixes, so run 3 of the fighter is
   on the final code.

### DM turns only (`screen.dm_tools`; the opening and `/fix` turns excluded)

| Run | DM turns | Model calls/turn | DM steps/turn | Tool calls/turn | Tokens in/turn | Tokens out/turn | Latency/turn (mean, max) |
|---|---|---|---|---|---|---|---|
| talker 1 (144920) | 9 | 3.0 | 2.1 | 1.7 | 17.9k | 2.6k | 20.8 s, 30.1 s |
| talker 2 (145813) | 9 | 2.8 | 2.0 | 1.7 | 16.7k | 2.7k | 21.5 s, 29.8 s |
| fighter 1 (145151) | 9 | 1.7 | 1.4 | 1.0 | 13.7k | 1.8k | 13.3 s, 27.4 s |
| fighter 2 (145810) | 8 | 1.1 | 1.0 | 0.8 | 8.7k | 1.2k | 8.8 s, 16.1 s |
| fighter 3 (150606, final code) | 10 | 1.1 | 1.0 | 0.7 | 11.2k | 1.4k | 10.6 s, 27.2 s |

- Model calls include the CLUE judgment, which `reveal_clue` makes.
- Answer turns (`commit`, `go_big`, a near-miss pick) make 0 or 1 call.
- Tokens in count all input, cache creation and cache reads included. The harness counts tokens this way for both
  engines from now on.

### Every turn with a model call (`turn_costs`; the same measure for both engines)

The talker runs averaged 3.2 and 2.9 calls/turn, and 27.5 s and 25.9 s/turn. The fighter runs averaged 2.4, 2.3 and
1.9 calls/turn, and 25.0, 20.7 and 24.7 s/turn. These include the pipeline opening and the Sonnet `/fix` turns.

**Indicative only:** the round-9 pipeline saves (013206 talker, 013226 fighter, 013246 explorer), on the same
measure, averaged 3.2–3.4 calls/turn and 34–45 s/turn. Their tokens-in figures are not comparable, because they did
not count cache creation. The head-to-head is the real comparison.

### Tool use (all five runs)

| Tool | Calls |
|---|---|
| `reveal_clue` | 22 |
| `mood` | 15 |
| `propose_roll` | 9 |
| `change` | 6 (travel ×3, new item ×2, fact ×1) |
| `state` | 0 |
| `recall` | 0 |

- **Refusals:** 2, both in fighter 3. Both were a `propose_roll` aimed at a person who existed only in prose ("the
  child's father"). The DM re-proposed in the same turn.
- **Ceiling violations:** 1 of 23 asks logged. An open person, a real cost: the cell was "price" and the DM granted
  "help".
- **Leaks:** 0 in the hidden arm, after one false positive was fixed. The audit flagged a subject the PC had already
  learned.

### What went wrong in play (brief)

- **talker 1:** good voices, and the player's notes praised the dialogue. One `/fix` came from spec 029's case graph,
  not the DM. The traveler was the case subject, yet `_from_case` had them point to Dunda for "who leads the refugees"
  (themselves), and the DM delivered that pointer faithfully. Pointers read as dodges ("Erurion dodged ... pointed to a
  new place").
- **fighter 1:** a bout "to yield" killed the opponent on a go-big critical, because harm is lethal unless the words
  say otherwise. A `/fix` repaired it. **Fixed:** a `nonlethal` flag on `propose_roll`. In the same run, the OFFER
  for a duel risked "you are noticed". **Fixed:** a fight risks harm first.
- **fighter 2:** the OFFER titles read "Learn about the gate" and "Go to the gate" for actions past the gate. A
  proposal that named no target defaulted to the scene's place (`typed_goal`). This caused two `/fix` reports.
  **Fixed:** the goal comes from the DM's `change_what` or goal words. "(nonlethal)" also showed in an OFFER title.
  **Fixed:** it now marks the method only.
- **talker 2:** one self-contradiction in a passage: a cloth handed over while "still at the stall". This is a model
  writing slip. Murzza deflected repeatedly, and the player found it "slightly repetitive".
- **fighter 3:** the player's notes were mostly positive. Remaining oddities:
  - "Learn from the traveler" titled an accusation (a typed `learn` goal);
  - "Hold the fight at the gate" titled a punch at a prose-only person;
  - a steep odds drop after a wound was not explained.

## Known gaps (prototype)

- **People who exist only in prose** aren't entities until the DM calls `change new_npc`, so the spine can't target
  them. Two refusals came from this.
- **The OFFER title is the typed goal (code).** It reads oddly when the DM's `change_kind` or `change_what` are thin.
  The title could show the DM's `goal` instead, but that would change `oof.goal_line`, which the pipeline shares.
- **No time passes on ordinary turns.** Only travel, rest, take-the-time and harm advance time. There is no world
  step, no clocks ticking from the world, no lead injection, no scene agenda or cut logic, and no dead-air cuts (no
  Director).
- **Pointers from the case graph are delivered as "Deliver: X doesn't know, but Y would"**, which can read as
  dodging. Spec 029's self-pointer (the subject pointing away from themselves) shows up here.
- **The secrets arm is not exercised live yet.** The head-to-head runs it. Leak detection is a word-overlap heuristic
  (at least 60% of content words, secrets of at least 3 words), so it can miss paraphrases.
- **The ceiling check depends on the DM listing `asks`.** An unlisted grant isn't counted.
- **`state` and `recall` were never called.** The situation block may already be enough, or the DM may be
  under-using memory over long runs. The long-horizon lines will show which.
- **`Game.open` uses the config it is given.** The CLI's default config resumes a dm-tools save on the pipeline. The
  harnesses pass the flag every time.
- **The offline stand-in has no DM heuristic.** Offline dm-tools runs (the long-horizon `--model offline`) give canned
  passages: plumbing only.
- **The pipeline-specific long-horizon measures don't apply to dm-tools turns.** These are the narration loop, claim
  log, learning beats and NPC lines. Compare on `turn_costs`, the `dm_tools` row, player notes, `/fix` counts and the
  experiment's measures.

## Commands for the head-to-head

Run from the repo root with `PYTHONUTF8=1`. Each persona runs once per arm; add `--turns 15` per the plan. The
pipeline arm leaves `--dm-engine` at its default.

```
# arm 1: the current pipeline
py -3.12 evals/playtest.py --engine claude --player claude --engine-model haiku --persona talker --turns 15 --quick-setup
# arm 2: DM with tools, secrets hidden
py -3.12 evals/playtest.py --engine claude --player claude --engine-model haiku --persona talker --turns 15 --quick-setup --dm-engine dm-tools
# arm 3: DM with tools, NPCs' private knowledge visible
py -3.12 evals/playtest.py --engine claude --player claude --engine-model haiku --persona talker --turns 15 --quick-setup --dm-engine dm-tools --dm-secrets visible
#   (repeat with --persona fighter and --persona explorer)

# scripted long-horizon lines through either engine (--model claude: every role on Haiku; offline = plumbing only)
py -3.12 evals/longhorizon.py --mode scripted --lines 60 --model claude
py -3.12 evals/longhorizon.py --mode scripted --lines 60 --model claude --engine dm-tools
py -3.12 evals/longhorizon.py --mode scripted --lines 60 --model claude --engine dm-tools --dm-secrets visible
```

**Outputs:** `evals/playtests/<stamp>-claude-<persona>[-dm-tools[-secrets]].md` and `.findings.jsonl`. Read these
rows: `turn_costs` (both arms), `dm_tools` (refusals, ceiling violations, leaks, clues, rolls, asks) and
`player_note`. Each save is `saves/playtest-<stamp>-<persona>[-dm-tools[-secrets]].db`, and its `turns.record`
holds `screen.dm_tools` per turn.

The seeded NPC scenes in `evals/npc_agency.py` (spec 028) are not in this branch. Spec 028 has not merged.
