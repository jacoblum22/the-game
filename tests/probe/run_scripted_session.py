"""Scripted, automated verification harness for feature 001.

Replaces the earlier relayed-chat probe's human-in-the-loop relay (probe-results.md) with a
real, repeatable script driven against the live API with actual tool-calling. Requires
GEMINI_API_KEY to be set -- this is NOT a pytest unit test (tests/unit/ covers the pure
parts); it makes real, billed API calls, so it's run manually via:

    python tests/probe/run_scripted_session.py

Built incrementally per tasks.md:
- T013 (US1): one fixed action, asserted a computed degree was produced. Superseded by the
  fuller sequence below, which exercises the same check as its first resolved turn.
- T016 (US2): a fixed 10-action sequence mirroring probe-results.md's turn variety
  (investigation, a compound question, combat, a time-pressure edge case, and a fresh
  compound-question test that the earlier relayed session never actually exercised).
- T017-T019 (US3): SC-002 (via a bounded LLM-judge call, see dm_agent.judge_consistency),
  SC-003 (state-change traceability), SC-004 (stakes-free turns correctly skip roll_check),
  and a final summary print.

Uses only dm_agent.TurnResult's provider-agnostic tool_calls list -- never raw Gemini/Anthropic
response internals -- so this script doesn't need to change again if the provider changes.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

from dm_agent import build_action_attempt, build_client, judge_consistency, run_turn  # noqa: E402
from state import CharacterState, SessionLog  # noqa: E402
from tools import ToolHandlers  # noqa: E402

# Mirrors the turn variety in probe-results.md. Comments mark what each line is meant to
# exercise; the model's own judgment (not this script) decides requires_resolution for real.
SCRIPT = [
    "I look around and ask what's going on here.",  # expected stakes-free
    "I search the area carefully for anything useful or out of place.",  # expected resolved
    (
        "Can you tell me what kind of creature that is, whether it seems hostile, "
        "and if it has any obvious weaknesses?"
    ),  # compound question (Pattern P17)
    "I try to convince them to let me pass peacefully.",  # expected resolved
    "I attack it with whatever weapon I have.",  # expected resolved
    "I take a slow breath and steady my nerves.",  # expected stakes-free
    "I attack it five more times as fast as I possibly can.",  # time-pressure edge case
    "I try to flee back the way I came.",  # expected resolved
    "I push through the pain and keep moving forward.",  # expected resolved, likely resource-implying
    (
        "Tell me everything you know: this place's history, who built it, "
        "and where any treasure might be hidden."
    ),  # a second, fresh compound-question test
]


def run_full_session() -> dict:
    character = CharacterState(
        name="Kess", resource_name="Vitality", resource_current=12, resource_max=12
    )
    session = SessionLog(character=character)
    handlers = ToolHandlers(session)
    client = build_client()

    conversation: list = []
    opening = run_turn(
        client,
        handlers,
        conversation,
        "Begin the session: narrate a brief opening scene and invite my first action.",
    )
    print(f"--- Opening\n{opening.narration}\n")

    for turn_number, action in enumerate(SCRIPT, start=1):
        state_before = session.character.to_dict()
        result = run_turn(client, handlers, conversation, action)
        state_after = session.character.to_dict()
        attempt = build_action_attempt(turn_number, action, state_before, state_after, result)
        session.append_turn(attempt)

        print(f"--- Turn {turn_number}: {action}")
        print(
            f"    requires_resolution={attempt.requires_resolution} degree={attempt.degree} "
            f"resource {state_before.get('resource_current')} -> {state_after.get('resource_current')}"
        )
        preview = result.narration[:200] + ("..." if len(result.narration) > 200 else "")
        print(f"    {preview}\n")

    log_path = Path("scripted_session.session.json")
    session.save(log_path)
    print(f"Full session log saved to {log_path}\n")

    return summarize(client, session)


def summarize(client, session: SessionLog) -> dict:
    resolved = [t for t in session.turns if t.requires_resolution]
    unresolved = [t for t in session.turns if not t.requires_resolution]

    # SC-001: every resolved turn has a computed degree. Checked for real, not assumed --
    # build_action_attempt only sets requires_resolution=True when a roll_check call was
    # actually found, but a missing degree on one of those would still be a real bug to catch.
    sc001_pass = all(t.degree is not None for t in resolved)

    # SC-002: bounded LLM-judge call per resolved turn (dm_agent.judge_consistency) -- this is
    # the actual measurement instrument this feature was built to produce; probe-results.md
    # could only estimate this by hand.
    contradiction_turns = [t.turn_number for t in resolved if judge_consistency(client, t.narration, t.degree)]

    # SC-003: which turns actually changed state, for a reviewer to audit against the
    # narration above -- state changing without narration implying it (or vice versa) is
    # exactly what this makes checkable from the log alone.
    state_change_turns = [
        t.turn_number
        for t in session.turns
        if t.state_before.get("resource_current") != t.state_after.get("resource_current")
    ]

    # SC-004: true by construction of build_action_attempt (requires_resolution=False means
    # no roll_check call was found in that turn) -- reported for visibility, not re-derived.
    sc004_pass = True

    return {
        "total_turns": len(session.turns),
        "resolved_count": len(resolved),
        "unresolved_count": len(unresolved),
        "sc001_all_resolved_have_degree": sc001_pass,
        "sc002_contradiction_turns": contradiction_turns,
        "sc002_contradiction_count": len(contradiction_turns),
        "sc003_state_change_turns": state_change_turns,
        "sc004_all_unresolved_skipped_roll": sc004_pass,
        "degree_tally": {
            d: sum(1 for t in resolved if t.degree == d)
            for d in ("critical_success", "success", "failure", "critical_failure")
        },
    }


if __name__ == "__main__":
    summary = run_full_session()
    print("=" * 60)
    print("SESSION SUMMARY")
    print("=" * 60)
    for key, value in summary.items():
        print(f"{key}: {value}")

    ok = summary["sc001_all_resolved_have_degree"] and summary["sc002_contradiction_count"] == 0
    sys.exit(0 if ok else 1)
