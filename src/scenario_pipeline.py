"""Three-stage synthetic scenario construction pipeline (feature 002, T006/T007).

Adapts NCP-Bench's construction approach (trajectory -> commitments -> initial facts, each
stage conditioned on the prior one) rather than inventing a new method -- see research.md's
decision for why. Prompts here are our own wording, not copied from NCP-Bench's published
templates, but follow the same structure and enforce the same T=0 Absolute Isolation
Principle. Each extraction function validates its own output immediately (T003's validators)
and raises on failure rather than returning malformed data -- per contracts/pipeline-prompts.md.

generate_scenario(), which orchestrates all four steps into one call, is User Story 1's own
task (T010), not implemented here -- this module only provides the atomic pieces.
"""

from __future__ import annotations

import json

from dm_agent import call_json
from world_state import (
    Commitment,
    TrajectoryNode,
    WorldState,
    validate_commitments,
    validate_trajectory,
    validate_world_state_references,
)


def extract_trajectory(outline: str) -> list[TrajectoryNode]:
    """Stage 1: outline -> an ordered list of TrajectoryNode. Contract #1 in pipeline-prompts.md."""
    prompt = f"""You are constructing a test scenario for a tabletop-style RPG's AI game master.

Given the campaign outline below, produce an ordered trajectory of plot nodes, as a JSON array.
Each node object must have exactly these fields:
- "node_id": a short unique string identifier (e.g. "n0", "n1", ...)
- "trigger_event": a plain-language description of what happens at this node
- "key_delta": the observable, world-state-level change this node causes -- not a private
  thought or feeling, something that could in principle be checked or verified
- "pov_note": what the player-character could plausibly know at or after this node -- do not
  describe anything the player-character couldn't witness or be told
- "sequence_index": an integer starting at 0, incrementing by 1 for each node in order, no gaps
- "references": a JSON array of short dotted state-key strings this node's key_delta affects,
  using the form "resources.<name>", "possessions.<name>", "status_flags.<name>", "position",
  or "character_resource" (use sensible short snake_case names; every node needs at least one)

Produce between 5 and 10 nodes total. Output ONLY the JSON array, no other text, no markdown
code fences.

Campaign outline:
{outline}
"""
    data = call_json(prompt)
    nodes = [TrajectoryNode.from_dict(n) for n in data]
    errors = validate_trajectory(nodes)
    if errors:
        raise ValueError(f"Generated trajectory failed validation: {errors}")
    return nodes


def extract_commitments(outline: str, trajectory: list[TrajectoryNode]) -> list[Commitment]:
    """Stage 2: outline + trajectory -> a list of Commitment. Contract #2 in pipeline-prompts.md."""
    trajectory_json = json.dumps([n.to_dict() for n in trajectory], indent=2)
    prompt = f"""You are constructing a test scenario for a tabletop-style RPG's AI game master.

Given the campaign outline and its trajectory of plot nodes below, produce a JSON array of
commitments -- rules the story's narration must not violate as it plays out. Each commitment
object must have exactly these fields:
- "commitment_id": a short unique string identifier (e.g. "c0", "c1", ...)
- "type": one of "invariant" (must hold true throughout, e.g. a character stays alive unless
  explicitly killed), "ordering" (one thing must happen before another), or "achievement"
  (a specific goal state must eventually be reached)
- "description": a plain-language statement of the commitment
- "satisfaction_condition": an explicit, fact-based condition for this commitment being met --
  must be directly checkable against world state, not a matter of interpretation
- "violation_condition": an explicit, fact-based condition for this commitment being broken
- "anchor_node_id": the node_id (from the trajectory below) this commitment is conditioned on
- "references": a JSON array of dotted state-key strings (same format as trajectory nodes)
  this commitment's conditions depend on

Do NOT create commitments about static background facts (names, occupations, appearance) --
only about things that can actually change and be violated during play. Produce between 3 and
8 commitments. Output ONLY the JSON array, no other text, no markdown code fences.

Campaign outline:
{outline}

Trajectory:
{trajectory_json}
"""
    data = call_json(prompt)
    commitments = [Commitment.from_dict(c) for c in data]
    errors = validate_commitments(commitments, trajectory)
    if errors:
        raise ValueError(f"Generated commitments failed validation: {errors}")
    return commitments


