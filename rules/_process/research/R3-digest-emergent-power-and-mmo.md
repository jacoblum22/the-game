# R3 Digest — Emergent Power Acquisition & MMO/ARPG Design Lessons

> Research digest for the ruleset authors. It covers two research rounds in full: the **fifth pass**
> (`reports/Emergent power acquisition mechanisms.md` plus its 4 research notes: ARPG affix
> generation, freeform combat positioning, LitRPG playstyle→class, roguelike build synergy), and the
> **fourth pass** (`reports/WoW PoE2 MMORPG design lessons.md` plus its 4 notes: computer-vs-tabletop
> complexity ceiling, MMORPG design broadly, Path of Exile gems, WoW talents & balance). It also
> covers the Feature 003 probe that these rounds fed (`src/ability_pool.py`,
> `specs/003-ability-acquisition-probe/implementation-results.md`, and its `contracts/tools.md`).
> Every source file was read in full; this digest aims to leave nothing load-bearing behind.
> Written by research agent R3. It is not a rules chapter. It proposes, maps, and warns, and the
> chapter authors decide.

---

## 0. How to use this digest

- **Section 1** is per-chapter: every finding relevant to chapters 00–14, the appendix, and `data/`.
  Findings that span several chapters appear in full once, and the other chapters point back to them
  (e.g. "→ see 08.3").
- **Section 2** is the mechanics catalog. Each mechanic gets a precise 2–5 line description plus
  the chapter that should adopt or adapt it. Use it when you need to know exactly how a precedent
  works.
- **Section 3** is the numbers ledger: every concrete number in the sources, with context.
- **Section 4** lists tensions and contradictions, both with the constitution and inside the research itself.
- **Section 5** lists gaps: questions the ruleset must answer that these sources do not.
- **Section 6** gives the top 15 implications, ranked.
- **Evidence grade.** Findings are tagged **[F]** for a cited fact in a source, **[I]** for an inference the
  source's own researcher drew, and **[R3]** for my synthesis or arithmetic, which appears in no source.
  Do not cite an [R3] item as research. Cite it as your own Decision Log reasoning.
- **Constitution citations** use `[C:V]`, `[C:P5]` and so on.

### 0.1 Citation key (expand the code to the full string when you cite)

Codes are short aliases. The expansion is the BRIEF-format citation. Headings for the research notes
are truncated to their first identifying clause. The file paths are exact.

| Code | Full citation |
|---|---|
| **E0** | `[R: reports/Emergent power acquisition mechanisms.md §Source Gates the Pool; Method Picks the Fill]` (title + opening synthesis paragraph) |
| **E1** | `[R: reports/Emergent power acquisition mechanisms.md §Diablo, Path of Exile, and Borderlands all split "identity" from "magnitude" into non-competing layers]` |
| **E2** | `[R: reports/Emergent power acquisition mechanisms.md §Slot-claiming effects need a priority rank, not a pairwise table]` |
| **E3** | `[R: reports/Emergent power acquisition mechanisms.md §Delve's dual-tier threshold is the one LitRPG mechanism explicit enough to implement directly]` |
| **E4** | `[R: reports/Emergent power acquisition mechanisms.md §A structured relationship-state, not a grid, is the genre-wide answer to prose-only tactical combat]` |
| **E5** | `[R: reports/Emergent power acquisition mechanisms.md §Candidate primitives and patterns]` |
| **E6** | `[R: reports/Emergent power acquisition mechanisms.md §What this pass changes in the constitution]` |
| **E7** | `[R: reports/Emergent power acquisition mechanisms.md §Conclusion]` |
| **A1** | `[R: research_notes/Emergent power acquisition mechanisms/arpg_affix_generation.md §Diablo series (D2/D3/D4)]` |
| **A2** | `[R: research_notes/Emergent power acquisition mechanisms/arpg_affix_generation.md §Path of Exile's item affix system]` |
| **A3** | `[R: research_notes/Emergent power acquisition mechanisms/arpg_affix_generation.md §Path of Exile 2's crafting currency system]` |
| **A4** | `[R: research_notes/Emergent power acquisition mechanisms/arpg_affix_generation.md §Borderlands' procedural gun-part generation]` |
| **A5** | `[R: research_notes/Emergent power acquisition mechanisms/arpg_affix_generation.md §What happens when this genre wants a "signature"/unique effect]` |
| **FP1** | `[R: research_notes/Emergent power acquisition mechanisms/freeform_combat_positioning.md §How does Blades in the Dark's Position/Effect system]` |
| **FP2** | `[R: research_notes/Emergent power acquisition mechanisms/freeform_combat_positioning.md §How many zones does a typical Fate Core/Fate Condensed scene have]` |
| **FP3** | `[R: research_notes/Emergent power acquisition mechanisms/freeform_combat_positioning.md §How do PbtA games (Dungeon World and others) handle]` |
| **FP4** | `[R: research_notes/Emergent power acquisition mechanisms/freeform_combat_positioning.md §How does Ironsworn / Ironsworn: Starforged's move-based combat]` |
| **FP5** | `[R: research_notes/Emergent power acquisition mechanisms/freeform_combat_positioning.md §What other notable narrative-first systems]` (Mörk Borg) |
| **FP6** | `[R: research_notes/Emergent power acquisition mechanisms/freeform_combat_positioning.md §Has any AI-driven/LLM-driven text RPG project documented]` (ChatRPG) |
| **L1** | `[R: research_notes/Emergent power acquisition mechanisms/litrpg_playstyle_class.md §Which specific novels/series implement]` |
| **L2** | `[R: research_notes/Emergent power acquisition mechanisms/litrpg_playstyle_class.md §For each system found: what actions/stats are tracked]` |
| **L3** | `[R: research_notes/Emergent power acquisition mechanisms/litrpg_playstyle_class.md §How do hybrid/multiclass outcomes get handled]` |
| **L4** | `[R: research_notes/Emergent power acquisition mechanisms/litrpg_playstyle_class.md §What happens when playstyle shifts significantly]` |
| **L5** | `[R: research_notes/Emergent power acquisition mechanisms/litrpg_playstyle_class.md §Author/fan meta-discussion]` |
| **L6** | `[R: research_notes/Emergent power acquisition mechanisms/litrpg_playstyle_class.md §Distinguishing note on prior-round-covered series]` |
| **RG1** | `[R: research_notes/Emergent power acquisition mechanisms/roguelike_build_synergy.md §Hades: the Duo Boon system]` |
| **RG2** | `[R: research_notes/Emergent power acquisition mechanisms/roguelike_build_synergy.md §Slay the Spire]` |
| **RG3** | `[R: research_notes/Emergent power acquisition mechanisms/roguelike_build_synergy.md §Binding of Isaac]` |
| **RG4** | `[R: research_notes/Emergent power acquisition mechanisms/roguelike_build_synergy.md §Risk of Rain 2]` |
| **RG5** | `[R: research_notes/Emergent power acquisition mechanisms/roguelike_build_synergy.md §Cross-case comparison]` |
| **W0** | `[R: reports/WoW PoE2 MMORPG design lessons.md §Squishes Rescale Numbers; Only Reworks Retire Content]` (title + opening paragraph) |
| **W1** | `[R: reports/WoW PoE2 MMORPG design lessons.md §FFXIV, GW2, and EVE run three incompatible bets on where balance work goes]` |
| **W2** | `[R: reports/WoW PoE2 MMORPG design lessons.md §PoE's gem-priority chains show behavior-changing composition without bespoke names]` |
| **W3** | `[R: reports/WoW PoE2 MMORPG design lessons.md §The complexity ceiling sits at player comprehension, confirming and sharpening Pattern P3]` |
| **W4** | `[R: reports/WoW PoE2 MMORPG design lessons.md §What this pass changes in the constitution]` |
| **W5** | `[R: reports/WoW PoE2 MMORPG design lessons.md §Conclusion]` |
| **CX1** | `[R: research_notes/WoW PoE2 MMORPG design lessons/computer_vs_tabletop_complexity_ceiling.md §Concrete "Computer-Only" Hidden Complexity]` |
| **CX2** | `[R: research_notes/WoW PoE2 MMORPG design lessons/computer_vs_tabletop_complexity_ceiling.md §Deliberate Simplifications Despite Computational Capacity]` |
| **CX3** | `[R: research_notes/WoW PoE2 MMORPG design lessons/computer_vs_tabletop_complexity_ceiling.md §Path of Exile: Does No Human GM Mean No Complexity Ceiling?]` |
| **CX4** | `[R: research_notes/WoW PoE2 MMORPG design lessons/computer_vs_tabletop_complexity_ceiling.md §Background-Resolved vs. Player-Facing Complexity]` |
| **CX5** | `[R: research_notes/WoW PoE2 MMORPG design lessons/computer_vs_tabletop_complexity_ceiling.md §Designer Decisions to Remove Complexity]` |
| **CX6** | `[R: research_notes/WoW PoE2 MMORPG design lessons/computer_vs_tabletop_complexity_ceiling.md §Synthesis]` |
| **MM1** | `[R: research_notes/WoW PoE2 MMORPG design lessons/mmorpg_design_broadly.md §Final Fantasy XIV's Tightly Controlled Job Design]` |
| **MM2** | `[R: research_notes/WoW PoE2 MMORPG design lessons/mmorpg_design_broadly.md §Guild Wars 2's Weapon-and-Trait-Based Openness]` |
| **MM3** | `[R: research_notes/WoW PoE2 MMORPG design lessons/mmorpg_design_broadly.md §EVE Online's Time-Based Skill Training]` |
| **MM4** | `[R: research_notes/WoW PoE2 MMORPG design lessons/mmorpg_design_broadly.md §Cross-Game Comparison]` |
| **MM5** | `[R: research_notes/WoW PoE2 MMORPG design lessons/mmorpg_design_broadly.md §Key Findings for Custom AI-Driven RPG Design]` |
| **PG1** | `[R: research_notes/WoW PoE2 MMORPG design lessons/path_of_exile_gems.md §How Does the Core Skill Gem + Support Gem Socketing System Work]` |
| **PG2** | `[R: research_notes/WoW PoE2 MMORPG design lessons/path_of_exile_gems.md §Concrete Examples of Support Gems That Fundamentally Change a Skill's Behavior]` |
| **PG3** | `[R: research_notes/WoW PoE2 MMORPG design lessons/path_of_exile_gems.md §How Does the Passive Skill Tree Work?]` |
| **PG4** | `[R: research_notes/WoW PoE2 MMORPG design lessons/path_of_exile_gems.md §How Do Ascendancy Classes Interact]` |
| **PG5** | `[R: research_notes/WoW PoE2 MMORPG design lessons/path_of_exile_gems.md §What Do Players and GGG Say About Build Diversity]` |
| **PG6** | `[R: research_notes/WoW PoE2 MMORPG design lessons/path_of_exile_gems.md §How Does GGG Handle Live Balance Patching?]` |
| **PG7** | `[R: research_notes/WoW PoE2 MMORPG design lessons/path_of_exile_gems.md §Is There Documented Discussion of Decision Paralysis]` |
| **PG8** | `[R: research_notes/WoW PoE2 MMORPG design lessons/path_of_exile_gems.md §Synthesis and Key Takeaways for RPG Design]` |
| **WT1** | `[R: research_notes/WoW PoE2 MMORPG design lessons/wow_talents_and_balance.md §Talent System Evolution]` |
| **WT2** | `[R: research_notes/WoW PoE2 MMORPG design lessons/wow_talents_and_balance.md §Number Scaling and Stat/Level Squishes]` |
| **WT3** | `[R: research_notes/WoW PoE2 MMORPG design lessons/wow_talents_and_balance.md §Live Balance-Patching Cadence and Process]` |
| **WT4** | `[R: research_notes/WoW PoE2 MMORPG design lessons/wow_talents_and_balance.md §Class and Specialization Reworks]` |
| **WT5** | `[R: research_notes/WoW PoE2 MMORPG design lessons/wow_talents_and_balance.md §Class Distinction Mechanics: Resource Systems and Global Cooldowns]` |
| **WT6** | `[R: research_notes/WoW PoE2 MMORPG design lessons/wow_talents_and_balance.md §Key Takeaways for Computer-Driven RPG Balance at Scale]` |
| **AP** | `[R: src/ability_pool.py]` (Feature 003 probe mechanism and fixtures) |
| **IR3** | `[R: specs/003-ability-acquisition-probe/implementation-results.md]` |
| **TC3** | `[R: specs/003-ability-acquisition-probe/contracts/tools.md]` |

The primary web URLs each finding rests on are listed in the source files. Where a chapter rule leans hard
on one precedent, cite the URL as well: the source file's line for that finding carries it. The
entries in Section 2 name the precedent so you can find it quickly.

### 0.2 Source-quality notes the authors must know

These bound how hard each finding can be leaned on.

- **Many primary pages were not fetched.** The researchers repeatedly hit 403/402/429 walls. The
  PoE wiki Modifiers/Tier pages, the Diablo Wiki Item Generation Tutorial, the Hades fandom wiki,
  the Defiance of the Fall and Azarinth Healer class pages, TV Tropes, and the RoyalRoad forums
  were all unreachable. Findings about those systems come from secondary summaries or search
  snippets **[F-secondary]** (A1 gaps, A2 gaps, L1 gaps, RG1 gaps).
- **Borderlands numbers were not directly verified.** The 35 part categories and 1,500–1,700 parts
  came from a search tool's summary of an unfetched page (A4 gaps).
- **No developer postmortems exist for the "table vs pipeline" framing.** The comparison of Hades,
  StS, Isaac, and RoR2 architectures is the researcher's analytical lens, not a developer's stated
  reasoning (RG5 gaps).
- **The LitRPG mechanics are fiction.** Delve's thresholds are rules *inside a novel*, not a shipped
  game. They are "implementable" but untested as play (L1, L2).
- **Only one rigorous LLM positioning study exists (ChatRPG, arXiv 2502.19519v2).** The commercial
  product claims (Friends & Fables, RoleForge, DungeonsDeep.ai) come from aggregator blogs (FP6 gaps).
- **The WoW report is the more polished of the two, but its dates contain an error.** It dates the
  fourth squish (Patch 12.0.0 "Midnight") to 2024, and its own inference "squishes recur every 4–6
  expansions" contradicts the dates it lists. See Section 4, T-R items.
- **Several findings conflict inside the research.** These cover PoE's tag-weight rule ("sum" vs
  "left-most most significant"), RoR2's coefficient range, and PoE2's node and ascendancy counts.
  Section 4 logs each one so no author quotes a wrong number.

### 0.3 The five theses that organize everything below [R3 synthesis of E0/E7/W0/W5]

1. **Gate, then fill.** Every successful generator in these sources separates *what kind of thing
   is possible* from *which specific one you get*. A low-cardinality categorical gate handles the
   first (source, manufacturer, god, tag, playstyle axis). A simpler selector handles the second
   (weighted roll, guaranteed pick, deterministic craft, cumulative counter, priority rank). Systems
   that tried one undifferentiated mechanism were later corrected toward this split: Diablo III's
   launch loot became Loot 2.0, and Borderlands 1/2's mixed parts became BL3's manufacturer-locked
   pools (E1, A1, A4).
2. **Bound the count, not the table.** Legibility comes from a fixed number of simultaneously active
   slots per object (PoE's 3+3 affixes, PoE2's 5 supports per skill, the Hades slots, HWFWM's 20).
   It does not come from a small design space (A2, E1, PG1).
3. **Compose by rule, name only the few.** Additive effects compose through shared pipelines (Isaac
   cache, RoR2 coefficients, StS hooks). Slot-claiming effects need one priority rank each (Isaac
   tear-replacers, PoE Pierce>Fork>Chain>Return). Hand-named combos are affordable only when keyed
   to a dimension the designer keeps small (Hades god-pairs) (E2, RG5, W2).
4. **Structure beats prose for adjudication.** Every narrative TTRPG surveyed keeps *some* discrete
   spatial state, and the one LLM system that tried pure prose broke: it narrated self-injury and
   hit the wrong targets. The fix was a structured tool boundary (E4, FP6). The Feature 003 probe
   says the same about content: the DM classifies onto closed categories, a tool computes the
   result, and residual error lives in embellished narration (IR3, TC3).
5. **Retirement is real, costly, and best avoided by never promising permanence.** A numeric squish
   only postpones the problem and retires nothing. Structural reworks retire content, but Blizzard's
   own research found they "put off far more people than it turned on." PoE's provisional league
   cycle avoids that cost by never granting permanence untested (W4, WT2, WT4, PG6).

---

## 1. Per-chapter findings

### 00 — Architecture (conventions, numeric scales, attribute list, tag-tree top levels, state model, tool surface, glossary, chapter contracts)

**00.1 Two-table data model: shared effect definitions referenced by content tables.** [F] Diablo II
stores affixes in `MagicPrefix.txt` and `MagicSuffix.txt`. Each affix lists *which stat, what range,
and which item types*, and references an ID in a separate **`ItemStatCost`** table that defines what
the stat actually *does*. The content tables say "which and how much"; one shared table says "what it
means" (A1). **Adopt [R3]:** give `data/` a single canonical `effects.yaml` (or equivalent). Every
ability template, item affix, adversary power, and class synergy bonus references an effect by `id`
plus parameters and never redefines the mechanic. This directly serves goal 2: one definition, one
adjudication, and no divergent re-narrations of "the same" effect. Chapters 05, 08, and 09 all
consume it, so ch 00 should own the contract.

**00.2 The identity layer and the magnitude layer never compete for an output slot.** [F] Three
precedents converge here, and this is the report's lead architectural finding:
- D2 Uniques and Sets are a *separate data structure* with 3–8 hand-picked properties. "There are no
  rules to the mods that can be on a unique."
- D3 Loot 2.0 places the Legendary Power in a reserved **Secondary** slot "specifically so it never
  competes with an item's Primary stat roll."
- Borderlands' manufacturer is a gate applied *before* part-rolling, so its signature behavior is
  guaranteed and never one outcome among many.

(E1, A1, A5.) **Adopt [R3]:** the state model gives every generated object (item, acquired power,
maybe an NPC gift) explicit **signature slot(s)** and **magnitude slot(s)** as separate fields with
separate rules. Signature content is looked up by category. Magnitude content is rolled. The report
also recommends that a P5-acquired ability "occupy its own reserved slot rather than rolling against
a character's regular stat growth" (E6). With P2 there is no longer "regular stat growth" (no
levels), so the live question has moved. Does an item- or acquisition-granted ability count against
P5's **hard total-slot ceiling**, or does it get a reserved slot class? See Section 4 T-12.

**00.3 Tag-tree top levels: classify before you weight.** [F] Every PoE mod first carries a **domain**
(what kind of entity it can appear on) and a **generation type** (prefix / suffix / corrupted-only /
always-applied). Only *then* do tag weights apply (A2). Base items carry an ordered tag list from
specific to general (example: `str_armour`, `body_armour`, `armour`, `default`), and "left-most tags
are treated as most significant" (A2). **Adopt [R3]:** each tag-tree node, and each content entry,
declares (a) its domain (which object types it can attach to: character evidence, ability, item,
adversary, location…) and (b) its ordered ancestry from specific to general. That ancestry list *is*
the constitution's hierarchy cascade [C:P5], and it gives a deterministic "most specific match
wins" rule wherever a weight or rule must pick one level. See 03.1 for the conflict between "sum"
and "left-most" in the source.

**00.4 Share one category vocabulary across all content types.** [F] Diablo IV's Tempering recipes are
"categorized by theme, e.g. 'Mobility,' the same categorization scheme used for the Codex of Power's
Legendary Aspects" (A1). RoR2 uses one `ItemTag` set (Damage / Healing / Utility / …) both for loot
eligibility (Category Chests) and for AI and copy restrictions (RG4). **Adopt [R3]:** a single tag
tree serves evidence (ch 03), abilities (ch 05), items (ch 08), and adversaries (ch 09). A shared
vocabulary is what lets an adversary's nature gate a loot pool *and* an absorbable-power pool *and*
evidence tags without a translation table.

**00.5 A closed trigger-hook vocabulary.** [F] Slay the Spire's cards, relics, and powers each subscribe
to a small, shared set of combat event hooks. BaseMod mirrors them as `OnCardUse`, `OnPlayerDamaged`,
`OnPowersModified`, `PostBattle`, `PostDraw`, `PostExhaust`, and `RelicGet`. "Synergy is discovered,
not authored," and the combat core is "the same five or six rules every turn" (RG2, E2). **Adopt
[R3]:** ch 00 should publish the complete, closed list of trigger points any passive or active
effect may key on. Candidates: `on_declare_action`, `on_roll_result(degree)`, `on_hit`, `on_miss`,
`on_take_damage`, `on_vitality_threshold`, `on_defeat_foe`, `on_turn_start/end`,
`on_scene_start/end`, `on_rest`, `on_condition_applied/removed`, `on_item_acquired`,
`on_tag_event`, `on_focus_spent`. With a closed list, the DM always knows *where* to check for
effects, and a new effect composes with every old one at zero pairwise authoring cost (RG5).
Chapters 05, 06, 08, and 09 all consume this.

**00.6 One modifier-evaluation pass in a fixed order.** [F] In Isaac, stat-modifying items write into
a shared `MC_EVALUATE_CACHE` recomputation. `AddCacheFlags` marks the affected stats and
`EvaluateItems` recomputes them. The ordering is explicit: "the stats for vanilla items and effects
are applied before the callback is fired for any modded effects" (RG3). **Adopt [R3]:** ch 00 or 01
defines one evaluation order for stacking modifiers, for example base → attribute → calling/tier →
equipped items → situational/positional → temporary conditions → caps/DR. The AI never has to
reason about pairwise stacking. It runs the pass.

**00.7 Two shared stacking-formula families.** [F] RoR2 uses exactly two stacking families across its
entire item pool. **Linear** is `f(x) = 1 + a·x`. **Hyperbolic** applies to percentage effects,
because "linear stacking would eventually lead to a 100% chance to trigger or 100% reduction"
(RG4). **Adopt [R3]:** every stackable numeric in `data/` declares its family: linear-capped or
hyperbolic. For reference only [R3, not in source]: RoR2's hyperbolic form is `1 − 1/(1 + a·x)`.
With a = 0.15 that yields 13.0% / 23.1% / 42.9% / 60.0% at 1 / 2 / 5 / 10 stacks. It never reaches 100%.

**00.8 A proc coefficient and a proc-chain terminator.** [F] In RoR2, "Effective Trigger Chance = Item
Chance × Proc Coefficient." Every ability has a coefficient. Damage-over-time effects have
coefficient **0.0**, so they "cannot themselves re-trigger on-hit items," which is "a single global
rule preventing infinite proc chains rather than a hand-authored exception per pair" (RG4). **Adopt
[R3]:** add a global rule that an effect *triggered by another effect* cannot fire trigger-hooks
itself (or does so at coefficient 0). That closes infinite-loop exploits, and it is exactly the
edge case an AI DM would otherwise adjudicate inconsistently (goal 2). Attacks may also carry a
coefficient, so that multi-hit or area attacks trigger on-hit effects at reduced odds.

**00.9 Bound the numeric scales from day one; a squish is a confession.** [F] WoW squished stats four
times: 2014 (~96% stats, ~92% health), 2018, 2020 (also levels 120→50), and a fourth dated 2024 in
the source. Each preserved relative power exactly: "a Fireball that previously hit for 450,000 out
of 3,000,000 health (15%) now hit for 30,000 out of 200,000 (still 15%)." None of them retired
anything. Moving to "linear scaling models" in 2014 did not prevent later squishes. A 2011 developer
blog cited nearing the signed 32-bit limit (~2.1 billion) (WT2, W4). WT6's takeaway: "commit to
either a bounded scaling system (hard caps, linear or inverse scaling) or accept periodic content
consolidation (squish-like resets)." **Adopt [R3]:** the d20 core is already bounded. Ch 00 should
state hard ceilings for every modifier source and for totals (e.g. a maximum total bonus to a roll
from all sources), because P2's tiers add "potency" with no level cap on how long a campaign runs.
The sandbox is open-ended, so unbounded tier growth *will* inflate. [C:VI] already forbids counting
a squish as retirement.

