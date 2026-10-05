# 02 — Character

> This chapter governs how a character comes to exist: the conversation that makes one, the three
> origins it is assembled from (a people, an upbringing, a livelihood), its seven attributes, the
> trainings and tongues it starts with, the two rolls the engine makes for it at birth and the one it
> offers later, its starting Vitality, Focus and fate, its kit, and the ties (a drive, bonds,
> aspirations, one true thing, a faction tie) that hand the living world something to pull on. It is
> shaped by two facts about this game. First, there are no levels and no chosen callings: who a
> character *becomes* is decided by what they do in play (constitution P2, P5), so creation lays
> foundations (capability, texture, hooks) and never an identity. Second, the first person to play
> this is a newcomer talking to an AI: so every choice in creation has a recorded default, the whole
> procedure can be finished in five answers, the full depth is always one word away, and nothing chosen
> in the first ten minutes can turn out to be a trap.

**Reading this chapter.** Standard format (00.19). Rules are 02.1–02.11. Canonical data:
`data/origins.yaml` (8 peoples, 9 upbringings, 21 livelihoods, the breadth profiles, creation defaults,
the random tables), `data/gen_birth.yaml` (the `gen.birth` generator domain: 117 pool entries),
`data/kits.yaml` (30 kits), and three fragments: `data/licenses.yaml owner-block 02` (tongues, letters,
people gifts), `data/effects.yaml owner-block 02` (one effect), `data/boundaries.yaml owner-block 02` (three
handlers). All were generated and validated by one script from authored tables (scratchpad
`ch02/gen02.py`, `gen_contrib02.py`, `draws02.py`), so every id in them exists in `tags.yaml`,
`licenses.yaml` or `abilities.yaml`, every budget adds up, and every number in the Tables and Worked
examples below was computed, not estimated. The continuous character **Wren** (00's WE-00-1…9) is made
end to end in WE-02-1, so that her sheet in 00 is now a derived result.

---

## Design intent

**Goals served.** Goal 1 (the player feels free to try any creative idea): any classic-fantasy concept
can be stated in a sentence and built, every one of chapter 04's twenty-five iconic archetypes is
pursuable from the first scene (T-02-12), and a concept the lists do not name is still buildable
(02.2.4, Edge cases). Goal 2 (the AI responds correctly): creation is a sequence of closed choices with
recorded defaults; the engine places every number; the DM's only judgments are five small
classifications, each with a stated worst case, each shown to the player before anything is locked.

**What creation is for, in one paragraph.** A character leaves creation with four things. *Capability*:
attributes, the floor, a handful of training licenses, perhaps one technique. *Texture*: a knack and a
quirk nobody chose, tongues, a kit with ids. *Direction*: a drive, an aspiration, and the Leanings view
(04.6.5) already showing where the player says they are headed. *Entanglement*: named people who care
or hold a grudge, a faction that knows them, and five to seven hooks the world will pull. It leaves
without a calling, a tier, a calling-partition ability, or a single point of evidence. Those are earned
[C:P2; C:P5; R3 02.3, 02.4].

**The four structural decisions.**
1. **Three origins, taken one of each** (people × upbringing × livelihood): the shape of Blades in the
   Dark's heritage + background + playbook and of Pathfinder's and 5e's ancestry + background + a
   chosen role, with the third slot holding a *past* in place of the chosen role, because that role is
   not chosen here [R: https://bladesinthedark.com/character-creation; R1 M-30; DL-02-22].
2. **Attributes are placed from fixed arrays, never bought.** Mistborn Adventure Game's
   strong / average / weak ranking and Ironsworn's 3-2-2-1-1 array are the precedents: nothing is
   priced, so nothing can be arbitraged, which is how P11 is satisfied without an audit of costs
   [R2 02; R: https://en.wikipedia.org/wiki/Ironsworn; C:P11; DL-02-03].
3. **P4's two trade-offs are two separate dials.** *Quantity against freedom* is the people's attribute
   rule: a people's Typical rule gives two more attribute points and decides three of the seven
   placements; the Free rule gives fewer points and decides nothing (02.3.2). *Breadth against
   competence* is the breadth profile: the more trainings a character takes, the fewer are held above
   the floor, and the broadest profile holds none above it (02.5.2). Neither dial can be turned after
   the creation window closes [C:P4; R2 #10; DL-02-04; DL-02-07].
4. **P1's variance is one generator domain used at two moments.** At creation the engine draws a knack
   and a quirk from a pool the origins gate; that draw is applied, because P1 makes variance at creation
   mandatory. After creation it draws the **Bent**, +1 to one attribute, from the attributes the
   character's own resolved deeds have exercised; that draw is an offer the player may accept or defer,
   gambling on a later one, because P1 forbids auto-applying variance after creation [C:P1; 00.11;
   00.4.3 a; DL-02-08; DL-02-11].

**What this chapter deliberately avoids.**
- *A shared point pool of any kind.* No attribute points, no flaw-for-points trades, no build currency.
  Every choice is one option from a closed bracket [C:P11; R1 02 "point-buy is the riskiest
  customization mechanic"; R2 02: flaws taken for points "get gamed"].
- *An origin that is a calling in disguise.* No origin grants a calling, a tier, a calling-partition
  ability, a competence above +2, or evidence [04 Interface request; 05 Interface request; DL-02-14].
- *Trap options and taxes.* Every people is the best choice for some concepts and a poor one for others
  (T-02-3); no option is one a competent player would always or never take [R1 02 "ability tax";
  R1 #13]. A newcomer who takes every default gets a sturdy, legal, useful character (WE-02-2).
- *Front-loaded reading.* The player is never shown a list longer than seven without asking for it, and
  never needs a rule explained before play begins [R1 02 "decision paralysis"; R5 §4 items 1, 5, 6].
- *Flavor-only drawbacks.* Every drawback in this chapter is a number in state (a forced −1, a lower
  Focus, a missing license, an NPC at Unfriendly), so the engine applies it without anyone remembering
  to [R1 02: a flaw that is only flavor is "a canary"].
- *Gear as power.* A kit gives access and utility: no item above `fine`, nothing magical, at most light
  armor [R1 02 "gear must not outclass innate abilities"; 02.8.2].

**Runtime capabilities assumed.** RC-STORE (the character record and every creation write), RC-RNG
(birth draws, the random tables), RC-DATA (the data files above, validated on load), RC-QUERY (tag
ancestry for pool gates and competence), RC-SCHED (the three handlers), RC-LOG (the creation log and
the prologue lines), RC-SEAL (nothing in this chapter is sealed; the chapter relies on 03's sealing of
tallies). No capability is assumed that 00.14.1 does not list.

---

## Rules

Rule ids are `02.S.R`. Kinds follow 00.2.2. Rules with a `[J:*]` decision use the 00.2.5 template in
full; `[D]`, `[T]` and `[N]` rules are written as cards that stand alone (SG-26). "The player" is the
person; "the character" or "the PC" is who they play.

### 02.1 The character at creation

**02.1.1 What creation produces.** `[D]` Creation ends with one `Character` entity (00.6.2) whose fields
hold exactly what this table lists, each written by a typed tool call with reason `creation`. Nothing
else about the character exists until play writes it.

| Field (00.6.2) | Value at the end of creation | Set by |
|---|---|---|
| `kind`, `name`, `tags` | `pc`; the chosen name; the people's `creature.folk.*` tag | 02.9.6, 02.4.2 |
| `attributes` | seven values, each −1…+3, summing to **+5** (Free rule) or **+7** (Typical rule) | 02.3 |
| `competence` | the floor `{tag: deed, value: 1, source: floor}` plus one entry of **+2** per training held deep | 02.5.1–02.5.3 |
| `licenses` | the fifteen basic verbs and `lic.focus.push` (held by all, 00.12.5, 05.6.7); tongues at their grades; `lic.lang.letters` if granted; one people gift if the people has one; the training licenses picked, each at grade `trained` | 02.4, 02.5 |
| `slots.acquired` | empty, or exactly one technique at rank 1 (`source.kind: gift`, provisional per 05.2) | 02.5.4, 02.6.3 |
| `slots.calling`, `slots.equipped`, `callings` | empty | 02.1.3 |
| `vitality` | `{current = max = 12 + Endurance}` | 02.7.1 |
| `focus` | `{current = max = base}`, base 3, 4 or 5 from the upbringing | 02.7.2 |
| `fate` | `{current: 1, max: 3}` | 02.7.3 |
| `harm_state`, `wounds`, `marks`, `conditions`, dread | `active`; none; none; none; 0 | 02.7.3 |
| `possessions` | the two kits' items, each an entity with an id; coin | 02.8 |
| `location` | chapter 13's opening place | 13 |
| `relationships` | one or two bonds; zero to two faction ties | 02.9.2, 02.9.5 |
| `commitments` | the long vow or the creed; any debt a bond or hook carries | 02.9.1 |
| `aspirations` | one to three `{text, tags}` | 02.9.3 |
| effect instances | the knack; the quirk; a people gift's effect | 02.6.2, 02.4.2 |
| facts | `pc.origin.people`, `.upbringing`, `.livelihood`, `.rule` (typical or free); `pc.true_thing` if stated; the facts a magic livelihood writes | 02.4.7, 02.9.4, 02.5.5 |
| meta `pc.creation` | path taken, every choice and whether it was a default, the birth results, open slots, window state, Bent state | 02.2.6, 02.6 |
| tallies, evidence ledger, reputation | empty | 02.11.1 |

**02.1.2 The order of creation.** `[D]` Creation is ten steps, always in this order, because each step's
options depend only on earlier ones. A path (02.2) changes how many of them the player is *asked*
about, never which are *done*.

| Step | What is decided | Rule | Fast path asks? |
|---|---|---|---|
| C0 | Preferences and safety (session zero) | 02.10 | yes, briefly |
| C1 | Concept and **livelihood** | 02.2.4, 02.4.5 | **yes** |
| C2 | **People**, and its rule (Typical or Free) | 02.4.2, 02.3.2 | only if the player raises it |
| C3 | **Upbringing** | 02.4.4 | no (the livelihood's default) |
| C4 | **Attributes**: shape and placement | 02.3 | no (02.3.5) |
| C5 | **Trainings**: profile, picks, technique, learning picks | 02.5 | no (the livelihood's defaults) |
| C6 | **Birth**: the engine's draw | 02.6 | no (rolled; told) |
| C7 | **Starting numbers** and **kit** | 02.7, 02.8 | no |
| C8 | **Ties**: drive, bonds, aspiration, the one true thing, faction tie | 02.9 | **yes**: the drive and one bond |
| C9 | **Name and look**; the sheet; confirm | 02.9.6, PR-02-6 | **yes**: the name |

**02.1.3 What creation never grants.** `[D]` No path, origin, default, pregen or successor rule grants
any of the following; a data entry that would is invalid (PR-02-9):
(a) a calling or a tier; (b) an ability in the calling partition; (c) more than one ability in the
acquired partition, or any above rank 1; (d) a competence entry above +2 or at any tag other than a
level-2 deed tag (the floor at `deed` excepted); (e) a training license above grade `trained`; (f) an
attribute outside −1…+3 or a sum outside +5…+7; (g) evidence, tallies, reputation or a rank in an
institution; (h) Vitality outside 11–15, Focus outside 3–5, fate other than 1; (i) an item that
02.8.2 forbids; (j) a fact about the world beyond the character's own person, ties and past.
[C:P2; C:P5; C:VII; 00.3.6; 00.4.3; 04 and 05 Interface requests; DL-02-14]

**02.1.4 Who decides what.** `[D]` In creation, as everywhere (00.14.3; INV-3; INV-4):
- the **player** chooses among options and states names, sentences and preferences;
- the **engine** places numbers, validates every choice against `data/origins.yaml`, and makes every
  random draw (`generate` for birth; `roll_table` for "surprise me");
- the **DM** asks, shows the options and the default, classifies free text into closed sets (five
  `[J:*]` decisions: 02.2.4 concept, 02.6.4 manner of childhood, 02.9.1 drive kind, 02.9.3 aspiration
  tags, 02.9.4 the one true thing), and records. The DM never picks an option the player was not shown,
  never picks "at random", and never supplies a number.

### 02.2 Paths

**02.2.1 Three paths, one procedure.** `[D]` There is one creation procedure (02.1.2) and three ways
through it. The player picks one at the start and may switch at any step.

| Path | The player answers | Everything else | Typical length | Procedure |
|---|---|---|---|---|
| **Fast** | five things: taste and limits; who you are; what you want; who matters; your name | recorded defaults (02.2.2) | 5 exchanges | PR-02-2 |
| **Full** | every step C0–C9 | nothing is defaulted unless the player says "you choose" | 12–20 exchanges | PR-02-1 |
| **Ready-made** | which pregenerated character; optionally a new name | the pregen's record; the birth draw is still made live | 2 exchanges | PR-02-3 |

The fast path is the default the DM offers first to a new player. It is a sequencing of the same rules:
a fast-path character is legal under every rule of the full path, and a character built on the full
path that happened to choose every default is the same character [BRIEF A3 "fast paths are legitimate";
R1 #14, M-31 (Baldur's Gate 3 offers a premade Origin beside a fully custom character);
R: https://bg3.wiki/wiki/Character_creation; R5 §4 item 6; Worlds/Stars Without Number backgrounds
list "quick skills" beside the full tables, R: https://takeonrules.com/2018/07/09/lets-read-stars-without-number-character-creation/;
DL-02-01].

**02.2.2 Every choice has a default.** `[D]` For each choice in creation, `data/origins.yaml` records a
default (`creation_defaults`, and each livelihood's `defaults`). When the player does not choose (says
"you choose", "whatever is normal", "skip", or simply answers the next question), the engine applies
the default and records `default: true` for that choice. The DM always names the default before it is
taken ("If you move on without choosing: …", 12.15.6), so a default is never a hidden decision.

| Choice | Default |
|---|---|
| livelihood | Soldier (`orig.life.soldier`) |
| people; rule | Human; a non-human people takes its Typical rule |
| upbringing | the livelihood's `defaults.upbringing` |
| attribute shape; placement | Peaked; the livelihood's `attribute_priority` applied by 02.3.5 |
| breadth profile; picks; technique | the livelihood's `defaults` |
| the human's extra training | the first tag on the livelihood's list that no pick has taken |
| an upbringing's license choice | the first on its list not already held |
| a tongue to pick | chapter 13's `second_tongue` for the region; without one, Dwarvish |
| learning picks, in order | Letters; then Common to its next grade; then the second tongue; then the Old Tongue |
| manner of childhood | `unremarked` (or `hard` for Bound service; `gifted` for Touched) |
| kit choice | the first option |
| drive | the livelihood's first `drive_seeds` line |
| anchor bond | the upbringing's first `bond_seeds` line |
| thorn bond, the one true thing, faction tie | **open** (02.9.8) |
| aspiration | the one the drive answer names, if it names one; otherwise **open** (02.9.8) |
| name; look | rolled on chapter 13's name table for the people; left to narration |
| pacing profile; pillar weights | `standard`; all `same` (12.7.3, 12.5.9) |

**"Surprise me."** If the player asks for chance to decide a people, an upbringing or a livelihood, the
engine rolls `tbl.creation.people`, `tbl.creation.upbringing` or `tbl.creation.livelihood` (T-02-13;
`roll_table`). For an attribute placement it draws uniformly among the legal placements of the Peaked
shape. The result is shown as an offer the player may accept or decline once; a declined result is
replaced by the default, not by a second roll (so chance is a choice, not a slot machine) [R4 SG-12;
Cairn and Mausritter roll attributes and then allow one swap: R: https://cairnrpg.com/second-edition/players-guide/character-creation/].

**02.2.3 Depth on request.** `[D]` At every step the player may say any of these, in any words; the DM
answers out of fiction at once and it costs nothing:

| The player says | The DM does |
|---|---|
| **"details"** (or "show me", "what are my options") | shows the step's complete option list from data, seven at a time, each with its one-line trade-off |
| **"why"** | states the trade-off of the option or the default in one or two sentences, with the numbers ("Cloister-raised: Focus 5 instead of 4, and you can read. You give up a second tongue and a trade license.") |
| **"you choose"** | applies the default (02.2.2) after naming it |
| **"surprise me"** | rolls (02.2.2) |
| **"back"** | returns to any earlier step; later steps keep their answers where still legal, and are re-defaulted where not |
| **"full"** / **"fast"** / **"ready-made"** | switches path from this step on |
| **"sheet"** | shows the character so far (PR-02-6) |
| **"just start"** | applies every remaining default and goes to C9 |

No explanation is given that was not asked for, except the three one-line first-use notes PR-02-7 lists
[R5 §4 item 5 "progressive disclosure"; R1 02 "crunch is exposed on demand, never forced"].

**02.2.4 Classifying a described concept.**

```
### 02.2.4  From a sentence to three origins                          [J:enum] [D]
Trigger [T]:        at C1 the player describes a character in their own words instead of picking
                    from the list ("an old soldier who wants to open an inn", "a thief with a
                    conscience", "someone who talks to ghosts")
Loads in:           creation (before any situation exists)
License check:      none (out of fiction)
Decisions (J):      1. BRANCH [J:enum] "What has this person mostly spent their life DOING?" One of
                       the nine deed branches (00.5.2 definitions and distinguishing tests), or
                       "no trade at all". Classify by the verbs in the sentence, not by its
                       adjectives. Uncertain between two -> keep both.
                    2. LIVELIHOOD [J:enum] within the branch's list in
                       origins.yaml#concept_branches (1 to 4 entries per branch):
                       martial: Soldier (fought for pay or duty) | Rider (served on horseback) |
                         Laborer (lived by strength, not arms) | Watchman (kept order)
                       guile: Thief (took things) | Charlatan (fooled people)
                       wilds: Hunter | Herder | Sailor | Wanderer (no fixed work)
                       lore: Scholar (books) | Healer (bodies) | Watchman (cases)
                       arcane: Apprentice    divine: Acolyte
                       primal: Hedge-taught (was taught) | Touched (was born with it)
                       influence: Merchant (goods) | Performer (audiences) | Courtier (the powerful)
                       craft: Artisan (one craft) | Tinker (mixtures and mechanisms) | Laborer
                       "no trade at all" -> Wanderer.
                       Default when uncertain: do not choose; offer the two nearest.
                    3. PEOPLE and UPBRINGING [J:flag each] "Does the sentence NAME one?" True only
                       when a people ("a dwarf") or a place of raising ("grew up on the docks") is
                       stated. False -> the default (02.2.2). Never infer a people from a name or
                       a manner.
Computation [D]:    the engine looks up the chosen entries and their defaults. Everything in the
                    sentence that is not an origin (the inn, the conscience, the ghosts) is kept
                    verbatim as material for C8: a want becomes the drive, a relationship a bond,
                    a singular fact the one true thing. A capability the sentence claims and no
                    origin grants ("talks to ghosts") is checked against licenses: if a livelihood
                    grants it (Touched or Hedge-taught, school spirits), that is offered; if none
                    does, it becomes an aspiration and the DM says so (02.9.4 handles the wording).
Stakes:             none (nothing is rolled)
State writes:       none until the player confirms the offer; then pc.origin.* (02.4.7)
Narration may not imply: that the classification is final, or any capability not granted
Worst case (J):     the wrong livelihood is OFFERED; the player sees its name and one-line gloss
                    and says no (class ii). Nothing is locked before C9, and the creation window
                    (02.2.6) allows one revision after play begins (class iv).
Examples:           inside: "an old soldier who wants to open an inn" -> martial -> Soldier; the inn
                      is the drive.
                    boundary: "a caravan guard who also cooks" -> martial (guarding is the work);
                      cookery is an off-list access pick or the village upbringing's craft.
                    boundary: "a physician who solves murders" -> lore -> Healer or Watchman are
                      both true -> offer both: "Healer (bodies) or Watchman (cases)?"
                    outside: "a prince in exile" -> names a place of raising (court), no work ->
                      Court-raised + "no trade at all" would be Wanderer, but the DM offers
                      Courtier and Rider as the nearer lives and lets the player say.
                    non-example: "the best swordsman in the kingdom" -> a livelihood (Soldier)
                      and an ASPIRATION ("to be the best blade in the kingdom", tags
                      deed.martial.blade). The claim itself is an assertion (SG-06): creation
                      grants +2, not a reputation.
Anchor:             no (creation only)
Basis:              [R5 §4 item 6: Cypher's "I am an adjective noun who verbs"] [R1 #14] [R4 §3.2 S1
                    closed-set classification is the AI's reliable form] [00.5.2] [SG-06] [DL-02-21]
```

**02.2.5 Ready-made characters.** `[D]` A pregenerated character is a complete creation record with
every choice of C1–C5 and C7–C8 already made, authored by chapter 13 for its region and stored as
data. It is produced by PR-02-1 and must pass PR-02-9 like any character; it differs from a character
the player built only in who chose. Three things are **not** fixed in a pregen:
(a) the **birth draw** (C6) is made live when the player picks the pregen, so two players who pick the
same one still diverge (P1); (b) the **name** may be changed; (c) the **creation window** (02.2.6)
applies, so the player may revise it once after trying it. A pregen's bonds, faction tie and hooks
point at entities of chapter 13's region by id. Chapter 13 authors at least four, covering among them a
fighter, a sneak, a talker or scholar, and a worker of magic, and at least one non-human
[R5 CC-12; R5 §4 item 1 (starter sets use pregens so the first session starts in minutes); DL-02-01].

**02.2.6 The creation window, the second look, and the lock.** `[D]` + `[T]`
- **The window.** When C9 completes, `pc.creation.window = open`. It closes at the **first `reflection`
  boundary** the character reaches (in practice, the first completed long rest): handler
  `h.02.creation_lock` (`reflection`, phase 9) sets `pc.creation.window = locked` and writes the fact
  `pc.creation.locked`.
- **The second look.** While the window is open, **once**, between scenes and never during a conflict
  or an open OFFER, the player may revise what was chosen *within* their origins: the attribute shape
  and placement; Typical or Free (02.3.4); the breadth profile, its picks and the technique; the
  upbringing's license choice; tongues and learning picks; kit choices; drive, bonds, aspirations, the
  one true thing and faction tie. The revision is one out-of-fiction exchange (PR-02-8), validated like
  creation.
- **What the second look cannot change.** The three origins themselves, once the first scene has been
  framed (people and past are facts that narration and NPCs have already relied on); the birth results
  (a draw is never re-made by revising, and since the origins are fixed its pool gate cannot change);
  any resolved frame; anything spent, lost, sold or given away. Kit items are re-issued only if
  untouched.
- **The lock.** After the window closes, every creation choice is permanent: this is P4's "locked at
  creation". From then on attributes change only as 00.4.3 allows (the Bent, 02.6.5; one +1 at a
  confirmed tier 4, 04; a maim, 07); trainings are added only by chapter 05's acquisition paths; a
  training is exchanged only by chapter 15's Retrain activity; origins never change.
*Why a window at all.* A newcomer cannot judge a placement they have never rolled. Baldur's Gate 3 lets
a player rebuild at camp for a token fee; here the same kindness is given once and then withdrawn, so
that P4's trade-offs are real for the rest of the character's life
[R: https://game8.co/games/BG3/archives/421001; R1 02 "what you choose at the start can make the
difference between a great game and a rage quit"; C:P4; DL-02-15].

**02.2.7 Successors.** `[D]` When a character is retired or dies and the player takes up a successor
(chapter 11's legacy procedure; R6 D-R4, D-R5), the successor is created by this chapter's procedure
with these differences and no others:
1. **The floor, and nothing of the predecessor's power.** The successor starts unrecognized, with the
   floor, origin trainings at +2 at most, an empty calling partition and fate 1. No attribute, license,
   competence, ability, calling, tier, Focus or Vitality of the predecessor passes on [C:VI; R6 D-R2
   step 5; 04.11.4].
2. **Known candidates constrain origins.** If the successor is someone already in the world (11 offers
   three candidates), their recorded people, home and work fix the matching origins (`[J:flag]`: is it
   recorded? true only when a fact holds it); the player chooses whatever is not recorded.
3. **Inheritance arrives as ties and things, through chapter 11:** a share of renown (11's state); one
   heirloom added to the kit (it is 11's and 08's item, so 02.8.2's kit limits do not bind it); legacy
   results as hooks and bonds, of which the predecessor, if alive, may be the anchor bond (mentor,
   standing +1).
4. **Trained successors.** If the predecessor completed chapter 11's Train-a-Successor activity in
   play, the successor's creation writes chapter 03's backstory events (03.2.8) for the tags that
   activity names: at most three tags, 24 points each. This is the only use of backstory evidence in
   the game, and it is allowed because that training was a deed done in play (02.11.1).
5. **A fresh birth draw**, with the generator's recency rule halving the predecessor's knack and quirk
   (`recency_window: 5`), so heirs differ from those they follow.
6. The creation window applies; the Bent starts unoffered.
[R6 §D.3; DL-02-20]

### 02.3 Attributes

**02.3.1 Arrays, not points.** `[D]` A character's seven attribute modifiers (00.4.1: Might, Agility,
Endurance, Wits, Intellect, Presence, Resolve) are one of six fixed **arrays** of seven values, each
value placed on one attribute. Nothing is bought, traded or spent. Every array holds exactly one −1 and
at most one +3, so every character has one clear weakness and at most one peak.

| Rule | Sum | **Peaked** | **Even** | **Broad** |
|---|---|---|---|---|
| **Free** | +5 | +3, +2, +1, 0, 0, 0, −1 | +2, +2, +1, +1, 0, 0, −1 | +2, +1, +1, +1, +1, 0, −1 |
| **Typical** | +7 | +3, +2, +2, +1, 0, 0, −1 | +2, +2, +2, +2, 0, 0, −1 | +2, +2, +2, +1, +1, 0, −1 |

The player chooses the **shape** freely (default Peaked). The shape is freedom, not quantity: the three
shapes of a rule have the same sum. All six arrays sit inside 00.4.3's creation envelope (each value
−1…+3; sums +5 and +7 are its two ends), so no array needs a clamp
[C:P11; C:P4; 00.4.3; R2 02 (Mistborn Adventure Game: every character ranks attributes strong, average
and weak; R: https://en.wikipedia.org/wiki/Mistborn_Adventure_Game); Ironsworn assigns 3, 2, 2, 1, 1
(R: https://en.wikipedia.org/wiki/Ironsworn); DL-02-03].

**02.3.2 The two rules: quantity against freedom (P4).** `[D]` Which rule a character uses is set by
their people (02.4.2) and by one choice (02.3.4):
- **The Free rule** (sum +5): the player places the array on the seven attributes in any order. Humans
  always use it. So does anyone who is *uncommon of their kind* (02.3.4).
- **The Typical rule** (sum +7): two more points, and the people decides three of the seven placements:
  one attribute must hold **+2 or more**, a second must hold **+1 or more**, and a third is **fixed at
  −1** (the array's only −1 goes there). The player places the rest.

| People | at least +2 | at least +1 | fixed at −1 | What the fixed −1 costs every such character |
|---|---|---|---|---|
| Elf | Agility | Wits | Endurance | starting Vitality 11; poor against poison, cold, exhaustion |
| Dwarf | Endurance | Resolve | Agility | Guard 2 lower than an Agility +1 character; poor aim and stealth |
| Halfling | Agility | Resolve | Might | weak blows, grapples and loads |
| Orc-kin | Might | Resolve | Intellect | poor recall, study and formal sorcery |
| Goblin-kin | Wits | Agility | Presence | poor persuasion, command and divine workings |
| Giant-kin | Might | Endurance | Wits | slow tempo, poor notice |
| Beastfolk | Wits | Agility | Resolve | dread threshold 7; poor against fear and compulsion |

Each of the seven attributes is the fixed low of exactly one people (checked by the generator script),
so the peoples are seven different answers to "what are you willing to be bad at?". The trade is real
in both directions and the audit shows it (T-02-3): over sixteen classic concepts, a people's Typical
rule beats the Free rule by up to 6 weighted points for the concepts its floors suit and trails it by
up to 10 where its fixed low bites; no people is best at everything, and each is better than Free for
some concepts and worse for others. The human's compensation for always carrying two fewer points is
complete freedom and one extra training (02.4.3)
[C:P4; R2 02 (The Land: humans 4 free points, other races more with forced allocation; "only works if
every option is calibrated to feel roughly equal in total value"); R3 02.1; DL-02-04].

**02.3.3 Placement and validation.** `[D]` A placement is legal when (a) the multiset of the seven
values equals the chosen array; (b) under the Typical rule, the people's two floors hold and its fixed
attribute holds −1. The engine validates on every change and refuses an illegal placement, naming the
constraint ("Dwarf, Typical: Agility is fixed at −1"). There are 1,680 legal placements under the Free
rule (840 Peaked, 630 Even, 210 Broad) and 84 under each people's Typical rule (54, 6, 24): the
difference between those two numbers is the freedom P4 speaks of.

**02.3.4 Uncommon of your kind.** `[D]` A player whose people is not human may choose, at C2, to be
**uncommon of their kind**: the character uses the **Free rule** (sum +5, any shape, any placement) in
place of their people's Typical rule. They keep the people's gift, tongues, hooks and birth pool; they
do not receive the human's extra training. The choice is recorded as `pc.origin.rule = free` and is
part of the creation lock (02.2.6). This is how a goblin priest, a dwarf acrobat or an orc scholar is
built at full strength in their chosen thing: by giving up the two points their people would have
given them [Pathfinder Second Edition allows any character to replace an ancestry's listed boosts and
flaw with two free boosts: R: https://2e.aonprd.com/Rules.aspx?ID=2079; DL-02-04]. A character of
mixed heritage picks which parent's people entry they take, and may describe their looks as they like;
the rules follow the entry.

**02.3.5 Default placement.** `[D]` When the player does not place the array, the engine does, from the
livelihood's `defaults.attribute_priority` (an ordering of the seven attributes): among all legal
placements of the chosen shape, it takes the one that gives the highest value to the first attribute in
the ordering, then the highest possible to the second, and so on (lexicographic maximum). The result
for every livelihood and people is tabulated in T-02-6. **Caster exception** `[revision: I-009]`: for a
magic livelihood (02.5.5) whose people's Typical rule fixes the livelihood's casting attribute (05.7.2) at
−1, the default uses the **Free rule** (02.3.4) instead, and the DM says so in one line; the player may
still choose the Typical rule, and the DM then states the effect DC it produces (Edge cases, "Choices
against the grain"). Four cells
change: the Orc-kin apprentice, the Goblin-kin acolyte, and the Beastfolk hedge-taught and Touched, whose
casting attribute moves from −1 to +3 (`origins.yaml#creation_defaults.typical_rule_except`). *Why:* the
fast path should never make a caster who cannot cast; with the default, every default-path new caster
beats one T2 foe 90.5–94.8% of the time on its branch working, where a Typical-rule caster at +1 does
62–73% (`sim02.py`) [DL-02-25]. *Example:* Soldier's priority is Might,
Endurance, Agility, Wits, Resolve, Presence, Intellect. Human, Peaked (+3, +2, +1, 0, 0, 0, −1): Might
+3, Endurance +2, Agility +1, Wits 0, Resolve 0, Presence 0, Intellect −1. Dwarf, Typical, Peaked
(+3, +2, +2, +1, 0, 0, −1; Endurance ≥ +2, Resolve ≥ +1, Agility −1): Might +3, Endurance +2, Agility
−1, Wits +2, Resolve +1, Presence 0, Intellect 0.

**02.3.6 Attributes after creation.** `[D]` After the creation window closes, an attribute changes only
by: the **Bent** (02.6.5; +1 to one attribute, never above +3, once, if accepted); chapter 04's one +1
at a confirmed tier 4 (never above +4); chapter 07's maims (−1, never below −2). So a Free character's
sum runs +5 at creation and +6 with the Bent; a Typical character's +7 and +8. Derived values follow
the attribute at once (maximum Vitality, 02.7.1; dread threshold; Guard; tempo)
[00.4.3; 04 Interface amendment 8; 07.7.4].

### 02.4 Origins

**02.4.1 Three origins, one of each.** `[D]` Every character has exactly one **people**, one
**upbringing** and one **livelihood**, each an entry of `data/origins.yaml` (`kind`: `people`,
`upbringing`, `livelihood`). Any people may be combined with any upbringing and any livelihood: 8 × 9 ×
21 = 1,512 combinations, none forbidden. What each kind sets, and nothing else:

| Kind | Sets | Never sets |
|---|---|---|
| **People** (who you were born) | the attribute rule (02.3.2); one innate gift; your native tongue and Common; one deed branch and your people tag in the birth pool; two hooks | trainings, Focus, kit |
| **Upbringing** (where and how you grew) | base Focus (3, 4 or 5); letters or not; second tongues; one or two access licenses; the pack and purse; two deed branches and terrain tags in the birth pool; bond seeds; two hooks | attributes, deep trainings |
| **Livelihood** (what you did before the story) | the list your trainings are picked from; the kit of the work; the default profile, picks and attribute priority; magic's first license and its `requires`; two deed branches in the birth pool; drive, aspiration and bond seeds; two hooks | attributes, Focus |

[Blades in the Dark: heritage, background and playbook are three separate picks, each with "write a
detail": R: https://bladesinthedark.com/character-creation; Burning Wheel builds a character from the
lifepaths they walked: R: http://rpgsystems.wikidot.com/burning-wheel; R1 M-30; DL-02-22]

**02.4.2 People.** `[D]` The eight peoples are the eight `creature.folk.*` tags of 00's vocabulary:
Human, Elf, Dwarf, Halfling, Orc-kin, Goblin-kin, Giant-kin, Beastfolk (T-02-2). A people grants:
- its **attribute rule** (02.3.2), or the Free rule if the player chooses 02.3.4;
- one **gift**: a license of kind `fact` in `data/licenses.yaml owner-block 02`, with its effect given as an
  effect reference (Starsight, Stonesense, Underfoot, Iron blood, Cave-eyes, Great frame, Keen nose).
  Each is one small thing, always on, read literally (INV-8). Humans have no gift and take 02.4.3
  instead;
- its **native tongue** at grade `native` and the Common tongue at `accented` (humans and halflings
  hold Common at `native`; a halfling also picks one further tongue at `accented`);
- its `creature.folk.*` tag on the character entity (reaction rolls, 12.11.2, and pool gates read it).

A people sets no training, no competence and no kit. Chapter 13 decides which peoples live in its
region and may add peoples in its owner-block (02.4.8). A gift is never learned, lost or bought.

**02.4.3 The human's extra training.** `[D]` A human takes **one extra training license held as access**
(grade `trained`, no competence above the floor) on any level-2 deed tag outside the three magic
branches. It is in addition to the breadth profile's picks (02.5.2) and is chosen at C5.

**02.4.4 Upbringing.** `[D]` The nine upbringings (T-02-4) each spend exactly **three permanent units**,
and differ only in how:

| Thing granted | Units |
|---|---|
| base Focus 5 / 4 / 3 | 2 / 1 / 0 |
| one training license, held as access | 1 |
| `lic.lang.letters` | 1 |
| one further tongue at `accented` | 1 |

Coin and the quality of clothes also vary by upbringing (`wealth`: destitute, poor, modest,
comfortable), but they are outside the budget because they are spent within a session and nothing
permanent may be priced in coin (02.8.2). So the upbringing is a real, locked trade between **inner
reserve** (Focus, which never changes after creation, 05.6.1) and **worldly knowledge** (letters,
tongues, trades): the Cloister gives Focus 5 and letters and nothing else; the Court gives letters,
etiquette and a tongue at Focus 3 [C:P4; 00.3.13; DL-02-05; DL-02-10]. Where an upbringing offers a
choice of license, the player picks one from its list.

**02.4.5 Livelihood.** `[D]` The twenty-one livelihoods (T-02-5) are what the character did before the
story: Soldier, Hunter, Rider, Laborer, Thief, Charlatan, Sailor, Herder, Scholar, Healer, Apprentice,
Acolyte, Hedge-taught, Touched, Merchant, Performer, Courtier, Artisan, Watchman, Tinker, Wanderer.
A livelihood is **not a calling**: it grants no calling, tier or pick, and a Soldier who spends her
days picking locks will be recognized as what she does (04). It grants:
- a **list** of five to eight level-2 deed tags (`trainings`), from which the breadth profile's picks
  are made (02.5.3); together the livelihood lists and the upbringings cover all 81 level-2 deed tags
  (script-checked);
- for the four **magic livelihoods** (Apprentice, Acolyte, Hedge-taught, Touched), one school of their
  branch as the deep pick, with the license's `requires` satisfied (02.5.5);
- the **kit** of the work (02.8);
- **seeds**: three drives, two aspirations with tags, two bonds, two hooks, two organization tags.

The Scholar and the Apprentice also grant `lic.lang.letters` (their work cannot be done without it).

**02.4.6 Tongues and letters.** `[D]` A tongue is a license `lic.lang.*` with three grades
(`data/licenses.yaml owner-block 02`): **broken** (simple concrete matters; every Talk in it holds a
Precision snag and its reach is capped at Limited), **accented** (everyday speech with no snag; subtle,
technical or courtly matters hold a Precision snag), **native** (everything). Speaking with someone in
a tongue not held is not Talk in that tongue: it is the license's crude fallback (gesture, tone and
shared nouns; DC +5, reach Limited; 01.18). **Letters** (`lic.lang.letters`) lets a character read and
write every tongue they hold at accented or native; without it, reading is Observe's excluded method
and falls to the license's crude fallback (numerals, seals, a few signs). Nine tongues are defined for
the eight peoples: Common, Elvish, Dwarvish, Orcish, Goblin, Giantish, Kin-speech, the Old Tongue (dead;
at most accented), and the Cant. Chapter 13 owns the tongues of its region and may rename or add
[00.4.4: Intellect's one derived value is tongues and lore at creation; 05.9.4: the arcane path
requires literacy; DL-02-12].

**02.4.7 Origin facts.** `[D]` At C9 the engine writes four facts with `source: data`,
`visibility: shown`: `pc.origin.people`, `pc.origin.upbringing`, `pc.origin.livelihood`, and
`pc.origin.rule` (`typical` | `free`). These are established facts in the full sense of 00.6.7: the
player may cite them as levers where they honestly help a method (00.3.9: "raised on the docks" for
reading a harbor's routine), the gate may read them, and chapter 12's reaction roll reads them (+1 when
the PC shares an NPC's origin, faith or trade, 12.11.2). They license nothing by themselves: an origin
fact is not a training, and "I was a soldier, so I know siegecraft" is Recall's common knowledge of
one's trade (T-00-11) at the floor unless `lic.training.martial_tactics` is held
[R4 §9 02 #4; R7 §2.24 (13th Age backgrounds are argued into relevance each time, which an AI decides
inconsistently: hence facts plus explicit licenses here); SG-06].

**02.4.8 Setting origins and the origin audit.** `[D]` Chapter 13 may add peoples, upbringings and
livelihoods for its setting in `origins.yaml#blocks` (owner "13"), and may mark any entry here as
absent from its region. Every added entry must pass PR-02-9, whose tests are the invariants of this
part: a people has exactly one floor of +2, one floor of +1 and one fixed −1 (or is Free), at most one
gift whose effect is one effect reference, and grants no training; an upbringing spends exactly three
units; a livelihood lists five to eight level-2 deed tags, gives a kit inside 02.8.2, and grants
nothing in 02.1.3. An entry that fails is not loaded (RC-DATA).

### 02.5 Trainings, breadth, and the floor

**02.5.1 The floor (P2).** `[D]` Every PC holds the competence entry `{tag: deed, value: 1, source:
floor}` from creation to the end of their life. Because competence is read from the beat's primary
deed tag *or any ancestor* (00.3.6), and `deed` is the ancestor of every deed tag, the floor applies to
every check a PC ever makes. This chapter **confirms the value +1** that 00.3.6 proposed. A PC with an
average attribute therefore rolls at +1 untrained, a successor starts exactly here (02.2.7), and no
creation path can produce a character who is helpless at ordinary things. The floor is the numeric half
of P2's baseline; the other half is the fifteen basic verbs every character may always attempt
(00.12.5) and the universal Focus push (05.6.7) [C:P2; 00.3.6; 01 Interface request; R3 02.4; DL-02-02].

**02.5.2 The breadth profile: breadth against competence (P4).** `[D]` At C5 the player chooses one of
four **profiles**. A profile says how many training licenses the character takes from their
livelihood's list and how many of them are held **deep**. It is a closed bracket: nothing is traded
between its columns.

| Profile | Held deep (+2) | Held as access | Technique | For a character who… |
|---|---|---|---|---|
| **Focused** | 2 | 0 | — | is plainly good at two things from the first scene |
| **Gifted** | 1 | 0 | 1 (rank 1) | is good at one thing and has one trick or spell of it |
| **Rounded** | 1 | 2 | — | is good at one thing and has worked at two more |
| **Broad** | 0 | 5 | — | has turned a hand to everything and mastered nothing yet |

What the two ways of holding a training mean, exactly:

| | **Held deep** | **Held as access** |
|---|---|---|
| License | `lic.training.<tag>` at grade `trained` | the same |
| What the license opens (05.9) | the tag's methods that the basic verbs exclude, up to Hard obstacles; learning and emulating its techniques; stretching them | the same |
| Competence entry | `{tag, value: 2, source: origin}` | none: checks under the tag use the floor (+1) |
| Focus push (05.6.7: only where competence is above the floor) | allowed | not allowed |

So breadth buys *permission* and depth buys *performance*. A Broad character may attempt surgery,
lockwork, tracking, a courtly address and a contract dispute, every one of them at the floor and none
of them pushable; a Focused character does two things at +2 with the push available, and for
everything else has only the basic verbs. This is the Mistborn Adventure Game's answer to the
all-access character ("how do you let people play Mistborn and not have everybody else suck"): the
one who can do everything starts mediocre at all of it [C:P4; R2 02, #10; 05.9.4 "breadth is available
and is not power"; DL-02-07]. *Audit:* counting an access license as 1 unit and a deep one or a
technique as 2, the profiles are worth 4, 4, 4 and 5: Broad is paid one unit for holding nothing above
the floor.

**02.5.3 Making the picks.** `[D]`
1. Each pick is a level-2 deed tag on the livelihood's `trainings` list; its training license is
   `lic.training.<branch>_<tag>` (`data/licenses.yaml`).
2. **One pick may be off-list**: any level-2 deed tag outside the three magic branches. (The life you
   led was not the only thing you ever did.)
3. A **magic school** (a level-2 tag under `deed.arcane`, `deed.divine` or `deed.primal`) may be picked
   only by a magic livelihood, only from its `magic.schools`, and only **one** school (02.5.5).
4. The engine grants each license at grade `trained` (`grant`, source `orig.life.*`), and for each deep
   pick writes the competence entry at +2.
5. Then the human's extra training (02.4.3), the upbringing's licenses (02.4.4) and the learning picks
   (02.5.6) are granted; duplicates are resolved by 02.5.7.

Totals: a character leaves creation with between 1 training license (Gifted, Cloister-raised, not
human, Intellect 0 or less) and 11 (Broad 5, an upbringing's 2, the human's 1, three lore picks from
Intellect +3). In both cases at most two tags hold competence above the floor.

**02.5.4 The gifted technique.** `[D]` The Gifted profile grants **one** ability: any entry of
`data/abilities.yaml` with `min_tier: 1` whose first tag is at or under the tag held deep, excluding
abilities that require a conduct (`requires_conduct`) and the absorbed-power mirrors (`ab.abs_*`). It
is granted into the **acquired** partition at **rank 1** with `source.kind: gift`, provisional under
chapter 05's ordinary rule for acquired abilities (05.2), and it uses its training's license like any
learned ability. It is the only ability any character starts with: the calling partition is empty until
a calling's first tier fills it (05.2.4; 04.8.4), at which point a pick may promote the gifted
technique into the calling partition (chapter 05's promotion rule). Each livelihood lists suggestions
(`technique_suggestions`); the rule above is what binds [05 Interface request: "at most one ability
into the acquired partition at rank 1"; C:V; DL-02-07].

**02.5.5 Magic livelihoods.** `[D]` Magic is licensed like everything else (C:VII): a character works
magic from the first scene only if a livelihood gave them a school's training license with its
`requires` met (05.9.4). Four livelihoods do, one per source and one innate:

| Livelihood | Branch; casting attribute (05.7.2) | Schools to choose one from | How the license's `requires` is satisfied at creation | Facts and items written |
|---|---|---|---|---|
| **Apprentice** | arcane; Intellect | fire, frost, storm, earth, illusion, divination, warding, mind, summoning, necromancy, alteration | literacy and a text or teacher | `lic.lang.letters`; a spellbook in the kit with the fact `teaches: <the gifted spell>`; a master as a mentor bond |
| **Acolyte** | divine; Presence | healing, warding, smiting, rites, oaths, revelation, exorcism, pact | a keeper that accepts the character (05.7.4) | `pc.keeper.<school> = <a power of chapter 13's>`; the keeper's sign (`item.tool.implement.holy_symbol`) in the kit; the keeper's faith starts at Warm (02.9.5), so the keeper's regard holds |
| **Hedge-taught** | primal; Resolve | growth, beastkin, weather, shapeshifting, spirits, elements, hexcraft | a place or spirit that accepts the character | `pc.accepted.primal.<school> = <a place, named with the player>`; the teacher as a mentor bond |
| **Touched** | primal; Resolve | the same seven, named by the player or left to birth (02.6.3) | none to satisfy: the gift is the acceptance | `pc.accepted.primal.<school> = innate`, written by `gen.birth` |

Rules for all four: (a) the school is the character's deep pick (competence +2 at the school's tag);
(b) on the **Gifted** profile (their default) the technique is a `min_tier: 1` spell of that school,
so the character can cast from the first scene, at 1 Focus a casting for most first spells; (c) on
**Focused** or **Rounded** they hold the school deep with no spell, and can do only small workings
(05.7.6) and emulation until they learn one: the DM says this in plain words before the player
confirms; (d) on **Broad** the school is one of the five access picks; (e) the Touched must take
Gifted, because the gift decides both picks. One school only: a second school is learned in play by
chapter 05's paths [04.2.7 coverage audit; 04 and 05 Interface requests; DL-02-06; DL-02-09].

**02.5.6 Learning picks (Intellect's derived value).** `[D]` A character has **learning picks** equal
to their Intellect, minimum 0 (00.4.4: the one value Intellect derives). Each pick is one of: a tongue
at `accented`; one grade more in a tongue already held; `lic.lang.letters`; or one `lic.training.lore_*`
license held as access. Learning picks never grant competence. A character who gains Intellect later
(the Bent, a tier) gains no pick: the picks are a fact about their youth.

**02.5.7 Duplicates.** `[D]` No one holds two instances of a license (INV-13). If two sources grant the
same training license: deep beats access (the license is held once, with the +2); and the source whose
grant was absorbed gives, in its place, the next license on its own list that is not held (an
upbringing's choice list, a livelihood's list), or, if it has no list or the list is exhausted, one
learning pick. Two grants of letters, or of a tongue at the same grade, resolve the same way.

### 02.6 Birth: the variance beneath the choices (P1)

**02.6.1 One domain, four layers, two moments.** `[D]` Everything random about who a character is comes
from one generator domain, `gen.birth` (`data/gen_birth.yaml`), run by the algorithm of 00.11 through
the `generate` tool. Its **source** (the pool-gating circumstance) is the character: at creation, the
union of the three origins' `birth_pool` tags (a people tag, deed branches, terrain tags). Its
**circumstance** (the fill-quality circumstance) is how the character came through childhood (02.6.4).
Its pool has four layers:

| Layer | Slot | What it is | Entries | When drawn | Applied? |
|---|---|---|---|---|---|
| **knack** | magnitude | +1 edge on checks whose primary deed tag is at or under one level-2 deed tag (`eff.check_edge`) | 81, one per level-2 deed tag, each gated by its **branch** | creation | yes |
| **quirk** | magnitude | one small permanent quirk: a lever in a narrow circumstance, a hazard step, or a daily reveal | 22 | creation | yes |
| **gift** | signature | an innate primal school (+2) with its first working | 7 | creation, Touched only | yes |
| **bent** | magnitude | +1 to one attribute (`eff.02.bent`) | 7 | after creation | **only if accepted** |

P1 asks for both halves: variance at creation that is mandatory ("so that two characters with identical
visible choices still diverge"), and variance after creation that is never forced on the player. The
knack and quirk are the first half; the Bent is the second [C:P1; 00.11.1; R3 02.7 "the origin is the
pool gate, and a birth roll is the fill"; R4 §9 02 #2: birth variance is an engine roll; DL-02-08].

**02.6.2 The creation draw.** `[D]` At C6 the engine calls
`generate(gen.birth, source: pc, circumstance, degree: none)` (PR-02-4). On the `plain` quality rung it
fills two magnitude slots, one from each of the layers knack and quirk:
- **Knack.** The pool gate admits the knacks of every deed branch in the source's tags: two branches
  from the upbringing, two from the livelihood, one from a non-human people (the union is 2 to 5
  branches; over all 1,512 origin combinations the knack pool holds between 15 and 52 entries, median
  35). A magic branch enters only through a magic livelihood. The draw is weighted (all knacks weight
  2). The result is an edge of +1 (family `edge`, cap +2 with any item edge; 00.3.5) on that tag and
  its descendants, for life. It stacks with competence, so a knack that lands on a deep training makes
  a +6 specialist (attribute +3, competence +2, edge +1: the top of band 1, 00.3.7); with the default
  picks that happens between 0% and 12% of the time depending on the livelihood (T-02-9). Far more
  often the knack lands beside what the character trained: a hunter with a feel for the sea, a clerk
  with a carpenter's hands. That is its purpose: it is an invitation the player did not write.
- **Quirk.** Twenty-two entries (T-02-8), almost all open to everyone. Each is one effect reference of
  the core library's size: a Precision, Protective or Amplifying lever in one narrow, checkable
  circumstance (which still counts toward the two-lever limit and still cites a fact, 00.3.9 f), a
  hazard step of one rung against one harm kind, or a daily reveal.

Both results are written as permanent effect instances on the character with source `gen.birth` and are
`shown` in the codex by name and text. Neither can be re-rolled, traded or removed, at creation or in
the second look. A knack for a school of magic the character cannot yet work is still theirs: it
waits.

**02.6.3 The gift (the Touched).** `[D]` For a Touched character the circumstance is `gifted` and the
rung is `marked`: one signature slot (layer gift) and the same two magnitude slots. The seven gift
entries are gated by their school's tag. If the player **named** the power in their concept ("I've
always been able to call the wind"), the source carries that one school tag, one entry passes the pool
gate, and it fills the slot. If the player **left it to birth**, the source carries all seven school
tags and the engine draws one, equal weights. The gift entry grants the school's training license at
`trained` as an innate license, competence +2 at the school, the acceptance fact, and its listed
first working at rank 1 (T-02-7). **The spark** names an element as well: fire, water, earth or air,
named in the concept or drawn by the engine with equal weights in the same draw (fact `pc.spark.element`),
and its first working is that element's: Cinder Stride, Undertow, Heave or Stolen Breath
(`gifted_ability_by_element`) [revision: I-015; DL-02-24]. This is the innate spark that chapter 04's Elementalist needs
(04.2.7), generalized to all seven primal schools because all seven are things one can be born to
[HWFWM's awakening stones fill a slot by a roll shaped by who the person is, with no reroll; racial
gifts are a small fixed package: R2 02; 04 Interface request; DL-02-09].

**02.6.4 The manner of childhood.**

```
### 02.6.4  The manner of childhood                                   [J:enum]
Trigger [T]:        step C6, before the creation draw
Loads in:           creation
License check:      none
Decisions (J):      1. MANNER [J:enum], from what is RECORDED (the origins) and what the player has
                       SAID about the character's birth or childhood (asked once, on the full path
                       only: "Was anything said about your birth, or about your early years?"):
                       gifted     true only when the livelihood is Touched. False for every other
                                  livelihood, whatever the account says.
                       hard       true only when the upbringing is Bound service, or the account
                                  establishes want, war, plague, servitude or exile in childhood.
                                  False for ordinary poverty or a strict household.
                       omened     true only when the account establishes a sign at the birth or in
                                  the cradle: a storm, a comet, an eclipse, a caul, a death in the
                                  house that night, a seer's word. False for a sign that came later
                                  in life (that is a hook, 02.9.7).
                       unremarked everything else, and whenever the player gave no account.
                       First match in the order written (gifted, hard, omened, unremarked).
                       Default when uncertain: unremarked.
Computation [D]:    the manner is the `circumstance` passed to generate (gen_birth.yaml#fill_map):
                    unremarked -> weighted; hard -> biased, x3 on entries carrying
                    deed.wilds.survival (the survival knack and six quirks: 27.5% of quirk
                    weight becomes 53.2%); omened -> biased, x3 on entries carrying
                    trait.nature.magical (the four uncanny quirks: 10.0% becomes 25.0%);
                    gifted -> the signature fill of 02.6.3, magnitude slots weighted.
Stakes:             none
State writes:       pc.creation.birth.manner; if the player gave an account, a fact
                    pc.birth.account = <their words, neutrally restated> (shown)
Narration may not imply: that the manner granted anything beyond the two (or three) drawn results
Worst case (J):     a manner one step off: the weights of at most 7 of the 103 knack and quirk
                    entries are tripled or not, for one draw; no entry becomes available or
                    unavailable (class i).
Examples:           inside (hard): "we were turned off our land when I was six and lived on the
                      road two winters".
                    boundary (unremarked): "my father was a hard man" -> a strict household, not
                      want or exile.
                    inside (omened): "born with a caul, the midwife crossed herself".
                    boundary (unremarked): "a fortune-teller told me at fifteen I'd die by water"
                      -> a later sign: a hook (question), not a manner.
                    non-example: "I was born lucky, so give me something good" -> an assertion
                      about outcomes (SG-06); the manner is unremarked and the draw is the draw.
Anchor:             no
Basis:              [C:P5 pool gate and fill quality are domain-independent] [00.11.2] [R2 02: HWFWM
                    awakening weighted by who the person is] [SG-05] [DL-02-08]
```

**02.6.5 The Bent.** `[T]` + `[D]` After creation, a character's nature settles one step further: the
**Bent**, +1 to one attribute, permanently, never above +3. It is P1's variance after creation, and so
it is never applied without the player's yes.
- **Eligible when:** the creation window is closed (02.2.6), the Bent is neither accepted nor forgone,
  and at least one deed branch has **three resolved frames** with the PC as actor since creation
  (counted by the engine from the frame log by primary deed tag; no judgment).
- **Offered at:** a `reflection` boundary, by handler `h.02.bent_offer` (phase 8). The first offer
  comes no earlier than the reflection *after* the one that closed the window.
- **The draw.** `generate(gen.birth, source: pc, circumstance: bent_first | bent_again, degree: none)`
  on the `latent` rung: one magnitude slot, layer bent. The **source tags for this draw are the deed
  branches with at least three such frames**; each attribute's entry is gated by the branches whose
  work exercises it (T-02-10): a character who has only fought can find a bent toward Might, Agility or
  Endurance; one who has fought and ranged the wilds adds Wits. An attribute already at +3, and any
  entry the player has declined before, is excluded. The draw among what remains is weighted, equal
  weights. So the Bent is random, and it is random among the things the character has actually been
  doing [C:P5 "derived from what a character actually did"; C:P1].
- **The offer** is made out of fiction as a `[CHOICE]` with no default (02.6.6). Nothing changes until
  the player answers.

**02.6.6 Accept, or defer and gamble.** `[D]` The player's two answers to a Bent offer:
- **Accept.** `eff.02.bent` raises the attribute by 1; `pc.creation.bent = accepted`; derived values
  follow (02.3.6). The Bent is finished for this character's life.
- **Defer.** The offered result is discarded and that attribute is struck from all later Bent draws for
  this character. Nothing is applied. A new draw is made at a later reflection (02.6.7), from the pool
  as it then stands: the branches the character has worked in by then, less the struck attributes. The
  player then accepts or defers again.

A character may defer **twice**. The third draw is the last: the player **accepts it or forgoes the
Bent** for good (`pc.creation.bent = forgone`); nothing is ever applied by default, and an unanswered
offer simply stays open. This is the gamble P1 describes: by deferring, the player gives up a sure +1
now for a chance at the one they want later, plays without it meanwhile, and can end with a worse
choice or none. With `n` attributes eligible and one wanted, accepting the first draw gives it with
chance 1 in `n`; deferring until it comes gives it with chance 3 in `n` (certain when `n` ≤ 3, 75% at
4, 60% at 5, 50% at 6) and nothing otherwise (T-02-11). The player can shift the odds honestly, by
what the character does between draws: branches worked add attributes to the pool, and they are never
removed [C:P1 "a deliberate departure from every source researched"; Diablo III's enchanting, the one
partial precedent, lets a player re-roll one property and keep the old result if they prefer: R3 02.2;
DL-02-11].

**02.6.7 Spacing.** `[D]` After a deferral, the next draw is made at the first `reflection` at which
both hold: at least **two** reflections have passed since the deferral, and the PC has been the actor in
at least **ten** further resolved frames (engine-counted). An open offer the player has not answered is
re-shown at each session start in the SITUATION block (12.15.11) and never re-drawn. *Narration may not
imply* that the Bent has taken effect before it is accepted, or that deferring cost the character
anything in the fiction.

**02.6.8 How birth is shown.** `[N]` + `[D]` The knack, the quirk and a gift are `shown`: the codex lists
each by its plain name and literal text ("A knack for tracking: +1 on tracking"). The DM tells the
player the results at C6 in one or two sentences of ordinary language, as things that have always been
true of the character, and never as a roll ("You have always been able to find north with your eyes
shut, and you took to boats faster than a forester's child should"). In play, narration may color a
success with the knack or quirk when its effect applied to the frame, and at no other time (INV-2).
Because variance the player did not choose "can read as unfair unless framed narratively", two things
are fixed: every creation result is a benefit (no entry of the knack, quirk or gift layers has a
downside), and the one result that changes an attribute is always an offer [R2 02; R2 #14; SG-15].

### 02.7 Starting numbers

**02.7.1 Vitality.** `[D]` `vitality.base = 12 + Endurance`. At creation Endurance is −1…+3, so base
Vitality is **11…15**; over a lifetime's Endurance range of −2…+4 it is **10…16**, which is exactly
00.3.12's envelope, with the reference character (Endurance 0) at the reference value 12. A new
character's maximum Vitality equals its base, and current equals maximum. Chapter 07 owns everything
after that: it adds 2 per power band above the first, applies wound penalties, clamps at 24, and
recomputes when Endurance changes (07.1.2; DL-00-04; handler `h.07.vitality_max`). Endurance is the only
attribute that feeds Vitality (00.4.4), and one point of it is worth one Vitality: a third of one
Moderate blow, so that toughness matters and no character is built on it alone [00.3.12; 07 Interface
request; DL-02-16].

**02.7.2 Focus.** `[D]` `focus.base` is the upbringing's `focus_base`: **3, 4 or 5** (02.4.4). It derives
from no attribute (00.3.13; DL-00A-09) and never changes after creation (05.6.1). A new character's
maximum Focus equals the base (no calling yet: `T_high = 0`), and current equals maximum. Chapter 05
owns all growth, costs and recovery. What a new character spends Focus on: the push, on beats under a
deep training (05.6.7); a gifted technique's cost; grit (07).

**02.7.3 Fate, dread, harm state.** `[D]` A new character has `fate.current = 1` (01.16.1), dread 0,
harm state `active`, no wounds, no marks, no conditions, no afflictions. A new character's power band is
1 (04's `power_band`: no confirmed tier).

**02.7.4 Computed values the sheet shows.** `[D]` These are computed by their owning chapters from the
record and are shown at C9 so the player sees what their choices did; this chapter stores none of them:
**Guard** = 10 + Agility + competence of the readied melee weapon or shield + a shield's +1 edge
(06.4.1); **tempo** = Wits + competence at `deed.martial.tactics.reading` or an ancestor (06.2.2);
**dread threshold** = 8 + Resolve (07.11); the seven **defenses** = 10 + attribute + competence + edge
(00.3.8); **carrying capacity** from Might (08).

### 02.8 Kit

**02.8.1 Two kits.** `[D]` A new character receives the **pack** of their upbringing (clothes, sundries,
food, coin) and the **kit** of their livelihood (tools and arms, and a little more coin), both from
`data/kits.yaml`. Kits name items by `item.*` tag with a quality and a quantity; chapter 08 resolves
each tag to a base item (00.17.1 Q17), so this chapter uses none of 08's ids. Where a kit offers a
choice (a soldier's sword, spear, hand axe or mace), the player picks one option; the default is the
first. The two coin amounts are added. A player may exchange any kit item for another item of the same
level-2 item tag and the same or a lower quality at no cost (a sword for a rapier; a shortbow for a
sling); anything else is bought in the opening scene at chapter 08's prices.

**02.8.2 Kit limits.** `[D]` No kit item is above quality `fine`; none carries a property from any
generator pool (nothing magical, nothing with a signature); armor is at most `item.armor.light`
(reduction 1, 07); weapons are of weight light, one-handed, bow or sling (T-06-6: base severity
Moderate at most); at most one mount, of quality `worn`; no healing potion. Starting coin runs from 3
(Bound service with the Hedge-taught kit: 1 + 2) to 55 (a Court-raised Merchant: 30 + 25). Gear gives access and
utility; a character's strength is in their record, not their pack [R1 02; 06 Interface request to 02:
"a martial origin should start with light armor and a one-handed weapon or bow"; DL-02-13].

**02.8.3 Every item has an id.** `[D]` At C7 each kit item is created as an entity (`create_entity`,
kind `item`, with chapter 08's base item for the tag, its quality, and the kit line's `note` as a
narration seed), added to `possessions`, and the items a character would wear or hold ready are marked
equipped. From the first turn a possession can be cited as a lever, handed over, lost as a cost
(`cost.gear`) or checked by the gate, because it exists in state [R4 §9 02 #5; 00.6.6].

### 02.9 Ties: who the character is to the world

Step C8 gives the living world its handles on the character. Everything here is narrative material
with a small, exact mechanical footprint: a commitment, a relationship on the standing scale, a row in
the Leanings view, a fact, a seeded hook. None of it adds to a roll [R1 02: "13th Age balances
distinctiveness narratively, not with a shared currency… once they carry power, they need audited
cost"; R5 CC-04, CC-08, CC-09, CC-10].

**02.9.1 The drive.**

```
### 02.9.1  The drive, and the long vow                               [J:enum] [D]
Trigger [T]:        step C8: the player answers "What does your character want most, or believe
                    most?" in one sentence, or takes one of the livelihood's three drive_seeds
Loads in:           creation; and at any reflection when the player rewrites the drive
License check:      none
Decisions (J):      1. KIND [J:enum]
                       want   true only when the sentence names something that could be FINISHED:
                              a thing to find, win, build, undo, avenge, reach or return. Test:
                              "could a scene end with this done?"
                       creed  true only when the sentence names something that can only be KEPT or
                              BROKEN: a principle, a refusal, a loyalty. Test: "is there no day on
                              which this is finished?"
                       Default when uncertain: want (it gives the world something to place).
                    2. CONDUCT TAG [J:enum], creeds only: the one conduct axis (00.5.3: mercy,
                       honesty, courage, loyalty, generosity, justice, humility, restraint, piety,
                       protection) the creed speaks to, with its pole, or none. Uncertain -> none.
Computation [D]:    want  -> a commitment {kind: vow, text} on the character (the LONG VOW) and a
                             thread seed handed to chapter 11 (02.9.7, kind thread). Chapter 11
                             makes the thread, sizes its clock and places its first clues; when the
                             vow is kept, chapter 01 awards fate +1 (01.16.2: vow_kept).
                    creed -> a commitment {kind: invariant, text, conduct: <axis and pole | none>}.
                             It creates no thread. It is a rotation facet (02.11.3): chapter 12
                             frames scenes that put it under pressure. Keeping or breaking it has
                             no rule of its own; acts that express the conduct axis are evidence
                             under chapter 03 like any other act, and an oath is something chapter
                             04 may one day offer.
                    Either kind may be rewritten by the player at any reflection, out of fiction;
                    a rewritten vow's thread is closed as abandoned by chapter 11.
Stakes:             none
State writes:       the commitment; pc.creation.drive; the thread seed (want only)
Narration may not imply: that the drive is known to anyone in the world, or that it grants a lever
Worst case (J):     a creed filed as a want: a thread that cannot complete sits in the register
                    until the player rewrites it at a reflection (class iv). A want filed as a
                    creed: no thread is seeded; the player says so and it is refiled (class iv).
Examples:           want: "I will have back the stake I was cheated of." "Find who burned the
                      ferry." "A wall of my own to stand on."
                    creed: "I will never again fight for a cause I cannot name." (conduct: none)
                      "No one dies of a thing I know how to mend." (conduct.mercy, merciful)
                    boundary: "I want to be the greatest swordsman alive" -> neither: it names who
                      the character hopes to BECOME, which is an aspiration (02.9.3). The DM files
                      it there and asks the drive question once more.
                    non-example: "I want 500 coins" stated as a claim to start with them: a drive
                      is a want, never a grant (02.1.3).
Anchor:             no
Basis:              [R5 CC-08, CC-09, P-40 (Ironsworn: a background vow and an inciting incident),
                    P-46 (Burning Wheel beliefs tell the GM what to challenge)] [R1 02 (Robin's
                    Laws: a character needs "a need and desire to join in the story")] [DL-02-17]
```

Chapter 13 supplies the other half of a strong start: the inciting incident of its opening.

**02.9.2 Bonds.** `[D]` A bond is a named person who matters to the character from the first minute. A
new character has **two bond slots**: an **anchor** (someone who holds them to the world) and a
**thorn** (someone or something unresolved). Each origin entry offers seeds; the player may take one,
change it, or write their own.

| Slot | Kind | Starting standing toward the PC (00.3.16) | Also written |
|---|---|---|---|
| anchor | **kin** | +2 Friendly | |
| anchor | **friend** | +2 Friendly | |
| anchor | **mentor** | +1 Warm | for a magic livelihood, the teacher or master is this bond |
| anchor | **ward** | +2 Friendly | a commitment: they depend on the character |
| thorn | **rival** | −1 Wary | |
| thorn | **creditor** | 0 Neutral | a commitment (kind debt): what is owed |
| thorn | **enemy** | −2 Unfriendly | |
| thorn | **lost** | none (absent) | a sealed fact: what became of them; a hook of kind `question` |

For each bond the engine creates an NPC at depth **recurring** (12.11.1: name, gender, age band, a
detail, a want, a fear, a voice, one refusal), using the player's words for whatever they stated and
the tables for the rest, and sets the standing in the table with `set_relationship` (reason `bond`).
A bond's standing is **set, not rolled**: the reaction roll is for first impressions (12.11.2), and a
bond is not one; no bond starts at Devoted. For a **lost** bond the engine asks the Oracle one sealed
question at rung Even ("does this person still live?") and seals the answer; its gate is a clue
(chapter 15). Chapter 13 places each bond NPC in its region: the anchor within the opening settlement
or a day of it, the thorn wherever chapter 11's situations want them. Standing then moves only by
chapter 15's rules; a bond can be lost [Blades in the Dark: mark one close friend and one rival,
R: https://bladesinthedark.com/character-creation; Dungeon World bonds, R1 M-30; R5 CC-10; DL-02-17].

**02.9.3 Aspirations.**

```
### 02.9.3  Aspirations                                               [J:enum] [D]
Trigger [T]:        step C8: the player says who their character hopes to BECOME; or 02.9.1 routes
                    a sentence here; or, at any reflection, the player adds, changes or drops one
Loads in:           creation; reflection
License check:      none
Decisions (J):      1. TAGS [J:enum]: up to TWO tags that name what the aspiration is an aspiration
                       TO: deed tags classified level by level (branch, then level 2, then level 3
                       only if the sentence is that specific) and/or one conduct axis. Use the
                       definitions and distinguishing tests of data/tags.yaml. Uncertain at a
                       level -> stop at the level above. Nothing in the sentence maps to a deed or
                       a conduct (e.g. "to be rich") -> no tags: it is recorded as text only, and
                       the DM says it will not appear in Leanings.
Computation [D]:    the engine writes {text, tags} to Character.aspirations (at most THREE held).
                    Effects, all of them chapter 04's and 12's: each tag adds its row to the
                    Leanings view even while unformed (04.6.5); a calling candidate keyed at or
                    under an aspiration's tag is presented first among offers of equal confidence
                    (04.7); each aspiration is a rotation facet (02.11.3).
                    An aspiration NEVER adds evidence, weight, confidence or competence
                    (03 Design intent; 04.6.5).
Stakes:             none
State writes:       Character.aspirations; pc.creation.aspirations
Narration may not imply: that the aspiration is a calling, a promise by the world, or progress
Worst case (J):     tags one level too shallow or on a sibling: a Leanings row carries the wrong
                    plain name until the player corrects it at a reflection; no threshold, tally
                    or offer content changes (class iii and iv).
Examples:           "to be the best shot in the marches" -> [deed.martial.archery].
                    "to be the shield others stand behind" -> [deed.martial.shield,
                      conduct.protection].
                    boundary: "to be a knight" -> knighthood is a rank (chapter 11), which is not
                      a tag; what a knight DOES is [deed.martial.mounted]; the DM says both.
                    boundary: "to be a great wizard" with no school named -> [deed.arcane]: stop
                      at the branch.
                    non-example: "to be recognized as a Ranger at tier 3" -> names a calling and a
                      number the codex never shows; restate as what the character does
                      ("to be at home in any wild country, bow in hand") ->
                      [deed.wilds, deed.martial.archery].
Anchor:             no
Basis:              [04.6.5] [04 Interface request: aspirations carry tags] [03 Design intent:
                    aspirations never weight evidence] [R6 R-A7] [DL-02-17]
```

On the full path a new character states one or two aspirations (the livelihood offers two seeds). On
the fast path the aspiration is taken from the answer to the drive question if that answer named one,
and is otherwise left **open** (02.9.8): a defaulted aspiration would point the Leanings view and the
order of offers somewhere the player never chose.

**02.9.4 The one true thing.**

```
### 02.9.4  The one true thing                                        [J:flag] [J:flag] [D]
Trigger [T]:        step C8 (full path), or any reflection while the slot is open: the player
                    states one thing that is true of this character and of no one else they
                    are likely to meet
Loads in:           creation; reflection
License check:      none: this rule exists so that the statement is NOT read as a license
Decisions (J):      1. CAPABILITY [J:flag] "Read literally, would this let the character attempt
                       anything that the basic verbs and the licenses they hold do not, or add to
                       any number?" True only when the sentence contains an ability, a sense, an
                       immunity, a bonus or a resource. Uncertain -> true (SG-05: when a rule asks
                       "does this grant something?", the answer is no).
                    2. WORLD [J:flag] "Does it assert something about the world beyond the
                       character's own person, ties and past: a rank, a title, a claim on property
                       or power, a fact about a people, a place, a god?" True only when someone
                       else in the world would have to agree for it to be so. Uncertain -> true.
Computation [D]:    both false -> set_fact(pc.true_thing = <text>, source: player_accepted,
                       certainty: established, visibility: shown), and one hook (02.9.7; kind
                       question or rumor, the player's choice).
                    CAPABILITY true -> not recorded as stated. The DM offers, in this order: the
                       same thing as a past event ("you once heard the dead speak"); as an
                       aspiration (02.9.3); or, if a livelihood grants it, that livelihood.
                    WORLD true -> recorded as a BELIEF: set_fact(..., certainty: believed), with
                       its truth decided by the Oracle at rung Even and SEALED (00.6.5); gate: a
                       clue or a principal NPC's word. The hook is of kind question.
                    Once recorded, the fact may be cited as a lever like any established fact,
                    within 00.3.9's limits, when it honestly helps a method.
Stakes:             none
State writes:       the fact (or belief and sealed truth); the hook; pc.creation.true_thing
Narration may not imply: that a believed thing is true or false; any capability
Worst case (J):     CAPABILITY wrongly false: a sentence with a capability in it is recorded as a
                       fact. It still licenses nothing: the gate reads licenses, never this fact
                       (00.12.2), so the first attempt to USE it is a G3 redirect (class iv).
                    WORLD wrongly false: a claim about the world is recorded as established; the
                       claim check and chapter 13's canon catch a contradiction at first use, and
                       the correction procedure (12.3.4) demotes it to a belief (class iv).
Examples:           both false: "I am the only one who walked out of Ember Hollow." "I have never
                      told a lie, and people can tell." (a reputation is others' business; this
                      is a fact about her own past, and "people can tell" is dropped as an
                      outcome.) "I was born during the eclipse." "I carry a key I cannot find the
                      lock for."
                    CAPABILITY true: "I can speak with the dead." -> offered as "the dead spoke
                      to you once, and you have not been the same" (fact), or the aspiration
                      [deed.primal.spirits], or the Touched livelihood (the sight).
                    WORLD true: "I am the last heir of the old kings." -> a belief; the Oracle
                      decides and seals whether it is so; the hook asks who else believes it.
                    non-example: "I am the strongest man in the valley." -> a comparison is an
                      outcome of contests not yet held; Might +3 is how one is strong.
Anchor:             yes, for any later moment when a player proposes a fact about their own
                    character's past ("as a child I worked these docks"). Intent verbs: "I have
                    always", "back when I", "I am the only". Knobs: none beyond the two flags; the
                    same outcomes apply (fact, belief with sealed truth, or redirect). Covers:
                    facts about the PC's own person, ties and past. Does not cover: facts about
                    the present scene (the Oracle, 00.12.7).
Basis:              [13th Age: One Unique Thing is narrative, never a mechanical grant,
                    R: https://roll20.net/compendium/13thage/Rules:Creating%20Characters; R1 M-28;
                    R2 02: an innate rule-breaker must be narrow, and is better earned later]
                    [C:VII] [SG-05] [SG-06] [00.6.7] [DL-02-17]
```

**02.9.5 Faction ties.** `[D]` A new character may be known to institutions. The player picks one
**bracket**; nothing is traded between brackets and there is no pool:

| Bracket | Ties | Meaning |
|---|---|---|
| **none** | — | no institution knows you |
| **a foot in the door** | one tie at **+1 Warm** | an organization of one kind treats you as one of its own, loosely |
| **sworn and hunted** | one tie at **+2 Friendly** and one at **−2 Unfriendly** | you belong somewhere in earnest, and that has made you an enemy |

A tie names an **organization kind** (a level-2 `org.*` tag: each upbringing and livelihood suggests
two), not a faction. Chapter 13 maps the kind to a faction of its region and chapter 11 writes the
faction's status toward the PC (the standing scale, 00.3.16; 00.17.1 Q13: its members' default standing
is that status). If the region has no faction of that kind, the tie is held open (02.9.8). An
**Acolyte's** tie to their keeper's faith at Warm is required by 02.5.5 and *is* their foot in the
door; they may make it sworn and hunted. A tie is standing, never rank: a rank is chapter 11's to
grant, in play [13th Age spreads three points across relationships with the setting's powers,
positive, conflicted or negative: R: https://roll20.net/compendium/13thage/Rules:Creating%20Characters;
R1 M-28; C:P11; DL-02-17].

**02.9.6 Name and look.** `[N]` + `[D]` The player gives the character a **name** (or asks for one from
chapter 13's name table for the people: the engine offers three) and states the character's **pronouns**;
the engine never rolls a PC's pronouns and the narration never uses one the player did not give
(P13's first data point was an unearned pronoun). **Look** and **age** are optional sentences recorded
as shown facts (`pc.look`, `pc.age_band`: young, grown, old); they have no mechanical weight and
narration may not derive any from them.

**02.9.7 Hooks.** `[D]` A hook is a seed the living world may grow. Creation writes each as a record
handed to chapter 11, which owns hooks' lifecycle (seeded → active → resolved, expired or retired) and
gives each activated hook its three clue placements and its fallback (BRIEF A2 #11):

```yaml
CreationHook:
  id: str                 # hook.pc.<n>
  kind: enum              # thread | rumor | npc | place | debt | enemy | question
  text: str               # the origin's line, or the player's own words
  source: str             # orig.people.* | orig.up.* | orig.life.* | drive | bond.<npc id> | true_thing | faction_tie
  entities: [id]          # the bond NPC, a faction, a place; empty until chapter 13 or 11 binds them
  tags: [tag]             # the origin's tags, the aspiration's or drive's tags
  state: seeded
```

Which hooks a new character has: **one from each origin** (the player picks one of the entry's two
lines, default the first: three hooks); **the drive**, if a want (one thread hook); **each bond** (one
hook each: an `npc`, or the kind the bond's row states); **the one true thing**, if stated (one); **a
faction tie at −2**, if taken (one `enemy`). That is five to eight seeds. Origin lines use the
micro-format `"<kind>: <text>"` in `data/origins.yaml`. Creating a hook writes nothing else: the people
and places a hook mentions come into being when chapter 11 or 13 binds it, and until then the hook is
`available` to the player as text and commits the world to nothing more specific than its text
[R1 #10 hook lifecycle; R1 02: creation should output story hooks; R5 P-39 (Beyond the Wall: each
creation step adds an NPC or a place to the world); R6 §B].

**02.9.8 Open slots.** `[D]` A player need not fill every slot of C8 before play. On the fast path the
thorn bond, the one true thing, the faction tie and (unless the drive answer named one) the aspiration
start **open**; on any path the player may leave any of those four open. An open slot is filled later, **out of fiction, at a
reflection or a session start**, by the same rule that would have filled it at creation, with one
added limit that keeps a late answer from being a lever on the scene in front of the player:
- a bond filled late creates a **new** NPC, never one already in the cast, and chapter 13 or 11 places
  them at least one scene away;
- a faction tie filled late may name only a faction the PC has **not yet dealt with**;
- a true thing filled late passes 02.9.4 and may not concern any entity in the current scene.
Handler `h.02.open_slots` (`reflection`, phase 9) queues at most one reminder per session ("You still
have an unnamed rival and a true thing to tell me, whenever you like"), and none once the player says
to stop. An open slot is never filled by default and never by the DM [R5 §4 item 6: "the remaining
choices deferred until they first matter"; Dungeon World: "draw maps, leave blanks"; SG-06; DL-02-18].

### 02.10 Preferences

**02.10.1 What creation asks.** `[D]` Session zero is chapter 14's (tone, the lethality promise, lines
and veils, flags, auto-commit; 12.5.1). Creation's step C0 runs it and records four more answers
through chapter 14's preference record, because they are best asked while a character is being made:

| Preference | Asked as | Values | Default | Used by |
|---|---|---|---|---|
| `creation.path` | "Quick start, the full workshop, or a ready-made character?" | fast, full, ready_made | fast | this chapter |
| `player.new_to_this` | "Have you played a game like this before?" | yes, no | no → treated as new | 12 (first-use notes), 14 |
| pillar weights (the first check-in, 12.5.9) | "Which of these sounds most like fun: fights, exploring, talking your way through, working out mysteries, long journeys, building something between adventures? Pick up to two; anything you'd rather have less of?" | more / same / less per pillar | all same | 12.9.3 |
| `pacing.profile` (full path only) | "Steady, gentle, or relentless?" | standard, gentle, relentless | standard | 12.7.3 |

No answer changes a number, an odds or a cost anywhere (12.5.9). Every question may be skipped [R1 02 session zero, Robin's Laws; 12.5.9; DL-02-19].

**02.10.2 What creation hands on.** `[D]` At C9 the engine gives chapter 12's rotation ledger the
character's first **facets** (02.11.3), gives chapter 14's codex the sheet, and writes the SITUATION
block's first "you said" line from the drive ("Last time you said: <the drive>", 12.15.11), so the
first session opens pointed at what the player told the game they wanted.

### 02.11 What creation writes, and what it does not

**02.11.1 No evidence at creation.** `[D]` Ordinary creation writes **no** evidence event and leaves
every tally at zero. Every origin entry declares `backstory: []`. A character's past is expressed as
**capability** (competence, licenses, a technique), **possessions**, **facts** and **ties**; identity is
left to deeds resolved in play.
*Why, when chapter 03 offers optional backstory evidence (03.2.8, DL-03-25).* (1) Constitution P5 and
P2 route identity and power through "what a character actually did"; an origin line is a statement, not
a resolved deed, and everywhere else in this ruleset evidence, loot and grants fire only on resolved
outcomes (00.6.8; 00.11.2). (2) A seed of 24 points on tags the player picked from a list is a small
menu choice of calling: exactly the shape P5 exists to avoid. (3) It is not needed: the past already
pays, as +2 and a license from the first roll; the aspiration already puts the player's intended
direction in the Leanings view; and a focused character reaches a first recognition at about the fourth
session without it (04's pacing: median session 4), which is where a newcomer's first earned title
should fall. (4) The one case where a past *was* played is the trained successor, and there the
mechanism is used (02.2.7 item 4). [C:P5; C:P2; R3 02.3 considered seeding tallies; DL-02-14]

**02.11.2 The prologue.** `[D]` + `[N]` So that the world can speak of the character's past, the engine
appends three to five lines to the chronicle (`chronicle_append`, dated before play, tagged `prologue`),
built from the origins' descriptions, the bonds and the birth account: "Raised at a hunter's steading
in the high forest." "Took her first deer with her mother's bow." "Left when the wardens came." These
are the lines an NPC, a rumor or a recognition vehicle may later cite. They are chronicle, not evidence,
and the narrator may add color to them only at the player's word.

**02.11.3 Facets.** `[D]` Creation creates these entries in chapter 12's rotation ledger (12.9.1), all
**untested**: each training license and each tongue; each tag held deep (a specialty); the gifted
technique; the knack's tag; the three chosen origin hooks; the drive; each aspiration; each bond; the
one true thing; each faction tie. Chapter 12 treats an untested facet as overdue four scenes after its
acquisition (12.9.2), so the first session is built, by rule, out of what the player chose
[R1 #8; R1 12.B].

---

## Procedures

Every procedure is run by the DM with the engine's tools. Creation happens out of fiction, before
`session_start`'s first scene; it advances no fictional time.

**PR-02-1 The full path.** `[D]` (with the `[J:*]` decisions of the rules cited)
0. **C0 Preferences.** Run chapter 14's session zero; ask 02.10.1's questions; record.
1. **C1 Livelihood.** Show the first seven livelihoods and "more"; or classify the player's sentence
   (02.2.4). The player confirms one. Keep everything else in their sentence for C8.
2. **C2 People.** Show the peoples available in the region (chapter 13), each with its one-line
   trade-off (T-02-2). If not human: ask "typical of your kind (+7, three placements decided) or
   uncommon (+5, free)?" (02.3.2, 02.3.4), showing both arrays.
3. **C3 Upbringing.** Show the nine (T-02-4), the livelihood's default marked. Resolve its license
   choice and tongue pick, if any.
4. **C4 Attributes.** Show the three shapes for the rule in force, and the default placement (02.3.5)
   as a starting point. The player rearranges; the engine validates each change (02.3.3) and shows what
   follows from it: Vitality, Guard with the default kit, dread threshold, learning picks.
5. **C5 Trainings.** Show the four profiles (02.5.2) and the livelihood's list. The player picks the
   profile, the tags (one may be off-list), which are held deep, and on Gifted the technique (02.5.4:
   the engine lists the eligible abilities with their literal text and Focus cost). A magic livelihood
   picks its school first (02.5.5). Then the human's extra training (02.4.3) and the learning picks
   (02.5.6). The engine resolves duplicates (02.5.7).
6. **C6 Birth.** Ask once: "Was anything said about your birth, or about your early years?" Classify
   the manner (02.6.4). Run PR-02-4. Tell the results (02.6.8).
7. **C7 Numbers and kit.** The engine computes Vitality, Focus, fate (02.7). Show the two kits; the
   player makes any kit choice and exchange (02.8.1).
8. **C8 Ties.** The drive (02.9.1); two bonds (02.9.2); one or two aspirations (02.9.3); the one true
   thing (02.9.4); the faction-tie bracket (02.9.5); one hook line from each origin (02.9.7). Any of
   the thorn, the true thing and the tie may be left open (02.9.8).
9. **C9 Name, look, confirm.** Name and pronouns (02.9.6). Run PR-02-6.

**PR-02-2 The fast path.** `[D]` Five exchanges (the script is PR-02-7):
1. Taste, limits, path (C0). 2. Who you are (C1; plus C2 only if the player names a people).
3. What you want (the drive, C8). 4. Who matters (the anchor bond, C8). 5. Your name (C9).
Between exchange 4 and 5 the engine applies every default of 02.2.2 for C2–C7 and the rest of C8,
runs PR-02-4 with the default manner, and then runs PR-02-6. The player may say "details" at any
exchange to open that step as PR-02-1 does, and return.

**PR-02-3 A ready-made character.** `[D]`
1. Show chapter 13's pregens: for each, the name, one sentence, what they are good at, and what they
   want. 2. The player picks one; may rename it. 3. Load the pregen's record (it has passed PR-02-9).
4. Run PR-02-4 live (02.2.5). 5. Run PR-02-6. The creation window applies.

**PR-02-4 The birth draw.** `[D]` (`generate`, domain `gen.birth`; the steps are 00.11.3's)
1. **Source tags** = the people's `birth_pool` ∪ the upbringing's ∪ the livelihood's; for a Touched
   character, plus the named school tag, or all seven primal school tags if unnamed.
2. **Circumstance** = the manner (02.6.4). **Degree** = `none`.
3. **Pool gate:** keep entries with a `gate_tags` member equal to, or an ancestor of, a source tag
   (00.5.4 c). **Tier gate:** all entries are tier 1; a new character's band is 1: all kept.
4. **Rung and slots:** `plain` (knack, quirk) or, for `gifted`, `marked` (gift, knack, quirk).
5. **Fill**, slot by slot, each from its layer: gift first (the one gated-in entry; if several, an
   equal-weight draw), then knack, then quirk. Weight = the entry's `weight`, ×3 if the fill is `biased`
   and the entry carries the bias tag, ×½ if the entry was produced in the domain's last five draws
   (successors). The engine draws with RC-RNG and logs pool size, total weight and the roll.
6. **Write:** for each result, `apply_effect` for its effect references as a permanent instance with
   source `gen.birth`; for a gift, also `grant` the training license (`trained`), the competence entry
   (+2), the acceptance fact and the gifted ability (acquired partition, rank 1, `source.kind: gift`).
   Record all in `pc.creation.birth`.
7. **Tell** the player (02.6.8). The log is `available` on request ("how was that decided?").

**PR-02-5 The Bent: offer, accept, defer.** `[T]` + `[D]` (handler `h.02.bent_offer`, `reflection`,
phase 8)
1. If `pc.creation.window ≠ locked`, or `pc.creation.bent` is `accepted` or `forgone`: stop.
2. If an offer is open and unanswered: do nothing (it is re-shown at session start); stop.
3. If the last answer was a deferral and the spacing of 02.6.7 is not yet met: stop.
4. Compute the source tags: every deed branch with ≥ 3 resolved frames whose actor is the PC since
   creation. If none: stop.
5. `generate(gen.birth, pc, bent_first | bent_again, none)`: pool gate by those branches; exclude
   attributes at +3 and struck entries; one equal-weight draw. If the pool is empty: stop (try again at
   the next reflection).
6. `offer_create {kind: other, content: the drawn entry, represent_when: session_start, expires: never}`
   and show, out of fiction, after the reflection's other business:
   ```
   [CHOICE] Your Bent: something in you has settled. Endurance +1, for good (Vitality 12 → 13).
            (a) accept · (b) defer: this one is gone for you; another comes later, from what you
            have been doing by then (you may defer twice in all; this is the first time)
            No default: nothing changes until you choose.
   ```
   On the third draw (b) reads "forgo: no Bent, ever".
7. **Accept:** `apply_effect(eff.02.bent, {attribute, amount: 1})`; `pc.creation.bent = accepted`;
   owners recompute derived values. **Defer:** strike the entry; `deferrals += 1`; record the
   reflection count and frame count for 02.6.7. **Forgo** (third draw only): `pc.creation.bent =
   forgone`.

**PR-02-6 Finishing: validate, write, show.** `[D]`
1. **Validate** the whole record against the character tests of PR-02-9. On a failure, name it and
   return to that step.
2. **Write**, in this order, each with reason `creation`: `create_entity(kind pc)` with name, tags,
   attributes, pronouns; the floor and each deep competence entry; `grant` each license (tongues with
   grade; letters; the people gift; trainings at `trained`) and the gifted technique; `apply_effect`
   for the gift's effect, the knack and the quirk; `update_quantity` to set Vitality, Focus and fate;
   `create_entity` for each kit item, and coin; `set_fact` for the origin facts, the true thing, a
   magic livelihood's facts, look and age; the drive's commitment; for each bond, the NPC (12.11.1),
   `set_relationship`, and any commitment; aspirations; faction-tie seeds and hooks to chapter 11;
   prologue lines (`chronicle_append`); facets to chapter 12; `pc.creation` with `window: open`.
3. **Show the sheet** (format below) and the three first-use notes if `player.new_to_this` (PR-02-7).
4. Hand over to chapter 13's opening (`mark_boundary(session_start)` if not yet marked).

```
[SHEET] <Name> (<pronouns>) — <People> · <Upbringing> · <Livelihood>
  Might +3 · Agility +1 · Endurance +2 · Wits 0 · Intellect −1 · Presence 0 · Resolve 0
  Vitality 14/14 · Focus 4/4 · fate 1 · Guard 14 · dread 0 of 8
  Good at (+2): <deep tags, plain names>      Also trained: <access tags>
  Technique: <name — its literal text, cost>  (if any)
  From birth: <knack, plain> · <quirk name>   Gift: <people gift>
  Speaks: <tongue (grade), …> · <reads | cannot read>
  Carries: <items, plain> · <n> coin
  Wants: "<drive>"   Hopes to become: <aspiration>   Matters: <bond (kind)>
  Still open: <open slots>   · You may adjust your choices once before your first night's rest.
```

**PR-02-7 The creation conversation.** `[D]` + `[N]` The DM speaks out of fiction throughout, in plain,
warm sentences, never in a character's voice and never as a form to fill in. The fixed parts are the
`[CREATE n/N]` blocks: the DM may reword the sentence above a block, and must keep the block's options,
their order, the default line and the count. One block per message; the block is always last
(12.15's order: a pause block ends the message). Rules are not explained unless asked, except the three
first-use notes at the end. The fast-path script, in full:

*Message 1 (opening).*
```
Welcome. This is an adventure told in words. You say what your character does, in your own words,
and I tell you what happens. There is no menu and no wrong way to ask. I keep the rules, and when
the dice matter I show you the odds before you commit. Your character can die, but never without
a plain warning and a choice first.

[CREATE 1/5] Before we begin
  (a) What would you like plenty of? Up to two: fights · exploring · talking your way through ·
      mysteries · journeys · building something of your own. Anything you'd like less of?
  (b) Is there anything you would rather never see in the story, or only off-stage?
  (c) Quick start (five questions, a few minutes), the full workshop, or a ready-made character?
  If you move on without choosing: a bit of everything · nothing ruled out (you can say so at any
  time) · quick start
```
*Message 2.*
```
[CREATE 2/5] Who are you?
  Pick a life your character led before this story, or describe them in a sentence and I will
  find the nearest.
  (a) Soldier — levy, guard or sellsword         (b) Hunter — forester, trapper or poacher
  (c) Thief — burglar, cutpurse or smuggler       (d) Healer — herbalist, midwife or barber-surgeon
  (e) Apprentice — a sorcerer's pupil             (f) Performer — minstrel, player or storyteller
  (g) Wanderer — pilgrim, vagabond or exile       (more) fourteen other lives
  You are human unless you tell me otherwise ("peoples" shows the others).
  If you move on without choosing: Soldier.
```
After the answer the DM confirms in one sentence what the choice means, in fiction-shaped words and no
numbers ("A soldier, then: good with a blade and a shield, strong, hard to put down."), and moves on.

*Message 3.* The three options are the livelihood's `drive_seeds`.
```
[CREATE 3/5] What do you want?
  One sentence: the thing your character wants most, or believes most. Or take one of these:
  (a) "I will never again fight for a cause I cannot name."
  (b) "I owe a death, and I mean to pay it back to the one who is owed."
  (c) "I want a wall of my own to stand on, and people behind it worth the standing."
  If you move on without choosing: (a).
```
*Message 4.* Options: the upbringing's anchor seed, then the livelihood's.
```
[CREATE 4/5] Who matters to you?
  Name one person your character would cross the country for, and what they are to you. Or:
  (a) the wagon-family or company that still counts you one of theirs
  (b) the file-mate who carried you off a field once
  If you move on without choosing: (a).
```
*Message 5.*
```
[CREATE 5/5] What are you called?
  A name, and how I should speak of your character (he, she, they, or as you like).
  Say "suggest" and I will offer three names.
  If you move on without choosing: I will offer three names and wait; a character needs a name.
```
*Message 6 (the result).* Two sentences that tell the birth results as things that were always true
(02.6.8); then the `[SHEET]`; then, for a new player, exactly these three notes; then the last block.
```
[RULES] Say what you do in your own words. You can always ask "what are my options?" or "what do
        I know?" and I will answer plainly.
[RULES] When something is risky I will show you the odds and what failure would cost before you
        commit. You can change your mind then.
[RULES] No roll can kill your character unless I have warned you first, in these brackets.

[CREATE] Ready?  (a) begin · (b) change something (say what, or "details")
         You may also adjust these choices once after you have tried them, any time before your
         character's first night's rest.
         If you move on without choosing: begin.
```
**The full-path prompts** (one block per step; the options come from data; every block ends with its
default line from 02.2.2):

| Step | Block title and question | Options shown |
|---|---|---|
| C1 | `Who are you?` as above | seven livelihoods, then "more" |
| C2 | `Your people.` "Who were you born among?" then, if not human: "Typical of your kind, or uncommon?" | the region's peoples with trade-off lines; the two arrays |
| C3 | `Where did you grow up?` | nine upbringings: Focus, what you learned, your purse |
| C4 | `What are you made of?` "Here is how a <livelihood> usually stands. Move anything you like." | three shapes; the default placement; live Vitality, Guard, dread |
| C5 | `What can you do?` "Deep in two, a trick up your sleeve, well-rounded, or a bit of everything?" | four profiles; the list; eligible techniques with text and cost |
| C6 | `Your early years.` "Was anything said about your birth, or about your childhood?" | free text, or skip |
| C7 | `What you carry.` | the two kits; kit choices |
| C8 | `What you want` · `Who matters` · `Who you hope to become` · `One true thing` · `Who knows you` | seeds from the origins; brackets |
| C9 | `What are you called?` then the sheet and `Ready?` | — |

**PR-02-8 The second look.** `[D]` (02.2.6)
1. The player asks to revise, between scenes, while `pc.creation.window = open` and
   `pc.creation.revised = false`. Otherwise: refuse with the reason and what is still possible (a later
   training by chapter 05's paths; Retrain, chapter 15).
2. Show the sheet. The player states every change. Validate each as at creation.
3. Apply as one batch of writes with reason `second_look`; re-issue only untouched kit items; never
   re-run PR-02-4; set `pc.creation.revised = true`.
4. If any shown fact that narration has used changed (a bond's name, the drive), issue one
   `[CORRECTION]` (12.15.9) so the record and the story agree.

**PR-02-9 Authoring and auditing an origin, a kit or a pregen.** `[D]` Run by the data loader
(RC-DATA) on every entry, and by chapter 13's author on every pregen. An entry or record that fails
any test is rejected.

| # | Test | Applies to |
|---|---|---|
| 1 | every tag, license, ability and effect id exists in its data file | all |
| 2 | attributes: each −1…+3; the multiset is one of the six arrays; Typical placements obey the people's floors and fixed low | people, pregen |
| 3 | a people has exactly one floor of +2, one of +1, one fixed −1, on three different attributes; or none of them (Free) | people |
| 4 | a people grants at most one gift; the gift's effects are one effect reference whose magnitude is no larger than: one lever in a stated circumstance, an edge of +1 on at most two verbs, a hazard step of one rung, or the waiver of one named snag or restriction | people |
| 5 | an upbringing spends exactly 3 units (02.4.4); Focus is 3, 4 or 5 | upbringing |
| 6 | a livelihood lists 5–8 level-2 deed tags; its default picks are on its list and match its default profile; its default technique has `min_tier: 1` and its first tag lies under the default deep pick | livelihood |
| 7 | a magic livelihood names one branch, lists only that branch's schools, each school has a `min_tier: 1` spell, and its `requires_satisfied_by` names the fact or item that satisfies 05.9.4 | livelihood |
| 8 | competence granted: none above +2; none outside a level-2 deed tag; at most two tags above the floor | livelihood, pregen |
| 9 | nothing in 02.1.3 is granted | all |
| 10 | a kit obeys 02.8.2 | kit, pregen |
| 11 | bond seeds: the first is an anchor kind, the second a thorn kind; hook lines use the micro-format with a listed kind | upbringing, livelihood |
| 12 | `backstory` is empty | all |
| 13 | a pregen has: three origins; a legal profile; a drive; an anchor bond bound to a region NPC; one aspiration with tags; and no birth results (they are drawn live) | pregen |

Tests 1, 3 (as "each attribute is some people's fixed low exactly once"), 5, 6, 7, 10 (tags and
qualities) and 11 were run by `gen02.py` on the shipped data: all pass.

---

## Tables

`data/origins.yaml`, `data/gen_birth.yaml` and `data/kits.yaml` are canonical for every id and number
(00.1.4 item 5). The tables below are rendered from those files by the scratchpad script `tables02.py`
(T-02-2 to T-02-10, T-02-13) or computed by `gen02.py` (T-02-3, T-02-11, T-02-15), so they cannot drift
from the data. Tables embedded in Rules are indexed here: the arrays (02.3.1), the Typical placements
(02.3.2), the upbringing budget (02.4.4), the profiles (02.5.2), the magic livelihoods (02.5.5), the
layers of birth (02.6.1), bond kinds (02.9.2), faction-tie brackets (02.9.5), preferences (02.10.1).

**T-02-1 What a new character has: the numbers other chapters read.**

| Quantity | Value at creation | Rule | Read by |
|---|---|---|---|
| Attribute values; sum | each −1…+3; **+5** (Free) or **+7** (Typical); one −1 always; at most one +3 | 02.3.1 | 01, 06, 07, 09 |
| Competence floor | **+1** at `deed` (confirmed) | 02.5.1 | 01, 03, 04 |
| Origin competence | **+2**, on at most **two** level-2 deed tags | 02.5.2 | 01, 04 (tier 1 is +3 or +2) |
| Best check modifier | +5 (attribute +3, deep +2); **+6** only with a knack on that tag | 02.6.2 | 00.3.7 band 1 (+4…+6) |
| Training licenses held | 1 to 11, all at grade `trained` | 02.5.3 | 05, 12 (facets) |
| Abilities held | 0, or **1** at rank 1 in the acquired partition | 02.5.4 | 05 |
| Vitality | **12 + Endurance** = 11…15 (base; 10…16 over a lifetime) | 02.7.1 | 06, 07, 09 |
| Focus base | **3, 4 or 5** by upbringing; never changes | 02.7.2 | 05 |
| fate | **1** | 02.7.3 | 01, 07 |
| Power band | 1 | 04 | 09 |
| Dread; threshold | 0; 8 + Resolve = 7…11 | 07.11 | 07 |
| Guard | 10 + Agility + (1 or 2) + (1 with a shield) = **10…16** | 06.4.1 | 06, 09 |
| Edge from birth | +1 on one level-2 deed tag (the knack) | 02.6.2 | 01 (edge cap +2), 08 (item edges share the cap) |
| Bonds; faction ties | 1 or 2 NPCs at set standing; ties +1, or +2 and −2 | 02.9.2, 02.9.5 | 11, 12, 15 |
| Hooks seeded | 5 to 8 | 02.9.7 | 11 |
| Coin | 3 to 55 | 02.8.2 | 08 |
| The Bent | +1 to one attribute, offered after creation, never above +3 | 02.6.5 | 00.4.3 a, 07 (Vitality) |

**T-02-2 Peoples.** (`origins.yaml`, `kind: people`; gifts in `data/licenses.yaml owner-block 02`)

| People | Rule | Must hold | Fixed | Gift (license; literal effect) | Tongues | Birth-pool branch |
|---|---|---|---|---|---|---|
| **Human** | Free +5 | — | — | **Adaptable**: one extra training held as access (02.4.3) | Common tongue (native) | — |
| **Elf** | Typical +7, or Free +5 | Agility ≥ +2, Wits ≥ +1 | Endurance −1 | **Starsight**: dim light is no hindrance to your sight (night-sight for 06.3.7's dim rule) | Elvish (native), Common tongue (accented) | `deed.lore` |
| **Dwarf** | Typical +7, or Free +5 | Endurance ≥ +2, Resolve ≥ +1 | Agility −1 | **Stonesense**: underground you always know down, depth and the way back; Precision lever on Observe and Recall about worked stone, mines, tunnels, caves | Dwarvish (native), Common tongue (accented) | `deed.craft` |
| **Halfling** | Typical +7, or Free +5 | Agility ≥ +2, Resolve ≥ +1 | Might −1 | **Underfoot**: Precision lever on Sneak while a crowd or a larger creature is between you and the watcher | Common tongue (native); one more of choice (accented) | `deed.influence` |
| **Orc-kin** | Typical +7, or Free +5 | Might ≥ +2, Resolve ≥ +1 | Intellect −1 | **Iron blood**: hazards of venom and disease count one severity rung lighter | Orcish (native), Common tongue (accented) | `deed.martial` |
| **Goblin-kin** | Typical +7, or Free +5 | Wits ≥ +2, Agility ≥ +1 | Presence −1 | **Cave-eyes**: in darkness you see to `band.close` as others see in dim light | Goblin (native), Common tongue (accented) | `deed.guile` |
| **Giant-kin** | Typical +7, or Free +5 | Might ≥ +2, Endurance ≥ +1 | Wits −1 | **Great frame**: +1 edge on Force and Grapple | Giantish (native), Common tongue (accented) | `deed.martial` |
| **Beastfolk** | Typical +7, or Free +5 | Wits ≥ +2, Agility ≥ +1 | Resolve −1 | **Keen nose**: Precision lever on Observe by scent | Kin-speech (native), Common tongue (accented) | `deed.wilds` |

Every people also carries two hooks and its `creature.folk.*` tag. A non-human may take the Free rule
(02.3.4) and keeps everything in this table except the "must hold" and "fixed" columns.

**T-02-3 The quantity-against-freedom audit.** For sixteen classic concepts, the best weighted
attribute score attainable under the Free rule and under each people's Typical rule (any shape). The
weights model a solo character: every attribute is worth 1 (one person meets every kind of check); the
four that feed a defense or a pool (Agility, Endurance, Wits, Resolve) are worth 1 more; a concept adds
4, 3 and 2 to its first, second and third attribute. **Bold** beats Free; *italic* trails it.

| Concept (first, second, third attribute) | Free (+5) | Elf | Dwarf | Halfling | Orc-kin | Goblin-kin | Giant-kin | Beastfolk |
|---|---|---|---|---|---|---|---|---|
| warrior (Mig, End, Agi) | 28 | *24* | *27* | *24* | **34** | **32** | **33** | **31** |
| archer (Agi, Wit, End) | 31 | *29* | *22* | **37** | 31 | **37** | *25* | **35** |
| rogue (Agi, Wit, Pre) | 30 | **34** | *21* | **35** | **31** | **31** | *23* | **34** |
| scholar (Int, Wit, Pre) | 27 | **30** | **29** | **30** | *20* | **28** | *20* | **31** |
| wizard (Int, Wit, Res) | 28 | **31** | **31** | **32** | *22* | **34** | *22* | *27* |
| priest (Pre, Res, Wit) | 28 | **31** | **31** | **32** | **30** | *24* | *25* | *24* |
| druid (Res, Wit, End) | 31 | *29* | **35** | **35** | **33** | **37** | *25* | *22* |
| bard (Pre, Agi, Wit) | 28 | **33** | *24* | **34** | 28 | *24* | *25* | **33** |
| envoy (Pre, Wit, Int) | 27 | **30** | **29** | **30** | *26* | *22* | *20* | **31** |
| smith (Mig, Int, End) | 26 | *25* | **31** | *21* | *25* | **28** | **31** | **27** |
| scout (Wit, Agi, End) | 31 | *29* | *26* | **37** | 31 | **37** | *21* | **35** |
| brawler (Mig, End, Res) | 28 | *24* | **33** | *24* | **34** | **30** | **33** | *27* |
| knight (Mig, Pre, End) | 26 | *25* | **31** | *21* | **32** | *25* | **31** | **27** |
| shaman (Res, Pre, Wit) | 29 | **32** | **32** | **33** | **31** | *28* | *26* | *20* |
| thief (Agi, Wit, Int) | 30 | **34** | *21* | **35** | *29* | **35** | *23* | **34** |
| captain (Pre, Mig, Wit) | 26 | **29** | **27** | *25* | **32** | *21* | *25* | **31** |
| **mean difference from Free** | | +0.9 | −0.2 | +1.9 | +0.9 | +1.2 | −2.9 | +0.9 |
| **best / worst difference** | | +5 / −4 | +5 / −9 | +6 / −5 | +6 / −7 | +6 / −5 | +5 / −10 | +5 / −9 |
| **concepts better / equal / worse than Free** | | 9 / 0 / 7 | 10 / 0 / 6 | 11 / 0 / 5 | 8 / 3 / 5 | 10 / 0 / 6 | 4 / 0 / 12 | 11 / 0 / 5 |

Reading: every people's Typical rule is better than Free for some concepts and worse for others; none
is best everywhere; the mean premium for accepting three decided placements is about one point, which
is what the human's extra training is set against. Giant-kin are the extreme case: five points better
than Free as a warrior, brawler, smith or knight, and worse at everything that needs quick wits, so a
giant-kin with another calling in mind takes 02.3.4. The audit is a design check, not a rule: no
number in it is used in play.

**T-02-4 Upbringings.** (`origins.yaml`, `kind: upbringing`; packs in `kits.yaml`)

| Upbringing | Raised in | Focus | Licenses (held as access) | Letters | Tongues | Purse | Birth-pool branches | Organization kinds |
|---|---|---|---|---|---|---|---|---|
| **Wilds-raised** | a steading, a hunter's camp or a hermit's hut, far from any road | **4** | survival; one of foraging / tracking / animals | no | — | poor, 5 coin | wilds, martial | clan.family, order.hunters |
| **Village-raised** | a farm, a mill or a cottage, among people who have known you since birth | **4** | animals; one of cookery / woodcraft / textiles / building / leathercraft / smithing | no | — | poor, 8 coin | craft, wilds | clan.family, faith.shrine |
| **Street-raised** | alleys, tenements and markets, fed by whatever the day turned up | **4** | streetwise | no | Cant (accented) | poor, 5 coin | guile, influence | outlaw.thieves, outlaw.smugglers |
| **Guild-quarter raised** | over a workshop or a counting-room, with a ledger always open on the table | **3** | trade; one of smithing / woodcraft / leathercraft / textiles / jewelcraft / cookery / scribing | yes | — | modest, 20 coin | craft, influence | guild.craft, guild.merchant |
| **Court-raised** | a great house, as kin, ward, page or servant, where every word had a second meaning | **3** | etiquette | yes | one of choice (accented) | comfortable, 30 coin | influence, lore | crown.noble, crown.royal |
| **Cloister-raised** | a temple school, a monastery or a hermit-scholar's cell, by bell and by rule | **5** | — | yes | — | poor, 3 coin | lore, craft | faith.temple, order.monastic |
| **Road-raised** | wagons, camps and caravanserais; a different horizon every month | **4** | navigation | no | one of choice (accented) | modest, 12 coin | wilds, influence | company.trading, company.mercenary |
| **Water-raised** | a fishing boat, a river barge or a harbor, wet to the knees since you could walk | **4** | seafaring | no | one of choice (accented) | modest, 12 coin | wilds, martial | company.trading, outlaw.smugglers |
| **Bound service** | a mine, a galley, a debtor's indenture or an orphan-house, until you got out | **5** | one of escape / athletics | no | — | destitute, 1 coin | martial, guile | outlaw.bandits, crown.civic |

Each row spends exactly three units (02.4.4). Each also carries an anchor seed, a thorn seed and two
hooks.

**T-02-5 Livelihoods.** (`origins.yaml`, `kind: livelihood`; kits in `kits.yaml`)

| Livelihood | Training list (level-2 deed tags) | Default profile and picks | Default upbringing | Kit (first option); coin |
|---|---|---|---|---|
| **Soldier** (levy, guard or sellsword) | martial.blade, martial.polearm, martial.axe, martial.shield, martial.armor, martial.tactics, martial.athletics, influence.command | **Focused**: deep blade + shield | Road-raised | leather armor, round shield, dagger, remedies, sword; in place of the sword: spear / hand axe / mace; 5 coin |
| **Hunter** (forester, trapper or poacher) | martial.archery, wilds.tracking, wilds.survival, guile.stealth, wilds.foraging, wilds.animals, martial.thrown, guile.ambush | **Focused**: deep archery + tracking | Wilds-raised | shortbow, arrows ×20, leather armor, dagger, rope and hook, tools of the work, spear; in place of the spear: hand axe; 3 coin |
| **Rider** (squire, courier or outrider) | martial.mounted, wilds.animals, martial.blade, martial.polearm, influence.etiquette, martial.armor | **Focused**: deep mounted + blade | Court-raised | riding horse (worn), padded armor, dagger, sword; in place of the sword: spear; 5 coin |
| **Laborer** (farmhand, miner, docker or porter) | martial.athletics, martial.unarmed, craft.building, wilds.animals, craft.cookery, martial.bludgeon | **Rounded**: deep athletics; access unarmed, building | Village-raised | tools of the work, dagger (worn), food ×2, club; in place of the club: hammer / hand axe; 4 coin |
| **Thief** (burglar, cutpurse or smuggler) | guile.thievery, guile.stealth, guile.escape, guile.streetwise, guile.deception, martial.athletics | **Focused**: deep thievery + stealth | Street-raised | dagger ×2, thieves' tools, rope and hook, cloak, gloves; 6 coin |
| **Charlatan** (gambler, mountebank or go-between) | guile.deception, guile.disguise, influence.insight, influence.persuasion, guile.streetwise, influence.performance | **Focused**: deep deception + insight | Street-raised | dagger, disguise kit, clothing (fine), ring (worn), tools of the work; 10 coin |
| **Sailor** (deckhand, bargee or fisher) | wilds.seafaring, wilds.navigation, martial.athletics, craft.textiles, influence.trade, martial.blade | **Rounded**: deep seafaring; access navigation, athletics | Water-raised | dagger, rope and hook, tools of the work, hand axe; in place of the hand axe: club; 6 coin |
| **Herder** (drover, shepherd or beast-keeper) | wilds.animals, wilds.survival, wilds.navigation, martial.polearm, wilds.foraging, lore.bestiary | **Focused**: deep animals + survival | Village-raised | staff, sling, sling stones ×20, dagger, tools of the work, food ×2; 3 coin |
| **Scholar** (scribe, clerk or tutor) | lore.history, lore.languages, lore.law, craft.scribing, lore.investigation, lore.arcana; grants Letters | **Rounded**: deep history; access languages, investigation | Cloister-raised | dagger (worn), document ×3, tools of the work, light, oil ×2; 8 coin |
| **Healer** (herbalist, midwife or barber-surgeon) | lore.medicine, wilds.foraging, craft.alchemy, influence.insight, lore.bestiary, craft.cookery | **Focused**: deep medicine + foraging | Village-raised | healer's kit, remedies ×3, dagger, pack; 5 coin |
| **Apprentice** (a sorcerer's pupil) | **one school of arcane** (fire, frost, storm, earth, illusion, divination, warding, mind, summoning, necromancy, alteration); lore.arcana, lore.languages, craft.scribing, craft.alchemy, craft.enchanting, lore.history; grants Letters | **Gifted**: deep fire; technique *Flame Lance* | Cloister-raised | document, wand, tools of the work, dagger, staff; in place of the staff: light and oil; 5 coin |
| **Acolyte** (novice, shrine-keeper or lay brother or sister) | **one school of divine** (healing, warding, smiting, rites, oaths, revelation, exorcism, pact); lore.religion, lore.medicine, influence.persuasion, influence.teaching, lore.history | **Gifted**: deep healing; technique *Mend Flesh* | Cloister-raised | holy symbol, document, remedies ×2, dagger (worn), mace; in place of the mace: staff; 4 coin |
| **Hedge-taught** (a cunning-woman's ward or a grove's pupil) | **one school of primal** (growth, beastkin, weather, shapeshifting, spirits, elements, hexcraft); wilds.foraging, lore.medicine, wilds.animals, lore.bestiary, wilds.survival | **Gifted**: deep growth; technique *Root Snare* | Wilds-raised | totem, remedies ×2, dagger, staff, pack; 2 coin |
| **Touched** (born with a power no one taught you) | **one school of primal** (growth, beastkin, weather, shapeshifting, spirits, elements, hexcraft); wilds.survival, guile.stealth, influence.insight, wilds.foraging, martial.athletics | **Gifted**: deep elements; technique *Cinder Stride* | Village-raised | dagger, cloak, charm, light; 3 coin |
| **Merchant** (peddler, factor or caravan hand) | influence.trade, influence.persuasion, influence.insight, wilds.navigation, lore.law, wilds.animals | **Focused**: deep trade + persuasion | Guild-quarter raised | dagger, trade goods ×2, tools of the work, document; 25 coin |
| **Performer** (minstrel, player or storyteller) | influence.performance, influence.persuasion, lore.history, guile.deception, influence.etiquette, martial.athletics | **Focused**: deep performance + persuasion | Road-raised | instrument, clothing (fine), dagger; 8 coin |
| **Courtier** (page, herald or envoy's aide) | influence.etiquette, influence.intrigue, influence.persuasion, lore.law, lore.history, influence.insight | **Focused**: deep etiquette + intrigue | Court-raised | clothing (fine), document, tools of the work, ring, rapier; in place of the rapier: dagger; 15 coin |
| **Artisan** (smith, wright, weaver, mason or jeweler) | craft.smithing, craft.woodcraft, craft.leathercraft, craft.textiles, craft.building, craft.jewelcraft, influence.trade, lore.engineering | **Focused**: deep smithing + trade | Guild-quarter raised | tools of the work, trade goods, dagger (worn), hammer; in place of the hammer: hand axe; 10 coin |
| **Watchman** (constable, reeve's man or gate-warden) | martial.bludgeon, lore.investigation, lore.law, influence.intimidation, guile.streetwise, influence.insight | **Rounded**: deep investigation; access bludgeon, law | Guild-quarter raised | padded armor, light, oil ×2, tools of the work, dagger, club; in place of the club: mace / spear; 5 coin |
| **Tinker** (alchemist's hand, locksmith or trap-maker) | craft.alchemy, craft.artifice, lore.engineering, guile.thievery, guile.poisoncraft, craft.smithing, influence.trade | **Focused**: deep alchemy + artifice | Guild-quarter raised | tools of the work, oil ×2, remedies, dagger, pack; 6 coin |
| **Wanderer** (pilgrim, vagabond or exile) | wilds.survival, wilds.navigation, guile.streetwise, influence.insight, lore.religion, wilds.foraging | **Broad**: deep —; access survival, navigation, streetwise, insight, foraging | Road-raised | staff, dagger (worn), pack, food ×3, remedies; 4 coin |

Level-2 deed tags per branch, for reference: arcane 11, craft 11, divine 8, guile 8, influence 9, lore 9, martial 12, primal 7, wilds 6 (81 in all). Every one appears on at
least one livelihood list or upbringing; any may be the off-list pick (magic schools excepted).

**T-02-6 Default attribute placements** (02.3.5; Peaked shape; humans under the Free rule, the others
under their Typical rule, except the cells marked † which take the Free rule by 02.3.5's caster
exception). Each cell lists Might, Agility, Endurance, Wits, Intellect, Presence, Resolve, in that order.

| Livelihood (priority) | Human | Elf | Dwarf | Halfling | Orc-kin | Goblin-kin | Giant-kin | Beastfolk |
|---|---|---|---|---|---|---|---|---|
| Soldier (Mig End Agi Wit Res Pre Int) | +3 +1 +2 0 −1 0 0 | +3 +2 −1 +2 0 0 +1 | +3 −1 +2 +2 0 0 +1 | −1 +2 +3 +2 0 0 +1 | +3 +2 +2 0 −1 0 +1 | +3 +1 +2 +2 0 −1 0 | +3 +2 +2 −1 0 0 +1 | +3 +1 +2 +2 0 0 −1 |
| Hunter (Agi Wit Mig End Int Pre Res) | +1 +3 0 +2 0 0 −1 | +2 +3 −1 +2 +1 0 0 | +2 −1 +2 +3 0 0 +1 | −1 +3 +2 +2 0 0 +1 | +2 +3 0 +2 −1 0 +1 | +2 +3 +1 +2 0 −1 0 | +2 +3 +2 −1 +1 0 0 | +2 +3 +1 +2 0 0 −1 |
| Rider (Mig Agi Pre End Res Wit Int) | +3 +2 0 0 −1 +1 0 | +3 +2 −1 +1 0 +2 0 | +3 −1 +2 0 0 +2 +1 | −1 +3 +2 0 0 +2 +1 | +3 +2 0 0 −1 +2 +1 | +3 +2 +1 +2 0 −1 0 | +3 +2 +1 −1 0 +2 0 | +3 +2 0 +2 0 +1 −1 |
| Laborer (Mig End Res Agi Wit Pre Int) | +3 0 +2 0 −1 0 +1 | +3 +2 −1 +1 0 0 +2 | +3 −1 +2 +1 0 0 +2 | −1 +2 +3 +1 0 0 +2 | +3 +1 +2 0 −1 0 +2 | +3 +1 +2 +2 0 −1 0 | +3 +1 +2 −1 0 0 +2 | +3 +1 +2 +2 0 0 −1 |
| Thief (Agi Wit Pre Int End Res Mig) | −1 +3 0 +2 0 +1 0 | 0 +3 −1 +2 +1 +2 0 | 0 −1 +2 +3 0 +2 +1 | −1 +3 0 +2 0 +2 +1 | +2 +3 0 +2 −1 0 +1 | 0 +3 +1 +2 +2 −1 0 | +2 +3 +1 −1 0 +2 0 | 0 +3 0 +2 +1 +2 −1 |
| Charlatan (Pre Wit Agi Int Res End Mig) | −1 +1 0 +2 0 +3 0 | 0 +2 −1 +2 +1 +3 0 | 0 −1 +2 +2 0 +3 +1 | −1 +2 0 +2 0 +3 +1 | +2 0 0 +2 −1 +3 +1 | 0 +2 0 +3 +2 −1 +1 | +2 +2 +1 −1 0 +3 0 | 0 +2 0 +2 +1 +3 −1 |
| Sailor (Agi End Mig Wit Pre Res Int) | +1 +3 +2 0 −1 0 0 | +2 +3 −1 +2 0 +1 0 | +2 −1 +3 +2 0 0 +1 | −1 +3 +2 +2 0 0 +1 | +2 +3 +2 0 −1 0 +1 | +1 +3 +2 +2 0 −1 0 | +2 +3 +2 −1 0 +1 0 | +1 +3 +2 +2 0 0 −1 |
| Herder (End Wit Res Agi Mig Pre Int) | 0 0 +3 +2 −1 0 +1 | +1 +2 −1 +3 0 0 +2 | +1 −1 +3 +2 0 0 +2 | −1 +2 +3 +2 0 0 +1 | +2 0 +3 +2 −1 0 +1 | 0 +1 +3 +2 0 −1 +2 | +2 +1 +3 −1 0 0 +2 | +1 +2 +3 +2 0 0 −1 |
| Scholar (Int Wit Pre Res Agi End Mig) | −1 0 0 +2 +3 +1 0 | 0 +2 −1 +2 +3 +1 0 | 0 −1 +2 +2 +3 0 +1 | −1 +2 0 +2 +3 0 +1 | +2 0 0 +3 −1 +2 +1 | 0 +1 0 +2 +3 −1 +2 | +2 0 +1 −1 +3 +2 0 | 0 +1 0 +2 +3 +2 −1 |
| Healer (Int Wit Pre Res End Agi Mig) | −1 0 0 +2 +3 +1 0 | 0 +2 −1 +2 +3 +1 0 | 0 −1 +2 +2 +3 0 +1 | −1 +2 0 +2 +3 0 +1 | +2 0 0 +3 −1 +2 +1 | 0 +1 0 +2 +3 −1 +2 | +2 0 +1 −1 +3 +2 0 | 0 +1 0 +2 +3 +2 −1 |
| Apprentice (Int Wit Res Agi Pre End Mig) | −1 0 0 +2 +3 0 +1 | 0 +2 −1 +2 +3 0 +1 | 0 −1 +2 +2 +3 0 +1 | −1 +2 0 +2 +3 0 +1 | −1 0 0 +2 +3 0 +1† | 0 +1 0 +2 +3 −1 +2 | +2 0 +1 −1 +3 0 +2 | 0 +2 0 +2 +3 +1 −1 |
| Acolyte (Pre Res Wit End Int Mig Agi) | 0 −1 0 +1 0 +3 +2 | 0 +2 −1 +1 0 +3 +2 | 0 −1 +2 +1 0 +3 +2 | −1 +2 0 +1 0 +3 +2 | +2 0 0 +1 −1 +3 +2 | 0 −1 0 +1 0 +3 +2† | +2 0 +1 −1 0 +3 +2 | 0 +1 +2 +2 0 +3 −1 |
| Hedge-taught (Res Wit End Agi Pre Int Mig) | −1 0 +1 +2 0 0 +3 | 0 +2 −1 +2 0 +1 +3 | 0 −1 +2 +2 0 +1 +3 | −1 +2 +1 +2 0 0 +3 | +2 0 +1 +2 −1 0 +3 | 0 +1 +2 +2 0 −1 +3 | +2 +1 +2 −1 0 0 +3 | −1 0 +1 +2 0 0 +3† |
| Touched (Res Agi Wit End Pre Mig Int) | 0 +2 0 +1 −1 0 +3 | 0 +2 −1 +2 0 +1 +3 | 0 −1 +2 +2 0 +1 +3 | −1 +2 +1 +2 0 0 +3 | +2 +2 0 +1 −1 0 +3 | 0 +2 +1 +2 0 −1 +3 | +2 +2 +1 −1 0 0 +3 | 0 +2 0 +1 −1 0 +3† |
| Merchant (Pre Wit Int Res End Agi Mig) | −1 0 0 +2 +1 +3 0 | 0 +2 −1 +2 +1 +3 0 | 0 −1 +2 +2 0 +3 +1 | −1 +2 0 +2 0 +3 +1 | +2 0 0 +2 −1 +3 +1 | 0 +1 0 +3 +2 −1 +2 | +2 0 +1 −1 +2 +3 0 | 0 +1 0 +2 +2 +3 −1 |
| Performer (Pre Agi Wit Int Res End Mig) | −1 +2 0 +1 0 +3 0 | 0 +2 −1 +2 +1 +3 0 | 0 −1 +2 +2 0 +3 +1 | −1 +2 0 +2 0 +3 +1 | +2 +2 0 0 −1 +3 +1 | 0 +3 0 +2 +2 −1 +1 | +2 +2 +1 −1 0 +3 0 | 0 +2 0 +2 +1 +3 −1 |
| Courtier (Pre Wit Int Res Agi End Mig) | −1 0 0 +2 +1 +3 0 | 0 +2 −1 +2 +1 +3 0 | 0 −1 +2 +2 0 +3 +1 | −1 +2 0 +2 0 +3 +1 | +2 0 0 +2 −1 +3 +1 | 0 +1 0 +3 +2 −1 +2 | +2 0 +1 −1 +2 +3 0 | 0 +1 0 +2 +2 +3 −1 |
| Artisan (Mig Int Agi End Wit Res Pre) | +3 +1 0 0 +2 −1 0 | +3 +2 −1 +1 +2 0 0 | +3 −1 +2 0 +2 0 +1 | −1 +2 +2 0 +3 0 +1 | +3 +2 +2 0 −1 0 +1 | +3 +1 0 +2 +2 −1 0 | +3 +2 +1 −1 +2 0 0 | +3 +1 0 +2 +2 0 −1 |
| Watchman (Wit Mig Res Pre End Int Agi) | +2 −1 0 +3 0 0 +1 | +2 +2 −1 +3 0 0 +1 | +2 −1 +2 +3 0 0 +1 | −1 +2 0 +3 0 +1 +2 | +2 0 0 +3 −1 +1 +2 | +2 +1 0 +3 0 −1 +2 | +3 0 +1 −1 0 +2 +2 | +2 +1 0 +3 0 +2 −1 |
| Tinker (Int Agi Wit End Res Pre Mig) | −1 +2 0 +1 +3 0 0 | 0 +2 −1 +2 +3 0 +1 | 0 −1 +2 +2 +3 0 +1 | −1 +2 0 +2 +3 0 +1 | +2 +3 0 +2 −1 0 +1 | 0 +2 +1 +2 +3 −1 0 | +2 +2 +1 −1 +3 0 0 | 0 +2 +1 +2 +3 0 −1 |
| Wanderer (Wit End Res Agi Pre Int Mig) | −1 0 +2 +3 0 0 +1 | 0 +2 −1 +3 0 +1 +2 | 0 −1 +2 +3 0 +1 +2 | −1 +2 +2 +3 0 0 +1 | +2 0 +2 +3 −1 0 +1 | 0 +1 +2 +3 0 −1 +2 | +2 +1 +3 −1 0 0 +2 | 0 +2 +2 +3 0 +1 −1 |

**T-02-7 The seven gifts of the Touched.** (`gen_birth.yaml`, layer `gift`)

| Gift | School (innate license, competence +2) | First working (rank 1, acquired partition) | Its literal text | Focus |
|---|---|---|---|---|
| **Green hand** | `deed.primal.growth` | *Root Snare* (`ab.root_snare`) | Roots and stems seize one target within band.near (it rolls Evade against your effect DC): on a failure it is off-balance until the end of its next turn and grabbed by the growth until it breaks free or the scene ends. | 1 |
| **Beast-tongue** | `deed.primal.beastkin` | *Beast Speech* (`ab.beast_speech`) | For the scene you may Talk with beasts within band.close and understand their answers, and you hold a Precision lever on Talk and Handle beats with them. | 0 |
| **Wind-called** | `deed.primal.weather` | *Gust* (`ab.gust`) | A blast of wind strikes up to two targets within band.near in a line from you (each rolls Endure (Might) against your effect DC): on a failure each is pushed one band away and knocked prone. | 1 |
| **Skin-turner** | `deed.primal.shapeshifting` | *Claws* (`ab.claws`) | For the scene your unarmed Strikes deal cutting harm one severity rung heavier (base Moderate), +1. | 1 |
| **The sight** | `deed.primal.spirits` | *Spirit Tongue* (`ab.spirit_tongue`) | For the scene you perceive the spirits present at this place and may Talk with them. | 0 |
| **The spark** (fire) | `deed.primal.elements` | *Cinder Stride* (`ab.cinder_stride`) | For 3 rounds your Strikes deal fire harm in place of their own type, +1. | 1 |
| **The spark** (water) | `deed.primal.elements` | *Undertow* (`ab.undertow`) | Water rises around one being within band.near (it rolls Endure (Might) against your effect DC): on a failure it takes Light crushing harm, is dragged one band toward the water and knocked prone. | 1 |
| **The spark** (earth) | `deed.primal.elements` | *Heave* (`ab.heave`) | The ground under one being within band.near bucks and heaves (it rolls Evade against your effect DC): on a failure it takes Light crushing harm, is knocked prone and is slowed until the end of its next turn. | 1 |
| **The spark** (air) | `deed.primal.elements` | *Stolen Breath* (`ab.stolen_breath`) | Pull the air from the lungs of one breathing being within band.near (it rolls Endure (Endurance) against your effect DC): on a failure it takes Moderate harm from lack of air and is choking until the end of its next turn. | 1 |
| **The eye** | `deed.primal.hexcraft` | *Evil Eye* (`ab.evil_eye`) | One being within band.near that can see you rolls Endure (Resolve) against your effect DC: on a failure it is weakened and distracted until the scene ends. | 1 |

**T-02-8 Birth quirks.** (`gen_birth.yaml`, layer `trait`; total weight 40. A lever granted by a quirk
is an ordinary lever: it cites the quirk as its fact, counts toward the two-lever limit, and applies
only when its stated circumstance is recorded in the scene.)

| Quirk | What the player is told | Effect reference | Weight | Tripled by manner |
|---|---|---|---|---|
| **Iron stomach** | Spoiled food, bad water and swallowed poisons trouble you less. | `eff.hazard_step` −1 rung; harm.venom.poison; when the hazard is eaten or drunk | 2 | hard |
| **Cold-hardy** | Cold weather counts one rung lighter for you. | `eff.hazard_step` −1 rung; harm.frost.cold; when hazard | 2 | hard |
| **Heat-hardy** | Heat and thirst count one rung lighter for you. | `eff.hazard_step` −1 rung; harm.fire.heat; when hazard | 2 | hard |
| **Long wind** | You keep going: a Precision lever when you run, swim or march far. | `eff.grant_lever` precision; verbs exert, endure, move; when the method is sustained effort over an interval or more | 2 | hard |
| **Light sleeper** | You wake at a wrong sound: a Precision lever to notice anything while you rest or sleep. | `eff.grant_lever` precision; verbs observe; when you are resting or asleep | 2 | hard |
| **True north** *(only if the pool holds wilds or road or water)* | You always know which way you came: a Precision lever to keep or recover a heading. | `eff.grant_lever` precision; verbs observe, handle, recall; when the intent is to keep, find or retrace a route | 3 | — |
| **Sure feet** | Ice, wet stone and narrow beams trouble you less: a Protective lever on treacherous footing. | `eff.grant_lever` protective; verbs exert, move, evade; when the footing is recorded as treacherous | 2 | — |
| **Cat's fall** | You fall well: a Protective lever on any check where the stake is a fall. | `eff.grant_lever` protective; verbs exert, move, evade; when the declared failure is a fall | 1 | — |
| **Strong grip** | What you hold stays held: a Precision lever to keep a grip on a ledge, a rope, a weapon or a person. | `eff.grant_lever` precision; verbs grapple, exert; when the intent is to keep hold of something already held | 2 | — |
| **Keen ears** | A Precision lever to notice or place a sound. | `eff.grant_lever` precision; verbs observe; when the method is listening | 2 | — |
| **Far sight** | A Precision lever to make out anything at band.far or beyond. | `eff.grant_lever` precision; verbs observe; when the thing observed is at band.far or band.distant and in the light | 2 | — |
| **Steady hands** | A Precision lever on small, exact work with the fingers. | `eff.grant_lever` precision; verbs handle; when the method is fine work on something smaller than a hand | 2 | — |
| **Head for numbers** | A Precision lever to reckon a tally, a price, a measure or the odds. | `eff.grant_lever` precision; verbs recall, observe; when the question is a count, a sum, a price or a measure | 2 | — |
| **Memory for faces** | A Precision lever to place a person you have seen before, however changed. | `eff.grant_lever` precision; verbs recall, observe; when the question is whether, where or when you have seen this person | 2 | — |
| **Honest face** | Strangers believe you when you are telling the truth: a Precision lever on a truthful Talk to someone who has never met you. | `eff.grant_lever` precision; verbs talk; when what you say is true by the record, and the listener is at first meeting | 2 | — |
| **Forgettable face** | A Precision lever to go unremarked in a crowd or to be misdescribed afterwards. | `eff.grant_lever` precision; verbs sneak; when the method is blending into a crowd of ordinary people | 2 | — |
| **Carrying voice** | You are heard at the back: an Amplifying lever when you speak or sing to a crowd. | `eff.grant_lever` amplifying; verbs talk; when the audience is a crowd or a company | 2 | — |
| **Animal ease** | Beasts settle near you: a Precision lever to calm or approach an animal that is not hunting you. | `eff.grant_lever` precision; verbs handle, talk; when the target is a beast that is not attacking | 2 | — |
| **Weather-ache** | An old ache tells you tomorrow's weather: at each dawn you learn the day's rolled weather. | `eff.reveal` the weather rolled for the coming day (ch.10), at each day boundary | 1 | hard, omened |
| **Prickling neck** | You feel it when eyes are on you: a Precision lever to notice that you are being watched or followed. | `eff.grant_lever` precision; verbs observe; when the question is whether someone is watching or following you | 1 | omened |
| **Cold calm** | Fear arrives late in you: a Precision lever to Endure fear. | `eff.grant_lever` precision; verbs endure; when the effect resisted would apply cond.frightened or dread | 1 | omened |
| **Dreamer** | Your dreams keep what your waking mind lost: once after each long rest, a Precision lever to Recall something you witnessed yourself. | `eff.grant_lever` precision; verbs recall; when the thing recalled was witnessed by you; first such Recall after a completed long rest | 1 | omened |

**T-02-9 Knack pools.** The knack is drawn among the level-2 deed tags of the branches in the
character's birth pool, each at weight 2.

| Livelihood + its default upbringing (human) | Branches in the pool | Knacks eligible | Chance the knack lands on a default deep training |
|---|---|---|---|
| Soldier + Road-raised | influence, martial, wilds | 27 | 2 in 27 (7%) |
| Hunter + Wilds-raised | martial, wilds | 18 | 2 in 18 (11%) |
| Rider + Court-raised | influence, lore, martial, wilds | 36 | 2 in 36 (6%) |
| Laborer + Village-raised | craft, martial, wilds | 29 | 1 in 29 (3%) |
| Thief + Street-raised | guile, influence, martial | 29 | 2 in 29 (7%) |
| Charlatan + Street-raised | guile, influence | 17 | 2 in 17 (12%) |
| Sailor + Water-raised | martial, wilds | 18 | 1 in 18 (6%) |
| Herder + Village-raised | craft, lore, wilds | 26 | 2 in 26 (8%) |
| Scholar + Cloister-raised | craft, lore | 20 | 1 in 20 (5%) |
| Healer + Village-raised | craft, lore, wilds | 26 | 2 in 26 (8%) |
| Apprentice + Cloister-raised | arcane, craft, lore | 31 | 1 in 31 (3%) |
| Acolyte + Cloister-raised | craft, divine, lore | 28 | 1 in 28 (4%) |
| Hedge-taught + Wilds-raised | martial, primal, wilds | 25 | 1 in 25 (4%) |
| Touched + Village-raised | craft, guile, primal, wilds | 32 | 1 in 32 (3%) |
| Merchant + Guild-quarter raised | craft, influence, wilds | 26 | 2 in 26 (8%) |
| Performer + Road-raised | influence, lore, wilds | 24 | 2 in 24 (8%) |
| Courtier + Court-raised | influence, lore | 18 | 2 in 18 (11%) |
| Artisan + Guild-quarter raised | craft, influence | 20 | 2 in 20 (10%) |
| Watchman + Guild-quarter raised | craft, influence, lore, martial | 41 | 1 in 41 (2%) |
| Tinker + Guild-quarter raised | craft, influence, lore | 29 | 2 in 29 (7%) |
| Wanderer + Road-raised | influence, wilds | 15 | 0 in 15 (0%) |

Over all 1,512 combinations of people, upbringing and livelihood the pool holds 15 to 52 knacks (median
35): never so few that the result is predictable.

**T-02-10 The Bent's pool gate.** (`gen_birth.yaml`, layer `bent`)

| Attribute (`birth.bent.*`) | In the pool when the character has 3 or more resolved frames in any of |
|---|---|
| Might | `deed.martial`, `deed.craft` |
| Agility | `deed.martial`, `deed.guile`, `deed.craft` |
| Endurance | `deed.martial`, `deed.wilds`, `deed.primal` |
| Wits | `deed.wilds`, `deed.guile`, `deed.lore`, `deed.influence` |
| Intellect | `deed.lore`, `deed.arcane`, `deed.craft` |
| Presence | `deed.influence`, `deed.divine`, `deed.guile` |
| Resolve | `deed.primal`, `deed.divine`, `deed.arcane`, `deed.influence` |

| If the character has worked only in | The Bent pool holds |
|---|---|
| martial | Might, Agility, Endurance |
| guile | Agility, Wits, Presence |
| wilds | Endurance, Wits |
| lore | Wits, Intellect |
| arcane | Intellect, Resolve |
| divine | Presence, Resolve |
| primal | Endurance, Resolve |
| influence | Wits, Presence, Resolve |
| craft | Might, Agility, Intellect |

**T-02-11 The Bent: what deferring is worth.** `n` = attributes in the pool at the first draw
(equal weights; a declined attribute is struck; the pool is assumed not to grow between draws).

| n | The one you want comes on the first draw | You defer until it comes (at most twice): you get it | …and you end with no Bent | Either of two you would be glad of, by the same policy |
|---|---|---|---|---|
| 2 | 50% | 100% | 0% | 100% |
| 3 | 33% | 100% | 0% | 100% |
| 4 | 25% | 75% | 25% | 100% |
| 5 | 20% | 60% | 40% | 90% |
| 6 | 17% | 50% | 50% | 80% |

A character whose work is narrow (two or three attributes in the pool) can have the Bent they want for
the price of waiting; one whose work is wide is offered more and risks more. Working in a new branch
before the next draw adds its attributes to the pool: it widens the choice and lowers each chance.

**T-02-12 Archetype coverage.** Each of chapter 04's twenty-five iconic archetypes (04.2.7) as a
creation recipe that makes it pursuable from the first scene. A recipe is a suggestion; recognition
still comes only from deeds.

| Archetype (04's calling) | Livelihood; profile and picks | Notes |
|---|---|---|
| Fighter (Warrior) | Soldier; Focused: blade + shield | any people; Orc-kin and Giant-kin Typical excel |
| Ranger | Hunter; Focused: archery + tracking | Wren (WE-02-1) |
| Rogue (Thief, Shadow) | Thief; Focused: thievery + stealth | Street-raised adds streetwise and the Cant |
| Bard | Performer; Focused or Gifted (*Stirring Song*) | Road-raised |
| Cleric (Priest, Healer) | Acolyte; Gifted: healing + *Mend Flesh* | Cloister-raised: Focus 5 |
| Paladin | Acolyte; Gifted: smiting + *Smite*; off-list access pick blade or shield; or Rider with the aspiration [divine.oaths] | the oath itself is chapter 04's offer |
| Druid | Hedge-taught; Gifted: growth + *Root Snare* | Wilds-raised |
| Wizard | Apprentice; Gifted: a school + its spell | Cloister-raised |
| Sorcerer (Elementalist) | Touched, the spark (`birth.gift.elements`) | innate; no teacher needed |
| Warlock (Pactbound) | Acolyte; Gifted: pact + *Patron's Brand*; the keeper is a patron | the calling is offered by V13 in play |
| Monk | Laborer; Focused: unarmed + athletics; Cloister-raised; a creed on `conduct.restraint` | |
| Barbarian (Berserker) | Soldier or Laborer; Focused: axe + athletics; Wilds-raised | the primal half is found in play (a place's acceptance) |
| Necromancer | Apprentice; Gifted: necromancy + *Wither* | |
| Artificer | Tinker; Focused: artifice + alchemy | the arcane half is learned in play |
| Alchemist | Tinker; Gifted: alchemy + *Quick Tincture* | |
| Merchant-prince | Merchant; Focused: trade + persuasion | Guild-quarter raised; the *prince* is rank and holdings (11) |
| Scholar | Scholar; Rounded or Broad; lore picks from Intellect | |
| Knight (Cavalier) | Rider; Focused: mounted + blade; Court-raised | knighthood is a rank (11); an aspiration names it |
| Witch (Hexer) | Hedge-taught; Gifted: hexcraft + *Evil Eye*; or Touched (the eye) | |
| Shaman (Spirit-talker) | Hedge-taught or Touched; spirits + *Spirit Tongue* | |
| Assassin, Spy | Thief; Focused: stealth + ambush (off-list) / Charlatan; Focused: deception + disguise | |
| Healer, mundane (Physician) | Healer; Focused: medicine + foraging, or Gifted (*Field Surgeon*) | |
| Monster-hunter (Slayer) | Hunter; Rounded: tracking deep, archery and bestiary (off-list) as access | |
| Captain | Soldier; Focused: tactics + command | Road-raised |
| Smith and the trades (Artisan) | Artisan; Focused: the craft + trade, or Gifted (*Keen Edge* and its kin) | Village- or Guild-quarter raised |

**T-02-13 Fate's hand.** (`origins.yaml#tables`; rolled only when the player asks for chance, 02.2.2)

- `tbl.creation.people` (d100): 1–55 Human · 56–65 Dwarf · 66–75 Elf · 76–83 Halfling · 84–89 Orc-kin · 90–93 Goblin-kin · 94–97 Beastfolk · 98–100 Giant-kin
- `tbl.creation.upbringing` (d100): 1–30 Village-raised · 31–42 Wilds-raised · 43–54 Street-raised · 55–66 Guild-quarter raised · 67–76 Road-raised · 77–86 Water-raised · 87–92 Cloister-raised · 93–96 Court-raised · 97–100 Bound service
- `tbl.creation.livelihood` (d100): 1–5 Soldier · 6–10 Hunter · 11–15 Rider · 16–20 Laborer · 21–25 Thief · 26–30 Charlatan · 31–35 Sailor · 36–40 Herder · 41–45 Scholar · 46–50 Healer · 51–55 Apprentice · 56–60 Acolyte · 61–63 Hedge-taught · 64–65 Touched · 66–70 Merchant · 71–75 Performer · 76–80 Courtier · 81–85 Artisan · 86–90 Watchman · 91–95 Tinker · 96–100 Wanderer

**T-02-14 Optional data fields this chapter adds** (allowed by `data/SCHEMAS.md`: owners may add
optional fields and document them here).

| File | Field | Type | Meaning |
|---|---|---|---|
| origins.yaml | `kind` | people \| upbringing \| livelihood | which of the three origins the entry is |
| | `attribute_rules.floors`, `.shapes`, `.uncommon_of_kind` | map; map; rule | Typical minimums; the arrays allowed; the Free rule a non-human may take (02.3.4) |
| | `extra_access_trainings`, `language_picks`, `license_choice` | rule; int; {pick, of} | the human's training; tongues to pick; a choice among licenses |
| | `focus_base`, `wealth`, `coin`, `budget_units` | int; enum; int; int | upbringing values (02.4.4) |
| | `kit_id` | kit id | the kit in kits.yaml that `kit` copies |
| | `trainings`, `magic`, `grants`, `defaults`, `technique_suggestions` | lists and maps | livelihood content (02.4.5, 02.5) |
| | `org_tags`, `bond_seeds`, `drive_seeds`, `aspiration_seeds` | lists | seeds for C8 |
| | `birth_circumstance` | circumstance id | forces the manner (Bound service: hard; Touched: gifted) |
| | `backstory` | [tag] | declared, always empty (02.11.1) |
| | top level: `profiles`, `creation_defaults`, `bond_kinds`, `faction_tie_brackets`, `tables`, `concept_branches`, `attribute_shapes`, `upbringing_budget` | | the closed lists of 02.5.2, 02.2.2, 02.9.2, 02.9.5, 02.2.2, 02.2.4, 02.3.1, 02.4.4 |
| gen_birth.yaml | `layer` (= `mod_group`) | knack \| quirk \| gift \| bent | which slot kind an entry fills |
| | `quality_rungs[].magnitude_layers`, `.signature_layer` | lists | which layer each slot draws from |
| | `text`, `competence`, `gifted_ability`, `attribute`, `excluded_when` | | player-facing text; a gift's +2; a gift's working; a Bent's attribute; a Bent's exclusion |
| | top level: `bent`, `bias_rule`, `allows_degree_none` | | 02.6.5–02.6.7; 02.6.4; 00.11.2 |
| kits.yaml | `note`; `choices` | str; [{pick, options}] | narration seed for the resolved item; the kit choice |

**T-02-15 What the starting numbers mean** (success or better, exhaustive d20 with chapter 01's
one-step rule; reference ladder).

| A new character who is… | Modifier | Easy 10 | Moderate 15 | Hard 20 | Very hard 25 |
|---|---|---|---|---|---|
| at their forced low, untrained (attribute −1, floor) | 0 | 55% | 30% | 5% | 5% |
| ordinary and untrained (attribute 0, floor) | +1 | 60% | 35% | 10% | 5% |
| capable, holding the training as access (attribute +2, floor) | +3 | 70% | 45% | 20% | 5% |
| capable, holding it deep (attribute +2, +2) | +4 | 75% | 50% | 25% | 5% |
| a specialist (attribute +3, +2) | +5 | 80% | 55% | 30% | 5% |
| a specialist with a knack on the tag (+3, +2, +1) | +6 | 85% | 60% | 35% | 10% |

The +1 and +5 rows are 00.3.17's calibration lines CT-1 to CT-4 for an untrained PC and a band-1
specialist, unchanged: this chapter's numbers sit on the ladder chapter 00 calibrated. A training held
as access changes none of these numbers for its holder; it changes which attempts are legal at all
(a Hard lock is G2 for the access holder and G3 for everyone else).

---

## Worked examples

Three characters are made end to end, with every number: one on the full path (Wren, 00's continuous
character), one on the fast path (a newcomer's first character), one unusual concept. Every birth draw
below was made by running the shipped `gen_birth.yaml` through the generator's steps with a seeded
random source (scratchpad `draws02.py`): pool sizes, total weights and rolls are the script's output.
Names of gods, lodges and places are *(illustrative; chapter 13 owns)*.

### WE-02-1 The full path: Wren

**C0.** The player has played before; wants more exploring and investigating, everything else the
same; pacing `standard`. Recorded through chapter 14's preference record.

**C1 Livelihood.** Player: "A forester's daughter who can track anything, and wants to know what is
burning the deep wood." 02.2.4: the verbs are *track* and (implied) *hunt* → branch `deed.wilds` →
within wilds: Hunter, Herder, Sailor, Wanderer → **Hunter**. No people is named → Human. "A forester's
daughter" names a place of raising → Wilds-raised is offered. "Wants to know what is burning the deep
wood" is kept for C8. The player confirms all three.

**C2 People.** Human: the **Free** rule (sum +5), no gift, one extra training (02.4.3), Common at
native.

**C3 Upbringing.** Wilds-raised: Focus **4**; `lic.training.wilds_survival` and one of foraging,
tracking, animals. Tracking will come from the livelihood, so she takes **foraging**. No letters, no
second tongue. Budget: 1 (Focus 4) + 1 + 1 = 3 units.

**C4 Attributes.** Shape Peaked: +3, +2, +1, 0, 0, 0, −1. The Hunter's priority (Agility, Wits, Might,
Endurance, Intellect, Presence, Resolve) gives the default placement, which she keeps:

| Might | Agility | Endurance | Wits | Intellect | Presence | Resolve | Sum |
|---|---|---|---|---|---|---|---|
| +1 | +3 | 0 | +2 | 0 | 0 | −1 | +5 |

Shown as she places: Vitality 12 + 0 = **12**; dread threshold 8 − 1 = **7**; learning picks 0.

**C5 Trainings.** Profile **Focused**: `deed.martial.archery` and `deed.wilds.tracking`, both deep
(+2). The human's extra training: `deed.martial.polearm`, held as access (her spear). With the
upbringing's two, she holds five training licenses, all `trained`:

| License | Held | Competence used under the tag |
|---|---|---|
| `lic.training.martial_archery` | deep | +2 |
| `lic.training.wilds_tracking` | deep | +2 |
| `lic.training.martial_polearm` | access | floor +1 |
| `lic.training.wilds_survival` | access | floor +1 |
| `lic.training.wilds_foraging` | access | floor +1 |

Preview shown at this step: a bow shot is Agility +3, competence +2 = **+5**; against a Guard of 13 she
needs 8 or better: 65% (critical success 15%, critical failure 5%).

**C6 Birth.** Asked about her early years, the player says "nothing special". Manner: `unremarked`.
Source tags: `creature.folk.human`; `deed.wilds`, `deed.martial`, `terrain.forest`, `terrain.highland`
(Wilds-raised); `deed.wilds`, `deed.martial` (Hunter). `generate(gen.birth, pc.wren, unremarked, none)`,
rung `plain`:
- knack: the pool gate admits the knacks of wilds (6) and martial (12): 18 entries, total weight 36;
  roll 34 → band 33–34 → **`birth.knack.wilds_survival`**: +1 edge on survival.
- quirk: 22 entries, total weight 40; roll 1 → band 1–2 → **`birth.quirk.iron_stomach`**: eaten or
  drunk poisons count one rung lighter.

The DM tells it: "You have never once been sick from bad water, and a cold camp has never frightened
you: you have a feel for getting through a night out of doors that no one taught you." A survival check
now reads Wits +2, floor +1, edge +1 = +4 (Moderate: 50%).

**C7 Numbers and kit.** Vitality **12/12**; Focus **4/4**; fate **1**; dread 0 of 7. Kits: the Hunter's
(shortbow, 20 arrows, leather armor, dagger, rope and hook, snares and a skinning knife, and by choice
a spear; 3 coin) and the Wilds-raised pack (worn clothing, cloak, boots, pack and waterskin, 4 days'
food, tinderbox and torches; 5 coin): 8 coin. Guard with the spear readied: 10 + 3 (Agility) + 1
(polearm at the floor) = **14**; leather armor reduces physical harm by 1 (07).

**C8 Ties.**
- *Drive:* "Find what is burning the deep wood." KIND: could a scene end with this done? Yes → **want**
  → a commitment (vow) and a thread seed for chapter 11.
- *Bonds:* anchor, the Hunter's seed made her own: **mentor**, Sella Varn, the old forester who taught
  her to read a trail (+1 Warm). Thorn: **rival**, Warden Brask, who has sworn to catch her on the
  wrong side of a boundary stone (−1 Wary). Two recurring NPCs are created (12.11.1).
- *Aspiration:* "to be the best shot in the marches" → `[deed.martial.archery]`.
- *The one true thing:* "I am the only one who has seen the burned stag and lived." CAPABILITY: no
  ability, sense or number → false. WORLD: it is about her own past; no one need agree → false. Recorded
  as an established, shown fact, with a hook of kind `question`.
- *Faction tie:* a foot in the door: `org.order.hunters` at +1 (chapter 13 maps it to a lodge).
- *Hooks (7):* Human "a countryman or cousin…" (npc); Wilds "something has been taking animals or
  people from the edge of the country you grew up in" (thread); Hunter "a quarry you wounded and lost
  is still out there" (thread); the drive (thread); Sella (npc); Brask (npc); the burned stag (question).

**C9.** "Wren", she. PR-02-6 validates and writes.
```
[SHEET] Wren (she) — Human · Wilds-raised · Hunter
  Might +1 · Agility +3 · Endurance 0 · Wits +2 · Intellect 0 · Presence 0 · Resolve −1
  Vitality 12/12 · Focus 4/4 · fate 1 · Guard 14 · dread 0 of 7
  Good at (+2): archery · tracking      Also trained: polearms · survival · foraging
  From birth: a knack for survival (+1) · Iron stomach
  Speaks: Common (native) · cannot read
  Carries: shortbow, 20 arrows, spear, leather armor, dagger, rope and hook, snares, cloak, pack,
           4 days' food, torches · 8 coin
  Wants: "Find what is burning the deep wood."   Hopes to become: the best shot in the marches
  Matters: Sella Varn (mentor) · Warden Brask (rival)   Known to: a hunters' lodge (Warm)
  True of you alone: the only one who has seen the burned stag and lived
  You may adjust your choices once before your first night's rest.
```
**Afterwards: the lock and the Bent.** Wren's first completed long rest is the dawn of WE-00-1 (row 4):
`reflection` fires, `h.02.creation_lock` closes the window. By the next reflection she has, since
creation, more than three resolved frames each in `deed.martial` (the hound fight, WE-00-2) and
`deed.wilds` (the trail). `h.02.bent_offer`: source tags `[deed.martial, deed.wilds]` → the pool gate
admits Might, Agility, Endurance and Wits; Agility is +3 and is excluded → pool {Might, Endurance,
Wits}, roll 2 of 3 → **Endurance**.
```
[CHOICE] Your Bent: something in you has settled. Endurance +1, for good (Vitality 12 → 13).
         (a) accept · (b) defer: this one is gone for you; another comes later (you may defer
         twice in all)        No default: nothing changes until you choose.
```
She accepts: `eff.02.bent {endurance, 1}`; Vitality 13/13. Her attributes are now Might +1, Agility +3,
Endurance +1, Wits +2, Intellect 0, Presence 0, Resolve −1: exactly the sheet 00 gave her. (00's
illustrative sheet shows Vitality 12; by 02.7.1 it is 13 once the Bent is taken. See Interface
requests, 00-3.)
*The other branch.* Had she deferred, hoping for Wits: Endurance is struck; at the draw two reflections
and ten frames later the pool is {Might, Wits}; the script's roll is 2 of 2 → Wits. She would have had
the one she wanted at 1 chance in 2, and the price was two sessions without the +1.

### WE-02-2 The fast path: a newcomer's first character

The whole exchange. The player has never played a game like this.

> **DM:** *(Message 1 of PR-02-7: the welcome, then)* `[CREATE 1/5] Before we begin` …
> **Player:** Fights and exploring I suppose. Nothing I can think of. Quick, please.

Recorded: conflict `more`, exploration `more`, the rest `same`; no lines or veils yet; path fast;
`player.new_to_this = yes`.

> **DM:** `[CREATE 2/5] Who are you?` … *(seven lives)* … `If you move on without choosing: Soldier.`
> **Player:** An old soldier who's had enough of it. He wants to buy an inn somewhere quiet.

02.2.4: *soldier* → branch martial → **Soldier**. No people named → Human. No place of raising named →
the Soldier's default, Road-raised. "Wants to buy an inn" is kept.

> **DM:** A soldier, then: good with a blade and a shield, strong, hard to put down. And I have noted
> the inn. `[CREATE 3/5] What do you want?` (yours) "I want to buy an inn somewhere quiet and never
> draw steel again." (a)… (b)… (c)… `If you move on without choosing: yours.`
> **Player:** Yes, that.

02.9.1: could a scene end with the inn bought? Yes → **want** → the long vow, and a thread seed. The
sentence names no one he hopes to *become* → the aspiration stays open.

> **DM:** `[CREATE 4/5] Who matters to you?` (a) the wagon-family or company that still counts you one
> of theirs · (b) the file-mate who carried you off a field once · or someone of your own.
> **Player:** My daughter, Lysa. She's twelve. She lives with my sister.

Anchor bond, kind **ward** (she depends on him): NPC `npc.lysa` (recurring; name and age band from the
player's words, the rest rolled), standing +2 Friendly, and a commitment "Lysa depends on you". The
sister is written on mention as a walk-on.

> **DM:** `[CREATE 5/5] What are you called?`
> **Player:** Bram. He.

The engine now applies the defaults (02.2.2), draws, and writes:
- **Attributes** (Human, Free, Peaked; Soldier's priority Might, Endurance, Agility, Wits, Resolve,
  Presence, Intellect): Might **+3**, Endurance **+2**, Agility **+1**, Wits 0, Resolve 0, Presence 0,
  Intellect **−1**. Sum +5.
- **Upbringing** Road-raised: Focus **4**; navigation (access); one tongue of choice → the default,
  Dwarvish (accented). Budget 1 + 1 + 1 = 3.
- **Trainings** Focused: blades and shield, deep (+2). The human's extra training: the first tag on the
  Soldier's list not yet taken → polearms (access). Intellect −1 → no learning picks.
- **Birth** (`unremarked`; source tags human, wilds, influence, martial, road, camp): knack pool 27
  entries (wilds 6, influence 9, martial 12), total weight 54, roll 47 → **a knack for navigation**
  (+1); quirk roll 1 of 40 → **Iron stomach**.
- **Numbers:** Vitality 12 + 2 = **14**; Focus **4**; fate **1**; dread threshold **8**; Guard with
  sword and round shield = 10 + 1 (Agility) + 2 (blade or shield, deep) + 1 (shield) = **14**; a sword
  blow rolls Might +3, competence +2 = **+5** (65% against Guard 13).
- **Kit:** leather armor, round shield, dagger, bandages, sword; clothing, cloak, boots, pack and
  bedroll, 4 days' food, tinderbox and torches; 5 + 12 = **17 coin**.
- **Hooks (5):** Human, Road ("in any roadside inn there is a fair chance of someone who traveled with
  your people"), Soldier ("your old company is hiring again, and not for honest work"), the inn
  (thread), Lysa (npc). **Open:** a thorn, a true thing, a faction tie, an aspiration.

> **DM:** You have always had a sense for the road: which fork, how far to water. And an army's
> cooking never once laid you low.
> ```
> [SHEET] Bram (he) — Human · Road-raised · Soldier
>   Might +3 · Agility +1 · Endurance +2 · Wits 0 · Intellect −1 · Presence 0 · Resolve 0
>   Vitality 14/14 · Focus 4/4 · fate 1 · Guard 14 · dread 0 of 8
>   Good at (+2): blades · shield      Also trained: polearms · navigation
>   From birth: a knack for navigation (+1) · Iron stomach
>   Speaks: Common (native), Dwarvish (accented) · cannot read
>   Carries: sword, round shield, leather armor, dagger, bandages, pack and bedroll, 4 days' food,
>            torches · 17 coin
>   Wants: "I want to buy an inn somewhere quiet and never draw steel again."
>   Matters: Lysa, your daughter (ward)
>   Still open: someone who troubles you · one true thing · who knows you · who you hope to become
> ```
> *(the three `[RULES]` notes)* `[CREATE] Ready? (a) begin · (b) change something`
> **Player:** Begin.

Five answers. Every one of the twenty-odd choices he was not asked about is recorded with
`default: true` and can be opened with "details".

**The second look, two scenes later.** Bram has missed twice with a borrowed bow (Agility +1, floor
+1: +2) and the player asks whether he could be quicker. Between scenes, window open, not yet revised
(PR-02-8): the player moves the +2 from Endurance to Agility and the +1 back. The engine validates
(Free rule: any placement) and writes: Agility +2, Endurance +1; Vitality 14 → **13**; Guard 14 →
**15**. Nothing else changes; `pc.creation.revised = true`. The same request the morning after his
first night's rest would be refused: "Your choices are settled now (02.2.6). What you can still do:
train (chapter 05), or see what your Bent brings."

### WE-02-3 An unusual concept: Thessaly Quill

Player: "A goblin who was raised by temple scribes, drives out ghosts, and wants to be a knight."

**C1.** 02.2.4: *drives out* (a working of granted power) → branch divine → **Acolyte**. A people is
named (goblin) and a place of raising (a temple) → **Goblin-kin**, **Cloister-raised**. "Wants to be a
knight" is kept for C8.

**C2 The trade-off, in numbers.** An Acolyte casts with Presence (05.7.2). Goblin-kin's Typical rule
fixes Presence at −1.

| | Typical (sum +7) | Uncommon of her kind (sum +5) |
|---|---|---|
| A legal placement for this concept | Wits +3, Agility +2, Resolve +2, Endurance +1, Might 0, Intellect 0, Presence **−1** | Presence **+3**, Resolve +2, Wits +1, Agility 0, Endurance 0, Intellect 0, Might −1 |
| Effect DC of her turning (10 + Presence + competence 2) | **11** | **15** |
| A walking corpse with Endure (Resolve) +1 withstands it | 55% | 35% |
| What she keeps either way | Cave-eyes; Goblin (native), Common (accented) | the same |
| What it costs | her working fails more often than not | two attribute points; no floor on Wits or Agility |

She chooses **uncommon of her kind** (`pc.origin.rule = free`). This is P4's trade made visible: the
points were available, and she declined them for the freedom to be good at the thing her people are
not.

**C3.** Cloister-raised: Focus **5**; letters. No trade license, no second tongue. 2 + 1 = 3 units.

**C4.** Peaked, placed as above. Vitality **12**; dread threshold **10**; Intellect 0: no learning
picks.

**C5.** Acolyte, school **exorcism**; profile **Gifted**: `deed.divine.exorcism` deep (+2) and the
technique *Turn the Dead* (`ab.turn_undead`, `min_tier` 1, first tag `deed.divine.exorcism.turning`;
1 Focus; up to three undead within `band.near` roll Endure (Resolve) against her effect DC 15; a
failure is frightened until the scene ends), rank 1, acquired partition. The license's `requires`: the
engine writes `pc.keeper.exorcism = the Lantern-Bearer` *(illustrative)*, the keeper's sign is in her
kit, and the faith's status toward her starts at Warm. She holds **one** training license: the lowest
count the rules allow, and her five Focus are the most they allow.

**C6 Birth.** Player: "She was born during an eclipse. No warren would keep her; the scribes took her
in." 02.6.4 checks the manners in order. `gifted`: no (she is not Touched). `hard`: yes, exile in
childhood is established. First match wins → **hard**. The eclipse would have made her `omened` had
nothing come before it; an account that fits two manners takes the earlier one, and the player is told
which: "I've read that as a hard childhood. The eclipse I'll keep as a fact about you." It is written as
`pc.birth.account`.
Draw (`hard`: ×3 on entries carrying `deed.wilds.survival`; source tags goblin, guile, lore, craft,
hold, temple, divine): knack pool 36 entries (guile 8, lore 9, craft 11, divine 8), total weight 72 (no
survival knack is in her pool, so nothing there is tripled), roll 15 → band 15–16 → **a knack for
scribing** (+1). Quirk: 21 entries (True north is gated out: her pool holds no wilds, road or water),
total weight 37 + 2 × 11 = 59 with the six hardy quirks tripled; roll 46 → band 46–47 → **Honest
face**: a Precision lever on a truthful Talk to someone who has never met her. The DM: "The scribes
used to say your hand was the neatest in the copy-room before you could reach the desk. And strangers
believe you, when you are telling the truth; which, for a goblin at a city gate, is worth something."

**C7.** Vitality **12**; Focus **5**; fate 1. Kits: Acolyte's (holy symbol, a book of rites, remedies
×2, a worn dagger, a mace) and the Cloister pack (a worn habit, cloak and sandals, a scrip, 2 days'
food, a small book of hours): 4 + 3 = **7 coin**. Guard with the mace: 10 + 0 + 1 = **11**. A mace blow
rolls Might −1, floor +1 = **0** (45% against Guard 12).

**C8.**
- *Drive:* "I will be knighted, and they will have to say my name in the hall." Could a scene end with
  this done? Yes: the knighting is an event → **want** → the long vow. (The rank itself is chapter
  11's to grant.)
- *Aspiration:* "to be a knight in deed, whatever they call me" → what a knight *does*:
  `[deed.martial.mounted, conduct.courage]`. Leanings now shows two rows at *unformed*: "mounted
  combat" and "courage". Nothing is added to any tally.
- *Bonds:* anchor **mentor**, Brother Anselm, who taught her letters (+1 Warm). Thorn **rival**, a
  fellow novice who thinks her calling a pretence (−1 Wary).
- *The one true thing:* "I am the only goblin ever to take the vows of the Lantern." CAPABILITY: false.
  WORLD: it asserts something about a people and a faith's whole history; others would have to agree →
  **true** → recorded as a **belief**. The engine asks the Oracle at rung Even and seals the answer
  (d100 = 54: yes; sealed, gate: the temple's oldest roll of vows). Hook, kind `question`: "who else
  would care if it were so?"
- *Faction tie:* **sworn and hunted**: the Lantern's faith at **+2** (which satisfies the regard
  05.7.4 needs) and `org.order.knightly` at **−2**: the order she means to join has already laughed
  her out of its yard once.
- *Hooks (8):* Goblin-kin "a gate-warden has you marked as a thief before you have touched anything"
  (enemy); Cloister "one book, door or grave in the cloister was forbidden to you" (question); Acolyte
  "a superior of your faith who doubts your calling and will test it" (npc); the knighting (thread);
  Anselm (npc); the novice (npc); the vows (question); the knights (enemy).

**C9.** Thessaly Quill, she.
```
[SHEET] Thessaly Quill (she) — Goblin-kin (uncommon of her kind) · Cloister-raised · Acolyte
  Might −1 · Agility 0 · Endurance 0 · Wits +1 · Intellect 0 · Presence +3 · Resolve +2
  Vitality 12/12 · Focus 5/5 · fate 1 · Guard 11 · dread 0 of 10
  Good at (+2): exorcism
  Technique: Turn the Dead — up to three undead within near must withstand you (DC 15) or be
             frightened of you for the scene · 1 Focus
  From birth: a knack for scribing (+1) · Honest face      Gift: Cave-eyes
  Speaks: Goblin (native), Common (accented) · reads and writes
  Carries: mace, holy symbol, book of rites, remedies, dagger, habit and cloak, scrip, 2 days' food,
           a book of hours · 7 coin
  Wants: "I will be knighted, and they will have to say my name in the hall."
  Hopes to become: a knight in deed   Matters: Brother Anselm (mentor) · a fellow novice (rival)
  Known to: the Lantern's faith (Friendly) · a knightly order (Unfriendly)
  You believe: you are the only goblin ever to take the vows of the Lantern
```
**Is the concept playable from the first scene?** She can turn the dead (G2: her spell), read and
write, see in the dark, and talk her way through a temple as one of its own. She cannot fight from the
saddle (`lic.training.martial_mounted` is not held: G3, with the redirect "ride there and fight on
foot; a riding-master could teach you"), and on foot she strikes at +0. Nothing stops her from riding
(Handle), from fighting, or from being brave where people can see it, and each resolved deed is
evidence. Whether she becomes a knight is now a question for play, which is the point.
*Tempting non-example.* "Since I'm an exorcist, I can see the ghost, right?" *Turn the Dead*'s literal
scope affects undead "that can see or hear you" and grants no sight; `lic.training.divine_exorcism`
licenses the school's workings and small workings, not a sense. G3: "You feel the cold of it and
nothing more. You can call on your keeper and turn whatever is here, seen or not; to *see* the dead is
something the spirit-talkers learn." (INV-8; 01.3.6.)

### WE-02-4 Boundary pairs and non-examples

| # | Case | Ruling | Why |
|---|---|---|---|
| 1 | **Same choices, different people.** Odo makes Wren's exact choices (Human, Wilds-raised, Hunter, the same placement and picks). | His draw (same pools; rolls 2 of 36 and 24 of 40): **a knack for archery** and **Steady hands**. His bow shots roll +6 (70% against Guard 13) where Wren's roll +5 (65%); her survival checks roll +4 where his roll +3. | P1: variance beneath identical visible choices (02.6.2). Neither chose it; both are better for it. |
| 2 | **Deep, access, none.** Three characters with Agility +2 face a guild lock (Hard, DC 20). A Thief holds thievery deep; a Wanderer took it as her off-list access pick; a Soldier holds nothing. | Thief: G2, +4, 25%, and may push. Wanderer: G2, +3, 20%, no push. Soldier: G3 → the license's crude fallback, Force on the hasp (Might; loud; WE-00-3). | 02.5.2: access is permission, depth is performance. |
| 3 | **Inside the window / after the lock.** Bram moves two attribute values in scene 3 (WE-02-2); the same request after his first long rest. | Allowed once; refused with what is still possible. | 02.2.6; P4. |
| 4 | **A manner that fits two.** Thessaly's account (WE-02-3). | `hard`, by first match; the eclipse is kept as a fact. | 02.6.4's ordered list; SG-10 (no nested exceptions). |
| 5 | *Non-example:* "Take Presence down to −2 and give me another point of Might." | Refused: attributes are arrays (02.3.1); nothing is traded, and −2 is outside the creation range. The DM shows the three shapes. | C:P11; 00.4.3. |
| 6 | *Non-example:* "He's a retired general, so the garrison will take his orders." | Soldier grants no rank (02.1.3 g). Offered: a faction tie (`org.crown.military`, Warm: they know him), command as a training pick, the aspiration `[deed.influence.command]`, and a true thing ("I once held the bridge at Carrow") that passes 02.9.4. Orders are a Talk like anyone's. | 00.17.1 Q22: rank is 11's; SG-06. |
| 7 | *Non-example:* "My apprentice already knows three spells." | Gifted grants one technique at rank 1 (02.5.4). Others are learned in play: witnessed and emulated (05.5.4), or studied from a text (05.8.5). The DM offers a spellbook hook instead. | 02.1.3 c; C:V. |
| 8 | *Non-example:* "I was born lucky, start me with 3 fate." | fate is 1 (02.7.3). "Born lucky" may be a true thing only as a past event ("the roof fell and I walked out"); as a claim about outcomes it fails CAPABILITY. | 01.16; 02.9.4. |

---

## Edge cases & adaptation anchors

**Concepts the lists do not name.**
- *A life not on the list* ("a gravedigger", "a retired pirate", "a circus strongman", "a beekeeping
  hermit"). Classify by what they did (02.2.4), take the nearest livelihood, use the off-list pick for
  what makes them different, and call the livelihood whatever the player likes: the **name is fiction,
  the entry is rules**. A gravedigger is a Laborer with `lore.religion` off-list; a retired pirate is a
  Sailor on the Focused profile with blades; the strongman is a Performer with `martial.athletics` deep.
- *A people not on the list.* If chapter 13 has added it, use that entry. If not, and the concept needs
  no capability the entry lacks, take the nearest entry and describe it freely (a cat-person is
  Beastfolk). A body that would itself be a capability (wings, four legs, a hand's height) is not
  granted by description: flying is `slot.movement_mode` and needs a license (G3), and the DM says what
  a setting origin would have to supply.
- *Two lives* ("a soldier who became a priest"). The later life is the livelihood. The earlier one is
  the off-list pick, a bond, a hook, and one line of the prologue. The Rounded and Broad profiles exist
  for exactly this.
- *Born with a power that is not primal* ("she has healed by touch since she was a child"). Divine
  power needs a keeper (05.7.4). Build her as an Acolyte whose keeper is a power of chapter 13's that
  she does not understand (the hook is a `question`), or as a Touched with the green hand, whose
  renewal is the nearest primal thing. An innate arcane gift does not exist: arcane is formula (05.7.2).

**Choices against the grain.**
- *A magic livelihood under a Typical rule that fixes the casting attribute at −1* (an Orc-kin
  Apprentice, a Goblin-kin Acolyte, a Beastfolk Hedge-taught or Touched). The default already takes the
  Free rule (02.3.5's caster exception); a player who asks for the Typical rule anyway may have it. Before
  confirming, the DM states the effect DC it produces (10 − 1 + 2 = 11) and the first-fight odds it means
  (one T2 foe: 62–73% on the branch working, against 90–95% at +3; `sim02.py`). WE-02-3 is the worked
  case [revision: I-009].
- *A character built weak on purpose* (the frail scholar, the cowardly knight). Legal; the arrays allow
  only one −1, and the floor stands. Nothing is given in exchange.
- *A bodily or mental condition from before the story* (blind in one eye, a lame leg, mute). It is a
  shown fact. If the player wants it to have mechanical weight, the DM takes the matching entry of
  chapter 07's `injuries.yaml` (kind `mark`) and shows its literal effects before the player confirms.
  It grants nothing in return: there are no points for flaws in this game (C:P11; PF2e's voluntary flaws
  are likewise "purely for roleplaying", R: https://2e.aonprd.com/Rules.aspx?ID=2079).
- *Age.* Young, grown or old is a fact with no mechanics. An old soldier who "used to be better" is
  built as he is now.
- *Wealth, land, a title.* Court-raised and the Merchant's kit are as rich as creation goes. A title or
  a holding is rank and property (chapter 11): it may be a belief (02.9.4, WORLD), a drive, or a hook,
  never a starting possession.
- *A companion animal.* The dog, horse or hawk the player describes is a bond (kind friend) and a
  facet. Whether it acts in a conflict is chapter 16's; until a companion record exists it is a
  presence in the fiction and a reason to be careful, not a combatant.
- *"Can I just pick my knack?"* No. The knack and the quirk are the two things in a character nobody
  chose (P1). Everything else is chosen, and both results are benefits.
- *"I don't want anything random."* The creation draw is mandatory and cannot be declined; it can be
  ignored, since neither result ever forces an action. The Bent can be forgone.

**The procedure itself.**
- *Creation is interrupted* (the session ends at C5). Nothing has been written to the `Character`;
  `pc.creation` holds the answers so far. Resume at the next unanswered step. The record is written in
  one batch at C9 (PR-02-6), so a half-made character never exists in state.
- *The player says only "just start".* Every default applies: a human Soldier, Road-raised, with the
  default drive and anchor. The engine still asks for a name (a character needs one) and still draws.
- *The player wants to see everything before choosing anything.* "details" at C1 shows all 21
  livelihoods seven at a time; the codex's creation view (chapter 14) may show the tables of this
  chapter whole. Depth is never withheld; it is never pushed.
- *The region lacks something creation points at* (no faction of the tie's kind, no shrine of the
  keeper, no second tongue). The slot is held open (02.9.8) and the hook stays seeded; chapter 13 is
  asked for the entity (Interface requests). The character is still legal.
- *A name the cast already uses.* The engine checks the cast list; the DM asks for another or a byname.
- *Death or retirement before the window closes.* The window dies with the character. The successor is
  a new creation (02.2.7).
- *The Bent finds an empty pool* (every eligible attribute is at +3 or struck). No offer is made;
  `h.02.bent_offer` tries again at each reflection, and a newly worked branch can reopen it.
- *An attribute is maimed below the creation range before the Bent is taken.* The Bent may raise it;
  the cap is +3, and a maim is not undone by anything else (07.7.4).

**Adaptation anchors.** Rules of this chapter the DM may reach for outside creation (00.2.6):

| Anchor | Reach for it when | Knobs (T-00-20) | Does not cover |
|---|---|---|---|
| **02.9.4 The one true thing** (`Anchor: yes`) | in play, the player proposes a fact about their own character's past ("I worked these docks as a boy", "I've met this man") | none: the two flags decide between an established fact, a belief with a sealed truth, and a redirect | facts about the present scene (the Oracle, 00.12.7); anything that would be a license |
| **02.6.2 the quirk shape** (a pattern, not a card) | a mark, a boon or a long habit should leave a small permanent trace and no entry exists | the owning chapter authors it as *one* effect reference: a lever in a stated circumstance, a hazard step of one rung, or one daily reveal | anything that adds to a roll everywhere (that is competence or an edge, and has an owner) |
| **Origins as a quick past for an NPC** | chapter 12 or 16 needs to know what a recurring NPC or a hireling can do | people × upbringing × livelihood with the livelihood's default picks gives two +2 tags, tongues and letters | adversary stat blocks (chapter 09) |
| **02.2.6 the second look** | a player learns that a choice does not do what they thought, early | none: once, inside the window | anything after the lock (Retrain, chapter 15; chapter 05's paths) |

## State touched

**Writes (all with reason `creation`, `second_look` or `bent`):**
- **Entities:** the `Character` (kind `pc`); one item entity per kit line; one NPC per bond (through
  12.11.1).
- **Attributes** (owner 02 for values, 00 for the rules of change): set at C9; changed by the second
  look and by `eff.02.bent`.
- **Competence map:** the floor entry; one +2 entry per deep training (source `origin`).
- **Licenses held:** tongues, letters, a people gift, training licenses at `trained` (the license
  *definitions* are 05's, and this chapter's fragment for tongues, letters and gifts).
- **Slots:** at most one ability in `acquired` (05 owns the partition and its provisional rule).
- **Quantities:** Vitality, Focus, fate set to their starting values (semantics 07, 05, 01); coin (08).
- **Effect instances:** the knack, the quirk, a people gift's effect (permanent; source `gen.birth` or
  `orig.people.*`).
- **Facts:** `pc.origin.*`; `pc.true_thing` or a belief with a sealed truth; `pc.keeper.<school>`;
  `pc.accepted.primal.<school>`; `pc.birth.account`; `pc.look`; `pc.age_band`; `pc.creation.locked`.
- **Relationships:** bond standings (15 owns standing thereafter). Faction ties are handed to 11 as
  seeds; 11 writes faction status.
- **Commitments:** the long vow or the creed; a ward's dependence; a creditor's debt.
- **Aspirations** (`Character.aspirations`).
- **Meta `pc.creation`** (owner 02; visibility `available`): `{path, choices: {step: {value, default}},
  window: open | locked, revised: bool, birth: {manner, knack, quirk, gift, log}, bent: {status: pending
  | offered | accepted | forgone, deferrals: 0..2, struck: [attr], last_deferral: {reflections,
  frames}}, open_slots: [slot]}`.
- **Ledgers:** prologue lines in the chronicle (11's ledger, through `chronicle_append`); the
  generation log of each birth draw.
- **Handed to other owners:** hooks and the thread seed (11); facets (12); preferences (14).

**Reads:** `data/origins.yaml`, `gen_birth.yaml`, `kits.yaml`, `licenses.yaml`, `abilities.yaml`,
`tags.yaml`; chapter 13's region data (peoples present, names, second tongue, keepers, factions by
kind, pregens); the frame log (count of resolved frames by deed branch with the PC as actor, for the
Bent: no tally is read); the reflection count.

**Visibility (00.6.4).** Shown: attributes, Vitality, Focus, fate, licenses, the technique, the knack,
the quirk, the gift, kit, bonds' rung names, aspirations, the drive, the true thing (or "you
believe…"), open slots, the Bent offer. Available: `pc.creation` (every choice and whether it was a
default; each birth draw's log). Sealed: the truth of a belief; what became of a lost bond. Nothing in
this chapter is `background`.

**Tools used (00.14.2):** `create_entity`, `set_fact`, `update_quantity`, `set_relationship`, `grant`,
`apply_effect`, `generate` (domain `gen.birth`), `roll_table` (`tbl.creation.*`), `oracle` (sealed, for
a lost bond and a belief), `seal`, `offer_create` / `offer_resolve` (the Bent), `chronicle_append`,
`get_state`, `codex` (the sheet), and chapter 14's preference record.

**Hooks subscribed (00.10.2):** none. The knack and people gifts are `additive` effects; quirk levers
are lever grants; nothing in this chapter is an `independent_trigger`.

**Boundary handlers registered** (`data/boundaries.yaml owner-block 02`): `h.02.bent_offer` (`reflection`,
phase 8), `h.02.creation_lock` (`reflection`, phase 9), `h.02.open_slots` (`reflection`, phase 9). None
is interrupting.

**Clocks created:** none. (The license fragment names two learning clocks, `clk.learn_tongue` and
`clk.learn_letters`, 8 segments each, in the acquisition paths of tongues and letters; they are
instances of chapter 05's training-clock shape and are created by chapter 15's activities, not here.)

**Runtime capabilities assumed:** RC-STORE, RC-RNG, RC-DATA, RC-QUERY, RC-SCHED, RC-LOG, RC-SEAL.

## Interface requests

**To 00 (architecture; proposed amendments, none needed for this chapter to work as written).**
- **00-1** `effects.yaml` owner-blocks (T-00-19) list 04–11, 15, 16. This chapter needs one entry,
  `eff.02.bent` (`data/effects.yaml owner-block 02`): please add owner-block "02".
- **00-2** The generator (00.11) is used for `gen.birth` with three small extensions, each stated in
  the data header and T-02-14: slots drawn by **layer** (`magnitude_layers`; `mod_group` = layer gives
  the same result under 00.11.3 step 6 alone); `degree: none` for every birth draw (00.11.2 permits it
  "where the domain allows"); an entry-level `excluded_when` (the Bent: attribute at +3, or declined
  before), which is 00.11.3 step 9's cap check moved before the draw. If any is unwelcome, the
  fallback is exact: mod-group exclusion alone yields one knack and one quirk, and the cap step yields
  the same Bent pool with one redraw.
- **00-3** 00's illustrative Wren (WE-00 sheet) is Might +1, Agility +3, Endurance +1, Wits +2,
  Intellect 0, Presence 0, Resolve −1, Vitality 12. Under this chapter that is Wren *after* her Bent
  (creation sum +5, Bent +1 on Endurance); her Vitality is then 12 + 1 = 13. One number in an
  illustrative sheet; no rule conflicts.
- **00-4** 00.4.3 a ("the P1 deferred birth reroll") is the Bent (02.6.5–02.6.7). T-00-4 might note
  that a PC's attribute sum after creation is at most +8 (Typical + Bent) or +9 with chapter 04's tier-4
  increase; each attribute still obeys −2…+4.
- **00-5** Glossary additions: *origin*; *people*, *upbringing*, *livelihood*; *Free rule*, *Typical
  rule*, *shape*, *uncommon of your kind*; *profile*; *held deep* / *held as access*; *knack*,
  *quirk*, *gift* (birth), *the Bent*, *manner* (of childhood); *creation window*, *second look*,
  *lock*; *drive*, *long vow*, *creed*; *bond* (*anchor*, *thorn*); *aspiration*; *the one true
  thing*; *faction tie*; *hook* (creation); *open slot*; *prologue*; *tongue*, *letters*. Note for
  SG-21: this chapter says **quirk**, never "trait", for the birth layer, because `trait` is a tag
  facet; and **livelihood**, never "trade" or "background", because `deed.influence.trade` and chapter
  01's caution-or-ambition trade already use that word. [DL-02-23]
- **00-6** `data/SCHEMAS.md`: record the optional fields of T-02-14 under origins.yaml, gen_birth.yaml
  and kits.yaml; `gen_birth.yaml#output_kind` is `property` for three layers and attribute variance for
  the fourth.
- **00-7** Two out-of-fiction labels are used that 12.15 does not yet list: `[CREATE n/N]` (a creation
  step's pause block; a `[CHOICE]` with a step count) and `[SHEET]` (the character summary). Proposed
  for 12.15 and chapter 14's renderer.

**To 01 (resolution).** A new PC's fate is 1 (done). The tongue grades use a Precision snag and a reach
cap granted by the license's effects (`eff.06.grant_snag`, `eff.reach_step`): these are engine-cited
(the fact is the grade held) and count toward the two-snag limit like any snag. Origin facts and the
one true thing may be cited as levers under 00.3.9 with no special rule.

**To 03 (tags and evidence).** Creation writes **no** evidence; `backstory` is empty on every origin
(DL-02-14 answers DL-03-25's "02 decides"). 03.2.8 is used only for a trained successor (02.2.7 item
4): the tags come from chapter 11's activity, at most three, 24 points each. The Bent reads the *frame
log* (count of resolved frames by deed branch with the PC as actor since creation), never a tally. A
creed's conduct tag is a label for chapter 12's rotation; it is not evidence and has no sign until an
act expresses it.

**To 04 (recognition and growth).** Satisfied: origin competence is at most +2; one livelihood per
magic branch grants a first license with its `requires` met; `gen.birth` grants an innate primal
license (all seven schools, including `deed.primal.elements`); aspirations are `{text, tags}`, at most
three, with up to two tags each. Assumed: the gifted technique in the acquired partition is eligible
for promotion by a pick (05's rule); the tier-4 attribute increase is separate from the Bent and may
raise the same attribute (+3 from the Bent's cap, then +4).

**To 05 (abilities, Focus, magic).** Satisfied: base Focus 3–5 set by upbringing; at most one gifted
ability, acquired partition, rank 1, `source.kind: gift`; each magic livelihood satisfies its
license's `requires`. Decided: no origin grants `lic.focus.reserve` (it stays a thing learned).
Requests: (a) only *Cinder Stride* (fire) and *Stone Shape* exist under `deed.primal.elements`; a
`min_tier: 1` working for water and for air would let a spark of those elements start with its own
element (**met**, revision I-015: Undertow, Heave and Stolen Breath, and the spark grants its element's
working, 02.6.3); (b) issue I-009 (one zero-cost attack working per magic branch) matters most to new
characters: a starting caster has 3–5 Focus and one spell, and this chapter's simulation shows what
happens to one who must fight without it (OEQ-02-10) (**met**, revision I-009: 05.7.11's branch working,
held through the livelihood's training license with no slot; a default-path new caster now beats one T2
90.5–94.8%); (c) confirm that an innate license granted by
`gen.birth` needs no further `requires` (the fact `pc.accepted.primal.<school> = innate` is meant to
satisfy 05.9.4).

**To 06 (conflict).** A new character's Guard runs 10–16 (T-02-1), against the reference P1 line's 14.
Starsight and Cave-eyes are written to 06.3.7's words ("night-sight" in dim light, and in darkness to
`band.close`). Great frame is an edge on two verbs, not a size step. Kits give every martial livelihood
light armor and a one-handed weapon or a bow, as asked.

**To 07 (harm, recovery, death).** Base Vitality is `12 + Endurance` (11–15 at creation; 10–16 over a
lifetime), re-evaluated by `h.07.vitality_max`; the Bent on Endurance raises it by 1. A new PC has
dread 0, no wounds, no marks. A bodily condition chosen at creation uses an `injuries.yaml` entry of
kind `mark` and grants nothing in exchange.

**To 08 (items, loot, crafting).** Resolve each kit line's `item.*` tag to a base item; map the three
assumed quality names `worn` < `common` < `fine` onto your rungs; confirm the coin scale (1 coin = one
day's plain food and lodging) or give the factor. A spellbook is an `item.goods.document` with the fact
`teaches: <ability id>`. A kit's riding horse is an `item.conveyance.mount` of the lowest rung. Great
frame: treat the holder as Might +1 for carrying capacity only. Food ×N in a kit is N days of supply
(with chapter 10).

**To 09 (adversaries).** `threat_advisory` reads `power_band`, and every new character is band 1; but
this chapter's simulation (OEQ-02-10) shows band-1 characters differ widely in a melee: against one T2
foe a new soldier wins 99% and a new acolyte without Focus 31% (90.5% since revision I-009, on her branch
working; a caster who kept a Typical rule with the casting attribute at −1, 62–73%). Please let the advisory read the PC's
actual attack modifier and Guard at band 1 (or rate T2 "hard" for a PC whose best attack is below +3),
so the lethal warning speaks before a scholar is put sword to sword with a soldier.

**To 10 (exploration).** Weather-ache reveals the day's rolled weather at each `day` boundary, after
`h.10.weather` has rolled it. Stonesense answers "which way is down, how deep, which way back"
underground as Certain.

**To 11 (living world).** Consume `CreationHook` records (02.9.7) and own their lifecycle; make a
thread (kind vow) from a long vow and close it as abandoned if the drive is rewritten; map each faction
tie's `org.*` kind to a faction and write its status (+1; or +2 and −2); accept prologue lines
(`chronicle_append`, tag `prologue`); keep the sealed fate of a lost bond for a later clue. For
successors: candidates with recorded origins, one heirloom, the share of renown, legacy results as
hooks and bonds, and the Train-a-Successor activity whose output is the tag list for 03.2.8 (at most
three). Emit `vow_kept` for chapter 01 when a long vow completes.

**To 12 (DM procedures).** Creation is run before the first scene, out of fiction, by PR-02-7. Create
the facets of 02.11.3 as untested. Show an open Bent offer and one open-slot reminder in the SITUATION
block. Bond NPCs are generated at depth recurring with standing **set** by 02.9.2 (an exception to
12.11.2's roll, since a bond is not a first impression). The first "you said" line is the drive. Add
`[CREATE]` and `[SHEET]` to 12.15.

**To 13 (starter setting).** Needed from the region: which peoples are present; a name table per
people; `second_tongue`; the powers an Acolyte may keep, with their faiths; a place of acceptance for a
Hedge-taught character; a faction for each `org.*` kind the origins name (or an explicit "none");
where each bond is placed; at least four pregens passing PR-02-9 (02.2.5); the inciting incident that
pairs with the long vow. Setting origins go in `origins.yaml#blocks` and pass PR-02-9.

**To 14 (player's guide).** Session zero and the preference record (keys in 02.10.1); codex views for
the sheet (PR-02-6), "From birth", "Ties" and "Still open"; the creation tables of this chapter as an
opt-in reference; rendering for `[CREATE]`, `[SHEET]` and the Bent's `[CHOICE]` (no default).

**To 15 (social, investigation, downtime).** Bonds' standing moves by your rules from the set value.
The Retrain activity is the only way to exchange a training after the lock. Learning a tongue or
letters uses `clk.learn_tongue` / `clk.learn_letters` (8 segments; ticks in the license entries). A
lost bond's fate is a sealed fact whose gate is a clue.

**To 16 (companions).** An animal named in a bond is a candidate companion; a hireling's abilities can
be read off a livelihood's default picks.

## Open empirical questions

Each has a shipped default in the rules above and a named test.

| Id | Question | Default shipped | Named test |
|---|---|---|---|
| OEQ-02-1 | Is the fast path fast and sufficient for a newcomer? | five exchanges; three first-use notes (PR-02-7) | **T-02-FAST**: ten people who have never played; measure exchanges and minutes to the first scene, and rules questions asked before it. Targets: median ≤ 5 exchanges, ≤ 6 minutes, 0 questions needed; ≥ 8 of 10 say the character "feels like mine" after session 1 |
| OEQ-02-2 | Is the concept classification reliable? | branch, then livelihood, offer two when unsure (02.2.4) | **T-02-CONCEPT**: 60 one-sentence concepts × 3 independent DM runs; target ≥ 90% agreement on branch and ≥ 85% on the livelihood or the same two-way offer |
| OEQ-02-3 | Is Typical-against-Free a real choice for players? | +7 with three placements decided, against +5 free (02.3.2) | **T-02-P4**: over 50 non-human creations on the full path, the share taking Typical should lie between 40% and 80%; outside it, move a floor or change the sums (inside 00.4.3's envelope there is one step of room: +6) |
| OEQ-02-4 | Are the four profiles all taken? | Focused 2 / Gifted 1+1 / Rounded 1+2 / Broad 0+5 (02.5.2) | **T-02-BREADTH**: over 100 creations no profile below 10% or above 50%; and at session 3 Broad characters report "I could try things" at least as often as Focused ones report "I was good at my thing" |
| OEQ-02-5 | Is the Bent a gamble players enjoy? | three draws, two deferrals, struck entries (02.6.6) | **T-02-BENT**: deferral rate between 15% and 50% of first offers; forgone Bents under 10%; the first offer falls in session 1 or 2 for at least 80% of characters |
| OEQ-02-6 | Does the knack change what players try? | +1 edge on one level-2 tag near the character's life (02.6.2) | **T-02-KNACK**: by session 5, the share of characters with at least five resolved frames under their knack's tag, against the base rate for that tag among characters without it; target at least 1.5 times |
| OEQ-02-7 | Is first recognition timely with no backstory evidence? | tallies start at zero (02.11.1) | **T-02-FIRST**: median session of the first calling offer for focused play; target ≤ 5 (04's simulation: 4). If later, adopt 03.2.8 for deep trainings only and re-test |
| OEQ-02-8 | Is base Focus priced right against knowledge? | Focus 5 = 2 units, 4 = 1, 3 = 0 (02.4.4) | **T-02-FOCUS**: share of Gifted characters choosing a Focus-5 upbringing; if above 70%, price Focus 5 at 3 units (it then buys nothing else) |
| OEQ-02-9 | Is one second look enough, and is it abused? | once, before the first reflection (02.2.6) | **T-02-WINDOW**: share of characters using it (expected 10–30%) and what they change; any use that follows a failed roll by under one scene is logged as a candidate for review |
| OEQ-02-10 | Do the weakest legal characters survive a first fight? | Vitality 11–15, Guard 10–16 (T-02-1) | **T-02-FIRSTFIGHT**: chapter 06's simulation run on this chapter's lines (`_process/simulation/02-character-sim.md`; 20,000 fights a row, no Focus spent). Result now (revision I-009): every martial line beats one T1 foe 100%, two T1 99.8–100%, one T2 98–99.8%; every default-path new caster **using its branch working (05.7.11), no Focus** beats one T1 100%, two T1 98.4–99.3%, one T2 90.5–94.8% (in melee with a staff or mace it was 31–55%); a caster who keeps a Typical rule with the casting attribute at −1 (a choice against the grain, 02.3.5) 62–73% against one T2; the weakest legal line (+1, Guard 10, Vitality 11) 98.9% / 83.5% / 39.3%. Target: no default-path new character meets a fight rated "fair" that it loses more than 15% of the time: **met** (worst 9.5% lost). The against-the-grain lines remain 09's advisory to warn of (it reads the real line, 09.6) |
