# Feature Specification: Scene state written by code (spec 010)

**Feature Branch**: `claude/nostalgic-dewdney-eb1cde` (spec dir `010-scene-state`)

**Created**: 2026-10-08

**Status**: Implemented (see [implementation-results.md](implementation-results.md))

**Input**: The final live run (`evals/baselines/live_narration_final.txt`, Haiku, 19 narrated turns) left one
dominant failure: *contradicted position* in 8 of 19 turns. The narrator places people differently from the store,
because nothing wrote positions or postures from what happened in the beat. 00.6.6a item 4 and 12.14.13's T1c row
say code writes scene state; the per-verb outcome table was never written.

Rules implemented (look up with `rules/tools/rq.py`; not restated here): T-12-18 (new; data
`pacing.yaml#details.scene_writes`), 00.6.6a item 4, 12.11.9 steps 1 and 3, 12.4.8 step 8 (bands cleared at scene
end), 12.14.13 (T1c row), 12.3.1 (`position` row), DL-12-77. Rules wave report:
`rules/_process/reports/R2-F-report.md`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A resolved beat leaves people where it put them (Priority: P1)

After a beat resolves, code writes the T1c slots T-12-18 names for its actor and target (posture, held, manner,
activity) through `write_detail`, citing the beat's frame (or beat) as the explaining event, so a later value
supersedes an earlier one only with a cause. All are `scene` slots and expire at scene end.

**Acceptance Scenarios**:

1. **Given** a successful Grapple at Standard reach, **Then** the target's posture is "held fast by you" and the
   PC holds them in a grip; at Great reach the posture is superseded by "restrained by you", citing the frame.
2. **Given** a slot that expired at the last scene end, **When** a new beat writes it, **Then** the write
   supersedes the cleared fact (no store rejection).

### User Story 2 - An NPC's response changes their manner, and their activity only when they move (Priority: P1)

Each engaged NPC's response (12.11.9 step 3: a resolved Talk, a refusal, a want, a `tbl.npc_action` row clamped
to the practice) writes manner, and activity only for a physical change (squares up, turns away, takes cover).
The rolled activity is the `activity` detail.

### User Story 3 - The narrator cites scene state instead of improvising it (Priority: P1)

Every turn, the record's scene-state lines are rebuilt for whoever is present *now*: each present person's (the
PC's too) activity, posture, hold and manner, and each present NPC's range band to the PC. They are citable record
lines (not must-name). A person who left the scene this turn drops out. Range bands are cleared at scene end.

**Acceptance Scenarios**:

1. **Given** the PC travels to a new place mid-turn, **Then** no line names an NPC from the old scene.
2. **Given** a shove earlier in a scene, **When** the PC returns to that place in a later scene, **Then** no band
   to the PC is shown or judged.

## Success Criteria

- **SC-001** Full suite passes; ruff and pyright clean on touched files; rules validator 0 ERROR / 0 WARN.
- **SC-002** `evals/longhorizon.py --mode scripted`: 0 engine errors.
- **SC-003** Live loop (Haiku via `--model claude-narration`, at most 25 narrated turns): report first-draft pass
  rate (36.8% before, target > 50%), position contradictions (8/19 before), cut turns, calls per turn.
