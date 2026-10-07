# Revision B report: world, encounters, DM, items

Agent: Revision B (Opus). Scope: I-028 (top priority), I-029, I-030, I-031, I-032, I-022, I-016, I-017,
I-019, I-018, I-001 (`_process/FINISH-PLAN.md`, order of work item 2). Appended after every step.

## Step 0: baseline (2026-10-05)
- Read FINISH-PLAN.md, issue-ledger.md, revision-A-report.md, integration-report.md, BRIEF §9–12 and
  Addenda A/B, AUTHOR-BRIEF.md.
- Validator baseline: `python _process/validate_ruleset.py`: 0 ERROR / 0 WARN, 80 INFO.
- Generator reproducibility (each run into a scratch copy of `rules/`, then `integration-merge.py`, then
  diff against the live `data/`):
  - `10-gen10_sites.py`: identical.
  - `11-gen_factions.py`: identical after `integration-merge.py`. **Hazard found:** the script writes
    straight into `data/factions.yaml` (path from `__file__`), and its raw output lacks the owner-blocks
    that only the merge restores. Running it in the live tree without the merge silently deletes 2,886
    lines. Restored from git at once; from here it is only ever run in a scratch copy followed by the merge.
  - `10-gen10_travel.py`: **drifted.** The integration pass added the quartermaster journey role (ch.16's
    fifth role, 16.8.3) to `travel.yaml#roles` by hand; the generator did not have it, so a re-run would
    have dropped it. Ported into the generator (row plus its inline comment); output now byte-identical.

## Step 1: I-029 generic encounter tables, and I-022 site denizen tables (done)
- Diagnosis (shape matrix over every archetype, band and shape, `10-word-audit.py`'s field code): no single
  band-relative row works across home bands. Groups of three or more home-band foes are lethal from P2 up
  (T-09-10); a home-band minion mob of 4–6 is fair at P2 and lethal at P4; archetype band ranges forced clamps
  (troll 3–5 at home 1 → lethal). So I-029 is not a tuning problem but a shape problem.
- Fix: each generic terrain table now has one threat sub-table per home band (`threat_by_home`), 55 tables,
  hand-written with flavour notes in the new `_process/simulation/10_data_enc.py` (read by
  `10-gen10_travel.py`). Rows gain `variant` and `leader`. Home-5 home+1 faces are band-5 solos (09.8.2).
- 34 archetypes gained terrain tags in `09_data_arch*.py` (e.g. troll: road, wetland, frozen; ghost: road,
  wetland, frozen, deepwood, water). `09-gen_data09.py` re-run: only the terrain lists change; its printed
  output is byte-identical. The travel generator now checks every threat archetype lives in its terrain.
- `10-word-audit.py` rewritten (library + main): per-home tables, variants, leaders, `adv.*` refs for
  regional tables; new failures for a lethal high face, an out-of-band archetype, a broken shape rule; a
  repeat metric. Result: **55 / 55 pass** (was 7 / 55); word mix trivial 35.7 / easy 21.5 / fair 34.5 / hard
  8.2 / lethal 0 %; repeat chance max 0.195 (old max 0.255); 12–22 archetypes per terrain.
- PR-10-10 (new): `10_table_builder.py` builds a threat table from a weighted pool by slot, start shape
  (T-10-25) and step-down ladder to a word ceiling. I-022: `sites.yaml#denizen_pools` lists every pair's pool;
  the sites generator now fails on any pair below three archetypes (0 now; 20 before; the infested theme gate
  gained `creature.beast.monstrous` so it has band-5 creatures). `10-site-tables.py`: **560 / 560** pair × band
  tables pass PR-10-8.
- Chapter: ch.10 10.10.1 (row schema, two sub-tables, fielding), 10.10.2 (result), PR-10-8 (new checks, step 5),
  new PR-10-10, T-10-16 (re-rendered from data), new T-10-25, 10.13.13, PR-10-6 step 5, T-10-17 infested,
  two edge cases, the 09 interface row. SCHEMAS travel/sites; `10-exploration-sim.md`; DL-10-26, DL-10-27,
  DL-09-25.
- Validator: 0 ERROR / 0 WARN.

## Step 2: I-028 world seed — data and reference implementation (done; chapter text next)
- Searched first: ch.13 answered 77 interface requests (`region_thallen.yaml#interface_checklist`); a grep of
  every chapter for region/setting reads found 220 lines naming ch.13 or region data. Existing generators reused,
  not rebuilt: 11.3.18/PR-11-8 (faction templates, `tbl.11.faction_seed`, `tbl.11.faction_tier`), PR-10-6 and
  `sites.yaml` (sites), 12.11.1's NPC tables (`oracles.yaml`), `world_turn.yaml` (situation templates, hooks,
  rumor truth), `travel.yaml` (rings, terrain defaults, generic non-threat tables), PR-10-10 (new, step 1),
  ch.02's 02.3.5 placement (pregens).
