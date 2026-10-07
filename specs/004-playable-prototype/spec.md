# Feature Specification: Playable Prototype

**Feature Branch**: `004-playable-prototype`

**Created**: 2026-10-07

**Status**: Draft

**Input**: User description: "A prototype of the actual game, start to finish, not a session zero. I can
jump in and just play the game the way it was designed, with no limit on turns. Recommend and plan the
tech stack; the first vertical slice resolves freeform action end to end. Built on the rules v1.0 release
candidate in `rules/`."

## Context

Features 001–003 were probes. They showed that a model can keep narration in step with a computed degree
of success, and that its failures are mostly "narrated a change it never recorded". The ruleset
(`rules/`, v1.0 RC) now specifies the whole game: a world built from nothing (12.16), character creation
(ch.02), a 12-step turn loop (PR-12-1), one resolution pipeline for every action (PR-01-1), harm and
death (ch.07), fights (ch.06, ch.09), growth (ch.03–05), journeys and sites (ch.10), items (ch.08), a
living world (ch.11), social play, investigation and downtime (ch.15) and companions (ch.16).

This feature is that game, as a prototype the owner can sit down and play. It is delivered in
**milestones**. Every milestone is a complete game from "new game" to the character's end, with no limit
on how long it is played; each one adds depth to systems the previous one handled coarsely. The first
milestone is the critical one: the whole arc, start to finish, with the universal resolution pipeline
carrying every kind of action.

How the prototype handles a system it has not built yet is fixed and visible: the action still goes
through the one pipeline (01.1.1 says every action does), using the anchor the rules give for it, and any
bookkeeping the rules register for later milestones is logged as "not yet built" rather than silently
skipped.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Start a new game and play it to the end (Priority: P1)

As the player, I start the game and choose "new game". The DM builds a world with me from nothing,
asking only the questions I want to answer and rolling the rest. It then makes my character with me in a
short conversation (or I take a ready-made one), and opens the story with my character in the middle of
something happening. From then on I simply play: I say what my character does, in my own words, for as
long as I like. Scenes open and close, time passes, I move from place to place, meet people the world
generates, ask about things the world has not settled yet, rest, recover, take risks, get hurt, and if
it comes to it, die, always after a plain warning and a choice. When my character's story ends, I get an
epilogue and can start a new character in the same world. I can quit at any moment and pick up exactly
where I left off.

**Why this priority**: This is the request: the actual game, start to finish, playable. Every later
milestone deepens a part of this arc; none of them is worth anything without it.

**Independent Test**: Start a new game with no files, finish creation, play at least 150 turns across at
least 10 scenes and 3 places, including at least one rest, one fight resolved through the pipeline, and
one quit and resume; then take the character to an ending (death, retirement or yield) and confirm the
epilogue and the option to continue the world.

**Acceptance Scenarios**:

1. **Given** no saved games, **When** the player chooses "new game", **Then** the world-seed procedure
   runs in the player's chosen mode (guided, oracle or mixed), shows each step's summary, and only accepts
   a seed that passes the seed check (PR-12-9).
2. **Given** a finished seed, **When** creation starts, **Then** the player can take the five-question
   quick start, the full workshop, or a ready-made character from the seed, and every option they skip is
   filled by the rules' stated default (PR-02-1 to PR-02-7).
3. **Given** a finished character, **When** play begins, **Then** the opening frames a scene at an
   incident, with an open prompt to the player (12.16.16).
4. **Given** play in progress, **When** the player keeps playing, **Then** there is no turn limit: scenes
   are framed and cut by the DM's procedures (12.4), time advances by the mode and activity, and boundary
   bookkeeping runs at every boundary crossed.
5. **Given** the character is in mortal danger, **When** a frame could kill, **Then** the player has had
   the lethal warning and a choice before the roll (07.3), and a character at the Threshold gets the
   last-chance menu (07.5).
6. **Given** the character dies or retires, **When** the story ends, **Then** the player gets an epilogue
   drawn from the record, and can start a new character in the same world or a new world.
7. **Given** a game in progress, **When** the player quits at any point (including in the middle of an
   offer or creation), **Then** resuming restores everything exactly, with a short recap from the record.

---

### User Story 2 - Attempt anything and see it resolved honestly (Priority: P1)

As the player, I type what my character does in my own words. The game works out what I am attempting,
whether I may attempt it at all, and whether it needs a roll. If it does, before anything is rolled it
shows me roughly how hard it is, my chance of success, what is at stake and what failure will cost. I
commit, change my approach, or withdraw. If I commit, the game rolls, records the outcome and its
consequences, and only then narrates what happened, without contradicting the roll or the record.
Talking, asking and trivial actions just happen, without dice. Things my character has no means to
attempt are never narrated as possible, and I always get a way forward.

