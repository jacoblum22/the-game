"""CLI entry point for the action-resolution probe (feature 001).

Run with: python src/main.py
Requires GEMINI_API_KEY set (see .env.example). Optional GAME_DM_MODEL to override the
default model. See quickstart.md for the full guide.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

from dm_agent import build_action_attempt, build_client, run_turn
from state import CharacterState, SessionLog
from tools import ToolHandlers


def main() -> None:
    character = CharacterState(
        name="Kess", resource_name="Vitality", resource_current=12, resource_max=12
    )
    session = SessionLog(character=character)
    handlers = ToolHandlers(session)

    try:
        client = build_client()
    except Exception as exc:  # build_client raises if GEMINI_API_KEY is missing
        print(f"Could not start the Gemini client: {exc}")
        print("Set GEMINI_API_KEY (see .env.example) and try again.")
        sys.exit(1)

    log_path = Path(f"session_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.session.json")
    print(f"Session log will be written to {log_path}")
    print(f"Character: {character.name} -- {character.resource_name} {character.resource_current}/{character.resource_max}")
    print("Type an action, or 'quit' to end the session.\n")

    conversation: list = []
    turn_number = 0

    # Opening narration -- the model invents the scene; character/resource are already fixed.
    opening = run_turn(
        client,
        handlers,
        conversation,
        "Begin the session: narrate a brief opening scene for this character and invite their first action.",
    )
    print(opening.narration, "\n")

    while True:
        try:
            player_input = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            player_input = "quit"

        if player_input.lower() in {"quit", "exit"}:
            break
        if not player_input:
            continue

        turn_number += 1
        state_before = session.character.to_dict()
        result = run_turn(client, handlers, conversation, player_input)
        state_after = session.character.to_dict()
        session.append_turn(
            build_action_attempt(turn_number, player_input, state_before, state_after, result)
        )
        print(f"\n{result.narration}\n")

    session.save(log_path)
    print(f"Session ended. Log saved to {log_path}")


if __name__ == "__main__":
    main()
