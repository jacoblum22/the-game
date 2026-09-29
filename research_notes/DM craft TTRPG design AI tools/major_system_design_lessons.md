# Major TTRPG System Design Lessons: Character Build Diversity and Balance

## D&D 5e Balance Problems and the 2024 Revision Response

### Takeaway

D&D 5e suffers from well-documented balance problems including martial-caster disparity, trap feat options, and multiclassing exploits. The 2024 revision explicitly attempted to address these through Weapon Mastery and spell adjustments, but evidence suggests the gap widened rather than narrowed, with the martial-caster divide remaining a persistent problem.

### Cited Findings

**Documented Pre-2024 Balance Problems:**
- Martial-caster disparity is the system's most persistent balance issue, with spellcasters becoming progressively more powerful at higher levels — [RPGBot analysis](https://rpgbot.net/2024-dnd/2024-dnd-meta/)
- The multiclassing system enables both "overpowered" combinations and "trap" builds; certain combinations like Hexblade Warlock are game-breaking while others (like Grappler) are rarely worth taking — [D&D Beyond Forums discussion](https://www.dndbeyond.com/forums/d-d-beyond-general/general-discussion/219424-multiclassing-is-the-problem?page=2)
- Feat balance is poorly internal: Sharpshooter and Great Weapon Master are "feel mandatory" for martial viability, while feats like Athlete, Dual Wielder, and Grappler are "rarely worth taking" — [Screen Rant article](https://screenrant.com/dnd-broken-official-rules-ban-dungeons-dragons/)
- The -5/+10 mechanic of Sharpshooter and Great Weapon Master creates a situation where "having a feat so good that it feels like you're missing out if you don't take it removes the purpose of a customizable system" — [RPGBot feat analysis](https://rpgbot.net/dnd5/characters/feats/great-weapon-master-sharpshooter/)
- Martial classes lack "variety of meaningful choices available to spellcasters," with stretches of levels where martial characters gain "just more of the same" while casters receive "1-2 notable new spells" — [EN World forum discussion](https://www.enworld.org/threads/martial-caster-fix.711567/)

**2024 Revision Intended Changes:**
- Weapon Mastery traits were added to all martial weapons, providing "extra bonuses when they attack—such as AOE damage, moving enemies, or imposing disadvantage" — [RPGBot article](https://rpgbot.net/2024-dnd/2024-dnd-meta/)
- Healing spells were significantly buffed: "The 2024 rules fully double the healing dice for Cure Wounds, Healing Word, and the mass versions of both" — [RPGBot article](https://rpgbot.net/2024-dnd/2024-dnd-meta/)
- Monk class received targeted improvements and is now considered "one of the strongest martial classes" — [RPGBot article](https://rpgbot.net/2024-dnd/2024-dnd-meta/)
- Grappling mechanics were rebalanced to reduce optimization exploits — [RPGBot article](https://rpgbot.net/2024-dnd/2024-dnd-meta/)

**Documented Outcome—2024 Revision Failed to Close the Gap:**
- "New and updated spells made spellcasters even more powerful" despite the revision's explicit focus on martial improvements — [RPGBot article](https://rpgbot.net/2024-dnd/2024-dnd-meta/)
- Spells like Conjure Minor Elementals became "game-breaking," allowing solo Wizards to "vastly outpace optimized martial characters" — [RPGBot article](https://rpgbot.net/2024-dnd/2024-dnd-meta/)
- New "Spirit Guardians-style spell" variants are "now available to every full spellcaster," exacerbating the divide — [RPGBot article](https://rpgbot.net/2024-dnd/2024-dnd-meta/)
- Spellcasters gained "easier to manage" ability score flexibility (via Shillelagh with any mental ability) compared to martial builds — [RPGBot article](https://rpgbot.net/2024-dnd/2024-dnd-meta/)
- Overall assessment: "The martial-caster divide persists" despite the 2024 revision's explicit attempt to address it — [RPGBot article](https://rpgbot.net/2024-dnd/2024-dnd-meta/)

**Community Reception:**
- Community remains divided on whether a real problem exists; some participants argue "there's no evidence that there's a problem" and note that "martial classes are overrepresented" in actual player selection — [EN World forum](https://www.enworld.org/threads/martial-caster-fix.711567/)
- The revision generated "no clear consensus" on success; participants propose entirely different solutions (reducing spell slots vs. buffing martial abilities), suggesting either incompleteness or fundamental community disagreement on what "the problem" is — [EN World forum](https://www.enworld.org/threads/martial-caster-fix.711567/)

### Inferences

1. D&D 5e's bounded accuracy system (bonuses scaling from ~+5 to ~+11 over 20 levels) may be fundamentally incompatible with balanced spell progression, as spells scale qualitatively while martial scaling is linear.

2. The design philosophy of rewarding system mastery over preventing "trap options" (contrasting with 3e's philosophy) creates a secondary balance problem: players feel compelled to take specific feats to remain viable, reducing meaningful customization choice.

3. WotC's 2024 revision attempted a technical fix (Weapon Mastery, spell nerfs) without addressing the underlying architectural problem: that spellcasting provides both damage AND utility, while martial classes primarily provide damage.

### Gaps

- No documented analysis of whether the 2024 revision specifically nerfed problematic spells or if new spells offset the intended nerfs
- Limited designer commentary from WotC on whether martial-caster parity was intentionally designed or acknowledged as acceptable disparity
- No rigorous post-2024 empirical data on actual campaign outcomes (player retention, character longevity by class, documented power levels in play)
- Unknown whether the community's failure to reach consensus on the 2024 revision reflects genuine balance achievement or continued disagreement on root causes

---

## Pathfinder 2e Design Philosophy and Community Reception

### Takeaway

Pathfinder 2e's stated design philosophy prioritizes "meaningful character options" (avoiding "trap options" where players can create incompetent characters) and balance through mathematical rigor, with designers deliberately scaling back spells and buffing non-magical combat to create class parity. Community reception reflects general agreement that PF2e solved the martial-caster disparity problem better than D&D 5e, though at the cost of reduced "feeling of power" for some players.

### Cited Findings

**Designers' Stated Philosophy:**
- Core principle stated by Jason Bulmahn: "If you have to spend a great deal of time creating a character or reading a manual, that's a time investment that you have to sink in before the fun can begin" — [Paizo forum discussion](https://paizo.com/threads/rzs2v2wu?Pathfinder-2-has-the-right-design-philosophy=)
- Design avoids front-loading options at first level; instead, "mechanical options [are distributed] across all 20 levels, allowing beginners to learn the game incrementally" — [Paizo forum discussion](https://paizo.com/threads/rzs2v2wu?Pathfinder-2-has-the-right-design-philosophy=)
- Character options are "proper choices, not a hidden subgame of 'avoid making an incompetent character'" — stated design goal per Paizo forums — [Paizo forum discussion](https://paizo.com/threads/rzs2v2wu?Pathfinder-2-has-the-right-design-philosophy=)
- Design acknowledges low levels serve as a "game tutorial" for understanding mechanics, so developers focused on improving high-level gameplay (a "persistent Pathfinder 1e weakness") — [Paizo forum discussion](https://paizo.com/threads/rzs2v2wu?Pathfinder-2-has-the-right-design-philosophy=)
- Jason Bulmahn (Director of Game Design at Paizo as of 2017) "managed an incredibly talented group of game designers" over a "three-year design cycle" for PF2e starting in 2016 — [Screen Rant article](https://screenrant.com/pathfinder-2e-dungeons-dragons-5e-better-worse/)

**Balance Design Mechanics:**
- "PF2e was built from scratch with mathematical balance as a design priority" — [Screen Rant comparison](https://screenrant.com/pathfinder-2e-dungeons-dragons-5e-better-worse/)
- "Paizo deliberately scaled back some of the spells in the game, and beefed up melee and non-magical combat so that classes are more equally balanced" — [Screen Rant comparison](https://screenrant.com/pathfinder-2e-dungeons-dragons-5e-better-worse/)
- Proficiency scaling differs from 5e: "Everything a character is proficient in increases by 1 with every level, with additional boosts for Expertise, Mastery, and more" compared to D&D 5e's "bounded accuracy" — [CBR comparison](https://www.cbr.com/pathfinder-vs-dnd-5e/)
- Skills have tiered progression: "Trained and go through Expert, Master, and Legendary," plus skill feats representing specific extraordinary abilities, creating more granular progression — [CBR comparison](https://www.cbr.com/pathfinder-vs-dnd-5e/)
- Characters gain "feats at every level across multiple categories (class, ancestry, skills, general)," providing "huge amount of customization" — [CBR comparison](https://www.cbr.com/pathfinder-vs-dnd-5e/)
- Magic item balance: "PF2e expects characters to have multiple items at every level," unlike 5e which "partially managed balance by cutting back on magic items" — [CBR comparison](https://www.cbr.com/pathfinder-vs-dnd-5e/)

**Community Reception on Balance:**
- "The caster-martial disparity problem has been improved in Pathfinder 2e according to many people, though mostly in combat, and not always appeasing everyone" — [Web search summary](https://www.paizo.com/threads/rzs43rlk)
- "Pathfinder 2e represents a significant improvement over the original Pathfinder system (First Edition), which had more severe balance issues between martial classes and spellcasters" — [Community discussion analysis](https://www.paizo.com/threads/rzs43rlk)
- The approach generated significant debate: "Critics worried the design sacrifices the tactical depth and character customization veteran players valued, while supporters appreciated efforts to make low levels more engaging mechanically" — [Paizo forum discussion](https://paizo.com/threads/rzs2v2wu?Pathfinder-2-has-the-right-design-philosophy=)

**Design Philosophy Reception:**
- The system's solution maintains "tight power level control" by design: "Everyone is largely incapable of accomplishing anything of actual value alone to keep anyone from 'carrying the fight' but also punishing trying to perform too far out of their class's designated roles" — [Paizo forum discussion](https://paizo.com/threads/rzs2v2wu?Pathfinder-2-has-the-right-design-philosophy=)

### Inferences

1. Pathfinder 2e's mathematical approach to balance (scaling proficiencies per level, tiered skill progression) represents an intentional architectural difference from D&D 5e's bounded accuracy, suggesting designers learned from 3.5e that tighter math produces more reliable balance.

2. The design philosophy of avoiding "trap options" requires more front-loaded design work (defining what choices are viable) compared to 5e's "let players discover what works," potentially explaining why PF2e had a longer design cycle (3 years vs. 5e's presumably shorter development).

3. The community's acceptance of "tight power control" (preventing any character from "carrying the fight") appears to trade off the "feeling of power" (noted as a concern by some players) for system balance, a deliberate design choice documented in forum discussions.

### Gaps

- No designer interviews or blog posts specifically detailing what balance problems Paizo identified in 1e and how PF2e's specific mechanics address them (e.g., why proficiency-per-level vs. 5e's bounded accuracy)
- Limited quantitative community data on martial vs. caster actual play outcomes in organized play (Pathfinder Society) to validate the balance improvement claim
- No documented comparison of trap option frequency in PF2e vs. other systems (how often do players create objectively weak builds?)
- No designer commentary on the tradeoff between "feeling of power" and mathematical balance

---

## 13th Age Design Mechanics and Build Diversity Assessment

### Takeaway

13th Age prioritizes flexibility and player agency through iconic class design, the Talent system, and post-attack power selection for martial classes. The system was redesigned in 2nd edition to address community feedback that classes like the Ranger felt underpowered compared to more flexible classes like the Wizard, demonstrating designers' responsiveness to balance issues over a span of years.

### Cited Findings

**Core Design Philosophy and Origins:**
- Rob Heinsoo and Jonathan Tweet designed 13th Age to be "the version of the DnD style game that we wanted to play together on Wednesday night" — [War Gamer article](https://www.wargamer.com/13th-age/2nd-edition-dnd-designers)
- "The game was designed by the lead designers of D&D 3rd Edition (Tweet) and 4th Edition (Heinsoo)" — [War Gamer article](https://www.wargamer.com/13th-age/2nd-edition-dnd-designers)
- Originally pitched as a "love letter" to the d20 system, keeping "the combat crunch while shedding grid-dependency and skill counting" — [War Gamer article](https://www.wargamer.com/13th-age/2nd-edition-dnd-designers)

**Build Diversity Mechanics:**
- "Within classes there's plenty of room for diversity by picking Talents and attacks individually from a list, and enhancing them with Feats" — [13th Age class design guidelines](https://13thage.org/index.php/classes/646-13th-age-class-design-guidelines)
- "The degree of build diversity varies by class: Some classes have only one build and all talents push in the same direction, like the Paladin, while other classes are extremely diverse, depending on your choices, with the druid as the most extreme example" — [13th Age class design guidelines](https://13thage.org/index.php/classes/646-13th-age-class-design-guidelines)
- Fighters can "pick what power they use after they attack," Bards "sing songs where the final verse has an escalating effect," and Sorcerers "charge their spells before attacking" — [13th Age system guide](https://www.wargamer.com/13th-age/2nd-edition-dnd-designers)
- One Unique Thing system: each character "sets each character apart from all others, and provides the raw materials for adventures and campaign arcs" — [13th Age system description](https://ageofravens.blogspot.com/2014/12/13th-age-system-guide-for-new-players.html)

**Documented Balance Problems and 2nd Edition Fixes:**
- The Ranger in 1st edition had "some abilities that were always available," which meant they "had to be terrible" for balance purposes — [War Gamer interview](https://www.wargamer.com/13th-age/2nd-edition-dnd-designers)
- One Ranger player was "disappointed by how much cooler the redesigned Wizard was," indicating felt imbalance between class versatility — [War Gamer interview](https://www.wargamer.com/13th-age/2nd-edition-dnd-designers)
- 2nd edition addressed these issues with the Ranger receiving "a complete overhaul, transforming limited abilities into 'really interesting abilities that do a lot more damage' while keeping companions mechanically engaging" — [War Gamer article](https://www.wargamer.com/13th-age/2nd-edition-dnd-designers)
- The Fighter, "often criticised for being too simple in the first edition, being 'substantially improved' to offer more tactical depth" — [War Gamer article](https://www.wargamer.com/13th-age/2nd-edition-dnd-designers)
- The "Bard class has been entirely rewritten to better integrate with the system's rhythm of combat" — [War Gamer article](https://www.wargamer.com/13th-age/2nd-edition-dnd-designers)

**Design Philosophy on Balance:**
- Heinsoo's design principle: designers "each win about 50% of the time because we're each right about 50% of the time," where Heinsoo favors "powerful, fun abilities" while Tweet focuses on "balance" — [War Gamer interview](https://www.wargamer.com/13th-age/2nd-edition-dnd-designers)
- Heinsoo deliberately rejected forced repurchases, disliking "the whole Warhammer thing" of frequent edition cycles, shaping the decision to "maintain backward compatibility with existing supplements" — [War Gamer interview](https://www.wargamer.com/13th-age/2nd-edition-dnd-designers)

**Icon Connection System Complexity:**
- Designers realized their original rules for the Icon Connection system (which ties characters to the world) were too vague; experienced GMs were "using the Icon Connection system the same way," requiring expansion "from three pages to approximately 60 pages of detailed examples and clarification" — [War Gamer interview](https://www.wargamer.com/13th-age/2nd-edition-dnd-designers)

### Inferences

1. 13th Age's design demonstrates that post-attack power selection (Fighters choosing powers after seeing the attack result) is a viable mechanic for martial class flexibility, enabling "powerful, fun abilities" without creating trap options, as even poorly chosen powers can still deal damage.

2. The Ranger's imbalance in 1e (abilities that are "always available" must be weak) reveals a design constraint: passive abilities must be weak to be balanced, while active choices (like Wizard spell selection) can be powerful. 2e's redesign attempted to solve this by making Ranger abilities more active/conditional.

3. The Icon Connection system's evolution (3 pages → 60 pages) suggests that design clarity and adjudication complexity grew significantly, indicating the rule set may not scale as simply as the designers intended.

### Gaps

- No quantitative data on build diversity success in actual play (e.g., what percentage of players choose non-standard talent combinations?)
- Limited documentation on whether 2e's class redesigns actually achieved balance parity across all classes
- No comparative analysis of how 13th Age's post-attack power selection compares in complexity to D&D 5e or Pathfinder 2e for adjudication
- No designer discussion of whether the Talent system (player choice of class features) is easier or harder for GMs to adjudicate than feat-based or subclass-based systems

---

## Head-to-Head System Comparisons and Retrospectives

### Takeaway

While no single published designer retrospective directly compares all three systems, comparative analyses in the RPG community have documented that D&D 5e prioritizes accessibility and bounded accuracy over balance, Pathfinder 2e prioritizes mathematical balance and feat-based customization, and 13th Age prioritizes flexibility and DM narrative agency. The designers of 13th Age (former lead designers of D&D 3e and 4e) explicitly designed their system as a reaction to perceived limitations of those editions.

### Cited Findings

**D&D 5e vs. Pathfinder 2e Comparative Analysis:**
- "D&D 5e's design philosophy centers on 'bounded accuracy' and simplified mechanics that keep the focus on collaborative storytelling, while Pathfinder Second Edition emerged in 2019 as Paizo's answer to players craving tactical depth and character customization, built from the ground up to reward system mastery" — [CBR comparison](https://www.cbr.com/pathfinder-vs-dnd-5e/)
- D&D 5e treats feats as "optional extras" where "they vary in power, with little mind to balance," while PF2e is "feat focused" with characters gaining "feats at every level across multiple categories," providing "huge amount of customization" but requiring "more decision-making from players" — [CBR comparison](https://www.cbr.com/pathfinder-vs-dnd-5e/)
- Scaling difference: "A character will start with a bonus of around +5 to the things they're best at, and have around a +11 by 20th level" in D&D 5e, whereas "Everything a character is proficient in increases by 1 with every level, with additional boosts for Expertise, Mastery, and more" in PF2e — [CBR comparison](https://www.cbr.com/pathfinder-vs-dnd-5e/)
- Magic item management: "PF2e expects characters to have multiple items at every level," whereas D&D 5e "partially managed balance by cutting back on magic items" — [CBR comparison](https://www.cbr.com/pathfinder-vs-dnd-5e/)

**13th Age's Reaction to Previous Editions:**
- 13th Age was explicitly designed as a reaction to D&D 3e and 4e by their respective lead designers, described as "what happens when DnD designers get free rein" — [War Gamer headline](https://www.wargamer.com/13th-age/2nd-edition-dnd-designers)
- The system kept "the combat crunch while shedding grid-dependency and skill counting" from D&D 4e — [War Gamer article](https://www.wargamer.com/13th-age/2nd-edition-dnd-designers)

### Inferences

1. The three systems represent distinct design philosophies placed on a spectrum: D&D 5e (accessibility/storytelling) → 13th Age (flexibility/narrative) → Pathfinder 2e (mathematical balance/optimization depth).

2. Designers explicitly learned from previous editions: 13th Age shed 4e's grid complexity, Pathfinder 2e adopted 3.5e's feat-based customization while applying mathematical rigor, and D&D 5e simplified 3.5e's complexity.

### Gaps

- No published GDC-style retrospective or designer roundtable specifically comparing these three systems' balance philosophies
- Limited designer interviews from Paizo on what specific PF1e balance failures they aimed to prevent in PF2e (beyond general high-level commentary)
- No direct comparison of how trap options manifest in each system (what percentage of published options are considered non-viable?)

---

## AI-GM Runability and System Adjudication Complexity

### Takeaway

Current AI-GM experiments demonstrate that system complexity significantly impacts adjudication feasibility. Complex rule systems require dedicated rules-engine agents and clear adjudication guidelines. D&D 5e's bounded accuracy and simpler math may be more AI-friendly than Pathfinder 2e's layered progression system, but no system has been explicitly tested at scale with AI-GMs. The community discussion around TTRPG system design has not yet deeply explored AI-GM compatibility as a design criterion.

### Cited Findings

**AI-GM Current Challenges:**
- "Current AI GMs struggle with running complex rules since they have no concept of facts or truthfulness, and would need to add a rules-engine agent to make it reasonable" — [AI in TTRPGs article](https://www.myarchivist.ai/ai-dungeon-master/ai-in-ttrpgs)
- "Some AI frameworks separate story and rules so the AI never dumps mechanics into narrative, and force the AI to check every declared action against the System Profile and call for rolls when required" — [AI in TTRPGs article](https://www.myarchivist.ai/ai-dungeon-master/ai-in-ttrpgs)
- "Convention sessions have been run with an AI Game Master, where the human facilitator manages the logistics and safety, but the narrative responses, NPC reactions and consequence adjudication come from a language model" — [AI in TTRPGs guide](https://featheredfiction.com/2026/01/05/solo-rpg-ai-gm-guide/)
- "For complex systems, the GM often needs to do a lot more work before, during, and after the game, involving reading, planning, and doing math. Overly complicated rules often get in the GM and the players' way" — [AI in TTRPGs article](https://www.myarchivist.ai/ai-dungeon-master/ai-in-ttrpgs)

**Emerging AI GM Solutions:**
- "AI can become a co-GM, providing real-time support for improvisation and helping manage logistical aspects like spinning up stat blocks and creating descriptions and dialog on the fly" — [AI in TTRPGs article](https://www.myarchivist.ai/ai-dungeon-master/ai-in-ttrpgs)

**Community Discussion of System Runability:**
- As of late 2024/2025, the RPG community has begun discussing AI-GM compatibility ("Any AI Gamemasters Out There?" thread on EN World), but no major system designer has explicitly stated their design philosophy regarding AI-GM ease of adjudication — [EN World forum](https://www.enworld.org/threads/any-ai-gamemasters-out-there.708090/)

### Inferences

1. Bounded accuracy systems (like D&D 5e) may be inherently more AI-friendly than scaling progression systems (like Pathfinder 2e), as constant bonuses are easier for language models to track than layered proficiency tiers.

2. Systems requiring explicit action resolution (like 13th Age's post-attack power selection) may be easier for rules-engines to adjudicate than systems with implicit mechanical effects (like D&D 5e passive bonuses).

3. The lack of any system designer explicitly optimizing for AI-GM adjudication suggests this is not yet a design criterion, but it may become one as AI-GM tools mature.

### Gaps

- **Critical gap**: No system has been tested at scale (50+ sessions) with AI-GMs running the complete ruleset for balance adjudication
- No analysis of which system mechanics (Pathfinder 2e's tiered proficiencies, D&D 5e's advantage/disadvantage, 13th Age's Talent selection) are most difficult for AI to adjudicate consistently
- No published designer commentary from WotC, Paizo, or Pelgrane Press on whether AI-GM compatibility was considered in design, or should be in future editions
- No documentation of whether the added complexity of Pathfinder 2e's feat-per-level system creates proportionally higher adjudication burden for AI vs. human GMs
