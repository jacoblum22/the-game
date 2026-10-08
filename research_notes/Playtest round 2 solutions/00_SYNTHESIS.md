# Playtest round 2: synthesis of the four research lanes

Written 2026-10-08. It combines four parallel research reports into one design and one build order:

- [A. Memory and context selection](A_memory_and_context.md)
- [B. Narration and claim verification](B_narration_verification.md)
- [C. Content contract and NPC agency](C_content_contract_npcs.md)
- [D. Adjudication, difficulty and presentation](D_adjudication_difficulty.md)

Each lane report holds the sources, the rule ids and the details. This note covers what the lane reports
cannot: how the pieces fit together, where they conflicted, what the owner must decide, and the order to build
in.

**Owner guidance applied throughout.** The roughly 90 playtest fixes are a starting point, not a constraint. A
fix is kept when it is a good idea and retired when it was a patch over a deeper problem (§7).

---

## 0. Bottom line

1. **All four lanes found the same root cause.** Language models are *guessing* things that code should
   *own*, and the store holds too little for code to own them:
   - the Checker guesses what the prose claimed;
   - the Reader guesses gates from 83 licences;
   - the Framer guesses difficulty with no rubric;
   - the narrator guesses what NPCs know and do;
   - incidental description is guessed again every turn because it was never written down.

   Every stopgap in the engine patches one instance of this.
2. **Memory is not a separate system to choose. It is a loop the rules already half-define.**
   - The rules decide what gets *written*: the content tiers, established details, answers, scene cards.
   - Code decides what gets *selected*: the spotlight, a salience ranking, per-role views.
   - The narrator *cites* what it used.
   - Code *verifies* the citations against the store.
   - What was established is *written back*.

   No vector database, knowledge-graph service or LLM-written memory is needed; the field evidence argues
   against them here (A §2). Every proposal is deterministic code over the existing event-sourced store.
3. **The headline playtest metric hid the real state.** The 4% fallback rate looked good, but (B §1.2):
   - 98.6% of first drafts failed the claim check;
   - only 3 of 374 turns went out as first drafted;
   - 56% of turns had sentences silently cut;
   - re-checking an unchanged sentence gave a different result 33% of the time.

   The truth gate is the right idea; it is ahead of every shipping product. Its *mechanism* is the problem.
4. **The rules already contain most of the missing machinery; the engine never runs it** (C §1, verified):
   - 12.10.6(d) settles an NPC's role knowledge by the Oracle;
   - T-15-3 makes a first question to a Neutral NPC *certain*;
   - 15.9 and PR-15-6 hold the clue graph, the Three Clue Rule and "core clues never fail";
   - but the case-building handlers are parked at M6, and `incident.py` imitates them by hand.
5. **Cost is a hidden problem.** Today's pipeline runs about 3–6¢ per turn on `gemini-3.8-flash`, depending on
   cache hits. That is over the 1–3¢ target, and **Gemini prices double on 2027-01-01** (A §P6, verified). The
   combined redesign removes roughly 1.5 model calls per turn, which is what brings it back inside budget.

---

## 1. How memory and the rules fit together

The owner's core worry is which lore, which past turns and which context to give each role, so that it never
contradicts itself and remembers what matters. The combined answer is one loop with five stages. Each stage has
a ruleset owner and an engine owner, so the rules and the memory system cannot drift apart.

```
          ┌────────────────────────────────────────────────────────────────────┐
          │                      STORE (event log = canon)                     │
          │  seed packs · established details · answers index · case graph ·   │
          │  NPC memories · scene cards (derived from events, never prose)     │
          └───▲──────────────────────────────────────────────────────┬────────┘
   5 WRITE BACK │                                                     │ 2 SELECT
   (tiers decide│                                                     ▼
    what is kept)│     spotlight → pin + rank by salience → budget → view per role
          ┌──────┴────────┐                                  ┌──────────────────────┐
          │ 4 VERIFY       │◄──── refs, kinds, new elements ──│ 3 NARRATE            │
          │ refs ∈ packet  │                                  │ one item per sentence│
          │ no contradiction│                                 │ citing record + facts│
          │ with whole store│                                 └──────────────────────┘
          └────────────────┘
   1 WRITE (at seed, in play): content tiers decide who may create what (§1.1)
```

