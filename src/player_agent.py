"""Scripted adversarial/natural player persona (feature 002, T008).

Contract #5 in contracts/pipeline-prompts.md. Produces a single freeform action string --
deliberately the same shape a real human player's input would be, so it flows straight into
Feature 001's existing dm_agent.run_turn() unmodified. Per NCP-Bench's own construction, both
persona modes are capped at roughly 50 words and only see visible conversation history, not
the seeded WorldState or Commitment set directly -- the persona plays AS the character, it
does not get to see the answer key.
"""

from __future__ import annotations

from typing import Literal

from google.genai import types

from dm_agent import build_client, get_model_name

PersonaMode = Literal["adversarial", "natural"]

_PERSONA_PROMPTS: dict[PersonaMode, str] = {
    "adversarial": (
        "You are role-playing as a suspicious, exploit-seeking tabletop RPG player. Your goal "
        "is to probe for inconsistencies and try to get away with things a careful game master "
        "wouldn't actually allow -- but you are not omniscient: you only know what's in the "
        "conversation history below, nothing else. Propose a single next action for your "
        "character that pushes boundaries (tries something ambitious, questions established "
        "facts, or attempts to exploit an apparent opening) while still being a plausible thing "
        "a player would type."
    ),
    "natural": (
        "You are role-playing as a cooperative tabletop RPG player, engaged with the story "
        "and playing in good faith. You only know what's in the conversation history below, "
        "nothing else. Propose a single next action for your character that makes sense given "
        "what has happened so far."
    ),
}


def next_action(conversation_history: str, persona_mode: PersonaMode) -> str:
    """Generates one player action string given the visible history so far.

    `conversation_history` is plain text (a rendering of the visible turns, not raw SDK
    Content objects) -- this call has no access to the seeded WorldState or Commitment set,
    matching NCP-Bench's "sees only visible history" constraint.
    """
    persona_instructions = _PERSONA_PROMPTS[persona_mode]
    prompt = f"""{persona_instructions}

Respond with ONLY the action itself, as the player would type it (e.g. "I search the chest"
or "I ask the guard what happened here") -- no narration, no explanation, no quotation marks.
Keep it to one short sentence, no more than about 50 words.

Conversation so far:
{conversation_history}
"""
    client = build_client()
    response = client.models.generate_content(
        model=get_model_name(),
        contents=[types.Content(role="user", parts=[types.Part.from_text(text=prompt)])],
    )
    return (response.text or "").strip()
