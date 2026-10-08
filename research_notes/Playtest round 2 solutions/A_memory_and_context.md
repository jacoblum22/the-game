# A. Memory and context selection (playtest round 2)

Research date: 2026-10-07. Lane A of four (B: narration and claim checks, C: content contract and NPC agency,
D: adjudication and difficulty). This note builds on
`research_notes/Tech stack and Phase 0 build/memory_and_consistency_state_of_the_art.md` and does not repeat it.
Sources were fetched through Exa. Figures marked *(verified)* were read on the primary page during this pass.
Figures marked *(Exa summary)* come from an Exa deep-research summary that cites the primary URL, and should be
re-checked before anyone quotes them.

## 0. Summary

The design is already the one the field has converged on: canonical store, closed packet, scene-scoped view,
four verbatim exchanges, summaries never summarized again. What failed in the playtests was not "memory" in the
chat-history sense. Three specific holes caused the failures:

1. **Incidental description is never written down.** When the narration describes an entity that already
   exists, everything it implies about that entity is dropped (`engine/dm/mentions.py::_one` returns on reuse).
   The next turn re-improvises the detail and contradicts it (P-063, P-073, P-127). The narrator also has only one
   or two stored descriptors per entity, so it reuses them every turn (P-030, P-094).
2. **Nothing outside the scene reaches any role.** When the player names an absent NPC, that NPC's record goes
   to no role, Checker included, so the name gets improvised (P-085).
3. **Ranking is "newest 40 facts"**, plus special cases bolted on as the problems appeared (written words, the
   object window).

The fix is an entity-profile memory with **established details**, a **spotlight set** built from mentions,
**salience-ranked budgets**, structured **scene cards** for episodic recall, and **different views for different
roles**. All of it is deterministic code over the store, with no new model calls. Long-horizon play (hundreds
of sessions) was **never exercised**: every run was 15 play turns. A seeded long-horizon regression has to come
first, or none of this can be measured.

## 1. The problem, and what the packet builder does today

### 1.1 Current pipeline (as read in code)

- `engine/dm/packet.py::build_packet` builds every packet in this order: role instructions → core (00.15.4
  cards **plus the active-trigger list**) → ≤12 cards → view → last 4 exchanges → message.
- `scene_view` (12.2.4 item 3) contains:
  - `scene_scope` (`engine/retrieve/scene.py`): the PC, the cast present, the place, and the 12 newest things
    lying there (plus any thing with written words);
  - `scene_facts`: narrator-visible facts about the scope, **newest first, capped at 40**, with written-word
    facts exempt from the cap (P-110);
  - up to 8 clocks and 8 threads (names only);
  - a "known cast" list: the 12 people the PC knows by name, **most recently introduced first**, names only.
- `narrator_view` (`engine/store/views.py`) strips seals, `truth`, and hidden clocks, and applies name knowledge
  (12.10.2).
- **Every role gets the same `scene_view`.** The exceptions:
  - World adds NPC motives (`roles/world.py::world_view`);
  - the Narrator adds `scene_setting` plus `freshness_lines`;
  - `checker_ids` is the scene scope plus entities created this turn.
- Freshness (12.14.11) is a regex pass over the text of the last 10 deliveries (`roles/narrator.py::_freshness`).
  It lists repeated openings, images, and NPC speech openers. No usage data is ever stored.
- NPC memories (12.11.7) are stored as `memory.<n>` facts on the NPC, so they reach the view through
  `scene_facts`.
- Write-on-mention (`mentions.py`) creates new npc/item/object/place entities with their implied properties. **An
  existing entity is reused and its implied properties are discarded.**

**Replay measurements** (offline model, 38 turns; `tests/replay/games/offline_seed11.json`, my script):

| Role | Median packet size | Instructions+core+cards identical to the role's previous call |
|---|---|---|
| Narrator | ~61k chars | 94% |
| World | ~57k | 80% |
| Reader | ~52k | 100% |
| Framer | ~44k | 62% |
| Checker | ~18k | 100% |
| Director | ~51k | **0%**: the core section carries the volatile trigger list, and the instructions also vary |

At roughly 4 chars per token, the big roles run about 11–15k tokens per call. SC-002 holds by construction: no
section grows with game length.

### 1.2 The observed failure classes, by mechanism

