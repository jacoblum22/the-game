# R7 — Freeform Adjudication: How to Let the Player Try Anything and Still Rule It Right

> Research digest for The Game's ruleset. Author: research agent R7. Serves chapters **01 (resolution)**,
> **06 (conflict)**, **10 (exploration/social/downtime)** and **12 (DM procedures)**. It surveys ~30
> systems and GM-craft sources on how an arbitrary player description becomes a mechanical
> resolution, synthesizes the design space, and recommends a concrete adjudication pipeline consistent
> with Principle VII → P8 → P17, proven on 13 worked examples. Mechanics are described in my own
> words; sources are listed at the end. Odds figures were computed by
> `scratchpad/odds.py` (exhaustive enumeration of d20 faces; reproduced in §5.9).

---

## 0. Executive summary

**The problem.** The owner's first design goal ("the player must feel free to try any creative
idea") and second ("the AI must adjudicate it correctly and consistently") look like opposites. Every
system surveyed sits somewhere on a tradeoff line between them: Wushu and Exalted maximize felt
freedom by letting description itself generate success or bonus dice, and pay for it with
adjudication that depends on taste; D&D 5e and GURPS maximize consistency with tables, and pay for it
with a flat "roll the skill, pass/fail" answer to most creative ideas. The research shows the
tradeoff is **not fundamental**. The systems that feel free *and* rule consistently all do the same
thing: they break adjudication into a **stack of small, separate questions**, and give each one its own
simple, checkable rule. The trouble in weaker systems comes from merging those questions.

**The seven separable questions** (the core finding; every good freeform system answers at least
four of them separately):

1. **What do you want, and what do you do?** (intent vs. method: Burning Wheel, the Alexandrian, Angry GM)
2. **Are you allowed to even try?** (permission: Fate's aspects-as-permissions, PF2e trained-only
   actions, GURPS no-default skills, Savage Worlds' Arcane Background, our Principle VII)
3. **Does it need dice?** (say yes or roll: Dogs in the Vineyard, Torchbearer's Good Idea, OSR,
   Ironsworn's "not everything is a move")
4. **Which existing rule is this most like?** (the anchor: PF2e's "most similar basic action", Fate's
   four actions and Bronze Rule, 5e's "an improvised weapon that resembles a real one uses its stats")
5. **How hard is it, how dangerous is it, and how much can it achieve?** These are three different
   dials: difficulty, stakes and reach. Blades in the Dark's position and effect are the clearest
   proof that stakes and reach must be kept apart from difficulty.
6. **What happened?** (a deterministic degree: PF2e four degrees; Blades 1-3/4-5/6/crit; PbtA
   6-/7-9/10+) and **how much of a compound intent got delivered** (Blades' effect-graded information,
   Dungeon World's Discern Realities, our P17)
7. **What does it cost, and what's next?** (a closed consequence menu: Blades' five consequences,
   Ironsworn's Pay the Price, Mouse Guard's twist-or-condition, Fate's minor/serious cost; our P16)

**How creativity should be rewarded (the key design answer).** Reward the **fictional leverage** a
creative method exploits, not how well it's described. Systems that grade description (Exalted stunt
dice, Wushu detail-counting) either make players write longer or make the GM judge taste, and taste
is exactly what an AI can't apply the same way twice. Systems that turn creativity into
**position** (Blades), **aspects** (Fate's Create an Advantage, where "throw sand in its eyes" is
literally the book example), or **status conditions** (Savage Worlds Tests) reward the *idea* through
a fixed mechanical channel. Recommended rule: a creative method earns a benefit **only when the AI can
name the specific established fact it exploits (a "lever")**. Each lever does one of three fixed
things, at most two levers per roll. If it's cool but no fact can be named, it's narration only.

**How impossibility should be handled.** "Impossible" is three different things, and handling them
the same way is the main source of both stinginess and permissiveness:
- **Impossible for anyone** in the setting. No roll; say why; offer the nearest thing that *is*
  possible (P16).
- **Impossible for you, now.** This is Principle VII's unlicensed case. Redirect to a **declared
  crude fallback** (a basic action, often weaker) and show the **path to the license**. This follows
  Dungeon World's Ritual move ("it's possible, but first you must...") and Burning Wheel's Beginner's
  Luck (unskilled attempts count toward learning).
- **Possible but past your reach** (DC above 20 + your modifier). Tell the player the odds before the
  roll. Don't hide a 5% miracle.

**The recommended pipeline (§4)**, in one line: **PARSE → GATE → NECESSITY → ANCHOR → FRAME →
OFFER → ROLL → READ → DELIVER → CONSEQUENCE → RECORD**. Each step is labeled [D] (deterministic),
[J] (bounded judgment against listed criteria) or [N] (narration). Three new artifacts make it work.
First, a **World-Fact Oracle** for facts nobody has established yet ("is there sand on this floor?"),
so the AI neither says yes to everything nor no to everything. Second, **data-declared fallbacks
and acquisition paths on every license**, so VII's "redirect" is looked up instead of improvised.
Third, a **ruling ledger**, so an improvised ruling becomes precedent the next time (PF2e's
chandelier-then-rope-bridge consistency advice, turned into state).

**What should change upstream (details in §7):**
- Adopt PF2e's "natural 20/1 shifts the degree one step" in place of "natural 20 = critical success".
- Recalibrate the DC ladder against the default +2 modifier. A "moderate" DC 15 succeeds only 40%
  of the time.
- Generalize P17 from information to **all** compound intents, and let the *player* rank the
  sub-questions instead of the DM.
- Add the Oracle and the ruling ledger as named patterns.
- Record that the probe's "DC 25 for ten arrows" ruling mixed up *quantity* with *difficulty*.

---

## 1. Scope, method, and what this builds on

**Already in the project, not repeated here:**
- The four-degree margin math (PF2e) and the basic shapes of Fate/Blades/Genesys/WoD degrees,
  from `research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md`.
- The zone and range abstractions (Fate zones, Dungeon World range bands, Ironsworn close/far), from
  `research_notes/Emergent power acquisition mechanisms/freeform_combat_positioning.md`.
- The probe's findings (`specs/001-action-resolution-probe/probe-results.md`): a capable model
  applies a deterministic degree cleanly; soft-locks happen; all-or-nothing compound queries feel
  wrong; the model improvised a fair throttle on "ten arrows".

**What this adds:** the upstream half of resolution, which the existing notes don't cover. How a
description becomes a legal attempt with a chosen stat, a DC, stakes and reach. How creativity turns
into mechanics. How impossibility and missing capability get redirected. How compound, extended,
opposed and assisted actions are structured. Which rules make good anchors for analogy.

**Method.** SRDs and official free rules where available (Fate SRD, Blades SRD, Dungeon World SRD,
Ironsworn SRD, Cypher open reference, PF2e Archives of Nethys, D&D Basic Rules, d20 SRD,
13th Age SRD, Year Zero SRD). Well-regarded secondary summaries were used where the primary text
isn't free (Burning Wheel, Mouse Guard/Torchbearer, Genesys, Heart, 7th Sea, Exalted, Wushu, Feng
Shui 2, GURPS, Mythic). GM-craft essays: the Alexandrian's *Art of Rulings*, the Angry GM, Principia
Apocrypha. Recent LLM-GM papers were checked for evidence on permissiveness. Where a claim rests on
a secondary source, the catalog says so.

---

## 2. Mechanics catalog

Format per entry: **mechanic** — how it works (3–6 lines) · **AI-DM strengths / weaknesses** ·
**Relevance** (01 resolution / 06 conflict / 10 exploration-social / 12 DM procedures).

### 2.1 Fate Core / Fate Condensed / Fate Accelerated (Evil Hat; Fate SRD, CC-BY)

**The four actions.** Every action is one of four: **Overcome** (get past an obstacle),
**Create an Advantage** (make or exploit a situation aspect), **Attack** (harm or take someone out),
**Defend** (stop an attack or advantage). Each has a fixed four-outcome table: fail / tie / success /
success with style. For Overcome: fail = don't get it, or get it at a serious cost; tie = get it at a
minor cost; success = clean; style = clean plus a boost.
· *Strengths:* the most complete "everything maps to four verbs" design in print. An AI can
classify any intent into four buckets with high agreement, and each bucket's outcome table is fixed.
*Weakness:* the buckets say what kind of result you get, not how hard the task is or what's at
risk. Fate leaves that to the difficulty ladder and GM taste.
· *Relevance:* 01 (the verb-classification step), 06 (Attack/Defend), 12.

**Create an Advantage (CaA).** Roll to put a new aspect on a target or the scene (e.g., *Blinded*,
*On Fire*, *High Ground*) or to find a hidden one. Success gives a free invoke (two with style). An
invoke is +2 or a reroll on a later, fictionally relevant roll. The SRD's own conflict example of an
advantage is throwing sand or salt in an enemy's eyes to make them *Blinded*.
· *Strengths:* the gold standard for turning a creative idea into a bounded mechanical asset. The
idea has to be rolled, it takes an action, and it pays off in a fixed currency (+2, used once).
*Weakness:* aspect wording is freeform, so an AI may inflate what an aspect allows. Fate itself
warns that aspects must pass a "sniff test".
· *Relevance:* 01 (setup and lever mechanics), 06 (combat maneuvers), 10.

**Aspects are always true: permissions.** Fate Condensed says outright that aspects grant or
remove *permission* for what can happen. A creature *Pinned* under a hydraulic press has lost
permission to move. A character with *Cybernetically Enhanced Legs* may have permission to leap a
wall with no roll at all. Fate Core's Extras chapter formalizes **permission** (the fictional
justification for having something at all) and **cost** (what you pay for it). The System Toolkit's
magic chapter notes that requiring an aspect is the simplest way to gate magic.
· *Strengths:* the cleanest precedent for Principle VII's "established narrative fact" license, and
for facts that *remove* options (conditions). *Weakness:* the permission a fact grants is decided by
table taste. For an AI that has to be pinned down (§4, GATE: literal scope).
· *Relevance:* 01 (the gate), 05, 12.

**Succeed at a cost.** On a failed Overcome, the GM may offer success at a *serious* cost, and a tie
gives success at a *minor* cost. The SRD lists minor costs such as foreshadowing peril, placing an
aspect, or giving an NPC a boost. A serious cost is a real, possibly lasting toll right now.
· *Strengths:* two named severity tiers are easy to apply. *Weakness:* when to offer it is up to the
GM, so it has to be made deterministic (see §4 READ, near-miss).
· *Relevance:* 01, 07.

**Challenges and contests.** A *challenge* resolves a complex task as several Overcome rolls, each
against a different part of the problem with a different skill. The mix of results is read as a
whole: mixed results mean partial victory plus complications. A *contest* is a race to three
victories between sides with mutually exclusive goals. Style counts double, and a tie brings in a
twist aspect. Teamwork: each helper with at least Average skill adds +1, capped.
· *Strengths:* the challenge is the best precedent for *decomposing* compound actions into
independently rolled beats. *Weakness:* "read the mix" is judgment and needs a table.
· *Relevance:* 01 (compound/extended), 10 (chases, rituals, investigations).

**Fate Accelerated approaches.** Six *how* stats (Careful, Clever, Flashy, Forceful, Quick,
Sneaky). You pick the approach from the description of your action, and you can't describe
something that doesn't make sense just to use your best approach (creeping quietly isn't Forceful).
· *Strengths:* the clearest statement of "**the stat follows the method**", a rule an AI can check
("does the described method match the stat?"). *Weakness:* players shade descriptions to reach good
stats. FAE answers that the method's *fiction* matters: a Forceful approach has Forceful consequences.
· *Relevance:* 01 (stat selection).

**The Bronze Rule / Fate Fractal.** Anything (a storm, a gun, a curse, a ship) can be written up
like a character, with aspects, skills and stress, instead of inventing a new subsystem.
· *Strengths:* the purest **analogy engine** in any system. When a player takes on something with
no rule (a storm, a mob, a ward), stat it as an adversary and use the existing conflict rules.
*Weakness:* can produce stat blocks for things that should just be fixed obstacles.
· *Relevance:* 09, 10, 12 (improvising from the substrate).

**Stunts.** A narrow rule exception attached to a skill: +2 in a specific circumstance, a new use
for a skill, or a once-per-session effect.
· *Relevance:* 05 (shape of licensed abilities: a stunt is a **scoped license**).

### 2.2 Blades in the Dark (John Harper; Blades SRD, CC-BY)

**The action roll.** (1) The player states a *goal* and chooses an *action rating* that fits what
the character does. (2) The GM sets **position** (controlled / risky / desperate: how bad failure
can be) and **effect** (limited / standard / great: how much success achieves). (3) Bonus dice.
(4) Roll a d6 pool and take the highest. 6 = success, 4–5 = success with consequence, 1–3 = failure
with consequence, two 6s = critical. The *position* sets how harsh the consequence is.
· *Strengths:* separating **risk** from **scope** before the roll is the most useful single idea for
this project. Once the GM has announced the two dials, the result table is deterministic.
*Weakness:* setting position and effect is GM judgment. Blades lists the factors that feed it but
gives no algorithm.
· *Relevance:* 01 (stakes and reach dials), 06, 12.

**Effect factors and zero effect.** Effect starts from the GM's sense of the situation, then moves
by three factors: **potency** (exploiting a weakness, magic, extra risk or time), **quality/tier**
(better tools and resources), and **scale** (numbers, size, scope). If the factors stack against you,
effect can reach **zero**: the action can't accomplish its goal without a special ability or pushing
yourself. Players can **trade position for effect** (accept more risk for more result).
· *Strengths:* "zero effect" is a principled middle ground between "impossible" and "roll": you may
act, but this method can't reach this goal. It's the exact counterpart of VII's redirect. The factor
list is a checklist an AI can run. *Weakness:* how many factors add up to one step is left vague.
· *Relevance:* 01 (reach dial; §4 FRAME), 06 (scale vs. mobs), 09.

