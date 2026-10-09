# Feature Specification: Dialogue and texture (spec 013; S1 + S2)

**Feature Branch**: worktree branch (spec dir `013-dialogue-texture`)

**Created**: 2026-10-08

**Status**: Draft

**Input**: Owner ruling 2026-10-09 ("I definitely agree with S1 and S2"; structural fixes over patches).
Scope: `rules/_process/reports/R2-H-report.md`, "Engine checklist → Spec 013", items 1-9. Rules implemented (look up
with `rules/tools/rq.py`; not restated): PR-12-10, PR-12-12, 12.10.8, 12.11.9, 12.14.12, 12.3.1a, 12.3.1b, 01.6.8,
DL-12-90..93; data `pacing.yaml#answer_ladder`, `#testimony`, `#npc.activity`, `#npc.responds`,
`#narration.must_name`, `social.yaml#event_tags.concerns`.

Evidence: `evals/playtests/20261008-145410-claude-talker.md` (re-run) and `20261008-135029-claude-talker.md`:
"I don't know …, but X would" runarounds (8 turns, then 2), a name given then denied (Nibwen / Laendil), lines
repeated verbatim ("Tibgit Lucky" ×4, "day wages" ×3), idle activity lines every turn, officers beating rugs in a
hall, non-addressed NPCs interjecting (Ysrion with his back turned; Nibwen's second cup), stilted refusals.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - NPCs talk like people (Priority: P1)

The player asks an NPC an ordinary question. Code decides only whether the NPC is willing (checklist item 2); the
narrator answers in the NPC's voice from a speaker card (item 3): what they know, their role's common knowledge,
public news, and what they have already said. No code line says "does not know X, but Y would" (item 1).

**Acceptance Scenarios**:

1. **Given** an NPC asked "where is the smithy?", **When** the turn resolves, **Then** the record holds one
   willingness line `{npc, question, willingness, reason}` and no pointer, and the narrator's message holds a
   speaker card for that NPC with no sealed fact, undelivered placement or motive.
2. **Given** a recorded refusal whose tags match the question, **Then** willingness is `unwilling` with the refusal
   as its reason; **given** a Neutral or warmer NPC and an ordinary question, **Then** `willing` without a roll.
3. **Given** a question about a case (a story role, the incident), **Then** it still goes only through the case
   graph: a holder delivers, a non-holder names the core holder (unchanged).

### User Story 2 - NPCs remember what they said (Priority: P1)

Every spoken NPC line is a `said` record `{speaker, turn, words, about, question}` (item 4), fed back on the
speaker card next turn. A drafted line that repeats one of the speaker's own `said` lines is redrafted
(`not_a_repeat`).

**Acceptance Scenarios**:

1. **Given** Nibwen said "Laendil learned their trade from Tibgit Lucky", **When** he is asked about Laendil
   again, **Then** his card shows that line and the narrator is told never to contradict or repeat it.
2. **Given** a draft where a speaker's quoted words overlap one of their `said` lines above
   `narration.freshness.said_overlap` (0.6), **Then** the sentence is redrafted.

### User Story 3 - Testimony becomes truth only when it matters (Priority: P2)

PR-12-12 (item 5): when the player relies on testimony (the Reader's `rests_on`, a target known only from a `said`
record, travel to a place named only in testimony), one call states the claim and code settles it: the case for a
consequential claim (never delivering a clue), the Oracle at Likely beyond the ordinary, else accepted. The `said`
record is marked settled once.

**Acceptance Scenarios**:

1. **Given** a beat whose Reader `rests_on` names a `said` id, **Then** a fact `source: testimony` (or `oracle`)
   is written before the beat frames, and the record is settled; **a second reliance settles nothing**.
2. **Given** a claim touching a case node the case does not hold, **Then** it is false and written as
   `npc.<id>.wrong_about`; no clue is delivered.

### User Story 4 - Only what matters is mandatory (Priority: P1)

Must-name (item 6) is the closed list: beat outcome, applied change and cost, what changed, the direct-question
answer line, a clue or lead, a pause. Activities, postures, manners and other NPCs' reactions are optional material,
shown without handles. Activities are rolled once per scene from the role's own cell and end on engagement; an
ended activity is never a lever (item 7). Only addressed or concerned NPCs respond (item 8).

**Acceptance Scenarios**:

1. **Given** a scene with three NPCs, **When** the PC talks to one for three turns, **Then** each NPC's activity
   was rolled once, the addressed one's ended on engagement and was not re-rolled, and no activity is must-name.
2. **Given** an ended activity, **Then** its fact is not offered to the Framer as a lever.
3. **Given** the PC talks to Nibwen and mentions nobody else, **Then** no other present NPC responds; **given** the
   player's words name Ysrion, **Then** Ysrion is concerned (`concerns_self`) and his reaction is optional material
   (a deed, no speech), never must-name.
4. **Given** plain speech or a question to an addressed NPC, **Then** no `tbl.npc_action` talk wording ("asks the
   PC something", "wants something first") is a record line; the row gives willingness only.

### Edge Cases

- A question asked of no one present: no answer line, no pointer (the narrator may have the PC look around).
- An NPC with no role cell: activity from `other`; never another role's rows.
- A `said` record already settled: never settled again; its fact is citable.
- Recall with nothing stored: "you recall nothing more" (no pointer, no Proposer).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001** (item 1): Retire the ladder as a speech source: `rungs_for`, `store_hit`, `pack_hit`, `ratify`,
  `point`, `_walk_on`, `_kept_at`, `_chain_logged`, `_pointer_said`, `_can_answer`, `_touches`, `ladder_owns`, the
  rung loop; delete `roles/proposer.py`, its prompt and schema; remove `answer_ladder.repeat_pointer_limit` and
  `delivery.information.ladder_depth`. Keep the case route, casting and `volunteer`.
- **FR-002** (item 2): Willingness by PR-12-10 step 2 (refusal tags, Talk frame, certainty test, row band).
- **FR-003** (item 3): Speaker card for the asked/addressed NPC; leak-free; narrator guidance on hearsay, rare
  "I don't know" and never contradicting or repeating `said` lines.
- **FR-004** (item 4): `said` records in state, index `(npc, question_kind, topic) → said ids`; `not_a_repeat`.
- **FR-005** (item 5): PR-12-12 triggers (a) and (c) with one `[J:enum]` claim call and three routes.
- **FR-006** (item 6): Must-name diet; optional material section; retire `hide_stale`.
- **FR-007** (item 7): Activities once per scene, own role cell else `other`, end on engagement; not levers once
  ended.
- **FR-008** (item 8): Responders = addressed ∪ concerned (tag in `event_tags.concerns`) ∪ fight targets; no
  per-present-NPC response; talk wordings never record lines for speech.
- **FR-009** (item 9): Tests per the brief; OEQ-12-25 metric counts in `evals/longhorizon.py`.

### Key Entities

- **said record**: `{id, speaker, turn, words, about, question, settled, fact}` in meta `npc.said`.
- **willingness line**: an `NpcActionEntry` (`source: talk_outcome`, `source_ref: PR-12-10`, tag
  `willingness:<band>`), must-name.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A runaround ("I don't know …, but X would") cannot be produced by code (no pointer path remains).
- **SC-002**: In a 15-turn talker playtest: "I don't know" turns ≤ 2 (re-run baseline 2/15), verbatim NPC line
  repeats fewer than the baseline (Tibgit ×4, day wages ×3), no interjection by a non-addressed NPC.
- **SC-003**: Offline long-horizon (scripted) run: 0 engine errors.
- **SC-004**: Full test suite passes.

## Assumptions

- PR-12-12 triggers (b) (a lever citing a `said` id) and (d) (a frame input reading the claim) are deferred: the
  Framer's candidate list and typed frame inputs belong to specs 016 and 015; an unsettled `said` record is never a
  fact id, so frame_check already refuses it as a lever.
- Willingness for a question that fails the certainty test reads the rolled row as a band (1-3/4-6/7-10).