| Issue | What happened | Mechanism |
|---|---|---|
| P-063 (open) | Samkin's iron rings "catch the light", then "no rings catch the light"; the rings repeat every turn | The store holds only `detail: iron rings`. The narrator embellishes (moving or still, catching light or not), and the embellishment is unchecked atmosphere or dropped as an implied property of an existing entity. The one stored descriptor is all it has to say about her, so it repeats. |
| P-127 (open) | A guard "swings wildly", then answers calmly; a pinned man "turns his face to the wall" | No transient per-entity state (posture, hold, agitation). The only memory of the scuffle is the verbatim window. |
| P-073 (fixed by patch) | A pendant is in her palm, then not in her hand | Holder now written on mention (3c6cbbf). This is one instance of the general hole above. |
| P-085 (open) | Captain Tibine de Morois is called "Vesas de Morois"; a horse appears from nowhere | Tibine was not in scope when the player asked about her and the figure on her coat. Her record went to no role, and `checker_ids` could not attribute the claim. |
| P-037 (open) | A named NPC drifts back to "a woman" | Name state reaches the narrator only while the NPC is in scope. The known-cast list is names only and not linked to the prose. |
| P-041 / P-110 (fixed by patch) | A notice's words contradicted, then left the window | Patched by special-casing `WRITTEN` predicates in both `scene_scope` and `scene_facts`. This is a pin bolted onto a newest-first ranking. |
| P-030 / P-078 / P-094 | Scene details, an NPC's stock line, and a notice's lettering line repeat | Thin records combined with "describe the place from this" means the same words come back. Freshness (regex over prose) caught images and dialogue but not object text, because written words are always injected. |
| P-095 (fixed by patch) | Narrated cast not in the store | `position_set` on reuse (e17a4f9). The root cause is openings narrating beyond the seed; that belongs to C. |

**Latent issues found while reading the code** (not yet seen in play, but they will appear in long play):

- `scene_facts` does not filter archived NPC memories. 12.11.7 says only the five active memories go in the
  packet.
- The newest-40 cap will push early established facts about the PC or place out during a long scene.
- The known-cast list ignores the 12.6.6 weights.
- The trigger list in the core section breaks the cached prefix (see 4 below).

### 1.3 Key tension (I-127)

Atmosphere is free and unchecked, and that is correct (DL-12-37). But a detail that names an addressable
feature of an existing entity, such as rings, a scar, a posture, or a coat, is not atmosphere under 12.3.1's own
test. Today it falls through anyway: it is neither extracted as an `identity` claim against a stored field nor
written on mention. **Write those details down and check later prose against them. Atmosphere stays free.**

## 2. What the field does

**Engine-owned canon is the consensus. Prose memory is a derived layer.**

- Latitude's Voyage: "Voyage's World Engine sits atop the AI as an impartial judge, governing world state…"
  The figure of "thousands of turns" is a marketing claim with no published test. <https://latitude.io/>
  *(Exa summary)*
- Orchestrated Reality (arXiv 2606.16014) validates only what is in its schema. It reports "an NPC's missing
  finger swapping between left and right hand across a 24-turn session", and concludes that closing the gap
  needs "either richer entity schemas or a downstream consistency guard". <https://arxiv.org/html/2606.16014>
  *(verified)*. This is exactly P-063 and P-073.

**Always-visible versus retrieved.** Letta/MemGPT keeps "memory blocks… always visible – no retrieval needed",
with character limits, and an archival store searched by tool. A read-only block that the application maintains
is the safe variant for us. <https://docs.letta.com/v1-sdk/memory/memory-blocks/index.md> *(Exa summary)*.
Our view is already such a block. The question is only what goes in it.

**Keyword lorebooks with budgets.**

- AI Dungeon Story Cards fire when their triggers appear in the input or output. Cards are prioritised by how
  recently and frequently they were triggered, under a budget split of roughly 25% cards, 50% history and 25%
  Memory Bank. The Memory Bank embeds summaries of 6-action blocks.
  <https://help.aidungeon.com/faq/what-goes-into-the-context-sent-to-the-ai>,
  <https://help.aidungeon.com/faq/the-memory-system> *(Exa summary)*.
