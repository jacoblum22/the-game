"""Generic multi-category state model for the long-horizon consistency stress test (feature 002).

Extends Feature 001's CharacterState (src/state.py) rather than modifying it -- WorldState
composes a CharacterState plus additional generic categories research showed are the most
fragile fact types (resources that get revised, possessions, position, status/existence flags).
Field names and validation rules follow specs/002-long-horizon-consistency-test/data-model.md.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Literal, Optional, Union

from state import ActionAttempt, CharacterState  # noqa: F401  (ActionAttempt re-exported for reuse)

CommitmentType = Literal["invariant", "ordering", "achievement"]
CommitmentStatus = Literal["pending", "satisfied", "violated"]
ConflictType = Literal["fact", "commitment", "player_input"]
StateCategory = Literal["character_resource", "resources", "possessions", "position", "status_flags"]
TerminationReason = Literal["conflict", "natural_ending", "turn_cap_reached"]
PersonaCondition = Literal["adversarial", "natural"]


@dataclass
class TrajectoryNode:
    """One entry in the generated scenario's ordered plot outline."""

    node_id: str
    trigger_event: str
    key_delta: str
    pov_note: str
    sequence_index: int
    references: list[str] = field(default_factory=list)
    """WorldState keys this node's key_delta affects, e.g. 'status_flags.door_north_locked' or
    'resources.stamina'. Explicit rather than inferred from free text, so reference validation
    (world_state.py's validate_world_state_references) is deterministic, not a text-parsing
    heuristic. Populated by the extraction pipeline itself (src/scenario_pipeline.py)."""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "TrajectoryNode":
        return cls(**data)


@dataclass
class Commitment:
    """A typed, machine-checkable rule the DM's narration must not violate."""

    commitment_id: str
    type: CommitmentType
    description: str
    satisfaction_condition: str
    violation_condition: str
    anchor_node_id: str
    status: CommitmentStatus = "pending"
    references: list[str] = field(default_factory=list)
    """Same convention as TrajectoryNode.references -- WorldState keys this commitment's
    satisfaction/violation conditions depend on."""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Commitment":
        return cls(**data)


@dataclass
class WorldState:
    """The generic, multi-category seeded state -- this session's single source of truth."""

    character: CharacterState
    resources: dict[str, dict[str, int]] = field(default_factory=dict)
    possessions: dict[str, bool] = field(default_factory=dict)
    position: str = ""
    status_flags: dict[str, Union[bool, str]] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "character": self.character.to_dict(),
            "resources": self.resources,
            "possessions": self.possessions,
            "position": self.position,
            "status_flags": self.status_flags,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WorldState":
        return cls(
            character=CharacterState.from_dict(data["character"]),
            resources=data.get("resources", {}),
            possessions=data.get("possessions", {}),
            position=data.get("position", ""),
            status_flags=data.get("status_flags", {}),
        )

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "WorldState":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls.from_dict(data)


@dataclass
class ConflictRecord:
    """One detected conflict, produced by the auditor."""

    turn_number: int
    conflict_type: ConflictType
    state_category: Optional[StateCategory]
    description: str

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "ConflictRecord":
        return cls(**data)


@dataclass
class SessionOutcome:
    """The final, aggregate result of one run."""

    run_id: str
    persona_condition: PersonaCondition
    turns_completed: int
    termination_reason: TerminationReason
    survived: bool
    succeeded: bool
    turn_of_first_conflict: Optional[int] = None
    conflicts: list[ConflictRecord] = field(default_factory=list)
    checkpoints: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "persona_condition": self.persona_condition,
            "turns_completed": self.turns_completed,
            "termination_reason": self.termination_reason,
            "survived": self.survived,
            "succeeded": self.succeeded,
            "turn_of_first_conflict": self.turn_of_first_conflict,
            "conflicts": [c.to_dict() for c in self.conflicts],
            "checkpoints": self.checkpoints,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SessionOutcome":
        return cls(
            run_id=data["run_id"],
            persona_condition=data["persona_condition"],
            turns_completed=data["turns_completed"],
            termination_reason=data["termination_reason"],
            survived=data["survived"],
            succeeded=data["succeeded"],
            turn_of_first_conflict=data.get("turn_of_first_conflict"),
            conflicts=[ConflictRecord.from_dict(c) for c in data.get("conflicts", [])],
            checkpoints=data.get("checkpoints", []),
        )

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "SessionOutcome":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls.from_dict(data)