**Consequences and resistance.** A closed menu of consequence types: reduced effect,
complication (often ticks on a clock: 1/2/3 segments by severity), lost opportunity, worse position,
harm (levels 1–4). Severity scales with position. Players can make a resistance roll to reduce or
avoid a consequence. It always works, and the stress it costs shrinks the better the roll.
· *Strengths:* a **closed consequence menu** is exactly what an AI needs to avoid inventing
arbitrary punishments. *Weakness:* the consequence type is still chosen by the GM, so it needs
selection criteria.
· *Relevance:* 01, 07, 12.

**Devil's Bargain; assist; setup; group action.** The GM or table offers +1d in exchange for a fixed
complication that happens *whatever the roll* (collateral damage, a clock tick, heat, lost coin). An
ally assists for +1d by taking 1 stress. A **setup** action works indirectly: if it succeeds, whoever
follows through gets +1 effect or better position. In a **group action** everyone rolls and the
best result counts, but the leader takes stress for each failure.
· *Strengths:* **setup** is the formal version of "sand then slide". *Weakness:* the Devil's Bargain
relies on the GM proposing a good price. That's fine for an AI if the price comes from a fixed menu.
· *Relevance:* 01 (help, setup, linked beats), 06.

**Progress clocks.** Segmented circles (4 = complex, 6 = complicated, 8 = daunting) track
obstacles, dangers, races, linked chains, tug-of-war and faction goals. Name clocks after the
obstacle, not the method ("Interior Patrols", not "sneak past the guards"). In downtime, a
long-term project clock ticks by roll: crit 5, 6 → 3, 4–5 → 2, 1–3 → 1.
· *Strengths:* a deterministic, externally stored way to track any extended task. Probably the
most portable subsystem in indie design. *Weakness:* sizing is judgment, but it only has three values.
· *Relevance:* 01 (extended tasks), 10, 11.

**Gathering information.** Common knowledge is simply answered. Otherwise the roll's *effect* sets
the quality of information: great = complete, with room for follow-ups; standard = good details;
limited = partial, more work needed. Questions too complex for one roll become long-term projects.
· *Strengths:* independent confirmation of P17. Blades already grades *how much* information you
get by effect rather than giving all or nothing. *Relevance:* 01 (P17), 10.

### 2.3 Apocalypse World / Powered by the Apocalypse

**"To do it, do it" and moves as triggers.** A move is a fictional trigger plus a mechanical
procedure. You can't invoke "go aggro" by name. Your character has to *do* something in the fiction
that counts, and if they do it, the move happens. 10+ full success, 7–9 success with a hard choice or
cost, 6− the MC makes a move.
· *Strengths:* makes resolution **fiction-first and non-optional**: the description decides which
procedure applies, not the player's preference. Close to VII's framing. *Weakness:* when no move
fits, the MC just says what happens, which is judgment with no floor.
· *Relevance:* 01, 12.

**MC principles and moves.** The MC makes a move when players look to them, give a golden
opportunity, or miss. The MC moves are a **closed menu** (separate them, capture someone, inflict
harm, announce future badness, take away their stuff, offer an opportunity with or without cost,
tell them the possible consequences and ask, and so on). The principles include *ask provocative
questions and build on the answers* and *be a fan of the characters*.
· *Strengths:* a closed consequence and complication vocabulary. *Tell them the possible
consequences and ask* is the model for §4 OFFER. *Weakness:* choosing soft vs. hard moves is taste.
· *Relevance:* 12.

### 2.4 Dungeon World (Koebel & LaTorre; DW SRD, CC-BY)

**Defy Danger — stat by method.** When you act despite an imminent threat, say *how* you deal with
it. Powering through = STR, getting out of the way or acting fast = DEX, enduring = CON, quick
thinking = INT, mental fortitude = WIS, charm = CHA. On 10+ the threat doesn't land. On 7–9 you
stumble or hesitate, and the GM offers a worse outcome, a hard bargain, or an ugly choice.
· *Strengths:* the textbook catch-all basic action with the **stat chosen by method**. *Weakness:*
covers only "act despite danger", so it can't handle creating advantage or long tasks.
· *Relevance:* 01, 06.

**Discern Realities / Spout Lore.** Study a situation: 10+ lets you ask three questions from a fixed
list, 7–9 lets you ask one. Spout Lore gives interesting and useful information on 10+, and on 7–9
only interesting information that you have to make useful yourself.
· *Strengths:* the **question-count-by-degree** shape of P17, with a *fixed list* of askable
questions. That's a strong consistency tool: the questions can't be loaded.
· *Relevance:* 01 (P17), 10.

**GM moves** include *tell them the requirements or consequences and ask*, *show signs of an
approaching threat*, *offer an opportunity, with or without cost*, *use up their resources*, and
*show a downside to their class, race or equipment*.
· *Relevance:* 12 (the redirect vocabulary).

**The Wizard's Ritual.** At a place of power, tell the GM what magical effect you want. It's
*always possible*, but the GM attaches one to four conditions from a fixed list: it takes
days/weeks/months; first you must ___; you need help from ___; it costs a lot of money; the best
you can do is a lesser, unreliable, limited version; you and your allies risk danger from ___.
· *Strengths:* **the single best precedent for redirecting instead of refusing**. The answer to
"can I do this?" is "yes, if..." plus a *closed list* of requirement types. This becomes the
**acquisition-path** field of a license (§4 GATE-3).
· *Relevance:* 01 (VII redirect), 05, 10 (downtime projects).

### 2.5 Ironsworn / Starforged (Shawn Tomkin; Ironsworn SRD, CC-BY)

**Action roll and Face Danger.** d6 + stat vs. two d10 challenge dice. Beat both = strong hit, beat
one = weak hit, beat neither = miss. Doubles are a *match*: a twist or opportunity. **Face Danger**
is the catch-all for risky actions with no specific move, and the stat is chosen by approach: edge
for speed, agility or precision; heart for charm, loyalty or courage; iron for aggression, strength
or endurance; shadow for deception, stealth or trickery; wits for expertise, insight or observation.
A strong hit succeeds. A weak hit succeeds at a cost from a fixed list (lose momentum, 1 harm,
1 stress, 1 supply). A miss means **Pay the Price**.
· *Strengths:* built for **solo play with no human GM**, which is structurally our situation. Every
open question is meant to be resolved by a procedure. *Weakness:* "envision the outcome" still
needs judgment, but it's bounded by fixed lists.
· *Relevance:* 01, 12.

**Secure an Advantage.** Assess, prepare or gain leverage. A strong hit gives +1 on your next move
or +2 momentum. A weak hit gives +1 momentum. A miss means Pay the Price.
· *Relevance:* 01 (setup beats: a *generic* lever-creation action).

**Pay the Price.** On a miss, pick the most obvious negative outcome, or roll on a table of
consequence types (harm, stress, supply, a new danger, a companion hurt, a vow threatened, and so on).
· *Strengths:* a **rollable fallback** when the AI has no obvious consequence, which is anti-drift.
*Relevance:* 12.

**Progress tracks and challenge ranks.** Vows and journeys use 10-box tracks. Rank (troublesome,
dangerous, formidable, extreme, epic) sets progress per milestone (3 boxes, 2, 1, ½, ¼). The finish
is a *progress roll*: your filled boxes vs. the challenge dice, with no stat.
· *Relevance:* 01 (extended tasks), 11 (long goals).

**Ask the Oracle.** Answer a yes/no question about the world by choosing odds and rolling d100:
almost certain = yes on 11+, likely 26+, 50/50 51+, unlikely 76+, small chance 91+. A match is an
extreme result or twist.
· *Strengths:* **the answer to "is there sand on the floor?"** when no one has decided. Fairness comes
from committing to odds *before* rolling, instead of the GM deciding by whim (which pulls toward
"yes" for a sycophantic AI, or toward "no" for an adversarial one). *Relevance:* 01, 10, 12.

### 2.6 Cypher System (Monte Cook Games; Cypher open reference)

**One difficulty scale for everything.** Every task is rated 0–10 (routine, simple, standard,
demanding, difficult, challenging, intimidating, formidable, heroic, immortal, impossible). The target
number on a d20 is 3 × difficulty. **Easing:** training eases one step and specialization two;
assets (tools, help, circumstance) ease up to **two steps, maximum**; Effort (spending a stat pool)
eases one step per level. Difficulty 0 means automatic success with no roll. Difficulties 7–10 can't
be rolled until eased.
· *Strengths:* **everything has a level**, the same scale as creatures and objects. That makes the
DC a property of the thing, not of the attempt, which helps consistency. The **asset cap of two**
is an elegant limit on stacking creativity. *Weakness:* the core guidance admits there is no master
list and asks for logical judgment. It relies on a human sense of "who could do this".
· *Relevance:* 01 (DC ladder, lever cap), 12.

**GM intrusions.** Instead of the GM rolling for complications, the GM offers one (e.g., the rope
frays) and pays the player XP. The player can refuse by paying XP. A natural 1 gives a free
intrusion.
· *Strengths:* complications become an *economy*, visible and consensual. *Weakness:* when to
intrude is pure taste. Our P16 anti-soft-lock trigger is the deterministic equivalent.
· *Relevance:* 12.

**Unusual stat pairings.** The core advises allowing an unusual stat for a task (e.g., Intellect to
find a door's weak point) when it makes sense, but not letting it become routine.
· *Relevance:* 01 (method → stat).

### 2.7 Savage Worlds Adventure Edition (Pinnacle)

**Tests** (formerly Tricks). Describe a maneuver (throwing sand, a taunt, a feint) and make an
opposed skill roll against the target's linked attribute. Success makes the target **Distracted**
(−2 to its trait rolls) or **Vulnerable** (+2 to actions against it) until the end of its next turn.
A raise also Shakes it.
· *Strengths:* the most **bounded creativity-to-mechanics conversion** in mainstream play. Any
clever maneuver, however it's described, gives one of *two* fixed conditions. An AI can't inflate it.
*Weakness:* the effects are generic, so flavor carries the difference.
· *Relevance:* 01 (lever types), 06.

**Support.** Describe how your skill helps an ally: success gives +1, a raise gives +2, total help
usually capped at +4. **Unskilled attempts** roll d4−2. **Arcane Background** is a hard gate: no
powers at all without the Edge. **Improvised weapons** are −2 to attack, with damage by size.
· *Relevance:* 01 (help caps), 05 (license gate precedent), 06.

### 2.8 D&D 5e (2014 core; Basic Rules / SRD 5.1)

**Improvising an action.** A player may attempt anything not covered by the listed actions. The DM
says whether it's possible and what roll, if any, decides it.
· *Strengths:* sets expectations for freedom. *Weakness:* no procedure behind it. It's the model of
"DM decides" that P8 and VII exist to tighten.
· *Relevance:* 01, 12.

**The ability-check DC table** (very easy 5, easy 10, medium 15, hard 20, very hard 25, nearly
impossible 30). **Contests** (both roll, higher wins, a tie changes nothing). **Variant pairings**
(e.g., Strength for Intimidation). **Working together**: the helper must be able to do the task
alone, and some tasks (threading a needle) can't be helped. The lead gets advantage. **Group checks**
succeed if at least half succeed. **Passive checks** use 10 + modifiers.
· *Strengths:* simple and well known. The "can this task even be helped?" test is a good gate.
*Weakness:* advantage is a coarse single bonus, and contests double the dice.
· *Relevance:* 01, 10.

**DMG: success at a cost and degrees of failure.** Optional rules. When a check fails by only 1 or
2, the DM may offer success with a complication. Some failures have worse results when they fail by
5 or more.
· *Relevance:* 01 (near-miss band; §4 READ).

**Improvised weapons and improvised damage.** An object that resembles a real weapon can be treated
as that weapon. Otherwise it does 1d4. DMG p.249 gives an improvised-damage table (burned by coals
1d10 up to submerged in lava 18d10) and damage severity by level (setback, dangerous, deadly).
· *Strengths:* **"if it resembles X, use X's stats" is the canonical analogical-anchor rule**, plus
a severity ladder for hazards the rules never listed. *Relevance:* 06, 07, 10.

### 2.9 Pathfinder 2e (Paizo; Archives of Nethys, ORC)

**The most similar basic action.** GM Core: when you're unsure which action a task uses, find the
most similar basic action. If none fits, invent an *undefined action* and give it the relevant
traits (attack, concentrate, manipulate, move) so that existing rules (attack penalties, reactions,
concentration) apply automatically. Stay consistent with earlier rulings. The book's example: a
character swung from a chandelier to attack and needed an Athletics check with a +1 to hit, so later
hanging from a rope bridge to attack a bat "sounds similar" and gets the same ruling. It also urges
"yes, but" over "no".
· *Strengths:* **the most explicit analogy doctrine in any mainstream system**. It adds trait tagging
(an improvised action inherits the rules its traits imply) and *precedent* as a consistency tool.
Both map directly onto our P3 substrate and onto a ruling ledger. *Weakness:* the precedent lives
in the GM's memory, so we have to externalize it.
· *Relevance:* 01, 06, 12 (anchor step; ruling ledger).

**DC tables.** *Simple DCs* by the proficiency the task demands: untrained 10, trained 15, expert 20,
master 30, legendary 40. *Level-based DCs* (level 0 = 14 up to level 25 = 50) for things with a
level. *Adjustments*: incredibly easy −10, very easy −5, easy −2, hard +2 (uncommon), very hard +5
(rare), incredibly hard +10 (unique). Circumstance bonuses/penalties are ±1 minor, ±2 major, capped
at ±4. Social DCs move with attitude (easy for friendly, very hard for hostile). **Opposed checks**
are usually a roll against the target's DC (10 + modifier), so only one side rolls.
· *Strengths:* **"DC by who could do this"** (untrained/trained/expert...) is the most AI-checkable
DC heuristic surveyed. The ±4 circumstance cap bounds stacking. A **static DC for the opposition**
halves the dice and keeps the target's defense a stored property. *Relevance:* 01 (FRAME).

**Trained-only actions and minimum proficiency.** Many skill actions need at least trained
proficiency to attempt (e.g., Decipher Writing, Treat Wounds, Disable a Device, Pick a Lock, Borrow
an Arcane Spell, Learn a Spell). GM Core adds that some tasks can't be succeeded at without a minimum
rank, even if attempted.
· *Strengths:* **the mainstream precedent for Principle VII's license tier**. Some verbs exist only
for people with training. *Relevance:* 01 (GATE), 05.

**Recall Knowledge.** Harder follow-ups. A critical failure gives *false* information that should be
wrong without being campaign-wrecking.
· *Relevance:* 01 (P17 critical-failure row), 10.

### 2.10 GURPS 4e (Steve Jackson Games)

**Defaults and no-default skills.** An untrained character can use a skill at a *default*: an
attribute minus 4 (Easy), 5 (Average) or 6 (Hard), or another skill minus some amount. Some skills
have **no default**: an untrained person can't meaningfully attempt them. **Techniques** are narrow
maneuvers that default to a parent skill at a penalty and can be bought up to a cap.
· *Strengths:* a **graded capability gate**. "Can attempt at a penalty" and "cannot attempt" are
different, and the difference is data on the skill. That's the direct model for the §4
`crude_fallback` field. *Relevance:* 01, 05.

**Task-difficulty modifiers.** A named ladder from +10 (automatic) through +8 trivial, +6 very
easy, +4 easy, +2 very favorable, +1 favorable, 0 average, −1 unfavorable, −2 very unfavorable,
−4 hard, −6 very hard, −8 dangerous, down to −10 (impossible: no sane person would try). Each rung
has a one-line description of *who would hesitate*.
· *Strengths:* describing each rung by *who would hesitate* makes it calibratable by an AI.
*Relevance:* 01. **Language comprehension levels** (none, broken, accented, native) are a model for
graded licenses (worked example 4).

### 2.11 Genesys / FFG Star Wars (Fantasy Flight; secondary sources)

**Two-axis narrative dice.** A dice pool gives success/failure *and* advantage/threat as independent
axes. Triumph and despair are special. Difficulty is set by the number of purple dice (simple 0,
easy 1, average 2, hard 3, daunting 4, formidable 5), which can be *upgraded* to red. Spending tables
say what advantage and threat buy (e.g., one advantage recovers strain or gives a boost die, three
negate cover or a similar benefit).
· *Strengths:* "failed, but something good happened" and "succeeded, but at a price" are different
results. *Weakness:* it needs special dice and the spending is table-negotiated. For us, the idea
is a **cost menu with fixed prices**.
· *Relevance:* 01 (the consequence axis), 06.

### 2.12 Mythic Game Master Emulator (Word Mill; secondary sources)

**The fate chart and chaos factor.** Ask a yes/no question, choose odds from impossible to "has to
be", and cross-reference the **chaos factor** (1–9, starting at 5, rising when things spin out of
control and falling when the characters are in control). Roll d100: yes, no, exceptional yes,
exceptional no. Doubles within the chaos rating trigger a random event.
· *Strengths:* established solo-play precedent for letting a *procedure* decide undetermined facts.
Chaos is a deterministic "how wild is the world right now" dial. *Weakness:* in unskilled hands it
produces incoherent facts, so odds need grounding criteria.
· *Relevance:* 10, 12 (World-Fact Oracle).

