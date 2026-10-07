# 00 — Architecture

> This chapter is the spine of the ruleset. It fixes the conventions every other chapter is written
> in (rule form, rule kinds, citation, precedence), the numeric envelope every number must sit inside
> (dice, modifiers, Vitality, Focus, severity, stakes, reach, bands), the seven attributes, the top
> levels of the tag vocabulary, the typed state model and who owns each piece of state, the time
> ladder and the registry of what happens at every time boundary, and the shared mechanical
> primitives that sixteen chapters build on in parallel: one clock, one condition schema, one
> composition substrate for effects, one gate→fill generator for all emergent content, one license
> schema for the capability gate, one resolution frame, one tool surface, one rule-card format, one
> data-file convention, and one glossary. It is shaped by a single finding that recurs across all
> seven research digests: an AI Dungeon Master is excellent at *interpreting* free-form intent into a
> closed vocabulary and poor at *choosing numbers, remembering situational rules, resisting
> persuasion, keeping secrets, and imposing loss*. So this chapter makes the AI's job classification
> onto closed lists and makes everything else deterministic, stored, and triggered — which is what
> lets the player try anything (goal 1) while the AI still rules it correctly (goal 2).

**Reading this chapter.** 00 is written in the standard chapter format (00.19). Its *Rules* section is
organized in nineteen parts (00.1–00.19); its *Tables* section holds the reference tables the rules
cite (T-00-*); its *Procedures* section holds the algorithms (PR-00-*); its *Worked examples* follow one
continuous character, **Wren**, through a two-day journey, a fight, a loot drop, a locked door, a
racing alarm clock, and a precedent reused (WE-00-1…9). Every example number that a later chapter
owns is marked *(illustrative; ch.NN owns)*. The machine-readable companions are
`data/tags.yaml`, `data/attributes.yaml`, `data/scales.yaml`, `data/substrate.yaml`,
`data/effects.yaml`, `data/basic_verbs.yaml`, `data/boundaries.yaml`, and `data/SCHEMAS.md`.

---

## Design intent

**Goals served.** Goal 1 (the player feels free to try any creative idea) and goal 2 (the AI responds
and reacts correctly) [BRIEF §3]. Every structure below is judged only by those two tests.
Player-facing complexity is not a cost [DL-00-01]; *what the player is told* is still decided by
goal 1 (00.6.4 visibility classes).

