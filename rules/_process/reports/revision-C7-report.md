# Revision C7 report: basis tags for ch.11-12 (I-065), job fees in ch.11 (I-091), pacing mix (I-095), In fiction column (I-098), word-mix figures (I-099), joining at Wary (I-105)

Agent C7, main checkout. The orchestrator was writing ch.14 and `DL-14.md` at the same time: those were not
touched, and the appendix was **not** re-assembled (the orchestrator does that). Note: the orchestrator's WIP commit
c4900cd caught this work mid-way, including a `factions.yaml` whose owner-blocks the generator had just dropped; the
working tree now has them restored (see I-091).

## I-065 (ch.11-12): resolved, row closed

- **Re-count** (`basis_audit.py`): ch.11 had 38 of 113 cards untagged, ch.12 67 of 136 (as C6a counted).
- **Scripts:** `rules/_process/basis/C7-11.py` and `C7-12.py` hold the `{card: basis}` maps, and `apply_basis.py`
  applies them. They tagged 105; a second run tags 0.
- **Where the bases come from** (each card read through `rq.py` first):
  - the DL-11 or DL-12 entry for the card or its section;
  - another chapter's decision that the card applies (DL-12-13/15/21/24, DL-08-18, DL-11-01/02/05/10/11/21,
    DL-05-35);
  - the trace clause;
  - the R5 row for the card's subject, which I checked against R5 itself. trace-11's R5 list does not line up
    one-to-one with its rule list.
- **New DL entries** for cards whose numbers had no recorded basis:
  - **DL-11-35**: 11.9.5 strikes on holdings. The DC is DL-11-03's opposed DC, with the garrison as the defender's
    rating and the domain tier as its tier. It also covers 11.9.6's improvements: the prices, build weeks and 3 / 6
    caps are stated as unmeasured defaults.
  - **DL-11-36**: 11.10.4 festival effects.

  Neither rule looked unjustified.
- **Appendix:** `basis/C7-appendix.py` (idempotent) adds DL-11-35/36, the BRIEF §6 rows in trace-11 and trace-12,
  and updates **DL-INT-13**:
  - its evidence now runs through C6d, C6e and C7;
  - its "Revisit if" no longer lists done chapters. It now reads: a card whose only basis is a derivation, or
    ch.13 or ch.14 entering the audit.
- **Validator:** `BASIS_CHAPTERS` = 00-12, 15, 16, which gives 1,416 cards, 0 untagged.
- **New row I-106:** `imp.walls` in the data has an effect that the 11.9.6 card lacks, and the card states no
  minimum holding for four improvements.

## I-091 (ch.11): resolved, row closed

All four changes are tagged `[revision: I-091]`:
1. **11.5.11:** coin is now paid at 08.8.8's job fee for the thread's band (`economy.yaml#job_fees`).
2. **11.5.12:** the "a faction's commission" row cites the fee. The same change is in `world_turn.yaml`, which is a
   hand-kept file.
3. **T-11-4 and T-11-3:** the `aid_pc` opportunity-bang job and the Friendly row's "jobs offered" both cite the fee.
   - The `aid_pc` text in `11-gen_factions.py` was updated and the generator re-run.
   - The generator writes `factions.yaml` directly and drops its owner-blocks. `integration-merge.py` restored
     them; the only diff left is that one line.
4. **The thread schema's `reward` comment** names `job_fees`.

DL-11-37 records the change.

## I-095: resolved

- **04.3.5:** a new paragraph says the fight mix is a campaign mix: about half of a PC's fights are chosen. It has
  a three-row table from `09-word-mix-pacing-output.txt`:

  | Mix | Archer, median sessions to tiers 1-5 | Tier 5 within 60 |
  |---|---|---|
  | Assumed (DL-00-05) | 5 / 10 / 18 / 32 / 54 | 183 of 200 |
  | Half chosen | 6 / 13 / 21 / 34 / 58 | 135 of 200 |
  | Rolled only | 20 / 58 / — / — / — | 0 of 200 |

  The swordsman rows are in the table too.
- **T-04-8:** new row R15, and R1 now points to it.
- **Decision:** 12.7.4 is not changed. The director governs intensity, not growth, and 12.9.2 says opportunities
  are never forced. The rules already make sure a chosen fight is always within reach: 12.16.12, 11.5.10 and
  12.8.5.
- **02.11.1 and OEQ-02-7** now carry the caveat.
- DL-04-33 records the decision.
- **For ch.14:** the player guide is the place to tell the player that seeking out danger is how a character grows.

## I-098: resolved

04.3.4 gains a note that the "In fiction" column is staging guidance, not a requirement. Tier 4's "many countries"
means the Contexts column, not geography; the fiction says it literally only once play has crossed into new
regions (12.16.18). DL-04-34.

## I-099: resolved

09.12.3 and DL-09-26 now give the mix as 34 / 27 / 35 / 4 / 0, and also note the old figures.

## I-105: resolved

- **16.6.2, PR-16-7 step 1 and 16.3.7:** the departure clock starts only on a step down to Wary. An ally that joins
  at Wary holds there until regard or grievance moves it. A well-kept beast reaches Neutral in about three weeks.
- No data change: `clk.16.departure` carries no creation condition.
- DL-16-25's open note is replaced by the decision.

## Close-out

- Anchors recompiled: 129, 0 errors.
- **Validator:** 0 WARN.
  - In the main checkout, the new DL ids give XREF ERRORs until the appendix is re-assembled.
  - On a scratch copy that I re-assembled, the only ERROR left is DL-00A-34 at `00-architecture.md:1922`. That is
    the orchestrator's new 00.16.6, and it is not in decision-log.md yet.
- Scripts written: `rules/_process/C7-dl.py`, which adds DL-04-33/34 and DL-11-37 and updates DL-16-25 (idempotent),
  and `basis/C7-*.py`.
- Nothing was committed.
