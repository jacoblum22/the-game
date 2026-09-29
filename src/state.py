"""Character state and session-log data structures for the action-resolution probe (feature 001).

Fields and validation rules here follow specs/001-action-resolution-probe/data-model.md
exactly. Nothing here is meant to survive into the real ruleset unchanged -- see that
feature's spec.md Assumptions.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, Optional

Degree = Literal["critical_success", "success", "failure", "critical_failure"]


@dataclass
class CharacterState:
    """The single source of truth for a character's tracked resource.

    Held in the session's JSON file; the model must query/update this via tools
    (src/tools.py) rather than track it in its own conversational memory.
    """

    name: str
    resource_name: str
    resource_current: int
    resource_max: int

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if not 0 <= self.resource_current <= self.resource_max:
            raise ValueError(
                f"resource_current ({self.resource_current}) must be between 0 and "
                f"resource_max ({self.resource_max}), per data-model.md's validation rule"
            )

    def apply_delta(self, delta: int) -> None:
        """Apply a change to resource_current, clamped to [0, resource_max]."""
        new_value = self.resource_current + delta
        self.resource_current = max(0, min(self.resource_max, new_value))

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "CharacterState":
        return cls(**data)


@dataclass
class ActionAttempt:
    """One row per player action, whether or not it required resolution.

    This is the row that makes SC-002/SC-003 (probe-results.md, spec.md) checkable.
    """

    turn_number: int
    action_description: str
    requires_resolution: bool
    narration: str
    state_before: dict
    state_after: dict
    dc: Optional[int] = None
    roll: Optional[int] = None
    modifier: Optional[int] = None
    total: Optional[int] = None
    degree: Optional[Degree] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def __post_init__(self) -> None:
        if self.requires_resolution and self.degree is None:
            raise ValueError(
                "degree must be set when requires_resolution is True "
                "(data-model.md: 'degree must be non-null iff requires_resolution is true')"
            )
        if not self.requires_resolution and self.degree is not None:
            raise ValueError(
                "degree must be None when requires_resolution is False "
                "(data-model.md: 'degree must be non-null iff requires_resolution is true')"
            )

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "ActionAttempt":
        return cls(**data)


@dataclass
class SessionLog:
    """The full record for one session -- the flat JSON file (plan.md's Storage decision)."""

    character: CharacterState
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    turns: list[ActionAttempt] = field(default_factory=list)

    def append_turn(self, turn: ActionAttempt) -> None:
        self.turns.append(turn)

    def to_dict(self) -> dict:
        return {
            "character": self.character.to_dict(),
            "started_at": self.started_at,
            "turns": [t.to_dict() for t in self.turns],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SessionLog":
        return cls(
            character=CharacterState.from_dict(data["character"]),
            started_at=data["started_at"],
            turns=[ActionAttempt.from_dict(t) for t in data.get("turns", [])],
        )

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "SessionLog":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls.from_dict(data)
