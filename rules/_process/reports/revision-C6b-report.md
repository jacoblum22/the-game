# Revision C6b report: card-level basis tags, ch.00-03 (I-065)

Agent C6b. Row: I-065 (BRIEF §6: every rule cites its basis as `[C:]`, `[R]` or `[DL-]`). Scope: ch.00, 01, 02, 03.
Status: **partly resolved, left open**. Ch.08-12 and 15-16 remain.

## I-065

**Method.** This is C6a's method, unchanged (DL-INT-13):
- `basis_audit.py` lists the untagged cards in each chapter.
- One `{card: basis}` map per chapter, `rules/_process/basis/C6b-00.py` … `C6b-03.py`, is applied by `apply_basis.py`. It asserts one match per card, is idempotent (a second run tags 0), and re-audits the chapter.
- The tag is `[<basis>; revision: I-065]`, placed after the card's kind tags.

Each card was read through `rq.py` before it was given a basis. Bases come from three places:
- the DL-00 or DL-00A architecture decision that the card fixes or applies (DL-00A-02 frame, -07 attributes, -11 severity/stakes/reach, -12 time, -19 licenses and verbs, -20 clocks, -21 conditions, -22 state, -23 tools, -24 cards);
- the DL that names the card or its section;
- the constitution clause the trace fragment maps the card to.

No basis was guessed.

**Counts before C6b.** 141 of 357 cards were untagged, the same as C6a's handoff:

| Chapter | Untagged |
|---|---|
| 00 | 37/113 |
| 01 | 61/121 |
| 02 | 21/60 |
| 03 | 22/63 |

All 141 are now tagged.

**Repo-artifact bases.** Six ch.00 cards restate the orchestration brief:
- 00.1.2 (chapter map, §A1)
- 00.16.1, 00.16.2, 00.16.4 and 00.16.5 (data conventions, §12)
- 00.17.2 (chapter contracts, §9/§A1)

These cite it as `[R: rules/_process/BRIEF.md §N]`, which is 00.1.6's repo-artifact form. 00.16.2 and 00.16.5 also cite DL-INT-11 and DL-INT-01.

**Cards with no recorded basis.** There were two, and both now have DL entries:
- **DL-00A-33** covers 00.1.3: reading order follows dependency, not chapter number. Ch.00's DL entries live in the hand-written head of `decision-log.md`, above the assembly marker, so the entry is inserted there.
- **DL-01-28** covers 01.7.4: auto-commit only for frames that are Safe or Risky, not lethal, not secret, carry no mode price, and show at least 50% odds. Each exclusion restates an existing rule. The 50% line is recorded honestly as an unmeasured default, with a revisit trigger.

Neither looked unjustified, so no new ledger row. No card's only honest basis was a derivation, so DL-INT-13's fifth form (`[derived:]`) was not needed. Pointer cards (00.8.7 "See PR-00-3", 01.14.2, 03.10.6 "See 03.4.6") carry the basis of the decision they point to.

**Appendix.**
- DL-INT-13's evidence was extended.
- BRIEF §6 rows were added to trace-00 … trace-03, through `basis/C6b-appendix.py`.
- `decision-log.md` and `traceability.md` were re-assembled.
- The anchors were recompiled.

**Validator.** `BASIS_CHAPTERS` is now 00-07. The INFO line reads "699 rule cards, 0 untagged". Full run: 0 ERROR / 0 WARN.

**Noticed, not changed.** 00.1.1, 00.1.3 and 00.1.2 name a ch.14 (Player's Guide) that has no file in `rules/`. This is outside I-065's scope and is presumably known, so no row was opened.

**Handoff.** These are the counts at C6a's base. The chapters were being edited in parallel, so re-count them first:

| Chapter | Untagged |
|---|---|
| 08 | 49/82 |
| 09 | 50/76 |
| 10 | 82/102 |
| 11 | 38/113 |
| 12 | 67/136 |
| 15 | 57/104 |
| 16 | 73/101 |

That is 416 in all. Ch.13 stays out. For each chapter:
1. Run `python rules/_process/basis_audit.py NN`.
2. Copy `basis/C6b-03.py` and fill in its map.
3. Write a DL entry where no basis exists.
4. Add the chapter to `BASIS_CHAPTERS`.

Close I-065 when the list holds 00-12 and 15-16 at 0 WARN.
