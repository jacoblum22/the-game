# Revision A report: progression and magic

Agent: Revision A (Opus). Scope: I-009, I-007, I-003, I-015, I-020, I-008, I-004
(`_process/FINISH-PLAN.md`, order of work item 1). Appended after every step.

## Step 0: baseline (2026-10-05)
- Read FINISH-PLAN.md, issue-ledger.md, BRIEF §10–12 and Addenda A/B, AUTHOR-BRIEF.md.
- Validator baseline: `python _process/validate_ruleset.py` reports 0 ERROR / 0 WARN, 80 INFO.
- Appendix assembly: `_process/simulation/integration-assemble-appendix.py`; anchors:
  `_process/simulation/12-compile_anchors.py`.

## Step 1: generators made reproducible (precondition for every data change)
- `05-gen_data05`: the live `abilities.yaml`, `licenses.yaml`, `rituals.yaml` and `composites.yaml` had drifted
  from the generator through integration edits ("In place of Fend" on 3+1 defense reactions; "a designed rite
  (05.8.4)" in two excludes; the 04 owner-block header wording; the rite-conditions table id; rit.forge_virtue's
  one-worked-property clause; the `cone` spread row and `spread_form_map`). All ported into `ab_martial.py`,
  `ab_arcane.py`, `emit05.py`, `rites05.py`, `comp05.py`. Verified: generate into a scratch copy, run
  `integration-merge.py`, `diff -r` against live `data/` = identical before any revision content was added.
- `02-gen_data02`: Windows-only hard-coded paths in `gen02.py`, `gen_contrib02.py`, `draws02.py`, `sim02.py`,
  `tables02.py` replaced by repo-relative paths (`GAME_RULES` env override); the `origins.yaml` header wording
  edited at integration ported into `gen02.py`. Verified the same way: identical.
- Pipeline for both chapters is now: generator `--emit` → `integration-merge.py` → validator.

## Step 2: I-009 / I-015 / I-007 data authored (generator tables)
- 05.7.11 branch workings (new `slot_class: license`; no slot; zero Focus; rank = grade in the casting school's
  license, mirroring 06.4.5 mastery): `ab.force_bolt` (arcane, band.near, harm.arcane.force, crit pushes one
  band), `ab.rebuke` (divine, band.close, radiant or necrotic by keeper, +1 rung vs the opposed nature),
  `ab.wild_lash` (primal, band.near, harm of the source present, off-balance). S2/S3/S4 by rank; budgets 3–4 /
  4–6 / 6–7 against allowances 4 / 6 / 8. Every magic training license's scope now names its branch working.
- I-015: `ab.undertow` (water), `ab.stolen_breath` (air), `ab.heave` (earth; Stone Shape is min_tier 3, so
  earth had no min_tier-1 working either). The spark (`birth.gift.elements`) now grants the working of the
  element named or drawn (`gifted_ability_by_element`); ch.02 generator and T-02-7 renderer updated.
- I-007: nine min_tier-5 negative-pole abilities (`ab.no_quarter`, `ab.web_of_lies`, `ab.last_embrace`,
  `ab.hoard_heart`, `ab.iron_decree`, `ab.peerless`, `ab.wrath_unbound`, `ab.unhallow`, `ab.cold_calculus`);
  the generator's coverage check now enforces a 1/3/5 ladder on every pole a calling uses.
- Data emitted; validator 0 ERROR / 0 WARN after fixing one bad tag reference I introduced.
- Census: 266 abilities = 179 pool + 57 oath + 3 branch workings + 27 absorbed.

## Step 3: I-009 simulations (06 sim section J; ch.02 sim extended)
- `06-conflict-sim.py` gained a caster mode (`caster=`: working severity, armor-bypass for non-physical harm per
  09.3.6, Force Bolt's crit push, a Focus spell or the push) and `foe_fend` (09's adversary Fend). All earlier
  rows reproduce byte for byte; section J appended. Output: `06-conflict-sim-output.txt` (20,000 fights/row).
