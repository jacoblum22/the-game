# Memory and factual consistency for AI game masters (2024 to October 2026)

Research date: 2026-10-07. Gathered by a research subagent.

**Source caveat.** The network proxy blocked direct fetches from arxiv.org, huggingface, latitude.io,
fables.gg and ianbicking.org. Most claims below therefore come from search-engine summaries of the
primary sources. Two primary sources were read directly: the NCP-Bench repo and the intra-game repo.
Re-check exact figures at the source before quoting them.

**Correction made during synthesis.** The subagent reported that it could not trace the "64.78%
reduction in critical hallucinations" figure. It is in fact traced in this repo's earlier report
(`reports/Long horizon LLM narrative benchmarks.md`). The source is the structured-knowledge-tree
detective-game paper, arXiv 2609.23043, which the subagent also cites below.

## Bottom line

**Convergence.** In 2025–26, serious shipping products and the most-cited papers all moved toward
the same three ideas:

- code owns the state;
- the model proposes typed changes ("deltas") that code validates;
- the narrator only renders facts it was given.

**Memory alone does not fix factual contradictions.** In NCP-Bench, the HiAgent baseline cut
commitment conflicts from 26% to 4%. But fact conflicts stayed at 59% (60% before), and
player-input conflicts rose from 13% to 38%.

**Verification works on small structured claims.** A judge reading the whole prose passage is weak.

## Shipping products

### AI Dungeon (Latitude), then Heroes, then Voyage

**AI Dungeon** combines three pieces:

- **Story Cards:** keyword-triggered entries, ranked by recency and frequency, packed until the token
  budget runs out.
- **Memory Bank:** embedding-retrieved summaries.
- **Auto-Summarization.**

Latitude's own docs concede the model "won't always reference or even correctly repeat information
from the Memory."

