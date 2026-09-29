"""Scripted, automated verification harness for feature 001.

Replaces the earlier relayed-chat probe's human-in-the-loop relay (probe-results.md) with a
real, repeatable script driven against the live API with actual tool-calling. Requires
GEMINI_API_KEY to be set -- this is NOT a pytest unit test (tests/unit/ covers the pure
parts); it makes real API calls, so it's run manually via:

    python tests/probe/run_scripted_session.py

Built incrementally per tasks.md:
- T013 (US1): one fixed action, asserts a computed degree was produced.
- T016 (US2): extends to a full 10+ action sequence, mirroring probe-results.md's turn variety.
- T017-T019 (US3): adds the SC-002/SC-003/SC-004 consistency checks and a final summary.

Uses only dm_agent.TurnResult's provider-agnostic tool_calls list -- never raw Gemini/Anthropic
response internals -- so this script doesn't need to change again if the provider changes.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

from dm_agent import build_client, run_turn  # noqa: E402
from state import CharacterState, SessionLog  # noqa: E402
from tools import ToolHandlers  # noqa: E402


def run_us1_check() -> bool:
    """T013: one fixed, real-stakes action; assert a computed degree was produced."""
    character = CharacterState(
        name="Kess", resource_name="Vitality", resource_current=12, resource_max=12
    )
    session = SessionLog(character=character)
    handlers = ToolHandlers(session)
    client = build_client()

    conversation: list = []
    run_turn(
        client,
        handlers,
        conversation,
        "Begin the session: narrate a one-sentence opening scene and invite my first action.",
    )

    action = "I try to force open the heavy oak door blocking the passage."
    result = run_turn(client, handlers, conversation, action)

    print(f"Action: {action}")
    print(f"Narration:\n{result.narration}\n")
    print(f"Tool calls this turn: {result.tool_calls}")

    roll_calls = [c for c in result.tool_calls if c["name"] == "roll_check"]
    if not roll_calls:
        print("FAIL (SC-001): roll_check was never called for a real-stakes action.")
        return False

    print(f"roll_check result: {roll_calls[0]['result']}")
    print("PASS (SC-001): a computed degree was produced for this action.")
    return True


if __name__ == "__main__":
    ok = run_us1_check()
    sys.exit(0 if ok else 1)
