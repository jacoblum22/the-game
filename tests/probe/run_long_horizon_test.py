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

Parallelized (added after the transcript-based fast-forward work): scenario generation and
session-running are both independent across (scenario, persona) pairs -- no shared mutable
state between them, each gets its own client and its own WorldState copy -- so both phases now
run concurrently via a thread pool (--workers, default 4) instead of sequentially. This is a
real change to the error-handling model, not just a speed change: previously, any single run's
exception aborted the WHOLE remaining batch (the "stopped_early" behavior). With concurrent
runs in flight at once, that no longer makes sense -- each run's failure is now caught and
reported individually (this run failed, here's why), and the batch keeps going regardless of
whether other runs succeeded or failed. All progress logging goes through log() below, which
timestamps and flushes every line -- Python fully buffers stdout by default when it isn't
attached to a real terminal (e.g. redirected to a file), which otherwise delays visibility into
progress until the buffer fills or the process exits entirely.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

from google.genai import types  # noqa: E402

from auditor import check_turn  # noqa: E402
from campaign_outlines import OUTLINES  # noqa: E402
from dm_agent import SYSTEM_PROMPT, build_client, run_turn  # noqa: E402
from player_agent import next_action  # noqa: E402
from scenario_pipeline import (  # noqa: E402
    IsolationViolationError,
    generate_fast_forward_scenario,
    generate_scenario,
)
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

# Found live during T021's first attempt: dm_agent.run_turn's default max_tool_iterations (5)
# was sized for Feature 001's 3-tool surface. Feature 002's 5 tools plus the system prompt's
# "call get_state liberally" instruction mean a single turn can legitimately need more
# round-trips (e.g. get_state, roll_check, update_resource, set_fact, THEN narration -- already
# 5 iterations before the final text reply). Scoped to this harness only, not Feature 001's
# shared default, per this project's additive-extension pattern.
MAX_TOOL_ITERATIONS = 10


def log(run_id: str, message: str) -> None:
    """Timestamped, immediately-flushed progress line. Safe to call from multiple threads --
    each call is a single print(), and CPython serializes individual print() calls (the GIL
    guards the underlying write), so concurrent runs' lines interleave whole, never mid-line.
    flush=True matters here specifically because stdout is fully buffered (not line-buffered)
    whenever it isn't attached to a real terminal -- e.g. redirected to a log file, as this
    harness always is per quickstart.md -- so without it, nothing would be visible until the
    buffer filled or the process exited, defeating the entire point of progress logging.
    """
    print(f"[{time.strftime('%H:%M:%S')}] [{run_id}] {message}", flush=True)


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
    (contract #5's "plays as the character, doesn't see the answer key").

    A fast-forwarded session (scenario_pipeline.generate_fast_forward_scenario) needs no special
    handling here -- its synthetic transcript is spliced directly into the real conversation
    history by run_session, so the DM sees it as ordinary prior turns, the same as it would see
    real prior turns in a non-fast-forwarded session. An earlier version of this function took
    a `recap` parameter injected as a system-prompt block instead; replaced because a short
    summary in the system prompt isn't the same thing as actual prior-turn volume in context.
    """
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
    transcript: list[tuple[str, str]] | None = None,
) -> SessionOutcome:
    """T013/T014: drives real turns via Feature 001's unmodified run_turn(), checking each via
    the auditor, until a conflict is found or the turn cap is reached.

    `transcript`: optional -- when set (a fast-forwarded session, see scenario_pipeline.
    generate_fast_forward_scenario), a list of (player_action, dm_narration) pairs spliced
    directly into `conversation` as real prior turns before any live turn runs, so the DM (and
    the player persona, via render_visible_history) see genuine accumulated context, not a
    summary of it. Defaults to None so the original from-scratch behavior is unchanged.
    """
    handlers = WorldStateToolHandlers(world_state)
    system_prompt = build_dm_system_prompt(trajectory, commitments)
    client = build_client()

    conversation: list = []
    visible_turns: list[tuple[str, str]] = []
    if transcript:
        for action, narration in transcript:
            conversation.append(types.Content(role="user", parts=[types.Part.from_text(text=action)]))
            conversation.append(types.Content(role="model", parts=[types.Part.from_text(text=narration)]))
            visible_turns.append((action, narration))
    conflicts = []
    checkpoints = []
    termination_reason = "turn_cap_reached"
    turn_of_first_conflict = None
    turns_completed = 0

    opening_instruction = (
        "Continue the session from where the transcript above leaves off: ground the player in "
        "the current moment with a brief scene (do not re-narrate anything already covered "
        "there), and invite their next action."
        if transcript
        else "Begin the session: narrate a brief opening scene consistent with the seeded "
        "world state and invite the player's first action."
    )
    opening = run_turn(
        client,
        handlers,
        conversation,
        opening_instruction,
        max_tool_iterations=MAX_TOOL_ITERATIONS,
        tool_schemas=COMBINED_TOOL_SCHEMAS,
        system_prompt=system_prompt,
    )
    visible_turns.append(("(session start)", opening.narration))
    log(run_id, f"Opening: {opening.narration[:150]}...")
    for call in opening.tool_calls:
        log(run_id, f"    tool_call: {call['name']}({call['input']}) -> {call['result']}")

    for turn_number in range(1, turn_cap + 1):
        history_text = render_visible_history(visible_turns)
        action = next_action(history_text, persona_mode)
        # Captured BEFORE run_turn's tool calls mutate world_state, so the auditor can tell
        # "already true before this action" apart from "became true because of it" -- see
        # auditor.check_turn's docstring for why this matters.
        state_before = world_state.to_dict()
        result = run_turn(
            client, handlers, conversation, action,
            max_tool_iterations=MAX_TOOL_ITERATIONS,
            tool_schemas=COMBINED_TOOL_SCHEMAS, system_prompt=system_prompt,
        )
        visible_turns.append((action, result.narration))
        turns_completed = turn_number

        conflict = check_turn(
            turn_number, result.narration, action, world_state, commitments,
            state_before=state_before,
        )
        log(
            run_id,
            f"Turn {turn_number}: {action[:60]!r} -> "
            f"{'CONFLICT: ' + conflict.description[:80] if conflict else 'ok'}",
        )
        # Diagnostic (added to verify the "narration lags its own tool call" hypothesis before
        # trusting it): print exactly what tools were called this turn, with what arguments and
        # what they returned, so a conflict can be checked against ground truth instead of only
        # the auditor's own English description of it.
        for call in result.tool_calls:
            log(run_id, f"    tool_call: {call['name']}({call['input']}) -> {call['result']}")

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


NCP_BENCH_BASELINE = {
    "fact_conflict_rate_range": "40-68% (among failing episodes, across 6 tested models)",
    "best_model_survival_at_turn_20": "42% (GPT-5.2, the best tested model)",
}


def build_report(outcomes: list[SessionOutcome]) -> dict:
    """T016: per-run and aggregate survival/success rates, turn-of-first-conflict (and its
    normalized position), and a conflict-type x state-category breakdown, per FR-008."""
    total = len(outcomes)
    survived_count = sum(1 for o in outcomes if o.survived)
    succeeded_count = sum(1 for o in outcomes if o.succeeded)

    type_category_counts: dict[str, int] = {}
    for o in outcomes:
        for c in o.conflicts:
            key = f"{c.conflict_type}/{c.state_category or 'n/a'}"
            type_category_counts[key] = type_category_counts.get(key, 0) + 1

    total_conflicts = sum(len(o.conflicts) for o in outcomes)
    fact_conflicts = sum(1 for o in outcomes for c in o.conflicts if c.conflict_type == "fact")

    per_run = []
    for o in outcomes:
        normalized = (
            round(o.turn_of_first_conflict / o.turns_completed, 3)
            if o.turn_of_first_conflict and o.turns_completed
            else None
        )
        per_run.append(
            {
                "run_id": o.run_id,
                "persona_condition": o.persona_condition,
                "survived": o.survived,
                "succeeded": o.succeeded,
                "turns_completed": o.turns_completed,
                "turn_of_first_conflict": o.turn_of_first_conflict,
                "normalized_position_of_first_conflict": normalized,
                "conflict_count": len(o.conflicts),
            }
        )

    return {
        "total_runs": total,
        "survival_rate": (survived_count / total) if total else None,
        "success_rate": (succeeded_count / total) if total else None,
        "fact_conflict_rate_of_all_conflicts": (fact_conflicts / total_conflicts) if total_conflicts else None,
        "type_category_breakdown": type_category_counts,
        "per_run": per_run,
    }


def print_report(report: dict) -> None:
    print(f"Total runs: {report['total_runs']}")
    print(f"Survival rate: {report['survival_rate']}")
    print(f"Success rate: {report['success_rate']}")
    print(f"Fact-conflict rate (share of all detected conflicts): {report['fact_conflict_rate_of_all_conflicts']}")
    print("Conflict type/category breakdown:", report["type_category_breakdown"])
    print("\nPer-run detail:")
    for r in report["per_run"]:
        print(
            f"  {r['run_id']} ({r['persona_condition']}): survived={r['survived']} "
            f"succeeded={r['succeeded']} turns={r['turns_completed']} "
            f"first_conflict_turn={r['turn_of_first_conflict']} "
            f"(normalized={r['normalized_position_of_first_conflict']}) conflicts={r['conflict_count']}"
        )

    print("\n--- T017: Comparison against published NCP-Bench baselines (SC-003) ---")
    print(f"  This run's survival rate: {report['survival_rate']}")
    print(f"  NCP-Bench's best-model survival at turn 20: {NCP_BENCH_BASELINE['best_model_survival_at_turn_20']}")
    print(f"  This run's fact-conflict rate: {report['fact_conflict_rate_of_all_conflicts']}")
    print(f"  NCP-Bench's fact-conflict rate range: {NCP_BENCH_BASELINE['fact_conflict_rate_range']}")
    print("  (A comparison point, not a pass/fail gate -- per SC-003 and this project's SC-002 precedent.)")


def run_category_coverage_check(
    trajectory: list[TrajectoryNode],
    commitments: list[Commitment],
    world_state: WorldState,
) -> dict:
    """T018: SC-004 -- deliberately targets each of the four seeded state categories
    (resources, possessions, position, status_flags) with a real action, confirming that
    whatever conflict-or-no-conflict outcome results is correctly category-attributed. This
    tests OUR attribution mechanism's coverage across all four categories -- it does not claim
    every targeted action forces an actual conflict, only that our own code correctly
    classifies whatever happens.
    """
    handlers = WorldStateToolHandlers(world_state)
    system_prompt = build_dm_system_prompt(trajectory, commitments)
    client = build_client()
    conversation: list = []

    run_turn(
        client, handlers, conversation,
        "Begin the session: narrate a brief opening scene consistent with the seeded world state.",
        max_tool_iterations=MAX_TOOL_ITERATIONS,
        tool_schemas=COMBINED_TOOL_SCHEMAS, system_prompt=system_prompt,
    )

    targets: list[tuple[str, str]] = []
    if world_state.resources:
        rname = next(iter(world_state.resources))
        targets.append(("resources", f"I push myself hard, straining my {rname.replace('_', ' ')}."))
    if world_state.possessions:
        pname = next(iter(world_state.possessions))
        targets.append(("possessions", f"I check whether I am carrying the {pname.replace('_', ' ')}."))
    targets.append(("position", "I state clearly, out loud, exactly where I am standing right now."))
    if world_state.status_flags:
        sname = next(iter(world_state.status_flags))
        targets.append(("status_flags", f"I double-check the current status of the {sname.replace('_', ' ')}."))

    results: dict[str, dict] = {}
    for turn_number, (category, action) in enumerate(targets, start=1):
        state_before = world_state.to_dict()
        result = run_turn(
            client, handlers, conversation, action,
            max_tool_iterations=MAX_TOOL_ITERATIONS,
            tool_schemas=COMBINED_TOOL_SCHEMAS, system_prompt=system_prompt,
        )
        conflict = check_turn(
            turn_number, result.narration, action, world_state, commitments,
            state_before=state_before,
        )
        results[category] = {
            "action": action,
            "conflict_found": conflict is not None,
            "attributed_category": conflict.state_category if conflict else None,
        }

    print("\n--- T018: SC-004 category-coverage check ---")
    required = {"resources", "possessions", "position", "status_flags"}
    covered = required & set(results.keys())
    for category, info in results.items():
        print(
            f"  {category}: action={info['action']!r} "
            f"conflict_found={info['conflict_found']} attributed={info['attributed_category']}"
        )
    missing = required - covered
    if missing:
        print(f"  WARNING: categories never exercised (scenario had no seeded facts for): {missing}")
    else:
        print("  All 4 required categories exercised.")

    return results


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
    parser.add_argument(
        "--category-coverage", action="store_true",
        help="Also run T018's SC-004 category-coverage check on the first generated scenario",
    )
    parser.add_argument(
        "--fast-forward", type=float, default=None, metavar="FRACTION",
        help="Fraction (0.0-1.0) of each scenario's trajectory to synthetically fast-forward "
        "through (a generated multi-turn transcript + a state seeded past that point) instead "
        "of playing every turn live from the start -- cuts API cost roughly in proportion to "
        "the fraction skipped, since only the REMAINING turns run for real, while still giving "
        "the DM a genuinely large volume of prior context. Omit to run each session from "
        "scratch (the original behavior).",
    )
    parser.add_argument(
        "--fast-forward-turns", type=int, default=30, metavar="N",
        help="Number of synthetic turns to generate for --fast-forward's transcript "
        "(default: 30). Ignored if --fast-forward is omitted.",
    )
    parser.add_argument(
        "--workers", type=int, default=4, metavar="N",
        help="Max concurrent threads for scenario generation and session-running (default: 4). "
        "Each (scenario, persona) run is fully independent -- its own client, its own "
        "WorldState copy -- so this is safe to raise; keep it modest relative to your API "
        "tier's rate limits rather than maximally high.",
    )
    return parser.parse_args()


def _generate_one_scenario(
    name: str, outline: str, args: argparse.Namespace
) -> tuple[list[TrajectoryNode], list[Commitment], WorldState, list[tuple[str, str]] | None]:
    """One scenario-generation unit of work, run inside the Phase 1 thread pool."""
    log(name, "Generating scenario...")
    if args.fast_forward is not None:
        trajectory, commitments, world_state, transcript, cutoff_index = generate_fast_forward_scenario(
            outline, args.fast_forward, args.fast_forward_turns
        )
        log(
            name,
            f"Scenario ready -- fast-forwarded past node {cutoff_index} of "
            f"{len(trajectory) - 1}, {len(transcript)}-turn synthetic transcript",
        )
        return trajectory, commitments, world_state, transcript
    trajectory, commitments, world_state = generate_scenario(outline)
    log(name, f"Scenario ready -- {len(trajectory)} nodes, {len(commitments)} commitments")
    return trajectory, commitments, world_state, None


def _run_one_session(
    name: str,
    persona: str,
    trajectory: list[TrajectoryNode],
    commitments: list[Commitment],
    world_state: WorldState,
    transcript: list[tuple[str, str]] | None,
    args: argparse.Namespace,
) -> SessionOutcome:
    """One session-running unit of work, run inside the Phase 2 thread pool.

    Found live (during fast-forward development, but a pre-existing bug): passing the SAME
    world_state object to run_session for each persona let the second persona's session
    silently inherit whatever mutations the first persona's session left behind, instead of
    starting from the actual seeded state -- WorldState.from_dict(world_state.to_dict()) is
    now a genuine deep copy (since to_dict()'s own live-reference bug was fixed), so each
    persona gets its own independent, correctly-seeded copy. This matters even more now that
    generation and running are both concurrent: multiple personas may genuinely run AT THE
    SAME TIME against copies seeded from the same original world_state.
    """
    run_id = f"{name}-{persona}"
    run_world_state = WorldState.from_dict(world_state.to_dict())
    log(run_id, "Starting session...")
    outcome = run_session(
        trajectory, commitments, run_world_state, persona, args.turns, run_id,
        transcript=transcript,
    )
    outcome.save(Path(f"{run_id}.scenario.json"))
    log(
        run_id,
        f"Finished -- survived={outcome.survived} succeeded={outcome.succeeded} "
        f"turns={outcome.turns_completed} conflicts={len(outcome.conflicts)}",
    )
    return outcome


if __name__ == "__main__":
    args = parse_args()

    scenario_ok = run_scenario_checks()
    print("=" * 60)
    print("SC-001 result:", "PASS -- all scenarios isolated" if scenario_ok else "FAIL -- see above (informational; does not block session-running below, which regenerates its own scenarios independently)")

    if args.scenarios_only:
        sys.exit(0 if scenario_ok else 1)

    personas = [p.strip() for p in args.personas.split(",") if p.strip()]
    outline_items = list(OUTLINES.items())[: args.runs]

    # Phase 1: generate all scenarios concurrently -- independent per outline, no shared state.
    scenarios: dict[str, tuple] = {}
    generation_errors: dict[str, str] = {}
    interrupted = False

    print(f"=== Phase 1: generating {len(outline_items)} scenario(s), up to {args.workers} at a time ===")
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(_generate_one_scenario, name, outline, args): name
            for name, outline in outline_items
        }
        try:
            for future in concurrent.futures.as_completed(futures):
                name = futures[future]
                try:
                    scenarios[name] = future.result()
                except IsolationViolationError as exc:
                    log(name, f"Skipped -- isolation check failed: {exc}")
                    generation_errors[name] = f"isolation check failed: {exc}"
                except (ValueError, TypeError) as exc:
                    # Found live (T021): a malformed generation (bad structural shape, or the
                    # kind of stray-key issue world_state.py's from_dict now filters
                    # defensively) should cost this one scenario, not the whole batch.
                    log(name, f"Skipped -- generation failed: {exc}")
                    generation_errors[name] = f"generation failed: {exc}"
                except Exception as exc:  # noqa: BLE001 -- quota/rate-limit/network errors
                    log(name, f"Skipped -- unexpected error: {exc!r}")
                    generation_errors[name] = f"unexpected error: {exc!r}"
        except KeyboardInterrupt:
            interrupted = True
            log("main", "Interrupted (Ctrl+C) -- cancelling not-yet-started generations.")
            # Known limitation: Python cannot forcibly kill an ALREADY-RUNNING thread, only
            # prevent not-yet-started ones from starting. Any generation already mid-flight
            # keeps running in the background; we just stop waiting on it here.
            executor.shutdown(wait=False, cancel_futures=True)

    first_scenario = next(iter(scenarios.values()), None)

    # Phase 2: run every (scenario, persona) session concurrently -- independent of each other.
    outcomes: list[SessionOutcome] = []
    run_errors: dict[str, str] = {}

    if not interrupted and scenarios:
        run_tasks = [
            (name, persona, *scenarios[name])
            for name in scenarios
            for persona in personas
        ]
        print(f"=== Phase 2: running {len(run_tasks)} session(s), up to {args.workers} at a time ===")
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = {
                executor.submit(_run_one_session, name, persona, trajectory, commitments, world_state, transcript, args): f"{name}-{persona}"
                for name, persona, trajectory, commitments, world_state, transcript in run_tasks
            }
            try:
                for future in concurrent.futures.as_completed(futures):
                    run_id = futures[future]
                    try:
                        outcomes.append(future.result())
                    except Exception as exc:  # noqa: BLE001 -- see _run_one_session's callers
                        log(run_id, f"FAILED: {exc!r}")
                        run_errors[run_id] = repr(exc)
            except KeyboardInterrupt:
                interrupted = True
                log("main", "Interrupted (Ctrl+C) -- cancelling not-yet-started runs.")
                executor.shutdown(wait=False, cancel_futures=True)

    print("=" * 60)
    if interrupted:
        print("Interrupted by user (Ctrl+C).")
    print(
        f"{len(outcomes)} run(s) completed, {len(run_errors)} run(s) failed, "
        f"{len(generation_errors)} scenario(s) failed to generate.\n"
    )
    if generation_errors:
        print("Scenario generation failures:")
        for name, reason in generation_errors.items():
            print(f"  {name}: {reason}")
    if run_errors:
        print("Session run failures:")
        for run_id, reason in run_errors.items():
            print(f"  {run_id}: {reason}")

    if outcomes:
        report = build_report(outcomes)
        print_report(report)
    else:
        print("No runs completed -- nothing to report.")

    if args.category_coverage and first_scenario is not None and not interrupted:
        run_category_coverage_check(*first_scenario[:3])
    elif args.category_coverage and interrupted:
        print("\nSkipping the category-coverage check since the run was interrupted.")

    sys.exit(1 if (interrupted or run_errors or generation_errors) else 0)
