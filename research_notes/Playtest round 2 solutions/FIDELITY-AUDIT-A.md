# Fight fidelity audit A: dm-tools fight loop against chapter 06 (with 07 and 09 as a fight uses them)

Read-only audit of branch spec033-base (481cfce). Classes: AW = as written; CHG = changed; MISS = missing; BBD = built but
decides on stale/partial information or its output is overwritten; RB = rule text revised to describe the engine's shortcut.
Paths are under `engine/`. "Unverified" is said where I did not trace it. One save checked: `saves/playtest-20261011-073517-fighter-dm-tools.db`.

## What a fight round is in code
`dm_tools._run` -> PC's `propose_roll` beat(s) (dm_tools.py:732) -> `_world` (:339) -> `dm_world.world_step` (:34) -> `_foes` (dm_world.py:98):
ONE DM call lists every able foe with its legal acts (dm_tools.py:311, :259), code rolls each pick in start-list order, then
`beat_time` advances one `round` (world_step.py:439). Nothing else of the 06 turn exists: no `h.06.*` handler is registered
(handlers/h06.py:10-18; `MILESTONE_HANDLERS[2]` in handlers/__init__.py:91 is the whole "Fights" milestone, none built, including
`h.07.after_conflict`, `h.07.dying_check`, `h.05.round_recharge`).

