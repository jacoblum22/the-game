# Point-Buy Character Cost Systems and Move/Verb-Based Ability Design

## Point-Buy and Audited Character Cost Systems

### How does Mutants & Masterminds' point-buy system work, and what design strategies prevent exploits in superhero-level power disparity?

#### Takeaway
Mutants & Masterminds uses a Power Level cap system paired with point-buy to manage superhero-scale power disparity, intentionally allowing wider variance than systems like GURPS by design. Rather than preventing attribute arbitrage, the system contains it through explicit power level ceilings on attack/defense interactions.

#### Cited Findings
- Mutants & Masterminds uses a "Power-by-the-point" system where all character aspects (abilities, feats, skills, powers, equipment) are purchased from a pool of points — [Source](https://tvtropes.org/pmwiki/pmwiki.php/TabletopGame/MutantsAndMasterminds)
- Each Power Level grants 15 Power Points for character creation — [Source](https://tvtropes.org/pmwiki/pmwiki.php/TabletopGame/MutantsAndMasterminds)
- Power Level functions as an overall limit to prevent certain power/ability combinations from becoming too strong, establishing an overall "danger bracket" that keeps players and plots aligned — [Source](https://tvtropes.org/pmwiki/pmwiki.php/TabletopGame/MutantsAndMasterminds)
- Power Level caps combat-relevant stats: attack bonus, damage output, dodge/parry defense values, and resilience/toughness — [Source](http://www.realityrefracted.com/2011/08/power-level-limits.html?m=1)
- The default Power Level 10 represents "average Marvel team book character" while DC characters trend toward Power Level 14-16, intentionally allowing GMs to set the "feel and scale" of their game — [Source](http://www.realityrefracted.com/2011/08/power-level-limits.html?m=1)
- The system's flexibility allows novice players to create imbalanced characters (e.g., "a detective made of water" vs. optimized Superman) due to insufficient mechanical understanding, despite having similar point costs — [Source](https://tvtropes.org/pmwiki/pmwiki.php/TabletopGame/MutantsAndMasterminds)

#### Inferences
- M&M's exploit resistance strategy differs fundamentally from GURPS: rather than making all builds equal, the system allows powerful disparities but constrains them to specific power levels, assuming the GM will set an appropriate power level for the campaign
- The need for "mechanical understanding" to avoid imbalanced characters suggests the system has non-obvious trade-offs that aren't adequately transparent from point costs alone
- Power Level caps act as a "backstop" mechanism, preventing infinite scaling in certain dimensions regardless of point allocation

#### Gaps
- No specific documentation on the most common exploits players discover in M&M (attribute combinations, power/feat stacking patterns)
- Limited information on how power level caps specifically interact with multi-power combinations or whether certain power types have loopholes

---

### How does the HERO System's point-buy work, and is it considered more or less exploit-resistant than GURPS?

#### Takeaway
HERO System uses tiered power costs (1d6 effect = 5 points base, modified by power type) and built-in asymmetry (defense cheaper than offense) to resist exploitation. While it offers the same flexible point-buy structure as GURPS, its explicit limitation system and standardized cost ratios create stronger guardrails against attribute arbitrage.

#### Cited Findings
- Champions (the HERO System superhero variant) was the first RPG to use point-based character creation instead of random rolls, published 1981 — [Source](https://en.wikipedia.org/wiki/Champions_(role-playing_game))
- HERO System uses a standardized cost base: 1d6 of effect costs 5 points (applies to STR, Blast, and similar powers) — [Source](https://pdb.fandom.com/wiki/Hero_System)
- Power costs adjust by type: Dispel costs 3 points per die (lower, limited application), Drain costs 6 per die (stronger effect), Killing Attacks cost 15 per die (highest damage) — [Source](https://pdb.fandom.com/wiki/Hero_System)
- Defense values are typically cheaper to purchase than equivalent offense, creating a built-in balance mechanism — [Source](https://pdb.fandom.com/wiki/Hero_System)
- Most powers include a modifiers system allowing limitations (narrower application, situational restrictions) that reduce cost while improving thematic accuracy — [Source](https://en.wikipedia.org/wiki/Hero_System_Rulesbook)
- Design philosophy intends to allow "fun and open-endedness without being so open that it's too easy to exploit the system," with rules structured to allow GM customization while maintaining underlying balance assumptions — [Source](https://pdb.fandom.com/wiki/Hero_System)
- Players must design not only powers but also skills, disadvantages, and other traits, creating a holistic point budget requirement — [Source](https://en.wikipedia.org/wiki/Champions_(role-playing_game))

#### Inferences
- HERO System's use of discrete cost brackets (3, 5, 6, 15) for different power types creates stronger differentiation than systems allowing continuous cost scaling, reducing the incentive to arbitrage between similar powers
- The requirement to purchase skills, disadvantages, and traits alongside powers prevents min-maxing pure offense/defense by forcing players to distribute points across character facets
- The "defense cheaper than offense" principle directly counters one of GURPS's documented vulnerabilities (heavy stacking of damage output)
- The modifiers system gives explicit tools for thematic limitations, reducing exploitative workarounds

#### Gaps
- No direct comparison document between HERO and GURPS vulnerability to specific exploits (attribute minmax, disadvantage gaming)
- Limited information on whether players have discovered workarounds to the modifier system or whether the 3/5/6/15 cost brackets have known loopholes

---

### How do 13th Age and Savage Worlds implement alternative character cost systems?

#### Takeaway
13th Age uses a *narrative relationship* model (Icon connections and One Unique Thing) rather than traditional point-buy, making balance implicit in narrative uniqueness. Savage Worlds uses forced point-equilibrium (Hindrances = Edges), preventing pure optimization by requiring players to accept mechanical disadvantages.

#### Cited Findings

**13th Age:**
- All PCs have One Unique Thing—something distinctive true only about that character, typically non-combat but potentially any game element — [Source](https://pelgranepress.com/2022/05/14/one-shot-unique-things/)
- PCs receive 3 points to distribute across Icon Relationships at character creation, with points spent measuring influence/usefulness to the character — [Source](https://roll20.net/compendium/13thage/Creating%20Characters)
- Icon relationships, talents, and One Unique Thing intertwine to showcase character specialness and create memorable play — [Source](https://pelgranepress.com/tag/13th-age-character-builds/)

**Savage Worlds:**
- Characters start with 0 points; Hindrances grant points (1 per Minor, 2 per Major) — [Source](https://writeups.letsyouandhimfight.com/jackmann/savage-worlds/)
- Edges cost 2 points each during character creation — [Source](https://writeups.letsyouandhimfight.com/jackmann/savage-worlds/)
- Limit: 1 Major Hindrance and 2 Minor Hindrances maximum — [Source](https://writeups.letsyouandhimfight.com/jackmann/savage-worlds/)
- Points earned from Hindrances must be spent on Edges or attributes; final budget must balance to exactly 0 — [Source](https://writeups.letsyouandhimfight.com/jackmann/savage-worlds/)
- Raising an attribute or gaining a skill point can also cost points (variable costs) — [Source](https://writeups.letsyouandhimfight.com/jackmann/savage-worlds/)

#### Inferences
- 13th Age's approach prevents exploitation by making balance a *narrative property* rather than mathematical—the system assumes each One Unique Thing is intrinsically interesting and non-trivial, discouraging purely mechanical optimization
- Savage Worlds' forced equilibrium (Hindrances gain = Edges spend) is structurally similar to risk/reward mechanics and prevents the "net positive" builds that plague systems without this constraint
- Savage Worlds' fixed Major/Minor Hindrance limits prevent players from claiming excessive compensatory points through disadvantage stacking

#### Gaps
- No documented exploit patterns for 13th Age (players may have found loopholes in Icon connection interpretation)
- Limited guidance on whether Savage Worlds' point costs for attributes and skills can create arbitrage opportunities

---

### What specific design techniques prevent point-buy exploits, and how are they implemented across systems?

#### Takeaway
Exploit prevention uses five primary levers: (1) hard caps on individual stats/powers, (2) tiered cost brackets to prevent continuous arbitrage, (3) forced distribution across categories, (4) meaningful disadvantage mechanics, and (5) asymmetric costs (e.g., defense cheaper than offense).

#### Cited Findings
- Categorical restrictions in point-buy force point allocation across different character facets (powers, skills, disadvantages, etc.), making optimization harder — [Source](https://www.ttrpg-games.com/blog/what-are-point-allocation-systems-in-rpgs/)
- Point caps on individual attributes or skills prevent stockpiling of a single dimension — [Source](https://www.ttrpg-games.com/blog/what-are-point-allocation-systems-in-rpgs/)
- Diminishing returns (increasing costs as stats increase) reduce the incentive to max out any single stat — [Source](https://www.ttrpg-games.com/blog/what-are-point-allocation-systems-in-rpgs/)
- Penalty systems and limits prevent "ridiculously powerful characters" or characters "whose flaws are actually advantages" — [Source](https://www.ttrpg-games.com/blog/what-are-point-allocation-systems-in-rpgs/)
- If disadvantages grant points only at creation and are "forgotten" during play, they become easily exploitable flavor; if they cost points (making them story foci), players prioritize playing them, creating mechanical consequences — [Source](https://www.norsefoundry.com/blogs/game-systems/point-buy-and-how-does-it-work-in-dnd)
- Strategic variety should be encouraged through balanced action costs and clear mechanics, preventing any single approach from dominating — [Source](https://www.ttrpg-games.com/blog/what-are-point-allocation-systems-in-rpgs/)
- Min-maxing (allocating points to "best" stats while neglecting others) is a common player behavior, though often socially discouraged — [Source](https://www.norsefoundry.com/blogs/game-systems/point-buy-and-how-does-it-work-in-dnd)

#### Inferences
- The most effective exploit-resistant systems use *multiple mechanisms in combination*: D&D 5e point-buy, HERO System, and Savage Worlds all use categorical restrictions + forced equilibrium + meaningful disadvantages
- Disadvantage mechanics are a design canary—if they're exploitable, it indicates larger flaws in the point cost model
- Asymmetric costs (defense/offense, different power types) are more effective than homogeneous costs because they reduce simple linear optimization

#### Gaps
- No systematic comparison of which systems have had specific exploit patterns discovered post-publication
- Limited data on whether diminishing returns curves have optimal break-points that players exploit

---

## Move/Verb-Based Ability Design

### How does Blades in the Dark structure its special abilities, and how does it compare to PbtA "moves"?

#### Takeaway
Blades in the Dark uses playbook-specific special abilities with narrow mechanical triggers (passive bonuses, resource expenditure, action-specific effects) rather than PbtA-style stat-based moves. Abilities tend toward incremental bonuses with occasional potent standouts, making them feel less impactful than base action increases.

#### Cited Findings
- Blades in the Dark special abilities are playbook-specific, with each playbook containing seven abilities — [Source](https://bladesinthedark.com/character-playbook)
- Special abilities include passive benefits (like +1d or +1 effect) in specific contexts and resource expenditure mechanics (spending "special armor") — [Source](https://bladesinthedark.com/character-playbook)
- Many abilities integrate with the "push yourself" system, allowing characters to trigger special effects without paying the standard 2-stress cost, instead gaining normal push benefits (+1d, +1 effect, act despite harm) — [Source](https://bladesinthedark.com/character-playbook)
- Special armor is a renewable resource restored at the beginning of downtime — [Source](https://bladesinthedark.com/character-playbook)
- Abilities often feel less impactful than increasing base Action ratings, as they consist mainly of incremental bonuses (+1d, +effect) in narrow situations, though standout abilities (like "Functioning Vice") are notably potent — [Source](https://enworld.org/threads/blades-in-the-dark-advice-please.702150/page-6)
- Unlike PbtA, Blades in the Dark uses a skill list rather than stats, so abilities don't align with stat-based triggers — [Source](https://enworld.org/threads/blades-in-the-dark-advice-please.702150/page-6)
- PbtA playbooks typically contain 10-12 moves, whereas Blades offers only 7 abilities per playbook — [Source](https://enworld.org/threads/blades-in-the-dark-advice-please.702150/page-6)
- The game explicitly allows multiple players to play the same playbook as long as characterizations are sufficiently differentiated — [Source](https://enworld.org/threads/blades-in-the-dark-advice-please.702150/page-6)

#### Inferences
- Blades' narrower abilities (7 per playbook) provide fewer mechanical options than PbtA (10-12 moves), suggesting deliberate simplification
- The design shift away from stat-based triggers (characteristic of PbtA) toward action-specific bonuses creates less narrative ambiguity about when abilities apply
- The lower perceived impact of incremental bonuses may reflect designer intent to keep abilities modest relative to base mechanics, preventing them from overshadowing core skill rolls
- The "Functioning Vice" standout suggests the system works best with a mix of narrow and broad abilities

#### Gaps
- No documented design rationale for the 7-ability limit or comparison of mechanical balance across playbooks
- Limited analysis of whether certain playbooks' ability suites dominate others

---

### How does Fate Core's "stunts" system work, and what design patterns constrain ambiguity?

#### Takeaway
Fate Core uses three core stunt patterns (add new actions, provide situational bonuses, create rules exceptions) with explicit constraints (narrow circumstances, situational restrictions, frequency caps) and prerequisite chains. This framework allows player customization while preventing open-ended mechanical ambiguity.

#### Cited Findings
- Fate Core stunts are tied explicitly to skills and provide "numerous ways to customize your character" — [Source](https://fate-srd.com/fate-core/stunts-refresh)
- Stunts carry a refresh cost: starting 3 refresh, -1 per stunt (minimum 1 refresh) — [Source](https://fate-srd.com/fate-core/stunts-refresh)
- Three primary stunt design patterns:
  - **Add new actions**: Allow a skill to perform actions it normally cannot, replicating another skill's actions or introducing entirely new capabilities in specific situations — [Source](https://fate-srd.com/fate-core/building-stunts)
  - **Provide action bonuses**: Grant "+2 to skill total" or equivalent under narrowly defined circumstances, representing specialization — [Source](https://fate-srd.com/fate-core/building-stunts)
  - **Create rules exceptions**: Make single exceptions to game rules within narrow contexts, though cannot modify core aspects system governing fate point economy — [Source](https://fate-srd.com/fate-core/building-stunts)
- Stunts are designed with "circumstances...pretty narrow compared to the base skills they modify" — [Source](https://fate-srd.com/fate-core/building-stunts)
- Constraints include:
  - Specific actions only (creating advantages OR attacking/defending, not both)
  - Situational restrictions (only among nobles, only supernatural contexts)
  - Frequency caps (once per conflict/scene/session) — [Source](https://fate-srd.com/fate-core/building-stunts)
- Stunt families chain related stunts with prerequisites using either:
  - **Stacking**: Making original stunts more powerful
  - **Branching**: Providing thematically related but mechanically distinct abilities, without modifying the prerequisite stunt — [Source](https://fate-srd.com/fate-core/building-stunts)
- Fate point-powered stunts cost a fate point when effects are powerful or lack natural usage limits (especially for abilities affecting conflict stress) — [Source](https://fate-srd.com/fate-core/building-stunts)
- The system allows flexibility: stunts can be skill-agnostic, tied to multiple skills, or tied to aspects/gear/stress tracks — [Source](https://fate-srd.com/fate-system-toolkit/stunts)

#### Inferences
- The "narrow circumstances" requirement is Fate's primary exploit-resistance mechanism, preventing stunts from becoming general-purpose rule modifications
- Refresh cost acts as a player agency trade-off (more stunts = fewer fate points), creating meaningful build decisions rather than pure optimization
- The three design patterns give a clear framework within which designers can create new stunts, reducing the risk of designing overpowered or narratively incoherent abilities
- Stunt families (prerequisite chains) allow for progression/specialization without exponential power growth
- Fate point-powered stunts handle the "frequency problem"—abilities with unlimited use are balanced by requiring a finite resource

#### Gaps
- Limited documentation on actual player-authored stunts and whether the "narrow circumstances" constraint is enforced in practice or often violated
- No data on whether specific skill combinations enable stunt synergies that break the designer's intent

---

### What is the design spectrum between fully pre-specified moves/abilities and open frameworks, and where is the middle ground?

#### Takeaway
The spectrum runs from *fully pre-specified* (Blades in the Dark, PbtA: fixed ability lists with narrow triggers) to *open frameworks* (Fate Core: templates and constraints allowing player authorship). The middle ground combines *fixed templates with guided authorship*—pre-defined patterns (like Fate's three stunt types) that allow variation within constraints.

#### Cited Findings
- Powered by the Apocalypse (PbtA) design principle: "the underlying structure of using Moves as quanta of rules allowed designers to write a game for any conceivable narrative conflict" — [Source](https://cannibalhalflinggaming.com/2025/11/13/the-design-decision-which-won-narrative-gaming/)
- In move-based systems, narrative comes first: players describe actions, and if actions align with a specific trigger, a move activates — [Source](https://medium.com/@carljrogers/narrative-driven-learning-role-playing-games-6c488c8f6dfb)
- Move-based systems use narrative-driven triggers (e.g., "Investigate a Mystery," "Act Under Fire," "Call in a Debt") to activate mechanical resolution — [Source](https://medium.com/@carljrogers/narrative-driven-learning-role-playing-games-6c488c8f6dfb)
- Popular frameworks include move-based systems, token economies, GM-light/GMless play, and one-page frameworks, each offering benefits like quick setup, streamlined rules, and narrative focus — [Source](https://medium.com/@carljrogers/narrative-driven-learning-role-playing-games-6c488c8f6dfb)
- Fate Core provides three core stunt patterns, allowing designers to create custom stunts within those templates rather than selecting from a fixed list — [Source](https://fate-srd.com/fate-core/building-stunts)
- Blades in the Dark provides fixed playbook ability lists (7 per playbook), with no official guidance on player-authored abilities — [Source](https://bladesinthedark.com/character-playbook)

#### Inferences
- Full pre-specification (Blades, PbtA) minimizes ambiguity about when/how abilities apply but limits total mechanical option space and novelty
- Fate's template approach (three stunt types + constraints) creates a *guided authorship* middle ground—designers set patterns, players author within them
- The constraint-based middle ground allows both narrative novelty and mechanical clarity: constraints like "narrow circumstances" and "frequency caps" prevent infinite power escalation
- Systems using fully pre-specified moves/abilities report cleaner narrative resolution (less "does this move apply?" questions) versus systems with open frameworks

#### Gaps
- Limited documentation on whether Fate's three stunt patterns adequately cover player desires for custom abilities, or whether open-framework systems experience frequent requests for "off-pattern" stunts
- No data comparing resolution time (ambiguity disputes) between fully pre-specified systems and open frameworks in actual play
- Limited analysis of whether constrained authorship frameworks successfully prevent the power-creep that open frameworks allegedly experience

---

## Cross-System Summary and Design Patterns

### Point-Buy Systems: Exploitation Vectors and Mitigations

**Common Exploit Patterns:**
1. Attribute arbitrage: Concentrating points into a single high-value stat
2. Disadvantage gaming: Taking disadvantages that rarely trigger during play but grant compensatory points
3. Power stacking: Combining multiple mid-tier powers to exceed balance intentions

**Mitigation Mechanisms Across Systems:**
- **Hard caps**: M&M's Power Level, D&D's standard ability score ceilings
- **Tiered costs**: HERO System's cost brackets (3/5/6/15 points), preventing linear optimization
- **Forced distribution**: HERO's requirement to buy skills/disadvantages/traits alongside powers
- **Asymmetric pricing**: Defense cheaper than offense; limitation modifiers for thematic fit
- **Meaningful disadvantages**: Disadvantages that cost points (Savage Worlds) force players to integrate them into character concept rather than flavor-only
- **Equilibrium models**: Savage Worlds' forced Hindrance-to-Edge balance

**Comparative Resilience:**
- HERO System and Savage Worlds appear more exploit-resistant than GURPS due to tiered costs and forced distribution
- M&M's approach trades exploit-proofing for flexibility, relying instead on Power Level gatekeeping
- 13th Age's narrative-first approach prevents mathematical exploitation by making all characters equal narratively (by construction)

### Move/Ability Systems: Ambiguity Reduction and Option Space Trade-offs

**Design Trade-offs:**
| Dimension | Fully Pre-Specified (Blades, PbtA) | Template-Guided (Fate Core) | Open Framework |
|-----------|-----------------------------------|---------------------------|-----------------|
| Narrative clarity | High; triggers unambiguous | Medium-high; patterns guide interpretation | Low; requires GM adjudication |
| Option space | Limited but focused | Medium; pattern variations enabled | Expansive; risk of power-creep |
| Mechanical power | Modest, incremental bonuses | Moderate; refresh cost controls scaling | Unbounded without constraints |
| Designer burden | Moderate; design all abilities | Low; set patterns, let players author | Very high; must maintain all variants |

**Constraint Mechanisms:**
- **Trigger specificity**: Fate's "narrow circumstances," PbtA's explicit move names
- **Resource costs**: Fate points for powerful stunts, Blades' special armor
- **Frequency gates**: "Once per scene/session" language in Fate stunt design
- **Prerequisite chains**: Stunt families prevent standalone super-powerful abilities

**Key Insight:**
The middle ground (Fate's template approach) appears to optimize for both clarity and novelty—designers provide patterns, players customize within guardrails, and constraints prevent ambiguity or power escalation.

---

## Sources Referenced

- [Mutants & Masterminds - TV Tropes](https://tvtropes.org/pmwiki/pmwiki.php/TabletopGame/MutantsAndMasterminds)
- [Power Level Limits - Reality Refracted](http://www.realityrefracted.com/2011/08/power-level-limits.html?m=1)
- [HERO System - Primus Database Wiki](https://pdb.fandom.com/wiki/Hero_System)
- [Champions (role-playing game) - Wikipedia](https://en.wikipedia.org/wiki/Champions_(role-playing_game))
- [HERO System - Wikipedia](https://en.wikipedia.org/wiki/Hero_System)
- [Pelgrane Press - 13th Age Character Builds](https://pelgranepress.com/tag/13th-age-character-builds/)
- [13th Age - Roll20 Compendium](https://roll20.net/compendium/13thage/Creating%20Characters)
- [Savage Worlds by JackMann - RPG Writeups](https://writeups.letsyouandhimfight.com/jackmann/savage-worlds/)
- [Fate Core - Building Stunts](https://fate-srd.com/fate-core/building-stunts)
- [Fate Core - Stunts & Refresh](https://fate-srd.com/fate-core/stunts-refresh)
- [Fate System Toolkit - Stunts](https://fate-srd.com/fate-system-toolkit/stunts)
- [Blades in the Dark - Character Playbook](https://bladesinthedark.com/character-playbook)
- [EN World - Blades in the Dark Advice](https://enworld.org/threads/blades-in-the-dark-advice-please.702150/page-6)
- [Point-buy Play and Design – Correspondence is about Diligence](https://www.arkenstonepublishing.net/isabout/2020/04/23/point-buy-play-and-design/)
- [What Are Point Allocation Systems in RPGs? - TTRPG Games](https://www.ttrpg-games.com/blog/what-are-point-allocation-systems-in-rpgs/)
- [D&D Point Buy Guide - Dungeon Solvers](https://www.dungeonsolvers.com/dnd-point-buy-guide/)
- [Point Buy and How Does it Work in DND – Norse Foundry](https://www.norsefoundry.com/blogs/game-systems/point-buy-and-how-does-it-work-in-dnd)
- [The Design Decision Which Won Narrative Gaming - Cannibal Halfling Gaming](https://cannibalhalflinggaming.com/2025/11/13/the-design-decision-which-won-narrative-gaming/)
- [Narrative Driven Role Playing Games - Medium](https://medium.com/@carljrogers/narrative-driven-learning-role-playing-games-6c488c8f6dfb)