**Heroes** (Dev Log #11, <https://latitude.io/news/11>) added:

- hierarchical summarization;
- a memory bank;
- typed game state (inventory, stats, quests) fed back to the model every turn.

**Voyage** launched on 2026-04-21 after "six prototype engines."

- Its deterministic "World Engine" tracks health, inventory, currency, geography, relationships and
  consequences "so the AI can't hallucinate them away." The model only narrates.
- Latitude positions this against "agreeable improvisation" by the model.
- Sources: TechCrunch, 2026-04-21; RuntimeWire.

**Lesson:** the biggest incumbent abandoned memory-as-text in favour of engine-owned state.

### Friends & Fables ("Franz")

- **Memories V2** (June 2025):
  - V1 produced too many small, low-value memories.
  - V2 makes fewer, larger memories, attached to characters and locations.
- **Patch 25.41** (October 2025):
  - Memories are tagged by which characters should have them.
  - Each NPC's last 20 memories feed a per-NPC planning step.
- **Franz 2.0:** a research step before each reply builds the context blocks.
- **Franz 2.0.1:** long out-of-character correction arguments degraded play.

**Lesson:** corrections should edit the state, not pile up in the transcript. Combat and HP are
resolved by the engine.

### Hidden Door (launched August 2025)

- The game runs as many small AI tasks over a database of cards plus authored trope "beats."
- **Pronouns are computed from a distribution and stored. The model never chooses them.** This
  directly answers this project's pronoun incident.
- Ian Bicking's design review still lists character consistency and pronouns as a problem area.

### Intra (Ian Bicking, July 2025)

- Code decides ground truth, such as who holds the key.
- An append-only event stream is the only mutable structure. Current state is a view over that
  stream, and undo means truncating the log.
- Source: <https://github.com/ianb/intra-game>, read directly.

### Other products

- **NovelAI and SillyTavern:** keyword-triggered lorebooks, plus recursive activation and vector
  storage. Good for static lore; they do nothing for state that changes.
- **Character.ai** (May 2026 redesign): story memory, auto-extracted facts, and up to 15 verbatim
  pins. The pins exist because the model paraphrases memories. Users still report lost history and
  characters drifting back to the base persona.
- **Inworld:** per-character knowledge filters, an early product form of scoping what each NPC
  knows.

## Research findings

### Benchmarks: what fails

**NCP-Bench** (ICML 2026, arXiv 2608.08160; repo read directly):

- GPT-5.2 is conflict-free in only 42% of runs at turn 20.
- Fact conflicts end 40–68% of the runs that fail.
- With HiAgent memory, commitment conflicts fell from 26% to 4%, fact conflicts were essentially
  unchanged (60% to 59%), and player-input conflicts rose from 13% to 38%.

**ByteSized32-State-Prediction** (ACL 2024, arXiv 2406.06485):

- The best state-transition accuracy is about 60%.
- GPT-4 gets about 77% of direct effects and about 50% of indirect effects right.
- Errors compound: 60% accuracy per step falls below 1% after 10 steps. This is the core argument
  for code-owned mechanics.

**RPGBench** (arXiv 2502.00595): mechanical consistency falls with length, even when the model is
forced to output structured JSON.

**ConStory-Bench, "Lost in Stories"** (ACL Findings 2026, arXiv 2603.05890):

- Factual and temporal errors dominate, and cluster mid-narrative.
- Errors sit in spans of higher token entropy, which gives a cheap signal for prioritizing audits.

**FlawedFictions** (COLM 2025, arXiv 2504.11900):

- Plot-hole detection degrades with story length.
- LLM summaries introduce 50%+ more plot holes than the originals. Summarizing is itself a source of
  error.

**ContraDoc** (NAACL 2024, arXiv 2311.09182): models are near chance at spotting self-contradictions
in long documents, and stories are the hardest domain.

**"Seduced by the Narrative" / CoC-Seduce** (July 2026, arXiv 2607.02802):

- Across 20 models acting as TTRPG adjudicators, players can talk the model into bad rulings
  ("rhetorical injection"). Arguments that sound logical but aren't are the strongest attack.
- Neither larger models nor reasoning modes reliably help.

### Architectures that work

- **Orchestrated Reality** (June 2026, arXiv 2606.16014). This is the closest published match to our
  design.
  - World state is a tree of canonical JSON entities, and the narrator sees only a narrative
    projection of it.
  - Each turn runs Plan → Diff → Validate (schema and permissions) → Apply, as an atomic,
    content-hashed commit.
  - Only one GM agent is allowed to commit.
  - The paper includes a catalogue of 15 incidents from a real deployment.
- **Function-calling GM** (Song, Zhu and Callison-Burch 2024, arXiv 2409.06949): game-specific
  functions improved both narrative quality and state-update consistency.
- **ConWriter** (arXiv 2608.05169): symbolic checks on state transitions, validation prioritized by
  uncertainty, and repair that rewrites only the bad span. It beats DOME on ConStory-Bench.
- **NstAgent** (September 2026, arXiv 2609.35759): structured state for characters, past events and
  future requirements. Consistency holds from 10K to 100K words.
- **Structured Knowledge Trees** (arXiv 2609.23043):
  - Clue nodes carry `Revealed`, `Source`, `Is_Truth`, `Prerequisites` and `Contradicts_With`.
  - This is the source of the 64.78% reduction in critical hallucinations.
- **Zep/Graphiti** (arXiv 2501.13956): bi-temporal facts that are invalidated rather than deleted,
  with the raw episodes kept underneath.
- **Retrieval:**
  - Hybrid BM25 plus embeddings plus a reranker cut retrieval failures by 67% (Anthropic, Contextual
    Retrieval).
  - HippoRAG 2 (arXiv 2502.14802) improves associative and multi-hop recall.
  - LongMemEval (arXiv 2410.10813) finds memory systems are weakest on updated knowledge and
    temporal reasoning.

### Verification

- **Decompose, then verify.** Break text into atomic claims and check each one (FActScore,
  VeriScore arXiv 2406.19276, DnDScore). DnDScore adds decontextualization so each claim can be
  checked on its own.
- **Chain-of-Verification** (arXiv 2309.11495) helps only when the verification questions are
  answered *without* seeing the draft.
- **Self-checks have a measured blind spot.** These two findings explain why the narrator's
  self-check missed the pronoun.
  - Self-Correction Bench (arXiv 2507.02778): models miss their own errors about 64.5% of the time,
    while fixing the same errors when they are attributed to someone else.
  - Hallucination snowballing (arXiv 2305.13534): models defend earlier errors they would recognize
    as wrong in isolation.
- **MiniCheck** (arXiv 2404.10774): GPT-4-level grounded fact-checking from a 770M model at about
  400× lower cost.
- **"Let Me Speak Freely"** (arXiv 2408.02442): strict JSON output hurts reasoning but helps
  classification. Keep schema-constrained calls small.

## Failure modes and the technique for each

- **Invented details.** Code generates the attributes a schema requires (pronouns, name, species,
  appearance) when an entity is created. An unsupported claim is either rejected or committed
  explicitly as a new fact; it never becomes canon silently.
- **NPC knowledge leakage.**
  - Tag each memory with its witnesses.
  - Give facts `known_by` / `revealed` flags.
  - Each NPC's dialogue prompt gets only that NPC's view.
  - The auditor checks "the speaker asserts F, but F is not in the speaker's knowledge."
  - Leakage grows with the number of rounds (MAGPIE, arXiv 2510.15186).
- **Forgotten promises.** Keep a first-class ledger of commitments and threads, injected every turn.
- **Timeline errors.** Bi-temporal facts, a game clock owned by code, and time-aware retrieval.
- **Numeric drift.** Numbers live only in code. The auditor checks every number that appears in the
  prose.
- **Sycophancy.**
  - Split the player's input into intent and claims, and check the claims against state *before*
    adjudicating.
  - Keep adjudication in a separate call with no narrator persona. Agreeable personas sharply raise
    sycophancy (r up to 0.87, arXiv 2604.10733).
  - Out-of-character corrections update the state, not the transcript.
- **Summarization drift.** A summary is a view regenerated from the event log. Never summarize a
  summary.

## Cost and latency

- Run adjudication and state changes (small and structured) first, then narrate.
- Run fast structural audits (regex or NER for names, pronouns, numbers and inventory) while the
  draft is produced.
- Run independent checks concurrently, so latency is the slowest check rather than the sum of all
  checks.
- Fix failures by repairing the bad span, not regenerating everything.
- Use small checkers by default, and save the cross-family auditor for high-risk spans.
- Prompt caching:
  - Put the stable prefix first and the volatile state last.
  - Anthropic reports up to 90% lower cost and 85% lower latency on long prefixes.

## Ranked techniques for our architecture

1. Engine-owned canonical state, updated by Plan → Diff → Validate → Apply.
2. An append-only event log as the source of truth.
3. Decide outcomes in a structured step, then narrate from a closed "render packet".
4. A cross-family auditor checking atomic claims, using factored questions that never show it the
   draft. "Unsupported" claims escalate, not just "contradicted" ones.
5. Per-NPC knowledge scoping, with witnesses tagged when facts are written.
6. A commitments and threads ledger.
7. Verify the player's claims before adjudication, in an adjudication call with no narrator persona.
8. Bi-temporal facts and a clock owned by code.
9. Hybrid retrieval, plus expansion to the neighbours of entities in the scene.
10. Tiered, parallel, cached verification with span-level repair.

## Open problems

- **What counts as "unsupported" in creative prose.** Expect to maintain hand-tuned allowlists per
  attribute class.
- **Auditors are weak on long or subtle text.** Claims have to be small and structured.
- **Rhetorical injection** has no reliable fix.
- **Responsiveness versus consistency.** Tighter constraints can make the narrator ignore the
  player, so responsiveness needs its own metric.
- **A change can pass validation and still be wrong.** ByteSized32 found about 50% accuracy on
  indirect effects.
- **No public evidence beyond about 100 turns.** Nothing benchmarks multi-session campaigns of
  thousands of turns.

## Checking the project's own cited figures

- **"64.78%":** traced to arXiv 2609.23043, per this repo's earlier report.
- **"46–58% consistency with function-calling":** may combine separate sources.
  - The 58% matches LLM-DND-GST joint state-tracking accuracy (arXiv 2210.07109), which came from
    fine-tuning, not function calling.
  - The roughly 60% from ByteSized32 is nearby.
  - Worth tracing before it is cited again.
- **NCP-Bench's 42% at turn 20 (GPT-5.2):** confirmed.
