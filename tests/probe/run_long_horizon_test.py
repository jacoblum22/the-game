"""Long-horizon consistency stress test harness for feature 002.

Not a pytest unit test (tests/unit/ covers the pure structural parts) -- this makes real,
billed API calls. Run manually per quickstart.md. Built incrementally per tasks.md:
- T012 (US1): scenario-only verification -- runs generate_scenario against all 3 campaign
  outlines and reports isolation-check pass/fail for each, satisfying SC-001.
- T013-T015 (US2): the real turn-by-turn session loop, termination logic, and CLI args.
- T016-T018 (US3): the aggregate, category-resolved report.

Known simplification (documented, not hidden): termination_reason only ever reports "conflict"
or "turn_cap_reached" in this implementation -- reliably detecting a "natural story ending"
(e.g. character death, quest completion) as a THIRD distinct outcome would need its own
detection mechanism, which this feature's scope didn't extend to. Similarly, `succeeded` checks
achievement-commitment status, but the auditor (auditor.check_turn) only ever detects
VIOLATIONS, not satisfactions -- so in practice `succeeded` behaves as roughly synonymous with
`survived` unless a scenario happens to have zero achievement commitments. Both are honest,
scoped-down starting points, not claimed as fully solved.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

from auditor import check_turn  # noqa: E402
from campaign_outlines import OUTLINES  # noqa: E402
from dm_agent import SYSTEM_PROMPT, build_client, run_turn  # noqa: E402
from player_agent import next_action  # noqa: E402
from scenario_pipeline import IsolationViolationError, generate_scenario  # noqa: E402
from tools import TOOL_SCHEMAS  # noqa: E402
from world_state import (  # noqa: E402
    EXTRA_TOOL_SCHEMAS,
    Commitment,
    SessionOutcome,
    TrajectoryNode,
    WorldState,
    WorldStateToolHandlers,
)

COMBINED_TOOL_SCHEMAS = TOOL_SCHEMAS + EXTRA_TOOL_SCHEMAS


def run_scenario_checks() -> bool:
    """T012: SC-001 -- generate a scenario for all 3 outlines, report isolation pass/fail."""
    all_passed = True

    for name, outline in OUTLINES.items():
        print(f"--- Scenario: {name}")
        try:
            trajectory, commitments, world_state = generate_scenario(outline)
        except IsolationViolationError as exc:
            print(f"    FAIL (isolation): {exc}")
            all_passed = False
            continue
        except ValueError as exc:
            print(f"    FAIL (structural validation): {exc}")
            all_passed = False
            continue

        print(f"    PASS: {len(trajectory)} trajectory nodes, {len(commitments)} commitments")
        print(f"    Starting position: {world_state.position!r}")
        print(
            f"    Seeded categories: resources={list(world_state.resources)}, "
            f"possessions={list(world_state.possessions)}, "
            f"status_flags={list(world_state.status_flags)}"
        )
        print()

    return all_passed


def build_dm_system_prompt(trajectory: list[TrajectoryNode], commitments: list[Commitment]) -> str:
    """Extends Feature 001's base SYSTEM_PROMPT with this session's prep notes -- the DM (like
    a real GM) knows the planned trajectory and commitments; the player persona does not
    (contract #5's "plays as the character, doesn't see the answer key")."""
    trajectory_json = json.dumps([n.to_dict() for n in trajectory], indent=2)
    commitments_json = json.dumps([c.to_dict() for c in commitments], indent=2)
    return f"""{SYSTEM_PROMPT}

## Additional tools for this session
Beyond roll_check/get_state/update_state, you also have:
- update_resource(name, delta, reason): for named resources in get_state's `resources` dict
  (not your one primary character resource -- keep using update_state for that).
- set_fact(category, key, value, reason): for possessions/status_flags/position facts.
  `value` is always a string ("true"/"false" for booleans).
Call get_state to see ALL current facts whenever they might matter, not just before rolls.

## This session's planned trajectory (your own prep notes -- the player does not see this)
Use this to guide the story naturally as the player's actions bring events about. Do not
force an event that doesn't fit what the player actually did, and do not reveal anything a
node's pov_note says the player-character shouldn't know yet:
{trajectory_json}

## Active commitments -- rules your own narration must never violate
{commitments_json}
"""


def render_visible_history(visible_turns: list[tuple[str, str]]) -> str:
    """Plain-text rendering for player_agent.next_action -- narration and past player actions
    only, never raw tool-call internals, matching the "sees only visible history" constraint."""
    lines = []
    for action, narration in visible_turns:
        lines.append(f"Player: {action}")
        lines.append(f"DM: {narration}")
    return "\n".join(lines)


def run_session(
    trajectory: list[TrajectoryNode],
    commitments: list[Commitment],
    world_state: WorldState,
    persona_mode: str,
    turn_cap: int,
    run_id: str,
    checkpoint_interval: int = 5,
) -> SessionOutcome:
    """T013/T014: drives real turns via Feature 001's unmodified run_turn(), checking each via
    the auditor, until a conflict is found or the turn cap is reached."""
    handlers = WorldStateToolHandlers(world_state)
    system_prompt = build_dm_system_prompt(trajectory, commitments)
    client = build_client()

    conversation: list = []
    visible_turns: list[tuple[str, str]] = []
    conflicts = []
    checkpoints = []
    termination_reason = "turn_cap_reached"
    turn_of_first_conflict = None
    turns_completed = 0

    opening = run_turn(
        client,
        handlers,
        conversation,
        "Begin the session: narrate a brief opening scene consistent with the seeded world "
        "state and invite the player's first action.",
        tool_schemas=COMBINED_TOOL_SCHEMAS,
        system_prompt=system_prompt,
    )
    visible_turns.append(("(session start)", opening.narration))
    print(f"[{run_id}] Opening: {opening.narration[:150]}...")

    for turn_number in range(1, turn_cap + 1):
        history_text = render_visible_history(visible_turns)
        action = next_action(history_text, persona_mode)
        result = run_turn(
            client, handlers, conversation, action,
            tool_schemas=COMBINED_TOOL_SCHEMAS, system_prompt=system_prompt,
        )
        visible_turns.append((action, result.narration))
        turns_completed = turn_number

        conflict = check_turn(turn_number, result.narration, action, world_state, commitments)
        print(
            f"[{run_id}] Turn {turn_number}: {action[:60]!r} -> "
            f"{'CONFLICT: ' + conflict.description[:80] if conflict else 'ok'}"
        )

        if conflict:
            conflicts.append(conflict)
            turn_of_first_conflict = turn_number
            termination_reason = "conflict"
            checkpoints.append(
                {"turn_number": turn_number, "survived_so_far": False, "conflict_count_so_far": len(conflicts)}
            )
            break

        if turn_number % checkpoint_interval == 0:
            checkpoints.append(
                {"turn_number": turn_number, "survived_so_far": True, "conflict_count_so_far": len(conflicts)}
            )

    if not checkpoints or checkpoints[-1]["turn_number"] != turns_completed:
        checkpoints.append(
            {"turn_number": turns_completed, "survived_so_far": termination_reason != "conflict", "conflict_count_so_far": len(conflicts)}
        )

    survived = termination_reason != "conflict"
    achievement_commitments = [c for c in commitments if c.type == "achievement"]
    succeeded = survived and all(c.status == "satisfied" for c in achievement_commitments)

    return SessionOutcome(
        run_id=run_id,
        persona_condition=persona_mode,
        turns_completed=turns_completed,
        termination_reason=termination_reason,
        survived=survived,
        succeeded=succeeded,
        turn_of_first_conflict=turn_of_first_conflict,
        conflicts=conflicts,
        checkpoints=checkpoints,
    )


def parse_args() -> argparse.Namespace:
    """T015: CLI args per quickstart.md's Step 2/3 usage."""
    parser = argparse.ArgumentParser(description="Long-horizon consistency stress test")
    parser.add_argument("--scenarios-only", action="store_true", help="Run only T012's SC-001 check, no sessions")
    parser.add_argument("--turns", type=int, default=15, help="Turn cap per session (default: 15, the small validation case)")
    parser.add_argument("--runs", type=int, default=1, help="Number of scenarios to run sessions for (default: 1)")
    parser.add_argument(
        "--personas", type=str, default="natural",
        help="Comma-separated persona modes to run per scenario, e.g. 'adversarial,natural' (default: natural)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    scenario_ok = run_scenario_checks()
    print("=" * 60)
    print("SC-001 result:", "PASS -- all scenarios isolated" if scenario_ok else "FAIL -- see above")

    if args.scenarios_only or not scenario_ok:
        sys.exit(0 if scenario_ok else 1)

    personas = [p.strip() for p in args.personas.split(",") if p.strip()]
    outline_items = list(OUTLINES.items())[: args.runs]

    outcomes: list[SessionOutcome] = []
    for name, outline in outline_items:
        trajectory, commitments, world_state = generate_scenario(outline)
        for persona in personas:
            run_id = f"{name}-{persona}"
            outcome = run_session(trajectory, commitments, world_state, persona, args.turns, run_id)
            outcomes.append(outcome)
            outcome.save(Path(f"{run_id}.scenario.json"))

    print("=" * 60)
    print(f"Completed {len(outcomes)} run(s). See T016-T018 for aggregate reporting.")
