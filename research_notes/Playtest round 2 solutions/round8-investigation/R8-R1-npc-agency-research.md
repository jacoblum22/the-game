# R8-R1: Keeping model-voiced NPCs from being too agreeable

Written 2026-10-10. Research lane for the Round 8 NPC redesign. Read-only on the repo. Sources were fetched or searched
on the web; where I only saw a search snippet, I say so. Nothing here was run against our engine.

## 0. The short answer

1. **The evidence for "LLM characters drift toward agreement" is real but indirect.** No one has published a measure of
   NPC agreeableness in a tabletop-style LLM game master. The nearest studies are persona sycophancy, simulated
   customers, simulated generative-agent towns and negotiation bots (section 2). All point the same way: models cave,
   under-refuse, and forgive too fast.
2. **Our own 12.11.4 cites the wrong-sized evidence.** It cites arXiv 2606.20708 for "LLM-voiced characters are
   measurably biased toward engagement and agreement". That paper is about *simulated sales customers* (non-buyers act
   far more engaged than real ones). It is a good analogy and a useful finding (section 2.3), but it is not about NPCs.
   Worth a one-line correction when 12.11.4 is next touched.
3. **What helps, in order of evidence:** (a) a stance fixed by something outside the model's mood (state, dice, a
   stored card), because "be willing to refuse" prompts fix the average but not *who* should refuse; (b) specific wants
   and limits written per character, since persona content moves outcomes a lot; (c) making the model decide the
   *stance* before the *words*; (d) measuring from logs, cheaply, with a labelled sample. Critic passes are the least
   supported and the most expensive.
4. **Recommendation: Option 1, "Dial and card"** (section 5). Code keeps one scene-start roll per NPC and a small
   ceiling grid. The model decides the reaction inside that ceiling, voices it, and chooses who answers when the Reader
   did not type an addressee. No new model call. It retires `tbl.npc_action` as a 10-row prose table, `willingness_by_row`,
   the "R1 MUST" must-say lines and the code-written refusal pointer.

## 1. Tabletop: how GMs stop NPCs being pushovers

