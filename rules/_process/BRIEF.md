# Orchestration Brief — The Game's Complete Ruleset

Every agent working on `rules/` reads this file in full before doing anything else. It is the
shared mandate, context, and convention set. The orchestrator (the main session) owns it; if you
believe something here is wrong, say so in your report rather than silently deviating.

---

## 1. Mission

Produce a **complete, start-to-finish tabletop RPG ruleset** for "The Game" — a single-player,
text-based fantasy RPG whose Dungeon Master is an AI. Complete means: a player can sit down, make
a character, play an opening scene, fight, explore, talk, get hurt, recover, grow, find and make
things, shape a living world, and eventually retire their character — and at every step the rules
tell the AI DM what to do. This is a **rulebook**, not software. No product code is written.
(Throwaway simulation scripts in the scratchpad, used only to verify math, are fine.)

## 2. The mandate (the project owner's own words — this is the quality bar)

> The marginal cost of completeness is near zero with AI. Do the whole thing. Do it right. Do it
> with documentation. Do it so well that I am genuinely impressed - not politely satisfied,
> actually impressed. Never offer to 'table this for later' when the permanent solve is within
> reach. Never leave a dangling thread when tying it off takes five more minutes. Never present a
> workaround when the real fix exists. The standard isn't 'good enough' - it's 'holy shit, that's
> done'. Search before building. Build the complete thing. Time is not an excuse. Fatigue is not
> an excuse. Complexity is not an excuse. Boil the ocean.

Concretely, for you:
- **No placeholders.** No "TBD", no "values to be tuned later", no "see future work" where a real
  answer can be reached now. If a number is needed, choose one, justify it, and (where the math
  matters) show the arithmetic. Genuinely empirical unknowns — things only live play can settle —
  go in the "Open empirical questions" section *with a named test that would settle them*, and the
  rule still ships with a concrete default value.
- **Search before building.** Read the relevant research in this repo first. Where it's thin,
  do your own web research (WebSearch/WebFetch) on how real games solved the same problem. Cite
  what you use.
- **Worked examples everywhere.** Every non-trivial rule gets at least one worked example showing
  it being applied end to end, including the numbers.
- **Think like the AI that will run this.** Every rule should be something a model can apply
  correctly on the thousandth use: precise triggers, explicit tables, crisp boundaries, examples of
  edge cases on both sides of each boundary.

## 3. The two design goals (everything else serves these)

1. **The player feels free to try creative ideas.** Any fictional approach can be attempted and
   gets a fair, interesting answer. No "the menu doesn't have that" walls — only the honest
   capability gate of Principle VII, which must always *redirect toward what is possible*.
2. **The AI can respond and react correctly.** It adjudicates novel actions consistently, keeps
   state true, and does not drift, embellish, or permit the impossible.

