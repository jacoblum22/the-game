<!--
Sync Impact Report
Version change: 3.0.0 → 3.1.0 (MINOR: VIII.9 added, "code never deduces the story": no inference of story
  state from actions or words, no word matching for decisions. Owner ruling 2026-10-10, spec 032.)
Version change: 2.0.0 → 3.0.0 (MAJOR: the project's stance toward the model is redefined. The owner directed
  it on 2026-10-08/09 and approved recording it here and in rules/00-architecture.md.)
Added principles:
  - VIII. Code Owns the Spine; the Model Owns Language and Judgment. Eight rules: (1) code owns the spine
    (state, dice, rules arithmetic, secrets and clues, what must be exact) and does not author narrative
    content models must repeat; (2) check by measured precision, only what breaks the game; (3) truth only
    when it matters (speech is testimony); (4) whole over parts; (5) remove friction before adding
    procedure; (6) better context, not more rules; (7) diagnose from evidence; (8) the player is part of
    error correction. Kept: structured state, typed goals, clues and cases, dice, the feedback loop.
    Caution: trust is model-dependent; validate on Gemini Flash.
Superseded or reinterpreted (each listed under VIII, "What VIII supersedes"):
  - Truth-gated narration (state only what the store holds): reinterpreted. The store holds the spine and
    what has been settled; nothing else needs a source before it is narrated.
  - P13's independent checker (a second model, of another family, checking every claim): superseded by
    VIII.2. P13 amended in place; TODO(CROSS_FAMILY_CHECKER) closed by withdrawal.
  - "The DM never chooses what is true" (rules 12.6.1): reinterpreted as already loosened by owner rulings
    D1 (T1b) and S1 (rules DL-12-91). It governs what the game relies on, not speech or incidental detail.
  - NPCs mute unless sourced: superseded (already reversed by S1/S2, rules DL-12-91 to DL-12-93).
  - Atomising every message, sentence and fact so it can be checked: superseded by VIII.4.
  - Rule cards as the model's payload (rules 00.15.1, 00.15.4): superseded by VIII.6. Cards stay as the
    specification and the lookup.
Modified principles and patterns:
  - I: one sentence ties the instruments to VIII's spine. Meaning unchanged.
  - P3: AMENDED note. The "reconciliation layer" is the code-owned spine, precision checks and the feedback
    loop, not a check of every narrated claim.
  - P13: AMENDED note. The gate is narrowed to VIII.2; the cross-family requirement is withdrawn for
    narration checks (moderation stays separate).
  - Technology Constraints: closed-choice forms are for what code must record; TODO(CROSS_FAMILY_CHECKER)
    closed.
Bump rationale: MAJOR. A design that complied with 2.0.0 (a second-family model checking every claim,
  cards as the packet, code-scripted NPC lines) now violates VIII; a design that P13 forbade (one model
  family, trusted except where precision checks catch real breaks) now complies.
Resolved deferrals: TODO(CROSS_FAMILY_CHECKER): withdrawn (Technology Constraints).
Deferred: validation of every loosening on Gemini Flash (no playtest has run on it yet). Engine packets still
  carry the core and situation cards to every role (rules DL-00-06, Migration); aligning them is follow-up
  work.