- SillyTavern World Info offers scan depth, recursion (an activated entry can activate others), and a total
  budget: "If the budget is exhausted, then no more entries are activated."
  <https://docs.sillytavern.app/usage/core-concepts/worldinfo/> *(verified, partially)*.
- NovelAI separates insertion *priority* from insertion *position*. <https://docs.novelai.net/en/text/lorebook/>
- The lesson for us: activation by mention plus a hard budget, applied to **store entities** rather than
  hand-written lore. Recursion corresponds to our entity-graph neighbours.

**Temporal knowledge graphs.** Zep/Graphiti keeps bi-temporal edges that are invalidated rather than deleted,
and retrieves with cosine plus BM25 plus BFS and reranking. On LongMemEval-S with gpt-4o it scored 71.2%
against 60.2% for full context, using 1.6k context tokens against 115k. But knowledge-update accuracy *fell*
with gpt-4o-mini (76.9% → 74.4%). <https://arxiv.org/abs/2501.13956> *(verified)*. Our event log with
`valid_from_seq` and `superseded_facts` already is a bi-temporal fact store. **We do not need Graphiti.** We need
its retrieval idea (BFS from the entities named in a query), done over our own tables.

**LLM-extracted memory** (Mem0: ADD/UPDATE/DELETE/NOOP; A-Mem: linked notes that evolve).

- Mem0 reached a judge score of 66.9 on LoCoMo, against **72.9 for full context**, using about 1.8k tokens
  against 26k. Compression trades accuracy for cost. <https://arxiv.org/html/2504.19413> *(Exa summary)*.
- Both let a model rewrite memories. That is unsafe where code owns truth: a contradiction in dialogue may be a
  lie, not an update.
- We should borrow only the *shape*: atomic facts attached to entities, a reconciliation step, and a NOOP for
  redundant writes.

**Generative Agents.** Retrieval score = recency + importance + relevance, each normalised and weighted 1, with
recency decaying at 0.995 per hour. Reflections fire when the accumulated importance exceeds 150.
<https://arxiv.org/abs/2304.03442> *(Exa summary)*. This is a good template for ranking the view. Reflections
would be model-written summaries, so leave them out.

**Friends & Fables Memories V2.** Moved to "fewer, larger" memories, which "are now also attached to characters
and locations". It dropped the type and importance fields. <https://fables.gg/patch-notes/memories-v2>
*(Exa summary)*. Entity-attached episodes are the pattern we should copy (scene cards, P5).

**Summaries drift.**

- FlawedFictions: summarising raised detected continuity errors from 0.31 to 0.45, about +50%, even with GPT-4o.
  Dropping a causal bridge creates a contradiction without inventing anything.
  <https://arxiv.org/html/2504.11900v3> *(Exa summary)*.
- Recursive book summarisation: "policy errors at lower levels compound at each composition task".
  <https://arxiv.org/abs/2109.10862> *(Exa summary)*.
- This supports 00.6.9d as written. Any episodic layer must be **computed from events, never from prose**.

**More context is not better recall.**

- LongMemEval: GPT-4o QA scored 0.714 with the top 5 retrieved items and 0.700 with the top 10.
  <https://github.com/xiaowu0162/LongMemEval> *(Exa summary)*.
- Chroma's "Context Rot" study of 18 models, including Gemini 2.5 Flash: performance "grows increasingly
  unreliable as input length grows", and distractor effects amplify with length.
  <https://research.trychroma.com/context-rot> *(verified)*.
- NoLiMa: Gemini 2.0 Flash's effective length is 4k (41.0% at 32k against a baseline of 89.4).
  <https://arxiv.org/html/2502.05167> *(Exa summary)*.
- Google's own guide: "if you don't need tokens to be passed to the model, it is best to avoid passing them."
  <https://ai.google.dev/gemini-api/docs/long-context> *(Exa summary)*.

## 3. Ranked proposals

Every proposal below is code over the store. None adds a model call. Each one also lists the stopgaps it
supersedes (owner guidance: the playtest fixes are a baseline, not sacred).

### P1. Entity profiles with established details (highest value)

**Rules.**
- New **00.6.6a "Established details"**, cross-referenced from 12.14.13. When narration asserts a concrete
  descriptive property of an addressable entity, it is written as a `detail.<slot>` fact with `certainty:
  narrated`, `source: mention`, and a **persistence** of one of three kinds:
  - `lasting`: appearance, marks, worn or carried things, voice, build;
  - `scene`: posture, hold, agitation, where they stand, what they are doing;
  - `beat`: momentary.
