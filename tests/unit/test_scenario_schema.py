"""Unit tests for src/world_state.py's structural validators (feature 002, T004).

Pure structural checks only -- no network calls, no semantic content judgment (that's
scenario_pipeline.check_isolation's job, exercised live, not here). Covers both valid cases
and each failure mode per tasks.md T004.
"""

from state import CharacterState
from world_state import (
    Commitment,
    TrajectoryNode,
    WorldState,
    validate_commitments,
    validate_trajectory,
    validate_world_state_references,
)


def make_node(node_id, sequence_index, references=None):
    return TrajectoryNode(
        node_id=node_id,
        trigger_event="something happens",
        key_delta="something changes",
        pov_note="player can see it",
        sequence_index=sequence_index,
        references=references or [],
    )


def make_commitment(commitment_id, anchor_node_id, commitment_type="invariant", references=None):
    return Commitment(
        commitment_id=commitment_id,
        type=commitment_type,
        description="a rule",
        satisfaction_condition="condition met",
        violation_condition="condition broken",
        anchor_node_id=anchor_node_id,
        references=references or [],
    )


def make_world_state(**kwargs):
    return WorldState(character=CharacterState("Kess", "Vitality", 12, 12), **kwargs)


# --- validate_trajectory ---


def test_valid_trajectory_passes():
    nodes = [make_node("n0", 0), make_node("n1", 1), make_node("n2", 2)]
    assert validate_trajectory(nodes) == []


def test_duplicate_node_id_fails():
    nodes = [make_node("n0", 0), make_node("n0", 1)]
    errors = validate_trajectory(nodes)
    assert len(errors) == 1
    assert "Duplicate node_id" in errors[0]


def test_sequence_index_gap_fails():
    nodes = [make_node("n0", 0), make_node("n1", 2)]  # gap at index 1
    errors = validate_trajectory(nodes)
    assert len(errors) == 1
    assert "gapless" in errors[0]


def test_sequence_index_duplicate_fails():
    nodes = [make_node("n0", 0), make_node("n1", 0)]
    errors = validate_trajectory(nodes)
    assert len(errors) == 1


# --- validate_commitments ---


def test_valid_commitments_pass():
    nodes = [make_node("n0", 0)]
    commitments = [make_commitment("c0", "n0")]
    assert validate_commitments(commitments, nodes) == []


def test_duplicate_commitment_id_fails():
    nodes = [make_node("n0", 0)]
    commitments = [make_commitment("c0", "n0"), make_commitment("c0", "n0")]
    errors = validate_commitments(commitments, nodes)
    assert any("Duplicate commitment_id" in e for e in errors)


def test_bad_anchor_node_id_fails():
    nodes = [make_node("n0", 0)]
    commitments = [make_commitment("c0", "nonexistent")]
    errors = validate_commitments(commitments, nodes)
    assert any("does not match any trajectory node" in e for e in errors)


def test_invalid_commitment_type_fails():
    nodes = [make_node("n0", 0)]
    commitments = [make_commitment("c0", "n0", commitment_type="not_a_real_type")]
    errors = validate_commitments(commitments, nodes)
    assert any("invalid type" in e for e in errors)


# --- validate_world_state_references ---


def test_valid_references_pass():
    nodes = [make_node("n0", 0, references=["status_flags.door_locked"])]
    commitments = [make_commitment("c0", "n0", references=["resources.stamina"])]
    ws = make_world_state(
        status_flags={"door_locked": True}, resources={"stamina": {"current": 5, "max": 10}}
    )
    assert validate_world_state_references(ws, nodes, commitments) == []


def test_orphaned_trajectory_reference_fails():
    nodes = [make_node("n0", 0, references=["status_flags.nonexistent_flag"])]
    ws = make_world_state()
    errors = validate_world_state_references(ws, nodes, [])
    assert any("references unknown key" in e for e in errors)


def test_orphaned_commitment_reference_fails():
    nodes = [make_node("n0", 0)]
    commitments = [make_commitment("c0", "n0", references=["possessions.nonexistent_item"])]
    ws = make_world_state()
    errors = validate_world_state_references(ws, nodes, commitments)
    assert any("references unknown key" in e for e in errors)


def test_bare_position_and_character_resource_always_valid():
    nodes = [make_node("n0", 0, references=["position", "character_resource"])]
    ws = make_world_state()
    assert validate_world_state_references(ws, nodes, []) == []
