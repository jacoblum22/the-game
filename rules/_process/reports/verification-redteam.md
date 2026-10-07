# Verification: exploit red team, ten highest-risk (2026-10-06)

Method: each exploit was stated as a player's loop, then checked against the rule text by grep and read (rule ids cited). "Stopped" means a rule closes it; "gap" means no rule does, with a proposed fix in a ledger row. Two candidates came from the chapter 00–03 read (verification-1-notes.md); the rest from the brief's list plus what the playtest and the chapter 04–12, 15, 16 pass surfaced.

| # | Exploit | Verdict | Stopped by / gap | Ledger |
|---|---|---|---|---|
| 1 | Free Oracle lever-fishing | **gap (MAJOR)** | see below | I-038 |
| 2 | Contest-band peaks from minor faction functionaries | **gap (MAJOR)** | see below | I-039 |
| 3 | Re-fighting one foe each day for evidence and loot (sparring partner, hired sellsword, released prisoner) | **gap (MAJOR)** | see below | I-041 |
| 4 | Recognition by counted evidence loops (practice pushes, training weeks, projects) | stopped | 04.3.3, 03.5.5, 03.7.3 | (I-047 residue) |
| 5 | Crafting and economy arbitrage (buy/sell loop, craft-to-sell, magic-made coin) | stopped | 08.8.4, 08.8.5, 08.8.9 | none |
| 6 | Rest and downtime loops (Focus, healing, reflection, week plans) | stopped | 05.6.9, 05.6.10, 05.7.8, 00.7.2, 15.10.2 | none |
| 7 | Companion and retinue stacking | stopped | 06.1.1, 06.1.6 (d), 16.2.1, 00.3.9 | none |
| 8 | Death avoidance (last-chance menu, fate, retreat, brink laundering) | stopped | 07.2.8, 07.5.2, 01.16.2, 07.4 | none |
| 9 | Social terms and certainty (a Neutral NPC grants favors with no roll) | partial | 15.3.4, 15.3.5, 15.3.10 | I-048 |
| 10 | Training licenses without limit (+2 competence each) and access vs training | partial (by design, with residue) | 05.9.3, 05.9.4, 15.11.6 | I-047 |

## 1. Free Oracle lever-fishing (gap)
- *Loop.* G0 questions cost no time and no action (01.3.8). 01.15.8: an Oracle answer to a question asked *before* a declaration is an established fact and may be a lever for it. Before every beat the player asks "is there loose grit on the floor? a ledge? a crate? a stream?" at **Likely** (75%, 01.15.2). Two levers cap at +4 (00.3.9), so +4 on every roll costs nothing. The same channel supplies Protective facts that drop a lethal frame to Risky (WE-01-3: the trough by the door).
- *What stops it today.* 01.15.7 only forbids re-asking the *same key* (a question whose key already has an answer is read, not rolled), and says fishing gets odds from the scene. The tension dial may shift odds one rung (00.12.7). No limit on how many such questions a scene may ask, none on how many may be used as levers, and a "no" is only a fact about that key.
- *Fix (ledger row I-038, default to adopt).* An Oracle answer used as a lever is **spent**: (a) at most one Oracle-sourced lever per frame; (b) odds drop one rung for each Oracle-sourced lever already used in the scene (Likely, Even, Unlikely, Remote); (c) the question must be about a feature the scene's `situation.*` tags plausibly hold (the J:flag the rule already uses for Oracle odds). Fix lives in 01.15.7–01.15.8; the OFFER cites the odds it was asked at.

## 2. Contest-band peaks from minor faction functionaries (gap)
- *Loop.* 15.3.11: a Talk frame aimed at "anyone who speaks for a faction on the faction's business" is a social contest, with contest band = the higher of the opposing party's threat band and the tier of the faction it acts for. A P1 talker petitions the tier-5 faction's door-warden on the faction's business: every beat takes `challenge_band = max(DC band, 5)` (03.4.3); successes set `peak` (band ≥ power_band + 1) and peak band 5, the evidence tier-4 and tier-5 great deeds are built from, with no danger (a combat band-5 deed needs a lethal-advisory fight).
- *What limits it.* Same-target day cap (03.5.4: a rematch on a *later day* counts normally), diminishing returns per scene (03.5.2), the routine cap on quality (03.5.3, which is relative to the *difficulty*, not the band), `D2` aware opponent. None reduces the band the functionary lends.
- *Fix (I-039).* The contest band is the faction's tier only for a party who **can bind the faction** (a principal, an officer with an authority recorded, 12.11.1) and never above `power_band + 2`; any other speaker counts band 1 or their own threat band. Same cap for craft (08.6.1 type-tier work: material gate, 08.3.4, already limits it; confirm in the sim).

## 3. Re-fighting one foe each day (gap)
- *Loop.* 03.5.4 closes the same-target loop within a day, and says "a rematch on a later day counts normally". 08.3.1 generates loot once per defeated side per conflict (and again for a yielded creature searched outside a conflict), with no per-creature lock. A hired sellsword (Zzirik Swift, a minor NPC with a blade), a friendly duelist, or a released yielder is defeated non-lethally once a day: counted defeat (03.7.2 `cnt.defeat`, band units), judged evidence, a drop check at the foe's band, and the foe's purse again.
- *What limits it.* Day cap on evidence per target (one per day); the drop check at 10–55%; relic tier cap by band. Nothing limits a daily loop, and its cost is only the NPC's willingness (a friendly one is paid in lifestyle units, 08.8.8).
- *Fix (I-041).* (a) A creature that has yielded loot or been defeated by the PC is **marked** (`looted_by_pc` with a date); it generates no further drop or purse until a season has passed and its gear is replaced from its own stock; (b) the same-target cap for an NPC who is not an enemy by record (standing ≥ Wary, or a hired or friendly spar) becomes a **week**, not a day, at every node (03.5.4 extension); a sparring bout between consenting parties is `situation.downtime.training`, not a conflict (no loot, 03.5.5).

