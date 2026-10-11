# Inventory: decisions made by word matching (2026-10-10)

Read-only Sonnet inventory at spec032-base (84d343a), done for constitution VIII.9: code never decides by word matching on prose.

**Reach:**
- **A:** reached from `dm_tools.py`/`dm_world.py`.
- **S:** reached only through the game shell.
- **X:** reached only through `/fix`.
- **N:** pipeline-only.

Low-confidence reach: D13, D16, D19, D20, D46, D53, D54.

## D: decisions that change state or outcomes

| # | where | text read | decides | reach |
|---|---|---|---|---|
| D1 | `pipeline.py:455 _AWAY`, `_moved` | beat words (withdraw, retreat, flee, away…) | moving away a band | A |
| D2 | `pipeline.py:504 _DOWN`, `_contact` | trip, prone, floor, sweep, down | knock-down vs push | A |
| D3 | `pipeline.py:916 _FREEING`, `_cleanse` | free, escape, wriggle… | frees from a hold | A |
| D4 | `pipeline.py:922 _same_goal` | goal id prefix | progress carries over | A (borderline P) |
| D5 | `conflict.py:26 NONLETHAL`, `27 UNARMED`, `139-153 weapon`; `dm_tools` appends "(nonlethal)" | method words | lethal or not, weapon or unarmed, so harm | A |
| D6 | `gate.py:34 _STOP`, `excluded_by`, `would_be_license` | method/intent words vs rule `excludes`/licence lists | refuses the beat or needs a licence | A |
| D7 | `gate.py:37 WRITING` | notice, sign, letter, book… | the beat is "reading writing" | A |
| D8 | `gate.py:355 LOOKS_AT`, `reads_writing` | look, peek, scan… | looks vs reads | A |
| D9 | `necessity.py:80 plain_reading`, `certain_talk`, `looks_here` | method/intent words | whether a roll is needed | A |
| D10 | `scene.py:23 READING`, `cannot_read` | read, wording, inscription… | refuses an impossible reading | A |
| D11 | `frame.py:352 _LIFT`, `lift_or_carry` | lift, carry, heave… | the attribute and verb (exert vs handle) | A |
| D12 | `frame.py:809-830 reverses` | undo and refuse phrasings | a cost cancels an earlier cost | A? |
| D13 | `frame.py:889-896 _fitted` | method words vs attribute and verb names | which attribute fits | A? |
| D14 | `oracle.py:32 _POSSESS`, `36 _NEG`, `positive` | has/holds; not/never | the oracle question's polarity | A |
| D15 | `change.py:111-125 _person` → `scene.resolve_names` | target text | who the persuade/restrain target is | A |
| D16 | `change.py:366` | `startswith` on text | the prior line covers the change | A? |
| D17 | `scene.py:178 _PROPER_RUN`, `191-235 resolve_names` | any text: capital runs, alias, role, head noun | maps prose to ids | A |
| D18 | `scene.py:168-174 focus_ids` | message and target | the entities in focus | A |
| D19 | `scene.py:346 scene_facts` | name matching | the facts packed | A? |
| D20 | `anchors.py:94-105 _intent_hits` | intent vs anchor phrases | which clue anchor is hit | A? |
| D21 | `dm_tools.py:496-502 _NAME`, `_PC_WORDS` | DM argument strings | "is a proper name"; "means the PC" | A |
| D22 | `dm_tools.py:533-562 _party` | DM arguments: ANIMAL, `_NAME`, pc words | who a roll or change is aimed at; walk-on kind | A |
| D23 | `dm_tools.py:565-586 _walk_on` | DM description | mints or reuses through `find_existing` / `cast_described` | A |
| D24 | `dm_tools.py:46-47, 505-531 target_kinds` | rules target-kind prose | person vs thing | A (static rules text) |
| D25 | `dm_tools.py:763-774 _state` | `about.lower() in (...)` | which state view | A |
| D27 | `dm_tools.py:~1077 _along` | `re.split` of DM text | the party list | A |
| D28 | `dm_tools.py:1192-1224 _told` | said text: `covers`, `is_repeat`, pc words | whether a said record is written | A |
| D29 | `dm_tools.py:~895-905` | item name vs existing names | twin-item advice | A (advisory) |
| D30 | `mentions.py:101 find_existing` | name vs names and aliases (fuzzy) | "this is the existing entity" | A |
| D31 | `mentions.py:31 _ARTICLE`, `bare`, `_proper`, `_slug` | mention text | proper-noun test | A |
| D32 | `mentions.py:213 _HELD_BY`, `_holder` | "held/carried by X" | writes a holder | A |
| D33 | `mentions.py:32-40 _NPC_KEYS`, `_PRONOUNS`, `_GENDERS`, `_npc` | description words | a walk-on's pronouns, gender, wants and fears | A |
| D34 | `npc_layer.py ANIMAL`, `is_animal`, `_TRADE`, `role_key` | role words | animal vs person | A |
| D35 | `social.py:208 find_npc`, `254 _GROUP`, `257 cast_described` | person description | already in the cast | A/S |
| D36 | `testimony.py:66-72 overlap`, `is_repeat` | two sentences | a repeat | A |
| D37 | `testimony.py:~119 _named`, `~139 _premise` | claim text | who a claim is about; premise on record | A |
| D38 | `testimony.py:167 _BEYOND`, `203 _OWN_WILL`, `~230 _case_route` | said text: secret, treasure…; will, refuses… | beyond the speaker's knowledge; routes to a case | A |
| D39 | `testimony.py:307 _FIGURE`, `311-320 _place_there` | number and place words | writes place facts from prose | A |
| D40 | `audit/text.py` (`norm`, `stem`, `content`, `overlap`, `covers`…) | any | the primitives under the above | A |
| D41 | `codex.py:216-354` `STOP`, `GENERAL`, `_stems`, `PROMISE`, `promise_subject`, `what_you_know` | the DM's recall query | which facts the DM is shown | A |
| D43 | `ending.py:44 _RETIRE`, `is_retire`, `retire_choice`, `ending_choice` | the player's message | retire, which ends the game | S |
| D44 | `game.py` routing of "/fix", "ooc:" | command prefixes | routing | S (command syntax, P) |
| D45 | `fixer.py:99 _names`, `134-140 resolve`, `387-410 _search_tool`, `_ledger_tool` | complaint and search args | keyword search; name → id | X |
| D46 | `dispute.py` | complaint text | (not mapped) | X |
| D47-D52 | `turn.py` (`rest_kind`, `_heads_for`, OOF words), `narration.py` (`moves_on`), `npc_layer` (named, addressed, tags), `audit/claims`, `declare`, `safety`, `screen`, `pipeline` (`own_line`) | prose | rests, travel, cuts, addressee, narration checks | N |
| D53 | `incident.py OFFICERS`, `details.slot_of`, `views.sheet_holds`, `unnamed_label` | role and slot words | various | ? |
| D54 | `packet.py pronouns_of`, `own_words`, `background_line`, `people_card` | NPC data | card contents (mostly formatting) | A |
| D55 | `_seed_packs.py role_key` | NPC role prose | the NPC's common-knowledge topics | A (play time via `speaker_card`) |

## M: measurement or log only (no effect on play)
- **`dm_tools._audit`:** the leak measure.
- **`dm_tools._log_only`:** pronoun, absent_named, item_unbacked.
- **`engine/llm/offline.py`:** the test double.
- **Eval-only uses of `audit/*`.**

## F: formatting only
- `dm_world._up`
- `packet.speaker_card` labels
- `player_text`, `oof`, `text/render`, `play/render`
- CLI menu keys

## P: parsing code-made strings (fine)
- entity ids (`_ID_LIKE`, `_ENTITY_ID`), licence and rule ids, rule atoms, the cost DSL
- `RULE_ID`
- enum tuples (`TOOLS`, `CHANGES`, `COSTS`, `MOOD`, `IDLE`, `JUMPS`)
