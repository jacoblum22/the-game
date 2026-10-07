# Revision C3 report

Rows: I-075, I-076, I-078, I-042, I-057, I-060, I-072, I-077, I-082 (ch.02, 06, 07, 16; with 00, 12, 15 where
a fix reached them). All nine resolved. Every edit is tagged `[revision: I-NNN]`. Nothing committed; ch.13 untouched.

## I-075 (MAJOR): dropped objects wiped mobs (resolved)
- **Fix.** I took the ledger's (a) and (b) and added a share cap. T-06-8 gains a **footprint**: a dropped,
  toppled, swung or rolled object selects at most its rung's count of creatures (hand 1, body 2, heavy 3,
  massive 4) inside its shape's cap. Against a mob each selected member takes one share, and no share can exceed
  one member's Vitality, so the object fells at most its count. A fallen object becomes a fact and cannot be
  dropped again; another drop needs another feature established (06.3.8).
- **Why the share cap.** Without it, a massive S4 on a T1 mob would still carry 4 × 8 = 32 harm over the pooled
  Vitality and fell six members. With it, "at most its count" holds.
- **Where.** T-06-9 row 5 no longer lists the portcullis, and row 19 is now its one anchor (S3 and restrained,
  on one creature). T-06-8's massive examples drop the portcullis too. Row 9 (body, at most 2) and row 29 (the
  count caps the pierce) take the footprint. Also changed: 06.5.10's `targets` knob, a new 06.10.4 bullet, the
  06.10.6 finding, and `conflict.yaml#improvised.selects_at_most` plus `improvised_footprint`, through
  `06-gen_data06.py`, which re-validates OK.
- **Sim.** `06-conflict-sim.py` gained an `env=` hook. It is unused by default, so sections A–K reproduce
  **byte-equal**. Section L was added (seed 606, 20,000 fights a cell).
  - The old reading felled a whole T1 mob of up to six on every hit. That is a 55% wipe rate at P1, which is the
    hit rate.
  - The ledger's "any band-2 mob" overstates the problem: T2 members (12 Vitality) were never wiped by S3 × 6.
  - New rule: a mob larger than the object's count is never wiped.
  - One drop moves a mob fight at most one advisory word gentler (T-06-13), and only for heavy or massive
    objects. The advisory words therefore stand.
- **Refs checked.** `loose_object` and `barrier` (06.3.8) still agree, and so does 06.8.1's cone for falling
  objects. The DL-06-11 basis is unchanged. DL-06-27.

## I-076: a barred gate did not stop pursuit (resolved)
- **Fix.** 07.4.3's ABLE now also needs a **way to follow**: no shut `barrier` and no other movement-blocking
  feature (`no_line` for Moves) between the pursuer and the PC's route. A barrier the pursuer could break still
  blocks, because breaking it takes the pursuer's own turn. The OFFER states the barrier's Force tier as the
  delay.
- **Where.**
  - 07.4.3 gains a boundary example.
  - PR-07-6 step 2 states the new ABLE condition.
  - WE-07-7 gains a fourth state: the barred cellar door, which gives a clean retreat.
  - 06.12.3 notes that a way barred before the Retreat is not a chase beat.
  - `harm.yaml#retreat.pursuit_test.able` changes through the generator.
- DL-07-22.

## I-078: two recovery seams (resolved)
- **(a) Long rests.** The ledger's fix is kept alongside "one a day". No `rest_long` begins until two watches
  have ended since the last one completed.
  - Changed: 00.7.2's table, 00's Q16, 07's rest table and recovery table, `scales.yaml` and `harm.yaml`
    (`min_gap_watches: 2`), and a new state field `last_rest_long_end`.
  - Check: nightly sleep leaves three watches between rests, and shifting sleep to the evening watch leaves two.
    The exploit, one rest in the night watch and another in the morning watch, left none.
- **(b) Treat.** 07.8.8 now allows one Treat beat for each wound and each affliction a day, by anyone.
  - A beat may frame only wounds that are neither `treated_today` nor closed.
  - A failed beat closes every wound it framed for the day (`treat_closed_today`, cleared at the day boundary in
    PR step 4).
  - Affliction records carry `treated_today`.
  - First aid on the Dying keeps its once-a-round retry (Edge cases).
  - `harm.yaml#treatment.per_wound_per_day` and `by`.
- DL-07-23.

## I-042: Wren's Vitality (resolved, retraced at 13)
- **Fix.** I retraced at 13 rather than writing "before her Bent". The sheets in 06, 07 and 12 each list
  Endurance +1, so keeping 12 would make each sheet contradict itself.