# --- Structural validation (T003) -------------------------------------------------------
#
# These are pure, deterministic checks -- no network calls, no LLM judgment -- unlike the
# semantic isolation check (scenario_pipeline.check_isolation, T007). They catch pipeline
# construction bugs (bad IDs, orphaned references) before a scenario is ever used in a real
# run, per data-model.md's validation notes.

VALID_COMMITMENT_TYPES = ("invariant", "ordering", "achievement")


def validate_trajectory(nodes: list[TrajectoryNode]) -> list[str]:
    """Returns a list of error strings; empty means valid."""
    errors: list[str] = []

    ids = [n.node_id for n in nodes]
    duplicates = {i for i in ids if ids.count(i) > 1}
    if duplicates:
        errors.append(f"Duplicate node_id(s): {sorted(duplicates)}")

    indices = sorted(n.sequence_index for n in nodes)
    expected = list(range(len(nodes)))
    if indices != expected:
        errors.append(
            f"sequence_index values must be a gapless 0..N-1 ordering; got {indices}, expected {expected}"
        )

    return errors


def validate_commitments(commitments: list[Commitment], trajectory: list[TrajectoryNode]) -> list[str]:
    """Returns a list of error strings; empty means valid."""
    errors: list[str] = []

    ids = [c.commitment_id for c in commitments]
    duplicates = {i for i in ids if ids.count(i) > 1}
    if duplicates:
        errors.append(f"Duplicate commitment_id(s): {sorted(duplicates)}")

    trajectory_ids = {n.node_id for n in trajectory}
    for c in commitments:
        if c.anchor_node_id not in trajectory_ids:
            errors.append(
                f"Commitment {c.commitment_id!r} has anchor_node_id {c.anchor_node_id!r}, "
                f"which does not match any trajectory node"
            )
        if c.type not in VALID_COMMITMENT_TYPES:
            errors.append(f"Commitment {c.commitment_id!r} has invalid type {c.type!r}")

    return errors


def _reference_exists(world_state: WorldState, ref: str) -> bool:
    """Checks whether a dotted reference like 'status_flags.door_north_locked' or
    'resources.stamina' points at a key that actually exists in world_state. Bare 'position'
    and 'character_resource' (the single CharacterState resource) need no sub-key."""
    if ref in ("position", "character_resource"):
        return True
    if "." not in ref:
        return False
    category, key = ref.split(".", 1)
    category_dict = getattr(world_state, category, None)
    if not isinstance(category_dict, dict):
        return False
    return key in category_dict


def validate_world_state_references(
    world_state: WorldState, trajectory: list[TrajectoryNode], commitments: list[Commitment]
) -> list[str]:
    """Returns a list of error strings; empty means valid.

    Checks only that referenced KEYS exist somewhere in the initial WorldState -- not that
    their VALUES are isolation-correct (that's scenario_pipeline.check_isolation's job, a
    semantic check this deliberately does not duplicate).
    """
    errors: list[str] = []

    for node in trajectory:
        for ref in node.references:
            if not _reference_exists(world_state, ref):
                errors.append(f"Trajectory node {node.node_id!r} references unknown key {ref!r}")

    for c in commitments:
        for ref in c.references:
            if not _reference_exists(world_state, ref):
                errors.append(f"Commitment {c.commitment_id!r} references unknown key {ref!r}")

    return errors
