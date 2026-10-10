# R7-R1: Should the model just make up undecided details?

**The question (decision D1).** The player asks "how much is the reward?", "who posted the notice?", "where was he last seen?" or
"what does the job pay?", and nothing in the game has decided the answer yet. Who should decide it?
- the model, in character, stored as testimony and settled only when the player acts on it (the owner's leaning);
- code, with tables or generators, when the hook is created (ROUND7-ANALYSIS D1-A);
- or a mix of the two.

**The short answer.** The owner is mostly right. For ordinary detail, letting the character make it up is what good human GMs
do, and our testimony design already makes that safe. There are four kinds of detail where "make it up and settle later"
goes wrong, because the player hears the detail and plans around it *before* anything settles:
1. **money**;
2. **the hook's main destination**;
3. **anything a case is built on**;
4. **terms several people will be asked about.**

Those four should be decided by code when the hook is made. Most of the tables already exist. Everything else should be
improvised freely, with two cheap guards. That is recommended **Option 2** below.

---

## 1. How tabletop games handle it

**Improvise freely, but decide the load-bearing parts.** Every tradition below lets the GM, or the players, invent most
detail on the spot. Every one of them also keeps a short written core that improvisation must not contradict.

- **Powered by the Apocalypse.**
  - Dungeon World's GM principles include "Draw maps, leave blanks" and "Ask questions and use the answers". The world
    is deliberately incomplete and gets filled in as play needs it ([Dungeon World SRD, Gamemastering][dw]).
  - Apocalypse World adds "Sometimes, disclaim decision-making". Big outcomes should come from the NPCs' own wants,
    from countdown clocks and from the moves, not from the MC's whim ([Daily Apocalypse #48][aw48]).
  - Lesson: small details are improvised, but consequential ones are handed to a *structure*.
- **Blades in the Dark.**
  - Common knowledge is simply answered. Hidden information takes a roll, and the roll sets *how much detail* you get,
    never whether the answer is true. In the book's words, "The GM always answers honestly" ([Blades SRD, Gathering
    Information][bitd]).
  - Community practice: give players what their characters would plausibly know, without making them dig for it
    ([Walking Mind, "Narrating from Knowledge"][wm]).
  - Lesson: when a fact exists, characters say it. A roll never decides whether content exists at all.
- **Solo oracles.**
  - Ironsworn/Starforged: "If an answer leaps to mind, go with it." Ask the oracle only when unsure. Its basic tool is a
    yes/no answer or a random prompt to interpret ([Starforged rulebook, "Trust Your Instincts"][sf]).
  - Mythic GME's Fate Chart answers only yes/no questions, and the player turns the answer into content ([Word Mill,
    Mythic GME 2e][mythic]; [review][mythicrev]).
  - Neither treats a bare "yes" as if it had *created* the thing asked about. That is what our Oracle did in round 7:
    "yes, the list names the worst place", with no place ever written (R7-I2 §1a). Both systems back the analysis's
    view that yes/no coin-flips standing in for "what/where/how much" answers should be retired.
- **Mystery design.**
  - Justin Alexander's Three Clue Rule and node-based design are about redundancy. Each conclusion has at least three
    clues, so one missed clue doesn't stall play ([Three Clue Rule][tcr]).
  - When he improvises clues, he keeps a fixed **revelation list**. Improvised clues must point at an existing
    revelation, so they have "a destination" ([Alexandrian comments][tcr2]).
  - He warns that fully unassigned, improvised clues produce thin mysteries. Improvising a clue to confirm whatever the
    players suspect also removes the feedback that makes a mystery work ([Making Clues][mc]).
  - GUMSHOE separates *finding* clues from *interpreting* them. Core clues are never rolled for. Laws's test: "if it's
    not important enough to put in your notes, it's not a core clue". When players get stuck, the GM invents a new
    core clue on the spot, pointing deeper in ([Pelgrane, improv and structure][gum1]; [How I prep][gum2]).
  - Lesson: **the solution and the core clue paths are written down**, and improvised details may only point toward
    them, never redefine them.