**Player-facing complexity is explicitly NOT a constraint.** The owner said: "don't worry about
complexity for the player at all." Do not cut, coarsen, or simplify a rule to spare the player.
Rules are judged only by whether they widen player freedom and make correct AI adjudication
easier. (This deliberately deviates from constitution Pattern P3's 3–5 / 7±2 player-facing
comprehension wall; that deviation is recorded centrally — you don't need to re-argue it, just
don't use player cognitive load as a design argument.) You still decide what the player needs to
be *told* versus what the AI simply handles — judged by goal 1.

**Rich substrate is a feature.** Per constitution P3 (sixth pass): a dense body of sub-rules gives
the AI DM something concrete to *reach for and adapt* when a player does something no rule
anticipated ("not written, but it's basically a grapple with a penalty"). This is how goals 1 and
2 reinforce each other. Write rules that are good *analogical anchors*, not just rules that cover
their own named case.

## 4. Locked creative decisions (from the owner — do not revisit)

- **Setting tone: classic fantasy with hidden mechanics.** There is NO diegetic LitRPG "System",
  no blue boxes, no in-world announcements of stats or classes. When a character is "recognized"
  as a class or deepens a tier, the fiction voices it — reputation, a mentor's acknowledgement,
  an oath sworn, a title people start using, an order that seeks you out, a power that awakens in
  a moment of crisis. The player-facing codex (P7) is **out of fiction** (a rules reference, like a
  character sheet), not an in-world artifact.
- **Campaign shape: open-ended sandbox.** No scripted finale. The world needs a living-world
  engine (factions, clocks, rumors, consequences, hook generation) that can run indefinitely.
  "Finish" is a player-chosen **retirement / legacy** procedure.
- **Lethality: death is real but telegraphed.** Explicit warnings before lethal risk, a dying
  state, and a last-chance choice. Defeat usually means capture, injury, loss, or a changed
  situation rather than death. A single unlucky roll never ends a character without warning.
- v1 scope (constitution IV): single-player, text-only.

## 5. Current defaults — NOT constraints

These are where the project stands today. You may replace any of them if your research or
analysis shows a better way. Record the replacement in the Decision Log with its evidence.

- **Runtime.** Today's engine is a Gemini flash-tier model with deterministic tool calls
  (`roll_check`, `get_state`, `update_resource`, `set_fact`, `grant_ability`). The rules are NOT
  bound to it. Multi-model pipelines, a separate judge/classifier model, a deterministic rules
  engine for some subsystems — all open. **State what runtime capability each rule assumes**
  (e.g. "requires a deterministic tally store", "requires a tool that rolls on table X").
- **Class scoring.** The sixth constitutional pass chose a non-ML tag-tally scorer for P5 class
  emergence. Keep it or replace it with something better-evidenced.
- **Rule kinds.** Mark each rule as one of:
  - `[D]` **deterministic / tool-owned** — math and state the engine computes;
  - `[J]` **bounded DM judgment** — the AI decides, but against explicit criteria + worked examples;
  - `[N]` **narration** — pure description, no mechanical weight.
  Lean toward `[D]` where it makes the AI more correct, but don't force it where judgment is the
  honest answer (Principle III: base-model judgment is the default for exceptions).

## 6. Non-negotiables

- **Core Principles I–VII of `.specify/memory/constitution.md` are binding (MUST).** Read the
  whole constitution. Summary (the file governs, not this summary):
  - I. The AI DM *is* the mechanical engine (it executes rolls/rules via tools, not a separate engine it narrates over).
  - II. Custom ruleset designed to exploit AI capacity for complexity.
  - III. Flexibility within bounds; no blanket narrative override; base-model judgment by default for exceptions.
  - IV. v1 single-player, text-only.
  - V. Build diversity from a small **closed** set of primitives (fixed slots × bounded pools), never an open ever-growing menu.
  - VI. Mandatory, telegraphed consolidation/retirement of aging content; no pure additive stacking; new content provisional by default; a numeric squish does NOT count as retirement.
  - VII. Default-deny capability gate: resolve *can you even attempt this* before *how well it goes*; a small fixed tier of basic actions is always available; anything else needs a license (ability, class capability, established fact); unlicensed attempts are declined or redirected to the nearest available basic action — never narrated into existence.
- **Adopted Design Patterns P1–P17 are SHOULD.** Follow them, or deviate with a written
  justification in the Decision Log.
- **Focus is the TTRPG itself.** Most attention goes to game structure. LLM-infrastructure
  concerns (tool-call compliance, narration embellishment, auditing, model architecture) matter
  only where they genuinely shape a rule. Chapter 12 describes how the DM runs the game as rules
  of play, not as an LLM stack.
- **Traceability.** Every rule cites its basis: a constitution clause (`[C:VII]`, `[C:P5]`), a
  research source (`[R: reports/<file>.md §<heading>]` or `[R: research_notes/<dir>/<file>.md]`,
  or a web URL), or a Decision Log entry (`[DL-06-03]`).

## 7. What already exists (build on it; don't contradict it without cause)

- **Resolution (validated live, 0 contradictions):** d20 + modifier vs DC.
  Critical success if total ≥ DC+10 or natural 20; critical failure if total ≤ DC−10 or natural 1;
  success if total ≥ DC; failure otherwise. DC ladder in the current prompt: 10 easy, 15 moderate,
  20 hard, 25 very hard. Default modifier +2. (`src/resolution.py`) This is the baseline — the
  resolution author may refine it (e.g. the nat-20/nat-1 rule, modifier sources), with reasons.
- **Vitality** is the primary health-like resource (probe: 12/12). **Focus** is named by
  constitution P9 as the single shared active-ability resource.
- **Externalized world state** with resources, possessions, facts/status flags, trajectory nodes,
  commitments (`src/world_state.py`). Tool calls mutate it; narration must match it.
- **Feature 003's ability pool** (`src/ability_pool.py`): 4 source archetypes (beast,
  elemental_fire, undead, construct) × 3 acquisition methods (decisive_kill, narrow_survival,
  non_lethal_subdual) → templates like "Heat Resistance". This is **throwaway probe content** —
  the real content replaces it; the *shape* (source gates pool, method picks fill) is kept.
