# V1 notes (scratch)
## Traceability pre-checks
- ISSUES dict in integration-assemble-appendix.py hardcoded; lists resolved rows (I-009, I-015, I-028, I-003, I-007, I-020, I-008) as "Open issues" -> stale. Mechanical: derive from ledger open rows.
- Fallback label truncation sat[:60] produces "(factions with tiers, holds, ratings, stages, linchpin fates,)" — cosmetic.
- P7 codex: ch.14 unwritten (Wave 6) but row says met.
- ch.13-only satisfiers: OB-02 first-session teaching arc (13.15.5); CC-12 pregens; CC-13 names; LW-12 truths; TM-07 calendar; SO-04 languages; R6 B-15 West Marches. Check world seed covers each.
- P13 gate "MUST NOT share model family" — check ch.12 claim check.
## ch.00 (read fully)
- WE-00 arithmetic recomputed: WE-00-2 (24, crit; 25/50/25), WE-00-4 (+4 vs 15 -> 50/5/5/15 near), WE-00-6 (needs 12 = 45%; S4 8+1=9; 16->7 bloodied) all OK. WE-00-1 travel timeline OK.
- WE-00-2 step 6/log: weights shown 1/2/1 after halving, but 00.11.3 step 7 says every weight is doubled before any is halved (integers) -> should read 2/4/2 (same 25/50/25). MECH fix.
- T-00-9: h.07.dying_check registered on BOTH turn_end and round -> possible double Dying advance per round; check ch.07 07.2.x.
- 00.3.7 band table: PC best-domain base mod P1 +4..+6 — check vs ch.02 creation numbers.
- 00.4.4: Wits->tempo, Might->carry, Presence->retinue, Resolve->strain threshold, Intellect->languages. Verify 06.2.2, 08.9, 16.2.1 (clamp(2+Presence,1,6)), 07.11 (8+Resolve), 02.
- 00.7.2: rest_long at most one per day; reflection at most once/day.
- 00.15.4 packet cap 12 cards, last 4 exchanges (pacing.yaml#packet).
- P13 gate model family: 00 says check_claims tool (RC-AUDIT) "claim-versus-state comparison over the store" — deterministic? see ch.12.
- 00.16.3: all entries provisional "until the verification wave promotes it to permanent" -> Verification is supposed to promote?? Out of scope design decision -> ledger (VI: promotion procedure for content scale has no criteria/owner).
## ch.01 (read fully)
- All WE-01-1..20 arithmetic recomputed vs T-01-3/T-01-10: all correct.
- Wren Vitality: 00 says 13/13 (12+Endurance +1); 01 header & WE-01-3 use 12; 02:2238 says Vitality 12 "after Bent"; 05/06/07/12 use 12. Need ch.02 ruling: is max Vitality recomputed when Bent raises Endurance? (00.3.12 "creation value"). -> consistency finding.
- REDTEAM: free Oracle lever-fishing. G0 questions cost no time/action; a player can ask "is there loose grit / a ledge / a crate" (Likely 75%) before each declaration, then cite yes-answers as levers (01.15.8 allows pre-declaration answers as levers). Caps: 2 levers, +4, so max +4 on every roll at zero cost. Check whether 12 / tension or precedent limits. 01.15.7 only blocks re-asks of same key. Likely MAJOR design: ledger.
- REDTEAM: Help lever from companion every roll (+2) — bounded.
- 01.16.2 fate: hard luck once per scene, cap 2; deliberately crit-failing Risky Safe frames? Only Risky/Dire, which cost S3. Thread completed +1: farmable by trivial threads? check ch.11 thread creation (player-declared vows?). note.
- 01.4.4 take the time: UNCERTAIN not COSTLY -> auto success at Standard reach, twice time; not for VH/Legendary. Fine.
- 01.4.2 re-attempt cost S1 when Safe — fine.
## ch.02 (read fully)
- WE-02-1/2/3, WE-02-4 arithmetic recomputed: all OK (pools, weights 59, DCs 11/15, 55/35%, Guard 14/15/11, knack pools T-02-9 spot checks).
- MECH: Wren after Bent = Vitality 13 (02.7.1 + PR-02-5 "12 -> 13"). 02 IR "00-3" and WE-02-1 parenthetical say 00 shows 12 -> stale (00 now 13/13). 01 header "Vitality 12" + WE-01-3 V track (12->11->10->9->8; "V 2") are stale -> fix to 13 (13->12->11->10->9; without license V 3).
- MECH: T-00-7 tag tree omits deed.craft.scribing and deed.influence.teaching (tags.yaml has 81 level-2 deed tags; T-02-5 says 81). Script-check all facets of T-00-7 vs tags.yaml.
- 02.11.1 / OEQ-02-7: "first recognition at about the fourth session (04's pacing: median session 4)" — check 04.3.5 (I-034 open: 04 pacing from old model).
- 02.6.5 Bent eligibility: 3 resolved frames in a branch; resolved frames include trivial rolls? Bent pool shaping (grind frames in a branch to steer Bent) — legit P5 design; minor redteam: farm cheap Safe frames in chosen branch to steer the Bent. Bounded (+1 once). note only.
- REDTEAM 02.2.6 second look after a failed roll: OEQ-02-9 logs it. bounded once.
## ch.03 (read fully; tail skimmed)
- WE-03-1..16 arithmetic recomputed: all OK (55% difficult, 8/6/3->11, 13 vs 12, strain 4->3->2->6, share cross-mults).
- REDTEAM candidate (I-003 contest band): social contest band = max(opposing party threat band, faction tier) for "someone who speaks for a faction". A P1 talker petitioning a functionary of a tier-5 faction gets challenge_band 5 -> peak flag on every success (peak = band >= power_band+1), peak_band 5, i.e. qualitatively-distinct higher-tier evidence without danger. Limits: same-target day cap, DR per scene, routine cap (quality relative), D2 aware opponent true. Check 15.3.11 definition of who qualifies; compare: combat band-5 deed needs lethal-advisory fight. -> likely ledger row (MAJOR?) "contest band lets P1 farm band-5 peaks from minor faction functionaries".
- Same for craft: band = type-tier of work (08.6.1) — check if a P1 can attempt type-tier 5 work.
- 03.1.3/PR-03-6: level-2 children: martial 12, arcane 11, craft 11 > 00.2.2's ~8 enum guideline; PR-03-6 sibling budget 8 applies only to new admissions. Classification is level-by-level; 12-way enum. Minor design note (OEQ-00-1 tests attribute; no test for 12-way level-2 classification). maybe OEQ-03 covers. low priority.
- 03.2.8 backstory evidence unused by 02 (02.11.1) except successors. consistent.
## ch.04 (reading)
- MAJOR consistency: power_band defined two ways. 04.5.6 counts provisional tiers ("provisional included"); 07.1.2 reads power_band "from confirmed tiers only (00.17.1 Q5)"; 00.17.1 Q5 says "recognized tiers only". 04.5.6's parenthetical points at "issue I-028" which is the world-seed row -> the original issue was lost in renumbering: dangling thread. Affects Vitality max, 09 advisory, 03 peak, 16 band cap. LEDGER (design: which). Mechanical part: fix the stale I-028 pointer to the new row.
- 04.3.5 pacing table (old band..band+2 model) vs 03.4.3/09.12.3 "5/11/22/39/60" vs parity 19/51: = I-034 (open). 02.11.1 "median session 4" same. Note under I-034 in consistency report.
- ch.04 WE-04-1..8 arithmetic recomputed (K1..K5 cross-mults, balance 1200>=1182, cooldown 143, legacy picks 3/2, Tamsin 50%): all OK.
## ch.05 (reading)
- REDTEAM downtime loop: 05.9.3 a training license learned by mentor (8-seg clock, 2/week = 4 weeks) or text (8 weeks) carries competence +2. Origin "access" licenses carry none (02.5.2). Unbounded: every 4 downtime weeks -> +2 on a new tag; no cap on number of +2 trainings (02.1.3 caps "at most two tags above floor" only at creation). Undercuts P4 breadth/competence decoupling & recognition. Check 15 training activity for limits. Also contradiction: an access-held license re-learned? INV-13 -> nothing; so Broad char can never get +2 by mentor on access tags (held) but CAN on new tags: perverse.
- REDTEAM rest/Focus: wilds Focus trigger "a breather completed outside any settlement" +1 once per scene; breathers past 2 restore 0 but trigger still fires each scene -> 1 Focus per interval-scene. Generation cap 3/scene; time cost only. minor.
- 05.6.1 T_high counts provisional tiers "as they do for power_band" -> consistent with 04.5.6, inconsistent with 07.1.2 (see power_band row).
- 05 WE-05-1..8 recomputed OK (90%/40%, S5 12, miscast 12->4, stretch 20%, rite 6 intervals, overdraw 9-3-1=5, Force Bolt 80%); T-05-12 row/column sums = 266 OK; 05.11.5 budgets OK.
- MECH STALE (I-009): WE-05-5 sim table Ash rows (staff, no branch working: 0.1% / 81.3% / 40.7%) and reading "(3) ... a caster without Focus is nearly helpless against an equal foe (0.1%), which is the lever that makes overdraw ... matter" contradict 05.6.5/05.7.11 (Spent T3 caster 80.7-91.0% vs one T3, 06-sim J2). Fix: label rows as pre-I-009 staff model; rewrite (3) citing J2.
- MECH: WE-05-5 traced fight "Vitality 12" for Wren with Endurance +1 -> 13 (12->9 becomes 13->10).
- 05.9.4 explicitly accepts unlimited training licenses at +2 each ("breadth is available and is not power"); keep red-team item but cite as stopped-by-design-intent; residual: contradicts 02.5.2 access (no competence) — ledger MINOR.
