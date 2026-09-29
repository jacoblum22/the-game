<!--
Sync Impact Report
Version change: 1.4.0 → 1.5.0 (MINOR: resolves Principle III's long-open TODO)
Modified principles:
  - III. Rule Flexibility Within Bounds — retitled from "(Deferred Mechanism)" to "(Base-Model
    Judgment by Default)". RESOLVED: default is the narrating AI's own judgment constrained by
    P12/P16/P17; no judge-gate (Jev or otherwise) is adopted now. This is an explicit default
    pending observed failure, not a claim that judgment is proven sufficient — a single probe
    session cannot establish that either way. TODO(RULE_OVERRIDE_MECHANISM) is closed and
    replaced with a concrete revisit trigger: adopt a gate only once sustained real play (not
    a short probe) surfaces a recorded, concrete failure case.
Version change (prior): 1.3.0 → 1.4.0 (MINOR: first live probe session — adds P16 and P17,
  extends P13 with an empirical finding)
Added patterns:
  - P16. Always Leave an Actionable Next Step (No Silent Dead Ends)
  - P17. Graduated Information Reveal for Compound Queries
Modified patterns:
  - P13 (AI Game Master Architecture) — added a first empirical data point (an unearned
    pronoun the DM's own self-assessment failed to catch) directly supporting the
    independent-verification requirement, rather than resting solely on external research.
Research/evidence basis: results of specs/001-action-resolution-probe/probe-results.md, the
  project's first live test of an AI DM (13 turns, 10 resolved actions, run via a Haiku
  subagent with the project owner playing in real time). Mechanical resolution/state tracking
  (P8/P13's core claim) held up with zero contradictions; the two new patterns below capture
  the DM-craft and resolution-granularity gaps that surfaced instead. Per that report's scope
  caveats, this was a relayed-chat test, not the actual tool-calling/externalized-state/judge-
  gate architecture — P13's core claims remain otherwise untested at that level.
Version change (prior): 1.2.0 → 1.3.0 (MINOR: fourth research pass — WoW/MMORPG/PoE2 — amends
  Principle VI and Pattern P3, extends P6, adds P14 and P15)
Modified principles:
  - VI. Mandatory Consolidation of Aging Content — added a provisional-by-default
    ("league-style trial window") path as the preferred consolidation mechanism, plus an
    explicit requirement to distinguish numeric rescaling (a squish, which retires nothing)
    from structural retirement (which this principle actually requires), plus a requirement
    to budget for the documented player-retention cost of large-scale reworks.
Modified patterns:
  - P3 (Granular State Is Not the Risk — Ambiguity Is) — sharpened with a named categorical
    boundary (background-resolved vs. player-facing complexity) and a citable numeric wall
    (3-5 items while learning, 7±2 once familiar); added a symmetric warning that
    over-simplification is its own miscalibratable risk, not just over-granularity.
  - P6 (Named Composite Bonuses) — gained a companion mechanism (priority-ordered,
    mutually-exclusive behavioral tags) for combination effects that don't merit individual
    authorship, since bespoke-named effects for every pairing does not scale past a handful
    of primitives.
Added patterns:
  - P14. Asymmetric Base Cadence for Class Differentiation
  - P15. Time-Gated Specialization as an Alternative to Point-Buy Auditing
Added sections: n/a
Removed sections: n/a
Deferred / TODO items carried forward unchanged:
  - TODO(RULE_OVERRIDE_MECHANISM): still open (Principle III).
  - TODO(TECH_STACK): still open (Technology Constraints).
  - P5 (Emergent-by-History Power Acquisition): still an open design priority, not settled.
Research basis: this amendment is sourced from a fourth dedicated research pass (WoW talent/
  balance history, FFXIV/GW2/EVE, Path of Exile / PoE2's gem system, and a cross-cutting
  computer-vs-tabletop complexity-ceiling study) commissioned specifically to stress-test
  Principle VI and Pattern P3 against the largest available real-world examples of
  computer-driven (not human-GM) balance and complexity management. Full report:
  reports/WoW PoE2 MMORPG design lessons.md.
-->
# The Game Constitution

## Core Principles

### I. AI-Driven Mechanical Resolution
The AI Dungeon Master directly executes all mechanical resolution — dice rolls, number
generation, and rule application. There is no separate deterministic rules engine sitting
outside the AI's control; the AI *is* the engine that runs the mechanics, not merely a
narrator layered on top of one.

### II. Custom Ruleset by Design
The project builds a custom tabletop-style ruleset rather than adapting an existing system
(e.g. an SRD). Rationale: an AI DM can track and adjudicate mechanical complexity that would
overwhelm a human running the table, so the ruleset MUST be designed to exploit that capacity
rather than staying constrained to what a human DM could manage alone.

### III. Rule Flexibility Within Bounds (Base-Model Judgment by Default)
The rules SHOULD allow for built-in flexibility or exceptions. The AI MUST NOT be granted
blanket authority to override rules purely for narrative convenience.

RESOLVED (supersedes the prior open TODO): the default mechanism is the narrating AI's own
judgment, constrained by this project's existing behavioral patterns — P12's limitation/
weakness/cost vocabulary, P16's no-silent-dead-ends rule, P17's graduated-reveal rule — rather
than a separate classifier or judge-gate. No dedicated exception-gating tool (e.g. TypeSafe's
Jev) is adopted at this time.

This is a default, not a conclusion that base-model judgment is sufficient at scale. The first
probe session offered a couple of encouraging anecdotes (it improvised sensibly when a player
tried to compress many attack attempts into one action; it accepted a live rule correction
mid-session), but a single 13-turn session cannot actually test whether judgment holds up under
sustained, compounding complexity — that is only observable once a more complete system has
been running for longer, with more rules and more chances to break down. Defaulting to
base-model judgment is therefore not evidence-based confidence that it will hold up; it is a
deliberate refusal to build speculative infrastructure (a judge-gate) for a failure mode that
has not actually been observed yet.

TRIGGER FOR REVISITING: adopt a dedicated exception-gating mechanism (Jev or otherwise) only
once real, sustained play (not a short probe) surfaces a concrete, observed case of the base
model's rule-breakdown judgment failing in a way that matters — not preemptively. Whoever
observes such a case should record it before proposing the amendment, so any future revisit is
grounded in a real example, not a hypothetical.

### IV. MVP Scope Discipline
Version 1 MUST be single-player only (no multiplayer/co-op) and text-based only (no voice,
images, or generated art). These are explicitly out of scope until a later version, not
merely unprioritized.

### V. Combinatorial Build Diversity via Closed Primitives
Character build diversity MUST come from combining a small, closed set of primitives (fixed
slots, each filled from a fixed-size option pool), not from an open-ended, ever-growing menu
of individually-authored powers. Rationale: this is the single most consistently validated
finding across every system researched (He Who Fights With Monsters' 4 essence slots × 5
abilities, Stormlight's 10 Surges in fixed pairs, Cradle's aspect × technique-archetype cross,
Allomancy's metal grid) — closed combinatorics generate enough raw diversity to feel endless
while staying enumerable for an AI adjudicator, whereas every open-menu system researched
(Underworld's unbounded ability-copying, The Land's ever-multiplying skill/school list) became
untrackable and power-crept. This principle governs the shape of future feature specs for
character creation and progression; it does not by itself fix the exact slot counts or pool
sizes, which are implementation decisions for /speckit-plan.

### VI. Mandatory Consolidation of Aging Content
The system MUST include an explicit, telegraphed mechanism for retiring, replacing, or
re-banding old content as new content is added. Pure additive stacking — where every new tier,
school, or ability bolts on top of the last without ever superseding it — is prohibited by
design, not merely discouraged. Rationale: this is the one failure mode every researched
system shares (HWFWM, The Land, Underworld, and, per the third research pass, D&D 5e's rules
text and 13th Age's Icon relationships all bloat the same way), and no source researched so
far solves it cleanly except Dungeon Crawler Carl's specialization forks (a skill's growth
path forks into a replacement, not an addition). A feature spec that adds progression content
MUST state how older content is consolidated, re-banded, or retired as part of that content,
not leave it for a later cleanup pass.

New progression content SHOULD default to explicitly provisional status (a bounded trial
window, analogous to Path of Exile's three-month league cycle) before being granted permanent
status, rather than launching as permanent and requiring later retirement; this converts the
harder problem of removing content players are already attached to into the easier problem of
declining to promote content that was never promised to stay. Where content has already been
granted permanent status and must later be retired or re-banded regardless, the spec MUST
budget for the documented cost of that retirement — World of Warcraft's own player research
found that "large-scale reworks of classes, especially rework after rework, put off far more
people than it turned on," and its Survival Hunter rework is the reference case for how
disruptive an unbudgeted retirement can be — by bundling retirement into infrequent,
clearly-telegraphed boundary points rather than continuous piecemeal changes. A spec MUST NOT
claim that pure numeric rescaling (a "squish," which preserves relative power but retires
nothing) satisfies this principle's retirement requirement; only structural retirement —
removing, replacing, or folding a mechanic — counts.

## Technology Constraints

TODO(TECH_STACK): language, platform, and engine are not yet chosen. This MUST be resolved
during /speckit-plan for the first feature rather than assumed implicitly; do not let an
implementation default become a de facto decision without recording it here.

## Adopted Design Patterns (Provisional)

These patterns are concrete design guidance distilled from three rounds of dedicated research
(LitRPG mechanics, Mistborn/TTRPG-balance/AI-integration, and DM-craft/TTRPG-design-theory/
AI-tooling). They carry less authority than the Core Principles above: they are the project's
current best answer, not a permanent commitment, and are explicitly expected to be revised —
including by a planned fourth research pass on WoW, MMORPGs generally, and Path of Exile 2,
undertaken specifically to learn where computer-driven adjudication can handle more complexity
than a tabletop system and where it still cannot. Treat a conflict between a pattern here and
empirical AI-capability findings as grounds for amendment, not as grounds to force the finding
to fit the pattern.

**P1. Layered Variance with Player-Controlled Reroll.** Some variance beneath a character's
visible choices is mandatory at character creation (a birth-random affinity/roll, in the style
of The Land or HWFWM's Awakening Stones), so that two characters with identical visible choices
still diverge. Any variance applied *after* creation MUST NOT be auto-applied — the player MAY
defer it and gamble on a later reroll instead of being forced to accept the first result. This
is a deliberate departure from every source researched; none of them give the player this
choice.

**P2. Hybrid Progression: XP Plus Milestone-Gated Earned Tiers.** Ordinary, routine progression
uses conventional XP/leveling. A small, limited number of *major* milestone gates instead use
narrative-truth gating (Stormlight's Ideals: power is earned by demonstrated readiness, not
grinding) — reserved for big transitions, not every tier-up.

**P3. Granular State Is Not the Risk — Ambiguity Is.** The system SHOULD default toward rich,
granular tracked state rather than artificially coarse abstractions chosen for human
legibility, since computation and storage are cheap for an AI. This explicitly revises the
instinct (surfaced in the second research pass) to prefer low-bookkeeping resolution like
Cradle's single-integer rank. However, this is not a free pass: the research is clear that the
actual adjudication risk is narration drifting out of sync with ground-truth state (measured at
best-case ~46-58% consistency even with enforced function-calling, per the third research
pass), not the volume of tracked numbers. Any feature that leans on this principle MUST also
account for how state is reconciled/verified, per the AI Game Master Architecture pattern
below — granularity without a reconciliation layer is not actually safe.

This risk generalizes beyond narration specifically: the fourth research pass confirms a named
categorical boundary in computer-driven games between *background-resolved* complexity (state
the system computes but never surfaces to the player — WoW's threat tables and
diminishing-returns curves, PoE's full damage-modifier stack — which can be arbitrarily
granular with zero risk) and *player-facing* complexity (state the player must hold in working
memory to make a decision — abilities, active effects, build choices), which hits a hard,
citable comprehension wall at roughly 3-5 simultaneous items while a mechanic is being learned
and 7±2 once familiar. A feature spec MUST classify each piece of tracked state as
background-resolved or player-facing and MUST NOT budget player-facing complexity past this
wall on the assumption that computation is cheap — computation being cheap is exactly why
background-resolved state is safe, and is irrelevant to whether player-facing state is safe.
Separately, simplification itself is not risk-free: WoW's Global Cooldown was deliberately
expanded, then reversed after sustained complaint, because slowing the game down was mistaken
for reducing what a player had to track — so any deliberate simplification MUST be treated as
a hypothesis to verify against real play, not a one-time design decision, the same
reconciliation discipline this principle already demands for over-granular state.

**P4. Character-Creation Trade-offs Locked at Creation.** Race/origin (and similar foundational
choices) set a stat-quantity-vs-freedom trade-off (more points but less placement freedom, or
vice versa) once, at character creation, not something that changes later. Separately, access
*breadth* and starting *competence* MUST be decoupled: a character built for broad access
(e.g. "a bit of everything") MUST start comparatively weak per-area, per the Mistborn Adventure
Game's tested fix for "how do you let someone play the hybrid superclass without everyone else
sucking" — breadth of access is not itself a source of day-one power.

**P5. Emergent-by-History Power Acquisition (Open Design Priority).** Abilities/effects derived
from what a character actually did — what they fought, killed, or otherwise experienced —
rather than picked from a menu, are considered one of the most important goals of this project
and warrant dedicated design work, not a quick decision. This is explicitly NOT settled.
Whatever mechanism is eventually designed MUST derive the acquired effect from a combination of
what the source actually was (the monster/entity's own nature or abilities) and how it was
defeated or acquired — not from an arbitrary lookup table (unmanageable at scale) and not from
a fully open, uncapped pool (Underworld's unbounded "copy any ability," which every source
agrees became untrackable). Hemalurgy's location-plus-method encoding is a useful structural
reference for *how* to build a compact generative rule, even though its specific inputs
(body location, cause of death) are not themselves what we want to copy.

**P6. Named Composite Bonuses for Aligned Combinations.** Combining two specific, aligned
primitives SHOULD yield a distinct, named emergent bonus (Stormlight's "Three Lashings" from
Adhesion+Gravitation; Mistborn's Compounding from a matched Allomantic/Feruchemical pair) —
not just cumulative, arithmetic stacking. This makes combination itself feel designed rather
than incidental.

Companion mechanism (added by the fourth research pass, since bespoke-named effects for every
pairing does not scale past a handful of primitives): where a bespoke name isn't warranted,
define a small closed set of composable behavioral tags plus a fixed total resolution order
among them, and let combination-driven behavior change fall out of applying that order
deterministically — Path of Exile's projectile-modifier tags are the reference (Pierce beats
Fork beats Chain beats Return, so "a piercing, forking, chaining projectile will first pierce
its maximum, then fork, then chain," with no authored name for that specific combination).
Reserve P6's bespoke named effects for the smaller set of combinations distinctive enough to
deserve one; use the priority-ordered tag mechanism for everything else.

**P7. Player-Facing Reference Layer.** The system MUST provide an opt-in, queryable reference
("codex") of a character's own rules/state/abilities, separate from in-scene narration —
Stormlight's in-world "Ars Arcanum" is the model. This is adopted as more than an
implementation detail: without it, either narration turns into an info-dump of mechanics every
turn, or players lose track of their own accumulated complexity (the exact problem HWFWM's
fandom had to solve externally with spreadsheets and a Discord bot).

**P8. Deterministic Degrees-of-Success as Default Resolution.** Action outcomes SHOULD default
to a deterministic degree-of-success branch (e.g. roll margin vs. a target number producing a
critical success / success / failure / critical failure) rather than an improvised,
judgment-call ruling. This is the strongest-fit finding of the third research pass specifically
because it is computable by an AI with zero ambiguity, unlike human-GM "rulings over rules"
styles. Recommended as a near-default, not yet exercised against a real feature spec.

**P9. Fixed Action-Economy Pool.** Combat/turn structure SHOULD give every character the same
base action budget regardless of build (Pathfinder 2e's 3-actions-plus-reaction model), so that
build diversity comes from *what* fills the actions rather than *how many* actions a build gets
— closing off action-economy-stacking exploits. Exact numbers are deferred to /speckit-plan.

**P10. Move/Verb Templates Reserved for Flavor Abilities.** Fully pre-specified, narrow "move"
verbs (PbtA-style: fixed trigger, fixed resolution) MAY be used for flavor- or
narrative-driven abilities that don't need full numeric modeling, but MUST NOT be the primary
vehicle for a character's core numeric power — reserve full mechanical modeling for that.

**P11. No Naive Shared Point-Buy Without Audited Guardrails.** A shared point-buy
character-creation model (spend points from one pool on anything) is prohibited unless every
purchasable option carries a rigorously audited, context-independent cost (tiered cost
brackets, forced spending across categories, hard caps — the HERO System / Savage Worlds
pattern, not GURPS's unguarded version). Rationale: GURPS's own documented exploits (attribute
arbitrage, disadvantage-gaming) require "an eagle-eyed GM" to police live — a check this
project's AI DM cannot provide by default, so the audit discipline must be designed in upfront
or the mechanic should be avoided.

**P12. Design Vocabulary: Limitation / Weakness / Cost as Independent Levers.** When designing
any ability's tradeoffs, treat *limitation* (what it can target/do), *weakness* (an external
vulnerability), and *cost* (a price paid elsewhere), per Sanderson's Second Law, as three
separate, independently-tunable levers rather than one vague "balance" dial. This is adopted as
shared design vocabulary for how the project discusses costs, not as a mechanic in itself.

**P13. AI Game Master Architecture: Three-Layer Split.** As a working assumption (not a
permanent commitment — this is exactly the kind of decision the planned WoW/MMORPG/PoE2
research pass may revise): deterministic tool-calls own hard mechanics (dice, state
transitions); an externalized, queryable store — not the LLM's context window — owns world
state; and a narrow, calibrated gate sits between "a player proposes something ambiguous" and
"the AI narrates it as true," with an abstain-and-escalate option rather than a forced binary
verdict. That gate MUST NOT share a model family with the narrating AI it checks (the
documented "GLM judging GLM" self-judging-bias failure). Moderation/safety gating MUST be kept
as a separate subsystem from world-state/consistency gating, since they tolerate different
error rates (a reversible false positive is acceptable for moderation; it is not acceptable for
state consistency). No source researched documents this exact architecture used for
game-mastering before — this is understood to be a novel application, not proven prior art, and
should be budgeted and tested as such.

First empirical data point (from this project's own first probe session, not external
research): asked to self-assess a completed session for inconsistencies, the narrating model
reported none, yet a human reviewer found it had introduced an unearned detail (a character's
gender/pronoun that was never established) partway through. This is a small instance of exactly
the failure this pattern is designed against — the narrating model's own self-report is not a
reliable substitute for independent verification, confirmed in this project's own data, not
only in the literature.

**P14. Asymmetric Base Cadence for Class Differentiation.** A single cadence parameter (e.g.
the base delay between actions) MAY differ by class/archetype group, rather than being
uniform, as a low-overhead way to create a durable, structural feel-difference between groups
without a unique ability list — WoW's agility-melee classes run a faster base cadence than
other classes, with haste explicitly excluded from affecting the faster group, at essentially
zero added balance-audit surface. Cheap to adopt; useful as a complement to, not a replacement
for, Principle V's combinatorial primitives.

**P15. Time-Gated Specialization as an Alternative to Point-Buy Auditing.** Where Pattern P11's
audited point-buy guardrails are judged too costly to author for a given system, specialization
MAY instead be enforced by making broad access take proportionally longer to acquire (EVE
Online's real-time skill training, where training every skill to maximum would take roughly
two decades) rather than by auditing every option's point cost. This sidesteps the audit
problem by construction — a character cannot be optimal everywhere because the scarce resource
is elapsed time, not points to police — at the cost of slower respec/pivoting. Recorded as a
named alternative for a future /speckit-plan decision under P4 or P11, not adopted outright.

**P16. Always Leave an Actionable Next Step (No Silent Dead Ends).** After resolving any
action, the AI DM MUST ensure the player has at least one concrete, actionable path forward —
a lead, a threat, a choice, a consequence — rather than a dead end of purely atmospheric or
inconclusive description. If several resolution attempts in a row (e.g. three or more) have
failed to produce a new actionable lead, the AI DM MUST proactively introduce one (an
environmental event, an NPC, a ticking clock) rather than waiting for the player to notice
they're stuck and ask for one. Rationale: this project's first probe session hit exactly this
failure at turn 6-8 — a player reported feeling "soft-locked" after several escalating-but-
inconclusive clues — confirming in practice what the third research pass already found in
theory: spotlight balance and scene pacing do not fall out of good mechanical design for free
and must be engineered as an explicit heuristic, not assumed.

**P17. Graduated Information Reveal for Compound Queries.** When a single player action
bundles multiple distinct sub-questions or pieces of information into one attempt (e.g. "is it
a demon, is it fey, does it have a weakness, is it intelligent" — really four or five separate
pieces of information in one roll), the degree of success MUST gate *how much* information is
revealed, not simply *whether* any is revealed: Critical Success reveals essentially all
bundled sub-answers; Success reveals roughly half (the DM's choice of which, favoring
narratively useful ones), leaving the rest genuinely unresolved rather than wrong; Failure
reveals at most one vague, uncertain impression; Critical Failure reveals nothing reliable
(optionally something misleading). Re-attempting the same bundled question MUST NOT be a free
retry — it should cost something (time, risk of detection, an escalating consequence)
consistent with whatever tension is already established in the scene. Rationale: this pattern
was identified live, by the player, during this project's first probe session, extending
Pattern P8's binary degrees-of-success into a "how much," not just "whether," axis. It was
accepted by the AI DM mid-session but was not re-exercised afterward — treat as
adopted-but-unverified until tested again.

## Governance

This constitution supersedes ad-hoc practice for this project. `/speckit-specify`,
`/speckit-plan`, `/speckit-tasks`, and `/speckit-implement` MUST treat the Core Principles above
as binding constraints, not suggestions; where a spec or plan conflicts with a Core Principle,
the conflict MUST be surfaced and resolved (either by changing the spec/plan, or by amending
this document) rather than silently overridden. The Adopted Design Patterns section carries
deliberately lower authority: a spec or plan MAY deviate from a pattern there when a specific
feature's needs, or new research/implementation evidence, warrant it, but SHOULD note the
deviation and its reason rather than silently drifting from it.

Amendments are made by re-running `/speckit-constitution` with the proposed change. Version
bumps follow semantic versioning: MAJOR for backward-incompatible principle removals or
redefinitions, MINOR for new principles/patterns or materially expanded guidance, PATCH for
wording or clarification only.

**Version**: 1.5.0 | **Ratified**: 2026-09-27 | **Last Amended**: 2026-09-28