def extract_initial_facts(
    outline: str, trajectory: list[TrajectoryNode], commitments: list[Commitment]
) -> WorldState:
    """Stage 3: outline + trajectory + commitments -> the seeded WorldState at sequence_index 0.
    Contract #3 in pipeline-prompts.md. Enforces the T=0 Absolute Isolation Principle in the
    prompt itself; check_isolation (T007) is the independent verification of that requirement.
    """
    trajectory_json = json.dumps([n.to_dict() for n in trajectory], indent=2)
    commitments_json = json.dumps([c.to_dict() for c in commitments], indent=2)
    prompt = f"""You are constructing a test scenario for a tabletop-style RPG's AI game master.

Given the campaign outline, trajectory, and commitments below, produce the STARTING world
state -- the state of the world at sequence_index 0, BEFORE any trajectory node has triggered.

CRITICAL RULE (the "T=0 Absolute Isolation Principle"): this starting state must not know
about or reflect anything that only becomes true once a later trajectory node fires. For any
state key referenced by a node with sequence_index > 0, the starting value must be the
PRE-node value (e.g. if a later node unlocks a door, status_flags for that door must start
as locked, not unlocked). If a fact is genuinely unknown to the player-character at the
start, POSITIVELY assert that (e.g. "identity_of_traitor_known": false) rather than omitting
the key entirely.

Output a single JSON object with exactly these fields:
- "character": {{"name": <string>, "resource_name": <string>, "resource_current": <int>, "resource_max": <int>}}
- "resources": an object mapping resource names (matching any "resources.<name>" references
  above) to {{"current": <int>, "max": <int>}}
- "possessions": an object mapping possession names (matching any "possessions.<name>"
  references above) to true/false
- "position": a short string describing the starting location
- "status_flags": an object mapping status names (matching any "status_flags.<name>"
  references above) to true/false or a short string

Every key referenced anywhere in the trajectory or commitments below MUST appear in the
appropriate section here, with a pre-node-trigger value. Output ONLY the JSON object, no
other text, no markdown code fences.

Campaign outline:
{outline}

Trajectory:
{trajectory_json}

Commitments:
{commitments_json}
"""
    data = call_json(prompt)
    world_state = WorldState.from_dict(data)
    errors = validate_world_state_references(world_state, trajectory, commitments)
    if errors:
        raise ValueError(f"Generated initial facts failed validation: {errors}")
    return world_state


def check_isolation(trajectory: list[TrajectoryNode], world_state: WorldState) -> dict:
    """T007: semantic isolation check. Contract #4 in pipeline-prompts.md.

    This is deliberately a separate, independent call from extract_initial_facts -- asking
    the same call that just generated the state whether its own output is correct would be
    a weaker check than a fresh pass specifically tasked with finding violations.
    """
    trajectory_json = json.dumps([n.to_dict() for n in trajectory], indent=2)
    world_state_json = json.dumps(world_state.to_dict(), indent=2)
    prompt = f"""Below is a trajectory of plot nodes (in order, starting at sequence_index 0)
and a proposed STARTING world state, meant to represent the state BEFORE any node has
triggered.

Check whether the starting world state leaks any knowledge of what happens at
sequence_index >= 1 or later -- does any fact in the starting state already reflect a change
that a later node's key_delta describes, or reveal information a node's pov_note says should
only become known later?

Output a single JSON object with exactly these fields:
- "isolated": true if no such leak exists, false if at least one does
- "violations": a JSON array of objects, each with "fact" (the leaking fact/value) and
  "leaked_from_node" (the node_id it should not yet reflect) -- empty array if isolated is true

Output ONLY the JSON object, no other text, no markdown code fences.

Trajectory:
{trajectory_json}

Starting world state:
{world_state_json}
"""
    return call_json(prompt)
