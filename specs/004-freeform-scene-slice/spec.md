# Feature Specification: Freeform Scene Slice

**Feature Branch**: `004-freeform-scene-slice`

**Created**: 2026-10-07

**Status**: Draft

**Input**: User description: "First vertical slice of the real engine: one scene of freeform action
resolved end to end (the PR-12-1 turn loop T1–T12, the PR-01-1 resolution pipeline, the OFFER pause,
the roll, state writes, narration and the claim check). Built on the rules v1.0 release candidate in
`rules/`."

## Context

Features 001–003 were probes. They showed that a model can keep narration in step with a computed
degree of success, and that its failures are mostly "narrated a change it never recorded". The
ruleset (`rules/`, v1.0 RC) now specifies the engine those probes were testing towards: a typed
state store, a 36-tool surface (00.14), a 12-step turn loop (PR-12-1), an 11-step resolution
pipeline (PR-01-1), a boundary registry (00.7, `data/boundaries.yaml`) and rule-card retrieval
(00.15).

This feature is the first slice of that engine. It is deliberately **narrow and deep**: one scene,
one player character, one place, a small cast, but every step of a turn done the way the rules say.
Breadth (combat, magic, travel, character creation, progression) comes in later slices.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Attempt something risky and see it resolved honestly (Priority: P1)

