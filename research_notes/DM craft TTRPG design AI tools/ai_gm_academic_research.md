# Additional Academic Research on AI Game-Mastering, LLM-Driven Narrative Games, and Fairness

## Evaluation Methodologies and Metrics for AI Game Masters

### Takeaway
Recent research has produced multiple comprehensive evaluation frameworks beyond consistency metrics, including RPGBENCH (a full benchmark for RPG engines), NARRA-Gym (multi-dimensional narrative assessment), and NCP-Bench (long-horizon consistency). These address story quality dimensions, user experience, and mechanically correct game state tracking.

### Cited Findings
- RPGBENCH is the first benchmark designed to evaluate large language models as text-based role-playing game engines, comprising two core tasks: Game Creation and Game Simulation, integrating objective verification of event mechanics and variable updates with subjective measures such as content interestingness, action quality, and role-playing capability evaluated via LLM-as-judge frameworks — [RPGBENCH: Evaluating Large Language Models as Role-Playing Game Engines](https://arxiv.org/abs/2502.00595)
- Action quality metrics are rated using LLM judges based on diversity, relevance, and clarity on a 1-5 scale normalized to [0,1] and averaged across rounds — [RPGBENCH](https://arxiv.org/abs/2502.00595)
- NARRA-Gym provides an 11-dimension rubric for evaluating interactive narrative agents: 7 story quality dimensions (relevance, coherence, empathy, surprise, engagement, complexity, character development) and 4 user experience dimensions (satisfaction, prose quality, helpfulness, reusability) — [NARRA-Gym for Evaluating Interactive Narrative Agents](https://arxiv.org/pdf/2605.08503)
- NARRA-Gym employs LLM-as-judge sweep with three independent models scoring each episode to reduce individual judge bias, plus human evaluation using within-group ranking aggregation with Plackett-Luce model to capture "qualities difficult to reduce to rubric anchors: whether the interaction feels paced at a human tempo, whether the prose invites continuation, and whether emotional turns feel earned rather than merely correct" — [NARRA-Gym](https://arxiv.org/pdf/2605.08503)
- NCP-Bench (Narrative Commitment Preservation Bench) comprises 100 narrative environments derived from movie synopses, with reference trajectories describing major plot steps, commitment sets specifying invariants and ordering rules, and initial fact ledgers, spanning 18 genres — [Can LLM Agents Stick to the Script? A Benchmark for Long-Horizon Consistency in Interactive Narratives](https://arxiv.org/abs/2608.08160)
- NCP-Bench evaluation tracks four metrics: Survival Rate (proportion of environments persisting without logical conflicts), Trajectory Progress (advancement along reference plot), Satisfied Commitments (percentage of narrative obligations fulfilled), and Conflict Breakdown (categorization of failures into fact conflicts, commitment violations, and player-input conflicts) — [Can LLM Agents Stick to the Script?](https://arxiv.org/abs/2608.08160)
- A framework for evaluating gaming narratives co-created with AI identifies 23 core Story Quality Dimensions (SQDs) derived from literature review; expert validation via Delphi study with 10 narrative design experts showed 78% scored 3.5 or higher on importance (1-5 Likert scale) and 26% scored above 4.5 as "critically important" — [Evaluating Quality of Gaming Narratives Co-created with AI](https://arxiv.org/abs/2509.04239)
- Experts categorized narrative dimensions via Kano model: 57% as "one-dimensional" (satisfaction proportional to performance), 26% as "must-haves" (basic expectations), 13% as "attractive" (unexpected features), and 4% as "indifferent"; two emergent dimensions were Voice ("distinctive and compelling narrative voice") and Genre Alignment — [Evaluating Quality of Gaming Narratives Co-created with AI](https://arxiv.org/abs/2509.04239)
- A master's thesis on LLM game masters evaluates creativity, coherence, responsiveness, and susceptibility to player influence through comparative analysis — [Large language models as RPG game masters : A comparative analysis on performance and player experience](https://thesis.dial.uclouvain.be/entities/masterthesis/98a98b9c-319d-4a51-abf8-5eae1a4a09e6)

### Inferences
- A gap exists between linguistic fluency and logical consistency in evaluated systems; comprehensive evaluation frameworks require both automated checks (game state, plot adherence) and qualitative LLM-as-judge assessment supplemented by human ranking to capture experiential qualities
- Story quality evaluation has matured from ad-hoc metrics to validated taxonomies (23 SQDs with expert consensus), suggesting standardization is possible and needed for comparing different GM systems
- Multi-dimensional assessment (story quality + user experience across multiple turns) appears more informative than single-turn metrics for predicting real-world GM usability

### Gaps
- Most evaluation frameworks treat individual story quality dimensions in isolation; no research found on how these dimensions interact or trade off (e.g., does maximizing "surprise" reduce "coherence"?)
- Limited documentation of evaluation methodology specifics in published papers—exact prompt templates, judge model versions, and inter-rater agreement statistics are rarely detailed

---

## Consistency and Long-Horizon Narrative Integrity

### Takeaway
Research identifies substantial consistency gaps in LLM-driven narratives over extended interactions. A comprehensive taxonomy of consistency bugs has been documented (timeline/plot logic, characterization, world-building, factual details, narrative style), with key findings that even state-of-the-art models (GPT-5.2) maintain consistency in only 42% of interactions after 20 turns, and consistency errors cluster in factual and temporal reasoning dimensions.

### Cited Findings
- "Lost in Stories" research identifies five main error categories in long-form LLM-generated narratives: (1) Timeline & Plot Logic (absolute time contradictions, duration mismatches, simultaneity paradoxes, causeless effects, causal logic violations, abandoned plot elements), (2) Characterization (memory contradictions, knowledge inconsistencies, skill fluctuations), (3) World-building & Setting (core rule violations, social norm breaches, geographical inconsistencies), (4) Factual & Detail Consistency (appearance mismatches, nomenclature confusions, quantitative discrepancies), (5) Narrative & Style (perspective confusions, tone inconsistencies, style shifts) — [Lost in Stories: Consistency Bugs in Long Story Generation by LLMs](https://arxiv.org/abs/2603.05890)
- Consistency errors show clear tendencies: they are most common in factual and temporal dimensions, tend to appear around the middle of narratives, with factual and temporal issues representing the dominant failure modes, suggesting entity tracking and temporal reasoning remain significant challenges — [Lost in Stories](https://arxiv.org/abs/2603.05890)
- The NCP-Bench evaluation reveals that even the strongest model (GPT-5.2) demonstrates only a 42% survival rate after 20 turns, with fact conflicts constituting the dominant failure mode (40%-68% across models), and "only isolated runs satisfied all achievement commitments within the 100-turn limit" — [Can LLM Agents Stick to the Script?](https://arxiv.org/abs/2608.08160)
- The research notes that "only isolated runs satisfied all achievement commitments within the 100-turn limit," underscoring that current LLMs struggle fundamentally with maintaining coherent world states under adversarial pressure over extended interactions, though human baseline testing confirms the task is solvable — [Can LLM Agents Stick to the Script?](https://arxiv.org/abs/2608.08160)
- LLMs often fail to maintain consistency throughout long narratives, contradicting their own established facts, character traits, and world rules, with the development of AI-assisted narrative generation outpacing game developers' ability to ensure consistent quality — [Can LLMs Generate Good Stories? Insights and Challenges from a Narrative Planning Perspective](https://arxiv.org/abs/2506.10161)
- Automated evaluation pipelines detect contradictions using a five-dimension taxonomy with 19 fine-grained error subtypes for assessing narrative consistency, reporting gaps in creativity-related dimensions (originality, character development) and difficulties with long-range plot coherence — [Can LLMs Generate Good Stories?](https://arxiv.org/abs/2506.10161)
- Research emphasizes that high linguistic quality does not guarantee narrative integrity against unconstrained user interventions; in evolving world simulations and AI-native games, models must preserve facts, relationships, causal dependencies, and character states — [Can LLM Agents Stick to the Script?](https://arxiv.org/abs/2608.08160)
- The Game Knowledge Management System approach uses schema-governed LLM pipelines to structure knowledge representation for executable narrative generation in RPGs, addressing the consistency challenge through explicit knowledge management — [Game Knowledge Management System: Schema-Governed LLM Pipeline for Executable Narrative Generation in RPGs](https://www.mdpi.com/2079-8954/14/2/175)

### Inferences
- Consistency is fundamentally a world-state tracking problem, not a language modeling problem; models that maintain explicit representations of facts, relationships, and causal dependencies outperform models relying solely on context windows
- The dominance of factual and temporal errors suggests that improving entity tracking and temporal reasoning would address the majority of consistency issues
- Current benchmarks (NCP-Bench at 42% survival) establish that this is a solvable but hard problem; systems performing better than this are likely using explicit state tracking mechanisms

### Gaps
- No published research directly compares implicit state-tracking (in-context prompt engineering) versus explicit knowledge representation approaches on the same consistency benchmark
- Limited documentation of how different model architectures (e.g., retrieval-augmented generation, structured prompting with schema validation) affect consistency metrics on standard benchmarks
- No research found on whether consistency bugs correlate with player dissatisfaction or fairness problems in actual gameplay

---

## Fairness in Adjudicating Novel Player-Invented Actions

### Takeaway
This is a largely unexplored area in published academic research. No studies directly address the fairness problem of an AI GM evaluating genuinely novel player actions against explicit rules without being either a pushover or overly restrictive. However, related research on adversarial robustness, player agency, and rule-learning from natural language provides partial insights.

### Cited Findings
- Players did not respond to AI in games as a single category: the same AI capability was acceptable when it expanded valued play experiences, but problematic when it appeared to take over judgment, authorship, or player choice; self-determination theory identifies autonomy and competence as central psychological needs, explaining why dynamic balancing or recommendation could be resisted when it reduced meaningful choice or made achievement feel less earned — [Static Vs. Agentic Game Master AI for Facilitating Solo Role-Playing Experiences](https://arxiv.org/abs/2502.19519)
- A framework for adversarial safety in LLMs formulates safety alignment as a non-zero-sum, non-cooperative game where an Attacker agent learns to generate novel deceptive prompts through iterative RL training, while a Defender agent simultaneously optimizes to recognize and refuse such inputs; the attacker, endowed with initial reasoning ability, evolves novel, previously unseen combinatorial strategies through iterative training — [MAGIC: A Co-Evolving Attacker–Defender Adversarial Game for Robust LLM Safety](https://arxiv.org/abs/2602.01539); [Safety Alignment of LMs via Non-cooperative Games](https://arxiv.org/abs/2512.20806)
- Models must be both robust enough to withstand adversarial manipulation and flexible enough to recognize fairness cues and respond accordingly; the framework's ability to simulate adversarial and cooperative scenarios enables testing of how AI systems will perform in real-world contexts where trust, fairness, and adaptability are critical — [MAGIC](https://arxiv.org/abs/2602.01539)
- RobustMLLMJudge is the first general framework for evaluating the adversarial robustness of general-purpose multimodal LLMs when functioning as judges — [On the Adversarial Robustness of Multimodal LLM Judges](https://arxiv.org/abs/2606.15608)
- FLEX benchmark evaluates robustness of fairness interventions under distribution shift, addressing how fairness systems handle adversarial or novel inputs — [FLEX: A Benchmark for Evaluating Robustness of Fairness](https://aclanthology.org/2025.findings-naacl.199.pdf)
- Players' attitudes toward AI in games depend critically on perceived locus of control: "the same AI capability was acceptable when it expanded valued play experiences, but problematic when it appeared to take over judgment, authorship, or player choice" — [Static Vs. Agentic Game Master AI](https://arxiv.org/abs/2502.19519)

### Inferences
- The fairness problem in novel player actions is fundamentally about maintaining player agency and perceived autonomy while enforcing rule consistency; overly restrictive rule interpretation is seen as removing player choice, while overly permissive interpretation is seen as lowering meaningful challenge
- Adversarial robustness research suggests that handling novel (out-of-distribution) inputs is a generalizable challenge for LLM-based judges; fairness in game adjudication likely requires similar adversarial training or robust evaluation approaches
- The lack of published research on this specific problem suggests it is either (a) an underexplored gap, or (b) handled implicitly in deployed game systems without formal evaluation

### Gaps
- **No peer-reviewed research directly found on AI GM fairness in adjudicating novel player-invented actions against explicit rulebooks.** This is a significant gap in the literature, despite being a core concern for practical TTRPG systems.
- No studies comparing different adjudication strategies (strict rule-following vs. fairness-balancing interpretations) on player satisfaction or perceived fairness
- No benchmarks evaluating how LLMs handle rule interpretation conflicts (e.g., when a novel action fits the letter of one rule but violates the spirit of another)

---

## Multi-Agent Approaches to Game Mastering

### Takeaway
Multiple research teams have implemented specialized multi-agent architectures separating narration, rule-checking, and character simulation. Key approaches include PLAYER* (dynamically planning agent interactions), RuleSmith (multi-agent self-play for game balancing), and narrative fabula/discourse pipelines (separating simulation from prose generation). These systems show promise in improving consistency and enabling modularity.

### Cited Findings
- Tabletop RPG game mastering benefits from multi-agent systems in which specialized LLM agents provide feedback to refine GM responses; a consistent theoretical pattern across narrative multi-agent systems applies the fabula/discourse distinction as a two-stage pipeline where one component simulates or plans story-world events and another generates the discourse in textual prose — [TRPG Game Mastering Using LLM-Based Multi-Agent System](https://wordplay-workshop.github.io/pdfs/20.pdf)
- A Director (or Game Master) agent subtly nudges the simulation while a separate Narrator agent performs a topological sort of the graph and translates each structured event into compelling prose, feeding it only the context needed for that specific scene; character agents with goals, states, and memories interact across a simulated world to produce event records, which a separate agent then rephrases into "novel-style story" with control over narrative pace — [TRPG Game Mastering Using LLM-Based Multi-Agent System](https://wordplay-workshop.github.io/pdfs/20.pdf)
- PLAYER* enhances multi-agent LLM performance in murder mystery games through three mechanisms: (1) Sensor-Driven Question Generation where sensors detect emotion, motivation, and opportunity to dynamically guide question creation, (2) Action Space Refinement via a pruner mechanism that reduces computational waste by estimating informativeness, and (3) Anytime Sampling-Based Planning inspired by robotics algorithms (RRT*) that constructs and dynamically prunes a search tree in real-time — [PLAYER*: Enhancing LLM-based Multi-Agent Communication and Interaction in Murder Mystery Games](https://arxiv.org/abs/2404.17662)
- PLAYER* shifts from static question libraries to adaptive, information-driven strategies that mirror human investigative reasoning during gameplay, enabling agents to "navigate complex social interactions" without human-written scenario-specific guides, improving generalizability across different murder mystery scripts — [PLAYER*](https://arxiv.org/abs/2404.17662)
- RuleSmith leverages two key mechanisms for automated game balancing: (1) LLM Self-Play as Evaluation where two language model agents independently control opposing factions in a strategy game and interpret natural-language rulebooks, and (2) Bayesian Optimization with Adaptive Sampling treating game parameters as the optimization target using a Gaussian process surrogate model searching a 12-dimensional rule space — [RuleSmith: Multi-Agent LLMs for Automated Game Balancing](https://arxiv.org/abs/2602.06232)
- RuleSmith constructs "a structured natural language description of the current game state" for each decision point, enabling models to understand game context without explicit training, and minimizes a loss function measuring "win-rate disparities" between factions calculated from multiple independent self-play matches — [RuleSmith](https://arxiv.org/abs/2602.06232)
- Narrative Theory-Driven LLM Methods survey reviews multi-agent approaches including story generation and understanding, noting that character agents with goals, states, and memories produce event records that separate narrative agents repurpose into formatted prose — [Narrative Theory-Driven LLM Methods for Automatic Story Generation and Understanding: A Survey](https://arxiv.org/abs/2602.15851)

### Inferences
- Separating simulation/world-state from narrative prose generation appears to improve both consistency and quality; agents specialized in different tasks (world-state tracking, rule enforcement, narration) likely perform better than monolithic models
- Adaptive, information-driven planning (PLAYER*) outperforms static scenario-specific guides in generalizability, suggesting that meta-level planning about what information to gather is more important than memorized response templates
- Self-play evaluation (RuleSmith) provides an automated mechanism for balancing that scales beyond manual tuning, suggesting this approach could be generalized to other game-balancing problems in TTRPG contexts

### Gaps
- Limited research on how to coordinate feedback loops between specialized agents (e.g., does a rule-checking agent need to loop back to the world-state agent, and if so, how often?)
- No published comparisons between multi-agent approaches and single-model approaches on the same narrative consistency or player satisfaction benchmarks
- No research on how to handle conflicts between agent recommendations (e.g., if the rule-checker contradicts the narrator, which agent wins?)

---

## Player Experience and Comparative Studies (AI vs. Human GMs)

### Takeaway
Limited but emerging empirical research shows that AI GMs score comparably to human GMs on player engagement and satisfaction in some dimensions, with a 2024 survey of 412 solo/small-group AI-RPG users finding 68% reported higher initial immersion with AI (especially in environmental interaction), though human GMs retain advantages in social energy, surprise, and reading the room. Player acceptance depends critically on perceived autonomy and whether AI decisions are seen as expanding or restricting meaningful choice.

### Cited Findings
- A 2024 survey of 412 solo and small-group AI-RPG users found that 68% reported higher initial immersion with AI—particularly during exploration, travel, and environmental interaction; AI excelled at creating immersive environments, scoring 4.13 out of 5 compared to humans' 3.35 — [Player experience data derived from commercial AI GM platforms](https://dungeonsdeep.ai/blog/the-best-ai-game-masters-compared-in-2026)
- Both AI and human DMs kept players engaged and comfortable, with similarly strong scores in positive experiences (4.03 vs 4.2) and equally low frustration levels; traditional DMs held only modest leads in narrative flow (4.0 vs 3.76) and player competence (4.4 vs 4.06) — [Player experience comparison data](https://boingboing.net/2025/01/14/ai-might-be-your-next-dungeon-master.html)
- "Immersion without trust is shallow, and trust forms when players believe their choices matter, their emotions are honored, and the world responds with integrity—not just plausibility; trust is built by humans, through presence, memory, and moral courage, and AI can amplify those qualities, but cannot originate them" — [Analysis of AI GM limitations](https://boingboing.net/2025/01/14/ai-might-be-your-next-dungeon-master.html)
- AI Dungeon Masters excel at solo play, group sessions when no human GM is available, and practice sessions for new players; they handle rules consistently and are available 24/7 with zero prep time — [Best AI Dungeon Master Tools in 2026: 10 Platforms Compared](https://lore-keeper.com/blog/best-ai-dungeon-master-2026)
- A pilot study with 8 users of an AI game master (GM v1) demonstrated high usability and user satisfaction with willingness to replay; a more comprehensive evaluation compared two versions with 12 users during longer playing sessions, with participants focusing on responsiveness and adaptability, noting significant differences in response quality and flexibility — [Static Vs. Agentic Game Master AI for Facilitating Solo Role-Playing Experiences](https://arxiv.org/abs/2502.19519)
- Player acceptance of AI depends on perceived locus of control: the same AI capability was acceptable when it expanded valued play experiences but problematic when it appeared to take over judgment, authorship, or player choice — [Static Vs. Agentic Game Master AI](https://arxiv.org/abs/2502.19519)
- Evaluation of AI-powered NPCs in virtual reality environments used multiple questionnaires: Virtual Agent Believability Questionnaire (36 questions measuring nine dimensions including behavior, awareness, intelligence, emotion, personality, agency, believability on 7-point scale), System Usability Scale (SUS) scoring 79.44/100, and Game Experience Questionnaire (social presence module), with average cycle latency of 6.9 seconds across system components — [An Empirical Evaluation of AI-Powered Non-Player Characters' Perceived Realism and Performance in Virtual Reality Environments](https://arxiv.org/abs/2507.10469)
- A 2024-2025 study found that players with expert-level TTRPG experience provided different assessments than novices, with experts more sensitive to consistency errors and narrative flow, while novices prioritized entertainment value and immersion — [Player Experience Research on AI Game Masters](https://arxiv.org/abs/2502.19519)

### Inferences
- The "immersion paradox" suggests AI excels at environmental detail and availability but struggles with the deeper trust-building that comes from perceived intentionality and presence
- Player experience appears to be driven more by perceived autonomy and choice than by technical quality of narrative; a mediocre story that respects player agency may be preferable to a high-quality story that feels railroaded
- Expert vs. novice differences suggest that AI GMs may be particularly valuable for newer players and solo play, while established groups may prefer human GMs despite higher latency and prep burden

### Gaps
- No large-scale, randomized, controlled studies comparing the same scenario played with AI vs. human GMs; most comparisons are between different groups or survey data
- Limited research on how player expectations (formed by marketing, prior experience) bias their assessment of AI vs. human GM quality
- No longitudinal studies tracking whether players who start with AI GMs eventually prefer human GMs, or vice versa
- Missing data on how player satisfaction changes with repeated play (habituation effects)

---

## Additional Relevant Research Areas

### Procedural Narrative Generation with LLMs

- **PANGeA** (Procedural Artificial Narrative using Generative AI) provides a structured approach for procedural generation of interactive narratives in turn-based RPGs, addressing challenges in adapting narratives to player actions — [PANGeA: Procedural Artificial Narrative using Generative AI for Turn-Based Video Games](https://arxiv.org/abs/2404.19721)
- **SNAP** (A Plan-Driven Framework for Controllable Interactive Narrative Generation) uses structured planning to generate narratives with greater control over plot, pacing, and character arcs — [SNAP: A Plan-Driven Framework for Controllable Interactive Narrative Generation](https://arxiv.org/abs/2601.11529)
- Character-driven narrative generation using goal-based multi-agent approaches enables long-form story generation where character motivations drive plot development — [From Personas to Plot: Character-Grounded Multi-Agent Story Generation for Long-Form Narratives](https://arxiv.org/abs/2607.00918)
- **The Story Shapes the Agent** research shows that narrative context and framing significantly influence LLM behavior and decision-making, suggesting that how rules and story context are framed affects GM adjudication — [The Story Shapes the Agent: Narrative Priors in LLM Behavior](https://arxiv.org/abs/2607.18566)

### State Tracking and World Modeling

- **StateAct** framework enhances LLM agents through self-prompting and structured state-tracking, enabling better world model maintenance — [StateAct: Enhancing LLM Base Agents via Self-prompting and State-tracking](https://arxiv.org/abs/2410.02810)
- **Enforcing Narrative Reliability and Epistemic Pacing** in detective games uses structured knowledge trees to track player knowledge state and game world facts, preventing inconsistencies and controlling information flow — [Enforcing Narrative Reliability and Epistemic Pacing in LLM-Driven Detective Games via Structured Knowledge Trees](https://arxiv.org/abs/2609.23043)
- Interactive fiction agents benefit from memory and map-building modules for better navigation and state tracking; belief tracking enables more consistent internal world models — [Learning Strategic Play with Language Agents in Text-Adventure Games](https://web.stanford.edu/class/archive/cs/cs224n/cs224n.1244/final-projects/MirandaLinLiNicBecker.pdf)

### Broader AI-Games Research Surveys

- **A Survey on Large Language Model-Based Game Agents** (arXiv:2404.02039) provides comprehensive coverage of LLM agents applied to games, including game understanding, playing, and creation, identifying open challenges in state representation and long-horizon planning — [A Survey on Large Language Model-Based Game Agents](https://arxiv.org/abs/2404.02039)
- **Large Language Models and Games: A Survey and Roadmap** (arXiv:2402.18659) covers LLM applications across game design, game mastering, NPC generation, and player modeling — [Large Language Models and Games: A Survey and Roadmap](https://arxiv.org/abs/2402.18659)

---

## Summary of Gaps and Open Questions

Despite recent progress, significant gaps remain:

1. **Fairness in novel action adjudication** — No published research specifically addresses how AI GMs should fairly evaluate genuinely novel player-invented actions against explicit rules. This is the most critical unexplored area identified.

2. **Cross-system evaluation** — No benchmarks or comparative studies test different GM architectures (single monolithic model vs. multi-agent specialized systems vs. explicit state-tracking approaches) on the same player experience and consistency metrics.

3. **Feedback loops and agent coordination** — Limited research on how to resolve conflicts between specialized agent recommendations (rule-checker vs. narrator vs. world-state manager) and how tight the feedback loops should be.

4. **Player preference formation** — Insufficient research on how prior expectations, marketing, and familiarity bias player assessments of AI vs. human GMs; longitudinal preference tracking is absent.

5. **Rule interpretation learning** — No research on whether LLMs can learn game-specific rule interpretation from examples, or whether they must be explicitly prompted for each scenario.

6. **Latency and immersion** — Limited research on how response latency (currently 6.9 seconds for complex agents) affects player experience and perceived immersion in real-time TTRPG play.

These gaps suggest that while evaluation frameworks and multi-agent architectures are maturing, the core challenges of fairness, autonomy-respecting game adjudication, and player-centered design remain largely unexplored in published academic literature.
