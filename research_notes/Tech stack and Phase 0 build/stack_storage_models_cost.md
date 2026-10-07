# Stack, storage, models and cost

Research date: 2026-10-07. Gathered by a research subagent.

## How reliable these numbers are

The proxy blocked ai.google.dev, openai.com, fly.io and pydantic.dev, so not every source could be read directly.

- **Claude prices:** taken from Anthropic's own reference (snapshot 2026-09-25).
- **Gemini, OpenAI and open-weight prices:** taken from news coverage and price trackers. Where they are uncertain they are marked **[unverified]**.
- **Package versions:** checked on PyPI on 2026-10-07.

## Recommended stack

| Layer | Recommendation | Runner-up |
|---|---|---|
| Server | **Python 3.11+ with FastAPI**, streaming over SSE | TypeScript/Bun with Mastra or Vercel AI SDK 6 |
| LLM orchestration | **Pydantic AI 2.54.0** behind our own thin `Narrator`/`Verifier` interface | Raw provider SDKs |
| Storage | **SQLite in WAL mode, one file per campaign**: an append-only event log plus tables rebuilt from it (projections); FTS5 for text search; numpy or sqlite-vec for vectors | Postgres with JSONB, pgvector and ParadeDB `pg_search` (Neon/Supabase) |
| Graph DB | **Not needed**: store relationships as fact rows and walk them with recursive SQL | Graphiti on FalkorDB, only if graph queries become central |
| Rules retrieval | Filter by tag and anchor, then FTS5 keyword search and embeddings, merged with reciprocal-rank fusion, then a reranker; a cached "core rules" block goes in every call | Same, using Voyage rerank-2.5-lite |
| Narrator | **Gemini 3.8 Flash** with `thinking_level=low` | Claude Sonnet 5.5 |
| Verifier | **Claude Haiku 4.5**, a different model family from the narrator | GPT-5.6 Luna [unverified] |
| Classifier | Rules or regex first, then a cheap model | |
| Frontend | **Textual TUI**, served in a browser via `textual-serve`, then FastAPI + SSE with htmx or SvelteKit | Tauri 2 desktop app with a Python sidecar |
| Observability | **Logfire**: free for 10M spans a month | Langfuse (acquired by ClickHouse, January 2026); Phoenix |
| Hosting | Local CLI first, then a small VPS or a Fly.io machine with SQLite on a volume, plus off-box backups | Cloud Run with Neon (Cloud Run's disk doesn't persist) |

## Orchestration notes

- **Pydantic AI:** typed tools, validated output with automatic retry, many providers, fallback models, and optional durable execution through Temporal, DBOS, Prefect or Restate. Releases ship several times a week, so pin the version. Check that it exposes Anthropic `cache_control` and Gemini `cached_content`; if not, drop to the raw SDK for those calls.
- **Durable execution can wait.** A turn is a short transaction and the event log is already the checkpoint. Add DBOS later for background world-tick jobs.
- **LangGraph:** its graph state would duplicate our event store.
- **OpenAI Agents SDK and Google ADK 2.0:** each favours its own vendor.
- **Claude Agent SDK:** packages Claude Code (file and bash tools), which is the wrong shape for a game server.
- **LiteLLM: don't build on it.** Its PyPI package was compromised on 2026-03-24: versions 1.82.7 and 1.82.8 stole credentials. Pin every dependency with hashes.

## Storage sketch

Core tables:

- `events(seq, branch_id, turn_id, type, payload_json, actor, rng_seed, schema_ver, prev_hash)` is the source of truth.
- `branches(id, parent_id, fork_seq)` and `snapshots(branch_id, seq, blob)` support save, branch and rollback.
- `turns(turn_id, input, narration, model_ids, usage, verifier_verdict, trace_id)`.
- `entities(...)`.
- `facts(subject, predicate, object|value, valid_from_turn, valid_to_turn, source_event_seq, status, established_by)` follows the bi-temporal pattern borrowed from Graphiti.
- `rule_cards`, with FTS5 and vector indexes.

Notes on the alternatives:

- Kuzu (an embedded graph DB) is archived; its last release was 0.11.3.
- Graphiti 0.30.2 needs Neo4j, FalkorDB or Neptune, plus an LLM to extract facts from each episode. That makes state non-deterministic.
- sqlite-vec is pre-1.0 (0.1.9). For ~3k cards × 1024 dimensions (~12 MB), brute-force numpy search is just as good.
- A campaign of thousands of turns is roughly 10⁵–10⁶ events, which is trivial for SQLite.