### 1.1 One authority table: who decides what is true

This table reconciles B's P5, C's three tiers and C's I-153 Option C into a single rule. It is the most
important thing to settle, because every other piece leans on it.

| Tier | Examples | Who decides it is true | Stored? | Checked? | Retrieved |
|---|---|---|---|---|---|
| **T0 Atmosphere** | light, smell, sound, mood, an unnamed crowd's murmur | Narrator, freely | Never | Only against location, time and safety (I-127, as now) | n/a |
| **T1a Established detail** | the smith's scarred hands, iron rings, a guard's posture, a notice's lettering | Narrator, *as written* for incidental properties of things in view (B P5) | **Yes.** A `detail.<slot>` fact, with persistence lasting, scene or beat (A P1) | Later prose must not contradict it (an `identity` or `position` claim) | Profile of each entity in view; `last_used` marks drive freshness |
| **T1b Ordinary knowledge** | what an innkeeper knows about the roads, prices, local news | **Proposed** by the model, **settled by the Oracle** at 12.10.6(d) role-fit odds (C Option C) | Yes. A fact plus a knowledge record, and the "doesn't know" result is stored too | Prose must match the declared answer | Asked-and-answered index: the same question gets the same answer |
| **T1c Scene state** | each present NPC's activity, posture after a grapple | **Code**: from the resolved beat and the default NPC layer (A P7, C P4) | Yes, with scene persistence; expires at scene end | Prose must match the record line | Pinned while the scene runs |
| **T2 Consequential** | clues, culprits, secrets, people with wants, adversaries, hazards, valuable items | **Generators only**: the case builder, casting, NPC generation, tables | Yes, sealed until revealed | Strict: must be in this turn's record, or it is cut | Pinned to threads and the journal once unsealed |

**What this buys:**
- Contradictions about appearance (P-063, P-073, P-127) become checkable, because the detail is stored.
- Repetition (P-030, P-078, P-094) becomes a lookup, because the store knows which details were used last
  turn.
- "Success with nothing" (P-025, P-120) becomes impossible, because the answer ladder always ends in a fact or
  a real lead.
- Names and culprits never come from the LLM, because "who" questions go to casting.

### 1.2 What each role sees

This merges A's P5 with D's and C's packet needs. A section is a section of the view; nothing here grows with
game length (SC-002).

| Role | Sees | Never sees |
|---|---|---|
| **Reader** | the message, the last 2 exchanges, names and aliases of the scene plus the spotlight, the PC's knacks as words, the open pause | licences, setting prose, profiles |
| **Framer** (rolled beats only) | the beat; ≤4 anchor cards; the verb's obstacle-class list; ≤8 candidate facts filtered by code; stakes sources; one precedent | the PC sheet (the modifier is computed), the cast list |
| **Narrator** | the **PC-knowledge layer only**: the record with handles, profiles with usage marks, the spotlight *as the PC knows it*, ≤2 scene cards, seeded looks | motives, `truth`, sealed content |
| **Checker** (a diff audit, often skipped) | numbered sentences with their declarations rendered in words, compact profiles for the cited ids | rule cards outside 12.3 |
| **Director** | threads, clocks, cast weights, scene cards | verbatim exchanges beyond the last one |

**Selection inside the view** (A P2 and P3):

- **Pinned** (always shown):
  - identity;
  - written words;
  - open commitments;
  - the 5 *active* NPC memories;
  - scene state;
  - conditions;
  - the open pause.
- **Spotlight.** Up to 4 out-of-scene entities, chosen in this order:
  - entities named in the message;
  - the beat's target;
  - entities named in the last delivery;
  - the scene agenda's thread;
  - one hop of relationship neighbours.
