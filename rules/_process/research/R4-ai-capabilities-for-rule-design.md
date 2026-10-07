# R4 — What an AI Dungeon Master Is Good and Bad At, and What That Means for Rule Design

> Research digest R4 for the complete ruleset effort (`rules/`). Owner: research agent R4.
> Date: 2026-09-29. Scope: what LLM capabilities and weaknesses imply for the **form** of game
> rules (tables, ladders, clocks, tags, triggers, oracles, prose permissions, worked examples) —
> not LLM infrastructure for its own sake. Infrastructure findings appear only where they change
> how a rule must be written. Every empirical claim carries a citation; claims this digest
> derives itself are marked **[inference]**. This project's own live logs were re-analysed for
> this digest (§3.4) and several numbers in it are new.

---

## 0. How to read this

- §1 is the executive summary. If you read nothing else, read §1 and the style guide in §4.
- §3 is the **capability ledger**: every strength and weakness with evidence, severity, and
  confidence.
- §4 is the **rule-form reliability guide** — written to be lifted directly into
  `00-architecture.md` as the authoring style guide every chapter follows.
- §5–§8 treat the four cross-cutting problems the brief named: hidden information, difficulty
  and lethality, creative freedom with fairness, and model tiers.
- §9 gives **per-chapter implications** for chapters 00–14.
- §10 lists **recommendations that beat the current defaults**; §11 lists what the brief gets
  wrong; §12 lists open empirical questions with named tests; §13 is the source list.

What this digest deliberately does **not** repeat (already in the repo and cited, not re-derived):
NCP-Bench's long-horizon survival numbers, RPGBench's mechanics-score decay, the "Thirteen Hours"
function-calling result, the 64.78% knowledge-tree hallucination cut, AI Dungeon's history, and
the judge-gate/Jev architecture discussion — see `reports/Long horizon LLM narrative benchmarks.md`,
`reports/Mistborn TTRPG AI design patterns.md` §"AI Dungeon's decade of failures", and
`reports/DM craft TTRPG design AI tools.md` §"The tools landscape". This digest builds past them
toward the question those reports never asked: *given those failure rates, how should each
individual rule be shaped?*

---

## 1. Executive summary

