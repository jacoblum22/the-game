# Revision C5b report

Agent C5b. Rows: I-061, I-068, I-069, I-070, I-081, I-084, I-096, I-097 (ch.11, ch.12, the world seed). Brief:
`_process/REVISION-AGENT-BRIEF.md`. Baseline: `11-world-sim.py` and `12-world-seed.py` (with `--emit`) reproduced
their committed outputs and example byte for byte before any edit. `11-gen_factions.py` reproduces the first 4,836
lines of `factions.yaml`; the owner blocks after `blocks:` are merged at integration. Every regeneration was
therefore spliced: the generated head, then the committed blocks.

## I-061 agenda dice and the goal rating (done; better than the default)
- 11.3.7 and PR-11-2: each override that names a d6 rolls its own die, only when its condition holds. The
  temperament row is a fresh d6. `factions.yaml#agenda.dice` says so.
- Why not the ledger's single die: a faction at war that missed the 1–3 strike would read only rows 4–6. It could
  then never court, scheme or move on the PC while at war. The sims already roll separate dice, so T-11-24 stands.
- 11.3.5: `rating` is the one the action's Check column names. For `goal` it is `goal.rating` (11.3.1). See
  `#check.rating`. DL-11-30.

## I-068 entrenched (done)
- 11.3.5: −1 on `goal` and `expand` only, 0 on every other check, +1 to the DC of strike, scheme and court against
  it. 11.3.9: the weight of size takes the general modifier, so entrenched reads 0. WE-11-4 is now 13 + 4 + 0 = 17
  vs 16, and the margrave still holds.
- `11-world-sim.py`: `stage_mod(f, action)`. `scheme` also gains the +1 entrenched defense, which the sim lacked.
- Re-run: every T-11-24 cell refreshed. Moves are of at most one step, except the Cult's p90 week of collapse
  (35–44 → 30–37). Final mean tiers are 2.39 / 2.35 / 2.39, and nothing passed tier 3.
- The I-080 liar scenarios moved: within two years 195 → 204 wars, and the median war week 55 → 50.5. 11.6.9 and
  DL-11-29 are updated.
- `13-world-sim.py` and `--rule-cap` both run 11's code, and both reproduce byte for byte, so no ch.13 figure moves.
  DL-11-31.

## I-069 the wound's age (done)
- Every `tbl.12.seed.wound` row gains `era_years`: fallen realm 40–60; plague and invasion 20–30; schism 15–25;
  silent god and long winter 8–15; frontier 5–12; waking 2–5; any other wound 11–30.
- Pitches with an age now say `{years}` / `{Years}`.
- 12.16.4 rolls the age, and 12.16.15's opening year is that age, replacing the free `10 + d20`.
- Sim: the age is drawn on a seed-derived stream of its own, as I-083 did, so steps 1–6 are unchanged.
- Seed 1: "twenty-three winters ago", and the opening date is "23 years since the Burning".
- Sweep fix: the opening's second lead always quoted the wound's rumor, even when it pointed at the other
  situation. It now quotes the situation it points to. DL-12-33.

## I-070 petty faiths (done)
- PR-11-8 step 5 gains a **petty branch**: d6 on `factions.yaml#petty_goals` (1–2 grow, 3 take, 4 stir, 5–6 feud).
  The goal is local, on 6 segments, with the kind's text pattern and target rule, and the faction's highest rating.
- 11.3.16: `stir` is defined (`sit_t.festival_trouble` at its seat). The old text said "a situation from its
  template list", and no template has one. 11.3.16 also says what happens when a faction turns petty or full.
- `12-world-seed.py` writes the minor faiths this way, drawing the same d6 and d2, so earlier draws are kept.
- New check `ws.req.11_petty` (T-12-16, 64 checks).
- Seed 1: Halda's faithful *win more of Merestead to it, and a hold of its own* (1/6). Ala's faithful *settle its
  quarrel with the faithful of Oswen* (1/6). DL-11-34, DL-12-34.

