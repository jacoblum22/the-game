"""Three-stage synthetic scenario construction pipeline (feature 002, T006/T007).

Adapts NCP-Bench's construction approach (trajectory -> commitments -> initial facts, each
stage conditioned on the prior one) rather than inventing a new method -- see research.md's
decision for why. Prompts here are our own wording, not copied from NCP-Bench's published
templates, but follow the same structure and enforce the same T=0 Absolute Isolation
Principle. Each extraction function validates its own output immediately (T003's validators)
and raises on failure rather than returning malformed data -- per contracts/pipeline-prompts.md.

generate_scenario() (T010, User Story 1) orchestrates all four stages into one call, at the
bottom of this file.
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


def extract_state_at_cutoff(
    outline: str,
    trajectory: list[TrajectoryNode],
    commitments: list[Commitment],
    cutoff_index: int = -1,
) -> WorldState:
    """Generalizes the original t=0 seed extraction to an arbitrary cutoff point: the WorldState
    immediately AFTER the node with sequence_index == cutoff_index has fired, and BEFORE any
    node with a higher sequence_index has fired. cutoff_index=-1 (the default) means "before any
    node," i.e. the original t=0 case -- extract_initial_facts is a thin wrapper over this with
    that default, so its existing callers and contract are unchanged.

    Added for the fast-forward seeding capability (see generate_fast_forward_scenario): rather
    than always running every turn live from t=0, a session can be seeded partway through its
    trajectory -- for a fraction of the API cost of playing the earlier turns out for real --
    while keeping the SAME isolation discipline this pipeline already enforces at t=0, just
    relative to cutoff_index instead of always 0.
    """
    if cutoff_index < 0:
        cutoff_description = "at sequence_index 0, BEFORE any trajectory node has triggered"
        isolation_rule = (
            'CRITICAL RULE (the "T=0 Absolute Isolation Principle"): this starting state must '
            "not know about or reflect anything that only becomes true once a later trajectory "
            "node fires. For any state key referenced by a node with sequence_index > 0, the "
            "starting value must be the PRE-node value (e.g. if a later node unlocks a door, "
            "status_flags for that door must start as locked, not unlocked)."
        )
    else:
        cutoff_description = (
            f"immediately AFTER the trajectory node with sequence_index {cutoff_index} has "
            f"triggered, and BEFORE any node with a higher sequence_index has triggered"
        )
        isolation_rule = (
            'CRITICAL RULE (the same "Absolute Isolation Principle" as the t=0 case, applied '
            f"at this later cutoff): this state must fully reflect everything nodes with "
            f"sequence_index 0 through {cutoff_index} (inclusive) have already caused, but must "
            f"not know about or reflect anything that only becomes true once a node with "
            f"sequence_index > {cutoff_index} fires. For any state key referenced by such a "
            "later node, the value here must still be the PRE-that-node value."
        )
    trajectory_json = json.dumps([n.to_dict() for n in trajectory], indent=2)
    commitments_json = json.dumps([c.to_dict() for c in commitments], indent=2)
    prompt = f"""You are constructing a test scenario for a tabletop-style RPG's AI game master.

Given the campaign outline, trajectory, and commitments below, produce the world state
{cutoff_description}.

{isolation_rule} If a fact is genuinely unknown to the player-character at this point,
POSITIVELY assert that (e.g. "identity_of_traitor_known": false) rather than omitting the key
entirely.

Output a single JSON object with exactly these fields:
- "character": {{"name": <string>, "resource_name": <string>, "resource_current": <int>, "resource_max": <int>}}
- "resources": an object mapping resource names (matching any "resources.<name>" references
  above) to {{"current": <int>, "max": <int>}} -- MUST NOT include a key equal to
  "character.resource_name" above; that resource is tracked separately in "character" and
  reusing its name here would create two ambiguous, separately-tracked slots for the same thing
- "possessions": an object mapping possession names (matching any "possessions.<name>"
  references above) to true/false
- "position": a short string describing the current location
- "status_flags": an object mapping status names (matching any "status_flags.<name>"
  references above) to true/false or a short string

Every key referenced anywhere in the trajectory or commitments below MUST appear in the
appropriate section here, with a value correct as of this cutoff point. Output ONLY the JSON
object, no other text, no markdown code fences.

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
        raise ValueError(f"Generated state-at-cutoff failed validation: {errors}")
    return world_state


