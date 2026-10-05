# Integration Report — Wave 3 → Wave 4

Single integrator agent. Rollback point: scratchpad `rules-snapshot-pre-integration` (untouched).
Work list: `_process/INTERFACE-REQUESTS.md` (all sections), `_process/issue-ledger.md` (I-023, I-024, I-026,
I-027 and every item marked integration), BRIEF §12 + Addenda, AUTHOR-BRIEF §3.

Progress notes are appended per step as work completes, so an interruption loses nothing.

## Progress log

- [started] Read BRIEF §12/Addenda, AUTHOR-BRIEF §3, INTERFACE-REQUESTS (full), issue ledger, 00 in full,
  SCHEMAS, every chapter's Interface-requests section. Inventoried all 41 contrib fragments.
- [step 1, part A — done] 00-architecture.md: 56 exact-match amendments applied by
  `scratchpad/integ/edit00.py` + `edit00b.py` (each asserted to match once); T-00-9 regenerated from the merged
  registry (105 handlers, 25 boundary rows); SCHEMAS.md (21 edits), scales.yaml (3), substrate.yaml (14),
  effects.yaml core (3). Details in "Step 1" below.
- [step 2, part A — done] boundaries.yaml rebuilt from seeded rows + 13 contrib owner-blocks (105 handlers, 0
  duplicates; 03/04 reserved-row wording applied; one defect fixed: `h.10.watch_check.rule_id` parsed as the
  number 10.9, now the string "10.9"). Ten canonical files received owner-blocks by text merge (entries
  preserved byte-for-byte, verified by parse + deep equality): effects (10 blocks, 38 entries), licenses (5/30),
  composites (1/32), conditions (1/6), factions (1/19), adversaries (1/33), origins (1/2), kits (1/2), hazards
  (1/2), calendar (1/1). YAML anchors in the 13 fragments renamed per fragment to stay unique. tags.yaml: 31 of
  31 proposals adopted (832 → 863 tags); 29 `trait.*` rows now cite T-01-13; `terrain.road.bridge` narrowed
  (DL-INT-03). All 42 fragments moved to `_process/merged-contrib/`; 66 path references in chapters, appendix
  fragments and data headers re-pointed to the canonical owner-blocks.
- [step 3, part A — done] Integration edits applied (each with an `[integration: …]` citation; every edit an
  exact unique match, logged): 01 (15 edits incl. I-024), 03 (9 + evidence.yaml 6 + index tables T-03-1/T-03-12
  for the 31 adopted tags), 04 (11), 05 (3 + composites.yaml cone/spread_form_map, rituals.yaml rit.imbue,
  abilities.yaml "in place of Fend" ×8), basic_verbs.yaml Handle (2), 06 (13), 07 (6), 08 (2), 09 (4).
  Generator scripts in `_process/simulation/` repointed from `data/contrib/` to `_process/merged-contrib/` (13
  scripts) so they stay runnable. Remaining: 10, 11 (I-026), 12, 13, 15, 16; I-027 audit.
