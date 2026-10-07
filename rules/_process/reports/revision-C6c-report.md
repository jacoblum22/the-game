# Revision C6c report: card-level basis tags, ch.09-10 (I-065)

Agent C6c. Row: I-065 (BRIEF §6: every rule cites its basis as `[C:]`, `[R]` or `[DL-]`). Scope: ch.09 and 10 only
(ch.08, 11 and 12 were being edited by other agents in parallel).
Status: **partly resolved, left open**. Ch.08, 11, 12, 15 and 16 remain.

## I-065

**Method.** C6a's and C6b's method, unchanged (DL-INT-13):
- `basis_audit.py` lists the untagged cards in each chapter.
- One `{card: basis}` map per chapter, `rules/_process/basis/C6c-09.py` and `C6c-10.py`, is applied by
  `apply_basis.py`. It asserts one match per card, is idempotent (a second run tagged 0), and re-audits the chapter.
- The tag is `[<basis>; revision: I-065]`, placed after the card's kind tags.

Each card was read through `rq.py`'s index before it was given a basis. Bases come from:
- the DL-09 or DL-10 entry whose Decision names the card or its section;
- the ch.06/07 decision the card applies to adversaries or to the land (mobs DL-06-20, attention order DL-06-16,
  morale clock DL-06-18, size DL-06-30, reduction cap and hazard rungs DL-07-14, Two-Key DL-07-01, lethal warning
  DL-07-02, defeat table DL-07-19, afflictions DL-07-17, want DL-07-21);
- the DL-00/DL-00A decision it fixes (time modes DL-00A-12, clocks DL-00A-20, verbs and licenses DL-00A-19, state
  DL-00A-22, cards and anchors DL-00A-24);
- the constitution clause the trace fragment maps the card to;
- for ch.10, the R5 completeness row trace-10 maps the section to (EX-01 travel, EX-02 navigation, EX-03 roles,
  EX-04 weather, EX-05 hazards, EX-06 foraging, EX-07 wilderness structure, EX-08 site crawl, EX-09 light, EX-10
  search, EX-13 discovery, EX-14 spatial description, AV-06 tables, AV-08 traps, HR-07 deprivation, EQ-09 supply and
  light, EQ-10 mounts and vehicles, X-05 real-time light excluded), and R6 B-15 for 10.2.4's West Marches rings.

No basis was guessed.

**Counts at re-count.**

| Chapter | Untagged | C6a's count |
|---|---|---|
| 09 | 50/76 | 50/76 |
| 10 | 83/104 | 82/102 |

All 133 are now tagged.

**Card with no recorded basis.** One, and it now has a DL entry:
- **DL-10-31** covers 10.1.6: a place's `settlement_scope` is the market its seed names, else the nearest settlement
  by route watches, and `null` past 8 travel watches. The field answers 03's interface request and feeds DL-03-09's
  public tally and DL-11-15's reputation. The 8-watch line is recorded honestly as an unmeasured default (four days'
  walk on 10.3.3's default day), with a revisit trigger.

It did not look unjustified, so no new ledger row. No card's only honest basis was a derivation, so DL-INT-13's
fifth form (`[derived:]`) was not needed.

**Appendix.**
- `basis/C6c-appendix.py` (idempotent) adds DL-10-31, extends DL-INT-13's evidence, and adds BRIEF §6 rows to
  trace-09 and trace-10.
- `decision-log.md` and `traceability.md` were re-assembled with `integration-assemble-appendix.py`.
- The anchors were recompiled (129 anchors, 0 errors, 0 warnings; only source hashes moved).

**Validator.** `BASIS_CHAPTERS` is now 00-07, 09, 10. The INFO line reads "879 rule cards, 0 untagged". Full run:
0 ERROR / 0 WARN.

**Noticed, not changed.** DL-INT-13's "Revisit if" still names "the remaining chapters (00-03, 08-12, 15-16)"; left
as is so that the parallel C6 agents' edits to the same entry do not conflict. Whoever closes I-065 should update it.

**Handoff.** Remaining: ch.08, 11, 12, 15, 16 (C6a's counts 49/82, 38/113, 67/136, 57/104, 73/101; re-count first).
For each chapter: run `python rules/_process/basis_audit.py NN`, copy `basis/C6c-10.py`, fill in its map, write a
DL entry where no basis exists, add the chapter to `BASIS_CHAPTERS`. Close I-065 when the list holds 00-12 and
15-16 at 0 WARN.