- **Moved numbers.**
  - WE-06 trace: 13/13, 13 → 10, ends at 10/13.
  - WE-06-5: 13 → 5.
  - WE-06-8: S5 from full leaves her 1; from anything less it Staggers her.
  - WE-07-1: 13 → 8 (worn) → 3 (bloodied), with an excess of 2 discarded. Her maximum after the barrow is 7, from
    the floor ceil(13/2).
  - WE-07-3: 13 → 11 → 8 → 5 → 2, ending at 2.
  - WE-07-5: maxima 7, 10 and 13; rests give 7 (full), 6 (partial) and 3 (interrupted).
  - WE-12 and 12's RESULT sample: 13 → 10.
- **Unchanged.** Maimed and Reprieve still stand at ceil(max/4) = 2. No example's outcome changes. DL-06-28.

## I-057: Strike attribute for a branch working (resolved)
- 06.4.3 decision 2 now names the exception: a branch working is a Strike with the branch's casting attribute,
  needs no weapon, and reaches as 05.7.11 says. DL-06-29.

## I-060: Bent frame count (resolved, not the ledger default)
- **Why not the default.** The default, "the count resets at each accepted Bent", implies a second Bent. 02.6.6
  forbids that: an accepted Bent is "finished for this character's life".
- **Where the misreading came from.** `gen_birth.yaml#bent.cap: 3` was the attribute ceiling, not a Bent count.
- **Fix.** 02.6.5 now states one Bent a life with a count that never resets. The generator (`gen02.py --emit`)
  renames `cap` to `attribute_cap`, adds `per_life: 1`, and extends `eligible_after`. `gen_birth.yaml` is
  otherwise byte-equal.
- **Note for whoever runs `gen02.py --emit`.** It also rewrites `origins.yaml` and `kits.yaml` without their
  integration-merged `blocks:`. I restored both. This is how the merge pipeline works (integration-merge.py
  re-adds them), not drift.
- DL-02-26.

## I-072: Devotion through a bond (resolved)
- "A bond" is dropped from 15.1.7 and from 16.5.10. A creation bond is a starting standing (+2 at most, 02.9.2),
  never a step to Devoted. A bonded ally reaches Devoted by the same deeds of weight as anyone, or by its thread's
  completion (16.12.3).
- `social.yaml#small_step_caps.ceilings.devoted_only_from` changes `bond` to `ally_thread_complete`.
- DL-16-23.

## I-077: posted allies had no cap (resolved)
- **Cap.** 16.2.3 adds a posting cap per place, counted in retinue places: `retinue_cap`, or the holding's staff
  line (08.8.8) when that is larger. A post over the cap gets G4.
- **In a conflict at the post.** Posted allies are present but are not the retinue. Each acts through its task,
  or as a scene ally when the PC Commands it (1 PC action each, 06.14.2), and stays posted afterward.
- **Mounts.** T-16-1's beast row drops "ridden into conflict": a ridden mount is part of its rider's participant
  (06.15.1), as T-16-2 says.
- `companions.yaml#retinue.posted_cap` changes through `16-gen_data16.py`, which was byte-equal before the change.
- DL-16-24.

## I-082: `07-gen_harm07.py` crashed (resolved)
- **Fix.** Run on its own, the file now hands over to `07-gen_data07.py`, which defines `E`, `L` and `write` and
  then execs this file. It no longer stops at `NameError: E`.
- **V2c1's hand edit.** V2c-006's text was already in the generator. The regenerated `harm.yaml` differs from
  V2c1's hand edit only in line wrapping, and the two load as identical YAML.
- **Byte-equality.** Re-running through either entry point gives byte-equal output (checked with `cmp`).
  injuries, afflictions, last_chance and the merged-contrib outputs did not change.
- `harm.yaml` was then regenerated, not hand-edited, for I-076 and I-078.
- DL-07-24.

## Close-out
- DL entries: DL-02-26, DL-06-27..29, DL-07-22..24, DL-16-23..24.
- `appendix/decision-log.md` and `traceability.md` were re-assembled with `integration-assemble-appendix.py`.
- `12-compile_anchors.py`: 129 anchors, 0 errors, 0 warnings.
- Validator: 0 ERROR / 0 WARN.
- New ledger rows: none.
- Tooling note: `06-gen_data06.py` rewrites `conditions.yaml` with an empty `blocks:`, which drops ch.07's merged
  block. Restore it with `git checkout`, or re-run the merge, after running that generator. As with `gen02.py`,
  this is the merge pipeline working as designed.
