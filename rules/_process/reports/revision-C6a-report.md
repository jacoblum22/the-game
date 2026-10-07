# Revision C6a report: card-level basis tags, ch.04-07 (I-065)

Agent C6a. Row: I-065 (BRIEF §6: every rule cites its basis as `[C:]`, `[R]` or `[DL-]`). Scope: ch.04, 05, 06, 07.
Status: **partly resolved, left open for C6b** (ch.00-03 and 08-16 remain).

## I-065

**Design.** The ledger's first proposal was to accept section-level basis plus derivation references as meeting
§6. Rejected (DL-INT-13): `rq.py` shows one card at a time, so a basis stated only in a section intro is invisible
at the point of use, and a derivation reference names a dependency, not a reason. Every card now carries its own tag.

**Audit.** `rules/_process/basis_audit.py` (uses `rq.py`'s index). A rule card is an index entry of kind `card`
with an `NN.S.R` id; a basis tag is a bracket group containing `C:<clause>`, `R<n>`, `R:` or `DL-…`, which may wrap a
line. Prose mentions ("(BRIEF §4; C:VII)") do not count. Result before C6a: ch.04 21/65, 05 34/89, 06 77/99,
07 56/89 untagged (188 of 342). The constitution audit's 216 for 04-08 used a one-line match.

**Edits.** One script per chapter, `rules/_process/basis/C6a-04.py` … `C6a-07.py`, each a `{card: basis}` map
applied by `apply_basis.py`. The tag `[<basis>; revision: I-065]` goes right after the card's kind tags. The script
asserts exactly one match per card, is idempotent (a second run tags 0), and re-audits the chapter. Basis sources,
in order: the DL whose Decision names the card, a range holding it, or its section; the constitution clause the
chapter's trace fragment maps the card to; the research row the trace maps the section to (R5 CF-01…CF-14 for 06,
R5 HR-01…HR-09 and CF-10 for 07, R6 A-07/A-21/V7/R-A5 for 04's triggers and events, R1 §06/§09 where the chapter
cites them). Each card was read before it was assigned a basis. No basis was guessed.

**Cards with no recorded basis.** There were two, and both now have DL entries:
- DL-05-41 covers 05.6.11 (consumables restore at most 4 Focus between long rests).
- DL-06-30 covers 06.3.10 (the six-rung size ladder and its five effects).

Neither looked unjustified, so no new ledger row was opened.

**Also fixed.** 05.8.6 still said "until ch.04 agrees", but 04.8.4 had already adopted the promotion request. The
sentence now says so.

**Appendix.**
- DL-INT-13 records the convention.
- A BRIEF §6 row was added to each of trace-04 … trace-07, through `basis/C6a-appendix.py`.
- `decision-log.md` and `traceability.md` were re-assembled.
- The anchors were recompiled (only the source hashes changed).

**Validator.** New check 12, BASIS, WARNs on each untagged card in `BASIS_CHAPTERS = ["04", "05", "06", "07"]`. A
later agent extends the list as chapters are done. Its INFO line reports "342 rule cards, 0 untagged". Full run:
0 ERROR / 0 WARN.

**Handoff to C6b.** These are the remaining counts at C6a's base. Ch.08-16 were being edited in parallel, so
re-count them before starting:

| Chapters | Untagged cards |
|---|---|
| 00 / 01 / 02 / 03 | 37/113, 61/121, 21/60, 22/63 (141 in all) |
| 08 / 09 / 10 / 11 / 12 / 15 / 16 | 49/82, 50/76, 82/102, 38/113, 67/136, 57/104, 73/101 (416 in all) |
| 13 | 72/77 (not edited, stays out of BASIS) |

Method for each chapter:
1. Run `python rules/_process/basis_audit.py NN`.
2. Copy `basis/C6a-07.py` to `C6b-NN.py` and fill in its map.
3. Write a DL entry where no basis exists.
4. Add the chapter to `BASIS_CHAPTERS`.

Close I-065 when `BASIS_CHAPTERS` holds 00-12 and 15-16 at 0 WARN. DL-INT-13's revisit clause names the one open
design question: if a card's only honest basis is a derivation, admit `[derived: NN.S.R]` as a fifth form in 00.1.6.
