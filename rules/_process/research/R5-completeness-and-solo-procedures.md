# R5 — Completeness Taxonomy & Solo/Sandbox Procedures

> Research digest for The Game's ruleset. Defines what "complete" means for a solo, AI-GM'd,
> open-ended classic-fantasy sandbox with hidden mechanics; catalogs, with precise mechanics, the
> procedures real solo and sandbox games use to keep a world alive with no human GM; lays out
> how games structure time at every scale; and records how the best games onboard a newcomer.
> Author: research agent R5. Date: 2026-09-29. Status: research input (not rules). Every
> mechanic below is described in my own words; nothing is reproduced at length.

---

## 0. How to use this document

- **Chapter authors**: search this file for your chapter number (e.g. `→ 10`) to find every
  checklist item you own and every catalog procedure tagged for you. Each catalog entry ends with
  an **Adaptation for us** paragraph that translates the mechanic to our d20 / Vitality / Focus /
  hidden-mechanics frame.
- **The auditor** (whoever audits the finished ruleset): §1 is the audit instrument. Every row
  has a stable ID (e.g. `EX-07`). An audit passes a row when the owning chapter contains a rule
  with an ID that implements it, or the Decision Log records a deliberate exclusion with reasons.
- **The orchestrator**: §1's "UNOWNED" rows and §5 are the gaps in the current chapter map.

### Legend

**Essential? column**
- **E** — essential for v1 of *this* game (solo, AI-GM, open-ended sandbox, hidden mechanics).
  Missing it is a completeness defect.
- **R** — recommended: real games treat it as core, and our sandbox will hit it within the first
  ~10 sessions; ship a concrete rule (even a compact one).
- **O** — optional / later: ship a one-paragraph adaptation anchor so the DM can improvise
  consistently, but a full subsystem is not required for v1.
- **X** — not applicable (multiplayer-only or excluded by a locked decision); listed so the audit
  can confirm the exclusion was deliberate.

**Owner column** uses BRIEF.md §9's chapter map (`00`–`14`, `data`, `appendix`). "UNOWNED" means
no chapter's ownership line names it; a proposed home follows. "(implicit)" means a chapter
plausibly covers it but its ownership line does not name it — the risk is that each author
assumes someone else wrote it.

**Game abbreviations** (full citations in §7): 5.2 = D&D SRD 5.2 / 2024 DMG · PF2 = Pathfinder 2e
Remaster (Player Core / GM Core) · IS = Ironsworn · ISD = Ironsworn: Delve · ISF = Ironsworn:
Starforged · MY = Mythic GME 2e · BitD = Blades in the Dark · SaV = Scum and Villainy · SWN / WWN
= Stars / Worlds Without Number · DW = Dungeon World · CRN = Cairn 2e · ITO = Into the Odd ·
SD = Shadowdark · FBL = Forbidden Lands · TOR = The One Ring 2e (+ Strider Mode) · AM = Ars
Magica 5e · PD = Pendragon · MR = Mausritter · 4AD = Four Against Darkness · TYOV = Thousand
Year Old Vampire · KA = Kal-Arath · C&S = Crown & Skull · TB = Torchbearer · BtW = Beyond the
Wall · BW = Burning Wheel · UNE = Universal NPC Emulator · GUM = Gumshoe.

### Method

I surveyed the tables of contents and core procedures of 20+ complete games (§1.0), then merged
every subsystem they contain into one deduplicated list, then asked of each item: *would a solo
player with an AI DM, in an open sandbox, hit this?* and *who in our chapter map owns it?*
Mechanics in §2 were verified against SRDs and official free material where available (Ironsworn
SRD, Starforged SRD, the Delve preview pages, the Blades SRD, SRD 5.2, Archives of Nethys) and
against secondary sources elsewhere; where I state a number from a source I could not open
directly, the text says so.

---

## 1. Master completeness checklist

### 1.0 Table-of-contents survey (what "a complete game" contains)

| Game | Structure (chapter-level) | What it teaches us about completeness |
|---|---|---|
| **SRD 5.2** (CC-BY) | Playing the Game (rhythm of play, six abilities, d20 tests, actions, social interaction, exploration: vision & light, hiding, objects, hazards, travel; combat; damage & healing) · Character Creation (incl. level advancement, multiclassing, trinkets) · Classes · Origins (backgrounds, species) · Feats · Equipment (coins, weapons + mastery, armor, tools, gear, mounts & vehicles, lifestyle expenses, food/lodging, hirelings, spellcasting services, crafting, potions, scrolls) · Spells · **Rules Glossary** · **Gameplay Toolbox** (travel pace, creating a background, curses & magical contagions, environmental effects, fear & mental stress, poison, traps, combat encounters) · Magic Items (rarity, activation, cursed, resilience, crafting, sentient) · Monsters · Animals | The "toolbox" pattern: small, reusable hazard subsystems (fear, poison, curses, environment) that the DM grabs when needed. A **rules glossary** is a first-class chapter, not an appendix. Hirelings, lifestyle and services live in Equipment. |
| **D&D 2024 DMG** | The Basics (DM duties, session prep, **session zero**, ensuring fun for all) · Running the Game (combat, exploration, social; adjudicating) · DM's Toolbox · Creating Adventures (premise → encounters → rewards; 5 outlines) · Creating Campaigns · Cosmology · Treasure · **Bastions** (player-owned base: crafting, research, recruiting) · Lore Glossary | Session zero and safety are core DM chapters. A player base/holding system (Bastions) is how a modern core game supplies a downtime/endgame loop. |
| **PF2 Player Core ch.8 + GM Core** | Making choices · baseline content guidelines · rules overview · **three modes of play** (encounter / exploration / downtime) · checks & degrees of success · actions · defenses · damage · HP, healing, dying · hero points. GM Core: gamemastery basics, tools (hazards, afflictions, environment), building games, **subsystems** (victory points, influence, research, chases, infiltration, reputation, duels, leadership, hexploration, vehicles), treasure | Explicit **mode taxonomy** with rules for entering/leaving each mode. A generic progress engine (**victory points**) reused across a dozen named subsystems — exactly our "rich substrate / analogical anchor" goal. |
| **WWN** (free ed.) | Character creation · rules of the game · magic & arcane traditions · the world · **creating your campaign** (region, courts, societies) · **creating adventures** (combat/exploration/social/investigative challenges; ruins) · creatures · **factions & major projects** · index | A complete sandbox game dedicates ~half its pages to GM-side generators and a faction engine; PCs changing the world is a named subsystem ("major projects"). |
| **Ironsworn** (CC-BY) | Basics (moves, action/progress/oracle rolls, momentum, progress tracks) · your character (stats, vows, bonds, debilities, assets, experience, equipment) · moves (adventure, relationship, combat, suffer, quest, fate) · the setting & **Your Truths** · launching your campaign · foes · **oracles** | A solo game is complete only with (a) oracles, (b) a quest/vow layer that tells the player and the "GM" what the story is about, and (c) explicit session/campaign launch procedure. |
| **Ironsworn: Delve** | At the Threshold · Into the Depths (site play) · Finding Your Path (options) · Sites · Denizens · **Threats** · Objects of Power · Oracles | Site-crawl as a *progress-track* procedure (not a map), and long-running threats with menace tracks. |
| **Ironsworn: Starforged** (CC-BY) | Move categories: **session**, adventure, quest, **connection**, exploration, combat, suffer, recover, threshold, **legacy**, fate, **scene challenge**; truths; sector creation; oracles | Adds **session moves** (safety + recap + pacing formalized as moves), legacy tracks, connections, scene challenges. |
| **Mythic GME 2e** | Fate questions / Fate Chart / Fate Check · Chaos Factor · scenes (expected/altered/interrupted) · random events · meaning tables (+45 element tables) · lists (threads, characters) · thread progress track · behavior checks · adventure setup · rules summary | The canonical "GM in a box". Everything an AI DM would otherwise decide by fiat has a procedure. |
| **Blades in the Dark** (SRD) | Basics · action & consequences (position/effect, resistance, stress/trauma, harm) · characters · the crew · **the score** (engagement roll, flashbacks) · **downtime** (payoff, heat, entanglements, activities) · **the faction game** · the GM · setting · changing the game | The most precisely engineered **session-cycle** (free play → score → downtime) and **faction ladder** in print. |
| **Forbidden Lands** | Player's handbook: character, skills, talents, combat, **journeys (quarter days)**, **strongholds**, magic · GM's guide: running the game, bestiary, **legends & adventure-site generators**, random encounters | Sandbox hexcrawl with a base-building endgame and generators for sites and legends. |
| **The One Ring 2e** (+ Strider Mode) | Characters · adventuring phase · **journeys** (roles, events, fatigue) · **councils** (structured social) · combat · **fellowship phase** (incl. yearly Yule) · Loremaster · **Eye Awareness** · Strider Mode (solo: telling table, lore table, solo stance) | Two-phase play (adventure / fellowship), structured social encounters, and a hidden **world-attention meter**. |
| **Cairn 2e** | Player's guide: core rules, creation, inventory (slots), combat, magic, **scars** · Warden's guide: principles, running the game, factions, wilderness | Minimal but complete; shows how little a complete game strictly *needs* (and what it can never drop: principles, inventory, harm, travel). |
| **Mausritter** | Character · rules · magic · GM: **adventure sites, hexcrawl (19 hexes), factions, settlements**, hirelings/warbands | Faction advancement as a one-line end-of-session roll. |
| **Shadowdark** | Characters · gear · spells · running the game: **crawling rounds, light, encounter cadence**, bestiary, treasure, carousing | Time and light as the primary tension engines of a site crawl. |
| **Torchbearer** | Adventure phase (turns & **the Grind**) · camp phase · **town phase** (lifestyle) · winter phase | Time counted in *resolved actions* (deterministic — ideal for an AI). |
| **Pendragon** | … · **Winter Phase** (annual: events, aging, family, horses, glory → stat increases) | Year-scale procedure and generational play. |
| **Ars Magica 5e** | … · **seasons** (3-month activity blocks), covenant, lab, **aging rolls each winter** | Season-scale downtime as the main advancement engine. |
| **Four Against Darkness** | Solo dungeon: room/corridor generation (d66), contents (2d6), monster categories, **final-boss escalation** | A no-GM dungeon needs only: generation, encounter taxonomy, escalation to climax. |
| **Thousand Year Old Vampire** | Prompts, **memories (5 × 3 experiences), diary**, skills, resources, characters | Bounded memory as a mechanic (an analogy for our state-summarization problem). |
| **Kal-Arath** | 2d6 rules, classless, player-facing rolls; tables for oracle, travel, dungeons, settlements, encounters | "Rules light, table heavy" solo: procedures are the content. |
| **Crown & Skull** | No stats/HP; point-buy; skill & gear attrition; hex discovery tables | Attrition-as-health; discovery tables drive a solo sandbox. |

**Synthesis.** Every complete game contains the same ~15 families: foundations, character,
resolution, conflict, harm, advancement, powers, equipment/economy, adversaries, NPCs,
exploration, social, time/structure, living world, GM procedure — plus the *presentation* layer
(safety, onboarding, examples, references, glossary, index). Solo games add an **oracle layer**
and a **thread/quest layer** that group games leave to the human GM's head. Our checklist
follows those families.

### 1.1 Foundations & conventions

