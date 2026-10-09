# Feature Specification: The feedback loop, understand first, then verify (spec 014)

**Feature Branch**: worktree branch (spec dir `014-feedback-understand`)

**Created**: 2026-10-08

**Status**: Implemented (see [implementation-results.md](implementation-results.md))

**Input**: ROUND3-ANALYSIS S3 and the owner's ruling (DL-12-94): "I'm surprised that it's not figuring out what the
player is talking about when they point out an error and it can directly read the whole transcript." On real reports
the spec-012 loop pinned a number or a name by code first ("vitality 18" for "I never got the purse", twice; "your
face is turned face"), and other reports got "As recorded … Say which fact or roll is wrong. Logged."

Scope: `rules/_process/reports/R2-H-report.md`, "Spec 014" items 1-5. Rules implemented (look up with
`rules/tools/rq.py`; not restated): PR-12-11, 12.3.6, 12.15.9, 12.2.2 (DISPUTE), DL-12-94, INV-9; data
`pacing.yaml#feedback` (`locate_call: retired`, `understand_call`, `answers`, `categories`).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The game understands a fuzzy report and says it back (Priority: P1)

The player reports an error in their own words, often several at once ("the season is wrong", "I succeeded but
never got the purse", "Nero answered for the officer"). One understanding call reads the report with the whole
transcript and returns what the player believes, what the transcript shows happened, the category (including
`ruling_question`), the turn and its words. Every answer opens with the complaint restated in plain words.

**Acceptance Scenarios**:

1. **Given** "I succeeded but never got the purse" after a successful roll that moved no purse, **Then** the answer
   starts "You're saying …" with the purse complaint, and quotes the roll's turn, never an unrelated number.
2. **Given** a report bundling two complaints, **Then** each gets its own restatement and answer.
3. **Given** a report about a turn many scenes back, **Then** the passage is found (the whole transcript is read).

### User Story 2 - Code verifies and every report gets a plain answer (Priority: P1)

After the understanding, code checks the record: the stored value and its provenance, the frame (recomputed) and
what it wrote, the claim log; then PR-12-11's first fitting row. Every answer ends corrected, explained, or not
found with a "did you mean"; never a bare "Logged."

**Acceptance Scenarios**:

1. **Ruling question**, the frame recomputes the same → explained in plain words: what was rolled, its result, its
   reach and what it changed in the record.
2. **Rule wrong**, the frame recomputes differently → ruling error with the reliance CHOICE (as spec 012).
3. **Store agrees with the player** (season, pronouns, a stored detail) → "You're right: …; the narration slipped."
4. **Incidental fiction**, uncertain or re-rolled → the player's reading wins as a pinned correction.
5. **Mechanics with no record** → what the record holds and why; logged for review; nothing written (INV-9).
6. **Nothing in the transcript fits** → "I can't find that; did you mean turn N, "…"?" with the nearest passage.
7. Spec 012's planted cases (remembered wrong, rule wrong with take-back, contradiction, misread take-back, player
   mistaken, incidental fiction, mechanics, take-back blocked) keep their outcomes.

### User Story 3 - The loop is measured on real complaints (Priority: P1)

The corpus is every `/fix` line of the 20261008 persona re-runs plus three short round-3 forms, each on its save cut
back to just before the report, with the expected understanding and outcome. Scored before (spec 012 code) and after.

### Edge Cases

- The understanding call fails or returns nothing usable: the answer is "not found" with the nearest passage.
- The transcript is longer than the budget: the scene cards (the current scene's turns) plus the turns that match
  the report's words, newest first, within the budget.
- A turn the call names that does not exist, or a quote the turn does not hold: dropped; code searches for the
  nearest passage instead.
- A complaint about an open OFFER (no committed frame yet): explained from the offer's levers and their facts.
- Background or sealed subjects: never revealed; the objection logged.

## Requirements *(mandatory)*

- **FR-001** Retire the code-first pinner (`_pins`, `_number`, `_named`, `_value_near`, `_slot`, `_claim_from` as
  the first step, `_candidates`, `_ask_locator`, the locator role); `default_identify` no longer pins.
- **FR-002** One understanding call per report: the report and the whole transcript (or, past
  `transcript_budget_tokens`, the scene's turns plus search hits); returns up to three complaints, each
  `{believes, happened, category, turn, quote}` plus what it is about (the subject and the player's value).
- **FR-003** Restate first, from `believes`, in every answer.
- **FR-004** Verify by code: store value and provenance, frame recompute and the frame's writes, open OFFER levers,
  calendar and pronouns on record, claim log; decide by PR-12-11's table with the new rows not found and
  ruling_question.
- **FR-005** Every answer ends corrected, explained, or not found; no bare "Logged."; no garbled values.
- **FR-006** The dispute record and the review-log block gain `believes`.
- **FR-007** Corpus fixture and harness; scores before and after committed.

## Success Criteria *(mandatory)*

- **SC-001** Full suite passes; ruff and pyright clean on touched files; spec 012's scenario tests kept or adapted
  with the same outcomes.
- **SC-002** Corpus: the share of reports understood (category and turn) and answered with the right outcome, before
  and after; after at least 9 in 10 understood (OEQ-12-26's target) on the live model.
- **SC-003** No corpus answer contains "Say which fact" or ends in a bare "Logged.".
- **SC-004** Live check (≤ 10 turns, Haiku through the Claude CLI): 3-4 corpus complaints re-planted; replies
  reported verbatim.

## Assumptions

- The understanding call may return up to three complaints (real reports bundle them); each is verified and logged as
  its own dispute record. At most one reliance CHOICE per report; later ones are answered forward.
- Besides the five returned fields the call names `subject` (a visible entity id), `about` (a closed list: fact,
  quantity, possession, name, pronoun, season_or_time, look_or_activity, who_said_what, roll_or_outcome,
  action_reading, other), `key` and `value`: reading the report, not judging it. Code maps `key` to a stored
  predicate or quantity; the model never decides what is written.
- Incidental (T0/T1a) adds `activity` to spec 012's lasting look slots; `who_said_what` and look/activity reports with
  nothing on record are incidental; possessions, quantities, rolls and harm keep INV-9.
- The understanding role replaces the locator role (`Role.UNDERSTAND`); its schema lives in a new module
  (`engine/dm/understand.py`); `schemas.py` (spec 013's lane) only maps the role to it.
- The typed intended change (01.2.7) is spec 015's; until then a ruling explanation names the frame's verb, intent,
  reach and the writes it made.