- **Ranked** (fills the remaining budget): `salience + recency(per scene) + relevance + adjacency`. This
  replaces "newest 40 facts".
- **Episodic recall.** At most 2 **scene cards**: structured views of past scenes involving present or
  spotlight entities that fall outside the 4-exchange window. They are computed from events, never summaries
  of summaries, because summarising measurably *adds* continuity errors (A §2, FlawedFictions).

### 1.3 Robustness guarantees

| Guarantee | Mechanism | Measured by |
|---|---|---|
| The narrator cannot cite what it wasn't given | Refs are **enums built from the packet**, so constrained decoding enforces it (B P1) | Schema |
| Support is judged against the packet; contradiction against the **whole store** | B P1 / A | A claim true only by an off-packet fact passes but is logged as a **retrieval miss**: a free, continuous metric of A's selection quality |
| Sealed content never reaches the narrator | Per-role views plus the existing `narrator_view` seals (INV-10) | A leak test on every Narrator packet |
| The packet does not grow | Token budgets per section, not item counts | View tokens at turns 50, 200 and 500 in the long-horizon harness |
| The same question gets the same answer | Asked-and-answered index (C P2) | Ask-twice probe |
| Memory does not drift over time | Scene cards and recaps are regenerated from events; recaps never read earlier recaps | Recap sentences must each cite an event |
| Details do not bloat | A closed slot list, ≤8 active lasting details per entity, archived rather than deleted | Store size per entity in the aged-state test |

---

## 2. The merged per-turn pipeline

| Step | Who | Model call? |
|---|---|---|
| 1. Pre-route obvious out-of-fiction questions ("what do I know", journal) | Code (D keeps `_knowledge_parts`, moved before the Reader) | No |
| 2. **Read:** verb (15), target, 3 method facets, `question_kind` (6) + topic | Reader | 1 small call |
| 3. **Spotlight and views** | Code | No |
| 4. **Gate and necessity** from verb, facets, licences, class base, social certainty | Code (D P1, P3) | No |
| 5. **Frame** only if the beat rolls: obstacle class + optional one-rung nudge citing a fact | Framer | 0–1 call, skipped on trivial or certain beats |
| 6. OFFER from typed templates; roll; read the degree | Code (D P5, B P4) | No |
| 7. **World step:** default NPC layer (activity, practice, volition, the addressed NPC always answers); answer ladder for Talk/Observe/Recall | Code (C P2, P4); the World LLM only as a tie-breaker | Usually none; a ~0.1¢ proposer call when the ladder reaches rung 3 |
| 8. **Narrate:** sentences, each with refs, `about`, typed `new` elements (with `element_kind`) and an atmosphere flag | Narrator | 1 call |
| 9. **Judge:** refs resolved by `check_claims` with the subject given; deterministic scans; coverage of must-name record lines; profile diff | Code (B P1, A P1) | No |
| 10. **Audit** of undeclared assertions; skipped when everything is declared | Checker (B P2) | 0–1 small call |
| 11. **Repair** failing sentences only; after 2 rounds render the missing record lines from typed fields | Narrator (narrow) or code (B P3) | Rare, short |
| 12. **Write back:** T1 details, answers, scene state, `last_used` marks | Code | No |
| 13. Scene end: expire scene state, commit memories, write the scene card | Code | No |

**Model calls per turn:** about 4.9 today (B §1.2: narrator 1.81, checker 1.61, others 1.52). The target is
about 2.5–3: a Reader call, a Narrator call, and some of the Framer, audit and repair calls.

---

## 3. Where the lanes overlapped or conflicted, and the resolution

