# R2 Digest — LitRPG mechanics & Mistborn / TTRPG-balance / AI-integration research

> Research digest for chapter authors of The Game's ruleset. It covers **every finding** in the two research
> rounds below, organized by the BRIEF's chapter map (00–14), followed by a mechanics catalog, a numbers
> ledger, tensions, gaps, and ranked implications. Authors may rely on this digest in place of reading
> the ten source files, but every bullet carries a citation so any claim can be checked at its source.
> Author: research agent R2. Date: 2026-09-29.

## 0. How to use this digest

### 0.1 Sources covered (all read in full)

| Key | File | What it covers | Sourcing tier (how much to trust it) |
|---|---|---|---|
| LR | `reports/LitRPG mechanics for AI DM design.md` | Synthesis report, round 1 (HWFWM, The Land, Underworld, Stormlight) | Synthesis; inherits note quality. Contains one arithmetic misreading (see §4, T-11) |
| HW | `research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md` | HWFWM essences, ranks, stones, power creep, tracking burden | **Medium-high**: fandom wiki + Book-12 appendices + Reddit/TV Tropes. Canon is separated from a non-canon fan "Jumpchain CYOA", which is flagged |
| SL | `research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md` | Surgebinding, Orders, Ideals, Shards, Sanderson's Laws | **High**: direct Coppermind quotes |
| TL | `research_notes/LitRPG mechanics for AI DM design/the_land_founding.md` | The Land / Chaos Seeds attributes, skills, affinity, professions, settlement scales | **High for numbers** (wiki tables). Has internal inconsistencies (see §4) |
| UW | `research_notes/LitRPG mechanics for AI DM design/underworld_level_up_or_die.md` | Underworld Blue Mage | **Low**: reviewer paraphrase only, no wiki. Absorption rules are completely unknown |
| MR | `reports/Mistborn TTRPG AI design patterns.md` | Synthesis report, round 2 | Synthesis; one over-reading of the 46.1% figure (see §4, T-9) |
| MM | `research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md` | Allomancy, Feruchemy, Hemalurgy, Twinborn/Compounding, Mistborn Adventure Game (MAG) balance | **Medium**: Coppermind returned 403, so every Coppermind fact here is a WebSearch AI-synthesis. The MAG "fix" comes from a listicle (fandomwire) → **medium-low** |
| OL | `research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md` | Dungeon Crawler Carl, Primal Hunter, Cradle, Mother of Learning, Beware of Chicken | Cradle / MoL **medium-high**; DCC / Primal Hunter **medium-low** (search snippets); BoC **low** |
| BT | `research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md` | Bounded accuracy, PF2e, GURPS, PbtA, CR, trap options, the Alexandrian, AI-GM discourse | **Medium-high**. PF2e/5e rule facts are solid; the Alexandrian is quoted directly; the AI-GM discourse is product-blog level |
| AI | `research_notes/Mistborn TTRPG AI design patterns/ai_game_integration.md` | AI Dungeon, function-calling GM paper, CALYPSO, Generative Agents, Voyager, judge gating, Jev | **Mixed**: the arXiv papers are high; journalism medium; dev.to and "resolve_improvised_stunt" low/unverified |

### 0.2 Citation convention
Every bullet ends with one or more citations in the BRIEF's format:
`[R: <path> §<heading>]`. `§<heading>` is the **exact leading words of the source heading**, so it can be
grepped. The two reports' untitled opening paragraphs are cited as `§(opening summary)`. Underworld's
un-headed preamble (author confirmation and source-quality caveat) is cited as `§(preamble)`.

### 0.3 Bullet format
**Bold lead** = the finding. Then: numbers, mechanics, and named precedents · *Rules out / warns:* what the
finding forbids or cautions against · *→* cross-references to other chapters · citation. Where I add my own
arithmetic or analysis, it is labelled **[R2 analysis]**. Where I use background knowledge that is not in the
sources, it is labelled **[unsourced — verify]** and appears only in §5 Gaps.

### 0.4 The frame I read everything through
The owner's locked decisions (BRIEF §4) change how much of this material transfers:
- **No diegetic System.** Every LitRPG source here has blue boxes, and the project has none. What transfers
  is the *mechanical shape* (thresholds, slots, ranks, rolls). What must be replaced is the *announcement
  vehicle*. The genre's own correction ("blue boxes for significant milestones only") points the same way.
  The project goes one step further: milestones are voiced by the fiction (oaths, mentors, titles, orders,
  awakenings), not by a box.
- **Sandbox with retirement/legacy.** Any mechanic that assumes a scripted arc (a final Ideal, a series
  finale) has to become an open-ended ladder with a hard top.
- **Death real but telegraphed.** This favors mechanics with delayed lethality (Shardblade's delayed death,
  disclosed odds on the Chaos Lord evolution) over instant-kill mechanics.

---

## 1. Per-chapter findings

### Chapter 00 — Architecture (conventions, scales, attributes, tag-tree top levels, state model, tool surface, glossary)

- **The closed-primitive shape is the most-confirmed finding in both rounds, and it comes in five geometries 00 can choose from.**
  (a) *Cyclic adjacent pairs*: Stormlight's 10 Surges give 10 Orders, each with a fixed adjacent pair. Only 10 of the C(10,2)=45 possible pairs are legal (22%) **[R2 analysis]**.
  (b) *Grid*: Allomancy's 16 metals = 4 groupings (Physical/Mental/Temporal/Enhancement) × internal/external × push/pull.
  (c) *Cross*: Cradle's madra aspect × 4 technique archetypes (Striker/Enforcer/Forger/Ruler).
  (d) *Slot-within-slot with a hard cap*: HWFWM's 4 essences × 5 abilities = 20.
  (e) *Fixed elements, free recombination*: in Mother of Learning, humans *cannot invent new spell elements*, but existing ones recombine freely.
  *Rules out:* open acquisition such as Underworld's "copy any monster" and The Land's ever-multiplying schools.
  *→* 03 (tag-tree geometry), 04, 05.
  [R: reports/LitRPG mechanics for AI DM design.md §Combinatorial diversity comes from small closed sets] [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How does Surgebinding work mechanically] [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §How does Allomancy work] [R: research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md §Cradle] [R: research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md §Mother of Learning]

