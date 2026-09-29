"""Generic multi-category state model for the long-horizon consistency stress test (feature 002).

Extends Feature 001's CharacterState (src/state.py) rather than modifying it -- WorldState
composes a CharacterState plus additional generic categories research showed are the most
fragile fact types (resources that get revised, possessions, position, status/existence flags).
Field names and validation rules follow specs/002-long-horizon-consistency-test/data-model.md.
"""

from __future__ import annotations

import json
import copy
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path
from typing import Literal, Optional, Union

from resolution import resolve
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
        # Found live (T021): the extraction call runs in plain JSON mode, not a schema-bound
        # mode, so the model can emit a stray top-level key (observed: a literal
        # "possessions.keeper_logbook" field sitting beside "references" instead of being an
        # item inside it). Filtering to known fields turns that into a silently-dropped key
        # instead of a raw TypeError crashing the whole pipeline before validation ever runs.
        known = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in known})


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
        # Same defensive filtering as TrajectoryNode.from_dict -- see its comment.
        known = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in known})


@dataclass
class WorldState:
    """The generic, multi-category seeded state -- this session's single source of truth."""

    character: CharacterState
    resources: dict[str, dict[str, int]] = field(default_factory=dict)
    possessions: dict[str, bool] = field(default_factory=dict)
    position: str = ""
    status_flags: dict[str, Union[bool, str]] = field(default_factory=dict)

    def to_dict(self) -> dict:
        # Found live (T021 verification): the old version returned these three dicts by
        # LIVE REFERENCE, not as a snapshot. Confirmed end-to-end (including through the
        # google-genai SDK's own Part construction, which also holds a live reference rather
        # than copying) that an EARLIER get_state() result silently changes if a LATER tool
        # call in the same turn mutates world_state -- meaning the model (and our own auditor)
        # could receive an already-mutated "snapshot" disguised as an earlier one. resources
        # needs a deep copy since update_resource mutates its inner per-resource dicts in
        # place; possessions/status_flags only ever hold scalar values, so a shallow copy of
        # the outer dict is enough to stop them aliasing the live object.
        return {
            "character": self.character.to_dict(),
            "resources": copy.deepcopy(self.resources),
            "possessions": dict(self.possessions),
            "position": self.position,
            "status_flags": dict(self.status_flags),
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
VALID_REFERENCE_PREFIXES = ("resources.", "possessions.", "status_flags.")
VALID_BARE_REFERENCES = ("position", "character_resource")


def _is_well_formed_reference(ref: str) -> bool:
    """Checks a reference string uses one of the 5 allowed forms, catching a model inventing
    its own category (e.g. "npc.clerk.is_alive") at the stage it's generated, rather than two
    stages later when validate_world_state_references would otherwise be the first to notice."""
    if ref in VALID_BARE_REFERENCES:
        return True
    return any(ref.startswith(prefix) and len(ref) > len(prefix) for prefix in VALID_REFERENCE_PREFIXES)


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

    for n in nodes:
        for ref in n.references:
            if not _is_well_formed_reference(ref):
                errors.append(
                    f"Trajectory node {n.node_id!r} has malformed reference {ref!r} -- must be "
                    f"one of {VALID_BARE_REFERENCES} or start with one of {VALID_REFERENCE_PREFIXES}"
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
        for ref in c.references:
            if not _is_well_formed_reference(ref):
                errors.append(
                    f"Commitment {c.commitment_id!r} has malformed reference {ref!r} -- must be "
                    f"one of {VALID_BARE_REFERENCES} or start with one of {VALID_REFERENCE_PREFIXES}"
                )

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

    # Found live (fast-forward batch): a generation pass seeded the SAME resource name as both
    # `character.resource_name` (the one primary resource, written via update_state) and a key
    # in `resources` (an additional resource, written via update_resource) -- two independently
    # tracked state slots sharing a name, with no way for the DM to know only one is "real."
    # The DM correctly called update_state; the auditor correctly checked resources[name], which
    # nothing had touched, and (correctly, given what it was shown) flagged a conflict. The seed
    # itself was the bug, not the DM or the auditor.
    if world_state.character.resource_name in world_state.resources:
        errors.append(
            f"Resource name {world_state.character.resource_name!r} is used for both "
            f"character.resource_name and a key in resources -- these are two separately "
            f"tracked state slots and must not share a name"
        )

    for node in trajectory:
        for ref in node.references:
            if not _reference_exists(world_state, ref):
                errors.append(f"Trajectory node {node.node_id!r} references unknown key {ref!r}")

    for c in commitments:
        for ref in c.references:
            if not _reference_exists(world_state, ref):
                errors.append(f"Commitment {c.commitment_id!r} references unknown key {ref!r}")

    return errors


# --- Tool-calling extension for multi-category state (T013 -- a real, reasoned deviation) ---
#
# Feature 001's src/tools.py stays completely unchanged (plan.md's Project Structure). FR-003
# said roll_check/get_state/update_state would be reused "without modification to those tools'
# contracts" -- that holds for roll_check and update_state below (byte-for-byte identical
# behavior to Feature 001's ToolHandlers), but WorldState's extra categories (named resources
# beyond the one CharacterState resource, possessions, position, status_flags) genuinely need
# a way to be written that didn't exist in Feature 001's scope, since Feature 001 only ever had
# one resource to update. Rather than force update_state's signature to do something it wasn't
# designed for, two new tools are added ADDITIVELY -- update_resource and set_fact -- rather
# than modifying the original three's contracts. This is documented here as a real, reasoned
# deviation discovered during implementation, not a silent scope change; see
# contracts/pipeline-prompts.md for the corresponding contract note.

EXTRA_TOOL_SCHEMAS: list[dict] = [
    {
        "name": "update_resource",
        "description": (
            "Apply a change to one of the world's additional tracked resources (not the "
            "character's primary resource -- use update_state for that). Call this whenever "
            "a turn's outcome implies a change to a named resource in `resources`."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "The resource's name, matching a key in `resources`."},
                "delta": {"type": "integer", "description": "Signed change to apply."},
                "reason": {"type": "string", "description": "Short reason for the change, for the audit log."},
            },
            "required": ["name", "delta", "reason"],
        },
    },
    {
        "name": "set_fact",
        "description": (
            "Set a possession, status flag, or the current position to a new value. Call "
            "this whenever a turn's outcome implies such a change -- do not narrate a fact "
            "change without also calling this."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": ["possessions", "status_flags", "position"],
                    "description": "Which category of fact to set.",
                },
                "key": {
                    "type": "string",
                    "description": "The fact's key within its category (ignored for 'position').",
                },
                "value": {
                    "type": "string",
                    "description": "The new value, as a string ('true'/'false' for booleans).",
                },
                "reason": {"type": "string", "description": "Short reason for the change, for the audit log."},
            },
            "required": ["category", "key", "value", "reason"],
        },
    },
]