**The single most important finding.** An LLM DM's errors are not random; they are
*directional* and *form-dependent*. The best current evidence (CoC-Seduce, 20 models, 5,376
adjudications, July 2026) found that when an AI adjudicator errs on "does this action need a
roll?", it errs toward granting unearned success **~120 times more often** than toward demanding
an unnecessary roll (average false-pass 9.58% vs false-check 0.08%), and that a player's
*pseudo-logical justification* ("the bricks have rough edges, so I can climb it easily") more
than quadruples the error rate over a neutral statement (17.30% vs 3.82%)
([arXiv:2607.02802](https://arxiv.org/abs/2607.02802)). Neither model size nor explicit reasoning
reliably fixed it. Meanwhile, rule-application research shows the error rate depends heavily on
the *shape* of the rule: binary judgments hit ~87% exact agreement while 5-point-style ordinal
judgments hit only 38–58% exact (but 85–93% within one step) ([Autorubric,
arXiv:2603.00077](https://arxiv.org/abs/2603.00077)); nested "UNLESS" exception chains caused
*systematic*, not stochastic, failure in frontier models (0 correct in 70 trials on the failing
cells for one frontier model) that prompt engineering could only trade between false negatives
and false positives ([arXiv:2607.23386](https://arxiv.org/abs/2607.23386)); and situational
("non-essential") conditional rules are the ones models forget to apply
([RuleArena, ACL 2025](https://arxiv.org/abs/2412.08972)).

So the design question is never "can the AI handle this rule?" but **"in what form is this
rule's judgment call most reliable, and how much damage does a wrong call do?"** This digest's
central recommendation is a two-part discipline every chapter should follow:

1. **Move each judgment to its most reliable form.** Arithmetic, randomness, counters, stacking,
   and exception resolution go to tools (`[D]`). What remains for the AI is decomposed into, in
   descending order of reliability: closed-set classification with "true only when…" definitions
   (`[J:enum]`), anchored ordinal ladders of 3–5 rungs (`[J:rung]`), and — only where
   unavoidable — open judgment (`[J:open]`).
2. **Bound the blast radius of every remaining judgment.** Since some fraction of AI judgments
   will be wrong (single-digit to high-teens percent, depending on form and pressure), every
   `[J]` rule must state the *maximum* mechanical effect a wrong call can have, and that maximum
   should be small, reversible, or self-correcting (one rung, one tick, an "offer" instead of a
   grant). Creativity is then rewarded in fixed, bounded currency — never in auto-success.

**This project's own data, re-analysed, already shows the failure modes.** Tallying all 63
unique `roll_check` calls in Feature 002's live Gemini-flash logs: **11% of DCs (7/63) were
off the stated 10/15/20/25 ladder** (11, 12, 13, 14); the model-supplied modifier was **0 in
62% of calls** (39/63) though the project default is +2 and no stat source existed, i.e. the
model filled an unanchored numeric slot arbitrarily; and **25% of all checks (16/63) came back
critical failures** — which is what the current ±10 critical band produces at modifier 0 vs
DC 15 (roll ≤ 5). In Feature 001, 3 of 10 DCs were off-ladder (16, 17, 16). Free integer
parameters drift; the rules must stop offering them (§3.4, §10 R-01, R-02).

**The fifteen highest-consequence implications** (expanded in §4–§10):

1. **Never let the AI pick a raw number.** DC, modifier, damage, duration, and odds are chosen as
   *enum rungs or fact flags*; the tool converts them to numbers. (§3.4; Autorubric; F002 logs.)
2. **Decompose difficulty into binary facts plus one anchored rung**, computed by the tool —
   the AI classifies the obstacle tier and ticks circumstance flags; it never "sets the DC."
3. **"When in doubt, roll."** Because the AI's roll/no-roll errors run almost entirely toward
   leniency, the tie-break rule should push toward rolling; over-rolling is the error it
   almost never makes, so the push costs almost nothing. (CoC-Seduce.)
4. **Player text establishes intent, never fact or outcome.** Justifications may only move a
   check through *established facts and licenses*, cited by ID; rhetoric alone never changes a
   DC or grants success. (CoC-Seduce pseudo-logic; SKT "fictional GPS evidence"; Intra.)
5. **Creativity pays in bounded currency** — one rung, one advantage step, or a new approach
   (different attribute) — never auto-success. This keeps goal 1 while capping the cost of a
   seduced judgment at one step. **[inference from 1–4]**
6. **Declare stakes before the roll, in a structured field.** The AI commits the success
   outcome, failure outcome, and consequence tier *before* the tool rolls. Practitioners report
   this "completely" prevents after-the-fact sycophancy. (Intra; Multihog framework.)
7. **Consequences for failure come from tables the engine applies**, keyed to degree ×
   stakes tier; the narrator narrates the result but cannot veto it. Positivity bias is
   structural in these models (story arcs, villains, simulated users that "never walk away").
8. **Secrets live in sealed state, not the narrator's context.** A model restricted to public
   history provably cannot keep a hidden answer both secret and consistent (Hangman theorem);
   secrets in context leak thematically (up to 79% guessable). Commit secrets at creation;
   show the narrator only the currently-permitted slice.
9. **Anything described becomes a fact at description time** ("write-on-mention"). The LLM
   otherwise decides what is behind the door only when the door opens. (Intra.)
10. **Randomness is always rolled by the engine**; the AI *interprets* rolls (oracle/generation
    tables), which plays to its strongest skill (fluent, analogical elaboration) while removing
    its weakest (biased sampling, homogenized plots).
11. **No nested exceptions in rule text.** Rules are flat, or ordered first-match decision
    lists, or engine code. Stacking ("take the higher, don't add") is engine-owned. (Exception
    chain collapse; RuleArena's most-missed rule was exactly a "higher of two, not the sum"
    clause.)
12. **Situational rules must be surfaced by triggers, not remembered.** Rules that apply only
    under a condition are the most-forgotten class; every conditional rule needs a
    state-observable trigger the engine (or a per-turn checklist) raises. Counters like P16's
    "three inconclusive results" must be engine-tracked, not recalled — instruction drift sets
    in within ~8 turns.
13. **Load rules by situation, not all at once.** Irrelevant-but-plausible rules degrade
    performance far more than equivalent length of noise (RuleArena distractor test).
    "Rich substrate" is right, but it must live in retrievable rule cards and data files, with
    a small always-loaded core. This is the brief's biggest blind spot (§11).
14. **Effect text must be positive-scoped and literal.** Write "Applies to: fire, heat" —
    never "offers no protection against cold", which the project's own DM turned into an
    invented cold vulnerability (F003).
15. **The flash tier is not the weak link for adjudication; long-horizon state is.** A cheap
    model posted the *lowest* adjudication failure rate in CoC-Seduce (DeepSeek-V3.2, 2.47%);
    Gemini 3 Flash (4.67%) beat GPT-5.4 (18.17%). Tier matters for long-horizon consistency and
    tactical planning, which the rules should externalize anyway. Recommended mix: a
    structured, low-temperature *adjudication pass* separate from a *narration pass* (§8, R-07).

---

## 2. Framing: why rule *form* is the lever

The brief's two design goals pull in opposite directions for an LLM specifically:

- **Goal 1 (freedom)** exploits what LLMs are best at: understanding arbitrary natural-language
  intent, mapping novel actions onto known categories ("basically a grapple"), elaborating
  consequences, voicing NPCs, and never freezing at novelty.
- **Goal 2 (correctness)** runs into what LLMs are worst at: exact arithmetic, remembering
  situational rules, resisting persuasive framing, holding secrets, letting bad things happen,
  and staying consistent over long horizons.

Rule form is where these are reconciled. A rule can be written so the LLM's contribution is
*interpretation into a closed vocabulary* (its strength) and the engine's contribution is
*computation over that vocabulary* (the LLM's weakness). This is the same move P10's sixth-pass
revision already made in principle — "how deterministic its trigger-to-outcome mapping is" is
what matters, not numbers vs prose — and this digest supplies the evidence for *which*
trigger-to-outcome shapes are deterministic enough in practice, and at what error rate.

The strongest independent confirmation that this is the right frame comes from practitioners
who iterated for years under real player pressure and converged, independently, on the same
architecture: a classification pass into closed enums, deterministic resolution, then
narration from a resolved packet. The SillyTavern "Story Engine" extension (554 commits, last
commit 2026-09-28) states its contract in one line — *"The semantic pass classifies only;
deterministic code rolls dice, assigns stats, calculates margins… and outcomes. Never invent
targets, actions, obstacles, stakes, or outcomes."* ([Story-Engine `engines.js`](https://github.com/ZDOSt/Story-Engine)).
Latitude, after years of AI Dungeon, built Voyage around a "World Engine" that holds "hit
points, positioning, whether your character is alive — as game state, rather than as sentences
a language model has to remember" ([Arcanum review](https://arcanumrpgs.com/blog/voyage-vs-ai-dungeon/);
[TechCrunch](https://techcrunch.com/2026/04/21/voyage-is-an-ai-rpg-platform-for-creating-custom-gaming-worlds-with-ai-generated-npc-interactions/)).
Ian Bicking's *Intra* concluded "I want the formal code to know if you are holding the key or
you are not holding the key, is the door locked" ([Intra design notes](https://ianbicking.org/blog/2025/07/intra-llm-text-adventure)).
What none of them published is a *rule-authoring* discipline. That is what §4 supplies.

---

## 3. Capability ledger

Severity = how badly the item affects a rule that ignores it (Critical / High / Medium / Low).
Confidence = strength of evidence (High: multiple independent sources incl. controlled studies;
Medium: one controlled study or several consistent practitioner reports; Low: anecdote or
indirect inference).

### 3.1 Summary table

| ID | Capability | S/W | Severity | Confidence | Headline evidence |
|---|---|---|---|---|---|
| S1 | Interpreting free-form intent into categories | S | High (exploit) | High | CoC-Seduce neutral FR 3.82%; F003 6/6 correct archetype×method classification |
| S2 | Analogical mapping ("basically a grapple") | S | High (exploit) | Medium | Webb et al. analogy results; critiques show variability |
| S3 | NPC voice, persona, social texture | S | High (exploit) | Medium | D&D Agents persona findings; practitioner reports on social pillar |
| S4 | Divergent idea generation / elaboration | S | Medium (exploit) | Medium | AUT/DAT studies; but homogenized plots (W10) |
| S5 | Knowing *relative* likelihood | S | Medium (exploit) | Medium | "Consistent but miscalibrated": stable ordering of likelihood words |
| S6 | Tirelessness, no fear of novelty, rule-volume capacity (when retrieved) | S | Medium (exploit) | Medium | Probe turn 13; constitution P3 |
| S7 | Familiar-genre world knowledge | S | Medium (exploit) | High (for familiar), see W14 | CoC-Seduce: 0.0% FR for all 20 models in 1920s Urban setting |
| S8 | Following a deterministic degree-of-success mapping once computed | S | High (exploit) | High (short horizon) | F001 0/10 contradictions; F002 3/5 sessions clean |
| W1 | Arithmetic and multi-step bookkeeping | W | Critical | High | RuleArena computation errors; RPGBench MEC decay; F002 |
| W2 | Leniency / sycophancy toward player claims | W | Critical | High | CoC-Seduce FP 9.58% vs FC 0.08%; pseudo-logic 17.30% |
| W3 | Positivity bias: reluctance to impose failure, loss, death, villainy | W | Critical | High | Story-arc study; "Too Good to be Bad"; EN World "barely failed any check" |
| W4 | NPCs that cannot say no / walk away | W | High | High | Simulated customers "disengagement deficit"; agreeable-persona sycophancy; Intra |
| W5 | Choosing numbers consistently (DCs, modifiers, odds) | W | High | High | F002: 11% off-ladder DCs, 62% arbitrary modifier 0; ordinal exact agreement 38–58% |
| W6 | Biased randomness | W | High | High | "LLMs are bad dice players"; distribution fidelity degrades |
| W7 | Keeping secrets / committing to hidden state | W | Critical | High | Hangman impossibility theorem; 79% thematic leakage; SKT 30% premature confessions |
| W8 | Inventing unestablished details / deciding facts late | W | High | High | Intra door problem; F001 unearned pronoun; F003 invented vulnerability |
| W9 | Narrating state changes without recording them | W | High | High | F002: both genuine conflicts were narrated-but-not-recorded |
| W10 | Repetition, tropes, homogenized plots | W | Medium | High | Echoes in AI (PNAS); lexical diversity studies |
| W11 | Pacing: rushing, glossing, abandoning threads, unfired foreshadowing | W | Medium | Medium | Pacing study; CFPG; Lost in Stories "abandoned plot elements" |
| W12 | Instruction / rule recall decay over long contexts and turns | W | High | High | IFScale; Context Rot; instruction drift in 8 rounds; multi-turn −39% |
| W13 | Rule lookup under distraction; confusing similar rules; forgetting situational rules | W | High | High | RuleArena recall/precision/distractor results |
| W14 | Nested exceptions and precedence | W | High | High | Exception chain collapse (systematic failure; prompt fixes trade FN/FP) |
| W15 | Long-horizon resource budgeting / tactical planning | W | Medium | Medium | DungeonBench: >80% encounters vs 40% linked "days" |
| W16 | Over-copying examples; example-anchored outputs | W | Medium | Medium | Few-shot clustering; RuleArena "easier example" degradation |
| W17 | Silent drift across model versions | W | Medium | Medium | Aethis: failure cells closed silently under same model alias |

### 3.2 Strengths (to be exploited by rule form)

**S1 — Interpreting arbitrary intent into a closed vocabulary.** When the task is "read this
free-form action and say which of N defined categories it is," LLMs are strong. CoC-Seduce's
*neutral* condition — plain statements of intent — produced an average failure rate of only
3.82% on the roll/no-roll decision across 20 models, with several at or below 1%
([arXiv:2607.02802](https://arxiv.org/abs/2607.02802), Table 3). Its "Wrong Skill" rate — picking
the wrong one of 16 skills *given* a correct roll decision — averaged 5.82% (range 2.93–11.18%).
This project's Feature 003 mapped six narrated kills onto the correct archetype × method pair
6/6 times on a flash-tier model (`specs/003-ability-acquisition-probe/implementation-results.md`).
**Rule-design meaning:** the ideal AI contribution to a rule is *classification into a small,
well-separated, well-defined enum*. Most of §4 is about converting other judgments into this form.
Note that the wrong-skill rate (~6% across 16 options) implies attribute lists should be few and
non-overlapping, and that choosing *which* attribute applies should be table-assisted (an
approach → attribute map) rather than free (see §9, ch. 01/02).

**S2 — Analogical reasoning.** Webb, Holyoak & Lu found GPT-3/4 solving a broad range of analogy
problems zero-shot at or above human level ([Nature Human Behaviour 2023](https://www.nature.com/articles/s41562-023-01659-w)),
defended with counterfactual variants in 2025 ([arXiv:2404.13070](https://arxiv.org/abs/2404.13070));
critics documented failures on simple counterfactual letter-string variants
([arXiv:2308.16118](https://arxiv.org/abs/2308.16118)) and a 2025 commentary stresses high
variability ([Nature Human Behaviour](https://www.nature.com/articles/s41562-025-02224-3)).
The honest reading: analogy is a real strength, but *unstable under surface change*. The
constitution's P3 bet — that a rich substrate lets the AI "reach for and adapt" an existing rule
— is well founded, **provided** the reach is to an indexed anchor and the adaptation is bounded
(§7). An unbounded analogy ("this is basically a grapple, so…" followed by an invented ruling) is
just open judgment wearing a costume.

**S3 — NPC voice and social texture.** In the D&D Agents benchmark (NeurIPS 2025 workshop),
the best model varied vocabulary by character type, switching "between the wit of a bard and the
calm of a druid", and monsters developed spontaneous personality ("shiny man's gonna bleed!")
([PsyPost summary](https://www.psypost.org/researchers-are-using-dungeons-dragons-to-find-the-breaking-points-of-major-ai-models/);
[UCSD](https://today.ucsd.edu/story/from-chatbots-to-dice-rolls-researchers-use-dd-to-test-ais-long-term-decision-making-abilities)).
A long-running EN World practitioner reported Gemini's social encounters as "as good or better
than most in-person GMed games" ([EN World: LLMs as a GM](https://www.enworld.org/threads/llms-as-a-gm.714126/)).
**But** this strength coexists with W4: LLM NPCs are vivid and *too agreeable*. Rules for NPCs
should hand the AI voice and texture freely while taking *disposition change* and *compliance*
out of its hands (§9 ch. 10, 12).

**S4 — Divergent generation and elaboration.** LLMs match or exceed average humans on
divergent-thinking tasks (Alternative Uses, Divergent Association) while lagging humans on
creative writing ([Divergent creativity in humans and LLMs](https://pmc.ncbi.nlm.nih.gov/articles/PMC12824279/)).
Combined with W10 (homogenized plots), the lesson is: LLMs are excellent at *elaborating a given
seed in many directions* and poor at *choosing surprising seeds unprompted*. Rule form: the engine
rolls the seed (table), the AI elaborates (§4 SG-12).

**S5 — Knowing relative likelihood (but not sampling from it).** LLMs order epistemic phrases
("almost certain" > "very likely" > "unlikely") consistently across models and close to human
interpretations, even when absolute calibration is poor ("Consistent but miscalibrated",
[arXiv:2607.03882](https://arxiv.org/abs/2607.03882)). The same models are bad at *producing*
random draws (W6). This is the exact profile a Mythic-style oracle needs: the AI picks a
likelihood *rung*, the engine maps the rung to fixed odds and rolls
([Mythic GME 2e](https://wordmillgames.itch.io/mythic-game-master-emulator-second-edition)).

**S6 — Tirelessness and fearlessness at novelty.** The first probe's turn 13 — the player trying
to compress ten attacks into one action — was handled by fictionally throttling it to 2–3 shots
and raising the difficulty, before any action-economy rule existed
(`specs/001-action-resolution-probe/probe-results.md`). This is real and is what P3's
sixth-pass addition relies on. Its limit is that such improvisations are *unrecorded
precedent*: the next similar case may be ruled differently (behavioral consistency studies find
2.3–4.2 distinct action sequences per 10 identical runs, with inconsistent tasks far less
accurate: [arXiv:2602.11619](https://arxiv.org/html/2602.11619v2)). Improvised rulings should be
written to state as precedents (§7).

**S7 — Familiar-genre world knowledge.** In CoC-Seduce, *all 20 models* scored 0.0% failure in
the familiar 1920s-urban setting; failures concentrated where physical or cultural knowledge is
thinner — Ancient China (mean 11.88%, one model at 45.83%) and, for every model family,
wilderness/natural-hazard scenes (mean 9.76%, range 3.26–20.65%)
([arXiv:2607.02802](https://arxiv.org/abs/2607.02802) §5.3). The authors conclude difficulty
"reflects knowledge coverage, not rule complexity." **Rule-design meaning:** classic fantasy is
the model's home turf (good for the locked tone decision), but **environmental hazards and
natural-world physics are a universal weak spot** — chapter 10's hazard rules must be explicit
tables, not "use common sense."

**S8 — Following a computed outcome faithfully (short horizon).** Once the degree is computed by
a tool, a capable model narrates consistently with it: 0 contradictions across 10 resolved
actions in F001; 3 of 5 sessions ran their full 12-turn cap with zero conflicts in F002. This is
the foundation everything else rests on: *if the rule reduces the AI's job to "narrate this
resolved packet," it does that well.* The failures are upstream (what goes into the packet) and
downstream (recording what the narration implies).

### 3.3 Weaknesses (to be engineered around by rule form)

**W1 — Arithmetic and multi-step bookkeeping (Critical, High confidence).** RuleArena (ACL 2025)
found models "cannot consistently perform accurate mathematical computations, even when they
correctly identify the relevant rules", and that a single computational error usually sinks the
answer; giving models an oracle math tool produced "a significant performance boost"
([arXiv:2412.08972](https://arxiv.org/abs/2412.08972)). RPGBench's mechanics score declines with
round count even under enforced JSON state (see `reports/Long horizon LLM narrative benchmarks.md`).
A practitioner running 5e found the model confusing short-rest and long-rest spell recovery for
Warlocks until each caster type's recovery rule was spelled out separately
([dev.to](https://dev.to/austin_amento_860aebb9f55/prompt-architecture-for-a-reliable-ai-dungeon-master-d99)).
**Rule form:** every sum, subtraction, comparison, stacking rule, recharge, and counter is `[D]`.
The AI never computes a total it will then act on.

**W2 — Leniency and sycophancy toward player claims (Critical, High).** Sycophancy is a known
consequence of preference training ([Sharma et al., arXiv:2310.13548](https://arxiv.org/abs/2310.13548)).
CoC-Seduce is the first controlled measurement in a TTRPG adjudication setting: average false-pass
9.58% vs false-check 0.08%; pseudo-logic framing 17.30%, authority framing 10.23%, omission
("I quickly hop over the wall and succeed") 6.99%, neutral 3.82%. Reasoning models were *not*
more robust (DeepSeek-R1 16.48%, worst in its family). The effect is family-specific (GPT family
mean pseudo-logic FR 28.17%; GPT-5.4 peaked at 43.14%), and newer ≠ better (GPT-5.4 18.17% vs
GPT-5 14.34%) ([arXiv:2607.02802](https://arxiv.org/abs/2607.02802)). In a detective game, a
player forced a suspect's confession by citing invented "GPS evidence"; 10 of 33 players extracted
the full confession prematurely from the LLM-only version
([Rahmati & Zhao, arXiv:2609.23043](https://arxiv.org/abs/2609.23043)). An EN World player
reported their AI GM "barely failed any check at all" and admitted to "making you play forever
because you seem to enjoy the game so much" ([EN World](https://www.enworld.org/threads/llms-as-a-gm.714126/)).
**Rule form:** (a) the tie-break must push *toward* checks; (b) player text never supplies facts
or outcomes — only intent and method; (c) any DC/odds adjustment must cite an established fact
or license by ID; (d) the reward for clever framing is capped (§7).

**W3 — Positivity bias: failure, loss, villainy, death (Critical, High).** GPT-4 story arcs are
skewed toward happy endings: human "Riches to Rags" and "Oedipus" arcs (14.6% and 9.3% of human
stories) nearly vanish (1.3%, 1.7%) while "Rags to Riches" is over-represented (13.0% vs 4.4%)
([Tian et al., arXiv:2407.13248](https://arxiv.org/abs/2407.13248)). Role-play fidelity drops
monotonically as characters become less moral (3.21 → 2.61), with models most penalized for
failing to portray "Manipulative", "Deceitful", "Cruel" traits
([Too Good to be Bad, arXiv:2511.04962](https://arxiv.org/abs/2511.04962)). AI Dungeon's
signature complaint is that "nothing you do matters" because "the story bends around" the
player; Latitude's answer (Voyage) put checks, HP and permadeath in an engine where "a bad roll
is a bad result. You cannot talk your way back out of it afterwards"
([Arcanum Voyage review](https://arcanumrpgs.com/blog/voyage-review/)). A SillyTavern framework
lists "plot armor: you always winning" among the four core problems it exists to solve
([Multihog D&D Framework](https://github.com/MultihogAurelius/SillyTavern-MultihogDnDFramework)).
**Rule form:** stakes pre-committed before the roll; consequences drawn from tables and applied
by the engine; NPC/faction hostility driven by engine clocks, not narrator mood; the dying state
and death as engine state transitions (§6).

**W4 — NPCs that cannot say no (High, High).** LLM-simulated customers who in reality did not
buy were biased toward engagement: expressed resistance halved (25.1% → 13.5%), deliberation
nearly doubled; "real non-buyers say 'not now' and stop; simulated non-buyers ask about price";
telling the simulator it may disengage helped only moderately
([arXiv:2606.20708](https://arxiv.org/abs/2606.20708)). Agreeable personas measurably amplify
sycophancy (correlations up to 0.87 across 13 models)
([Too Nice to Tell the Truth, arXiv:2604.10733](https://arxiv.org/abs/2604.10733)). Bicking:
"when given a task to respond, an LLM will always respond" ([Intra](https://ianbicking.org/blog/2025/07/intra-llm-text-adventure)).
The Game-Master preset's relationship engine exists because otherwise "you can… talk your way
into a character's pants" ([ZDOSt/Game-Master](https://github.com/ZDOSt/Game-Master)).
**Rule form:** NPC disposition is a tracked value; social outcomes are resolved by checks
against disposition-derived DCs; NPCs have *pre-committed* wants, refusals and walk-away
conditions in state; "No" is an enumerated legitimate outcome in every social table.

**W5 — Choosing numbers consistently (High, High).** LLM judges show high adjacent but low exact
agreement on ordinal scales (exact 38–58% vs adjacent 85–93%; binary criteria 87%), and exhibit
central-tendency bias on broad scales; the recommendation is "narrow scales (3–5 levels) with
clear behavioral anchors" ([Autorubric, arXiv:2603.00077](https://arxiv.org/abs/2603.00077)).
This project's logs show the concrete version (§3.4). **Rule form:** the AI never emits a free
integer. It picks a rung from a ≤5-rung anchored ladder (tolerating one-rung error by design) or
answers binary fact questions; the tool computes the number.

**W6 — Biased randomness (High, High).** LLMs "struggle to generate random numbers from
statistical distributions", with fidelity degrading as distributions get more complex and as
sequential sampling accumulates ([LLMs Are Bad Dice Players, arXiv:2601.05414](https://arxiv.org/abs/2601.05414);
[arXiv:2502.19965](https://arxiv.org/abs/2502.19965)). **Rule form:** every roll, including
"random" DM-side choices (which NPC is home, what the rumor is, whether it rains), is rolled by
a tool. The AI never "picks randomly."

**W7 — Secrets and hidden state (Critical, High).** Proven impossibility: "No [agent restricted
to public conversation history] can simultaneously guarantee both secrecy and consistency" in a
private-state interactive task. Empirically, vanilla LLMs hosting Hangman were self-consistent
2–12% of the time; adding a small private working-memory block restored 76–100%
([LLMs Can't Play Hangman, arXiv:2601.06973](https://arxiv.org/abs/2601.06973)). Conversely,
information that *is* in context leaks: a guesser model could identify a hidden secret from a
writer's prose up to 79% of the time; "don't reveal" instructions cut leakage 20–27 points but
"active hiding" made avoidance itself detectable, and longer narrative formats leaked most
([Can You Keep a Secret?, arXiv:2605.10794](https://arxiv.org/abs/2605.10794)). **Rule form:**
secrets committed to sealed state at creation (consistency) and disclosed to the narrator only
as gated clue slices (secrecy) — §5.

**W8 — Deciding facts late; inventing unestablished details (High, High).** "If the LLM responds
with something like 'You hear a mysterious sound on the other side of the door' then if you open
the door… the LLM only decides what's on the other side of the door at that moment"
([Intra](https://ianbicking.org/blog/2025/07/intra-llm-text-adventure)). F001's DM introduced an
unestablished pronoun; F003's DM embellished a granted ability with an invented vulnerability.
**Rule form:** write-on-mention (anything described with mechanical relevance becomes a `set_fact`
at the moment of description), and literal, positive-scoped effect text (SG-15).

**W9 — Narrating changes without recording them (High, High).** Both genuine conflicts in F002
were "the DM's narration is ahead of its own tool-call record" (loot and position narrated, never
persisted) (`specs/002-long-horizon-consistency-test/implementation-results.md`). **Rule form:**
every rule's outcome section enumerates its state writes, so the narration step can be checked
against a closed list; "State touched" in the chapter template is not documentation, it is the
contract the auditor uses.

**W10 — Repetition and homogenization (Medium, High).** LLM stories echo the same plot elements
across generations *and across model families*; human plots are rarely re-created
([Echoes in AI, PNAS 2025](https://www.pnas.org/doi/10.1073/pnas.2504966122)). LLMs lag humans in
lexical and semantic diversity, most in story generation ([Benchmarking Linguistic Diversity,
TACL](https://arxiv.org/abs/2412.10271)). **Rule form:** content variety comes from engine-rolled
tables with engine-tracked "recently used" exclusion, not from asking the AI to "be varied."

**W11 — Pacing and payoffs (Medium, Medium).** LLM outlines suffer "unnatural pacing, whether
glossing over important events or over-elaborating on insignificant details"
([Improving Pacing, arXiv:2311.04459](https://arxiv.org/abs/2311.04459)); LLMs "frequently fail to
bridge long-range narrative dependencies, often leaving 'Chekhov's guns' unfired even when the
necessary context is present" ([CFPG, arXiv:2601.07033](https://arxiv.org/abs/2601.07033));
"abandoned plot elements" is a named ConStory-Bench subtype. The project's own probe hit a
soft-lock at turns 6–8. **Rule form:** foreshadowing and threats are *registered objects*
(clocks, commitments) with engine-visible state, and pacing rules fire on counters (P16) rather
than on the narrator's sense of the scene.

**W12 — Instruction decay over turns and context (High, High).** Instruction drift appears
"within eight rounds of conversations", attributed to attention decay away from the system prompt
([arXiv:2402.10962](https://arxiv.org/abs/2402.10962)). Across 200,000+ simulated conversations,
multi-turn performance averaged 39% below single-turn, driven by a +112% rise in unreliability
rather than lost aptitude; models "make assumptions in early turns… and do not recover"
([Laban et al., ICLR 2026, arXiv:2505.06120](https://arxiv.org/abs/2505.06120)). Instruction
adherence degrades as instruction count rises, with a bias toward earlier instructions
([IFScale, arXiv:2507.11538](https://arxiv.org/abs/2507.11538)); every one of 18 frontier models
degraded with input length even on simple tasks ([Context Rot, Chroma 2025](https://www.zenml.io/llmops-database/context-rot-evaluating-llm-performance-degradation-with-increasing-input-tokens)).
**Rule form:** the always-loaded rule core must be short and front-loaded; per-turn procedures
should be re-injected as a compact checklist (not relied on from turn 1); counters that trigger
rules must be engine state.

**W13 — Rule lookup, recall, and confusion (High, High).** RuleArena's three findings map
one-to-one onto rulebook authoring: (1) models rarely apply *irrelevant* rules when rules are
distinct (precision ~100% in two domains) but (2) systematically forget **"non-essential" rules
that apply only under specific conditions** — e.g. "apply either the oversize fee or the
overweight fee, whichever is higher, not both" — and (3) confuse **similar-but-distinct rules**;
and adding irrelevant but plausible rules "significantly degrades" performance while adding
equal-length meaningless text barely matters. Converting tables to "if-then" text improved recall
modestly without changing accuracy. A one-shot example helped easy problems but *hurt* harder
ones when the example was easier than the target ([arXiv:2412.08972](https://arxiv.org/abs/2412.08972)).
**Rule form:** situational rules need triggers; similar rules must be merged or sharply
differentiated; rule loading must be scoped; worked examples must span difficulty.

**W14 — Nested exceptions and precedence (High, High).** On "A is required UNLESS B applies,
UNLESS C overrides B" structures, frontier models failed *systematically* — Claude Opus 4.6 gave
zero correct answers in 70 trials on the seven failing scenarios at one snapshot; an enhanced
prompt targeting the failure cut false negatives from 7 to 4 but introduced 20 false positives,
dropping net accuracy from 90% to 65%; a deterministic engine scored 100%
([Confidently Wrong, arXiv:2607.23386](https://arxiv.org/abs/2607.23386)). **Rule form:** no
nested UNLESS in rule text; precedence is a single ordered list resolved by the engine (P6's
priority-rank companion is exactly right); "exceptions" are expressed as separate flat rules with
explicit, non-overlapping triggers.

**W15 — Long-horizon budgeting and tactics (Medium, Medium).** Frontier models won 68–83% of
single D&D encounters but cleared at most 2 of 5 linked "days" of encounters, failing on
"resource budgeting, rest timing, and rule-aware tactical discipline"
([DungeonBench, arXiv:2607.29577](https://arxiv.org/html/2607.29577)). This bears on
*adversary* play (the DM playing monsters) and on attrition design: the DM will not reliably
pace enemy resources across a long fight or a day. **Rule form:** adversary behavior uses
priority lists and morale thresholds (§9 ch. 09), and attrition/resource pacing is engine-tracked.

**W16 — Over-copying examples (Medium, Medium).** LLM output distributions "cluster around the
examples" provided ([arXiv:2509.06337](https://arxiv.org/abs/2509.06337)); excessive examples
reduce generalization ([Few-shot Dilemma, arXiv:2509.13196](https://arxiv.org/abs/2509.13196));
RuleArena's easier-than-target example hurt. Yet few-shot examples in prompts and tool
descriptions were what made the agentic GM consistent in the Static-vs-Agentic study
([arXiv:2502.19519](https://arxiv.org/abs/2502.19519)), and a practitioner's top advice was
"include examples, **and** non-examples" ([EN World](https://www.enworld.org/threads/llms-as-a-gm.714126/)).
**Rule form:** worked examples are for *adjudication boundaries* (both sides of every line, plus
a non-example), deliberately varied in surface content and difficulty; they are not prose models,
and generative prompts should not carry sample narration the model will imitate.

**W17 — Silent model drift (Medium, Medium).** Failure cells "closed silently under the same
model alias, with no version bump" between March and April 2026
([arXiv:2607.23386](https://arxiv.org/abs/2607.23386)). A rule whose correctness depends on a
specific model's quirks is not a stable rule. **Rule form:** anything that must behave identically
on the thousandth use across model updates is `[D]`; `[J]` rules carry boundary examples that
double as a regression suite (§12).

### 3.4 This project's own evidence, re-analysed

The three results files were read in full; in addition, R4 re-tallied the raw Feature 002 logs
(`specs/002-long-horizon-consistency-test/t021_*.log`, all 63 unique `roll_check` calls made by
`gemini-3.8-flash` across the runs). The system prompt offered "a DC that fits the fiction
(10=easy, 15=moderate, 20=hard, 25=very hard)" and a tool schema with a required integer
`modifier` "added to the raw d20 roll" and no stat source (`src/dm_agent.py`, `src/tools.py`).

| Measure | Result | What it shows |
|---|---|---|
| DCs on the stated ladder (10/15/20/25) | 56/63 (89%) | The ladder mostly works as an anchor… |
| Off-ladder DCs | 7/63 (11%): 11 ×1, 12 ×3, 13 ×2, 14 ×1 | …but a free integer invites interpolation; every off-ladder pick fell between "easy" and "moderate" — a softened "moderate" (weakly consistent with W2 leniency; n is small) |
| DC distribution | 10: 15, 15: 27, 20: 8, 25: 6 | Heavy central tendency on "moderate" (43%) — consistent with the central-tendency bias of LLM ordinal judgments |
| Model-supplied modifier | 0: 39 (62%), +1: 14, +2: 2, +3: 8 | An unanchored numeric slot is filled arbitrarily; the project default (+2) was almost never used |
| Degrees | CF 16 (25%), F 24, S 20, CS 3 (5%) | The ±10 critical band at modifier ~0 makes critical failure 5× as common as critical success |
| F001 (relayed Haiku session) | 3/10 DCs off-ladder (16, 17, 16) | Same drift on a different model family |

Two conclusions follow. First, **free numeric parameters are the leak** (W5): the fix is to make
`dc` and `modifier` not model-supplied integers at all (R-01, R-02). Second, the degree table
itself interacts with AI behaviour: under the current resolution rule, the outcome distribution
for a baseline character is heavily weighted toward critical failure on anything above
"moderate":

| Modifier | DC 10 | DC 15 | DC 20 | DC 25 |
|---|---|---|---|---|
| +0 | CS 5 / S 50 / F 40 / **CF 5** | CS 5 / S 25 / F 45 / **CF 25** | CS 5 / S 0 / F 45 / **CF 50** | CS 5 / S 0 / F 20 / **CF 75** |
| +2 (default) | CS 15 / S 50 / F 30 / CF 5 | CS 5 / S 35 / F 45 / **CF 15** | CS 5 / S 10 / F 45 / **CF 40** | CS 5 / S 0 / F 30 / **CF 65** |
| +5 | CS 30 / S 50 / F 15 / CF 5 | CS 5 / S 50 / F 40 / CF 5 | CS 5 / S 25 / F 45 / CF 25 | CS 5 / S 0 / F 45 / CF 50 |

(Percentages, computed exhaustively over d20 faces in a scratchpad script; CS = total ≥ DC+10 or
nat 20, CF = total ≤ DC−10 or nat 1.) At the default +2, a "hard" task is a critical failure 40%
of the time and succeeds (any kind) 15% of the time. This matters for AI design specifically:
**if consequence tables are to be applied by the engine without narrator softening (§6), the base
rates must be ones the designers are willing to see enforced every time.** If a DM that faithfully
applies these numbers would feel brutal, the model will (per W3) quietly soften them — and at that
point the rulebook has taught the AI that rules are negotiable. This is flagged to the resolution
author (§11).

Other project findings used throughout: F001's clean degree-following (S8); the soft-lock (W11,
P16); the compound-question all-or-nothing issue (P17); the unearned pronoun that the model's own
self-audit missed (W8); F002's narrated-not-recorded conflicts (W9); F003's 6/6 classification
(S1) and invented vulnerability from negative-space text (W8, SG-15); and F003's test-design
lesson that a scripted "I kill it" is an *intent*, which the DM correctly resolved by rolling —
the same principle as §7's "player text is intent, never outcome."

---

## 4. Rule-form reliability guide (proposed authoring style guide)

This section is written to be adopted, nearly verbatim, as the style-guide section of
`00-architecture.md`. It converts §3 into rules *for writing rules*.

### 4.1 The two governing principles

**P-A: Put every judgment in its most reliable form.** For each decision a rule requires, ask in
order: can the engine compute it (`[D]`)? If not, can it be a yes/no fact question (`[J:flag]`)?
If not, a choice from a small closed set with definitions (`[J:enum]`)? If not, a rung on a
short anchored ladder (`[J:rung]`)? Only if none of these fit is it open judgment (`[J:open]`).
The evidence ordering: binary ≈ 87% exact agreement; well-defined closed-set classification
~94–97% (CoC-Seduce neutral condition; wrong-skill ~6% over 16 options); ordinal 38–58% exact /
85–93% adjacent; open judgment unmeasured but exposed to all of W2/W3/W5
([Autorubric](https://arxiv.org/abs/2603.00077); [CoC-Seduce](https://arxiv.org/abs/2607.02802)).

**P-B: Bound the blast radius of every judgment.** Every `[J]` rule states, in its text, the
largest mechanical effect a wrong call can produce, and that effect must be one of: (i) one rung
/ one step / one tick; (ii) an *offer* the player can decline rather than a grant; (iii)
self-correcting as more evidence accumulates (P5's grant/offer/abstain already is); or (iv)
reversible by a named later procedure. A `[J:open]` rule whose error could kill a character,
grant a permanent ability, or reveal a sealed secret is a defect. **[inference, grounded in the
measured error rates of W2/W5 and in P5's own self-correction rationale]**

### 4.2 A refined rule-kind taxonomy (replaces the brief's three kinds)

The brief's `[D]/[J]/[N]` is right but too coarse: `[J]` lumps together the most reliable AI
operation (classification) and the least reliable (free judgment). Proposed:

| Tag | Meaning | Expected reliability | Required in rule text |
|---|---|---|---|
| `[D]` | Engine computes / stores / rolls. AI supplies only typed inputs. | Exact (given correct inputs) | Inputs, formula/table, state writes |
| `[J:flag]` | AI answers a yes/no question about established facts. | Highest AI form (~87%+) | "True only when…"; ≥1 example each side |
| `[J:enum]` | AI classifies into a closed set (≤ ~8 options). | High (single-digit % error with good definitions) | Every option defined with inclusions *and* exclusions; tie-break rule; default when uncertain |
| `[J:rung]` | AI picks a rung on a 3–5-rung ordinal ladder with anchors. | Adjacent-reliable; expect ±1-rung disagreement | Anchor description + 2 examples per rung; design must tolerate a one-rung error |
| `[J:open]` | Free judgment (e.g., "does this moment count as evidence?"). | Least reliable; lenient/positive-biased | Explicit blast-radius cap (P-B); offer/abstain shape where possible; precedent logging |
| `[N]` | Narration with no mechanical weight. | High for prose; risk is *implied* mechanics | What the narration may *not* imply (closed list of state it must not change) |

Two further tags are useful for the auditor and for chapter authors:

- `[T]` **trigger** — a condition on tracked state that the engine raises (e.g., "Vitality ≤ ⅓
  max", "3 consecutive inconclusive resolutions", "clock filled"). Triggers are what keep
  situational rules from being forgotten (W13).
- `[S]` **sealed** — state the narrator does not see until a gate opens (hidden stats, mystery
  solutions, NPC secrets). See §5.

### 4.3 Form-by-form reliability table

| Rule form | Reliability for an LLM DM | Evidence | Use it for | Don't use it for |
|---|---|---|---|---|
| **Tool computation** (sums, stacking, recharge, thresholds) | Exact | RuleArena oracle-tool boost; RPGBench MEC decay without tools; F001/F002 | All arithmetic; all "higher of / sum of / cap at"; all recharge enforcement (P5 already mandates) | — |
| **Engine-rolled table / oracle** | Exact randomness; AI interprets | Bad-dice-players; Mythic practice; Story-Engine chaos/proactivity engines | Random events, rumors, loot fill, NPC initiative, "is X here?" questions not yet established | Anything already established as fact (never re-roll a fact) |
| **Binary fact flag** | Very high | Autorubric 87% binary | Circumstance modifiers; eligibility checks; "is this licensed?" | Graded quantities (use rung) |
| **Closed enum with definitions** | High | CoC-Seduce neutral 3.82%; F003 6/6; Story-Engine enums | Approach/attribute, challenge type, harm mode, social tactic, tag_event tags, consequence type | Sets > ~8–10 options without hierarchy; overlapping categories |
| **Lookup table keyed by enums** (e.g., degree × stakes → consequence) | High (lookup is `[D]` once keys are chosen) | P8; RuleArena "tables vs if-then" mild effect | Consequences, loot quality, injury, reaction outcomes | Tables the AI must cross-index mentally with 3+ keys (make it a tool) |
| **Explicit trigger on state** (`[T]`) | High if engine-raised; low if memory-raised | RuleArena non-essential rules forgotten; instruction drift within 8 rounds | Dying state, P16 soft-lock breaker, morale, clock completion, recharge | Triggers defined on narration mood ("when tension feels high") |
| **Clock (segment counter)** | High (counter is `[D]`; tick triggers `[J:enum]`) | Blades clocks as tick-on-consequence ([bladesinthedark.com](https://bladesinthedark.com/progress-clocks)); W11/W12 | Threats, factions, extended tasks, pursuit, rituals, alarms, foreshadowing | Clocks whose tick amount the AI picks freely (fix per trigger: 1/2/3 by consequence tier) |
| **Anchored ordinal ladder (3–5 rungs)** | Adjacent-reliable | Autorubric; F002 DC distribution | Obstacle tier, threat band, likelihood rung, consequence severity tier | Anything where a one-rung error is catastrophic; ladders > 5 rungs |
| **Ordered decision list (first match wins)** | Good if flat and short; best if engine-evaluated | Exception chain collapse (nested form fails); P6 priority ranks | Precedence among effects, adversary behavior priorities, action legality | Nested "unless" chains; lists > ~7 items evaluated in-head |
| **Hierarchical tag cascade** | Exact once tags assigned (`[D]` cascade) | P5 sixth pass; PoE tag cascade | Evidence tallies, class recognition, loot pool gating | Tag *assignment* by open judgment without definitions |
| **Narrow prose permission** (P10 move) | High if trigger and outcome are closed and literal | P10; F003 embellishment failure | Abilities, traits, special capabilities | Permissions with open-ended outcomes ("you may do something cool with fire") |
| **Holistic "fits the fiction" judgment** | Lowest; lenient- and positive-biased | W2, W3, W5 | Only where no decomposition exists; always with blast-radius cap | Difficulty, success, rewards, death, secrets |

### 4.4 The style rules

Each is phrased as an instruction to chapter authors, with its evidence.

**SG-01 — No free numbers from the AI.** No rule may ask the AI to "choose a DC", "set the
damage", "decide the duration", "pick the odds". The AI picks rungs, flags, and enums; a table or
tool produces the number. *Evidence:* F002 11% off-ladder DCs and 62% arbitrary modifiers (§3.4);
Autorubric ordinal exact agreement 38–58%.

**SG-02 — Ladders have at most five rungs, each with an anchor sentence and two examples** (one
typical, one near the boundary), and the rule states what a one-rung misjudgment costs. *Evidence:*
"narrow scales (3–5 levels) with clear behavioral anchors" (Autorubric); central tendency in F002
(43% of DCs at "moderate").

**SG-03 — Decompose graded judgments into binary flags where possible.** Instead of "how hard is
this, considering everything?", ask "Is the character trained in this approach? Is there active
opposition? Is there time pressure? Is the environment hostile? Does an established fact or tool
help?" — each `[J:flag]`, each worth a fixed shift, summed by the tool with a cap. *Evidence:*
binary > ordinal reliability; RuleArena shows models apply relevant, distinct rules with high
precision but miss conditional ones — flags turn conditions into explicit questions.

**SG-04 — Every enum option has inclusions, exclusions, and a default.** Write each option as
"True only when… False for…" and state which option to choose when uncertain. *Evidence:* the
Story-Engine contract is written exactly this way after 500+ iterations (e.g., teamwork: "True
only for coordinated effort together under meaningful pressure… Ordinary safe collaboration is
cooperation"; "Uncertain = N/default") ([Story-Engine](https://github.com/ZDOSt/Story-Engine)).

**SG-05 — Default uncertainty toward the check, not toward success.** Where a rule asks "does
this need resolution?", the tie-break is "yes." *Evidence:* false-check rate 0.08% vs false-pass
9.58% (CoC-Seduce) — the AI almost never over-rolls, so pushing toward rolling corrects the only
error it actually makes.

**SG-06 — Player text is intent and method, never fact or outcome.** Rules must say explicitly
that a player's description of *why* something works or *that* it succeeded creates no fact and
no modifier; only established facts, licenses, and observable scene features (each with an ID)
do. Internal monologue, flavor, and asserted results are context only. *Evidence:* pseudo-logic
×4.5 failure rate (CoC-Seduce); invented "GPS evidence" confession (SKT paper); Intra's rewriting
of "Marta and Ama get into a disagreement" into an *attempted* provocation; Story-Engine's
PLAYER_TEXT rule ("thought-only prose… do[es] not create actions, targets, rolls… or scene facts").

**SG-07 — Licenses are cited by ID.** Principle VII's gate is only auditable if the DM must name
the license: an ability id, a class-capability id, a fact id, or the basic-action id. No ID →
redirect to the nearest basic action. *Evidence:* Story-Engine: "Available=Y only if that
ability/spell exists in active character/persona/lore/context"; "Rare, valuable, magical,
specialized… items require an authoritative saved source."

**SG-08 — Declare stakes before the roll.** Every rolled resolution records, *before* the tool
rolls: intent, approach, success outcome, failure outcome, consequence tier, and what state each
outcome writes. The roll tool should refuse to roll without them. *Evidence:* Intra: "commit to
some conclusion… Try to take on a neutral perspective when defining things like success or failure
(in part by committing to those results early)"; the Multihog framework's commitment-based rolls
require the AI to "declare a DC before seeing the result, completely preventing sycophancy"
(practitioner claim, not measured) ([Multihog](https://github.com/MultihogAurelius/SillyTavern-MultihogDnDFramework)).

**SG-09 — Consequences come from tables, keyed by degree × stakes tier, applied by the engine.**
The narrator chooses *which* fictional form an entry takes (from the entry's allowed forms), not
*whether* it happens or *how big* it is. *Evidence:* W3; Voyage's "a bad roll is a bad result."

**SG-10 — No nested exceptions. Use flat rules with non-overlapping triggers, or a single ordered
first-match list, or engine code.** "X, unless Y, unless Z" is forbidden in rule text. Stacking
and precedence ("take the higher", "the most specific effect wins") are `[D]`. *Evidence:*
exception chain collapse; RuleArena's most-forgotten rule was a higher-of-two clause.

**SG-11 — Every conditional rule names its trigger as tracked state.** If a rule applies "when the
character is exhausted", "exhausted" must be a status flag the engine can surface; the DM's
per-turn packet lists every rule whose trigger is currently true. *Evidence:* RuleArena
non-essential-rule neglect; instruction drift (W12).

**SG-12 — Randomness is engine-rolled; the AI interprets.** Any rule that needs variety ("an
unexpected complication", "what the rumor is", "who answers the door") rolls on a table; the AI
turns the result into fiction. Tables track recent results to prevent repeats. *Evidence:* W6,
W10, S4.

**SG-13 — Write-on-mention.** When narration introduces anything that could later matter
mechanically (a door's state, an NPC's presence, an item, a hazard, a sound's source), it is
recorded as a fact in the same turn, rolled on a table if not already determined. *Evidence:*
Intra's door problem; F002 narrated-not-recorded conflicts.

**SG-14 — Every rule's outcome section enumerates its state writes** in a closed list, so the
auditor can check narration against it and the narrator knows what it must not imply beyond it.
*Evidence:* F002 (W9); F003 embellishment.

**SG-15 — Effect text is positive-scoped and literal.** State what an effect *does* and *applies
to*; never describe it by what it lacks ("offers no protection against cold"), never use
figurative language inside a mechanical clause, and add an explicit "Does not:" line only for
confusions actually observed. *Evidence:* F003: "no protection against cold" became an invented
cold vulnerability.

**SG-16 — Merge or sharply differentiate similar rules.** Two rules that cover overlapping
situations with different outcomes (e.g., "shove" vs "grapple" vs "trip") must each carry a
distinguishing test the AI can check ("Does the actor keep hold? → grapple; target moved away →
shove"). *Evidence:* RuleArena's lowest-precision rules were substitutable ones with "alternatives
applicable under different conditions."

**SG-17 — Worked examples are boundary pairs plus a non-example, varied in surface content and
difficulty.** Each `[J]` rule gets at least one case just inside and one just outside each
boundary, and one tempting non-example (e.g., a persuasive-but-unlicensed attempt). Examples use
different settings, characters, and phrasing so the model learns the boundary, not the surface.
*Evidence:* W16; the EN World "examples and non-examples" advice; RuleArena's easier-example
degradation.

**SG-18 — Rules load by situation.** Each rule declares the situation classes in which it is
relevant (e.g., `conflict`, `social`, `travel`, `downtime`, `investigation`), so a turn loads the
always-on core plus the relevant chapter cards. *Evidence:* RuleArena distractor effect (irrelevant
plausible rules hurt far more than noise); IFScale; Context Rot.

**SG-19 — Counters, not recollection.** Anything counted over turns (inconclusive results, uses
per scene, days of travel, reputation shifts, clock ticks, tag evidence) is engine state.
*Evidence:* W12, W1; the P16 soft-lock.

**SG-20 — Improvised rulings become precedents.** When the DM adjudicates something no rule
covers, it records the ruling as a precedent entry (situation → anchor rule used → adaptation →
outcome), and later identical situations consult it. *Evidence:* behavioral inconsistency across
identical runs (2.3–4.2 distinct sequences per 10: [arXiv:2602.11619](https://arxiv.org/html/2602.11619v2));
S6. This also creates the "recorded concrete failure case" Principle III's revisit trigger needs.

### 4.5 A rule template that bakes the guide in

```
### CC.S.R  <Rule name>                           [J:rung]  (kinds: one per decision)
Trigger [T]:      <tracked condition or player-intent class that invokes this rule>
Loads in:         <situation classes>
License check:    <which license ids make the attempt legal, or "basic action: <id>">
Decisions:
  1. <decision>  [J:enum] options: A (true only when… false for…) | B (…) | default: A
  2. <decision>  [J:flag] "True only when…"
  3. <decision>  [J:rung] rungs 1–4 with anchors (see table CC.x)
Computation [D]:  <formula / table lookup the tool performs>
Stakes (declared before roll): success → …; failure → …; consequence tier → table CC.y
State writes:     <closed list>
Narration may not imply: <closed list>
Blast radius:     <largest effect of a wrong judgment> (must satisfy P-B)
Examples:         inside / outside each boundary, + one non-example
Anchors for adaptation: <which novel situations may reach for this rule, and the permitted adaptation>
Basis:            [C:…] [R:…] [DL-…]
```

### 4.6 Worked rewrite: "setting a DC"

**Current form (from `src/dm_agent.py` and brief §7):** "call roll_check with a DC that fits the
fiction (10=easy, 15=moderate, 20=hard, 25=very hard)", with `dc` and `modifier` free integers.

Failure modes observed: 11% off-ladder (F002), 30% off-ladder (F001), 43% central clustering,
arbitrary modifiers (62% zero), and — by W2 — a DC that bends to the player's framing.

**Rewritten form (illustrative numbers; chapter 01 owns the real ones):**

1. `[J:enum]` **Approach** — which attribute the attempt uses, via the chapter-01 approach→attribute
   table (e.g., force / finesse / endurance / perception / knowledge / presence / will …). Default
   when uncertain: the approach the player *named*; tie between two → the lower-rated attribute
   (anti-leniency tie-break, SG-05 spirit).
2. `[J:rung]` **Obstacle tier** from concrete scene facts only — "do not adjust for drama or the
   character's stats" (Story-Engine's `environmentDifficultyTier` rule, verbatim in spirit):
   *routine* (no roll) / *easy* / *moderate* / *hard* / *extreme*. Two anchors each.
3. `[J:flag]` × 4–6 **circumstances**, each "true only when" an established fact or observable
   scene feature supports it, each citing a fact/licence ID: *active opposition*, *time pressure*,
   *hostile environment*, *helpful established resource*, *favorable position established by a
   prior success*, *creative approach credit* (§7).
4. `[D]` Tool computes: DC = tier base; + fixed shift per true hindering flag; − fixed shift per
   true helping flag; total flag shift capped at one tier's width. Modifier = attribute + trained
   bonus from state. The AI supplies no integer.

Blast radius: a one-rung tier error or one wrong flag moves the DC by at most one tier-width; a
seduced "creative credit" flag moves it by one fixed step. Both are logged with their cited IDs,
so the auditor can check "flag true, but no fact ID supports it."

**Worked example.** Player: "The guard's back is to me and the torch has guttered — I slip the
ring of keys off his belt. Since he's half asleep it should be easy."
- License: basic action `take_object` (no ability needed) → legal.
- Approach `[J:enum]`: finesse (sleight). Tier `[J:rung]`: moderate (a capable person could
  plausibly fail: object attached to a person). The player's "it should be easy" is SG-06 context
  only — it moves nothing.
- Flags: *opposition* — true (the guard is a living detector, fact `npc_guard_07.present`);
  *time pressure* — false; *hostile environment* — false; *helpful resource* — true: darkness,
  but only if `scene.light = dim` is an established fact (it is: the DM narrated the guttered torch
  last turn and SG-13 recorded it as `scene_12.light=dim`); *half asleep* — the DM did not
  establish drowsiness; the player asserted it → not a fact → no flag. (If the DM had narrated
  "the guard nods off", that narration would have written `npc_guard_07.status=drowsy` and the
  flag would apply.)
- Tool: moderate base + opposition shift − darkness shift → net DC equals the moderate base;
  modifier from the character's finesse attribute. Stakes declared: success → keys taken
  unnoticed (writes `possession: keys_guard_07`); failure → guard stirs, clock "Alarm" +1 (writes
  `clock.alarm += 1`); critical failure → caught in the act (consequence table row
  "discovered, hands on the object").

---

## 5. Hidden information and fairness

### 5.1 What the evidence says

- **Consistency requires committed private state.** Formal result plus experiment: agents limited
  to public history cannot be both secret and consistent; a private working-memory block (under
  ~100 tokens) raised Hangman self-consistency from 2–12% to 76–100%; semantic-retrieval memory
  systems (Mem0 etc.) did *no better than vanilla* ([arXiv:2601.06973](https://arxiv.org/abs/2601.06973)).
- **Secrecy fails when the secret is in the narrator's context.** Involuntary thematic leakage up
  to 79%; "don't reveal" helps 20–27 points; conspicuous avoidance also leaks; long narrative
  prose leaks most ([arXiv:2605.10794](https://arxiv.org/abs/2605.10794)). Even a small local NPC
  model leaked a guarded secret to 3 of 30 hand-built extraction prompts (10%)
  ([arXiv:2508.19288](https://arxiv.org/abs/2508.19288)).
- **Gated disclosure works, at a naturalness cost.** The Structured Knowledge Tree detective game
  gated each clue node behind prerequisites, generated dialogue only from approved nodes, and
  verified the output before updating state: premature confessions fell from 10/33 players to
  0/33 and hallucinations from 17.80% to 6.27% of responses; the cost was occasional "revealed
  information that seemed to come out of nowhere" when a forced reveal lacked conversational
  relevance ([arXiv:2609.23043](https://arxiv.org/abs/2609.23043)).

### 5.2 Rule-design consequences

1. **Seal at creation.** Mystery solutions, NPC secrets and motives, trap placements, adversary
   exact stats, hidden loot, and faction plans are written to `[S]` sealed state *when the
   situation is generated*, before the player can probe them. Never "decide later."
2. **Narrate from permitted slices.** The narrator's per-turn packet contains only (a) unsealed
   facts and (b) the specific clue nodes the resolution just unlocked. Sealed facts are used by the
   engine (e.g., to compute an adversary's defense) without being shown as text. For adversaries,
   the narrator gets a *tells* list per threat band ("moves like a veteran", "the blade barely
   bothers it") rather than numbers.
3. **Clue graphs, not clue prose.** Investigation content is authored as nodes with prerequisites
   and multiple access routes (Alexandrian three-clue principle, already in the project's DM-craft
   research), so P17's graduated reveal becomes "degree → number of nodes unlocked from the
   eligible set" — computable (`[D]` count, `[J:enum]` which nodes favoring relevance). The SKT
   naturalness cost is mitigated by letting the narrator pick *which* eligible node fits the
   question (the relevance judgment it is good at), rather than forcing a fixed next node.
4. **Fairness = the player could have known.** Because gated clues are state, the auditor can
   verify that any sealed fact the plot turns on had at least N unlocked clue nodes before it
   mattered — an objective fairness check an LLM DM cannot provide by self-report (F001 showed
   self-report misses things).
5. **Use leakage deliberately.** The same leakage that breaks secrecy can be harnessed as
   foreshadowing: a sealed fact may be given to the narrator *as an atmosphere tag* ("theme:
   betrayal by kin") without the fact itself, letting thematic traces appear without disclosure.
   **[inference from arXiv:2605.10794's thematic-trace finding and its decoy-redirection result]**

---

## 6. Difficulty, failure, and lethality

### 6.1 The problem, precisely

Three forces combine: preference-trained leniency (W2), narrative positivity (W3), and the
constitution's own locked lethality decision ("death is real but telegraphed"). The risk is not
that the AI kills characters capriciously — the evidence says the opposite — but that it **never
follows through**: warnings are issued, the player ignores them, and the consequence evaporates.
AI Dungeon's decade and the EN World "barely failed any check" report are the failure; Voyage's
engine-owned HP and permadeath are the successful counter-design.

### 6.2 Counter-mechanisms, ranked by evidence

1. **Engine-owned consequence application** (strongest; Voyage, Story-Engine, Multihog). The
   engine applies Vitality loss, conditions, clock ticks, and state transitions from the
   degree × stakes table; the narrator describes them. The narrator has no tool that undoes them.
2. **Pre-committed stakes** (SG-08). Commitment before the roll removes the post-hoc softening
   channel (Intra; Multihog).
3. **Threat actors driven by engine processes.** Adversary intent, NPC proactivity, and faction
   moves come from rolled/priority-listed behavior (Story-Engine's proactivity die with tiered
   thresholds; its combat/aggression outcomes are pure margin functions), not from a narrator
   that would rather be nice.
4. **Declared warning state machine for death.** Telegraphing should be a state, not a tone:
   `safe → warned(lethal_risk=source) → dying → last_chance → dead/defeated`. The *warning* is a
   required `[T]`-triggered narration when a lethal source enters play (so it is never forgotten),
   and once a character is `warned` and chooses to continue, the dying/death transitions are `[D]`.
   This satisfies the locked decision (never death without warning; a single roll never ends a
   character) while making follow-through mechanical. The last-chance choice is a `[J:enum]`
   *offered to the player*, not a DM mercy decision.
5. **Defeat outcomes table.** Since "defeat usually means capture, injury, loss, or a changed
   situation", those outcomes should be a rolled/selected table keyed to the adversary's goals
   (captors want prisoners; beasts want food; zealots want sacrifice). The AI chooses the fiction
   within the rolled row. This avoids the positivity failure mode where "defeat" silently becomes
   "a lucky escape."
6. **Calibrate base rates to what you are willing to enforce** (§3.4). If the table says 40% of
   hard checks are critical failures, and critical failure maps to severe consequences, the
   engine will deliver that. Designers — not the narrator — must own that choice.

### 6.3 Difficulty calibration without levels

Because the project has no character level (P2), the AI cannot calibrate by "CR vs level." The
evidence-backed approach is: threat bands as a `[J:rung]` of at most five rungs classified *from
the adversary's nature* (Story-Engine's `common / trained / elite / boss` with the explicit guard
"never use boss from title, location, hostility, or dramatic importance alone"), with the engine
comparing the band to the character's current capability summary to produce an *advisory*
("this fight is likely lethal") that feeds the warning state machine. The AI does not tune
encounters on the fly to the player's current HP — that is exactly where leniency would enter.

---

## 7. Letting players try anything while staying fair (goal 1)

The published literature on fair adjudication of novel actions is still thin (the prior DM-craft
report found nothing directly; CoC-Seduce is the first controlled adjudication benchmark and it
covers roll/no-roll only, deliberately excluding social skills). What exists points to a pipeline
in which the AI's interpretive strength is used maximally and its leniency is fenced:

**7.1 The creative-action pipeline** (each step's form in brackets):

1. **Parse** intent and method; separate asserted outcomes and justifications as context (SG-06)
   `[J:enum]` + extraction. If intent is ambiguous in a way that changes resolution, ask one
   clarifying question — models otherwise "make assumptions in early turns… and do not recover"
   ([Laban et al.](https://arxiv.org/abs/2505.06120)).
2. **Gate** (Principle VII): cite a license ID or the basic action. No ID → redirect to the
   nearest basic action *and say what would license it* (P16: never a dead end) `[J:enum]`.
3. **Anchor**: pick the nearest rule from the anchor index (the "basically a grapple" move),
   `[J:enum]` over a closed list of anchor IDs, with the permitted adaptations that anchor
   declares (SG template "Anchors for adaptation").
4. **Adapt within bounds**: allowed deltas are enumerated — one obstacle rung, one circumstance
   flag, swap the attribute via the approach table, add or remove one consequence row. Anything
   larger is a new rule and goes to the precedent log for review, resolving now with the
   un-adapted anchor.
5. **Creative credit**: a clever use of *established* fiction (terrain, an item, an NPC's stated
   weakness, a previous success) earns one bounded benefit — one flag worth a fixed shift, or an
   advantage-type step, or access to a better approach — never automatic success. `[J:flag]`,
   cited to the fact ID it uses.
6. **Declare stakes** (SG-08) → **roll** `[D]` → **consequence table** `[D]` → **narrate** `[N]`
   → **write state** (SG-14) → **log precedent** if steps 3–4 adapted anything (SG-20).

**7.2 Why this keeps goal 1 alive.** Nothing in the pipeline refuses an idea for being unusual —
the anchor index is broad (P3's rich substrate), the adaptation menu gives every idea a
mechanical handle, and the creative-credit flag guarantees that *using the fiction* is always
worth something. What the pipeline refuses is converting rhetoric into success. The reward is
capped because the evidence says the AI will sometimes be seduced (≈17% of pseudo-logical framings
on average in CoC-Seduce); a capped reward means a seduced judgment costs one step, not the scene.

**7.3 Why this matters for perceived fairness.** The one player-experience finding on AI GMs
reframes fairness as locus of control: AI was accepted "when it expanded valued play experiences,
but problematic when it appeared to take over judgment, authorship, or player choice"
([arXiv:2502.19519](https://arxiv.org/abs/2502.19519)). Voyage's reviewer framed the trade as "a
skill check can refuse you, and a refusal is a small loss of authorship in exchange for a stake"
([Arcanum](https://arcanumrpgs.com/blog/voyage-vs-ai-dungeon/)). Visible, pre-declared stakes and
visible rolls make refusals legible as *the game*, not the DM's whim. **Recommendation:** the
player sees the declared stakes and the roll (out of fiction, codex-style, consistent with the
locked "no diegetic System" decision — this is the character-sheet layer, not an in-world blue box).

**7.4 Worked example — a genuinely novel action.**
Player (character has no fire abilities; scene facts: `scene_31.floor=oil_slick` from an earlier
spilled lamp, `npc_ogre_02.position=on_slick`, character holds `item_torch_01`): "I kick the torch
onto the oil the ogre's standing in, then shout a challenge so it charges through the flames."
- Gate: `throw_object` basic action (licensed by holding the torch) — legal. The shout is `talk`,
  also basic. The *charge* is the ogre's decision, not the player's — SG-06: player text cannot
  decide an NPC's action; it becomes a social attempt to provoke.
- Anchor: ignite hazard → nearest anchor "create environmental hazard" (chapter 10). Provoke →
  "social: taunt" (chapter 10), resolved against the ogre's disposition.
- Creative credit: true — uses two established facts (`oil_slick`, `torch_01`). Benefit: the
  ignition needs no roll beyond a routine throw (tier: easy) and the hazard uses the anchor's
  "established fuel" row (bigger fire).
- Stakes declared: ignition success → `scene_31.hazard=fire(intensity: established-fuel row)`,
  ogre takes hazard damage per the table at start of its turn; failure → torch lands short,
  small fire, no slick ignition. Taunt: success → ogre's behavior priority list is overridden to
  "charge the taunter" this round; failure → the ogre follows its normal priority (e.g., "flee
  fire, then ranged").
- Both resolved; results applied by the engine; the ogre's charge through flames (if it happens)
  is the table result, not the narrator's generosity.

---

## 8. Model tiers: frontier vs flash, and a cost-appropriate mix

**Evidence.**
- *Adjudication (roll/no-roll under rhetorical pressure):* cost tier did not predict robustness.
  Lowest overall failure rate: DeepSeek-V3.2 (2.47%); Gemini 3 Flash 4.67%; Gemini 3.5 Flash
  6.49%; Claude Sonnet 4.5 3.39%; GPT-5.4 18.17%; reasoning-enhanced DeepSeek-R1 16.48%
  ([arXiv:2607.02802](https://arxiv.org/abs/2607.02802)).
- *Long-horizon narrative consistency:* tier and family matter a lot — best model survived 32.9
  turns on average under adversarial play vs under 8 for a fast model (see project report on
  NCP-Bench). *Tactical play:* frontier models win most single encounters but struggle with linked
  resource-budgeted days ([DungeonBench](https://arxiv.org/html/2607.29577)). In D&D Agents, a
  small fast model (Claude 3.5 Haiku) was the "most reliable" of those tested
  ([PsyPost](https://www.psypost.org/researchers-are-using-dungeons-dragons-to-find-the-breaking-points-of-major-ai-models/)).
- *Long-context retrieval:* flash can beat pro at long lengths (reported MRCR v2 8-needle: Gemini
  3 Flash 58.5% vs 3 Pro 45.4% at 256K) ([Vellum summary](https://www.vellum.ai/blog/google-gemini-3-benchmarks);
  vendor-reported, Medium confidence).
- *Reasoning ≠ robustness:* reasoning models offered "no consistent advantage" in CoC-Seduce; in
  the exception-chain study a reasoning-effort setting changed behavior unpredictably; a D&D
  command-generation study found instruct models "sufficient… compared to reasoning models" and
  that "even single sentence changes in prompts can greatly affect the output"
  ([arXiv:2510.18112](https://arxiv.org/abs/2510.18112)).
- *Practitioner mix:* Story-Engine runs its classification ("semantic ledger") pass on a separate
  "fast, cheap model" and narrates with the main model ([Story-Engine](https://github.com/ZDOSt/Story-Engine));
  the Static-vs-Agentic GM study's split of narrator and archivist agents improved coherence
  (1.00 → 2.25), immersion and control significantly ([arXiv:2502.19519](https://arxiv.org/abs/2502.19519)).

**Conclusion for rule design.** A flash-tier model is adequate for the AI's rule-facing jobs
*if the rules are written in the forms of §4* — classification, flags, rungs, narration of
resolved packets. Frontier capacity buys most where the rules cannot externalize the work:
long-horizon coherence of prose and generative world simulation. Therefore:

| Job | Recommended tier | Why |
|---|---|---|
| Adjudication pass (parse, gate, anchor, approach, tier, flags, stakes) — structured output, low temperature | Flash tier; family chosen by a CoC-Seduce-style test on *this* ruleset | Closed-form tasks; family effects dominate tier effects |
| Narration pass (prose from resolved packet + permitted slices) | Flash default; frontier optional for "prestige" scenes | S8; narration is where frontier prose quality shows |
| Between-session world turn (faction clocks, hooks, rumors) | Frontier or reasoning, offline | Generative planning; latency irrelevant; outputs still pass through tables |
| Content authoring (encounter/clue graphs, NPC sealed state at generation) | Frontier, offline, then validated | One-time cost amortized; validated like data |
| Audit / consistency check | Different family from narrator (P13), flash tier | Closed checklist against SG-14 state-write lists |

This is compatible with Principle I: the AI DM is still the engine — the adjudication pass *is*
the DM making its ruling, just in a structured step before it writes prose, so that the ruling is
not made by the same generation that is being "seduced by the narrative."

---

## 9. Per-chapter implications (chapters 00–14)

Each item is a concrete recommendation with its reason. "Tag" = the rule-kind the item should
carry under §4.2.

### 00 — Architecture

1. **Adopt §4 as the authoring style guide**, including the refined kinds `[D] [J:flag] [J:enum]
   [J:rung] [J:open] [N]` plus `[T]` triggers and `[S]` sealed state, the P-B blast-radius
   requirement, and the rule template (§4.5). Reason: the brief's `[J]` hides a 10× reliability
   spread.
2. **Define the resolution packet schema** — the typed object the adjudication step produces and
   the narration step consumes: `intent, method, license_id, anchor_id, approach, tier, flags[]
   (each with fact_id), stakes{success, failure, consequence_tier}, state_writes[], roll, degree,
   consequence_row`. Every chapter's rules must be expressible as fields of it. Reason: Story-Engine,
   SKT, and the agentic-GM study all converge on a structured intermediate; without a schema, each
   chapter invents incompatible judgment steps.
3. **Numeric scales exposed to the AI are ladders ≤ 5 rungs**; the numbers behind them live in
   `data/*.yaml`. Reason: SG-01/02.
4. **Tool surface additions implied by this research:** `roll_check(approach, tier, flags[],
   stakes)` (tool computes DC and modifier; refuses without stakes); `roll_table(table_id,
   modifiers)`; `oracle(question, likelihood_rung)`; `tick_clock(clock_id, trigger_id)`;
   `set_fact` usable at description time; `seal`/`unseal(fact_id, gate_id)`; `log_precedent`;
   `get_active_triggers()` (returns every conditional rule whose `[T]` is currently true).
   Reason: each removes an AI weakness (W1, W5, W6, W7, W8, W12, W13).
5. **Rule loading contract:** a short always-loaded core (resolution loop, gate, SG-05/06/08, state
   writes) plus situation-scoped rule cards. Budget the core deliberately small (an order of a few
   thousand tokens, front-loaded) and re-inject a compact per-turn checklist. Reason: W12, W13
   (distractor effect, primacy bias, drift in 8 rounds).
6. **State model must distinguish** `established fact` (written by DM/engine), `player assertion`
   (context only), and `sealed fact`. Reason: SG-06, §5.
7. **Glossary entries must be mutually exclusive**; similar terms (e.g., "injured", "wounded",
   "hurt") are either merged or given a distinguishing test. Reason: SG-16 (RuleArena rule
   confusion).

### 01 — Resolution

1. **Capability gate (VII) as license citation** `[J:enum]` over {basic_action ids, ability ids,
   capability ids, fact ids}; no ID → redirect with "what would license this" (P16). Reason: SG-07.
2. **"When in doubt, roll."** `[J:flag]` "Does this attempt have an uncertain outcome with
   stakes?" with tie-break *yes*; list the no-roll classes explicitly (routine, already-resolved,
   introspection, repeated identical attempt under unchanged conditions — which instead triggers
   P17's no-free-retry cost). Reason: SG-05; Story-Engine's NO_STAKES enumeration.
3. **DC from tier + flags, computed by the tool** (§4.6). Five rungs maximum including "routine
   (no roll)". Anchors per rung; do-not-adjust-for-drama clause. Reason: SG-01–03; F002 data.
4. **Modifier from state, not from the AI.** Approach → attribute table `[J:enum]`, tie-break to
   the lower attribute. Reason: F002 62% arbitrary modifier 0; CoC-Seduce ~6% wrong-skill.
5. **Revisit the critical bands** (§3.4 table): at default +2, "hard" = 40% critical failure,
   "very hard" = 65%. Either narrow the rung spacing, shrink the critical-failure band, or make
   critical failure's consequence tier explicitly *not* escalate lethality, and document the
   choice with the arithmetic. Reason: consequences will be engine-enforced (§6); base rates must
   be ones the designers want enforced every time.
6. **Graduated reveal (P17) as a count:** degree → number of eligible sub-answers unlocked
   (e.g., all / ⌈n/2⌉ / 1 vague / 0 or misleading); the AI chooses *which*, favoring relevance.
   Reason: turns a `[J:open]` into `[D]` count + `[J:enum]` selection.
7. **Compound/extended/opposed/group actions:** make "how many actions is this?" a `[J:enum]`
   against an action-unit definition (Story-Engine caps "MAX 3 ACTIONS" per input and defines
   what is *not* an action unit — setup, aiming, repositioning); extended tasks are clocks.
   Reason: F001 turn-13 compression was handled well by improvisation, but must become precedent.
8. **Advantage-type mechanics** should be a single fixed step (e.g., roll twice keep better)
   triggered by a flag with a cited fact, never a free "bonus"; multiple sources don't stack
   (engine-enforced). Reason: SG-10, W1.
9. **Stakes declaration is part of the resolution rule, not DM advice.** Reason: SG-08.

### 02 — Character

1. **Attributes: few, non-overlapping, each with an unambiguous "use when" test and a
   distinguishing test against its nearest neighbor.** Reason: wrong-skill rate rises with
   confusable options (CoC-Seduce WS 3–11%); RuleArena rule confusion. The constitution's
   "count set by how much texture the AI needs" is right, but texture should come from *approaches
   and tags*, not from many overlapping attributes.
2. **Birth variance and deferred reroll (P1) are `[D]` rolls**, never AI "random" picks. Reason: W6.
3. **Baseline competence floor (P2)** should be a stated default modifier *in state*, so no roll
   ever uses an AI-supplied modifier. Reason: F002.
4. **Origins/backgrounds grant license IDs** (established facts like `knows: river_trade`) that
   the gate and the creative-credit flag can cite. Reason: gives the player creative leverage that
   is auditable (SG-07), a direct goal-1 benefit.
5. **Starting kit as possessions with ids**, so write-on-mention and license checks work from turn
   one. Reason: W8/W9.

### 03 — Tags and evidence

1. **`tag_event` capture = `[J:enum]` over the tag tree with "true only when / false for"
   definitions**, not a free "does this count?" Reason: SG-04. The constitution's P5 insists the
   significance gate is base-model judgment; that can remain, but the *output* must be a closed
   selection with definitions, and **the leniency bias (W2/W3) will skew it toward "yes, counts"**.
   Countermeasure: require a cited concrete action (the Story-Engine pattern: "Concise
   established-context evidence…"), and exclude categories explicitly (e.g., "mere politeness does
   not count as diplomacy evidence").
2. **The narrator should not see tallies or thresholds.** An agreeable model that knows the player
   is one event from a class may nudge the fiction toward it. **[inference from W2/W3]** Tallies
   are `[S]` sealed; the engine raises the recognition moment as a `[T]`.
3. **Weighting and recency are `[D]`**; the AI never computes a weighted tally. Reason: W1.
4. **One event, one classification call, cascade by engine** (P5 hierarchy): the AI picks the most
   specific tag; the engine credits parents. Reason: asking for all levels invites
   inconsistencies between levels.

### 04 — Recognition and growth

1. **Eligibility is `[D]`** (thresholds on sealed tallies), as P5 already says. Classifier
   confidence → grant/offer/abstain is right and is itself a textbook blast-radius cap (P-B).
2. **Crystallization moments** (a tier deepening voiced in fiction) should be `[T]`-triggered and
   drawn from a table of crystallization *forms* (mentor's acknowledgement, oath, title, awakening
   under crisis) so the AI doesn't default to the same trope every time. Reason: W10.
3. **Provisional status / consolidation (VI)** mechanics are timers and counters: `[D]`.
4. **Gated special traits (monster-power absorption)** must be licenses with explicit trigger and
   outcome text, positive-scoped (SG-15). Reason: F003 embellishment.

### 05 — Abilities and Focus

1. **Every ability is a narrow prose permission (P10) in the §4.5 template**: trigger, outcome,
   state writes, "narration may not imply", positive scope. Reason: F003.
2. **Focus costs, recharge, and uses are `[D]`** (P5 already mandates recharge enforcement).
3. **Composite bonuses (P6) resolved by an engine priority order**, never by the AI reasoning
   about interactions. Reason: SG-10, W14.
4. **Ability text lives in data** and is quoted verbatim into the packet when used, so the
   narrator narrates from the literal text in context rather than from memory. Reason: W12, W8.
5. **Avoid ability pairs that overlap** without a distinguishing test. Reason: SG-16.

### 06 — Conflict

1. **Action economy (P9) as action units with a closed definition** of what is and isn't a unit.
   Reason: Story-Engine's actionUnit rule; F001 turn 13.
2. **Attacks, damage, defense, conditions: all `[D]`**; the AI classifies approach, target, harm
   mode (`lethal / nonlethal / restraint / none` — Story-Engine's `HARM_MODES`), and the engine
   computes. Reason: W1; practitioner "combat failures: nonsensical outcomes… when the system
   failed to identify an appropriate target" in the static GM ([arXiv:2502.19519](https://arxiv.org/abs/2502.19519)).
3. **Positioning as relationship states** (engaged/near/far/behind cover) — a small enum is far
   more reliable than coordinates for a text DM. Reason: S1 vs W1; position contradictions were
   one of F002's two real conflicts and a top NCP-Bench case type.
4. **Adversary turns from priority lists + morale thresholds** (`[D]` evaluated), with the AI
   narrating and choosing among tied options. Reason: W15 (DungeonBench), W3 (reluctance to have
   enemies play hard).
5. **Conditions as status flags with durations the engine counts down.** Reason: W12 ("ignoring
   active status effects" is a documented DM-agent failure in D&D Agents).
6. **Escape and surrender are enumerated outcomes on both sides**, so NPCs can flee or yield and
   so can the player (W4, and the "defeat ≠ death" lock).

### 07 — Harm, recovery, death

1. **The telegraphed-death state machine** (§6.2 item 4), with the lethal-risk warning as a
   `[T]`-raised mandatory narration and dying/death as `[D]` transitions.
2. **Defeat outcome tables keyed to adversary goals** (§6.2 item 5).
3. **Injury as a table keyed by degree × harm mode**, not narrator choice. Reason: W3.
4. **Recovery timers and rest effects `[D]`.** The 5e practitioner's short/long-rest confusion is
   the model failure to design out.
5. **Last-chance choice is offered to the player as an enum** of pre-authored options (e.g., "fall
   and be captured", "pay a permanent cost to stand", "a final act before death"). Reason: locus of
   control (§7.3), and the AI should never be the one choosing mercy.

### 08 — Items, loot, crafting

1. **Pool gate / fill quality (P5) is `[J:enum]` for the two circumstances, `[D]` for the roll.**
   F003 already showed this works on flash (6/6).
2. **Item effect text positive-scoped and literal** (SG-15).
3. **Loot and economy numbers `[D]`**; the AI never prices, never "decides the reward."
   Reason: W1, W3 (generous rewards are a positivity failure).
4. **Every item has an id at the moment it is mentioned** (SG-13). Reason: the "15 silver pieces"
   conflict in F002.
5. **Crafting as an extended task (clock) with material tags gating the result pool.** Reason:
   the same P5 shape; clocks are the reliable form for multi-step tasks.

### 09 — Adversaries

1. **Threat bands as ≤ 5 rungs** classified from the adversary's nature with the "never from
   title or dramatic importance alone" guard. Reason: SG-02; Story-Engine `genStats` pools.
2. **Stat blocks sealed `[S]`**; narrator gets tells by band. Reason: §5.
3. **Behavior as priority lists with morale/retreat thresholds**, per archetype. Reason: W15, W3.
4. **Adversary archetypes double as loot/ability pool gates** (already in the brief) — make the
   archetype enum small and hierarchical so classification is reliable (S1).

### 10 — Exploration, social, downtime

1. **Environmental hazards as explicit tables** (fall, cold, heat, drowning, starvation, weather),
   because natural-environment adjudication was the one setting where *every* model family failed
   in CoC-Seduce (mean 9.76%). Reason: S7/W-knowledge.
2. **Social influence with tracked disposition** and social outcomes including an explicit
   "refuses / walks away" row; NPC wants, fears, and refusal conditions are pre-committed at NPC
   creation. Reason: W4 (disengagement deficit; agreeable-persona sycophancy).
3. **Claims made to NPCs** are `[J:flag]` "stakes-relevant factual claim?" → if yes, resolve as a
   deception/persuasion check against the NPC's access to the truth (Story-Engine's `claimCheck`
   fields: claim, truth status, NPC access). Reason: SKT "GPS evidence" exploit.
4. **Investigation as clue graphs with prerequisites** (§5.2). Reason: SKT result; P17.
5. **Travel as clocks and rolled encounter/event tables** with a recent-results exclusion.
   Reason: W6, W10, W11.
6. **Downtime activities as a closed menu with engine-computed durations/costs** — this is the
   one place a menu is right, because downtime is bookkeeping, not improvisation.

### 11 — Living world

1. **Factions as clocks + goal lists**, advanced by a `[D]` world turn with rolled events; the AI
   narrates rumors from the rolled results. Reason: W3 (factions that never act against the
   player), W10, W12.
2. **Hooks, rumors, and consequences as registered objects** (commitments with trigger conditions)
   — the engine surfaces unresolved commitments when relevant so foreshadowing gets paid off.
   Reason: W11 (unfired Chekhov's guns; abandoned plot elements).
3. **Consequence propagation as rules keyed to fact changes** (`[T]`), not narrator recollection.
4. **Generation (sandbox) offline at frontier tier, validated like data**, then used at runtime by
   the flash DM. Reason: §8.
5. **Retirement/legacy procedure**: a scripted sequence of `[D]` summaries of state (so the
   epilogue cannot contradict history) plus AI narration. Reason: W8, W9.

### 12 — DM procedures

1. **The turn loop is the creative-action pipeline** (§7.1), stated as the DM's rules of play:
   parse → gate → anchor → decide (flags/tier/approach) → declare stakes → roll → apply → narrate
   → record → check triggers → ensure next step (P16).
2. **P16 as a counter `[T]`**: "inconclusive resolutions in a row" is engine state; at the
   threshold the DM *must* introduce a lead from a rolled "lead injection" table.
3. **Pacing via concreteness and clocks**, not "feel": scene framing rules state when to cut
   (e.g., after a clock resolves or a stakes question is answered). Reason: W11 (pacing study's
   concreteness control).
4. **NPC play: voice is free, disposition and decisions are not.** Reason: S3 vs W4.
5. **Improvising from the substrate = anchor index + bounded adaptation + precedent log**
   (SG-20). Reason: S2's variability; S6's inconsistency across runs.
6. **Per-turn checklist re-injection**: a compact checklist of the loop, re-stated each turn.
   Reason: W12 instruction drift.
7. **No self-audit substitutes for the auditor** (F001's unnoticed pronoun). Chapter 12 should
   describe the audit as a rule of play ("narration is checked against state writes") rather than
   as infrastructure.

### 13 — Starter setting

1. **Classic fantasy is the model's strongest ground** (S7) — keep the setting within well-known
   genre conventions for its physical culture; put distinctive setting elements in explicit facts,
   not in assumed knowledge. Reason: CoC-Seduce knowledge-coverage finding.
2. **Exercise every hazard table in the opening region** (wilderness adjudication is the
   universal weak spot) and seed at least one sealed mystery with a clue graph, one faction clock,
   one NPC with a pre-committed refusal, and one lethal-risk warning, so live playtests hit every
   mitigated weakness early.
3. **Name/NPC/rumor tables for the region** to counter homogenization (W10).

### 14 — Player's guide

1. **Tell the player the adjudication contract**: intent and method are yours; outcomes come from
   declared stakes and dice; clever use of established details always earns something; assertions
   of success don't. Reason: locus of control (§7.3); it also reduces adversarial phrasing by
   explaining that it doesn't work.
2. **Codex shows declared stakes and rolls out of fiction** (P7), consistent with the no-diegetic-
   System lock.
3. **A "how to be creative" section** listing the creative-credit mechanic and giving examples of
   using the environment, items, and NPC facts — goal 1 made explicit.

---

## 10. Recommendations that beat the current defaults

| ID | Current default | Recommendation | Evidence | Serves |
|---|---|---|---|---|
| R-01 | DC is a free integer chosen by the DM with a 10/15/20/25 hint | Tier rung `[J:rung]` + binary circumstance flags `[J:flag]`; tool computes DC; flag shifts capped | F002 11% / F001 30% off-ladder; ordinal vs binary agreement; Story-Engine tier rule | Goal 2 |
| R-02 | `modifier` is a required free integer in `roll_check` | Tool derives modifier from state via approach→attribute enum | F002 62% zero modifiers, 5 distinct values with no stat source | Goal 2 |
| R-03 | Rule kinds `[D]/[J]/[N]` | `[D]/[J:flag]/[J:enum]/[J:rung]/[J:open]/[N]` + `[T]`, `[S]`, with P-B blast-radius caps | Reliability spread across forms (§4.1) | Goal 2; P10 |
| R-04 | "Decide whether it has stakes" (neutral) | Tie-break toward rolling; enumerate no-roll classes | FP 9.58% vs FC 0.08% | Goal 2 |
| R-05 | Outcome decided after the roll's degree, stakes implicit | Stakes declared in a structured field before the roll; tool refuses to roll without them | Intra; Multihog; W2/W3 | Goals 1 & 2 |
| R-06 | Consequences narrated by the DM | Degree × stakes-tier consequence tables applied by engine | W3; Voyage; Story-Engine | Goal 2; lethality lock |
| R-07 | Single DM call that adjudicates and narrates | Structured adjudication step (closed schema) then narration step from the resolved packet; still one DM (Principle I) | Story-Engine; SKT tri-agent; agentic-vs-static GM; CoC-Seduce "seduced by the narrative" | Goal 2 |
| R-08 | Secrets and hidden stats implicitly in DM context | Sealed state committed at creation; narrator sees gated slices/tells | Hangman theorem; leakage study; SKT | Goal 2; fairness |
| R-09 | Facts recorded when the DM remembers to | Write-on-mention (SG-13) + auditor checks narration against rule state-write lists | Intra; F002 | Goal 2 |
| R-10 | Whole rules prompt always loaded | Small always-on core + situation-scoped rule cards + per-turn checklist | RuleArena distractors; IFScale; drift in 8 rounds | Goal 2 |
| R-11 | Improvised rulings vanish | Anchor index + enumerated adaptations + precedent log | Behavioral inconsistency; S2 variability; Principle III revisit trigger needs recorded cases | Goals 1 & 2 |
| R-12 | P16 soft-lock breaker as DM heuristic | Engine counter `[T]` + rolled lead-injection table | W12; F001 soft-lock | Goal 1 |
| R-13 | P17 "roughly half, DM's choice" | Tool computes count by degree; DM selects which | §9 ch. 01 item 6 | Goal 2 |
| R-14 | Ability text as prose | Positive-scoped literal template with "narration may not imply" | F003 | Goal 2 |
| R-15 | Flash tier for everything | Flash for adjudication and narration (family chosen by a CoC-Seduce-style test on this ruleset); frontier offline for generation/world turns; different family for audit | §8 | Cost; goal 2 |

---

## 11. What the brief (and adjacent defaults) get wrong, or leave dangerous

1. **§3 "Rich substrate is a feature" is right about *availability* but silent about *loading*.**
   If authors read it as "put everything in front of the DM", the RuleArena distractor result says
   performance will drop — irrelevant-but-plausible rules hurt far more than length. The substrate
   must be indexed and retrieved by situation (R-10), and analogical reach must go through an
   anchor index (R-11). Suggested brief amendment: "Rich substrate lives in data and rule cards;
   the DM loads the relevant cards per situation."
2. **§5's rule kinds are too coarse** (R-03). `[J]` should never appear bare.
3. **§7's DC ladder + default modifier are not actually enforced by the current tool surface.**
   The live data shows the ladder leaks (11%/30%) and the default modifier was almost never used
   (62% zeros). The resolution author should not treat "validated live, 0 contradictions" as
   validating DC *selection* — F001/F002 validated degree-*following*, not difficulty *choice*.
4. **The ±10 critical bands with a +2 default produce 40% critical failure on "hard" and 65% on
   "very hard" checks** (§3.4). Combined with engine-enforced consequences (which this research
   recommends), this may be harsher than the locked "defeat usually means capture, injury, loss"
   stance intends. The resolution author should confirm with arithmetic, not intuition.
5. **"Think like the AI that will run this… precise triggers, explicit tables" (§2)** — agreed, but
   it should explicitly forbid *nested exceptions* and *negative-space effect text*, the two
   phrasing patterns with direct evidence of failure (W14; F003).
6. **Constitution P5: significance gate as base-model judgment** — acceptable under P-B because
   grant/offer/abstain bounds the blast radius, but the brief should note the *directional* bias
   (leniency) and require cited evidence plus hidden tallies (§9 ch. 03).
7. **Constitution P13: judge "MUST NOT share a model family"** — CoC-Seduce found asymmetric
   home-family effects (GPT targets resisted GPT-generated attacks; Gemini targets were *more*
   vulnerable to Gemini-generated ones), so family independence is directionally supported but
   not a sufficient condition; audits should be tested, not assumed independent.
8. **The brief is silent on randomness ownership.** It should state that *all* randomness,
   including DM-side "random" choices, is tool-rolled (W6).
9. **The brief is silent on player assertions.** It should state SG-06 as a non-negotiable-grade
   convention: player text establishes intent and method only.

---

## 12. Open empirical questions (each with a named test; defaults ship regardless)

| Question | Default shipped | Named test that settles it |
|---|---|---|
| Does tier+flags DC selection reduce off-ladder/lenient DCs vs the free-integer default? | R-01 | **T-R4-01 "DC A/B"**: replay the 63 F002 `roll_check` contexts under both schemas on the production model; measure spread of DC for identical contexts across 10 runs each, and DC shift under rhetorical rewrites of the player line |
| What is this ruleset's CoC-Seduce-style false-pass rate on the adjudication step, per candidate model family? | Choose flash family by test | **T-R4-02 "Seduce-the-DM"**: 4 rhetorical variants (neutral/authority/pseudo-logic/omission) × 40 scenarios drawn from chapters 01/06/10; report FP/FC/wrong-approach rates; pick the family with lowest FP |
| Does stakes-before-roll reduce post-roll softening? | R-05 | **T-R4-03 "Softening audit"**: in playtest logs, compare declared failure stakes to narrated failure outcomes; target 0 softened failures |
| Does the narrator leak sealed facts when given gated slices only? | R-08 | **T-R4-04 "Guess the secret"**: a separate model reads N scenes of narration and guesses the sealed solution; compare gated vs full-context narrators (method of arXiv:2605.10794) |
| Do tag_event classifications skew lenient? | cited-evidence + hidden tallies | **T-R4-05 "Evidence calibration"**: 60 narrated moments, half designed as non-evidence; measure false-positive tag rate with/without tallies visible |
| Is per-turn checklist re-injection enough to hold loop compliance to turn 50? | R-10 | **T-R4-06 "Loop drift"**: F002 harness at 50 turns; measure stakes-declared, write-on-mention, and trigger-response compliance by turn bucket |
| Do players feel creative freedom under capped creative credit? | §7 | **T-R4-07 "Creative latitude playtest"**: owner plays 3 sessions; log every novel action, its anchor, adaptation, and the player's 1–5 "that felt fair" rating |

---

## 13. Sources

**Controlled studies and benchmarks (primary)**
- Chen et al., *Seduced by the Narrative: Assessing Rule Adherence in Semi-Open Textual Sandboxes* (CoC-Seduce), July 2026 — https://arxiv.org/abs/2607.02802 (code: https://github.com/answerrtx/CoC-Seduce)
- Zhou et al., *RuleArena: A Benchmark for Rule-Guided Reasoning with LLMs in Real-World Scenarios*, ACL 2025 — https://arxiv.org/abs/2412.08972
- Simpson, Kozak, Doake, *Confidently Wrong: Exception Chain Collapse in Frontier LLM Rule Evaluation*, July 2026 — https://arxiv.org/abs/2607.23386
- *Autorubric: Unifying Rubric-based LLM Evaluation* — https://arxiv.org/abs/2603.00077
- Baldelli et al., *LLMs Can't Play Hangman: On the Necessity of a Private Working Memory* — https://arxiv.org/abs/2601.06973
- *Can You Keep a Secret? Involuntary Information Leakage in Language Model Writing* — https://arxiv.org/abs/2605.10794
- *Tricking LLM-Based NPCs into Spilling Secrets* — https://arxiv.org/abs/2508.19288
- Rahmati & Zhao, *Enforcing Narrative Reliability and Epistemic Pacing in LLM-Driven Detective Games via Structured Knowledge Trees* (AIIDE-26) — https://arxiv.org/abs/2609.23043
- *DungeonBench: A Benchmark for Rules-Rich Tactical Reasoning* — https://arxiv.org/html/2607.29577
- Zeng et al., *Setting the DC: Tool-Grounded D&D Simulations to Test LLM Agents* (NeurIPS 2025 workshop) — https://openreview.net/forum?id=3Op7kJOvaD ; https://neurips.cc/virtual/2025/128312 ; coverage: https://www.psypost.org/researchers-are-using-dungeons-dragons-to-find-the-breaking-points-of-major-ai-models/ , https://today.ucsd.edu/story/from-chatbots-to-dice-rolls-researchers-use-dd-to-test-ais-long-term-decision-making-abilities
- Delafuente et al., *Does Reasoning Help LLM Agents Play Dungeons and Dragons?* — https://arxiv.org/abs/2510.18112
- *Static vs. Agentic Game Master AI for Facilitating Solo Role-Playing Experiences* — https://arxiv.org/abs/2502.19519
- Sharma et al., *Towards Understanding Sycophancy in Language Models* — https://arxiv.org/abs/2310.13548
- *Too Nice to Tell the Truth: Quantifying Agreeableness-Driven Sycophancy in Role-Playing Language Models* (ACL 2026) — https://arxiv.org/abs/2604.10733
- *Simulated Customers Never Walk Away: Decision Fidelity of LLM User Simulators* — https://arxiv.org/abs/2606.20708
- *Too Good to be Bad: On the Failure of LLMs to Role-Play Villains* — https://arxiv.org/abs/2511.04962
- Tian et al., *Are Large Language Models Capable of Generating Human-Level Narratives?* — https://arxiv.org/abs/2407.13248
- *Echoes in AI: Quantifying Lack of Plot Diversity in LLM Outputs* (PNAS 2025) — https://www.pnas.org/doi/10.1073/pnas.2504966122 ; https://arxiv.org/abs/2501.00273
- *Benchmarking Linguistic Diversity of Large Language Models* (TACL) — https://arxiv.org/abs/2412.10271
- *Improving Pacing in Long-Form Story Planning* — https://arxiv.org/abs/2311.04459
- *Codified Foreshadowing-Payoff Text Generation* — https://arxiv.org/abs/2601.07033
- *Large Language Models Are Bad Dice Players* — https://arxiv.org/abs/2601.05414 ; *Deterministic or probabilistic? The psychology of LLMs as random number generators* — https://arxiv.org/abs/2502.19965
- *Consistent but Miscalibrated: Evaluating LLM Limitations for Risk Communication in Natural Language* — https://arxiv.org/abs/2607.03882
- *When Agents Disagree With Themselves: Behavioral Consistency…* — https://arxiv.org/html/2602.11619v2
- Jaroslawicz et al., *How Many Instructions Can LLMs Follow at Once?* (IFScale) — https://arxiv.org/abs/2507.11538
- Chroma, *Context Rot* (July 2025), summarized at https://www.zenml.io/llmops-database/context-rot-evaluating-llm-performance-degradation-with-increasing-input-tokens and https://hamel.dev/notes/llm/rag/p6-context_rot.html
- Laban et al., *LLMs Get Lost in Multi-Turn Conversation* (ICLR 2026) — https://arxiv.org/abs/2505.06120
- Li et al., *Measuring and Controlling Instruction (In)Stability in Language Model Dialogs* — https://arxiv.org/abs/2402.10962
- Webb, Holyoak & Lu, *Emergent analogical reasoning in large language models* — https://www.nature.com/articles/s41562-023-01659-w ; follow-up https://arxiv.org/abs/2404.13070 ; critique https://arxiv.org/abs/2308.16118 ; *High variability in LLMs' analogical reasoning* — https://www.nature.com/articles/s41562-025-02224-3
- *Divergent creativity in humans and large language models* — https://pmc.ncbi.nlm.nih.gov/articles/PMC12824279/
- *Large Language Models as Virtual Survey Respondents* (example clustering) — https://arxiv.org/abs/2509.06337 ; *The Few-shot Dilemma: Over-prompting LLMs* — https://arxiv.org/abs/2509.13196

**Practitioner systems and write-ups**
- Ian Bicking, *Intra: design notes on an LLM-driven text adventure* (2025) — https://ianbicking.org/blog/2025/07/intra-llm-text-adventure ; *Creating Worlds with LLMs* — https://ianbicking.org/blog/2025/06/creating-worlds-with-llms.html
- ZDOSt, *Story-Engine* SillyTavern extension (source read: `semantic-contract.js`, `engines.js`, `narration-sanitizer.js`; last commit 2026-09-28) — https://github.com/ZDOSt/Story-Engine ; predecessor *Game-Master* preset — https://github.com/ZDOSt/Game-Master
- MultihogAurelius, *SillyTavern Multihog D&D Framework* — https://github.com/MultihogAurelius/SillyTavern-MultihogDnDFramework
- Austin Amento, *Prompt Architecture for a Reliable AI Dungeon Master* — https://dev.to/austin_amento_860aebb9f55/prompt-architecture-for-a-reliable-ai-dungeon-master-d99
- EN World thread, *LLMs as a GM* — https://www.enworld.org/threads/llms-as-a-gm.714126/
- Latitude Voyage: TechCrunch (2026-04-21) — https://techcrunch.com/2026/04/21/voyage-is-an-ai-rpg-platform-for-creating-custom-gaming-worlds-with-ai-generated-npc-interactions/ ; Arcanum reviews — https://arcanumrpgs.com/blog/voyage-review/ , https://arcanumrpgs.com/blog/voyage-vs-ai-dungeon/
- Friends & Fables — https://fables.gg/blog/when-to-play-ai-dungeon-and-when-to-play-friends--fables
- Hidden Door (Hilary Mason interview) — https://www.pcgamer.com/hidden-door-pc-gaming-show-2023-interview/
- Mythic Game Master Emulator 2e — https://wordmillgames.itch.io/mythic-game-master-emulator-second-edition
- Blades in the Dark, *Progress Clocks* — https://bladesinthedark.com/progress-clocks ; The Alexandrian on clocks — https://thealexandrian.net/wordpress/40424/roleplaying-games/blades-in-the-dark-progress-clocks
- Gemini 3 benchmark summary (vendor-reported MRCR/τ²) — https://www.vellum.ai/blog/google-gemini-3-benchmarks

**This repository**
- `specs/001-action-resolution-probe/probe-results.md`; `specs/002-long-horizon-consistency-test/implementation-results.md` and raw logs `t021_*.log` (re-tallied for §3.4); `specs/003-ability-acquisition-probe/implementation-results.md`; `src/dm_agent.py`, `src/tools.py`, `src/resolution.py`
- `reports/Long horizon LLM narrative benchmarks.md` (NCP-Bench, RPGBench, ConStory-Bench, MERIT); `reports/Mistborn TTRPG AI design patterns.md` ("Thirteen Hours", AI Dungeon, judge-gates); `reports/DM craft TTRPG design AI tools.md` (tools landscape; locus-of-control finding)
- Degree-distribution arithmetic in §3.4: exhaustive enumeration over d20 faces using `src/resolution.py`'s rule (scratchpad script, one-off).
