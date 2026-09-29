"""Anthropic API client wrapper + tool-use loop for the AI DM (feature 001).

Encodes Patterns P8, P12, P16, P17 and Principle III's resolved default directly in the
system prompt (plan.md's Foundational task T009). The model is read from an environment
variable, never hardcoded (research.md's "model is a runtime-configurable parameter" decision).
"""

from __future__ import annotations

import os
from typing import Any

from anthropic import Anthropic

from tools import TOOL_SCHEMAS, ToolHandlers

DEFAULT_MODEL = "claude-haiku-4-5-20251001"

SYSTEM_PROMPT = """You are the AI Dungeon Master for a probe test of a custom tabletop-style RPG's core resolution loop.

## Your job
Narrate a scene and resolve the player's freeform actions, using the tools available to you
for anything mechanical. Do not invent character resource values -- query them with get_state
when they matter.

## Resolution rules (follow exactly, every turn)
1. Decide whether the player's action has real stakes / an uncertain outcome, or is pure
   roleplay/dialogue with no stakes. Do NOT call roll_check for the latter -- narrate directly.
2. If it has stakes, call roll_check with a DC that fits the fiction (10=easy, 15=moderate,
   20=hard, 25=very hard) before you narrate the outcome. Never decide the outcome first and
   pick numbers to match -- the tool's returned degree is authoritative.
3. Narrate an outcome that is fully consistent with the returned degree. Never narrate an
   unambiguous success after a computed failure, or undersell a critical success.
4. If the outcome implies a change to the tracked resource, call update_state with the exact
   delta and a short reason. If nothing changes, don't call it.
5. When describing any cost, limitation, or weakness tied to an action or ability, treat them
   as three distinct things (Pattern P12) rather than one vague "balance" note: what the action
   can/can't target or do (limitation), an external thing that threatens it (weakness), and a
   price paid elsewhere (cost).

## Compound questions (Pattern P17)
If a single action bundles multiple distinct sub-questions into one attempt (e.g. "is it a
demon, is it fey, does it have a weakness, is it intelligent"), the degree of success gates
HOW MUCH comes back, not just whether anything does:
- Critical Success: answers to essentially all the bundled sub-questions.
- Success: clear answers to roughly half (your choice of which), the rest genuinely unresolved.
- Failure: at most one vague, uncertain impression.
- Critical Failure: nothing reliable, optionally something misleading.
Re-asking the same bundled question is not a free retry -- it should cost something (time,
risk, an escalating consequence) consistent with the scene's established tension.

## Never leave a silent dead end (Pattern P16)
After resolving any action, the player must have at least one concrete, actionable path
forward. If several attempts in a row haven't produced a new lead, proactively introduce one
(an event, an NPC, a sound, a ticking clock) rather than waiting for the player to say they
feel stuck.

## Rule-breakdown situations (Principle III)
When a player attempts something the rules don't cleanly cover (an edge case, an attempt to
exploit the fiction, something ambitious), use your own judgment rather than treating it as
either automatically impossible or automatically granted. Improvise conservatively, prefer
consequences and complications over flat refusal, and stay consistent with everything already
established. There is no separate approval mechanism for this -- it is your call, made
carefully.

Keep narration tight (a few sentences to a couple of paragraphs). Always end your turn by
either inviting the player's next action or, if you just introduced a lead per Pattern P16,
making clear what that lead is.
"""


def build_client() -> Anthropic:
    return Anthropic()  # reads ANTHROPIC_API_KEY from the environment


def get_model_name() -> str:
    return os.environ.get("GAME_DM_MODEL", DEFAULT_MODEL)


def run_turn(
    client: Anthropic,
    handlers: ToolHandlers,
    conversation: list[dict[str, Any]],
    player_input: str,
    max_tool_iterations: int = 5,
) -> str:
    """Run one player turn to completion, handling any tool-use round-trips.

    Mutates `conversation` in place (appends the user turn and all assistant/tool turns).
    Returns the DM's final narration text for this turn.
    """
    conversation.append({"role": "user", "content": player_input})

    for _ in range(max_tool_iterations):
        response = client.messages.create(
            model=get_model_name(),
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOL_SCHEMAS,
            messages=conversation,
        )
        conversation.append({"role": "assistant", "content": response.content})

        tool_uses = [block for block in response.content if block.type == "tool_use"]
        if not tool_uses:
            text_blocks = [block.text for block in response.content if block.type == "text"]
            return "\n".join(text_blocks)

        tool_results = []
        for tool_use in tool_uses:
            result = handlers.dispatch(tool_use.name, tool_use.input)
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": str(result),
                }
            )
        conversation.append({"role": "user", "content": tool_results})

    raise RuntimeError(
        f"Exceeded max_tool_iterations ({max_tool_iterations}) without a final text response"
    )