- Detail **slots** form a closed list, for example `hair, face, mark, build, clothing, worn, held, voice,
  manner, posture, activity, condition_visible`, and for objects `material, state, marking`. One value per slot.
  A later write to the same slot supersedes the earlier one *only* when this turn's adjudication record holds
  an event that explains the change (she put the rings away, he was pinned). Otherwise the change is a
  contradiction.
- **PR-00-7 step 2** extends to existing entities: "for an existing entity, each implied property is compared
  with its profile. New: write it. Same: NOOP. Different: an `identity`/`position` claim failure (12.3.2)."
- **12.3.1**: the `identity` class is checked against `detail.*` facts as well as entity fields. Persistence
  `scene` details are checked against posture and position claims (P-127).
- **12.4.8** gets a new step: `scene` details expire at `scene_end` (superseded, history kept).
- Cap: at most **8 active lasting details** per entity, ranked by salience, then last used; the rest are
  archived and never lost (same pattern as the 12.11.7 memory cap).
- **12.14.13 worst case**: a narrated detail is ordinary by definition. It may be cited as a lever under the
  existing +2 / one-rung cap, and it never creates value, clues, or hazards.

**Engine.**
- `engine/dm/mentions.py::_one`: on reuse, diff the implied properties against the profile instead of
  returning. A small `slot_of(predicate)` map extends the existing `_NPC_KEYS`.
- `engine/store`: no schema change. Details are facts. Add a projection index `details[eid]` holding
  slot → fact id and last-used turn.
- `packet.py::render_view`: render a compact profile per entity in view, with stable identity, active details,
  and a `(used last turn)` mark on details the previous delivery used.
- `roles/narrator.py`: `freshness_lines` reads the `last_used` marks for images instead of re-scanning prose.
  Keep the cheap opening-clause and speech-opener regex as a backstop.

**Interfaces.**
- **B (claim checks):** if B's "narrator declares" lands, `mentions[].implied` is where details are declared.
  Undeclared descriptive sentences go to the Checker. Either way, code does the diff.
- **C (content contract):** details are the "free but persisted" tier between atmosphere and furniture. Richer
  seeds (2–4 lasting details per NPC and place) start each entity with variety, which directly cuts repetition.
- **D (adjudication):** narrated details are citable levers under the existing cap. The Framer should see the
  profile of the beat's target.

**Cost.** About 30–60 tokens per profiled entity, and no calls.

**Test.**
- Mutation tests (FlawedFictions style): flip `detail.hand` and expect an `identity` failure; move the rings
  with a recorded "puts them away" beat and expect a pass.
- A replay of the P-063, P-073 and P-127 transcripts.
- The OEQ-00-6 measure (narrated-but-unrecorded elements per turn, target ≤2%), extended to details.

**Supersedes.**
- P-073's holder-on-mention special case (3c6cbbf). It becomes `detail.held` plus possession.
- The image half of P-030 and P-078's freshness regex (74f7749, 3c6cbbf). Usage marks replace it; the regex
  stays only as a backstop.
- The `_DESCRIPTIVE_KEYS` ordering hack in `packet.py`.

### P2. Spotlight set: mention-driven scope expansion

**Rules.** 12.2.4 item 3 adds that, beyond the scene, the view includes up to **K = 4 spotlight entities**,
chosen deterministically:
1. entities named or aliased in the player's message;
2. the target of the Reader's beat;
3. entities named in the last delivery;
4. the scene agenda's thread and its linked entities;
5. one hop of relationship neighbours of the above, when the budget allows (the World Info "recursion" idea).

A spotlight entity is rendered **as the PC knows it**: name or unnamed label, profile, the PC's knowledge
records about it, and its last scene card. World truth is never rendered for it. Sealed entities show their
slice or nothing (INV-10).

**Engine.**
- New `engine/retrieve/scene.py::spotlight(state, message, last_delivery, beat)`. It uses an alias index built
  from entity names, aliases and roles; `find_existing` in `mentions.py` already does the matching.
- `scene_view` takes a `spotlight` argument.
- `checker_ids` includes the spotlight, so P-085's "Vesas" claim is attributed to Tibine and judged.