- **"Closed" must mean both slot count and pool size are fixed. HWFWM closes only the slot count.**
  - HWFWM's essence pool spans 5 rarity tiers with dozens of named essences (Uncommon alone lists Blood, Dark, Death, Ice, Light…; Legendary lists Dimension, Myriad, Sin, Vast, Visage, Void).
  - The 5 abilities per essence are *rolled* from an unenumerated set.
  - The report's "4 slots × 5 options = 5⁴ = 625" is therefore a hypothetical, not HWFWM's actual structure **[R2 analysis]**.
  - Stormlight and Allomancy close both slot count and pool size.

  *Warns:* a hard slot cap (the thing constitution V/P5 cite from HWFWM) does **not** by itself bound what the DM must know. Pools must be closed too.
  *→* 04, 05, data/*.yaml.
  [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How does the class/"Classification" system work] [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How do Awakening Stones work] [R: reports/LitRPG mechanics for AI DM design.md §Combinatorial diversity comes from small closed sets]

- **Attribute-count precedents, and the failure each one teaches.**

  | System | Attributes | Lesson |
  |---|---|---|
  | HWFWM | **4**: Power (strength + "meta-weight", i.e. how much you get thrown around by same-or-lower ranks), Speed (flexibility, dexterity, velocity), Spirit (senses, mental aspects, ability strength, *mana pool size*), Recovery (recovery rate of mana/stamina/health *and affliction duration*) | Each is hard-bonded to one essence, so the stat spread is an *output* of identity choices, not a spent currency |
  | The Land | **9** primaries (Str, Agi, Dex, Con, End, Int, Wis, Cha, Luck) + ~7 secondaries (Concealment, Creativity, Intuition, Mental Aegis, Natural Armor, Perception, Resilience) | Secondaries were "never fully quantified" yet carry hard numbers later (e.g. Perception 15, Creativity 3.26). Strength = +10 kg carry per point |
  | Underworld | **5** (Str, Dex, Con, Int, Wis) | Int became "redundant" because Wisdom was overloaded to cover elemental magic |
  | GURPS | **4** (ST, DX, IQ, HT) | Buying +1 IQ raises every IQ-based skill at once, so it is cheaper than raising skills individually (attribute arbitrage) |
  | Primal Hunter | 7+ (Str, Agi, End, Per, Int, Willpower, Wis) | — |
  | 5e | 6 | Ability scores capped at 20 (+5) |

  *Rules out:*
  - attributes with overlapping lanes (one becomes vestigial);
  - derived stats without formulas;
  - attributes that are cheap to raise post-creation (arbitrage).

  P4's "mostly fixed at creation" contains arbitrage, but any item or effect that raises an attribute reopens it.
  *Design note:* HWFWM gives an attribute ownership of a *time axis* (Recovery shortens afflictions) and a *tier-relative* axis (Power vs. same-or-lower ranks). Attributes need not only add to d20 rolls.
  *→* 02, 06, 07.
  [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How do core Attributes work] [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §How do core stats/attributes work] [R: research_notes/LitRPG mechanics for AI DM design/underworld_level_up_or_die.md §How do core stats/attributes work] [R: research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md §How do point-buy systems like GURPS] [R: research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md §The Primal Hunter] [R: research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md §How does D&D 5e's "bounded accuracy" work]

- **The numeric envelope must be stated: bounded accuracy caps the total bonus at about +11 so the d20 always matters.**
  - 5e caps: proficiency about +6, magic weapons +3, ability modifier +5 (score 20), max DC 30, max AC 30.
  - Flat attack-bonus feats were *removed* in favor of advantage.
  - Content that pushes a build past the envelope "breaks the system," because monster math assumes PCs stay inside it.
  - What bounded accuracy buys: a low-level horde (an orc horde) stays a credible threat at high level, and 5e could delete 4e's "minion" category.
  - *Limit:* bounded accuracy caps numeric spread but does **not** equalize capability ("linear fighter, quadratic wizard" survived the 2024 PHB).

  *Warns:* a chapter-00 modifier cap is necessary but not sufficient for balance. Capability parity needs separate levers (P9 action economy, spotlight).
  *→* 01, 05, 06, 09.
  [R: research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md §How does D&D 5e's "bounded accuracy" work] [R: reports/Mistborn TTRPG AI design patterns.md §TTRPG balance theory supplies]

- **Show banded tiers, not raw large integers, for anything that can grow.**
  - Underworld escalated to enemies "in the thousands and tens of thousands" of levels. Bare numbers like "level 8,000 vs 8,050" stop reading as felt difficulty.
  - Cradle exposes no numbers at all, only rank names.
  - The Land's genre retrospective records the corrective: "significant milestones only."

  The raw number is still needed for adjudication math, so the mapping function (raw → band) must be explicit.
  *→* 09 (threat bands), 14 (codex display).
  [R: reports/LitRPG mechanics for AI DM design.md §Candidate primitives and patterns] [R: research_notes/LitRPG mechanics for AI DM design/underworld_level_up_or_die.md §Complexity of tracking/adjudicating] [R: research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md §Cradle] [R: reports/Mistborn TTRPG AI design patterns.md §An updated, tradeoff-flagged primitive list]

- **A single generic "scale" data type is precedented: named bands + numeric thresholds + an effect per band.**
  The Land reuses one template for skill ranks, Settlement Loyalty (−7..+7 with productivity %), Morale (±100% on growth, productivity and fighting spirit together), Fighting Spirit (−5..+5 = ±50% damage), the War Leader rank ladder (7 ranks with per-battle point quotas), Building Quality and Alchemy tiers.
  The report's verdict: the template "generalizes cleanly from character to faction."
  00 should define the type once for 03/07/10/11 to instantiate.
  *Warns:* band boundaries must not overlap. The Land's own skill bands give Adept 70–100 and Master 100–149, so level 100 is in both (see §4).
  [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §Crafting, settlement-building, and other non-combat progression] [R: reports/LitRPG mechanics for AI DM design.md §The Land stacks three parallel progression ladders] [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §How do skills work]

- **The state model must be externalized and authoritative. Three unrelated domains converge on this.**
  - AI Dungeon's "forgets names/threads/relationships" complaint (root cause: a ~4,000-token free-tier context) survived multiple full relaunches ("Renaissance", "Saga"). That persistence is evidence that bigger context and prompt engineering are insufficient.
  - Generative Agents (Smallville, 25 agents) use a memory stream + reflection + planning.
  - Voyager keeps a vector-indexed skill library of *verified* code, retrieving the top-5 relevant entries per task. Result: 3.3× more unique items, 2.3× travel distance, up to 15.3× faster tech milestones.
  - FictionRAG splits memory into **three lanes: factual events, persona traits, worldview constraints**. This is a ready-made partition for the facts store.

  *→* 12, 11.
  [R: research_notes/Mistborn TTRPG AI design patterns/ai_game_integration.md §What is AI Dungeon] [R: research_notes/Mistborn TTRPG AI design patterns/ai_game_integration.md §What academic research exists on LLM agents] [R: research_notes/Mistborn TTRPG AI design patterns/ai_game_integration.md §What patterns exist for preventing an LLM from overriding rules] [R: reports/Mistborn TTRPG AI design patterns.md §AI Dungeon's decade of failures]

- **The tool surface has two function classes in the only quantified AI-GM study, plus an injected rules summary.**
  - "Thirteen Hours" (arXiv:2409.06949) defines **dice-roll functions** (`activate_test`: generates the roll and decides success/failure; narration cannot alter it) and **state functions** (`create_npc`, `add_item`: own all transitions).
  - It also injects a "manually summarized" rules digest into the prompt.
  - Results: consistency **4.388/5** with all functions vs **3.691/5** with none; enforcement reliability (correctly *rejecting* actions a player shouldn't be able to take) **3.949/5**; state-prediction exact match only **46.1%**.

  The project's current tools (`roll_check`, `get_state`, `update_resource`, `set_fact`, `grant_ability`) map onto these two classes. 00 should add the classes the rules will need (tag evidence write, condition apply/tick, table roll, clock tick).
  *Warns:* function calling is necessary, not sufficient. Every rule must name its state writes (BRIEF chapter-format "State touched").
  [R: research_notes/Mistborn TTRPG AI design patterns/ai_game_integration.md §What other notable "AI Dungeon Master" projects exist] [R: reports/Mistborn TTRPG AI design patterns.md §AI Dungeon's decade of failures]

- **A status/effect registry is mandatory, with per-status fields for stack count, decay timer and interaction rules.**
  - HWFWM's closed 20-ability kit still produced **~35 distinct named boons/afflictions for one character** by Book 12.
  - The author needed **three appendix chapters** (Appendix II–IV).
  - The fandom built spreadsheets, a wiki, and a Discord lookup bot, described as "a fan-built GM toolkit."
  - Stacking rules varied per status: "[Blood of the Immortal]: stacking but does not grow stronger" vs "[Sin]: stacking, increases necrotic damage taken" vs "[Penance]: stacking, drops off over time."

  *Warns:* closure of the *slot grammar* does not close the *status vocabulary*. 00 must close both.
  *→* 06 conditions, 05 (P6 behavioral tags).
  [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §Is there indication of how complex/trackable] [R: reports/LitRPG mechanics for AI DM design.md §Comprehensible live adjudication demands bounded slots]

- **Per-track records have a three-field precedent.**
  The Land tracks every skill as (level, progression-%, affinity-%) independently of character level. Book-1 examples: Archery 4/85, Imbue Arrow 3/93, Life Magic 1/11, Stealth 4/49.
  This transfers to per-tag records: tally, progress to next threshold, hidden aptitude.
  *→* 03.
  [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §How do skills work]

- **Every tracked field must resolve to a value.**
  Underworld's on-page sheet repeatedly showed "unknown" on multiple stat lines, so the UI had more line-items than the story ever resolved.
  *Rule-writing implication:* no state field may be declared without a defined initial value and update rule.
  [R: research_notes/LitRPG mechanics for AI DM design/underworld_level_up_or_die.md §How do core stats/attributes work] [R: research_notes/LitRPG mechanics for AI DM design/underworld_level_up_or_die.md §Complexity of tracking/adjudicating]

- **Glossary: limitation / weakness / cost (Sanderson's Second Law, "Limitations > Power").**

  | Term | Definition | Example |
  |---|---|---|
  | Limitation | What it can target/do | Steel/Iron push/pull only directly toward/away from metal. Sanderson says Mistborn's metals and Stormlight are **limitations, not costs** |
  | Weakness | External vulnerability | Kryptonite |
  | Cost | A price paid elsewhere in the fiction | Wheel of Time's male-channeler insanity |

  Hemalurgy adds the refinement that one mechanic can carry **two independent cost axes**: a quantitative loss and a qualitative vulnerability.
  *→* 05, all chapters.
  [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §What are Sanderson's (Three) Laws of Magic] [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §How does Hemalurgy work]

- **Sanderson's Third Law sub-principles as architecture rules for adding content.**
  - *Extrapolation*: work out a mechanic's social, political and economic consequences.
  - *Interconnection*: a character's powers should "seem like a coherent whole rather than separate abilities." Mistborn's powers were derived from "what thieves would want."
  - *Streamlining*: show existing magic used differently by a new culture before inventing a new system, but not so far that plausibility drops.
  - Headline: "Expand on what you have already, before you add something new."

  *→* 04, 05, 11, 13 (new content reuses primitives), VI.
  [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §What are Sanderson's (Three) Laws of Magic]

- **Candidate top-level tag axes found in the sources.**

  | Axis | Precedent content |
  |---|---|
  | **Domain** | Stormlight's 10 Surges (Adhesion, Gravitation, Division, Abrasion, Progression, Illumination, Transformation, Transportation, Cohesion, Tension). Cradle aspects (earth, stone, water, life, lightning, blood, shadow, fire, force, pure). Allomancy groupings (Physical, Mental, Temporal, Enhancement). MoL's 15 disciplines + 2 support fields (named: Projection, Negation, Animation, Blood Magic) |
  | **Method / shape** | Cradle's Striker (project outward), Enforcer (empower body/equipment), Forger (create independent constructs), Ruler (control ambient aura at scale). HWFWM's 6 ability categories (Aura, Conjuration, Familiar/Summon/Puppet, Special Ability incl. Perception, Special Attack, Spell). Allomancy's internal/external × push/pull |
  | **Values / behavior** | Stormlight's 20 spren-attraction attributes (full list under 03) |
  | **Trade vs combat** | The Land's split: ~31 non-combat professions vs ~8 combat professions, with different profession thresholds |

  *→* 03 owns content; 00 owns the top levels.
  [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How does Surgebinding work mechanically] [R: research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md §Cradle] [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §How does Allomancy work] [R: research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md §Mother of Learning] [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How do Perks and Feats work mechanically] [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §How does the class system work]

- **Keep moderation/safety gating separate from world-state/consistency gating.**
  - AI Dungeon's 2021 filter had a high false-positive rate that "soft-locked" innocent scenarios. Its Google Play rating fell **4.8 → 2.6** and the Discord moderation team was briefly overwhelmed.
  - A separate privacy misstep (reading private stories to build the filter) compounded it.
  - Moderation can tolerate reversible false positives; state consistency cannot.

  One line in 00's contracts suffices (the BRIEF de-scopes LLM infrastructure).
  [R: research_notes/Mistborn TTRPG AI design patterns/ai_game_integration.md §What is AI Dungeon] [R: reports/Mistborn TTRPG AI design patterns.md §AI Dungeon's decade of failures]

- **Any classification step needs an abstain branch and an independent checker.**
  - The LLM-judge literature recommends a three-valued gate: confident failure at p ≥ 0.9, pass at p ≤ 0.5, *abstain-and-escalate* in between.
  - A live repo flagged "GLM judging GLM" (same model family as judge and agent) as invalidating its own comparison.
  - TypeSafe's Jev is a real non-generative classifier: up to 255 caller-defined options, calibrated probability per option, ~70–500 ms, ~$0.001 per decision.

  Constitution III currently adopts **no** judge gate. The transferable *rule-design* point is that every [J] rule should specify what the DM does when it cannot decide.
  *→* 04 (grant/offer/abstain), 12.
  [R: research_notes/Mistborn TTRPG AI design patterns/ai_game_integration.md §What patterns exist for preventing an LLM from overriding rules] [R: reports/Mistborn TTRPG AI design patterns.md §AI Dungeon's decade of failures]

- **Regression-test precedent: "dialogue-game-based evaluation."**
  A game-master harness runs scripted episodes, validates responses "against formal rules," and scores rule compliance programmatically. This is a template for the appendix's named empirical tests.
  [R: research_notes/Mistborn TTRPG AI design patterns/ai_game_integration.md §What academic research exists on LLM agents]

### Chapter 01 — Resolution (capability gate, DCs, modifiers, degrees, P17, compound/opposed/group, advantage)

- **PF2e's four degrees are the source of the project's resolution rule, but the project's natural-20/1 rule differs.**
  - *PF2e:* beat the DC by 10+ = critical success; miss by 10+ = critical failure; a natural 20 **shifts the degree up one step** and a natural 1 **down one step**.
  - *The project (BRIEF §7):* a natural 20 **is** a critical success and a natural 1 **is** a critical failure, regardless of total.
  - **[R2 analysis, exact enumeration]** The two rules differ only at the edges:
    - (i) +2 vs DC 25: a nat 20 totals 22, which misses. The project calls it a critical success (5%); PF2e calls it a plain success.
    - (ii) +12 vs DC 10: a nat 1 totals 13, which passes. The project calls it a critical failure (5%); PF2e calls it a plain failure.
  - Under the project rule an expert *critically fails a trivial task 5% of the time*. That grates against "a single unlucky roll never ends a character without warning" wherever critical failure carries harm.

  *→* 07.
  [R: research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md §How do Pathfinder 2e's three-action economy] [R: reports/Mistborn TTRPG AI design patterns.md §TTRPG balance theory supplies]

- **[R2 analysis] At the default +2 modifier, the ±10 critical-failure band makes hard DCs dangerous.**

  | +2 vs | Crit fail | Fail | Success | Crit success |
  |---|---|---|---|---|
  | DC 10 | 5% | 30% | 50% | 15% |
  | DC 15 | 15% | 45% | 35% | 5% |
  | DC 20 | **40%** | 45% | 10% | 5% |
  | DC 25 | **65%** | 30% | 0% | 5% (project) / 0% + 5% success (PF2e) |

  At +5 vs DC 20: 25 / 45 / 25 / 5. At +8 vs DC 25: 35 / 45 / 15 / 5.
  The resolution author must decide what critical failure *costs* at DC 20+ for low-modifier characters, or those DCs become trap attempts.
  *→* 07 (defeat outcomes), 12.
  [R: research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md §How do Pathfinder 2e's three-action economy]

- **Math-first beats rulings-over-rules for an AI adjudicator. The documented AI-GM risk is "theatrical flair" over mechanics.**
  - "5e asks for more judgement calls, while Pathfinder 2e asks for more rules fluency."
  - PF2e "replaces the patchwork of special-case rules... with four defined outcome tiers that govern every check."
  - AI-GM discourse: models "may ignore or misunderstand mechanics in favor of theatrical flair."

  *Rules out:* unstructured DM rulings as the default for anything with stakes.
  *→* 12.
  [R: research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md §How do Pathfinder 2e's three-action economy] [R: research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md §Is there existing design discourse about TTRPG systems built to be run by a computer/AI GM]

- **Advantage-style circumstance mechanics are the envelope-safe way to reward favorable circumstances.**
  5e *removed* feats with flat attack bonuses and used advantage instead, precisely to protect bounded accuracy.
  This argues for an advantage-type modifier (or a degree shift) over stacking +N bonuses for circumstance and creative positioning.
  *→* 06.
  [R: research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md §How does D&D 5e's "bounded accuracy" work]

- **Modifier stacking must be specified.**
  - Dungeon Crawler Carl sums 3–4 independent sources for one action: a skill's per-level scaling (Pugilism +25% bare-knuckle damage per level), gear (Toe Ring +3 to Powerful Strike; War Gauntlets +2 to Iron Punch), and temporary Skill Tonics.
  - Underworld reportedly mixes flat and percentage modifiers (e.g. "+5 Str/+5 Dex/+5 Con", "−49% Wisdom"). **Unverified; possibly search-summary hallucination.**

  *Warns:* without stacking rules (which sources stack, which take the highest), modifier inflation breaks the envelope.
  *→* 05, 08.
  [R: research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md §Dungeon Crawler Carl] [R: research_notes/LitRPG mechanics for AI DM design/underworld_level_up_or_die.md §How do core stats/attributes work]

- **PbtA bands, and when "partial success is most common" is actually true.**
  - PbtA: 2d6 + modifier; 10+ full success, 7–9 partial or hard choice, 6− the GM makes a move. "Failure should still move the plot forward."
  - **[R2 analysis]** Partial success is *strictly* the most common result only at +1 (27.8 / 44.4 / 27.8%). At +0 it ties with a miss (16.7 / 41.7 / 41.7). At +2 it ties with full success (41.7 / 41.7 / 16.7).
  - Transferable idea: every non-success result must change the situation (→ P16), and a "success at a cost" reading of the failure band is PbtA-precedented.

  *→* 12.
  [R: research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md §How do "Powered by the Apocalypse" (PbtA) games]

- **Capability gate (VII): the sources supply a taxonomy of license sources.**
  1. Innate or birth: a Misting's single metal "for life"; Allomancy is hereditary.
  2. Recognized identity: the Order's two Surges from the spren bond.
  3. Tier-gated within an identity: "some orders cannot use one of their Surges until they swear a higher Ideal"; Radiants "often learn their 'anti-clockwise' Surge first."
  4. Item-conferred: Honorblades grant an Order's two Surges to *anyone*, "without regard for oaths," but "consume far more Stormlight" and give none of the bond's extras.
  5. Borrowed, range- and time-limited: a Squire's power fails beyond **30–50 miles** from their Radiant, or within **1–2 hours** of an Oathgate separation, and holds Stormlight less efficiently.
  6. Stolen or grafted: Hemalurgy.

  **Declaration is not a license:** Radiants "cannot just say the words to advance."
  The only quantitative datum on correct gating is the Thirteen-Hours "enforcement reliability" of 3.949/5.
  *→* 04, 05, 08.
  [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How do Ideals/oaths gate power growth] [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How does Surgebinding work mechanically] [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How do Shardblades and Shardplate fit] [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §How does Allomancy work] [R: research_notes/Mistborn TTRPG AI design patterns/ai_game_integration.md §What strategies exist for balancing player-facing creative/build customization]

- **Sanderson's First Law is a fairness rule for the DM: no deus ex machina.**
  - "An author's ability to solve conflict with magic is DIRECTLY PROPORTIONAL to how well the reader understands said magic."
  - Ideally "the magic is explained to the reader before it is used to resolve a conflict," which avoids "Where did he get that?"
  - Rule-level translation: a license (or an NPC power) should not *decide* a conflict unless its limits and possibilities were established first (codex entry, foreshadowing, prior demonstration).
  - Sanderson's *middle ground* (his Harry Potter example): the reader knows limits and possibilities without knowing the workings.

  *→* 09 (foreshadow adversary powers), 12, 14.
  [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §What are Sanderson's (Three) Laws of Magic] [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §Is there commentary on how Sanderson keeps]

- **Mother of Learning's structured vs. unstructured magic is the best precedent in either round for letting players push a licensed ability creatively without narrating capability into existence (goal 1).**
  - *Structured* magic: rigid constructs invoked by fixed words and gestures. Learnable in weeks, reliable, narrow possibility space.
  - *Unstructured* magic: shaping without a spell boundary. Flexible, but can take "years/decades" for complex effects.
  - Advanced practitioners gain *flexibility within a structured spell's boundary* through mastery, and eventually cast reflexively without components.

  Translation: a licensed ability used as written resolves normally. A creative extension *of the same ability's principle* is an "unstructured" attempt at a higher DC, a higher cost, or more time. Tier or mastery widens what counts as structured.
  This keeps VII intact (the extension must share the ability's principle) while answering "can I use my power to do X?" with "yes, harder" rather than "no."
  *→* 05, 12.
  [R: research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md §Mother of Learning]

- **One governing principle per ability lets the DM extrapolate novel uses consistently (Allomancy's push/pull).**
  - Iron pulls metal toward you; Steel pushes it away. Per Newton's third law, pushing a light object (a coin) sends *it* flying, while pushing a heavy anchor (a building) sends *you* flying.
  - The same verb resolves differently by relative mass, "a physics-grounded limitation baked directly into the verb."
  - Sanderson's origin: a "limited" version of Star Wars telekinesis.

  If every ability template carries a governing principle plus a "cannot" list, novel uses become derivable rather than invented (goal 2).
  *→* 05, 12.
  [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §How does Allomancy work] [R: reports/Mistborn TTRPG AI design patterns.md §Mistborn's three magic systems]

- **"Flare" is a generic, voluntary boost of degree or effect for extra cost.**
  In Allomancy (as adapted by MAG), each metal burns at its own rate ("instantaneous up to 40 minutes") and has a *flare* mode that boosts potency "at the cost of drastically accelerated consumption."
  This is a clean universal "push it" option for any active ability, tied to Focus.
  *→* 05.
  [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §How does Allomancy work]

- **Opposed checks across a large tier gap may skip the roll.**
  - Cradle: "it takes ten Coppers to challenge an Iron, and ten Irons to challenge a Jade," an ~10× gap per rank.
  - HWFWM Silver: "a killing blow from a Normal/Iron/Bronze attacker no longer seriously harms a Silver-ranker."
  - HWFWM Power: "the less one is thrown around by those of the same or lower ranks."

  Precedent for a rule: beyond a set band gap, certain outcomes are auto-resolved (VII-style "not a legal attempt") rather than rolled.
  *→* 06, 09.
  [R: research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md §Cradle] [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How does leveling work] [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How do core Attributes work]

- **A fixed action budget prevents compressing many attempts into one action.**
  PF2e gives every character 3 actions + 1 reaction; common costs are Stride 1, Strike 1, Raise a Shield 1, most spells 2, open a door 1. This "closes off action-economy-stacking exploits."
  This is the rule-level answer to the probe's "10 attacks in one action" improvisation (BRIEF §7).
  *→* 06.
  [R: research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md §How do Pathfinder 2e's three-action economy]

- **"Rule of Cool" / "yes, and… then make the mechanics match the fiction" is the only AI-specific creative-action guidance found, and it is unverified.**
  - The Rule-of-Cool guidance file 404'd.
  - `resolve_improvised_stunt` is "possibly hallucinated."
  - Sanderson's unofficial Zeroth Law ("Err on the side of AWESOME") is a *design-order* principle (start from the awesome idea, build rules around it), not a runtime override.

  *Warns:* do not import Rule of Cool as a licensing rule. It conflicts with VII and III ("no blanket narrative override"). It can govern *how the DM frames the redirect* (goal 1) and outcome color on success.
  *→* 12.
  [R: research_notes/Mistborn TTRPG AI design patterns/ai_game_integration.md §What strategies exist for balancing player-facing creative/build customization] [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §What are Sanderson's (Three) Laws of Magic]

- **The creative-action fairness problem is genuinely unsolved in the literature.**
  "The near-total absence of dedicated literature here is itself informative." No academic paper treats AI adjudication of creative actions as its subject.
  Chapter 01 is writing new ground, so worked examples and edge-case anchors carry more weight than usual.
  [R: research_notes/Mistborn TTRPG AI design patterns/ai_game_integration.md §What strategies exist for balancing player-facing creative/build customization] [R: reports/Mistborn TTRPG AI design patterns.md §AI Dungeon's decade of failures]

- **Graduated reveal (P17) has two in-fiction analogues useful for anchoring reveal degrees.**
  - Detection: Bronze reveals others' Allomantic pulses; Copper conceals them from Seekers (a detection vs. concealment contest).
  - Foresight: Truthwatchers show "at least two demonstrated cases of foresight"; Atium/Gold effects relate to future and past perception (low-confidence metal names).

  *→* 10.
  [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §How does Allomancy work] [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §What makes different Radiant orders/characters feel mechanically distinct]

- **Rolls must be visible and tool-owned so the player trusts hidden variance.**
  Hidden variance "needs a GM-side RNG the player trusts." The dev.to write-up names the failure: "an AI Dungeon Master might declare a player rolled a 47 on a twenty-sided die." (Low-confidence source; the principle is corroborated by the arXiv paper.)
  [R: reports/LitRPG mechanics for AI DM design.md §Candidate primitives and patterns] [R: research_notes/Mistborn TTRPG AI design patterns/ai_game_integration.md §What patterns exist for preventing an LLM from overriding rules]

### Chapter 02 — Character (creation, attributes, origins/P4, birth variance/P1, baseline floor/P2, starting kit)

- **Decouple access breadth from starting competence: the Mistborn Adventure Game's stated fix.**
  - Crafty Games named the risk: "how do you let people play Mistborn and not have everybody else suck."
  - Mistborn (all-metal) characters start with "mediocre stats," and *every* character picks attributes they are **strong, average, and weak** in.
  - A Misting has 1/16 (or 1/8) of a Mistborn's toolkit but stays competitive.

  This is the precedent behind constitution P4.
  *Evidence caveat:* the source is a WebSearch synthesis of a fandomwire listicle, so "tabletop-tested" is the report's gloss (§4 T-6).
  The strong/average/weak ranking is also an alternative to point-buy that sidesteps P11 auditing.
  *→* 04 (hybrids), 00.
  [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §Documented power-creep / balance discussion] [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §How does this compare to Surgebinding's design] [R: reports/Mistborn TTRPG AI design patterns.md §Mistborn's three magic systems]

- **Origin as a quantity-vs-freedom trade (The Land).**
  - Humans: **4** stat points per level, fully free placement ("broader affinity for skills"; "no special bonuses").
  - Chaos Seed sub-race: **6** per level, fully free, plus **15** talent points (vs 10) and **+25% skill progression per level**.
  - Other races: "up to 5" with partial forced auto-allocation.

  The project has no levels (P2), so this transfers as an *origin package* trade: more starting power but constrained placement, vs less power but free placement.
  *Warns:* "only works if every option is calibrated to feel roughly equal in total value."
  *→* 00.
  [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §How do core stats/attributes work] [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §How does the class system work] [R: reports/LitRPG mechanics for AI DM design.md §Candidate primitives and patterns]

- **Cap-for-restriction (Primal Hunter): accept a qualitative restriction to earn a higher ceiling.**
  At E-grade an unrestricted profession caps at **22** total stats; a profession "carrying severe restrictions" caps at **27**.
  Because the restriction is qualitative, "a flexible generalist path is never strictly dominated."
  This transfers to origin or oath options such as "swear never to use X, gain +N ceiling in Y." It rhymes with Stormlight oaths.
  *→* 04 (vows), 05.
  [R: research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md §The Primal Hunter] [R: reports/Mistborn TTRPG AI design patterns.md §Five more progression-fantasy series]

- **HWFWM racial gifts: a fixed, small origin package that includes an affinity bias.**
  - "Racial Abilities? Everyone gets **6**," usually including a fixed Affinity.
  - Examples: humans get faster ability growth and an inclination toward special attacks; Elves lean caster (nature/life/magic); Leonids get better stamina recovery and lower stamina consumption.
  - Racial gifts "can go through evolution. Usually from traumatic events." This is a crisis-awakening vehicle (→ 04).
  - Two characters with identical essences still diverge by race.

  Transferable: an origin = a small fixed gift set, one of which *biases later rolled fills* (P1 layered variance).
  [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How do Perks and Feats work mechanically] [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How does the class/"Classification" system work] [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §What makes two characters' builds feel meaningfully distinct]

- **P1 birth-variance precedents: The Land's per-skill Affinity is the cleanest.**
  - "Determined at birth and... thought to be random."
  - It governs *both* leveling speed *and* ceiling.
  - "A minimum starting affinity of 50 percent is required to learn a skill," and "affinity decreases with each level gained."
  - HWFWM's Awakening-Stone rolls are weighted by "race, essences, what the person knows... and what hasn't been awakened," with personality theorized.
  - **Neither source allows a reroll.** P1's deferred reroll is the project's deliberate departure.

  *Warns:* hidden variance "can read as unfair ('why did I roll worse') unless framed narratively."
  *→* 03 (per-tag hidden aptitude), 14 (show as qualitative descriptors).
  [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §How do skills work] [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How do Awakening Stones work] [R: reports/LitRPG mechanics for AI DM design.md §Emergent, personal-feeling builds need a hidden variance layer]

- **An innate "restriction-remover" at creation, with "unique class" moments reserved for later gated events.**
  - Richter's Book-1 uniqueness is not a class. It is three innate Abilities: **Limitless** (100% affinity in any skill, *including race-bound ones*), **Gift of Tongues** (understands nearly any sapient language), and **Fast Learner** (+30% skill advancement).
  - The note's recommendation: "give the PC one or two innate rule-breaking Abilities at creation (remove a specific restriction other characters face) and reserve 'unique class'-feeling moments for rare, narratively-gated Evolution/Ascension events later."

  *Warns:* Limitless made Richter "good at just about everything," i.e. an ace. A restriction-remover must be narrow.
  *→* 04.
  [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §How does the class system work]

- **Pacing gates for permanent choices: a tutorial before lock-in, and deferral with a deadline.**
  - DCC locks stat allocation until **Floor 3**, so early play runs on automatic, action-based skill leveling.
  - HWFWM's community wisdom: wait to awaken abilities until you hold your full essence set, to bias rolls toward synergy.
  - The Land's anti-stall valve: points unspent across more than one level "for a week" are **randomly assigned automatically**.

  Combined, these give P1's deferred reroll and P2's early floor a concrete shape: choices may be deferred, but a deferral has a stated deadline and a default.
  *→* 04, 13 (opening scenario as the tutorial phase).
  [R: research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md §Dungeon Crawler Carl] [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How do Awakening Stones work] [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §How do core stats/attributes work]

- **Point-buy warnings (P11).**
  - GURPS's designers: "the points hadn't created balance—they had created identity." A 200-point physicist "can be chopped into kindling by a 40-point combat-optimized fighter."
  - Disadvantages get gamed: players take ones with "little or no tangible effect on play" to refund points. GMs are advised to cap disadvantages at ~50% of the pool (e.g. −75 in a 150-point game). It takes "an eagle-eyed GM."
  - 5e: multiclass/MAD characters are *meant* to pay slower primary-stat progression for versatility. Removing that price makes the game "less good."

  *Rules out:* unaudited shared point pools; flaws-for-points without enforcement.
  *→* 04 (hybrid cost).
  [R: research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md §How do point-buy systems like GURPS] [R: research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md §How does D&D 5e's "bounded accuracy" work]

- **P2 baseline floor: the strongest precedent is Stormlight's First Ideal, which is identical for all ten Orders.**
  - "Life before death. Strength before weakness. Journey before destination." The wording is "exact and is used by all orders, including the Lightweavers and Elsecallers."
  - A *universal tier-0 package every character holds regardless of identity* is exactly a baseline floor.
  - Other floor shapes:
    - HWFWM's **Normal** rank "includes people who have some, but not all essence slots used" (a partial-slot floor).
    - MoL's **five prerequisite skills** before any spellcasting (sense own reserves; draw quickly and reliably; direct along pathways; visualize the effect; hold concentration). These take "roughly 2–4 years" and "cannot be shortcut."
    - Cradle's **Foundation** rank.
    - Stormlight **Squires** (borrowed power from a mentor, → 04).

  *→* 04, 05.
  [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How do Ideals/oaths gate power growth] [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How does leveling work] [R: research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md §Mother of Learning] [R: research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md §Cradle]

- **Players will optimize, and that is not bad faith (Elorion; the Alexandrian).**
  - Underworld's protagonist "gathers plenty of data to figure out the system before committing stat points." Critics found the result depthless.
  - The Alexandrian: optimization "often stems from logical in-character motivation rather than metagaming malice," and is inevitable in "any system featuring 2+ choices... that have a mechanical impact."

  Creation rules should expect a researching player and remain robust (P11).
  *→* 12, 14.
  [R: research_notes/LitRPG mechanics for AI DM design/underworld_level_up_or_die.md §What makes builds feel distinct] [R: research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md §Designer blogs/essays]

- **Generalist vs specialist at creation: the Misting/Mistborn cliff is the anti-pattern.**
  Access in Allomancy is "binary, not gradient": a Misting has one of the 8 basic metals for life, a Mistborn has all. There is "no incremental unlock path." This is "a much starker access cliff than Surgebinding's."
  *Rules out:* a "does everything" origin with no compensating handicap.
  *→* 04.
  [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §How does Allomancy work]

### Chapter 03 — Tags & evidence (vocabulary, `tag_event`, tallies, weighting, recency)

- **Stormlight's spren-attraction attributes are a ready-made, closed, behavior-based identity vocabulary.** Ten Orders × two attributes = 20 values:

  | Order | Values | Surges |
  |---|---|---|
  | Windrunners | Protecting / Leading | Adhesion + Gravitation |
  | Skybreakers | Just / Confident | Gravitation + Division |
  | Dustbringers | Brave / Obedient | Division + Abrasion |
  | Edgedancers | Loving / Healing | Abrasion + Progression |
  | Truthwatchers | Learned / Giving | Progression + Illumination |
  | Lightweavers | Creative / Honest | Illumination + Transformation |
  | Elsecallers | Wise / Careful | Transformation + Transportation |
  | Willshapers | Resolute / Builder | Transportation + Cohesion |
  | Stonewards | Dependable / Resourceful | Cohesion + Tension |
  | Bondsmiths | Pious / Guiding | Tension + Adhesion |

  - Spren choose "according to the actions and personalities of those people," so eligibility is *behavior-gated*.
  - The same data point does double duty as matchmaking gate and characterization shorthand.
  - The gate operates below full rank too: squire candidates need "a mental state geared to protection."

  Transferable: a **values/conduct branch** of the tag tree whose evidence is *choices*, not dice. Constitution P5 already allows no-roll, values-expressive evidence.
  *→* 04.
  [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How does Surgebinding work mechanically] [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §What makes different Radiant orders/characters feel mechanically distinct]

- **Hierarchical cascade precedent: The Land's two-rule sub-skill tree.**
  1. A sub-skill's level "cannot be higher than that of the parent skill."
  2. "Any increase in a subskill will result in an increase in the parent skill's level."

  You may acquire a sub-skill before its parent, but "if you learn a sub-skill you will also learn the parent." The report calls this "a simple two-rule tree structure... a live adjudicator could implement cheaply." It is the direct precedent for P5's "a narrow event counts at every ancestor level."
  *Note:* under a pure cascade, parent ≥ child holds automatically, so rule 1 is redundant **[R2 analysis]**.
  [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §How do skills work] [R: reports/LitRPG mechanics for AI DM design.md §The Land stacks three parallel progression ladders]

- **The multi-credit question is named precisely by DCC.**
  Use-based leveling means "the GM has to notice when an action qualifies as 'using' a given skill and increment it, including edge cases (does using an explosive in a novel way count toward IED as well as a new skill?)."
  Bookkeeping must track "usage counts/context per skill, not just allocate points."
  The hierarchy answers the vertical part: credit every ancestor. 03 must also answer the lateral part: when does one moment credit two unrelated leaves? This is exactly the hybrid-evidence question.
  [R: research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md §Dungeon Crawler Carl]

- **Evidence quality matters more than quantity. Cheap, repeatable evidence must saturate.**
  - HWFWM has an "honest" path (training, "real danger," "post-battle meditation") and a monster-core path described as "cheap" and "**self-limiting**."
  - The core path "caps most users below Diamond," and makes Gold's required "Essence Revelation" *harder* for core-users. (Exception: crafters can reach Diamond purely through crafting.)
  - Cradle ties advancement to "spiritual development and understanding rather than time investment or grinding alone," as "a deliberate authorial choice to avoid pure numbers-go-up power creep."
  - Stormlight: "cannot just say the words."

  Transferable to `tag_event` weighting: weight by stakes/risk, cap low-stakes repetition per scene or context, and require a *qualitatively distinct* evidence event for higher tiers rather than more of the same.
  *→* 04.
  [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How does leveling work] [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How do core Attributes work] [R: research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md §Cradle] [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How do Ideals/oaths gate power growth]

- **Negative (contrary) evidence exists and has consequences.**
  In Stormlight, "acting against the attributes that attracted the spren weakens the bond"; eventually the spren "breaks" (→ 04 revocation).
  Values tags therefore need *signed* evidence (for and against), not just positive tallies.
  The constitution's "Paladin can atone" framing and Stormlight's "recommitment" both assume contrary evidence is recorded.
  [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How do Ideals/oaths gate power growth]

- **Diminishing returns and rate multipliers are precedented and can be hidden.**
  - The Land: affinity "decreases with each level gained" (marginal gains shrink), Fast Learner +30%, Chaos Seed +25% progression per level.
  - HWFWM: humans advance abilities faster.
  - Non-canon CYOA: "Rapid Growth" ~25% faster.

  Per-tag hidden aptitude (P1) can be a rate multiplier and/or a threshold modifier.
  *→* 02.
  [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §How do skills work] [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §How does the class system work] [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How do Perks and Feats work mechanically]

- **The biggest distinctness lever is *category distribution*: what kind of thing your abilities mostly are.**
  HWFWM's inference: distinct builds should "differ in *what kind of thing their 15–20 abilities mostly are* and *how those abilities' status effects interact*, not just in bigger numbers."
  - Jason's kit is afflictions and drains (attrition).
  - Farrah's Volcano confluence is "overwhelming firepower."
  - A fan build sharing Jason's Dark essence rolled a completely different category mix (stealth-infiltration + summoner).

  This argues for a **method/shape axis** in the tag tree parallel to domain (the Cradle archetypes and HWFWM categories listed in 00).
  [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §What makes two characters' builds feel meaningfully distinct]

- **Emergent-by-history needs a bounded trigger set, or it degrades into Underworld.**
  The round-2 table: DCC's use-based auto-leveling and MoL's knowledge persistence are "tamer" emergent models that "still need a bounded trigger set (DCC: countable actions; MoL: a fixed spell-element library)."
  *Rules out:* evidence keyed to open-ended lists (every monster, every ability). This matches constitution P5's "low-cardinality keying."
  [R: reports/Mistborn TTRPG AI design patterns.md §An updated, tradeoff-flagged primitive list] [R: research_notes/LitRPG mechanics for AI DM design/underworld_level_up_or_die.md §Is there a distinctive hook]

- **Knowledge is a separate state kind from tallies (MoL).**
  Raw power resets each loop, but "procedural knowledge (which spell-element combinations work...)" persists. The "build" becomes "a knowledge-graph."
  A **known-techniques / known-facts ledger** is a distinct record type that 03 should not fold into tallies. It matters for legacy (→ 11) and for "established narrative fact" licenses (VII).
  [R: research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md §Mother of Learning] [R: reports/Mistborn TTRPG AI design patterns.md §Five more progression-fantasy series]

- **Audit trail for the scorer: store verified evidence, retrieve the relevant subset (Voyager).**
  Voyager stores *verified-successful* skills indexed by natural-language description and retrieves the top-5 for a new task.
  Transferable: each `tag_event` record carries a short natural-language description, so the DM can cite *why* a calling is being offered ("you held the bridge alone; you carried the wounded out…"). That is the fiction's voice for recognition.
  [R: research_notes/Mistborn TTRPG AI design patterns/ai_game_integration.md §What academic research exists on LLM agents]

- **Many domains, not just combat, should generate evidence (the Alexandrian's diversification).**
  "If characters must succeed at *multiple* distinct tasks... they structurally cannot hyper-specialize."
  The tag vocabulary's breadth across social, exploration, craft and values branches is what makes this possible.
  *→* 10, 12.
  [R: research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md §Designer blogs/essays]

### Chapter 04 — Recognition & growth (callings, scoring, grant/offer/abstain, tiers, provisional status, gated special traits)

**4a. In-fiction recognition vehicles without a System.** These are the owner's "oaths, reputation, mentors, awakenings."

- **Separate the mechanical recognition from its fictional vehicle. Stormlight lets the same power set arrive through different acquisitions with different strings attached.**
  Surges can come via:
  1. the Nahel bond (earned by character, grows with Ideals);
  2. an Honorblade (anyone, no oaths, higher cost, no extras);
  3. the Fused's Voidlight "brands" (9 brands, *one* Surge each; Adhesion is "of Honor" and unavailable to Odium);
  4. direct blessing ("unbound by oaths/rules and 'immensely dangerous,'" which destroyed a world);
  5. Nightblood.

  The note's inference: "vary *how* a character gets power (its narrative/moral cost) independently of *what* the power does mechanically — ... same 'class,' different acquisition fictions with different strings attached."
  The tally decides *that* a calling is recognized [D]. The DM picks *which vehicle* voices it [J].
  [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How does Surgebinding work mechanically]

- **"Something is drawn to you": the world initiates.**
  Spren seek bondmates by demonstrated attributes (see 03 table). Class eligibility is behavior-gated, not menu-picked.
  An order, patron or mentor approaching the PC *because of what they did* is the diegetic equivalent of an eligibility threshold being crossed.
  [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How does Surgebinding work mechanically] [R: reports/LitRPG mechanics for AI DM design.md §Stormlight gates power behind sworn oaths]

- **The oath vehicle: swearing an Ideal is the power-up moment, with a gatekeeper and a visible tell.**
  - "Whenever a Radiant swears an Ideal, they Connect to their spren..." and take "an influx of Investiture," described as "a confluence of power and Intent, along with an alignment of self."
  - "Swearing an Ideal releases a large amount of light, **proportional to what numbered Ideal it is**." This is a diegetic "level-up flare" that witnesses see, so it feeds reputation.
  - The Stormfather and Cultivation "have some discretion in deciding whether or not a Radiant has progressed enough that their oath can be accepted," but "this discretion appears to be limited." That is a bounded-judgment gatekeeper.
  - Ideals are "thought" to be sworn in order. Szeth's Fifth-before-Fourth-quest is "an explicit, flagged exception rather than a silent rule violation."

  Map: eligibility [D] → a moment [J] → an offered oath (P2/P5 "offer") → acceptance with a visible tell [N].
  [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How do Ideals/oaths gate power growth]

- **The mentor vehicle: Squires.**
  A full Radiant grants "lesser, order-specific power access... without their own spren bond." Squire power is "entirely parasitic on the nearby Radiant": it fails beyond **30–50 miles** of separation or within **1–2 hours** of an Oathgate separation, and squires hold Stormlight less efficiently.
  This is "an explicit 'apprentice tier' bolted onto the main progression."
  Transferable: (a) **a mentor's acknowledgement** as a pre-recognition vehicle; (b) a *provisional, dependent* tier that can serve as the P2 floor for characters attached to a recognized NPC; (c) a range/time condition that is trivially deterministic [D].
  [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How do Ideals/oaths gate power growth] [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §What makes different Radiant orders/characters feel mechanically distinct]

- **The trial / examination vehicle: The Land's Profession Trial.**
  - A dual threshold: overall level 10 + Journeyman in a non-combat skill, *or* level 20 + Journeyman in a combat skill. (The Trial page says level 20 + non-combat Journeyman; see §4.)
  - Then "ritual words are spoken indicating the profession are seeking, i.e. '**I am Alchemist**.'"
  - "One week of time passes in The Land."
  - This is Delve's primary/secondary structure (constitution P5) with a *ritual declaration* on top. The player's own words ("I am…") are the affirmation step.

  In a no-System world the "Nexus" becomes a guild examination, a masterwork judged by peers, or an order's rite.
  *→* 10 (downtime).
  [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §How does the class system work] [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §How does character leveling interact with skill leveling]

- **The institution vehicle: HWFWM's Magic Society and Adventure Society.**
  - "The in-world Magic Society keeps records of known combos." A *curated combination table held by an in-world institution* is the diegetic form of P5's sparse hybrid table. Scholars can *name* what you have become.
  - The Adventure Society "Restricts" certain essences and combinations (Death, Corrupt, Undeath, Succubus, Sacrifice, Wendigo, Cyborg) because they "push users toward harming innocents." Being caught "can put a bounty/kill-contract on the user."

  Recognition therefore has **social consequences**, positive and negative (→ 11 reputation).
  [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How does the class/"Classification" system work]

- **The crisis-awakening vehicle.**
  - HWFWM racial gifts "can go through evolution. Usually from traumatic events."
  - The Land's Chaos Lord evolution was offered "because he had entered the Sea of Chaos and survived," "a 99.9999% success rate" — a *survived ordeal* unlocking an offer, **with the odds disclosed**.

  → 07: telegraphed risk can carry explicit odds.
  [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How do Perks and Feats work mechanically] [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §How does the class system work]

- **The revelation / insight vehicle for higher tiers.**
  - HWFWM Gold: "monster-fighting/training alone stops being sufficient"; progression requires "**Essence Revelation**, a distinct, harder-earned breakthrough."
  - Cradle: advancement via "understanding."

  Higher tiers should need a *different kind* of evidence (an insight or ordeal moment), not just a bigger tally.
  [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How does leveling work] [R: research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md §Cradle]

- **The deed-becomes-legend vehicle.**
  DCC's AI showrunner "occasionally grants 'Unique' skills as rewards for unprecedented player feats — a discretionary, GM-adjudicated reward channel rather than a fixed table."
  In a no-System world, a title people start using after a singular deed is the same channel. It must still be bounded (P5: no ability list of its own) — for example, one bounded title-benefit.
  [R: research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md §Dungeon Crawler Carl]

- **The one-time choice vehicle.**
  The Land's "Choice" was earned once, for being first to a milestone (absorbing a Chaos Shard). It offered **3 mutually exclusive** rewards (double current Chaos Points / the ability Feel of Chaos / three extra Respawns) within a strict **7-second** in-fiction window.
  This is a precedent for P5's "offer" tier presenting *named, mutually exclusive* options at a crystallization moment. The time pressure is optional.
  [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §What makes builds feel distinct/personalized]

- **The lineage vehicle.**
  Allomancy and Feruchemy are "**genetic/hereditary** — access is a birth trait." Twinborn appeared only after Terris intermarried with the wider population.
  → 02 origins, and 11 legacy (an heir inherits a lineage trait).
  [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §How does Allomancy work] [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §What is a Twinborn]

- **The patron vehicle is revocable.**
  HWFWM divine essences "retain a permanent connection to their granting god, who can reclaim them — doing so can leave a character 'dangerously unbalanced' if they've already advanced past Iron rank on that essence."
  *Warns:* revocation after investment is a steep penalty and must be telegraphed (VI budget).
  [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How does the class/"Classification" system work]

- **The place vehicle.**
  HWFWM Awakening Stones "manifest in thematically-aligned locations (e.g., 'a dark essence appearing under a gloomy staircase or an awakening stone of the rain appearing during a rainstorm over a pond')." Gods can craft them for followers.
  Beware of Chicken's farm becomes "qi-rich" through cultivation.
  Growth can be tied to *sites* (shrines, wells of power) as well as deeds.
  *→* 08, 10, 13.
  [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How do Awakening Stones work] [R: research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md §Beware of Chicken]

- **Individualized tier text as a rule-governed exception.**
  Lightweavers and Elsecallers "discover more individualized personal truths or aspirations instead of ideals." Two members of the same class get textually different progression.
  The note: "a good systematic-but-not-arbitrary design can have *rule-governed exceptions* as long as the exception itself follows a stated principle."
  Transferable: each calling's tier moments can be (a) fixed oath text or (b) player-authored truths, marked per calling.
  [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §What makes different Radiant orders/characters feel mechanically distinct] [R: reports/LitRPG mechanics for AI DM design.md §Emergent, personal-feeling builds need a hidden variance layer]

**4b. Tier structure (P2)**

- **Stormlight's Ideals are the constitution's named template for P2, and the specific shape transfers.**
  - **5 Ideals** per Order. Ideal 1 is universal; Ideals 2–5 are Order-specific and sequential.
  - Each Ideal increases Stormlight **efficiency** and unlocks new Surge applications.
  - **Universal checkpoints at fixed tiers across every Order:** Shardblade at Ideal 3, Shardplate at Ideal 4. This gives "the same predictable meta-progression shape even though the specific oath content stays personal."
  - Distribution: "**Many Radiants only swear up to the Third Ideal**, as they become increasingly more demanding and exceptional." The Fifth is rare ("the Order of the Skybreakers has not had someone swear the Fifth Ideal for centuries").

  Transferable: a fixed tier count; a universal benefit slot at the same tier for every calling; calling-specific content elsewhere; designed so most characters plateau mid-ladder in a sandbox.
  [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How do Ideals/oaths gate power growth] [R: reports/LitRPG mechanics for AI DM design.md §Stormlight gates power behind sworn oaths]

- **Permanence as the top tier's reward, which maps naturally onto VI's provisional-by-default.**
  "At the Fifth/Final Ideal, the Nahel bond becomes unbreakable except by death (before that point there are 'apparently safe ways to break the bond')."
  Lower tiers are therefore revocable or provisional; the top tier is permanent.
  This is the cleanest in-fiction precedent for "new content provisional by default, promoted to permanent at a boundary point."
  *→* 05, VI.
  [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How do Ideals/oaths gate power growth]

- **Revocation: power as a relationship, not a possession.**
  Breaking oaths weakens the bond until the spren "breaks." The bondmate "loses all Surgebinding ability," and a bonded Shardblade reverts to "an ordinary sword (a 'deadeye'/dead Blade)." This is "undoable only by genuinely recommitting to oaths (extremely difficult), not by any other grind."
  The note: "power in this system is a *revocable, relationship-based* privilege... a strong asymmetry compared to typical RPG XP that only ratchets upward."
  *Tension:* the constitution prefers "atone rather than instantly and irreversibly losing power." Stormlight is harsher but *graduated* (the bond weakens before it breaks). A strain meter with stated thresholds reconciles them.
  *→* 03 (contrary evidence), 07.
  [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How does Surgebinding work mechanically] [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How do Ideals/oaths gate power growth]

- **Mutual macro/micro gating (HWFWM).**
  - Each ability climbs sub-ranks **1–9** within the current Rank, then "cannot progress further until you rank up [the whole character]."
  - Rank-up requires the whole ability set to meet a threshold. Iron: all 4 essence slots bonded. Bronze: "all 20 abilities must be unlocked AND advanced to at least Bronze-0" (contradicted within the source: "not all need be at Bronze level yet").
  - This "keeps a party synchronized in power without an external DM ruling."
  - *Gap:* "the exact quantitative threshold... isn't specified numerically... likely intentionally soft-gated." An AI DM "needs to make this explicit and numeric."

  Transferable: tier N+1 of a calling may require breadth at tier N (e.g. all its slots filled) as well as depth.
  [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How does leveling work] [R: reports/LitRPG mechanics for AI DM design.md §Candidate primitives and patterns]

- **Rank ladders with named steps and biological or narrative markers.**
  - HWFWM: Normal → Iron → Bronze → Silver → Gold → Diamond → Transcendent (**7**). Life expectancy ~60/75/100/200/500 years; Gold "no longer needs to breathe"; Diamond "ageless... many old rules stop applying"; Transcendent is "the level of gods."
  - Cradle: Foundation → Copper → Iron → Jade → Gold (Low/High) → Underlord → Overlord → Archlord → Herald/Sage → Monarch. Iron = superhuman body; Jade = long-range madra sense.

  Each tier has a *fictional marker* the world can notice (supports reputation-based recognition).
  *Warns:* HWFWM later bolted **new top tiers and power sources** on top of the closed frame (Diamond, Half-Transcendent, Transcendent, Great Astral Being, Prime Avatar, Astral Nexus, Numen, System Administrator). Readers name this "where tracking and stakes both degrade." The ladder needs a **hard top**.
  [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How does leveling work] [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §Does the series show power creep] [R: research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md §Cradle]

- **Internal ranks with a breadth threshold before ascension (The Land's Chaos Lord).**
  - **9** internal ranks: Beginning, Low, Improved, Middle, Empowered, High, Major, Great, Grand.
  - ">50% of ranks required before a further Ascendance."
  - A **random Bloodline** is awarded on taking the Evolution (P1-style variance *at a tier event*).
  - *Warns:* the Evolution multiplies per-level currency (15 stat points vs 4 ≈ 3.75×; 30+15 talent points vs 10 ≈ 4.5×). Tier rewards that multiply *rates* compound into runaway.

  [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §How does the class system work] [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §Does the series show power creep]

- **Ordered unlocks inside a calling.**
  "Radiants often learn their 'anti-clockwise' Surge first," and "some orders cannot use one of their Surges until they swear a higher Ideal."
  A calling's capabilities can arrive in a fixed internal order across tiers. This is deterministic and keeps each tier's reveal meaningful.
  [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How does Surgebinding work mechanically] [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How do Ideals/oaths gate power growth]

**4c. Specialists, hybrids, synergy**

- **Hybrid classes derived from combination: HWFWM's confluence.**
  - With 3 chosen essences, "a 4th 'Confluence' essence manifests automatically from that specific combination." It "cannot be chosen directly — reject it and there is no replacement."
  - Combos were lookup-deterministic in Books 1–10 (the Magic Society's records), then became *less* deterministic from Book 11 after a cosmic plot event.
  - The inference: model the class as "(Race template) + (3 chosen Essence tags) + (1 derived Confluence tag)," "a combinatorial tag system rather than a discrete class list."

  This is the closest canon precedent for P5's hybrid: a *derived* identity from a specific combination of evidence branches.
  *Tension:* "reject it and there is no substitute" conflicts with P1/P5's offer semantics.
  [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How does the class/"Classification" system work]

- **Aligned-combination bonus (P6): Twinborn Compounding.**
  - A Twinborn has one Allomantic and one Feruchemical power; the metals "do not have to be the same." **16 × 16 = 256** raw pairings.
  - The **16 matched** pairings (6.25%) unlock Compounding: burning your own charged metalmind releases the stored attribute "**tenfold**," "a categorically new ability that exists in neither parent system alone." Example: iron Compounding yields "an order of magnitude more weight than was originally stored."
  - *Warns:* Miles "Hundred-Lives" got "near infinite amounts of Healing." An unbounded multiplicative loop broke the healing curve. A hybrid synergy must be bounded (P6 "bounded, audited").
  - Stormlight's equivalent: Adhesion + Gravitation = "the Three Lashings" (Basic/Full/Reverse).

  → 05 owns composites.
  [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §What is a Twinborn] [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §What makes different Radiant orders/characters feel mechanically distinct]

- **Breadth vs competence for hybrids.**
  The MAG fix (02) applies at recognition: hybrid recognition should not arrive with *more* day-one power than either specialist.
  Complementary levers:
  - 5e's MAD price (slower primary progression);
  - P15/EVE time-gating;
  - Primal Hunter's cap-for-restriction (a specialist accepts a restriction for a higher ceiling).

  *Warns:* "some players will read [a breadth handicap] as a penalty for choosing breadth."
  [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §Documented power-creep / balance discussion] [R: research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md §How does D&D 5e's "bounded accuracy" work] [R: reports/Mistborn TTRPG AI design patterns.md §An updated, tradeoff-flagged primitive list]

- **Grid vs pair: two philosophies of class shape.**
  - A grid (Allomancy) supports "many independent single-power specialists... plus a rare hybrid superclass."
  - A cyclic pair (Surgebinding) supports "fewer, thematically-paired dual-specialists... with no unbalanced single-power or all-power extremes."
  - Synthesis: "borrow a grid for the 'which powers can this character access' question and an oath/Ideal-style gate for the 'how strong is each accessed power right now' question." Horizontal diversity from the grid, vertical progression from the oath.

  This maps onto P5 (specialist/hybrid recognition = access) plus P2 (tiers = depth).
  [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §How does this compare to Surgebinding's design]

- **No calling should be strictly inferior.**
  HWFWM: "No essence is absolutely inferior or superior... a person with a Duck essence can be stronger than someone with a predator essence like Fox; the system is explicitly designed to avoid a tier list."
  The Alexandrian's **Concept balance** ("all character concepts should be equally viable") "requires limiting either character creation flexibility or gameplay scope."
  PF2e's "no trap options" via exhaustive audit vs 5e's "limit the number of choice points; benchmark each against one reference unit (a feat is worth +2 to an ability score)."
  [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How does the class/"Classification" system work] [R: research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md §Designer blogs/essays] [R: research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md §Is there a recognized concept of "trap options"]

- **Specializations gated by conditions (The Land's Enchanter).**
  Six named specialties: Ambient, Battle, **Essence** ("Must be a Master of a Place of Power"), Macro, Flesh, **Synergist** ("the path to the greatest enchantments... arduous and time-consuming"; weapon+armor sets with the strongest bonuses).
  Sub-specialties inside a calling, each with a *fictional* prerequisite, give branching without new callings.
  Rogue also branches into Assassin / Spy / Counter-Intelligence; Warrior into Death Knight / Berserker.
  [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §How does the class system work] [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §What makes builds feel distinct/personalized]

- **Specialization forks replace rather than add. This is the first confirmed consolidation mechanism (VI).**
  - DCC skills auto-level through use "up to roughly level 10 before requiring a specialization choice."
  - Example: "Explosives Handling" forks into "Dangerous Explosives Handling" or "Goblin Explosives." Specialization trades "raw damage vs. elemental effects vs. reduced mana cost."
  - The fork "retires the generic skill's further growth path."

  The round-2 report: this "proves the retirement mechanism... is achievable without being player-hostile, provided the branch point is designed in from the start."
  [R: research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md §Dungeon Crawler Carl] [R: reports/Mistborn TTRPG AI design patterns.md §What this round changes]

**4d. VI consolidation / retirement precedents (the full set found)**

- **Every precedent in the corpus.**

  | # | Precedent | What it retires |
  |---|---|---|
  | (1) | DCC specialization fork | The generic skill's further growth path |
  | (2) | HWFWM's author removed an early bonus-loot/quest mechanic ~Book 3 "because it would start making [the protagonist] dangerously overpowered," replacing it with a racial-ability trait | A one-off mechanic ("proving mid-series mechanic retirement is possible but was applied only once") |
  | (3) | HWFWM Books 4–6 "tonal shift" and later "stat recap chapters" | *Presentation* only, not mechanics (a squish-like non-retirement) |
  | (4) | Stormlight oath-break / deadeye | Revocation |
  | (5) | MoL loop reset | Raw power resets, knowledge persists. A structural model: when retiring powers, *keep what the player learned* |
  | (6) | Underworld | "One later book reportedly narrowing the protagonist's toolkit back to a single signature ability" (low confidence) |
  | (7) | HWFWM Book 11+ cosmic event | Made confluence non-deterministic: an *in-fiction world event as the boundary point for a rules change* (→ 11) |
  | (8) | The Land | Unspent points auto-assigned after a week (a use-it-or-lose-control valve) |
  | (9) | DCC "Benefits" | "One-off grants that cannot be leveled" — a content category that never grows, so never needs retiring |

  *Every source's failure:* "additive stacking without retirement."
  [R: reports/LitRPG mechanics for AI DM design.md §All four systems break down the same way] [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §Does the series show power creep] [R: research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md §Mother of Learning] [R: research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md §Dungeon Crawler Carl] [R: research_notes/LitRPG mechanics for AI DM design/underworld_level_up_or_die.md §Does the series show power creep] [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How does the class/"Classification" system work]

- **The specific bloat mechanisms to design against.**
  - HWFWM: "Every time they level up it add[s] effects to every power". Ability text is cumulative, so "total described state per ability only grows, never resets." → a rank-up must restate the ability's full current text (replace), not append.
  - The Land: each book's sheet is "a strict superset of the last." Level 8 with ~12 skills (Book 1) became Level 45 with 11 magic schools, ~40 skills/sub-skills, a Profession, a Bloodline and an Evolution, attributes ~3–6× higher (Con 16→79, Int 18→78). Book 7 ran 2,000+ pages vs ~400.
  - Underworld: level 25 start → 57 "within the first hour of the audiobook" → beats a level-200 enemy while under level 100 → "no level limit," enemies "in the thousands and tens of thousands." A reviewer attributes this to the author: "keep[s] changing it so the main character can... be more overpowered."

  [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §Is there indication of how complex/trackable] [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §Does the series show power creep] [R: research_notes/LitRPG mechanics for AI DM design/underworld_level_up_or_die.md §Does the series show power creep]

- **Mitigation that works in the fiction: expand what exists before adding (Stormlight, Law 3).**
  No citable critique of Surgebinding power creep was found. This is weak evidence (a research gap), but the substrate is "a hard ontological ceiling baked into the setting's cosmology rather than a soft convention an author can quietly loosen."
  Put the ceiling *in the world* (a fixed number of Surges or callings), not only in the rules.
  [R: reports/LitRPG mechanics for AI DM design.md §All four systems break down the same way] [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §Does this system show signs of "breaking down"]

**4e. Gated special trait: monster-power absorption (Blue Mage)**

- **Underworld is the only Blue Mage precedent, and it specifies nothing.**
  "Blue Magic... allow[s] you to steal the natural skills of other creatures and mimic their abilities through magic." Elorion "can absorb all the Blue Magic he can find."
  **No source gives the rules**: "automatic on kill, resource-gated, capped in number, or subject to failure," or whether abilities can be lost. It is "the single largest mechanical gap in this dataset."
  So 04 must author all four: trigger, cost, cap, failure.
  Useful structural borrowings:
  - Hemalurgy's *location + method-of-death encodes which power* (→ P5's pool-gate/fill);
  - Hemalurgy's *dual cost* (a quantitative loss on every transfer plus a qualitative "susceptible to external control" vulnerability);
  - HWFWM's 20-slot cap.

  *Rules out:* uncapped absorption.
  *Warns:* the nominal "healer" in Underworld became "healing magic that hurts everything" plus fire, "abandoning the healer role." A reviewer calls it unbalanced because it removed the healer's "group-dependency weakness." A gated trait must not dissolve its own class's weakness.
  [R: research_notes/LitRPG mechanics for AI DM design/underworld_level_up_or_die.md §Is there a distinctive hook] [R: research_notes/LitRPG mechanics for AI DM design/underworld_level_up_or_die.md §How does the class system work] [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §How does Hemalurgy work] [R: reports/LitRPG mechanics for AI DM design.md §Underworld's Blue Mage turns the bestiary]

- **Hemalurgy is a deliberate cross-system "wild card" with its own cost logic.**
  Sanderson built Hemalurgy so it "can interact with every one of the magics," and so it would carry "moral complications" (inspired by Runelords' "stealing people's strength").
  The note's inference: "design the exception-granting mechanic... as its own explicit subsystem with its own cost logic, rather than bolting ad hoc exceptions onto each power system individually."
  So Blue Mage absorption and item-grafting should share one subsystem.
  *→* 08.
  [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §Sanderson's own design commentary] [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §How does Hemalurgy work]

- **A setting-history rarity lever.**
  Twinborn "only began to appear after the Final Ascension, due to the intermingling of the Terris people... with the other citizens." Compounding was "a one-time occurrence during the time of the Lord Ruler."
  Rarity can be encoded as "this combination was not previously possible given the world's social structure." The living world can *unlock* a gated hybrid or trait over campaign time.
  *→* 11.
  [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §What is a Twinborn]

- **Class labels must not over-promise.**
  - Underworld's "healer" didn't heal.
  - The Land's "unique class" premise didn't map to any named mechanic.
  - Primal Hunter's "Vessel" couldn't be confirmed.
  - HWFWM's "Classification/Perks/Feats" are fan terms.

  A recognized calling's name must correspond to its mechanical content, or the AI will embellish from the name (the probe's cold-vulnerability failure, BRIEF §7).
  [R: research_notes/LitRPG mechanics for AI DM design/underworld_level_up_or_die.md §How does the class system work] [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §How does the class system work] [R: research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md §The Primal Hunter] [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How do Perks and Feats work mechanically]

### Chapter 05 — Abilities & Focus (slots & hard cap, templates, passive/active, recharge, Focus, P10/P12, P6)

- **The slot cap has a precedent, and so do category caps within slots.**
  - HWFWM: 4 essences × 5 abilities = **20** cap. **4 unlock free** on bonding (one per essence); **16** require an Awakening Stone. "No duplicate essences" forces combination over stacking.
  - A *category cap* inside the grid: "Essence users can only possess a single aura ability unless another ability [or racial gift] removes or lessens this restriction." Estella Warnock holds four (one per essence) via a special gift.
  - Non-canon CYOA prices for breaking caps: "Four Fold" (200–400 CP) for 4 auras; "Additional Slots" (200 CP) for +1 slot per essence. These show that cap-breaking is itself a priced, rare exception.

  Transferable: a hard total cap, per-category caps (a "one aura" analogue for persistent/area effects), and cap-lifting only via named rare traits.
  [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How do Perks and Feats work mechanically] [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How do Awakening Stones work] [R: reports/LitRPG mechanics for AI DM design.md §He Who Fights With Monsters turns four slots]

- **Ability template taxonomies to borrow as `type` fields.**
  - HWFWM's six categories: Aura, Conjuration, Familiar/Summon/Puppet, Special Ability (incl. Perception), Special Attack, Spell.
  - Cradle's four technique shapes: Striker, Enforcer, Forger, Ruler.
  - MoL's structured spell vs unstructured shaping.
  - DCC's distinction between leveling Skills, non-leveling Benefits, and Stats.

  Use the category as a hook for category caps, P6 behavioral tags, and tag evidence (method axis, → 03).
  [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How do Perks and Feats work mechanically] [R: research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md §Cradle] [R: research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md §Dungeon Crawler Carl]

- **Formal item/ability schema precedent (HWFWM's system-message template).**
  "[Awakening Stone of X] (unranked, [rarity]). An awakening stone containing ___. (consumable, awakening stone). Requirements: Unawakened essence ability. Effect: Awakens an essence ability."
  Fields: name, rank, rarity, description, type tags, **Requirements**, **Effect**.
  Add the constitution's recharge and P12 fields, and this is essentially a `data/abilities.yaml` schema.
  [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How do Awakening Stones work]

- **Rolled fills weighted by existing slots (P5 fill-quality).**
  - Awakening Stones unlock a *latent* ability. Which one is "random in nature, but... influenced by race, essences, what the person knows... and what hasn't been awakened."
  - "Rare stones are more specialized in giving an ability but can still give what a common stone would give."
  - No re-rolling a bad unlock.

  The inference calls this "a controlled-randomness gacha layer bolted onto a deterministic slot structure... roll on a weighted table conditioned on race + existing essences + narrative fictional positioning."
  *Gap:* the weighting formula is "never quantified." The project must author it.
  *→* 08.
  [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How do Awakening Stones work]

- **Ability growth should add new *effects* at tiers, not just bigger numbers, and the ability text must be restated.**
  Hand of the Reaper by rank:
  - Iron: conjure a shadow arm that inflicts [Creeping Death].
  - Bronze: also inflicts [Rigor Mortis]; a second arm.
  - Silver: also [Weakness of the Flesh]; many arms at range.
  - Gold: more arms, further range, arms can hold conjured weapons.

  This is felt growth. But cumulative text is the bloat driver (see 04d).
  *Warns:* HWFWM readers found fights "bogged down by... walls of text explaining stats and abilities."
  [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How do Perks and Feats work mechanically] [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §Is there indication of how complex/trackable]

- **Focus design inputs from Stormlight.**
  1. It is a consumable harvested from infused gems (recharged by highstorms).
  2. It "leaks out of the imperfect human body over time (**faster the more you hold**)," a holding cost above baseline.
  3. A visible glow is a detectable tell.
  4. It produces "an adrenaline-like compulsion toward action," a behavioral side-effect.
  5. Running out "leaves the user 'exhausted and feeling deflated'," a post-depletion condition.
  6. Efficiency improves with each Ideal ("better hold Stormlight").
  7. Squires hold it less efficiently.
  8. Honorblades cost "far more."
  9. Alternate fuels leak differently ("Towerlight... leaks faster").

  Sanderson classifies Stormlight as a **limitation, not a cost**.
  Transferable Focus rules: the pool; decay above a comfort threshold; an exhaustion condition at 0; tier-based efficiency as a *tier reward* (a non-additive growth reward that doesn't bloat the sheet); higher costs for off-identity or borrowed use.
  *→* 07.
  [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How does Surgebinding work mechanically] [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How do Ideals/oaths gate power growth] [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §What are Sanderson's (Three) Laws of Magic]

- **Focus design inputs from Allomancy.**
  - Each metal has its own burn rate (instant up to 40 minutes).
  - **Flare** = more potency for "drastically accelerated consumption."
  - Metal must be *ingested*, and impure or toxic metal harms the user (a physical-world cost).
  - Aluminum "destroys" Allomantic reserves (a weakness: an effect that zeroes the pool).
  - Duralumin amplifies whatever else is burned simultaneously, a combination modifier. (Higher-metal names are low confidence.)

  Transferable: per-ability Focus cost and duration; an optional flare surcharge; a "drain" effect class that zeroes Focus as a rare, telegraphed adversary weakness-exploit.
  [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §How does Allomancy work]

- **Feruchemy is a structurally different cost shape: debt and repayment, conserved.**
  - "Voluntarily *weakens* themselves in some attribute to charge a 'metalmind'... then later *taps*... to retrieve exactly what was put in."
  - "Explicitly zero-sum/conservation-based," labeled in-world as the art of *balance*.
  - Examples: copper stores memories (copperminds); aluminum stores Identity; tapping zinc makes you hungry.
  - Sanderson's origin: insomnia ("Why can't I save my sleep...?").
  - A charged metalmind "is itself a physical asset that... could be stolen, hoarded, or passed along" (keyed vs unkeyed is **unconfirmed**).

  Transferable to P9's single Focus pool as a *second cost shape inside the same pool*: "bank" Focus by accepting a reduced maximum (or a weakened attribute) now, and draw it later.
  *Warns:* it needs "an explicit accounting ledger per stored attribute; easy to make either trivial or punishing if the storage/tap ratio isn't tuned."
  *→* 08 (banked items).
  [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §How does Feruchemy work] [R: reports/Mistborn TTRPG AI design patterns.md §Mistborn's three magic systems] [R: reports/Mistborn TTRPG AI design patterns.md §An updated, tradeoff-flagged primitive list]

- **Recovery channels for resource pools (Cradle madra).**
  Madra is replenished "by cycling madra itself, by drawing in matching 'vital aura' from the environment, or by consuming elixirs."
  That is three channels: **self (rest/meditation), environment (place-matched), consumable**.
  Environment-matching ("pure madra... has no corresponding environmental vital aura") means location can speed recovery for matching identities.
  *→* 07, 10, 08.
  [R: research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md §Cradle]

- **P12 levers catalogued from the sources (limitation / weakness / cost).**
  - *Limitations:*
    - Allomancy push/pull and the mass rule; Stormlight fuel.
    - Stormlight healing bounded by "Cognitive identity" ("if a soldier considers his scars part of his self-identity, Stormlight will not heal them").
    - Fused: a single Surge only.
    - MoL: the fixed element set; structured spells' rigidity.
    - The Land: minimum 50% affinity to learn at all.
    - HWFWM: rank ceiling; one aura.
  - *Weaknesses:*
    - Aluminum nullifies Shardblade sharpness and wipes Allomantic reserves.
    - Shardblade countermeasures: another Blade, Plate, "half-shards," a fully charged metalmind or heavily Invested object/person, aluminum.
    - Copper/bronze detectability.
    - Hemalurgic susceptibility to external control.
    - Jason's kit "flounders against fast, weak swarms."
  - *Costs:*
    - Feruchemy's pre-paid weakness; zinc hunger; metal toxicity.
    - Hemalurgy's power loss plus murder.
    - Honorblades' Stormlight surcharge; Wheel of Time insanity.
    - The Primal Hunter restriction for a higher cap; 5e MAD slower progression.

  *Rule-writing implication:* each ability's data entry gets three separate fields.
  [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How does Surgebinding work mechanically] [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How do Shardblades and Shardplate fit] [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §How does Hemalurgy work] [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §How does Feruchemy work] [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §What makes two characters' builds feel meaningfully distinct]

- **P10 / PbtA moves: narrow verbs with fixed triggers.**
  Each playbook has a "small, hand-authored list of named 'moves,' each with a fully pre-specified trigger" and resolution. "You don't choose from a big list: you choose a concept, and then select options from that concept."
  This is "a low-ambiguity fallback pattern for flavor-driven or narrative abilities." (Constitution P10 already extends it to core power when precisely scoped.)
  *Warns:* "small total build space per playbook; doesn't scale to 'endless' customization on its own."
  [R: research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md §How do "Powered by the Apocalypse" (PbtA) games] [R: reports/Mistborn TTRPG AI design patterns.md §An updated, tradeoff-flagged primitive list]

- **A power-budget benchmark is needed.**
  - 5e (Mearls): options were "power balanced against a clear benchmark (a feat is worth +2 to an ability score)." Benchmarking against one flat unit produced feats that are strictly worse than an ASI in most builds.
  - PF2e: exhaustive audit against a shared math budget ("fiddly math-iness to ensure no build is better than any other build by too much of a margin," e.g. two-weapon feats gated to different classes). The cost: "bonuses feel less impactful."
  - The note: for "procedurally generated or player-authored options," an explicit, checkable power-budget formula scales better than curated benchmarking.

  This is directly relevant to P5 loot fills and Blue Mage abilities, which are generated.
  [R: research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md §Is there a recognized concept of "trap options"] [R: research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md §How do Pathfinder 2e's three-action economy]

- **Named composites (P6): Three Lashings and Compounding.** See 04c.
  P6's behavioral-tag companion has *indirect* support here: HWFWM's stacking statuses each needed a different stacking rule, which argues for a closed vocabulary of stacking behaviors. Candidates: "stacks, no scaling"; "stacks, scales"; "stacks, decays over time"; "threshold-cleared (Bleeding: removed only after enough healing is absorbed)"; "cannot be cleansed."
  [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §What makes two characters' builds feel meaningfully distinct] [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §Is there indication of how complex/trackable]

- **Synergy planning is an intended player-facing tactic.**
  "It's generally better to wait to unlock abilities until after you've got your full set of essences so that you can develop good synergies."
  The inference: "the real 'perk economy' in HWFWM is Awakening Stone allocation timing + essence choice order."
  → 14: explain that deferring a fill can improve it (if 05/08 make the weighting depend on existing slots).
  [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How do Perks and Feats work mechanically]

- **Temporary boosts and gear affinity.**
  DCC Skill Tonics (temporary skill boosts) and gear bonuses to *specific named skills* (Toe Ring +3 to Powerful Strike).
  Items can target a specific ability rather than a generic stat. This is safer against arbitrage (GURPS) because it scales one thing.
  *→* 08.
  [R: research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md §Dungeon Crawler Carl]

- **Mandatory universal counters (MoL Negation).**
  Negation (dispelling/disrupting other spells) is "considered mandatory for every mage." A universal defensive verb every practitioner has is a candidate *basic action* (VII's always-available tier) for magic-using characters, or a universal Focus-spend.
  [R: research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md §Mother of Learning]

### Chapter 06 — Conflict (action economy, turn order, positioning, attacks, damage, defense, conditions, reactions, morale, escape)

- **The fixed action economy (P9): PF2e's 3 actions + 1 reaction.**
  Stride 1, Strike 1, Raise a Shield 1, most spells 2, open a door 1.
  "Positioning matters, conditions matter, teamwork matters, a +1 bonus matters." The choice among attack again, raise a shield, move, demoralize, trip, recall knowledge or cast "can matter a lot."
  *Warns:* "some builds will feel mechanically homogeneous at the turn-structure level."
  [R: research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md §How do Pathfinder 2e's three-action economy] [R: reports/Mistborn TTRPG AI design patterns.md §TTRPG balance theory supplies]

- **Many weak foes are real threats. Single-number difficulty ratings fail.**
  - 5e CR: "Four characters at the fifth level sometimes can easily beat a monster of CR 9 or even 10, yet die because of several creatures of CR 1," attributed to ignoring action economy and monster count.
  - "There's no Encounter Size Multiplier table for PCs"; summons and allies break it; "after level 3... the discrepancy... gets worse and worse."
  - Remedy in the discourse: combine XP budgets *with* CR. The note's inference: prefer "a simulated or multi-axis check... (e.g., simulated action economy, expected damage-per-round math)."
  - Bounded accuracy keeps hordes credible.

  For a single PC, action-economy asymmetry (1 vs N) is *the* dominant variable.
  *→* 09.
  [R: research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md §What is "encounter balance math"] [R: research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md §How does D&D 5e's "bounded accuracy" work]

- **Builds must have structural weaknesses, and encounters should test them.**
  Jason's affliction kit "dominate[s] tough foes... but flounder[s] against fast, weak swarms," "a real asymmetric build trade-off, not a flat power difference."
  The Alexandrian: diversify challenges rather than escalate. Opponents come in shapes (single tough, swarm, fast, ranged, social) that stress different builds.
  *→* 09, 12.
  [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §What makes two characters' builds feel meaningfully distinct] [R: research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md §Designer blogs/essays]

- **Condition archetypes from HWFWM's afflictions (templates for `data/conditions.yaml`).**
  - **Bleeding:** absorbs healing; removed only after enough healing is absorbed; cannot be cleansed.
  - **Rigor Mortis:** stacking Speed/Recovery debuff that also deals damage as it stacks.
  - **Sin:** stacking increase to necrotic damage taken.
  - **Penance / Wages of Sin:** stacking damage-over-time.
  - **Penance:** drops off over time.
  - **Blood of the Immortal:** stacking but does not grow stronger.
  - **Blood Frenzy:** stacking self-buff to Speed and Recovery up to a threshold cap.
  - **Strength of My Enemies:** stacking self-buff to Power and Spirit up to a cap.
  - **Verdict:** an execute that scales with the target's existing affliction/injury state.

  Recovery (the attribute) shortens affliction duration.
  *Warns:* ~35 such statuses for one character is the tracking-burden case. Close the vocabulary and give every entry stack/decay/cleanse/interaction fields.
  [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §What makes two characters' builds feel meaningfully distinct] [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How do core Attributes work] [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §Is there indication of how complex/trackable]

- **Positioning as relationship, and physics-based forced movement.**
  - Allomancy's push/pull resolves by relative mass: "pushing on a much heavier anchor... instead sends the *user* flying."
  - HWFWM Power's "meta-weight": "the less one is thrown around by those of the same or lower ranks."

  Forced-movement contests are adjudicable by a single comparison of (mass or tier) rather than case rulings.
  *→* 01.
  [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §How does Allomancy work] [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How do core Attributes work]

- **Damage and armor precedents (Shards).**
  - Shardblades cut non-living matter "as if passing through water." Against the living they "cut the being's soul": death is **delayed** unless the strike hits the head or spine (instant, "cauterizing black smoke from the eyes"). Limbs are deadened rather than severed.
  - Shardplate: "**two hits typically shatters a plate section**." This is locational armor degradation with a small integer.
  - Shards summon and dismiss at will and "cannot be summoned inside a solid object."

  *→* 07 (delayed death = dying state), 08.
  [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How do Shardblades and Shardplate fit]

- **Group morale and fighting spirit as multipliers (The Land).**
  - Fighting Spirit: −5 "Broken Spirit" = −50% damage up to +5 "Blood Lust" = +50%.
  - Morale multiplies Population Growth, Productivity *and* Fighting Spirit together, from "Rebellion" (−100% to all three) to "Party Every Night" (+100%).
  - War Leader ranks with war-point quotas per battle (Battle Captain 2,500 WP/battle).

  A morale track for NPC groups (break/rout thresholds) can reuse the 00 scale type.
  *→* 09, 11.
  [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §Crafting, settlement-building, and other non-combat progression]

- **Tier gaps in combat.**
  - Cradle's ~10× per rank.
  - HWFWM Silver: lower-rank killing blows no longer seriously harm.
  - Underworld: beating a level-200 enemy while under 100 was called "severely unbalanced."

  The gap-to-outcome function must be explicit, with telegraphing when the PC faces an out-of-band foe (→ 07, 09).
  [R: research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md §Cradle] [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How does leveling work] [R: research_notes/LitRPG mechanics for AI DM design/underworld_level_up_or_die.md §How does leveling and skill acquisition work]

- **Unbounded physical enhancement dominates combat.**
  Pewter (strength/speed/balance/endurance/healing) is described as "almost too overwhelming... completely breaking the rules of combat and survival" (listicle-sourced).
  Self-buffs to physical stats need caps (the stacking-to-a-cap pattern above) and durations.
  [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §Documented power-creep / balance discussion]

- **Emotional influence as push/pull (a combat-social bridge).**
  Zinc "riots"/inflames emotions; Brass "soothes/dampens" them.
  A two-direction emotion-shift verb is a clean template for morale attacks (demoralize/rally) and for social influence (→ 10).
  [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §How does Allomancy work]

- **Reactions and defense.**
  PF2e's single reaction; "Raise a Shield" costs an action. Shard countermeasures define which defenses can stop an exceptional attack (a weapon or effect can carry a "can only be stopped by…" list).
  [R: research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md §How do Pathfinder 2e's three-action economy] [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How do Shardblades and Shardplate fit]

- **Live combat narration must not become stat recitation.**
  HWFWM fights got "bogged down by... walls of text explaining stats and abilities... in the middle of battle." Audiobook listeners "lose track of fights."
  → 12: narrate consequences, keep numbers in tools and the codex.
  [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §Is there indication of how complex/trackable]

### Chapter 07 — Harm, recovery, death (injury, Vitality consequences, rest, telegraphed death, defeat outcomes)

- **Delayed death is a ready-made dying state.**
  A Shardblade wound through the body is not instantly fatal (the soul is cut). It can be healed by a Radiant's Stormlight, which "creates new soul-tissue, leaves a scar," or by Progression's "Regrowth." It "doesn't work on head/spine kills."
  Transferable: a lethal-severity wound opens a dying window during which specific, named interventions (not generic healing) can save the character. Only an explicitly telegraphed "head/spine"-class blow is instantly fatal, and under the lethality lock it must be warned about in advance.
  [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How do Shardblades and Shardplate fit]

- **Identity-bounded healing: scars a character accepts as self don't heal.**
  "If a soldier considers his scars part of his self-identity, Stormlight will not heal them," "an explicit rule tying the power's limits to belief/identity."
  Transferable: lasting injuries can become *identity traits* by player choice. A permanent wound converts into a tag or trait (evidence toward a calling; → 03/04) rather than pure loss. It gives defeat a growth path.
  [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How does Surgebinding work mechanically] [R: reports/LitRPG mechanics for AI DM design.md §Stormlight gates power behind sworn oaths]

- **Post-depletion exhaustion.**
  Running out of Stormlight leaves the user "exhausted and feeling deflated." Feruchemy's tap is paid "at the cost of a period of weakness" (store phase).
  Two templates: (a) hitting 0 Focus imposes an exhaustion condition; (b) voluntary pre-paid weakness.
  *→* 05.
  [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How does Surgebinding work mechanically] [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §How does Feruchemy work]

- **Recovery as an attribute lane and three recovery channels.**
  HWFWM's Recovery attribute governs "how fast one can recover mana, stamina, and health" *and* "how long most afflictions will be in effect." Leonids have better stamina recovery.
  Cradle's madra channels: self-cycling, environmental aura, elixirs.
  Rest rules can key off one attribute for both rate and condition duration.
  [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How do core Attributes work] [R: research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md §Cradle]

- **Healing-resistant wounds.**
  Bleeding "absorbs healing, removed only after enough healing is absorbed, cannot be cleansed." This is a template for grievous wounds that demand sustained care (time, a healer, a place) rather than one spell.
  *→* 06.
  [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §What makes two characters' builds feel meaningfully distinct]

- **Telegraph risk with explicit odds.**
  The Chaos Lord evolution was offered with "a 99.9999% success rate." The fiction *told* the character the odds.
  This is a precedent for the lethality lock's "explicit warnings before lethal risk": state the risk band, or even a number, before the choice.
  [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §How does the class system work]

- **Extra lives exist as rare rewards.**
  "Three extra Respawns" was one of the three Choice options. A last-chance resource ("fate," "a debt owed by death") exists in the genre as a *chosen reward*, not a default.
  *→* 04.
  [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §What makes builds feel distinct/personalized]

- **Trauma as a growth trigger.**
  HWFWM racial gifts "evolve... usually from traumatic events." Chaos Lord was offered after surviving the Sea of Chaos.
  Near-death and defeat can be *evidence events* (→ 03) and crystallization moments (→ 04), so "defeat usually means a changed situation" can include a changed self.
  [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How do Perks and Feats work mechanically] [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §How does the class system work]

- **Tier-scaled lethality.**
  HWFWM: "a killing blow from a Normal/Iron/Bronze attacker no longer seriously harms a Silver-ranker." Life expectancy scales with rank.
  Deaths and injuries from out-of-band sources can be ruled out mechanically (a consistency anchor); deaths from in-band or higher sources are what must be telegraphed.
  *→* 09.
  [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How does leveling work]

- **Loss of power as a defeat outcome.**
  - Oath-break deadening.
  - Divine reclamation ("dangerously unbalanced").
  - Hemalurgic spikes leaving a "damaged spirit web" susceptible to control (kandra, koloss).

  Defeat can cost *capability* or *autonomy*, not just Vitality: a captured character could be "spiked"/marked. Any such outcome needs telegraphing and a recovery route (the recommitment precedent).
  [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How does Surgebinding work mechanically] [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §How does Hemalurgy work] [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How does the class/"Classification" system work]

- **Critical-failure exposure at default modifiers.**
  (R2 analysis; see 01) At +2, DC 20 carries a 40% critical-failure chance and DC 25 a 65% chance. 07's harm-on-critical-failure rules must be calibrated to that, or the DC 20+ band becomes the main source of untelegraphed injury.
  [R: research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md §How do Pathfinder 2e's three-action economy]

### Chapter 08 — Items, loot, crafting (pool gate / fill quality, properties, crafting, wealth, economy)

- **Loot pools gated by circumstance and place (HWFWM Awakening Stones and essences).**
  - Stones and essences arise from "the same natural process that produces essences and Monsters."
  - They manifest thematically: a dark essence under a gloomy staircase; a rain stone "during a rainstorm over a pond."
  - Gods and Astral Beings can craft them for followers.

  This is P5's pool-gating circumstance extended from "what you defeated" to *where and when you searched*. A location's nature gates the eligible drop pool.
  *→* 13 (seed the starter region with themed sites), 10.
  [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How do Awakening Stones work]

- **Rarity specializes the result rather than raising raw power.**
  - "Rare stones are more specialized in giving an ability but can still give what a common stone would give as well."
  - The Legendary "Awakening Stone of the Celestials" was used only **3** times in the story, each time by a Celestine. Each user gained an ability enhancing an existing racial gift: rarer items *synergize with who you are*.
  - HWFWM's design stance that "no essence is absolutely inferior."

  Together these argue for rarity = narrower, better-targeted fill (fill-quality axis), not a bigger number.
  [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How do Awakening Stones work] [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How does the class/"Classification" system work]

- **Crafting quality has two axes. The Land's alchemy is a direct fit for pool-gate / fill-quality.**
  - Potency *type* ladder (8): Brew → Tincture → Solution → Infusion → Elixir → Philter → Draught → Essence.
  - Separate *strength* ladder (7): Tainted → Clouded → Weak → Basic → Enhanced → Strengthened → Processed.
  - Building Quality (7): Slum → Poor → Average → Above Average → Well Built → Exquisitely Built → CORE.
  - Crafting is "folded into the Profession/skill system... rather than a separate meta-system."

  Mapping: the ingredients' nature gates *which* product family and type-tier are reachable (pool gate); the crafter's execution sets strength (fill quality). Constitution P5 already says crafting should reuse this shape.
  *Gap:* "no percentage effects given" for most of these tiers.
  [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §Crafting, settlement-building, and other non-combat progression]

- **Item property schema, and the exposition warning.**
  - The Land's loot readout: "steel short sword. Base damage 8-11. Max Damage 10-13. Durability 9 of 11. Frequency: common. Quality: Average." That gives the fields damage range, max, durability current/max, frequency (rarity) and quality.
  - GeekDad: loot readouts ran "five, or even 10 minutes... over, and over, and over again."
  - The modern corrective: "major loot" only in narration.

  Item stats live in data and codex. Narration names the item and what matters now.
  *→* 12, 14.
  [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §How complex would this system be] [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §Does the series show power creep]

- **Items that confer capability, not just numbers (Honorblades and dead Shardblades).**
  - Honorblades grant their two Surges to **anyone**, "without regard for oaths." They "consume far more Stormlight" and grant none of the bond's extras. They can also activate Oathgates.
  - "Dead" Shardblades from the Recreance are usable by anyone and have no Surges.

  Transferable (goal 1): a relic can *license* an off-identity capability (VII item-conferred license) at a **higher Focus cost** and without tier growth. This lets players try ideas outside their calling without eroding what callings mean.
  Also a precedent for NPC villains who "cheated into power without the vow-gated growth path" (→ 09).
  [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How do Shardblades and Shardplate fit] [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How does Surgebinding work mechanically]

- **Banked power as loot (Feruchemical metalminds).**
  A charged metalmind "is itself a physical asset that... could be stolen, hoarded, or passed along — a distinct 'banked power as loot' design lever."
  Transferable: charged items that hold stored Focus or a stored benefit, whether the owner charged them or they were looted.
  *Unconfirmed:* the keyed/unkeyed rule (who can tap). The project must decide it.
  [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §How does Feruchemy work]

- **Grafting items (Hemalurgic spikes).**
  - Where the spike goes and how the donor died "together encode which power is granted." This is "a designed solution to a combinatorial-explosion problem."
  - The transfer is lossy in two ways: loss at creation, and decay while the spike is out of the body. The decay "can reportedly be engineered away."
  - The recipient becomes susceptible to external control.
  - No sourced % loss exists. Do **not** attribute a number to Sanderson; "some meaningful, undisclosed fraction is always lost" is the transferable principle.

  This is the item form of the Blue Mage trait (→ 04e).
  [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §How does Hemalurgy work] [R: reports/Mistborn TTRPG AI design patterns.md §Mistborn's three magic systems]

- **Items that advance you, but with a ceiling.**
  HWFWM monster cores are a "cheap, self-limiting" path that caps most users below Diamond. Crafters/artificers are the exception: they can reach Diamond "through pure crafting application."
  If consumables can feed tag evidence or tier progress, they must saturate. That keeps the "honest path" (deeds) primary.
  *→* 03.
  [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How does leveling work] [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How do core Attributes work]

- **An item budget is structurally required (the Alexandrian's Iron Man Principle).**
  "As long as: (A) There are magic items which are useful... (B) The PCs can have those items; and (C) The designers care about game balance at all; then (D) There will need to be guidelines for how many items the PCs should have."
  Generalized: every build-affecting resource category "needs its own explicit budget rule from day one."
  → 08 must state item-slot or attunement limits and acquisition rates.
  [R: research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md §Designer blogs/essays]

- **Set and synergy items.**
  The Land's Enchanter "Synergist" makes "weapon and armor sets with the strongest bonuses," via "an arduous and time-consuming path." Set bonuses are a P6 composite applied to gear, gated by crafting investment.
  [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §How does the class system work]

- **Skill-targeted gear and temporary tonics.** DCC: gear adds to one specific skill; tonics give temporary boosts (see 05).
  [R: research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md §Dungeon Crawler Carl]

- **Consumable quality as risk.** Allomancy's ingested metals carry purity and toxicity risk. Low-quality consumables can carry a side-cost, which gives a quality axis for potions and fuels.
  [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §How does Allomancy work]

- **Resource conversion.** The Land's companion Alma spends **10 Psi Points** per **+1** base attribute. This is a precedent (and a warning) for conversion rates between currencies. Any conversion must be priced against the envelope (GURPS arbitrage).
  [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §How do core stats/attributes work]

- **Magic that bypasses the economy.** 5e casters make martials "optional" at high level, and *Fabricate* lets them "bypass the gold economy." Crafting and magic must not trivially mint wealth, or the economy collapses.
  [R: research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md §How does D&D 5e's "bounded accuracy" work]

- **Mechanics may be retired for over-generating loot.** HWFWM's early "bonus-loot/quest" system was removed around Book 3 "because it would start making [the protagonist] dangerously overpowered." 08's reward rates should be the first place a VI revisit trigger is attached.
  [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §Does the series show power creep]

- **Countermaterials.** Aluminum nullifies a Shardblade's supernatural sharpness and is "rare, Soulcast-only." "Half-shards" are engineered counters. A world material that counters a power class supports P12 weaknesses and economic value.
  [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How do Shardblades and Shardplate fit]

### Chapter 09 — Adversaries (archetypes = pool gates, threat bands without levels, templates, behaviors)

- **Threat bands without character levels: Cradle's 10× rule is the anchor.**
  - Rank ladder: Foundation → Copper → Iron → Jade → Gold → Underlord → Overlord → Archlord → Herald/Sage → Monarch.
  - "It takes ten Coppers to challenge an Iron, and ten Irons to challenge a Jade."
  - "An adjudicator... mostly needs to track *rank*... at the cost of coarser resolution."
  - Cradle deliberately commits to no dice math, so "an AI GM adapting this would need to invent the actual resolution math."

  09 must supply the band → d20-modifier / Vitality / action-count mapping.
  Because P2 removes character level, 09 also needs a *derived* PC band (from tier state) to compare against.
  [R: research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md §Cradle] [R: reports/Mistborn TTRPG AI design patterns.md §Five more progression-fantasy series]

- **Single-scalar difficulty fails. Budget with multiple axes.** CR ignores action economy, count, allies and summons (see 06). 09's threat budget should count at least (band, number of actors, actions per round, and special capabilities) separately.
  [R: research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md §What is "encounter balance math"] [R: reports/Mistborn TTRPG AI design patterns.md §TTRPG balance theory supplies]

- **Bounded accuracy lets low-band hordes stay relevant and removes the need for a "minion" category.** With a stated modifier cap, a mob of weak foes remains a threat. 4e's minion category became unnecessary.
  [R: research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md §How does D&D 5e's "bounded accuracy" work]

- **Adversaries use a reduced version of the player grammar (the Fused).** The Fused have **9** "brands" (Adhesion is excluded), each granting a **single** Surge instead of a pair, fueled by Voidlight. Enemy power systems can reuse the PC primitive set in a cut-down or recolored form (Law 3, streamlining), which keeps adjudication familiar.
  [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How does Surgebinding work mechanically]

- **Cheap, legible NPC power types from a grid (Mistings).** A grid "naturally supports *many independent single-power specialists*... dead simple: one verb, one resource." It is "good for a game that wants lots of cheap, legible NPC power-types and a small number of exceptional PCs/villains." NPCs can be one-primitive templates.
  [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §How does this compare to Surgebinding's design]

- **Villains who took the shortcut.** Honorblade wielders and Hemalurgic or blessed beings gain power without oaths, but with strings attached: higher cost, susceptibility to control, danger ("direct blessing... immensely dangerous, leading to that world's destruction"). "A useful asymmetry for an AI DM wanting NPC villains who have 'cheated' into power." These adversaries' weaknesses come from their acquisition route. That is exploitable, and it is a P12 weakness the PC can discover (→ P17).
  [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How do Shardblades and Shardplate fit] [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How does Surgebinding work mechanically]

- **Controllable creature classes.** Kandra and koloss, being Hemalurgically enhanced, "can be externally controlled by Investiture poured into their 'damaged spirit web.'" An adversary archetype with a *control vulnerability* gives a non-lethal resolution path (goal 1: talk, dominate, free them).
  [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §How does Hemalurgy work]

- **An adversary's nature gates the loot / ability pool (P5).** HWFWM monsters are produced by the same natural process as essences and stones. An archetype's nature = its pool gate. This is already constitutional; the sources confirm the fictional coherence.
  [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How do Awakening Stones work]

- **Design encounters to stress builds, not to out-escalate them.** Alexandrian: GM escalation against optimized characters drives an arms race. Instead, (1) diversify and (2) focus on consequences. The alternative in "Fetishizing Balance": adjust to observed party power rather than treating guidelines as law.
  For an AI DM this means: threat choice should key off the PC's *weaknesses and untested tags* (Jason vs swarms), not off an ever-rising number.
  [R: research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md §Designer blogs/essays]

- **Out-of-band threats must be telegraphed and adjudicated by rule.** Underworld's "level 200 enemy while still under level 100" in Book 1 read as "severely unbalanced," and later "enemies in the thousands and tens of thousands" read as spectacle without stakes. Two rules follow: a PC shouldn't routinely beat far-out-of-band foes, and an out-of-band foe should be recognizable in the fiction before engagement (→ 07 telegraphing).
  [R: research_notes/LitRPG mechanics for AI DM design/underworld_level_up_or_die.md §Does the series show power creep]

- **Foreshadow deciding powers (First Law applied to enemies).** An NPC power the player "doesn't understand" that decides a fight risks reading as a deus ex machina. Adversary templates should mark signature powers as "reveal before decisive use."
  [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §What are Sanderson's (Three) Laws of Magic]

- **Detection and concealment arms race.** Bronze (Seekers) detects Allomantic pulses; Copper hides them. Adversaries can carry detection/counter-detection tags that interact deterministically with PC stealth and magic use.
  [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §How does Allomancy work]

### Chapter 10 — Exploration, social, downtime

- **Training takes time, and downtime must compress it.** MoL's five prerequisite skills take ~2–4 years and "cannot be shortcut." Complex unstructured effects take "years/decades." Structured spells take weeks. The note says the system "would need explicit compression rules (skipped/abstracted training time) to run at tabletop session pace." Downtime needs time-cost tables per activity.
  [R: research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md §Mother of Learning]

- **Trials and examinations as downtime.** The Land's Trial: "one week of time passes." Recognition rites can be downtime activities with a set duration (→ 04).
  [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §How does the class system work]

- **Meditation and reflection as a growth activity.** HWFWM attributes rise via "post-battle meditation" as well as danger and training. A post-conflict reflection downtime could be where evidence consolidates, i.e. where recognition moments are checked (→ 03/04).
  [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How do core Attributes work]

- **Social influence as bidirectional emotion shift.** Zinc inflames and Brass soothes emotions: a clean two-verb social template (incite / calm).
  [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §How does Allomancy work]

- **Investigation analogues.** Tin (enhanced senses), Bronze (detect magic use), Copper (conceal it), Feruchemical copper (stored memories as a retrievable archive), Truthwatcher foresight, Elsecallers' affinity with the otherworld (Shadesmar). These anchor perception and information abilities and their P17 reveal degrees.
  [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §How does Allomancy work] [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §How does Feruchemy work] [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §What makes different Radiant orders/characters feel mechanically distinct]

- **Travel and range as a mechanic.** Squire power fails beyond 30–50 miles from the mentor. Distance from a patron, order or place can switch capabilities off, which is a deterministic travel consequence.
  [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How do Ideals/oaths gate power growth]

- **Place-based cultivation and home improvement (Beware of Chicken).**
  - Cultivation redirected to "farming yields, animal companion development, and philosophical growth."
  - The farm (Fa Ram) "has itself become a qi-rich location through the protagonist's cultivation."
  - A rooster develops its own path.

  Downtime can improve a *place* that then feeds recovery and evidence (Cradle's vital-aura matching). Companions can grow too.
  *Warns:* BoC keeps mechanics off-page, which works only by "offload[ing] almost all resolution to GM/author narrative judgment." Downtime still needs rules.
  [R: research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md §Beware of Chicken]

- **Settlement or base as a progression ladder.** The Land runs Loyalty, Morale, Fighting Spirit, Crime (no numbers), Building Quality and settlement "Powers." The settlement grants its Master spells (Summon Mist Worker, Concealing Mist, Confusing Mist, Mist Lights, Dungeon Transport, Curse Removal) "independent of personal Magic skill levels." A holding can be a license source (VII: an established fact grants a capability). It is also a sandbox downtime pillar and a legacy asset (→ 11).
  [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §Crafting, settlement-building, and other non-combat progression] [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §What makes builds feel distinct/personalized]

- **Multi-domain challenge frequency (diversification).** Exploration and social scenes are the Alexandrian's anti-optimization lever. They also produce the non-combat evidence the tag tree needs.
  [R: research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md §Designer blogs/essays]

- **Institutions to interact with.** Adventure Society (quests, restrictions, bounties) and Magic Society (records, scholarship). These give social and investigation targets tied directly to recognition (→ 04, 11).
  [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How does the class/"Classification" system work]

### Chapter 11 — Living world (factions, clocks, hooks, rumors, consequences, generation, retirement & legacy)

- **Faction and settlement stat template.** The Land's scales are directly reusable as faction attributes:
  - **Loyalty −7..+7** with thresholds and productivity effects: Cautious (−1, ≤−250) −20%; Eager (+1, ≥250) +10%; Enthusiastic (+2, ≥500) +20%; Reliable (+3, ≥1,000) +40%; Trusting (+4, ≥2,500) +70%.
  - **Morale** bands: Rebellion −100% → Unhappy (−250) → Neutral → Happy (+250) → Delighted → Elated → Joyous → Ecstatic → Blissful → "Party Every Night" +100%.
  - **Fighting Spirit ±5 → ±50% damage.**

  The report: "the 'tiered scale, numeric thresholds, % effects' template generalizes cleanly from character to faction."
  [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §Crafting, settlement-building, and other non-combat progression] [R: reports/LitRPG mechanics for AI DM design.md §The Land stacks three parallel progression ladders]

- **Quest chains unlock holdings' powers.** The Land's "Unlock Your Power I–III" completes dungeon objectives to unlock Masteries (Air, Life, Dark, Water). Rewards were big: 5,000 EXP per Mastery; 50,000 base EXP for the lich Singh; a secret +500 Morale/+500 Loyalty. That gives factions and holdings their own progression tracks, driven by hooks.
  [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §Crafting, settlement-building, and other non-combat progression]

- **Extrapolation: magic reshapes society.** Law 3's first sub-principle: "work out the full social/political/economic consequences of the magic on the world." For example, the Adventure Society restricts callings; the Magic Society records combinations; gem economies are recharged by highstorms. The living world should derive institutions from the ruleset's own powers.
  [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §What are Sanderson's (Three) Laws of Magic] [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How does the class/"Classification" system work]

- **Reputation consequences of identity.** Restricted essences mean a bounty or kill-contract. Some recognized callings (necromantic, predatory) must trigger faction reactions: a consequence-propagation rule keyed to calling tags.
  [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How does the class/"Classification" system work]

- **Orders that seek you out.** Spren and orders seek candidates with the right demonstrated attributes. Squire candidacy requires a matching mental state. Factions can have **recruitment triggers** keyed to tag thresholds. This is the living-world half of 04's recognition vehicles.
  [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §What makes different Radiant orders/characters feel mechanically distinct] [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How does Surgebinding work mechanically]

- **World events as rules boundary points (a VI tool).**
  - HWFWM: a cosmic plot event ("restoration of the Cosmic Throne") made confluences non-deterministic from Book 11.
  - Twinborn and Compounding exist only after a historical change (the populations mixed).

  The living world can host the *telegraphed boundary points* the constitution wants for bundling retirements. Example: a world-shaking event announces that some content is being re-banded. It can also stagger when rare combinations become available.
  *Warns:* HWFWM's change was plot-driven and unannounced, not telegraphed.
  [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How does the class/"Classification" system work] [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §What is a Twinborn]

- **Periodic world resource cycles.** Highstorms recharge Stormlight gems. A recurring world event that recharges a resource is a clock that couples economy, travel and ability use.
  [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How does Surgebinding work mechanically]

- **Streamlining for sandbox generation.** Show "existing magic used differently by a new culture" rather than inventing new systems. Generated regions and factions should reinterpret the closed primitive set so the rules surface doesn't grow (V, VI).
  [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §What are Sanderson's (Three) Laws of Magic]

- **Legacy precedents.**
  - Heredity: Allomancy is genetic, so an heir can inherit a birth trait.
  - Knowledge persistence (MoL): what was learned carries over when power resets. A successor could inherit the predecessor's *known facts and techniques ledger*, not their power.
  - Holdings persist (The Land's settlement).
  - Orders persist across centuries (Skybreakers without a Fifth Ideal "for centuries").
  - Squires as protégés: a retiring character's protégé starts with a mentor-derived floor.

  These are candidate mechanics for the retirement/legacy procedure.
  [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §How does Allomancy work] [R: research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md §Mother of Learning] [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How do Ideals/oaths gate power growth]

- **Consequence-driven play over escalation.** "Spend less time trying to one-up your players and more time thinking about the interesting stories that result from the consequences of success." The world engine's job is consequence propagation, not difficulty scaling.
  [R: research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md §Designer blogs/essays]

- **Durable memory for a long-running world.** AI Dungeon's forgetting (names, threads, relationships) is the failure mode of an indefinite sandbox. Smallville's emergent social behavior came from per-agent memory, reflection and planning. NPCs and factions need persisted state and goals, not narrative recall. The FictionRAG three-lane split applies.
  [R: research_notes/Mistborn TTRPG AI design patterns/ai_game_integration.md §What is AI Dungeon] [R: research_notes/Mistborn TTRPG AI design patterns/ai_game_integration.md §What academic research exists on LLM agents] [R: research_notes/Mistborn TTRPG AI design patterns/ai_game_integration.md §What patterns exist for preventing an LLM from overriding rules]

### Chapter 12 — DM procedures (turn loop, pacing/P16, reveal/P17, NPC play, improvising from substrate, sessions)

- **Division of labor: code owns outcomes, narration owns flavor.**
  - Thirteen Hours: narration "cannot alter these except by calling the function."
  - Hobbyist convergence: "Code handles dice rolls, HP tracking, spell logic; LLM handles NPC dialogue, narrative flavor, creative choices."
  - The named cheat: declaring "a player rolled a 47 on a twenty-sided die."

  In the turn loop: gate (VII) → roll (tool) → state write (tool) → narrate from recorded state.
  [R: research_notes/Mistborn TTRPG AI design patterns/ai_game_integration.md §What other notable "AI Dungeon Master" projects exist] [R: research_notes/Mistborn TTRPG AI design patterns/ai_game_integration.md §What patterns exist for preventing an LLM from overriding rules]

- **Reconcile state every turn: tool use alone leaves drift.** 46.1% state-prediction exact match even with functions. "Budget for a reconciliation step." The project's probe confirms the failure: narration states unrecorded changes and embellishes ability text (BRIEF §7; constitution P13).
  A turn-end check ("did anything I narrated change state that no tool recorded?") is the rules-level expression of this.
  [R: research_notes/Mistborn TTRPG AI design patterns/ai_game_integration.md §What other notable "AI Dungeon Master" projects exist] [R: reports/Mistborn TTRPG AI design patterns.md §AI Dungeon's decade of failures]

- **The DM's self-report is not verification.** "GLM judging GLM... says nothing about whether an independent judge would differ." (The constitution records its own probe instance.) Procedures should rely on tool-state comparison, not self-assessment.
  [R: research_notes/Mistborn TTRPG AI design patterns/ai_game_integration.md §What patterns exist for preventing an LLM from overriding rules]

- **Spotlight balance must be engineered.**
  Alexandrian: Spotlight balance is "more an art than a science." The round-2 report: "an AI GM has no native equivalent of a human GM's felt sense that 'the rogue hasn't had a moment in three sessions,' so Spotlight balance needs to be engineered as an explicit scene-framing heuristic."
  In single-player, "spotlight" becomes *rotating which of the PC's capabilities and tags the scene calls on*: each recognized calling, ability or untested tag should get a scene that showcases it within some window. That can be tracked deterministically (e.g. scenes since each ability was relevant).
  Pairs with P16.
  [R: research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md §Designer blogs/essays] [R: reports/Mistborn TTRPG AI design patterns.md §TTRPG balance theory supplies]

- **Don't escalate against the optimizer; diversify and focus on consequences.** (See 09 and 11.) This is procedural guidance for scene generation.
  [R: research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md §Designer blogs/essays]

- **Adjust to observed power, within rules.** "Fetishizing Balance" recommends adjusting difficulty to the actual party rather than treating guidelines as law, and warns that both CR-zealotry and CR-dismissal are errors. This must still be a *rule* (when and how the DM retunes) so it is not a blanket override (III).
  [R: research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md §Designer blogs/essays]

- **Narrate milestones; don't dump stats.**
  - The genre's own corrective: "Blue boxes for significant milestones only. Level-ups, major loot, skill unlocks. Not every minor stat change." "Show me the story, not the spreadsheet."
  - HWFWM's author moved to "periodic 'stat recap chapters'."
  - The note's analogy: "periodic explicit state summaries (rather than constant blow-by-blow mechanical narration) may be the sustainable middle ground."

  Procedure: narration voices consequences; the codex holds numbers; offer a recap at session or chapter boundaries.
  [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §How complex would this system be] [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §Is there indication of how complex/trackable]

- **Disclose limits before reliance (Sanderson's middle ground).** "Tell the player what an ability *cannot* do and what it costs *before* they rely on it in a critical moment... without necessarily explaining the cosmological/metaphysical 'why'." This is the procedural counterpart to the probe failure where the DM invented a cold vulnerability from "no protection against cold."
  [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §Is there commentary on how Sanderson keeps] [R: reports/LitRPG mechanics for AI DM design.md §Comprehensible live adjudication demands bounded slots]

- **Improvise new content hook-first, then map it to primitives.** Sanderson's systems all start "from a *personal/thematic hook first*... and only *then* formalized into a rigorous rule-grid." The Zeroth Law says begin with the awesome idea.
  For improvising an NPC power, a location effect or a rumor: choose the hook, then express it only through existing primitives (Streamlining). This is the "reach and adapt" move constitution P3 describes.
  [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §Sanderson's own design commentary] [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §What are Sanderson's (Three) Laws of Magic]

- **Abstain rather than force a binary verdict.** Three-valued judging. In DM procedure: when a [J] call is genuinely uncertain (a borderline evidence moment or an ambiguous creative action), prefer outcomes that don't lock in. Examples: offer instead of grant (P5); record provisional evidence; ask one clarifying question.
  [R: research_notes/Mistborn TTRPG AI design patterns/ai_game_integration.md §What patterns exist for preventing an LLM from overriding rules]

- **Rules-first beats story-first for an adjudicating GM.** The product landscape splits into full rules automation, flexible system interpretation, and "story-first... narrative game engines." The note's inference: borrow PF2e's math-first philosophy "as the safer foundation for autonomous adjudication."
  [R: research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md §Is there existing design discourse about TTRPG systems built to be run by a computer/AI GM]

- **Agentic multi-step beats a static prompt.** The static-vs-agentic GM paper (v2 ReAct/multi-agent) "significantly improv[ed] modularity and game experience, including immersion and curiosity" (abstract only; full text unavailable). This weakly supports a DM turn loop with explicit sub-steps rather than one-shot narration.
  [R: research_notes/Mistborn TTRPG AI design patterns/ai_game_integration.md §What other notable "AI Dungeon Master" projects exist]

- **"Failure moves the plot forward" (PbtA) is P16's rationale.** The 6− result is "a GM-authored complication," never a dead end.
  [R: research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md §How do "Powered by the Apocalypse" (PbtA) games]

- **Read gates by rule, not by vibe (Stormlight's limited gatekeeper).** The oath gatekeeper's discretion "appears to be limited." DM discretion at recognition moments should be bounded by criteria and examples ([J] with a rubric). The research table's own note: an Ideal-style gate "requires a genuinely qualitative judgment call unless converted into a numeric rubric."
  [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How do Ideals/oaths gate power growth] [R: reports/Mistborn TTRPG AI design patterns.md §An updated, tradeoff-flagged primitive list]

### Chapter 13 — Starter setting (classic-fantasy region + opening that exercises every subsystem)

- **The opening as a tutorial phase that defers permanent optimization.** DCC's "Floor 3" lock lets new players "learn action-based advancement before facing a big permanent allocation decision." The opening region should produce early tag evidence and a first recognition *offer* before any irreversible choice.
  [R: research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md §Dungeon Crawler Carl] [R: reports/Mistborn TTRPG AI design patterns.md §Five more progression-fantasy series]

- **Themed sites as pool gates.** Seed the region with places whose nature gates loot and awakenings (the gloomy stair, the rain pond; Beware of Chicken's qi-rich farm).
  [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How do Awakening Stones work] [R: research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md §Beware of Chicken]

- **Institutions that recognize and restrict.** A guild or society that examines and names callings (Magic Society records; The Land's Trial) and one that polices forbidden ones (Adventure Society restrictions and bounties) exercise 04 and 11 from session one.
  [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How does the class/"Classification" system work] [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §How does the class system work]

- **An order and a mentor with a squire relationship.** A present, recognized NPC who can extend a borrowed, range-limited power tests the P2 floor and 04's mentor vehicle in the starter region.
  [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How do Ideals/oaths gate power growth]

- **Interconnection and thematic coherence.** Design the region's powers and cultures from a thematic core ("what thieves would want") so they "seem like a coherent whole." Local cultures reinterpret the primitive set (Streamlining).
  [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §What are Sanderson's (Three) Laws of Magic]

- **A holding the PC can improve.** A settlement or base with Loyalty/Morale scales (The Land's Mist Village) exercises downtime and the living world.
  [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §Crafting, settlement-building, and other non-combat progression]

- **Multi-domain threats.** Include at least one swarm (tests single-target builds), one tough solo, one social and one exploration hazard. This follows the diversification principle and Jason's swarm weakness.
  [R: research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md §Designer blogs/essays] [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §What makes two characters' builds feel meaningfully distinct]

- **A periodic world event.** A highstorm-like recurring event that recharges or disrupts a resource exercises clocks.
  [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How does Surgebinding work mechanically]

- **An adversary who cheated the path.** An Honorblade- or Hemalurgy-style villain with shortcut power and an exploitable string (see 09).
  [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How do Shardblades and Shardplate fit] [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §How does Hemalurgy work]

### Chapter 14 — Players' guide & codex spec (P7)

- **The codex is the Ars Arcanum pattern, moved out of fiction per the BRIEF.** Sanderson's "Ars Arcanum" is a scholarly glossary appended to each volume (in-world attributed to Khriss). It separates "story-experienced" magic from "reference-layer systematized detail," available to curious readers without being "forced into every scene." The BRIEF makes the codex out-of-fiction; the structural split is the same.
  [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §Is there commentary on how Sanderson keeps] [R: reports/LitRPG mechanics for AI DM design.md §Comprehensible live adjudication demands bounded slots]

- **Without a codex, players build their own (HWFWM's symptom).** "A few google spreadsheets... one has a breakdown of team [Jason]'s abilities... a list of all (explicitly) known essences and awakening stones," a wiki, and a Discord bot that looks up "any essence and get all its known confluences." Even the author needed three appendix chapters. Codex views should mirror these: my abilities; my active effects; known combinations; known items.
  [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §Is there indication of how complex/trackable]

- **Every ability entry must show "cannot" and "cost" (First Law, middle ground).** Show limits and possibilities; the metaphysics can stay opaque.
  [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §Is there commentary on how Sanderson keeps]

- **Show hidden variance qualitatively (P1 + P7 reconciliation).** The Land note: "hide raw affinity numbers behind qualitative descriptors" and "surface milestone-only notifications." In the codex this reads e.g. "a natural knack for…" rather than 73%. That keeps the variance hidden but not misleading.
  [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §How complex would this system be]

- **Present escalating quantities as bands.** (See 00.) The codex shows tier names. Raw numbers are available on request if the owner wants them (a P3 player-complexity non-constraint).
  [R: reports/LitRPG mechanics for AI DM design.md §Candidate primitives and patterns]

- **Player strategy advice the guide can give.**
  - Deferring a fill can improve synergy (HWFWM's "wait until you have your full set").
  - Structural weaknesses are real (swarms vs attrition kits).
  - Hybrid breadth trades against early competence (MAG).
  - Oaths and values can be strained and broken (Stormlight).
  - Optimization is expected and fine (Alexandrian).

  [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How do Perks and Feats work mechanically] [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §What makes two characters' builds feel meaningfully distinct] [R: research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md §Designer blogs/essays]

- **The codex must reflect authoritative state.** The reference layer "only works if the reference layer is actually kept current and the AI DM reliably queries it." It is generated from state, never from narration memory.
  [R: reports/LitRPG mechanics for AI DM design.md §Candidate primitives and patterns] [R: reports/Mistborn TTRPG AI design patterns.md §An updated, tradeoff-flagged primitive list]

- **Pacing of disclosure.** The Land's Book-1 sheet vs its Level-45 sheet shows how fast a sheet grows. The guide should explain consolidation (VI) up front, so players expect retirements at boundary points ("budget for the documented cost").
  [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §Does the series show power creep]

---

## 2. Concrete mechanics catalog

Each entry gives what it is mechanically (2–5 lines), then **Adopt/adapt →** the chapter(s). ★ marks mechanics that inform **in-fiction class/identity recognition without a diegetic System**. ⚖ marks **cost / limitation / weakness (P12)** mechanics.

### 2.1 Identity & recognition mechanics

1. **★ Spren attraction (Stormlight).** Ten spren types, each drawn to two personality attributes (the table in 03). A spren bonds a person whose *demonstrated actions* match. The bond grants that Order's fixed Surge pair. Players never pick an Order; behavior picks it. **→ 03** (values branch), **04** (eligibility), **11** (orders recruit). [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How does Surgebinding work mechanically]
2. **★ Ideals / oaths (Stormlight).**
   - 5 sequential tiers. Ideal 1 is universal; 2–5 are Order-specific.
   - Swearing requires genuine readiness; a gatekeeper has limited veto.
   - Swearing releases light proportional to the Ideal number, raises Stormlight efficiency and unlocks Surge applications.
   - Blade at 3, Plate at 4. Most stop at 3. The Fifth makes the bond permanent.

   **→ 04** (tiers, P2), **05** (efficiency), **07/VI**. [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How do Ideals/oaths gate power growth]
3. **★ ⚖ Oath-breaking / deadeye.** Acting against your attributes weakens the bond; eventually the spren breaks. You lose all Surges and your Blade becomes a mundane sword. Only genuine recommitment restores it. **→ 03** (signed evidence), **04** (revocation + atonement track), **07**. [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How does Surgebinding work mechanically]
4. **★ ⚖ Squires.** A full Radiant grants a candidate lesser Order power without a bond. It fails beyond 30–50 miles, or 1–2 hours after an Oathgate separation, and holds Stormlight less efficiently. Candidates need a matching mental state. **→ 02** (P2 floor), **04** (mentor vehicle, provisional tier), **10** (range), **11** (legacy protégé). [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How do Ideals/oaths gate power growth]
5. **★ Individualized truths (Lightweavers / Elsecallers).** The same class, but the tier-2–5 text is a personal truth the character discovers rather than a fixed oath. It is a rule-governed exception. **→ 04** (per-calling "fixed vs personal" tier-text flag). [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §What makes different Radiant orders/characters feel mechanically distinct]
6. **★ ⚖ Multiple acquisition routes to the same powers.** Nahel bond (earned, grows) / Honorblade (anyone, costlier, no growth) / Fused brand (one Surge, Voidlight) / direct blessing (unbound, "immensely dangerous"). The same capability comes with different strings. **→ 04** (vehicle table), **08** (relics), **09** (villains). [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How does Surgebinding work mechanically]
7. **★ Confluence (HWFWM).** Holding 3 chosen essences auto-manifests a 4th, derived from that exact combination. You cannot choose it; reject it and there is no substitute. It is lookup-deterministic (institutional records) until a world event makes it partly random. **→ 04** (hybrid = derived identity; sparse table), **11** (world event changes rules). [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How does the class/"Classification" system work]
8. **★ ⚖ Institutional records and restrictions (HWFWM).** The Magic Society catalogs known combinations. The Adventure Society restricts harmful essences and combinations; possession can bring a bounty. **→ 04, 11, 13**. [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How does the class/"Classification" system work]
9. **★ ⚖ Divine essences (HWFWM).** Granted by a god, who stays connected and can reclaim them. Reclamation after advancing past Iron leaves the user "dangerously unbalanced." **→ 04** (patron vehicle, revocable), **11**. [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How does the class/"Classification" system work]
10. **★ Racial gift evolution (HWFWM).** 6 fixed gifts per race, including an affinity. Gifts "evolve... usually from traumatic events." **→ 02** (origin package), **04/07** (crisis awakening). [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How do Perks and Feats work mechanically]
11. **★ Essence Revelation (HWFWM Gold).** Beyond Silver, fighting and training stop sufficing. A distinct breakthrough is required, and it is harder for anyone who relied on cheap cores. **→ 03** (evidence quality), **04** (higher tiers need a different evidence kind). [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How does leveling work]
12. **★ Profession Trial (The Land).** Eligible at (level 10 + Journeyman non-combat) or (level 20 + Journeyman combat). You speak ritual words ("I am Alchemist"); a week passes. Named sub-specialties follow, each with fictional prerequisites (e.g. Essence Enchanter requires Mastery of a Place of Power). **→ 04** (examination vehicle, dual threshold), **10** (downtime). [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §How does the class system work]
13. **★ Evolution via survived ordeal (The Land's Chaos Lord).** Offered after surviving the Sea of Chaos, with a disclosed 99.9999% success rate. It has 9 internal ranks; Ascendance needs >50% of them; a random Bloodline is granted on taking it. **→ 04** (ordeal vehicle, tier-event variance), **07** (disclosed odds). [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §How does the class system work]
14. **★ Choice (The Land).** A one-time reward for being first to a milestone: 3 mutually exclusive options within a 7-second window. **→ 04** (offer tier with named exclusive options). [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §What makes builds feel distinct/personalized]
15. **★ Unique skills for unprecedented feats (DCC).** A GM-discretionary reward for a singular deed. **→ 04** (titles from deeds; bounded). [R: research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md §Dungeon Crawler Carl]
16. **★ Advancement through understanding (Cradle).** Rank-ups tied to "spiritual development and understanding," not grinding. **→ 03, 04**. [R: research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md §Cradle]
17. **★ Heredity (Allomancy / Feruchemy).** Power is genetic. Misting (1 metal) or Mistborn (all) is fixed at birth. Twinborn appear only after populations mix. **→ 02** (lineage origin), **11** (legacy heirs, history-gated rarity). [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §How does Allomancy work] [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §What is a Twinborn]
18. **★ Thematic manifestation sites (HWFWM).** Essences and stones appear in places matching their theme. Gods craft them for followers. **→ 04** (place vehicle), **08, 13**. [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How do Awakening Stones work]
19. **★ Visible tier tell.** Ideal-swearing emits light proportional to the tier, so witnesses see it and reputation spreads. **→ 04** ([N] tell), **11** (rumor seeding). [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How do Ideals/oaths gate power growth]
20. **★ Class-label-implies-personality.** Order membership lets readers "infer personality... without extra exposition." A calling's name carries characterization, so NPC reactions can key off it. **→ 04, 11**. [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §What makes different Radiant orders/characters feel mechanically distinct]
21. **★ Knowledge-as-build (Mother of Learning).** Raw power resets; procedural knowledge persists. **→ 03** (known-techniques ledger), **11** (legacy). [R: research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md §Mother of Learning]

### 2.2 Progression & tier mechanics

22. **Mutual macro/micro rank-gating (HWFWM).** Ability sub-ranks 1–9 sit within the character Rank and cap at the Rank. Rank-up requires all abilities at a threshold (Iron: all 4 slots bonded; Bronze: all 20 unlocked, with the level requirement disputed in the source). **→ 04**. [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How does leveling work]
23. **Two advancement paths with different ceilings (HWFWM).** Honest (danger, training, meditation) vs monster cores (cheap, capped below Diamond; crafters are the exception). **→ 03, 08**. [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How does leveling work]
24. **Skill ranks by level band (The Land).** Novice 1–9, Initiate 10–24, Apprentice 25–44, Journeyman 45–69, Adept 70–100, Master 100–149 (overlap at 100), Grandmaster 150+. Perks unlock at rank thresholds. **→ 00** (scale type), **03/04** (tag thresholds with named bands). [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §How do skills work]
25. **Sub-skill tree, two rules (The Land).** A child is capped by its parent; child progress credits the parent; learning a child also teaches the parent. **→ 03**. [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §How do skills work]
26. **Affinity (The Land).** A birth-random percentage per skill. It sets both leveling rate and ceiling, needs ≥50% to learn, and falls as levels rise. Limitless sets 100%. **→ 02** (P1), **03**. [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §How do skills work]
27. **XP curve (The Land).** Cumulative XP where per-level cost rises by a fixed increment within each 10-level band, and the increment doubles each band. Per-level cost: 1k, 2k, … 9k (L2–L10), then 11k, 13k… **[R2 verified against the wiki table; the source's "flat within band" reading is wrong]**. Useful only as a closed-form threshold template, since P2 removes XP. **→ 03/04** (threshold curves). [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §How does character leveling interact with skill leveling]
28. **Use-based auto-leveling plus a specialization fork (DCC).** Skills level by use to ~10, then force a fork that replaces the generic path. Stat allocation is locked until Floor 3. Benefits never level. **→ 03, 04** (VI fork), **02** (deferred choices). [R: research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md §Dungeon Crawler Carl]
29. **Cap-for-restriction (Primal Hunter).** 22 total stats unrestricted vs 27 with severe restrictions (E-grade). **→ 02, 04, 05** (vows). [R: research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md §The Primal Hunter]
30. **Single-integer rank + 10× rule (Cradle).** One rank per combatant resolves most contests; each rank is ~10× the one below. **→ 09, 01**. [R: research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md §Cradle]
31. **Race/origin quantity-vs-freedom (The Land).** 4 free vs ~5 restricted vs 6 free (Chaos Seed, plus a +25% progression and talent bonus). **→ 02**. [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §How do core stats/attributes work]
32. **Anti-stall auto-allocation (The Land).** Points unspent across more than one level for a week are assigned randomly. **→ 02** (deferral deadline). [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §How do core stats/attributes work]

### 2.3 Slot / combinatorics mechanics

33. **4 essences × 5 abilities = 20 cap; no duplicates; one aura (HWFWM).** 4 slots free, 16 need stones. **→ 05**. [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How do Perks and Feats work mechanically]
34. **Awakening Stones (HWFWM).** A consumable, single use, that awakens a latent slot. The fill is rolled, weighted by race, existing essences, knowledge, unawakened options and (theorized) personality. Rarer stones are more specialized. No reroll. **→ 05, 08** (P5 fill). [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How do Awakening Stones work]
35. **Ten Surges in a closed ring of 10 adjacent pairs (Stormlight).** Each Surge is shared by exactly 2 Orders. **→ 00/03** (geometry). [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How does Surgebinding work mechanically]
36. **Allomantic grid (4×2×2 = 16).** Physical/Mental/Temporal/Enhancement × internal/external × push (alloy) / pull (base). Named basic pairs: Iron/Steel (pull/push metal), Tin/Pewter (senses/physical enhancement), Zinc/Brass (riot/soothe emotions), Copper/Bronze (conceal/detect Allomancy). **→ 00/03, 05, 09**. [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §How does Allomancy work]
37. **Aspect × technique archetype (Cradle).** Aspects: earth, stone, water, life, lightning, blood, shadow, fire, force, pure. Archetypes: Striker, Enforcer, Forger, Ruler. Advanced artists layer several technique types. **→ 03, 05**. [R: research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md §Cradle]
38. **Fixed spell elements, free recombination (MoL).** Humans cannot invent elements; there are 15 disciplines + 2 support fields. **→ 00, 05, VI**. [R: research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md §Mother of Learning]
39. **Twinborn + Compounding.** 16×16 = 256 pairings; the 16 matched ones release stored attributes ×10. **→ 04/05** (P6 hybrid synergy; must be bounded). [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §What is a Twinborn]
40. **Three Lashings.** A named composite of Adhesion + Gravitation (Basic/Full/Reverse). **→ 05** (P6). [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How does Surgebinding work mechanically]
41. **Misting / Mistborn cliff.** Binary access with no incremental path. **→ 02/04** (anti-pattern; the MAG handicap fix). [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §How does Allomancy work]
42. **Blue Magic (Underworld).** Copy the natural abilities of creatures killed or absorbed. **No known trigger, cap, cost or failure rule.** **→ 04** (gated special trait; the project must author all four). [R: research_notes/LitRPG mechanics for AI DM design/underworld_level_up_or_die.md §Is there a distinctive hook]
43. **Hemalurgy encoding.** Spike location plus the donor's manner of death encode which power is stolen, with no per-metal table. **→ 04/08** (pool-gate/fill grammar for grafting). [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §How does Hemalurgy work]

### 2.4 Resource & cost mechanics (⚖)

44. **⚖ Stormlight as fuel.** Inhaled from infused gems (recharged by highstorms). It leaks faster the more you hold, glows, drives you toward action, and leaves exhaustion when empty. Efficiency rises with Ideals. Squires are less efficient; Honorblades cost far more; Towerlight leaks faster. It is a limitation, not a cost. **→ 05, 07**. [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How does Surgebinding work mechanically]
45. **⚖ Allomantic burn and flare.** A per-metal burn duration (instant to 40 minutes). Flaring raises potency and burns much faster. Ingesting impure metal harms you. Aluminum wipes reserves. Duralumin amplifies whatever else is burning. **→ 05, 01**. [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §How does Allomancy work]
46. **⚖ Feruchemical store/tap.** Weaken an attribute now to charge a metalmind; tap it later for the same amount (net zero). Side effects (zinc hunger). The metalmind is a physical, possibly stealable asset. **→ 05** (debt-shaped Focus option), **08** (banked items), **07** (weakness period). [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §How does Feruchemy work]
47. **⚖ Hemalurgic dual tax.** (a) A quantitative loss at creation plus decay while the spike is outside a body (the decay can be engineered away); (b) a qualitative susceptibility to external control. Plus the moral cost (murder). No sourced %. **→ 04e, 08, 09, 07**. [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §How does Hemalurgy work]
48. **⚖ Identity-bounded healing.** Stormlight will not heal what the bearer considers part of their self. **→ 07**. [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How does Surgebinding work mechanically]
49. **⚖ Madra recovery channels (Cradle).** Self-cycling, environment-matched aura, elixirs. **→ 05, 07, 10**. [R: research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md §Cradle]
50. **⚖ Structured vs unstructured casting (MoL).** Structured: fixed words and gestures, weeks to learn, narrow and reliable. Unstructured: open shaping, years to decades, flexible. Mastery adds flexibility inside a structured boundary and removes components. **→ 01, 05** (creative extensions of licensed abilities). [R: research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md §Mother of Learning]
51. **⚖ Shardblade/Plate rules.** Blades cut the soul; death is delayed except from head or spine hits; there is a closed counter list (Blade, Plate, half-shards, charged metalmind or Invested object, aluminum). Plate: two hits shatter a section. Blades can't be summoned inside a solid object. **→ 06, 07, 08**. [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How do Shardblades and Shardplate fit]
52. **⚖ MAG breadth-vs-competence handicap.** The broad-access build starts with mediocre stats. Everyone assigns strong/average/weak attributes. **→ 02, 04**. [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §Documented power-creep / balance discussion]
53. **⚖ 5e multiclass (MAD) price.** Versatility is paid for with slower primary-stat progression. Removing the price degrades the game. **→ 04** (hybrid pricing). [R: research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md §How does D&D 5e's "bounded accuracy" work]
54. **⚖ Aura cap and cap-lifting gifts (HWFWM).** One aura, unless a rare gift raises the limit. **→ 05**. [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How do Perks and Feats work mechanically]
55. **⚖ Build structural weakness (HWFWM Jason).** An attrition/affliction kit is strong against tough single targets and weak against fast swarms. **→ 05, 06, 09**. [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §What makes two characters' builds feel meaningfully distinct]
56. **⚖ Healer-weakness dissolution (Underworld, cautionary).** A nominal healer given damaging "healing" plus elemental magic loses its group-dependency weakness. Reviewers call this unbalanced. **→ 04, 05** (don't let a trait delete its own class's weakness). [R: research_notes/LitRPG mechanics for AI DM design/underworld_level_up_or_die.md §How does the class system work]

### 2.5 Resolution & balance math

57. **PF2e degrees of success.** ±10 from the DC gives a critical; a natural 20 or 1 shifts one step. **→ 01**. [R: research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md §How do Pathfinder 2e's three-action economy]
58. **PF2e 3 actions + 1 reaction**, with standard costs. **→ 06**. [same]
59. **Bounded accuracy.** Total bonus capped at ~+11 (proficiency +6, item +3, ability +5); DC and AC max 30; advantage replaces flat-bonus feats. **→ 00, 01**. [R: research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md §How does D&D 5e's "bounded accuracy" work]
60. **PbtA bands.** 2d6: 10+ / 7–9 / 6−, with the probabilities in §3. **→ 01, 05** (moves). [R: research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md §How do "Powered by the Apocalypse" (PbtA) games]
61. **GURPS point-buy and its exploits.** Attribute arbitrage (+1 IQ raises every IQ skill); disadvantage refunds gamed; cap disadvantages at ~50% of the pool. **→ 02** (prohibition / P11). [R: research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md §How do point-buy systems like GURPS]
62. **CR / XP budget and its failure modes.** It ignores action economy, count, allies, and PC party size. Remedy: use multiple axes. **→ 09**. [R: research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md §What is "encounter balance math"]
63. **Trap-option avoidance.** Two routes: PF2e exhaustive audit, or 5e few choice points benchmarked to one unit (a feat = +2 to an ability). **→ 04, 05, 08**. [R: research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md §Is there a recognized concept of "trap options"]
64. **Alexandrian balance taxonomy.** Concept / Naturalistic / Spotlight balance; the Iron Man Principle; the Optimization Arms Race (diversify, focus on consequences). **→ 04, 08, 09, 12**. [R: research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md §Designer blogs/essays]

### 2.6 World / faction mechanics

65. **The Land's settlement scales.** Loyalty (−7..+7), Morale (±100% on three multipliers), Fighting Spirit (±5 → ±50% damage), War Leader ranks (7, with per-battle quotas), settlement Powers via quest chain, and settlement-cast spells for the Master. **→ 11, 10, 06, 00**. [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §Crafting, settlement-building, and other non-combat progression]
66. **Crafting quality ladders (The Land).** Alchemy type (8) × Alchemy strength (7); Building Quality (7). **→ 08**. [same]
67. **Highstorm recharge cycle (Stormlight).** A periodic world event recharges the magic resource. **→ 11, 13**. [R: research_notes/LitRPG mechanics for AI DM design/stormlight_archive_magic.md §How does Surgebinding work mechanically]
68. **Place-based cultivation (BoC; Cradle vital aura).** A place becomes richer through cultivation, and matching environments speed recovery. **→ 10, 11**. [R: research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md §Beware of Chicken] [R: research_notes/Mistborn TTRPG AI design patterns/other_popular_litrpgs.md §Cradle]

### 2.7 AI-architecture mechanics (only where they shape rules)

69. **Dice-roll vs state function classes, plus an injected rules summary** (Thirteen Hours). **→ 00, 12**. [R: research_notes/Mistborn TTRPG AI design patterns/ai_game_integration.md §What other notable "AI Dungeon Master" projects exist]
70. **Three-lane memory** (FictionRAG: events / persona traits / worldview constraints); **verified skill library with top-5 retrieval** (Voyager); **memory stream + reflection + planning** (Generative Agents). **→ 00, 11, 03**. [R: research_notes/Mistborn TTRPG AI design patterns/ai_game_integration.md §What patterns exist for preventing an LLM from overriding rules] [R: research_notes/Mistborn TTRPG AI design patterns/ai_game_integration.md §What academic research exists on LLM agents]
71. **Three-valued judge gate** (p≥0.9 fail / p≤0.5 pass / abstain), **independence requirement**, **Jev** (≤255 options, calibrated). **→ 04** (grant/offer/abstain analogy), **12**. [R: research_notes/Mistborn TTRPG AI design patterns/ai_game_integration.md §What patterns exist for preventing an LLM from overriding rules]
72. **Dialogue-game evaluation harness** for regression-testing rule compliance. **→ appendix/open-empirical-questions**. [R: research_notes/Mistborn TTRPG AI design patterns/ai_game_integration.md §What academic research exists on LLM agents]

### 2.8 Mistborn Adventure Game (MAG) — what the sources actually contain

The sources contain **only** the following about MAG. They do **not** describe MAG's resolution dice mechanic at all (see §5 Gaps).
- Mistings use one metal; Mistborn use all, simultaneously if desired.
- Per-metal burn rates (instant to 40 minutes real-world duration).
- Flare mode (more potency, faster consumption).
- Metal purity and toxicity harm.
- Feruchemy: storing makes you weaker, tapping makes you stronger than usual.
- The design problem statement ("how do you let people play Mistborn and not have everybody else suck").
- The fix: Mistborn start with mediocre stats, and all characters rank attributes strong / average / weak.

[R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §How does Allomancy work] [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §How does Feruchemy work] [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §Documented power-creep / balance discussion]

---

## 3. Numbers ledger

Abbreviated source keys (see §0.1) are used in the "Source" column. The full citation is `[R: <path> §<heading>]` with the path from §0.1.

| # | Number | Context | Source (key §heading) |
|---|---|---|---|
| 1 | 4 | HWFWM attributes: Power, Speed, Spirit, Recovery | HW §How do core Attributes work |
| 2 | 3 + 1 | HWFWM essences: 3 chosen + 1 auto-derived confluence | HW §How does the class/"Classification" system work |
| 3 | 5 | HWFWM essence rarity tiers (Common, Uncommon, Rare, Epic, Legendary) | HW §How does the class/"Classification" system work |
| 4 | 5 / 20 | Abilities per essence / total ability cap (4×5) | HW §How do Perks and Feats work mechanically |
| 5 | 4 free / 16 stones | Abilities auto-unlocked on bonding / Awakening Stones needed to fill the rest | HW §How do Awakening Stones work |
| 6 | 1 (Estella: 4) | Aura abilities allowed per character (a rare gift lifted it to one per essence) | HW §How do Perks and Feats work mechanically |
| 7 | 6 | HWFWM ability categories (Aura, Conjuration, Familiar/Summon/Puppet, Special Ability incl. Perception, Special Attack, Spell) | HW §How do Perks and Feats work mechanically |
| 8 | 1–9 | HWFWM ability sub-ranks within each character Rank | HW §How does leveling work |
| 9 | 7 | HWFWM ranks: Normal, Iron, Bronze, Silver, Gold, Diamond, Transcendent (the report once says a "6-rank frame") | HW §How does leveling work; LR §All four systems break down the same way |
| 10 | ~60 / 75 / 100 / 200 / 500 yrs | Life expectancy, Normal through Gold | HW §How does leveling work |
| 11 | 6 | Racial gifts per character ("Everyone gets 6") | HW §How do Perks and Feats work mechanically |
| 12 | ~35 | Distinct boons/afflictions from Jason's kit alone (Book 12) | HW §Is there indication of how complex/trackable |
| 13 | 3 | Appendix chapters needed for one character's kit (Appendix II–IV) | HW §Is there indication of how complex/trackable; LR §Comprehensible live adjudication |
| 14 | 3 | Times the Legendary Celestials stone was ever used | HW §How do Awakening Stones work |
| 15 | Books 1–10 / 11+ | Confluence deterministic / non-deterministic after a world event | HW §How does the class/"Classification" system work |
| 16 | ~Book 3 | HWFWM early bonus-loot mechanic removed for overpowering | HW §Does the series show power creep |
| 17 | 100/200/400/600 CP; +1 slot (200); Four Fold 200–400; Rapid Growth ~25% | **Non-canon** HWFWM Jumpchain perk costs | HW §How do Perks and Feats work mechanically |
| 18 | 5⁴ = 625 | Report's illustrative 4-slot × 5-option pool (not HWFWM's real structure; §4 T-2) | LR §Combinatorial diversity comes from small closed sets |
| 19 | 10 / 10 / 10 | Surges / Orders / spren types (Bondsmiths: 3 unique spren) | SL §How does Surgebinding work mechanically |
| 20 | 10 of 45 | Legal Surge pairs out of C(10,2) possible **[R2 analysis]** | SL §How does Surgebinding work mechanically |
| 21 | 20 | Spren-attraction attributes (2 per Order) | SL §How does Surgebinding work mechanically |
| 22 | 5 | Ideals per Order (1 universal + 4 Order-specific) | SL §How do Ideals/oaths gate power growth |
| 23 | 3 / 4 | Ideal granting Shardblade / Shardplate | SL §How do Ideals/oaths gate power growth |
| 24 | "many stop at 3"; 5th "for centuries" (Skybreakers) | Tier distribution | SL §How do Ideals/oaths gate power growth |
| 25 | 30–50 miles; 1–2 hours | Squire power range / time limit after an Oathgate separation | SL §How do Ideals/oaths gate power growth |
| 26 | 9 brands, 1 Surge each | Fused (Odium) access | SL §How does Surgebinding work mechanically |
| 27 | 2 hits | Shardplate section shatters | SL §How do Shardblades and Shardplate fit |
| 28 | 3 (+ Zeroth) | Sanderson's Laws | SL §What are Sanderson's (Three) Laws of Magic |
| 29 | 9 + ~7 | The Land primary + secondary attributes | TL §How do core stats/attributes work |
| 30 | 10 kg | Carry capacity per Strength point | TL §How do core stats/attributes work |
| 31 | 4 / ~5 / 6 / 15 | Stat points per level: Human (free) / other races (restricted) / Chaos Seed / Chaos Lord | TL §How do core stats/attributes work; TL §How does the class system work |
| 32 | 10 / 15 / 30(+15) | Talent points per level: base / Chaos Seed / Chaos Lord | TL §How does the class system work |
| 33 | +25% | Chaos Seed skill progression per level | TL §How does the class system work |
| 34 | 1 week | Unspent points auto-randomized / Profession Trial duration | TL §How do core stats/attributes work; TL §How does the class system work |
| 35 | L10 + Journeyman (non-combat) / L20 + Journeyman (combat) | Profession eligibility (the Trial page says L20 for non-combat: conflict) | TL §How does the class system work |
| 36 | 50% | Minimum affinity to learn a skill | TL §How do skills work |
| 37 | 1–9 / 10–24 / 25–44 / 45–69 / 70–100 / 100–149 / 150+ | Skill rank bands (the 100 overlap is a boundary defect) | TL §How do skills work |
| 38 | 30% / 100% | Fast Learner advancement bonus / Limitless affinity | TL §How does the class system work |
| 39 | L2=1k, L3=3k, L4=6k, L5=10k, L10=45k, L11=56k, L15=120k, L20=245k, L25=450k, L30=755k, L40=1.885M, L50=4.255M | The Land cumulative XP; per-level cost = previous + 1000·2^⌊(L−1)/10⌋ **[R2 verified: 0 mismatches]** | TL §How does character leveling interact with skill leveling |
| 40 | 9 ranks; >50% | Chaos Lord internal ranks; share required before Ascendance | TL §How does the class system work |
| 41 | 99.9999% | Disclosed Chaos Lord evolution success rate | TL §How does the class system work |
| 42 | 3 options / 7 s | Choice reward | TL §What makes builds feel distinct/personalized |
| 43 | L8: HP160/MP180/SP160; Str 11 Agi 17 Dex 19 Con 16 End 16 Int 18 Wis 10 Cha 18 Luck 14; Mental 5%, Air 50%, Spiritual 5% | Richter Book-1 sheet | TL §How do core stats/attributes work |
| 44 | L45: Str 67 Agi 42 Dex 33 Con 79 End 48 Int 78 Wis 50 Cha 41 Luck 65; HP944/MP828/SP480 | Richter late-series sheet (~3–6× growth) | TL §How do core stats/attributes work; TL §Does the series show power creep |
| 45 | 11 schools / ~40 skills | Richter's late sheet breadth | TL §How do skills work; TL §Does the series show power creep |
| 46 | 6 | Enchanter specialties | TL §How does the class system work |
| 47 | ~31 non-combat / ~8 combat | Named Professions | TL §How does the class system work |
| 48 | −7..+7; ≤−250 −20%; ≥250 +10%; ≥500 +20%; ≥1,000 +40%; ≥2,500 +70% | Settlement Loyalty bands → productivity | TL §Crafting, settlement-building, and other non-combat progression |
| 49 | ±100%; ±250 thresholds | Morale extremes; Unhappy/Happy thresholds | TL §Crafting, settlement-building, and other non-combat progression |
| 50 | −5..+5 → ±50% damage | Fighting Spirit | TL §Crafting, settlement-building, and other non-combat progression |
| 51 | 7 ranks; 2,500 WP/battle | War Leader ladder; Battle Captain quota | TL §Crafting, settlement-building, and other non-combat progression |
| 52 | 5,000 / 50,000 EXP; +500 Morale/Loyalty | Settlement Mastery and quest rewards | TL §Crafting, settlement-building, and other non-combat progression |
| 53 | 8 / 7 / 7 | Alchemy potency, Alchemy strength and Building Quality tiers | TL §Crafting, settlement-building, and other non-combat progression |
| 54 | 10 Psi → +1 attribute | Alma's conversion rate | TL §How do core stats/attributes work |
| 55 | 2,000+ vs ~400 pages | Book 7 vs typical entry | TL §Does the series show power creep |
| 56 | 5 | Underworld attributes | UW §How do core stats/attributes work |
| 57 | 25 → 57 (first hour) → beats L200 while <100; "thousands and tens of thousands" | Underworld level escalation | UW §How does leveling and skill acquisition work |
| 58 | 20 | Kidnapped students choosing classes | UW §How does the class system work |
| 59 | +5/+5/+5; −49% Wis | **Unverified**, possibly hallucinated | UW §How do core stats/attributes work |
| 60 | 16 = 8 basic + 8 higher; 4×2×2 | Allomantic metals / grid | MM §How does Allomancy work |
| 61 | instant–40 min | Allomantic burn durations (MAG) | MM §How does Allomancy work |
| 62 | 1 of 8 basic | Misting access | MM §How does Allomancy work |
| 63 | 3 of 16 | Feruchemical metal/attribute pairings confirmed in sources | MM §How does Feruchemy work |
| 64 | 256 / 16 / ×10 | Twinborn combos / matched combos (6.25%) / Compounding multiplier | MM §What is a Twinborn |
| 65 | none | Hemalurgic loss % (unsourced; don't invent one and attribute it) | MM §How does Hemalurgy work |
| 66 | ~level 10 | DCC skill level at the specialization fork | OL §Dungeon Crawler Carl |
| 67 | +25%/lvl; +10% yield & ½ premature detonation/lvl | DCC Pugilism; IED | OL §Dungeon Crawler Carl |
| 68 | +3 / +2 | DCC Toe Ring; War Gauntlets bonuses | OL §Dungeon Crawler Carl |
| 69 | Floor 3 | DCC stat-allocation unlock | OL §Dungeon Crawler Carl |
| 70 | +175/+150/+125/+100/+50/+50/+50 +125 free | Primal Hunter per-level class package (one example) | OL §The Primal Hunter |
| 71 | 22 vs 27 | Primal Hunter E-grade cap: unrestricted vs restricted | OL §The Primal Hunter |
| 72 | ~10 ranks; ×10 per rank | Cradle ladder; "10 Coppers ≈ 1 Iron, 10 Irons ≈ 1 Jade" | OL §Cradle |
| 73 | 4 | Cradle technique archetypes | OL §Cradle |
| 74 | 5 skills; 2–4 years | MoL prerequisites before any spellcasting | OL §Mother of Learning |
| 75 | 15 + 2 | MoL disciplines + support fields | OL §Mother of Learning |
| 76 | 4 or 7 realms × 5 minor stages | Beware of Chicken (**low confidence**, conflicting lists) | OL §Beware of Chicken |
| 77 | +6 / +3 / +5 / 30 / 30 / ~+11 | 5e proficiency / magic weapon / ability mod / max DC / max AC / max total bonus | BT §How does D&D 5e's "bounded accuracy" work |
| 78 | 3 + 1 | PF2e actions + reaction per turn | BT §How do Pathfinder 2e's three-action economy |
| 79 | Stride 1, Strike 1, Raise Shield 1, spell 2, door 1 | PF2e action costs | BT §How do Pathfinder 2e's three-action economy |
| 80 | ±10; nat 20/1 = ±1 step | PF2e degree thresholds | BT §How do Pathfinder 2e's three-action economy |
| 81 | 2d6: 10+ / 7–9 / 6− | PbtA bands. **[R2]** At +0: 16.7/41.7/41.7%; +1: 27.8/44.4/27.8%; +2: 41.7/41.7/16.7%; −1: 8.3/33.3/58.3%; +3: 58.3/33.3/8.3% | BT §How do "Powered by the Apocalypse" (PbtA) games |
| 82 | 200-pt vs 40-pt | GURPS physicist chopped by fighter | BT §How do point-buy systems like GURPS |
| 83 | ~50% (−75 of 150) | GURPS disadvantage cap advice | BT §How do point-buy systems like GURPS |
| 84 | 10–20 pts | GURPS cost of +1 IQ (raises all IQ skills) | BT §How do point-buy systems like GURPS |
| 85 | 4 PCs L5 vs CR 9–10 win; vs several CR 1 die | CR failure case | BT §What is "encounter balance math" |
| 86 | +2 ASI | 5e feat benchmark | BT §Is there a recognized concept of "trap options" |
| 87 | 4.388 vs 3.691 /5 | Consistency with vs without function calling | AI §What other notable "AI Dungeon Master" projects exist |
| 88 | 3.949/5 | Enforcement reliability (rejecting disallowed actions) | AI §What other notable "AI Dungeon Master" projects exist |
| 89 | 46.1% | State-prediction exact match (a unit test, not narration consistency) | AI §What other notable "AI Dungeon Master" projects exist |
| 90 | 41.8% / 23.6% | Hallucination reduction / coherence gain (dev.to, **low confidence**) | AI §What other notable "AI Dungeon Master" projects exist |
| 91 | ~4,000 tokens | AI Dungeon free-tier context | AI §What is AI Dungeon |
| 92 | 4.8 → 2.6 | AI Dungeon Google Play rating after the filter | AI §What is AI Dungeon |
| 93 | 25 agents | Smallville | AI §What academic research exists on LLM agents |
| 94 | 3.3× / 2.3× / 15.3×; top-5 | Voyager gains; skills retrieved per task | AI §What academic research exists on LLM agents |
| 95 | ≤255 options; 70–500 ms; ~$0.001; 40–200× faster; 40–400× cheaper | Jev | AI §What patterns exist for preventing an LLM from overriding rules |
| 96 | p≥0.9 fail / p≤0.5 pass / abstain | Three-valued judge rule | AI §What patterns exist for preventing an LLM from overriding rules |
| 97 | (see table in 01) | **[R2]** d20 degree distributions at +2/+5/+8/+12 vs DC 10/15/20/25, project rule vs PF2e | BT §How do Pathfinder 2e's three-action economy |

**[R2] Full d20 enumeration** (project rule = BRIEF §7; PF2e = one-step shift). Percentages are CF/F/S/CS. The only rows where the two rules differ are marked ◆.

| Mod | DC 10 | DC 15 | DC 20 | DC 25 |
|---|---|---|---|---|
| +2 | 5/30/50/15 | 15/45/35/5 | 40/45/10/5 | ◆ proj 65/30/0/5 · PF2e 65/30/5/0 |
| +5 | 5/15/50/30 | 5/40/50/5 | 25/45/25/5 | 50/45/0/5 |
| +8 | 5/0/50/45 | 5/25/50/20 | 10/45/40/5 | 35/45/15/5 |
| +12 | ◆ proj 5/0/30/65 · PF2e 0/5/30/65 | 5/5/50/40 | 5/30/50/15 | 15/45/35/5 |

---

## 4. Tensions & contradictions

### 4.1 With the constitution / BRIEF

- **T-1. The constitution's P5 body still mandates a "calibrated classifier... MUST NOT share a model family," but the sixth pass and the BRIEF chose a non-ML tag-tally scorer.** The Sync Impact Report records the switch; the P5 text was not rewritten.
  A deterministic tally trivially satisfies "independence." But the *three-valued* policy needs a **confidence per candidate**, and a tally has none unless 04 defines one (e.g. tally margin over threshold, share of evidence in the candidate's branch, number of distinct evidence moments). 04 must define it explicitly.
  The research's three-valued rule (p≥0.9 / ≤0.5 / abstain) gives shape but no numbers for a tally.
  [R: research_notes/Mistborn TTRPG AI design patterns/ai_game_integration.md §What patterns exist for preventing an LLM from overriding rules]

- **T-2. Constitution V cites "HWFWM's 4 essence slots × 5 abilities" as closed-primitive validation, but HWFWM closes slot *count*, not *pools*.** The essence list is large and spans 5 rarities; ability fills are rolled from unenumerated sets. HWFWM's documented tracking crisis (~35 statuses, appendices, fan bot) happened *inside* the closed slot frame.
  V is necessary but not sufficient. The condition vocabulary and the pools must be closed too.
  [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §Is there indication of how complex/trackable]

- **T-3. The constitution overstates Underworld's causal evidence.** V says open-menu systems "became untrackable and power-crept."
  - Underworld's absorption rules are *completely unknown*.
  - Its sources are reviewer paraphrase.
  - "Untrackable" is explicitly an *inference* in the note.
  - Reviewers attribute the creep to *authorial choice* ("the author keep[s] changing it"), not to the system.

  The design conclusion (cap absorption) still holds, but on first principles, not evidence.
  [R: research_notes/LitRPG mechanics for AI DM design/underworld_level_up_or_die.md §Complexity of tracking/adjudicating] [R: research_notes/LitRPG mechanics for AI DM design/underworld_level_up_or_die.md §Overall source-coverage note]

- **T-4. Constitution VI says DCC's forks are the only clean solve.** The sources contain more precedents (see 04d): Stormlight's provisional-until-Fifth-Ideal permanence; MoL's reset-but-keep-knowledge; HWFWM's one-off mechanic removal; world-event rule changes; non-leveling "Benefits."
  VI is not contradicted, just under-supplied. The Stormlight permanence precedent fits VI's provisional-by-default especially well.

- **T-5. P2 removes levels, but the precedents that give *threat scaling* all assume a character rank** (Cradle, HWFWM, The Land, Underworld).
  09 needs a derived power band for the PC computed from tier state, or adversary bands have nothing to compare to. P2 doesn't forbid a *derived* band ("MUST NOT rely on a separate, flavor-independent level number tracked apart from what a character actually did"); a band computed *from* recognized tiers is permissible.

- **T-6. P4 calls the MAG breadth/competence fix "tested."** The only source is a WebSearch synthesis citing a fandomwire listicle. The fix is plausible and the design problem is quoted, but "tabletop-tested" is the report's gloss. Treat it as medium-low evidence. 02/04 should justify the number they choose with their own arithmetic, not by appeal to MAG.
  [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §Documented power-creep / balance discussion]

- **T-7. BRIEF §7's resolution (auto-crit on a nat 20 / nat 1) vs the PF2e source's one-step shift.** They differ only at the edges, but one edge is "experts critically fail trivial tasks 5% of the time." That cuts against "a single unlucky roll never ends a character without warning" wherever critical failure carries harm.
  Separately, the ±10 band gives a 40% critical-failure chance at +2 vs DC 20 (see 01). Not wrong, but the resolution author must calibrate consequences to it.

- **T-8. Hidden variance (P1; The Land's affinity) vs the codex (P7) vs Sanderson's First Law.**
  - P7 wants the player to see their own state.
  - The First Law says don't let unexplained magic resolve conflicts.
  - The Land's affinity is fully hidden.

  The source-suggested resolution: qualitative descriptors. 02 and 14 must agree on exactly what is shown.
  [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §How complex would this system be]

- **T-9. Constitution P3 cites "~46–58% consistency."** My sources support only **46.1%**, and that figure is a *state-prediction unit test* ("correctly predicting resulting state"), not a measured narration-vs-state consistency rate. The consistency metric was 4.388/5.
  The round-2 report made the leap to "narration drifting out of sync... in more than half of cases." The 58% figure is not in these sources (it may come from another report).
  The conclusion (reconciliation needed) is sound; the number is being used loosely.
  [R: research_notes/Mistborn TTRPG AI design patterns/ai_game_integration.md §What other notable "AI Dungeon Master" projects exist] [R: reports/Mistborn TTRPG AI design patterns.md §AI Dungeon's decade of failures]

- **T-10. Revocation severity.** Stormlight's oath-breaking is severe (lose everything, recover only by recommitment). The constitution prefers atonement ("rather than instantly and irreversibly losing power").
  HWFWM divine reclamation leaves the character "dangerously unbalanced." Harsh revocation also collides with VI's player-retention budget ("rework after rework, put off far more people").
  Resolution space: graduated strain with telegraphed thresholds.

- **T-11. Confluence's "reject it and there is no substitute" vs P5's offer/abstain and P1's deferral.** HWFWM forces the derived identity. The project gives the player agency. Not a problem, but 04 should state explicitly that it departs from the precedent.

- **T-12. Zeroth Law / Rule of Cool vs Principle VII and III.** "Err on the side of AWESOME" and "yes, and…" invite narrating capability into existence. That is the exact thing VII forbids. Confine them to framing and outcome colour; never licensing.

- **T-13. The BRIEF's "player-facing complexity is not a constraint" vs the genre's documented failure of stat-dump narration.** No contradiction in principle, since the failure is *narration density*, not player-held complexity. But authors must not read "complexity is fine" as "narrate the numbers." The research is unanimous that in-scene stat recitation fails (GeekDad, the HWFWM audiobook complaints, the 2026 retrospective).

### 4.2 Within the research

- **T-14. The Land's XP curve is misread by both the note and the report.** They say per-level cost is "flat within each 10-level band and doubles every band (1,000/level for L2–10, 2,000/level for L11–20)." The wiki's own cumulative table (L3=3,000, L10=45,000, L20=245,000) matches only **per-level cost = previous cost + 1000·2^⌊(L−1)/10⌋**. That is, the *increment* is flat within a band and doubles each band; the per-level cost grows linearly (1k, 2k, …, 9k, then 11k, 13k…).
  I verified this with 0 mismatches across all 16 tabulated levels. The "flat per band" reading predicts L10=10,000 vs the actual 45,000.
  Irrelevant to rules (P2 removes XP) but matters if anyone copies the curve as a threshold template.
  [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §How does character leveling interact with skill leveling] [R: reports/LitRPG mechanics for AI DM design.md §The Land stacks three parallel progression ladders]

- **T-15. The Land's Profession thresholds conflict.** The Skills wiki says L10 + Journeyman (non-combat) or L20 + Journeyman (combat); the Trial wiki says L20 + non-combat Journeyman.
  [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §How does the class system work]

- **T-16. The Land's skill bands overlap.** Adept is 70–100 and Master is 100–149. This is a real-world example of the boundary ambiguity the BRIEF warns against (crisp boundaries).
  [R: research_notes/LitRPG mechanics for AI DM design/the_land_founding.md §How do skills work]

- **T-17. HWFWM's Bronze requirement conflicts.** The wiki says "all 20 abilities... advanced to at least Bronze-0"; the Reddit thread says "not all need be at Bronze level yet."
  [R: research_notes/LitRPG mechanics for AI DM design/he_who_fights_with_monsters.md §How does leveling work]

- **T-18. The HWFWM rank count is 7 in the note and "6-rank frame" in the report.**
  [R: reports/LitRPG mechanics for AI DM design.md §All four systems break down the same way]

- **T-19. Cradle is cited both for "coarse single-integer rank = lowest bookkeeping" (round 2) and against it.** P3 explicitly revised the instinct to prefer Cradle-style coarseness toward rich granular state. The two are compatible if rank is a *derived band* over granular state (see T-5), not the only state.
  [R: reports/Mistborn TTRPG AI design patterns.md §Five more progression-fantasy series]

- **T-20. "Mistborn = all 16 metals" vs "all basic metals" is ambiguous in the sources, and the Higher-metal names conflict (Malatium/Electrum vs unnamed).** Don't build on specific Higher-metal effects.
  [R: research_notes/Mistborn TTRPG AI design patterns/mistborn_magic.md §How does Allomancy work]

- **T-21. PbtA's "partial success is statistically most common" is only strictly true at +1** (my enumeration). At +0 it ties with a miss; at +2 it ties with full success.
  [R: research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md §How do "Powered by the Apocalypse" (PbtA) games]

- **T-22. PF2e's precision earns contradictory verdicts.** "No trap options" (a safe flavor pick) vs "bonuses feel less impactful." The notes present this as a genuine open dial, not a resolved fact.
  [R: research_notes/Mistborn TTRPG AI design patterns/ttrpg_balance_theory.md §How do Pathfinder 2e's three-action economy]

---

## 5. Gaps (questions a complete ruleset needs that these sources do not answer)

1. **Blue Mage rules.** No source gives an absorption trigger, cap, cost, failure state, or loss rule. 04 must author all of them from first principles plus the Hemalurgy/P5 analogues.
2. **HWFWM rank-up threshold math** ("how advanced must the set be") is soft/narrative in the source. The project needs explicit numbers.
3. **Awakening-Stone weighting formula** is "never quantified." The project must author P5 fill weights.
4. **Affinity math.** How affinity converts into rate and ceiling isn't specified (only: higher = faster and higher; 50% minimum to learn; decreases per level).
5. **Hemalurgic loss %** is not sourced. Do not attribute any number to Sanderson.
6. **Band-to-dice mapping.** No source says what one rank/band gap equals in d20 modifiers, damage or action count. Cradle deliberately avoids numbers. 09 must derive it (e.g. by simulation).
7. **Confidence from a tally.** No source defines how a deterministic tally yields the "confidence per candidate" that the three-valued policy needs (T-1).
8. **A creative-action fairness method specific to an AI adjudicator** is absent from the literature; the only candidate files ("Rule of Cool" guidance, `resolve_improvised_stunt`) are unverifiable.
9. **Mistborn Adventure Game resolution mechanics** are entirely absent from the sources.
   **[unsourced — verify]** My background knowledge, not in the repo: MAG resolves with a d6 dice pool (roughly 2–10 dice); the result is the highest value showing on a matched pair, and 6s act as bonus "Nudges." Characters have Attributes (Physique, Charm, Wits) and Standings (Resources, Influence, Spirit), plus narrative hooks (Drive, Destiny, Tragedy).
   If the owner cares about MAG precedent for origins (Destiny/Tragedy as creation hooks), a web-research pass should verify this before anyone cites it.
10. **Mistborn "Snapping".** **[unsourced — verify]** In canon, latent Allomancy awakens through trauma ("Snapping"). It is the canonical Mistborn precedent for "a power that awakens in a moment of crisis," one of the owner's named recognition vehicles, and it is not in the repo sources. HWFWM's trauma-evolved racial gifts are the only in-repo precedent.
11. **Squire mechanics in detail.** How many squires a Radiant may have, what squires can access, and the promotion path from squire to full Radiant are not in the sources. They matter if 04 adopts a mentor-derived floor.
12. **Second-through-Fifth Ideal texts and per-Order Ideal quests** weren't retrieved. Only the First Ideal and structural rules are available. Authoring oath content has no textual model beyond structure.
13. **Shardplate mechanics** (regeneration, Stormlight infusion, "gemhearts") weren't fetched. Only the "two hits per section" rule exists.
14. **Keyed vs unkeyed metalminds** (who can tap a looted store) is unconfirmed. 08 must decide.
15. **Twinborn / Compounding extra gating** beyond a shared metal is unclear. For P6: does an aligned hybrid need an extra trigger?
16. **The full 16-metal Allomancy and Feruchemy tables** are not verified. Don't cite individual Higher metals.
17. **Crafting % effects** for most quality tiers (Crime, Spell Strength, the higher alchemy bands) have no numbers.
18. **Bloodline mechanics** (The Land) were not fetched.
19. **Secondary-attribute derivation** (The Land) was never formalized by the author. There is no model to copy; the project must write formulas if it has derived stats.
20. **Encounter math for a solo PC.** CR's missing "encounter size multiplier for PCs" is worse at a party size of 1. No source addresses solo balance directly.
21. **Spotlight balance for a single player** has no algorithm anywhere (Alexandrian: "art"). The project must engineer one (12).
22. **Critique of Surgebinding / Allomancy power creep** was not retrieved. The "Stormlight is disciplined" conclusion is weak evidence.
23. **DCC and Primal Hunter balance reception** was not found. Primal Hunter's "Vessel" is unconfirmed as a mechanic.
24. **The AI-GM failure-mode literature** (exploitation by min-maxed builds, systematic degree misjudgment) was not found. It is flagged as the sharpest gap.
25. **Static-vs-agentic GM paper** and **FREYR** full texts were unreadable. Their failure modes are unknown.
26. **Settlement content specific to *Founding*** vs later books is unclear. Book 1 may show only a slice.
27. **Retirement / legacy procedure precedent.** No source describes retiring a character and handing off to a successor. The heredity, knowledge persistence, holdings and protégé analogues are my extrapolation.
28. **Death / dying-state mechanics.** The LitRPG sources say almost nothing about a dying state, last-chance choices, or capture-as-defeat. Only Shardblade delayed death, "Respawns" as a reward, and disclosed evolution odds bear on it. 07 needs other research (R1/R3 presumably).
29. **Action-economy numbers for a solo PC vs many foes** (P9) aren't covered beyond PF2e's 3+1.
30. **The Focus pool's size, costs and recovery rates** have no numeric precedent. Every fuel here (Stormlight, madra, metals) is qualitative. 05 must derive numbers, e.g. from encounter length and action economy.

---

## 6. Top 15 implications (ranked)

Ranked by leverage on the two design goals: (1) player freedom to try creative ideas; (2) the AI adjudicating correctly. Player-facing complexity is not a cost.

1. **Split recognition into a deterministic trigger and a DM-chosen fictional vehicle.** This is how "classic fantasy with hidden mechanics" works mechanically.
   - The tag tally decides *that* a calling or tier is earned [D].
   - The DM picks *which vehicle voices it* from a closed vehicle table [J], keyed to the evidence that drove it. Vehicles: an order that seeks you out (spren attraction); an oath offered at a crisis (Ideals); a mentor's acknowledgement or squire-ship; an examination or trial ("I am Alchemist"); an institution naming what you are (Magic Society records); a title from a singular deed (DCC unique skills); an awakening in crisis or ordeal (HWFWM trauma-evolved gifts; Chaos Lord); a revelation (Essence Revelation; Cradle understanding); a place (thematic stone sites); a patron (divine essences).
   - The player then affirms (the P5 offer). Stormlight proves the same power can arrive through different fictions with different strings.

   *(04, 11, 03)*
2. **Build P2 tiers on Stormlight's Ideal shape, and use permanence as the top-tier reward.**
   - A fixed tier count with a hard top.
   - Tier 1 is universal and identical for every character (Stormlight's First Ideal is shared by all ten Orders), which doubles as the P2 baseline floor.
   - Universal benefit checkpoints at fixed tiers for every calling (Blade@3, Plate@4 analogues), with calling-specific content between them.
   - Sequential, readiness-gated, with a visible tell; designed so most characters plateau mid-ladder.
   - Lower tiers are provisional/revocable and the top tier locks permanent. That is VI's provisional-by-default expressed in the fiction.

   *(04, 02, VI)*
3. **Close three more things than the constitution names: the condition/status vocabulary, the tier ladder's top, and ability text growth.**
   - HWFWM kept a closed 20-slot grid yet produced ~35 statuses for one character, bolted on new top tiers (Diamond → Numen), and let ability text accrete per rank.
   - Every status gets stack / decay / cleanse / interaction fields drawn from a closed stacking-behavior vocabulary (P6 companion).
   - The ladder has a stated maximum.
   - A tier-up *restates* an ability's full text; it never appends.

   *(00, 05, 06, 04)*
4. **Give every ability a governing principle and a "cannot" list, and resolve creative extensions as "unstructured" attempts.**
   - Allomancy's push/pull shows how one physical principle lets the DM derive novel uses consistently.
   - Mother of Learning's structured/unstructured split supplies the resolution: using an ability as written is reliable; stretching it within its principle is allowed at a higher DC, cost or time, and mastery (tier) widens the reliable envelope.
   - This is the single strongest goal-1 mechanism in the corpus that stays inside VII (the extension must share the licensed principle), and it gives the AI a derivation instead of an invention (goal 2).

   *(05, 01, 12)*
5. **Weight evidence by quality and stakes, make it saturate, and require a new kind of evidence at higher tiers.**
   - HWFWM's cheap core path "self-limits" below Diamond and makes Gold's Essence Revelation harder.
   - Cradle ties advancement to understanding, not grinding; Stormlight: "cannot just say the words."
   - So `tag_event` weight scales with risk/stakes, low-stakes repetition caps per scene/context, and each higher tier needs a qualitatively distinct crystallizing event.
   - This stops grinding, which is the failure every LitRPG source documents.

   *(03, 04)*
6. **Make values/conduct a signed tag branch, with a graduated strain → break → atonement track.**
   - Stormlight's 20 spren-attraction attributes are a ready closed vocabulary for behavior-based identity.
   - Acting against them "weakens the bond" before it breaks, and recovery requires recommitment.
   - Record contrary evidence, show a strain state with telegraphed thresholds, and offer atonement (the constitution's Paladin framing), so revocation is never a surprise and never a single call.

   *(03, 04, 07)*
7. **Fix the resolution edges before anyone builds harm on them.**
   - Adopt PF2e's one-step natural-20/1 shift (or explicitly defend the auto-crit rule). Otherwise experts critically fail trivial tasks 5% of the time.
   - Calibrate critical-failure consequences to the default +2 modifier, where DC 20 is a 40% critical failure and DC 25 is 65%.
   - State a bounded-accuracy envelope (max total modifier ≈ +11) so the d20 stays meaningful.
   - Prefer advantage-style circumstance modifiers over stacking flat bonuses.

   *(01, 07, 00)*
8. **Design Focus from the fuel precedents, and add Feruchemy's debt shape as a bounded second mode inside the same pool.**
   - From Stormlight: a pool with a comfort threshold (holding above it leaks); a visible tell; an exhaustion condition at 0; *efficiency gained per tier* as a non-additive growth reward; surcharges for borrowed or off-identity use (squires, Honorblades).
   - From Allomancy: an optional "flare" surcharge for a stronger result.
   - Recovery: three channels (rest/self, a matching environment, consumables).
   - Feruchemy's "bank now at a cost, draw later" is the only structurally different cost shape found. Offer it as a Focus option with an explicit ledger, not as a separate resource (P9).

   *(05, 07)*
9. **Let relics license off-identity capabilities at a premium.**
   - Honorblades grant an Order's powers to anyone "without regard for oaths," at a much higher fuel cost and with no growth.
   - Items can therefore be VII licenses for things outside the PC's calling, priced higher and not feeding tiers.
   - This widens goal-1 freedom (you *can* try the fire trick if you carry the brand) without diluting callings, and gives loot real meaning under the Iron Man Principle's required item budget.

   *(08, 01, 04)*
10. **Separate the breadth of access from day-one competence, for hybrids and generalist origins.**
    - The MAG fix: the all-access build starts mediocre, and everyone assigns strong/average/weak attributes.
    - 5e's MAD price.
    - Primal Hunter's cap-for-restriction.
    - Twinborn Compounding shows aligned hybrids deserve a *bounded* named synergy (Miles's near-infinite healing is the cautionary case).
    - Hybrid recognition should cost more evidence or time, never grant more immediate power, and carry a capped P6 synergy.

    *(04, 02, 05)*
11. **Derive a PC power band from tier state and scale threats by band and action count, never by a single scalar.**
    - Cradle's ~10× per rank is the anchor, which must be translated into d20/Vitality/action terms by simulation.
    - CR's documented failure (several CR 1s kill a party that beats a CR 9) proves action economy and count must be budgeted separately.
    - That matters doubly for a solo PC.
    - Out-of-band foes are telegraphed and adjudicated by rule, and some outcomes auto-resolve across large gaps (HWFWM Silver immunity).

    *(09, 06, 07)*
12. **Stress builds instead of out-escalating them: diversify challenges and engineer "spotlight" deterministically.**
    - The Alexandrian: escalation starts an arms race; the fix is diversification and consequences.
    - Every build needs a real structural weakness (Jason vs swarms), and scene generation should rotate which of the PC's capabilities and untested tags the scene calls on, tracked as state.
    - This is the single-player translation of spotlight balance, and it pairs with P16.

    *(12, 09, 10, 13)*
13. **Loot and crafting: gate pools by nature *and place*, treat rarity as specialization, and use two quality axes.**
    - HWFWM stones manifest where their theme lives, and rarer stones are *more targeted*, not bigger.
    - The Land's crafting uses a type-tier (Brew → … → Essence) crossed with a strength-tier (Tainted → … → Processed). That is exactly pool-gate × fill-quality.
    - Consumables that advance a character must saturate (monster cores).
    - Enforce an explicit item budget, and don't let magic mint wealth (Fabricate).

    *(08, 13, 10)*
14. **Narrate milestones and consequences; the codex holds the crunch and every "cannot" and "cost".**
    - The genre's own correction ("milestones only"; "show me the story, not the spreadsheet") and HWFWM's recap chapters.
    - Sanderson's rule to reveal limits and costs before the player relies on them. The DM must never let an unexplained power decide a conflict (First Law).
    - Hidden variance appears in the codex as qualitative descriptors.
    - Every narrated change must correspond to a recorded tool write, with a turn-end reconciliation check (46.1% state-prediction accuracy even with tools; the project's own probe embellishment).

    *(12, 14, 00)*
15. **Put VI's boundary points in the world, and retire by forking and replacing while keeping knowledge.**
    - DCC's specialization fork replaces the generic path.
    - HWFWM's world event changed the confluence rules. A telegraphed in-world event can be the boundary point that bundles re-banding (the constitution's "infrequent, clearly-telegraphed boundary points").
    - MoL shows the humane retirement pattern: power resets, knowledge persists.
    - Sanderson's Law 3 ("expand before you add") plus a cosmological ceiling (a fixed number of callings or primitives in the world itself) makes the cap part of the setting, not a rule an author can loosen.

    *(04, 11, 05, 13)*
