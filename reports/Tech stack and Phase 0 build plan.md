# Building it: tech stack, memory, and a Phase 0 plan

*Research pass, 2026-10-07. This report is the synthesis. Raw findings, with citations, are in
`research_notes/Tech stack and Phase 0 build/`. It was written against the ruleset on
`origin/integration-wave-swxsot` (v1.0 release candidate) and constitution v1.7.0.*

**Source caveat:** Exa was not available in this session, so this pass used ordinary web
search and fetch. The proxy blocked several primary sources: arxiv.org, Google's and OpenAI's
pricing pages, and letta.com. Those findings rest on search summaries and are marked as such in the
notes. Re-check any price or exact figure before committing to it.

## Summary

- **The rules have already solved most of the memory and hallucination problem.** They decide what
  the AI is allowed to do, and the industry has converged on the same split:
  - code owns state;
  - the model classifies onto closed lists;
  - outcomes are adjudicated before any prose is written;
  - a claim check runs against the store before delivery.

  The evidence:
  - Latitude rebuilt AI Dungeon's successor, Voyage, around a deterministic "World Engine".
  - Intra and Hidden Door use the same pattern.
  - The closest published paper, *Orchestrated Reality* (June 2026), describes a Plan → Diff →
    Validate → Apply loop that is almost exactly our T4–T6.
- **What's left is narrower, and most of it is engineering, not research:**
  - (a) Linking the claim extractor's output to the right entity ids, and catching every
    claim. Extraction recall is now the ceiling on correctness.
  - (b) Per-NPC knowledge scoping in dialogue.
  - (c) Deciding what counts as an "unsupported detail" in creative prose.
  - (d) Rhetorical injection, where the player argues the model into a ruling.
  - (e) A change that passes validation but is still wrong.

  Section 3 covers each one.
- **The biggest risk is not hallucination. It is scope and per-turn cost/latency.**
  - The rules specify about 1,500 deterministic rules, 36 tools and a 12-step turn loop. Run
    naively, as one model call per judgment, a turn would cost 30–60 s.
  - Phase 0 needs a code-driven orchestrator that batches the model's judgments into 3–4
    structured calls. It also needs a vertical slice, not breadth.
- **Recommended stack:**
  - Python and FastAPI.
  - Pydantic AI, pinned, behind our own interface.
  - SQLite event log plus projections, one file per campaign.
  - Hybrid rule-card retrieval.
  - Gemini 3.8 Flash as narrator and adjudicator.
  - A Claude-family claim extractor (Haiku 4.5), different family from the narrator, as P13
    requires.
  - Textual for the UI, Logfire for tracing.
  - Estimated cost is **~3.5–6¢ per turn**, with a typical turn taking **6–10 s**.
- **"Laya" is a real, three-week-old model, not a typo.** It is a ~420M-parameter decision
  classifier from Convai Innovations that you are expected to fine-tune. It fits our `[J:enum]` /
  `[J:flag]` classification steps well, *after training*. It is unusable zero-shot. Worth a
  time-boxed Phase 0 spike. **Letta** (the other name it might have been) is a poor fit and is
  mid-pivot to TypeScript.

## 1. Where the rules stand (what we're building against)