**Interfaces.**
- B: the Checker can judge claims about absent people.
- C: the I-153 "who is X" answers land as knowledge records that the spotlight then surfaces.
- D: the Reader can resolve targets that are not present ("I send word to the captain").

**Cost.** At most about 400 tokens.

**Test.** The P-085 replay. A probe set: name an absent NPC, then check that their name and pronoun are
correct and stay correct.

**Supersedes.** The "first-name matching" stopgap listed in HANDOFF section 5 is folded into the alias index,
and part of P-037.

### P3. Salience-ranked, token-budgeted view (replaces "newest 40")

**Rules.** 12.2.4 item 3 states a ranking, and `pacing.yaml#packet.view_budget` states per-section token
budgets. These are budgets, not item counts.

- **Pinned** (always shown, own budget): identity fields; written words; open commitments involving anyone in
  view; **active** NPC memories (12.11.7); conditions and quantities in view; the open pause.
- **Ranked** (fills the rest): `score = salience + recency + relevance + adjacency`.
  - Salience: memory salience 1–3; commitment 3; `lasting` detail 1; `scene` detail 2 while its scene runs.
  - Recency: decay per scene, not per turn, so a long scene does not starve the start of the scene.
  - Relevance: +2 when the fact's subject or value is in the spotlight or the beat.
  - Adjacency: +1 for a relationship to anyone present.
- The known-cast and thread lists are ordered by **12.6.6 weights**, not by introduction order.

**Engine.**
- `retrieve/scene.py::scene_facts` becomes `ranked_facts(state, scope, spotlight, budget)`.
- Filter `memory.*` facts whose `status` is archived.
- `packet.py`: reuse the per-section budgets already implied by `MAX_VIEW_*`.

**Interfaces.** Any role that reads the view gets the same ranking.

**Cost.** Neutral, or a little smaller.

**Test.**
- SC-002 at age: build a synthetic store with 300 scenes of events (offline model, seeded) and assert that the
  view's token count at the 95th percentile stays flat.
- Assert that pinned items are always present.

**Supersedes.**
- The `WRITTEN` exemptions in `scene_facts` and `scene_scope` (P-110, P-041 be20402). They become pins.
- The `MAX_SCENE_OBJECTS` carve-out.
- The implicit "most recently introduced" known list.

### P4. Scene cards: an episodic layer computed from events, not from prose

**Rules.**
- 12.4.8 step 8 is extended. Closing a scene writes a **scene card**, a *view* over the scene's events and not
  a summary: `{scene, place, time, cast, agenda → answer, beats [(actor, verb, target, degree)], facts written,
  memories committed, threads touched}`. The chronicle line stays as it is (11.12).
- 12.5.3: a recap reads the scene cards and the chronicle. Never a previous recap.
- 00.6.9d holds by construction: a card can be regenerated from the log, and nothing is ever summarised again.
- The Narrator and World views get **at most 2 scene cards**: the most recent card involving a spotlight or
  present entity that falls *outside* the 4-exchange window ("last time you met the captain…").

**Engine.**
- `engine/world/scenes.py` builds the card at `scene_ended` as a projection, stored in `meta` or as a derived
  table.
- `retrieve/` gets `cards_for(entity_ids, k=2)` with entity overlap, then recency.
- BM25 or embeddings only if campaigns outgrow id overlap. Do not add them now.

**Interfaces.**
- B: card lines are store-backed, so the narrator may state them.
- C: NPC memory voicing (12.11.7) gets the deed's context.
- D: none.

**Cost.** About 150 tokens per card, so 300 at most.

**Test.**
- Recall probes at 50, 200 and 500 turns ("what did I promise Tibine?"). Score supported precision and
  coverage separately (LoCoMo-style).
- Assert that the recap never cites a sentence with no event behind it.

**Supersedes.** Nothing. It removes the pressure to widen the verbatim window (OEQ-12-1: keep 4 unless
T-12-WINDOW says otherwise).

### P5. Role-differentiated views

**Rules.** Add a table to 12.2.4 (and to contracts/model-calls.md) saying what each role sees, respecting the
12.10.1 layers:

