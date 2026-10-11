# HANDOFF 033 P2a (T020-T029 ticked)
Done, all keyed on `beat.stated is not None` (pipeline byte-equal; `offline_seed11.json` untouched): `pipeline` `_stated_position`,
`_force_ladder` (C2), no `_moved`/`_contact`/`conflict.start`/`typed_goal`/GOAL_ASK, `_cleanse` without words, `_same_goal(exact=)`,
`_stated_cost_params`; `change` (no untyped restrain, no `_person` words, `free` ends holds); `conflict.weapon_of`, `strike_harm(w=, mode=)`;
`costs.footing_options/apply_footing/pending_footing`; `_propose_roll` no " (nonlethal)". Tests: `tests/engine/test_spec033_p2a.py` (26).
Flipped 2 old tests in `test_spec032_p4` (no code-started fight; nonlethal rides in `stated`). `offline_seed11_dmtools` re-recorded locally.
Guard: P2a DENY entries `raise` (+ `_freeing_words`, `typed_goal`, `strike_harm_by_words`; `_cleanse`/`_person` left out, still called); pending:P2a rows
deleted, `_person` reclassed P, `_force_ladder` P rows added, 5 stale F rows (`oof.price_line`, `to_player`) deleted. `reached.txt` NOT committed: regenerate at merge.
Gates: full pytest 2544 passed, 5 skipped, 2 xfailed (with regenerated reached.txt); ruff and pyright clean on touched files.
Traps:
1. Footing: a stated cost.footing writes nothing and sets meta `footing_pending` {actor, opponent, frame_id, severity, options}. P3 shows it on COST TO SHAPE,
   calls `costs.apply_footing(tx, rules, pending, cost_form)` -> (option, defaulted), logs `not_chosen:cost_form` when defaulted.
2. `env.defaults` (PipelineEnv) holds `not_chosen:fail_on` made inside the pipeline; nothing drains it into `screen.dm_tools.defaults` yet (P3, propose and answer turns).
3. `frame.reverses`/`reverses_goal` is P2b's (frame.py), not done. slide/lower/swept write a `footing` fact (+ NPC position, never the PC's place); `lower:` needs place `data["lower"]` (none generated).
4. The Strike reach refusal is P4 (T032). Strike/Grapple write no band now. band_back = one band farther from the opponent; restrained/pinned with no opponent get an entity-less source.
