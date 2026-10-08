# B. Narration and claim verification (themes B and G)

Research lane B of four, written 2026-10-07 after the 62-run playtest loop. Neighbouring lanes: A (memory and
context selection), C (content contract and NPC agency), D (adjudication and difficulty). This note extends
`research_notes/Tech stack and Phase 0 build/memory_and_consistency_state_of_the_art.md` and does not repeat it.
Every source below was read at its primary URL unless it is marked *(unverified)*.

**Bottom line.** Stop reverse-engineering the prose. The narrator should write its prose **one sentence per
item, each sentence carrying what it asserts**: references to record lines and fact ids in the packet, plus any
new elements. Code judges those declarations with the existing `check_claims`. A slimmer Checker only *diffs*
each sentence against its own declarations, so it reports undeclared assertions, not every assertion. Failures
are repaired one sentence at a time, and the fallback is rendered from typed fields, not regex. Two smaller rule
changes remove most redrafts: an incidental property of an existing element is written on mention instead of
being decided by an Oracle coin flip, and "deliver what passed" becomes the rule rather than a stopgap.

---

## 1. The problem, and how the loop works today

### 1.1 The current loop (PR-12-1 T7–T10, `engine/dm/narration.py::narrate_checked`)

1. **T7.** The Narrator (`roles/narrator.py`) returns `fiction` plus `mentions` (new addressable elements).
2. **T8.** `write_mentions` writes those elements. If an unsettled property was settled, one "mention redraft"
   follows (PR-00-7 step 3).
3. **T9.** A separate Checker call (`roles/checker.py`, a 700-word prompt) re-reads the prose with its sentences
   numbered. It guesses every assertion as `{sentence, subject id, class, predicate, value, asserts_change,
   pc_words_or_feelings}`, choosing among 14 classes (12.3.1).
4. `engine/audit/claims.py::check_claims` (about 1,100 lines) computes a verdict for each claim (12.3.2). Four
   stopgaps then adjust the verdicts:
   - `_carry` keeps passes on unchanged sentences;
   - `_apply_writes` writes unknown subjects on mention;
   - `_settle` asks the Oracle about `undetermined` claims;
   - `_plan` builds the redraft instructions.
5. Failures are handled in one of three ways:
   - **a pure cut**, where code deletes the sentences;
   - **a redraft**, which means a new Narrator call and a new Checker call, re-guessing everything;
   - **past the budget**, where every failing sentence is cut and the remainder delivered (I-131, I-135).

   The plain fallback (`engine/audit/fallback.py`) is used only when nothing remains. It rewrites the
   Reader's free-text restatements into second person with suffix rules and regex (`_you`, `_base`, `_negate`,
   `fact_sentence`).

### 1.2 What the saves show

I read `turns.record.draft_versions` and `model_calls` from the 33 runs after 19:30 (code close to final): 524
turns, 374 of which had narration.

| Measure | Value | What it means |
|---|---|---|
| Checked first drafts with at least one failing claim | **290 / 294 (98.6%)** | The gate fails almost every draft. |
| Failing claims per first draft | median 5, mean 5.3, p90 9 (of about 16 claims) | |
| Narrated turns delivered as first drafted | **3 / 374** | The "4% fallback" figure hides this. |
| Turns delivered after code cut sentences | 208 / 374 (56%) | Content silently removed. One cause of "she agreed but never said what". |
| An identical sentence, re-checked in the next draft, gets a different set of claim classes | **832 / 2,508 (33%)** | Direct evidence of extraction noise (P-002). `_carry` exists to paper over it. |
| Failing verdicts overridden by `_carry` | 1,044 | |
| Oracle asks on narrator details / answered "no" (forcing a redraft) | 713 / **342** | A coin flip against the draft, on details nobody asked about. |
| Narrator `mentions` per draft vs unknown-subject claims the Checker found per first draft | 0.86 vs 2.1 | **The narrator under-declares by about 2.5×** under the current prompt. |
| Calls per turn: narrator / checker / everything else | 1.81 / 1.61 / 1.52 | Narration is **69%** of all model calls. |
| Mean latency per call (Haiku via CLI) | narrator 14.8 s, checker 20.5 s | About 60 s of narration per turn. CLI overhead inflates this, but the ratio holds. |

