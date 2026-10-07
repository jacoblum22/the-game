# Research: Tech stack and the freeform scene slice

**Feature**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Date**: 2026-10-07

This is Phase 0 of `/speckit-plan`. It answers the tech-stack questions for the whole engine, then
narrows each one to what the first slice needs. It builds on the earlier research pass on branch
`claude/happy-franklin-ypo2wq` (`reports/Tech stack and Phase 0 build plan.md` and its notes), which
it does not repeat. Section 1 says where this pass agrees with that one and where it changes course.

**Sources and how far to trust them.**
- The ruleset, read by id with `rules/tools/rq.py`: 00.6, 00.7, 00.14, 00.15, 01.1–01.15, PR-01-1,
  12.2, 12.3, PR-12-1, PR-12-2, PR-12-7, T-12-1, and `data/anchors.yaml`, `data/boundaries.yaml`,
  `data/pacing.yaml`, `data/basic_verbs.yaml`.
- Claude prices: Anthropic's model reference, snapshot 2026-09-25 (Haiku 4.5 $1/$5, Sonnet 5.5
  $2/$10 per million input/output tokens).
- Gemini 3.8 Flash: third-party price trackers, 2026-10-07 ($0.75 in, $0.075 cached, $3.75 out
  including thinking, until 2026-12-31; double from 2027-01-01; thinking levels low/medium/high,
  medium by default, no minimal). Google's own page was not reachable. **Re-check before relying on
  it.**
- gpt-oss-120b: price trackers, mid-2026 (Groq $0.15/$0.60; OpenRouter about $0.07/$0.28). Structured
  output (JSON schema) is supported on both. **Unverified first-hand.**
- `google-genai` structured output: the SDK's own docs via Context7. `response_json_schema` accepts
  standard JSON Schema with `enum`, `$defs`, `anyOf`, `minItems`/`maxItems`; very large enums hit a
  server-side complexity limit.
- The prototype (`src/`), Features 001–003 and the constitution (v1.8.0).

## 1. What changes from the earlier plan

| Topic | Earlier plan (happy-franklin) | This pass | Why |
|---|---|---|---|
| Language, store, loop shape | Python; SQLite event log; code drives PR-12-1, the model fills typed forms | **Same** | Nothing found against it; this pass adds detail |
| LLM wrapper | Pydantic AI, pinned | **Two thin adapters of our own** (Gemini SDK, OpenAI-compatible SDK), Pydantic only for schemas | Only four call shapes; we need explicit thinking level, cache control and per-turn schemas on every call; fewer fast-moving dependencies (the same report flagged supply-chain risk) |
| "Call A" | One adjudication call per turn | **Two calls, A1 (read) and A2 (frame)** | The anchor candidates depend on the parsed verb, so the anchor enum can't be built before parsing. Splitting also keeps each call's packet under the 12-card cap |
| Claim checker | Claude Haiku 4.5 | **gpt-oss-120b on an OpenAI-compatible host** (Groq by default), Haiku as the fallback | The prototype moved off paid Anthropic API use (`src/dm_agent.py` docstring); gpt-oss is about 7× cheaper per check and still a different family from Gemini (P13) |
| UI | Textual TUI, then web | **Plain terminal REPL, then a FastAPI web app** | Hosting for remote players needs the web app anyway; a TUI would be thrown away. The slice's UI need is tiny |
| RNG | `numpy.random.Generator` | **`random.Random` streams from the standard library** | All 28 seeded sims that use randomness use `random.Random`, so ported generators can reproduce them exactly; no numpy dependency |
| Retrieval | Tag/anchor/trigger filter, then FTS5 + embeddings + reranker | **Deterministic only in the slice**; fuzzy search deferred | 00.15 specifies deterministic retrieval; the slice has no case that needs fuzzy search |
| Tracing | Logfire | **The turn record in the store is the trace**; OpenTelemetry later if needed | One less service and account; the turn record already holds every call, token count and cost |
| Laya spike, fine-tuning | Phase 0 spike | **After the slice** | Needs logged, labelled turns, which the slice produces |
| Phase 0 scope | World seed, walking, NPC, G3, OFFER, save/resume | **One scene, every turn step** | Matches the ask; narrow and deep first |