## 4. Counted-evidence loops (stopped)
- *Loop.* `cnt.focus` credits Focus spent on a push (03.7.2); rests restore up to roughly two pools a day (05.6.9: long rest to max, two short rests of half, two breathers of +1); safe "practice" beats pushed for units; training weeks; `cnt.progress` and `cnt.made` from projects.
- *Stopped.* The counted requirement is **in addition to** the weighted requirement (04.3.3: counted = weighted ÷ 10, so a tier needs both); practice is Safe, unopposed, routine and never judged evidence (03.5.5, 03.5.3); `cnt.training` counts toward at most half of the counted requirement (04.3.3); saturation per counter and per node within a scene (03.7.3). Counted alone never crystallizes a tier.
- *Residue.* Whether Safe projects (15.12) saturate `cnt.progress` per day is not stated; recorded as one of the open checks in I-047.

## 5. Crafting and economy arbitrage (stopped)
- Buying asks list + 1 notch (08.8.4); mundane items sell at half; trade goods sell at list in a scarce market and at list − 1 notch in a common one (08.8.5): no round trip profits. What a seller made sells for at most materials plus the maker's wage (08.8.9 item 2, the labor cap); property items sell only through `clk.find_buyer` in towns and cities (item 3); market depth caps weekly coin (item 4); glut lowers repeat sales (item 5); conjured goods are worth 0 (item 1); coin enters only through tables (item 6). Transmutation is G4 unless the seed allows it (this seed: `no_gold_making`).

## 6. Rest and downtime loops (stopped)
- Focus: breathers restore Focus only twice between short rests; two full short rests a day; one long rest a day (05.6.9; 00.7.2). The wilds trigger (a breather outside a settlement) and every other trigger share a cap of 3 generated Focus per scene (05.6.10); consumables 4 between long rests (05.6.11). Healing: at most two healings per recipient between long rests (05.7.8). Downtime: one week activity plus two day activities per week (15.10.2); lifestyle is charged every week spent in a settlement (15.10.3); each week is a World Turn and every day runs situation timelines, so a loop is paid in a clock (15.10.3, 11.2.1).

## 7. Companion and retinue stacking (stopped)
- A companion has 0 actions and acts only when the PC spends an action to command it (06.1.1, 06.14); each commanded companion has its own repeated-attack window per PC turn (06.1.6 d), but the PC pays an action per command; the retinue cap is clamp(2 + Presence, 1, 6) (16.2.1); help is one lever and the two-lever cap applies (00.3.9, 01.14.8); interception by companions is a reaction, one per round (06.6.7). A companion's death is a setback (16.9.5).

## 8. Death avoidance (stopped)
- The last-chance menu is offered at the Threshold with prices (07.5.2), not on request; each stabilization leaves a brink wound and the next fall enters Dying at step 1 + brink (07.2.8); the bargain's costs escalate ("her next reprieve would cost 2", WE-07-1); fate is earned only by hard luck (once per scene, never above 2), a completed thread, or a kept vow (01.16.2), and spending it is a reroll with a price (01.16.3); yield and retreat carry stated costs (07.4); a lethal frame is declared before the roll (01.6.9, 07.3). The residual path (shedding the lethal flag with a Protective lever) is the Oracle channel of exploit 1.

## 9. Social terms and certainty (partial)
- 15.3.5 allows up to two terms (a want served, a universal interest protected, a cost shared), each `[J:flag]`; 15.3.4 lowers the effective size one rung per term; 15.3.10 makes an effective-R1 request to a Neutral-or-warmer NPC **certain** (no roll, no evidence). A Neutral NPC (ceiling R2) therefore grants a favor (R2) on the offer of one term, and an R3 request on two. The playtest produced exactly this (verification-playtest.md section 2).
- *Limits:* two terms, a cited hesitation reason restores the roll (15.3.10), refusals still apply, patience. *Open:* 15.3.5 lists what a term writes (coin, commitments, `known_to_pc`; 15.4.1 State writes) and 11.4.9 says the world keeps commitments, but I did not trace what a broken term costs; the effect on difficulty is unmeasured. Treated as an open question with a measurement in I-048.

## 10. Training licenses without limit (partial, by design)
- 05.9.3/05.9.4: a mentor-path or text-path training license carries competence +2 at its tag; four weeks with a mentor, eight from a text; no cap on the number of such licenses; 05.9.4's text accepts it ("breadth is not power", per 02.1.3's creation cap). 15.11.6: never above `trained`, no time compression, a teacher may refuse. *Residue:* origin `access` licenses carry no competence (02.5.2) while a later training carries +2, so a Broad character prefers to *learn* what they were born holding; and a PC with unlimited weeks can hold +2 in every level-2 tag, which dilutes P4's specialist/breadth trade. Logged as I-047 with a default (cap the number of training-granted competence entries at the character's learning picks plus tier).
