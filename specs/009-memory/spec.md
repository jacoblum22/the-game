# Feature Specification: Memory infrastructure (spec 009, part A)

**Feature Branch**: `worktree-agent-abb25593185a07ed6` (spec dir `009-memory`)

**Created**: 2026-10-08

**Status**: Draft

**Input**: Spec 009 part A: established-detail store primitives, scene cards and recap from cards, the spotlight
with an alias index, per-role views with a leak test, and "what did I promise X?" from stored commitments.
Part B (the narration-side profile diff in `mentions.py::_one`, usage marks from declarations, role call sites in
spec 006/007 files) is out of scope.

Rules implemented (look up with `rules/tools/rq.py`; not restated here): 00.6.2 (Fact `certainty: narrated`,
`persistence`), 00.6.6a (established details), 12.2.4 item 3 and its per-role table, 12.4.8 steps 8–9, 12.5.3,
12.14.11 (usage marks: the store half only), DL-12-70, DL-12-72..75, OEQ-12-20..23. Data:
`pacing.yaml#details`, `#packet.view_budget.spotlight` / `.scene_cards`, `#packet.spotlight_k`,
`#packet.max_scene_cards`. Background: `research_notes/Playtest round 2 solutions/A_memory_and_context.md` (P1,
P2, P4, P5, P7, P8, §4), `00_SYNTHESIS.md` §1, §5 Phases 3–4, §7; `rules/_process/reports/R2-E-report.md`
("For the engine spec"), `R2-A-report.md`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A detail, once stated, stays stated (Priority: P1)

Incidental details of people and things (rings, a scar, a posture) are stored in a closed set of slots, one
value per slot. A restatement is a no-op; a change is accepted only when this turn's record explains it, else it
is reported as a contradiction. Scene-only state (held, posture, activity, manner) expires when the scene ends.

**Independent Test**: unit tests on a small store: write new / same / superseded-with-event / contradiction; the
per-entity cap keeps the 8 most salient, then most recently used, lasting details active and archives the rest
(still queryable); `scene` details are gone after the scene ends, with history kept.

**Acceptance Scenarios**:

1. **Given** a merchant with `detail.worn = iron rings`, **When** "iron rings" is written again, **Then** nothing
   is written.
2. **Given** the same, **When** "no rings" is written with no explaining event, **Then** a contradiction is
   reported and the store is unchanged; with an explaining event, the old value is superseded and kept as history.
3. **Given** a guard with `detail.posture = pinned`, **When** the scene ends, **Then** the posture is no longer
   current.

### User Story 2 - Past scenes are remembered as structure, not prose (Priority: P1)

Every ended scene has a card: place, time, cast, agenda and answer, beats (actor, verb, target, degree), facts
written, memories committed, threads touched. Cards are recomputed from the log at will and are identical each
time. A recap reads cards and the chronicle, never an earlier recap. The view carries at most 2 cards about
present or spotlight people, from outside the verbatim window.

**Independent Test**: play scenes, rebuild the projection from events: the cards are equal; `cards_for` ranks by
entity overlap then recency; the recap's state summary lists card lines.

### User Story 3 - Absent people the player names reach the DM, as the PC knows them (Priority: P1)