## 2. Three options for the engine

Each option has to deliver the same rules: INV-3 (the model never supplies a number), writes before
prose (12.2.8), the claim check by another model family (P13), the boundary registry (00.7), the
12-card packet (00.15.4) and replayability.

### Option A: Python engine, code-driven turn loop, the model fills typed forms (recommended)

The turn loop PR-12-1 and pipeline PR-01-1 are a Python state machine. At each `[J]` step the engine
asks the model for a structured object whose fields are enums built from the rules and the current
state (cast ids, held licence ids, fact ids, the ≤8 anchor candidates). Code does every `[D]` step:
frame computation, the roll, read, costs, writes, boundaries, claim verdicts. State is an append-only
event log in SQLite.

- **For.** It reuses everything that exists: `rq.py`, the validator, 78 simulation scripts (the
  reference implementations for generators), the YAML loaders, the prototype's provider code. The
  rules are written in exactly this shape (01.1.4: "the pick is always from a closed list"). A made-up
  id can't be expressed in an enum, which is stronger than catching it afterwards. Turns are
  replayable because every model output and every draw is logged. 4–5 model calls per rolled turn.
- **Against.** Python is slower than needed for nothing here (the work is I/O-bound on model calls).
  The web client later is a second language (HTML templates plus a little JS), but that's thin.
- **Risk.** Implementing ~1,500 `[D]` rules is most of the work in any option. Mitigated by being
  data-driven where the YAML is the rule, tagging code with rule ids, and golden tests from the 143
  worked examples.

### Option B: TypeScript full stack (Node or Bun, Vercel AI SDK with Zod, Postgres or SQLite, a React UI)

The same code-driven architecture, in one language from engine to browser.

- **For.** One language for engine and web UI; Zod plus the AI SDK's `generateObject` is a mature
  structured-output path; very easy hosting on serverless platforms.
- **Against.** Every existing tool is Python. The 78 simulations are the reference for generators and
  balance; porting to TypeScript means either rewriting them or running cross-language parity tests
  forever. `rq.py` and the validator stay Python, so the repo becomes bilingual on day one. Serverless
  hosting fights the one-file-per-campaign store, so it would push Postgres early. Jake's existing code
  is Python.
- **Verdict.** Not worth a rewrite. Revisit only for the browser client, and only if it outgrows
  server-rendered HTML.

### Option C: Model-driven agent loop over the 36 tools (grow the prototype)

The narrator model gets the tool surface (00.14.2) and decides which tools to call, as `src/dm_agent.py`
does today with three tools.

- **For.** Least code to start; already working in the probes; flexible.
- **Against.** PR-12-1 has 15–25 judgments per rolled turn. As tool round trips that is 30–60 s and
  20¢+ per turn (earlier estimate). Step order, INV-3 and "writes before prose" would be enforced only
  by the prompt, and the probes' only real failures were exactly "narrated a change without calling
  the tool". The model sees 36 tool schemas on every call. Replay is harder because control flow lives
  in the model.
- **Verdict.** Keep `src/dm_agent.py` as a comparison baseline; don't build on it.

### Scorecard

| Criterion | A: Python, code-driven | B: TypeScript, code-driven | C: Agent loop |
|---|---|---|---|
| Enforces INV-3 and step order structurally | Yes | Yes | No (prompt only) |
| Reuses rules tooling and sims | Fully | No | Fully |
| Model calls per rolled turn | 4–5 | 4–5 | 10–25 |
| Deterministic replay | Yes | Yes | Hard |
| Path to a hosted web app | FastAPI + HTML | Native | FastAPI + HTML |
| Time to first playable scene | Medium | Slowest | Fastest, then stalls |

**Recommendation: Option A.**

## 3. Decisions by topic

### R1. Engine language and runtime

