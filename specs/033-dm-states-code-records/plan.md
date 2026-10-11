# Plan 033: the DM states, code records

Spec: `spec.md` (R1-R13, assumptions A1-A11). Cases: `cases.md`. Tasks: `tasks.md`. Prompt draft: `contracts/dm.md.draft`.

## 1. Shape

One mechanism carries most of it: **`Beat.stated`** (`engine/resolve/types.py`), a small pydantic model filled by
`dm_tools._propose_roll` from the DM's fields. When `beat.stated` is set (dm-tools), every guessing helper on the
resolve path is skipped and the stated value is used; when it is None (the pipeline) nothing changes (R13). No
`engine` flag is threaded anywhere else: the beat carries its own provenance.

```
Stated: reads: bool = False · approach: str = "plain" · force: "push"|"prone"|None · weapon: str|None
        nonlethal: bool = False · fail_on: str|None · position: tuple[mover, band, other] | None
```

The rest is the dm-tools turn itself: the step's `foes` and `cost_form` fields, `change position`, the `as`/`name`/
`knows` fields, `end_game`, and the world step telling (not doing) leads and witnesses.

## 2. The DM-facing contract

Every field is optional unless the "Omitted" column says REFUSED. A refusal lists the legal options and uses 032's
one-revision rule (a second breach of the same tool is dropped and logged).

