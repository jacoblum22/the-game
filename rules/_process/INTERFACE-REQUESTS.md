# Interface Requests Register

Orchestrator-owned. Every request one chapter makes of another, collected from authors' reports so
that each later author (chapters are now written one at a time) sees what is asked of it. When you
author a chapter, read the section addressed to you and satisfy each item or explain in your DL why not.

## Applied amendments to 00 (orchestrator-approved)
- From 01: near-miss definition (00.3.10, glossary) — failure with margin ≥ −3 incl. nat-1 step-down (DL-01-03).
- From 01: engine-applied repetition snags are outside the two-snag count, inside the ±4 cap (00.3.9 g; DL-01-08).
- From 01: stored-DC key = obstacle id + anchor signature (00.3.8; DL-01-21).
- From 01: frame fields added — necessity.reason += take_the_time, certain_with_cost; secret; threatened_cost; alternate_cost; trade (00.13.1).

## Requests from ch.01 (Resolution) — done
- **02**: a new PC starts with fate 1.
- **03**: evidence fires only on resolved outcomes; success-at-cost counts as success.
- **05**: every license carries explicit `principle`, `stretch`, `emulate`, `crude_fallback` (missing = null + `rule_conflict` log). Focus "push" on a roll is optional and 05's to define.
- **06**: `cond.grabbed` severity_variable (S1/S2); define the reserved conditions the cost menu uses; adopt/tune the repetition shape 0/−2/−4 (window = the turn; counts every attack-trait beat); define each creature's "Guard" attack defense; Ready ↔ reactions; companion command action for Help.
- **07**: `apply_harm(lethal:false)` never moves a PC into Dying (INV-6); `last_chance.yaml` needs `fate_cost` (1–3); stabilize DC for first aid; `lethal_context` written before a declaration.
- **08**: `cost_immune` flag; meaning of `damaged`/`broken` for items; improvised weapons use the resembled weapon's stats.
- **09**: defenses for every attribute; tells; `lethal_context` per archetype.
- **10**: hazard `resist` fields; listening-clock tick sources (`trait.sense.loud`, `cost.exposure`, `cost.time`); falls of 20 ft+ are a Heavy (S3) source.
- **11**: thread `completed` and vow-kept events as fate triggers; reputation entries from `cost.exposure` at S5.
- **12**: `tbl.twist` with rows per severity S1–S5 and `tbl.meaning`; compile the 15 anchor cards into `anchors.yaml`; use 01.11.4's inconclusive-beat definition; tension may shift Oracle odds by ≤1 rung; the OFFER script renders 01.7.1.
- **13**: `canon_impossible` list; what spirits understand; language licenses and their fallbacks.
- **14**: codex shows frames, OFFERs, fate, and the `auto_commit` preference.
- **15**: social DCs composed on Talk's `against` defenses, using standing and claim plausibility (doubtful = snag; outrageous = Limited reach; known false = G4); alertness ladder unaware → suspicious → alert → alarmed; refusal facts written by `cost.closed_door`.
- **16**: companion base modifiers for group actions and Help.

## Applied amendments to 00 from ch.12
- Tools #35 `log_turn`, #36 `revert_writes` added to 00.14.2.
- Id prefixes `anc.` (anchor cards), `scn.` (scenes), `trg.` (triggers) added to 00.16.2.
- Pending for integration: SCHEMAS.md note for optional fields in oracles.yaml/pacing.yaml and a `clock_templates` key; 00.15.4 packet numbers (core + ≤12 cards + verbatim player message + last 4 exchanges, DL-12-02).
- Terminology: NPC depth names are **walk-on / recurring / principal** ("major" is a banned severity word). 15 and 16 must use "principal".

## Requests from ch.12 (DM Procedures) — done
- **01**: note in 01.15.2 that tension shifts only eventful-tagged questions, never the player's G0 questions (integration edit).
- **11**: clocks list `random_event` as a tick source; bangs carry `intensity_delta` (defaults threat 3 / social 1 / opportunity 0) and a specificity key; thread status `stalled` with its fallback queued; every hook ≥3 clue placements; rumors carry `points_to`; accept chronicle-line offers; S5 twist rows need haven, commitment and situation facts.
- **09**: `reaction: true|false` per archetype; tells by band; `threat_advisory` used as the pacing push filter.
- **10**: watch/interval checks may name `tbl.event_focus`; ch.10 may opt in to reading the pacing phase.
- **07**: emit setback facts (pacing/adaptation input).
- **06**: reload state as a fact; T-12-11's band wording.
- **13**: region tables replace the generic NPC, name and omen tables in `oracles.yaml`.
- **14**: render the out-of-fiction labels (DL-12-18); flags need tags; turn log and corrections ledger viewable by the player.
- **15**: map NPC memory valences to standing steps; clue delivery follows 12.10.4.
- **16**: companions count as spotlight facets; a companion's death is a setback.
- **All later chapters**: mark anchor-worthy rules `Anchor: yes` with knobs; anchors.yaml is RECOMPILED at integration from every chapter's cards (scratchpad compile_anchors.py).

