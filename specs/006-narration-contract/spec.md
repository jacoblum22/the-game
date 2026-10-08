# Feature Specification: Narration contract and default NPC layer

**Feature Branch**: `worktree-agent-a8fed8017034eb06e` (spec dir `006-narration-contract`)
**Created**: 2026-10-08
**Status**: Draft
**Input**: Phase 2 of `research_notes/Playtest round 2 solutions/00_SYNTHESIS.md` (§1.1, §2 steps 7–11, §5, §7):
B P1, P3, P5 and C P1, P4. Rules already written by R2-B (`rules/_process/reports/R2-B-report.md`): 12.3.1,
12.3.1a, 12.3.2, 12.3.3, 12.2.10, 12.14.12, 12.14.13, 12.11.9, PR-12-2, PR-00-7, DL-12-40..43. This spec cites
them rather than restating them.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The narration a player reads is what the narrator wrote, and it is true (Priority: P1)

A player acts; the engine resolves it; the narrator writes the turn as a list of sentences, each declaring what
it cites (record handles, view facts), whom it is about, what it introduces (typed by kind) or that it is
atmosphere. Code judges each sentence against the store with its subject given, scans it deterministically,
and checks that every must-name item is cited (12.3.1, 12.3.1a, 12.14.12).

**Why this priority**: 98.6% of first drafts failed the old check and 56% of turns had sentences silently cut
(B §1.2). This is the core of the redesign.

**Independent Test**: unit tests of the declaration judge and coverage on built records; the replay bench on
recorded packets.

**Acceptance Scenarios**:

1. **Given** a turn whose record has a beat outcome and an NPC response, **When** the narrator cites both
   handles in passing sentences, **Then** the first draft is delivered unchanged with no extra model call.
2. **Given** a sentence citing a fact whose value it contradicts, **When** judged, **Then** that sentence alone
   is redrafted with the store's value; the others are kept as written.
3. **Given** an atmosphere sentence naming a present NPC or a numeral, **When** judged, **Then** it is treated
   as undeclared (12.3.1a item 2).
4. **Given** a draft that cites no sentence for a must-name item, **When** two repair rounds fail, **Then** the
   item's rendered line (code-built, a statement) is delivered and a `rule_conflict` ruling is logged.

### User Story 2 - The narrator may furnish the world without a coin flip, never invent what matters (Priority: P1)

New elements carry `element_kind`; the kind fixes the tier (12.14.13). Incidental detail (T1a) is written as
narrated; ordinary knowledge (T1b) is settled by the Oracle; consequential elements (T2) pass only when the
turn's record delivers them; consequential unset properties go to the Oracle (12.3.2 `undetermined` split).

**Independent Test**: unit tests of the tier lookup and of `undetermined` split by tier.

**Acceptance Scenarios**:

1. **Given** "a coil of rope hangs by the door" declared `furniture`, **Then** it is written on mention and not
   cut.
2. **Given** a new `clue` or a non-ordinary `item` not in the record, **Then** the sentence is cut.
3. **Given** an NPC's coat colour (incidental, unset), **Then** it is written as narrated; **given** "the door is
   locked" (consequential, unset), **Then** the Oracle settles it before delivery.

### User Story 3 - Every present NPC has a default, and an addressed NPC always answers (Priority: P1)

Code rolls each present NPC's activity at scene entry (role × watch), fixes the turn's practice, chooses each
engaged or addressed NPC's response (resolved frame → recorded refusal/want → action row clamped to the
practice), and writes every response and activity as a record line with a handle the narrator cites
(12.11.9, DL-12-43). The World model call is no longer on the default path.

**Independent Test**: seeded unit tests: same seed, same responses; an addressed NPC always has a response
line; refusals are voiced.

**Acceptance Scenarios**:

1. **Given** the PC greets a walk-on, **Then** the record holds a response line from `tbl.npc_practice`'s
   greeting row, and the narration cites it.
2. **Given** a refusing row, **Then** the response line is a refusal in the NPC's voice (register, habit),
   never silence.
3. **Given** the same seed and inputs, **Then** the NPC responses are identical.

### User Story 4 - Repairs are narrow (Priority: P2)

A redraft carries only the failing sentences plus the store's values; passing sentences are neither re-sent
nor re-checked; after two rounds a still-failing sentence is cut and uncovered must-name items are rendered;
the plain fallback is the case where no sentence passed (12.3.3).

**Independent Test**: unit tests on the repair loop with a scripted narrator.

### Edge Cases

- The narrator returns no sentences, or the model call fails: the plain fallback (every must-name item
  rendered).
- A must-name item that cannot be rendered as a statement (an Oracle question whose predicate has no listed
  verb): its "yes" is the question's own words; a "no" or an unrenderable item is left out and logged.
- A turn that ends at a pause: no open prompt is restored.
- The array schema hurts prose on a model: the fallback schema (`fiction` plus declarations keyed by sentence
  index) is selectable by config.