| Role | Sees | Does not see |
|---|---|---|
| Reader | names and aliases of scope plus spotlight, the open pause, the last exchange | setting prose, details, cards beyond its own |
| Framer | target profile, positions, conditions, levers (established details of the target and place), anchors | setting prose, cast list |
| World | world truth for present NPCs minus seals: motives, memories, knowledge; off-screen clocks; scene cards | freshness, setting prose |
| Narrator | **PC-knowledge layer only**: setting, profiles with usage marks, record, spotlight as known, ≤2 scene cards | motives, `truth`, background facts |
| Checker | compact profiles for claim ids (scope, spotlight, created), the draft | rule cards outside 12.3, setting |
| Director | threads, clocks, cast weights, scene cards | verbatim exchanges beyond 1 |

**Engine.** `packet.py::view_for(role, state, ctx)` builds the role-specific view. `build_packet` is unchanged.

**Interfaces.** C's default NPC layer runs on the World view. D's code-chosen gates (theme D) shrink the Reader
view further.

**Cost.** Likely a 20–40% cut for the Reader, Framer and Checker, though this needs measuring.

**Test.**
- Per-role packet golden files.
- A leak test: no Narrator packet contains a `truth`, motive or sealed string (INV-10, extended).

**Supersedes.** Nothing directly. It is a prerequisite for B's smaller Checker.

### P6. Cache-aware layout on Gemini Flash

**Pricing** (`gemini-3.8-flash`, the model in `engine/llm/budget.py`), from
<https://ai.google.dev/gemini-api/docs/pricing> *(verified)*:

- $0.75 per million input tokens, $0.075 per million cached, $3.75 per million output (thinking included),
  through 2026-12-31;
- **all three double on 2027-01-01**.

**Implicit caching** is on by default, has a **4,096-token minimum** for 3.x Flash, and is prefix-based. Google
advises putting "large and common contents at the beginning" and sending similar prefixes close together in
time. <https://ai.google.dev/gemini-api/docs/caching> *(verified)*.

**Cost per turn** (estimate: about 75k input tokens across Reader, Framer, World, 1.8 Narrator calls and 1.8
Checker calls; about 2k output):

| | 2026 prices | From 2027 |
|---|---|---|
| No cache hits | about 6.4¢ | |
| 60% of each packet served from cache | about 3.3¢ | about 6.6¢ |

Caching, smaller role views, and minimal thinking are what keep play inside the owner's 1–3¢ target.

**Rules.**
- 00.15.4 / 12.2.4: the active-trigger list moves **out of the core section** to the head of the view. Its
  content is unchanged; only its position moves, for caching (record a DL entry).
- Cards are ordered from stable to volatile: role cards → situation cards → trigger and anchor cards.

**Engine.**
- `packet.py::render_core` drops the triggers, which are emitted with the view.
- Order cards by stability in `retrieve/cards.py::load_cards_for`.
- Log `tokens_in_cached` per role; the field already exists in `engine/llm/base.py`.
- Set the thinking budget per role: minimal for the Reader and Checker.

**"Just put more in" with a ~1M window?**
- Not for the Narrator. Truth-gating needs the PC-knowledge layer, not the world. Distractors measurably hurt
  (Chroma, NoLiMa). Canon changes every turn, so a big prefix stops being cacheable after the first write.
  Reading 200k tokens from cache on every call would cost about 1.5¢ per call before anything else.
- A large *cached static gazetteer* (seed places, factions, NPC public fields) may suit the
  **World/Director** roles at scene boundaries. That is an experiment, not a default.
- Fiction.LiveBench (secondary transcription) puts Gemini 2.5 Flash at 77.8 at 16k and 68.8 at 120k.
  Scores for the 3.x Flash models were not verified.

**Test.** A cache-hit rate per role at or above 60% over a replay run on the real model (owner-run).

**Supersedes.** Nothing.

### P7. Transient beat state (part of P1, listed so it is not lost)