**Why this priority**: This is the core of every turn in every milestone; User Story 1 is made of it.

**Independent Test**: In any scene, send a risky declaration, a plain question to an NPC, a question about
an unsettled fact, an unlicensed attempt and an impossible one; confirm the offer-before-roll, the honest
outcome, no needless rolls, a once-settled fact staying settled, and a redirect with an alternative for
the last two.

**Acceptance Scenarios**:

1. **Given** a declaration that needs a roll, **When** it is assessed, **Then** the game pauses with an
   offer showing the approach, difficulty, odds, stakes and threatened cost, and nothing has been rolled.
2. **Given** an open offer, **When** the player commits, withdraws, changes method or trades ambition for
   caution, **Then** the game rolls once, or rolls nothing and spends nothing, or shows a fresh offer, as
   the rules say (01.7).
3. **Given** a near miss, **When** the outcome is read, **Then** the player chooses failure or success at a
   cost before anything is narrated (01.9.3).
4. **Given** small talk, a plain question, or a trivial act, **When** it is resolved, **Then** there is no
   roll and no offer.
5. **Given** a fact the world has not settled, **When** the player asks about it, **Then** the Oracle
   settles it once and the answer is recorded and kept.
6. **Given** an unlicensed or impossible attempt, **When** it is gated, **Then** it is not narrated as
   possible, nothing is spent, and the response names at least one actionable alternative (01.3.6, P16).

---

### User Story 3 - The narration never invents or contradicts the record (Priority: P1)

As the player, I can trust what the game tells me: people keep their names and pronouns, counts stay
right, nobody acts without a recorded reason, secrets stay secret until I uncover them, and the narration
never decides what my character says or feels. A draft that gets any of this wrong is fixed before I see
it; after two failed fixes I get a plain, true account instead. Over a long game, things the story
established hundreds of turns ago still hold.

**Why this priority**: A long, unlimited game is only playable if it stays consistent; the probes' failures
were exactly this.

**Independent Test**: Feed the narration step drafts seeded with known errors and confirm each is caught
and fixed or cut; in a 150-turn session, sample turns and confirm no delivered contradiction of stored
state, including facts established early in the session.

**Acceptance Scenarios**:

1. **Given** a draft that contradicts a stored fact, **When** it is checked, **Then** it is rewritten to
   the stored value before delivery.
2. **Given** a draft that describes an unrecorded change, **When** it is checked, **Then** the change is
   cut, never written to match the prose.
3. **Given** a draft that mentions a new, ordinary element, **When** it is checked, **Then** it is recorded
   with only what the draft implies, or cut.
4. **Given** a draft still failing after two redrafts, **When** the turn completes, **Then** the plain
   fallback is delivered and the turn is flagged for review.

---

### User Story 4 - Fights, round by round (Priority: P2)

Milestone 2. Fights run as the rules design them: tempo and surprise, the fixed action pool, position and
range bands, attacks, defenses, reactions, conditions, morale, surrender, escape and chases, against
adversaries built from archetypes and bands whose behaviour the DM never chooses freely (ch.06, ch.09), with
the rest of harm and recovery: wounds, marks, afflictions and dread (ch.07).

**Why this priority**: Milestone 1 resolves fights as ordinary rolled beats, which is playable but flat.
Fights are the most rules-dense part of the game and the first place players notice depth.

**Independent Test**: Start a conflict in a running game, play it to its end by each route (victory,
surrender, escape, defeat), and confirm every round follows PR-06-2 and every adversary turn comes from its
behaviour list.

**Acceptance Scenarios**:

1. **Given** a hostile encounter, **When** conflict starts, **Then** tempo and surprise are determined and
   rounds proceed with the fixed action pool.
2. **Given** an adversary's turn, **When** it acts, **Then** its action comes from its behaviour rules, not a
   free DM choice.

---

### User Story 5 - Growing from what I actually do (Priority: P3)

Milestone 3. My deeds are recorded as evidence, settled at scene ends and reflections, and recognised as
callings and tiers when the pattern is clear, with offers I can accept, decline or defer; abilities, Focus,
magic, rites and training licences work as designed (ch.03, ch.04, ch.05, 15.11).

**Independent Test**: Play a long game leaning on one kind of deed and confirm a recognition offer arrives
through the rules' vehicles, can be accepted or deferred, and grants exactly what the rules say.

---

### User Story 6 - The road and the dungeon (Priority: P4)

Milestone 4. Journeys by the watch with navigation, roles, supply, light, weather and encounter checks;
sites to delve with areas, hazards and traps (ch.10).