- New `data/world_seed.yaml` (owner 12): 14 steps, 23 session-zero questions (each with closed options and an
  oracle roll, so player-guided, oracle or mixed), 13 oracle tables (12 wounds with pitch, truths, creature
  gates, situation, threat faction, goal and era; 12 keeper forms; peoples' presence; name parts for all eight
  peoples; place names; terrain by climate; haven sites; rulers; faction names; places of acceptance; calendar
  names; inciting incidents), the 05.7.10/07/15 canon defaults, haven furnishing by tier, and 62 requirements
  (T-12-27: every region read, the seed key that supplies it, the check).
- New `_process/simulation/12-world-seed.py`: runs every step from data, writes a region record of the
  `region_*.yaml` shape, builds each area's encounter table with PR-10-10 and audits it with PR-10-8 (imported
  modules), and checks all 62 requirements. Results (`12-world-seed-output.txt`, deterministic, byte-identical on
  re-run): seed 1 (oracle) passes 62/62 with 13 regional tables and 11 site tables all passing PR-10-8; a guided
  run (13 player answers) passes 62/62; 200 further oracle seeds pass every check (2,600 regional tables; word
  mix trivial 33.0 / easy 25.2 / fair 37.7 / hard 4.1 / lethal 0 %). Example committed:
  `12-world-seed-example.yaml` (seed 1: the High Fells, an invasion world, haven Merestead).
- Defect found and fixed on the way: 54 YAML mapping keys in `world_turn.yaml` (32), `pacing.yaml` (17) and
  `social.yaml` (5) were unquoted `on`/`true`/`false`, which YAML 1.1 parses as booleans (e.g. every
  `tick_sources[].on` in pacing.yaml read as `True`). Quoted (deep-equality verified); `validate_ruleset.py`
  now fails any boolean mapping key.

## Step 3: I-028 chapter text, the 13 re-point sweep, and the pre-made seed check (done)
- ch.12: new **12.16** (18 rules: what a seed is; who answers, with the one `[J:enum]` in template form; the
  fourteen steps; premise, canon, faith, peoples and tongues, land, haven, factions, cast, sites, tables,
  rumors, calendar, opening and pregens; the seed check; after the seed), **PR-12-9**, **T-12-15** and
  **T-12-16** (rendered from data: `12-world-seed.py --tables`), **WE-12-11** (the High Fells, every number from
  seed 1, with a guided boundary pair, a veto pair and a tempting non-example), `[SEED n/14]` label (12.15.15),
  12.5.1 (session zero now runs the seed), header, edge cases, state touched, interface notes, OEQ-12-11.
- Every chapter's references to ch.13 as a required source were re-pointed to the region's seed (12.16) with
  ch.13 named as one optional pre-made seed: 00 (9 edits incl. T-00-19, 00.17 Q19/Q20 and the 10/12/13
  contract rows), 01 (5), 02 (27), 03 (1), 04 (2), 05 (8), 06 (3), 07 (3), 08 (7), 09 (11), 10 (23), 11 (24),
  12 (6), 15 (3), 16 (2), SCHEMAS (region_*.yaml owner and keys; new world_seed.yaml section). Each carries
  `[revision: I-028]` where a requirement changed. ch.13: one framing paragraph only (its summary now says it
  is an optional pre-made seed, checked by 12.16.17).
- 00.16.2a regenerated (`integration-prefix-registry.py`): `ws.` registered (owner 12); region prefixes now
  owned "12 (a world seed's output) / 13 (an optional pre-made seed)".