| Point | Lanes | Resolution |
|---|---|---|
| Established details | A P1 and B P6 are the same proposal | **Merged.** A owns the slots, caps and expiry; B's sentence declarations (`new`/`implied`) feed it; C's T1 is the tier it lives in. |
| Narrator authority | B P5 (write incidental properties as narrated) vs C Option C (Oracle settles ordinary knowledge) | **Both, split by kind** (§1.1). Description of what is in view is T1a, written as narrated. Claims about the world beyond the view (T1b) carry more weight, since they become leads, so the Oracle settles them. **One owner decision covers both** (§4, D1). |
| Who proposes the T1b answer *before* narration | C P2 suggests the World call; C P4 removes the World call | **A tiny dedicated proposer call** (~0.1¢), only when the ladder reaches rung 3 (no stored fact, nothing in the seed pack). It should be rare once seed packs land. Fallback: the narrator proposes in its declarations and a "no" triggers a one-sentence repair. |
| Reader schema | D P1 (facets) and C P2 (`question_kind`) | Compatible. One schema change: drop gate, licence, would-be licence and necessity; add 3 facets, `question_kind` and `topic`. |
| "No roll" rules | D P3 (computed necessity), C (common knowledge is a certain Talk), 15.9.5 (core clues never fail) | **One `necessity()` function** holds all three. |
| "Never offer a roll with nothing to deliver" | D P5 depends on C | Satisfied by C's ladder: rung 4 (a real lead) means success always delivers. |
| Transient posture and activity | A P7, C P4, D (verb outcomes) | **One scene-state slot vocabulary** (posture, hold, activity, manner) written by code from beat outcomes and the NPC layer. Needs a small table per verb outcome (owner: rules). |
| Price basis | C used Gemini 2.5 Flash prices; A, B and D used `gemini-3.8-flash` | Use **3.8 Flash** ($0.75 / $0.075 cached / $3.75 per M through 2026; doubling 2027-01-01), verified by A and B. C's relative savings still hold. |
| Checker scope | B P2 (diff audit) needs A P5 (role views) | Build the views first; the diff audit comes later and is gated on a measured under-declaration rate. |

---

## 4. Decisions only the owner can make

Each has a recommendation. D1–D3 block the most work.

**Owner rulings, 2026-10-08:** D1, D2, D3 and D4 accepted as recommended. D1 is the tiered split, D2 yes, D3
guardrails then rubric, D4 a reduced case builder in M1. The DL entries are to be written in the step-2 rules wave, before
the spec each one gates.

**Assumed for the overnight run, 2026-10-08, pending owner review:** the owner asked for the full plan to be
implemented unattended, so D5–D8 take their recommended defaults. Each is recorded in its DL entry as
"assumed, owner to confirm", so any of them can be reversed with a revision.

| Decision | Default taken |
|---|---|
| D5 | Support judged against the packet; contradiction against the whole store; off-packet support logged as a retrieval miss |
| D6 | Numbers plus words |
| D7 | Safe frames auto-commit by default, as a preference |
| D8 | A's slot list and a cap of 8 |

D9 (a real-Gemini run) and the Laya spike need the owner, for API spend and a Kaggle GPU account, so they are
deferred.