**Independent Test**: Travel between two settlements of the seeded region and delve one site, confirming
watches, the time-tick check and encounters follow PR-10-2 to PR-10-7.

---

### User Story 7 - Things worth having (Priority: P5)

Milestone 5. Loot from defeats and finds, buying, selling and haggling, crafting projects, gifts, carrying
and identification (ch.08).

**Independent Test**: Defeat a foe, take its loot, sell it, buy gear and run one crafting project, confirming
each step's output against the generators' reference sims.

---

### User Story 8 - A world that moves without me (Priority: P6)

Milestone 6. Factions take turns each week, situations and bangs develop, threads and hooks fill the quest
register, rumours travel, reputation follows the character, the chronicle records it all (ch.11); lies are
recorded beliefs with sealed truths, investigations run on sealed clue graphs, and negotiations and social
conflicts follow ch.15.

**Independent Test**: Skip three weeks of time and confirm three World Turns ran in full (00.7.7); run an
investigation to its end without a dead end or a leak.

---

### User Story 9 - Companions, downtime and legacy (Priority: P7)

Milestone 7. Recruiting and keeping allies with loyalty and breaking points (ch.16), the downtime week and
long projects (15.10, 15.12), and the full retirement and legacy rules (11.13, 07).

**Independent Test**: Recruit a companion, spend a downtime season, retire the character and start a
successor in the same world who inherits what the rules say.

---

### Edge Cases

- The player sends a new declaration while an offer is open: the open offer is treated as withdrawn.
- A message mixes parts (talk, a question, an action): each part is classified and handled in the rules'
  order (12.2.2).
- The player claims something not established ("there's obviously a rope here"): recorded as context,
  never as a fact (INV-9).
- A declaration bundles more than three actions: at most three resolve; the rest are carried forward or
  asked about.
- The player disputes an earlier response: answered from the turn record, and a real error is corrected
  by a recorded correction (12.3.4).
- The player signals discomfort with content: acted on before anything else, and their lines and veils from
  creation are respected for the rest of the game.
- The player attempts something whose full rules belong to a later milestone (a spell, a journey, a craft):
  it is resolved through the pipeline with the rules' anchor for it, and the "not yet built" bookkeeping is
  logged, never silently dropped.
- A model call fails, times out or refuses: the turn does not half-apply; it completes from the rules'
  defaults where they exist or reports a recoverable error with state unchanged.
- The model returns an option outside what it was allowed to choose: rejected, re-asked once, then the
  rule's default.
- Spending passes the player's budget: the game says so between turns and asks whether to continue; it
  never stops in the middle of a turn and never limits the number of turns.
- Very long games: nothing older than the last four exchanges is sent to a model except through stored
  state (the chronicle, threads, journal, scene header), so turn 2,000 costs about what turn 20 costs.

## Requirements *(mandatory)*

### Functional Requirements

**The game, start to finish (Milestone 1)**

- **FR-001**: The system MUST start a new game from nothing through the world-seed procedure (PR-12-9,
  12.16) in guided, oracle or mixed mode, and accept a seed only when the seed check passes.
- **FR-002**: The system MUST create the player character through the rules' creation paths: the quick
  start, the full workshop and a ready-made character from the seed (PR-02-1 to PR-02-7), including the
  birth draw (PR-02-4), applying every stated default for anything the player skips.
- **FR-003**: The system MUST open play at an incident (12.16.16) and then run unlimited turns, framing and
  cutting scenes by the DM procedures (12.4, PR-12-7), with the pacing director, tension, random events
  and lead injection keeping play moving (12.6–12.8).
- **FR-004**: The player MUST be able to move between places in the seeded region's place graph (10.1),
  with time advancing by the route; full journey rules come in Milestone 4.
- **FR-005**: NPCs MUST be generated on first meeting with name, pronouns and descriptors fixed at
  creation (PR-12-5), and keep a social record (wants, refusals, patience, standing, memories; 15.1–15.2,
  12.11).
- **FR-006**: Harm, the harm states, the lethal warning, yield and retreat, the Threshold and last-chance
  menu, and rest and recovery MUST work as ch.07 specifies (07.1–07.5, 07.8). Death MUST never come without
  a prior plain warning and a choice.
- **FR-007**: Abilities the character starts with MUST be usable as ch.05 specifies (PR-05-1) with Focus
  spent and recovered (05.6).
- **FR-008**: A fight in Milestone 1 MUST resolve through the general pipeline against an adversary
  improvised by the rules' procedure (PR-09-2); round-by-round conflict comes in Milestone 2.
