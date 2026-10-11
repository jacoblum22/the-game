# Inventory: where code writes story state the DM didn't ask for (2026-10-10)

Read-only Sonnet inventory at spec032-base (P8a merged, P8b staged). The owner's ruling: code never infers story state from
actions or names; only the DM sets it through a tool, or as a rule's stated result of a roll the DM chose.

**Reach:**
- **Y:** the dm-tools engine reaches it. The entry points are `_propose_roll` → `run_beats` and `dm_world.world_step` → `foes_act`, `release_holds`, `beat_time`, `inject_lead`.
- **N:** pipeline-only.

## Class A: code guessing the fiction (delete candidates)

| # | where | what | trigger | reach |
|---|---|---|---|---|
| A1 | `pipeline.py:507-531` `_contact` | Actor and target set **engaged**; the actor's location set to here | Any melee Strike, Grapple or Force on a creature, **even a failed one**. Rule 06.4.3 says an out-of-reach Strike is refused ("Move first"); code does the opposite | Y |
| A2 | `pipeline.py:504, 522-523` `_contact` (Force) | Pushed back, or prone; the `_DOWN` word regex picks which (06.5.3 says "the actor's choice declared in the beat") | A landed Force | Y |
| A3 | `pipeline.py:463-499` `_moved` | Location = here; engaged "beside"; or a step toward or away, where "away" = an `_AWAY` word in the beat; a missing band defaults to near | `verb.move`, or a `move_to` goal | Y |
| A4 | `pipeline.py:808-812` `_roll` → `conflict.start` | **Starts a fight**: the conflict, foe Vitality, near band, conflict mode | Any rolled attack-trait beat on an NPC | Y |
| A5 | `conflict.py:92-95` `start` | Near band and location for each foe | Seeding a fight (06.3.9 default) | Y via A4 |
| A6 | `npc_layer.py:652-662` `respond` | A fight start plus a foe turn | A hostile NPC's reaction row | N |
| A7 | `conflict.py:260-263` `foe_beat` | The foe **closes in** a band | Every spent exchange in a fight | Y |
| A8 | `conflict.py:253-258, 216-237` | The foe stands up or breaks free; off-balance on the PC on a critical | Every exchange | Y |
| A9 | `conflict.py:266-278` | **The foe strikes the PC**: d20 against Guard, then harm. Backed by rules 06.9.2 and 06.4.1, but the foe's choice is code's | Every exchange | Y |
| A10 | `scene_state.py:63-100` `beat_writes` | Posture, manner and held slots from beats (T-12-18) | Every resolved beat | N |
| A11 | `pipeline.py:340`, `change.py:167-202`, `dm_tools.py:642-647` `_VERB_GOAL` | An untyped beat gets a goal from its verb (strike → harm, grapple → restrain, sneak → hide, move → move_to), which then triggers A3, A4 and A12 | Any untyped rolled beat | Y |
| A12 | `change.py:308-311` | An untyped Grapple becomes restrain, so a hold is applied | A landed Grapple | Y |
| A13 | `pipeline.py:969-988` `_cleanse` | Removes a hold if the beat is "aimed at it" (target or `_FREEING` words) | Cleanse check | Y |
| A14 | `pipeline.py:897-905` `_folded_hold` | A hold from the Reader's `holds` | Reader | N |
| A15 | `pipeline.py:1021-1027`, `costs.py:343-354` | **Code picks who notices you** (cost.exposure) and raises their alertness | `cost.exposure` | Y |
| A16 | `pipeline.py:1028-1033`, `costs.py:286-293` | **Code picks which item** is lost or damaged (cost.gear) | `cost.gear` | Y |
| A17 | `dm_tools.py:273-284`, `dm_world.py:109-111` | Ends the scene and opens a new one | A rest, day or week boundary (12.4.2) | Y |
| A18 | `dm_world.py:60-65`, `dm_tools.py:138-141` | Opens a scene if none is open; time mode free → site | Any turn without a scene | Y |
| A19 | `dm_world.py:56-57, 97-106`, `pacing.py:234-290`, `gen/hooks.py` | **Spawns people and documents** (a lead), and the PC learns it | The stuck-player counter (12.8.1) | Y |
| A20 | `h15.py:27`, `gen/case.py:341-392` `audit_cases` | **Spawns witness NPCs** at haven buildings | Every scene end | Y |
| A21 | `dm_tools.py:918-919` | An `npc_leaves` with no place goes to the first reachable place | The DM omits a place | Y |
| A22 | `dm_tools.py:581-585` → `mentions.py:171-179` `find_existing` | **Reuses an existing NPC by name, alias, role or given name**, and may move them "here now" | The DM names an unknown capitalised person | Y |
| A23 | `mentions.py`, `narration.py:156,255` | Entities and positions from the Narrator's draft; "held by X" regex | Narrator mentions | N |
| A24 | `social.py:257-285` `cast_described` | Moves or spawns people by role match | Director | N |
| A25 | `testimony.py:311-326` `_place_there` | Moves a person to a place a claim names | Testimony settle | N |
| A26 | `turn.py`, `narration.py`, `director.py` | Rest, move-on and scene cut from message regexes and counters | Player words | N |
| A27 | `narration.py:161-185` `_ask_oracle` | Writes a fact from an Oracle answer about a draft claim | Narrator | N |

