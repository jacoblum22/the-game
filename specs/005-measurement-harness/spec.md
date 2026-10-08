# Feature Specification: Measurement harness (round-2 Phase 0)

**Feature Branch**: `005-measurement-harness`
**Created**: 2026-10-08
**Status**: Draft
**Input**: "Phase-0 measurement harness for the round-2 redesign: offline replay bench over recorded model
calls, Reader golden set + scorer, long-horizon harness with aged-state store and scripted player, committed
baselines." Plan of record: `research_notes/Playtest round 2 solutions/00_SYNTHESIS.md` §5 Phase 0.

Specs 006–009 cite this harness's numbers as their acceptance gates. The research notes hold the reasoning;
this spec only fixes what is measured, on what data, and what counts as done.

## User Scenarios & Testing

### User Story 1 - Replay bench gives the narration baseline and an A/B slot (Priority: P1)

The owner (or a later spec's implementer) runs one offline command and gets B §1.2's table for today's engine:
first-draft pass rate, turns with cut sentences, Checker class instability on unchanged sentences, narrator
calls per turn, Oracle "no" redrafts, declared vs undeclared new elements. The same command accepts another
narrator and judge and scores them on the same recorded packets (B P1 "Offline A/B").

**Why this priority**: Phase 2's gate (first-draft pass > 50%, cut turns < 15%, narrator calls ≤ 1.2) is
meaningless without a reproducible "today" number from committed data.

**Independent Test**: from a clean checkout (no saves, no network) the command prints the baseline table;
with a stub narrator/judge it prints a second column scored on the same packets.

**Acceptance Scenarios**:
1. **Given** the committed corpus, **When** the bench runs with the recorded plug, **Then** it prints the six
   baseline measures and they equal the committed baseline file.
2. **Given** a narrator and judge supplied by name, **When** the bench runs, **Then** each recorded first-draft
   packet is drafted and judged by them and the same measures are printed for that run.
3. **Given** local saves, **When** the extractor runs, **Then** it rebuilds the corpus deterministically and
   within the size bound.

### User Story 2 - Reader golden set scores any Reader (Priority: P1)

About 80 hand-labelled player lines (D P1 test, D P6) — the exact inputs behind P-004, P-023, P-024, P-031,
P-038, P-064, P-115, P-122, P-123, neutral controls, and negated minimal pairs — with today's fields (verb,
gate, necessity) and the proposed ones (method facets `against_will`, `uses_power`, `speech`; `question_kind`
from C's six kinds). A scorer runs a Reader implementation over the set and prints per-field accuracy.

**Why this priority**: spec 008's gate is "verb ≥ 95%, gate ≥ 98%"; model swaps change adjudication silently
without it (D P6).

**Independent Test**: scoring the recorded Reader outputs (today's Haiku answers, frozen in the set) prints
per-field accuracy with no model call.

**Acceptance Scenarios**:
1. **Given** the golden set, **When** the scorer runs a Reader, **Then** it prints accuracy per field and lists
   the misses by line id.
2. **Given** a Reader that does not produce a field (today's Reader has no facets), **Then** that field shows
   as not scored rather than 0%.

### User Story 3 - Long-horizon harness measures memory and repetition (Priority: P2)

A seeded run of ~300 scripted player lines on the offline model, plus a synthetic store aged to ~300 scenes,
prints a short summary (A P8): contradictions per 100 turns by claim class, recall-probe precision and
coverage, cross-turn novelty-4, view tokens at turns 50/200/300, cached-prefix share per role. A flag switches
the model to Gemini (owner-run).

**Why this priority**: SC-002 (bounded packets) and Phase 3/4 gates need a long-run number; today's evidence
stops at 15 turns.

**Independent Test**: the offline run completes and prints the summary; a second run with the same seed
prints identical numbers.

**Acceptance Scenarios**:
1. **Given** seed S, **When** the scripted run finishes, **Then** the summary prints every metric above and is
   identical across two runs.
2. **Given** the aged store, **When** packets are built at scenes 50/200/300, **Then** view tokens per role are
   printed and the boundedness check passes or names the growing section.

### Edge Cases
- A save from an older engine with missing fields (no `draft_versions`, no claims): skipped and counted.
- A turn with no narration (out-of-fiction, pause): excluded from per-narrated-turn measures, counted in
  per-turn ones.
- A recorded packet whose shared sections changed between commits: stored once per distinct text.
- A pluggable narrator raising an error on a packet: counted as a failed draft, run continues.
- Offline model output is canned: recall and contradiction numbers measure the pipeline, not prose quality;
  the summary says so.

## Requirements

### Functional Requirements
- **FR-001**: An extractor MUST build a curated corpus from local saves: every narrated turn's draft history
  (texts, declared mentions, claim classes per sentence, verdicts, fixes), per-turn call counts by role, and a
  capped sample of first-draft narrator packets with shared sections stored once.
- **FR-002**: The committed corpus MUST stay ≤ 3 MB on disk and be regenerable from saves.
- **FR-003**: The replay bench MUST compute B §1.2's six measures from the corpus with no network or model.
- **FR-004**: The bench MUST accept a narrator (packet → draft) and judge (packet + draft → per-sentence pass /
  fail with class) by import path, and score them on the corpus packets with the same measures that apply.
- **FR-005**: The golden set MUST hold ≥ 75 lines, each with id, source (transcript and input number, or
  "constructed"), the line, the scene context a Reader needs, and labels for verb, gate, necessity,
  `against_will`, `uses_power`, `speech`, `question_kind`.
- **FR-006**: The golden set MUST include the issue lines named in Story 2 and ≥ 8 negated minimal pairs.
- **FR-007**: The scorer MUST run any Reader by import path and print per-field accuracy and misses; recorded
  Haiku outputs MUST be scorable with no model call.
- **FR-008**: The long-horizon harness MUST build an aged synthetic store of ~300 scenes from a seed and report
  view tokens per role at scenes 50/200/300.
- **FR-009**: It MUST drive the real engine with a scripted player of ~300 lines covering revisits, questions
  about absent NPCs, recall probes, scuffles and reading notices, on the offline model by default.
- **FR-010**: It MUST print contradictions per 100 turns by claim class, recall precision and coverage,
  novelty-4 over the previous 10 deliveries, view tokens at turns 50/200/300, and cached-prefix share per role.
- **FR-011**: A real-model run MUST be possible by flag; no real-model run is part of this feature.
- **FR-012**: Every baseline output MUST be committed next to its script, and `implementation-results.md`
  MUST carry the baseline table.
- **FR-013**: The harness MUST NOT change engine or rules code; needed hooks are listed for their owners.
- **FR-014**: Default test runs MUST stay fast; long runs are marked slow and excluded by default.

### Key Entities
- **Corpus turn**: one narrated turn's draft history and call counts (no packet text).
- **Corpus packet**: one first-draft narrator packet (section references) with its recorded draft, claims and
  verdicts.
- **Golden line**: a player line, its context, its labels, and today's recorded Reader answer if one exists.
- **Long-horizon summary**: the metric block for one seeded run.

## Success Criteria
- **SC-001**: A clean checkout reproduces every committed baseline number byte-for-byte, offline, in under 2
  minutes for the bench and golden scorer together.
- **SC-002**: Specs 006–009 can each name a committed baseline number as their gate without new measurement
  code (bench measures, golden fields, long-horizon metrics).
- **SC-003**: The baseline table in `implementation-results.md` matches B §1.2 within the stated population
  difference (B used 33 late runs; the corpus states its own population).
- **SC-004**: The default test suite grows by under 15 seconds.

## Assumptions
- Clarify was skipped by instruction; open questions were answered from the notes:
  - **Population**: the bench reports all saves with draft history and the late subset (stamp ≥ 19:30 on
    2026-10-07, B's 33-run cut) separately.
  - **Judging a new draft**: per D5 support is judged against the packet, so a plugged judge needs only the
    packet; whole-store contradiction is measured in live runs (Story 3), not in the bench.
  - **Gate labels** follow 01.3.1 (G0 question, G1 basic, G2 licensed, G3 unlicensed, G4 impossible), judged
    as a correct Reader would with the PC holding no licence unless the context says so.
  - **`question_kind`** values: `who_is`, `where_is`, `what_happened`, `what_like`, `what_want`, `who_knows`,
    `none` (C §3 Option B list).
  - **Necessity** labels use 01.4.1's reasons; scoring also reports the roll / no-roll collapse.
  - **Cached-prefix share** is the share of a role's packet characters in sections identical to that role's
    previous packet (Gemini implicit caching is prefix-based); offline runs have no provider cache data.
  - **Contradictions** come from recorded verdicts (`contradicted`) by class. The 12.4.8 scene-end sweep is
    not built in the engine (a hook for its owner); the canon audit of A P8 needs P1's details and is out of
    scope.
- Labels are by one labeller (this implementer); disagreements are fixed by editing the set, with history in
  git.