- **Keeping improvisation consistent.** Common GM practice:
  - write every improvised name and detail down at once;
  - keep, for each recurring NPC, "what they know, what they don't, what they want";
  - check those notes before saying "yes, and" to anything that touches the core ([Tribality][trib];
    [Tenkar's Tavern][tenkar]).
  - Deliberately contradictory rumours are fine, but only if the GM's notes still say what is actually true (same
    sources).

**What this means for us.** Tabletop practice matches our design almost exactly:
- the spine (cases, money, clue paths) is prepared and protected;
- speech is improvised;
- improvised claims become "notes" (our testimony store);
- the GM consults those notes before contradicting them.

The one tabletop habit we lack is the last one: *showing the notes back to the person improvising* (see §3, risk 4).

## 2. How AI game masters and LLM fiction handle it

| System / work | What the model may invent | How consistency is kept | Reported failures |
|---|---|---|---|
| **AI Dungeon** | Everything. | Players write "Plot Essentials" (always in context) and keyed "Story Cards" (added when a keyword appears) ([help: World Info][aid1]; [context][aid2]). | The help pages admit the AI "won't always reference or even correctly repeat" World Info. Users report the AI "forgetting" as old text scrolls out; players fix it by editing the output. |
| **Hidden Door** | Prose, choices and outcomes. Only **cards** (characters, places, special objects, plot directions) are state ([Bicking review][hd]). | The prompt is built from the cards. Tropes and world rules are prewritten ([interview][hd2]). | Location jumps; a "plan" mentioned that never existed; **coins narrated into the story and then spent on a toll**. Bicking's advice is to "track and commit to a world state" and to decide outcomes before writing prose. |
| **Friends & Fables (Franz)** | Story and NPCs. Inventory, location and HP are tracked. | Editable, **lockable** memories; a "research step" before replying; an out-of-character mode for state edits ([Franz 2.0 notes][ff]). | Memory and combat tracking drift in long sessions. The developers say they are unsure the memories system keeps quests on track. |
| **Inworld** | Dialogue, within each character's knowledge. | **Personal knowledge** (only this character) is kept apart from **common knowledge** (shared, filterable by group). Entries are written in the character's voice ([Inworld docs][iw1]; [common][iw2]). | (Vendor docs; no failure data.) |
| **Murder-mystery LLM games** (AI Alibis, Google's Neural Noir) | Suspects' dialogue. | Knowledge is **partitioned per character** so the solution can't be pulled from one generator ([Neural Noir][nn]). | AI Alibis notes that the suspects' secrets sit in their context windows, so it has to discourage leaks with critique passes. |
| **CALYPSO** (Zhu et al., AIIDE 2023) | Encounter descriptions for a *human* DM. | The human filters. | The model "makes up" monster facts not in the books. The author argues this matters less in a creative setting ([paper][cal]; [Register][calreg]). |
| **FIREBALL** (Zhu et al., ACL 2023) | Turn narration. | Structured game state supplied to the model. | Supplying state measurably improved the generated turns ([ACL][fb]). |
| **"I Cast Detect Thoughts"** (Zhou et al., ACL 2023) | DM guidance. | Explicit DM *intent* plus a model of the players. | Guidance written with an explicit intent was 3× more likely to achieve that intent ([ACL][icdt]). |
| **PANGeA** (Buongiorno et al., AIIDE 2024) | Level data, NPCs, dialogue. | Designer rules; an LLM validator checks free-text input against the game's rules; short- and long-term memory ([arXiv][pg]). | Free-form input pushes the model out of scope. |
| **Player-driven emergence** (Peng et al., Microsoft, CoG 2024) | NPC dialogue in a fixed-premise mystery. | Fixed narrative premise. | Players found *fun emergent* content outside the plan. Without intervention, the model tends to **repeat patterns** ([arXiv][peng]; [MSR][msr]). |
| **Ubisoft Ghostwriter** | Only barks and crowd chatter, never lore. | A writer picks or edits each line ([Shacknews][gw]). | (Deliberately narrow scope.) |
| **SCORE** (2025) | Long stories. | Symbolic tracking of item and character state, summaries, retrieval ([arXiv][score]). | Reports fewer hallucinations than plain GPT (preprint; not independently reproduced). |
| **RPGBench** (2025) | The game engine role. | Structured event state. | Stories are engaging, but models are **systematically weak at consistent mechanics** ([arXiv][rpgb]). |
| **NCP-Bench** (Ma et al., Aug 2026) | Narration against a fact ledger. | New narrator facts are added to the ledger once checked. | **Fact conflicts in 40–68% of interactions.** The best model is conflict-free in only 42% of runs after 20 turns. "High linguistic quality does not guarantee commitment preservation" ([arXiv][ncp]). |
| **Structured Knowledge Trees for detective games** (Rahmati & Zhao, Sep 2026) | Suspect dialogue, limited to the allowed knowledge. | A knowledge tree plus retrieve, generate and verify agents. | Critical hallucinations down 64.78%; premature disclosure prevented; but **forced reveals hurt usability** ([arXiv][skt]). |
| **Orchestrated Reality** (2026, WIP) | Narration. | State is committed as JSON changes (plan, diff, validate, apply). | It argues that narrators which assert state in prose pile up contradictions ([arXiv][or]). |

**Patterns across these systems:**
1. **Everyone lets the model invent flavour.** No shipped system pre-generates every detail.
2. **Every system that holds up keeps a small, hard core outside the prose.** Hidden Door's cards, Inworld's knowledge,
   Franz's locked memories, the detective games' partitioned knowledge, FIREBALL's state. The core is what the
   mechanics read: money, inventory, places, the solution.
3. **The reported failures are the risks we list.** Contradiction (NCP-Bench, Hidden Door's location jumps), money
   appearing from prose (Hidden Door's coins), plans and places promised but never written (Hidden Door's "plan"; our
   Magby's list), repetition (Microsoft) and secret leaks (AI Alibis).
4. **Over-locking has its own cost.** The knowledge-tree detective game cut hallucinations but made conversations feel
   forced. That is the same "wall" our round 6 and 7 players felt.
5. **I found no paper on our exact pattern**: lazy truth, where speech stays testimony until the player acts on it. The
   closest work is NCP-Bench's ledger, which commits narrator facts *immediately* once checked. Our approach is novel
   ground, so the risk estimates below are reasoned judgments, not measurements.

## 3. Applying it to our design

What we already have (checked in code):
- **Testimony.** `engine/dm/testimony.py` stores speech as `said` records. Settlement runs only on travel, on a
  target, or when a claim is cited as a premise. `_case_route` already routes claims that touch a case: a claim the
  case doesn't hold becomes `wrong_about` (the speaker was wrong).
- **Money tables.** `rules/data/economy.yaml` has `job_fees` by band, and invariant **AI-6**: "Coin enters only
  from … job fees … each from a table … never from a DM's choice". So **a model-invented sum that the game later pays
  would break a standing invariant.**
- **Notice tables.** `tbl.12.seed.document` (in `world_seed.yaml`) already generates seeded notices with `{reward}`,
  `{issuer}`, `{contact}` and `{contact_place}`. So "who posted it" and "the reward" are *already* table-made for
  seeded notices. The gap is the lead and incident hooks, such as `offer` and `refugees` (R7-I2 §7 A).
- **Write-on-mention.** `engine/dm/mentions.py` already creates places, NPCs and items that the narrator names.
- **The narrator prompt forbids it today.** `narrator.md` says "Do not invent … what someone knows". Option 1 or 2
  would need that line changed to allow in-character answers (testimony) while forbidding new *facts about the world
  state*.

### Risk by risk, under "the model invents, stored as testimony, settled when acted on"

**1. An invented detail solves or contradicts a sealed case.**
- *Likelihood:*
  - **Accidental solve: low.** The narrator never sees sealed facts. It can only hit the culprit by luck, roughly 1 in
    the size of the cast. Even then `_case_route` delivers no clue.
  - **Contradiction: medium to high, whenever the question is the case's own subject.** In round 7 the fighter's case
    solution *was* "who makes the offer". "Who posted the notice / who's paying?" is exactly the question an NPC would
    answer by inventing. Every invented name then settles as `wrong_about`, so the townsfolk become accidental liars and
    the mystery fills with red herrings nobody designed. Alexander warns about exactly this: improvised clues without a
    revelation list.
- *Guard (cheap): case-protected topics on the speaker card.* List the case subject and node topics, never their
  answers, as "you don't know this; if asked, say so, or point to the one who would". That is GUMSHOE's and
  Alexander's "improvised clues must point at the written path". The holder's clue goes out through D2-A's delivery.
  This is about one line per speaker per case. Settlement routing already exists as a backstop.

**2. Invented sums break the economy.**
- *Likelihood:* **high.** Models inflate ("a hundred gold for your trouble"), and Hidden Door shows prose money being
  spent. "Settle later" fails here because the player hears the number *before* acting and plans around it. If
  settlement then clamps "50 gold" to the band-2 fee of 85 silver, the NPC looks like a liar, or the game breaks AI-6.
- *Guard:*
  - **Pay is decided before anyone speaks it:** the job fee by band, or the notice's `{reward}`, written on the
    offerer's card when the hook is made.
  - For a sum outside any hook ("I'd give you 5 silver for that knife"), **the price band at settlement**: a deal's
    typed price comes from the band table, and haggling moves it one notch at most (08.8.2).
  - A spoken figure outside the band is still testimony. It never reaches the purse.

**3. The player travels to an invented place.**
- *Likelihood:* **medium.** Following leads is the point of play.
- *Impact:* a dead end if the place has no site, which is the refugees' "location written to `world`, where it
  affects nothing" (R7-I2 §1c/§4).
- *Guard:*
  - **Write-on-mention already creates the place.** Add *generate-on-travel*: when travel settles a place known only
    from testimony, roll its site from `sites.yaml` / the region tables. That is "draw maps, leave blanks" done safely.
  - **The hook's main destination should be authored** at creation, because the Director and the threads need to
    point at it.

**4. Two NPCs invent contradicting details.**
- *Likelihood:* **high for anything several people get asked about.** `said_by` shows a speaker only *their own*
  lines, so NPC B never sees what NPC A said. NCP-Bench finds fact conflicts in 40–68% of interactions *even with a
  ledger*.
- *Impact:* **low for rumours.** Witnesses disagree; it is realistic, and the first claim acted on settles. **Medium
  for hook terms.** Two different rewards for one notice reads as a bug.
- *Guard (cheap):*
  - Hook terms are authored and put on the card of everyone who'd know.
  - **Show the topic's testimony from other speakers** on the speaker card ("others have said: …"). This is the
    tabletop "check your notes", and it is one change to the `said_by` filter.

**5. Repetition or inflation.**
- *Likelihood:* **medium to high.** Microsoft found LLM NPCs repeat patterns. Expect the same "old mill", "Old Tom"
  and "a hundred gold" across games.
- *Guard:* tables for the key terms give seeded variety for free; the price band caps inflation; the existing
  `is_repeat` freshness check covers a speaker repeating themselves.

**Summary.**

| Risk | Likelihood | Cheapest guard | Already built? |
|---|---|---|---|
| Case solved by accident | low | — (settlement already withholds) | yes |
| Case contradicted ("who posted it?") | medium–high | protected topics on the speaker card | settlement backstop only |
| Economy | high | pay from `job_fees` / `{reward}` before speech; band at settlement | tables yes, wiring no |
| Invented place travelled to | medium | write-on-mention + generate-on-travel; author the hook's destination | mention yes, site no |
| NPCs contradict each other | high (hook terms) | others' testimony on the card; authored terms | no |
| Repetition / inflation | medium–high | tables for key terms; band cap | partly |

---

## 4. Options for the owner

The same scene in each option: a notice reads "Reward for the missing ferryman". You ask the ferry-keeper how much,
who posted it and where he was last seen. Then you ask his widow about him.

### Option 1: Let the model make it all up; guard at settlement (the owner's leaning)
Any undecided detail is answered in character and stored as testimony. Code steps in only when the player acts on it:
it clamps sums to the price band, routes case topics to the case, and generates places on travel.

> The ferry-keeper: "Fifty gold, posted by the reeve. Last seen at the Old Mill." The widow says "the reeve's clerk
> posted it, for thirty". You go to the reeve. The case holds "who wants the ferryman gone", so both claims settle as
> wrong. The reeve knows nothing of a notice. You find the ferryman and are paid the table's 85 silver, not fifty gold.

- *Good:* the least code; fully fluid speech.
- *Bad:*
  - everyone gave a different reward;
  - the money you planned around wasn't real;
  - the "reeve" lead was a dead end nobody designed.
- *Cost:* change the narrator's "do not invent" line, plus three settlement guards.

### Option 2: Code decides the hook's key terms; the model improvises everything else (recommended)
When a hook is made, generators write its **pay** (`job_fees` band or the notice's `{reward}`), its **issuer and
contact** (`tbl.12.seed.document` already does this), its **destination** (a region site) and **who's involved**, all
as unsealed knowledge on the cards of those who'd know. Everything else is the character's to improvise as testimony.
Two cheap guards apply: protected case topics on the speaker card, and other speakers' testimony on the same topic
shown back. Price band at settlement and generate-on-travel act as backstops.

> The ferry-keeper: "Twenty silver, the council's coin. Reeve Haddow put it up; ask at the toll-house." That came
> from the card. "Last seen? Taking a fare across at dusk, a man in a grey hood," he adds. That is improvised
> testimony. The widow, asked "who'd want him gone?", says "I can't say. Ask the toll-keeper, he and my man had words."
> That is a protected topic, pointing to the clue holder. You get the same twenty silver from anyone you ask, and
> twenty silver is what you're paid.

- *Good:*
  - everything the mechanics read is real and consistent;
  - the case stays clean;
  - speech is still free;
  - most of the tables exist already.
- *Bad:* a generator step per hook kind (offer, refugees, bounty, warning). Terms are written for hooks the player
  may never follow, but that is a few fields, not prose.
- *Cost:* wire the existing tables into the lead/incident builders, add one card section, and change one filter.

### Option 3: Decide lazily, the first time anyone asks
Nothing is generated up front. The first time the player asks a key-term question ("how much / who / where"), code
rolls the answer from the same tables, writes it on the card, and the NPC says it. Later NPCs see it.

> First question to the ferry-keeper: code rolls `{reward}` = "twenty silver" and `{issuer}` = Reeve Haddow, and he
> says so. The widow later gives the same answer. The "last seen" detail is improvised as in Option 2.

- *Good:* nothing is generated for unpursued hooks; consistent once asked.
- *Bad:* it needs a classifier at question time to tell a key-term question from small talk. That is the same routing
  problem that failed in round 7 (word-overlap case routing: 0 clues in 38 questions). It also adds a model call or a
  rule on the hot path, and the issuer stays undecided while the case needs it. The Director and the threads can't
  point at a destination that doesn't exist yet.
- *Cost:* more than Option 2, for a saving (a few table rolls) that doesn't matter.

### Recommendation: Option 2
- It is the owner's own idea with a fence around it. NPCs make up the "last seen", the colour and the gossip. Code
  decides only what the rules already say code must own:
  - money (invariant AI-6);
  - case subjects (Principle VIII.1: secrets and clues are spine);
  - the hook's destination, so threads and travel have somewhere real to go.
- It matches what works elsewhere. GMs keep a revelation list and notes (Alexander, GUMSHOE). Blades answers honestly
  from what exists. Hidden Door, Inworld and the detective games keep a small hard core outside the prose. It avoids the
  reported failures: prose money, contradictions, unwritten promises.
- It costs the least code that actually closes round 7's gap, because the tables (`job_fees`, `tbl.12.seed.document`
  fields, sites) already exist.

**In all three options:**
- the yes/no Oracle stops answering "what / where / how much" questions;
- the narrator line "Do not invent … what someone knows" is narrowed to "don't state new world facts in narration; a
  character may say what they believe".

**Validate on Gemini Flash** before treating "free testimony" as settled (Principle VIII caution). NCP-Bench's numbers
suggest that smaller models contradict themselves more.

---

## Sources
- [dw]: https://www.dungeonworldsrd.com/gamemastering/
- [aw48]: https://daily-apocalypse.com/daily-apocalypse/48-sometimes-disclaim-decision-making
- [bitd]: https://bladesinthedark.com/gathering-information
- [wm]: https://walkingmind.evilhat.com/2018/05/07/narrating-from-knowledge/
- [sf]: https://dokk.org/library/ironsworn_starforged_rulebook_2019 (Starforged rulebook; "Seeking Answers",
  "Trust Your Instincts"; see also https://tomkinpress.com/pages/ironsworn)
- [mythic]: https://wordmillgames.com/page/mythic-gme.html
- [mythicrev]: https://dev.rpg.net/reviews/archive/13/13308.phtml
- [tcr]: https://thealexandrian.net/?p=7985 (The Three Clue Rule)
- [tcr2]: https://thealexandrian.net/creations/misc/node-design/node-design2.html (node-based design)
- [mc]: https://thealexandrian.net/?p=46338 (Random GM Tips: Making Clues)
- [gum1]: https://pelgranepress.com/2018/01/03/see-page-xx-improv-and-gumshoe-scenario-structure/
- [gum2]: https://pelgranepress.com/2018/02/01/how-i-prep-adventures-in-gumshoe
- [trib]: https://www.tribality.com/2019/11/26/game-prep-improvisational-tips/
- [tenkar]: https://www.tenkarstavern.com/2014/08/improvised-npcs-do-you-keep-track-of.html
- [aid1]: https://help.aidungeon.io/faq/all-about-world-info
- [aid2]: https://latitudegames.notion.site/What-goes-into-the-Context-sent-to-the-AI-7e5881352de6427da9c92b04149e8e50
- [hd]: https://ianbicking.org/blog/2025/08/hidden-door-design-review-llm-driven-game
- [hd2]: https://aigamechangers.substack.com/p/the-machine-is-not-itself-creative
- [ff]: https://fables.gg/patch-notes/franz-20-working-context-lore-improved-planning-and-more
- [iw1]: https://docs.inworld.ai/docs/tutorial-basics/facts-knowledge/
- [iw2]: https://docs.inworld.ai/docs/tutorial-basics/common-knowledge/
- [nn]: https://ai.google.dev/competition/projects/neural-noir
- [cal]: https://arxiv.org/abs/2308.07540
- [calreg]: https://www.theregister.com/2023/08/19/chatgpt_dnd_dm/
- [fb]: https://aclanthology.org/2023.acl-long.229
- [icdt]: https://aclanthology.org/2023.acl-long.624
- [pg]: https://arxiv.org/abs/2404.19721
- [peng]: https://arxiv.org/abs/2404.17027
- [msr]: https://www.microsoft.com/en-us/research/project/emergence/
- [gw]: https://www.shacknews.com/article/134702/ubisoft-ghostwriter-ai-technology
- [score]: https://arxiv.org/abs/2503.23512
- [rpgb]: https://arxiv.org/abs/2502.00595
- [ncp]: https://arxiv.org/html/2608.08160
- [skt]: https://arxiv.org/abs/2609.23043
- [or]: https://arxiv.org/html/2606.16014v1

*Confidence notes.*
- The Mythic "don't ask when the answer is obvious" habit is community practice; I did not verify the rulebook wording.
- The AI Alibis leak remark comes from a search snippet of its demo page.
- The likelihood ratings in §3 are reasoned from the code and from round 7, not measured.

[dw]: https://www.dungeonworldsrd.com/gamemastering/
[aw48]: https://daily-apocalypse.com/daily-apocalypse/48-sometimes-disclaim-decision-making
[bitd]: https://bladesinthedark.com/gathering-information
[wm]: https://walkingmind.evilhat.com/2018/05/07/narrating-from-knowledge/
[sf]: https://dokk.org/library/ironsworn_starforged_rulebook_2019
[mythic]: https://wordmillgames.com/page/mythic-gme.html
[mythicrev]: https://dev.rpg.net/reviews/archive/13/13308.phtml
[tcr]: https://thealexandrian.net/?p=7985
[tcr2]: https://thealexandrian.net/creations/misc/node-design/node-design2.html
[mc]: https://thealexandrian.net/?p=46338
[gum1]: https://pelgranepress.com/2018/01/03/see-page-xx-improv-and-gumshoe-scenario-structure/
[gum2]: https://pelgranepress.com/2018/02/01/how-i-prep-adventures-in-gumshoe
[trib]: https://www.tribality.com/2019/11/26/game-prep-improvisational-tips/
[tenkar]: https://www.tenkarstavern.com/2014/08/improvised-npcs-do-you-keep-track-of.html
[aid1]: https://help.aidungeon.io/faq/all-about-world-info
[aid2]: https://latitudegames.notion.site/What-goes-into-the-Context-sent-to-the-AI-7e5881352de6427da9c92b04149e8e50
[hd]: https://ianbicking.org/blog/2025/08/hidden-door-design-review-llm-driven-game
[hd2]: https://aigamechangers.substack.com/p/the-machine-is-not-itself-creative
[ff]: https://fables.gg/patch-notes/franz-20-working-context-lore-improved-planning-and-more
[iw1]: https://docs.inworld.ai/docs/tutorial-basics/facts-knowledge/
[iw2]: https://docs.inworld.ai/docs/tutorial-basics/common-knowledge/
[nn]: https://ai.google.dev/competition/projects/neural-noir
[cal]: https://arxiv.org/abs/2308.07540
[calreg]: https://www.theregister.com/2023/08/19/chatgpt_dnd_dm/
[fb]: https://aclanthology.org/2023.acl-long.229
[icdt]: https://aclanthology.org/2023.acl-long.624
[pg]: https://arxiv.org/abs/2404.19721
[peng]: https://arxiv.org/abs/2404.17027
[msr]: https://www.microsoft.com/en-us/research/project/emergence/
[gw]: https://www.shacknews.com/article/134702/ubisoft-ghostwriter-ai-technology
[score]: https://arxiv.org/abs/2503.23512
[rpgb]: https://arxiv.org/abs/2502.00595
[ncp]: https://arxiv.org/html/2608.08160
[skt]: https://arxiv.org/abs/2609.23043
[or]: https://arxiv.org/html/2606.16014v1
