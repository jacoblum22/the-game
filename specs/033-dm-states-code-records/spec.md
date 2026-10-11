# Feature spec 033: the DM states, code records (no deduction, no word matching on the dm-tools path)

**Input**: owner rulings 2026-10-10 (13 requirements, below); constitution 3.1.0 VIII.9 "Code never deduces the story";
`research_notes/Playtest round 2 solutions/spec032-investigation/fiction-inference-inventory.md` (classes A/B/C, N) and
`word-matching-inventory.md` (classes D/M/F/P); `specs/032-dm-tools-mvp/HANDOFF.md`; rules 06.3.9, 06.4.3, 06.4.8,
06.5.2, 06.5.3, 06.9.1-06.9.4, 06.11.5, 01.13.1, 01.13.4-01.13.9, 01.9.3, 02.4.6, 12.8.1, PR-12-3, 15.9.4, 11.13.1.
**Status**: design only (slice 1). `plan.md` (contract table, phases, analysis), `cases.md`, `tasks.md` and
`contracts/dm.md.draft` sit beside this file. Clarify was skipped; its questions are answered as assumptions (below).
**Base**: `spec032-base` at 8a8bcb8 (53875ef plus one OVERNIGHT-LOG commit; no code difference).

## The principle (VIII.9, binding)

