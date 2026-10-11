# HANDOFF 032 P8b (fights and costs), on spec032-base + this commit; default NOT flipped
Done (cases: `cases.md` section P8b; tests: `tests/engine/test_spec032_p8b.py`, 50 pass; none from the held-out set):
- ROOT CAUSE of H07/H10/H11 (0 foe turns): `code_framer` called `schema_context` without `cost_menu_ids`, so a scene with no scene facts had the
  cost menu `cost.twist` alone and EVERY `propose_roll` was refused ("cost.twist only when no other entry is a candidate"). Now passes the whole menu.
- "You get hurt" for reading tracks: old loop returned the FIRST source's candidate (`threatened[0]` = harm) before the DM's `fail_cost` source was tried.
  Now: DM cost if legal in some source (source that lists it first), else the verb's list in `resolution.yaml#cost_selection.verb_costs` (new, DL-01-54;
  observe/recall = time, exposure, drain, never harm); none legal on a risky look = Safe roll. Verbs with no list keep the old fallback. `PREFERRED_COST` removed.
- Start range: 06.3.9 says the DM sets it, so `change fight` takes `to` = engaged|close|near|far|distant (unknown/empty = near, no refusal; ignored for a fight already running). dm.md says so.
- P7 "first foe acts were moves": `code_framer` never set `trait.delivery.melee`, so a PC Strike wrote no contact band (`_contact`). Now a Strike with the pair at no band/engaged/close gets the trait; after `change fight to=near` it stays ranged.
- "Changed: your opponent worn": `oof.changed_line` now "<name> is <state>" (shared with the pipeline).
- Gates: p8b 50 pass; ruff clean and pyright clean (no new errors; pydantic/pytest unresolved is the env) on touched files; validator 0/0; full pytest: 2348 passed, 2 failed (prompt word budget, an old "bloodied" string), both fixed after; affected files re-run 167 passed.
- Re-recorded BOTH games: dmtools (dm.md changed) and `offline_seed11` whose ONLY diff is `rules_hash` (resolution.yaml gained `verb_costs`).
Not done: tasks.md has no P8 rows (nothing ticked). Live re-run of the fighter/talker personas and of held-out is NOT done (the set is spent; do not tune on it).
Traps for the merge with P8a: I edited only `code_framer` (the cost/trait block), `_fight` + one line in `_change` (`_fight(..., str(c.get("to")))`), and removed the `PREFERRED_COST` constant at the top of dm_tools.py;
dm.md line for `fight` too. Both of us change the recorded dmtools game: re-record `offline_seed11_dmtools` ONCE after merging, never merge the JSON. Also CRLF files.
A `propose_roll` with a ranged attack needs `change fight to=<range>` first (no `range` field was added to propose_roll). A landed Force pushes the target back (06.5.3), so Force is not "engaged" afterwards.