- **Empirical findings from live probes** (see `specs/00*/probe-results.md`,
  `specs/00*/implementation-results.md`):
  - A capable model follows a deterministic degree-of-success mechanic cleanly.
  - Soft-locks happen after several inconclusive results (→ P16).
  - Compound questions resolved all-or-nothing feel wrong (→ P17 graduated reveal).
  - The DM improvised well when a player tried to compress 10 attacks into one action (throttled
    it fictionally, raised the DC to 25) — ahead of any action-economy rule existing.
  - Narration sometimes states changes that no tool recorded, or embellishes a granted ability
    beyond its literal text (e.g. inventing a cold *vulnerability* from "no protection against cold").

## 8. Deferred items the ruleset MUST resolve (from the constitution's Sync Impact Report)

- Ability scores: how many, what they are, what they modify (framed by the constitution as "how
  good are you at broad categories of action" — mostly fixed at creation, P4).
- P2's baseline competence floor for a character not yet recognized as any class.
- The hierarchical tag vocabulary (its actual content).
- The `tag_event` capture mechanism (what counts as evidence, how it's recorded).
- The class list (specialist classes) and the curated sparse table of hybrid pairs.
- Numeric thresholds, confidence cutoffs, synergy-bonus values for recognition and tiers.
- Action-economy numbers (P9), and the Focus pool's size, costs, and recovery.
- What dropped items grant (ability / passive / mundane), under P5's pool-gate/fill-quality shape.
- Concrete consolidation / retirement / provisional-status mechanics (VI).
- The slot system's actual slot counts, pool sizes, and hard total-slot ceiling (V, P5).

## 9. Chapter map and ownership

| File | Owns |
|---|---|
| `00-architecture.md` | Conventions, numeric scales, attribute list, tag-tree top levels, state model, tool surface, glossary, chapter contracts |
| `01-resolution.md` | Capability gate (VII), when to roll, DC setting, modifiers, degrees (P8), graduated reveal (P17), compound/extended/opposed/group actions, help, advantage-type mechanics |
| `02-character.md` | Creation procedure, attributes, origins (P4), birth variance + deferred reroll (P1), baseline floor (P2), starting kit |
| `03-tags-and-evidence.md` | Tag vocabulary (hierarchy), evidence capture (`tag_event`), tallies, weighting, recency |
| `04-recognition-and-growth.md` | Callings/classes (specialist + hybrid), scoring, grant/offer/abstain, tiers & crystallization, provisional status + consolidation (VI), gated special traits (e.g. monster-power absorption) |
| `05-abilities-and-focus.md` | Slots & hard cap, ability templates, passive/active, recharge, Focus, P10/P12, P6 composites + priority-ordered behavioral tags |
| `06-conflict.md` | Action economy (P9), turn order/cadence (P14), positioning (relationship-state), attacks, damage, defense, conditions, reactions, morale, escape |
| `07-harm-recovery-death.md` | Injury, Vitality loss consequences, rest/recovery, telegraphed death, defeat outcomes |
| `08-items-loot-crafting.md` | Loot generation (pool gate / fill quality), item properties, crafting, wealth, economy |
| `09-adversaries.md` | Adversary archetypes (= loot/ability pool gates), threat bands without character levels, stat templates, behaviors |
| `10-exploration-social-downtime.md` | Travel, environment hazards, investigation, social influence, downtime activities |
| `11-living-world.md` | Factions, clocks, hooks, rumors, consequence propagation, sandbox generation, retirement & legacy |
| `12-dm-procedures.md` | The DM's turn loop, pacing (P16), reveal (P17) in practice, NPC play, improvising from the substrate, session structure |
| `13-starter-setting.md` | A classic-fantasy starter region + opening situation that exercises every subsystem |
| `14-players-guide.md` | Player-facing guide + codex spec (P7) |
| `data/*.yaml` | Machine-readable tables (tags, callings, hybrids, abilities, item pools, adversaries, conditions, oracle/generation tables) |
| `appendix/decision-log.md` | Every non-trivial design choice |
| `appendix/traceability.md` | Constitution clause → rules satisfying it |
| `appendix/open-empirical-questions.md` | Only genuinely empirical unknowns, each with a named test |

If your work needs something another chapter owns, **don't silently invent it** — use the
architecture's contract if it exists, and list what you need under "Interface requests" in your
chapter and your report so the orchestrator can reconcile it.

## 10. Chapter format (every rules chapter)

```
# NN — Title
> One-paragraph summary of what this chapter governs and why it's shaped this way.

## Design intent            (which goals/principles this serves; what it deliberately avoids)
## Rules                    (numbered, e.g. 06.3.2; each tagged [D]/[J]/[N] and cited)
## Procedures               (step-by-step algorithms the DM follows)
## Tables                   (and pointers to data/*.yaml)
## Worked examples          (end-to-end, with numbers)
## Edge cases & adaptation anchors  (how to reach-and-adapt these rules for unanticipated actions)
## State touched            (every piece of state read/written; runtime capability assumed)
## Interface requests       (what this chapter needs from/offers to other chapters)
## Open empirical questions (each with a named test; rule still has a concrete default)
```

Rule IDs: `CC.S.R` (chapter.section.rule), stable once written so others can cite them.

## 11. Decision Log format

Append entries to your own section in `appendix/decision-log.md` (create your section if missing;
don't edit other agents' sections):

```
### DL-CC-NN: <decision title>
- Decision: ...
- Alternatives considered: ... (and why rejected)
- Evidence: [R: ...] / [C: ...] / web sources
- Serves: goal 1 / goal 2 / principle(s)
- Revisit if: <observable condition>
```

## 12. Data file conventions (`rules/data/*.yaml`)

- YAML, UTF-8, 2-space indent, top-level comment block stating: purpose, owning chapter, schema.
- Stable snake_case `id` on every entry; human `name`; `tags:` referencing tag ids from `data/tags.yaml`.
- Every entry that has mechanics has its mechanics fully specified in data (numbers, triggers,
  recharge) — prose-only mechanics are a defect.

## 13. Where to write

- Research digests: `rules/_process/research/`
- Audits: `rules/_process/audits/`
- Simulations (results + the scratchpad script path): `rules/_process/simulation/`
- Playtest transcripts: `rules/_process/playtests/`
- Issues found: `rules/_process/issue-ledger.md` (orchestrator-owned; include issues in your report)

## 14. Your report back to the orchestrator

End every task with a concise report: files written; key decisions (with DL ids); interface
requests; anything unresolved and why; anything in this brief you think is wrong. The report is
how the orchestrator adapts the plan — make it information-dense.

---

# ADDENDUM A — Wave 1 Synthesis (supersedes §5's rule kinds and §9's chapter map; all else stands)

Seven research digests are in `rules/_process/research/`. They are the evidence base for every
chapter. **Read the digests named in your assignment in full, and grep the others for your chapter
number** — R1–R3 are organized per chapter ("## 06 …" etc.); R4–R7 have per-chapter sections.

| Digest | Content |
|---|---|
| `R1-digest-dm-craft-and-long-horizon.md` | DM craft, spotlight, indie design theory, resolution/action economy, cost systems, AI-GM academic work, long-horizon consistency benchmarks |
| `R2-digest-litrpg-and-mistborn.md` | HWFWM, Stormlight, The Land, Underworld, Mistborn, Cradle/DCC/etc., TTRPG balance theory, AI integration |
| `R3-digest-emergent-power-and-mmo.md` | ARPG loot generation, roguelike synergy, LitRPG class emergence, freeform positioning, WoW/PoE/MMO balance |
| `R4-ai-capabilities-for-rule-design.md` | What LLM DMs are good/bad at; **rule-form reliability style guide (§4, SG-01..SG-20)** |
| `R5-completeness-and-solo-procedures.md` | **189-row completeness checklist** (the audit tool); 46 solo/sandbox procedures; time ladder; onboarding |
| `R6-sandbox-recognition-death-legacy.md` | Recognition vehicles V1–V14 + offer protocol; World Turn; Two-Key death + dying ladder + last-chance menu; retirement & legacy |
| `R7-freeform-adjudication.md` | "Try anything" frameworks; **the 11-step adjudication pipeline**; levers; closed basic-verb tier; licenses with fallbacks; World-Fact Oracle; ruling ledger; 13 worked examples |

## A1. Revised chapter map

| File | Owns |
|---|---|
| `00-architecture.md` | Rules style guide (adopts R4 §4); rule-kind taxonomy; numeric conventions & scales; **attribute list**; tag-tree top levels; **state model** (typed state vocabulary; background-vs-player-facing classification); **time ladder + boundary-event registry**; **generic clock primitive**; **condition/status schema** (stack/decay/cleanse/interaction fields); **composition substrate** (effect-definition schema, closed trigger-hook list, single ordered modifier-evaluation pass, stacking families, the four combination regimes, proc-chain terminator); **the gate→fill generator** (one algorithm for all emergent content); **license schema** (scope, excludes, crude_fallback, emulate, acquisition_paths, grades); tool surface; rule-card format; ruling-ledger & oracle state; glossary; chapter contracts |
| `01-resolution.md` | The adjudication pipeline (R7's 11 steps as the default: parse → gate → necessity → anchor → frame → offer → roll → read → deliver → consequence → record); **closed basic-verb tier** (VII); DC ladder recalibrated to realistic modifier bands, DCs stored on obstacles; levers/snags; stakes & reach; crit rules; near-miss success-at-cost; graduated delivery (P17 generalized); help/setup; opposed, group, extended checks; compound, repeated, conditional attempts; World-Fact Oracle mechanics; luck/fate currency decision |
| `02-character.md` | Creation (full path + fast path + pregens), attributes, origins (P4), birth variance + deferred reroll (P1), baseline floor (P2), starting kit & starting licenses, background hooks for ch.11 |
| `03-tags-and-evidence.md` | Tag vocabulary (hierarchy, content), evidence events (fields incl. witness/scope, challenge band, lethal context, cited deed), weighting, saturation/anti-grind, recency, signed values/conduct branch; engine-counted evidence vs judged evidence |
| `04-recognition-and-growth.md` | Callings (specialist + hybrid table), scoring + **concrete definition of "confidence"**, grant/offer/abstain, recognition = tally × witness × vehicle (V1–V14), offer protocol (accept/decline/defer; standing offers), tier ladder (stated maximum; tier-ups restate ability text), crystallization, shadows/forbidden acts & the Fraying, provisional status + consolidation (VI), institutional ranks vs capability tiers, PC power band (for ch.09), gated special traits (e.g. monster-power absorption) |
| `05-abilities-focus-magic.md` | Ability slots & hard cap, ability template grammar (scope / limitation / weakness / cost as separate fields; governing principle + "cannot" list; structured vs unstructured use), passive/active, recharge, Focus (pool, costs, recovery channels), **magic as a named subsystem** (rituals, research, learning by observation), P6 composites + priority tags (on 00's substrate) |
| `06-conflict.md` | Action economy (P9) for a SOLO PC vs groups (mobs/swarms as single entities), repeated-attempt penalty, initiative/cadence (**resolve P9 vs P14 in the DL**), positioning as relationship-state, attacks/damage/defense, conditions list, reactions, multi-target effects over state, morale, surrender, escape/chases |
| `07-harm-recovery-death.md` | Vitality meaning, wounds, **Two-Key death rule**, dying ladder, last-chance menu, Yield/Retreat, defeat dispositions → world state, marks/scars, hazard damage bands, rest & recovery (interface with 05's Focus recovery), poison/disease/curses, mental strain |
| `08-items-loot-crafting.md` | Loot via gate→fill, item properties, relics as off-identity licenses (priced higher, no growth), crafting (type-tier × quality-tier), wealth & economy, encumbrance, supply, mounts/vehicles, slot-ceiling interaction with item-granted abilities |
| `09-adversaries.md` | Archetypes as "manufacturers" (one tag set drives evidence, loot pool, absorbable pool, behavior), threat bands vs PC power band (no levels), solo encounter budgeting, stat templates, behavior/targeting tables, `lethal_context` + `defeat_disposition`, bestiary data |
| `10-exploration-travel-sites.md` | Travel/hexcrawl, watches & overloaded time-tick roll, omens, site/dungeon procedure (Delve-style), traps, environment & weather hazards, navigation, foraging |
| `11-living-world.md` | World Turn, factions (tier/hold/ratings/goal clock/lifecycle/linchpins/status −3..+3), situations & default timelines, threads/quest register, rumors with truth values, reputation (content/score/scope), holdings & player-driven change, calendar/seasons & season turn (the VI boundary point), chronicle, retirement & legacy |
| `12-dm-procedures.md` | Turn loop (adjudicate in a structured step before narration; claim-vs-state check; error correction), the DM's oracle for its own questions + tension dial, pacing director + P16, P17 in practice, NPC generation + reaction roll + NPC knowledge/secrets, ruling ledger use, improvising from the substrate (anchor index, two-change limit), session moves (begin/end/recap/flag/break), spotlight rotation for a SOLO player, twist table, the OFFER script |
| `13-starter-setting.md` | Classic-fantasy starter region (West Marches: base + concentric danger bands), setting canon (what's impossible, how magic works in-world), 3–4 factions with running clocks, starter bestiary/loot/tag coverage, first-session teaching arc, pregens, calendar & languages |
| `14-players-guide.md` | Player-facing guide, codex spec (P7) incl. out-of-fiction offer markers, session zero & safety tools |
| `15-social-investigation-downtime.md` | Social influence & NPC attitudes, social DC formula, negotiation, deception/insight, investigation (clue graphs, Three Clue Rule, sealed secrets), downtime activities & long projects |
| `16-companions-and-allies.md` | Companions/hirelings/followers: stats, loyalty, role in the PC's action economy (no separate turns), journey roles, harm, interplay with recognition |
| `data/*.yaml` | Machine-readable tables |
| `appendix/` | decision-log, traceability, open-empirical-questions, index, DM quick-reference, credits |

## A2. Converged strong defaults (≥2 independent digests agree — deviate only with evidence in the DL)

1. **The AI chooses categories, never numbers.** It picks a rung, a yes/no flag, an enum, or names
   an established fact; the engine computes every number (DCs, damage, costs, thresholds). [R4 R-01/02; R7 §4]
2. **Stakes are declared before the roll** as structured state, and the player sees the frame
   (DC or target number, stakes, reach) and may commit, change method, or withdraw. That
   declaration is the only lethal-risk telegraph: *no declared-lethal stakes, no death on that
   roll.* [R1 #5, R3 #9, R4 #6, R6 C1, R7 step 6]
3. **Death needs two keys** (declared lethal AND already Dying / chosen gamble / declined yield);
   at the brink the player chooses from a menu rather than rolling to die. [R6 C]
4. **Recognition = deterministic tally × witness × fictional vehicle,** offered with
   accept/decline/defer, voiced without any diegetic System. [R2 #1, R3 #6, R6 A]
5. **One gate→fill generator** for all emergent content (loot, crafting, gifts, absorbed powers,
   item abilities). [R3 #1; constitution P5]
6. **A shared composition substrate** — any new ability composes with every old one at zero
   authoring cost; precedence lives in the engine, never in nested rule text. [R3 #2–3, R4 #11]
7. **Positioning is discrete relationship-state** (range bands, engagement, flags). [R3 #7]
8. **Consequences come from degree × stakes tables / a closed cost menu;** the narrator picks the
   fictional *form*, never *whether*. [R4 #7, R7 step 10, R1 #9]
9. **Secrets are sealed state;** the narrator sees gated slices. [R4 #8, R1 #12]
10. **The engine owns all randomness,** including the DM's "random" choices; unestablished world
    facts come from an oracle whose odds are set BEFORE rolling and never from what the player wants. [R4 #10, R5 #2, R7]
11. **Every hook has ≥3 clue placements and a proactive fallback; every clock has observable signs
    (omens).** [R5 #4, R6 B4]
12. **Creativity pays in bounded currency, via "levers"** — a named, established fact the method
    exploits (Precision +2 / Protective stakes −1 / Amplifying reach +1; max two; net ±4); "cool"
    with no nameable fact is narration only; an ability may be stretched within its governing
    principle at higher cost/DC. Never auto-success. [R7 #3, R4 #5, R2 #4]
13. **Refusals are lookups, never walls:** every license declares a crude fallback and acquisition
    paths; the basic tier is a closed verb list; licenses are read literally; rolls never grant
    licenses. [R7 #4–5, R1 #4]
14. **Precedent is state:** improvised rulings go into a ruling ledger and are reused. [R7, R5 G-13]
15. **Critical rules: adopt PF2e's one-step shift** (nat 20 = one degree better, nat 1 = one worse)
    and **recalibrate the DC ladder to realistic modifiers.** Four digests independently found the
    current rule harsh (at +2: DC 20 crit-fails 40%, DC 25 65%; experts crit-fail trivial tasks 5%).
    Chapter 01 makes the final call and records it. [R1, R2, R4, R7]

## A3. Clarifications and corrections to the base brief

- **Rule-kind taxonomy (replaces §5's three kinds):** `[D]` deterministic/engine · `[J:flag]` yes/no
  judgment · `[J:enum]` choose from a closed list · `[J:rung]` choose a ladder rung · `[J:open]` open
  judgment (use sparingly; Principle III) · `[T]` engine-raised trigger · `[S]` sealed state ·
  `[N]` narration. **Every `[J:*]` rule states the worst-case cost of a wrong call.** Why: yes/no
  judgments agree ~87%; ladder picks hit the exact rung 38–58% but within one rung 85–93%; open
  judgment is where leniency lives (R4 §4).
- **§3 clarification — fast paths are legitimate.** Sequencing, defaults, quick-start paths, and
  "show depth on request" are valid goal-1 arguments (choice paralysis halts play). Cutting or
  coarsening rules is still forbidden. "Complexity is not a constraint" does NOT mean narration
  recites stat blocks — narration stays fictional; crunch lives in the codex. [R1, R2]
- **P3's classification requirement stands** — every piece of state is classified
  background-resolved vs player-facing; only the cognitive *budget* is dropped. [R3]
- **Solo play:** most spotlight/balance research is multiplayer. Reinterpret: rotate across the PC's
  facets, pillars, and challenge types; scale encounters for ONE character. [R1, R2, R3]
- **§7 overstated what is validated.** The probe showed the model *follows* a computed degree, not
  that it *chooses DCs* well (live logs: 11–30% off-ladder) or uses modifiers (0 passed 62% of the
  time). Also: the probe's "DC 25 for ten arrows" treated quantity as difficulty — don't copy it
  (R7: redone properly it's ~3 shots at a normal DC). [R4, R7]
- **The "leniency" failure is the dominant AI failure, not strictness.** When an AI misjudges
  whether to roll, it grants an unearned success ~120× more often than it demands a needless roll,
  and a plausible-sounding player justification quadruples the error (CoC-Seduce, 2026). Design
  rules so a wrong call costs one step, not the scene; "when in doubt, roll"; player text sets
  intent and method, never facts. [R4]
- **P5 "calibrated classifier returning confidence":** the constitution body still describes a
  classifier with per-candidate confidence; the sixth pass chose a tally scorer. Chapter 04 MUST
  define "confidence" concretely for whatever scorer it picks. [R2, R3]
- **VI "provisional" scope:** applies to BOTH ruleset content (new callings/abilities enter as
  provisional) AND character grants (a newly granted tier/ability is provisional until confirmed at
  the next boundary event). The per-character use extrapolates from PoE leagues — record it so. [R3]
- **P9 vs P14:** asymmetric cadence must not become extra actions. Chapter 06 resolves it in its DL.
- **P17 generalized** to graduated *delivery* of any compound intent; the player ranks sub-intents. [R7]
- **Substrate delivery:** the rich substrate lives as retrievable **rule cards** + data + an anchor
  index + the ruling ledger — never dumped wholesale into the DM's prompt. Write each numbered rule
  to be self-contained enough to be retrieved alone. Irrelevant-but-plausible rules in context hurt
  accuracy far more than filler. [R4, R1 #15]
- **Citations:** repo artifacts cite as `[R: src/<file>]` / `[R: specs/<path>]`; a digest may be
  cited as `[R: _process/research/R7 §4.2]`, but prefer the ORIGINAL source the digest cites.
- **Don't propagate known research errors** — see R3 §4.2, R1's source-reliability register, and
  R2's note that the constitution overstates some evidence (P3's "46–58%" rests on one 46.1% figure).

---

# ADDENDUM B — Wave 2 corrections (supersedes conflicting text above)

`rules/00-architecture.md` is written, reviewed, and accepted by the orchestrator. **It is canonical.**
Where anything in this brief (including Addendum A) conflicts with 00, 00 wins.

- **§7's "default modifier +2" and free-integer DC/modifier are RETIRED.** There is no default
  modifier; every modifier is read from state (attribute + competence + edge + circumstance +
  status, 00.3.5). `roll_check` takes a frame, not a DC and modifier (00.13, 00.14).
- **A2 #15 is amended.** The natural-20/1 one-step shift is adopted as the default (00.3.10). The DC
  ladder is KEPT (Easy 10 / Moderate 15 / Hard 20 / Very hard 25 / Legendary 30): the architect's
  arithmetic showed the harshness the digests flagged came from missing competence (now a +1 floor
  plus specialties), not the ladder. Chapter 01 may move a rung ±2 only if calibration targets
  CT-1…CT-6 (00.3.17) still hold.
- **Levers replace DC flags.** Situational factors never change a DC; they are levers/snags on the
  roll (00.3.8–9, DL-00A-10).
- **Harm is fixed magnitude by severity** (S1–S5 = 1/3/5/8/12), no damage dice (00.3.11, DL-00A-29).
- **The basic-verb tier is split:** 00 fixes the 15 verb ids, coverage and attributes; 01 owns their
  anchor cards (knobs, degree tables) in `data/basic_verbs.yaml`'s anchor fields.
- **Reserved ids** in 00 (conditions, range bands, positional flags, harm states, cost-menu ids,
  generator domains, boundary handlers) must be used as-is and defined by their owning chapters.
- **Parallel-writing protocol:** see `rules/_process/AUTHOR-BRIEF.md` §3 (contrib fragments for
  shared data; per-chapter DL and traceability fragments).