| Where | Field | Values | Omitted | Code does (exactly) |
|---|---|---|---|---|
| any id slot (`target`, `who`, `to`, `npc`, `said.npc`, `foes.foe/target`) | | an id; `"pc"`; or a recorded name, exactly | | id, or exact case-insensitive equality with one unsealed recorded name; else words (below) |
| `propose_roll`, `change`, `said[]` | `as` | `he`, `she`, `they`, `creature`, `thing` | `they` for a person-only slot (data `target_kinds`), else `thing` | words not on record: person = walk-on with those pronouns (name rolled); creature = `mind: animal`, "it"; thing = the act is on the words, no entity |
| `propose_roll` | `change_kind=move_to`, `change_what`=band, `change_whom` | band: engaged, close, near, far, distant | mover = the actor | on success (incl. at a cost) writes that band between mover and the other party; failure moves no one |
| `propose_roll` | `change_kind=restrain` | | no hold | 06.5.2 ladder at the delivered reach; an untyped Grapple holds no one |
| `propose_roll` | `force` | `push`, `prone` | REFUSED for `verb.force` | 06.5.3 ladder: reach 1 off balance; 2 push one band or prone; 3 two bands, or prone and off balance |
| `propose_roll` | `weapon` | an item id the actor holds, `unarmed` | the item recorded in hand (`wields` fact), else unarmed | 06.4.4 weight from the item's tags; never from words |
| `propose_roll` | `nonlethal` | bool | false (06.4.8) | harm mode of a landed Strike |
| `propose_roll` | `reads` | bool | false | 02.4.6: letters needed once literacy is on record (G2/G3), `cannot_read` by tongue, plain reading of words on record = no roll |
| `propose_roll` | `approach` | `plain` or one verb `excludes` entry (13 strings from data) | `plain` | 00.12.3: excluded method needs a licence in its `covered_by`; held = G2, else G3 redirect |
| `propose_roll` | `fail_on` | an id | REFUSED for exposure, gear, closed_door when no structural source exists (a listening clock; the beat's target for closed_door) | exposure: that observer's alertness; gear: that item; closed_door: that person |
| `propose_roll` | `fail_cost` | a cost id or none | none: the fallback list (`verb_costs`, DL-01-54) minus costs that need `fail_on` | as 032 P8b |
| step | `foes[]` | `{foe, act, target, nonlethal}`; act: strike, close_in, withdraw, stand, break_free, grapple, flee, yield, wait | target = pc; nonlethal false; an able foe missing = one re-ask, then it waits (logged) | legality from state, d20 vs defense, `apply_harm`, hold ladder; an act made illegal by the PC's result lapses with its reason |
| step | `cost_form` | one option id from the COST TO SHAPE line | one re-ask (with any missing foes), then nothing structural (logged) | the 01.13.7 row's option, written exactly |
| `change position` | `who`, `to`, `what` | `to` a band (then `what` = the other party) or a place id here | `who` = pc | writes it; a PC to another place is REFUSED (use travel) |
| `change fight` | `to` | a band | REFUSED (06.3.9's default retired for dm-tools) | starts the conflict at that band; the only fight start |
| `change npc_leaves` | `to` | a place id, or empty | elsewhere, unrecorded | position (no "first reachable place") |
| `change new_npc` | `what`, `name`, `as`, `knows` | role words; a proper name; pronouns/kind; a clue node id | unnamed; they; none | walk-on (never reuses anyone); `knows` places that node's reserve on it |
| `change new_item` | `knows` | a clue node id | none | a document placement of that node |
| tool | `end_game` | `why` | | opens the retire confirmation (11.13.1) |
| `said[]` | `npc`, `words`, `as` | | they | recorded as given; dropped only if the speaker is dead, gone or not here |

Removed from the contract: `_VERB_GOAL` goal defaults; `you`/`the player` as the PC; capitals as names; head nouns
as creatures; `(nonlethal)` appended to the method.

### Prompt budget
`contracts/dm.md.draft` is 786 words (now 798; budget 800). Trims that pay for the new lines: the intro (-30), the
propose_roll paragraph rewritten around the fields (-40), the target example strings (-25), mood and end_scene (-20),
the world paragraph (-15), the "declares" paragraph cut to one sentence (-25). The schema carries the enums; the prompt
names each field once.

## 3. Design per requirement

**R1 positions (P2a).** In `pipeline._finish`, when `beat.stated` is set: `_moved` and `_contact` are not called;
`_stated_position(env, frame, delivered)` writes `stated.position` on success, and Force's ladder writes push bands
or `cond.prone` per `stated.force`. A Strike, Grapple or Force aimed at a target with a recorded band other than
engaged is refused at `_propose_roll` (P4; 06.4.3 "Move first"; 06.5.2 needs engaged); with no band recorded the act goes
ahead and no band is written. `change.apply_change` skips the untyped-Grapple-to-restrain line and `_person`'s name
resolution when stated. `_cleanse` drops `_FREEING`: aimed = target is none, the actor or the holder, or
`change_kind=free`. `dm_tools` stops using `change._VERB_GOAL`.

**R2 fight start (P2a).** `pipeline._roll` does not call `conflict.start` when stated. `dm_tools._fight` (P4) requires
`to` and passes it.

**R3 foes (P3).** New `engine/resolve/foe_act.py`: `legal_acts(st, foe, pc) -> list[str]` (state only: prone ->
stand; held -> break_free only while pinned, else also strike/grapple per T-06-10; engaged -> strike, grapple,
withdraw; not engaged -> close_in; always flee, yield, wait) and `foe_act(tctx, rng, foe, act, target, nonlethal)`
reusing `foe_beat`'s pieces (`_break_free`, stand, band step, the d20-vs-Guard strike with `_line`, `apply_harm`,
`effective` lethal) plus grapple (d20 + atk vs the target's Might defense; success = reach 2, critical = 3, then
`change.hold`), flee (band distant, then off-scene; leaves the conflict, 06.11.5) and yield (`defeated` manner
yielded; `able` false). `dm_world.world_step` runs the turn's foe picks instead of `ws.foes_act`, then `check_end`.
Picks come from the last DM step that gave `foes`; with a `propose_roll` that paused, they are stored in the pause's
`detail["foes"]` and run on the answer turn. The FIGHT block lists each foe: id, band, conditions, state words, and its
legal acts now. `conflict.foe_beat` and `world_step.foes_act` stay for the pipeline.

**R4 leads and witnesses (P5).** `pacing.lead_candidates(state) -> dict` (the PR-12-3 ladder's sources, read-only, no
rng) feeds `dm_world._lead`: "A lead is due (the player seems stuck). Open threads: ... Sources on record: ...
Bring one in if it fits." Then the trigger is lowered and the streak reset (`inject_lead`'s bookkeeping half,
factored out). No threads: "no open thread is on record". `gen/case.short_of_sources(state)` (read-only half of
`audit_cases`) feeds one WITNESS NEEDED line per node (once, meta flag `told_short`), with the node id; the h15 hook
skips `audit_cases` under dm-tools. `gen/case.place_on(tx, node_id, holder)` places the node's reserve on the DM's
entity (P4 wires it into `new_npc`/`new_item knows`).