- **FR-009**: When the character's story ends (death, retirement, career end), the system MUST deliver an
  epilogue from the record and offer a new character in the same world or a new world.
- **FR-010**: The player MUST be able to quit at any moment and resume exactly, including mid-creation and
  mid-offer, with a recap built from the record (12.5).
- **FR-011**: The player MUST be able to look up their character's own rules, state and abilities out of
  fiction (the codex, P7), showing exactly what the visibility classes allow (00.6.4).
- **FR-012**: The system MUST NOT limit the number of turns, scenes or sessions.

**Every turn**

- **FR-013**: Every player message MUST run through the turn loop (PR-12-1, T1–T12) in order, stopping only
  at the rules' pause points (12.2.6).
- **FR-014**: Every player message MUST be stored verbatim before processing, and every delivered response
  verbatim after delivery (12.2.5).
- **FR-015**: Each part of a message MUST be classified into the rules' eight classes and handled in the
  rules' order (12.2.2).
- **FR-016**: Each declaration beat MUST go through the resolution pipeline (PR-01-1), at most three beats
  per declaration.
- **FR-017**: Every judgment the AI makes MUST be a choice from a closed list built from the rules and the
  current state. The AI MUST NOT supply any difficulty, modifier, odds, harm amount, tick count, duration or
  price (INV-3, 00.14.3). A choice outside the allowed list MUST be rejected.
- **FR-018**: Difficulty, modifiers, odds, the roll, the degree, reach, cost severity, harm and every other
  number MUST be computed by the system from the rules' tables and the stored state.
- **FR-019**: A rolled beat MUST show an offer before the roll and accept commit, change, withdraw and the
  ambition/caution trades (01.7); the player's auto-commit preference MUST be honoured where allowed (01.7.4).
- **FR-020**: The default-deny gate MUST hold: basic verbs always; anything else needs a held licence;
  unlicensed attempts redirected (G3), impossible ones refused with an alternative (G4).
- **FR-021**: Unsettled facts MUST be settled by the World-Fact Oracle (01.15) and recorded with their source.
- **FR-022**: Precedent MUST be looked up before any adaptation, Oracle call, Good Idea or G3/G4 decision
  (00.15.6).

**State, time and boundaries**

- **FR-023**: All world state MUST live in a durable store that is the single source of truth; every change
  MUST be a recorded write with its source.
- **FR-024**: Sealed state MUST never appear in what the narrator sees, only its permitted slices (00.6.5).
- **FR-025**: Game time MUST follow the time ladder and modes; advancing time MUST fire every boundary
  crossed, in the rules' order and phases (00.7.5–00.7.7).
- **FR-026**: Boundary handlers MUST be dispatched from the rules' registry (`data/boundaries.yaml`); a
  handler not yet built MUST be logged as skipped each time it would run.
- **FR-027**: Every random draw MUST come from a seeded generator and be logged with its purpose.
- **FR-028**: Generators (world seed, birth, NPCs, tables; later loot, gifts, crafting) MUST reproduce their
  reference simulations' behaviour.

**Rules retrieval**

- **FR-029**: Each model call MUST see only the always-loaded core, at most twelve retrieved rule cards, the
  narrator view of state, the player's current message verbatim and the last four exchanges verbatim
  (12.2.4).
- **FR-030**: Cards MUST be retrieved by situation tags, anchors (at most eight candidates) and active
  triggers, in that priority order under the cap.

**Narration and claim check**

- **FR-031**: Narration MUST be drafted only after all of the turn's writes, from the record and a fresh
  narrator view (12.2.8).
- **FR-032**: Every new addressable element in a draft MUST be recorded on mention or cut (00.6.6).
- **FR-033**: Every draft MUST be checked claim by claim before delivery (12.3.1–12.3.2), fixed per verdict,
  and replaced by the plain fallback after two failed redrafts (12.3.3).
- **FR-034**: Claim extraction MUST be a separate model call from narration, with no access to the
  narrator's prompt or reasoning, and swappable to a different model family by configuration alone. Pattern
  P13 requires a different family; the owner chose one provider for now, so that part is deferred as
  `TODO(CROSS_FAMILY_CHECKER)`.
- **FR-035**: Every response MUST pass the T10 screen: intent acknowledged, a next step exists, no line or
  veil crossed, the character not given words or feelings, no numbers or rules words in the fiction, ending
  on an open prompt or one pause block.
- **FR-036**: Content-safety handling MUST be separate from consistency checking, and a SAFETY message part
  MUST be acted on first.

**Record, cost and later milestones**

- **FR-037**: The system MUST record per turn the verbatim input, classifications, frames, rolls, writes,
  claims and verdicts, the delivered response, and every model call with its tokens, cost and latency.
