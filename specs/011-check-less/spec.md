# Feature Specification: Check less (spec 011)

**Feature Branch**: worktree branch (spec dir `011-check-less`)

**Created**: 2026-10-09

**Status**: Implemented (see [implementation-results.md](implementation-results.md))

**Input**: Owner direction 2026-10-09 (DL-12-80): the truth gate is too strict. False positives (the checker
matching "the sword" to the wrong one of two swords) cost more than occasional model slips. Block only critical
narrator-voice errors, treat dialogue as testimony, and let the player's report (spec 012, in parallel) catch the
rest. Scope: `rules/_process/reports/R2-G-report.md`, "engine checklist → Spec 011", items 1–12, exactly.

Rules implemented (look up with `rules/tools/rq.py`; not restated here): 12.3.1, 12.3.1a, 12.3.1b, 12.3.2,
12.3.3, 12.14.13, 12.11.9, 12.2.9, 00.6.6a, 01.6.8, 01.6.10, 01.3.7; DL-12-70, DL-12-80..83, DL-12-87, DL-01-29,
DL-01-33; data `pacing.yaml#claim_check`, `#details`, `social.yaml#event_tags`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Only critical narrator-voice errors stop a sentence (Priority: P1) — checklist 3, 5, 6, 7, 8

The player reads the narrator's prose as drafted unless it states, in the narrator's own voice and about a
certain subject, something on the blocking list (outcome or capability, harm, conditions, quantities, a
mechanically relevant possession, coarse position, presence or life, sealed content or an unknown name, PC
agency) that the record contradicts. Everything else is delivered and logged.

**Acceptance Scenarios**:

1. **Given** two swords in scope (red, green), **When** a sentence says "the sword is green", **Then** no verdict
   is given in either direction, whichever sword the claim names; the claim is logged.
2. **Given** a claim in a blocking class with a certain subject that the store contradicts, **Then** it blocks
   (redraft or cut); **given** an attitude or descriptive-detail clash, **Then** it is logged only.
3. **Given** a narrator-voice sentence declaring a new clue, hazard or adversary no cited line delivers, **Then**
   it is cut; an uncertain element kind is T1a (written, never cut).
4. **Given** a lasting detail on a known person that clashes with the store, **Then** the store keeps its value,
   the clash is logged, and the sentence is delivered (a held weapon or a coarse position still redrafts).
5. **Given** an undeclared or atmosphere sentence, **Then** it is redrafted or cut only on a code-scan hit
   (numeral, unknown name, outcome word, sealed string); otherwise delivered and logged.

### User Story 2 - What characters say is testimony (Priority: P1) — checklist 2

Each sentence declares its `speaker` (a present person, never the PC). Quoted words with a speaker are speech:
recorded as a `said` record `{speaker, turn, words, about}`, never a world fact, never truth-checked. Code checks
only that the speaker is present and not the PC, and that no quoted words put in the PC's mouth go beyond the
player's message. A stored name heard in speech becomes known to the PC (`how: heard`).

**Acceptance Scenarios**:

1. **Given** an NPC who says an unknown name and a number in quotes, **Then** nothing is cut and a `said` record
   is kept, with no fact written.
2. **Given** a sentence that quotes the PC saying words the player never wrote, **Then** it is caught
   (`pc_agency`).

### User Story 3 - The audit measures, it does not gate (Priority: P1) — checklist 1, 12

The Checker runs on 1 turn in `full_extraction_every` (by turn id), after delivery; its findings go to the claim
log only. Live runs report claim-log entries per 100 turns by class and sampled blocking-list misses per 100.

### User Story 4 - Resolution fixes I-159, I-160(a) (Priority: P2) — checklist 9, 10

A cited Precision snag on a nudged or class `other` beat applies as Protective. Two unoffset reach factors (or a
total potency) route the beat to G4 before the OFFER, nothing spent.

### User Story 5 - NPC responses come from tags (Priority: P2) — checklist 11

Code tags each event from the beat (verb, facets, target, topic, terms, pressure mark, the Framer's `asks`) and
matches refusals and wants through `social.yaml#event_tags`: a refusal is spoken; a want served takes row 9 (a
request) or 8, defeated row 2 (1 at Hostile), engaged row 6, then the practice clamp. The World call is only the
fallback. A crowd's response is a scene fact `crowd_response` on the place, with a record line.

### Edge Cases

- A sentence with both speech and narration: only the quoted part is testimony; the rest is narrator voice.
- Quoted words with no declared speaker and a "you say" attribution: PC words, checked against the message.
- No present person: `speaker` offers only `none`.

## Requirements *(mandatory)*

- **FR-001** (item 1): `details.max_active` and its reader are removed; the view orders lasting details by
  salience then last use within the profile budget; a correction counts as cited. `claim_check.audit.skip_enabled`
  is removed; `audit_mode` is `sampled` (crc32 of the turn id), after delivery, findings to the claim log.
- **FR-002** (item 2): narrator schema `speaker`; speech split by quoted spans; speech checks by code; `said`
  records; heard names learned.
- **FR-003** (items 3, 4): blocking list × narrator voice × certain subject; everything else logged
  `{turn, sentence, class, verdict, store_value}`; no verdict without a certain subject.
- **FR-004** (item 5): code scans every turn decide undeclared/atmosphere sentences.
- **FR-005** (item 6): T2 cut only for narrator-voice declared clue/hazard/adversary or non-ordinary
  person/item/document undelivered; uncertain kind T1a; audit-typed T2 never cuts.
- **FR-006** (items 7, 8): incidental clashes and unsourced incidental acts logged; blocking slots redraft.
- **FR-007** (item 9), **FR-008** (item 10), **FR-009** (item 11) as in stories 4–5.
- **FR-010** (item 12): `evals/longhorizon.py` reports the new metrics.

### Key Entities

- **Claim-log record** `{turn, sentence, class, verdict, store_value}` (kept on the turn record); a sampled audit
  entry also marks `blocking_miss` (a blocking-list failure that was delivered), for OEQ-12-23.
- **Said record** `{speaker, turn, words, about}` (kept on the turn record; never a fact).

## Success Criteria *(mandatory)*

- **SC-001** Full suite passes, with tests for every acceptance scenario above, the I-159 refusal, the I-160(a)
  route, I-176 tag matching and the crowd response; ruff and pyright clean on touched files.
- **SC-002** Scripted offline long-horizon run: 0 engine errors.
- **SC-003** Live (Haiku, ≤ 25 narrated turns), against spec 010's 42.1% / 26.3% / 1.37: first draft as drafted
  > 50%, cut turns < 15%, narrator calls per turn ≤ 1.2; claim-log entries per 100 turns by class; sampled
  blocking-list misses per 100 turns. Real numbers reported, met or not.

## Assumptions

- The scene-end sweep (12.4.8 step 4) has no engine code yet; item 8's sweep clause has nothing to change.
- The claim log and said records live on the saved turn record (spec 012 reads them as evidence).
- Item 11's World fallback reads the checklist literally: no tag matches and the NPC holds motives pointing to
  opposite rows (a want and a refusal).
