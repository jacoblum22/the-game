# C. Content contract and NPC agency (I-153 and handoff themes A and C)

Research lane C, playtest round 2. Read-only research: no rules or engine edits. Sources are cited inline.
"Verified" means I read the primary page. "Per Exa summary" means the claim came from an Exa deep-research
run and I did not re-read the source.

---

## 1. The problem, restated

**The store is too thin for a truth-gated narrator, and NPCs may act only when something is sourced.**

What the 62-run loop found (HANDOFF §6 A and C):

- **Places have only a name.** The opening place's `desc` is the same as its name, and `landmarks` is empty
  (I-130).
- **NPCs carry no knowledge.** `knowledge_scope` is just `[role, people]`, a list of tags with no facts in it
  (`engine/gen/npc.py:201`).
- **Incidents have no subject.** "Someone is missing", but nobody is named (I-145, P-067).
- **Successful Talks produce nothing.** When the store has nothing on the topic, the result reads as a failure:
  P-025, P-114, P-120, I-153. Notices and omens are never described (P-054, P-110).
- **No path can create a name.** The Oracle answers only yes or no, and 12.14.13 forbids creating "a person
  with … knowledge of a thread" by mention. So "who is X?" had no answer at all (I-140c).
- **Ordinary NPC behaviour had no source,** so each piece needed its own exception:
  - replying (I-140a, P-026);
  - standing activity, such as the smith at her forge (I-128);
  - being present (P-056, P-095);
  - moving in a fight (P-099);
  - answering when someone else was addressed (P-118);
  - common knowledge of names (I-149).

**The stopgaps now in the engine form an implicit second rulebook:**

| Stopgap | Where | What it does |
|---|---|---|
| `bind_incident` | `engine/dm/incident.py` | At the first opening, binds the incident's subject to a random existing NPC, plus a reporter and two witnesses who each know one clue (I-148). |
| `settle_who` + `STORY_ROLES` + `WHO` regex | `incident.py:162` | Settles "who is X?" with a uniform random pick among *all* existing NPCs (marked `ponytail: every existing NPC fits any person-role`). |
| `_talk_answers`, `_who_questions`, `_WHAT_ASKED`, `_NAME_OF` | `engine/dm/world_step.py:270-325` | Regexes over player text. A "what" question becomes a note telling the narrator to "name one concrete, ordinary thing". With no facts, the fallback is the top thread, else "<first present person> might know more" (marked ponytail). |
| Notes to the narrator after a successful look | `world_step.py` (P-086) | Prompt text asking for "at least one concrete thing", settled afterwards by the Oracle at claim-check time. |
| `_learning_success` → `undetermined` | `engine/audit/claims.py:882` | After the fact, what the narrator invented for a successful Talk is passed to the Oracle, unless it contains a "clue" keyword. |
| `_FORBIDDEN_NEW` | `claims.py:370` | A keyword proxy for 12.14.13's five forbidden kinds (I-129). |
| The exception for an addressed NPC's speech | `claims.py`, d06505c | The NPC spoken to may talk and react; deeds still need a source (I-140a). |

**Note.** The current engine already practises a hidden form of *propose, then let the Oracle ratify*: the narrator
invents an answer, and the Checker sends it to the Oracle. But it does this after the prose is written, by
keyword, and without typing the answer. Formalising this pattern, and moving it before narration, is the core
of the recommendation below.

**A key finding from reading the rules: the ruleset already has most of the right machinery, but the engine
doesn't run it.**

- T-12-4 already has a row for "a person who must exist now → NPC generation" and a row for `tbl.meaning`.
- 12.10.6(d) already makes role common knowledge an Oracle question: Likely for facts of the NPC's trade,
  Unlikely otherwise.
- 15.9 already has sealed clue graphs, the Three Clue Rule as an invariant (15.9.4) and "core clues never fail"
  (15.9.5).
- PR-15-6 already builds a case "at hook creation … or at a mystery arising in play", with the culprit chosen
  from "an existing NPC by role and want first".
- **But** `h.15.placement_audit` and the case machinery are scheduled for Milestone 6
  (`engine/time/handlers/h15.py`), and nothing in `engine/` builds a clue graph.

So `incident.py` is a hand-rolled stand-in for PR-15-6, and `settle_who` is a stand-in for casting by role fit.

---

## 2. What the field does

### 2.1 Tabletop: how a success always yields something without the GM inventing truth