Dependent artifacts: rules/00-architecture.md (design intent, 00.1.1, 00.1.3, 00.1.4, 00.1.5, 00.2.1,
  00.12.7, 00.13.1, 00.15.1, 00.15.4; [revision: R2-J0]); rules decision DL-00-06; traceability row VIII.
  specs/*/plan.md Constitution Check rows keep citing the version they were planned under.
Evidence: research_notes/Playtest round 2 solutions/ROUND3-ANALYSIS.md (S1-S3: code-scripted dialogue,
  mandatory texture, a feedback loop built for precise claims; "check less should be decided by measured
  precision, not by claim class"), ROUND4-ANALYSIS.md (R1 hedging from a hearsay rule; R3/R5 friction),
  ROUND5-ANALYSIS.md (T3 repetition traced to blind repair calls, not the model), and round6-investigation/
  I1 (sentence-array schema and coverage repairs cause choppy, repeated speech; 28 of 30 repair targets
  from coverage), I2 (settling testimony is what produced the garbage in mechanics), I3 (`/fix`: 1 of 15
  disputes right; complaint text pinned as fact), I4 (rule text is 70-85% of each packet and mostly unused;
  the situation plus short guidance cuts input about 73%; goal/method splitting comes from instructions, not
  model size).

Prior report (1.8.0 → 2.0.0):
Version change: 1.8.0 → 2.0.0 (MAJOR: Principle I is redefined. The owner approved the first
  feature's tech stack on 2026-10-07; recording it here also brings Principle I's wording in line
  with the reading the ruleset already uses.)
Modified principles:
  - I. AI-Driven Mechanical Resolution (title unchanged). Removed: the AI "directly executes all
    mechanical resolution — dice rolls, number generation" and "there is no separate deterministic
    rules engine sitting outside the AI's control". Replaced with 00-architecture's "Principle I,
    stated precisely": the AI DM makes every judgment that sets something in motion; deterministic
    instruments do the arithmetic, dice and bookkeeping the rules mark `[D]`, in the order PR-12-1
    fixes; nothing bypasses the instruments. Kept: the AI is the engine, not a narrator on top of one.
Bump rationale: this is a backward-incompatible redefinition, so MAJOR. It removes a normative
  prohibition and puts a requirement in its place. A design that complied with 1.8.0 (the model
  producing its own dice and numbers in context) now violates I, because it bypasses the
  instruments. A design that 1.8.0's wording arguably forbade (code running the `[D]` steps, as in
  specs/004) now complies. The intent is unchanged. `rules/` (00-architecture) has used this reading
  since v1.0, and the principle now agrees with P13 ("deterministic tool-calls own hard mechanics").
  Resolving TODO(TECH_STACK) on its own would have been MINOR.
Expanded sections:
  - Technology Constraints: TODO(TECH_STACK) resolved (engine, schemas, storage, models, front end,
    hosting), with plan.md and research.md cited for detail.
Added sections: n/a
Removed sections: n/a
Resolved deferrals:
  - TODO(TECH_STACK): resolved (Technology Constraints). The "still open" lines in the prior reports
    below are kept as history.
Newly deferred by this amendment:
  - TODO(CROSS_FAMILY_CHECKER): the claim checker shares the narrator's model family (Gemini). This
    is a recorded deviation from Pattern P13 and stays open until a second-family checker is restored.
Dependent artifacts: specs/004-playable-prototype/plan.md Constitution Check rows for Principle I
  and Technology Constraints now cite v2.0.0.
Research basis: specs/004-playable-prototype/research.md (R1–R4, R6, R9, R10, R12) and plan.md
  (Technical Context, Complexity Tracking); rules/00-architecture.md "Principle I, stated precisely".

Prior report (1.7.0 → 1.8.0):
Version change: 1.7.0 → 1.8.0 (MINOR: the ruleset in `rules/` (v1.0) resolves every item this
  document deferred to "a future /speckit-plan", and records three owner-approved pattern
  amendments it made along the way. No Core Principle is changed.)
Modified patterns:
  - P3: the player-facing comprehension wall is no longer a design budget. Owner direction
    (2026-09-29, DL-00-01): rules are judged only by player freedom and AI correctness. The
    classification requirement (background vs player-facing) stands and is refined into four
    visibility classes (rules 00.6.4); the codex (P7, rules ch.14) carries player-facing load.
  - P5: (a) the evidence-significance gate is computed from the frame's pre-committed fields
    (consequential AND pressured AND own act), not judged after the fact; fresh judgment remains
    only for tags and conduct (DL-03-01). (b) The "calibrated classifier" is realized as a
    deterministic five-confirmation scorer with the same three-valued policy (DL-04-10); it
    shares no model family with the narrator, so P13's independence requirement is met.
  - P14: the cadence parameter is not varied by action count. P9's fixed pool takes precedence;
    cadence differences live in what one action contains (weapon weight), tempo, and reactions
    (DL-06-02).
Resolved deferrals (each resolved in `rules/`; cited rule ids):
  - Ability scores: seven attributes and a closed list of derived values (00.4.1, 00.4.4, 02.3).
  - P2's baseline competence floor (00.3.6, 02.5.1).
  - The hierarchical tag vocabulary (00.5, 03.1, data/tags.yaml).
  - The tag_event capture mechanism (00.6.8, 03.1, 03.7.2).
  - P5's class list and the curated hybrid table (04.2, data/callings.yaml, data/hybrids.yaml).
  - P5's numeric thresholds, confidence cutoffs and synergy bonuses (04.3, 04.4, 04.8).
  - P9's action-economy numbers; Focus pool size, costs and recovery (06.1.1, 05.6).
  - What dropped items grant (08.3, 08.4, 00.11.5).
  - VI's consolidation, retirement and provisional mechanics (04.8, 05.12, 00.16.3).
  - Slot counts, pool sizes and the hard slot ceiling (05.2).
  - Ruleset versioning for live saves (00.16.6).
Deferred / TODO items carried forward unchanged:
  - TODO(TECH_STACK): still open (Technology Constraints).
Research basis: the ruleset's decision log (`rules/appendix/decision-log.md`) and traceability
  matrix (`rules/appendix/traceability.md`), which map every principle and pattern to rule ids.

Prior report (1.6.0 → 1.7.0):
Version change: 1.6.0 → 1.7.0 (MINOR: sixth pass — an extended design conversation plus several
  targeted research checks conducted during it — resolves P5's default application and sharpens
  its class-emergence mechanism, revises P2's leveling model, adds a new Core Principle bounding
  what the AI DM may treat as a possible action, gives P9 a shared active-ability resource
  companion mechanism, revises P10's numeric-vs-narrative test, and sharpens P3 with the
  rationale for why background-resolved richness specifically aids an AI DM's improvisation)
Modified patterns (continued):
  - P3 (Granular State Is Not the Risk — Ambiguity Is) — added the rationale for *why*
    background-resolved complexity should be maximized, not merely permitted: it is the raw
    material an AI DM draws on to adjudicate a genuinely novel player action by reaching for and
    adapting an existing sub-rule, rather than inventing a ruling from nothing — the traditional
    reason crunchy systems aid human-GM improvisation, now framed as an AI-specific strength
    (no fear-of-novelty response) rather than a cost to be minimized. Explicitly corrects a
    within-session misstep: open-endedness and player-facing simplicity are independent axes,
    not the same thing, and reducing background richness in the name of simplicity risks
    reducing the system's ability to handle surprising player actions gracefully.
  - P9 (Fixed Action-Economy Pool) — gained a companion mechanism: one shared, generic resource
    pool (tentatively "Focus") governs the cost of every active ability across every class,
    separate from the character's primary Vitality-like resource, rather than each class
    authoring its own bespoke resource type.
  - P10 (Move/Verb Templates Reserved for Flavor Abilities) — revised: the deciding factor for
    whether a mechanism may carry a character's core power is no longer numeric-vs-narrative
    representation, but how deterministic its trigger-to-outcome mapping is. A precisely-scoped
    narrative permission is exactly as safe as a numeric formula; a vague, open-ended judgment
    call is exactly as risky in either format.
Modified patterns:
  - P2 (Hybrid Progression) — retitled from "Hybrid Progression: XP Plus Milestone-Gated Earned
    Tiers" to "History-Gated Power Tiers (No Separate Level)". REVISED, not merely extended:
    conventional XP/leveling is removed as the default progression mechanism. Power growth now
    routes entirely through Pattern P5's class/archetype-emergence mechanism, via deepening,
    narratively-crystallized tiers within a recognized identity — Stormlight's Ideals
    generalized from "reserved for rare major transitions" into the project's sole progression
    mechanism, not a supplement to XP.
  - P5 (Emergent-by-History Power Acquisition) — both flavors sharpened with resolved detail:
    (1) the specific-ability-from-source-and-method mechanism is generalized from its
    combat-specific naming (source archetype / acquisition method) to a domain-independent
    shape (a pool-gating circumstance / an orthogonal fill-quality circumstance), and its
    default application is redirected to loot/item generation rather than direct personal
    ability-granting — direct monster-power absorption from a kill is rescoped as a class-gated
    special capability ("Blue Mage"-style), not the default player experience; (2) the
    class/archetype-emergence mechanism's category axes are sharpened into a bounded,
    hierarchical tag vocabulary (a narrow event counts as evidence at every level of its
    hierarchy at once), with two resolved class shapes — specialist (single dominant tag at any
    hierarchy level) and hybrid (co-occurrence of tags from unrelated branches, defined via an
    explicitly curated sparse table, never a full cross-product); (3) the significance/
    eligibility gate deciding whether a moment counts as evidence at all is resolved as
    base-model judgment (Principle III's existing default), not a separate bounded taxonomy,
    since a fixed taxonomy was found to relocate that judgment call rather than remove it; (4)
    granted abilities/bonuses may be passive (narration-consistency-checked, no tracked usage)
    or active (player-invoked, each with its own explicit recharge condition that MUST be
    mechanically tracked and enforced, not left as descriptive prose).
Added principles:
  - VII. Default-Deny Capability Gate — before resolving how well an attempted action goes
    (Pattern P8), the AI DM MUST first resolve whether the action is even a legal attempt; only
    a small, fixed tier of basic actions is available by default, and anything beyond it needs
    an explicit license (a granted ability, an unlocked class capability, an established
    narrative fact).
Added patterns: n/a
Removed sections: n/a
Deferred / TODO items carried forward unchanged:
  - TODO(TECH_STACK): still open (Technology Constraints).
  - P5's exact class list, numeric thresholds, confidence cutoffs, and synergy-bonus values:
    still deferred to a future /speckit-plan.
Newly deferred by this amendment:
  - The shared "does this moment count as evidence" capture mechanism (tentatively
    `tag_event`), which both of P5's flavors depend on, is not yet designed in implementation
    detail or built — identified as the next concrete dependency to resolve, not designed here.
  - The exact hierarchical tag vocabulary, and the curated table of valid hybrid-class pairs,
    remain unauthored — this amendment resolves their shape, not their content.
  - P2's baseline competence floor for a character not yet recognized as any class is left
    unresolved — deferred to a future /speckit-plan.
  - Ability scores (P4/P11 already assume a stat-allocation system exists, but never specified
    how many scores or what they modify) remain undecided in count and shape. Resolved framing
    only: they answer "how good are you at broad categories of action" (roll modifiers, mostly
    fixed at creation per P4), a different question from the class/tag system's "what can you
    even attempt, and who have you become" — and their count should be set by how much raw,
    mostly background-resolved texture the AI DM needs to adjudicate novel actions well, not by
    a target for minimizing player-facing numbers. The actual number and their exact modifiers
    are deferred to a future /speckit-plan.
Research basis: this amendment is sourced from an extended real-time design conversation plus
  several targeted Haiku-tier research checks conducted during it (Multiple Instance Learning
  and chunk-level retrieval for classification, ultimately ruled out in favor of a non-ML
  tag-tally approach; real game-AI player-modeling precedent; TTRPG values-tracking precedent,
  e.g. D&D's Paladin oaths and Fallout/Fable/Baldur's Gate 3's karma-and-reputation systems;
  hierarchical tag taxonomies and domain-x-method class design, e.g. Path of Exile's tag
  cascades and D&D 5e's Wizard/Warlock/Sorcerer split; and mainstream-vs-narrative TTRPG
  advancement models, e.g. Pathfinder 2e's feat structure and Blades in the Dark's
  playstyle-triggered XP) — not a single dedicated research-round report the way the fourth and
  fifth amendments were.
Version change (prior): 1.5.0 → 1.6.0 (MINOR: fifth research pass resolves Pattern P5's direction)
Modified patterns:
  - P5 (Emergent-by-History Power Acquisition) — retitled from "(Open Design Priority)" to
    "(Direction Resolved, Specifics Deferred)". Architecture resolved for both flavors: (1)
    specific-ability-from-source+method uses a source-gated bounded sub-pool plus a
    method-selected fill mechanism (Diablo/PoE/Borderlands' item-generation pattern), with
    slot-claiming conflicts resolved via P6's priority-rank companion mechanism; (2)
    class/archetype emergence is a narrative label DERIVED from an underlying, hard-capped
    combinatorial ability-slot system (never an independent ability-dispensing system of its
    own), eligibility gated by deterministic dual-tier thresholds (Delve's Primary/Secondary
    Requirement model) keyed to a small fixed set of category axes, resolved by a calibrated,
    model-family-independent classifier (per Pattern P13) that scores a bounded candidate set
    and returns a confidence value per candidate rather than a forced pick, decided via a
    three-valued grant/offer-to-player/abstain policy, with mixed histories resolved by
    presenting a named hybrid option for the player to choose rather than a computed
    tie-break formula. The exact class list, thresholds, confidence cutoffs, and bonus values
    remain deferred to a future /speckit-plan — this amendment resolves architecture, not
    numbers.
  - P6 (Named Composite Bonuses) — added a cross-reference noting Pattern P5's class-synergy
    bonus is an instance of this mechanism, not a separate one.
Added patterns: n/a
Removed sections: n/a
Deferred / TODO items carried forward unchanged:
  - TODO(TECH_STACK): still open (Technology Constraints).
Newly deferred by this amendment:
  - P5's exact class list, numeric thresholds, confidence cutoffs, and synergy-bonus values —
    architecture is resolved; numbers are not, and are left for a future /speckit-plan.
Research basis: this amendment is sourced from a fifth dedicated research pass (ARPG procedural
  affix/effect generation, roguelike/roguelite build-synergy architecture, and LitRPG
  class-from-aggregate-playstyle precedent) commissioned specifically to resolve Pattern P5,
  the project's longest-standing open design priority. Full report:
  reports/Emergent power acquisition mechanisms.md.
Version change (prior): 1.4.0 → 1.5.0 (MINOR: resolves Principle III's long-open TODO)
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
The AI Dungeon Master *is* the engine that runs the mechanics, not merely a narrator layered on
top of one. Stated precisely (rules/00-architecture.md, "Principle I, stated precisely"), "the
engine" and "the tool" mean the deterministic instruments the AI DM operates. The AI DM MUST make
every judgment that sets something in motion: *when* to call an instrument, *what* to classify,
and *how* to narrate the result. The instruments do the arithmetic, the dice, and the
bookkeeping. Code runs only the steps the rules mark `[D]`, in the order PR-12-1 (the turn loop)
fixes, and MUST NOT make a judgment the rules mark `[J]`. Nothing happens that the AI DM did not
set in motion, and nothing the AI DM sets in motion bypasses the instruments. The instruments are
the spine of Principle VIII; language and judgment are the model's.

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

### VII. Default-Deny Capability Gate
Before resolving *how well* an attempted action goes (Pattern P8's degree-of-success), the AI
DM MUST first resolve *whether the action is even a legal attempt*. A small, fixed tier of
basic actions — move, observe, talk, a basic unskilled attack, and similarly mundane actions any
character could plausibly attempt — is always available to every character by default. Anything
beyond that tier MUST be explicitly licensed by a granted ability, an unlocked class capability,
or an established narrative fact before the DM narrates an attempt at it as possible; an attempt
with no such license MUST be declined or redirected (narrated as failing outright, or reframed
as the nearest basic action actually available), never narrated into existence merely because
the player described it. Rationale: an AI narrator's generosity is a documented risk in both
directions — Pattern P16 already guards against an AI DM being too withholding (silent dead
ends), and this principle is its counterpart, guarding against an AI DM being too permissive
(treating any described action as possible by default). This principle governs *capability*,
not *outcome quality* — it answers "can you even try this," a question logically prior to and
separate from P8's "how well did the attempt go."

### VIII. Code Owns the Spine; the Model Owns Language and Judgment
Owner direction, 2026-10-08/09 (rules DL-00-06). The earlier stance treated the model as an unreliable
component to be constrained at every step. This principle replaces that stance. The model is a capable
reader and writer: it is given good context, trusted where a mistake does not break the game, and
corrected when it is wrong. The owner's own words: "fixes aren't sacred"; "we might be too intense with the
rules; AI doesn't hallucinate so much… pull back on non-critical cases"; "dialogue is testimony"; "make the
system less strict… a robust system for the player to provide feedback… have it go back and check"; "don't
get too in the weeds"; "analyse things holistically, not individually".

1. **Code owns the spine; the model owns language and judgment.** The spine is structured state, dice,
   rules arithmetic, secrets and clues, and anything else that must be exact. Code MUST own it
   (Principle I). Code MUST NOT author narrative content that a model is then made to repeat: prose, NPC
   lines, or facts mislabelled from speech.
2. **Check by measured precision, and only what breaks the game.** A check MAY block output only where its
   measured precision is high and what it guards would break the game: the spine, a sealed secret or clue,
   or a safety line. Everything else is trusted, logged, or corrected by the player. Whether a check
   blocks is decided by measurement, not by the class of claim it inspects.
3. **Truth only when it matters.** What a character says is testimony, not world truth. It is settled into
   world truth only when the player relies on it mechanically, and it is settled at that moment.
4. **Whole over parts.** Models read whole messages and write whole passages. Only what code must decide or
   remember exactly is atomised into closed choices, fields and records. Messages, sentences and facts
   are not split up just so they can be checked.
5. **Remove friction before adding procedure.** When play stalls or feels stiff, first remove the step,
   gate or mandatory content that causes it. Add a new procedure only when removal cannot fix the problem.
   Fixes are not sacred: a past fix that now causes friction is removed, not defended. Model the world at
   the grain play needs; fine position matters much less than place and range.
6. **Better context, not more rules.** The ruleset is the specification the code implements, not a
   payload for the model. Each model call gets the situation, plus short guidance for the judgment that
   call makes. A model call MUST NOT be given rule text for decisions it does not make.
7. **Diagnose from evidence.** Before naming a cause, trace the actual model inputs and outputs of the
   failing turn (what the call was given, what it returned, what code did with it). A model that can see
   the conversation should not normally repeat itself, so a failure that looks like the model's is first
   checked against what it was shown. Analyse holistically: group symptoms by shared cause, and don't
   patch them one at a time.
8. **The player is part of error correction.** The feedback loop (`/fix`) MUST understand a report, go
   back and check the record, repair visibly, and answer plainly. It is the safety net that lets the rest
   of the system be loose, so its quality is measured on real complaints.
9. **Code never deduces the story.** Code MUST NOT infer story state from actions or words: positions,
   range, presence, who comes along, who holds whom, a person's identity, an enemy's choice, a cost's form,
   or anything else a reader of the scene would judge. Only the DM model sets these, through a tool or by
   choosing a rule's option; code records what it is told and does the arithmetic (dice, harm, a rule's
   stated result of a roll). Code MUST NOT decide anything by word matching (regexes, keyword lists, name,
   alias, head-noun or content-word overlap) over natural-language text; parsing code-made ids and tokens is
   fine. When code and the story disagree, give the DM a tool or a field to state it, never an inference.
   Owner, 2026-10-10: "Code should absolutely not be doing that sort of thing… there are a million
   different ways that this could go down"; "we need to remove all instances of [word matching]".

*What VIII keeps:* structured state, typed goals (intended changes), clues and cases, dice, and the
feedback loop.

*What VIII supersedes or reinterprets* (older text that conflicts is read through this list):
- **Truth-gated narration** ("state only what the store holds"): reinterpreted. The store holds the spine
  and what has been settled. Nothing else needs a source before it is narrated; incidental detail is
  written as narrated, and speech is testimony.
- **P13's independent checker** (a second model, of another family, checking every claim): superseded by
  VIII.2. See P13's v3.0.0 amendment.
- **"The DM never chooses what is true"** (rules 12.6.1): reinterpreted, as owner rulings D1 (T1b) and S1
  (rules DL-12-91) already loosened it. It governs what the game will rely on (spine facts, clues,
  consequential content). It does not govern a character's speech or incidental detail.
- **NPCs mute unless sourced:** superseded. Characters speak freely in character (rules DL-12-91 to
  DL-12-93).
- **Atomising every message, sentence and fact so it can be checked:** superseded by VIII.4.
- **Rule cards delivered to the model** (rules 00.15.1, 00.15.4): superseded by VIII.6. The cards remain the
  specification, and the lookup for implementers, authors and tools.

*Caution: trust is model-dependent.* The evidence for this principle comes from Haiku-engine playtests.
Each loosening MUST be validated on the target model, Gemini Flash (Technology Constraints), before it is
treated as settled. If that model needs more checking, the checking is added back by measured precision
(VIII.2), not by claim class.

*Precedence.* Where an Adopted Design Pattern, or a rule written under the earlier stance, conflicts with
VIII, VIII governs. The conflict is resolved by revising that pattern or rule, not by tightening VIII.

## Technology Constraints

The owner approved this stack on 2026-10-07 with the first feature's plan. Detail, alternatives and
costs are in `specs/004-playable-prototype/plan.md` (Technical Context, Complexity Tracking) and
`specs/004-playable-prototype/research.md`. Changing any item below is an amendment to this
document, not a plan-level default.

- **Engine:** Python 3.11+, one engine package, `engine/`. Code drives the PR-12-1 turn loop and the
  PR-01-1 resolution pipeline. Where code must record or compute from an answer, model roles fill
  per-turn JSON-Schema forms whose enums come from the rules and the current game state, so that
  judgment is a closed choice (Principle I). Narration and speech are whole passages (VIII.4).
- **Schemas and state objects:** Pydantic v2.
- **Storage:** one SQLite event log per game: append-only events as the source of truth, a typed
  projection, and snapshots. This is the external store Pattern P13 requires.
- **Models:** Gemini 3.8 Flash for every model role, on one key (`GEMINI_API_KEY`). The claim
  checker is a separate call that can be swapped out on its own.
  `TODO(CROSS_FAMILY_CHECKER)` is closed (v3.0.0): Principle VIII.2 withdraws the requirement that a
  second model family check narration. A second-family checker is restored only if measurement on
  the target model shows a check that breaks the game needs one.
- **Front end:** a terminal front end first, then a FastAPI + htmx web front end.
- **Hosting:** one SQLite file per game.

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

**P2. History-Gated Power Tiers (No Separate Level).** REVISED (sixth pass): power growth MUST
NOT rely on a separate, flavor-independent level number tracked apart from what a character
actually did — this project's emergent-by-history premise (Pattern P5) extends to progression
itself, not only to which specific abilities a character has. Power growth is routed entirely
through Pattern P5's class/archetype-emergence mechanism: a recognized class/identity MAY
deepen, through further sustained or intensified tag evidence, into successive tiers, each
unlocking additional potency (a stronger version of its synergy bonus, or a new bounded
ability). This generalizes Stormlight's Ideals from a mechanic reserved for rare, major
transitions into the project's sole progression mechanism, rather than a supplement to
conventional XP/leveling.

A tier SHOULD be crystallized by a specific, narratively-significant moment — mirroring how an
Ideal is sworn at a moment of crisis or realization, not silently granted the instant a counter
crosses a line — presented to the player as an affirmed choice via Pattern P5's existing
three-valued grant/offer/abstain policy's "offer" tier, not auto-applied. Where a character has
not yet been recognized as any class, or a recognized class's first tier has not yet triggered,
the system MUST still provide some baseline floor of competence rather than leaving early
characters fragile-by-default; the exact shape of that floor (a flat starting competence, a
small class-independent pool, or something else) is deferred to a future /speckit-plan, not
resolved here.

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

Sixth-pass addition — why background-resolved richness should be maximized, not merely
permitted: open-endedness and player-facing simplicity are independent axes, not the same
thing, and a spec MUST NOT reduce background-resolved complexity in the name of simplicity
without checking which axis it's actually affecting. The traditional reason a crunchy tabletop
system helps a human GM improvise is that a rich mechanical vocabulary gives them something
concrete to reach for and adapt when a player does something no rule explicitly covers ("this
isn't quite written down, but it's basically a grapple check with a penalty"), whereas a
stripped-down system leaves them to invent a ruling from nothing, which is exactly where an
inexperienced or anxious human GM freezes up. An AI DM does not carry that fear-of-novelty cost,
so it can make that same reach-and-adapt move fluidly — which means background-resolved richness
should be treated as raw material for graceful improvisation, not bookkeeping overhead to be
minimized. This does not relax the player-facing comprehension wall above; it means the wall
applies only to what a player must actively track, never to the density of the substrate the AI
DM privately reasons with.

AMENDED (v1.8.0, owner direction, DL-00-01): the comprehension wall above is retained as
research context but is **not** a design budget for this project. No rule is cut or coarsened to
reduce what the player must track; rules are judged only by player freedom and AI correctness. The
MUST to classify every piece of tracked state stands (rules 00.6.3, 00.6.4), and the player-facing
load is carried by the codex (P7; rules ch.14).

AMENDED (v3.0.0, Principle VIII): the "reconciliation layer" this pattern requires is the code-owned
spine, the blocking checks that measure as precise (VIII.2), and the feedback loop (VIII.8). It is not a
check of every narrated claim against the store.

**P4. Character-Creation Trade-offs Locked at Creation.** Race/origin (and similar foundational
choices) set a stat-quantity-vs-freedom trade-off (more points but less placement freedom, or
vice versa) once, at character creation, not something that changes later. Separately, access
*breadth* and starting *competence* MUST be decoupled: a character built for broad access
(e.g. "a bit of everything") MUST start comparatively weak per-area, per the Mistborn Adventure
Game's tested fix for "how do you let someone play the hybrid superclass without everyone else
sucking" — breadth of access is not itself a source of day-one power.

**P5. Emergent-by-History Power Acquisition (Direction Resolved, Specifics Deferred).**
Abilities/effects derived from what a character actually did — what they fought, killed, or
otherwise experienced — rather than picked from a menu, remain one of the most important goals
of this project. A fifth research pass (ARPG procedural affix/effect generation, roguelike
build-synergy architecture, and LitRPG class-from-playstyle precedent; full report:
`reports/Emergent power acquisition mechanisms.md`) resolves the *architecture* for this
pattern, across both of its flavors below — the exact class list, thresholds, confidence
cutoffs, and bonus values remain deferred to a future `/speckit-plan`, not settled here.

*Specific-ability-from-source-and-method.* Whatever mechanism is built MUST derive an acquired
effect from a combination of what the source actually was (a monster/entity's own nature, or a
category of action performed) and how it was defeated, acquired, or performed — never an
arbitrary lookup table (unmanageable at scale) and never a fully open, uncapped pool
(Underworld's unbounded "copy any ability," which every source agrees became untrackable). The
resolved shape, confirmed convergently across Diablo/PoE/Borderlands' item-generation systems
and Hades/Delve's curated-table designs: the **source categorically gates a small, bounded
sub-pool of eligible effects** (the way a monster's nature gates which effect-templates are
even possible, mirroring how Borderlands' manufacturer identity gates its parts pool), and the
**acquisition method then selects how one is filled from that gated pool** — a guaranteed pick,
a weighted/biased roll, or a deterministic addition, mirroring Path of Exile's Essence/Fossil/
Crafting-Bench split. For acquired effects that claim an exclusive behavioral slot (override a
basic action) rather than stacking additively, resolve conflicts with a priority-rank field per
effect (Pattern P6's companion mechanism, independently reinvented by Binding of Isaac's
designers for the identical problem), not a bespoke pairwise rule.

REVISED (sixth pass): this mechanism's two circumstance-axes are domain-independent, not
combat-specific. The *pool-gating circumstance* is whatever fundamentally characterizes the
thing being engaged with (a monster's nature, a crafting material, or a future domain's own
equivalent); the *fill-quality circumstance* is the manner or quality of how the character
engaged with it (decisive vs. costly vs. merciful, or a future domain's own equivalent) —
"source archetype" and "acquisition method" were Feature 003's combat-specific instantiation of
this shape, not its definition, so a future feature in a different domain (e.g. crafting) MUST
NOT be assumed to need its own bespoke two-axis design when this general shape already fits it.

This mechanism's default application to combat outcomes MUST be loot/item generation (a
defeated source drops an item generated from its gated pool), not a direct, personal ability
granted to the character. Feature 003's original framing — a kill directly granting the
character a personal ability — does not reflect how most player characters should experience
combat rewards; that framing is instead reserved as a class-gated special capability (a "Blue
Mage"-style monster-power-absorption trait, itself something a character must be recognized for
via the class/archetype-emergence mechanism below), not the default. Whether a dropped item
itself grants an ability, a passive bonus, or nothing beyond mundane value is a further
application of the same pool-gate/fill-quality shape, deferred to a future /speckit-plan.

*Class/archetype emergence.* The underlying combinatorial ability-slot system (small, fixed
slots times bounded option pools, recombined — HWFWM's and Stormlight's model, already this
project's general build-diversity approach) is what generates real mechanical diversity, and it
MUST carry a hard total-slot ceiling (mirroring HWFWM's fixed 20-ability cap) rather than
growing without bound. A "class" or title is a **derived narrative label computed over that
combinatorial state** (e.g., which fraction of filled slots are blade-tagged vs. arcane-tagged)
— it MUST NOT become an independent system that hands out an ability list of its own; doing so
would reintroduce the menu-driven, non-emergent model this pattern exists to avoid. Eligibility
for a class-consideration moment MUST be gated by deterministic, engine-tracked counters, not
narration — a dual-tier threshold (a rank/ratio across a small, fixed set of category axes,
plus a cumulative action counter, per Delve's Primary/Secondary Requirement structure) keyed to
a small, author-fixed set of axes, never to the full, ever-growing ability or monster list (the
same low-cardinality-keying trick Hades uses for its Duo Boon table). Once eligible, a
calibrated classifier — which MUST NOT share a model family with the narrating AI, per Pattern
P13's existing independence requirement — scores the bounded, eligible candidate set (not the
full class list) using the character's actual combinatorial state, returning a confidence value
per candidate rather than a forced single answer. Resolve those scores with a three-valued
policy: high confidence grants directly; mid confidence presents the candidate(s) as real,
player-chosen options rather than an auto-applied result (consistent with Pattern P1's existing
"player may defer or gamble" value); all-low-confidence abstains and re-checks later rather than
forcing a decision the evidence doesn't support. Mixed/hybrid histories — for which no source in
the fifth research pass supplied an explicit numeric tie-break formula — are resolved by
surfacing a named hybrid candidate (The Wandering Inn's "consolidation" precedent) alongside the
single-track options and letting the player choose, rather than requiring the system to compute
a winner. A recognized class MAY unlock a small, bounded, audited synergy bonus requiring the
class's specific combination to trigger (Pattern P6's named composite bonus, or Pattern P14's
cadence differentiation) — never a new ability list of its own.

REVISED/SHARPENED (sixth pass): the "small, author-fixed set of axes" this eligibility gate is
keyed to MUST be a bounded but hierarchical tag vocabulary — a narrow, specific tag (e.g. a
specific school of magic) counts as evidence simultaneously for its broader parent tags (that
school's element, and magic generally), so a single narrated event contributes to every level of
specificity it actually belongs to at once, rather than requiring a separate judgment per level
(Path of Exile's own tag-cascade system, applied to behavioral tags rather than item affixes, is
the confirmed precedent for this shape). Two resolved class shapes fall out of this hierarchy: a
**specialist** class is defined by dominance of one tag at any level of the hierarchy (a broad
tag like general spellcasting, or a narrow one like a specific mundane trade), evaluated against
its own threshold independent of every other class's threshold — this is what prevents broad/
common classes from structurally starving niche/narrow ones, since a narrow class never competes
against a broad class for the same evidence pool. A **hybrid** class is defined by co-occurrence
of tags from otherwise-unrelated branches of the hierarchy (e.g. requiring both meaningful
arcane evidence and meaningful martial evidence); hybrid classes MUST be defined via an
explicitly-authored, curated sparse table of valid tag-combination pairs, never a full Cartesian
cross-product of every possible pairing, per the same combinatorial-explosion caution Principle
V already applies to ability primitives (Hades' Duo Boon table and Delve's curated requirement
pairs are the confirmed precedent for keeping this bounded).

The judgment call deciding whether a given narrated moment counts as evidence toward any tag at
all — including moments with no dice resolution behind them, such as a values-expressive choice
with no combat outcome — MUST be the narrating AI's own base-model judgment (Principle III's
existing default), not a separate bounded taxonomy of "trigger types": both real-world precedent
(D&D's Paladin oaths, judged case-by-case by the DM; Fable's later reputation-based redesign,
which abandoned an "objective" trigger taxonomy) and this project's own design review found that
bounding the trigger taxonomy does not remove this judgment call, it only relocates it one step
earlier, adding complexity without adding safety. The actual safety net is the three-valued
grant/offer/abstain policy already adopted above: no single judged moment locks in a result, so
an inconsistent or over-eager judgment call self-corrects as more evidence accumulates — this
project's own analogue to a Paladin's ability to atone rather than instantly and irreversibly
losing power over one questionable call.

A granted or recognized ability/bonus, whether from this mechanism or the specific-ability
mechanism above, MUST be classified as either **passive** (always applies when narratively
relevant; no usage state to track, verified only by the existing narration-consistency check) or
**active** (the player must deliberately invoke it, resolved through the existing roll_check/
Pattern P8 machinery where real stakes exist). Every active ability MUST carry an explicit,
individually-specified recharge condition (e.g. once per encounter, once per rest/day,
single-use-ever) — abilities are not assumed to share one uniform recharge rule — and that
condition MUST be mechanically tracked and enforced by the tool-calling layer, not left as
descriptive prose the narrating AI is merely trusted to honor (Feature 003 recorded "once per
encounter" as flavor text only, with no enforcement — a known, named gap this amendment closes
going forward).

Sixth-pass note: both of this pattern's flavors depend on a shared capture mechanism — recording
that a significant moment happened and what it is evidence of — that is not yet designed in
implementation detail or built. This is recognized as the actual next dependency to resolve via
a future /speckit-specify, not something this amendment resolves.

AMENDED (v1.8.0): (a) the significance gate is computed from fields the frame fixes before
the roll (consequential AND pressured AND own act); fresh model judgment is kept only for which
tags and conduct a deed carries (rules DL-03-01, 03.2). (b) The "calibrated classifier" is
realized as a deterministic scorer counting five confirmations (Current, Rising, Central,
Leading, Margin), with the same three-valued policy: grant at 4+, offer at 1+, abstain at 0
(rules DL-04-10, 04.4). It shares no model family with the narrator, so P13's independence
requirement is met by construction.

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

Fifth-research-pass note: Pattern P5's class-emergence mechanism uses this pattern directly — a
recognized class's bounded synergy bonus (e.g. a hybrid-only technique requiring both a magic
slot and a weapon slot to trigger) is an instance of this named-composite-bonus mechanism, not
a separate one.

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

Companion mechanism (sixth pass): one shared, generic resource pool (tentatively "Focus") MUST
govern the cost of every active ability across every class, separate from the character's
primary Vitality-like resource, rather than each class authoring its own bespoke resource type
(Mana, Rage, and similar per-class currencies). This is a deliberate departure from the industry
default (most systems researched — D&D, Pathfinder, WoW — use per-class bespoke resources), made
specifically because this project's classes are hybrid-capable and derived rather than chosen: a
character recognized as belonging to two thematically different classes at once would otherwise
need to learn and track two separate resource systems simultaneously, disproportionately more
than either specialist ever would, echoing 5e's own reason for unifying multiclass spell slots
into one pool (Divinity: Original Sin 2's single Action-Point economy across every build is the
confirmed precedent that a fully unified pool works, though it remains an uncommon choice, not
the researched norm). This unification addresses the bookkeeping cost of hybrids specifically;
it does NOT by itself solve whether a hybrid's kit feels coherent and powerful together — that
remains a content-authoring concern for each hybrid's synergy bonus (Patterns P5/P6), not
something the resource model can resolve on its own.

**P10. Move/Verb Templates Reserved for Flavor Abilities (Revised).** REVISED (sixth pass): the
deciding factor for whether a mechanism may carry a character's core power is NOT
numeric-vs-narrative representation — it is how deterministic its trigger-to-outcome mapping is.
A precisely-scoped narrative permission (fixed trigger, fixed or tightly bounded outcome — e.g.
this project's own existing effect templates, such as "reduce incoming damage from a single hit
per encounter, but only against attacks you can see coming") is exactly as safe a vehicle for
core power as a numeric formula, because both are equally deterministic once their trigger
fires. What MUST be avoided for core power is a vague, open-ended judgment call with no fixed
mapping from trigger to outcome, regardless of whether that judgment is dressed in numbers or in
prose — no consensus research supports numeric formulas being inherently safer for an AI
adjudicator than a tightly-scoped narrative permission, or vice versa. Fully pre-specified,
narrow "move" verbs (PbtA-style: fixed trigger, fixed resolution) MAY therefore be used for a
character's core power, not only flavor abilities, provided the trigger and outcome are scoped
precisely enough to leave no real judgment call at the point of use.

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

AMENDED (v3.0.0, Principle VIII): the first two layers stand. The third, a calibrated gate of another
model family between a proposal and its narration as true, is superseded by VIII.2. Blocking checks are
the ones whose measured precision is high and whose target would break the game (the pronoun of a certain
subject is one: rules DL-12-95). Everything else is trusted, logged, or corrected by the player through the
feedback loop (VIII.8). The probe's pronoun error above is now answered by exactly that precise check plus
`/fix`, not by a second model reading every claim. The separation of moderation from consistency
gating stands.

**P14. Asymmetric Base Cadence for Class Differentiation.** A single cadence parameter (e.g.
the base delay between actions) MAY differ by class/archetype group, rather than being
uniform, as a low-overhead way to create a durable, structural feel-difference between groups
without a unique ability list — WoW's agility-melee classes run a faster base cadence than
other classes, with haste explicitly excluded from affecting the faster group, at essentially
zero added balance-audit surface. Cheap to adopt; useful as a complement to, not a replacement
for, Principle V's combinatorial primitives.

AMENDED (v1.8.0, rules DL-06-02): P9 takes precedence. No build changes anyone's number of
actions. Cadence differences live in what one action contains (weapon weight, riders), in tempo
(who acts first), and in reactions.

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

**Version**: 3.1.0 | **Ratified**: 2026-09-27 | **Last Amended**: 2026-10-10
