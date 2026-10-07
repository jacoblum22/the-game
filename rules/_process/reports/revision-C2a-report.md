# Revision C2a report

Agent C2a. Rows: I-037 (MAJOR), I-039 (MAJOR), I-083 (MAJOR), I-063, I-064, I-034.
Chapters touched: listed per row. ch.13 untouched. Nothing committed.

## I-037 (MAJOR) `power_band` has two definitions (done)
- Ledger default adopted: **confirmed tiers only**, everywhere. 04.5.6 now reads each unsuspended calling's
  `confirmed_tier` (new field in 04.1.2's calling record: the highest tier whose grant is permanent). A provisional
  tier's own grants work at once; band, maximum Vitality, 09's advisory, 03's `peak`, 16's band cap and 05.6.1's
  `T_high` / `breadth` wait for confirmation (12 evidence-bearing scenes, 04.8.2). Rationale: a lapse must not lower
  Vitality, Focus and allies' lines; 04.8.2 already holds the tier-4 attribute back for the same reason.
- Edited: 04.5.6 (formula, why; the stale "see issue I-037 / I-028" parenthetical removed), 04.1.2 (field), 04.8.5
  item 5 (`inherited_band` at confirmed tiers), 04 edge case "Power band during suspension or provisional grants",
  WE-04-1 session 9 (band 2 once Archer 2 is confirmed), 05.6.1 (`T_high`, `breadth`), 00.17.1 Q5, 07.1.2 (cites
  04.5.6), `data/callings.yaml#power_band` comment and its generator header `04-callings_header.yaml`.
- Refs checked (`--refs 04.5.6`, grep `power_band`): 03.4.3 `peak` (reads 04's function; unchanged), 16.2.4 band cap
  and `trg.16.band_cap_changed` (fires on any band change; confirmation is a change), 02:829 ("no confirmed tier",
  consistent), 09.6.6, 10's out-of-band rule, 07.1.2 recompute order (phase 9 after 04's phase-8 confirmation),
  WE-04-1 sessions 17 and 37 (already confirmed-based), 04.9 Paladin example (suspension). DL-04-29.

## I-063 P4/P5 best-domain modifier (done)
- Chosen: widen 00.3.7's P4 to +9…+11 and P5 to +10…+12 (`scales.yaml#bands.pc_best_base` too), and 04.5.1 states
  its assumption (tier-4 increase on that attribute; one lower without) and that the reference PC is the top of
  the range. Rejected the restate-only option: it leaves every edge-0 P4/P5 specialist off its own band.
- T-06-12 re-checked: its +11 / +12 reference lines are inside the new ranges, so 06's and 09's sims and audits are
  unaffected (PR-09-4 reads the PC's own line). Added a "PC column" paragraph to 00.3.7. DL-04-30.

## I-064 keeper's regard at Fraying stage 2 (done)
- Chosen: regard fails only at stage 3 (the ledger's first option). 05.7.4 states stage 1 / 2 / 3 / atonement in
  order; 05's edge case "acts against the keeper's axes" now says stage 3 and that regard returns during an
  atonement; WE-04-6's atonement line says his spells work at tier 1's ranks. 04.9.3 / 04.9.4 unchanged (they were
  right). grep of "stage 2" across chapters: no other divine-silence claim. DL-05-36.

## I-039 (MAJOR) + I-083 (MAJOR), designed together (done)
- Interaction: I-039 caps the band a contest can lend; I-083 needs high-band opposition to exist. Capping alone
  (binding party + `power_band` + 2) leaves the seeded world with no band-5 party, and the per-opposition limit
  alone makes tier 4 unreachable (sim row W-NEW-NOPOWERS: never tier 4). So the cap and the limit come with supply.
- I-039 rule (ledger default, kept): only a party that can **bind** the faction (head or officer, 11.3.17; a
  faction keeping a truth itself, for lore) lends its tier; anyone else counts its own band; every contest band
  (social, lore, craft) is at most `power_band` + 2, matching a fight's lethal +2. 03.4.3, 15.3.11, 15.9.20,
  08.6.4 item 6, `evidence.yaml#challenge_band_source`. DL-15-36.
- I-083 rule. Rejected the relative band (`max(absolute, power_band + offset)`): a contest has no danger
  estimate to read an offset from, so the DM would choose it, and a P4 envoy would do band-5 deeds against a
  headman. Chosen: (a) the world seed writes the **powers of the far rings** (12.16.11): band 4 per ring-4 area,
  band 5 per ring-5 area, each keeping a sealed truth (`tbl.12.seed.powers`, `ws.req.04_powers`; 12.16.18 new
  regions: powers at band 5); (b) 04.3.4: at most **two** great deeds per tier from one opposition (party, case,
  research project, work), carried as `contest.opposition` (03.2.1, `evidence.yaml`). DL-04-31, DL-12-31.
- Generator: `12-world-seed.py` writes the powers on a seed-derived stream of their own, so every earlier roll is
  unchanged (example diff: additions only) and adds the `powers` check. PASS: 63 of 63 on seed 1, guided run,
  200 oracle seeds. 12.16.17, 12.16.18 (also fixed its stale "58 of 62": the script says 54 of 63), WE-12-11
  steps 8 and 14 and its guided line, OEQ-12-11, T-12-16 updated.
- Sim: `04-recog-parity.py` gains an I-083 section (its I-003 section is byte-identical to the committed output):
  contest parties drawn from 20 seeded worlds, power band from confirmed tiers (I-037) for every style.
  | style | old seed, I-003 rules | revised | archer |
  |---|---|---|---|
  | envoy T3/T4/T5 | 19 / 33 / never | 19 / 32 / 49 | 20 / 34 / 52 |
  | smith | 19 / 32 / 47 | 23 / 35 / 48 | |
  | scholar | 18 / 34 / never | 19 / 32 / 49 | |
  Farming envoy (a tier-5 door-warden on offer): median 24 band-4/5 deeds banked in sessions 1–10 before, 0 after.
  `04-recog04.py` log rows now carry the opposition id (8th field; no reader of the old 7 changed).
- Text: 04.3.4 (limit, cap), 04.3.4's requirement-key table, 04.3.5 (new "Parity in a seeded world" table),
  T-04-8 R12. Refs checked: `--refs` 03.4.3 / 15.3.11 / 15.9.20 / 04.3.4; 09.6 and 09's challenge-band notes
  (conflict only, unchanged); DL-03-26 / DL-15-32 history left as is.

## I-034 pacing tables on the advisory model (handed off, row open)
- Done: `04-recog04.py` draws conflicts at power band + the DL-00-05 offset by default (`conflict_tier`,
  `CONFLICT_OFFSET`); `09-i005-check.py` adapted to the new line (output byte-identical); `04-feat04.py` and
  `04-wren04.py` load `04-recog04.py` by path (they pointed at a scratch name `recog04.py` and could not run); all
  three re-run, outputs committed.
- Not done, and why: the new R1 numbers miss 04.3.5's own targets (archer 5 / 12 / 23 / 40 / 60, tier 5 within 60
  in 103 of 200; swordsman 3 / 8 / 15 / 25 / 38), so copying them into 04.3.5, T-04-8 R1–R10 and WE-04-1 would
  print a failed target as the design. New row **I-089**: decide retune (W thresholds or since-fields) or restated
  targets, then refresh 04.3.5's table, T-04-8 R1–R10 (all rows move: see `04-recog04-output.txt`) and rewrite
  WE-04-1 from `04-wren04-output.txt` (seed 7; every session number and tally moves). I-089 also logs that
  12.11.1 writes no `band` for an on-demand NPC.

## Close-out
- DL: DL-04-29..31, DL-05-36, DL-12-31, DL-15-36 (numbers taken as next free at the time; check against other C2
  agents). New ledger row I-089. README's known-issues list drops I-037 and I-039.