As a player in a scene, I type what my character does in my own words ("I wait for the keeper to
look away, then climb the bridge rail and drop onto the barge below"). The game works out what I
am attempting, whether I may attempt it at all, and whether it needs a roll. If it does, before
anything is rolled it shows me what I am up against: roughly how hard it is, my chance of success,
what is at stake and what failure will cost. I commit, change my approach, or withdraw. If I commit,
the game rolls, records the outcome and its consequences in the world's state, and then narrates
what happened, without contradicting the roll or the recorded state.

**Why this priority**: This is the whole bet of the ruleset in one interaction: the player can try
anything, the AI rules correctly, and the narration never runs ahead of the record. Every later
slice reuses this path.

**Independent Test**: Load the scene, send one risky declaration, commit at the offer, and check
(a) an offer was shown before any roll, (b) the outcome is one of the four degrees computed from the
roll and the shown difficulty, (c) every consequence the narration mentions is in the state record,
and (d) nothing in the state record changed that the narration or the offer did not account for.

**Acceptance Scenarios**:

1. **Given** a scene with a locked gate and a toll keeper, **When** the player declares an action
   that needs a roll, **Then** the game pauses with an offer showing the approach, difficulty, odds,
   stakes and the threatened cost, and no die has been rolled yet.
2. **Given** an open offer, **When** the player commits, **Then** the game rolls once, computes the
   degree by the ruleset's degree rule, applies the declared cost at the severity the ruleset gives
   for that degree, records it, and narrates an outcome consistent with the degree and the record.
3. **Given** an open offer, **When** the player withdraws, **Then** nothing is rolled, no time
   passes and no state changes.
4. **Given** an open offer, **When** the player changes their method instead, **Then** the game
   re-assesses the new method and shows a new offer.
5. **Given** a roll that lands one short of success (a near miss), **When** the outcome is read,
   **Then** the player is asked to choose between failure and success at a cost, as the rules
   require, before anything is narrated.

---

### User Story 2 - Talk, ask and act without needless rolls (Priority: P2)

As a player, I can greet someone, ask the keeper a plain question, ask what my character notices,
or do something trivial, and the game answers in the fiction without rolling dice or showing an
offer. When I ask about something the world has not settled yet ("is the barge crewed?"), the game
settles it fairly (by the ruleset's oracle) and remembers the answer.

**Why this priority**: Most turns in play are not risky checks. If these turns are slow, rolled, or
inconsistent, the game feels wrong even if checks are perfect.

**Independent Test**: Send a greeting, a plain question to an NPC, a perception question about the
scene, and a question about an unsettled fact; confirm no offers were shown, the unsettled fact was
settled once and recorded, and asking the same question again gets the same answer.

**Acceptance Scenarios**:

1. **Given** the scene, **When** the player sends in-character small talk, **Then** the game
   responds in the fiction with no roll and no offer.
2. **Given** a fact the scene has not established, **When** the player asks about it, **Then** the
   game settles it once through the oracle, records it with its source, and later turns treat it as
   established.
3. **Given** a declaration that needs no roll (trivial, or with nothing at stake), **When** it is
   resolved, **Then** it simply happens, is recorded, and is narrated.

---

### User Story 3 - Be redirected, never refused into a dead end (Priority: P2)

As a player, when I try something my character has no means to attempt ("I cast a spell to unlock
the gate", with no magic), or something impossible given what is established, the game does not
pretend it worked and does not just say no. It tells me in the fiction why not and offers the
nearest thing I can actually attempt, or names how such a thing could be learned.

**Why this priority**: The default-deny gate (Principle VII) and the no-dead-ends rule (P16) are
what keep "try anything" from becoming "anything works". They must hold from the first slice.

**Independent Test**: Send an unlicensed declaration and an impossible one; confirm neither is
narrated as possible, each response contains at least one actionable alternative, and no time or
resources were spent unless the player accepted an alternative.

**Acceptance Scenarios**:

1. **Given** a character with no licence for magic, **When** the player declares a spell, **Then**
   the attempt is not narrated as possible, the game offers the closest basic alternative (if the
   rules list one) and names at least one way such an ability could be acquired.
2. **Given** an established fact that rules an action out, **When** the player declares it, **Then**
   no roll happens and the response explains why in one sentence of fiction and offers the nearest
   achievable intent.

---

### User Story 4 - The narration never invents or contradicts the record (Priority: P1)

As a player, I can trust what the game tells me: people keep the names and pronouns they were given,
counts of things stay right, nobody acts without a reason the game recorded, secrets are not
blurted out, and the narration never decides what my character says or feels. If a draft of the
narration gets any of this wrong, the game fixes it before I see it; if it cannot fix it after two
tries, it gives me a plain, dull but true account instead.

**Why this priority**: The probes' only real failures were narration getting ahead of the record
(Feature 002) and an invented detail the narrator's own self-check missed (Feature 001). This
check is the safeguard, and it must be independent of the narrator.

**Independent Test**: Feed the narration step drafts seeded with known errors (a changed pronoun, an
unrecorded change, a leaked secret, words put in the character's mouth) and confirm each is caught
with the right verdict and fixed or cut before delivery; confirm the plain fallback is used when a
draft cannot be fixed in two redrafts.

**Acceptance Scenarios**:

1. **Given** a draft that contradicts a stored fact, **When** it is checked, **Then** it is rewritten
   to the stored value before delivery.
2. **Given** a draft that says something changed with no recorded source, **When** it is checked,
   **Then** the change is cut from the narration and is not written to state.
3. **Given** a draft that mentions a new, ordinary piece of scenery, **When** it is checked, **Then**
   the new element is recorded with only the properties the draft implies, or cut.
4. **Given** a draft that still fails after two redrafts, **When** the turn completes, **Then** the
   player receives the plain fallback and the turn is flagged for review.

---

### User Story 5 - End the scene and review the session (Priority: P3)

As a player, when the scene's question is answered or I move on, the scene closes properly: time
has advanced by what the actions took, the scene's end-of-scene bookkeeping runs, and the session
can be saved, closed and resumed exactly where it was. As the developer, I can open the record of
any turn and see the verbatim message, every judgment made, every roll, every state change and every
claim-check verdict, and I can replay a recorded session and get identical state.

**Why this priority**: Without a faithful record and replay, no later tuning or model change can be
evaluated; and without scene end, time and boundaries are never exercised.

**Independent Test**: Play a scene to its end, quit, resume, and confirm the state is identical;
replay the recorded session with recorded model outputs and confirm byte-identical state.

**Acceptance Scenarios**:

1. **Given** a scene whose question has been answered, **When** the turn completes, **Then** the
   scene end is marked, the registered end-of-scene steps that this slice covers run in the
   ruleset's phase order, and steps outside the slice are logged as skipped (never silently
   ignored).
2. **Given** a saved session, **When** it is resumed, **Then** the state, time, open pause and recent
   exchanges are exactly as they were.
3. **Given** a recorded session, **When** it is replayed with the recorded model outputs, **Then**
   every roll, state change and delivered response is identical.

---

### Edge Cases

- The player sends a new declaration while an offer is open: the open offer is treated as withdrawn
  (nothing spent) and the new declaration is resolved.
- The player's message mixes parts ("Evening. Is this the toll? I slip past while he answers."): each
  part is classified and handled in the ruleset's order.
- The player claims something not established ("there's obviously a rope here"): the assertion is
  recorded as context, never as a fact, and gives no advantage unless the world already holds it.
- A declaration bundles more than three actions: at most three are resolved; the rest are carried
  forward or asked about.
- The player disputes an earlier response ("you said the gate was open"): the answer comes from the
  turn record, never from memory, and any genuine error is corrected by a recorded correction.
- The player signals discomfort with content: the game acts on it before anything else in the turn.
- A model call fails, times out or refuses: the turn does not half-apply; it either completes from
  the engine's defaults where the rules define one or reports a recoverable error with state unchanged.
- The model returns an identifier, option or number outside what it was allowed to choose: it is
  rejected and re-asked once, then the rule's stated default is used.
- A per-session spending cap is reached: the session pauses cleanly with state saved.

## Requirements *(mandatory)*

### Functional Requirements

**Turn and pipeline**

- **FR-001**: The system MUST run every player message through the ruleset's turn loop (PR-12-1,
  steps T1–T12) in order, stopping only at the pause points the ruleset lists (12.2.6) that are in
  scope for this slice.
- **FR-002**: The system MUST store every player message verbatim before any other processing and
  every delivered response verbatim after delivery (12.2.5).
- **FR-003**: The system MUST classify each part of a message into the ruleset's eight message
  classes (12.2.2) and handle the parts in the ruleset's order.
- **FR-004**: The system MUST resolve each declaration beat through the ruleset's resolution pipeline
  (PR-01-1): parse, gate, necessity, anchor, frame, offer, roll, read, consequence and record; at most
  three beats per declaration.
- **FR-005**: Every judgment the AI makes MUST be a choice from a closed list built from the ruleset
  and the current state (ids, enum values, rungs, flags, short text). The AI MUST NOT supply any
  difficulty, modifier, odds, harm amount, tick count, duration or price (INV-3, 00.14.3). A choice
  outside the allowed list MUST be rejected.
- **FR-006**: Difficulty, modifiers, odds, the roll, the degree, delivered reach and cost severity
  MUST be computed by the system from the ruleset's tables and the stored state, never by the AI.
- **FR-007**: A rolled beat MUST show an offer before the roll (01.7.1) and MUST accept commit,
  change, withdraw and the ruleset's ambition/caution trades (01.7.3). A player preference for
  auto-commit (01.7.4) MUST be honoured where the ruleset allows it.
- **FR-008**: The system MUST apply the default-deny gate: basic verbs are always available; anything
  else needs a held licence; unlicensed attempts are redirected (G3) and impossible ones are refused
  with an alternative (G4), with no time or resources spent unless an alternative is accepted.
- **FR-009**: Questions about unsettled facts MUST be settled by the ruleset's World-Fact Oracle
  (01.15) and recorded with their source; the same question MUST then get the same answer.
- **FR-010**: Before any adaptation of an anchor, oracle call, Good Idea or G3/G4 decision, the system
  MUST look up precedent in the ruling ledger and reuse a matching ruling's numbers unless a stated
  fact differs (00.15.6).

**State, time and boundaries**

- **FR-011**: All world state MUST live in a durable store that is the single source of truth; no
  state may exist only in the narration or in the AI's context. Every change MUST be a recorded write
  with its source.
- **FR-012**: Sealed (secret) state MUST never appear in what the narrator sees; only its permitted
  slices may (00.6.5).
- **FR-013**: The system MUST keep game time on the ruleset's time ladder and advance it by the time
  mode and activity durations the ruleset gives; advancing time MUST fire every boundary crossed, in
  the ruleset's order and phases (00.7.5–00.7.7).
- **FR-014**: Boundary handlers MUST be dispatched from the ruleset's handler registry
  (`data/boundaries.yaml`). Handlers this slice does not implement MUST be logged as skipped each time
  they would have run.
- **FR-015**: Every random draw MUST come from a seeded generator and be logged with its purpose, so a
  session can be replayed exactly.

**Rule retrieval**

- **FR-016**: For each turn the AI MUST see only the always-loaded core, at most twelve retrieved rule
  cards, the narrator view of state, the player's current message verbatim and the last four exchanges
  verbatim (12.2.4); nothing older except through stored state.
- **FR-017**: Rule cards MUST be retrieved by the scene's situation tags, the anchors matching the
  beat's verb and tags (at most eight candidates), and active triggers, with triggers first, then
  anchors, then situation cards, under the cap.

**Narration and claim check**

- **FR-018**: Narration MUST be drafted only after all of the turn's state writes, from the
  adjudication record and a fresh read of the narrator view (12.2.8).
- **FR-019**: Every new addressable element a draft introduces MUST be recorded on mention or cut
  (00.6.6).
- **FR-020**: Every draft MUST be checked claim by claim against the store before delivery, using the
  ruleset's claim classes and verdicts (12.3.1–12.3.2), fixed per verdict, re-checked, and replaced by
  the plain fallback after two failed redrafts (12.3.3).
- **FR-021**: Claim extraction MUST be a separate model call from narration, with no access to the
  narrator's prompt or reasoning, and MUST be swappable to a different model family by configuration
  alone. Pattern P13 requires a different family; for this slice the owner chose a single provider, so
  that requirement is deferred and tracked as `TODO(CROSS_FAMILY_CHECKER)` (see Assumptions).
- **FR-022**: Each delivered response MUST pass the ruleset's screen (T10): the player's intent is
  acknowledged, a next step exists, no line or veil is crossed, the character is not given words or
  feelings, no numbers or rules words appear in the fiction, and it ends on an open prompt or exactly
  one pause block.
- **FR-023**: Content-safety handling MUST be separate from consistency checking (P13), and a SAFETY
  message part MUST be acted on before anything else in the turn.

**Session, record and evaluation**

- **FR-024**: The system MUST record, per turn, the verbatim input, classifications, every frame, every
  roll, every state write, every claim and verdict, the delivered response, the model calls made, their
  token use, cost and latency.
- **FR-025**: A session MUST be saveable and resumable at any point, including mid-offer.
- **FR-026**: A recorded session MUST be replayable from its recorded model outputs and seed, producing
  identical state and responses, without calling any model.
- **FR-027**: The system MUST enforce a per-session spending cap and stop cleanly, with state saved,
  when it is reached.
- **FR-028**: The scene end MUST be marked when its question is answered or the player moves on, and
  the end-of-scene steps in scope MUST run (PR-12-7).

### Out of Scope

Combat and conflict rounds; abilities, Focus and magic beyond the licence check; harm beyond the cost
menu's harm entry at the severities a single scene reaches; travel, sites and encounter checks;
character creation (the slice uses a prepared character); the world seed (the slice uses a prepared
scene); progression and recognition beyond recording evidence events; companions; downtime; loot,
crafting and the other generators except the Oracle and table rolls; ranking of bundled beats
(declaration order is used, as the ruleset's default); multiplayer of any kind (Principle IV); any
graphical interface or hosting.

### Key Entities *(include if feature involves data)*

- **Scene**: one continuous situation with a focus: place, time mode, agenda, the character's hoped
  answer, cast present, situation tags.
- **Player character**: a prepared character sheet: attributes, competences, licences, vitality,
  possessions, conditions.
- **Non-player character**: identity (name, pronouns, descriptors), wants, refusals, memories of the
  player character, knowledge.
- **Fact**: a subject–predicate–value statement with its source, certainty, visibility and the time
  it became true (and stopped being true).
- **Clock**: a progress track that ticks only from listed sources and shows omens.
- **Frame**: the full record of one beat's resolution from parse to record; immutable from the roll on
  except for the read/consequence/record fields.
- **Offer**: what the player was shown before a roll and their answer.
- **Ruling**: a precedent record of an adapted or improvised ruling.
- **Turn record**: the verbatim exchange plus everything decided, rolled, written and checked.
- **Rule card**: one numbered rule packaged for retrieval, with its situation tags, trigger and anchor.
- **Event**: one append-only entry in the session's history; all state is derived from events.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a scripted 30-turn session over the slice scene, 100% of rolled outcomes use a
  difficulty and modifier computed by the system, and 0 numbers in any frame come from the AI.
- **SC-002**: 100% of rolled beats show an offer before the roll (or auto-commit where allowed), and 0
  rolls happen after a withdraw.
- **SC-003**: Across the seeded-error test set (at least 40 drafts, at least 3 per verdict), the claim
  check catches at least 90% of seeded errors, and fewer than 10% of correct claims are flagged.
- **SC-004**: In live play of the slice scene (at least 3 sessions of 20+ turns, including one played
  by an adversarial persona), 0 delivered responses contain a contradiction of stored state found on
  human review, and the plain fallback is used on fewer than 5% of turns.
- **SC-005**: 100% of unlicensed and impossible declarations in the test set are not narrated as
  possible, and 100% of those responses offer at least one actionable alternative.
- **SC-006**: A replay of every recorded test session reproduces state and responses exactly, with no
  model calls.
- **SC-007**: A typical turn without a pause completes in under 10 seconds, and a rolled turn shows its
  offer in under 5 seconds (median over the live sessions).
- **SC-008**: Median model cost per turn is at most 3 US cents, reported per call and per turn; no
  session exceeds its spending cap.
- **SC-009**: Every turn's record lets a reviewer answer "why did this happen?" for every state change
  without reading the narration.

## Assumptions

- The rules v1.0 release candidate on `integration-wave-swxsot` is the source of truth. The slice reads
  `rules/` and never modifies it. Rule ids are cited in code so later rules changes show what is stale.
- The open MAJOR issue I-038 (Oracle fishing) touches this slice. Until the rules fix it, the slice caps
  free Oracle questions per scene with a configurable limit and logs every call, so its effect can be
  measured; the cap is an engine setting, not a rules change.
- One prepared scene is enough to exercise the full turn: a toll bridge at dusk with a locked gate, a
  toll keeper (an NPC with a want and a refusal), a moored barge, a sealed secret, one visible clock and
  one hidden fact the Oracle can settle. It uses no content from the optional ch.13 setting.
- One prepared player character, built by hand to the ch.02 rules and validated against `data/`.
- The player plays alone (Principle IV). A text interface in a terminal is sufficient for this slice.
- Live sessions are played or scripted by the developer; automated tests never call a paid model.
- One model provider (Google Gemini, one API key) for every role in this slice, by owner decision
  (2026-10-07), to keep setup simple. The checker therefore shares the narrator's family, which Pattern
  P13 forbids. This is a recorded, temporary deviation, `TODO(CROSS_FAMILY_CHECKER)`: the slice measures
  the checker's recall on seeded errors (SC-003) so the cost of the deviation is known, and moving the
  checker to another family must be a configuration change only.
