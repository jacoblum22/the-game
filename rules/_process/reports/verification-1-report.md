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