## Approved 00 amendments from ch.03 (apply at integration; treat as in force NOW)
1. `record_evidence` gains `op`: record | void | add_witness | atonement.
2. SCHEMAS.md#evidence.yaml documents ch.03's optional keys; a counter's `tags` may be empty when it has a `tag_source`.
3. 00.6.8: `degree` is `success` for a success-at-cost; the EvidenceEvent shape is extended in 03.2.1.
4. 00.5.6: a secondary deed tag earns evidence only when GROUNDED (ground kinds: ability, license, item, setup_beat, companion, mount, position), at half value.
5. 00.10.2: ch.03's counters are engine listeners at any depth, not effect subscribers under INV-12.
6. Glossary additions: quality (routine/difficult/challenging), settlement, evidence-bearing scene, ground, carrier, strain, deed line.
7. T-00-9: add handler `h.03.day_settle` (`day`, phase 9).
8. `trait.*` rows in tags.yaml cite T-01-13.
- Constitution PATCH note queued (v1.8.0): P5's "significance is base-model judgment" is refined by DL-03-01 — deed significance is computed from frame fields committed before the roll (consequential + pressured + the actor's own declared act); fresh judgment remains for the primary tag and for conduct evidence (which must cite a state write).

## Requests from ch.03 (Tags & Evidence) — done
- **01**: `frame_check` stores `base_odds` (circumstance = 0); a resisted-effect check is flagged `beat.declared: false`; RECORD step 4 runs PR-03-1. (integration edit)
- **02**: competence entries use T-03-1 tags; OPTIONAL `backstory` evidence (≤3 tags at 24 points each, never counting toward recent/distinct scenes/crises/peaks — 02 decides whether to use it, DL-03-25); aspirations never weight evidence.
- **04**: require judged AND counted thresholds together, PLUS a quality floor and a distinct-scenes floor (a routine-only grinder passes weight 80 by ~session 5); write atonement events; name bonded witnesses; provide `power_band` for the peak flag; define confidence; log the tally values used with each recognition. Calibration (03's sim, 5 scenes/session): focus level-2 node ≈24 pts/session (reaches 80/200/450 at median session 4/8/19); focus branch ≈30/session (80/200/450 at 3/7/15); hybrid smaller-node reaches 60/120 at session 3/6; branch balance ≈0.12–0.34 incidental vs ≈1.0 deliberate hybrid; honest mercy ≈ +1/session. Suggested (not binding): hybrid floor min ≥ 60 with balance ≥ 1/3; Fraying stages at strain 4/8/12 or any forbidden citation. Sealed functions: tally, detail, share, dominance, profile, cooccurrence, diversity, conduct, counted (03.9).
- **05**: every ability's first tag is a deed tag at level 2 or 3; mark effects that dictate choices `dictates_choice: true`.
- **06**: state which defense a strike on an UNAWARE target rolls against (if awareness → primary tag guile.ambush.*; if Guard → weapon tag primary, DL-03-24); keep `flag.hidden` / `flag.mounted` current; `on_defeat` carries the defeating frame id; a mob is one entity.
- **07**: harm state readable at declaration; marks may read `evidence_for_frame`.
- **08**: level-3 item tags on base items; `provenance.maker`; a quality rung index; the generosity floor uses weekly lifestyle cost.
- **09**: `creature_tags` listed most specific first; `speaks` per archetype; threat band on every adversary.
- **10**: `loc.*.discovered` written with its frame id; journey-role facts; settlement ancestry on places.
- **11**: consume `public_deed` packets and `public()`; NPC home and faction memberships; reputation by persona when `as_identity` is set.
- **12**: turn-loop step T6 runs PR-03-1; reliable `scene_end` marks (settlement hangs on them); disputes route to PR-03-4. (integration edit)
- **13**: facts marking places consecrated or tended; NPC homes.
- **14**: a codex "Deeds" view per `ledger_view`.
- **15**: `clu.*.found` facts; training writes `cnt.training`; the `unaware` alertness value.
- **16**: `tracks_evidence` per template; companions as carriers.
- **Tags**: tags.yaml now has 832 tags (levels 0–3). `situation`, `trait`, `org`, `harm` have no level-3 content yet; propose via `data/contrib/tags.NN.yaml` (PR-03-6). Sibling budget: 8 children per parent. Level 4 only when a data entry needs it.

## Approved 00 amendments from ch.04 (apply at integration; treat as in force NOW)
1. `gen.pick` is a registered generator domain (the tier "pick" procedure = tag-gated `chosen` selection from 05's ability pool).
2. `licenses.yaml` gains an owner-block "04" (capability licenses `lic.call.*`).
3. Effect expression context gains `secondary_tags`, `gate.mode`, and a "your calling key" resolver.
4. `evaluate_recognition` trigger enum: reflection | crisis | arrival | request; packet shape per 04.4.6.
5. `retire` takes `superseded_by` and leaves specialties; `grant` takes `provisional` and a source.
6. Handlers: `h.04.crisis_check` (beat_end, phase 8), `h.04.provisional_check` (reflection, 8), `h.04.fraying_check` (scene_start, 8).
7. `Character.callings` extended per 04.1.2. 8. 00.4.3: the lifetime +1 attribute applies when tier 4 is CONFIRMED.
9. Glossary additions per ch.04. 10. Constitution PATCH items queued (P5 classifier wording; VI character-scale provisional as extrapolation; variants).
11. Relics never feed tiers: 08 marks relic licenses `feeds_evidence: false`; 03 drops deed events made under such a license (integration edit to 03).
- SCHEMAS amendment to consider at integration: allow ladder references in callings.yaml (file is 403 KB fully expanded).

## Requests from ch.04 (Recognition & Growth) — done
- **05 (CRITICAL — 04 was written against these assumptions; 05 must author to them or justify changes in its DL):**
  - Calling partition 12 slots, acquired partition 4 (04's rules hold for 9–16).
  - Every `slot_class: calling` ability: first tag at deed level 2 or 3; `min_tier` 1–5; `mod_group`; `ranks` as COMPLETE restatements (≤3 ranks; rank = 1 + floor((tier − min_tier) ÷ 2)). Optional: `replaces`, `requires_conduct`.
  - Coverage: ≥2 abilities per level-2 deed tag (one at min_tier 1); ≥12 per branch with ≥2 at each min_tier; ≥2 per positive conduct axis. (If fewer, kin-pool abilities fill candidates and unfillable picks are kept.)
  - `lic.training.*` license per level-2 deed tag with grades trained < expert < master.
  - Every license carries `emulate` and `stretch` prices (04's Sure Hand and Open Art capabilities read them).
  - Mirror the 27 `gen_absorb.yaml` pool entries as acquired abilities; provide re-slotting at `rest_long`.
  - 05 may retune the nine family Focus triggers (1 Focus, once per scene; twice from tier 4).
  - Picks cumulative by tier: 2/3/4/5/6 (deed-keyed callings); 1/1/2/2/3 (oath). Up to 3 deed seats + 1 oath seat.
  - Composites: 04 authored 32 hybrid composites in `data/contrib/composites.04.yaml` using core effects only.
- **02**: origin competence at most +2; a first magic license from at least one origin per magic branch; `gen.birth` able to grant an innate `deed.primal.elements` license; aspirations carry tags.
- **03**: confirm `peak_band` counts successes only and add `success_by_band`; `detail(since)` by scene index; non-folk opponent-kind count; optional `conduct().pos_events`; reconcile `deed.wilds.animals.falconry` (contrib/tags.04.yaml). (integration edits)
- **09**: `absorbable`, `signature_of`, `cannot_absorb` on archetypes/adversaries; a scene-log record when a creature uses a power (the Taking requires the PC saw it act). Note 04's power bands: tier→band fine/narrow 1–5; broad/hybrid 1/2/3/4/4; 04's sim assumed opposition drawn from the PC's band to band+2.
- **10 / 13**: place `resonance`; keeper powers with conduct axes; institutions per deed branch; whether the four `none` hybrid pairs hold in the setting.
- **11**: consume `recognition_event` (04.7.8); `institutions_matching` returns `{faction_id, status_to_pc, has_ranks, next_sitting}`; restitution as a thread; `apotheosis_available`.
- **12**: a `[RECOGNITION]` out-of-fiction label; lead engine places the NPC that V2/V12 needs; open offers in the SITUATION block. (integration edit)
- **14**: codex views Callings, Oaths, Offers, Leanings.
- **15**: Retrain and Penance downtime activities; `cnt.training` with a mentor.
- **16**: a companion with `tracks_evidence` holds one seat, to tier 3.
- Key numbers: max tier 5 (Called, Proven, Tempered, Exalted, Paragon); competence by tier fine/narrow +3/+4/+5/+5/+6, broad/hybrid +2/+3/+4/+4/+5; pacing (focused archer) tiers at sessions 4/9/19/34/56.

## Approved 00 amendments from ch.05 (apply at integration; treat as in force NOW)
1. Handlers `h.05.rest_recharge`, `h.05.reslot`, `h.05.reserve`, `h.05.provisional_abilities`.
2. Six effect definitions in `data/contrib/effects.05.yaml` accepted (incl. `eff.05.waive` = `prevent` on a named snag/provoked reaction; `eff.05.end_working` = `remove_condition` extended to a magical effect instance).
3. License kind `universal` added (`lic.focus.push`).
4. `Character` extended: `focus` sub-fields, `shelf`, `witnessed`, `HeldAbility` shape, per-being healing counter.
5. `applies_when` context gains event-scoped keys (`event`, `event.target`).
6. Hook subscribers may observe events targeting or near them (reactions such as Counterspell/Riposte rely on it).
7. Glossary additions per ch.05 (working, rite, flare, push, reserve, Spent, overdraw, shelf, small working…).
- SCHEMAS amendment to consider: allow rank-1 fields to be read from `ranks[0]` (abilities.yaml is 951 KB).

## Requests from ch.05 (Abilities, Focus, Magic) — done
- **04 (integration edits to ch.04)**: (a) the pick gate must match an ability's `conduct_pole` to the calling's `pole`; (b) acquired-held or shelved abilities are eligible for a pick and ranked first (promotion); (c) adopt the `tier_reached` rank and Focus rule for consolidated picks; (d) dark callings' tier-5 pick is kept until tier-5 dark abilities exist (see issue I-007).
- **01 (integration edits)**: name the miscast as an alternate cost source in 01.9.2; Handle's card admits the license's attribute for small workings; the Focus push is declared at OFFER beside 01.7.3's trade.
- **02**: base Focus 3–5 (reference 4); one origin per magic branch grants its first training license with `requires` satisfied; origin competence at most +2; at most one gifted ability into the acquired partition. Casting attributes: arcane Intellect, divine Presence, primal Resolve.
- **03 (integration edits)**: `cnt.focus` counts a push at the frame's primary tag; emulation evidence lands on the emulated technique's tag.
- **06**: define `cond.exposed` as giving attackers a Precision lever; action cost per verb and reactions per round; engagement links and `flag.lined_up`; adopt the five spread tags in `conflict.yaml#multi_target` (order/caps: pierce 4, burst 6, fork 5, chain 3, linger 5; 6 targets total); a "bloodied" expression; stances end at `conflict_end`; the companion command action; size steps. Abilities in `data/abilities.yaml` assume these — read the pool's conflict abilities before fixing numbers.
- **07**: emit rest `quality` on rest boundaries with `h.07.rest_recovery` running BEFORE `h.05.rest_recharge`; `apply_harm(lethal:false, no_reduction:true)` for overdraw strain harm (never to 0 Vitality); confirm `cond.exhausted` stacks (intensify, 3); define "stabilized"; whether mundane treatment counts toward the healing cap of 2 healing effects per recipient per long rest (05 assumed yes). Focus rest recovery: breather +1 (max 2 between short rests); short rest +half max (first 2/day); long rest to max.
- **08**: one active ability per item with a stated rank; relic `feeds_evidence: false` plus +1 Focus surcharge; priority-rank bands item intrinsic 15–19, applied consumables 20–24; implements (reserve vessel); teaching texts; components by price band; `gen.gift` abilities go to the acquired partition; meaning of `damaged`/`broken`.
- **09**: adversaries may hold pool abilities; scene-log records for witnessing; Focus-emptying powers only at T4–T5 with a tell.
- **13**: the eight magic-canon items in 05.7.10 (`canon_impossible` for magic, keepers and their axes, resonance and dead ground, spirit frequency, components, teachers and texts).
- **10, 11, 14, 15, 16**: full lists in ch.05's Interface requests section — read that section when authoring.
- Key numbers: slots 20 = 12 calling / 4 acquired / 4 equipped + shelf 4; Focus max = base + highest tier + 1 per other calling at tier ≥3 (cap 12); cost bands 0–4; training grades trained/expert/master; rite scales personal/local/site/regional (clocks 4/6/8/12).

## ORCHESTRATOR DECISION (binding): PC maximum Vitality grows with power band
max Vitality = creation value (02's formula, 10–16, reference 12) + 2 × (power_band − 1), hard cap 24
(00.3.12). `power_band(pc)` is 04's (from confirmed tiers). 07 owns the rule text and the handler that
recomputes the maximum when `power_band` changes (current Vitality rises by the same amount); 02 states
the creation formula; 04 gets an integration note. Basis: ch.06 simulation — with flat Vitality 12,
P4 vs one T4 falls 87% → 68% and P5 vs one T5 80% → 57% (rules/_process/simulation/06-conflict-sim.md);
resolves R3 gap G-8 ("where max Vitality grows from without levels"). Recorded as DL-00-04.

## Approved 00 amendments from ch.06 (apply at integration; treat as in force NOW)
- `economy` op may carry a non-positive `actions_delta` (dazed, stunned, surprised REMOVE actions; INV-11 still forbids adding actions).
- `lever` op covers snag grants. `eff.grant_lever` accepts `to` / `engine_cited`; `eff.condition_immunity` accepts `flags` / `effects_with_trait`.
- Reserved ids added: `flag.obscured`, `flag.in_chokepoint`, `flag.aloft`; `cond.surprised`, `cond.silenced`, `cond.broken`, `cond.heartened`.
- Handlers `h.06.chase_round`, `h.06.objective_check` (+5 more in contrib/boundaries.06.yaml).
- Optional `diminishing.group` on conditions. Glossary additions per ch.06 (Guard, mastery, tempo, windup, mob, engagement link…).
- 00.3.7's coherence paragraph and `advisory_by_difference` yield to T-06-13 (the advisory matrix), which is the contract for 09's `threat_advisory`.

## Requests from ch.06 (Conflict) — done
- Economy: PC 3 actions + 1 reaction; EVERY adversary 2 actions at every band (09 may not raise it); T1 no reaction, T2+ one; mobs 2 actions no reaction; companions 0 actions, 1 reaction; Command = 1 PC action buys one companion beat; five standing orders.
- **07**: `apply_harm` needs `mode` (lethal | nonlethal); define when Retreat is certain vs becomes a chase (06: escape clock 6 racing pursuit clock 8); decide whether a windup (any S4+ or shaped adversary attack must show a visible windup on an earlier turn) may count as the lethal warning; armour reduction 1/2/3 with cap 4 assumed; `no_reduction` for bleeding and choking; the real Dying ladder (06's sim used a proxy of two further hits while Staggered); apply the Vitality-by-band decision above.
- **02**: creation Vitality formula inside 10–16; note the by-band growth above.
- **08**: build weapons on T-06-6 and T-06-7 (unarmed S1; light and one-handed S2 at 1 action; heavy S3 at 2 actions; bows S2; crossbows S2/S3 with reload 1/2; twelve properties, at most two per item); shields give +1 Guard edge and no reduction; mark natural armour `no_gaps`; items may carry a spread shape; mastery (Strike base severity +1 rung at expert, +2 at master) is part of the base, outside the ±2 effect-step cap — item harm_edge must stay within budget alongside it.
- **09**: per adversary — Guard and all seven defences, tempo DC (by band 10/11/12/13/14), size (tiny…colossal), reaction flag, `windup` on S4+ or shaped attacks, nerve (morale clock skittish 4 / steady 6 / resolute 8 / fearless none), break behaviour, role, objective, weak spot, mob members, swarm flag, pace. Use T-06-12 reference lines and satisfy T-06-13 (advisory matrix). NOTE: at mid-envelope, T4 and T5 foes are lethal IN PAIRS to a PC of their own band, and three equal-band foes are lethal from P2 up — budget solo encounters accordingly (mobs make crowds fightable: four T2 vs P2 is 3% as individuals, 43% as one mob). Re-run `rules/_process/simulation/06-conflict-sim.py` with your final templates.
- **05 (integration/revision)**: map spell-delivery forms to shapes (cone → `cone`, a sixth shape, cap 4); ONE ZERO-COST ATTACK WORKING PER MAGIC BRANCH (issue I-009); shield-block texts say "in place of Fend".
- **10, 12, 13, 14, 15, 16**: listed in ch.06's Interface requests section — read it when authoring. anchors.yaml recompile at integration picks up 06's 13 anchor rules and T-06-9's forty environment rulings.

## Approved 00 amendments from ch.07 (apply at integration; treat as in force NOW)
1. `apply_harm(target, severity, harm_tags, source, lethal, mode, no_reduction, periodic, dealt)` with extended return.
2. `Character` gains `wound_load`, `down`, `defeated {manner}`, `dread`, `afflictions`, `reprieves_taken`, `watches_awake`.
3. Rest boundaries carry a payload `{quality: full|partial|interrupted, site: haven|camp|rough, treated}`; handlers may declare `before:` within a phase.
4. Seven added handlers (contrib/boundaries.07.yaml); triggers `trg.lethal_warning`, `trg.danger_notice`, `trg.exits`.
5. Glossary: wound load, brink, Down, Threshold, stabilized, lethal frame/context, scar, brink mark, maim, haunt, **dread** (the name for mental strain — "strain" stays 03's conduct term), shaken, rest site, treated, grit.
6. 06.7.6 `defeated(x)` does not count a Dying PC (it still acts); a Dying NPC is defeated. (integration edit to 06)

## Requests from ch.07 (Harm, Recovery, Death) — done
- Key numbers (T-07-20): max Vitality = 02's base (10–16) + 2 × (power_band − 1), cap 24; reduction cap 4, armor 1/2/3, shields 0; wound load limit 3; Dying 3 steps, stabilize DCs 10/15/20; Vitality by rest: breather +2, short +half max, long to max; dread threshold 8 + Resolve (min 4); rest sites haven/camp/rough; setback facts `setback.defeated/yielded/captured/dying_entered/threshold/retreated/companion_dead`.
- Last-chance menu: 9 options (incl. "The Road Ends" = retire alive); Reprieve `fate_cost = min(3, 1 + reprieves_taken)`.
- **02**: creation Vitality base inside 10–16 (Endurance feeds it); note band growth is 07's.
- **05 (integration edit)**: "grit" — an alternate use of the Focus push (ignore wound penalties for a beat, no reach) in 05.6.7.
- **06 (integration edits)**: PR-06-3 passes `dealt / lethal / mode`; only `kill`-disposition sides attack a Dying PC; rounds continue while anyone is Dying.
- **09**: per archetype/adversary — `lethal_context`, `defeat_disposition` (7 dispositions in harm.yaml), `captive_fate`, `dread: S1–S4`, wound site on attacks, `can_bargain`; "kills outright" text reads as S5 harm against PCs. Advisory→outcome targets (per 100 lethal fights, fighting on): trivial 0 / easy 1 / fair 5 / hard 26 / lethal 80 reach the menu — keep 09's `threat_advisory` consistent with these. Re-run 06 and 07 sims on your final templates.
- **10**: `rest_site` on places; hazard `aftermath`; `h.10.supply` applies `cond.exhausted` stacks; want/deprivation harm takes no reduction; falls take no reduction.
- **11**: consume `victory_over_pc`, rout ticks on world clocks, the `pc.dead` belief, cache rumors (lost gear recoverable once); retirement entry points from The Road Ends and the fourth dread break.
- **12 (integration edit)**: `[WARNING]` and `[STATUS]` labels; the last-chance menu is a `[CHOICE]` with NO default (departs from 12.15.6's default line).
- **08, 13, 14, 15, 16**: listed in ch.07's Interface requests section — read it when authoring (08: armor reduction 1/2/3, shields 0 reduction; 16: companion `clk.bleeding_out` 4 segments; 15: Treat/recovery activities in downtime; 14: codex views for wounds/dread; 13: havens).

## Approved 00 amendments from ch.02 (apply at integration; treat as in force NOW)
- Owner-block "02" in effects.yaml for `eff.02.bent`; `gen.birth` extensions (layer slots, degree `none`, `excluded_when`); optional schema fields (T-02-14); out-of-fiction labels `[CREATE n/N]`, `[SHEET]`; glossary (people, upbringing, livelihood, knack, quirk, the Bent, breadth profile, drive, anchor bond, thorn bond, one true thing). 00's example character Wren is post-Bent: Vitality 13.

## Requests from ch.02 (Character) — done
- Key numbers: attributes −1…+3, sum +5 (Free rule) or +7 (Typical rule); floor +1; origin competence +2 on ≤2 tags; best starting modifier +5 (+6 with a knack); base Vitality = 12 + Endurance (11–15 at creation); Focus base 3/4/5 by upbringing; fate 1; dread threshold 7–11; Guard 10–16; 1–11 training licenses at `trained`; 0–1 ability; 5–8 hooks; coin 3–55; coin unit: 1 coin = one day's plain food and lodging.
- **05 (revision)**: the "spark" (Touched livelihood's innate primal gift) only has fire and earth workings at min_tier 1 under `deed.primal.elements` — add water and air (issue I-015); I-009 is critical for new casters; confirm an innate license needs no further `requires`.
- **08**: map assumed quality names `worn` < `common` < `fine`; confirm the coin unit above; define a spellbook's `teaches:` fact; kits in `data/kits.yaml` use `{item_tag, quality, quantity}`.
- **09**: `threat_advisory` should read the PC's ACTUAL attack modifier and Guard at band 1 (starting characters vary widely: martial vs T2 wins 98–99.8%, new caster in melee 31–55%, weakest legal 21%).
- **11**: consume creation's hook records, the vow thread (drive), faction ties, prologue chronicle lines, successor inputs.
- **12 (integration edit)**: bond NPCs get a SET standing (anchor/thorn), not a reaction roll; facets; the labels.
- **13**: peoples present in the region (8 peoples, 9 upbringings, 21 livelihoods in origins.yaml), name tables, a second tongue, keepers, places of acceptance (for hedge magic), factions by org kind, bond placement, and ≥4 pregens that pass PR-02-9.
- **14**: preference keys and codex views (T-02-x).

## Approved 00 amendments from ch.08 (apply at integration; treat as in force NOW)
- An item sub-cap at evaluation step E4 (enforces the item share across up to five items): edge +1 per quantity, harm_edge +1, reduction 3 per harm tag, ×½ resistance only from a tier-4+ signature, steps ±1, one item lever per roll, carry +4, supply −1/day. Items never touch attributes, competence, Vitality/Focus maxima, actions, slots or tiers.
- Item fields per 08.1.1; glossary (quality ladder worn/common/fine/masterwork/wondrous/storied, item share, relic, attunement, residuum, Unit of wealth…); weights doubled before halving (integer rule); optional `flaw.` id prefix.

## Requests from ch.08 (Items, Loot, Crafting) — done
- Key numbers: quality index 1–6 (worn, common, fine, masterwork, wondrous, storied; signature/magnitude slots 0/0, 0/0, 0/1, 1/1, 1/2, authored); drop check by source band d100 ≤ 10/20/35/50/70 (every defeat still yields materials, purse, gear); coin = one day's plain food and lodging; lifestyles 0/4/7/14/35/100 coin per week; one Unit of wealth = weekly lifestyle cost; carrying capacity 10 + 2×Might; 2 supply per load unit; torch 6 intervals, lantern 24 per flask; attunement limit 5; hireling weekly wages T1 7–10, T2 14–21, T3 50, T4 150, T5 never for coin; crafter wages 10/25/60; holdings from cottage 150 to keep 25,000.
- **09 (CRITICAL)**: the archetype loot contract is 08.3.4 and `data/gen_loot.yaml#contract_09` (tags, yield, trophy base, `loot.flaw`, signature, gear, purse). Tag every archetype to it and re-run 08's pool check (`rules/_process/simulation/08-loot-sim.py`) on the bestiary (target: pool ≥ 3 at tier 1). Archetype tags gate property pools; band sets tier cap.
- **01 (integration edit)**: cost.gear S5 — an item with a signature or bound ability takes the "location lost" form, never "destroyed".
- **03 (integration)**: review 17 proposed level-3 item tags in `data/contrib/tags.08.yaml`; drop deed evidence from frames that used a relic license (`feeds_evidence: false`).
- **04**: keep `gen_absorb` ids stable — `gen_item_ability` reuses its active entries by reference.
- **05 (integration edit)**: `rit.imbue` cites 08.6.10 (enchanting: one property per item, ever).
- **06 (integration edit)**: list armor's own snags and `burdened` among the engine-cited snags.
- **07**: named prosthesis items (hook, brace, peg, glass eye) are NOT yet in base_items.yaml (issue I-016).
- **10**: carrying capacity, supply lots, light durations above.
- **11**: holdings prices; gift triggers and holding yields are 11's to define.
- **13**: storied items, boon signatures, regional stock. **14**: codex views. **15**: the haggling frame (prices move by fixed notches per band; 8 anti-inflation rules). **16**: mounts and wages above.

## ORCHESTRATOR DECISION (binding): DL-00-05 — challenge band is relative to the PC
For evidence weighting, a conflict's challenge band = PC power_band + advisory offset (trivial −2, easy −1,
fair 0, hard +1, lethal +2), clamped 1–5. Integration edit to ch.03. Resolves I-005.

## Approved 00 amendments from ch.09 (apply at integration; treat as in force NOW)
- `pow.` id prefix (adversary-only powers).
- 00.3.7's Vitality envelope applies to standard and minion adversaries only; elite, solo and mob pools may exceed it.
- 00.3.7's coherence paragraph and `advisory_by_difference` RETIRED in favour of T-09-9 (extended advisory matrix) and PR-09-4 (`threat_advisory` estimator).
- T4/T5 reference Vitality becomes 24/36 (adversaries have Fend from T3).

## Requests from ch.09 (Adversaries) — done
- Key numbers: band competence c_b +1…+5 (T1–T5); variants minion ×½, elite ×2 (T1–T3)/×1.25 (T4–T5), solo ×4/×3/×3/×1.75/×1.5; adversary Focus 0/1/2/3/4 (+1 elite, +2 solo, +1 caster, 0 minion); effect DC = 10 + attribute + c_b; encounter spread Δ −1/0/+1 = 30/55/15%; dispositions across 63 archetypes: capture 17, drag to lair 17, drive off 14, kill 11, rob 2, leave 2; 13 can bargain, 25 carry dread, 26 lethal context.
- **03 (integration)**: adopt DL-00-05; adopt or decline 6 proposed creature tags (`data/contrib/tags.09.yaml`).
- **04 (revision)**: issue I-020 (`signature_of`, `no_pool`).
- **06 (integration)**: may adopt T-09-9 as its advisory matrix; OEQ-06-1 answered (3-vs-2 economy holds at bands 1–3).
- **08 (revision)**: issue I-019 (water elemental pool).
- **12 (integration)**: 09's per-archetype NPC-reaction field is named `reaction_roll` (06's combat `reaction` flag is separate).
- **13**: select a regional subset of `adversaries.yaml` and add entries via its owner-block using PR-09-1.
- **07, 05, 10, 11, 14, 15, 16**: items listed in ch.09's Interface requests section — read it when authoring (10: encounters belong to places, T-09-10 budget; 15: five mind types govern social/mental rules (DL-09-18); 11: `tbl.09.nemesis` victor memory; 16: companion makes the advisory word one step gentler).

## Approved 00 amendments from ch.10 (apply at integration; treat as in force NOW)
- New quantity `travel_points` in T-00-13 (so `eff.10.travel_points` lets items/abilities change journey speed; family `adjust`).
- Seven added handlers (contrib/boundaries.10.yaml) in T-00-9; Place and route-link field extensions per ch.10; SCHEMAS sections list optional keys in each data-file header; glossary additions per ch.10 (danger rating safe/settled/wild/perilous/deadly, pace ladder, leg, march unit, pending threat, telltale, roused…).

## Requests from ch.10 (Exploration, Travel, Sites) — done
- Key numbers: route length in watches; leg needs 6 × watches progress points; pace crawl 2/slow 4/normal 6/fast 8/ride 9/hard ride 12; danger rating 5 rungs (night +1); one d12 per watch / site check; hostile encounters arrive as a sealed pending threat with a visible omen first (one pending at a time; arrives on next encounter/omen face or 4th check); encounters per day 0.38/0.57/0.77/0.89 by danger (hostile 0.16/0.45/0.66/0.81); supply 1 per consumer per day; site sizes small 6/8, medium 8/8, large 12/12, vast 12+12/12; forced march allowance 2 units/day; havens have no time-tick check.
- **03 (integration)**: adopt 3 proposed terrain tags (contrib/tags.10.yaml); `cnt.discovery` ignores discoveries with `frame_id: null` (wandering in ≠ finding).
- **09 (integration)**: may move `archetype_signs` (omen signs for all 63 archetypes, in travel.yaml) into archetypes.yaml as a `signs` field distinct from tells.
- **11**: consume the venture record; `safe`-rating changes and the regional events table are 11's.
- **12 (integration)**: add a `[JOURNEY]` out-of-fiction block; anchors.
- **13**: places with all fields; regional encounter tables in the two-sub-table shape (d20 threat by relative band 6/11/3 + d6 non-threat; audit PR-10-8); site placements; havens; climates (5 climates × 4 seasons in weather.yaml).
- **14**: codex views Journey, Map, Site, Weather.
- **15**: search and study activities; **16**: companion journey roles (03's four roles), mounts as supply consumers.

## Approved 00 amendments from ch.15 (apply at integration; treat as in force NOW)
- Social defense = defense + standing term + request-size term (00.3.8 note); 15's social fields on the NPC shape; request and claim fields on the Frame; id prefixes `dt.` (downtime activities), `case.` (investigation cases), `lie.` (recorded lies); a fixed `how` list for `record_knowledge` plus a lie-exposure listener; `request_size` and `plausibility` accepted as ladders for the `step` op; relationship writes via `eff.15.standing_step`; 8 handlers (contrib/boundaries.15.yaml); a "15" owner-block in licenses.yaml.

## Requests from ch.15 (Social, Investigation, Downtime) — done
- Key numbers: standing → social DC modifier +5/+3/+1/0/−1/−3/−5 (Hostile…Devoted); request ceiling Hostile R1 with a term / Unfriendly R1 / Wary R1 / Neutral R2 / Warm R3 / Friendly R4 / Devoted R5; request modifiers R1 +0, R2 +2, R3 +5, R4 +8, R5 +10; payment price 1/1/2/3/4 Units of the NPC's weekly lifestyle; NPC lifestyles by role 0(1)/4/7/14/35/100; training fees 7/25/100 per week; wages 7/10/25/60 per week; ransom = 10 × PC weekly lifestyle × power band (min 20, due in 4 weeks); downtime week = one week-long activity (5 days) + two day activities, or seven day activities.
- **06 (integration)**: cite 15's meaning for `cond.charmed`. Standing does NOT enter intimidation/provocation DCs (DL-15-14).
- **07**: confirm the ransom formula against `captive_fate`.
- **08**: align NPC lifestyles by role with economy.yaml.
- **11**: officer duties as refusals; trigger member-standing recompute on every faction status change; fire case fallbacks from 15's data; an attention clock for "Lie low"; holdings yield reads `managed_this_week`.
- **12 (integration)**: add a `kind` field to `tbl.npc_refusal` rows (maps 1:1 to 15's 12 refusal kinds); run the lead audit after 15's placement audit.
- **13**: settlement tiers, teacher availability, sentry floors, `case.*` investigation templates (≥3 placements per necessary node; `case.mill_fire` is the model).
- **14**: a journal view (PC knowledge, clues, beliefs).

## Approved 00 amendments from ch.16 (apply at integration; treat as in force NOW)
- Id prefixes `cmp.` (companion templates), `kn.` (companion knacks); `companion` entity kind carries an `ally_kind` field; new handlers/triggers (contrib/boundaries.16.yaml) in the registry; glossary terms (retinue place, serving band, regard clock, grievance clock, counsel, held line, protégé, posted…).
- ORCHESTRATOR ACCEPTS ch.16's compromises: companion Vitality 6/12/16/18/20 (always below the PC's; below 09's standard line at bands 3–5) and a deliberately conservative advisory with 2+ allies (errs toward warning).

## Requests from ch.16 (Companions & Allies) — done
- Key numbers: retinue cap clamp(2 + Presence, 1, 6); allies serve at min(own band, max(1, power_band − 1)); anyone above the PC's band refuses to follow (redirect: escort, deal, thread); companion Focus = 09's adversary base by band (+1 casters), refills at long rest only; keep 4 coins/week; unpaid 2 weeks → hireling leaves; settlement max hire band village 1/town 2/city 3; departure clock 4 segments +1/day; held line 6-segment tug clock.
- **15 (integration)**: standing source 8 (an ally's regard or grievance clock completing); an exception for amends that restore a step lost in a confrontation; wage terms in a hire bypass the price test; regard completions vs 15.1.7's weekly cap (unless a shared-danger tick fed the cycle).
- **06 (integration)**: engine-set orders (default, losing heart, rushing to a Dying PC) cost no PC action; a Devoted ally may intercept without the *guard me* order.
- **07 (integration)**: cohorts share one bleeding-out clock and one stabilizing beat; adopt companion Vitality figures; lethal warnings name the companions at risk.
- **09 (integration)**: amend 09.6.3 and PR-09-4 with the "able ally" definition and the hard exception (a "hard" estimate whose no-ally win is < 75% stays hard).
- **10 (integration)**: add the fifth journey role, quartermaster.
- **08 (integration)**: trained-beast prices (hound 15, war hound 60, hawk 40).
- **03 (integration)**: adopt `deed.wilds.survival.provisioning`.
- **04 (integration)**: confirm protégé rules (one deed seat, tier ≤3, own band = tier + 1) fit the pick procedure; carry a `confirmed` flag on `recognition_event`.
- **11**: companion personal threads; factions courting companions; companions as successor candidates; vows on a companion's death.
- **12 / 13 / 14**: claim-check class for companion actions / regional hiring tables / codex views.

## Approved 00 amendments from ch.11 (apply at integration; treat as in force NOW)
- Id prefixes `sit.`, `sit_t.`, `bang.`, `wr.`, `thr.`, `rum.`, `rep.`, `chr.`, `imp.`, `ftpl.`, `legacy.`; entity kind `object` subtypes `situation`, `legacy`; trigger `trg.11.flashpoint`; labels `[SEASON]`, `[RETIRE]`; SCHEMAS lists T-11-1 optional keys; factions use `lifecycle_stage`, linchpin `consequence` + `fates`. Factions are "full" and "petty" (never major/minor).

## Requests from ch.11 (Living World) — done
- **13 (CRITICAL)**: regional factions conforming to 11.3.1 (tier 0–5 with hold; ratings force/cunning/wealth/sway, each 0..tier+2, summing to 4 + 2×tier; temperament; goal clocks local 8/regional 12/realm 12+12; linchpins with SEALED pre-declared fates); the org-tie → faction mapping for 02's faction ties; calendar names (season = quarter day + three 30-day months; 28-day moon); regional `tbl.11.season_events`, `tbl.11.hook`, `tbl.<region>.events`; regional values (what communities admire/despise — reputation valence); lifespans by people. Re-run `rules/_process/simulation/11-world-sim.py` with the real factions (target 1.5–3.5 goals per faction per year, ≤10% at tier 5).
- **03 (integration)**: adopt 3 situation tags (contrib/tags.11.yaml).
- **04 (integration)**: retirement offer uses 04.7's protocol; `apotheosis_forms` keyed by deed branch.
- **07 (integration)**: the aging mark is a 00.4.3(c) mark, source `aging`.
- **12 (integration)**: render `[SEASON]`, `[RETIRE]`; fallback bangs fire at the next scene_start; kickers read the rotation ledger; NPC generation writes `home` and `member_of`.
- **14**: codex views Factions, Register, Reputation, Ranks & obligations, Holdings, Calendar, Chronicle, Legacy.
- **15 (integration)**: list `dt.11.train_successor` in the downtime menu.

## Approved 00 amendments from ch.13 (apply at integration)
- Id prefixes `keeper.`, `obj.`; SCHEMAS documents the region file's optional keys (T-13-16); place facts `hushed` and `true_bell` added to the readable place facts.
- ch.13 GRANTED an owner-block "13" in `afflictions.yaml` (it was missing from T-00-19); regional afflictions may be added in revision (I-025).

## Requests from ch.13 (Starter Setting) — done
- **11 (integration)**: fix `11-world-sim.py`'s `gain_hold` to follow 11.3.4 (expand must not raise a faction above tier 3); add the `steadfast` row to its AGENDA (I-026).
- **10 (integration)**: PR-10-8's threat-word step is ambiguous about adversary counters (13 computed it with the counter held, per 09.4.4); run the word step on `travel.yaml`'s generic tables too (I-027).
- **09 (integration)**: state in 09.8.2 that every band-5 standard is lethal alone vs a band-4 PC, so a ring-4 table cannot put one at home+1.
- **05 (optional)**: a Bell-and-Hammer storied set if a composite is added.
- **15 (integration)**: move the three cases (`case.silent_bells`, `case.orsolin_signet`, `case.treaty_of_the_ford`) into `investigation.yaml#cases`.
- **14**: render the Truths of the March, the teaching-arc first-use notes, and the six pregen cards.