**00.10 Classify state as background-resolved or player-facing, for "told vs handled" rather than for
a budget.** [F] Threat tables (1 damage = 1 threat, a 5.0× tank multiplier, healing threat halved
and divided by observer count), crowd-control diminishing returns, stat diminishing returns above
30%, and PoE's whole damage stack all run invisibly with zero player cost (W3, CX1, CX4). The
research line is "background complexity can be unlimited" [I]. **Adopt:** constitution P3 still
says a spec "MUST classify each piece of tracked state as background-resolved or player-facing."
The BRIEF removes the *budget* on the player-facing side, not the classification. Keep the
classification as the tool for deciding what the codex shows by default versus what the DM simply
applies (goal 1: tell the player what widens their options). See Section 4 T-7.

**00.11 The tool boundary: the DM classifies, the tool computes.** [F] In the Feature 003 contract,
the model decides *when* to call `grant_ability` and supplies `source_archetype` and
`acquisition_method` from closed sets. It "never supplies, and never narrates into existence,
*which effect template* results — that's computed entirely by `ability_pool.resolve_ability_grant`."
An unknown category fails validation "the same way an out-of-range `roll_check` argument would," not
through a silent fallback. There is deliberately *no* tool for "does this count as an acquisition at
all," which stays base-model judgment (TC3). The live result was 6/6 correct classifications (IR3).
**Adopt:** this is the proven template for every generator tool: loot rolls, crafting results,
evidence capture, and positional updates. The DM's judgment step is always *classification onto a
closed set*. Content selection is always `[D]`.

**00.12 Structured combat parameters.** [F] ChatRPG v2 fixed its prose-combat failures by moving
resolution into a "Battle tool" that takes "attack order, hit chances, and damage severity for each
exchange" as structured JSON, with "few-shot prompting examples baked into the tool description"
and a dedicated "Narrator" agent for combat (FP6). **Adopt [R3]:** the ch 00 tool surface should
include an attack/exchange resolution tool whose required arguments are *explicit target id(s)*,
the attack's source ability id, and the relationship-state preconditions. It should also carry
worked examples inside its own description, per the ChatRPG few-shot finding. The current tools
(`roll_check`, `get_state`, `update_resource`, `set_fact`, `grant_ability`) have no target field.
The ChatRPG failure mode was literally *target misidentification*. (→ 06.1, 06.2.)

**00.13 A per-layer power budget, so no single layer eats the others.** [F] PoE builds combine at least
4 independent vectors: base class, ascendancy, skill gem + supports, and passive tree, plus jewels
(PG8). In the current PoE2 league, jewels became so strong that "if every build simply collects as
many jewel sockets as possible, the game risks losing … creativity" (PG5, W2). **Adopt [R3]:** ch 00
should state the intended share of a character's total power carried by each layer: attributes
(ch 02), calling tiers (ch 04), abilities (ch 05), items (ch 08), and situational factors (ch 01/06).
It should also cap each layer's maximum contribution to any single roll, so that for example items
can never exceed +N. This is the audit hook P11 wants, applied at the layer level.

**00.14 Attribute-list inputs, which are thin.** [F] Few sources speak to attributes:
- PoE2 attributes are Str/Dex/Int. Characters "start in the middle" of the tree at a node "defined
  by attribute and archetype alignment," and travel nodes are selectable as +5 of one attribute
  (PG3).
- Azarinth Healer's base class grants a flat package of +10 Vitality, +5 Strength, +5 Dexterity,
  +10 Intelligence, +10 Wisdom (L2 gaps).
- Delve gates a class on a **stat ratio**: Dynamo requires Clarity ≥ 5× Focus (L1, L2).
- Ironsworn's stats (heart, shadow, wits, iron, edge) are chosen *by fictional approach* (FP4).

The Ironsworn model is the most useful for ch 00/01/02 [R3]: attributes as approach-keyed modifiers
("how you go about it"). That fits the constitution's framing, "how good are you at broad categories
of action" [C: Sync Impact Report, ability scores]. Naming note: Delve's "Focus" is a *stat*, while
this project's Focus is the shared *resource* [C:P9]. Avoid confusion in the glossary.

**00.15 Tight systems help prediction; loose systems need richer adjudication.** [F] Lostgarden:
"tight" systems let a participant "broadly signal intent, capabilities and internal mental state,"
while "loose" systems present "a large number of options" (MM4). MM4 infers that tight balance
(FFXIV) "works well … when the AI needs to enforce strict rules," while loose balance (GW2) "requires
more sophisticated AI: the system must track and respond to emergent builds the designer didn't
explicitly anticipate." **Implication [R3]:** P5's emergent builds are by definition loose. The
rich-substrate approach [C:P3 sixth pass] is the compensating mechanism, because the AI must be
able to reach for an existing rule when an unanticipated build shows up.

**00.16 Glossary terms these sources introduce** (so every chapter uses one meaning): *pool gate*,
*fill mechanism / fill quality*, *signature (identity) slot*, *magnitude slot*, *affix*, *tier*,
*mod group* (mutual exclusion set), *per-object slot cap*, *priority rank*, *trigger hook*, *proc
coefficient*, *stacking family*, *evaluation pass*, *relationship-state* (range band / engagement /
flank / cornered), *position* and *effect* (if ch 01 adopts Blades' axes), *clock*, *consolidation*
(named merge), *fold-into-base*, *fork-replacement*, *provisional / trial window*, *promotion*,
*squish* (a non-retirement), *structural retirement*, *conferral* (authority-granted calling),
*circumstantial shift*.

---

### 01 — Resolution (capability gate, when to roll, DC, modifiers, degrees, P17, compound/extended/opposed/group, help, advantage)

**01.1 Position and Effect: two severity axes set before the roll from fiction alone.** [F] In Blades
in the Dark, the GM sets Position (Controlled / Risky / Desperate: "how bad can things go") and
Effect (Limited / Standard / Great: how far short of, exactly at, or beyond the goal) *after* the
player declares the action and *before* the roll. The default is **Risky/Standard**, "modified by the
action being used, the strength of the opposition, and the effect factors." Spatial and tactical
factors are folded straight into Position: outnumbered, no cover, choke point, sniper vantage (FP1,
E4). **Adapt [R3]:** P8's four degrees answer *which band* a result falls in. A Position-like
dial answers *how severe the failure band's consequences are*, and an Effect-like dial answers *how
much a success accomplishes*. Two uses:
1. It is the natural **telegraph** for lethal risk (BRIEF §4 locked decision): the DM must announce
   "Desperate" before a roll that can kill. See 07.1.
2. It gives the DM explicit criteria (`[J]` with a table) instead of raw judgment for consequence
   size.

**01.2 Player levers on the severity axes are a freedom mechanic.** [F] In Blades, players can "Push"
(spend Stress) for better Effect, or *trade Position for Effect* by worsening one step to improve
the other (FP1). **Adapt [R3]:** a player-declared "I take the bigger risk for the bigger payoff"
lever serves goal 1. It gives creative players a way to buy ambition, and it maps onto spending
Focus [C:P9]: "spend Focus to push Effect one step."

**01.3 Partial success does not negate the attempt.** [F] Blades GM guidance: on a 4/5 (partial),
do not say "the enemy escapes." The enemy ends up cornered, but the PC pays a complication, such as
the enemy grabbing their gun (FP1). In PbtA, a partially successful dodge can leave the orc between
the PC and the party (FP3). **Implication [R3]:** the current d20 resolution has success, failure,
and two crits, with no "success at a cost" band. Ch 01 should decide whether failure *near* the DC
(e.g. within 1–4 below) becomes "success with complication." The research strongly favors cost over
negation for positioning-type actions, and P16 (no dead ends) supports the same direction.

**01.4 A flat situational modifier worth ±3.** [F] Mörk Borg handles flanking and high ground as a flat
**+3 / −3** to attack or dodge rolls, "nothing more," and reviewers praise it for "online play"
(FP5, E4). **Arithmetic [R3]:** on a d20, ±3 moves success odds by 15 percentage points while the
DC stays within reach (target between 4 and 20), which is 60% of one step on the current DC ladder
(steps are 5 apart). That makes a clean candidate for the positional/situational modifier unit.
Compare how ch 01 prices advantage-type mechanics.

**01.5 The approach picks the attribute.** [F] In Ironsworn, how a fight starts decides the stat:
Enter the Fray rolls **+heart** when facing off, **+shadow** when moving on an unaware foe or striking
without warning, and **+wits** when ambushed. Strike rolls **+iron** in close quarters and **+edge**
at range (FP4). **Adapt [R3]:** ch 01's "which modifier applies" rule can be *approach-keyed*: the
player's described approach selects the attribute. That rewards creative framing (goal 1) and gives
the DM a deterministic mapping from description to attribute (goal 2).

**01.6 Degree drives the next step: tempo moves with result quality.** [F] Ironsworn: a strong hit on
Enter the Fray gives +2 momentum and initiative. A strong hit on Strike gives +1 harm and keeps
initiative. A weak hit inflicts harm but *loses* initiative (FP4). **Adapt [R3]:** degree of success
can move tempo or initiative, not only damage (→ 06.5).

**01.7 One declared action is not many effects.** [F] WoW's Global Cooldown exists so that no player
can "combine multiple effects into one action." Without it, "the decision is easy because there is
none — for example, a druid could activate their defensive ability and start casting a healing spell
for the tank simultaneously" (CX2, W3). [F, BRIEF §7] The live probe DM throttled an attempt to
compress 10 attacks into one action and raised the DC to 25. **Adopt [R3]:** ch 01's compound-action
rule has independent MMO precedent. One declared action resolves at most one *activated* effect
unless an ability explicitly licenses bundling ([C:VII]: bundling itself needs a license). The
**GCD reversal** (→ 06.4) warns that a bundling limit must create a decision, not merely slow things
down.

**01.8 Intent is an attempt, never an outcome.** [F] Feature 003's first scripted scenarios narrated
a kill as the player's action. The live DM correctly *rolled*, got a critical failure, and narrated
the player being mauled, "the opposite of the scripted premise," and so did not call `grant_ability`
(IR3). **Implication:** this is P8 plus [C:VII] working as designed, and ch 01 should cite it as the
worked edge case: "the player's narration of success is a declaration of intent. Resolution decides
the outcome, and downstream mechanics (loot, evidence, grants) fire only on the *resolved* outcome."
It also tells ch 03: a `tag_event` for "decisive kill" can only be recorded from a resolved result.

**01.9 Resolve an ambiguous target before rolling, not after.** [F] ChatRPG v1 produced "characters
stumbling or self-injuring when the system failed to identify an appropriate target," and a simple
kick came back as an "unjustified self-inflicted trip" (FP6). **Adopt [R3]:** add a resolution
precondition. Any action whose target is not uniquely determined by relationship-state plus the
player's words must have its target resolved *first*: by the only legal candidate, by a stated
default (e.g. the nearest engaged foe), or by asking. Self-harm is never narrated unless a resolved
result (crit fail) licenses it.

**01.10 Modifiers evaluate in one pass.** → 00.6 (Isaac cache order). Ch 01 owns the concrete order,
if ch 00 delegates it.

**01.11 An adjudication vocabulary for unanticipated actions.** [F] PbtA's MC moves (e.g. "separate
them") are a generic toolkit used on a miss or partial to reshape the situation. "All GM moves put
the characters in a position to make a choice and act" (FP3). **Adapt:** a closed list of DM
consequence-moves is P3-style substrate the AI can reach for (→ 12.3). It pairs with P16.

**01.12 Group and help actions: one source.** [F] Mörk Borg's "skirmish" initiative has "the whole
party act in the same round against the opposition" (FP5). This is thin for help rules in a
single-player game with companions. See the Section 5 gaps.

---

### 02 — Character (creation, attributes, origins P4, birth variance and deferred reroll P1, baseline floor P2, starting kit)

**02.1 Lock the base identity, keep the specialization swappable.** [F] PoE2: "A character's base
Class cannot be swapped, but their Ascendancy can be changed at a later stage" (PG4). The WoW report
explicitly flags this as relevant to P4: "one axis (ascendancy) can stay flexible while another (base
class) stays locked, rather than treating 'locked at creation' as all-or-nothing" (W2). **Implication
[R3]:** ch 02's origin choices ([C:P4] locked stat-quantity-versus-freedom trade-off) can be the
locked axis. Ch 04's calling specializations may be re-derivable.

**02.2 A player-controlled reroll of one non-signature property has a precedent.** [F] In Diablo III,
"Enchanting lets a player reroll one non-legendary affix on demand, but not the legendary power
itself" (A1). **Link [R3]:** [C:P1] requires that post-creation variance "MUST NOT be auto-applied"
and that the player "MAY defer it and gamble on a later reroll," which the constitution calls "a
deliberate departure from every source researched." D3's Enchant is a partial precedent: player-chosen,
one property, signature protected. Ch 02 can model its deferred reroll this way: reroll exactly one
non-signature variance result, and the signature/birth identity is never rerollable.

**02.3 An origin can express a pathway without a menu.** [F] EVE's Academy offers "premade Skill Plans
… for all four Academy pathways: Explorer, Enforcer, Industrialist, and Soldier of Fortune," while
"players *begin* with divergent training paths from day one" (MM3). PoE2 "all classes now start in
the middle … with the starting node defined by attribute and archetype alignment" (PG3). **Adapt
[R3]:** an origin can seed *initial evidence tallies or tag affinities* (a head start toward certain
callings) instead of granting a class. That keeps [C:P5] emergence (no menu class) while giving
day-one direction.

**02.4 Baseline floor (P2): the first recognition is a threshold, not day one.** [F] Defiance of the
Fall grants a character's **first class at level 25**, "mainly based on achievements and
experiences" (L1, L2). Wandering Inn classes appear after a *sustained pattern* (L1). GW2's
non-trinity gives "every player the simple means to defend themselves" (MM2, W1). **Implication
[R3]:** there is precedent for a class-less opening period, and none of these sources supplies the
floor itself. That makes [C:P2]'s floor the ruleset's own design work. The GW2 precedent argues the
floor must include *self-sufficiency*: a solo character must be able to defend, heal minimally, and
escape without any calling. The fixed basic-action tier ([C:VII]) is part of that floor.

**02.5 Breadth versus depth at creation: the Randidly trade-off.** [F] In *The Legend of Randidly
Ghosthound*, a classed character "can level up but is capped in the number of skills they can learn,
while a classless character … can learn unlimited skills but cannot level up conventionally." The
source rules this out as an aggregate-to-class precedent (L1). **Relevance [R3]:** it is still a
clean statement of [C:P4]'s breadth-versus-competence decoupling. Useful as an analogy for the
unrecognized state (broad and weak) versus the recognized one (narrow and strong).

**02.6 Starting kit and "smart" loot.** [F] Diablo III's Smart Loot "guarantees class-appropriate main
stats" (A1). **Adapt [R3]:** the starting kit can be origin-appropriate by construction. Whether
*ongoing* loot should bias toward the character's tags is a real tension (→ 08.14, Section 4 T-9).

**02.7 Starting abilities come from source and method, not a menu.** [F] AP / IR3 show the
source-gates-pool shape producing concrete starting-kit-sized content: 3 templates per archetype, one
per flavor_bias. **Adapt [R3]:** P1's birth variance could itself be a gate/fill roll. The origin is
the pool gate, and a birth roll is the fill.

---

### 03 — Tags & Evidence (vocabulary hierarchy, `tag_event` capture, tallies, weighting, recency)

**03.1 Hierarchical tag membership, and the most-specific-wins rule.** [F] PoE base items carry an
ordered tag list from specific to general (`str_armour`, `body_armour`, `armour`, `default`). Mods
list a spawn weight per tag. The generator "collects all tags on the item, sums the matching
weights," and "discards any mod whose total weight resolves to zero" (hard eligibility filter under
soft weighting). "Where an item has multiple applicable tags, left-most tags are treated as most
significant" (A2). **Internal inconsistency:** "sums the matching weights" and "left-most most
significant" are two different rules, and the researcher flags "left-most" as unverified (A2 gaps).
**Adopt [R3]:** [C:P5] already requires that "a narrow event counts as evidence at every level of its
hierarchy at once." That is the *cascade* half, and PoE's ordered ancestry is its item-side
precedent. For any rule that must pick *one* level (e.g. which weight or threshold applies), the
deterministic choice is **most specific matching level wins**. It is simpler for the AI than summing,
and it prevents double-counting.

**03.2 Tags double as unlock counters.** [F] Isaac's `tearsup` tag marks every tear-rate item and is
used "for unlock-tracking purposes (e.g., contributing toward the 'Lachryphagy' trinket unlock
condition tied to collecting enough tear-rate-up items in a run)" (RG3). **Relevance:** this is a
shipped precedent for exactly this project's move of **tallying tagged events toward an unlock
threshold**. Classification metadata becomes the progression counter.

**03.3 Tags gate compatibility as well as counting.** [F] PoE: "Gem compatibility is determined by
tags on skill gems … Greater Multiple Projectiles Support only works with Projectile skill gems"
(PG1). RoR2's `ItemTag` set (Damage, Healing, Utility, AIBlacklist, BrotherBlacklist,
OnKillEffect, CannotCopy) is used for eligibility and restrictions, not for trigger resolution
(RG4). **Adopt [R3]:** the same tag vocabulary should answer "can modifier X apply to ability Y"
(ch 05), "can item X drop from source Y" (ch 08), and "can adversary power X be absorbed" (ch 04/09,
the `CannotCopy` analog). One vocabulary with three uses.

**03.4 Two evidence kinds: judged events and mechanically counted events.** [F] Delve's **Primary
Requirement** is a rank-count within a category, such as "at least 4 skills at or above rank 5" in
Offensive Auras, or a stat ratio. Its **Secondary Requirement** is a cumulative action counter: "≥50
kills via Offensive Auras," "mitigating at least 1,000 total damage points for self or allies,"
"≥5,000 mana spent through Aura Metamagic," "≥1,000,000 total mana recovered" for Legendary Dynamo
(L1, L2, E3). **Adapt [R3]:** this project's evidence splits along the same line.
- **(a) Judged tag events** (`[J]`, [C:III]): "did this moment count, and toward what tag?" Examples
  are a merciful choice, a clever ruse, an oath kept.
- **(b) Mechanically counted events** (`[D]`): counters the engine increments from tool results with
  no judgment. Examples are Focus spent *through* abilities carrying tag X, damage prevented by
  tag-Y abilities, foes defeated using tag-Z abilities, crits with weapon family W, and scenes
  resolved without violence.

Class eligibility can require both, mirroring Delve's primary and secondary. The (b) counters are
fully auditable, which is the P13 safety story, and they shrink the judgment surface [C:P5 sixth
pass, "the actual safety net is the three-valued policy"].

**03.5 Diversity counters.** [F] Delve's Dynamo has secondary requirements "around recovering mana and
having **diverse kill types**" (L1). **Adapt [R3]:** a *count of distinct values* (distinct source
archetypes defeated, distinct tags evidenced) is a third counter shape. Useful for hybrid and
generalist callings, and for resisting grinding.

**03.6 Keep the axes that key thresholds at low cardinality.** [F] Delve's axes (Offensive Auras,
Defensive Auras, Aura Metamagic, the Clarity/Focus ratio) are "a small, fixed, author-controlled set
— the same low-cardinality-keying trick Hades uses for its Duo Boon table — which is what keeps the
threshold table tractable even as the number of individual skills a character can hold grows without
bound" (E3). "A spec adopting this mechanism MUST NOT key thresholds off the full, ever-growing
ability/monster list" (E6 proposed text, now in [C:P5]). **Convergent cardinalities [R3, from
sources]:** Hades 8 gods, Hades II 9, EVE's 4 academy pathways, RoR2's 3 chest categories
(Damage/Healing/Utility), the probe's 3 flavor_biases (defensive/utility/offensive), and Delve's ~4
example categories. **Recommendation [R3]:** keep the top-level tag branches in single digits (6–9).
That caps possible hybrid branch-pairs at C(k,2) = 15–36 (→ 04.9).

**03.7 One counter per candidate class, evaluated independently.** [F] Threadbare's protagonist holds
"a large roster of classes (Greater Toy Golem, Cave Bear, Ruler, Tailor, Model, Necromancer, Duelist,
Animator, Enchanter, Golemist, Scout, Smith, Sculptor, and Shaman)," which implies "the underlying
tracker … would need one counter per candidate class rather than one shared melee/magic axis" (L1,
L2). **Link:** this is the constitution's specialist rule ("evaluated against its own threshold
independent of every other class's threshold") [C:P5 sixth pass]. Threadbare is the fictional
existence proof that independent per-class tracking yields many concurrent identities, so a hard cap
on *concurrent recognized callings* is needed (→ 04.12).

**03.8 Significance gating is judgment, and the sources agree.** [F] No LitRPG source exposes a
significance filter except Delve's raw counters. Wandering Inn and Defiance are "narratively opaque"
(L2). [C:P5 sixth pass] already resolved that significance is base-model judgment. **Nothing in these
sources contradicts it.**

**03.9 Anti-grinding: diminishing returns and reset windows as precedent.** [F] WoW crowd-control DR
halves each successive application's duration "until reaching 1/16th duration (PvE) or full immunity
after 2 applications (PvP), with a 16-second reset window." Stat DR makes "secondary stat scaling …
progressively less valuable after 30% stacking," introduced "specifically to limit what players could
stack" (CX1, W3). **Adapt [R3]:** none of the class sources address grinding. Delve's 50 kills would
reward it. An anti-farming rule is needed for the `[D]` counters, and WoW's DR shape is the
template. Repeated identical evidence within one scene, or against trivial opposition, counts at
diminishing weight (1, ½, ¼, …, then 0) and resets per scene. Judged evidence (a) is already
protected by the significance judgment.

**03.10 Recency: the sources split.** [F] Delve's counters are cumulative, with no decay (L2). EVE's
skill points are "never lost … unless you choose to extract them" (MM3). On the other side, Wandering
Inn relabels on *changes* in behavior (specialization, advancement, circumstantial shift). Azarinth
Healer shows a label diverging from actual playstyle, "a useful negative/contrast case for 'does the
label track the aggregate behavior'" (L4, L1). **No source weights recent evidence over old.** This
gap is logged in Section 5, and the tension (cumulative versus drift-tracking) is in Section 4 T-8.

**03.11 Re-evaluate at checkpoints, with an escape valve for dramatic moments.** [F] Wandering Inn
class changes "usually happen at ten-level intervals," with "off-classes" as exceptions for
"sufficiently dramatic shifts" (L2, L4). **Adapt [R3]:** with no levels, the checkpoint needs a
replacement clock: per rest, per session, per N `tag_events`, or per story milestone. A crisis moment
can also force an off-schedule evaluation, which matches [C:P2]'s "crystallized by a specific,
narratively-significant moment." This belongs in ch 03 (when tallies are checked) and ch 04 (what
the check does).

**03.12 A spend-channel tag for Focus.** [F] Delve counts "mana spent **through** Aura Metamagic,"
which ties resource spend to a category (L1). **Adapt [R3]:** because Focus is unified [C:P9],
tagging *which ability's* Focus spend occurred gives a free `[D]` evidence stream per tag. It costs
nothing extra to track and cannot be fudged by narration.

