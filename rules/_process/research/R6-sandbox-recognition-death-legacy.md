# R6 — Recognition Without a System, Living-World Engines, Telegraphed Death, and Legacy

> Research digest for the three owner-locked creative decisions (BRIEF §4) that the existing
> `reports/` corpus does not cover: (A) how a *hidden-mechanics* classic-fantasy world voices class
> emergence and tier crystallization; (B) how an open-ended sandbox stays alive, reactive, and
> paced with no human GM; (C) how death can be real but always telegraphed; (D) how a sandbox
> "finishes" through retirement and hands the world to a successor. Each section is a mechanics
> catalog (system → how it works → AI-DM fitness → target chapter) followed by a synthesized
> **recommended design space**. Written by research agent R6. Mechanics are paraphrased; no rules
> text is reproduced. Sources are listed at the end with URLs.

**Chapter keys** (BRIEF §9): **04** recognition & growth · **07** harm/recovery/death · **11**
living world, retirement & legacy · **12** DM procedures · **13** starter setting. Occasional
cross-references to 03 (tags/evidence), 06 (conflict), 10 (exploration/social/downtime).

**AI-DM fitness shorthand.** Each entry ends with a `+` (what makes it good for an AI adjudicator:
determinism, crisp triggers, low hidden judgment) and a `−` (where it leans on human-table
consensus, vague judgment, or social negotiation an AI running solo for one player can't
reproduce). Many tabletop mechanics rely on *group* consensus (Burning Wheel's trait vote, Kingdom's
crossroads); for a single-player AI game the question is always "what replaces the table?"

---

## 0. Executive summary

1. **Every successful hidden-mechanics recognition system separates three things the LitRPG box
   fuses together: the *tally* (hidden, deterministic), the *witness* (who in the world could
   plausibly notice), and the *moment* (when the fiction stages it).** Ultima IV is the purest
   precedent: hidden virtue counters, an in-world seer who reports progress only in graded
   vagueness, and a shrine where the player chooses to meditate to crystallize the result. That
   three-part split maps exactly onto P5's tally → classifier → grant/offer/abstain pipeline.
2. **Recognition has a natural *visibility ladder*** — rumor → epithet → acknowledgement → summons
   → seat/title — and each rung corresponds to a confidence band. Low-confidence evidence can be
   voiced as a rumor with no mechanical effect (the in-fiction face of *abstain*); mid confidence
   as a summons or mentor's question (*offer*); high confidence as a community that has already
   started using a name (*grant*). This gives the DM a tone-appropriate voice for all three policy
   outcomes, not only "offer."
3. **Offers must be deferrable in-fiction.** Stormlight's Ideals, Dragon's Dogma's maisters,
   Mount & Blade's vassalage letters, Earthdawn's teachers, and the Greybeards' summons all *wait*.
   A standing, re-visitable offer (a letter, a door left open, an oath not yet spoken) is the
   diegetic form of P1's "player may defer."
4. **The living world is a clocked, turn-based background simulation plus a pacing director on top.**
   The best-evidenced shape is Blades' faction clocks + faction status (−3…+3) + heat/entanglements,
   run on a SWN-style *faction turn* at every downtime boundary, with a Left 4 Dead–style intensity
   tracker (build-up → peak → relax) deciding *when* the world pushes, and a Façade/Valve-style
   "most-specific eligible event wins" rule deciding *what* pushes.
5. **"Hooks never dead-end" is solved by redundancy, not cleverness.** The Alexandrian's Three
   Clue Rule (and its inversion) plus node-based design is the direct structural implementation
   of P16. Every surfaced hook should reach its destination by ≥3 independent routes.
6. **Telegraphed death = two keys, never one.** Torchbearer (death only via a declared kill
   conflict, or while already Injured/Sick), Blades (fatal harm requires a desperate position the
   GM announced *and* declining to resist), and Apocalypse World (soft move before hard move) all
   require both a *declared lethal context* and a *pre-existing dying/damaged state* before death
   is on the table. That two-key rule is how "a single unlucky roll never ends a character"
   becomes mechanical rather than aspirational.
7. **The best last-chance mechanics give the player a *menu*, not a coin flip.** Dungeon World's
   revised Face Death (captured / glorious last act / gamble / Death-marked / transform), Ironsworn's
   Face Death (noble sacrifice or a quest-bargain with Death that leaves you cursed), Fate's
   concession, and 13th Age's flee-for-a-campaign-loss all trade death for a *story cost the
   player chooses*. These are the defeat-without-death outcomes the owner asked for.
8. **Retirement works when the world keeps the character.** Every strong legacy system (Pendragon
   heirs, Ironsworn legacy tracks, Wildermyth legacy tiers, Dwarf Fortress legends, Blades stash
   tiers) converts the retiring character into *world state*: renown that partially transfers,
   unfinished threads that transfer with progress, enemies that transfer too, and a legend that
   NPCs repeat. Retirement is also the project's cleanest instance of Principle VI — the ultimate
   *structural* retirement of accumulated content.

---

## A. In-fiction recognition of class/identity without a diegetic System

### A.1 The problem, restated precisely

The constitution (P5, P2) produces three machine-level events:

| Machine event | Policy tier | Fiction must... |
|---|---|---|
| Classifier returns high confidence for a calling | **grant** | show the world *already treating* the character as that thing |
| Mid confidence (or a hybrid candidate, or a tier crystallization) | **offer** | stage a moment where the player can accept, decline, or defer — in character |
| All-low confidence | **abstain** | say *nothing mechanical*, but may still let the world murmur |
| Evidence contradicts a held identity (oath-type callings) | (revocation / atonement) | voice the loss as a fraying, not a notification |

BRIEF §4 forbids blue boxes, stat talk, and in-world announcements of classes. Principle VII still
requires that the player know (via the out-of-fiction codex, P7) exactly what they are licensed to
attempt. So the voicing layer must be *diegetic* while the licensing layer stays *out of fiction*.
The research question is: which in-world agents, rituals, and moments have games and fiction used
to carry that load?

### A.2 Mechanics catalog

#### A.2.1 Oaths, vows, and bonded witnesses

**A-01 · Stormlight Archive — Ideals and the Nahel bond** (04)
- *How it works.* A spren (a sapient fragment of an ideal) bonds a person whose conduct already
  resonates with its order's outlook; minor powers leak through before any oath. Progress is
  gated by speaking the order's *Ideals* — five oaths, the first shared by all orders, the rest
  order-specific. An Ideal "takes" only when it is spoken *and* true of the speaker at that moment,
  usually at a crisis; the bond deepens and new capacities unlock (Blade, Plate, efficiency).
  Acting against sworn Ideals dims the spren and throttles power; persistent betrayal can kill the
  spren (the historical Recreance produced "deadeye" spren). The Fifth Ideal makes the bond
  breakable only by death. The First Ideal can even be spoken in pieces across a conversation.
- *AI-DM fit.* `+` Exactly P2's model: a hidden readiness condition plus a player-spoken
  crystallization. The spren is a *witness with a stake* — it can comment, doubt, and wait.
  `−` The "is it true of you right now" test is pure judgment; the novels can delay an Ideal for
  a whole book (Kaladin and the Fourth Ideal), which in a game risks feeling withheld.