def extract_initial_facts(
    outline: str, trajectory: list[TrajectoryNode], commitments: list[Commitment]
) -> WorldState:
    """Stage 3: outline + trajectory + commitments -> the seeded WorldState at sequence_index 0.
    Contract #3 in pipeline-prompts.md. Enforces the T=0 Absolute Isolation Principle in the
    prompt itself; check_isolation (T007) is the independent verification of that requirement.
    Thin wrapper over extract_state_at_cutoff's default (cutoff_index=-1) -- see its docstring.
    """
    return extract_state_at_cutoff(outline, trajectory, commitments, cutoff_index=-1)


def check_isolation(
    trajectory: list[TrajectoryNode], world_state: WorldState, cutoff_index: int = -1
) -> dict:
    """T007: semantic isolation check. Contract #4 in pipeline-prompts.md.

    This is deliberately a separate, independent call from extract_state_at_cutoff -- asking
    the same call that just generated the state whether its own output is correct would be
    a weaker check than a fresh pass specifically tasked with finding violations.

    `cutoff_index` generalizes this the same way extract_state_at_cutoff is generalized: -1
    (the default) is the original t=0 case; a non-negative value checks for leakage from nodes
    with sequence_index > cutoff_index instead of always > 0.
    """
    if cutoff_index < 0:
        state_description = "a proposed STARTING world state, meant to represent the state BEFORE any node has triggered"
        leak_threshold = "sequence_index >= 1"
    else:
        state_description = (
            f"a proposed world state, meant to represent the state immediately AFTER the node "
            f"with sequence_index {cutoff_index} but BEFORE any later node"
        )
        leak_threshold = f"sequence_index > {cutoff_index}"
    trajectory_json = json.dumps([n.to_dict() for n in trajectory], indent=2)
    world_state_json = json.dumps(world_state.to_dict(), indent=2)
    prompt = f"""Below is a trajectory of plot nodes (in order, starting at sequence_index 0)
and {state_description}.

Check whether this world state leaks any knowledge of what happens at {leak_threshold} --
does any fact already reflect a change that a later node's key_delta describes, or reveal
information a node's pov_note says should only become known later?

Output a single JSON object with exactly these fields:
- "isolated": true if no such leak exists, false if at least one does
- "violations": a JSON array of objects, each with "fact" (the leaking fact/value) and
  "leaked_from_node" (the node_id it should not yet reflect) -- empty array if isolated is true

Output ONLY the JSON object, no other text, no markdown code fences.

Trajectory:
{trajectory_json}

World state:
{world_state_json}
"""
    return call_json(prompt)


def generate_synthetic_transcript(
    outline: str,
    trajectory: list[TrajectoryNode],
    commitments: list[Commitment],
    cutoff_index: int,
    target_turn_count: int = 30,
    chunk_size: int = 10,
) -> list[tuple[str, str]]:
    """Generates a full alternating (player_action, dm_narration) transcript covering trajectory
    nodes with sequence_index <= cutoff_index, granular enough to total roughly
    target_turn_count turns -- not one turn per major plot beat, but the ordinary
    investigative/exploratory/conversational turns a real session would have BETWEEN beats too.

    This replaces an earlier, weaker design (a short prose "recap") that only ever produced a
    handful of summary sentences with no real bulk -- which doesn't actually test what
    long-horizon consistency is about: does a genuinely LARGE volume of accumulated turn content
    in the model's context cause degradation, not just "can it follow an accurate summary."
    Splicing this transcript directly into the real conversation history (as the harness does)
    gives the model an actual large context to contend with, at the cost of a handful of big
    generation calls instead of dozens of live sequential turns.

    Generated in chunks (chunk_size turns per call, passing the transcript-so-far forward for
    continuity) rather than one shot, to keep each individual completion's length and quality
    manageable -- asking for ~30 turns of rich content in a single completion risks truncation
    or degrading coherence toward the end.
    """
    covered_nodes = [n for n in trajectory if n.sequence_index <= cutoff_index]
    covered_json = json.dumps([n.to_dict() for n in covered_nodes], indent=2)

    transcript: list[tuple[str, str]] = []
    remaining = target_turn_count
    while remaining > 0:
        this_chunk = min(chunk_size, remaining)
        transcript_so_far = (
            json.dumps(
                [{"player_action": a, "dm_narration": d} for a, d in transcript], indent=2
            )
            if transcript
            else "(nothing yet -- this is the start of the session)"
        )
        prompt = f"""You are writing a synthetic transcript of a tabletop-style RPG session, to
be used as test data. Write the NEXT {this_chunk} turns of a natural, granular player/DM
back-and-forth, as a JSON array of exactly {this_chunk} objects, each with a "player_action"
and a "dm_narration" string field.

The full transcript (across all chunks) must progress through, and only through, these plot
nodes -- but NOT one turn per node. Include ordinary investigative, exploratory, and
conversational turns between the major beats too, the way a real session actually plays out:
{covered_json}

Do not reveal or imply anything beyond the plot nodes listed above -- nothing past where this
transcript is meant to end. Output ONLY the JSON array, no other text, no markdown code fences.

Campaign outline:
{outline}

Transcript so far (continue naturally from here -- do not repeat any of it):
{transcript_so_far}
"""
        data = call_json(prompt)
        for item in data:
            transcript.append((item["player_action"], item["dm_narration"]))
        remaining -= this_chunk

    return transcript


