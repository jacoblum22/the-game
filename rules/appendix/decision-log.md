# Decision Log

Every non-trivial design decision in the ruleset, with alternatives considered and evidence.
Format and conventions: see `_process/BRIEF.md` §11. Each chapter author owns its own section;
entries are append-only once other chapters cite them (`[DL-CC-NN]`).

## DL-00 — Orchestrator (cross-cutting decisions)

### DL-00-01: Player-facing complexity is not a design constraint
- Decision: No rule is cut, coarsened, or simplified to reduce what the player must track. Rules are judged only by (1) player freedom to try creative ideas and (2) the AI's ability to respond correctly.
- Alternatives considered: Constitution Pattern P3's player-facing comprehension wall (3–5 items while learning, 7±2 once familiar) as a hard budget — rejected by the project owner's explicit direction ("don't worry about complexity for the player at all").
- Evidence: Owner direction, 2026-09-29. P3 is a SHOULD-level pattern, so deviation is permitted with justification.
- Serves: goal 1, goal 2.
- Revisit if: real playtesting shows players failing to use their own characters' capabilities because they cannot find or recall them (then the fix is the codex [C:P7], not cutting rules).

### DL-00-02: Classic fantasy with hidden mechanics; sandbox; telegraphed death
- Decision: No diegetic "System"; recognition is voiced through fiction; open-ended sandbox with retirement/legacy as the "finish"; death is possible only after explicit telegraphing, a dying state, and a last-chance choice.
- Alternatives considered: diegetic LitRPG System (closest to the research corpus); arc campaign with a finale; episodic runs; no-permadeath; hardcore — all offered, owner chose the above.
- Evidence: Owner decision, 2026-09-29.
- Serves: goal 1 (fiction-first freedom), tone.
- Revisit if: owner changes direction.

### DL-00-03: Technical choices are defaults, not constraints
- Decision: The Gemini-flash + deterministic-tools runtime, the non-ML tag-tally class scorer, and the [D]/[J]/[N] split are starting defaults. Authors may replace any of them with a better-evidenced approach, recorded here. Each chapter states the runtime capability it assumes.
- Evidence: Owner direction, 2026-09-29.
- Revisit if: n/a (standing policy).

### DL-00-04: PC maximum Vitality grows with power band
- Decision: max Vitality = creation value (10–16, reference 12) + 2 × (power_band − 1), hard cap 24. Ch.07 owns the rule and its recompute handler; ch.02 the creation formula; ch.04 supplies `power_band`.
- Alternatives considered: flat Vitality for life (ch.06 simulation: P4 vs one T4 falls 87% → 68%, P5 vs one T5 80% → 57%); Vitality per tier of every calling (stacks across callings, breaks the cap); Endurance-only growth (attributes are nearly fixed, 00.4.3).
- Evidence: rules/_process/simulation/06-conflict-sim.md; R3 gap G-8; 00.3.12 envelope.
- Serves: goal 2 (fights at equal band stay fair across the whole power range), C:P2 (growth routed through recognized tiers, no separate level).
- Revisit if: Wave-4 simulation with ch.09's final templates shows equal-band win rates outside 70–95% for a baseline specialist.

### DL-00-05: A conflict's challenge band is relative to the PC (resolves I-005)
- Decision: for evidence weighting (ch.03), a conflict's challenge band = the PC's power_band + an advisory offset (trivial −2, easy −1, fair 0, hard +1, lethal +2), clamped 1–5, instead of the foe's raw threat band. Integration edit to ch.03; ch.04's thresholds stand.
- Alternatives considered: keep threat band (ch.09's re-run of ch.04's pacing script under ch.09's encounter budget gives tiers at sessions 7/20/31/46, tier 5 never); accept current-band deeds for tiers 2–3 in ch.04 (patches one calling family, leaves the mismatch).
- Evidence: rules/_process/simulation/09-i005-check.py + output (restores 5/11/22/39/60, tier 5 in 59/100 runs); consistent with DL-03-02 (quality is relative to odds, not absolute DC).
- Serves: goal 1 (growth tracks what was hard *for you*), C:P2 (history-gated tiers stay reachable).
- Revisit if: Wave-4 campaign simulation shows tier pacing outside ±25% of 5/11/22/39/60 for a focused character.

## DL-00A — Architecture

Decisions made in `00-architecture.md` (Wave 2). Digest shorthand `[R1 §x]`…`[R7 §x]` per 00.1.6.

### DL-00A-01: Adopt R4's rule-form guide as the binding style guide, with eight additions
- Decision: Rule kinds `[D] [J:flag] [J:enum] [J:rung] [J:open] [T] [S] [N]`; P-A (most reliable form) and P-B (bounded blast radius); a mandatory "Worst case:" line on every `[J:*]` rule; SG-01…SG-20 adapted, plus SG-21 canonical names/banned words, SG-22 every number cites its scale, SG-23 integers and no percentages, SG-24 clocks name the obstacle and carry omens, SG-25 lifecycle on every entry, SG-26 self-contained cards, SG-27 explicit negative facts, SG-28 durations in ladder units. The R7 anchor standard (seven properties) and two-change limit are part of it.
- Alternatives considered: BRIEF §5's three kinds (hides a ~10× reliability spread inside `[J]`); a free-form style guide (no audit hook).
- Evidence: [R4 §4.1–4.5; R: https://arxiv.org/abs/2603.00077; R: https://arxiv.org/abs/2607.02802; R: https://arxiv.org/abs/2607.23386]; [R7 §3.4]; [BRIEF A3].
- Serves: goal 2; C:III (bounded judgment); C:P10.
- Revisit if: T-R4-02 ("Seduce-the-DM") shows a rule form performing outside its stated reliability band.

### DL-00A-02: The AI supplies no numbers; checks are assembled from state inside a typed frame
- Decision: `roll_check(dc, modifier)` with free integers is retired. The frame (00.13) computes the DC (stored → opposed → tier) and the modifier (attribute + competence + edge + circumstance + status) from state; the DM supplies ids, rungs, flags and enums only (INV-3). BRIEF §7's "default modifier +2" is retired.
- Alternatives considered: keeping free integers with a ladder hint (observed 11% off-ladder DCs, 62% arbitrary modifier 0); DC from tier plus circumstance flags on the DC (merged instead into levers, DL-00A-10).
- Evidence: [R4 §3.4 (F002 logs re-tallied), R-01, R-02]; [R: src/tools.py]; [BRIEF A2 #1].
- Serves: goal 2; C:I (the DM still drives every tool); C:P8.
- Revisit if: T-R4-01 ("DC A/B") shows the frame does not reduce DC spread for identical contexts.

### DL-00A-03: Dice and who rolls
- Decision: d20 for every check, d100 for the Oracle and percentile tables, small dice only inside data tables; the engine rolls everything including the DM's "random" choices; each attempt is one roll by the active side (aimed actions: actor vs defense; resisted effects: target vs effect DC), decided by a `[J:flag]`.
- Alternatives considered: the player always rolls (Blades/Ironsworn; makes adversary degrees awkward and doubles the defensive math); both sides roll (contests double the dice and variance); damage dice (rejected, DL-00A-29).
- Evidence: [R4 §3.3 W6; R: https://arxiv.org/abs/2601.05414]; [R5 §5.2 #2]; [R3 §4 T-16]; PF2e static defenses [R7 §2.9].
- Serves: goal 2; auditability.
- Revisit if: playtests show players feel passive when adversaries roll (then 06 may add player-facing defense reactions; the one-roll rule stands).

### DL-00A-04: The bounded-accuracy envelope
- Decision: total check modifier clamped −8…+16; PC base (attribute + competence + edge) ≤ +12, others ≤ +14 (T5 only); competence 0…+6; edge +2; circumstance ±4 (≤ 2 levers, ≤ 2 snags); status −4/+2; five power/threat bands with typical modifiers per band (00.3.7).
- Alternatives considered: PF2e-style unbounded proficiency growth (inflates with an endless sandbox; a squish would later be needed and never counts as retirement under C:VI); no caps (fails the per-layer power budget).
- Evidence: [R2 §00 bounded accuracy, #7]; [R3 §00.9, §00.13]; [R1 §00.C hard caps]; coherence simulation `coherence00.py` (equal bands ≈ fair; +1 band hard; +2 lethal-advisory).
- Serves: goal 2 (legible odds on the thousandth roll); C:VI; C:P11.
- Revisit if: T-00-CEIL shows T5 encounters trivial for P5 characters.

### DL-00A-05: Keep the 10/15/20/25/30 ladder; bind ch.01 with calibration targets
- Decision: the reference DC ladder is unchanged; ch.01 may move a rung ±2 only if CT-1…CT-6 still hold. The research's "harsh ladder" finding is resolved by competence (the floor and specialties), not by moving DCs.
- Alternatives considered: lowering all DCs (breaks the top of the envelope; paragons auto-succeed "hard"); narrowing the critical-failure band (ch.01's call; not needed for CT-6 at reasonable attempts).
- Evidence: exhaustive enumeration T-00-6 (`odds00.py`); [R4 §3.4]; [R7 §4.2, §5.9]; [R2 §3 enumeration].
- Serves: goal 2; honest OFFER odds (goal 1).
- Revisit if: ch.01's DL or playtests show "moderate" tasks failing more than ~45% for specialists.

### DL-00A-06: Competence lives on tags; the P2 floor is a competence entry at the root
- Decision: the "trained bonus" is a competence map keyed to deed tags; lookup = highest entry on the beat's primary deed tag or any ancestor. Every PC holds +1 at `deed` (constitution P2's baseline floor), which ch.02 may set in 0…+2. Items never grant competence.
- Alternatives considered: a separate skill list (a second, overlapping vocabulary the AI must classify into); a flat proficiency bonus (no texture, invites attribute arbitrage); no floor (early characters fragile, violates P2).
- Evidence: [C:P2]; [C:P5 hierarchy cascade]; [R3 §03.1 most-specific, §03.3 tags as compatibility]; [R4 §9 02 #3].
- Serves: goal 2 (one vocabulary for evidence, competence, callings); goal 1 (every PC is competent at something from day one).
- Revisit if: T-00-ATTR shows primary-tag classification below 70% agreement at level 2.

### DL-00A-07: Attribute ranges and the only ways attributes change
- Decision: creation −1…+3, sum +5…+7; lifetime −2…+4; at most one +1 ever (calling tier), at most −1 per attribute from maims; items, conditions and abilities never change attributes; each attribute feeds its defense and at most one listed derived value.
- Alternatives considered: attributes that grow with tiers (reintroduces levels by the back door, C:P2); item attribute bonuses (GURPS-style arbitrage).
- Evidence: [C:P4]; [R1 §00.C attribute arbitrage]; [R2 §00 attribute table]; [R3 §4 T-19].
- Serves: goal 2; C:P4; C:P11.
- Revisit if: ch.04's tier rewards need a second attribute increase to feel meaningful (then amend here, not locally).

### DL-00A-08: Seven attributes: Might, Agility, Endurance, Wits, Intellect, Presence, Resolve
- Decision: seven method-keyed attributes, each with a one-question distinguishing test against its neighbors; the verb → attribute map with a lower-of-two tie-break shown in the OFFER.
- Alternatives considered: four (GURPS/HWFWM: merges perception and knowledge into an overloaded stat); five (Ironsworn approaches: no split between knowing and noticing, no withstanding-mind stat); six (R7's placeholder set: Wits overloaded with perception + knowledge + magic theory, the Underworld Wisdom failure); FAE's six approaches (describe manner, not capability; invite "describe it Sneaky to use my best stat"); eight or more (overlapping lanes raise wrong-choice rates).
- Evidence: [C: Sync Impact Report, ability scores]; [R2 §00 attribute precedents]; [R4 §3.2 S1 (wrong-skill 3–11%), §9 02 #1]; [R7 §2.1 FAE, §4.1]; [R3 §00.14].
- Serves: goal 2 (reliable selection); goal 1 (every method has a stat that fits it).
- Revisit if: T-00-ATTR agreement on attribute < 90%.

### DL-00A-09: Vitality and Focus envelopes; Focus is not attribute-derived
- Decision: PC Vitality 10–16 at creation, cap 24 (07 owns semantics, 02 the formula); Focus 3–5 at creation, cap 12, activation 0–4 base and ≤ 6 after modifiers (05 owns); Focus derives from no attribute.
- Alternatives considered: Focus from Resolve or Intellect (creates a caster god-stat stacking casting and pool); large pools (100-style: invites percentage thinking).
- Evidence: [C:P9]; [R2 #8, §5 gap 30]; [R3 §05.7]; [R6 §C.3]; [BRIEF §7 probe Vitality 12].
- Serves: goal 2; C:P9.
- Revisit if: ch.05's spend simulation cannot fit its costs inside 3–5 starting Focus.

### DL-00A-10: Levers and snags are the only situational currency; DCs never move for circumstance
- Decision: every situational help or hindrance is a lever or snag citing an established fact (Precision ±2 roll, Protective ∓1 stakes, Amplifying ±1 reach), max two of each, net roll ±4; R4's "circumstance flags on the DC" are expressed as snags/levers so nothing is counted twice; the DC is a stable property of the obstacle.
- Alternatives considered: DC flags plus levers (double counting; two places to be lenient); advantage/disadvantage (a second currency; stacking ambiguity).
- Evidence: [R7 §4.2, F2, F3]; [R4 §4.6, SG-03]; [BRIEF A2 #12]; Cypher asset cap and PF2e ±4 cap [R7 §2.6, §2.9].
- Serves: goal 1 (creativity always pays, visibly); goal 2 (capped, auditable).
- Revisit if: T-R7 LV-1 shows lever naming below 90% consistency across identical scenes.

### DL-00A-11: One severity scale; stakes with a separate lethal flag; reach as 0–4
- Decision: S1 Light / S2 Moderate / S3 Heavy / S4 Grievous / S5 Catastrophic, harm 1/3/5/8/12, unit magnitude 1/1/2/3/4, hazard effect DC by rung; stakes Safe / Risky (S2) / Dire (S3) with `lethal` legal only on Dire with `lethal_context` recorded beforehand (INV-6); reach Limited/Standard/Great framed, Zero/Exceptional computed; delivered reach feeds ticks, harm steps and delivery counts.
- Alternatives considered: a fourth stakes rung "Deadly" (conflates magnitude with lethality); R7's words "standard/severe" (collide with common adjectives; the rung names are distinct and mapped).
- Evidence: [R7 §4.2–4.3]; [R6 §C.3 C-R1]; [R3 §6 #9]; [BRIEF A2 #2–3, #8]; 5e DMG damage severity [R7 §2.8].
- Serves: goal 2 (one ladder the DM learns once); telegraphed death (BRIEF §4).
- Revisit if: T-00-PACE shows harm values produce fights outside 4–7 rounds at equal bands.

### DL-00A-12: The time ladder, time modes, and the boundary registry
- Decision: round 6 s → interval 10 min → hour → watch 6 h (morning/afternoon/evening/night) → day (dawn to dawn) → week → season (13 weeks) → year (364 days); event boundaries (beat, turn, conflict, scene, rests, reflection, venture, session, mode change); five time modes fixing time per beat; a registry of handlers with nine phases; skipping time runs every boundary crossed; interrupts halt the skip. The 10-minute unit is named *interval* so that *turn* keeps its natural meaning (an actor's turn in a round).
- Alternatives considered: R5's "turn" for 10 minutes (collides with combat turns); midnight day boundary (splits the night's rest across two days); real-time elements (meaningless in async text play).
- Evidence: [R5 §3.1–3.3, TM-01, TM-02, TM-11]; [R1 §00.B temporal errors dominant, G-19]; [R6 §B.3 B-R1].
- Serves: goal 2 (the world never freezes; temporal claims computed); goal 1 (skips are safe).
- Revisit if: T-00-SITE shows the interval-per-beat cadence mis-paces sites.

### DL-00A-13: One tag vocabulary with ten facets
- Decision: facets deed, conduct, creature, harm, material, item, terrain, situation, trait, org; one hierarchy with cascade and most-specific-wins; stewards per facet, 03 owns the file.
- Alternatives considered: separate vocabularies for evidence, loot and rules (needs translation tables; breaks "an adversary's nature gates loot and evidence"); a single flat list (no cascade).
- Evidence: [R3 §00.3–00.4, §03.1–03.3]; [R1 §00.D tags as retrieval keys]; [C:P5].
- Serves: goal 2; C:P5.
- Revisit if: 03 finds a recurring need for a tag that belongs to two facets (then add an alias mechanism, not a second tree).

### DL-00A-14: Nine deed branches are the calling axes
- Decision: martial, guile, wilds, lore, arcane, divine, primal, influence, craft; hybrids key only on distinct branch pairs (≤ 36); athletics under martial; magic split by source (study / granted / living world).
- Alternatives considered: six broad branches (loses magic-source and craft identities); twelve (66 pairs; untractable hybrid table); magic as one branch (cleric, druid and wizard indistinguishable to recognition).
- Evidence: [R3 §03.6 (single-digit keys), §6 #4–5]; [C:P5 curated sparse hybrid table]; [R1 G-25 archetype coverage].
- Serves: goal 1 (every classic archetype is reachable); goal 2 (low-cardinality keys).
- Revisit if: 04's coverage audit finds an iconic archetype unreachable.

### DL-00A-15: Conduct as ten signed axes
- Decision: mercy, honesty, courage, loyalty, generosity, justice, humility, restraint, piety, protection; evidence carries ±1; tallies net; oaths, shadows and the Fraying key on them.
- Alternatives considered: unsigned virtue tags with separate vice tags (doubles the vocabulary; loses the atonement arithmetic); Stormlight's twenty attributes (too many overlapping axes).
- Evidence: [R2 #6]; [R6 §A.2.2, §A.6 R-A6, V14]; [C:P5 values-expressive evidence].
- Serves: goal 1 (values matter mechanically); goal 2 (a signed counter, not a mood).
- Revisit if: 03 shows two axes consistently co-scored (merge them).

### DL-00A-16: The composition substrate
- Decision: one effect table (`effects.yaml`, core library seeded by 00); 29 closed hooks; 20 closed operations; one evaluation pass E0–E7; modifier families with fixed stacking; one-copy rule (INV-13); no percentages.
- Alternatives considered: pairwise interaction rules (O(n²) and exception chains, which fail systematically); per-chapter effect vocabularies (drift).
- Evidence: [R3 §00.1, §00.5–00.8, §6 #2]; [R4 §3.3 W14 (exception-chain collapse)]; Diablo II ItemStatCost, Slay the Spire hooks, Isaac cache [R3 §2B].
- Serves: goal 1 (novel combinations resolve by rule); goal 2.
- Revisit if: T-00-DEPTH or ch.05 authoring finds mechanics no core effect can express at a rate above 10% of entries.

### DL-00A-17: Four regimes, full suppression, and a one-link recursion terminator
- Decision: additive / independent trigger / priority-exclusive / named composite; a priority-exclusive loser is fully suppressed (including numbers) unless `cosmetic_merge`; ties to the earlier-acquired; hook subscribers fire only on depth-0 events; core rules ignore depth.
- Alternatives considered: RoR2-style proc coefficients (probabilistic chains; harder to audit in text); allowing depth 2 generally (loops become possible via clocks and conditions).
- Evidence: [R3 §05.4–05.5, §00.8]; Isaac Technology + Brimstone [R3 §05.4]; [C:P6 companion mechanism].
- Serves: goal 2 (no chain adjudication ever); goal 1 (designed combos still work via composites).
- Revisit if: T-00-DEPTH shows > 5% of intended synergies need a second link.

### DL-00A-18: One gate→fill generator for six domains, with no character bias
- Decision: loot, craft, gift, item_ability (08), absorb (04), birth (02) run one algorithm: pool gate by tags → tier cap by band → quality rung → fill method (signature / biased / chosen / weighted / recipe) → Greater / Flawed by degree → slot-by-slot fill with mod-group exclusion → recency halving → fixed magnitudes → caps → output with log. Content only from resolved outcomes. No smart-loot bias toward the recipient.
- Alternatives considered: per-domain generators; smart loot (a third axis P5 does not name; locks players into their current calling); variable property counts (less legible).
- Evidence: [C:P5 sixth pass]; [R3 §08.1–08.9, §6 #1, §4 T-9]; [R: src/ability_pool.py]; D3 Loot 2.0 and BL3 locked pools [R3 §08.8].
- Serves: goal 2 (the DM classifies, the tool computes; F003 6/6); goal 1 (chosen fills give relevance by player choice).
- Revisit if: T-00-VARIETY shows repeats above 15%, or playtests show loot feels irrelevant (then consider a player-chosen bias fill, never an automatic one).

### DL-00A-19: License schema, the fifteen basic verbs, gate classes, stretch and emulate
- Decision: every capability beyond the basic tier is a License with positive scope, excludes, crude fallback, acquisition paths, optional grades, principle, stretch and emulate; the basic tier is R7's fifteen verbs (closed) plus free activities; Yield and Retreat are named uses of Talk and Move; gate classes G0–G4; rolls never grant licenses; literal reading with beat splitting.
- Alternatives considered: an open "similarly mundane actions" tier (the leniency channel); licenses without fallbacks (walls, violating goal 1 and P16).
- Evidence: [C:VII]; [R7 §4.0–4.4, F4–F5]; [R2 #4 governing principle and stretch]; GURPS defaults, PF2e trained-only, DW Ritual, 3.5 UMD [R7 §2].
- Serves: goal 1 (refusals are redirects with a path); goal 2 (a lookup, not an invention).
- Revisit if: T-R7 AN-1 shows gate-class agreement below 80%.

### DL-00A-20: The clock primitive with per-tick omens and a racing tie rule
- Decision: one clock (sizes 4/6/8/12; public / sensed / hidden; tick sources fixed per clock; auto ticks and decay per boundary; completion effects as depth-0 processes; links; tug). Every tick of a non-public clock renders one omen of its stage (stirring / building / imminent); imminent-and-lethal raises the lethal warning. On a simultaneous completion, the acting side's delivered reach completes first.
- Alternatives considered: omens only at thresholds (a hidden clock could advance several ticks unperceived, breaking the telegraph lock); free tick amounts (the leniency channel).
- Evidence: [R: https://bladesinthedark.com/progress-clocks]; [R5 §5.2 #4]; [R6 §B.3 B-R5]; [R4 §4.3 clock row]; [BRIEF A2 #11].
- Serves: goal 1 (threats are legible); goal 2; BRIEF §4 telegraphed death.
- Revisit if: T-00-OMEN shows omens rarely perceived.

### DL-00A-21: Condition schema, closed stacking vocabulary, reserved ids
- Decision: one Condition schema (00.9.1); six stacking rules (unique, refresh, replace_stronger, intensify, independent, escalate); exclusion groups with ranks; neutralizing opposites; diminishing returns for control; 23 reserved condition ids ch.06 must define. Harm states are not conditions.
- Alternatives considered: free-text statuses (HWFWM's ~35 untracked statuses); leaving ids to 06 (parallel authors would invent incompatible ids).
- Evidence: [R2 §00 status registry, #3]; [R3 §06.7 CC diminishing returns]; [R4 §9 06 #5].
- Serves: goal 2; BRIEF §4 (no stun-lock deaths).
- Revisit if: 06 needs a stacking behavior not expressible by the six (amend here).

### DL-00A-22: Typed state model with four visibility classes
- Decision: eighteen state types (entity, quantity, flag, fact, relationship, position, knowledge, clock, condition, license, effect_instance, tally, ledger, commitment, offer, time, frame, meta); sealing applies to any; P3's binary classification refined to shown / available / background / sealed; single owner per state family; write-on-mention with undetermined properties settled by the Oracle; assertions never facts.
- Alternatives considered: the current five categories in `src/world_state.py` (no knowledge, time, sealing); vector memory as truth (updated-fact accuracy collapses to 0.30–0.95).
- Evidence: [R1 #1, §00.A–00.B; MERIT figures]; [R4 §5 (Hangman, leakage)]; [C:P3, P13]; [BRIEF A3 P3 classification].
- Serves: goal 2; C:P3; C:P7 (the codex renders the classes).
- Revisit if: T-00-WOM shows narrated-but-unrecorded above 2%.

### DL-00A-23: The tool surface replaces the current five tools
- Decision: 34 tool contracts in six groups with ten runtime capabilities; `roll_check` requires a committed frame; `get_state` filters sealed content; `generate` and `grant` replace `grant_ability`.
- Alternatives considered: extending the current tools minimally (keeps free integers and no sealing).
- Evidence: [R4 §9 00 #4]; [R3 §00.11–00.12]; [R2 §00 tool classes]; [R: src/tools.py; R: src/world_state.py].
- Serves: goal 2; C:I, C:P13.
- Revisit if: implementation shows a tool whose inputs still require the DM to supply a number.

### DL-00A-24: Rule cards, a small always-loaded core, the anchor index, the ruling ledger
- Decision: every numbered rule compiles to a card; only the turn checklist, invariants, gate classes and the stakes/reach/lever card are always loaded; the anchor index is compiled by 12; rulings are ledger records with signatures and precedent reuse.
- Alternatives considered: loading whole chapters (distractor effect); precedent in model memory (inconsistent across runs).
- Evidence: [R4 §3.3 W12–W13; R: https://arxiv.org/abs/2412.08972]; [R7 §4.8, F9]; [R5 G-13]; [BRIEF A3].
- Serves: goal 2; C:III (the ledger records concrete cases for the revisit trigger).
- Revisit if: T-R4-06 ("Loop drift") shows core compliance decaying before turn 50.

### DL-00A-25: One hard ability ceiling in three partitions
- Decision: calling / acquired / equipped partitions summing to one hard total (envelope 12–24, reference 20 = 12 + 4 + 4); items grant at most one active ability each, only while equipped; passive item properties use the item-layer budget, not slots.
- Alternatives considered: items outside the ceiling (the ceiling leaks); items inside the calling slots (items crowd out callings, D3's launch problem).
- Evidence: [R3 §4 T-12, §05.1]; [C:P5 hard total-slot ceiling]; HWFWM 20 [C:V].
- Serves: C:V; goal 1 (items still matter).
- Revisit if: ch.05/08 simulation shows a partition always empty or always full.

### DL-00A-26: Exactly one meta-currency, `fate`
- Decision: `fate` 0–3, owned by 01 (earning, resolution uses), consumed by 07 for the last-chance reprieve; no other spendable luck currency.
- Alternatives considered: separate reprieve and luck tokens (two currencies for one idea); none (loses the reprieve option in R6's last-chance menu).
- Evidence: [R5 RS-18, G-14]; [R6 §C.3 C-R3 option 6]; [BRIEF A1 01 "luck/fate currency decision"].
- Serves: goal 1; BRIEF §4.
- Revisit if: ch.01's DL decides fate has no resolution use at all (it then remains a reprieve-only token under the same id).

### DL-00A-27: One standing scale for NPCs and factions
- Decision: −3…+3 (Hostile … Devoted) for NPC disposition, faction status and signed relationships; moved only in steps; starting standing rolled.
- Alternatives considered: a 5-rung disposition plus a separate faction scale (two scales for one relation; members of a faction would need a translation).
- Evidence: [R6 §B.3 B-R2 (Blades status −3…+3)]; [R7 §4.2 disposition ladder]; [R4 §3.3 W4].
- Serves: goal 2.
- Revisit if: ch.15 needs finer social granularity (add clocks, not rungs).

### DL-00A-28: Aligned power and threat bands
- Decision: five PC power bands (from recognized tiers, 04) and five threat bands (09) on the same rungs; the band sets loot tier caps; advisories by band difference feed the lethal warning.
- Alternatives considered: character levels (forbidden by C:P2); a single scalar power number (fails action-economy budgeting; CR's documented failure).
- Evidence: [R2 #11, §4 T-5]; [R3 §08.4, §09.2, §09.8]; [R4 §6.3].
- Serves: goal 2; BRIEF §4 (lethality is advised before it happens).
- Revisit if: ch.09 finds bands insufficient to separate solo-encounter difficulty (add count modifiers in 09, not more bands).

### DL-00A-29: Fixed harm magnitudes, no damage dice
- Decision: harm is a severity rung converted to a fixed number; variance comes from the degree (reach steps, crits), edges, and the number of exchanges.
- Alternatives considered: damage dice (extra variance where the lethality lock needs predictability; OFFER previews become ranges).
- Evidence: [R3 §07.5 (discrete severity passed as a tool argument)]; Blades harm levels, Ironsworn fixed harm [R7 §2.2, §2.5]; [BRIEF §4].
- Serves: goal 2; telegraphed death (exact previews).
- Revisit if: T-00-PACE shows fights feel samey (then 06 may add degree-keyed severity steps, never dice).

### DL-00A-30: Precedence of rules and of concerns
- Decision: a flat first-match rule precedence (constitution → 00 invariants → state-family owner → license scope → data over prose → precedent → less-granting reading) and a concern order (safety → state truth → rules integrity → intent fidelity → fairness → pacing).
- Alternatives considered: "specific beats general" as a free principle (invites nested exceptions); no agenda order (the AI has no tie-breaker).
- Evidence: [R5 FN-04]; [R1 §4 T-7, T-14]; [R4 SG-10].
- Serves: goal 2.
- Revisit if: the ruling ledger accumulates `rule_conflict` records between two chapters (fix the chapters, then this list if needed).

<!-- ===== assembled at integration from appendix/fragments/ (do not edit below; edit the fragments) ===== -->

## DL-01 — Resolution

### DL-01-01: Keep the reference DC ladder (Easy 10 / Moderate 15 / Hard 20 / Very hard 25 / Legendary 30)
- Decision: the 00 reference ladder is confirmed unchanged; stored in `resolution.yaml#dc_tiers` and `scales.yaml#obstacle_tiers`.
- Alternatives considered: every ascending ladder within ±2 per rung (3,125 candidates, exhaustive d20 enumeration, scratchpad `odds01.py`). 324 satisfy CT-1…CT-6; feasible values Easy 8–11, Moderate 14–16, Hard 19–21, Very hard 24–26, Legendary 29–31. Moving any rung except Easy by ±2 breaks a target (Moderate→CT-2, Hard→CT-3, Very hard→CT-4, Legendary→CT-5); Easy +2 breaks CT-1. Easy 9 is feasible but buys +5 points on trivial-adjacent tasks at the cost of a non-round number; no evidence asks for it (OEQ-01-2).
- Evidence: 01 T-01-3 and its calibration proof; 00.3.17; [R4 §3.4] (the old harshness came from missing competence, DL-00A-05); PF2e simple DCs by proficiency (https://2e.aonprd.com/Rules.aspx?ID=2628).
- Serves: goal 2 (stable, round, AI-holdable numbers; 5-point rungs = 2.5 Precision levers); goal 1 (honest odds).
- Revisit if: LAD-1 shows ≥ 30% of untrained Easy attempts felt "should have worked" while CT-1 holds.

### DL-01-02: Confirm the one-step natural 20/1 shift
- Decision: base degree by margin (±10 bands); natural 20 one step up, natural 1 one step down; ties go to the actor.
- Alternatives considered: the old "nat 20 always critical success / nat 1 always critical failure" (BRIEF §7) — rejected: 5% critical miracles at unreachable DCs (+2 vs 25), 5% critical failures of certain successes for experts (+12 vs 10).
- Evidence: [R7 §5.9, §7.1 #1]; [R1 01.A, T-4]; [R2 01, #7]; [R4 §9 01 #5]; PF2e degrees (https://2e.aonprd.com/Rules.aspx?ID=2286).
- Serves: goal 2 (no permissive miracles; VII direction), lethality lock (no expert death-by-nat-1).
- Revisit if: playtests show "only a natural 20" OFFERs discourage legitimate long shots (then consider nat 20 = success at framed reach, already the case).

### DL-01-03: Near miss = failure with margin ≥ −3, including a natural 1 that stepped a success down
- Decision: `near_miss` true when the final degree is failure and margin ≥ −3; the player may take success at a cost.
- Alternatives considered: 00's "1–3 below the DC" only (leaves an expert who met the DC with a nat 1 no recourse); −2 (5e DMG); −5 (makes failure feel rare, 25% band).
- Evidence: [R7 §4.3, §7.3 NM-1]; Fate ties (R1 M-02); Blades 4/5 partials (R3 01.3); PbtA 7–9.
- Serves: goal 1 (anti-stall, P16), goal 2 (deterministic).
- Revisit if: NM-1 (OEQ-01-1). Interface request to 00 filed (00.3.10 wording; T-00-6 near-miss cells for +8…+16 vs low DCs become 5).

### DL-01-04: Exactly one cost per beat; critical failure +1 rung; Safe critical failure costs S1
- Decision: T-01-5. Safe F none / NM S1 / CF S1; Risky S2/S2/S3; Dire S3/S3/S4. No beat pays two costs.
- Alternatives considered: R7's "Dire CF = one severe + one standard" — rejected: two decisions and two writes for one roll, and S4 (8 harm) already exceeds S3+S2 (5+3); Safe CF = S2 (R7) — rejected: breaks Safe's promise.
- Evidence: 00.3.14 (`critical_failure_step: 1`); [R4 SG-09]; [R7 §4.3].
- Serves: goal 2 (one pick, one form, one write), lethality lock (S5 never from a single roll).
- Revisit if: playtest finds Dire critical failures feel toothless (SOFT-1 logs).

### DL-01-05: Stakes and reach are set by yes/no flags, not holistic rungs
- Decision: stakes = SOURCE flag (closed source list) then HEAVY flag (closed list of S3 sources), tie-break toward the higher rung; reach = WHOLE flag then ONE-FACTOR flag, tie-break toward Limited; Great is never picked, only reached by an Amplifying fact, an effect/license step or the trade; in conflict, a failure that is only the foe's ordinary turn is Safe.
- Alternatives considered: picking stakes/reach as 3-rung ladders (00's `[J:rung]` framing) — kept as the output, but decomposed into flags per SG-03 because binary judgments agree ~87% vs 38–58% exact on ladders.
- Evidence: [R4 SG-03, §4.1]; [R: https://arxiv.org/abs/2603.00077]; Blades position/effect factors (R7 §2.2).
- Serves: goal 2; goal 1 (the higher stakes rung is the honest telegraph, shown before commitment).
- Revisit if: AN-1 agreement on stakes < 85%.

### DL-01-06: The fate economy
- Decision: start 1, cap 3; earn by hard luck (CF on the PC's Risky/Dire frame, once per scene, never above 2), thread completed, vow kept; spend 1 to reroll a seen d20 by or against the PC (one per roll; not secret frames, Oracle, tables, generators, others' fortune rolls); `spend_fate(n)` for ch.07's last-chance options (`fate_cost` 1–3).
- Alternatives considered: fate to buy a degree step (too strong; bypasses odds shown in the OFFER); fate to create facts (the sycophancy channel; rejected); Ironsworn-style momentum meter (a second scale to track); earning per session (real time never matters).
- Evidence: R5 RS-18/P-15 (momentum), R6 C-R3 item 6 (reprieves earned back by great deeds), PF2e hero points, WFRP fate (R6 C-17); 00.17.1 Q9.
- Serves: goal 1 (a comeback valve), lethality lock (a scarce, visible reprieve).
- Revisit if: FATE-1 (OEQ-01-7) shows mean fate at a lethal brink outside 1.0–1.5.

### DL-01-07: The threatened cost (and an alternate) is declared at FRAME
- Decision: every rolled frame names a threatened menu entry; Risky/Dire frames also name an alternate; success-at-cost lets the player choose between them.
- Alternatives considered: choosing the cost after the roll (the post-hoc softening channel, W3).
- Evidence: Burning Wheel's stated failure, 7th Sea's announced consequences, Blades position (R7 §3.3 F8); [R4 SG-08, §6.2 #2].
- Serves: goal 2 (anti-drift), goal 1 (the player knows the price).
- Revisit if: SOFT-1 (OEQ-01-8) shows declared costs poorly fitting in > 10% of frames.

### DL-01-08: The repeated-attempt shape: engine snags 0 / −2 / −4 per window
- Decision: k-th instance in a window carries k−1 engine-applied Precision snags (max two), outside the two-cited-snag limit, inside the ±4 cap; conflict window = the turn, counting every `trait.action.attack` beat regardless of target; ch.06 may set any non-increasing sequence inside −4. Quantity never raises the DC.
- Alternatives considered: PF2e's −5/−10 (exceeds the ±4 circumstance cap and would need a sixth modifier family — an amendment to 00); counting repetition against the two-snag limit (a dark room's third attack would be no worse than its first).
- Evidence: [R1 01.C, M-06]; [R7 §5 Ex.7] (the probe's DC-25 ruling ~16× harsher than the fiction: 5% vs 79%); 00.3.9.
- Serves: goal 2 (P9: one declaration is not many effects); goal 1 (repetition stays a real option).
- Revisit if: REP-1 (OEQ-01-9). Interface request to 00 (00.3.9b clarification) filed.

### DL-01-09: Take the time
- Decision: uncertain-but-not-costly beats succeed at Standard reach for twice the mode's time; never for Very hard or Legendary.
- Alternatives considered: always roll (wastes rolls where failure costs nothing and trains fishing); "take 20" at any tier (lets patience beat expertise).
- Evidence: 5e take 20 / PF2e lineage (R7 §2.8); Dogs in the Vineyard "say yes" (R7 §2.19).
- Serves: goal 1 (no pointless rolls), goal 2 (time still passes through every boundary, INV-15).
- Revisit if: players use it to bypass encounter checks (then raise the multiplier).

### DL-01-10: Group actions are one roll: all-must → lowest modifier, any-may → highest
- Decision: 01.14.7; at most one Help lever; cost lands on the member whose modifier was used unless another engaged its source.
- Alternatives considered: 5e "half the group succeeds" (multiple rolls, compounding); rolling per member (more rolls, harsher, W1 bookkeeping).
- Evidence: 5e group checks (R7 §2.8); Blades group action (R7 §2.2); solo reinterpretation (BRIEF A3).
- Serves: goal 2 (one die), goal 1 (companions matter through Help).
- Revisit if: companions (16) are routinely left behind because their modifier drags group rolls.

### DL-01-11: Oracle answer shape — six outcomes on one d100
- Decision: Ironsworn thresholds kept (26/51/76/91); doubles 11…99 and 100 (10 faces) = "and" (extreme, the "and" rolled on 12's meaning table); 5 faces either side of the threshold = "but" with closed qualifier lists (yes-but: lesser/costly/elsewhere/noticed; no-but: substitute/trace/adjacent); tie between rungs → the rung less favorable to the asker's evident hope.
- Alternatives considered: Mythic chaos factor on every roll (12's tension dial covers it with a one-rung shift); binary answers only (no generative "but").
- Evidence: [R7 §4.7]; R5 P-01, P-02, P-03 (Kal-Arath six-way shape); [R4 S5, W6]; https://ironsworn-rpg.fandom.com/wiki/Ask_the_Oracle.
- Serves: goal 1 (the player may go looking for affordances and get fair answers), goal 2 (odds before rolling; anti-sycophancy tie-break).
- Revisit if: OR-1 (OEQ-01-4) shows odds moving with player desire.

### DL-01-12: `deliver_count(N, reach)`: 1 → max(1,⌊N/3⌋); 2 → ⌈N/2⌉; 3 → N; 4 → N + bonus
- Decision: T-01-6; failure = one vague (true) impression; critical failure = nothing, or one small, correctable falsehood only when the source can mislead; N capped at 5 after deduplication; sealed-behind-gate items ineligible.
- Alternatives considered: R7's Limited ⌊N/2⌋ / Great N−1 (Limited and Standard coincide at N = 2–4; Great withholds from an earned success).
- Evidence: [C:P17]; [R7 §4.5]; Blades gathering information; Dungeon World Discern Realities (R7 §2.4); PF2e Recall Knowledge crit failure (R7 §2.9); [R1 01.D] (never beyond the permitted slice).
- Serves: goal 1 (graduated delivery, player ranking), goal 2 (count computed).
- Revisit if: players feel Limited delivers too little at N = 4–5.

### DL-01-13: Secret frames and the sealed Oracle
- Decision: Observe/Recall/Talk-to-read beats whose target is sealed or undetermined roll secretly: the OFFER shows modifier, stakes, reach and cost but not DC, odds or die; existence questions are asked of a sealed Oracle; fate cannot be spent on them; frames become available once unsealed.
- Alternatives considered: all rolls visible (a failed search then leaks "something is here").
- Evidence: R5 RS-12 ("name it"); [R4 §5]; PF2e secret checks; R1 G-24.
- Serves: goal 2 (sealed state stays sealed, INV-10); goal 1 (the decision information is still shown).
- Revisit if: players report secret frames as untrustworthy (then show the modifier-vs-tier band).

### DL-01-14: The ambition and caution trades
- Decision: once per beat, before commit, the player may go big (stakes +1, reach +1) or play it safe (both −1), pure player choice, clamped.
- Alternatives considered: DM-offered devil's bargains (DM judgment, drift).
- Evidence: Blades trading position for effect (R3 01.2, #9); R7 §2.2.
- Serves: goal 1 (ambition as a player lever), goal 2 (no judgment).
- Revisit if: go-big trades into lethal frames are taken without reading the re-shown OFFER.

### DL-01-15: The cost menu's forms and writes
- Decision: 01.13 / `resolution.yaml#cost_menu`: nine entries, each with fits-when, forms and exact writes per S1–S5; time by mode table; exposure's alertness ladder; gear's damaged/broken states; closed door's standing steps; twist through `tbl.twist` by severity; costs must land in full; selection order already-threatened → most-engaged → not-repeated → twist.
- Alternatives considered: free-form costs (W3 softening); a d100 complication table on every failure (loses the method's fiction).
- Evidence: [R7 §4.3]; Blades consequences; Ironsworn Pay the Price (R5 P-16); [R4 SG-09].
- Serves: goal 2; goal 1 (costs follow from the method, so they read as fair).
- Revisit if: one entry exceeds 40% of all costs in playtest logs (variety failure).

### DL-01-16: Let it ride as an engine ride record, with a priced re-attempt
- Decision: 01.4.2; a ride ends on a new approach, a new lever fact, a superseded cited fact, the interval passing, or the re-attempt cost (one time or exposure cost at the stakes severity, S1 if Safe, paid up front).
- Alternatives considered: free retries (compounds odds, teaches fishing); never retrying (walls).
- Evidence: the Alexandrian "let it ride"; Year Zero no-retry (R7 §2.13); [C:P17] no-free-retry; R5 P-46.
- Serves: goals 1 and 2.
- Revisit if: re-attempt costs are paid on > 30% of failures (the price is too low).

### DL-01-17: The Good Idea rule is three flags with hard bounds
- Decision: removes the source (not merely helps) + unopposed + bounded (Safe/Risky, not lethal, no license, no unseal, no generation, no standing change, ≤ 2 ticks); default false.
- Alternatives considered: Torchbearer's unbounded "clever solution" (the leniency channel).
- Evidence: [R7 §2.15]; [R4 SG-05; CoC-Seduce false-pass 9.58% vs false-check 0.08%].
- Serves: goal 1 (clever plans win without dice), goal 2 (bounded, logged).
- Revisit if: SED-1 shows Good Idea used as the false-pass route.

### DL-01-18: G4's tie-break is the one that favors the attempt
- Decision: uncertain G4 tests → false (roll at an honest tier) — the only pro-attempt tie-break in the chapter.
- Alternatives considered: SG-05's "no" everywhere (would make "impossible" the lenient-to-the-DM wall goal 1 forbids).
- Evidence: [R7 §3.3 F4]; BRIEF §3 goal 1.
- Serves: goal 1; goal 2 is protected because a wrongly allowed attempt must still beat the dice.
- Revisit if: AN-1 shows G4 under-called for canon impossibilities.

### DL-01-19: The sensitive-upgrade test gates G1
- Decision: a beat giving more perception, memory, mobility, control, access, awareness or freedom than an ordinary person has is not G1.
- Evidence: NCP-Bench auditor list [R1 01.B, #4].
- Serves: goal 2 (the dimensions where generous narration produces impossible outcomes).
- Revisit if: ordinary acts are sent to G3 in > 5% of AN-1 cases.

### DL-01-20: Three beats per declaration; bundles of at most five
- Decision: 01.2.3, 01.10.2.
- Evidence: Story-Engine action-unit cap and WoW global cooldown (R3 01.7; R4 §9 01 #7).
- Serves: goal 2 (decision points), goal 1 (queued, not refused).
- Revisit if: players find queuing tedious in non-conflict scenes.

### DL-01-21: Stored DCs are keyed by obstacle and anchor signature
- Decision: `dc.<obstacle>.<anchor>[+dc:<delta>]` — a climb and a vault of one wall keep separate DCs; a stored DC changes only when a fact changes the obstacle.
- Evidence: [R7 §5 Ex.5, §3.3 F2]; anchor property 6 (00.2.6).
- Serves: goal 2 (consistency across attempts and sessions).

### DL-01-22: Reach overflow becomes one follow-up Precision lever
- Decision: an unusable delivered rung (at most one) becomes `momentum.<actor>.<target>`, expiring after the next beat or at scene end.
- Evidence: R7 §4.3 (beyond Great → a free lever); Ironsworn strong-hit momentum (R3 01.6).
- Serves: goal 1 (critical successes always mean something).

### DL-01-23: A default degree table for resisted effects
- Decision: 01.18.3 (CS no effect + lever; S no effect; NM success at cost from a different entry; F the effect; CF the effect +1 rung); stakes from the effect's severity; sources with their own staged tables override.
- Evidence: 00.3.3; PF2e saving-throw degrees (as adapted); R6 C-R1.
- Serves: goal 2 (07/10 afflictions and hazards plug in without new judgment).

### DL-01-24: Help is one Precision lever, at most one per beat, only from an eligible helper
- Decision: 01.14.8.
- Evidence: 5e working together (the helper must be able to do it alone); Savage Worlds support caps; Blades assist (R7 §2.7–2.8, §2.2).
- Serves: goal 2 (no lever stacking via crowds; crowds are Amplifying facts).

### DL-01-25: Lever and snag tie-breaks are asymmetric
- Decision: an uncertain lever is not applied; an uncertain fitting snag is applied, and an established fitting snag is obligatory.
- Evidence: [R4 SG-05, W2] (the error is directional: toward leniency).
- Serves: goal 2.
- Revisit if: LV-1 shows snags applied inconsistently (then add a snag checklist to the OFFER).

### DL-01-26: Free Oracle facts are capped as levers, not by bending the odds (revision I-038)
- Decision: 01.15.8: a free fact (an Oracle answer to a player's question; the oracle log names the asker, 01.15.5) is at most one lever per roll, a lever on at most two rolls per character per scene, and never the Protective lever that takes a lethal frame below Dire; past a cap it must be worked by a Setup (01.14.9). Narrated, generated, observed and DM-asked facts are unaffected.
- Alternatives considered: the ledger default, dropping the odds one rung per Oracle lever used (rejected: 01.15.2 sets odds from the world only and 12.6.3 keeps the dial off player questions; it would make honest world questions less true because the player asked others); capping questions per scene (rejected: punishes curiosity, not the bonus).
- Evidence: `01-oracle-fishing.py` (seed 38): no cap +3.66 a roll at three questions a roll, +3.99 at six; cap 2 gives +1.33 / +0.80 / +0.50 a roll over 3 / 5 / 8-roll scenes, flat in the number of questions; cap 1 +0.40 at five rolls (too stingy), cap 3 +2.0 at three rolls.
- Serves: goal 2 (no free +4 on every roll), goal 1 (the environment still pays when it is worked).
- Revisit if: playtests show scenes routinely longer than eight rolls with no environment levers (then three rolls a scene).

### DL-01-27: A total potency is two factors of zero reach (revision I-073)
- Decision: 01.3.7 test 3: POTENCY is total when the target cannot be affected by this kind of method at all (no mind for Talk or Handle, no body for Grapple or Strike) and counts as two factors; one reason supplies one factor; the barred gate shouted open is G4 with a redirect.
- Alternatives considered: listing "no mind" as a fifth G4 test (rejected: the factor list already holds it; only its weight was unstated).
- Evidence: verification-2c adversarial playtest S1 (literal DMs split between a roll at Limited and a G4).
- Serves: goal 2 (one reading for a literal DM).

## DL-02 — Character

### DL-02-01: Three paths through one procedure; the fast path is the default offered
- Decision: one ten-step procedure (02.1.2) with three paths: Fast (five answers, every other choice a recorded default), Full (every step), Ready-made (a chapter-13 pregen with a live birth draw). Every choice has a data default named before it is taken; "details", "why", "back", "surprise me", "just start" work at every step (02.2.2–02.2.3).
- Alternatives considered: one long procedure (choice paralysis, "game-halting" for a newcomer, R1 02); pregens only (no ownership; R5 §4 still wants a fast custom path); a cut-down rule set for beginners (forbidden: rules are sequenced, never coarsened, BRIEF A3).
- Evidence: [R1 02, #14, M-31 (Baldur's Gate 3 premade and custom)]; [R5 §4 items 1, 5, 6; CC-12]; Worlds/Stars Without Number "quick skills" (https://takeonrules.com/2018/07/09/lets-read-stars-without-number-character-creation/); https://bg3.wiki/wiki/Character_creation.
- Serves: goal 1 (a newcomer starts playing in minutes; depth is one word away); goal 2 (defaults are data).
- Revisit if: T-02-FAST misses its targets (median > 5 exchanges or > 6 minutes, or players ask rules questions before the first scene).

### DL-02-02: The P2 floor is confirmed at +1 at `deed`
- Decision: every PC holds competence +1 at the root `deed` for life (02.5.1).
- Alternatives considered: 0 (untrained PCs fall below CT-1/CT-2; a successor starts helpless); +2 (equals an origin's deep training, erasing the numeric value of depth and of P4's breadth/competence split).
- Evidence: [C:P2]; 00.3.6; 00.3.17 CT-1…CT-6 (computed on +1); 01 Interface request; [R1 02 "no creation path a trap"]; [R3 02.4].
- Serves: goal 2 (the ladder 00 calibrated holds); goal 1 (no character is helpless).
- Revisit if: chapter 01 moves a DC rung so that CT-1 or CT-2 fails at the floor.

### DL-02-03: Attributes are fixed arrays in three shapes; no point-buy of any kind
- Decision: six arrays (Free: +3,+2,+1,0,0,0,−1 / +2,+2,+1,+1,0,0,−1 / +2,+1,+1,+1,+1,0,−1, sum +5; Typical: +3,+2,+2,+1,0,0,−1 / +2,+2,+2,+2,0,0,−1 / +2,+2,+2,+1,+1,0,−1, sum +7). Every array has one −1 and at most one +3. The player chooses the shape and the placement; nothing is priced.
- Alternatives considered: audited bracket point-buy (P11 allows it, but arrays give the same freedom with zero audit surface); rolled attributes (offered only as "surprise me" over legal placements); flaw-for-points (forbidden: disadvantage gaming).
- Evidence: [C:P11]; [R1 02 point-buy verdict; R2 02 GURPS]; Mistborn Adventure Game strong/average/weak (https://en.wikipedia.org/wiki/Mistborn_Adventure_Game); Ironsworn 3-2-2-1-1 (https://en.wikipedia.org/wiki/Ironsworn).
- Serves: goal 2 (no arbitrage to police); C:P4.
- Revisit if: playtests show players want a shape the three do not offer (add a shape, never a pool).

### DL-02-04: P4 quantity-vs-freedom: each people's Typical rule (+7, three placements decided) or the Free rule (+5)
- Decision: a non-human people's Typical rule gives sum +7 with one floor of +2, one of +1 and one attribute fixed at −1; each attribute is exactly one people's fixed low. Humans always use Free (+5) and take one extra access training; any non-human may be "uncommon of their kind" (Free rule, keeps gift and tongues, no extra training). One small innate gift per non-human people.
- Alternatives considered: Typical at +6 (audit: worse than Free for 8–13 of 16 concepts for every people, i.e. a trap); peoples that fix the peak attribute (free lunch for aligned concepts; essentialist); no Free escape (closes the goblin priest and the orc scholar).
- Evidence: [C:P4]; [R2 02 The Land: humans 4 free points, others more with forced allocation; "only works if every option is calibrated to feel roughly equal"]; [R3 02.1]; Pathfinder 2e alternate ancestry boosts (https://2e.aonprd.com/Rules.aspx?ID=2079); audit T-02-3 (gen02.py A3: Typical better than Free for 4–11 concepts, worse for 5–12; mean premium −2.9…+1.9).
- Serves: goal 1 (every concept buildable at strength); C:P4; C:P11.
- Revisit if: T-02-P4 shows the Typical share outside 40–80% of non-human full-path creations.

### DL-02-05: Upbringings spend exactly three permanent units
- Decision: Focus 5 / 4 / 3 cost 2 / 1 / 0 units; an access license, letters, or a tongue cost 1 each; every upbringing spends 3; coin varies outside the budget.
- Alternatives considered: pricing coin (transient; would let wealth buy permanence); free upbringing packages (unaudited; P11).
- Evidence: [C:P4]; [C:P11]; [R1 02 HERO brackets]; 00.3.13 envelope 3–5.
- Serves: goal 2; C:P4 (inner reserve vs worldly knowledge, locked).
- Revisit if: T-02-FOCUS shows > 70% of Gifted characters choosing a Focus-5 upbringing.

### DL-02-06: Twenty-one livelihoods in place of a chosen class; four license magic
- Decision: the third origin is a past (livelihood) that sets a training list, kit and seeds, never a calling; Apprentice, Acolyte, Hedge-taught and Touched license magic with each license's `requires` satisfied (letters + spellbook + master; keeper + sign + faith at Warm; place + teacher; innate).
- Alternatives considered: class-like playbooks (a menu identity, contrary to P5); no magic at creation (fails 04's coverage audit and goal 1).
- Evidence: [C:P5]; [C:VII]; 04.2.7; 04 and 05 Interface requests; Blades heritage/background/playbook (https://bladesinthedark.com/character-creation); Burning Wheel lifepaths (http://rpgsystems.wikidot.com/burning-wheel).
- Serves: goal 1 (all 25 iconic archetypes pursuable from the first scene, T-02-12); goal 2.
- Revisit if: a playtest concept cannot be classified to any livelihood plus the off-list pick.

### DL-02-07: P4 breadth-vs-competence: four breadth profiles
- Decision: Focused (2 deep), Gifted (1 deep + 1 technique), Rounded (1 deep + 2 access), Broad (5 access). Deep = license + competence +2 + push eligibility; access = license only (rolls at the floor, no push). One pick may be off-list.
- Alternatives considered: a training pool (P11); a single fixed package per livelihood (no breadth dial at all).
- Evidence: [C:P4] (Mistborn Adventure Game: the all-access character starts mediocre, R2 02, #10); 05.6.7 (push only above the floor); 05.9.4.
- Serves: goal 1 (breadth is a real option); C:P4.
- Revisit if: T-02-BREADTH shows any profile under 10% or over 50%.

### DL-02-08: Birth variance at creation: one knack and one quirk from `gen.birth`
- Decision: the origins' birth_pool tags gate a pool of 81 knacks (by deed branch) and 22 quirks; manner of childhood (unremarked / hard / omened / gifted) selects weighted or biased fill; both results are permanent benefits, applied (P1's mandatory creation variance).
- Alternatives considered: random attribute variance at creation (feels unfair on a key attribute; R2 warns); per-skill affinity percentages (The Land; a second, hidden progression system); no layer (violates P1).
- Evidence: [C:P1]; [C:P5 pool gate / fill quality]; 00.11; [R2 02 The Land affinity, HWFWM awakening stones and racial gifts]; [R3 02.7]; [R4 §9 02 #2]; gen02.py A4.
- Serves: goal 1 (characters diverge; an invitation the player did not write); goal 2 (engine draw, logged).
- Revisit if: T-02-KNACK shows the knack does not change what players attempt.

### DL-02-09: The Touched: seven innate primal gifts via the signature slot
- Decision: the Touched livelihood draws a gift (innate primal school, competence +2, first working at rank 1) in `gen.birth`'s signature slot; named → that school, unnamed → equal draw among seven.
- Alternatives considered: the spark alone (narrows "born with it" to one school); random gifts for anyone (unequal power by chance).
- Evidence: 04.2.7 (Elementalist's start is a birth spark); 04 Interface request; [R2 02 HWFWM]; 05.9.4.
- Serves: goal 1; C:P1.
- Revisit if: 05 adds `min_tier: 1` workings for water and air (then let the spark's element be drawn).

### DL-02-10: Focus base is set by upbringing, not by any attribute
- Decision: base 3, 4 or 5 from the upbringing (02.7.2).
- Alternatives considered: flat 4 (wastes the envelope 00 gave); by attribute (forbidden, DL-00A-09); by profile (couples two P4 dials).
- Evidence: 00.3.13; DL-00A-09; 05.6.1.
- Serves: C:P4 (a locked, legible trade); C:P9.
- Revisit if: as DL-02-05.

### DL-02-11: The Bent is P1's post-creation variance, with a deferred reroll
- Decision: +1 to one attribute (never above +3), drawn after the creation window closes from attributes gated by deed branches with ≥ 3 resolved frames; offered with no default; the player accepts or defers (the attribute is struck), at most twice; the third draw is accept-or-forgo; spacing 2 reflections and 10 frames.
- Alternatives considered: unlimited rerolls (a wait, not a gamble); rerolls without striking; a creation-time attribute roll (P1 then has no post-creation half); weighting by sealed tallies (reads 03's sealed state; the frame log suffices).
- Evidence: [C:P1 "a deliberate departure from every source researched"]; 00.4.3 a; [R3 02.2 Diablo III enchanting]; [C:P5 history-gated]; T-02-11.
- Serves: goal 1 (the player controls the gamble); C:P1.
- Revisit if: T-02-BENT shows deferral under 15% or over 50%, or forgone over 10%.

### DL-02-12: Tongues with three grades, and Letters as a separate license
- Decision: nine setting-agnostic tongues (broken/accented/native, with a snag and reach cap at broken, a snag on subtle matters at accented) plus `lic.lang.letters`; Intellect gives learning picks (tongues, letters, lore access).
- Alternatives considered: universal literacy (removes the arcane `requires` and a classic texture); tongues as binary (no partial understanding).
- Evidence: 00.4.4 (Intellect → tongues or lore at creation); 05.9.4; 01.18 Talk fallback; WE-01-4.
- Serves: goal 1 (partial communication is playable); goal 2.
- Revisit if: chapter 13 finds the grades too coarse for its region.

### DL-02-13: Kits by item tag with hard limits
- Decision: two kits (upbringing pack + livelihood kit) as `{item_tag, quality, quantity}`; no item above `fine`, nothing magical, at most light armor, light/one-handed/bow weapons, one worn mount, no healing potion; free like-for-like exchanges.
- Alternatives considered: starting gold only (slows the start); gear packages with power (gear must not outclass the character).
- Evidence: 00.17.1 Q17; [R1 02]; [R3 02.6]; [R4 §9 02 #5]; 06 Interface request (light armor and a one-handed weapon or bow for martial origins).
- Serves: goal 2 (items exist with ids from turn one).
- Revisit if: 08's prices make any kit's value exceed another's by more than a factor of three in coin terms.

### DL-02-14: No evidence at creation (backstory evidence used only for trained successors)
- Decision: every origin's `backstory` is empty; tallies start at zero; the past is expressed as competence, licenses, facts, ties and prologue chronicle lines. 03.2.8 is used only when a predecessor completed chapter 11's Train-a-Successor activity in play.
- Alternatives considered: 03.2.8 for deep trainings (a small menu of calling; unresolved deeds as evidence).
- Evidence: [C:P5 "derived from what a character actually did"]; [C:P2]; 00.6.8 and 00.11.2 (only resolved outcomes); 04 pacing (first tier ~session 4 without seeds); DL-03-25 ("02 decides").
- Serves: C:P5; goal 2.
- Revisit if: T-02-FIRST shows a median first offer after session 5 for focused play.

### DL-02-15: A creation window with one "second look", locked at the first reflection
- Decision: until the first reflection (first long rest) the player may revise once, between scenes, any choice within the origins (not the origins, not birth results, nothing spent); then everything locks (P4).
- Alternatives considered: no revision (punishes newcomers' uninformed choices); unlimited respec (P4 trade-offs stop being real); a paid respec (a coin sink unrelated to the fiction).
- Evidence: [C:P4]; [R1 02 "a rage quit"]; Baldur's Gate 3 respec (https://game8.co/games/BG3/archives/421001).
- Serves: goal 1 (a newcomer can correct a mistake); C:P4.
- Revisit if: T-02-WINDOW shows use above 30% or uses timed to exploit a failed roll.

### DL-02-16: Base Vitality = 12 + Endurance
- Decision: 11–15 at creation, 10–16 over a lifetime's Endurance range, reference 12 at Endurance 0; band growth is 07's (DL-00-04).
- Alternatives considered: 10 + 2×Endurance (Endurance becomes a must-have); flat 12 (Endurance feeds nothing, against 00.4.4).
- Evidence: 00.3.12; 00.4.4; DL-00-04; 07.1.2; sim02 (Vitality 11–15 lines).
- Serves: goal 2 (exactly fills the envelope).
- Revisit if: T-00-PACE or T-02-FIRSTFIGHT shows Endurance dominating build choices.

### DL-02-17: Ties: drive (want or creed), two bonds (anchor, thorn), tagged aspirations, the one true thing, faction-tie brackets
- Decision: the drive is classified want (long vow + thread) or creed (invariant commitment); bonds have fixed kinds and set standings; aspirations carry ≤ 2 tags and never weight evidence; the one true thing is checked for CAPABILITY and WORLD (a world claim becomes a belief with an Oracle-sealed truth); ties are none / +1 / (+2, −2).
- Alternatives considered: icon-style points (a pool); free-text distinctive with power (a license by the back door); rolled bond standing (a bond is not a first impression).
- Evidence: [R1 M-28 13th Age One Unique Thing and icon relationships (https://roll20.net/compendium/13thage/Rules:Creating%20Characters)]; [R1 M-30 Dungeon World bonds]; Blades friend and rival; [R5 CC-04, CC-08–CC-10, P-40, P-46]; 04.6.5; [C:VII]; SG-05, SG-06.
- Serves: goal 1 (the world has handles on the character); goal 2 (no capability enters through prose).
- Revisit if: the true-thing flags disagree across runs (add to T-02-CONCEPT).

### DL-02-18: Open slots, filled later only out of fiction and away from the current scene
- Decision: thorn bond, true thing, faction tie and (unless stated) aspiration may stay open; filled at a reflection or session start, creating new entities one scene away; one reminder per session at most.
- Alternatives considered: defaults for everything (puts an aspiration where the player never pointed); filling mid-scene (the slot becomes a lever).
- Evidence: [R5 §4 item 6]; Dungeon World "leave blanks"; SG-06.
- Serves: goal 1 (fast start without lost depth).
- Revisit if: players never fill open slots (then prompt at the first reflection instead).

### DL-02-19: Creation captures the first preference check-in
- Decision: C0 asks path, newness, the six pillars (more/same/less) and, on the full path, the pacing profile, recorded through 14's preference record; nothing changes a number.
- Alternatives considered: leaving all preferences to 14's session zero (misses the moment the player describes what they want).
- Evidence: [R1 02 Robin's Laws, session zero]; 12.5.9; 12.9.3.
- Serves: goal 1.
- Revisit if: T-12-ROT shows creation's weights poorly predict later check-ins.

### DL-02-20: Successors start at the floor; inheritance arrives as ties and things
- Decision: 02.2.7 (fresh creation, known candidates fix recorded origins, heirloom outside kit limits, legacy as hooks and bonds, backstory evidence only from Train-a-Successor, fresh birth draw with recency).
- Alternatives considered: inherited competence or attributes (no structural retirement, C:VI).
- Evidence: [R6 §D.3 D-R4, D-R5]; 04.11.4; [C:VI].
- Serves: C:VI; goal 1.
- Revisit if: 11's legacy procedure needs a different hand-off.

### DL-02-21: A described concept is classified by branch, then livelihood, with a two-way offer when unsure
- Decision: 02.2.4 (`[J:enum]` level by level; people and upbringing only when named).
- Alternatives considered: a 21-way flat classification (overlap raises error); inferring people from names (an unearned fact).
- Evidence: [R4 §3.2 S1]; 00.5.2; [R5 §4 item 6 Cypher's one sentence].
- Serves: goal 2; goal 1.
- Revisit if: T-02-CONCEPT agreement < 90% on branch.

### DL-02-22: Three origins, one of each (people × upbringing × livelihood)
- Decision: 8 × 9 × 21 combinations, none forbidden; each kind sets a disjoint part of the record (02.4.1).
- Alternatives considered: one origin entry per concept (combinatorial authoring; less freedom); lifepath chains (Burning Wheel: rich but long, and invites age/skill arbitrage).
- Evidence: Blades in the Dark creation (https://bladesinthedark.com/character-creation); Burning Wheel lifepaths (http://rpgsystems.wikidot.com/burning-wheel); Traveller careers (https://www.traveller-srd.com/core-rules/careers/); [R1 M-30]; [C:V] (closed primitives combined).
- Serves: goal 1; C:V.
- Revisit if: chapter 13 needs an origin that does not fit one of the three kinds.

### DL-02-23: The birth layer is called "quirk"; the third origin is called "livelihood"
- Decision: canonical names avoiding collisions with the `trait` tag facet and with `deed.influence.trade` / 01's trade.
- Evidence: SG-21; 00.18.
- Serves: goal 2.
- Revisit if: 00's glossary adopts other words.

### DL-02-24: The spark grants the working of its own element (revision I-015)
- Decision: `birth.gift.elements` names an element (fire, water, earth, air), chosen in the concept or drawn by the engine with equal weights in the gift draw, writes `pc.spark.element`, and grants that element's `min_tier` 1 working (Cinder Stride, Undertow, Heave, Stolen Breath) through `gifted_ability_by_element`.
- Alternatives considered: one fixed working for every spark (rejected: the gift's own text names four elements, and a water-born character starting with fire contradicts the concept); a separate gift per element (rejected: it would weight the elements school four times in the seven-school draw).
- Evidence: 02.6.3; T-02-7 (rendered by `tables02.py`); DL-05-32; I-015.
- Serves: goal 1.
- Revisit if: ch.13-style settings add elements (the map is data and grows with them).

### DL-02-25: A caster's default placement never fixes its casting attribute at −1 (revision I-009)
- Decision: 02.3.5's default takes the Free rule for a magic livelihood when the people's Typical rule fixes that livelihood's casting attribute at −1 (Orc-kin apprentice, Goblin-kin acolyte, Beastfolk hedge-taught and Touched); data `origins.yaml#creation_defaults.typical_rule_except`.
- Alternatives considered: leave it, relying on the DM's offer of 02.3.4 (rejected: the fast path is exactly where no offer is read, and its default would lose a first fight to a trained foe 27–38% of the time on the branch working, against 5–10% at +3); forbid the combination (rejected: it is a legitimate concept, and remains available by choice).
- Evidence: `02-gen_data02/sim02-output.txt` (revision rows); A2 audit in `gen02-output.txt`; T-02-6.
- Serves: goal 1 (a quick-start caster can cast), goal 2 (the default needs no judgment).
- Revisit if: A3's quantity-versus-freedom audit is rerun and a people's Typical rule is changed.

## DL-03 — Tags and Evidence

### DL-03-01: Deed significance is computed from the frame's pre-committed fields; fresh judgment is kept only for tags and conduct
- Decision: "does this deed count?" = `consequential AND pressured AND own_act`, each computed from frame fields fixed before the roll (stakes, opposition, tier, clocks, delivered reach, costs applied, actor). The DM makes one classification per deed (the primary tag, at FRAME) and judges conduct with citations. Nothing is asked after the outcome is known.
- Alternatives considered: (a) a free `[J:open]` "is this significant?" at RECORD, as the constitution's P5 text describes: rejected because that is exactly the post-hoc, lenient-biased call (false passes ≈120× false checks; plausible framing quadruples it), and the narrator would be judging its own scene; (b) a bounded taxonomy of trigger types: rejected by the constitution itself (relocates the judgment); (c) record everything and let 04 filter: rejected, volume drowns the quality signal and rewards grinding.
- Evidence: [C:P5 sixth pass]; [R4 W2–W3, §9 03 #1–#2, R-05 pre-declared stakes]; R: https://arxiv.org/abs/2607.02802; [R1 #11 NCP discipline]; [BRIEF A3 leniency].
- Serves: goal 2 (no new judgment surface); C:III (judgment kept where it is the honest answer). **Pattern note:** this is a refinement of P5's "base-model judgment" wording, not a taxonomy: the judgments that decide significance are the DM's own (stakes, tier, opposition), made at FRAME. A constitution PATCH sentence is requested of the orchestrator.
- Revisit if: T-03-CALIB shows moments players and reviewers agree were significant being dropped by D1–D3 in more than 10% of cases.

### DL-03-02: Quality is relative, read from the frame's base odds (circumstance excluded)
- Decision: routine ≥ 70%, difficult 40–65%, challenging ≤ 35% success-or-better, computed with levers and snags removed and status kept.
- Alternatives considered: absolute challenge band as the weight (an expert farming band-2 foes gains as much as a novice; no harder-when-higher); odds including levers (taxes clever play: goal 1); a separate advancement roll as in Pendragon or RuneQuest (an extra roll for the same information the OFFER already holds).
- Evidence: Burning Wheel Routine/Difficult/Challenging (http://questingblog.com/wp-content/uploads/2015/02/Burning-Wheel-Procedural-Guide-V2.pdf; https://forums.burningwheel.com/t/errata-number-of-tests-for-advancement/3833); Pendragon winter check [R6 A-04]; RuneQuest experience check (https://rqwiki.chaosium.com/rules/experience.html); Skyrim skill cost curve (https://en.uesp.net/wiki/Skyrim:Leveling); T-00-6.
- Serves: goal 2 (zero extra judgment; already computed); goal 1 (levers never reduce evidence).
- Revisit if: T-03-YIELD shows more than 80% of a typical character's events landing in one rung.

### DL-03-03: The points table (quality 2/4/6; stakes 0/2/4; lethal +2; critical success +2; novelty +2)
- Decision: integer points, range 2–16; typical risky success at the edge of ability = 6.
- Alternatives considered: multiplicative weights (need fractions; one event could dwarf a session); 1/2/3 base (halving loses resolution under diminishing returns); weighting critical successes heavily (rewards luck).
- Evidence: [R2 #5, §03 HWFWM honest vs cheap path]; [R6 A-12 Blades desperate rolls]; simulation `evidence03.py` (largest event = two-thirds of a focused session's node yield; 20% of a threshold of 80).
- Serves: goal 2 (bounded blast radius, class iii); SG-23.
- Revisit if: T-03-YIELD's focus-node yield falls outside 15–35 points per session.

### DL-03-04: Failures count half when they cost something; Safe failures are not evidence; success at cost is a success
- Decision: as stated; critical failure is treated as failure.
- Alternatives considered: successes only (stalls growth for characters attempting hard things; contradicts Burning Wheel and Blades precedent); failures at full weight (a career of failing equals a career of succeeding).
- Evidence: [R6 A-06, A-12]; [R1 §03 "recorded as an attempt, never as a success"]; 01.9.3 (Interface request from 01).
- Serves: goal 1 (trying hard things is never wasted).
- Revisit if: playtests show players fishing for failures at Dire stakes to farm half-points (the same-target and diminishing rules should prevent it).

### DL-03-05: Evidence is settled per scene; diminishing returns 1, ½, ¼, 0 at every node
- Decision: events are pending until `scene_end` (reserved handler `h.03.antigrind_reset`) or the day boundary (`h.03.day_settle`); each node keeps its three best contributions at full, half and a quarter.
- Alternatives considered: diminishing in order of occurrence (a trivial first beat uses the full slot); per-session caps as in Blades ("1 if at all, 2 if a lot": sessions are not fictional time, 00.7.9); DR only at the leaf (weapon switching would multiply branch evidence).
- Evidence: [R3 03.9 WoW diminishing returns]; [R6 A-12]; simulation scenarios B and C/C2 (switching weapons: 1,106 vs 1,191; no gain).
- Serves: goal 2 (anti-grind without judgment).
- Revisit if: T-03-SCENE shows long scenes under-credited.

### DL-03-06: The routine cap (one routine contribution per node per day)
- Decision: as stated.
- Alternatives considered: no cap (rat grinder 910 vs honest 486); routine never counts (starves trades whose daily work is routine); a cap per scene (grinders cut more scenes).
- Evidence: Burning Wheel (routine tests stop counting at higher exponents); simulation scenario B (2,196 → 910 → 340).
- Serves: goal 2.
- Revisit if: T-03-ROUTINE shows more than 60% of a crafter's or healer's eligible events removed.

### DL-03-07: The same-target cap (per target, per level-2 deed node, per day)
- Decision: a later scene's event against an already-settled (target, node) pair the same day settles as 0.
- Alternatives considered: a cooldown in steps or intervals (Ultima IV; needless precision); per-scene only (the Skyrim horse loop survives across scenes).
- Evidence: https://en.uesp.net/wiki/Skyrim:Sneak; https://bumbershootsoft.wordpress.com/2017/09/29/hacking-the-virtues-becoming-the-avatar-in-five-easy-steps/.
- Serves: goal 2.
- Revisit if: legitimate same-day rematches (a running duel across scenes) turn out to be common.

### DL-03-08: Novelty by context class (+2 when the kind of opposition or obstacle is new for that level-2 node within the window)
- Decision: as stated; context class = opposing creature tag at level 2, else the obstacle's tag at level 2, else the scene's situation tag at level 2.
- Alternatives considered: no novelty term (range within a skill unrewarded); novelty by individual target (every new goblin is "new"); a DM-judged "was this new?" (lenient).
- Evidence: [R2 §03 Alexandrian diversification]; [R3 03.5 Delve diverse kill types].
- Serves: goal 1 (variety pays); goal 2 (computed).
- Revisit if: T-03-YIELD shows novelty firing on more than half of all events (then lengthen the window or drop to +1).

### DL-03-09: Witnesses never weight capability; they feed a separate public tally with scope
- Decision: points are identical witnessed or not; `public(actor, tag, scope)` and `public_deed` packets carry witnessed deeds to 11.
- Alternatives considered: a witness multiplier (the brief's list included "witness" under weighting): rejected because it penalizes stealth, wilderness and solitary callings and rewards performing for crowds; it also fuses tally and witness, which R6's central finding separates.
- Evidence: [R6 §0 #1, R-A1, R-A3, A-15 Ars Magica]; new Fable per-settlement reputation (https://www.gamespot.com/articles/new-fable-keeps-series-tradition-of-kicking-chickens-alive-and-youll-be-judged-for-it/1100-6537589/).
- Serves: goal 1; 00.17 Q22 (recognition vs reputation).
- Revisit if: 04 finds public recognition vehicles need a finer public measure than `public()` provides.

### DL-03-10: Recency is counted in evidence-bearing scenes (12 full + 12 half), not in calendar time
- Decision: as stated.
- Alternatives considered: a window in days or weeks (a skipped winter erases recency; sandbox time is elastic); exponential decay per reflection (reflections fire weekly in downtime: same problem); cumulative only (labels never track drift).
- Evidence: [R3 T-8, G-3, 03.10]; [R6 A-08]; simulation scenario D (pivot visible in 2 sessions; old recent gone in 5).
- Serves: goal 2 (deterministic, play-relative); goal 1 (downtime is never punished).
- Revisit if: T-03-PIVOT misses its 2–4 session target.

### DL-03-11: Cumulative weight never decays; only void and atonement remove evidence
- Decision: as stated.
- Alternatives considered: slow decay of `weighted` (loses "who you were"; makes thresholds a treadmill).
- Evidence: Delve and EVE permanent counters [R3 03.10]; [R1 §03 explicit supersession; FAMA].
- Serves: goal 2; C:VI is served by 04's consolidation, not by eroding history.
- Revisit if: 04 finds stale callings cannot be relabelled with `recent` alone.

### DL-03-12: Counted evidence is a separate tally fed by eleven engine counters
- Decision: `cnt.defeat`, `cnt.focus`, `cnt.ward`, `cnt.control`, `cnt.progress`, `cnt.made`, `cnt.discovery`, `cnt.clue`, `cnt.lifesave`, `cnt.journey`, `cnt.training`; never summed with judged points; 04 is asked to require both.
- Alternatives considered: counted events adding to the judged tally (double counts the same beat; lets judgment and counting blur); no counted evidence (all growth rests on judged calls).
- Evidence: Delve Primary/Secondary requirements [R3 03.4, 04.1, #4]; [C:P5 dual-tier]; [R3 03.12 spend-channel tag].
- Serves: goal 2 (a key no judgment can turn); C:P13 spirit.
- Revisit if: T-03-COUNT shows a counter that is trivially farmable or never fires.

### DL-03-13: Conduct is grounded in a state write; magnitude 2 or 4 read from the write; strain works off at half rate; atonement supersedes explicitly
- Decision: as 03.3.3 and 03.8.
- Alternatives considered: free ±1 per judged moment (lenient; 2.6× inflation in simulation); instant oath break on one act (BG3's brittle triggers); symmetrical work-off (a wrong is undone as fast as it is done).
- Evidence: [R2 #6]; [R6 A-01–A-03, V14]; [R1 §03 T-9]; simulation E/E2.
- Serves: goal 2; C:P5 ("atone rather than instantly and irreversibly losing power").
- Revisit if: T-03-STRAIN shows the road back is felt as unreachable or as trivial.

### DL-03-14: Secondary tags earn half and must be grounded
- Decision: at most two; each cites an ability, license, item, Setup beat, companion, mount or position that carries the tag.
- Alternatives considered: ungrounded secondaries (a spurious node reached 49% of the real one in simulation); no secondaries (hybrid and style evidence lost; DCC's lateral multi-credit question unanswered).
- Evidence: [R2 §03 DCC multi-credit; HWFWM category distribution]; simulation E/E2 (49% → 15%).
- Serves: goal 2.
- Revisit if: T-03-CALIB shows grounded-but-irrelevant secondaries above 10% of events.

### DL-03-15: Deed tags go to level 3 everywhere; level 4 is reserved
- Decision: 270 level-3 deed tags; no level-4 tags seeded; level 4 only by PR-03-6 with a data entry that needs it.
- Alternatives considered: weapon-by-weapon level 4 (duplicates the item facet; more confusable choices); stopping at level 2 (callings and ability pools cannot key on techniques such as fencing, sniping, lockpicking).
- Evidence: [R4 §3.2 S1 wrong-choice rate rises with overlap]; [R3 03.6 low-cardinality keys]; 00.2.2 (`[J:enum]` ≤ ~8 options).
- Serves: goal 2.
- Revisit if: 04 or 05 request more than ten level-4 tags.

### DL-03-16: Two level-2 deed tags appended: `deed.influence.teaching`, `deed.craft.scribing`
- Decision: as 03.1.3.
- Alternatives considered: teaching under `lore` (teaching moves a person; lore knows); scribing under `lore.languages` (that tag reads; this makes).
- Evidence: [R6 A-21, V2 the taught route]; 00.5.5 append-only rule.
- Serves: goal 1 (mentor and scribe identities reachable).
- Revisit if: 04's coverage audit finds them unused.

### DL-03-17: Shares and ratios are rational pairs compared by cross-multiplication
- Decision: `share`, `dominance`, `balance` return `{num, den}`.
- Alternatives considered: percentages (banned by SG-23); pre-divided integers (rounding makes thresholds inexact).
- Evidence: SG-23; INV-17.
- Serves: goal 2.
- Revisit if: never (pure representation).

### DL-03-18: Crisis and peak flags carry "qualitatively distinct" evidence
- Decision: `crisis` and `peak` as 03.4.5, counted in `detail`, no points.
- Alternatives considered: extra points for crisis (already covered by Dire and lethal); a judged "was this a defining moment?" (lenient).
- Evidence: [R2 #5]; [R6 R-A4, V5].
- Serves: goal 2.
- Revisit if: 04 needs a third kind of distinct evidence.

### DL-03-19: Compelled acts give no conduct evidence, but deed evidence stays
- Decision: as 03.2.6.
- Alternatives considered: no evidence at all under compulsion (the skill used was the actor's); conduct counted (punishes the player for a charm).
- Evidence: [R6 anti-patterns: compelled behaviour]; goal 1.
- Serves: goal 1.
- Revisit if: 05 adds effects that only partly constrain choice.

### DL-03-20: Evidence is tracked for PCs and opted-in companions only
- Decision: as 03.2.7.
- Alternatives considered: tallies for every NPC (unbounded state with no consumer).
- Evidence: 00.17 Q8; [C:IV].
- Serves: goal 2.
- Revisit if: 11 wants NPC rivals to grow by the same mechanism.

### DL-03-21: The reflection sweep restores only frame-qualified omissions
- Decision: as 03.3.5.
- Alternatives considered: end-of-session question lists (Forbidden Lands): rejected as a second, lenient judgment pass.
- Evidence: [R6 A-14]; [R4 W2].
- Serves: goal 2.
- Revisit if: omission rates in playtest logs are under 2% (then drop the sweep).

### DL-03-22: Aspirations never add weight
- Decision: aspirations (02) affect salience and hooks only.
- Alternatives considered: a weight multiplier for declared aspirations (reintroduces a menu).
- Evidence: [R6 A-13, R-A7].
- Serves: C:P5 (emergence).
- Revisit if: never without a constitution change.

### DL-03-23: Challenge band is read from the final DC and adds no points
- Decision: DC ≤ 12 → 1; 13–17 → 2; 18–22 → 3; 23–27 → 4; ≥ 28 → 5; exposed through `detail`.
- Alternatives considered: band as a weight (see DL-03-02); band from the threat band only (non-combat deeds have none).
- Evidence: 00.3.7, 00.3.17; [R6 R-A4].
- Serves: goal 2.
- Revisit if: 01 moves the DC ladder (recompute the ranges).

### DL-03-24: A strike on an unaware target is classified by the contest the frame rolls
- Decision: rolled against awareness → `deed.guile.ambush.*` primary, weapon grounded by item; rolled against Guard or the shot's difficulty → weapon or spell tag primary, ambush grounded by position.
- Alternatives considered: every strike on an unaware target is ambush-primary (a hunter shooting an unwary deer would lose her archery competence, since competence reads only the primary tag); never ambush-primary (contradicts 00.5.2).
- Evidence: 00.5.2, 00.5.6, 00.3.6.
- Serves: goal 1 (competence follows the skill actually tested); goal 2 (a checkable test).
- Revisit if: 06 frames all such strikes one way (then the rule collapses to that case).

### DL-03-25: Optional backstory evidence (up to three tags × 24 points) written at creation
- Decision: as 03.2.8; counts toward `weighted` and `raw` only.
- Alternatives considered: none (a forester begins with no history at all); larger seeds (an identity granted at creation: a menu).
- Evidence: [C:P4]; T-03-10 (24 ≈ one session).
- Serves: goal 1.
- Revisit if: 02 declines it or 04's thresholds make it decisive.

### DL-03-26: Contests, ruinous stakes and the brink: the non-combat crisis and challenge band (revision I-003)
- Decision: outside conflict, a beat in a **contest** (social: a Talk frame on a principal or a faction's spokesman, 15.3.11; craft: a crafting project's step, 08.6.4; lore: a case or research a principal or faction keeps, 15.9.20) takes `challenge_band = max(DC band, contest band)`, the contest band being the opposing party's threat band or its faction's tier, or the work's type-tier. A Dire non-conflict frame whose threatened cost at its critical-failure severity is irreversible is **ruinous**: +2 points like lethal (03.4.2) and a crisis (03.4.5). A contest beat declared with the contest's opposing clock one segment from full is **at the brink**, a crisis like Staggered. All three are engine-read from records (faction tier, threat band, type-tier, the declared cost, the clock), never judged.
- Alternatives considered: (a) OEQ-04-10's own fallback, counting a Dire challenging success twice for non-combat branches: rejected, it multiplies one event instead of naming the non-combat events that are as grave as a lethal fight, and it does nothing for the band cap; (b) a counted analogue of `cnt.defeat` for a contest won (`cnt.prevail`, units = contest band): simulated and dropped, because the contest pillars' counted share already clears 04.3.3's tenth (R9 of `04-recog-parity.py`) and it changed no pacing; (c) lowering tier 3–5's crisis and great-deed counts for non-combat callings: rejected, it would make the tiers mean less for one pillar instead of giving that pillar the same kinds of deed.
- Evidence: `04-recog-parity.py` (200 seeds, 90 sessions, one play shape for every pillar): medians to tier 3 / tier 5 — archer 19 / 51; envoy 18 / 46; smith 18 / 45; scholar 17 / 46 under the revised rules (all within ±20% at both tiers); under the earlier rules the smith never reached tier 3, and the envoy and scholar ran 21% faster than the archer to tier 3 (the band they faced was modelled as band to band + 2, which the contest band now replaces with the same offset a fight has). [03.4.3; 03.4.5; 15.3.11; 15.9.20; 08.6.4; I-003; R1 #13]
- Serves: goal 1 (every calling has a real path to tier 5), goal 2 (no new judgment: every input is a record).
- Revisit if: live pick and tier logs (T-04-CRISIS) show any pillar's tier-3 median outside ±20% of the combat median.

### DL-03-27: Counted yield measured, not estimated (revision I-004)
- Decision: 03.7.3's arithmetic estimate is replaced by a measurement: `03-counted-yield.py` runs chapter 06's conflict engine and applies this chapter's points and saturation to every beat, defeat, flight and Focus push. Counted share at the weapon node per band 1–5: 0.11 / 0.15 / 0.22 / 0.23 / 0.33 without Focus, 0.26–0.44 when pushing; the contest pillars 0.31 (social), 0.76 (craft) and 0.31 (lore) at the median, and never below 0.24 at the tenth percentile (`04-recog-parity.py` R9).
- Alternatives considered: keep the estimate (rejected: I-004); measure in 04's play model only (rejected: its defeat and Focus rates are themselves assumptions; the conflict engine produces them from the rules).
- Evidence: `03-counted-yield-output.txt` (4,000 fights a row); integer halving makes a second band-1 defeat in one scene worth 0, which is why band 1 is lowest.
- Serves: goal 2 (numbers backed by measurement).
- Revisit if: live play (T-03-COUNT, T-04-COUNT) yields a counted share under 0.10 at any PC's top node.

### DL-03-28: The social contest's methods are a closed list (revision I-071)
- Decision: a Talk frame is a social contest only by `smethod.request`, `bargain`, `deceive`, `intimidate`, `interrogate`, or any beat of a campaign or debate, aimed at a principal or a faction's spokesman (03.4.3; 15.3.11 cites it; `evidence.yaml#challenge_band_source`). Win over, provoke, perform, command and read take the DC's band.
- Alternatives considered: 15.3.11's "any method but read" (rejected: lets a Warm-capped win-over of a guild master mint band-4 deeds); 03.4.3's list without debate (rejected: 15.3.11 already names a council's patience as a contest clock).
- Evidence: `04-recog-parity.py`'s envoy plays requests only, so its parity medians (18 / 46) stand unchanged.
- Serves: goal 2, goal 1 (parity kept without a soft path to high-band deeds).

### DL-03-29: "Brink" is chapter 07's word; the contest flag is "one from full" (revision I-046)
- Decision: 03.4.5's contest crisis flag, 03's frame field (`contest.one_from_full`), 08.6.4, 15.3.11, 15.9.20, 04.3's notes and `evidence.yaml` say "one from full"; "brink" means only brink wounds, the brink menu and Dying at 1 + brink (07).
- Evidence: verification-1 (two meanings of one word in an AI-read ruleset).
- Serves: goal 2 (one term, one meaning).

## DL-04 — Recognition and Growth

Fragment for `appendix/decision-log.md`. Format: BRIEF §11. Simulation references are to
`rules/_process/simulation/04-recognition-sim.md` (R1–R10).

### DL-04-01: A calling is a derived label; a tier grants only gated draws from shared sources
- Decision: no calling entry lists an ability. A tier grants a competence value, grades in ch.05's shared training licenses, one of five universal capability licenses, picks into ch.05's one tag-gated ability pool, and one bounded family mechanic (04.1.1).
- Alternatives considered: per-calling ability lists (the menu-driven model P5 forbids); per-calling signature licenses (183 bespoke licenses: an ability list by another name, and unauthorable to the license schema's standard).
- Evidence: [C:P5 "MUST NOT become an independent system that hands out an ability list of its own"]; [C:V]; [R3 04.6, 04.15].
- Serves: goal 2 (one pool to audit), principles V and VII.
- Revisit if: playtests show callings of one family feel interchangeable (then author more family mechanics, not ability lists).

### DL-04-02: A calling for every level-2 deed tag (81), nine branch callings, forty curated level-3 callings
- Decision: full coverage at level 2; level 3 only where the fiction recognizes the narrower identity as its own (04.2.1). 183 callings in all.
- Alternatives considered: a short list of about twenty iconic callings (holes in coverage make the roster a menu by omission; goal 1); a calling for every level-3 tag (270 more entries; most would be "a blade-user who uses a greatsword").
- Evidence: [C:P5 "dominance of one tag at any level of the hierarchy"]; [R3 03.7 Threadbare: one counter per candidate]; 00.5.2.
- Serves: goal 1 (any sustained way of playing reaches a name); goal 2 (independent evaluation, no competition logic).
- Revisit if: T-04-PACE shows level-3 callings pre-empting their level-2 parents in a way players dislike (R6: Lockbreaker came first for 51 of 100 burglars).

### DL-04-03: One proposed tag, `deed.wilds.animals.falconry`
- Decision: propose a level-3 tag for the Falconer (`data/tags.yaml`, adopted at integration) with a fallback re-keying to `animals.training`.
- Alternatives considered: key the Falconer on `animals.training` (loses the distinct kind: working a trained bird is not teaching it); a level-4 tag (03 reserves level 4).
- Evidence: PR-03-6 steps 1–6; the brief names the falconer as the example of a narrow calling.
- Serves: goal 1. Revisit if: 03 rules it an alias.

### DL-04-04: Branch callings need breadth, and are never granted
- Decision: a broad calling needs weighted ≥ 120, at least three level-2 children at ≥ 30, and the largest child at most two-thirds of the branch; it is always an offer.
- Alternatives considered: no breadth test (the branch tally passes its line before any child's, so every archer would be offered Warrior first: R3 without the test); a share cap of 3/4 (offered Warrior to about half of bow-focused archers).
- Evidence: [R1 T-13 "broad classes make bad playbooks"]; [C:P4 breadth is not day-one power]; simulation R3 (mixed-weapons 200/200, archer 34/200, swordsman 1/200).
- Serves: goal 2; P4. Revisit if: OEQ-04-1.

### DL-04-05: The hybrid table covers all 36 pairs (32 named, 4 none); the trigger is min 60, balance 2/5, joint scenes 5, recent 15
- Decision: one row per pair of deed branches; hybrids are always offers; they grant competence on two roads at the broad schedule and carry the pair's composite.
- Alternatives considered: a handful of hybrids (leaves most mixed play unnamed); balance 1/3 as 03 suggested (offered the hybrid to 87 of 200 characters playing 90/10; at 2/5 it is 9 of 200); requiring both specialist thresholds (Cataclysm's failure, R3 04.4); competence on both whole branches (more day-one power than a specialist, against R2 #10).
- Evidence: [C:P5 curated sparse table]; [R3 04.3, 04.4, 04.9, 04.10, T-5, G-1]; simulation R4.
- Serves: goals 1 and 2. Revisit if: OEQ-04-4.

### DL-04-06: Variants: the same key with an added requirement (Monk, Devourer)
- Decision: a variant shares a level-2 calling's key and adds one requirement of another kind; base and variant are one lineage.
- Alternatives considered: deed × conduct hybrids (P5 keys hybrids only on deed-branch pairs); new tags for "monk" or "devourer" deeds (a tag names a kind of method, not an identity).
- Evidence: [R3 04.1: Delve's Beacon family shares a primary and differs by secondary].
- Serves: goal 1 (two iconic archetypes), P5. Revisit if: more than five variants are ever wanted (then the mechanism needs its own table).

### DL-04-07: Conduct-keyed callings: ten vows, nine dark callings, one oath seat
- Decision: vows key on positive poles (sworn, V4), dark callings on negative poles (bargained, V13); no competence; a boon restated at tiers 3 and 5; thresholds on `pos` / `neg` 16, 40, 80, 140, 220; `conduct.courage` has no dark calling.
- Alternatives considered: conduct as a mere requirement of deed callings (loses "oath/conduct-keyed callings" and the atonement loop); vows without a seat limit (ten simultaneous oaths: untrackable Fraying).
- Evidence: [C:P5 specialists may key on conduct tags]; [R2 #6]; [R6 A-11, R-A6]; 03.8.5; simulation R10.
- Serves: goal 1 (the paladin, the monk, the villain); goal 2 (one axis, one stage track).
- Revisit if: OEQ-04-7.

### DL-04-08: Requirement shape: weighted + counted + quality floor + distinct scenes; higher tiers need great deeds, crises and contexts since the last tier
- Decision: 04.3.2 and 04.3.4. A great deed is tied to the tier being entered, not to `power_band`.
- Alternatives considered: weight alone (03's grinder passes 80 by session 5); 03's `peaks` (relative to `power_band`, so a second calling of a high-band character could never deepen); a witness requirement at tier 4 (penalizes hermits; 03.4.6).
- Evidence: [C:P5 Delve dual-tier]; [R2 #5]; [R6 R-A4]; 03 Interface requests (a); simulation R1, R5.
- Serves: goal 2. Revisit if: OEQ-04-1, OEQ-04-10.

### DL-04-09: Counted requirement = one tenth of the weighted threshold; training counts for at most half
- Decision: 04.3.3.
- Alternatives considered: a fifth (would bind honest low-count pursuits: negotiation runs at 0.15); no counted requirement (loses the second key that judgment cannot inflate).
- Evidence: [03.7.1]; [R6 A-27]; simulation R9.
- Revisit if: OEQ-04-2.

### DL-04-10: Confidence = the count of five confirmations (Current, Rising, Central, Leading, Margin); grant at 4+, offer at 1+, abstain at 0 or stale
- Decision: keep the deterministic tally scorer; define confidence as 04.4.2; grants only for tier-1 fine and narrow specialists with a clear field.
- Alternatives considered: a separate classifier model (the constitution's body text; adds a model and a calibration problem for no gain in independence: a deterministic scorer shares no model family, R3 T-4); threshold margin as the score (tested: margins of counted and quality predict nothing beyond their floors); a first version using margin, counted margin, quality, currency and clear field (not monotone: 62, 74, 65, 72, 96 in 100).
- Evidence: [C:P5]; [BRIEF A3]; [R2 T-1, gap 7]; `04-feat04.py` (which facts predict confirmation); simulation R7 (37, 59, 64, 73, 91, 97 in 100 by score; grant 91, offer 74, abstain 38).
- Serves: goal 2 (calibrated, auditable); goal 1 (mixed histories are offered as named alternatives).
- Deviation from Pattern P5's wording ("calibrated classifier … MUST NOT share a model family"): recorded; a constitution PATCH is requested.
- Revisit if: OEQ-04-3, OEQ-04-5.

### DL-04-11: Named composites for hybrids only; specialists get a family Focus trigger; conduct callings a boon
- Decision: 32 composites keyed on deed-branch pairs with three restated ranks; nine Focus triggers; nineteen boons (04.5.4).
- Alternatives considered: a composite per specialist (the substrate's composite keys are two deed branches, two conduct axes, two harm branches or two flagged licenses: a single-key specialist has no honest pair, and 183 composites cannot be audited); P14 cadence differences (06 owns cadence; INV-11).
- Evidence: [C:P5 "MAY unlock a small, bounded, audited synergy bonus"]; [C:P6]; [C:P9 companion; R3 T-1 generation triggers over one pool]; [R2 4c bounded compounding].
- Revisit if: 05 retunes Focus; OEQ-00-4 (one-link chains).

### DL-04-12: Vehicles are filtered and ordered by the engine; the DM picks among at most three
- Decision: 04.6.2; recency of two; V7 and V6 need nothing, so recognition is never withheld for want of a recognizer.
- Alternatives considered: free DM choice of staging (W10: the model repeats one trope; and it would stage drama where no crisis was flagged); fully engine-chosen (loses fit to the scene).
- Evidence: [R6 A.4, R-A1, R-A2]; [R4 §9 04 #2].
- Revisit if: OEQ-04-6.

### DL-04-13: Readiness is a derived band voiced by the Seer's Reading and shown as "Leanings"; no readiness clock
- Decision: five bands from the next tier's weighted threshold; the codex shows key-tag names and band words only; a reader names the kind of deed still missing.
- Alternatives considered: a hidden clock per candidate with omens (a second copy of a sealed tally that could drift, and an omen on every tick would be noise); full transparency of thresholds (Delve; breaks hidden mechanics); no visibility (goal 1: the player cannot pursue an identity on purpose).
- Evidence: [R6 V6, A-03]; [R3 04.13, T-6, G-16]; 00.17 Q7 permits, does not require, a readiness clock.
- Revisit if: OEQ-04-12.

### DL-04-14: Offer protocol: accept / decline / defer; defer is the default; personal offers never expire while eligible
- Decision: 04.7.1–04.7.7; decline cooldown of 24 evidence-bearing scenes and + W1/2; closed price list.
- Evidence: [R6 A.5]; [C:P1]; 12.2.6 pause point 7.
- Revisit if: players report losing track of standing offers.

### DL-04-15: Character-scale provisional status: confirm from 12 evidence-bearing scenes at since-grant weighted ≥ 3/10 of W1; lapse at 24; always a warning first
- Decision: 04.8.2. The measure is evidence at the key since the grant, counted in play, not in calendar time; the tier-4 attribute increase waits for confirmation.
- Alternatives considered: test `recent` at the season boundary (the recency window still holds pre-grant evidence, so an abandoned tier confirms); calendar windows (a winter of rest would lapse a ranger; 03.6.1); permanent on grant (C:VI's provisional default).
- Evidence: [C:VI]; [BRIEF A3]; [00.17 Q12]; [R3 04.16, T-3, G-4] (the extrapolation from content leagues is recorded as such); simulation R8.
- Revisit if: OEQ-04-8.

### DL-04-16: Oath words are the player's own, checked by one flag against the oath's axes and forbidden acts
- Decision: 04.7.4; the stored oath block governs whatever the words say.
- Evidence: [R6 V4, A-01]; [R2 #5 individualized truths]. Revisit if: the flag is answered inconsistently (T-04-VEH logs it).

### DL-04-17: Three deed seats and one oath seat; consolidation keeps every pick and specialty and pre-pays future picks
- Decision: 04.8.1, 04.8.5: the result tier is bounded by the constituents'; specialties and capabilities persist; `legacy_picks` cancel later picks; consolidation is blocked during the Fraying.
- Alternatives considered: two seats (Azarinth) (too tight for a hybrid plus a trade); unlimited (Threadbare's fourteen); consolidation that drops surplus picks (felt as loss; R1 T-16; WoW's rework evidence).
- Evidence: [C:VI structural retirement]; [R3 04.3, 04.12, #5, #10]; [R1 T-16].
- Revisit if: OEQ-04-9.

### DL-04-18: Picks: three candidates ranked by the character's own evidence, own pool before kin; unspent picks are kept
- Decision: 04.8.4, PR-04-5. Proposed to 00 as domain `gen.pick`.
- Alternatives considered: free choice from the whole eligible pool (a menu; against P5's premise); a random fill (no agency); a kin pool at min_tier + 1 (left tier-1 narrow callings with two candidates until 05's pool is large; replaced by ordering).
- Evidence: [C:P5]; [C:P1 defer and gamble]; [R3 04.7 one of three per tier].
- Revisit if: 05's pool turns out to have fewer than three eligible abilities for most narrow callings at tier 1.

### DL-04-19: Monster-power absorption belongs to one calling, the Devourer, offered only by V13
- Decision: `lic.call.taking`; a variant of the Bestiarist with a hunter's record as its added requirement.
- Alternatives considered: a hybrid (every pair already has a better claimant, and non-casters could not reach a primal pair); a trait any calling may buy (not "class-gated").
- Evidence: [C:P5]; [R6 A-28, V13]; [R2 4e].
- Revisit if: OEQ-04-11.

### DL-04-20: The Taking: trigger, cap, cost, failure
- Decision: trigger = the PC's own resolved defeat of a creature it saw act, declared in the scene; a Resolve check against the creature's band tier; 2 Focus; one attempt per creature, one success per long rest; library 4–12 by tier, used only when slotted in the acquired partition; failure costs S2 / S3 and forbids a retry.
- Alternatives considered: automatic on kill (Feature 003's probe; uncapped in effect); a chance roll with no check (no player decision); slot-free absorption (leaks the hard ceiling, 00.17 Q2).
- Evidence: [R: https://finalfantasy.fandom.com/wiki/Learning] (witness, survive, win); [R3 04.18 library + cannot-copy]; [R: src/ability_pool.py] (shape kept); [R2 gap 1].
- Revisit if: OEQ-04-11.

### DL-04-21: The absorbable pool (27 entries of core effects) and one bane per creature branch
- Decision: `gen_absorb.yaml#pool`, `#banes`; folk have no pool.
- Evidence: [R2 #47 Hemalurgy's qualitative tax; #56 a trait must not delete its calling's weakness]; [C:P12]; SG-15.
- Revisit if: 09's bestiary needs signatures the pool lacks.

### DL-04-22: The Fraying: three stages on strain 4 / 8 / 12 or a forbidden act; atonement by a clock; lapse only after two season boundaries; none at tier 5
- Decision: 04.9. Non-oath callings have shadows that show and remove nothing.
- Alternatives considered: instant loss on a forbidden act (BG3's brittle breaks; R6 A-02); loss for non-oath callings (a cruel archer is still an archer); a Fraying clock (would duplicate 03's strain).
- Evidence: [C:P5 atonement]; [R6 V14]; [R2 #6, T-10]; 03.8.5.
- Revisit if: OEQ-04-7.

### DL-04-23: The ladder's numbers: five tiers; competence 3/4/5/5/6 (narrow) and 2/3/4/4/5 (broad, hybrid roads); five universal capabilities; band from tiers
- Decision: 04.5.1–04.5.7; W 80 / 200 / 440 / 800 / 1,300 (narrow), ×¾ (fine), ×1½ (broad); the attribute increase at a confirmed tier 4.
- Alternatives considered: 03's suggested 80 / 200 / 450 (kept in spirit; 440 so that broad is exactly 660); a bespoke tier-3 license per calling (DL-04-01); competence +4 at tier 1 (breaks band P1 of 00.3.7).
- Evidence: [00.3.5–00.3.7; DL-00A-04]; [R2 #2 Ideals: fixed top, universal checkpoints]; [R3 04.6]; simulation R1 (archer: sessions 4 / 9 / 19 / 34 / 56).
- Pattern note: P2's "crystallized by a specific, narratively-significant moment" is met by 04.5.8: the completing deed is the crystallizing event and a reflection counts as the moment of realization, so that a tier is never withheld.
- Revisit if: OEQ-04-1.

### DL-04-24: Companions that track evidence hold at most one calling, to tier 3
- Decision: 04 Edge cases. Evidence: 03.2.7; 00.17 Q8. Revisit if: ch.16 wants growth beyond tier 3 for a squire who becomes a PC.

### DL-04-25: The Monk's conduct gate carries the positive pole (revision I-007)
- Decision: `call.monk` gains `pole: positive`, so its `pool_gate.conduct: [conduct.restraint]` admits the restraint vow's abilities (04.8.4 requires the ability's `conduct_pole` to equal the calling's `pole`).
- Alternatives considered: drop the conduct gate from the Monk (rejected: the variant is defined by restraint, and its oath names that axis); give oath-bearing callings a pole by rule rather than data (rejected: one explicit field is what the pick gate reads).
- Evidence: `05-ladder-check.py` reported the gate as dead data (no oath-gated ability admitted); after the fix the Monk's restraint row reads 1/0/1/0/1 at the positive pole.
- Serves: goal 2 (data and rule agree).
- Revisit if: another oath-bearing calling adds a conduct axis to its pool gate (the ladder check will flag a missing pole).

### DL-04-26: `no_pool` covers the human-like folk only; `signature_of` recorded (revision I-020)
- Decision: `gen_absorb.yaml#no_pool` lists human, elf, dwarf, halfling, orc and goblin. Giant-kin and beastfolk carry natural powers and are gated like any creature: Stone Grip already gated giants; gnolls and ratfolk are added to Predator's Nose, ratfolk to Night Eyes, lizardfolk to Gills and Scale Ward. The 25 pool entries named as an archetype's signature record those archetypes in `signature_of` (46 in all). `signature_of` (what a source's decisive fill takes) and `signature_eligible` (what the fallback draw may take when the named entry is gated out, 00.11 step 6) stay distinct fields.
- Alternatives considered: keep `no_pool: creature.folk` with an exception list in ch.09 (rejected: two sources of truth, and the shipped Stone Grip contradicted it); derive `signature_of` at load time only (rejected: the field is in the schema and ch.08's decisive fill reads it; the generator check keeps it from going stale).
- Evidence: ch.09's interface requests to 04; `09-gen_data09.py` now reads `no_pool` from the data and fails when `signature_of` disagrees with `archetypes.yaml` (0 errors after the change; gnoll, lizardfolk now list eligible entries).
- Serves: goal 1 (a Devourer can take a troll's grip, as the fiction promises), goal 2 (one source of truth).
- Revisit if: new folk peoples are added (decide human-like or natural per people).

### DL-04-27: The counted divisor stays at 10, on measurement (revision I-004)
- Decision: 04.3.3's counted requirement stays at the weighted threshold ÷ 10. Measured on chapter 06's conflict engine (`03-counted-yield.py`), it costs extra play only for a band-1 fighter who meets nothing but mobs and never spends Focus: one fight more than the weighted threshold already needs (9 instead of 8) for tier 1, and nothing at tiers 2–5 or with any Focus spent. The contest pillars measure 0.31 (social), 0.76 (craft) and 0.31 (lore) at the median, and never below 0.24 at the tenth percentile, above the tenth. OEQ-04-2's pre-set trigger (lower to ÷ 15 if a pillar yields under 0.12) was a proxy for "the requirement binds honest play"; band 1 without Focus measures 0.11, but measured directly the binding is one fight in one corner, and ÷ 15 would loosen the requirement for every pillar to spare it. The trigger is restated as the direct test: lower the divisor if the counted requirement delays any pillar's tier by more than one session.
- Alternatives considered: ÷ 15 everywhere (rejected above); a band-1 exception (rejected: a rule for a one-fight effect).
- Evidence: `03-counted-yield-output.txt`; `04-recog-parity-output.txt` R9. [04.3.3; OEQ-04-2; I-004]
- Serves: goal 2.
- Revisit if: T-04-COUNT in live play shows a session's delay in any pillar.

### DL-04-28: Non-combat parity accepted on simulation (revision I-003)
- Decision: the requirement sets of 04.3 are unchanged; parity comes from what the evidence rules now count (DL-03-26: contest band, ruinous, brink; 15.3.11, 15.9.20, 08.6.4). OEQ-04-10 is answered: envoy, smith and scholar reach tier 3 at sessions 18 / 18 / 17 and tier 5 at 46 / 45 / 46, against the archer's 19 and 51 in the same play shape.
- Alternatives considered: separate, lower ladders for non-combat callings (rejected: the tiers would mean different things by pillar); OEQ-04-10's "count a Dire challenging success as two crises" (rejected in DL-03-26).
- Evidence: `04-recog-parity.py` and its output; `04-recognition-sim.md` (I-003 section). The play shape (55% of scenes in one's pillar, 3–6 beats, a quarter of pillar scenes Dire) is an assumption shared by every style; with 04's original thinner social shape (2–4 beats, 15% Dire) the envoy still reaches tier 3 at 20 and tier 5 at 54.
- Serves: goal 1 (R1 #13: every calling needs a real path).
- Revisit if: T-04-CRISIS fails in live logs.

### DL-04-29: `power_band` reads confirmed tiers only (revision I-037)
- Decision: 04.5.6 computes `power_band(pc)` from each unsuspended calling's `confirmed_tier` (the highest tier whose grant is permanent; a new `Character.callings` field, 04.1.2), with `inherited_band` read the same way (04.8.5 item 5). A provisional tier's grants (competence step, training, capability, family-mechanic rank, pick) work at once; the numbers that size the character wait for confirmation: power band, and through it maximum Vitality (07.1.2), 09's advisory, 03's `peak` flag and 16's band cap, plus 05.6.1's `T_high` and `breadth`. 00.17.1 Q5, 05.6.1, 07.1.2, 04's edge case, WE-04-1 and `callings.yaml` (and its generator header) say the same.
- Alternatives considered: count provisional tiers everywhere (rejected: a lapse would lower Vitality, Focus and the advisory and rebuild every ally's line for a grant the player never kept, the "rise and fall" that 04.8.2 already forbids for the tier-4 attribute); split the two (Vitality confirmed, Focus provisional; rejected: the inconsistency I-037 reports).
- Evidence: verification-1 ch.04 read (V1-006). Pacing: a confirmation lands 12 evidence-bearing scenes after the grant (04.8.2); `04-recog-parity.py`'s I-083 section models the lag (confirmed band) for every style, archer included.
- Serves: goal 2 (one definition), Principle VI (provisional means trial, never a temporary stat bump).
- Revisit if: live logs show the two-to-three-session lag in Vitality after a grant reading as a broken promise.

### DL-04-30: 00.3.7's P4 and P5 PC column widened to what the ladder gives (revision I-063)
- Decision: 00.3.7's PC best-domain base modifier reads P4 **+9…+11** and P5 **+10…+12** (was +10…+11 and +12; `scales.yaml#bands.pc_best_base` the same). 04.5.1's sentence now says the ranges assume the tier-4 increase on that attribute (one lower without it), and that the band's reference PC (T-06-12: +11 at P4, +12 at P5) is the specialist with edge +1 or +2 at the top of the range.
- Alternatives considered: restate 04.5.1 only, leaving a tier-4 specialist at edge 0 "below its band" (rejected: then the PC column of 00.3.7 is not what a band means, and every P4 or P5 character without gear edge would be off-envelope by definition); raise tier-4 competence to +6 (rejected: the base-modifier cap +12 and DL-04-23's ladder, and T-06-12's reference lines would all move).
- Evidence: 04.5.1's arithmetic (competence +5 / +6, attribute +4, edge 0–2); T-06-12's reference lines (+11, +12) lie inside the new ranges, so `06-conflict-sim.py`, 09's audits and PR-09-4 are unchanged (PR-09-4 reads the PC's own line, never the band's range).
- Serves: goal 2 (00 and 04 agree).
- Revisit if: ch.09's second reference PC (I-040) wants a low-edge P4/P5 line for its audits.

### DL-04-31: The world supplies band-4/5 opposition; a tier counts at most two great deeds per opposition (revision I-083)
- Decision: (a) 12.16.11 seeds the **powers of the far rings**: a principal in each ring-4 area at band 4 and each ring-5 area at band 5 (`tbl.12.seed.powers`), each keeping a sealed truth and holding a position; a new region's powers are band 5 (12.16.18); T-12-16 gains `ws.req.04_powers` (63 checks). (b) 04.3.4: at most two of a tier's great deeds come from one opposition (a contest's party, a case or research project, a work; recorded as `contest.opposition`, 03.2.1, `evidence.yaml`).
- Alternatives considered: make a contest's band relative, `max(absolute, power_band + an advisory offset)` (rejected: a contest has no danger estimate to read the offset from, so the offset would be chosen, and a P4 envoy would do band-5 deeds against a village headman; the world should hold the champions a tier-5 deed is done against, as T-10-2's ring 5 already says); guarantee tier-4/5 factions in the seed (rejected: 11.3.4 makes a tier above 3 a realm-scale achievement, and with I-039's binding rule a faction lends only through its head anyway); no per-opposition limit (rejected: the playtest's four band-5 deeds in four days in one archive).
- Evidence: `04-recog-parity.py` I-083 section (200 seeds, 20 seeded worlds, confirmed band): old seed: envoy and scholar never reach tier 5 in 90 sessions; revised seed without powers: never tier 4 (the per-opposition limit needs supply); revised: envoy 19 / 32 / 49, smith 23 / 35 / 48, scholar 19 / 32 / 49 against the archer's 20 / 34 / 52 (tiers 3 / 4 / 5), all within 20%. `12-world-seed.py`: 63 of 63 on seed 1, the guided run and 200 oracle seeds; the powers are drawn on a seed-derived stream of their own, so the committed example changed only by the four powers.
- Serves: goal 1 (R1 #13: every calling has a real path in a generated world, not only in a modelled one).
- Revisit if: T-04-CRISIS logs show a social or lore PC at tier 4 who cannot find a second band-5 party (more powers per region, or a new region earlier).

### DL-04-32: Tiers 2–5 retuned to the pacing targets on the advisory-offset model; a work is one opposition per scene (revision I-034, I-089)
- Decision: keep 04.3.5's targets (tier 1 at 3–5, tier 2 ≈ 9, tier 3 ≈ 18, tier 4 ≈ 32, tier 5 not before 50) and move the weighted thresholds of tiers 2–5: narrow 80 / **160 / 340 / 640 / 1,200** (was 200 / 440 / 800 / 1,300), fine and hybrid ×¾ (60 / 120 / 255 / 480 / 900), broad ×1½ (120 / 240 / 510 / 960 / 1,800); counted stays W ÷ 10 (8 / 16 / 34 / 64 / 120). Tier 1 and every since-field are unchanged. 04.3.4: a **work** counts as one opposition **per scene** worked on it (08.6.4); parties, cases and research projects stay one opposition each. 04.3.5, T-04-8 (R1–R14) and WE-04-1 re-traced from the seeded re-runs; `04-recog04.py`, `04-gen_data04.py`, `04-callings_header.yaml`, `callings.yaml`, `03-counted-yield.py`, `04-recog-parity.py` changed; `09-i005-check.py` prints both ladders.
- Alternatives considered: restate the targets (rejected: 04's Design intent makes the targets the design, chosen before calibration from the precedents, R2 #2, and the thresholds the calibration, "scaled to this game's event rate by simulation and never copied", R3 G-2; the event rate is what DL-00-05 changed); scale every W by one factor, as OEQ-04-1's test proposes (rejected: the targets need ×0.77 at tier 3 and ×0.80 at tier 4 but only ×0.92 at tier 5, whose "not before 50" a common ×0.8 would breach); retune the since-fields (rejected: `04-binding-check.py` shows the weighted total met last at tiers 3–5 in 145–194 of 200 runs, so they do not bind; at tier 2 the quality floor binds but lowering it 10 → 8 moved the median by nothing); lower tier 1 to 70 (rejected: median 5 is inside the 3–5 window, and 80 is quoted by 03, 05, 11 and the examples); keep a work as one opposition for the whole project (rejected: with the faster ladder the smith's tier 3 in seeded worlds fell to 22 against the archer's 16, +38%, outside ±20%; a work's steps are bounded by its progress and spoilage clocks as a fight's by its encounter, so it cannot be farmed as an archive or a door-warden can).
- Evidence: `04-recog04-output.txt` (200 seeds): archer 5 / 10 / 18 / 32 / 54, tier 5 within 60 in 183 of 200, p10 of tier 5 at 50 (was 5 / 12 / 23 / 40 / 60, 103 of 200); swordsman 3 / 7 / 12 / 20 / 34. `04-binding-check-output.txt`: requirement met last per tier, both ladders. `04-recog-parity-output.txt`: I-003 shape archer 15 / 47, envoy 14 / 42, smith 14 / 40, scholar 14 / 42 (all within 15%); seeded worlds (T3 / T4 / T5) archer 16 / 28 / 48, envoy 16 / 27 / 45, smith 17 / 27 / 44, scholar 16 / 27 / 45 (within 8%); the I-039 farming envoy still banks 0 band-4/5 deeds in ten sessions. `09-i005-check-output.txt`, `12-time-pacing-output.txt` (tier 5 at 2.0 / 2.5 world years), `03-counted-yield-output.txt` (the divisor still costs 0 extra fights at tiers 2–5), `04-wren04-output.txt` (WE-04-1).
- Serves: goal 1 (a focused identity deepens at the intended pace: three recognitions of real capability inside a 32-session campaign, a top far away); C:P5.
- Revisit if: T-04-PACE logs put tier 3 outside 16–24 or tier 5 before 50 for focused play (then retune W again; the since-fields stay).

## DL-05 — Abilities, Focus, and Magic

Format per BRIEF §11. Citations per 00.1.6. Numbers consumed by other chapters are marked **[consumed]**.

### DL-05-01: Slot ceiling 20 = 12 calling + 4 acquired + 4 equipped; closed
- Decision: adopt 00.17.1 Q2's reference values unchanged; no effect, item, tier or rite adds a slot or moves one between partitions. **[consumed: 04, 08]**
- Alternatives considered: 24 (14/5/5) (rejected: three callings at tier 3 would no longer fill the calling partition exactly, so the cap would bind later than consolidation becomes attractive); 16 (rejected: a third calling would be starved of picks, working against hybrids); HWFWM-style cap-lifting gifts (rejected: a cap that can be raised is a menu that grows).
- Evidence: [C:V] [C:P5 "hard total-slot ceiling (mirroring HWFWM's fixed 20-ability cap)"] [R2 §05] [R3 05.1] [04.8.4: 3 callings × 4 picks at tier 3 = 12]
- Serves: goal 2 (enumerable state); principles V, VI.
- Revisit if: pick logs show the calling partition full before the second calling reaches tier 3, or never full by tier 5.

### DL-05-02: One shared pool of 251 abilities; the count set by coverage
- Decision: 176 tag-gated abilities (every level-2 deed tag ≥ 2, one at `min_tier` 1; every branch ≥ 14 with ≥ 2 at each `min_tier`), 48 oath-gated (3 per positive conduct axis, 2 per negative), 27 mirrors of ch.04's absorbable powers. No ability belongs to a calling.
- Alternatives considered: a list per calling (forbidden by P5); ~400 abilities, 4–5 per level-2 tag (rejected: authoring and audit surface doubles while a pick shows three candidates; depth comes from forms × ranks × flares × stretch, R3 05.16); a per-branch pool only, ~10 per branch (rejected: 81 level-2 callings would share candidates and narrow callings would have nothing of their own).
- Evidence: [C:P5] [C:V] [04.2.1, 04.8.4, 04 Interface request 3] [R3 05.16]
- Serves: goal 1 (any way of playing finds abilities), goal 2 (enumerable).
- Revisit if: T-05-PICKRATE shows dead or mandatory abilities, or a calling's candidate list repeats across three picks.

### DL-05-03: The shelf (4) for known-but-unslotted acquired abilities
- Decision: a fifth acquired ability is shelved, a ninth is forgotten; re-slotting at a completed long rest. Absorbed powers use ch.04's library instead.
- Alternatives considered: forget at once on the fifth (rejected: punishes learning; no re-slotting possible, which 04 asks for); an unbounded "known" list (rejected: Underworld's unbounded copying, C:V).
- Evidence: [C:V] [R3 04.18, 05.13] [04.10.3]
- Serves: goal 1, principle V.
- Revisit if: players never use the shelf, or routinely hit the cap of nine.

### DL-05-04: A closed grammar of eight ability forms
- Decision: Edge, Lever, Permission, Working, Reaction, Form, Exception, Reserve; each fixes regime, timing and allowed operations.
- Alternatives considered: Fate's three patterns as they stand (rejected: no place for hook-triggered effects, slot claims or resource conversion, which the substrate makes first-class); HWFWM's six categories (rejected: fictional kinds, not mechanical shapes: they do not tell the engine how an ability combines); no grammar (rejected: R1 finds no published game trusting open powers without a list or a grammar).
- Evidence: [R1 §05, M-17] [R: https://fate-srd.com/fate-core/stunts-refresh] [C:P10] [R3 05.5]
- Serves: goal 2; P10.
- Revisit if: more than 5% of proposed abilities in a content pass fit no form.

### DL-05-05: Absorbed powers are mirrored by reference, not re-authored
- Decision: the 27 `gen_absorb.yaml` pool entries appear in `abilities.yaml` with `mirror_of`, a principle, license fields and `slot_class: acquired`; their effects, tiers, costs and limits remain ch.04's. They are not budget-checked by 05.11.
- Alternatives considered: copy the effects (rejected: two sources of truth); leave them out of `abilities.yaml` (rejected: `use_ability` and the codex would need a second lookup).
- Evidence: [04 Interface request 8] [00.16.4]
- Serves: goal 2.
- Revisit if: the Taking's powers prove out of line with pool abilities of the same tier (then 04 re-tiers them with T-05-9).

### DL-05-06: One training license per level-2 deed tag, with grades that mean something
- Decision: 81 `lic.training.*`; grade sets obstacle-tier cap (Hard / Very hard / Legendary), technique cap (`min_tier` 2 / 4 / 5), stretch price and flares; mentor or text path grants `trained` and competence +2; expert and master come only from calling tiers. **[consumed: 01, 02, 04, 15]**
- Alternatives considered: training licenses only where basic verbs exclude the method (04's minimum; rejected: every level-2 calling's Mark needs a license to refer to, and emulation needs a domain license for every tag); grades purchasable by downtime (rejected: P2, power is history-gated).
- Evidence: [00.3.6] [00.12.4] [04.5.1] [WE-00-3] [C:P2] [C:P15]
- Serves: goals 1 and 2; VII.
- Revisit if: the obstacle-tier cap produces refusals players find arbitrary (track G4-by-grade rulings).

### DL-05-07: Stretch is always a rolled beat at DC +5, +1 Focus, Limited reach; grade widens it
- Decision: as stated; expert raises the reach cap to Standard; master removes the DC shift. Two flags decide legality (same operation and object; no sensitive upgrade), tie-break false.
- Alternatives considered: a flat extra Focus with no roll (rejected: unbounded leniency risk, R4); a rung-based "how far is the stretch" ladder (rejected: a `[J:rung]` where a `[J:flag]` suffices, P-A).
- Evidence: [R2 #4 Mother of Learning] [R: http://www.redcap.org/page/Spontaneous_spell] [01.3.5] [R7 §4.4] [R4 SG-05]
- Serves: goal 1 (the strongest in-bounds creativity mechanism), goal 2.
- Revisit if: T-05-STRETCH agreement is under 85%.

### DL-05-08: Emulation needs the training license and a witnessed fact; it feeds a learning clock
- Decision: DC +5, Focus ×2, Limited reach; technique cap by grade; success ticks `clk.learn` by delivered reach; clocks of 6 / 8 / 12; mentor 3, text 2, practice 1 per week. **[consumed: 04, 15]**
- Alternatives considered: anyone may emulate (rejected: VII; non-holders get the crude fallback); emulation teaches at once on a critical success (rejected: INV-7).
- Evidence: [00.12.4] [R7 §4.4, §5 Ex.7] [R: https://www.d20srd.org/srd/skills/useMagicDevice.htm] [C:P15]
- Serves: goal 1; VII; P15.
- Revisit if: T-05-LEARN shows fewer than half of started clocks completing.

### DL-05-09: Focus maximum = base + highest tier + breadth (≤ 3), cap 12; no per-tier cost discount
- Decision: as stated; base 3–5 from ch.02 (reference 4); `T_high` counts specialties' `tier_reached`. **[consumed: 02, 04, 14]**
- Alternatives considered: Stormlight-style efficiency per tier (rejected: every cost in data becomes a moving number; a deeper pool gives the same felt efficiency); attribute-derived maximum (forbidden by 00.3.13); flat pool forever (rejected: a tier-5 character's rank-3 abilities and grand costs need a deeper pool; the simulation's "fraction of pool per fight" would drift).
- Evidence: [00.3.13] [R2 #8] [C:P2] [05-focus-sim.md §3]
- Serves: goal 2; P2, P9.
- Revisit if: T-05-DAY shows high-tier characters never Spent or always Spent.

### DL-05-10: Calling identity through generation, not currency; ch.04's nine triggers confirmed
- Decision: one pool; each family's trigger restores 1 Focus (once per scene from tier 2, twice from tier 4); a cap of 3 Focus generated per scene from triggers, composites, boons and Reserve abilities. **[consumed: 04]**
- Alternatives considered: per-family resources (forbidden by P9); no generation at all (rejected: WoW's lesson that resource shape carries identity, R3 05.7); uncapped generation (rejected: loops with healing and conversion abilities).
- Evidence: [C:P9] [R3 05.7, #13, T-1] [04.5.4]
- Serves: goals 1 and 2.
- Revisit if: T-05-TRIGGER shows a family outside 0.3–0.8 fires per scene.

### DL-05-11: Five discrete cost bands (0–4), band limited by minimum tier
- Decision: knack 0, lesser 1, greater 2, grand 3 (`min_tier` ≥ 3), pinnacle 4 (`min_tier` 5); after modifiers ≤ 6.
- Alternatives considered: continuous costs (rejected: arbitrage between near-equal effects, HERO's lesson); a cost equal to tier (rejected: low-tier abilities become obsolete, high-tier unaffordable).
- Evidence: [R1 §05 HERO brackets] [00.3.13]
- Serves: goal 2.
- Revisit if: the budget audit shows clustering at one band.

### DL-05-12: The push buys reach or stakes, never the roll; open to everyone on trained tags
- Decision: 1 Focus, once per beat, reach +1 or stakes −1, only where competence exceeds the floor; not a lever. **[consumed: 01, 03]**
- Alternatives considered: +2 to the roll (rejected: an ability tax, right on every roll; makes Focus a second modifier family); available on any beat (rejected: removes the meaning of training); no push (rejected: an unrecognized character would have a Focus pool with nothing to spend it on, against P2's floor).
- Evidence: [R1 M-24] [R3 #9] [00.3.9] [C:P2] [01 Interface request]
- Serves: goal 1.
- Revisit if: pushes are used on more than half of all rolled beats (then it is a tax) or almost never.

### DL-05-13: Six flares, +1 Focus each, one per activation (two at master), with a tell
- Decision: Hard, Far, Wide, Lasting, Quiet, Sure; a flared activation is visible and audible; a flared spell miscasts one rung heavier.
- Alternatives considered: free-form "spend more for more" (rejected: an open dial is the −5/+10 problem); support-gem slots per ability (rejected: a second slot system).
- Evidence: [R2 #8 Allomantic flare] [R3 05.3] [R1 M-24]
- Serves: goal 1 within bounds.
- Revisit if: one flare is chosen in more than 60% of flared activations.

### DL-05-14: Recovery: breather +1 (two between short rests), short rest +half (two a day), long rest full
- Decision: as stated, by rest quality; resonant place +1. **[consumed: 07, 10]**
- Alternatives considered: full recovery at any short rest (rejected: Focus stops being a decision); PF2e's ten-minute refocus to full for a 3-point pool (rejected for a 4–12 pool: the hour would be free); long rest only (rejected: the simulation shows a tier-1 character empty by the third fight).
- Evidence: [R: https://2e.aonprd.com/Rules.aspx?ID=276] [05-focus-sim.md: 5 fights sustained with two short rests; empty by fight 4 with breathers only] [00.7.2]
- Serves: goal 2; pacing.
- Revisit if: T-05-DAY shows short rests taken in under 40% or over 70% of opportunities.

### DL-05-15: The reserve: a 1:1 bank-and-draw mode inside the one pool
- Decision: `lic.focus.reserve`, a vessel (an implement), capacity 2 / 3 / 4, charged by a day at a lowered maximum.
- Alternatives considered: a second resource (forbidden by P9); a storage ratio better than 1:1 (rejected: Compounding's near-infinite loop); no reserve (rejected: the brief asks for the Feruchemy shape as a bounded option).
- Evidence: [R2 #8, §05 Feruchemy] [C:P9] [C:P12]
- Serves: goal 1.
- Revisit if: the ledger proves error-prone in play, or the reserve is universal (then fold it into the base).

### DL-05-16: The power budget: allowance = tier + 2·Focus + recharge + timing + limitation + weakness + other cost; value within 2 under
- Decision: T-05-9 effect units; every rank checked by script; passives carry no cost terms and three category limits; a rank is worth 2 EU; composites ≤ 4 EU.
- Alternatives considered: benchmarking against one unit ("a feat = +2", rejected: 5e's trap options); a net budget with Focus priced as a discount (rejected in drafting: under-valued every costed ability); no floor (rejected: comparability needs one).
- Evidence: [R2 §05 power-budget benchmark] [R1 M-22 13th Age] [C:P11] [C:P12] [abilities.yaml#census.budget_slack]
- Serves: goal 2.
- Revisit if: T-05-BUDGET finds same-tier abilities more than 10 points of win rate apart.

### DL-05-17: Composites on three key kinds; priority bands; five ordered spread tags
- Decision: 8 harm-branch, 5 conduct-axis and 9 ability-pair composites (deed-branch pairs are ch.04's); rank bands 10–12 / 15–19 / 20–24 / 30–34 / 40–49; spread order pierce → burst → fork → chain → linger, six targets in total. **[consumed: 06, 08]**
- Alternatives considered: a composite for every pair (rejected: P6's own companion mechanism exists because that does not scale); composites keyed on any two abilities (rejected: high-cardinality keys; only flagged abilities key composites).
- Evidence: [C:P6] [R3 05.4, 05.5, B-1, B-5, E-3] [00.10.7]
- Serves: goals 1 and 2.
- Revisit if: T-00-DEPTH finds intended synergies that need a second link.

### DL-05-18: Three magic sources with engine-applied signatures; three different casting attributes
- Decision: arcane (Intellect; word and gesture; counterable), divine (Presence; sign and regard), primal (Resolve; source present). **[consumed: 02, 04, 13]**
- Alternatives considered: one casting attribute (rejected: 00.4.2's god-stat failure); per-spell components (rejected: authoring cost and recall burden; a branch signature is inherited at zero cost).
- Evidence: [R2 §05 P12 levers by source] [04.2.2 family attributes] [00.4.2]
- Serves: goals 1 and 2; P12.
- Revisit if: one branch's limitation is refused in play far more often than the others'.

### DL-05-19: Miscast replaces the critical failure's cost; fixed table by branch and severity
- Decision: Backlash / Silence / Debt at S1–S4; severity from stakes; +1 rung if flared or emulated.
- Alternatives considered: a corruption track (see DL-05-21); a d100 wild-surge table (rejected: unbounded results; SG-09 asks for table rows the engine applies, and narrator-invented surges are the leniency failure in reverse).
- Evidence: [R5 MG-07] [01.9.2] [R4 SG-09]
- Serves: goal 2.
- Revisit if: T-05-MISCAST shows more than 5% of Risky fights decided by a miscast.

### DL-05-20: Small workings (cantrips) are tool-equivalent, free, and harmless
- Decision: a `[J:flag]` test "could an ordinary person with a common tool do this in the same time?".
- Alternatives considered: no free magic (rejected: casters would feel magical only in fights); a list of cantrips per school (rejected: a list is a menu; the test generalizes).
- Evidence: [C:VII admission test] [R2 §05 MoL] [01.4.1]
- Serves: goal 1.
- Revisit if: small workings are used to obtain levers at a rate that changes outcomes (then the fact they create stops being citable for a scene).

### DL-05-21: No corruption meter
- Decision: magic's dangers are miscast, overdraw, rite failure costs and debts; moral consequence is ch.04's shadows and Fraying.
- Alternatives considered: a taint track (rejected: a second moral ledger beside 03/04's conduct axes; and a slow meter is exactly the state the AI softens, R4).
- Evidence: [R5 MG-07] [04.9] [R4 leniency]
- Serves: goal 2.
- Revisit if: ch.13's canon makes a source inherently corrupting; then it is an affliction of 07's.

### DL-05-22: Non-pick abilities are provisional until used in three scenes
- Decision: confirm at the first reflection after three scenes of use; shelve at the second season boundary otherwise, with a warning.
- Alternatives considered: permanent at once (rejected: VI's provisional default); lapse by deletion (rejected: learning time would be lost; the shelf keeps it).
- Evidence: [C:VI] [00.17.1 Q12] [04.8.2]
- Serves: VI.
- Revisit if: the rule only produces bookkeeping (nothing is ever shelved by it).

### DL-05-23: Healing cap: two Vitality-restoring effects per recipient between long rests
- Decision: as stated; the third restores 0 and the tool says so first. **[consumed: 07, 08]**
- Alternatives considered: no cap (rejected: Focus → Vitality conversion across a day, and the divine Focus trigger makes it self-funding); a cap by the healer (rejected: two healers double it).
- Evidence: [R5 HR-09 WWN System Strain]
- Serves: goal 2.
- Revisit if: T-05-HEAL with ch.07's numbers shows the cap too tight for a solo PC.

### DL-05-24: Rites are known, not held; two racing clocks; rites can be designed by research
- Decision: 24 authored rites; progress vs a 4-segment strain clock; four scales; eight drawn conditions; custom rites provisional. **[consumed: 10, 11, 15]**
- Alternatives considered: rites as abilities (rejected: they would crowd slots and their price is time, not Focus); free-form ritual magic by DM judgment (rejected: `[J:open]` with unbounded effect); conditions chosen by the DM (rejected: the engine draws them; the DM fills specifics from facts).
- Evidence: [R5 MG-04] [R: https://www.dungeonworldsrd.com/classes/wizard/] [R: https://earthdawn.fandom.com/wiki/Spellcasting] [00.8] [C:V]
- Serves: goal 1 (big magic has a door), goal 2.
- Revisit if: designed rites cluster at one scale or one effect.

### DL-05-25: Six new effect definitions in the 05 owner-block
- Decision: `eff.05.spell_delivery`, `eff.05.defense_reaction` (claims for two slots the core library did not seed), `eff.05.waive` (the Exception form), `eff.05.refresh_use`, `eff.05.counter_working`, `eff.05.end_working`.
- Alternatives considered: express each with core effects (tried first, PR-00-8): `eff.prevent_hit` cannot cancel a declared working or a named snag; `eff.cleanse` cannot end a non-condition effect instance; `eff.restore` has no "uses" quantity.
- Evidence: [00.10.1] [PR-00-8] [T-00-14]
- Serves: goal 2.
- Revisit if: 00 amends the core library to cover them (then retire these with `superseded_by`).

### DL-05-26: Spent is a state of Focus, not a condition; overdraw is the bounded exception to "no Vitality into Focus"
- Decision: at 0 Focus sustained workings end, concentration is snagged, no flare or push; overdraw pays a shortfall of 1–3 with S2–S4 strain harm and an exhaustion stack, three times per long rest, never to 0 Vitality.
- Alternatives considered: a new `cond.spent` (rejected: conditions are ch.06's file and Spent is cleansed only by Focus); unconsciousness at 0 (rejected: removes the player from play); free overdraw (rejected: Vitality becomes the Focus pool).
- Evidence: [R2 #8 Stormlight exhaustion] [R5 MG-07] [05-focus-sim.md: a caster at 0 wins 0.1%]
- Serves: goals 1 and 2.
- Revisit if: overdraw is used in more than a third of fights (the pool is then too small).

### DL-05-27: Ranks follow ch.04's formula; a consolidated pick keeps its specialty's tier
- Decision: `rank = min(authored, 1 + floor((T − min_tier) ÷ 2))`; for a pick carried through consolidation or fork, `T` = max(new tier, specialty `tier_reached`); acquired partition rank 1.
- Alternatives considered: ranks drop with the new calling's tier (rejected: contradicts 04.8.5's "nothing is lost on the day").
- Evidence: [04.5.5, 04.8.5] [R2 #3]
- Serves: VI (restated, never appended).
- Revisit if: 04 rejects the request (then consolidation needs a different statement of what is kept).

### DL-05-28: Oath-gated abilities carry non-magic first tags and a pole
- Decision: the 48 conduct abilities have martial, influence, lore or guile first tags and `conduct_pole`; eligibility needs the axis and the pole.
- Alternatives considered: divine first tags (rejected: they would be spells needing a school's training, which a vow does not grant); no pole (rejected: vows and dark callings share an axis in ch.04's pool gate).
- Evidence: [04.2.5, 04.8.4] [05.7.1]
- Serves: goal 2.
- Revisit if: 04 separates the pool gates by pole itself.

### DL-05-29: Pattern deviations recorded
- Decision: (a) **P3's comprehension wall** is not used as a design constraint (BRIEF §3; recorded centrally, DL-00-01): the pool is 251 and a sheet may hold 20; the codex carries it. (b) **P5's "passive: no usage state"** is kept exactly; anything with a use or cost is active, including automatic triggers (they have `timing: trigger`). (c) **P10**: Permissions and Exceptions are prose permissions with fixed triggers; they may carry core power because each is a lookup with no judgment at the point of use, or one `[J:flag]`. (d) **P14**: no cadence parameter is defined here; identity lives in Focus generation (DL-05-10).
- Alternatives considered: n/a.
- Evidence: [C:P3] [C:P5] [C:P10] [C:P14] [BRIEF §3]
- Serves: traceability.
- Revisit if: the constitution is amended.

### DL-05-30: Data files are generated from authored tables and validated by script
- Decision: `rules/_process/simulation/05-gen_data05/` holds the authoring tables and the generator; hand edits to the four data files are overwritten by the next run.
- Alternatives considered: hand-written YAML (rejected: 251 entries × 30 fields; ids, tags, budgets and coverage could not be kept consistent by eye).
- Evidence: [00.16.4] [03 and 04 used the same method]
- Serves: goal 2.
- Revisit if: the engine's loader takes over validation.

### DL-05-31: One zero-cost branch working per magic branch, held through training (revision I-009)
- Decision: add Force Bolt (arcane), Rebuke (divine) and Wild Lash (primal) as `ab.*` records with `slot_class: license` (05.7.11). Every holder of a training license of the branch holds its working; it takes no slot and is never picked. 0 Focus, at will, one action, aimed against Guard. Severity follows the grade in the casting school's license (trained S2, expert S3, master S4), the same steps as 06.4.5's weapon mastery. Each branch keeps a fictional identity: raw force that can shove (arcane), the keeper's regard against its opposite (divine), and the source present striking for you (primal). The frame's deed tag is the school the caster names, so competence, evidence and `cnt.focus` land there.
- Alternatives considered: (a) ordinary pool abilities picked into a slot: rejected, because a fighter's Strike costs no slot, so a caster would pay a slot tax for the same floor, and a new character (who holds one ability at most, 02.5.4) could not have both its spell and its working. (b) Severity by calling tier, as 05.3.9's rank rule gives: rejected, because a broad caster would then outgrow a broad fighter at tier 3; reading the grade keeps the two in step. (c) One rung lighter (S1/S2/S3): simulated (section J5), a Spent P3 caster beats one T3 66.0% with Force Bolt, 60.6% with Rebuke and 27.9% with Wild Lash, whose physical harm armor reduces; the primal branch fails the ≥ 40% acceptance, and keeping it would need a severity per branch instead of one rule shared with 06.4.5's mastery. (d) Forbidding the push on the working, so that Focus flows only into spells: rejected, because 05.6.7 makes the push universal and the simulation shows the push gives a caster the same gain it gives a fighter.
- Evidence: `06-conflict-sim.py` section J (20,000 fights a row): a new caster (+5) on the working alone beats one T2 92.8–93.6% (staff 51.3%); a Spent P3 caster beats one T3 80.7–91.0% (74.5–86.8% against 09's Fend), against 0.4% before; at P1–P5 the best branch gives 100 / 99 / 91 / 48 / 30% against the no-Focus specialist's 100 / 100 / 99.7 / 87 / 80%. Focus: the push lifts a P3 caster against one T4 from 34% to 55% and against two T3 from 26% to 47% (a fighter: 62→84, 73→90). `02-gen_data02/sim02.py`: every default-path new caster beats one T2 90.5–94.8%. [06.10.6; 06 IR (b) to 05; I-006; I-009; R5 MG-07]
- Serves: goal 1 (a caster can always try something in a fight) and goal 2 (the working is a record the engine executes; the DM never invents a staff-swing for a mage).
- Revisit if: T-05-BUDGET or playtests show 1-Focus damage spells chosen in under 20% of a caster's Focus spends (the working plus a push crowding them out; see the ledger row on damage-over-time weighting), or a Spent caster's win rate against an equal-band foe exceeds the broad fighter's at any band.

### DL-05-32: A min_tier-1 working for each primal element (revision I-015)
- Decision: add Undertow (water), Stolen Breath (air) and Heave (earth) under `deed.primal.elements`, each a 1-Focus resisted Working budgeted at tier 1 with three ranks. The Touched's spark grants the working of the element the player names or the engine draws (02.6.3; `gen_birth.yaml#birth.gift.elements.gifted_ability_by_element`).
- Alternatives considered: water and air only, as the ledger asked: rejected, because the only earth ability (Stone Shape) has `min_tier` 3 and is not a legal gifted technique (02.5.4), so an earth spark would also have started with nothing of its own; giving every spark Cinder Stride: rejected, the gift's text names four elements.
- Evidence: 02.6.3; 02.5.4; T-02-7; I-015.
- Serves: goal 1 (the concept "I have always been able to call the water" plays from the first scene).
- Revisit if: pick logs show one element's working dominating the elements pool (T-05-PICKRATE).

### DL-05-33: Tier-5 abilities for every dark pole, and a ladder proved by script (revision I-007)
- Decision: author one `min_tier` 5 ability per negative pole (No Quarter, Web of Lies, The Last Embrace, Hoard-Heart, Iron Decree, Peerless, Wrath Unbound, Unhallow, The Cold Calculus), budgeted at tier 5 like the positive set and each carrying its pole's appetite as a mechanic (refused quarter, a planted story, a betrayal recorded, Focus from theft, a forbidding decree, glory alone, fury that burns the body, a desecration, a life spent for one's own). `05-ladder-check.py` applies 04.8.4's pool gate to every calling × axis × tier and fails on a pick with no candidate; the generator's coverage check now requires min_tier 1, 3 and 5 on every pole a calling uses. The check also found the Monk's conduct gate dead (no `pole`), fixed in ch.04's generator (`pole: positive`).
- Alternatives considered: let the tier-5 dark pick fall back to any oath ability on the axis regardless of pole: rejected, 04.8.4 forbids crossing poles; give dark callings a smaller allowance: rejected, it would make the dark road strictly worse rather than different. Middle tiers: the allowance rises only at tiers 1, 3 and 5, and the light poles also have nothing at 2 and 4, so nothing was added there.
- Evidence: `05-ladder-check-output.txt` (183 callings, 20 conduct calling × axis rows, 0 failures; against the pre-revision data 19 failures: 18 dark tier-5 holes and the Monk gate). [04.8.4; 05.2.4; 05.3.10; I-007]
- Serves: goal 1 (a dark road is a full road), goal 2 (no pick is silently kept).
- Revisit if: T-05-PICKRATE shows a dark tier-5 ability never taken when offered.

### DL-05-34: `replaces` chains and derived flare lists are not gaps (revision I-008)
- Decision: neither is a gap; both are kept and now checked. (1) `replaces`: an ability grows by restated ranks (05.3.9), so no upgrade chain is needed for growth; `replaces` is the content-lifecycle link of 05.12.3 (a new entry sharing a `mod_group` must replace or retire the old) and of 05.2.5 (the upgrade takes the old slot). The generator now enforces 05.12.3 (a shared `mod_group` without a `replaces` link, or a link to an unknown id, is an error); the current pool has no shared `mod_group`, so no chain is owed. (2) Flare lists are derived from each record's effects by 05.6.8's "listed when" column, which is the rule; a hand-picked list would drift from the effects it describes. The audit found one place where the derivation and the rule text disagreed: 35 spells list Quiet without a sense trait. The derivation is right (a working of magic is always perceived through its limitation: word, sign or stirred source), so 05.6.8's column now says so.
- Alternatives considered: hand-authored flare lists (rejected: unverifiable at 239 records); authoring upgrade chains now (rejected: it would duplicate what ranks already do and grow the pool without a coverage hole, against 05.11.6).
- Evidence: audit in revision A (`gen_data05.py` check; 0 shared mod_groups; 35 Quiet-without-sense spells, all magic). [05.2.5; 05.3.9; 05.6.8; 05.12.3]
- Serves: goal 2.
- Revisit if: content passes add abilities in an existing `mod_group` (the script will then demand the chain).

### DL-05-35: A keeper grants only the schools it keeps, and has a nature (revision I-052)
- Decision: 05.7.4: a divine license's school must be one of its keeper's schools (PC, pregen or NPC priest); every keeper record states `nature: sacred | profane` (12.16.6), which Rebuke and every "sacred/profane keeper" effect reads. The seed generator picks the Acolyte pregen's school from the main keeper and filters NPC priests' licenses; the seed check enforces both.
- Evidence: verification-1 playtest (Evella trained in healing under a war god; `dark: false` undefined); `12-world-seed.py` PASS (62/62, 200 oracle seeds 0 fails).
- Serves: goal 2 (no undefined field, no illegal pregen).

### DL-05-36: The keeper's regard fails at Fraying stage 3, not 2 (revision I-064)
- Decision: 05.7.4: an oath-bearing divine calling keeps its keeper's regard through stages 0–2; at stage 2 its spells work one tier down with the calling (04.9.3), at stage 3 regard fails, and while an atonement clock runs from stage 3 the calling is read at stage 2 (04.9.4), so the spells return one tier down. The edge case "acts against the keeper's axes" and WE-04-6's atonement say the same.
- Alternatives considered: keep stage 2 as the cut-off and have 04.9.3 / 04.9.4 say divine spells fall silent from stage 2 (rejected: stage 2 would then be a near-total loss for a Paladin and almost nothing for a Ranger, and an atoning Paladin could do no divine deed toward the atonement; 04's three stages are graduated by design, and stage 1 already removes the oath-gated abilities).
- Evidence: verification-2a ch.05 read; 04.9.3's stage table; 04.9.4's atonement state.
- Serves: goal 2 (04 and 05 agree); C:P5 ("a Paladin's ability to atone").
- Revisit if: live play shows a stage-2 caster's spells undercut the warning that stage 2 is meant to be.

### DL-05-37: The training path's +2 entries are capped; counted units outside a scene settle by day (revision I-047)
- Decision: 05.9.3: competence entries of source `taught` are capped at learning picks (02.5.6) + the highest confirmed tier among held callings, minimum 1; a license past the cap is held as access (02.5.2) unless the player sets aside a taught entry at a long rest; training an access-held license is deepening (same clock, writes +2, within the cap). `licenses.yaml#training_competence_cap` (via `emit05.py`). 03.7.3: counted units written outside a scene (downtime weeks, long and Safe projects) settle per day, so `cnt.progress` and `cnt.made` saturate per counter, node and day.
- Alternatives considered: cap the licenses themselves (rejected: breadth of permission is the Broad profile's point, 02.5.2, and 05.9.4's "breadth is available and is not power"); no cap (the red-team's +2 everywhere for a PC with spare weeks); a flat cap of 2 (rejected: gives the tier-5 sage the novice's breadth of depth; Intellect is the attribute whose one derived value is learning, 00.4.4).
- Evidence: verification-1 red team (I-047); 02.5.2's audit values a deep license at 2 units and access at 1, so each uncapped month of mentoring added a deep unit no profile could buy at creation.
- Serves: C:P4 (breadth against competence); goal 1 (depth comes from deeds).
- Revisit if: T-05 playtests show a high-Intellect character holding more +2 entries than a focused calling of the same tier grants competence (then drop learning picks from the cap).

### DL-05-38: Every level-2 deed tag has a min_tier-4 and a min_tier-5 ability (revision I-087)
- Decision: 05.11.6 adds a coverage floor: each of the 81 level-2 deed tags holds at least one tag-gated ability at `min_tier` 4 and one at `min_tier` 5, so that a narrow calling's own pool (its level-2 parent's subtree, 04.8.4) can fill its tier-4 and tier-5 picks from its own art. 123 abilities were authored to meet it (`05-gen_data05/ab_deep.py`; 61 at `min_tier` 4, 62 at `min_tier` 5), one rank each, each with its own name, `mod_group`, principle and exclusions, each priced by 05.11 (T-05-9) and passed by `gen_data05.py`'s budget, grammar, id and lint checks. `gen_data05.py`'s coverage check now fails on a gap, and the validator's `POOLS` INFO reports nodes lacking either tier. The pool is 389 entries (302 tag-gated); `gen_item_ability.yaml#pool` gains the 117 active ones (279).
- Alternatives considered: one tier-4-or-5 ability per node, as C2b's audit counted (rejected: a narrow calling has picks at both tiers 4 and 5, and 62 nodes would still send their tier-5 pick to kin); leaving depth to kin picks (rejected: legal under 04.8.4, but the tier-5 pick of most narrow callings then did not deepen their art, the I-087 finding); widening the own pool to the branch (rejected: it erases what makes a narrow calling narrow).
- Evidence: verification-2c long-arc playtest (I-087); `validate_ruleset.py -v` POOLS before: 43 of 81 nodes with no min_tier 4+, 92 of 132 specialists with no own-pool tier-5; after: 0 of 81 nodes lacking min_tier 4 or 5, 0 specialists with no own-pool tier-5; `05-ladder-check-output.txt` (183 callings, 0 failures).
- Serves: goal 1 (depth comes from deeds); C:P5 (the shared pool serves every calling); C:V (coverage, not taste, sets the count).
- Revisit if: OEQ-05-6's pick-rate logs show tier-4/5 entries of one node never picked (fold them) or always picked (re-price them).

## DL-06 — Conflict

Format per BRIEF §11. Citations per 00.1.6. Numbers consumed by other chapters are marked **[consumed]**.
Simulation: `rules/_process/simulation/06-conflict-sim.py` (seeded `random.Random(606)`, 20,000 fights per
row), output `06-conflict-sim-output.txt`, write-up `06-conflict-sim.md`.

### DL-06-01: Budget of 3 actions + 1 reaction for the PC, 2 actions for every adversary, 0 for companions
- Decision: PC 3 actions and 1 reaction; adversaries 2 actions at every threat band, reactions by band (T1 none, T2+ one); a mob 2 actions and no reaction; a companion no actions (commanded only) and 1 reaction. Chapter 09 may not raise an adversary's actions. **[consumed: 05, 09, 12, 16]**
- Alternatives considered: symmetric 3/3 (PF2e as written; rejected: two same-band foes would make six attack rolls a round against a lone PC, and every enemy action is a narrated beat in text: slow and lethal); 5e's action/bonus/reaction (rejected: a second action type splits builds into busy and idle, R1 M-12); a `solo` template with 3 actions (rejected: a single rule is more reliable for the AI, and a lone adversary's threat is better carried by heavier, announced blows, DL-06-17); adversaries with 1 action (rejected: Move-then-Strike would be impossible in a turn, so melee foes would never close and attack).
- Evidence: [C:P9] [INV-11] [R1 #7, M-11, M-14 (Lancer NPCs cannot Overcharge or Brace: https://lancer-faq.netlify.app/)] [R: https://2e.aonprd.com/Traits.aspx?ID=653 (minions: 2 actions, no reactions, only when commanded)] [01.2.3: three beats per declaration]. Simulation A/B: with 3 vs 2, one same-band foe is won 80–100%; two are "hard" to "lethal".
- Serves: goal 2 (fewer rolls and no target-choice drift per round), goal 1 (three beats is room for a move, a trick and a blow); P9.
- Revisit if: T-06-ECON (OEQ-06-1) fails with chapter 09's final templates.

### DL-06-02: P9 versus P14 resolved: cadence lives in what one action contains, in tempo, and in reactions
- Decision: no build, calling, effect or template changes anyone's number of actions. Cadence differences are (a) weapon weight (three Moderate blows or one Heavy blow plus a spare action), riders, flares and the push; (b) tempo (who acts before whom); (c) which defense reaction a character has, and a possible second reaction from a stance. **[consumed: 04, 05, 08]**
- Alternatives considered: a faster group gets a fourth action (WoW's literal 1.0 s vs 1.5 s translated: 1.5× the actions; forbidden by P9 and INV-11); a per-calling repetition sequence (rejected: callings are derived labels with no place to store it, and it would be a hidden accuracy stat); an Ironsworn-style initiative token kept on a strong hit (rejected: it makes the PC's roll quality decide whether foes act at all, which collides with engine-run adversary turns, 06.9).
- Evidence: [C:P9] [C:P14] [00.17.1 Q21] [R3 §06.4 options (a)–(c), T-2, F-2]. Simulation C/D: heavy vs one-handed within 6 points unaided at every row, and ahead with Focus (P2 vs T3: 78% vs 72%): a feel difference with no budget difference.
- Serves: principle V and P9 (no action stacking), P14 (a structural feel difference).
- Revisit if: playtests show weapon weight is not felt as cadence (then add a third weight before touching the budget).

### DL-06-03: Repetition snags 0 / −2 / −4, adopted from 01 unchanged
- Decision: the k-th attack-trait beat in a turn takes 0, −2, −4 as engine snags; a heavy Strike is one attack; reactions are outside the window; each companion has its own window. **[consumed: 01, 05, 09]**
- Alternatives considered: 0/−4/−4 (inside the cap; costs about 5% of a three-Strike turn's harm and does little to change the choice); PF2e's −5/−10 (outside the ±4 circumstance cap; would need a new modifier family, DL-01-08); a hard cap of two attacks a turn (rejected: a wall, and "ten arrows" deserves three).
- Evidence: [01.14.3; DL-01-08] [R7 §5 Ex.7] [R: https://2e.aonprd.com/Rules.aspx?ID=220]. Arithmetic: +5 vs Guard 15 → 55/45/35%, at least one hit 84%.
- Serves: goal 1 (repetition is real), goal 2 (quantity is never difficulty).
- Revisit if: T-06-VARIETY (OEQ-06-2) shows more than half of PC turns are three attacks.

### DL-06-04: Tempo is one PC roll compared with every adversary's static tempo DC
- Decision: `d20 + Wits + competence(deed.martial.tactics.reading)`; adversaries with tempo DC above the total act before the PC, the rest after; fixed for the conflict; natural 20 seizes, natural 1 goes last; the PC may Delay. Reference DCs 10–14 by band. **[consumed: 09, 12]**
- Alternatives considered: a roll per participant (PF2e; many rolls of bookkeeping before anyone acts); side initiative (Wits matters only in round one); a token bag (Troika: order the player cannot plan around, and randomness per draw the AI must narrate each time); popcorn or free-form (no engine order to enforce).
- Evidence: [00.4.4 Wits → tempo] [00.3.3 one roll by the acting side] [R: https://2e.aonprd.com/Rules.aspx?ID=2423] [R: https://troikasrd.ttrpg.tools/the-rules/05-initiative/] [R3 §06.5] [R5 CF-01].
- Serves: goal 2 (one roll, a stored order), goal 1 (the player can plan around a known order).
- Revisit if: fights against 4+ individual foes show the interleaving is mis-narrated (then fall back to "fast foes, PC, slow foes" blocks, which this already is).

### DL-06-05: Surprise is a condition from state: one action on the first turn, last in round 1, no reaction, a lever to attackers
- Decision: `cond.surprised` for participants unaware of every enemy that acts against them at `conflict_start`; never from speed alone.
- Alternatives considered: a lost first turn (classic; with one PC it is a free round of every foe's attacks: too close to "one unlucky roll"); no surprise rule, hidden lever only (underpays ambushes, which the game wants to reward).
- Evidence: [R5 CF-01] [R: https://2e.aonprd.com/Rules.aspx?ID=2541] [BRIEF §4]. Arithmetic: a surprised P1 PC faces at most 4 attacks from two T2 foes before acting, expected harm about 5 to 8 of 12 by her armor.
- Serves: goal 1 (ambush pays), the lethality lock (ambush of the PC is survivable).
- Revisit if: ambushes by the PC end fights before round 2 in more than half of playtest cases.

### DL-06-06: Weapon weights: every real weapon is Moderate or Heavy; a heavy weapon's Strike costs two actions
- Decision: T-06-6: unarmed S1; light and one-handed S2 at 1 action; heavy S3 at 2 actions; bows S2; crossbows S2/S3 with reloads of 1/2; a closed list of 12 properties, at most two per item. **[consumed: 08, 09, 05]**
- Alternatives considered: S1 light / S2 one-handed / S3 heavy all at 1 action (with harm 1/3/5 a light weapon is a third of a sword and a heavy one dominates; computed at +5 vs Guard 13: heavy at 1 action deals about 56% more per turn); harm-edge +1 for "martial" weapons (eats half the +2 harm-edge cap that items and abilities need); weapon dice (forbidden: 00.3.11 fixed harm).
- Evidence: [00.3.11] [01.18.8 "weapon base severity (08)"] [R3 §06.12 weapons define kit] [R: https://www.dungeonworldsrd.com/equipment/ (range and property tags instead of damage ladders)]. Arithmetic at +5 vs Guard 13: two one-handed Strikes 4.0 expected harm, one heavy Strike 3.7, and 1.6 vs 2.4 through reduction 2.
- Serves: goal 2 (two severities to remember), goal 1 (weapons differ by what they let you do).
- Revisit if: chapter 08's items need a third severity for balance.

### DL-06-07: Position is PC-centric bands + engagement links + groups + ten flags; Flank is an action
- Decision: one band per participant to the PC, links per pair, a group label for derived bands between others (06.3.4), seven reserved flags plus `flag.obscured`, `flag.in_chokepoint`, `flag.aloft`; `flag.flanked` requires an enemy to spend an action. **[consumed: 05, 09, 10, 12]**
- Alternatives considered: a full pairwise band matrix (N(N−1)/2 relations to keep consistent: the triangle problem); Fate zones (clean, but 00.6.1 and the tool surface define position as band-to-participant plus flags, and 05's pool was written to bands); automatic flanking whenever two foes are engaged (Savage Worlds' gang-up as a free bonus: with one PC it would make every second foe worth +2 to both for no decision; as an action it taxes the opposition's small budget and gives the player a turn to answer).
- Evidence: [00.6.1; 00.17.1 Q14] [R3 #7, §06.2 synthesis] [R: https://fate-srd.com/fate-core/movement] [R: https://www.dungeonworldsrd.com/equipment/] [R: https://samhaine.wordpress.com/2020/04/06/savage-worlds-rules-summary/ (gang up)] [R1 §06 positions must be state].
- Serves: goal 2 (a small enum the AI can hold and the auditor can check), goal 1 (terrain is usable because it is state).
- Revisit if: T-06-POS (OEQ-06-3) shows more than one position mismatch per fight.

### DL-06-08: Guard = Agility defense with the readied weapon's or shield's competence; a Strike on an unaware target still rolls against Guard
- Decision: guard tag = readied melee weapon or shield, else `deed.martial.unarmed`, ancestors count, shooting weapons give none; unaware targets give levers (surprised or hidden), not a different defense; the weapon tag is primary and ambush is a grounded secondary. **[consumed: 01, 03, 05, 09]**
- Alternatives considered: Guard without competence (a master swordsman as easy to hit as a clerk); competence from any held weapon (an archer parrying with a bow); rolling against Wits for every unaware target (DL-03-24's first branch as the default: a hunter would lose her archery competence shooting an unwary deer).
- Evidence: [00.3.8 opposed defense "for the attribute and tag the method works against"] [00.3.7 reference Guard 14 for Wren] [DL-03-24] [01 Interface request].
- Serves: goal 2 (one defense for every Strike), P4/P5 (competence follows the skill tested).
- Revisit if: 03's evidence shows ambush callings starved by the secondary-tag half value.

### DL-06-09: Mastery: the Strike's base severity rises one rung at training grade expert and two at master
- Decision: read from the `lic.training.martial_*` grade covering the weapon tag (expert: narrow/fine tier 3, broad/hybrid tier 4; master: narrow/fine tier 5); part of E1 base, outside the ±2 effect-step cap; not for workings or adversaries. **[consumed: 04, 05, 08, 09]**
- Alternatives considered: no scaling (the first simulation pass, before this rule: a tier-4 fighter with S2 Strikes won 2.8% against one T4 foe without Focus: issue I-006 generalized); harm edge by tier (collides with the +2 cap); extra attacks by tier (INV-11); lowering adversary Vitality at high bands instead (outside 00.3.7's envelope: T4 has a 20-Vitality floor).
- Evidence: [issue I-006] [R: https://www.13thagesrd.com/combat-rules/ (weapon dice scale with advancement)] [R1 §06 crit and scaling notes] [05.9.2 grades] simulation A/E: with mastery, specialist no-Focus win rates vs one same-band foe 100/100/99.7/87/80; broad calling 87 (P3), 73 (P4).
- Serves: goal 1 (a martial character is never only as good as their Focus), P4 (breadth costs: broad callings reach the rung a tier later).
- Revisit if: T-06-MASTERY (OEQ-06-9).

### DL-06-10: Called shots: a fixed −2 engine snag for one effect from a closed list
- Decision: gap (ignore worn armor), leg (slowed), arm (weakened; drops on a critical), head (−4; dazed), weak spot (extra Amplifying lever), held object.
- Alternatives considered: hit locations on every attack (bookkeeping with no decision); free-form "called shot = DM decides" (the leniency failure); calling as a reach trade (collides with 01.7.3's single trade).
- Evidence: [R: https://samhaine.wordpress.com/2020/04/06/savage-worlds-rules-summary/ (limb −2, head −4)] [01.18.8 "effects beyond harm are not free riders"] simulation C: calling the gap raises P3 vs T4 from 62% to 73%.
- Serves: goal 1 (a no-Focus answer to armor; "I go for the eyes" has a ruling), goal 2 (closed list).
- Revisit if: one call is chosen in more than 60% of called Strikes.

### DL-06-11: Environment use is anchor selection by intended change, with size rungs for objects and forty ready rulings
- Decision: 06.5.10's first-match list; T-06-8 (hand S1 / body S2 / heavy S3 / massive S4); T-06-9; one roll against the higher of the object's DC and the Guard for aimed drops; features as a closed `feature_kind` enum written on mention.
- Alternatives considered: a stunt bonus for creativity (Exalted/Feng Shui: pays prose, not facts; R7 §3.3); a separate "improvised action" subsystem (a second resolution path to keep consistent); the DM sets a DC per stunt (SG-01).
- Evidence: [R7 §3.4, §5 Ex.1 and Ex.9] [01.5.3 two-change limit] [WE-01-9] [R1 §06 terrain is the challenge] [R5 CF-12].
- Serves: goal 1 (anything in the scene is usable), goal 2 (a lookup, logged as precedent).
- Revisit if: T-06-ANCHOR (OEQ-06-8) agreement falls below 85%.

### DL-06-12: Four conditions added: surprised, silenced, broken, heartened
- Decision: 27 conditions in all. `cond.heartened` is the single carrier of the status family's bonus (+1/+2).
- Alternatives considered: a longer list (HWFWM's ~35 statuses is the named tracking-burden case, R2 §06); folding surprise into dazed (different rules: order and levers); morale as a bare fact (a visible condition has narration obligations and a restriction the behavior list reads).
- Evidence: [00.9.4 "it may add more"] [01.17 `trait.action.speech` names "silenced"] [00.3.5 status best bonus].
- Serves: goal 2 (closed, small vocabulary).
- Revisit if: chapters 07/09/10 need a condition not expressible as one of the 27 plus an affliction stage.

### DL-06-13: A condition speaks in three voices only: bearer's status, engine-cited levers or snags for others, restrictions and periodic effects
- Decision: as 06.7.2. `cond.exposed` is a Precision lever for attackers (05's request); `cond.off_balance` is a bearer penalty and a citable, not automatic, lever.
- Alternatives considered: every condition as a defense penalty (status on Guard stacks with levers to +8 swings); every condition as a lever (crowds out the player's own two cited levers).
- Evidence: [00.3.5 families] [00.9.3] [05 Interface request (a)] [WE-00-6 (off-balance cited as a lever by the player)].
- Serves: goal 2 (no pairwise rules; caps bound every stack).
- Revisit if: playtests show automatic levers leaving no room for cited ones in more than a third of attacks.

### DL-06-14: Control diminishes on one shared counter per target: second application halved, third fails, −1 per round free
- Decision: control = restrained, pinned, blinded, dazed, stunned, frozen, charmed, frightened S3. **[consumed: 05, 09]**
- Alternatives considered: per-condition counters (00's PR-00-5 as written: alternating stun and blind would evade it); WoW's reset after a fixed time (a 16-second window is 3 rounds: equivalent to this decay); immunity after one (too protective of adversaries: control builds would be worthless).
- Evidence: [R3 §06.7 (halving, immunity, reset)] [00.9.3 e] [BRIEF §4].
- Serves: the lethality lock (no stun-lock of a solo PC), goal 1 (control stays useful when spaced).
- Revisit if: T-06-CONTROL (OEQ-06-10).

### DL-06-15: Shapes: 05's five spread tags adopted with their caps and order; `cone` added as a sixth
- Decision: pierce 4, burst 6, cone 4, fork 5, chain 3, linger 5; six targets in all; engine selects by fixed tie-breaks. **[consumed: 05, 09]**
- Alternatives considered: the five only (dragon breath and swung or falling masses would have to be `burst`, which reads oddly for effects that start at the source); geometry (R3 §06.3: a real capability ceiling for a text DM).
- Evidence: [05.10.4] [R3 §06.3, #7] [C:P6 companion: a fixed total order].
- Serves: goal 2.
- Revisit if: 05 prefers to carry `cone` as a spread tag (then the mapping in Interface requests becomes identity).

### DL-06-16: Adversaries run from behavior lists; targets by a fixed attention order; four default lists
- Decision: 06.9.1–06.9.4; taunts add to the attention score. **[consumed: 09, 12]**
- Alternatives considered: the DM picks plausible actions (W3 positivity bias: enemies that never press; "nonsensical outcomes when the system failed to identify an appropriate target"); a full threat table as in WoW (more state than one PC and a few companions need).
- Evidence: [R4 §9 06 item 4, §6.2 item 3] [R: https://arxiv.org/abs/2502.19519] [R3 §06.8] [A2 #10].
- Serves: goal 2.
- Revisit if: playtests show adversaries behaving stupidly in ways a longer default list would fix (then lengthen the lists, never return the choice to the narrator).

### DL-06-17: Heavy blows (base S4+, or shaped) need a visible Windup on an earlier turn
- Decision: 06.9.5; a spoiled windup must be repeated. **[consumed: 07, 09]**
- Alternatives considered: no rule (a T4 foe's S4 critical is 12 Vitality unannounced); a per-fight warning only (07's lethal warning: necessary, but not a decision point); cooldown dice (5e recharge: randomness without a tell).
- Evidence: [BRIEF §4] [R6 §C.2.1 warning layer] [R4 §6.2 item 4: telegraphing as a state] simulation: T4/T5 lines include the windup; equal-band wins at P4/P5 are 87/80%.
- Serves: goal 1 (a turn to answer the worst blow), the lethality lock.
- Revisit if: T-06-WINDUP (OEQ-06-5).

### DL-06-18: Morale is a tug clock per side with closed tick sources and mandatory omens
- Decision: nerve skittish 4 / steady 6 / resolute 8 / fearless none; sources as 06.11.3; break rows by state. **[consumed: 05 (`ab.commanding_ground`), 09, 11]**
- Alternatives considered: OSE's 2d6 checks at first death and half strength (kept as the two largest tick moments; rejected as dice because a hidden roll gives the player nothing to work and the narrator a chance to soften); Shadowdark's single check at half; DM judgment (the leniency channel, R1 T-5).
- Evidence: [R: https://oldschoolessentials.necroticgnome.com/srd/index.php/Morale_(Optional_Rule)] [R: https://billhook.bearblog.dev/saves-and-morale-in-shadowdark/] [R: https://cairnrpg.com/first-edition/cairn-srd/] [00.8 one clock] [R2 §06 morale tracks] simulation B/G: with morale, P3 vs two T3 73% (68% fearless); P1 vs a T1 mob of six 95% (74% fearless).
- Serves: goal 1 (the player can aim at their nerve), goal 2 (deterministic), INV-14.
- Revisit if: T-06-MORALE (OEQ-06-4).

### DL-06-19: Command costs one PC action for one companion beat; five standing orders set what a companion keeps and what its reaction does
- Decision: 06.14. **[consumed: 05, 16]**
- Alternatives considered: PF2e's one action for two minion actions (adds beats to the round: an action-economy multiplier per companion); companions on their own turns (the documented failure point of every action economy, R1 §06); companions as pure levers (denies them bodies, positions and harm).
- Evidence: [00.17.1 Q8] [INV-11] [R: https://2e.aonprd.com/Traits.aspx?ID=653] [R1 G-5] [R5 CF-13, NP-05].
- Serves: P9; goal 1 (allies matter by position and capability).
- Revisit if: chapter 16's playtests show companions never commanded (then let one standing order grant a free one-band Move, nothing more).

### DL-06-20: A mob is one entity with pooled Vitality and a numbers step; a swarm is a mob of tiny creatures
- Decision: 06.10; +1 severity step at 3–5 members, +2 at 6+; harm carries over; shaped effects hit k times. **[consumed: 03, 09]**
- Alternatives considered: individual mooks with 1 Vitality (still one turn each: the action problem remains); PF2e troops' thresholds (more state than a members count); a gang-up bonus to hit (accuracy stacking; the step uses the severity ladder already there).
- Evidence: [R: https://pelgranepress.com/2016/07/11/13th-age-mooks-destined-to-die/] [R: https://2e.aonprd.com/Rules.aspx?ID=3365] [R: https://cairnrpg.com/first-edition/cairn-srd/] [R1 #7] simulation: four T2 as individuals vs P2 3%, as a mob 43%.
- Serves: goal 1 (crowds are fightable), goal 2 (one stat line, one turn).
- Revisit if: T-06-MOB (OEQ-06-6).

### DL-06-21: Chases are racing clocks: escape 6 against pursuit 8 (start by band 2/1/0), one beat a side per chase round, varied approach
- Decision: 06.12. **[consumed: 07, 10]**
- Alternatives considered: 4 against 4 (simulated: 50% escape in 1.8 rounds: a coin flip with no room for ideas); 6 against 6 (47%); an opposed Move roll (one roll decides: the lethality lock argues against it); PF2e chase points per obstacle (party-scaled).
- Evidence: [R3 §06.10; https://bladesinthedark.com/progress-clocks] [R: https://2e.aonprd.com/Rules.aspx?ID=3049] [00.8.5] simulation I: 70% from near, 60% from close, 79% from far, 81% with a lever a round, 51% from riders, 3.4 rounds.
- Serves: goal 1 (escape is a real exit and a string of ideas), R6 C-R4.
- Revisit if: T-06-CHASE (OEQ-06-7).

### DL-06-22: Defend and Fend are engine snags on the attacker; the defense-reaction slot holds one answer
- Decision: Defend (1 action) and Fend (the basic reaction, rank 0 in `slot.defense_reaction`) each put −2 on attacks, inside the ±4 cap; abilities that claim the slot replace Fend. **[consumed: 05]**
- Alternatives considered: +2 to Guard as a status bonus (status's best bonus is the only one: it would not stack with `cond.heartened` and would not be capped with cover); no basic reaction (R3 §06.9: a solo PC needs self-defense in the always-available tier).
- Evidence: [00.3.9 g] [T-00-14 `slot.defense_reaction`] [R3 §06.9] simulation C: Fend is worth 1–17 points of win rate; Defend loses a duel slightly and wins against crowds.
- Serves: goal 1, goal 2.
- Revisit if: playtests show Fend is declared on every first attack without thought (then make it automatic and remove the prompt).

### DL-06-23: Harm mode on every attack frame; an adversary at 0 Vitality is defeated, and 07 decides its state
- Decision: lethal / nonlethal / restraint; nonlethal costs a snag only with edged, pointed or shot weapons.
- Alternatives considered: a separate subdual harm track (a second pool per creature); nonlethal as a free declaration after the fact (the outcome would be chosen after the roll).
- Evidence: [R4 §9 06 item 2 (harm modes)] [R5 CF-10] [BRIEF §4].
- Serves: goal 1 (taking prisoners is always possible), goal 2.
- Revisit if: 07 defines dispositions that need a fourth mode.

### DL-06-24: Four effect definitions added in the owner-block
- Decision: `eff.06.fewer_actions` (economy, non-positive `actions_delta`), `eff.06.pace` (modify speed), `eff.06.grant_snag` (lever, sign snag), `eff.06.internal_harm` (harm, no reduction).
- Alternatives considered: prose-only mechanics for dazed and stunned (a defect under 00.16.4); stretching `restrict` to "more than N actions" (not what the operation says).
- Evidence: [PR-00-8] [00.10.3] [INV-11].
- Serves: goal 2.
- Revisit if: 00 declines the `economy` clarification (then dazed and stunned become core `[T]` rules of this chapter referenced by id).

### DL-06-25: Reference lines and targets for the simulation
- Decision: T-06-12 (adversary lines at or near the top of 00.3.7's ranges for T1–T2, the middle for T3–T5; PC Vitality 12/14/16/18/20 and armor 1/1/2/2/3 assumed); targets as stated in 06.10.6; the advisory matrix T-06-13 as the contract with 09. **[consumed: 09, 07, 02]**
- Alternatives considered: tuning this chapter's economy until two same-band foes were "fair" at every band (would need 4 actions or halved adversary harm); asking 09 for softer T4/T5 lines (left to 09: the envelope and OEQ-00-7 want legends hard).
- Evidence: [00.3.7] [OEQ-00-2 T-00-PACE] [R2 #11: band and count budgeted separately] the simulation's sections A–H.
- Serves: goal 2 (encounter advice from data).
- Revisit if: 02/07 fix PC Vitality or armor differently (section F shows the sensitivity).

### DL-06-26: In a conflict a Strike is Safe by default; the reckless blow is 01's "go big" trade
- Decision: failure of a PC's attack costs nothing but the foe's own turn; trading to Risky and Great is the all-out attack; no separate rule.
- Alternatives considered: every miss costs (PbtA-style: with engine-run adversary turns the PC would be hit twice for one failure); a dedicated "wild attack" action (a second way to do what the trade already does).
- Evidence: [01.6.9 conflict clause] [01.7.3] [R: https://samhaine.wordpress.com/2020/04/06/savage-worlds-rules-summary/ (wild attack)] simulation C: the reckless first Strike gains 6–13 points against armored foes and loses 5 against a foe it does not need it for.
- Serves: goal 2 (one mechanism), goal 1.
- Revisit if: players never use the trade in fights.

## DL-07 — Harm, Recovery, and Death

Format per BRIEF §11. Citations per 00.1.6. Numbers consumed by other chapters are marked **[consumed]**.
Simulation: `rules/_process/simulation/07-harm-sim.py` (seeded `random.Random(707)`, 20,000 fights a row, on
chapter 06's fight model and T-06-12 lines), output `07-harm-sim-output.txt`, write-up `07-harm-sim.md`.

### DL-07-01: The Two-Key rule, stated so that death is only ever the player's own choice or the player's own gamble
- Decision: `harm_state.dead` is written for a PC only when Key 1 (a lethal frame: a lethal context recorded, shown and effective before the declaration) and Key 2 hold, where Key 2 is exactly: Last Stand chosen at the Threshold; the Gamble chosen at the Threshold and failed; a voluntary last stand confirmed; or a forfeited Bargain that returns the character to the Threshold. No check, clock, hazard or affliction kills. **[consumed: 01, 06, 09, 10, 11, 12, 14]**
- Alternatives considered: death when the dying ladder passes its top (Pathfinder 2e's dying 4, D&D's third failed death save): rejected, it is a death roll and the brief requires a last-chance choice; a Mörk Borg-style broken table with a death row: rejected (one roll kills a quarter of the time); "Key 2 = already Dying" with death on the next lethal hit and the menu only as an interrupt the DM may offer: rejected, because it leaves mercy with the DM, which is where the leniency failure lives (R4 §6).
- Evidence: [R6 §C.3 C-R1…C-R3] [BRIEF §4; BRIEF A2 #3] [R: https://sites.google.com/view/torchbearerwiki/faq (death only through closed doors)] [R: https://bladesinthedark.com/consequences-harm (fatal harm only if the player does not resist)] [R: https://www.dungeon-world.com/not-the-end-face-death/] [INV-6].
- Serves: goal 1 (bold play without fear of an arbitrary end), goal 2 (an auditable refusal of the write), the lethality lock.
- Revisit if: T-07-MENU (OEQ-07-4) shows players treat the menu as costless (one option chosen more than half the time with no lasting effect on play), which would mean death is not felt as real.

### DL-07-02: The lethal warning is an engine trigger with ten causes, shown in plain words, effective only after one player declaration; a Windup counts
- Decision: `trg.lethal_warning` is raised from tracked state by a closed list of causes (advisory, archetype, disposition, severity S4+, windup, clock at imminent, hazard, affliction warn stage, deprivation, chosen); delivery is one perceivable sign in fiction plus a fixed `[WARNING]` block naming the source, the exits and fate; the context is effective from the end of the player's next declaration or turn. A separate danger notice covers *hard* advisories and writes no context. **[consumed: 06, 09, 10, 12, 14]**
- Alternatives considered: the DM decides when to warn (`[J:flag]`): rejected, the research finding is that warnings are forgotten or softened unless raised by state (R4 §4.3, §6.2 item 4); warning only on *lethal* advisories: rejected, a wolf pack rated *fair* still kills, and "this can kill you" must be true whenever Dying is possible; effective at once: rejected, an ambush would then deliver warning and lethal blows in the same engine step, which is no warning; the Windup as the only warning: rejected as too late for anything but that blow, but accepted as a cause (06's question).
- Evidence: [R4 §6.2 item 4 (a warning state machine)] [R6 C-01 (soft move before hard move), C-02, C-04 (information, choice, impact)] [00.8.4] [06.9.5] [01.6.9].
- Serves: the lethality lock; goal 2 (the DM delivers, never decides); goal 1 (the exits are always stated).
- Revisit if: T-07-WARN (OEQ-07-2) shows the block is ignored through frequency, or T-07-OMIT shows delivery under 98%.

### DL-07-03: The blow that Staggers does only that; wounds exist only at 0 Vitality; a wound's severity is the bucket of the final amount
- Decision: harm beyond 0 Vitality is discarded (no negative Vitality, no overflow, no massive-damage rule). While Staggered or Dying each harm event is a wound whose severity is the bucket of the amount after reduction (1–2 / 3–4 / 5–7 / 8–11 / 12+ → S1…S5). Periodic events add wound load and create no record. **[consumed: 05, 06, 09, 10]**
- Alternatives considered: Cairn's overflow into an attribute with a save (fast, and can kill without a choice point); a wound on every hit at any Vitality (Blades' harm rows: makes Vitality redundant); severity from the attack's rung before armor (armor would then not protect against wounds); a "graze" class for small amounts (an extra rule for what the Light bucket already does).
- Evidence: [00.3.12] [06.9.5 ("cannot take a character from full Vitality to anything worse than Staggered")] [R6 C-08] [R: https://cairnrpg.com/second-edition/wardens-guide/combat/] [R4 §9 07 item 3 (wounds from a table, not from the narrator)]. Exact arithmetic: section A of the simulation.
- Serves: "a single unlucky roll never ends a character" as arithmetic; goal 2 (one rule, no exception for big hits).
- Revisit if: playtests show Staggered is reached and left so often that it stops reading as danger.

### DL-07-04: Ladder numbers: Dying has 3 steps, the wound load limit is 3, stabilize DCs are 10 / 15 / 20, the Dying character acts, and brink is a clocked Heavy wound
- Decision: `dying_step` 1…3 (inside 00's 2…4); load ≥ 3 fells; the dying check is Endure with Endurance against Easy / Moderate / Hard by step, with a hold on a failure by 3 or less; one action a turn while Dying; each stabilization leaves `inj.the_brink`, which raises the next fall's entry step and heals on a 4-segment clock. **[consumed: 01, 05, 06, 16]**
- Alternatives considered and what the simulation showed: load limit 2: fair fights reached the menu 9 in 100 fighting on (5 with an exit), hard 36 (17); limit 3: 5 (2) and 26 (11), which meets the targets. A flat DC 15: a first fall stabilizes 66% and a third 23%, against 85% and 11% for 10 / 15 / 20, so memory would matter less. An unconscious Dying state (5e, PF2e): rejected for a solo game, where it turns the brink into watching dice (Darkest Dungeon's Death's Door acts). Brink cleared by one night's rest: median recovery from Dying was 1 day in every regime; as a clocked wound it is 2 days with care and 4 without. Four steps (PF2e): one more round of checks with no new decision.
- Evidence: [R: https://2e.aonprd.com/Rules.aspx?ID=2319] [R6 C-07, C-10, C-R2] [R: https://darkestdungeon.wiki.gg/wiki/Stress] `07-harm-sim.md` sections B–G.
- Serves: the lethality lock ("a dying state"); goal 1 (agency at the door).
- Revisit if: T-07-LADDER (OEQ-07-1) on chapter 09's final templates moves the fair row above 6.

### DL-07-05: The last-chance menu has nine options, three always available, no default, and strikes only by cited fact
- Decision: Captured, Maimed, Death's Bargain, Left for Dead, Rout, Reprieve, Last Stand, Gamble, The Road Ends. Maimed (once a scene, while an attribute can be lowered), Last Stand, Gamble and The Road Ends are always available, so "at least three, one of them not death" holds in every state and is validated by the engine. The DM strikes only for a reason on the option's closed list. The Gamble is Endure against Moderate: 45% death at +2. **[consumed: 01, 11, 12, 14]**
- Alternatives considered: R6's eight without The Road Ends: a character with every attribute maimed, cornered among killers with no fate would have had no survival option; a default choice when the player does not answer (12.15.6 asks for one): rejected, no default is safe to impose, so the pause persists; DM-chosen outcome ("the DM picks what fits"): rejected (R4 §9 07 item 5: the AI should never be the one choosing mercy); the Gamble against Hard: 70% death at +2, a trap option; against Easy: 20%, dominant.
- Evidence: [R6 §C.3 C-R3] [R: https://www.dungeon-world.com/not-the-end-face-death/] [R6 C-13…C-17] [R4 §7.3 (locus of control)]; simulation section I.
- Serves: the lethality lock; goal 1; goal 2.
- Revisit if: T-07-MENU or T-07-GAMBLE (OEQ-07-4, -5) fall outside their bands; T-07-STRIKE finds illegal strikes surviving validation.

### DL-07-06: Death's Bargain is a curse, a vow thread and a weekly countdown; forfeit returns the character to the Threshold
- Decision: `aff.deaths_debt` (four stages, no checks) advances each time `clk.deaths_debt` (8, +1 a week) completes unpaid; the ask is the bargainer's recorded want or a table roll; forfeit rebuilds the menu without the Bargain under the context `chosen`.
- Alternatives considered: a one-time narrative promise with no clock (nothing enforces it: leniency); immediate death on refusal (a death without a new warning; here the bargain is the warning and the Threshold is revisited, not skipped).
- Evidence: [R6 C-14 (Ironsworn's Face Death: a vow, cursed until done)] [00.8] [01.16.2 (a vow kept earns fate)].
- Serves: goal 1 (defeat that generates a quest), the living world (11).
- Revisit if: bargains are taken at nearly every Threshold where offered (then raise its price: a shorter clock).

### DL-07-07: A reprieve costs 1, then 2, then 3 fate, and leaves no brink wound
- Decision: `fate_cost = min(3, 1 + reprieves_taken)`. **[consumed: 01, 14]**
- Alternatives considered: a flat 1 (with hard luck refilling fate to 2, the reprieve would be available at most Thresholds); all remaining fate (PF2e's hero points: punishes having saved more); a separate reprieve pool (a second meta-currency, forbidden by 00.17.1 Q9).
- Evidence: [01.16.1–01.16.4] [R6 C-17 (finite, visible, earned by deeds)] [R: https://2e.aonprd.com/Rules.aspx?ID=2319 (no wounded increase)].
- Serves: the lethality lock (a visible, shrinking margin).
- Revisit if: reprieves are more than a third of menu choices over twenty sessions.

### DL-07-08: Yielding buys terms, not fate
- Decision: an accepted Yield gives no further harm, consciousness, knowledge of the route, and one term from a closed list by disposition; acceptance is a lookup on `defeat_disposition`. No resource is earned.
- Alternatives considered: +1 fate for yielding in a lethal context (R6 C-R4's "small resource gain", from Fate's concession): rejected, 01's earning list is closed and a reward for surrender is farmable; a roll to be accepted: rejected, acceptance is the victor's nature (06.11.7), stated before commitment.
- Evidence: [R6 C-15, C-R4] [06.11.7] [01.16.2].
- Serves: goal 1 (surrender is a real move with a visible price), goal 2.
- Revisit if: T-07-EXIT (OEQ-07-3) shows Yield is almost never chosen where accepted.

### DL-07-09: Retreat is clean, a chase, or a rout; a rout always works and costs the world 2 ticks (3 from the Threshold)
- Decision: the pursuit test (willing and able) decides whether Retreat is certain; when it is contested the player chooses 06's chase (no stated price) or a rout (certain; U(S3) ticks on the clock the fight was about, U(S4) at the Threshold). **[consumed: 06, 11, 12]**
- Alternatives considered: Retreat always a chase (no certain exit before the brink: contradicts R6 C-R4 and 13th Age's finding that a priced flight is what keeps defeats from becoming deaths); Retreat always certain and free of world cost (a free escape from every fight).
- Evidence: [R: https://www.13thagesrd.com/combat-rules/ (flee and take a campaign loss)] [R6 C-16] [06.12 (70% from near, 60% from close)] [12.7.5 (a retreat at S3 or heavier is a setback)].
- Serves: goal 1; the living world (the cost is a clock tick the player can see or sense).
- Revisit if: routs are the response to most hard fights (then the world cost is too cheap: raise to S4 / S5).

### DL-07-10: Wounds are data keyed by harm family × site × severity; penalties are status (worst only), never on Guard; maims are drawn by table
- Decision: 170 wound entries (ten families, four sites, S2–S5, plus ten Light), four site carriers with penalties −1 / −2 / −2 / −3 and three rungs of restriction; Heavy and worse lower maximum Vitality by 2 / 3 / 4; maims lower the first eligible attribute in a fixed order. **[consumed: 08, 15, 16]**
- Alternatives considered: free-text wounds named by the narrator (the positivity bias softens them, R4 W3); a single generic "wounded" condition (no site, nothing for the fiction to hold); penalties on Guard (a death spiral under exactly the conditions where the PC is being hit); a d100 critical table per weapon (Warhammer: more texture than the engine needs, and random death rows).
- Evidence: [R4 §9 07 item 3] [R: https://bladesinthedark.com/consequences-harm (harm rows as named conditions)] [00.3.5 status worst-only] [00.4.3 c] [R6 C-09 take].
- Serves: goal 2 (state the narrator must match), goal 1 (wounds are specific things to work around).
- Revisit if: T-00-ATTR-style agreement tests show the site restrictions are misapplied more than 10% of the time (then cut to two rungs).

### DL-07-11: Three rest sites (haven, camp, rough) and a first-match quality rule; quality travels in the boundary payload
- Decision: 07.8.2–07.8.4. **[consumed: 05, 10, 15]**
- Alternatives considered: quality by DM judgment (`[J:rung]` each rest: three rungs chosen 38–58% exactly); a single rest type (5e's short and long rest confusion, R4 §9 07 item 4, is avoided by fixed durations and a payload); computing quality inside a handler (order-dependent with 05's handlers).
- Evidence: [00.7.2; 00.17.1 Q1, Q16] [R5 HR-05] [05.6.9].
- Serves: goal 2.
- Revisit if: 10's site and weather data make more caps computable (then the `[J:rung]` shrinks further).

### DL-07-12: Vitality returns in the same three sizes as Focus
- Decision: breather +2 (first two between short rests), short rest half (first two a day), long rest to maximum; partial and interrupted columns as T-07-14. **[consumed: 05, 10, 12]**
- Alternatives considered: slow natural healing of Vitality (1 a day: makes Vitality a wound track and every fight a multi-day cost, against 00.3.12's meaning); hit-dice-like pools (a second resource to track for the same decision); full Vitality after any fight (Cairn: removes attrition within a venture entirely).
- Evidence: [05.6.9; DL-05-14] [R6 C-08] [R1 §07 (rest must cost time)] [R: https://cairnrpg.com/second-edition/wardens-guide/combat/].
- Serves: goal 2 (one table shape to remember), goal 1 (a clear when-to-stop decision).
- Revisit if: T-07-DAY (OEQ-07-7) shows the fourth fair fight of a day entered above 80% Vitality without a healer.

### DL-07-13: Recovery clocks 4 / 6 / 12 with three daily ticks; Treat's DC by wound tier; treatment is outside the healing cap
- Decision: T-07-15; Treat at Easy / Moderate / Hard / Very hard (surgery, expert grade); one Treat a patient a day; Treat restores no Vitality; "one recovery step" = 7 ticks. **[consumed: 05, 15, 16]**
- Alternatives considered: wounds healed by magic like Vitality (05.7.8 forbids it and the cap would be meaningless); a single recovery clock for the whole character (Blades: simple, but one Grievous wound and one Light then heal at the same rate); treatment as automatic with the license (no decision, no risk at surgery).
- Evidence: [R: https://bladesinthedark.com/consequences-harm] [R5 HR-05, HR-09] [05.7.8; DL-05-23] [05 `lic.training.lore_medicine` grade caps]; simulation section G (median 2 / 2 / 4 days).
- Serves: goal 1 (pushing on wounded or paying time is a choice), goal 2.
- Revisit if: T-07-HEAL (OEQ-07-8) shows a median above 3 days wounded per venture.

### DL-07-14: Reduction cap 4; a closed no-reduction list; hazard severity by five anchored rungs; falls as 06 gave them; breath 6 + 2 × Endurance rounds
- Decision: 07.2.2, 07.10. **[consumed: 06, 08, 09, 10]**
- Alternatives considered: a cap of 3 (heavy armor alone would reach it, leaving nothing for items); minimum 1 harm on any hit (armor would never make rabble harmless, which is its job); armor against falls (plate does not help a fall).
- Evidence: [00.10.6] [T-06-11] [R1 §07 (caps on defense)] [06.5.8] [01.6.9 (20 ft is Heavy)].
- Serves: goal 2.
- Revisit if: 09's templates leave whole bands unable to harm a P4–P5 character (then mobs' numbers step is the lever, not the cap).

### DL-07-15: Mental strain is named dread; threshold 8 + Resolve; a break is tested; three haunts; the fourth break ends the career
- Decision: 07.11. Dread is distinct from 03's conduct *strain* and from `harm.mind.strain` Vitality harm. **[consumed: 02, 09, 11, 14]**
- Alternatives considered: the name "strain" (taken twice already); sanity as a second Vitality (Call of Cthulhu: ends lives and removes control); stress that forces actions (Darkest Dungeon's afflictions disobey: unacceptable for a single player's only character); threshold 6 + 2 × Resolve (a 2–14 spread makes Resolve a second god-stat for horror campaigns).
- Evidence: [00.4.4] [R6 C-R7, C-12] [R5 HR-06] [R: https://darkestdungeon.wiki.gg/wiki/Stress] [R: https://cubicle7games.com/en_US/blog/the-one-ring-the-shadow] [R: https://bladesinthedark.com/consequences-harm (the fourth trauma retires)].
- Serves: the lethality lock's "defeat changes the situation"; goal 1 (the player never loses the character's hands).
- Revisit if: T-07-DREAD (OEQ-07-9) shows first haunts before session 15 for an average character.

### DL-07-16: Seven contributed effects
- Decision: `eff.07.vitality_max_penalty`, `eff.07.dread`, `eff.07.maim`, `eff.07.stabilize`, `eff.07.affliction_shift`, `eff.07.rest_cap`, `eff.07.block_restore`, each on one of the twenty closed operations, each with a `why_not_core` line. Everything else uses the core library and 06's four.
- Alternatives considered: negative amounts on `eff.max_modify` (its range is 1..4; a core change); ending Dying with `eff.cleanse` (harm states are not conditions, 00.9.4); a new quantity `dread` in T-00-13 (an amendment to 00; a `resource` effect suffices).
- Evidence: [00.10.1; PR-00-8] [00.4.3 c].
- Serves: principle V (closed operations).
- Revisit if: 00 amends the core library to cover any of them.

### DL-07-17: Afflictions: one stage table, a hold on a failure by 3 or less, `warn_stage` on anything lethal, `max_checks` for what the body burns off
- Decision: 07.9; 18 entries (8 poisons, 6 diseases, 4 curses), 8 of them lethal. Stage checks ignore the affliction's own carrier and wound penalties.
- Alternatives considered: PF2e's table without the hold (a coin-flip each period; the hold is this ruleset's near miss); poisons as flat harm (no clock for treatment to race); stage checks taking the carrier's own penalty (a spiral: each stage makes the next check worse).
- Evidence: [R5 HR-08, G-8] [R: https://2e.aonprd.com/Rules.aspx?ID=2319] [00.9.4 (`cond.poisoned` as carrier)] [01.18.3].
- Serves: goal 2 (one procedure for every poison, sickness and curse), goal 1 (an anchor for anything that worsens on a schedule).
- Revisit if: lethal poisons reach Dying in under four checks from their warning in play.

### DL-07-18: Applying DL-00-04: maximum Vitality = base + 2 × (band − 1), with a floor of half under wound penalties
- Decision: 07.1.2; `h.07.vitality_max`; current rises with a band rise. The floor is this chapter's addition. **[consumed: 02, 04, 06, 09]**
- Alternatives considered: no floor (three Heavy wounds and a brink at P1 would leave a maximum of 4, which makes the recovery days unplayable rather than tense).
- Evidence: [DL-00-04] [06-conflict-sim.md section F] [R3 §07.8 (Vitality growth without levels)].
- Serves: goal 2; the top bands' fights.
- Revisit if: 02's base formula moves outside 10–16.

### DL-07-19: Defeat is a table keyed to the victor; captivity is a place, a clock and three openings; taken gear goes to a cache that disperses and is never deleted
- Decision: 07.6; T-07-11; `tbl.captivity_openings`; `clk.captors_intent` (6, a day) racing `clk.out_of_their_hands` (6); `clk.cache` (6, a week). A `kill` victor without Key 1 leaves the PC for dead.
- Alternatives considered: DM-narrated aftermath (defeat quietly becomes escape: R4 §6.2 item 5); gear lost for good (R1 §07: fails emotionally); capture as a scripted scene (takes agency with no way back, R1 §07).
- Evidence: [R6 C-19, C-20, C-R5] [R1 §07] [C:P16] [R4 §6.2 item 5].
- Serves: the lethality lock (defeat usually means capture, a wound, loss, or a changed situation); goal 1.
- Revisit if: T-07-CAPTIVE (OEQ-07-10) fails.

### DL-07-20: Companions bleed out on a 4-segment public countdown, with no menu
- Decision: 07.12. Key 1 protects companions exactly as it protects the PC; their second key is the clock. **[consumed: 06, 16]**
- Alternatives considered: the PC's full ladder for each companion (too much state for a commanded ally); instant death at 0 (no rescue objective); a menu for companions (00.17.1 Q8 forbids it).
- Evidence: [00.17.1 Q8] [R6 C-11 (a rescue clock makes a death an objective)].
- Serves: goal 1 (a clear, urgent thing to do), goal 2.
- Revisit if: companions are saved nearly always (then 3 segments) or nearly never (then 6).

### DL-07-21: Sleep and want are counters with fixed thresholds
- Decision: `watches_awake` 4 / 6 / 8 add stacks of `cond.exhausted`; beyond 8, S2 harm a watch and Down; want adds a stack a day (10) and becomes lethal only after the `deprivation` warning. The player may push on with an Endure beat.
- Alternatives considered: an Endure check every watch (many rolls for a slow process); exhaustion as its own six-rung ladder (5e): `cond.exhausted` with three stacks already exists and is shared with overdraw.
- Evidence: [R5 HR-07] [01.18.15] [06 T-06-10] [05.6.6].
- Serves: goal 2 (counters, not recollection: SG-19).
- Revisit if: 10's travel procedure wants a finer grain than the watch.

## DL-08 — Items, Loot, and Crafting

### DL-08-01: What a dropped item grants — four property kinds, one active at most
- Decision: Every item property is one of four kinds — mundane (works equipped), passive (equipped and attuned), license (attuned; no competence; no evidence), item_ability (one active ability through an equipped slot). License and item-ability properties may sit only in the signature slot, so an item holds at most one of them.
- Alternatives considered: items granting abilities freely in any slot (GW2's five abilities per weapon) — rejected: it breaks 00.17.1 Q2's "at most one item-bound active" and turns gear into a second ability menu (C:V); items granting only numbers — rejected: loses goal 1's "carry the brand and try the fire trick" (R2 #9).
- Evidence: [C:P5 deferred question]; [00.11.5]; [R3 08.10 (GW2, D3, D4 patterns)]; [R2 #9].
- Serves: goal 1, goal 2; C:V; C:P5.
- Revisit if: playtests show players ignoring relics entirely (then lower bound power's min tier to 2) or carrying four relic actives by P3 (then raise it to 4).

### DL-08-02: A six-rung quality ladder with fixed slot counts
- Decision: worn 0/0, common 0/0, fine 0/1, masterwork 1/1, wondrous 1/2, storied (authored) 1/2; index 1–6 for 03's cnt.made; price multipliers ×½, ×1, ×3, ×10, ×30.
- Alternatives considered: variable property counts per rarity (PoE1's 2–6) — rejected for legibility (PoE2 moved to exactly four); a separate "magic level" axis beside make quality — rejected: two ladders where one serves both mundane make and identity (fine = an open magnitude slot).
- Evidence: [R3 08.9, A-21]; [R3 08.2 identity vs magnitude]; [R2 08 "rarity specializes"].
- Serves: goal 2; C:V (bound the count).
- Revisit if: OEQ-08-3 shows masterwork drops feel interchangeable (then a rung between masterwork and wondrous with 1/1 + a higher tier).

### DL-08-03: Ch.02's worn/common/fine map to rungs 1–3; a kit's fine item has an OPEN slot
- Decision: 02's names are this ladder's first three rungs; 02.8.2's "no property from any generator pool" is honored because fine's magnitude slot arrives empty and may later receive a worked property or a crafter's addition.
- Alternatives considered: rename fine to "good" — rejected (02 is written); give kit fine items a fixed mundane property — rejected (contradicts 02.8.2).
- Evidence: [02 Interface request]; [08.6.10].
- Serves: goal 2 (no contradiction across chapters).
- Revisit if: 02 changes kit limits.

### DL-08-04: Weapons are 06's table exactly; 08 owns the roster, not the weights
- Decision: 33 weapon and ammunition base items built on T-06-6/T-06-7 with at most two properties each, deed tags and training licenses named; generated from the same script so a retune of 06 regenerates 08's data with no rule change.
- Alternatives considered: 08-owned weapon stats — rejected by 00.17.2 ("weapon harm base severities (with 08)") and 06's request.
- Evidence: [06.4.4–06.4.5]; [06 Interface request to 08].
- Serves: goal 2.
- Revisit if: 06 changes T-06-6/7.

### DL-08-05: cost_immune = attuned relics and storied items; immunity to attrition, not theft
- Decision: cost.gear cannot target an attuned relic or storied item; abilities cannot sunder it; it cannot be disarmed; capture and robbery still take it to a cache.
- Alternatives considered: all property items immune — rejected: removes 01's gear cost from most mid-game play; nothing immune — rejected: a bound relic lost to one near miss is the "losing gear hurts more than the numbers" failure (R1 07).
- Evidence: [01.13.4]; [06.5.4]; [07.6.4]; [R1 07].
- Serves: goal 1 (attachment is safe from dice), goal 2.
- Revisit if: players stop fearing gear costs entirely (count cost.gear selections in playtests).

### DL-08-06: Improvised weapons use the resembled weapon's numbers without its properties or mastery
- Decision: a [J:enum] resemblance choice → the weapon's weight row, no T-06-7 properties, an "improvised" snag unless trained in the resembled weapon; none → 06's size rungs.
- Alternatives considered: free-form DM severity — rejected (SG-01).
- Evidence: [01 Interface request]; [06.5.8]; [R7 §4.4].
- Serves: goal 1 (anything is a weapon), goal 2.
- Revisit if: T-00-ATTR-style agreement tests show resemblance disagreement above 15%.

### DL-08-07: The item share — items never fill a capped family
- Decision: item-sourced contributions are clamped at E4 to +1 edge (per quantity and scope), +1 harm edge, reduction 3 per harm tag, one ×½ only from a tier-4+ signature, ±1 steps, one item lever per roll, carry +4, supply −1/day, Focus cost −1 once per scene from an implement signature; items never touch attributes, competence, maxima, actions, reactions, slots or tiers.
- Alternatives considered: let items fill caps (PoE's jewel meta crowding out the tree) — rejected; points-budget per item (D&D's item value) — rejected as unenforceable across stacking; no cap beyond families — rejected (items would crowd out callings, the D3 launch failure).
- Evidence: [R3 00.13, #11, PG5]; [R1 08 Mythcreants gear balance]; [00.3.5]; T-08-16 (clamp binds for ~1 character in 5).
- Serves: goal 2; C:P2 (growth is calling-driven); C:P11 (audited budget).
- Revisit if: OEQ-08-3's kept-for-effect share falls below 30%.

### DL-08-08: A drop check by source band, never by the PC
- Decision: trophy yield drops a property item on d100 ≤ 10/20/35/50/70 by T1–T5; hoard and always yields always drop; every defeat still yields harvest, purse and gear.
- Alternatives considered: always drop (D3-style fountains) — rejected: 50–110 property items by P4; drop chance by PC-vs-foe gap — rejected: reads the recipient (00.11.4); fixed one-in-N per session — rejected: not P5's source-driven shape.
- Evidence: [R3 A-1 (Diablo II NoDrop)]; [R2 08 HWFWM over-generation retired]; T-08-16.
- Serves: goal 2; C:VI (a reward rate with a named revisit trigger).
- Revisit if: OEQ-08-2.

### DL-08-09: Loot circumstances decisive / costly / merciful / scavenged; mercy pays as well as killing
- Decision: 00's reference set adopted; costly is gen_absorb's narrow_survival (one classification); decisive, costly and merciful all give masterwork; merciful's fill is chosen.
- Alternatives considered: merciful as a lower rung — rejected: conduct axes must not pay cruelty in loot; separate costly definition — rejected: two near-identical judgments for one event.
- Evidence: [C:P5]; [R: src/ability_pool.py]; [04.10]; [03 conduct.mercy].
- Serves: goal 1 (mercy is a real choice), goal 2 (one call, two domains).
- Revisit if: players spare foes only for loot (a conduct-gaming pattern visible in the evidence ledger).

### DL-08-10: Base selection honors the signature; one redraw for thin pools
- Decision: with a signature fill the base is drawn among bases the signature accepts, else the signature's first base kind supplies one; a base whose pool is smaller than the slots is redrawn once.
- Alternatives considered: draw the base blind — rejected: the sim showed 43 of 438 decisive drops lost their signature (a wyvern's weapon-only sting on a shield).
- Evidence: 08-loot-sim.py runs (49 overrides, 0 redraws after the fix).
- Serves: goal 2 (decisive always means identity).
- Revisit if: 09's trophy lists make overrides exceed 10% of decisive drops.

### DL-08-11: Relics license off-identity capability at a premium, with no growth
- Decision: relic = bound power or license property; license properties grant languages at broken, peoples' senses, or training licenses at trained with NO competence; feeds_evidence false; +1 Focus surcharge on abilities without the training license (05.6.3); fixed rank; cost_immune while attuned; a spare if already held.
- Alternatives considered: relics granting competence — rejected by 00.3.6; relics feeding tiers — rejected by 00.11.5 and 04's request.
- Evidence: [R2 #9 Honorblades]; [C:P12 three levers]; [04.11.3].
- Serves: goal 1, VII.
- Revisit if: OEQ-08-6.

### DL-08-12: Harvest is a Handle beat; essences need a dissection license; parts carry provenance
- Decision: hides, bones, fangs are G1 Handle; glands, hearts, blood, ichor, residue need foraging, bestiary or alchemy training or the crude fallback; reach sets how many parts; parts keep their source archetype and band and carry its signature into crafts.
- Alternatives considered: automatic materials on every kill — rejected: no player choice, no time cost; generic materials without provenance — rejected: loses Monster Hunter's identity loop.
- Evidence: [04.10.1]; [R: https://en.wikipedia.org/wiki/Monster_Hunter_Wilds]; [R2 #13].
- Serves: goal 1 (any body is a resource), goal 2.
- Revisit if: harvest beats become routine filler (count harvests skipped in playtests).

### DL-08-13: The pool gate widens by place for place-gated entries only
- Decision: terrain tags of the place open entries flagged place_gated (snowshod, marsh-strider, warm, tomb-ward…) whatever the source; nothing else reads place.
- Alternatives considered: place as a third fill axis — rejected by 00.11.4 and P5's two-axis shape; place-only sites — kept for hoards (source = the place).
- Evidence: [R2 #13 "gate by nature and place"; HWFWM stones].
- Serves: goal 1 (where you hunt matters), C:P5.
- Revisit if: place-gated entries exceed 20% of drops in any region (13's tables).

### DL-08-14: Attunement: five items, at a breather, unsealing on attune
- Decision: five attuned items; mundane properties need none; attuning unseals; ends if the item is not possessed at a long rest's end.
- Alternatives considered: 3 (5e) — rejected: binds before the item share does, so the share never matters; 10 (PF2 investment) — rejected: too many independent triggers per turn.
- Evidence: [R2 08 Iron Man Principle]; T-08-16 (5 items → ~1 in 5 clamp).
- Serves: goal 2.
- Revisit if: OEQ-08-3.

### DL-08-15: Craft circumstances crafted / commissioned / improvised with chosen / biased / weighted fills
- Decision: own licensed work chooses (PoE bench); a commission names one bias tag (RoR2 category chest); improvised work is weighted and capped at common; recipes override one slot.
- Alternatives considered: commission chooses exactly — rejected: makes self-crafting pointless; crafting signature by choice — rejected: provenance is the identity.
- Evidence: [R3 08.3, 08.15, A-18, A-26].
- Serves: goal 1 (control through skill), C:P5.
- Revisit if: commissioned items dominate PC gear by P3.

### DL-08-16: Crafting as two racing clocks; quality is declared ambition
- Decision: progress 4/6/8/12 by target vs spoilage 4 (6 for wondrous); DC by target (Easy/Moderate/Hard/Very hard); Greater on a critical completing beat; Flawed at spoilage ≥ last-but-one segment.
- Alternatives considered: one roll decides quality — rejected: P5 type-tier × quality-tier needs a declared ambition, and single rolls are swingy; Flawed on any critical failure — rejected after simulation (40% flawed masterworks at +7).
- Evidence: [R4 §9 08 #5]; [05.8.2 rites]; 08-craft-sim.py (T-08-14).
- Serves: goal 2; C:P15 (time as the scarce resource).
- Revisit if: OEQ-08-5.

### DL-08-17: Salvage returns identity as residuum and teaches recipes
- Decision: salvage destroys an item for stock, a residuum gating its signature, and on reach 3+ a recipe (D4's Codex).
- Alternatives considered: sell-only disposal — rejected: coin flood (AI rules); no recipe learning — rejected: crafting would lack a progression of its own.
- Evidence: [R3 08.10, A-10].
- Serves: goal 1; anti-inflation.
- Revisit if: recipe counts per crafter exceed 15 by P3 (consolidate as a VI boundary).

### DL-08-18: Gifts: earned / favored / bargained; the giver's boon signature always eligible; abilities only from powers
- Decision: earned masterwork chosen; favored masterwork with the giver's signature placed; bargained wondrous chosen; only powers give abilities (acquired partition, provisional); institutions give items, ranks and training.
- Alternatives considered: favored as fine — rejected: its signature fill would have no slot; institutions giving abilities — rejected by 04.11.3.
- Evidence: [00.11.1]; [04.11.3]; [05.8.7]; [R6 V13].
- Serves: goal 1, goal 2.
- Revisit if: bargained gifts become the dominant source of wondrous items.

### DL-08-19: One coin, lots instead of sub-units, notches instead of percentages, eight anti-inflation rules
- Decision: coin = a day's plain food and lodging (02 confirmed); sub-coin goods sold by the lot; price bands ×5 with fixed notches (1/1/2/10/50/250/1000) for haggling, gluts and fees; conjured worthless, labor cap, half-list property sales via a find-buyer clock, market depth, glut, table-only coin entry, item-share caps on economic properties, labor-and-rent holdings.
- Alternatives considered: a silver/copper sub-currency — rejected: a second quantity and fractional pricing; percentage haggling — rejected by SG-23.
- Evidence: [R2 08 Fabricate]; [R1 08 gold hallucination]; [R5 EQ-03, EQ-04, EQ-13].
- Serves: goal 2.
- Revisit if: OEQ-08-4.

### DL-08-20: Lifestyles weekly 0/4/7/14/35/100; the Unit of wealth = the weekly lifestyle cost
- Decision: lifestyle charged by h.08.upkeep for any week touching a settlement; shortfall drops a rung; a Unit scales coin costs by severity and sets 03's generosity floor.
- Alternatives considered: a fixed coin floor for generosity — rejected: a copper means nothing to the rich and everything to the destitute.
- Evidence: [R: https://bladesinthedark.com/coin-stash]; [R5 EQ-05]; [03 Interface request].
- Serves: goal 2; conduct fairness.
- Revisit if: lifestyle is never changed by players in playtests (then fold lifestyle into an automatic tier).

### DL-08-21: Three new effects (eff.08.adjust, eff.08.cost_step, eff.08.bound_ability)
- Decision: add only what no core effect expresses: adjust-family quantities (carry, supply use), a step on a cost's severity against an item, and an item-bound ability grant with rank and evidence flag.
- Alternatives considered: overload eff.max_modify or eff.grant_license — rejected: wrong quantity/semantics (PR-00-8 "expand before you add" respected for every other property: 210 properties use core and 05/06/07 effects).
- Evidence: [00.10.1]; [PR-00-8].
- Serves: goal 2.
- Revisit if: 00 adds equivalent core effects.

### DL-08-22: Load units and capacity 10 + 2 × Might
- Decision: Might feeds carrying capacity (00.4.4's one derived value); 8–18 units; burdened above capacity (snags, slower), overloaded above twice.
- Alternatives considered: weight in pounds — rejected (arithmetic burden, no legibility gain); Mausritter's fixed 10 slots — rejected: 00.4.4 assigns capacity to Might.
- Evidence: [R5 EQ-02]; [R: https://en.wikipedia.org/wiki/Mausritter]; [00.4.4].
- Serves: goal 2.
- Revisit if: load is ignored in play (no burdened state reached in three playtests) — then halve capacity's base.

### DL-08-23: gen.item_ability reuses 04's natural powers and 05's techniques
- Decision: no new ability content; 159 pool entries: active gen_absorb entries (creature-gated) and active calling abilities without conduct requirements (deed-gated), with a source_to_deed map for non-deed sources.
- Alternatives considered: an authored item-ability list — rejected: an ever-growing menu (C:V) and duplicate mechanics.
- Evidence: [C:V]; [R3 #1]; [04.10]; [05.2.8].
- Serves: goal 2; C:V.
- Revisit if: 05 retires abilities (the pool follows the lifecycle field).

### DL-08-24: The bound power appears only at tier 3+; a decisive win never falls back to a relic
- Decision: bound power min tier 3; signature-fill fallbacks exclude relics; result 14.0% of drops carry a bound power, 15.5% any relic.
- Alternatives considered: min tier 2 and no exclusion — simulated 23% relics (more than one masterwork in three), which makes borrowed power ordinary.
- Evidence: 08-loot-sim.py iterations (T-08-16).
- Serves: goal 1 (relics feel special), C:VII.
- Revisit if: OEQ-08-6 or playtest relic counts.

### DL-08-25: Property values 20/50/125/300/750 by tier; bound powers ×2
- Decision: list price adds these per property; sale through the find-buyer rule at half.
- Alternatives considered: pricing by effect type — rejected: unauditable for 210 entries.
- Evidence: [R5 EQ-13]; economy derivation 08.8.10.
- Serves: goal 2.
- Revisit if: OEQ-08-4.

### DL-08-26: Sealed properties: signature apparent, the rest sealed until attunement, a firing, a sage or a study
- Decision: identification by four paths, study using P17's graduated delivery and a once-per-long-rest lock.
- Alternatives considered: fully known drops — rejected: removes the reason to study and the risk of flaws; fully sealed — rejected: the signature is the item's identity, visible by nature.
- Evidence: [00.6.5]; [C:P17]; [R4 §5].
- Serves: goal 1 (curiosity pays), goal 2 (sealed state never leaks).
- Revisit if: players attune blind every time (then identification is irrelevant and can be simplified).

### DL-08-27: One worked property per item, ever
- Decision: enchanting adds exactly one property into an open magnitude slot, by recipe or chosen, at min(reagent band, grade cap); never a license or bound power.
- Alternatives considered: unlimited enchanting — rejected: PoE2 restricted crafted mods to one for exactly this reason; enchanting identity — rejected: identity is made, not added.
- Evidence: [R3 A-23 (PoE2 Alloy)]; [05 rit.imbue].
- Serves: goal 2; C:V.
- Revisit if: enchanters have nothing to do after their own kit is enchanted (then allow re-enchanting by replacing the worked property).

### DL-08-28: Signature properties share mod groups with their families
- Decision: an elemental strike signature shares strike_form, an on-hit signature on_hit, a resistance signature its resistance group — so no item carries two of a kind.
- Alternatives considered: unique groups per signature — rejected after simulation showed sting + venom-touched double procs on one whip.
- Evidence: 08.2.3; 08-loot-sim.py.
- Serves: goal 2 (one-line items).
- Revisit if: OEQ-08-1 repeat rates rise above 20% on the affected natures.

### DL-08-29: Made by hands: armaments from folk and undead open folk-made properties
- Decision: weapons, armor and shields taken from folk or undead add creature.folk to the source tags.
- Alternatives considered: none (skeleton pools at tier 1 were 2 entries).
- Evidence: 08-loot-sim.py contract check.
- Serves: goal 2 (no empty pools).
- Revisit if: 09 tags undead armaments differently.

### DL-08-30: A crafting project is a craft contest (revision I-003)
- Decision: 08.6.4 item 6: a step's challenge band is at least the work's type-tier; a step on a work with an irreplaceable material is Dire and its `cost.gear` on that material is ruinous; a step with spoilage one from full is at the brink; fine-or-better works may be played as scenes, and a masterwork's or wondrous work's completing beat always is.
- Alternatives considered: let crafting steps stay Risky and DC-banded (rejected: no work then rose above band 4 and no step was ever a crisis, so a smith's calling stopped at tier 2 in every simulated run); judged evidence from every downtime step (rejected: it would turn the week planner into a grind, against 15.10.6).
- Evidence: `04-recog-parity.py`: smith tier 3 never (earlier rules) → 18; tier 5 never → 45 (archer 19 / 51).
- Serves: goal 1.
- Revisit if: crafting-heavy play logs show smiths playing fewer than a third of their works as scenes (the judged path would then be too rare in practice).

### DL-08-31: The loot variety test runs on the real bestiary, and pools are widened until every case passes
- Decision: [revision: I-017, I-019] `08-loot-sim.py` checks every archetype of `archetypes.yaml` that yields loot, at each of its bands, with its own `trophy_base`; 58 properties gain 114 thematic gate tags (`08-gen_data08.py#EXTRA_GATES`), and `prop.tidesense` (Tide-sense: a Precision lever on Observe and Move in, on or under water) is the water-gated tier-1 entry I-019 asked for.
- Alternatives considered: stronger recency (×¼ instead of ×½, 00.11.3 step 7: rejected, it would change every generator domain to fix one); broader trophy base lists in 09's data (rejected as the main lever: 09 owns `trophy_base`, and a decisive drop's signature fixes the base kind anyway).
- Evidence: 186 cases, mean repeat 8.0%, worst 14.6% (was 75 cases above 15%, worst 100%); 09 contract 186/186 (was 171/186); reference set worst 14.6% (clockwork sentinel 5.5%, slime 11.6%); drop rates, rungs and item-share compliance unchanged (T-08-16).
- Serves: goal 3 (variety: loot that keeps surprising); OEQ-00-5.
- Revisit if: 09 adds an archetype (the sim fails it until its pools pass).

### DL-08-32: Prostheses are base items
- Decision: [revision: I-016] Six `base_items.yaml` entries tagged `item.tool.kit.prosthesis` (hook, arm brace, peg or fitted boot, hinged knee brace, glass eye, ear trumpet), price band 2, crafted under the matching trade, body slot `fitted`, `trophy_eligible: false`, each with `offsets {maim, narrows, never}` naming its 07 maim and exactly what it narrows (a hook allows a strapped shield; a brace halves a status penalty; a glass eye hides the loss and changes no number). 07.7.6, 07's maim `offset` texts and 08.5.1 point to them.
- Alternatives considered: one generic "made replacement" entry (rejected: 07.7.6 names the things, and each narrows a different restriction).
- Evidence: the generators' validation passes; the loot sim's drops are unchanged (prostheses are never trophies).
- Serves: goal 2 (no rule names an item the data lacks); the brief's maim-as-story stance (07).
- Revisit if: a playtest asks for a prosthesis of a wondrous rung (a relic hand): that is a crafting project on these bases.

### DL-08-33: Fewer drops and leaner hoards, so magic items are not routine at P3–P5
- Decision: [revision: I-018] The drop check becomes T1 10 · T2 15 · T3 30 · T4 40 · T5 55 (was 10/20/35/50/70); hoards lose one item at T3–T5 (T3 one masterwork, T4 one wondrous, T5 one wondrous and one masterwork); a hoard is generated where it is kept, so a hoard-keeper defeated away from its lair or vault rolls as a trophy and its hoard waits there (08.3.3, 08.3.12, PR-08-1 step 3, `gen_loot.yaml`). The masterwork rate is unchanged.
- Alternatives considered: lowering the masterwork rate (costly wins giving fine items: rejected, it changed the share of masterworks from 74% to 52% but not the count of items, which was the problem); counting hoards into 08.2.7's table instead (rejected: the table is the design target that 09's tuning and 12's pacing read).
- Evidence: `08-campaign-sim.py`, 300 campaigns × 70 sessions (T-08-17): property items won per band P1 4 / P2 6 / P3 13 / P4 24 against 08.2.7's 2–4 / 4–6 / 8–12 / 15–25 (before: P3 22, P4 45.5 in a 60-campaign run); bound abilities attuned and top signature tiers within 08.2.7's columns; coin one tier ahead at P3–P4 with lifestyle the only sink. `08-loot-sim.py` re-run: rates 7.3/16.0/32.5/38.8/55.3%, compliance 1,000/1,000.
- Serves: goal 3 (loot that matters because it is not routine); the brief's item-density assumption (08.2.7) that 09 and 12 rely on.
- Revisit if: playtests (T-08-DENSITY) count more than one row ahead, or coin runs two tiers ahead once real sinks are spent (OEQ-08-4).

## DL-09 — Adversaries

### DL-09-01: Archetypes are manufacturers; 63 of them over the nine creature branches
- Decision: An archetype (`arch.*`) is one data entry whose single tag set is read by four consumers without restatement: evidence (03: opponent kind, challenge band, lethal context), loot (08: creature, harm, deed and org tags; trophy base; flaw), absorption (04: pool gate, eligible entries, cannot_absorb, signature) and behavior (09/06: lists, morale, mind). Sixty-three archetypes cover every branch of the creature facet and every level-2 tag (some archetypes cover two). Each carries a `cannot` list of categorical impossibilities backed by state.
- Alternatives considered: per-adversary hand-authored pools and behaviors (unbounded authoring; no provenance); a dozen coarse archetypes (one per branch) — too coarse for loot gates and behavior (a lich and a skeleton would share a list); keying hybrid/absorber tables on archetypes — rejected per R3 §09.6: the nine branches are the low-cardinality keys, archetypes are instances.
- Evidence: [R3 §6 #14; R3 §09.1–09.3, 09.6] [C:P5] [R: https://2e.aonprd.com/Rules.aspx?ID=2874]
- Serves: goal 2 (classification onto a closed list; one source of truth per creature), goal 1 (every creature carries citable facts).
- Revisit if: 13 needs an archetype the library lacks more than twice (add it; never a new rule).

### DL-09-02: Classify branch first, then archetype; by what it is, not what it does
- Decision: 09.2.4: a two-level enum; tie-break by nature; default horror only when nothing else fits; a figure of speech creates nothing.
- Alternatives considered: one flat enum of 63 (wrong-choice rate rises with options, R4 §3.2 S1).
- Evidence: [R4 §3.2; 00.2.2 hierarchical enums] [data/tags.yaml definitions]
- Serves: goal 2.
- Revisit if: T-00-ATTR-style agreement tests show < 90% branch agreement.

### DL-09-03: Bands are assigned by nature with Story-Engine's guard, ties to the lower rung
- Decision: 09.3.1: five anchored rungs; never from title, location, hostility or dramatic importance; tie → lower; bounded by the archetype's bands.
- Alternatives considered: tie → higher (manufactures lethal warnings; a wrong low band is caught by the advisory, which reads the real numbers).
- Evidence: [R4 §6.3] [00.3.7] [R2 §09 (Cradle's rank as the anchor)]
- Serves: goal 2; BRIEF §4 (telegraphed lethality stays meaningful).
- Revisit if: playtests show creatures consistently felt stronger than their band.

### DL-09-04: The standard line is 06's T-06-12 plus adversary Fend, with T4/T5 Vitality 24/36
- Decision: Attack/Guard/harm/reduction/nerve/tempo as T-06-12; T3+ adversaries Fend (06.6.5, which 06's script omitted); T4 and T5 Vitality lowered from 26/40 to 24/36 so that one equal-band foe is still beaten ≥ 80% with no Focus (P4 87.8%, P5 80.2%; with 26/40 and Fend: 81.6% and 73.6%).
- Alternatives considered: keep 26/40 (breaks 06.10.6's target at P5); drop adversary Fend (contradicts 06.6.5); raise PC lines (not 09's to change).
- Evidence: 09-adversary-sim.py section A [06.10.6] [00.3.7 envelope]
- Serves: goal 2 (the rule as written is the rule simulated); constitution P9.
- Revisit if: 06 changes Fend or the PC lines (re-run section A).

### DL-09-05: Vitality is solved, not chosen; resistances are counters, not weight
- Decision: Every adversary's Vitality is the value inside its band's envelope whose estimated harm ratio against the band's reference PC matches the band standard's divided by (1 + power premium). Resistance and regeneration are excluded from the solve (the PC is assumed to hold the counter); the advisory reports the creature without the counter separately, and the lore check reveals the counter.
- Alternatives considered: PF2e-style hand-picked benchmarks by role (designer judgment per entry; no guarantee of band fidelity); counting resistances in the solve (a vampire would have 2 Vitality and be trivial to anyone with silver — the puzzle disappears).
- Evidence: [R: https://2e.aonprd.com/Rules.aspx?ID=2874 (top-down benchmarks)] [R2 #12 (structural weakness)] 09-gen_data09-output.txt (all 123 entries within fidelity tolerance)
- Serves: goal 2 (a band means the same everywhere), goal 1 (resistances are problems with named answers).
- Revisit if: OEQ-09-3 (premium refit) moves more than a tenth of entries out of tolerance.

### DL-09-06: Improvised creatures go through PR-09-1 and a logged ruling
- Decision: 09.4.8 / PR-09-2: four classifications, engine-built record, ruling logged with signature arch+band+role+variant.
- Alternatives considered: the DM writes a quick stat line (free numbers, SG-01 violation).
- Evidence: [00.15.6] [SG-01] [R4 §9 09]
- Serves: goal 2.
- Revisit if: improvisations become frequent enough that 13 should add entries.

### DL-09-07: Band competence +1…+5 and five attribute rungs
- Decision: T-09-2: `c_b` = 1/2/3/4/5; rungs apex/high/mid/low/feeble (+ none for mindless mental) chosen so that high + `c_b` reproduces 06's reference attack and Guard exactly and mid with no training reproduces 06's tempo reference.
- Alternatives considered: per-archetype free attribute values (unbounded; no shared scale); fewer rungs (an ogre's Agility and an elf's would collapse).
- Evidence: [00.3.5, 00.3.7, 00.4.3 envelopes] [06.2.2] [T-06-12]
- Serves: goal 2 (top-down, reproducible).
- Revisit if: 06 or 00 change the reference lines.

### DL-09-08: Four variants with band-dependent multipliers fitted by simulation
- Decision: minion ½, standard 1, elite ×2 (T1–T3) / ×1.25 (T4–T5), solo ×4 (T1) / ×3 (T2–T3) / ×1.75 (T4) / ×1.5 (T5); reactions, nerve, Focus and powers shift per T-09-5; solos gain Shrug, a phase, a heavy blow. Targets: an elite is one or two words harsher than a standard of its band and never lethal; a solo is hard from T3 up.
- Alternatives considered: one multiplier per variant (13th Age's ×2 / ×3) — at P4–P5 the lone PC's curve is steep, so a fixed ×2 makes an elite T4 lethal (29% wins) and a fixed ×3 makes a T2 solo fair; extra actions for solos (forbidden, INV-11).
- Evidence: 09-adversary-sim.py section C [R: https://www.13thagesrd.com/monsters/monster-creation/] [R: https://lancer-faq.netlify.app/] [06.1.2]
- Serves: goal 2; constitution P9.
- Revisit if: OEQ-09-4 (solos with Focus outside 55–85%).

### DL-09-09: `threat_advisory` is a closed-form estimator of 06's fight, validated against it
- Decision: PR-09-4 computes expected harm and its variance from exact d20 rates, a kill timeline, the morale clock and tempo, then Staggered and loss probabilities, classified by 06's T-06-13 thresholds. Constants (beaten at 1.75 landed blows past Staggered; Staggered tested at Vitality − 1) were tuned to maximize exact agreement with gentler misses not outnumbering harsher ones. Adjustments: companion one gentler (06), surprise one harsher; 06's "no martial calling one row harsher" is replaced by reading the PC's actual line (02's request).
- Alternatives considered: (a) the T-06-13 lookup (cannot read mixed groups, variants, roles, resistances or a real PC's line; 06 itself said "re-run, not a formula"); (b) a summed foe-equivalent rating (the CR failure, R2 #11); (c) a seeded Monte Carlo in the engine (accurate, but not hand-checkable and expensive at framing; kept as the validation reference).
- Evidence: 09-adversary-sim.py section D (586 encounters: 90.4% exact, 100% within one word); 09-estimator-tune.py [R2 #11] [R4 §6.3] [06.10.6]
- Serves: goal 2 (honest, computed difficulty before the fight); BRIEF §4.
- Revisit if: OEQ-09-1 shows played outcomes outside the word's band more than 15% of the time.

### DL-09-10: Lore is a P17 delivery over a fixed, ranked item list
- Decision: 09.10.2: common knowledge by origin (G1) or the archetype's licensed lore (G2); DC by band and rarity (T-09-16); six items ranked by the player; delivered by 01's deliver_count; items become available in the codex and citable facts; a critical failure may plant a false belief but never about lethality.
- Alternatives considered: all-or-nothing identification (the probe's bundled-question failure, R7 Ex.8); free knowledge of weaknesses (removes the puzzle).
- Evidence: [C:P17] [R7 §5 Ex.8] [01.10.4] [06.9.6]
- Serves: goal 1 (knowledge is a plan), goal 2.
- Revisit if: OEQ-09-6 shows tells alone suffice and lore checks feel redundant.

### DL-09-11: Behavior lists are flat first-match rows over closed vocabularies; illegal rows are false
- Decision: 44 predicates and 32 macros, each defined over state; a row whose act cannot be executed now is false; every list ends with `always`; each list states its instinct and parley/yield/retreat conditions.
- Alternatives considered: free-text tactics notes (the DM chooses; leniency and nonsense targets, R4 §6.2); weighted random action tables (randomness where intent should be legible).
- Evidence: [R4 SG-10, §6.2 item 3, §9 09 item 3] [06.9.1] [R: https://www.dungeonworldsrd.com/monsters/ (instinct and moves)] [R1 §09]
- Serves: goal 2.
- Revisit if: playtests show creatures acting stupidly in a situation no predicate covers (add a predicate, never a judgment).

### DL-09-12: Morale breaks per archetype; frenzy is a break
- Decision: `break_then` from 06's closed list per archetype; zealots, abominations and lesser demons break into frenzy (they stop defending); minions one nerve rung lower, elites and solos one higher.
- Alternatives considered: every break is flight (wrong for the cornered and the fanatical).
- Evidence: [06.11.5] [R: https://oldschoolessentials.necroticgnome.com/srd/index.php/Morale_(Optional_Rule)]
- Serves: goal 1 (morale is a lever the player can work).
- Revisit if: frenzied breaks make group fights harder than their advisory says (T-09-MIX).

### DL-09-13: Encounters belong to places; the budget fields Δ −1/0/+1 at 30/55/15
- Decision: T-09-10 from the simulation; crowds are mobs; at most two individuals of the PC's band; bosses are solos or leaders with lower-band help; region tables have a home band with lairs above it as places; the advisory tells the truth about what was rolled.
- Alternatives considered: scaling encounters to the PC (the world levels with you; removes the meaning of bands and of telegraphed danger).
- Evidence: 09-adversary-sim.py section F [R1 #7] [R2 #11] [T-06-13]
- Serves: goal 1 (a world with stakes), goal 2.
- Revisit if: OEQ-09-5.

### DL-09-14: Eight challenge axes, a complication table and rotation toward the stalest
- Decision: axes numbers, toughness, reach, control, ground, objective, clock, talk; `tbl.09.complication` d12 and `tbl.09.mixing` d8; rerolls toward the stalest axis via 12's ledger.
- Alternatives considered: R1 #8's six levers only (no solo-specific "talk" and "control").
- Evidence: [R1 #8] [R2 #12] [12.9.2]
- Serves: goal 1.
- Revisit if: the rotation ledger shows an axis never appearing in a region.

### DL-09-15: The victor remembers (Nemesis table)
- Decision: promotion to recurring and one roll on `tbl.09.nemesis` (d8) when an adversary beats the PC, escapes alive, or survives as a recurring foe; results change wants, fears, followers, rumors and hunts — only one changes numbers (standard → elite), none changes band.
- Alternatives considered: no memory (defeat without consequence, R6 C-20); promotions that raise band (power creep, loot and evidence dishonesty).
- Evidence: [R6 C-20, §A V8] [R: https://www.gamesradar.com/shadow-mordor-nemesis-system-amazing-how-works/]
- Serves: goal 1 (a living, reactive world).
- Revisit if: OEQ-09-7.

### DL-09-16: Defeat dispositions by the victor's nature; `kill_when` switches are recorded facts
- Decision: one of 07's seven per archetype (capture 17, drag to lair 17, drive off 14, kill 11, rob 2, leave 2); `kill_when` lists the closed facts that switch a side to kill, a `[J:flag]` citing the fact; the switch raises 07's disposition warning.
- Alternatives considered: the DM decides when foes "get angry" (mercy and cruelty by narrator mood).
- Evidence: [R6 C-19, C-R5] [R4 §6.2 item 5] [07.6.1, 07.3.3]
- Serves: goal 2; BRIEF §4.
- Revisit if: switches fire in more than one fight in ten (they should be rare).

### DL-09-17: Adversary powers are `pow.*`; adversary Focus is a special budget
- Decision: 68 adversary-only powers in archetypes.yaml (effects by reference only); adversaries also hold 05's pool abilities by id; Focus by band and variant pays for both; Focus emptying only at T5, Focus drains only from T4, each with a tell.
- Alternatives considered: `adversary_only` entries in 05's pool (mixes two owners' content); per-power uses only (no shared budget for casters).
- Evidence: [05.6.13; 05 Interface requests] [00.10.1] [R2 §05]
- Serves: goal 2; constitution P9 companion (one resource).
- Revisit if: 00 rejects the `pow.` prefix (then `ab.adv.*` in a 09 owner-block of abilities.yaml).

### DL-09-18: Five minds decide social and mental rules without judgment
- Decision: mindless, animal, cunning, sapient, alien; each fixes mental immunity, Talk legality, yielding and the reaction roll (09.2.7).
- Alternatives considered: per-entry flags for each rule (inconsistent).
- Evidence: [06.11.5] [12.11.2] [data/tags.yaml trait.nature.mental]
- Serves: goal 2.
- Revisit if: a creature fits none of the five.

### DL-09-19: `reaction_roll` names 12's request; `reaction` stays 06's combat reaction
- Decision: 12 asked for "reaction: true|false" meaning the out-of-combat reaction roll; 06 uses `reaction` for the combat reaction. This chapter names 12's field `reaction_roll`.
- Alternatives considered: one field with two meanings (ambiguity, SG-21).
- Evidence: [12.11.2 step 4] [06.6.5]
- Serves: goal 2.
- Revisit if: 12 prefers another name (rename in data, no rule change).

### DL-09-20: Severity compensation when the envelope binds
- Decision: up to two rungs of primary severity, only when the solve hits the envelope's edge and fidelity is outside 0.67–1.5 (T1: 0.5–2.0). Eleven bestiary entries took a step.
- Alternatives considered: widening the envelope (00's to set); accepting out-of-band entries (a "T2" that fights like a T1 misleads loot and evidence).
- Evidence: 09-gen_data09-output.txt
- Serves: goal 2.
- Revisit if: more than a fifth of entries need compensation (the archetype rungs are wrong).

### DL-09-21: An adversary heavy blow costs one action after its Windup
- Decision: the Windup (an action on an earlier turn) is the price; the blow itself is one action; every heavy attack and shaped power winds up, whatever its severity; solos gain a heavy copy of their primary.
- Alternatives considered: two-action heavy blows like a PC's heavy weapon (a solo would spend its whole turn every other turn).
- Evidence: [06.9.5] [06's script (one-action blows after a windup)]
- Serves: BRIEF §4 (every heavy blow announced a turn ahead).
- Revisit if: 06 changes 06.9.5.

### DL-09-22: Issue I-005 — propose an advisory-offset challenge band to 03
- Decision: a conflict's challenge band = power band + (−2, −1, 0, +1, +2) by advisory word; measured with 04's own pacing script: restores tier pacing to within 2–5 sessions of 04's targets under 09's encounter budget (the foe's raw band leaves the archer at tier 2/3/4 at sessions 20/31/46 and never tier 5).
- Alternatives considered: 09 fielding band+1 foes routinely (a hard or lethal fight as the default — against BRIEF §4); leaving 04's assumption (pacing built on fights the budget does not field).
- Evidence: 09-i005-check.py / -output.txt
- Serves: goal 1 (growth tracks real difficulty, crowds included).
- Revisit if: 03 adopts it (close I-005) or rejects it (04 retunes the great-deed gate).

### DL-09-23: Loot trophy bases and the absorbable exception for giant-kin and beastfolk
- Decision: trophy bases set where branch defaults starve the pool (raptor amulet, deep-water beast cloak, earth elemental amulet, plant gloves, abomination charm, troll charm, wolf and cat cloaks); giant-kin and beastfolk get absorbable pools (requested of 04); the water elemental remains at 2 entries and is filed with 08.
- Alternatives considered: adding pool gate tags the creature does not honestly have.
- Evidence: 09-gen_data09-output.txt loot section [08.3.4] [gen_absorb.yaml]
- Serves: goal 2 (contract compliance), C:P5.
- Revisit if: 08 adds a water-gated property (switch the elemental back to its default base).

### DL-09-24: Out-of-band foes are telegraphed by trigger, not by judgment
- Decision: first perception of an adversary above the PC's band renders a band tell (one band) or fires 07's lethal warning (two or more, where the advisory is always lethal).
- Alternatives considered: the DM decides when to warn (the leniency/forgetting failure, R4 §6.1).
- Evidence: [R2 §09] [R4 §6.2 item 4] [07.3.3]
- Serves: BRIEF §4.
- Revisit if: players report being surprised by a creature's danger after perceiving it.

### DL-09-25: Archetype terrain lists widened so every terrain table and every site pair has its own creatures
- Decision: [revision: I-022, I-029] thirty-four archetypes gained `encounter.terrain` tags (`09_data_arch.py`, `09_data_arch2.py` → `archetypes.yaml`): e.g. wolf + road; troll + road, wetland, frozen; ghost + road, wetland, frozen, deepwood, water; monstrous beast + plains, arid, underground, wetland, frozen; brigand + wetland, arid, water, settlement, plains, ruin; aberration and great dragon + sea. Each is a place the creature plausibly lives or hunts; no band, stat or loot changed.
- Alternatives considered: let tables and site gates draw creatures from outside their terrain (rejected: `encounter.terrain` is the only data that says where a creature lives, so 10's tables would contradict 09's data); new archetypes for the thin terrains (rejected: the existing ones fit once their range was stated honestly, and new archetypes need bestiary, loot and absorbable data).
- Evidence: before, 20 of 112 site pairs gated fewer than three archetypes and frozen held 3 archetypes, arid 5 (`10-gen10_sites.py`); after, 0 pairs below three, and the generic tables draw 12–22 archetypes per terrain. `09-gen_data09.py` output is unchanged apart from the terrain lists.
- Serves: goal 2 (data says where things live; tables and gates agree), goal 1 (varied encounters).
- Revisit if: a pre-made setting or world seed wants a creature excluded from a terrain (it overrides with its own regional table).

## DL-10 — Exploration, Travel, and Sites

### DL-10-01: The world is a place graph, written on mention; hexes are an authoring option
- Decision: Places (regions, areas, settlements, sites, site areas, landmarks, buildings) joined by route links are canonical (10.1.1–10.1.3). Every addressable way, exit, landmark and feature is written before it is narrated (10.1.4); undiscovered places are sealed; discovery carries the finding frame's id (10.1.5). A hex map is authored as a graph whose nodes are hexes.
- Alternatives considered: a hex grid as the rules' geometry (the AI would have to compute adjacency and distance — the long-gap geography failure; text has no map); free-prose geography (31% plant-to-contradiction gap).
- Evidence: [R1 §10 (geography is long-gap state)] [R5 EX-07, EX-14] [00.6.6] [R: https://thealexandrian.net/wordpress/17308/roleplaying-games/hexcrawl]
- Serves: goal 2 (no remembered geography), goal 1 (any place can be set out for).
- Revisit if: T-00-WOM finds narrated-but-unrecorded exits above 2% of turns.

### DL-10-02: Route length is stored in watches at normal pace; the engine converts pace through progress points
- Decision: `travel_watches` (00.6.2) is the length at normal walking pace in fair weather with terrain folded in; a leg needs 6 × W points and a travel watch earns points by pace (10.3.2). The AI never computes miles.
- Alternatives considered: miles plus a terrain multiplier (arithmetic the AI does badly; two numbers per route); PF2's activities-per-hex (needs hexes).
- Evidence: [R5 P-33] [R1 §10] [SG-01]
- Serves: goal 2.
- Revisit if: 13's authoring shows routes whose length varies a lot by season (then add seasonal W to the link).

### DL-10-03: The pace ladder 2 / 4 / 6 / 8 / 9 / 12, steps only downward; a `travel_points` quantity requested
- Decision: crawl 2, slow 4, normal 6, fast 8, ride 9, hard_ride 12 points a watch; burden, weather off-road, night without light and slowing hazards each step down one rung; overloaded cannot travel. Items and abilities cannot change journey speed until 00 adds the quantity `travel_points` (eff.10.travel_points is staged).
- Alternatives considered: percentages (banned, SG-23); letting `speed` (06's bands per move action) double as journey speed (two meanings for one quantity).
- Evidence: riders ~1.5× walkers over a day (horses tire; sustained riding ≈ 30–40 miles vs 20–25 walking); slow careful pace two-thirds (PF2 exploration activities at half speed for Search/Avoid Notice, R5 P-33).
- Serves: goal 2 (integers on a ladder), goal 1 (pace is a player choice with visible trade-offs).
- Revisit if: OEQ-10-1's playtests find ride pace trivializes distance.

### DL-10-04: Way-finding is needed only off road, river and track (or in blind conditions), and rolls once a day
- Decision: 10.4.1: roads and rivers never lose anyone; tracks only in fog, blizzard or lightless night; trackless legs make one way-finding beat a day that rides until conditions worsen.
- Alternatives considered: a check per watch (four rolls a day, mostly noise); Alexandrian's per-hex lost chance (needs hexes); no getting lost (travel loses its geography).
- Evidence: [R5 EX-02, P-31 (Lead the Way per day/hex)] [01.4.2 let it ride] [R: https://thealexandrian.net/wordpress/17464/roleplaying-games/hexcrawl-part-12-at-the-table]
- Serves: goal 2 (few rolls, each meaningful), goal 1 (the beaten way is always open).
- Revisit if: T-10-LOST shows players never leave roads.

### DL-10-05: The way-finding beat is a secret Observe with reach meanings, take-the-time allowed, and an honest G3 when no landmark exists
- Decision: 10.4.2: licensed by `lic.training.wilds_navigation`; unlicensed by its crude fallback only with a visible landmark (10.4.4); otherwise 10.4.5's five paths including "go blind" (legal Move, automatically off course). Secret frame. Reach 0 off course (sealed veer), 1 slower, 2 on course, 3 a better line (+2 points), 4 a discovery. Taking the time (no roll, half points) is legal at Easy–Hard.
- Alternatives considered: navigation as a basic verb (contradicts lic.training.wilds_navigation's scope and VII); a plain pass/fail (wastes reach; P17); hiding nothing (the player would see a failure the character cannot know: 01.4.7).
- Evidence: [C:VII] [01.4.4, 01.4.7] [sim10_nav.py: trained +4 off course 10/35/60/85% by tier; fallback +3 at DC+5: 40/65%] [R5 P-31, P-33]
- Serves: goal 1 (always a way), goal 2 (sealed state, no leniency).
- Revisit if: OEQ-10-4.

### DL-10-06: Supply is one a day; forage yields delivered reach, hunting twice that; want is 07's exhausted ladder
- Decision: 10.6: 1 supply per consumer per day, +1 in heat or arid country without water; half rations; forage = delivered reach per watch (reach − 1 per hour); hunt = 2 × reach and a carcass; snares d6 by game tier; want = one cond.exhausted stack per unfed day, deprivation warning at three (07.8.10).
- Alternatives considered: itemized rations (bookkeeping without decisions); Ironsworn's 0–5 supply track (too coarse to price a hunt against a forage).
- Evidence: [R5 P-30 (supply), P-31 (forage/hunt/fish)] [08.9.4] [07.8.10] [sim10_nav.py: licensed forager ≈ 2.05/1.35/0.85 supply a watch Easy/Moderate/Hard; hunter 4.1/2.7/1.7]
- Serves: goal 1 (living off the land is a real option), goal 2 (one integer, one handler).
- Revisit if: OEQ-10-7.

### DL-10-07: Danger rating (how often) is a separate five-rung field from band (how strong); the night counts one rung higher
- Decision: safe / settled / wild / perilous / deadly (10.9.2), stored on places; selects the d12 face map; the night watch +1 rung; roads by their link's value.
- Alternatives considered: one field for both (a deadly-but-weak swamp of midges and a rare-but-legendary dragon's range need different answers); PF2's terrain flat-check DC (no omen faces).
- Evidence: [R5 P-34 (Shadowdark danger → cadence), P-33] [R6 B-15 (distance as difficulty)] [09.8.2]
- Serves: goal 2 (one rung to pick, a table to read), goal 1 (the West Marches rings are legible).
- Revisit if: OEQ-10-1.

### DL-10-08: One overloaded d12 per watch and per site check; every face means something; a lull is good going
- Decision: T-10-10: encounter, omen, local event (12's event focus), depletion, weather shift (site: stir, shift), discovery, opportunity, lull (+1 point; the pending timer pauses). Face counts scale with rating (E 1/1/2/3, O 1/2/2/2 travel).
- Alternatives considered: the Alexandrian's d12 with only encounter and keyed-location faces (mostly null); a d6 1-in-6 encounter die (no texture); TOR's event-paced travel (excellent density but needs a party of roles and a marching test per stage; adopted in spirit through roles and the omen timer).
- Evidence: [R6 B-14, B-R5] [R: https://necropraxis.com/2014/02/03/overloading-the-encounter-die/] [R: https://necropraxis.com/2014/12/23/hazard-system-v0-2/] [R5 P-32, P-36] [sim10_travel.py: arrivals 0.38/0.57/0.77/0.89 a day; one each of event, discovery, opportunity, depletion, weather shift per ~3 days]
- Serves: goal 2 (the engine rolls; nothing is the DM's mood), goal 1 (every watch can matter).
- Revisit if: OEQ-10-1.

### DL-10-09: Omens before threats — a hostile encounter is always a pending threat first
- Decision: 10.9.5: threat rows become a sealed pending threat with a rendered sign; it arrives on the next E or O face or the fourth check (lulls do not count); one pending threat at a time; out-of-band threats say so in their first sign; the player may avoid, investigate, prepare, seek or ignore (10.9.6).
- Alternatives considered: Mausritter's omen only on a near-miss (most threats unannounced); omen as pure flavor (no decision); a fixed arrival time (too predictable; the E/O race keeps it uncertain).
- Evidence: [BRIEF §4] [R5 P-36, P-17, P-19] [R6 B-R5, C-01..C-04] [sim10_travel.py: 50% avoidance cuts hostile arrivals ~40%]
- Serves: goal 1 (information before danger: real choices), goal 2 (state-driven telegraphing; INV-14's spirit for encounters).
- Revisit if: OEQ-10-2.

### DL-10-10: Encounter tables are two sub-tables; generic terrain tables ship, audited 30/55/15
- Decision: 10.10.1–10.10.2: threat d20 by relative band (faces 1–6 home−1, 7–17 home, 18–20 home+1) and non-threat d6; a d12 threat share by rating (1–3 / 1–7 / 1–9 / 1–10) picks the sub-table; eleven generic terrain tables in travel.yaml pass PR-10-8 by construction; regional tables (13) use the same shape.
- Alternatives considered: one table per terrain per band (55 tables); one flat table per terrain (the threat share could not vary with the ring).
- Evidence: [09.8.1–09.8.2 (T-09-10, Δ 30/55/15)] [gen10_travel.py audit] [R5 AV-06]
- Serves: goal 2 (budget by construction), goal 1 (the same wood is gentler near home).
- Revisit if: 13's tables need a fourth sub-table (e.g. rumors-as-encounters).

### DL-10-11: Hazards that can kill always speak first; cold, heat, falls, want and magic take no reduction
- Decision: 10.12: every hazard has signs, `perceived_on_sight`, `lethal_context` and `aftermath`; unperceived hazards cannot be lethal (07.3.5); S4+ perceived raise the severity warning; blizzard, bitter cold and scorching heat are S3 with lethal context (exposure kills, warned); `no_reduction` on internal harms.
- Alternatives considered: weather as narration only (the CoC-Seduce failure); all exposures S1 (no frontier ever kills); armor reducing cold (absurd; 08.1.6 reduces attacks).
- Evidence: [R4 §9 10 item 1; R: https://arxiv.org/abs/2607.02802] [07.3.3–07.3.6, 07.10] [R5 EX-05]
- Serves: goal 2, BRIEF §4.
- Revisit if: playtests find exposure harm swamps travel (then S1/S2 entries move to every other watch).

### DL-10-12: Weather is fourteen states, five climates, four seasonal d12 regimes, with one-in-three persistence
- Decision: 10.11; `weather.yaml`. Tomorrow is rolled a day ahead (forecasts exist); a d6 of 1–2 holds yesterday's weather; the shift face moves today along worse/better links; standing facts (snow_lying, high_water, drought) carry weather across days.
- Alternatives considered: Cairn's d6 effect-only weather (no states for 05's source test or the narrator); independent daily rolls (flip-flopping skies); a Markov chain per climate (opaque to audit).
- Evidence: [R5 EX-04, P-36] [05.7.3 (weather record)] [02 (weather-ache)]
- Serves: goal 2 (no invented weather), goal 1 (forecasting is a skill worth having).
- Revisit if: OEQ-10-5.

### DL-10-13: Sites are Delve's theme × domain, eight by fourteen, gating denizens, dangers and place-gated loot
- Decision: 10.13.2; `sites.yaml`: 8 themes × 14 domains = 112 site kinds from 22 cards; each pair gates the denizen table (archetype creature tags ∩ domain terrain; theme-only fallback for the 20 thin pairs the generator lists), dangers, discoveries, features, hazards, traps and the hoard's place axis (08.3.4 item 4, 08.3.12).
- Alternatives considered: hand-authored dungeons only (no infinite sandbox); Delve's d100 denizen matrix (our archetypes already carry bands and terrain); random room tables without a theme (no P5 gate).
- Evidence: [R5 P-28] [C:V, C:P5] [R2 #13] [gen10_sites.py validation: 92 of 112 pairs gate ≥ 3 archetypes by terrain]
- Serves: goal 1 (endless, coherent places), goal 2 (closed tables).
- Revisit if: 13 finds a common site kind that fits no pair.

### DL-10-14: Explore onward is a basic-verb beat by approach (care, stealth, haste); progress = delivered reach; each success opens an area
- Decision: 10.13.6: care = Observe (2 intervals; perceives traps), stealth = Sneak (1; unaware denizens; no unshuttered light), haste = Move at Great reach and loud (1); DC the site's stored explore tier; Risky because the danger clock listens; reach ≥ 1 makes a new area (PR-10-7).
- Alternatives considered: Delve's three-stat roll with d100 outcome columns (a second resolution system); area-by-area mapping (EX-14: text has no map).
- Evidence: [R5 P-28 (edge/shadow/wits), P-13] [01.14.6 (extended actions)] [00.8.2 (progress = delivered reach)]
- Serves: goal 1 (the approach is a meaningful choice), goal 2 (one pipeline).
- Revisit if: OEQ-10-3.

### DL-10-15: The progress and danger clocks do not void each other; roused is escalation, not defeat
- Decision: 10.13.8–10.13.9: completing the heart does not stop the place waking on the way out (`races_with: null`); a full danger clock rouses the site (cadence every interval, rating +1, denizens alarmed, the guardian comes) and resets; the second fill brings the guardian at once.
- Alternatives considered: 00.8.5 racing (finding the heart would end the danger: no tension on the way out); rousing as a fail state (soft-lock).
- Evidence: [R5 P-20 (Delve menace), P-35 (escalation to a climax)] [00.8.5] [sim10_site2.py: medium site roused first 25% careful / 21% stealthy / 36% hasty at +5; 4/3/9% at +9]
- Serves: goal 1 (pressing on is a real gamble), goal 2 (state, not mood).
- Revisit if: OEQ-10-3.

### DL-10-16: Sizes 6/8, 8/8, 12/12 and vast 12+12/12; cadence 3/2/2/1; persistence with drift, decay and regrowth
- Decision: 10.13.3, 10.9.3, 10.13.11: small/medium/large/vast clocks; site checks every 3 intervals (settled) to every 1 (deadly), one step faster in the dark; a return loses 1 progress a full week away (≤ half, never below secured areas); the danger clock decays 2 a quiet day; regrowing themes repopulate weekly.
- Alternatives considered: Delve's rank-based progress (no clock primitive reuse); sites that reset entirely (no persistence: the West Marches promise is a persistent world).
- Evidence: [sim10_site2.py size sweep: small 12%, medium 25%, large 26% roused at +5 care] [R5 P-28 (return: clear progress by the lower challenge die)] [R6 B-15]
- Serves: goal 2 (persistent state), goal 1 (a site worth returning to).
- Revisit if: OEQ-10-3.

### DL-10-17: Traps carry telltales; tiers and harm scale by site band; the trap's effect DC is its detect tier one rung up
- Decision: 10.14.3: a telltale is always narrated as a feature (plain wherever harm is S3+, subtle allowed only at S1–S2 bands); passive notice or a look at the telltale perceives it; eight ways to deal with a perceived trap, seven of them basic verbs (10.14.5).
- Alternatives considered: hidden traps found only by search (the "gotcha" R1 lists as a DM mistake); a fixed DC table (traps would not scale with the place).
- Evidence: [BRIEF §4] [R1 §07 (traps that always counter the players)] [R5 AV-08] [07.3.3, 07.3.5]
- Serves: goal 1 (creative bypasses are anchored), goal 2 (no lethal trap without a perceived sign).
- Revisit if: OEQ-10-6.

### DL-10-18: The march allowance is two units a day; forced marches cost 07's exhaustion stacks with push-on
- Decision: 10.3.5: walkers and mounts 2 units; fast pace 2 units a watch; each unit over a stack of cond.exhausted (deferrable by 07.8.10's push-on).
- Alternatives considered: TOR's fatigue on arrival (a second fatigue track); no limit (journeys become pure arithmetic).
- Evidence: [R5 P-32 (fatigue), P-31 (quarter days)] [07.8.10]
- Serves: goal 1 (speed vs strain is a choice), goal 2 (one condition for all strain).
- Revisit if: players never push past two watches (then the third watch is only half a unit).

### DL-10-19: Journey roles are 03's four; one per traveler per watch; the solo PC defaults navigator or lookout
- Decision: 10.5: navigator, lookout, scout, forager with pace limits and deterministic effects; companions take them (16).
- Alternatives considered: TOR's guide/hunter/look-out/scout (hunter merged into forager to match 03's counters); no roles for a solo PC (companions would add nothing to travel).
- Evidence: [R5 P-31, P-32, EX-03] [03.9 cnt.journey]
- Serves: goal 1 (companions matter on the road), goal 2.
- Revisit if: 16 needs a fifth role (e.g. quartermaster) — add it here with an evidence tag.

### DL-10-20: Sixteen handlers, exposures in phase 2, progress in 4, checks in 7
- Decision: T-10-23; nine reserved by 00 defined, seven added (wayfinding, two exposures, site recovery, day reset, regrowth, scene frame).
- Alternatives considered: folding exposures into the check handler (then periodic harm would run after the encounter roll, inverting 00.7.5's order).
- Evidence: [00.7.4–00.7.6]
- Serves: goal 2 (no "remember to…").
- Revisit if: integration finds a phase conflict with another chapter's handler.

### DL-10-21: Three level-3 terrain tags proposed, none used yet
- Decision: tags.10.yaml proposes terrain.ruin.fortress.tower, terrain.road.causeway, terrain.water.river.ford for 13's authoring.
- Alternatives considered: using them in data now (03 has not adopted them; data must validate).
- Evidence: [00.5.5]
- Serves: goal 2.
- Revisit if: 03 declines them (then the tower domain keeps terrain.ruin.fortress).

### DL-10-22: The one pacing opt-in: the omen timer pauses in RELAX and recovery
- Decision: 10.9.7: during 12's RELAX or a recovery window a pending threat arrives only on an E or O face; nothing else in this chapter reads pacing.
- Alternatives considered: suppressing encounter faces in RELAX (a hidden adjustment 12.7.6 forbids); not opting in (a defeated PC could meet a second threat within a day by the timer alone).
- Evidence: [12.7.2, 12.7.5–12.7.6] [R6 B-10, B-11]
- Serves: goal 2 (declared, logged), goal 1 (room to recover).
- Revisit if: playtests find RELAX makes travel feel toothless.

### DL-10-23: Light burns by the interval in every mode; scene light is computed; darkness has four mechanical effects
- Decision: 10.7: `h.10.light` everywhere (night travel by torch costs six torches a watch); scene light by first match (T-10-9); darkness → blinded for sight, crawl, site cadence faster, unperceived hazards not lethal; a carried light makes its bearer visible.
- Alternatives considered: Shadowdark's real-time torch (meaningless in async text, R5 X-05); light only in sites (night travel would be free).
- Evidence: [R5 P-13, P-34, EX-09, X-05] [08.9.5] [06.3.7]
- Serves: goal 2, goal 1 (light is a resource the player manages).
- Revisit if: T-00-SITE shows light never runs short (then torches burn 4 intervals).

### DL-10-24: A venture starts on leaving a haven and ends on entering one; havens have no time-tick die
- Decision: 10.2.2–10.2.3: `safe` is place data or an 11 write; the venture record feeds 11's reckoning and 12's bookkeeping.
- Alternatives considered: ventures declared by the player (forgettable); checks in havens at a low rating (the base would feel unsafe; 11 and 12 already bring trouble to the gate when the world moves).
- Evidence: [R5 P-12] [R6 B-15, B-R7] [07's request] [00.7.2]
- Serves: goal 2, goal 1 (a safe home base is a West Marches promise).
- Revisit if: 11 needs ventures that end at a non-haven (e.g. a long-term camp).

### DL-10-25: Lost is sealed; the veer is engine-drawn; the seal opens on expected arrival + one watch, a beat, or recognition
- Decision: 10.4.6–10.4.7: the narrator shows true terrain and never says "lost"; the player learns it as the character does; recovery is backtrack, reorient or strike a line — costing time, never a dead end.
- Alternatives considered: telling the player at once (the frame would leak what the character cannot know); a lost check every watch (noise).
- Evidence: [R5 EX-02] [R: https://thealexandrian.net/wordpress/17308/roleplaying-games/hexcrawl (veering)] [01.4.7] [C:P16]
- Serves: goal 2 (sealed state), goal 1 (getting lost is an adventure, not a trap).
- Revisit if: OEQ-10-4 finds lost days dead-end.

### DL-10-26: The generic encounter tables are written per home band, and the audit fails what it used to repair
- Decision: [revision: I-029] each terrain branch's generic table (`travel.yaml#encounter_tables`) holds one d20 threat sub-table per home band 1–5 (`threat_by_home`, 55 in all; T-10-16), hand-written in `_process/simulation/10_data_enc.py` against T-09-10's shapes, with two new row fields: `variant` (09.4.6) and `leader`. Every row names an archetype fielded at its band, so the engine never clamps; at home 1 the home − 1 faces are band-1 creatures written small, at home 5 the home + 1 faces are band-5 solos (09.8.2). PR-10-8 now also fails a lethal high face, an archetype outside its fielded bands and a broken shape rule (it used to repair the shape silently). Thirty-four archetypes gained terrain tags (`09_data_arch*.py`, DL-09-25) so each table draws only creatures that live in its terrain (`10-gen10_travel.py` checks it).
- Alternatives considered: keep one band-relative table and tune counts (rejected: the same row is fair at one home band and lethal at another; groups of three or more at the home band are lethal from P2 up by T-09-10, so no single count works across bands, and archetype band ranges force clamps); generate the generic tables with PR-10-10 (rejected for the generic ones: they are the hand-written, flavoured fallback every region leans on; PR-10-10 is kept for pools nobody wrote by hand); add ladders of archetypes to one row (rejected: harder to audit and to read than five short tables).
- Evidence: `10-word-audit-output.txt`: 55 of 55 tables pass (was 7 of 55); no lethal face at the middle or high count; word mix trivial 35.7 / easy 21.5 / fair 34.5 / hard 8.2 / lethal 0 %; 12–22 distinct archetypes per terrain; repeat chance ≤ 0.195 per table (first draft mean 0.176, max 0.255). T-09-10 and the shape matrix in the audit's history (I-029).
- Serves: goal 2 (the fallback table is in budget at every band, so PR-10-8 step 5 is safe), goal 1 (a world that does not scale to the PC is still survivable where its band says it should be).
- Revisit if: T-09-MIX-CAMPAIGN (OEQ-09-5) finds the word mix too gentle (hard 8% against its 30% target) — then raise start shapes at home bands 2–4 and re-run the audit.

### DL-10-27: One builder for every table nobody wrote by hand (PR-10-10), and a pool for every site pair
- Decision: [revision: I-022, I-028] PR-10-10 builds a threat sub-table from a weighted pool: eight slots in 30/55/15, an archetype drawn per slot among those fielded at its band, a start shape (T-10-25) stepped down a fixed ladder until the row's PR-10-8 word is at most fair (home + 1: hard). A site's denizen table uses its pair's pool (`sites.yaml#denizen_pools`, all 112 pairs now gate at least three archetypes, so the old 20-pair fallback list is gone) with the theme gate alone as fallback; a world seed's regional tables use the seed's pool (12.16). Tables built this way pass PR-10-8 by construction.
- Alternatives considered: authoring 112 × 5 site tables (rejected: 560 hand tables, and a world seed's regions are unknown in advance); the old rule "the archetype's usual group at band − 1 / band / band + 1" (rejected: it is the shape that failed I-029 on the generic tables).
- Evidence: `10-site-tables-output.txt` (seed 1022): 560 of 560 pair × band tables pass PR-10-8; 4,456 of 4,480 slots from the pair pool, 24 from the theme gate, 0 by nearest band. `12-world-seed-output.txt` audits a seed's regional tables built the same way.
- Serves: goal 2 (no judgment in table building; P5's pool gate applied to who lives where), goal 1.
- Revisit if: played delves report site tables that feel samey (then add per-theme start-shape offsets).

## DL-11 — The Living World

### DL-11-01: The World Turn runs at every `week` boundary, in eight fixed steps
- Decision: `h.11.world_turn` (week, phase 6) runs Elapse → Maintain → Timelines → Faction actions → Consequences → Attention → News and rumors → Queue, whatever the mode, including timeskips; `advance_time` never skips it (INV-15).
- Alternatives considered: run it only at downtime (the world freezes during long expeditions, R5 P-23's warning); run it per session (sessions are not fiction time, 00.7.9); a daily faction turn (seven times the bookkeeping for no perceivable gain; situations that need days run on `day` instead).
- Evidence: [R6 B-01, B-R1 (SWN's maintain → goal → action → rumors)] [R5 P-23 "each downtime or each 7 in-world days, whichever first"] [R6 B-06 (a fixed cadence)] [00.7.4–00.7.7]
- Serves: goal 2 (the world moves without the DM remembering); goal 1 (time spent anywhere has consequences the player can read).
- Revisit if: T-11-PULSE shows players feel the world is too busy or too still at weekly cadence.

### DL-11-02: The World Turn never touches the PC directly; it reaches the PC as traces and bangs
- Decision: no World Turn write harms, costs, moves or licenses the PC, or resolves a protected thread; threats wait in the bang queue for chapter 12's director; only an event at the PC's location interrupts.
- Alternatives considered: let faction actions resolve against the PC off-screen (Blades' downtime entanglements partly do) — rejected because a loss the PC never had a frame to answer violates INV-5/INV-6's spirit and R1 #9 ("never make hidden adjustments").
- Evidence: [R1 #9] [R6 B-11 (the director decides when)] [12.7.4] [07's Two-Key rule]
- Serves: goal 1 (every loss is something the player could act on); goal 2 (fewer off-screen judgments).
- Revisit if: playtests show entanglements expiring unfired so often that factions feel toothless (then shorten bang expiry, not bypass frames).

### DL-11-03: Faction actions are d20 checks: d20 + rating + 2 × tier vs DCs whose scope term cancels the actor's tier; goal ticks 2/1/0
- Decision: one faction check on 00.3.10's degrees; goal DC = 10 + 2 × tier + 3/5/7 by scope; opposed DC = 10 + defender rating + 2 × defender tier; goal clock ticks critical success 2, success 1, else 0; critical failure is a slip.
- Alternatives considered: SWN's opposed d10s (a second die family for checks, against 00.3.1); Mausritter's d6 for everyone (too coarse for factions the player engages); ticks of 3/2/1 — simulated: goals every 8 weeks per faction and 47% of factions at tier 5 in two years (runaway).
- Evidence: [R6 B-01, B-02] [R5 P-23, P-25] [rules/_process/simulation/11-world-sim.py: 2.5 goals per faction per year, mean tier +0.6 over two years, 8% tier 5; re-run at integration with 11.3.4's realm-grow cap applied in the script (I-026): mean tier +0.25, highest tier 3, 0% tier 5 (T-11-24)]
- Serves: goal 2 (the AI never decides outcomes for factions).
- Revisit if: T-11-GOALS falls outside 1.5–3.5 goals per faction per year with real regional factions.

### DL-11-04: What a faction does is a temperament agenda table rolled by the engine, with a targeting ladder
- Decision: six temperaments, each a d6 row (about half `goal`), three overrides (slip → recover; war → strike; +2 status → aid), conditions read from state; targets by a fixed ladder.
- Alternatives considered: the DM chooses each faction's action "as fits its goals" (the positivity bias of R4 W3 makes factions never act against the player); a full SWN asset economy (bookkeeping the player never perceives).
- Evidence: [R4 W3, W12] [R6 B-01 ("one action per faction")] [R6 B-20]
- Serves: goal 2.
- Revisit if: playtests show a temperament's row produces implausible behavior three times (rewrite that row).

### DL-11-05: Full factions take the turn; petty factions roll one d6 (named "full/petty", not "major/minor")
- Decision: full = tier ≥ 2, or engaged with the PC, or named by a thread/situation/rank, or an officer met; at most six per region; the rest roll Mausritter's d6. "Major/minor" are banned severity words (T-00-22; 12's terminology note), so the classes are "full" and "petty".
- Alternatives considered: one engine for all (cost without perception); petty factions frozen (the small fry never change).
- Evidence: [R5 P-25, P-23] [R6 B-20] [T-00-22]
- Serves: goal 2 (cost proportional to perception).
- Revisit if: petty factions' completions feel random to players (then give them traces only at completion — already so).

### DL-11-06: Tier 0–5 with hold; ratings sum 4 + 2 × tier capped at tier + 2; growth past tier 3 needs a realm-scope grow goal; the weight of size each season
- Decision: Blades' tier and hold (lose hold when weak → drop a tier, hold strong; gain when strong → rise with hold weak); four ratings (force, cunning, wealth, sway); rise above tier 3 only via realm grow; tier ≥ 3 factions roll d20 + highest rating + stage vs 10 + 2 × tier each Season Turn or lose hold.
- Alternatives considered: SWN's faction hit points (an attrition grind players reported as stalling); no size check (simulation: steady drift to tier 5).
- Evidence: [R6 B-02, B-05] [simulation T-11-24] [08.7.2's tier-to-band mapping 0–1 → 1 … 5 → 5]
- Serves: goal 2; bounded escalation.
- Revisit if: T-11-GOALS shows > 10% tier-5 factions after two years or tier collapse below the starting mean.

### DL-11-07: Consequence propagation is one link per World Turn; situations carry sealed default timelines
- Decision: immediate `on_fact_set` reactions may only queue/tick/write at depth 1; weekly reactions run in step 5 over the change log and their writes are next week's inputs; most-specific-eligible wins; ≤ 1 reaction per change, ≤ 6 per region per turn; situations' timelines are written whole and sealed at creation with `prevented_by` facts.
- Alternatives considered: free-form DM consequences (the dominant "abandoned plot element" and leniency failures); unbounded chains (runaway escalation in one turn); timelines "decided when needed" (R4 W8).
- Evidence: [R6 B-12, B-17, B-19] [R1 #10] [00.10.8 depth rule]
- Serves: goals 1 and 2.
- Revisit if: players report consequences arrive "too late to feel connected" (then mark more reactions immediate).

### DL-11-08: Linchpins carry four pre-declared, sealed fates
- Decision: dies / captured / turned / exposed, each an effect list written when the faction is created; fired by fact triggers; once each.
- Alternatives considered: improvised world-state changes on a leader's death (inconsistent, AI-decided); Kenshi's single world-state per NPC (less expressive).
- Evidence: [R6 B-08] [R1 #10 (T=0 isolation)]
- Serves: goal 1 (killing the warden is a knowable choice); goal 2.
- Revisit if: fates of generic templates read as repetitive across factions (author template-specific fate lists).

### DL-11-09: Status moves only by known deeds, by a fixed step table, capped per turn
- Decision: T-11-3; `[J:flag]` known (uncertain → false); small rows ±1 per turn, weight rows ±2, total ±2 per turn; unknown deeds held for aftermath links; a status write recomputes members at once.
- Alternatives considered: DM-judged attitude shifts (sycophantic drift, R4 W2/W4); Blades' exact rule (−1/−2 per operation) without a knowledge gate (factions omniscient).
- Evidence: [R6 B-02] [R5 P-22] [03.10] [15.1.3]
- Serves: goal 2; goal 1 (stealth and secrecy matter).
- Revisit if: statuses swing more than two rungs a month in play.

### DL-11-10: Every consequential change leaves a trace; bangs carry intensity_delta and specificity; queue of six
- Decision: four trace kinds (news, rumor, visible change, omen); T-11-10 maps changes to traces; bangs default intensity threat 3 / social 1 / opportunity 0; specificity pc_deed > npc > faction > region > generic; queue cap 6; a kicker whenever no personal bang is queued.
- Alternatives considered: summaries of off-screen events at session start only (no in-world texture); unbounded queue (12's director drowns).
- Evidence: [R6 B-20 (Sylvester)] [12.7.4] [R6 B-19]
- Serves: goal 1 (the world is legible); goal 2.
- Revisit if: T-11-TRACE shows players cannot name off-screen faction acts.

### DL-11-11: Rumors' truth is rolled at birth by source and never changed except to outdated; spread by scope steps
- Decision: T-11-11's d10 rows (eyewitness 60% true … boast 20% … planted 0%); a d6 distortion; every rumor points to a real placement (false ones to a refuting one); spread one step per World Turn to neighbors (≤ 8 watches), region in 2, realm in 4 more; beyond two steps a new hearsay rumor.
- Alternatives considered: DM-chosen truth (the AI's bias toward useful/true); fixed 1/3 splits (no texture by source).
- Evidence: [R6 B-04, B-R6] [R6 A-15 (scopes by social distance)] [15.9.18]
- Serves: goals 1 and 2.
- Revisit if: T-11-RUMOR shows players stop investigating rumors (truth rate too low) or never doubt them (too high).

### DL-11-12: World content has lifecycles and caps; the season boundary consolidates
- Decision: hooks expire at 8 weeks; unprogressed non-vow threads at 13 weeks (protected 12 scenes); caps: 12 active threads, 8 seeded hooks known, 8 situations/region, 6 full factions/region, 6 bangs, 3 reputation entries/scope; vows never expire.
- Alternatives considered: let the register grow (the long-campaign failure of every LLM narrator, R4 W11); expire vows too (betrays the player's oath).
- Evidence: [R1 #10] [C:VI] [R4 W11]
- Serves: goal 2; Principle VI at world scale.
- Revisit if: T-11-HOOKS shows players lose threads they cared about to expiry.

### DL-11-13: Attention is a per-faction hidden clock of 8 fed by loudness; completions raise pursuit and draw entanglements
- Decision: Blades' heat generalized: loudness quiet/contained/loud/wild computed from the venture record; decay 1/week; Lie low −2; pursuit 0–3 sets the entanglement column.
- Alternatives considered: one global notoriety meter (TOR's Eye; loses who is noticing); per-region heat only (loses which faction acts).
- Evidence: [R5 P-18, P-26] [R6 B-02] [simulation: war scenario ≈ one entanglement or move every 9 weeks]
- Serves: goal 1 (consequences proportional to loudness); goal 2.
- Revisit if: T-11-HEAT rates the enemy "relentless".

### DL-11-14: Battles are an anchor on breaking clocks; level-3 situation tags proposed
- Decision: 11.3.15's racing breaking clocks (4/6/8/12 by tier), faction checks per time unit, the PC's beats as ticks; proposes `situation.conflict.skirmish.battle`, `situation.social.court.sitting`, `situation.downtime.project.domain`.
- Alternatives considered: no mass combat (16 and 06 both asked for it); a full wargame (bookkeeping beyond perception).
- Evidence: [R5 P-21 (progress vs tension clock)] [00.8.5] [16.7.12]
- Serves: goal 1 (armies are a legal arena); goal 2.
- Revisit if: battles take more than one session-hour to resolve in play.

### DL-11-15: Reputation is {content, scope, score} from witnessed deeds only, with triangular thresholds, epithets, valence by community values, fading and folding
- Decision: points 1 per noteworthy carried packet; score 1/3/6/10/15; epithet at score 2 with two noteworthy packets; valence computed from the scope's faction values; spread settlement → region → realm at score − 2; fade after four seasons below score 4; three entries per scope with folding.
- Alternatives considered: one renown scalar (Mount & Blade; no content); Ars Magica's exact XP curve (5 × (n+1) — too slow for a solo campaign's span).
- Evidence: [R6 A-15, A-16, A-18, A-19, R-A3] [03.10.5] [00.17.1 Q22]
- Serves: goal 1 (the world speaks of what the player did); goal 2.
- Revisit if: T-11-REP falls outside 4–8 sessions to score 3.

### DL-11-16: Threads are ranked troublesome…epic onto clocks 4/6/8/12/12+12 with flashpoints at half and imminent
- Decision: Ironsworn's ranks on 00's clock sizes; ticks by delivered reach, core clues +1, milestones +2, random events +1 (never the last); flashpoints force a turn; no final progress roll (beats already rolled).
- Alternatives considered: Ironsworn's progress roll at the end (double-counts uncertainty already in the beats); unranked threads (no reward or expiry scaling).
- Evidence: [R5 P-14, P-08] [00.8.3]
- Serves: goals 1 and 2.
- Revisit if: threads stall mid-clock in playtests despite flashpoints.

### DL-11-17: Every hook has ≥ 3 placements of ≥ 2 kinds and a fallback; the hook supply keeps 3+ known open matters
- Decision: activation builds a 15-style case; fallbacks fire after 3 pursued scenes without progress or when stalled; supply ladder: the PC's own → ally → faction → situation → table.
- Alternatives considered: hooks with single leads (the probe's soft-lock); unlimited hook generation (flood).
- Evidence: [R6 B-13, B-R4] [R5 P-41] [C:P16] [simulation: < 3 known in 4 of 104 weeks; never > 10]
- Serves: goal 1 (never stuck); goal 2.
- Revisit if: T-11-HOOKS shows a session opening with no actionable lead.

### DL-11-18: Ranks are seat-limited rungs with obligations, conferred at sittings; `institutions_matching` adds `heard` and `teachers`
- Decision: five rungs (unlimited, unlimited, tier + 1, 1 + tier ÷ 2, 1); requirements of status and reputation; closed list of benefits (title, access, followers 2/4/6, lifestyle, authority, gifts, standing); obligations (duty, service, values); provisional first season; contests by V9 trials.
- Alternatives considered: ranks granting capability (forbidden by 04.11, 00.17.1 Q22); unlimited seats (no politics).
- Evidence: [R6 A-22, R-A5] [04.11] [16's and 15's requests]
- Serves: goal 1 (institutions are playable); goal 2.
- Revisit if: players find obligations so heavy they never take ranks.

### DL-11-19: Holdings yield by a stewardship check reading 08's dice; great projects change the map through a closed list; rulership lets the player choose a domain's action
- Decision: d20 + steward modifier (+2 managed) vs 15 chooses higher/one/lower/none of 08's yield dice; ten world-change kinds; the PC's domain is a faction whose action and goal the player picks.
- Alternatives considered: flat yields (no play in stewardship); free-form world changes (unbounded); domain-management minigame (ACKS-scale bookkeeping).
- Evidence: [R5 LW-09, LW-10, P-24] [08.8.8] [15.12] [R6 D-14]
- Serves: goal 1 (the player can change the world and rule it); goal 2.
- Revisit if: yields create wealth faster than 08's anti-inflation targets.

### DL-11-20: Retirement is the largest structural retirement; only bounded channels carry value
- Decision: everything the character is retires (callings, abilities, licenses, competence, fate, seats); the world keeps the chronicle, reputation, holdings and the character as an NPC.
- Alternatives considered: playable return of retired PCs (Wildermyth; undermines finality); full inheritance of power (breaks C:VI and 02.2.7).
- Evidence: [R6 D-R2 step 5, D-05] [C:VI] [04.11.4] [02.2.7]
- Serves: Principle VI; goal 1 (finishing is meaningful).
- Revisit if: players decline to retire characters because the successor feels too weak (then improve the ledgers' strong results, never the floor).

### DL-11-21: The calendar: four 91-day seasons of a quarter day plus three 30-day months; a 28-day moon
- Decision: 364 = 4 × (1 + 3 × 30); weeks unbroken; every season and year starts on weekday 1; thirteen moons a year; names are 13's.
- Alternatives considered: thirteen 28-day months (misaligned with seasons: 91/28 = 3.25); twelve 30-day months plus four floating days (the chosen shape, with the days fixed as quarter days).
- Evidence: [00.7.1] [R5 TM-07]
- Serves: goal 2 (dates are computable).
- Revisit if: chapter 13's setting needs a different month count (it may rename, not re-divide).

### DL-11-22: Aging from a people's age, by Endure checks per Year Turn; aging marks; age ends careers, never lives
- Decision: checks from 35/50/80/120/300 by people at Easy→Very hard by decade; failure → an aging mark (−1 Might/Agility/Endurance within 00.4.3 (c)); 3 marks → yearly retirement offer; 5 → career end; NPC deaths by an aging Oracle.
- Alternatives considered: Ars Magica's aging table with death (violates INV-6); no aging (a decades-long sandbox with ageless heroes; R5 HR-10).
- Evidence: [R5 HR-10, P-44] [R6 B-05, D-08] [00.4.3]
- Serves: goal 1 (time matters); INV-6.
- Revisit if: long campaigns end by age before players choose to retire (raise the starting ages).

### DL-11-23: The season boundary is Principle VI's boundary point, telegraphed a week ahead by a herald
- Decision: `h.11.season_turn` before `h.04.season_consolidation`; at week 12 an out-of-fiction `[SEASON]` herald lists everything due (04's provisional grants, 11's provisional ranks and phenomena, expiries, fades); nothing consolidates elsewhere except retirement and overflow caps; world phenomena are provisional content confirmed only by `confirm_when`.
- Alternatives considered: continuous consolidation (VI forbids piecemeal); an untelegraphed boundary (VI requires telegraphing).
- Evidence: [C:VI] [R1 #15] [R2 #15] [R3 11.3, 11.7] [R5 P-44]
- Serves: Principle VI; goal 1 (the player can act before what is due).
- Revisit if: players miss the herald (render it in the SITUATION block too).

### DL-11-24: The chronicle is the append-only truth with a closed list of writers; digests are never re-digested
- Decision: writers listed in 11.12.2; ≤ 5 World Turn lines; corrections supersede; recaps, NPC citations, continuity checks and legends read it; season and year digests from raw entries only.
- Alternatives considered: DM-written session summaries (summary-of-summary drift, 00.6.9 d; R4 W9).
- Evidence: [R6 B-07, B-12, B-R8] [00.6.9] [R2 11 (durable memory)]
- Serves: goal 2.
- Revisit if: the chronicle grows faster than retrieval can serve (then add per-entity indexes, never deletion).

### DL-11-25: Ironsworn's legacy rolls converted to d20 + ledger (0–10) with thresholds 20 / 12
- Decision: three ledgers scored from the record; d20 + ledger: ≥ 20 strong, 12–19 opportunity, ≤ 11 trouble (5/40/55% at 0; 30/40/30% at 5; 55/40/5% at 10); trouble is always a hook.
- Alternatives considered: Ironsworn's 2d10 challenge dice (a die family 00.3.1 reserves; checks use d20); a flat inheritance (no texture).
- Evidence: [R6 D-04] [R5 P-43] [exhaustive d20 enumeration, scratchpad]
- Serves: goal 1 (every legacy leaves something to do).
- Revisit if: T-11-LEGACY shows trouble results dominating rich lives.

### DL-11-26: Successors: three from the story by a source ladder, each with a tie and a thorn, plus a newcomer; eight bounded inheritance channels
- Decision: sources protégé/heir/trainee → ally → bond → rescued → rival's child; tie and thorn read from records; channels: renown share (score 1, or 2), one heirloom, ledger results, ≤ 3 trained tags, the predecessor as NPC, standing moved one step toward 0, the home holding, a purse ≤ 350; nothing of power.
- Alternatives considered: random heirs (Rogue Legacy; disconnected from the story); full family simulation (Pendragon's background bookkeeping).
- Evidence: [R6 D-02, D-03, D-10, D-13, D-R4, D-R5] [02.2.7] [16.16]
- Serves: goal 1 (the successor belongs to the world); Principle VI.
- Revisit if: T-11-LEGACY shows fewer than two of three candidates drawn from sources 1–3.

### DL-11-27: The world sims run 11.3.7's agenda exactly; override (c) needs a due aid or a d6 of 1
- Decision: [revision: I-032] `11-world-sim.py` now selects every faction action by 11.3.7 cell for cell (`choose_action()`: overrides (a) slip, (b) war on a d6 of 1–3, (c) `aid_pc`; each temperament row with its own condition; a failed condition reads as `goal`; strike/scheme/court targets by the ladders), and models `court`, `aid_pc`, `lie_low`, a discovered `scheme` and `recover`'s DC per 11.3.6. `13-world-sim.py` no longer patches the steadfast row. The exact run exposed a rules defect: `aid_pc`'s last result (an opportunity bang) is always eligible, so override (c) as written made every faction at status +2 or better spend every turn aiding the PC (20.5% of all faction turns in the engaged run; that faction never worked its goal). 11.3.7 (c), PR-11-2 and `factions.yaml#agenda.overrides` now read: status ≥ +2 and either one of `aid_pc`'s first three results is due (a ransom, a threat bang naming the PC's holding, a reward owed) or a d6 shows 1 (the opportunity bang).
- Alternatives considered: dropping (c) and leaving `aid_pc` to the steadfast row (rejected: a Devoted faction would never pay a due ransom); (c) on a d6 of 1–3 like war (rejected: a friendly faction would then give up half its turns, which no other contract row asks for).
- Evidence: T-11-24 re-run (300 seeds × 104 weeks, byte-reproducible): goals 15 per region per two years (13 / 15 / 18), about 2 per faction per year (target 1.5–3.5); 67–70% of faction turns go to goals; `aid_pc` 3%; mean tier 1.75 → 2.37; tier 5 in 0%. The Thallen re-run: 1.81–2.05 goals per faction per year; 8 entanglements in two years for a PC at war.
- Kept, with the evidence: war is decisive. Under override (b) two tier-1 neighbours at relation −3 strike each other on half their turns, and the sim's Ember Cult collapses at a median week 10–12 (p90 35–44); 11.3.9's vacuum refills the map. This is the rule's intent ("war is news in both seats", 11.3.14); a seed never starts a pair at −3 (12.16.10 starts the threat at −2 to its foes), and 11.3.14's cooling returns a quiet war to −2.
- Serves: P-world (a world that moves by rule, not by the DM's inclination); goal 2.
- Revisit if: playtests show wars between small factions ending before the PC can take a side (then cap override (b) at d6 1–2 or make a faction's first hold loss in a season absorb the second).

### DL-11-28: Train-a-Successor banks three different tags (revision I-087 (b))
- Decision: 11.13.10: each 4-tick stretch banks the tag taught most among those not yet banked (none if only banked tags were taught); at most three, each different. 02.2.7 item 4, 03.2.8 and `legacy.yaml#train_successor` say the same.
- Alternatives considered: cap one tag at 24 points (the same result stated as a cap; "distinct" is one word in three places and needs no arithmetic); allow repeats (rejected: three events at one node is 72 points, nearly tier 1's 80, a recognition bought in downtime).
- Evidence: verification-2c long-arc playtest (I-087 (b)); 03.2.8's 24 points is one median session at a focus node, so one tag is one session's head start, as backstory is meant to be.
- Serves: goal 1 (identity from play); 02.11.1 (backstory only as a deed done in play).
- Revisit if: successors in play arrive with no banked tag because teachers rotate tags too slowly (then bank per 4 ticks across the whole clock).

## DL-12 — DM Procedures

### DL-12-01: The turn loop is two passes — adjudicate (state) then narrate — with a claim-by-claim check before delivery, as a rule of play
- Decision: PR-12-1's twelve steps: T1–T6 produce an adjudication record and all state writes before any prose (12.2.8); T7–T10 draft, write-on-mention, `check_claims`, and screen (fidelity, P16, safety, agency, no mechanics in fiction); T11–T12 deliver and log. No separate judge model is adopted; the check is the DM's own procedure run against the store with a tool.
- Alternatives considered: (a) one generation that adjudicates and narrates (the probe's architecture) — rejected: "seduced by the narrative", 120× leniency bias, narrated-not-recorded changes (R4 W2, W9); (b) a separate judge/gate model — not adopted: constitution III defaults to base-model judgment until sustained play records a concrete failure; 12.12.4 defines how such evidence is collected; (c) self-assessment ("did I make mistakes?") — rejected: the project's own probe self-assessed clean while carrying an unearned pronoun (C:P13).
- Evidence: [R4 §8, R-07]; [R1 #2, 12.D, T-1] (−64.78% critical hallucinations from a verify step; NCP two-stage audit); [R2 ch.12]; [C:III]; [C:P13]; https://arxiv.org/abs/2502.19519; https://github.com/ZDOSt/Story-Engine.
- Serves: goal 2 (state truth), goal 1 (fidelity check), C:I, C:III, C:P13.
- Revisit if: T-12-CLAIM shows < 95% catch of planted errors, or the review list produces a Principle III candidate.

### DL-12-02: The packet — core + at most 12 cards + narrator view + the message verbatim + 4 verbatim exchanges
- Decision: 12.2.4; `pacing.yaml#packet`. Older context reaches the DM only through state (chronicle, threads, journal, scene header); a summary is never summarized.
- Alternatives considered: whole-history context (drift within ~8 rounds; distractor effect); summarizing memory (HiAgent: commitment conflicts 26% → 4% but player-input conflicts 13% → 38%); windows of 2 (loses the immediate thread: the pronoun just used, the offer just made) and 8 (approaches the drift horizon).
- Evidence: [R4 W12, W13]; [R1 12.D, #15]; https://arxiv.org/abs/2402.10962; https://arxiv.org/abs/2505.06120; https://arxiv.org/abs/2412.08972.
- Serves: goal 2.
- Revisit if: T-12-WINDOW (OEQ-12-1).

### DL-12-03: Claim verdicts are asymmetric; two redrafts, then a plain fallback
- Decision: 12.3.2: a `new_element` (ordinary furniture) may be written to the store; an `unsourced_change` never is — a change needs a resolved source. After two redrafts, deliver the plain fallback (true and dull) with `review_flag`.
- Alternatives considered: writing state to match prose (turns every narration slip into a world change; INV-1 forbids it); unlimited redrafts (no termination); dropping the turn (stalls play).
- Evidence: [00.6.6; INV-1, INV-2]; [R1 T-14] (tool state wins; latest wins only among writes); [R4 W8, W9].
- Serves: goal 2.
- Revisit if: the plain fallback exceeds 2% of live turns (T-12-CLAIM).

### DL-12-04: Error correction — state wins except for a record error; OOF note by default; rewind only within the scene; make whole only for spent quantities
- Decision: PR-12-4 / 12.3.4–12.3.6. Record errors are repaired by a corrective write citing the resolved source; narration errors leave the store alone. In-fiction reconciliation only when it adds no fact. Reliance: keep / accept forward / rewind inside the current scene; before it, correct forward and refund quantities spent because of the falsehood. Correct, never compensate.
- Alternatives considered: always rewind (destroys play history and invites fishing); never rewind (punishes the player for the DM's error); compensation beyond refunds (turns DM errors into rewards, an exploit); in-fiction-only reconciliation (smuggles convenient facts).
- Evidence: [R1 G-3, #2] (no procedure in any source; errors expected within ~20–30 turns: 42% survival@20 for the best model); NarrativeEngine rollback practice (R1 G-3 target).
- Serves: goal 2, goal 1 (fairness, locus of control).
- Revisit if: playtest corrections show players rewinding to fish for rolls, or reliance disputes recur (review list).

### DL-12-05: Narration may create only ordinary furniture by mention
- Decision: 12.14.13: clues, valuable items, hazards, adversaries and people with wants or secrets come only from their owning procedures; uncertain → treat as a clue and cut.
- Alternatives considered: unrestricted write-on-mention (lets prose manufacture clues and loot, bypassing the clue graph and the generator — the "DM decides what's behind the door" failure in a new form).
- Evidence: [R4 W8] (Intra's door problem); [R5 P-41] (clues come from clue graphs); [00.11.1].
- Serves: goal 2; fairness of mysteries.
- Revisit if: playtests show furniture judged a clue so often that scenes feel bare (log the cut elements).

### DL-12-06: Scene test deviates on d10 ≤ tension − 3 (not Mythic's d10 ≤ Chaos)
- Decision: 12.4.4; T-12-9: 0% at T 1–3, 20% at the default T 5, 60% at T 9.
- Alternatives considered: Mythic's rate (50% at the default) — rejected: in Mythic the scene test and random events are the world's only motion; here clocks, watch/interval checks, the World Turn and NPC wants already move the world, so a 50% deviation rate would bury the player's plans; no test at all — rejected: a world that always cooperates with the plan is the exact solo failure Mythic solves.
- Evidence: [R5 P-05, P-01]; [R6 B-16]; exhaustive table `pace12.py`.
- Serves: goal 1 (the player's plan usually happens), C:P16 / liveliness.
- Revisit if: T-12-SCENE (OEQ-12-4).

### DL-12-07: Tension 1–9 from state; the Oracle shift applies only to questions with an eventful answer, never to the player's G0 questions
- Decision: 12.6.3–12.6.4. Chaos and control points are computed from the scene log; the only judgment is the PC's hoped answer to the agenda. Tension shifts the odds one rung toward the eventful answer at T ≥ 7 and away at T ≤ 3, only among Likely…Remote; triggers random events on Oracle doubles with digit ≤ T; sets the scene test. It never touches DCs, frames, costs or the player's own questions.
- Alternatives considered: Mythic's "Chaos makes yes more likely" (yes is not always more chaotic: "is the bridge standing?"); shifting every question (lets tension move a player's search for a rope — a hidden adjustment of the player's odds); DM-felt control/chaos (judgment where state suffices).
- Evidence: [R5 P-01, P-02]; [00.12.7] (≤ 1 rung); [01.15.2]; [R1 #9] (no hidden adjustments).
- Serves: goal 2 (fair odds for the player), liveliness.
- Revisit if: T-12-EVENTFUL agreement < 85%.

### DL-12-08: Random events — an original focus table weighted for a faction sandbox, with hard bounds
- Decision: `tbl.event_focus` (d100): NPC action 16%, faction move 10%, thread advances 10%, PC complication 8%, PC opportunity 8%, current context 8%, remote 8%, new NPC 6%, thread complicates 6%, rumor 6%, omen 6%, ambiguous 6%, thread resolves off-screen 2%. Events never harm, cost, kill, grant, or reveal sealed facts; a thread vowed or progressed within 12 scenes cannot resolve off-screen.
- Alternatives considered: Mythic 1e's table as is (no factions or rumors; "close a thread" at 3% is too punishing in a sandbox where the player owns threads).
- Evidence: [R5 P-11]; [R6 B-16, B-20] (traces the player can perceive).
- Serves: goal 1 (the player's threads are protected), liveliness.
- Revisit if: T-12-EVENT (OEQ-12-10).

### DL-12-09: The pacing director — intensity = min(10, max(scene points, previous − 3)); BUILD / PEAK / RELAX; three profiles; it governs only its own pushes
- Decision: 12.7; standard profile peak 7, relax 2 scenes, flatline push after 3 flat scenes, recovery 3 scenes after a setback; gentle 6/3/4/4; relentless 8/1/2/2. Escalation after a 3-scene easy streak changes the kind of challenge, never numbers.
- Alternatives considered: no director (P16 only) — leaves the "flatline / pile-on" problem to DM feel; a director that suppresses other chapters' encounter checks — rejected: hidden adjustment and cross-chapter interference; per-round L4D timings — translated to scenes because text play has no real-time.
- Evidence: [R6 B-10, B-11, B-18, B-19, B-R3]; https://steamcdn-a.akamaihd.net/apps/valve/2009/ai_systems_of_l4d_mike_booth.pdf; https://rimworldwiki.com/wiki/AI_Storytellers; [R1 #9, T-5]. Arithmetic: one Dire failure with an S3 cost in a conflict = 6; with a lethal declaration or Staggered ≥ 7 → PEAK means "a fight that genuinely threatened the PC"; a 10 drains to BUILD territory in three scenes (10 → 7 → 4).
- Serves: goal 1 (breathing room after losses), C:P16.
- Revisit if: T-12-PACE (OEQ-12-3).

### DL-12-10: Starting standing by a 2d6 reaction roll with at most ±2 from cited facts; Devoted never at first sight; faction members ±1 from status
- Decision: 12.11.2; T-12-12. Unaffiliated: ≤2 Hostile, 3–4 Unfriendly, 5–6 Wary, 7–8 Neutral, 9–10 Warm, 11+ Friendly (mean −0.25 at +0). Members: faction status, then 2d6 2–4 −1 / 5–9 0 / 10–12 +1 (16.7/66.7/16.7%).
- Alternatives considered: the DM choosing a "fitting" attitude (constitution-level forbidden: 00.3.16 "rolled, never chosen"); B/X's five-band reaction table (does not map onto the seven-rung standing scale); uniform d7 (no central tendency; too many hostile strangers).
- Evidence: [R6 §B.3 B-R2]; [R5 AV-07]; [R4 W4] (agreeable-NPC bias needs pre-committed state); 00.17.1 Q13; exhaustive enumeration `pace12.py`.
- Serves: goal 2.
- Revisit if: T-12-REACT (OEQ-12-7).

### DL-12-11: Lead injection — content from a seven-rung specificity ladder over existing state, form from a d12 table; threshold 3
- Decision: 12.8.2. The lead always points at something already in state (a clue placement, a fallback, a clock, an NPC want, a rumor, a new hook with ≥ 3 placements); the roll only decides how it arrives; it never solves the thread or costs anything.
- Alternatives considered: rolling the lead's content on a generic table (invents unconnected content; corrupts clue graphs); DM-chosen leads (the probe's failure: it did not happen until the player complained); threshold 2 (fires on ordinary bad luck).
- Evidence: [C:P16]; [R4 R-12]; [R5 P-08, P-41]; [R6 B-R4, B-13, B-19]; probe soft-lock at turns 6–8.
- Serves: goal 1, C:P16.
- Revisit if: T-12-LEAD (OEQ-12-5).

### DL-12-12: Spotlight for one player — a rotation ledger over pillars, nine challenge types and the PC's facets; thresholds 6 / 6 / 8 / 4; used only as tie-break and opportunity
- Decision: 12.9; the player's check-in halves or doubles pillar thresholds; diversification forbids repeating a challenge type for a third consecutive opposition scene when an alternative exists.
- Alternatives considered: no ledger (the DMR's headline: spotlight never falls out of mechanics); forcing overdue content (railroading; violates goal 1); per-session balance (the research warns a session-level metric misfires — balance over the arc).
- Evidence: [R1 12.B, #8, T-15, M-35, M-36]; [R2 ch.12, #12]; [R5 X-01]; DW GM move "give an opportunity that fits a character's abilities" (https://www.dungeonworldsrd.com/gamemastering/).
- Serves: goal 1.
- Revisit if: T-12-ROT (OEQ-12-6).

### DL-12-13: NPCs in three depths (walk-on / recurring / principal); every field rolled and written at once; five active memories per NPC
- Decision: 12.11.1, 12.11.7. Gender and pronouns are rolled at walk-on (the pronoun slip); twelve memory valences with salience 1–3; the most specific relevant memory leads an NPC's first line.
- Alternatives considered: full generation at first mention (wasted state for extras); fields "decided later" (the door problem); unbounded memory (retrieval noise; TYOV's bounded memory is the better pattern).
- Evidence: [R5 NP-01, P-04 (UNE), P-06, P-42]; [R6 B-19] (Hades/Valve); [C:P13]; [R4 W4, W7].
- Serves: goal 2, goal 1 (NPCs who remember make deeds matter).
- Revisit if: T-12-MEM (OEQ-12-9).

### DL-12-14: Session moves as rules of play; adjust changes content, never mechanical weight; check-in every fourth session
- Decision: 12.5. Begin / recap (from state) / end / break / flags / adjust (five re-framings) / rewind (closed list) / check-in.
- Alternatives considered: adjust as a mechanical undo (turns safety into a reroll and corrupts fairness); no check-ins (an AI cannot read a face; R1 recommends asking); check-in every session (nags).
- Evidence: [R5 P-10, SC-01, SC-02, SC-06]; [R1 12.B, G-22, M-34, M-40]; 00.1.5 (safety first).
- Serves: goal 1, player safety.
- Revisit if: playtest players skip the check-in more than half the time (then make it on request only).

### DL-12-15: Original meaning tables (4 × 100, recency 20) and twist rows per severity (d8 × 5) with ch.12-owned clock templates
- Decision: `oracles.yaml` — words authored for this ruleset (not copied from Mythic or Ironsworn, which are copyrighted or carry attribution terms); twist rows: S1 complication, S2 obstacle, S3 threat (band ≤ scene) or a new danger clock with 1 tick, S4 escalation, S5 world reversal — matching 01.13.10 exactly; every created clock uses a template in `pacing.yaml#clock_templates` with omens for every stage (00.8.1).
- Alternatives considered: smaller word lists (d20; repeats within a session — W10 homogenization); reusing published tables (licensing; FN-12); twist rows that harm (01 forbids: harm is `cost.harm`).
- Evidence: [R5 P-04, P-16, FN-12]; [R4 W10]; [R7 §4.3 Twist]; 01.13.10.
- Serves: goal 2 (variety without DM choice), C:VI (all provisional).
- Revisit if: T-00-VARIETY-style counts show a meaning word recurring within 20 draws more than 10% of the time.

### DL-12-16: The anchor index is compiled, never hand-edited; retrieval scores 3 / 2 / 1; seeded with the fifteen verb cards
- Decision: 12.13.6; `anchors.yaml` compiled from `basic_verbs.yaml` (and later from every `Anchor: yes` card and data anchor block) with validation; ids `anc.<rule id>`; the verb tag map assigns deed and situation tags per verb.
- Alternatives considered: a hand-maintained index (drifts from its sources); embedding-only retrieval (not auditable; R1 notes structured stores beat embeddings for changing facts).
- Evidence: [00.15.3]; [R7 §3.4]; [R4 SG-16, SG-18]; [R1 #15].
- Serves: goal 1 (any action finds an anchor), goal 2 (bounded adaptation).
- Revisit if: T-00-ATTR-style tests show the gated verb card is not the chosen anchor in ≥ 90% of plain actions.

### DL-12-17: Narration limits (beat 200, conflict turn 150, scene opening 200, recap 120, skip 150 words) and the freshness rule
- Decision: 12.14.10–12.14.11.
- Alternatives considered: no limits (long prose multiplies claims and repetition; RPGBench interestingness decays through repetition); tighter limits (lose the scene-setting craft).
- Evidence: [R1 12.A]; [R4 W10, W11].
- Serves: goal 2 (fewer claims to get wrong), pacing.
- Revisit if: the owner's playtest asks for longer or shorter prose (a preference, recorded at check-in).

### DL-12-18: Out-of-fiction blocks with fixed labels and order; the pause block always last
- Decision: 12.15; ch.14 owns rendering. The OFFER renders 01.7.1 items 1–7 in order; the Oracle never appears (background); hidden clocks never appear.
- Alternatives considered: free-form OOF commentary (inconsistent; leaks); hiding all numbers (violates P7 and 01.7's visible odds).
- Evidence: [00.1.7]; [R4 §7.3] (visible stakes make refusals legible); [01.7.1].
- Serves: goal 1, goal 2.
- Revisit if: ch.14's usability test finds the OFFER block unreadable.

### DL-12-19: Principle III candidates — three overturned flagged records of one error class across two sessions
- Decision: 12.12.4; also rule candidates after three reuses of a precedent (12.12.6).
- Alternatives considered: any single flagged record (one case is noise); never reporting (III's trigger would never be observable).
- Evidence: [C:III] ("record it before proposing the amendment"); [R4 SG-20]; [R7 §4.8].
- Serves: C:III, C:VI.
- Revisit if: the review list grows faster than maintainers can read it (raise to five).

### DL-12-20: A closed list of nine pause points with defaults when the player moves on
- Decision: 12.2.6; `pacing.yaml#pause_points`.
- Alternatives considered: pausing whenever the DM is unsure (re-introduces DM judgment and slows play); never pausing (auto-resolves player choices — locus of control).
- Evidence: [01.7.1, 01.9.3, 01.10.3]; [R4 §7.3]; https://arxiv.org/abs/2502.19519.
- Serves: goal 1.
- Revisit if: playtest logs show a pause point left unanswered more than 20% of the time (its default may need to change).

### DL-12-21: The world seed: a session-zero procedure that writes a whole starting region, so no setting is required
- Decision: [revision: I-028] 12.16 and PR-12-9 build the starting world in fourteen steps (premise, canon, faith, peoples and tongues, land, haven, factions, cast, sites, encounter tables, rumors, calendar, opening and pregens, the seed check) from `data/world_seed.yaml`'s questions and oracle tables, reusing every generator the rules already had (PR-11-8 and 11.3.18 for factions, PR-10-6 for sites, 12.11.1 for people, `world_turn.yaml`'s situation templates and rumor truth, T-10-2's rings, 02's creation defaults for pregens) and one new one (PR-10-10 for tables). Its output is a region record of the `region_*.yaml` shape, so every chapter reads a seed exactly as it read chapter 13's region; chapter 13's Thallen Vale is re-framed as one optional pre-made seed, and 220 references across the chapters that treated chapter 13 as required now name the region's seed. It lives in ch.12 because it is a DM procedure run at session zero (12.5.1), and it orchestrates 10's, 11's and 02's procedures rather than owning their content.
- Alternatives considered: a short "truths" list only (Ironsworn's) — rejected: the rules read 62 distinct things from a region (T-12-16), from teachers and sentry floors to org-tie maps and the second tongue, and a list of truths supplies none of them mechanically; generating the world lazily, on first need — rejected: chapter 02 reads peoples, tongues, keepers and names before the first scene, and the opening needs factions already in motion and three leads; keeping chapter 13 as the default — rejected by the owner (FINISH-PLAN, 2026-10-05).
- Evidence: `_process/simulation/12-world-seed.py` (deterministic): seed 1 and a guided run pass 62 of 62 checks; 200 further oracle seeds pass every check; 2,600 regional tables built and all pass PR-10-8. The requirement list is built from every chapter's "To 13" requests (77 answered in `region_thallen.yaml#interface_checklist`) and every rule that reads region data (a grep of all chapters: 220 lines). [R5 P-22..P-36] [R: https://www.ironswornrpg.com/ (truths)] [R6 B-12, B-15, B-20].
- Serves: goal 1 (a player can start in a world they shaped, or one that surprises them), goal 2 (everything a setting supplies is state, written by procedure, never improvised in narration).
- Revisit if: T-12-SEED (OEQ-12-11) finds more than three setting gaps a session in a seeded world.

### DL-12-22: Every seed question has closed options and an oracle; a custom answer is classified, its words kept as description
- Decision: [revision: I-028] 12.16.2: guided, oracle or mixed mode per question; a player's own words are classified `[J:enum]` to the nearest option (the only judgment in the procedure) and kept as the entity's description, never as a mechanic; one veto per step in oracle mode.
- Alternatives considered: free-text answers parsed into data (rejected: an open judgment per answer, the leniency failure R4 measured); oracle only (rejected: goal 1 — the player should be able to shape their world).
- Evidence: [R4 §3.2 S1 (closed-set classification is the AI's reliable form)]; the guided run in `12-world-seed.py` (fourteen player answers, one a classified custom answer) passes every check.
- Serves: goal 1, goal 2.
- Revisit if: players report the options too coarse for the worlds they want (then add options, never free text).

### DL-12-23: The seed writes the world at the depth play starts with; deeper content is generated on demand by its owner
- Decision: [revision: I-028] 12.16.18 and `world_seed.yaml#defaults.uses_generic`: the seed writes 13 areas, about 11 sites, 4 full factions, about 17 NPCs and the haven in full, and leaves events, hooks, season events, NPC tables beyond names, omens, chase ground, hire quirks, cases, storied items, regional afflictions and setting origins to the generic tables or their owners' on-demand rules, each named in the seed record. A new region past ring 5 re-runs steps 5, 9, 10 and 11.
- Alternatives considered: authoring regional versions of every generic table per seed (rejected: no rule needs them, and each would need its own audit); a deeper seed (more settlements, more NPCs) (rejected: write-on-mention already covers them, and a larger seed costs context the DM must carry).
- Evidence: T-12-16 marks 11 requirements `generic_or_table`; all 62 pass on 201 seeds.
- Serves: goal 2 (proportional state), goal 1.
- Revisit if: playtests show a generic table breaking a region's tone (then the seed writes that table).

### DL-12-24: The seed check defines what a setting must supply, and every setting (generated or pre-made) must pass it
- Decision: [revision: I-028] 12.16.17: `world_seed.yaml#requirements` (T-12-16) is the single list of what the rules read from a region, each with the seed key and a mechanical check; a generated seed re-runs the failing step; a pre-made seed (chapter 13's, or any) must pass the same check.
- Alternatives considered: trusting each chapter's interface requests (rejected: they were addressed to chapter 13 and never checked against a generated world); a checklist in prose (rejected: unenforceable).
- Evidence: `12-world-seed.py` implements every check; 62 of 62 pass on the committed example.
- Serves: goal 2 (AI correctness: no rule reads a key that can be missing).
- Revisit if: a chapter adds a region read (then add its requirement and re-run the script).

### DL-12-25: Claim class `action`, and the review of every later chapter's "To 12" note
- Decision: [revision: I-030] 12.3.1 gains a fourteenth claim class, `action` (a non-player entity's act), checked against the act's closed source in the turn's adjudication record (12.2.9; for an ally, 16.13.3's six reasons); an act with no source takes the existing verdict `unsourced_change`, so no new verdict is needed. `pacing.yaml#claim_check.classes` lists it. Every "To 12" note in chapters 01–11, 15 and 16 was checked against chapter 12, item by item (66 items). Applied: `action`; owed `[WARNING]`/`[STATUS]` blocks fail the claim check and survive the plain fallback (07); `harm_condition` checks a narrated death against `harm_state.dead` (07); `position` checks T-06-4's flag words (06); PR-06-6 named as 12.2.9's enemy-turn step (06); T-12-3 cites 06.2.1 and 06.13.1 and lists 06.13.1's four end conditions (06); a `[CONFLICT]` status line row in 12.15.15 for windups, bands, flags and a sensed morale clock (06: the "status line" 06.9.5 and WE-06-8 cite had no format); ability prices (Focus, uses, flare, overdraw) and the relic surcharge on the OFFER's Costs line (05 c, 08); one-line drops in RESULT (08); held abilities' cards in the packet with their rank text verbatim (05 a); ch.09's eight challenge axes kept by the rotation ledger (09.8.5 said 12.9.2 keeps them; it did not); T-09-13 cited for band tells (09); the reason-to-lie flag in 12.11.5 (15); T-15-2 cited in 12.11.6 (15); the V face cited in 12.6.5 (10); any ally's death is a setback and an open personal thread is a lead-injection source (16 c, e); the stale field name `reaction` corrected to `reaction_roll` in 12's own "To 09" note.
- Not applied, and why: 01's six items, 02's, 03's T6/`scene_end`/disputes, 04's, 09's `reaction_roll` and `threat_advisory`, 10's `[JOURNEY]` and skip narration, 11's five and 15's `kind`/lead-audit items were already in force (registered integration items, or written into 12 before the note). 03's reflection sweep is 03's own handler at `reflection`, returned through 12.2.3 item 8, and "narration never mentions recording" is T-12-1's T10 ("no numbers or rules words in the fiction"). 03's `last_exercised` is offered, not required: the rotation ledger counts facets its own way (12.9.1). 05 (b) needs nothing: `roll_table` rolls any registered table. 05 (d), 07's and 10's anchors are compiled by `12-compile_anchors.py` (I-031). 07's "triggers are returned by `get_active_triggers`" is 12.2.3 item 3. 08's "generation log available" is 08's visibility, which 12.15.1 already honours. 10's time-tick die is a boundary handler, 01.11.3 source (5). 15's clue delivery (12.10.4), principal depth and walk-on promotion on a Talk target (12.11.1) were already 12's rules. 16 (a) facets and (d) memories were adopted as written; banter's budget (16.13.4) is loaded with the ally card.
- Alternatives considered: re-wording 16.13.3 to an existing class (rejected: `outcome` is about the PC's frames and `attitude` about standing; no class covered a non-player act, so NPC acts with no source were also unchecked); a new verdict `unsourced_action` (rejected: `unsourced_change` already means "no write or source this turn", and its fix, cut it, is the right one).
- Evidence: the 66-item review is listed in `_process/reports/revision-B-report.md` (step 4); validator 0 ERROR / 0 WARN.
- Serves: goal 2 (AI correctness: an NPC or ally acting from nowhere is now a checkable claim); P13.
- Revisit if: a playtest log shows `action` claims flagged on ordinary scene furniture (a crowd moving), which would call for an exemption like `new_element`'s scene-furniture rule.

### DL-12-26: Every anchor card states its knobs and intent verbs in compiler terms; the anchor compile is warning-free
- Decision: [revision: I-031] the 13 compile warnings are cleared at their sources, not suppressed. Cards with no T-00-20 knob now name them, fixed where nothing may change: 02.9.4 (`stakes` Safe and `targets` the character's own past, both fixed: the two flags decide), 06.5.4 (`targets`, `reach_unit`, `condition`), 06.5.10 (the seven knobs its Computation line already allowed, at most two per frame), 08.6.7 (`dc`, `time_cost`), 09.2.4 (`targets`, `time_cost` none: the two enums decide). 08.6.4, 08.6.7 and 08.6.8 gained intent verbs ("make, forge, brew…", "repair, mend…", "salvage, break it down…") instead of the compiler's title fallback. T-06-9 rows 20, 24, 33, 35 and 39 name a basic verb first: Move (across difficult ground; `action_cost` +1 per Move), Strike called at the held object, Evade as Defend, Evade resisted, Evade as Full defense (06.1.5 defines Defend as a named use of `verb.evade`). The compiler now collapses wrapped card text inside knob defaults (four anchors' defaults lost their embedded runs of spaces; no value changed otherwise).
- Alternatives considered: teaching the compiler to accept "none" as a knob list (rejected: retrieval scores knobs, and a card with none could not be adapted, 00.2.7); mapping Defend to a sixteenth verb (rejected: 06.1.5 says it is Evade).
- Evidence: `12-compile_anchors.py`: 129 anchors, 0 errors, 0 warnings (was 13 warnings).
- Serves: goal 2 (AI correctness: every anchor the DM retrieves has machine-readable knobs and a basic verb).
- Revisit if: a new anchor card is added without `Intent verbs:` and `Knobs:` (the compiler warns again).

### DL-12-27: A created feature's length and growth are one knob (revision I-062)
- Decision: T-00-20's `duration` is a feature's whole behavior over time (length, growth, spread, fading); where a feature sits is the beat's target, not a knob (T-00-20, 01.5.3, 12.13.3 with the doorway-fire example).
- Alternatives considered: a new `behavior` knob (rejected: every anchor card and the compile's closed list would change for no gain).
- Evidence: verification-1 playtest (the fire barrier split three ways); `anchors.yaml` knob lists read by script (`anc.06_t9_31` lists only `reach_unit`; `anc.10_12_9` carries `duration`).
- Serves: goal 2.

### DL-12-28: Want and refusal rolls must fit (revision I-053)
- Decision: `tbl.npc_want_verb` rows carry `takes` (object rows they govern); a misfit verb steps down the table, wrapping; four objects reworded ("a debt", "an old enemy", "a rival", "a child"); `tbl.npc_refusal` row 12 is `not_for: [deed.martial]`, same stepping (12.11.1). Applied at the generic tables, so runtime NPCs and seeds both benefit.
- Alternatives considered: constraining only `world_seed.yaml` (the ledger default; rejected: 12.11.1 rolls the generic tables in live play); rerolling (rejected: stepping is deterministic and still rolled).
- Evidence: seed 1's cast reads sensibly; `12-world-seed.py` seed check `npcs` asserts every want fits and no martial NPC holds `refusal.fight`.
- Serves: goal 1 (a first session's NPCs make sense), goal 2.

### DL-12-29: Seed NPCs carry competence and licenses (revision I-059)
- Decision: 12.16.11: every cast NPC has `competence` (role tags at its band's c_b, T-09-2) and `licenses` (level-2 role tags' training licenses at trained; teacher targets at expert); the seed check fails a teacher whose record does not hold its target.
- Evidence: `12-world-seed.py` PASS; ch.13's pre-made region (unmaintained) lacks these fields (I-088, wontfix).
- Serves: goal 2 (15.11.1's MENTOR test reads a record).

### DL-12-30: A reference rate of world time per session, for calibration (revision I-085)
- Decision: 12.7.7 and `pacing.yaml#world_time`: adventures of 2–4 sessions at 2–10 days a session, 1–6 weeks of downtime after each, an optional season a year: about two world weeks a session; a calibration and review target, never a constraint; a review flag when a season takes outside 3–10 sessions twice running. Aging is a long-campaign rule by design (11.10.5).
- Evidence: `12-time-pacing.py` (seed 85, joins `04-recog04.py` and `11-world-sim.py`): 1.94 / 2.37 weeks a session; tier 5 at 2.1 / 2.6 years (archer); 2.3–2.8 sessions a thread against the world sim's thread rate; aging only for PCs who start old (about three checks in 60 sessions).
- Serves: goal 2 (the season- and week-paced rules are calibrated against something stated).
- Revisit if: owner playtests log sessions per season outside 3–10.

### DL-12-31: The world seed writes the powers of the far rings (revision I-083)
- Decision: 12.16.11 step (the cast) writes one principal per ring-4 area at band 4 and per ring-5 area at band 5 from `tbl.12.seed.powers` (d8, a used row stepping down), each with a sealed `keeps` truth; `ws.req.04_powers` checks it; 12.16.18's new region writes its own powers at band 5. 12.16.18's chapter-13 sentence now gives the script's real count (54 of 63) instead of the stale "58 of 62".
- Alternatives considered: put the powers in the lairs (rejected: a lair's master is a fight, and a power must be a party a contest can face); one power per region (rejected: tier 5 needs two band-5 oppositions under DL-04-31).
- Evidence: `12-world-seed-output.txt` (PASS, 63/63; seed 1's powers listed in WE-12-11 step 8); `04-recog-parity-output.txt` (I-083 section).
- Serves: goal 1; 12.16's promise that a seed is as playable as a hand-made setting at every tier.
- Revisit if: a pre-made region is maintained again (it must add its own powers).

### DL-12-32: A generated NPC carries a band: 1, or its home area's band as a principal (revision I-089)
- Decision: 12.11.1 writes `band` on every generated NPC: 1 at walk-on and recurring depth; on promotion to principal, the `band` of its home's area (12.16.8), never lowered; a record that already carries a band (an adversary line's threat band, an ally's own band, a seeded record) keeps the higher. A faction's tier is never written into it (03.4.3 lends it only to a binding party on the faction's matter). 00's NPC schema gains `band`.
- Alternatives considered: band 1 for every on-demand NPC (the gap I-089 logged: a principal met in the far rings would be band 1 in a contest, and 12.16.11's seeded powers would be the only high-band social opposition); band from the role or the faction's tier (rejected: role bands are not authored, and the faction tier is I-039's binding-party question, already answered); the DM's judgement (rejected: 03.4.3 requires the band be engine-read, never chosen).
- Evidence: 03.4.3 reads "the `band` its NPC record holds"; 12.16.8's areas carry `band` by ring; `12-world-seed.py` writes cast bands 1–2 for haven trades and 4/5 for the far rings' powers, which the rule reproduces for an on-demand principal in those areas.
- Serves: goal 2 (no band is chosen); goal 1 (a social calling's opposition grows with the world it travels in).
- Revisit if: live play shows principals in far-ring areas making band-4/5 contests too common (then require principal depth and a thread role, or count them as one opposition per area).

## DL-13 — The Starter Setting: the Thallen March

### DL-13-01: One fictional engine — "true sound holds back the Quiet" — expressed only through existing mechanics
- Decision: the region's central idea (a silence that stills people and spirits, pushed back by bells cast with a rare metal) is built entirely from other chapters' primitives: the Hush is two hazards in `hazards.yaml`'s owner-block applying 06's `cond.silenced` and `cond.deafened` plus 07's dread exposure; a true bell is an ordinary item with the fact `true_bell` named in the hazards' `protections`; the Quiet is two linked clocks; the Woken are an upbringing; the Stilled are NPCs with a fact. One region-only rule (the Waking rule, 13.2.4) is `[D]` with one `[J:flag]`.
- Alternatives considered: (a) a bespoke "Hush meter" on the PC (a second resource the codex and the DM must track; violates 00.17's one-currency spirit); (b) a curse-like affliction for the Hush (07 has no 13 owner-block for afflictions); (c) a generic dark-lord setting (needs no new idea, but gives the newcomer nothing to reason from).
- Evidence: 05.7.2 (arcane and divine need speech, primal needs the source present — the Hush interacts with all three for free); 10.12.8 (magical zones are hazards); 00.12.7 (canon facts settle the Oracle).
- Serves: goal 1 (one idea the player can reason from: "if I ring the bell, the hounds flinch"; "magic that needs words fails where sound fails"), goal 2 (the DM rules from data, never inventing a rule).
- Revisit if: T-13-OPEN shows newcomers do not grasp the idea by the end of session 1 (then the pitch gets a sixth line).

### DL-13-02: West Marches kept exactly; rings computed, not asserted
- Decision: T-10-2's rings and words unchanged; every settlement, site and landmark's ring is checked by the generator as the shortest *known* route in watches from Tolling (1 day = 2 watches, 10.3.5) against T-10-2's bounds; areas carry the ring's band and danger and a table of that home band. The secret causeway (19 watches to Sael, ring 4 by distance) is excluded until found, which is exactly the fiction's reason Pell hides it.
- Alternatives considered: rings by hand (drifts as routes change); one area per ring (too coarse for the place graph).
- Evidence: 10.2.4; R6 B-15, B-R7; generator report (all 34 ringed places pass).
- Serves: goal 2 (distance is the dial and the dial is checked).
- Revisit if: a route is added (regenerate; the check runs).

### DL-13-03: Four full factions, fifteen petty; the Choir full from the first scene
- Decision: full at the start: House Vantry (t3), the Bellwardens (t2), Pell & Daughters (t2), the Hushed Choir (t1, full because the opening case names it, 11.3.2). Fifteen petty factions cover every org kind any origin names and every deed branch's institutions; they become full by 11.3.2 when met. Relations at −2 (Vantry↔Wakeful, Vantry↔Pell, Choir→Bellwardens, Pell↔Hemrats, Gorrund↔Ruvag) drive 11.3.7's agenda.
- Alternatives considered: six full factions (the cap; more World Turn load than a newcomer's world needs on day 1); three (no triangle plus an inside threat).
- Evidence: 13-world-sim.py (11's run() verbatim with these factions, 300 seeds × 104 weeks): 2.57–2.71 goal completions per full faction per year (target 1.5–3.5); tier-5 share after two years 10.0–10.4% verbatim, **0%** with 11.3.4's tier rule applied (the verbatim sim's `gain_hold` ignores it; interface request to 11); no collapses; Choir completes its goal at median week 11.
- Serves: goal 2 (every faction conforms to 11.3.1, checked: tier, hold, ratings 0..tier+2 summing to 4 + 2 × tier, goal scope by tier, clock sizes, four sealed fates per linchpin, effect ids).
- Revisit if: T-11-GOALS in real play shows the Choir firing before newcomers engage (OEQ-13-2).

### DL-13-04: The opening is an incident with a public clock, not a quest line
- Decision: the session opens in medias res at the Last Bell's missed stroke; Harrowby's silent bell and stilled villagers are a running situation with a public 6-segment countdown (a day); four independent ways to wake them; every teaching beat is an opportunity in any order; the player may ignore all of it.
- Alternatives considered: a tutorial dungeon (railroads the newcomer); a quiet market-day start (12.4.3's strong-start rule forbids it); a hidden countdown (a newcomer cannot weigh what they cannot see).
- Evidence: R5 P-37 (Blades' starting situation), P-40 (Ironsworn two-vow start), §4 onboarding (play before rules, one subsystem per scene, one out-of-fiction line the first time); 12.4.3; 12.8 (P16 leads).
- Serves: goal 1 (choice from the first word), goal 2 (every lead is data).
- Revisit if: T-13-OPEN fails.

### DL-13-05: The Waking rule — fresh (Certain), set (Remote, once a season), the Mother Bell (all)
- Decision: a Stilled wakes at once to a true bell within a day; after that it is set and wakes only to a watch of true sound or the spring ebb at Oracle Remote (10%), once per Stilled per season, or to the Mother Bell rung whole.
- Alternatives considered: set Stilled never wake (removes player agency over Jonquil Pell and the true Orsolin); always wake to a true bell (makes the Hem trivial to "solve" with one bell; the Mother Bell arc loses its point).
- Evidence: 00.12.7 (Oracle rungs: Remote yes on 91+); 13.1.5 truth T2 lets the player choose Likely or Impossible.
- Serves: goal 1 (a real, repeatable try), goal 2 (no judgment beyond "over them").
- Revisit if: OEQ-13-3.

### DL-13-06: No regional afflictions; the Hush uses conditions and dread
- Decision: 07 asked for regional afflictions "if 00 grants an owner-block"; 00 does not (T-00-19), so the Hush is hazards + conditions + dread + the stilling-as-defeat rule.
- Alternatives considered: a contrib afflictions file (not allowed by T-00-19).
- Evidence: T-00-19; 07.11.2.
- Serves: goal 2.
- Revisit if: 00 grants 13 an `afflictions.yaml` block.

### DL-13-07: Two setting origins: Woken of Orrow (upbringing), Salvager (livelihood)
- Decision: add the setting's two most characteristic lives; both pass PR-02-9 in the generator; the Woken spend exactly three units (Focus 4, letters, Orrowan accented), destitute; `peoples` limits the Woken to peoples who lived in Orrow.
- Alternatives considered: a Woken *people* (a Woken is a human with a history, not a people); Orrowan at native (02.4.4's budget prices only accented tongues).
- Evidence: 02.4.4, 02.4.8, PR-02-9; R5 P-39 (creation writes the world).
- Serves: goal 1 (the setting is playable from inside), goal 2 (audited).
- Revisit if: the Woken are overpicked (a sign the hook is strong, not a problem).

### DL-13-08: Orrowan is a new tongue; the Old Tongue becomes the Deep Tongue
- Decision: 02's Old Tongue is "dead, at most accented", so the Woken's living language is a new license `lic.lang.orrowan` (owner-block of `licenses.yaml`), the region's second tongue; the Old Tongue keeps its id and is renamed in narration only.
- Alternatives considered: renaming the Old Tongue (would make it living, against 02.4.6).
- Evidence: 02.4.6 ("Chapter 13 owns the tongues of its region and may rename or add").
- Serves: goal 2.
- Revisit if: never.

### DL-13-09: The four `none` hybrid pairs hold in this setting
- Decision: affirm all four (wilds × arcane, arcane × primal, divine × primal, primal × influence) with in-world reasons; author no divine × primal hybrid.
- Alternatives considered: author a divine × primal "Bell-singer" (would need 04's files, which have no 13 owner-block, and would blur the setting's line between named keepers and the nameless Quiet).
- Evidence: T-04-3; 13.2.2 (the Quiet is nameless and stills spirits).
- Serves: goal 2 (canon and the hybrid table agree).
- Revisit if: 04 opens an owner-block and the setting grows a nameless keeper.

### DL-13-10: The opening case's opposition clock *is* the Choir's goal clock
- Decision: `clk.thallen.choir_goal` serves both 11 (the faction goal) and 15 (the case's opposition clock); it is ticked only by the faction's World Turn actions and its linchpin fates; its omens name placements.
- Alternatives considered: a separate case clock (two clocks for one event can disagree; 15.9.13's opposition clock would then double-tick the same threat).
- Evidence: 15.9.13; 11.3.6.
- Serves: goal 2 (one source of truth).
- Revisit if: 11 or 15 forbids shared ownership (then the case clock mirrors the faction's by a link).

### DL-13-11: PR-10-8's word computed with the counter held; band-5 minions at the far edge
- Decision: PR-10-8 step 2's advisory word is computed as 09.4.4 calibrates (taken 1, regen 0: the PC holds the counter), with the no-counter word printed beside it; at home band 4 the home + 1 faces use a band-5 *minion* alone (hard), because every band-5 standard is lethal to a P4 reference; at home band 5 the home + 1 faces are band-5 solos.
- Alternatives considered: the no-counter word (would make trolls and wraiths "lethal" at their own band on 10's generic tables too); dropping the home + 1 faces at bands 4–5 (breaks 30/55/15).
- Evidence: 09's own `advisory_alone` uses the counter-held convention; the probe of 29 archetype/band/variant lines (all band-5 standards lethal vs P4; band-5 minions hard; plants and folk mages fair vs P5); generator audit (14 tables, 0 lethal rows).
- Serves: goal 2 (a table the estimator certifies), goal 1 (the far rings still have their legends, as lairs).
- Revisit if: 09 or 10 rules on counters in PR-10-8.

### DL-13-12: 12's gender table kept; no identity override
- Decision: keep 12's even woman/man table; the region's cultures have no rule about it.
- Alternatives considered: a regional distribution (no reason in the fiction).
- Evidence: 12's request ("if the setting wants").
- Serves: goal 2.
- Revisit if: the player asks.

### DL-13-13: Relics count as magic for `refusal.magic` only when seen to work or known
- Decision: 13.3.9 (`[J:flag]`, uncertain → false).
- Alternatives considered: always (an NPC refusing a PC who wears a ring nobody can tell is magic); never (a priest of Merrow happily watching a cursed blade at work).
- Evidence: 15's request; 15.2.3.
- Serves: goal 2.
- Revisit if: disputes arise in play.

### DL-13-14: A curio dealer at Pell's yard in a region with no city
- Decision: d2 property items a week (08's city dealer is d4), scavenged at band 2, list + 2 notches.
- Alternatives considered: no curio dealer anywhere (the salvage economy is the setting's heart; property items would have no buyer short of Esterlow); a full city dealer (inflation).
- Evidence: 08.8.4, 08.8.9 (anti-inflation; half the stock of a city).
- Serves: goal 1.
- Revisit if: T-08's wealth curve runs hot in the March.

### DL-13-15: Five storied items, no sets
- Decision: five rung-6 items with property sets checked against tiers and base kinds; no set (a set needs a composite in 05's file).
- Alternatives considered: a Bell-and-Hammer set (Thallow's Handbell + Clapperfall) — offered to 05 as an interface item.
- Evidence: 08.4.8; T-00-19.
- Serves: goal 2.
- Revisit if: 05 accepts the composite.

### DL-13-16: The Quiet ticks yearly
- Decision: `clk.thallen.quiet_wakes` starts 5/12 and ticks +1 at each Year Turn (+3 if the Last Bell falls), −1 a season in which a great bell is hung or recast; seven years untouched, four if the Last Bell falls; then `quiet_rises` (+2 a Season Turn).
- Alternatives considered: +1 a Season Turn (under two years: a newcomer's campaign would be overrun before it found its feet).
- Evidence: 00.8.1 sizes (12 + 12 for a realm-scale situation); the World Turn re-run's pace of faction goals.
- Serves: goal 1 (a horizon, not a timer).
- Revisit if: long campaigns never see it move.

### DL-13-17: Original names; classic furniture
- Decision: every proper name (Thallen, Orrow, Tolling, the Wend, Sael, the Hush, the Hem, Saint Thallow, Aumbry, Merrow, Weyla, Gorrund, Tinkettle, Ashgorge …) is original to this ruleset; creature kinds are classic and generic; 09's own entry names are not renamed in data (narration may).
- Alternatives considered: borrowing a published setting's map (forbidden by the brief).
- Evidence: the owner's direction (classic fantasy, original setting).
- Serves: the brief.
- Revisit if: a collision with a published name is found (rename in data; regenerate).

## DL-15 — Social, Investigation, and Downtime

### DL-15-01: Standing rungs carry a fixed DC modifier, ceiling and patience (+5/+3/+1/0/−1/−3/−5)
- Decision: T-15-1 binds each standing rung to a social DC modifier (Hostile +5, Unfriendly +3, Wary +1, Neutral 0, Warm −1, Friendly −3, Devoted −5), a request ceiling (none-with-term/R1/R1/R2/R3/R4/R5), patience (0/1/2/3/3/4/unlimited), a price shift and a behavior contract. The numbers make an at-ceiling request DC 11–15 for an ordinary person from Wary up (T-15-3; scratchpad social15.py).
- Alternatives considered: R7 §4.2's five-step attitude DC (hostile +5 … devoted −5) with no ceiling (a lucky roll could get anything from anyone — the leniency failure); standing as levers/snags (would eat the two-lever cap and double count).
- Evidence: [R7 §4.2] [R6 B-02 Blades status contracts] [R4 W4] [R: https://2e.aonprd.com/Rules.aspx?ID=1201] [12.11.2 reaction mean −0.25]
- Serves: goal 2 (consistent NPCs), goal 1 (every rung has a winnable ask).
- Revisit if: T-15-SOCIAL-PLAY shows at-ceiling success outside 50–65% for P1 talkers.

### DL-15-02: Faction members store a personal offset from faction status
- Decision: standing(member) = clamp(status + offset); personal steps recompute the offset; status changes move members together; a positive offset cannot lift a member past the highest source cap their own steps earned (15.1.3).
- Alternatives considered: members fully independent after first meeting (factions stop mattering); members always equal to status ±1 (personal history erased by politics).
- Evidence: [00.17.1 Q13] [R6 B-09 Mount & Blade two-level relations]
- Serves: goal 2.
- Revisit if: playtests show members' standing swinging implausibly with status (then halve status deltas for members with offset ≠ 0).

### DL-15-03: One table maps 12's memory valences to standing steps
- Decision: T-15-2 maps the twelve valences (plus `confessed`) to steps with magnitude conditions and per-source caps; heard-of deeds at most ±1; uncertain magnitude → smaller step.
- Alternatives considered: DM judgment of "how much they'd warm" (unbounded, sycophantic drift).
- Evidence: [12.11.7 request] [R4 W4] [R6 B-19]
- Serves: goal 2.
- Revisit if: T-15-FRIEND shows players perceive standing as unresponsive to deeds.

### DL-15-04: Talk makes acquaintances, gifts make friends, deeds make devotees; +1 per NPC per week from small sources
- Decision: win-over caps at Warm; gifts, Cultivate and `impressed` cap at Friendly; Devoted only from deeds of weight or a bond; small sources give at most +1 per NPC per week.
- Alternatives considered: unlimited talk-driven standing (the slow-drift form of sycophancy); no caps but larger DCs (still a drift, just slower).
- Evidence: [R4 W4 disengagement deficit, agreeable-persona sycophancy] [R5 P-27 Starforged connection ranks]
- Serves: goal 2; goal 1 (friendship remains reachable by play).
- Revisit if: T-15-FRIEND's cultivated NPC takes more than 6 weeks to reach Friendly.

### DL-15-05: Walk-ons are promoted and their wants, fears and refusals rolled BEFORE the first social frame
- Decision: the moment a Talk targets a walk-on, 12's recurring-depth fields are rolled and sealed, then the frame is built.
- Alternatives considered: rolling refusals only when "needed" (the DM would effectively choose whether the NPC refuses after hearing the request).
- Evidence: [R4 §5.2 item 1 seal at creation] [R: https://arxiv.org/abs/2601.06973]
- Serves: goal 2.
- Revisit if: generation cost per scene is too high in live play (then pre-roll at write-on-mention for addressable roles).

### DL-15-06: Refusals are G4 for the intent; 12 generated kinds with explicit inclusions, exclusions and lifts; covers-tie-break true
- Decision: a covered, unlifted refusal is G4 (no roll, term, lever or eloquence passes it); 3 of 12 kinds are absolute; the redirect names the lift or another way.
- Alternatives considered: refusals as large DC penalties (a natural 20 still talks the oath-bound into perjury — the CoC-Seduce failure in a new shape); covers-tie-break false (anti-leniency direction lost).
- Evidence: [12.11.4] [R4 W4] [R: https://arxiv.org/abs/2606.20708] [SG-05]
- Serves: goal 2; goal 1 is kept by the redirect.
- Revisit if: T-15-SOCIAL-PLAY shows refusals hit in more than 25% of social declarations.

### DL-15-07: Patience per scene; walking away at zero
- Decision: patience by standing; failures, G4 refusals/ceilings and insults spend it; at 0 the NPC ends the exchange (S1 closed door, no standing loss); Hostile starts at 0 and hears only parley, Yield, or a request with a term.
- Alternatives considered: let-it-ride alone (blocks only the same request; fishing with variants continues).
- Evidence: [R4 W4] [01.4.2]
- Serves: goal 2.
- Revisit if: T-15-PATIENCE shows walk-aways in more than 15% of exchanges.

### DL-15-08: Social methods are a closed enum with distinguishing tests; default request
- Decision: ten methods (T-15-4), each fixing attribute, defense, defender competence tags, primary tag, standing-in-DC and ceiling; read is an Observe beat.
- Alternatives considered: one generic Talk resolution (cannot tell lies from requests; deception's knowledge consistency needs its own writes).
- Evidence: [01.18.7] [00.4.1 method decides attribute] [R4 §3.2 S1]
- Serves: goal 2.
- Revisit if: T-00-ATTR-style agreement on method is below 90%.

### DL-15-09: Request size is a five-rung ladder keyed to what granting costs THIS person
- Decision: R1 trifle … R5 grave, DC +0/+2/+5/+8/+10, payment price U(S1..S5) Units of the NPC's lifestyle; information sized by what telling costs; higher rung on a tie; never adjusted for phrasing.
- Alternatives considered: no request axis (every ask equally hard: a stranger's lend-me-a-horse equals directions); PF2e's per-NPC influence thresholds (needs authored stat blocks for every NPC).
- Evidence: [R: https://2e.aonprd.com/Rules.aspx?ID=1201] [00.3.11] [SG-02]
- Serves: goal 2 (the rung is the place a seduced judgment would act, and it is bounded at one rung).
- Revisit if: T-15-SEDUCE shows size rungs moving with rhetoric.

### DL-15-10: The social DC adds standing and request size to 00.3.8's opposed defense
- Decision: DC = 10 + attribute + competence + edge + status + standing mod + request mod + mode price; defenses computed fresh. Recorded as an Interface request to 00 (00.3.8 says situational factors never change a DC; these are stored properties of the person and the ask, not situational factors).
- Alternatives considered: standing and size as levers (cap collisions; double counting with real levers).
- Evidence: [01.18.7 delegation to 15] [R7 §4.2] [00.3.8]
- Serves: goal 2.
- Revisit if: 00's integration rejects the composition (then express both as a single `adjust` family on `dc`).

### DL-15-11: A request above the ceiling is G4, not a harder roll
- Decision: effective size > ceiling → G4 with a computed counter-offer; exactly one rung above, with a term and standing ≥ Wary → a persuasion campaign.
- Alternatives considered: rolling at a huge DC (preserves a 5% miracle that is exactly the unearned success the research warns of).
- Evidence: [R4 W2 120:1 leniency] [R7 F4 impossibility categories]
- Serves: goal 2; goal 1 via the counter and campaign.
- Revisit if: players report social walls in playtest exit surveys more than twice per session.

### DL-15-12: Four term types are the only things that shrink a request
- Decision: Want (recorded want or a universal interest under an established threat), Payment (verified value ≥ price), Leverage (debt, held secret, credible threat), Obligation (a written commitment; Wary+). Max two; one fact one use; tie-break false.
- Alternatives considered: free-form "good offers" judged by the DM (unbounded; seducible).
- Evidence: [R: https://2e.aonprd.com/Rules.aspx?ID=1201 (Discover and cater)] [R5 SO-07] [SG-06]
- Serves: goal 1 (finding wants is rewarded), goal 2.
- Revisit if: T-15-SEDUCE finds terms granted from rhetoric without a cited id.

### DL-15-13: Social delivery specializes the Talk card's reach ladder
- Decision: T-15-5 (Limited = a lesser yes chosen from the record; Standard = as asked; Great = an extra from the record; Exceptional = + a lever); agreements are written as the NPC's committed act.
- Alternatives considered: binary yes/no (all-or-nothing, the probe's complaint).
- Evidence: [01.18.7] [C:P17 spirit] [R7 §4.2]
- Serves: goal 1.
- Revisit if: Limited-reach outcomes are rated "pointless" in playtests.

### DL-15-14: Standing does not enter intimidation or provocation DCs (deviation from 06's request for taunts and demands)
- Decision: fear and anger ignore regard; intimidation has its own threat ceiling (R2; R5 only for threats to life or kin) and costs −1 standing at scene end; parley (a request) does use standing.
- Alternatives considered: standing in every social DC as 06 asked (a Hostile foe would be harder to frighten, which inverts fiction: hostility does not make a man braver).
- Evidence: [06 Interface requests] [R7 §4.2 Ex.10 (wolves intimidated by torch)]
- Serves: goal 2 (fictional coherence), goal 1 (threats are a real option against enemies).
- Revisit if: 06's morale sim shows demands too strong against Hostile foes.

### DL-15-15: Performance against an audience-mood tier, paid within market depth
- Decision: five audience tiers; coin per evening by settlement and reach (T-15-11), capped by 08's market depth and labor cap.
- Alternatives considered: a performance roll against each listener (crowds are obstacles, not people).
- Evidence: [T-00-5] [08.8.5, 08.8.9]
- Serves: goal 1.
- Revisit if: a performer out-earns a master crafter (OEQ-08 economy tests).

### DL-15-16: Claim plausibility is checked against the NPC's knowledge, four rungs, worse-for-the-liar tie-break
- Decision: known false (G4) / outrageous (reach Limited) / doubtful (engine snag −2) / plausible; shifts for alertness, caught_lying and evidence; checked only against what the NPC knows (12.10.6).
- Alternatives considered: plausibility judged against the world's truth (the NPC would "sense" lies it has no way to detect — a leak of sealed state).
- Evidence: [01.18.7] [R4 §9 10 #3 Story-Engine claimCheck] [R: https://arxiv.org/abs/2609.23043]
- Serves: goal 2.
- Revisit if: T-15-SEDUCE shows plausibility rungs moving with phrasing.

### DL-15-17: Every lie is a recorded belief with a sealed truth and a truth-out clock
- Decision: belief facts held by believers; lie records with truth-holders and contradiction patterns; a hidden clock 8/6/4 by plausibility with five tick sources; exposure on contradicting knowledge or completion; confession costs −1 instead of −2.
- Alternatives considered: lies resolved and forgotten (NPC knowledge contradictions, the named long-horizon failure); a per-week Oracle "is it discovered?" (no telegraph, no player agency).
- Evidence: [R1 §10 knowledge contradictions] [R4 W7] [00.8 omens]
- Serves: goal 2 (consistency), goal 1 (lies are powerful and have a shelf life the player can see coming).
- Revisit if: T-15-LIES exposure rates fall outside the target band.

### DL-15-18: Alertness is a four-rung stored ladder with listed raises, effects and an hourly decay to floors
- Decision: unaware → suspicious → alert → alarmed; effects on surprise, deception, talk and Sneak; raised only by listed sources; decay one rung per quiet hour to a floor.
- Alternatives considered: alertness as narration (06's surprise and 10's notice need state).
- Evidence: [01.13.6] [06.2.4] [03 request for `unaware`]
- Serves: goal 2.
- Revisit if: 10's site playtests show alertness decaying too fast for tension.

### DL-15-19: Reading a person is a bundled Observe against a mask, delivering record fields under P17
- Decision: seven closed items; concealed items against mask (10 + Presence + deception competence), open items Easy; delivered items unseal wants, fears, refusals or "lying / no lie you can see"; critical failure may mislead.
- Alternatives considered: insight against standing (friends would be easier to read, which is backwards for secrets); unlimited free reading (wants are the main lever source and must cost something).
- Evidence: [R: https://2e.aonprd.com/Rules.aspx?ID=1201 Discover] [C:P17] [01.10]
- Serves: goal 1.
- Revisit if: reads are used every exchange (then spend patience on noticed reads by default).

### DL-15-20: Deals: the NPC's counter is computed from its record; payments haggle to a floor of half
- Decision: counter order — top servable want, payment at price, obligation; bargain moves notches per 08's ladder; floor half.
- Alternatives considered: the DM names a price (the documented "ask about price instead of leaving" failure).
- Evidence: [R4 W4] [08.8.7]
- Serves: goal 2.
- Revisit if: counters feel mechanical in playtests (add a d6 flavor table of how the counter is phrased; no number changes).

### DL-15-21: Ransom = 10 × the PC's weekly lifestyle × power band
- Decision: a deterministic ransom figure, payable within 4 weeks, bargainable to half.
- Alternatives considered: captor-chosen sums (free number from the AI, SG-01).
- Evidence: [08.8.6 lifestyle as wealth proxy] [09.9 captive_fate] [07.4]
- Serves: goal 2.
- Revisit if: 07/09 define a captor-specific ransom table.

### DL-15-22: Persuasion campaigns: two racing clocks, varied approaches, a want-serving deed ticks 2
- Decision: only for ceiling+1 with a term and standing ≥ Wary; progress 4/4/6/8 by target, patience 4/6/6/8 by standing; beat DC at the rung below the target; one beat per day; compromise by patience fill.
- Alternatives considered: unlimited re-rolls over days (grind); no multi-scene persuasion (big asks would be walls).
- Evidence: [PF2e influence] [Burning Wheel Duel of Wits compromise] [01.14.6] [scratchpad social15.py: e.g. P1 talker vs defense 10: 98–100% wins, 7–30% with compromise; vs defense 16: 39–89%, 37–76% compromise]
- Serves: goal 1 (big asks are pursuable), goal 2 (bounded, priced).
- Revisit if: campaigns are won in under 3 beats on average against principal NPCs.

### DL-15-23: Debate is one tug clock before a decider; six exchanges; status quo on a tie
- Decision: PC beats vs the decider's defense with standing toward the PC; opponent by fortune check with the decider's standing toward the opponent; 6/8 segments from half.
- Alternatives considered: opposed roll-offs (01.14.5 forbids); vote-by-vote resolution (councils' members are rarely all generated).
- Evidence: [01.14.5] [R5 TOR councils]
- Serves: goal 1.
- Revisit if: debates routinely run to the six-exchange limit.

### DL-15-24: The Three Clue Rule is an engine invariant with reserves and an audit
- Decision: per necessary node ≥3 placements, ≥2 holder kinds, ≥2 methods, ≥1 core, ≥2 places, 2 reserves; `h.15.placement_audit` keeps ≥2 live; PR-15-7 generates more; ≥1 proactive fallback per case.
- Alternatives considered: the rule as GM advice (the narrator cannot be trusted to remember; R1 gap G-6).
- Evidence: [R: https://thealexandrian.net/wordpress/1118/roleplaying-games/three-clue-rule] [R5 P-41] [R6 B-13, B-R4] [12.8.4]
- Serves: C:P16; goal 1.
- Revisit if: T-15-CASE finds any stalled-without-lead state.

### DL-15-25: Core clues are delivered without a roll on reaching the holder with a fitting method
- Decision: GUMSHOE's guarantee: a necessary node's core content is never behind a failable roll; rolls buy extra findings, time and safety; persons' core clues require the telling to be within their ceiling.
- Alternatives considered: rolled access to every clue (the probe's soft-lock; plot stagnation).
- Evidence: [R: https://pelgranepress.com/gumshoe/files/GUMSHOE%20SRD%20CC%20version.pdf] [R5 P-41] [specs/001 probe soft-lock]
- Serves: C:P16; goal 1.
- Revisit if: T-15-CASE median resolution falls under 4 scenes.

### DL-15-26: Deduction is a deterministic sufficiency check with two indistinguishable answers; confirmation only by evidence
- Decision: a theory is matched to a node; if the cited held clues contain a `deducible_from` set → "supported" (inferred knowledge), else "unsettled" — the same answer for wrong theories; confirmation only by direct placements, confessions, tests or accusations; the solution never moves.
- Alternatives considered: a Recall roll to "work it out" (a roll that can reveal the sealed answer — leak); DM confirmation by narration (sycophantic, and the research's leakage path).
- Evidence: [R4 §5.2 items 3–4] [R: https://arxiv.org/abs/2605.10794] [R: https://arxiv.org/abs/2609.23043]
- Serves: goal 2 (no leak), goal 1 (player reasoning is recognized as reasoning).
- Revisit if: T-15-LEAK shows a rise in guess accuracy.

### DL-15-27: Downtime week = one week activity (5 days) + two day activities, or seven day activities
- Decision: the week is the planning unit; handlers resolve day and week activities; an interrupted week activity with under five days ticks nothing.
- Alternatives considered: Blades' two activities per downtime (no time grain); free day-by-day allocation of everything (lets learning clocks compress).
- Evidence: [R6 B-05 Ars Magica seasons] [R5 P-45] [C:P15] [00.7.3]
- Serves: goal 2; P15 time-gating.
- Revisit if: T-15-BREADTH exceeds 6 licenses a year.

### DL-15-28: Learning is deterministic (no roll) at fixed weekly rates from the source; one learning clock per week
- Decision: Train ticks clocks at 05/02's rates; fees per 08.8.8; cnt.training 1/week; grants provisional; rolls never grant.
- Alternatives considered: rolled training (luck would let some characters learn in a week; INV-7's spirit).
- Evidence: [05.8.5] [05.9.4] [02.4.6] [C:P15] [C:VII]
- Serves: goal 2.
- Revisit if: players find training weeks unengaging (add an optional rolled "push" costing coin that never exceeds +1 tick).

### DL-15-29: Projects: scope-sized clocks (8/12/12+12/12×3), weekly roll ticks by reach, delegation 1/week, obstacles cap at half
- Decision: as 15.12.1, mapping Blades' 1/2/3/5 to delivered reach 1–4; WWN-style named obstacles removed by threads.
- Alternatives considered: WWN renown-priced projects (no renown currency here).
- Evidence: [R: https://bladesinthedark.com/downtime-activities] [R5 P-24, P-45] [R6 B-03]
- Serves: goal 1 (player-driven world change), goal 2.
- Revisit if: local projects take longer than a season with steady work.

### DL-15-30: Five owner-block effects for social results through the substrate
- Decision: eff.15.standing_step, request_step, plausibility_step, alertness_step, expose_lie; the step ladders and relationship writes need 00 amendments.
- Alternatives considered: prose effects on items ("people like you more") — prose-only mechanics are a defect (00.16.4).
- Evidence: [00.10.1] [PR-00-8]
- Serves: goal 2.
- Revisit if: 00 rejects the ladders (then items use levers only).

### DL-15-31: Social fact licenses (audience, safe conduct, guest-right, persona)
- Decision: four `kind: fact` licenses with fallbacks and acquisition paths, gating address to courts and giving passage/hospitality/persona effects.
- Alternatives considered: treating access to a lord as a mere request (a court would be as open as a tavern; VII's "established narrative fact" license unused).
- Evidence: [C:VII] [00.12.1]
- Serves: goal 2; goal 1 via redirects.
- Revisit if: the audience gate is reported as a wall (then make its fallback reach Standard for petitions with evidence).

### DL-15-32: Social and lore contests carry a band, and ruin and the brink are crises (revision I-003)
- Decision: 15.3.11 (social contests on principals or a faction's spokesman) and 15.9.20 (cases and research a principal or faction keeps) give their beats the contest band of 03.4.3; 15.3.8's Dire `cost.closed_door` against a principal or a faction is ruinous (03.4.5); a beat with the campaign's patience or the case's opposition clock one from full is at the brink.
- Alternatives considered: rating social deeds by the DC alone (rejected: the deed's greatness in the world is the party moved, not one exchange's difficulty, as a fight is rated by the fight); a judged "this negotiation matters" flag (rejected: a judgment where records already answer).
- Evidence: DL-03-26; `04-recog-parity.py` (envoy 18 / 46 against the archer's 19 / 51; scholar 17 / 46).
- Serves: goal 1, goal 2.
- Revisit if: as DL-03-26.

### DL-15-33: Terms buy certainty with one term only (revision I-048)
- Decision: 15.3.10's certainty size is the size minus at most one term (terms still lower the DC and the ceiling, 15.3.4); an Obligation term counts toward certainty only while the PC owes the NPC no undelivered commitment.
- Alternatives considered: the ledger default "original size R2 or less" (rejected: correct for Neutral, but it would remove the no-term certainty of Friendly R2 and Devoted R3).
- Evidence: `15-certainty-sim.py` (seed 48): certain beats 37.7% → 32.0% (honest), 53.6% → 38.8% (two terms always); certain R3+ requests 39.6% → 8.2%. WE-16-1 (Oda) now rolls at DC 10.
- Serves: goal 2 (an R3 real cost always meets the dice).

### DL-15-34: A request that defeats a want is one rung larger and never certain (revision I-074)
- Decision: 15.3.2 (one rung higher, cap R5, `[J:flag]` with a want id); 15.3.10's hesitation list adds the want; 15.2.5 item 3 does not apply when the request's Leverage term is the same fear.
- Evidence: verification-2c S2; `15-certainty-sim.py`: want-defeating requests certain 37.8% → 0%.
- Serves: goal 2 (NPCs act on their own goals).

### DL-15-35: Refusals read conduct or outcome; certain beats print "no evidence" (revision I-054)
- Decision: each refusal kind carries `reads: conduct | outcome` (T-15-6, `social.yaml`): a conduct refusal covers only the NPC's own doing; an outcome refusal covers any act of theirs that knowingly brings it about, including helping another. 12.15.3's RESULT shows a no-roll beat's reason and "no evidence" or "evidence as a no-roll success".
- Alternatives considered: the ledger's conduct-only reading for all kinds (rejected: would let "tell the killer where the child sleeps" past `innocent`).
- Evidence: verification-1 playtest (refusal.wilds and the nephew); 03.2.6.
- Serves: goal 2.

### DL-15-36: Only a binding party lends its faction's tier, and a contest's band is capped at power band + 2 (revision I-039)
- Decision: 03.4.3 / 15.3.11 / 15.9.20 / 08.6.4: a contest's band is the opposing party's own band (threat band, else its record's `band`), raised to its faction's tier only when the party can bind the faction (its head or an officer, 11.3.17; a faction that keeps a truth itself lends its tier to a lore contest); a door-warden, clerk or member speaking for it counts its own band. Every contest band (social, lore, craft) is at most the actor's `power_band` + 2, the most a fight lends (lethal +2).
- Alternatives considered: rate every deed by the individual's own band only (rejected: a bargain with a duke who binds a realm is a greater deed than one with a band-2 duke without it; the faction's weight is real when the party can commit it); no cap (rejected: a P1 who reaches a binding head of a tier-5 faction would still bank band-5 deeds without the danger a fight at that band carries); cap at power band + 1 (rejected: contests would then never reach a fight's lethal +2, and parity in `04-recog-parity.py` holds at + 2).
- Evidence: verification-redteam.md exploit 2; `04-recog-parity.py` I-083 section: a P1–P2 envoy farming a tier-5 faction's door-warden banks a median 24 band-4/5 deeds in ten sessions under the old rule and 0 under this one; tier pacing of honest play unchanged (envoy tier 3 at 19, tier 5 at 49). The craft analog (08.6.1 type-tier) takes the same cap; a project is one opposition (DL-04-31).
- Serves: goal 1 (non-combat parity without a cheap exploit); goal 2 (a deed's band means what the world says).
- Revisit if: live logs show a social calling's tier-4/5 great deeds coming mostly from capped contests (the cap binding often).

## DL-16 — Companions and Allies

### DL-16-01: The band rule — nobody above the PC's power band follows; allies serve at power band − 1
- Decision: anyone whose own band is at or below the PC's power band may follow; an ally serves at `serving_band = min(own_band, max(1, power_band − 1))`; people above the PC's band refuse (G4, redirected to escort, deal or thread); bound beings serve at the cap whatever their working's band (16.2.4).
- Alternatives considered: (a) no cap, companions at any band (simulation: one equal-band companion moves the advisory two words in 4 of 16 shapes — breaks 09.6.3's one-word contract and lets a follower out-fight the hero); (b) cap at the PC's own band (same failure); (c) refuse everyone above the cap (P2 characters could hire no town soldier at all — every town soldier is band 2; rejected as hostile to goal 1); (d) a "command span" limit instead of a band limit (does not stop a single strong ally out-powering the PC).
- Evidence: `16-companion-sim.py` (T-16-21): capped, one ally never moves a word by more than one; [R: https://oldschoolessentials.necroticgnome.com/srd/index.php/Retainers] (retainers of equal or lower standing than the employer); constitution IV (no second protagonist); 05's `rit.beast_bond` ("at or below your power band") uses the same test.
- Serves: goal 2 (the advisory stays true; the hero stays the hero), goal 1 (anyone at or below the PC's band can be recruited; everyone else has an honest redirect).
- Revisit if: T-16-CAP shows players reject "a veteran fights at my level" in the fiction (then voice it more, do not lift it: the advisory contract depends on it).

### DL-16-02: Retinue cap = clamp(2 + Presence, 1, 6), counted in places
- Decision: 00.4.4's derived value is `2 + Presence`, minimum 1, maximum 6; places per T-16-2 (mounts and pack beasts, scene allies, household and holding staff take none; cohorts one per member); overflow resolved by the next week; posting someone frees a place (16.2.1–16.2.3).
- Alternatives considered: the old-school Charisma table (4 at average; built for a group sharing a table's attention); `1 + Presence` (0 allies for a Presence −1 caster — too lonely for solo play); no cap (every hireling a body that soaks attacks: T-16-21 shows four allies move a fight up to four words).
- Evidence: [R: https://oldschoolessentials.necroticgnome.com/srd/index.php/Retainers]; R5 G-3 and #8 (solo play needs companions); T-16-21 (two allies 1.1 words mean, four 2.0); the DM voices every ally (12.11.3).
- Serves: goal 1 (a party's texture for everyone, a household for the magnetic), goal 2 (bounded voicing and fight math).
- Revisit if: T-16-RETINUE shows ally-narration errors growing faster than the retinue (then 1 + Presence).

### DL-16-03: Cohorts are mobs from the PC's side, priced one place and one wage per member
- Decision: 3–6 members of one template joined for one reason act as one ally (pooled Vitality, 06.10.3's numbers step, one Command, one reaction, one standing); places and pay per current member; fallen members share one bleeding-out clock and one stabilizing beat (16.2.6).
- Alternatives considered: a cohort as one place (Blades' gang): the simulation shows a cohort of four is worth 1.7 words against four individuals' 2.0 — one place would make it a four-for-one bargain; cohorts with their own turn (free beats, INV-11).
- Evidence: T-16-21; [R: https://github.com/amazingrando/blades-in-the-dark-srd-content/blob/main/Blades-in-the-Dark-SRD.md] (gangs vs experts, cohort harm); 06.10 (mobs).
- Serves: goal 1 (warbands are possible), goal 2 (one entity to track; no hidden power).
- Revisit if: players never form cohorts (then they are not simpler enough) or always do (then they are cheaper than intended).

### DL-16-04: Ally lines are chapter 09's band tables at the serving band; Vitality 6/12/16/18/20, clamped below the PC
- Decision: attributes by rung, competence `c_b` on trained tags (no PC floor), defenses and Guard by 09.3.4, attacks at the band's standard harm plus an offset, no heavy blows; Vitality the lower of 09's standard and the PC reference Vitality of the band (band 1 raised to 6), size multipliers, clamped to the leading PC's maximum − 1; base modifiers clamped to the PC's band floor; Focus 09's adversary base (+1 casters), refilled only at long rests (16.4).
- Alternatives considered: bespoke companion stat blocks (a second numeric system to calibrate); PC-style characters (a second PC); 09's standard Vitality unchanged (bands 3–5 would give allies more Vitality than the hero — the validator caught it); T1 Vitality 5 (a band-1 ally falls to any heavy blow).
- Evidence: 09.3.2–09.3.4 and T-09-3; T-06-12 and DL-00-04 (PC Vitality 12 + 2 × (band − 1)); `16-gen_data16.py` (0 errors over 40 templates at every band); 07.12.1 (allies' Vitality is 16's).
- Serves: goal 2 (one numeric scale; never out-powering), goal 1 (any template at any band).
- Revisit if: T-16-ADV shows allies at bands 3–4 too fragile to matter (then the clamp, not the line, is the lever).

### DL-16-05: Hiring is a deal whose price is the wage; hazard sets the request rung
- Decision: T-16-9's five hazard rungs (camp work, safe road, venture, deadly, forlorn) size the hire; the wage advance and hazard pay are terms without 15.3.5's price test; wages never reduce R5; champions need a want term on a thread; legends never hire for coin (16.3.3). Candidates come from `dt.recruit`, limited by settlement and the PC's band (16.3.2).
- Alternatives considered: hiring as an automatic purchase (no NPC consistency: anyone hires for anything); hire DC by wage paid (coin buys courage — Mausritter's lesson is that pay buys service up to what was signed for, not past it).
- Evidence: 15.3.2–15.3.5; 08.8.8 wages; [R: https://loottheroom.uk/the-long-read-mausritter] (hirelings flee when asked beyond their bargain).
- Serves: goal 1 (hiring is fast, usually certain with terms), goal 2 (contracts bound what a hireling will face).
- Revisit if: hiring rolls fail so often that players stop hiring (then make wage-term hires at the ceiling certain).

### DL-16-06: Knacks — fifteen closed capabilities, at most three per ally, replace never stack
- Decision: T-16-6; each a training license or a core-effect bundle or a flag a named rule reads; template ≤ 2, one by training a season, a signature knack on the personal thread's completion; a fourth replaces one (16.4.7).
- Alternatives considered: allies drawing on 05's full ability pool (an open menu: C:V); no special capabilities (allies interchangeable bodies).
- Evidence: [C:V]; [C:VI]; Blades expert edges via the SRD link above; R5 NP-05.
- Serves: goal 2 (a one-line identity the AI cannot embellish), goal 1 (a trainable, story-earned difference).
- Revisit if: three knacks prove too few for long-lived companions (then raise to four, still replacing).

### DL-16-07: Loyalty acceptance, will, and losing heart are lookups on standing, contract and oath
- Decision: T-16-7 fixes what each rung accepts (Devoted/Friendly lethal, Warm Dire, Neutral Risky, Wary Safe); contracts add by hazard (R3 Dire, R4 lethal); oaths add lethal at Warm or better; WILL = capability + stakes within the largest acceptance + refusal + allowed order (16.7.2); allies at Neutral or below lose heart (automatic *stay back*) when first bloodied, when an ally falls in sight, or when the PC is Staggered; Warm only on the last; Friendly and Devoted never (16.7.4).
- Alternatives considered: OSR loyalty and morale rolls (a random refusal the player cannot plan around, and an AI-chosen moment to roll); no refusals (allies as tools).
- Evidence: [R: https://oldschoolessentials.necroticgnome.com/srd/index.php/Retainers] (loyalty in the face of danger); [R: https://loottheroom.uk/the-long-read-mausritter] (morale saves under stress and unpaid); R4 W4 (agreeable-NPC bias needs pre-committed refusals).
- Serves: goal 2 (no judgment at the moment of command; refusals shown before the action is spent), goal 1 (warmth is visibly worth more than pay).
- Revisit if: players report refusals as arbitrary (T-16-LOYAL survey).

### DL-16-08: Loyalty moves by two sensed six-segment clocks with closed sources; regard stops at Friendly
- Decision: regard and grievance clocks (16.5.3) fed only by T-16-8's seven regard and ten grievance sources (beasts: four and four); completions are standing steps (a proposed 15.1.5 source 8); regard completions count against 15.1.7's weekly small-source cap unless the cycle held an R3 (shared danger); regard never lifts past Friendly — Devoted only from deeds of weight, the personal thread, or a bond; grievance decays one a week without a tick; every tick renders an omen.
- Alternatives considered: one approval number (DA:O/BG3; one meter hides mixed feelings and invites spam); standing steps per event (one deed moves loyalty — too volatile; leniency error moves a rung); regard able to reach Devoted (`16-loyalty-sim.py`: an aligned PC's companion Devoted by session 12 in 93% of runs — devotion by attrition).
- Evidence: `16-loyalty-sim.py` (T-16-22); [R: https://bg3.wiki/wiki/Approval]; [R: https://steamcommunity.com/app/48700/discussions/0/535150948595822006/] (Mount & Blade complaints and departures); INV-14.
- Serves: goal 2 (no loyalty by narrator mood; one wrong tick is 1/6 of a step), goal 1 (the player can read and work loyalty).
- Revisit if: T-16-LOYAL pacing falls outside 4–10 sessions to Friendly for an aligned PC.

### DL-16-09: Followers come from confirmed, witnessed calling tiers and from ranks
- Decision: at most one follower offer a season at `reflection`, for a confirmed tier ≥ 2 whose evidence had a carrier witness, or a follower-granting rank (11); template by the calling's key branch (T-16-20); own band `band_cap − 1`; Friendly; oath of service; first value fixed by the calling's conduct evidence; accept/decline/defer (16.3.6).
- Alternatives considered: followers by reputation score alone (11's numbers not yet written; and a score is not a scene); followers on every tier (a flood at high tiers); provisional grants counting (a lapse would strand a follower).
- Evidence: 03.10 (witnesses and carriers); 04 (confirmation at the season boundary); R6 A-R1 (public recognition is witness-gated); R5 NP-05 (followers by rank and reputation).
- Serves: goal 1 (the world answers the PC's name), goal 2 (deterministic trigger, bounded rate).
- Revisit if: no follower appears in a 20-session campaign of a PC with confirmed tier 2 (then lower to tier 1 confirmed).

### DL-16-10: Counsel before, confrontation after, and a closed list of reasons for any ally act
- Decision: a `[J:flag]` AFFRONT test at OFFER makes a present ally voice one line of counsel before a deed it would resent (16.5.7); a completed grievance clock is a confrontation scene where amends that address a named source restore the lost step once (16.5.9); an ally acts only for the six reasons of 16.13.3 and expresses judgment only through counsel and omens.
- Alternatives considered: silent loyalty loss (teaches nothing; feels arbitrary); open-ended companion banter about the PC's conduct (the narrator would invent opinions — R4 W4's agreeable-persona and engagement biases in reverse).
- Evidence: [R: https://bg3.wiki/wiki/Approval] (warnings before departure); [R: https://arxiv.org/abs/2606.20708] (persona agreement bias, cited by 12.11.4); 00.3.14's telegraph principle.
- Serves: goal 2 (allies stay in character by construction), goal 1 (the player always hears what an ally cares about before it costs them).
- Revisit if: T-16-COUNSEL agreement is below 85% (then restrict AFFRONT to known values only).

### DL-16-11: The departure clock — four public days, voided by recovery
- Decision: Wary creates `clk.16.departure.<id>` (public countdown, 4, +1 a day, +1 per grievance tick); Neutral or warmer voids it; Unfriendly announces and leaves at the next safe scene's end; three warnings precede a loyal ally's departure (ultimatum omen, confrontation, departure clock) (16.6.2–16.6.3).
- Alternatives considered: immediate departure at a threshold (BG3's −50: abrupt); departure by DM judgment (drift).
- Evidence: [R: https://bg3.wiki/wiki/Approval] (two warnings); R6 C (telegraph before loss).
- Serves: goal 1 (time to make amends), goal 2 (a public, mechanical countdown).
- Revisit if: players lose allies without noticing the clock (then add an out-of-fiction `[STATUS]` line at each tick).

### DL-16-12: Betrayal only at Hostile, after an ultimatum, through a listed opportunity, never harming directly
- Decision: four conditions (Hostile; the grievance ultimatum rendered; not `kn.loyal`; an opportunity fact) and a six-row table by opportunity (theft, selling a secret, joining a courting faction, informing, slipping a watch, leaving a fight); no direct harm, no lethal frame, no bypass of 07's keys (16.6.6).
- Alternatives considered: betrayal as a DM twist at any standing (the least forgivable improvisation an AI can make); no betrayal at all (removes the stakes of loyalty).
- Evidence: R6 C (telegraphed loss); 12.7's twist discipline; Blades' *Loyal* edge (immunity to being turned).
- Serves: goal 2, goal 1 (betrayal is a consequence the player can see coming and prevent).
- Revisit if: betrayals never happen in long play (then the conditions are too strict) or feel unearned in surveys.

### DL-16-13: The advisory with allies — one word gentler, the hard exception, never more than one
- Decision: refine 09.6.3: applies with at least one able ally (conscious; Warm+ or contract-covered; serving band ≥ band cap); a hard estimate with no-ally win < 75 stays hard; at most one word for any number of allies (16.7.11); lethal warnings name allies; the advisory names any ally a single blow could drop.
- Alternatives considered: a full estimator with allies (PR-09-4 extension: more exact, but a new closed form to tune); counting each ally as a word (wrong: two allies average 1.1 words).
- Evidence: T-16-21 — one capped ally: lethal → hard 3/3, fair → easy 5/5, easy → trivial 1/1, hard → fair exactly when the no-ally win ≥ 75 (2/7), else hard (5/7); larger retinues under-credited (the safe direction, 09.6.8).
- Serves: goal 2 (the advisory stays honest), goal 1 (players know what a companion buys them).
- Revisit if: T-16-ADV (OEQ-16-3).

### DL-16-14: Allies who will not take orders fight as a held line, not with turns
- Decision: escorts, independent sides and over-band allies hold named foes on a public tug clock (6, from 3), one fortune check a round (CS +2, S +1, F −1, CF −2), numbers steps on both sides, the PC may join or shore it (16.7.12; PR-16-11; `eff.16.held_line_step`).
- Alternatives considered: allied sides with their own turns (free beats on the PC's side — the exact failure 06 closed); one fortune check for the whole side (no tension, no player agency); a first draft with success = delivered reach (equal-band holders won 83%: the escort always won — re-tuned to symmetric steps, 62%).
- Evidence: `16-heldline-sim.py` (exact chain): equal band 62%, a band or more above 75–96%, below or outnumbered 23–34%; 06's edge cases "Three sides" and "A battle"; R1 G-5, R3 G-27.
- Serves: goal 1 ("they hold the bridge while I…"), goal 2 (bounded, deterministic, visible).
- Revisit if: T-16-HOLD.

### DL-16-15: The party's time; journey roles plus quartermaster; downtime duties
- Decision: in site mode the party makes one significant beat per interval (allies Help or replace the PC's beat); in free mode and downtime allies work in parallel (one duty a week each, T-16-15); allies take 10's four roles plus a fifth, quartermaster (prevents one depletion face, rows 1–4, a day; tag `deed.wilds.survival.provisioning`); night rota at most two watches per ally (16.8).
- Alternatives considered: unlimited parallel site beats (halves every site's danger with a porter); no fifth role (the brief's quartermaster has no home; 03 and 10 invited extension); guide and groom as extra roles (guide = navigator; groom folded into the quartermaster's stores-and-beasts remit).
- Evidence: 10.5, 10.9, 10.13 (time-tick checks on intervals); R5 P-31, P-32 (Forbidden Lands quarter-day activities, The One Ring roles and fellowship phase); 03's `cnt.journey` ("10/16 may extend").
- Serves: goal 1 (companions matter on the road and at home), goal 2 (no time multiplication where time is the pressure).
- Revisit if: T-16-SITE.

### DL-16-16: An ally's death is real, telegraphed, and grieved in bounded state
- Decision: allies die only under Key 1 and after 07's four-round public bleeding clock with no stabilizing beat; the warning names allies; the death adds belongings to kin, a vow offered (never imposed), the others' G10 and loss of heart, memories, and the thread of absence; no lever from grief (16.9).
- Alternatives considered: companion death on a failed save (Ironsworn's miss-with-a-1: un-telegraphed in this ruleset's terms); immortal companions (removes the stakes the owner locked in).
- Evidence: 07.12; [R: https://ironsworn-rpg.fandom.com/wiki/Companion_Endure_Harm]; R6 C-R2; BRIEF §4.
- Serves: goal 1 (loss matters), goal 2 (a single roll never kills an ally).
- Revisit if: players report allies dying "out of nowhere" in surveys (then the warning text is failing, not the rule).

### DL-16-17: Allies grow by season — one band, bounded by the cap
- Decision: at the season boundary an ally's own band rises by one when it served the season and fought two conflicts against foes of its band (or one hard/lethal); template maximum; the serving band still capped (16.10.1).
- Alternatives considered: allies sharing the PC's evidence (P5 is per actor; most allies are not tracked: 03.2.7); never growing (static companions); growing per fight (a grind).
- Evidence: C:P2 (no levels; history-gated growth); C:VI (boundary points); 04's season consolidation.
- Serves: goal 1 (a porter becomes a veteran in two seasons), goal 2 (deterministic, rare, capped).
- Revisit if: long campaigns find allies stuck far below the cap (then lower the conflict requirement).

### DL-16-18: Protégés carry a bounded calling of their own
- Decision: protégé templates (squire, apprentice, acolyte) track evidence; 04 evaluates them with one deed seat, no oath seat, tier ≤ 3; a tier raises own band to tier + 1, competence clamped to `c_b + 1`, picks into a three-ability partition that replaces beyond three (16.10.4).
- Alternatives considered: no ally callings (the squire never becomes a knight); full callings (a second PC).
- Evidence: 03.2.7; 04's edge case "A companion"; R6 D-R4 (successors pre-connected); Pendragon's squires.
- Serves: goal 1 (the arc players love), goal 2 (bounded; a successor seeded).
- Revisit if: protégés out-pace the PC's attention (then limit to one protégé at a time).

### DL-16-19: A hireling who reaches Friendly after four weeks may stay on as a companion
- Decision: at contract end, a hireling at Friendly with four or more weeks served offers to stay for keep instead of wages; its contract hazard no longer binds it, its rung does (16.14.4).
- Alternatives considered: automatic conversion (no moment); never (hirelings forever mercenary).
- Evidence: [R: https://oldschoolessentials.necroticgnome.com/srd/index.php/Retainers] (retainer loyalty and the henchman tradition); Mount & Blade companions.
- Serves: goal 1 (a visible reward for treating people well).
- Revisit if: no conversion occurs in long play (then three weeks).

### DL-16-20: Legacy — allies as successors; retired heroes as mentors and escorts
- Decision: Friendly-or-warmer allies, protégés and contented departed companions are successor candidates (starting at 02's baseline); allies' standing toward an heir is their old standing − 1; a retired PC's band exceeds a successor's, so it serves as mentor, patron, contact or escort, never retinue (16.16).
- Alternatives considered: retired PC as a companion (a power transfer the retirement reset forbids, R6 D-R4).
- Evidence: R6 D-04, D-10, D-R4.
- Serves: goal 1 (continuity), goal 2 (no power carried over).
- Revisit if: 11's legacy procedure chooses otherwise.

### DL-16-21: Three owner-block effects and eight handlers
- Decision: `eff.16.loyalty_tick`, `eff.16.set_order`, `eff.16.held_line_step` (core effects cannot address per-ally clock instances or an ally's order field); handlers `h.16.retinue_upkeep` (defined), `h.16.contract_term`, `h.16.conflict_orders`, `h.16.follower_offers`, `h.16.season_growth`, `h.16.venture_end`, `h.16.held_line`, `h.16.loyalty_record`.
- Alternatives considered: prose effects (00.16.4 forbids); reusing `eff.tick_clock` with computed ids (items could not name "this ally's regard").
- Evidence: PR-00-8 (expand before you add); 00.7.4.
- Serves: goal 2.
- Revisit if: 00's integration finds a core expression.

### DL-16-22: companions.yaml is generated and validated
- Decision: `rules/_process/simulation/16-gen_data16.py` builds `data/companions.yaml` (40 templates with lines at every band; all of 16's tables) and validates every tag, license, ability, condition, effect, wage and base-item id against the canonical files and 16.4.6's never-out-power check.
- Alternatives considered: hand-written YAML (unvalidated ids drift).
- Evidence: the validator caught the band 3–5 Vitality problem (DL-16-04) and a wage-band mismatch (the boatman).
- Serves: goal 2.
- Revisit if: n/a (re-run whenever 05/08/09 data changes).

## DL-INT — Integration (Wave 3 → 4)

Decisions the integrator took while making the fifteen chapters one ruleset. None redesigns a rule: each applies
an approved amendment, resolves an ambiguity in the direction an existing rule already fixed, or records a
mechanical repair. Genuine design conflicts were logged as issues instead (`_process/issue-ledger.md`, I-029 to I-032).
Full record: `_process/integration-report.md`.

### DL-INT-01: Owner-block fragments are merged by text, entries preserved exactly, and stay re-mergeable
- Decision: every `data/contrib/<file>.NN.yaml` owner-block was inserted into its canonical file under `blocks:`
  (owner order) with the fragment's own header kept as comments; each merge was verified by parsing and deep
  equality against the fragment. `boundaries.yaml` was rebuilt from the seeded rows plus every owner-block (an
  owner's restatement supersedes 00's seeded row of the same id). The fragments moved to
  `_process/merged-contrib/`; the generator scripts that read or write them were repointed there, and
  `_process/simulation/integration-merge.py` re-applies every merge after any regeneration.
- Alternatives considered: re-dumping each file through a YAML library (loses comments and the authors'
  formatting); leaving fragments in `data/contrib/` (two places to read every owner's entries).
- Evidence: AUTHOR-BRIEF §3; 00.16.5; the merge log in the integration report.
- Serves: goal 2 (one canonical source per id; RC-DATA).
- Revisit if: a generator is re-run without the merge script (the validator then reports the missing ids).

### DL-INT-02: `terrain.road.causeway` is adopted as a level-2 tag
- Decision: ch.10 proposed it as level 3, but its parent `terrain.road` is a branch, so it is a level-2 child.
  00.5.5 lets 03 add level-2 children with a DL entry; this entry, written on 03's behalf at integration, is that
  record. The tag is already used by the region file; T-00-7 lists it.
- Alternatives considered: declining it (leaves a dangling tag in `region_thallen.yaml`); re-parenting it under
  `terrain.wetland` (renames a used id).
- Evidence: 00.5.5 rules 1–7 (all met); `tags.10.yaml` proposal.
- Serves: goal 2 (every place tag resolves).
- Revisit if: ch.03's revision prefers another parent (then retire with `superseded_by`).

### DL-INT-03: `terrain.road.bridge` no longer covers fords
- Decision: 00's seeded definition "Bridges and fords." overlapped the adopted `terrain.water.river.ford`; the
  bridge definition now reads "a way over a river, gorge or gap" and names the ford tag. The id is unchanged.
- Alternatives considered: two tags covering fords (violates SG-16's distinguishing-test rule).
- Evidence: 00.5.5 rule 4; SG-16; the ford proposal's own distinguish line.
- Serves: goal 2 (one classification per kind of place).
- Revisit if: never; a data entry tagged `bridge` for a ford is a data error.

### DL-INT-04: PR-10-8's word step is computed with the archetype's counter held
- Decision: the audit's advisory word is 09.6.4's `advisory_alone` (the reference PC carries the archetype's
  named counter); the no-counter word is printed beside it. Generic band-relative tables are audited at every
  home band 1–5 by `_process/simulation/10-word-audit.py` (issue I-027).
- Alternatives considered: the no-counter word (would bar every troll and wight from a table though their
  counters are discoverable lore, 09.10.2).
- Evidence: 09.6.4; 13's audit (DL-13-11) already used this convention.
- Serves: goal 2 (one reading of the budget for 13 and for 10's generic tables).
- Revisit if: playtests show players meeting counter-gated rows without the lore to find the counter.

### DL-INT-05: Within `interval` phase 2, affliction onset runs before site exposure (I-023)
- Decision: the registry order (owner chapter, then id) already runs `h.07.affliction_onset` before
  `h.10.site_exposure`; it is kept and stated in 00.7.5 and in `boundaries.yaml`'s header, so an affliction
  contracted in an interval first advances at the next one.
- Alternatives considered: a `before:` reversing it (would advance a fresh affliction in its first interval).
- Evidence: 07.9.3; 10.12.2; 00.7.5.
- Serves: goal 2 (no double-counted exposure).
- Revisit if: a hazard needs same-interval onset (then it should state an immediate stage, not reorder handlers).

### DL-INT-06: One order for multi-target shapes
- Decision: 05's spread tags and 06's shapes are one ordered list, 06's T-06-15: pierce, burst, cone, fork, chain,
  linger (cone inserted third by 06). 05.10.4 and `composites.yaml#spread_tags` now carry cone and the same order
  numbers, and `eff.05.spell_delivery` forms map to shapes (line → pierce, burst, cone, chain, zone → linger).
- Alternatives considered: two order lists differing only in numbering (an engine would have to choose).
- Evidence: T-06-15; 06's request to 05 (a); DL-05-17.
- Serves: goal 2.
- Revisit if: a sixth player-facing shape is added (amend both at once).

### DL-INT-07: The starter region's cases live in `investigation.yaml#cases`
- Decision: `case.silent_bells`, `case.orsolin_signet` and `case.treaty_of_the_ford` moved from
  `region_thallen.yaml#cases` (which now lists their ids) to `investigation.yaml#cases`, where 15's case rules
  read them; the graphs are byte-identical.
- Alternatives considered: two homes for cases (ids defined twice).
- Evidence: 13's Interface request to 15; 15.9.4.
- Serves: goal 2.
- Revisit if: regions grow enough cases to want a per-region file (then a `region_*.yaml#cases` schema section).

### DL-INT-08: T-00-9 is generated from `boundaries.yaml`
- Decision: the registry table in 00 is regenerated from the data file (105 handlers), which is canonical (00.1.4
  item 5); rows are boundaries, cells handlers by phase with any `before`.
- Alternatives considered: hand-maintaining a summary (it was already stale by 76 handlers).
- Evidence: 00.7.4; T-00-19.
- Serves: goal 2.
- Revisit if: never; regenerate on every handler change.

### DL-INT-09: 00.3.7's coherence paragraph and `advisory_by_difference` are retired, not deleted
- Decision: per the approved amendments from 06 and 09, both yield to T-09-9 / PR-09-4; the scale entry is kept
  with `lifecycle: retired` and `superseded_by` (00.16.3) so old records resolve.
- Evidence: IR ch.06 #7, IR ch.09 #3; DL-09-09.
- Serves: goal 2 (one advisory contract).
- Revisit if: never.

### DL-INT-10: WE-01-2's claim is "his long-lost sister" (I-024)
- Decision: Wren is a woman; the example now has her claim to be the guard's lost sister (his siblings, in the
  "no" branch, are two brothers), and 12.15.5's REDIRECT sample and 15's example label were aligned.
- Alternatives considered: keeping "brother" as an "outrageous claim" teaching point (the example's numbers
  treat the claim as plausible, so the text would contradict its own frame).
- Evidence: I-024; WE-01-2's frame (doubtful, not outrageous).
- Serves: goal 2 (examples that teach the rule they show).
- Revisit if: never.

### DL-INT-11: Every id prefix in use is registered in a generated table, 00.16.2a
- Decision: 00.16.2 names 53 prefixes, but the merged data defines ids under 90. The other 37 are file-local
  families such as `act.`, `cnt.`, `flag.`, `req.`, `standing.` and `wage.`. Under 00.16.2 every id's prefix
  must say which file defines it. So a registry table, 00.16.2a, is generated from the ids actually defined in
  `data/` by `_process/simulation/integration-prefix-registry.py`. Each row gives the prefix, the defining
  file(s) and the owning chapter, read from T-00-19. 00.16.2's prose list stays the core. The validator counts
  00.16.2 plus 00.16.2a as "registered" and reports any other prefix as an ERROR. A new prefix is added by
  re-running the script. The continuation session fixed the script's owner lookup for annotated file names
  (`callings.yaml#requirements`, `abilities.yaml (inline clock spec)`, `00-architecture.md#…`), which had
  printed "?" for `clk.`, `gen.`, `req.` and `tbl.`.
- Alternatives considered: (a) appending 37 prefixes to 00.16.2's prose by hand. That would be unreadable
  and stale at the next data change, the same failure DL-INT-08 fixed for T-00-9. (b) Renaming file-local
  ids under registered prefixes. That would rewrite authored data across a dozen files, beyond what
  integration may do.
- Evidence: 00.16.2 ("the prefix tells any reader which file defines them"); 00.1.4 item 5 (data is
  canonical); `validate_ruleset.py` § prefix registry; DL-INT-08 (the same pattern for T-00-9).
- Serves: goal 2 (every id resolves to one defining file; the engine can route any id by its prefix).
- Revisit if: Wave 4's audit finds a registry-only prefix that collides in meaning with a named one (then
  rename it in data, with `superseded_by`, and regenerate).

### DL-INT-12: A [J] rule may give its worst case inline, under one canonical label (I-001)
- Decision: [revision: I-001] 00.2.5 accepts two forms for a rule with a `[J:*]` decision: the template block, or the inline form (the decision as options or a "true only when" test, the default when uncertain, and the worst case labelled *Worst case (J):*, with an optional qualifier: *Worst case (J, tier):*, *Worst case (J) of a one-rung error:*). The worst case is never omitted. A script normalized the 127 inline labels in chapters 00–12, 15 and 16 that read *Worst case:*, *Worst case (tier):* or *Worst case of …* (ch.13 is left as written, per the owner's constraint; its one legacy label is accepted and counted apart). `validate_ruleset.py` now fails any `[J:*]` rule whose worst case is missing or carries a non-canonical inline label.
- Alternatives considered: converting every inline judgment to the full block (rejected: 152 rules, most of them one judgment inside a `[D]` rule, would gain eight to ten empty or repeated fields each and lose the prose that says why the judgment is bounded; the block's value is the worst case, which the inline form keeps); accepting any wording (rejected: an auditor and the anchor index need one string to find).
- Evidence: 239 rules with a `[J:*]` decision: 86 in block form, 152 inline with the canonical label, 1 legacy label in ch.13, 0 missing (validator summary); the normalizer is idempotent (a second run changes nothing).
- Serves: goal 2 (every judgment's worst case is stated and machine-findable); constitution P-B.
- Revisit if: a playtest's ruling ledger shows a judgment whose real worst case exceeded the stated one (then that rule moves to the block form with examples).
