# HANDOFF 033 P1 (the DM contract; lane dm_tools schema/intake/stubs, types.py, dm.md, offline.py)
Done (T010-T015): `Stated` + `Beat.stated` (None, excluded from dumps: the pipeline's events are unchanged); `dm_tools.schema_for`
(+`approaches`), `foe_schema(legal)`, `_stated` intake, `_position` (writes the band/place), `_end_game` stub; `dm.md` 780 words;
offline `_dm` fills the new fields and answers a foe schema (strike if legal else first); `offline_seed11_dmtools` re-recorded.
Contract: every object is all-required (schemas.obj), so OMITTED = `""`/`"none"`/`"plain"`/false. `as`: none|he|she|they|creature|thing
(propose_roll, change, said[]); `force` none|push|prone; `approach` plain + the 13 `excludes.what` strings; `weapon`,`fail_on` ids;
`reads`; change gets `name`,`as`,`knows`, kind `position`; tool `end_game{why}`; step gets `cost_form` (no `foes`, D2).
Defaults logged in `screen.dm_tools.defaults` as `not_chosen:{field}`: force (verb.force), weapon (strike; wields fact else unarmed),
fail_on (cost exposure/gear/closed_door), fight.to (change fight, logged at dispatch), change_whom (move_to mover = actor), position `who`/`what`. NOT logged: nonlethal; `not_chosen:as` is P4 (`_party`); cost_form/foes.<id> are P3.
Refused (a value given but illegal): weapon not held, approach not in the list, move_to a place id (use travel).
Gates: P1 file 11 tests; full pytest on the merged tree (e77cc07) 2517 passed, 5 skipped, 2 xfailed; ruff clean, pyright clean on touched files (pydantic "unresolved" env note only).
Traps: (1) ScriptedModel now `conform`s scripted DM dicts (offline.py `_dm_defaults`, per tool branch) so old scripts need no new keys.
(2) `as`, `name`, `knows`, `cost_form`, `reads`, `approach`, `fail_on`, `force` are in the schema but only `Stated` carries them; `_party`/
`_walk_on`/`new_npc`/`new_item`/`_fight` (to default near) ignore `as/name/knows` until P4. (3) P2a must read
`beat.stated` in pipeline/conflict/change; `_propose_roll` still appends " (nonlethal)" to the method and `_VERB_GOAL` is gone
(an untyped beat is `Change` None; `apply_change`/pipeline still guess downstream). (4) Stated.position = (mover, band, other) only when the
target is an entity and `change_what` is exactly a band; `_position` has no reach refusal (P2a). (5) `foe_schema` per-foe `act` enum = legal
acts; P3 supplies `legal`. (6) guard allow: I added `schema_for:words:AS_KINDS` (P) and dropped the `_propose_roll _VERB_GOAL` row; `reached.txt` regenerated.
