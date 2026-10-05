## DL-INT — Integration (Wave 3 → 4)

Decisions the integrator took while making the fifteen chapters one ruleset. None redesigns a rule: each applies
an approved amendment, resolves an ambiguity in the direction an existing rule already fixed, or records a
mechanical repair. Genuine design conflicts were logged as issues instead (`_process/issue-ledger.md`, I-029 to I-032).
Full record: `_process/integration-report.md`.

### DL-INT-01: Owner-block fragments are merged by text, entries preserved exactly, and stay re-mergeable
- Decision: every `data/contrib/<file>.NN.yaml` owner-block was inserted into its canonical file under `blocks:`
  (owner order) with the fragment's own header kept as comments; each merge was verified by parsing and deep
  equality against the fragment. `boundaries.yaml` was rebuilt from the seeded rows plus every owner-block (an
  owner's restatement supersedes 00's seeded row of the same id). The fragments moved to
  `_process/merged-contrib/`; the generator scripts that read or write them were repointed there, and
  `_process/simulation/integration-merge.py` re-applies every merge after any regeneration.
- Alternatives considered: re-dumping each file through a YAML library (loses comments and the authors'
  formatting); leaving fragments in `data/contrib/` (two places to read every owner's entries).
- Evidence: AUTHOR-BRIEF §3; 00.16.5; the merge log in the integration report.
- Serves: goal 2 (one canonical source per id; RC-DATA).
- Revisit if: a generator is re-run without the merge script (the validator then reports the missing ids).

### DL-INT-02: `terrain.road.causeway` is adopted as a level-2 tag
- Decision: ch.10 proposed it as level 3, but its parent `terrain.road` is a branch, so it is a level-2 child.
  00.5.5 lets 03 add level-2 children with a DL entry; this entry, written on 03's behalf at integration, is that
  record. The tag is already used by the region file; T-00-7 lists it.
- Alternatives considered: declining it (leaves a dangling tag in `region_thallen.yaml`); re-parenting it under
  `terrain.wetland` (renames a used id).
- Evidence: 00.5.5 rules 1–7 (all met); `tags.10.yaml` proposal.
- Serves: goal 2 (every place tag resolves).
- Revisit if: ch.03's revision prefers another parent (then retire with `superseded_by`).

### DL-INT-03: `terrain.road.bridge` no longer covers fords
- Decision: 00's seeded definition "Bridges and fords." overlapped the adopted `terrain.water.river.ford`; the
  bridge definition now reads "a way over a river, gorge or gap" and names the ford tag. The id is unchanged.
- Alternatives considered: two tags covering fords (violates SG-16's distinguishing-test rule).
- Evidence: 00.5.5 rule 4; SG-16; the ford proposal's own distinguish line.
- Serves: goal 2 (one classification per kind of place).
- Revisit if: never; a data entry tagged `bridge` for a ford is a data error.

### DL-INT-04: PR-10-8's word step is computed with the archetype's counter held
- Decision: the audit's advisory word is 09.6.4's `advisory_alone` (the reference PC carries the archetype's
  named counter); the no-counter word is printed beside it. Generic band-relative tables are audited at every
  home band 1–5 by `_process/simulation/10-word-audit.py` (issue I-027).
- Alternatives considered: the no-counter word (would bar every troll and wight from a table though their
  counters are discoverable lore, 09.10.2).
- Evidence: 09.6.4; 13's audit (DL-13-11) already used this convention.
- Serves: goal 2 (one reading of the budget for 13 and for 10's generic tables).
- Revisit if: playtests show players meeting counter-gated rows without the lore to find the counter.

### DL-INT-05: Within `interval` phase 2, affliction onset runs before site exposure (I-023)
- Decision: the registry order (owner chapter, then id) already runs `h.07.affliction_onset` before
  `h.10.site_exposure`; it is kept and stated in 00.7.5 and in `boundaries.yaml`'s header, so an affliction
  contracted in an interval first advances at the next one.
- Alternatives considered: a `before:` reversing it (would advance a fresh affliction in its first interval).
- Evidence: 07.9.3; 10.12.2; 00.7.5.
- Serves: goal 2 (no double-counted exposure).
- Revisit if: a hazard needs same-interval onset (then it should state an immediate stage, not reorder handlers).

### DL-INT-06: One order for multi-target shapes
- Decision: 05's spread tags and 06's shapes are one ordered list, 06's T-06-15: pierce, burst, cone, fork, chain,
  linger (cone inserted third by 06). 05.10.4 and `composites.yaml#spread_tags` now carry cone and the same order
  numbers, and `eff.05.spell_delivery` forms map to shapes (line → pierce, burst, cone, chain, zone → linger).
- Alternatives considered: two order lists differing only in numbering (an engine would have to choose).
- Evidence: T-06-15; 06's request to 05 (a); DL-05-17.
- Serves: goal 2.
- Revisit if: a sixth player-facing shape is added (amend both at once).

### DL-INT-07: The starter region's cases live in `investigation.yaml#cases`
- Decision: `case.silent_bells`, `case.orsolin_signet` and `case.treaty_of_the_ford` moved from
  `region_thallen.yaml#cases` (which now lists their ids) to `investigation.yaml#cases`, where 15's case rules
  read them; the graphs are byte-identical.
- Alternatives considered: two homes for cases (ids defined twice).
- Evidence: 13's Interface request to 15; 15.9.4.
- Serves: goal 2.
- Revisit if: regions grow enough cases to want a per-region file (then a `region_*.yaml#cases` schema section).

### DL-INT-08: T-00-9 is generated from `boundaries.yaml`
- Decision: the registry table in 00 is regenerated from the data file (105 handlers), which is canonical (00.1.4
  item 5); rows are boundaries, cells handlers by phase with any `before`.
- Alternatives considered: hand-maintaining a summary (it was already stale by 76 handlers).
- Evidence: 00.7.4; T-00-19.
- Serves: goal 2.
- Revisit if: never; regenerate on every handler change.

### DL-INT-09: 00.3.7's coherence paragraph and `advisory_by_difference` are retired, not deleted
- Decision: per the approved amendments from 06 and 09, both yield to T-09-9 / PR-09-4; the scale entry is kept
  with `lifecycle: retired` and `superseded_by` (00.16.3) so old records resolve.
- Evidence: IR ch.06 #7, IR ch.09 #3; DL-09-09.
- Serves: goal 2 (one advisory contract).
- Revisit if: never.

### DL-INT-10: WE-01-2's claim is "his long-lost sister" (I-024)
- Decision: Wren is a woman; the example now has her claim to be the guard's lost sister (his siblings, in the
  "no" branch, are two brothers), and 12.15.5's REDIRECT sample and 15's example label were aligned.
- Alternatives considered: keeping "brother" as an "outrageous claim" teaching point (the example's numbers
  treat the claim as plausible, so the text would contradict its own frame).
- Evidence: I-024; WE-01-2's frame (doubtful, not outrageous).
- Serves: goal 2 (examples that teach the rule they show).
- Revisit if: never.

### DL-INT-11: Every id prefix in use is registered in a generated table, 00.16.2a
- Decision: 00.16.2 names 53 prefixes, but the merged data defines ids under 90. The other 37 are file-local
  families such as `act.`, `cnt.`, `flag.`, `req.`, `standing.` and `wage.`. Under 00.16.2 every id's prefix
  must say which file defines it. So a registry table, 00.16.2a, is generated from the ids actually defined in
  `data/` by `_process/simulation/integration-prefix-registry.py`. Each row gives the prefix, the defining
  file(s) and the owning chapter, read from T-00-19. 00.16.2's prose list stays the core. The validator counts
  00.16.2 plus 00.16.2a as "registered" and reports any other prefix as an ERROR. A new prefix is added by
  re-running the script. The continuation session fixed the script's owner lookup for annotated file names
  (`callings.yaml#requirements`, `abilities.yaml (inline clock spec)`, `00-architecture.md#…`), which had
  printed "?" for `clk.`, `gen.`, `req.` and `tbl.`.
- Alternatives considered: (a) appending 37 prefixes to 00.16.2's prose by hand. That would be unreadable
  and stale at the next data change, the same failure DL-INT-08 fixed for T-00-9. (b) Renaming file-local
  ids under registered prefixes. That would rewrite authored data across a dozen files, beyond what
  integration may do.
- Evidence: 00.16.2 ("the prefix tells any reader which file defines them"); 00.1.4 item 5 (data is
  canonical); `validate_ruleset.py` § prefix registry; DL-INT-08 (the same pattern for T-00-9).
- Serves: goal 2 (every id resolves to one defining file; the engine can route any id by its prefix).
- Revisit if: Wave 4's audit finds a registry-only prefix that collides in meaning with a named one (then
  rename it in data, with `superseded_by`, and regenerate).