- Acceptance: new caster (+5, Guard 12, Vit 12) with its working vs one T2: Force Bolt 93.6%, Rebuke 92.8%,
  Wild Lash 92.8% (≥ 75% met; staff alone 51.3%). Spent tier-3 caster (rank 2, S3) vs one T3: 91.0 / 90.3 /
  80.7% (≥ 40% met); with 09's adversary Fend 86.8 / 86.2 / 74.5%; at WE Ash's Vitality 12, 84.6 / 83.6 / 70.6%.
  Before I-009: 0.4%.
- Martial comparison (no Focus, one equal-band foe): caster 100/99/91/48/30 (best branch) vs specialist
  100/100/99.7/87/80 at P1–P5; never above the specialist, and below the broad martial at P3 (87.4) only for
  Wild Lash. Casters do not outclass martial.
- Focus comparison (P3 caster, Focus 7): push on the working raises win% vs T3 91→96, vs T4 34→55, vs 2×T3
  26→47 (martial push: 99.7→99.9, 62→84, 73→90). Focus is worth as much to a caster as to a fighter. A 1-Focus
  damage spell (Flame Lance r2) adds only +1/+11/+0: in fights of under three rounds its burning rider is worth
  less than the push's severity rung. Logged as a new ledger row (EU table weighting of damage-over-time).
- `02-gen_data02/sim02.py` extended with eight caster lines using their workings (output appended; earlier rows
  byte-identical).
- ch.02 default fix: 02.3.5 now defaults a magic livelihood to the Free rule when its people's Typical rule would
  fix the casting attribute at −1 (Orc-kin apprentice, Goblin-kin acolyte, Beastfolk hedge-taught and Touched).
  Generator (`gen02.py`, `tables02.py`, `creation_block.py`) changed; `origins.yaml` regenerated.

## Step 4: I-007 ladder verified
- `_process/simulation/05-ladder-check.py` (+ `05-ladder-check-output.txt`): every calling (183) × pool axis ×
  tier 1–5 under 04.8.4's gate. Now 0 failures. Against HEAD data it reports the 18 dark tier-5 holes and a dead
  conduct gate on the Monk (pole unset, so 05.3.10 admitted no restraint ability), proving the check bites.
- Monk fixed in `04-gen_data04.py` (`pole: positive`); ch.04's generator made path-portable and its header
  drift ported (verified reproducible first).
- Middle tiers: light and dark poles both carry abilities at min_tier 1, 3, 5 (allowance rises only at 1, 3,
  5), so neither pole is thinner; nothing else to fill.

## Step 5: chapter text for I-009 / I-015 / I-007 / I-008
- ch.05: 05.1.1 exception, 05.2.3 list, 05.3.1 `slot_class: license`, 05.6.2 knack band, 05.6.5 Spent,
  05.6.8 Quiet column (I-008), new **05.7.11 The branch working** (table, five rules, budget, simulated
  numbers), 05.11.5 census, 05.11.6 counts and ladder, IR to 04 items 2/3/10, OEQ-05-6, a worked example
  (WE-05-8 "Spent, and still casting" with two boundaries and a non-example). T-05-12 and T-05-14 are now
  rendered from data by `05-gen_data05/tables05.py` (verified to reproduce the HEAD tables from HEAD data
  before applying).
- ch.02: 02.3.5 caster exception, 02.6.3 spark by element, T-02-6 and T-02-7 re-rendered by `tables02.py`
  (unchanged rows byte-identical), edge case "against the grain", IR to 05 (a)/(b) marked met, IR to 09,
  OEQ-02-10 result; `02-character-sim.md` caster table.
- ch.06: the I-006 paragraph and IR (b) to 05 marked done with section J numbers; `06-conflict-sim.md`
  section J results and decision line.
- ch.04: kept-pick edge case rewritten (no calling meets it now), Monk pole (04.2.6).
- `data/SCHEMAS.md`: `slot_class` gains `license`.
- I-008 decided: not gaps (DL-05-34). Generator now enforces 05.12.3 (shared mod_group needs `replaces`);
  05.6.8's Quiet column corrected to match the derivation (35 spells).
