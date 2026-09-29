# Computer vs. Tabletop Complexity Ceiling: MMORPG Design Lessons

## Concrete "Computer-Only" Hidden Complexity: What MMORPGs Track Invisibly

### Takeaway
MMORPGs maintain extensive background complexity that would be computationally unmanageable for a human GM, but this complexity remains invisible to players—threat tables, diminishing returns curves, and detailed damage modifiers are the prototypes of "machine-only" systems.

### Cited Findings
- **Threat Tables**: The WoW threat system is a multi-layered calculation where threat generation equals damage dealt (1 damage = 1 threat baseline), but is modified by class-specific multipliers (tanks receive 5.0x threat modifier via abilities like Blood Presence or Righteous Fury), ability-specific bonuses (each ability adds "bonus threat" on top of baseline damage-derived threat), and special calculations for healing (healing generates threat equal to half the effective healing per NPC that observed it, divided by observer count). — [Wowpedia: Threat](https://wowpedia.fandom.com/wiki/Threat)

- **Diminishing Returns Curves**: WoW uses two types of diminishing returns—Crowd Control (CC) diminishing returns where each successive CC application reduces duration by half until reaching 1/16th duration (PvE) or full immunity after 2 applications (PvP), with a 16-second reset window; and Stat diminishing returns where secondary stat scaling becomes progressively less valuable after 30% stacking, a mechanic introduced in Shadowlands specifically to limit what players could stack. — [Maxroll.gg: Crowd Control DR](https://maxroll.gg/wow/resources/crowd-control-diminishing-returns); [Maxroll.gg: Stat DR](https://maxroll.gg/wow/resources/stat-diminishing-returns)

- **Damage Formula Opacity**: Until Wrath of the Lich King, threat itself was entirely hidden and reverse-engineered by the community using trial-and-error AddOns, demonstrating that WoW was designed with systems players never see operating in the background. — [Warcrafttavern: Threat Guide](https://www.warcrafttavern.com/wow-classic/guides/threat-guide-reference-table/)

- **Path of Exile's Invisible Calculations**: Path of Building, a third-party calculator, can compute DPS "by factoring in auras, buffs, charges, curses, monster resistances and more," demonstrating that PoE's combat system involves dozens of multiplicative modifiers applied simultaneously—this complexity is computed but never fully displayed to the player. — [Path of Building Community](https://pathofbuilding.community/)

### Inferences
- The computers can absolutely handle threat tables, diminishing returns curves, and detailed modifier stacking. None of this is computationally constrained.
- These systems are kept hidden not because the computer can't display them (it easily could), but because displaying them would overwhelm players with information that has no strategic use. A player cannot "optimize the threat table"—they can only follow threat management rules the designer has already worked out.
- The threshold appears to be: if the complexity is purely background math with no player-facing strategic decisions tied to it, it can be unlimited. Threat, DR curves, and hidden buff stacking all fall into this category.

### Gaps
- No direct designer commentary found explaining why threat was kept hidden in early WoW or stating "we kept this hidden for cognitive load reasons." The Wotlk move to visible threat was presented as a quality-of-life improvement but not explicitly framed as responding to player comprehension limits.

---

## Deliberate Simplifications Despite Computational Capacity

### Takeaway
MMORPGs impose player-facing simplifications (Global Cooldown, debuff icon caps, action bar limits) explicitly to manage player comprehension, not because computers can't handle more—and these design decisions are documented with designer reasoning that centers on decision-making significance and cognitive load.

### Cited Findings
- **Global Cooldown as Comprehension Control**: Game Director Ion Hazzikostas stated the GCD change was specifically to give "individual abilities more significance again" by preventing players from combining multiple effects into one action. The reasoning was framed as preventing decision-collapse: "Without the global cooldown, the decision is easy because there is none—for example, a druid could activate their defensive ability and start casting a healing spell for the tank simultaneously." — [Gamesear: GCD Reversal](https://www.gamesear.com/news/world-of-warcraft-will-soon-be-reverting-the-rather-controversial-global-cooldown-change)

- **Debuff Icon Display Cap (16 default, up to 40 exist)**: WoW's default UI displays no more than 16 debuff icons despite up to 40 debuffs existing simultaneously on a target during raid encounters. This is a pure UI comprehension limit; players adopted third-party AddOns (BigDebuffs, Buff Buddy) to work around it, indicating the cap was recognized as a hindrance rather than a necessary computational limit. — [WoW Forums: Debuff Limit](https://us.forums.blizzard.com/en/wow/t/debuff-limit-and-target-frame/1094410)

- **Action Bar Size Limitations**: "Players want skill button designs to meet the following requirements: 1) to release skills quickly and easily; 2) to accurately release skills with less attention; 3) to quickly know when skills will be available." Dense action bars violate these requirements, so modern MMORPGs impose limitations not because computers can't render more buttons, but because "active skills and their cooldowns are second only to being able to see the enemy and health bars in terms of importance during combat." — [Medium: MMORPG UX/UI Evolution](https://medium.com/design-bootcamp/the-evolution-of-ux-ui-in-mmorpgs-mechanisms-and-emotional-impacts-f4562fd91a15)

- **Cognitive Load Ceiling in Learning**: Celia Hodent's research on working memory (cited in GDC presentations on The Gamer's Brain) shows that "working memory span is about 5 'items' more or less 2" but "3 items to process at the same time is THE MAXIMUM when in learning mode." New tasks demand significantly higher cognitive resources than familiar ones, meaning that even if a player masters threat mechanics, adding simultaneous complexity elsewhere causes cognitive collapse. — [Celia Hodent: GDC 2016 - The Gamer's Brain](https://celiahodent.com/gamers-brain-ux-onboarding/)

- **The "7±2" Rule in UI Design**: Game design guidance specifies designers should "limit the number of choices and information elements presented simultaneously" based on the 7±2 cognitive limit, suggesting that 7 is the practical ceiling for choices, not 2-3 but the strictest implementations use 3. — [LinkedIn: Cognitive Load Reduction](https://www.linkedin.com/advice/0/how-do-you-reduce-cognitive-load-game-design)

### Inferences
- The Global Cooldown was added as a deliberate simplification to prevent ability combinations from collapsing decision-making into "just press all buffs at once." This is not a computational problem—a computer can instantly calculate the optimal stacking. It's a comprehension problem: the player should have to *choose* which ability to use next, not have that choice made for them by the ability combinations.
- The 16-debuff cap demonstrates that WoW actively chose a comprehension limit over a computational one. The game tracks all debuffs perfectly; showing 16 of 40 is a deliberate UI design choice.
- The eventual reversal of the extended Global Cooldown (after 2 years of player complaints in BFA/Shadowlands) suggests that Blizzard overestimated what level of simplification was needed, then corrected by removing the GCD from burst cooldowns while maintaining it for offensive buffs.

### Gaps
- No direct designer commentary found explicitly stating "we capped debuff display at 16 because humans can't track 40 icons." The decision appears to be buried in UI design rationales rather than publicly discussed as a cognitive load limit.
- The Global Cooldown reversal was framed as a design philosophy shift, not explicitly as "we simplified too much for comprehension reasons."

---

## Path of Exile: Does No Human GM Mean No Complexity Ceiling?

### Takeaway
Path of Exile *demonstrates that removing the human-GM bottleneck does not eliminate the complexity ceiling—it simply moves it from "the GM can't track 40 calculations" to "the player can't understand 1,500 passive nodes," and the near-mandatory adoption of third-party Path of Building shows the real ceiling is player comprehension, not computation.

### Cited Findings
- **Passive Tree Scope**: Path of Exile has over 1,200-1,500 individual passive nodes offering customization, with PoE 2 maintaining this scale while adding Weapon Specialization that dynamically shifts Passives based on active weapon. — [VULKK: PoE 2 Passive Tree Guide](https://vulkk.com/2025/02/08/path-of-exile-2-passive-tree-guide/); [Maxroll.gg: PoE 2 Resources](https://maxroll.gg/poe2/resources/poe-2-passive-tree-and-dual-specialization)

- **Path of Building Necessity (Community Recognition)**: Path of Building is described as "an indispensable tool" for PoE aficionados and the "Passive Skill Tree Calculator stands as an indispensable tool, highlighting how the game's complexity makes such calculators essential for optimizing gameplay." The tool computes "skill DPS, damage over time, life/mana/ES totals" while "factoring in auras, buffs, charges, curses, monster resistances and more." — [Pathofbuilding.community](https://pathofbuilding.community/); [Blog: PoE Build Complexity](https://pathofbuilding.net/path-of-exile-passive-skill-tree-calculator/)

- **No Built-in Build Planner Until Recently**: PoE existed for years without an in-game build planning tool, relying entirely on third-party software (Path of Building), which itself was an external tool that became so critical that Grinding Gear Games eventually created an official build planner. This suggests the complexity ceiling was hit long before the game company addressed it mechanically. — [Path of Exile Official Site: Build Planner](https://poe.com/Build-Planner)

### Inferences
- The fact that Path of Building became mandatory despite being a third-party tool is direct evidence that player comprehension is the binding constraint, not computation. Grinding Gear Games could have designed PoE to require less tree planning (fewer nodes, simpler interactions, fixed builds), but instead they chose maximum mechanical complexity and accepted that players would need external tools.
- Path of Exile's evolution toward tool-integration (officially supporting Path of Building, integrating it into PoE 2) shows the design team explicitly *acknowledging* that players hit a comprehension ceiling and need computational support to navigate it. This is the inverse of a human GM's computational bottleneck—it's a player's comprehension bottleneck.
- PoE 2's Weapon Specialization *increases* complexity despite the game already hitting the threshold where external tools are mandatory. This suggests designers are choosing depth over simplification.

### Gaps
- No explicit designer commentary from GGG (Grinding Gear Games) stating "we accept third-party calculators because players can't track 1,500 nodes." The reasoning for Path of Building integration is framed as a convenience feature, not a comprehension necessity.
- Unknown: whether the PoE audience is self-selected toward players comfortable with external tools, or whether PoE alienates players who can't/won't use Path of Building.

---

## Background-Resolved vs. Player-Facing Complexity: The Real Dividing Line

### Takeaway
The distinction is fundamental and explains the entire ceiling: **background-resolved complexity (threat, diminishing returns, hidden modifier stacking) can be unlimited because it requires zero comprehension; player-facing complexity (build choices, debuff display, action priority) hits a hard comprehension wall at roughly 3-5 simultaneous items.**

### Cited Findings
- **Comprehension vs. Tracking vs. Depth**: Game design literature distinguishes three types: Comprehension Complexity (understanding rules and abilities—harmful), Tracking Complexity (mentally managing multiple simultaneous elements—harmful), and Depth (difficulty of finding the best move—valuable). Designers should minimize comprehension and tracking while preserving depth. — [Game Developer: Complexity vs. Depth](https://www.gamedeveloper.com/design/design-101-complexity-vs-depth)

- **Hidden Information as Complexity Solution**: "Hidden information allows you to notably increase the complexity of a game by giving players many more options to consider, but does it in a way that's invisible to the casual player." The metaphor used in game design is that a weapon might have ten stats and complex tradeoffs, but if each weapon also has a "level" and "suggested class," casual players make a quick, reasonable choice. — [RPGnet: Hidden Information Design](https://www.rpg.net/columns/virtually/virtually65.phtml)

- **Depth ≠ Complexity**: "The goal is to achieve simplicity and depth, not complexity. Half of game design is game design, and the other half is simplification." Depth emerges from permutations and combinations of simple mechanics, not from adding more variables the player must track. — [GameDev.net: Simplicity vs. Complexity](https://www.gamedev.net/forums/topic/683868-simplicity-vs-complexity/)

- **Cognitive Load in Learning**: "3 items to process at the same time is THE MAXIMUM when in learning mode," though familiar tasks expand this to 5±2 items. Beyond this, players suffer performance degradation and stress responses. — [Celia Hodent: The Gamer's Brain](https://celiahodent.com/gamers-brain-ux-onboarding/)

### Inferences
- **An AI DM's problem falls squarely into the background-resolved category.** The AI can calculate threat, diminishing returns, modifier stacking, and hidden accuracy checks with zero cognitive load on the player. These systems are actually *ideal* for AI adjudication because complexity is no longer visible.
- **The player-facing problem remains:** describing outcomes and mechanics clearly. An AI DM doesn't suffer the same comprehension bottleneck a human GM does (it can track 40 debuffs), but it faces a different problem—how to narrate/explain those 40 debuffs in a way a player understands.
- **This research confirms that "state volume isn't the risk, narration/comprehension is."** A computer can adjudicate unlimited hidden complexity. The ceiling is the player's ability to understand what the rules mean in plain English, not the computer's ability to calculate them.

### Gaps
- No research found directly addressing how to communicate complex hidden mechanics to players in comprehensible ways, which would be the core UI/narration challenge for an AI DM.

---

## Designer Decisions to Remove Complexity: When Simplification Became the Mistake

### Takeaway
While specific documented cases of "removed complexity turned out to be a mistake" are sparse in search results, the Global Cooldown reversal is a concrete example where Blizzard overestimated the need for simplification and walked it back after community feedback, suggesting that even well-reasoned comprehension limits can be miscalibrated.

### Cited Findings
- **Global Cooldown Expansion and Reversal**: In Battle for Azeroth, Blizzard extended the Global Cooldown to most offensive buff abilities to prevent "burst damage stacking" and give "individual abilities more significance." However, this resulted in "affected abilities didn't change in any significant way, so players still had to go through exactly the same rotations as before, just with far more stop-gaps sprinkled throughout," leading to widespread complaints. Blizzard reversed course in Shadowlands, removing GCD from most burst cooldowns while maintaining it on offensive buffs. — [Gamesear: GCD Reversal News](https://www.gamesear.com/news/world-of-warcraft-will-soon-be-reverting-the-rather-controversial-global-cooldown-change); [MMO-Champion: New GCD Discussion](https://www.mmo-champion.com/threads/2389509-New-Global-Cooldown/page13)

- **Cooldown-Centric Design Criticism**: Even after the reversal, players complained that "Cooldown-centric design does not seem to be going over well," indicating the fix didn't fully resolve the underlying issue. — [WoW Forums: Cooldown-Centric Design](https://us.forums.blizzard.com/en/wow/t/cooldown-centric-design-does-not-seem-to-be-going-over-well/2303262)

### Inferences
- The GCD expansion was theoretically sound (spread out ability usage to increase decision significance), but failed in practice because it reduced the pace of gameplay without increasing actual decision depth—players still used the same rotation, just slower. This suggests Blizzard confused **pace reduction** with **complexity reduction**.
- The fact that even after reverting most GCD applications, the design still faced criticism suggests that the simplification framework itself (limiting actions per second) was addressing the wrong problem. Players may have wanted either (a) more meaningful actions per second, or (b) fewer but more powerful actions, not simply slower button-presses.

### Gaps
- **Critical gap:** No comprehensive catalog of "complexity features removed from MMORPGs that players later requested back" was found in search results. The GCD is one example, but broader evidence would strengthen this section.
- No designer post-mortems found explaining why the GCD expansion failed from a design perspective, only player complaints and the eventual reversal.

---

## Synthesis: Where's the Real Line Between "Computer-Only" and "Player-Comprehension" Complexity?

### The Dividing Line Is Asymmetrical, Not Symmetric

The research reveals that the ceiling is not a single line but a **categorical boundary**:

1. **Below the line (Unlimited):** Complexity the computer resolves silently, generating outcomes without requiring player comprehension of the calculation. Examples: threat tables, diminishing returns curves, hidden accuracy checks, buff stacking multipliers. These can scale infinitely because the player never sees them.

2. **At the line (Critical):** Complexity the computer resolves but *must present to the player* in comprehensible form. Examples: debuff icons, action bar buttons, build passive nodes, cooldown timers. These hit a hard wall at 3-5 simultaneous items in learning, 7±2 items when familiar.

3. **The narration gap (AI-specific):** An AI DM faces the same comprehension challenges as a human GM regarding player-facing information, but gains the ability to handle unlimited hidden complexity. The AI DM's bottleneck is not "can it track 40 debuffs" (yes) but "can it explain 40 debuffs to a player in 2 sentences" (harder than it sounds).

### Why This Matters for an AI-Run D&D-Style RPG

- **You can have unlimited hidden subsystems** (threat tables, modifier stacking, NPC mood curves, faction reputation tracking) without cognitive load consequences, because the player never sees them.
- **You must ruthlessly simplify player-facing decisions** (to the 3-5 simultaneous choice limit during learning, 7 at most when familiar). This means either limiting the number of active abilities/mechanics, or **burying complexity in default suggestions** the way PoE does ("this passive is a Keystone, focus here") or the way weapons do ("Suggested for Barbarian").
- **The third-party tool precedent suggests an alternative:** accept that players *will* use external tools if complexity exceeds what the UI can represent. Path of Exile's decision to eventually integrate Path of Building officially suggests that supporting external optimization tools is acceptable, even preferable to over-simplifying.
- **"Depth not complexity" is the design goal:** A mechanic with 40 debuffs is complex. A mechanic with 3 debuffs that interact in 40 ways (due to hidden modifiers) is deep *and* simple.

### Open Question for Your Design

The research does not directly answer whether an AI DM should:
- A) Simplify the mechanics displayed to the player (matching MMORPG design), hiding the AI's calculation power
- B) Display the full complexity the AI can calculate, betting that player understanding of *why* a decision mattered is worth more than ease-of-choice
- C) Offer both: simple default paths and deep optimization paths, following the PoE model

The evidence suggests (A) + (C) is safest—simplify to 3-5 choices by default, but provide tools/information for players who want to understand the full mechanical depth underneath.

---

## Research Methodology & Source Quality Notes

### Sources Evaluated
- **Primary:** WoW forum discussions, Wowpedia (official wiki), Maxroll.gg (player-maintained reference), Pathofbuilding.community (third-party tool documentation)
- **Secondary:** Medium articles on MMORPG design and cognitive load, GameDeveloper.com design essays
- **Academic/GDC:** Celia Hodent's presentations on working memory and cognitive load cited in GDC materials
- **Limitations:** 
  - No direct designer interviews or post-mortems on specific simplification decisions were found.
  - Path of Exile community discussion is strong, but official Grinding Gear Games commentary on complexity thresholds is sparse.
  - The Global Cooldown is the only concrete "designed-then-reversed" mechanic documented.

### Inferences Clearly Flagged
- The claim that "background complexity can be unlimited" is inferred from the existence and design of threat tables, not from explicit designer statements.
- The claim that "PoE's complexity ceiling moved from computation to comprehension" is inferred from the necessity and integration of third-party tools, not from GGG's explicit framing.

