# Revision C2c report

Agent C2c. Row: I-087 (part (a); C2b resolved part (b)). Nothing committed; ch.13 untouched.

## I-087 (a): tier-4 and tier-5 depth under every level-2 node (resolved)
- **Scope as set by the prompt:** every level-2 deed node callings pick from has at least one `min_tier`-4 and
  one `min_tier`-5 tag-gated ability. This is stricter than C2b's audit, which counted "any ability at
  `min_tier` 4+": by that count 43 nodes had a gap, but 61 of 81 nodes had no `min_tier`-4 ability and 62 had no
  `min_tier`-5 one. All 81 level-2 nodes are under some calling's own gate (8 to 13 callings each, a near-uniform
  spread), so all gaps were filled; no handoff remains.
- **Authored:** 123 abilities (61 at `min_tier` 4, 62 at `min_tier` 5), one rank each (MAX_RANKS), in one spec
  file `rules/_process/simulation/05-gen_data05/ab_deep.py`, added to `gen_data05.py`'s MODULES. Each has its own
  id, name, leaf tag, `mod_group`, principle, limitation and at least one exclusion, and follows the existing
  tier-4/5 models: workings at Focus 2–3 with a scene or long-rest limit, riders at Focus 1–2, passives with no
  cost and no hard control. Each was priced by the generator's 05.11 budget (T-05-9 units, value within 2 of its
  allowance) and passed its id, hook, slot, condition, flag, band, duration and lint checks (ERRORS: 0). Every
  `ab.*` and `rit.*` cross-reference in the file resolves (scripted check; spot-checked with `rq.py`). No
  duplicate id, name or `mod_group`.
- **Guard against regression:** `gen_data05.py` coverage now errors on a level-2 tag lacking `min_tier` 4 or 5.
  Validator check 11 `POOLS` reports nodes lacking either tier (it used to report only "no 4+").
- **Pipeline:** `gen_data05.py --emit`, `integration-merge.py` (owner blocks restored, verified), `tables05.py`
  (T-05-12 and T-05-14 rewritten from data; `--check` same), `05-ladder-check.py` (183 callings, 0 failures;
  output committed). Ch.08's item-ability pool reads abilities.yaml: `08-gen_data08.py` run in a scratch copy,
  only `gen_item_ability.yaml` changed (162 → 279 entries, additions only) and was copied in.
- **Result:** pool 389 entries (302 tag-gated, 57 oath, 3 branch workings, 27 absorbed); per branch, tiers 4 and
  5 now equal the branch's node count. `POOLS`: 0 of 81 nodes lacking tier 4 or 5 (was 61 / 62); 0 of 132
  deed-keyed specialists without an own-pool tier-5 ability (was 92).
- **Text updated:** ch.05 reading line (pool count), bet 1, 05.11.6 (count, new coverage bullet, "a narrow
  calling sees its own three to five"), the interface-note coverage item, OEQ-05-6; 08.4.3 pool count. DL-05-38.
- **Re-checked, unchanged:** `12-world-seed.py` output and example (byte-identical), `08-loot-sim.py` (byte-identical
  to a run on HEAD data), `09-gen_data09.py` and `16-gen_data16.py` (pass; the merge restores `adversaries.yaml`).
- **Housekeeping:** the committed `08-loot-sim-output.txt` was stale before this row (missing its last three
  lines; a run on HEAD data prints them). Refreshed it; the content did not change.
- **Still INFO by design:** 122 of 132 specialists have fewer than six own-pool abilities. A narrow calling's own
  pool is one level-2 subtree, now 3 to 5 entries (7 for `primal.elements`). Kin picks stay legal (04.8.4). Six
  per node would mean about 250 more abilities, and 05.11.6 says not to grow the pool past its floor.

## Close-out
- `integration-assemble-appendix.py` re-run (decision-log gains DL-05-38; no trace fragment changed).
  `12-compile_anchors.py`: 129 anchors, 0 errors, 0 warnings. Validator: 0 ERROR / 0 WARN (INFO: POOLS 2,
  REFS-EX 9, REFS-MD-EX 70).
- Ledger: I-087 marked resolved (C2b, C2c), with evidence.
- New ledger rows: none.