Top failing (verdict, class) pairs:

| Verdict | Class | Count | Lane |
|---|---|---|---|
| `unsourced_change` | action | 524 | C (NPC agency) |
| `unsourced_change` | position | 294 | |
| `undetermined` | identity | 176 | |
| `new_element` | sealed | 164 | |
| `contradicted` | identity | 145 | |
| `contradicted` | position | 139 | |
| `undetermined` | possession | 124 | |
| `contradicted` | knowledge | 121 | |

The 164 `sealed` failures are the Checker labelling ordinary prose as "sealed" with nothing sealed to match:
pure classifier noise, cut by code.

### 1.3 Issues

| Theme | Issues | Root cause |
|---|---|---|
| **B** | P-002, P-018, P-079, P-112, P-125, P-063, I-131, I-135 | Claims are guessed after the fact. Each redraft re-guesses, so the loop does not converge, and the stopgaps (carry, cut-and-deliver) treat that symptom. |
| **G** | P-003, P-040, P-077, P-091, P-096, P-097, P-108, P-126 | The fallback, journal and OFFER text take *model-written* strings (restatements, Oracle predicates turned into slugs, speech records) and convert them with regex. The input has no types, so every new sentence shape breaks it. |

---

## 2. What the field does

### 2.1 Plan first, then write (content selection, then realization)

