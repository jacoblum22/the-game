# Feature Specification: Content seed, casting and the reduced case (spec 008, part A)

**Feature Branch**: `worktree-agent-a057e6ec4e10abb58` (spec dir `008-content-seed-casting`)

**Created**: 2026-10-08

**Status**: Draft

**Input**: Spec 008 part A: world seed packs, casting, the reduced case builder, I-149, retiring the seed-time
incident binding, and the "names exhausted" fix. Part B (the answer ladder, PR-12-10) is out of scope.

Rules implemented (look up with `rules/tools/rq.py`; not restated here): 12.16.9, 12.16.11, 12.16.16, 12.16.17
(seed-pack checks), 12.4.3 (layout read from the store), 00.11.1 (`cast` domain), PR-15-6 and 15.9.4 (reduced
profile), 12.10.2 (I-149), DL-12-60..63, DL-15-38. Data: `world_seed.yaml` (`tbl.12.seed.place_look`,
`.furniture`, `.document`, `.knowledge_pack`, `#pack_requirements`), `social.yaml#cast` / `#common_knowledge`,
`investigation.yaml#reduced_case`. Reference implementation: `rules/_process/simulation/12-world-seed.py`
(`seed_packs`, `reduced_case`, `validate_case`, `check_packs`, `role_key`, `keyed`). Background:
`research_notes/Playtest round 2 solutions/00_SYNTHESIS.md` §1.1, §4 (D1, D2, D4), §5 Phase 3, §7;
`C_content_contract_npcs.md` §4.3, §4.5; `rules/_process/reports/R2-D-report.md`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The opening has real material (Priority: P1)

A new game's world has, for every place, a one-line look, 2–4 furniture items and its exits; for every cast
NPC, 2–4 knowledge facts and a stance toward the incident; and posted notices with real text. The narrator
describes the present place from that stored material instead of inventing a layout.

**Why this priority**: every later piece (the answer ladder, established details) needs the material (synthesis
§5 Phase 3: packs come first).

**Independent Test**: build a seed; the 7 pack checks pass; the engine's packs equal the reference's on the
same seed; the opening scene's setting lists the present place's look, furniture and exits.

**Acceptance Scenarios**:

1. **Given** seed N, **When** the world is built twice, **Then** packs, documents and the case are identical.
2. **Given** a packed world, **When** the seed check runs, **Then** all 64 + 7 requirements hold.
3. **Given** the hire lead, **When** its notice is read, **Then** its text names who to see and where.

### User Story 2 - The inciting incident is a real case (Priority: P1)

The incident's subject is cast from the existing people where the role fits (else generated), with two
necessary conclusions, three placements each, one core placement at the opening place and one reserve.
"Who is missing?" is answered from the case, never by a uniform-random pick.

**Independent Test**: over 30 seeded openings the incident case validates and its core placement is held at the
opening place by someone who is there; asking "who is missing" names the case's subject.

**Acceptance Scenarios**:

1. **Given** a seeded opening, **When** the PC asks who the incident's subject is, **Then** the answer is the
   case's subject and asking again gives the same answer.
2. **Given** a story-role question with no case behind it, **When** the on-demand builder runs, **Then** a valid
   reduced case is written with its entry core placement where the question was asked.
3. **Given** a reduced case whose holders die or leave, **When** a scene ends, **Then** the placement audit
   places the reserve (then a generic placement) so each unfound necessary node keeps at least 2 live
   placements.

### User Story 3 - Casting answers "who is <role>" (Priority: P2)

A "who is <role>" or "who would know" question picks an existing person gated by role, scope and seal and
weighted by fit; an empty pool yields generation or "no one you know".

**Independent Test**: unit tests on a small store: the gate excludes the PC, the anchor bond, sealed people and
far powers; a role match is preferred; the same question casts the same person.

### User Story 4 - A local knows the haven's names; long games never run out of names (Priority: P2)

A PC whose anchor bond lives in the haven starts knowing the names of the haven's officers and of the heads of
factions seated there (I-149). A long campaign never fails with "names exhausted".

**Independent Test**: the local PC's opening writes name knowledge for those people (an outsider's writes
none); `evals/longhorizon.py --mode scripted` runs past 300 lines.

### Edge Cases

