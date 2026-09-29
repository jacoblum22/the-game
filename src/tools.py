"""Tool schemas and handlers for roll_check, get_state, update_state.

This module IS the boundary the constitution's Principle I and Pattern P13 care about:
the model can only affect mechanics and state by calling these tools -- it cannot narrate
a change into existence. Shapes here match specs/001-action-resolution-probe/contracts/tools.md
exactly. Deliberately absent: any tool for narration or for deciding whether an action needs
resolution -- those stay as the model's own judgment, per Principle III's resolved default.
"""

from __future__ import annotations

from typing import Any

from resolution import resolve
from state import CharacterState, SessionLog

# Anthropic tool-use schemas. See contracts/tools.md for the input/output contract these encode.
TOOL_SCHEMAS: list[dict[str, Any]] = [
    {
        "name": "roll_check",
        "description": (
            "Resolve an action that requires a check. Computes a deterministic "
            "degree-of-success from a real dice roll -- you supply the DC and modifier, "
            "the roll and degree are computed here, not by you. Call this only when the "
            "action genuinely has stakes; do not call it for stakes-free roleplay."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "dc": {"type": "integer", "description": "Target number to beat."},
                "modifier": {
                    "type": "integer",
                    "description": "Flat modifier added to the raw d20 roll.",
                },
            },
            "required": ["dc", "modifier"],
        },
    },
    {
        "name": "get_state",
        "description": (
            "Query the character's current tracked state. Call this before narrating any "
            "turn where the current resource value might matter, rather than relying on "
            "your own memory of what you said last turn."
        ),
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "update_state",
        "description": (
            "Apply a change to the character's tracked resource. Call this whenever a "
            "turn's outcome implies a change -- do not narrate a state change without "
            "also calling this, and do not call this without narrating a consistent reason."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "delta": {
                    "type": "integer",
                    "description": "Signed change to apply (negative to reduce, positive to restore).",
                },
                "reason": {
                    "type": "string",
                    "description": "Short reason for the change, for the audit log -- no mechanical effect.",
                },
            },
            "required": ["delta", "reason"],
        },
    },
]


class ToolHandlers:
    """Holds the live session state and dispatches tool calls against it."""

    def __init__(self, session: SessionLog, default_modifier: int = 2) -> None:
        self.session = session
        self.default_modifier = default_modifier
        self.last_update_reason: str | None = None

    def roll_check(self, dc: int, modifier: int | None = None) -> dict[str, Any]:
        result = resolve(dc=dc, modifier=modifier if modifier is not None else self.default_modifier)
        return {
            "roll": result.roll,
            "modifier": result.modifier,
            "total": result.total,
            "degree": result.degree,
        }

    def get_state(self) -> dict[str, Any]:
        return self.session.character.to_dict()

    def update_state(self, delta: int, reason: str) -> dict[str, Any]:
        self.session.character.apply_delta(delta)
        self.last_update_reason = reason
        return {
            "resource_current": self.session.character.resource_current,
            "resource_max": self.session.character.resource_max,
        }

    def dispatch(self, tool_name: str, tool_input: dict[str, Any]) -> dict[str, Any]:
        """Route a tool_use block's name/input to the matching handler."""
        if tool_name == "roll_check":
            return self.roll_check(**tool_input)
        if tool_name == "get_state":
            return self.get_state()
        if tool_name == "update_state":
            return self.update_state(**tool_input)
        raise ValueError(f"Unknown tool: {tool_name}")