| # | Decision | Recommendation | Why |
|---|---|---|---|
| **D1** | **Narrator authority.** (a) Incidental properties of things in view are written as narrated, with no Oracle coin flip. (b) Ordinary knowledge is proposed by the model and settled by the Oracle. (c) Consequential content comes only from generators. Add to 12.6.1: "Proposing a candidate and letting the Oracle settle it is not choosing." | **Yes** | (a) removes 342 forced redrafts in 33 runs; (b) is how Mythic and Starforged reconcile "no GM chooses truth" with "success yields content"; (c) keeps every clue, name and secret procedural. |
| **D2** | **I-153.** Does an honest "I don't know" plus a real person or place who would know count as a success? | **Yes**, at least at Limited reach | Without it, the ladder must always invent a fact, which pushes back toward the narrator authoring truth. |
| **D3** | **I-158.** Difficulty | **Option B in two steps.** Ship A's four guardrails (one snag at most; lower rung for everyday acts; critical failure ≤ success on non-Dire unopposed frames; an observer counts only if they'd act). Then a per-verb obstacle-class rubric with a one-rung nudge that cites a fact. Keep 01.8.1 and T-01-3 unchanged. | The crowd goes from 10%/45% to 55%/5%, and fight approaches get distinct odds. Leniency risk is answered by code computing the DC, not by harsh tie-breaks. |
| D4 | Pull a reduced 15.9 / PR-15-6 case builder into Milestone 1 (2 nodes, 3 placements each, 1 core at the opening) | **Yes** | It is the honest replacement for `incident.py`, and the rules already specify it. Roughly 300–400 lines. |
| D5 | Support scope: support is judged against the packet; contradiction against the whole store; off-packet truths pass but are logged as retrieval misses | **Yes** | The strict alternative makes narration hostage to retrieval quality. |
| D6 | OFFER display: numbers plus words, or words only? | **Both** ("better than even, 55%") | Numbers alone get misread (XCOM); words alone hide honest odds. |
| D7 | Safe frames (cost ≤ S1) auto-commit, as a creation-time preference | **Default on** | Fixes P-024's odds screen for opening a door. |
| D8 | Detail slot list width and the cap of 8 active lasting details | Start with A's list and cap; tune with the long-horizon harness | |
| D9 | One real-Gemini run of the long-horizon scripted test (about 300 turns) | **Yes, after Phase 2** | About $10–20 at today's prices. It is the only way to verify cost, cache-hit rate and Flash behaviour. Everything so far was measured on Haiku. |

---

## 5. Build order

Each phase is a spec-kit feature with a harness gate. Rules changes follow the project process: a revision, a DL
entry in `DL-CC.md`, re-assembled appendices, anchors, and a clean validator.

### Phase 0: measure first (no owner decisions needed)
- **Offline replay of recorded packets** (B). `model_calls.request` holds about 300 first-draft narrator packets.
  It is the free A/B bench for every narration change.
- **Reader golden set** (D P6): about 80 player lines from the 62 runs, labelled with verb, facets, necessity
  and `question_kind`.
- **Minimal long-horizon harness** (A P8):
  - an aged-state synthetic store of 300 scenes, for packet boundedness;
  - a scripted player of about 300 lines covering revisits, absent NPCs, recall probes, scuffles and notices;
  - metrics: contradictions per 100 turns by class, recall precision and coverage, cross-turn novelty-4, view
    tokens, cache-hit rate.
- **Difficulty sim** `rules/_process/simulation/01-difficulty_rubric_sim.py` (D §5, designed only), with
  committed output.

### Phase 1: low-risk structural wins
- **B P4: typed rendering layer** (`engine/text/render.py`, about 150 lines, no dependency). Retires the regex
  in `fallback.py`.
- **A P3: ranked, budgeted view**, plus the bug that leaks archived NPC memories into the view (12.11.7).
- **A P6: cache-aware layout.** Move the trigger list out of the core section; the Director's cache hit rate is
  0% today.
- **D guardrails** (Option A) and **D P4** (a cost follows its stakes source).

### Phase 2: the core restructure (after D1–D3)
- **One narrator schema change:** B P1 (sentence declarations with refs as packet enums) + C P1 (`element_kind`
  and the tier lookup) + B P3 (repair one sentence at a time; "deliver what passed" becomes a rule).
- **C P4: default NPC layer.** This addresses B's largest failure class (524 NPC acts with no record row) and
  replaces the World LLM call.