- DL entries: DL-05-31..34, DL-02-24, DL-02-25, DL-04-25.

## Step 6: I-020
- `gen_absorb.yaml` (hand-authored; no generator writes it): `no_pool` narrowed to the six human-like folk;
  beastfolk gates added (gnoll/ratfolk Predator's Nose, ratfolk Night Eyes, lizardfolk Gills and Scale
  Ward) so the narrowed rule has content; `signature_of` recorded on 25 entries (46 archetypes).
- `09-gen_data09.py` reads `no_pool` from the data and fails when `signature_of` disagrees with
  `archetypes.yaml`. Its loot-pool check had been silently failing on a Windows path in `08-loot-sim.py`
  (which suppressed every 09 emit); fixed. Re-run: 0 errors, output text identical, `archetypes.yaml`
  changes only in the folk absorbable blocks (gnoll and lizardfolk now have eligible entries).
- ch.04 04.10.5 and IR to 09; ch.09 09.11.3 and IR to 04 updated; DL-04-26.
- ch.05 re-emitted (absorbed-power mirrors carry the new gate tags).

## Step 7: I-003 non-combat parity
- Diagnosis (instrumented `04-recog04.py`): the envoy's tiers 3–5 stalled on weighted accrual and crises; craft
  was structurally capped (every crafting step Risky, so no crisis; no work above DC band 4, so no tier-5 great
  deed).
- Rules: 03.4.3 contest band (social/lore: opposing party's threat band or faction tier; craft: type-tier);
  03.4.5 **ruinous** (Dire + irreversible threatened cost; +2 points like lethal, 03.4.2) and **brink**
  (opposing clock one from full) as crises; 15.3.8 + new 15.3.11 (social contests), new 15.9.20 (lore
  contests), 08.6.4 item 6 (craft contests, Dire on irreplaceable material, scenes for fine+ works);
  `evidence.yaml` (challenge_band_source incl. the conflict advisory rule it lacked, flags, event fields).
- Sim: new `_process/simulation/04-recog-parity.py` (loads 04's engine unchanged, conflict opposition per
  DL-00-05, one play shape for all pillars, current vs revised rule sets). A trialled `cnt.prevail` counter
  was dropped (no pacing effect; counted never binds the contest pillars).
- DL-03-26, DL-04-28, DL-15-32, DL-08-30.

## Step 8: I-004 counted yield
- 06's fight model gained an evidence log (beats, defeats, flights); new `03-counted-yield.py` applies 03's
  points and saturation. Counted share 0.11/0.15/0.22/0.23/0.33 (bands 1–5, no Focus), 0.26–0.44 pushing.
  The ÷10 divisor costs one extra fight in eight only for a band-1 mob-only no-Focus fighter → kept
  (DL-04-27, DL-03-27). 03.7.3's arithmetic estimate replaced by the measurement.

## Step 9: close-out
- Generator path portability: `05-gen_data05/gen_data05.py`, `08-gen_data08.py`, `08-loot-sim.py`,
  `04-gen_data04.py` and the 02 scripts no longer need a Windows path. ch.08 regenerated: `gen_item_ability`
  pool 159 → 162 (the three element workings; branch workings and oath abilities excluded by its filter).
- Final reproducibility: generating 05, 02, 04, 09, 08 into a scratch copy and running `integration-merge.py`
  gives a `data/` identical to the live tree. `05-ladder-check.py` exit 0; `tables05.py --check` True.
- Appendix re-assembled (`integration-assemble-appendix.py`); anchors recompiled (`12-compile_anchors.py`,
  same 13 pre-existing warnings, I-031).
- Validator: 0 ERROR / 0 WARN (80 INFO).
- Ledger: I-003, I-004, I-007, I-008, I-009, I-015, I-020 resolved with evidence; new I-033 (EU weighting of
  damage-over-time conditions) and I-034 (04's pacing tables predate DL-00-05's opposition model).
- Not committed (FINISH-PLAN).