| Tradition | Mechanism | How truth stays fixed | Source |
|---|---|---|---|
| **GUMSHOE** | With the right ability, in the right place: "you will never fail to gain a piece of necessary information. It is never dependent on a die roll." Each scene has a designated core clue. Spends buy extras, never access. | The *route* to a prepared fact can change; the fact cannot. | [GUMSHOE SRD rules](https://gumshoesrd.opengamingnetwork.com/rules/), [Laws, "GUMSHOE says yes"](https://pelgranepress.com/2018/02/01/see-page-xx-gumshoe-says-yes/) (verified) |
| **Alexandrian** | The Three Clue Rule; node-based design; *proactive nodes* that come to the PCs when they have missed leads; "prep exactly what NPCs know". He also notes that GUMSHOE's "an NPC gives everything" flattens social play, so it adds **leveraged clues**: some testimony needs a prior clue to unlock. | Revelations are fixed; delivery is flexible. | [Three Clue Rule](https://thealexandrian.net/wordpress/1118/roleplaying-games/three-clue-rule), [Secret Life of Nodes](https://thealexandrian.net/wordpress/45263/roleplaying-games/the-secret-life-of-nodes), [Returning to the scene](https://thealexandrian.net/wordpress/49595/roleplaying-games/running-mysteries-returning-to-the-scene-of-the-crime) (verified) |
| **Dungeon World** | Discern Realities asks from a **closed list of six question types**. Answers "are always honest ones. Even if the GM has to figure it out on the spot. Once they answer, it's set in stone." A negative answer is legal: "Nothing, sorry." | Content may be created on demand, but it is then written permanently. | [DW SRD moves](https://www.dungeonworldsrd.com/moves/) (verified) |
| **Blades in the Dark** | "If it's common knowledge, the GM will simply answer your questions. If there's an obstacle … an action roll … not common knowledge but no obstacle, a simple fortune roll determines the quality." "The GM always answers honestly, but with a level of detail according to the level of effect" (Limited, Standard or Great). | Access, risk and depth are separate decisions. | [Blades SRD, Gathering Information](https://bladesinthedark.com/gathering-information) (verified) |
| **Ironsworn / Starforged** | Gather Information on a strong hit: "you discover something helpful and specific". On a weak hit, insight that complicates things. Content comes from Ask the Oracle or Action/Theme prompts. The outcome band fixes what *kind* of content must appear; the oracle fills it. | Oracle answers are accepted as canon. | [Starforged SRD adventure moves](https://rsek.github.io/starforged-srd/moves/adventure) (verified) |
| **Mythic GME 2e** | The player *proposes* a yes/no question with odds and the Fate Chart answers. Meaning Tables cover open questions. NPC behaviour: expected action → test it with a Fate Question → Meaning Tables if there is no expectation. | "Expectations and interpretations based on the ongoing Context". The proposer frames; the dice decide. | [Mythic 2e PDF](https://bryanmiller.us/pdf/mythic-game-master-emulator-2nd-edition.pdf) (verified, ToC and intro) |
| **Sly Flourish** | Ten "secrets and clues" are prepped *without a location* and attached to whatever plausible conversation or search comes up. | Prepared content, improvised delivery. | [Secrets and Clues](https://slyflourish.com/sharing_secrets.html) (per Exa summary) |

**What these traditions share.** None of them lets a successful information action return nothing. Each one
separates three things:

1. **Access:** may the PC get at the answer at all?
2. **Depth:** how much does the PC get?
3. **Authorship:** who decides what the content is?

GUMSHOE and Alexander fix content in prep. Dungeon World, Starforged and Mythic create it in play, but commit it
the moment it is stated. Blades adds the piece this project is missing: a **common-knowledge branch** that needs
no roll at all.

### 2.2 Games: lazy, persistent generation and structured content

- **Caves of Qud** generates historical events first and then *rationalises* their causes. When the state has
  no suitable cause, "the event can even create one by … altering the sultan's allied factions … the effect
  causes the cause." Gospels are placed lazily as shrines and engravings during exploration, and enter a
  journal once found. Grinblat & Bucklew, FDG 2017
  ([PDF](https://freeholdgames.com/papers/Generation_of_mythic_biographies_in_Cavesofqud.pdf), verified). This
  is exactly the pattern a "who did it?" asked mid-play needs: build the case behind the question, then answer
  from it.
- **Dwarf Fortress, Elite, No Man's Sky:** a seeded base world that can be rebuilt, plus persistent deltas.
  Lesson: use keyed per-entity seeds, so a generated answer does not change with the order of exploration
  (per Exa summary; [Adams interview](https://dhs.stanford.edu/algorithmic-literacy/an-interview-with-tarn-adams)).
- **Ultima Ratio Regum** keeps `world_fact`, `evidence_seen` and `character_knows` separate. NPC enquiries are
  structured lines filtered by status and knowledge
  ([0.8 release](https://www.markrjohnsongames.com/2020/12/27/ultima-ratio-regum-0-8-released/); per Exa
  summary).
- **Storylets and QBN.** Emily Short: storylets unlocked by qualities, and *salience-based* selection, where
  "it's relatively easy to build a rudimentary set of content with sensible, broad defaults, and then gradually
  add new, more salient content"
  ([Beyond Branching](https://emshort.blog/2016/04/12/beyond-branching-quality-based-and-salience-based-narrative-structures/),
  verified).
- **Kreminski & Wardrip-Fruin (ICIDS 2018)** describe *parametrized storylets* (Starfreighter): "dynamic queries
  that treat the game state as a database … 'bind' them to named parameters. A parametrized storylet may only be
  presented … if all of its parameters are successfully bound"
  ([PDF](https://mkremins.github.io/publications/Storylets_SketchingAMap.pdf), verified). This is the
  principled form of what `bind_incident` and `settle_who` do by hand: **casting roles onto existing entities
  by query.**
- **Wildermyth** binds heroes to event roles by aspects and relationships. If no candidate fits, the event is
  not eligible, rather than inventing someone
  ([Story inputs and outputs](https://www.wildermyth.com/wiki/Story_Inputs_and_Outputs); per Exa summary).

### 2.3 NPC social simulation

- **Versu.** Social practices are "reactive joint plans, providing affordances … The practices never control
  the agents directly." Each agent chooses by utility, and only among the affordances of the practices it is
  part of. Evans & Short, IEEE TCIAIG 2014
  ([PDF](https://www.cs.uky.edu/~sgware/reading/papers/evans2014versu.pdf), verified).
  - This answers "what may an NPC do this turn" with a small, legal action set per practice: greeting, trade,
    conversation, work.
- **Comme il Faut / Prom Week.** *Volition*, the initiator's desire, is scored separately from *acceptance*, the
  responder's score of at least 0. Effects are committed before they are realised in text. About 4,900 rules
  and 30 exchanges (AIIDE 2011; [PDF](https://mtreanor.com/publications/CiF-AIIDE2011.pdf); per Exa summary).
- **Façade.** Each beat has a canonical progression plus reactive interruptions: about 2,500 joint dialogue
  behaviours, 27 beats, about 15 per run
  ([AIIDE 2005](https://cdn.aaai.org/AIIDE/2005/AIIDE05-016.pdf); per Exa summary). The lesson is that every
  NPC needs a **default next action** that runs when nothing salient happens.
- **Generative Agents (Smallville).** Running 25 agents for two game days cost "thousands of dollars"
  (per Exa summary of the paper's limitations). The commonest errors included agents that "fabricated
  embellishments to the agent's memory" ([arXiv 2304.03442](https://arxiv.org/pdf/2304.03442), verified).
  - This is the direct warning against Option A below: an LLM authoring NPC knowledge freely will embellish it.
- **Project Sid, Inworld, Convai.** Knowledge filters and per-character knowledge banks scope what goes into
  the context. They do not stop parametric leakage (per Exa summary).
- **TimeChara (ACL Findings 2024).** Point-in-time character hallucination is significant even in GPT-4o
  ([ACL](https://aclanthology.org/2024.findings-acl.197/), verified). The Exa summary reports that naive RAG made
  future-knowledge leaks *worse* (46% → 33.5% consistency) and that a cut-off expert method raised it to 95.5%
  (figures not re-verified).
  - Lesson: **filter what an NPC may know before retrieval**, not after.
- **SHARP (2024)** and **"Too Nice to Tell the Truth" (2026)** find that role-play agents' factual stance
  follows their affection toward the speaker (per Exa summary). This supports 12.11.4's existing remedy: decide
  accept or refuse in code, and let standing change tone and willingness, never truth.
- **Neuro-symbolic hybrids.** IVIE and PAYADOR, and "World-State Transformations"
  ([arXiv 2605.24719](https://arxiv.org/html/2605.24719v1); per Exa summary), follow the same loop: the LLM
  proposes a typed transformation, a symbolic validator checks it, it is committed, and only then narrated. This
  is the closest published precedent for the shape recommended here.

---

## 3. I-153: three ruled designs

**The question:** may a successful Talk reveal ordinary information the world does not yet hold?

**A guarantee common to all three options (recommended either way).** A successful Talk always delivers at least
one of the following, and never nothing:

- (a) a stored fact the NPC knows;
- (b) a newly settled ordinary fact;
- (c) a case placement (a core clue);
- (d) an honest **"I don't know"** together with a **pointer**: a real person or place that would know, chosen
  by procedure.

(d) is Dungeon World's "Nothing, sorry" made playable, and Alexander's proactive lead. P-120 showed that a bare
"no" reads as a failure. A "no" plus a real lead does not.

### Option A: narrator-authored common knowledge (write-on-answer)

- On a success, the narrator may state ordinary, non-secret information the NPC would plausibly know.
- The Checker types each statement. Ordinary statements are written as the NPC's fact (`source: narration`) and
  a knowledge record. Clue, person-with-want and secret kinds are cut.
- **Pros:**
  - cheapest;
  - most fluent;
  - closest to Blades' "the GM will simply answer".
- **Cons:**
  - The DM chooses what is true, against 12.6.1 as written.
  - The "ordinary vs clue" line is drawn after the fact by an extractor, which is the noisiest step (theme B).
  - The same question asked twice drifts, because there is no deterministic answer (P-063).
  - Embellishment risk: the Smallville finding.
  - Gemini Flash will push the line harder than Haiku did.
  - It also makes theme B's job harder, because every Talk creates unverifiable new facts.

### Option B: tables only (every answer from a generator)

- The Reader classifies the question into a **closed set of question kinds**, Dungeon World style:
  - who is X;
  - where is X;
  - what happened;
  - what is X like or for;
  - what do you want or think;
  - who would know.
- Each kind has a procedure that never involves the LLM:
  - first, the store and the NPC's knowledge;
  - then the 12.10.6 knows-check (the Oracle at role-fit odds);
  - then content from a table (casting among existing NPCs; the place graph; topic tables; `tbl.meaning`);
  - the result is written with `source: table`, then delivered.
- **Pros:**
  - 12.6.1 holds exactly;
  - reproducible from the seed;
  - unit-testable;
  - the Checker has nothing to guess, because answers exist before prose.
- **Cons:**
  - Authoring cost: topic tables per role.
  - Answers can read as stilted.
  - Coverage gaps for off-list questions, such as "what did the healers say?".
  - Question classification becomes a new model choice; it is small, but theme D warns about such choices.

### Option C (recommended): tiered answer ladder with propose-and-ratify for ordinary facts

- **Route by content tier**, defined in §4.1:
  - **Consequential questions** (culprit, missing person's whereabouts, secrets, threads) → only the case graph.
    If no case exists behind a story-role question, run a reduced PR-15-6 *now*, Caves of Qud style, and answer
    from its placements.
  - **Ordinary questions** → the ladder:
    1. **Store.** The NPC's knowledge records and public facts in scope (today's `deliver_learning` ranking).
    2. **Knowledge pack.** The NPC's 2–4 seeded facts, plus their role's *topics* (data).
    3. **Propose and ratify.** The narrator's structured output proposes one candidate answer, typed
       `{kind: ordinary_fact, subject, predicate, value}`. The engine asks the Oracle "Does <NPC> know that
       <candidate>?" at 12.10.6(d) odds: Likely if on a role topic, Unlikely otherwise.
       - Yes → write the fact (`source: oracle`, `proposed_by: narrator`) and a knowledge record.
       - No → the NPC doesn't know; go to step 4.
       This is Mythic's procedure exactly: the proposer frames, the dice decide. It already holds under
       00.12.7, where the DM frames the question and its odds.
    4. **Pointer.** Who would know, chosen by casting (§4.3), never "the first present person".
- **Depth by delivered reach** (T-15-5 / T-01-6, Blades' effect levels):
  - Limited: rungs 1–2 only, partial answers.
  - Standard: rungs 1–3.
  - Great: rungs 1–3, and the NPC volunteers one extra (a want, or a lead).
- **Pros:**
  - 12.6.1 holds: dice, not the DM, decide truth.
  - Fluent answers, without authoring a table for everything.
  - Each answer is typed before the prose, which collapses theme B's extraction problem for Talk turns.
  - Consistent: a stored answer is found at rung 1 next time.
  - "Doesn't know" is persisted as well.
- **Cons:**
  - Proposals are still biased toward what the LLM finds interesting. This is selection bias, bounded by the
    odds and the tier filter.
  - The "ordinary" type label is a model output, but it is checked by code (`kind` comes from a closed list,
    and the subject or predicate may not touch a sealed fact).
  - It needs B's declare-then-verify output.
  - The owner must accept that "propose then roll" satisfies 12.6.1.

**Recommendation: C.** It is how the strongest solo-play tradition (Mythic and Starforged) reconciles "no GM
chooses truth" with "success always yields content". It turns the engine's existing after-the-fact Oracle hack
into a typed, pre-narration step. B's tables become the floor where proposals are weak. Specifically, use casting
for every "who" and "who would know", so names never come from the LLM.

---

## 4. Ranked concrete proposals

Gemini Flash costs below use list prices of about **$0.30/M input and $2.50/M output** (Gemini 2.5 Flash).
Re-check against the model actually deployed. A 15k-token packet is roughly 0.45¢ of input.

### 4.1 P1: the three-tier content contract, typed (rules first)

**Rules.** Rewrite 12.14.13 and PR-00-7 around three tiers, each with its own **origin rule** and **check rule**:

| Tier | Contents | May originate from | Written | Checked (B) |
|---|---|---|---|---|
| **T0 Atmosphere** | Light, smell, sound, mood, unnamed crowd behaviour | Narration, freely | Never | Only against location, time and safety (I-127, as now) |
| **T1 Ordinary** | Furniture (from the place-type table if asked about), a present NPC's continuing activity, ordinary documents' gist, **ordinary knowledge** (local geography, prices, trade facts, public news) | Seed packs, tables, **or propose-and-ratify** (Oracle) | On mention or on answer, with `source` and `proposed_by` | Narration must match a declared T1 item; an undeclared T1 item is written on mention if its `kind` is T1 |
| **T2 Consequential** | Clue, item beyond common value, hazard or trap, adversary, person with a want, secret, thread knowledge, *the identity of a story role* | **Only** generators: case builder (PR-15-6/7), NPC generation 12.11.1, ch.10 tables, loot (00.11), casting (§4.3) | At generation, sealed until unsealed | Strict: must be in this turn's record as delivered or unsealed; otherwise cut |

- The narrator's declarations carry `element_kind` from a closed list: `furniture | feature | person | item |
  document | knowledge | clue | hazard | adversary`. This is I-129's fix.
- `_FORBIDDEN_NEW` becomes a lookup from kind to tier.
- Revise **I-128** so that a continuing, non-consequential activity is a T1 `position/activity` claim checked
  against presence. `action` stays for deeds that change something.

**Engine.**

- `engine/audit/claims.py`: replace `_forbidden_new` with a tier lookup on the declared kind.
- `engine/dm/mentions.py` writes T1 declarations.

**Supersedes:**

- `_FORBIDDEN_NEW` and its `ponytail:` comment (I-129);
- the addressed-speech exception (I-140a), absorbed by P4;
- the I-128 cutting of standing activity.

**Interactions:**

- **A (memory):** T0 is never stored. T1 is stored at low salience and retrieved by entity or place. T2 is high
  salience and pinned to thread or journal.
- **B (claims):** this contract tells B which sentences need checking. Only T1 and T2 declarations are claims.
- **D (adjudication):** none.

**Cost:** zero extra calls. The declarations ride on the narrator's structured output (B's proposal).

**Test:**

- A fixed seed-and-script regression: count cut T0 sentences (target 0), and T2 kinds that appear undeclared
  (target 0).
- Unit tests on the kind-to-tier table.

### 4.2 P2: the Talk answer ladder (I-153 Option C)

**Rules.**

- **New procedure PR-12-x "Answering a question"** in 12.10, with steps exactly as in §3 C.
  - Its trigger is a resolved Talk, Observe or Recall whose restatement carries a `question_kind`.
- **12.10.6(d)** becomes data-driven: `social.yaml#common_knowledge`. For each role tag, it lists topics at
  Likely; anything else is Unlikely. Settlement scope adds public facts and seeded rumors. Examples:
  - innkeeper: travellers, roads, prices;
  - gate captain: arrivals, faction tensions, the watch;
  - healer: the sick and injured, herbs.
- **T-15-5 / I-140(b):** how many items each reach delivers. Proposal: Limited = 1, Standard = ⌈N/2⌉ or 1
  ratified, Great = all plus one volunteered.
- **00.12.7:** add the *proposal form*. A candidate answer is asked as a yes/no at role-fit odds, and "a 'no'
  to a knowledge question is followed in the same breath by who would know" (extends P16).
- **12.6.1:** add one clause. "Proposing a candidate and letting the Oracle settle it is not choosing; stating
  it unsettled is."
- **T-12-4:** add two rows:
  - "who is <role>" → casting (§4.3);
  - "what <NPC> knows about <topic>" → PR-12-x.

**Engine.**

- New `engine/dm/answer.py`, about 150 lines, called from `deliver_learning`.
- The Reader schema gains `question_kind` (an enum of 6) and `topic`.
- The narrator schema gains `proposed_answer` (one typed fact).
- Ratification runs **before** the narration draft. Practical route: a two-pass Talk turn, or the World role's
  call (P4) proposes, since it already sees the NPC.

**Supersedes:**

- `world_step._talk_answers`, `_who_questions`, `_WHAT_ASKED`, `_NAME_OF`, `_WHO_ASKED`;
- the "name one concrete thing" narrator notes (P-086 note, P-120);
- the thread-as-answer and first-present-person fallbacks;
- `claims._learning_success → undetermined`;
- `incident.settle_who`'s `asked=True` path;
- the "responds as the talk went: success" placeholder (P-025).

**Interactions:**

- **A:** every answer writes `(npc, question_kind, topic) → fact_id | "unknown"`, an **asked-and-answered
  index**. A repeat question hits rung 1, which gives consistency (P-063) and is cheap to retrieve. Salience:
  medium. It becomes high when the PC records it in the journal or it touches a thread.
- **B:** a Talk turn's factual content is pre-declared, so the Checker only confirms that the prose matches the
  declared answer.
- **D:** following Blades, common knowledge asked of a non-hostile NPC is a *certain* Talk with no roll. This
  removes a large share of harsh-odds exposure (I-158) from purely informational asks.

**Cost:** at most one Oracle roll (free), plus about 100 output tokens of proposal riding an existing call: about
0.03¢. If a separate proposal call is needed, about 2k tokens in and 100 out: about 0.09¢.

**Test:**

- Talker persona metric: **empty-success rate** (successful learning beats with no item and no pointer), target
  0. Today it is the dominant complaint in 205857-newcomer.
- Ask-twice consistency: same fact id, 100%.
- Seed replay determinism.
- A seeded sim in `rules/_process/simulation/` of "knows" vs "pointer" rates by role odds, to calibrate the
  Likely and Unlikely rungs so that "I don't know" stays below about 35% of ordinary asks.

### 4.3 P3: casting by role fit (a gate→fill domain), plus a reduced case builder for T2

**Rules.**

- **00.11: register a `cast` domain.**
  - The pool is the existing NPCs, gated by role tags, home or scope, `member_of`, and not sealed, the PC, the
    anchor bond or a far power. This reuses `incident._people`'s filter, which is a genuinely good piece.
  - The fill is weighted by fit (role tags of the asked role × place × faction).
  - If the pool is empty → generate a new NPC (T-12-4 "a person who must exist now", 12.11.1) or answer "no one
    you know", by table.
  - This answers I-140(c) and I-148's "proper who-is-X table with role fit".
- **12.16.16: the inciting incident runs PR-15-6 at seed time, in reduced form:**
  - a solution: the subject or culprit cast from the cast;
  - 2 necessary nodes;
  - 3 placements each (a reporter, witnesses, a place or document);
  - 1 core placement at the opening place.
  - This answers I-145.
- **PR-15-6 "mystery arising in play":** a story-role "who" question with no case behind it triggers the same
  reduced builder (the Qud pattern). The NPC answers from a placement if they hold one, else gives a pointer to
  a holder.
- Pull `h.15.placement_audit` forward from M6 to M1 for these reduced cases, so the Three Clue Rule actually
  holds.

**Engine.**

- `engine/gen/case.py`, reading the existing `rules/data/investigation.yaml#clue_graph_template`, `#validity`
  and `#tables`.
- Casting is a `gen` config, not new code paths in `dm/`.

**Supersedes:**

- `incident.bind_incident`, `SUBJECTS`, `STORY_ROLES`, `WHO`, `settle_who` (I-148);
- the P-067 fix (00b6534);
- the uniform-random `ponytail:` pick.

`incident_line` can survive as a renderer over the case's known facts.

**Interactions:**

- **A:** case nodes and placements are T2: sealed, high salience. Unsealing writes the PC's knowledge record.
  The journal (T-15-15) is the PC-facing memory.
- **B:** sealed content never reaches the packet (INV-10). Only unsealed placements are claimable.
- **D:** core placements are delivered without a roll (15.9.5). Other placements follow `request_size` and
  refusals, which keeps Alexander's leveraged clues and avoids GUMSHOE's flattening.

**Cost:** seed time only, zero LLM. In play, a case built mid-session is code plus table rolls.

**Test:**

- PR-15-6 validity checks as unit tests.
- Regression: "who is missing?" is answerable within 3 turns in 100% of seeded openings, against P-067's
  "never".
- Sim: placement liveness over 30 scripted sessions.

### 4.4 P4: default NPC layer (theme C)

**Rules.** A new 12.11.9, "Every present NPC has a default". Versu practices and the Façade canonical beat,
simplified:

1. Each present NPC has an **activity**, rolled when they enter the scene from `role × hour` (data: the smith
   at the forge, a guard on watch). It is written as a T1 position or activity fact. This settles I-128 and
   removes the need for exceptions such as P-056 and P-095.
2. Each turn, the scene's **practice** (greeting, trade, conversation, work, fight, crowd) gives a small set of
   legal responses. Choose in this order:
   - a resolved frame;
   - else a recorded refusal or want whose tags match the event (CiF-style volition, scored in code);
   - else `tbl.npc_action` by standing (12.11.5, as now).
3. **An addressed NPC always answers:** either via PR-12-x, or with a refusal *spoken in their voice*
   (`tbl.npc_refusal` + voice habit). This fixes P-114's identical "Not now".
4. Accept or refuse is code (CiF's acceptance score of at least 0). Standing changes tone and willingness,
   never truth (SHARP).

**Engine.**

- Replace the World role's LLM call (`roles/world.npc_responses`) with tag matching between the event
  (verb, target, topic) and the motive tags in `npc_motives`.
- Keep the World role only as an optional tie-breaker when two or more motives match.
- Reuse what exists: `present_npcs`, `first_interaction`, the `tbl.npc_action` roll.

**Supersedes:**

- the addressed-speech exception (I-140a);
- the "talk with no target speaks to the only NPC" special case (keep it as practice logic);
- I-128's interim cutting.

Keep the P-118 and P-056 fixes as tests.

**Interactions:**

- **A:** NPC memory of the PC (12.11.7) gets one event per *resolved* exchange. Routine activities are T1 low
  salience, and are overwritten rather than appended.
- **B:** NPC actions are pre-declared entries in `record.npc_actions`. The Checker matches prose to them.
- **D:** none, beyond Talk frames.

**Cost:** saves one LLM call per turn when NPCs are present, about 0.4–0.6¢, which is a significant fraction of
the 1–3¢ budget. The added code is deterministic.

**Test:**

- Unanswered-address rate: target 0.
- Distinct refusal lines across 3 NPCs: target 3.
- A seeded replay must produce the same NPC responses.

### 4.5 P5: a richer world seed (content packs)

**Rules.**

- **12.16.9 / 12.4.3 (I-130):** every place gets:
  - a one-line **look** (place-type descriptor × region `tbl.*.furnishings`; the Thallen table already exists);
  - **2–4 furniture items**;
  - its **exits** (from the route graph).
- **12.16.11:** every cast NPC gets:
  - **2–4 knowledge facts**: one about their trade (role topic), one local or public, one about another cast
    member (a tie), and optionally one rumor from 12.16.14 that they hold;
  - a **stance** toward the incident or faction (Oracle by tie).
- **12.16.17 seed check:** add "every haven place has a look and at least 2 furniture items; every cast NPC has
  at least 2 facts; the incident case validates".
- **I-149:** a local PC knows the names of the haven's officers listed in 12.16.11 (smith, innkeeper, captain,
  healer, wise one) and of local faction heads. An outsider knows none.
- **Documents.** A seeded notice, bill or charter is a `document` with a `text` fact, from a document table:
  hire, warning, charter or bounty, with fields. If a lead points to it, its text names the lead's target. This
  addresses P-054 and generalises the P-110 fix.

**Engine.** `engine/gen/_seed_steps.py` (`place` and `cast` steps), `_seed_check.py`, and `world_seed.yaml`
defaults.

**Size:**

- A haven of about 10 places × about 4 facts, plus about 10 cast × about 4 facts, plus a case of about 15
  facts: roughly **100–120 extra facts**.
- That is about 3–5k tokens if all of it were rendered. It is not: only the present place and NPCs go into the
  packet, about 300–600 tokens per turn.

**Supersedes:**

- the `scene_setting` padding role (keep it as the renderer);
- most write-on-mention churn at the opening;
- the P-079 opening-fallback pressure.

**Interactions:**

- **A:** seed facts are the long-term backbone, at medium salience and indexed by entity.
- **B:** more grounded material means fewer new elements to check.
- **D:** furniture becomes citable levers (12.14.13's worst case: at most +2).

**Cost:** zero LLM at seed if table-driven. Optionally, one seed-time call to polish the "look" lines, as
atmosphere only, under 1¢ once.

**Test:**

- Seed-check assertions.
- Opening narration length and concreteness in the regression set.
- The explorer persona's count of "nothing to look at".

### 4.6 What not to build

- **Generative-agents-style simulation of every NPC each turn.** Smallville's cost and its embellishment errors
  rule it out.
- **Retrieval of NPC knowledge without pre-filtering.** TimeChara shows it worsens leaks.
- **LLM-judged storylet triggers** (Drama Llama). Predicates belong in code.

---

## 5. Fixes to keep versus fixes to retire

**Keep. These are good ideas; fold them into the new structure:**

- **d06505c:** delivering stored facts ranked by relevance. It becomes rung 1 of PR-12-x.
- **cf4d28c (P-110):** reading delivers a document's words first. Generalise it via document entities (P5).
- **44d181e (P-056/P-061):** mid-scene NPCs join `cast_present`, and the narrator quotes NPC words.
- **1fc7fe8 (P-118):** the addressed NPC answers, not a bystander.
- **db07b1d / 4be967b (P-069):** names as knowledge, per 12.10.2. Keep, with I-149's rule from P5.
- **P-086's "stalled after two failures" (12.14.8):** failure as the world's answer. Keep it as is.
- **f4caed6 (P-099):** positions written in a fight.
- **`incident._people`'s exclusion filter:** reuse it as the casting gate.
- **`scene_setting` in `packet.py`:** keep it as the renderer of seeded looks.

**Retire, superseded:**

| Retire | Superseded by |
|---|---|
| `incident.bind_incident`, `SUBJECTS` (I-148, 00b6534/P-067) | P3, the reduced case at seed |
| `incident.settle_who`, `STORY_ROLES`, `WHO`, `NO_ONE` path, uniform-random `ponytail:` | P3 casting, P2 ladder |
| `world_step._talk_answers`, `_who_questions`, `_WHO_ASKED`, `_WHAT_ASKED`, `_NAME_OF`, `_ASKS_NAME` regexes | Reader `question_kind` enum, P2 |
| Narrator notes "name at least one concrete thing" / "answer plainly … one concrete, ordinary thing" (P-086 note, ab69f6f/P-120) | P2 propose-and-ratify, typed before narration |
| Fallbacks "gives what they can: <top thread>" and "<first present> might know more" | P2 rung 4, the casting pointer |
| `claims._learning_success → undetermined` (the after-the-fact Oracle) | P2 ratification before the draft |
| `_FORBIDDEN_NEW` keyword proxy (I-129) | P1 typed `element_kind` and tier |
| The addressed-NPC speech exception in claims (d06505c part, I-140a) | P4 declared NPC responses |
| "responds as the talk went: success" placeholder (P-025) | P2 declared answer |
| The World role's LLM call, as the default path | P4 code volition (the LLM becomes a tie-breaker only) |

---

## 6. Rule ids to revise, with outline text

- **12.6.1:** add "Proposal is not choice: the DM may frame a candidate answer and settle it by the Oracle at
  odds fixed before the roll (00.12.7). Stating an unsettled candidate is choosing."
- **00.12.7:** add the proposal form, and "A 'no' to whether someone knows is followed by who would know
  (casting, 00.11 `cast`)."
- **00.11.1:** register the `cast` domain (pool: existing NPCs gated by role, scope and seal; fill: weighted by
  fit; empty pool → 12.11.1 or 'no one you know').
- **00.6.6 / PR-00-7:** step 1 lists each element with its `element_kind`. Step 2 routes by tier: T0 skip; T1
  write; T2 → its owning procedure, or cut.
- **12.14.13:** replace the prose list with the three-tier table (§4.1). Keep the `[J:flag]` question for kind
  assignment only, and make "uncertain → T2".
- **12.10.6:** (d) reads from `social.yaml#common_knowledge`. Add (e): "an NPC's answer, once settled, is a
  knowledge record; 'does not know' is recorded too."
- **12.10 new PR-12-x "Answering a question":** the ladder (store → pack → propose-and-ratify → pointer); depth
  by reach; never empty.
- **T-15-5 / T-01-6:** item counts per reach for Talk (I-140b).
- **12.11.4–12.11.5, new 12.11.9:** the default NPC layer (activity, practice, volition, the addressed NPC
  always answers, refusal spoken in voice).
- **12.2.9:** an NPC's sources gain "default activity (12.11.9)" and "answer (PR-12-x)".
- **12.13.4:** improvised content gets T1 only, by procedure. Never T2.
- **12.16.9, 12.16.11, 12.16.16, 12.16.17, 12.4.3:** the seed packs (§4.5), the reduced PR-15-6 for the
  incident, and the seed-check rows.
- **PR-15-6 / 15.9.4:** a "reduced case" profile for M1 (2 nodes, 3 placements, 1 reserve), and its trigger
  from a story-role question.
- **12.10.2 / I-149:** who a local PC knows by name.
- **Ledger rows each change closes:** I-153, I-140, I-145, I-148, I-149, I-128, I-129, I-130.

---

## 7. Risks and open questions for the owner

1. **Does propose-and-ratify satisfy "the DM never chooses what is true"?** I argue yes, as in Mythic, but it is
   a philosophical call. If no, choose Option B and budget for writing role topic tables (about 20 roles × 6
   topics).
2. **Does an honest "I don't know" plus a real pointer count as a success?** I recommend yes, at Limited reach
   at least. Otherwise the ladder must always produce a fact, which pushes toward Option A.
3. **Pulling a reduced 15.9 into M1.** This is the honest replacement for `incident.py`, but it is new scope:
   roughly `case.py` at 300–400 lines plus the audit handler.
4. **Store growth.** Ratified T1 facts accumulate. Agent A should treat T1 as evictable from the packet, but
   never deleted, since the event log persists. Low salience is not the same as forgettable when it comes to
   consistency.
5. **Proposal bias.** The LLM proposes interesting answers, and the Oracle says yes at Likely odds about
   65–75% of the time. The odds rung and the T1 filter bound this, but a seeded sim should check that ratified
   facts do not cluster into accidental clues. Audit by sampling: are any ratified T1 facts later cited as
   levers worth more than +2?
6. **The quality of question-kind classification on Gemini Flash.** An enum of 6 is small, but measure it on
   the 62-run transcripts before building on it.
7. **GUMSHOE flattening.** If every Talk always yields, NPCs can feel like vending machines. Keep refusals,
   `request_size` and leveraged placements. Allow lying only via 15.6.2's reason-to-lie flag.
8. **Interface dependency on B.** P1 and P2 assume the narrator emits typed declarations. If B chooses
   a different design, P2's ratification can run in the World role's call (P4's tie-breaker) or a small
   dedicated call (about 0.09¢).