- An incident with no person behind it (alarm, theft, omen): the subject is a thing; the case still validates.
- No cast NPC fits the subject's role: a walk-on subject is generated (12.11.1).
- A region without a ring-1 site or a gate: the reference's fallbacks (the haven) apply.
- Pre-made or older saves without packs: nothing is required of them (DL-12-61 migration: packed on load is
  not built here; see Assumptions).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: After the 13 seed steps the world record is packed (12.16.9, 12.16.11, 12.16.16) on streams keyed
  by the seed and each entity's id, so no other seed draw moves; the engine's packed record equals the
  reference's `seed_packs(build_seed(seed), seed)`.
- **FR-002**: The seed check runs the 7 `#pack_requirements` checks after the 64 existing ones; a failing pack
  check re-runs from step 13.
- **FR-003**: The packed record reaches the store: place look/furniture/exits in place data; NPC knowledge packs
  (withheld from the narrator) and stances in NPC data; documents as things with a `text` fact at their place;
  case walk-ons as NPCs; case records in meta.
- **FR-004**: The narrator's scene setting shows the present place's look, furniture and exits, and nothing of
  other places' packs.
- **FR-005**: `cast(state, role, *, scope)` implements the 00.11.1 `cast` domain (`social.yaml#cast`): pool gate
  (reusing the incident people filter), fill weighted by fit, deterministic per question; empty pool -> None for
  the caller's 12.11.1 / "no one you know".
- **FR-006**: `engine/gen/case.py` builds the reduced case (PR-15-6 reduced profile) at seed time for the
  incident and on demand for a story-role question; it validates per 15.9.4 (reduced numbers); it exposes the
  consequential pointer (core holder first, R2-D).
- **FR-007**: `h.15.placement_audit` is live in Milestone 1 and audits reduced cases.
- **FR-008**: I-149: a local PC's opening writes name knowledge of the haven officers and haven-seated faction
  heads; an outsider gets none.
- **FR-009**: Retire `incident.bind_incident`, `SUBJECTS` and the opening's binding call; `incident_line` renders
  the case as the PC knows it. `settle_who` and the Talk regexes stay (part B), but answer story roles from the
  case and other roles by casting.
- **FR-010**: Person names never run out: when a people's table is exhausted, fresh given names are composed
  from that people's syllables.

### Key Entities

- **Seed pack**: look, furniture, exits (place); knowledge[] {fact, slot, topic, text, how, tier}, stance (NPC).
- **Document**: {id, option, at, text}; a thing with a `text` fact in the store.
- **Reduced case**: {id, profile, trigger, option, opening_place, solution (sealed), nodes[2] {fact, placements[3],
  reserve[1]}, fallbacks, audit}; in meta `world.cases`.

## Success Criteria *(mandatory)*

- **SC-001**: Same seed -> identical packs and case (determinism test); engine = reference on the parity seeds.
- **SC-002**: 30 of 30 seeded openings: the incident case validates and its core placement is at the opening
  place, held by someone there.
- **SC-003**: The scripted long-horizon run exceeds 300 lines with no name exhaustion.
- **SC-004**: The full test suite passes; ruff and pyright are clean on touched files.
- **SC-005**: The per-turn packet size change is measured and reported; only the present place and NPCs render.

## Assumptions

- Packs are applied in `WorldSeed.record()`, so every engine world (game, `build_rolled`) is packed; the parity
  test compares against the reference's packed record.
- Case records are not rendered to any role (meta is never rendered); "sealed" is honoured by not rendering.
- Until part B, `settle_who` answers a story role covered by a case with the case's subject (as the retired
  binding did); the per-holder delivery and pointer belong to the ladder. The pointer helper is exposed now.
- On-demand option mapping: missing/taken -> missing, challenger -> duel, message/messenger -> dying_messenger,
  refugee -> refugees, offer -> offer; other story roles go to casting.
- Casting and on-demand cases use keyed `random.Random` streams (seed + question), as the seed does, not the
  logged game RNG: they are pure functions of the seed and the question, so replay is exact.