- **D P1 + P3:** the gate and necessity are computed; the Reader schema shrinks (with C's `question_kind`).
- **Gate:** first-draft pass rate above 50% (today 1.4%), turns with cut sentences below 15% (today 56%),
  narrator calls per turn ≤ 1.2, Reader golden set with verb ≥ 95% and gate ≥ 98%.

### Phase 2b: Laya spike (2–3 days)
- Train Laya on the shrunken Reader schema, using the recorded calls relabelled plus negation pairs, and score
  it against the golden set. If it passes, extend it to the Framer class, the NPC practice and the diff-audit
  gate. See [E_laya_fit.md](E_laya_fit.md).

### Phase 3: content and memory
- **C P5: rich world seed** (looks, furniture, exits, 2–4 facts and a stance per NPC, documents with text). It
  comes first in this phase because established details and the answer ladder both need material.
- **A P1 + P7 / B P6: established details and scene state.**
- **C P2: answer ladder**, plus the asked-and-answered index. **C P3:** casting and the reduced case builder.
- **D P2: rubric (Option B), D P5: plain-language OFFER templates** (built on B P4's renderer).
- **Gate:** empty-success rate 0; ask-twice consistency 100%; "who is missing?" answerable within 3 turns in
  100% of seeded openings; no non-Dire unopposed OFFER with CF > S; contradictions per 100 turns below the
  Phase 0 baseline.

### Phase 4: scale and cost
- **A P2: spotlight; A P5: role views; B P2: diff-mode Checker.** The diff audit's skip is enabled only once
  undeclared assertions fall below 0.3 per turn.
- **A P4: scene cards and recap from cards.**
- **The real-Gemini long-horizon run (D9).** Then resume playtests at 2 personas as a regression monitor.

---

## 6. Cost picture

Rough figures from the lane estimates; they must be re-measured on Gemini.

| | Today | After Phase 4 |
|---|---|---|
| Model calls per turn | about 4.9 | about 2.5–3 |
| Narration cost (B) | about 3.2¢ | about 1.4–1.6¢ |
| World call | about 0.5¢ | about 0 (code; a rare tie-breaker or proposer) |
| Framer | every rolled beat | skipped on trivial or certain beats (plausibly 20–30%) |
| Whole turn, 2026 prices | about 3.3¢ (60% cached) to 6.4¢ (uncached) | **plausibly about 1.5–2.5¢** |
| Whole turn, from 2027-01-01 | double | about 3–5¢: caching and role trimming become budget-critical |

---

## 7. Fixes to keep, and fixes to retire

**Keep and build on these** (good ideas, generalised by the redesign):
- The truth gate with code computing verdicts; the class checks in `audit/claims.py` (reused with subjects
  given).
- I-127 / DL-12-37: atmosphere is never a claim; new ordinary elements are never cut for being new.
- Name knowledge (`name_known`, `name_of`, 12.10.2; P-069, P-096); `DEGREE_WORDS`.
- Mid-scene NPCs joining `cast_present` (P-056); the addressed NPC answers, not a bystander (P-118); positions
  written in a fight (P-099); `position_set` on reuse (P-095).
- Stored facts delivered ranked by relevance (d06505c): it becomes rung 1 of the answer ladder.
- Reading delivers a document's words (cf4d28c), generalised by document entities.
- Illegal frame choices impossible by schema (01a3737); anchors limited to the verb family (ea57355).
- Enter re-prompts, a RESULT after every roll, "change approach" asks how (172b2b2); per-beat RESULT labels
  (P-104).
- `incident._people`'s exclusion filter, reused as the casting gate.
- The opening-clause and speech-opener freshness regex, as a cheap backstop.
- The P-084 guard: the Oracle never writes NPC list fields.

**Retire, superseded:**

| Retire | Superseded by |
|---|---|
| `_carry` redraft carry-over (P-002) | Sentence declarations (B P1) |
| Cut-only remainder delivery, the "What do you do?" patch-in, `pure_cut` / `keep_prompt` (I-131, I-135) | Per-sentence repair as a rule (B P3) |
| `_FORBIDDEN_NEW` keyword proxy (I-129), `_DEEDS`, `_mention_name`, `_GENERIC_PREDICATES`, `GIVEN_NOTES` / `_restates_given` / `_reacts_to_incident`, screen 12.2.7's Checker flags (I-150a) | Declared `element_kind` + tier lookup + coverage (B P1, C P1) |
| `claims._learning_success → undetermined` (an after-the-fact Oracle call); `_settle` on incidental claims | Answer ladder before narration (C P2); T1a write-as-narrated (B P5) |
| `incident.bind_incident`, `SUBJECTS`, `STORY_ROLES`, `WHO`, `settle_who` and its uniform-random pick (I-148, P-067) | Casting + reduced case builder (C P3) |
| `world_step._talk_answers`, `_who_questions`, `_WHAT_ASKED`, `_NAME_OF`, `_ASKS_NAME` regexes; "name one concrete thing" narrator notes; the "top thread" / "first present person" fallbacks; the "responds as the talk went" placeholder | Reader `question_kind` + answer ladder (C P2) |
| The addressed-NPC speech exception in claims (I-140a); I-128 cutting of standing activity; the World LLM call as the default path | Default NPC layer (C P4) |
| `fallback.py`'s `_you`, `_base`, `_AND_VERB`, `_negate`, `_oracle_line`, `_finite`; `fact_sentence` slug munging (P-003, P-040, P-077, P-091, P-097, P-108, P-126) | Typed renderer (B P4) |
| `plain_offer_words`, `_fix_pronouns`, `_fact_words`, `_difficulty_phrase`, TRADE_LABELS (P-005, P-028) | OFFER templates + glossary (D P5) |
| `gate.py` "G1 before G3" override, `_plain_form_of` speech case (P-031, P-122); Reader prompt gate, "gentle touch" and would-be-licence lines (P-023, P-064, P-123); `reader_check` G2 rule | Computed gate (D P1) |
| `_plain_reading` regex (P-110); the Reader's `necessity` field; the costs.py "observer is a judgement call" stopgap | `necessity()` (D P3) |
| Framer tier and snag tie-break prompt lines; the "Moderate default" | Rubric (D P2) |
| `WRITTEN` exemptions in `scene_facts` / `scene_scope` (P-110, P-041); the `MAX_SCENE_OBJECTS` carve-out; the `_DESCRIPTIVE_KEYS` ordering; the newest-introduced known-cast list | Pins + ranked view (A P3) |
| Holder-on-mention special case (P-073); the freshness image regex (P-030, P-078) | Established details + `last_used` marks (A P1) |
| First-name matching | Alias index (A P2) |

Ledger rows each phase should close: I-128, I-129, I-130, I-131, I-134, I-135, I-138, I-140, I-143, I-145,
I-146, I-148, I-149, I-150, I-153, I-155, I-158. Open playtest issues it addresses: P-024, P-037, P-054, P-063,
P-085, P-092, P-094, P-098 (via spotlight and seeded looks), P-114, P-117, P-119 (via the closed slot list),
P-121, P-124, P-125, P-127.

---

## 8. Risks

1. **The narrator under-declares** (measured at 2.5× today). Everything in Phase 2 bets that per-sentence
   declarations beat a trailing list. *Mitigation:* the offline replay must show < 0.3 undeclared assertions
   per turn before the Checker is ever skipped; until then the diff audit runs every turn.
2. **Prose quality inside a sentence array on Gemini Flash** is untested. A/B it on the replay set, and keep a
   fallback schema (`fiction` plus refs keyed by sentence index).
3. **Over-constraint.** Once a detail is stored, the narrator is locked to it, and thin entities still repeat.
   Established details only work after the rich seed (Phase 3 order matters).
4. **NPCs become vending machines** if every Talk yields. Keep refusals, request size, leveraged clues and
   15.6.2's reason to lie.
5. **Proposal bias in T1b.** The LLM proposes interesting answers, and Likely odds say yes about 70% of the
   time. A seeded sim should check that ratified facts don't cluster into accidental clues.
6. **Rubric coverage.** Acts that fit no obstacle class fall back to the guardrails. The sim should report the
   share that land in `other` (target < 10%).
7. **Model drift.** All measurements so far are on Haiku. The golden set and the long-horizon harness must be
   release gates for any model or version change.
8. **Hundreds of sessions** is unproven anywhere in the field; no public benchmark goes past about 100
   interactive turns. The aged-state synthetic test is the cheapest proxy. Promote real-play failures into the
   scripted corpus as they appear.