**Branch note first:** the ruleset, constitution v1.7.0 and Feature 003 are only on
`origin/integration-wave-swxsot` (21 commits ahead of `main`, last commit 2026-10-07, "V2b1
verification in progress"). `main` still has constitution v1.5.0 and no `rules/` directory. Before
Phase 0, finish V2b, freeze, and merge it to `main`, so the build branches off one source of truth.

### Size and shape

| Thing | Count |
|---|---|
| Chapters | 16 (00–13, 15, 16; ch.14 Player's Guide/codex deferred until the interface exists) |
| Numbered rules | ~1,490 |
| Rule-kind tags | ~1,525 `[D]` deterministic · 231 `[J:flag]` · 180 `[J:enum]` · 52 `[J:rung]` · 7 `[J:open]` · 104 `[T]` triggers · 116 `[N]` · 30 `[S]` sealed |
| Procedures / worked examples / invariants | 138 PR-* / 143 WE-* / 20 INV-* |
| Data | 56 YAML files, 5.6 MB (abilities.yaml alone is 1 MB) |
| Seeded simulations | 68 Python scripts in `rules/_process/simulation/` |
| Open issues | 5 MAJOR (I-037…I-041), 24 minor. None blocks the build |

### The architectural bet the rules already make

Ch.00 states the bet directly. The model is good at *classifying free-form intent onto closed
lists* (~94–97% on closed sets, ~87% on yes/no). It is bad at choosing numbers, remembering
situational rules, resisting persuasion, keeping secrets and imposing loss. The rules respond in
four ways:

1. **Numbers are never the model's.** The model supplies ids, enums, rungs, flags and short text
   only. It never supplies a DC, modifier, harm amount, tick count, odds, price or duration
   (00.14.3, INV-3).
2. **Every judgment is reduced to its most reliable form:** flag → enum → rung → open. Only 7
   `[J:open]` rules remain in the whole corpus.
3. **Situational rules fire from state, not recall.** 104 `[T]` triggers come back from
   `get_active_triggers()` each turn. Handlers in `boundaries.yaml` run on the time ladder.
4. **Adjudication is written before prose** (12.2.8). The turn produces a typed *frame* and a list
   of state writes first. Narration is drafted from the stored record, then its claims are checked
   against the store (12.3).

### This is already most of a technical spec

The plan for the tech stack mostly lives in four places in the rules:

- **00.6 State model:** 18 typed state families. These are entity, quantity, flag, fact,
  relationship, position, knowledge, clock, condition, license, effect_instance, tally, ledger,
  commitment, offer, time, frame and meta. Each has a visibility class (shown / available /
  background / sealed). There are fixed state disciplines: no change without a tool write; a
  summary is never the source of truth; temporal claims are computed from timestamps.
- **00.14 Tool surface:** 36 tools over 10 runtime capabilities: RC-RNG, STORE, SEAL, SCHED, LOG,
  DATA, QUERY, EVAL, RETRIEVE, AUDIT. These map almost one-to-one onto backend modules.
- **00.15 Retrieval and the context packet:** an always-loaded core, plus at most 12 rule cards
  (triggers first, then anchors, then situation cards), plus the narrator view of state, plus the
  player message verbatim, plus the last 4 exchanges verbatim. Nothing older is included except
  through typed state.
- **PR-12-1 Turn loop:** T1 RECEIVE → T2 CLASSIFY → T3 LOAD → T4 ADJUDICATE → T5 WORLD → T6 WRITE
  → T7 DRAFT → T8 MENTION → T9 CHECK → T10 SCREEN → T11 DELIVER → T12 RECORD.
  - The claim check uses 14 claim classes and 8 verdicts.
  - It allows at most 2 redrafts, then falls back to a plain narration built only from the record.
  - Disputes are answered from the turn log, never from memory.
  - `revert_writes` handles rewinds within a scene.

The prototype code (`src/`) is a *different and much smaller* contract:
- `roll_check(dc, modifier)` with free integers, which 00.14 explicitly removes;
- a flat-JSON `WorldState`;
- an agent loop where the model decides which tools to call.

The prototype proved the concept (Feature 002: 60% of runs had zero conflicts over 12 turns, and
both real failures were "narrated a change without calling the tool"). It is not the engine the
rules describe, and Phase 0 should not try to grow it into one.

## 2. Memory and hallucination: how far the rules get us

Most failure modes the research names already have a rule against them:

| Failure (research) | Where the rules already handle it |
|---|---|
| Numeric drift; state transitions compounding errors (ByteSized32: 60% accurate per step falls below 1% after 10 steps) | INV-3: the model never supplies numbers. Every number comes from `frame_check`, `apply_harm`, `update_quantity` and similar tools |
| Narration getting ahead of the record (Feature 002's only two real failures) | 12.2.8: writes come before prose. INV-1: no change without a write. The `unsourced_change` verdict cuts a change rather than writing it to match the prose |
| Invented details such as the pronoun incident (Hidden Door's fix: code chooses pronouns) | PR-12-5 fixes pronouns when an NPC is generated. 00.6.6 records anything mentioned in narration as it is introduced. An unsettled property is `undetermined` and goes to the Oracle; the narrator never invents it |
| Forgotten promises and threads (NCP-Bench: structure cut commitment conflicts 26% → 4%) | `commitment` is a typed state family, and the threads register |
| Timeline errors | 00.6.9e: temporal claims are computed from timestamps. Time is a deterministic ladder |
| Summary drift (summaries add 50%+ more plot holes) | 00.6.9d: a summary is never the source of truth and is never summarized again. The prompt carries 4 verbatim exchanges, with everything older held in typed state |
| Player claims and sycophancy ("I already have the key") | INV-9: something the player asserts is not a fact. Levers must cite fact ids. Assertions sit in their own frame field |
| Self-checks are blind to their own errors (Self-Correction Bench: about 64.5% blind spot) | P13: the checker must be a different model family. A plain fallback runs after 2 failed redrafts |
| Secrets leaking | The `sealed` partition. The narrator view never contains sealed content, and a `leak` verdict catches it if it gets through |
| Corrections piling up in the chat (Friends & Fables 2.0.1) | 12.3.4: corrections are typed writes and a corrections ledger; they don't live in the transcript |

So "partially figured out" undersells it. The design is sound and matches where the field ended up.
What it doesn't settle is how well each **model-judgment step** performs in practice. Every safeguard
above depends on some `[J]` step doing its job:

- T8 (MENTION) must notice that the draft introduced something.
- T9's extraction must turn every sentence into correctly classified claims about the right entity
  ids.
- T2 must classify the player's message correctly.

Whatever these steps miss gets past the deterministic checks. **The project's correctness is now
bounded by the recall of a few classification and extraction steps**, which is measurable and
trainable. That changes what Phase 0 should measure (section 7).

## 3. Big problems I foresee, ranked

### 3.1 Per-turn call count, latency and cost

PR-12-1 lists roughly 15–25 distinct judgments per turn. Examples: classify the message parts;
PARSE, GATE, NECESSITY, ANCHOR, then about ten FRAME fields per beat (up to 3 beats); NPC
want/refusal flags; DRAFT; MENTION; claim extraction; fixing each verdict; up to 2 redrafts; and
5 SCREEN flags. If each judgment is its own model call, as the prototype's agent loop would naturally
do, a turn takes **30–60 s and costs 20¢+**.

**Fix:** turn the prototype inside out, so code drives the loop and the model fills in typed forms.

- **The model never chooses among 36 tools.** The orchestrator runs PR-12-1 itself and asks the
  model for a few **structured outputs** whose fields are closed enums.
- **The enums are built per turn from the store.**
  - The `anchor` field's enum is the ≤8 candidates from the anchor index.
  - `levers` can only take fact ids that exist in the scene.
  - Entity references can only take ids from the scene cast.

  A made-up id then can't be expressed at all, which is stronger than catching it afterwards.
- The critical path becomes about four model calls:

  | Call | Model | Produces | Then |
  |---|---|---|---|
  | **A. Adjudicate** | narrator family, low thinking | T2 classification plus PARSE through FRAME for all beats, as one JSON | the engine runs `frame_check`. On a refusal, call A is retried once with the named failure |
  | — OFFER pause — | — | the player sees the odds and commits | this naturally hides latency on rolled beats |
  | **B. Draft** | narrator family | prose written from the adjudication record plus the fresh narrator view, along with the T8 mention list as a structured sidecar | the engine writes the new entities |
  | **C. Extract claims** | **different family** | claims `{subject_id, class, predicate, value}` constrained to scene ids, plus the five T10 screen flags | `check_claims` is **deterministic code** against the store (12.3.2's verdicts are `[D]`) |
  | **D. Redraft** | narrator family | only for the ~20–30% of turns with a non-`supported` verdict; patch the failing span (ConWriter-style localized repair), not the whole response | back to call C |

- **Delivery versus streaming.** The rules check the draft *before* delivery (T9 runs before T11), so
  we can't stream raw tokens to the player. Generate the draft fast (Flash outputs about 300 tok/s,
  so ~250 words takes about 1–2 s), check it, then reveal it with a typewriter effect. That's an
  explicit UX decision, so I've flagged it under decisions below.

### 3.2 Linking claims to the right entity

A claim is `{subject id, …}`, but prose says "the old man," "he," "the captain." Mapping those
phrases to `npc.tam_harlan` is real coreference work and **isn't specified anywhere in the rules**.

- If the link is wrong, the check raises a false `contradicted` and sends a needless redraft.
- If the link is missed, the claim is treated as a `new_element` and junk entities get created.

Mitigations:

- Give every entity aliases and descriptors in the store.
- Constrain call C's subject field to the scene cast plus `unknown`.
- Treat `unknown` as "cut the claim or ask," never as "create an entity."
- Track the false-positive rate separately. Feature 002's first runs were dominated by *auditor*
  bugs, not DM errors. Expect the same here.

### 3.3 Implementing ~1,500 deterministic rules that are still changing

- **The AI part is the smaller part.** Most of the engineering is RC-EVAL (the substrate executor:
  evaluation pass, hooks, combination regimes), RC-SCHED (the boundary registry and its 9 phases),
  the 104 triggers, the generators and the sealing.
- **Rules are still changing.** 5 MAJOR issues are open, and V2b is in progress.

Defences:

- **Make the engine data-driven wherever the YAML already is the rule.** For example, the boundary
  handlers, tables, abilities and adversaries.
- **Tag every code path with the rule id it implements** (`# rule: 06.3.2`).
- **Extend `validate_ruleset.py` into a coverage report.** Every `[D]` rule should be marked
  implemented, data-driven or deferred, so a rules edit shows exactly which code is now stale.
- **Turn the 143 worked examples (WE-\*) into golden tests.** They already have numbers end to end.
  This is the cheapest high-value test suite available.
- **Port the 68 seeded sims as reference implementations,** and check the engine against their
  committed outputs.

### 3.4 What counts as "unsupported" in creative prose

- **No paper solves this.** The rules have a policy:
  - `new_element` → write it down if it is ordinary scene furniture (12.14.13), otherwise cut it;
  - `undetermined` → ask the Oracle.
- **Two costs.** In practice, every adjective about a stored NPC is a judgment call. If the line is
  drawn too strict, prose gets bland or redrafts loop. If too loose, details creep in.
- **What to do:**
  - Expect per-class allowlists (appearance details vs. identity facts) and tune them from data.
  - Measure the plain-fallback rate. If it rises above a few percent of turns, the policy is too
    strict.

### 3.5 Rhetorical injection

CoC-Seduce (July 2026) found that 20 models acting as TTRPG adjudicators are talked into bad rulings
by plausible-sounding pseudo-logic. Neither larger models nor reasoning reliably helps. The ruleset's
own research measured "a plausible justification ~quadruples the error rate."

Our defences are structural:

- Assertions are context, never facts (INV-9).
- Levers must cite fact ids (`frame_check` refuses otherwise).
- The OFFER step shows the frame to the player.

**What to do:**

- Keep the adjudicator call **persona-free.** It is not the narrator, and it gets no "be a fun DM"
  instructions. Agreeable personas measurably raise sycophancy.
- Add an adversarial-persona eval targeting the levers and the GATE classes. Feature 002's
  adversarial player is the start of this.

### 3.6 A change can pass validation and still be wrong

- **The limit.** Schema validation can't tell that the model picked the *wrong* legal anchor or
  stakes rung.
- **What the rules already do.** They cap the damage. Each `[J]` rule has a stated worst case
  (class iv: one step, reversible), and the ruling ledger plus `review_flag` gives the Principle III
  revisit the evidence it needs.
- **Remaining work: build the dashboard.** The ruling ledger is the dataset; someone has to look at
  it.

### 3.7 Smaller problems

- **Branch hygiene.** The rules exist only on an integration branch (section 1). Merge to `main`
  before building.
- **Gemini 3.8 Flash latency.** On default thinking it measured a 13.3 s time to first token.
  Always set `thinking_level` explicitly. `minimal` was removed, so requests that ask for it now
  fail.
- **The Gemini promo ends on 2027-01-01.** Flash prices double then.
- **Safety refusals on fantasy violence.** Both Claude (`refusal` stop reason) and Gemini have
  safety filters that can refuse.
  - Handle a refusal with a fallback.
  - Keep refusal handling out of the consistency ledgers (12.3.7 already separates moderation from
    consistency).
- **Two cited figures need tracing.**
  - "46–58% consistency even with function-calling" (P3, ch.00) may combine separate sources. The
    58% matches a 2022 fine-tuned state-tracking result, not function calling.
  - The 64.78% figure traces cleanly to arXiv 2609.23043.
- **Supply chain.** LiteLLM's PyPI package was compromised on 2026-03-24. Keep dependencies few and
  hash-pinned.

## 4. Recommended stack

| Layer | Pick | Runner-up | Why |
|---|---|---|---|
| Language / server | **Python 3.11+, FastAPI** | TypeScript (Bun + Mastra) | The prototype, 68 sims, validator, `rq.py` and generators are all Python. Pydantic models can serve as the tool schemas, the change ("delta") schemas and the API schemas at once. A TypeScript web client can come later without touching the engine. |
| LLM layer | **Pydantic AI (pinned)** behind our own `Adjudicator` / `Narrator` / `ClaimExtractor` interfaces | Raw provider SDKs | Typed structured output with automatic retry, both Gemini and Claude supported, fallback models. Pin it: it releases several times a week. Drop to the raw SDK wherever explicit cache control isn't exposed. |
| Orchestration | **Our own code: PR-12-1 as a plain Python state machine** | LangGraph | The turn loop is already fully specified. A graph framework would duplicate our event store. No durable-execution framework yet: a turn is one transaction, and the event log is the checkpoint. |
| Store (RC-STORE, LOG, SEAL) | **SQLite (WAL), one file per campaign.** An append-only `events` table is the source of truth; typed projection tables mirror 00.6's state families. | Postgres + JSONB + pgvector (when hosted and multi-user) | Single-player and local-first. Save, branch and rewind become a file copy or a fork of the log. `revert_writes` becomes compensating events. Thousands of turns is only ~10⁵–10⁶ events. |
| Facts | Bi-temporal rows: `valid_from` / `valid_to` plus `source_event` | Graphiti | "What was true at time T" and provenance for every fact (00.6.7's six sources). Borrows Graphiti's model without its per-turn model-based extraction. |
| Graph DB | **None** | FalkorDB + Graphiti | Relationships are fact rows, walked with recursive SQL. Kuzu is archived, and Graphiti makes state non-deterministic. |
| Rules retrieval (RC-RETRIEVE) | **Filter by tag, anchor and trigger first** (this is what 00.15 specifies), then FTS5 keyword search + embeddings for fuzzy lookups, then a small reranker | Voyage rerank API | Most retrieval is already deterministic: triggers, `anchors.yaml`, situation tags. Fuzzy search is a fallback, not the primary route. Embedding the whole corpus costs under $0.15. |
| Caching | The always-loaded core is a stable prompt prefix. Order: system → core → cards → state → recent exchanges → message. | — | Gemini implicit caching (min 4,096 tokens); Claude cache reads cost 0.1× the normal input price. |
| Adjudicator + narrator | **Gemini 3.8 Flash, `thinking_level` set explicitly** | Claude Sonnet 5.5 (better prose, about 2× the cost) | Cheapest model that is capable enough. Keeps the prototype's provider. Re-evaluate before the 2027 price change. |
| Claim extractor / verifier | **Claude Haiku 4.5** (a different family from the narrator, per P13) | A fine-tuned Qwen 3.5 model (§5) | Different family, cheap, good at structured output. If we ever switch the narrator to Claude, the verifier must move to Gemini or Qwen. |
| Cheap classifiers | Regex/rules, then Flash-Lite, then **a fine-tuned Laya** (§5) | — | T2 classification, `[J:flag]` checks. |
| RNG (RC-RNG) | `numpy.random.Generator` seeded per campaign. Every draw is logged with its purpose. | — | Replaying a session means re-reading the RNG log and the stored model outputs. |
| UI | **Textual TUI** (story pane, codex pane, frame/OFFER widget with commit/change/withdraw buttons), served to a browser via `textual-serve` | FastAPI + SSE + SvelteKit | Pause points (12.2.6) are structured choices, so they need buttons, not free text. The codex (P7, ch.14) is a side panel rendering exactly the visibility classes. |
| Tracing / evals | **Logfire** (free for 10M spans/month) + pytest + a replay harness | Langfuse self-hosted, Phoenix | One trace per turn, with every model call, tool write and verdict. |
| Hosting | Local first; later one small VPS / Fly machine with SQLite on a volume plus Litestream backups | Cloud Run + Neon | Not needed for Phase 0. |

**How the runtime capabilities (00.14.1) map to modules:**

| Module | Runtime capabilities it covers |
|---|---|
| `engine/store` | RC-STORE, RC-LOG, RC-SEAL |
| `engine/data` | RC-DATA: load and validate the 56 YAML files against `SCHEMAS.md` |
| `engine/query` | RC-QUERY: tag ancestry |
| `engine/eval` | RC-EVAL: the substrate executor |
| `engine/sched` | RC-SCHED: time ladder, boundary registry |
| `engine/rng` | RC-RNG |
| `engine/retrieve` | RC-RETRIEVE |
| `engine/audit` | RC-AUDIT: `check_claims` |
| `dm/` | the PR-12-1 orchestrator and the three model roles |
| `ui/` | the TUI |

## 5. Laya, Letta and fine-tuning

**Laya** (github.com/NandhaKishorM/laya) is from Convai Innovations, not the NPC company Convai
Technologies. It was first released on 2026-09-18 under Apache 2.0, and its README benchmarks it
against Jev.

**What it is:**

- ModernBERT-large, 421M parameters, with a 512-token context.
- It does not generate text. It answers typed questions about a "state" in one forward pass, in
  ~33 ms on a T4:
  - `choice` (pick a label);
  - `score` (an ordinal level);
  - `noul` (probability that a yes/no statement is true).

**What it can and can't do yet:**

- **Zero-shot it is worse than always guessing the most common label** (0.36 against 0.46).
- **Fine-tuned it reaches 0.77.** Training uses `laya-train` on a CSV, and runs on free Kaggle GPUs
  in hours.
- **Limitations the README itself documents:**
  - accuracy collapses beyond about 20 labels (Banking77: 0.43, against Jev's 0.87);
  - negation failures ("don't cancel" chose cancel in 4 of 4 cases);
  - over-confident until calibrated per domain.

**Where it fits.** Our rules are deliberately built out of exactly what Laya does: 231 `[J:flag]`
(yes/no checks, which map to `noul`) and 180 `[J:enum]` (closed-list choices, which map to
`choice`), each with inside/outside/non-example cases already written. The best candidates:

1. **T2 message classification.** Eight classes, a short input, it runs every turn, and errors are
   cheap.
2. **12.2.2's SPEECH vs. DECLARATION** decision, and the other single-flag checks in T10 SCREEN
   (PC agency, mechanics stated in the fiction).
3. **Choosing the ANCHOR among ≤8 candidates.** This fits under its ~20-label ceiling.

**Where it doesn't fit:**

- Claim *extraction* (generative).
- Narration.
- Anything that needs more than 512 tokens of context, such as the full scene state.
- Any check where negation matters a lot and the model hasn't been trained on our negations.
- Never use it as the sole auditor.

**Training data is nearly free to make.**

- The rule cards' inside/outside/non-example cases are seed data.
- A frontier model can paraphrase thousands of player messages per class.
- Hard negatives come from neighbouring cards.
- Every logged turn whose label was confirmed downstream becomes a new labelled row.
- Always hold out a hand-labelled set taken from real play.

**Verdict.** A good Phase 0 **spike** (one to two days, T2 only), measured against Flash-Lite on
accuracy, calibration and latency. It is three weeks old and has a single main author, so put it
behind the same `Classifier` interface and keep the model-based classifier as the fallback.

**Letta (MemGPT): don't adopt it.**

- It is mid-pivot. The Python server is retired, the Python SDK was deprecated on 2026-09-13, and
  development is now TypeScript-first and cloud-first.
- Its core idea is that the model curates its own memory, which is the opposite of 00.6.9.
- Two ideas are worth borrowing:
  - "sleep-time" consolidation between sessions, where a background job proposes chronicle entries
    and changes that the auditor validates;
  - git-style diffable state, which our event log already gives us.

**Fine-tuning small models (Qwen 3.5 2–9B, not Gemma, since Gemma is the narrator's family):**

- **Claim-extractor distillation.** This is the most valuable fine-tune long-term: call C runs every
  turn.
  - Log Haiku's extractions and keep the ones the downstream check and human review confirmed.
  - After a few thousand turns, train a LoRA. A training run costs under $10; the effort goes into
    the eval set.
  - MiniCheck is the precedent: a 770M model checks grounded claims as well as GPT-4.
- **Don't fine-tune in Phase 0.** Collect the traces now, with the logging already in place, and
  train once there is data.

## 6. Cost and latency per turn (estimate)

Assumptions: about four model calls per turn (section 3.1), the core cached, and a redraft on about
30% of turns. Prices are from the stack notes, and the Gemini prices are not verified first-hand.

| Call | Tokens (in cached / in new / out) | Promo price (to 2026-12-31) | From 2027-01-01 |
|---|---|---|---|
| A. Adjudicate (Flash) | 10k / 8k / 1.5k | $0.012 | $0.024 |
| B. Draft (Flash) | 6k / 6k / 0.8k | $0.008 | $0.016 |
| C. Extract claims (Haiku 4.5) | 3k / 4k / 1k | $0.009 | $0.009 |
| D. Redraft (30% of turns, B + C again) | — | $0.005 | $0.008 |
| Classifier, retrieval, background jobs | — | ~$0.002 | ~$0.002 |
| **Total per turn** | | **~$0.037** | **~$0.060** |
| **5,000-turn campaign** | | **~$185** | **~$300** |

The stack research reached a similar range independently: $0.043–0.072 per turn.

**Latency.**

- A typical turn takes about 2.5 s (A) + 1.5 s (B) + 1.5 s (C) ≈ **6 s**. A turn that needs a
  redraft takes **10–12 s**.
- Rolled beats split at the OFFER pause, and the player's commit time hides call A entirely.
- Show a "thinking" indicator. Friends & Fables shows its research step for the same reason.

**What moves cost and speed most:**

- **Thinking tokens.** Track them per call.
- **How many redrafts we need.**
- **Whether Laya or regex absorbs T2 and the flags.**

Sonnet 5.5 as narrator roughly doubles the cost for noticeably better prose. That trade is best made
with eval data rather than up front.

## 7. Phase 0 plan

**Goal:** one vertical slice of the real architecture, end to end, not breadth. A player can:

- start a world from the world seed (12.16);
- walk somewhere, which advances time and crosses boundaries;
- talk to a generated NPC;
- attempt an unlicensed action and be redirected (G3);
- make a rolled check with an OFFER pause;
- save, quit and resume.

That covers the store, sealing, time, retrieval, the frame pipeline, the claim check and the UI. It
leaves out combat, magic, crafting and progression.

**0.0 Housekeeping (before code)**

1. Finish V2b, merge `integration-wave-swxsot` into `main`, and tag the rules v1.0.
2. Resolve the MAJOR issues that touch the slice: I-038 (Oracle fishing). The others (I-037, I-039,
   I-040, I-041) touch combat and progression and can wait.
3. Record the stack decision in the constitution's `TODO(TECH_STACK)` through `/speckit-constitution`.
   Include the narrator/verifier family pairing as a recorded constraint.
4. Write Feature 004's spec with `/speckit-specify`, from this section.

**0.1 Engine core (no model calls; everything is unit tests)**

- **Store:** the `events` table plus projections for:
  - entity, quantity, flag/fact, relationship, position, knowledge, clock, time and ledgers;
  - the narrator/codex/audit views with sealing.
- **Data loader:** reads `data/*.yaml` and validates it against `SCHEMAS.md`.
- **RNG** with draw logging.
- **Time ladder** and the `boundaries.yaml` scheduler, for the handlers the slice touches.
- **Tools:** `frame_check`, `roll_check`, `read_result`, `oracle`, `roll_table`, `create_entity`,
  `set_fact`, `update_quantity`, `set_position`, `record_knowledge`, `advance_time`, `check_claims`,
  `log_turn`, `revert_writes`.
- **Golden tests** from the worked examples:
  - WE-00-1 (a boundary crossing)
  - WE-00-3 (an unlicensed attempt)
  - WE-00-4 (assembling a check)
  - WE-00-5 (clocks)
  - plus the ch.01 examples.

**0.2 Turn loop**

- PR-12-1 as a state machine, with calls A–D as typed Pydantic outputs whose enums come from the
  store.
- Retrieval by trigger, anchor and tag, under the 12-card cap.
- Pause points.
- The plain fallback.
- The prototype's `dm_agent.py` stays as-is, for comparison runs.

**0.3 UI:** the Textual app with a story pane, a codex pane and an OFFER widget, plus save and
resume.

**0.4 Evals and observability**

- Logfire traces.
- Port Feature 002's harness (scenario seeding, persona player, conflict report) onto the new
  engine, so its numbers become the baseline to beat.
- Track five metrics:
  1. **Claim-check verdict rates and plain-fallback rate**
  2. **Extraction recall** against a hand-labelled set of ~200 drafts. This is the number that bounds
     correctness (section 2).
  3. **Auditor false-positive rate** (Feature 002's lesson)
  4. **Input fidelity**, i.e. NCP-Bench's player-input conflicts (HiAgent's lesson: consistency
     fixes can make the narrator ignore the player)
  5. **Cost, latency and thinking tokens per turn**

**0.5 Spikes (time-boxed, can run alongside the rest)**

- **Laya on T2:** 1–2 days, compared against Flash-Lite.
- **Narrator comparison:** Flash against Sonnet 5.5 on the same replayed inputs, judged by a
  cross-family judge.

**Exit criteria for Phase 0:**

- A 50-turn persona-driven session runs end to end on the new engine.
- Its conflict rate is at or below Feature 002's.
- Turns stay within about 10 s and about 6¢.
- Every metric above is reported.

## 8. Decisions I need from you

1. **Stack defaults:** Python/FastAPI, SQLite event log, Gemini Flash narrator, Haiku extractor,
   Textual. Agree, or would you rather go web-first, or Claude-as-narrator?
2. **Delivery UX:** the rules require checking before delivery. That means no token-by-token
   streaming, just a short "thinking" pause and then a typewriter reveal. OK? The alternative is
   streaming with a post-hoc correction, which would mean amending 12.3.
3. **Auto-commit:** should rolled beats pause for OFFER by default, or should auto-commit (01.7.4)
   be the default, with the pause only on risky or dire stakes? This decides how chatty play feels.
4. **The Laya spike:** worth 1–2 days in Phase 0?
5. **Merge timing:** OK to treat the end of V2b as the freeze point, and merge the integration branch
   to `main` before Feature 004 starts?