Code MUST NOT infer story state (positions, range, presence, who comes along, who holds whom, identity, an enemy's
choice, a cost's form) and MUST NOT decide anything by matching words in natural-language text. The DM model states
these through a tool or a field, or by choosing one of a rule's options. Code records what it is told and does the
arithmetic: dice, harm, the stated result of a roll. Parsing code-made ids and tokens is fine (class P); formatting
is fine (class F); keyword search may find candidates that a model then judges (class S), but a match never decides.

## Requirements (the owner's rulings, numbered as given)

| # | Requirement | Inventory items | Acceptance |
|---|---|---|---|
| R1 | Positions come from the DM: `change position`, or `change_kind=move_to` on `propose_roll`. Rule options (Force push or prone, a footing form) are DM-chosen fields. No first-option pick, no word test. | A1 A2 A3 A11 A12 A13, D1 D2 D3, B1 (OR) | No band, location or hold is written on the dm-tools path except from a DM field or a rule's stated roll result on DM-stated fields (cases C1-C3). |
| R2 | Only the DM's `change fight` (with `to`) starts a fight. | A4, A5 | `conflict.start` is reached only from `dm_tools._fight` (guard). |
| R3 | The DM picks each foe's act every exchange from the 06.9.4 option set; code checks legality, rolls, applies harm. | A7 A8 A9 | `conflict.foe_beat` is never reached by dm-tools; each foe act in a save traces to a DM `foes` entry (C4). |
| R4 | Leads and witnesses are facts to the DM; code never spawns people or documents in play. | A19 A20 | `inject_lead` and `audit_cases` are never reached by dm-tools; the DM is told (C6, C7). |
| R5 | Penalty details are DM-stated fields, used exactly: who notices, which item, which footing form, lethal or not, the weapon. | A15 A16, B1, D5 | `_cost_params` and `conflict.weapon` (word path) never reached; costs land on the stated ids (C5). |
| R6 | No name guessing. Identity is an exact id or exact equality with a recorded name; walk-ons get kind and pronouns from the DM (`as`); `"pc"` is a literal token. | A22, N1-N6, D17 D21-D23 D30-D35 | `find_existing`, `write_mentions`, `ANIMAL`, `_NAME`, `_PC_WORDS`, `resolve_names` never reached (C8). |
| R7 | Every beat-text decision becomes a closed DM field with a default: reads writing, lift or carry, attribute, roll needed, cost reversal, licence and exclusion. | D6-D16 | `excluded_by`, `would_be_license`, `reads_writing`, `lift_or_carry` word path, `reverses` word path, `_fitted` never reached (C1). |
| R8 | Testimony: `said` is recorded as given; only spine checks (speaker exists or becomes a walk-on, present, alive). | D28, D36-D39 | `is_repeat`, `overlap`, `covers` never reached by `_told` (C9). |
| R9 | Retire by `/retire` or the DM's `end_game`; no word test on the player's message. | D43 | `is_retire`'s regex is not consulted under dm-tools (C10). |
| R10 | Search stays search; where a match decides today (D20 anchor hits, D18 focus), use ids or the model's judgment. | D18-D20, D41, D45 | The frame's anchor is the verb's card id; focus is ids; recall stays search (class S, allow-listed). |
| R11 | Word-matching measures leave the engine; robust measures live in `evals/` (Haiku judge, fixed rubric, a hand-checked precision sample; every count printed with its precision). | M: `_audit`, `_log_only`, `npc_agency.leaked`, h2h C7 | No `leaks`/`log_only` stats written by dm-tools; `evals/turn_judge.py` reports count plus precision (C11). |
| R12 | A guard: a runtime denylist test over offline dm-tools games, and a static test over `dm_tools.py`, `dm_world.py` and the functions they reach; failures cite constitution VIII.9. | all | Both tests in the default pytest run (C12). |
| R13 | Out of scope: deleting the pipeline. dm-tools must not reach pipeline guessing code; the pipeline keeps its own until its deletion spec. | | Pipeline tests unchanged; recordings other than `offline_seed11_dmtools` untouched. |

## What stays (rule-backed, class B and C)

Strike harm on a landed blow (06.4.3) with the DM's weapon and lethal choice; the hold ladder (06.5.2) when the DM typed
`restrain`; breaking free ends a hold and a critical leaves the holder off balance; Force's ladder on the DM's push or
prone; the cost DSL's writes at the read severity on the DM's ids and form; exposure at S3+ ends hidden (01.13.6); hold
release when a party is out (06.5.2); scene membership from recorded location (12.4.1); dying and waking (07.2.x); a
time jump or travel opens a scene (owner ruling 2026-10-10); the inconclusive-streak counter that raises the lead
trigger (12.8.1); the clue judgment model call (spec 029) behind `reveal_clue`.

## Assumptions (clarify skipped; each is the default the plan builds on)

- **A1 Foe acts are declared with the move.** The DM lists `foes` in the same answer as the PC's move (with a
  `propose_roll`, they are stored on the pause and run when the roll resolves). No extra model call per exchange.
  An act that the PC's result made illegal (the foe is now down, pinned, out of reach) lapses, and the DM is told why
  (a rule's result, not a choice). See owner decision D2 for the alternative.
- **A2 Missing picks get one re-ask, then nothing.** A fight exchange whose `foes` omits an able foe, or a cost that
  needs a form with no `cost_form`, gets one extra DM call asking only for the missing picks. Still missing: the foe
  waits, and the cost writes nothing structural (the DM is told the severity in words). Both are logged.
- **A3 Defaults only where a rule or the record names one; refusals where the rule says "the actor's choice".**
  `nonlethal` false (06.4.8); `weapon` = the item recorded in hand, else unarmed (a recorded fact, not a guess);
  `as` they for a person-only slot, thing otherwise; a foe's `target` the PC; `approach` plain; `reads` false. Refused
  with the options listed (one revision, the 032 mechanism): Force without `force`; `fight` without `to` (A5 deleted);
  exposure, gear or closed_door with no `fail_on` and no structural source; a Strike at a recorded band out of reach.
- **A4 Footing forms are picked after the roll.** The severity is known only after the roll and 01.13.7's options
  differ by severity, so the answer turn shows COST TO SHAPE with the options that can land (an opponent exists,
  a flag is held, an exit exists) and the DM picks one in the same call that narrates the result.
- **A5 Positions on a roll are bands only.** `move_to` on `propose_roll` takes a band toward the other party; a move to
  another place is `change travel` after the success, a place here is `change position`.
- **A6 Retire: both.** `/retire` (exact command, class P) and the DM's `end_game` tool open the existing confirmation
  pause; the confirmation makes a DM false positive harmless. Menus answered by text accept a choice id or its number.
- **A7 Testimony is never settled by code on dm-tools.** If a told thing becomes true, the DM records it with `change
  fact`; PR-12-12's word triggers (`triggered`, `_premise`, `_named`) stay pipeline-only.
- **A8 Exclusions map to licences by data.** Each `excludes` entry in `basic_verbs.yaml` gains `covered_by` (licence
  ids), and each verb gains `target_kinds` (person, object); the rules phase adds them. No licence is chosen by words.
- **A9 Leads and witnesses are told once.** A raised lead trigger is lowered and the streak reset after the DM is told
  (bookkeeping). A clue node short of live sources is told once per node (a meta flag) with its id; the DM's
  `new_npc`/`new_item` with `knows: <node id>` places the node's reserve on that entity (an id, no words).
- **A10 Foe acts are melee only.** strike, close_in, withdraw, stand, break_free, grapple, flee, yield, wait. Windup,
  flank, aim, reload, shoot and defend wait for chapter 09's lists (today's `foe_beat` has none of them either).
- **A11 Measures need a hand-checked sample.** The orchestrator (or owner) fills the hand verdicts in the last phase; a
  measure with fewer than 20 hand verdicts prints "precision unmeasured" and is not quoted as a number.

## Success criteria

- SC1: the runtime guard plays the offline dm-tools recording and the scripted coverage games with every denylisted
  function patched to raise, and passes; a planted call fails it with "constitution VIII.9" in the message.
- SC2: the static guard passes with a reviewed allow-list (classes P, F, S only); a planted regex in `dm_tools.py`
  fails it.
- SC3: `dm.md` at most 800 words (draft: 786).
- SC4: full gates: ruff, pyright, pytest (no new failures), `validate_ruleset.py` 0 ERROR / 0 WARN.
- SC5 (live, last phase): fresh talker, fighter and explorer games on dm-tools (Haiku engine, Sonnet player): 0 guard
  hits (log mode); every foe act traced to a DM pick; refusals per turn and model calls per turn within 25% of 032's
  P7 figures; told lines dropped (C9) below 032's 28; turn-judge counts reported with measured precision.