| ID | Item | What it is | Precedents (how they do it) | Ess. | Owner |
|---|---|---|---|---|---|
| FN-01 | Premise & tone statement | What the game is, what play looks like, what the player does | Every core book's ch.1; IS "what you do" | E | 14 (player) + 00 |
| FN-02 | Glossary | Every defined term, one line each | 5.2 Rules Glossary is its own chapter; TOR/BitD glossaries | E | 00 |
| FN-03 | Numeric & dice conventions | Rounding, dice notation, min/max, stacking of like bonuses | 5.2 "round down"; PF2 bonus types (circumstance/status/item don't stack with same type) | E | 00 |
| FN-04 | Rule-precedence principle | What wins when two rules conflict | 5.2 "specific beats general"; PF2 "most specific rule applies" | E | 00 |
| FN-05 | Rulings stance (Principle III) | When the DM may extrapolate; what it may never override | DW "principles"; OSR "rulings not rules"; our Principle III | E | 00 + 12 |
| FN-06 | State model | Every tracked variable, its owner, visibility (hidden vs player-facing) | Implicit in all; explicit in computer games; P3 demands classification | E | 00 |
| FN-07 | Tool surface | Which operations are deterministic tool calls | (project-specific) | E | 00 |
| FN-08 | Chapter contracts / interfaces | What each chapter guarantees others | (project-specific) | E | 00 |
| FN-09 | **Index** | Term → rule-ID lookup across chapters | Every print core book | E | **UNOWNED** → `appendix/index.md` (generated from rule IDs + glossary) |
| FN-10 | **Quick-reference sheets** | 1–2 page summaries: DM turn loop, DC ladder, degrees, conditions, time ladder, oracle | BitD/5.2/TOR cheat sheets (e.g. Alexandrian's BitD & Ars Magica sheets); IS move sheets | E | **UNOWNED** (14 owns player guide/codex only) → `appendix/quick-reference.md` (DM) + 14 (player) |
| FN-11 | Ruleset versioning & errata | How rules change and how live characters migrate | Constitution VI; PoE leagues; BitD "changing the game" | R | appendix/decision-log + 04 (content lifecycle) |
| FN-12 | Licensing & attribution | Credits for any CC-BY material adopted (IS/ISF oracles, SRD 5.2) | SRD 5.2 and IS require attribution text | R | **UNOWNED** → `appendix/credits.md` (only needed if we copy CC text/tables verbatim) |

### 1.2 Character creation

| ID | Item | What it is | Precedents | Ess. | Owner |
|---|---|---|---|---|---|
| CC-01 | Creation procedure | Ordered steps, start → playable | All; IS "creation summary"; ISF "launch" | E | 02 |
| CC-02 | Attributes | Broad-competence scores | 5.2 six abilities; IS 5 stats; BitD 12 actions/3 attributes | E | 02 (list in 00) |
| CC-03 | Origins / ancestry / culture | Locked trade-offs (P4) | 5.2 species+background; FBL kin; TOR cultures | E | 02 |
| CC-04 | Background & history prompts | Who you were; generates hooks | 5.2 backgrounds; IS background vow; BtW playbooks write the village; 13th Age "one unique thing" | E | 02 (+11 consumes hooks) |
| CC-05 | Birth variance + deferred reroll | P1 | FBL/TOR random tables; our P1 | E | 02 |
| CC-06 | Baseline competence floor | P2 floor for the unrecognized | 5.2 proficiency bonus; our P2 | E | 02 |
| CC-07 | Starting kit & wealth | Gear packages, coin | 5.2 packs; CRN "start with a bundle"; SD rolls | E | 02 (+08 prices) |
| CC-08 | **Drives / values / beliefs** | Player-authored statements of what the character wants/believes; tell the DM what to hook | BW Beliefs & Instincts; PD Traits/Passions; BitD vice & drives; FBL Pride & Dark Secret | E | 02 (authoring) + 03 (values tags) — **ownership of the *mechanic* not explicit** |
| CC-09 | **Starting goal & inciting incident** | A long-term goal plus an immediate crisis at session 1 | IS: begin with a background vow + inciting-incident vow; BitD starting situation | E | **Split, unassigned**: 02 (goal) + 13 (incident) — assign explicitly |
| CC-10 | Starting relationships | NPCs who matter from minute one | DW bonds; IS bonds; ISF connections; BtW village NPCs | E | 02 (+ NPC record per NP-02) |
| CC-11 | Character sheet / codex spec | What the player sees | P7; every game's sheet | E | 14 |
| CC-12 | Quick / pregenerated characters | 3–5 ready characters or a 5-question fast path | 5.2 starter sets; PF2 Beginner Box pregens; Cypher "I am an X who Ys" | R | **UNOWNED** → 14 (fast path) or 13 (pregens fitted to starter region) |
| CC-13 | Name & look tables | Cultural name lists, appearance prompts | IS/ISF name oracles; MR/CRN tables | R | 13 + data |
| CC-14 | Companion/animal at creation | Starting companion option | IS companion assets; MR hirelings | O | see NP-05 |

### 1.3 Resolution

| ID | Item | What it is | Precedents | Ess. | Owner |
|---|---|---|---|---|---|
| RS-01 | Capability gate | Can you attempt this at all | our VII | E | 01 |
| RS-02 | When to roll | Uncertainty + stakes; otherwise say yes / say no | DW "say yes or roll"; BitD "only roll when there's risk" | E | 01 |
| RS-03 | DC ladder & DC-setting procedure | How the DM picks a number | 5.2 DC table; PF2 level-based DCs + adjustments | E | 01 |
| RS-04 | Modifier sources & stacking | Where bonuses come from, what stacks | PF2 bonus types; 5.2 adv/dis doesn't stack | E | 01 (+00 FN-03) |
| RS-05 | Degrees of success | Crit/success/fail/crit-fail outcome meanings | PF2 four degrees; IS strong/weak/miss | E | 01 |
| RS-06 | Success-at-cost / partial menus | What a "weak hit" costs; complication menus | IS weak hit; BitD devil's bargain & consequences; PbtA GM moves | E | 01 + 12 |
| RS-07 | Advantage-type mechanics | Situational edge without math | 5.2 adv/dis; BitD +1d; IS +adds | E | 01 |
| RS-08 | Opposed & contested rolls | Two sides roll | 5.2 contests; SWN faction attacks | E | 01 |
| RS-09 | Extended / progress tasks | Multi-step goals with a track | IS progress tracks; BitD clocks; PF2 victory points | E | 01 (engine) + 11 (world clocks) |
| RS-10 | Help, teamwork, companions assisting | Assist mechanics | 5.2 Help; BitD assist (+1d, costs stress); PF2 Aid | E | 01 |
| RS-11 | Retry rule | When a failed check can be re-attempted | BW "let it ride"; PF2 "can't retry without change"; P17 | E | 01 |
| RS-12 | Secret / DM-side rolls | Rolls the player must not see the result of | PF2 "secret" trait (Recall Knowledge, Seek); 5.2 passive scores | E (hidden mechanics) | 01 (implicit) — **name it** |
| RS-13 | Fortune / world-outcome roll | Resolving what an NPC or faction manages without the PC | BitD fortune roll (dice = tier/quality); MY fate question | E | 01 |
| RS-14 | **Oracle / likelihood ladder** | How the DM answers its *own* uncertainty about the world | MY fate chart; IS Ask the Oracle (5 odds bands); KA d6 oracle; TOR telling table | E | **UNOWNED** as a named rule → 12 + `data/oracles.yaml` (see §2.1, §5 R-2) |
| RS-15 | Twist / complication injection rate | A fixed probability of "something unexpected" | IS matches (~10% of rolls); MY random events on doubles ≤ Chaos | R | 01 or 12 — **unassigned** |
| RS-16 | Graduated reveal (P17) | Degree gates how much info | our P17 | E | 01 |
| RS-17 | Compound / multi-action throttling | Many actions packed into one declaration | probe finding; PF2 multiple-attack penalty | E | 01 + 06 |
| RS-18 | Meta-currency | Player-spendable luck/hero points | PF2 hero points; IS momentum; TOR Hope; SD luck tokens; BitD stress-to-push | R | **UNOWNED** — decide (01 or 07); strongly relevant to the telegraphed "last-chance choice" |
| RS-19 | Knowledge / lore checks | What you know vs. what you discover | PF2 Recall Knowledge (secret, degrees); GUM core clues | E | 01 + 10 |

### 1.4 Conflict

| ID | Item | What it is | Precedents | Ess. | Owner |
|---|---|---|---|---|---|
| CF-01 | Starting a fight: surprise, ambush, initiative | Who acts first | 5.2 surprise; PF2 initiative via Perception/Stealth; IS Enter the Fray (initiative as a stake) | E | 06 |
| CF-02 | Action economy | Actions per turn | PF2 3 actions + reaction; P9 | E | 06 |
| CF-03 | Positioning / range / zones in text | Spatial model without a grid | IS/FATE zones; relationship-state positioning | E | 06 |
| CF-04 | Attacks & damage | Hit, damage, criticals | all | E | 06 |
| CF-05 | Defense & armor | Avoidance, soak | 5.2 AC; BitD armor boxes; IS armor-less harm | E | 06 |
| CF-06 | Conditions catalog | Named statuses with exact effects | 5.2 glossary conditions; PF2 conditions w/ values | E | 06 + `data/conditions.yaml` |
| CF-07 | Reactions / interrupts | Off-turn actions | PF2 reactions; 5.2 opportunity attacks | E | 06 |
| CF-08 | Morale, surrender, rout | When foes break | OSE/WWN morale 2d6; FBL; SD morale at half HP | E | 06 (+09 behaviors) |
| CF-09 | Escape & pursuit / chases | Disengaging; chase subsystem | PF2 chase VP; ISF scene challenge; 5.2 chase rules (2014 DMG) | E | 06 (escape) — chase **implicit**, name it |
| CF-10 | Non-lethal, subdual, capture | Taking prisoners / being taken | 5.2 knock out; our lethality lock | E | 06 + 07 |
| CF-11 | Cover, light, visibility | Seeing and hiding in a fight | 5.2 cover, obscurement | E | 06 |
| CF-12 | Environment & improvised actions in combat | Chandeliers, terrain, hazards | 5.2 improvised; P3 anchors | E | 06 |
| CF-13 | Companions/allies in combat | How NPC allies act | IS companion assets (no separate turns); 5.2 hirelings; WWN henchmen | E | **UNOWNED** — see NP-05 |
| CF-14 | Mounted & vehicle combat | Horses, carts, boats | 5.2 mounted combat; PF2 vehicles | R | 06 — **not named** |
| CF-15 | Mass combat / skirmish at scale | Armies, warbands, sieges | FBL/PD battles; MR warbands; WWN faction attacks | O | **UNOWNED** → 11 (abstract via faction engine) |
| CF-16 | Duels / formal single combat | Stylized one-on-one | PF2 duels; BW | O | 06 (anchor only) |
| CF-17 | Social conflict (structured) | Debate, negotiation as contest | TOR council (resistance + time limit); PF2 influence; ISF scene challenge | E | 10 |
| CF-18 | Stealth & infiltration | Sneaking past/through | PF2 infiltration (awareness vs edge points) | E | 10 — **implicit**, name it |

### 1.5 Harm, recovery, death

| ID | Item | What it is | Precedents | Ess. | Owner |
|---|---|---|---|---|---|
| HR-01 | Vitality loss consequences | What damage does at thresholds | our Vitality; IS health 0–5 | E | 07 |
| HR-02 | Lasting injury / scars | Durable wounds | CRN scars table (HP to exactly 0); IS maimed; BitD harm levels 1–4 | E | 07 |
| HR-03 | Dying state & last-chance choice | Telegraphed death | IS Face Death; PF2 dying 1–4; our lock | E | 07 |
| HR-04 | Defeat outcomes | Capture, loss, changed situation | IS Pay the Price; BitD consequences; our lock | E | 07 |
| HR-05 | Rest & recovery ladder | Short/long rest, camp, safe haven, downtime | 5.2 short/long rest; IS Make Camp/Sojourn; TOR safe havens; BitD recover clock | E | 07 (+10 downtime) |
| HR-06 | **Mental harm: fear, stress, despair** | Non-physical damage track | IS spirit + Face Desolation; BitD stress/trauma; TOR Shadow/Miserable; 5.2 "fear and mental stress" toolbox | E | 07 — **not named**; decide |
| HR-07 | Fatigue, exhaustion, deprivation | Food, water, sleep, exertion | CRN deprived → Fatigue slots; TB Grind; 5.2 exhaustion; FBL sleepless | E | 07 + 10 — **split, name owner** |
| HR-08 | **Afflictions: poison, disease, curses** | Staged conditions over time | PF2 afflictions (stages, onset, save cadence); 5.2 poison, curses & magical contagions | E | **UNOWNED** as a named subsystem → 07 |
| HR-09 | Healing magic & its limits | How supernatural healing is capped | WWN System Strain (heal cap = CON); 5.2 hit dice | R | 07 + 05 |
| HR-10 | Aging & long-term decline | Years passing | AM aging rolls each winter from 35; PD winter aging | O | **UNOWNED** → 11 (season/legacy) |
| HR-11 | Death aftermath & continuity | New character inherits something | ISF Continue a Legacy; IS Write Your Epilogue; BitD retirement | E | 11 |
| HR-12 | Telegraphing lethal risk | Warn before death is possible | our lock; ISD "Reveal a Danger"; DW "tell them the requirements/consequences and ask" | E | 07 + 12 |

### 1.6 Advancement

| ID | Item | What it is | Precedents | Ess. | Owner |
|---|---|---|---|---|---|
| AD-01 | Growth engine | P2/P5 tag tally → recognition → tiers | our constitution; BitD playstyle XP | E | 03 + 04 |
| AD-02 | Evidence capture | tag_event | our P5 | E | 03 |
| AD-03 | Tier crystallization | Offer/grant at meaningful moments | Stormlight Ideals; ISF legacy | E | 04 |
| AD-04 | Consolidation / provisional content | VI | our VI | E | 04 |
| AD-05 | Retraining / respec | Changing a choice | PF2 Retrain downtime; our VI | R | 04 |
| AD-06 | **Goal / quest completion rewards** | What finishing a player goal earns | IS vows (XP 1–5 by rank); ISF quests legacy track; MY thread closure | E | **UNOWNED** → 11 (threads) + 04 (as evidence/tier trigger) |
| AD-07 | **Reputation / renown / titles** | Public standing — the in-fiction voice of hidden progression | PD Glory; WWN Renown (spent on major projects); FBL reputation; BitD rep; TOR Valour/Wisdom-adjacent standing | E (hidden-mechanics voice) | **UNOWNED** → 11 (with 04 feeding it) |
| AD-08 | Wealth-as-advancement | Money converts to growth | SD carousing (gold → XP); ITO; AM | O | 08 (anchor) |
| AD-09 | Non-combat advancement parity | Growth from social/exploration/craft | BitD playbook triggers; our hierarchical tags | E | 03 |

### 1.7 Abilities & magic

| ID | Item | What it is | Precedents | Ess. | Owner |
|---|---|---|---|---|---|
| MG-01 | Slots, templates, cap | V/P5 | HWFWM; IS assets (3 abilities each) | E | 05 |
| MG-02 | Focus economy | P9 companion | D:OS2 AP | E | 05 |
| MG-03 | **Magic as a named subsystem** | What magic is in-world, who can do it, how it fails | 5.2 spellcasting; WWN arcane traditions; IS rituals (assets); CRN spellbooks + fatigue | E (classic fantasy) | 05 — **"magic" not named in map**; also 13 for lore |
| MG-04 | Ritual / extended magic & magical research | Long, costly, prepared magic | 5.2 rituals; AM lab work; IS Draw the Circle-style rituals | R | **UNOWNED** → 05 (ritual template) + 10 (as downtime project) |
| MG-05 | Magic item identification, activation, charges | How you learn and use items | 5.2 attunement, charges, "the next dawn"; SD | E | 08 |
| MG-06 | Divine/religious power | Gods, prayer, faith | 5.2 clerics; TOR; WWN | R | 05 + 13 |
| MG-07 | Corruption / cost of power | Magic's price | IS corrupted bane; DCC corruption; P12 | R | 05 |
| MG-08 | Counter-magic & dispelling | Opposing effects | 5.2 counterspell/dispel | R | 05 |

### 1.8 Equipment, wealth, economy

| ID | Item | What it is | Precedents | Ess. | Owner |
|---|---|---|---|---|---|
| EQ-01 | Equipment list & properties | Weapons, armor, tools, gear | 5.2 equipment chapter | E | 08 |
| EQ-02 | **Encumbrance / inventory** | How much you can carry | CRN/MR/SD slot inventory; C&S; IS encumbered condition | E | 08 — **not named** |
| EQ-03 | Currency & prices | Coins, price list | 5.2 coins | E | 08 |
| EQ-04 | Buying/selling, availability | What a settlement sells; sell-back rates | ACKS market classes; 5.2 "selling treasure" | E | 08 |
| EQ-05 | Lifestyle & upkeep | Cost of living between adventures | 5.2 lifestyle expenses; TB lifestyle cost; BitD coin/stash | R | 08 (+10) |
| EQ-06 | Loot generation | Pool-gate / fill-quality | our P5; 4AD treasure tables | E | 08 |
| EQ-07 | Crafting | Making items | 5.2 crafting; PF2 Craft downtime | E | 08 |
| EQ-08 | Durability, wear, repair | Gear attrition | MR usage dots (3 per item); C&S gear attrition; CRN | R | 08 |
| EQ-09 | Consumables, light, supply abstraction | Torches, rations, ammo | IS supply track (0–5); usage die; SD torches | E | 08 + 10 |
| EQ-10 | Mounts, animals, vehicles, ships | Buying & using transport | 5.2 mounts & vehicles; TOR mounts reduce fatigue | R | **UNOWNED as named** → 08 (goods) + 10 (speed) |
| EQ-11 | Services & hirelings | Paying NPCs for work | 5.2 hirelings & spellcasting services | R | 08 (prices) + NP-05 |
| EQ-12 | **Holdings / base / stronghold** | A place the PC owns and improves | 2024 DMG Bastions; FBL strongholds; BitD lair; AM covenant | R (sandbox endgame) | **UNOWNED** → 11 (or 10 downtime) |
| EQ-13 | Treasure economy calibration | How much wealth enters the world | 5.2 treasure tables by tier | R | 08 |

### 1.9 Adversaries

| ID | Item | What it is | Precedents | Ess. | Owner |
|---|---|---|---|---|---|
| AV-01 | Archetypes & stat templates | Pool gates | 5.2 stat blocks; IS ranks | E | 09 |
| AV-02 | Threat bands / encounter difficulty | Budgeting a fight without levels | IS ranks (troublesome→epic); PF2 XP budget | E | 09 |
| AV-03 | Behaviors, tactics, motives | How they fight and want | DW monster instinct + moves; 4AD reaction tables | E | 09 |
| AV-04 | Bestiary content | Actual creatures | all | E | 09 + data |
| AV-05 | Boss/legendary/lair | Climactic foes | 5.2 legendary actions; 4AD final boss | R | 09 |
| AV-06 | Random encounter tables & cadence | What you meet and how often | SD by danger level; PF2 flat check by terrain; OSE per terrain | E | 10 (cadence) + 09 (tables) |
| AV-07 | **Reaction roll** | Initial disposition of a met creature/NPC | OSE/WWN 2d6 reaction; 4AD monster reactions | E | **UNOWNED** → 10 (social) or 12 |
| AV-08 | Traps | Mechanical dangers | 5.2 traps toolbox; PF2 hazards | E | 10 (hazards) — **traps not named** |
| AV-09 | Adversary persistence & escalation | Recurring enemies learn | ISD threats; BitD faction status | R | 11 |

### 1.10 NPCs & companions

| ID | Item | What it is | Precedents | Ess. | Owner |
|---|---|---|---|---|---|
| NP-01 | **NPC generation** | Name, look, motive, mood, power | UNE (power vs PC, verb+noun motivation, bearing, mood); MY behavior check; IS/ISF character oracles | E | **UNOWNED as named** → 12 + `data/oracles.yaml` |
| NP-02 | NPC persistence / roster | Who exists, what they know, where they are | MY Characters list; our externalized state | E | 12 + 00 (state) |
| NP-03 | Disposition & relationship tracks | Attitude that moves | BitD status −3..+3; ISF connections (rank + progress); PF2 attitudes | E | 10 |
| NP-04 | Off-screen NPC agency | NPCs act when you're away | BitD faction clocks; MR faction rolls; MY NPC action events | E | 11 |
| NP-05 | **Companions / hirelings / followers** | NPCs who travel and fight with the PC | IS companion assets; MR hirelings & warbands; WWN henchmen; 5.2 hirelings; TOR Strider | E (solo) | **UNOWNED** → new section (proposed 09 stats + 12 play + 10 hiring) |
| NP-06 | NPC voice & play | How the DM portrays | DW "give every monster life"; MY behavior check | E | 12 |
| NP-07 | Romance, family, heirs | Intimate & generational ties | PD family & heirs; TOR Raise an Heir | O | **UNOWNED** → 11 (legacy) + SC content prefs |

### 1.11 Exploration & environment

| ID | Item | What it is | Precedents | Ess. | Owner |
|---|---|---|---|---|---|
| EX-01 | Travel procedure | Pace, time, route | IS Undertake a Journey; TOR marching tests; 5.2 travel pace | E | 10 |
| EX-02 | Navigation & getting lost | Finding the way | FBL Lead the Way; OSE lost chance; PF2 Map the Area | E | 10 |
| EX-03 | Journey roles / activities | Who does what on the road | FBL quarter-day activities; TOR Guide/Hunter/Look-out/Scout; PF2 exploration & hexploration activities | E | 10 |
| EX-04 | Weather & seasons | Conditions affecting travel | CRN d6/day; TOR season tables; ACKS climate | E | 10 (+11 calendar) — **not named** |
| EX-05 | Environmental hazards | Cold, heat, falling, drowning, suffocation | 5.2 environmental effects | E | 10 |
| EX-06 | Foraging, hunting, survival | Living off the land | FBL forage/hunt/fish w/ mishaps; PF2 Subsist | E | 10 |
| EX-07 | Wilderness structure in text | Hexes vs pointcrawl vs region graph | MR 19-hex; WWN hexes; IS waypoints (abstract) | E | 11 (generation) + 10 (movement) — **decide** |
| EX-08 | **Site / dungeon crawl procedure** | Moving through a dangerous place | ISD Delve the Depths (areas as progress); SD crawling rounds; TB turns; 4AD rooms | E | 10 — **not named** (map says "travel, hazards, investigation") |
| EX-09 | Light & vision | Darkness as a resource | SD real-time torch; TB torch/lantern/candle turns | E | 10 |
| EX-10 | Searching & discovery | Finding hidden things | PF2 Search/Seek (secret); 5.2 | E | 10 |
| EX-11 | Investigation structure | Clue economy | Alexandrian Three Clue Rule; GUM core clues | E | 10 |
| EX-12 | Settlements & urban play | Towns as sites: services, districts | MR settlements; WWN courts; BitD Doskvol | E | 11 (gen) + 13 (content) — **not named** |
| EX-13 | Discovery & landmarks | Wonders found in the wild | ISF Make a Discovery (d100); FBL | R | 11 |
| EX-14 | Spatial description in text | Communicating layout without maps | (none — text-only is novel) | E | 12 — **UNOWNED as named** |

### 1.12 Social & information

| ID | Item | What it is | Precedents | Ess. | Owner |
|---|---|---|---|---|---|
| SO-01 | Social influence resolution | Persuade, intimidate, deceive | PF2 influence; IS Compel; BitD Sway/Command | E | 10 |
| SO-02 | Insight / lie detection | Reading people | 5.2 Insight; PF2 Sense Motive (secret) | E | 10 |
| SO-03 | Bargaining & trade | Haggling prices | ACKS; 5.2 | R | 10 + 08 |
| SO-04 | Languages & communication | Who can talk to whom | 5.2 languages | R | **UNOWNED** → 13 (languages) + 01 (gate) |
| SO-05 | Law, crime, heat | Authorities react | BitD heat/wanted/entanglements | R | 11 |
| SO-06 | Rumors & information economy | What people say | WWN; BitD Gather Information; TOR Gather Rumours | E | 11 |
| SO-07 | Favors & debts | Owed obligations | BitD Cooperation entanglement; FBL | R | 11 (+NP-03) |

### 1.13 Time & structure

| ID | Item | What it is | Precedents | Ess. | Owner |
|---|---|---|---|---|---|
| TM-01 | **Canonical time ladder** | Every scale defined with conversions | OSE round/turn/day; MR round/turn/watch; PF2 modes | E | **UNOWNED** → 00 (see §3) |
| TM-02 | **Tick table** | What happens at each boundary (end of round, turn, watch, day, scene, session, downtime, season) | TB Grind; SD crawling cadence; MY end-of-scene; BitD downtime | E | **UNOWNED** → 00 (with each chapter registering its ticks) |
| TM-03 | Mode transitions | Entering/leaving combat, exploration, downtime | PF2 modes; BitD phases | E | 12 |
| TM-04 | Scene framing & cutting | Where scenes start and end | MY expected/altered/interrupted; BitD "cut to the action" | E | 12 |
| TM-05 | Session open/close | Recap, flags, momentum, next-time notes | ISF Begin/End a Session; MY bookkeeping | E | 12 |
| TM-06 | Downtime menu | What can be done between adventures | BitD 6 activities; PF2 downtime; TOR undertakings | E | 10 |
| TM-07 | **Calendar & timekeeping** | Dates, days of week, festivals, seasons | PD year; AM seasons; TOR Yule; FBL | E | **UNOWNED** → 11 (engine) + 13 (content) |
| TM-08 | **Season/year phase** | Periodic big-tick procedure | PD Winter Phase; TOR Yule; AM winter aging | R | **UNOWNED** → 11 |
| TM-09 | Pacing controls | Dead-end prevention, escalation | P16; MY Chaos Factor; IS momentum | E | 12 |
| TM-10 | Time skips / montage | Fast-forwarding safely | ISF Take a Break; BitD downtime | E | 12 |
| TM-11 | Real-time vs play-time | Whether table time matters | SD real-time torches (not usable async) | E (decide) | 00 |

### 1.14 Living world

| ID | Item | What it is | Precedents | Ess. | Owner |
|---|---|---|---|---|---|
| LW-01 | Factions: stats, goals, turns | Organizations with agency | SWN/WWN factions; BitD ladder; MR factions | E | 11 |
| LW-02 | Clocks / fronts / threats | Hidden timers for dangers | BitD clocks; DW fronts; ISD threats | E | 11 |
| LW-03 | Hooks & adventure generation | Where adventures come from | WWN adventure creation & tags; BtW scenario packs | E | 11 |
| LW-04 | Rumors | See SO-06 | — | E | 11 |
| LW-05 | Consequence propagation | Actions ripple | BitD heat/status; faction reactions | E | 11 |
| LW-06 | Region / sandbox generation | Making new places | WWN region; ISF sectors; MR hexcrawl | E | 11 |
| LW-07 | Site generation | Dungeons/ruins on demand | ISD theme × domain; WWN ruins; 4AD | E | 11 (implicit in "sandbox generation") |
| LW-08 | Random world events | Unprompted happenings | MY random events; ISF Begin a Session vignettes | E | 11 + 12 |
| LW-09 | **Player-driven world change** | Big projects that alter the map | WWN major projects; BitD long-term projects; Bastions | R | **UNOWNED** → 11 |
| LW-10 | Domain / rulership | Ruling land or leading an org | WWN rulership; ACKS domains | O | **UNOWNED** → 11 (anchor) |
| LW-11 | Retirement & legacy | Player-chosen ending | IS Write Your Epilogue; ISF Continue a Legacy; BitD retire | E | 11 |
| LW-12 | Campaign genesis / world truths | Player-shaped setting facts | IS/ISF Truths; BtW village | E | 13 |
| LW-13 | Thread (quest) register | The list of open storylines | MY Threads list; IS vows | E | **UNOWNED** as named → 11 (+12 use) |
| LW-14 | World-attention / notoriety meter | The world notices the PC | TOR Eye Awareness; BitD heat | R | 11 |

### 1.15 DM procedures & principles

| ID | Item | What it is | Precedents | Ess. | Owner |
|---|---|---|---|---|---|
| DM-01 | Agenda & principles | What the DM is trying to do | DW agenda/principles; BitD GM goals | E | 12 |
| DM-02 | Turn loop | The per-message algorithm | (project-specific) | E | 12 |
| DM-03 | Complication / GM-move menu | What to do on a miss | DW GM moves (soft/hard); IS Pay the Price d100 | E | 12 + 01 |
| DM-04 | Improvising from substrate | Reach-and-adapt | P3 | E | 12 |
| DM-05 | **Rulings precedent log** | Recording novel rulings so they're applied consistently | (no game does it formally; human GMs keep notes) | E (goal 2) | **UNOWNED** → 12 + 00 (state) |
| DM-06 | Narration standards | What to say/hide; no blue boxes | our tone lock | E | 12 |
| DM-07 | Between-session / off-screen procedure | Faction turns, clock ticks while away | BitD downtime; MR end-of-session rolls | E | 12 + 11 |
| DM-08 | Continuity audit | Reconciling narration vs state | P13 | E | 12 |
| DM-09 | Handling out-of-character talk | Rules questions, codex queries | P7; ISF session moves | E | 12 + 14 |
| DM-10 | Prep: situations not plots | Stance for sandbox content | Alexandrian; DW "draw maps, leave blanks" | E | 12 |

### 1.16 Safety, consent, table culture

| ID | Item | What it is | Precedents | Ess. | Owner |
|---|---|---|---|---|---|
| SC-01 | **Content preferences (lines & veils)** | What must never appear / appear offscreen | TTRPG Safety Toolkit; ISF Set a Flag; PF2 baseline | E | **UNOWNED** → 14 (player-set) + 12 (DM obligations) |
| SC-02 | **In-play adjust / skip / rewind** | Changing course mid-scene | X-card; Script Change; ISF Change Your Fate (reframe/refocus/replace/redirect/reshape) | E | **UNOWNED** → 12 + 14 |
| SC-03 | **Session zero** | Expectations: tone, lethality, themes, pacing | 2024 DMG session zero; BitD first session | E | **UNOWNED** → 13 (first-session script) + 14 |
| SC-04 | Lethality/difficulty consent | Explicit agreement to "death is real but telegraphed" | our lock; 2024 DMG | E | same as SC-03 |
| SC-05 | Moderation boundary | Out-of-game content safety separate from world state | P13 | E | 12 (rule) |
| SC-06 | Undo / retcon policy | When the player can take back a declaration | common table practice | R | 12 |

### 1.17 Onboarding & presentation

| ID | Item | What it is | Precedents | Ess. | Owner |
|---|---|---|---|---|---|
| OB-01 | "What is a roleplaying game" for a newcomer | Plain-language explanation | 5.2 intro; PF2 Beginner Box | E | 14 |
| OB-02 | **First-session teaching arc** | A scripted-but-open opening that introduces one subsystem at a time | PF2 Beginner Box solo adventure; BG3-style tutorial; BitD first score | E (first playtester is a newcomer) | **UNOWNED** → 13 |
| OB-03 | Play examples everywhere | Worked transcripts | IS/ISF extensive examples; BitD | E | every chapter + 14 |
| OB-04 | Long-form example of play | One full session annotated | 5.2 "example of play"; IS | E | 14 (or `_process/playtests`) |
| OB-05 | Progressive rules disclosure | Teach when needed | BitD; PbtA "the conversation" | E | 12 + 14 |
| OB-06 | Player-facing "how to act" advice | What kinds of inputs work well | IS "tips"; DW | E | 14 |

### 1.18 Deliberately excluded (audit confirmation)

| ID | Item | Why excluded | Ess. | Owner |
|---|---|---|---|---|
| X-01 | Spotlight balance between players | Single-player (IV) | X | — (note in 12 that spotlight = *NPC companions & threads* instead) |
| X-02 | Party role distribution / PvP | Single-player | X | — |
| X-03 | Diegetic "System" UI | Locked tone | X | 12 (explicitly forbidden) |
| X-04 | Maps/visual handouts | Text-only (IV) | X | — (EX-14 compensates) |
| X-05 | Real-time torches (SD) | Async text play has no reliable real time | X | 10 (use action-count time instead, §3) |

**Count:** 189 audit rows + 5 deliberate exclusions (plus the 21-game TOC survey). **UNOWNED: 33 rows;
owned only implicitly, split without an assignee, or "not named" in the owner's map line: 17 more rows** — all 50 consolidated into 18 gaps in §5.1. Essential split: 153 E, 30 R, 7 O.

---

## 2. Solo & sandbox procedure catalog

**Why solo procedures are the right source for an AI DM.** A solo player is simultaneously
protagonist and GM, and has two problems: (1) they cannot surprise themselves, and (2) they are
biased toward the outcomes they'd like. Solo designers solved both with *procedures*: dice decide
what the author won't, and structured lists/tracks keep threads from being forgotten. An AI DM has
the same two problems in a different form: (1) language models regress to the most probable,
most clichéd continuation (the world stops surprising), and (2) they are documented to be
generous toward the player (constitution VII's rationale) and to drift from state (P3/P13).
Every procedure below is a tested answer to one of those problems. Each entry gives: the source,
the precise mechanic, what problem it solves, and an **Adaptation for us** with chapter tags.

Catalog groups: §2.1 oracles & world-questions · §2.2 scene & session structure · §2.3 progress,
pressure & pacing · §2.4 living-world engines · §2.5 exploration, sites & travel · §2.6
generation · §2.7 memory, legacy & long time.

### 2.1 Oracles & world-questions

#### P-01 Mythic Fate Chart / Fate Check + Chaos Factor (MY) → 12, data
- **Mechanic.** Any yes/no question about the world ("Is the gate guarded?") is assigned one of
  nine odds levels (from Impossible through 50/50 to Certain). *Fate Chart*: roll d100 and
  cross-reference odds × current Chaos Factor; each cell has three thresholds — an
  exceptional-yes band (the bottom ~fifth of the yes range), a yes threshold, and an
  exceptional-no band (the top ~fifth). At 50/50 and Chaos 5 the yes chance is 50%. *Fate Check*
  (2e alternative): roll 2d10 and sum, add an odds modifier (±2 Likely/Unlikely, ±4 Very, ±6
  Sure Thing/No Way, ±8 Has To Be/Impossible), add a Chaos modifier (Chaos 3 or lower shifts
  toward "no", 6 or higher toward "yes", 4–5 neutral); 11+ is yes.
- **Chaos Factor** is an integer 1–9, starting at 5 (2e). It rises by 1 after a scene the PC
  did not control and falls by 1 after a scene the PC did control. It raises the chance of
  "yes" (more things happen), of random events, and of scenes not going as expected.
- **Random events on questions.** Rolling doubles (11, 22, … 99 on d100) where the repeated digit
  is ≤ the Chaos Factor triggers a random event alongside the answer (≈ Chaos% of 9 in 100).
- **Solves.** Author bias on world facts; gives the world a dial for "how out of control is
  this" that is *driven by play*, not by the GM's mood.
- **Adaptation for us.** Give the DM a deterministic `ask_oracle(question, odds)` tool with a
  9-rung odds ladder expressed in d100 (keeps our d20 for *player* resolution, reserving d100
  for *world* questions so they are never confused). Replace Chaos Factor with a **Tension**
  value 1–9 that ticks from P16's existing counter: +1 per scene in which the PC was reactive or
  lost ground, −1 per scene in which the PC drove events. Tension then sets random-event
  frequency (P-11) and scene alteration (P-05). This converts P16's "after ~3 inconclusive
  results, inject a lead" from a DM judgment into a mechanical consequence. Mark `[D]`.
  **Rule of use:** the DM asks the oracle only for facts *not already established* and not
  covered by a more specific table; established facts are never re-rolled (consistency, goal 2).

#### P-02 Ironsworn "Ask the Oracle" (IS, ISF) → 12, data
- **Mechanic.** Pick odds and roll d100: *Almost Certain* yes on 11+, *Likely* 26+, *50/50*
  51+, *Unlikely* 76+, *Small Chance* 91+. A roll of doubles (11, 22, …) signals an extreme
  result or twist. Beyond yes/no, "Ask the Oracle" also means rolling on inspiration tables
  (action + theme; descriptor + focus) or simply choosing the most interesting answer.
- **Solves.** Same as P-01 with fewer moving parts; the doubles-as-twist rule gives a constant
  ~9–10% surprise rate independent of any chaos dial.
- **Adaptation for us.** If P-01's Tension dial is judged unnecessary, this five-band ladder is
  the minimal viable oracle. Recommend adopting IS's five bands *plus* P-01's Tension shift of
  one band per 2 points above/below 5 — simple and tunable. Either way, doubles on d100 = twist.

#### P-03 Kal-Arath d6 oracle with "but" (KA) → 12
- **Mechanic.** d6: 1–3 no, 4–6 yes; 1 and 6 are extreme ("no, and…" / "yes, and…"); odd
  results attach "but". Likely: roll 2d6 keep higher; unlikely: keep lower.
- **Solves.** Produces *qualified* answers (yes-but, no-and) rather than binaries — the texture
  that makes an answer generative.
- **Adaptation for us.** Borrow the six-way *answer shape* (no-and / no / no-but / yes-but / yes
  / yes-and) as the output vocabulary of our oracle tool, mapping d100 bands onto it. Qualified
  answers are exactly what P16 needs (a "but" is a lead).

#### P-04 Meaning tables, element tables & "Discovering Meaning" (MY) ; UNE ; TOR Lore Table → 12, data
- **Mechanic.** When an event or answer needs *content*, roll two d100 words — an Action pair
  (verb + subject) or a Description pair (adverb + adjective) — and interpret in context. 2e adds
  45 themed element tables (locations, characters, objects, etc.) and "Discovering Meaning" for
  questions a yes/no can't answer. TOR's Strider Mode Lore Table uses a feat die + success die
  to index action/aspect/focus words. UNE generates an NPC via: power relative to the PC
  (much weaker … much stronger), a motivation from verb × noun tables (three motives,
  ranked), a bearing (demeanor), a conversational mood toward the PC, and a focus of interest.
- **Solves.** LLM cliché: two random words force an unexpected but interpretable direction.
- **Adaptation for us.** Ship `data/oracles.yaml` with (a) an action/theme pair table, (b) a
  descriptor/focus pair table, (c) a UNE-shaped NPC generator whose outputs are *written to
  state* the moment the NPC is named (NP-01, NP-02). Rule: when a meaning roll is made, the DM
  must commit the interpretation as a fact via `set_fact` before narrating it. `[D]` roll,
  `[J]` interpretation.

#### P-05 Mythic scene test: expected / altered / interrupted (MY) → 12
- **Mechanic.** Before each scene the player states the *expected* scene. Roll d10: if above
  the Chaos Factor, it happens as expected; if ≤ Chaos and **odd**, it is an **Altered Scene**
  (the next most likely version — 2e offers a Scene Adjustment roll: remove/add a character,
  reduce/increase an activity, remove/add an object, or two adjustments); if ≤ Chaos and
  **even**, it is an **Interrupted Scene** (a random event replaces it).
- **Solves.** Prevents a world that always cooperates with the protagonist's plan.
- **Adaptation for us.** At every scene boundary the DM runs one d10 vs Tension (P-01). This is a
  cheap, deterministic source of "the world moved while you planned". `[D]` roll, `[J]`
  adjustment. Hidden: the player never sees the roll, only the altered fiction.

#### P-06 Mythic behavior check & NPC action tables (MY 2e) → 12
- **Mechanic.** An NPC is given descriptors (identity, personality, current activity). When
  its reaction is uncertain, a fate question keyed to those descriptors is asked; if its action
  is uncertain, an NPC action roll (2d10 with a disposition modifier from passive to
  aggressive) chooses between continuing, shifting, acting on the PC, etc.
- **Solves.** NPCs behaving consistently with *their* established traits instead of the story's
  convenience.
- **Adaptation for us.** Each persistent NPC record carries 3 descriptors + a disposition value
  (see NP-03). When the DM is unsure what an NPC does, it rolls a disposition-modified NPC-action
  table rather than choosing. `[D]` + `[J]`.

### 2.2 Scene & session structure

#### P-07 Mythic lists: Threads & Characters (MY) → 11, 12
- **Mechanic.** Two lists: open **threads** (goals, quests, mysteries) and **characters**
  (NPCs/groups that matter). 2e lists have up to 25 lines (5 sections × 5). Random events that
  reference "a thread" or "an NPC" pick from the list by dice; an element can be entered up to 3
  times to raise its odds; an empty line means "choose the most fitting, or roll again". At the
  end of every scene, add new elements, remove resolved ones, and add a duplicate entry for any
  element that was highly relevant.
- **Solves.** Forgotten threads — the #1 failure of long solo campaigns and, per this project's
  long-horizon research, of LLM narrators.
- **Adaptation for us.** Maintain `threads` and `cast` as first-class state collections with a
  **weight** field (1–3). Random events and hook generation sample from them by weight. The
  end-of-scene bookkeeping step (P-09) updates weights. `[D]`.

#### P-08 Mythic thread progress track, discovery checks, flashpoints, keyed scenes, peril points (MY 2e) → 11, 12
- **Mechanic.** Optional track per major thread (10, 15, or 20 points) with **flashpoints**
  every 5 points — a dramatic event that must occur when a flashpoint is reached. When the PC
  investigates a thread, they may ask a **discovery** question ("is anything discovered?"); on a
  yes, a thread-discovery table grants progress points. **Keyed scenes** are author-defined
  triggers ("when the PC enters the capital…") that force a specified scene. **Peril points**
  (a small pool, ~2–3) let the player avoid one disastrous outcome each.
- **Solves.** Mysteries that never resolve (P16's soft-lock) and threads with no pacing.
- **Adaptation for us.** Each thread gets a length (short 10 / standard 15 / long 20) and
  flashpoints at 5-point marks. P17 discovery results award progress (crit 3, success 2, fail 1
  only if the fail still yielded a lead, crit-fail 0). **Flashpoints are the mechanical
  implementation of P16**: if the track reaches a flashpoint, the DM *must* stage a revelation
  or confrontation. Keyed scenes map to our starter-setting's authored triggers (13).
  Peril points map to RS-18 (meta-currency decision). `[D]`.

#### P-09 End-of-scene bookkeeping (MY) → 12
- **Mechanic.** After each scene: adjust Chaos ±1, update lists, note new facts.
- **Adaptation for us.** Formal `end_scene` procedure: (1) Tension ±1; (2) threads/cast add,
  remove, reweight; (3) tick any clock whose trigger fired; (4) commit tag_events; (5) confirm
  every narrated change has a matching state write (P13 reconciliation); (6) check P16 counter.
  This is the natural checkpoint for the continuity audit (DM-08). `[D]`.

#### P-10 Starforged session moves (ISF) → 12, 14
- **Mechanic.**
  - *Begin a Session*: review/adjust flagged content, recap, set the scene; optionally a short
    vignette spotlighting a danger, opportunity or insight (rollable); +1 momentum.
  - *Set a Flag*: mark a topic the player wants handled with care; when it comes up, pause and
    consider its role.
  - *Change Your Fate*: when content is flagged, an oracle answer is rejected, or a consequence
    is uncomfortable, choose one of five re-framings — **reframe** (shift perspective),
    **refocus** (move the spotlight), **replace** (swap an element), **redirect** (bring in
    help), **reshape** (alter the situation wholesale).
  - *Take a Break*: after a progress move or intense scene, reflect; continue with +1 on the next
    move, or end.
  - *End a Session*: review for missed progress, mark connection/quest development, note focus
    for next time, +1 momentum.
- **Solves.** Safety tools and session hygiene expressed as *rules of play* rather than table
  etiquette — ideal for an AI that must be told exactly when to do them.
- **Adaptation for us.** Adopt all five nearly verbatim in function: `begin_session` (recap from
  state, restate open threads, ask about flags), `set_flag` (writes to a content-preferences
  record, SC-01), `change_your_fate` (the out-of-character adjust tool, SC-02; the five
  re-framings are an excellent bounded menu), `take_a_break`, `end_session` (writes "next time"
  notes). Mark: SC-01/SC-02 `[D]` state + `[J]` application.

#### P-11 Mythic random events & event focus (MY) → 11, 12
- **Mechanic.** A random event is generated by (1) rolling its **focus** on d100, then (2) a
  meaning pair for content. 1e focus table: remote event 1–7, NPC action 8–28, new NPC 29–35,
  move toward a thread 36–45, move away from a thread 46–52, close a thread 53–55, PC negative
  56–67, PC positive 68–75, ambiguous 76–83, NPC negative 84–92, NPC positive 93–100. 2e
  reweights this, adds a **current context** result (the event stays within the current
  focus), and offers genre variants (horror, action, mystery, social, personal, epic).
- **Solves.** "Nothing happens unless the player acts."
- **Adaptation for us.** Author our own focus table (reweighted for a sandbox where factions
  matter: add *faction move* and *rumor arrives*; keep *close a thread* rare). Trigger events from
  (a) oracle doubles ≤ Tension, (b) interrupted scenes, (c) session start (P-10 vignette). `[D]`
  selection.

#### P-12 Blades session cycle: free play → engagement → score → downtime (BitD, SaV) → 12, 10
- **Mechanic.** Free play (roleplay, gather info, choose a target) → pick plan type + one detail
  → **engagement roll** (1d6 base, ±dice for plan detail, target tier, friends/enemies): crit
  = exceptional start, 6 = controlled position, 4–5 risky, 1–3 desperate — skipping the approach
  and cutting to the first moment of danger → the score (flashbacks allowed) → downtime (payoff,
  heat, entanglement, faction clocks, two activities each).
- **Solves.** A repeatable loop with a known shape, so neither the player nor GM wonders "what
  now?"; the engagement roll removes over-planning paralysis.
- **Adaptation for us.** Our sandbox loop: *free play* (town/downtime, threads chosen) → *venture
  start* (a single engagement-style roll that sets the opening position of an expedition,
  factoring preparation and intel) → *venture* (travel/site/conflict) → *return & reckoning*
  (P-18 heat, faction turn, downtime). The engagement roll is a strong antidote to a solo
  player's endless-planning failure mode. `[D]`.

#### P-13 Torchbearer phases: adventure / camp / town (/ winter) (TB) → 00, 10
- **Mechanic.** Adventure phase: each test consumes a **turn**; every 4th turn every character
  gains a condition in fixed order (hungry & thirsty → exhausted → angry → sick → injured →
  afraid → dead); torches last 2 turns, lanterns 3, candles 4. Camp phase: no turns pass,
  counters reset. Town phase: every activity adds to a **lifestyle cost** paid before the next
  adventure. Longer cycles roll into a winter phase.
- **Solves.** Time pressure without real-time; attrition that is fully deterministic.
- **Adaptation for us.** Adopt **time = resolved actions** inside sites (see §3): an exploration
  turn advances when the PC makes a check or takes a significant action, not on the wall clock.
  This is the single most AI-friendly time model surveyed.

### 2.3 Progress, pressure & pacing

#### P-14 Ironsworn vows & progress tracks (IS, ISF) → 11, 01, 04
- **Mechanic.** A **vow** is a player-declared goal with a rank: troublesome, dangerous,
  formidable, extreme, epic. Each gets a 10-box track (4 ticks per box). *Reach a Milestone*
  marks progress by rank: troublesome 3 boxes, dangerous 2, formidable 1, extreme 2 ticks, epic 1
  tick. *Fulfill Your Vow* is a **progress roll**: 2d10 challenge dice vs filled boxes (no action
  die, momentum ignored) — beat both: strong hit; beat one: weak hit (something is still
  undone); neither: miss (recommit at higher rank, or forsake). Rewards: IS XP 1/2/3/4/5 by rank
  (spent 3 per new asset, 2 per upgrade); ISF marks a quests legacy track (troublesome 1 tick →
  epic 3 boxes). *Swear an Iron Vow* rolls +heart for momentum. *Forsake Your Vow* costs (IS: −2
  momentum; ISF: stress, damaged relationships, lost assets, or enemies advance). The same
  track engine runs journeys, fights, bonds, expeditions.
- **Solves.** A sandbox's "what is this story about?" — the player tells the system, and the
  system tracks it. Progress rolls make even long goals carry uncertainty at the end.
- **Adaptation for us.** Our class-emergence engine needs a **goal layer** (AD-06, LW-13): player
  goals become threads with rank; milestones mark progress; completion is a crystallization
  moment for P2 tiers ("sworn and fulfilled" is precisely a Stormlight Ideal moment). The
  progress-roll idea (luck still matters at the finish) adapts to d20 as: d20 + filled boxes vs DC
  = 10 + rank×2, or keep IS's 2d10 vs boxes for world-scale tracks. `[D]`.

#### P-15 Ironsworn momentum (IS, ISF) → 01 (meta-currency decision)
- **Mechanic.** Momentum −6 to +10, starts/resets at +2. Gained from successes and certain
  choices; lost on setbacks. *Burn* momentum: if momentum exceeds a challenge die, cancel that
  die (turning misses into hits), then reset. Negative momentum equal to the action die cancels
  the action die. Each debility lowers max by 1 and reset (to +1 with one, 0 with two+).
- **Solves.** Converts a streak of setbacks-survived into a guaranteed success later — a
  player-controlled anti-frustration valve.
- **Adaptation for us.** Strong candidate for RS-18: a player-visible **Resolve**-like meter that
  accrues on hard-fought partial successes and can be spent to upgrade one degree of success.
  Because momentum reset is lowered by conditions, it also ties harm to agency without extra
  bookkeeping. `[D]`.

#### P-16 Pay the Price & complication menus (IS; DW GM moves) → 12, 01
- **Mechanic.** On a miss, apply the most obvious negative outcome, *or* roll d100 on a generic
  table (harm, stress, supply loss, a companion hurt, a new danger, time lost, a situation
  worsening, etc.), *or* ask the oracle. DW's GM moves split into **soft** (a threat
  telegraphed, reversible) and **hard** (consequence lands) and forbid saying the move's name.
- **Solves.** Consistent, varied consequences; prevents both mercy-bias and repetition.
- **Adaptation for us.** `data/complications.yaml`: a d100 menu of consequence types, each
  mapped to a state write (update_resource, set_fact, clock tick). Rule: on a failure without an
  obvious consequence, roll; never pick the same type twice in a row. The soft/hard split is
  precisely our telegraphed-lethality lock: lethal outcomes may only follow a prior soft move
  that warned of them. `[D]` roll, `[J]` fit.

#### P-17 Blades progress clocks (BitD) → 11, 01
- **Mechanic.** Circles of 4 (complex), 6 (complicated) or 8 (daunting) segments. Types:
  **danger** clocks (fill on consequences, 1–3 segments by severity), **racing** clocks (two
  clocks, first to fill wins), **linked** clocks (one unlocks another), **mission/countdown**
  clocks (a deadline), **tug-of-war** clocks (fill and empty), **long-term project** clocks
  (8+ segments, filled by downtime rolls: 1–3 → 1 tick, 4–5 → 2, 6 → 3, crit → 5), **faction**
  clocks (advanced by the GM in downtime).
- **Solves.** Makes threats and long efforts visible, discrete, and cumulative.
- **Adaptation for us.** Clocks are hidden state (tone lock) but **each segment must be paired
  with an observable sign** — this is DW's "grim portent" idea (P-19) applied at segment level.
  Rule: whenever a hidden clock ticks, the DM narrates its authored portent at the next
  plausible opportunity (a rumor, a sign in the environment, an NPC's changed behavior). That
  satisfies both hidden mechanics and "telegraphed". `[D]` ticks, `[J]` portent placement.

#### P-18 Blades heat, wanted level, entanglements (BitD) → 11
- **Mechanic.** After a score, heat by exposure: 0 (smooth & quiet), 2 (contained), 4 (loud),
  6 (wild), +1 high-profile target, +1 hostile turf, +1 at war, +2 if killing was involved. Heat
  fills a 9-box track; filling it raises **wanted level** (max 4) and resets heat. Then roll
  **entanglement** dice equal to wanted level (0 → roll 2, take lowest) on a table keyed by
  current heat band (0–3, 4–5, 6+): results range from gang trouble and questioning to
  reprisals, show of force, demonic notice, and arrest.
- **Solves.** Consequence propagation that is automatic, proportional and escalating.
- **Adaptation for us.** Generalize "heat" to **Notice** per faction or authority (LW-14): each
  venture adds notice by how loud it was; thresholds escalate the response tier. The entanglement
  table becomes a per-region "the world responds" table. `[D]`.

#### P-19 Dungeon World fronts: dangers, impulses, grim portents, impending doom, stakes (DW) → 11
- **Mechanic.** A front groups 2–3 related **dangers**; each danger has an **impulse** (what it
  wants), 1–3 (adventure front) or 3–5 (campaign front) **grim portents** (the steps it will take
  if unopposed, written as if the PCs didn't exist) and an **impending doom** (the irrevocable
  bad end). **Stakes questions** name what the GM genuinely wants to find out in play. When a
  portent "comes to pass", mark it; the GM advances fronts when players ignore them or on
  failures.
- **Solves.** The world has intentions independent of the player, prepared as situations.
- **Adaptation for us.** Our `threats` in 11 should be front-shaped: impulse + ordered portents
  + doom + stakes. Portents double as the observable signs for P-17. The DM's between-session
  procedure asks of each front: "did the player oppose this since its last portent?" — if not,
  advance.

#### P-20 Ironsworn: Delve threats & menace (ISD) → 11
- **Mechanic.** A threat is attached to a vow and has a category (e.g. ravaging horde, scheming
  leader, zealous cult, malignant plague, cursed site, rampaging creature), a goal, and a 10-box
  **menace** track. Menace is marked when the player gives ground (outcomes of misses, milestones
  on the linked vow that leave the threat unchecked, time passing); if menace fills, the threat
  achieves its goal and the linked vow cannot be fulfilled as sworn.
- **Solves.** Couples the villain's clock to the player's quest progress — a race.
- **Adaptation for us.** Every thread (P-14) may have an opposing threat; implement as a
  **racing clock** pair (P-17): the player's thread track vs the threat's menace.

#### P-21 Starforged scene challenge (ISF) → 10, 06
- **Mechanic.** For an extended non-combat challenge: set rank formidable, name the objective,
  create a progress track and a **tension clock** of 4 (severely disadvantaged), 6 (even), or 8
  (strong advantage) segments. Face Danger: strong hit marks progress (match: twice); weak hit
  marks progress and fills 1 segment; miss fills 1 (match: 2) and Pay the Price. Secure an
  Advantage builds momentum or bonuses, and fills segments on a miss. When either the track or
  the clock fills, roll **Finish the Scene** (progress roll).
- **Solves.** A single generic engine for chases, debates, heists, rituals, storms.
- **Adaptation for us.** This is the best candidate for our generic **extended task** rule
  (RS-09) and CF-09/CF-17/CF-18: one engine (progress track vs tension clock) with named skins
  for chase, infiltration, negotiation, ritual — mirrors PF2's victory-point subsystems, but
  with a built-in opposing clock. Strong analogical anchor for novel actions (P3).

### 2.4 Living-world engines

#### P-22 Blades faction ladder: tier, hold, status (BitD) → 11
- **Mechanic.** Every faction has **tier** (0–V; scale and quality of its resources) and
  **hold** (weak/strong; how securely it keeps that tier). Each faction's **status** with the
  crew runs −3 (war) to +3 (allies): +3 helps even at cost to itself; +2 helps if no serious
  cost; +1 helps if cheap; 0 neutral; −1 makes trouble if cheap; −2 harms if no serious cost; −3
  harms even at cost. Scores against a faction usually move status −1 or −2; helping moves +1;
  hidden jobs don't move it. At war (any −3): +1 heat per score, −1 hold, one downtime
  activity instead of two. Hitting a faction's vulnerability costs it 1 hold; losing weak hold
  drops a tier. Each faction has long-term-goal clocks; in downtime the GM ticks the ones that
  are relevant (for uncertain progress, a fortune roll using the faction's tier).
- **Solves.** A compact, legible relationship model the GM can run for dozens of factions.
- **Adaptation for us.** Adopt status −3..+3 per faction verbatim in shape (it's already an
  enumerated behavior table — perfect for `[D]` lookups). Keep tier as the faction's power band,
  aligned with 09's threat bands. Faction goals are clocks ticked in the faction turn (P-23).

#### P-23 SWN/WWN faction turn (SWN, WWN) → 11
- **Mechanic.** Factions have Force, Cunning and Wealth ratings (WWN adds a Magic rating), hit
  points, **assets** (each tied to one rating, with attack/counterattack dice and upkeep), tags,
  a current **goal**, and experience. Each faction turn, in order: earn income (SWN: half
  Wealth + a quarter of Force+Cunning, rounded down), pay upkeep, optionally change goal
  (forfeiting that turn's income if the old goal wasn't met), then take **one action** (attack,
  buy/create an asset, move/repair/hide/sell assets, expand influence, seize territory, use an
  asset ability). Attacks are contested rolls (d10 + attribute vs d10 + attribute) between
  assets. Completing a goal grants faction XP that buys rating increases. WWN runs faction turns
  on a roughly monthly cadence and ties PCs' **major projects** (P-24) into the same world.
- **Solves.** A living world that changes on a schedule whether or not the PCs are present.
- **Adaptation for us.** The richest model; our 11 should use a trimmed version: 3 ratings
  (Might, Cunning, Wealth; plus Arcane where relevant), a goal clock, 2–6 assets, one action per
  turn, **turn cadence = each downtime or each 7 in-world days, whichever first** (so the world
  never freezes during a long expedition). Results write to state and seed rumors (SO-06).
  Deterministic tool: `run_faction_turn(faction_id)`. `[D]` + `[J]` narration.

#### P-24 WWN major projects (WWN) → 11
- **Mechanic.** When PCs want to change the world beyond what a single adventure accomplishes
  (found a town, reform a guild, end a feud), the GM rates the project's difficulty on a ladder
  and scales it by scope (from a village up to a kingdom); PCs pay the cost in **Renown** earned
  through adventuring (money can buy some); specific obstacles can instead be removed by
  adventures, each cutting the difficulty. (Exact values per the WWN free edition, ch. "Factions
  and Major Projects".)
- **Solves.** Gives an open sandbox a *player-driven* endgame and turns reputation into agency.
- **Adaptation for us.** LW-09: player world-change = a long-term project clock whose size comes
  from difficulty × scope, paid down by (a) downtime rolls, (b) spending reputation (AD-07), (c)
  adventures that clear named obstacles (each obstacle = a thread). This also gives retirement
  (LW-11) something to *leave behind*.

#### P-25 Mausritter end-of-session faction roll (MR) → 11
- **Mechanic.** Each faction lists resources and goals, each goal with a few progress steps. At
  the end of each session roll d6 per faction for its active goal: +1 per relevant resource, −1
  per opposing faction's relevant resource; 4–5 marks 1 progress, 6 marks 2. Completing a goal
  changes the world and may add a resource.
- **Solves.** The cheapest possible faction engine that still produces change.
- **Adaptation for us.** Use this as the **minor-faction** engine (villages, gangs, cults) while
  P-23 runs major factions — two tiers keep cost proportional.

#### P-26 TOR Eye Awareness (TOR) → 11
- **Mechanic.** A hidden company score rises from specific triggers (displays of power, magic
  use, rolling the Eye rune on the feat die in dark lands). When it reaches the region's **Hunt
  threshold**, a Revelation episode occurs (the enemy acts on the PCs), then the score resets. In
  Strider Mode it resets after every fellowship phase.
- **Solves.** A world that notices you, proportionally to how loudly you act.
- **Adaptation for us.** LW-14 Notice, per region/faction, hidden, with authored thresholds and
  response tables (merges with P-18).

#### P-27 Starforged connections & Ironsworn bonds (IS, ISF) → 10, 02
- **Mechanic.** *Make a Connection* (roll +heart) creates an NPC with a **role** and **rank**;
  a connection aids the PC (+1 and momentum) on moves tied to its role. *Develop Your
  Relationship* marks progress on the connection's track by rank; *Test Your Relationship*
  handles strain (miss: sever, or swear a vow to repair); *Forge a Bond* is a progress roll that
  converts a connection into a bond (bonds legacy track; greater aid or a second role).
- **Solves.** NPC relationships with mechanical weight and an arc.
- **Adaptation for us.** NP-03: relationship = rank + progress track + role(s) that license
  assistance (a Principle VII license source: "the smith is your bond, so you can commission
  masterwork"). Bond formation is tag evidence for social callings. `[D]`.

### 2.5 Exploration, sites & travel

#### P-28 Delve: site = theme × domain + area progress (ISD) → 10, 11, data
- **Mechanic.** *Discover a Site*: choose a **theme** (condition — e.g. ancient, corrupted,
  fortified, hallowed, haunted, infested, ravaged, wild) and a **domain** (physical type — e.g.
  barrow, cavern, frozen cavern, icereach, mine, pass, ruin, sea cave, shadowfen, stronghold,
  tanglewood, underkeep), set a rank (troublesome 3 progress per area … epic 1 tick per area).
  Returning to a partly explored site: roll both challenge dice and clear progress boxes equal to
  the lower. *Delve the Depths* per area: roll +edge (haste), +shadow (stealth/trickery) or +wits
  (observation/expertise). Strong hit: mark progress and Find an Opportunity. Weak hit: d100 on a
  stat-specific column — e.g. for wits, 1–40 mark progress + Reveal a Danger, 41–55 mark
  progress, 56–80 choose progress or opportunity, 81–99 both, 00 mark progress twice + danger
  (edge and shadow columns have different band widths, encoding the approach's risk profile).
  Miss: Reveal a Danger. *Reveal a Danger* d100: 1–30 theme card danger, 31–45 domain card
  danger, 46+ general dangers (hostile denizen, hazard, complicating discovery, harrowing
  sensation, consequence of an earlier choice, blocked/trapped way, resource lost, lost way,
  mystery/tough choice, roll twice). *Find an Opportunity* d100 (terrain favors you, history
  revealed, secure area, clue, get the drop on a denizen, forage, useful object, warned of
  threat, helpful or needy denizen) then take +1 momentum or act on it at +1. *Locate Your
  Objective*: progress roll ends the delve; miss clears all but one box and raises rank.
  *Escape the Depths*: a separate move to flee. **Denizen matrix** d100: very common 01–27,
  common 28–41/42–55/56–69, uncommon 70–75/76–81/82–87/88–93, rare 94–95/96–97/98–99,
  unforeseen 00.
- **Solves.** A complete no-map dungeon crawl; content is generated per area from two small
  cards, so infinite sites come from ~20 short tables (a Principle V closed-combinatorics win).
- **Adaptation for us.** This is the strongest fit anywhere in the survey for **EX-08** in a
  text-only game: areas as abstract progress, approach choice changes the risk table, theme ×
  domain gates content (and — critically — gates the **loot/adversary pools** of P5: the site's
  theme is the pool-gate for what's found there). Recommend 10 adopt the shape and 11 own the
  theme/domain tables. Use our d20 check for the per-area roll and the Delve-style
  approach-specific outcome columns. `[D]`.

#### P-29 Starforged expeditions & discoveries (ISF) → 10
- **Mechanic.** *Undertake an Expedition* per segment: roll +edge (speed), +shadow (stealth) or
  +wits (vigilance); strong hit marks progress; weak hit marks progress at a cost or a waypoint
  peril; miss: no progress, crisis. *Explore a Waypoint* (+wits): opportunity (+2 momentum) or
  mark progress; weak hit finds something interesting tied to danger; miss: threat. *Make a
  Discovery* (d100 of wonders) marks 2 ticks on the discoveries legacy track; *Confront Chaos*
  (1–3 aspects of something dreadful) marks a tick per aspect. *Finish an Expedition* is a
  progress roll with legacy rewards by rank.
- **Adaptation for us.** Exploration of the *wild* (as opposed to sites) gets its own reward
  channel: discoveries feed an **explorer** tag family (03) and rumors/landmarks (11). Validates
  that exploration can be advancement evidence equal to combat (AD-09).

#### P-30 Ironsworn journeys & supply (IS) → 10
- **Mechanic.** *Undertake a Journey*: set rank; each waypoint roll +wits; strong hit: mark
  progress and choose (spend supply for +1 momentum, or conserve); weak hit: mark progress and
  −1 supply; miss: a hazard or threat, no progress. *Reach Your Destination* is a progress roll.
  Supply is a shared 0–5 abstraction for food, water, ammunition and small gear; at 0 the
  *unprepared* condition. *Make Camp* (+supply) restores health/spirit/momentum options.
- **Adaptation for us.** Supply as an abstract track (EQ-09) avoids ration bookkeeping while
  keeping scarcity; an AI tracks a 0–5 integer far more reliably than itemized rations.
  Recommend: abstract supply for travel, itemized goods for everything else.

#### P-31 Forbidden Lands quarter days & activities (FBL) → 10, 00
- **Mechanic.** A day = 4 quarter days (morning, day, evening, night). Each quarter, each
  character does one activity: hike, lead the way, keep watch, forage, hunt, fish, make camp,
  rest, sleep, explore. Leading the way rolls against getting lost/mishaps per hex; forage, hunt
  and fish have their own mishap tables; one camp maker covers the party; sleep needed within the
  day or become sleepy; hiking at night is harder.
- **Adaptation for us.** Adopt the **watch = quarter day** unit (§3) with one activity per
  watch; a solo PC choosing between hunting, watching, and resting *is* the survival tension.
  Companions (NP-05) take the other roles — another reason companions are essential in solo.

#### P-32 The One Ring journeys, fatigue & fellowship phase (TOR) → 10, 11
- **Mechanic.** Journey length = hexes on the route +1 day per hard-terrain hex (halved
  mounted). Roles: Guide (route, rolls marching tests), Hunter, Look-out, Scout. The Guide's
  marching test sets where the next **event** occurs (success: 3+ hexes ahead; failure: 2 in
  spring/summer, 1 in autumn/winter); each event targets a role and tests its skill; outcomes
  add **fatigue** to everyone. On arrival, mounts subtract their vigour and a travel test can
  shed more; remaining fatigue burdens the character. Between adventures a **fellowship
  phase** (a week to a season) gives one undertaking each (plus Yule's annual extras: raise an
  heir, heal scars, recount a story, etc.).
- **Adaptation for us.** (1) Travel produces *events at a pace set by a skill roll* rather than
  per-day random checks — this halves pointless encounters (see Rancourt's density comparison:
  TOR is the lowest-density, most narratively integrated). (2) Fatigue as a journey cost that
  converts to a condition at arrival. (3) The fellowship phase + annual Yule is the model for
  TM-08.

#### P-33 PF2 hexploration (PF2) → 10
- **Mechanic.** Days measured in **hexploration activities** by speed (≤10 ft: ½; 15–25: 1;
  30–40: 2; 45–55: 3; 60+: 4). Group activities: Travel (open 1, difficult 2, greater difficult 3
  activities per hex; roads one step better), Reconnoiter (find hex features). Individual
  activities: Fortify Camp, Map the Area (lowers navigation DC by 2), Subsist. Random encounters:
  one flat check per day vs terrain DC (plains 12, forest/swamp 14, mountain 16,
  aquatic/arctic/desert 17; −2 on roads/rivers, +3 flying); success = 1 encounter, critical = 2.
- **Adaptation for us.** The **flat-check-by-terrain** encounter rule is clean and `[D]`; we can
  use DC-based terrain danger with our d20 (e.g. d20 ≥ region danger DC ⇒ encounter).

#### P-34 Shadowdark crawling rounds & danger level (SD) → 10
- **Mechanic.** In dangerous sites, time moves in crawling rounds; encounter check 1-in-6 every 3
  rounds (unsafe), every 2 (risky), every round (deadly); losing all light makes the site
  deadly. Light lasts 1 real hour.
- **Adaptation for us.** Adopt **danger level → check cadence** (hidden per-area attribute);
  replace real-time light with an action-count budget (§3).

#### P-35 Four Against Darkness escalation to a final boss (4AD) → 10, 11
- **Mechanic.** Rooms/corridors from d66 layout tables; contents 2d6 (treasure, trap, special
  feature/event, vermin, minions, weird monster, boss, small dragon lair). On a boss result, roll
  d6 + number of bosses/weird monsters met so far: 6+ (or dungeon fully laid out) means this is
  the **final boss**. XP for bosses, quests, or 10 minion encounters survived.
- **Adaptation for us.** Climax probability that **rises with elapsed challenge** — use for
  site objectives: Locate-Objective difficulty falls (or its chance rises) with each danger
  already overcome, guaranteeing sites end. Complements P16.

#### P-36 Kal-Arath / OSR travel loop (KA, CRN, MR) → 10
- **Mechanic.** Per day (KA): weather → lost? → forage? → point of interest? → encounter? →
  resolve; consume rations at day's end. CRN 2e: 3 watches/day, 1-in-6 encounter per watch,
  weather d6/day (1–3 no effect, 4–6 escalating penalties); deprivation >1 day adds a Fatigue
  that fills an inventory slot. MR: 4 watches/day; the d6 encounter die yields an **omen** (a
  sign of the encounter) on a near miss.
- **Adaptation for us.** The **omen** result is the hidden-mechanics gem: a near-miss on the
  encounter check produces a *sign* (tracks, smoke, distant howling) — the world telegraphs
  before it strikes, matching our lethality lock. Recommend 10's encounter check: 1 = encounter,
  2 = omen of the next encounter (on a d6 or its d20 equivalent).

### 2.6 Generation

#### P-37 Blades starting situation (BitD) → 13
- **Mechanic.** Open with two factions already at odds, each eager to recruit and to punish help
  given to the other; a third faction positioned to profit or be ruined; first scene at one
  faction's headquarters with an offer on the table.
- **Adaptation for us.** Template for 13's opening situation: triangle of interests + an offer
  that forces a choice in scene 1. Works just as well solo.

#### P-38 SWN/WWN tags (SWN, WWN) → 11, data
- **Mechanic.** Places and factions get 1–2 **tags**, each a paragraph plus short lists: Enemies,
  Friends, Complications, Things, Places. Combining two tags gives an instantly playable locale.
- **Adaptation for us.** Every region/settlement/site in `data/` carries tags with those five
  lists; the DM rolls or picks from the lists when improvising (P3 substrate). Closed
  combinatorics again (tag pairs).

#### P-39 Beyond the Wall playbooks & scenario packs (BtW) → 02, 11, 13
- **Mechanic.** Character playbooks are roll tables that simultaneously build the character, its
  relationships, and the home village (each step adds an NPC or location to the shared map).
  Scenario packs generate a one-night adventure (villain, locations, secrets) from tables with
  hooks keyed to the characters just made.
- **Adaptation for us.** Character creation (02) should *write the world* (13): each background
  step adds an NPC to the cast list and a fact to the region. Our adventure generator (11) should
  key hooks to the PC's drives (CC-08) and bonds (CC-10).

#### P-40 Ironsworn "Your Truths" & inciting incident (IS, ISF) → 13, 02
- **Mechanic.** For each setting pillar (the old world, iron, legacies, communities, leaders,
  defense, mysticism, religion, firstborn, beasts, horrors), pick or roll one of three truths,
  each with a quest starter. Start play with **two vows**: a long-term background vow
  (extreme/epic) and an inciting-incident vow (immediate).
- **Adaptation for us.** 13 should present a short set of player-selectable truths (e.g. 6
  pillars × 3 options) that toggle regional facts and seed threads — giving the newcomer
  meaningful choices without lore reading. Two-vow start is the fix for CC-09.

#### P-41 Alexandrian node-based design, Three Clue Rule, "situations not plots"; Gumshoe core clues → 10, 12
- **Mechanic.** For any conclusion the player must reach, provide at least three clues; conversely
  any three clues yield at least one conclusion. Structure adventures as nodes connected by
  leads. Prep situations (actors, goals, resources) not sequences. Gumshoe: clues required to
  progress are *never* gated behind a failable roll — rolls decide extra benefit, not access.
- **Adaptation for us.** Pair with P17: core leads are guaranteed; degree of success governs
  *extra* information and cost. This is how P16 and P17 coexist without soft-locks: a thread's
  next node is always reachable by ≥3 routes. Put the rule in 10 (investigation) and the
  audit in 12 (the DM checks each open thread has ≥1 live lead; if not, P16 fires).

### 2.7 Memory, legacy & long time

#### P-42 Thousand Year Old Vampire memories (TYOV) → 12, 00
- **Mechanic.** The vampire holds at most 5 memories of up to 3 experiences each; new
  experiences displace old memories; up to 4 memories can be moved into a diary (lost if the
  diary is lost). Prompts are traversed by d10 − d6.
- **Adaptation for us.** Not a player mechanic — a design analogy for **state summarization**:
  a bounded "active memory" of the most salient facts per NPC/thread, with overflow archived to
  a queryable store (the diary), is exactly the long-horizon pattern the project's research
  recommends. Worth naming in 00's state model: *active* vs *archived* facts, with explicit
  promotion/demotion rules at session end.

#### P-43 Legacy tracks, Continue a Legacy, Write Your Epilogue (ISF, IS) → 11
- **Mechanic.** ISF: three legacy tracks (quests, bonds, discoveries); each filled box = 2 XP
  (after the 10th box the track clears and further boxes give 1 XP). On retirement or death,
  *Continue a Legacy*: a new character rolls challenge dice against *each* of the predecessor's
  three legacy tracks — strong hit inherits a path/companion, a connection, or the ship; weak hit
  completes an unfinished vow, rebuilds a connection, or revisits a meaningful place; miss: a
  former foe rises, the new character opposes the predecessor, or old discoveries bite back. IS:
  *Write Your Epilogue* rolls against the bonds track to determine the retired character's
  ending.
- **Adaptation for us.** LW-11/HR-11 template: retirement = progress rolls against the
  character's *recorded history* (threads completed, bonds, discoveries, world changes) to
  determine (a) the epilogue's tenor and (b) what a successor inherits. Our tag tallies are a
  natural "legacy track" source — nothing new to track.

#### P-44 Pendragon Winter Phase; Ars Magica seasons & aging; TOR Yule (PD, AM, TOR) → 11
- **Mechanic.** PD, once per in-game year: experience checks on skills used, training, family
  events table (births, deaths, marriages, heirs), horse survival (d20: 1–2 lose the horse),
  economic circumstances, aging, glory totals (every 1,000 glory → an improvement). AM: time is
  budgeted in **seasons** (3 months), each spent on one activity (study, lab work, adventure);
  aging rolls every winter from age 35 (stress die + age/10 − living conditions − longevity
  ritual). TOR: an annual Yule fellowship with extra undertakings.
- **Adaptation for us.** TM-08: a **season turn** every 3 in-game months: major faction turns,
  season change (weather tables, travel modifiers), property upkeep (EQ-12), one seasonal
  downtime project each, relationship drift, rumors refresh, and (if long campaigns) aging. It is
  also the natural **consolidation boundary** constitution VI asks for ("bundle retirement into
  infrequent, clearly telegraphed boundary points") — provisional content can be confirmed or
  retired at season turns.

#### P-45 Blades downtime activities (BitD) → 10
- **Mechanic.** Two activities per PC per downtime (extra ones cost 1 coin or 1 rep; one fewer
  at war): **acquire asset** (roll crew tier; result sets quality: crit tier+2, 6 tier+1, 4–5
  tier, 1–3 tier−1; +1 quality per 2 coin), **long-term project** (ticks 1/2/3/5), **recover**
  (tick a healing clock), **reduce heat** (clear 1/2/3/5), **train** (mark XP), **indulge vice**
  (roll dice = lowest attribute, clear stress = highest die; clearing more than you had =
  overindulgence: trouble, brag +2 heat, lost, or tapped supplier).
- **Adaptation for us.** TM-06 menu with the same *roll → ticks* ladder (1/2/3/5) for every
  project-like activity; our d20 degrees map cleanly (crit-fail 0 or setback, fail 1, success
  2–3, crit 5).

#### P-46 Burning Wheel Beliefs & "Let it ride" (BW) → 02, 01
- **Mechanic.** Players write Beliefs (goal-laden convictions) that tell the GM what to
  challenge; acting on/against them earns rewards. "Let it ride": one roll settles a question
  until circumstances materially change; no re-rolling the same intent.
- **Adaptation for us.** CC-08 (drives as authored hooks, feeding threads) and RS-11 (retry rule).

---

## 3. Time-scale structure

### 3.1 What the surveyed games do

| Scale | Typical length | Games & unit | What "ticks" at this scale |
|---|---|---|---|
| **Action** | seconds | PF2 action (3/turn); 5.2 action/bonus/reaction | action budget, reactions |
| **Round / exchange** | ~6 s | 5.2, PF2 rounds; IS combat is fiction-paced exchanges gated by initiative; SD crawling round in sites | ongoing damage, condition durations, Focus-type spends |
| **Exploration turn** | ~10 min, or *one resolved action* | OSE/MR 10-minute turn; **TB turn = one test**; SD crawling rounds | light, encounter checks (every 2–3 turns), the Grind (every 4th turn → condition) |
| **Scene** | variable | MY scene; ISF scene challenge; BitD score beats | Chaos/Tension ±1, list bookkeeping, scene test for the next scene |
| **Watch / quarter-day** | 4–8 h | FBL 4 quarters; MR 4 watches; CRN 3 watches; Alexandrian hexcrawl watches | one travel/camp activity each; encounter check; sleep need |
| **Day** | 24 h | 5.2 travel pace/day; PF2 hexploration activities/day; KA daily loop; TOR marching | rations/supply, weather roll, long rest, daily-recharge abilities |
| **Journey / expedition / venture** | days–weeks | IS journeys (waypoints), ISF expeditions, TOR journeys (events by marching test), BitD score | progress track; fatigue on arrival; heat after |
| **Session** | real-world sitting | ISF Begin/End a Session; BitD end-of-session XP; MR faction rolls; KA 30–45 min | recap, flags, XP/evidence review, minor faction rolls |
| **Downtime interval** | days–weeks | BitD downtime (2 activities); PF2 downtime days; TOR fellowship (week–season) | payoff, heat, entanglements, projects, recovery, faction clocks |
| **Season** | 3 months | AM seasons; TOR seasons affect travel; FBL | one seasonal project; weather regime; major faction turns |
| **Year** | 12 months | PD Winter Phase; TOR Yule; AM winter aging | aging, family, annual events, big consolidation |
| **Generation / legacy** | decades | PD heirs; ISF Continue a Legacy; IS Write Your Epilogue | inheritance, epilogue |

### 3.2 Findings

1. **Every scale owns a resource that ticks at its boundary** — rounds consume Vitality/Focus,
   turns consume light and trigger encounter checks, watches consume rest, days consume supply,
   downtime consumes money and time, seasons consume years. A game feels complete across scales
   when *each* scale has at least one meaningful clock; it feels hollow at any scale that has
   none (5.2's notorious "nothing happens during travel" problem).
2. **Transitions are triggered by explicit events.** PF2: encounter mode begins when initiative is
   rolled; exploration resumes when the encounter ends; downtime begins when the party is safe
   and chooses to pass time. BitD: the engagement roll is the *only* transition into a score;
   downtime begins when the score ends. Clean triggers prevent the AI from drifting between
   modes (e.g. letting combat-round precision leak into travel).
3. **Deterministic time beats real time for an AI.** SD's real-time torch is great at a physical
   table and meaningless in an async text chat. TB's "a turn passes when you make a test" is
   perfectly deterministic: the engine counts resolved checks. Recommend this for sites.
4. **Time compression is a procedure, not a narration choice.** ISF's Take a Break, BitD
   downtime and TOR fellowship phases make skipping time *a move with consequences* (clocks
   advance, factions act). An AI that skips time must run the tick table for every boundary it
   skipped — otherwise the world freezes when the PC isn't looking.
5. **Solo play shortens sessions** (KA recommends 30–45 minutes; many solo players play in short
   bursts). Session-scale procedures must be cheap and must survive arbitrary stops: a
   player may close the chat mid-scene. Therefore session-scale bookkeeping should also run at
   scene ends (MY does exactly this).
6. **Two-phase rhythm (adventure ↔ recovery) is universal**; three-phase (adventure / camp /
   town, TB) or four-phase (+ season/winter, PD/AM/TB) exists in every game with a sandbox
   long game. Our open-ended sandbox needs the four-phase version or the long game has no shape.

### 3.3 Recommended canonical time ladder for `00-architecture.md` (proposal)

| Unit | Definition | Converts to | Boundary ticks (registered by owning chapter) |
|---|---|---|---|
| Action | one declared action (P9 budget) | 3 actions + 1 reaction = 1 round | 06 |
| Round | ~6 s of conflict | 10 rounds ≈ 1 minute | conditions, ongoing effects, per-round recharges (05, 06) |
| **Turn** | one resolved non-combat check or significant action in a site; ≈10 min | 6 turns ≈ 1 hour; 1 conflict = 1 turn | light budget, danger-level encounter check (10), afflictions onset (07) |
| Scene | a continuous situation with one focus | — | Tension ±1, thread/cast bookkeeping, scene test, reconciliation (12) |
| **Watch** | 6 h; 4 per day (morning, afternoon, evening, night) | 1 watch of travel = 1 travel activity | one activity per watch, encounter/omen check, sleep need (10) |
| Day | 4 watches | — | supply −1 while travelling, weather, long rest, per-day recharges (05, 07, 10) |
| Venture | leaving safety → returning | — | reckoning: notice/heat, rewards, threads (11) |
| Downtime block | 7 days in safety | — | 2 downtime activities, recovery clock, **minor faction rolls**, **major faction turn** (10, 11) |
| Season | 13 weeks | 4 seasons = 1 year | season turn: weather regime, seasonal project, **consolidation boundary (VI)**, property upkeep (11, 04) |
| Year | 4 seasons | — | aging (optional), annual events, legacy review (11) |

The **tick table** (TM-02) is the contract: each chapter registers "at boundary X, do Y" rows, and
the DM's `advance_time(unit, n)` tool runs every registered row for every boundary crossed.
Skipping 3 weeks = 3 downtime blocks = 3 faction turns, deterministically.

---

## 4. Onboarding findings

The first playtester is a newcomer. What the best games do:

1. **Play before (most of) the rules.** The PF2 Beginner Box includes a choose-your-own-path
   solo adventure that teaches exploration, combat and rewards by doing them one at a time;
   reviewers single this out as the easiest on-ramp. D&D starter sets and the TOR starter set
   use pregenerated characters so session 1 starts in minutes. → *Our AI DM can do this
   better than any book*: the first session can be a **teaching arc** that introduces one
   subsystem per scene (talk → observe/investigate → a check with a degree → a minor fight →
   a rest → a choice with a faction consequence), each time explaining the rule *out of
   character* in one line the first time it fires, then never again unless asked.
2. **Character creation is world creation** (DW "ask questions and use the answers", "draw maps,
   leave blanks"; BtW playbooks write the village; IS Truths). For a newcomer this converts lore
   dumps into questions they can answer ("Who taught you to fight? What did they ask of you in
   return?") and gives the DM hooks for free.
3. **Start in motion with two goals.** IS: begin with a long-term background vow and an
   immediate inciting incident. DW: start "at the entrance to the dungeon" or "being sentenced
   before the king". BitD: the first session is creation then straight into a score, inside a
   pre-built faction conflict. → 13's opening should put the PC in a situation demanding action
   within the first message, with a long-term drive already recorded.
4. **Teach the stance, not just the rules.** IS and DW spend pages on *how to play*: be a fan of
   your character, lean into consequences, ask questions. For our game the key stance messages
   for a newcomer are: (a) describe what you want to do in plain words — no menu; (b) the DM will
   tell you when something is impossible and what you could do instead (VII's redirect); (c)
   failure moves the story; (d) you can always ask "what do I know?" or "what are my options?"
   out of character; (e) death is always warned about first.
5. **Progressive disclosure.** BitD and PbtA explicitly teach rules "as they come up". Our P7
   codex supports this: the codex is opt-in, and the DM's first-use explanations are logged so
   they aren't repeated.
6. **Fast character creation path.** Cypher's one-sentence character ("I am an adjective noun
   who verbs"), 13th Age's One Unique Thing, and pregens all exist because full creation is a
   barrier. Recommend 02 offer a **5-question fast path** (origin, what you're good at, what you
   want, who you love, what you fear) that the DM maps onto the full procedure, with the
   remaining choices deferred until they first matter (P1's deferral spirit).
7. **Safety & expectations up front, briefly** (2024 DMG session zero; ISF Begin a Session / Set a
   Flag). For a solo newcomer this is a 60-second exchange: tone check, "anything you don't want
   to see?", how to pause or change course (P-10), and the lethality promise.
8. **Examples everywhere.** IS and ISF run a continuous example character through the whole book;
   every rule chapter has a short example. BRIEF already mandates worked examples; add one
   *continuous* example character across chapters so examples compound.

---

## 5. Recommendations

### 5.1 Gaps in the chapter map (UNOWNED / unassigned, consolidated)

| # | Gap (checklist IDs) | Proposed owner | Why it matters |
|---|---|---|---|
| G-1 | **Canonical time ladder + tick table** (TM-01, TM-02, TM-11) | 00 | Without it every chapter invents its own time; skipping time freezes the world |
| G-2 | **Oracle / likelihood ladder / meaning tables / Tension dial** (RS-14, RS-15) | 12 + `data/oracles.yaml` | The AI's own uncertainty needs dice or its generosity/cliché bias decides |
| G-3 | **Companions, hirelings, followers** (NP-05, CF-13, EQ-11, CC-14) | new section: 09 (stat templates), 10 (hiring/loyalty), 12 (play) — or a new `15-companions.md` | Solo play's main social & tactical texture; also enables Help rules and journey roles |
| G-4 | **Thread / quest register & goal rewards** (LW-13, AD-06, CC-09) | 11 (register, tracks, flashpoints) + 04 (completion as crystallization) | No-XP design needs another answer to "what did finishing that earn?"; P16 enforcement |
| G-5 | **Reputation / renown / titles** (AD-07) | 11 (with 04 feeding) | The in-fiction voice of hidden progression (tone lock) and currency for world change |
| G-6 | **Session zero, content flags, in-play adjust** (SC-01..04, SC-06) | 14 (player side) + 12 (DM obligations) + 13 (first-session script) | Required by every modern core book; cheap; protects the newcomer |
| G-7 | **First-session teaching arc + fast creation/pregens** (OB-02, CC-12) | 13 + 02/14 | First playtester is a newcomer |
| G-8 | **Afflictions (poison, disease, curse) + mental harm** (HR-06, HR-08) | 07 | Classic fantasy staples; a staged-affliction template is a superb analogical anchor |
| G-9 | **Calendar, seasons, season turn** (TM-07, TM-08, HR-10, EX-04) | 11 (engine) + 13 (content) | Sandbox long-game rhythm; VI consolidation boundary |
| G-10 | **Holdings, bases, major projects, domain** (EQ-12, LW-09, LW-10) | 11 | Player-driven endgame in an endless sandbox; gives legacy something to leave |
| G-11 | **Site/dungeon crawl procedure** (EX-08, AV-08 traps) | 10 (name it) | Map says "travel, hazards, investigation" — the dungeon is missing by name |
| G-12 | **NPC generation, reaction roll** (NP-01, AV-07) | 12 + data | Every improvised NPC must be generated *and committed to state* |
| G-13 | **Rulings precedent log** (DM-05) | 12 + 00 state | Goal 2 consistency for novel actions; the "thousandth use" requirement |
| G-14 | **Meta-currency decision** (RS-18) | 01 or 07 (decide) | Ties to "last-chance choice"; momentum/hero points are the precedent |
| G-15 | **Encumbrance / supply abstraction, mounts & vehicles** (EQ-02, EQ-09, EQ-10, CF-14) | 08 + 10 | Named in no ownership line |
| G-16 | **Magic as a named subsystem; rituals & research** (MG-03, MG-04) | 05 (+13 lore) | "Magic" appears nowhere in the map despite classic fantasy |
| G-17 | **Index, DM quick-reference, credits** (FN-09, FN-10, FN-12) | appendix | Auditability; CC-BY attribution if we lift oracle tables |
| G-18 | **Languages; spatial description in text; mass combat** (SO-04, EX-14, CF-15) | 13/01; 12; 11 | Smaller, but each will come up; ship anchors |

### 5.2 Top recommendations (ranked)

1. **Adopt a time ladder with a tick-registration contract in 00** (§3.3). Everything else —
   faction turns, recovery, supply, afflictions, consolidation — hangs off it. Provide an
   `advance_time` tool that runs every registered tick for every boundary crossed.
2. **Give the DM an oracle** (`ask_oracle`, 9-rung d100 ladder with qualified yes-but/no-and
   answers, doubles-as-twist) **and a Tension dial** fed by P16's counter (P-01, P-02, P-03).
   World questions use d100, player actions use d20 — never confused. Established facts are never
   re-asked. This is the single most important import from solo play: it removes the AI's own
   bias from world facts.
3. **Make threads first-class state** (Mythic lists + Ironsworn vows + Mythic flashpoints, P-07,
   P-08, P-14). Weighted threads and cast lists feed random events; each thread has a ranked
   progress track with flashpoints every 5 that *force* a revelation — P16 becomes mechanical.
   Completion of a player-sworn thread is a P2 crystallization moment.
4. **Hidden clocks with authored observable portents** (P-17 + P-19 + MR omens): every hidden
   clock segment and every near-miss encounter check produces a narrated sign. This reconciles the
   hidden-mechanics lock with the telegraphed-lethality lock in one rule.
5. **Two-tier faction engine** on the downtime/season cadence: SWN/WWN-style faction turns for
   majors (P-23), Mausritter d6 rolls for minors (P-25), Blades status −3..+3 as the relationship
   table (P-22), Blades heat/entanglements generalized to per-region **Notice** (P-18, P-26).
6. **Adopt Delve's site procedure for dungeons** (P-28): area-based progress, approach-specific
   outcome tables, Reveal-a-Danger / Find-an-Opportunity tables, theme × domain as the P5
   pool-gate for loot and adversaries. Pair with TB's "a turn passes per resolved action" and SD's
   danger-level encounter cadence (P-13, P-34), and 4AD's rising-climax chance (P-35).
7. **One generic extended-task engine** — progress track vs tension clock (ISF scene challenge,
   P-21) — skinned for chase, infiltration, negotiation, ritual, siege-of-a-door. The best
   single analogical anchor for novel multi-step actions.
8. **Companions as a named subsystem** (G-3): stat template, loyalty/relationship track (P-27),
   what they do in combat without separate turns (IS companion-asset model), journey roles
   (P-31/P-32), and what happens when they're hurt. Solo play without companions is lonely
   *and* mechanically thin.
9. **Session moves for safety and continuity** (P-10): begin/end session, set a flag, change
   your fate (five bounded re-framings), take a break — plus a 60-second session zero in 13's
   opening script and a newcomer teaching arc (§4).
10. **A season turn as the constitution-VI consolidation boundary** (P-44): major faction turns,
    weather regime, seasonal projects, holdings upkeep, and confirm/retire provisional content —
    telegraphed in advance to the player, never mid-venture.

Also recommended (beyond the top 10): the rulings precedent log (G-13); a staged-affliction
template (G-8); UNE-shaped NPC generation committed to state on first mention (G-12); Blades'
1/2/3/5 tick ladder for all downtime projects (P-45); major projects paid in renown (P-24);
legacy via progress rolls against recorded history (P-43); a 5-question fast creation path;
supply as a 0–5 abstraction for travel (P-30); TOR-style event-paced travel to avoid encounter
spam (P-32); Gumshoe core-clue guarantee plus the Three Clue Rule wired into P17 (P-41).

### 5.3 Things in BRIEF.md I'd flag

- §9 lists `data/*.yaml` "oracle/generation tables" but **no chapter owns oracles**; recommend 12.
- §9's `10-exploration-social-downtime.md` is overloaded: travel + sites + hazards + investigation
  + social + downtime is ~a third of a core book. Consider splitting social/downtime out, or at
  minimum the auditor should check 10 against EX-, SO-, TM-06 rows individually.
- §4 "open-ended sandbox" implies a season/year cadence and a player-driven endgame (holdings,
  major projects, legacy); only legacy is currently owned.

---

## 6. Open questions this research cannot settle (with tests)

- **Tension dial value.** Does a Mythic-style chaos dial improve perceived liveliness over
  plain P16? *Test:* two 20-scene simulated sessions, same seed situation, one with Tension-driven
  scene tests/random events, one with P16 only; blind-rate "the world surprised me" per scene and
  count dead-end streaks ≥3. Default meanwhile: adopt it (cheap, deterministic).
- **Encounter density.** Per-watch checks (CRN ~0.5/day) vs event-paced travel (TOR, lowest).
  *Test:* simulate 30 travel days under each; count encounters that produced a new lead vs
  "filler". Default: 1-in-6 per watch with omen on 2, travel events paced by the navigation roll.

---

## 7. Sources

Official / SRD / free rules
- Ironsworn SRD (CC-BY) — https://tedtschopp.github.io/Ironsworn-SRD/Ironsworn%20SRD.html
- Ironsworn free downloads (Tomkin Press) — https://tomkinpress.com/collections/free-downloads
- Ironsworn: Starforged SRD — moves index https://rsek.github.io/starforged-srd/ ; session
  https://rsek.github.io/starforged-srd/moves/session ; quest https://rsek.github.io/starforged-srd/moves/quest ;
  exploration https://rsek.github.io/starforged-srd/moves/exploration ; scene challenge
  https://rsek.github.io/starforged-srd/moves/scene_challenge ; connection
  https://rsek.github.io/starforged-srd/moves/connection ; legacy https://rsek.github.io/starforged-srd/moves/legacy
- Ironsworn: Delve (preview pages incl. move reference, site worksheet, theme/domain cards) —
  https://d1vzi28wh99zvq.cloudfront.net/pdf_previews/302260-sample.pdf ; product page https://tomkinpress.com/pages/ironsworn-delve
- Ironsworn challenge ranks — https://ironsworn-rpg.fandom.com/wiki/Challenge_Ranks
- Blades in the Dark SRD — https://github.com/amazingrando/blades-in-the-dark-srd-content/blob/master/Blades-in-the-Dark-SRD.md ;
  faction game https://bladesinthedark.com/faction-game ; entanglements https://bladesinthedark.com/entanglements ;
  downtime https://bladesinthedark.com/downtime-activities-play ; crew https://bladesinthedark.com/crew
- Blades cheat sheet (J. Alexander) — https://www.thealexandrian.net/creations/bladesinthedark/bladesinthedark-cheat-sheet-v2.pdf
- SRD 5.2 (CC-BY-4.0) — https://media.dndbeyond.com/compendium-images/srd/5.2/SRD_CC_v5.2.pdf ; https://www.dndbeyond.com/srd
- D&D 2024 DMG overview — https://www.dndbeyond.com/posts/1916-updates-in-the-dungeon-masters-guide-2024 ;
  https://dungeonsanddragonsfan.com/new-dungeon-masters-guide/
- Pathfinder 2e (Archives of Nethys): Playing the Game https://2e.aonprd.com/Rules.aspx?ID=2263 ;
  Exploration mode https://2e.aonprd.com/Rules.aspx?ID=469 ; Running modes of play https://2e.aonprd.com/Rules.aspx?ID=511 ;
  Hexploration https://2e.aonprd.com/Rules.aspx?ID=1265 ; Exploration activities https://2e.aonprd.com/Activities.aspx?Category=1 ;
  Downtime activities https://2e.aonprd.com/Activities.aspx?Category=2
- Worlds Without Number free edition — https://www.drivethrurpg.com/en/product/348809/worlds-without-number-free-edition
- Dungeon World SRD: fronts https://www.dungeonworldsrd.com/gamemastering/fronts/ ; first session
  https://www.dungeonworldsrd.com/gamemastering/first-session/
- Cairn 2e — core rules https://cairnrpg.com/second-edition/players-guide/core-rules/ ; combat
  https://cairnrpg.com/second-edition/wardens-guide/combat/
- Mausritter hexcrawl template — https://mausritter.com/assets/static/mausritter-hexcrawl-template.0eeYbW34.pdf
- TTRPG Safety Toolkit (Shaw & Bryant-Monk) — https://static1.squarespace.com/static/5e3843beb37a0716cf512998/t/62d1ae9c02aeab07ccac8f57/1657908893036/TTRPG_Safety_Toolkit_Guide_v2.5.pdf

Commercial games (described from reviews, publisher pages and reference sheets)
- Mythic GME 2e — https://www.wordmillgames.com/page/mythic-gme.html ; review https://hws3.wordpress.com/2023/03/11/review-mythic-game-master-emulator-2nd-edition/ ;
  fate check analysis https://drakonspyre.substack.com/p/worlds-alone-ii-check-your-fate ; lists guide
  https://jasonholtdigital.com/resources/setting-up-and-using-lists/ ; overview https://rollingalone.substack.com/p/rolling-without-a-gm-when-mythic
- Stars Without Number factions — https://takeonrules.com/2018/12/27/lets-read-stars-without-number-factions/ ;
  https://forum.rpg.net/threads/stars-without-number-factions.759846/
- WWN factions summary — https://grokipedia.com/page/Factions_Worlds_Without_Number
- The One Ring 2e journeys — https://theroleplayersguild.com/articles/the-one-ring-rpg/journeys-travel/journey-rules ;
  cheat sheet https://notes.nicolevanderhoeven.com/The+One+Ring+2e+Cheat+Sheet ; Strider Mode review
  https://rpgbot.net/the-one-rings-strider-rules-a-review/
- Forbidden Lands journeys — https://forum.rpg.net/threads/wir-forbidden-lands.853129/page-2 ; https://www.strangeassembly.com/2019/review-forbidden-lands
- Shadowdark time & light — https://thealexandrian.net/wordpress/52539/roleplaying-games/untested-shadowdark-real-time-dungeon-depths ;
  https://rodsandholes.com/shadowdark_rules_reference.html
- Torchbearer grind & phases — https://necropraxis.com/2014/03/10/torchbearer-grind-record/ ; https://cannibalhalflinggaming.com/2019/07/10/torchbearer-in-depth/
- Mausritter review (factions, watches) — https://deathtrap-games.blogspot.com/2021/01/game-review-mausritter-2e.html ;
  https://loottheroom.uk/the-long-read-mausritter
- Four Against Darkness — https://inkwellideas.com/solo-role-playing-games/solo-rpgs-four-against-darkness/ ;
  https://deathtrap-games.blogspot.com/2021/01/game-review-four-against-darkness.html
- Thousand Year Old Vampire — https://en.wikipedia.org/wiki/Thousand_Year_Old_Vampire ; https://www.rpg.net/reviews/archive/18/18890.phtml
- Kal-Arath & solo procedure — https://castlegrief.substack.com/p/how-to-play-ttrpgs-solo-part-2 ; https://solorpglist.com/item.php?id=949
- Crown & Skull — https://www.runehammer.online/crown-skull-rpg ; https://www.matthewdavisprojects.com/thoughts/solo-role-playing-crown-and-skull
- Pendragon Winter Phase — https://www.mk-rpg.org.uk/Pendragon_winter_phase_summary ; https://gnomestew.com/pendragon-core-rulebook-6th-edition-review/
- Ars Magica seasons & aging — https://www.redcap.org/page/Season ; https://thealexandrian.net/creations/ars-magica/ars-magica5-cheat-sheet-v1.pdf
- Beyond the Wall — https://writeups.letsyouandhimfight.com/gimpinblack/beyond-the-wall/ ; https://www.dieheart.net/beyond/
- UNE — https://chimericalrealm.blogspot.com/2021/01/universal-npc-emulator-and-everyone.html
- Pathfinder Beginner Box solo adventure — https://paizo.com/pathfinder/beginnerbox ; https://screenrant.com/pathfinder-beginner-box-review-2e-second-edition/
- Blades starting situations — https://thealexandrian.net/wordpress/40638/roleplaying-games/blades-in-the-dark-alternative-starting-situations

Design writing
- B. Rancourt, "A Survey of Overland Travel" — https://rancourt.substack.com/p/a-survey-of-overland-travel
- J. Alexander, Node-Based Scenario Design / Three Clue Rule — https://thealexandrian.net/wordpress/7949/roleplaying-games/node-based-scenario-design-part-1-the-plotted-approach ;
  https://thealexandrian.net/wordpress/7985/roleplaying-games/node-based-scenario-design-part-3-inverting-the-three-clue-rule
- Sly Flourish on fronts — https://slyflourish.com/looking_back_on_fronts.html

In-repo basis: `rules/_process/BRIEF.md`; `.specify/memory/constitution.md` (Principles III, VI,
VII; Patterns P1–P17); `reports/DM craft TTRPG design AI tools.md` (fabula/discourse split,
externalized state).