### 2.13 Year Zero Engine / Tales from the Loop / Vaesen (Free League; YZE SRD)

**Only roll when it's critical; no retries; push.** Roll only for uncertain, high-stakes moments.
You can't reroll the same action unless circumstances change substantially. You may **push** once:
reroll the non-1 dice and take damage or stress per bane (in Tales from the Loop, a Condition).
Modifiers run from +3 trivial to −3 formidable. Each helper gives +1 (max three).
**Extended trouble** needs a set number of successes across mixed skill rolls.
· *Strengths:* the **no-retry rule** is the cleanest statement of "let it ride". Push is a
player-chosen, pre-priced risk. *Relevance:* 01, 10.

### 2.14 Burning Wheel Gold (Luke Crane; secondary sources)

**Intent and task; say yes or roll.** The player states *intent* (what they want) and *task* (what
the character does). The GM sets an obstacle and **states the consequence of failure before the
roll**. If the task is within the character's ability and nothing is at stake, the GM says yes.
**Let it ride:** one test per obstacle, with no re-rolling until conditions truly change.
**Linked tests:** the result of a preparatory test gives bonus dice (success) or raises the
obstacle (failure) on the main test. **FoRKs:** related skills add dice. **Help** adds dice.
**Beginner's Luck:** with no skill, test the root stat at **double obstacle**, and the attempt counts
toward *learning the skill*.
· *Strengths:* **stating the failure consequence before the roll** is the most important
anti-drift habit an AI DM can have. It turns an after-the-fact judgment into a commitment. Linked
tests formalize multi-beat actions. Beginner's Luck is the model for "unskilled attempts are a path
to capability". *Relevance:* 01, 04 (learning by doing), 12.

### 2.15 Mouse Guard / Torchbearer (Luke Crane & Thor Olavsrud)

**Twist or condition.** On a failed test the GM either introduces a **twist** (the goal isn't
reached, the situation changes, often a new obstacle) or lets the player **succeed with a
condition** (hungry, angry, afraid, exhausted, injured, sick; each a fixed mechanical penalty).
**Obstacles are built from factors**: a base plus a fixed list of complications that each raise the
obstacle. Torchbearer's **Good Idea**: a truly clever solution from an unexpected direction can
simply succeed, with no roll.
· *Strengths:* **twist or condition** is the smallest possible consequence menu, and "success +
condition" is the tidiest fail-forward. **Factor-counted obstacles** make DC-setting checkable.
**Good Idea** is the right reward for player ingenuity that changes the problem.
*Weakness:* "clever" is judgment, so it needs criteria. *Relevance:* 01, 07, 10.

### 2.16 Heart: The City Beneath (Grant Howitt & Christopher Taylor; secondary)

**Dice pool with difficulty removing dice.** Pool = 1d10 + skill die + domain die + mastery. Take
the highest die: 1–5 fail, 6–7 success at a cost, 8–9 success, 10 critical. **Risky** removes the
highest die, **Dangerous** removes the two highest, and anything harder is simply **impossible**.
· *Strengths:* **a hard ceiling on difficulty**. There's no "DC 35 for a 1% miracle", and
impossible is a category rather than a number. The success-at-a-cost band is part of the core
result table. *Relevance:* 01 (reach ceiling), 07.

### 2.17 Troika! (Daniel Sell)

**Roll-under Skill + Advanced Skill; opposed "roll versus".** Advanced Skills cover spells,
trades and odd knowledges. Without the relevant Advanced Skill you roll the base Skill alone, and
spells *are* Advanced Skills, so no spell means no casting.
· *Relevance:* 05 (skills-as-licenses in the leanest possible form).

### 2.18 OSR practice (Finch's *Quick Primer*, Principia Apocrypha, "rulings not rules")

Rulings over rules: make a common-sense ruling in the spirit of the game and move on. Player skill
over character ability: problems are meant to be solved by describing *how*, and rolls are the
fallback. Ask players how they do it. Be generous with clever solutions within the realm of
possibility.
· *Strengths:* the purest version of goal 1. Describing concretely *is* the adjudication, and a good
plan wins without dice. *Weakness:* consistency depends on one referee's memory and temperament,
which is exactly what an AI lacks across contexts. Needs the ruling ledger.
· *Relevance:* 12.

### 2.19 Dogs in the Vineyard (Vincent Baker, 2004)

**Say yes or roll the dice.** If nothing is at stake, say yes and move on. Otherwise go to dice.
· *Relevance:* 01 (the NECESSITY step), and the ancestor of Burning Wheel's rule.

### 2.20 Wushu (Daniel Bayn)

**The Principle of Narrative Truth.** What a player describes happens as described. Dice only
decide how much it moves the scene forward. Each detail in the description adds a die (default
cap 6). There's a veto for descriptions that break the scene.
· *Strengths:* maximum felt freedom. *Weakness for us:* directly **violates Principle VII** (the
description creates the capability) and rewards verbosity. It's the counter-example that defines
the boundary. *Relevance:* design-space boundary only.

### 2.21 Feng Shui 2 (Robin Laws; Atlas)

**Unconventional attacks are just attacks.** Using the environment to hurt someone (smashing them
with a chandelier) uses your normal attack and damage with **no penalty**. It only counts as a
**stunt**, adjudicated separately, when it does something *beyond damage* (the chandelier *pins*
them).
· *Strengths:* a crisp **flavor vs. effect line**. Flamboyant description is free and changes
nothing, and an extra mechanical effect is a different action with its own resolution. That line is
the basis of the "cool alone is not a lever" rule. *Relevance:* 01, 06.

### 2.22 Exalted (White Wolf / Onyx Path)

**Stunt dice.** The GM rates a description one to three dots for how cool it is. Each dot adds a
bonus die, and a successful stunt restores motes or Willpower.
· *Strengths:* strongly encourages vivid play. *Weakness for us:* the reward is a *taste judgment*
on prose, applied every action. Players learn to write more, not think better, and an AI grading
its own player's prose will drift and be sycophantic. **Not recommended** except as flavor.
*Relevance:* design-space boundary.

### 2.23 7th Sea 2e (John Wick Presents)

**Raises as currency; consequences and opportunities.** You roll Trait + Skill d10s and group
them into sets of 10 (raises). There's no difficulty number. Instead the GM announces
**consequences** (bad things that happen unless you spend raises to prevent them) and
**opportunities** (bonuses you can buy with spare raises) *before* the roll. One raise achieves the
intent.
· *Strengths:* the purest **pre-announced stakes** system. The player sees the menu of risks and
bonuses and allocates success against them. *Weakness:* hard to price. *Relevance:* 01 (OFFER), 06.

### 2.24 13th Age (Pelgrane; 13th Age SRD)

**Backgrounds and DCs by environment.** Skills are replaced by player-written *backgrounds* (e.g.,
"former imperial courtier +3") argued into relevance. DCs are set by the *environment's tier*, not
the task: adventurer tier normal 15 / hard 20 / ridiculously hard 25, champion +5, epic +10. It
endorses **failing forward**.
· *Strengths:* freeform, fiction-derived bonuses. DC tied to *where you are* is easy to keep
consistent. *Weakness:* how relevant a background is gets argued each time, which an AI decides
inconsistently. *Relevance:* 01, 02 (origins as soft licenses).

### 2.25 D&D 3.5 / Pathfinder 1e — Use Magic Device

A trained-only skill that lets anyone attempt to **emulate** a class or racial feature in order to
use a magic item they otherwise couldn't: wand DC 20, scroll 20 + caster level, emulate a class
feature DC 20, activate blindly 25. Failing by 10+ is a *mishap*, and a natural 1 locks you out of
that item for 24 hours.
· *Strengths:* **a licensed skill whose whole purpose is attempting unlicensed things**, with priced
failure modes. The model for the §4 *emulate* field. *Relevance:* 05.

### 2.26 GM-craft essays

**The Alexandrian, *Art of Rulings*.** Separate **intention** from **method**. If you don't know what
the player is trying to achieve, find out before ruling. **Let it ride:** make one check for the
whole effort and let it stand, because repeated checks compound failure (75% three times ≈ 42%) and
teach players to stop making plans. Roll again only when the original attempt fails, the approach
changes, a significant milestone is reached, or circumstances change drastically.
**The Angry GM, *Adjudicate Actions*.** Get the intention and approach, then ask *is it possible*
(and can this approach reach this intent?), *is there a real chance of failure*, and *is there a cost
of failure*. Roll only if all three are true. Then separate the **outcome** (did the intention
happen?) from the **consequences** (what the approach causes regardless: noise, evidence,
reputation).
· *Relevance:* 12. This is the skeleton of §4.

### 2.27 LLM game-master research (checked for evidence on permissiveness)

- *Static vs. Agentic Game Master AI for Solo Role-Playing* (arXiv 2502.19519). The single-prompt v1
  GM was found **overly permissive**: it accepted player whims and embellished outcomes. The
  multi-agent v2 (ReAct with tools) scored significantly higher on mastery (p=.004), coherence
  (p=.040) and satisfaction (p=.047). This is evidence that **structured, stepwise adjudication beats
  one-shot narration on exactly our goal 2**.
- *Orchestrated Reality* (arXiv 2606.16014). Treats the world as an audited object. The model's
  actions are a **discrete intent kind plus structured parameters**, validated before being
  committed. It documents that a narrator stating world state in free prose makes an autonomous
  engine unworkable. This is conceptually the same as "classify into an anchor, fill its knobs,
  validate against state". (Work in progress: 15 illustrative incidents, no controlled study yet.)
- The project's own probe: zero mechanical contradictions once a degree was computed, but
  embellished ability text and a made-up pronoun. **Errors cluster where the AI writes freeform, not
  where it computes.** This justifies pushing as much of the pipeline as possible to [D].

---
## 3. The design space for "try anything"

### 3.1 Seven families

Nearly every surveyed mechanism falls into one of seven families. Most real systems combine two or
three.