def _coerce_fact_value(value: str) -> bool | str:
    """status_flags may be boolean or a short string; possessions are always boolean."""
    if value.strip().lower() in ("true", "false"):
        return value.strip().lower() == "true"
    return value


class WorldStateToolHandlers:
    """Same dispatch interface as tools.ToolHandlers (roll_check/get_state/update_state),
    backed by a WorldState instead of a bare CharacterState, plus the two additive tools
    above. roll_check and update_state keep byte-for-byte identical behavior to Feature 001's
    ToolHandlers -- only what get_state returns (the whole WorldState, richer than just the
    character) differs.
    """

    def __init__(self, world_state: WorldState, default_modifier: int = 2) -> None:
        self.world_state = world_state
        self.default_modifier = default_modifier

    def roll_check(self, dc: int, modifier: Optional[int] = None) -> dict:
        result = resolve(dc=dc, modifier=modifier if modifier is not None else self.default_modifier)
        return {
            "roll": result.roll,
            "modifier": result.modifier,
            "total": result.total,
            "degree": result.degree,
        }

    def get_state(self) -> dict:
        return self.world_state.to_dict()

    def update_state(self, delta: int, reason: str) -> dict:
        self.world_state.character.apply_delta(delta)
        return {
            "resource_current": self.world_state.character.resource_current,
            "resource_max": self.world_state.character.resource_max,
        }

    def update_resource(self, name: str, delta: int, reason: str) -> dict:
        if name not in self.world_state.resources:
            raise ValueError(f"Unknown resource {name!r} -- not in world_state.resources")
        entry = self.world_state.resources[name]
        entry["current"] = max(0, min(entry["max"], entry["current"] + delta))
        return {"name": name, "current": entry["current"], "max": entry["max"]}

    def set_fact(self, category: str, key: str, value: str, reason: str) -> dict:
        if category == "position":
            self.world_state.position = value
            return {"category": "position", "value": self.world_state.position}
        if category == "possessions":
            coerced = _coerce_fact_value(value)
            self.world_state.possessions[key] = coerced if isinstance(coerced, bool) else True
            return {"category": "possessions", "key": key, "value": self.world_state.possessions[key]}
        if category == "status_flags":
            self.world_state.status_flags[key] = _coerce_fact_value(value)
            return {"category": "status_flags", "key": key, "value": self.world_state.status_flags[key]}
        raise ValueError(f"Unknown fact category: {category!r}")

    def dispatch(self, tool_name: str, tool_input: dict) -> dict:
        if tool_name == "roll_check":
            return self.roll_check(**tool_input)
        if tool_name == "get_state":
            return self.get_state()
        if tool_name == "update_state":
            return self.update_state(**tool_input)
        if tool_name == "update_resource":
            return self.update_resource(**tool_input)
        if tool_name == "set_fact":
            return self.set_fact(**tool_input)
        raise ValueError(f"Unknown tool: {tool_name}")