- **Moryossef, Goldberg and Dagan, *Step-by-Step* (NAACL 2019)**, <https://aclanthology.org/N19-1236/>.
  - A symbolic plan, faithful to the input, followed by neural realization. The abstract claims improved
    "reliability and adequacy".
  - The agent summary reports manual error reductions of 85% (omitted facts), 56% (repeated or invented) and
    90% (wrong lexicalisation) against a strong end-to-end baseline *(figures not rechecked in the PDF)*.
  - The follow-up (<https://arxiv.org/abs/1909.09986>) reranks candidates by whether their entity sequence
    matches the plan.
- **Puduppully, Dong and Lapata (AAAI 2019)**, <https://arxiv.org/abs/1809.00582>: select the content, then
  realize it. Higher precision on relation generation.
- **Castro Ferreira et al. (EMNLP 2019)**, <https://aclanthology.org/D19-1052/>: pipelines beat end-to-end on
  semantic adequacy in human ratings, but not uniformly.
- **Slobodkin et al., *Attribute First, then Generate* (ACL 2024)**, <https://aclanthology.org/2024.acl-long.182/>.
  - Steps: select spans, plan sentences, then generate sentence by sentence. The selected spans *are* the
    citations.
  - Citations become far more concise, attribution accuracy is kept or improved, and human verification is
    faster.
  - This is the closest published analogue of "sentences carry their declarations".
- **Wiseman, Shieber and Rush (EMNLP 2017)**, <https://arxiv.org/abs/1707.08052>: "even templated baselines
  exceed the performance of these neural models on some metrics".
  - The agent summary reports template relation precision of about 99% against about 48% for the neural model
    *(numbers not rechecked)*.
  - This is the case for template fallbacks.

**Lesson.** A declared plan is auditable, but nothing forces the prose to stay inside it. Every paper above
either constrains realization or checks it afterwards.

### 2.2 Declarations and self-citation: the failure modes

- **ALCE (EMNLP 2023)**, <https://aclanthology.org/2023.emnlp-main.398/>: even the best models left about half
  of their ELI5 generations not fully supported by the passages they themselves cited *(per the agent summary
  of the abstract)*. A self-declared source is not proof of support.
- **Self-Correction Bench**, <https://arxiv.org/abs/2507.02778> (verified): a 64.5% blind spot. Models fix an
  error when it is attributed to someone else but miss the identical error as their own.
  - Implication: a merged call whose "verified: true" flag is self-graded is worthless.
  - What a merged call *can* usefully emit is the declaration itself.
- **Under-declaration** is the key risk named by every source. Our own saves measure it at about 2.5×
  (section 1.2).

### 2.3 Products

| Product | Same-turn structured output? | Prose checked against state? |
|---|---|---|
| **Intra** (Ian Bicking): <https://ianbicking.org/blog/2025/07/intra-llm-text-adventure>, `lib/game/classes.ts` | Yes: tags in the reply (`set`, `dialog`, `description`, …) | No. The tags are checked for shape and permitted property changes only. |
| **Infinite Worlds** (<https://infiniteworlds.mywikis.wiki/wiki/How_Infinite_Worlds_works>) | Yes: `outcomeDescription` plus tracked-item and quest-state fields | No |
| **Friends & Fables, "How Franz works"** (verified, <https://fables.gg/blog/how-franz-works>) | No. Up to a dozen LLM calls: a research step builds a Working Context, then post-processing LLMs read the narration and decide the state changes. | No. Dev log 26.01 says narration and state updates need rewriting. |
| **Latitude Voyage** (<https://latitude.io/>) | Claimed "World Engine" as impartial judge | No published mechanism or error rate |
| **Hidden Door** | No public evidence | No public evidence. Pronouns are computed and stored (prior note). |

**Conclusion.** No shipping product publicly verifies prose against state. This project's truth gate is ahead
of the field; the issue is its cost and noise, not its premise.

### 2.4 Verification techniques: which are cheap per turn

**Decompose, then verify** (FActScore <https://arxiv.org/abs/2305.14251>, SAFE <https://arxiv.org/abs/2403.18802>,
VeriScore <https://arxiv.org/abs/2406.19276>, DnDScore <https://arxiv.org/abs/2412.13175>). These are what the
Checker does now. Decomposition itself is noisy:

- **Decomposition Dilemmas (NAACL 2025)**, <https://aclanthology.org/2025.naacl-long.320/> (verified abstract):
  "a trade-off between accuracy gains and the noise introduced through decomposition". The agent summary reports
  that with MiniCheck every decomposition method *lowered* accuracy against checking undecomposed sentences.
- **A Closer Look at Claim Decomposition** (\*SEM 2024): results swing with the decomposition prompt.
- **DnDScore:** 19% of judgments flip once pronouns are decontextualized. Our 33% instability matches this.
- **VeriScore:** found only 0.03 verifiable claims per creative story under an open-world definition. Fiction
  is mostly embellishment, so the useful signal is contradiction, not "unsupported".

**Small grounded checkers** (no API cost, but they need local inference and torch, a new heavy dependency):

| Checker | Size | Reported accuracy (BAcc) |
|---|---|---|
| MiniCheck-FT5 (<https://arxiv.org/abs/2404.10774>, verified) | 770M | GPT-4 level on LLM-AggreFact at about 400× lower cost |
| Leaderboard (<https://llm-aggrefact.github.io/>) | | Bespoke-MiniCheck-7B 77.4, MiniCheck-FT5 75.0 |
| Vectara HHEM-2.1-open | ~0.1B | about 1.5 s per 2k tokens on CPU (vendor figure) |

All of them judge "is this supported?", and fiction's embellishment reads as "neutral". Useful only as an
optional contradiction pre-filter, not as the gate.

**Other options:**

- **SelfCheckGPT** (20 samples) multiplies the cost. Offline diagnostics only.
- **LLM as judge:** order and verbosity biases (<https://arxiv.org/abs/2306.05685>). Ask for spans and fact
  ids, never for "is this good?".
- **ConStory-Checker** (<https://arxiv.org/abs/2603.05890>): an LLM consistency checker with precision .88 but
  **recall .55** on injected errors. An LLM audit cannot prove that errors are absent; it can only lower their
  rate.

**Deterministic checks available to us:**

- the record handles and fact ids that were cited (existence, class compatibility);
- names and aliases in a sentence against the entities referenced;
- numerals against quantities;
- pronouns against the stored pronouns of the referenced entity;
- mechanics words (already done);
- sealed-content matching (already done);
- **coverage**: every must-name record line is cited by some sentence (12.14.12).

**Format cost** ("Let Me Speak Freely", <https://arxiv.org/abs/2408.02442>, verified): format restrictions can
cut reasoning quality. The Narrator already writes prose inside JSON, so the marginal risk of splitting it into
sentences is small, but it must be A/B-tested.

### 2.5 Rendering (theme G)

- **SimpleNLG** (<https://github.com/simplenlg/simplenlg>; a Python port is `simplenlg` on PyPI, MPL-1.1): a
  clause from {subject, verb lemma, object} with features for tense, person, negation and passive.
- **Inform 7's adaptive text** (`[We] [take] the lamp`, <https://ganelson.github.io/inform-website/book/WI_14_2.html>):
  the verb agrees with whichever entity is printed in the slot. This is the exact pattern needed for "you" vs a
  third person.
- **Morphology libraries:** `inflect` (MIT, maintained, a/an, plurals, pronoun case) and `lemminflect` (MIT,
  unmaintained since 2022).
- **Authoring tools:** Tracery and Ink are authoring grammars, not clause realizers.
- **T2G2** (<https://aclanthology.org/2020.emnlp-main.527/>): fill templates, then let an LM smooth them. A
  model for an optional "polish" pass that never adds facts.
- **Emily Short, "World Models Rendered in Text"** (<https://emshort.blog/2018/06/19/world-models-rendered-in-text/>):
  select, then order, then realize.

**Fit for this project.** The vocabulary is closed: about 15 basic verbs, a relation registry and the degree
words. A ~150-line in-repo realizer with an irregular-verb table needs no dependency (ponytail rung 3).

---

## 3. Ranked proposals

Costs are on `gemini-3.8-flash` ($0.75 per M input, $0.075 cached, $3.75 per M output including thinking,
through 2026-12-31, doubling on 2027-01-01, <https://ai.google.dev/gemini-api/docs/pricing>, verified).

**Assumptions:**

| Call | Input | Output |
|---|---|---|
| Narrator | ~12k tokens, ~8k cacheable | ~0.5k visible + ~1k thinking at the minimum "low" level |
| Checker | ~4k tokens | ~1.2k visible + ~1k thinking |

This gives about **0.9¢ per narrator call** and **0.95¢ per checker call**. Narration today costs about
1.81 × 0.9 + 1.61 × 0.95 ≈ **3.2¢ per turn**, already over the 1–3¢ target before the other roles.

### P1. Sentence-carried declarations, with code judging them (theme B core). Highest value.

**Design.** The narrator schema replaces the `fiction` string with `sentences`. Each item has:

- `text`;
- `refs`: handles of record lines (`R1`…, one per line of `record_text`) and fact ids from the narrator view.
  These are **enums built from the packet**, so constrained decoding makes it impossible to cite something
  outside the view.
- `about`: entity ids from the scene scope;
- `new`: the existing `mentions` shape plus a `kind` enum and an `ordinary` flag (12.14.13);
- `atmosphere`: boolean.

The fiction is `" ".join(texts)`. Code then:

- **(a)** resolves each ref and judges it with `check_claims`, with the subject *given*, not guessed. Every
  class check is reused.
- **(b)** writes `new` elements (T8, unchanged).
- **(c)** runs the deterministic scans of 2.4 on every sentence. An `atmosphere` sentence that contains a name,
  a numeral or an entity alias fails as undeclared.
- **(d)** computes **coverage**: each must-name record line (the outcome, the NPC's response, conditions,
  omens, positions) must be cited by at least one sentence. Coverage replaces the Checker's
  `intent_acknowledged` and `next_step_exists` flags for the record's parts.

**Supersedes:**

| Retired | Why |
|---|---|
| `_carry` (P-002) | Sentence identity is explicit. An unchanged sentence keeps its declarations, so nothing is re-guessed. |
| `_mention_name` / `_GENERIC_PREDICATES` | Names are declared. |
| `_apply_writes` as the main path | Kept only as a backstop for undeclared new elements. |
| `_restates_given`, `GIVEN_NOTES` matching, `_reacts_to_incident` | Given notes become record handles that are cited. |
| `_DEEDS` phrase list (claims.py:168) | |
| `_FORBIDDEN_NEW` keyword list (claims.py:368) | Replaced by the declared `kind` enum. C's three-tier contract defines the kinds. |
| `split_sentences` heuristics in the check path | |
| Screen 12.2.7's use of the Checker flags (I-150a) | Replaced by coverage. |

**Rules.**

- **12.3.1:** claims come from the narrator's declarations `[J:enum]`, plus any undeclared assertion the audit
  finds `[J:flag]`.
- **New 12.3.1a "Sentence coverage":** every sentence is either declared or atmosphere. An atmosphere sentence
  naming anything addressable is undeclared.
- **12.2.10:** gains "every quantity, condition, position, possession or standing a sentence states cites the
  fresh view's id". This makes "read before you narrate" checkable.
- **PR-12-2 step 1** is rewritten from "split the draft and list every assertion" to "resolve each sentence's
  declarations; scan; compute coverage".
- **PR-00-7 steps 1–2** become the declaration itself.

**Engine.**

- `roles/narrator.py`: schema, prompt, and handles in `record_text`.
- `dm/schemas.py`: enums for refs.
- `dm/narration.py`: a new `judge_declarations`.
- `audit/claims.py`: an entry point that takes a given subject and class.
- `dm/mentions.py`: unchanged.

**A (memory).** The packet *is* the allowed fact set, and the enum enforces it.

- Judge **support** against the packet and the record.
- Judge **contradiction** against the whole store. A claim that is true only by an off-packet fact passes, but
  is logged as a **retrieval miss**: a free metric for lane A's selection quality.

**C (content).** About 524 of the failures are NPC acts with no record row. P1 only helps if C's default NPC
layer puts each present NPC's response in the record as a citable line. Without it, P1 moves the failures to
the audit; it does not remove them.

**D (adjudication).** Outcome sentences cite the beat handle (degree, reach), so P-112-type contradictions
reduce to "the sentence's polarity vs the cited degree". That is checkable by the audit and by a
negation-keyword scan.

**Cost.** About +250 output tokens on the Narrator (≈ +0.1¢). No extra call.

**Test** (the harness already logs everything needed):

| Metric | Today | Target |
|---|---|---|
| First-draft pass rate (new metric) | 1.4% | > 50% |
| Turns with cut sentences | 56% | < 15% |
| Narrator calls per turn | 1.81 | ≤ 1.2 |
| Fallback rate | | ≤ 4% |

Contradiction findings come from the scene-end sweep (12.4.8 step 4) and from player notes containing
"contradict / repeats / never said".

**Offline A/B before any live run.** `model_calls.request` stores every narrator packet. Replay the ~300
recorded first-draft packets through the new schema and compare pass rates. No playtest is needed for the first
signal.

### P2. A diff-mode Checker: verify, don't extract

**Design.** The Checker gets the numbered sentences, each with its declarations rendered in words by P4's
renderer, plus the entity list. It returns only:

- **(i)** assertions in a sentence that its declarations do not cover, as `Claim`s (existing schema, judged by
  `check_claims`);
- **(ii)** declarations the sentence does not actually express, or expresses differently, which catches
  over-declaration and "agreed but never said what".

The usual output is an empty or short list.

- **Conditional run:** skip the call when every sentence is declared, no atmosphere sentence was flagged, and
  the turn has no `pc_agency` risk (the player's message has no SPEECH part).
- **Safeguard:** in the harness, run the old full extraction on 1 turn in 10, to measure what the diff Checker
  misses. This counters the anchoring risk of showing it the declarations, and keeps FR-034's independence in
  spirit: it sees data, never the narrator's reasoning.

**Supersedes.** The 14-class full extraction on every draft and the cost of re-extracting every redraft.

**Rules.**

- **12.3.1:** "extraction" becomes "audit of undeclared assertions".
- **12.3.1's worst case** stays: missed claims are class iv, caught by the 12.4.8 sweep.
- **12.4.8 step 4** also re-checks declared position, possession, quantity and harm sentences.

**Engine.** `roles/checker.py`, `prompts/checker.md` (shorter, because classification moves to the narrator),
and `dm/schemas.py`.

**Cost.** Output drops from ~1.2k to ~0.1k visible tokens: about **0.4¢ per call**, run on ≤ 1.0 calls per
turn. Narration goes from ~3.2¢ to **~1.4–1.6¢ per turn**, and from ~3.4 to ~2.1 sequential calls (fewer when
the audit is skipped).

**Optional later step.** Put the audit on a Flash-Lite model (price not checked for this note), or add HHEM or
MiniCheck as a local contradiction pre-filter. That adds the torch dependency; defer it until the harness shows
the audit's cost matters.

**Test.**

| Metric | Today | Target |
|---|---|---|
| Undeclared assertions per turn | 2.1 | < 0.3 |
| Checker calls per turn | 1.61 | ≤ 0.7 |
| Agreement of the 1-in-10 full extraction with diff findings | | Recall of the diff mode against full extraction ≥ 0.8 |

### P3. Repair one sentence at a time; "deliver what passed" becomes the rule

**Design.** Each failing sentence is handled on its own:

| Failure | Fix |
|---|---|
| `cut`-type, not covering a must-name line | Code drops the sentence. |
| Covers a must-name line, or has a store value to use | **One narrow redraft call per round**: only the failing sentences, with the store's values. The Narrator returns replacements; passing sentences are never re-sent or re-checked. |
| Still failing after 2 rounds | Delivered as the **rendered fact line** for the record item it was meant to cover (P4). |

The plain fallback becomes the extreme case of the same rule: no model sentence passed, so every covered item
is rendered.

**Supersedes:**

- I-131 and I-135 (cut-only remainder delivery, commits 3d478c9 and fd898d8): ruled, not stopgap;
- the `pure_cut` / `keep_prompt` special cases;
- the "What do you do?" patch-in;
- P-018, P-125 (the fallback echoing the player's questions), P-079.

**Rules.**

- **12.3.3** is rewritten: "A failing sentence is fixed by the table's rule. A redraft re-writes only failing
  sentences. After two redrafts, a still-failing sentence is cut, and any must-name record item left uncovered
  is stated by its rendered line. The plain fallback is this rule when no drafted sentence passes."
- The `rule_conflict` ruling is logged only when a rendered line was needed.
- The "dull but true" rationale stays.

**Engine.** `dm/narration.py` (the loop becomes per-sentence; the file roughly halves) and
`roles/narrator.py` (`Redraft` carries only failing sentences).

**Cost.** Narrow redrafts are short: ~1–2k fresh input over a cached prefix, ~150 output tokens.

**Test.**

- Redraft calls per turn.
- Rendered-line rate, which replaces the fallback rate.
- Player notes containing "agreed but never said".

### P4. A small typed rendering layer (theme G)

**Design.** A new `engine/text/render.py`, about 150 lines and no dependency, provides:

- `clause(subject_id, verb_lemma, obj=None, *, neg=False, tense="present")`. The subject is printed through
  `name_of` (name knowledge, 12.10.2), "you" for the PC. Verbs agree by a suffix rule plus an irregular table,
  which is complete because the verbs come from a closed list.
- `np(id)` with a/an and plurals.
- `degree_words`.

Every player-facing generated sentence goes through it:

- **Facts:** every fact gets a **typed relation** from a registry, each with a clause template (`held_by`,
  `at`, `knows`, `said`, …).
  - Free-text answers (an Oracle question, NPC speech) are stored with their **original sentence as a gloss**
    and shown **verbatim or quoted**, never transformed.
  - Oracle questions are asked as a *statement* plus its negation ("The shutters are closed." / "The shutters
    are open."), so the answer selects one stored sentence.
- **The fallback's beat lines** render from typed fields: the actor, D's closed verb lemma, the target ids,
  `approach_words`, and the degree. The Reader's free-text `restatement` is shown only inside OOF blocks, as
  written.
- **OFFER and RESULT lines** render from frame fields. Coordinate the wording with the presentation work on
  I-134 and I-138 (theme F).

**Supersedes** in `audit/fallback.py`: `_you`, `_base`, `_AND_VERB`, `_negate`, `_oracle_line`, `_finite`, and
the slug munging in `fact_sentence`. These were the P-003, P-040, P-077, P-091, P-096, P-097, P-108 and P-126
fixes, and all five `ponytail:` comments in that file. `oof.short_text`-based `_for_beat` (P-104) uses the verb
phrase instead.

**Keep:** `DEGREE_WORDS`, `the_name` / `name_of` (P-096's name-knowledge fix), and `drop_reader_notes`.

**Rules.**

- **12.14.4** (no mechanics in fiction) is unchanged.
- **12.3.3's fallback** lists its sources as typed record fields.
- **New presentation rule:** "player-facing generated sentences are rendered from typed fields. Model text is
  either quoted whole or not shown."
- **Ch.00's fact model** gains a closed relation vocabulary with a `gloss` field.

**Interfaces.**

- **A:** the journal and "what you know" read glosses, so they will not garble.
- **D:** needs the Reader to emit a verb lemma from a closed list (the handoff's recommendation 5).

**Cost.** None at runtime.

**Test.**

- A golden file of rendered sentences: irregular verbs, "you" vs third person, negation, unknown names.
- In the harness, grep delivered text for the P-003/P-040 signatures ("You try to <Capital>", "is at within",
  "( intervals)").

### P5. Incidental properties are written on mention; the Oracle is kept for consequential ones

**Design.** Today:

- a *new* element gets whatever properties the draft implies;
- an *existing* element's unset property goes to an Even-odds Oracle, and a "no" forces a redraft (342 times in
  33 runs).

Make the two symmetric. An unset property that is **incidental** is written as drafted, by the same 12.14.13
test: "would it help or hinder beyond what any such place ordinarily offers?" Examples are a coat's colour or a
worker's trade.

Only **consequential** properties go to the Oracle *before* prose, at T4: locked, armed, present, knows. Those
are already reached through player actions and G0 questions at T4, so mid-narration Oracle calls become rare,
and the PR-00-7 mention redraft almost disappears.

Identity fields (pronouns, age, role) are rolled at creation (12.11.1 walk-on, as Hidden Door does). C's richer
seed fills places' looks and furniture, so far fewer details are unset at all.

**Supersedes:**

- `_settle`'s handling of incidental claims;
- the `mention_redraft_done` path in most turns;
- `settle_who` on the narration path (P-067). "Who" answers come only from C's knowledge facts and tables.

**Rules.**

- **12.3.2's `undetermined` row** splits: incidental → `write_on_mention`; consequential → Oracle or table.
- **PR-00-7 step 3** is restricted to consequential properties.
- This bends "if unsure, roll rather than decide" for trivia only. Record the owner's decision with a DL
  entry.

**Engine.** `audit/claims.py` (a flag on the verdict), `dm/narration.py::_settle`, and `dm/mentions.py`
(implied properties of existing entities).

**Test.**

- Oracle-"no" verdicts per narrated turn: today 0.91 (342 in 374 turns), target ≈ 0.
- Identity contradictions in later turns, which should not rise.

### P6. Established details: description of addressable things binds later turns

**Design.** A property a delivered sentence states about an addressable element is stored as a low-salience
`detail` fact (`implied` in the declaration). Examples are the smith's scarred hands, or rings on a merchant's
fingers. Later drafts are judged against it, which fixes P-063 and P-127-type drift. Atmosphere stays unstored
(I-127).

The stored details also tell the freshness logic which images were already used. That could replace the 3-gram
heuristic at narrator.py:295/353; P-094's "the same detail repeats" is related.

**Supersedes.** Partly the freshness heuristics; open P-063.

**Rules.**

- **12.14.2:** "a detail of an addressable element stated in delivered narration is established; atmosphere is
  not."
- **00.6.6:** the write includes details implied by delivered prose.

**A (memory).** This is lane A's call on salience and decay. Details should enter the packet only for entities
in scene, capped, oldest dropped first. Store bloat is the real risk.

**Test.**

- Same-entity contradictions across turns, from the 12.4.8 sweep plus a harness probe that asks "what does X
  look like?" twice, ten turns apart.
- Packet size.

### P7. Not recommended

- **A fully merged narrator-plus-self-verification call.** Self-grading has a measured 64.5% blind spot. Merge
  the *declaration* (P1), keep an independent audit (P2).
- **Moving the gate after delivery.** It contradicts INV-2. The sweep already covers class-iv misses.
- **SelfCheckGPT-style sampling at runtime.** Too expensive.
- **A heavy NLG dependency.** SimpleNLG ports are unmaintained and RosaeNLG is archived (March 2026). The
  vocabulary is closed, so an in-repo realizer is enough.

**Order of work.**

1. P4 (independent, zero risk).
2. P5 (rules decision plus a small engine change).
3. P1 with P3.
4. P2.
5. P6, once lane A has settled packet caps.

Each step is a spec-kit feature with its own harness gate.

---

## 4. Which existing fixes to keep or retire (owner guidance: treat the playtest fixes as a baseline)

**Keep: genuinely good ideas.**

- The truth gate itself, with code computing the verdicts. The class checks in `audit/claims.py` (identity,
  harm words, positions, quantities, outcome with P-112's degree check, leak and slice) are reused by P1 with
  subjects given.
- I-127 / DL-12-37: atmosphere is never a claim, new ordinary elements are written and never cut for being
  new, and redrafts never shrink.
- Write-on-mention in `dm/mentions.py`: reuse of existing names, walk-on generation, refusal of forbidden
  kinds.
- The Oracle "yes = supported" rule (P-002), now for consequential properties only.
- Owed blocks, `pure_oof`, `skip_drafting` (no narration when the OFFER restates the beat), and per-beat
  RESULT labels (P-104).
- Name knowledge in `name_of` (P-096, 12.10.2), and `DEGREE_WORDS`.

**Retire: patches on a larger wound.**

| Stopgap | Replaced by |
|---|---|
| `_carry` redraft carry-over (P-002) | P1 |
| Cut-only remainder delivery and the "What do you do?" patch-in (I-131, I-135; fd898d8, 3d478c9) | P3, which rules it |
| `pure_cut` / `keep_prompt` branches | P3 |
| `_mention_name` / `_GENERIC_PREDICATES` | P1 |
| `_apply_writes` as the main path | P1 (backstop only) |
| `_FORBIDDEN_NEW` keyword proxy, claims.py:368 `ponytail:` | P1, using C's tiers |
| `_DEEDS` phrase list, claims.py:168 `ponytail:` | P1 |
| `_atmosphere` / `_reacts_to_incident` / `GIVEN_NOTES` / `_restates_given` | P1. Incident reactions are C's default NPC rows. |
| Screen 12.2.7's flags (I-150a) | P1 coverage |
| `settle_who` on the narration path (P-067) | P5 and C |
| `fallback.py`'s `_you`, `_base`, `_AND_VERB`, `_negate`, `_oracle_line`, `_finite`, and `fact_sentence`'s slug munging, with their five `ponytail:` comments (P-003, P-040, P-077, P-091, P-096 phrasing, P-097, P-108, P-126) | P4 |
| Narrator freshness 3-gram heuristics, narrator.py:295/353 (partly) | P6 |
| Full 14-class extraction on every redraft | P2 |

---

## 5. Risks and open questions for the owner

1. **Under-declaration is real.** Measured at 2.5× under today's prompt.
   - P1 bets that "every sentence carries its refs" does better than a trailing `mentions` list, because the
     declaration is built while each sentence is written, not recalled afterwards.
   - **Gate:** the offline replay must show undeclared assertions < 0.3 per turn before P2's conditional skip
     is switched on. Until then, run the diff audit every turn.
2. **Will Gemini Flash write as well in a sentence array?** Unknown; nothing tests creative prose in JSON
   arrays. A/B prose quality on the replay set with the same persona judge (Haiku, then Gemini), and keep a
   fallback schema (`fiction` plus a parallel `refs` list keyed by sentence index).
3. **Enum size.** Gemini accepts a subset of JSON Schema, and large schemas can be rejected. With ~40 fact ids
   and 10 record handles this should be fine. The engine's schema-loosening levels (`gemini.py` `LOOSEST`)
   already exist as an escape hatch.
4. **P5 bends a core principle** ("roll rather than decide"), for trivia only. This needs an explicit owner
   decision and a DL entry. Alternative: keep the Oracle but ask it *before* drafting for the properties the
   packet lacks for entities in scene. This costs pre-rolls but no redrafts.
5. **Support scope.** Proposed: support = packet plus record; contradiction = whole store; true-only-off-packet
   passes but is logged as a retrieval miss. Owner and lane A should confirm. The stricter alternative,
   "off-packet support fails", makes narration hostage to retrieval quality.
6. **Store growth from P6.** Lane A must set the cap and decay. Without them, P6 trades contradictions for
   packet bloat.
7. **What this note cannot fix.** P1 cannot fix the biggest failure class (524 unsourced NPC acts). That needs
   lane C's default NPC layer and content contract, and I-153's ruling on what a successful Talk may reveal.
8. **The figures were measured on Haiku via CLI.** Latency and token counts are not Gemini's. Re-measure on
   Gemini once before the costs above are quoted as fact.