---

### 04 — Recognition & Growth (callings, specialist + hybrid, scoring, grant/offer/abstain, tiers & crystallization, provisional + consolidation VI, gated special traits)

**04.1 Delve's dual-tier threshold.** [F, detailed] A **Primary Requirement** gates eligibility: a
category rank-count ("≥4 skills at rank ≥5") or a stat ratio ("Clarity ≥ 5× Focus"). A **Secondary
Requirement** decides when the gated class actually triggers: a cumulative counter ("≥50 kills via
Offensive Auras"; "≥1,000 damage mitigated"; "≥5,000 mana via Aura Metamagic"). Higher tiers use
extreme totals ("Legendary Dynamo": all stat points in Clarity *and* ≥1,000,000 mana recovered).
Named tier families are "Remedial" → "High" → "Legendary." Classes carry rarity labels ("Dynamo
(Rare)"). The system is "deterministic and transparent once unlocked … but opaque in advance" (L1,
L2, E3). **Adopt:** this is [C:P5]'s mandated dual-tier structure. What the chapter must add:
(1) the axes, meaning the tag levels (→ 03.6);
(2) the counter kinds, judged versus counted (→ 03.4);
(3) numbers scaled to this game's event rate (Section 5, G-2);
(4) the scorer that turns threshold proximity into a per-candidate confidence (Section 4, T-4).

**04.2 Five grant paths, all fiction-voiceable.** [F] Wandering Inn documents several:
- **Action-based acquisition:** sustained behavior. Erin gets [Innkeeper] "after cleaning up and
  running an abandoned inn."
- **Authority-based grant:** "a ruler with the right class/authority can hand a class directly to
  someone, e.g., an Emperor granting [General] to a character with no prior action-history
  prerequisite," which the source "notes is a separate mechanism from playstyle-driven emergence."
- **Specialization:** a [Warrior] focused on spears becomes [Spearmaster].
- **Advancement:** [Tactician] becomes [Strategist].
- **Circumstantial shift:** a permanently injured [Warrior] becomes [Wounded Warrior].

(L1, L4.) **Adapt [R3]:** the BRIEF's locked fiction voicing ("a mentor's acknowledgement, an oath
sworn, a title people start using, an order that seeks you out, a power that awakens in a moment of
crisis") maps onto these paths almost one to one. Action-based means a title people start using.
Authority-based means an order that seeks you out or a mentor's acknowledgement. Advancement and
specialization mean a deepened tier, sworn at crisis. Circumstantial shift means an awakening or
reshaping after injury or catastrophe. **Tension:** an authority-based grant with *no* action
prerequisite conflicts with [C:P5] ("class … derived … never an independent system that hands out an
ability list"). Resolution option [R3]: conferral may *offer* a calling as a **provisional**
([C:VI]) calling whose continuation still requires evidence, and it never grants abilities outside
the slot system. See Section 4 T-13.

**04.3 Consolidation (named hybrid merge) and its missing trigger.** [F] Wandering Inn: "[Warrior] and
[Strategist] class can merge to form a [Commander] class." One character's [Princess] + [Warrior] +
[Barmaid] + [Beast Tamer] + [Carer] + [Tactician] consolidated into **[Worldly Princess]**, six into
one. Consolidation requires a secondary class to be advanced "sufficiently to inform" the primary,
"a plurality/threshold-based merge rather than an even 50/50 split rule" (L3, E3). **No source in any
series states a numeric tie-break or merge trigger.** "This piece must be authored fresh, not
imported" (E3, E5, E7, L3 gaps). **Two lessons for ch 04 [R3]:**
- Consolidation is **also a Principle VI mechanism**: six labels retire into one. It is "structural
  retirement … folding a mechanic," which [C:VI] says counts.
- The merge trigger must be original design. An ownership-free proposal to test: a hybrid becomes
  *eligible* when each constituent branch independently meets a **lower** threshold (for example
  X% of its specialist threshold). It is *offered* (never auto-granted, per [C:P5] "surfacing a named
  hybrid candidate … letting the player choose") when neither constituent's lead over the other
  exceeds Y. Simulate before committing (→ Section 5 G-1).

**04.4 Hybrids must be reachable without deep single-track investment (Cataclysm).** [F] Cataclysm's
rule of 31 points in the primary tree before branching produced "even more cookie cutter builds" and
"was especially punitive for hybrid classes that couldn't effectively leverage their versatility until
much higher levels" (WT1). **Warns against [R3]:** a hybrid threshold of "both specialist thresholds
fully met." That makes hybrids strictly later than specialists and punishes mixed play. Hybrid
thresholds should require *meaningful* evidence in two branches (per [C:P5]), below full specialist
depth in either.

**04.5 Forced specialization through a cap works when it bites across trees.** [F] In original WoW,
players "aimed for 31-point capstone talents but couldn't reach two capstones, forcing meaningful
specialization" (WT1). **Link [R3]:** [C:P5]'s hard total-slot ceiling plays the same role. With a
tight enough cap, a character can reach top tier in only one or two callings, so specialization
comes from the budget rather than from an audit ([C:P15]'s idea without real time).

**04.6 Tier rewards must be capabilities, not filler.** [F] The original WoW trees suffered from
"'filler talents' — many talents requiring five points for modest stat bonuses (e.g., increased
critical strike chance)." Bloat "wasn't solved by reducing total talent points; it was solved by
fundamentally restructuring the system to remove passive stat-stacking talents." Dragonflight
"removed the 'five-point talents'" (WT1). **Adopt [R3]:** each tier crystallization under [C:P2]
should grant a *new license* ([C:VII]) or a *behavior-changing* composite ([C:P6]), not "+1 to X."
That keeps growth meaningful and helps bounded numbers (→ 00.9).

**04.7 One of three per tier: a precedent for the offer tier.** [F] Mists of Pandaria reorganized
talents into "six tiers of three choices each," one choice per tier every 15 levels. "Choices in one
tier no longer affected choices in any other" (WT1). Warlords added a seventh tier (21 talents).
**Arithmetic [R3]:** 3^6 = 729 and 3^7 = 2,187 distinct builds from 18 or 21 authored talents. That is
[C:V]'s closed-combinatorics claim in live-service form. **Adapt:** a crystallization "offer" could
present up to 3 options (for example 3 candidate abilities from the calling's bounded pool), which
fits [C:P5]'s offer tier and [C:P1]'s "player may defer."

**04.8 Gate deeper tiers on invested count.** [F] Dragonflight blocks row 5+ "until spending eight
points" and row 8+ "until spending twenty points" (WT1). **Link:** this is the tier analog of Delve's
secondary counter. Tier N+1 requires cumulative evidence ≥ threshold(N+1), with thresholds rising
non-linearly (8 → 20 is 2.5×).

**04.9 Size the hybrid table by C(k,2) and key it to branches.** [F] Hades' ~30 Duo Boons are keyed
to god pairs: 8 gods give C(8,2) = 28 pairs. Hades II has 37 duos against C(9,2) = 36 pairs, "roughly
one flagship combo per god-pair." The low-cardinality keying makes the hand-curated table tractable
(RG1, RG5, E2). **Adopt [R3]:** hybrid callings key to *pairs of tag branches at a fixed hierarchy
level* (for example top-level or second-level). Maximum table size is then C(k,2). **Nuance
(Section 4 T-5):** the constitution's "sparse" language is satisfied at the *pair* level by Hades II's
near-complete coverage. "Sparse" should be read as "never the Cartesian product of individual
abilities or tags at every level," not "few branch pairs." Authoring one hybrid per plausible branch
pair and *explicitly declaring* implausible pairs as "no hybrid" is consistent with the evidence.

**04.10 Hybrid prerequisites name specific members, with exceptions and exclusions.** [F] "Most Duo
Boons require exactly one prerequisite boon from each god; one boon (**Vengeful Mood**) is a
documented exception requiring three." There are also hand-authored exclusions: "Cold Embrace and
Crystal Clarity can't be combined" (RG1). **Adapt [R3]:** a hybrid entry's schema needs a prerequisite
list (default one qualifying tag per branch, overridable), an optional exclusion list, and a
`requires_count` override.

**04.11 Consolidation and circumstantial shift can change the label without shipping new abilities.**
[F] [C:P5] makes the class label "derived … computed over that combinatorial state." Wandering Inn's
relabels ([Wounded Warrior]) show a label tracking circumstance (L4). **Implication [R3]:** a label
change is cheap and fictional. The *mechanical* change (a synergy bonus) is the only part that needs
Principle VI handling. Ch 04 should separate "label recomputed" (`[D]`, frequent) from "bonus changed"
(a telegraphed boundary event).

**04.12 Cap concurrent callings.** [F] Azarinth Healer uses "a **dual-class-slot** system where 'every
skill, class, and ability can evolve'" (L1). Threadbare accumulates 14 or more (L1). Wandering Inn
consolidates many into one (L3). **No consensus number exists** (Section 5 G-23). **[R3]:** a hard cap
(for example 2 or 3 recognized callings at once), with consolidation as the release valve when a
third would be recognized, matches Azarinth's dual slot and Wandering Inn's merge, and it keeps the
hybrid-table lookup bounded.

**04.13 "Opaque in advance, legible once crossed" versus hidden mechanics.** [F] Delve surfaces the
unlocked option "by name with the qualifying numbers implied," yet "a character doesn't necessarily
know a given hidden class exists." Wandering Inn is "semi-transparent: characters know classes exist
and can recognize when they've gained one, but cannot always predict exactly when/how." Defiance is
"opaque/retrospective" (L2). **Decision needed:** the codex [C:P7] is out-of-fiction (BRIEF §4). Does
it show progress toward *unrecognized* callings? Goal 1 argues for some visibility, so the player can
pursue an identity on purpose. The "hidden class" pleasure argues for opacity. The research supports
a middle option: show recognized callings and their tier thresholds fully, and show only *nearness*
(not identity) for callings not yet surfaced. See Section 5 G-16.

**04.14 Rework cost: don't change a recognized identity under the player.** [F] Survival Hunter's
conversion to melee (Legion, 2016) split the community into "revert" and "refine" camps "for at least
two full expansions." By 2017 Hazzikostas conceded "execution needs work but we're committed." Blizzard's
own research: "large-scale reworks of classes, especially rework after rework, put off far more people
than it turned on" (WT4, W4). [C:VI] already requires budgeting this cost "by bundling retirement into
infrequent, clearly-telegraphed boundary points." **Adopt [R3]:** a recognized calling's identity and
granted abilities change *only* at telegraphed boundary events: tier crystallization, consolidation, a
player-invoked respec, or a crisis awakening. They never change through continuous drift or DM
reinterpretation, and a circumstantial shift is *offered*, not imposed.

**04.15 Class fantasy beats raw parity.** [F] WoW's successful Dragonflight and War Within reworks
"restored class fantasy," and WT4 infers that "identity-driven design is more sustainable than pure
mathematical optimization" (WT4, WT6). FFXIV's tight parity produced "mechanical homogenization"
("prioritized perfect balance at the expense of job identity"; Dark Knight lost MP management,
Astrologian's cards were simplified, Scholar lost DPS spells, Samurai lost Kaiten) (MM1, W1).
Players want "low skill floors and high skill ceilings," with Black Mage as the model (MM1).
**Implication [R3]:** each calling needs a *distinct fantasy mechanic* (a synergy bonus, a cadence
quirk, a Focus-generation trigger) even when that costs perfect balance. Single-player removes the
multiplayer fairness pressure that drove FFXIV to homogenize.

**04.16 Provisional-by-default (league cycle) applied to callings and tiers.** [F] PoE leagues run
three months, introduce "exactly one new mechanic," and then GGG will "integrate … rework, or discard"
(PG6, W4). "Retirement of a *failed* mechanic never triggers the sunk-cost backlash retirement of an
*entrenched* one does, because players were told up front it might not stay" (W4). [C:VI] adopts this
("New progression content SHOULD default to explicitly provisional status"). **Adapt [R3] (not
directly evidenced at character scale; see T-3):** a newly recognized calling, tier, or acquired
ability starts **provisional**. The codex marks it so, and the fiction voices it as "the title hasn't
stuck yet" or "the power still feels borrowed." It is confirmed at the next boundary event if the
evidence holds, or it lapses quietly. That is also [C:P5]'s abstain/re-check loop made visible.

**04.17 Swap the specialization, keep the identity.** → 02.1 (PoE2 ascendancy swap). Also [F] Legion
"added … free swapping between specs … with their talent selection for each one automatically saved"
(WT1). **Adapt [R3]:** a character may hold saved loadouts per recognized calling and switch them at
rest.

**04.18 Blue-Mage absorption as a gated trait: the pool shape plus copy restrictions.** [F] [C:P5]
rescoped direct monster-power absorption to "a class-gated special capability ('Blue Mage'-style)." No
source in these rounds documents a Blue Mage implementation. The adjacent mechanics are these:
- The probe's shape: source gates the pool, method picks the fill (AP).
- RoR2's **`CannotCopy`** and **`AIBlacklist`** item tags, which exclude some items "from being
  granted to certain enemies/AI or copied by certain effects" (RG4).
- Diablo IV's Codex of Power, where aspects are "found once, then reusable indefinitely" as a library
  (A1, A5).

**Adapt [R3]:** an absorber calling (1) runs the probe's gate/fill on a *resolved* qualifying defeat,
(2) cannot absorb powers tagged `cannot_absorb` in the adversary data, (3) stores absorbed powers in a
**library** (the D4 Codex shape), and (4) slots only up to the hard cap. The library/slot split keeps
[C:V] closed while letting the absorber collect.

**04.19 A calling's synergy bonus is P6.** [C:P5, P6] already say so. [F] PoE "Keystones … grant unique
bonuses capable of fundamentally changing character functionality, often with significant downsides"
(PG3). Acrobatics, for example, grants dodge but penalizes armour, energy shield, and block. **Adapt
[R3]:** a top-tier calling bonus can be keystone-shaped, with a big behavior change and a real
downside, expressed through [C:P12]'s levers.

**04.20 Precedents for Pattern P14 cadence at the calling-group level.** → 06.4. [F] Agility melee runs
on a 1.0-second GCD versus 1.5 for everyone else, and haste does not affect the 1.0 group (WT5, W4).

**04.21 Emergence rationale: menus do not solve paralysis.** [F] TV Tropes (via search snippet):
menu-driven class systems "don't save time or allow anyone more choices, but also can't help with
choice paralysis when they force you into making choices all the same" (L5). *Unbound Ascension*
frames classlessness as enabling a protagonist who "questions the information received" (L5). The
evidence is weak (the section is "the weakest-sourced" of the note) but usable in ch 04 or ch 14 design
intent.

**04.22 Constitution precedents this round did not re-research.** HWFWM, The Land, Underworld, DCC,
Primal Hunter, Cradle, and Mother of Learning were explicitly out of scope (L6). Don't cite this
round for them.


---

### 05 — Abilities & Focus (slots and hard cap, templates, passive/active, recharge, Focus, P10/P12, P6 composites and priority-ordered behavioral tags)

**05.1 Slot counts across the precedents.** [F] The sources give these per-object active-slot caps:
- **PoE** items: 3 prefixes + 3 suffixes = 6 (A2).
- **Diablo II** rares: up to 6 (3+3). Magic items: 50% suffix-only, 25% prefix-only, 25% both (A1).
- **Diablo III**: 4 Primary + 2 Secondary (A1).
- **PoE2**: up to **9 active skills**, each with up to **5 support gems**, and "only one of each
  individual Support Gem in your entire skill loadout" (PG1, W2).
- **PoE1**: a 6-link socket structure, typically "one or two main skills augmented by multiple support
  gems" (PG1).
- **Hades**: 5 exclusive boon slots (Attack/Strike, Special/Flourish, Cast/Shot, Dash, Call/Aid) (RG1).
- **GW2**: each of 2 weapon sets gives 5 skills (main-hand 3, off-hand 2, two-hander 5) (MM2).
- **HWFWM** (constitution): 4 essences × 5 abilities = 20 [C:V, C:P5].

**Observation [R3]:** "about 6 rolled properties per object" converges across D2, D3, and PoE1. "5
modifiers per active thing" converges across PoE2 supports and Hades slots. Ch 05's slot counts and
hard cap should be justified against this table.

**05.2 The one-copy-per-loadout rule is an anti-stacking guardrail by construction.** [F] PoE2 allows
only one copy of any support gem across the entire loadout, "preventing unlimited stacking of the same
modifier." The report calls it "a structural anti-stacking guardrail that prevents the additive-bloat
failure mode Principle VI already worries about, achieved through a hard cap rather than an audit
process" (PG1, W2, PG8: "achieves more variety through fewer choices … by forcing specialization rather
than generic stacking"). **Adopt [R3]:** at most one instance of any given ability template, or of any
given behavioral-modifier tag, per character, enforced as a `[D]` state invariant.

**05.3 Support-gem modifiers: behavior change priced in Focus and a stated penalty.** [F] PoE support
gems "do not grant additional active abilities; instead, they modify any active skill gems linked to
them while typically **increasing the mana cost** of the skill" (PG1). Greater Multiple Projectiles
(PoE1) adds 4 projectiles and +10% increased projectile damage, but the skill deals **26% less**
projectile damage. PoE2's Multiple Projectiles adds 2 projectiles at **20% less damage and 20% less
attack/cast speed**. The "less" penalty does not apply to poison, so the same gem is a pure upgrade
for one archetype and a real tradeoff for another (PG2, W2). **Adopt [R3]:** a closed family of
*ability modifiers* (the constitution's composable behavioral tags [C:P6 companion]). Each one:
(a) changes behavior (more targets, a different delivery, a trigger condition);
(b) raises the ability's Focus cost [C:P9];
(c) carries one explicit [C:P12] cost or weakness clause.

Modifiers are what make a small base-ability pool feel large ([C:V]), and the Focus-cost increase is
the natural price tag.

**05.4 Priority-ordered, mutually exclusive behavioral tags.** [F] Pierce (the projectile passes through
and continues), Fork (it splits in two at ±60°, once only unless Awakened Fork), Chain (it redirects to
another nearby enemy, with the count set by gem level), and Return resolve in a fixed order. "A
piercing, forking, chaining projectile will first pierce its maximum, then fork, then chain." No
combination gets a name (PG2, W2). [F] Isaac's tear-replacers (Brimstone, Mom's Knife, Technology,
Haemolacria, Ludovico) compete for the single "what does the attack look like" slot. Documented
outcomes include "Mom's Knife has priority" over Brimstone, "Haemolacria has priority" over Brimstone,
and "Technology + Brimstone: the lasers coil the beams, purely visual, and Technology does not grant
its damage multiplier." In effect the designers "rank-order the tear-replacers rather than writing a
rule for every pair" (RG3, E2). **Adopt (already [C:P6] + [C:P5]):** every *slot-claiming* effect in
`data/` carries a `priority_rank` integer and the slot it claims (e.g. `basic_attack_delivery`,
`movement_mode`, `defense_reaction`). The higher rank owns the slot. Isaac's Technology+Brimstone case
shows one refinement: when the loser is suppressed, it *loses its numeric bonus too*, unless it is
explicitly marked "cosmetic merge" [R3]. Authoring cost stays at O(n), not O(n²) (E2).

**05.5 Three combination regimes: route every effect into exactly one.** [I/R3 from RG5, E2, E5]
| Regime | Use when | Mechanism | Precedent |
|---|---|---|---|
| Shared pipeline | Additive or multiplicative scalar effects | Write into the evaluation pass (00.6), with a stacking family (00.7) | Isaac stat cache; RoR2 |
| Independent triggers | Chance- or condition-based on-hit/on-event effects | Each rolls independently via a hook (00.5), scaled by a coefficient (00.8); no ordering needed | RoR2 proc coefficient; StS hooks |
| Priority rank | Effects claiming an exclusive behavioral slot | Highest `priority_rank` owns the slot | Isaac tear-replacers; PoE projectile tags |
| Named composite | A distinctive flagship combination | A hand-authored P6 entry keyed to a low-cardinality pair | Hades Duo Boons |

Ch 05 should *require* every ability template to declare its regime. That single field tells the AI
how the ability combines with anything, which is the core of goal 2 for novel builds.

**05.6 Identity versus magnitude inside an ability.** → 00.2. [F] D4's temper manual has a found theme
and a fill of 3–5 possible affixes, rolled on application, with a numeric roll on top: "three
independently-tuned layers" (E1, A1). **Adapt [R3]:** an ability template = fixed *behavior*
(identity) + a bounded numeric *magnitude* band that its source's fill quality can set (→ 08.6 for the
Greater Affix analog).

**05.7 Unified Focus versus per-class resources: the identity cost.** [F] WoW's resources are
"tailored to the playstyle of its respective class":
- Mana regenerates slowly.
- Rage is generated by damage taken and dealt.
- Energy regenerates quickly and caps at 100.
- Focus (hunters) regenerates moderately.
- Runic Power is generated by spending runes, caps at 100, and pays for costs like Death Coil at 50.

WT5 infers that "resource systems enforce playstyle identity at the mechanical level … Without resource
and GCD variety, all DPS specs would converge toward similar ability sequences" (WT5). [C:P9] chose one
unified Focus pool anyway, for hybrid bookkeeping. **Resolution option [R3] (see T-1):** unify the
*currency* and differentiate the *generation*. Each calling's synergy bonus can include a
Focus-*regeneration trigger* in the style of WoW's generators: a martial calling regains Focus when
struck (Rage), an arcane calling when resting or meditating (Mana), a skirmisher each turn it moves
(Energy). All of them pay into the same pool. This keeps P9's one pool and restores the identity
lever. It is also [C:P14]-adjacent: a cheap, structural feel difference at near-zero audit surface.

**05.8 Recharge conditions: explicit, enforced, and wary of cooldown-centric feel.** [C:P5] requires
that every active ability carry an explicit, mechanically tracked recharge. [F] The probe recorded
"once per encounter" as flavor text with no enforcement, a named gap (IR3, AP descriptions). [F] Even
after the GCD reversal, WoW players complained that "Cooldown-centric design does not seem to be going
over well" (CX5). This is weak evidence but relevant. **Implication [R3]:** vary recharge *types*
(Focus-only, per scene, per rest, charges, trigger-refreshed such as "recharges when you are
Bloodied") so the kit does not collapse into many once-per-encounter buttons. Every one is `[D]`
tracked.

**05.9 P10 in practice: templates that are precise narrative permissions.** [F] The probe's templates
are the constitution's own P10 example: "reduce incoming damage from a single hit per encounter, but
only against attacks you can see coming." **The failure (IR3):** Heat Resistance reads "Fire and
intense heat harm you less than they should — but this offers **no protection against cold**, and can
lull you into standing too close to danger." The live DM narrated that cold now "shocks the character
more harshly than normal," inventing an *active vulnerability* out of "a neutral absence of benefit."
The auditor caught it (5/6 = 83% consistency). **Adopt [R3]:** the template authoring standard in
ch 05 must separate [C:P12]'s three levers into *separate fields*:
- `scope` (what it covers).
- `limitation` (what it does not cover, written as a scope boundary, e.g. "Does not affect cold
  damage").
- `weakness` (an explicit active vulnerability, present only if intended).
- `cost`.

Soft phrasing like "no protection against X" or "can lull you into…" should be banned, because
"lull you into standing too close" is an unenforceable behavioral hint that invites embellishment.
Add the one-line narration rule IR3 recommends: "narrate exactly what the tool result licenses, no
more."

**05.10 Passive versus active, and a shared pipeline for passives.** [C:P5] passive means "always applies
when narratively relevant." [F] Isaac passives write into a shared cache (RG3). **Adapt [R3]:** every
passive must state its hook (00.5) or its pipeline slot (00.6). A passive that "just applies when
relevant" with no hook is the vague judgment call [C:P10] forbids for core power.

**05.11 Remove buttons that are never a decision (Kaiten).** [F] FFXIV removed Samurai's Kaiten button
"while making certain attacks auto-crit" (MM1). The button was a mandatory step before other attacks,
a press with no decision. This change is a consolidation example (fold the mandatory step into the
payoff). The community still counted it as lost identity (MM1). **Implication [R3]:** in ch 05, if an
ability is *always* used before another, fold it in. But be aware it may read as identity loss, so do
it at a boundary event (→ 04.14).

**05.12 Fold into base: how to retire a cliff-edge ability.** [F] PoE2 deleted the Acrobatics keystone
"as a distinct choice and its core mechanic (evasion applying to all hits, not just some) was folded
directly into the base evasion system." PoE2 also removed Masteries and life nodes (PG3, W2). **Adopt
[R3]:** it is a named [C:VI] retirement move for abilities. When a lower-tier ability is superseded,
its core effect folds into the base of its successor, so the slot frees without a felt loss. This
parallels Dungeon Crawler Carl's fork-replacement [C:VI]. The two are the chapter's structural
retirement tools: **fold**, **fork**, and **consolidate** (04.3).

**05.13 Swap loadouts, and the cost of swapping mid-fight.** [F] GW2 "all professions have the ability
to switch between two weapon sets while in combat, with the exception of elementalist and engineer
who can only weapon swap when out of combat." Traits reward swapping ("Gain quickness when you swap
weapons") (MM2). PoE2 weapon-swap passive points are "active depending on which weapon is equipped"
(PG3). **Adapt [R3]:** equipped abilities may exceed active slots only through *loadouts* that swap
at a stated cost: an action in combat, free at rest. This widens freedom (goal 1) without breaking
the hard cap on *simultaneously active* slots.

**05.14 Item-granted abilities.** → 08.10 (GW2 weapons grant skills; D3 legendary powers; PoE2
ascendancy-granted skills "can themselves be supported by gems," i.e. they plug into the same modifier
system; PG4).

**05.15 Proc-chain terminator and coefficients.** → 00.8. Ch 05 owns the per-ability
`trigger_coefficient` if adopted.

**05.16 Depth versus complexity.** [F] "A mechanic with 40 debuffs is complex. A mechanic with 3 debuffs
that interact in 40 ways (due to hidden modifiers) is deep and simple" (CX6). "Depth emerges from
permutations and combinations of simple mechanics" (CX4). **Implication:** this matches [C:V]. Few
primitives with many rule-based interactions give depth. It justifies spending authoring effort on
interaction rules (05.5) over sheer ability count.

---

### 06 — Conflict (action economy, turn order and cadence, positioning, attacks, damage, defense, conditions, reactions, morale, escape)

**06.1 Structure is required, and a grid is not.** [F] No surveyed narrative TTRPG tracks a grid:
Blades, Fate, Dungeon World, Ironsworn/Starforged, and Mörk Borg all do without one (E4). ChatRPG v1,
with no structure, produced "non-sensical outcomes" (FP6). The commercial fork: Friends & Fables
"reintroduced a visual layer — hex battlemaps, token movement"; RoleForge and DungeonsDeep.ai keep
prose but let "a non-LLM system" track "whatever positional/mechanical state exists" (FP6). **The
report's recommendation:** "a discrete relationship-state (engaged-in-melee / at-range / flanked /
cornered), living in P13's externalized tool-call/state-store layer and resolved via P8's
deterministic degree-of-success … not … a visual grid" (E6). **Honesty caveat [R3]:** ChatRPG's own
fix was a *resolution* tool, and it "explicitly does not report building any dedicated spatial
state-management … and flags this as an unaddressed limitation" (FP6). The evidence proves that
*some* structure is required. The relationship-state is the report's synthesis from the TTRPG
precedents, not something ChatRPG tested (T-14).

**06.2 The four relationship-state precedents, from lightest to heaviest.** Each is a candidate model.
- **Mörk Borg** [F]: a flat ±3 for flanking or high ground, and no persistent state (FP5).
- **Ironsworn** [F]: a per-move binary, close quarters (+iron) versus at range (+edge), plus an
  initiative token (FP4).
- **Dungeon World** [F]: 5 named range bands, **Hand / Close / Reach / Near / Far**: "Hand (attacking
  something within reach), Close (arm's reach plus a foot or two), Reach (… several feet away, maybe
  as far as ten), Near (seeing the whites of their eyes), and Far (shouting distance)." "No distances
  given for anything." Weapons and moves are tagged with the band they need (FP3).
- **Fate zones** [F]: "two to four probably being sufficient … more than six or so zones tends to get
  cumbersome." A zone is "close enough that you can … walk up to and punch them in the face." Melee
  (Fight) works only within a zone. Shoot reaches "up to two zones away." Moving one zone is free
  with an action; more zones, or a zone hindered by a situation aspect, needs an Athletics overcome.
  For mass combat, zones = players + 1 (FP2).
- **Blades** [F]: no spatial state; spatial facts are folded into Position/Effect (FP1).

**Synthesis [R3]:** for this game (single PC, possibly companions, several foes) the state that
actually decides legality is:
(1) a **range band per PC–foe pair** (DW's 5 bands, or Fate's zone count);
(2) **engaged with** (a set of melee lock relationships);
(3) **flanked / cornered / in cover / elevated**, as boolean situational flags feeding the ±3 unit
(01.4).

All of it lives in state and is written only by tool calls. That answers "can I reach, flank, or
retreat" and gives weapons an explicit reach tag.

**06.3 The geometric ceiling is a real limitation, so write the AoE rule.** [F] "Cannot answer precise
multi-target AoE geometry ('exactly which 3 of 6 enemies are in my cone') — a real capability ceiling,
not just a style choice" (E5). **Adopt [R3]:** define area and multi-target effects *over the
relationship-state*, not over geometry. PoE's projectile verbs map cleanly onto it:
- **Pierce**: also hits the next foe "behind" the target (same band, same line, via a `lined_up`
  flag).
- **Chain**: jumps to N other foes engaged with or near the target.
- **Fork**: splits to up to 2 foes in the target's band.
- **Burst**: hits all foes engaged with a point or zone.
- **Cone**: hits up to K foes in the Close band.

Fixed caps plus the priority order (05.4) make multi-target deterministic.

**06.4 Cadence, the GCD, and the P9/P14 tension.** [F] Base GCD is 1.5 s. Rogues, cat-form druids, and
monks run 1.0 s. "Haste can reduce the GCD to a minimum of 0.75 seconds (1.0 second prior to Legion)."
"Haste does **not** affect the GCD of agility-based energy melee classes" (WT5). "Classes with shorter
cooldowns offer consistent performance, while those with longer cooldowns emphasize high-impact
bursts" (WT5). [C:P14] adopts asymmetric cadence. **But [C:P9] demands "the same base action budget
regardless of build."** In a turn-based game, a literal cadence difference *is* an action-budget
difference: 1.0 versus 1.5 s is 1.5× the actions. **Resolution options [R3] (T-2):**
(a) Cadence lives in *what an action contains*: a "quick" calling's basic attack may split into two
    lighter strikes, each at reduced damage, which is the WoW consistent-versus-burst trade.
(b) Cadence lives in *initiative or tempo*: who acts first in a round, or who keeps initiative on a
    strong hit, per Ironsworn (06.5).
(c) Cadence lives in *reaction availability*: the quick group gets a second reaction but no extra
    actions.

None of these adds actions, so [C:P9] holds.

**06.5 Turn order: side-based, token-based, or free-form.** [F]
- Dungeon World: "There is no action economy or initiative order … Combat doesn't take place in
  strict turns" (FP3).
- Mörk Borg: "the whole party acts in the same round against the opposition" (FP5).
- Ironsworn: whoever holds **initiative** acts. A strong hit keeps it, a weak hit gives it up, and
  Enter the Fray sets it by approach (FP4).
- Monster of the Week: "the Keeper … does not roll for monster actions but reacts to the hunters'
  rolls"; combat "often boils down to a single action roll to see if you win and what price you paid"
  (FP3).

**Implication [R3]:** for single-player against many foes, an Ironsworn-style initiative token laid
over [C:P9]'s fixed per-turn budget is attractive. The PC's roll quality decides whether foes get to
act *proactively* (lost initiative) or only *reactively*. Whether adversaries roll at all is an open
decision (T-16).

**06.6 A pacing throttle is not a decision generator.** [F] BfA extended the GCD to offensive
cooldowns. "Affected abilities didn't change in any significant way, so players still had to go
through exactly the same rotations as before, just with far more stop-gaps sprinkled throughout."
Shadowlands reversed most of it. "Blizzard confused *pace reduction* with *comprehension reduction*"
(W3, CX5). **Warns against [R3]:** action taxes (e.g. "activating any ability costs your move") that
slow play without adding a choice. Every economy restriction in ch 06 should be checked: does it
create a decision?

**06.7 Crowd-control diminishing returns protect both sides.** [F] Successive CC halves in duration
(1 → ½ → ¼ → ⅛ → 1/16) in PvE, gives "full immunity after 2 applications" in PvP, and resets after
16 seconds (CX1). **Adopt [R3]:** repeated control conditions (stun, restrain, prone-lock) on the
same target within a scene diminish. For example the second application lasts half as long, and the
third fails ("immune"), resetting after a full round without control. This prevents lock-down
exploits by the player (goal 2) *and* stunlock deaths of the solo PC. The latter matters for the
locked "no single unlucky roll ends a character" decision (→ 07.3).

**06.8 A threat/attention model for companions and targeting.** [F] WoW threat: 1 damage = 1 threat,
plus class multipliers (5.0× for tank abilities like Righteous Fury), per-ability bonus threat, and
healing threat equal to half the effective healing per observing NPC, divided by the observer count.
It was fully hidden until Wrath (CX1, W3). **Adapt [R3]:** a background-resolved `[D]` attention
score decides which of PC / companion / summon an adversary targets, so the DM does not pick targets
by narrative whim. It is also a new analog anchor: "taunt" and "draw attention" abilities have a
number to act on.

**06.9 Self-defense for everyone: non-trinity.** [F] GW2 "breaks the trinity by giving every player
the simple means to defend themselves," which "structurally lightens the balance burden, since
encounters no longer *require* specific roles" (MM2, W1). **Implication [R3]:** a solo PC is
non-trinity by necessity. Basic defense and reaction options belong in the always-available tier
[C:VII], and encounters (ch 09) must never *require* a role.

**06.10 Chases and escape use opposed clocks.** [F] Blades runs an "Escape" clock for the PCs and a
"Cornered" clock for the pursuers in parallel: "if the PCs fill their clock first they get away,
otherwise they are cornered and can't flee" (FP1). **Adopt:** a primary mechanism for escape and
pursuit in ch 06, which also serves ch 07 (defeat as capture or cornering) and ch 10 (travel pursuit).

**06.11 A structured exchange tool.** → 00.12. Required arguments: attacker, explicit target(s),
ability, and relationship-state preconditions validated. ChatRPG's lesson: put the few-shot examples
*in the tool description* (FP6).

**06.12 Weapons define kit.** [F] In GW2, "the weapon you're currently wielding is a major determining
factor for how your character will play." "The main-hand weapon determines the first three weapon
skills, the off-hand … the last two" (MM2). In PoE2, "Skills … are weapon-based and animation-driven,
with damage dealing determined by actual weapon or spell contact … to discourage single-button builds"
(PG1). **Adapt [R3]:** weapon *families* (a tag in 03) can license basic-attack variants
([C:VII]'s licenses). A spear licenses Reach-band attacks, a shield licenses a block reaction. This
makes gear matter to capability, not just to numbers.

**06.13 Morale.** Not covered by any source in these rounds (Section 5 G-10).

**06.14 Positioning cues must be written clearly.** [F] Blades "fictional positioning": the GM must
"write the world" clearly enough that the stakes of an exposed clearing or a choke point "are legible
without measuring it." Two squads crossing the same clearing can get different Position purely from
who they are (FP1). **Implication:** ch 06/12 DM procedure: whenever relationship-state changes,
narration must name it in plain words ("you're now in the orc's reach; the archer has a clear line on
you"). The player needs this to exercise freedom, and it gives the auditor something to check.

**06.15 An adjudication hazard with no persistent memory.** [F] PbtA's actual-play advice does not
formally solve "who's near whom … across a whole fight to stay consistent turn-to-turn" (FP3 gaps).
**Implication:** this is exactly why the state must be externalized ([C:P13]) rather than kept in
narration.

---

### 07 — Harm, Recovery, Death (injury, Vitality consequences, rest/recovery, telegraphed death, defeat outcomes)

**07.1 Position as the lethal-risk telegraph.** → 01.1. [F] Blades' Desperate means "if this doesn't go
perfectly, they'll be utterly screwed," and it is set and known *before* the roll (FP1). **Adopt
[R3]:** the BRIEF's "explicit warnings before lethal risk" becomes a rule. Any roll whose failure band
can move the PC to the dying state must be announced at Desperate-equivalent position before the roll.
No Desperate announcement means no death on that roll.

**07.2 Circumstantial shift: injury can reshape identity.** [F] "A [Warrior] permanently injured
becomes [Wounded Warrior]" (L4). **Adapt [R3]:** a lasting injury in ch 07 can be one of ch 04's
fiction-voiced relabel triggers, *offered*, not imposed (04.14). It gives injury narrative weight
without a death spiral, and it is a consolidation or retirement opportunity.

**07.3 No stunlock deaths.** → 06.7 (CC diminishing returns). [R3] This directly serves the locked
decision that "a single unlucky roll never ends a character without warning."

**07.4 Never narrate self-harm without a result.** → 01.9. [F] ChatRPG narrated self-injury when it
could not find the target (FP6). **Rule anchor:** Vitality loss for the PC occurs only through a
resolved result or an explicit, announced hazard. The narration layer can never originate it.

**07.5 Harm increments come in degree-scaled steps.** [F] Ironsworn: strong hit "+1 harm," weak hit
still "inflicts harm but loses initiative" (FP4). ChatRPG's Battle tool takes "damage severity" as a
parameter (FP6). **Adapt [R3]:** a discrete severity scale set by degree (e.g. glancing / solid /
severe / devastating), passed as a tool argument, is more auditable than free damage numbers
narrated after the fact.

**07.6 Defeat as a changed situation.** [F] Blades' opposed clocks end in *cornered*, not dead
(FP1). PbtA "separate them" moves reshape the scene (FP3). The on-4/5 guidance says the enemy is
cornered but grabbed the gun (FP1). **Adapt:** ch 07's defeat outcomes (capture, loss, separation,
a changed situation) have direct PbtA/FitD anchors.

**07.7 Softcore versus hardcore as a variant precedent.** [F] PoE leagues run four variants: standard
softcore ("character returns to Standard on death"), hardcore (permanent death), SSF, and HC SSF
(PG6). **Relevance [R3]:** a precedent for an optional lethality dial if the owner ever wants one.
The current lock is "death is real but telegraphed," so this is mention-only.

**07.8 Where Vitality growth comes from, without levels.** [F] PoE2 "Life nodes have been eliminated
entirely from the passive tree. Survivability is now determined primarily through equipment" (PG3,
W2). **Open question [R3]:** [C:P2] removes levels, so ch 07/04/08 must decide the source of max
Vitality growth: calling tiers, items, or neither (flat Vitality with better *mitigation* from gear
and abilities). PoE2 is precedent for "not from the progression track" (Section 5 G-8).

**07.9 Recovery and rest.** Not covered, beyond using rest as a recharge and loadout-swap point
(05.8, 05.13). See Section 5.

---

### 08 — Items, Loot, Crafting (loot generation by pool gate / fill quality, item properties, crafting, wealth, economy)

*This chapter is the primary consumer of the fifth research pass. [C:P5] (sixth pass) makes loot the
default application of the gate/fill mechanism, and the ARPG research is itself about items. Read
Section 2A/2B of the catalog alongside this section.*

**08.1 The canonical generator: filter → weighted sample → group exclusion → slot cap.** [F/I] PoE's
generator is a three-part algorithm: "(1) filter the candidate pool by tag compatibility with the base
item and item level, (2) weight-sample within that filtered pool, (3) reject/reroll if the sampled
mod's group is already occupied." Selection probability = `target_mod_weight /
total_weight_of_eligible_mods`, and the per-item cap is 3 prefix + 3 suffix (A2). The researcher calls
this "a strong candidate template for a tabletop 'roll an ability from source × acquisition-method'
system: source/acquisition act as the 'tags' that filter the eligible ability pool, then a weighted or
flat roll picks within it, with a small number of 'ability groups' preventing redundant stacking" (A2
inference). **Adopt:** this is the loot algorithm skeleton. The adversary archetype or material is the
tag filter (the pool gate, [C:P5]), the acquisition circumstance chooses the fill method (08.3), mod
groups prevent redundancy, and the per-item cap bounds the result.

**08.2 The source gates by replacing the pool, not by adding a stat.** [F] Borderlands: "manufacturer
identity does not modify a shared parts pool, it *replaces* which pool is even eligible." Tediore
reloads by throwing the gun, which explodes as a fresh one "digistructs." Maliwan is elemental-only,
with higher tech uptime. Jakobs is never elemental, with high base damage, low fire rate, and high
crit multipliers ("keep it simple, no gimmicks"). This expresses "in-fiction values through mechanics,
not just flavor text." BL3 "does not mix manufacturers' parts … each manufacturer has multiple variants
for each part." The earlier cross-mixing was judged less legible (E1, A4). **Adopt:** in ch 08/09,
each adversary archetype and each maker tradition has its *own* item-property pool, and some
properties are *categorically impossible* for some sources. That is what makes a drop recognizable
("this is clearly troll-bone work") and gives the AI a crisp legality check (goal 2).

**08.3 The fill-method menu: currencies as entry points into the same table.** [F] PoE's currencies are
"different *entry points* into that same weighted table rather than separate generators" (E1, A2):
| PoE currency | Fill behavior | P5 fill-quality analog [R3] |
|---|---|---|
| **Essence** | Guaranteed one specific affix; the rest roll normally. Tier 5 "Screaming"+ can reforge an existing rare | Decisive/clean acquisition guarantees the source's *signature* property (the probe's `decisive_kill` → `guaranteed`) |
| **Fossil** (in resonators) | Biases weighting toward a theme or tag; costlier | Costly or method-flavored acquisition biases toward a flavor (the probe's `narrow_survival` → defensive ×3) |
| **Crafting Bench** | Deterministically adds one chosen mod to an open slot; the value may still roll | Deliberate crafting or a commissioned work: the player chooses one property from the eligible pool |
| **Chaos** (not confirmed in source) | Full reroll | Scavenged or incidental loot: plain weighted roll |
| **Exalted** (not confirmed in source) | Adds one random affix | "Found an extra property" on a critical success |

(Chaos and Exalt behavior "was not directly confirmed with a citation … should be treated as a gap"
(A2 gaps). Do not cite the source for them.)

**Adopt [R3]:** ch 08 should name a closed set of 3–5 fill methods and map each *acquisition
circumstance* (decisive / costly / merciful / crafted / scavenged / gifted) and *degree of success*
onto one. The report: "Needs 3-4 named acquisition-method archetypes authored once, then reused
everywhere" (E5).

**08.4 Tiers gated by source power: the D2 affix-level gate.** [F] D2's `alvl` is derived from item
level and base quality level: if `ilvl < 99 − qlvl/2` then `alvl = ilvl − qlvl/2`, else `alvl =
2·ilvl − 99`. ilvl is capped at 99, and if qlvl > ilvl, ilvl is first raised to qlvl. Required level
≈ 75% of alvl. It is "a **gate function**, not a weighting function … a hard eligibility cutoff," and
"may be more portable to a tabletop context where computing continuous weights isn't practical" (A1).
PoE: "a low-tier life mod might add ~10-20 life while a high-tier version … ~80-90 life, and higher
item level raises the chance/eligibility of higher tiers" (A2). **Adopt [R3]:** without character
levels (BRIEF ch 09 "threat bands without character levels"), the **source's threat band** plays
ilvl. It hard-gates which property *tiers* may appear, and ch 09's bands double as loot tiers.
Worked arithmetic of the D2 formula [R3]: with ilvl 50 and qlvl 20, 50 < 89, so alvl = 40, and
required level ≈ 30. With ilvl 95 and qlvl 20, 95 ≥ 89, so alvl = 2·95 − 99 = 91.

**08.5 Mod groups: hard mutual exclusion, scoped per slot class.** [F] "Only one mod from a group can
appear at a time," but "a group's exclusivity is scoped to prefixes or to suffixes separately," so a
prefix and a suffix from the same family can coexist. This prevents "two different '% increased life'
mods of different tiers from both landing on one item" (A2, E1). **Adopt [R3]:** every item property
carries a `mod_group`. A roll landing in an occupied group rerolls (a `[D]` rule).

**08.6 Magnitude rolls, and a "greater" upgrade on a critical fill.** [F] D4's Greater Affix is "a random
+50% bonus to a rolled value" that "additionally grants a re-roll chance." Ancestral items "are
guaranteed at least one GA and get two Temper slots" (A1). **Adapt [R3]:** a critical success on the
acquiring action (P8) upgrades one property to Greater (×1.5 magnitude, rounded per ch 00) and could
open an extra slot. This is the cleanest link between ch 01's degrees and ch 08's fill quality.

**08.7 Signature items live outside the rules.** [F] D2 Uniques have 3–8 "custom created"
properties, some with narrow ranges ("100-120% enhanced damage") but a fixed *set*, and "no rules to
the mods." Sets add "conditional set-bonus stats that activate as more pieces of the set are equipped"
(A1, A5). **Adopt [R3]:** a hand-authored `unique` item class (named, a fixed property set, limited
ranges) that is exempt from mod groups and slot caps but *counted* in the per-layer power budget
(00.13). Also a `set` class with conditional N-piece bonuses, which is [C:P6] composites on items.

**08.8 Structure fixed a broken launch in two franchises.** [F] D3's launch itemization rolled "completely
random," and players lived with it "for nearly two years until Loot 2.0 imposed the Primary/Secondary
structure and Smart Loot constraints." Borderlands moved from cross-manufacturer mixing to locked
pools. Both franchises "moved from 'more open randomness' toward 'more constrained, categorically-gated
randomness' after shipping the more open version first" (A1, A4). **Implication:** strong evidence
against a loosely constrained "the DM invents what drops" approach. Ch 08 should be structurally
constrained from v1.

**08.9 A fixed modifier count beats variable counts for legibility.** [F] PoE2: "Every rare item
created with Orbs will gain exactly 4 modifiers," replacing PoE1's variable 2–6, framed as "more
predictable and stable." PoE2 removed Scouring, Chromatic, Jeweller's, and Fusing, the socket ones
"because the socket system has been completely reworked." PoE2 also restricts an item to a *single
crafted modifier* (via the Alloy currency) (A3). Caveat: the "legibility" rationale is the
researcher's inference, not a GGG quote (A3 gaps). **Adopt [R3]:** each rarity tier generates a
*fixed* number of properties (e.g. common 0, fine 1, masterwork 2, rare 4), and each item carries at
most **one** player-crafted property.

**08.10 What dropped items grant (a deferred item in BRIEF §8).** The sources give three patterns:
- [F] GW2: equipment *grants active abilities* while wielded (5 per weapon set; MM2).
- [F] D3: a legendary *power* sits in a reserved slot on an item (A1).
- [F] D4: aspects become *reusable knowledge* in the Codex after being found once, then get
  "imprinted" onto items (A1, A5).

**Adapt [R3]:** item grants split three ways, all under gate/fill.
- **Mundane** properties (magnitude).
- **Passive** properties (a hook or pipeline effect while equipped).
- **Item-bound active abilities** (usable only while equipped; count against a separate
  *equipment ability* slot class, or against the hard cap, per the T-12 decision).

D4's Codex pattern gives a crafting path: *salvaging* a signature item could teach its signature as a
reusable crafting recipe.

**08.11 Crafting uses the same shape.** [C:P5 sixth pass]: "a future feature in a different domain (e.g.
crafting) MUST NOT be assumed to need its own bespoke two-axis design." [F] D4 Tempering: a
world-found manual (a found category, 3–5 affixes by theme) applied to an item picks one of its 3–5
affixes at random and rolls a value (A1). The PoE Crafting Bench is deterministic (A2). **Adopt
[R3]:** crafting has the *material* as pool gate (troll hide gates regeneration-family properties),
the *crafter's result* as fill (a P8 degree picks guaranteed / chosen / weighted / Greater), and
*recipes or techniques* as found-once, reusable knowledge (the Codex). All of it runs through the same
tool, as the probe's `resolve_ability_grant` does, so the DM only classifies.

**08.12 Pseudo-stats and search for a large property space.** [F] PoE's trade site lets players search
"for any specific modifier in the entire game" and exposes "pseudo mods (composite/derived stats, e.g.
total elemental resistance) precisely because raw modifiers are too numerous." The genre's answer is
"delegating the math to community tooling rather than compressing the design space" (A2). **Adopt
[R3]:** the codex [C:P7] (ch 14) computes rollups ("total fire mitigation: …") so neither the player
nor the DM re-adds properties by hand. That is a `[D]` codex function.

**08.13 Bound the count, not the table.** [F] "The genre does *not* solve combinatorial legibility by
capping the *total design space* … it solves it by (a) capping the per-object number of rolled slots
and (b) pushing full-space evaluation to external tooling." For tabletop, "the more relevant lesson is
(a)" (A2 inference). The BL3 scale is ~35 part categories and ~1,500–1,700 parts (unverified), "1
billion+" guns in BL3, and "roughly 30 billion" in BL4 across about a dozen manufacturers, with a
"gun map" compatibility chart to keep combinations coherent (A4). **Implication [R3]:** ch 08's
property tables can be *large* (a rich substrate, [C:P3]) as long as the per-item count is fixed and
every entry is enumerated in `data/`. An authored **compatibility map** (the Gearbox "gun map") is the
check that generated items still "read" as their source.

**08.14 Smart loot versus P5 purity.** [F] D3's Smart Loot guarantees "class-appropriate main stats"
(A1). **Tension [R3] (T-9):** biasing drops toward the PC's tags feels good, but it adds a third axis
(the character) to [C:P5]'s two (source, method), and it risks a self-reinforcing loop against
pivoting. A mild option: when the PC is *recognized*, one property roll per drop may use the
calling's tags as an extra fossil-style bias, never as a gate.

**08.15 Category choice as a fill.** [F] RoR2's `ItemTag` categories (Damage/Healing/Utility) decide
eligibility for Category Chests (RG4). **Adapt [R3]:** a "choose the category, roll within it"
acquisition, such as a patron's gift or a commissioned smith, is a clean player-freedom fill (goal 1).

**08.16 The economy, which is thin.** [F] EVE's "player-driven economy (ships, modules, and damage
types are balanced against each other through supply/demand and iterative balance patches) provides a
second-order balancing mechanism" (MM3). PoE's "commodity-based economy" is an intimidation factor
(PG7). **No pricing, wealth-curve, or currency-sink data** exists in these rounds (Section 5 G-18).

**08.17 The probe's pool shape, and how it extends.** [F] AP: 4 archetypes (beast, elemental_fire,
undead, construct) × 3 methods (decisive_kill → `guaranteed` signature; narrow_survival → `weighted`
biased to defensive; non_lethal_subdual → `weighted` biased to utility). Each archetype pool holds
exactly 3 templates, one per flavor_bias (defensive/utility/offensive), with exactly one
`is_signature`. The weights are biased 3 : unbiased 1, "a genuine bias, never a disguised
guarantee." **Arithmetic [R3]:** with 3 templates, a weighted fill gives 3/(3+1+1) = **60%** biased
and **20%** each other. The probe *lacks* several things: a magnitude layer, tiers, mod groups, a
deterministic/chosen fill, a critical-quality upgrade, and multi-property objects. Extend it with
08.1–08.9 and keep its shape (BRIEF §7). Signatures by archetype: beast = Thick Hide (defensive),
elemental_fire = Ember Burst (offensive), undead = Grave Chill (offensive), construct = Iron Frame
(defensive).

---

### 09 — Adversaries (archetypes = loot/ability pool gates, threat bands without character levels, stat templates, behaviors)

**09.1 An archetype is a manufacturer.** → 08.2. [F] The Borderlands manufacturer expresses identity
"through mechanics, not just flavor text" (A4). **Adopt [R3]:** each archetype's data entry names
(a) its evidence tags (what defeating it counts toward, ch 03), (b) its loot property pool (ch 08),
(c) its absorbable-power pool with `cannot_absorb` flags (ch 04), and (d) its behavior verbs. All four
come from **one** tag set (00.4).

**09.2 A threat band is the ilvl.** → 08.4. [R3] One band value drives the adversary stat template
*and* the loot-tier gate.

**09.3 Tags keep AI-only and player-only effects apart.** [F] RoR2's `AIBlacklist` and
`BrotherBlacklist` keep certain items away from enemies, and `CannotCopy` blocks copying (RG4).
**Adopt [R3]:** some effects in `effects.yaml` are marked `player_only` or `adversary_only` (for
example, adversaries never gain effects that make the "telegraphed death" guarantee unenforceable).

**09.4 Encounters must not require a role.** → 06.9 (GW2 non-trinity). [F] FFXIV encounters assume
tank/healer/DPS, which drives homogenization (MM1). [R3] Solo encounters must be solvable by any
calling and by an unrecognized character, possibly by different routes (goal 1).

**09.5 Hidden per-adversary state is fine.** [F] Background-resolved complexity is unlimited (CX1,
CX4). **Implication [R3]:** adversaries can carry rich hidden state (attention tables, morale values,
resistances by tag), because it feeds the DM's improvisation substrate [C:P3 sixth pass]. The codex
reveals it only through P17 knowledge checks.

**09.6 Keep the adversary archetype count at low cardinality.** [R3 from 03.6, E3] If adversary
archetypes key *hybrid* or *absorber* tables, keep the archetype *families* few, like Hades' gods.
Individual monsters can be many, since they are instances of families.

**09.7 Behavior verbs.** [F] AW MC moves (FP3). Blades position cues (FP1). There are no adversary AI
behavior tables in these sources (Section 5 G-22).

**09.8 Tight balance helps prediction.** [I] "encounters can be designed assuming specific job roles,
loot can be tuned precisely, and the AI can make high-confidence predictions about player power"
under tight balance (MM4). **Implication:** threat bands need a player-power estimate. With emergent
builds, ch 09 should estimate PC power from *state* (tier count, slotted abilities, item layer) with
a `[D]` formula rather than from narration.

---

### 10 — Exploration, Social, Downtime (travel, hazards, investigation, social influence, downtime)

**10.1 Time-gated training as downtime.** [F] EVE skills "train in real time, even when logged off" at
a rate set by "attributes, the skill's training time multiplier, and the level to which you are
training." Every skill has 5 levels, there are 400+ skills, and training all of them "would take
around two decades." Prerequisite chains gate advanced skills. The Skill Extractor is a costed respec
(MM3, W1). [C:P15] is the constitution's form of this. **Adapt [R3]:** downtime training (in-world days)
could buy *non-calling* competencies (languages, trades, lore) without a point-buy audit. The scarce
resource is in-fiction time, which also feeds the living-world clocks (ch 11). A costed "unlearn"
(extractor) supports re-specialization.

**10.2 Learned techniques as found-once knowledge.** → 08.11 (the D4 Codex). [R3] Investigation and
research downtime can *discover* recipes and techniques that are then permanently known.

**10.3 Clocks for extended non-combat actions.** → 06.10. [F] Blades uses opposed clocks for chase
and cornering (FP1). **Adapt:** travel pursuit, infiltration, and negotiations under time pressure.

**10.4 Zones outside combat.** [F] Fate's zones are a general "abstract representation of physical
space," and movement across several zones needs an overcome roll when a situation aspect hinders it
(FP2). **Adapt [R3]:** the same band or zone state can describe a chase through a market or a
multi-room infiltration.

**10.5 Position and Effect generalize to social play.** [I/R3] Blades' axes are not combat-specific
(FP1). Social stakes (Desperate: the duke will have you arrested) map the same way.

**10.6 Coverage warning.** These sources barely touch exploration, social influence, hazards,
investigation, or downtime beyond the above (Section 5 G-11).

---

### 11 — Living World (factions, clocks, hooks, rumors, consequence propagation, sandbox generation, retirement & legacy)

**11.1 Factions confer callings.** [F] Wandering Inn's authority-based grant: an Emperor grants
[General] (L1). **Adapt [R3]:** factions and orders as calling-*conferral* sources, fiction-voiced ("an
order that seeks you out," BRIEF §4), bounded by [C:P5] (→ 04.2, T-13). This turns faction standing
into a progression lever, which gives the sandbox a strong hook engine.

**11.2 Factions express values through their item pools.** [F] Borderlands manufacturers "reflect their
… values … through mechanics, not just flavor text" (A4). **Adapt [R3]:** each faction or crafting
culture's pool gate *is* its ideology in mechanical form.

**11.3 Seasonal provisional content at world scale.** [F] One new mechanic per 3-month league, then
integrate, rework, or discard (PG6). **Adapt [R3] (speculative):** the living world could introduce
"seasonal" phenomena (a comet year, a plague, a war) as provisional world mechanics that the sandbox
may later make permanent or retire. That is a [C:VI]-compliant way to add world content indefinitely
in an open-ended campaign.

**11.4 Economic second-order effects.** → 08.16 (EVE). A thin source.

**11.5 Retirement and legacy analogs.** [F] D4's Codex of Power is account-bound: aspects are found
once and "reusable indefinitely" (A1). EVE skill points are permanent, with the extractor transferring
value at a cost (MM3). PoE league characters return to Standard at league end or on death (PG6).
**Adapt [R3]:** at retirement, a *legacy codex* of discovered recipes, techniques, and lore passes to a
successor character, which is D4's account-bound library turned into a lineage.

**11.6 Racing clocks.** → 06.10. Opposed clocks are also a faction-versus-faction race mechanic.

**11.7 Scheduled change and communicating the why.** [F] GW2's "living document": "smaller overall scope
in changes some months and major balance overhauls less frequently." ArenaNet publishes the *why*,
which W1 recommends copying ("publish the *why*, not just the *what*"). WoW publishes hotfix notes
without criteria (WT3, WT6). **Adapt [R3]:** when the world changes the PC's circumstances (a faction
falls, a law changes), the DM surfaces the causal chain as rumor or consequence (the "why"), which
supports P16 hooks.

---

### 12 — DM Procedures (turn loop, pacing P16, reveal P17, NPC play, improvising from the substrate, session structure)

**12.1 Classification is the DM's core job.** → 00.11. [F] 6/6 correct classifications onto closed
categories (IR3). **Procedure [R3]:** every generator call follows three steps. (1) Did the resolved
outcome occur? (2) Classify gate and fill from closed lists. (3) Call the tool and narrate *only* its
output.

**12.2 Narrate exactly what the tool licenses.** [F] IR3's embellishment failure (Heat Resistance →
invented cold vulnerability) and its recommendation: "narrate exactly what the tool result licenses, no
more." [C:P13 first empirical point] Self-assessment missed an unearned pronoun. **Procedure:** after
any grant, quote the granted text's limits in narration or keep them in the codex, and never
extrapolate weaknesses.

**12.3 Consequence moves as a closed list.** [F] AW MC moves, including "separate them," and "all GM
moves put the characters in a position to make a choice and act" (FP3). **Adopt [R3]:** ch 12's list
of DM moves (reveal a threat, separate them, put someone in a spot, take something, advance a clock,
offer an opportunity with a cost…). It is a [C:P3] substrate, and it implements [C:P16].

**12.4 Set position and effect *before* the roll and say them.** → 01.1, 07.1. [F] Blades procedure
(FP1).

**12.5 Worked examples belong at the point of use.** [F] ChatRPG put "few-shot prompting examples baked
into the tool description to keep combat logic consistent" and used a specialized combat narrator
(FP6). **Implication:** supports the BRIEF's "worked examples everywhere," placed where the DM will
read them at decision time (tool or rule text), not only in an appendix.

**12.6 Two tiers of change velocity: rulings versus amendments.** [F] WoW has hotfixes (instant,
several per week) versus x.x.5/x.x.7 patches (every 8–10 weeks), and "cadence collapse" arrives when
patches outpace validation. WT6 suggests "8–12 weeks between major balance passes, with hotfixes in
between" (WT3, WT6). **Adapt [R3]:** a DM's in-session ruling on an unanticipated case is a
"hotfix." It applies now and gets *logged* as precedent. Changing an actual rule or a granted ability
happens only at a boundary (between sessions or at a tier event). It is never re-litigated mid-scene.
This is the procedural form of 04.14 and [C:III].

**12.7 Metrics-driven review.** [F] Slay the Spire's team "used play-metrics/telemetry (rather than a
hand-designed combination catalog) to observe which emergent card/relic combinations were over- or
under-performing" (RG2, GDC 2019). **Adapt [R3]:** log tag_events, ability uses, and item grants in
structured form, so that provisional content (04.16) can be promoted or retired on evidence. This
supports the Open Empirical Questions appendix.

**12.8 Buff underused options, don't nerf attached ones.** [F] PoE2 ("balancing through buffs rather
than heavy nerfs," "a rising tide"), GW2 ("highlight underutilized skills"; buff "rather than
aggressive nerfs") (PG5, MM2, W1). **Adapt [R3]:** when a provisional ability underperforms, promote an
improved version. When one overperforms, prefer to let it lapse at its trial boundary rather than
nerfing a confirmed ability.

**12.9 Explaining hidden mechanics is the AI's real bottleneck.** [I] "The AI DM's bottleneck is not
'can it track 40 debuffs' (yes) but 'can it explain 40 debuffs to a player in 2 sentences'" (CX6).
"No research found directly addressing how to communicate complex hidden mechanics" (CX4 gaps).
**Implication:** ch 12/14 must write their own explanation procedures, such as condensed state
summaries on request (the codex) and a short "what changed" line after each exchange.

**12.10 DM clarity about space.** → 06.14, 06.15.

---

### 13 — Starter Setting (a classic-fantasy starter region and opening situation that exercises every subsystem)

**13.1 Maker traditions as manufacturers.** → 08.2, 11.2. [R3] Seed 3–5 maker traditions or cultures
whose item pools are *categorically* distinct: a Jakobs-like forge that never enchants but makes
brutal, crit-heavy steel; a Maliwan-like mage-guild whose goods are all elemental; a Tediore-like
hedge-tinker whose items are cheap, disposable, and explosive on breakage. A player can then recognize
provenance from behavior.

**13.2 Patron or spirit pools as Hades gods.** [F] 8–9 gods, each with its own boon pool and one Duo
per pair (RG1). **Adapt [R3]:** if the setting has patrons (saints, spirits, old gods) that grant
gifts, keep them to ≤8, give each its own gated pool, and let "duo" blessings key to patron pairs.
This is also a natural home for a hybrid-table test case.

**13.3 Adversary archetypes spanning the tag tree.** [R3] The starter adversaries should cover each
top-level evidence branch and at least one `cannot_absorb` case, and should demonstrate each fill
method (decisive, costly, merciful, crafted, scavenged).

**13.4 An opening scene that exercises the relationship-state.** [R3] Include one fight with 3+ foes
at mixed bands, a choke point (flag), a flanking opportunity, and an escape clock, so that 06.2–06.10
and the ChatRPG target-resolution rule (01.9) are all exercised.

---

### 14 — Player's Guide + Codex (P7)

**14.1 The codex is the official Path of Building.** [F] PoE went "years without an official build
planner, relying entirely on the third-party Path of Building until GGG eventually built an official
equivalent." The report: "the fix GGG converged on — officially blessing an external, queryable
optimization tool rather than simplifying the tree — is exactly Pattern P7's 'player-facing reference
layer' prescription" (W3, CX3). **Adopt [R3]:** the codex computes, not just lists. It shows totals,
rollups (08.12 pseudo-stats), ability regimes and priority ranks, active conditions with remaining
duration, relationship-state, and provisional flags. This is also the research's strongest support
for the BRIEF's deviation from P3's cap: PoE kept the complexity and solved comprehension with a tool
(T-7).

**14.2 The display cap is a UI choice, not a truth cap.** [F] WoW shows 16 debuff icons of up to 40, and
players used add-ons (BigDebuffs) to see more (CX2, W3). **Implication [R3]:** the codex should show a
*summary* by default and *everything* on request, never hide state permanently.

**14.3 Onboarding, not simplification.** [F] PoE director Jonathan Rogers: "being such an old game is
itself the accessibility problem," not complexity. "Once the passive tree's purpose is understood …
it becomes substantially less intimidating" (PG7, PG8 #5). The hidden-information design pattern: "a
weapon might have ten stats … but if each weapon also has a 'level' and 'suggested class,' casual
players make a quick, reasonable choice" (CX4). **Adopt [R3]:** the player's guide should teach
purpose first ("what is this subsystem for") and provide *suggested defaults* (CX6 option C: "simple
default paths and deep optimization paths, following the PoE model").

**14.4 Publish the why.** → 11.7 (GW2). [R3] The player's guide and the codex should carry short "why
this rule exists" notes, and the Decision Log is the out-of-fiction source.

**14.5 Transparency of callings.** → 04.13 (the decision on what the codex reveals about unrecognized
callings).

**14.6 Depth versus comprehension versus tracking.** [F] Game Developer's three categories:
comprehension complexity (harmful if excessive), tracking complexity (harmful if excessive), and depth
(valuable) (CX4, W3). **Under the BRIEF [R3]:** player comprehension is explicitly not a constraint on
*rules*. It remains a constraint on *presentation*, which the codex solves.

**14.7 Working-memory numbers, for reference only.** [F] Hodent: "3 items to process at the same time is
THE MAXIMUM when in learning mode," and ~5±2 once familiar; 7±2 is the general UI ceiling (CX2, CX4,
W3). The BRIEF says not to use these as a design argument for rules. They remain relevant *only* to how
much the DM narrates per turn and what the codex surfaces by default.

---

### data/ and appendix pointers

- **`data/effects.yaml`** (shared effect definitions, 00.1); **`data/tags.yaml`** (domain, ordered
  ancestry, cardinality ≤ 9 at the top level, 03.6); **`data/hooks`** (closed trigger list, 00.5);
  **`data/abilities.yaml`** (regime, priority_rank, claimed slot, scope/limitation/weakness/cost fields,
  recharge type, Focus cost, modifier compatibility tags; 05.4, 05.5, 05.9); **`data/item_pools.yaml`**
  (pool gate by source/material, mod_group, tier by threat band, weights, signature entries, unique and
  set classes; 08.1–08.9); **`data/callings.yaml`** (primary and secondary thresholds, tiers, synergy
  bonus, Focus-generation trigger, fantasy mechanic; 04.1, 05.7); **`data/hybrids.yaml`** (branch-pair
  key, prerequisites, exclusions, `requires_count` override; 04.9, 04.10); **`data/adversaries.yaml`**
  (archetype family, tags, loot pool id, absorbable pool with `cannot_absorb`, threat band; 09.1);
  **`data/conditions.yaml`** (the DR class for control effects, 06.7).
- **Decision Log `Revisit if:` triggers** these sources suggest: "a single layer supplies > X% of total
  power in simulation" (the jewel meta); "a recognized calling's identity changed outside a boundary
  event" (Survival Hunter); "wrong-target or self-harm narration observed" (ChatRPG); "a granted
  ability's narration exceeded its text" (IR3).
- **Open empirical questions** these sources imply (each with a named test) are in Section 5.


---

## 2. Concrete mechanics catalog

Each entry gives the mechanic, its exact description, the source code(s), and the chapter(s) that
should adopt or adapt it. "Adopt" means use it as-is in a translated form. "Adapt" means the shape
carries over and the numbers do not. "Anchor" means keep it as an analogy only.

### 2A. Loot and affix generation (primarily ch 08)

**A-1 · Diablo II Magic/Rare affix tables.** Prefixes and suffixes live in flat, tab-delimited tables
(`MagicPrefix.txt` / `MagicSuffix.txt`). Each entry gives a stat, a value range, eligible item types,
and a level requirement, and references a stat ID whose behavior is defined once in `ItemStatCost`.
Magic items roll 50% suffix-only, 25% prefix-only, 25% both. Rare items get up to 6 affixes (≤3
prefixes + ≤3 suffixes). *Source:* A1. *Chapter:* 08 (adapt the table layout), 00 (adopt the shared
effect-definition table).

**A-2 · Diablo II affix level (alvl) gate.** `alvl = ilvl − qlvl/2` when `ilvl < 99 − qlvl/2`,
otherwise `alvl = 2·ilvl − 99`. ilvl is capped at 99 and raised to qlvl if lower. An affix is eligible
only if its level ≤ alvl, which is a hard cutoff, not a weight. The required level to use the item is
≈ 75% of alvl. *Source:* A1. *Chapter:* 08 + 09 (adapt: the source's threat band acts as ilvl and
gates property tiers).

**A-3 · Diablo II Unique and Set items.** A separate, hand-authored data type with a fixed name and a
fixed list of 3–8 properties. Some values roll in narrow ranges (e.g. 100–120% enhanced damage), but
the *set* of properties never changes. No affix-group or slot rules apply. Set items add conditional
bonuses as more pieces are equipped. *Source:* A1, A5. *Chapter:* 08 (adopt `unique` and `set` item
classes; set bonuses are [C:P6] composites).

**A-4 · Diablo III Loot 2.0 slot structure.** Up to 4 Primary + 2 Secondary affixes, with no
prefix/suffix distinction. A Legendary Power always occupies a Secondary slot so it can never crowd
out Primary rolls. All items of one legendary type draw their generated stats from the same pool. The
legendary power itself is guaranteed and non-random. *Source:* A1, A5, E1. *Chapter:* 08 (adopt
reserved signature slots), 00 (the identity/magnitude separation).

**A-5 · Diablo III Smart Loot.** Drops are guaranteed to carry class-appropriate main stats. *Source:*
A1. *Chapter:* 02 (starting kit, adopt), 08 (optional mild bias, see T-9).

**A-6 · Diablo III Enchanting.** The player may reroll one chosen non-legendary affix on demand. The
legendary power can never be rerolled. *Source:* A1. *Chapter:* 02/08 (adapt as [C:P1]'s deferred
reroll: reroll one non-signature property, never the signature).

**A-7 · Diablo III launch itemization failure.** In 2012, rare and legendary stats rolled "completely
random[ly]," with no structure. Players endured it for about 2 years until Loot 2.0 (2014, Reaper of
Souls) imposed structure. *Source:* A1, E1. *Chapter:* 08 (anchor: evidence against unconstrained
generation).

**A-8 · Diablo IV Tempering.** A world-dropped, hand-authored Temper Manual teaches a recipe of 3–5
possible affixes grouped by theme (e.g. "Mobility"). Applying the recipe to an item randomly picks one
listed affix and rolls its value. It adds one extra deterministic *affix slot* to Rare, Legendary,
Unique, and Mythic items. That makes three independently tuned layers: found category → constrained
random pick → numeric roll. *Source:* A1, E1. *Chapter:* 08 (adapt for crafting: a technique learned
→ random pick among its options → magnitude).

**A-9 · Diablo IV Greater Affix and Ancestral.** A Greater Affix is a random +50% on a rolled value and
also grants a reroll chance. Ancestral items are guaranteed at least one GA and get 2 temper slots.
*Source:* A1. *Chapter:* 08 + 01 (adapt: a critical-success fill upgrades one property ×1.5 and/or
opens a slot).

**A-10 · Diablo IV Codex of Power.** Legendary Aspects and temper recipes, once found, are stored
permanently at the account level and can be imprinted onto any suitable generated item indefinitely.
Signature content becomes a reusable library, not a consumable drop. *Source:* A1, A5. *Chapter:* 08
(crafting recipes), 04 (the absorber library), 11 (legacy inheritance).

**A-11 · PoE mod classification.** Every mod has a **domain** (which entity type it may appear on) and a
**generation type** (prefix / suffix / corrupted-only / always-applied), assigned before any weighting.
*Source:* A2. *Chapter:* 00/03 (adopt: tags declare domain), 08.

**A-12 · PoE tag-weighted spawning.** The base item carries an ordered tag list (e.g. `str_armour,
body_armour, armour, default`). Each mod lists a spawn weight per tag. Weights are matched against the
item's tags, and mods with a resulting weight of 0 are ineligible. P(mod) = its weight / the sum of
eligible weights. The source gives two conflicting descriptions of multi-tag resolution: "sums the
matching weights" and "left-most tags … most significant" (the latter unverified). *Source:* A2, E1.
*Chapter:* 08 (adopt the filter-then-weight shape), 03 (hierarchy; use most-specific-wins, see 03.1).

**A-13 · PoE affix tiers gated by item level.** Each mod family has discrete tiers (e.g. life, where a
low tier gives ~10–20 and a high tier ~80–90). Higher ilvl raises tier eligibility and chance.
*Source:* A2. *Chapter:* 08 (adopt with threat bands).

**A-14 · PoE mod groups.** Only one mod per group may exist on an item. The exclusivity is scoped
separately to prefixes and to suffixes, so the same family can appear once in each. Example: two tiers
of "% increased life" cannot both be prefixes. *Source:* A2, E1. *Chapter:* 08 (adopt `mod_group`), 05
(adapt: one-copy rule for ability modifiers).

**A-15 · PoE per-item cap.** Every non-unique item has at most 3 prefixes + 3 suffixes = 6 rolled
affixes, "regardless of how many thousands of possible mods exist in the underlying table." *Source:*
A2, E1. *Chapter:* 08, 05 (the "bound the count, not the table" principle).

**A-16 · PoE Essence.** It upgrades a base item to Rare with one *guaranteed* affix, and the rest roll
normally from the weighted table. Higher tiers (tier 5 "Screaming"+) can fully reforge an existing
rare, overriding meta-crafted mods. *Source:* A2, E1. *Chapter:* 08 (adapt as the "guaranteed
signature" fill), matching the probe's `guaranteed` fill.

**A-17 · PoE Fossils (in resonators).** They bias the weighting toward specific mod types or tags on the
same underlying table, at a higher cost than essences. *Source:* A2. *Chapter:* 08 (adapt as the
"biased" fill), matching the probe's `weighted` + `biased_toward` fill.

**A-18 · PoE Crafting Bench.** It deterministically adds one specific chosen prefix or suffix to an
item with an open slot. The mod is guaranteed, and its value may still roll in range. It also handles
sockets, links, and colors. *Source:* A2. *Chapter:* 08 (adopt as the "chosen" fill for deliberate
crafting).

**A-19 · PoE trade-site stat filter and pseudo mods.** Players can search for any single modifier in the
game, and the site computes derived composite stats (e.g. total elemental resistance) because raw mods
are too fragmented to reason about. *Source:* A2. *Chapter:* 14 (adopt codex rollups), 08.

**A-20 · Craft of Exile (third-party).** It simulates tier tables, weights, and per-craft probabilities
that the game never shows. *Source:* A2. *Chapter:* 14 (anchor: the codex can show odds out of
fiction).

**A-21 · PoE2 fixed-count rares.** A rare created with orbs gets exactly 4 modifiers, replacing a
variable 2–6. *Source:* A3. *Chapter:* 08 (adopt a fixed property count per rarity tier).

**A-22 · PoE2 currency removals.** Orb of Scouring, Chromatic, Jeweller's, and Fusing were removed. The
socket currencies went because sockets were decoupled from gear. *Source:* A3. *Chapter:* anchor for
[C:VI]: an example of structural retirement by removing a whole subsystem.

**A-23 · PoE2 single crafted modifier (Alloy).** Each item may carry only one crafted modifier, and the
Alloy currency occupies "that exact crafted modifier slot." *Source:* A3. *Chapter:* 08 (adopt: at most
one player-crafted property per item).

**A-24 · Borderlands parts and manufacturer gating.** Guns are assembled from ~35 part categories drawn
from ~1,500–1,700 part instances (BL3; unverified). The manufacturer selects the entire eligible part
pool and the behavioral scripts. BL3 bans cross-manufacturer parts, because "each manufacturer has
multiple variants for each part." Gearbox kept a "gun map" compatibility chart so generated guns
"read" as their brand. The scale is 1B+ (BL3) and ~30B (BL4) permutations across ~12 brands.
*Source:* A4, E1. *Chapter:* 08/09/13 (adopt: the source replaces the pool; an authored compatibility
map).

**A-25 · Borderlands signature manufacturer behaviors.** Tediore: reloading throws the gun as an
exploding grenade and a new copy "digistructs," expressing "cheap and disposable." Maliwan: elemental
only, higher elemental uptime, a prestige brand. Jakobs: never elemental, with high base damage, low
fire rate and reload speed, and high crit multipliers ("keep it simple, no gimmicks"). *Source:* A4.
*Chapter:* 13 (maker traditions), 08.

**A-26 · RoR2 Category Chests.** They drop only items tagged Damage, Healing, or Utility respectively.
*Source:* RG4. *Chapter:* 08 (adapt a "choose the category" fill for gifts and commissions).

**A-27 · Feature 003 probe generator.** `resolve_ability_grant(source, method)`: validate both against
closed dicts (raise on unknown). If the method is `guaranteed`, return the pool's single
`is_signature` template. If it is `weighted`, sample with weight 3 for templates matching
`biased_toward` and 1 otherwise (60/20/20 over a 3-template pool). The model supplies only the
classifications. *Source:* AP, TC3, IR3. *Chapter:* 08/04 (keep the shape and extend it with magnitude,
tiers, groups, and chosen/greater fills).

### 2B. Combination and synergy architectures (ch 05, 03, 04)

**B-1 · Hades Duo Boons.** About 30 hand-authored combination boons (Hades I; 10–30 in sources), keyed
to pairs of 8 gods: C(8,2) = 28 pairs, typically 1 duo per pair. A duo becomes offerable once the
player holds one specific named boon from each of the two gods. Vengeful Mood requires 3 prerequisites
instead of 2. Some pairs are explicitly incompatible (Cold Embrace + Crystal Clarity). Hades II has 37
duos over 9 gods, C(9,2) = 36 pairs. *Source:* RG1, RG5, E2. *Chapter:* 04 (the hybrid table keyed to
tag-branch pairs), 13 (patrons).

**B-2 · Hades slots.** Boons occupy exclusive slots: Attack/Strike, Special/Flourish, Cast/Shot, Dash,
Call/Aid. Duo prerequisites name specific boons, not "any boon in slot X." *Source:* RG1. *Chapter:* 05
(anchor for per-slot exclusivity).

**B-3 · Slay the Spire event hooks.** Cards, relics, and powers independently subscribe to shared combat
hooks (BaseMod: `OnCardUse`, `OnPlayerDamaged`, `OnPowersModified`, `PostBattle`, `PostDraw`,
`PostExhaust`, `RelicGet`). No combination table exists. Effects on the same trigger compose
automatically. The core combat rules are "the same five or six rules every turn." Balance came from
telemetry, per the 2019 GDC talk "Metrics Driven Design and Balance." *Source:* RG2, RG5, E2. *Chapter:*
00/05 (adopt a closed hook list), 12 (log-driven review).

**B-4 · Isaac stat cache.** Passive stat items register cache flags (`AddCacheFlags`), and
`EvaluateItems` recomputes the affected stats in one pass (`MC_EVALUATE_CACHE`). Vanilla effects apply
before modded ones. It handles 700+ items with no pairwise logic. *Source:* RG3, E2. *Chapter:* 00/01
(adopt one ordered evaluation pass).

**B-5 · Isaac tear-replacer priority.** Items that replace the attack's form have per-pair documented
outcomes that amount to a rank order: Mom's Knife > Brimstone; Haemolacria > Brimstone; Ludovico + Mom's
Knife overrides Brimstone; Technology + Brimstone gives visually coiled beams, and Technology loses its
damage multiplier. *Source:* RG3, E2. *Chapter:* 05 (adopt a `priority_rank` per slot-claiming effect;
the suppressed effect's bonus is lost unless marked cosmetic).

**B-6 · Isaac item tags as unlock counters.** The `tearsup` tag marks tear-rate items, and collecting
enough in a run counts toward the Lachryphagy unlock. *Source:* RG3. *Chapter:* 03 (a precedent for
tag tallies toward unlocks).

**B-7 · RoR2 proc coefficient.** Every ability or attack has a coefficient (nominally 0–1, though the
same source's example uses 3.0). An on-hit item's effective chance = item chance × coefficient (e.g.
10% bleed × 0.6 = 6%). Each on-hit item rolls independently, and there is no priority system.
*Source:* RG4, E2. *Chapter:* 05/00 (adapt a `trigger_coefficient` per ability).

**B-8 · RoR2 proc chains and the DoT terminator.** When one proc triggers another, each step computes
from the previous step's damage, without the original hit's bonuses. DoTs (Bleed, Burn) have a
coefficient of 0.0, so they never re-trigger on-hit effects. That is one global loop-breaker.
*Source:* RG4, E2. *Chapter:* 00/05 (adopt: effect-triggered effects do not fire hooks).

**B-9 · RoR2 stacking families.** Only two formula families cover the whole pool: linear `f(x) = 1 +
a·x`, and hyperbolic for percentage effects that must never reach 100% (standard form `1 − 1/(1+a·x)`,
[R3], not in source). *Source:* RG4, E2. *Chapter:* 00/05/08 (adopt: every stackable declares its
family).

**B-10 · RoR2 ItemTags.** Classification metadata (Damage, Healing, Utility, AIBlacklist,
BrotherBlacklist, OnKillEffect, CannotCopy) governs loot eligibility, AI exclusion, and copy
restrictions, not trigger order. *Source:* RG4. *Chapter:* 03/09/04 (adopt `player_only`,
`adversary_only`, `cannot_absorb`).

**B-11 · The cross-case rule.** Additive effects go through a shared pipeline. Probabilistic triggers
are independent with coefficients. Slot-claiming effects use a priority rank. Named combos are allowed
only on a low-cardinality key. *Source:* RG5, E2, E5, E7. *Chapter:* 05 (adopt as the four-regime
table, 05.5).

### 2C. Tags and classification (ch 03)

**C-1 · PoE tag cascade (item-side).** A base item's ordered tag list runs from specific to general, so
a body armour is simultaneously `str_armour`, `body_armour`, `armour`, and `default`. Constitution
[C:P5] cites PoE's tag cascade as its precedent for behavioral-tag hierarchy. *Source:* A2, and the
constitution. *Chapter:* 03.

**C-2 · PoE gem-tag compatibility.** Support gems apply only to skills that carry the required tag
(GMP → Projectile). *Source:* PG1. *Chapter:* 05/03 (adopt: modifiers declare required ability tags).

**C-3 · D4 shared theme taxonomy.** The same category scheme (e.g. "Mobility") classifies both temper
recipes and Legendary Aspects. *Source:* A1. *Chapter:* 00/03 (one vocabulary across content types).

### 2D. Class emergence, progression, and consolidation (ch 04, 02, 03)

**D-1 · Delve Primary and Secondary Requirements.** *Primary* (eligibility) is a category rank-count
("≥4 skills at rank ≥5 in Offensive Auras / Defensive Auras / Aura Metamagic") or a stat ratio
("Clarity ≥ 5× Focus" for Dynamo). *Secondary* (trigger) is a cumulative counter:
- Remedial Scourge Beacon: ≥50 kills via Offensive Auras.
- Remedial Warder Beacon: ≥1,000 damage mitigated for self or allies.
- Remedial Meta-Beacon: ≥5,000 mana spent through Aura Metamagic.
- Dynamo: mana recovered plus diverse kill types.

The system is legible once unlocked and opaque in advance. *Source:* L1, L2, E3. *Chapter:* 04 (adopt
the structure), 03 (counter kinds).

**D-2 · Delve tier families.** Remedial → High → Legendary within a class family. Legendary Dynamo
requires holding Dynamo with all stat points in Clarity *and* ≥1,000,000 total mana recovered. Classes
carry rarity labels (Rare). *Source:* L1, L2, L4. *Chapter:* 04 (adapt tier deepening per [C:P2]).

**D-3 · Wandering Inn action-based acquisition.** Sustained behavior matching a profession triggers a
class ([Innkeeper] after running an inn). Re-evaluation "usually" happens at 10-level intervals, with
off-schedule "off-classes" for dramatic shifts. Semi-transparent: characters know classes exist and
recognize gains but cannot predict timing. *Source:* L1, L2, L4, E3. *Chapter:* 04, 03 (checkpoint
cadence).

**D-4 · Wandering Inn authority-based grant.** A ruler with sufficient authority can grant a class
directly (an Emperor grants [General]) with no action prerequisite, a separate mechanism from
emergence. *Source:* L1. *Chapter:* 04/11 (adapt as conferral; bounded, see T-13).

**D-5 · Wandering Inn consolidation.** Two or more sufficiently advanced classes merge into a new named
class: [Warrior] + [Strategist] → [Commander]; [Princess] + [Warrior] + [Barmaid] + [Beast Tamer] +
[Carer] + [Tactician] → [Worldly Princess]. A secondary class must be advanced "sufficiently to inform"
the primary (a plurality/threshold merge). No numeric trigger is given. *Source:* L3, E3. *Chapter:* 04
(adopt the named merge; author the trigger).

**D-6 · Wandering Inn post-grant change paths.** Specialization ([Warrior] → [Spearmaster] after
exclusive spear use), advancement ([Tactician] → [Strategist]), and circumstantial shift ([Warrior] →
[Wounded Warrior] after a permanent injury). *Source:* L4. *Chapter:* 04, 07.

**D-7 · Threadbare per-activity classes.** Repeated task-specific actions produce many concurrent
classes (Greater Toy Golem, Cave Bear, Ruler, Tailor, Model, Necromancer, Duelist, Animator, Enchanter,
Golemist, Scout, Smith, Sculptor, Shaman), implying one counter per class. *Source:* L1, L2.
*Chapter:* 03/04 (independent specialist counters; the need for a concurrency cap).

**D-8 · Defiance of the Fall first class.** The first class is granted at character level 25,
retrospectively, "mainly based on achievements and experiences," with no visible formula. Many classes
are hidden or rare. *Source:* L1, L2. *Chapter:* 02/04 (a first-recognition checkpoint; the floor
before it).

**D-9 · Azarinth Healer.** Dual class slots, and "every skill, class, and ability can evolve." The
class label (Healer) diverges from the lived playstyle (melee skirmishing with self-regeneration). The
base class grants a flat stat package: +10 Vitality, +5 Strength, +5 Dexterity, +10 Intelligence, +10
Wisdom. *Source:* L1, L2. *Chapter:* 04 (concurrency cap ≈ 2; a warning that labels must re-derive).

**D-10 · Randidly Ghosthound classed versus classless.** Classed characters can level but have a capped
skill count. Classless characters can learn unlimited skills but cannot level conventionally. The
source explicitly rules this out as an aggregate-to-class precedent. *Source:* L1. *Chapter:* 02
(anchor for [C:P4] breadth-versus-competence).

**D-11 · WoW original talent trees (2004–2008).** 51 points at launch, 71 by Wrath, spread over 3 trees.
A 31-point capstone per tree meant no one could reach two. Five-point filler talents (e.g. +1% crit per
point) caused bloat. Costly respecs discouraged experimentation and produced cookie-cutter builds.
*Source:* WT1. *Chapter:* 04 (anchor: cap-forced specialization; warns against filler).

**D-12 · WoW Cataclysm (4.0, Nov 2010).** 41 points, and 31 in the primary tree before branching.
"Concentrated coolness." This produced "even more cookie cutter builds" and punished hybrids until high
levels. *Source:* WT1. *Chapter:* 04 (warns against deep single-track prerequisites for hybrids).

**D-13 · WoW Mists of Pandaria (5.0, Sep 2012).** Six tiers × 3 choices = 18 talents, one choice per
tier every 15 levels, no points, and tiers are independent. Warlords (6.0) added a 7th tier, making 21.
This held, with tweaks, through Shadowlands. *Source:* WT1. *Chapter:* 04 (adopt "choose 1 of ≤3 at each
crystallization"; 3^6 = 729 builds [R3]).

**D-14 · WoW Legion free spec swap.** Free switching between specs, with each spec's talents
auto-saved. *Source:* WT1 (the claim that this was new in Legion is questionable, see T-R6). *Chapter:*
04/05 (saved loadouts per calling).

**D-15 · WoW Dragonflight trees (10.0, Nov 2022).** Two trees (class-wide and spec) after a 12-year
absence. The class tree lets you take abilities from other specs "for hybrid flavor." Row 5+ is gated
behind 8 spent points and row 8+ behind 20. Five-point talents were removed. Goals: agency, meaningful
leveling rewards, class and spec connection. *Source:* WT1. *Chapter:* 04 (gate tiers on cumulative
investment), 02 (a shared "class tree" as a candidate shape for the P2 floor).

**D-16 · PoE2 ascendancy.** 12 base classes × 3 ascendancies = 36 (the node-count source says 22
ascendancy trees and 409 nodes, see T-R4). Ascendancies unlock through campaign Ascension Trials in
Acts 2, 3, and 4. Higher trials give more points. Ascendancy notables can grant skills that accept
supports. The base class is locked and the ascendancy is swappable. *Source:* PG4, W2. *Chapter:* 02/04
(lock the base, swap the specialization).

**D-17 · EVE skill training.** 400+ skills, each trainable to level 5 in real time (online or offline)
at a rate set by attributes, a per-skill multiplier, and the target level. Maxing everything takes ~20
years. Prerequisite chains gate advanced skills. Skill points are permanent unless removed with a
costed Skill Extractor. There are 4 Academy pathways (Explorer, Enforcer, Industrialist, Soldier of
Fortune). *Source:* MM3, W1. *Chapter:* 10 (downtime training), 04 (respec cost), [C:P15].

**D-18 · The report's proposed hybrid-trigger status.** "No source in any series gives an explicit
numeric tie-break rule — this piece must be authored fresh." *Source:* E3, E5, E7, L3. *Chapter:* 04.

### 2E. Abilities, modifiers, and behavior tags (ch 05)

**E-1 · PoE1 gem sockets.** Active skill gems socket into gear, and support gems must be linked in the
same item's socket chain. Endgame builds use 6-links: typically 1–2 main skills with several supports.
A support grants no active ability, modifies the linked skills, and typically raises mana cost.
*Source:* PG1. *Chapter:* 05 (adapt modifiers that raise Focus cost).

**E-2 · PoE2 gem sockets.** Support sockets live on the skill gem itself, not on gear. Up to 9 active
skills, each with up to 5 supports. Only one copy of any support in the whole loadout. Skills are
weapon- and animation-based to discourage single-button builds. *Source:* PG1, W2. *Chapter:* 05 (adopt
the per-skill modifier cap and the one-copy rule).

**E-3 · Pierce / Fork / Chain / Return.** Pierce: the projectile passes through the target and
continues (first priority). Fork: it splits into two at ±60° (once, unless Awakened Fork). Chain: it
redirects to another nearby enemy, with the count set by gem level. Return comes back. Resolution
order: pierce to its maximum, then fork, then chain. Only one behavior resolves per collision.
Combinations have no names. *Source:* PG2, W2. *Chapter:* 05 (priority-ranked behavior tags), 06
(multi-target over relationship-state, 06.3).

**E-4 · Multiple Projectiles.** PoE1 GMP: +4 projectiles, +10% increased projectile damage, 26% less
projectile damage. PoE2 MP: +2 projectiles, 20% less projectile damage, 20% less attack/cast speed.
LMP + GMP gives 6 extra (PoE1). The "less damage" penalty does not reduce poison, so the gem synergizes
with fast-hitting poison builds (Barrage, Tornado Shot). *Source:* PG2, W2. *Chapter:* 05 (adopt
behavior + penalty modifiers; one gem can be an upgrade for one archetype and a trade for another).

**E-5 · PoE keystones.** About 33 passives that fundamentally change mechanics, often with big
downsides. Acrobatics (PoE1): extra dodge chance, but penalties to armour, energy shield, and block.
*Source:* PG3. *Chapter:* 04/05 (top-tier calling bonuses shaped as keystones).

**E-6 · PoE2 Acrobatics fold-in.** The keystone was deleted, and its core (evasion applies to all hits)
became part of base evasion. *Source:* PG3, W2. *Chapter:* 04/05 ([C:VI] fold-into-base retirement).

**E-7 · PoE2 passive-tree retirements.** Life nodes were removed (survivability moved to gear),
Masteries removed, the Scion class removed, all classes start in the middle by attribute and archetype
alignment, and travel nodes became selectable (+5 Str, Int, or Dex). *Source:* PG3, W2. *Chapter:* 04/07
(retirement examples; the Vitality source question).

**E-8 · PoE2 weapon-swap passive points.** Specific passive points are active only with a given
weapon set equipped. *Source:* PG3. *Chapter:* 05/08 (conditional passives by equipped item).

**E-9 · GW2 weapon skills.** Each weapon set gives 5 skills (main hand 3 + off hand 2, or two-handed 5).
There are two sets, swappable in combat except for Elementalist and Engineer. Traits reward swapping
(Brutality: gain quickness on swap; Quick Draw: quickness plus a faster next skill recharge). Elite
specializations replace a trait line and unlock new weapons and skills. *Source:* MM2, W1. *Chapter:*
08 (items license abilities), 05 (loadout swap costs).

**E-10 · FFXIV Kaiten removal.** Samurai's Kaiten, a pre-attack resource button, was removed and
certain attacks became auto-crit. It is a consolidation of a no-decision step, and the community still
counted it as lost identity. *Source:* MM1, W1. *Chapter:* 05 (fold always-paired steps, but only at a
boundary).

**E-11 · Probe templates (P10 exemplars and failure).** 12 templates, each with a trigger/limit phrase.
Heat Resistance's "no protection against cold" was narrated as an active vulnerability, which the
auditor caught (5/6 consistency). *Source:* AP, IR3. *Chapter:* 05 (separate scope, limitation,
weakness, and cost fields).

### 2F. Resources, cadence, and turn structure (ch 05, 06)

**F-1 · WoW resource types.** Mana: consumed by spells, regenerates slowly, used by all classes except
rogues and warriors. Rage: generated by damage taken and dealt. Energy: fast regeneration, cap 100.
Focus (hunters): energy-like, slower regeneration. Runic Power: generated by spending runes, cap 100,
with fixed costs (Death Coil 50) or per-second drains. *Source:* WT5. *Chapter:* 05 (adapt:
calling-specific Focus *generation* over a unified pool, see T-1).

**F-2 · WoW Global Cooldown.** Every ability triggers a shared cooldown: base 1.5 s, but 1.0 s for
rogues, cat-form druids, and monks. Haste lowers the 1.5-s GCD to a floor of 0.75 s (1.0 s before
Legion) and does not affect the 1.0-s group. Its purpose is to stop "combining multiple effects into one
action." *Source:* WT5, CX2, W3. *Chapter:* 01 (one activation per action), 06/[C:P14] (cadence
asymmetry, translated per 06.4).

**F-3 · WoW GCD expansion and reversal.** BfA extended the GCD to offensive buff cooldowns for
"significance." Players "still had to go through exactly the same rotations … just with far more
stop-gaps." After about 2 years of complaints, Shadowlands removed it from most burst cooldowns while
keeping it on offensive buffs. Criticism of "cooldown-centric design" continued. *Source:* CX5, W3.
*Chapter:* 06/05 (check that a throttle creates a decision).

**F-4 · Ironsworn Enter the Fray and Strike.** Enter the Fray: face-off +heart, unaware foe +shadow,
ambushed +wits; a strong hit gives +2 momentum and initiative. Strike needs initiative: close quarters
+iron, at range +edge; a strong hit gives +1 harm and keeps initiative, a weak hit gives harm and loses
initiative. *Source:* FP4, E4. *Chapter:* 01 (approach-keyed attribute), 06 (initiative token).

**F-5 · Mörk Borg skirmish initiative.** The whole party acts in the same round against the opposition,
choosing its own order, with a flat ±3 for positional advantage. *Source:* FP5, E4. *Chapter:* 06, 01.

**F-6 · Dungeon World flow.** No initiative or action economy, and seamless transitions. The GM makes
moves in response to player actions and misses. *Source:* FP3. *Chapter:* 06 (anchor; contrast with
[C:P9]).

**F-7 · Monster of the Week.** The Keeper does not roll for monsters and reacts to the hunters' rolls.
Combat often comes down to one roll: "if you win and what price you paid." *Source:* FP3. *Chapter:*
06/09 (the "who rolls" decision, T-16).

### 2G. Positioning as relationship-state (ch 06)

**G-1 · Blades Position/Effect.** A 3×3 grid: Controlled/Risky/Desperate × Limited/Standard/Great. The
GM sets both after the action is declared and before the roll. Default Risky/Standard, modified by the
action used, the opposition's strength, and effect factors. Spatial facts fold into Position. Players can
Push (spend Stress) for Effect, or trade one step of Position for one step of Effect. *Source:* FP1, E4.
*Chapter:* 01/06/07.

**G-2 · Blades opposed clocks.** An Escape clock (PCs) races a Cornered clock (pursuers). Whoever fills
first wins, so the PCs either escape or are cornered and cannot flee. *Source:* FP1. *Chapter:* 06/07/10/11.

**G-3 · Blades partial-success rule for positioning.** On a 4/5, the positioning goal still happens with
a complication. The GM never answers "they escape." *Source:* FP1. *Chapter:* 01/06.

**G-4 · Fate zones.** 2–4 per scene, rarely over ~6 ("cumbersome"). Mass combat uses players + 1. A
zone is punching distance. Fight works within a zone, Shoot up to 2 zones away. One zone of movement is
free with an action; more, or a hindered zone, requires an Athletics overcome. There is no
firing-into-melee rule (aspects handle it). *Source:* FP2, E4. *Chapter:* 06, 10.

**G-5 · Dungeon World range bands.** Hand, Close, Reach, Near, Far, with no numeric distances. Weapons
and moves carry the band they need. *Source:* FP3. *Chapter:* 06 (adopt as the band ladder candidate).

**G-6 · PbtA positioning by consequence.** A partial dodge leaves the orc between the PC and the party.
"Separate them" is an MC move. Positioning is one currency among many GM moves. *Source:* FP3.
*Chapter:* 06/12.

**G-7 · Ironsworn close/range binary.** → F-4. *Chapter:* 06.

**G-8 · Mörk Borg ±3.** A flat modifier for flanking or high ground, and nothing more. *Source:* FP5.
*Chapter:* 01/06.

**G-9 · ChatRPG Battle tool.** v1 (unstructured) produced self-injury and wrong targets. v2 used a
structured tool specifying "attack order, hit chances, and damage severity for each exchange" as JSON,
few-shot examples in the tool description, and a specialized Narrator agent. It had no spatial state,
which the paper flags as future work. *Source:* FP6, E4. *Chapter:* 00/06/12.

**G-10 · Commercial AI-GM fork.** Friends & Fables uses hex battlemaps and token movement. RoleForge
and DungeonsDeep.ai keep prose over a deterministic rules engine. Both claims come from blogs.
*Source:* FP6. *Chapter:* 06 (anchor).

### 2H. Balance, live operations, consolidation, and retirement (ch 04, 05, 12, principle VI)

**H-1 · WoW stat squishes.**
- 6.0.2 (14 Oct 2014): ~96% stats, ~92% health; the Fireball went from 450,000/3,000,000 to
  30,000/200,000 (15%); it moved to linear item scaling and was demoed at BlizzCon 2013.
- 8.0.1 (2018): stats and item level.
- 9.0.1 (Nov 2020): stats, item level, and character levels 120 → 50 (new cap 60), the first level
  squish.
- 12.0.0 "Midnight" (dated 2024 in the source): stats and item level.

The first developer blog came on 3 Nov 2011, citing the 32-bit (~2.1B) limit. Squishes retire nothing.
*Source:* WT2, W4. *Chapter:* 00 (bounded scales), [C:VI].

**H-2 · WoW Survival Hunter rework (Legion 7.0, Aug 2016).** Ranged became melee with no reversion
path. The community split into revert and refine camps for at least 2 expansions, and in 2017
Hazzikostas said "execution needs work but we're committed." Blizzard's research: "rework after rework
put off far more people than it turned on." *Source:* WT4, W4, [C:VI]. *Chapter:* 04/12.

**H-3 · PoE league cycle.** Each 3-month league adds one new mechanic, revealed with balance changes
via livestream and notes, in 4 variants (SC, HC, SSF, HC SSF). Mid-league patches are small and
surgical. At the end, the mechanic is integrated, reworked, or discarded. *Source:* PG6, W4. *Chapter:*
04/05 (provisional status), 11 (seasonal world content).

**H-4 · Buff-over-nerf.** PoE2 is "balancing through buffs rather than heavy nerfs … almost every
ascendancy and class [has] multiple playable options." GW2 highlights underused skills. *Source:* PG5,
MM2, W1. *Chapter:* 12.

**H-5 · The PoE2 jewel meta.** One layer of a 4+-layer system grew strong enough that stacking jewel
sockets threatens build creativity. *Source:* PG5, W2. *Chapter:* 00 (per-layer power budget).

**H-6 · FFXIV tight balance.** One weapon per job, all abilities from leveling and job quests, potency
tuning within role categories (Patch 7.5), and no new healer so the existing 3 stay balanced. Every job
is viable in world-first clears, at the cost of homogenization. Yoshida: "adding new jobs has become
rather cumbersome, as maintaining the uniqueness of job mechanics while balancing their numbers has
become extremely taxing." It scales linearly. *Source:* MM1, W1. *Chapter:* 04 (warning), 09.

**H-7 · GW2 living-document balance.** A published philosophy with small monthly changes and infrequent
major overhauls. The team admits "not everything in the guidelines align with the reality" and
promises incremental change. Meta convergence is accepted. It scales roughly quadratically. *Source:*
MM2, W1. *Chapter:* 12/14.

**H-8 · EVE time-gated specialization.** → D-17. It scales "logarithmically," because unbalanced
corners go unreached rather than being balanced away. *Source:* MM3, MM5, W1. *Chapter:* 10, [C:P15].

**H-9 · WoW patch tiers.** Hotfixes (server-side, instant or with a restart, several per week), x.x.5
and x.x.7 medium patches (since Legion and Dragonflight, 8–10-week lifespans), and major patches.
Cadence concerns in 12.0.x: "balance fixes can lag behind player feedback." *Source:* WT3, WT6.
*Chapter:* 12 (rulings versus amendments).

**H-10 · The Dungeon Crawler Carl fork (the constitution's prior precedent).** A skill's growth path
forks into a replacement, not an addition [C:VI]. Not re-researched this round. *Chapter:* 04/05.

### 2I. Complexity and presentation (ch 14, 12, 00)

**I-1 · WoW hidden threat.** 1 damage = 1 threat, with a 5.0× tank modifier (Righteous Fury, Blood
Presence), per-ability bonus threat, and healing threat = ½ effective healing per observing NPC ÷
observer count. It was hidden until WotLK and reverse-engineered with add-ons. *Source:* CX1, W3.
*Chapter:* 06/09 (a background attention model).

**I-2 · WoW diminishing returns.** CC: halving to 1/16 (PvE), immunity after 2 (PvP), 16-s reset.
Stats: less value after 30% (Shadowlands). *Source:* CX1, W3. *Chapter:* 06/07 (control DR), 03
(anti-grind), 05/08 (stacking DR).

**I-3 · WoW debuff display cap.** 16 shown of up to 40, and players used add-ons. *Source:* CX2, W3.
*Chapter:* 14.

**I-4 · MMO action-bar design.** Players want to "release skills quickly … accurately … with less
attention … quickly know when skills will be available." Cooldowns are "second only to being able to
see the enemy and health bars." *Source:* CX2. *Chapter:* 14 (the codex shows readiness and recharge
state prominently).

**I-5 · Path of Building.** A third-party calculator for DPS, DoT, and life, mana, and ES totals
"factoring in auras, buffs, charges, curses, monster resistances." It was de facto mandatory, and GGG
later built an official planner. *Source:* CX3, W3. *Chapter:* 14.

**I-6 · Hidden-information design.** A weapon with 10 stats also shows "level" and "suggested class."
"Half of game design is game design, and the other half is simplification." *Source:* CX4. *Chapter:*
14.

**I-7 · The Hodent and 7±2 numbers.** 3 items maximum while learning, 5±2 when familiar, 7±2 in UI
guidance. *Source:* CX2, CX4, W3. *Chapter:* 14 (presentation only, per the BRIEF).

**I-8 · The complexity trichotomy.** Comprehension, tracking, and depth (Game Developer). *Source:*
CX4, W3. *Chapter:* 14/12.


---

## 3. Numbers ledger

Grouped by domain. "Use" suggests which chapter might calibrate against the number. [R3] marks my own
arithmetic.

### 3.1 Item and affix generation
| Number | What | Context / caveat | Source |
|---|---|---|---|
| 50% / 25% / 25% | D2 magic item: suffix-only / prefix-only / both | Per-item affix composition | A1 |
| 6 (3+3) | D2 rare affix maximum | Any combination up to the cap | A1 |
| 99 | D2 ilvl cap | ilvl is raised to qlvl if lower | A1 |
| `ilvl − qlvl/2` / `2·ilvl − 99` | D2 alvl branches | Break point at `99 − qlvl/2` | A1 |
| ≈75% | D2 required level as a fraction of alvl | Equip requirement | A1 |
| 40 / 91 | [R3] alvl worked examples | ilvl 50 / qlvl 20 → 40; ilvl 95 / qlvl 20 → 91 | A1 + R3 |
| 3–8 | D2 Unique property count | Fixed set; narrow ranges, e.g. 100–120% ED | A1 |
| 4 + 2 | D3 Primary + Secondary affix slots | Legendary power always in a Secondary slot | A1 |
| ~2 years (2012–2014) | D3 launch loot left unconstrained | Until Loot 2.0 (Reaper of Souls, 2014) | A1 |
| 3–5 | Affixes per D4 Temper recipe | Themed, e.g. "Mobility" | A1 |
| +50% | D4 Greater Affix bonus to a rolled value | Also grants a reroll chance | A1 |
| ≥1 GA, 2 temper slots | D4 Ancestral guarantees | | A1 |
| 3 + 3 = 6 | PoE non-unique affix cap | Independent of mod-table size | A2, E1 |
| ~10–20 vs ~80–90 | PoE life mod low tier vs high tier | Tier example | A2 |
| Tier 5 ("Screaming") | PoE essence tier that can reforge a rare | | A2 |
| exactly 4 | PoE2 rare modifier count via orbs | PoE1 was a variable 2–6 | A3 |
| 4 | PoE2 currencies removed (Scouring, Chromatic, Jeweller's, Fusing) | | A3 |
| 1 | PoE2 crafted modifiers per item (Alloy) | | A3 |
| ~35 | BL3 weapon part categories | Unverified secondary | A4 |
| ~1,500–1,700 | BL3 part instances | Unverified secondary | A4 |
| 1 billion+ / ~30 billion | BL3 / BL4 gun permutations | BL4 = 30× BL3 | A4 |
| ~12 ("about a dozen") | BL4 manufacturers | | A4 |
| 3 | RoR2 Category Chest categories (Damage/Healing/Utility) | | RG4 |
| 4 × 3 × 3 | Probe: archetypes × methods × templates per pool | 1 signature per pool | AP |
| 3 : 1 | Probe biased : unbiased weight | Never a disguised guarantee | AP |
| 60% / 20% / 20% | [R3] probe weighted-fill outcome over a 3-template pool | 3/(3+1+1) | AP + R3 |

### 3.2 Combination and synergy
| Number | What | Context | Source |
|---|---|---|---|
| 8 / ~30 | Hades I gods / duo boons | Estimates ranged 10–30; not canonically verified | RG1 |
| 28 | C(8,2) god pairs, Hades I | Typically 1 duo per pair | RG1, RG5 |
| 9 / 37 / 36 | Hades II gods / duos / C(9,2) pairs | ≈1 duo per pair | RG1 |
| 1 per god (typical); 3 (Vengeful Mood) | Duo prerequisite boons | Named exception | RG1 |
| 5 | Hades boon slots | Attack, Special, Cast, Dash, Call | RG1 |
| 700+ / 720+ | Isaac items | Community synergy documentation | RG3 |
| "5 or 6" | Slay the Spire core rules per turn | Design commentary | RG2 |
| 2019 | GDC "Slay the Spire: Metrics Driven Design and Balance" | Giovannetti | RG2 |
| 0–1 (nominal); 0.6, 3.0 examples | RoR2 proc coefficient | 10% × 0.6 = 6%; "30% with 3.0" contradicts the 0–1 range | RG4 |
| 0.0 | RoR2 DoT coefficient | The chain terminator | RG4 |
| 2 | RoR2 stacking formula families | Linear, hyperbolic | RG4 |
| 13.0 / 23.1 / 42.9 / 60.0% | [R3] hyperbolic 1−1/(1+0.15x) at x = 1/2/5/10 | Illustrative, not in source | R3 |
| C(k,2) | [R3] maximum hybrid pairs for k branches | k=6→15, 7→21, 8→28, 9→36, 10→45 | R3 |

### 3.3 Class emergence and progression
| Number | What | Context | Source |
|---|---|---|---|
| ≥4 skills at rank ≥5 | Delve primary requirement (Beacon family) | Per category | L1, L2 |
| ≥50 kills | Delve Remedial Scourge Beacon secondary | Via Offensive Auras | L1 |
| ≥1,000 damage mitigated | Delve Remedial Warder Beacon secondary | Self or allies | L1 |
| ≥5,000 mana | Delve Remedial Meta-Beacon secondary | Spent through Aura Metamagic | L1 |
| Clarity ≥ 5× Focus | Delve Dynamo primary (stat ratio) | Dynamo is "Rare" | L1 |
| ≥1,000,000 mana recovered | Delve Legendary Dynamo | Plus all stat points in Clarity | L1 |
| 3 | Delve tier words (Remedial, High, Legendary) | | L1, L4 |
| 10 levels | Wandering Inn usual re-evaluation interval | Off-classes are exceptions | L2, L4 |
| 2 → 1; 6 → 1 | Wandering Inn consolidation examples | [Commander]; [Worldly Princess] | L3 |
| level 25 | Defiance of the Fall first class | Retrospective | L1 |
| 14 | Threadbare's listed classes | Concurrent, one per activity | L1 |
| 2 | Azarinth Healer class slots | "Dual-class-slot" | L1 |
| +10/+5/+5/+10/+10 | Azarinth base Healer stat package (Vit/Str/Dex/Int/Wis) | 40 points total [R3] | L2 |
| 51 → 71 | WoW talent points, launch → Wrath | 3 trees | WT1 |
| 31 | WoW capstone cost | Two capstones unreachable | WT1 |
| 5-point | WoW filler talents | Removed in Dragonflight | WT1 |
| 41 (31 primary) | Cataclysm points (required primary before branching) | Nov 2010 | WT1 |
| 80+ → 18 (6×3) | MoP talent choices | One per tier every 15 levels; Sep 2012 | WT1, W4 |
| 21 (7×3) | WoD (6.0) talents | Nov 2014 | WT1 |
| 729 / 2,187 | [R3] 3^6 / 3^7 build counts | Closed combinatorics | R3 |
| 12 years | Gap before Dragonflight's return to branching trees | 2010 → 2022 | WT1 |
| 2 | Dragonflight trees (class + spec) | Nov 2022 | WT1 |
| 8 / 20 points | Dragonflight gates for row 5+ / row 8+ | | WT1 |
| 12 × 3 = 36 | PoE2 base classes × ascendancies | Conflicts with "22 ascendancy trees" | PG4, W2 |
| Acts 2, 3, 4 | PoE2 ascendancy trial locations | | PG4 |
| 400+ | EVE skills | | MM3 |
| 5 | EVE levels per skill | | MM3 |
| ~20 years | EVE time to max all skills | "two decades" | MM3, W1 |
| 4 | EVE Academy pathways | Explorer, Enforcer, Industrialist, Soldier of Fortune | MM3 |
| 1–90 / 1–80 | FFXIV / GW2 level ranges | Comparison table | MM4 |
| 3 | FFXIV healers kept at 3 | No new healer, for balance | MM1 |
| 20 (4×5) | HWFWM ability cap | Constitution precedent for the hard cap | [C:V], [C:P5] |

### 3.4 Abilities, modifiers, and slots
| Number | What | Context | Source |
|---|---|---|---|
| 6-link | PoE1 socket chain maximum | 1–2 main skills | PG1 |
| 9 | PoE2 simultaneous active skills | | PG1 |
| 5 | PoE2 supports per skill | | PG1, W2 |
| 1 | PoE2 copies of a support per loadout | Anti-stacking | PG1, W2 |
| +4, +10% increased, 26% less | PoE1 GMP | Projectile damage | PG2, W2 |
| +2, 20% less damage, 20% less speed | PoE2 Multiple Projectiles | | PG2, W2 |
| 6 | PoE1 LMP + GMP extra projectiles | | PG2 |
| ±60° | PoE Fork angles | Once, unless Awakened Fork | PG2 |
| 4 | Projectile behavior tags in priority order | Pierce > Fork > Chain > Return | PG2, W2 |
| 2,831 | PoE1 passive nodes (3.29) | Older count ~1,325 | PG3 |
| 4,524 (33 / 968 / 3,074 / 12) | PoE2 shared-tree nodes (keystones / notables / small / jewel sockets) | Conflicts with "1,200–1,500" | PG3 |
| 409 / 22 | PoE2 ascendancy nodes / trees | | PG3 |
| 1,200–1,500 | "Meaningfully distinct" passive nodes (report) | | W3, CX3 |
| +5 | PoE2 selectable travel node (Str/Int/Dex) | | PG3 |
| ~33 | PoE keystones | | PG3 |
| 5 (3+2) × 2 sets | GW2 weapon skills | Elementalist and Engineer cannot swap in combat | MM2 |

### 3.5 Resources and cadence
| Number | What | Context | Source |
|---|---|---|---|
| 1.5 s | WoW base GCD | | WT5 |
| 1.0 s | GCD for rogues, cat druids, monks | Haste does not affect it | WT5, W4 |
| 0.75 s (1.0 pre-Legion) | Haste floor on the 1.5-s GCD | | WT5 |
| 1.5× | [R3] fast group's action-rate ratio (1.5/1.0) | Why P14 ≠ P9 in turn-based play | R3 |
| 100 | WoW Energy cap; Runic Power cap | | WT5 |
| 50 | Death Coil Runic Power cost | | WT5 |
| ~2 years | BfA GCD expansion before reversal | BfA → Shadowlands | CX2 |

### 3.6 Positioning and combat flow
| Number | What | Context | Source |
|---|---|---|---|
| 3 × 3 | Blades Position × Effect | Default Risky/Standard | FP1 |
| 2 | Blades opposed clocks in a chase (Escape vs Cornered) | | FP1 |
| 4/5 | Blades partial-success roll result | Complication, not negation | FP1 |
| 2–4 (≤~6) | Fate zones per scene | ">six or so … cumbersome" | FP2 |
| players + 1 | Fate mass-combat zones | | FP2 |
| 1 free / 2 zones | Fate free movement / Shoot range | Athletics for more movement | FP2 |
| 5 | Dungeon World range bands | Hand, Close, Reach, Near, Far | FP3 |
| "as far as ten" feet | DW Reach band upper example | | FP3 |
| +2 momentum; +1 harm | Ironsworn strong-hit bonuses | Enter the Fray; Strike | FP4 |
| ±3 | Mörk Borg situational modifier | | FP5 |
| 15 pp / 60% of a DC step | [R3] ±3 on d20 | DC steps are 5 apart | R3 |

### 3.7 Balance, live operations, and complexity
| Number | What | Context | Source |
|---|---|---|---|
| 3 months | PoE league length | One mechanic each | PG6, W4 |
| 4 | PoE league variants | SC, HC, SSF, HC SSF | PG6 |
| 4 | WoW stat squishes | 2014, 2018, 2020, "2024" | WT2, W4 |
| ~96% / ~92% | 2014 squish stat / health reduction | | WT2 |
| 450k/3M → 30k/200k = 15% | Fireball example | Relative power preserved | WT2 |
| 120 → 50 (cap 60) | 2020 level squish | First in 16 years | WT2 |
| 3 Nov 2011 | First squish developer blog | | WT2 |
| ~2.1 billion | Signed 32-bit limit cited | | WT2 |
| "4–6 expansions" | Claimed squish recurrence | Contradicts the listed dates (see T-R1) | WT2 |
| 2+ expansions | Survival Hunter controversy duration | 2016 → 2018+ | WT4, W4 |
| 8–10 weeks | WoW x.x.5/x.x.7 patch lifespan | | WT3 |
| 8–12 weeks | Suggested maximum balance-pass cadence | The researcher's inference | WT6 |
| 1 : 1 | WoW baseline damage-to-threat | | CX1 |
| 5.0× | Tank threat modifier | | CX1 |
| ½ ÷ observers | Healing threat | | CX1 |
| 1/2, 1/4, 1/8, 1/16 | CC DR steps (PvE) | | CX1 |
| 2 | Applications to PvP CC immunity | | CX1 |
| 16 s | CC DR reset | | CX1 |
| 30% | Stat DR onset (Shadowlands) | | CX1 |
| 16 of 40 | WoW debuffs shown vs possible | | CX2 |
| 3 / 5±2 / 7±2 | Working-memory items (learning / familiar / UI rule) | Presentation only, per the BRIEF | CX2, CX4 |

### 3.8 Probe results
| Number | What | Source |
|---|---|---|
| 38 / 7 | Total tests passing / ability-pool tests | IR3 |
| 6/6 (100%) | Correct `grant_ability` classifications | IR3 |
| 5/6 (83%) | Narration/grant consistency | IR3 |
| beast 2/2, elemental_fire 1/2, undead 1/1, construct 1/1 | Consistency by archetype | IR3 |
| decisive_kill 2/2, narrow_survival 2/2, non_lethal_subdual 1/2 | Consistency by method | IR3 |
| <50 | Live API calls for the full validation | IR3 |

---

## 4. Tensions and contradictions

### 4.1 With the constitution (and the BRIEF)

**T-1 · P9's unified Focus versus resources as the MMO identity lever.** WT5: resource systems
"enforce playstyle identity at the mechanical level," and without them "all DPS specs would converge."
FFXIV's homogenization (MM1) shows the same failure from another angle. [C:P9] unified Focus for hybrid
bookkeeping and itself concedes that unification "does NOT by itself solve whether a hybrid's kit feels
coherent." **Resolution candidate:** one pool, with calling-specific *generation triggers* (05.7). This
is compatible with P9's text, which constrains the *pool* and not how it refills.

**T-2 · P14's cadence asymmetry versus P9's fixed action budget.** In a turn-based game, WoW's
1.0/1.5-s asymmetry *is* 1.5× the actions, which [C:P9] exists to forbid ("closing off
action-economy-stacking exploits"). The constitution adopted both without noticing the collision.
**Resolution candidates:** 06.4 (a) split actions, (b) initiative or tempo, (c) reactions. Needs a
Decision Log entry in ch 06.

**T-3 · VI's provisional-by-default rests on live-service evidence, not character-scale evidence.** The
PoE league is a studio-level, multi-player, 3-month *content* trial (PG6). No source tests provisional
status for an *individual character's* newly granted ability or calling. The BRIEF assigns "provisional
status + consolidation (VI)" to ch 04, which implies the per-character scale. That application is an
extrapolation (04.16), and the trial-window length has no evidence (G-4). Authors should record it as
such. It is also worth deciding whether VI applies at *both* scales: rules content marked provisional in
the rulebook, and per-character provisional grants.

**T-4 · The constitution's P5 body still mandates a "calibrated classifier" from a different model
family. The sync report and the BRIEF say non-ML tag-tally.** P5 text: "a calibrated classifier —
which MUST NOT share a model family with the narrating AI … scores the bounded, eligible candidate set
… returning a confidence value per candidate." The 1.7.0 sync report says ML approaches were
"ultimately ruled out in favor of a non-ML tag-tally approach." BRIEF §5 calls the tally scorer the
current default. **Reconciliation:** a deterministic tally scorer that outputs a per-candidate
confidence (e.g. proximity to threshold, normalized) satisfies the letter. It shares no model family
because it is not a model, and it is calibrated by construction if thresholds map to confidence bands.
The Delve research (E3) supports deterministic thresholds. Ch 04 must state this reconciliation
explicitly, or the orchestrator should queue a constitution PATCH.

**T-5 · "Curated sparse table … never a full Cartesian cross-product" versus Hades II's near-complete
pair coverage.** Hades II authors ~1 duo for every one of its 36 god pairs (RG1). The constitution's
worry is combinatorial explosion across *all* tags or abilities, and the research shows explosion is
avoided by *keying* to a low-cardinality level, not by leaving most pairs empty. **Clarification
needed:** "sparse" = never keyed to individual abilities or deep tags. Near-complete coverage at the
keyed branch level is fine, and implausible pairs are *explicitly* recorded as "no hybrid."

**T-6 · Delve's legibility versus the locked "hidden mechanics."** Delve's system *announces* classes
with numbers, while the owner locked "no blue boxes." Wandering Inn (semi-transparent) and Defiance
(opaque) fit the fiction lock better, but the codex is out-of-fiction and *could* show everything.
Goal 1 argues for visibility. See 04.13 and G-16.

**T-7 · P3's comprehension wall versus the BRIEF's deviation.** The fourth pass's strongest-confirmed
finding (W3, W5) is the 3–5 / 7±2 wall, and its researcher recommended "(A) + (C)": simplify to 3–5
choices by default, plus optional depth (CX6). The BRIEF removes the budget. **But the same research
supports the BRIEF's approach through PoE:** GGG kept 1,500+ nodes and solved comprehension with an
official tool rather than simplification (CX3, W3), and "complexity is not … the reason new players
don't play" (PG7). The deviation is defensible *only if* the codex (ch 14) is a real computational
aid in the Path of Building mold. Also, P3's separate MUST to "classify each piece of tracked state as
background-resolved or player-facing" is not about the budget and should survive the deviation (00.10).

**T-8 · Cumulative evidence (Delve, EVE) versus drift-tracking labels (Wandering Inn, Azarinth).**
Permanent counters make recognition stable but let a character keep a calling they no longer live.
Drift-tracking makes the label honest but risks unwelcome relabels, and rework cost (WT4) says
unwelcome identity change is expensive. **Resolution candidate:** thresholds use cumulative counters,
confirmation and maintenance of a *provisional* status use a recent window, and relabels happen only as
*offers* at boundary events (04.14).

**T-9 · Smart Loot versus P5's two-axis derivation.** See 08.14. A character-keyed bias is a third axis
[C:P5] does not name.

**T-10 · V's "small, closed pools" versus ARPG-scale tables.** V targets *character build primitives*.
The ARPG lesson is to "bound the count, not the table" (A2). **Clarification:** property tables for
items may be large and enumerated. What must stay small and closed is the set of *slots* and each
ability pool a character draws from. Ch 05 and ch 08 should state which tables V governs.

**T-11 · P6's named composites versus the pipeline evidence.** P6 plus its companion covers named
composites and priority tags, but the constitution names no mechanism for *additive and probabilistic*
composition (the Isaac cache, RoR2 coefficients, StS hooks), which the research calls the dominant
scalable pattern (RG5). Ch 05 should adopt it as the default regime (05.5). It is compatible with the
constitution, just not codified there.

**T-12 · The hard total-slot ceiling versus reserved signature slots.** [C:P5] requires one hard total
ceiling. D3 reserves a separate slot so signatures never compete (A1), and E6 recommends acquired
abilities "occupy its own reserved slot." Do item-bound abilities and absorbed powers count toward the
one ceiling? **A decision is needed** (ch 05 + ch 08). If they don't, the "hard" ceiling leaks. If they
do, items crowd out calling abilities, which is D3's exact launch problem. **Candidate:** one total
ceiling partitioned into reserved sub-quotas (e.g. calling slots N, equipment-ability slots M,
acquired/absorbed slots K, with N+M+K = the cap).

**T-13 · Authority-based conferral versus "class is derived, never an independent dispenser."**
Wandering Inn's Emperor-grants-[General] (L1) is exactly the non-derived path [C:P5] forbids, yet the
BRIEF's locked fiction voicing includes "an order that seeks you out." **Candidate:** conferral
*offers* a provisional calling (VI) that grants only the calling's *label and synergy eligibility*.
Its tiers still require evidence, and it lapses without evidence.

**T-14 · The ChatRPG evidence supports "structure," not specifically "relationship-state."** E6 recommends
relationship-state and cites ChatRPG, but ChatRPG added a *resolution* tool and explicitly built *no*
spatial state (FP6). The relationship-state recommendation is sound but rests on TTRPG precedent plus
inference. Ch 06 should not claim ChatRPG validated it, and it should list relationship-state
sufficiency as an open empirical question.

**T-15 · Per-ability recharge versus the cooldown-centric criticism.** [C:P5] requires an explicit
recharge per active ability, and the probe used "once per encounter" everywhere. WoW players criticize
"cooldown-centric design" (CX5). The evidence is weak, but it argues for varied recharge types (05.8).

**T-16 · Who rolls?** The current engine centers `roll_check` on the player. Monster of the Week has
the Keeper *never* roll for monsters (FP3). Ironsworn has the player roll everything, while D&D-style
systems have adversaries roll. The sources don't settle it, and it shapes ch 06/09 action economy and
AI determinism.

**T-17 · The freeform ethos of PbtA and Ironsworn versus VII's default-deny.** Ironsworn tells players to
"not be afraid to break out of the rules" (FP4), and Dungeon World has no action economy (FP3). This
project deliberately inverts that ([C:VII]). Borrow their *positioning abstractions* without their
permissiveness: a narrated flank still needs a legal movement.

**T-18 · Blades' Position is GM judgment; P8 prefers determinism.** Setting Position and Effect is a
`[J]` call. Adopting it requires a criteria table (factors → steps) plus worked examples, or it
reintroduces the "rulings over rules" ambiguity P8 was chosen to avoid.

**T-19 · Stat-ratio class gates versus attributes fixed at creation.** Delve gates Dynamo on Clarity ≥ 5×
Focus (L1). If attributes are "mostly fixed at creation" ([C:P4], the sync report), any
attribute-ratio primary requirement makes certain callings creation-locked destiny. Ch 04 should
avoid attribute-based primaries, or state that they are deliberate origin-flavored gates.

**T-20 · The report's "P5 remains open" framing is superseded.** E6 proposed keeping P5 open with
"leading candidate" language. Constitution 1.7.0 resolved it. Authors should cite E-sections for
evidence, not for status.

### 4.2 Inside the research (factual inconsistencies; do not propagate)

**T-R1 · Squish cadence.** WT2 lists 2014, 2018, 2020, and 2024, which is every 1–2 expansions, yet
infers "recur every 4–6 expansions." The dates contradict the inference.

**T-R2 · The Midnight squish date.** Patch 12.0.0 "Midnight" is dated 2024 in WT2/W4. The same note
calls 2024–2026 the "current expansion (Midnight/World Soul Saga)." The date is probably wrong (the
expansion that launched in 2024 was The War Within). Don't cite "2024" for the fourth squish.

**T-R3 · PoE multi-tag weighting.** A2 says both "sums the matching weights" and "left-most tags most
significant," and the researcher could not verify the latter. Don't cite either as the definitive PoE
rule. Cite the filter-then-weight shape.

**T-R4 · PoE2 counts.** Node totals: 2,831 (PoE1) vs 1,325 (older) vs 4,524 (PoE2 shared tree) vs
"1,200–1,500" (W3). Ascendancies: 12×3 = 36 (PG4) vs "22 ascendancy trees, 409 nodes" (PG3), and PG4
itself hedges "though the actual class count varies." Quote only with the uncertainty.

**T-R5 · RoR2 coefficient range.** "Between 0 and 1" but "30% with coefficient 3.0" (RG4).

**T-R6 · WoW history slips.** W4 says "Legion's seven-row single-choice structure," but WT1 says Warlords
(6.0, 2014) added the seventh tier and Legion kept the MoP system. WT1 also presents Dual Talent
Specialization as a Legion addition, while it has existed since Wrath patch 3.1. That last point is from
my background knowledge and not in the sources, so verify it before citing.

**T-R7 · The E5 table's misattribution.** The candidate-primitives table labels the
Essence/Fossil/Crafting-Bench trio as a "Diablo" trio. It is Path of Exile.

**T-R8 · Hades I duo count.** "~10 shown in a single article to ~30 in the data-tool listing"
(RG1 gaps). The 1:1 pair ratio claim for Hades I is approximate.

**T-R9 · Borderlands figures.** The 35 / 1,500–1,700 numbers are unverified search-summary claims (A4
gaps). The 30-billion BL4 figure is from a Gearbox press statement reported by TweakTown.

**T-R10 · GCD reversal specifics.** W3 says "Blizzard reversed most of the change in Shadowlands." CX2
says it removed the GCD "from burst cooldowns while maintaining it for offensive buffs," and CX5 says
"removing GCD from most burst cooldowns while maintaining it on offensive buffs." That is slightly
inconsistent with the stated expansion target ("offensive buff abilities"). Quote only "largely
reversed."

---

## 5. Gaps: questions a complete ruleset needs that these sources do not answer

Each gap names a suggested **settling test** (for the Open Empirical Questions appendix), where the gap
is empirical.

- **G-1 · The hybrid-merge trigger rule.** No source gives a numeric trigger for when mixed history mints
  a hybrid versus a single winner (E3, E7, L3). *Original design is required.* Test: simulate
  scripted histories (pure, 70/30, 55/45, and 3-branch mixes, 200 each) and measure how often each rule
  candidate offers a hybrid. Target: the hybrid is offered for genuinely mixed play and never for a
  single-track history with incidental off-branch events.
- **G-2 · Scaling counters to TTRPG event rates.** Delve's 50 kills and 5,000 mana assume a video-game
  event density. A TTRPG session may produce only a handful of significant tagged events. Test: log
  `tag_event` counts per session over 5+ play sessions, then set thresholds so the first recognition
  lands at a target session count that the chapter must choose.
- **G-3 · Recency and decay weighting.** No source weights recent evidence (03.10). Test: simulate a
  mid-campaign playstyle pivot and measure sessions until the new calling is offered and the old one
  lapses, under cumulative versus windowed tallies.
- **G-4 · Provisional-window length at character scale.** The 3-month league has no per-character
  analog (T-3). Test: playtest trial windows of 1 boundary event vs 2 sessions and record lapse and
  confirm rates and whether the player perceives loss.
- **G-5 · Multi-target and AoE under relationship-state.** The sources name the ceiling (E5) but give no
  rule. 06.3 proposes a mapping. Test: 20 scripted multi-foe fights, measuring target-set disagreements
  between the DM's narration and the state.
- **G-6 · Persistent "who's near whom" consistency.** Neither PbtA nor ChatRPG solved it (FP3 gaps, FP6).
  Test: rate of narration/relationship-state contradictions per 10 exchanges, with and without a forced
  state echo.
- **G-7 · What dropped items grant.** The sources give patterns (GW2, D3, D4) but no rule for a
  slot-capped character (T-12). Design decision.
- **G-8 · Source of max-Vitality growth without levels.** PoE2 moved it to gear (PG3). Nothing else in
  the sources speaks to it.
- **G-9 · Focus pool numbers.** There is no precedent for a unified pool's size, cost scale, or recovery.
  WoW's 100-cap Energy and Runic Power are single-class pools. Needs simulation (turn-by-turn spend
  curves).
- **G-10 · Morale, surrender, and fleeing foes.** Absent.
- **G-11 · Exploration, social influence, investigation, travel hazards, and downtime.** Only Blades
  clocks, Fate zones, and EVE time-gating reach these chapters. Other research digests must carry ch 10.
- **G-12 · The Borderlands part-selection algorithm** (weighted or not; how rarity relates to part count)
  (A4 gaps).
- **G-13 · Exalted and Chaos Orb mechanics** (A2 gaps).
- **G-14 · Hades duo prerequisite keying** (slot vs identity vs tag) (RG1 gaps).
- **G-15 · How to explain hidden mechanics to players** (CX4 gaps).
- **G-16 · How transparent unrecognized callings should be in the codex** (04.13, T-6). A design
  decision; test player satisfaction in playtest.
- **G-17 · A re-evaluation cadence clock without levels** (Wandering Inn's 10-level interval needs a
  replacement) (03.11).
- **G-18 · Economy numbers.** Prices, wealth curves, sinks. None.
- **G-19 · Blue-Mage absorption precedent.** No shipped absorber system was researched. Only adjacent
  mechanics exist (04.18).
- **G-20 · A retirement and legacy procedure.** Only analogies (D4 Codex, EVE, PoE Standard).
- **G-21 · A metric for "build diversity."** MM4 gaps: no study measures actual diversity. The project
  needs its own if it wants to audit [C:V].
- **G-22 · Adversary behavior and targeting tables.** Only the threat model (I-1) and MC moves.
- **G-23 · A concurrency cap on recognized callings** (Azarinth 2, Threadbare many; no consensus)
  (04.12).
- **G-24 · Target-resolution failures beyond ChatRPG.** One study. Test: the rate of wrong-target or
  self-harm narration with the 01.9 precondition rule, over 50 ambiguous-target actions.
- **G-25 · Class-label/playstyle divergence handling** (the Azarinth case). When does a mismatch
  justify an offer to relabel?
- **G-26 · A "success at a cost" band in d20 resolution.** The research favors partial success for
  positioning (FP1, FP3). The current resolution has no such band, and the sources don't say how to add
  one to a d20 vs-DC system.
- **G-27 · Companion and hireling action economy under P9.** Mörk Borg's side-based initiative is the
  only precedent.

---

## 6. Top 15 implications (ranked)

Ranked by leverage on the two design goals: (1) player freedom to try creative ideas, and (2) the AI
responding correctly. Player-facing complexity is deliberately not weighed.

1. **Make "gate → fill" the single generator for every emergent-content domain.** It covers loot,
   crafting, patron gifts, absorbed powers, and item-granted abilities, and is implemented as one
   algorithm: tag-filter the pool by source (hard zero-weight exclusion) → choose the fill method from
   the acquisition circumstance and degree of success (guaranteed signature / biased / player-chosen /
   plain weighted / Greater upgrade on a crit) → mod-group exclusion → fixed per-object slot cap. The
   DM only classifies onto closed lists, and a tool computes the content. This is the proven Feature
   003 boundary (6/6), and every ARPG converged on it after launching something looser (E1, A1–A5, AP,
   TC3, IR3). *Ch 08, 04, 05, 09, 00.*

2. **Build a composition substrate so any new ability combines with every old one at zero authoring
   cost.** It consists of one shared effect-definition table (D2 `ItemStatCost`), a closed trigger-hook
   list (StS), one ordered modifier-evaluation pass (the Isaac cache), two stacking families (RoR2),
   and a proc-chain terminator (RoR2's 0.0 coefficient). This is the densest source of the [C:P3]
   "reach-and-adapt" material: a novel player combo resolves by rule instead of by invention (goals 1
   and 2). *Ch 00, 05.*

3. **Route every ability into exactly one of four combination regimes, declared in data.** Shared
   pipeline (additive), independent trigger with coefficient (probabilistic), priority rank per claimed
   behavioral slot (exclusive, O(n)), or named composite keyed to a low-cardinality pair (flagship).
   The priority rule makes a suppressed effect lose its bonus unless marked cosmetic (Isaac
   Technology + Brimstone) (RG5, E2, W2, B-5). *Ch 05, 04.*

4. **Class emergence is Delve's dual-tier threshold over two evidence kinds.** Judged tag events
   (`[J]`, [C:III]) plus engine-counted events (`[D]`: Focus spent through tagged abilities, damage
   prevented, foes defeated by tagged means, distinct-source diversity counts). Keys sit at a fixed,
   low-cardinality tag level (single-digit top-level branches), each calling is evaluated independently
   (Threadbare), anti-grinding DR applies to repeated counted events (WoW DR shape), and thresholds are
   scaled to TTRPG event rates by simulation, not copied from Delve (E3, L1, L2, CX1). *Ch 03, 04.*

5. **Hybrids are named consolidations, keyed to branch pairs and sized by C(k,2).** Author near-complete
   coverage of plausible branch pairs (Hades II ≈1:1) with explicit "no hybrid" entries. Prerequisites
   and exclusions follow Hades' schema. Hybrids must be reachable *below* full specialist depth
   (Cataclysm's lesson). The merge trigger is original work that must be simulated. Consolidation also
   counts as [C:VI] structural retirement (six titles become one) (L3, RG1, WT1). *Ch 04.*

6. **Give recognition multiple fiction-voiced paths, each bounded by P5.** Behavioral emergence,
   conferral by an order or mentor (offered as provisional, evidence-sustained), specialization and
   advancement at crystallization moments, and circumstantial shift after injury or catastrophe, always
   *offered* and never imposed. This maps one to one onto the BRIEF's locked voicing list (L1, L4, WT4).
   *Ch 04, 07, 11.*

7. **Store positioning as discrete relationship-state in the deterministic layer.** Per PC–foe pair it
   holds a range band (DW's 5 bands or Fate zones), engagement links, and flank / cornered / cover /
   elevation flags worth a ±3 unit (Mörk Borg; 15 pp on d20). Only tool calls write it, and narration
   must name every change. Multi-target effects are defined *over the state* (pierce / chain / fork /
   burst / cone with fixed caps and PoE's priority order), not over geometry. Escape runs on opposed
   clocks (E4, E6, FP1–FP6, PG2). *Ch 06, 00.*

8. **Resolve the target before the roll, and treat intent as an attempt.** An exchange tool takes
   explicit target ids and validates relationship-state preconditions. Self-harm is never narrated
   without a result that licenses it. Downstream grants, loot, and evidence fire only on *resolved*
   outcomes (ChatRPG v1's failure; the Feature 003 scripted-kill finding) (FP6, IR3). *Ch 01, 06, 03, 12.*

9. **Adopt a Position-and-Effect layer as the telegraph and the ambition lever.** Severity is announced
   before the roll, and a "Desperate" announcement is the mandatory lethal-risk warning (no Desperate,
   no death on that roll). Effect sets success magnitude. The player may trade Position for Effect or
   spend Focus to push Effect. Positioning attempts that fail near the DC cost rather than negate
   (Blades 4/5), which needs a `[J]` criteria table (FP1, T-18, G-26). *Ch 01, 06, 07.*

10. **Principle VI toolkit, bundled at boundary events.** Provisional-by-default grants (the league
    logic scaled to a character; record the extrapolation), **fold-into-base** (PoE2 Acrobatics),
    **fork-replacement** (DCC), and **consolidation** (Wandering Inn). All of them happen only at
    telegraphed boundary events such as tier crystallization, rest, or a crisis. Granted abilities are
    never reinterpreted mid-life (Survival Hunter rework cost), squishes never count, and the policy is
    buff-over-nerf (PG3, PG6, WT4, W4, PG5). *Ch 04, 05, 12.*

11. **Tier rewards are capabilities, and numbers are bounded forever.** Each crystallization grants a new
    [C:VII] license, a behavior-changing modifier, or a keystone-shaped composite with a real [C:P12]
    downside, offered as 1-of-≤3 (MoP) and gated on cumulative investment (Dragonflight's 8/20).
    Never +1 filler (WoW's 5-point talents). Every modifier source and every roll total has a hard
    ceiling, and a per-layer power budget stops one layer from eating the rest (the PoE2 jewel meta)
    (WT1, WT2, PG5). *Ch 00, 04, 05, 08.*

12. **Ability templates separate scope, limitation, weakness, and cost into distinct fields, and the DM
    narrates only what the tool licenses.** The one real probe failure (Heat Resistance → an invented
    cold vulnerability) came from mixing a limitation with an implied weakness in prose. [C:P12]'s
    three levers, as separate data fields with banned soft phrasing, close it structurally (IR3, AP).
    *Ch 05, 12, 08.*

13. **Keep Focus unified while preserving calling identity through generation and cadence *within* P9.**
    Calling-specific Focus-regeneration triggers (WoW's Rage, Energy, and Mana logic over one pool).
    Cadence asymmetry expressed as split light attacks, initiative or tempo, or extra reactions, never
    as extra actions. Record the P9/P14 collision and its resolution in the Decision Log (WT5, MM1,
    T-1, T-2). *Ch 05, 06, 04.*

14. **Adversary archetypes are manufacturers: one tag set drives evidence, loot pool, absorbable pool,
    and behavior.** Archetypes express fictional values through mechanics, make some properties
    categorically impossible (recognizable provenance and crisp legality checks), carry
    `cannot_absorb` / `player_only` / `adversary_only` flags (RoR2 ItemTags), and use threat band as
    item level for tier gating (D2 alvl). Encounters never require a role (GW2), and adversary power
    uses a `[D]` estimate of PC power from state (A4, RG4, A1, MM2, MM4). *Ch 09, 08, 13, 04.*

15. **The codex is the official Path of Building.** It computes rollups (PoE pseudo-mods), shows full
    state on request (never capped like WoW's 16 of 40), shows ability regimes, priority ranks,
    recharge readiness, provisional flags, and relationship-state, and carries "why" notes (GW2's living
    document). This is what makes the BRIEF's rejection of P3's comprehension cap evidence-consistent:
    PoE kept the complexity and solved comprehension with a tool (CX3, W3, A2, PG7, MM2). *Ch 14, 12.*