## Retrieval and caching

- The full corpus is ~650–700k tokens, so it can't go in every call: 700k tokens × 2 calls costs about $0.10–0.28 per turn, and slows responses.
- A 20–50k-token core block can be cached. Each cached read costs:
  - Gemini 3.8 Flash: $0.075 per 1M tokens on promotional pricing, $0.15 from 2027-01-01. Implicit caching applies at a minimum of 4,096 tokens.
  - Claude: reads cost 0.1× the base input price; writes cost 1.25× (5-minute cache) or 2× (1-hour cache).
- Embedding the whole corpus once costs under $0.15 with any current model.
- Reranking: a local bge-class cross-encoder, or Voyage rerank-2.5-lite at about $0.0002 per turn.

## Prices (per 1M tokens: input / cached / output)

| Model | Input | Cached | Output | Notes |
|---|---|---|---|---|
| Claude Sonnet 5.5 | $2 | $0.20 | $10 | Anthropic reference, 2026-09-25 |
| Claude Opus 5.5 | $4 | $0.20 | $20 | |
| Claude Haiku 4.5 | $1 | ~$0.10 | $5 | |
| Gemini 3.8 Flash (released 2026-09-02) | $0.75 | $0.075 | $3.75 | Promotional pricing until 2026-12-31; from 2027-01-01, $1.50 / $0.15 / $7.50 |
| Gemini 3.1 Flash-Lite | $0.25 | — | $1.50 | [unverified] |
| GPT-5.6 Sol / Terra / Luna | $5 / $2 / $0.20 | — | $30 / $12 / $1.20 | [unverified] |
| DeepSeek V4 Flash | $0.14 | $0.0028 | $0.28 | Hosted in China |
| gpt-oss-120b on Groq | $0.15 | — | $0.60 | |
| gpt-oss-120b on Cerebras | $0.35 | — | $0.75 | |

## Latency

- **The biggest trap.** Gemini 3.8 Flash with its default (medium) thinking measured **13.3 s to first token**, against a class median of 3.0 s. It outputs about 300 tokens per second.
- **Set the thinking level explicitly.** The `minimal` level was removed, so requests that ask for it fail.
- **Targets:**
  - classify and retrieve: under 400 ms
  - adjudicate: under 3 s
  - first narration token: under 3 s after the outcome is resolved
  - whole turn: under 10 s

## Evals and observability

- **Golden-session replay:** seeded randomness plus stored model outputs turns the game engine into plain pytest regression tests.
- **Counterfactual replay:** re-run recorded player inputs against a new prompt or model, and score contradiction rate, adherence to the deterministic rules, verifier flag rate, and cost and latency.
- **Use a different model family for judges too.** Judges favour their own family (arXiv 2502.01534 and arXiv 2609.17857), so evaluation judges need a different family from the narrator, just as the verifier does.

## Hosting

| Option | Cost | Notes |
|---|---|---|
| Fly.io shared-cpu-1x, 256 MB | ~$2–2.50/month, plus $0.15/GB/month for volumes | |
| Hetzner CX23 | ~€5.49/month | Price rose twice in 2026 |
| Litestream for SQLite backups | — | Current status unverified |
| Cloud Run | 2M requests/month free | Only sensible if we use Postgres |

Auth: Cloudflare Access or Tailscale for a private alpha. For public users, Supabase Auth or Clerk with per-user spending caps.

## Risks

- **Prices change under us.** Gemini Flash doubles on 2027-01-01, and three Flash versions shipped in six weeks. Pin model IDs and run evals before any model swap.
- **Thinking tokens.** They drive both latency and cost; track them per call.
- **Model-driven state drift.** The model only proposes changes; code validates them and commits them as events.
- **Verifier false positives.** Measure them.
- **Supply chain.** The LiteLLM compromise, archived Kuzu and pre-1.0 sqlite-vec are reasons to keep dependencies few and pinned.
- **Safety refusals on fantasy violence.** Claude 5.x returns a `refusal` stop reason, and Gemini has its own safety filters. Handle refusals with a fallback, and keep moderation separate from consistency checking.
- **Unverified prices.** Check them against the official pages before committing to a model.