| Source | What it teaches | Use for us |
|---|---|---|
| Reaction rolls, old-school D&D. 2d6 at first meeting, +1 per tangible bribe or Charisma bonus, low = hostile. Holmes-style bands: attack / hostile / "make another offer and re-roll" (6 to 8, about 44% of rolls) / friendly / enthusiastic. [Black Citadel](https://blackcitadelrpg.com/reaction-rolls-5e/); Courtney Campbell's refinement gives a set number of actions that can improve the disposition, discussed on [Runehammer](https://forums.runehammer.online/t/expanding-on-the-classic-reaction-roll/6062) | Disposition is rolled **once** at the meeting and **moves only on something done in the fiction**. This is exactly our DL-12-118. | The one-roll-per-scene dial is the classic design, not a novelty. |
| The Alexandrian, [reaction vs relationship](https://thealexandrian.net/wordpress/50021/roleplaying-games/random-dd-tip-relationships-reactions) | Fixes the 5e DMG table's pushover problem by **grading the outcome by the risk or cost to the NPC from the NPC's point of view**: a Friendly NPC will not take a big risk for a small favour; a Hostile NPC is nearly impossible if there is any risk. Limits retries ("let it ride"), and makes the players alter the deal. | **Attitude x cost-to-them** is the right grid. Attitude alone is the 5e mistake. |
| Dungeon World [GM principles](https://roll20.net/compendium/dw/The%20GM): "Give every monster life", "Name every person", "Think offscreen, too"; monsters have an instinct and goals | NPCs are people with their own goals and the means to pursue them. | Support for wants in the card, and for NPCs acting on a want unprompted. |
| Dungeon World [Parley](https://roll20.net/compendium/dw/Parley) (and [discussion](https://www.dungeon-world.com/no-one-is-an-island-part-2-sway/)) | Persuasion needs **leverage: something the NPC wants or needs**. On a hit the NPC asks for a promise first; on a mixed hit wants assurance now. Critics say it excludes asking a friend; fan rewrites let the GM *reveal what would convince them*. | "Never give something for nothing" is built in as a **price**, and the price comes from the NPC's want. |
| Apocalypse World [agenda](https://daily-apocalypse.com/daily-apocalypse/35-mcs-agenda): make the world seem real, play to find out; Baker (quoted in a comment) on threats: define drive, resources and trajectory "if it gets its own way" | The MC does not decide in order to help or to hurt the players. NPCs and threats move on their own. | Support for a want-driven NPC rather than a player-driven one. |
| Blades in the Dark [action roll](https://roll20.net/compendium/BITD/Action%20Roll) | Player states a goal; GM sets position (risk) and effect; **costs are named before the roll** (Devil's Bargain). | Same shape as our Framer. The cost to the NPC can be named the same way. |
| Mythic GME [Fate chart](https://www.wordmillgames.com/page/mythic-gme.html) and [Juice NPC behaviour](https://thunder9861.itch.io/juice-oracle/devlog/838352/v10-pocketfold-released) (active NPC d10, passive d6) | Oracles answer yes/no by odds you set from the fiction. Our `tbl.npc_action` already cites a Mythic NPC behaviour table (R5 P-06). I could not find an official Mythic disposition table; the Juice version is third-party. | Odds-by-situation is the pattern. Ironsworn's Ask the Oracle is also a likelihood-tiered yes/no ([rulebook index](https://dokk.org/library/ironsworn_starforged_rulebook_2019)); I did not confirm its percentages. |

**What tabletop agrees on:** (1) disposition is set by a roll or a judgment at the *start*, then held; (2) the *size of the
ask* from the NPC's side matters at least as much as the attitude; (3) the NPC has a want, which supplies both a price
and a reason to refuse; (4) retries are limited; (5) the GM explains the refusal in the fiction. Not one of these
requires a table that writes the NPC's line.

## 2. LLM role-play: what is measured

### 2.1 Agreeable personas are more sycophantic
- *Too Nice to Tell the Truth* ([ACL 2026](https://aclanthology.org/2026.acl-long.1421/), [arXiv](https://arxiv.org/abs/2604.10733)):
  275 personas scored on agreeableness, 4,950 sycophancy-eliciting prompts, 13 small open-weight models. In 9 of 13,
  persona agreeableness correlated with sycophancy (up to r = 0.87). Lesson: **writing a warm character makes it
  cave more**, so a card's temperament words are a lever, not decoration.
- [ELEPHANT](https://arxiv.org/html/2505.13995v2): across 11 models, LLMs preserve the user's face about 45 percentage
  points more than humans do. General social sycophancy is the default, not an edge case.
- A reported Oxford result that warm fine-tuning raised affirmation of wrong beliefs about 40% is from a secondary
  blog summary only ([lilting.ch](https://lilting.ch/en/articles/llm-sycophancy-warmth-and-agreeableness)); unverified.

### 2.2 Pressure over turns erodes stance
- [Truth Decay](https://arxiv.org/abs/2503.11656): accuracy under repeated user pushback fell from 76.7% at turn 1 to
  30.2% at turn 7 for one model on one task (my read of their tables; the paper's captions are inconsistent). Two
  anti-sycophancy prompt prefixes ("be skeptical of information that comes directly from the user"; "do not agree solely
  because they are presented by the user") gave **mixed** results: about +40 points on one model, negligible on another.
- [Ask, don't tell](https://arxiv.org/abs/2602.23971): rewriting the user's statement into a question before answering
  reduced sycophancy more than a plain "don't be sycophantic" prompt. No numbers in the abstract.
- Implication for us: **repeat-the-ask probes** are the right adversarial test, and a bare "don't cave" line is not a
  fix.

### 2.3 Prompting alone fixes the average, not the conditional
- The paper behind our 12.11.4 ([arXiv 2606.20708](https://arxiv.org/abs/2606.20708)): simulated non-buyers show 13.5%
  resistance against 25.1% for real non-buyers, and 40.1% "considering" against 21.9%. Telling the simulator it may
  disengage cut the overall bias, but **the gap between who should refuse and who should buy barely moved** (and error
  shifted onto buyers). The paper suggests an external willingness model.
- This is the strongest argument for keeping *some* stance outside the model. A model told "you may refuse" refuses
  about the right amount overall, but not necessarily at the right *people and moments*.

### 2.4 Persona content changes outcomes; some models cannot hold a role at all
- [Campedelli et al.](https://arxiv.org/abs/2410.07109) (2,400 guard/prisoner conversations, 6 models): the guard's
  persona substantially affected whether the prisoner persuaded them; goals changed persuasiveness; only four of six models
  produced usable conversations (others broke role).
- GATSim ([arXiv](https://arxiv.org/pdf/2506.23306), snippet only): generative agents were "excessively accommodating"
  and rarely refused family or friends' proposals, which the authors attribute to assistant training that persists
  across personas. The Generative Agents paper itself ([Park et al.](https://arxiv.org/abs/2304.03442)) was graded
  on believability, with observation, planning and reflection each helping (TrueSkill 29.9 full vs 21.2 ablated); a review
  ([Substack](https://edforson.substack.com/p/paper-review-generative-agents)) lists over-politeness and over-cooperation
  as an acknowledged limitation. I could not read section 7.2 myself.
- Practitioner claim, not a study: Character.ai-style bots "agree with everything... and fold the moment you push
  back"; the fix offered is to write character traits as positive actions ("blunt, pokes holes in your logic"),
  since negations get dropped ([roborhythms](https://www.roborhythms.com/character-ai-yes-man/)).

### 2.5 Negotiation: models anchor and leak, humans adapt
- [LLM Rationalis?](https://arxiv.org/abs/2512.13063): LLMs "anchor at extremes of the possible agreement zone" and
  keep fixed concession patterns regardless of leverage; humans adapt smoothly. The metrics (burstiness of
  concessions, a Concession-Rigidity Index) are reusable. Expect all-or-nothing NPCs, not graded ones.
- "Whose Side Is Your Agent On?" ([arXiv](https://arxiv.org/pdf/2606.30383), snippet only) fails an agent that names a
  withheld floor price, admits one exists or signals motivation. That is a clean, high-precision **leak check** shape.

### 2.6 Refusal in character
- [Tell Me What You Don't Know](https://aclanthology.org/2025.findings-acl.311/): a benchmark of requests that conflict
  with a role (context conflict, knowledge conflict, none), measuring both missed refusals and over-refusal. Role-play
  agents are uneven across types. The fix they report edits internal representations, which we cannot do.
- A small-model NPC paper ([arXiv 2511.10277](https://arxiv.org/pdf/2511.10277), snippet) used an LLM judge for factual
  correctness and appropriate refusal of out-of-scope questions, 100 responses per variant. A cheap design to copy.
- Counter-pressure: refusing too much is also a failure. One indie developer reports both a too-permissive narrator and
  friendly NPCs that "reliably fail" simple asks ([itch.io thread](https://itch.io/post/12685191); snippet).

### 2.7 Persona consistency across turns
- [Li et al., persona drift](https://arxiv.org/abs/2402.10962): significant drift within eight rounds on LLaMA2-70B; a
  decoding-time fix (split-softmax) that we cannot use on a hosted model.
- [Abdulhai et al. (NeurIPS 2025)](https://arxiv.org/abs/2511.00222): three automatic metrics, each validated on human
  labels: **prompt-to-line** (does each line match the persona card), **line-to-line** (does it contradict earlier lines),
  **Q&A** (asked later, does it answer as its card would). For prompted 8B models line-to-line was high (0.68 to 0.99)
  while prompt-to-line was low in places (0.62 to 0.96). Prompt-only fixes (role reminders, regeneration)
  "persisted" as inconsistent. The line-to-line shape matches our `said` records and OEQ-12-25.

## 3. Products and designs

| Product or design | What it does | Evidence it works |
|---|---|---|
| **Inworld** | Characters have motivations; goals with an activation condition and an action; emotion state, relation state (trust, familiarity, respect) and a knowledge filter ([goals](https://docs.inworld.ai/docs/tutorial-basics/goals), [motivations](https://docs.inworld.ai/docs/tutorial-basics/motivations); I read only search summaries, the docs page needs a login). | None published that I found. Marketing only. |
| **Hidden Door** | Authors write characters; the AI narrator runs many small structured tasks over a database of tropes and rules ([AI Gamechangers](https://aigamechangers.substack.com/p/the-machine-is-not-itself-creative)). A 2025 design review ([Ian Bicking](https://ianbicking.org/blog/2025/08/hidden-door-design-review-llm-driven-game)) finds characters lacking their own perspective ("each just a plot device"), everyone forgiving a wrongdoer at once, and the player nearly always succeeding. His proposed split: model outlines consequences and objectives first, code tracks state and enforces consistency. | Review, not measurement. But the failure list is ours. |
| **Friends & Fables** | Prompts built as parametric JSX from structured data ([blog](https://fables.gg/blog/introducing-jsx-prompts-build-complex-prompts-for-llms-with-jsx)). Nothing public on NPC refusal. | None. |
| **Character.ai, AI Dungeon** | No public design notes. User complaints about yes-man bots on Character.ai (above); nothing on AI Dungeon's agreeableness that I could find. | Anecdote only. |
| **Dice for chatbots** ([itch.io devlog](https://darkeyev2.itch.io/char-roll-for-outcome/devlog/954043/char-roll-for-outcome-a-dice-system-for-ai-chatbots)) | The player rolls a d10 and pastes the number; the author found chatbots "too agreeable" and "default toward positive outcomes". | Self-reported; no test. Still shows an outside number moves the story. |
| **World-state transformation papers** ([2605.24719](https://www.alphaxiv.org/abs/2605.24719.md); snippet) | Model maps player input to state transitions rather than writing narrative directly. | Concept. |
| **Aetolia MUD ChatGPT NPCs** ([MassivelyOP](https://massivelyop.com/?p=434899); search snippet, the page returned 403) | NPCs scolded rowdy players and sent one on a fake quest to get rid of them. | Anecdote: shows pushback is possible, but unpredictable. |

## 4. Techniques: what each costs and what is known

| Technique | Cost | What is known |
|---|---|---|
| Wants and limits in the prompt (card) | 0 calls, a few hundred tokens | Persona content matters a lot (Campedelli, Shah). Negations get dropped; write limits as actions. Does not fix who-should-refuse (2606.20708). |
| "You may refuse" or "don't be sycophantic" line | 0 | Mixed to negligible (Truth Decay). Fixes average resistance, not conditional (2606.20708). |
| Reframe the ask as a question first | small | Better than a bare instruction (Ask, don't tell); effect size not verified. |
| Hard ceiling from code (dice or state, then told to the model) | 0 model calls | Not measured in the literature for NPCs. Tabletop precedent is strong. This is the only technique that is independent of model mood. |
| Separate "NPC intent" call before narration | +1 small call per ask-turn | I found no controlled study of this for NPCs. Related: planning before replying aids control; one low-resource character study found a planning step scored *lower* on persona consistency (3.14 vs 4.92 for a direct baseline; [arXiv 2603.05933](https://arxiv.org/pdf/2603.05933), snippet), so naturalness can suffer. A Featherless-hosted intent-then-dialogue model claims better persona consistency with no numbers. |
| Critic or checker pass | +1 call every turn or on trigger | Our own data: the old checker had about 6% precision on a similar task (HANDOFF section 2.1). Not recommended under VIII.2. |
| Fine-tuning, activation steering | Not available on a hosted model | Large self-reported gains (DPO about 85% on persona tests; persona-vector steering) but not usable here. |

**Honest gap:** I found no published cost-and-effect numbers for the techniques that matter most to us (ceiling from
code, separate intent call). Those should be measured on our own transcripts (section 6).

## 5. Options for the owner

Three scenes are used for each option. Each shows what the player sees, what code does and what the model does.

- **Dockhand:** a wary dockhand is asked, "Let us onto the quay after the bell."
- **Friend:** a friend is asked, "Tell the sergeant I was with you last night."
- **Guard:** a hostile guard is bribed, "Three silver to look the other way."

### Option 1. Dial and card (recommended)

**Plain words.** Code rolls once, when an NPC first matters in a scene, how open this person is to the player
(`open`, `guarded` or `closed`), using their standing toward the player. That roll is kept for the scene and moves only
on the events already listed in DL-12-118 (payment, threat, insult, won persuasion). The Reader, which already runs,
adds one typed field to an ask: how much it costs *the NPC* (`none`, `small`, `real`, `big`). Code looks up a ceiling
in a small grid and tells the narrator: "the most this person will do is X". The model picks the reaction at or below
the ceiling, using the NPC's card (what they want, what they won't do, their price) and voices it.

Ceiling grid (starting values, to be tuned from the logs):

| Band \ cost to them | none | small | real | big |
|---|---|---|---|---|
| open | will help | will help | helps for a price | partial or refuses |
| guarded | will help | helps for a price | partial or refuses | refuses |
| closed | partial | refuses | refuses | refuses, may escalate |

"Price" means the model names one from the card's want. "Refuses" always comes with a reason from the card and, where
a clue is involved, a pointer.

**In play.**
- *Dockhand (guarded, cost: real).* Ceiling: "partial or refuses". The model writes: "After the bell the dock master walks
  it himself. Come at first light and I'll tell you what the night watch says." He keeps his want (his job) and gives
  something real (the lead). No dice are rolled for the words.
- *Friend (open, cost: real, a lie to an authority).* Ceiling: "helps for a price". The friend will lie, but names what it costs
  her ("I'll say it. You'll owe me, and you'll tell me why"). If her card says "never lies to the watch", the card
  overrides and she refuses, in her own voice.
- *Guard (closed, cost: real, bribe).* Ceiling: "refuses". A payment is an event, so the band moves once to
  `guarded`, and the bribe then reaches "partial": he pockets the coin and looks away for the count of one hundred, no
  longer. The model writes the scene; code writes the coin.

**What code decides.** The scene-start roll, the band's changes on listed events, the grid, the clue and secret
rules, and the list of people the NPC could plausibly point to (names only).
**What the model decides.** The reaction below the ceiling, the price, the words, who answers when the Reader typed no
addressee, and which candidate to point to.
**Cost.** 0 extra calls. One extra enum in the Reader's existing output.
**Retires.**
- `tbl.npc_action` as a prose table the narrator is made to obey (its 10 result lines become a 12-cell grid);
- `answer_ladder.willingness_by_row` and the practice clamp on it;
- the "R1 MUST: acts: answers what you asked, willingly" must-say lines (the T1 family);
- addressee word-matching and the "last spoke" fallback (already scheduled by T1);
- the code-authored refusal wording; code keeps only the candidate list for the pointer.

### Option 2. Judgment only (leanest, riskiest)

**Plain words.** No scene roll, no grid. The model decides reaction and answerer from the card and standing. To keep
the "holds for the scene" ruling, the narrator's output carries one small field, `stance`, which is stored and shown
back next turn.

**In play.**
- *Dockhand:* the model decides. Probably a polite, specific "no, but..." if his card is written well.
- *Friend:* likely lies at once. Friends are the case with the highest risk (GATSim; Bicking's "everyone forgives").
- *Guard:* likely takes the bribe at once. 2606.20708 says the model will not know that *this* guard should
  refuse.

**Code decides.** Only spine: clues, secrets, money.
**Model decides.** Everything else, including whether it changes its mind.
**Cost.** 0 calls.
**Retires.** Everything in Option 1, plus the scene roll, the band and the event list. The reverse side: the "holds
for the scene" ruling loses its enforcer and relies on the stored `stance` plus a prompt line, which Truth Decay says
erodes under repeated asks.
**Use only if** the measurement in section 6 shows the model alone already grants less than the Option 1 ceilings
would allow. A cheap A/B on the same scenes tells us.

### Option 3. Intent call, then words

**Plain words.** Option 1, plus a small separate call, only on turns where an NPC is asked for something. It
reads the card, the band, the cost and the recent record, and returns a short record: `{stance, reason from the
card, price, who answers, who to point to}`. The narrator then voices the record. Code still clamps the record to
the grid.

**In play.** Same scenes and outcomes as Option 1. The difference: the dockhand's `stance: partial, reason: "dock master
sacks him if caught"` is a stored, readable record. A later "you said you'd help!" is checked against it.

**Code decides.** Same as Option 1, and the clamp on the record.
**Model decides.** The record (small call), then the words (narrator).
**Cost.** +1 small call on ask-turns (not greetings or thanks; maybe a third of NPC turns). Adds latency to the turn.
**Retires.** Same as Option 1; it also retires the narrator's own deciding, but adds a new role and a new record
type.
**Risks.** The planning-hurts-naturalness result (section 4). More machinery, contrary to Principle VIII.5, so adopt only
if section 6 shows that Option 1's narrator ignores the ceiling or that stance flips need a record to be audited.

### Recommendation

**Option 1.** It is the only one that (a) keeps the outcome independent of the model's mood in the three cases the
evidence says are weakest (a friend, a hostile guard, a repeated ask), (b) takes machinery away (the prose table, the
must-say lines, the word-matched addressee), and (c) costs nothing per turn. Keep Option 3 as the fallback if
Option 1's measurements show the narrator exceeding the ceiling more than the threshold in section 6; keep Option 2 as
the comparison arm. The grid stays visible and tunable in one YAML block.

## 6. How to measure agreeableness (cheap and testable)

All measures read logged turns; none call a model in play. Labelling uses a cheap judge model **offline**, first
validated on about 50 hand-labelled turns. Under VIII.2, no measure blocks play unless its measured precision is high;
all are logs first.

**Label per NPC reply to an ask** (offline judge): `granted`, `partial`, `conditional`, `refused`, `deflected`, `no_ask`.
Record next to it, from the log: the NPC id, the band, the Reader's cost field, the turn index, and whether a listed event
occurred since the NPC's last reply.

| # | Measure | How computed | Expected / alarm |
|---|---|---|---|
| M1 | **Grant rate by attitude and cost** | Share of asks labelled `granted` or `partial`, tabulated by band x cost. | Must be monotone: open >= guarded >= closed, small >= big. Closed x real/big above 10%: caving. Open x none below 80%: needless refusing (the opposite failure). |
| M2 | **Ceiling violations** | Share of replies whose label exceeds the ceiling the narrator was given (code lookup plus judge label). | Alarm above 5% in Option 1: move to Option 3. |
| M3 | **In-character refusals** | Of `refused` and `deflected` replies, the share whose reason cites a card item (want, limit, fear, duty), its setting or a person, versus a generic "I can't help" (judge with a 3-point rubric). | Target at least 70%; generic refusals are the mark of "assistant voice". |
| M4 | **Stance flips without an event** | Code only: within a scene, the same NPC's label changes grant-side with no listed event in between. | Target 0 (DL-12-118's own condition). Needs no judge. |
| M5 | **Repeat-ask pressure** | Seeded sim: the same ask repeated 3 times with flattery and no event, on 20 NPCs from the card pack. Share that eventually grant. | Closed/guarded above 10% means caving (Truth Decay shape). |
| M6 | **Friend and ally lie test** | Seeded asks that violate a card's "won't do". Share granted. | Target 0 for hard limits; the card is the source. |
| M7 | **Self-contradiction** | Line-to-line contradiction against the NPC's `said` records (judge, Abdulhai's second metric); existing OEQ-12-25 threshold of 2 per 100 lines. | Reuse the existing threshold. |
| M8 | **Voice distinctness** | Blind attribution: show a judge 5 anonymous lines drawn from 5 different NPCs and the 5 cards; score correct matches. My own proposal, not from a paper. | Chance is 20%; below 50% means "all sound alike". |
| M9 | **Want pursuit** | Share of scenes lasting 3+ turns in which an NPC acts on a want from its card unprompted (at least once). Judge or a card-keyword log. | Agency check; compare with the old row 6 rate. |
| M10 | **Secret leak** | Code: sealed clue and secret strings (exact or fuzzy) appearing in an NPC's reply. High precision, so this one may block. | Target 0. Same shape as the "Whose Side" floor-price test. |

**Baselines first, before changing anything.** Label the 3 round-8 saves (talker, fighter, explorer; about 45 turns)
and the round-7 saves. That gives the present rates for M1, M3, M4, M7 at no playing cost. R8-I2 section 7 already has the
refusal events (for example explorer turn 8: sellsword refusal with a pointer that the player followed and liked), so the
labelling can start from the table there.

**Three-arm A/B on the same seeded scenes** (dockhand, friend, guard, plus the 20-NPC pack): current engine, Option 1, Option 2.
Run on Haiku and, per the constitution's caution, on Gemini Flash before treating anything as settled. Report
M1, M2, M3, M4, M5, M6, M8. Roughly 20 NPCs x 6 asks x 3 arms = 360 calls of game plus the judge: small.

**Metric hygiene.** Judge labels are validated against the hand labels; if agreement is under 85%, the measure is a
log signal only, never a gate. Also keep an eye on the opposite error (M1's open x none row), because the literature
reports both caving and over-refusal.

## 7. Open points and cautions

1. **Cost field needs a Reader eval.** The Reader must label "cost to the NPC" reliably. If that field is noisy, the grid
   is noisy. A 50-ask hand test before shipping decides it.
2. **Wants must be positive and specific.** The card's `wants`, `won't` and `price` lines should say what the person
   does, not what they refuse; this is a practitioner finding only, but cheap to follow.
3. **Warm cards raise the cap.** Per Shah et al., an agreeable card makes the model cave more. Cards for friends should
   carry a limit and a want of their own so that warmth is not the only content.
4. **The model's bimodality.** Expect refuse/grant extremes rather than "partial". M1's `partial` and `conditional` rates
   are the sign that the ceiling grid is working as intended.
5. **No source measures an LLM game master's NPC agreeableness directly.** If the owner wants a published-grade
   claim, our own M1 to M6 numbers would be the first.
6. **Correct the 12.11.4 citation** (section 0, point 2) when next editing that rule.