P-127 needs `scene`-persistence details (posture, hold, agitation) written **from the resolved beat** by code,
not by the narrator. Example: a successful grapple writes `posture: pinned` on the target. The World role's
responses (C's NPC layer) write `manner` or `activity` for each present NPC each beat. The Narrator then
renders what the record says. This shares P1's slot list and expiry. **Supersedes:** nothing yet. It replaces
the need for the narrator to infer posture from the verbatim window.

### P8. Seeded long-horizon consistency regression (do this first: it measures P1–P7)

Today's evidence covers at most 15 play turns. `specs/002` predates the engine: it ran a 12-turn cap and found
3 of 5 sessions conflict-free.

Proposal: `evals/longhorizon.py`, three modes, as in the Exa evaluation survey:

1. **Frozen replay** (existing `tests/replay`): engine regressions.
2. **Scripted live**: fixed world seed, fixed RNG, and a **scripted player** of about 300 lines covering
   revisits, absent-NPC questions, recall questions, scuffles, and reading notices. Run with the offline model
   for SC-002 and pipeline checks, and with Gemini (owner-run) for quality.
3. **Aged-state synthetic**: generate a store with N = 300 scenes of seeded events to test packet boundedness
   and retrieval without paying for 300 scenes of real play.

**Metrics** (all deterministic, or using the existing Checker):

- **Contradictions per 100 turns, by claim class**, from the Checker, the scene-end sweep (12.4.8 step 4), and
  a new offline **canon audit** that re-extracts details from every delivery and diffs them against `detail.*`
  history (P1 makes this cheap).
- **Narrated-but-unrecorded rate** (OEQ-00-6, target ≤2%).
- **Recall probes**: probes inserted at turns 50, 200 and 500, answered against the journal. Score precision
  and coverage.
- **Cross-turn novelty-4**: the share of 4-grams in a delivery that are absent from the previous 10, tracked
  separately per entity, plus the longest copied span. This replaces subjective "repeats" notes.
- **View tokens** at the 50th and 95th percentile at turns 50, 200 and 500 (SC-002).
- **Cache-hit rate**, cost per turn, and latency.
- NCP-style **survival curve** (turns to the first confirmed contradiction), reported alongside progress so
  stalling cannot score well. Context: GPT-5.2 reaches 42% survival at turn 20 with Gemini 2.5 Flash as
  auditor (<https://arxiv.org/html/2608.08160v1>, *Exa summary*).

**Mutation suite.** Inject contradicting details, a resurrected NPC, or a spent item into the store or a draft,
and require the checker or audit to name both the establishing event and the violating event (ContraDoc and
FlawedFictions style). Include valid changes as negative controls.

**Folds in** T-00-WOM (OEQ-00-6) and T-12-WINDOW (OEQ-12-1). Commit the seeded outputs, following the
project's sim habit.

## 4. The recommended per-turn context pipeline

1. **Parse** (Reader, its own small view). The message's names are resolved through the alias index, giving
   `mentioned_ids`.
2. **Spotlight** (code): `scene_scope` ∪ top-K of {mentioned_ids, the beat target, entities named in the last
   delivery, agenda thread entities, one-hop neighbours}, with seals applied.
3. **Rank and budget** (code): pinned items first, then `salience + recency(scene) + relevance + adjacency`.
   Fill the per-section budgets (`pacing.yaml#packet.view_budget`). Choose ≤2 scene cards for spotlight or
   present entities whose last scene lies outside the verbatim window.
4. **Project per role** (code, `view_for`): Narrator gets the PC-knowledge layer, World gets truth minus seals,
   and so on (P5 table).
5. **Assemble** (`build_packet`): instructions → core cards → cards ordered stable to volatile → [trigger list
   + view] → last 4 exchanges → message. Log cached tokens.
6. **Adjudicate and narrate** (unchanged pipeline). The Narrator returns prose plus `mentions[].implied`.
7. **Write back** (code, before delivery): new entities as today; for existing entities, a **profile diff**
   (NOOP, new detail, or claim failure); `last_used` marks on the details the delivery used; `scene` details
   written from the resolved beat (posture, hold).
8. **Check** (B's design) against the profiles of the scope, spotlight and created entities.
9. **Scene end** (12.4.8): expire `scene` details; commit memories; write the scene card from events; update
   cast and thread weights.
10. **Session start**: recap from scene cards and the chronicle (12.5.3), every sentence checked.

## 5. Fixes to keep, and fixes to retire

**Keep.** These are sound and general:

- name knowledge (`name_known`, `unnamed_label`, 12.10.2);
- NPCs created mid-scene joining `cast_present` (P-056);
- `position_set` on reuse (P-095), as one case of the profile diff;
- the opening-clause and speech-opener freshness regex (a cheap backstop);
- sealed-slice handling in `narrator_view` and `entity_names`;
- `scene_setting` as material, though in the long run it should render from profiles;
- NPC memory storage (12.11.7), once archived memories are filtered.

**Retire once P1–P3 land:**

- the `WRITTEN` exemptions in `scene_facts` and `scene_scope` (P-110, P-041 be20402), replaced by pins;
- the `MAX_SCENE_OBJECTS` written-thing carve-out, replaced by pins;
- holder-on-mention as a special case (P-073 3c6cbbf), replaced by the `detail.held` profile diff;
- the freshness image regex (P-030 74f7749, P-078 3c6cbbf), replaced by `last_used` usage marks. This also
  closes P-094;
- the `_DESCRIPTIVE_KEYS` ordering in `packet.py`, replaced by profile rendering;
- the newest-introduced known-cast list, replaced by 12.6.6 weights;
- first-name matching, replaced by the alias index (P2).

**Not mine to retire, but affected:**

- `settle_who`, incident binding, and the forbidden-kind keyword list belong to C's content contract. A richer
  seed plus profiles make them unnecessary.
- `fact_sentence` munging belongs to G and B. Profiles give typed fields to render from.

## 6. Rules sections to revise (summary)

- **00.6.6 / PR-00-7:** add the established-details rule; diff against the profiles of existing entities.
  Settle OEQ-00-6 with T-LH.
- **12.2.4 item 3:** spotlight, ranking, budgets, the role table, and the trigger list's position. **00.15.4:**
  the matching amendment (DL entry).
- **12.3.1:** the `identity` and `position` classes are checked against `detail.*`; define `narrated`
  certainty.
- **12.4.8:** `scene` detail expiry, and the scene card in step 8. **12.5.3:** recap from scene cards.
- **12.6.6:** the weights also order the view's cast and thread lists.
- **12.11.7:** state outright that the archived memories are excluded from the packet (the engine bug).
- **12.14.11:** freshness keyed on stored usage marks, covering object text and dialogue.
- **12.14.13:** details are ordinary, are levers under the cap, and never create value.
- **Data:** `pacing.yaml#packet.view_budget`, `#details.max_active` (8), `#packet.spotlight_k` (4).
- **New OEQs:** the detail cap and slot list; spotlight K; the budget split.

## 7. Risks and open questions for the owner

1. **Detail bloat or junk.** Persisting narrated details can store nonsense, as P-119's "familiar face"
   object did. Mitigations: the closed slot list, the per-entity cap, and refusing details whose subject cannot
   be resolved to an id. *Decide:* how wide is the slot list?
2. **Over-constraint.** Once rings are "iron rings, still", the narrator may feel locked in. The usage marks
   push towards *other* details, but a thin entity still repeats. P1 depends on C's richer seeds (2–4 lasting
   details per entity) to work well.
3. **Who writes the profile diff when B's design changes?** If the narrator declares facts, the diff uses the
   declarations. If not, the Checker's extraction feeds it, which is noisy (theme B). Sequence P1 *after* B's
   decision, or build the diff so it accepts either source.
4. **Scene-detail authorship.** Code writing posture from beats (P7) needs C and D to agree on a small posture
   vocabulary for each verb outcome.
5. **Spotlight leakage.** Rendering absent entities "as the PC knows them" depends on knowledge records being
   complete. Where they are thin, the narrator sees only a name, which is safe but terse.
6. **Gemini specifics are not verified for 3.x Flash.** No long-context, latency, or schema-adherence numbers
   were found for `gemini-3.8-flash`. The Exa summary's figures are for 2.5 and 3 Flash Preview. The owner
   should run T-LH's scripted mode once on the real model and record cache-hit rate, time to first token, and
   contradictions per 100 turns. The price doubling on 2027-01-01 makes caching and role trimming
   budget-critical, not optional.
7. **Hundreds of sessions** stays unproven anywhere in the field: no public benchmark goes beyond about 100
   interactive turns. The aged-state synthetic test is the cheapest proxy. Promote failures found in real play
   into the scripted corpus.
8. **Sequencing.** Recommended order: P8 harness (minimal) → P3 (ranking, plus the archived-memory bug) → P1+P7
   (profiles) → P2 (spotlight) → P5 (role views) → P6 (cache layout) → P4 (scene cards, which matter once
   sessions run longer than one scene).
