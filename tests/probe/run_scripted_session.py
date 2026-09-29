"""Scripted, automated verification harness for feature 001.

Replaces the earlier relayed-chat probe's human-in-the-loop relay (probe-results.md) with a
real, repeatable script driven against the live API with actual tool-calling. Requires
ANTHROPIC_API_KEY to be set -- this is NOT a pytest unit test (tests/unit/ covers the pure
parts); it makes real, billed API calls, so it's run manually via:

    python tests/probe/run_scripted_session.py

Built incrementally per tasks.md:
- T013 (US1): one fixed action, asserts a computed degree was produced.
- T016 (US2): extends to a full 10+ action sequence, mirroring probe-results.md's turn variety.
- T017-T019 (US3): adds the SC-002/SC-003/SC-004 consistency checks and a final summary.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

from dm_agent import build_client, run_turn  # noqa: E402
from state import CharacterState, SessionLog  # noqa: E402
from tools import ToolHandlers  # noqa: E402


def find_tool_use_and_result(conversation: list[dict], tool_name: str, since_index: int):
    """Scan conversation turns from since_index for a matching tool_use and its result.

    Returns (tool_use_block, result_dict_str) or (None, None) if not found. This is how T013
    checks a degree was actually produced, before US2/US3 (T014-T019) build proper per-turn
    ActionAttempt logging into SessionLog itself.
    """
    tool_use_block = None
    for message in conversation[since_index:]:
        if message["role"] != "assistant":
            continue
        for block in message["content"]:
            block_type = getattr(block, "type", None) or (
                block.get("type") if isinstance(block, dict) else None
            )
            if block_type == "tool_use":
                name = getattr(block, "name", None) or block.get("name")
                if name == tool_name:
                    tool_use_block = block
    if tool_use_block is None:
        return None, None

    tool_use_id = getattr(tool_use_block, "id", None) or tool_use_block.get("id")
    for message in conversation[since_index:]:
        if message["role"] != "user":
            continue
        for block in message["content"]:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "tool_result" and block.get("tool_use_id") == tool_use_id:
                return tool_use_block, block.get("content")
    return tool_use_block, None


def run_us1_check() -> bool:
    """T013: one fixed, real-stakes action; assert a computed degree was produced."""
    character = CharacterState(
        name="Kess", resource_name="Vitality", resource_current=12, resource_max=12
    )
    session = SessionLog(character=character)
    handlers = ToolHandlers(session)
    client = build_client()

    conversation: list[dict] = []
    run_turn(
        client,
        handlers,
        conversation,
        "Begin the session: narrate a one-sentence opening scene and invite my first action.",
    )

    before_index = len(conversation)
    action = "I try to force open the heavy oak door blocking the passage."
    narration = run_turn(client, handlers, conversation, action)

    tool_use, result = find_tool_use_and_result(conversation, "roll_check", before_index)
    print(f"Action: {action}")
    print(f"Narration:\n{narration}\n")

    if tool_use is None:
        print("FAIL (SC-001): roll_check was never called for a real-stakes action.")
        return False
    if result is None:
        print("FAIL: roll_check was called but no result was found in the conversation.")
        return False

    print(f"roll_check result: {result}")
    print("PASS (SC-001): a computed degree was produced for this action.")
    return True


if __name__ == "__main__":
    ok = run_us1_check()
    sys.exit(0 if ok else 1)