When the player names someone not in the scene (or the beat targets them, the last delivery named them, the
scene's thread links them, or they are one relationship away), up to 4 such entities enter the view, rendered
with the PC's name for them, the PC's knowledge about them and their last scene card: never world truth, never
sealed content. Full names win over shared first or last names ("Joss Fenn" is not Joss Dunmere or Pell Fenn).

**Independent Test**: unit tests: spotlight order (message, target, last delivery, thread, one hop), K = 4, seals
and unknown names respected, full-name preference; the aged harness's view stays bounded with the spotlight on.

### User Story 4 - Each role sees only what it needs (Priority: P2)

The Narrator sees the PC-knowledge layer (no motives, `truth` or sealed strings); the Reader names, aliases and
the open pause; the Framer the target's and place's profiles, positions, conditions and candidate facts; the
World truth minus seals; the Director threads, clocks, cast weights and cards. The cache-stable packet prefix and
section order are unchanged.

**Independent Test**: a leak test over every Narrator packet of a seeded game; per-role packet sizes measured
before and after on the replay game.

### User Story 5 - "What did I promise X?" (Priority: P2)

The player asks what they promised someone; the answer lists the open commitments involving that person, from
the store, resolved through the alias index.

**Independent Test**: the aged harness's promise probe; a unit test on a store with two similarly named people.

### Edge Cases

- A slot outside the closed list, a subject with no id, or a `scene` slot written from narration: refused.
- A seed `detail`/`appearance` data field (free text, no slot): not mapped here; the DL-12-70 migration needs the
  narration diff's slot declaration (part B).
- A scene reopened (12.4.2): it keeps its id; its card is rebuilt at its next end.
- A sealed spotlight entity: its permitted slice, or nothing.
- Between scenes, recency counts the last two ended scenes (the R2-A "only 2 scenes back" gap).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Fact certainty accepts `narrated`; facts carry an optional `persistence` (lasting | scene | beat).
- **FR-002**: The projection keeps a details index per entity: slot -> current fact id and last-used turn, for
  `detail.<slot>` facts with a value; a `details_used` event sets last use.
- **FR-003**: Active lasting details per entity are capped at `details.max_active`, by salience (2 seeded or
  generated, else 1) then last use; the rest are archived (excluded from views, still current facts, still in the
  contradiction scope).
- **FR-004**: `write_detail` applies one value per slot: new -> write; same -> no-op; different -> supersede only
  with an explaining record reference, else return a contradiction with no write. Slots and persistence come from
  `pacing.yaml#details.slots`.
- **FR-005**: At scene end, before `scene_ended`, every current `scene` / `beat` detail is superseded (cleared),
  history kept (12.4.8 step 8).
- **FR-006**: At `scene_ended` the projection stores the scene's card, folded from the scene's events only, so a
  rebuild reproduces it; recency in the ranked view uses the stored scene starts.
- **FR-007**: `cards_for(state, ids, k=2)` ranks ended scenes by entity overlap then recency; cards render as the
  PC knows them and within `view_budget.scene_cards`.
- **FR-008**: The recap's state summary (12.5.3) includes card lines for scenes since the last recap.
- **FR-009**: An alias index maps PC-known names, aliases and roles to ids; full-name matches win, a single given
  or family name matches only when unambiguous and not part of a full-name match. The journal's "what do I know
  about X" uses it.
- **FR-010**: `spotlight(state, message, last_delivery, beat)` returns up to `packet.spotlight_k` ids outside the
  scene in the 12.2.4 order, never sealed-without-slice; rendered within `view_budget.spotlight`.
- **FR-011**: `view_for(role, state, ctx)` projects one selection per role per the 12.2.4 table; `build_packet`
  uses it for a `WorldState` view, keeping the packet order and the cached prefix.
- **FR-012**: No Narrator packet contains a fact `truth`, a motive (wants, refusals, fears, secrets, knowledge
  pack) or a sealed string (leak test).
- **FR-013**: A "what did I promise X?" question is answered out of fiction from open commitments involving X.

### Key Entities

- **Detail**: a fact `detail.<slot>` with persistence; index entry {fact_id, last_used}.
- **Scene card**: {scene, place, started_at, ended_at, started_seq, cast, agenda, answer, beats[{actor, verb,
  target, degree}], facts[], memories[], threads[]}; projection field `scene_cards`.
- **Spotlight**: an ordered list of up to K entity ids, with the reason each was chosen.

## Success Criteria *(mandatory)*

- **SC-001**: The full test suite passes; ruff and pyright are clean on touched files.
- **SC-002**: `evals/longhorizon.py --mode aged`: Narrator view tokens grow at most 10% from scene 50 to 300 with
  the spotlight and cards on; recall coverage and promise coverage reported against the 0.67 / 0.00 baseline.
- **SC-003**: `--mode scripted` runs with no engine errors.
- **SC-004**: Card regeneration from the log is deterministic (rebuild equality in tests).
- **SC-005**: The leak test passes on every Narrator packet of the seeded test game; per-role packet sizes are
  reported before and after.

## Assumptions

- Clarify skipped by instruction; these stand in for it.
- Usage marks are written only through the `details_used` event; who emits it (the narration diff at RECORD,
  T12) is part B. Salience from "cited in a record line or as a lever" is part B; part A uses source only.
- The explaining event is passed by the caller as a record reference (frame or event id); the writer does not
  judge whether it truly explains the change (part B's diff decides).
- In-scene entities keep their background facts in the Narrator view (they are perceivable now); the strict
  PC-knowledge rendering applies to spotlight entities. Motive keys and predicates are stripped for the Narrator.
- The Reader's schema still offers scene fact ids for G4 though its view no longer lists facts; spec 007's
  computed gate (D P1) owns that.
- The World and Checker packets are built from strings in spec 006's files: their `view_for` / spotlight hookup is
  part B (listed in implementation-results).
- "Outside the verbatim window" is read as "an ended scene": the four verbatim exchanges almost always lie in
  the current scene, which has no card yet.
- The promise question is routed out of fiction in `engine/dm/turn.py` (not a 006/007 file); the Reader's own
  classification is untouched.
