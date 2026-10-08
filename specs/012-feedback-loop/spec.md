# Feature Specification: The player feedback loop (spec 012)

**Feature Branch**: worktree branch (spec dir `012-feedback-loop`)

**Created**: 2026-10-08

**Status**: Implemented (see [implementation-results.md](implementation-results.md))

**Input**: Owner direction (2026-10-09): "make our system much less strict, allow some of these errors to potentially
pass through, and instead make sure we have a robust system for the player to provide feedback, say something was
applied incorrectly, remembered incorrectly, etc., and have it go back and check." Spec 011 loosens the claim check
in parallel; this loop is the safety net for what now gets through.

Scope: `rules/_process/reports/R2-G-report.md`, "engine checklist → Spec 012", items 1-9. Rules implemented (look
up with `rules/tools/rq.py`; not restated): PR-12-11, 12.3.6, 12.3.4, PR-12-4, 12.5.8, 12.5.10, 12.15.9, 12.15.11,
14.2.5, 14.2.7, INV-9, DL-12-84, DL-12-85, DL-12-86; data `pacing.yaml#feedback`, `#corrections`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Report an error in one obvious way (Priority: P1)

The player types `/fix <what is wrong>`, or just says so ("that's wrong", "she already told me her name"). The
hint `Something wrong? Type /fix and say what.` is shown when play starts or resumes, in the glossary (`?`), and
after a fiction message that may also be a dispute (checklist item 1).

**Acceptance Scenarios**:

1. **Given** a game resumed in the play client, **Then** the hint is printed once after the first play screen.
2. **Given** `?`, **Then** the glossary ends with the hint. **Given** `/fix the guard was dead`, **Then** the
   dispute is checked with no Reader call.
3. **Given** a fiction message like "wait, you said the gate was open", classified as fiction, **Then** the
   response ends with the hint.

### User Story 2 - The game checks the record, not its memory (Priority: P1)

The report is located against the whole transcript (every turn; checklist item 2): code pins turn ids, quotes,
names, numbers and frame ids; when nothing pins it, one locator call returns `{turn, quote, category}`. Evidence
(item 3) is the passage, every other turn naming the subject, the stored value with its provenance (source event,
source kind, turn), the frame with its cited facts and a code recomputation (item 4), and any claim-log entries.
The outcome follows PR-12-11's table (item 5) and is delivered as `[CORRECTION]` or `[FIX]` (item 7).

**Acceptance Scenarios** (each against a real offline game with a planted error):

1. **Remembered wrong**: a resolved write established a value and a later unsourced write replaced it → record
   error: a pinned corrective write (`source: correction`, `supersedes`, `pinned`); 20 turns later the value is
   unchanged and still in the subject's profile in the narrator view.
2. **Rule applied wrong**: the recomputed frame differs → ruling error; the player takes the beat back and redoes
   it (the redo frame matches the recomputation).
3. **Contradiction outside the scene**: the answer quotes an earlier turn of an earlier scene found by the
   whole-transcript search, and states the store's value.
4. **Action misread**: a beat resolved with no OFFER shown, on a reading the player's words do not support → the
   beat is taken back (writes reverted, roll void) and the player declares again.
5. **Player mistaken**: the answer quotes the turn the record went by; nothing is written.
6. **Incidental fiction, evidence uncertain**: no stored value for a detail slot → the player's reading wins as a
   pinned correction.
7. **Mechanics the player cannot back up**: nothing on record → the store stands (INV-9), the answer says what the
   record holds, the report is logged for review, nothing is written.
8. **Take-back blocked**: an irreversible event (a session boundary, death or Dying, unsealing, a completed clock)
   between the beat and the report → no rewind; corrected going forward.

### User Story 3 - The owner can read every dispute (Priority: P2)

Each report writes a dispute record `{id, time, turn, words, category, passage, evidence, outcome, writes,
reverted}` to the corrections ledger and a markdown block to `saves/<campaign>.disputes.md` beside the save
(item 8). Disputes per 100 narrated turns (all, upheld, by category) is reported by `evals/longhorizon.py` (item 9).

### Edge Cases

- A report naming nothing on record and no turn: the answer asks which statement, quoting the latest exchange;
  still logged.
- Background or sealed subjects: never revealed (`[UNKNOWN]`), the objection logged.
- A take-back past the scene start reverts the scene change too (the PC is back in the beat's scene); more than
  10 turns back or a blocker → forward correction.
- A reliance CHOICE left open is logged with the outcome pending; the answer updates the record.

## Requirements *(mandatory)*

- **FR-001** `/fix` is a DISPUTE by code; natural disputes are classified by the Reader; a possible dispute in
  fiction appends the hint (item 1).
- **FR-002** Locate searches every turn; pins by turn id, quote, name, number, frame id; else one locator call
  (item 2). Categories: remembered_wrong, rule_wrong, contradiction, misread, other.
- **FR-003** Evidence: provenance of every fact touched; frame, cited facts, rule ids and inputs; claim log (item 3).
- **FR-004** Rule disputes recompute DC, modifier and odds from rules data and the state at the frame's commit;
  a difference or an omitted established fact is a ruling error with reliance (item 4).
- **FR-005** Outcomes by PR-12-11; a correction is a pinned `fact_set` (`source: correction`); the player's reading
  wins only for T0/T1a detail slots with uncertain evidence (item 5, INV-9).
- **FR-006** Take-back past the scene start when code-confirmed, unblocked, within 10 turns; a misread beat with
  no OFFER shown can be taken back whenever reported, within that limit (item 6; 12.5.8 item 2).
- **FR-007** Labels `[CORRECTION]` and `[FIX]` (no `NOTE` in dispute answers) (item 7).
- **FR-008** Review log: ledger record and `saves/<campaign>.disputes.md` block (item 8).
- **FR-009** Pinned facts are always in their subject's profile in the role views (`view_for`), never archived.
- **FR-010** Harness: dispute rate per 100 narrated turns in `evals/longhorizon.py`; one persona line in
  `evals/playtest.py` (item 9).

## Success Criteria *(mandatory)*

- **SC-001** Full suite passes; ruff and pyright clean on touched files.
- **SC-002** One scenario test per outcome listed in User Story 2, each on a real offline game.
- **SC-003** Discoverability: hint at session start and in the glossary; `/fix` works in the client.
- **SC-004** Every dispute in the scenario tests leaves a readable review-log block.
- **SC-005** Live check (≤ 10 turns, Haiku through the Claude CLI): planted disputes answered; outcomes reported.

## Assumptions

- The locator call also restates the player's claim (`subject`, `key`, `value`): reading the report, not judging
  it. Code parses those first; the call fills only what code could not.
- "Incidental" (T0/T1a) = the lasting detail slots other than `condition_visible`; every other key (quantities,
  possessions, conditions, positions, clues, sealed facts, rulings, ordinary predicates) keeps INV-9.
- The review log's wall-clock time is outside the event log (replay determinism); the ledger record carries the
  game time and turn id.
- Spec 011 owns the claim log; this loop reads meta `claim_log` entries for the passage's turns when present.
