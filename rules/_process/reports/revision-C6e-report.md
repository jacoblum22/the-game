# Revision C6e report: basis tags for ch.08 (I-065), crude-repair limit (I-092), job fees in ch.15 (I-091)

Agent C6e. Rows: I-065 (ch.08 only), I-092, I-091. Ch.11, 12, 15 and 16 were being edited in parallel; ch.15 was
touched only at the deal and Work passages that I-091 needs.

## I-065 (ch.08): partly resolved, left open

**Method.** C6c's method, unchanged (DL-INT-13):
- `basis_audit.py 08` re-counted the chapter: **46 of 82** cards were untagged (C6a's count was 49/82).
- `rules/_process/basis/C6e-08.py` holds the `{card: basis}` map, and `apply_basis.py` applies it. It tagged 46;
  a second run tagged 0, and the re-audit shows 0 untagged.

Each card was read through `rq.py` before it got a basis. Bases come from:
- the DL-08 entry that names the card or its section;
- the other chapter's decision that the card applies:
  - DL-07-14 reduction cap, DL-06-08 Guard, DL-06-01 action budget;
  - DL-05-23 healing cap, DL-05-41 consumable Focus, DL-05-08 learning, DL-05-24 rites, DL-05-15 reserve,
    DL-05-35 keepers;
  - DL-02-13 kits, DL-10-06 supply, DL-10-23 light, DL-11-19 holdings, DL-16-02 retinue places;
  - DL-00A-13 tags, DL-00A-18 generator, DL-00A-19 verbs, DL-00A-22 state;
- the trace-08 constitution clause;
- the R5 EQ row that trace-08 maps the section to (EQ-01, 02, 04, 07, 09, 10, 11, 12, 13);
- R3 A-23 for 08.6.10.

No basis was guessed, and no card needed `[derived:]`.

**Cards with no recorded basis.** Three cards' own numbers had none, so each now has a DL entry. Each entry says
its numbers are unmeasured defaults and gives a revisit trigger:
- **DL-08-39**, 08.5.1 body slots: the closed slot table. Its counts are checked against attunement's five.
- **DL-08-40**, 08.6.11 batches, scrolls and copies: segment counts from DL-08-16's ladder; three doses at half
  price per dose; the scroll cost from `price_rule`.
- **DL-08-41**, 08.10.4 hull clock: 4/6/8 by price, on DL-00A-20's clock sizes.

None of them looked unjustified, so there is no new row.

**Appendix and validator.**
- `basis/C6e-appendix.py` (idempotent) adds DL-08-39..41 and the BRIEF §6 row to trace-08.
- The appendix was re-assembled and the anchors recompiled.
- `BASIS_CHAPTERS` now holds 00-10. INFO reads "961 rule cards, 0 untagged".

**Not changed, as instructed:** DL-INT-13. Its evidence and its "Revisit if" list still stop at C6c, and whoever
closes I-065 should update both.

**Remaining:** ch.11, 12, 15 and 16. Re-count each first; C6a's counts were 38/113, 67/136, 57/104 and 73/101.

## I-092: resolved

- **01.13.4**, the S3 `cost.gear` row, now reads: "Handle crude repair: Easy, 1 interval, on worn, common or fine
  items only; finer work needs the lasting repair, 08.6.7".
- **`ab.field_patch`**: its limitation (generator `05-gen_data05/ab_craft.py`) adds "of worn, common or fine
  quality (08.6.7)".
- **Also found:** `lic.training.craft_smithing`'s crude fallback (`lic_training.py`) gave the same crude repair
  with no limit. Its consequence now adds "worn, common or fine items only (08.6.7)". The fallback is copied into
  `licenses.yaml` and into three abilities' crude fallbacks.
- **Regeneration:** I ran `gen_data05.py --emit` (0 errors), then `integration-merge.py`, which restores the merged
  owner-blocks; the emit alone drops them from `licenses.yaml` and `composites.yaml`. The data diff is those lines
  only.
- DL-08-37 is extended.

## I-091: ch.15 and ch.08 done; left open for ch.11

**Ch.15** (three minimal edits):
- **15.7.1 item 4** (new): a patron's job is the reverse deal. It is offered at 08.8.8's job fee for its challenge
  band (`economy.yaml#job_fees`), never at a DM's figure. Half is paid up front below Warm, and the PC keeps only
  that half on a failure.
- **15.7.2:** its trigger now includes a patron's job fee. Its computation raises the fee one notch at delivered
  reach 2+ and never more, which matches 08.8.8's "one notch".
- **15.13.7 Work:** a patron's job is not Work; the job fee pays for it.

I did not put this in 15.3.5's Payment term, as the row proposed. That term is value the PC hands to the NPC, so
the fee belongs with the deal rules.

**Ch.08 and data:**
- 08.8.8's pointer, and the same pointer in `job_fee_rules`, read "an NPC's request with a Payment term, 15.3".
  They now read "an NPC's paid request, 15.7.1 item 4".
- 08.8.9 rule 6 and AI-6 replace the tableless "rewards (11)" with: a patron's coin reward for an 11 thread is the
  job fee of its band.
- I re-ran `08-gen_data08.py`; the `economy.yaml` diff is those lines only.
- DL-08-36 is extended.

**Remaining, ch.11 only.** The I-091 row lists four changes:
1. 11.5.11's "coin from the patron's means at 08's wage scale" should cite `job_fees`.
2. The thread table row "a faction's commission" should cite `job_fees`.
3. `aid_pc`'s opportunity-bang job, and the Friendly row's "jobs offered", should say the job pays the job fee.
4. The `reward:` schema comment should name `job_fees` for coin. `factions.yaml` should be mirrored if it is
   generated.

## Close-out

- Appendix re-assembled; anchors recompiled (only source hashes moved).
- Validator: 0 ERROR / 0 WARN.