| Family | Members | Core move |
|---|---|---|
| **A. Universal verbs** | Fate's four actions; Ironsworn Face Danger / Secure an Advantage; Dungeon World Defy Danger; PF2e basic actions | Every action maps onto a small, closed set of verbs with fixed result tables |
| **B. Rated obstacles** | Cypher 0–10; PF2e simple/level DCs; 5e DC ladder; GURPS task modifiers; Genesys purple dice; Heart risky/dangerous; Torchbearer factors | Difficulty is read off a named ladder, ideally as a property of the obstacle |
| **C. Fiction dials** | Blades position/effect; 7th Sea consequences/opportunities; Genesys advantage/threat | Risk and scope are set separately from difficulty, before the roll |
| **D. Say-yes / rulings** | Dogs in the Vineyard; Burning Wheel; OSR; Torchbearer Good Idea; Ironsworn "not everything is a move" | Most actions don't roll; a good plan beats dice |
| **E. Description-rewarded** | Exalted stunts; Wushu; (Feng Shui's flavor-is-free half) | How good the description is feeds the mechanics directly |
| **F. Oracles** | Mythic fate chart; Ironsworn Ask the Oracle | Undetermined world facts are decided by committed odds plus dice |
| **G. Permission gates** | Fate permissions and aspects; PF2e trained-only; GURPS no-default; Savage Worlds Arcane Background; Troika Advanced Skills; 3.5 UMD; Dungeon World Ritual; BW Beginner's Luck | Some verbs exist only with a license, and the best gates say what to do instead |

### 3.2 Comparison on the six axes

Ratings: ●●● strong, ●● medium, ● weak, judged for **a single-player game run by an AI DM**.

| Family | Freedom felt | Consistency of AI adjudication | How DCs get chosen | How creativity is rewarded | How impossibility is handled | How partial success / cost is expressed |
|---|---|---|---|---|---|---|
| A. Universal verbs | ●●● anything classifies | ●●● classification is easy to agree on | Borrowed from B | Via the advantage verb (CaA, Secure an Advantage) | Mostly unstated; "the fiction doesn't allow it" | Fixed per-verb tables (tie = minor cost; 7–9 = hard choice) |
| B. Rated obstacles | ●● | ●●● when the ladder has *who could do this* anchors; ● when it's vibes | Named ladder; best as an obstacle property (Cypher, PF2e levels) | Bonuses/easing, ideally capped (Cypher's two-asset cap; PF2e ±4) | A ceiling (Cypher 7+ unrollable; Heart "impossible"; GURPS −10) | Usually binary unless paired with degrees |
| C. Fiction dials | ●●● | ●● dials are judgment, but announced *before* the roll, which commits the GM | Implicit in position | By improving position or effect (Blades), buying opportunities (7th Sea) | **Zero effect**: you may act, but this can't reach that | ●●● best in class: the consequence menu scales with position |
| D. Say-yes / rulings | ●●● | ● depends on the referee's memory and temperament | Rarely needed | **Auto-success** (Good Idea); player skill | Referee says no, ideally with reasons | Referee's fiat |
| E. Description-rewarded | ●●● | ● taste-graded; drifts and flatters | Irrelevant or secondary | Directly, by prose quality (dots, detail count) | Wushu: nothing is impossible (**violates VII**) | Dice decide how far it goes, not whether |
| F. Oracles | ●● | ●●● once odds are chosen | N/A (odds, not DC) | A player can go looking for helpful facts and get a fair answer | "Impossible" is an odds rung | Exceptional yes/no; twists on a match |
| G. Permission gates | ● if it's a bare "no"; ●●● if it redirects | ●●● a license is a lookup | N/A | Licenses are *earned* (training, advancement) | **Redirect**: default at a penalty (GURPS), double obstacle (BW), a fixed list of requirements (DW Ritual) | Mishap on a large failure (UMD) |

### 3.3 What the comparison shows: nine findings

**F1. Freedom comes from separating the questions, not from saying yes.** The high-freedom,
high-consistency cells combine A + B + C + G: a small verb set, a named difficulty ladder, dials set
before the roll, and gates that redirect. D and E give freedom by trusting the referee, which is the
one thing our architecture can't assume. **Design implication:** keep the seven questions of §0
separate; each is a pipeline step.

**F2. The stat follows the method; the DC follows the obstacle; bonuses follow facts.** FAE,
Dungeon World's Defy Danger, Ironsworn's Face Danger and 5e's variant pairings all pick the stat from
*how* the character acts. Cypher (everything has a level), PF2e (levels and simple DCs) and 13th Age
(DC by environment) make difficulty a property of *what is being overcome*. Blades' potency and
quality factors, Fate's invokes and Cypher's assets make bonuses depend on *facts about the
situation*. Mixing these up causes most inconsistency. The classic failure: a cool method gets a
lower DC. Next time the same wall has a different DC because the player described it differently.

**F3. Reward the idea's leverage, never the prose.** Exalted and Wushu reward description and fail
our goal 2. Fate's CaA, Savage Worlds' Tests, Blades' setup and position, and Torchbearer's Good Idea
reward *what the idea changes in the fiction*. The Feng Shui line is the test: flavor that changes
nothing is free and earns nothing, while a mechanical side effect is a separate action.

**F4. Impossibility is three categories, and each needs its own response.** Setting-impossible
(Heart's "impossible", GURPS −10, Cypher 10): no roll. Not-for-you-yet (PF2e trained-only, GURPS
no-default, Savage Worlds Arcane Background, Troika): gate plus redirect. Past your reach (Cypher
7–9 until eased): tell the player the odds. Systems that fold these into "roll with a huge penalty"
(5e DC 30, or our current nat-20-always-crits) quietly allow miracles. Systems that fold them into
"no" (bare gates) create the "menu doesn't have that" walls goal 1 forbids.

**F5. The best redirects are closed lists.** Dungeon World's Ritual conditions, GURPS defaults, BW's
double obstacle, and 3.5's emulate DCs all turn "no" into "yes, if..." with a *finite, pre-written*
set of terms. For an AI that's decisive, because the redirect is a lookup, not an invention.
**Implication:** every license entry in `data/` carries a `crude_fallback` and `acquisition_paths`
field.

**F6. Partial success needs a closed consequence menu scaled by a pre-set stakes dial.** Blades,
Ironsworn, Mouse Guard, Fate, 7th Sea and Genesys all give a finite set of cost *types* with severity
tied to a dial set before the roll. That's what stops "success at a cost" from turning into arbitrary
punishment.

**F7. Compound actions come in four shapes, and each has a standard solution.**
(1) *Sequential beats* (setup → payoff): Blades setup, BW linked tests, Fate CaA → invoke.
(2) *Repetition of one act* ("shoot ten times"): the action economy throttles it, not the DC.
(3) *Bundled questions*: effect or degree decides how many get answered (Blades information by
effect, Dungeon World's 3-vs-1 questions, our P17).
(4) *Long efforts*: clocks and progress tracks (Blades, Ironsworn, Fate challenges, YZE extended
trouble).

**F8. Commitment before the roll is the strongest anti-drift tool.** BW states the consequence first,
7th Sea announces consequences and opportunities first, Blades sets position and effect first, and
Dungeon World's GM tells the requirements and consequences and asks. Once difficulty, stakes, reach
and the failure consequence are announced, reading the roll is mechanical. This matches the probe:
where the DM computed from a pre-set DC it made zero contradictions.

**F9. Precedent is a consistency mechanism.** PF2e tells GMs to rule the rope bridge the way they
ruled the chandelier, and OSR's consistency depends on the referee's memory. For an AI with no
durable memory, **precedent has to be stored state**: a ruling ledger keyed by the action's anchor
and deltas.

### 3.4 What makes a rule a good analogical anchor

This answers research question 4 and gives P3's "reach and adapt" substrate its authoring standard.
Across Fate's four actions, PF2e's basic actions and traits, 5e's "resembles a weapon" rule, Cypher's
"everything has a level", Blades' effect factors and the Bronze Rule, the rules that get borrowed well
share seven properties:

1. **Named by intent-shaped verbs** ("Grapple: seize and hold", not "Athletics check type B"), so a
   new action's *intent* retrieves it.
2. **Explicit knobs with defaults.** The parameters an adaptation may change are listed: DC tier,
   stat, action cost, reach, stakes, duration, the condition inflicted. If a rule has no named knobs,
   an adaptation rewrites it rather than adjusting it.
3. **A complete degree table.** Every outcome (critical success, success, near miss, failure,
   critical failure) is stated, so the borrowed rule gives a complete result.
4. **A declared scope and exclusions.** "Covers: X. Does not cover: Y." This stops the embellishment
   the probe saw (Heat Resistance growing a cold vulnerability).
5. **Traits or tags** that pull in general rules automatically (PF2e's attack/manipulate/move/
   concentrate. Ours: `physical`, `social`, `arcane`, `ranged`, `reaction`, `loud`...).
6. **Stable numbers.** The DC belongs to the obstacle and persists. Adapting doesn't reset it.
7. **Composable.** It can be a beat in a linked sequence or a tick source for a clock.

**Adaptation discipline (proposed rule):** an improvised ruling may move **at most two knobs** away
from its anchor. If more are needed, either the anchor is wrong (pick a closer one) or the action is
compound (split it into beats). This single constraint keeps "basically a grapple with a penalty" from
sliding into "a brand-new rule I just invented".

---

## 4. Recommended adjudication pipeline

The pipeline has eleven steps. Steps are tagged **[D]** deterministic/tool-owned, **[J]** bounded
judgment against the listed criteria, **[N]** narration. It implements Principle VII (steps 2–3),
then P8 (steps 7–8), then P17 (step 9), with P16 closing every path (step 10) and P3 feeding step 4.

### 4.0 The pipeline (verbatim, for chapters 01 and 12 to adopt)

> **1. PARSE [J].** Split the declaration into **intent** (what the player wants to be true
> afterward) and **method** (what the character physically, verbally or magically does). Split
> compound declarations into **beats**: one method, one target, one intended change each. Mark each
> beat as *sequential* (depends on an earlier beat), *repeated* (the same act N times), *bundled*
> (several questions or intents from one act), *conditional* (if X then Y) or *extended* (too big
> for one attempt). Ask **at most one** clarifying question, and only if the answer would change the
> gate, the anchor or the stakes. Otherwise state the reading you're assuming ("Taking that as: you
> want to get past him unseen") and go on.
>
> **2. GATE [D lookup + J scope-read].** Classify each beat:
> - **G0, Question/fact.** The player is asking about the world. Answer from state. If the fact is
>   *unestablished*, and the setting and scene don't decide it, consult the **World-Fact Oracle**
>   (odds chosen first, then d100). `set_fact` the answer before narrating it.
> - **G1, Basic.** The method is one of the fixed **basic verbs** (§4.1). Always legal.
> - **G2, Licensed.** The method needs a license (a granted ability, a class capability, or an
>   established fact: a language, training, a tool, a spell known, an item property), and the
>   character holds one **whose literal scope covers this beat**. If the license covers only part of
>   the beat, split it: the covered part is licensed, and the rest falls back to G1 or G3.
> - **G3, Unlicensed.** Beyond the basic verbs, with no license covering it. **Never narrate the
>   attempt as possible.** Look up the domain's declared `crude_fallback` (a basic verb with a DC
>   shift and a reach cap, or `none`) and its `acquisition_paths`. Offer the fallback as the attempt
>   actually available, and name at least one path to the real capability (P16).
> - **G4, Impossible.** It contradicts an established fact or the setting's physics or metaphysics
>   for *anyone*, **or** the method can't reach the intent (zero reach: the approach can't produce
>   the goal). No roll. Say why in one sentence of fiction and offer the nearest achievable intent or
>   method.
>
> A redirected or declined beat **spends no time or action** unless the player accepts the
> alternative.
>
> **3. NECESSITY [J against criteria].** Roll only if **all three** hold: the outcome is *uncertain*,
> failure *costs* something or changes the situation, and the beat isn't already *riding* on an
> earlier result for the same obstacle and approach (let it ride). Otherwise **say yes**: success at
> Standard reach, no roll. Apply the **Good Idea rule**: if the method uses established facts to
> remove the obstacle's source of uncertainty *and* nothing is actively opposing it, it succeeds
> without a roll.
>
> **4. ANCHOR [J against the library].** For each beat to be rolled, pick the nearest existing rule
> (a basic verb, a licensed ability's own rule, or a named sub-rule from the substrate). Check the
> **ruling ledger** for an earlier ruling with the same anchor and similar deltas; if one exists,
> reuse its numbers. Otherwise adapt the anchor by **at most two knob changes**. More than two means
> re-anchor or split.
>
> **5. FRAME [D given inputs].** Set five values:
> - **Stat**: follows the *method*, not the intent.
> - **DC**: follows the *obstacle*. Read it from the obstacle's stored DC if one exists, else from the
>   DC ladder (§4.2); opposed = 10 + the opposing modifier. Store a new obstacle DC with `set_fact`.
> - **Levers**: named established facts the method exploits. Each is typed *Precision* (+2 to the
>   roll), *Protective* (Stakes −1 step) or *Amplifying* (Reach +1 step). **At most two levers; net
>   roll modifier capped at ±4.** Snags mirror levers.
> - **Stakes**: Safe / Risky / Dire. How bad failure can be.
> - **Reach**: Limited / Standard / Great. How much success can achieve.
>
> **6. OFFER [N + D].** Before rolling, tell the player the frame in fiction plus numbers: the DC
> (or "you need X+ on the die"), the stakes and what failure would cost, and the reach. If 20 +
> modifier + levers < DC, say plainly that **only a natural 20 can succeed, and at best to a plain
> Success**. The player may commit, change method, or withdraw at no cost.
>
> **7. ROLL [D].** `roll_check(d20 + stat + levers vs DC)`. Compute the base degree by margin
> (≥ DC+10 critical success; ≥ DC success; ≤ DC−10 critical failure; else failure), then apply
> **natural 20 → one step better, natural 1 → one step worse**.
>
> **8. READ [D].** Degree × Reach → how much of the intent is delivered. Degree × Stakes → cost.
> On a Failure with margin −1 to −3 (**near miss**), the player may take **success at a cost**: one
> cost from the menu at the frame's stakes severity.
>
> **9. DELIVER [D count + J selection].** For a bundled or multi-intent beat, the degree gates **how
> many** sub-answers or sub-intents are delivered (P17 generalized, §4.5). The **player's own
> priority order** decides which.
>
> **10. CONSEQUENCE [J from a closed menu].** Apply costs only from the **cost menu** (§4.3) at the
> frame's severity. Add the method's own consequences (noise, evidence, reputation), which happen
> whatever the degree. Make sure at least one actionable next step exists (P16). After three
> resolutions in a row with no new lead, introduce one.
>
> **11. RECORD [D].** Write every changed fact, resource, condition and clock with tool calls before
> narrating them. Log the ruling (anchor, deltas, DC, levers, stakes, reach) to the ruling ledger.
> Emit `tag_event` evidence where the moment is significant (P5). Then narrate [N], saying nothing the
> state doesn't hold, and never describing a license doing more than its literal text.

### 4.1 The basic verb tier (VII's "always available" list, and the anchor library's spine)

Principle VII lists move, observe, talk, a basic unskilled attack, and "similarly mundane actions".
The research suggests fixing the tier as a **closed set of verbs, each an anchor with knobs**. The
admission test for the basic tier: *any able-bodied adult in the setting could attempt this with no
training and a real (non-negligible) chance.* The test for licensed: *without training or power, the
untrained person has no real chance or doesn't know how to begin* (the GURPS no-default and PF2e
trained-only criterion).

