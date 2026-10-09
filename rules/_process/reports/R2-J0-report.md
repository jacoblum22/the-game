# R2-J0 report: the working stance (constitution VIII)

Revision R2-J0. Rule edits tagged `[revision: R2-J0]`; decision DL-00-06 (owner direction 2026-10-08/09, quoted).
Constitution 2.0.0 → 3.0.0. Appended after every step.

## Progress
- Setup: worktree reset to milestone-1-playable (b9c4a1b). Read CLAUDE.md, the constitution, ROUND3/4/5-ANALYSIS.md,
  round6-investigation I1–I4 (untracked in the main checkout; read there). Baseline validator 0 ERROR / 0 WARN.
- Constitution: new Principle VIII (eight rules, what it keeps, what it supersedes or reinterprets, the Gemini
  caution, precedence); I tied to VIII; P3 and P13 AMENDED notes; Technology Constraints (closed choices only where
  code records; TODO(CROSS_FAMILY_CHECKER) withdrawn); Sync Impact Report; version 3.0.0.
- 00-architecture (12 asserted edits, scratch `r2j0_edit.py`): chapter summary; design intent (architectural bet,
  new "The working stance"); 00.1.1 AI DM row; 00.1.3; 00.1.4 (I–VIII); 00.1.5; 00.2.1 P-A scope; 00.12.7; 00.13.1;
  00.15.1; 00.15.4. 00.15.4 keeps the six core ids, so `CardIndex.core()` is unchanged.
- DL-00-06 in the decision log's DL-00 head; VIII row in `fragments/trace-00.md` (status partial: engine packets
  still carry cards to every role); VIII added to the assembler's clause list and clause regex.
- Re-assembled the appendix, compiled anchors (0 errors, 0 warnings), compiled cards last. Validator: 0 ERROR /
  0 WARN. Card/packet tests: 50 passed.

## Follow-up (not done here; engine code untouched)
- Align `engine/dm/packet.py` with 00.15.1/00.15.4: the situation plus short per-role guidance (I4 Part A).
- Validate the loosened areas on Gemini Flash.
