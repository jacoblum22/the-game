"""Live probe harness for feature 003 (T012/T014/T015).

Not a pytest unit test (tests/unit/test_ability_pool.py covers the deterministic mechanism
itself) -- this makes real, billed API calls, one independent turn per scripted scenario, per
quickstart.md. Each scenario is deliberately a single, isolated turn (a fresh conversation, a
fresh WorldState) rather than a continuous session -- this probe is testing whether the DM
correctly maps a narrated event onto grant_ability's fixed archetype/method categories, not
long-horizon consistency (that's Feature 002's job).

Built incrementally per tasks.md:
- T012 (US2): drives each scripted scenario through the real tool-calling loop, reports
  whether grant_ability was called with the archetype/method the scenario was designed to
  imply.
- T013-T015 (US3): extends the report with the auditor's narration/grant consistency check,
  broken out by source archetype and acquisition method (SC-002/SC-003).
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

from ability_acquisition_scenarios import SCENARIOS, AcquisitionScenario  # noqa: E402
from auditor import check_turn  # noqa: E402
from dm_agent import SYSTEM_PROMPT, build_client, run_turn  # noqa: E402
from state import CharacterState  # noqa: E402
from tools import TOOL_SCHEMAS  # noqa: E402
from world_state import EXTRA_TOOL_SCHEMAS, WorldState, WorldStateToolHandlers  # noqa: E402

COMBINED_TOOL_SCHEMAS = TOOL_SCHEMAS + EXTRA_TOOL_SCHEMAS


def log(scenario_name: str, message: str) -> None:
    """Timestamped, flushed progress line -- same rationale as run_long_horizon_test.py's
    log(): stdout is fully buffered when redirected to a file, so flush=True is load-bearing,
    not decorative."""
    print(f"[{time.strftime('%H:%M:%S')}] [{scenario_name}] {message}", flush=True)


ABILITY_PROBE_SYSTEM_PROMPT = f"""{SYSTEM_PROMPT}

## Additional tool for this session
Beyond roll_check/get_state/update_state, you also have grant_ability(source_archetype,
acquisition_method, reason). Call it whenever the player's action describes defeating,
surviving, or otherwise acquiring something from a source belonging to one of these fixed
archetypes: "beast", "elemental_fire", "undead", "construct". You choose source_archetype and
acquisition_method ("decisive_kill" for a clean, decisive kill; "narrow_survival" for barely
surviving a costly, dangerous encounter; "non_lethal_subdual" for disabling or subduing
something without destroying it) based on what the narration actually describes -- you do NOT
choose which specific ability results; that is computed for you and returned. Your narration of
the outcome must match what the tool returns, not invent a different effect.
"""


def run_one_scenario(scenario: AcquisitionScenario) -> dict:
    """Runs one scripted scenario as a single isolated turn. Returns a result dict covering
    both US2 (was grant_ability called with the right archetype/method) and US3 (did the
    narration match what was granted)."""
    world_state = WorldState(character=CharacterState("Kess", "Vitality", 10, 10))
    handlers = WorldStateToolHandlers(world_state)
    handlers.current_turn = 1
    client = build_client()
    conversation: list = []

    action = f"{scenario.context} {scenario.action}"
    state_before = world_state.to_dict()
    result = run_turn(
        client, handlers, conversation, action,
        max_tool_iterations=5,
        tool_schemas=COMBINED_TOOL_SCHEMAS,
        system_prompt=ABILITY_PROBE_SYSTEM_PROMPT,
    )

    log(scenario.name, f"Narration: {result.narration[:150]}...")
    for call in result.tool_calls:
        log(scenario.name, f"    tool_call: {call['name']}({call['input']}) -> {call['result']}")

    grant_calls = [c for c in result.tool_calls if c["name"] == "grant_ability"]
    tool_called_correctly = False
    actual_archetype = None
    actual_method = None
    if grant_calls:
        call = grant_calls[0]
        actual_archetype = call["input"].get("source_archetype")
        actual_method = call["input"].get("acquisition_method")
        tool_called_correctly = (
            actual_archetype == scenario.expected_source_archetype
            and actual_method == scenario.expected_acquisition_method
        )

    conflict = None
    if world_state.ability_grants:
        grant = world_state.ability_grants[-1]
        conflict = check_turn(
            1, result.narration, action, world_state, [],
            state_before=state_before, ability_grant=grant,
        )

    log(
        scenario.name,
        f"grant_ability called: {bool(grant_calls)}, correct archetype/method: "
        f"{tool_called_correctly}, narration conflict: {conflict is not None}",
    )

    return {
        "scenario": scenario.name,
        "expected_source_archetype": scenario.expected_source_archetype,
        "expected_acquisition_method": scenario.expected_acquisition_method,
        "grant_ability_called": bool(grant_calls),
        "actual_source_archetype": actual_archetype,
        "actual_acquisition_method": actual_method,
        "tool_called_correctly": tool_called_correctly,
        "conflict": conflict.description if conflict else None,
    }


def print_report(results: list[dict]) -> None:
    total = len(results)
    correct = sum(1 for r in results if r["tool_called_correctly"])
    conflicts = [r for r in results if r["conflict"]]

    print(f"\nTotal scenarios: {total}")
    print(f"grant_ability called with correct archetype/method: {correct}/{total}")
    print(f"Narration/grant conflicts detected: {len(conflicts)}/{total}")

    print("\nPer-scenario detail:")
    for r in results:
        print(
            f"  {r['scenario']}: called={r['grant_ability_called']} "
            f"expected=({r['expected_source_archetype']}, {r['expected_acquisition_method']}) "
            f"actual=({r['actual_source_archetype']}, {r['actual_acquisition_method']}) "
            f"correct={r['tool_called_correctly']} conflict={r['conflict']}"
        )

    print("\nBreakdown by source archetype:")
    for archetype in {r["expected_source_archetype"] for r in results}:
        subset = [r for r in results if r["expected_source_archetype"] == archetype]
        subset_correct = sum(1 for r in subset if r["tool_called_correctly"])
        subset_conflicts = sum(1 for r in subset if r["conflict"])
        print(f"  {archetype}: {subset_correct}/{len(subset)} correct, {subset_conflicts}/{len(subset)} conflicts")

    print("\nBreakdown by acquisition method:")
    for method in {r["expected_acquisition_method"] for r in results}:
        subset = [r for r in results if r["expected_acquisition_method"] == method]
        subset_correct = sum(1 for r in subset if r["tool_called_correctly"])
        subset_conflicts = sum(1 for r in subset if r["conflict"])
        print(f"  {method}: {subset_correct}/{len(subset)} correct, {subset_conflicts}/{len(subset)} conflicts")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ability acquisition probe")
    parser.add_argument(
        "--scenarios", type=int, default=None,
        help="Run only the first N scripted scenarios (default: all)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    scenarios = SCENARIOS[: args.scenarios] if args.scenarios else SCENARIOS

    results = []
    for scenario in scenarios:
        results.append(run_one_scenario(scenario))

    print("=" * 60)
    print_report(results)

    sys.exit(0 if all(r["tool_called_correctly"] and not r["conflict"] for r in results) else 1)