**R5 penalty details (P2a, P3).** `pipeline._consequence` builds cost params from `stated.fail_on` instead of
`_cost_params` when stated. `costs._apply` for `cost.footing` with no form and a stated beat returns the deferred
options (never the first); `costs.footing_options(state, frame, sev) -> list[Option]` lists only what can land, and
`costs.apply_footing(tx, pending, option)` writes it. `conflict.strike_harm(..., weapon=, mode=)` takes the stated
weapon and mode; `conflict.weapon_of(rules, st, item_id)` replaces the word path when stated. The DM is shown
COST TO SHAPE on the answer turn; its `cost_form` is applied (P3).

**R6 identity (P4).** `_id`: exact id or exact name equality (kept). `_party`: `"pc"` literal; words not on record
use `as` (default by slot from data `target_kinds`); no `ANIMAL`, `_NAME`, `bare`, `find_existing`,
`write_mentions`. `_walk_on(ctx, words, place, as_, name)`: creature = today's animal record without the head-noun
test; person = `social.meet_npc(..., reuse=False, pronouns=, name=)`. `target_kinds` reads the new data field, not
`_PERSON_KIND`/`_THING_KIND` over rule prose (D24). The new_item twin advice uses exact name equality.

**R7 beat-text decisions (P2b).** `gate.check_gate`: when stated, `reading = stated.reads`, the exclusion is the
`stated.approach` entry (exact string), the would-be licence is its `covered_by`; `excluded_by`, `excluded_anywhere`,
`would_be_license`, `_tongue`, `reads_writing` not called. `necessity`: `plain_reading` uses `stated.reads`.
`frame.lift_or_carry`: the take branch only (structural); `lift_attribute` keeps best odds and the DM's attribute,
skipping the rubric's words. `frame.reverses`: the structural branch, plus `resolution.yaml#reverses_goal` (kind ->
cost ids/forms, from rules phase R); the word patterns are not used when stated. `_fitted` is a no-op for stated
beats (forms are ids). The cost-reversal "field" is not needed: the table over ids decides it (smallest set).

**R8 testimony (P4).** `_told`: speaker by `_id`, else a walk-on with `as` (default they); drop only if `_acting`
says dead, gone or not here. No `covers`, `is_repeat`, `overlap`, clue-overlap test.

**R9 retire (P5).** `game._submit` under dm-tools: `message.strip() == "/retire"` opens `ask_retire`; otherwise the
message goes to the DM, whose `end_game` opens the same pause. `retire_choice`/`ending_choice` accept a choice id or
its number under dm-tools.

**R10 search (P2b).** `code_framer` passes `focus=[target, change ids]` (no `focus_ids` text) and the anchor list
`[verb_anchor(verb)]`. `recall` (codex `what_you_know`, fixer `_search_tool`) stays search: class S on the
allow-list (it lists candidates; the DM judges).

**R11 measures (P4 removes, E builds).** `dm_tools._audit`, `_log_only`, `_content`, `_name_tokens` and the
`leaks`/`log_only`/`claim_log` writes go. `evals/turn_judge.py`: sample N turns per save (seeded), Haiku judge with a
fixed rubric per measure (secret leak, pronoun mismatch, absent person named as present, item handed with no record,
mood change with no event in the scene, ask outcome: free grant / priced / partial / refused), JSON verdicts;
`evals/baselines/turn_judge_hand.yaml` holds hand verdicts; the report prints `count (precision p, n hand-checked)`
and "precision unmeasured" below 20. `npc_agency.leaked` and h2h C7 read the judge (keyword versions deleted). The
ask rubric separates a priced deal from a cave.