- *Take.* Keep the shape (readiness is tracked, the words are the player's act), bound the
  judgment with the tally: the DM may only stage an Ideal-type moment when the engine says the tier
  is eligible, and the player's words, not a hidden DM verdict, finalize it.

**A-02 · D&D 5e Paladin oaths, the Oathbreaker, and BG3's Oathbreaker Knight** (04)
- *How it works.* Tabletop: a paladin swears a Sacred Oath (tenets listed); violation is judged
  by the DM case-by-case; the usual path is atonement, with the Oathbreaker as the fall for the
  unrepentant. Baldur's Gate 3 made it diegetic: breaking a tenet (detected by scripted triggers)
  flips an "Oath Broken" state and a spectral **Oathbreaker Knight** appears at camp — an NPC who
  explains what happened and offers two paths: embrace the break (take the Oathbreaker subclass)
  or pay for restoration (a fixed gold cost).
- *AI-DM fit.* `+` BG3 shows the pattern *recognizer as a person who arrives with choices*: loss
  is voiced by a visitor, not a pop-up, and the visitor carries an explicit accept/decline menu.
  `−` BG3's single-trigger breaks are brittle (players report breaking oaths on edge cases); a
  bug that killed the Knight stranded players with no restoration path — a real-world warning that
  the *recognizer must be un-killable or replaceable*.
- *Take.* Revocation should route through the same offer machinery as recognition; the witness
  must be persistent (an order, a god, the spren-analogue), never a single mortal NPC who can die.

**A-03 · Ultima IV — hidden virtue counters, the Seer, and shrine meditation** (04, 12)
- *How it works.* Eight virtues are tracked as hidden counters updated by ordinary conduct
  (e.g., not cheating a blind merchant, not killing fleeing foes, giving to beggars, honesty in
  dialogue). The player *cannot see the numbers*. An in-world seer (Hawkwind) reports progress per
  virtue in graded, vague language ranging from "you have far to go" to "you are ready — go to the
  shrine." When ready, the player must travel to that virtue's shrine, speak its mantra, and
  meditate across three cycles to gain partial Avatarhood (an "eighth"), accompanied by a vision.
  Later unvirtuous acts cost the eighth; one catastrophic act (using the forbidden Skull) strips
  all of them. Character creation itself was a fortune-teller's sequence of ethical dilemmas that
  determined your starting class.
- *AI-DM fit.* `+` The single best precedent for this project. Hidden deterministic tally;
  in-world *graded reporting* without numbers; a player-initiated crystallization at a place; a
  diegetic revocation. `−` The seer is a single location — a player far away has no feedback.
- *Take.* Generalize "the Seer" into a *class of reporting witnesses* available everywhere (see
  V6 below), with a fixed graded vocabulary mapped to tally bands.

#### A.2.2 Trait and virtue tallies that tick up from conduct

**A-04 · King Arthur Pendragon — Traits, checks, the Winter roll, and virtue bonuses** (04, 03, 11)
- *How it works.* Thirteen paired personality traits (Chaste/Lustful, Valorous/Cowardly, etc.)
  each sum to 20. When a knight acts decisively in accordance with a trait in play, the GM
  awards a *check*. In the annual Winter Phase, each checked trait is rolled on d20: if the roll
  *exceeds* the current value, it rises by 1 (and its opposite falls). A trait at 16+ is
  "famous" — others know the knight for it — and generates passive Glory each year. Crossing
  defined *combinations* grants named statuses: the **Chivalrous** knight (sum of six specific
  traits ≥ 80) gains +3 armor ("armor of chivalry") and 100 Glory per year; a **Religious** knight
  (all five of their faith's traits ≥ 16) gains 100 Glory and faith-specific benefits. Trait rolls
  can also *compel* behavior — a high trait can override the player's intent at a moment of
  temptation.
- *AI-DM fit.* `+` The d20-must-exceed rule is a gorgeous anti-grind: evidence ticks are cheap,
  but each point is harder to gain the higher you are, so tiers deepen with diminishing velocity
  without any separate XP curve. Combination thresholds (Chivalrous = sum over a trait set) are a
  direct precedent for P5 hybrid/composite recognition. "Famous at 16+" is a built-in *visibility
  threshold*. `−` Compelled behavior conflicts with goal 1 (player freedom); keep it out.
- *Take.* Borrow (1) check-then-batch-roll (evidence is marked in play, resolved at a reflection
  boundary), (2) the harder-when-higher progression, (3) set-sum thresholds for composite
  identities, (4) a fame threshold at which NPCs start knowing.

**A-05 · Pendragon — Passions** (04, 12)
- *How it works.* Passions (Loyalty to a lord, Love of family, Hate of an enemy, Honor,
  Hospitality) are rolled when invoked at a charged moment. Success makes the knight *inspired*
  (a large bonus to one skill; a critical can double it). Failure disheartens (a skill-wide penalty
  and the passion drops a point); a fumble can tip into melancholy or madness until Winter.
- *AI-DM fit.* `+` A clean model for "a power that awakens in crisis" gated by a tracked value.
  `−` Madness removes control from the player; unsuitable as-is.
- *Take.* A calling's crisis-awakening can be modeled as a bounded invocation keyed to a tracked
  commitment, with failure costing the commitment, not player control.

**A-06 · Burning Wheel — Beliefs, Instincts, Traits; the trait vote; artha routing** (04, 12)
- *How it works.* Players write Beliefs (goals-with-conviction) and Instincts (if-then reflexes);
  playing to them, even to the character's detriment, earns *artha* (Fate, Persona, Deeds).
  Traits come in three kinds (character, call-on once-per-session, die traits). At the end of a
  session or arc the group proposes and **votes** on new traits (and removal of unplayed ones).
  Beliefs/Instincts that were backed by spent Fate are eligible to become character traits;
  Persona-backed ones can become minor die traits or call-ons; Deeds-backed ones can become major
  die traits. Heavy artha spending on one ability (20 Fate + 10 Persona + 3 Deeds) produces an
  *epiphany*: a permanent quality shift. Skill advancement requires a *mix* of Routine, Difficult,
  and Challenging tests scaled to current rating, and failures count — you improve by attempting
  hard things, not by succeeding at easy ones.
- *AI-DM fit.* `+` Artha routing is a precise *evidence-quality ladder*: the kind of commitment
  behind an act decides the kind of trait it can become. The R/D/C mix is a ready-made rule for
  tier depth ("a tier requires k evidence events at or above challenge band X"). `−` The vote is a
  *group* consensus; a single-player AI game has no peers to vote.
- *Take.* Replace the vote with the offer tier: the classifier nominates, the *player* votes
  (accept/decline/defer). Adopt the R/D/C requirement for tier crystallization so grinding trivial
  evidence cannot deepen a tier.

**A-07 · Mouse Guard — the Winter session** (04, 11)
- *How it works.* A periodic reflective session where the patrol reviews the year: skills
  advance from accumulated passes *and* fails, traits are adopted or "nixed" by the group's
  judgment of how they were played, and beliefs/goals may change. Traits can be used against
  yourself to earn checks for the player's turn.
- *AI-DM fit.* `+` Shows the value of a *scheduled* recognition boundary: nothing is reassessed
  mid-scene; everything is reassessed at a known, fictionally-justified rest. `−` Group judgment
  again.
- *Take.* The "reflection boundary" (see V7) is where most non-crisis recognition should be
  voiced.

**A-08 · Avatar Legends — Balance, center, and growth questions** (04)
- *How it works.* Each playbook has two opposed principles on a balance track. Moves and NPCs
  shift the current balance; it drifts back to the character's *center* at rest. At session end
  each player answers a playbook-specific *growth question* (yes → mark growth); growth buys
  advances including *shifting your center*, and ultimately a playbook climax (the Moment of
  Balance).
- *AI-DM fit.* `+` Two-speed identity: fast, noisy short-term drift vs. slow, deliberate center.
  That is exactly the recency-vs-cumulative split chapter 03 needs for tallies. Growth questions
  are yes/no evidence gates. `−` "Who shifted whom" relies on social reading.
- *Take.* Recognition should key off the *center* (cumulative, slow), never the momentary balance.

**A-09 · Masks: A New Generation — Labels and Influence** (04, 12)
- *How it works.* Five labels (Danger, Freak, Savior, Superior, Mundane) are both roll stats and
  self-image. Labels shift constantly, often because someone with **Influence** over you tells you
  who you are; adults automatically hold Influence over teenage heroes. Being told who you are *is*
  the mechanic.
- *AI-DM fit.* `+` A precise model for *NPC voice as recognizer*: an influential NPC's statement
  is the fiction's way of reflecting identity. `−` Constant shifting would violate P2's
  stability; the project's callings must be sticky.
- *Take.* Use influential NPCs as the *voice* of recognition, never as its *cause* (the tally is
  the cause). An NPC with standing (mentor, lord, rival) may name what the tally already shows.

**A-10 · Monsterhearts 2 — Conditions and Growing Up** (04, 11)
- *How it works.* Conditions are labels others hang on you (and exploit). After enough advances
  across the table, a *season* ends and characters take season advances — including switching
  skin or growing up (new moves that transcend the playbook's dysfunction).
- *AI-DM fit.* `+` Season boundary as a structural checkpoint for identity change. `−` Social
  labels in Monsterhearts are adversarial table play.
- *Take.* Reputational *labels* (epithets) can carry small mechanical hooks in social play — see
  the reputation entries below.

**A-11 · The One Ring 2e — Callings, Shadow, and Shadow Paths** (04, 07)
- *How it works.* Each hero picks a Calling (Captain, Champion, Messenger, Scholar, Treasure
  Hunter, Warden) that grants favored skills and a distinctive feature *and* a matching Shadow
  Path — the calling's characteristic corruption (lust for power, vengeance, secrets, wandering,
  dragon-sickness, despair). Shadow accumulates from misdeeds and dread; when Shadow ≥ current
  Hope the hero is Miserable, and a bad Feat die then triggers a *bout of madness* — a regrettable
  act, a permanent flaw on that calling's path, and reduced Hope.
- *AI-DM fit.* `+` Every identity has a *built-in failure direction*. That is the "oath-type"
  revocation for non-oath callings: a calling's excess, not only its betrayal, is tracked. `−`
  Loss-of-control moments again.
- *Take.* Every calling should author a named *shadow*: the direction the tally drifts if the
  calling is pursued without its counterweight. The shadow is a recognition too (the world
  notices the tyrant in the captain).

#### A.2.3 Playbook/calling triggers that make growth follow play

**A-12 · Blades in the Dark — XP triggers** (04, 03)
- *How it works.* Desperate action rolls mark XP in that action's attribute immediately. At
  session end each character checks: the playbook's own trigger (e.g., the Cutter's "address a
  challenge with violence or coercion" — success irrelevant), "expressed your beliefs, drives,
  heritage, or background," and "struggled with vice or trauma." 1 XP if it happened, 2 if it
  happened a lot. Playbook advances buy special abilities.
- *AI-DM fit.* `+` Deterministic, cheap, and it makes *risk* the evidence (desperate rolls).
  Success-independence prevents failure spirals. `−` Playbooks are chosen up front — the opposite
  of emergence.
- *Take.* The "1 if at all, 2 if a lot" cap is an excellent evidence-saturation rule per
  reflection period; desperate/lethal-context actions should weight evidence more heavily.

**A-13 · Heart: The City Beneath — Callings and Beats (minor, major, zenith)** (04, 11)
- *How it works.* A Calling (why you went into the Heart) supplies a core ability and a list of
  *beats* — concrete narrative milestones like "take major mind fallout" or "put knowledge above an
  ally's life." Each session the player picks two active beats; the GM is instructed to build
  opportunities for them. Completing beats yields minor or major advances; a **Zenith** ability is
  the calling's culmination and usually ends the character (death, transformation, departure).
- *AI-DM fit.* `+` Beats are a *player-to-DM signaling channel* — the player announces what arc
  they want and the DM is obligated to create openings. That is the missing "intent" input to
  P5's classifier. Zenith as a chosen ending is a direct retirement mechanic (§D). `−` Picking
  from a list is menu-driven; emergence is lost if beats are the *only* route.
- *Take.* Offer "aspirations" as optional player flags that raise the *salience* (not the weight)
  of related evidence and bias hook generation toward it (§B), never as a purchase menu.

**A-14 · Forbidden Lands — end-of-session XP questions, Pride, Dark Secret** (04, 11)
- *How it works.* XP comes from answering fixed questions at session end (participated; traveled
  into unknown lands; defeated a monster; found treasure; built for the stronghold; acted on your
  Pride; your Dark Secret caused trouble; went to lengths for someone you care about). Pride is a
  once-per-session d12 boost tied to a declared value.
- *AI-DM fit.* `+` Question lists are auditable evidence gates. `−` Undifferentiated XP.
- *Take.* A short fixed question list at each reflection boundary is an AI-friendly way to catch
  evidence that per-event tagging missed.

#### A.2.4 Reputation, renown, titles, and epithets

**A-15 · Ars Magica 5e — Reputations with content, score, and type** (04, 11, 10)
- *How it works.* A Reputation is a triple: *content* ("Witch," "Honest Broker"), *score*, and
  *type* — Local, Ecclesiastical, or Hermetic — which defines who could have heard. A reputation
  starts at 1 when the character does something noteworthy **in front of witnesses who will
  talk**; each further noteworthy act adds one experience point to it as if it were a skill (so
  ten acts to go from 1 to 2). Whether a given person has heard is a roll whose difficulty rises
  with social distance (same village → same county → same country; same parish → whole Church).
- *AI-DM fit.* `+` Exactly the data shape the project needs: reputation is separate from
  identity, witness-gated, audience-scoped, and *slow*. `−` Per-person hearing rolls are
  table-heavy (irrelevant for an AI).
- *Take.* Adopt the triple verbatim as a state object: `reputation{content, score, scope}`, with
  the witness requirement as the gate for *public* recognition (an unwitnessed deed feeds the tally
  but not the reputation).

**A-16 · Forbidden Lands — Reputation "precedes you"** (11, 10)
- *How it works.* On arriving at a new settlement, roll d6 equal to Reputation; any 6 means
  locals have heard of you. Whether that is good or bad depends on *what* you're known for, which
  the GM decides.
- *AI-DM fit.* `+` Dead simple, probabilistic, and separates fame (how known) from valence (for
  what). `−` Valence is left to judgment.
- *Take.* Separate *renown* (magnitude) from *reputation content* (what for), exactly as Ars
  Magica does; roll or compute recognition on arrival.

**A-17 · Mount & Blade: Warband — Renown and vassalage offers** (11, 04)
- *How it works.* Renown accrues from battles (more for fighting against the odds, capped per
  battle), quests, and feasts. It raises party size and social access. At about 150 renown
  (reduced by good relations with a king), **kings start sending offers** of vassalage; the player
  may accept, ignore, or negotiate. Joining sets relations with the faction and its enemies.
  Relations are individual per lord, not faction-wide.
- *AI-DM fit.* `+` The canonical *the-order-seeks-you-out* mechanic with a numeric gate and a
  standing, ignorable offer. Per-NPC relations beside faction status is a useful two-level model.
  `−` Renown is a single scalar with no content.
- *Take.* Institutional offers should be triggered by renown in *that institution's* domain and
  arrive as persistent, ignorable letters/emissaries.

**A-18 · Fable series — titles, renown, and (2020s) per-settlement reputations** (04, 11)
- *How it works.* Original Fable: renown from deeds made crowds cheer and react; titles were
  bought from a Title Vendor (the infamous default "Chicken Chaser"). Later games awarded titles
  for specific acts. The announced new Fable makes reputation *local and plural*: kick chickens in
  front of enough people and "chicken chaser" becomes one of the things you're known for *in that
  settlement*, with different NPCs valuing that reputation differently.
- *AI-DM fit.* `+` The modern design is the right one: reputation is per-community, earned by
  witnessed repetition, and *valence varies by observer*. `−` Purchased titles break emergence.
- *Take.* Epithets are earned from witnessed repetition within a community; the same epithet can
  be praise in one place and an insult in another.

**A-19 · Saga bynames (Old Norse *viðrnefni*)** (04, 13)
- *How it works.* In the Icelandic sagas, bynames were conferred by the community, not chosen,
  and were often unflattering. Many are anchored in a specific incident narrated in the saga
  (Harald Fairhair's vow not to cut his hair until Norway was unified; Eirik Bloodaxe's
  fratricides; Kveldulf's evening moods). Scholarship (Whaley, *Nicknames and Narratives in the
  Sagas*) treats the byname as a narrative device: it both records and *foreshadows* character.
- *AI-DM fit.* `+` A cultural license for the fiction to *name* the character without the
  character's consent — the cheapest, most natural grant-tier voicing. `−` None if bounded.
- *Take.* The epithet is the default voicing for a *grant*: someone in the world starts calling
  you something, and it sticks because it's true. The player may embrace or resent it; they
  cannot un-earn it.

**A-20 · Middle-earth: Shadow of Mordor — the Nemesis system** (04, 11, 07)
- *How it works.* Orc captains remember encounters with the player: who won, how, scars, fears
  (burned orcs may fear fire). An orc who kills the player is promoted and boasts about it next
  time; orcs you humiliated return with grudges and new traits.
- *AI-DM fit.* `+` *Adversaries as recognizers*: enemies naming and remembering you is some of the
  most visceral recognition in games, and it works because the memory is state. `−` Needs a
  persistent adversary roster (chapter 09/11).
- *Take.* Rivals and recurring enemies are a distinct witness class: they recognize the
  dangerous parts of an identity first, and their recognition often *precedes* allies'.

#### A.2.5 Orders, hierarchies, masters, and initiation

**A-21 · Earthdawn — Disciplines, circles, initiation (including spontaneous)** (04)
- *How it works.* An adept follows a Discipline (Warrior, Nethermancer, Troubadour...), which is
  less a class than a *way of seeing the world* that grants magical talents. Progress is by
  Circles 1–15 grouped into tiers (Initiate, Novice, Journeyman, Warden, Master); advancing usually
  requires having the talent ranks *and* training from a teacher of higher circle (with some
  circles advancing without a teacher). Initiation is normally by a teacher, but the setting
  explicitly allows **spontaneous initiation under extreme stress** — the discipline awakens in a
  moment of crisis, e.g., at the site of an atrocity to someone of the right mindset.
- *AI-DM fit.* `+` Both routes the owner named — "a mentor's acknowledgement" and "a power that
  awakens in crisis" — are canon in one system, and tiers are named. `−` Teacher-gating creates
  logistics friction in a solo game if a teacher is far away.
- *Take.* Two routes to the same recognition: *taught* (mentor ritual at a reflection boundary)
  and *awakened* (crisis, mid-scene). The engine decides eligibility; the fiction picks the route
  by circumstance.

**A-22 · AD&D 1e — Druid and monk hierarchies with finite seats** (04, 11, 13)
- *How it works.* Above a certain level, druids and monks advance only if a seat is free or they
  defeat the incumbent: nine Druids per region, three Archdruids, one Great Druid; monks from
  level 8 have limited seats and must win weaponless single combat against the holder. A
  non-lethal loss drops the loser to the bottom of the previous level.
- *AI-DM fit.* `+` A *title* is a scarce, occupied, in-world position with an NPC in it — which
  generates hooks, rivals, and politics for free. `−` Hard gating of power behind combat
  contradicts emergence if it applies to *capability* rather than *rank*.
- *Take.* Separate **capability tiers** (from tally; never seat-limited) from **institutional
  ranks** (seat-limited titles within orders that confer social standing, resources, and
  obligations). Ranks are a chapter-11 faction feature that *reacts to* recognition.

**A-23 · Skyrim — the Greybeards' summons** (04, 12)
- *How it works.* After the player absorbs a first dragon soul, a thunderous Shout from the
  mountain calls the Dragonborn's name across the land; the local jarl explains that the
  Greybeards are summoning the Dragonborn to High Hrothgar. The player can go immediately, later,
  or never.
- *AI-DM fit.* `+` The textbook *order seeks you out* with a deferrable standing offer and a
  fictional explainer (the jarl) who translates the event for the player. `−` Unique, prophetic
  identity; most callings are not world-shaking.
- *Take.* Scale the herald to the calling: a hedge-witch's recognition is a crone who comes to the
  door; a world-rare calling can shake mountains.

**A-24 · Dragon's Dogma 2 — Maisters and hybrid vocations** (04)
- *How it works.* Basic vocations are licensed at a guild. The hybrid vocations (Magick Archer,
  Mystic Spearhand, etc.) are unlocked only by finding a specific master in the world who teaches
  that fusion; they are exclusive to the player-character.
- *AI-DM fit.* `+` Hybrids voiced by a *specific master of that fusion* is a clean diegetic face
  for P5's curated hybrid table: each authored hybrid pair has an authored "maister" archetype.
  `−` Fixed NPC locations make it a scavenger hunt rather than emergence.
- *Take.* When the classifier surfaces a hybrid candidate, the offer comes via a figure who
  embodies that fusion, generated/placed near the player rather than pre-placed.

**A-25 · Dragon Age: Origins — Specializations taught, bargained, or ritualized** (04)
- *How it works.* Specializations unlock through in-world sources: a companion teaches one after
  approval is high enough; a spirit teaches another in exchange for a bargain; one requires a
  morally dark ritual choice during a main quest. Manuals can also be bought.
- *AI-DM fit.* `+` Shows three *sources of offer* — relationship (approval), bargain, and
  transgression — each with a distinct cost texture. `−` Purchasable manuals collapse emergence.
- *Take.* The offer's *source* should match the tally's content: relationship callings via
  people, occult callings via bargains, dark callings via transgression.

#### A.2.6 Use-based learning and reflective moments

**A-26 · The Elder Scrolls — use-based skills; Oblivion's "rest and meditate"; birthsigns and standing stones** (04, 02)
- *How it works.* Skills rise by use. In Oblivion, after enough major-skill increases the game
  prompts the player to rest and meditate on what they have learned; the level-up occurs only when
  the player sleeps. Birthsigns (Morrowind/Oblivion) are fixed at creation; Skyrim moves them into
  the world as Standing Stones the player can find and swap.
- *AI-DM fit.* `+` The "gains are realized at rest" pattern is exactly the reflection boundary.
  Standing stones show a *place* as recognizer. `−` The prompt itself is a thin System voice.
- *Take.* Realize most growth at rest, voiced as dreams, reflection, or morning stiffness in a new
  shape — never as a prompt.

**A-27 · Kingdom Come: Deliverance — skill-by-use with trainers and reading** (04, 10)
- *How it works.* Skills rise by use; trainers (for a fee) grant levels but only at intervals
  (once per several levels); books require the Reading skill. Perks unlock at thresholds.
- *AI-DM fit.* `+` Throttled mentoring prevents buying past the use requirement. `−` Pure
  numeric.
- *Take.* A mentor can *accelerate or unlock* but never *substitute* for tally evidence.

#### A.2.7 Transformations and dark offers

**A-28 · Wildermyth — event-driven transformations and hooks** (04, 11)
- *How it works.* Heroes are changed by authored events that present the player a choice (accept
  the wolf's gift, let the crystal in); accepted transformations stack visually and mechanically
  and can culminate in a unique retirement ending. Each hero has personal "hooks" (goals) whose
  resolution grants bonuses, including retirement bonuses.
- *AI-DM fit.* `+` Transformations are *offers inside scenes* with both boon and bane —
  exactly how "gated special traits (monster-power absorption)" should feel. `−` Authored events.
- *Take.* The Blue-Mage-style absorption calling should be offered as a Wildermyth-style
  transformation event with a visible cost.

**A-29 · Blades in the Dark — Demonic Notice (entanglement)** (04, 11)
- *How it works.* A downtime entanglement where a demon approaches with a dark offer: accept the
  bargain, hide until it loses interest (forfeit rep), or handle it another way.
- *AI-DM fit.* `+` A priced, three-way offer triggered by world state. `−` None.
- *Take.* Dark callings are offered by *interested powers*, and declining has a small cost —
  the power remembers.

### A.3 Cross-cutting analysis

**Who recognizes.** Across the 29 entries, recognizers fall into seven classes. Each has a
natural confidence band and a natural calling family:

| Recognizer class | Examples | Natural policy tier | Best for |
|---|---|---|---|
| **The community** (crowd, village, soldiers) | saga bynames, Fable, Ars Magica local rep | grant (after the fact) | any calling with public deeds |
| **The mentor / master** | Earthdawn teachers, DD2 maisters, KCD trainers, DA:O companions | offer | skill- and craft-based callings; hybrids |
| **The institution / order** | M&B kings, Greybeards, AD&D hierarchies | offer (standing) | martial, religious, scholarly, guild callings |
| **The bonded witness** (spren, god, patron, familiar) | Stormlight, paladin deity, BG3 Knight | offer; revocation | oath-type callings |
| **The seer / reader** | Hawkwind, fortune-tellers | abstain-as-progress-report | all; the only voice for *abstain* |
| **The adversary** | Nemesis orcs, rivals | grant (feared name); early warning | martial, dark, notorious callings |
| **The self / body / place** | Oblivion rest, Earthdawn spontaneous awakening, standing stones, shrines | grant (passive) or offer (crisis) | innate and mystical callings |

**When it's staged.** Three moments recur: (1) **in crisis** (Stormlight, Earthdawn spontaneous,
Pendragon passions) — the most dramatic, but it interrupts a scene and must therefore be quick and
deferrable; (2) **at a reflection boundary** (Pendragon Winter, Mouse Guard winter, Oblivion sleep,
Burning Wheel trait vote, Forbidden Lands questions) — calm, batchable, AI-friendly; (3) **on
arrival or contact** (Forbidden Lands reputation, M&B offers, Greybeards) — the world reaches out
when the character enters its reach.

**How the offer is shaped.** Every deferrable offer in the corpus has the same three affordances:
it is *legible* (someone explains what is being offered in fictional terms), it is *standing*
(it persists while ignored), and it is *priced* (accepting binds you to something: an oath, a
lord, a bargain, a transformation). Offers without a price (bought titles, purchased manuals) are
exactly the ones reviewers say break the fiction.

**How loss is voiced.** Revocation is always *gradual first* (dimming spren, Oath Broken state,
Hawkwind's worsening words, TOR's Shadow crossing Hope) and only *final* after persistent
contradiction or one catastrophic act that was explicitly forbidden in advance (the Skull of
Mondain). That is P5's atonement analogue, and it matches Principle VI's "telegraphed" mandate.

### A.4 The voicing-mechanism catalog (the deliverable for chapter 04)

Each mechanism is a reusable **staging template** the DM applies to a machine event. "Maps to"
states which P5 policy outcome it voices. "Offer form" states the in-fiction accept / decline /
defer affordance. Rule kind per BRIEF §5.

**V1 · The Witnessed Epithet** — *maps to: grant; also public-reputation growth* `[D]` trigger, `[N]` phrasing
- *Recognizer:* the community that witnessed the deeds. *Staging:* an NPC who wasn't present
  uses a name for the character ("you're the one they call the Lantern of Coldmarsh"); crowds or
  soldiers repeat it. *Offer form:* none needed — epithets are conferred, not accepted. The player
  may embrace ("that's me") or resent it; both are roleplay, not mechanics.
- *Rules:* only witnessed evidence feeds epithets (Ars Magica gate); epithets are scoped to the
  communities that witnessed (Fable/Ars Magica scope); valence varies by community.
- *Failure mode to avoid:* epithets that name the class label itself ("the Battlemage"). Epithets
  name *what you did*, never the ruleset's class name.

**V2 · The Mentor's Acknowledgement** — *maps to: offer (tier crystallization or taught calling)* `[J]`
- *Recognizer:* a master of the calling (existing NPC with relevant standing, or one introduced
  by the hook engine). *Staging:* the mentor observes, then asks a question that names the path
  without naming the mechanic ("You fight like someone who has stopped expecting to come home.
  Do you want to learn to do it on purpose?"). *Offer form:* accept (begin the rite/lesson),
  decline (the mentor accepts it; the door stays open), defer ("come back when you know").
- *Rules:* a mentor can unlock or accelerate only what the tally already makes eligible (KCD);
  never substitutes for evidence.

**V3 · The Order Seeks You Out** — *maps to: offer (institutional calling or rank)* `[D]` trigger, `[J]` staging
- *Recognizer:* an institution whose domain matches the evidence. *Staging:* a letter, emissary,
  summons, or sign (M&B vassalage offers; Greybeards). *Offer form:* standing — the emissary names
  a place and a time window or leaves a token that can be presented later. Ignoring it is a
  legitimate choice; outright refusal may carry a small reputational cost with that institution
  (Blades' Cooperation/Demonic Notice precedent).
- *Rules:* institutional offers carry *obligations* (a lord's service, an order's vows); accepting
  links the character to a faction in chapter 11.

**V4 · The Oath Spoken** — *maps to: offer → crystallization (P2 tier)* `[J]` staging, `[D]` effect
- *Recognizer:* the bonded witness (patron, god, the calling's ideal made manifest) or simply the
  character's own voice. *Staging:* at a moment where the next tier's principle is at stake, the
  DM surfaces (out-of-fiction, briefly) that a deepening is available, and the player *speaks the
  words* in character — their own words, which the DM checks only against the tier's principle,
  not against a script (Stormlight's pieces-across-a-conversation precedent).
- *Offer form:* speak now, or let the moment pass (the readiness persists; it may be taken at the
  next qualifying moment).
- *Rules:* the words become a recorded commitment (state: `commitments`), the basis for later
  revocation checks.

**V5 · The Awakening in Crisis** — *maps to: offer (first recognition or tier) under pressure* `[J]`
- *Recognizer:* the body, the blood, the ideal itself. *Staging:* at the peak of a charged scene,
  something *answers* — heat in the hands, the old words remembered, the dead going quiet. The
  DM pauses the action for one line: an out-of-fiction marker that this is an offer, then the
  fiction.
- *Offer form:* **seize it** (the calling crystallizes now, with an immediate, bounded effect in
  this scene), **let it pass** (defer — it will return at the next qualifying crisis or
  reflection boundary), or **refuse it** (decline, with the refusal recorded; the same calling
  cannot be re-offered via crisis for a cooldown).
- *Rules:* only when the engine flags eligibility *and* the scene is at high intensity (§B pacing
  tracker) — never manufactured from nothing (Earthdawn requires "of the right mindset").

**V6 · The Seer's Reading** — *maps to: abstain and progress reporting* `[D]` band, `[N]` phrasing
- *Recognizer:* anyone who reads people — a fortune-teller, an old soldier, a priest, a rival's
  cold appraisal, the character's own dreams. *Staging:* on request or on a reflection boundary,
  the reader describes the character's trajectory in graded vagueness. *Offer form:* none.
- *Rules:* a fixed ladder of phrasing bands mapped to tally state (Hawkwind precedent) — e.g.,
  *unformed* / *leaning* / *becoming* / *on the threshold* / *ready* — so the player can learn
  their trajectory in-fiction without numbers; the codex (P7) may show the exact state
  out-of-fiction. This is the only mechanism that gives *abstain* a voice.

**V7 · The Reflection at Rest** — *maps to: grant/offer batch at a scheduled boundary* `[D]`
- *Recognizer:* the self, companions around a fire, a winter spent. *Staging:* at a long rest,
  downtime, or season boundary (Pendragon Winter; Oblivion sleep), the DM runs the recognition
  pass; grants arrive as quiet realizations or small scenes the next morning; offers arrive as a
  dream, a companion's question, or the next day's visitor.
- *Rules:* the default recognition point for everything that did not warrant a crisis awakening.
  This is where check-then-batch resolution happens (Pendragon).

**V8 · The Rival Names You** — *maps to: grant (notorious/martial/dark identity) and early warning* `[N]`
- *Recognizer:* a recurring adversary (Nemesis). *Staging:* the enemy uses your epithet, fears
  your signature move, adapts to it. *Rules:* adversaries recognize from the evidence they
  *suffered*, so their recognition can precede allies' — a useful early grant voice for martial
  callings.

**V9 · The Rite or Trial** — *maps to: offer (rank within an order; tier with an institutional face)* `[D]` structure
- *Recognizer:* an order's examiners. *Staging:* a trial scene (AD&D challenge; Earthdawn circle
  tests). *Rules:* trials test for **rank** (social standing, seat), not for **capability**
  (which the tally already decides). Failing a trial never removes capability; it delays rank.

**V10 · The Body Remembers** — *maps to: grant (passive/baseline growth)* `[N]`
- *Recognizer:* the character's body and habits. *Staging:* the character notices they now do
  something without thinking — hands steady, eyes finding exits (Elder Scrolls/Kingdom Come use
  learning, voiced). *Rules:* reserved for passive abilities and small grants; never for major
  identity changes.

**V11 · The Place Answers** — *maps to: offer (mystical calling) or grant (minor boon)* `[J]`
- *Recognizer:* a shrine, standing stone, old battlefield, relic. *Staging:* arriving at a place
  resonant with the tally triggers a sign; meditating/praying/keeping vigil there is the
  acceptance (Ultima IV shrines; Skyrim stones). *Rules:* places are placed by chapter 11/13 as
  standing affordances; returning later is always possible (defer = don't kneel yet).

**V12 · The Master of the Fusion** — *maps to: offer (hybrid calling)* `[J]`
- *Recognizer:* a figure who embodies the hybrid pair (DD2 maisters). *Staging:* the hook engine
  introduces them near the character when a curated hybrid candidate surfaces. *Offer form:* the
  hybrid is presented *beside* the single-track options (P5's Wandering-Inn consolidation), in the
  fiction as "you could keep walking both roads, as I have."

**V13 · The Interested Power** — *maps to: offer (dark or transgressive calling, monster absorption)* `[J]`
- *Recognizer:* a demon, a dying god, the beast's lingering hunger (Blades Demonic Notice; DA:O
  bargains; Wildermyth transformations). *Staging:* a bargain with an explicit price. *Offer form:*
  accept with price / decline (the power remembers) / defer (it will return, usually at a worse
  moment).

**V14 · The Fraying** — *maps to: revocation warning → atonement or fall* `[D]` thresholds, `[N]` phrasing
- *Recognizer:* the bonded witness or the community. *Staging:* graded — first the witness
  withdraws (dimmer power, cooler welcome), then it speaks, then it offers the choice (BG3 Knight):
  atone (a concrete quest or cost) or turn (the calling's shadow path becomes available as its
  own offer). *Rules:* a single contradictory act only *warns*; revocation requires persistent
  contradiction or one act that was *explicitly forbidden in advance* by a sworn oath (Skull of
  Mondain precedent). Never silent.

### A.5 The offer protocol (how accept / decline / defer should work)

Synthesizing A-01, A-17, A-23, A-24, A-29 and V1–V14:

1. **Out-of-fiction marker, in-fiction content.** A one-line, out-of-fiction marker tells the
   player an offer is live (this is the codex layer, P7, and is not a blue box — it is the same
   channel a tabletop GM uses when they say "this is a big moment; take your time"). The offer
   itself is entirely in-fiction. The codex then shows the exact mechanical consequence of each
   choice. This preserves BRIEF §4 (no in-world System) and Principle VII (the player knows their
   licenses) at the same time.
2. **Three answers, always.** Accept / Decline / Defer. Defer is never a trap: a deferred offer
   persists as a *standing offer* in state with a re-presentation condition (next reflection
   boundary, next qualifying crisis, or on returning to the place/person).
3. **Decline is recorded, not punished — with one exception.** Declining an *institutional* or
   *dark-power* offer may carry a small, pre-stated relationship cost (Blades Cooperation).
   Declining a *personal* calling costs nothing but a cooldown before the same calling can be
   re-offered via the same staging.
4. **Offers have prices.** Every accept binds something: a commitment (oath), a relationship
   (lord, order, mentor), a cost (transformation bane), or a rank's obligations. Price-free offers
   feel purchased.
5. **Hybrids are offered beside, not instead of.** When a curated hybrid surfaces, the offer
   presents it next to the dominant single-track option(s) (P5), voiced by V12.
6. **One live offer per staging at a time.** At most one crisis offer per scene; reflection
   boundaries may present several, ordered by confidence.

### A.6 Recommended design space for Section A (chapter 04, with 03/11/12 hooks)

- **R-A1. Adopt the tally / witness / moment split as chapter 04's architecture.** The tally is
  `[D]` (chapter 03). The *witness* is a separate gate: public recognition (epithets,
  reputation, institutional offers) requires witnessed evidence; private recognition (awakening,
  reflection, the body) does not. The *moment* is chosen from V1–V14 by a table keyed to (policy
  outcome × calling family × current scene intensity).
- **R-A2. Give each policy outcome its own voice.** Grant → V1/V8/V10 (the world already knows).
  Offer → V2/V3/V4/V5/V9/V11/V12/V13 (someone asks). Abstain → V6 (someone reads you, vaguely),
  or silence. Revocation → V14. This eliminates the "only offers have a fictional face" gap.
- **R-A3. Model reputation as Ars Magica's triple** `{content, score, scope}` plus a separate
  renown magnitude, witness-gated, 1 point per noteworthy witnessed act with harder increments as
  it rises (Pendragon's d20-must-exceed or Ars Magica's skill-like XP). Reputation is chapter 11
  state that *reacts to* recognition but is not the recognition itself.
- **R-A4. Crystallize tiers only with challenge-banded evidence** (Burning Wheel's R/D/C mix,
  Blades' desperate-roll weighting): a tier's eligibility requires some evidence events at or
  above a challenge band, so trivial repetition cannot deepen a tier. Batch non-crisis
  recognition at reflection boundaries (Pendragon/Mouse Guard/Oblivion).
- **R-A5. Separate capability tiers from institutional ranks.** Capability comes only from the
  tally (P2/P5). Ranks are seat-limited titles inside factions (AD&D hierarchies) that confer
  standing, resources, obligations — and generate hooks. Losing a trial never removes capability.
- **R-A6. Every calling authors a *shadow* and every oath-type calling authors its forbidden
  acts in advance** (TOR shadow paths; Ultima's Skull). The shadow is recognized too.
- **R-A7. Optional player *aspirations* (Heart beats) raise salience and bias hook generation**
  toward an identity the player wants, without adding evidence weight. This gives the player a
  voice in emergence without reintroducing a menu.
- **Anti-patterns (explicitly reject):** purchased titles or manuals (Fable Title Vendor, DA:O
  manuals); NPCs speaking the ruleset's class names or numbers; compelled behavior from traits or
  passions (Pendragon madness/trait compulsion); group votes (replace with player accept);
  single-mortal-NPC recognizers who can die and strand the player (BG3 Knight bug).

**Worked sketch (for chapter 04 authors).** Tally after a long run of night ambushes, witnessed
by caravan guards, shows a specialist candidate *[stealth → ambush]* at mid confidence and a
curated hybrid *[stealth × fire-magic]* at mid confidence. The session ends at a waystation (a
reflection boundary). V7 runs: grants — none. Offers — two. The DM stages them the next morning:
(1) a caravan master (V3-lite, community institution) says the guards have started calling the
character "the Quiet Match" (V1 epithet, *already public* because witnessed) and offers a
standing contract as outrider — accepting joins the Caravaners' Compact (faction link, price:
obligations); (2) at noon a charcoal-burner who hides in her own smoke (V12, a master of the
fusion) asks whether the character wants to learn to "carry the fire quietly." Codex marker lists
both offers with their exact mechanical effects and "defer" persistence (until the character
leaves the Ashwood region / next reflection boundary). The player accepts (2), defers (1). State:
`calling=smokewalker (hybrid, tier 1)`, `standing_offer: caravaners_outrider (expires on leaving
region)`, `reputation{content:"the Quiet Match", score:1, scope:caravan-road}`.

---

## B. Living-world sandbox engines

### B.1 The problem, restated

The sandbox has no scripted finale (BRIEF §4) and no human GM. It needs four capabilities that
human GMs supply from intuition: (1) **the world moves when the player isn't looking**
(factions pursue goals); (2) **the world reacts** to what the player did (consequences propagate);
(3) **the world offers** (hooks and rumors that always lead somewhere — P16); and (4) **the world
is paced** (tension rises and falls rather than flatlining or relentlessly escalating). Tabletop
procedures, solo-play oracles, and video-game AI directors each solved one or two of these; the
catalog below is organized by which capability each entry supplies.

### B.2 Mechanics catalog

#### B.2.1 Faction simulation (the world moves and reacts)

**B-01 · Stars Without Number / Worlds Without Number — the faction turn** (11, 12)
- *How it works.* Each faction has three ratings (Force, Cunning, Wealth; 1–8), hit points
  derived from them (collapse at 0), a currency (FacCreds), XP, one or two tags that bend its
  rules, and *assets* (units, agents, holdings) that have their own HP and ratings and are what
  actually act and get attacked. A faction turn runs between sessions in a fixed order:
  initiative → maintenance (upkeep for assets beyond the faction's ratings) → goal check → income
  (roughly half Wealth plus a quarter of Force+Cunning) → **one action per faction** (attack, buy
  asset, expand influence, repair, refit, sell, seize territory, use an asset ability) → end of
  turn → **rumors and news**. An attack is an opposed roll (d10 + attacking rating vs. d10 +
  defending rating): win and the target asset takes damage; lose and your asset absorbs the
  defender's counterattack. Factions pick a *goal* (military conquest, commercial expansion,
  intelligence coup, destroy the foe...) and earn XP when they achieve it, spent on rating
  increases. WWN carries the engine into fantasy. The designer's target is ~30 minutes per turn.
- *AI-DM fit.* `+` Fully procedural and turn-based, with an explicit **rumors and news** step
  whose output is exactly what the player should hear. One action per faction per turn bounds
  drift. `−` Asset-level wargaming is heavy and, per player reports, can stall into attrition;
  the AI doesn't mind bookkeeping, but the *player* only sees headlines, so granularity should be
  spent where it produces perceivable change.
- *Take.* The turn's shape (maintain → goal → one action → rumors) is the backbone of chapter 11's
  World Turn. Opposed rating rolls resolve faction-vs-faction outcomes; every turn ends by emitting
  rumors.

**B-02 · Blades in the Dark — the faction game** (11, 12)
- *How it works.* Every faction has a **Tier** (0–VI: wealth/influence/scale; also sets the
  quality of its gear and the size of its gangs — Tier I gangs are 3–6 people, Tier V about 80) and
  a **Hold** (weak/strong: how securely it keeps its position; weak hold dropping costs a Tier).
  The crew's **status** with each faction runs −3 (war) to +3 (allies), each level an explicit
  behavioral contract (e.g., +1 helpful: helps if it costs nothing; −2 hostile: looks for chances
  to hurt you short of serious cost; −3 war: goes out of its way to hurt you — and the crew takes
  extra heat, temporarily loses hold, and gets fewer downtime actions). An operation shifts status:
  −1 or −2 with those it hurts, +1 with those it helps, no change if kept perfectly quiet.
  **Faction clocks** hold each faction's long-term project; the GM ticks those the players care
  about each downtime, and scores can tick them too. **Rep** (2 per score, ±1 per Tier of
  difference) grows the crew's Tier. **Heat** per score (0 quiet / 2 contained / 4 loud / 6 wild,
  +1 high-profile target, +1 hostile turf, +1 at war, +2 if bodies) rolls into a **Wanted Level**
  at 9. After every score, an **entanglement** is drawn from a table indexed by heat (column) and
  wanted level (dice pool): gang trouble, questioning, rivals, reprisals, the unquiet dead,
  cooperation (an allied faction calls in a favor), demonic notice, arrest. Entanglements arrive
  *already in motion* and each lists ways out (pay, hand someone over, fight, negotiate). Downtime
  runs in fixed order: payoff → heat → entanglements → activities.
- *AI-DM fit.* `+` The best-specified reactive-world engine in the corpus: every number is
  explicit, every status level is a behavioral contract an AI can follow literally, and
  entanglements turn consequences into *situations*, not notifications. Manifesting before the
  PCs can pre-empt them guarantees they are hooks rather than planning puzzles. `−` Heat/wanted is
  crime-specific; a fantasy sandbox needs a generalized per-faction "attention" axis.
- *Take.* Adopt status −3…+3 with per-level behavioral contracts, faction clocks, and a
  post-expedition **attention roll** indexed by loudness and accumulated attention.

**B-03 · Blades — the progress-clock typology** (11, 12, 06)
- *How it works.* Clocks of 4 (complex), 6 (complicated), or 8 (daunting) segments track
  *obstacles, not methods* ("The Tower," never "Climb the Tower"). Types: danger clocks (tick 1–3
  by consequence severity), racing clocks (two opposed), linked clocks (one unlocks another),
  mission clocks (a closing window), tug-of-war clocks (fill and empty), long-term projects (8
  segments, or chains of clocks), and faction clocks. The designer's image: a clock is a
  speedometer, not an engine — it reflects the fiction rather than dictating it.
- *AI-DM fit.* `+` A universal, deterministic progress primitive; "obstacle, not method"
  preserves goal 1 (any approach can tick it). `−` Segment choice is judgment; bound it by table.
- *Take.* Clocks are chapter 11's state primitive for everything that advances over time.

**B-04 · Forbidden Lands — legends, adventure sites, strongholds** (11, 13, 10)
- *How it works.* Adventure sites are generated from tables, each with a *legend* — a story
  locals tell — whose truth the GM fixes (true, partly true, false; an oracle die can resolve
  "yes, but"). Legends are the main channel for lore and hooks. Reputation governs recognition in
  new settlements (A-16). Players can found a **stronghold** (hirelings, production, defense) that
  becomes the sandbox's fixed point and a target for its threats.
- *AI-DM fit.* `+` Legends-with-truth-values are ideal rumor objects: generate the story, fix
  its truth privately, let the player investigate. `−` Truth choice is judgment unless tabled.
- *Take.* Every rumor is a state object with a hidden truth value fixed at creation, never
  retconned to suit play.

**B-05 · Ars Magica — seasons and covenant lifecycles** (11)
- *How it works.* Time is budgeted in **seasons** (one main activity per three months).
  Covenants have a lifecycle named after the seasons — Spring (young, scrappy), Summer
  (flourishing), Autumn (established, complacent), Winter (declining toward oblivion). Characters
  make aging rolls every winter after 35; magi accumulate Warping toward Twilight and eventually
  Final Twilight. Sagas span decades; troupe play rotates which characters are played.
- *AI-DM fit.* `+` A lifecycle for *institutions* — factions rise and decay without anyone
  attacking them. Season-grain downtime bridges adventures cleanly. `−` Lab systems irrelevant.
- *Take.* Factions carry a lifecycle stage (rising / flourishing / entrenched / declining) that
  biases goal choice and clock speed. Downtime is budgeted in coarse units with one primary
  activity each.

**B-06 · King Arthur Pendragon — the annual cycle and the Great Pendragon Campaign** (11, 12)
- *How it works.* Roughly one adventure per game-year, then a Winter Phase run as a fixed batch:
  experience rolls, aging, squire and horse survival, training, Glory tally, marriage and
  childbirth rolls, child survival, and a manor-economy roll that sets next year's living
  standard. *The Great Pendragon Campaign* spans 80+ years; the world changes era by era whether
  or not the knights act, and knights age, die, and are succeeded by heirs.
- *AI-DM fit.* `+` A fixed cadence is the simplest possible living-world clock, and a batch phase
  is exactly what an AI executes well. `−` The GPC's scripted history conflicts with "no scripted
  finale"; keep the cadence, drop the script.
- *Take.* The World Turn runs at a fixed fictional cadence *and* on demand whenever time passes.

**B-07 · Dwarf Fortress — generated history, legends, retire vs. abandon** (11, 13)
- *How it works.* World generation simulates centuries — civilizations, wars, artifacts,
  historical figures; Legends mode lets the player browse all of it, and the player's own
  fortresses and adventurers are recorded in the same history. A fortress can be *retired* (it
  keeps living as an NPC settlement and can be unretired) or *abandoned* (it becomes a ruin anyone,
  including a later player, can reclaim or explore in adventure mode).
- *AI-DM fit.* `+` History-as-database is the right model for world memory; retire/abandon maps
  straight onto §D. `−` Full simulation is out of scope; the AI generates history lazily and
  records it.
- *Take.* Keep an append-only **chronicle** that NPCs, rumors, and legends draw on.

**B-08 · Kenshi — world states from pivotal NPCs** (11)
- *How it works.* Killing or capturing specific faction leaders triggers *world states*: towns
  change owners, fall to ruin, or pass to other factions; spawns and politics change permanently.
- *AI-DM fit.* `+` A small set of pivotal NPCs whose fate deterministically rewires the map is a
  cheap, legible way to make player impact permanent and consistent. `−` Pre-authored.
- *Take.* Each major faction names 1–3 **linchpins** whose death, capture, or turning has a
  pre-declared world-state consequence.

**B-09 · Mount & Blade — lords, relations, wars, ransom** (11)
- *How it works.* Kingdoms are made of individual lords with personal relations to the player;
  wars start and end on their own; lords are captured and ransomed; fiefs change hands.
- *AI-DM fit.* `+` Two-level relations (per NPC and per faction) give texture cheaply.
- *Take.* Keep per-NPC disposition for named NPCs beside per-faction status; they can diverge.

#### B.2.2 Directors, storytellers, drama managers (the world is paced)

**B-10 · RimWorld — AI storytellers** (12, 11)
- *How it works.* A storyteller schedules incidents (raids, disease, traders, windfalls) from
  colony state — wealth, population, recent losses, time since the last big event. **Cassandra
  Classic** runs a cycle: an "on" phase (~4.6 days) in which one or two major threats fire, then an
  "off" phase (~6 days); major threats are at least ~1.9 days apart; minor incidents average one
  per ~4.8 days; and the game opens with a guaranteed gentle sequence (one mad animal, then one
  raider) before the cycle starts. **Phoebe Chillax** spaces major threats far apart. **Randy
  Random** ignores pacing. An **adaptation** score grows while the colony prospers and is knocked
  down by losses, scaling threat intensity; a **population-intent** curve makes newcomer events
  likely for tiny colonies and unlikely for large ones.
- *AI-DM fit.* `+` Named pacing *personalities* over one shared event pool; adaptation and
  population-intent are ready-made rubber bands for a solo game. `−` Colony-sim numbers.
- *Take.* Pacing profiles (default rising cycle; gentle option). Adaptation: after a defeat or a
  dying state, a recovery window with no major threats; after a streak of easy wins, allow
  escalation. The opening gentle sequence belongs to the starter setting.

**B-11 · Left 4 Dead — the AI Director** (12)
- *How it works.* The Director estimates each survivor's **emotional intensity** (rising with
  damage taken, nearby kills, being incapacitated) and cycles: **build-up** (normal spawning) →
  **sustain peak** briefly after intensity maxes → **peak fade** → **relax** (no new threats while
  survivors recover) → build-up again. It also procedurally places supplies and special threats.
- *AI-DM fit.* `+` Implementable in text: a hidden `intensity` fed by recent harm, danger, and
  stakes, and a phase that decides whether the world pushes or rests — the quantitative answer to
  "don't flatline, don't grind the player down." `−` Real-time; translate to scenes.
- *Take.* A scene-level intensity tracker with four phases governs *when* hooks, entanglements,
  and wandering threats fire.

**B-12 · The Alexandrian — "Don't Prep Plots": timelines, bangs, the campaign status document** (11, 12)
- *How it works.* Prep **situations**, not plots. Each situation gets a **timeline** of what
  happens if the PCs do nothing, ending in a new status quo. Keep two timelines: background events,
  and **bangs** — events that come looking for the PCs, kept as flexible "bullets" customized when
  fired (kickers, spotlight bangs, timeline bangs, random-encounter bangs). Bangs force choices
  but never dictate responses. A **campaign status document** holds the bang timeline, background
  events with a public "word on the street" layer, and per-scenario change logs recording how
  locations evolved after the PCs disturbed them; it is archived each session.
- *AI-DM fit.* `+` The status document *is* the externalized world-state store P13 demands,
  organized for play. If-ignored timelines give factions default behavior without improvisation.
- *Take.* Mirror it in state: `situations[]` with default timelines, `bangs[]` fired by the
  pacing director, `news[]` (public), per-location change logs.

**B-13 · The Alexandrian — Three Clue Rule, inversion, node-based design, proactive nodes** (11, 12, 13)
- *How it works.* For any conclusion the players must reach, place at least three clues (they
  will miss, misread, or ignore some). Inverted: give players access to any three clues and they
  will reach at least one conclusion — so a web of nodes (people, places, organizations, events),
  each holding ≥3 clues pointing onward, yields robust non-linear play. **Proactive nodes** come to
  the players (response teams, messengers, assassins) when they stall or provoke a reaction.
- *AI-DM fit.* `+` This is P16 as architecture. `−` The generator must write the clues into
  multiple places *in state* at creation, not improvise them in narration.
- *Take.* A hook is a node; creating it writes ≥3 clue placements (person / place / object) and
  one proactive fallback bang.

**B-14 · Hexcrawl procedures — The Alexandrian; Necropraxis's overloaded die; Knave** (10, 11, 13)
- *How it works.* The Alexandrian's hexcrawl measures travel in **watches**; each watch rolls a
  d12 encounter check (1 = wandering encounter; 12 = the hex's keyed location is found); movement
  budgets depend on terrain and encumbrance; leaving landmarks or trails requires navigation, with
  explicit progress penalties for getting turned around. Necropraxis's **overloaded encounter die**
  (the Hazard System) gives *every* face a meaning — in its combat form: setback, fatigue,
  expiration of ongoing effects, locality shift, percept (a clue to the enemy's plan), advantage;
  exploration versions similarly mix encounters, signs of encounters, resource depletion, and
  environmental change — so no roll is null. Knave-style procedures keep exploration abstract
  ("a turn spent exploring this hex") rather than nesting crawls inside crawls.
- *AI-DM fit.* `+` Deterministic, tabled; the overloaded die guarantees every tick of time
  produces something (a mechanical anti-dead-end), and omens-before-encounters is built-in
  telegraphing (§C). `−` Hex geometry optional; regions or pointcrawls work equally well.
- *Take.* One **time-tick roll** per watch (wild), turn (delve), or day (settlement) on an
  overloaded table: threat / omen / depletion / shift / opportunity / keyed discovery.

**B-15 · West Marches (Ben Robbins)** (11, 13)
- *How it works.* A frontier town as base; a wilderness of areas (marsh, haunted forest, ruined
  temple) more dangerous the farther out; **no plot** — players choose destinations from rumors,
  treasure maps, and pooled discoveries on a shared map; persistent world. Robbins' three pillars:
  players schedule sessions, parties are ad hoc, no plot.
- *AI-DM fit.* `+` Distance-as-difficulty is a legible, player-controlled dial that needs no
  character levels — ideal for a system with none (P2). The base anchors consequences. `−`
  Multi-group scheduling is irrelevant solo.
- *Take.* The starter setting is a West Marches layout.

**B-16 · Mythic Game Master Emulator 2e — Chaos Factor, Threads, Characters** (12, 11)
- *How it works.* Solo players ask yes/no **fate questions** resolved against odds shifted by a
  **Chaos Factor** (1–9, start 5; up when scenes slip out of the player's control, down when in
  control). Doubles at or under the Chaos Factor trigger a **random event** whose focus comes from
  a d100 table (remote event, NPC action, new NPC, move toward or away from a thread, PC
  positive/negative, ambiguous, current context), targeting entries on weighted **Threads** and
  **Characters** lists (an entry listed several times is more likely). Scene setups can be
  *altered* or *interrupted* by a roll against Chaos.
- *AI-DM fit.* `+` Built for no-human-GM play. Weighted lists are a ready hook selector; Chaos is
  a second pacing axis (control vs. chaos) complementing intensity. `−` The AI DM *knows* world
  state, so the oracle's role is surprise injection, not truth generation.
- *Take.* Keep weighted `threads[]` and `characters[]` in state; random-event focus picks from
  them; a control/chaos meter modulates scene interruption frequency.

**B-17 · Crusader Kings III — on_actions, pulses, story cycles** (11)
- *How it works.* CK3 dropped CK2's "mean time to happen" polling for **on_actions** (hooks fired
  when something happens: a birth, a death, a war) and periodic **pulses** (e.g., yearly), each
  drawing from weighted lists of eligible events with triggers, cooldowns, and an explicit weight
  for "nothing happens." **Story cycles** are persistent multi-stage narratives attached to a
  character that fire their own events until an end condition.
- *AI-DM fit.* `+` Exactly how consequence propagation should fire: *when X happens, consider
  events eligible for X, weighted, with cooldowns.* Story cycles model long personal threads. `−`
  Authoring load.
- *Take.* Consequences = on_action hooks on state changes + a periodic pulse.

**B-18 · Façade — beat sequencing to a tension arc** (12)
- *How it works.* Authored **beats** carry preconditions, weights, priorities, and a tension
  effect; the drama manager picks the unused eligible beat whose tension effect best fits the
  near-term target on an authored arc.
- *AI-DM fit.* `+` Formalizes "choose the next push to fit the desired tension." `−` A sandbox has
  no single arc — the target must be the director's cycle (B-11), not an Aristotelian curve.
- *Take.* Candidate pushes carry an `intensity_delta`; pick the one best matching the phase target.

**B-19 · Valve's rule-matching dialog (GDC 2012); Hades' prioritized, requirement-gated lines** (12, 11)
- *How it works.* Valve matches hundreds of world facts against a rule database; the **most
  specific matching rule wins**, general rules serve as fallbacks, so writers can add special cases
  and running gags without code. *Hades* selects among thousands of lines by requirements and
  priority, so characters remember and respond to the player's specific history (including deaths).
- *AI-DM fit.* `+` "Most specific eligible wins" is the right tie-break whenever several
  consequence events or recognition stagings qualify; it makes reactions feel personal.
- *Take.* Rank eligible events by specificity: this-NPC-and-this-deed > faction > region > generic.

**B-20 · Tynan Sylvester — "The Simulation Dream"** (11, 12)
- *How it works.* RimWorld's designer argues that emergent story lives in the *player's model* of
  the game — players read intent into systems (apophenia) — so simulation the player cannot
  perceive is wasted, and what matters is simulation that leaves interpretable traces.
- *AI-DM fit.* `+` A decisive rule for spending living-world complexity.
- *Take.* Every World Turn change of consequence emits at least one perceivable trace (a rumor, a
  price, a new banner on the gate, a missing face at the inn).

### B.3 Recommended design space for Section B (chapters 11, 12, 13)

**B-R1. A World Turn procedure (chapter 11)**, run at every downtime/travel boundary and whenever
fictional time elapses:

| Step | What happens | Precedent | Kind |
|---|---|---|---|
| 1. Elapse | Compute time passed in turn units (day / week / season) | Ars Magica seasons; Pendragon year | `[D]` |
| 2. Maintain | Faction upkeep; lifecycle stage may shift | SWN maintenance; covenant seasons | `[D]` |
| 3. Default timelines | Advance each situation's if-ignored timeline | Alexandrian timelines | `[D]` |
| 4. Faction actions | Each faction takes **one** action toward its goal: tick its clock, or opposed rating rolls vs. a rival | SWN; Blades faction clocks | `[D]` roll, `[J]` target |
| 5. Consequences | Fire on_action hooks for state changes since the last turn; eligible events weighted, most-specific wins, cooldowns honored | CK3; Valve; Kenshi | `[D]` |
| 6. Attention | For each faction the player crossed, roll an entanglement indexed by loudness × accumulated attention | Blades heat/entanglements | `[D]` |
| 7. News & rumors | Emit perceivable traces: rumors with fixed hidden truth values, news, visible changes | SWN rumors; FL legends; Sylvester | `[D]` generate, `[N]` phrase |
| 8. Queue | Update the bang queue and weighted thread/character lists | Alexandrian bangs; Mythic lists | `[D]` |

**B-R2. Faction model.** Tier with hold; three or four ratings for opposed rolls; one or two tags;
a goal and a clock; a lifecycle stage; 1–3 linchpins with pre-declared world-state consequences;
status toward the player −3…+3 with a behavioral contract per level; per-NPC dispositions for
named members.

**B-R3. Pacing director (chapter 12).** Hidden `intensity` (inputs: harm taken, lethal context,
clocks near completion, recent conflict) cycling build-up → peak → fade → relax; a pacing profile
(default rising cycle; gentle option); **adaptation** — after a defeat or dying state, a recovery
window with no major threats. Candidate pushes carry `intensity_delta`; choose the eligible push
that best fits the phase target, ties broken by specificity.

**B-R4. Hooks never dead-end.** Every hook is a node with ≥3 clue placements in state and one
proactive fallback bang that fires after N scenes without progress; P16's three-inconclusive-results
trigger fires it early.

**B-R5. Overloaded time-tick roll** per watch/turn/day. **Omens always precede threats** — the
same rule anchors §C's telegraph layer.

**B-R6. Rumors are objects:** `{seed, source, truth ∈ {true, partial, false, outdated}, points_to}`
fixed at creation. Rumors about the player's own deeds are how reputation (§A) propagates.

**B-R7. Starter setting as West Marches (chapter 13):** a safe-ish base, concentric danger bands
keyed to threat bands (the no-levels difficulty dial), rumor-driven exploration, persistent map
knowledge, a gentle opening sequence, and three or four factions with conflicting clocks already
running.

**B-R8. A chronicle:** an append-only world history that NPCs, rumors, and legends draw on and into
which the player's deeds — and eventually their retirement — are written (§D).

**Worked sketch.** The player spends six days hunting a wyrm in the Tangle (a downtime boundary).
*Elapse:* one week unit. *Default timelines:* the Mill Dispute reaches step 3 (the miller's son is
jailed). *Faction actions:* the Salt Guild (Tier 2, goal: monopoly) ticks "Corner the Salt Road"
4→5 of 8; the Ash Wardens (Tier 1) attack a Guild warehouse — Force 3 + d10 (7) = 10 vs. Guild
Cunning 2 + d10 (9) = 11 → the Wardens lose and their asset takes the counterattack.
*Consequences:* on_action `great_beast_slain` has two eligible events — "hunters flood the Tangle"
(regional) and "a wyrm-cult elder swears vengeance on the slayer" (keyed to this beast and this
PC); the second wins on specificity and joins the bang queue as a proactive node. *Attention:* the
hunt was loud (bonfires, a burnt grove) → the Tangle Wardens' attention table yields
"Questioning": a warden captain waits at the inn. *Rumors:* "the wyrm was the last of its clutch"
— truth *false* (one egg survives); it points to the node "The Last Egg," with three clue
placements (a hunter's boast, a cracked shell in the lair, a cult tithe ledger). *Pacing:*
intensity is at peak after the fight, so the director enters *relax*: the captain's visit is
staged as a conversation, and the cult elder is held in the queue.

---

## C. Telegraphed death

### C.1 The problem, restated

BRIEF §4: death is real but telegraphed — explicit warnings before lethal risk, a dying state, a
last-chance choice; defeat usually means capture, injury, loss, or a changed situation; a single
unlucky roll never ends a character without warning. That decomposes into four design layers:

1. **Warn** — how the game makes lethal stakes legible *before* the roll that could kill.
2. **Dying** — the intermediate state between "hurt" and "dead," with its own clock.
3. **Last chance** — the choice point where the player trades death for a cost.
4. **Resolution** — death, or one of many defeat-without-death outcomes.

The catalog groups systems by the layer they contribute most to; many contribute to several.

### C.2 Mechanics catalog

#### C.2.1 Warning layer — how games declare lethal stakes

**C-01 · Apocalypse World / Dungeon World — soft moves before hard moves** (12, 07)
- *How it works.* The GM's moves include "announce future badness," "announce off-screen
  badness," and "tell them the possible consequences and ask." A **soft move** sets up a threat and
  leaves room to react; a **hard move** delivers an irrevocable consequence. Hard moves are
  reserved for *golden opportunities*: a failed roll, or a soft move the players ignored.
- *AI-DM fit.* `+` A two-step rule the AI can literally follow: no irrevocable harm unless a
  warning was issued and not answered, or the player rolled into it. `−` "Golden opportunity"
  needs a crisp definition to be `[D]`.
- *Take.* Lethal consequences require a prior soft move (a **Lethal Warning**) that the player
  saw and did not neutralize.

**C-02 · Blades in the Dark — position and effect declared before the roll** (06, 07, 12)
- *How it works.* Before a roll, the GM sets **position** (controlled / risky / desperate) and
  **effect**, and states the likely consequences; the player can change approach, push (stress),
  or accept a Devil's Bargain. A desperate position is where severe or fatal harm lives.
- *AI-DM fit.* `+` Stakes are public before dice. `−` Position is a judgment call.
- *Take.* A *lethal* tier of position must be announced out loud before the roll; if it wasn't
  announced, the worst consequence on the table is sub-lethal.

**C-03 · Torchbearer — death only through three doors** (07)
- *How it works.* The GM may inflict the Dead condition only (a) through a **kill conflict**
  (both sides choose kill as the goal — choosing to kill puts your own life on the line), (b) when
  a character who is already **Injured** fails a test involving physical harm, or (c) when one who
  is already **Sick** fails a test involving disease, poison, madness, or grief. Even losing a kill
  conflict can be softened into a compromise.
- *AI-DM fit.* `+` The cleanest precedent for a *closed list of lethal doors*. Every door
  requires either declared lethal intent or a pre-existing damaged state. `−` None.
- *Take.* Death is legal only through an enumerated list of doors (the "two keys" rule, C.3).

**C-04 · Cairn and the Into the Odd lineage — telegraph danger, be honest** (07, 12)
- *How it works.* Cairn's Warden principles direct the GM to telegraph serious danger, making more
  dangerous situations more obvious, to put traps in plain sight, and to answer player questions
  honestly and directly. Chris McDowall's *Information → Choice → Impact* doctrine: give clear
  information, let the players make a meaningful choice, then deliver impact; difficulty should be
  made clear *before* an attempt, and extreme danger can be a "barrier to entry" ("this won't
  work") rather than a hidden roll.
- *AI-DM fit.* `+` A principle the AI can check itself against: "did the player have the
  information to choose?" `−` A principle, not a mechanism.
- *Take.* Every lethal threat is described with at least one perceivable sign of its lethality
  before it can act lethally (the overloaded die's *omen* face, B-14).

**C-05 · Burning Wheel — intent and task; "let it ride"** (01, 07)
- *How it works.* Before rolling, the player states intent and task and the GM states what
  failure will mean; the result stands for the whole situation (no re-rolling until circumstances
  change).
- *AI-DM fit.* `+` Failure consequences are negotiated before dice.
- *Take.* The DM names the failure consequence (including "you may die") when the roll is set.

#### C.2.2 Dying layer — the state between hurt and dead

**C-06 · D&D 5e — 0 HP and death saving throws** (07)
- *How it works.* At 0 HP you fall unconscious and roll a d20 death save each turn: 10+ is a
  success, lower a failure; three successes stabilize, three failures kill. A natural 20 restores
  1 HP; a natural 1 counts as two failures. Taking damage at 0 HP is a failure (a critical hit,
  two). Massive damage — damage remaining after reaching 0 that equals or exceeds your maximum HP —
  kills outright.
- *AI-DM fit.* `+` Fully deterministic, three-turn window for rescue. `−` Death can arrive from
  pure dice with no player choice, and the instant-death rule violates "never one roll."
- *Take.* A turn-clocked dying window is good; remove instant death; add a player choice.

**C-07 · Pathfinder 2e — Dying, Wounded, Doomed; Hero Points** (07)
- *How it works.* At 0 HP you gain **dying 1** (dying 2 from a critical); at **dying 4** you die.
  Each turn a flat recovery check at DC 10 + dying value moves dying down or up by 1 (2 on a
  critical either way). Losing dying leaves you **wounded 1** (stacking); if you go down again
  while wounded, the wounded value is added to your new dying value — repeated knockdowns get
  deadlier. **Doomed** lowers the dying value at which you die and fades one per full rest.
  Separately, a character can spend *all* their Hero Points (at least one) to shed dying entirely
  and stabilize at 0 HP without increasing wounded — a player-controlled escape hatch.
- *AI-DM fit.* `+` The best numeric dying track in print: an explicit ladder, memory of recent
  near-deaths (wounded), and a player-spendable reprieve. `−` Many small numbers; fine for an AI.
- *Take.* Adopt a dying ladder with **wounded-style memory** (each fall makes the next more
  dangerous until properly rested) and a spendable reprieve resource.

**C-08 · Cairn and Mausritter — HP as avoidance, then attribute damage and critical injury** (07)
- *How it works.* Hit Protection represents avoiding harm, not flesh. Damage past 0 HP strikes the
  STR attribute; the victim then saves against the new STR — failure is **critical damage**:
  incapacitated, and dead within about an hour without aid. STR 0 is death. In Cairn, damage that
  lands *exactly* on 0 HP instead rolls on a **Scars** table: a permanent mark that can even raise
  an attribute, or a lasting setback. Mausritter: every STR hit forces a save to keep fighting;
  failure gives the **Injured** condition and takes you down; left untended for six exploration
  turns, you die.
- *AI-DM fit.* `+` The HP-is-avoidance framing makes being "hit" mean something (and lets HP loss
  be narrated as near-misses and exhaustion rather than wounds). Scars make near-death
  *transformative*. `−` STR hits can kill fast without a choice point.
- *Take.* Vitality as avoidance/stamina; real wounds are a separate, slower track; exact-zero
  scars are a delightful near-death *reward* mechanic.

**C-09 · Mörk Borg — the Broken table** (07)
- *How it works.* At 0 HP roll d4: unconscious briefly then back with a little HP; a broken or
  severed limb or lost eye; internal bleeding — death within hours unless treated; or dead.
- *AI-DM fit.* `+` Tabled. `−` A single roll kills 25% of the time — the exact thing BRIEF forbids.
- *Take.* Use the *non-lethal* entries (maiming, bleeding clocks) as a menu of lasting
  consequences; never a random death row.

**C-10 · Darkest Dungeon — Death's Door** (07)
- *How it works.* At 0 HP a hero enters **Death's Door** with heavy penalties; every further hit
  forces a deathblow check (base ~67% to survive, capped at 87% with bonuses). Leaving Death's
  Door leaves a lingering recovery penalty for the rest of the expedition.
- *AI-DM fit.* `+` Dramatic, readable ("one more hit could kill"). `−` Still dice-only death.
- *Take.* The "every further hit is a risk" state is a strong dying *warning*; pair it with a
  choice, not only a percentage.

**C-11 · XCOM (2012/Enemy Within) — bleeding out** (07, 06)
- *How it works.* Fatal damage can instead leave a soldier critically wounded and bleeding out for
  about three turns; a medkit stabilizes them (out of action for the mission) or the squad
  finishes the mission in time. Survivors carry lasting costs (reported as a permanent Will loss).
- *AI-DM fit.* `+` A rescue clock that turns a death into an *objective* for the rest of the scene.
- *Take.* The dying state should create a new, explicit objective (reach them, carry them out,
  bargain for them).

**C-12 · Blades in the Dark — harm levels, resistance, armor, trauma** (07)
- *How it works.* Harm is written as specific injuries at levels 1 (lesser: reduced effect), 2
  (moderate: −1 die), 3 (severe: incapacitated without help or pushing), 4 (fatal). A full row
  overflows upward; overflowing level 3 is a catastrophic permanent consequence — which may be
  death. A player may **resist** any consequence: resistance always works (reduce or avoid; the
  GM's reduce-vs-avoid habit sets the campaign's grittiness), and costs stress of 6 minus the
  highest die of the resistance roll. Armor boxes can reduce harm instead. A character dies from
  level-4 harm only if they *don't resist it* (sometimes a player chooses death as right for the
  story). Stress maxing out causes **trauma**: taken out of the scene, a permanent trauma
  condition; the fourth trauma retires the character (§D).
- *AI-DM fit.* `+` Death requires the player to decline resistance — the player always holds the
  last key. Trauma turns repeated brushes with disaster into a *retirement* clock rather than a
  death clock. `−` Stress bookkeeping is extra (fine for an AI).
- *Take.* The player always holds a resist/concede option at the final step; mental/spiritual
  strain accumulates into lasting conditions that eventually end a *career*, not a life.

#### C.2.3 Last-chance layer — the choice at the threshold

**C-13 · Dungeon World — Last Breath, and the revised "Face Death" menu** (07)
- *How it works.* Original **Last Breath**: when dying, glimpse the land of Death and roll with no
  modifier: 10+ stable; 7–9 Death offers a bargain (take it and live, refuse and die); miss, dead.
  The designers later replaced it with a **menu** for fatal harm: be **captured** (live, lose
  freedom, leave a token behind); **go out in glory** (control one last act, then die); **gamble
  with Death** (roll, with costs on a partial); **peek through the Veil** (survive Death-marked, one
  step closer next time); **transform** (become someone new — change class).
- *AI-DM fit.* `+` The menu is the single most useful artifact in this section: it converts
  death into a player choice among authored costs, each an AI can execute. `−` "Gamble" alone
  still allows dice death — acceptable only because the player chose to gamble.
- *Take.* The last-chance choice should be a closed menu (C.3), including a gamble that is
  *opt-in*.

**C-14 · Ironsworn — Endure Harm at zero, and Face Death** (07)
- *How it works.* At 0 health, a failed Endure Harm rolls a d100 table: 1–10 mortal wound (Face
  Death); 11–20 dying (heal within an hour or two, or Face Death); 21–35 unconscious (Face Death
  only if a merciless foe is there); 36–50 reeling (vigorous action risks another roll); 51–100
  battered but standing. **Face Death** (classic): a strong hit — death rejects you; a weak hit —
  choose: die, but only after a **noble sacrifice**, or Death wants something: swear a
  formidable-or-extreme iron vow to fulfil it, returning **cursed** until it's done (fail or refuse
  the vow and you die); a miss — dead. Starforged adds legacy continuation (§D).
- *AI-DM fit.* `+` Death with *terms*: the bargain becomes a quest thread and a debility — a
  consequence that generates story (and hooks for §B). The mortal-wound results mostly *delay* the
  decision, creating rescue windows. `−` A miss on the final roll is dice death.
- *Take.* "Death's Bargain" (a curse + a vow-quest) belongs on the last-chance menu; outcomes
  that merely delay (dying/unconscious) give companions and the pacing director time to act.

**C-15 · Fate Core — Conceding vs. being Taken Out** (07, 06)
- *How it works.* Before any roll, a player may **concede** a conflict: they lose, but they
  describe *how*, avoiding the worst fates, and receive a fate point plus one per consequence
  already suffered. If instead they are **taken out**, the winner decides what happens to them.
  Consequences (mild/moderate/severe) absorb shifts of harm as lasting named conditions.
- *AI-DM fit.* `+` A pre-emptive, *rewarded* surrender option; the player trades control of the
  outcome for dignity and resources. `−` Needs a trigger point (before dice).
- *Take.* A **Yield** option before any lethal-context roll: the player loses the scene on
  negotiated terms and gains a small resource.

**C-16 · 13th Age — Flee and take a campaign loss** (07, 11)
- *How it works.* While any PC is conscious, any player may propose that the party flee; if all
  agree, they escape, carrying their fallen, and everyone alive survives — but the party takes a
  **campaign loss**: a story-level setback (the village burns, the villain gets the relic, an ally
  dies).
- *AI-DM fit.* `+` Converts personal death into *world* consequence — exactly the living world's
  input. `−` None in a solo game (no unanimity needed).
- *Take.* A **Retreat** option that is always available with a pre-stated world cost, which feeds
  chapter 11's clocks directly.

**C-17 · Warhammer Fantasy Roleplay 4e — Fate and Fortune** (07)
- *How it works.* Fate points are a scarce permanent pool: spending one avoids death (swapping it
  for incapacitation) or negates a single event's damage, and it is gone for good; new Fate is
  awarded only for extraordinary heroism. Fortune (rerolls) refreshes each session up to current
  Fate — so burning Fate also makes you less lucky.
- *AI-DM fit.* `+` A visible, finite "lives" counter that the player spends deliberately; its
  depletion is itself a telegraph ("I have no Fate left"). `−` Pure resource; no story texture.
- *Take.* A finite, visible reprieve resource that can only be earned back by great deeds; its
  level tells the player how close to real mortality they are.

#### C.2.4 Resolution layer — death and its alternatives

**C-18 · Mouse Guard — twists and conditions; conflicts end in compromise** (07, 01)
- *How it works.* A failed test yields either a **twist** (a new obstacle) or success at a price —
  a **condition** (Hungry/Thirsty, Angry, Tired, Injured, Sick), each with its own recovery test.
  Conflicts end with the loser still owed a compromise scaled to how close the fight was.
- *AI-DM fit.* `+` Failure as a *changed situation* is the default, not damage. Compromise scales
  with closeness — a computable rule.
- *Take.* Losing a lethal conflict narrowly should still yield a compromise from the winner.

**C-19 · Kenshi and Mount & Blade — being beaten is the norm, dying the exception** (07, 11)
- *How it works.* In Kenshi, characters knocked unconscious are usually looted, left, enslaved,
  imprisoned, or eaten by wildlife depending on who beat them; limbs can be lost and replaced with
  prosthetics. In Mount & Blade, a defeated player is taken prisoner and escapes after a time,
  having lost their party and some belongings.
- *AI-DM fit.* `+` Defeat outcomes are *determined by the victor's nature*: slavers enslave,
  bandits rob, beasts drag you off, the law arrests. That is a table the AI can follow.
- *Take.* A **victor-disposition table**: what this kind of foe does with a beaten enemy.

**C-20 · Hades, Souls-likes, Nemesis — death as a story beat** (07, 11)
- *How it works.* *Hades*: dying returns you to the house, where the story advances and
  characters remember how you died; limited Death Defiance charges revive you mid-run. *Souls*:
  death drops your currency at the spot; one chance to reclaim it — die first and it's lost.
  *Shadow of Mordor*: the orc who killed you is promoted and remembers.
- *AI-DM fit.* `+` Defeat *changes the world* (a promoted enemy, a lost cache that can be
  recovered once). `−` These are resurrection games; permadeath is off in all three.
- *Take.* Defeat-without-death should always write world state: the enemy who beat you grows;
  what you lost lies somewhere you can go back to, once.

**C-21 · Cairn Scars; Blades trauma; BW's "lasting consequence" culture** (07, 04)
- *How it works.* Near-death leaves marks — Cairn's scars (sometimes an improvement), Blades'
  permanent trauma conditions (which grant XP when they cause trouble), Fate's severe consequences.
- *Take.* Surviving the dying state should leave a **mark** with both texture and, sometimes, an
  upside — and marks are evidence (chapter 03) for callings (the scarred veteran, the one who came
  back wrong).

### C.3 Recommended design space for Section C (chapter 07, with 06/11/12 hooks)

**C-R1. The Two-Key Rule for death `[D]`.** A character can die only if **both** keys are turned:
- **Key 1 — Declared lethality.** The threat was established as lethal *before* the roll: an
  explicit Lethal Warning (C-01 soft move; C-02 declared position; C-04 visible sign; B-14 omen),
  recorded in state as `lethal_context=true` for that threat/scene.
- **Key 2 — Already dying, or chose to risk it.** The character is already in the Dying state
  (C-07), *or* the player explicitly chose a gamble/last stand (C-13), *or* the player declined a
  resist/yield option offered at the brink (C-12, C-15).
Without both keys, the worst available outcome is Dying, a lasting mark, or a defeat outcome —
never death. This is Torchbearer's closed-doors principle (C-03) generalized and made auditable.

**C-R2. The ladder: Warned → Staggered → Dying → Threshold.**
- *Warned:* the threat carries `lethal_context`; narration must include a perceivable sign.
- *Staggered (Vitality 0):* Vitality is avoidance/stamina (C-08); at 0, further hits become
  **wounds** — named, lasting injuries on a severity track (C-12) — and each wound in a lethal
  context advances toward Dying.
- *Dying:* a small ladder (e.g., Dying 1–3) with a per-round recovery/deterioration check and
  **wounded-style memory** (C-07): each time you fall, you start the next fall one step worse
  until properly rested. Dying creates an explicit rescue objective for companions and the scene
  (C-11); the pacing director's adaptation (B-R3) suppresses *new* threats while it resolves.
- *Threshold:* when the dying ladder would pass its top, the player does **not** roll to die — they
  choose from the last-chance menu.

**C-R3. The Last-Chance Menu (closed, ≥6 options), synthesized from C-13…C-17 `[D]` structure,
`[J]` details.**
1. **Captured** — survive in the victor's hands (victor-disposition table, C-19); gear taken to a
   known place; a rescue/escape thread opens.
2. **Maimed** — survive with a permanent injury (a Mörk Borg/Kenshi-style entry, C-09/C-19); may
   later be offset by a prosthetic, a regrown limb, or a calling that embraces it.
3. **Death's Bargain** — survive *cursed* until a vow-quest is fulfilled (C-14); refusing or
   abandoning the quest returns you to the threshold.
4. **Left for Dead** — survive, lose the scene's objective and some possessions (Fate "taken out"
   softened), wake later somewhere the fiction implies.
5. **Rout** — escape, carrying the fallen, and accept a **campaign loss** that ticks a named world
   clock (C-16).
6. **Spend a Reprieve** — spend a scarce, visible reprieve point (C-17, C-07 Hero Points): stabilize
   at the bottom rung with no other cost. Reprieves are earned back only through great deeds.
7. **Last Stand** — go out in glory: a final action at maximum effect, then death (C-13); the deed
   enters the chronicle as a legend (§D).
8. **Gamble** — roll to cheat death; success = stable, partial = pick one of 1–4, failure = death.
   Opt-in only.
The DM may strike options the fiction makes impossible (no one to capture you in an empty tomb),
but must always leave at least three, including one that is not death.

**C-R4. Yield and Retreat before dice (C-15, C-16).** At any point before a lethal-context roll,
the player may **Yield** (lose on negotiated terms; small resource gain) or **Retreat** (escape
with a pre-stated world cost). These are always legal basic actions (Principle VII's basic tier).

**C-R5. Defeat outcomes by victor disposition (C-19, C-20).** Every adversary archetype
(chapter 09) carries a `defeat_disposition` (kill / capture / rob / enslave / ransom / drive off /
drag to lair / leave), and defeat writes world state: the victor gains renown or rank (Nemesis),
lost gear is placed somewhere recoverable once (Souls), and the player's reputation takes a
content entry ("the one the Salt Guild broke").

**C-R6. Marks from the brink (C-08, C-21).** Surviving Dying leaves a mark rolled or chosen from a
table (scar, tremor, ghost-sight, a debt to Death) — some with upsides — recorded as tag evidence
for callings (chapter 03/04).

**C-R7. Mental strain retires, it doesn't kill (C-12).** Accumulated dread/strain produces lasting
conditions; a fourth (or chosen threshold) ends the adventuring career — feeding §D's retirement,
not death.

**Worked example.** A barrow-wight (adversary `lethal_context: true`, disposition: *drag to lair*)
wakes. The time-tick omen earlier reported frost on the grave-goods and a wight's hand-print on
the seal (Warning issued, Key 1 turned). The player fights. Vitality 12 → 0 over three exchanges
(near-misses and exhaustion); the fourth hit lands a wound: "Grave-cold in the shoulder" (moderate).
Next hit: Dying 1. The director freezes new threats (adaptation). The companion drags the player
back; the player fails the recovery check → Dying 2. The wight strikes again → Dying 3, the top.
Key 2 is turned — but the player does not roll for death. The menu is offered: Captured (the wight
drags you into its barrow; you wake among the dead, gear on the altar) / Maimed (lose the arm the
cold touched) / Death's Bargain (the wight's master will spare you if you return the barrow-king's
stolen crown — cursed: *no warmth heals you* until done) / Rout (escape, but the wight follows you
to Cold Hollow: world clock "Barrow-Dead Walk" +2) / Spend a Reprieve (1 of 1 left) / Last Stand /
Gamble. The player chooses Death's Bargain. State: `condition: cursed(grave_cold)`, `vow:
return_crown (extreme)`, `dying: 0`, `wounded: 1`, `mark: frost-white streak in hair` (evidence:
`death.bargained`, `undead.survived`), `chronicle += "walked out of the Ninefold Barrow owing the
dead a crown"`.

---

## D. Retirement and legacy

### D.1 The problem, restated

The sandbox never ends on its own, so "finish" is a player-chosen retirement (BRIEF §4). A good
retirement procedure must (1) make ending feel like a *culmination* rather than quitting; (2)
convert the character into lasting **world state** so the world remembers; (3) let a **new
character inherit** the world, some of its advantages, and its unfinished business; and (4) serve
Principle VI — retirement is the project's largest-scale *structural* retirement of accumulated
content (slots, callings, tiers), with a clean restart of power for the successor.

### D.2 Mechanics catalog

**D-01 · Blades in the Dark — trauma retirement and stash tiers** (11, 07)
- *How it works.* The fourth trauma forces retirement (or taking the fall in prison for the crew's
  wanted level). What the character stashed determines the epilogue: 0–10 coin, the gutter; 11–20,
  a hovel; 21–39, a modest home or small business; 40, a fine home or medium business. Each full
  row of ten sets a lifestyle quality 0–4. Dead or retired characters are replaced by a new
  scoundrel — possibly a promoted gang member — who joins the same crew; the crew (tier, turf,
  claims, faction statuses) persists.
- *AI-DM fit.* `+` Deterministic epilogue from tracked state; the *crew* is the persistent
  protagonist that carries the world across characters. `−` Retirement is forced, not chosen.
- *Take.* An epilogue computed from tracked holdings; a persistent entity (the base, the order,
  the household) that outlives any single character.

**D-02 · King Arthur Pendragon — heirs, family, and inherited Glory** (11)
- *How it works.* Winter Phases produce marriage, children, and child survival rolls; a knight's
  eldest son (or chosen heir) is ready by the time the father ages out or dies. The heir inherits
  lands, family characteristics, and a fraction of the parent's **Glory** (10% in the
  long-standing 5th-edition rule; community discussion reports 6th edition raising it to make the
  parent's career matter more). The Great Pendragon Campaign expects several generations per
  player.
- *AI-DM fit.* `+` The canonical generational model; inheritance is computable. `−` Requires the
  family simulation to have run in the background.
- *Take.* A *fraction* of renown transfers, never all of it; lineage is a state object built up
  during play (spouse, children, wards, apprentices), so the successor already exists in the world.

**D-03 · The One Ring 2e — Raise an Heir** (11)
- *How it works.* During the long winter (Yule) Fellowship Phase, a hero can take the Raise an
  Heir undertaking, investing Treasure and Adventure Points into a named heir's starting
  experience; enough investment lets the heir start stronger and inherit heirlooms.
- *AI-DM fit.* `+` Succession is *prepared during play* by a deliberate downtime choice. `−` None.
- *Take.* A downtime activity "Train a Successor" that banks value for the next character.

**D-04 · Ironsworn / Starforged — legacy tracks and Continue a Legacy** (11, 04)
- *How it works.* Starforged tracks three **legacies** — Quests (vows fulfilled), Bonds
  (connections forged), Discoveries (expeditions completed) — as 10-box progress tracks that pay
  experience as they fill, then reset at a lower rate. When a character retires, dies, or is lost,
  the new character rolls **Continue a Legacy** against each of the old character's three tracks:
  a strong hit inherits something concrete (an asset or companion, a connection with its progress,
  a ship with modules); a weak hit inherits an *opportunity* (take up an unfinished vow with half its
  progress, rebuild a lapsed connection, revisit a meaningful place with progress marked); a miss
  inherits *trouble* (the predecessor's enemy has grown, you come to oppose their values, their
  discoveries had unintended consequences). Classic Ironsworn: the story ends, but the legacy
  doesn't.
- *AI-DM fit.* `+` The best inheritance procedure in the corpus: deterministic, three-channeled,
  and every outcome — even the bad one — is a hook. `−` None.
- *Take.* Adopt three legacy ledgers (Deeds, Bonds, Discoveries or setting-appropriate equivalents)
  and a per-ledger inheritance roll whose *bad* outcomes are hooks too.

**D-05 · Wildermyth — legacy tiers, retirement age, hooks** (11, 04)
- *How it works.* Heroes age in-campaign; passing retirement age retires them at the next interval
  with their gear (and a small Legacy Point bonus). After a campaign, chosen survivors or retirees
  are promoted a **legacy tier** — Folk Hero → Local Legend → Fabled Adventurer → Balladsung Hero →
  Mythwalker — and can be recruited into later campaigns for Legacy Points, retaining themes,
  maimed limbs, transformations, and a tier-scaled share of their abilities, but returning older.
  Resolving personal **hooks** grants retirement bonuses; fully transformed heroes get unique
  retirement endings (a statue in the village square; flying off among spirits).
- *AI-DM fit.* `+` Named, escalating *legend ranks* that are pure recognition — exactly the
  in-fiction voice for a retired character's renown. Unique endings per identity match Heart's
  Zenith. `−` Recruiting old heroes back as PCs undermines retirement's finality.
- *Take.* A retired character's legend rank is computed from their deeds; they may return as an
  **NPC** (mentor, patron, cameo), never as a playable PC at full power.

**D-06 · Heart: The City Beneath — Zenith abilities** (04, 11)
- *How it works.* A calling's final beat grants a Zenith ability: an overwhelming, one-time
  culmination that usually ends the character (death, transformation, departure). Choosing a
  Zenith beat signals the player wants the arc to end.
- *AI-DM fit.* `+` Retirement as a *climax the player chooses*. `−` Near-guaranteed death is too
  dark as the only route.
- *Take.* A top-tier calling crystallization can offer an **Apotheosis retirement**: a final,
  spectacular act that ends the career (not necessarily the life) and writes a legend.

**D-07 · Burning Wheel — emotional attributes at 10** (11, 04)
- *How it works.* Each stock's emotional attribute (human Faith, elven Grief, dwarven Greed, orcish
  Hatred) grows through play; at 10, the character leaves play in a stock-specific way (the elf
  sails into the West, the dwarf seals himself in with his hoard, the believer is taken up).
- *AI-DM fit.* `+` An *identity-driven* ending: the character doesn't die, they become too much of
  what they are. `−` Can be involuntary.
- *Take.* Callings may carry an **Apotheosis threshold**: at maximum depth, retirement becomes
  *available* (offered, never forced) as the identity's natural ending — the paladin's ascension,
  the necromancer's lichdom, the ranger's disappearance into the wood.

**D-08 · Ars Magica — aging, Final Twilight, troupe and covenant continuity** (11)
- *How it works.* Aging rolls begin after 35; magi drift toward Final Twilight; the saga lives
  in the covenant, which outlasts its members; troupe play rotates characters (magi, companions,
  shared grogs).
- *AI-DM fit.* `+` The institution as protagonist again (cf. Blades crew). `−` Troupe rotation is
  multi-player.
- *Take.* If the player built or joined an institution, it is the continuity carrier.

**D-09 · Legacy: Life Among the Ruins — families across ages** (11)
- *How it works.* Each player controls a **Family** playbook (stats like Reach, Grasp, Tech, Mood;
  Surpluses and Needs; traditions) as well as individual characters. Play alternates between
  zoomed-in character stories and zoomed-out family turns, and the campaign jumps forward between
  **ages**, with new characters from the same families.
- *AI-DM fit.* `+` A two-scale structure: a character's story ends; the family's continues. The
  age-jump is a world timeskip procedure. `−` Faction-scale play is heavy for solo.
- *Take.* Between characters, run N World Turns (a timeskip), then start the successor in the
  changed world.

**D-10 · Kingdom (Ben Robbins) — roles, crossroads, promotion of minor characters** (11)
- *How it works.* Players hold roles (Power, Perspective, Touchstone) within a community facing
  **Crossroads** (decisions that may change it forever). When a main character leaves or dies, a
  minor character is promoted to main.
- *AI-DM fit.* `+` "Promote someone already in the story" means the successor is pre-connected.
- *Take.* The successor-selection menu should favor NPCs the player already knows (apprentice,
  sibling, companion, rescued prisoner, rival's child).

**D-11 · Microscope — history as the product** (11)
- *How it works.* Players build a fractal history (periods → events → scenes), jumping around in
  time; the output is a coherent history.
- *AI-DM fit.* `+` A model for *legend-making*: at retirement, the character's life is summarized
  into a period with key events that become world lore.
- *Take.* The epilogue produces a short structured history (period + 3–5 events) appended to the
  chronicle.

**D-12 · Dwarf Fortress — retire vs. abandon; legends; revisiting** (11)
- *How it works.* A retired fortress lives on as an NPC settlement; an abandoned one becomes a
  ruin; a later adventurer can visit either and find what the old player left; Legends mode
  records it all.
- *Take.* The retiring character's holdings either **persist** (run by heirs/NPCs) or **fall**
  (become a site in the sandbox with a legend), per the epilogue.

**D-13 · Darkest Dungeon and Rogue Legacy — the persistent meta-structure** (11)
- *How it works.* *Darkest Dungeon*: heroes die or are dismissed; the hamlet's upgrades persist
  and new recruits arrive. *Rogue Legacy*: at death, choose one of three heirs, each with traits
  that trade upside for downside; gold spent on the manor persists, while unspent gold is taken at
  the gate (a portion can be banked with upgrades).
- *AI-DM fit.* `+` Heir choice among *three* with visible trait trade-offs is exactly P1's
  "layered variance with player choice." `−` Mortality-as-grind is the opposite of this project's
  telegraphed-death tone.
- *Take.* Successor generation offers **three candidates** with visible trade-offs; wealth that was
  *invested* (in holdings, the base, the successor) persists, while unspent coin mostly does not.

**D-14 · Dungeon World and the AD&D "name level" tradition** (11, 04)
- *How it works.* Dungeon World's level-10 advances include retiring to safety or taking an
  apprentice. AD&D's classes attract followers and found strongholds at "name level," shifting play
  toward domains; titles per level were in-world (Veteran, Swordsman, Hero... Lord).
- *Take.* A mature character may **transition** from adventurer to patron/domain-holder — a soft
  retirement where they become a quest-giving NPC in the successor's game.

**D-15 · Monsterhearts — season advances (switch character)** (11)
- *How it works.* At a season's end, a player may switch to a new character or a new playbook as
  the advance.
- *Take.* Offer a **retirement window** at natural seams (season boundaries, arc completions),
  in addition to "whenever the player asks."

### D.3 Recommended design space for Section D (chapter 11, with 04/07 hooks)

**D-R1. Triggers — retirement is always the player's choice, but the game offers it at seams.**
The player may retire at any reflection boundary. The game **offers** retirement (never forces it)
when: a calling reaches its apotheosis threshold (D-06/D-07); a personal aspiration or oath is
fulfilled (Wildermyth hooks); the character accumulates the maximum lasting marks/strain (C-R7,
D-01); the character reaches old age (Pendragon/Ars Magica aging); or the player completes a major
arc at a season boundary (D-15). Death (only via §C's Two-Key Rule) also triggers the legacy
procedure.

**D-R2. The Epilogue procedure `[D]` inputs, `[N]` output.**
1. *Choose the ending type:* Retire to a life (Blades stash tiers → lifestyle); Become a patron
   (D-14: they stay in the world as an NPC with their holdings); Apotheosis (D-06/D-07: the
   calling's authored ending); Depart (the road, the West, the sea); or, after death, Remembered.
2. *Compute the settlement* from tracked holdings: wealth invested, property, titles/ranks,
   faction statuses → lifestyle tier and what persists (Blades) and whether holdings **persist or
   fall** (Dwarf Fortress).
3. *Write the legend:* compute legend rank (Wildermyth: Folk Hero → ... → Mythwalker) from
   renown and deeds; write a Microscope-style period with 3–5 events into the chronicle; generate
   2–3 **rumors** about the character with truth values (so the legend is partly wrong, as legends
   are); set the retired character's epithet(s) as permanent world vocabulary.
4. *Close or bequeath threads:* each open vow/thread/story cycle is marked resolved,
   **bequeathed** (transferred to the successor with half its progress — Ironsworn weak hit), or
   **left to the world** (it advances on its own in the timeskip).
5. *Structural retirement (Principle VI):* the character's slots, callings, tiers, and active
   abilities are retired wholesale; only the inheritance channels below carry value forward.

**D-R3. The Timeskip.** Run N World Turns (e.g., one season to several years, chosen by the player
from a short list) so the world visibly moves on: faction clocks advance, linchpins may die, the
retired character's holdings develop or decay, their enemies grow (Ironsworn miss; Nemesis). This
is Legacy's age-jump and Pendragon's winter at scale.

**D-R4. Successor selection — three candidates, pre-connected.** Generate three successor
candidates, favoring people already in the story (apprentice, heir, companion, rescued prisoner,
rival's child — Kingdom/Pendragon/Blades promotion), each with a visible trade-off (Rogue Legacy),
plus the always-available option of a newcomer. Successors start at the P2 baseline floor —
**never** at the predecessor's power (retirement is a structural reset).

**D-R5. Inheritance channels (bounded).**
- *Renown:* a fraction of the predecessor's renown in communities connected to the successor
  (Pendragon's fraction; recommend 10–25%) — "you're the Lantern's apprentice."
- *One heirloom:* a single item (or bequeathed ability-bearing item, chapter 08) — never the whole
  kit (Rogue Legacy's gate tax; TOR heirlooms).
- *Legacy ledgers:* three per-ledger inheritance rolls (Ironsworn): Deeds → an unfinished vow with
  progress or a standing offer from an institution; Bonds → a relationship that starts warm;
  Discoveries → a known place, map, or secret. *Bad results inherit trouble* (a grown enemy, an
  owed debt, an institution that expects the successor to repay the predecessor's obligations).
- *Investment:* anything invested during play via "Train a Successor" (TOR Raise an Heir) adds
  bounded starting advantages (e.g., a head start in one tag tally — evidence, not a calling).
- *The predecessor as NPC:* the retired character persists as an NPC (mentor, patron, legend) with
  a fixed disposition toward the successor — and may be a V2 mentor for the successor's recognition
  (§A), closing the loop between the two halves of the game.

**D-R6. The chronicle is the true save file.** Every character's life, death, and retirement is
recorded; rumor tables and NPC dialogue can cite it; later characters can visit the ruins,
statues, and graves of earlier ones (Dwarf Fortress, Wildermyth's statue ending). This is how the
sandbox "finishes" meaningfully without ever ending: each character is a completed period in an
ongoing history.

**Worked example.** After two in-game years, "the Quiet Match" (hybrid smokewalker, tier 3) fulfils
the aspiration "burn out the Salt Guild's slave pens." At the next reflection boundary the game
offers retirement (arc completed at a seam); the player accepts and chooses *Become a patron*.
Settlement: 34 coin invested in the Ashwood charcoal camps → modest lifestyle; the camps
**persist** (run by the charcoal-burner mentor). Legend rank: Local Legend (renown 3 across the
caravan road and Ashwood). Chronicle: period "The Quiet Fires" with four events. Rumors generated:
"The Match can walk through a burning barn" (*partial* — she could, once, with Focus she no longer
has); "She's still out there, lighting the old pens" (*false*). Threads: "The Last Egg" (open,
40%) → bequeathed; "Salt Guild vengeance" → left to the world. Timeskip: the player chooses "one
year." Four World Turns run: the Guild (now Tier 1, weak hold after the pens burned) rebuilds
slowly; the wyrm cult hatches the last egg (thread progress for the bequeathed vow jumps to a
crisis). Successor candidates: (a) Tamsin, the freed pen-slave the Match rescued (+Bonds: starts
warm with the Caravaners' Compact; −: Guild bounty), (b) the charcoal-burner's nephew (+Discoveries:
knows the Ashwood's hidden paths; −: owes the Wardens a debt), (c) a newcomer. Legacy rolls: Deeds —
weak hit: take up "The Last Egg" at half progress; Bonds — strong hit: the caravan master's standing
offer transfers; Discoveries — miss: the cult now knows the Ashwood paths too. The player picks
Tamsin, who starts at the baseline floor with 10% of the Match's caravan-road renown ("the Match's
girl"), the Match's smoke-grey cloak as heirloom (a mundane-plus item), and the Match herself as
an NPC patron — who, sessions later, will be the one to notice when Tamsin starts carrying fire
quietly too.

---

## Sources

### A — Recognition, callings, reputation
- Burning Wheel trait vote and artha: https://writeups.letsyouandhimfight.com/hectorgrey/burning-wheel/ ; https://takeonrules.com/2022/03/01/trait-vote-sessions-in-burning-wheel/ ; http://endersquest.wikidot.com/artha
- Burning Wheel advancement (Routine/Difficult/Challenging): http://questingblog.com/wp-content/uploads/2015/02/Burning-Wheel-Procedural-Guide-2.2.pdf ; https://forums.burningwheel.com/t/advancing-skills-stats-attributes/13154
- Pendragon traits, checks, Winter Phase: https://www.mk-rpg.org.uk/Pendragon_winter_phase_summary ; https://boardgamegeek.com/wiki/page/Paraphrased_Pendragon_Rules ; http://www.thekeep.org/cgi/amber?action=browse&id=Pendragon%2FTraitsAndPassions&revision=10
- Pendragon chivalry/religious bonus, famous trait: https://basicroleplaying.org/topic/8448-pendragon-chivalry-bonus-requirement-80-or-96/ ; https://writeups.letsyouandhimfight.com/divinecoffeebinge/pendragon/
- Pendragon passions: https://boardgamegeek.com/wiki/page/Paraphrased_Pendragon_Rules ; https://www.chaosium.com/blogpendragon-design-journal-4-refining-traits-and-passions/
- Heart: The City Beneath beats and zeniths: https://diceexploder.com/posts/transcript-beats-heart-the-city-beneath-with-aaron-voigt ; http://www.diceexploder.com/blog/2025/4/8/zenith-abilities-heart-the-city-beneath-with-aaron-voigt ; https://writeups.letsyouandhimfight.com/lazyangel/heart-the-city-beneath/
- Masks labels and influence: https://en.wikipedia.org/wiki/Masks:_A_New_Generation ; https://1d6chan.miraheze.org/wiki/Masks:_A_New_Generation
- Monsterhearts conditions, growing up, seasons: https://writeups.letsyouandhimfight.com/feinne/monsterhearts-2e-and-second-skins/ ; https://www.strangeassembly.com/2018/review-monsterhearts-2
- Mouse Guard winter session, traits, conditions/twists: https://writeups.letsyouandhimfight.com/kestral/mouse-guard-rpg/ ; https://mythcreants.com/blog/why-mouse-guard-handles-failure-better-than-any-other-rpg/ ; https://islaythedragon.com/featured/its-what-you-fight-for-a-review-of-mouse-guard-roleplaying-game/
- The One Ring 2e callings and Shadow: https://cubicle7games.com/en_EU/blog/the-one-ring-the-shadow ; https://rpgbot.net/the-one-ring-2nd-edition-a-review/
- Avatar Legends balance, center, growth: https://cannibalhalflinggaming.com/2021/07/23/avatar-legends-quickstart-review/ ; https://magpiegames.com/blogs/news/5-tips-for-gming-avatar-legends-the-rpg
- Earthdawn disciplines, circles, spontaneous initiation: https://earthdawn.fandom.com/wiki/Disciplines ; https://pandagaminggrove.blogspot.com/2013/06/earthdawn-anatomy-of-discipline-25.html ; https://pandagaminggrove.blogspot.com/2012/12/earthdawn-anatomy-of-discipline-08.html
- Stormlight Ideals / Nahel bond / Recreance: https://coppermind.net/wiki/Knights_Radiant ; https://coppermind.net/wiki/Nahel_bond ; https://coppermind.net/wiki/Deadeye ; https://stormlightarchive.fandom.com/wiki/Immortal_Words
- BG3 Oathbreaker Knight: https://baldursgate3.wiki.fextralife.com/Oathbreaker_Knight ; https://www.thegamer.com/baldurs-gate-3-oathbreaker-paladin-redemption-guide/ ; https://www.dexerto.com/baldurs-gate/killing-one-baldurs-gate-3-paladin-will-all-but-break-your-game-2738709/
- Ultima IV virtues, Hawkwind, shrines: http://crpgaddict.blogspot.com/2010/06/ultima-iv-shrines-meditation-and.html ; https://www.filfre.net/2014/07/ultima-iv/ ; https://en.wikipedia.org/wiki/Ultima_IV:_Quest_of_the_Avatar
- Blades in the Dark XP triggers, advancement (SRD): https://github.com/amazingrando/blades-in-the-dark-srd-content/blob/main/Blades-in-the-Dark-SRD.md ; https://bladesinthedark.com/advancement
- Forbidden Lands reputation, XP questions, Pride: https://forbiddenlandsopentable.obsidianportal.com/wikis/skills ; https://forum.frialigan.se/viewtopic.php?t=6883 ; https://rpgbot.net/forbidden-lands-a-review/
- Ars Magica 5e reputations: https://www.redcap.org/page/Ars_Magica_5E_Standard_Edition,_Chapter_Three:_Characters ; https://writeups.letsyouandhimfight.com/mors-rattus/ars-magica-5th-edition/
- Mount & Blade renown and vassalage: https://mountandblade.fandom.com/wiki/Renown ; https://floris.fandom.com/wiki/Building_Your_Reputation ; https://strategywiki.org/wiki/Mount&Blade/Relations
- Fable titles and new-Fable reputation: https://fable.fandom.com/wiki/Chicken_Chaser ; https://www.gamespot.com/articles/new-fable-keeps-series-tradition-of-kicking-chickens-alive-and-youll-be-judged-for-it/1100-6537589/ ; https://80.lv/articles/new-fable-promises-true-open-world-reputation-reactions-from-npcs
- Saga bynames: https://journals.lub.lu.se/index.php/anf/article/viewFile/11525/10217 (Diana Whaley, "Nicknames and Narratives in the Sagas") ; https://runenym.com/guides/viking-naming-conventions
- Nemesis system: https://www.gamesradar.com/shadow-mordor-nemesis-system-amazing-how-works/ ; https://medium.com/@niklaseckstein/how-the-nemesis-system-creates-stories-d26754b30d2e
- AD&D druid and monk hierarchies: https://adnd2e.fandom.com/wiki/Druid_(PHB) ; http://www.mjyoung.net/dungeon/char/clas010.html ; http://mjyoung.net/dungeon/char/clas017.html
- Skyrim Greybeards summons: https://elderscrolls.fandom.com/wiki/Dragon_Rising ; https://en.uesp.net/wiki/Skyrim:Dragon_Shouts
- Oblivion leveling ("rest and meditate"): https://en.uesp.net/wiki/Oblivion:Leveling
- Kingdom Come skills, trainers, reading: https://kingdom-come-deliverance.fandom.com/wiki/Skills ; https://guides4gamers.com/kingdom-come-deliverance/articles/skill-trainers-and-books/
- Dragon's Dogma 2 hybrid vocations via maisters: https://dragonsdogma2.wiki.fextralife.com/Mystic_Spearhand ; https://dragonsdogma2.wiki.fextralife.com/Classes
- Wildermyth transformations, legacy, retirement: https://wildermyth.com/wiki/Legacy ; https://steamcommunity.com/app/763890/discussions/0/3949028823317388988/

### B — Living-world engines and pacing
- SWN/WWN factions: https://takeonrules.com/2018/12/27/lets-read-stars-without-number-factions/ ; https://princeofnothingblogs.wordpress.com/2019/05/13/review-stars-without-number-pt-vi-breakfast-of-champions/ ; https://d0ngiovanni.github.io/swn-faction-spreadsheet/ ; https://forum.rpg.net/index.php?threads/tell-me-about-faction-play-in-stars-worlds-without-number.879678/
- Blades faction game, clocks, heat, entanglements, downtime, harm, death, retirement (SRD): https://github.com/amazingrando/blades-in-the-dark-srd-content/blob/main/Blades-in-the-Dark-SRD.md
- Forbidden Lands legends, sites, strongholds: https://dramatistofmind.com/forbidden-lands-legends-and-adventures/ ; https://dramatistofmind.com/generating-adventure-site-in-forbidden-lands/ ; https://www.stuartellisgorman.com/blog/forbidden-lands-by-free-league-publishing-a-gms-review
- Ars Magica seasons, covenant lifecycle, aging, Twilight: https://publish.obsidian.md/ars-magica-definitive-manuscript/00+Chapters/Chapter+06+-+Covenants ; https://www.redcap.org/page/Season ; http://www.redcap.org/page/Aging ; https://thealexandrian.net/creations/ars-magica/ars-magica5-cheat-sheet-v1.pdf
- Pendragon Winter Phase / Great Pendragon Campaign: https://www.mk-rpg.org.uk/Pendragon_winter_phase_summary ; https://egag.fandom.com/wiki/The_Great_Pendragon_Campaign ; https://www.questportal.com/blog/mastering-the-winter-phase-in-pendragon
- Dwarf Fortress legends, retire/abandon/reclaim: https://dwarffortresswiki.org/index.php/DF2014:Legends ; https://dwarffortresswiki.org/index.php/Reclaim_fortress_mode ; https://en.wikipedia.org/wiki/Dwarf_Fortress
- Kenshi world states: https://kenshi.fandom.com/wiki/World_States ; https://kenshi.fandom.com/wiki/Town_Overrides
- RimWorld storytellers: https://rimworldwiki.com/wiki/AI_Storytellers ; https://rimworldwiki.com/wiki/Cassandra_Classic ; https://rimworldwiki.com/wiki/Phoebe_Chillax
- Left 4 Dead AI Director: https://left4dead.fandom.com/wiki/The_Director ; https://en.wikipedia.org/wiki/Left_4_Dead
- The Alexandrian: https://thealexandrian.net/wordpress/4154/roleplaying-games/dont-prep-plots-prepping-scenario-timelines ; https://thealexandrian.net/wordpress/42961/roleplaying-games/smart-prep-part-4-campaign-status-documents ; https://thealexandrian.net/wordpress/36768/roleplaying-games/the-art-of-pacing-prepping-bangs ; https://thealexandrian.net/wordpress/7985/roleplaying-games/node-based-scenario-design-part-3-inverting-the-three-clue-rule ; https://thealexandrian.net/wordpress/8122/roleplaying-games/node-based-scenario-design-collectors-edition ; https://thealexandrian.net/wordpress/17308/roleplaying-games/hexcrawl ; https://thealexandrian.net/wordpress/17464/roleplaying-games/hexcrawl-part-12-at-the-table
- Overloaded encounter die / Hazard System: https://necropraxis.com/2014/02/03/overloading-the-encounter-die/ ; https://necropraxis.com/2014/12/23/hazard-system-v0-2/ ; https://www.prismaticwasteland.com/blog/overloading-the-random-encounter-table
- Ben Milton / Knave procedures: https://questingbeast.substack.com/p/the-glatisant-issue-45 ; https://www.prismaticwasteland.com/blog/hexcrawl-checklist-part-one
- West Marches: https://arsludi.lamemage.com/index.php/78/grand-experiments-west-marches/ ; https://www.domainofmanythings.com/blog/west-marches
- Mythic GME 2e: https://matthewsantacruz.substack.com/p/how-i-use-the-mythic-gm-emulator ; https://www.gamingtavern.uk/index.php?threads/review-mythic-game-master-emulator-2nd-edition.8422/
- Crusader Kings III events: https://ck3.paradoxwikis.com/Event_modding ; https://forum.paradoxplaza.com/forum/developer-diary/crusader-kings-3-dev-diary-30-event-scripting.1397140/
- Façade drama manager: https://cdn.aaai.org/AIIDE/2005/AIIDE05-016.pdf ; https://faculty.cc.gatech.edu/~isbell/reading/papers/MateasSternGDC03.pdf
- Valve dynamic dialog: https://www.gdcvault.com/play/1015528/AI-driven-Dynamic-Dialog-through ; https://emshort.blog/2012/03/16/gdc-2012-talk-on-dynamic-dialogue/
- Hades narrative design: https://www.gdcvault.com/play/1026975/Breathing-Life-into-Greek-Myth ; https://www.gamedeveloper.com/design/how-supergiant-weaves-narrative-rewards-into-i-hades-i-cycle-of-perpetual-death
- The Simulation Dream: https://tynansylvester.com/2013/06/the-simulation-dream/

### C — Telegraphed death and defeat
- D&D 5e death saves (SRD 5.1/5.2): https://www.dndbeyond.com/srd
- Pathfinder 2e dying/wounded/doomed: https://2e.aonprd.com/Rules.aspx?ID=2319 ; Hero Points: https://2e.aonprd.com/Rules.aspx
- Blades harm, resistance, death, trauma (SRD): https://github.com/amazingrando/blades-in-the-dark-srd-content/blob/main/Blades-in-the-Dark-SRD.md
- Ironsworn Endure Harm table and Face Death: https://ironsworn-rpg.fandom.com/wiki/Endure_Harm_Consequences_Table ; https://ironsworn-rpg.fandom.com/wiki/Moves ; Starforged legacy moves: https://rsek.github.io/starforged-srd/moves/legacy
- Dungeon World Last Breath and Face Death menu: https://roll20.net/compendium/dw/Last%20Breath ; https://www.dungeon-world.com/not-the-end-face-death/
- Cairn damage, critical damage, scars, Warden principles: https://cairnrpg.com/second-edition/wardens-guide/combat/ ; https://cairnrpg.com/second-edition/players-guide/overview-and-principles/ ; https://cairnrpg.com/first-edition/cairn-srd/
- Mausritter: https://mausritter.com/srd/how-to-play/ ; https://josef-adamcik.cz/ttrpg/low-lethality-in-mousritter.html
- Mörk Borg Broken table: https://kindofold.substack.com/p/mork-borg-now-with-permanent-damage ; https://www.blackweller.ca/Morkborg_Delethalizer/
- Torchbearer death doors: https://sites.google.com/view/torchbearerwiki/faq ; https://sites.google.com/site/torchbearertheland/home/conflicts
- Fate Core conceding: https://fate-srd.com/fate-core/conceding-conflict ; https://fate-srd.com/fate-core/ending-conflict
- 13th Age fleeing / campaign loss: https://www.13thagesrd.com/combat-rules/ ; https://walkingmind.evilhat.com/2013/09/03/13th-age-running-the-game/
- WFRP 4e Fate/Fortune: https://www.kalevalahammer.com/2018/07/wfrp4-preview-fate-and-fortune.html ; https://www.enworld.org/threads/heres-how-wfrp4-will-handle-fate-and-fortune-resilience-and-resolve.665556/
- Darkest Dungeon Death's Door: https://darkestdungeon.wiki.gg/wiki/Death's_Door_(Darkest_Dungeon)
- XCOM bleeding out: https://xcom.fandom.com/wiki/Bleeding_out ; https://www.ufopaedia.org/index.php/Critical_Wounds_(EU2012)
- Apocalypse World MC moves: https://writeups.letsyouandhimfight.com/evil-mastermind/apocalypse-world/ ; https://thealexandrian.net/wordpress/9584/roleplaying-games/apocalypse-world
- McDowall (ICI; difficulty): https://www.bastionland.com/2020/03/difficulty-in-bastionland.html ; https://www.bastionland.com/2020/08/small-decisions-big-impact.html
- Mount & Blade capture: https://mountandblade.fandom.com/wiki/Prisoners
- Kenshi defeat/knockout norms: https://tvtropes.org/pmwiki/pmwiki.php/VideoGame/Kenshi

### D — Retirement and legacy
- Blades stash and retirement (SRD, above).
- Pendragon heirs and inherited Glory: https://basicroleplaying.org/topic/23767-glory-in-the-new-edition-of-pendragon/ ; http://rlyehreviews.blogspot.com/2019/10/review-1000-king-arthur-pendragon.html
- The One Ring 2e Raise an Heir: https://notes.nicolevanderhoeven.com/The+One+Ring+2e+Cheat+Sheet ; https://forum.frialigan.se/viewtopic.php?t=8255
- Ironsworn / Starforged legacies (above).
- Wildermyth legacy (above).
- Burning Wheel emotional attributes: https://forum.rpg.net/threads/burning-wheel-tell-mme-all-about-emotional-attributes.551339/ ; https://tvtropes.org/pmwiki/pmwiki.php/TabletopGame/BurningWheel
- Ars Magica troupe/covenant: https://www.redcap.org/page/Ars_Magica ; https://rpgmuseum.fandom.com/wiki/Troupe
- Legacy: Life Among the Ruins: https://www.ageofravensgames.com/blog/legacy-system-guide-for-new-players ; https://gnomestew.com/the-indie-game-shelf-legacy-life-among-the-ruins-second-edition/
- Kingdom: https://www.lamemage.com/kingdom/ ; https://gnomestew.com/kingdom-2nd-edition-review/
- Microscope: https://en.wikipedia.org/wiki/Microscope_(role-playing_game) ; https://www.rpg.net/reviews/archive/15/15181.phtml
- Rogue Legacy heirs and Charon: https://roguelegacy.wiki.gg/wiki/Charon ; https://rogue-legacy-2.fandom.com/wiki/Traits
- Dwarf Fortress (above).

### Caveats on sourcing
- Mechanics are paraphrased from SRDs, official wikis, reviews, and designer posts; where numbers
  come from secondary sources they are marked approximate (RimWorld cycle lengths, XCOM Will loss,
  Pendragon's inherited-Glory fraction by edition). None of the recommendations depends on the
  exact value of an approximate number.
- The Blades in the Dark SRD was read in full for the harm, clock, faction, downtime, and
  retirement sections (CC-BY 3.0 source); those numbers are exact.
