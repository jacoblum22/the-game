# R2-K report: spec 027 rules side (round-7 cleanup)

Revision R2-K. Rule edits tagged `[revision: R2-K]`. Source: specs/027-round7-cleanup/spec.md (owner decisions
2026-10-09/10: "I agree B, A, A, C"; hand-offs H1, H4, H9). Ids: DL-12-122..DL-12-125, DL-01-46 (confirmed),
DL-12-118 (confirmed); ledger I-220..I-226. Appended after every step.

## Progress
- Setup: read CLAUDE.md, spec 027 spec.md, cases.md (C9, C28), tasks.md T2. Looked up DL-12-99, DL-12-113,
  DL-12-118, DL-12-121, DL-01-46; ledger tail (I-215..I-219).
- Survey: read by id 12.14.11, 12.11.3, 12.2.4 (profiles item, Narrator row), 12.4.3 item 1, 00.6.6a item 5,
  PR-12-11 step 3, 01.7.4, 12.15 (order), 12.15.2 (Auto-commit line), 12.16.9, `world_seed.yaml#tbl.12.seed.haven_site`,
  WE-01-2, 01.15.1, 01.15.8, 01.8.1, WE-12-11, DL-12-109, DL-12-114, 01.6.10, `resolution.yaml#reach_flags`,
  `#take_the_time`. Evidence checked in specs/023..026 implementation-results.md. Findings: no rule text says the
  haven gate takes the site feature's name (only 12-world-seed.py line 546, the lead's); resolution.yaml is
  hand-written (no generator writes it; `reach_flags` has no engine reader); WE-01-2's ORACLE step and both branches
  ask the Oracle about the beat's own target (01.15.1), not only branch B; WE-12-11 step 6 lists the harbour gate as
  "quay" (the seed example names the gate after the feature, DL-12-125 changes that).
- Rules edits (scratchpad r2k027_rules.py, exact unique matches): 12.14.11 (setting once extended to people and
  things, DL-12-122), 12.2.4 (profiles item; Narrator row), 12.11.3 (pointer), PR-12-11 step 3 (`reframe` note,
  DL-12-123), 12.15 order item 3 and 12.15.2 Auto-commit line (DL-12-124), 01.7.4 ("above the passage"), 12.16.9 (gate
  name, DL-12-125), WE-12-11 steps 6 and 13, WE-01-2 (PARSE no longer queues the target's family to the Oracle; both
  branches read his record; branch B has no snag: +1 vs 11, 10+ 55%, critical failure 5%; *Why* rewritten), 01.4.4
  (DL-01-46 no longer provisional), `resolution.yaml` (`take_the_time.fallback` comment; `reach_flags.whole.tie_break:
  true`), `world_seed.yaml` (comment on `tbl.12.seed.haven_site` `feature`). One fix by hand: a newline the script put
  inside WE-12-11's table row was removed. The lead's 12-world-seed.py change (gate named "the gate", described "the
  gate, by <feature>") matches 12.16.9.
- Decisions and ledger (scratchpad r2k027_dl.py): DL-01-46 owner-confirmed (title, Owner ruling with the quote, the
  "owner picks another option" revisit clause dropped); DL-12-99 pointer line; DL-12-113 "Revisited" (spec 024 live
  run); DL-12-118 confirmed (title, "Revisited" with the quote, Revisit if extended); new DL-12-122 (B), DL-12-123 (C),
  DL-12-124 (auto OFFER above the passage), DL-12-125 (gate name). Ledger I-220..I-226 appended; I-214's resolution
  points to I-221. Appendix re-assembled (integration-assemble-appendix.py).
- Anchors compiled (12-compile_anchors.py: 129 anchors, errors 0, warnings 0). Exit gate: validate_ruleset.py
  0 ERROR / 0 WARN; INFO: BASIS 1, POOLS 2, REFS-EX 9, REFS-MD-EX 70.
- For the engine lead: engine/build/compile_cards.py not run (lead runs it last). 12-world-seed.py's gate change
  (the lead's) matches 12.16.9 / DL-12-125; WE-12-11 step 6 now says "the gate (by the quay)", which matches the
  committed example once the lead's re-run of the seed lands. No pacing.yaml key was added for DL-12-122 (no
  counter or flag by design; the rule is about when data is shown).
