"""Gemini API client wrapper + tool-use loop for the AI DM (feature 001).

Encodes Patterns P8, P12, P16, P17 and Principle III's resolved default directly in the
system prompt (plan.md's Foundational task T009). The model AND the provider are both
runtime-configurable, not hardcoded: this file originally called Anthropic's API directly;
it was swapped to Google's Gemini API (google-genai SDK) once the project owner decided to
avoid paid Anthropic API usage and use an existing Gemini key instead. Only this file changed
-- state.py, resolution.py, and tools.py's actual logic were untouched, which is exactly the
"cheap to reverse" property research.md's original decision was chosen for.

Automatic function calling is not used: tools are passed as schema-only FunctionDeclaration
objects (no attached Python callable), so the SDK has nothing to auto-execute -- dispatch
happens explicitly through ToolHandlers, keeping the Principle I / Pattern P13 boundary
visible and inspectable rather than hidden inside SDK-internal auto-execution.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from google import genai
from google.genai import types

from tools import TOOL_SCHEMAS, ToolHandlers

DEFAULT_MODEL = "gemini-3.8-flash"


def _load_dotenv(path: Path | None = None) -> None:
    """Minimal .env loader -- sets os.environ from KEY=VALUE lines in a .env file at the
    repo root, without overriding anything already set in the real environment.

    Exists because shell-set environment variables don't reliably survive across this
    project's separate tool/terminal processes (Bash tool, PowerShell tool, and the user's
    own terminal panel are three different processes); a file on disk sidesteps that
    entirely. Deliberately not using python-dotenv to avoid a dependency for ~10 lines.
    """
    if path is None:
        path = Path(__file__).resolve().parent.parent / ".env"
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


_load_dotenv()

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


@dataclass
class TurnResult:
    """What happened during one player turn -- provider-agnostic on purpose.

    Callers (main.py, tests/probe/run_scripted_session.py) should only ever touch this,
    never raw Gemini response/content objects, so a future provider swap stays contained to
    this file, matching research.md's "cheap to reverse" design intent.
    """

    narration: str
    tool_calls: list[dict[str, Any]] = field(default_factory=list)


def build_client() -> genai.Client:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set. Set it and try again (see .env.example).")
    return genai.Client(api_key=api_key)


def get_model_name() -> str:
    return os.environ.get("GAME_DM_MODEL", DEFAULT_MODEL)


def _build_tool() -> types.Tool:
    declarations = [
        types.FunctionDeclaration(
            name=schema["name"],
            description=schema["description"],
            parameters_json_schema=schema["input_schema"],
        )
        for schema in TOOL_SCHEMAS
    ]
    return types.Tool(function_declarations=declarations)


_TOOL = _build_tool()


def run_turn(
    client: genai.Client,
    handlers: ToolHandlers,
    conversation: list[types.Content],
    player_input: str,
    max_tool_iterations: int = 5,
) -> TurnResult:
    """Run one player turn to completion, handling any tool-use round-trips.

    Mutates `conversation` in place (appends the user turn and all model/tool turns).
    Returns a TurnResult with the DM's final narration and a record of any tool calls made.
    """
    conversation.append(types.Content(role="user", parts=[types.Part.from_text(text=player_input)]))
    tool_call_log: list[dict[str, Any]] = []

    for _ in range(max_tool_iterations):
        response = client.models.generate_content(
            model=get_model_name(),
            contents=conversation,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                tools=[_TOOL],
            ),
        )
        model_content = response.candidates[0].content
        conversation.append(model_content)

        function_calls = response.function_calls
        if not function_calls:
            return TurnResult(narration=response.text or "", tool_calls=tool_call_log)

        response_parts = []
        for call in function_calls:
            result = handlers.dispatch(call.name, dict(call.args))
            tool_call_log.append({"name": call.name, "input": dict(call.args), "result": result})
            response_parts.append(types.Part.from_function_response(name=call.name, response=result))

        # The API's error message for an invalid role lists valid roles as: SYSTEM, SYSTEM_1,
        # USER, ASSISTANT, DEVELOPER, CONTEXT, USER_CONTEXT, MODEL -- no "tool" role, despite
        # the google-genai README's own example using role='tool'. Using "user" here matches
        # Anthropic's equivalent convention (tool results sent as a user-role message) and is
        # confirmed valid by the API's own error output.
        conversation.append(types.Content(role="user", parts=response_parts))

    raise RuntimeError(
        f"Exceeded max_tool_iterations ({max_tool_iterations}) without a final text response"
    )