## I-081 deposed (done)
- 11.3.10 gains a fifth, optional fate trigger, `deposed`: an officer leaves office alive and free. With no list of
  its own it fires the `captured` writes, and a write aimed at a captor reads as `recover`.
- Request size, by 15.3.2's own words: R4 for an officer, R5 for a head or an identity office. Ch.15 is unchanged.
- 11.3.11: a deposition counts −2.
- 11.3.17 **open seats**: filled at the next World Turn's Maintain step, by the named successor or else a new
  officer from `fields`. A faction left with no linchpin seals fates for its first officer.
- PR-11-1 step 2, `world_turn.yaml` and the seed check (which now accepts the optional fate) are updated. DL-11-32.

## I-084 the founding threat can escalate (done; 04.3.4 handed off as I-098)
- 11.3.3 **outgrown factions**: a full faction is outgrown when its champion's band is below the PC's `power_band`
  and it is set against the PC.
- Its next goal is *win {power} to its cause*: a `change` goal, regional at any tier, rated by its highest rating.
  The target is the nearest band-5 power of the far rings that no faction holds.
- On completion the power becomes its patron and band-5 champion. The goal is foiled if the power is dead, held
  captive, the PC's ally, or Warm or better toward the PC.
- Rejected, the ledger's realm `grow`: tier 3 cannot pursue realm goals, the clock takes about two years, and tier 4
  still fields only a band-4 champion.
- Sim: `11-escalation-check.py` (2,000 seeds, reusing 11-world-sim's check and agenda) gives a median of 35 weeks
  (p10 24, p90 50) at a highest rating of 5 while rising, 45 weeks at 4 while flourishing, and 51 weeks entrenched.
- 12.16.8: if both ring-5 areas roll home band 4, the second becomes 5, and `ws.req.10_rings` checks this.
- 12.16.18: a new region's ring 1 is home band 4, and its later rings are 4–5.
- 12.16.11 notes that the powers can be won. DL-11-33, DL-12-35.

## I-096 the seed's word mix (done)
- 12.16.17 now quotes trivial 35.4 / easy 26.4 / fair 34.7 / hard 3.5 / lethal 0. It also says that home-1 tables
  are audited against both reference PCs (PR-10-8 step 2). DL-12-36.

## I-097 (closed wontfix)
- The owner does not use the setting. The fix is not a one-liner outside ch.13: `13-gen_region.py` would have to call
  `10-word-audit.audit_table` and rebuild its tables. `12-world-seed.py` still reports the gap.

## Re-runs
- `11-world-sim-output.txt`: changed (I-068).
- `13-world-sim-output*.txt`: byte-identical.
- `12-world-seed-output.txt` and `-example.yaml`: regenerated. PASS: 64/64 on seed 1, the guided run and 200
  oracle seeds. The tables passed on all 2,600 builds.
  - Seed 1 changed from the Tangled Ridge's home-5 table on: the opening incident is now *alarm*, there are new
    pregen names, and the bestiary holds 46 entries.
  - WE-12-11 steps 1, 5, 7, 13 and 14 and the guided run are updated.
- `09-word-mix-pacing-output.txt`: only the quoted mix moved. The d20 faces and the pacing results are identical.
  09.12.3's rounded "trivial 34 / easy 26 / fair 36 / hard 4" is now 34 / 27 / 35 / 4. That is ch.09 text, so it
  goes to **I-099**.
- `04-recog-parity.py` builds 20 seeded worlds; re-run, it reproduced `04-recog-parity-output.txt` byte for byte.

## New rows
- **I-098** (04): 04.3.4's tier-4 "In fiction" column read as a gate (the ch.04 part of I-084).
- **I-099** (09): 09.12.3's rounded table mix after the C5b re-run.

## Close-out
- `integration-assemble-appendix.py` re-assembled `decision-log.md`. No trace fragment changed.
- `12-compile_anchors.py`: 129 anchors, 0 errors, 0 warnings. Only the source hashes moved.
- `validate_ruleset.py`: 0 ERROR / 0 WARN.
- Ch.13 untouched.
