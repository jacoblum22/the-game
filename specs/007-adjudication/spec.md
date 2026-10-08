# Feature Specification: Adjudication (computed gate and necessity, difficulty rubric, plain OFFER)

**Feature Branch**: `007-adjudication` (worktree branch)

**Created**: 2026-10-08

**Status**: Draft

**Input**: "007-adjudication: computed gate and necessity, difficulty rubric (obstacle class + bounded nudge, snag cap,
critical-failure guard, cost follows stakes source), Safe auto-commit, plain-language OFFER templates with
engine-computed alternatives and one menu convention." Implements the R2-C rules
(`rules/_process/reports/R2-C-report.md`) from lane D P1–P5
(`research_notes/Playtest round 2 solutions/D_adjudication_difficulty.md`; synthesis §2 steps 1–6, §4 D3/D6/D7,
§5 Phase 2, §7). Rule ids are cited, not restated: look them up with `py -3.12 rules/tools/rq.py <id>`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The game never refuses what the sheet says I can do (Priority: P1)

A player types an ordinary act ("I threaten the innkeeper", "I gently turn the child's face toward me"). The
game classifies only what the act is (verb, target, three yes/no facets, question kind, shape). Whether it is a
basic act, a licensed one, beyond the character, or impossible is computed from the sheet and the rules data, so
a sheet knack never becomes a redirect and a gentle act is never framed as force.

**Why this priority**: wrong gates (P-004, P-031, P-122, P-123) cost whole turns and were the top playtest
complaint of theme D. Rules: 00.12.3 `[D]`, 12.2.2 decision 3, PR-01-5 step 1, DL-01-30, DL-12-50.

**Independent Test**: the Reader golden set (`evals/reader_golden.py`) scored with the new Reader and the
computed gate; a table test over every verb × facet × licence.

**Acceptance Scenarios**:

1. **Given** a PC with no licences, **When** the player threatens someone in words, **Then** the beat is a basic
   Talk (G1), never a redirect.
2. **Given** a PC holding a persuasion licence, **When** the player talks someone round, **Then** the beat is
   licensed (G2) citing that licence.
3. **Given** a PC with no relevant licence, **When** the player picks a lock or uses "witch-sight", **Then** the
   beat is redirected (G3) naming the licence code looked up.
4. **Given** "I don't grab it, I ask for it", **When** read, **Then** the facets say no force and the beat is Talk.

---

### User Story 2 - No roll when nothing is at stake, honest odds when something is (Priority: P1)

Opening an unbarred wicket, reading a notice the character can read, or asking a Neutral stranger a plain
question resolves without a roll and without a Framer call. When a beat does roll, its difficulty comes from the
verb's obstacle class (the rubric), moved at most one rung by a cited lasting fact; one situational hindrance
costs −2 and any further one raises the stakes instead; a frame whose critical-failure chance would exceed its
success chance is fixed by code or shown as a *long shot* with a better way first. A cost always follows the
source of the stakes (a question never threatens a sword blow).

**Why this priority**: theme E (harsh flat odds; I-158, I-143, I-155, P-024, P-107, P-117). Rules: 00.3.8,
00.3.9(b), T-00-5, 01.4.1, 01.6.4, 01.6.5, 01.6.8, 01.6.9, 01.6.11, 01.6.13; DL-01-29, DL-01-31.

**Independent Test**: unit tests over `necessity()` and `frame_check`; the odds audit over the golden set's rolled
beats.

**Acceptance Scenarios**:

1. **Given** a Talk question to a Neutral NPC, **When** resolved, **Then** it is certain: no Framer call, no roll.
2. **Given** a rolled Move through a crowd with two hindering facts cited as snags, **When** framed, **Then** one
   applies as −2 and the other as stakes +1.
3. **Given** a non-Dire, unopposed, non-secret frame with critical failure above success, **When** checked,
   **Then** the Precision snag converts to Protective, and if still above, the OFFER is labelled long shot with
   the best computed alternative first.
4. **Given** stakes source "goodwill", **When** the Framer threatens harm, **Then** the frame is refused.
5. **Given** a nudge citing the same fact as a Precision snag, **When** checked, **Then** the frame is refused.

---

### User Story 3 - An OFFER I can read, and a menu that always works the same way (Priority: P2)

The OFFER is a fixed template in plain words: the chance as a number and a word, what success and failure bring
with severity words, the trades in one line each, up to three engine-computed "Another way" options with their
chances. No rule id, DC, severity code, verb id, anchor or mode name appears. Every pause prints `[Enter] <label>`
for its default, letters for the alternatives, and `?` explains a glossary word. Safe, likely frames roll at once
(auto-commit, on by default) and are shown as `[OFFER — auto]` above their RESULT.

**Why this priority**: theme F (P-005, P-028, P-044, P-092, I-134, I-138). Rules: 01.7.1, 01.7.4, 12.15.2,
14.2.7; DL-01-32, DL-12-51.

**Independent Test**: snapshot tests of ~20 rendered OFFER blocks and a forbidden-token test; CLI tests of the
menu convention.

**Acceptance Scenarios**:

1. **Given** any rendered OFFER, **Then** it contains none of `S\d`, `DC`, `verb.`, `anchor`, `Mode:`.
2. **Given** a Risky OFFER, **When** the player presses Enter, **Then** it commits ("[Enter] Do it" was printed).
3. **Given** a Dire, lethal or long-shot OFFER, **When** the player presses Enter, **Then** the block is shown
   again and committing takes `d`.
4. **Given** a Safe frame at ≥ 50% with auto-commit on, **When** framed, **Then** it rolls at once; a Risky
   frame never does.
5. **Given** "change approach", **Then** the game asks how (kept from 172b2b2).