| Verb | Covers | Typical stat (by method) | Default reach unit | Notes / typical licensed neighbors |
|---|---|---|---|---|
| **Move** | reposition, dash, withdraw, slip through a crowd | Agility | distance/position state | Tumbling *through* an enemy is Move vs. its defense |
| **Observe** | search, study, listen, track by eye | Wits | P17 information units | Reading an unknown script = licensed |
| **Recall** | common knowledge of your origin and culture | Wits | information units | Specialist lore = licensed |
| **Talk** | inform, persuade, deceive, intimidate, bargain, taunt | Presence (method decides) | how far an NPC's disposition/action moves | Needs a shared language, otherwise the fallback is gesture |
| **Strike** | hit with body, weapon or improvised object; shoot; throw | Might / Agility | damage (ch.06) | Weapon *techniques* = licensed |
| **Grapple** | seize, hold, pin, restrain, snatch a held item | Might | condition on target | Includes mounting a large creature |
| **Force** | shove, trip, topple, break, burst, pry | Might | condition or object state | Breaking a lock = Force; picking it = licensed |
| **Exert** | climb, jump, swim, lift, balance, run far | Might / Agility / Endurance | success or position | Improvised tools enter as levers |
| **Evade** | dodge, duck, take cover, get clear of a hazard | Agility | Stakes reduction | The Defy Danger catch-all |
| **Sneak** | hide, move quietly, conceal an object, palm | Agility / Wits | exposure-clock effect | |
| **Handle** | use an object as its nature suggests; crude repair; first aid (stabilize only); calm or lead an animal | Wits / Presence / Agility | object or condition state | Surgery, smithing, lockpicking = licensed |
| **Endure** | resist cold, poison, fear, pain; hold breath; keep going | Endurance / Resolve | avoids a condition | |
| **Setup** | create a lever for yourself or an ally (feint, distract, blind, prepare) | by method | one lever (§4.2) | Fate CaA / Blades setup / Savage Worlds Test / Ironsworn Secure an Advantage |
| **Help** | give your lever to someone else's attempt | by method | one Precision lever | Only if the helper could plausibly do the task alone (5e) |
| **Ready** | hold an action for a trigger | — | — | Reactions per ch.06 |

Fifteen verbs, in line with Fate's four actions plus Dungeon World's eight basic moves, or PF2e's
roughly fifteen basic actions. The list is closed: new content extends *licenses*, not this list
(Principle V). Stat names in this table and in §5 are **illustrative placeholders**; ch.00/02 own the
attribute list.

### 4.2 FRAME numbers (proposed defaults for chapter 01 to adopt or refine)

**DC ladder**, stated by *who could do it* (the PF2e simple-DC and GURPS rung-description method),
so an AI can calibrate by asking "who would hesitate?":

| Tier | DC | Who could do it | Success-or-better at +2 | +4 | +6 |
|---|---|---|---|---|---|
| Trivial | no roll | anyone, in these conditions | — | — | — |
| Easy | 10 | an untrained adult, taking care, usually succeeds | 65% | 75% | 85% |
| Moderate | 15 | needs competence; untrained often fail | 40% | 50% | 60% |
| Hard | 20 | challenges a practiced professional | 15% | 25% | 35% |
| Very hard | 25 | experts often fail | 5% | 5% | 10% |
| Legendary | 30 | the edge of mortal ability; needs levers or licenses | 5%\* | 5%\* | 5%\* |
| Beyond | — | no mortal without a license that changes the category | G4 | G4 | G4 |

\*A natural-20 step-up from Failure. Figures use the recommended step rule; the full distribution is
in §5.9.

**Opposed:** DC = 10 + the opponent's relevant modifier + the opponent's own levers (PF2e). Only the
player rolls. **Social:** DC = 10 + the target's insight/resolve modifier, then disposition: hostile
+5, unfriendly +2, neutral 0, friendly −2, devoted −5 (the PF2e attitude ladder in DC form). **Claim
plausibility** is *not* a DC: *plausible* = no change; *doubtful* = one Snag; *outrageous* = Reach
capped at Limited; *known false to the target* = G4 for the belief intent.

**Levers and snags** (the creativity channel):

| Lever type | What makes a fact this type | Effect | Mirror snag |
|---|---|---|---|
| Precision | lets the method be done *better*: a tool, a blind or distracted target, a running start, a mentor's advice, help | +2 to the roll | −2 |
| Protective | makes failure *less bad*: cover, an escape route, a rope tied off, a clear line of retreat | Stakes −1 step | Stakes +1 step |
| Amplifying | makes success *go further*: a weak spot, overwhelming numbers, a crowd on your side, a magical resonance | Reach +1 step | Reach −1 step |

Rules: (a) a lever **must name a fact** already in state, stated in narration before the declaration,
or created by an earlier beat (Setup). "Cool" is not a fact. (b) **Maximum two levers per roll**
(Cypher's two-asset cap); the net roll modifier from levers and snags is capped at ±4 (PF2e's
circumstance cap). (c) One fact yields at most one lever. (d) The *type* comes from what the fact
does, so it isn't the DM's choice. If a fact honestly fits two types, the player picks.

**Stakes** (Blades position, in our terms):
- **Safe**: failure only means it doesn't happen. You can walk away and try another way.
- **Risky**: failure costs one standard cost.
- **Dire**: failure costs one severe cost. **If any possible cost could kill, the OFFER step must say
  so in plain words** (BRIEF §4: death is telegraphed).

**Reach** (Blades effect):
- **Limited**: part of the intent; one clock tick; information at floor(N/2), minimum 1; an NPC moves
  one disposition step.
- **Standard**: the intent as stated; two ticks; ceil(N/2); an NPC does the reasonable thing asked.
- **Great**: the intent plus a bonus; three ticks; all units; an NPC goes beyond what was asked.
- Set by the Blades effect factors: **potency** (a weakness exploited, magic), **quality** (tools),
  **scale** (numbers and size). A disadvantage in any factor that no lever offsets → Limited.
  Disadvantages in two factors with nothing offsetting → **zero reach**: this method can't reach this
  intent → G4 (redirect).

### 4.3 READ tables (P8 extended with reach and stakes)

**Degree → delivery:**

| Degree | Delivery |
|---|---|
| Critical success | Reach + 1 step (beyond Great = Great plus a free Precision lever on a follow-up) |
| Success | Reach as framed |
| Failure, near miss (−1…−3) | Nothing, **or** (the player's choice) Success at the framed reach plus one cost at stakes severity |
| Failure | Nothing; one cost at stakes severity (Safe: none) |
| Critical failure | Nothing; costs at stakes + 1 step (Safe → one standard cost; Risky → one severe; Dire → one severe plus one standard) |

Near-miss width: margins −1 to −3 are 15% of faces at mid-range DCs (DC 10–20 at mods +2 to +4; §5.9). That raises "success in some
form" from 40% to 55% at the +2/DC 15 baseline, near Blades' risky single-die roll (50% for 4+ on
1d6; 75% on 2d6 take-highest) without erasing failure. The 5e DMG uses −1…−2, and a −1…−5 band (25%)
would make failure feel rare. **−3 is the recommended width**; it goes to open empirical questions
(§7).

**The cost menu** (closed; 9 types; the AI picks a type whose trigger fits the method's fiction, and
if two fit, the one already threatened in the scene):

| Cost | Standard | Severe | Fits when the method... |
|---|---|---|---|
| **Harm** | Vitality loss, "setback" band (ch.07) | "dangerous" band, or an injury condition | is physical and exposed |
| **Drain** | lose 1 Focus / 1 consumable | lose 2 / a valuable consumable | relies on effort or supplies |
| **Gear** | an item is dropped or left behind | an item breaks or is lost | uses a tool or weapon |
| **Time** | a scene clock ticks 1 | ticks 2 | takes time while something else moves |
| **Exposure** | noticed; an alert clock ticks 1 | spotted and identified; alert ticks 2 | involves stealth, lying, noise |
| **Footing** | a condition (off-balance, prone, grabbed) | a worse condition (pinned, surrounded, lost) | involves position |
| **Shortfall** | reach −1 on the delivered result | reach −2 | (success-at-cost only) |
| **Closed door** | this *approach* can't be retried on this obstacle | this approach and this NPC's goodwill | social or one-shot actions |
| **Twist** | a new obstacle enters | a new threat enters | nothing else fits (roll on the ch.12 twist table) |

A cost can't contradict the degree: a success-at-cost still delivers success (Blades: a consequence
never negates a success).

### 4.4 GATE data (the license schema this pipeline needs from chapter 05 and data/)

Each license entry gets these fields, so that G2/G3 are lookups:

```yaml
- id: language_ogrish
  kind: language            # language | ability | class_capability | training | spell | item_property | fact
  grades: [broken, accented, native]   # graded licenses (GURPS comprehension levels)
  scope: "Understand and speak Ogrish at the held grade."
  excludes: ["reading Ogrish glyph-script (separate license)"]
  crude_fallback: { verb: talk, method: "gesture, tone, shared nouns", dc_shift: +5, reach_cap: limited }
  emulate: null             # only for domain licenses: attempt adjacent unknown techniques
  acquisition_paths:
    - { type: project, clock: 8, per: "scene of sustained contact", requires: "an Ogrish speaker present" }
    - { type: teacher, effect: "Amplifying lever on the project" }
    - { type: recognition, via: "P5 tag evidence: lore.languages" }
```

```yaml
- id: arcane_channeling_fire
  kind: class_capability
  scope: "Cast known fire-domain spells, paying their Focus cost."
  excludes: ["spells outside the fire domain", "spells not known"]
  crude_fallback: none      # an untrained person cannot shape fire at all
  emulate: { allowed_for: "witnessed fire-domain spells of castable rank",
             dc_shift: +5, focus_mult: 2, reach_cap: limited,
             crit_fail: "mishap: backlash, standard Harm of the spell's element",
             success_ticks: "learn_<spell> clock (6)" }
  acquisition_paths:
    - { type: recognition, via: "P5 class emergence: arcane.fire" }
    - { type: mentor, requires: "a fire-domain caster willing to teach" }
```

The `emulate` field is 3.5's Use Magic Device and BW's Beginner's Luck brought under VII: only
*holders of the domain license* may try adjacent unknown techniques, at a priced penalty, and success
feeds learning. Non-holders get `crude_fallback` (possibly `none`) plus `acquisition_paths`. This is
the Dungeon World Ritual's "yes, if..." in data form. Two hard rules keep it honest: **a roll never
grants a license** (licenses change only through their acquisition paths, P5 recognition, or item
grants), and **a license does exactly its literal scope**. Anything more is G1/G3 for the excess.

### 4.5 DELIVER: P17 generalized to "graduated delivery"

For any beat with N distinct sub-questions **or** sub-intents:

