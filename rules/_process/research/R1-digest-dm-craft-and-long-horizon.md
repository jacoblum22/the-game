# R1 Digest — DM Craft, TTRPG Design Theory, AI-GM Tooling, and Long-Horizon LLM Consistency

> Research agent R1. Distills, chapter by chapter, everything in these 12 sources: the third research pass
> (`reports/DM craft TTRPG design AI tools.md` plus its 7 research-note files) and the Feature 002 long-horizon
> pass (`reports/Long horizon LLM narrative benchmarks.md` plus its 3 research-note files). Every file was read
> in full. Chapter authors should be able to rely on this digest instead of re-reading the sources. The digest
> does **not** write rules. It lists the evidence, precedents, numbers, warnings, tensions and gaps the rules have to deal with.

## How to use this digest

- **Citation format.** Citations follow BRIEF §6: `[R: <path> §<heading>]`. Headings are shortened to their
  first distinctive words, which is enough to find them in the file. `[C:…]` cites the constitution, and
  `[BRIEF §n]` cites the brief.
- **Bullet shape (Section 1).** Each bullet gives **the finding**, then the concrete numbers or named precedents,
  then **Rules out / warns** (what it prohibits or cautions against), then the citation. When a finding matters
  to several chapters, it is written out in full once, and other chapters point to it with "→ see 00.x" rather
  than repeating it.
- **"Digest-author note"** marks analysis or arithmetic that **I** added and that is not in the sources, such as
  computed probabilities, internal inconsistencies I found in the sources, or reinterpretations for
  single-player play. Treat these as analysis to check, not as research findings.