- The knowledge pack stays in NPC data (sealed from the narrator), not as store facts: part B's rung 2 reads it.
- Pre-R2-D saves are not re-packed on load (no such saves are supported in M1).
- Minimal call-site edits outside the lane: `session.opening` (the binding call), `packet.scene_setting` (render
  the present place's pack), `places.NPC_SEALED` (+knowledge), the handler milestone table; each reported.

---

# Part B: the answer ladder (PR-12-10, 12.10.8)

Owner rulings D1 (tiered authority) and D2 ("I don't know" plus a real lead is a success). Rules: PR-12-10,
12.10.8, 12.10.6 (d)(e), 00.12.7 (proposal form), T-15-5 questions, T-01-6, 15.9.5, DL-12-44, DL-12-60..64,
DL-15-38..39. Reference: `rules/_process/simulation/12-answer_ladder_sim.py`.

## User Story 5 - A question to an NPC is answered before the draft (Priority: P1)

A resolved Talk, Observe or Recall that carries a question (the Reader's `question_kind` and `topic`), or a plain
SPEECH question to a present NPC, is answered by code at RECORD: the asked-and-answered index, then the tier
route (consequential -> the case graph; "who is <role>" -> casting; "what do you want" -> the record), then for
ordinary knowledge the store, the NPC's knowledge pack, one typed candidate proposed and settled by the Oracle at
12.10.6(d)'s odds, and last a pointer to a real person or place. The answer is a record line with a handle.

**Acceptance**: each rung answers when the rungs above it are empty; asking the same NPC the same question twice
gives the same fact id (or the same "does not know" and pointer); a Limited reach never proposes; a Great reach
adds one volunteered extra; a success is never empty.

## User Story 6 - Story-role questions reach the case (Priority: P1)

"Who is missing?" goes only to the case graph: a holder of a placement on the node delivers it (and the node is
marked found); anyone else says they do not know and names the holder of the node's core placement. With no case
behind the question, the reduced case is built now. A search at a place holding a placement delivers it too, so
node 2 can complete.

**Acceptance**: in 30 of 30 seeded openings, "who is missing?" is answered within 3 turns (offline).

### Functional Requirements (part B)

- **FR-011**: `engine/dm/answer.py` implements PR-12-10 steps 1-7; the index is meta `answers.index`
  `(npc|kind|topic) -> {fact, line, pointer}`; "does not know" is the Oracle's `knows_*` = false fact plus the
  pointer.
- **FR-012**: Rung 3 is a dedicated small model call (Role `proposer`: `{kind, subject, predicate, value}`), made
  only when rungs 1-2 are empty and the reach allows it; code rejects a non-ordinary candidate or one touching a
  sealed fact or a case node; the Oracle settles it at odds fixed before the roll (`social.yaml#common_knowledge`).
  The offline model implements it deterministically.
- **FR-013**: Depth by reach (`social.yaml#delivery.information.ladder_depth`); of N questions `deliver_count(N,
  reach)` are answered (T-01-6); a certain beat or SPEECH runs at Standard.
- **FR-014**: The pointer comes from casting (`pointer_target`): a person, else the topic's place, else a walk-on
  generated there; never the first present person.
- **FR-015**: Retire `world_step._talk_answers`, `_who_questions`, `_WHAT_ASKED`, `_NAME_OF`, `_WHO_ASKED`,
  `_ASKS_NAME`, `learn_names`, the "name one concrete thing" notes, the top-thread and first-present fallbacks, the
  "responds as the talk went" placeholder and `incident.settle_who`; `claims._learning_success` becomes
  unreachable (`TODO(008-B retire)`, spec 009-B's file).
- **FR-016**: `mark_found` when a placement is delivered (Talk to a holder, a search at a holder place, object or
  document).

### Success Criteria (part B)

- **SC-006**: Unit tests per rung, depth by reach, never-empty, ask-twice, "does not know" recorded,
  consequential routing, offline determinism.
- **SC-007**: Long-horizon scripted (offline): 0 engine errors; empty-success rate 0; ask-twice consistency 100%.
- **SC-008**: 30 of 30 seeded openings answer "who is missing?" within 3 turns (offline).

### Assumptions (part B)

- The Reader's topic may be null (the offline Reader never sets it): the topic is then inferred from the
  question's words against the closed topic list's keys and gists, else `local_news`.
- A Talk with no question part is a request (T-15-5 "yes, as asked"), not a learning beat.
- Observe and Recall keep the store ranking as rung 1; their pack rung is the place's furniture; no Oracle rung
  (PR-12-10 is about an NPC's knowledge).
- `proposed_by: narrator` has no column on facts; the rule id `PR-12-10` and `source: oracle` mark ratified facts.