### Edge Cases

- No obstacle class fits: class `other`, a model-picked tier with the guardrails (lower rung for everyday acts).
- A nudge would cross the trivial line: refused (a rolled class never nudges to trivial).
- No alternative approach is computable: the "Another way" line is omitted (long shot still labelled).
- A secret frame: odds hidden, "you can't judge how hard this is", no close-call line, never auto-committed.
- A "what do I know?" message: answered by code before any Reader call.
- A conditional or queued beat ("I attack if they keep stalling"): not resolved now; restated as queued.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001** (12.2.2, DL-12-50): the Reader records per beat only verb, target, `against_will`, `uses_power`,
  `speech`, shape (now / queued / conditional), a cited `g4_fact`; per part `question_kind` (6 + none) and `topic`. It no longer
  proposes gate, licence, would-be licence or necessity.
- **FR-002** (00.12.3, PR-01-5): the gate class is a pure function of verb, facets, held licences, the verbs'
  `excludes`, active conditions and a cited G4 fact; a knack is never a gate; the would-be licence is looked up
  by code.
- **FR-003** (14.6.3): "what do I know?" is routed by code before the Reader call.
- **FR-004** (01.4.1, 15.3.10): a necessity function decides no-roll classes from state: certain social beats,
  reading words on record; and a trivial class base after framing. COSTLY's "aware party" is computed: only a
  party who would act on a failure makes the observer stakes source available. Trivial or certain beats found before framing skip the Framer call.
- **FR-005** (00.3.8, 01.6.5): rolled unopposed beats take the obstacle class base from
  `basic_verbs.yaml#anchor.obstacle_classes` plus at most one nudge citing a fact with a stated why; class
  `other` takes a model tier; the nudge never crosses the trivial line.
- **FR-006** (01.6.4): social and opposed beats always use the 15.3.3 / opposed defense, never a tier.
- **FR-007** (00.3.9(b), 01.6.8): at most one cited Precision snag; a further hindering fact applies as Protective.
- **FR-008** (01.6.13): the critical-failure guard as written, labelling *long shot* with the best computed
  alternative.
- **FR-009** (01.6.11, DL-01-31): threatened and alternate costs are narrowed by `resolution.yaml#stakes_cost_menus`
  (harm from an observer only when they are armed and hostile, cited).
- **FR-010** (01.7.4, DL-01-32): auto-commit defaults on and applies only to Safe, non-lethal, non-secret,
  non-long-shot frames with no mode price and success ≥ 50%.
- **FR-011** (12.15.2, 14.2.7, DL-12-51): the OFFER renders from typed frame fields by template, chances as
  number + word; "Another way" lists up to three engine-computed approaches with zero model calls.
- **FR-012** (12.15.2): every pause uses one menu convention: `[Enter] <label>` always printed, letters for
  alternatives, `?` explains glossary words; Enter never withdraws.
- **FR-013**: retire `plain_offer_words`, `_fix_pronouns`, `_fact_words`, `_difficulty_phrase`, TRADE_LABELS,
  the "G1 before G3" override, `_plain_form_of`, `reader_check`'s G2 rule, `_plain_reading`, the Reader prompt's
  gate / would-be-licence / gentle-touch lines, the Framer's tier and snag tie-break lines, the Moderate default
  and costs.py's "observer is a judgement call" ponytail.

### Key Entities

- **Reader beat**: verb, target, facets, shape. **Reader part**: text, class, question kind, topic.
- **Gate decision**: class, verb, licence, mode, reason, redirect (unchanged shape, now computed).
- **Necessity**: roll or a no-roll reason (trivial, take_the_time, certain …).
- **Framer proposal**: obstacle class (or `other` + tier), nudge why / value / fact, levers, snags, stakes source,
  costs.
- **Frame**: adds class, nudge, long-shot flag and computed alternatives.

## Success Criteria *(mandatory)*

- **SC-001**: Reader golden set: verb ≥ 95%, computed gate ≥ 98% (baseline 72% / 64%), measured on Claude Haiku;
  negation pairs reported separately.
- **SC-002**: odds audit over the golden set's rolled beats: zero non-Dire unopposed OFFERs with critical failure
  above success unless labelled long shot; share of beats with ≥ 3 distinct alternative odds reported.
- **SC-003**: no rendered OFFER contains `S\d`, `DC`, `verb.`, `anchor` or `Mode:`.
- **SC-004**: the full test suite passes; prompt word budgets do not grow.

## Assumptions

- Clarify was skipped (overnight, owner asleep). D6 (numbers + words) and D7 (Safe auto-commit on) are taken as
  the R2-C rules assume them (owner to confirm).
- Request size for a rolled social beat: the Framer picks R1–R5 (15.3.2 is `[J]`); a plain question with
  `question_kind` set is R1 for the certainty test.
- "Would act on a failure" is computed from state: an adversary or Hostile/Unfriendly NPC present, the beat's
  target when `against_will`, or a fight in progress. Spec 006's NPC layer may refine stance later.
- "Trivial before framing" covers what code can see without the Framer (certain social, reading on record,
  nothing pressing); a trivial class chosen by the Framer still resolves without a roll, after its call.
- The open sim finding (wrong nudge + wrong snag = 35 points) is bounded within the rules only by refusing a
  nudge and a Precision snag that cite the same fact; a stricter bound needs a rule change, logged as a ledger
  row, not made here.
- 15.3.10's hesitation test is `[J]`: code treats a talk as certain only when the NPC has no recorded refusal;
  any recorded refusal leaves the beat to the Framer (roll), so code never makes the lenient judgment.
- The answer ladder that consumes `question_kind` / `topic` is spec 008.