**The architectural bet, in one paragraph.** The research shows the AI's errors are *directional*
(toward leniency: ~120× more false passes than false checks, and a plausible player justification
roughly quadruples the error rate) and *form-dependent* (yes/no judgments ≈87% exact agreement;
closed-set classification ≈94–97%; 5-rung ladders 38–58% exact but 85–93% within one rung; nested
exceptions fail systematically) [R4 §1, §3.3; R: https://arxiv.org/abs/2607.02802;
R: https://arxiv.org/abs/2603.00077; R: https://arxiv.org/abs/2607.23386]. This project's own logs
show the concrete version: 11% of DCs off the stated ladder and a model-supplied modifier of 0 in 62%
of checks [R4 §3.4]. Therefore this chapter (a) moves every number, sum, stack, precedence, counter
and random choice into deterministic tools; (b) reduces every remaining AI judgment to its most
reliable form — flag, then enum, then rung, then open judgment only where unavoidable; (c) caps the
damage any single wrong judgment can do to one step, one tick, an offer, or a reversible change; and
(d) makes situational rules *fire from tracked state* instead of relying on recall. The richness of
the substrate is kept — maximized, per constitution P3 — but it lives in retrievable rule cards, data
files, an anchor index, and a ruling ledger, never dumped wholesale into the DM's context [BRIEF A3].

**What this chapter deliberately avoids.**
- Numbers chosen by the AI. The AI picks rungs, flags, enums, fact ids; tools compute [BRIEF A2 #1].
- Free-standing bonuses. The only situational currency is the *lever* (and its mirror, the *snag*),
  which must cite an established fact [BRIEF A2 #12; R7 §4.2].
- Pairwise interaction rules. Every effect declares one of four combination regimes; precedence is a
  single ordered pass evaluated by the engine [R3 §6 #2–3].
- Bespoke generators. One gate→fill algorithm serves loot, crafting, gifts, absorbed powers,
  item-granted abilities and birth variance [C:P5; R3 §6 #1].
- Bespoke clocks, bespoke condition formats, bespoke time rules. One of each [R5 §3; R2 #3].
- Character levels. The word *level* is not used in rules text; power is read from recognized tiers
  [C:P2].
- A diegetic System. Every mechanism here is out of fiction; the fiction voices it [BRIEF §4].

**Principle I, stated precisely.** In this ruleset "the engine" and "the tool" mean the deterministic
instruments the AI DM operates. The DM decides *when* to call them, *what* to classify, and *how* to
narrate the result; the tools do the arithmetic, the dice, and the bookkeeping. The DM remains the
mechanical engine of the game in the constitution's sense: nothing happens that the DM did not set in
motion, and nothing the DM sets in motion bypasses the instruments [C:I; C:P13; R1 §4 T-18].

---

## Rules

Rule IDs are `00.S.R`. Kinds follow 00.2.2. Every rule cites its basis. Digest shorthand:
`[R1 §x]` … `[R7 §x]` means `[R: _process/research/R<n>-<name>.md §x]` (full file names in 00.1.6).

### 00.1 Reading the ruleset

**00.1.1 Audience map.** `[N]` The ruleset has three audiences, and every chapter marks which parts
serve which.

| Audience | Reads | Needs from the text | Never receives |
|---|---|---|---|
| **Player** | 14 (Player's Guide), the codex (14), OFFER lines, out-of-fiction markers | What they may try, what it costs, the odds, what they know | Sealed state; raw tallies; adversary stat blocks |
| **AI DM** (runtime) | The always-loaded core (00.15.4), rule cards retrieved per situation, data entries, active triggers, the ruling ledger | Closed choices with "true only when" definitions; examples on both sides of each boundary | Whole chapters at once; sealed state until unsealed |
| **Implementer** (engine builder) | 00 (all), `data/SCHEMAS.md`, every chapter's *State touched* and *Tables* | Types, schemas, tool contracts, runtime capabilities | — |

**00.1.2 How the chapters relate.** `[N]` 00 fixes form and interfaces. 01 is the adjudication
pipeline every action passes through. 02–05 build the character (creation, evidence, recognition,
abilities). 06–07 are conflict and harm. 08–09 are things and foes. 10, 15, 16 are the other pillars
(exploration and travel; social, investigation and downtime; companions). 11 is the world that moves.
12 is how the DM runs the turn loop over all of it. 13 is content that exercises every subsystem.
14 is what the player sees. Dependencies run downward only through the contracts in 00.17; no chapter
reaches into another chapter's state except through a named interface.

**00.1.3 Reading order.** `[N]` Implementers and chapter authors: 00 → 01 → 12 → 03 → 04 → 05 → 06 →
07 → 02 → 08 → 09 → 10 → 15 → 16 → 11 → 13 → 14. Players: 14 → 13 (opening only) → the codex. The AI
DM at runtime reads nothing in order; it receives the core (00.15.4) plus retrieved cards.

**00.1.4 Precedence of rules.** `[D]` When two rules seem to conflict, apply the first matching line
(a flat, first-match list; no nesting) [R4 SG-10]:
1. The constitution's Core Principles I–VII.
2. The invariants of this chapter (T-00-1).
3. The rule of the chapter that owns the state family being changed (00.6.3).
4. A license's literal scope, for the part of the beat it covers (00.12.4).
5. A data-file entry over any prose paraphrase of it (data is canonical for numbers and ids).
6. A ruling-ledger precedent over fresh improvisation, unless a stated fact differs (00.15.6).
7. Otherwise: apply whichever reading grants less (no success, no license, no fact) and roll if in
   doubt; log a ruling and an issue for the orchestrator [R4 SG-05].
State always beats narration; among state writes, the latest write wins [R1 §4 T-14].

**00.1.5 Precedence of concerns.** `[J:enum]` When the DM must trade concerns off (not rules — goals
within the rules), the order is: (1) the player's safety settings (lines and veils, 14); (2) state
truth — never narrate against state; (3) rules integrity — no MUST is broken; (4) player intent
fidelity — acknowledge the stated intent, never substitute another, never silently reset
[R1 #3]; (5) fairness — declared stakes are honored exactly; (6) pacing and drama. *Worst case (J) of a
wrong call:* a scene paced worse than it could be; items 1–5 are protected by `[D]` rules elsewhere.
[R1 §4 T-7]

**00.1.6 Citation conventions.** `[N]` Every rule cites its basis in one of these forms:
`[C:VII]`, `[C:P5]` (constitution); `[DL-06-03]` (decision log); `[R: src/resolution.py]`,
`[R: specs/<path>]` (repo artifacts); `[R: <url>]` (web sources — preferred over a digest when the
digest cites an original); digest shorthand `[R1 §x]` = `R1-digest-dm-craft-and-long-horizon.md`,
`[R2 §x]` = `R2-digest-litrpg-and-mistborn.md`, `[R3 §x]` = `R3-digest-emergent-power-and-mmo.md`,
`[R4 §x]` = `R4-ai-capabilities-for-rule-design.md`, `[R5 §x]` = `R5-completeness-and-solo-procedures.md`,
`[R6 §x]` = `R6-sandbox-recognition-death-legacy.md`, `[R7 §x]` = `R7-freeform-adjudication.md`, all in
`rules/_process/research/`. Don't propagate the research errors logged in R1's reliability register,
R2 §4.2 and R3 §4.2 [BRIEF A3]. Text changed at integration carries a marker: `[amended: DL-…]` (or
`[amended: IR ch.NN]`, an orchestrator-approved amendment recorded in `_process/INTERFACE-REQUESTS.md`)
in this chapter, and `[integration: <source>]` in chapters 01–16; the full list is
`_process/integration-report.md`.

**00.1.7 Out-of-fiction layer.** `[N]` Numbers, odds, offers and the codex are shown out of fiction,
like a character sheet; they are never voiced by any in-world entity. The fiction voices
recognition, danger and consequence in its own terms [BRIEF §4; R6 §A.5 item 1].

### 00.2 Rules style guide

This part adopts R4 §4 (the rule-form reliability guide) and R7 §3.4 (the anchor standard) as the
binding authoring standard for every chapter [BRIEF A1].

**00.2.1 The two governing principles.** `[N]`
- **P-A — Put every judgment in its most reliable form.** For each decision a rule needs, ask in
  order: can the engine compute it (`[D]`)? a yes/no question about established facts (`[J:flag]`)?
  a choice from a closed, defined set (`[J:enum]`)? a rung on a short anchored ladder (`[J:rung]`)?
  Only if none fits is it open judgment (`[J:open]`) [R4 §4.1].
- **P-B — Bound the blast radius.** Every `[J:*]` rule states, in its text, the largest mechanical
  effect a wrong call can produce, and that effect must be one of: (i) one rung, one step, or one
  clock tick; (ii) an *offer* the player can decline instead of a grant; (iii) self-correcting as
  evidence accumulates; (iv) reversible by a named later procedure. A `[J:open]` rule whose error
  could kill a character, permanently grant a capability, or reveal a sealed secret is a defect
  [R4 §4.1].

**00.2.2 Rule-kind taxonomy.** `[N]` Every numbered rule carries exactly one kind per decision it
contains (a rule with two decisions carries two kinds). These replace BRIEF §5's three kinds
[BRIEF A3].

| Kind | Definition | Example | Reliability note | Required in the rule text |
|---|---|---|---|---|
| `[D]` | The engine computes, stores, rolls, or enforces. The AI supplies only typed inputs. | "Check total = attribute + competence + edge + circumstance + status, clamped to −8…+16." | Exact, given correct inputs; auditable without a judge [R1 §00.E]. | Inputs, formula or table, state writes. |
| `[J:flag]` | The AI answers one yes/no question about established facts. | "Is the target aware of the actor? True only when a fact or narration established it notices; false when unestablished (then ask the Oracle)." | Highest AI form, ≈87% exact agreement [R: https://arxiv.org/abs/2603.00077]. | "True only when… / False for…", one example each side, tie-break. |
| `[J:enum]` | The AI classifies into a closed set of ≤ ~8 options (hierarchical sets allowed when classified level by level). | "Which basic verb is this method? (15 options, T-00-11)." | High; single-digit error with good definitions; wrong-choice rate rises with overlap [R4 §3.2 S1]. | Each option with inclusions *and* exclusions; tie-break; default when uncertain. |
| `[J:rung]` | The AI picks a rung on a 3–5-rung ladder with anchors. | "Obstacle tier: Easy / Moderate / Hard / Very hard / Legendary." | Exact 38–58%, within one rung 85–93%: design must tolerate a one-rung error [R4 §3.3 W5]. | An anchor sentence and two examples per rung (one typical, one near a boundary); cost of a one-rung error. |
| `[J:open]` | Free judgment. Use sparingly (constitution III). | "Does this moment count as evidence at all?" [C:P5] | Least reliable; lenient- and positive-biased [R4 §3.3 W2–W3]. | Blast-radius cap (P-B), an offer/abstain shape where possible, and a precedent log entry. |
| `[T]` | A trigger: a condition on tracked state that the engine raises and surfaces to the DM. | "Vitality reaches 0 → Staggered." "Three inconclusive beats in a row → lead injection." | High if engine-raised; low if memory-raised [R4 §4.3]. | The exact state condition; what it loads or forces. |
| `[S]` | Sealed state: exists and is used by the engine, but is withheld from the narrator's context until a gate opens. | An NPC's secret; an adversary's stat block; a tally. | Secrets in narrator context leak (up to 79%); private committed state restores consistency (2–12% → 76–100%) [R4 §5.1]. | The gate that unseals it; what the narrator receives instead (tells, omens, qualitative bands). |
| `[N]` | Narration with no mechanical weight. | "Describe the hall's smell and light." | High for prose; the risk is *implied* mechanics [R4 §4.2]. | What the narration may *not* imply (a closed list of state it must not change). |

*Oversized level-2 sets* `[D]`. The seeded deed tree classifies level by level (03.1.5), and five branches hold
more than eight level-2 children: `deed.martial` 12, `deed.arcane` 11, `deed.craft` 11, `deed.lore` 9,
`deed.influence` 9. They are kept, because a wrong child there costs at most a sibling under the right branch,
shown in the OFFER (03.1.5's worst case), while regrouping them would rename seeded tags (00.5.5 forbids it).
They are an admitted exception to the ≤ ~8 guideline, tested by OEQ-00-1's level-2 stratum; no further
level-2 child is added to them (PR-03-6 step 6) [revision: I-044; DL-00A-32].

**00.2.3 The worst-case-cost requirement.** `[D]` A `[J:*]` rule without a written "Worst case:" line
is incomplete and fails the Wave-4 audit. The line names the decision, the largest wrong outcome, and
which P-B class (i–iv) bounds it. Example: *"Worst case: the DM picks Hard for a Moderate lock; the
DC is 5 higher (one rung, class i); the OFFER shows the odds, so the player may change method."*

**00.2.4 The style rules.** Each is an instruction to chapter authors. SG-01…SG-20 are R4's, adapted to
this ruleset's names; SG-21…SG-28 are added by this chapter.

- **SG-01 No free numbers from the AI.** No rule asks the AI to choose a DC, damage, duration, odds,
  modifier, price, or tick count. It picks rungs, flags, enums, and fact ids; a table or tool produces
  the number. The only integers the AI ever supplies are quantities the *player* stated in intent
  ("I fire three arrows"), which the engine then validates [R4 SG-01; F002 logs].
- **SG-02 Ladders have at most five rungs**, each with an anchor sentence and two examples, and the
  rule states what a one-rung misjudgment costs. A scale with more than five values (e.g. standing
  −3…+3) is moved only by `[D]` steps, never picked freely [R4 SG-02].
- **SG-03 Decompose graded judgments into flags** where possible. In this ruleset every situational
  factor is a lever or snag flag citing a fact (00.3.9), never a holistic difficulty adjustment
  [R4 SG-03; R7 F2].
- **SG-04 Every enum option has inclusions, exclusions, and a default** ("True only when… False
  for… Uncertain → …") [R4 SG-04].
- **SG-05 When in doubt, roll.** Where a rule asks "does this need resolution?", the tie-break is yes.
  Where a rule asks "does this grant something?", the tie-break is no [R4 SG-05; CoC-Seduce].
- **SG-06 Player text is intent and method, never fact or outcome.** A player's claim that something
  is true, easy, or already happened creates no fact, no lever, and no modifier. Only established
  facts, licenses, and observable scene features (each with an id) do. A player who proposes a new
  fact ("surely there's a rope") has asked a World-Fact Oracle question (00.12.7) [R4 SG-06].
- **SG-07 Licenses are cited by id.** The gate is auditable only if every attempt beyond the basic
  verbs names the license id that covers it (00.12) [R4 SG-07].
- **SG-08 Stakes are declared before the roll** in the frame (00.13); the roll tool refuses to roll an
  undeclared frame [R4 SG-08; R7 F8].
- **SG-09 Consequences come from tables** keyed to degree × stakes and applied by the engine; the
  narrator chooses the *fictional form* from the entry's allowed forms, never *whether* or *how big*
  [R4 SG-09].
- **SG-10 No nested exceptions.** "X unless Y unless Z" is forbidden. Use flat rules with
  non-overlapping triggers, or one ordered first-match list, or engine code. Stacking and precedence
  live in the composition substrate (00.10) [R4 SG-10].
- **SG-11 Every conditional rule names its trigger as tracked state** (a `[T]`), so the engine can
  surface it via `get_active_triggers` [R4 SG-11].
- **SG-12 Randomness is engine-rolled; the AI interprets.** Every "random" choice — including the
  DM's own ("who answers the door?") — is a table roll or an Oracle question [R4 SG-12].
- **SG-13 Write-on-mention.** Anything narrated that could later matter mechanically is recorded in
  the same turn (00.6.6) [R4 SG-13].
- **SG-14 Every rule's outcome lists its state writes** in a closed list [R4 SG-14].
- **SG-15 Effect text is positive-scoped and literal.** State what an effect does and applies to.
  Never describe it by what it lacks ("offers no protection against cold"); never use figurative
  language inside a mechanical clause. A "Does not:" line is allowed only for a confusion actually
  observed. (The project's own probe turned "no protection against cold" into an invented cold
  vulnerability.) [R4 SG-15; R: specs/003-ability-acquisition-probe/implementation-results.md]
- **SG-16 Merge or sharply differentiate similar rules.** Two rules for overlapping situations each
  carry a distinguishing test the AI can check [R4 SG-16].
- **SG-17 Worked examples are boundary pairs plus a non-example**, varied in surface content and
  difficulty [R4 SG-17].
- **SG-18 Rules load by situation.** Each rule card declares the `situation.*` tags it loads in
  (00.15) [R4 SG-18].
- **SG-19 Counters, not recollection.** Anything counted across turns is engine state [R4 SG-19].
- **SG-20 Improvised rulings become precedents** in the ruling ledger (00.15.6) [R4 SG-20].
- **SG-21 Canonical names only.** Use the glossary's canonical term (00.18); the banned-words list
  (T-00-22) applies to rules text and data. Narration may use natural language, but never a banned
  mechanical term in fiction.
- **SG-22 Every number cites its scale.** A number in rules text or data is either a value on a scale
  defined in 00.3/`data/scales.yaml`, or a value inside the envelope of such a scale with its owning
  table named. Magic numbers are a defect.
- **SG-23 Integers only; no percentages** in rules or data except d100 odds (00.3.1) and probabilities
  displayed in an OFFER. Fractions arise only from the ×½ multiplier and are rounded down at pass step
  E7 (00.10.5).
- **SG-24 Every clock names its obstacle, not its method, and every hidden clock carries omens**
  (00.8) [R: https://bladesinthedark.com/progress-clocks; BRIEF A2 #11].
- **SG-25 Every data entry has a lifecycle status** (`provisional` by default; 00.16.3) [C:VI].
- **SG-26 Every rule is a self-contained card.** A rule retrieved alone must be correct alone: it
  restates the ids it depends on, and never relies on "as described above" [BRIEF A3; R4 §9 00 #5].
- **SG-27 Negative facts are explicit.** Secrets, unmet NPCs, undiscovered places and unknown
  properties exist in state as sealed facts or as positive assertions of ignorance ("X does not yet
  know Y") [R1 §00.B].
- **SG-28 Name the time.** Any duration, delay, or recurrence is expressed in a unit of the time
  ladder (00.7) or as a named boundary event; "a while", "soon", "later" are not durations.

**00.2.5 The rule template.** `[N]` Every numbered rule in chapters 01–16 that contains a `[J:*]`
decision supplies the template's (J) fields; `[D]`, `[T]`, `[S]` and `[N]`-only rules may omit them. Fields map
one-to-one to the rule-card record (00.15.2). **Two forms comply** [revision: I-001]: the **block** below, used
where a rule is mainly a judgment (several decisions, examples worth a boundary pair); and the **inline form**,
used where one judgment sits inside a `[D]` rule: the decision stated as options or a "true only when" test, its
default when uncertain, and its worst case under the label *Worst case (J):* (a qualifier may follow inside the
parentheses or after them: *Worst case (J, tier):*, *Worst case (J) of a one-rung error:*). Either way the worst
case is never omitted; `validate_ruleset.py` fails a `[J:*]` rule that has neither the block's `Worst case (J):`
field nor an inline *Worst case (J…* label.

```
### CC.S.R  <Rule name>                                    <kinds, e.g. [J:rung] [D]>
Trigger [T]:        <tracked condition or intent class that invokes this rule>
Loads in:           <situation.* tags>
License check:      <license ids that make the attempt legal, or "basic verb: verb.<id>">
Decisions (J):      1. <decision> [J:enum] options: A (true only when… false for…) | B … | default: A
                    2. <decision> [J:flag] "True only when…"   (cites fact ids)
                    3. <decision> [J:rung] rungs with anchors (table ref)
Computation [D]:    <formula / table lookup / tool call>
Stakes:             <declared before the roll: success → …; failure → …; severity / lethal>
State writes:       <closed list, using 00.6 state-family names>
Narration may not imply: <closed list>
Worst case (J):     <largest effect of a wrong judgment; P-B class>
Examples:           inside / outside each boundary; one tempting non-example
Anchor:             <yes/no; if yes: intent verbs, knobs with defaults and allowed deltas (00.2.6)>
Basis:              [C:…] [R…] [DL-…]
```

**00.2.6 The anchor standard.** `[N]` A rule marked `Anchor: yes` is one the DM may reach for when an
action matches no rule ("basically a grapple with a penalty"). It must have all seven properties
[R7 §3.4]:
1. **Named by an intent-shaped verb** ("Grapple: seize and hold"), so a new action's intent retrieves it.
2. **Explicit knobs with defaults** — the parameters an adaptation may change, from the closed knob
   list T-00-20 (DC source/tier, attribute, action cost, reach unit, stakes rung, duration and growth, condition
   inflicted, harm severity, target set, time cost).
3. **A complete degree table** (critical success, success, near miss, failure, critical failure).
4. **A declared scope and exclusions** ("Covers: … Does not cover: …").
5. **Tags and traits** that pull in general rules automatically (`trait.action.attack`,
   `trait.sense.loud`, …; T-00-7).
6. **Stable numbers** — the DC belongs to the obstacle and persists once set (00.3.8).
7. **Composable** — usable as a beat in a linked sequence and as a tick source for a clock.

**00.2.7 The two-change limit.** `[D]` An improvised ruling may move **at most two knobs** away from
its anchor. If a third change is needed, the anchor is wrong (re-anchor to a closer rule) or the
action is compound (split it into beats). The ruling is logged with its signature (anchor id + the
deltas) [R7 §3.4].

**00.2.8 Separability.** `[N]` Binding rules (numbered rules, tables, data) are kept strictly separate
from craft commentary (Design intent, sidebars), so a runtime can inject only the binding text for
the current situation [R1 §00.A; R1 #15].

### 00.3 Numeric conventions and scales

All values below are mirrored in `data/scales.yaml`, which is canonical for ids and numbers. Where a
later chapter owns the final number, this part fixes the **envelope** the number must sit inside and,
where the math matters, the **calibration targets** the number must satisfy.

**00.3.1 Dice.** `[D]` Three dice families exist, and each has one job:
- **d20**: every check (an actor attempting something whose outcome is uncertain), via
  `roll_check` (00.14). No other die resolves an attempt.
- **d100**: the World-Fact Oracle (00.12.7) and percentile tables. World questions never use the
  d20; actions never use the d100, so the two can never be confused [R5 §5.2 #2].
- **d4, d6, d8, d10, d12**: only *inside* data tables rolled by `roll_table` (e.g. a d6 rumor table).
  No rule text ever says "roll 2d6 damage": harm is a fixed magnitude (00.3.11).

**00.3.2 The engine rolls everything.** `[D]` Every die (the player's checks, adversaries' attacks,
Oracle questions, table rolls, generator draws, birth variance, and every "random" choice the DM
would otherwise make) is rolled by a tool with a seeded, logged generator. The DM never generates,
imagines, or "picks at random" a result [BRIEF A2 #10; R4 SG-12; R: https://arxiv.org/abs/2601.05414].

**00.3.3 Who rolls: the active side.** `[D]` + `[J:flag]` Each attempt is **one d20 roll** by the side
that is acting; the other side contributes a static number.
- **Aimed actions** (the source must get past the target: a Strike, a Grapple, a Talk to persuade, a
  Sneak past a watcher) → the actor rolls against the target's **defense** (00.3.8).
- **Resisted effects** (the effect lands unless the target withstands it: poison, fear, a hazard, a
  spell that allows resistance) → the target rolls **Endure** or **Evade** against the **effect DC**
  (00.3.8).
- The test between the two is `[J:flag]` *"Does the effect need the source to get past the target?"*
  True only when the source's skill or aim decides whether it lands; false when it lands by default
  and the target's body or will decides whether it takes hold. Uncertain → aimed (the acting side
  rolls). *Worst case (J):* the wrong side rolls; odds shift by at most the difference between the two
  sides' modifiers, and the OFFER shows them (class i). Chapter 06 applies this to conflict, 07 to
  afflictions, 10 to hazards, 05 to abilities.
- Adversaries' attacks are therefore rolled by the engine for the adversary against the PC's defense.
  "The player rolls" is never a rule: the player *decides*; the engine rolls [resolves R3 §4 T-16].

**00.3.4 Integers and rounding.** `[D]` All stored values are integers. The only fractional operation
is the ×½ multiplier (00.10.4), rounded **down** at pass step E7. Clamps are applied at every write:
a value never leaves its declared min/max. No percentage modifiers exist (SG-23).

**00.3.5 Check modifier composition.** `[D]` A check's total modifier is the sum of five families, each
with its own stacking rule and cap (T-00-4):

`total = attribute + competence + edge + circumstance + status`, then clamped to **−8…+16**.

| Family | Source | Range per roll | Stacking |
|---|---|---|---|
| **attribute** | the one governing attribute (00.4) | PC −2…+4; others −5…+10 | single value |
| **competence** | the highest competence entry on the beat's primary deed tag or any ancestor (00.5.6) | 0…+6 | highest only |
| **edge** | flat bonuses from items and abilities | 0…+2 | sum, capped at +2 |
| **circumstance** | levers and snags (00.3.9) | −4…+4 | sum, capped at ±4 |
| **status** | conditions (00.9) | −4…+2 | worst single penalty + best single bonus |

The **base modifier** (attribute + competence + edge) of a PC never exceeds **+12**; of any other
entity, **+14** (only at threat band T5). There is no default modifier: every modifier is read from
state. The old "+2 default" and the free-integer `modifier` argument are retired [R4 R-02; R4 §3.4].

**00.3.6 Competence.** `[D]` Competence is this ruleset's "trained bonus", and it lives on tags: an
entity holds a *competence map* of `{deed tag → value}`. For a beat, the engine looks up the beat's
primary deed tag (00.5.6) and takes the highest value among that tag and all its ancestors. Values:
**0** untrained; **+1** the PC floor, held by every PC at the root tag `deed` (constitution P2's
baseline floor, so it applies to everything a PC does); **+2…+6** from origins (02), licenses that
carry training (05), and calling tiers (04). Items never grant competence. The floor is +1 by
default; 02 may set it in 0…+2 with a DL entry, and it must remain a single entry at `deed`
[C:P2; DL-00A-06].

**00.3.7 The bounded-accuracy envelope and power bands.** `[D]` Because there are no character levels
[C:P2], power is described by **bands** read from state. The same five rungs describe a PC's power
(04 computes `power_band`) and an adversary's threat (09 assigns `threat_band`), so they compare
directly.

| Band | PC power band (04) | Adversary threat band (09) | PC best-domain base modifier | Adversary typical attack/defense modifier | Vitality envelope |
|---|---|---|---|---|---|
| 1 | P1 **novice** (unrecognized or tier 1) | T1 **rabble** (untrained folk, vermin) | +4…+6 | +0…+2 | PC 10–16 at creation / T1 2–5 |
| 2 | P2 **seasoned** | T2 **trained** (soldiers, wolves) | +6…+8 | +3…+5 | T2 6–12 |
| 3 | P3 **elite** | T3 **elite** (knights, ogres) | +8…+10 | +6…+8 | T3 12–20 |
| 4 | P4 **champion** | T4 **champion** (heroes, trolls, young dragons) | +9…+11 | +9…+11 | T4 20–32 |
| 5 | P5 **legend** | T5 **legend** (ancient dragons, demon lords) | +10…+12 | +12…+14 | PC cap 24 / T5 32–60 |

**The PC column** `[revision: I-063]` is the range a band's specialists actually hold (04.5.1: competence +5 / +6
at tiers 4 / 5, the best attribute +4 after the tier-4 increase, edge 0–2); the lower ends of P4 and P5 were +10
and +12 until revision C, which only a specialist with edge +1 or +2 reached. The **reference PC** of each band
(T-06-12's lines; 09.4.4's audits) sits at the top of the range (+11 at P4, +12 at P5): the envelope's adversary
numbers are tuned against it, and PR-09-4 rates every real encounter from the PC's own line, so a specialist
with edge 0 sees a fight rated for the modifier it has.

**Envelope scope.** The adversary Vitality column binds the `standard` line of each band and, from
below, `minion`s; `elite`, `solo` and mob pools are multiplied past it by ch.09's variants (×2 / ×1.25
elite; ×4 / ×3 / ×3 / ×1.75 / ×1.5 solo; mobs 06.10.2), so a T1 elite can exist. The reference standard
line is T-09-3: Vitality **5 / 12 / 18 / 24 / 36** for T1–T5 (T4 and T5 lowered from 06's 26 / 40 once
adversary Fend was modelled) [amended: IR ch.09; DL-09-04]. A PC's maximum Vitality grows with power
band: creation value + 2 × (power_band − 1), cap 24 (00.3.12) [amended: DL-00-04].

**Coherence: retired.** The single-attack coherence check first printed here and
`scales.yaml#bands.advisory_by_difference` are **retired** (kept in the file as `lifecycle: retired`):
with ch.06's action economy (3 PC actions + a reaction against 2) and adversary Fend from T3, they misstate
every pairing (a P1 PC beats one T2 98.7% of the time, not "even but favorable"). The contract for
`threat_advisory` is ch.09's extended advisory matrix **T-09-9** and its estimator **PR-09-4**, which
count the foes and read the PC's actual numbers; ch.06's T-06-13 is the earlier form of the same matrix,
and ch.16 (16.7.11) adds the ally adjustment. Encounter budgets are T-09-10 [amended: IR ch.06 #7, IR
ch.09 #3; DL-09-09].

**00.3.8 Difficulty: DCs, defenses, and effect DCs.** `[D]` + `[J:rung]`
- **The DC follows the obstacle** [R7 F2]. A DC comes from exactly one of three sources, in this
  first-match order: (1) the obstacle's **stored DC** (a fact written the first time it was framed,
  keyed by obstacle id + anchor signature so the same wall climbed and the same wall broken keep
  separate DCs, DL-01-21; numbers are stable, anchor property 6); (2) an **opposed defense**: `10 + the defender's attribute +
  competence + edge + status` for the attribute and tag the method works against; (3) the **obstacle
  tier** `[J:rung]` (T-00-5), whose numbers ch.01 owns. The first time (3) is used, the DC is written
  to the obstacle as a stored DC. *Worst case (J, tier):* one rung = one DC step, shown in the OFFER.
- An **effect DC** (for resisted effects) uses the same formula as a defense, from the source's side:
  `10 + source attribute + competence + edge`. A hazard's effect DC is the tier matching its severity
  (S1 → Easy … S5 → Legendary) unless ch.10 lists a specific DC.
- Situational factors never change a DC. They are levers and snags on the acting side's roll
  (00.3.9). Cover, darkness, a slippery floor, a distracted guard: each is a snag or lever citing a
  fact id. This merges R4's "circumstance flags on the DC" into R7's levers so nothing is counted twice
  [DL-00A-10].
- A **social** opposed defense (an NPC resisting persuasion, deception or a request) adds two
  state-derived terms to the defense above: the defender's **standing term** (+5 Hostile … −5 Devoted)
  and the **request-size term** (R1 +0 … R5 +10), composed by ch.15 (15.3.3). They are read from state,
  never chosen, so they are not situational factors. Standing does not enter intimidation or provocation
  (DL-15-14) [amended: DL-15-10].

**00.3.9 Levers and snags.** `[J:flag]` + `[J:enum]` + `[D]` The single creativity-and-circumstance
currency [BRIEF A2 #12; R7 §4.2].

| Type | A fact is this type when it… | Lever effect | Mirror snag |
|---|---|---|---|
| **Precision** | lets the method be done *better* (a tool, a blind or distracted target, a running start, help, a Setup) | +2 to the roll | −2 to the roll |
| **Protective** | makes failure *less bad* (cover, a tied-off rope, a clear retreat) | stakes −1 rung | stakes +1 rung |
| **Amplifying** | makes success *go further* (a weak spot, numbers, a resonance, a crowd on your side) | reach +1 rung | reach −1 rung |

Rules: (a) each lever or snag **cites a fact id** that was established in state (or created by an
earlier beat, such as a Setup) *before* the declaration; "cool" is not a fact; a fact a player's own
Oracle question established (a free fact) is further capped by 01.15.8 [revision: I-038]; (b) **at most two
levers and two snags** per roll; (c) the net roll modifier from levers and snags is capped at ±4, and
the resulting stakes and reach are clamped to their ladders; (d) one fact yields at most one lever;
(e) the type follows from what the fact does, and if a fact honestly fits two types the player picks;
(f) an effect that "grants a lever" (00.10.3 op `lever`) creates a citable fact and still counts
toward the two-lever limit; (g) snags the *engine* applies by rule (the repetition snags of ch.01,
DL-01-08) do not count toward the two-snag limit but do count toward the ±4 cap. *Worst case (J):* one wrongly allowed lever = +2, one stakes rung, or one reach
rung (class i), and the cited fact id makes it auditable.

**00.3.10 Degrees of success.** `[D]` Every roll produces exactly one of four degrees,
`critical_success`, `success`, `failure`, `critical_failure`, plus a boolean `near_miss` on failures.
The degree is computed from the margin with critical bands at ±10; a natural 20 shifts the degree one
step up and a natural 1 one step down (the converged default, which ch.01 confirms or replaces with a
DL entry); `near_miss` is true when the final degree is `failure` and the margin is ≥ −3, which
includes a roll that met the DC but was stepped down by a natural 1 [BRIEF A2 #15; R7 §4.0 steps 7–8;
C:P8; amended per DL-01-03]. The four degree ids are fixed by this chapter; everything that reads a degree
(clocks, generators, costs, delivery) reads these ids.

**00.3.11 The severity scale (S1–S5).** `[D]` + `[J:rung]` One five-rung scale measures every magnitude
of *badness* in the game: harm, costs, stakes consequences, hazards, conditions, wounds, damage to
factions. Its values are fixed here (T-00-3):

| Rung | Name | Anchor (who is affected, how long) | Harm (Vitality) | Unit magnitude U | Hazard effect DC |
|---|---|---|---|---|---|
| S1 | **Light** | a nuisance; recovers within the scene | 1 | 1 | Easy |
| S2 | **Moderate** | a real setback; lasts the scene or needs a rest | 3 | 1 | Moderate |
| S3 | **Heavy** | a serious blow; lasts until a long rest or treatment | 5 | 2 | Hard |
| S4 | **Grievous** | could end a fight or a life; lasts days or leaves a mark | 8 | 3 | Very hard |
| S5 | **Catastrophic** | lethal to most; lasting or permanent | 12 | 4 | Legendary |

*Harm* is the Vitality loss before mitigation. *Unit magnitude U* is how many units a cost of that
severity removes from anything counted in units: clock ticks, Focus, supply, standing steps, uses.
R7's "standard cost" is S2 and its "severe cost" is S3. The words *minor, major, severe* are not rung
names (T-00-22). *Worst case (J) of a one-rung error* when a rule asks the DM to classify severity: harm
differs by 2–4 Vitality or one unit (class i).

**00.3.12 Vitality.** `[D]` Vitality is the primary harm resource: wind, luck, and the ability to
avoid a telling blow. Envelope: a PC's maximum Vitality is **10–16 at creation (reference 12)** and
never exceeds **24**; adversaries per band (00.3.7). It grows with recognized standing, not with a
counter: **maximum = creation value + 2 × (power_band − 1)**, cap 24 (12 / 14 / 16 / 18 / 20 at the
reference base); ch.07 owns the rule text (07.1.2) and the recompute handler `h.07.vitality_max`, and
current Vitality rises by the same amount when the band rises [amended: DL-00-04]. At Vitality 0 an entity is **Staggered**; further
harm becomes wounds and moves it toward **Dying**; death follows the Two-Key rule. Chapter 07 owns the
semantics and the numbers inside this envelope; 02 owns the creation formula, which may use Endurance
(00.4.4; 02 sets it at 12 + Endurance, DL-02-16) [R6 §C.3 C-R1–C-R2].

**00.3.13 Focus.** `[D]` Focus is the one shared pool for every active ability across every calling
[C:P9]. Envelope: **3–5 at creation (reference 4)**, hard cap **12**; an activation costs **0–4**
before modifiers and **never more than 6** after them. Focus is **not** derived from any attribute (so
no attribute becomes a caster's god-stat) [DL-00A-09]. Chapter 05 owns pool growth, costs and every
recovery channel (contract 05↔07, 00.17).

**00.3.14 Stakes.** `[J:rung]` + `[J:flag]` Stakes answer "how bad can failure be?" and are declared in
the frame before the roll [BRIEF A2 #2].

| Rung | Anchor | Cost on failure | Examples (typical / boundary) |
|---|---|---|---|
| **Safe** | Failure only means it doesn't happen; you can walk away and try another way. | none (an S1 cost if the player takes success-at-cost) | reading an old map at leisure / picking a lock with no one near while the night is young |
| **Risky** | Failure costs something real. | one **S2** cost from the menu | sneaking past a sleepy guard / climbing a wet wall above a 10-ft drop |
| **Dire** | Failure costs something heavy, and may be lethal. | one **S3** cost from the menu | leaping a chasm / fighting a troll in its lair |

- A critical failure raises the cost severity one rung (default; ch.01 owns the READ table).
- *Worst case (J) of a one-rung framing error:* one severity rung of cost (class i), visible in the OFFER.
- **`lethal`** is a separate `[J:flag]` on the frame, legal only when stakes are Dire **and** the scene
  or threat carries `lethal_context: true` recorded *before* the declaration (the lethal warning,
  ch.07). *True only when* failure could move the PC to Dying or beyond; the OFFER must then say so in
  plain words. **No roll whose frame is not lethal can cause death** (invariant INV-6). *Worst case (J):*
  lethal wrongly false → the PC cannot die from that roll (errs safe, class iv); wrongly true → legal
  only if the warning was already on record, and the player saw it before committing.

**00.3.15 Reach.** `[J:rung]` Reach answers "how much can success achieve?" [R7 §4.2; Blades effect,
R: https://bladesinthedark.com/effect]. Framed rungs: **Limited (1)**, **Standard (2)**, **Great (3)**.
Computed rungs: **Zero (0)**, where the method cannot reach the intent (the beat is gated G4, 00.12.3);
**Exceptional (4)**, reachable only by a critical success stepping up from Great. *Delivered reach* is
a number 0–4, and everything that consumes success reads that number: progress-clock ticks = delivered
reach; a harm-dealing anchor's severity shifts by `(delivered reach − 2)` steps; information units per
ch.01's delivery table; NPC movement per ch.15. *Worst case (J) of a one-rung framing error:* one tick,
one severity step, or one information unit (class i).

**00.3.16 Other shared scales.** `[D]` (numbers and names in T-00-3 and `data/scales.yaml`)
- **Obstacle tiers** (DC rungs): Trivial (no roll) · Easy · Moderate · Hard · Very hard · Legendary ·
  Beyond (impossible, gate G4). Five rollable rungs; numbers owned by ch.01 within 00.3.17.
- **Standing** (NPC disposition, faction status, any signed relationship): −3 Hostile, −2 Unfriendly,
  −1 Wary, 0 Neutral, +1 Warm, +2 Friendly, +3 Devoted. Moved only in `[D]` steps; a newly generated
  NPC's starting standing is rolled (ch.12), never chosen [R6 §B.3 B-R2].
- **Clock sizes**: 4 (a scene's worth), 6 (complicated), 8 (daunting), 12 (a long project).
- **Oracle odds rungs**: Certain (no roll) · Likely · Even · Unlikely · Remote · Impossible (no roll).
  Thresholds are ch.01's (reference: yes on 26+ / 51+ / 76+ / 91+ on d100; doubles = extreme answer or
  twist) [R7 §4.7; R: https://ironsworn-rpg.fandom.com/wiki/Ask_the_Oracle].
- **Meta-currency `fate`**: 0–3 points; the only player-spendable luck currency in the ruleset
  (contract 01↔07, 00.17).

**00.3.17 DC ladder envelope and calibration targets.** `[D]` Chapter 01 owns the final DC numbers. The
reference ladder that already satisfies every target below is **Easy 10, Moderate 15, Hard 20, Very
hard 25, Legendary 30**. Chapter 01 may move any rung by up to ±2 (with a DL entry and a recomputed
table) provided every target holds (success-or-better, step rule, exhaustive d20 enumeration):

| Target | Requirement | Reference ladder |
|---|---|---|
| CT-1 Easy | a PC at +2 (average attribute + floor) succeeds ≥ 60% | 65% |
| CT-2 Moderate | a P1 specialist at +5 succeeds 50–65%; an untrained PC at +1 succeeds 30–40% | 55% / 35% |
| CT-3 Hard | P1 specialist at +5: 25–35%; P3 at +9: 45–55% | 30% / 50% |
| CT-4 Very hard | P1 specialist: ≤ 10%; P5 at +12: 35–45% | 5% / 40% |
| CT-5 Legendary | P5 with one Precision lever (+14): 20–30%; anything ≤ +9 needs a natural 20 | 25% / 5% |
| CT-6 Crit-fail sanity | at any rung where a character succeeds ≥ 50%, critical failure ≤ 10% | holds (≤ 5%) |

The full distribution is T-00-6. The research's alarm about the old ladder (40% critical failure at +2
vs DC 20) came from *missing competence*, not from the ladder: with the floor and specialties the same
numbers are honest, and the critical-failure rate is high only on long shots the OFFER shows in advance
[R4 §3.4; DL-00A-05].

### 00.4 Attributes

**00.4.1 The seven attributes.** `[D]` Attributes answer "how good is this character at broad
categories of action" [C: Sync Impact Report, ability scores]. There are seven. Each is stored only as
a modifier (no separate "score"). The attribute follows the **method**, never the intent [R7 F2].

| Id | Name | Governs (use when the method is…) | Distinguishing test vs nearest neighbor |
|---|---|---|---|
| `might` | **Might** | applying bodily force: lifting, breaking, shoving, heavy blows, grappling, climbing by strength | vs Agility: *does success come from how much force, or from how exact and fast the motion is?* Force → Might. |
| `agility` | **Agility** | moving body and hands quickly and exactly: dodging, balance, quiet movement, fine manipulation, aimed and thrown attacks, finesse blows | vs Wits: *is it the body executing, or the mind noticing?* Executing → Agility. |
| `endurance` | **Endurance** | withstanding bodily strain: poison, disease, cold, exhaustion, holding breath, running or swimming far | vs Might: *acting on the world in a burst, or holding out against it?* Holding out → Endurance. vs Resolve: *is the body or the mind under strain?* Body → Endurance. |
| `wits` | **Wits** | noticing and reacting in the moment: perception, awareness, reading a situation or a person, quick practical improvisation | vs Intellect: *is the answer in front of you now (perceive, react), or in your head (know, reason, plan)?* In front → Wits. |
| `intellect` | **Intellect** | knowing and reasoning: recall, deduction, study, analysis, planning, reasoned argument, knowledge-driven work | vs Wits (above). |
| `presence` | **Presence** | moving other minds: persuading, deceiving, commanding, performing, intimidating by force of personality, handling animals by manner | vs Wits: *changing someone's mind, or reading it?* Changing → Presence. vs Resolve: *will pushed outward, or held inward?* Outward → Presence. |
| `resolve` | **Resolve** | withstanding mental and spiritual strain: fear, pain, temptation, domination, despair; keeping concentration | vs Endurance and Presence (above). |

**00.4.2 Why seven.** `[N]` The count is set by the texture the AI DM needs to adjudicate novel actions,
not by minimizing numbers [C: Sync Impact Report]. Six would merge Wits and Intellect, and the merged
stat would own perception, knowledge and most magic theory: the most-rolled stat in the game plus the
scholar's identity. That is the overload failure seen in Underworld's Wisdom and the reason D&D splits
Intelligence from Wisdom [R2 §00 attribute table]. Eight or more would create overlapping lanes
(Dexterity vs Agility; Perception vs Wits) whose wrong-choice rate rises with every confusable option
[R4 §3.2 S1]. Seven gives each of three domains (body, mind, will) an attribute for acting and one for
withstanding (Might and Agility vs Endurance; Wits and Intellect; Presence vs Resolve), each separated
by a one-question test. The finer texture the AI needs (lockpicking vs smithing vs courtly etiquette)
comes from **tags and competence** (00.5, 00.3.6), not from more attributes [R4 §9 02 #1; DL-00A-08].

**00.4.3 Ranges and change.** `[D]` PC attribute modifiers are **−1…+3 at creation**, and the seven sum
to **+5…+7** (ch.02 designs the method and P4's quantity-vs-freedom trade-off inside that band;
reference array +3, +2, +1, +1, 0, 0, −1 = +6). After creation an attribute changes only by: (a) the P1
deferred birth reroll, **the Bent** (02.6.5–02.6.7); (b) at most **one +1 in a lifetime**, granted by a
calling tier (04) and applied when that calling's **tier 4 is confirmed** [amended: IR ch.04 #8], never
above +4; (c) a permanent mark or maim (07; an aging mark, 11.10, is one), at most −1 per attribute, never
below −2. A PC's attribute sum after creation is therefore at most +8 (Typical rule + the Bent), or +9
with the tier-4 increase [amended: IR ch.02]. **Items,
conditions and abilities never change attributes**; they act through edge, status, or other effects.
This keeps P4's "mostly fixed at creation" and closes attribute arbitrage [C:P4; R1 §00.C; R2 §00].
Non-PC entities range −5…+10.

**00.4.4 Derived values (closed list).** `[D]` Each attribute feeds its own defense (00.3.8) and at
most the one derived value below. No other derivation from attributes is permitted.

| Attribute | The one derived value it may feed | Owner |
|---|---|---|
| Might | carrying capacity | 08 |
| Agility | (none beyond its defense, which is the usual defense against aimed physical attacks) | 06 |
| Endurance | maximum Vitality | 02 / 07 |
| Wits | tempo / initiative | 06 |
| Intellect | number of languages or lore specialties at creation | 02 |
| Presence | maximum retinue (companions and followers) | 16 |
| Resolve | mental-strain threshold | 07 |

**00.4.5 Basic verb → attribute map.** `[J:enum]` The attribute for a beat is chosen from the verb's
allowed list by the *method as described* (T-00-11). When the method fits two allowed attributes
equally, the frame uses the **lower**, and the OFFER names the alternative method that would use the
higher ("if instead you [method], use Agility"); the player may re-declare at no cost. *Worst case (J):*
the lower of two attributes is used (at most 5 points), shown before commitment (class ii).
[R4 §4.6 step 1; R7 §4.1]

### 00.5 The tag vocabulary: top levels

**00.5.1 One vocabulary, ten facets.** `[D]` All tags in the game live in one hierarchy in
`data/tags.yaml`, so the same vocabulary answers "what did the character do" (evidence, competence,
callings), "what is this thing" (adversary nature, loot pools, materials), "what does this effect do"
(harm types, traits), and "which rules apply here" (situations) [R3 §00.4; R1 §00.D]. The root level
is ten **facets**; below each facet sit its **branches** (level 1) and their **first children**
(level 2). Tag ids are dot paths beginning with the facet: `deed.martial.archery`.

| Facet | What it describes | Attaches to (domain) | Branches (level 1) | Content steward |
|---|---|---|---|---|
| `deed` | what an actor does; the axes of evidence, competence and callings | beats, evidence, competence, licenses, abilities, callings | martial, guile, wilds, lore, arcane, divine, primal, influence, craft | 03 |
| `conduct` | the values an act expresses; **signed** axes | evidence, callings, oaths, shadows | mercy, honesty, courage, loyalty, generosity, justice, humility, restraint, piety, protection | 03 |
| `creature` | the nature of a being; adversary archetype families | entities, adversaries, pool gates, absorbable pools | beast, folk, undead, spirit, fiend, construct, elemental, dragon, horror | 09 (via 03) |
| `harm` | the kind of harm or energy | effects, attacks, hazards, resistances, conditions | physical, fire, frost, storm, corrosion, venom, blight, radiance, mind, arcane | 07 (via 03) |
| `material` | what a thing is made of | items, crafting pool gates | metal, wood, stone, hide, fiber, bone, gem, botanical, essence | 08 (via 03) |
| `item` | what kind of object | items, kits, base items | weapon, armor, shield, garment, jewelry, tool, consumable, goods, conveyance | 08 (via 03) |
| `terrain` | the kind of place | places, scenes, hazards, encounter tables, site themes | settlement, road, forest, highland, plains, wetland, arid, frozen, water, underground, ruin | 10 (via 03) |
| `situation` | which rules load | rule cards, scenes | conflict, social, investigation, exploration, travel, downtime, rest | 12 (via 03) |
| `trait` | properties of an action or effect that pull in general rules | beats, abilities, effects, items | action, sense, delivery, nature, duration | 01 (via 03) |
| `org` | the kind of organization | factions, institutions, recognition vehicles | crown, faith, order, guild, company, clan, outlaw, cult | 11 (via 03) |

The level-2 children of every branch (except `conduct`, whose axes are leaves at level 1 and carry
sign instead) are fixed in `data/tags.yaml` and summarized in T-00-7.

**00.5.2 The deed branches are the calling axes.** `[D]` The nine `deed` branches are the
low-cardinality keys for class emergence: specialist callings may key on any `deed` or `conduct` tag
at any depth; **hybrid callings key only on pairs of distinct `deed` branches** (at most C(9,2) = 36
pairs), per constitution P5's curated sparse table [C:P5; R3 §03.6, §6 #5]. Keeping this set in single
digits is what keeps the hybrid table and the Delve-style thresholds tractable.

| Branch | Covers (inclusions) | Distinguish from |
|---|---|---|
| `deed.martial` | fighting with weapons, shields, armor and body; tactics; physical prowess (athletics, feats of strength, acrobatics) | `guile.ambush` (striking from hiding is guile when concealment is the point) |
| `deed.guile` | stealth, thievery, deception, disguise, ambush, poisoncraft, escapes, the underworld | `influence` (guile makes someone believe something false or not notice; influence moves them with truth, emotion or authority) |
| `deed.wilds` | survival, tracking, navigation, animals, foraging, seafaring | `primal` (wilds is mundane skill; primal is nature *magic*) |
| `deed.lore` | knowing and finding out: history, languages, creatures, medicine, engineering, law, arcane theory, religion, investigation | `arcane`/`divine` (lore *knows about* magic; those branches *work* it) |
| `deed.arcane` | learned, formulaic sorcery | `divine` (power by study and formula vs power granted by a power one serves) |
| `deed.divine` | power and rites through gods, oaths, pacts, the sacred | `primal` (a named power or oath vs the living world's spirits) |
| `deed.primal` | nature and spirit magic: growth, beast-kinship, weather, shapeshifting, spirits, hexes | `wilds` (above) |
| `deed.influence` | persuasion, command, performance, intimidation, intrigue, trade, etiquette, insight into people | `guile` (above) |
| `deed.craft` | making and mending: smithing, woodcraft, leathercraft, textiles, alchemy, cookery, building, artifice, jewelcraft, enchanting | `lore.engineering` (craft makes the thing; lore knows how it works) |

**00.5.3 The conduct facet is signed.** `[D]` Each `conduct` axis has a positive and a negative pole
(e.g. `conduct.mercy`: merciful / cruel). A tag_event on a conduct axis carries a sign (+1 or −1)
and never two signs. Tallies on conduct axes are net and may be negative; oath callings, shadows and
the Fraying key on them (04) [R2 #6; R6 §A.6 R-A6]. Poles and distinguishing tests are in
`data/tags.yaml`.

**00.5.4 Cascade and most-specific-wins.** `[D]` (a) **Cascade:** anything tagged X also counts for
every ancestor of X (evidence toward `deed.martial.archery.bow` counts toward `deed.martial.archery`,
`deed.martial` and `deed`) [C:P5]. (b) **Most-specific-wins:** wherever a rule must pick one level
(which weight, which threshold, which pool entry), the deepest matching tag wins; ties at the same
depth go to the tag listed first in the entry [R3 §03.1]. (c) **Match semantics:** a pool entry or rule
gated on tag G matches a source tagged S when G equals S or G is an ancestor of S.

**00.5.5 Rules for adding tags.** `[D]` Changes to facets (level 0) and branches (level 1) require an
amendment to this chapter (DL-00A entry and orchestrator approval). Level-2 children listed in
`data/tags.yaml` are append-only: 03 may add level-2 children with a DL-03 entry, may retire one only by
`lifecycle: retired` plus `superseded_by`, and may never rename one. Level 3 and deeper are added by 03
(and proposed by any chapter via its Interface requests) under these rules: (1) exactly one parent;
(2) snake_case segment, ids never reused; (3) maximum depth five segments including the facet
(`deed.martial.blade.sword.longsword`); (4) a definition written "True only when… False for…" and a
distinguishing test against every sibling with overlapping scope (SG-04, SG-16); (5) positive scope
only (SG-15); (6) domain inherited from the facet unless narrowed; (7) a tag names a *kind*, never an
individual (no `creature.dragon.great.vermithrax`; individuals are entities). A chapter written in
parallel may use a level-3+ tag not yet in the file if it follows these rules and lists it under
Interface requests; 03 reconciles.

**00.5.6 Tags on a beat.** `[J:enum]` + `[D]` Every beat carries exactly one **primary deed tag**, the
most specific `deed` tag that describes the *method* (the DM classifies level by level: branch, then
child, then deeper only if the data has it; uncertain → stop at the last level you are sure of).
Competence (00.3.6) reads only the primary deed tag. A beat may also carry up to two secondary deed
tags and any number of `trait` tags (T-00-7). A secondary deed tag earns evidence only when it is
**grounded** — the frame cites a state element of one of the ground kinds `ability`, `license`, `item`,
`setup_beat`, `companion`, `mount`, `position` (03.1.6) — and then at half value; competence still reads
only the primary tag [amended: DL-03-14]. *Worst
case (J):* the primary tag is one level too shallow (competence from an ancestor applies, which is the
same or lower, class i) or on the wrong sibling (the floor applies instead of a specialty; shown in the
OFFER breakdown, class ii).

### 00.6 The state model

**00.6.1 The state types.** `[D]` All game state is an instance of one of these types, held in an
external, update-on-write store; nothing mechanical lives only in narration or in the model's context
[C:P13; R1 #1; R1 §00.A–00.B]. Every write is a typed tool call with a reason and a timestamp; every
value has a defined initial value and update rule [R2 §00].

| Type | What it is | Examples | Write tools |
|---|---|---|---|
| **entity** | anything with identity: id, kind, name, tags, existence status, `introduced_at` | PC, NPC, adversary, companion, item, place, faction, thread, rumor, clue node | `create_entity` |
| **quantity** | a revisable integer with min/max, changed by deltas with reasons | Vitality, Focus, coin, supply, ammunition, fate | `update_quantity` |
| **flag** | a boolean or enum property of an entity | `door_archive.locked = true`; `guard_07.alertness = drowsy` | `set_fact` |
| **fact** | an atomic declarative proposition with source, certainty and visibility | "The Salt Guild owns the north warehouse"; "Guard Tam has no sister" [integration: I-024] | `set_fact` |
| **relationship** | a typed edge between two entities, usually on the standing scale | NPC→PC standing; faction→PC status; membership; ownership; bond | `set_relationship` |
| **position** | where an entity is: (a) location in the place graph; (b) in a conflict, the range band to each other participant plus positional flags | Wren at `loc.grey_keep.archive`; Wren–captain `close`, flag `flanked` | `set_position` |
| **knowledge** | who knows which fact, since when, and how | PC learned the watch changes at midnight; the captain knows Wren's face | `record_knowledge` |
| **clock** | the segmented counter of 00.8 | Alarm in Grey Keep 3/6 | `create_clock`, `tick_clock` |
| **condition** | an instance of a condition on an entity (00.9) | captain: `cond.exposed` (S1, until end of scene) | `apply_condition`, `remove_condition` |
| **license** | a license held by an entity, with grade, source and lifecycle (00.12) | Wren: `lic.lang.common` (native) | `grant`, `revoke` |
| **effect_instance** | an active effect with source, target, remaining duration | Rime Oil on Wren's spear (3 strikes) | `apply_effect` |
| **tally** | sealed evidence totals per tag (03) | `deed.martial.archery`: weighted 7 | `record_evidence` (engine-maintained) |
| **ledger** | an append-only log | write log, evidence ledger, ruling ledger, chronicle, oracle log, offer log | the tool that writes each |
| **commitment** | a typed promise the world or the narration must keep (invariant / ordering / achievement), including oaths, vows, debts | "Wren swore to return the crown"; "the keep's archive is always locked at night" | `set_fact` (kind commitment) |
| **offer** | a standing offer awaiting accept / decline / defer | the Caravaners' outrider contract, expires on leaving the region | `offer_create`, `offer_resolve` |
| **time** | the game clock and every timestamp and duration | Spring, week 4, day 1, afternoon watch | `advance_time`, `mark_boundary` |
| **frame** | the transient resolution record of one beat (00.13), logged after use | frame #412 | `frame_check`, `roll_check` |
| **meta** | engine and session state that is not in the fiction | tension, intensity, inconclusive streak, table recency, player preferences | owning chapter's tools |

**Sealing** is not a separate type: any instance or field of any type may be sealed (00.6.5).

**00.6.2 Canonical object shapes.** `[D]` The shapes below are the minimum fields every implementation
and chapter uses; owning chapters add fields (never rename or remove these). Types: `id` strings are
prefixed per 00.16.2; `tag[]` are `data/tags.yaml` ids; `time` is a timestamp (00.7.1).

```yaml
Entity:            # base of every entity
  id: str            # e.g. "npc.tam_harlan", "pc.wren", "item.i0042"
  kind: enum         # pc | npc | adversary | companion | item | place | faction | thread | rumor | clue | object
                     # companion: every ally kind, told apart by Ally.ally_kind (16.1.2) [amended: IR ch.16]
                     # object: named objects (obj.*, a region's: the world seed 12.16, or a pre-made setting such as 13) and the subtypes situation, legacy (11) [amended: IR ch.11, IR ch.13; revision: I-028]
  name: str
  tags: [tag]
  exists: enum       # exists | destroyed | dead | departed | unknown
  introduced_at: time
  visibility: enum   # shown | available | background | sealed   (00.6.4)
  sealed_fields: [str]

Character (PC; extends Entity):
  attributes: {might: int, agility: int, endurance: int, wits: int, intellect: int, presence: int, resolve: int}
  competence: [{tag: tag, value: int, source: str}]      # 00.3.6; floor = {tag: deed, value: 1}
  vitality: {current: int, max: int}                      # 07
  harm_state: enum   # active | staggered | dying | dead   (07 owns ladder; dying carries step)
  dying_step: int
  wounds: [ref]      # 07
  focus: {current: int, max: int}                         # 05
  fate: {current: int, max: 3}                            # 01
  conditions: [ConditionInstance]
  licenses: [LicenseInstance]
  slots: {calling: [ref], acquired: [ref], equipped: [ref]}   # 05 partitions, 00.17
  callings: [{calling_id: str, tier: int, lifecycle: enum}]  # 04
  possessions: [item_id]
  location: place_id
  relationships: [ref]
  commitments: [ref]
  marks: [ref]                                            # 07
  aspirations: [str]                                      # 02 ({text, tags}, at most 3; 02.9.3)
  reputation: [ref]                                       # 11
  # --- owner extensions [amended: IR ch.04 #7, ch.05 #4, ch.07 #2] ---
  # callings[] entries (04.1.2): {calling_id, tier, lifecycle, granted_at {time, scene, evidence_scene_index},
  #   crystallized_by, vehicle, roads {branch: tag}, seat (deed|oath), fraying_stage 0..3, suspended,
  #   legacy_picks, specialties [{tag, value}], inherited_band, declined_until}
  # focus (05.1.2): + {reserve {banked, capacity, charging, vessel}, state (steady|spent),
  #   generated_this_scene, restored_by_consumables_since_long_rest, breathers_since_short_rest,
  #   short_rests_today, overdraws_since_long_rest}
  # slots.* hold HeldAbility (05.1.2): {ability_id, partition, source {kind, ref}, rank 1..3, uses,
  #   sustained, bound, lifecycle, acquired_at}
  shelf: [ability_id]                                     # 05.2.6
  witnessed: [ability_id]                                 # 05.8
  healings_since_long_rest: int                           # 05.7.8 (per-being healing cap)
  wound_load: int                                         # 07.2.6
  down: bool                                              # 07.2.9
  defeated: {manner: str}|null                            # 07.1.3, 07.6
  dread: {current: int, threshold: int}                   # 07.11
  afflictions: [ref]                                      # 07.9
  reprieves_taken: int                                    # 07.5.8
  watches_awake: int                                      # 07.8.10
  # marks[] entries carry kind (scar | brink_mark | maim | haunt | aging) (07.7)

NPC (extends Entity):
  role_tags: [tag]            # deed/org tags describing what they do
  attributes: {...}           # as Character; only those ever needed, rest rolled on first need
  standing_to_pc: int         # −3..+3 (15)
  wants: [str]                # sealed until learned (15); structured per 15.2.1
  refusals: [str]             # pre-committed "No" conditions (15); structured per 15.2.1
  knowledge: [fact_id]        # sealed unless shared
  secrets: [fact_id]          # sealed
  depth: enum                 # walk-on | recurring | principal (12.11.1)
  band: int                   # 1..5, own band for a contest (03.4.3); written by 12.11.1 [revision: I-089]
  home: place_id              # 11.1.2; 03.10 scope
  member_of: [faction_id]     # 11.1.2; 11.3.17
  # social fields (15.2.1) [amended: IR ch.15 #2]: faction_offset, fears, patience {max, left},
  #   alertness [{toward, value: unaware|suspicious|alert|alarmed, since}], beliefs [lie_id],
  #   lifestyle, mind (mindless|animal|cunning|sapient|alien), speaks [lic.lang.*]

Ally (extends NPC; kind companion; 16.1.2) [amended: IR ch.16]:
  ally_kind: enum             # hireling | companion | follower | beast | bound | cohort | scene_ally
  # + template (cmp.*), own_band, serving_band, line, knacks [kn.*], abilities, members, drives,
  #   temperament, regard/grievance/departure clocks, joining, contract, hears, standing_order,
  #   default_order, orders_allowed, journey_roles, carry, supply_need (full shape 16.1.2)

Adversary (extends Entity; 09):
  archetype: str              # arch.* (manufacturer)
  threat_band: int            # 1..5
  attributes, competence, defenses, vitality, harm, behaviors: ...   # sealed stat block
  tells: [str]                # what the narrator may say instead of numbers
  lethal_context: bool
  defeat_disposition: enum    # kill | capture | rob | ransom | drive_off | drag_to_lair | leave  (07/09)

Item (extends Entity; 08):
  base: str                   # bi.* base item
  quality: enum               # worn | common | fine | masterwork | wondrous | storied (08.1.4)
  signature: [Property]       # identity layer (00.11)
  properties: [Property]      # magnitude layer
  sealed_properties: [Property]
  equipped: bool
  # + 08.1.1 [amended: IR ch.08]: quality_index 1..6, material, worked, flaw, bound_ability {ability_id, rank},
  #   relic, feeds_evidence, cost_immune, slot, attuned, condition (intact|damaged|broken|serviceable_until_rest_long)
Property: {prop_id: str, tier: int, effects: [{effect_id: str, params: map}]}

Place (extends Entity; 10; a region's seed, 12.16) [revision: I-028]:
  parent: place_id
  links: [{to: place_id, route: str, travel_watches: int}]   # + route_kind, terrain, current, known, danger, hazards, vehicle_ok (10.1.3)
  terrain: [tag]
  discovered: bool
  # + 10.1.2 [amended: IR ch.10 #1]: place_kind, band, danger, safe, rest_site, climate, nav_tier,
  #   forage_tier, game_tier, openness, landmarks, water_source, grazing, encounter_table, hazards,
  #   resonance, settlement_scope, known, site, state_log

Fact:
  id: str
  subject: id
  predicate: str
  value: any
  source: enum        # narration | oracle | generation | ruling | data | player_accepted
  certainty: enum     # established | rumored | believed
  truth: enum         # true | partial | false | outdated   (rumors, beliefs; sealed)
  visibility: enum
  established_at: time
  supersedes: fact_id

Clock:           see 00.8.1
ConditionInstance: see 00.9.1
LicenseInstance: {license_id: str, grade: str, source: str, acquired_at: time, lifecycle: enum, expires: duration|null}
EvidenceEvent:   see 00.6.8
RulingRecord:    see 00.15.5
Frame:           see 00.13.1
Offer: {id, kind: enum(recognition|institution|bargain|trade|other), content: ref, vehicle: str,   # recognition content: {calling, tier, alternatives} (04)
        presented_at: time, status: enum(open|accepted|declined|deferred|expired),
        represent_when: [boundary|condition], expires: duration|condition, price: str}
Thread (11): {id, title, kind: enum(vow|quest|situation), progress_clock: clock_id, status, clue_placements: [ref]}
Rumor (11):  {id, text_seed, source, truth: enum, points_to: ref}      # truth sealed
ChronicleEntry (11): {time, text, entities: [id], tags: [tag]}
```

**00.6.3 Ownership of state families.** `[D]` Each state family has exactly one owning chapter, which
defines its semantics and is the only chapter whose rules write it directly; others change it only
through the owner's named interface (00.17) [R1 §00.A]. Visibility class per 00.6.4.

| State family | Owner | Visibility | Notes |
|---|---|---|---|
| Time, calendar position, time mode | 00 (model) / 11 (calendar engine) / 13 (names) | shown | |
| Attributes | 02 (values) / 00 (rules of change) | shown | |
| Competence map | 02, 04, 05 (sources) / 00 (lookup) | available | codex shows each entry and source |
| Vitality, harm state, dying step, wounds, marks | 07 | shown | |
| Focus | 05 | shown | |
| Fate | 01 | shown | |
| Conditions (instances) on the PC | 06 (list) / 07 (afflictions, injuries) | shown | |
| Conditions on others | 06 | shown if `visible: true`, else background | |
| Licenses held, slots, abilities | 05 (abilities, slots) / 02 (origin licenses) / 04 (calling capabilities) / 08 (item licenses) | shown | |
| Callings, tiers, provisional status | 04 | shown once recognized | |
| Tallies (weighted evidence) | 03 | **sealed** | seer readings voice a qualitative band (04 V6) |
| Evidence ledger (deeds recorded) | 03 | available (deed text and tags only) | weights sealed |
| Standing offers | 04 (recognition) / 11 (institutional) | shown | |
| Commitments, oaths, vows | 04 (oaths) / 11 (vows, debts, threads) | shown | |
| Reputation {content, scope, score} | 11 | content and scope available; score background | |
| Possessions, coin, item properties | 08 | shown; unidentified properties sealed | |
| Supply, light | 10 | shown | |
| Location, place graph, discovery | 10 (model) / 13 (content) | shown when discovered; undiscovered sealed | |
| Relationship-state in conflict (bands, flags) | 06 | shown | narration must name every change |
| Clues found, PC knowledge | 15 | shown (journal) | |
| NPC identity, appearance | 12 | shown on meeting | |
| NPC standing toward the PC | 15 | available (rung name only) | the OFFER's DC reveals it anyway |
| NPC wants, refusals, knowledge, secrets | 15 / 12 | sealed until learned | |
| Adversary stat blocks | 09 | sealed | narrator gets tells |
| Adversary Vitality | 06/07 | background; "bloodied" (≤ half) and "down" shown | |
| Factions: existence, status to PC | 11 | available once known | |
| Faction goals, clocks, linchpins | 11 | hidden (omens) / sealed | |
| Threads (quest register) | 11 | shown | |
| Rumors: text heard | 11 | shown | truth value sealed |
| World facts known to the PC | 00 (fact type) | shown | |
| World facts unknown to the PC | 00 | background | |
| Secrets, mysteries, hidden solutions | 15 / 11 / 13 | sealed | |
| Clocks | the chapter that creates each | per the clock's visibility | |
| Frames, OFFER | 01 | shown | |
| Ruling ledger | 12 (use) / 00 (shape) | available | player may ask how something was ruled |
| Chronicle | 11 | available | |
| Tension dial, intensity, inconclusive streak | 12 | background | |
| Table recency lists, oracle log | 12 / 01 | background | answers become facts |
| Safety settings, preferences, auto-commit | 14 / 12 | shown | |

**00.6.4 Visibility classes.** `[D]` Constitution P3 requires every piece of tracked state to be
classified as background-resolved or player-facing [C:P3; BRIEF A3]. This ruleset refines the two
classes into four (the first two are player-facing, the last two background-resolved):
- **shown**: the codex displays it by default;
- **available**: the codex displays it on request; the DM answers a player's out-of-fiction question
  about it truthfully;
- **background**: engine and DM only; never shown as a number; may be voiced qualitatively in fiction;
- **sealed**: withheld even from the narrator's context until a gate opens (00.6.5).
The codex (14) renders exactly this classification; nothing is shown that is sealed, and nothing
shown may be contradicted by narration.

**00.6.5 Sealed state.** `[S]` + `[D]` Secrets are committed to state when the situation is created,
never "decided later" [R4 §5.2]. A sealed item carries a **gate**: the condition that unseals it (a
frame's degree unlocking a clue node; the PC entering a place; an NPC deciding to confide; a clock
completing). The engine uses sealed values in computation (an adversary's defense, a rumor's truth)
without ever returning them to the narrator's view. Instead the narrator receives the item's
*permitted slice*: tells, omens, qualitative bands, or an atmosphere tag ("theme: betrayal by kin")
[R4 §5.2 items 2 and 5]. `unseal` is the only way sealed content enters narration. *Invariant INV-10.*

**00.6.6 Write-on-mention.** `[J:flag]` + `[D]` When narration introduces a candidate element (an NPC, an
object, a door, an exit, a sound's source, a hazard, a feature of terrain), the DM asks: *"Could the
player plausibly cite this later as a lever, an obstacle, a hazard, a target, someone to talk to,
something to take, a route, or a clue?"* True only when the element is concrete and addressable;
false for pure atmosphere (the smell of rain, the color of the sky). Uncertain → true (SG-05 spirit).
If true, the element is recorded **before** the narration is delivered: `create_entity` (with an id
and the properties the narration implies) or `set_fact`. Properties the narration implies are fixed
now; properties it does not imply stay **undetermined** and are settled by the Oracle when first needed
(00.12.7), with odds set by the facts established at that moment [R4 SG-13; R: https://ianbicking.org/blog/2025/07/intra-llm-text-adventure].
*Worst case (J):* an atmospheric detail is recorded needlessly (harmless), or a relevant one is not (the
claim-vs-state check in ch.12 catches the narrated-but-unrecorded element, class iv).

**00.6.7 Assertion is not fact.** `[D]` A player's statement about the world is stored only as the
beat's `assertion` context in the frame, never as a fact (SG-06). Facts come from exactly six sources:
narration by the DM (recorded under 00.6.6), the Oracle, a generator, a ruling, data, or a player
proposal the DM *accepts* as an Oracle "Certain" (the scene type implies it). *Invariant INV-9.*

**00.6.8 Evidence event (tag_event) core shape.** `[D]` Ch.03 owns capture and weighting; these fields
are fixed so 01, 04, 06 and 11 can emit and read evidence in parallel [R6 §A.6; R1 #11]:

```yaml
EvidenceEvent:
  id: str
  actor: id
  time: time
  deed: str              # neutral one-line restatement of the observable act (not inner state)
  tags: [tag]            # most specific deed tags (cascade by engine), plus conduct tags
  conduct_sign: {tag: +1|-1}
  kind: enum             # judged | counted     (counted = fired automatically by a hook, 03)
  frame_id: str|null     # the resolved frame, if any; evidence fires only on RESOLVED outcomes
  degree: enum|null      # a success-at-cost is recorded as `success` [amended: IR ch.03 #3]
  challenge_band: int    # 1..5: from the final DC (DL-03-23); in a conflict, power_band + the advisory
                         # offset (trivial −2, easy −1, fair 0, hard +1, lethal +2), clamped [amended: DL-00-05]
  stakes: enum           # safe | risky | dire
  lethal_context: bool
  witnesses: [id]        # entities that observed it (gates PUBLIC recognition, 04/11)
  scope: str|null        # community or place reference for reputation (11)
```

Ch.03 extends this shape (03.2.1: fields added, none renamed) [amended: IR ch.03 #3].

**00.6.9 State discipline.** `[D]` (a) No state change without a tool write (INV-1). (b) Narration may
restate only what the store holds after this turn's writes (INV-2). (c) The latest write to a field
wins; history is kept. (d) A summary is never the source of truth for state, and a summary is never
summarized again [R1 §4 T-17]. (e) Temporal claims ("yesterday", "three days ago") are computed from
timestamps, never recalled [R1 §00.B].

### 00.7 Time: the ladder, the modes, and the boundary registry

**00.7.1 The time ladder.** `[D]` Game time is fictional and deterministic; real time never matters (no
real-time timers, no "if the player takes too long") [R5 §3.2 #3; resolves R5 TM-11]. Every duration,
cooldown and recurrence in the ruleset is expressed in these units (SG-28) [R5 §3.3; DL-00A-12].

| Unit | Length | Contains | Notes |
|---|---|---|---|
| **action** | part of an actor's turn | — | how many actions a turn holds is ch.06's (P9) |
| **round** | 6 seconds | one **turn** per acting side or entity (ch.06 orders them) | conflict only |
| **interval** | 10 minutes | 100 rounds | the exploration unit in sites (in other games, the "exploration turn") |
| **hour** | 60 minutes | 6 intervals | |
| **watch** | 6 hours | 6 hours | four per day: **morning** (dawn–midday), **afternoon** (midday–dusk), **evening** (dusk–midnight), **night** (midnight–dawn) |
| **day** | 24 hours, dawn to dawn | 4 watches | the day ends at dawn, after the night watch |
| **week** | 7 days | | the World Turn cadence (11) |
| **season** | 13 weeks = 91 days | | the consolidation boundary (VI) |
| **year** | 4 seasons = 364 days | | exact; the region's seed (12.16.15; a pre-made setting such as ch.13) names months, days and festivals inside it but adds no days [revision: I-028] |

A timestamp is `{year, season, week, day, watch, hour, interval, round}` plus a monotone beat counter.

**00.7.2 Event boundaries.** `[D]` Some boundaries are events rather than lengths of time. Each fires
when the event happens, whatever the clock says:

| Event boundary | Fires when | Who marks it |
|---|---|---|
| `beat_end` | a declaration has been fully resolved and recorded (pipeline step RECORD) | 01 |
| `turn_start` / `turn_end` | an actor's turn within a round begins / ends | 06 |
| `conflict_start` / `conflict_end` | round-by-round play begins / ends | 06 |
| `scene_start` / `scene_end` | a continuous situation with one focus is framed / cut | 12 |
| `breather` / `rest_short` / `rest_long` | a rest of that type completes (1 interval / 1 hour / 1 watch of sleep, at most one `rest_long` per day) | 07 |
| `reflection` | on each completed `rest_long`, on each week spent in downtime, and at each season boundary; at most once per day | 00 (derived) |
| `venture_start` / `venture_end` | the PC leaves safety / returns to safety | 10 |
| `session_start` / `session_end` | a real-world sitting begins / ends (not fictional time) | 12 |
| `mode_change` | the time mode changes (00.7.3) | 12 |

Rest durations are fixed here because the time math depends on them; what rests *restore* and what
*interrupts* them is ch.07's (and ch.05's for Focus). A rest boundary carries a payload
`{quality: full | partial | interrupted, site: haven | camp | rough, treated: bool}`, computed by ch.07
when it marks the boundary (07.8.1), so no handler depends on another's order to read it
[amended: DL-07-11].

**00.7.3 Time modes.** `[D]` + `[J:enum]` At every moment the game is in exactly one **time mode**,
which fixes how much time a beat consumes:

| Mode | Time per beat | Typical situations |
|---|---|---|
| `conflict` | beats happen within turns; time advances one round at each round's end | fights, chases in close pursuit |
| `site` | each significant beat (one that resolves a check or a meaningful activity) = 1 interval; insignificant beats = 0 | dungeons, ruins, searching a building |
| `free` | the activity's listed duration (ch.10 exploration activities, ch.15 social/investigation/downtime activities, ch.05 rituals, ch.07 rests); unlisted beats take no time | conversation, town scenes |
| `travel` | each travel activity = 1 watch | overland, water, underground journeys |
| `downtime` | each downtime activity = its listed days; the week is the planning unit | recovery, projects, training, trade |

The DM classifies the mode `[J:enum]` at each `scene_start` (default: the mode of the previous scene;
uncertain → `free`). *Worst case (J):* a scene run in `free` that should have been `site` under-consumes
intervals; the omission is bounded by the scene, and the site's own danger clock still ticks from
costs (class i).

**00.7.4 The boundary registry.** `[D]` Every chapter that needs something to happen at a boundary
registers a **handler** in `data/boundaries.yaml`: `{handler_id, boundary, phase, owner, effect,
interrupting}`. No rule may say "at the end of each day, remember to…" without a registered handler
(SG-11, SG-19). The registry's reserved handlers are listed in T-00-9 and seeded in the data file;
owners define each handler's behavior in their own chapter, may add handlers in their own owner-block,
and may not edit another owner's rows.

**00.7.5 Phases within a boundary.** `[D]` When a boundary fires, its handlers run in this fixed phase
order; within a phase, in registry order (by owner chapter number, then handler id), except that a
handler may declare `before: [handler ids]` to run ahead of named handlers of the same phase
(`h.07.rest_recovery` before `h.05.focus_recover` and `h.05.rest_recharge`) [amended: IR ch.07 #3].
Registry order is deliberate where it matters: in `interval` phase 2, `h.07.affliction_onset` (07) runs
before `h.10.site_exposure` (10), so an affliction contracted this interval first advances at the next
one, never twice in its first interval [integration: I-023].

| Phase | Name | What runs here |
|---|---|---|
| 1 | **expire** | durations reach zero; effects and conditions end |
| 2 | **periodic** | ongoing effects apply (burning harm, bleeding, regeneration) |
| 3 | **recover** | rests restore, recharges refresh |
| 4 | **consume** | upkeep: supply, light, wages, lifestyle |
| 5 | **clocks** | automatic ticks and decays; completions |
| 6 | **world** | World Turn, Season Turn, faction and situation processes |
| 7 | **checks** | encounter, omen and random-event rolls |
| 8 | **growth** | evidence consolidation, recognition passes, provisional confirmations |
| 9 | **record** | ledgers, chronicle, counters reset |

**00.7.6 Order across simultaneous boundaries.** `[D]` When several boundaries fall at the same instant,
event boundaries run first in this order: `conflict_end` → `scene_end` → rest completions →
`reflection` → `venture_end`; then time boundaries from the smallest unit to the largest: `round` →
`interval` → `hour` → `watch` → `day` → `week` → `season` → `year`. Each boundary runs all nine
phases before the next boundary begins.

**00.7.7 Skipping time runs everything.** `[D]` `advance_time` never jumps. It computes every boundary
the skipped span crosses and runs each one, in chronological order, with every registered handler, as
if the time had been played [R5 §3.2 #4]. Skipping three weeks runs twenty-one `day` boundaries, three
`week` boundaries (three World Turns), and everything else crossed. No handler may declare a shortcut
unless its result is provably identical (it may then run in closed form). *Invariant INV-15.*

**00.7.8 Interrupts.** `[D]` + `[T]` A handler marked `interrupting` (an encounter check that hits, a
clock completion that puts a threat on the scene, a random event that demands a response) raises an
**interrupt**. The current boundary finishes its remaining phases, so bookkeeping stays consistent;
then `advance_time` halts at that instant, returns the unconsumed remainder, and the DM frames a scene
at the interrupting event. The remainder is not "spent": the PC may resume the activity afterward
[WE-00-1].

**00.7.9 Session boundaries are not time.** `[D]` `session_start`/`session_end` never advance fictional
time. Because a solo player may stop at any moment, every bookkeeping step ch.12 registers on
`session_end` is also registered on `scene_end` [R5 §3.2 #5].

### 00.8 The clock primitive

**00.8.1 One clock.** `[D]` Every countdown, danger, progress track, faction goal, project, pursuit,
ritual, alarm, and extended task in the ruleset is an instance of this one structure; no chapter
invents another [R5 §2.3 P-17; R: https://bladesinthedark.com/progress-clocks; BRIEF A2 #11].

```yaml
Clock:
  id: str                    # "clk.alarm_grey_keep"
  name: str                  # names the obstacle or threat, never the method (SG-24)
  kind: enum                 # danger | progress | countdown | faction_goal | project | tug
  owner: str                 # chapter id and/or entity id that owns it
  segments: int              # 4 | 6 | 8 | 12
  filled: int                # 0..segments
  visibility: enum           # public | sensed | hidden
  direction: enum            # fill (only up) | tug (up and down; kind tug)
  tick_sources:              # the ONLY ways it ticks besides auto_ticks
    - {on: <hook | boundary | cost_type | trait | frame_ref>, ticks: <int | "delivered_reach" | "U(severity)">, condition: <state expr | null>}
  auto_ticks:  [{boundary: str, ticks: int, condition: str|null}]
  decay:       [{boundary: str, ticks: -int, only_if: "no tick since last <boundary>"}]
  omens:                     # required when visibility != public; >= 2 entries per stage
    stirring: [str]          # shown on a tick while filled < half
    building: [str]          # shown on a tick while filled >= half and not imminent
    imminent: [str]          # shown on a tick while remaining <= max(1, segments / 4)
  on_complete:
    effects: [{effect_id: str, params: map}]   # state writes, via the substrate
    interrupting: bool       # halts advance_time (00.7.8)
    then: enum               # close | reset | void
  races_with: clock_id|null
  links: [{when: "complete" | "reaches:<n>", action: "tick:<clock_id>:<n>" | "create:<template>" | "void:<clock_id>" | "unlock:<fact_id>"}]
  status: enum               # active | completed | voided | paused
  created: {at: time, by: rule_id}
  history: [{at: time, delta: int, source: str}]
```

**00.8.2 Tick amounts are never chosen.** `[D]` A tick's size comes only from the clock's own
`tick_sources` and `auto_ticks`, using these canonical conversions: progress from a resolved frame =
**delivered reach** (0–4, 00.3.15); a cost of a given severity = **U(severity)** (1, 1, 2, 3, 4 for
S1–S5, 00.3.11); a method consequence (e.g. a `trait.sense.loud` beat heard by a listening clock) =
the number the clock's source row states. The DM decides only *whether* a listed source fired
(`[J:flag]`, citing the frame or fact). *Worst case:* one source wrongly judged to fire = its listed
ticks, logged with the frame id (class i or iv) [R4 §4.3 "clock" row].

**00.8.3 Sizing.** `[J:rung]` When a rule creates a clock without a template size, the DM picks the
size from the ladder: **4** a simple obstacle or a scene's worth of effort; **6** complicated, several
distinct steps; **8** daunting, needs sustained effort across scenes; **12** a long project across
downtime. *Worst case (J):* one rung = 2–4 segments (class i). Templates in data fix sizes wherever
possible.

**00.8.4 Visibility and omens.** `[D]` + `[N]` A **public** clock's fill is shown in the codex. A
**sensed** clock's existence is known to the player but not its fill. A **hidden** clock is known only
through its omens. Every tick of a sensed or hidden clock obliges the narrator to render **one omen from
the current stage** in that turn's narration, as a perceivable trace (a sound, a sign, a change in
behavior, a rumor) that an attentive character could notice [INV-14; R5 §5.2 #4; R6 §B.3 B-R5]. The
engine selects the stage and the omen entry (without repeats until the list is exhausted); the narrator
chooses the wording. When a hidden clock reaches **imminent** and its completion would put the PC in
lethal danger, the lethal-warning trigger (ch.07) fires, which records `lethal_context` (Key 1 of the
Two-Key rule). Investigation may raise a clock's visibility (hidden → sensed → public) as a delivered
reach outcome (ch.15). *Narration may not imply:* the clock's exact fill (unless public), or any tick
that did not happen.

**00.8.5 Racing clocks.** `[D]` Two clocks with `races_with` pointing at each other race: the first to
complete wins, and the other is set `voided` (its `on_complete` never runs). If one event would complete
both, the clock ticked by the acting side's delivered reach completes first and the other is voided
(success is delivered before its costs, R7 §4.3) [R: https://bladesinthedark.com/progress-clocks
"racing clocks"; R3 §06.10].

**00.8.6 Linked clocks and tug clocks.** `[D]` `links` fire in list order when their condition is met
(`complete` or `reaches:n`) and may tick, create, void, or unlock. A `tug` clock may tick down as well as
up; a tug clock that reaches 0 from above triggers any link declared `reaches:0`. Completion effects
are a new causal root (depth 0, 00.10.8), so a clock completion may fire hooks, but a completion cannot
recur without the clock being reset.

**00.8.7 Clock procedure.** `[D]` See PR-00-3.

### 00.9 The condition schema

**00.9.1 Schema.** `[D]` Ch.06 owns the condition list (`data/conditions.yaml`); ch.07 owns afflictions
(staged poison, disease, curse) and injuries, which are built from conditions; every condition in the
game uses this schema [R2 #3; R2 §00 status registry; BRIEF A1].

```yaml
Condition:
  id: str                    # cond.*
  name: str
  tags: [tag]                # e.g. harm.fire for burning; trait.nature.mental for frightened
  category: enum             # physical | sensory | mental | positional | magical | affliction_stage
  severity: S1..S5           # default severity; instances may carry their own if severity_variable
  severity_variable: bool
  stacking: enum             # unique | refresh | replace_stronger | intensify | independent | escalate  (00.9.2)
  max_stacks: int            # for intensify / independent
  escalates_to: {condition: cond_id, at_stacks: int}   # for escalate
  duration: <duration expr>  # rounds:N | intervals:N | hours:N | scene | until_rest:<type> | until_cleansed | permanent | while:<state expr>
  decay: [{boundary: str, action: reduce_stack | reduce_severity | remove}]
  cleanse: [{means: str, requires: str|null, check: {verb: str, dc_tier: str}|null}]
  exclusion_group: str|null  # mutually exclusive family (e.g. "stance", "posture")
  priority_rank: int         # within its exclusion group
  neutralizes: [cond_id]     # applying this removes those, and this one is NOT applied (opposites)
  diminishing: {window: scene|conflict, halve_after: int, immune_after: int, group: str|null}|null   # control conditions; group = one shared counter per target (06.7.4) [amended: IR ch.06]
  modifies: [{effect_id: str, params: map}]    # via the substrate: status modifiers, restrictions, harm over time
  periodic: [{boundary: str, effect_id: str, params: map}]
  on_apply: [{effect_id, params}]
  on_remove: [{effect_id, params}]
  visible: bool              # perceivable by others; narration obligation when true
  narration_may_not_imply: [str]
  lifecycle: enum            # provisional | permanent | retired

ConditionInstance:
  instance_id: str
  condition_id: str
  target: id
  severity: S1..S5
  stacks: int
  remaining: <duration expr>
  source: {entity: id, effect_id: str, frame_id: str|null}
  applied_at: time
```

**00.9.2 The stacking vocabulary (closed).** `[D]` When a condition is applied to a target that already
has it, exactly one of these rules applies, as declared by the condition:

| Stacking | On reapplication | Example use |
|---|---|---|
| `unique` | ignored while an instance exists | prone |
| `refresh` | remaining duration becomes the longer of old and new; severity unchanged | blinded |
| `replace_stronger` | the instance with higher severity is kept (ties: refresh) | frightened |
| `intensify` | stacks +1 up to `max_stacks`; each stack adds its per-stack effect; duration refreshes | burning, bleeding |
| `independent` | a separate instance with its own duration, up to `max_stacks` | curses from different sources |
| `escalate` | stacks +1; at `at_stacks` the instance is replaced by `escalates_to` | chilled → frozen |

**00.9.3 Interactions.** `[D]` (a) Status modifiers from conditions obey the status family: only the
worst penalty and the best bonus on a given roll apply (00.3.5). (b) Restrictions (a condition that
forbids a verb, a method, a sense or a license, e.g. restrained forbids Move) are a union: if any
active condition forbids it, it is forbidden; a forbidden method is gated G4 for the beat (00.12.3).
(c) Within an `exclusion_group`, only the highest `priority_rank` instance is active; the others are
suppressed (they keep their durations and resume if the winner ends). (d) `neutralizes` resolves
opposites at application. (e) `diminishing` protects both sides from lock-down: a control condition
applied to the same target within the window lasts half as long after `halve_after` applications and
fails after `immune_after`; conditions sharing a `diminishing.group` share one counter per target
[R3 §06.7; amended: DL-06-14]. (f) Every condition's mechanical effects are effect references in
the substrate; a condition never carries prose-only mechanics (BRIEF §12).

**00.9.4 Reserved condition ids.** `[D]` Ch.06 owns every condition's definition, but because
chapters 05, 07, 08, 09, 10 and 16 reference conditions while being written in parallel, these ids are
reserved now with their intent; ch.06 must define each (it may add more, and may not rename or drop
these): `cond.off_balance`, `cond.prone`, `cond.grabbed`, `cond.restrained`, `cond.pinned`,
`cond.blinded`, `cond.deafened`, `cond.dazed`, `cond.stunned`, `cond.unconscious`, `cond.frightened`,
`cond.charmed`, `cond.distracted`, `cond.exposed`, `cond.slowed`, `cond.weakened`, `cond.exhausted`
(intensify, 3 stacks), `cond.bleeding` (intensify), `cond.burning` (intensify), `cond.chilled`
(escalate to `cond.frozen`), `cond.frozen`, `cond.choking`, `cond.poisoned` (the generic affliction
carrier used by ch.07's staged afflictions), and, added by ch.06, `cond.surprised`, `cond.silenced`,
`cond.broken`, `cond.heartened` [amended: IR ch.06]. One-line intents are in T-00-15. Harm states
(`staggered`, `dying`, `dead`) are **not** conditions; they are ch.07's harm-state ladder.

### 00.10 The composition substrate

The substrate is what lets any new ability, item property, condition or adversary power combine with
every existing one at zero authoring cost: precedence lives in one engine pass, not in pairwise rule
text [R3 §6 #2–3; BRIEF A2 #6; R4 SG-10]. It has six parts: effect definitions, effect operations,
trigger hooks, the evaluation pass, stacking families, and the four combination regimes, closed by one
recursion terminator. Canonical lists are in `data/substrate.yaml`; the core effect library is
`data/effects.yaml`.

**00.10.1 Effects are defined once and referenced everywhere.** `[D]` Every mechanical meaning in the
game is an **effect definition** in `data/effects.yaml` (the ruleset's equivalent of Diablo II's
`ItemStatCost` table). Abilities, item properties, conditions, adversary powers, composites, hazards
and clock completions never restate a mechanic in prose; they reference an effect id with parameters
[R3 §00.1]. This chapter seeds a **core library** of parameterized effects that cover the common cases
(check edges by tag, harm steps, reductions, resistances, condition application, resource changes,
lever grants, license grants, restrictions, slot claims, movement, ticks, reveals, creation,
prevention, redirection). A chapter adds a new effect definition only when no core effect with
parameters expresses it, in its own owner-block of the file, with a DL entry ("expand before you add",
R2 §00 Sanderson's Third Law).

```yaml
EffectDefinition:
  id: str                 # eff.*
  op: enum                # one of the 20 operations, 00.10.3
  quantity: enum|null     # for modify/step/multiply: the quantity it changes (T-00-13)
  family: enum|null       # modifier family (00.10.6)
  regime: enum            # additive | independent_trigger | priority_exclusive | named_composite
  hook: enum|null         # required for independent_trigger (00.10.2)
  slot: enum|null         # required for priority_exclusive (T-00-14)
  params: {name: type}    # declared parameters and their allowed ranges
  applies_when: expr|null # state condition (tags, harm types, verbs, situations)
  limits: {per: <boundary>, uses: int}|null
  player_only | adversary_only: bool
  text: str               # positive-scoped, literal (SG-15); rendered into narration packets verbatim
```

The expression context of `applies_when` (and of `when`/`active_when` in data) is the documented key
set: `verb`, `deed_tag`, `secondary_tags` (grounded), `harm_tags`, `situation`, `target_tags`,
`actor_tags`, `band`, `flags`, `conditions`, `gate.mode`, the resolver "your calling key", and the
event-scoped keys `event` and `event.target` ("this beat", "the target of this Strike")
[amended: IR ch.04 #3, IR ch.05 #5].

**00.10.2 The trigger hooks (closed list).** `[D]` A passive or active effect that responds to events
subscribes to exactly one hook from this closed list. With a closed list the DM always knows *where* to
check for effects, and a new effect composes with every old one without pairwise rules [R3 §00.5;
Slay the Spire hooks, R3 §2B]. The firing point of each hook is fixed by the resolution pipeline (01)
and the conflict loop (06):

| Group | Hook | Fires |
|---|---|---|
| Resolution | `on_declare` | a beat is declared, before GATE |
| | `on_frame` | a frame is computed, before OFFER (effects may add levers, change reach) |
| | `on_roll` | the d20 is rolled, before the degree is read (rerolls, fate) |
| | `on_degree` | the degree is known (params filter by degree) |
| | `on_check_against` | an aimed action targets this entity, before its roll (reactions) |
| Conflict | `on_attack_hit` | an attack by this entity succeeds (any success degree) |
| | `on_attack_miss` | an attack by this entity fails |
| | `on_hit_taken` | an attack against this entity succeeds, before harm is applied |
| | `on_harm_dealt` | harm from this entity has been applied |
| | `on_harm_taken` | harm to this entity has been applied |
| | `on_vitality_threshold` | Vitality crosses half, or reaches 0 (params pick which) |
| | `on_defeat` | this entity defeats a foe (the foe is Staggered, Dying, dead, yields, or flees) |
| | `on_move` | this entity's range band or positional flags change |
| Status | `on_condition_applied` | a condition is applied to this entity, or by this entity (param: `to`/`by`) |
| | `on_condition_removed` | a condition ends on this entity |
| Resources | `on_focus_spent` | this entity spends Focus (param: the ability's tags) |
| | `on_resource_depleted` | a quantity of this entity reaches its minimum |
| Time | `on_turn_start` / `on_turn_end` | this entity's turn within a round |
| | `on_boundary` | a named boundary of 00.7 fires (param: the boundary) |
| Things | `on_item_acquired` | this entity gains an item |
| | `on_equip` / `on_unequip` | an item is equipped or unequipped |
| World | `on_tag_event` | evidence with a matching tag is recorded for this entity |
| | `on_clock_tick` / `on_clock_complete` | a named clock (or kind) ticks or completes |
| | `on_fact_set` | a fact matching a key pattern is written (consequence propagation, 11) |
| Harm states | `on_dying` / `on_stabilize` | this entity enters Dying / leaves it |

A subscriber may filter on events that target it or happen near it, not only on its own: a reaction such
as Counterspell (another's `on_declare`), Riposte (the `on_degree` of an attack against the holder) or Set
Spear (another's `on_move`) is an "other entities' effect" in 00.10.7's order [amended: IR ch.05 #6].
Ch.03's evidence counters are **engine listeners** on these hooks, at any depth; they are not effect
subscribers and INV-12 does not apply to them (a listener writes counted evidence and nothing else)
[amended: IR ch.03 #5; DL-03-12].

Adding a hook is an amendment to this chapter.

**00.10.3 Effect operations (closed list).** `[D]` Every effect definition performs exactly one of
these twenty operations (full parameter lists in `data/substrate.yaml`):
`modify` (add to a quantity in the evaluation pass) · `step` (shift a ladder rung: severity, reach,
stakes, tier) · `multiply` (×2 or ×½ on harm) · `harm` (deal harm of a severity and harm tags) ·
`resource` (restore or drain a quantity) · `apply_condition` · `remove_condition` · `restrict` (forbid
a verb, method, sense or license) · `grant_license` (temporary or permanent) · `lever` (create a citable
fact that is a lever of a given type for stated beats) · `claim_slot` (take over a behavioral slot) ·
`move` (change range band or positional flags) · `tick` (tick a clock) · `reveal` (unseal a fact or clue)
· `create` (bring an entity into being from a template) · `trigger_check` (force a resisted check with a
degree table) · `prevent` (negate an incoming event) · `redirect` (change an incoming event's target) ·
`set_fact` · `economy` (change reactions; remove, never add, actions; see INV-11).

Readings fixed at integration: `lever` also grants **snags** (`sign: snag`, ch.06's `eff.06.grant_snag`),
and its `to:` may name those acting against the bearer, with `engine_cited` snags outside the two-cited
count (00.3.9 g) [amended: IR ch.06]; `prevent` may negate a named snag or a provoked reaction, not only a
hit (`eff.05.waive`); `remove_condition` may end a magical `effect_instance` that is not a condition
(`eff.05.end_working`) [amended: IR ch.05 #2; DL-05-25]; `step` admits the ladders `request_size` (R1–R5)
and `plausibility` (four rungs) besides severity, reach, stakes and tier, and `set_fact` on a
relationship is written through `set_relationship` (`eff.15.standing_step`) [amended: IR ch.15 #6;
DL-15-30].

**Invariant INV-11 (P9).** No effect grants additional *actions* per turn. `economy` may add or remove
reactions, only where ch.06 allows it, and may carry a non-positive `actions_delta` (dazed, stunned and
surprised remove actions) [C:P9; C:P14 cannot add actions, R3 §4 T-2; amended: IR ch.06 #1].

**00.10.4 The evaluation pass.** `[D]` Every computed quantity (T-00-13: a check total, a defense, a DC,
harm dealt, harm taken, a Focus cost, a duration, clock ticks, reach, stakes, maximum Vitality, maximum
Focus, speed, carrying capacity, price) is evaluated in one fixed order, with no exceptions and no
pairwise reasoning [R3 §00.6; Isaac's cache evaluation, R3 §2B]:

| Step | Name | What happens |
|---|---|---|
| E0 | **collect** | gather every applicable modifier: active effects whose `applies_when` holds, the frame's levers and snags, the entity's conditions |
| E1 | **base** | take the base value (anchor, obstacle, weapon, ability); if any `claim_slot` effect owns the relevant slot, its form replaces the base form |
| E2 | **steps** | apply rung shifts (degree/reach steps first, then effect steps), summed and clamped to the ladder; effect steps are capped at ±2 in total |
| E3 | **convert** | turn rungs into numbers via `data/scales.yaml` (e.g. S4 → 8) |
| E4 | **add** | add the additive families in this order, each by its own stacking rule and cap: attribute, competence, edge, circumstance, status, harm_edge, reduction, adjust. Before a family's own cap, contributions whose source is an **item** are summed and clamped to the family's **item share** (00.10.6) [amended: DL-08-07] |
| E5 | **multiply** | apply multipliers (at most one ×2 and one ×½; if both are present they cancel) |
| E6 | **clamp** | apply the global caps and floors (T-00-4); harm never below 0 |
| E7 | **round** | round down (only fractional values from E5 exist) |

The result and its full breakdown are stored in the frame (00.13) and shown in the OFFER.

**00.10.5 Harm uses the pass twice.** `[D]` Harm is evaluated on the dealer's side (base severity →
steps from delivered reach and effects → convert → harm_edge) and then on the receiver's side
(reduction → multipliers for resistance and vulnerability by harm tag → clamp at 0 → round down),
before ch.07 applies it to Vitality or wounds. A resistance or vulnerability always keys on a `harm.*`
tag and uses cascade (resisting `harm.fire` resists `harm.fire.heat`) [WE-00-6].

**00.10.6 Modifier families and stacking families.** `[D]` Each modifier belongs to exactly one family,
and each family has exactly one stacking rule (the closed stacking-family vocabulary: `single`,
`highest_only`, `sum_capped`, `worst_and_best`, `steps_clamped`, `multiplier_pair`):

| Family | Applies to | Stacking | Cap | Item share (08.2.2) |
|---|---|---|---|---|
| attribute | checks, defenses, effect DCs | single | per 00.4.3 | none (items never touch attributes) |
| competence | checks, defenses, effect DCs | highest_only | +6 | none |
| edge | checks, defenses, effect DCs | sum_capped | +2 | +1 per quantity |
| circumstance | checks (levers/snags only) | sum_capped | ±4 | one item lever per roll |
| status | checks, defenses | worst_and_best | −4 / +2 | — |
| step | any ladder quantity | steps_clamped | ±2 from effects (degree/reach steps uncapped) | ±1 |
| harm_edge | harm dealt | sum_capped | +2 | +1 |
| reduction | harm taken | sum_capped | ch.07 sets within 0…4 | 3 per harm tag |
| multiplier | harm dealt or taken | multiplier_pair | one ×2, one ×½ | ×½ resistance only from a tier-4+ signature |
| adjust | every other quantity (Focus cost, duration, ticks, maxima, speed, carry, price, supply use, travel points) | sum_capped | the quantity's own envelope | carry +4; supply −1 a day |

Items never touch attributes, competence, maximum Vitality or Focus, actions, slots or tiers
[amended: DL-08-07].

Two effects with the **same effect id** from different sources never stack in any family: only the
strongest instance applies (the one-copy rule, R3 §05.2). *Invariant INV-13* extends this to licenses:
an entity holds at most one instance of any license id; an item granting a license already held grants
nothing extra.

**00.10.7 The four combination regimes.** `[D]` Every effect declares exactly one regime; this single
field tells the DM and the engine how it combines with anything [R3 §05.5, §6 #3; C:P6]:

| Regime | Use when | Mechanism |
|---|---|---|
| **additive** | the effect is a number that adds to a quantity | writes into the evaluation pass in its family; no ordering needed beyond the pass |
| **independent_trigger** | the effect happens when an event happens (with or without a chance) | subscribes to one hook; each subscriber resolves separately; a chance is expressed as a d20 natural range ("on a natural 18–20") and rolled by the engine |
| **priority_exclusive** | the effect replaces *how* something works (what a strike delivers, how the entity moves, what its defensive reaction is) | claims one named **behavioral slot** (T-00-14) with a `priority_rank`; the highest rank owns the slot; every lower claimant is **fully suppressed**, including its numbers, unless it is marked `cosmetic_merge: true`; ties go to the earlier-acquired effect |
| **named_composite** | two distinctive primitives deserve a designed combination (constitution P6) | a hand-authored entry in `data/composites.yaml` keyed to exactly two low-cardinality keys (two `deed` branches, two `conduct` axes, two `harm` branches, or two license ids flagged `composite_key`); active while both keys are present; may suppress named components |

**Ordering of simultaneous triggers.** `[D]` When several independent triggers subscribe to the same
event, they resolve in this order: (1) the *target* entity's `prevent` and `redirect` effects (they may
cancel the event; if it is cancelled, no further subscriber fires); (2) the *acting* entity's effects;
(3) all other entities' effects; within each group by `priority_rank` descending, then by acquisition
time. Each resolves fully before the next begins.

**00.10.8 The recursion terminator.** `[D]` Every event carries a **depth**. An event caused directly by
a declared beat, an adversary's action, a condition's scheduled `periodic` effect, a boundary handler,
or a clock completion has depth 0. Anything an `independent_trigger` effect causes has depth 1.
**Hook subscribers fire only on depth-0 events.** A triggered effect therefore never triggers another
triggered effect: chains are at most one link long, infinite loops are impossible by construction, and
the DM never has to adjudicate a chain [R3 §00.8, RoR2's proc coefficient 0.0]. Core engine rules are
not subscribers and always apply regardless of depth: harm still reduces Vitality, a Vitality
threshold still produces Staggered or Dying, a clock tick still counts. *Invariant INV-12.*
*Example:* a spear hit (depth 0) fires Quarry's Mark (applies `cond.exposed`, depth 1); the wielder's
"when you apply a condition to a foe, regain 1 Focus" does **not** fire on that depth-1 application
[WE-00-6].

**00.10.9 Uses and recharge.** `[D]` Every active effect declares its limits as `{per: <boundary>,
uses: n}` or a Focus cost or both; the engine counts uses and refreshes them on the named boundary's
phase 3 (recover). "Once per encounter" means `per: conflict_end`; "once per rest" means
`per: rest_short` or `rest_long` as declared. No recharge exists only in prose [C:P5; R3 §05.8].

### 00.11 The gate→fill generator

**00.11.1 One generator for all emergent content.** `[D]` Every domain in which content is produced by
circumstance rather than picked from a menu runs this one algorithm: **loot** (08), **craft** (08),
**gift** (08; patron, order and faction boons), **item_ability** (08; the ability an item grants),
**absorb** (04; the calling-gated monster-power trait), **birth** (02; P1 birth variance) and **pick**
(04; `gen.pick`, the tier pick: a tag-gated `chosen` selection from 05's ability pool using steps 1, 2, 4
and 6 of 00.11.3, PR-04-5) [amended: IR ch.04 #1]. `gen.birth` uses three declared extensions: slots
drawn by **layer** (`magnitude_layers`), `degree: none` for every draw, and an entry-level
`excluded_when` (step 9's cap check moved before the draw) [amended: IR ch.02; DL-02-08]. A new
domain registers a configuration; it never writes a new generator [C:P5 sixth pass; R3 §6 #1;
BRIEF A2 #5]. The DM classifies; the tool computes content. The probe's shape (source gates the pool,
method picks the fill) is kept; the probe's content is not [R: src/ability_pool.py; BRIEF §7].

**00.11.2 Inputs.** `[D]` `generate(domain, source, circumstance, degree, options)`:
- **domain**: one registered domain id.
- **source**: the pool-gating circumstance: an entity id (whose tags and band are read) or, for
  materials and places, an id with tags. This is *what the thing fundamentally is*.
- **circumstance** `[J:enum]`: the fill-quality circumstance, *how the character engaged with it*,
  chosen from the domain's closed enum (for loot, the reference set is `decisive`, `costly`,
  `merciful`, `scavenged`; for craft, `commissioned`, `crafted`, `improvised`; each domain defines "true
  only when" text). Uncertain → the domain's declared default (for loot: `scavenged`).
- **degree**: the degree of the resolved frame that produced the acquisition, or `none`. Content is
  generated only from **resolved** outcomes (a narrated kill that was never resolved generates nothing)
  [R3 §6 #8].
- **options**: player choices for a `chosen` fill; the recency window; forced inclusions from a
  `recipe`.

**00.11.3 The algorithm.** `[D]` (full procedure PR-00-4)
1. **Pool gate.** Start from the domain's pool table. Keep entries whose `gate_tags` match the
   source's tags (match semantics 00.5.4c). Remove entries whose `excluded_tags` match, entries whose
   `base_kinds` exclude the output's base (e.g. a weapon-only property on a charm), and entries flagged
   `player_only`/`adversary_only`/`cannot_absorb` against this use. This is a hard zero-weight
   exclusion [R3 §08.1].
2. **Tier gate.** The source's band sets `tier_cap` (T1 → 1 … T5 → 5); remove entries whose minimum
   tier exceeds it (the band plays the role of Diablo II's item level) [R3 §08.4].
3. **Quality rung and slots.** The domain maps `(circumstance, degree)` to a quality rung, and the rung
   fixes the number of **signature slots** (0 or 1, the identity layer) and **magnitude slots** (the
   magnitude layer). Counts are fixed per rung, never variable [R3 §00.2, §08.9].
4. **Fill method.** The domain maps the circumstance to one of five fill methods (closed list):
   `signature` (the source's signature entry fills the signature slot; magnitude slots by weight),
   `biased` (weights ×3 for entries carrying the domain's bias tag for this circumstance), `chosen`
   (the player picks from up to three eligible entries shown by the tool), `weighted` (plain weighted
   draw), `recipe` (the entries a known recipe names, deterministic).
5. **Degree effects.** A critical success grants **Greater**: one property (signature first) gains
   +1 tier, which may exceed `tier_cap` by at most 1. A critical failure grants **Flawed**: one
   magnitude slot is removed, or, for craft, one property carries its entry's declared flaw.
6. **Fill, slot by slot.** Signature slot first, then magnitude slots. After each pick, remove every
   entry sharing the picked entry's `mod_group` (hard mutual exclusion) and every entry the recipient
   already holds as a unique [R3 §08.5].
7. **Recency.** Entries produced in the last 5 draws of this domain have their weight halved (never
   removed), to counter repetition; to keep weights integers, every weight is doubled before any is
   halved [R4 SG-12; R4 §3.3 W10; amended: IR ch.08].
8. **Magnitude.** Each picked property takes its entry's value for its tier (fixed per tier; no
   rolled ranges).
9. **Caps.** Check the per-object slot cap and the item layer's power budget (08). If a pick would
   break a cap, drop that pick and refill that slot once; if it fails again, leave the slot empty.
10. **Output.** A generated object with provenance (source id and tags, domain, circumstance, degree,
    quality rung), its signature and magnitude properties with effect references, any sealed
    properties (unidentified), and a generation log (pool size after each gate, weights, draws). The
    tool writes it to state; the DM narrates only what the output contains and names it
    (write-on-mention). The DM never adds a property the output does not hold.

**00.11.4 Character bias is not an axis.** `[D]` The generator uses exactly two circumstances
(source and manner) [C:P5]. It never biases toward the recipient's calling or tags (no "smart loot").
Relevance to the player comes through `chosen` fills (patron gifts, commissions) and through the player
choosing where to hunt and what to craft [R3 §4 T-9; DL-00A-18].

**00.11.5 What items grant.** `[D]` An item property is one of three kinds: **mundane** (magnitude
only: harm_edge, reduction, capacity), **passive** (an additive or triggered effect while equipped), or
**item-bound active ability** (a license usable only while equipped, occupying an *equipped* ability
slot, 00.17 contract 05↔08). Relics that license off-identity capabilities do so at a surcharge and
never feed calling tiers [R2 #9]. This resolves BRIEF §8's deferred "what dropped items grant" at the
level of structure; 08 owns the tables.

### 00.12 Licenses, the basic verbs, and the Oracle

**00.12.1 License schema.** `[D]` Principle VII's gate is a lookup: every capability beyond the basic
verbs is a **license** with this schema, and every license entry in any data file conforms to it
[C:VII; R7 §4.4; BRIEF A2 #13]:

```yaml
License:
  id: str                 # lic.* (or ab.* for abilities, which are licenses with mechanics)
  name: str
  kind: enum              # basic_verb | ability | spell | calling_capability | training | language | item_property | fact | condition_grant | rank | universal
                          # universal: held by every character beyond the closed 15 verbs (lic.focus.push) [amended: IR ch.05 #3]
  tags: [tag]             # deed tags it belongs to (evidence, competence, emulate domain)
  principle: str          # the governing principle in one sentence (what it fundamentally does)
  scope: str              # POSITIVE literal statement of what it lets you attempt (SG-15)
  excludes: [str]         # nearest things it does not cover, each with the license that would
  grades: [{grade: str, scope: str}]   # optional ordered grades (e.g. language: broken, accented, native)
  attribute: str|"by_method"          # governing attribute for checks it licenses
  grants_competence: [{tag: tag, value: int}]   # optional (training licenses)
  crude_fallback: {verb: verb_id, method: str, dc_shift: 0|5|10, reach_cap: limited|standard, consequence: str|null} | none
  stretch: {dc_shift: int, cost_add: int, reach_cap: limited|standard, within: principle} | null
  emulate: {allowed_for: str, dc_shift: int, cost_mult: int, reach_cap: str, crit_fail: effect_ref, learn_clock: clock_template} | null
  acquisition_paths: [{type: recognition|mentor|project|item|origin|institution|bargain|discovery, detail: str, clock: clock_template|null, requires: str|null}]
  effects: [{effect_id, params}]      # for abilities/items; via the substrate
  cost: {focus: int}|null
  limits: {per: boundary, uses: int}|null
  source: str             # what granted it (origin id, calling tier, item id, fact id)
  feeds_evidence: bool    # default true; false for relic-granted licenses: deeds done under it write no
                          # evidence (00.11.5; 08.4.4; 03 drops them) [amended: IR ch.04 #11]
  lifecycle: enum         # provisional | permanent | retired
```

**00.12.2 The literal-reading rule.** `[D]` A license covers exactly its `scope` text read literally,
at its held grade. If a license covers only part of a beat, the beat is split: the covered part is
licensed; the rest falls to the basic verbs or is unlicensed [R7 §4.0 step 2]. Narration may never
describe a license doing more than its scope ("the flames part around you" from a heat resistance is an
embellishment, not a ruling). *Invariant INV-8.* **Rolls never grant licenses**: a license changes only
through its `acquisition_paths`, recognition (04), an item, or a recorded fact; a success at an
unlicensed technique through `emulate` ticks a learning clock and nothing more. *Invariant INV-7.*

**00.12.3 Gate classes.** `[J:enum]` Ch.01 owns the GATE procedure; this chapter fixes the classes every
chapter refers to [R7 §4.0 step 2]:

| Class | True only when | Result |
|---|---|---|
| **G0 Question** | the player is asking about the world, not acting | answer from state; if unestablished, the World-Fact Oracle (00.12.7) |
| **G1 Basic** | the method is one of the 15 basic verbs within its `covers` list | always legal |
| **G2 Licensed** | the method needs a license and the actor holds one whose literal scope covers this beat | legal under that license |
| **G3 Unlicensed** | beyond the basic verbs, no held license covers it, but someone *could* | never narrated as possible; redirect to the domain's `crude_fallback` (if not `none`) and name at least one `acquisition_path`; no time or action spent unless the player accepts the alternative |
| **G4 Impossible** | contradicts an established fact or the setting's canon for anyone, or delivered reach would be Zero, or an active condition forbids the method | no roll; one sentence of fiction saying why; offer the nearest achievable intent or method (P16) |

Default when uncertain between G2 and G3: G3 (SG-05). *Worst case (J):* a licensed attempt is redirected
(the player sees the license id that was checked and can point out the error; class iv), or an
unlicensed attempt is allowed as G2 (the frame records the license id cited, which the auditor checks;
class iv).

**00.12.4 Stretch and emulate.** `[D]` Two priced ways to reach past a license's literal scope keep
goal 1 alive without breaking VII [R2 #4; R7 §4.4]:
- **Stretch**: a holder uses *their own* license in a new way that is within its `principle` but
  outside its literal `scope`, at the license's `stretch` price (higher DC, extra Focus, capped reach).
  A license with `stretch: null` cannot be stretched.
- **Emulate**: a holder of a *domain* license attempts an adjacent technique of the same domain they
  have witnessed but do not know, at the `emulate` price; success ticks the learning clock.
Non-holders get neither; they get `crude_fallback` and `acquisition_paths`.

**00.12.5 The basic verbs (the default license set).** `[D]` Fifteen verbs are always legal for every
character; the list is closed, and new content extends licenses, never this list [C:VII; C:V;
R7 §4.1]. Admission test: *any able-bodied adult in the setting could attempt this with no training and
a real chance*. Ch.01 owns each verb's anchor card (knobs, degree table); `data/basic_verbs.yaml` holds
ids, coverage, exclusions and attributes (T-00-11 summarizes).

`verb.move` · `verb.observe` · `verb.recall` · `verb.talk` · `verb.strike` · `verb.grapple` ·
`verb.force` · `verb.exert` · `verb.evade` · `verb.sneak` · `verb.handle` · `verb.endure` ·
`verb.setup` · `verb.help` · `verb.ready`

**Yield** (a Talk that surrenders on terms) and **Retreat** (a Move that withdraws from a conflict) are
named uses of basic verbs that are always legal; ch.07 owns their outcomes [R6 §C.3 C-R4].

**00.12.6 Free activities.** `[D]` These never roll and never need a license; they still consume time
per the time mode: wait; rest; eat and drink; sleep; speak a few words (not an attempt to persuade);
draw, stow, drop, pick up or hand over an unattended item; look around casually (noticing without a
check is ch.01's passive rule); recall your own memories and the character's established facts; ask the
DM an out-of-fiction question (takes no fictional time).

**00.12.7 The World-Fact Oracle (G0).** `[J:rung]` + `[D]` When the answer to a question about the world
is **unestablished** (not in state, not implied by narration) and **not settled by setting canon or
scene logic**, the DM chooses an odds rung **before** rolling, from the scene's nature and never from
what the player wants, and the engine rolls d100 [BRIEF A2 #10; R7 §4.7; R5 §2.1]. Rungs: Certain (no
roll, yes) · Likely · Even · Unlikely · Remote · Impossible (no roll, no). Ch.01 owns the thresholds
and the doubles-as-twist rule; ch.12 owns the DM's use of the same Oracle for its own questions and
any tension shift, which may move the rung by at most one. The answer is written as a fact at once
(`source: oracle`), and a "no" is followed in the same breath by what *is* there (P16). Established
facts are never asked again. *Worst case (J):* a one-rung odds error shifts the chance by 15–25 points,
logged with the question (class i).

### 00.13 The resolution frame

**00.13.1 The frame is the contract between judgment and narration.** `[D]` Every rolled beat is
resolved through one typed record, the **frame**, produced by a structured adjudication step before any
prose is written, then consumed by narration [R4 §9 00 #2; R4 R-07; R: https://arxiv.org/abs/2502.19519].
Ch.01 owns the procedure that fills it (the pipeline PARSE → GATE → NECESSITY → ANCHOR → FRAME → OFFER
→ ROLL → READ → DELIVER → CONSEQUENCE → RECORD); every chapter's rules must be expressible as fields of
it, and none may add a judgment step outside it.

```yaml
Frame:
  id: str
  beat: {id: str, actor: id, intent: str, method: str, assertion: str|null,     # assertion = player claims, context only
         shape: single|sequential|repeated|bundled|conditional|extended, parent_beat: str|null,
         declared: bool}             # false for a resisted-effect check the actor did not choose (03's D3) [integration: IR ch.03 to 01]
  gate: {class: G0|G1|G2|G3|G4, verb: verb_id|null, license: license_id|null, mode: normal|stretch|emulate|fallback}
  necessity: {roll: bool, reason: uncertain_and_costly|riding|trivial|good_idea|impossible|take_the_time|certain_with_cost}
  secret: bool                       # ch.01 secret frames (DL-01-13)
  threatened_cost: {menu_id: str, severity: S1..S5} | null   # declared at FRAME (DL-01-07)
  alternate_cost:  {menu_id: str, severity: S1..S5} | null
  trade: none|go_big|play_it_safe    # DL-01-14
  anchor: {rule_id: str, deltas: [str], precedent: ruling_id|null}          # deltas <= 2 (00.2.7)
  attribute: attr_id
  deed_tag: tag                     # primary (00.5.6); secondary: [tag]
  traits: [tag]
  obstacle: {id: str|null, dc_source: stored|opposed|tier|effect, tier: str|null, defender: id|null, dc: int}
  levers: [{fact_id: str, type: precision|protective|amplifying}]            # <= 2
  snags:  [{fact_id: str, type: precision|protective|amplifying}]            # <= 2
  stakes: {rung: safe|risky|dire, lethal: bool, failure_preview: str}
  reach:  {rung: limited|standard|great, factors: [str]}
  modifier: {attribute: int, competence: int, edge: int, circumstance: int, status: int, total: int}   # computed
  odds: {success_or_better: int, critical_success: int, critical_failure: int, near_miss: int}        # computed, shown
  base_odds: int                     # success-or-better with circumstance = 0 (03's quality read) [integration: IR ch.03 to 01]
  request: {size: R1..R5, effective: R1..R5, terms: [{type, ref}]} | null   # social beats (15.3) [amended: IR ch.15 #3]
  claim: {fact: str, plausibility: str, shifts: [str]} | null              # a claim the beat asserts (15.5) [amended: IR ch.15 #3]
  offer: {shown_at: time, choice: commit|change|withdraw|auto}
  roll: {d20: int, total: int, margin: int} | null
  degree: critical_success|success|failure|critical_failure|null
  near_miss: bool
  success_at_cost_taken: bool
  delivered: {reach: 0..4, units: int|null, items: [str]}
  costs: [{menu_id: str, severity: S1..S5, form: str}]
  method_consequences: [str]
  state_writes: [write_ref]
  evidence: [evidence_id]
  ruling: ruling_id|null
```

**00.13.2 Frame invariants.** `[D]` `roll_check` refuses a frame unless: the gate class is G1, G2 (or a
G3 fallback the player accepted) with the license or verb id present; every lever and snag cites an
existing established fact; the stakes rung is set; `lethal` is legal (00.3.14); the offer choice is
`commit`, or `auto` under the player's auto-commit preference (ch.14; never for a lethal frame). The
frame is immutable after the roll except for the READ, DELIVER, CONSEQUENCE and RECORD fields.
*Invariants INV-5, INV-6, INV-20.*

### 00.14 The tool surface

These are **requirements** for the deterministic instruments the rules assume, stated as prose schemas;
they are not code. The current five tools (`roll_check(dc, modifier)`, `get_state`, `update_state` /
`update_resource`, `set_fact`, `grant_ability`) are defaults the surface below replaces [BRIEF §5;
R: src/tools.py; R: src/world_state.py]: `roll_check`'s free `dc` and `modifier` integers are removed
(the frame computes them); `update_state`/`update_resource` become `update_quantity`; `set_fact` is
typed; `grant_ability` becomes `generate` + `grant`.

**00.14.1 Runtime capabilities.** `[D]` Each tool names the capabilities it implies:

| Id | Capability |
|---|---|
| RC-RNG | a seeded random generator whose every draw is logged with its purpose |
| RC-STORE | a typed, update-on-write state store with ids, clamps, timestamps and write history |
| RC-SEAL | a sealed partition with gates, and a narrator view that filters sealed content |
| RC-SCHED | the time model and boundary registry, with ordered phases and interrupts |
| RC-LOG | append-only ledgers (writes, evidence, rulings, oracle, offers, chronicle) |
| RC-DATA | a loader for `data/*.yaml` that validates every id and enum against the schemas |
| RC-QUERY | tag-ancestry queries and pool filtering (competence lookup, gate→fill, cascade) |
| RC-EVAL | the substrate executor: evaluation pass, hook dispatch, regimes, depth |
| RC-RETRIEVE | rule-card retrieval by situation tags, anchors, and active triggers |
| RC-AUDIT | claim-versus-state comparison over the store |

**00.14.2 The tools.** `[D]` Inputs → outputs; the owner chapter defines semantics beyond the shape.

| # | Tool | Inputs | Outputs | Owner | RC |
|---|---|---|---|---|---|
| 1 | `frame_check` | beat, gate, anchor, attribute, deed_tag, obstacle, levers, snags, stakes, reach | frame with computed DC, modifier breakdown, odds, cost previews; or a refusal naming the failed validation | 01 | STORE, DATA, EVAL, QUERY |
| 2 | `roll_check` | frame_id | d20, total, margin, degree, near_miss | 01 | RNG, LOG |
| 3 | `read_result` | frame_id, take_success_at_cost: bool | delivered reach, cost severities due | 01 | EVAL |
| 4 | `deliver` | frame_id, items ranked by the player | count delivered and which items (P17) | 01 | EVAL |
| 5 | `apply_costs` | frame_id, [{menu_id, form}] | state writes applied; refusal if the severity or menu id is illegal | 01 | STORE, EVAL |
| 6 | `oracle` | question, odds_rung, fact_key | d100, yes/no, extreme, twist; the fact written | 01 / 12 | RNG, STORE, LOG |
| 7 | `roll_table` | table_id, context {tags, band}, exclude_recent | the entry (and any sub-rolls); recency updated | 12 (and table owners) | RNG, DATA, LOG |
| 8 | `get_state` | scope (entity, place, scene, codex), view (narrator, codex, audit) | the permitted slice; sealed fields replaced by permitted slices | 00 | STORE, SEAL |
| 9 | `create_entity` | kind, template_id, fields, visibility, sealed_fields | id | 00 | STORE, DATA |
| 10 | `set_fact` | subject, predicate, value, source, certainty, visibility | fact id (supersedes any prior value) | 00 | STORE, LOG |
| 11 | `update_quantity` | entity, quantity, delta, reason, frame_id | new value, clamps applied, raised triggers (e.g. Vitality 0) | 00 (07/05/08/10 semantics) | STORE, LOG |
| 12 | `set_relationship` | a, b, kind, value or steps, reason | new value | 15 / 11 | STORE |
| 13 | `set_position` | entity, location or {band_to: {entity: band}}, flags ± | new position; `on_move` fired | 10 / 06 | STORE, EVAL |
| 14 | `record_knowledge` | knower, fact_id, how ∈ {witnessed, told, read, overheard, recalled, inferred, rumor, confided} (15.9.17); an engine listener exposes lies on `contradicted_by` [amended: IR ch.15 #5] | ok | 15 | STORE |
| 15 | `seal` / `unseal` | item ref, gate / via | ok; unsealed content now in narrator view | 00 | SEAL, LOG |
| 16 | `apply_effect` | effect_id, params, source, targets, depth | results of the effect and any hooks it fires | 00 | EVAL, STORE |
| 17 | `apply_harm` | target, severity, harm tags, source {entity, frame}, lethal, mode (lethal \| nonlethal), no_reduction, periodic, dealt [amended: IR ch.07 #1] | amount applied, full breakdown, harm-state transition, wound, load | 07 | EVAL, STORE |
| 18 | `apply_condition` / `remove_condition` | target, condition_id, severity, duration, source | instance after stacking rules | 06 | EVAL, STORE |
| 19 | `use_ability` | actor, ability_id, targets, frame_id | validation (license, slot, recharge, Focus), Focus spent, effect results | 05 | EVAL, STORE |
| 20 | `evaluate` | quantity, context | value and breakdown (for previews and the codex) | 00 | EVAL |
| 21 | `advance_time` | amount {unit, n} or until {boundary or event}, mode | boundaries crossed, handler results, interrupt with the halt time and the remainder | 00 | SCHED, RNG, LOG |
| 22 | `mark_boundary` | event boundary id | handler results | 00 | SCHED |
| 23 | `create_clock` / `tick_clock` / `set_clock` | template or fields / clock_id, source_ref / visibility or status | clock state, stage, omen key, completion effects | 00 | STORE, SCHED, EVAL |
| 24 | `generate` | domain, source, circumstance, degree, options | the generated object and generation log | 00 (08, 04, 02 configure) | RNG, QUERY, DATA, STORE |
| 25 | `record_evidence` | op (record \| void \| add_witness \| atonement; default record) with an EvidenceEvent, or (event_id, reason), or (event_id, entity, how, fact_id) [amended: IR ch.03 #1] | event id (nothing about tallies is returned) | 03 | STORE, SEAL, LOG |
| 26 | `evaluate_recognition` | trigger (reflection \| crisis \| arrival \| request) [amended: IR ch.04 #4] | packets per 04.4.6 {calling_id, tier, kind, policy grant/offer/abstain, vehicles, price_ids, deed_lines, alternatives, reading?}; no numbers | 04 | SEAL, QUERY |
| 27 | `offer_create` / `offer_resolve` | offer / offer_id, answer accept, decline or defer | offer state; grants on accept | 04 / 11 | STORE, LOG |
| 28 | `grant` / `revoke` / `retire` | entity, license, ability or calling tier, provisional, source (an offer id or {calling, tier}); `retire` takes `superseded_by` and leaves specialties (04.8.5) [amended: IR ch.04 #5] | new holdings; lifecycle updated | 04 / 05 | STORE, LOG |
| 29 | `log_ruling` / `find_rulings` | ruling record / anchor_id, deltas, tags | id / matching precedents | 12 | LOG, QUERY |
| 30 | `get_active_triggers` | none | every `[T]` currently true, with the rule-card ids to load | 12 | RETRIEVE, STORE |
| 31 | `load_cards` | situation tags, anchor ids, trigger ids | rule cards | 12 | RETRIEVE |
| 32 | `check_claims` | claims extracted from draft narration | mismatches against state | 12 | AUDIT |
| 33 | `chronicle_append` | entry | ok | 11 | LOG |
| 34 | `codex` | view | the player-facing render per visibility class | 14 | STORE, SEAL |
| 35 | `log_turn` | turn record {input verbatim, frames, writes, claim-check verdicts, narration} | turn id | 12 | LOG |
| 36 | `revert_writes` | write ids, reason (only within the current scene; ch.12 error correction, DL-12-04) | reverted values, compensating log entries | 12 | STORE, LOG |

**00.14.3 What the DM supplies to tools.** `[D]` Only: ids (of entities, facts, licenses, rules,
clocks, tables), enum values from `data/`, rungs, flags, the player's stated quantities, and short
text (intent, method, reasons, forms). Never a DC, modifier, harm amount, tick count, odds number,
price or duration (SG-01). *Invariant INV-3.*

### 00.15 Rule cards, the anchor index, and the ruling ledger

**00.15.1 The substrate is delivered as retrievable cards.** `[D]` The rich substrate lives as
numbered rules packaged as **rule cards**, plus data entries, plus an **anchor index**, plus the
**ruling ledger**. It is never loaded wholesale: irrelevant-but-plausible rules degrade accuracy far
more than neutral filler [BRIEF A3; R4 §3.3 W13; R: https://arxiv.org/abs/2412.08972].

**00.15.2 Rule-card record.** `[D]` Each numbered rule compiles to one card (the markdown template of
00.2.5 is its source):

```yaml
RuleCard:
  id: str                  # "06.3.2"
  title: str
  kinds: [str]             # e.g. ["[J:rung]", "[D]"]
  loads_in: [tag]          # situation.* tags; "core" for always-loaded cards
  trigger: str|null        # [T] condition, if the card is trigger-loaded
  license_check: str|null
  decisions: [str]
  computation: str|null
  stakes: str|null
  state_writes: [str]
  narration_may_not_imply: [str]
  worst_case: str|null     # required when kinds contains a [J:*]
  examples: [{side: inside|outside|non_example, text: str}]
  anchor: {intent_verbs: [str], deed_tags: [tag], knobs: [{knob: str, default: str, allowed_deltas: [str]}]} | null
  tables: [table_id]
  basis: [str]
```

**00.15.3 The anchor index.** `[D]` Every card with an `anchor` block is entered into
`data/anchors.yaml` (compiled by ch.12 from the chapters' cards), keyed by intent verbs, deed tags and
situation tags. At the ANCHOR step the DM chooses `[J:enum]` among the anchors the index returns for
the beat's verb and tags (at most eight candidates; default: the anchor of the beat's basic verb).
*Worst case:* a near-but-wrong anchor, bounded by the two-change limit and logged (class iv).

**00.15.4 The always-loaded core.** `[D]` Only these travel with every turn: the turn-loop checklist
(ch.12), the invariants T-00-1, the gate classes (00.12.3), the stakes/reach/lever card (00.3.9,
00.3.14–15), and the active-trigger list. Everything else loads by `situation.*` tag, anchor, or
trigger [R4 §9 00 #5; R4 §3.3 W12]. The packet is capped at the core plus **at most twelve** loaded
cards, with the player's message verbatim and the **last four exchanges** verbatim; ch.12 owns these
numbers (`pacing.yaml#packet`) [amended: DL-12-02].

**00.15.5 Ruling ledger record.** `[D]`

```yaml
RulingRecord:
  id: str
  time: time
  frame_id: str
  signature: str            # "<anchor_id>+<delta1>+<delta2>", deltas sorted
  situation: str            # neutral one-line restatement of the case
  facts_cited: [fact_id]
  frame_summary: {attribute: str, dc_source: str, dc: int, levers: [str], snags: [str], stakes: str, reach: str}
  result: {degree: str, outcome: str}
  precedent: {status: new|reused|departed, from: ruling_id|null, differing_fact: fact_id|null}
  kind: adaptation|oracle|good_idea|g4|g3_redirect|rule_conflict
  review_flag: bool         # true when a ruling looks like a rule breakdown (Principle III revisit evidence)
  tags: [tag]
```

**00.15.6 Precedent rule.** `[D]` + `[J:flag]` Before framing any beat that needs an anchor adaptation,
an Oracle call, a Good Idea, or a G3/G4 decision, the DM calls `find_rulings`. If a record matches the
signature, the DM reuses its numbers, unless a stated fact differs, which the new record names in
`differing_fact` [R7 §4.8; R5 G-13]. *Worst case (J):* a precedent reused where a fact differed (class iv:
the player can cite the fact; a new ruling supersedes). The ledger also supplies the "recorded concrete
failure case" that constitution III's revisit trigger requires [C:III].

### 00.16 Data-file conventions

**00.16.1 Format.** `[D]` YAML, UTF-8, 2-space indentation. Every file opens with a comment block
stating purpose, owning chapter, and the schema it follows (`data/SCHEMAS.md` section). Every file has
a top-level `schema_version` and a list under a named key. Every entry has a stable snake_case `id`
with its file's prefix, a human `name`, `tags` from `data/tags.yaml`, a `lifecycle`, and a `basis`
citation [BRIEF §12].

**00.16.2 Id prefixes.** `[D]` Ids are globally unique, and the prefix tells any reader which file
defines them: `attr` (attributes, bare ids), `verb.` basic verbs, `eff.` effects, `cond.` conditions,
`aff.` afflictions, `inj.` injuries, `ab.` abilities, `rit.` rituals, `lic.` other licenses, `call.`
callings, `hyb.` hybrids, `comp.` composites, `veh.` recognition vehicles, `orig.` origins, `bi.` base
items, `prop.` item properties, `mat.` materials, `arch.` adversary archetypes, `adv.` adversaries,
`haz.` hazards, `trap.` traps, `site.` site themes, `fac.` factions, `loc.` places, `npc.` NPCs,
`clk.` clock templates, `tbl.` tables, `gen.` generator domains, `h.` boundary handlers, `slot.`
behavioral slots, `anc.` anchor cards, `scn.` scenes, `trg.` triggers (added for ch.12). Added at
integration [amended: IR ch.08, 09, 11, 13, 15, 16]: `pow.` adversary-only powers (09,
`archetypes.yaml#powers`), `flaw.` item flaws (08, `item_properties.yaml#flaws`), `dt.` downtime
activities, `case.` investigation cases, `lie.` recorded lies (15), `cmp.` companion templates, `kn.`
companion knacks (16), `sit.` situations, `sit_t.` situation templates, `bang.` bangs, `wr.` world
reactions, `thr.` threads, `rum.` rumors, `rep.` reputation entries, `chr.` chronicle entries, `imp.`
improvements, `ftpl.` faction templates, `legacy.` legacy records (11), `keeper.` keepers, `obj.` named
objects (a region's: the world seed, 12.16, or a pre-made setting such as 13 [revision: I-028]). Tags use facet paths (`deed.…`) with no prefix.

**00.16.2a The id-prefix registry.** `[D]` Generated at integration from the ids defined in `data/` (`_process/simulation/integration-prefix-registry.py`); every prefix in use is registered here with the file(s) that define it and the owning chapter (T-00-19). 00.16.2's named prefixes are the core of this list; a new prefix is added by regenerating the table [amended: integration, DL-INT-11].

| Prefix | Defined in | Owner | Note |
|---|---|---|---|
| `ab.` | `abilities.yaml`, `gen_absorb.yaml`, `gen_item_ability.yaml` | 04; 05; 08 | |
| `act.` | `travel.yaml` | 10 | |
| `adv.` | `adversaries.yaml` | 09 | |
| `aff.` | `afflictions.yaml` | 07 | |
| `anc.` | `anchors.yaml` | 12 | |
| `arch.` | `archetypes.yaml` | 09 | |
| `axis.` | `behaviors.yaml` | 09 | |
| `band.` | `conflict.yaml` | 06 | |
| `beh.` | `behaviors.yaml`, `conflict.yaml` | 06; 09 | |
| `bi.` | `base_items.yaml` | 08 | |
| `birth.` | `gen_birth.yaml` | 02 | |
| `cal.` | `calendar.yaml` | 11 | |
| `call.` | `callings.yaml` | 04 | |
| `canon.` | `region_thallen.yaml` | 12 (a world seed's output, 12.16) / 13 (`region_thallen.yaml`, an optional pre-made seed) [revision: I-028] | |
| `case.` | `investigation.yaml` | 15 | |
| `ci.` | `region_thallen.yaml` | 12 (a world seed's output, 12.16) / 13 (`region_thallen.yaml`, an optional pre-made seed) [revision: I-028] | |
| `clk.` | `abilities.yaml (inline clock spec)`, `behaviors.yaml`, `behaviors.yaml (inline clock spec)`, `companions.yaml`, `conflict.yaml`, `downtime.yaml`, `economy.yaml (inline clock spec)`, `factions.yaml`, `harm.yaml`, `investigation.yaml`, `licenses.yaml (inline clock spec)`, `pacing.yaml`, `region_thallen.yaml`, `rituals.yaml (inline clock spec)`, `sites.yaml`, `social.yaml`, `world_turn.yaml (inline clock spec)` | 05; 06; 07; 08; 09; 10; 11; 12; 12 (a world seed's output, 12.16) / 13 (`region_thallen.yaml`, an optional pre-made seed) [revision: I-028]; 15; 16 | clock templates and instances (00.8); families declared by `id_pattern` |
| `clu.` | `investigation.yaml` | 15 | |
| `cmp.` | `companions.yaml` | 16 | |
| `cnt.` | `evidence.yaml` | 03 | |
| `comp.` | `composites.yaml` | 05 | |
| `cond.` | `conditions.yaml` | 06 | |
| `cost.` | `resolution.yaml` | 01 | |
| `dt.` | `downtime.yaml`, `legacy.yaml` | 11; 15 | |
| `eff.` | `effects.yaml` | 00 (core library) | |
| `end.` | `legacy.yaml` | 11 | |
| `fac.` | `factions.yaml` | 11 | |
| `fam.` | `world_turn.yaml` | 11 | |
| `fest.` | `calendar.yaml` | 11 | |
| `fg.` | `callings.yaml` | 04 | |
| `flag.` | `conflict.yaml` | 06 | |
| `flaw.` | `item_properties.yaml` | 08 | |
| `forb.` | `callings.yaml` | 04 | |
| `ftpl.` | `factions.yaml` | 11 | |
| `fx.` | `calendar.yaml` | 11 | |
| `gen.` | `00-architecture.md#00.11.1 (PR-04-5 over abilities.yaml)`, `gen_absorb.yaml`, `gen_birth.yaml`, `gen_craft.yaml`, `gen_gift.yaml`, `gen_item_ability.yaml`, `gen_loot.yaml` | 00; 02; 04; 08 | |
| `h.` | `boundaries.yaml` | 00 | boundary handlers (T-00-9) |
| `harm_state.` | `harm.yaml` | 07 | |
| `haz.` | `hazards.yaml`, `sites.yaml` | 10 | |
| `hold.` | `economy.yaml` | 08 | |
| `hyb.` | `hybrids.yaml` | 04 | |
| `imethod.` | `investigation.yaml` | 15 | |
| `imp.` | `world_turn.yaml` | 11 | |
| `inj.` | `injuries.yaml` | 07 | |
| `item.` | `region_thallen.yaml` | 12 (a world seed's output, 12.16) / 13 (`region_thallen.yaml`, an optional pre-made seed) [revision: I-028] | item entities (00.6.2: `item.i0042`; the region's storied items) share their first segment with the tag facet `item`; ids and tags never coincide |
| `journal.` | `investigation.yaml` | 15 | |
| `keeper.` | `region_thallen.yaml` | 12 (a world seed's output, 12.16) / 13 (`region_thallen.yaml`, an optional pre-made seed) [revision: I-028] | |
| `kit.` | `kits.yaml` | 02 | |
| `kn.` | `companions.yaml` | 16 | |
| `lc.` | `harm.yaml`, `last_chance.yaml` | 07 | |
| `ledger.` | `legacy.yaml` | 11 | |
| `lic.` | `licenses.yaml` | 05 | |
| `loc.` | `region_thallen.yaml` | 12 (a world seed's output, 12.16) / 13 (`region_thallen.yaml`, an optional pre-made seed) [revision: I-028] | |
| `mat.` | `materials.yaml` | 08 | |
| `month.` | `calendar.yaml` | 11 | |
| `nem.` | `behaviors.yaml` | 09 | |
| `npc.` | `region_thallen.yaml` | 12 (a world seed's output, 12.16) / 13 (`region_thallen.yaml`, an optional pre-made seed) [revision: I-028] | |
| `obj.` | `region_thallen.yaml` | 12 (a world seed's output, 12.16) / 13 (`region_thallen.yaml`, an optional pre-made seed) [revision: I-028] | |
| `orig.` | `origins.yaml` | 02 | |
| `ph.` | `world_turn.yaml` | 11 | |
| `plaus.` | `social.yaml` | 15 | |
| `pow.` | `archetypes.yaml` | 09 | |
| `pregen.` | `region_thallen.yaml` | 12 (a world seed's output, 12.16) / 13 (`region_thallen.yaml`, an optional pre-made seed) [revision: I-028] | |
| `price.` | `vehicles.yaml` | 04 | |
| `prop.` | `item_properties.yaml` | 08 | |
| `quarter.` | `calendar.yaml` | 11 | |
| `refusal.` | `social.yaml` | 15 | |
| `req.` | `callings.yaml#requirements` | 04 | |
| `request.` | `social.yaml` | 15 | |
| `rit.` | `rituals.yaml` | 05 | |
| `rl.` | `factions.yaml` | 11 | |
| `seam.` | `legacy.yaml` | 11 | |
| `sit.` | `region_thallen.yaml` | 12 (a world seed's output, 12.16) / 13 (`region_thallen.yaml`, an optional pre-made seed) [revision: I-028] | |
| `sit_t.` | `world_turn.yaml` | 11 | |
| `site.` | `sites.yaml` | 10 | |
| `skip.` | `legacy.yaml` | 11 | |
| `slot.` | `substrate.yaml` | 00 | |
| `smethod.` | `social.yaml` | 15 | |
| `st.` | `world_turn.yaml` | 11 | |
| `standing.` | `social.yaml` | 15 | |
| `svc.` | `economy.yaml` | 08 | |
| `tbl.` | `archetypes.yaml`, `behaviors.yaml`, `companions.yaml`, `companions.yaml#drives`, `companions.yaml#tbl.16.betrayal (key)`, `conflict.yaml`, `factions.yaml#tbl.11.entanglement (key)`, `factions.yaml#tbl.11.faction_seed (key)`, `factions.yaml#tbl.11.faction_tier (key)`, `factions.yaml#tbl.11.vacuum (key)`, `harm.yaml`, `investigation.yaml`, `legacy.yaml#tbl.11.successor_traits (key)`, `oracles.yaml`, `origins.yaml`, `region_thallen.yaml`, `rituals.yaml`, `sites.yaml`, `travel.yaml`, `weather.yaml`, `world_seed.yaml`, `world_turn.yaml#tbl.11.distortion (key)`, `world_turn.yaml#tbl.11.epithet_forms (key)`, `world_turn.yaml#tbl.11.fallback_form (key)`, `world_turn.yaml#tbl.11.hook (key)`, `world_turn.yaml#tbl.11.land_changes (key)`, `world_turn.yaml#tbl.11.local_events (key)`, `world_turn.yaml#tbl.11.rumor_truth (key)`, `world_turn.yaml#tbl.11.rumors (key)`, `world_turn.yaml#tbl.11.season_events.autumn (key)`, `world_turn.yaml#tbl.11.season_events.spring (key)`, `world_turn.yaml#tbl.11.season_events.summer (key)`, `world_turn.yaml#tbl.11.season_events.winter (key)` | 02; 05; 06; 07; 09; 10; 11; 12; 12 (a world seed's output, 12.16) / 13 (`region_thallen.yaml`, an optional pre-made seed) [revision: I-028]; 15; 16 | tables, wherever they live (keyed or with an id) |
| `term.` | `social.yaml` | 15 | |
| `thr.` | `harm.yaml` | 07 | |
| `trap.` | `sites.yaml`, `traps.yaml` | 10 | |
| `veh.` | `vehicles.yaml` | 04 | |
| `verb.` | `basic_verbs.yaml` | 00 (ids, coverage) / 01 (anchor fields) | |
| `wage.` | `economy.yaml` | 08 | |
| `wc.` | `world_turn.yaml` | 11 | |
| `wr.` | `world_turn.yaml` | 11 | |
| `ws.` | `world_seed.yaml` | 12 | |

**00.16.3 Lifecycle (VI at content scale).** `[D]` Every entry carries `lifecycle: provisional` until it is
promoted to `permanent` by the test below; retirement is `lifecycle: retired` with `superseded_by`
and never deletion, so old saves and ledgers still resolve. A squish (rescaling numbers) is not
retirement [C:VI; BRIEF A3 VI scope].
- **Promotion test** `[D]` (04.8.2's confirmation test applied to content; `pacing.yaml#review.promotion`).
  An entry is a **promotion candidate** when all three hold: (a) the ruling ledger shows it applied (cited
  by a ruling, or used by a tool call) in at least **20 evidence-bearing scenes** (03.6.1) over at least
  **2 sessions**; (b) no ruling that cites it was overturned (a correction, 12.3.4; an upheld dispute,
  12.3.6; a ruling-error correction) since its count began; (c) no open Principle III candidate or rule
  candidate of the review list names it (12.12.4, 12.12.6). An overturned ruling restarts its count at 0.
  20 sits between 04.8.2's 12-scene confirmation and 24-scene lapse windows: long enough that an entry has
  met more than one situation, short enough that a used entry promotes within a campaign's first seasons.
- **Who promotes.** `h.12.session_close` lists the session's new promotion candidates in the review list
  (12.12.4). An entry the campaign wrote itself (a world-seed entity, 12.16; improvised content, 12.13.4;
  the card of an adopted rule candidate, 12.12.6) is promoted by the engine when listed: no judgment is
  involved. A shipped entry (`rules/data/`) is promoted only by the project's maintainers in a verification
  wave, entry by entry, with play's review lists as the evidence (05.12.3); a campaign's listing of it is a
  report, and changes nothing in that campaign.
- **What promotion changes.** The codex drops the entry's "(provisional)" mark. A permanent entry is
  never demoted: a fault found later is fixed by retirement and a successor, which starts provisional
  [revision: I-043; DL-00A-31].

**00.16.4 Mechanics are data.** `[D]` Every entry with mechanics has them fully specified in data
(numbers, triggers, recharge, effect references). Prose-only mechanics are a defect [BRIEF §12].

**00.16.5 The files.** `[D]` T-00-19 lists every data file, its owner and its schema section in
`data/SCHEMAS.md`. A file owned by one chapter may be extended by another only through an owner-block
(`blocks: [{owner: "07", entries: [...]}]`) where T-00-19 says so; otherwise additions go through
Interface requests.

### 00.17 Chapter contracts

Each chapter **provides** named interfaces (functions of state, data files, handlers, reserved ids) and
**consumes** others'. A chapter may rely on a consumed interface exactly as specified here, even before
the providing chapter is written. A chapter that needs something not listed files an Interface request;
it does not invent it [BRIEF §9].

**00.17.1 Pre-resolved ownership questions.** `[D]` Every cross-chapter question raised by BRIEF
Addendum A and the digests' interface requests is decided here.

| # | Question | Decision |
|---|---|---|
| Q1 | Focus recovery: 05 or 07? | **05** owns Focus entirely (pool, costs, every recovery channel and amount). **07** owns rest: what counts as a `breather`, `rest_short`, `rest_long`, what interrupts one, and its `quality` (full / partial / interrupted), which it passes on the boundary event. 05 registers the `h.05.focus_recover` handler on those boundaries and may add non-rest channels (calling generation triggers, consumables through `eff.restore`). Vitality recovery is 07's. |
| Q2 | Slot ceiling: 05 or 08? | **05** owns the single hard ceiling on held abilities and its **three partitions**: `calling` (from recognition, 04), `acquired` (absorbed, taught, learned, emergent), `equipped` (item-bound actives, only while equipped). The partitions sum to the ceiling; envelope 12–24 total (reference 20 = 12 + 4 + 4). **08** must keep every item to at most one item-bound active ability and may never add slots; passive and mundane properties use no ability slot and count against 08's item-layer budget instead [R3 §4 T-12]. |
| Q3 | Condition list: 00 or 06? | **00** owns the schema, the stacking vocabulary and the reserved ids (00.9); **06** owns `data/conditions.yaml` and every definition; **07** owns afflictions and injuries in its own files, built from conditions; 05, 08, 09, 10, 16 reference conditions by id only. |
| Q4 | Recognition vehicles vs faction reactions (04↔11)? | **04** owns the vehicle table V1–V14 and the offer protocol; on every grant, offer, decline or revocation it emits `recognition_event {actor, calling, tier, policy, vehicle, witnesses, scope, answer}`. **11** consumes it to update reputation, faction status and rumors, and provides `institutions_matching(deed_branch, region) → [faction_id]` for V3/V9 staging. 04 never writes faction state; 11 never grants capability [R6 §A.6 R-A5]. |
| Q5 | PC power band (04→09)? | **04** provides `power_band(pc) → 1..5` computed `[D]` from confirmed tiers only (04.5.6: a provisional tier counts once confirmed; never from narration) [revision: I-037]; **09** provides `threat_advisory(encounter, pc) → trivial / easy / fair / hard / lethal` from threat bands, count and `power_band`; **07** consumes `lethal` advisories into the lethal warning. |
| Q6 | The Oracle: 01 or 12? | **01** owns the one Oracle mechanism (odds rungs, thresholds, doubles, when a player-driven beat needs it). **12** owns the DM's use of it for its own questions, the tension dial (which may shift a rung by at most one), and the meaning/inspiration tables (`data/oracles.yaml`). There is one odds ladder. |
| Q7 | Clocks: who owns them? | **00** owns the primitive; the chapter that creates a clock owns that instance and its template (faction goals 11, alarms and site dangers 10, chases 06, projects 15, rituals 05, dying and afflictions 07, recognition readiness 04). |
| Q8 | Companions (16↔06)? | **16** owns companion templates (within the envelope at the band of the companion), loyalty (on the standing scale), journey roles, and what companions may do. **06** owns the action economy: a companion has **no separate turn**; it acts only when the PC spends an action to command it, or through its own reactions and hooks; 06 defines the command action's cost. **07** owns companion harm: companions are protected by Key 1 (declared lethality) but have no last-chance menu. Presence sets retinue size (00.4.4). |
| Q9 | The meta-currency? | Exactly one: **`fate`** (0–3). **01** owns earning, spending in resolution, and the cap; **07** consumes `spend_fate(1)` for the last-chance menu's reprieve. No chapter creates another spendable luck currency. |
| Q10 | Tags: who writes `data/tags.yaml`? | **00** seeds levels 0–2; **03** owns the file and all deeper content; stewards (T-00-7) propose additions in their facets through Interface requests. |
| Q11 | Evidence: who records it? | Any chapter emits `record_evidence` at resolved significant moments; **03** owns significance criteria, weights, anti-grind and recency; counted evidence fires automatically from hooks 03 registers (e.g. `on_focus_spent` with the ability's tags). **04** reads only tallies. |
| Q12 | Provisional status | **Content scale:** every data entry (00.16.3). **Character scale:** 04 owns provisional grants, confirmed or lapsed at the `season` boundary (`h.04.season_consolidation`), and at `reflection` for early confirmation if 04 so rules. This extrapolation from PoE leagues is recorded as such [BRIEF A3]. |
| Q13 | Disposition vs faction status | One **standing** scale (−3…+3) for both. **15** owns NPC standing and its social DC effects; **11** owns faction status; a faction member's default standing toward the PC equals the faction's status (15 may shift it by one for individuals). |
| Q14 | Positioning | **06** owns relationship-state. Reserved range bands (ids fixed now because 05, 08, 09, 10 reference them): `band.engaged`, `band.close`, `band.near`, `band.far`, `band.distant`. Reserved positional flags: `flag.flanked`, `flag.cornered`, `flag.in_cover`, `flag.elevated`, `flag.hidden`, `flag.mounted`, `flag.lined_up`, and (added by 06) `flag.obscured`, `flag.in_chokepoint`, `flag.aloft` [amended: IR ch.06]. 06 defines each; it may add flags. |
| Q15 | Harm states | **07** owns the ladder; reserved ids: `harm_state.active`, `.staggered`, `.dying` (with steps 1…N, 07 sets N in 2…4), `.dead`; the disposition `defeated` (out of the fight, alive) is a flag written by 07. Death requires the Two-Key rule (INV-6). |
| Q16 | Rests and their durations | Durations fixed by 00.7.2 (breather 1 interval; short 1 hour; long 1 watch of sleep, once per day); effects and interruption rules 07; Focus 05. |
| Q17 | Starting kit vs item ids | **02** writes kits as `{item_tag, quality, quantity}` using `item.*` tags; **08** resolves tags to base items. So 02 never needs 08's ids. |
| Q18 | Hazards: 07 or 10? | **10** owns hazard entries (`data/hazards.yaml`: severity, harm tags, effect DC, exposure cadence); **07** owns what harm does. Hazard harm uses the severity scale. |
| Q19 | Calendar | **00** fixes the ladder arithmetic (364-day year); **11** owns the calendar engine and the Season Turn; the region's seed (**12.16.15**; a pre-made setting such as **13**) names months, days and festivals [revision: I-028]. |
| Q20 | Magic | **05** owns magic as a subsystem (spells as abilities, rituals as clocked extended tasks, research, learning by observation = `emulate`); the region's seed (**12.16.5**, written by the world seed; a pre-made setting such as **13** supplies its own) holds setting canon about magic (what is impossible for the Oracle's Impossible rung) [revision: I-028]. |
| Q21 | P9 vs P14 | **06** resolves in its DL; the architecture constraint is INV-11: no build, calling or effect gains actions; cadence differences may live only in tempo, reactions, or what one action contains. |
| Q22 | Reputation vs recognition | Recognition (capability) is 04's; reputation (what the world says) is 11's; ranks (seats in institutions) are 11's; losing a rank never removes capability [R6 §A.6 R-A5]. |

**00.17.2 Contract table.** `[D]` "Provides" lists interfaces other chapters may call or read;
"Consumes" lists what the chapter may rely on.

| Ch. | Provides | Consumes |
|---|---|---|
| **01 Resolution** | the pipeline procedure; `frame_check`/`roll_check`/`read_result`/`deliver`/`apply_costs` semantics; DC numbers for the tier ladder (meeting CT-1…CT-6); degree rule (crit bands, natural 20/1); near-miss and success-at-cost; READ tables (degree × reach → delivery; degree × stakes → cost severity); the **cost menu** ids (`cost.harm`, `cost.drain`, `cost.gear`, `cost.time`, `cost.exposure`, `cost.footing`, `cost.shortfall`, `cost.closed_door`, `cost.twist` — ids reserved here); `deliver_count(N, reach)`; compound, repeated, conditional, extended, opposed, group, help and setup rules; the Oracle mechanism; `fate`; anchor cards for the 15 verbs (knobs, degree tables); the `trait.*` general rules | 00 scales, attributes, verbs, licenses, tag lookup, substrate; 03 tag content; 05/02/04/08 licenses and competence; 06 conditions and status modifiers; 12 ruling ledger |
| **02 Character** | creation procedure (full, fast, pregen); attribute generation in the 00.4.3 envelope; origins (P4 trade-offs) granting licenses (`lic.lang.*`, training) and competence entries; birth variance as `gen.birth` + deferred reroll (P1); the P2 floor value (competence at `deed`); starting Vitality and Focus formulas within envelope; starting kits as item tags; drives, bonds, aspirations and background hooks for 11 | 00 attributes, scales, gate→fill; 03 tags; 05 license schema content; 08 base items by tag; 11 hook format; 13 origins' setting content |
| **03 Tags & Evidence** | `data/tags.yaml` below level 2, with definitions and tests; `record_evidence` semantics and the full tag_event schema (extending 00.6.8); significance criteria; weighting (challenge band, stakes, witness, lethal); saturation and anti-grind; recency windows; counted-evidence hooks; `tally(pc, tag) → {raw, weighted, recent}` (sealed; 04 only) | 00 tag top levels, hooks, boundaries (`reflection`, `scene_end`); 01 frames and degrees; 09 threat bands; 11/15 witness data |
| **04 Recognition & Growth** | callings (specialist and hybrid) in `data/callings.yaml`, `data/hybrids.yaml`; scoring and a concrete definition of confidence; grant/offer/abstain thresholds; `evaluate_recognition`; vehicles V1–V14 (`data/vehicles.yaml`); offer protocol and standing offers; tier ladder (stated maximum) with competence values and capabilities per tier; crystallization; shadows and the Fraying; character-scale provisional status; `power_band(pc)`; `gen.absorb` configuration; `recognition_event`; calling synergy composites (entries in 05's composites file, owner-block 04) | 03 tallies; 05 slots and ability pool; 00 gate→fill; 11 `institutions_matching`; 12 OFFER script |
| **05 Abilities, Focus, Magic** | slot system with the three partitions and the hard ceiling; ability template grammar (license schema + effect refs + regime + limits + cost + scope/limitation/weakness/cost + principle + stretch); `data/abilities.yaml`, `data/rituals.yaml`, `data/composites.yaml`; `use_ability`; Focus pool, costs, recovery handlers; recharge types; magic subsystem; ability modifiers | 00 substrate, licenses, scales; 07 rest events; 03 counted evidence; 04 tiers; 08 item-bound abilities |
| **06 Conflict** | action economy (actions per turn, reactions; INV-11); turn order and tempo (P9/P14 decision); range bands and positional flags (reserved ids); attack and defense procedure; weapon harm base severities (with 08); `data/conditions.yaml` including the reserved ids; reactions; multi-target over relationship-state; morale; surrender; escape and chases (racing clocks); mobs and swarms as single entities; repeated-attack penalty; companion command action | 07 harm application and states; 09 templates and behaviors; 00 substrate, clocks, boundaries; 16 companion templates |
| **07 Harm, Recovery, Death** | Vitality semantics; staggered, wounds, dying ladder, death; the Two-Key rule and the lethal-warning trigger (writes `lethal_context`); last-chance menu; Yield and Retreat outcomes; defeat dispositions → world-state writes; marks and scars; rest definitions and rest events with quality; Vitality recovery; afflictions (`data/afflictions.yaml`), injuries (`data/injuries.yaml`), mental strain; companion harm; `apply_harm` semantics; the reduction cap | 00 severity scale, conditions schema; 06 conditions; 01 `fate`; 09 `defeat_disposition`, `lethal_context`; 10 hazards; 11 world-state writes; 03 evidence for marks |
| **08 Items, Loot, Crafting** | item schema; `data/base_items.yaml`, `data/item_properties.yaml`, `data/materials.yaml`, `data/economy.yaml`; generator domains `gen.loot`, `gen.craft`, `gen.gift`, `gen.item_ability`; quality rungs and slot counts; relics; crafting as clocked extended tasks; prices, wealth, encumbrance (from Might), supply goods, mounts and vehicles; the item-layer power budget | 00 gate→fill, substrate; 09 archetype tags and threat bands; 01 degrees; 05 equipped partition |
| **09 Adversaries** | archetypes as manufacturers (`data/archetypes.yaml`: evidence tags, loot pool gate, absorbable pool, behaviors); threat bands T1–T5 stat templates within the 00.3.7 envelope; `threat_advisory`; solo encounter budgets; behavior priority lists and morale thresholds; `lethal_context` and `defeat_disposition` per archetype; tells; `data/adversaries.yaml` | 04 `power_band`; 06 conditions and economy; 07 harm; 08 pools |
| **10 Exploration, Travel, Sites** | travel by watches; supply; navigation; the overloaded encounter/omen check per watch and per interval; weather; `data/hazards.yaml`; sites (Delve-style procedure, one interval per significant beat); traps; foraging; light; place graph semantics; exploration activity durations; `venture_start/end` | 00 time ladder, clocks, boundaries; the region's content (12.16's world seed, or a pre-made setting such as 13) [revision: I-028]; 09 encounters; 07 harm |
| **11 Living World** | World Turn (`h.11.world_turn` on `week`); Season Turn (`season`); factions (`data/factions.yaml`); situations and default timelines; threads register; rumors with truth values; reputation; ranks; holdings; calendar engine; chronicle; retirement and legacy; `institutions_matching` | 04 `recognition_event`; 03 evidence; 00 clocks, time; 01/12 Oracle |
| **12 DM Procedures** | the turn loop (adjudication before narration; claim-vs-state check; error correction); mode transitions; scene framing; the DM's Oracle use and tension dial; pacing director; P16 counter and lead-injection table; P17 in practice; NPC generation and reaction roll; `data/oracles.yaml`; `data/anchors.yaml` (compiled); ruling ledger use; session moves; spotlight rotation for one player; twist table (target of `cost.twist`); OFFER script; the **world seed** (12.16, `data/world_seed.yaml`): a complete starting region from session-zero questions and oracle tables, checked against everything the rules read from a region (T-12-16) [revision: I-028] | everything |
| **13 Starter Setting (optional)** | one optional pre-made world seed: a region record of the world seed's shape (places, NPCs, factions with running clocks, bestiary subset, loot pools subset, encounter and rumor tables, names, setting canon, calendar names, languages as licenses, a first-session teaching arc, pregens), which must pass the seed check (12.16.17); no rule depends on it [revision: I-028] | every chapter's schemas; 12.16 |
| **14 Player's Guide** | the player-facing rules; codex spec rendering the visibility classes; out-of-fiction offer markers; session zero and safety; auto-commit preference; fast creation presentation | 00 visibility; 02; 04 offers; 12 session moves |
| **15 Social, Investigation, Downtime** | standing semantics and social DC composition (on 00.3.8); negotiation; deception, insight and claim plausibility; NPC wants, refusals and walk-away; investigation clue graphs (sealed nodes, ≥ 3 placements); `record_knowledge`; downtime activities and long projects (clocked, week cadence) | 11 reputation and factions; 12 NPC generation; 00 clocks, Oracle, sealing |
| **16 Companions & Allies** | companion, hireling and follower templates; loyalty; journey roles; companion behaviors; costs; recognition interplay (companions as witnesses) | 06 command action; 07 companion harm; 10 journeys; 11 factions; 15 standing |

### 00.18 Glossary

`[N]` One canonical name per concept; chapters must use these names (SG-21). Distinguishing tests are
given where two terms could be confused. Terms are grouped for reading; `data/scales.yaml` and the
index (appendix) carry the machine list.

**Resolution**
- **beat**: one declared action with one method, one target and one intended change; the unit the
  pipeline resolves. *Not* a turn (a turn may contain several beats).
- **intent** / **method**: what the player wants to be true afterward / what the character physically,
  verbally or magically does. The attribute follows the method.
- **assertion**: anything the player states as fact or outcome; context only, never a fact.
- **check**: a d20 roll resolving a beat. (Not "skill check", not "saving throw"; a resisted effect is
  an Endure or Evade check.)
- **frame**: the typed resolution record (00.13).
- **OFFER**: showing the player the frame (DC or target number, odds, stakes, reach, costs) before the
  roll, with the choice to commit, change method, or withdraw.
- **DC**: the number a check total must reach. Comes from a stored DC, a defense, an effect DC, or an
  obstacle tier.
- **defense**: `10 + attribute + competence + edge + status` for an entity resisting an aimed action.
- **effect DC**: the same formula from a source whose effect the target resists.
- **obstacle / obstacle tier**: the thing being overcome / its difficulty rung (Easy … Legendary).
- **degree**: critical success, success, failure, critical failure. **near miss**: a failure with margin ≥ −3 (including a success
  stepped down by a natural 1). **margin**: total minus DC.
- **stakes**: the pre-declared rung (Safe / Risky / Dire) of how bad failure can be. **lethal**: the
  frame flag that allows death (00.3.14).
- **reach**: the pre-declared rung (Limited / Standard / Great) of how much success achieves;
  **delivered reach**: the 0–4 number after the degree.
- **cost**: an entry from 01's closed cost menu paid on failure or success-at-cost. *Distinguish*
  **consequence**: a side-effect of the *method* that happens regardless of degree (noise, evidence).
  *Distinguish* **harm**: Vitality loss or wounds; harm may be a cost or a consequence.
- **lever** / **snag**: a cited established fact that helps / hinders a roll, typed Precision,
  Protective or Amplifying.
- **attribute**: one of the seven (00.4). **competence**: the tag-based trained bonus (00.3.6).
  **edge**: capped flat bonuses from items and abilities. **status**: modifiers from conditions.
  **base modifier**: attribute + competence + edge.
- **anchor**: an existing rule chosen to resolve a novel action. **knob**: a declared parameter an
  adaptation may change. **two-change limit** (00.2.7).
- **ruling** / **precedent**: an improvised decision recorded in the ruling ledger / a recorded ruling
  reused.
- **Oracle**: the World-Fact Oracle, d100 against pre-chosen odds.
- **gate** (capability gate) with classes G0–G4. *Distinguish* **pool gate** (the generator's first
  step); always say "pool gate", never bare "gate", for the generator.

**Capability**
- **license**: permission to attempt something beyond the basic verbs (00.12). **basic verb**: one of
  the fifteen always-legal verbs. **free activity**: never rolls, never needs a license.
- **scope**, **principle**, **excludes**, **grade**, **crude fallback**, **stretch**, **emulate**,
  **acquisition path**: license fields (00.12.1).
- **ability**: a license with mechanics in `data/abilities.yaml`; **active** (player-invoked, with
  limits) or **passive** (always on when its `applies_when` holds). **spell**: an ability of a magic
  deed branch. **ritual**: a clocked magical extended task.
- **slot**: one place in an ability partition (calling / acquired / equipped). *Distinguish*
  **behavioral slot** (`slot.*`, 00.10.7) which a priority-exclusive effect claims.
- **calling**: the ruleset's word for class; a derived identity (04). **specialist** / **hybrid**.
  **tier**: depth within a recognized calling. **rank**: a seat in an institution (11), never
  capability. **band**: power band P1–P5 / threat band T1–T5. **grade**: a license's rung.
  **rung**: any step of any ladder.
- **recognition**: a calling or tier being granted, offered, or withheld (**grant / offer / abstain**).
  **crystallization**: the moment a tier deepens. **vehicle**: the fictional staging of recognition
  (V1–V14). **provisional**: granted but not yet confirmed (VI).
- **tag**, **facet**, **branch**, **cascade**, **most-specific-wins** (00.5).
- **evidence** / **tag_event**: what an act counts toward / the record of it. **tally**: sealed
  weighted totals. **counted evidence**: fired automatically by hooks. **judged evidence**: recorded by
  the DM's significance judgment.

**Harm and resources**
- **Vitality**: the harm pool. **Staggered**: Vitality 0. **wound**: lasting harm taken while
  Staggered (not "injury" in rules text). **Dying** (with steps) / **dead**: ch.07's harm states.
  **bloodied**: Vitality at or below half (a shown descriptor).
- **Focus**: the one active-ability pool. *Distinguish* **implement** (the item a caster channels arcane or holy power through;
  tag `item.tool.implement`).
- **fate**: the single meta-currency.
- **severity**: S1 Light, S2 Moderate, S3 Heavy, S4 Grievous, S5 Catastrophic. **U(severity)**: its
  unit magnitude.
- **condition**: a status instance per 00.9. **affliction**: a staged condition sequence (07).
  **mark**: a permanent change from the brink (07).
- **standing**: the −3…+3 relationship scale.

**Time and world**
- **action**, **turn** (an actor's portion of a round), **round**, **interval** (10 minutes), **hour**,
  **watch**, **day**, **week**, **season**, **year**; **time mode**; **boundary** (time or event);
  **handler**; **phase**; **interrupt**.
- **scene**: a continuous situation with one focus. **conflict**: a scene in round-by-round mode.
  **encounter**: a meeting with an entity or group, which may or may not become a conflict.
  **venture**: from leaving safety to returning. **session**: a real-world sitting.
- **reflection**: the growth boundary (00.7.2).
- **clock**, **segment**, **tick**, **omen** (with stages stirring / building / imminent), **racing**,
  **tug**.
- **World Turn** / **Season Turn**: 11's weekly and seasonal world processes.
- **thread**: an entry in the quest register. **rumor**: a heard claim with a sealed truth value.
  **chronicle**: the append-only world history.
- **fact**, **entity**, **sealed**, **gate** (of sealed state), **permitted slice**, **tell**,
  **write-on-mention**.

**Composition and generation**
- **effect**, **operation**, **hook**, **regime** (additive / independent trigger / priority-exclusive /
  named composite), **evaluation pass** (E0–E7), **modifier family**, **stacking family**, **depth**,
  **composite**.
- **generator** (gate→fill), **domain**, **source**, **circumstance**, **quality rung**, **signature
  slot** / **magnitude slot**, **fill method** (signature / biased / chosen / weighted / recipe),
  **mod group**, **Greater** / **Flawed**, **tier cap**.

**Added at integration** (orchestrator-approved amendments; each term's owning rule in parentheses; the owning
chapter's rule is canonical) [amended: IR ch.02, 03, 04, 05, 06, 07, 08, 10, 11, 12, 16]

*Character and creation (02)*
- **origin**: one of three parts a character is assembled from: a **people** (birth: attribute rule, an innate
  gift, tongues), an **upbringing** (where they grew: base Focus, letters, access licenses, purse) and a
  **livelihood** (what they did: the training list, kit and hooks) (02.1; `data/origins.yaml`). Say
  *livelihood*, never "trade" or "background" (DL-02-23).
- **Typical rule** / **Free rule**: a people's attribute rule, +7 with three placements set by the people / +5
  in any shape and placement (02.3; DL-02-04). **shape**: the attribute array chosen (02.3.1). **uncommon of
  your kind**: a character of a non-human people who takes the Free rule (02.3.4).
- **breadth profile**: how many trainings a character takes against how many are **held deep** (with
  competence) or **held as access** (license only) (02.5.2).
- **knack** (birth): +1 edge under one level-2 deed tag, a `gen.birth` magnitude draw (02.6.1); *distinguish*
  a companion's **knack** (`kn.*`, 16.4.7). **quirk**: the birth layer's small permanent oddity (never
  "trait", a tag facet). **gift** (birth): a people's innate `fact` license (02.4.2). **the Bent**: the one
  deferred birth reroll, an offered +1 to an attribute (02.6.5–02.6.7; P1). **manner** (of childhood): the
  classified circumstance of a birth draw (02.6.4).
- **creation window** / **second look** / **lock**: open from the end of creation to the first `reflection`;
  one revision of choices within the origins while it is open; the fact `pc.creation.locked` that ends it
  (02.2.6).
- **drive**: the character's want (finishable: a **long vow**, a vow thread for 11) or **creed** (only kept or
  broken; a conduct label for 12's rotation, never evidence) (02.9.1). **bond**: a person who matters from
  the first minute, with a SET standing: **anchor** (holds them to the world) or **thorn** (unresolved)
  (02.9.2). **aspiration**: `{text, tags}`, at most three; never weights evidence (02.9.3). **the one true
  thing**: one statement true of this character alone, checked so that it is never read as a license
  (02.9.4). **faction tie**: an `org.*` kind mapped to a faction with a status (02.9.5). **hook** (creation):
  a `CreationHook` seed handed to 11 (02.9.7). **open slot**: a tie left unfilled, filled later out of fiction
  (02.9.8). **prologue**: chronicle lines written at creation (11.12.2). **tongue** / **letters**: a spoken
  language license / `lic.lang.letters`, reading and writing (02.4.6).

*Evidence (03)*
- **quality**: routine / difficult / challenging, how hard a deed was for its actor (03.4). **settlement**: the
  scene-end pass that applies saturation, caps and cascade to the scene's pending evidence (03.5, PR-03-2).
  **evidence-bearing scene**: a scene-day in which the actor received at least one settled judged deed (03.6). **ground**: the state write or
  frame element a judged element must cite (03.1.6). **carrier**: a witness who can spread a deed (03.10.2).
  **strain**: unatoned contrary conduct on an axis (03.8); *distinguish* **dread** (07) and the harm tag
  `harm.mind.strain`. **deed line**: the neutral one-line record of a deed in the ledger (03.2.4).

*Recognition (04)*
- **seat**: one of the places a held calling occupies, three deed and one oath (04.8.1). **pick** / **pick
  allowance**: a tier's right to fill one calling slot from 05's pool (`gen.pick`) / the cumulative count of
  them (04.8.4). **legacy pick**: a pick kept through a consolidation beyond the new tier's allowance
  (04.8.5). **lineage**: callings whose keys lie on one line of the tag tree (04.8.3). **road**: a hybrid's
  level-2 key in each branch (04.5.2). **specialty**: a frozen competence entry kept from a consolidated or
  forked calling `{tag, value, grade, tier_reached}` (04.8.5). **variant**: a calling sharing a level-2
  calling's key with one added requirement (04.2.6).
- **keeper**: the bonded witness of an oath, with its axes and forbidden acts (04.9.2; a region's `keeper.*`, written by the world seed 12.16.6 or a pre-made setting [revision: I-028]).
  **shadow**: the dark reading every calling carries (04.9.1). **Fraying**: the shadow's stages, **Dimmed**
  (1), **Fraying** (2), **the Choice** (3) (04.9.2). **turn**: taking the shadow at the Choice (04.9.5).
- **lapse** / **fork** / **fold** / **consolidation**: the four structural retirements: a provisional grant
  ends; a calling is replaced inside its lineage; a calling folds into the base as training and a +2
  specialty; several callings become one (04.8.2–04.8.6).
- **readiness band**: unformed / leaning / becoming / on the threshold / ready (04.6.5). **Leanings**: the
  `available` codex view naming key tags with their band word, never a number (04.6.5). **confirmation**:
  one of the five tests K1–K5 whose count is **confidence** (04.4.2).
- **the Taking**: the gated monster-power trait (`lic.call.taking`, 04.10.2). **library**: the powers a
  Devourer has taken (04.10.4). **bane**: a standing weakness a V13 recognition carries (04.7.5).

*Abilities, Focus and magic (05)*
- **hold**: have an ability in a slot. **partition**: calling / acquired / equipped (05.2). **shelf**: known,
  unslotted acquired abilities (05.2.6). **promotion**: an acquired or shelved ability taken by a pick
  (05.8.6). **form**: an ability that replaces how something works (`claim_slot`; 05.3.2); *distinguish*
  `slot.body_form`. **timing**: when an activation may be used (beat, rider, reaction, trigger; 05.4.1).
- **working**: an activation that is itself the beat; **rider**: one that attaches to the character's own
  beat (05.1.3). **flare**: one optional surcharge on an activation (05.6.8). **push**: spending Focus on an
  ordinary beat (05.6.7); **grit**: the push declared to ignore wound penalties for a beat (07.2.5).
  **Spent**: at 0 Focus. **overdraw**: paying Focus with Vitality (05.6). **reserve** / **vessel**: banked
  Focus and the implement that holds it (05.6.12).
- **regard**: a divine caster's standing with a keeper (05.7.2). **miscast**: magic going wrong in its
  branch's way, **Backlash** (arcane), **Silence** (divine), **Debt** (primal) (05.7.5). **small working**:
  a minor magical use under a training license on Handle's card (05.7.6). **rite**: a ritual (`rit.*`), a
  clocked magical extended task; its **strain clock** races its progress (05.8.4).
- **spread tag**: one of the ordered multi-target shapes (pierce, burst, fork, chain, linger; cone for
  adversaries) (05.4.4; 06.8). **effect unit** / **allowance**: the budget measure of an ability's effects /
  what its tier and prices allow (05.11.1). **training grade**: trained < expert < master; each grade's
  **technique cap** is the highest `min_tier` it can emulate or learn (05.5.4).

*Conflict (06)*
- **Guard**: the Agility defense against aimed physical attacks (06.4.1). **tempo** / **tempo DC**: who acts
  first, by a Wits check against each adversary's static `10 + Wits + competence` (06.2.2). **engagement
  link**: the bond between two engaged participants (06.3.5). **group**: a named spot or formation label
  (06.3.1). **feature**: a scene element anyone could use, hide behind or fall off (06.3.8). **size step**:
  one rung of size (06.3.10). **pace**: bands per move action, the quantity `speed` (06.3.3).
- **weight**: a weapon's one weight, fixing severity, action cost, hands and bands (06.4.4). **mastery**: a
  Strike's base severity +1 rung at expert, +2 at master (06.4.5). **harm mode**: lethal or nonlethal,
  declared with the attack (06.4.8). **called shot**: an engine −2 snag for one effect from a closed list
  (06.4.10). **shape**: an effect's selection rule over bands and links (06.8).
- **heavy blow**: an adversary attack at S4+ or with a shape; it needs a **windup**, a visible action on an
  earlier turn (06.9.5). **attention**: the fixed rule by which adversaries choose targets (06.9).
- **mob**: a group fighting as one entity with pooled Vitality; **swarm**: a mob of tiny creatures (06.10).
  **nerve**: a side's morale clock size; **morale clock**: the clock whose completion **breaks** a side
  (06.11).
- **Defend** / **Fend**: engine snags on an attacker (an action / a reaction) (06.1.5, 06.6). **Withdraw**,
  **Flank**, **Aim**, **Command**: named actions (T-06-1). **standing order**: one of five lasting companion
  orders (06.14.4). **chase round** and its **ground** (the round's obstacle) (06.12.3). **objective**: what
  a side fights for (06.13.2).

*Harm (07)*
- **wound load**: the sum of U(severity) over harm taken while Staggered since it was last cleared; at 3 the
  character falls (07.2.6). **brink**: the number of unhealed brink wounds (`inj.the_brink`), the memory of
  recent falls; the next fall enters Dying at 1 + brink (07.2.8). **Down**: out of the scene, alive, after a fall
  under a non-lethal frame (07.2.9). **Threshold**: the step past Dying 3, where the player chooses from the
  last-chance menu (07.5.1). **stabilized**: `dying_step` 0 (07.2.8).
- **lethal frame** / **lethal context**: a frame whose `lethal` flag is true / the recorded warning that makes
  one legal (07.3). **scar**, **brink mark**, **maim**, **haunt**: the kinds of mark (07.7, 07.11).
- **dread**: mental strain, a shown track against a threshold of 8 + Resolve (07.11); **shaken**: dread at or
  above half its threshold (07.11.3). **rest site**: haven / camp / rough (07.8.2). **treated**: a wound covered that
  day by a Treat that delivered reach (`treated_today`, 07.8.8).

*Items (08)*
- **quality ladder**: worn, common, fine, masterwork, wondrous, storied, with a **quality index** 1–6 (08.1.4).
  **item share**: the part of a capped family items may fill (08.2.2; 00.10.6). **attunement** (**attuned**):
  binding an item to its bearer, at most five (08.5.2). **relic**: an item holding a bound power or license
  property; licenses off-identity capability at a surcharge and feeds no evidence (08.4.4). **bound power**:
  an item-bound active ability (08.4). **worked property**: the one property added after making (08.6.10).
  **residuum**: the essence (`mat.residuum`) salvaged from an item's signature (08.6.8). **recipe**: a known fill for one craft slot
  (08.6.9). **provenance**: where an item came from (08.6.2). **trophy base**: the base a creature's drop is
  made on (08.3). **drop check**: whether a defeat drops a property item; **yield**: an archetype's drop kind
  (none / trophy / hoard / always) (08.3.3).
- **notch**: the step by which prices move (08.8.2). **lot**: the unit of cheap goods sold per coin (08.8.1).
  **load unit**: the unit of carried weight (08.9). **burdened** / **overloaded**: load above capacity /
  twice capacity (08.9.2). **Unit of wealth**: this character's weekly lifestyle cost (08.8.6). **find a
  buyer**: the clock by which property items sell (`clk.find_buyer`); **market depth**: a settlement's weekly
  limit; **glut**: the fall in price of repeated sales (08.8.9).

*Exploration (10)*
- **home band**: the band of a region's dangers (10.1.1). **danger rating**: safe / settled / wild / perilous /
  deadly, how often dangers come (10.9.2). **time-tick check**: the one d12 per watch or site check; each
  **face** means something, a **lull** included (10.9.1). **pending threat**: a sealed hostile encounter that
  shows an omen first (the **omen-first rule**) (10.9.5).
- **leg**: one stretch of a journey plan, needing 6 × watches **progress points** (10.3.1–10.3.2). **march
  unit** / **march allowance**: a watch's march cost / two units a day; past it, a **forced march** (10.3.5).
  **journey role**: navigator, lookout, scout, forager or quartermaster, a per-watch fact (10.5.1; 16.8.3).
  **way-finding**: the navigation beat; failing it puts the party **off course** by **the veer**, sealed
  (10.4). **telltale**: the perceivable sign of a sealed trap or hazard (10.14.2). **haven**: a place with
  `safe: true` (10.2.3).
- **site**: a place explored area by area; its **theme** (what happened to it) and **domain** (what kind of
  place it is) (10.13.1–10.13.2); an **area** is one step of it; **the heart** is the area generated when
  progress completes (10.13.10); a **roused** site checks every interval (10.9.3); a **secured** area makes a
  camp (10.13.11).

*DM procedures and the living world (12, 11)*
- NPC **depth**: **walk-on** / **recurring** / **principal** (12.11.1); never "minor" or "major". Factions are
  **full** or **petty** (11.3). Out-of-fiction labels are 12.15's list.

*Companions (16)*
- **ally**: anyone of T-16-1, an entity of kind `companion` with an `ally_kind` (16.1). **retinue**: the allies
  who follow the PC; each takes a **retinue place** under the cap clamp(2 + Presence, 1, 6) (16.2.1). **own
  band** / **serving band** / **band cap**: what an ally is / how well it fights beside this PC /
  `max(1, power_band − 1)` (16.2.4). **escort**: travelling with someone who will not follow (16.2.4).
  **posted**: left at a holding on purpose (16.2.3). **cohort**: three to six members who fight as one
  (16.2.6). **scene ally**: one who fights beside the PC for a scene without joining (16.1).
- **loyalty**: an ally's standing toward the PC (16.5.1). **regard** / **grievance**: sensed clocks whose
  completion moves loyalty a step (16.5.3). **confrontation**: the scene a completed grievance forces;
  **amends**: the beat that may restore the step (16.5.9). **counsel**: an ally's warning before a resented
  deed (16.5.7). **departure clock**: the public clock before an ally leaves (16.6.2). **drives**: two
  values, a want and a refusal (16.5.5). **joining**: why an ally follows (16.3). **held line**: an ally or
  group holding foes off as a tug clock (16.7.12). **protégé**: an ally who grows a calling, to tier 3
  (16.10.4). **knack** (companion): one of fifteen closed capabilities (16.4.7).

**00.18.1 Banned words.** `[D]` T-00-22 lists terms that may not appear in rules text or data (they
imply mechanics this game does not have, or collide with a canonical term): *level* (of a character),
*class* (use calling), *XP*, *HP / hit points* (Vitality), *mana, stamina* (Focus), *saving throw*
(Endure/Evade check), *skill check* (check), *advantage / disadvantage* (lever / snag), *injury /
injured / hurt* in rules (wound, harm), *minor / major / severe* as severity names, *exploration turn*
(interval), *the System*, *focus* for an item (implement), *gate* alone for the generator (pool gate).

### 00.19 The standard chapter format

`[N]` Every rules chapter (01–16) uses this format, restating BRIEF §10 with this chapter's additions:

```
# NN — Title
> One-paragraph summary of what this chapter governs and why it's shaped this way.

## Design intent            (goals/principles served; what it deliberately avoids)
## Rules                    (numbered NN.S.R; each rule in the 00.2.5 template; one kind per
                            decision from 00.2.2; every [J:*] with a Worst case line; cited)
## Procedures               (step-by-step algorithms, PR-NN-*)
## Tables                   (T-NN-*, with pointers to data/*.yaml, which is canonical)
## Worked examples          (WE-NN-*: end to end with numbers; boundary pairs + a non-example;
                            reuse the continuous character Wren where natural)
## Edge cases & adaptation anchors  (how to reach-and-adapt; list every Anchor: yes rule with knobs)
## State touched            (every state family read/written using 00.6 names; tools used (00.14);
                            hooks subscribed (00.10.2); boundary handlers registered (00.7.4);
                            clocks created (00.8); runtime capabilities assumed (00.14.1))
## Interface requests       (needs from / offers to other chapters, by 00.17 contract names;
                            new tags, effects, hooks or ids proposed)
## Open empirical questions (each with a named test; the rule still ships a concrete default)
```

---

## Procedures

**PR-00-1 Assembling a check.** `[D]` (called inside `frame_check`)
1. Read the frame's attribute and look up the actor's modifier (00.4). Reject if the attribute is not
   allowed for the beat's verb or license (T-00-11 / license `attribute`).
2. Competence: collect the actor's competence entries whose tag equals the primary deed tag or is an
   ancestor of it; take the highest (00.3.6). A PC always has at least the floor at `deed`.
3. Edge: sum the `modify` effects of family `edge` whose `applies_when` holds for this beat; cap +2.
4. Circumstance: validate each lever and snag (fact exists, established before the declaration, one
   lever per fact, at most two of each); sum Precision ±2 values; cap ±4. Apply Protective and
   Amplifying shifts to stakes and reach, clamped.
5. Status: from the actor's active conditions, take the worst penalty (cap −4) and the best bonus
   (cap +2).
6. Total = sum, clamped −8…+16 (and base ≤ +12 for a PC, +14 for others).
7. DC: first match of stored DC → opposed defense (run steps 1–5 for the defender without step 4,
   plus 10) → effect DC → tier number (then store it on the obstacle).
8. Odds: enumerate the 20 faces with ch.01's degree rule; store success-or-better, critical success,
   critical failure and near-miss percentages for the OFFER. If only a natural 20 can succeed, the
   OFFER must say "only a natural 20, and at best a plain success".
9. Write the breakdown to the frame.

**PR-00-2 Advancing time and processing boundaries.** `[D]` (`advance_time`, `mark_boundary`)
1. Compute every boundary between now and the target (or until the named event), in chronological
   order; at equal instants, order per 00.7.6.
2. For each boundary: run phases 1–9 (00.7.5); in each phase run the registered handlers in registry
   order; the generic handler `h.00.clock_auto` runs every clock's `auto_ticks` and `decay` rows for
   this boundary in phase 5.
3. If a handler raises an interrupt, finish the current boundary's remaining phases, set the game
   clock to this instant, and return `{halted_at, remainder, interrupt}`.
4. Otherwise set the game clock to the target and return the list of boundaries and handler results.
5. Every omen, rumor and trace a handler emitted is returned for narration; the DM narrates the passage
   of time from this list and adds nothing that is not in it (INV-2).

**PR-00-3 Ticking a clock.** `[D]` (`tick_clock`)
1. Validate the source against the clock's `tick_sources` (or the calling handler's `auto_ticks`);
   compute the amount (delivered reach, U(severity), or the listed number). Refuse a source the clock
   does not list.
2. Apply (clamped 0…segments; `fill` clocks never go down); append to history.
3. If the clock is sensed or hidden: compute the stage (stirring < half ≤ building; imminent when
   remaining ≤ max(1, segments ÷ 4)); pick the next unused omen of that stage; return it. If the stage
   is imminent and `on_complete` would expose the PC to lethal harm, raise ch.07's lethal-warning `[T]`.
4. If filled = segments: set `completed`; void any racing clock; run `on_complete.effects` as a depth-0
   process; run `links`; if `interrupting`, raise an interrupt; apply `then`.

**PR-00-4 Gate→fill.** `[D]` (`generate`; see 00.11.3)
1. Validate domain, source, circumstance (enum of the domain) and that `degree` belongs to a resolved
   frame (or is `none` where the domain allows it).
2. Pool gate: filter by `gate_tags` (ancestor match), drop `excluded_tags`, `base_kinds` mismatches and
   flagged uses. Log the pool size.
3. Tier gate: drop entries whose minimum tier exceeds `tier_cap` (source band).
4. Look up the quality rung from `(circumstance, degree)`; read signature and magnitude slot counts;
   read the fill method.
5. Apply degree effects (Greater / Flawed) as instructions for steps 6–8.
6. Fill the signature slot (method `signature`: the source's signature entry; if it was gated out, the
   slot is filled by weighted draw among entries marked `signature_eligible`), then each magnitude
   slot: compute weights (base weight; ×3 for the bias tag under `biased`; ×½ for recency), draw with
   RC-RNG, or present up to three for `chosen`, or take the recipe's entries. After each pick remove
   its `mod_group` and held uniques.
7. Set each property's tier (default: `tier_cap` for signature, `tier_cap − 1` minimum 1 for
   magnitude, unless the domain table sets otherwise; +1 for Greater).
8. Check slot and budget caps; refill once on violation; else leave empty.
9. Write the object; return it with the log.

**PR-00-5 Applying a condition.** `[D]` (`apply_condition`)
1. If any active condition `neutralizes` the new one, or the new one neutralizes an active one: remove
   the neutralized instance(s); if the new one was neutralized, stop.
2. Diminishing: count applications of this condition to this target inside the window; if ≥
   `immune_after`, fail; if ≥ `halve_after`, halve the duration (round down, minimum 1 unit).
3. If the target already has it, apply the stacking rule (00.9.2); else create an instance.
4. Resolve the exclusion group: only the highest `priority_rank` instance is active.
5. Run `on_apply` effects and fire `on_condition_applied` (subject to depth).
6. If `visible`, the narration must name it this turn.

**PR-00-6 Resolving an event through the substrate.** `[D]` (inside `apply_effect`, `apply_harm`,
`use_ability`, and the pipeline)
1. Create the event with its depth (00.10.8).
2. If depth = 0, collect hook subscribers for the event: target's prevent/redirect, then actor's, then
   others', each group by rank then acquisition time; resolve each fully in turn; stop if the event is
   prevented. Effects they cause are depth 1 and fire no subscribers.
3. Evaluate every quantity the event needs through the pass (E0–E7).
4. Apply state writes; run core `[T]` rules (Vitality thresholds, harm states, clock completion).
5. Return the results and every narration obligation (visible conditions, omens, band changes).

**PR-00-7 Write-on-mention.** `[J:flag]` + `[D]`
1. Draft the narration. List every concrete, addressable element it introduces.
2. For each, apply the 00.6.6 test; for each true, `create_entity` or `set_fact` with the properties
   the narration implies.
3. If the narration needs a property that is unestablished (is the door locked?), ask the Oracle first
   and narrate the answer.
4. Only then deliver the narration. The claim-vs-state check (ch.12) compares it with the store.

**PR-00-8 Authoring an extension (tag, effect, hook, id).** `[D]`
1. Search: does an existing tag, effect with parameters, or hook already express it? If yes, use it.
2. If not, and it is level 3+ tag / a new effect in your owner-block / a new id with your prefix: add
   it with a definition, a distinguishing test, `lifecycle: provisional`, and a DL entry.
3. If it is a facet, branch, level-2 tag, hook, operation, family, regime, behavioral slot, severity
   rung or time unit: file an Interface request to 00; do not use it until the orchestrator amends 00.

---

## Tables

Tables embedded in Rules are canonical and indexed here: **T-00-2** rule kinds (00.2.2); **T-00-3**
severity (00.3.11), stakes (00.3.14), reach (00.3.15), standing and other scales (00.3.16); **T-00-8**
time ladder (00.7.1) and event boundaries (00.7.2); **T-00-10** phases (00.7.5); **T-00-12** gate
classes (00.12.3); **T-00-16** hooks (00.10.2); **T-00-17** evaluation pass (00.10.4) and modifier
families (00.10.6); **T-00-18** tools (00.14.2); **T-00-21** contracts (00.17). The tables below are
defined here.

**T-00-1 Invariants.** `[D]` Engine-enforced everywhere. A chapter rule that would violate one is void.

| Id | Invariant |
|---|---|
| INV-1 | No state changes without a tool write. |
| INV-2 | Narration never contradicts state; state wins; narration restates only what the store holds after this turn's writes. |
| INV-3 | The DM never supplies a number other than a quantity the player stated; tools compute DCs, modifiers, harm, ticks, odds, prices, durations. |
| INV-4 | All randomness is engine-rolled and logged. |
| INV-5 | No roll without a committed frame with declared stakes. |
| INV-6 | No death without a lethal frame (Key 1) and ch.07's Key 2. |
| INV-7 | Rolls never grant licenses. |
| INV-8 | Licenses are read literally at their grade. |
| INV-9 | Player text is intent and method; assertions never become facts. |
| INV-10 | Sealed state never enters narrator context until unsealed. |
| INV-11 | No effect grants additional actions per turn (P9). |
| INV-12 | Triggered effects do not trigger (depth rule). |
| INV-13 | At most one instance of any license id, and one active instance of any effect id per family, per entity. |
| INV-14 | Every tick of a sensed or hidden clock renders one omen of its stage. |
| INV-15 | Every boundary crossed runs its registered handlers; time never skips silently. |
| INV-16 | Every addressable element has an id from its first mention. |
| INV-17 | Integers only; no percentage modifiers; round down only at E7. |
| INV-18 | Caps: check total −8…+16; PC base ≤ +12 (others ≤ +14); edge +2; circumstance ±4; status −4/+2; attributes per 00.4.3; Vitality ≤ 24 (PC); Focus ≤ 12; activation cost ≤ 6. |
| INV-19 | The ruling ledger is consulted before any adaptation, Oracle call, Good Idea, G3 or G4 decision. |
| INV-20 | Every `[J]` decision in a frame cites the fact ids it rests on. |

**T-00-4 Caps and envelopes (summary).** `[D]` All in `data/scales.yaml`.

| Quantity | Envelope / cap | Final numbers owned by |
|---|---|---|
| Attribute modifier (PC) | −1…+3 at creation, sum +5…+7; lifetime −2…+4; sum after creation ≤ +8 (≤ +9 with the tier-4 increase) | 02 (method, the Bent), 04 (the one +1), 07 (maims) |
| Attribute modifier (others) | −5…+10 | 09, 16 |
| Competence | 0…+6; PC floor +1 at `deed` (02 may set 0…+2) | 02, 04, 05 |
| Edge (checks/defenses; harm) | +2; +2 | 05, 08 |
| Circumstance | ±4 (≤ 2 levers, ≤ 2 snags) | 01 |
| Status | −4 worst / +2 best | 06 |
| Base modifier | PC ≤ +12; others ≤ +14 | — |
| Check total | −8…+16 | — |
| DC rungs | reference 10/15/20/25/30, each ±2 under CT-1…6 | 01 |
| Vitality | PC 10–16 at creation (12 + Endurance), + 2 per power band above 1, ≤ 24 [amended: DL-00-04]; adversaries per band 00.3.7 (standard line T-09-3: 5/12/18/24/36) | 02, 07, 09 |
| Harm per severity | 1 / 3 / 5 / 8 / 12 | fixed (00) |
| Harm reduction | 0…4 total | 07, 08 |
| Focus | 3–5 at creation, ≤ 12; activation 0–4 base, ≤ 6 | 05 |
| Fate | 0…3 | 01 |
| Ability slots | total 12–24 across calling / acquired / equipped | 05 |
| Clock sizes | 4 / 6 / 8 / 12 | fixed (00) |
| Tiers | a stated maximum; competence at the top ≤ +6 | 04 |

**T-00-5 Obstacle tiers.** `[J:rung]` Anchors are stated by who could do it [R7 §4.2; PF2e simple DCs,
R: https://2e.aonprd.com/Rules.aspx?ID=2628]. Numbers: ch.01 (reference in brackets).

| Tier | Anchor: who could do it | Typical example | Boundary example |
|---|---|---|---|
| Trivial (no roll) | anyone, in these conditions | open an unlocked door | climb a knotted rope with no one watching and nothing at stake |
| Easy [10] | an untrained adult, taking care, usually succeeds | climb a rough stone wall | calm a nervous but familiar horse |
| Moderate [15] | needs competence; the untrained often fail | pick out a trail on hard ground | talk a neutral guard into bending a small rule |
| Hard [20] | challenges a practiced professional | pick a guild-made lock | leap a 12-ft gap from a running start |
| Very hard [25] | experts often fail | track a ranger through rain over rock | forge a noble's seal well enough for a clerk |
| Legendary [30] | the edge of mortal ability; needs levers or licenses | hold a collapsing gate alone for a minute | talk a sworn enemy into laying down arms mid-battle |
| Beyond (G4) | no mortal without a license that changes the category | jump a 30-ft chasm unaided | persuade a river with no spirit in it |

*Worst case of a one-rung error:* DC off by one step (5 at reference), visible in the OFFER.

**T-00-6 Degree distribution (reference ladder, step rule; exhaustive d20).** Success-or-better %
(CS / S / F / CF; near-miss %). Scratchpad `odds00.py`. Near-miss counts include a natural 1 that stepped
a success down (DL-01-03); recomputed at integration, which changes the +9…+16 rows against low DCs from
0 to 5 (identical to 01's T-01-3) [amended: DL-01-03].

| Mod | DC 10 | DC 15 | DC 20 | DC 25 | DC 30 |
|---|---|---|---|---|---|
| +0 | 55 (5/50/40/5; 15) | 30 (5/25/45/25; 15) | 5 (5/0/45/50; 15) | 5 (0/5/20/75; 0) | 0 (0/0/5/95; 0) |
| +1 | 60 (10/50/35/5; 15) | 35 (5/30/45/20; 15) | 10 (5/5/45/45; 15) | 5 (0/5/25/70; 0) | 5 (0/5/0/95; 0) |
| +2 | 65 (15/50/30/5; 15) | 40 (5/35/45/15; 15) | 15 (5/10/45/40; 15) | 5 (0/5/30/65; 0) | 5 (0/5/5/90; 0) |
| +5 | 80 (30/50/15/5; 15) | 55 (5/50/40/5; 15) | 30 (5/25/45/25; 15) | 5 (5/0/45/50; 15) | 5 (0/5/20/75; 0) |
| +7 | 90 (40/50/5/5; 5) | 65 (15/50/30/5; 15) | 40 (5/35/45/15; 15) | 15 (5/10/45/40; 15) | 5 (0/5/30/65; 0) |
| +9 | 95 (50/45/5/0; 5) | 75 (25/50/20/5; 15) | 50 (5/45/45/5; 15) | 25 (5/20/45/30; 15) | 5 (0/5/40/55; 10) |
| +12 | 95 (65/30/5/0; 5) | 90 (40/50/5/5; 5) | 65 (15/50/30/5; 15) | 40 (5/35/45/15; 15) | 15 (5/10/45/40; 15) |
| +14 | 95 (75/20/5/0; 5) | 95 (50/45/5/0; 5) | 75 (25/50/20/5; 15) | 50 (5/45/45/5; 15) | 25 (5/20/45/30; 15) |
| +16 | 95 (85/10/5/0; 5) | 95 (60/35/5/0; 5) | 85 (35/50/10/5; 10) | 60 (10/50/35/5; 15) | 35 (5/30/45/20; 15) |

**T-00-7 Tag tree levels 1–2.** (Definitions, poles and tests in `data/tags.yaml`.)

| Branch | Level-2 children |
|---|---|
| deed.martial | blade, axe, bludgeon, polearm, archery, thrown, unarmed, shield, armor, tactics, mounted, athletics |
| deed.guile | stealth, thievery, deception, disguise, ambush, poisoncraft, escape, streetwise |
| deed.wilds | survival, tracking, navigation, animals, foraging, seafaring |
| deed.lore | history, languages, bestiary, medicine, engineering, law, arcana, religion, investigation |
| deed.arcane | fire, frost, storm, earth, illusion, divination, warding, mind, summoning, necromancy, alteration |
| deed.divine | healing, warding, smiting, rites, oaths, revelation, exorcism, pact |
| deed.primal | growth, beastkin, weather, shapeshifting, spirits, elements, hexcraft |
| deed.influence | persuasion, command, performance, intimidation, intrigue, trade, etiquette, insight, teaching |
| deed.craft | smithing, woodcraft, leathercraft, textiles, alchemy, cookery, building, artifice, jewelcraft, enchanting, scribing |
| conduct (signed axes, no level 2) | mercy, honesty, courage, loyalty, generosity, justice, humility, restraint, piety, protection |
| creature.beast | predator, herd, vermin, reptile, avian, aquatic, monstrous |
| creature.folk | human, elf, dwarf, halfling, orc, goblin, giant, beastfolk |
| creature.undead | mindless, ravenous, spectral, sovereign |
| creature.spirit | fey, place, ancestor, celestial |
| creature.fiend | demon, devil, possessor, hellbeast |
| creature.construct | golem, animated, clockwork, homunculus |
| creature.elemental | fire, earth, water, air, frost |
| creature.dragon | great, drake, wyvern, serpentine |
| creature.horror | aberration, ooze, fungal, plant, abomination |
| harm.physical / fire / frost / storm | cut, pierce, crush, asphyxia / flame, heat / cold, ice / lightning, thunder |
| harm.corrosion / venom / blight | acid, rust / poison, gas / necrotic, disease, decay |
| harm.radiance / mind / arcane | holy, light / psychic, strain / force, raw |
| material.* | metal: iron, steel, silver, gold, copper, rare · wood: timber, fine, witchwood · stone: common, fine, volcanic · hide: leather, fur, scale, chitin · fiber: cloth, silk, cordage · bone: bone, horn, ivory, fang · gem: precious, semiprecious, crystal · botanical: herb, fungus, resin · essence: blood, gland, heart, ichor, residue |
| item.* | weapon: blade, axe, bludgeon, polearm, bow, crossbow, thrown, ammunition · armor: light, medium, heavy · shield: light, heavy · garment: clothing, cloak, footwear, gloves, headwear · jewelry: ring, amulet, charm, circlet · tool: kit, instrument, implement, trade, light, container · consumable: potion, food, scroll, oil, remedy · goods: trade, treasure, document · conveyance: mount, vehicle, vessel |
| terrain.* | settlement: city, town, village, hold, camp · road: highway, track, bridge, causeway [amended: DL-INT-02] · forest: woodland, deepwood, jungle · highland: hills, mountains, cliffs · plains: grassland, farmland, moor · wetland: marsh, swamp, fen · arid: desert, badlands · frozen: tundra, glacier, snowfield · water: river, lake, coast, sea · underground: cave, mine, tunnel, sewer · ruin: dungeon, tomb, temple, fortress |
| situation.* | conflict: melee, ranged, chase, skirmish, duel · social: parley, interrogation, performance, court, bargaining · investigation: search, research, inquiry, surveillance · exploration: dungeon, ruin, cave, wilderness, settlement · travel: overland, water, underground · downtime: recovery, project, training, commerce, carousing · rest: camp, sanctuary |
| trait.* | action: attack, manipulate, move, concentrate, speech · sense: visible, audible, loud, scent · delivery: touch, melee, ranged, area, aura, line · nature: magical, sacred, profane, mental, illusion · duration: instant, sustained, lasting, permanent |
| org.* | crown: royal, noble, civic, military · faith: temple, shrine, mission · order: knightly, monastic, arcane, druidic, hunters · guild: craft, merchant, scholarly · company: mercenary, trading, exploring · clan: family, tribe, lineage · outlaw: thieves, bandits, smugglers, assassins · cult: fiendish, undeath, forbidden, doomsday |

**T-00-9 Boundary registry.** `[D]` Generated at integration from `data/boundaries.yaml`, which is canonical
(105 handlers; the reserved rows 00 seeded plus every chapter's owner-block) [amended: IR ch.03 #7, ch.04 #6,
ch.05 #1, ch.06, ch.07 #4, ch.10 #2, ch.15 #7, ch.16 #3]. Each owner defines the behavior in its chapter (rule ids
in the data file). Phase numbers per 00.7.5; within a phase, registry order (owner, then id) unless a `before`
is declared. A handler on several boundaries appears in each row.

| Boundary | Handlers (phase) |
|---|---|
| every boundary | `h.00.durations` (1); `h.08.durations` (1); `h.00.clock_auto` (5) |
| `beat_end` | `h.04.crisis_check` (8); `h.01.ruling_log` (9); `h.10.site_time` (9); `h.12.inconclusive_streak` (9) |
| `turn_start` | `h.06.turn_effects` (2) |
| `turn_end` | `h.06.turn_effects` (2); `h.07.dying_check` (2) |
| `conflict_start` | `h.07.lethal_scan` (7); `h.06.tempo_setup` (9); `h.12.intensity` (9); `h.16.conflict_orders` (9) |
| `conflict_end` | `h.06.clear_conflict_state` (1); `h.05.conflict_recharge` (3); `h.07.after_conflict` (3); `h.12.intensity` (9) |
| `scene_start` | `h.07.lethal_scan` (7); `h.10.scene_frame` (7); `h.12.pacing_push` (7); `h.12.scene_test` (7); `h.04.fraying_check` (8) |
| `scene_end` | `h.01.scene_cleanup` (1); `h.07.load_clear` (1); `h.05.scene_recharge` (3); `h.11.fallback_counters` (6); `h.15.placement_audit` (6); `h.12.lead_audit` (7); `h.07.career_end` (8); `h.03.antigrind_reset` (9); `h.12.bookkeeping` (9); `h.12.intensity_scene` (9); `h.12.npc_memory` (9); `h.12.rotation_update` (9); `h.12.tension_update` (9); `h.15.patience_reset` (9); `h.16.loyalty_record` (9) |
| `breather` | `h.05.focus_recover` (3); `h.07.rest_recovery` (3, before `h.05.focus_recover`, `h.05.rest_recharge`) |
| `rest_short` | `h.05.focus_recover` (3); `h.05.rest_recharge` (3); `h.07.rest_recovery` (3, before `h.05.focus_recover`, `h.05.rest_recharge`) |
| `rest_long` | `h.05.focus_recover` (3); `h.05.reserve` (3); `h.05.reslot` (3); `h.05.rest_recharge` (3); `h.07.rest_recovery` (3, before `h.05.focus_recover`, `h.05.rest_recharge`); `h.00.reflection` (8) |
| `reflection` | `h.02.bent_offer` (8); `h.03.recency_update` (8); `h.04.provisional_check` (8); `h.04.recognition_pass` (8); `h.04.standing_offers` (8); `h.05.provisional_abilities` (8); `h.16.follower_offers` (8); `h.02.creation_lock` (9); `h.02.open_slots` (9); `h.07.vitality_max` (9) |
| `venture_start` | `h.10.venture` (9) |
| `venture_end` | `h.11.reckoning` (6); `h.10.venture` (9); `h.12.venture_bookkeeping` (9); `h.16.venture_end` (9) |
| `session_start` | `h.12.session_open` (9) |
| `session_end` | `h.12.session_close` (9) |
| `mode_change` | `h.10.scene_frame` (7); `h.12.mode_change` (9) |
| `round` | `h.06.ongoing_harm` (2); `h.07.dying_check` (2); `h.05.round_recharge` (3); `h.06.chase_round` (5); `h.16.held_line` (7); `h.06.diminishing_window` (9); `h.06.objective_check` (9) |
| `interval` | `h.07.affliction_onset` (2); `h.10.site_exposure` (2); `h.10.light` (4); `h.10.site_check` (7) |
| `hour` | `h.15.alertness_decay` (5) |
| `watch` | `h.10.watch_exposure` (2); `h.07.fatigue` (4); `h.10.travel_progress` (4); `h.10.wayfinding` (4); `h.10.watch_check` (7) |
| `day` | `h.07.affliction_day` (2); `h.05.day_recharge` (3); `h.07.natural_recovery` (3); `h.10.supply` (4); `h.10.site_recovery` (6); `h.11.festival` (6); `h.11.situation_timelines` (6); `h.15.commitments_due` (6); `h.15.downtime_day` (6); `h.16.contract_term` (6); `h.10.weather` (7); `h.03.day_settle` (9); `h.10.day_reset` (9); `h.11.moon` (9) |
| `week` | `h.07.curse_cycle` (2); `h.08.upkeep` (4); `h.16.retinue_upkeep` (4); `h.08.craft_decay` (5); `h.08.markets` (6); `h.10.site_regrowth` (6); `h.11.world_turn` (6); `h.15.downtime_week` (6); `h.15.member_standing` (6); `h.00.reflection_if_downtime` (8); `h.11.world_record` (9); `h.15.standing_week` (9) |
| `season` | `h.10.weather_regime` (6); `h.11.season_turn` (6); `h.00.reflection` (8); `h.04.season_consolidation` (8); `h.05.provisional_abilities` (8); `h.16.season_growth` (8); `h.07.vitality_max` (9) |
| `year` | `h.11.year_turn` (6) |

**T-00-11 Basic verbs.** `[J:enum]` (full coverage and exclusions in `data/basic_verbs.yaml`)

| Verb | Covers | Default attribute | Other attributes by method | Licensed neighbors (excluded) |
|---|---|---|---|---|
| move | reposition, dash, withdraw, slip through a crowd, travel on foot | Agility | Might (force a way through), Endurance (long haul) | flying, teleporting |
| observe | search, study, listen, track by sight, read a person or scene | Wits | Intellect (sustained study of a thing) | reading an unknown script, magical sight |
| recall | common knowledge of one's origin, culture and trade | Intellect | — | specialist lore (licensed by training) |
| talk | inform, persuade, deceive, intimidate, bargain, taunt, perform, yield | Presence | Intellect (reasoned argument), Might (physical menace) | speaking a language not held (fallback: gesture) |
| strike | hit with body, weapon or improvised object; shoot; throw | Might | Agility (finesse, aimed, thrown) | weapon techniques |
| grapple | seize, hold, pin, restrain, snatch a held item, mount a large creature | Might | Agility (slip a hold) | — |
| force | shove, trip, topple, break, burst, pry | Might | — | lockpicking (licensed) |
| exert | climb, jump, swim, lift, balance, run far | Might | Agility (balance, precise leap), Endurance (sustained) | — |
| evade | dodge, duck, take cover, get clear of a hazard | Agility | — | — |
| sneak | hide, move quietly, conceal an object, palm | Agility | Wits (blend into a crowd, pick the moment) | disguise as a specific person |
| handle | use an object as its nature suggests; crude making and repair; first aid (stabilize only); calm or lead an animal; ride | Agility | Wits (improvised use), Intellect (knowledge-driven use), Presence (animals) | surgery, smithing, lockpicking, mounted combat |
| endure | resist cold, poison, disease, fear, pain; hold breath; keep going | Endurance | Resolve (fear, pain, temptation, domination) | — |
| setup | create a lever for yourself or an ally (feint, distract, blind, prepare) | by method | any | — |
| help | give a Precision lever to another's attempt (only if the helper could attempt it alone) | by method | any | — |
| ready | hold an action for a stated trigger | none (no roll) | — | reactions beyond ch.06's |

**T-00-13 Quantities in the evaluation pass.** `check_total`, `defense`, `dc`, `effect_dc`,
`harm_dealt`, `harm_taken`, `focus_cost`, `duration`, `clock_ticks`, `reach`, `stakes`, `vitality_max`,
`focus_max`, `speed` (bands per move action, 06), `carry` (08), `price` (08), `supply_use` (10),
`travel_points` (points per travel watch, family `adjust`, envelope 2…12 the pace ladder's; 10.3.2)
[amended: DL-10-03]. New quantities: amendment to 00.

**T-00-14 Behavioral slots (priority-exclusive).** `slot.strike_delivery` (what a Strike deals and in
which harm type); `slot.spell_delivery` (how a spell projects: bolt, cone, touch, burst);
`slot.movement_mode` (walk, climb, swim, fly, burrow); `slot.defense_reaction` (the reaction used when
attacked); `slot.body_form` (one transformed shape at a time); `slot.stance` (one combat stance); and
`slot.aura` (one active aura). New slots: amendment to 00.

**T-00-15 Reserved condition ids (intent; ch.06 defines).** The last two rows were added by ch.06 [amended: IR ch.06].

| Id | Intent | Id | Intent |
|---|---|---|---|
| cond.off_balance | footing lost; snag on physical actions | cond.frightened | fear; cannot willingly approach the source |
| cond.prone | on the ground | cond.charmed | regards the source as a friend |
| cond.grabbed | held; cannot move away | cond.distracted | attention split; snag on Wits |
| cond.restrained | bound; Move forbidden | cond.exposed | defenses opened; attackers gain a lever |
| cond.pinned | held down; most physical verbs forbidden | cond.slowed | fewer bands per move |
| cond.blinded | sight-based Observe forbidden | cond.weakened | reduced harm dealt |
| cond.deafened | hearing-based Observe forbidden | cond.exhausted | intensify ×3; snags growing per stack |
| cond.dazed | reduced actions this turn | cond.bleeding | intensify; periodic S1 harm per stack |
| cond.stunned | no actions | cond.burning | intensify; periodic fire harm |
| cond.unconscious | helpless; no actions | cond.chilled / cond.frozen | escalate at 2 stacks → frozen (Move forbidden) |
| cond.choking | cannot speak; snag; periodic harm in smoke or water | cond.poisoned | generic carrier for ch.07's staged afflictions |
| cond.surprised | caught unaware at the start of a conflict (06.2.4) | cond.silenced | cannot speak (a gag, a spell, a crushed throat) |
| cond.broken | its side's morale clock completed (06.11.5): flees, yields or cowers | cond.heartened | lifted by a rally, a blessing, a cause: the one status bonus (+1 or +2) |

**T-00-19 Data files.** `[D]` Schemas in `data/SCHEMAS.md` (section = file name).

| File | Owner | Owner-blocks allowed |
|---|---|---|
| tags.yaml | 00 (levels 0–2) / 03 | stewards propose via 03 |
| attributes.yaml, scales.yaml, substrate.yaml | 00 | none (scales: ch.01 fills DC and Oracle numbers in its block) |
| effects.yaml | 00 (core library) | 02, 04, 05, 06, 07, 08, 09, 10, 11, 15, 16 [02 amended: IR ch.02] |
| basic_verbs.yaml | 00 (ids, coverage) / 01 (anchor fields) | — |
| boundaries.yaml | 00 | every chapter, for its own handlers |
| resolution.yaml | 01 | — |
| origins.yaml, gen_birth.yaml, kits.yaml | 02 | 13 (setting origins and their kits) |
| evidence.yaml | 03 | — |
| callings.yaml, hybrids.yaml, vehicles.yaml, gen_absorb.yaml | 04 | — |
| abilities.yaml, rituals.yaml, composites.yaml, licenses.yaml | 05 | composites: 04; licenses: 02, 04, 08, 13, 15 [04, 15 amended: IR ch.04 #2, IR ch.15 #8] |
| conditions.yaml, conflict.yaml | 06 | conditions: 07 (affliction carriers) |
| harm.yaml, afflictions.yaml, injuries.yaml, last_chance.yaml | 07 | afflictions: 13 (regional afflictions) [amended: IR ch.13] |
| base_items.yaml, item_properties.yaml, materials.yaml, economy.yaml, gen_loot.yaml, gen_craft.yaml, gen_gift.yaml, gen_item_ability.yaml | 08 | — |
| archetypes.yaml, adversaries.yaml, behaviors.yaml | 09 | adversaries: 13 |
| hazards.yaml, travel.yaml, sites.yaml, traps.yaml, weather.yaml | 10 | 13 (regional entries) |
| factions.yaml, world_turn.yaml, calendar.yaml, legacy.yaml | 11 | factions, calendar: 13 |
| oracles.yaml, anchors.yaml, pacing.yaml, world_seed.yaml | 12 | anchors compiled from every chapter [world_seed.yaml: revision I-028] |
| region_*.yaml | 12 (a world seed's output, 12.16) / 13 (`region_thallen.yaml`, an optional pre-made seed) [revision: I-028] | — |
| codex.yaml | 14 | — |
| social.yaml, investigation.yaml, downtime.yaml | 15 | — |
| companions.yaml | 16 | — |

**T-00-20 Anchor knobs (closed list).** `dc` (source or tier) · `attribute` · `action_cost` ·
`reach_unit` · `stakes` · `duration` · `condition` (inflicted) · `harm_severity` · `harm_tags` ·
`targets` (count or selection over relationship-state) · `time_cost` · `focus_cost`.
Counting [revision: I-062]: a change is counted per knob, not per word changed. `duration` is a feature's
whole **behavior over time**: how long it lasts and how it changes while it lasts (grows, spreads, fades,
burns out, stays put); changing both its length and its growth is one knob. Where a created feature sits
(the doorway instead of the thatch) is the beat's target, not a knob.

**T-00-22 Banned words.** In rules text and data: *level* (of a character), *class*, *XP*, *HP / hit
points*, *mana*, *stamina*, *saving throw*, *skill check*, *advantage / disadvantage*, *injury /
injured / hurt*, *minor / major / severe* as severity names, *exploration turn*, *the System*, *focus*
(for an item), bare *gate* for the generator. In narration: any mechanical number, any rules term
voiced by an in-world character.

---

## Worked examples

All examples follow one continuous character. Numbers owned by later chapters are marked
*(illustrative; ch.NN owns)*; the architecture's own mechanics (evaluation pass, stacking, depth,
boundaries, clocks, generator, gate) are exact.

**Wren** *(illustrative sheet; ch.02 owns creation)*. Attributes: Might +1, Agility +3, Endurance +1,
Wits +2, Intellect 0, Presence 0, Resolve −1 (sum +6: under ch.02 this is Wren *after* her Bent, a creation
sum of +5 with the Bent's +1 on Endurance) [amended: IR ch.02]. Competence: `deed` +1 (floor),
`deed.wilds.tracking` +2 and `deed.martial.archery` +2 (a forester's origin). Vitality 13/13 (12 + Endurance, power band 1), Focus
4/4, fate 1. Licenses: the 15 basic verbs; `lic.lang.common` (native). Abilities *(illustrative; 05)*:
`ab.quarrys_mark` (independent trigger on `on_attack_hit`: apply `cond.exposed` S1 to the target until
`scene_end`; Focus 1; `per: scene_end, uses: 1`); `ab.cinder_stride` (priority-exclusive on
`slot.strike_delivery`, rank 10: Strikes deal `harm.fire`, harm_edge +1, for 3 rounds; Focus 1);
`ab.pressing_advantage` (independent trigger on `on_condition_applied` with `by: self`: regain 1
Focus; `per: scene_end, uses: 1`). Gear: spear (base S2, `harm.physical.pierce`), shortbow (S2
pierce), cloak, rope, rations, a flask of Rime Oil (consumable: priority-exclusive on
`slot.strike_delivery`, rank 20: Strikes deal `harm.frost`, harm_edge +1, for 3 strikes).

### WE-00-1 A boundary crossing: two days on the Salt Road

*Situation.* Spring, week 3, day 7, start of the morning watch, at Ashford. Wren travels to Grey Keep:
5 travel watches along the Salt Road *(illustrative; ch.10 owns travel)*. Plan: travel morning and
afternoon, camp in the evening, sleep through the night. The DM calls
`advance_time(until: arrival, mode: travel)`. The engine lists every boundary crossed and runs them in
order (PR-00-2). Encounter checks use an illustrative d6 per watch (1 encounter, 2 omen, 3–6 nothing;
ch.10 owns the real procedure); the region carries a hidden danger clock `clk.cinder_hunting_ground`
(6 segments; ticks 1 on each omen result; an encounter result here rolls on the road's encounter table).

| # | Boundary | Handlers that fired (phase) | Result |
|---|---|---|---|
| 1 | watch end, D7 morning | `h.10.travel_progress` (4); `h.10.watch_check` (7) | progress 1/5; d6 = 4, nothing |
| 2 | watch end, D7 afternoon | same | progress 2/5; d6 = 2, omen → `tick_clock(cinder_hunting_ground)` 0→1, stage *stirring*, omen: "a hare burned black lies by the road, with no fire anywhere near it" |
| 3 | watch end, D7 evening (camp) | `h.10.watch_check` (7) | d6 = 5, nothing |
| 4 | **dawn, D1**: `rest_long` completes (event boundaries first, 00.7.6) | `h.07.rest_recovery`, `h.05.focus_recover` (3); `h.00.reflection` (8) | Vitality and Focus already full; `reflection` fires |
| 5 | `reflection` | `h.03.recency_update`, `h.04.recognition_pass`, `h.04.standing_offers` (8) | recognition pass: **abstain** (no calling eligible); nothing is voiced |
| 6 | watch end, D7 night | `h.10.watch_check` (7) | d6 = 3, nothing |
| 7 | day end, D7 | `h.05.day_recharge` (3); `h.07.natural_recovery` (3); `h.10.supply` (4); `h.11.situation_timelines` (6); `h.10.weather` (7) | supply 3 → 2; weather for D1: cold rain |
| 8 | **week end, W3** | `h.08.upkeep`, `h.16.retinue_upkeep` (4); `h.11.world_turn` (6); `h.15.downtime_week` (6); `h.00.reflection_if_downtime` (8) | World Turn *(illustrative; 11)*: the Salt Guild's hidden goal clock "Corner the Salt Road" ticks 4 → 5 of 8; its perceivable trace is written as a rumor, "tolls doubled at the Grey Keep bridge", heard at the next settlement |
| 9 | watch end, D1 morning | travel, check | progress 3/5; d6 = 6 |
| 10 | watch end, D1 afternoon | travel (4), check (7) | progress 4/5; d6 = 1 → encounter table → "a cinder hound on the hunt"; the handler is **interrupting** |

The afternoon boundary finishes its phases 8–9, then `advance_time` halts at dusk on D1 and returns
`remainder: 1 travel watch`. The DM narrates the journey from the returned list only: the burned hare,
the cold rain at dawn, then a shape pacing the verge in the rain, steam rising where the drops hit its
back. It invents no second omen and no weather that was not rolled. After the encounter, Wren may
resume; the remaining watch is not lost.

### WE-00-2 The gate→fill generator produces an item

*Situation.* The hound fight resolves *(illustrative; 06)*. Wren's last beat is a shortbow shot:
Agility +3, competence +2 (`deed.martial.archery`), total +5 vs the hound's Guard 13. The d20 shows 19:
total 24, margin +11, **critical success**. The hound (`adv.cinder_hound_07`; tags
`creature.beast.predator`, `creature.elemental.fire`; threat band T2) is killed.

The DM classifies `[J:enum]` circumstance = **decisive** (killed in a fair fight by a resolved success;
not costly, not merciful, not scavenged) and calls
`generate(gen.loot, adv.cinder_hound_07, decisive, critical_success)`.

1. **Pool gate** *(pool content illustrative; 08 owns)*. The archetype's trophy base is
   `item.jewelry.charm`. Entries gated on the source's tags:

   | Entry | Gate | mod_group | Weight | Kept? |
   |---|---|---|---|---|
   | `prop.ember_ward` (the archetype's **signature**): reduce `harm.fire` by the tier value | `creature.elemental.fire` | resist_fire | 3 | yes |
   | `prop.warm_blood`: cold-weather hazards count one severity rung lower | `creature.elemental.fire` | env_cold | 2 | yes |
   | `prop.hounds_nose`: a Precision lever on Observe when tracking by scent | `creature.beast.predator` | senses | 2 | yes |
   | `prop.snarl`: edge +1 on Talk to intimidate `creature.beast` | `creature.beast.predator` | intimidate | 1 | yes |
   | `prop.searing_bite`: Strikes add fire harm | `creature.elemental.fire` | weapon_fire | 2 | **no**: `base_kinds: item.weapon` excludes a charm |

2. **Tier gate.** T2 → `tier_cap` 2. All entries start at tier 1: all kept.
3. **Quality rung.** (decisive, critical_success) → `fine`: 1 signature slot + 1 magnitude slot
   *(illustrative; 08)*. Fill method for `decisive`: **signature**.
4. **Degree effect.** Critical success → **Greater**: the signature property gains +1 tier (may reach
   `tier_cap` + 1 = 3).
5. **Signature slot.** `prop.ember_ward` at tier 2 + 1 = **3**: reduce fire harm by 3. Its mod_group
   `resist_fire` is removed from the pool.
6. **Magnitude slot.** Weights: warm_blood 4 × ½ (recency: generated three loot draws ago from a fire
   beetle; weights are doubled first, 00.11.3 step 7) = 2; hounds_nose 4; snarl 2. Total 8 → 25% / 50% / 25%. [verification: V1-002] The engine draws d100 = 63 → bands
   1–25 warm_blood, 26–75 hounds_nose, 76–100 snarl → **`prop.hounds_nose`**, tier `tier_cap − 1` = 1.
7. **Caps.** Charm slot cap 2 and the item budget (reduction 3, inside ch.07's cap of 4): pass.
8. **Output.** `item.i0107`, base `bi.fang_charm`, quality fine, signature `[ember_ward T3]`,
   magnitude `[hounds_nose T1]`, provenance {cinder_hound_07, decisive, critical_success}, log {pool 4 →
   4 → 3; weights 2/4/2; d100 63}.

The DM names it ("a fang on a thong, still warm") and narrates only what it holds. *Non-example:* "the
charm keeps the chill of the rain off you" is forbidden: warm_blood was not generated (INV-2, SG-15).

### WE-00-3 An unlicensed attempt, redirected by the license's fallback

*Situation.* Night at Grey Keep. The archive door is established as locked with a guild-made lock
(`door_archive.locked = true`; `door_archive.lock_make = guild`). Player: "I pick the lock with my
knife. It's just a cheap archive lock."

- **Assertion.** "It's just a cheap lock" contradicts an established fact and creates nothing (SG-06).
- **GATE** `[J:enum]`. Picking a lock is not within any basic verb's coverage (T-00-11 lists
  lockpicking as licensed). The license that would cover it is `lic.training.lockwork` *(illustrative;
  05 owns)*: scope "Open mechanical locks and simple traps with picks or improvised tools; at grade
  `common`, locks up to Hard tier." Wren does not hold it → **G3**.
- **Redirect (a lookup, not an invention).** The license's `crude_fallback`: `{verb: force, method:
  "break the lock, hasp or hinges", dc_shift: 0, reach_cap: standard, consequence: "trait.sense.loud"}`;
  `acquisition_paths`: mentor (a locksmith or a thief teaches; a 6-segment project clock ticked by one
  practice roll per week), origin (urban origins at creation), recognition (`deed.guile.thievery`,
  04). No time or action is spent.
- **The DM says:** "The wards are guild-cut; nothing in your hands knows how to read them. You can break
  it: the hasp is iron and the oak around it is old, but it will be loud. Picking locks like this is
  something a locksmith or a thief could teach you." The ruling is logged (`kind: g3_redirect`).
- The player chooses to break it (WE-00-4). *Boundary pair:* had the door carried a plain latch-bar,
  lifting it is `verb.handle` (G1) with no license at all; had the lock been sealed by a ward spell,
  breaking the hasp would open the wood but leave the ward: the beat splits by scope (00.12.2).

### WE-00-4 Assembling a check through the evaluation pass

*Beat.* Break the hasp. Anchor `verb.force` (no deltas). Primary deed tag `deed.martial.athletics`.
Two scenes ago the DM narrated "a length of iron bar lies among the gate's wreckage" and, by
write-on-mention, recorded it (`obj.iron_bar_03`, now carried: fact `pc.wren.holds obj.iron_bar_03`).

PR-00-1:
1. Attribute: Force allows Might only → **+1**.
2. Competence: entries on `deed.martial.athletics`, `deed.martial`, `deed`: only the floor → **+1**.
3. Edge: none → **0**.
4. Circumstance: lever `obj.iron_bar_03` typed **Precision** (a tool that lets the method be done
   better) → **+2**. The player also proposes "the rain has rusted it". There is no such fact; the
   question is G0: the Oracle, rung Unlikely (hasps in covered doorways rarely rust through), d100 = 41
   → **no**; `set_fact(door_archive.hasp.condition = sound)`. No snag, no lever.
5. Status: none → **0**. Total **+4** (clamp not reached).
6. DC: no stored DC for the hasp; not opposed; tier `[J:rung]` **Moderate** (an iron hasp in old oak:
   a strong, competent person usually manages) → **15** (reference; ch.01 owns), written as
   `door_archive.hasp.dc = 15`.
7. Odds: needs 11+ → success-or-better 50%, critical success 5%, critical failure 5%, near miss 15%.
8. Stakes `[J:rung]` **Risky** (guards in the keep; failure means being heard: an S2 Exposure cost).
   Reach **Standard**. Method consequence regardless of degree: loud.

OFFER: "Breaking the hasp: you need 11 or better (50%). It will be loud whatever happens; if it fails,
someone hears you properly." The player commits. `roll_check`: d20 = 9 → total 13, margin −2 →
**failure, near miss**. The player takes success-at-cost: one cost at S2 → the DM picks the menu type
whose trigger fits the method (`cost.exposure`: noise). State writes: `door_archive.hasp = broken`,
`door_archive.locked = false`; the alarm clock ticks for the loud consequence and for the exposure cost
(WE-00-5).

### WE-00-5 A hidden clock ticks with omens, and two clocks race

`clk.alarm_grey_keep` *(template content illustrative; 10, or a region's seed, 12.16)*: kind danger, 6 segments, **hidden**;
tick sources: a `trait.sense.loud` beat inside the keep → 1; `cost.exposure` → U(severity);
auto_ticks: +1 at each `hour` boundary while the PC is inside after dusk; omens — stirring: "a dog
barks twice somewhere below", "a door closes across the yard"; building: "lantern light moves along the
wall walk", "boots on the stair, unhurried"; imminent: "a voice calls a name and no one answers", "in
the gatehouse, someone is untying the bell rope". On complete: guards converge on the PC's location
(`create` encounter), **interrupting**; defeat disposition capture (so not lethal).

| Event | Tick | Fill | Stage → omen the narrator must render |
|---|---|---|---|
| hasp broken (loud) | +1 | 1/6 | stirring: a dog barks twice somewhere below |
| exposure cost S2 (U = 1) | +1 | 2/6 | stirring: a door closes across the yard |
| search beat 1 (Observe, success, Standard) | — | 2/6 | `clk.find_ledger` (public, 4) +2 → 2/4 |
| `hour` boundary (auto) | +1 | 3/6 | building (3 ≥ half): lantern light on the wall walk |
| search beat 2 (failure; Risky → S2 `cost.time`) | +1 | 4/6 | building: boots on the stair, unhurried |
| search beat 3 (success; Amplifying lever = the clerk's index card found earlier → Great) | — | 4/6 | `clk.find_ledger` +3 → complete; its link creates `clk.get_out` (public, 4) with `races_with: clk.alarm_grey_keep` |
| escape beat 1 (Sneak, success, Standard) | — | 4/6 | `clk.get_out` 2/4 |
| `hour` boundary (auto) | +1 | 5/6 | **imminent** (remaining 1 ≤ max(1, 6÷4)): someone is untying the bell rope. Completion is capture, not lethal: no lethal warning |
| escape beat 2 (Sneak, near miss; the player takes success-at-cost: `cost.exposure` S2) | would be +1 | — | the same event completes both clocks; the acting side's delivered reach completes first (00.8.5): `clk.get_out` 4/4 **completes**, `clk.alarm_grey_keep` is **voided** before its tick lands |

Wren drops over the outer wall as the bell starts, too late to matter. Narration mentions each omen
once, in the turn its tick happened, and never states the alarm's number (hidden clock).

### WE-00-6 An effect composing through the substrate

*Situation.* Next morning Captain Hesk (T3; Agility +2, competence `deed.martial` +4 → Guard 16;
Vitality 16; armor reduction 2 against `harm.physical` *(illustrative; 06/08/09)*) rides Wren down on
the Salt Road. On her previous turn Wren feinted (Setup, success), recording `cond.off_balance` on Hesk.
Earlier this conflict she activated Cinder Stride (Focus 4 → 3) and then coated her spear in Rime Oil.

1. **Priority-exclusive.** Both claim `slot.strike_delivery`. Rime Oil (rank 20) owns the slot. Cinder
   Stride (rank 10) is **fully suppressed**: no fire conversion and no +1 harm_edge. (`use_ability`
   warned at activation, since Rime Oil was already applied: the Focus was spent knowingly.)
2. **Frame.** Strike, a quick thrust → Agility +3; primary tag `deed.martial.polearm` → competence:
   floor +1 (her archery +2 does not cover polearms); lever: `cond.off_balance` on Hesk, typed
   **Amplifying** by the player (an opening to exploit) → reach Standard → Great. Total +4 vs Guard 16:
   needs 12 (45%). Stakes Risky (failure: Hesk's counter, S2 harm).
3. **Roll.** d20 = 20 → total 24, margin +8 = success; natural 20 → **critical success**. Delivered
   reach: Great + 1 = **Exceptional (4)**.
4. **Harm, dealer side** (00.10.5): E1 base S2 pierce; the slot owner replaces the harm type with
   `harm.frost`. E2 steps: delivered reach 4 → +2 → **S4**. E3 → **8**. E4 harm_edge: Rime Oil +1
   (Cinder Stride suppressed) → **9**.
5. **Harm, receiver side.** E4 reduction: Hesk's armor reduces `harm.physical` only; the harm is now
   `harm.frost` → 0. E5: no resistance or vulnerability to frost. **9** harm. Hesk 16 → **7** (at or
   below half → **bloodied**, a shown descriptor via `on_vitality_threshold`).
6. **Hooks** on the depth-0 event `on_attack_hit`: target's prevent/redirect first: Hesk's shield block
   is his reaction, already used this round, so none. Then Wren's: Quarry's Mark fires (Focus 3 → 2) →
   `apply_condition(cond.exposed)` on Hesk. That application is a **depth-1** event, so
   Pressing Advantage (`on_condition_applied by self`) does **not** fire (INV-12). Core rules still
   run: the harm counted, the threshold was crossed.
7. **Narration obligations:** name the exposed condition (visible) and the frost (rime crackling in the
   wound); never fire.

*Boundary pair.* Without the Rime Oil, Cinder Stride would own the slot: fire, +1 → 9 again but typed
`harm.fire`. *Non-example:* "the fire and the frost together shatter his mail": no composite exists for
this pair, and a suppressed claimant never counts as present for a composite's keys.

### WE-00-7 Conditions stacking and neutralizing

Hesk's squire throws a lamp at Wren: `cond.burning` *(illustrative; 06)*: intensify, max 3; periodic
at `turn_end`: harm S1 (`harm.fire.flame`) per stack.
- Applied: 1 stack. At Wren's turn end: harm 1 → receiver side: reduction from the Ember-Fang Charm
  (`harm.fire`, 3; cascade covers `harm.fire.flame`) → **0**.
- Applied again: intensify → 2 stacks, duration refreshed; at turn end: harm 2 → **0**.
- A hedge-witch's frost bolt then applies `cond.chilled`, which `neutralizes: [cond.burning]`: burning
  is removed and chilled is **not** applied (PR-00-5 step 1). The narrator shows steam and nothing else.
- *Boundary:* without the charm, 2 stacks would deal 2 harm per turn end, and a third stack 3.

### WE-00-8 Tags, competence and evidence

Wren shoots a fleeing bandit's horse from the treeline. The DM classifies the primary deed tag
branch → child → deeper: `deed.martial` → `deed.martial.archery` → `deed.martial.archery.bow` (if 03
has added level 3). Competence lookup over ancestors: `.bow` none, `.archery` **+2**, `.martial` none,
`deed` +1 → **+2**. Evidence after the resolved success: `record_evidence {deed: "shot a fleeing
rider's horse from cover at dusk", tags: [deed.martial.archery.bow], challenge_band: 2, stakes: risky,
lethal_context: false, witnesses: [npc.bandit_03]}`; the engine cascades it to `.archery`, `.martial`,
`deed` with ch.03's weights, and returns nothing about tallies. Wren then lets the unhorsed bandit run:
a second event, `tags: [conduct.mercy]`, `conduct_sign: +1`.

### WE-00-9 A precedent reused

During the escape Wren swung on the gatehouse chain to drop onto the outer bank. There was no rule for
it; the DM anchored to `verb.exert` (jump) with two knob changes: `dc` (re-derived tier: Hard, because
the chain turns a Beyond drop into a controlled swing) and `stakes` (Dire: a 20-ft fall). The ruling was
logged: signature `verb.exert+dc:tier_rederived+stakes`. A week later, at a mill, the player says "I
swing across the millrace on the hoist rope." `find_rulings(verb.exert)` returns it; the facts match
(a rope swing replacing an unjumpable gap), so the DM reuses **Hard** and **Dire**. The rope is wet: that
is a new fact, handled as a snag (Precision −2), not as a departure from the precedent.

---

## Edge cases & adaptation anchors

- **A chapter needs a quantity, hook, slot, operation, facet, branch or time unit that 00 lacks.** File an
  Interface request (PR-00-8); meanwhile express it with the nearest existing primitive plus a DL note.
  Never invent one silently.
- **A value would overflow a ladder** (harm above S5, reach above 4, stakes below Safe): clamp. A
  clamped step is never converted into something else unless a rule says so (e.g. 01's overflow of
  reach into a follow-up lever).
- **A fact was established in the same beat as the declaration.** It cannot be a lever for that beat
  (00.3.9a); it can be for the next.
- **Two independent triggers would each prevent the same event.** The first in order (00.10.7) prevents
  it; the second never fires (the event no longer exists) and keeps its use.
- **A suppressed priority-exclusive effect has a duration.** It keeps counting down while suppressed and
  resumes if the winner ends first.
- **An entity is mentioned whose kind is undetermined** ("someone moves in the dark"). Create an entity
  of kind `unknown` with an id and `introduced_at`; settle its kind by the Oracle or a table when first
  needed.
- **Time must pass inside a conflict for a long action** (a ritual during a fight). The action's duration
  in rounds is data (05); the rounds are played, not skipped.
- **The player wants to skip a lot of time** ("I spend the winter at the monastery"). `advance_time`
  runs every boundary (00.7.7); interrupts halt the skip; the DM narrates from the returned list.
- **A boundary handler of one chapter needs another chapter's state.** It reads it through that
  chapter's contract interface (00.17), never directly.
- **A player's out-of-fiction question about a sealed thing.** The DM answers with what the codex shows
  (visibility class) and says plainly that the rest is not known to the character.
- **An effect would give a reaction to an entity that has none by default.** Only via op `economy` and
  only where ch.06 allows (INV-11).
- **Anchoring the architecture itself.** When a novel mechanic appears in play, reach first for the
  clock (anything extended or threatening), the condition schema (anything that lingers), the generator
  (anything produced from circumstance), a license (anything that permits), a lever (anything
  situational); two-change limit applies.

## State touched

This chapter defines the state model rather than playing on it; directly, it owns:
- **Types and shapes** (00.6.1–00.6.2) for every family; **visibility classes** (00.6.4); the **sealed
  partition** and its gates (00.6.5).
- **Time** (00.7): the game clock, time mode, the boundary registry `data/boundaries.yaml`.
- **Clocks** as a primitive (00.8); **facts and entities** as generic types; the **write log**.
- **Frames** (00.13) as a type; the **ruling ledger** record shape (00.15.5).
- **Tools used / required:** all of 00.14.2. **Hooks:** defines all (00.10.2). **Handlers registered:**
  `h.00.clock_auto`, `h.00.durations`, `h.00.reflection`, `h.00.reflection_if_downtime`.
- **Runtime capabilities assumed:** RC-RNG, RC-STORE, RC-SEAL, RC-SCHED, RC-LOG, RC-DATA, RC-QUERY,
  RC-EVAL, RC-RETRIEVE, RC-AUDIT (00.14.1).

## Interface requests

What 00 needs from, and hands to, each chapter (beyond the contracts of 00.17, which are binding):
- **01:** confirm or adjust the DC ladder within CT-1…CT-6 with a recomputed T-00-6; confirm the degree
  rule and near-miss band; define the nine reserved cost-menu ids and the READ tables; define
  `deliver_count`; own `fate` (0–3, one mandatory use for ch.07); auto-commit interplay with 14 (never
  for lethal frames); the 15 verb anchor cards in `data/basic_verbs.yaml` (anchor fields only); the
  `trait.*` general rules.
- **02:** the attribute-generation method within 00.4.3; the floor value (default +1 at `deed`); the
  Vitality formula within 10–16; `gen.birth`; kits by item tag.
- **03:** all tags below level 2 with definitions; the full tag_event schema extending 00.6.8; counted
  evidence hooks; the conduct axes' poles and tests (seeded in `data/tags.yaml`).
- **04:** `power_band(pc)` from tiers; tier-to-competence values ending ≤ +6; the one lifetime +1 to an
  attribute; a concrete definition of confidence; `recognition_event`; `gen.absorb`; season
  consolidation handler.
- **05:** slot partition sizes (total 12–24); Focus numbers within 00.3.13; stretch and emulate prices;
  recharge types expressed as `{per, uses}`; the effect-library additions needed for abilities.
- **06:** definitions for every reserved condition id (T-00-15); range bands and flags (00.17 Q14); the
  P9/P14 decision under INV-11; the companion command action.
- **07:** the harm-state ladder (Dying steps 2–4), the Two-Key rule and lethal warning writing
  `lethal_context`; the reduction cap (0–4); rest effects and interruptions; afflictions and injuries on
  the condition schema.
- **08:** generator domain configs (`gen.loot`, `gen.craft`, `gen.gift`, `gen.item_ability`): pools,
  circumstance enums, quality rungs and slot counts, fill-method maps; the item-layer budget.
- **09:** threat-band templates within 00.3.7; `threat_advisory`; archetypes as manufacturers.
- **10:** hazards on the severity scale; travel and exploration activity durations; the watch and
  interval checks; site time per significant beat.
- **11:** World Turn and Season Turn handlers; calendar engine; `institutions_matching`; reputation from
  `recognition_event`.
- **12:** compile `data/anchors.yaml`; the always-loaded turn checklist; tension-dial Oracle shift (≤ 1
  rung); claim-vs-state procedure over `check_claims`.
- **13, 14, 15, 16:** content and presentation per 00.17.
- **To the orchestrator:** (a) retire BRIEF §7's "Default modifier +2" and free-integer DCs in favor of
  00.3.5/00.3.8; (b) a constitution PATCH candidate to align P5's "calibrated classifier" wording with a
  deterministic tally scorer whose confidence ch.04 defines (R2 §4 T-1, R3 §4 T-4); (c) note that
  Addendum A's "recalibrate the DC ladder" is satisfied by adding competence, not by moving DCs
  (DL-00A-05).

## Open empirical questions

Each has a concrete default already in the rules and a named test that would settle it.

| Id | Question | Default shipped | Named test |
|---|---|---|---|
| OEQ-00-1 | Are seven attributes separable enough for reliable selection? | 7 (00.4) | **T-00-ATTR**: 60 novel actions × 3 independent DM runs; target ≥ 90% agreement on attribute, ≥ 85% on deed branch, ≥ 70% on level-2 tag; disagreements become distinguishing-test revisions. **Level-2 stratum** (00.2.2's oversized sets): 12 more actions for each of martial, arcane, craft, lore and influence (60), 3 runs each; target ≥ 70% agreement on the child *within each of the five* (not pooled) and no sibling pair confused in more than 10% of its branch's actions; a miss rewrites the confused pair's distinguishing tests and retests; a second miss sets that branch's CHILD step to stop at the branch (03.1.5 step 2) until a 00 amendment regroups it [revision: I-044] |
| OEQ-00-2 | Do the harm magnitudes and Vitality envelope give the intended fight lengths? | 1/3/5/8/12; PC 10–16 | **T-00-PACE**: simulate 1,000 fights per band pairing with 06/09 numbers; target equal band ≈ 4–7 rounds with the PC Staggered in ≤ 30% of fights |
| OEQ-00-3 | Do omens make hidden clocks perceivable? | one omen per tick | **T-00-OMEN**: 3 playtest sessions; share of imminent-stage omens that draw a player response; target ≥ 50% |
| OEQ-00-4 | Is a one-link trigger chain enough for designed synergies? | depth rule 00.10.8 | **T-00-DEPTH**: enumerate every ability/item pair in 05/08 data; if > 5% of *intended* synergies need a second link, allow a `chain_ok` flag at depth ≤ 2 |
| OEQ-00-5 | Does halving recent entries give enough variety? | ×½ over the last 5 draws | **T-00-VARIETY**: 200 simulated drops per archetype; target the same property in consecutive drops ≤ 15% |
| OEQ-00-6 | Does write-on-mention hold over long play? | 00.6.6 | **T-00-WOM**: 50-turn harness; narrated-but-unrecorded elements per turn; target ≤ 2% |
| OEQ-00-7 | Does the +16 ceiling keep top-band play challenging? | caps 00.3.5 | **T-00-CEIL**: simulate P5 vs T5 and P5 vs T4 encounters; target T5 remains "hard" by 09's advisory |
| OEQ-00-8 | Is one interval per significant beat the right site cadence? | 00.7.3 | **T-00-SITE**: 3 dungeon runs; light and encounter-check pacing against 10's targets |
