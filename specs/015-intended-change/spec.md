# Feature Specification: Typed intended change (spec 015; S4)

**Feature Branch**: worktree branch (spec dir `015-intended-change`)

**Created**: 2026-10-08

**Status**: Implemented (see [implementation-results.md](implementation-results.md))

**Input**: Owner ruling 2026-10-09 ("S4 seems fine for now, although I think we could modify it later if this fix
doesn't work"). Scope: `rules/_process/reports/R2-H-report.md`, "Engine checklist → Spec 015" items 1-6, plus spec 016
item 3 (attribute rubric, moved here because it reads the `take` change) and the knockout status line (problem 13).
Rules implemented (look up with `rules/tools/rq.py`; not restated): 01.2.7 (with its Laya design note), 01.2.1,
01.2.2, 01.2.6, PR-01-1 steps 1 and 11, PR-01-3 step 5, T-12-18, 12.14.12, DL-01-34, DL-01-35; data
`resolution.yaml#intended_change`, `#attribute_rubric.lift_or_carry`.

Evidence: `evals/playtests/20261008-145430-claude-fighter.md` (save `playtest-20261008-145430-fighter.db`):
"lift his coin purse" succeeded 18 vs 10 and nothing moved the purse; the Grapple it was read as wrote "restrained"
instead (inputs 20-23); "grab the purse and punch her" showed only the grab in the OFFER (28); "Might +0" for a quick,
quiet lift when Agility gave 75% (24); a Staggered PC at load 0/3 went Down from one blow (31); the purse taken on a
critical success never reached the sheet (30-31).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A success changes what the player meant to change (Priority: P1)

The player says what they want to be different ("take the purse"). The Reader types it as one kind from the closed
list with slots from the scene (`take`: item, from). On success the engine writes the change at the delivered reach;
on failure nothing; on a success at a cost both, the cost never undoing it.

**Acceptance Scenarios**:

1. **Given** the save's market scene with Murzak carrying the coin purse, **When** a `take` (purse, from Murzak)
   succeeds at Standard reach, **Then** the purse's holder is the PC and the sheet lists it.
2. **Given** the same beat at Limited reach, **Then** the purse is contested (a hand on it) and still Murzak's.
3. **Given** the same beat failing, **Then** nothing changes.
4. **Given** each kind (take, give, move_to, open, close, learn, persuade_to, restrain, free, harm, hide), **Then**
   its success writes what 01.2.7's table names, scaled by reach (restrain: grip at 1-2, restrained at 3, pinned at 4).
5. **Given** a `take` whose item is not on the named person (or not in the record), **Then** nothing is written and
   the RESULT says why ("the coin purse is not on Feney").

### User Story 2 - The player sees the change before committing (Priority: P1)

The OFFER shows the typed change in plain words ("Taking: the coin purse, from Murzak Red-Hand") and, for a message
of several beats, the beats that follow ("Then: punch Murzak"), so a wrong kind or a dropped part is fixed for free.

**Acceptance Scenarios**:

1. **Given** "grab the purse and punch her", **When** the Reader returns `take` and `harm`, **Then** they are two
   beats, the first OFFER names the second, and both resolve in order.

### User Story 3 - The narration cites the change (Priority: P1)

The applied change (or why it was not applied) is a must-name record line; the narration that omits it fails
coverage, and a narrated possession change no write backs fails the claim check.

### User Story 4 - Lifting uses the fitting attribute (Priority: P2)

For a `take` change or a lift/carry method, the method's words pick Might, Agility or Endurance (heave: Might; palm,
quick and quiet: Agility; carry far: Endurance); otherwise the frame uses the one with the best odds and the OFFER
lists the others with their odds.

**Acceptance Scenarios**:

1. **Given** a PC with Agility above Might and a `take` with no picking word, **Then** the frame's attribute is
   Agility and the OFFER lists Might and Endurance with their chances.
2. **Given** "I heave the chest", **Then** Might, whatever the odds.

### User Story 5 - The Staggered line matches what a blow does (Priority: P2)

The `[STATUS] STAGGERED` card says a blow adds 1 to 4 wound load by how hard it lands, and the foe's RESULT line
shows the load it added, so going Down from one heavy blow at 0/3 is explained.

### Edge Cases

- No change typed (`none`, an old save's beat): the beat's own rules write as before (T-12-18 by verb).
- A Grapple typed `take` writes no hold; a hold is the face of `restrain` (T-12-18 folds under the change).
- `move_to`, `harm` and `learn` keep their existing writers (PR-06-4 and 06.3.5, ch.06/07, 01.10); the change line
  cites what they wrote.
- `make` (crafting, ch.08) is not built: not applied, and the RESULT says so.
- More than one change in one beat cannot be typed: the schema has one change per beat (two changes are two beats).

## Requirements *(mandatory)*

- **FR-001** The Reader's beat carries `change {kind, what, whom}`: kind from the 13 data kinds; `what`/`whom` from
  the ids in the Reader's scope (scene, the PC's and present people's things) and reachable places, or none.
- **FR-002** Every typed change is logged with its inputs (restatement, verb, ids in scope, kind, slots) beside the
  save, one line per beat (01.2.7 design note).
- **FR-003** RECORD applies the change on success by kind and delivered reach; failure applies nothing; success at a
  cost applies it; an unapplicable change is not applied and the RESULT says why.
- **FR-004** The OFFER shows the change in plain words and names the beats queued after it.
- **FR-005** The applied (or refused) change is a must-name record item; the possession check reads the holder the
  change wrote.
- **FR-006** T-12-18's Grapple rows apply when the change is `restrain` (or untyped); `free` ends the hold.
- **FR-007** Lift/carry attribute rubric per DL-01-35, alternatives with odds in the OFFER.
- **FR-008** The Staggered card and the foe's RESULT say how much wound load a blow adds.

### Key Entities

- **Change**: kind, what, whom (ids); stored on the beat (and so on its frame).
- **Holder**: who holds an item: its current `holder` fact (the change's write) before its data keys.

## Success Criteria *(mandatory)*

- **SC-001** Full suite passes; ruff and pyright clean on touched files.
- **SC-002** Reader golden set: verb and gate within ~3 points of 92.3% / 97.8%; change-kind accuracy reported (labels
  set by 01.2.7 before model answers were read); held-out set reported.
- **SC-003** `evals/longhorizon.py --mode scripted`: 0 engine errors.
- **SC-004** One live fighter run (15 turns, Haiku): report whether takes, gives, moves and restrains land in the store.

## Assumptions

- Slot names are positional over the data's `slots` lists: `what` is the first slot, `whom` the second (`move_to`'s
  `who` defaults to the actor; `persuade_to`'s act is the beat's intent).
- Kinds without a partial form in 01.2.7 apply whole at reach 1.
- An item with no known holder may be taken from the person named.
- Code never splits a beat: the Reader returns one beat per change (the schema allows one change per beat, the prompt
  says two changes are two beats); the existing fold of a serving step (01.2.2, 00.12.6) is unchanged [analyze: U1].
