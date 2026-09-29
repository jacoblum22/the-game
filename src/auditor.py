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

from ability_pool import SOURCE_ARCHETYPES, AbilityGrant
from dm_agent import call_json
from world_state import Commitment, ConflictRecord, WorldState


def check_turn(
    turn_number: int,
    narration: str,
    player_action: str,
    world_state: WorldState,
    commitments: list[Commitment],
    state_before: Optional[dict] = None,
    ability_grant: Optional[AbilityGrant] = None,
) -> Optional[ConflictRecord]:
    """Checks one turn's narration against the seeded fact ledger and active commitments.

    Returns a ConflictRecord if a conflict is found, or None. Uses a fresh call with no prior
    conversation context, same discipline as judge_consistency, to avoid the narrating turn's
    own potential bias influencing the check.

    `state_before` -- found live (T021 verification): without this, the auditor was only ever
    given the CURRENT (i.e. already-mutated-by-this-turn's-own-tool-calls) world state, with no
    way to tell "this was already true before the action" apart from "this became true because
    of the tool call THIS turn's own narration is describing." It was systematically flagging
    ordinary cause-and-effect (narration says "you find the spyglass," this turn's own tool
    call granted the spyglass) as a contradiction, and fabricating incorrect "before" values
    for resource deltas it was never actually shown. Passing the real pre-turn snapshot
    explicitly, separate from the post-turn one, removes the guesswork. Optional and defaults
    to None (old behavior) only so any other caller isn't forced to supply it immediately.

    `ability_grant` -- feature 003 (T013): when this turn called `grant_ability`, pass the
    resulting `AbilityGrant` so the auditor also checks whether the narration matches what was
    actually granted (name, description, and any stated limitation), reusing this same
    narration-vs-structured-state comparison rather than a separate mechanism, per
    contracts/tools.md. Optional and defaults to None so ordinary (non-granting) turns are
    unaffected.
    """
    world_state_json = json.dumps(world_state.to_dict(), indent=2)
    state_before_json = (
        json.dumps(state_before, indent=2) if state_before is not None else "(not provided)"
    )
    active_commitments = [c for c in commitments if c.status == "pending"]
    commitments_json = json.dumps([c.to_dict() for c in active_commitments], indent=2)

    ability_grant_block = ""
    if ability_grant is not None:
        template = next(
            t
            for t in SOURCE_ARCHETYPES[ability_grant.source_archetype].pool
            if t.template_id == ability_grant.template_id
        )
        ability_grant_block = f"""

This turn also granted a new ability. Check whether the narration is consistent with it -- does
it describe the effect this ability actually has (including its stated limitation), without
contradicting or inventing a different effect? A narration that doesn't mention the grant at
all is fine (it may be covered by other narration); only flag it if the narration actively
describes something that contradicts the granted ability.

Granted ability:
- name: {template.name}
- description: {template.description}
"""

    prompt = f"""A tabletop RPG session is being audited for consistency. Below are the world
state BEFORE this turn's action, the world state AFTER it (reflecting any tool calls this
turn's own resolution made), the active commitments (rules the narration must not violate),
the player's action this turn, and the game master's narration in response to it.

Check for a conflict of exactly one of these three types:
- "fact": the narration asserts something that contradicts the state. A change between the
  BEFORE and AFTER state that the narration itself describes happening THIS turn (e.g. the
  AFTER state shows a door unlocked, and the narration describes unlocking it this turn) is
  NOT a conflict -- that is the narration correctly explaining the change. Only flag a fact
  conflict when the narration is inconsistent with the state and nothing in the narration (this
  turn) explains the discrepancy -- e.g. the AFTER state still shows a door locked but the
  narration describes walking through it freely open; or a resource's actual BEFORE-to-AFTER
  delta doesn't match the delta the narration itself claims happened.
- "commitment": the narration violates one of the active commitments' violation_condition
- "player_input": the narration ignores or substitutes a different action than what the
  player actually attempted, without any in-fiction justification (note: the game master
  narrating that an action FAILS or has an unexpected consequence is NOT a player_input
  conflict -- only narrating a DIFFERENT action than the one the player took is)
{ability_grant_block}
If a fact-type conflict is found, also identify which category of the world state it belongs
to: "character_resource", "resources", "possessions", "position", "status_flags", or
"abilities" (use "abilities" specifically for a granted-ability/narration mismatch).

Output a single JSON object with exactly these fields:
- "conflict_found": true or false
- "conflict_type": one of "fact", "commitment", "player_input", or null if no conflict
- "state_category": one of "character_resource", "resources", "possessions", "position",
  "status_flags", "abilities", or null (null also if conflict_type is not "fact")
- "description": a short explanation of the conflict, or null if no conflict

Output ONLY the JSON object, no other text, no markdown code fences.

World state BEFORE this turn's action:
{state_before_json}

World state AFTER this turn's action:
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