def check_transcript(
    trajectory: list[TrajectoryNode],
    commitments: list[Commitment],
    transcript: list[tuple[str, str]],
    world_state_at_cutoff: WorldState,
    cutoff_index: int,
) -> dict:
    """Holistic verification pass over a full synthetic transcript, checking three things in
    one call before it's trusted as prior context for a real session:
    1. Isolation: nothing in the transcript reveals or implies knowledge of a trajectory node
       past cutoff_index (same discipline as check_isolation, applied to a full transcript
       instead of a single state snapshot).
    2. Internal inconsistency: does the transcript contradict itself -- narrating a fact as
       newly discovered after it was already established earlier in the SAME transcript, or an
       impossible/nonsensical sequence of events.
    3. State disagreement: extract_state_at_cutoff's output is generated independently of this
       transcript (a separate call) -- this checks they actually agree, e.g. an item the state
       says is possessed should be shown being acquired somewhere in the transcript, not just
       asserted with no corresponding event.
    4. Commitment violation: does the transcript violate any commitment's violation_condition
       (e.g. narrating a character's death when a commitment requires them to stay alive unless
       an explicit killing event occurs) -- checked here since a violated commitment is exactly
       the kind of "doesn't make sense" a synthetic transcript could otherwise slip past.
    """
    transcript_json = json.dumps(
        [{"player_action": a, "dm_narration": d} for a, d in transcript], indent=2
    )
    trajectory_json = json.dumps([n.to_dict() for n in trajectory], indent=2)
    commitments_json = json.dumps([c.to_dict() for c in commitments], indent=2)
    world_state_json = json.dumps(world_state_at_cutoff.to_dict(), indent=2)
    prompt = f"""Below is a synthetic transcript of a tabletop RPG session (player actions and
DM narration, in order), meant to represent turns that have ALREADY happened, up through (and
including) the trajectory node with sequence_index {cutoff_index} -- plus the commitments this
story must not violate and the world state that is supposed to result from the transcript.

Check for FOUR kinds of problem:
1. Isolation leak: does any line reveal or imply knowledge of a trajectory node with
   sequence_index > {cutoff_index} (something that has not happened yet)?
2. Internal inconsistency: does the transcript contradict itself -- e.g. narrating a fact as
   newly discovered after it was already established earlier in this same transcript, or an
   impossible/nonsensical sequence of events?
3. State disagreement: does the given world state disagree with what the transcript actually
   narrates -- e.g. the state shows an item as possessed but the transcript never shows it
   being acquired or found, or a resource's final value isn't a plausible result of what the
   transcript narrates happening to it?
4. Commitment violation: does any line in the transcript satisfy a commitment's
   violation_condition?

Output a single JSON object with exactly these fields:
- "valid": true only if NONE of the four problems above are found
- "issues": a JSON array of short strings describing each problem found (empty if valid is true)

Output ONLY the JSON object, no other text, no markdown code fences.

Trajectory:
{trajectory_json}

Commitments:
{commitments_json}

Transcript:
{transcript_json}

World state that should result from this transcript:
{world_state_json}
"""
    return call_json(prompt)


class IsolationViolationError(RuntimeError):
    """Raised when a generated scenario fails the isolation check and cannot be salvaged
    within the retry budget. Per spec.md's Edge Cases, an isolated=false scenario MUST be
    blocked from use -- this is that block."""


