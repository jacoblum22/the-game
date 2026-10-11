# Reach census (spec 033 P0)

Games: the recorded `offline_seed11_dmtools` (24 turns; the offline DM only talks and offers strike/grapple/force rolls)
and a scripted probe of 18 turns (`tests/guard/census.py`): read, move, grapple, free, force, talk/persuade, sneak, climb,
door, lift, new_npc/new_item/coin/fact, fight, strike, condition, npc_leaves, give_item, travel, rest, recall, state, clue,
mood, end_scene. Counts are calls inside a dm-tools turn (rec / probe). Re-run: `py -3.12 -m tests.guard.census table`.

Denylist: 71 entries (`tests/guard/viii9.py` DENY), all in log mode. 48 reached by a turn, 23 not. Static scan: 235 hits
in 870 reached functions plus all of `dm_tools.py` and `dm_world.py` (allow-list: 100 P, 55 F, 7 S, 73 pending).

## The low-confidence items
| item | verdict | evidence |
|---|---|---|
| D13 `frame._fitted` | reached 4/30, class P: exact-equality of a form against rule example text, no word matching; stays | `_costs` calls it |
| D14 `oracle.positive` | reached 0/4 only through `oof.fact_short` (a label): class F | the oracle question path is not a turn |
| D16 `change.py:366` | `startswith` on two code-assembled strings (a recorded `agreed` value): class P | `apply_change` reached 1/11 |
| D19 `scene.scene_facts` | reached 1/12: ranking by id overlap for the packet, no decision: class S | `schema_context` |
| D20 `anchors._intent_hits` | REACHED 90/983: regex of anchor phrases over the beat's intent and method text. Now DENY (P2b) | `score_anchor` |
| D46 `dispute.py` | unreached: only `/fix` (`Game.dispute`), not a turn: class X | no import from dm_tools/dm_world |
| D53 `incident.OFFICERS`, `details.slot_of`, `views.sheet_holds` | unreached; `views.unnamed_label` reached (format): F | display_name |
| D54 `packet.people_card` | reached 197/481, formatting: F; `pronouns_of`, `own_words`, `background_line` only outside turns | |
| `world_step.deliver_learning`, `npcs_respond` | unreached (pipeline's world step, not `dm_world`) | |
| `codex.what_you_know` | reached via `_recall` 0/1: class S | stays |
| `audit.text` primitives | reached from `_told.covers`, `testimony.overlap`, `SceneIndex.of` (from `_log_only`): all P4's; none from codex | edges in the census |

## Denylist entries reached (rec/probe), by the phase that removes them
- P2a: `_moved` 0/1, `_AWAY` 0/1, `_DOWN` 0/2, `_contact` 1/4, `_cleanse` 1/7, `_cost_params` 0/3, `conflict.start` 1/2 (from
  `_run`, never from `_fight`), `NONLETHAL` 1/1, `UNARMED` 0/1, `weapon` 1/1, `_VERB_GOAL` 0/5, `change._person` 0/1.
  Unreached: `_FREEING` (`_cleanse` runs, its word test did not).
- P3: `foes_act` 23/25 every fight exchange, `foe_beat` 0/16.
- P5: `inject_lead` 7/0 (the recorded game, stuck-player lead), `audit_cases` 0/2 (a scene end), `is_retire` and `_RETIRE`
  24/25 (shell scope: every submit).
- P2b: `_STOP` 180/1146, `excluded_by` 15/165, `excluded_anywhere` 1/11, `reads_writing` 2/21, `WRITING`, `LOOKS_AT`, `READING`
  0/1, `focus_ids` 1/11, `resolve_names` 0/2, `_PROPER_RUN` 0/2, `_LIFT` 0/12, `_intent_hits` 90/983. Unreached: `would_be_license`,
  `_tongue`, `_UNDO`, `_REFUSE` (they need an excluded method or a cost reversal).
- P4: `_NAME` 0/3, `_PC_WORDS` 24/47, `_PERSON_KIND`/`_THING_KIND` 6/66, `_audit`/`_log_only`/`_name_tokens` 24/31, `_content` 72/82,
  `write_mentions`, `find_existing`, `_proper`, `_npc` 0/1, `bare` 0/140, `_ARTICLE` 0/147, `ANIMAL` 0/9, `is_repeat` 13/24, `overlap` 42/276.
  Unreached: `_HELD_BY`, `_holder`, `_NPC_KEYS`, `_PRONOUNS`, `_GENDERS`, `_slug`, `is_animal`/`role_key`/`find_npc`/`_GROUP`/`cast_described`,
  testimony `_named`, `_premise`, `_BEYOND`, `_OWN_WILL`, `_case_route`, `_FIGURE`, `_place_there` (settle runs only in the pipeline).

## Word matchers the inventories missed (assigned)
- `gen.npc.role_implies` (role words imply age and pronouns; reached 0/3 through `new_npc` -> `meet_npc`): P4, now DENY.
  Safe once `as` always supplies pronouns.
- `dm_tools._along` (`re.split` of the DM's `who` list): ids only, class P; its `_PC_WORDS` is P4's.
- A21 (`npc_leaves` with no `to` goes to the first reachable place) reached in the probe (no refusal): no function to deny;
  P4 must delete the default in `_change`. A17 `time_jumped` and A18 `ensure_site` are structural and stay (spec "What stays").