**R12 guard (P0 builds in log mode, P6 makes it strict).** `tests/guard/viii9.py`:
- `DENY`: qualname -> (inventory id, `only_from` or None). Functions are patched to raise; module-level patterns and
  word lists (`_AWAY`, `_DOWN`, `_FREEING`, `NONLETHAL`, `UNARMED`, `WRITING`, `LOOKS_AT`, `_LIFT`, `_UNDO`,
  `_REFUSE`, `READING`, `ANIMAL`, `_VERB_GOAL`) are swapped for objects whose every method raises.
  Message: `"constitution VIII.9 (code never deduces the story): dm-tools reached {qualname} ({inventory id})"`.
- Games: `offline_seed11_dmtools` (the Driver recipe) and `tests/guard/games_033.py` (ScriptedModel games covering
  `cases.md`). A `sys.setprofile` hook records every engine function reached.
- Static: AST-scan every function in `dm_tools.py` and `dm_world.py` and every reached function for `re.*` calls,
  calls on module-level compiled patterns, and references to module-level collections of 3+ string literals; each
  hit must be in `tests/guard/viii9_allow.py` as class P, F or S with a reason, else fail citing VIII.9.
- Mode: `VIII9_GUARD=log` (live runs: write hits to a JSONL, never raise) or `raise` (tests). P0 ships `log` with a
  census; each phase moves its entries to `raise`; P6 asserts all are `raise`.

## 4. Rules phase (R)

06.9.1 rewritten: the DM picks each adversary's act every exchange from the acts its state allows; the engine checks
legality, rolls and applies harm (owner ruling 2026-10-10; record the retired rationale and the measure that watches
for it: foes that wait or yield while unhurt). 06.9.3 attention and 06.9.4 lists become guidance shown to the DM and the
legality table. 06.3.9: the start range is the DM's. 01.13.7: the form is the DM's pick after the roll among those that
can land. 06.5.3 unchanged (already "the actor's choice"). PR-12-3 and 15.9.4: under the DM engine they inform the DM
and spawn nothing. 11.13.1: `/retire` or the DM. Data: `basic_verbs.yaml` `target_kinds` per verb and `covered_by` per
`excludes` entry; `resolution.yaml#reverses_goal`. One DL entry in `DL-CC.md`, re-assembled; anchors recompiled;
validator 0/0. Check first whether `basic_verbs.yaml` is generated (`rules/_process/simulation/*gen*`).

## 5. Phases

Each phase is one fresh agent (15-60 turns, 100-turn cap), on its own branch from the previous merge, writing
`HANDOFF-<phase>.md` when it runs beside others. "Lane" lists the only files it may change (tests and spec docs for its
phase are always allowed).