- **Decision:** Python 3.11+ (the floor already in the tooling branch's `pyproject.toml`), synchronous
  code in the engine, `asyncio` only at the edges if the web app needs it. Standard library plus
  Pydantic v2 and PyYAML in the engine core.
- **Rationale:** Section 2. The engine is I/O-bound on model calls; Python's speed is not a factor.
  Keeping the core synchronous makes replay and tests simple.
- **Alternatives:** TypeScript (Option B); Rust or Go for a "fast deterministic core" (no performance
  need, and it would split the codebase).

### R2. Which LLMs, in which roles

| Role | Steps | Pick | Fallback | Why |
|---|---|---|---|---|
| **Reader** (A1) | T2 classify; PARSE, GATE, NECESSITY per beat; Oracle odds for fact questions | Gemini 3.8 Flash, thinking `low` | Gemini Flash-Lite after evals | Short closed-list choices; latency matters before the OFFER |
| **Framer** (A2) | ANCHOR choice and deltas; FRAME fields (attribute, deed tag, obstacle, levers, snags, stakes, lethal, reach, threatened and alternate cost, method consequences, secret) | Gemini 3.8 Flash, thinking `low` | thinking `medium` if evals show it pays | The hardest judgments; still all closed lists |
| **World** (W, only when needed) | T5 NPC want/refusal flags and the action-table context | Gemini 3.8 Flash, thinking `low` | — | Skipped when nobody present needs to respond |
| **Narrator** (B, D) | T7 draft and T8 mention list; redrafts | Gemini 3.8 Flash, thinking `low` | Claude Sonnet 5.5 if prose quality needs it (then the checker must move to a non-Claude family) | Cheapest capable model; the prototype already uses it |
| **Checker** (C) | T9 claim extraction; T10 screen flags | **gpt-oss-120b** via an OpenAI-compatible host (Groq by default) | Claude Haiku 4.5 | Must not be Gemini-family (P13). Extraction recall is the ceiling on correctness, so the slice measures recall and picks the cheapest checker that meets the target |

- **Rationale:** Jake already has a Gemini key and moved the prototype off paid Anthropic usage. The
  rules make the model's job closed-list classification plus prose, which Flash does well. Persona-free
  prompts for the Reader and Framer (CoC-Seduce, cited in the earlier report: agreeable personas raise
  sycophancy); only the Narrator has a voice.
- **Alternatives:** all-Claude (Sonnet narrator, Haiku framer, then a Gemini or gpt-oss checker; about
  2–3× the cost); all open-weight (cheapest, weaker prose, more hosting work); a single model for every
  role (violates P13 for the checker).
- **Price watch:** Gemini 3.8 Flash doubles on 2027-01-01. Model ids are pinned in config and every
  swap goes through the eval set first.

### R3. How the models are called

- **Adapters.** One small interface, `StructuredModel.call(role, packet, schema) -> (object, usage)`,
  with two implementations: `GeminiAdapter` (`google-genai`, already pinned at 2.25.0) and
  `OpenAICompatAdapter` (the `openai` SDK pointed at Groq, OpenRouter, or a local Ollama/vLLM server).
  A third, `ReplayAdapter`, returns recorded outputs so tests and replays never call a paid model.
- **Structured output.** Every call returns JSON constrained by a JSON Schema the engine builds per
  turn (Pydantic `create_model` → `model_json_schema()`), with enums for every id, rung and option.
  Gemini enforces the schema server-side (`response_json_schema`); the OpenAI-compatible path uses
  `response_format={"type": "json_schema", "strict": true}`. The engine re-validates every response
  with Pydantic regardless.
- **Big closed lists.** The tag tree (`tags.yaml`, 232 KB) is far too big for one enum. Deed tags are
  chosen in two stages: the anchor's own `deed_tags` and their ancestors first (usually under 20), and
  a branch-then-leaf shortlist only when the anchor lists none.
- **Invalid output.** One re-ask naming the failure (the same pattern as `frame_check` refusals, PR-01-2),
  then the rule's stated default when it has one, else a recoverable turn error with nothing written.
- **Thinking.** Always set explicitly (`low` by default); Flash's default `medium` was measured at 13 s
  to first token.
- **Caching.** Prompts are ordered stable-first: role instructions → always-loaded core → loaded cards →
  narrator view → last four exchanges → this message. The core plus role instructions is about 3–4k
  tokens; implicit caching needs a prefix of at least 4,096 tokens, so the slice measures hit rates and
  tries explicit cached content if implicit caching misses.
- **Refusals and safety.** A safety block or refusal from any provider is a recoverable turn error,
  logged under moderation, never under consistency (P13 keeps the two apart).
- **Budget.** Every call's tokens and cost go into the turn record; a per-session cap (default $1)
  stops play cleanly.

### R4. State storage

- **Decision:** One SQLite file per campaign (WAL mode, standard library `sqlite3`). An append-only
  `events` table is the source of truth. The current state is a projection: typed Pydantic objects for
  the 00.6 state families, rebuilt by replaying events and snapshotted at every `scene_end`. A small
  number of index tables (facts by subject and predicate, rulings by signature) are maintained
  alongside for queries.
- **Rationale:** Save, resume, branch and replay all fall out of an event log (copy the file, or replay
  to a sequence number). `revert_writes` (00.14.2 #36) becomes compensating events. Facts carry
  `valid_from`/`valid_to` and `source_event`, so "what was true at time T" and the six fact sources of
  00.6.7 are queryable. A campaign of thousands of turns is about 10⁵–10⁶ events, trivial for SQLite.
- **Alternatives:** Postgres with JSONB (the move when hosting many players on more than one server; the
  event schema carries over unchanged); a graph database (relationships are fact rows; no need);
  Graphiti-style model-extracted memory (makes state non-deterministic, against 00.6.9).

### R5. Rule-card retrieval

- **Finding:** only anchors are compiled today (`data/anchors.yaml`, 129 anchors). There is no compiled
  rule-card file, and only 88 rules use the full template with a `Loads in:` line.
- **Decision:** A build step, `engine/build/compile_cards.py`, reads the chapters through `rq.py`'s index
  (read-only; `rules/` is not modified) and writes `engine/build/cards.json`: the 00.15.2 RuleCard record
  for every numbered rule, keyed by id, with `loads_in`, `trigger` and `anchor` filled where the source
  has them. It records a hash of each source file so tests fail when cards are stale.
- **Key point:** the model only needs cards for the `[J]` decisions it is making. `[D]` rules are executed
  by code and never need to be in a prompt. So the packet per call is: the always-loaded core, the cards
  for that call's pipeline steps, the anchor candidates' cards (A2), cards whose `Loads in` matches the
  scene's situation tags, and the cards of fired triggers, in the 00.15.4 priority order under the cap.
- **Per-call packets:** A1 and A2 each get their own packet under the 12-card cap. 12.2.4 says "each
  turn"; splitting by call is an interpretation that should be confirmed in the rules (open question
  below). Fuzzy retrieval (FTS5, embeddings) is deferred until a case needs it.

### R6. Deterministic engine for `[D]` versus model judgment for `[J]`

- **Decision:**
  - Every `[D]` rule the slice touches is code with a `# rule: <id>` comment and, where a worked example
    exists, a golden test (WE-00-1, WE-00-3, WE-00-4, WE-00-5, WE-01-1 to WE-01-20 as they apply).
  - Every `[J]` decision is a field in one model call's schema, carrying its rule id, its closed option
    list and its default-when-uncertain, so the engine can apply the default when the model abstains.
  - The model's output is a proposal; code validates it (`frame_check`, PR-01-2) and commits it as events.
  - A coverage report (`engine/build/coverage.py`) lists each rule id the slice implements, defers or
    leaves to the model, so a rules change shows which code is stale.
- **Rationale:** This is the split 00.14.3 and 01.1.4 already specify; the coverage report makes it
  auditable as the rules keep changing (5 MAJOR issues open).
- **Finding:** T-01-3 and T-01-10 name `odds01.py` and `oracle01.py` as their canonical sources, but
  neither script is in the repository. The slice tests the engine against the tables themselves and
  against `data/resolution.yaml`. Worth a ledger row in the rules (not changed here).

### R7. The event loop from `data/boundaries.yaml`

- **Facts:** 105 handlers in 14 owner blocks; 9 phases; 8 time boundaries and 16 event boundaries;
  `scene_end` has 15 handlers, `beat_end` 4, `scene_start` 5, plus 3 wildcard handlers.
- **Decision:** A `Scheduler` loads the registry and dispatches to Python functions registered by
  handler id (`@handler("h.01.ruling_log")`). On load it checks that every id in the YAML is either
  implemented or on the slice's deferred list; a deferred handler logs a `handler_skipped` event each
  time it would run, so gaps are visible, never silent. `advance_time` computes every boundary crossed,
  orders them per 00.7.6 (event boundaries first, then time boundaries smallest to largest), runs all
  nine phases for each, and halts on an interrupting handler with the remainder returned (00.7.8).
  Handlers return events; they never write state directly.
- **Slice handlers:** `h.00.durations`, `h.00.clock_auto`, `h.01.ruling_log`, `h.01.scene_cleanup`,
  `h.12.inconclusive_streak`, `h.12.scene_test`, `h.12.npc_memory`, `h.12.bookkeeping` (the steps that
  touch slice state), `h.15.patience_reset`. Everything else is deferred and logged.

### R8. Porting the generators from the Python sims

- **Decision:** Each generator becomes an engine module that reads its `data/gen_*.yaml` and draws from a
  named RNG stream. The sim script is the reference implementation. Parity is tested two ways: exact
  (same seed, same draw order, same output) where the sim's draw order can be mirrored, and
  distributional (the same summary statistics as the sim's committed output, within tolerance) where it
  can't. The shared gate→fill algorithm (00.11) is ported once and configured per domain.
- **Order:** Oracle and `roll_table` (in the slice) → NPC generation (PR-12-5) → world seed (12.16) →
  loot, gifts, birth variance, crafting, item abilities.
- **Rationale:** Matches the rules' own claim that generators are table-driven; using `random.Random`
  (section 1) is what makes exact parity possible.

### R9. Player interface

- **Decision:** The engine exposes one session API (`start`, `submit`, `answer`, `save`, `resume`; see
  [contracts/engine-api.md](contracts/engine-api.md)). The slice's interface is a plain terminal REPL over
  it: fiction text, then out-of-fiction blocks, and numbered choices at pause points
  ([contracts/cli.md](contracts/cli.md)). The next interface is a FastAPI app serving HTML with htmx and
  server-sent events: a "thinking" indicator while the turn runs, then a typewriter reveal of the checked
  text, buttons for pause-point choices, and a codex side panel (P7, ch.14).
- **Delivery UX:** T9 checks the draft before delivery, so raw tokens can't stream to the player. The
  design is "thinking indicator, then reveal". Streaming with post-hoc correction would need a rules
  change to 12.3.
- **Alternatives:** Textual TUI (good, but thrown away when hosting); a React SPA (more than needed until
  the codex grows); Discord bot (multiplayer-shaped, against Principle IV).

### R10. Hosting for remote players

- **Principle IV holds:** remote players each play their own single-player campaign. No shared worlds or
  co-op in v1.
- **Path:** (1) local CLI (this slice); (2) the FastAPI app on Jake's machine via Remote Control for
  playtesting; (3) one small VPS (Hetzner or a Fly.io machine, a few dollars a month) running the app
  behind Caddy for TLS, one SQLite file per campaign on a persistent volume, continuous backup to object
  storage (Litestream, status to verify, or a nightly snapshot), invite-only sign-in (magic link or
  Cloudflare Access), API keys server-side only, per-player daily spending caps; (4) only at dozens of
  concurrent players, Postgres and more than one app server, with the same event schema.
- **Rationale:** Cheapest thing that works for a private alpha; nothing in the slice has to change to get
  there because the session API is the boundary.

### R11. Testing, evaluation and observability

- **Unit and golden tests** (pytest, no network): frame computation, the degree rule, odds enumeration
  against T-01-3, Oracle thresholds against T-01-10, cost severities, scheduler ordering, claim verdicts,
  and the worked examples with fixed dice.
- **Contract tests:** every model-call schema built for a recorded state is valid JSON Schema and
  accepts its recorded outputs.
- **Replay tests:** recorded sessions replay to identical events with `ReplayAdapter`.
- **Seeded-error set:** at least 40 drafts with known errors, at least 3 per verdict, to measure the
  checker's recall and false-positive rate (SC-003).
- **Live sessions:** scripted personas (honest, curious, adversarial: Feature 002's harness ported), each
  capped by budget. Every live run writes a report: verdict rates, fallback rate, recall, cost, latency.
- **Observability:** the turn record (FR-024) is the trace. A `report` command summarises a session.

### R12. Constitution alignment

- **Principle I** says there is "no separate deterministic rules engine sitting outside the AI's
  control". 00-architecture's "Principle I, stated precisely" reads it as: the DM decides when to call
  the instruments and what to classify, the tools do arithmetic, dice and bookkeeping, and "nothing
  happens that the DM did not set in motion". Option A fits that reading: every step that sets something
  in motion is a model judgment; the code runs only steps the rules mark `[D]`, in an order the rules fix
  (PR-12-1 is itself `[D]`). But the constitution's own wording reads more strictly than the rules'
  reading. **Recommendation:** amend Principle I's wording to match 00-architecture when recording the
  stack (owner decision).
- **Technology Constraints** still says `TODO(TECH_STACK)` and requires it to be resolved in the first
  feature's plan. Once Jake agrees with this plan, record the stack there through `/speckit-constitution`,
  including the narrator/checker family pairing as a standing constraint.

## 4. Cost and latency estimate for the slice

Token counts are assumptions until the slice measures them. Prices are Gemini 3.8 Flash promotional
rates and gpt-oss-120b on Groq.

| Call | Input (cached / new) | Output incl. thinking | Cost now | From 2027-01-01 |
|---|---|---|---|---|
| A1 Read | 3k / 3k | 0.4k | 0.40¢ | 0.80¢ |
| A2 Frame (rolled beats) | 3k / 7k | 0.9k | 0.89¢ | 1.77¢ |
| W World (when needed) | 3k / 3k | 0.3k | 0.36¢ | 0.72¢ |
| B Draft | 3k / 5k | 0.7k | 0.66¢ | 1.32¢ |
| C Check (gpt-oss-120b) | 5k | 1k | 0.14¢ | 0.14¢ |
| D Redraft + re-check (≈30% of turns) | — | — | 0.24¢ | 0.44¢ |
| **Rolled turn** (without W) | | | **≈2.3¢** | **≈4.5¢** |
| **Talk or question turn** (A1, B, C, D share) | | | **≈1.4¢** | **≈2.7¢** |

- The slice's ceiling (SC-008) is a 3¢ median, which holds at current prices. After the 2027 price change a
  rolled turn would exceed it unless the tuning below lands, so the ceiling is re-checked then. Getting to the earlier
  report's 1¢ target needs measured caching, Flash-Lite for A1, skipping A1 on obvious turns, and
  span-level redrafts. That's tuning work after the slice.
- **Latency:** A1 ≈ 1.5 s + A2 ≈ 2.5 s → the offer shows in about 4 s. After commit: W ≈ 1 s (if run)
  + B ≈ 2 s + C ≈ 1 s → about 3–4 s, 6–8 s with a redraft. Within SC-007.

## 5. Open questions for Jake

1. **Stack:** Option A as described (Python, SQLite event log, code-driven loop, Gemini Flash for every
   role but checking, gpt-oss-120b on Groq as the checker). Agree?
2. **Checker provider:** gpt-oss-120b on Groq needs a Groq account and key (pay-as-you-go, cents per
   session). The alternative is Claude Haiku 4.5 on an Anthropic key at about 7× the checking cost.
3. **Constitution:** OK to amend Principle I's wording and fill in Technology Constraints once you agree?
4. **Rules questions** (for the rules thread, not changed here): per-call packets under the 12-card cap
   (R5); the missing `odds01.py` and `oracle01.py` (R6).