1. **Deduplicate.** Mutually exclusive alternatives are *one* question ("demon? fey? shade?" = "what
   kind of creature?").
2. **The player ranks** the remaining N (or the DM uses declaration order if the player doesn't).
   This replaces P17's "the DM chooses which": the player's ranking is deterministic and
   player-favoring, and it removes a judgment call that can drift.
3. Delivered count by degree (with Standard reach): **CS all N**; **S ceil(N/2)**; **near-miss
   success-at-cost ceil(N/2)** plus a cost; **F one vague impression** of the top-ranked item, marked
   uncertain; **CF nothing reliable** (optionally one plausible falsehood, which must be minor and
   correctable, per PF2e's guidance). Reach adjusts S by one step: Limited → floor(N/2), minimum 1;
   Great → N−1, minimum 1.
4. **Re-asking** the undelivered items is a new attempt on the *same obstacle*: it needs a new
   lever, a new method, or an accepted cost (Time/Exposure). This is P17's no-free-retry rule plus
   "let it ride".

### 4.6 Compound shapes

- **Sequential beats (linked).** Resolve in order. The earlier beat's degree feeds the later one:
  CS → the later beat gains a Precision or Amplifying lever (player's choice) plus whatever the setup
  was for; S → gains the lever the setup was for; F → the later beat may go ahead without the lever
  at Stakes +1, or be abandoned with no action spent; CF → the later beat can't go ahead as planned,
  and the cost applies. Each beat costs its own actions (ch.06).
- **Repeated act.** Throttle to what the action economy and fiction allow in the time available (P9).
  Each repetition is its own roll with whatever multiple-attack penalty ch.06 defines. **Never raise
  the DC for quantity**: the DC is how hard one instance is, and quantity belongs to the action
  economy or the reach.
- **Conditional ("if X, then Y").** Resolve X (often G0, the Oracle). If X is false, Y is void, no
  time is spent, and the DM says what *is* true (P16).
- **Extended.** A clock named for the *obstacle*. Sizes: 4 (a scene's worth), 6 (complicated),
  8 (daunting), 12 (a long project across downtime). Ticks per roll: CS 3 (4 at Great), S by reach
  (1/2/3), near miss 1 plus a cost, F 0 plus a cost, CF 0 plus a cost, and a paired danger clock ticks
  1. At most one tick-roll per stated interval (per scene, per day), because let it ride applies to
  the interval.

### 4.7 The World-Fact Oracle (G0)

For a fact that is **unestablished** (not in state, not stated in narration) and **not settled by
setting or scene logic**, the DM picks the odds **before** rolling, from the scene's nature, never
from what the player wants:

| Odds | Yes on d100 | Use when |
|---|---|---|
| Certain | no roll | the scene type implies it (a stable has straw) |
| Likely | 26+ (75%) | commonly true of such places or people |
| Even | 51+ (50%) | could go either way |
| Unlikely | 76+ (25%) | uncommon but unremarkable |
| Remote | 91+ (10%) | rare; would be noteworthy |
| Impossible | no roll | contradicts the setting or scene |

Doubles (11, 22, ...) = an *extreme* answer or a twist (Ironsworn's match). `set_fact` the answer at
once. A "no" is followed in the same breath by what *is* there (P16). Odds labels and thresholds
follow Ironsworn's *Ask the Oracle*. The Certain/Impossible no-roll rows and the anti-sycophancy
clause are this project's additions. The Oracle is how the player's freedom to *go looking for*
affordances ("is there a chandelier? loose sand? a back door?") stays both real and fair.

### 4.8 The ruling ledger

After any adapted ruling (step 4 used deltas, or an Oracle, a Good Idea or a G4 decision), write a
ledger row: `{signature: "<anchor>+<delta1>+<delta2>", context, dc, levers, stakes, reach, result,
turn}`. Before framing any new beat, query the ledger by anchor. If an earlier ruling matches,
**reuse its numbers unless a stated fact differs**, and name the difference if you depart from it.
This is PF2e's chandelier/rope-bridge consistency advice, stored as state so it survives the model's
context window. Runtime capability assumed: a queryable key-value store (a `ledger:` namespace on
`set_fact`/`get_state` is enough).

---

## 5. Worked examples: thirteen wild actions through the pipeline

**Illustrative character, Wren** (placeholder numbers; ch.00/02 own the real attribute list):
Might +1, Agility +3, Endurance +1, Wits +2, Presence +2, Resolve +0. Vitality 12/12, Focus 4/4.
Carries a spear, shortbow and 14 arrows, a wool cloak, rations, flint, and a lit torch where noted.
Speaks Common. One license: **Heat Resistance** (passive; illustrative text: *"Damage from fire and
heat is halved, rounded down. You suffer no fatigue from hot environments."*). Die results are shown
as `d20=`. Hazard damage numbers are placeholders for ch.07's bands. Action counts refer to ch.06's
eventual economy.

### Example 1 — "I throw sand in its eyes, then slide under its legs."

*Scene (established):* a ruined courtyard, ankle-deep in grit; a 10-ft ogre (Agility +0, Might +5,
Wits −1) guards the gate behind it.

1. **PARSE.** Intent: get past the ogre to the gate without being clubbed. Two **sequential** beats:
   A = throw grit into its eyes; B = slide between its legs.
2. **GATE.** A = **Setup** (basic). Is there sand? The grit is established in narration → yes, no
   Oracle needed. B = **Move** through an enemy's space (basic).
3. **NECESSITY.** Both uncertain and costly (the club) → roll both.
4. **ANCHOR.** A → Setup with the condition knob set to *Blinded* (this is the SRD example of Fate's
   Create an Advantage; Savage Worlds would call it a Test). B → Move-through-enemy (PF2e's Tumble
   Through). No other deltas. The ledger has no earlier ruling, so a new row will be written.
5. **FRAME A.** Stat Agility +3 (a quick throw). DC = 10 + ogre Agility +0 = **10**. Levers: none.
   Stakes **Risky** (in club reach). Reach Standard = *Blinded* until the end of its next turn (Great =
   two turns).
6. **OFFER.** "You need 7+. If you miss, it's on guard and swinging."
7. **ROLL A.** d20=12 → 15 vs 10 → **Success**. `set_fact(ogre.condition = blinded, until = end of its next turn)`.
8. **FRAME B.** Agility +3, DC 10 + ogre Agility +0 = **10**. Levers: *Blinded* (Precision +2; created
   by beat A) and *Large creature: the gap between its legs* (Precision +2; its size is established)
   → +4, which hits the cap. Stakes Risky. Reach Standard = you end behind it and it gets no reaction.
9. **ROLL B.** d20=4 → 4+3+4 = 11 vs 10 → **Success** (margin +1). `set_fact(wren.position = behind ogre, 20 ft from gate)`.
   *Other branch:* d20=1 → 8 = failure by 2 → natural 1 steps down → **Critical failure**. Risky + 1
   = one severe cost: **Footing (severe)**, pinned under its foot.
10. **CONSEQUENCE.** The method has its own effect whatever the degree: a blinded ogre bellows, which
    is loud, so the gatehouse is alerted (alert clock +1). P16: the gate is 20 ft away, the ogre is
    blind until the end of its next turn, and there's a bar on the gate to lift.
11. **RECORD.** Ledger: `setup+condition:blinded` DC = 10 + target Agility; `move_through+lever:size_gap`.
    Two actions spent (ch.06).

*Why it's fair and consistent:* the creativity paid off twice, but only through *named facts* (grit on
the floor, blindness, size), and it was capped. A player who wrote three flowery paragraphs about it
would get exactly the same numbers.

### Example 2 — "I convince the guard I'm his long-lost brother."

*Scene:* a bored gate guard (Wits +1, disposition neutral). Wren wants into the keep.

1. **PARSE.** Method: a lie (Talk, deceive). Intent isn't stated, so the DM says the assumption:
   "Taking that as: you want him to let you in." One intent.
2. **GATE.** Talk is basic, **but** the lie depends on an **unestablished fact**: does he have a
   long-lost brother? → **G0 Oracle.** Odds are chosen from the world, not the wish: most men don't
   have a vanished brother → **Unlikely (76+)**.
   - **Branch A:** d100=41 → **No.** `set_fact(guard.siblings = two sisters, no brothers)`. The claim is
     now *known false to the target*, so the belief intent has zero reach → **G4 for this intent. No
     roll, no action spent.** The DM redirects: "He has no brother, and he'd know it on sight. You can
     still play it as a drunk's joke to get him talking (easy), or try a different story." The player
     takes the joke and asks when the gate changes guard. **FRAME:** Presence +2, DC 10 + 1 + neutral
     0 = **11**, Stakes **Safe** (worst case he's annoyed), Reach Standard. d20=9 → 11 → **Success**.
     He laughs and tells you the watch changes at the midnight bell. `set_fact(keep.watch_change = midnight)`.
   - **Branch B:** d100=88 → **Yes, and a double**, so an extreme answer: his younger brother vanished
     at sea fifteen years ago, and his mother still lights a candle for him. `set_fact(...)`. The lie is
     now possible but **doubtful** (Wren is about the right age, but the guard remembers a face) →
     one **Snag −2**. FRAME: Presence +2, DC 10 + 1 + 0 = **11**, Stakes **Risky** (being caught
     impersonating his dead brother means Closed door plus arrest), Reach Standard. OFFER: "You need 11+
     with the snag." d20=17 → 17 **Success**. He's shaken and lets you in "to see Mother".
     **Method consequence (independent of success):** a family now believes you're their lost son.
     `set_fact(commitment: the Harlan family believes Wren is Tam Harlan)`, a thread for ch.11.
3. **RECORD.** Ledger: `talk:deceive+claim:doubtful`.

*Why:* the Oracle is what makes this feel free *and* fair. The player's wild idea gets a real
chance, one the AI committed to before looking. A "no" never ends in a wall, because the method is
redirected to the nearest achievable intent (Angry GM: when the approach can't reach the intent,
don't roll). Success brought a consequence that came from the approach, not from the dice.

### Example 3 — "I use my fire resistance to walk through the burning barn and save the horse."

1. **PARSE.** Intent: get the horse out alive. Method: go into the fire, relying on the license. This
   is really an **extended** action with three beats inside a danger clock: find the horse, calm and
   lead it, get out. Danger clock *Roof collapses*: 4 segments, +1 automatically each round.
2. **GATE, literal scope.** Heat Resistance covers **fire and heat damage (halved)** and heat fatigue.
   It does **not** cover smoke (suffocation isn't heat), falling beams (impact) or the horse. So:
   flame damage is licensed and halved; smoke, beams and the horse fall to basic verbs (Endure, Evade,
   Handle). The DM must not narrate "the flames part around you" or "you breathe the smoke easily".
   That's exactly the embellishment the probe caught.
3. **FRAME and OFFER (Dire, so a lethal telegraph):** "This can kill you. Inside, the flames deal 3 a
   round; your resistance makes it 1. The smoke isn't heat, and your resistance does nothing for it:
   Endurance DC 15 each round inside or you take 2 and start choking. The roof has maybe four rounds."
   The player commits.
4. **Round 1: find the horse.** Observe (Wits +2), DC **15**, Snag: smoke −2. d20=14 → 14 → **Failure,
   margin −1: near miss.** The player takes success at a cost: **Time** (roof +1). Flames: 1 →
   Vitality 11. Smoke: Endure d20=16+1 = 17 ✓. Roof: 1 automatic + 1 cost = **2/4**.
5. **Round 2: calm and lead the horse.** Handle (Presence +2). A panicked animal: DC 10 + 0 + 5
   (hostile/panicked) = **15**. Lever: *throw my cloak over its eyes* (a possession) → Precision +2.
   d20=11 → 15 → **Success**. Flames 1 → V 10. Smoke: d20=6+1 = 7 ✗ → Harm 2 → V 8, and **Choking**
   (−2 on rolls while in smoke). Roof **3/4**.
6. **Round 3: get out.** Evade the falling beams (Agility +3), DC **15**, Snag: Choking −2. d20=15 →
   16 → **Success**. Flames 1 → V 7. You're out and the roof comes down behind you (4/4).
7. **RECORD.** `update_resource(vitality 12→7)`, `set_fact(horse = rescued)`, `set_fact(wren.condition
   = choking, clears after a scene in fresh air)`, `tag_event(rescue, courage)`.

*What the license was worth:* without it, the flames alone would have done 3 × 3 = 9, plus 2 from
the smoke = 11, leaving Wren at 1 Vitality. The license made the plan *survivable*, not *free*, and
the player knew that before committing.

### Example 4 — "I try to learn the ogres' language by listening to them."

1. **PARSE.** Two intents at two timescales: (a) understand *what they're saying right now*;
   (b) *learn the language*, which is acquiring a license.
2. **GATE.** (b) is a license (`language_ogrish`). **A roll never grants a license** (§4.4), so it's
   redirected to the license's `acquisition_paths`: an 8-segment **project clock** needing sustained
   contact. (a) Understanding speech without the license is G3. The license's `crude_fallback` for
   *listening* is **Observe**: reading tone, gesture and context, with information limited to what
   those can carry.
3. **(a) FRAME.** Observe, Wits +2, DC **15** (reading an unfamiliar tongue by its music needs
   competence), Stakes Risky (you're hiding close by). The player asks three questions and ranks them:
   (1) are they talking about me? (2) are they angry? (3) how many more are coming? d20=13 → 15 →
   **Success** → ceil(3/2) = **2 answers**, the top two: yes, one keeps pointing at your hiding
   cave; one is angry and the other amused. Question 3 stays **unresolved, not wrong** (P17).
4. **(b) PROJECT.** Clock `learn_ogrish (broken)`, 8 segments. One roll per scene of sustained contact
   (Wits +2 vs DC 15). Ticks: CS 3, S 2, near miss 1 plus a cost, F 0 plus a cost. A willing teacher
   would be an Amplifying lever (+1 reach step, so S = 3 ticks). Across four later scenes: d20=16 → 18
   S (+2); d20=7 → 9 F (0; cost **Exposure**: they catch you eavesdropping, which becomes a new scene);
   d20=19 → 21 S (+2); d20=20 → 22, margin +7 = Success, natural 20 steps up to **CS** (+3) → **7/8**.
   The next Success fills it: `grant_ability(language_ogrish, grade = broken)` +
   `tag_event(lore.languages)`. The *broken* grade's scope is simple concrete talk. Nuance is a Snag −2,
   and the *accented* grade is a new 12-segment clock.

*Why:* GURPS's graded comprehension, Blades' long-term projects, and BW's learning by doing, all kept
inside VII: the attempt was never refused, it just ran at its honest timescale.

### Example 5 — "I pole-vault over the wall using my spear."

*Scene:* a nine-foot fieldstone wall (established); a patrol clock at 2/4; a 7-ft spear.

1. **PARSE.** Intent: get over the wall *before the patrol comes round*. Method: a vault.
2. **GATE.** Exert (jump) is basic. The spear is a **tool**, so it's a lever, not a license.
3. **ANCHOR.** Exert-jump. Unaided, "jump a 9-ft wall" is **Beyond** (G4: no one standing-jumps
   nine feet). The spear changes *which obstacle* is being faced: "vault 9 ft on a rigid 7-ft pole"
   is **Hard, DC 20**. Knob changes: (1) the DC tier is re-derived for the new method-obstacle
   pairing, (2) Gear risk is added to the cost menu. That's two knobs, which is allowed.
4. **FRAME.** Agility +3 (a vault is coordination). Lever: *open ground for a running start*
   (established) → Precision +2. Stakes Risky (a 9-ft fall, a snapped spear). Reach Standard: you
   land on your feet on the far side.
5. **OFFER, with the alternative shown.** "Vault: you need 15+ (30%). A miss means a fall or a snapped
   spear. Or climb: DC 15, Might +1, you need 14+ (35%), but it takes two rounds, the patrol clock
   ticks twice, and they'd round the corner on you." The player vaults.
6. **ROLL.** d20=14 → 14+3+2 = 19 vs 20 → **Failure, margin −1: near miss.** The player takes success at
   a cost. The method fits **Gear**, so: you clear the wall, but the spear is left leaning on the
   *outside*. `set_fact(spear.location = outside north wall)`.
7. **CONSEQUENCE.** A spear against the wall is evidence. When the patrol clock fills, it's found
   (Exposure later). The player now has a follow-up problem rather than a dead end (P16).

*Why:* the creative method wasn't rewarded or penalized for being unusual. It faced a *different*
obstacle with an honest DC, and the player chose between two open options knowing the tradeoffs
(7th Sea/BW commitment before the roll).

### Example 6 — "I try to cast the spell I saw the hedge-witch cast."

**Case A: Wren, no arcane license.**
1. **GATE.** Casting is a licensed domain. Wren holds no arcane license → **G3**. The arcane domain's
   `crude_fallback` is **none**: an untrained person can't shape fire at all.
2. **Redirect, no action spent:** "You mouth the words and trace the gesture. Nothing answers; there's
   no spark in you to catch. What you *can* do is fix what you saw in memory before it fades." That
   makes it **Observe/Recall**, bundled N = 3 and ranked by the player: (1) the gestures, (2) the
   words, (3) what it cost her. Wits +2 vs DC 15, Stakes Safe. d20=17 → 19 → **Success** → 2 answers.
   `set_fact(wren.witnessed_spell.kindle = {gestures, words})`.
3. **Path (P16):** the hedge-witch is alive and in the village (a *mentor* path), and P5 recognition
   is the other path. `tag_event(arcane.fire, curiosity)`.

**Case B: a caster, Ash (holds `arcane_channeling_fire`; Wits +3; Focus 4), who witnessed an enemy
cast *Flame Whip* (fire domain, a castable rank).**
1. **GATE.** Ash holds the domain license, but *Flame Whip* isn't a known spell. It's within
   `emulate.allowed_for` → allowed as an **emulation**. (Had it been *Frost Lance*, outside the fire
   domain, it would be excluded → G3, fallback none.)
2. **FRAME.** The spell's base casting DC is 15, +5 for emulation = **20**. Focus cost 2 × 2 = **4**
   (all of Ash's Focus), spent whether or not it works. Reach **capped at Limited** (one lash at
   reduced effect: Dungeon World's "a lesser version, unreliable and limited"). A critical failure is a
   **mishap** (backlash: standard fire Harm, from 3.5's Use Magic Device).
3. **OFFER.** "You need 17+. It'll drain you completely. Best case, one weak lash."
4. **ROLL.** d20=16 → 19 vs 20 → **near miss**. Drain is already maxed out, so the fitting cost is
   **Harm** (standard): a backlash burn of 2. The whip lashes once at Limited reach.
   `update_resource(focus 4→0; vitality −2)`. Tick `learn_flame_whip` (6 segments) by reach: Limited
   = **1 tick**.

*Why:* VII holds absolutely for non-holders. Nothing was narrated into existence, yet the player
still got a concrete next step. Holders get Burning Wheel's "attempting teaches you", priced so it
never beats actually knowing the spell.

### Example 7 — "I shoot it ten more times" (the probe's turn 13, re-ruled)

*Original ruling:* one roll at DC 25; 16+2 = 18 → Failure. Under the old nat-20 rule that was a 5%
chance of anything.
1. **PARSE.** A **repeated** act, ×10.
2. **Throttle, not DC.** The fiction gives about one round before the cultists close (established).
   With an illustrative PF2e-shaped 3-action round and an illustrative multiple-attack penalty of
   0/−5/−10 (ch.06 owns the real numbers), that's **3 shots at most**. DC stays the creature's defense,
   **16**.
3. **OFFER.** "Three shots before they're on you: you need 14+ (35%), then 19+ (10%), then only a
   natural 20 (5%). Or two shots and use your third action to back toward the trees (a Protective
   lever next round)."
4. **Math.** P(at least one hit) = 1 − 0.65 × 0.90 × 0.95 = **44%**, against the original ruling's
   5%. The original ruling wasn't *lenient*. It was **nine times harsher than the fiction
   justified**, because it treated quantity as difficulty.

### Example 8 — "Is it a demon, fey, or shade? Does it have a weakness? Is it intelligent?" (probe turn 10, re-ruled)

1. **DELIVER step 1, dedupe:** "demon / fey / shade" are mutually exclusive → one question, *what kind
   of creature?* So N = 3.
2. **Player ranks:** (1) weakness, (2) intelligent?, (3) what kind.
3. **FRAME.** Observe from the canopy, probe modifier +2, DC **16** (stored as the obstacle's DC),
   Stakes Risky (close enough to be sensed).
4. **ROLL.** d20=13 → 15 → **Failure, margin −1: near miss.** Two legal readings, the player's choice:
   - Take the Failure: **one vague impression** of the top-ranked question, marked uncertain: "the
     cultists keep the silver chain well away from it... maybe that matters."
   - Take success at a cost: **ceil(3/2) = 2 answers** (weakness: silver; intelligent: yes, it's
     directing the cultists), plus **Exposure (standard)**: its head turns toward the canopy (alert
     clock +1).
5. Asking "what kind?" again needs a new method or lever (let it ride / P17 no-free-retry). In the
   probe, the same roll gave **zero** information on all five questions.

### Example 9 — "I shoot the chandelier rope so it drops on the bandit captain."

*Scene (established):* an iron wagon-wheel chandelier hangs over the long table where the captain
stands.
1. **GATE.** Strike at an object (basic). The chandelier and the captain's position are both
   established, so there's no Oracle.
2. **ANCHOR.** Strike, with two knobs: target = a **rope** (a small target at range → Hard, DC 20),
   and damage = **environmental hazard** (heavy falling object: ch.07's "dangerous" band) *instead of*
   arrow damage (5e's improvised-damage table; Feng Shui's "unconventional attacks are just attacks").
   The captain is under it, so there's no separate hit roll. The DC is the higher of the rope's 20 and
   the captain's defense (10 + Agility +2 = 12) = **20**.
3. **Beyond damage:** *pinned under the wheel* is an effect beyond damage (Feng Shui's stunt line),
   available only at **Great** reach, which here means only on a critical success.
4. **OFFER.** "You need 17+ (20%). Shooting *him* directly would be DC 12: you'd need 9+ (60%), for
   arrow damage. Risky: a miss announces you."
5. **ROLL.** d20=18 → 21 → **Success** (margin +1): the rope parts, the wheel crashes onto him
   (dangerous-band damage), no pin. **Method consequence:** the table collapses and the whole hall is
   up (alert clock +2, a consequence of the method, not a cost). Ledger: `strike:object+damage:hazard`.

*Why:* the player **traded odds for impact**, which is an honest, visible choice, not a free upgrade.

### Example 10 — "I play dead so the wolves lose interest."

1. **GATE.** Deceiving by body is basic, **but can the method reach the intent?** Against a hungry
   pack (scale: four wolves; potency: hunger), a motionless body is *food*. Two factors against,
   nothing offsetting → **zero reach → G4 for this intent**. No roll, no action spent.
2. **Redirect (P16):** "Wolves eat the dead. What works on wolves: look big and loud with your torch,
   get up the pine, or throw them your rations."
3. The player intimidates with the torch. **FRAME:** Presence +2, DC 10 + pack Resolve +1 +
   unfriendly (hungry) +2 = **13**. Lever: *lit torch* (established) → Precision +2. Stakes Risky.
   Reach Standard (they withdraw).
4. **ROLL.** d20=9 → 13 → **Success.** They pull back to the treeline. Standard, not Great, so they
   *shadow* you: the danger clock *The pack* stays at 1/4, and the next step is obvious.

### Example 11 — "I ask the river to calm down so I can cross."

1. **GATE, G0 first.** In the setting (ch.13 to confirm), spirits of place exist but are rare. Is
   there a spirit in *this* river? Unestablished → Oracle, **Unlikely (76+)**.
2. d100=62 → **No.** `set_fact(river_ash.spirit = none)`. Talking to a river with nobody in it is
   **G4**. "It's only water, fast and cold. Downstream the banks widen over a gravel bar." (That's a
   lead. If a ford hasn't been established, it's itself an Oracle question, *Likely* on a lowland
   river.)
3. *Other branch:* d100=83 → **Yes** (Unlikely needs 76+).
   A spirit exists → Talk is basic. Social DC = 10 + spirit Resolve +4 + unfriendly +2 = **16**.
   Calming a river is past mortal speech's Standard reach → **Reach capped at Limited** (a short calm
   stretch, for a while). The spirit may want something back (the Dungeon World Ritual's "first you
   must...").

### Example 12 — "I use my heat resistance to cool the forge so we can grab the ingot."

1. **GATE, literal scope.** Heat Resistance *reduces heat damage to you*. It doesn't emit cold or
   affect objects. "Cool the forge" is outside the license's scope → **G3 for that method**.
2. **Redirect, including the reinterpretation that *is* in scope:** "Your resistance won't cool
   anything, but it will let you reach in. Grabbing the ingot bare-handed from the coals is 4 heat; to
   you it's 2. Or quench the coals from the trough (two rounds)." The player reaches in.
3. **NECESSITY.** Grabbing an ingot is not uncertain, and the cost is automatic → **no roll**; the
   damage is simply applied. `update_resource(vitality −2)`, `set_fact(ingot = held)`.

*Why:* this is the anti-embellishment rule (the probe's cold-vulnerability finding) turned into a
procedure. The license is read literally, and the *creative use that fits the literal text* is
honored with no roll at all.

### Example 13 — "Is there a back door? If so, I slip out while the thugs argue."

1. **PARSE.** A **conditional**: X = back door (G0), Y = sneak out.
2. **Oracle.** An inn with a kitchen → **Likely (26+)**. d100=34 → **Yes**: the kitchen door opens on
   the alley. `set_fact`.
3. **FRAME Y.** Sneak, Agility +3, DC 10 + thugs' best Wits +1 = **11**. Lever: *they're arguing*
   (established) → Precision +2. Stakes Risky (Exposure). **Let it ride:** one roll covers crossing
   the common room and the kitchen unless something changes. d20=6 → 11 → **Success**: out into the
   alley.
4. *Other branch:* d100=22 → **No**, and a double, so an extreme answer: the kitchen door is bricked
   shut. Y is void, **no time spent**, and the DM leads with what *is* true (P16): the privy window off
   the back corridor.

### 5.9 Odds reference (exhaustive d20 enumeration; `scratchpad/odds.py`)

Percentages for Critical success / Success / Failure (of which near-miss −1…−3) / Critical failure.
"Current" = BRIEF §7's rule (nat 20 = crit success; nat 1 = crit failure). "Step" = the recommended
PF2e rule (nat 20/1 move the degree one step).

| Mod | DC | Current CS/S/F/CF | Step CS/S/F/CF | Differences |
|---|---|---|---|---|
| +2 | 10 | 15/50/30/5 | 15/50/30/5 | — |
| +2 | 15 | 5/35/45/15 | 5/35/45/15 | — |
| +2 | 20 | 5/10/45/40 | 5/10/45/40 | — |
| +2 | 25 | 5/0/30/65 | 0/5/30/65 | nat 20 is a plain Success, not a crit |
| +2 | 30 | 5/0/5/90 | 0/5/5/90 | same |
| +6 | 10 | 35/50/10/5 | 35/50/10/5 | identical here; once 1 + mod ≥ DC (e.g., +9 vs DC 10), Current makes a nat 1 a CF even though the total succeeds, while Step makes it a Failure |

Near-miss (−1…−3) share under Step: 15% at DC 10–20 for mods +2 and +4; 10–15% at +6; 0–15% at DC 25 (where the band runs into the natural-20 face).
The differences are small in frequency but big in meaning. The current rule turns every roll into
a 5% chance of a *critical* miracle, and for high-modifier characters it turns easy tasks into 5%
disasters. Under the step rule, "only a natural 20" leads at best to a plain Success, which is the
honest message for §4 OFFER.

---

## 6. Edge cases and adaptation anchors (for chapter 12)

- **The player argues for a lever.** The test is *name the fact*. If the fact exists in state or
  prior narration, the lever stands. If the player is proposing a *new* fact ("surely there's a
  rope"), that's G0: an Oracle question, answered before framing.
- **The player asks "can I try X?" out of character.** Run GATE and FRAME, then OFFER. Asking costs
  nothing (7th Sea and Burning Wheel commitment). This is the main tool for building felt freedom:
  the player learns the odds before committing.
- **Stacking levers by splitting one fact** ("the torch is bright *and* hot *and* scary"). One fact
  yields one lever (§4.2c).
- **A license doesn't quite fit.** Split the beat by literal scope (Examples 3 and 12). Never stretch
  the license, and never deny the part it does cover.
- **Many unrelated intents in one sentence** ("I bribe the magistrate, ask about the caravan and
  steal his seal"): PARSE splits them. Different methods are different beats, and each gets its own
  roll and its own action cost.
- **The same idea again after failing.** Let it ride: a new roll needs a changed circumstance, a new
  lever, a new method or an accepted cost. Otherwise the failure stands (YZE no-retry, the
  Alexandrian).
- **A player keeps fishing with the Oracle** ("is there a ballista? a dragon egg?"). Odds come from the
  scene, so absurd fishing gets *Remote* or *Impossible* by the criteria. Each Oracle yes is a
  `set_fact` the world keeps, so the world fills in consistently rather than bending.
- **The DM wants a complication that no roll produced.** Only three triggers are legal: P16's
  three-inconclusive-results rule, a clock filling, or a method consequence. That's our deterministic
  stand-in for the Cypher intrusion.

---

## 7. Implications for BRIEF.md, the constitution, and chapter owners

**7.1 Things in BRIEF/constitution the research says should change** (with evidence):

1. **Natural 20/1 (BRIEF §7).** Replace "critical success on a natural 20 / critical failure on a
   natural 1" with PF2e's **one-step shift**. The current rule gives every roll a 5% *critical*
   miracle (it pushes permissive outcomes in exactly the direction VII guards against). For modifiers
   of +8 or more it also makes certain successes into 5% critical failures. §5.9.
2. **DC ladder vs. default +2 (BRIEF §7).** "Moderate DC 15" succeeds 40% of the time at +2, and "hard
   DC 20" 15%. The ladder's names promise more than the math gives. Chapter 01 should either
   recalibrate the ladder by *who could do it* (§4.2) with a clear expected-modifier band (e.g., +2
   untrained, +4 practiced, +6 expert), or rename the rungs. The probe's DCs 15–17 with +2 fit the
   observed 5/10 success rate only because the rolls ran hot (mean d20 = 14.5 across the 10 rolls, against an expected 10.5).
3. **Constitution P17: generalize and hand the choice to the player.** (a) Extend graduated reveal
   from *information* to **any compound intent** ("graduated delivery"). (b) Replace "the DM's choice
   of which half" with the **player's ranking**, which is deterministic, player-favoring, and removes
   a judgment that can drift. (c) Add the dedupe step (mutually exclusive alternatives count as one
   question). Blades' effect-graded information and Dungeon World's question counts independently
   confirm the shape.
4. **Constitution VII: make "redirect" a lookup.** Add that the basic tier is a **closed verb list**
   (§4.1), that every license declares **`crude_fallback`** and **`acquisition_paths`**, that
   **licenses are read literally** (the probe's embellishment finding), that **rolls never grant
   licenses**, and that an "established narrative fact" license must exist *in state before the
   attempt* (or come from the Oracle). This follows DW Ritual, GURPS no-default, PF2e trained-only
   and 3.5 UMD.
5. **New pattern candidate: World-Fact Oracle.** Unestablished world facts are settled by odds
   committed before a d100 roll, not by DM fiat. It addresses sycophantic drift (the permissive
   failure documented in arXiv 2502.19519) and is standard in solo play (Mythic, Ironsworn).
6. **New pattern candidate: Ruling Ledger / precedent as state** (PF2e GM Core consistency advice +
   P13 externalized state). The P3 reach-and-adapt move becomes *repeatable*.
7. **P3 authoring standard:** adopt §3.4's seven anchor properties and the **two-knob adaptation
   limit** as the test for whether a substrate rule is a good analogical anchor.
8. **P8 extension:** keep the four degrees, add the **near-miss success-at-cost** option (−1…−3,
   player's choice) and the **stakes/reach dials** (Blades) as set-before-the-roll inputs. The
   four-degree spine stays deterministic.
9. **BRIEF §7's reading of the probe's turn 13** calls the DC-25 throttle a positive improvisation.
   The research says the *throttling* was right but the *DC raise* was wrong: quantity belongs to the
   action economy, not difficulty (Example 7: the ruling was about 9× harsher than the fiction
   justified). Worth recording so chapter 06 doesn't copy it.

**7.2 Interface requests** (for the orchestrator to route):
- **ch.00:** the attribute list (examples here use placeholders); the `ledger:` namespace; a d100
  `roll_oracle` or `roll_check` mode; a clock store (create/tick/read).
- **ch.05/data:** license schema fields `scope`, `excludes`, `crude_fallback`, `emulate`,
  `acquisition_paths`, `grades` (§4.4).
- **ch.06:** the action economy and multiple-attack penalty (Examples 1 and 7 use placeholders);
  reactions for Ready.
- **ch.07:** hazard damage bands (setback / dangerous / deadly, as in 5e's DMG) for the cost menu and
  environmental attacks; condition list (Choking, Blinded, Pinned...).
- **ch.12:** the twist table used by the cost menu's *Twist* row; the OFFER script; P16 triggers.
- **ch.13:** setting canon on what exists (spirits of place, etc.), because the Oracle's
  *Impossible* row depends on it.

**7.3 Open empirical questions (each with a named test; defaults ship regardless):**
- *Near-miss width* (default −1…−3). **Test NM-1:** run 3 probe sessions each at −2, −3 and −5, and
  record the player's "felt fair" rating per roll and the soft-lock rate. Pick the widest band that
  doesn't lower the rating of plain Failures.
- *Lever cap* (default 2 levers, ±4). **Test LV-1:** a 50-action creative-play probe logging how
  often players hit the cap and whether AI lever naming stays consistent across repeated identical
  scenes (the target is ≥ 90% agreement).
- *Oracle bias.* **Test OR-1:** present 40 identical scenes, varying only how much the player
  *wants* the fact, and check that the chosen odds don't move (the target is zero movement).
- *Anchor agreement.* **Test AN-1:** give 30 wild declarations to three independent runs of the DM
  model and measure agreement on gate class, anchor and DC tier (the target is ≥ 80% on gate and
  anchor, ≥ 70% on DC tier). Disagreements go into the ledger seed as precedents.

---

## 8. Sources

**Fate** — Four Actions: https://fate-srd.com/fate-core/four-actions · Taking Action, Dice & the
Ladder: https://fate-srd.com/fate-core/taking-action-dice-ladder · Invoking & Compelling:
https://fate-srd.com/fate-core/invoking-compelling-aspects · Advantages in a Conflict (sand/salt
example): https://fate-srd.com/fate-core/advantages-conflict · Aspects & Fate Points (aspects are
always true; permissions): https://fate-srd.com/fate-condensed/aspects-and-fate-points · Challenges,
Conflicts & Contests: https://fate-srd.com/fate-condensed/challenges-conflicts-and-contests · Bronze
Rule: https://fate-srd.com/fate-system-toolkit/bronze-rule · Extras (permissions & costs):
https://fate-srd.com/fate-core/extras · Toolkit Magic: https://fate-srd.com/fate-system-toolkit/magic
· Running the Game: https://fate-srd.com/fate-core/running-game · Succeed at a Cost (secondary):
https://www.worldanvil.com/w/fate-core-moose2181/a/succeed-at-a-cost--article · FAE approaches:
https://fatesrdbrasil.github.io/fate-srd/fate-accelerated/how-do-stuff-outcomes-actions-and-approaches/

**Blades in the Dark** — Action Roll: https://bladesinthedark.com/action-roll · Setting Position &
Effect: https://bladesinthedark.com/setting-position-effect · Effect: https://bladesinthedark.com/effect
· Consequences & Harm: https://bladesinthedark.com/consequences-harm · Progress Clocks:
https://bladesinthedark.com/progress-clocks · Teamwork: https://bladesinthedark.com/teamwork ·
Gathering Information: https://bladesinthedark.com/gathering-information · Alexandrian cheat sheet:
https://www.thealexandrian.net/creations/bladesinthedark/bladesinthedark-cheat-sheet-v3.pdf

**PbtA / Dungeon World** — DW Gamemastering: https://www.dungeonworldsrd.com/gamemastering/ · DW
Playing the Game: https://www.dungeonworldsrd.com/playing-the-game/ · DW Wizard (Ritual):
https://www.dungeonworldsrd.com/classes/wizard/ · Defy Danger: https://a-dungeon-world.fandom.com/wiki/Defy_Danger
· Discern Realities: https://www.dungeonworldtoolkit.com/playermove.php?moveid=7 · Apocalypse World
writeup: https://writeups.letsyouandhimfight.com/evil-mastermind/apocalypse-world/ · Ask provocative
questions: http://daily-apocalypse.com/daily-apocalypse/44-ask-provocative-questions-and-build-on-the-answers
· Baker, Powered by the Apocalypse: https://lumpley.games/2019/12/30/powered-by-the-apocalypse-part-1/

**Ironsworn** — SRD: https://tedtschopp.github.io/Ironsworn-SRD/Ironsworn%20SRD.html · Face Danger:
https://ironsworn-rpg.fandom.com/wiki/Face_Danger · Secure an Advantage:
https://ironsworn-rpg.fandom.com/wiki/Secure_an_Advantage · Ask the Oracle:
https://ironsworn-rpg.fandom.com/wiki/Ask_the_Oracle · Challenge Ranks:
https://ironsworn-rpg.fandom.com/wiki/Challenge_Ranks

**Cypher** — How to Play: https://screwtapello.gitlab.io/cypher-system-reference/how-to-play.html ·
Running the Cypher System: https://cyphersrd.quest/05-game-mastering/04-running-the-cypher-system/ ·
OG-CSRD: https://callmepartario.github.io/og-csrd/

**Savage Worlds** — Rules summary: https://samhaine.wordpress.com/2020/04/06/savage-worlds-rules-summary/
· Distracted/Vulnerable ruling: https://www.pegforum.com/forum/savage-worlds/official-answers-on-core-rules/37475-distraction-and-vulnerable

**D&D** — Basic Rules, Using Ability Scores: https://www.dndbeyond.com/sources/basic-rules/using-ability-scores
· 5e SRD ability checks: https://5e.d20srd.org/srd/skills/abilityChecks.htm · DMG Resolution &
Consequences (discussion): https://www.enworld.org/threads/dmg-242-resolution-and-consequences-suggestion.550546/
· Improvised damage (DMG p.249, secondary): https://makeaskillcheck.com/5e-improvised-damage/ · 3.5
Use Magic Device: https://www.d20srd.org/srd/skills/useMagicDevice.htm

**Pathfinder 2e** — Adjudicating Rules: https://2e.aonprd.com/Rules.aspx?ID=2497 · Difficulty
Classes: https://2e.aonprd.com/Rules.aspx?ID=2627 · Simple DCs: https://2e.aonprd.com/Rules.aspx?ID=2628
· Improvisation: https://2e.aonprd.com/Rules.aspx?ID=2486 · Adjudicating Actions:
https://2e.aonprd.com/Rules.aspx?ID=2551 · Degree of Success: https://2e.aonprd.com/Rules.aspx?ID=2286

**GURPS** — Task Difficulty Modifier: https://gurps.fandom.com/wiki/Task_Difficulty_Modifier ·
Techniques: https://gurpswiki.wikidot.com/ind:techniques · Skills: https://gurps.fandom.com/wiki/Skills

**Genesys** — https://writeups.letsyouandhimfight.com/citizenkeen/genesys/ ·
https://cannibalhalflinggaming.com/2020/09/16/genesys-in-depth/

**Mythic GME** — https://www.wordmillgames.com/page/mythic-gme.html ·
https://wispsoftime.com/content/rolling-solo-chapter-6-part-mythic-game-master-emulator/ · Oracle in
D&D discussion: https://www.enworld.org/threads/why-im-introducing-the-oracle-to-my-d-d-game-and-reducing-my-own-dm-authority.695320/

**Year Zero Engine** — https://callmepartario.github.io/og-yzesrd/ ·
https://freeleaguepublishing.com/wp-content/uploads/2023/11/YZE-Standard-Reference-Document.pdf

**Burning Wheel** — Procedure guide: http://questingblog.com/wp-content/uploads/2015/02/Burning-Wheel-Procedural-Guide-V2.pdf
· https://pastebin.com/sWJuhvbD · Let it ride: https://forums.burningwheel.com/t/letting-it-ride-example/15700
· Beginner's luck: https://forums.burningwheel.com/t/practice-and-beginners-luck/14033

**Mouse Guard / Torchbearer** — https://mythcreants.com/blog/why-mouse-guard-handles-failure-better-than-any-other-rpg/
· https://forum.rpg.net/threads/help-me-understand-torchbearer.708772/ ·
https://firebroadside.blogspot.com/2018/07/a-mouse-guard-and-torchbearer-primer.html

**Heart** — https://writeups.letsyouandhimfight.com/lazyangel/heart-the-city-beneath/ · **Troika!** —
https://www.rpg.net/reviews/archive/17/17763.phtml · **13th Age** — https://www.13thagesrd.com/running-the-game/
· https://pelgranepress.com/2013/05/24/13th-age-backgrounds/ · **7th Sea 2e** —
https://walkingmind.evilhat.com/2016/08/16/reading-7th-sea-second-edition/ ·
https://andrewjluther.com/2018/09/02/the-7th-sea-2e-risk-system/ · **Exalted** —
https://wiki.rpg.net/index.php/Exalted_Stunts · **Wushu** —
https://danielbayn.com/wushu/playing-the-game/index.shtml · **Feng Shui 2** —
https://thealexandrian.net/wordpress/44775/roleplaying-games/so-you-want-to-be-a-feng-shui-player-part-2
· **Dogs in the Vineyard** — https://en.wikipedia.org/wiki/Dogs_in_the_Vineyard ·
https://gnomestew.com/a-look-at-dogs-in-the-vineyard/

**OSR and GM craft** — Principia Apocrypha: https://lithyscaphe.blogspot.com/p/principia-apocrypha.html ·
The Alexandrian, Art of Rulings (intention & method):
https://thealexandrian.net/wordpress/37960/roleplaying-games/art-of-rulings-part-2-intention-and-method
· Let It Ride: https://thealexandrian.net/wordpress/38313/roleplaying-games/the-art-of-rulings-part-8-let-it-ride
· GM Don't List #2: https://thealexandrian.net/wordpress/38798/roleplaying-games/gm-dont-list-2-rolling-to-failure
· The Angry GM, Adjudicate Actions: https://theangrygm.com/adjudicate-actions-like-a-boss/

**AI GM research** — Static vs. Agentic GM AI: https://arxiv.org/html/2502.19519v2 · Orchestrated
Reality: https://arxiv.org/abs/2606.16014 · CALYPSO: https://arxiv.org/pdf/2308.07540 · LLMs and
Games survey: https://arxiv.org/html/2402.18659

**Project sources** — `.specify/memory/constitution.md` (VII, P3, P8, P16, P17);
`rules/_process/BRIEF.md`; `specs/001-action-resolution-probe/probe-results.md`;
`research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md`;
`research_notes/Emergent power acquisition mechanisms/freeform_combat_positioning.md`.