- **Evidence grades** (used where it matters): **[A]** primary or official rules source, or directly read
  code/prompt files; **[B]** peer-reviewed or arXiv paper numbers passed through one AI-summarizer fetch
  ("likely accurate, not byte-verified" per the notes' own caveats); **[C]** practitioner blog, forum or
  community consensus; **[D]** weak, commercial or unverifiable (e.g. a vendor blog's survey numbers). The
  reliability register at the end of this preamble lists the specific weak points.

## Source inventory

| Key | File | What it is |
|---|---|---|
| DMR | `reports/DM craft TTRPG design AI tools.md` | Third-pass synthesis report: spotlight/challenge craft, indie theory, 5e/PF2e/13th Age lessons, four deep-dived mechanics, tools landscape, verdict table |
| ACAD | `research_notes/DM craft TTRPG design AI tools/ai_gm_academic_research.md` | Evaluation frameworks, consistency research, fairness gap, multi-agent GMs, AI-vs-human player studies |
| TOOLS | `research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md` | Ink/Yarn/Twine/ChoiceScript, NovelAI/Kobold/SillyTavern, NarrativeEngine/Open Dungeon, bounded-narration techniques, failure modes, architecture patterns |
| COST | `research_notes/DM craft TTRPG design AI tools/cost_systems_and_move_based_abilities.md` | M&M, HERO, Savage Worlds, 13th Age, point-buy exploit levers; Blades abilities, Fate stunts, move-design spectrum |
| CRAFT | `research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md` | GM principles, pacing, yes-and, session zero, spotlight, challenge diversification, GM mistakes, AI translation gaps |
| INDIE | `research_notes/DM craft TTRPG design AI tools/indie_niche_ttrpg_design_theory.md` | GNS/Big Model, Robin's Laws, Kobold Guide, Mythcreants antipatterns, decision paralysis, crunch, PbtA, Dungeon World, feat bloat |
| MAJOR | `research_notes/DM craft TTRPG design AI tools/major_system_design_lessons.md` | 5e balance and 2024 revision, PF2e philosophy, 13th Age 1e→2e, head-to-head, AI-GM runability |
| RES | `research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md` | PF2e degrees, Fate/Blades/Genesys/WoD, tradeoffs; 5e/PF2e/4e/Lancer action economies, exploits, anti-dominance techniques |
| LHR | `reports/Long horizon LLM narrative benchmarks.md` | Feature 002 synthesis: synthetic construction validity, fact-conflict dominance, degradation curves, mitigation ranking |
| NCP | `research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md` | NCP-Bench deep-dive: commitments, construction pipeline, prompts, per-model numbers, HiAgent |
| OTHER | `research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md` | Oolong, Lost in Stories/ConStory-Bench, BOOKMARKS, knowledge-tree detective game, LOCOMO, MERIT/FAMA, Memora, SSGM, summarization drift |
| RPGB | `research_notes/Long horizon LLM narrative benchmarks/rpgbench.md` | RPGBench deep-dive: game JSON schema, GameChecker algorithm, metrics, per-model numbers |

## Source reliability register (read before trusting a number)

1. **NCP-Bench conflict percentages are not shares.** They add up to more than 100% per model (GPT-5.2: 40+24+31 = 95;
   GPT-4o-mini: 64+32+11 = 107; Qwen3: 68+33+26 = 127; Kimi-K2.5: 66+54+11 = 131). They are best read as
   *per-interaction incidence rates*, since one episode can log several conflict types. The report's phrase
   "fact conflicts dominate … 40–68% of all conflicts" is therefore loose wording, although the ranking (fact
   first) holds for 5 of 6 models. For GPT-5.2, fact (40%) is only modestly above player-input (31%). (Digest-author note.)
2. **Two different GPT-4o-mini baselines.** The main results table gives GPT-4o-mini 24.80 average turns and 64%
   fact conflicts. The HiAgent ablation, audited by GPT-5.4-mini instead of Gemini-2.5-Flash, gives 22.16 turns
   and 60% fact. The natural-vs-adversarial comparison uses the ablation-table numbers. The auditor choice alone
   moves the numbers by a few points. [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Failure modes] [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Mitigation strategies]
3. **NCP-Bench survival-curve readouts** ("below 50% between turns 5–15", "zero by 40–60") are the summarizer
   reading a chart by eye. The notes explicitly say **not to cite them as precise**. Only "~42% survival @20 for
   GPT-5.2" is a stated headline. The survival@20 figures for the other five models come from a single
   extraction pass. [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Failure modes]
4. **RPGBench table values** came through one AI-summarization pass over the arXiv HTML (the OpenReview PDF was
   bot-blocked). The metric *definitions* were confirmed against the repo code. [R: research_notes/Long horizon LLM narrative benchmarks/rpgbench.md §metrics]
5. **Player-experience survey numbers** (412 users, 68% higher immersion, 4.13 vs 3.35, and so on) come from a
   commercial AI-GM vendor blog (dungeonsdeep.ai) and a Boing Boing article. Grade **[D]**. The "expert vs novice"
   finding is attributed to arXiv:2502.19519, which is a pilot study with 8 and 12 users. Its generalizability
   is doubtful. [R: research_notes/DM craft TTRPG design AI tools/ai_gm_academic_research.md §Player Experience and Comparative]
6. **Unsourced or weakly sourced engineering numbers:** "character persona constraints reduce hallucinations by
   ~45%" (Medium guardrails post); PCG "40% increase in environmental diversity with 28% computational overhead
   reduction" (no source given). Grade **[D]**. [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Technical Approaches to Bounded AI Narration]
   [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Supporting Infrastructure]
7. **Factual slips inside the tools note:** its "Ink" section describes `$`-prefixed variables and a "Dialogue
   Presenter's Variable Storage component". Those are **Yarn Spinner** features, not Ink features. ChoiceScript's
   command is `*create`, not "*creation". These slips don't affect any design conclusion. [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Non-AI Branching Narrative Tools]
8. **Imprecise PF2e phrasing in RES:** "Success (beat DC by 1–9)". In the actual rule, *meeting* the DC is a
   success (total ≥ DC), critical success is total ≥ DC+10, and critical failure is total ≤ DC−10. The project's
   `src/resolution.py` thresholds match the actual rule. [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §How does Pathfinder 2e's four-degree system work]
9. **The DMR's "materially worse than 46.1%" comparison is apples-to-oranges.** 46.1% (from the second report,
   not in these sources) is an exact-match state-prediction rate. NCP-Bench's 42% is the share of episodes with
   *zero* audited conflicts through turn 20. Both are sobering, but neither is a "worse version" of the other.
   Constitution P3 cites "~46–58%". The 58% figure is not in any of my sources. [R: reports/DM craft TTRPG design AI tools.md §The tools landscape] [C:P3]
10. **AI-GM "runability" claims** (bounded accuracy is more AI-friendly; explicit resolution is easier than
    implicit passives) are labeled in the source as **untested inferences**. No system has been tested at scale
    (50+ sessions) with an AI GM. [R: research_notes/DM craft TTRPG design AI tools/major_system_design_lessons.md §AI-GM Runability]
11. **All "Lost in Stories" numbers** (CED, positions, gaps, entropy) are summary-level. The per-category CED
    breakdown and the detector's validation against humans were not retrieved. [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §What exactly is the "Lost in Stories" taxonomy]

---

# 1. Per-chapter findings

## 00 — Architecture (conventions, scales, attributes, tag-tree top levels, state model, tool surface, glossary)

### 00.A State authority and the tool surface

- **Game state must never live only in narration. Store it in an explicit structure, separate from prose.** The
  tools-landscape synthesis calls this principle "non-negotiable". Its canonical failure example: at turn 1 the
  PC has 10 gold, at turn 50 the summarized context says "an adventurer with gold", and at turn 51 the LLM
  invents a remainder, so nobody knows whether the PC had 10, 5 or 50. Precedents: Open Dungeon (narration by
  LLM, state "100% deterministic and engine-owned"); the SRD Rules Engine ("rules engine is law; narration is
  flavor"; the LLM narrates results but cannot invent them); the Song/Zhu/Callison-Burch "Thirteen Hours"
  function-calling paper (arXiv:2409.06949). **Rules out:** any rule whose state lives only in prose ("the
  character remembers they owe the guild"). Every rule has to name the state field it reads and writes, which
  the BRIEF's "State touched" section already requires. [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Design Tensions & Failure Modes]
  [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Supporting Infrastructure] [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Synthesis] [C:P13]
- **The field's convergent architecture has three layers.** Deterministic tool calls own mechanics, an external
  store owns world state, and a narrow gate sits between "player proposes something ambiguous" and "the AI
  narrates it as true". The DMR says this pass *confirms* that shape and adds a reference implementation
  (NarrativeEngine) plus a multi-agent variant (fabula/discourse). **Warns:** the DMR says the
  reconciliation/verification layer should be budgeted as "a first-class, expensive-to-build component rather
  than an afterthought". [R: reports/DM craft TTRPG design AI tools.md §What this round changes] [R: reports/DM craft TTRPG design AI tools.md §The tools landscape] [C:P13]
- **Function-calling pattern (per turn).** The LLM receives current state (JSON), the function schema and the
  player action. It emits narration (free text) plus structured calls (e.g. `UpdateEnemyHP`, `RollCheck`). The
  engine validates and applies the calls before the next turn. Stated limits: it needs careful schema design;
  the LLM must learn when to call which function; complex rules inflate the schema. Best fit: "turn-based TTRPGs
  where state changes are discrete and well-defined". **Implication for 00's tool surface:** state changes should
  be discrete, typed events (one call per atomic change), not free-form "update state" blobs. [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Technical Approaches to Bounded AI Narration] [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Key Architectural Patterns]
- **Structured output does not guarantee correct content.** RPGBench forces every model to emit the same JSON
  state block every round. Mechanical correctness (MEC, the fraction of rounds with zero error) was still only
  0.554–0.765 at 10 rounds, and it **declines** as rounds increase from 10 to 25 (GPT-4o ablation). Models make
  outright arithmetic and logic errors while filling in the enforced structure. The LHR draws the lesson for this
  project: real tool calls change *how* errors show up (a malformed call instead of a silent prose
  contradiction), not *whether* they happen. **Implication:** anything the engine can compute (sums, clamps,
  thresholds, recharge bookkeeping) should be computed by the tool, not by the model and then passed to the tool.
  `[D]` should mean "the tool does the math", not "the model does the math and the tool stores the result".
  [R: research_notes/Long horizon LLM narrative benchmarks/rpgbench.md §state representation format] [R: reports/Long horizon LLM narrative benchmarks.md §Degradation is fast]
- **Facts that change over time are the most fragile kind of state. Use update-on-write stores for them, never
  similarity retrieval.** MERIT/FAMA (arXiv:2609.05441): on *updated* facts, embedding retrieval accuracy
  "collapses unpredictably" to a range of 0.30–0.95 (0.45 max-seed gap). Update-on-write structured stores, and
  (notably) LLM summarization, stay within 0.70–1.00. LOCOMO-family benchmarks consistently rank *temporal*
  reasoning among the weakest categories (e.g. Synthius-Mem: 96.73% single-hop vs 89.32% temporal vs 77.33%
  open-domain). **Rules out:** vector-RAG as the source of truth for Vitality, Focus, inventory counts, positions,
  lock/alive/known flags, tallies or clock values. RAG is acceptable for static lore. [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §Other 2025–2026 benchmarks] [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §Mitigation strategies: quantified evidence] [R: reports/Long horizon LLM narrative benchmarks.md §Fact conflicts, not plot]
- **Retrieving the right fact is not enough: models act on a correctly retrieved updated fact only about 55% of
  the time.** (MERIT.) Swapping one memory implementation for another moved task success by up to **60
  points**. The best configurations gave 2.7–3.9× the marginal utility per dollar of the worst. **Implication for
  00:** the architecture has to include a *use-check* (was the fact honored in the narration?) as well as a
  fetch. → see 12.D (verification step). [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §Other 2025–2026 benchmarks] [R: reports/Long horizon LLM narrative benchmarks.md §Degradation is fast]
- **Two-tier memory (NarrativeEngine): "ledgers" plus RAG.** Persistent character/location ledgers are kept
  separate from a dynamic RAG layer for factions, power systems, economy and events, about **1,200 tokens/turn**.
  The stated reason: the split keeps static data from polluting the context window. The same system also
  versions campaign state and supports rollback and parallel branches. Pattern 1 in the tools note splits
  persistent knowledge (character facts, location descriptions, an immutable historical-event log) from dynamic
  state (NPC positions, active quests, recent events, environmental conditions). **Caution:** NarrativeEngine
  itself "still relies on unstructured LLM generation" and has "limited enforcement of game rules". It
  demonstrates memory design, not rules enforcement. [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Open-Source AI Dungeon Master Projects] [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Key Architectural Patterns]
- **Engine-owned state versus narrative-driven state is a spectrum, and every serious project draws the
  state-authority line somewhere.** Open Dungeon's cost: "narration is constrained to describe game state,
  limiting creative freedom". The DMR calls this "the sharpest available real-world statement of the tradeoff
  this project will have to resolve". **For 00:** each chapter contract should say which state is engine-owned
  `[D]` and where the narrator has latitude `[N]`, which the BRIEF's rule kinds already do. [R: reports/DM craft TTRPG design AI tools.md §The tools landscape] [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Open-Source AI Dungeon Master Projects]
- **Data-driven rules as composable data** (SRD Rules Engine): classes, feats, items, prerequisites and effects
  are defined as reusable data on an Entity-Component System. Foundry VTT's automation modules (Dynamic Active
  Effects, Midi-QOL) show rich rule automation kept separate from presentation. **Supports:** BRIEF §12's "prose-only
  mechanics are a defect" and the `data/*.yaml` design. [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Supporting Infrastructure]
- **RPGBench's game schema is a ready-made precedent for the state/event model.** It uses `state_variables`
  (player-facing numerics, each with `value_name`, `unique_id`, `description`, `initial_value`, `min_value`,
  `max_value`), `hidden_variables` (engine flags and counters with the same schema, e.g. `has_succeeded`,
  `tasks_completed`), `events` (with `scene` list, `entering_condition`, `succeed_condition`, `succeed_effect`,
  `fail_effect`, `explanations`), and global `pre_event_checks` (end-of-round rules such as "if succeeded →
  Exit"). Conditions and effects are **literal expression strings** (`v.creativity > 20`, `h.tasks_completed +=
  1`) that the harness evaluates. **Direct adoption candidate** for how `data/*.yaml` expresses triggers and
  effects: machine-evaluable conditions instead of prose. Min/max clamps are first-class, and RPGBench's error
  taxonomy has a separate bucket for clamp errors. [R: research_notes/Long horizon LLM narrative benchmarks/rpgbench.md §overall evaluation methodology] [R: research_notes/Long horizon LLM narrative benchmarks/rpgbench.md §dataset construction / prompts]
- **NCP-Bench's formal state is `s_t = (F_t, i_t, C, ℛ)`:** a fact ledger, a current trajectory index, a set of
  typed commitments, and an ordered reference trajectory. **Candidate backbone for 00's state model** alongside
  the existing resources/possessions/facts/trajectory nodes/commitments in `src/world_state.py`. The project's
  existing "trajectory nodes" and "commitments" map directly onto NCP's ℛ and C. The typing in 00.B makes them
  checkable. [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §What exactly is "Narrative Commitment Preservation" (NCP)] [BRIEF §7]
- **Layered context: rules first, then recent events, then lore.** "Rules buried in the middle of a dense prompt
  get overshadowed by recency effects." The tools note reports, without a number, that separating combat rules
  from narrative-craft guidance improves adherence without losing narrative quality. Its synthesis rule 5:
  "Rules first (inviolable). Recent events next. Lore and flavor last (can be pruned)." **Implication for 00's
  chapter contracts:** every chapter should keep its binding rules (the numbered `Rules`/`Tables`) cleanly
  separable from craft guidance (`Design intent`, commentary), so a runtime can inject only the binding part
  for the current mode (combat, social, travel). The BRIEF's chapter format already does this. It should be
  treated as a hard requirement. [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Key Architectural Patterns] [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Design Tensions & Failure Modes] [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Synthesis]
- **Constrained decoding and schemas can guarantee *shape* but not conditional logic.** "If player is below 10
  HP, monsters gain advantage" belongs in rules, not in an output schema. **For 00:** conditional mechanics live
  in data and rules evaluated by tools. Schemas only validate the form of tool calls. [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Technical Approaches to Bounded AI Narration]
- **Seven guardrail strategies** (a checklist for 00's "runtime capability assumed" field): schemas, retrieval,
  tool use, post-hoc verification, decoding constraints, policy gates, observability/logging. Also: "increasing
  constraints beyond a point reduces narrative coherence and creativity" (the "Rules Enforcement Paradox"). →
  see Tensions T-12. [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Technical Approaches to Bounded AI Narration] [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Design Tensions & Failure Modes]
- **Fabula/discourse split (multi-agent option).** A Director/simulation agent plans world-state events. A
  separate Narrator agent topologically sorts the event graph and turns *only the scene-relevant structured
  events* into prose, "feeding it only the context needed for that specific scene". **For 00:** if the orchestrator
  chooses a multi-model runtime, this is the documented shape: 11's living-world engine is the "fabula" producer
  and 12's narration is "discourse". **Open problem:** no published research says how to resolve disagreements
  between agents ("if the rule-checker contradicts the narrator, which agent wins?"). 00 must state an authority
  order if it adopts this. [R: research_notes/DM craft TTRPG design AI tools/ai_gm_academic_research.md §Multi-Agent Approaches] [R: reports/DM craft TTRPG design AI tools.md §The tools landscape]
- **Schema-governed knowledge pipelines** (Game Knowledge Management System, MDPI) and **StateAct**
  (self-prompting plus structured state-tracking) both treat consistency as explicit knowledge management. The
  ACAD inference: "Consistency is fundamentally a world-state tracking problem, not a language modeling problem."
  [R: research_notes/DM craft TTRPG design AI tools/ai_gm_academic_research.md §Consistency and Long-Horizon] [R: research_notes/DM craft TTRPG design AI tools/ai_gm_academic_research.md §Additional Relevant Research Areas]
- **Long-context, long-horizon and long-term memory are three different properties** ("The Horizon Gap" survey,
  1,547 papers). Oolong shows that frontier models (GPT-5, Claude Sonnet 4, Gemini 2.5 Pro) score **below 50%**
  on aggregation over contexts of up to 128K, even though the tokens are "present". **Rules out:** assuming that
  a big context window lets the DM "just remember". 00 should be designed as a long-horizon, long-term-memory
  system. [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §Oolong]
- **Campaign-collapse arc, reported by practitioners:** sessions 1–10 go well; at sessions 10–50 the context
  fills, older decisions get summarized, and drift begins; after session 50 the campaign becomes incoherent
  (threads forgotten, rules violated, encounters disconnected). **This is the failure an open-ended sandbox
  (BRIEF §4) is most exposed to.** The "plan for 100+ turns from day one" rule (tools synthesis #7) applies.
  Grade [C]. [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Design Tensions & Failure Modes] [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Synthesis]

### 00.B Fact typing, a candidate state-category taxonomy

- **The fact categories that fail first should be first-class, typed state.** NCP-Bench appendix case studies
  (qualitative, not quantified): **spatial/location** (*Alien*: a character's location changes with no
  narrated movement), **object state** (*Indiana Jones*: a "locked door" later treated as open with no unlocking
  event), **character status** (*Zombieland*: alive/dead or present/absent silently violated), **entity
  existence** (*Casino Royale*: something referenced as pre-established that was introduced later). The LHR
  adds **numeric resources revised more than once** (HP, gold, counts) as the single most fragile category.
  **Recommended state-type vocabulary for 00:** `location`, `object_state`, `status_flag`, `entity_existence`
  (with an introduction timestamp), `quantity` (numeric, revisable, tagged "updated"), `knowledge` (who knows
  what), `relationship`. [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Failure modes] [R: reports/Long horizon LLM narrative benchmarks.md §Fact conflicts, not plot] [R: reports/Long horizon LLM narrative benchmarks.md §What this means for Feature 002's spec]
- **Atomize facts into cognitive-state (who knows what), positional-state (where things are) and
  relationship-state facts.** Each fact is one atomic declarative sentence with an id (`f_0`, `f_1`, …). NCP's
  initial-fact extraction does this, and it ties each fact to the variables a commitment references. **For 00:**
  NPC knowledge is state, not flavor. "Knowledge Contradictions" (a character acting as if they don't know
  something they were told, or knowing something they shouldn't) is a named error subtype. [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Methodology for constructing test scenarios] [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §What exactly is the "Lost in Stories" taxonomy]
- **Positive assertion of ignorance.** NCP's "T=0 Absolute Isolation Principle" tells the generator to write
  facts like "X is not yet aware of Y" and "Z has not yet happened", rather than simply leaving unknowns out.
  **For 00:** secrets, undiscovered clues and unmet NPCs should exist as explicit negative facts. The DM then
  cannot leak them by accident (a "Triggering Unknown Facts" failure), and a later reveal is a recorded state
  change, not an improvisation. [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Methodology for constructing test scenarios] [R: reports/Long horizon LLM narrative benchmarks.md §NCP-Bench proves synthetic construction]
- **The five consistency-error categories** ("Lost in Stories", 19 subtypes), a taxonomy 00 can use to classify
  what each state field protects against:
  (1) *Timeline & Plot Logic*: absolute-time, duration, simultaneity contradictions; causeless effects; causal-logic violations; abandoned plot elements.
  (2) *Characterization*: memory contradictions, knowledge contradictions, skill fluctuations, forgotten abilities.
  (3) *World-building & Setting*: core-rule violations, social-norm violations, geographical contradictions.
  (4) *Factual & Detail*: appearance mismatches, nomenclature confusions, quantitative mismatches.
  (5) *Narrative & Style*: perspective confusions, tone inconsistencies, style shifts.
  **Empirically dominant:** Factual & Detail and Timeline & Plot Logic, not Characterization or World-building,
  even though the latter two are "conceptually closest" to forgetting. **Implication:** 00 needs an explicit
  **time model** (in-world clock/calendar, durations, sequence stamps on facts). Temporal errors are a dominant
  failure mode, and no chapter in the BRIEF's map explicitly owns game time. → see Gaps G-19. [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §What exactly is the "Lost in Stories" taxonomy] [R: research_notes/DM craft TTRPG design AI tools/ai_gm_academic_research.md §Consistency and Long-Horizon]
- **Distance between planting and contradiction varies by error type.** Geographical contradictions have the
  largest average gap (**31.0%** of story length). Perspective confusions have the smallest (**4.7%**). Facts
  are usually planted at 15–30% of the normalized position, and contradictions cluster at 40–60%. Errors
  accumulate about **linearly with output length**. **Implication:** long-gap categories (geography, world
  rules, NPC knowledge) need the external store, while short-gap categories (tone, perspective) are local
  coherence. Geography must be stored state (a region/place graph), not remembered description. [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §What exactly is the "Lost in Stories" taxonomy]

### 00.C Numeric scales and attributes

- **Bounded accuracy (5e: about +5 at level 1 to about +11 at level 20) versus layered proficiency (PF2e: +1 per
  level on everything proficient, plus tier boosts).** The sources float an *untested inference* that constant,
  small bonus ranges may be easier for an LLM to track than layered tiers. **For 00's numeric scale:** the
  project's d20 + small modifier vs DC 10/15/20/25 baseline is bounded-accuracy-shaped. That is consistent with
  the inference, but the inference is unverified. Constitution II also asks the ruleset to *exploit* AI capacity
  for complexity, which the tool layer can absorb, so the "AI-friendliness" argument weakens once math is `[D]`.
  [R: research_notes/DM craft TTRPG design AI tools/major_system_design_lessons.md §AI-GM Runability] [R: research_notes/DM craft TTRPG design AI tools/major_system_design_lessons.md §Head-to-Head] [R: reports/DM craft TTRPG design AI tools.md §Major systems' 2024-era] [C:II]
- **Attribute arbitrage** (GURPS): a flat bonus to a broad attribute is cheaper than raising narrow skills one
  by one, so a 40-point narrowly optimized fighter can "chop into kindling" a 200-point generalist. **Warns 00
  and 02:** if broad attributes and narrow competencies both add to rolls, their relative cost and their
  coverage have to be audited together, or broad attributes become the dominant investment. [R: reports/DM craft TTRPG design AI tools.md §Four candidate mechanics] [R: research_notes/DM craft TTRPG design AI tools/cost_systems_and_move_based_abilities.md §Cross-System Summary]
- **Hard caps as backstops** (M&M Power Level caps attack, damage, dodge/parry and toughness; D&D's standard
  ability-score ceilings). These are named as the first of five exploit-prevention levers. **For 00:** every
  numeric scale should declare a hard ceiling. [R: research_notes/DM craft TTRPG design AI tools/cost_systems_and_move_based_abilities.md §What specific design techniques prevent point-buy exploits]

### 00.D Tags as retrieval keys (tag-tree top levels)

- **Lorebooks use tag-triggered insertion.** SillyTavern: "Lorebook: retrieval-augmented generation of context;
  supports tags and dynamic insertion". NovelAI Lorebook: persistent world/character knowledge injected
  alongside generation, which the sources credit with improving coherence over context-only play. Pattern 5:
  "entries injected when tags match context". **Digest-author note:** 03's hierarchical tag vocabulary could
  double as the retrieval key for lore, NPC and rule entries. One vocabulary would then serve both evidence
  capture and context injection. That argues for choosing top-level tags that are also useful *scene*
  descriptors (e.g. martial / arcane / social / wilderness / craft), not only character-evidence descriptors.
  [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Community-Oriented Roleplay Platforms] [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §AI-Driven Interactive Fiction Platforms] [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Key Architectural Patterns]

### 00.E Glossary / rule-kind conventions

- **`[D]` rules can be scored against ground truth. `[J]` and `[N]` rules can only be judged by another model,
  and those judgments are noisy.** RPGBench's human–LLM-judge agreement on the subjective metrics was weak
  (Pearson r ≈ **0.129** for factual consistency and ≈ **0.140** for interestingness, on 20 games). The
  deterministic MEC metric needs no judge. **Implication:** wherever a rule can be `[D]`, it can be tested and
  audited mechanically. Every `[J]` rule is only as checkable as its criteria and worked examples are precise.
  This is more evidence for the BRIEF's "lean toward `[D]`". [R: research_notes/Long horizon LLM narrative benchmarks/rpgbench.md §which models/architectures] [R: research_notes/Long horizon LLM narrative benchmarks/rpgbench.md §metrics]
- **Rules text itself bloats when it is vague.** 13th Age's Icon Connection rules were "too vague". Experienced
  GMs converged on ad hoc house interpretations, and the 2nd edition had to expand the section **from 3 pages to
  about 60 pages** of examples and clarification. **Warns:** a vague rule does not stay small; it grows later
  under pressure. **Supports:** the BRIEF's worked-examples-everywhere and crisp-boundary mandate, and it also
  counts as a Principle VI concern (rules text needs consolidation too). [R: reports/DM craft TTRPG design AI tools.md §Major systems' 2024-era] [R: research_notes/DM craft TTRPG design AI tools/major_system_design_lessons.md §13th Age Design Mechanics] [C:VI]

---

## 01 — Resolution (capability gate, when to roll, DCs, modifiers, degrees, graduated reveal, compound/extended/opposed/group, help, advantage)

### 01.A Degrees of success

- **PF2e's four-degree margin rule is the strongest fit for an AI adjudicator. It needs zero judgment calls.**
  Critical success at total ≥ DC+10. Success at total ≥ DC. Failure below DC. Critical failure at total ≤ DC−10.
  A natural 20 moves the result **one degree better** and a natural 1 **one degree worse**, "regardless of the
  numeric margin". Some actions have stronger effects on a crit (a Strike deals **double damage**). The DMR
  verdict: "should move from candidate to near-default". It "generalizes cleanly to 'did the improvised action
  work'". Its only documented cost is that tight, fully audited math "makes individual bonuses feel less
  impactful". [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §How does Pathfinder 2e's four-degree system work] [R: reports/DM craft TTRPG design AI tools.md §Four candidate mechanics] [R: reports/DM craft TTRPG design AI tools.md §Updated primitive list] [C:P8]
- **Digest-author note: the project's natural-20 rule is stronger than PF2e's, and the ladder produces large
  critical-failure bands at the default modifier.** BRIEF §7 makes a natural 20 an automatic *critical success*
  and a natural 1 an automatic *critical failure*. PF2e *shifts by one degree* instead. The two rules differ
  only when a natural 20 would still miss the DC (DC ≥ 23 at +2) or a natural 1 would still meet it. At the
  ladder's "very hard" DC 25, a +2 character under the **project rule** gets 5% critical success, 0% success,
  30% failure and **65% critical failure**. Under **PF2e's shift rule** the same natural 20 (total 22) becomes a
  plain *success* (5%), with 0% crit. The full project-rule distribution at +2:

  | DC | Crit success | Success | Failure | Crit failure |
  |---|---|---|---|---|
  | 10 | 15% (nat 18–20) | 50% (8–17) | 30% (2–7) | 5% (nat 1) |
  | 15 | 5% (nat 20) | 35% (13–19) | 45% (4–12) | 15% (1–3) |
  | 20 | 5% (nat 20) | 10% (18–19) | 45% (9–17) | 40% (1–8) |
  | 25 | 5% (nat 20) | 0% | 30% (14–19) | 65% (1–13) |

  Two consequences for 01 and 07. (a) A "hard" or "very hard" DC at the default +2 critically fails 40–65% of
  the time, so a crit-fail consequence table has to fit **telegraphed** lethality (BRIEF §4). Crit failure must
  not mean "worse harm" by default at high DCs, or hard tasks become death traps. (b) The auto-crit natural 20
  lets a +2 character *critically succeed* at a task the DM set to DC 25 precisely because it should be barely
  possible (the probe's "10 attacks in one action" ruling). PF2e's shift would give a plain success. 01 should
  choose deliberately. (Arithmetic: d20 uniform; each face is 5%.)
- **Fate Core's four outcomes put the tie in its own non-punishing band.** Results are Fail (below
  opposition), **Tie** (equal: you get what you want *at a minor cost*, or a lesser version of it), Succeed
  (1–2 shifts above), and **Succeed with Style** (3+ shifts; the notes say "win by more"). The ladder runs from
  +8 Legendary to −2 Terrible. The tie exists "specifically to keep play moving even on an even roll". **For
  01:** a "success at a cost" band right around the DC is a proven anti-stall device. Compare P16's
  soft-lock finding. [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §How do OTHER systems implement graduated] [R: reports/DM craft TTRPG design AI tools.md §Four candidate mechanics]
- **Blades in the Dark's Position × Effect sets two independent axes *before* the roll.** Position is
  controlled / risky / desperate ("how bad can things go?"). Effect is limited / standard / great ("how much will
  this achieve?"). That gives **9 framings** before dice. The 1d6 result (critical / success / partial / failure)
  then resolves inside the frame. **Cost for an AI:** the GM (here, the AI) has to set the framing variables,
  which is judgment `[J]`. **Value for this project:** announcing Position before the roll is a ready-made
  **telegraphing** device for lethal risk (BRIEF §4: "explicit warnings before lethal risk"). → see 07. [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §How do OTHER systems implement graduated] [R: reports/DM craft TTRPG design AI tools.md §Four candidate mechanics]
- **Genesys/Star Wars narrative dice make success/failure and advantage/threat orthogonal, cancelling currencies.**
  One roll can produce "success with a complication" or "failure with an unexpected benefit", which a single
  degree number cannot express. **For 01:** a secondary *side-effect* axis (independent of the success degree)
  is the documented answer to "I did it, but something else happened". Cheap version: a separate
  complication/boon result keyed off die faces, independent of margin. [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §How do OTHER systems implement graduated] [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §documented tradeoffs]
- **World of Darkness dice pools get degrees by counting successes, not by thresholds.** Roll (attribute + skill)
  d10s, and each die at or above the target number counts as a success. Classic WoD uses TN 6 by default
  (adjustable), and ones cancel successes. New WoD fixes TN 8 and drops the ones-cancel rule. Degrees scale with
  character power without any extra rule. **For 01:** this is the alternative to fine-tuned DC math. It is noted
  here for completeness because the project's d20 baseline is already validated. [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §How do OTHER systems implement graduated] [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §documented tradeoffs]
- **"The most interesting narrative lies in the sweet spot of partial success."** Degree systems create
  succeed-at-a-cost space that binary pass/fail does not. Capacle also argues that ten binary choices produce
  **1,024** paths, and that degree systems reduce branching "by having fewer distinct outcomes". **Digest-author
  note:** that second argument is dubious as stated, since more degrees mean more branches per roll. Treat it as
  rhetoric. [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §documented tradeoffs]
- **Trend observation:** resolution systems drift toward multi-axis designs (success plus an independent
  side-channel) or degree counts as they mature. Tactical systems (PF2e, 4e) use fixed degree counts because they
  can be precisely balanced. Narrative systems (Fate, Blades) use degrees mainly to avoid binary stagnation.
  [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §Research Notes Summary] [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §documented tradeoffs]

### 01.B The capability gate (Principle VII) and adjudicating novel actions

- **No published research addresses fairness in adjudicating a player's novel, rules-unanticipated action.**
  Two targeted searches found nothing. There are no studies comparing strict versus fairness-balancing
  interpretation, and no benchmark for letter-versus-spirit rule conflicts. The DMR recommends naming it
  explicitly as an unsolved problem rather than assuming a judge-gate handles it "by extension". **Implication:**
  01's capability-gate procedure is original design work. It needs its own worked examples on both sides of
  every boundary, and 12 needs an error-correction path. [R: research_notes/DM craft TTRPG design AI tools/ai_gm_academic_research.md §Fairness in Adjudicating Novel] [R: reports/DM craft TTRPG design AI tools.md §The tools landscape] [R: reports/DM craft TTRPG design AI tools.md §What this round changes]
- **The practical target is *perceived locus of control*, not statistical correctness.** arXiv:2502.19519:
  "the same AI capability was acceptable when it expanded valued play experiences, but problematic when it
  appeared to take over judgment, authorship, or player choice". Self-determination theory names autonomy and
  competence as the central needs. Dynamic balancing or recommendations were resisted when they reduced
  meaningful choice or made an achievement feel less earned. The DMR concludes the fix "may need to be as much
  about how a ruling is *framed and explained*" as about how it is computed. **For 01/VII:** a decline or
  redirect should say *why* (which license is missing) and *what is possible instead*. That matches BRIEF §3's
  "must always redirect toward what is possible". [R: research_notes/DM craft TTRPG design AI tools/ai_gm_academic_research.md §Fairness in Adjudicating Novel] [R: research_notes/DM craft TTRPG design AI tools/ai_gm_academic_research.md §Player Experience and Comparative] [R: reports/DM craft TTRPG design AI tools.md §The tools landscape] [C:VII]
- **NCP-Bench's player-input rule separates "saying no in-world" from "ignoring the player".** The auditor
  counts it as **not** a violation when the narrator denies, redirects, interrupts, or turns a request into
  in-world friction, resistance or failure, **as long as the player's intent is directly acknowledged**. A
  player-input conflict fires only when the response (a) substantially ignores the input, (b) swaps in a
  different intention, (c) contradicts an explicit refusal or self-limit the player stated, (d) silently resets
  a state change the player's action implied, or (e) gives only token acknowledgment without concrete in-world
  follow-through. **This is almost a ready-made acceptance test for Principle VII declines:** acknowledge the
  intent, then redirect with concrete follow-through, and never swap in a different action. [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §What exactly is "Narrative Commitment Preservation" (NCP)] [C:VII] [C:P16]
- **High-sensitivity attributes need explicit justification before they are upgraded.** NCP's auditor requires
  explicit justification before a narrator upgrades **perception, memory, mobility, control, access, awareness
  or freedom**. **Digest-author note:** this is an externally derived list of exactly the dimensions where
  generous narration causes impossible outcomes (seeing through walls, remembering unlearned lore, flying,
  dominating minds, entering sealed places, sensing hidden things, escaping bonds). 01 could use it as the
  default "requires a license" checklist beyond the basic-action tier. [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §What exactly is "Narrative Commitment Preservation" (NCP)] [C:VII]
- **"Yes, and…" as the default posture, with an outright "no" reserved for what breaks the world or the rules.**
  Variants: **"Yes, but…"** (accept the premise, attach consequences, or subvert it to preserve established
  continuity); **"Yes, and…"** (fold it into plans); **strategic "No"** (only after trust has been built by
  frequent acceptance). **For 01:** this lines up with VII if "the rules" means "the license check". The gate
  says *no* only to unlicensed capability. It says "yes, but" to the fictional premise wherever the premise is a
  licensed or basic action. → see Tensions T-6. [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Core Principles of Good Dungeon Mastering]
- **Fudging is a named DM mistake.** So are changing DCs in the monsters' favor and traps that "always counter the
  player characters". **For 01:** set DCs and framings *before* rolling (as Blades does), record them, and never
  change them after seeing the die. This also serves goal 2 ("keeps state true"). [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Common Dungeon Master Mistakes]
- **Precondition checking catches silent capability errors.** RPGBench's GameChecker flags any event the model
  fired whose `entering_condition` was **not true in the previous state**. It then checks `succeed_condition`
  before applying success effects, and checks that it was false before applying failure effects. **Digest-author
  note:** this is the mechanical form of VII. "Can you attempt this" is a precondition over current state
  (licenses held, position, resources), and it can be checked against the *prior* state as a `[D]` step wherever
  the license is a recorded field. [R: research_notes/Long horizon LLM narrative benchmarks/rpgbench.md §state-tracking/memory specifically] [C:VII]
- **"Forcibly Changing Reality" is a named top-4 failure:** the narrator silently rewrites or erases a
  previously completed player action. **For 01:** once a result is resolved and recorded, it is final. Later
  narration may add consequences but may not quietly reverse it. [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Failure modes] [R: reports/Long horizon LLM narrative benchmarks.md §Fact conflicts, not plot]
- **Letter versus spirit conflicts are unbenchmarked.** A novel action can fit the letter of one rule while
  violating the spirit of another. No research addresses this. **For 01:** state a precedence rule (e.g. the
  more specific rule wins; a license's literal text beats a general permission). → see Gaps G-2. [R: research_notes/DM craft TTRPG design AI tools/ai_gm_academic_research.md §Fairness in Adjudicating Novel]
- **Framing shapes LLM behavior.** "The Story Shapes the Agent" (arXiv:2607.18566) reports that narrative
  context and framing significantly change LLM decisions. The ACAD reading: *how rules and story context are
  framed affects GM adjudication*. **For 01:** the capability gate should be evaluated on a neutral restatement
  of the attempted action (what exactly is attempted, what it requires), not on the player's dramatic phrasing.
  [R: research_notes/DM craft TTRPG design AI tools/ai_gm_academic_research.md §Additional Relevant Research Areas]

### 01.C Compound, extended, repeated and multi-attack actions

- **Diminishing returns on repeated attempts inside one turn.** PF2e's multiple-attack penalty is −5 on the
  second Strike and −10 on the third (agile weapons −4 and −8). It exists to stop "just attack three times" from
  being the dominant play. **For 01's compound-action rule:** the probe's "compress 10 attacks into one action"
  improvisation (throttled, DC raised to 25) has a published analogue. Repetition carries an escalating penalty
  per extra attempt, not a flat DC bump. [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §How do different systems structure what a character can do] [BRIEF §7]
- **Re-attempts are not free.** Constitution P17 already requires that re-asking a bundled question costs
  something. The DM-craft sources add the pacing angle: "skip empty time", so an unchanged-situation retry
  should advance clocks or time instead of repeating the roll for free. [C:P17] [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Core Principles of Good Dungeon Mastering]
- **Post-roll choice.** 13th Age fighters "pick what power they use after they attack", and even a poor pick
  still deals damage, so there are no trap choices. **For 01/06:** some abilities can key off the *rolled
  result* (natural value or degree) rather than being declared beforehand. That is a deterministic
  trigger-to-outcome mapping, P10-safe. [R: research_notes/DM craft TTRPG design AI tools/major_system_design_lessons.md §13th Age Design Mechanics] [C:P10]

### 01.D Graduated reveal (P17) and epistemic pacing

- **The knowledge-tree detective game is the implementation precedent for gating information by state.** A
  tri-agent pipeline (knowledge retrieval, dialogue generation, response verification) is constrained by a
  knowledge tree that encodes **what an NPC is permitted to reveal given the current narrative state**. It cut
  critical hallucinations by **64.78%** and **entirely prevented premature disclosure**, at a cost in
  conversational naturalness ("forced conversational reveals"). **For 01 (P17 in resolution) and 10
  (investigation):** reveal budgets should be state-bound. Degree of success chooses *how many* permitted nodes
  are revealed, and the tree decides *which* are permitted at all. [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §Other 2025–2026 benchmarks] [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §Mitigation strategies: quantified evidence] [R: research_notes/DM craft TTRPG design AI tools/ai_gm_academic_research.md §Additional Relevant Research Areas] [C:P17]
- **"Triggering Unknown Facts" is NCP's #2 failure category:** disclosing information the chronology says
  should not be known yet. **Rules out:** a reveal procedure that lets degree of success exceed what the world
  state permits. A crit on "what does the sealed letter say?" before anyone has the letter reveals nothing
  inside it. [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Failure modes]
- **POV compliance.** NCP's trajectory construction forbids omniscient narration. Information must be what the
  player-role character could plausibly know or observe. **For 01/12:** descriptions and reveals are filtered
  through what the PC can perceive. The high-sensitivity attributes (01.B) define the exceptions. [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Methodology for constructing test scenarios]

### 01.E Help, group, opposed, advantage-type mechanics

- **Skill challenges are the paradigm "needs several inputs" structure.** They require input from multiple
  players by construction. **Digest-author note:** in single-player v1, the equivalent is a multi-step extended
  task that needs *different approaches or tags* from the one character (or companions), which also serves the
  single-player spotlight reinterpretation in 12. [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Spotlight Balance] [R: reports/DM craft TTRPG design AI tools.md §Spotlight balance and challenge diversification]
- **Blades "push yourself":** pay **2 stress** to get **+1d**, **+1 effect**, or to **act despite harm**. Some
  special abilities let you get the push benefit without paying stress. **For 01:** a player-chosen, resource-paid
  bonus (e.g. spending Focus for +N or a step of effect) is a proven "try harder" valve. It also gives Focus
  (P9) a universal use beyond abilities. → see 05. [R: research_notes/DM craft TTRPG design AI tools/cost_systems_and_move_based_abilities.md §How does Blades in the Dark structure its special abilities]
- **Fate stunt bonus:** "+2 to skill total" under narrowly defined circumstances. This is the canonical
  situational-bonus size for a stunt-style specialization. [R: research_notes/DM craft TTRPG design AI tools/cost_systems_and_move_based_abilities.md §How does Fate Core's "stunts" system work]
- **Advantage/disadvantage (5e)** is only named in the sources, as one of the mechanics whose AI-adjudication
  difficulty is *unstudied*. No evidence either way. → see Gaps G-12. [R: research_notes/DM craft TTRPG design AI tools/major_system_design_lessons.md §AI-GM Runability]

---

## 02 — Character (creation procedure, attributes, origins, birth variance and deferred reroll, baseline floor, starting kit)

- **Decision paralysis is a documented, game-halting failure, not a matter of taste.** Too many choices, or
  choices whose outcomes are too complicated, cause analysis paralysis that "grinds the entire game to a halt".
  At creation, early choices cascade through every later advancement, so "what you choose at the start can make
  the difference between a great game and a rage quit". **For an AI DM:** the INDIE inference is that the AI
  "cannot directly prompt the human for a faster decision" the way a human GM says "just pick something, we'll
  adjust", so the system needs **aggressive defaults or a strict hierarchy for presenting options**, baked in
  structurally. → see Tensions T-3 regarding BRIEF §3. [R: research_notes/DM craft TTRPG design AI tools/indie_niche_ttrpg_design_theory.md §Decision Paralysis] [R: reports/DM craft TTRPG design AI tools.md §Indie design theory]
- **Dual-path creation (Baldur's Gate 3):** casual players can "speedrun the character sheet", while the full
  depth stays open to those who want it. The INDIE summary makes this a principle: offer both a template path
  and a modular expert path. **For 02:** a "quick build" path (a named origin plus defaults, playing within 1–2
  exchanges) *and* a full build path. This does not simplify the rules. It sequences how they are presented. [R: research_notes/DM craft TTRPG design AI tools/indie_niche_ttrpg_design_theory.md §Decision Paralysis] [R: research_notes/DM craft TTRPG design AI tools/indie_niche_ttrpg_design_theory.md §Summary]
- **Characters must have "a need and desire to join in the story" and must not be built so they veto it**
  (Robin's Laws). The INDIE summary also says to "require story justification for character builds". **For 02:**
  creation should output story hooks (drives, ties, a debt, an enemy, a question) that 11's hook generator can
  consume. Precedents: Dungeon World **bonds** ("where the class' outlook shines through"), 13th Age **One Unique
  Thing** (distinctive, usually non-combat, "provides the raw materials for adventures and campaign arcs") and
  **Icon Relationships** (3 points spread across relationships with the setting's great powers). [R: research_notes/DM craft TTRPG design AI tools/indie_niche_ttrpg_design_theory.md §Robin's Laws] [R: research_notes/DM craft TTRPG design AI tools/indie_niche_ttrpg_design_theory.md §Dungeon World] [R: research_notes/DM craft TTRPG design AI tools/cost_systems_and_move_based_abilities.md §13th Age and Savage Worlds] [R: research_notes/DM craft TTRPG design AI tools/major_system_design_lessons.md §13th Age Design Mechanics]
- **13th Age balances distinctiveness narratively, not with a shared currency.** One Unique Thing and Icon
  relationships have no point pool to arbitrage, so they avoid the whole class of point-buy exploits. **For 02
  origins (P4):** narrative-only distinctives (a unique fact about you, a relationship with a faction) can be
  unconstrained by points, *provided* they carry no mechanical power. Once they carry power, they need audited
  cost. → see 02 point-buy bullets. [R: reports/DM craft TTRPG design AI tools.md §Four candidate mechanics] [R: research_notes/DM craft TTRPG design AI tools/cost_systems_and_move_based_abilities.md §13th Age and Savage Worlds]
- **Archetype incompleteness: can the system build the iconic characters players want?** Iron Kingdoms RPG:
  players can't reproduce famous characters from the setting's own miniatures game. Mage: the Ascension looks
  like it supports many wizard archetypes, but a classic **necromancer** (controlling ghosts, raising zombies)
  needs many separate magical abilities most starting characters can't have. **For 02/04:** audit the
  origin-plus-early-emergence path against a list of classic-fantasy iconic archetypes (knight, ranger,
  necromancer, thief, priest, bard, druid, witch, monk, paladin, warlock/pact-maker, alchemist, beast-tamer,
  duelist, etc.). Each should be *pursuable from session one*, even if recognition comes later. [R: research_notes/DM craft TTRPG design AI tools/indie_niche_ttrpg_design_theory.md §Indie Communities and Common Character Customization Mistakes] [R: reports/DM craft TTRPG design AI tools.md §Indie design theory]
- **Ability tax:** an option presented as optional that is actually mandatory, because it is overpowered or
  because a build doesn't work without it. 5e examples: Sharpshooter and Great Weapon Master (−5 to hit / +10
  damage) "feel mandatory". Grappler, Athlete and Dual Wielder are "rarely worth taking". "Having a feat so good
  that it feels like you're missing out if you don't take it removes the purpose of a customizable system."
  **For 02:** no attribute, origin or starting option may be a tax. The audit test is whether a competent
  player would ever reasonably skip it. [R: research_notes/DM craft TTRPG design AI tools/indie_niche_ttrpg_design_theory.md §Indie Communities and Common Character Customization Mistakes] [R: research_notes/DM craft TTRPG design AI tools/major_system_design_lessons.md §D&D 5e Balance Problems]
- **Point-buy is the riskiest customization mechanic without guardrails** (P11 context). Evidence from four
  directions:
  **GURPS:** a flat pool "creates identity, not balance". Attribute arbitrage (broad attributes are cheaper than
  narrow skills). Disadvantage gaming (taking flaws with little effect on play). An "eagle-eyed GM" is the only
  stopgap.
  **M&M:** does not *prevent* disparity. It *contains* it with Power Level caps (15 power points per PL; PL10 is
  the default "Marvel team book"; DC-style heroes 14–16). Novices still build lopsided characters, e.g. "a
  detective made of water" next to an optimized Superman.
  **HERO:** the most exploit-resistant of the family. Discrete cost brackets (base 1d6 effect = 5 points;
  Dispel 3/die, Drain 6/die, Killing Attack 15/die). Defense costs less than offense. Limitations reduce cost.
  Forced spending across skills, disadvantages and powers.
  **Savage Worlds:** forced zero-sum. Start at 0. Hindrances grant points (Minor 1, Major 2), capped at 1 Major
  and 2 Minor. Edges cost 2. The sheet must balance to exactly 0.
  **Verdict (DMR):** adopt HERO-style brackets with forced distribution, or Savage-style zero-sum, *wholesale*,
  or use no shared point pool at all and rely on closed slot combinatorics. **Rules out:** any unaudited shared
  point pool in 02. [R: reports/DM craft TTRPG design AI tools.md §Four candidate mechanics] [R: research_notes/DM craft TTRPG design AI tools/cost_systems_and_move_based_abilities.md §How does Mutants & Masterminds' point-buy system work] [R: research_notes/DM craft TTRPG design AI tools/cost_systems_and_move_based_abilities.md §HERO] [R: research_notes/DM craft TTRPG design AI tools/cost_systems_and_move_based_abilities.md §13th Age and Savage Worlds] [R: research_notes/DM craft TTRPG design AI tools/cost_systems_and_move_based_abilities.md §Cross-System Summary] [C:P11]
- **Five exploit-prevention levers** (usable as a checklist if 02 uses any currency): (1) hard caps on
  individual stats or powers; (2) tiered cost brackets that stop continuous arbitrage; (3) forced distribution
  across categories; (4) meaningful disadvantages; (5) asymmetric costs (defense cheaper than offense). Plus
  **diminishing returns** (costs rise as a stat rises). Effective systems combine several. [R: research_notes/DM craft TTRPG design AI tools/cost_systems_and_move_based_abilities.md §What specific design techniques prevent point-buy exploits]
- **Disadvantages are a canary.** If a flaw grants points only at creation and is then "forgotten" in play, it
  becomes exploitable flavor. If it costs something, or becomes a story focus, players play it. **For 02:** any
  origin drawback must have a mechanical trigger that 12's DM loop actually fires (a `[D]` or `[J]` rule with
  criteria), not flavor text. [R: research_notes/DM craft TTRPG design AI tools/cost_systems_and_move_based_abilities.md §What specific design techniques prevent point-buy exploits]
- **Don't front-load options. Distribute them across the growth curve** (PF2e: mechanical options spread across
  all 20 levels, with low levels as a "game tutorial"). Jason Bulmahn: "If you have to spend a great deal of time
  creating a character or reading a manual, that's a time investment that you have to sink in before the fun can
  begin." Options should be "proper choices, not a hidden subgame of 'avoid making an incompetent character'".
  **For 02 and P2's baseline floor:** starting choices must not be able to produce an incompetent character. The
  floor exists so that no creation path is a trap. [R: research_notes/DM craft TTRPG design AI tools/major_system_design_lessons.md §Pathfinder 2e Design Philosophy] [R: reports/DM craft TTRPG design AI tools.md §Major systems' 2024-era] [C:P2]
- **Breadth versus competence.** This is not in these sources. It is constitution P4 (Mistborn). The Dungeon
  World note is related: "D&D classes are generally too broad to make effective playbooks", so narrow thematic
  archetypes work better as creation anchors. [R: research_notes/DM craft TTRPG design AI tools/indie_niche_ttrpg_design_theory.md §Dungeon World] [C:P4]
- **Dungeon World's modular creation:** an archetype plus **2–3 specialties** (per the "Class Warfare"
  supplement), instead of choosing from inside one broad, bloated class. **For 02 origins:** "origin + 2–3
  background specialties" is a precedent shape that stays enumerable. [R: research_notes/DM craft TTRPG design AI tools/indie_niche_ttrpg_design_theory.md §Dungeon World] [R: reports/DM craft TTRPG design AI tools.md §Indie design theory]
- **Session Zero** covers theme and tone, expected duration, schedule, absence policy, house rules, and **hard
  and soft limits** (hard: never crossed; soft: acceptable in moderation). **For 02's creation procedure (solo
  v1):** creation is the natural place for the one-player session zero: tone dials, content limits, and
  preferred play mix (→ 12.B player-type model). Autonomous AI facilitation of session zero is an *unstudied*
  gap. [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Core Principles of Good Dungeon Mastering] [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Translating Human GM Skills to AI]
- **Robin's Laws player types** (power gamer, butt-kicker, tactician, specialist, method actor, storyteller,
  casual gamer) and the **Player Goal Chart** (archetype, goals, planned actions per player). **For 02:** creation
  can record the player's stated preferences as state 12 uses for challenge rotation. Laws on character build:
  power gamers need visible optimization paths, and butt-kickers want simple, combat-ready characters (INDIE
  inference). [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Spotlight Balance] [R: research_notes/DM craft TTRPG design AI tools/indie_niche_ttrpg_design_theory.md §Robin's Laws]
- **Gear must not outclass innate abilities.** "Players dislike losing things they spent points on." If gear is
  stronger than innate options, the GM is stuck choosing between overpowered gear and underpowered characters.
  **For 02's starting kit:** starting gear gives utility and access, not the bulk of a character's power. → see 08. [R: research_notes/DM craft TTRPG design AI tools/indie_niche_ttrpg_design_theory.md §Indie Communities and Common Character Customization Mistakes]
- **Crunch is a tone signal.** Crunch appeals to butt-kickers, tacticians and power gamers. The usual
  recommendation is modular optional layers "rather than one universal complexity dial". The AI's internal
  simulation "can run deeper than what it exposes". Errant's specialized procedures (for estates and legal
  trials) show situation-specific crunch deepening immersion. **For 02 and 14:** depth can be exposed on demand
  (codex) and never forced. That is consistent with BRIEF §3's "player-facing complexity is not a constraint",
  since the complexity exists and is merely sequenced. [R: research_notes/DM craft TTRPG design AI tools/indie_niche_ttrpg_design_theory.md §Crunch vs. Playability] [R: reports/DM craft TTRPG design AI tools.md §Indie design theory]

---

## 03 — Tags & Evidence (tag vocabulary, `tag_event` capture, tallies, weighting, recency)

- **Record only what is conclusively established.** NCP's `fact_update` discipline: after each narrator turn,
  compare pre-turn facts against the new output. **Add** a fact only if it is *conclusively established*, not
  merely attempted or foreshadowed, and only if it is logically atomic and not a duplicate. **Remove** a fact
  only if it is *explicitly and non-speculatively invalidated*. Output `{new_facts, facts_to_remove,
  justification}`. **Direct template for `tag_event`:** an evidence record should require (a) that the deed was
  actually completed, (b) that it is atomic (one deed, one event), (c) a written one-line justification naming
  the tags and why. An *attempt* that failed may still be evidence of the *attempt's* tags if that is the rule,
  but it must be recorded as an attempt, never as a success. [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Methodology for constructing test scenarios]
- **Atomicity.** NCP trajectory nodes must be *atomic*: exactly one logical turning point, with "compound causal
  stages" explicitly prohibited. **For 03:** a compound action ("I talk my way past the guard, pick the lock and
  slip inside") generates separate evidence events per atomic deed. That keeps tallies honest and makes
  hierarchical cascade (P5) countable. [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Methodology for constructing test scenarios] [C:P5]
- **Anchor evidence to an observable world-state change.** NCP's `key_delta` must be "a factual, observable, or
  otherwise judgeable change at the world-state level", *not* a mental-state-only change. The rule exists so
  that another model can audit it. **Tension with P5**, which counts values-expressive choices with no dice
  behind them. **Digest-author reconciliation:** record the *expressed* choice as an observable act (what the
  character said or did: spared the thief, refused the bribe, kept the oath publicly) rather than an inferred
  inner state. → see Tensions T-9. [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Methodology for constructing test scenarios] [R: reports/Long horizon LLM narrative benchmarks.md §NCP-Bench proves synthetic construction] [C:P5]
- **No credit for skipped prerequisites.** NCP commitment extraction forbids "logical leaps", where a player
  skips a prerequisite investigative step and a commitment still counts as satisfied. **For 03/04:** evidence
  toward deep or advanced tags should not accrue from deeds that skip the tag's foundations, unless the rule
  explicitly allows it. [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Methodology for constructing test scenarios]
- **Tallies must be engine state, never recalled.** Temporal/updated facts are the weakest category (LOCOMO
  temporal < single-hop; embedding retrieval on updated facts 0.30–0.95), and models use correctly retrieved
  facts only 55% of the time. **Rules out:** any tally, recency window or weight the DM "keeps in mind". All
  counters are `[D]` fields written by `tag_event` and read by the recognition check. → see 00.A. [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §Other 2025–2026 benchmarks] [R: reports/Long horizon LLM narrative benchmarks.md §Degradation is fast]
- **Recency and obsolescence.** FAMA (Forgetting-Aware Memory Accuracy) specifically *penalizes relying on
  obsolete or invalidated memory*. Memora found "frequent reuse of invalid memories and failures to reconcile
  evolving memories". NCP's auditor applies "visible continuity priority" (the most recently established state
  wins over older narration). **For 03's recency rule:** evidence can be *superseded* (a redeemed oath-breaker)
  as well as decayed. Superseding must be an explicit logged event, not something the model infers. [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §Other 2025–2026 benchmarks] [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §What exactly is "Narrative Commitment Preservation" (NCP)]
- **Neutral recording guards against framing bias.** Narrative framing measurably shifts LLM decisions ("The
  Story Shapes the Agent"). **For 03:** the significance judgment (P5: base-model judgment) should be made on a
  neutral restatement of the deed ("Character struck the final blow on an armed human who had surrendered"), not
  on the scene's dramatic prose. That reduces drift in what counts as evidence. [R: research_notes/DM craft TTRPG design AI tools/ai_gm_academic_research.md §Additional Relevant Research Areas] [C:P5]
- **The tag vocabulary can double as retrieval keys** (→ see 00.D). Lorebook systems inject entries whose tags
  match the current context. **Digest-author note:** a single hierarchical vocabulary used both for evidence and
  for scene retrieval gets exercised constantly. That is good for consistency, as long as the evidence semantics
  stay separate from retrieval semantics (a scene tagged `arcane` is not evidence that the PC did arcane things). [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Key Architectural Patterns]
- **Where evidence data can double as the spotlight ledger.** The DMR's "per-player spotlight ledger" asks for a
  queryable record of which character facets have "had their moment". **Digest-author note:** in single-player
  v1, 03's tallies of *which tags have been exercised recently* are exactly the data a facet-rotation rule needs
  (→ 12.B). 03 should expose "last exercised" timestamps per top-level tag. [R: reports/DM craft TTRPG design AI tools.md §Spotlight balance and challenge diversification] [R: reports/DM craft TTRPG design AI tools.md §Updated primitive list]
- **Hierarchical tag cascade** (PoE) and Paladin/Fable judgment precedent come from the constitution, not from
  these sources. These sources add no tag-vocabulary content. → see Gaps G-10. [C:P5]

---

## 04 — Recognition & Growth (classes, scoring, grant/offer/abstain, tiers, crystallization, provisional status, consolidation)

- **Passive, always-available abilities are forced to be weak. Put power in active or conditional triggers.**
  13th Age 1e Ranger: "abilities that were always available … had to be terrible" for balance. Players found
  the class dull next to a flexible Wizard. One player was "disappointed by how much cooler the redesigned Wizard
  was". The 2e fix turned static always-on abilities into conditional/active ones that "do a lot more damage".
  The DMR makes it a rule: build power from **active, situational triggers**, not passive stat bonuses.
  **Caveat (DMR):** inherently passive archetypes (turtling, buffing) will feel underpowered under this rule
  unless specifically exempted. **For 04 tiers:** a tier's added potency should mostly be active or conditional.
  [R: reports/DM craft TTRPG design AI tools.md §Major systems' 2024-era] [R: reports/DM craft TTRPG design AI tools.md §Updated primitive list] [R: research_notes/DM craft TTRPG design AI tools/major_system_design_lessons.md §13th Age Design Mechanics] [C:P5]
- **Power can branch instead of stacking** (Fate **stunt families**). *Stacking* makes the original stunt more
  powerful. *Branching* adds thematically related but mechanically distinct abilities *without modifying the
  prerequisite*. Stunt families let power grow "by branching into new flavors rather than by stacking raw
  numbers". **For 04 and Principle VI:** tier deepening can be expressed as branching forks that *replace* or
  *transform* (as in DCC's specialization forks in the constitution), not additive stacking. Stunt families show
  prerequisite chains that "prevent standalone super-powerful abilities". [R: research_notes/DM craft TTRPG design AI tools/cost_systems_and_move_based_abilities.md §How does Fate Core's "stunts" system work] [R: reports/DM craft TTRPG design AI tools.md §Four candidate mechanics] [C:VI]
- **Each step up should add something qualitatively new, not "more of the same".** 5e martials get "just more of
  the same" across stretches of levels while casters get "1–2 notable new spells". The MAJOR inference: casting
  provides both damage **and** utility while martial classes mostly provide damage. Spells scale qualitatively,
  martials scale linearly. **For 04:** every calling's tier ladder needs *utility and access* growth (new things
  you can attempt, i.e. VII licenses), not only numeric potency. Otherwise non-magical callings fall into 5e's
  martial/caster trap. [R: research_notes/DM craft TTRPG design AI tools/major_system_design_lessons.md §D&D 5e Balance Problems] [R: reports/DM craft TTRPG design AI tools.md §Major systems' 2024-era]
- **Audit every side of the balance ledger at once, and keep auditing.** The 5e 2024 revision added Weapon
  Mastery to every martial weapon and doubled healing-spell dice (Cure Wounds, Healing Word and the mass
  versions), but "new and updated spells made spellcasters even more powerful" (e.g. Conjure Minor Elementals
  "game-breaking", solo Wizards "vastly outpace" optimized martials, Spirit-Guardians-style spells for every
  full caster). Verdict: "the martial-caster divide persists". The failure: one arm was fixed without
  re-auditing the other. PF2e deliberately scaled back spells *and* buffed martial combat *at the same time*.
  The DMR upgrades "small closed primitives" from a heuristic to a **governance requirement: a standing audit
  process, not a one-time balance pass**. **For 04:** callings and hybrids are balanced as one ledger, and any
  change to one calling's numbers triggers a re-audit of all. [R: research_notes/DM craft TTRPG design AI tools/major_system_design_lessons.md §D&D 5e Balance Problems] [R: reports/DM craft TTRPG design AI tools.md §Major systems' 2024-era] [R: reports/DM craft TTRPG design AI tools.md §What this round changes] [R: reports/DM craft TTRPG design AI tools.md §Updated primitive list]
- **Tight balance can cost "feeling of power".** PF2e keeps "everyone … largely incapable of accomplishing
  anything of actual value alone" so nobody "carries the fight", and it punishes acting far outside a class's
  role. Some players read that as lost power. The DMR says to make the tradeoff "consciously rather than by
  accident". **For 04 (solo play):** "no one carries the fight" makes no sense with one PC. The PC *has* to be
  able to carry scenes, so the balance target is PC-vs-challenge, not PC-vs-PC. → see Tensions T-15. [R: research_notes/DM craft TTRPG design AI tools/major_system_design_lessons.md §Pathfinder 2e Design Philosophy] [R: reports/DM craft TTRPG design AI tools.md §Major systems' 2024-era]
- **Recognition must feel earned and chosen, not imposed.** Players resist AI recommendation or dynamic
  balancing when it "reduced meaningful choice or made achievement feel less earned", and AI is problematic
  when it "appeared to take over judgment, authorship, or player choice". **Supports** P5's three-valued
  grant/offer/abstain policy with "offer" for tiers (P2), and suggests the *grant* branch (high-confidence
  auto-grant) is the riskiest for locus of control. 04 might present even high-confidence recognitions as
  affirmable moments. [R: research_notes/DM craft TTRPG design AI tools/ai_gm_academic_research.md §Fairness in Adjudicating Novel] [R: research_notes/DM craft TTRPG design AI tools/ai_gm_academic_research.md §Player Experience and Comparative] [C:P2] [C:P5]
- **Excessive investment kills an option.** "Excessive investment for an option is one of the quicker ways to kill
  viability in that option." **For 04 thresholds:** a narrow specialist or rare hybrid whose recognition
  threshold is out of proportion to its payoff will never be pursued. Thresholds should be set so each calling's
  expected turns-to-first-recognition falls in a band (simulate it). [R: research_notes/DM craft TTRPG design AI tools/indie_niche_ttrpg_design_theory.md §Feat Bloat]
- **Supplement and feat bloat:** new publications make older options weaker or obsolete, and players have to
  track interactions across books. The INDIE summary recommends "clear power ceilings and deprecation policy".
  The "Without Number" series (Stars/Worlds Without Number) is cited as doing feats well ("most bang for their
  buck" with "sensible constraints"), but with no mechanical detail. **Supports** VI and the hard slot ceiling
  in P5. [R: research_notes/DM craft TTRPG design AI tools/indie_niche_ttrpg_design_theory.md §Feat Bloat] [C:VI]
- **Narrow thematic classes make better anchors than broad ones.** Dungeon World "fell down … because D&D classes
  are generally too broad to make effective playbooks". **Tension with P5's specialist shape**, which allows a
  class keyed to a *broad* tag (e.g. general spellcasting). → see Tensions T-13. [R: research_notes/DM craft TTRPG design AI tools/indie_niche_ttrpg_design_theory.md §Dungeon World] [C:P5]
- **Balance philosophy splits roughly 50/50.** 13th Age's designers describe themselves as "each right about 50%
  of the time": Heinsoo favors "powerful, fun abilities", Tweet favors "balance". Heinsoo also rejected forced
  repurchases and kept backward compatibility. **Tension with VI's mandatory retirement.** → see Tensions T-16.
  [R: research_notes/DM craft TTRPG design AI tools/major_system_design_lessons.md §13th Age Design Mechanics]
- **Self-play balancing (RuleSmith):** two LLM agents independently control opposing factions from a
  natural-language rulebook. A Gaussian-process Bayesian-optimization loop tunes a **12-dimensional** rule space
  to minimize the win-rate gap between factions, over multiple independent self-play matches, with a structured
  natural-language state description at each decision point. **For 04/05/06 numbers:** an automatable way to tune
  thresholds, costs and synergy values against simulated play, "without waiting for enough live playtests". It is
  only as good as the fidelity of the simulated agents' strategies. [R: research_notes/DM craft TTRPG design AI tools/ai_gm_academic_research.md §Multi-Agent Approaches] [R: reports/DM craft TTRPG design AI tools.md §The tools landscape] [R: reports/DM craft TTRPG design AI tools.md §Updated primitive list]
- **Class diversity varies by class** (13th Age): the Paladin has one build where every talent pushes the same
  way, while the Druid is "extremely diverse". **For 04:** callings don't all need the same internal breadth.
  Some can be deliberately single-track. [R: research_notes/DM craft TTRPG design AI tools/major_system_design_lessons.md §13th Age Design Mechanics]
- **PF2e proficiency tiers** (Trained, Expert, Master, Legendary) plus skill feats for "specific extraordinary
  abilities", with feats at every level across class, ancestry, skill and general categories. **For 04:** a
  named four-rung competence ladder is precedent for tier naming. Note that P2 forbids a separate level number,
  so the *ladder* is reusable but "+1 per level" is not. [R: research_notes/DM craft TTRPG design AI tools/major_system_design_lessons.md §Pathfinder 2e Design Philosophy] [R: research_notes/DM craft TTRPG design AI tools/major_system_design_lessons.md §Head-to-Head] [C:P2]
- **Two distinct skills: authoring valid content and running it consistently.** In RPGBench, Gemini 1.5 Pro
  almost never authored a valid game (VCR 0.04) but still ran others' games at MEC 0.554, and Gemini 2.0 Flash
  ran games best (MEC 0.765) while authoring fewer valid ones (VCR 0.33 vs GPT-4o's 0.49). **For 04/05 (and
  08):** if the runtime ever *generates* ability or class content, generation quality has to be validated
  separately (a BFS-style validity check), not assumed from the runtime's adjudication quality. [R: research_notes/Long horizon LLM narrative benchmarks/rpgbench.md §which models/architectures]

---

## 05 — Abilities & Focus (slots and hard cap, templates, passive/active, recharge, Focus, P10/P12, P6)

- **Fate's three stunt patterns are a *closed grammar of ability shapes*, not a list of abilities.** (1) **Add a
  new action**: let a skill do something it normally can't, copy another skill's action, or add a capability in
  specific situations. (2) **Action bonus**: +2 (or equivalent) under narrowly defined circumstances. (3) **Rules
  exception**: a single exception to a game rule in a narrow context, which may not modify the core
  fate-point/aspect economy. **Mandatory constraints** on every stunt: *specific actions only* (e.g. create
  advantage *or* attack/defend, not both); *situational restriction* (only among nobles, only in supernatural
  contexts); *frequency caps* (once per conflict / scene / session). Circumstances are "pretty narrow compared
  to the base skills they modify". **Fate-point-powered stunts:** a stunt costs a fate point when its effect is
  powerful or has no natural usage limit, *especially* anything affecting conflict stress. **Refresh cost:** start
  with 3 refresh, −1 per stunt, minimum 1, so more stunts means fewer fate points. The DMR calls this "a genuinely
  new, highly transferable idea": a designer defines "a fixed list of *ways abilities are allowed to be shaped*",
  and a generative system can author within it without breaking the power budget, because narrow circumstances
  and frequency caps are "load-bearing, non-optional". **For 05:** this is the most directly usable template
  precedent for P5's "ability templates" and P10's "precisely scoped narrative permission". Mapping: pattern (2)
  ≈ numeric bonus template; pattern (1) ≈ license template (VII); pattern (3) ≈ exception template; fate point ≈
  **Focus** cost for anything unlimited or conflict-affecting. [R: research_notes/DM craft TTRPG design AI tools/cost_systems_and_move_based_abilities.md §How does Fate Core's "stunts" system work] [R: reports/DM craft TTRPG design AI tools.md §Four candidate mechanics] [R: reports/DM craft TTRPG design AI tools.md §Updated primitive list] [C:P9] [C:P10]
- **Warns:** the template grammar has to be comprehensive. If three patterns don't cover what's wanted, players
  keep requesting off-pattern abilities. Whether Fate's three cover player desire, and whether "narrow
  circumstances" is actually enforced in practice, are both *undocumented*. [R: reports/DM craft TTRPG design AI tools.md §Updated primitive list] [R: research_notes/DM craft TTRPG design AI tools/cost_systems_and_move_based_abilities.md §design spectrum]
- **The move-design spectrum.** *Fully pre-specified* (Blades: 7 special abilities per playbook; PbtA: typically
  10–12 moves per playbook). *Template-guided* (Fate). *Open framework*, which **no surveyed published system
  uses** ("no serious published TTRPG trusts fully open player-authored abilities without either a fixed list or
  a fixed template grammar"). The COST comparison table:

  | | Fully pre-specified | Template-guided | Open |
  |---|---|---|---|
  | Clarity | high | medium-high | low |
  | Option space | limited | medium | expansive, power-creep risk |
  | Mechanical power | modest, incremental | moderate (refresh cost) | unbounded |
  | Designer burden | moderate | low | very high |

  **Rules out** open-framework abilities. [R: research_notes/DM craft TTRPG design AI tools/cost_systems_and_move_based_abilities.md §design spectrum] [R: research_notes/DM craft TTRPG design AI tools/cost_systems_and_move_based_abilities.md §Cross-System Summary] [R: reports/DM craft TTRPG design AI tools.md §Four candidate mechanics] [C:V]
- **Blades' special abilities show the incremental trap.** Most are passive +1d or +1 effect in narrow contexts,
  or resource spends (e.g. "special armor", restored at the start of downtime). Many hook into "push yourself"
  so you get its benefit (+1d, +1 effect, act despite harm) without paying **2 stress**. They often "feel less
  impactful than increasing base Action ratings". Standouts like "Functioning Vice" are notably potent. With
  fewer abilities than PbtA (7 vs 10–12) and action-specific rather than stat-based triggers, there is "less
  narrative ambiguity about when abilities apply". **For 05:** fully specified triggers reduce "does this apply?"
  disputes, and mostly-incremental abilities feel weak. Mix in some transformative abilities. The inference: "the
  system works best with a mix of narrow and broad abilities". [R: research_notes/DM craft TTRPG design AI tools/cost_systems_and_move_based_abilities.md §How does Blades in the Dark structure its special abilities] [R: reports/DM craft TTRPG design AI tools.md §Four candidate mechanics]
- **PbtA moves** are "quanta of rules". The player describes the action, and if it matches a move's trigger, the
  move fires ("fiction first"). Named example triggers: Investigate a Mystery, Act Under Fire, Call in a Debt.
  Designers could "write a game for any conceivable narrative conflict" this way. **For 05/P10:** a move is a
  fixed trigger plus a fixed resolution, and it is P10-safe exactly when its trigger has no real judgment call.
  [R: research_notes/DM craft TTRPG design AI tools/cost_systems_and_move_based_abilities.md §design spectrum] [R: research_notes/DM craft TTRPG design AI tools/indie_niche_ttrpg_design_theory.md §Powered by the Apocalypse] [C:P10]
- **The DMR's verdict on moves is dated relative to P10.** The DMR says move/verb design is "the right tool
  specifically for flavor/narrative abilities" and "not a substitute for a full build-diversity engine". The sixth
  constitutional pass revised P10: moves *may* carry core power if trigger-to-outcome is deterministic. → see
  Tensions T-10. [R: reports/DM craft TTRPG design AI tools.md §Updated primitive list] [C:P10]
- **Passive versus active power budget** (→ see 04, 13th Age Ranger): passive abilities must be modest, and power
  should sit in active or conditional triggers. **For 05:** passive templates get a lower power ceiling than
  active ones by rule. [R: reports/DM craft TTRPG design AI tools.md §Updated primitive list]
- **Resource-gated frequency handles the "frequency problem"** (Fate points for unlimited-use stunts). 4e's power
  cadence is **at-will / encounter / daily**, with **Action Points** earned at milestones (completing encounters
  without an extended rest) that buy extra actions. Blades' special armor is renewable at downtime. **For 05's
  recharge vocabulary** (P5 requires each active ability to specify its own tracked recharge): precedent tokens are
  at-will; per-scene / per-conflict / per-encounter; per-rest / per-day; per-downtime; single-use; resource-paid
  (Focus). [R: research_notes/DM craft TTRPG design AI tools/cost_systems_and_move_based_abilities.md §How does Fate Core's "stunts" system work] [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §How do different systems structure what a character can do] [C:P5]
- **Lancer's Overcharge:** extra actions *now* for **heat** that makes you more vulnerable *later* (heat-based
  damage). **For 05/06:** an escalating "strain" cost (each extra use costs more, or builds a consequence track)
  is a precedent for spending Focus on action-economy boosts without breaking P9's fixed pool. [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §How do different systems structure what a character can do] [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §design techniques]
- **Cost brackets and limitations.** HERO's discrete brackets (3/5/6/15 per die by power type) stop linear
  arbitrage between similar effects. Its limitation modifiers lower cost *while improving thematic accuracy*.
  **For 05 costs (P12 vocabulary):** Focus costs should come in a few discrete bands keyed to effect category,
  not a continuous scale. Limitations (narrower targets or conditions) are a legitimate way to lower a Focus
  cost. [R: research_notes/DM craft TTRPG design AI tools/cost_systems_and_move_based_abilities.md §HERO] [C:P12]
- **Bonus-action riders show how "free extra actions" leak.** In 5e, if you cast a spell as a bonus action you
  can only cast a cantrip with your action that turn. That is a patch on exactly this leak. **Warns 05:** any
  ability granting an extra action or rider needs an explicit exclusivity rule. [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §How do different systems structure what a character can do]
- **Literal ability text and the embellishment risk.** "Forgotten Abilities" and "Skill Fluctuations" are named
  consistency-error subtypes. The BRIEF records the probe inventing a cold *vulnerability* from "no protection
  against cold". The high-sensitivity attribute list (perception, memory, mobility, control, access, awareness,
  freedom) marks where an embellished ability is most dangerous. **For 05:** every ability's data entry should
  state its effect literally *and* state what it does **not** do when misreading is likely ("grants no immunity;
  imposes no vulnerability"). → see 01.B. [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §What exactly is the "Lost in Stories" taxonomy] [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §What exactly is "Narrative Commitment Preservation" (NCP)] [BRIEF §7]
- **Feats can modularize or add power.** "Feats can help a designer streamline the combat system by modularizing
  extraneous actions" (clean organization) versus feats as new power vectors (bloat). **For 05:** an ability that
  simply *licenses* a basic maneuver the rules already describe (e.g. "you can disarm") is modularization and
  cheap. An ability that adds a new numeric vector is a power vector and needs audit. [R: research_notes/DM craft TTRPG design AI tools/indie_niche_ttrpg_design_theory.md §Feat Bloat]
- **Unified Focus pool:** these sources contain no data on shared-pool versus per-class resources. The
  constitution's precedent is DOS2's single AP economy. → see Gaps G-8. [C:P9]

---

## 06 — Conflict (action economy, turn order/cadence, positioning, attacks, damage, defense, conditions, reactions, morale, escape)

- **PF2e's fixed pool with variable costs is the front-runner for P9.** Every character gets **3 actions plus 1
  reaction** per round, whatever the build. Most actions cost 1 (Strike, Step, Seek, Interact, Raise a Shield).
  Many spells and activities cost 2. A few cost 3. **Movement draws on the same pool as attacking**, so positioning,
  buffing and utility are real choices rather than free extras. A 2-action activity still leaves room for a step
  or a second attack, and a 3-action activity takes the whole turn. Repeated Strikes take the MAP (−5/−10, agile
  −4/−8). Build diversity then comes from *what* fills the actions, not *how many* a build gets. That "closes off
  the entire class of action-stacking exploits (summons, Haste-chaining)". [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §How do different systems structure what a character can do] [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §design techniques] [R: reports/DM craft TTRPG design AI tools.md §Four candidate mechanics] [C:P9]
- **5e's action / bonus action / reaction split** is simple, but it spawns a secondary metagame. Some classes get
  a bonus action every round (Rogue Cunning Action, Monk, bonus-action casters), so their turns *feel* fuller than
  a single-action class's even when the single action is stronger. This is the "turn fulfillment" disparity.
  Bonus actions exist only when something grants one, and you cannot downgrade an action into a bonus action. A
  reaction refreshes at the start of your next turn (Shield, Counterspell, opportunity attack). **Warns 06:** if
  some builds get a secondary action type, felt engagement diverges, not just power. [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §How do different systems structure what a character can do] [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §documented exploits] [R: reports/DM craft TTRPG design AI tools.md §Four candidate mechanics]
- **Extra bodies are the failure point of action economy.** Summoned allies and Haste multiply actions. The 5e DMG
  never says how to fold them into encounter math. "The action economy favors the side with more 'bodies' …
  regardless of individual power levels". One side having "more turns worth of stuff" is "virtually impossible to
  overcome through tactics alone". D&D avoids "minion masters" largely for this reason. The notes *infer* that
  PF2e avoids the problem because summoned creatures draw on the summoner's action economy. **Digest-author note:**
  in actual PF2e, minions act only when the controller spends an action to command them. That is outside these
  sources but consistent with the inference. **For 06:** companions, summons, animal allies and hirelings must
  draw from, or be commanded out of, the PC's fixed action pool. They must never be free parallel turns. →
  see Gaps G-5 (companions). [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §documented exploits] [R: reports/DM craft TTRPG design AI tools.md §Four candidate mechanics]
- **4e's economy per round:** a Standard, a Move and a Minor action, plus one Opportunity Action (opportunity
  attack) per turn. Action Points are earned at milestones and buy an extra action. Powers are **at-will / encounter
  / daily**, so economy is controlled at the fight and day level rather than per turn. The structure was tuned to
  grid movement. [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §How do different systems structure what a character can do] [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §design techniques]
- **Lancer:** each turn a mech gets one move plus **either two quick actions or one full action**, plus free
  actions. Quick actions include Skirmish (attack), Boost (extra movement), Quick Tech (invade/hack) and activating
  a system. **Overcharge** buys an extra action at the cost of **heat**. **NPCs cannot Brace** (a defensive reaction,
  so they take full damage unless they have mitigation) and **cannot Overcharge**, which caps them at two quick
  actions. The asymmetry is deliberate, meant "to encourage tactical play around those differences" and "to keep
  encounters solvable". The DMR calls asymmetric NPC budgets "a genuinely new, directly reusable idea" for
  anything the AI runs as an opponent. The DMR's own caveat: players may see it as unfair unless the fiction
  motivates it or it is openly explained. [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §How do different systems structure what a character can do] [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §design techniques] [R: reports/DM craft TTRPG design AI tools.md §Four candidate mechanics] [R: reports/DM craft TTRPG design AI tools.md §Updated primitive list]
- **Categorized actions:** splitting a turn into an "offensive action", a "defensive action" and a "neutral action"
  changes how the game plays and stops any one action type from dominating. This is an alternative to PF2e's
  single fungible pool. [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §design techniques]
- **Three categories of anti-dominance design:** (1) hard caps with tradeoffs (PF2e); (2) resource attrition, as in
  5e, which assumes stronger builds burn out faster; this controls power across a day but *not* who dominates a
  single turn; (3) asymmetric NPC design (Lancer). **Documented problems cluster around summons/allies and
  bonus-action optimization, not the core structure.** [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §Research Notes Summary] [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §design techniques]
- **To raise difficulty, tilt the action economy toward the opposition by adding bodies, not by inflating stats.**
  "If you want to scale up difficulty, tilt the Action Economy away from the players." Use **3–12 opponents**
  rather than solo monsters. The action economy is "multiplicative", so "more combatants significantly increase
  difficulty regardless of individual monster power". **Digest-author warning:** this advice is tuned for a
  4–5-PC party. With one PC, every added enemy body is a large relative jump. 06 and 09 need a solo-specific
  body-count curve (e.g. mooks as swarms or single "mob" entities), because 3–12 individual opponents against a
  single PC with 3 actions is almost certainly lethal. → see Gaps G-5. [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Challenge Diversification] [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Spotlight Balance] [R: reports/DM craft TTRPG design AI tools.md §Spotlight balance and challenge diversification]
- **The environment is the cheapest source of variety.** "Four ogres on a road is a very different challenge
  than four ogres on a rope bridge over lava." Other levers: lava floors, chokepoints and tunnels, wide open spaces
  where spell range matters, threats at range *and* in melee "so that they have more problems to solve and have to
  move around more". **For 06 positioning:** positions and zones must be tracked relative to terrain features,
  because the terrain is the challenge. → see 00.B (spatial contradictions are a named failure). [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Challenge Diversification] [R: reports/DM craft TTRPG design AI tools.md §Spotlight balance and challenge diversification]
- **Objective-based conflict:** replace "defeat the monster" with "complete the ritual, protect the hostages, avert
  the alarm, avoid bloodshed". **For 06:** victory conditions should be a field of the encounter, not assumed to be
  "enemy at 0". [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Challenge Diversification] [R: reports/DM craft TTRPG design AI tools.md §Spotlight balance and challenge diversification]
- **Play monsters intelligently.** "Even low-level enemies like goblins and grimlocks can be surprisingly
  challenging when played intelligently." Consult tactical-behavior references. → see 09 for the adversary side.
  [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Challenge Diversification]
- **Run more battles "in the theater of the mind"** (Sly Flourish), favoring character-focused choices over tactical
  advantage. 13th Age deliberately kept "the combat crunch while shedding grid-dependency". **For 06:** abstract
  positioning (relationship-state, per the BRIEF's chapter map) has two named precedents. The actual zone model
  (e.g. 13th Age's engaged/nearby/far away) is *not described* in these sources. → see Gaps G-13. [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Common Dungeon Master Mistakes] [R: research_notes/DM craft TTRPG design AI tools/major_system_design_lessons.md §13th Age Design Mechanics] [R: research_notes/DM craft TTRPG design AI tools/major_system_design_lessons.md §Head-to-Head]
- **Crit effects:** a PF2e Strike deals double damage on a critical hit, a crit-scaled effect that needs no
  separate rule. [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §How does Pathfinder 2e's four-degree system work]
- **Escalation within a fight:** 13th Age bards' songs escalate on the final verse, and sorcerers charge spells
  before attacking. Both are precedent for in-conflict build-up mechanics that differ by class (P14 cadence
  differentiation). [R: research_notes/DM craft TTRPG design AI tools/major_system_design_lessons.md §13th Age Design Mechanics] [C:P14]
- **Adjusting mid-battle (Sly Flourish): add or remove monsters, change hit points within the hit-dice range,
  raise or lower damage.** "When your players feel like they're walking through too easily, give them a dose of
  some pain … when they look haggard … give them a break." **This conflicts with the "no fudging" anti-pattern
  and with goal 2's "keeps state true".** → see Tensions T-5 for the proposed resolution: adjust only through
  diegetic, logged world events such as reinforcement clocks, retreats and morale, never through hidden stat edits.
  [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Challenge Diversification] [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Common Dungeon Master Mistakes]
- **Positions must be state.** NCP's *Alien* case: a character's location changed with no narrated movement.
  Geographic contradictions have the longest plant-to-contradiction gap (31% of story length). **For 06:**
  combatant positions (zones/relations) are `[D]` state, updated by movement actions only. [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Failure modes] [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §What exactly is the "Lost in Stories" taxonomy]
- **Morale, escape and surrender:** these sources say almost nothing, apart from "avoid bloodshed" as an objective
  and "GM as fan, not adversary". → see Gaps G-14. [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Challenge Diversification] [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Common Dungeon Master Mistakes]

---

## 07 — Harm, Recovery & Death (injury, Vitality loss consequences, rest/recovery, telegraphed death, defeat outcomes)

- **Easy long rests trivialize high-level play.** "The single biggest issue with high-level play is the ease with
  which parties can take long rests." The prescribed fix is **narrative time pressure** that limits rest (e.g. "the
  Dragon Queen's armies will be at the city gates in **three days**"). **For 07:** recovery has to be tied to
  elapsed time, and 11's clocks advance while time passes, so resting costs something in the world. A free rest
  button is ruled out. [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Challenge Diversification] [R: reports/DM craft TTRPG design AI tools.md §Spotlight balance and challenge diversification]
- **Defensive gear can make characters "indestructible" sooner than expected** ("manage magic items carefully").
  **For 07:** damage reduction and defense stacking need hard caps. HERO's "defense cheaper than offense" is a
  *creation-cost* rule and should not be read as permission to stack defense in play. [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Challenge Diversification] [R: research_notes/DM craft TTRPG design AI tools/cost_systems_and_move_based_abilities.md §HERO]
- **Take agency away only with narrative justification.** "Taking Away Agency" (imprisonment, mandatory battles,
  stripping abilities) is a named GM mistake, allowed only when the narrative justifies it. **For 07 defeat
  outcomes** (BRIEF §4: capture, injury, loss, changed situation): capture and loss are exactly the agency-removing
  moves the craft literature warns about. Each defeat outcome must hand back an actionable next step at once (P16):
  an escape route, a bargaining chip, a visitor, a clock. [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Common Dungeon Master Mistakes] [C:P16]
- **Losing gear hurts more than the numbers suggest.** Players "dislike losing things they spent points on", and
  gear loss as a balancing lever fails emotionally even when it works on paper. **For 07:** "loss" as a defeat
  outcome should favor *recoverable* loss (confiscated, held for ransom, stolen by a named NPC) over permanent
  deletion, and should never be the default. [R: research_notes/DM craft TTRPG design AI tools/indie_niche_ttrpg_design_theory.md §Indie Communities and Common Character Customization Mistakes]
- **Telegraph risk before the roll.** Blades sets Position (controlled / risky / desperate) *before* rolling, which
  tells the player how bad things can get. **For 07's telegraphed-lethality rule:** announcing a "desperate"-style
  position before any roll that could lead to death is a precedent-backed way to satisfy "explicit warnings before
  lethal risk" (BRIEF §4). A "lethal" flag can be required before a roll's failure branch may include
  dying-state entry. [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §How do OTHER systems implement graduated] [BRIEF §4]
- **Act despite harm.** Blades' push lets a character act despite harm by spending 2 stress. **For 07:** injury
  penalties can be overridden for a resource cost (Focus), which keeps the character's options open while hurt. [R: research_notes/DM craft TTRPG design AI tools/cost_systems_and_move_based_abilities.md §How does Blades in the Dark structure its special abilities]
- **Life, death and presence must be state flags.** NCP's *Zombieland* case: alive/dead or present/absent
  status was silently violated. HP-type numbers are the most fragile updated facts. **For 07:** Vitality, the dying
  state, injuries and conditions are all `[D]` fields. The dying state must be an explicit flag with an explicit
  countdown, never inferred from narration. [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Failure modes] [R: reports/Long horizon LLM narrative benchmarks.md §Fact conflicts, not plot]
- **Pace the pain.** "When they look haggard and pale from the constant stress of hanging on the edge of death,
  give them a break." **For 07/12:** after a run of high-harm scenes, the DM should schedule a recovery opening.
  With no human face to read, the trigger has to come from state (e.g. Vitality below X for N consecutive
  scenes). → see Gaps G-15. [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Challenge Diversification]
- **Death, dying, injuries and conditions: these sources describe no mechanics** (no death saves, no wound tables,
  no condition lists). → see Gaps G-1. [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Summary of Research Scope]

---

## 08 — Items, Loot & Crafting (loot generation, item properties, crafting, wealth, economy)

- **Gear must not outclass innate abilities.** → see 02. This is the Mythcreants "gear balance" antipattern: gear
  more powerful than other character options creates a no-win choice between overpowered gear and underpowered
  characters. [R: research_notes/DM craft TTRPG design AI tools/indie_niche_ttrpg_design_theory.md §Indie Communities and Common Character Customization Mistakes] [R: reports/DM craft TTRPG design AI tools.md §Indie design theory]
- **Handing out too many magic items is "a classic new dungeon master mistake".** Players end up overpowered and
  steamroll the content. [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Common Dungeon Master Mistakes]
- **Item density is a balance assumption, not an afterthought.** PF2e "expects characters to have multiple items
  at every level", while 5e "partially managed balance by cutting back on magic items". **For 08:** the math has
  to state its item-density assumption (how many items of what power a typical character carries at each tier),
  because encounter and adversary tuning depend on it. [R: research_notes/DM craft TTRPG design AI tools/major_system_design_lessons.md §Pathfinder 2e Design Philosophy] [R: research_notes/DM craft TTRPG design AI tools/major_system_design_lessons.md §Head-to-Head]
- **Procedural seeding eases context load.** Procedural generation of NPCs, encounters, loot and world details
  "complements LLM narration", lowering context-window load and improving consistency. Hades and Spelunky are named
  as dungeon-layout precedents. (The "40% diversity / 28% overhead" figures are unsourced, grade [D].) **For 08:**
  loot should be *rolled on data tables by a tool* (the P5 pool-gate/fill-quality shape), not invented in prose.
  [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Supporting Infrastructure]
- **Wealth, counts and inventories are the most fragile state.** The canonical example is the gold hallucination.
  Quantitative mismatches are a named error subtype, and numeric resources revised more than once are the most
  fragile category of all. **For 08:** currency and inventory are `[D]` quantities, every transaction is a tool
  call, and narration must never state a post-transaction total the tool did not return. [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Design Tensions & Failure Modes] [R: reports/Long horizon LLM narrative benchmarks.md §What this means for Feature 002's spec] [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §What exactly is the "Lost in Stories" taxonomy]
- **Object-state failures.** NCP's *Indiana Jones* case: a locked door was later treated as open with no unlocking
  event. **For 08:** items with states (locked/unlocked, lit/unlit, charged/spent, broken/intact) carry explicit
  state fields. [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Failure modes]
- **A renewable item resource:** Blades' "special armor" is restored at the start of downtime. It is a precedent
  for item abilities with a downtime recharge. [R: research_notes/DM craft TTRPG design AI tools/cost_systems_and_move_based_abilities.md §How does Blades in the Dark structure its special abilities]
- **Economy as dynamic state:** NarrativeEngine keeps "factions, power systems, economy, and events" in its dynamic
  RAG layer. **Digest-author caution:** under the MERIT finding (00.A), prices and stocks that change should live
  in an update-on-write store, not RAG. [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Open-Source AI Dungeon Master Projects]
- **Crafting, economy design, rarity tiers: no mechanics in these sources.** The fifth-pass report (not in scope
  here) covers pool-gate/fill-quality. → see Gaps G-16. [C:P5]

---

## 09 — Adversaries (archetypes, threat bands without levels, stat templates, behaviors)

- **Asymmetric NPC budgets** (Lancer: NPCs cannot Brace or Overcharge). → see 06. For 09: adversary stat templates
  can deliberately use a smaller or simpler action set than PCs. This keeps the AI's opponent-side computation
  tractable and encounters solvable, as long as the fiction supports the difference. [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §How do different systems structure what a character can do] [R: reports/DM craft TTRPG design AI tools.md §Updated primitive list]
- **Sly Flourish's "lazy" levers for stronger monsters:** (1) treat the PCs as a higher level when picking the
  challenge; (2) raise HP by maximizing hit dice, or **double HP and call it an "elite"**; (3) push damage toward
  the maximum, justified in the fiction (a "necrotic aura", enchanted weapons); (4) **grant extra attacks** so the
  monster threatens more targets. **For 09:** an "elite" template (×2 Vitality, a damage bump, +1 attack) is a
  precedent-backed scaling tool that works without levels. [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Challenge Diversification]
- **Choose monsters from the story first.** "Choose monsters based on the story." Encounters should "develop from
  the story, the situation, and the actions of the characters", and there's no need to label them in advance as
  combat, roleplay or exploration. **For 09:** adversary selection keys off 11's world state (faction, region,
  ecology), and stat budget comes second. [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Challenge Diversification]
- **Intelligent tactics beat stat inflation.** → see 06. For 09: every adversary archetype should come with a short
  **behavior script**: goals, preferred range, when it retreats, what it protects, how it exploits terrain. That is
  what makes "played intelligently" something the AI can reproduce. [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Challenge Diversification] [R: reports/DM craft TTRPG design AI tools.md §Spotlight balance and challenge diversification]
- **Encounter mixing:** roll twice on an encounter table and combine the results: two groups fighting each other,
  one that just wiped out another, or the two as allies. It adds real complications without new content. **For
  09/11:** a mixing rule for encounter tables is cheap variety. [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Challenge Diversification] [R: reports/DM craft TTRPG design AI tools.md §Spotlight balance and challenge diversification]
- **Threat bands without levels.** M&M's **Power Level** works as a campaign "danger bracket" that caps attack,
  damage, defense and toughness. It's the nearest precedent for bounding adversary power without character levels.
  The sources offer nothing else on this point. → see Gaps G-17. [R: research_notes/DM craft TTRPG design AI tools/cost_systems_and_move_based_abilities.md §How does Mutants & Masterminds' point-buy system work]
- **Adversary scaling math has to respect solo play.** → see 06: "3–12 opponents" and "action economy is
  multiplicative" are party-scale guidance. [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Challenge Diversification]
- **The GM is a fan, not an adversary.** "Being the Adversary Instead of a Fan" is a top pitfall. So are traps and
  monsters that "always counter the player characters". **For 09:** smart adversaries must not become
  omniscient counters. They act on what they could know, and NPC knowledge is state (→ 00.B). [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Common Dungeon Master Mistakes]
- **NPC psychology as state (NarrativeEngine):** NPCs are simulated with psychology, goals and relationships.
  Their values shape how they speak, react and decide, and "NPC characteristics drift naturally as they experience
  events". **DREAM**'s Event-aware Memory Graph (based on the Activating-Event → Belief → Consequence cognitive
  model) builds **dual-granularity character profiles**: stable traits plus event-driven evolution. **For 09 (and
  10/11):** an NPC record = stable traits + a log of events that changed them. [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Open-Source AI Dungeon Master Projects] [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §Other 2025–2026 benchmarks]
- **A personality spec that can be checked.** RPGBench's main-NPC record carries a **Big-Five block**, each trait
  rated 1–5 with a free-text description, plus an `additional_facts` list. Personality consistency is scored by
  running the transcript through the **Ten-Item Personality Inventory (TIPI)** and taking the normalized Euclidean
  distance to the declared traits. **For 09:** a compact numeric personality vector per major NPC gives both
  a behavioral anchor and a way to audit drift. [R: research_notes/Long horizon LLM narrative benchmarks/rpgbench.md §state-tracking/memory specifically] [R: research_notes/Long horizon LLM narrative benchmarks/rpgbench.md §metrics]
- **Few-shot voice:** a character card (name, description, personality, *speech examples*, goals, relationships,
  secrets) "teach[es] voice more reliably than lengthy prose descriptions". **For 09:** major NPC entries include 2–3
  sample lines. [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Key Architectural Patterns] [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Synthesis]
- **PLAYER*'s sensors:** emotion, motivation and opportunity detectors drive what an agent asks or does next. A
  pruner discards low-information actions. Anytime sampling-based planning (like RRT*) builds and prunes a search
  tree in real time. Adaptive, information-driven planning generalized better than static scenario-specific guides.
  **For 09:** adversary AI can read motivation and opportunity rather than follow a fixed script, and an
  "opportunity" trigger list per archetype is the rules-level version of that. [R: research_notes/DM craft TTRPG design AI tools/ai_gm_academic_research.md §Multi-Agent Approaches] [R: reports/DM craft TTRPG design AI tools.md §The tools landscape]
- **Villains must be allowed to be villains.** "Content Guardrail Backlash": safety constraints made a villain
  behave non-antagonistically and broke their narrative role. Character.AI's decline is tied to heavy guardrails and
  memory resets. **For 09:** adversary behavior guidance should say plainly that antagonists act with real hostility
  within session-zero limits (→ 02). Moderation is a separate subsystem (P13). [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Design Tensions & Failure Modes] [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Community-Oriented Roleplay Platforms] [C:P13]

---

## 10 — Exploration, Social & Downtime (travel, hazards, investigation, social influence, downtime)

- **Skip empty time.** The Alexandrian's main pacing technique is to recognize and cut the dead time between
  meaningful decisions. **For 10:** travel and downtime get abstracted procedures (resolve the whole journey or
  downtime block) that resume turn-by-turn play only when a decision or event comes up. [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Core Principles of Good Dungeon Mastering]
- **AI strengths in exploration, per player reports:** AI rated **4.13/5** vs humans' **3.35** on immersive
  environments, and 68% of 412 surveyed users reported higher initial immersion "particularly during exploration,
  travel, and environmental interaction". Grade [D]. [R: research_notes/DM craft TTRPG design AI tools/ai_gm_academic_research.md §Player Experience and Comparative]
- **Investigation must be gated by state.** → see 01.D. The knowledge-tree detective game (−64.78% critical
  hallucinations, zero premature disclosure) and NCP's "Triggering Unknown Facts" failure. **For 10:** each mystery
  should be stored as a clue graph with per-node reveal conditions. P16's no-dead-ends rule and P17's graduated
  reveal then work on that graph. The sources do not contain the classic clue-redundancy rule (e.g. the Alexandrian
  "Three Clue Rule"). → see Gaps G-6. [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §Other 2025–2026 benchmarks] [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Failure modes] [C:P16] [C:P17]
- **PLAYER* (murder-mystery agents)** replaced static question libraries with adaptive investigation driven by
  what information was needed. **For 10:** NPC suspects and witnesses answer from their knowledge state, and the
  DM chooses which questions to surface based on what the player still doesn't know. [R: research_notes/DM craft TTRPG design AI tools/ai_gm_academic_research.md §Multi-Agent Approaches]
- **Social influence:** the sources offer craft stances ("yes, and", "build situations") and NPC-state architecture
  (values drive speech and decisions, drift from events, Big-Five anchors) but **no social-conflict mechanic**. →
  see Gaps G-7. [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Core Principles of Good Dungeon Mastering] [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Open-Source AI Dungeon Master Projects]
- **Knowledge contradictions** (a character acting as if they don't know what they were told, or knowing what
  they shouldn't) and **memory contradictions** are named error subtypes. **For 10:** each NPC's knowledge state
  is written to the store when information passes to them in social play (who told whom, when). [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §What exactly is the "Lost in Stories" taxonomy] [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Methodology for constructing test scenarios]
- **Situation-specific procedures deepen immersion.** Errant has dedicated procedures for managing estates and for
  legal trials. **For 10 downtime:** subsystems for specific downtime activities (running a holding, a trial,
  research, training) are precedented crunch, not bloat. [R: research_notes/DM craft TTRPG design AI tools/indie_niche_ttrpg_design_theory.md §Crunch vs. Playability]
- **Downtime refreshes certain resources.** Blades' special armor is restored at the start of downtime. [R: research_notes/DM craft TTRPG design AI tools/cost_systems_and_move_based_abilities.md §How does Blades in the Dark structure its special abilities]
- **Geography is long-gap state.** Geographical contradictions have the largest plant-to-contradiction gap (31.0%
  of story length). **For 10 travel:** routes, distances, travel times and landmarks are stored data, not
  remembered prose. [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §What exactly is the "Lost in Stories" taxonomy]
- **Time pressure is also a challenge type.** Narrative deadlines ("armies at the gates in three days") turn travel
  and downtime into resource decisions. [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Challenge Diversification]
- **Use varied challenges to pull the player into different kinds of play.** Skill challenges and objective-based
  scenes let different capabilities matter. → see 12.B. [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Spotlight Balance]

---

## 11 — Living World (factions, clocks, hooks, rumors, consequence propagation, sandbox generation, retirement & legacy)

- **The DM builds situations, not stories.** "DMs don't create the story—the group does." "Build situations and let
  the characters navigate them." "Rather than writing a story, you're writing scenarios." "Forcing Your Story"
  (railroading) is "one of the biggest pitfalls even expert GMs fall into". **For 11:** the world engine produces
  situations: faction goals in motion, pressures, opportunities. It does not produce plots with required outcomes.
  This matches the BRIEF's sandbox lock. [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Core Principles of Good Dungeon Mastering] [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Common Dungeon Master Mistakes] [R: reports/DM craft TTRPG design AI tools.md §Spotlight balance and challenge diversification]
- **"My Precious Encounter"** (every encounter lovingly crafted and "utterly indispensable") is an
  over-preparation antipattern. **For 11:** no generated hook is indispensable. Every hook can fail, be ignored, or
  resolve without the PC. [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Common Dungeon Master Mistakes]
- **NCP-style typed commitments are the most rigorous structure in these sources for world obligations.** There
  are three types. An **invariant** must stay true (or false) across a bounded span, e.g. "the Baron remains
  unaware of the smuggling ring until exposed". An **ordering** requires one event before another. An
  **achievement** is a milestone that must happen, e.g. "the cult completes the ritual". Each commitment has an id,
  a type, a description, a `satisfaction_condition` and a `violation_condition`. Conditions must be "fact-based,
  mutually exclusive, and unique" and "directly determinable" from observable actions or NPC responses without
  interpretation. Static background (names, occupations) is excluded; only dynamic plot constraints count. An
  achievement is violated when its violation condition fires **or** its satisfaction becomes logically
  impossible. **For 11:** faction agendas, clocks and hooks can be written as typed commitments. The world engine
  can then check mechanically whether a PC action advanced, blocked or broke one, and propagate the consequence.
  Caution: NCP's commitments are *narrative obligations of the narrator* in a scripted story. In a sandbox, faction
  commitments are *intentions the world pursues*, which the PC can legitimately foil. Foiling is a recorded
  outcome, not a violation. [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §What exactly is "Narrative Commitment Preservation" (NCP)] [R: reports/Long horizon LLM narrative benchmarks.md §NCP-Bench proves synthetic construction]
- **Trajectory nodes give the shape of faction plans.** Each node is atomic, with a `trigger_event` that causally
  connects to the next node's `key_delta`, and that delta must be an *observable world-state change*. The first
  node `s_0` is the "pre-eruption" moment, when the core conflict exists but is not yet visible. Node count scales
  with complexity. **For 11:** a faction's plan = ordered atomic steps, each with a trigger (what must happen for
  it to advance) and an observable effect (what changes in the world when it does). That is a clock whose segments
  have content. [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Methodology for constructing test scenarios]
- **T=0 isolation for secrets.** When seeding a region or a faction's secrets, write present-tense facts only,
  plus explicit ignorance facts ("the town does not yet know the well is poisoned"). Never embed future
  revelations as current truths. **For 11 and 13:** the world state the DM sees at any moment encodes only what is
  true *now*. Future developments live in the faction plan (trajectory), not in present facts. That prevents
  "Triggering Unknown Facts". [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Methodology for constructing test scenarios] [R: reports/Long horizon LLM narrative benchmarks.md §What this means for Feature 002's spec]
- **Abandoned plot elements are a named, dominant-category error** (Timeline & Plot Logic). **For 11:** every hook
  and rumor has a lifecycle state (seeded / active / resolved / expired / retired). The engine must eventually
  resolve or retire it, which is Principle VI applied to world content and prevents dangling threads. [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §What exactly is the "Lost in Stories" taxonomy] [C:VI]
- **Improvise, write it down, bring it back.** "Writing down everything you improvise and reincorporating it later
  is what makes the table believe the whole story was planned." **For 11/12:** every improvised fact (a named NPC,
  a rumor, a price, a grudge) is written to the store the moment it is narrated. The world engine then prefers to
  *reuse* recorded elements when it generates new hooks. [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Core Principles of Good Dungeon Mastering]
- **Deadlines as the living-world pressure.** Narrative time pressure ("three days") is the named fix for rest
  abuse and a challenge type in its own right. **For 11:** faction clocks tick with elapsed in-world time, which
  connects 07's rest to 11's world. [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Challenge Diversification]
- **Mix encounters to generate consequences.** Two table results combined (two groups fighting, one that just
  wiped out another, two allies) produce emergent faction interactions. → see 09. [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Challenge Diversification]
- **Director and narrator roles.** A Director agent "subtly nudges the simulation". Character agents with goals,
  states and memories produce event records. A separate narrator turns scene-relevant events into prose, with
  control over pacing. **For 11:** the living-world engine is the Director layer and outputs structured events. 12's
  narrator describes only those relevant to the current scene. [R: research_notes/DM craft TTRPG design AI tools/ai_gm_academic_research.md §Multi-Agent Approaches]
- **NarrativeEngine precedent:** factions, power systems, economy and events live in a dynamic layer. NPCs have
  goals and relationships and drift. Campaign state is **versioned, with rollback and parallel branches**. **For
  11:** versioning world state is precedented. A player-requested or error-correction rollback (→ 12.D) needs this.
  [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Open-Source AI Dungeon Master Projects]
- **Relationships with the world's great powers.** 13th Age Icon Relationships (3 points spread over the setting's
  major powers) tie characters to the world's big factions. The rules text for them grew **3 → ~60 pages** because
  the original was vague. **For 11:** a PC-to-faction relationship model is precedented, and it must be precisely
  specified from the start. [R: research_notes/DM craft TTRPG design AI tools/cost_systems_and_move_based_abilities.md §13th Age and Savage Worlds] [R: research_notes/DM craft TTRPG design AI tools/major_system_design_lessons.md §13th Age Design Mechanics]
- **Parallel threads that affect each other.** Ink supports parallel, shared-state story flows (switching between
  simultaneous conversations, with one able to affect another) and serializes state to JSON. **For 11:** there is
  precedent for many concurrent situation threads sharing one state store. [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Non-AI Branching Narrative Tools]
- **Campaign pacing** is the third pacing level, above session and scene. There's no operational guidance beyond
  its existence. → see Gaps G-15. [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Core Principles of Good Dungeon Mastering]
- **Campaign collapse (sessions 10–50+)** is the main threat to an indefinite sandbox. → see 00.A. [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Design Tensions & Failure Modes]
- **Retirement and legacy: nothing in these sources.** → see Gaps G-18.

---

## 12 — DM Procedures (turn loop, pacing, reveal in practice, NPC play, improvising from the substrate, session structure)

### 12.A The core loop and pacing

- **The core loop is a conversation:** the GM presents a situation, the players respond, the GM adjudicates the
  outcome. **For 12:** the DM turn loop can be built on this three-beat skeleton, with the BRIEF's steps inserted:
  capability gate, roll, state writes, verification, next-step guarantee. [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Core Principles of Good Dungeon Mastering]
- **Pacing works on three levels: session, scene, campaign.** Operational rules ("switch scenes every X turns") do
  not exist in the literature. → see Gaps G-15. [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Core Principles of Good Dungeon Mastering]
- **Skip empty time.** → see 10. [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Core Principles of Good Dungeon Mastering]
- **Push when it's too easy, ease off when it's too hard:** "a dose of some pain" when things are too easy, "a
  break" when the PCs are haggard. **For 12:** a human reads this from faces. An AI needs state triggers (Vitality
  trajectory, consecutive trivial or near-lethal scenes). [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Challenge Diversification]
- **Narration quality decays with length through repetition.** RPGBench's interestingness score (INT) *declines*
  over 10→25 rounds, which the authors attribute to repetitive narration. **For 12:** an explicit anti-repetition
  procedure: vary scene openings, avoid repeating descriptors, and rotate challenge types (→ 12.B). [R: research_notes/Long horizon LLM narrative benchmarks/rpgbench.md §which models/architectures] [R: reports/Long horizon LLM narrative benchmarks.md §Degradation is fast]
- **Offer choices without building a menu.** RPGBench's per-round structure has the engine present **three
  candidate next actions**, scored for *diversity, relevance and clarity* (ACT metric, each rated 1–5). **For 12
  and P16:** suggested leads are a legitimate next-step device. **Tension with goal 1** (no menu walls): suggestions
  must be framed as examples, never as the option set. → see Tensions T-11. [R: research_notes/Long horizon LLM narrative benchmarks/rpgbench.md §overall evaluation methodology] [R: research_notes/Long horizon LLM narrative benchmarks/rpgbench.md §metrics] [R: research_notes/DM craft TTRPG design AI tools/ai_gm_academic_research.md §Evaluation Methodologies]

### 12.B Spotlight and challenge rotation, reinterpreted for one player

- **Spotlight balance and challenge diversification must be built as explicit subsystems. Neither falls out of good
  mechanics.** This is the DMR's headline finding: "no source anywhere … shows a system that gets these for free
  from good mechanical design alone". A human GM notices that "the table is steamrolling" or "the rogue hasn't had
  a moment in three sessions". An AI needs "a per-player spotlight ledger, a challenge-type rotation rule". Current
  AI-GM research flags "delayed responses and limited emotional engagement" and offers no substitute for reading the
  room. [R: reports/DM craft TTRPG design AI tools.md §Engineering spotlight balance for an AI GM] [R: reports/DM craft TTRPG design AI tools.md §Spotlight balance and challenge diversification] [R: reports/DM craft TTRPG design AI tools.md §What this round changes] [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Translating Human GM Skills to AI]
- **Balance over the campaign arc, not each session.** "Balance doesn't mean sameness every session. It means trust
  over time." The goal is that everyone feels valued "over the course of the campaign rather than in every individual
  session". The DMR's warning: "a naive session-level metric will misfire." [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Spotlight Balance] [R: reports/DM craft TTRPG design AI tools.md §Updated primitive list]
- **Rotation cadence:** switch focus about **every 10–15 minutes** of real time, "when it feels natural". **Digest-author
  note:** this is multiplayer, real-time guidance. It does not translate directly to a solo text game. The
  single-player reinterpretation: rotate which *facet* of the one character, which *pillar* (combat / exploration /
  social / investigation / downtime) and which *challenge type* is foregrounded. Measure the rotation in scenes or
  turns and keep it in a ledger (→ 03's per-tag "last exercised"). No source validates any number for this. [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Spotlight Balance]
- **The named challenge types to rotate:** (1) environmental/tactical terrain; (2) intelligent tactics; (3)
  action-economy tilt; (4) objective-based (ritual, hostages, alarm, avoid bloodshed); (5) resource pressure / time
  pressure; (6) encounter mixing. The DMR's rotation primitive lists "environmental / tactical / objective-based /
  resource-pressure / encounter-mixing" and warns it "requires a content-generation layer diverse enough to actually
  produce all five challenge types, not just combat". **What proportion** of each type to use is an explicit gap. →
  see Gaps G-15. [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Challenge Diversification] [R: reports/DM craft TTRPG design AI tools.md §Updated primitive list]
- **Respond to an optimized build by changing the kind of problem, not by escalating monster stats.** "Fetishizing
  balance" produced "encounters which were less flexible, less dynamic, and less interesting". Performance gaps come
  from two characters sharing a niche, or from "campaign style doesn't match a character's specialization". The fix
  is on the DM's side (varied enemy types, encounter frequency, challenge mix), not nerfing the character. **For
  12:** when the player's build dominates, rotate challenge types. Don't inflate numbers. [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Spotlight Balance] [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Challenge Diversification] [R: reports/DM craft TTRPG design AI tools.md §Spotlight balance and challenge diversification]
- **Model the player's type and goals explicitly.** Laws' seven types and the Player Goal Chart. Some players love
  the spotlight and others prefer to observe. The inference "An AI GM might need to ask players directly about
  their engagement levels rather than inferring from non-verbal cues." **For 12:** explicit, periodic, out-of-fiction
  preference check-ins (tone, pace, what the player wants more of) are the evidence-backed stand-in for reading the
  room. [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Spotlight Balance] [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Translating Human GM Skills to AI]
- **Robin's Laws' "Know your players, Analyze your system, Build your campaign, Design adventures, Prepare to be
  spontaneous"** is a five-step GM preparation framework. Its first rule: "If your group is having fun, then you are a
  good GM." [R: research_notes/DM craft TTRPG design AI tools/indie_niche_ttrpg_design_theory.md §Robin's Laws] [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Core Principles of Good Dungeon Mastering]
- **Improvise with generators:** use name generators, trait lists and treasure generators when play goes off-plan.
  Shift some tasks to the players ("one of the core principles of D&D improv"). **For 12:** improvising from the
  substrate means drawing from `data/*.yaml` oracle tables, which also records what was improvised (→ 11). [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Core Principles of Good Dungeon Mastering]

### 12.C GM stance

- **Be a facilitator and a fan of the character, not an adversary.** Understand player goals and character
  backgrounds. [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Common Dungeon Master Mistakes]
- **Don't railroad.** But being open about what the GM isn't ready for ("you don't feel ready to have the story go
  that way yet") is *not* railroading. **For 12 (with 14):** an out-of-fiction note ("that region isn't detailed yet;
  here's what's knowable") is acceptable craft. It fits the hidden-mechanics tone only as an out-of-fiction aside. [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Common Dungeon Master Mistakes]
- **Don't fudge** (dice, DCs, always-countering monsters). → see 01.B, 06. [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Common Dungeon Master Mistakes]
- **Trust comes from player choices mattering.** "Trust forms when players believe their choices matter, their
  emotions are honored, and the world responds with integrity—not just plausibility" (Boing Boing, grade [D]). The
  inference, stated as an inference: "a mediocre story that respects player agency may be preferable to a
  high-quality story that feels railroaded". [R: research_notes/DM craft TTRPG design AI tools/ai_gm_academic_research.md §Player Experience and Comparative]
- **The GNS forcing question.** Is the game mainly optimizing challenge (gamism), curated story (narrativism) or
  world consistency (simulationism)? Edwards claims trying to satisfy all three equally is "a common mistake". →
  see Tensions T-7. [R: research_notes/DM craft TTRPG design AI tools/indie_niche_ttrpg_design_theory.md §GNS Theory] [R: reports/DM craft TTRPG design AI tools.md §Indie design theory]
- **PbtA presentation:** GMs are given "guidelines and principles rather than a full system of rules", and the rules
  explain themselves and set tone. **For 12:** it helps to write DM procedures as principles *plus* concrete
  procedures, since the BRIEF requires procedures and principles alone would fail goal 2. [R: research_notes/DM craft TTRPG design AI tools/indie_niche_ttrpg_design_theory.md §Powered by the Apocalypse]

### 12.D Consistency procedures (as rules of play)

- **The biggest measured consistency gain anywhere in these sources is a verification step:** check generated output
  against the knowledge store *before the player sees it*. The detective-game tri-agent (retrieve, generate,
  **verify**) cut critical hallucinations by **64.78%** and stopped all premature disclosure, at some cost to
  conversational naturalness. NCP-Bench's own auditor is the same kind of step: a narrow second pass that checks
  narration against the fact and commitment ledger, with a **double-check confirmation** before a conflict is
  confirmed. The LHR recommends extending the project's existing narration-vs-state judge. **For 12:** the DM turn
  loop should include a verification step as a *rule of play*: before finalizing narration, list every state claim
  the narration makes and confirm each against the tool state. This also bears on constitution III's revisit
  trigger. → see Tensions T-1. [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §Mitigation strategies: quantified evidence] [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Metrics] [R: reports/Long horizon LLM narrative benchmarks.md §Mitigation architecture] [C:III] [C:P13]
- **The model's own self-report can't be trusted.** Constitution P13's probe: the model reported no inconsistencies,
  yet it had introduced an unearned pronoun. "Linguistic fluency" is not "logical consistency". **For 12:** a DM
  self-check has to be a *structured claim-by-claim comparison against state*, not "did I make any mistakes?". [C:P13] [R: research_notes/DM craft TTRPG design AI tools/ai_gm_academic_research.md §Consistency and Long-Horizon]
- **Read state before narrating it.** Models act correctly on a correctly retrieved updated fact only about 55% of
  the time. **For 12:** before narrating any quantity, status or position, the DM reads it via `get_state` *in that
  turn*, and the narration quotes the tool's value, not memory. [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §Other 2025–2026 benchmarks]
- **Keep the player's most recent input verbatim.** HiAgent (hierarchical/summarizing memory) raised average
  survival from 22.16 to 30.05 turns and cut commitment conflicts from 26% to **4%**, but player-input conflicts
  **rose from 13% to 38%** (compression lost the fine-grained "what did the player just say"). Trajectory progress and
  satisfied commitments slightly *fell* (16.64%→15.68%, 10.03%→9.14%). The paper says the tradeoff is unresolved.
  Practitioner guidance: keep the **most recent ~10%** of context verbatim (current tool call, latest message, the
  reasoning just before it). Compress only older material that has already been acted on (scene-setting, reasoning
  chains, redundant observations). **Never summarize a summary**; hand off to a fresh context instead. Verbatim
  compaction keeps 50–70% of the text and guarantees accuracy. BOOKMARKS keeps the full storyline and retrieves on
  demand (39.44%→45.42% on mystery reasoning versus incremental summarization). Observation masking beat LLM
  summarization in 4 of 5 agentic settings. **For 12's session structure:** session-boundary recaps are generated
  *from state* (→ 13), not from a chain of summaries. The player's latest turn is always processed in full. [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Mitigation strategies] [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §Mitigation strategies: quantified evidence] [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §Other 2025–2026 benchmarks] [R: reports/Long horizon LLM narrative benchmarks.md §Mitigation architecture]
- **Latest established state wins, and some attributes need justification.** NCP's auditor gives precedence to the
  most recently established state ("visible continuity priority") and demands explicit justification before upgrading
  perception, memory, mobility, control, access, awareness or freedom. **Digest-author note:** in this project the
  *tool state* should outrank any narration, old or new. See Tensions T-14. [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §What exactly is "Narrative Commitment Preservation" (NCP)]
- **Rising token-level entropy may warn of an error.** Error-containing spans showed higher token-level entropy
  (e.g. **+19.24%** for Qwen3-4B). This could let a runtime target consistency re-checks. It's an infrastructure
  concern and only matters if the runtime exposes logprobs. [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §What exactly is the "Lost in Stories" taxonomy]
- **Expect errors early, and plan how to correct them.** With the best model under adversarial play, only ~42% of
  episodes reached turn 20 with no audited conflict. Across all models and conditions only ~3.5% reached 100 turns
  clean. Average turns before the first conflict ranged from **2.88** (Kimi-K2.5) to **32.92** (GPT-5.2). A
  cooperative player roughly doubled survival (GPT-4o-mini 22.16→46.08) and cut commitment conflicts about 3×
  (26%→9%), while fact conflicts barely moved (60%→56%). The LHR concludes that fact-tracking failure is driven
  mostly by accumulated turn count. **For 12:** the ruleset has to assume errors *will* happen within any long session
  and define an **error-correction procedure**: who notices (the DM's verification or the player), how it is fixed
  (state wins; narration is corrected with an in-fiction reconciliation or a short out-of-fiction note), and how it
  is logged. The sources give no such procedure. → see Gaps G-3. [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Failure modes] [R: reports/Long horizon LLM narrative benchmarks.md §Degradation is fast]
- **Rules first, then recent events, then lore.** → see 00.A. Keep combat rules separate from craft guidance. [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Key Architectural Patterns]
- **Moderation is a separate subsystem from consistency.** Moderation tolerates reversible false positives.
  Consistency does not. [C:P13] [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Design Tensions & Failure Modes]

### 12.E Evaluating the DM (for playtests and audits)

- **Off-the-shelf rubrics:** *NARRA-Gym* has 11 dimensions: 7 story (relevance, coherence, empathy, surprise,
  engagement, complexity, character development) and 4 user-experience (satisfaction, prose quality, helpfulness,
  reusability). Scoring is a **three-model LLM-judge sweep** to reduce single-judge bias, plus human within-group
  ranking aggregated with a Plackett-Luce model for qualities rubrics miss: pacing at a human tempo, prose that
  invites continuation, emotional turns that feel "earned rather than merely correct". The *23 Story Quality
  Dimensions* came from a Delphi study with 10 experts. 78% of dimensions scored ≥3.5/5 importance and 26% scored
  >4.5 ("critically important"). Kano classification: 57% one-dimensional, 26% must-have, 13% attractive, 4%
  indifferent. Two new dimensions emerged: **Voice** and **Genre Alignment**. *RPGBench* scores MEC, FAC, PER, INT and
  ACT. **Warns:** none of these measures rules-adjudication fairness, and the subjective ones correlate weakly with
  humans (r ≈ 0.13–0.14). No research shows how dimensions trade off (e.g. whether surprise reduces coherence).
  **For `rules/_process/playtests/`:** report per-category conflict counts, turn of first conflict, and survival
  versus success, at checkpoints (turn 20/50/80). [R: research_notes/DM craft TTRPG design AI tools/ai_gm_academic_research.md §Evaluation Methodologies] [R: reports/DM craft TTRPG design AI tools.md §The tools landscape] [R: reports/Long horizon LLM narrative benchmarks.md §What this means for Feature 002's spec]
- **Survival and success are separate metrics.** NCP-Bench's outcomes are Conflict, Survival (reached the cap with no
  flagged conflict) and Success (Survival plus every achievement commitment satisfied). HiAgent survived longer
  without advancing the story further. The Horizon Gap survey adds that "outcome-only signals grow uninformative" as
  horizons lengthen, which pushes evaluation toward per-step checks. [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Metrics] [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Mitigation strategies] [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §Other 2025–2026 benchmarks]
- **Experts and novices notice different things.** Experts are more sensitive to consistency errors and narrative
  flow. Novices prioritize entertainment and immersion. Grade [D]. [R: research_notes/DM craft TTRPG design AI tools/ai_gm_academic_research.md §Player Experience and Comparative]

---

## 13 — Starter Setting (a starter region and opening situation that exercises every subsystem)

- **Build the opening as a structured skeleton before writing prose.** NCP's 3-stage pipeline: a synopsis/outline
  → **trajectory** (atomic nodes with trigger_event and observable key_delta, POV-compliant) → **commitments**
  conditioned on the trajectory (invariant/ordering/achievement, machine-checkable, no static color) → **initial
  facts** conditioned on both (T=0 isolation, positive ignorance, atomized into cognitive/positional/relationship
  facts). Every stage uses the same fixed "senior Narrative Logic Architect" persona, strict JSON output and
  explicit forbidden constructs (compound nodes, mental-only deltas). The recap prose is generated *from* the
  skeleton "guaranteeing the two never disagree at seed time". **For 13:** the starter region should ship as data
  (facts, faction trajectories, commitments/clocks, secrets with ignorance facts), with the opening narration
  derived from it. Scale reference: NCP environments average **16.6 facts, 12.2 commitments, 15.1 trajectory nodes**. [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Methodology for constructing test scenarios] [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §What exactly is "Narrative Commitment Preservation" (NCP)] [R: reports/Long horizon LLM narrative benchmarks.md §What this means for Feature 002's spec]
- **Check the scenario is winnable and losable before shipping.** RPGBench runs every generated game through a **BFS
  validity checker** that confirms a success state and a failure state are both reachable and every declared event is
  reachable. Only 33–49% of the best models' generated games passed (VCR 0.33–0.49). **For 13:** the opening situation
  should come with a reachability audit. Can each subsystem the BRIEF lists (fight, explore, talk, get hurt, recover,
  grow, find and make things, shape the world) be triggered from the opening by at least one plausible player path?
  Can every hook be resolved and also failed? [R: research_notes/Long horizon LLM narrative benchmarks/rpgbench.md §overall evaluation methodology] [R: research_notes/Long horizon LLM narrative benchmarks/rpgbench.md §metrics] [BRIEF §1]
- **Offer all the challenge types.** → see 12.B. The starter region should contain at least one example of each
  named type (terrain, intelligent tactics, outnumbering, objective-based, time pressure, mixed encounters) and
  scenes that let each classic-fantasy archetype be pursued (→ 02 archetype coverage). [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Challenge Diversification]
- **Give the player situations with several ways through.** "Situations over plots": "an AI GM … would need to
  generate situations with multiple solution paths rather than scripted encounters". [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Core Principles of Good Dungeon Mastering]
- **Seed the fact types that break first.** Priorities: locks and possession, position, alive/present status,
  whether entities have been introduced yet, and numeric resources that change more than once. This helps
  playtesting too, because 13 doubles as the test bed for these failure categories. [R: reports/Long horizon LLM narrative benchmarks.md §What this means for Feature 002's spec]
- **Genre coverage:** NCP drew from 18 genres (Action 13%, Sci-Fi 12%, Comedy 11%, …). Only a scale reference. [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Methodology for constructing test scenarios]

---

## 14 — Player's Guide (player-facing guide and codex spec)

- **The codex must not become a menu.** P7's codex exists so narration doesn't turn into an info-dump and players can
  track their own complexity. The sources add that players accept AI rulings when they feel in control. A queryable
  codex that explains *why* a ruling went the way it did (which license, which DC, which degree) protects that sense
  of control. [R: research_notes/DM craft TTRPG design AI tools/ai_gm_academic_research.md §Fairness in Adjudicating Novel] [C:P7]
- **Offer two paths through the rules.** → see 02 (BG3 dual path). The guide can have a quick-start path and a full
  reference, and the depth is always available on request. [R: research_notes/DM craft TTRPG design AI tools/indie_niche_ttrpg_design_theory.md §Decision Paralysis]
- **Present rules with their reasons, and set tone.** PbtA books explain their rules, and the presentation carries
  tone and theme. "Mechanics are vibes too": granularity signals what the game cares about. [R: research_notes/DM craft TTRPG design AI tools/indie_niche_ttrpg_design_theory.md §Powered by the Apocalypse] [R: research_notes/DM craft TTRPG design AI tools/indie_niche_ttrpg_design_theory.md §Crunch vs. Playability]
- **Crunch is opt-in.** → see 02. [R: research_notes/DM craft TTRPG design AI tools/indie_niche_ttrpg_design_theory.md §Crunch vs. Playability]
- **Many players value control.** SillyTavern's popularity ("IDE for writers") shows a real segment of users prefers
  control to convenience. **For 14:** full transparency of one's own state through the codex is a feature for that
  segment. [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Community-Oriented Roleplay Platforms]
- **Say up front what the game will and won't do.** Being open about limits "is not railroading". The guide can
  explain the capability gate (VII) as a promise ("you can try anything; things beyond basic actions need a license,
  and the DM will always tell you what you *can* do instead"). [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Common Dungeon Master Mistakes] [C:VII]
- **The guide should tell players what to expect from the AI.** AI GMs are rated well on immersion and environment,
  weaker on "reading the room", emotional engagement and surprise. **For 14:** the guide should invite explicit
  feedback ("tell the DM more combat / less gore / faster pace") because the AI can't read faces. [R: research_notes/DM craft TTRPG design AI tools/ai_gm_academic_research.md §Player Experience and Comparative] [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Translating Human GM Skills to AI]

---

## Appendix-bound findings (decision log, traceability, open empirical questions)

- **Open empirical question template:** NCP/RPGBench-style playtests (adversarial and cooperative player personas,
  capped ≤50-word turns, visible-history-only, T=0-isolated seeds) are the field-standard method. They are MIT-licensed
  (`SpecificationGenerator(client).generate(source)`) and could be re-pointed at 13's starter outline. Any "open
  empirical question" about consistency can name this test. [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Published test-case construction prompts] [R: reports/Long horizon LLM narrative benchmarks.md §NCP-Bench proves synthetic construction]
- **RPGBench's GameChecker algorithm is tool-agnostic.** Recompute the "should-be" state by replaying the declared
  rules against the prior state, then diff per variable (buckets: complete-mismatch, range-invalid/unclamped, exact).
  It can audit real tool-call arguments. It's a named test for any `[D]` rule's live correctness. [R: research_notes/Long horizon LLM narrative benchmarks/rpgbench.md §state-tracking/memory specifically] [R: research_notes/Long horizon LLM narrative benchmarks/rpgbench.md §dataset construction / prompts]
- **RuleSmith self-play** is the named test for numeric balance questions (thresholds, costs, synergy values). [R: research_notes/DM craft TTRPG design AI tools/ai_gm_academic_research.md §Multi-Agent Approaches]
- **"Adopt everything as a hypothesis."** No system has been tested at scale (50+ sessions) with AI GMs. No designer
  has treated AI-GM adjudicability as a design criterion. [R: research_notes/DM craft TTRPG design AI tools/major_system_design_lessons.md §AI-GM Runability] [R: reports/DM craft TTRPG design AI tools.md §Major systems' 2024-era]

---

# 2. Concrete mechanics catalog ("search before building" inventory)

This lists every specific mechanic from a real game, tool or benchmark harness that appears in my sources. Each
entry gives: **System**, then **How it works** (mechanically precise, as far as the sources go; anything added from
outside the sources is flagged), then **Adopt/adapt →** the chapter(s) that could use it and how. Entries are grouped
by what they govern.

## 2.1 Resolution

**M-01 Four degrees of success, margin ±10, natural-die shift.** *System:* Pathfinder 2e.
*How:* Compare total to DC. Total ≥ DC+10 is a critical success. Total ≥ DC is a success. Total < DC is a failure.
Total ≤ DC−10 is a critical failure. A natural 20 moves the result one degree up and a natural 1 moves it one degree
down, whatever the margin, so a natural 20 that still misses the DC becomes a success, not a critical. Individual
actions define their crit effects (e.g. Strike deals double damage).
*Adopt →* 01 (already the project baseline, except that the project treats a natural 20/1 as an automatic
critical, see 01.A), 06 (crit damage). [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §How does Pathfinder 2e's four-degree system work] [R: reports/DM craft TTRPG design AI tools.md §Four candidate mechanics]

**M-02 Fate four outcomes on the ladder.** *System:* Fate Core.
*How:* Roll (4dF in Fate, not stated in the sources) plus skill against the opposition on an adjective ladder from +8
Legendary to −2 Terrible. Each rung is one "shift". Below the opposition is a Fail. Equal is a Tie: you get what you
wanted at a minor cost, or a lesser version of it. 1–2 shifts above is a Success. 3+ shifts is Succeed with Style.
*Adopt →* 01: a "success at a cost" band at DC±0–1, as an anti-stall device (P16). [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §How do OTHER systems implement graduated]

**M-03 Position × Effect.** *System:* Blades in the Dark.
*How:* Before rolling, the GM sets Position (controlled / risky / desperate: how bad the consequences can be) and
Effect (limited / standard / great: how much a success achieves). That gives 9 combinations. The 1d6-pool roll then
gives critical / success / partial / failure, read through that frame.
*Adopt →* 01 (a pre-roll frame as `[J]` with explicit criteria), 07 (announcing Position is the telegraphing device
for lethal stakes), 12. [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §How do OTHER systems implement graduated] [R: reports/DM craft TTRPG design AI tools.md §Four candidate mechanics]

**M-04 Orthogonal success/advantage dice.** *System:* Genesys / FFG Star Wars.
*How:* The dice show two independent pairs of symbols: Success/Failure and Advantage/Threat. Opposing symbols cancel
one for one, and the net of each pair is read separately. Results can be "success with threat" (success with a
complication) or "failure with advantage" (failure with a silver lining).
*Adopt →* 01: a secondary complication/boon axis separate from the degree (e.g. keyed off particular die faces), 12
(narrating side effects). [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §How do OTHER systems implement graduated] [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §documented tradeoffs]

**M-05 Counting successes in a dice pool.** *System:* World of Darkness.
*How:* Roll d10s equal to attribute plus skill. Each die at or above the target number is a success. Classic WoD sets
TN 6 by default, adjustable by difficulty, and each 1 cancels a success. New WoD fixes TN at 8 and drops the 1s rule.
The number of successes is the degree, so degrees scale with the size of the pool.
*Adopt →* 01, as an alternative reference only. Possibly 10/11 for extended tasks (accumulating successes). [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §How do OTHER systems implement graduated]

**M-06 Multiple-attack penalty.** *System:* PF2e.
*How:* The 2nd Strike in a turn takes −5 and the 3rd takes −10. Agile weapons take −4 and −8.
*Adopt →* 01 (compound or repeated attempts in one action window get escalating penalties), 06. [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §How do different systems structure what a character can do]

**M-07 Push yourself.** *System:* Blades in the Dark.
*How:* Take 2 stress to gain one of: +1d to the roll, +1 effect level, or the ability to act despite harm. Some
special abilities grant the push benefit without the stress cost.
*Adopt →* 01/05 (spend Focus to improve a roll or effect), 07 (act through injury). [R: research_notes/DM craft TTRPG design AI tools/cost_systems_and_move_based_abilities.md §How does Blades in the Dark structure its special abilities]

**M-08 Post-roll power selection ("flexible attacks").** *System:* 13th Age (fighter).
*How:* The fighter chooses which power applies *after* seeing the attack result. Every option still deals damage, so
there are no trap choices. (The published rule keys these to natural die values; that detail is not in the sources.)
*Adopt →* 05/06: abilities whose trigger is a rolled result, which is deterministic and P10-safe. [R: research_notes/DM craft TTRPG design AI tools/major_system_design_lessons.md §13th Age Design Mechanics]

**M-09 Skill challenge.** *System:* D&D 4e (named generically in the sources).
*How:* An extended task that needs several successful checks, contributed by several players or skills, to resolve.
*Adopt →* 01 (extended actions), 10, 12 (single-player version: require different approaches or tags). [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Spotlight Balance]

**M-10 Yes-and / Yes-but / strategic No.** *System:* improv-derived GM technique.
*How:* By default, accept what the player establishes and build on it. "Yes, but" accepts the premise and attaches a
cost, or bends it so it fits established continuity. Save an outright "no" for things that break the world or the
rules, and use it only after trust has been built through frequent acceptance.
*Adopt →* 01 (the wording of VII redirects), 12. [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Core Principles of Good Dungeon Mastering]

## 2.2 Action economy and cadence

**M-11 Three actions plus a reaction.** *System:* PF2e.
*How:* Each round you get 3 actions and 1 reaction. Things cost 1, 2 or 3 actions (Strike, Step, Seek, Interact and
Raise a Shield cost 1; most spells cost 2; some cost 3). Movement comes out of the same pool.
*Adopt →* 06 (the P9 front-runner). [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §How do different systems structure what a character can do] [C:P9]

**M-12 Action, bonus action and reaction.** *System:* D&D 5e.
*How:* Each creature gets 1 action, 1 bonus action and 1 reaction per round. A bonus action only exists if something
grants one, and you can't downgrade an action into one. The reaction refreshes at the start of your turn. If you cast a
bonus-action spell, you can only cast a cantrip with your action that turn.
*Adopt →* 06, mainly as a warning: a separate action type splits builds into those that feel busy every turn and those
that don't. [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §How do different systems structure what a character can do] [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §documented exploits]

**M-13 Standard/Move/Minor plus Action Points and power frequencies.** *System:* D&D 4e.
*How:* Each turn you get a Standard, a Move and a Minor action, plus one Opportunity Action (an opportunity attack) per
turn. Action Points are earned at milestones (finishing encounters without an extended rest) and each buys one extra
action. Powers come as at-will, encounter or daily.
*Adopt →* 05 (vocabulary for recharge frequency), 06 (milestone-earned surge actions). [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §How do different systems structure what a character can do]

**M-14 Move + (2 quick OR 1 full) + Overcharge; NPC asymmetry.** *System:* Lancer.
*How:* Each turn you get a move, then either two quick actions (Skirmish, Boost, Quick Tech, activating a system) or one
full action, plus free actions. Overcharge buys one extra action for heat, which raises later heat damage. NPCs cannot
Brace (a defensive reaction) and cannot Overcharge.
*Adopt →* 06 (the flexible-or-focused turn choice; Focus spent for an extra action), 09 (asymmetric adversary action
sets). [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §How do different systems structure what a character can do] [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §design techniques]

**M-15 Offensive, defensive and neutral action slots.** *System:* design pattern from the sources (no named game).
*How:* The turn is split into typed slots so no single action type can dominate.
*Adopt →* 06, as an alternative to a single fungible pool. [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §design techniques]

**M-16 In-combat escalation per class.** *System:* 13th Age.
*How:* A bard's song gets an escalating effect on its final verse. A sorcerer charges a spell before attacking. These
build-up mechanics differ by class.
*Adopt →* 05/06: differentiation by cadence (P14). [R: research_notes/DM craft TTRPG design AI tools/major_system_design_lessons.md §13th Age Design Mechanics] [C:P14]

## 2.3 Ability design

**M-17 Three stunt patterns.** *System:* Fate Core.
*How:* Pattern 1 adds a new action (a skill does what it normally can't). Pattern 2 gives +2 in narrow circumstances.
Pattern 3 makes one rule exception in a narrow context, and may not touch the core aspect/fate-point economy. Every
stunt must be limited to specific actions, be situationally restricted, and optionally carry a frequency cap (once per
conflict, scene or session).
*Adopt →* 05 (the template grammar for all abilities), 04 (tier grants), 08 (item abilities). [R: research_notes/DM craft TTRPG design AI tools/cost_systems_and_move_based_abilities.md §How does Fate Core's "stunts" system work]

**M-18 Refresh economy and fate-point-powered stunts.** *System:* Fate Core.
*How:* You start with 3 refresh, and each stunt costs 1 refresh, down to a minimum of 1. More stunts means fewer fate
points each session. A stunt whose effect is powerful or has no natural limit (especially one that affects conflict
stress) costs a fate point per use.
*Adopt →* 05: Focus plays the fate point's role for unlimited or conflict-affecting effects. The slot cap plays the
refresh role. [R: research_notes/DM craft TTRPG design AI tools/cost_systems_and_move_based_abilities.md §How does Fate Core's "stunts" system work]

**M-19 Stunt families.** *System:* Fate Core.
*How:* Stunts can require earlier stunts. A later stunt either **stacks** (strengthens the prerequisite) or
**branches** (adds a related but mechanically distinct ability and leaves the prerequisite unchanged).
*Adopt →* 04 (tier deepening as branching, compatible with VI), 05. [R: research_notes/DM craft TTRPG design AI tools/cost_systems_and_move_based_abilities.md §How does Fate Core's "stunts" system work]

**M-20 Playbook special abilities.** *System:* Blades in the Dark.
*How:* Each playbook has 7 abilities with narrow triggers. Most give +1d or +1 effect in a specific context, or spend
a renewable resource ("special armor", restored at the start of downtime). Several let you take a push benefit without
paying stress. Standouts such as "Functioning Vice" are much stronger than the rest.
*Adopt →* 05 (trigger clarity; mix incremental and transformative abilities), 10 (downtime refresh). [R: research_notes/DM craft TTRPG design AI tools/cost_systems_and_move_based_abilities.md §How does Blades in the Dark structure its special abilities]

**M-21 Moves.** *System:* PbtA (Apocalypse World, Dungeon World).
*How:* Fiction comes first. When the player's described action matches a move's trigger ("Act Under Fire",
"Investigate a Mystery", "Call in a Debt"), the move's fixed resolution runs. A playbook usually has 10–12 moves.
*Adopt →* 05 (P10: precisely triggered permissions may carry core power), 01 (trigger-matching for the basic-action
tier). [R: research_notes/DM craft TTRPG design AI tools/cost_systems_and_move_based_abilities.md §design spectrum] [R: research_notes/DM craft TTRPG design AI tools/indie_niche_ttrpg_design_theory.md §Powered by the Apocalypse]

**M-22 Always-on abilities rebuilt as conditional ones.** *System:* 13th Age 1e → 2e Ranger.
*How:* In 1e the Ranger's always-available abilities had to be weak, so the 2e redesign made them conditional and active,
with much higher damage.
*Adopt →* 04/05: a power-budget rule that passives are weak and conditionals are strong. [R: research_notes/DM craft TTRPG design AI tools/major_system_design_lessons.md §13th Age Design Mechanics]

**M-23 Weapon Mastery traits.** *System:* D&D 5e (2024).
*How:* Every martial weapon carries a mastery trait that adds a rider on attack: AOE damage, pushing the target, or
imposing disadvantage.
*Adopt →* 08 (weapon properties as built-in maneuvers), 06. *Warns:* in 5e this fixed only one side of the balance
ledger. [R: research_notes/DM craft TTRPG design AI tools/major_system_design_lessons.md §D&D 5e Balance Problems]

**M-24 Power attack (−5 to hit / +10 damage).** *System:* D&D 5e Sharpshooter / Great Weapon Master.
*How:* An optional trade of −5 to hit for +10 damage.
*Adopt →* none directly. It is the textbook **ability tax**: it outperforms alternatives so reliably that it stops
being optional. Audit any accuracy-for-damage trade against it. [R: research_notes/DM craft TTRPG design AI tools/major_system_design_lessons.md §D&D 5e Balance Problems]

## 2.4 Character creation and cost systems

**M-25 Power Level caps.** *System:* Mutants & Masterminds.
*How:* Everything is bought from one point pool, at 15 power points per Power Level. PL caps attack bonus, damage,
dodge/parry and toughness. PL 10 is the default ("Marvel team book") and DC-style heroes run PL 14–16. The cap
contains power disparity rather than preventing it.
*Adopt →* 00 (hard ceilings), 09 (threat band as a PL-like danger bracket). [R: research_notes/DM craft TTRPG design AI tools/cost_systems_and_move_based_abilities.md §How does Mutants & Masterminds' point-buy system work]

**M-26 Bracketed costs.** *System:* HERO System / Champions (1981, the first point-based creation).
*How:* A base 1d6 of effect costs 5 points (STR, Blast). Dispel costs 3 per die, Drain 6 per die, Killing Attack 15 per
die. Defense costs less than offense. Limitations reduce cost. Players must buy skills, disadvantages and powers
together.
*Adopt →* 05 (Focus cost bands by effect category), 02 (if any currency is used). [R: research_notes/DM craft TTRPG design AI tools/cost_systems_and_move_based_abilities.md §HERO]

**M-27 Zero-sum Hindrances and Edges.** *System:* Savage Worlds.
*How:* You start at 0. A Minor Hindrance gives 1 point and a Major gives 2, with a maximum of 1 Major and 2 Minor. An
Edge costs 2, and attributes and skills can also cost points. The final budget must be exactly 0.
*Adopt →* 02 (origin trade-offs, P4, if built as a currency). [R: research_notes/DM craft TTRPG design AI tools/cost_systems_and_move_based_abilities.md §13th Age and Savage Worlds]

**M-28 One Unique Thing and Icon Relationships.** *System:* 13th Age.
*How:* One Unique Thing is a narrative-only distinctive fact about the character, usually non-combat. Icon
Relationships are 3 points spread across relationships with the setting's great powers, and they measure influence
and usefulness.
*Adopt →* 02 (a narrative distinctive plus faction ties at creation), 11 (PC–faction relationships). [R: research_notes/DM craft TTRPG design AI tools/cost_systems_and_move_based_abilities.md §13th Age and Savage Worlds] [R: research_notes/DM craft TTRPG design AI tools/major_system_design_lessons.md §13th Age Design Mechanics]

**M-29 Unrestricted point pool (negative reference).** *System:* GURPS.
*How:* One flat pool for everything. This invites attribute arbitrage (a broad attribute is cheaper than narrow skills),
disadvantage gaming, and power stacking. A 40-point focused fighter can beat a 200-point generalist.
*Adopt →* none. It is the P11 counter-example. [R: reports/DM craft TTRPG design AI tools.md §Four candidate mechanics] [R: research_notes/DM craft TTRPG design AI tools/cost_systems_and_move_based_abilities.md §Cross-System Summary]

**M-30 Playbook, specialties and bonds.** *System:* Dungeon World (plus the "Class Warfare" supplement).
*How:* You pick an archetype playbook (starting moves, races, alignments, bond suggestions) and then 2–3 specialties.
Bonds tie the PC to the other characters.
*Adopt →* 02 (origin plus 2–3 specialties; bonds as story hooks). [R: research_notes/DM craft TTRPG design AI tools/indie_niche_ttrpg_design_theory.md §Dungeon World]

**M-31 A quick path through character creation.** *System:* Baldur's Gate 3.
*How:* Casual players can "speedrun the character sheet", while the full depth stays available.
*Adopt →* 02, 14. [R: research_notes/DM craft TTRPG design AI tools/indie_niche_ttrpg_design_theory.md §Decision Paralysis]

**M-32 Proficiency ladder.** *System:* PF2e.
*How:* Proficiency runs Trained → Expert → Master → Legendary, and everything proficient gains +1 per level. Feats come
at every level in class, ancestry, skill and general categories. Skill feats represent specific extraordinary
abilities.
*Adopt →* 04 (named tier ladder; not the per-level +1, which P2 forbids). [R: research_notes/DM craft TTRPG design AI tools/major_system_design_lessons.md §Pathfinder 2e Design Philosophy] [R: research_notes/DM craft TTRPG design AI tools/major_system_design_lessons.md §Head-to-Head]

**M-33 Bounded accuracy.** *System:* D&D 5e.
*How:* A character's best bonus is about +5 at level 1 and about +11 at level 20.
*Adopt →* 00 (scale reference for the d20 + mod vs DC 10/15/20/25 baseline). [R: research_notes/DM craft TTRPG design AI tools/major_system_design_lessons.md §Head-to-Head]

## 2.5 GM craft, encounter and pacing techniques

**M-34 Player Goal Chart.** *System:* Robin's Laws of Good Game Mastering.
*How:* For each player, record their archetype (power gamer, butt-kicker, tactician, specialist, method actor,
storyteller or casual), their goals, and the specific planned actions that will serve those goals over the campaign.
*Adopt →* 12 (a player-preference record for solo play), 02 (captured at creation). [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Spotlight Balance]

**M-35 Spotlight rotation.** *System:* general GM craft (Gooey Cube; the Alexandrian).
*How:* Switch focus about every 10–15 minutes, when it feels natural. Balance across the whole campaign arc rather than
each session. Use encounters that need several kinds of input.
*Adopt →* 12 (reinterpreted for one player as rotation across facets, pillars and challenge types). [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Spotlight Balance]

**M-36 Challenge diversification toolkit.** *System:* the Alexandrian, Sly Flourish, Scroll for Initiative.
*How:* Vary terrain (lava, chokepoints, open ground where range matters, threats both ranged and melee). Play
opponents intelligently. Tilt the action economy with 3–12 opponents. Use objectives (a ritual, hostages, an alarm,
avoiding bloodshed). Apply time pressure ("three days"). Manage magic items. Mix encounters.
*Adopt →* 06, 09, 11, 12, 13. [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Challenge Diversification]

**M-37 The "lazy" monster buff.** *System:* Sly Flourish.
*How:* Treat the PCs as higher level when picking challenges. Maximize hit dice, or double HP to make an "elite". Push
damage toward maximum. Add attacks.
*Adopt →* 09 (an elite template). [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Challenge Diversification]

**M-38 Roll twice and combine.** *System:* Sly Flourish.
*How:* Roll twice on the encounter table and combine the results: the two groups are fighting each other, one has just
wiped out the other, or they are allied.
*Adopt →* 09, 11. [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Challenge Diversification]

**M-39 Adjusting mid-combat.** *System:* Sly Flourish.
*How:* Add or remove monsters, adjust HP within its range, or change damage during play.
*Adopt →* only in diegetic form, as logged events. → Tensions T-5. [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Challenge Diversification]

**M-40 Session Zero.** *System:* D&D Beyond guidance.
*How:* Agree theme and tone, duration, schedule, absence policy and house rules, plus hard limits (never crossed) and
soft limits (acceptable in moderation).
*Adopt →* 02, 12, 14. [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Core Principles of Good Dungeon Mastering]

**M-41 Skipping empty time.** *System:* the Alexandrian.
*How:* Cut straight past stretches where no meaningful decision happens.
*Adopt →* 10, 12. [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Core Principles of Good Dungeon Mastering]

**M-42 Situation-specific procedures.** *System:* Errant.
*How:* Dedicated procedures for running estates and for legal trials.
*Adopt →* 10 (downtime subsystems). [R: research_notes/DM craft TTRPG design AI tools/indie_niche_ttrpg_design_theory.md §Crunch vs. Playability]

## 2.6 State, memory and verification machinery (tools, harnesses and papers)

**M-43 Typed commitments.** *System:* NCP-Bench.
*How:* Each commitment is `{id, type ∈ {invariant, ordering, achievement}, description, satisfaction_condition,
violation_condition}`. Conditions are fact-based, mutually exclusive, unique, and directly determinable. An invariant
must hold across a span. An ordering requires A before B. An achievement is required, and it is violated if its
violation condition fires *or* success becomes impossible.
*Adopt →* 11 (faction agendas, clocks, hooks), 00 (state types). [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §What exactly is "Narrative Commitment Preservation" (NCP)]

**M-44 Specification pipeline and T=0 isolation.** *System:* NCP-Bench `SpecificationGenerator`.
*How:* Three dependent stages. (1) An atomic trajectory, where each node has a trigger_event and an observable
key_delta, told from the player's point of view. (2) Commitments conditioned on the trajectory. (3) Initial facts
conditioned on both, holding only present-state facts, stating ignorance explicitly, and grouped as cognitive,
positional or relational.
*Adopt →* 13 (authoring the starter region), 11 (seeding a sandbox region). [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Methodology for constructing test scenarios]

**M-45 Fact-ledger update rule.** *System:* NCP-Bench `fact_update.txt`.
*How:* Add a fact only if it is conclusively established (not just attempted or foreshadowed), atomic, and not a
duplicate. Remove a fact only if it is explicitly invalidated without speculation. Output `{new_facts, facts_to_remove,
justification}`.
*Adopt →* 03 (`tag_event` discipline), 12 (writing to state after each turn). [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Methodology for constructing test scenarios]

**M-46 Conflict auditor with a double-check.** *System:* NCP-Bench `conflict_check.txt` and `conflict_double_check.txt`.
*How:* Inputs: role, history, current input, the story being audited, candidate updates, trajectory status, current
node, pre-turn facts, and commitments. Output: counts for fact, commitment and player-input conflicts, with reasons.
Precedence goes to the most recent visible state. Upgrades to perception, memory, mobility, control, access, awareness
or freedom need justification. Denying or redirecting the player is allowed if their intent is acknowledged. A second
pass must confirm a conflict before it counts.
*Adopt →* 12 (DM verification step), 01 (acceptance criteria for VII). [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §What exactly is "Narrative Commitment Preservation" (NCP)] [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Metrics]

**M-47 Player personas.** *System:* NCP-Bench `adversarial_input.txt` and `natural_input.txt`.
*How:* A simulated player, either adversarial (suspicious, exploit-seeking: tests consistency, probes boundaries,
interrogates NPCs, breaks tone, tries to derail) or natural (a cooperative, immersed player). Turns are 50 words or
fewer, in first person, based on visible history only, with no meta commentary.
*Adopt →* `_process/playtests/` and open empirical tests. [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Methodology for constructing test scenarios]

**M-48 Game schema and rule replay.** *System:* RPGBench.
*How:* State variables and hidden variables, each with min, max and initial values. Events carry entering, succeed and
fail conditions and effects as evaluable expressions. There are global checks before events. Each round follows
event planning → narration plus three action options → state update. The checker replays the declared rules against
the previous state and diffs every variable. MEC is the fraction of rounds with no errors.
*Adopt →* 00 (the form of data triggers and effects), `_process/simulation/`. [R: research_notes/Long horizon LLM narrative benchmarks/rpgbench.md §overall evaluation methodology] [R: research_notes/Long horizon LLM narrative benchmarks/rpgbench.md §state-tracking/memory specifically]

**M-49 BFS validity check.** *System:* RPGBench.
*How:* A breadth-first search over the game graph confirms that a success ending, a failure ending, and every declared
event can all be reached.
*Adopt →* 13 (reachability audit for the starter situation), 11 (generated hooks). [R: research_notes/Long horizon LLM narrative benchmarks/rpgbench.md §overall evaluation methodology]

**M-50 Checking against a knowledge tree.** *System:* LLM detective game ("The Interrogation of Adrian Gale", arXiv:2609.23043).
*How:* Three agents: retrieval, dialogue and verification. A knowledge tree encodes what the suspect is allowed to
reveal in the current narrative state, and output is verified before the player sees it. Reported results: −64.78%
critical hallucinations and no premature disclosures.
*Adopt →* 01 (P17), 10 (investigation), 12 (verification). [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §Other 2025–2026 benchmarks]

**M-51 Ledgers plus RAG.** *System:* NarrativeEngine (and LOTM-GAME).
*How:* Persistent ledgers hold characters and locations. A dynamic RAG layer holds factions, economy and events, about
1,200 tokens per turn. NPCs have values, goals and relationships, and they drift over time. State is versioned, with
rollback and branching.
*Adopt →* 00, 09, 11. [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Open-Source AI Dungeon Master Projects]

**M-52 Engine-owned state.** *System:* Open Dungeon; SRD Rules Engine (ECS, data-driven).
*How:* A deterministic engine owns all state. The LLM narrates results and interprets what the player means, but it
cannot invent results.
*Adopt →* 00 (the far end of the authority spectrum). [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Open-Source AI Dungeon Master Projects] [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Supporting Infrastructure]

**M-53 Lorebook and character card.** *System:* NovelAI, SillyTavern, DreamGen.
*How:* A character card holds name, description, personality, speech examples (few-shot), goals, relationships and
secrets. Lore entries are indexed by tags and injected when their tags match the current context. DreamGen supports
3–4 distinct characters in one scene.
*Adopt →* 09 (NPC records), 00 (tag-keyed retrieval). [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Key Architectural Patterns] [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §AI-Driven Interactive Fiction Platforms]

**M-54 Typed variables and flows in branching-narrative tools.** *System:* Ink, Yarn Spinner, ChoiceScript, Twine, NarrativeFlow.
*How:* Typed variables (numbers, strings, booleans) are serialized to JSON. Ink runs parallel story flows that share
state. ChoiceScript's first-class `*create/*set/*if` supports stat-driven branching. Yarn's Variable Storage persists
across sessions.
*Adopt →* 00 (the shape of the state store). [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Non-AI Branching Narrative Tools]

**M-55 Automation on a virtual tabletop.** *System:* Foundry VTT (Dynamic Active Effects, Midi-QOL).
*How:* Modules automate rolls, damage, spell effects and resource tracking, separately from how things are displayed.
*Adopt →* 00 (precedent for tool-owned effects). [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Supporting Infrastructure]

**M-56 Active storyline memory.** *System:* BOOKMARKS (arXiv:2605.14169).
*How:* The full storyline stays available. Bookmark checkpoints are updated passively and used to retrieve relevant
content on demand, instead of compressing history into summaries.
*Adopt →* 12 (memory policy). [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §Other 2025–2026 benchmarks]

**M-57 Hierarchical memory (the documented trade-off).** *System:* HiAgent (as used in NCP-Bench).
*How:* A hierarchical memory that summarizes. It raised survival and lowered commitment conflicts, but more than
doubled player-input conflicts.
*Adopt →* 12 (as a warning; keep recent turns verbatim). [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Mitigation strategies]

**M-58 Event-aware memory graph.** *System:* DREAM (arXiv:2608.05170).
*How:* Text is turned into events that are ordered in time and linked causally (the Activating-Event → Belief →
Consequence model). Each character profile has stable traits plus changes driven by events.
*Adopt →* 09 (NPC records), 11 (propagating consequences). [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §Other 2025–2026 benchmarks]

**M-59 Fabula/discourse split.** *System:* TRPG multi-agent GM research (wordplay workshop).
*How:* A Director or simulation agent plans the events. A Narrator topologically sorts them and turns only the events
relevant to the current scene into prose, controlling the pace.
*Adopt →* 00, 11, 12. [R: research_notes/DM craft TTRPG design AI tools/ai_gm_academic_research.md §Multi-Agent Approaches]

**M-60 PLAYER\*.** *System:* PLAYER* (arXiv:2404.17662).
*How:* Sensors for emotion, motivation and opportunity drive which question is asked next. A pruner discards
low-information actions. Anytime sampling-based planning (RRT*-style) builds a search tree and prunes it as play goes on.
*Adopt →* 09 (adversary and NPC decision-making), 10 (investigation NPCs). [R: research_notes/DM craft TTRPG design AI tools/ai_gm_academic_research.md §Multi-Agent Approaches]

**M-61 RuleSmith.** *System:* RuleSmith (arXiv:2602.06232).
*How:* Two LLM agents play opposing factions using a natural-language rulebook and a structured description of the game
state. Bayesian optimization (with a Gaussian-process surrogate and adaptive sampling) tunes a 12-dimensional parameter
space to minimize the gap in win rates.
*Adopt →* `_process/simulation/`, and the numeric tuning in 04, 05 and 06. [R: research_notes/DM craft TTRPG design AI tools/ai_gm_academic_research.md §Multi-Agent Approaches]

**M-62 Memory compaction policy.** *System:* practitioner guidance (Morph).
*How:* Keep verbatim the precise facts, numbers, direct quotes and the most recent ~10% of context. It is safe to
compress narrative scene-setting, reasoning chains that have already been acted on, and redundant observations. Use
verbatim compaction first (it keeps 50–70% of the text). Never compress something that has already been compressed;
hand off to a fresh context instead.
*Adopt →* 12 (session structure). [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §Mitigation strategies: quantified evidence]

**M-63 Evaluation instruments.** *System:* NARRA-Gym (11 dimensions, three-judge sweep, Plackett-Luce human ranking); SQD
(23 dimensions, Delphi, Kano); RPGBench (MEC, FAC, PER via TIPI, INT, and ACT covering diversity, relevance and
understandability); NCP (Conflict / Survival / Success); FAMA (penalizes use of obsolete memory); CED (errors per 10K
words, from ConStory-Checker); VR NPC instruments (a 36-item believability questionnaire across 9 dimensions on 7-point
scales, SUS, the social-presence module of the GEQ).
*Adopt →* `_process/playtests/` and `_process/audits/`. [R: research_notes/DM craft TTRPG design AI tools/ai_gm_academic_research.md §Evaluation Methodologies] [R: research_notes/DM craft TTRPG design AI tools/ai_gm_academic_research.md §Player Experience and Comparative] [R: research_notes/Long horizon LLM narrative benchmarks/rpgbench.md §metrics] [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §What exactly is the "Lost in Stories" taxonomy] [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §Other 2025–2026 benchmarks]

**M-64 Seven guardrail strategies and layered prompting.** *System:* practitioner guidance.
*How:* The guardrails are schemas, retrieval, tool use, verification, decoding constraints, policy gates and
observability. Layered prompting puts core rules and current-turn mechanics at the top, character and recent events in
the middle, and lore and creative voice at the bottom or in a separate injection. Separating combat rules from craft
guidance is reported to improve rule adherence.
*Adopt →* 00 (chapter-contract separability), 12. [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Technical Approaches to Bounded AI Narration] [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Key Architectural Patterns]

**M-65 Theory frames (diagnostics, not mechanics).** *System:* GNS (Edwards); the Big Model (Ephemera ⊂ Techniques ⊂
Exploration ⊂ Social Contract, with Creative Agendas including Simulationism as "The Right to Dream"); the Kobold Guide
(240 pages, 40 essays, including Stackpole's "Designing Magic Systems" and Heinsoo's "Seize the Hook", 2012 Gold ENnie).
*Adopt →* the design-intent sections. There is no mechanical content to adopt; the Kobold Guide's essays themselves
were not accessible. [R: research_notes/DM craft TTRPG design AI tools/indie_niche_ttrpg_design_theory.md §GNS Theory] [R: research_notes/DM craft TTRPG design AI tools/indie_niche_ttrpg_design_theory.md §Kobold Guide]

---

# 3. Numbers ledger

Every concrete number in the sources, grouped by what it measures. The "Grade" column uses the preamble's A–D scale.
Where the sources' numbers are internally inconsistent, the register in the preamble explains it.

## 3.1 Long-horizon consistency: NCP-Bench

| Number | Meaning / context | Grade | Cite |
|---|---|---|---|
| 42% | GPT-5.2 (best model) survival rate at turn 20: share of episodes with no audited conflict through turn 20 | B | [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Failure modes] |
| 40–68% | Fact-conflict incidence across the 6 narrator models (see register #1: these are incidence rates, not shares) | B | [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Failure modes] |
| ~3.5% | Share of all interactions (all models and conditions) that reached the 100-turn cap with no flagged conflict | B | [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Failure modes] |
| 100 turns | Episode cap | A | [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Metrics] |
| 100 / 18 | Environments / genres (Action 13%, Sci-Fi 12%, Comedy 11%, …), taken from the CMU Movie Summary Corpus | A | [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Methodology for constructing test scenarios] |
| 1,660 (16.6/env) | Initial facts | A | [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §What exactly is "Narrative Commitment Preservation" (NCP)] |
| 1,222 (12.2/env) | Commitments | A | [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §What exactly is "Narrative Commitment Preservation" (NCP)] |
| 1,511 (15.1/env) | Trajectory nodes | A | [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §What exactly is "Narrative Commitment Preservation" (NCP)] |
| 5 fields | Per commitment: id, type, description, satisfaction condition, violation condition | A | [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §What exactly is "Narrative Commitment Preservation" (NCP)] |
| 3 | Commitment types (invariant, ordering, achievement); also 3 conflict types (fact, commitment, player-input) and 3 episode outcomes (Conflict, Survival, Success) | A | [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §What exactly is "Narrative Commitment Preservation" (NCP)] [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Metrics] |
| 7 | High-sensitivity attributes that need explicit justification before upgrade: perception, memory, mobility, control, access, awareness, freedom | A | [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §What exactly is "Narrative Commitment Preservation" (NCP)] |
| GPT-5.2 | 32.92 avg turns; 9.94% trajectory; 11.22% satisfied; 40% fact / 24% commitment / 31% player-input; ~42% survival@20 | B (fact/commit/PI double-confirmed) | [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Failure modes] |
| GPT-4o-mini | 24.80; 10.57%; 10.90%; 64/32/11; ~30% survival@20 | B (single pass) | [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Failure modes] |
| DeepSeek-V3.2 | 15.88; 15.40%; 13.42%; 55/32/23; ~15% | B (fact/commit/PI double-confirmed) | [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Failure modes] |
| Qwen3-235B-A22B | 16.76; 13.16%; 10.60%; 68/33/26; ~12% | B (fact/commit/PI double-confirmed) | [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Failure modes] |
| Grok-4.1-Fast | 7.87; 12.07%; 10.37%; 65/47/12; ~5% | B (single pass) | [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Failure modes] |
| Kimi-K2.5 | 2.88; 10.26%; 5.18%; 66/54/11; <1% | B (single pass) | [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Failure modes] |
| 22.16 vs 46.08 | GPT-4o-mini average turns, adversarial vs natural player (the natural player roughly doubles survival) | B | [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Failure modes] |
| 16.64% vs 21.52% | Trajectory progress, adversarial vs natural | B | [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Failure modes] |
| 10.03% vs 12.56% | Satisfied commitments, adversarial vs natural | B | [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Failure modes] |
| 60% vs 56% | Fact conflicts, adversarial vs natural (barely moves) | B | [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Failure modes] |
| 26% vs 9% | Commitment conflicts, adversarial vs natural (~3× cut) | B | [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Failure modes] |
| 22.16 → 30.05 | Average turns, baseline → HiAgent (GPT-4o-mini, audited by GPT-5.4-mini) | B | [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Mitigation strategies] |
| 26% → 4% | Commitment conflicts, baseline → HiAgent | B | [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Mitigation strategies] |
| 13% → 38% | Player-input conflicts, baseline → HiAgent | B | [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Mitigation strategies] |
| 60% → 59% | Fact conflicts, baseline → HiAgent (unchanged) | B | [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Mitigation strategies] |
| 16.64% → 15.68% | Trajectory progress, baseline → HiAgent (slightly worse) | B | [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Mitigation strategies] |
| 10.03% → 9.14% | Satisfied commitments, baseline → HiAgent (slightly worse) | B | [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Mitigation strategies] |
| T 0.6 / top-p 0.95 / 8,092 tok | Narrator decoding settings (temperature, nucleus sampling, max generation length) | A | [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Methodology for constructing test scenarios] |
| ≤50 words | Simulated player turn length cap | A | [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Methodology for constructing test scenarios] |
| "<50% by turns 5–15", "0 by 40–60" | Survival-curve readouts from the chart. **The notes say not to cite these as precise.** | D | [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Failure modes] |

## 3.2 Long-horizon consistency: RPGBench

| Number | Meaning | Grade | Cite |
|---|---|---|---|
| 10 rounds | Main simulation length | A | [R: research_notes/Long horizon LLM narrative benchmarks/rpgbench.md §overall evaluation methodology] |
| {10, 15, 20, 25} | Length ablation (GPT-4o only): MEC declines, INT declines, FAC rises then stabilizes | B | [R: research_notes/Long horizon LLM narrative benchmarks/rpgbench.md §which models/architectures] |
| 100 → 125 | Wikipedia character pages → valid generated games (GPT-4o 49, DeepSeek V3 38, Gemini 2.0 Flash Exp 33, Gemini 1.5 Pro 4, Claude 3.5 Sonnet 1) | A/B | [R: research_notes/Long horizon LLM narrative benchmarks/rpgbench.md §overall evaluation methodology] |
| 5-shot | Game-creation prompting (examples authored with GPT-4o) | B | [R: research_notes/Long horizon LLM narrative benchmarks/rpgbench.md §overall evaluation methodology] |
| VCR 0.49 / 0.38 / 0.33 / 0.04 | Game-creation validity pass rate for GPT-4o / DeepSeek V3 / Gemini 2.0 Flash / Gemini 1.5 Pro | B | [R: research_notes/Long horizon LLM narrative benchmarks/rpgbench.md §metrics] |
| ~95% | Claude 3.5 Sonnet refusal rate on game creation | B | [R: research_notes/Long horizon LLM narrative benchmarks/rpgbench.md §which models/architectures] |
| MEC 0.765 / 0.693 / 0.554 | Mechanical consistency at 10 rounds for Gemini 2.0 Flash Exp / GPT-4o / Gemini 1.5 Pro | B | [R: research_notes/Long horizon LLM narrative benchmarks/rpgbench.md §metrics] |
| FAC 0.885–0.991 | Factual consistency range across models | B | [R: research_notes/Long horizon LLM narrative benchmarks/rpgbench.md §metrics] |
| INT 0.420–0.722 | Interestingness range | B | [R: research_notes/Long horizon LLM narrative benchmarks/rpgbench.md §metrics] |
| r ≈ 0.129 / 0.140 | Human vs LLM-judge correlation for FAC / INT (20-game subset) | B | [R: research_notes/Long horizon LLM narrative benchmarks/rpgbench.md §metrics] |
| 1–5 | Big-Five trait rating per NPC; also the INT and ACT rubric scale, normalized to [0,1] | A | [R: research_notes/Long horizon LLM narrative benchmarks/rpgbench.md §state-tracking/memory specifically] [R: research_notes/DM craft TTRPG design AI tools/ai_gm_academic_research.md §Evaluation Methodologies] |
| 3 | Candidate next actions offered per round; also 3 ACT sub-rubrics (diversity, relevance, understandability) and 3 per-round stages | A/B | [R: research_notes/Long horizon LLM narrative benchmarks/rpgbench.md §overall evaluation methodology] [R: research_notes/Long horizon LLM narrative benchmarks/rpgbench.md §metrics] |
| ~94k chars | Longest source character description | A | [R: research_notes/Long horizon LLM narrative benchmarks/rpgbench.md §overall evaluation methodology] |

## 3.3 Long-horizon consistency: other papers

| Number | Meaning | Grade | Cite |
|---|---|---|---|
| 5 / 19 | "Lost in Stories" error categories / subtypes (ConStory-Bench: 2,000 prompts, 4 task scenarios) | B | [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §What exactly is the "Lost in Stories" taxonomy] |
| 0.113 / 0.520 / 0.537 | Consistency Error Density (errors per 10K words) for GPT-5-Reasoning / Claude-Sonnet-4.5 / Qwen3-32B | B | [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §What exactly is the "Lost in Stories" taxonomy] |
| 15–30% / 40–60% | Normalized story position where facts are planted / where their contradictions cluster | B | [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §What exactly is the "Lost in Stories" taxonomy] |
| 31.0% / 4.7% | Average plant-to-contradiction gap for geographical / perspective errors | B | [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §What exactly is the "Lost in Stories" taxonomy] |
| +19.24% | Token-entropy increase in error spans (Qwen3-4B) | B | [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §What exactly is the "Lost in Stories" taxonomy] |
| linear | Errors accumulate roughly linearly with output length | B | [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §What exactly is the "Lost in Stories" taxonomy] |
| 0.30–0.95 (0.45 gap) | Embedding-retrieval accuracy on updated facts across models (max seed-to-seed gap) | B | [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §Other 2025–2026 benchmarks] |
| 0.70–1.00 | Update-on-write store and LLM-summarization accuracy on updated facts | B | [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §Other 2025–2026 benchmarks] |
| 55% | Rate at which agents act correctly on a correctly retrieved updated fact | B | [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §Other 2025–2026 benchmarks] |
| 0.00 → 0.55–1.00 | Dependent-task success with no memory → with memory (GPT-4.1, Claude Haiku 4.5) | B | [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §Other 2025–2026 benchmarks] |
| up to 60 points | Change in task success from swapping memory implementation | B | [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §Other 2025–2026 benchmarks] |
| 2.7–3.9× | Marginal utility per dollar, best vs worst memory configuration | B | [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §Other 2025–2026 benchmarks] |
| 39.44% → 45.42% | BOOKMARKS mystery-reasoning accuracy vs the strongest (summarization) baseline; 47 characters, 6 narratives, 9,537 test cases | B | [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §Other 2025–2026 benchmarks] |
| −64.78% | Critical hallucinations with the knowledge-tree plus verification agent; premature disclosure dropped to 0 | B | [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §Other 2025–2026 benchmarks] |
| 10 / ~600 / ~16K / 1,986 | LOCOMO: conversations / turns per conversation / tokens per conversation / QA pairs | B | [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §Other 2025–2026 benchmarks] |
| 86.17 vs 79.09 | RGMem vs Zep, LOCOMO overall | B | [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §Other 2025–2026 benchmarks] |
| 74.8 vs 64.2 | "Mode A Retrieval" vs Mem0, LOCOMO | B | [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §Other 2025–2026 benchmarks] |
| 94.37 (96.73 / 94.34 / 89.32 / 77.33) | Synthius-Mem LOCOMO overall (single-hop / multi-hop / temporal / open-domain) | B | [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §Other 2025–2026 benchmarks] |
| <50% at 128K | Oolong accuracy for GPT-5, Claude-Sonnet-4 and Gemini-2.5-Pro | B | [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §Oolong] |
| 1,547 | Papers reviewed by the Horizon Gap survey (2024–2026) | B | [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §Oolong] [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §Other 2025–2026 benchmarks] |
| ~10% | Most recent share of context to keep verbatim | C | [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §Mitigation strategies: quantified evidence] |
| 50–70% | Verbatim compaction's compression ratio | C | [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §Mitigation strategies: quantified evidence] |
| 4 of 5 | Agentic settings where observation masking beat LLM summarization | C | [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §Mitigation strategies: quantified evidence] |
| ~46.1% | Exact-match state prediction from the prior (second) report, cited by the DMR; not directly comparable to 42% (register #9) | B | [R: reports/DM craft TTRPG design AI tools.md §The tools landscape] |

## 3.4 AI-GM tooling and player experience

| Number | Meaning | Grade | Cite |
|---|---|---|---|
| ~1,200 tokens/turn | NarrativeEngine dynamic RAG injection | C | [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Open-Source AI Dungeon Master Projects] |
| sessions 1–10 / 10–50 / 50+ | Campaign-collapse arc: fine / drift / incoherent | C | [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Design Tensions & Failure Modes] |
| 100+ turns | "Assume your game will run 100+ turns" design rule | C | [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Synthesis] |
| ~45% | Hallucination reduction from character-persona constraints | D | [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Technical Approaches to Bounded AI Narration] |
| 7 | Guardrail strategies | C | [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Technical Approaches to Bounded AI Narration] |
| 40% / 28% | PCG diversity gain / compute-overhead reduction (unsourced) | D | [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Supporting Infrastructure] |
| 3–4 | Distinct characters per scene (DreamGen) | C | [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §AI-Driven Interactive Fiction Platforms] |
| "dozens of messages" | Character.AI memory-reset horizon | C | [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Community-Oriented Roleplay Platforms] |
| 75/25 | ChoiceScript revenue split (not relevant to design) | A | [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Non-AI Branching Narrative Tools] |
| 412 / 68% | Survey users / share reporting higher initial immersion with an AI GM | D | [R: research_notes/DM craft TTRPG design AI tools/ai_gm_academic_research.md §Player Experience and Comparative] |
| 4.13 vs 3.35 | Immersive environments, AI vs human | D | [R: research_notes/DM craft TTRPG design AI tools/ai_gm_academic_research.md §Player Experience and Comparative] |
| 4.03 vs 4.2 | Positive experience, AI vs human | D | [R: research_notes/DM craft TTRPG design AI tools/ai_gm_academic_research.md §Player Experience and Comparative] |
| 3.76 vs 4.0 | Narrative flow, AI vs human | D | [R: research_notes/DM craft TTRPG design AI tools/ai_gm_academic_research.md §Player Experience and Comparative] |
| 4.06 vs 4.4 | Player competence, AI vs human | D | [R: research_notes/DM craft TTRPG design AI tools/ai_gm_academic_research.md §Player Experience and Comparative] |
| 8 / 12 users | Static-vs-agentic GM pilot / longer-session comparison | B | [R: research_notes/DM craft TTRPG design AI tools/ai_gm_academic_research.md §Player Experience and Comparative] |
| 36 items, 9 dims, 7-pt; SUS 79.44/100; 6.9 s | VR NPC study: believability questionnaire, usability score, average cycle latency | B | [R: research_notes/DM craft TTRPG design AI tools/ai_gm_academic_research.md §Player Experience and Comparative] |
| 11 (7+4); 3 judges | NARRA-Gym rubric dimensions; judge models per episode | B | [R: research_notes/DM craft TTRPG design AI tools/ai_gm_academic_research.md §Evaluation Methodologies] |
| 23; 10 experts; 78% ≥3.5; 26% >4.5 | SQD taxonomy; Delphi panel size; importance distribution | B | [R: research_notes/DM craft TTRPG design AI tools/ai_gm_academic_research.md §Evaluation Methodologies] |
| 57 / 26 / 13 / 4 % | Kano classes: one-dimensional / must-have / attractive / indifferent | B | [R: research_notes/DM craft TTRPG design AI tools/ai_gm_academic_research.md §Evaluation Methodologies] |
| 1–5 → [0,1] | RPGBench action-quality scale | B | [R: research_notes/DM craft TTRPG design AI tools/ai_gm_academic_research.md §Evaluation Methodologies] |
| 12-dim | RuleSmith rule space | B | [R: research_notes/DM craft TTRPG design AI tools/ai_gm_academic_research.md §Multi-Agent Approaches] |
| 50+ sessions | Scale at which no system has been AI-GM-tested | C | [R: research_notes/DM craft TTRPG design AI tools/major_system_design_lessons.md §AI-GM Runability] |

## 3.5 Game-design numbers (real systems)

| Number | Meaning | Grade | Cite |
|---|---|---|---|
| ±10 | PF2e crit thresholds (≥DC+10 / ≤DC−10); natural 20/1 shift one degree | A | [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §How does Pathfinder 2e's four-degree system work] |
| ×2 | PF2e Strike damage on a critical | A | [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §How does Pathfinder 2e's four-degree system work] |
| 3 + 1 | PF2e actions + reaction per round | A | [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §How do different systems structure what a character can do] |
| 1 / 2 / 3 | PF2e action costs | A | same |
| −5 / −10 (agile −4 / −8) | PF2e multiple-attack penalty on 2nd / 3rd Strike | A | same |
| +1 per level; 4 ranks; 20 levels | PF2e proficiency scaling (Trained, Expert, Master, Legendary) | A | [R: research_notes/DM craft TTRPG design AI tools/major_system_design_lessons.md §Head-to-Head] |
| 3 years (from 2016) | PF2e design cycle | C | [R: research_notes/DM craft TTRPG design AI tools/major_system_design_lessons.md §Pathfinder 2e Design Philosophy] |
| ~+5 → ~+11 | 5e best bonus from level 1 to level 20 (bounded accuracy) | A | [R: research_notes/DM craft TTRPG design AI tools/major_system_design_lessons.md §Head-to-Head] |
| 1 / 1 / 1 | 5e action / bonus action / reaction | A | [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §How do different systems structure what a character can do] |
| −5 / +10 | 5e Sharpshooter / GWM trade | A | [R: research_notes/DM craft TTRPG design AI tools/major_system_design_lessons.md §D&D 5e Balance Problems] |
| ×2 | 2024 5e healing dice (Cure Wounds, Healing Word, mass versions) | A | [R: research_notes/DM craft TTRPG design AI tools/major_system_design_lessons.md §D&D 5e Balance Problems] |
| 1 Std + 1 Move + 1 Minor + 1 Opportunity | 4e per-turn actions; at-will / encounter / daily powers | A | [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §How do different systems structure what a character can do] |
| 1 move + (2 quick or 1 full) | Lancer turn | A | same |
| +8 … −2 | Fate ladder; Tie = equal; Success = 1–2 shifts; Style = 3+ | A | [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §How do OTHER systems implement graduated] |
| 3 / −1 / min 1 | Fate refresh start / per stunt / floor | A | [R: research_notes/DM craft TTRPG design AI tools/cost_systems_and_move_based_abilities.md §How does Fate Core's "stunts" system work] |
| +2 | Fate stunt situational bonus | A | [R: research_notes/DM craft TTRPG design AI tools/cost_systems_and_move_based_abilities.md §How does Fate Core's "stunts" system work] |
| 3 | Fate stunt patterns | A | [R: research_notes/DM craft TTRPG design AI tools/cost_systems_and_move_based_abilities.md §How does Fate Core's "stunts" system work] |
| 3 × 3 = 9 | Blades Position × Effect framings | A | [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §How do OTHER systems implement graduated] |
| 1d6 | Blades resolution die (pool) | A | [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §Research Notes Summary] |
| 2 stress | Blades push cost (+1d / +1 effect / act despite harm) | A | [R: research_notes/DM craft TTRPG design AI tools/cost_systems_and_move_based_abilities.md §How does Blades in the Dark structure its special abilities] |
| 7 vs 10–12 | Blades abilities per playbook vs PbtA moves per playbook | C | [R: research_notes/DM craft TTRPG design AI tools/cost_systems_and_move_based_abilities.md §How does Blades in the Dark structure its special abilities] |
| d10, TN 6 / TN 8 | Classic / new WoD success threshold | A | [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §How do OTHER systems implement graduated] |
| 15 PP/PL; PL 10; PL 14–16 | M&M points per Power Level; default; DC-hero range | A/C | [R: research_notes/DM craft TTRPG design AI tools/cost_systems_and_move_based_abilities.md §How does Mutants & Masterminds' point-buy system work] |
| 5 / 3 / 6 / 15 per die | HERO base 1d6 effect / Dispel / Drain / Killing Attack | A | [R: research_notes/DM craft TTRPG design AI tools/cost_systems_and_move_based_abilities.md §HERO] |
| 1981 | Champions: first point-based creation | A | [R: research_notes/DM craft TTRPG design AI tools/cost_systems_and_move_based_abilities.md §HERO] |
| 1 / 2; max 1 Major + 2 Minor; Edge 2; net 0 | Savage Worlds hindrance points, caps, edge cost, balance | A | [R: research_notes/DM craft TTRPG design AI tools/cost_systems_and_move_based_abilities.md §13th Age and Savage Worlds] |
| 3 points | 13th Age Icon Relationships at creation | A | [R: research_notes/DM craft TTRPG design AI tools/cost_systems_and_move_based_abilities.md §13th Age and Savage Worlds] |
| 3 → ~60 pages | 13th Age Icon Connection rules 1e → 2e | C | [R: research_notes/DM craft TTRPG design AI tools/major_system_design_lessons.md §13th Age Design Mechanics] |
| ~50% | Heinsoo/Tweet "each right about 50% of the time" | C | [R: research_notes/DM craft TTRPG design AI tools/major_system_design_lessons.md §13th Age Design Mechanics] |
| 200 vs 40 points | GURPS generalist beaten by a focused fighter | C | [R: reports/DM craft TTRPG design AI tools.md §Four candidate mechanics] |
| 2–3 | Dungeon World specialties per archetype | C | [R: research_notes/DM craft TTRPG design AI tools/indie_niche_ttrpg_design_theory.md §Dungeon World] |
| 7 | Robin's Laws player types | A | [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Spotlight Balance] |
| 10–15 min | Spotlight rotation interval | C | [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Spotlight Balance] |
| 3–12 | Recommended opponent count (vs solo monsters) | C | [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Challenge Diversification] |
| ×2 HP | Sly Flourish "elite" monster | C | [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Challenge Diversification] |
| 3 days | Example deadline ("Dragon Queen's armies") | C | [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Challenge Diversification] |
| 3 | Pacing levels (session / scene / campaign) | C | [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Core Principles of Good Dungeon Mastering] |
| 10 binary → 1,024 paths | Capacle's branching argument | C | [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §documented tradeoffs] |
| 240 pp / 40 essays / 2012 | Kobold Guide size / essays / Gold ENnie year | A | [R: research_notes/DM craft TTRPG design AI tools/indie_niche_ttrpg_design_theory.md §Kobold Guide] |
| 1999–2005 | Big Model development | A | [R: research_notes/DM craft TTRPG design AI tools/indie_niche_ttrpg_design_theory.md §GNS Theory] |
| 4 | Big Model nested boxes | A | [R: research_notes/DM craft TTRPG design AI tools/indie_niche_ttrpg_design_theory.md §GNS Theory] |

## 3.6 Digest-author computed numbers (not in the sources)

| Number | Meaning | Where |
|---|---|---|
| Project-rule degree distributions at +2 vs DC 10/15/20/25 | e.g. DC 20 → 5/10/45/40%; DC 25 → 5/0/30/65% (crit success / success / failure / crit failure) | 01.A table |
| DC ≥ 23 at +2 | Threshold above which "natural 20 = crit" (project rule) and "natural 20 shifts one degree" (PF2e) diverge | 01.A |
| 95 / 107 / 110 / 127 / 124 / 131 % | Sums of NCP fact + commitment + player-input incidence per model (showing they are not shares) | Register #1 |

---

# 4. Tensions & contradictions

Each entry states both sides and gives a resolution I lean toward. The lean is marked **(digest-author lean)** and is
not binding. Authors must log their own resolution in the Decision Log.

**T-1: A verification layer versus Principle III's "no gate until a failure is observed."**
*Side A:* the sources' largest measured consistency gain is a post-generation verification step: −64.78% critical
hallucinations, zero premature disclosure. NCP-Bench uses a two-stage auditor. The DMR calls reconciliation "a
first-class, expensive-to-build component". [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §Mitigation strategies: quantified evidence] [R: reports/DM craft TTRPG design AI tools.md §What this round changes]
*Side B:* constitution III defaults to base-model judgment with no judge gate, and says to adopt one only once
sustained play records a concrete failure. [C:III]
*Observation:* BRIEF §7 already records two failure types from live probes: narration stating changes no tool
recorded, and embellishing a granted ability (an invented cold vulnerability). P13 records the unearned pronoun. The
revisit trigger asks for *sustained* play, and the probes were short. **(Digest-author lean)** No separate gate is
needed. 12 should write a *claim-by-claim state check* into the DM's own turn procedure as a rule of play. It costs no
new infrastructure, it is a procedure not a model, and it answers the recorded failures. The orchestrator should also
note that III's trigger is arguably close to firing.

**T-2: Consistency versus fidelity to the player's input (goal 2 versus goal 1).**
*Side A:* every mechanism that tightens consistency in the sources costs something on the player side. HiAgent cut
commitment conflicts from 26% to 4% while player-input conflicts rose from 13% to 38%. The model best at facts
(GPT-5.2, 40% fact incidence) has the *highest* player-input incidence (31%). The knowledge tree forced reveals and
lost naturalness. Open Dungeon's engine-owned state "limit[s] creative freedom". The "Rules Enforcement Paradox"
says constraints beyond some point reduce coherence and creativity. [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Mitigation strategies] [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Failure modes] [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §Other 2025–2026 benchmarks] [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Open-Source AI Dungeon Master Projects] [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Design Tensions & Failure Modes]
*Side B:* BRIEF §3 asks for both at once. Player freedom is goal 1 and correct adjudication is goal 2.
**(Digest-author lean)** Treat player-input fidelity as its own checked property, not a by-product. The NCP
player-input rule (acknowledge intent; redirect is fine; never substitute another intent; never silently reset) should
sit next to the state check in 12.D so neither goal is paid for with the other. This is probably the central design
tension the sources expose.

**T-3: BRIEF §3 "player-facing complexity is NOT a constraint" versus documented decision paralysis.**
*Side A:* INDIE and DMR describe decision paralysis as "game-halting". Early choices cascade, and the AI cannot say
"just pick something". [R: research_notes/DM craft TTRPG design AI tools/indie_niche_ttrpg_design_theory.md §Decision Paralysis] [R: reports/DM craft TTRPG design AI tools.md §Indie design theory]
*Side B:* BRIEF §3 forbids using player cognitive load as a design argument. [BRIEF §3]
**(Digest-author lean)** These don't actually conflict if paralysis is treated as a *goal-1 harm about sequencing and
defaults*, not a reason to cut rules. The BG3 dual path keeps every rule and adds a fast path. The BRIEF should
explicitly allow "presentation sequencing and defaults" arguments while still forbidding rule cuts. See the report.

**T-4: The project's natural-20/1 rule versus PF2e's one-degree shift.**
*Side A:* BRIEF §7 makes a natural 20 a critical success and a natural 1 a critical failure, always. [BRIEF §7]
*Side B:* PF2e shifts by one degree. [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §How does Pathfinder 2e's four-degree system work]
*Consequence (01.A arithmetic):* the rules differ only for DC ≥ 23 at +2 (and trivially low DCs). At the ladder's DC 25,
the project rule gives a 5% critical and 65% critical failure. The auto-crit also sits badly with using a DC 25 to mean
"barely possible". 01 decides. Both are internally consistent.

**T-5: Adjusting mid-combat versus "no fudging / keep state true."**
*Side A:* Sly Flourish recommends adding or removing monsters and adjusting HP or damage during play based on how the
fight is going. [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Challenge Diversification]
*Side B:* fudging dice, changing DCs in the monsters' favor and always-countering monsters are named mistakes. Goal 2
requires state to stay true. Silently changing tool-owned HP would be a "Forcibly Changing Reality"-class inconsistency.
[R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Common Dungeon Master Mistakes] [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Failure modes]
**(Digest-author lean)** Allow adjustment only through *diegetic, logged, pre-declared mechanisms*: reinforcement
clocks, morale breaks, retreat thresholds, environmental events. These are rules that fire from state, never hidden
stat edits after stats have been established.

**T-6: "Yes, and" versus Principle VII's default-deny.**
*Side A:* improv craft says to default to yes and to use no only for what breaks the world or the rules. [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Core Principles of Good Dungeon Mastering]
*Side B:* VII allows only basic actions by default and requires a license for anything else. [C:VII]
**(Digest-author lean)** They work at different layers. "Yes, and" applies to *fictional premises and
approaches*. VII applies to *capabilities*. An unlicensed capability is exactly the "breaks the rules" case where
"no" is sanctioned, and "Yes, but" (reframe to the nearest basic action) is VII's required redirect. 01 should say this
explicitly so the AI doesn't feel it is choosing between two contradictory instructions.

**T-7: GNS "focus on one agenda" versus this project's three agendas.**
*Side A:* Edwards claims enjoyable RPGs focus on one of gamism, narrativism and simulationism, and that trying to serve
all three is "a common mistake". [R: research_notes/DM craft TTRPG design AI tools/indie_niche_ttrpg_design_theory.md §GNS Theory] [R: reports/DM craft TTRPG design AI tools.md §Indie design theory]
*Side B:* The Game combines a simulationist living world (11, P3), emergent narrative identity (P5 recognition) and
gamist challenge (06, 09). Nothing in the constitution names a primary agenda.
*Note:* GNS is contested and was superseded by the Big Model. Sources use it only as a "forcing question". **(Digest-author lean)** The
architecture chapter should still state a *priority order* for when agendas conflict (e.g. world consistency first,
then player agency, then challenge tuning), so the AI has a tie-breaker.

**T-8: "Zero-judgment" deterministic degrees versus the pre-roll framing that telegraphing needs.**
*Side A:* PF2e's margin rule is praised because it needs no judgment. [R: reports/DM craft TTRPG design AI tools.md §Four candidate mechanics]
*Side B:* telegraphed lethality (BRIEF §4) and effect scaling need a pre-roll frame (Blades Position/Effect). Setting
that frame is judgment, and the DMR says Blades and Genesys "require the GM to pre-set framing variables the AI would
need to generate itself". [R: research_notes/DM craft TTRPG design AI tools/resolution_mechanics_and_action_economy.md §How do OTHER systems implement graduated] [R: reports/DM craft TTRPG design AI tools.md §Four candidate mechanics]
**(Digest-author lean)** Keep degree computation `[D]` and make framing `[J]` with a table of criteria and worked
examples. Record the frame in state *before* the roll so it can't drift afterward.

**T-9: An observable key_delta versus P5's values-expressive evidence.**
*Side A:* NCP requires state changes that can be observed, not mental-only ones, so they can be audited. [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Methodology for constructing test scenarios]
*Side B:* P5 counts values-expressive choices with no dice resolution. [C:P5]
**(Digest-author lean)** Record the *act* that expressed the value (words said, mercy shown, oath kept publicly), not an
inferred inner state. Both constraints are then satisfied.

**T-10: The DMR on moves ("flavor only") versus the revised P10.**
*Side A:* the DMR puts move and verb design in flavor abilities, as "not a substitute for a full build-diversity
engine". [R: reports/DM craft TTRPG design AI tools.md §Updated primitive list]
*Side B:* the sixth-pass P10 allows moves for core power when the trigger→outcome mapping is deterministic. [C:P10]
The constitution is newer and binding, and the DMR predates it. The DMR's own evidence (Blades' clarity, Fate's
template guardrails) supports P10's criterion, which is determinism of the trigger, not format.

**T-11: Offering action options versus "no menu walls."**
*Side A:* RPGBench's engine offers three candidate next actions each round, scored for diversity and relevance. P16
requires an actionable next step. [R: research_notes/Long horizon LLM narrative benchmarks/rpgbench.md §overall evaluation methodology] [C:P16]
*Side B:* goal 1 says there are no "the menu doesn't have that" walls. [BRIEF §3]
**(Digest-author lean)** Offer leads as *examples* ("you could…, or anything else you have in mind"), never as the
closed option set. Suggestions can be varied deliberately using the challenge-rotation ledger.

**T-12: The "Rules Enforcement Paradox" versus P3's "maximize the substrate."**
*Side A:* "Increasing prompt complexity and constraint specificity beyond a certain point reduces narrative coherence
and creativity." [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Design Tensions & Failure Modes]
*Side B:* P3 (sixth pass) says to maximize background-resolved richness as material for improvisation. [C:P3]
**(Digest-author lean)** These are compatible if the substrate is *retrieved by situation* (layered and tag-keyed
injection, 00.A and 00.D) rather than kept in context all the time. The substrate can be huge while the *active*
constraint set per turn stays small. That makes separable, injectable chapter sections a design requirement.

**T-13: "Broad classes make bad playbooks" versus P5 specialists keyed to broad tags.**
*Side A:* Dungeon World failed as a PbtA game partly because "D&D classes are generally too broad to make effective
playbooks". [R: research_notes/DM craft TTRPG design AI tools/indie_niche_ttrpg_design_theory.md §Dungeon World]
*Side B:* P5 lets a specialist class be keyed to a broad tag such as general spellcasting. [C:P5]
**(Digest-author lean)** Broad-tag callings may exist, but 04 should give them *narrower thematic anchors*
(identity, oath, signature technique). Otherwise they become the generic "a bit of everything" identity that P4 says
must start weaker per area.

**T-14: "Latest visible state wins" (NCP auditor) versus "tool state wins."**
*Side A:* NCP's auditor gives precedence to the most recently established system state when old facts and new
narration collide. [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §What exactly is "Narrative Commitment Preservation" (NCP)]
*Side B:* this project's architecture makes the external store authoritative, and narration must match it. [BRIEF §7] [C:P13]
**(Digest-author lean)** Tool state wins over any narration. "Latest wins" applies only *among state writes* (the most
recent recorded write supersedes older ones), never between prose and state.

**T-15: Multiplayer-derived balance and spotlight craft versus single-player v1.**
*Side A:* nearly all DM-craft evidence here is about groups: rotating the spotlight every 10–15 minutes among players,
PF2e's "no one carries the fight", skill challenges needing several players, 3–12 opponents. [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Spotlight Balance] [R: research_notes/DM craft TTRPG design AI tools/major_system_design_lessons.md §Pathfinder 2e Design Philosophy] [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Challenge Diversification]
*Side B:* Principle IV sets v1 as single-player. [C:IV]
**(Digest-author lean)** Every group-scale number needs a solo reinterpretation. Spotlight becomes rotation across the
PC's facets, pillars and challenge types. "Carry the fight" becomes "the PC must be able to carry scenes". Opponent
counts need a solo curve. No source validates any solo numbers (→ G-4, G-5, G-17).

**T-16: Retirement (Principle VI) versus the psychology of loss.**
*Side A:* VI makes retiring and consolidating aging content mandatory. [C:VI]
*Side B:* players "dislike losing things they spent points on". 13th Age's designer rejected forced repurchases and
kept backward compatibility. [R: research_notes/DM craft TTRPG design AI tools/indie_niche_ttrpg_design_theory.md §Indie Communities and Common Character Customization Mistakes] [R: research_notes/DM craft TTRPG design AI tools/major_system_design_lessons.md §13th Age Design Mechanics]
The constitution already budgets for this cost (WoW rework evidence; provisional-by-default status). The sources add
that *transformation* (branching stunt families, fork-into-replacement) is felt as growth rather than loss. That argues
for VI retirements being written as *transformations* of what the player had. [R: research_notes/DM craft TTRPG design AI tools/cost_systems_and_move_based_abilities.md §How does Fate Core's "stunts" system work]

**T-17: Does summarization help or hurt?**
*Side A:* MERIT puts LLM-summarization memory in the stable 0.70–1.00 band on updated facts, alongside update-on-write
stores. [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §Other 2025–2026 benchmarks]
*Side B:* Morph ("summarization drift"), BOOKMARKS (summarization "discards details"), SSGM ("semantic drift") and
HiAgent (player-input conflicts nearly tripled) all show harm. Memora finds memory agents give only "marginal
improvements" over having no memory, while MERIT finds that the choice of implementation swings success by up to 60
points. [R: research_notes/Long horizon LLM narrative benchmarks/other_benchmarks_and_mitigations.md §Mitigation strategies: quantified evidence] [R: research_notes/Long horizon LLM narrative benchmarks/ncp_bench.md §Mitigation strategies]
**(Digest-author lean)** Summaries may *help recall of settled facts*. They *hurt recent, fine-grained fidelity* and
compound when stacked. Rule: never let a summary be the source of truth for state, and never summarize a summary.

**T-18: Principle I ("no separate engine") versus the sources' engine-owned state.**
*Side A:* constitution I says the AI *is* the mechanical engine and there is no separate deterministic engine outside
its control. [C:I]
*Side B:* the sources' strongest integrity results come from engine authority. Open Dungeon; the SRD Rules Engine
("rules engine is law"); "would need to add a rules-engine agent" to run complex rules; RPGBench's interpreter as
ground truth. [R: research_notes/DM craft TTRPG design AI tools/ai_rpg_tools_landscape.md §Supporting Infrastructure] [R: research_notes/DM craft TTRPG design AI tools/major_system_design_lessons.md §AI-GM Runability] [R: research_notes/Long horizon LLM narrative benchmarks/rpgbench.md §state representation format]
P13 already reconciles the two: the AI drives the process by *calling* deterministic tools. BRIEF §5 leaves the runtime
open. Authors should label every `[D]` rule as "the tool computes", which the sources support, without saying "a
separate engine decides", which I forbids.

**T-19: "Bounded accuracy is more AI-friendly" versus Principle II's "exploit AI capacity."**
*Side A:* an untested inference that small constant bonuses are easier for LLMs to track than layered tiers. [R: research_notes/DM craft TTRPG design AI tools/major_system_design_lessons.md §AI-GM Runability]
*Side B:* II says to design *for* complexity an AI can handle. PF2e-style layering (degrees, action costs) is the
adopted direction (P8, P9). [C:II] [C:P8] [C:P9]
**(Digest-author lean)** Once arithmetic is tool-owned, the LLM tracking burden argument largely goes away. Keep
bounded *DC ranges* for readable probabilities, and let tiered modifiers be computed by tools.

**T-20: Locus of control versus adaptive difficulty.**
*Side A:* players resisted dynamic balancing that reduced meaningful choice or made achievement feel "less earned". [R: research_notes/DM craft TTRPG design AI tools/ai_gm_academic_research.md §Fairness in Adjudicating Novel]
*Side B:* craft literature has the GM adjust difficulty to the party ("give them a dose of pain … give them a break").
[R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Challenge Diversification]
**(Digest-author lean)** Adapt *which kinds* of challenges appear (the challenge-rotation ledger) and *when* respite
comes. Never adapt the *numbers of a challenge already in play*. Consistent with T-5.

**T-21: "Passives must be weak" versus P5 passives and inherently passive archetypes.**
*Side A:* 13th Age says always-on abilities are forced to be weak, so power should sit in conditional triggers. [R: reports/DM craft TTRPG design AI tools.md §Updated primitive list]
*Side B:* P5 explicitly allows passive grants. The DMR itself warns that turtling and buffing archetypes are inherently
passive and "will feel underpowered … unless specifically exempted". [C:P5] [R: reports/DM craft TTRPG design AI tools.md §Updated primitive list]
**(Digest-author lean)** Budget passives lower by rule. Give inherently passive callings conditional *spikes* (a
reaction or an "when X happens" trigger) so their identity has active moments.

**T-22: Template-guided generative authorship versus Principle V's closed, fixed-size pools.**
*Side A:* the DMR praises Fate's templates because "players or a generative system can then author new abilities within
those templates". [R: reports/DM craft TTRPG design AI tools.md §Four candidate mechanics]
*Side B:* V requires fixed slots filled from *fixed-size* option pools, never an open ever-growing menu. [C:V]
**(Digest-author lean)** Use templates as the *authoring grammar for the fixed pools* (designers write every pool entry
through them). Don't let the runtime invent new entries at play time. If runtime generation is ever allowed, it must
be bounded by pool-gate and fill (P5) and validated (M-49).

**T-23: How strong is "fact failures are driven by turn count"?**
*Side A:* the LHR infers that fact-tracking failure is "driven mostly by accumulated turn count itself", because fact
incidence barely moved between adversarial and natural play (60% vs 56%). [R: reports/Long horizon LLM narrative benchmarks.md §Degradation is fast]
*Side B:* these are incidence rates among episodes, and natural episodes ran about twice as long, so per-turn fact error
rates actually *fell* under cooperative play. The data don't cleanly separate turn count from pressure. (Digest-author
note.) The design consequence (external state regardless) doesn't change.

**T-24: Being open about limits versus the hidden-mechanics tone.**
*Side A:* being open about what the GM can and can't support is not railroading, and players accept AI when control
is visible. [R: research_notes/DM craft TTRPG design AI tools/dm_craft_and_spotlight.md §Common Dungeon Master Mistakes] [R: research_notes/DM craft TTRPG design AI tools/ai_gm_academic_research.md §Fairness in Adjudicating Novel]
*Side B:* BRIEF §4 locks in a classic-fantasy tone with no in-world "System". [BRIEF §4]
**(Digest-author lean)** Openness belongs in the *out-of-fiction* codex (P7) and in brief out-of-fiction DM asides. It
never goes into in-world voice. The BRIEF already puts the codex out of fiction.

---

# 5. Gaps: questions a complete ruleset needs answered that these sources do NOT answer

These are listed so the orchestrator can commission research. Each gap has a suggested search target in *italics*.
These are pointers, not findings.

- **G-1 Death, dying, injury and conditions.** There are no mechanics in the sources for the dying state, last-chance
  choices, wound or injury tables, condition taxonomies, recovery and rest rates, or how lethality is telegraphed
  mechanically. Only "long rests trivialize" and Blades' act-despite-harm appear. *Targets: PF2e dying/wounded values;
  Blades harm levels and recovery clocks; Mothership/Into the Odd critical damage; Dungeon World's Last Breath;
  Warhammer Fantasy critical wounds; the One Ring's Wounded/Weary.*
- **G-2 Fairness in novel-action adjudication, and precedence between rules.** Confirmed empty in the literature
  twice. Nothing covers letter versus spirit, or specific versus general precedence. *Targets: "rulings not rules"
  (OSR Primer); Magic: the Gathering's Comprehensive Rules precedence ("specific beats general"); PF2e's "ambiguous
  rules" guidance.*
- **G-3 Error correction and retcons.** Errors are expected within about 20–30 turns. The sources have no procedure
  for correcting a DM error that the player has already seen (in-fiction reconciliation versus an out-of-fiction
  retcon, or rollback, which NarrativeEngine versions support). *Targets: solo RPG etiquette; Ironsworn "truths";
  VTT undo practices; NarrativeEngine rollback docs.*
- **G-4 Measuring single-player spotlight.** No metric, cadence or proportions exist for rotating facets, pillars or
  challenge types in solo play. The only number (10–15 minutes) is multiplayer and real-time. *Targets: solo-RPG
  design (Ironsworn, Thousand Year Old Vampire); CRPG pacing research (encounter-type ratios in BG3/Pathfinder CRPGs).*
- **G-5 Action economy for one PC, and companions.** How does a single PC with a fixed action pool fare against groups?
  How do companions, hirelings, summons and animal allies act without free extra turns? *Targets: PF2e minion and
  Command rules; Pathfinder Kingmaker/WotR CRPG companion handling; solo 5e ("solo adventurer" variant rules);
  Four Against Darkness; Lancer NPC templates.*
- **G-6 Investigation structure.** There is no clue-redundancy rule or mystery-node design. *Targets: the Alexandrian's
  Three Clue Rule and node-based scenario design; GUMSHOE core clues.*
- **G-7 Social influence and conflict.** No social-resolution mechanic appears. *Targets: PF2e Influence subsystem;
  Burning Wheel Duel of Wits; Blades social/faction status; Dungeon World Parley; Fate social conflict.*
- **G-8 Sizing and recovery for the Focus pool.** There is no evidence on shared versus per-class resource pools, pool
  sizes or recovery rates. *Targets: DOS2 AP economy; 5e spell-point variant; Fate refresh; Blades stress; PF2e Focus
  Points (a close namesake: 1–3 points, Refocus for 10 minutes).*
- **G-9 Progress clocks and faction turns.** The sources say "ticking clock" but never describe the mechanics.
  *Targets: Blades progress clocks (4/6/8 segments) and faction game; Stars/Worlds Without Number faction turns; Apocalypse
  World fronts and countdown clocks; Dungeon World fronts and grim portents.*
- **G-10 Content for the tag vocabulary.** None here. *Targets: PoE tag lists; Blades action list; skill taxonomies
  (PF2e 16 skills, GURPS categories); Wildermyth.*
- **G-11 Solo-play oracle and GM-emulator tools.** These are entirely absent, although they may be the most relevant
  precedent for a single-player AI-run game. *Targets: Mythic GM Emulator (chaos factor, fate chart, random events);
  Ironsworn/Starforged moves and oracles; UNE; CRGE.*
- **G-12 Advantage-type mechanics and modifier stacking.** There's no probability analysis or AI-adjudication data for
  advantage/disadvantage, boosts, circumstance bonuses or stacking caps, and no ability-score-count precedent.
  *Targets: 5e advantage math (≈ +3.3 to +5 equivalent); PF2e bonus types (circumstance/status/item; only the highest of
  each applies); Genesys boost/setback.*
- **G-13 Zones and range bands.** Theater of the mind and 13th Age's gridless combat are named, but no zone model is
  described. *Targets: 13th Age engaged/nearby/far away; Fate zones; Genesys range bands; Blades distance.*
- **G-14 Morale, surrender, escape and chases.** *Targets: B/X morale (2d6 vs morale score); Worlds Without Number
  morale; Blades/Genesys chase rules; Dungeon World Defy Danger.*
- **G-15 Pacing numbers.** There are no thresholds for scene length, challenge-type proportions, "steamrolling"
  detection or when to schedule a respite, and no operationalized campaign pacing. *Targets: the Alexandrian on
  pacing and scene framing; Sly Flourish Lazy DM prep (strong start, scenes); CRPG encounter-density studies.*
- **G-16 Economy, crafting and rarity.** *Targets: PF2e treasure-by-level tables; Blades coin and stash; Worlds Without
  Number economy; Kingdom Come/Valheim crafting; the fifth-pass report (outside my scope) for pool-gate and fill.*
- **G-17 Threat bands without levels, and solo encounter budgets.** Only M&M's Power Level appears. *Targets: PF2e
  encounter XP budget (a solo adaptation); 13th Age monster tiers; Blades tier; Ironsworn challenge ranks (troublesome →
  epic, progress per success) — likely the closest levelless precedent.*
- **G-18 Retirement and legacy.** None. *Targets: Blades retirement; Pendragon family and generational play; Ars Magica
  covenants; Ironsworn legacy tracks; Microscope.*
- **G-19 In-world time model.** Temporal errors are an empirically dominant failure, yet the sources give no calendar,
  watch or turn structure. *Targets: B/X exploration turns (10 minutes) and watches; Worlds Without Number calendar;
  Blades downtime cadence.*
- **G-20 Travel and hexcrawl procedure.** *Targets: The One Ring journey rules; Forbidden Lands; Worlds Without Number
  hexcrawl; the Alexandrian's hexcrawl series.*
- **G-21 Consistency of the current runtime.** No benchmark matches real tool-calling against narrative-embedded JSON
  against pure prose, and no data exists for Gemini flash-tier with tool calls on long horizons. The nearest data point
  is RPGBench's Gemini 2.0 Flash Exp MEC of 0.765 at 10 rounds with embedded JSON. *Target: the project's own Feature
  002 stress test.*
- **G-22 Safety tools and an autonomous session zero for solo AI play.** Only hard and soft limits are covered. The
  sources flag AI-run session zero as unstudied. *Targets: TTRPG Safety Toolkit (lines and veils, X-card, open door);
  solo-play safety practice.*
- **G-23 Surprise versus coherence.** It's unknown whether maximizing surprise costs coherence, and no guidance exists
  on staying surprising while consistent. *Targets: NARRA-Gym follow-ups; "Chekhov's gun" and reincorporation
  literature; Mythic random events.*
- **G-24 Hidden rolls and secret information.** There's no guidance on which rolls the player sees versus secret DM
  rolls (perception, lies, traps), which bears on locus of control. *Targets: PF2e secret checks; Blades "the GM never
  rolls"; GUMSHOE.*
- **G-25 A canonical list of classic-fantasy archetypes for coverage audits.** The sources set the requirement
  (Iron Kingdoms, Mage/necromancer) but supply no list. *Targets: the D&D/PF class lists plus prestige classes; the
  Dragon Age/Elder Scrolls class catalogues; TV Tropes fantasy character archetypes.*

---

# 6. Top 15 implications (ranked)

These are ranked by how much they affect the two design goals: (1) the player feels free to try creative ideas, and
(2) the AI responds correctly. Player-facing complexity is not treated as a cost here.

1. **Every piece of state that can change must be a typed, tool-owned `[D]` field written at the moment it changes.
   Narration may only restate what a tool returned in the same turn.** This covers Vitality, Focus, inventory counts,
   currency, positions, lock/alive/present/introduced flags, NPC knowledge, clocks, tallies and recharges. Fact
   contradictions are the dominant failure in every benchmark (NCP incidence 40–68%). Facts that change are the most
   fragile (embedding retrieval 0.30–0.95 vs structured stores 0.70–1.00). Models use a correctly retrieved fact
   correctly only 55% of the time. Enforced structure still drifts (RPGBench MEC 0.55–0.77, falling with length), so
   *the tool must do the arithmetic too*. 00 should define the state-type vocabulary: location, object_state,
   status_flag, entity_existence, quantity, knowledge, relationship, time. Every chapter's "State touched" section
   must map onto it.

2. **Write a claim-by-claim verification step into the DM turn loop as a rule of play, and pair it with an explicit
   error-correction procedure.** Before narration is final, list the state claims it makes and check each against tool
   state. Also check player-input fidelity: intent acknowledged, never substituted, never silently reset. This is the
   largest measured win in the sources (−64.78% critical hallucinations; NCP-style two-stage audit). The model's
   self-report is unreliable (P13). Since errors are expected within roughly 20–30 turns even for the best model (42%
   survival@20), 12 must also say how an error the player has already seen is corrected: tool state wins, with an
   in-fiction reconciliation or a short out-of-fiction note, and a log entry. This also bears on constitution III's
   revisit trigger.

3. **Treat consistency and player-input fidelity as separate properties, because the research shows they trade
   against each other.** HiAgent cut commitment conflicts from 26% to 4% while player-input conflicts rose from 13% to
   38%. The best fact-tracker (GPT-5.2) had the highest player-input conflict rate (31%). Rules that tighten goal 2 must
   come with an explicit goal-1 safeguard. The prime example is the NCP player-input rule: denial or redirection is
   fine only when the player's intent is acknowledged and followed through concretely.

4. **Make every Principle VII capability decline an acknowledged redirect, and use NCP's high-sensitivity list as the
   default license checklist.** Upgrades to perception, memory, mobility, control, access, awareness or freedom need an
   explicit license. Every decline must name the missing license and offer the nearest possible action ("Yes, but").
   Player acceptance of AI rulings depends on perceived locus of control, not correctness. No research covers fairness
   in adjudicating novel actions, so 01's gate procedure is original work. It needs dense two-sided worked examples and a
   stated precedence rule for when a letter-of-the-rule reading and a spirit-of-the-rule reading conflict.

5. **Keep degree computation deterministic (PF2e margin), frame risk before the roll, and choose the natural-20 rule
   deliberately.** Degrees are `[D]`. The pre-roll frame (Blades-style Position/Effect or equivalent) is `[J]` with
   criteria, recorded to state before the roll, and it is the mechanism that telegraphs lethal risk. Use a Fate-style
   tie band or a Genesys-style side-effect axis for "success at a cost" (anti-stall, P16). Recheck the ladder: at the
   default +2, DC 20 critically fails 40% of the time and DC 25 65% of the time, and "natural 20 = auto-crit" differs
   from PF2e's shift exactly at the "barely possible" DCs.

6. **Build every ability, tier grant and item power from a closed template grammar with mandatory narrow triggers,
   frequency caps and Focus costs.** This is Fate's three patterns (new action / narrow +2-type bonus / single rule
   exception) plus stunt-family branching. Pay for unlimited or conflict-affecting effects with Focus. Budget passives
   lower than active or conditional effects (13th Age Ranger). State literally what each ability does and does not do,
   to prevent embellishment. No published game trusts open-framework abilities. Templates serve as the authoring
   grammar for the fixed pools (Principle V), not as a runtime generator.

7. **Use a fixed action pool with variable costs and escalating repeat penalties, and design the solo economy
   explicitly.** Adopt PF2e's 3 actions + 1 reaction, costs of 1–3, movement from the same pool, and a MAP-style
   escalation (−5/−10) as the general rule for compound or repeated attempts. Adopt Lancer's asymmetric, smaller NPC
   action sets. Companions and summons act only from the PC's pool. Party-scale guidance ("3–12 opponents",
   "multiplicative bodies") would be lethal against a single PC, so 06 and 09 need a solo body-count curve (mobs or
   swarms as single entities).

8. **Challenge the player through the kind of problem, not stat inflation, and run it as an explicit rotation
   ledger.** The six levers are terrain, intelligent tactics, outnumbering, objectives, time pressure and encounter
   mixing. Track which challenge types and which of the PC's facets and pillars have recently been foregrounded, and
   rotate across the arc rather than per session. Keep the per-tag "last exercised" data in 03 so the ledger comes for
   free. This is the DMR's headline finding: spotlight and diversification never fall out of good mechanics.

9. **Never make hidden adjustments. All difficulty and pacing adaptation must be diegetic and logged.** Mid-fight
   changes happen only through pre-declared, state-fired mechanisms such as reinforcement clocks, morale breaks,
   retreats and environmental events. Adaptation changes *which* challenges and respites come next, never the numbers
   of a challenge already in play. This reconciles Sly Flourish-style dynamic adjustment with "no fudging", goal 2 and
   locus of control.

10. **Model the living world as typed commitments and trajectories, and give every hook a lifecycle.** Faction agendas
    and clocks become ordered atomic steps (trigger → observable change) plus invariant, ordering and achievement
    commitments with machine-checkable satisfaction and violation conditions. Foiling them is a recorded outcome.
    Secrets are stored as positive-ignorance facts (T=0 isolation), so the DM cannot leak what the world doesn't know
    yet. Every hook and rumor moves through seeded → active → resolved/expired/retired, which prevents the
    dominant-category "abandoned plot element" error and applies Principle VI to world content. Improvised facts are
    written immediately and reused preferentially.

11. **Record evidence (`tag_event`) with NCP's fact-update discipline.** Record only completed, atomic, observable acts,
    each with a one-line justification. Split compound actions into separate events. Give no credit across skipped
    prerequisites. Record values-expressive choices as the observable act that expressed them. Supersede evidence only
    through explicit logged events. All tallies and recency data are `[D]` counters. Base-model judgment decides
    *significance* (P5), applied to a neutral restatement of the deed to limit framing drift.

12. **Gate information by explicit knowledge state, and let degree of success choose how much of the permitted
    information is revealed.** Clues and NPC knowledge form a graph with per-node reveal conditions (the knowledge-tree
    precedent: zero premature disclosures). P17's graduated reveal selects among *permitted* nodes, never beyond them.
    Descriptions respect the PC's point of view. NPC knowledge is updated whenever information passes to them. 10 still
    needs a clue-redundancy rule, which is a gap.

13. **Hold balance in a single ledger and audit it continuously against archetype coverage and ability-tax tests.**
    Fixing one side of an asymmetry is the documented failure (5e 2024). Every calling needs utility and new licenses as
    it grows, not only damage, or martial callings repeat 5e's disparity. No option may be a tax. The origin → emergence
    path must reach every iconic classic-fantasy archetype from session one (the Iron Kingdoms / Mage necromancer
    failure). Thresholds must stay reachable ("excessive investment kills viability"). Tune numbers with RuleSmith-style
    self-play simulation and RPGBench-style rule replay, not guesswork.

14. **Give character creation both a fast default path and a full path, and make it output story hooks and player
    preferences.** Decision paralysis is game-halting, and the AI can't say "just pick something". BG3-style dual path.
    Origin plus 2–3 specialties (Dungeon World). A One-Unique-Thing-style distinctive, faction ties (13th Age Icons) and
    bonds become 11's hook seeds. A solo session zero records tone, hard and soft limits, and a Robin's-Laws-style
    preference profile for 12's rotation. Use no point-buy unless it uses HERO brackets or Savage-style zero-sum
    guardrails wholesale.

15. **Design the rules text itself for retrieval and long campaigns.** Keep binding rules cleanly separable from craft
    commentary so a runtime can inject only the relevant mode's rules (layered prompting: rules, then recent events,
    then lore). Key lore and rules retrieval to the same hierarchical tag vocabulary. Never make a summary the source of
    truth, never summarize a summary, and always process the player's latest turn verbatim. Build the starter region as
    a validated data skeleton (NCP pipeline plus BFS reachability) from which prose is derived. The sandbox is exactly
    the long-horizon setting where practitioner reports say campaigns collapse after about 10–50 sessions, and a vague
    rule grows under pressure (13th Age's 3 → 60 pages).