- Two or more recorded motives match the event: the World call breaks the tie when enabled; otherwise the best
  word-overlap match is taken (one candidate also goes to the World call: the match is 12.2.9's `[J:flag]`).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The narrator output is `sentences[]` of `{text, refs, about, new[], atmosphere}`; `refs` is a
  closed list built from the packet (record handles `R1…`, one per must-name and citable record item, a
  FICTION_QUESTION answer included, plus the view's fact ids); `about` is the scene scope; `new[]` items carry
  `element_kind`, `name`, `ordinary`, `implied` (12.3.1).
- **FR-002**: A fallback output shape (`fiction` plus declarations keyed by sentence index) is selectable by a
  config flag and judged by the same code (B risk 2).
- **FR-003**: Code resolves each ref into a claim with the subject given and judges it with the existing
  per-class checks; Checker claims in a declared sentence take the declared subject (12.3.1, 12.3.2).
- **FR-004**: Deterministic scans per sentence: names and aliases against `about` (a resolvable name is added
  to `about` and logged as under-declaration; an unresolvable proper name fails), numerals against quantities
  and cited values, pronouns against stored pronouns, mechanics words, sealed text, and an atmosphere
  sentence naming anything addressable (12.3.1a, 12.2.10).
- **FR-005**: Coverage: every must-name item (12.14.12) is cited by some sentence; coverage replaces the
  Checker's `intent_acknowledged` / `next_step_exists` flags for the record's parts (I-150a).
- **FR-006**: `element_kind` maps to a tier through `pacing.yaml#claim_check.element_tiers`; a `person`,
  `item` or `document` declared not `ordinary` is T2; an unknown kind is T2 (12.14.13).
- **FR-007**: `undetermined` claims split: incidental → written as narrated (a fact, source `narration`);
  consequential → the Oracle, then the sentence is redrafted to a "no" (12.3.2, B P5).
- **FR-008**: Per-sentence repair: cut-type failures dropped by code; others redrafted in one narrow call per
  round with only the failing sentences and the store's values; at most two rounds; then cut and render
  uncovered must-name items with `engine/text/render.py`; plain fallback when nothing passed; `rule_conflict`
  ruling only when a rendered line was used (12.3.3, PR-12-2).
- **FR-009**: The open prompt is restored by code only if the draft had one and repair cut it (12.3.3); no
  other patch-in.
- **FR-010**: Default NPC layer per 12.11.9 steps 1–6: activity rolled at scene entry from
  `tbl.npc_activity` (overwrite, never append); practice by `tbl.npc_practice.select_order`; response order
  resolved frame → recorded refusal/want → `tbl.npc_action` by standing clamped to the practice's rows (nearest,
  toward 5); an addressed NPC always answers (a voiced refusal when the source refuses; a walk-on's voice rolled
  on first answer); acceptance decided in code.
- **FR-011**: NPC responses are must-name record lines with handles; activities are citable record lines.
- **FR-012**: The World model call runs only as an optional judge (`world_judge`, default on) of an engaged NPC's recorded wants and refusals; an NPC with none (every walk-on) never causes a call (research R6, ledger I-160).
- **FR-013**: The Checker still runs on every draft (and on each repaired sentence set) but only its claims
  not covered by declarations count as undeclared assertions; the diff-mode Checker and skipping it are spec
  009's.
- **FR-014**: Retire the superseded stopgaps listed in the task's scope (tasks.md, phase "Retire"), each only
  after its replacement passes; keep `_apply_writes` as a backstop.
- **FR-015**: The replay bench accepts a narrator and judge for the new contract; a Claude-CLI narrator plug
  (Haiku, subscription) runs at most 80 recorded packets.

### Key Entities

- **Record item**: one line of the adjudication record with a handle (`R1…`), a kind (beat, cost, harm,
  condition, position, learned, oracle answer, NPC response, activity, omen, lead/incident note, scene),
  `must_name`, the entities it concerns, its words for the narrator and its rendered line.
- **Declared sentence**: text, refs, about, new elements (kind, name, ordinary, implied), atmosphere.
- **Sentence verdict**: pass, or the failure and its fix (cut, redraft with store value, Oracle).
- **NPC default**: activity (scene state), practice, response line and its source.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The full test suite passes, with new tests for the declaration judge, coverage, per-sentence
  repair, the tier lookup, NPC-layer determinism and "an addressed NPC always answers".
- **SC-002**: The offline long-horizon scripted run completes clean (no engine errors beyond the known
  name-exhaustion finding) with contradictions per 100 turns no worse than the spec 005 baseline (0.0).
- **SC-003**: On ≤ 80 recorded packets with a real model: first-draft pass rate > 50% (baseline 1.3%).
- **SC-004**: Turns with cut sentences < 15% (baseline 58%).
- **SC-005**: Narrator calls per turn ≤ 1.2 (baseline 1.81).
- **SC-006**: Undeclared new elements per draft reported against the baseline 2.88 (the < 0.3 gate is spec
  009's).
- **SC-007**: Misses are reported with the real number and what drives it; no pass is faked.

## Assumptions

- Spec-kit clarify is skipped by instruction; decisions are recorded here and in `research.md`.
- A sentence with no declaration, no flag, and nothing the scans or the audit find is treated as atmosphere;
  the strict reading (always undeclared) would cut bare prose the audit found nothing in (12.3.1a reads
  "code scans; the audit finds the rest").
- A beat's outcome and what a learning beat delivered are must-name items (B P1 (d), 12.3.3's rendered-line
  list), besides 12.14.12's list.
- An audit claim (Checker) on a subject the sentence did not declare is judged by its verdict like any claim
  and counted as an undeclared assertion; it does not by itself fail the sentence (the strict reading waits
  for spec 009's measured under-declaration rate).
- The replay bench has packets but no store: the replay judge runs the declaration judge against the packet
  (support = packet, DL-12-42) with the deterministic scans and coverage; store contradictions are covered by
  the unit tests and the long-horizon harness. Repair rounds in the replay call the narrator again.
- A T1b knowledge element is settled by the Oracle at Likely when a present NPC speaks it, else Unlikely
  (12.10.6(d) simplified: no role-fit judgement).
- Wants and refusals carry no tags, so a motive matches the event by content-word overlap (ponytail); the
  World call judges candidates when enabled.
- Out of scope (specs 007–009): Reader, Framer, gate, `incident.py`, `world_step` Talk regexes, diff-mode
  Checker, established-detail slots.
