# Verification-2a report (Wave 4, V2a)

Agent: V2a (Opus). Scope A: full consistency read of ch.04-08 (section by section via `rq.py`), numbers, worked examples,
cross-references, undefined terms, executability, cross-chapter contradictions. Scope B: constitution audit
(`verification-constitution.md`). Edits tagged `[verification: V2a-NNN]`; design-level findings become ledger rows
after I-062 with status "open (Revision C)". Appended after each chapter. Nothing committed.

## Step 0: baseline (2026-10-07)
- Read CLAUDE.md, FINISH-PLAN.md (last two sections), verification-1-report.md. Ledger runs to I-062.
- Not re-reported here: V1 findings I-037..I-062 (e.g. I-042 Wren V12 in 06/07/12 traces, I-045 pacing mix, I-046 "brink", I-057 branch-working attribute, I-058 self-healing).

## Step 1: ch.04 (sections checked: 04.1-04.11 with all subsections, PR-04-1..9, T-04-8/11/12, WE-04-1..9, edge cases, state, interface requests)
Recomputed: roster sum 183; counted = weighted/10 (8/20/44/80/130); parity percentages (-5/-5/-11, -10/-12/-10); 28-point scene cap and 7-point conduct cap against 03.5.2/03.8.2; DC bands against 03.4.3; confirmation thresholds 3/10 of W1; K1-K5 arithmetic and every WE-04-1 tally (balance 1,200 vs 1,182; legacy picks 3 then 2; decline re-offer at 143); R9 ratios; WE-04-6 strain and clock; WE-04-7 odds (11+ = 50%, S2 = 3 Vitality per 01); WE-04-8 "fifteen more scenes"; gen_absorb 27 / 25 / 46 against data.
Tooling fix:
- V2a-001 `rules/tools/rq.py`: headings inside ``` fences (every procedure card: "### 04.6.2  Vehicle selection" etc.) were treated as section boundaries, so `rq.py 04.6`, `04.7`, `04.6.2` and every fenced card printed only its heading. Fences are now skipped when indexing; TOC id counts for every chapter unchanged.
Fixes:
- V2a-002 04.6.4 example: Wren's archery "62 of 80 -> becoming" was on_the_threshold (>= 3W/4 = 60); now 52.
- V2a-003 04.7.5: "binds exactly one price" contradicted V5/V7/V11 offers with no price; now "at most one".
- V2a-004 04.9.6: "three stage notices" is false when a forbidden act opens stage 3 at once; reworded.
- V2a-005 WE-04-1 consolidation table: Tracker tier 2 also had the wilds Focus trigger; "martial and wilds Focus triggers" / "two Focus triggers are retired".
- V2a-006 04 intro and State touched (also 07 and 08 intros): `data/contrib/*.NN.yaml` no longer exists; now the owner-blocks of the shared files.
- V2a-007 04 IR to 03 (c): Devourer opponent kinds ">= 6" against 04.2.6 and `req.variant.devourer` 5.
Ledger: I-063 (04.5.1 modifier envelope vs 00.3.7 bands).

## Step 2: ch.05 (sections checked: 05.1-05.12 with all subsections, PR-05-1..9, T-05-8/9/12, WE-05-1..9, edge cases and anchor cards; interface requests scanned for numbers)
Recomputed: every 05.11.5 allowance/value; census 175+180+171 = 526 ranks, 239 budgeted; pool 179+57+3+27 = 266 and T-05-12 rows and columns (122/40/46/20/38, 81 tags); composites 8/5/9/32 and 18 `composite_key` abilities against data; 24 rites and 81 training licenses against data; focus.max table; branch-working allowance 4/6/8; learning paces (2 weeks, 6 emulations, 3 weeks from a text); WE-05-1 odds (90% / 40% / 5%) and harm (S4 = 8, crit S5 = 12, backlash 12 -> 4); WE-05-2 (DC 20, 20%); WE-05-5 fight trace, venture-day table (13 Focus spent, 8 restored) and the 2/3 and 4/5 pool shares; WE-05-6 (55%, 5 Focus); WE-05-7 rite trace (6 intervals, strain 3/4, effect DC 15); WE-05-8 overdraw (9-3-1 = 5) and Force Bolt (80%, 5 harm, crit S4). S-to-harm, drain and Oracle odds checked against 01's tables.
Fixes:
- V2a-008 05.6.5: "the two effects above are all it does" after a list of three; now "the effects above".
- V2a-009 WE-05-4: "the next four tier-ups" of a tier-2 Ranger; only three remain (to tier 5), one legacy pick stays outstanding.
Observations (no edit): T-05-1..7, T-05-10, T-05-11 are indexed only in 05's prose table index, so `rq.py T-05-5` returns "not found" (PR-05-4 cites T-05-5); look them up by their section ids.
Ledger: I-064 (divine regard fails at Fraying stage 2 in 05.7.4; 04.9.3/04.9.4 keep the calling working one tier down at stage 2).

## Step 3: ch.06 (sections checked: 06.1-06.15 with all subsections, PR-06-1..10, T-06-12/13/14/2, WE-06-1..9; tables T-06-1/4/5/6/7/8/10/15 read in their sections; edge cases and OEQs scanned)
Recomputed: repetition odds (55/45/35%, 84%); Guard 14 and 16; pace halving (1,1,1,2); T-06-8 one-rung worst case (2-4); 27 conditions (23 + 4) and the eight control conditions; every T-06-13 cell's word against its thresholds; the 06.10.6 targets against T-06-13 and T-06-14 (4-foe "lethal at every band but P1", mob 3% vs 43%, 62 -> 84 push, Defend 99.4 vs 99.7, Fend 62 -> 46, called gap 62 -> 73); every roll in WE-06-1 (tempo 16; 65/50/80% shots; morale 2 + 1 + 2 + 2 >= 6 at strength 3 of 22; chase 3/8 -> 8/8); WE-06-2 (Aim 80%); WE-06-3 (20%); WE-06-5 mob pool 30 -> 27 -> 24 -> 19 with members 6/5/4; WE-06-6 (65%); WE-06-8 (70%, 50%, crit 20%); WE-06-9 chase clocks.
Fixes:
- V2a-010 T-06-14 readings: "armor is worth 7-23 points and Fend 1-17" against the table (armor 1.6-23.1, Fend 0.2-16.7); now 2-23 and 0-17.
Observations (no edit): `rq.py T-06-13` returns the pointer paragraph in 06.10.6 ("is in Tables"), not the matrix at line ~1783 (first definition wins); read it by line range. Wren's Vitality 12 in WE-06-1/5/8 is I-042, not re-logged.
Ledger: none.

## Step 4: ch.07 (sections checked: 07.1-07.12 with all subsections, PR-07-1..12, T-07-10/11/14/15/18/20, WE-07-1..7; edge cases, interface requests and OEQs scanned)
Recomputed: every T-07-18 "hits to Stagger, then to Dying" cell at P1 and P3, armored and unarmored (16 cells); Gamble odds at Endure +2 (5/35/15/45%); T-07-15 days to heal (4/2/2, 6/3, 12/6) and 07.2.8's brink claim; 07.8.11 convalescence claim; 07.10.4 "falls within three turns"; the wound-penalty / floor arithmetic of WE-07-1 (12-9 = 3, floor 6; dread 1+1+2 = 4/7; six options, four not death); WE-07-2 (crit failure at -16; load 2 + 3 = 5 -> Down); WE-07-3 stage sequence (four checks of six; Vitality 12 -> 10 -> 7 -> 4 -> 1); WE-07-5 rest branches (6 / 5 / 3) and both healing columns; WE-07-6 (dread 5 + 2 = 7, steeled to 3); companion Vitality 6/12/16/18/20 against `companions.yaml`; Treat odds (65%, 40%).
Fixes: none needed in ch.07 text (the 07 intro's contrib reference is V2a-006, under Step 1).
Ledger: none new (Wren's Vitality 12 throughout WE-07 is I-042; 07.1.2 "confirmed tiers only" is I-037).

## Step 5: ch.08 (sections checked: 08.1-08.10 with all subsections, PR-08-1/5/6/7 read, PR-08-2/3/4/8/9 skimmed, T-08-3/14/16/17, WE-08-1..11; OEQs scanned)
Recomputed against data: base items (191), properties (211; 76 signature-eligible; 18 license), item-ability pool (162), materials (59), default signatures (45 = level-2 creature tags); loot-sim output (refills, share breaches); T-08-14 against 08.6.4 and 08.6.6 prose; 08.2.6 table (+6/+10/+12, 17/10/8%, 4/6/10 harm); capacity 10 + 2 x Might; purse means (1.5/7/19/53/135); every WE price (80, 175, 170, 60-coin commission), haggle (55%, 40), find_buyer weeks, load sums (8, 7+4, 18, 15, 14), study and repair odds.
Fixes:
- V2a-011 08.1.2: "185 base items"; data holds 191 (six prostheses added by I-016).
- V2a-012 08.2.6: P5 item edge "between 40% and 45%" against Very hard; at +11/+12 vs 25 it is 35% / 40%.
- V2a-013 08.2.4 / 08.2.5: refills "16 in 1,000" and share breaches 18.4 / 19.4 / 26.6% were pre-revision-B figures; T-08-16 and `08-loot-sim-output.txt` say 10, and 20.2 / 11.2 / 30.6%.
- V2a-014 design notes and T-08-3: "210 properties"; data holds 211 (Tidesense, I-019); its family row 23 -> 24.
- V2a-015 WE-08-3: ring list price 5 x 10 + 250 + 50 = 350, not 300 (still band 4).
Ledger: none new.

## Step 6: constitution audit
`verification-constitution.md`: Core Principles I-VII all compliant (3-5 rules spot-checked each); patterns 15 compliant,
P5 and P14 deviating with DL justification (DL-04-10; DL-06-02, DL-05-29); BRIEF §6 "Focus is the TTRPG" compliant;
card-level traceability deviating with no DL (216 of 424 ch.04-08 cards carry no `[C:]`/`[R]`/`[DL-]` tag; 37 cite
nothing at card level): ledger I-065. Fix V2a-016: stale contrib file names in `appendix/fragments/trace-04.md` and
`trace-05.md`; appendix re-assembled.

## Step 7: close-out
| Chapter | Sections read (parts, cards, PR, T, WE) | Fixes | Ledger rows |
|---|---|---|---|
| 04 | 76 ids + 9 PR, 3 T, 9 WE | 6 (V2a-002..007) + rq.py (V2a-001) | I-063 |
| 05 | 101 ids + 9 PR, 3 T, 9 WE | 2 (V2a-008, 009) | I-064 |
| 06 | 114 ids + 10 PR, 4 T, 9 WE | 1 (V2a-010) | - |
| 07 | 101 ids + 12 PR, 6 T, 7 WE | 0 (intro reference fixed under V2a-006) | - |
| 08 | 92 ids + PR-08-1/5/6/7 (others skimmed), 4 T, 11 WE | 5 (V2a-011..015) + intro under V2a-006 | - |
| constitution | 7 principles, 17 patterns, 2 non-negotiables | 1 (V2a-016) | I-065 |
- Validator: `python _process/validate_ruleset.py` 0 ERROR / 0 WARN. Anchors recompiled: 129, 0 errors, 0 warnings.
- Not done (handoff): ch.08 PR-08-2/3/4/8/9 skimmed only; interface-request blocks of 05-08 scanned for figures, not read line by line.
- Nothing committed.
