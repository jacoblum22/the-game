"""Conflict auditor: extends dm_agent.judge_consistency into a full fact/commitment/
player-input conflict classifier with state-category attribution (feature 002, T009).

Contract #6 in contracts/pipeline-prompts.md. Still a test-harness grading tool, not a
live-gameplay judge-gate -- same documented limitation as judge_consistency: this shares a
model family with the narrator, not the independent-model-family judge Pattern P13 eventually
calls for. That is an accepted, out-of-scope limitation for this feature (spec.md's
Assumptions), not something check_turn resolves.
"""

from __future__ import annotations

import json
from typing import Optional

from dm_agent import call_json
from world_state import Commitment, ConflictRecord, WorldState


def check_turn(
    turn_number: int,
    narration: str,
    player_action: str,
    world_state: WorldState,
    commitments: list[Commitment],
) -> Optional[ConflictRecord]:
    """Checks one turn's narration against the seeded fact ledger and active commitments.

    Returns a ConflictRecord if a conflict is found, or None. Uses a fresh call with no prior
    conversation context, same discipline as judge_consistency, to avoid the narrating turn's
    own potential bias influencing the check.
    """
    world_state_json = json.dumps(world_state.to_dict(), indent=2)
    active_commitments = [c for c in commitments if c.status == "pending"]
    commitments_json = json.dumps([c.to_dict() for c in active_commitments], indent=2)

    prompt = f"""A tabletop RPG session is being audited for consistency. Below are the
current known world state, the active commitments (rules the narration must not violate),
the player's action this turn, and the game master's narration in response to it.

Check for a conflict of exactly one of these three types:
- "fact": the narration asserts something that contradicts the current world state (e.g. a
  door listed as locked is narrated as freely open with no unlocking event described this
  turn or previously; a character listed as alive is narrated as dead with no killing event)
- "commitment": the narration violates one of the active commitments' violation_condition
- "player_input": the narration ignores or substitutes a different action than what the
  player actually attempted, without any in-fiction justification (note: the game master
  narrating that an action FAILS or has an unexpected consequence is NOT a player_input
  conflict -- only narrating a DIFFERENT action than the one the player took is)

If a fact-type conflict is found, also identify which category of the world state it belongs
to: "character_resource", "resources", "possessions", "position", or "status_flags".

Output a single JSON object with exactly these fields:
- "conflict_found": true or false
- "conflict_type": one of "fact", "commitment", "player_input", or null if no conflict
- "state_category": one of "character_resource", "resources", "possessions", "position",
  "status_flags", or null (null also if conflict_type is not "fact")
- "description": a short explanation of the conflict, or null if no conflict

Output ONLY the JSON object, no other text, no markdown code fences.

Current world state:
{world_state_json}

Active commitments:
{commitments_json}

Player's action this turn:
{player_action}

Game master's narration this turn:
{narration}
"""
    data = call_json(prompt)
    if not data.get("conflict_found"):
        return None

    return ConflictRecord(
        turn_number=turn_number,
        conflict_type=data["conflict_type"],
        state_category=data.get("state_category"),
        description=data.get("description") or "",
    )
