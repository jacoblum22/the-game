# Data Model: Long-Horizon Consistency Stress Test

Derived from spec.md's Key Entities, extending Feature 001's `state.py` rather than replacing
it. Category names are deliberately generic (per research.md's decision) so the same schema
serves any of the 3+ campaign outlines SC-001 requires.

## TrajectoryNode

One entry in the generated scenario's ordered plot outline.

| Field | Type | Notes |
|---|---|---|
| `node_id` | string | Unique within the scenario; referenced by `Commitment.anchor_node_id`. |
| `trigger_event` | string | What happens at this node, in plain language. |
| `key_delta` | string | The observable, world-state-level change this node causes — not a mental-state-only change (per NCP-Bench's definition). |
| `pov_note` | string | What the player-character could plausibly know at/after this node — enforces the point-of-view constraint during generation. |
| `sequence_index` | integer | Position in the trajectory's order; used by the isolation check to determine what's "not yet true" at the seed point. |
| `references` | list[string] | *(Added during implementation.)* Dotted `WorldState` keys this node's `key_delta` affects (e.g. `"status_flags.door_north_locked"`). Explicit rather than inferred from free text, so `world_state.validate_world_state_references` is a deterministic check, not a text-parsing heuristic. |

## Commitment

A typed, machine-checkable rule the DM's narration must not violate.

| Field | Type | Notes |
|---|---|---|
| `commitment_id` | string | Unique within the scenario. |
| `type` | enum | One of `invariant`, `ordering`, `achievement`. |
| `description` | string | Plain-language statement of the commitment. |
| `satisfaction_condition` | string | Explicit, fact-based condition for this commitment being met. Must not require interpretive judgment (per NCP-Bench's construction requirement). |
| `violation_condition` | string | Explicit, fact-based condition for this commitment being broken. |
| `anchor_node_id` | string | The `TrajectoryNode.node_id` this commitment is conditioned on. |
| `status` | enum | One of `pending`, `satisfied`, `violated`. Starts `pending`; updated by the auditor as the session runs. |
| `references` | list[string] | *(Added during implementation.)* Same convention as `TrajectoryNode.references` — dotted `WorldState` keys this commitment's conditions depend on. |

**Validation**: excludes static background facts (names, occupations) per NCP-Bench's
construction rule — a commitment must be about something that can actually be violated during
play, not a fact that's simply true forever.

## WorldState

The generic, multi-category seeded state — this session's single source of truth, extending
Feature 001's `CharacterState` rather than replacing it.

| Field | Type | Notes |
|---|---|---|
| `character` | CharacterState | Reused from Feature 001 unmodified (name, one resource, current/max). |
| `resources` | dict[str, {current: int, max: int}] | Additional numeric resources beyond `character`'s single one — at least one must be present and revised more than once per FR-002, since research shows updated numeric state is the single most fragile category. |
| `possessions` | dict[str, bool] | Item/possession flags (has the player obtained X). |
| `position` | string | Current location fact. |
| `status_flags` | dict[str, bool \| string] | Existence/status facts — alive/dead, present/absent, introduced/not-yet-introduced, locked/unlocked. |

**Validation**: every key in `resources`/`possessions`/`status_flags` used anywhere in the
generated `Commitment` set or `TrajectoryNode` set must exist in the initial `WorldState` (or be
explicitly marked not-yet-true per the isolation principle) — an orphaned reference is a
pipeline construction bug, not a runtime conflict, and should fail scenario generation rather
than surface later as a false-positive conflict.

## ConflictRecord

One entry per detected conflict, produced by the auditor.

| Field | Type | Notes |
|---|---|---|
| `turn_number` | integer | When the conflict was detected. |
| `conflict_type` | enum | One of `fact`, `commitment`, `player_input`, per NCP-Bench's taxonomy. |
| `state_category` | enum or null | Which `WorldState` category is implicated (`character_resource`, `resources`, `possessions`, `position`, `status_flags`), null for a pure commitment/player-input conflict not tied to a specific state field. |
| `description` | string | What the auditor found, for human review. |

## SessionOutcome

The final, aggregate result of one run — this is what FR-008's report is built from.

| Field | Type | Notes |
|---|---|---|
| `run_id` | string | Identifies which scenario + persona-condition this run used. |
| `persona_condition` | enum | `adversarial` or `natural`. |
| `turns_completed` | integer | How many turns actually ran before stopping. |
| `termination_reason` | enum | One of `conflict`, `natural_ending`, `turn_cap_reached`. |
| `survived` | boolean | True iff `termination_reason` is `natural_ending` or `turn_cap_reached` (no conflict occurred). |
| `succeeded` | boolean | True iff `survived` AND every `achievement`-type `Commitment` reached `status: satisfied`. |
| `turn_of_first_conflict` | integer or null | Null if `survived` is true. |
| `conflicts` | list[ConflictRecord] | All conflicts detected during the run, even after the first (useful for category-rate analysis even on a run that "failed" early). |
| `checkpoints` | list[{turn_number, survived_so_far, conflict_count_so_far}] | Intermediate snapshots per FR-008's "not only at session end" requirement. |

**State transitions**: `Commitment.status` moves `pending → satisfied` or `pending → violated`
(one-way; per NCP-Bench's own design, a violated commitment does not get a chance to later
become satisfied). `SessionOutcome.termination_reason` is set exactly once, when the run stops.