## Table (rule id | class | what the code does | evidence)
| Rule | Class | What the code does | Evidence |
|---|---|---|---|
| 06.1.1 budget (PC 3, foe 2, reactions) | CHG | Foe: 1 act per exchange (comment says so). PC: no action count in dm-tools (each `propose_roll` is its own one-beat run, so the pipeline's 3-beat check never fires); a round = one exchange. | conflict.py:274; dm_world.py:125-146; world_step.py:438; pipeline.py:200 only inside one plan |
| 06.1.2 fewer actions (dazed, stunned, surprised) | MISS | A stunned/dazed foe still gets its full pick: `legal_acts` reads only holds and prone; `able()` ignores conditions. | foe_act.py:47-59; conflict.py:108-115 |
| 06.1.3 / T-06-1 action costs | MISS (moves) | A move costs no action: `change position` and a stated move write any band for anyone, any distance. Foe `close_in`/`withdraw` = one band step. Heavy 2-action Strike, reload, stand cost: none. | dm_tools.py:1190-1211; pipeline.py:549-554; foe_act.py:133-139 |
| 06.1.4 free activities; PC Yield any time | MISS (PC yield) | Only a foe can `yield`. No PC yield path or "accepted by disposition" (06.11.7). | foe_act.py:114; no PC yield in dm_tools.py |
| 06.1.5 Defend | MISS | No `defending.<actor>` fact anywhere. | grep: 0 hits in engine/ |
| 06.1.6 repeated attacks | MISS | `repetition_instance` is never set above its default 1, so no −2/−4 for a 2nd/3rd attack. | types.py:163; frame.py:738-745 |
| 06.1.7 cadence channels | MISS | Tempo and reactions channels absent (rows below). | - |
| 06.1.8 turn_start / turn_end | MISS | Periodic conditions (bleeding, burning), Fend/Defend expiry, `frightened` decay, "owner's turns" durations never run; durations tick only on the exchange's `round` boundary. | h06.py:10-18; h00.py:47-66 |
| 06.2.1 start; PR-06-1 steps 1,3,4,5,6 | CHG | `start()` lists foes, gives Vitality, seeds band (`near`), sets mode. No sides, objectives, morale clock, surprise, tempo check, flags, advisory. The docstring admits it. | conflict.py:1-12, :77-105 |
| 06.2.1 "attack states whether it starts the fight" (R2-M2) | AW (as revised) | `starts_fight`/`fight_to` fields, blank = yes and logged; keyed on ids only. | dm_tools.py:233-236, :871-899; DL-06-42 |
| 06.2.2 Tempo (PR-06-1 step 5) | MISS | No tempo check, no order, no `tempo.seized`, no Delay. Foes act after the PC, in the order they were added to the fight record. The code says so. | world_step.py:438; dm_world.py:114,125; conflict.py:99 |
| 06.2.3 Rounds | CHG | Round = one exchange; `advance_time(1,"round")` only if a foe acted or a beat resolved. `h.06.ongoing_harm`, `h.05.round_recharge`, `h.06.chase_round`, `h.06.objective_check` never fire. | world_step.py:437-440 |
| 06.2.4 Surprise | MISS | `cond.surprised` is never applied or read. | grep: 0 hits |
| 06.2.5 Leaving/joining | CHG | Joiner added by `start()` (band `near` if none). Leaving = `able()` false (out of scene) only; "band distant to all" and reinforcement arrival band `far` not coded. | conflict.py:84-91, :108-115 |
| 06.3.1 position = bands + links + groups + flags | CHG | Only the band-to-PC (and the pairwise `position_set`). No links, groups; flags exist only from costs and are read by nothing in an attack. | costs.py:382-453; conflict.py:65-74 |
| 06.3.3 Moving (cost, pace, others-in-group, provokes) | CHG | DM states the band; no cost, no pace, no group shift, no Opportunity Strike. | dm_tools.py:1170-1218 |
| 06.3.4 bands between non-PC participants | MISS | A foe striking a companion reads `_band(foe, target)` or defaults `near`; no rule 1-3. | foe_act.py:131; dm_world.py:140 (comment) |
| 06.3.5 Engagement (links, capacity, screening) | MISS | `engaged.<a>.<b>` never written; any number of foes may be engaged. | grep: 0 hits |
| 06.3.6 / T-06-4 flags as levers and snags | MISS | No flanked, cornered, in_cover, elevated, hidden... lever or snag is cited on any attack (framer default levers `[]`). | schemas.py:542; frame.py:690-747 |
| 06.3.7, 06.3.8 cover, features | MISS | Not read in a fight. | - |
| 06.3.9 framing positions (R2-M) | AW (as revised) | DM's `to`; blank = engaged/weapon band or `near`, logged. | dm_tools.py:1414-1433 |
| 06.3.10 size | MISS | - | - |
| 06.4.1 Guard / T-06-5 | CHG (unmarked) | Foe vs PC: `_defense(...,"agility","deed.martial")`, ignoring the guard tag (weapon, shield, unarmed), shield edge, Defend, Fend. PC vs foe: from the foe's own attributes. T-09-3's `guard` is returned by `_line` and read by no one, so a seeded band-1 NPC is Guard about 10, not 12 (arithmetic, not rolled). | foe_act.py:152; conflict.py:290, :40-44; frame.py:552, :614-632 |
| 06.4.2 Strike at an unaware target | MISS | No surprised/hidden lever. | - |
| 06.4.3 PC Strike | CHG (marked) | Reach check per R2-M2 is AW. Harm = weapon base shifted by (reach-2); "no dealer-side pass, mastery, called shots". | conflict.py:189-205; dm_tools.py:902-924 |
| 06.4.4 / T-06-6 weapon weights | CHG (marked) | Weight from item tags; improvised = unarmed. | conflict.py:167-177 |
| 06.4.5 mastery, 06.4.10 called shots, 06.4.9 ammunition | MISS | Marked or absent. | conflict.py:197 |
| 06.4.6 evaluation pass | CHG | Receiver side (armor, resist) via `apply_harm`; dealer side E2/E4 missing. A foe's `red`, `taken`, `regen` from its line are never put on the entity, so foes take full harm. | apply.py:90-114; conflict.py:40-44 |
| 06.4.7 range/crowd/cover/unseen/Defend snags | MISS | None are engine-cited. | frame.py:738-745 |
| 06.4.8 harm mode (adversaries: from `defeat_disposition`) | CHG | Foe: the DM's `nonlethal` bool, default lethal; `defeat_disposition` read only for the Dying-PC test. PC: AW via `Stated.nonlethal`. | foe_act.py:32-35, :161; dm_world.py:143 |
| 06.5.2 Grapple, hold, break free | AW (core) | Hold = condition; foe `break_free` (1 action, Might defense); `release_holds`; held foe's legal acts limited. Tightening, choke, shield, take-item: MISS. | conflict.py:237-258; foe_act.py:47-53; world_step.py:47 |
| 06.5.3 Force (R2-M) | AW (as revised) | DM-stated push/prone; ladder. Hazard push: unverified. | pipeline.py:557-585 |
| 06.5.4-06.5.9 Disarm, Setup, Move-through, charge, falls, Aim | MISS / unverified | No fight-specific code found; only the generic pipeline. | - |
| 06.5.10 environment | unverified | Not traced. | - |
| 06.6.1-06.6.4, 06.6.6 Reactions, Opportunity Strike, Fend, defense slot, Ready | MISS | None built. `adversary.build` computes `reaction` kinds, but nothing calls it or reads them. | conflict.py:274; gen/adversary.py:197-204 |
| 06.6.5 adversary reactions | MISS | Foes get none (T2+ should have Opportunity Strike, T3+ Fend). | same |
| 06.6.7 companion Interception | MISS | - | - |
| 06.7 Conditions | CHG | Apply/remove and diminishing-at-application exist. `h.06.diminishing_window` (fall by 1/round, reset) is missing. A condition's limits on a FOE's acts exist only for hold/prone. PC side AW through the gate (01.3.7). | conditions.py:86-108, :186-198; gate.py:172 |
| 06.8 shaped effects | MISS | - | - |
| 06.9.1 DM picks each foe's act (R2-M; DL-06-40) | RB + BBD | See "Biggest five" 1-3. Rewritten to say "an adversary acts AFTER the PC's beat", with ONE act and ONE extra call; 06.2.2, 06.1.1 and PR-06-6 steps 2-3 ("2 actions", "for each action") were not revised, so the corpus contradicts itself. | 06.md:1125-1139 vs :88-103, :234-256, PR-06-6; dm_world.py:98-148 |
| 06.9.2 foe's beat as a frame | CHG | Direct `d20 + line.atk` vs Guard. No frame, no levers/snags, no Fend offer to the PC, "Reach Standard" fixed. Result shown as a RESULT line. | foe_act.py:152-164; world_step.py:97-102 |
| 06.9.3 attention (guidance to the DM) | MISS | No attention score or objective is shown; the DM picks a target blind to them. Bad/unknown target silently becomes the PC. | dm_tools.py:512-536; dm_world.py:134-142 |
| 06.9.4 default lists; T-06-16 | RB + CHG | Default = first row whose `do` text maps to a T-06-16 act and is legal; `when` is not evaluated; windup/flank/aim/reload/defend/cover rows skipped. T-06-16 says "melee only until ch.09 adds ..." (rule text now states the shortcut); "restrained: strike only with a close-quarters weapon" coded as any weapon. | foe_act.py:19-23, :51, :65-71 |
| 06.9.5 Windup / heavy blows | MISS | No windup act. Band-5 standard line has `sev: 4`, so an ordinary strike is S4 (critical S5) with no announcement. The foe's lethal warning is computed on `max(sev, heavy)`, a blow the code can never throw. | archetypes.yaml:22; foe_act.py:158; conflict.py:93-96; lethal.py:99-104 |
| 06.9.6 tells, sealed numbers | AW | `SHOW_FOE_ROLL = False` (owner's call). | world_step.py:35 |
| 06.9.7 no hidden adjustment | AW | Acts are open and logged. | dm_world.py:132-133 |
| 06.10 mobs, swarms | MISS | No `members`, no pooled Vitality. | - |
| 06.11 morale, break, omens | MISS | No morale clock. A foe "yield" is a free pick in every state of T-06-16, i.e. a unilateral surrender with no clock, break row or demand (06.11.7). RB. | foe_act.py:114-119; 06.md:1178-1191 |
| 06.12 chase, flight, pursuit | MISS | `flee` just moves the foe off the scene and the fight ends. No chase clock, no PC pursuit or flight. | foe_act.py:120-124; harm/exits.py:272 |
| 06.13.1 end test | CHG | Only (a) no foe able and (d) PC down/dead, run after foes act. No round-boundary objective check, no truce, no objective-achieved. | conflict.py:118-133 |
| 06.13.2 objectives | MISS | Only `kills()` reads a data field. | foe_act.py:32 |
| 06.13.3 defeat, `on_defeat` | CHG | `defeated` fact is written by harm; `on_defeat` is never fired (evidence, Focus, Taking readers get nothing). | grep: 0 hits |
| 06.13.4 what `conflict_end` clears | CHG | Mode and record cleared. Bands, flags and Defend/Fend/windup facts are not; duration `conflict` conditions end via `h.00.durations`. | conflict.py:128-132; h00.py:40 |
| 06.14 companions (no turn, Command, orders, intercept) | MISS | A companion is only a legal foe target; never acts. | dm_world.py:137-140 |
| 06.15 mounted | MISS | - | - |
| PR-06-2 a round | CHG | Per-participant turn_start/actions/turn_end in tempo order -> "PC, then foes, then one round". | world_step.py:437-440 |
| PR-06-3 steps 3, 6 (riposte), 7 (morale, attention, ammo, spoiled windup), 8 | MISS | - | pipeline.py:_finish |
| PR-06-6 an adversary's turn | BBD | Steps 1 (stunned skip), 2 (2 actions), 3 (per action), 4 (log skipped) not met; 5 ("never substitute an action the pick did not produce") is broken by the default replacement. | dm_world.py:128-133 |
| 07 `apply_harm`, 07.3 lethal warning, 07.2.7 dying | AW with coarse markers | No wound records, prevent/redirect, brink penalty (marked "coarse"). `h.07.dying_check` is run by the PC's turn end only. | apply.py:182,193,203; turn.py:823-840 |
| 07.6 defeat dispositions | CHG (marked) | Down PC wakes after an interval; no victor takes it. | turn.py:845-847 |
| 09 PR-09-1/2 stat block (attacks, tempo, reaction, morale, red, taken, regen, powers) | MISS (unwired) | `gen.adversary.build/improvise` has no caller outside tests. Fights use T-09-3's standard line by `threat_band` or `band` (`atk`, `sev` only). A seeded NPC "band 1" fights as a T1 line. | conflict.py:40-44; grep `improvise(`: 0 callers |
| 09.7.1 behavior lists | CHG | Only as the logged default (see 06.9.4); lists from the template (`beh.*` ids) not loaded for NPCs; role falls back to `melee`. | foe_act.py:65-71 |

## Defaults that stand in for a choice the rules give to someone
1. **Foe's act when the DM omits it or its pick is no longer legal:** first behavior-list row mapped to a legal act, else `wait`, logged
   `not_chosen:foes.<id>` (dm_world.py:129-133, foe_act.py:65-71). It also fires when the whole foe call fails (`default={"foes": []}`, :119).
2. **Which foe acts first:** record order of the fight (dm_world.py:114/125). The tempo check gives this to dice and Wits (06.2.2).
3. **Foe's target:** omitted, "pc", or any id that is not a downed-free companion -> the PC, logged only for the odd ones (dm_world.py:134-142).
4. **Foe's harm mode:** omitted -> lethal (foe_act.py:161), where 06.4.8 gives it to `defeat_disposition`.
5. **Foe's second action:** not given; the foe just does nothing more (06.1.1).
6. **Reactions:** neither side is ever asked (06.6); no default, they are absent. **PC yield and flight:** the DM has no tool, so they are
   only possible as free narration.
7. **Position:** the fight start band, a joiner's band `near` (conflict.py:90), no recorded band -> first reachable band (dm_tools.py:917),
   `legal_acts` treats no band as `near` (foe_act.py:56), Force with no choice -> push (dm_tools.py:~950), mover omitted -> PC (:977).
8. (Pipeline path only, frozen) `conflict.foe_beat` chooses the foe's act wholly in code (conflict.py:261-300).

## Live evidence of the stale-field problem (rule 06.9.1 / PR-06-6, form b)
`playtest-20261011-073517-fighter-dm-tools.db`, turn.26. The foe call listed both foes "fresh; engaged" with acts
`strike, withdraw, grapple, flee, yield, wait`, and the PC "bloodied". The DM answered in one response: Evwin `strike`
nonlethal, Yipka `grapple` nonlethal. Evwin's strike left the PC `down` ("you are down"); a down PC is open only to a kill side
(06.9.3), so Yipka's grapple was no longer legal and code replaced it with `wait` ("holds back, watching"), logged
`not_chosen:foes.npc.yipka_sun_basker`. In 3 of 14 fight turns with foes in the saves checked, two foes acted; 1 of 3 ended in a code default.
The DM never saw Evwin's result before choosing for Yipka, and cannot re-choose ("no re-ask", dm_world.py:103).

## Biggest five for a working fight (plain words)
1. **Foes pick blind and together.** One call chooses for everyone from the field as it was before anyone moved. A pick spoiled by an
   earlier foe is not re-asked; code swaps in a default act, which is the very thing the owner ruled out (VIII.9, "code never decides").
   Fix needs one foe at a time, each seeing the last result, in tempo order.
2. **No tempo, and the corpus now argues with itself.** 06.9.1 was rewritten to "foes act after the PC", while 06.2.2, 06.1.1 and PR-06-6
   still say tempo order and two actions. Decide one; then build the tempo check and the round loop of PR-06-2 (PC turn, foes in order).
3. **Foes get one action, the PC an uncounted number.** Nothing enforces 3 PC actions, action costs for moves, or repetition snags, and
   foes spend 1 of 2. The pace of the fight is therefore set by the DM model's habits, not by 06.1.
4. **No defense side: no Fend, reactions, Defend, Opportunity Strike, flags, cover.** The PC never gets to answer an attack, flags never
   change a roll, and leaving melee costs nothing. Foes' Guard and the PC's Guard also come from two different models (T-09-3 line vs
   attributes), and `improvise()`'s full stat block (reactions, tempo, armor, windup) is not wired in.
5. **Fights cannot end by the rules' routes.** No morale, break, objective, chase, truce or PC yield; a foe's `yield` or `flee` is a free pick
   in any state; end test is only "no one able". This is why a fight is a damage race only, and why a band-5 foe strikes S4 unannounced.

Not verified: the rolled numbers of the Guard mismatch (arithmetic only), 06.5.4-06.5.10 beyond a code search, 06.4.11, the T-06-10
condition table row by row, and whether the PC's DM ever exceeds 3 attacks in one exchange (code shows no cap; saves not counted).
