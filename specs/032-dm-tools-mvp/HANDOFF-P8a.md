# HANDOFF-P8a (people and things the DM names; from spec032-base 6336d8f; P8b parallel: dm_world/costs/oof)
Done (cases first: `cases.md` section P8a + the "revision" note; tests `tests/engine/test_spec032_p8a.py` 69 pass; full pytest line in the commit/report):
- Orchestrator design steer applied: code does NO name matching. `_party`: exact id (or exact name, or the id the DM gave `new_npc` this turn, `Turn.aliases`) is that
  entity; anything else is the DM naming someone new: a minimal walk-on at the scene's place (`_walk_on`: creature `mind: animal`, a capitalised name, else `meet_npc`
  with the words as role/alias), id returned in the tool result `(New on record, here now: <words> (<id>). Use these ids from now on.)`; the situation lists it.
  Removed: `_labels`/`_speaker`, `find_existing`/`cast_described` reuse, P3's head-noun reuse, plural group walk-ons.
- Verb target kinds from `basic_verbs.yaml` (`target_kinds`, replaces `PERSON_VERBS`): talk/grapple/sneak/help person; strike/force/setup person+object; observe/handle/move
  object+person; exert/endure object; recall/evade/ready none. `target_is_person` uses the DM's `change_kind` slot (persuade_to/restrain/free person; open/close/take/give/make thing).
  A thing in words is never made a person and never refused ("the stuck hatch" -> `change_what` text).
- `_told`: a line verbatim in the passage by a speaker that is not an entity id is a new walk-on's; dead/elsewhere (by id) still dropped.
- `travel` `who` = comma list of ids (exact name works); only those named move; output `With the character: ...` / `Did not come: <why>`. (No new schema field: `change.who`.)
- `ANIMAL` (npc_layer.py) matches compounds ending dog/hound; it only decides the KIND of a made walk-on (wolfhound was made a human "Lom Underhill"), never who it is.
- dm.md edited inside the 800-word budget; only `offline_seed11_dmtools` re-recorded. Saved H01-H04/H06 first calls replayed offline: all ROLL OFFERED (H03 rider is not made: observe is object-first).
Traps for the merge with P8b:
1. H01/H06 in the saved run also died on `threatened_cost: cost.twist only when no other entry is a candidate` after the DM gave cost.drain/time: costs lane, NOT fixed here.
2. Re-record `offline_seed11_dmtools` AFTER merging (do not hand-merge the JSON); dm.md is at the word budget, P8b must trim as much as it adds.
3. `_id` still resolves an exact name (kept: otherwise a DM writing a recorded person's exact name would duplicate them). Orchestrator may want that gone.
4. P3 tests R1/R16/R17-R20, `test_a_thing_is_not_made...`, E1 and P5b J8 were rewritten for the new rule (an `npc.` id or any unrecorded speaker is a new walk-on).
5. Working-copy files are CRLF; the new test file is LF. Held-out set is SEEN; nothing was tuned on it.
