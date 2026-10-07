# Revision C6d report: card-level basis tags, ch.15-16 (I-065)

Agent C6d. Row: I-065 (BRIEF §6: every rule cites its basis as `[C:]`, `[R]` or `[DL-]`). Scope: ch.15 and 16 only
(ch.08, 11 and 12 were being edited by other agents in parallel).
Status: **partly resolved, left open**. Ch.08, 11 and 12 remain.

## I-065

**Method.** C6c's method and tools, unchanged (DL-INT-13):
- `basis_audit.py` lists the untagged cards in each chapter.
- One `{card: basis}` map per chapter, `rules/_process/basis/C6d-15.py` and `C6d-16.py`, is applied by
  `apply_basis.py`. It asserts one match per card, is idempotent (a second run tagged 0), and re-audits the chapter.
- The tag is `[<basis>; revision: I-065]`, placed after the card's kind tags.

Each card was read through `rq.py`'s index before it was given a basis, and every cited DL id was checked to exist in
`decision-log.md`, and every R5 row in R5's tables. Bases come from:
- the DL-15 or DL-16 entry whose Decision names the card or its section;
- the other chapter's decision the card applies. For example: DL-06-01/19 (companions' 0 actions and Command),
  DL-06-07/16/22 (Flank, attention order, Fend), DL-01-24 (Help), DL-07-11/13/15/19/20 (rest, Treat, dread, defeat,
  bleeding out), DL-09-18 (minds), DL-02-12 (tongues), DL-11-11/13/15/18/19 (rumors, attention, reputation,
  teachers, holdings), DL-12-10/11/12/13 (starting standing, lead injection, spotlight facets, NPC depth and
  memories), DL-08-14/16/19/20 (attunement, crafting, labor cap, lifestyles), DL-00A-10/11/20/22/27;
- the constitution clause the trace fragment maps the card to;
- the R5 row trace-15 maps the section to (NP-03 15.1, SO-01 15.3-15.4, SO-03 15.7.1-15.7.4, SO-07 15.7.6, EX-11
  15.9, TM-06 15.10-15.13, AD-05 15.11.4, MG-04 15.13.4);
- the R5 row that names the card's subject (SO-04 languages, SO-06 rumors, LW-14 notoriety, NP-05 companions, NP-06
  NPC voice, EQ-10 mounts, and G-3, the companions gap that 16.12.1 already cites);
- R6 D-R4 for 16.16.1, which its prose already cited without a bracket.

No basis was guessed.

**Counts at re-count.**

| Chapter | Untagged | C6a's count |
|---|---|---|
| 15 | 57/104 | 57/104 |
| 16 | 73/101 | 73/101 |

All 130 are now tagged.

**Rules with no recorded basis.** Four cards, now covered by two new DL entries:
- **DL-16-25** covers three cards:
  - 16.3.7, the three roads by which a beast joins: bought at Neutral, bonded by `rit.beast_bond` at Friendly, or
    tamed at Wary by a 6-segment project clock;
  - 16.15.2, the four temperaments;
  - 16.15.5, the familiar as a band-1 beast at Friendly.

  The taming clock's 6 and the d4 temperament roll are recorded honestly as unmeasured defaults, with a revisit
  trigger.
- **DL-16-26** covers 16.6.5: an ally whose joining want is fulfilled stays at Friendly or warmer, and leaves
  content at Warm or below. That line is read from DL-16-08's regard ceiling and 16.12.2's confiding rung.

16.3.7 carried a C:III trace mention, but only for its `[J:flag]`'s Worst case line, not for the roads or the
standings, so it was given a DL entry rather than tagged C:III alone. None of these rules looked unjustified. No card's
only honest basis was a derivation, so DL-INT-13's `[derived:]` form was not needed.

**Appendix.**
- `basis/C6d-appendix.py` (idempotent) adds DL-16-25 and DL-16-26 to `fragments/DL-16.md`, and adds BRIEF §6 rows to
  trace-15 and trace-16.
- DL-INT-13 was **not** edited, as instructed.
- `decision-log.md` and `traceability.md` were re-assembled with `integration-assemble-appendix.py`.
- The anchors were recompiled (129 anchors, 0 errors, 0 warnings; only source hashes moved).

**Validator.** `BASIS_CHAPTERS` is now 00-07, 09, 10, 15, 16. The INFO line reads "1084 rule cards, 0 untagged". Full
run: 0 ERROR / 0 WARN.

**New row I-105 (MINOR, ch.16).** A tamed beast joins at Wary (16.3.7; PR-16-1 step 6). 16.6.2 and PR-16-7 step 1 start
the 4-day departure clock when standing "becomes Wary". If joining counts as becoming Wary, every tamed beast leaves
in four days: beast regard ticks at most +2 a week on a 6-segment clock, so it cannot reach Neutral in time. A
hireling whose reaction roll lands at Wary meets the same question. Left open. It is outside this row, and the fix
belongs to ch.16's owner. Its id was taken as the next number after I-097. If a parallel agent also added an I-105,
renumber one of them, because `merge_ledger.py` keeps only one row per id.

**Noticed, not changed.**
- Several ch.15 cards carry clock sizes that no DL entry records: 15.8.4 interrogation (4/6/8, hardens 6),
  15.9.14 research (4/6/8) and 15.9.15 surveillance (4/6, notice 4). Their basis is the trace clause C:P8 (clocks
  ticked by delivered reach) or R5 EX-11. They are tagged with those, following the C6a-C6c precedent: write a DL
  entry only when a card has no recorded basis at all. A later pass may want a DL entry for those sizes.
- DL-INT-13's "Revisit if" and evidence still name the older remaining list. Whoever closes I-065 should update them.

**Handoff.** Remaining: ch.08, 11, 12 (C6a's counts 49/82, 38/113, 67/136; re-count first). For each chapter: run
`python rules/_process/basis_audit.py NN`, copy `basis/C6d-16.py`, fill in its map, write a DL entry where no basis
exists, and add the chapter to `BASIS_CHAPTERS`. Close I-065 when the list holds 00-12 and 15-16 at 0 WARN, and update
DL-INT-13 then.
- Orchestrator merge note: renumbered I-098 to I-105, to avoid colliding with C5b's rows (C5b numbers from I-098).
