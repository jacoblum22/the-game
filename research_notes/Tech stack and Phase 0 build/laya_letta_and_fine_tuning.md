# Laya, Letta, and fine-tuning small models

Research date: 2026-10-07. Gathered by a research subagent using web search and fetch.

**Source caveat.** The network proxy blocked letta.com, docs.letta.com, huggingface.co and several
blogs. Primary sources were used wherever they could be reached: GitHub READMEs, PyPI metadata and
pull requests. Claims that come only from secondary sources are marked as such.

The Laya claims were re-checked by the orchestrator directly against the GitHub README on the same
day. All the numbers in the Laya section below are confirmed verbatim, including the negation
failure (issue #377), SST-5 0.372, Banking77 0.425 versus Jev's 0.870, and the line "Treat Laya as a
fast base to specialise, not as a zero-shot decision engine."

## What "Laya" means

There is a real product literally named **Laya**: <https://github.com/NandhaKishorM/laya>,
<https://pypi.org/project/laya/>.

- **Who makes it.** Convai Innovations. This is a different company from Convai Technologies, the
  game-NPC company.
- **What it is.** An open-weight, non-autoregressive "System 1 decision engine." It is licensed
  Apache 2.0.
- **How new it is.** The first PyPI release, v0.1.0, was on 2026-09-18. The latest seen was v0.3.28
  on 2026-10-05.
- **How it relates to Jev.** Its README benchmarks it against **Jev**, which is the TypeSafe
  exception-gating tool already discussed under constitution Principle III. That makes Laya almost
  certainly the tool the owner meant.

**Checkpoints:**

| Checkpoint | Base model | Parameters | Context |
|---|---|---|---|
| `laya` | ModernBERT-large | 421M | 512 tokens |
| `laya-multilingual` | mmBERT-base | 322M | 1,024 tokens (extendable to 8,192) |
| `laya-typed-decisions` | ModernBERT-large, fine-tuned | 421M | 512 tokens |

**How you use it.** Laya generates no text. You give it a *state* (text or JSON) plus typed
questions, and it returns calibrated probabilities in a single forward pass. There are three
question types:

- `choice`: pick one label from a list.
- `score`: an ordinal level.
- `noul`: the probability that a yes/no statement is true.

**Speed.** About 33 ms per question on a T4 GPU, or about 7.2 ms per question when batched.

**Accuracy.**

- It is not useful zero-shot. On the typed-decisions benchmark the base checkpoints score
  0.362/0.352, which is below the 0.461 majority-class baseline.
- Fine-tuned (`laya-typed-decisions`), it reaches 0.766. Training is the whole point.

**Fine-tuning.**

- Command: `laya-train --data file.csv --out ./ft`.
- Data: a CSV of `{state, questions, expected}` rows, or plain labelled data.
- Method: "RLCD", reinforcement learning against proper scoring rules.
- Hardware: free Kaggle 2×T4 GPUs (about 4–5 h for 4 epochs over ~30k questions), or Apple Silicon.

**Limitations the README documents:**

- **Many labels.** About 20 short options fit the token budget. Beyond that you need
  `predict_tournament`. On Banking77 (77 labels) it scores 0.425, against Jev's 0.870.
- **Negation.** On negated requests such as "don't cancel my account", it chose the cancel label for
  all four negated cases (issue #377).
- **Ordinal questions.** `score` is its weakest primitive (SST-5: 0.372).
- **Calibration.** As shipped it is over-confident. Thresholds must be fitted per domain and per
  option count (`fit_abstention_thresholds`, `apply_binning_map`).
- **Long inputs.** Accuracy is "more variable" beyond about 4,000 tokens.

**Risk:** it is three weeks old, has a single main author, and changes fast.

## Letta (formerly MemGPT)

**State of the project in 2026:**

- **The Python server is retired.** The `letta-ai/letta` README says the "retired Letta V1 API
  server" lives on an `archive` branch, unsupported and without security fixes.
- **Development has moved to TypeScript.** Active work is in `letta-ai/letta-code`: a TypeScript/npm
  harness with a CLI, desktop app, App Server and channels.
- **The Python SDK is deprecated.** `letta-python` was deprecated on 2026-09-13 in favour of the
  TypeScript-only Letta Agent SDK (letta-ai/letta-python PR #95).
- **The Agent File (`.af`) format** is deprecated and removed.
- **Current features:**
  - Self-editing memory blocks.
  - MemFS: git-tracked context with branch, diff and rollback ("context repositories", February
    2026).
  - Skill learning, subagents, and "dreaming" (sleep-time compute, arXiv 2504.13171).
- **"Training" means token-space learning, not changing model weights.** See Letta's December 2025
  post, "Continual Learning in Token Space".
- **Pricing** (secondary sources): free for 3 agents; Pro $20/month; API plan $20/month plus
  per-agent and per-tool-second fees; self-hosting free.

**Known weaknesses:**

- Each memory operation adds tokens and latency on the critical path.
- Editing memory blocks breaks prompt caching (forum.letta.com/t/breaking-prompt-caching/149).
- "Memory rot": contradicted facts persist.
- The memory is only as good as the model's choices about what to save.
- The platform churns quickly.

**Games and DMs:** no primary-source examples of Letta used for games or DMs were found.

**Fit for The Game: poor as infrastructure.** Its core idea is that the model curates its own
memory, which is the opposite of our "app-owned ground truth plus independent verifier" design. It
is also now TypeScript-first and cloud-first, while we are a Python project on Gemini.

**Patterns worth borrowing:**

- **Sleep-time consolidation:** between sessions, a background job proposes state changes, and the
  auditor validates them before they are committed.
- **Git-style versioned state** that can be diffed and rolled back.
- **Small "core memory" blocks rendered from the store** each turn, rather than edited freely by the
  model.

## Llama and other small open models (for fine-tuning)

**Model landscape:**

- **Llama:** status is murky. Meta launched the closed Muse Spark on 2026-04-08. Reports of
  open-weight "Llama 5" conflict and are unverified.
- **Better small bases, both Apache 2.0:**
  - **Qwen 3.5** (February 2026): 0.8B, 2B, 4B, 9B and 27B.
  - **Gemma 4** (2026-04-02): E2B, E4B, 26B-A4B and 31B.
- **Avoid Gemma for the auditor.** It is a Google model family like the Gemini narrator, so it would
  fail the independent-family requirement.

**Training costs** (secondary sources):

| Provider | Price |
|---|---|
| Together AI | ~$0.48 per 1M tokens for LoRA fine-tunes up to 16B; Qwen 3.5 9B ~$0.34/M |
| Fireworks | $0.50/M up to 16B; LoRAs served at the base model's price |
| OpenPipe | now owned by CoreWeave (September 2025); offers ART for reinforcement-learning fine-tuning |
| Unsloth on a local GPU | essentially free |

A classifier or judge LoRA trained on 5k examples × 1k tokens × 3 epochs comes to roughly 15M
tokens, or **under $10 per run**. The real cost is building the data and the evals.

**Prior evidence that small checkers work:** MiniCheck (<https://arxiv.org/abs/2404.10774>) is a
770M Flan-T5. It reaches GPT-4-level grounded fact-checking at about 400× lower cost, and was
trained mostly on *synthetic* claim/document pairs.

### Where fine-tuning fits, ranked

1. **Classifying freeform actions onto closed lists.** This is the best fit, and the best fit for
   Laya. Use two stages when there are more than ~20 labels: a coarse class, then a shortlist.
2. **Reranking rule cards.** A small cross-encoder or embedding fine-tune.
3. **Auditor grounding judge.** Code extracts claims and looks up the facts; a small NLI/MiniCheck-
   style judge then rules on each (claim, fact) pair. Uncertain cases escalate to a stronger
   cross-family model. Never use Laya zero-shot for this.
4. **Turning narration into structured state changes.** This needs a *generative* model, so Laya
   cannot do it. Use a Qwen 3.5 4B–9B LoRA, distilled from verified traces produced by a frontier
   model.

### Synthetic training data from our own pipeline

- **Classification labels:** have a frontier model paraphrase player phrasings for each card or tag,
  with hard negatives taken from neighbouring cards.
- **Auditor pairs:** start from true facts in the store and generate narration that is faithful,
  subtly contradictory, or that invents a detail. The labels are known by construction.
- **Extraction traces:** keep only traces that passed verification.
- **Evaluation:** always hold out a hand-labelled set taken from real sessions, because synthetic
  data can teach the generator's shortcuts.

## Memory layers: who decides what is true

| Layer | Who decides truth | Drift risk |
|---|---|---|
| Letta | the agent edits its own blocks (now git-versioned) | High |
| Mem0 | LLM extraction; since April 2026, "single-pass ADD-only… nothing is overwritten" | Medium-high: contradictions accumulate |
| Zep / Graphiti | LLM extraction, but with provenance back to raw episodes, bi-temporal validity windows, invalidation instead of deletion, and a Pydantic ontology. Runs on Neo4j or FalkorDB. Zep CE is retired; Graphiti is still open source (<https://arxiv.org/abs/2501.13956>) | Medium |
| LangMem / LangGraph store | bring your own store | depends on configuration |
| Cognee | an LLM-built knowledge graph | Medium-high |

**Conclusion:** canonical state should live in an app-owned store backed by an event log. An
LLM-curated layer is acceptable only as a secondary, citable index for narrative recall, and never as
the authority on mechanical facts.