| Phase | Lane | Model | Wave / parallel | Turns | Needs |
|---|---|---|---|---|---|
| P0 guard census | `tests/guard/*` (new) | Sonnet | W1, parallel | 30-45 | base |
| P1 contract | `dm_tools.py`: `schema_for`, `_propose_roll` intake, tool dispatch stubs (`end_game`, `position`); `resolve/types.py` (`Stated`); `roles/prompts/dm.md`; `llm/offline.py` (DM heuristic); re-record `offline_seed11_dmtools` | Sonnet | W1, parallel | 35-50 | base |
| R rules | `rules/` (06, 01, 12, 15, 11 cards; data `basic_verbs.yaml`, `resolution.yaml`; DL-CC; generators) | **Opus** | W1, parallel | 40-60 | base |
| E measures | `evals/turn_judge.py`, `evals/baselines/*`, `evals/npc_agency.py`, `evals/h2h_score.py`, `tests/evals/*` | Sonnet | W1, parallel | 30-45 | base |
| P2a resolve: positions, contact, fight start, costs | `resolve/pipeline.py`, `resolve/change.py`, `resolve/conflict.py` (`strike_harm`, `weapon_of`), `resolve/costs.py` | Sonnet | W2, parallel | 45-60 | P1, R |
| P2b resolve: gate, necessity, frame, anchors | `resolve/gate.py`, `resolve/necessity.py`, `resolve/frame.py`, `retrieve/anchors.py`, `retrieve/scene.py` | Sonnet | W2, parallel | 35-50 | P1, R |
| P4 people and testimony | `dm_tools.py`: `_id`, `_party`, `_walk_on`, `_told`, `_audit`/`_log_only` removal, `_change` (new_npc, new_item, npc_leaves, fight), `target_kinds`, `code_framer` focus/anchors; `world/social.py` (`meet_npc` params); `gen/case.py` (`place_on`) | Sonnet | W2, parallel | 40-55 | P1, R |
| P3 foes and the answer turn | `resolve/foe_act.py` (new); `dm_world.py` (`world_step` foe part); `dm_tools.py`: `_run`, `_dm_loop`, `_reask`, `_world`, `_fight_block`, `_outcomes_text`, pause `detail["foes"]`, `cost_form` | Sonnet | W3, parallel with P5 | 45-60 | P2a, P4 |
| P5 leads, witnesses, retire | `dm_world.py` (`_lead`, new `_witness`; one call line in `world_step`); `world/pacing.py` (`lead_candidates`, bookkeeping split); `gen/case.py` (`short_of_sources`); the h15 hook; `game.py`, `dm/ending.py`; `dm_tools._end_game` body | Sonnet | W3, parallel with P3 | 30-45 | P4 |
| P6 guard strict and gates | `tests/guard/*`, `tests/guard/games_033.py`; fixes only for guard hits (any lane, smallest change) | Sonnet | W4 | 40-60 | all above |
| P7 re-check | `specs/033-*/implementation-results-P7.md`, saves under `saves/` | Sonnet scores; the orchestrator runs live | W5 | 20-30 + live | P6 |

Merge order inside a wave: W2 P2a, P2b, P4 (P4 last: `dm_tools.py`); W3 P3 then P5 (both touch `world_step`'s
body by one call line each; P5 rebases on P3). Only `offline_seed11_dmtools` is re-recorded, by the last phase of each
wave that changed dm-tools behavior (P1, P4, P3/P5, P6), never in parallel.

## 6. Analysis (speckit-analyze, done by hand)

**Coverage.** Every requirement maps to tasks: R1 T020-T024, R2 T025, R3 T040-T046, R4 T050-T054, R5 T026-T029 and
T043, R6 T030-T034, R7 T035-T039, R8 T033, R9 T055-T056, R10 T037-T038, R11 T034 and T060-T064, R12 T001-T006 and
T070-T074, R13 T075 (pipeline tests unchanged). Every inventory item marked reach Y/A is either in the denylist,
allow-listed with a class, or confirmed unreached by P0's census (D13, D14, D16, D19, D20, D46, D53, D54 were
low-confidence).

**Consistency.** The contract table, `contracts/dm.md.draft` and the schema task (T010) list the same fields. `Stated`
is the only new shared type. A5 (bands only on a roll) and the `change position` kind agree with R1. A3 (refusals)
agrees with the owner's A5 deletion (`fight` needs `to`).

**Constitution.** VIII.9: no new inference; every new code decision reads ids, enums or recorded state. VIII.2:
refusals are spine-only (presence, reach, a required id), and 032's one-revision rule bounds their cost. VIII.5: the
measures move out of the engine; no new blocking check. VIII.6: the prompt grows by no words; the FIGHT block gives the
DM legal acts, not rule text. Principle I: closed choices (enums) for every judgment code records.

**Risks.**
1. 06.9.1's retired rationale (AI referees pick senseless targets, decline to press): watched by P7's foe-act mix
   (strike share while engaged; waits and yields while unhurt). Owner decision D1.
2. More refusals (Force, fight `to`, `fail_on`): watched as refusals per turn vs 032 P7; a field the DM keeps missing
   gets a default only by an owner ruling. Owner decision D3.
3. The declared-with-move foe acts can lapse (owner decision D2).
4. The schema grows (about 14 fields): tokens in per call rise; watched as C1.
5. Parallel edits of `dm_tools.py` (P1, P4, P3, P5): lanes are by function; merge order fixed above.
6. P0's census may find more reached word matchers than the inventories list: they join the denylist and the phase
   whose lane holds them; a lane-less one goes to P6.