## Class B: a rule's stated result of a roll or a paid cost (rule-backed)

| # | where | what | rule | reach |
|---|---|---|---|---|
| B1 | `costs.py:294-310` `cost.footing` | Off-balance, prone, restrained or pinned (with the foe as holder); otherwise a text fact. **With no form given, code takes the first OR option** | 01.13.7 | Y |
| B2 | `costs.py:355-357` | Loses hidden at S3+ | 01.13.6, 06.3.6 | Y |
| B3 | `costs.py:286-293` | Item dropped, damaged or destroyed (the item choice is A16) | 01.13.4 | Y |
| B4 | `costs.py:311-322` | A closed-door fact; standing -1 or -2 | 01.13.9 | Y |
| B5 | `costs.py`, `pipeline.py:1173-1190` | Harm and shortfall | 01.13.2, 01.13.8 | Y |
| B6 | `pipeline.py:839-845`, `conflict.py` | Strike harm; **the weapon and non-lethal choice come from word regexes** | 06.4.x, 06.13.1 | Y |
| B7 | `change.py:232-262` | The hold ladder by reach (only when typed restrain, or via A12) | 06.5.2 | Y |
| B8 | `scene_state.py:131-152` `release_holds` | Ends a hold when a party is out or not engaged (that band may itself be code-written, A1-A3) | 06.5.2 | Y |
| B9 | `scene_state.py:114-128` `_free` | Ends a hold on a landed free; **dm-tools never calls it, so a landed free ends no hold** | 01.2.7 | N |
| B10 | `projection.py`, `scenes.py` | Scene membership derived from location | 12.4.1 | Y |
| B11 | `details.py:142-146` | Bands and scene slots cleared at scene end | 12.4.8 | Y |
| B12 | `turn.py:823-870` | Dying, waking, last stand | 07.2.x, 07.5.9 | Y |
| B13 | `h00.py`, `social.py:603-623` | Condition expiry; a broken deal drops standing | 00.7.5, 06.7.3, 15.7.6 | Y |

## Class C: the DM asked through a tool

| # | where | what |
|---|---|---|
| C1 | `_travel` | The PC and the `who` ids move; the scene ends; time passes |
| C2 | `npc_leaves` | The NPC moves to the DM's place (default: A21) |
| C3 | `_end_scene` | The scene ends, then B11 and A20 |
| C4 | `_fight` | The DM's start range, the conflict |
| C5 | `_party`, `_walk_on`, `new_npc` | A walk-on made from the DM's words |
| C6 | `new_item`, coin, give, fact, condition | As asked |
| C7 | `_mood` | The DM's mood memory |
| C8 | `rest` | Time and recovery (the rest site is inferred from the place kind) |
| C9 | `apply_change` | A typed change_kind landing: holder, open, agreed, hidden, restrain |

## Identity and name guessing

| # | where | matches | reach |
|---|---|---|---|
| N1 | `dm_tools._id` | Exact name, unique and unsealed | Y |
| N2 | `_party`, `npc_layer.ANIMAL` | A head-noun list decides "creature"; a capital letter decides "named person"; a made-up id's tail becomes the words | Y |
| N3 | `mentions.find_existing` | Name, alias, id tail, role, given name ("Edda" → "Edda Brightcote") | Y via A22 |
| N4 | `change._person`, `scene.resolve_names` | A persuade_to target found by names in the DM's free text | Y |
| N5 | `pipeline._same_goal` | An id prefix picks the progress clock | Y |
| N6 | `pipeline` `_FREEING`, `_AWAY`, `_DOWN`; `conflict.py:25-28,139-153` | Word regexes: freeing, away, knock-down, weapon, non-lethal, unarmed | Y |
| N7-N9 | `npc_layer`, `social.cast_described`, `mentions`/`testimony` | Name, role and content-word matching | N |

## Not counted
- World generation and seeding (`gen/*`, seed placement, the opening scene, creation).
- Dead code (`harm/exits.py` yield and retreat).
- Display and audit code, which writes no state.
- `h.12.scene_test` and `random_event` write only `meta`, which dm-tools never reads.