- The seed check also runs on ch.13's `region_thallen.yaml` (`load_premade`): 58 of 62 hold. Four genuine gaps
  (no area-to-area routes; four tables with an undefined `leader+mob` count; situation steps without `trace`;
  one rumor pointing at prose) logged as **I-035, wontfix (owner: setting not used)**. Checks were made
  semantic (ids, not my generator's field names) so a hand-written or pre-made seed is judged on substance.
- Seed situations now follow 11.4.1's record exactly (title, region, actors, cadence, sealed timeline with
  `n/at/trigger/requires/prevented_by/key_delta/trace/bang`, `fired`), not ch.13's looser shape.
- DL-12-21..24 written; appendix re-assembled; validator 0 ERROR / 0 WARN.
- Data prose re-pointed through the generators, not by hand: `07-gen_data07.py` (afflictions "ch.13 may
  tighten" → the region's seed, 12.16.5; also ported the header drift `owner-block 07`), `04-gen_data04.py`
  (hybrid note), `05-gen_data05/lic_training.py` (licenses). Each regenerated in a scratch copy; the diff
  against live data held only the intended lines; `travel.yaml`'s header now describes `threat_by_home`.
  I-028 closed. Validator 0 ERROR / 0 WARN.

## Step 4: I-030 claim class `action` and every later "To 12" note (done)
- 12.3.1 now has 14 claim classes: `action` (a non-player entity's act) is checked against the act's closed
  source in the adjudication record (12.2.9; for allies 16.13.3's six reasons). An act with no source takes the
  existing verdict `unsourced_change` (its row extended). `pacing.yaml#claim_check.classes` updated.
- Every "To 12" note in 01–11, 15, 16 reviewed, 66 items (01: 6, 02: 6, 03: 6, 04: 6, 05: 4, 06: 4, 07: 5,
  08: 3, 09: 4, 10: 5, 11: 5, 15: 7, 16: 5). 19 edits applied with `[revision: I-030]`:
  - 07: owed `[WARNING]`/`[STATUS]` blocks fail the claim check and survive the plain fallback; a narrated
    death is a `harm_condition` claim checked against `harm_state.dead`.
  - 06: `position` checks T-06-4's words; PR-06-6 named as 12.2.9's enemy-turn step; T-12-3 cites 06.2.1 and
    06.13.1 and lists all four end conditions (it had one); a `[CONFLICT]` status-line row in 12.15.15
    (06.9.5 and WE-06-8 cite a "status line" no chapter formatted).
  - 05/08: the OFFER's Costs line names Focus, uses, flare and overdraw; a relic's surcharge gets its own line;
    drops are one line in RESULT; held abilities' cards load into the packet with rank text verbatim.
  - 09: the rotation ledger now keeps ch.09's eight challenge axes (09.8.5 said 12.9.2 kept them; it did
    not); T-09-13 cited; 12's own "To 09" note corrected from `reaction` to `reaction_roll`.
  - 15: the reason-to-lie flag (15.6.2) in 12.11.5; T-15-2 in 12.11.6. 10: the V face in 12.6.5 (d).
  - 16: any ally's death is a setback (16.9.5); an open personal thread is a lead-injection source.
- 47 items needed no text (already in force, or owned by the asking chapter); each reason is in DL-12-25.
- Validator 0 ERROR / 0 WARN.

## Step 5: I-031 anchor-compile warnings (done)
- 13 warnings → **0** (`12-compile_anchors.py`: 129 anchors, 0 errors, 0 warnings), fixed at the sources:
  knobs stated on 02.9.4 (adaptation table), 06.5.4, 06.5.10, 08.6.7, 09.2.4; intent verbs on 08.6.4, 08.6.7,
  08.6.8 (no more title fallback); T-06-9 rows 20/24/33/35/39 now lead with a basic verb (Move, Strike,
  Evade ×3; Defend and Full defense are named uses of `verb.evade`, 06.1.5). Row 20 gained its knob
  (`action_cost` +1 per Move) and row 24's knob cell was made parseable.
- Compiler fix: wrapped card text no longer leaves runs of spaces inside knob defaults (affected 4 other
  anchors' text only). `data/anchors.yaml` recompiled. DL-12-26. Validator 0 ERROR / 0 WARN.

## Step 6: I-032 world-sim agenda = 11.3.7 (done)
- `11-world-sim.py`: new `choose_action()` runs 11.3.7 cell for cell — overrides (a) slip, (b) war on d6 1–3
  against the war enemy, (c) `aid_pc`; every temperament row with its own condition (aggressive 3/4, cautious and
  mercantile `court`, zealous 3, secretive 3 at attention half and 4 `lie_low` at imminent, steadfast 2 `aid_pc`
  and 3 strike only at −3); target ladders; `court`/`aid_pc`/`lie_low`/discovered `scheme` effects and `recover`'s
  DC per 11.3.6. The stale docstring (ticks 3/2/1) fixed. `13-world-sim.py` no longer patches steadfast.
- **Rules defect found by the exact run:** `aid_pc`'s opportunity bang is always eligible, so override (c) made
  any faction at status +2 aid the PC every turn (20.5% of all turns; its goal starved). 11.3.7 (c), PR-11-2 and
  `factions.yaml` (via `11-gen_factions.py`, scratch + merge, one-line diff) now require a due aid (ransom,
  threatened holding, reward) or a d6 of 1.
- Re-run (300 seeds, byte-reproducible): goals 15/region/2y (was 21), ~2 per faction per year (target 1.5–3.5),
  goal share 67–70%, `aid_pc` 3%, mean tier 2.37–2.41 (was ~2.0), tier 5 0%. War is now decisive (the Cult falls
  at a median week 10–12), so the 11 sim's "PC at war" column reads 0 entanglements (p90 4); the Thallen re-run
  gives 8 (p10 5, p90 11). T-11-24 rewritten (plus two new rows: action mix, war length), its reading, 11.3.9's
  quote, OEQ-11-1, `11-world-sim.md`; ch.13's PR-13-4 (2.66–2.71 → 1.81–2.05) and 13.17.2's projections (Choir
  week 11–12; one collapse in a median run) — the same sim's quoted figures. DL-11-27. Validator 0/0.

## Step 7: I-017, I-019, I-016 loot pools and prostheses (done)
- `08-loot-sim.py` extended to the real bestiary (every `archetypes.yaml` archetype that yields loot × each band,
  186 cases, own `trophy_base`/gear/tags) and made reproducible (`zlib.crc32` seeds; `hash()` is salted). Found 75
  cases above the 15% repeat target (four at 100%) and 15 below the 09 contract's tier-1 pool of 3.
- `08-gen_data08.py#EXTRA_GATES`: 114 thematic gate tags on 58 properties; new `prop.tidesense` (I-019).
  Result: real bestiary mean 8.0%, worst 14.6%, 0 cases above 15%; contract 186/186 (water elemental tier-1 pool
  1 → 8). Reference set: clockwork sentinel 31.7 → 5.5%, slime 25.6 → 11.6%, mean 13.5 → 9.6%, worst 14.6%.
  Drop rates/rungs/compliance unchanged; craft sim output unchanged. T-08-16, OEQ-08-1, `08-loot-sim.md` updated.
- I-016: six prostheses (`item.tool.kit.prosthesis`, new level-3 tag) with `offsets {maim, narrows, never}`,
  slot `fitted` (08.5.1 row), T-08-1 fields; 07.7.6 and 07's maim offset texts point to them (07 generator; also
  re-pointed a stale "(13; default: none)" to 12.16.5). Data regenerated in scratch + merge; diffs only as intended.
- DL-08-31, DL-08-32. Validator 0/0.

## Step 7b: I-028 follow-up — the data sweep finished
- A wider grep (single-quoted YAML hides `13''s`) found 52 more data strings that still named ch.13 as the source
  of setting content (rituals' discovery paths ×24, tongues, NPC tables, calendar, gift givers, the conjured-coin
  rule, hold order, hoard keys) plus seven "10/13" / "11/13" pointers in 00, 05 and 08. Re-pointed at their
  sources: 02 (`gen02`, `gen_contrib02`, `creation_block`), 05 (`emit05`, `lic_training`, `rites05`), 07
  (`gen_harm07`), 08 (part2), 10 (travel), 11 (factions), ch.15's licence fragment, and the hand-authored files
  (calendar, oracles, origins, pacing, tags, vehicles, world_turn). Every generator was re-run in one scratch copy
  (02, 05 `--emit`, 07, 08, 10, 11, then merge); the diff against live data held only the intended lines.
- **Caught on the way:** two hand edits had produced invalid YAML (an unescaped apostrophe inside single-quoted
  strings in `licenses.yaml` and `rituals.yaml`); both files were replaced by the regenerated, valid output. Every
  data file now parses; validator 0 ERROR / 0 WARN. `owner-block 13` headers are kept: they describe how a
  pre-made seed such as ch.13 adds blocks, which is still true.

## Step 8: I-018 campaign wealth and power simulation (done)
- New `_process/simulation/08-campaign-sim.py` (seeded, byte-reproducible; 300 campaigns × 70 sessions; P1–P5 by
  04's pacing; two fights a session rolled on the generic encounter tables at home band = PC band, the real
  archetypes' yields and purses; site treasure ~1 session in 4; 08's generator code imported from
  `08-loot-sim.py`; half-list sales through `clk.find_buyer`; lifestyle the only sink).
- Finding (rules as shipped, 60 campaigns): property items P3 22 and P4 45.5 against 08.2.7's 8–12 and 15–25, a
  full row ahead (1.5 and 2.1 items a session): routine. Cause: 08.2.7 counted the drop check only; hoards (sites,
  and band-5 solos met at home+1 whose hoard generated on the road) and always-drop principals came on top.
- Retune (rules + `08-gen_data08_part2.py` + `gen_loot.yaml`): drop check 10/15/30/40/55; hoards T3 1 masterwork,
  T4 1 wondrous, T5 1 wondrous + 1 masterwork; a hoard-keeper away from its lair rolls as a trophy (08.3.3,
  08.3.12, PR-08-1). Result: P1 4, P2 6, P3 13, P4 24, P5 21 in 14 sessions (1.56 a session); bound attuned and top
  signature tier inside 08.2.7's columns; masterwork share 73%. Coin one tier ahead at P3–P4 (no sinks modelled).
- T-08-17 added; T-08-16, 08.2.7, 08.3.3, 08.3.12, PR-08-1, OEQ-08-2/-4, `08-loot-sim.md` updated; loot sim
  re-run (rates 7.3/16.0/32.5/38.8/55.3%, repeat results unchanged). DL-08-33. Validator 0/0.

## Step 9: I-001 the [J]-rule worst-case form (done)
- Audit (script): 239 rules carry a `[J:*]` decision; 86 use the 00.2.5 block, 153 give the worst case inline,
  0 omit it. Inline labels came in 20 spellings (*Worst case:* ×107, *Worst case (J):* ×27, *Worst case of …*,
  *Worst case (tier):*, wrapped and lower-case forms).
- Decision: both forms comply; the inline label is *Worst case (J):* (qualifier allowed). 00.2.5 amended.
  `norm.py` (scratch) rewrote 127 labels in 13 chapters (ch.13 excluded by the owner's constraint; its one legacy
  label is accepted and counted apart); a second run changes nothing. The marker is on 00.2.5 and DL-INT-12
  rather than on each of the 127 label edits.
- `validate_ruleset.py` JRULES now fails a missing or non-canonical label and reports: block 86, inline 152,
  ch.13 legacy 1, non-canonical 0, missing 0. Validator 0 ERROR / 0 WARN.

## Step 10: close-out (done)
- Re-verified after every data change: `12-world-seed.py` output and example byte-identical (PASS, 62/62);
  `10-word-audit.py` 55/55, 0 failures; `10-site-tables.py` identical (560/560); `08-loot-sim.py` and
  `08-campaign-sim.py` re-run on final data; `11-world-sim.py` and `13-world-sim.py` reproducible.
- `12-compile_anchors.py`: 129 anchors, 0 errors, 0 warnings. `integration-prefix-registry.py` re-run. Appendix
  re-assembled (DL-08-31..33, DL-11-27, DL-12-25..26, DL-INT-12 added this revision, after DL-09-25, DL-10-26..27,
  DL-12-21..24).
- Ledger: I-001, I-016, I-017, I-018, I-019, I-022, I-028, I-029, I-030, I-031, I-032 resolved with evidence;
  I-035 (ch.13's four seed-check gaps) wontfix, owner: setting not used.
- Validator: 0 ERROR / 0 WARN. Nothing committed.
- Open, by design: OEQ-08-4 (coin runs one tier ahead at P3–P4 because the simulation spends only lifestyle;
  real sinks are the player's choices); P3's item count sits one item above 08.2.7's row (13 vs 8–12); war
  between tier-1 neighbours is decisive within a season (kept; DL-11-27 names the revisit trigger).
