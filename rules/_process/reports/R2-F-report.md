# R2-F report: scene state from resolved beats (T-12-18)

Revision R2-F (rules half). Rule edits tagged `[revision: R2-F]`; decision DL-12-77. The data
(`pacing.yaml#details.scene_writes`) was written by the engine session and is not changed here.
Appended after every step.

## Progress
- Step 0 (read): `pacing.yaml#details.scene_writes`; 00.6.6a, 12.11.9, 12.4.8, 12.14.13, 12.3.1 (position row),
  06.3.5, 06.5.2, 06.5.3, PR-06-4, `tbl.npc_action`; DL-12-72's format; R2-E report.
- Steps 1-6 (rules, one scratch script with asserted unique matches): ch.12 table index row T-12-18; T-12-18 added
  at the end of ch.12's Tables (beats by verb x degree band with position/actor/target columns; the posture-is-not-
  a-condition note; responses table and practice rows generated from the yaml so they cannot drift); 12.11.9
  steps 1 and 3; 12.4.8 step 8 (bands cleared at scene end); 12.14.13 T1c row; 12.3.1 position row (one clause);
  ch.00 00.6.6a item 4 (cites T-12-18, the PC included; record-line slots cited, never improvised).
- Step 7 (DL): DL-12-77 in `appendix/fragments/DL-12.md` after DL-12-76; appendix re-assembled with
  `rules/_process/simulation/integration-assemble-appendix.py` (decision-log carries DL-12-77; traceability lists
  no R2-E/R2-F DLs, unchanged in kind).
- Step 8 (close-out): anchors 129 / 0 errors / 0 warnings; validator 0 ERROR / 0 WARN (INFO only).

## Notes for the orchestrator (data, not changed)
- Grapple reach 3 writes "pinned by {actor}", but 06.5.2's ladder is 3 -> `restrained`, 4 -> `pinned`.
- No row clears `held` on a disarm (06.5.4); 00.6.6a item 4's old disarm example was dropped, DL-12-77 names it.
- Force reach 1 writes "off balance" on any success (matches 06.5.3's `cond.off_balance`); a reach-2 push one
  band away also keeps "off balance".
- Step 9 (follow-up, coordinator revised the data for notes 1 and 4): T-12-18's beats table now matches the data
  exactly: Grapple success rows reach 1-2 grip, reach 3 restrained, reach 4 pinned; Force success writes manner on
  guard, posture off balance at reach 1 only (`reach_max: 1`), down on the ground at reach 2+ with a knock-down; the
  row-selection sentence names `reach_min` and `reach_max`. Responses and practice rows unchanged in the data,
  checked. DL-12-77 kept as is (disarm stays in its Revisit if). Anchors 129 / 0 / 0; validator 0 ERROR / 0 WARN.
- Step 10 (follow-up 2, data revised again): Force success writes no "off balance" (manner, plus down on the
  ground at reach 2+ with a knock-down); `reach_max` dropped from T-12-18 and from the yaml comment. Responses are
  manner-only except where the body acts (rows 1-2, fight/crowd physical rows, work row 2): T-12-18's responses and
  practice tables regenerated from the yaml; 12.11.9 step 3 reworded (talk alone never changes the activity);
  DL-12-77 decision and evidence updated; appendix re-assembled. Anchors 129 / 0 / 0; validator 0 ERROR / 0 WARN.
- Step 10 (engine session, after the live run): 12.3.1 `position` row gains the common-noun and direction clause; DL-12-77 gains the live result; appendix re-assembled; anchors recompiled; validator 0 ERROR / 0 WARN.
- Step 11 (owner ruling, 2026-10-08): fine placement is T0 atmosphere, never stored or judged; only coarse position (place, band to the PC, held/pinned, mounted, arriving/leaving) is a claim. DL-12-77 records the ruling with the owner's words; 12.3.1 position row and 12.14.13 T0 row edited; 00.6.6a's slot list has no fine-placement slot (unchanged). Engine: claims `_coarse`.
