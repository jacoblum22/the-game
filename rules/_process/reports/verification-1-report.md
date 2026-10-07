# Verification-1 report (Wave 4)

Agent: Verification-1 (Opus). Scope: FINISH-PLAN.md order-of-work item 3, audits 1–5 (constitution compliance,
cross-chapter consistency, completeness against R5, exploit red team, citation verification; closes I-010,
I-012, I-014, I-021). Appended after every step. Edits are tagged `[verification: V1-NNN]`; design-level
findings become ledger rows from I-037 with status "open (Revision C)".

## Step 0: baseline (2026-10-05)
- Read FINISH-PLAN.md, revision-B-report.md, issue-ledger.md (I-001..I-036), BRIEF §6 and §8.
- Validator baseline: `python _process/validate_ruleset.py`: 0 ERROR / 0 WARN, 81 INFO.
- Scratch notes: session scratchpad `verif1/` (not committed).

## Step 1: single-pass read, chapters 00–03 (in progress)
- Read 00, 01, 02, 03 in full; notes in scratchpad `verif1/notes.md`. Every worked-example number in WE-00, WE-01,
  WE-02 and WE-03 recomputed: all agree with the current rules except Wren's Vitality (see below).
- Found so far (fixes and ledger rows follow in Step 4): Wren's Vitality is 13 after her Bent (02.7.1, PR-02-5),
  but 01's sheet and WE-01-3 use 12 and 02's interface note says 00 shows 12 (00 was already corrected); T-00-7
  omits the two level-2 deed tags 03.1.3 added (`craft.scribing`, `influence.teaching`); 00.11.3 step 7's
  doubled-then-halved weights are not what WE-00-2's log shows; traceability's "Open issues" column is a
  hard-coded list of rows that are now resolved; red-team candidates: free Oracle lever-fishing (01.15.8),
  contest-band peaks from minor faction functionaries (03.4.3).

## Step 2 (resumed 2026-10-06, Sonnet): task 1, fixes for the ch.00-03 findings
Mechanical, exact-match edits tagged `[verification: V1-NNN]`:
- V1-001 Wren Vitality 13 (12 + Endurance +1 after the Bent): 01 header, WE-01 sheet line and WE-01-3's V track (13 > 12 > 11 > 10 > 9; without the license V 3); 02's WE-02-1 parenthetical and interface note 00-3 (marked met); 05 WE-05-5's traced fight (13 > 10). 06, 07 and 12 traces still use 12: ledger I-042.
- V1-002 WE-00-2: weights now shown doubled first (4 x 1/2 = 2 / 4 / 2, total 8, still 25/50/25), log "weights 2/4/2", matching 00.11.3 step 7.
- V1-003 T-00-7: added `deed.craft.scribing` and `deed.influence.teaching` (script check against tags.yaml: those were the only two of 342 level-2 ids missing).
- V1-004 WE-05-5: the Ash "spends none (a staff)" row labelled as the pre-05.7.11 staff model; reading (3) rewritten to cite J2 (Spent caster 80.7-91.0%).
- V1-006 04.5.6: the dangling "issue I-028" pointer now names I-037.
- V1-007 `integration-assemble-appendix.py`: `ISSUES` ("Open issues" column of traceability.md) rebuilt from open ledger rows; appendix re-assembled.
- Checked and dropped from the notes: T-00-9's dying check on both `turn_end` and `round` is not a double advance (the `round` row is for a Dying character outside a conflict, boundaries.yaml h.07.dying_check).
Design-level findings became ledger rows (see the ledger): I-037 (power_band two ways, MAJOR), I-038 and I-039 (red team, MAJOR), I-042 to I-044, I-046.

## Step 3: task 2, consistency pass on ch.04-12, 15, 16 (ch.13 skipped)
- Method: a script listing every cited rule id, table id, PR, OEQ and DL that has no definition (all clean; the 14 hits were research citations such as "R3 04.12", not rule ids); targeted greps for the figures revisions A and B changed: casting baseline (no stale "helpless caster" claim outside 06's dated I-006 note and the V1-004 fix), non-combat parity (03.4.3, 15.3.11, 15.9.20, 08.6.4 consistent), drop rates (08 worked examples WE-08-1 and WE-08-3 still used the pre-retune 20% and 35% checks: fixed as V1-005, now 15% and 30%), encounter tables (band shares 30/55/15 agree across 09, 10, 12), world sim (11.3.9, T-11-24, OEQ-11-1 agree with the Revision B run), 00.4.4 derived-value uses (06.2.2, 08.9, 16.2.1, 07.11 agree).
- Found and logged: I-045 (04/09 pacing mix assumes hard 30% / lethal 5%; shipped tables 8.2% / 0%), I-046 ("brink" has two meanings), I-037.
- Not exhaustively read: ch.04-12, 15 and 16 were checked by script and by targeted greps on the Revision A/B figures, not read in full; the playtest read the procedures it used (12.2, 12.13, 15.3-15.4, 15.10, 10.3, 10.9-10.10, 06.1-06.4, 06.10-06.11, 07.2, 11.2-11.3, 05.6-05.7).

## Step 4: task 3, completeness
`verification-completeness.md`: 189 R5 rows mapped to rule ids: 175 covered, 7 pending ch.14, 5 partial, 2 missing (FN-11 versioning, FN-12 credits). BRIEF section 8: all 10 deferred items resolved (item 9 with one open question, I-043). Ledger: I-049, I-050, I-051.

## Step 5: task 4, red team
`verification-redteam.md`: ten exploits; three gaps (I-038 Oracle lever-fishing, I-039 contest band, I-041 daily rematch and loot), two partial (I-047, I-048), five stopped with citations.

## Step 6: task 5, paper playtest
`verification-playtest.md`: Evella Elderward in the High Fells seed; creation, social scene, exploration leg, two fights including a Spent caster, an injury, downtime, a world turn, a freeform action. Ledger: I-040 (MAJOR: audit reference PC), I-052 to I-062 (MINOR).

## Step 7: task 6 and close-out
- I-010, I-012, I-014 and I-021 closed: "accepted: claims cited to the research digests (owner cost decision 2026-10-06)".
- Ledger now runs to I-062; 26 new rows (I-037 to I-062): 5 MAJOR (I-037, I-038, I-039, I-040, I-041), 21 MINOR, all "open (Revision C)".
- `python _process/validate_ruleset.py`: 0 ERROR / 0 WARN (81 INFO). `12-compile_anchors.py`: 129 anchors, 0 errors, 0 warnings (anchors.yaml recompiled after the 08 and 05 text edits). Appendix re-assembled. Nothing committed.