def generate_scenario(
    outline: str, max_isolation_retries: int = 2
) -> tuple[list[TrajectoryNode], list[Commitment], WorldState]:
    """T010 (User Story 1): orchestrates all four pipeline stages into one scenario.

    The trajectory and commitments are generated once; if the isolation check fails, only
    the initial-facts stage (the one actually responsible for isolation) is regenerated, up
    to `max_isolation_retries` times, rather than restarting the whole pipeline -- cheaper,
    and the trajectory/commitments aren't where an isolation leak originates.
    """
    trajectory = extract_trajectory(outline)
    commitments = extract_commitments(outline, trajectory)

    last_violations = None
    for attempt in range(max_isolation_retries + 1):
        world_state = extract_initial_facts(outline, trajectory, commitments)
        result = check_isolation(trajectory, world_state)
        if result.get("isolated"):
            return trajectory, commitments, world_state
        last_violations = result.get("violations")

    raise IsolationViolationError(
        f"Scenario failed isolation check after {max_isolation_retries + 1} attempts. "
        f"Last violations: {last_violations}"
    )


def generate_fast_forward_scenario(
    outline: str,
    cutoff_fraction: float,
    target_turn_count: int = 30,
    max_isolation_retries: int = 2,
) -> tuple[list[TrajectoryNode], list[Commitment], WorldState, list[tuple[str, str]], int]:
    """Like generate_scenario, but seeds the state partway through the trajectory instead of
    always at sequence_index 0, plus a full synthetic transcript of turns that already
    "happened" to get there -- so a real session only needs to play out the REMAINING
    trajectory nodes, not the whole thing, for a fraction of the API cost of running a long
    session live turn-by-turn from scratch, while still giving the model a genuinely large
    volume of prior context to contend with (not just a short summary of it).

    This is the project's own originally-proposed "synthetic recap + pre-populated state" idea
    (this feature's initial research brief), built directly on the SAME isolation-checked
    pipeline already used for the t=0 case rather than the unstructured "freehand recap"
    research.md's Decision log set aside -- the objection there was the lack of isolation
    discipline, not the fast-forward idea itself, and this keeps that discipline at an arbitrary
    cutoff instead of discarding it. An earlier version of this function generated a short
    prose recap instead of a full transcript; that was too thin to actually stress long-context
    behavior (a few summary sentences isn't the same volume as many turns of real content) and
    was replaced with generate_synthetic_transcript before this ever ran a real batch.

    Takes a FRACTION (0.0-1.0) rather than a raw node index: the cutoff can only be resolved to
    an actual index after the trajectory exists (trajectory length varies per generation), and
    generating the trajectory just to peek at its length, then generating it AGAIN inside a
    lower-level call, would double that call's cost and -- since generation is stochastic --
    silently use a DIFFERENT trajectory than the one actually reported. This function generates
    the trajectory exactly once and resolves the cutoff from it internally.

    Returns (trajectory, commitments, world_state_at_cutoff, transcript, cutoff_index) --
    trajectory and commitments are unchanged from the full-story versions (the DM's own "prep
    notes" still cover the whole planned story, same as generate_scenario); only the seeded
    state and the transcript are cutoff-specific. Both the state and the transcript are
    regenerated together on any validation failure (isolation OR internal inconsistency OR
    disagreement between them, per check_transcript), since they need to agree with each other.
    """
    if not (0.0 <= cutoff_fraction < 1.0):
        raise ValueError(f"cutoff_fraction must be in [0.0, 1.0), got {cutoff_fraction}")

    trajectory = extract_trajectory(outline)
    commitments = extract_commitments(outline, trajectory)
    if len(trajectory) < 2:
        raise ValueError(
            f"trajectory has only {len(trajectory)} node(s) -- need at least 2 to fast-forward "
            f"through part of it and still leave a real node for the live turns to play out"
        )
    cutoff_index = max(0, min(len(trajectory) - 2, round(cutoff_fraction * (len(trajectory) - 1))))

    last_issues = None
    for attempt in range(max_isolation_retries + 1):
        world_state = extract_state_at_cutoff(outline, trajectory, commitments, cutoff_index)
        state_check = check_isolation(trajectory, world_state, cutoff_index)
        if not state_check.get("isolated"):
            last_issues = state_check.get("violations")
            continue

        transcript = generate_synthetic_transcript(
            outline, trajectory, commitments, cutoff_index, target_turn_count
        )
        transcript_check = check_transcript(trajectory, commitments, transcript, world_state, cutoff_index)
        if transcript_check.get("valid"):
            return trajectory, commitments, world_state, transcript, cutoff_index
        last_issues = transcript_check.get("issues")

    raise IsolationViolationError(
        f"Fast-forward scenario (cutoff_index={cutoff_index}) failed validation after "
        f"{max_isolation_retries + 1} attempts. Last issues: {last_issues}"
    )