- **FR-038**: A recorded game MUST be replayable from its recorded model outputs and seed with identical
  results and no model calls.
- **FR-039**: The system MUST track spending against a player-set budget, warn between turns when it is
  passed and ask whether to continue; it MUST NOT stop mid-turn or cap turns.
- **FR-040**: Milestones 2–7 MUST each add their chapters' rules (User Stories 4–9) without breaking saved
  games from earlier milestones; their boundary handlers move from "skipped" to "run".

### Out of Scope

Multiplayer of any kind (Principle IV); voice, images or generated art (Principle IV); a graphical or web
interface in Milestone 1 (it is a planned track after Milestone 1); hosting for other players (planned after
the web interface); the optional ch.13 setting (worlds come from the seed procedure).

### Key Entities *(include if feature involves data)*

- **World seed**: the region built at new game: tone, peoples, places, factions, tongues, name tables,
  pregens, secrets, the opening incident (12.16).
- **Place**: a node in the region's place graph with its routes, safety and danger.
- **Player character**: everything creation writes (02.11): attributes, origin, trainings, competences,
  licences, abilities, kit, ties, drive, preferences, Vitality, Focus.
- **Non-player character**: identity, social record, memories, knowledge, standing.
- **Scene**: one continuous situation: place, mode, agenda, hoped answer, cast, situation tags.
- **Fact**: a statement with source, certainty, visibility and validity in time.
- **Clock**, **condition**, **licence**, **commitment**, **thread**: the rules' typed state (00.6.1).
- **Frame**, **offer**, **ruling**: the resolution record of one beat and its precedents.
- **Chronicle and journal**: what the story and the character have recorded, the only memory older turns
  reach the model through.
- **Turn record** and **event**: the append-only history everything is derived from.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A first-time player goes from "new game" to their first in-fiction action in under 15 minutes
  with the quick start (seed in mixed mode plus five creation questions).
- **SC-002**: A single game can be played for at least 500 turns with no turn limit and no growth in
  per-turn cost or latency beyond 20% of the first 50 turns' median.
- **SC-003**: Across the seeded-error test set (at least 40 drafts, at least 3 per verdict), the claim check
  catches at least 90% of seeded errors and flags fewer than 10% of correct claims.
- **SC-004**: In owner playtests of Milestone 1 (at least three games, 150+ turns each, one played as an
  adversarial player), human review of sampled turns finds 0 delivered contradictions of stored state,
  including facts established more than 100 turns earlier, and the plain fallback appears on fewer than 5%
  of turns.
- **SC-005**: 100% of rolled outcomes use numbers computed by the system; 0 numbers in any frame come from
  the AI; 100% of rolled beats show an offer first (or auto-commit where allowed).
- **SC-006**: 100% of character deaths are preceded by the lethal warning and a choice.
- **SC-007**: 100% of unlicensed and impossible attempts get an actionable alternative and are not narrated
  as possible.
- **SC-008**: Quitting and resuming at any point restores the game exactly; a replay of every recorded test
  game reproduces it exactly with no model calls.
- **SC-009**: A rolled declaration shows its offer within 5 seconds and a non-pausing turn completes within
  10 seconds (median).
- **SC-010**: Median model cost per turn is at most 3 US cents at current prices.
- **SC-011**: The owner, after a Milestone 1 playtest, judges that it plays as "the actual game" rather than a
  test harness (a yes/no recorded in the results).

## Assumptions

- The rules v1.0 release candidate on `integration-wave-swxsot` is the source of truth. The prototype reads
  `rules/` and never modifies it; code cites rule ids so rules changes show what is stale. Rule fixes found
  while building go to the rules thread.
- The open MAJOR issues stay open while building. I-038 (Oracle fishing) touches Milestone 1, so the engine
  caps free Oracle questions per scene by a setting and logs every call; I-040 and I-041 touch fights and
  rematches (Milestone 2).
- Ch.14 (the Player's Guide and in-game codex presentation) is unwritten; Milestone 1 shows the codex as
  plain out-of-fiction text.
- One player per game (Principle IV). Milestone 1 is played in a terminal on the owner's machine.
- One model provider (Google Gemini, one API key) for every role, by owner decision (2026-10-07). The checker
  therefore shares the narrator's family, which Pattern P13 forbids. This is a recorded, temporary deviation,
  `TODO(CROSS_FAMILY_CHECKER)`; the checker's recall is measured on seeded errors (SC-003), and moving it to
  another family must be a configuration change only.
- Automated tests never call a paid model. Playtests are played by the owner or scripted personas.
