"""The owner's own way to run the DM: through the Claude Agent SDK, on their Claude login (Claude Code), with no API key.
The DM's memory is Claude Code's session file, and the save keeps its id. The browser version runs on the API instead
(dm/model.py); both use the same tools, instructions and saves."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ResultMessage,
    TextBlock,
    create_sdk_mcp_server,
)
from claude_agent_sdk import tool as sdk_tool

from dm.model import MAX_ROUNDS, Tool

# The Claude Code program adds its own notes to every session. Run the DM outside any git repo (no git or worktree
# notes) and switch off the notes that have switches: the developer's memory, CLAUDE.md files, the token count and
# the mid-turn "the user hasn't heard from you in a while" nudge. As on the API (owner, 2026-10-13): no automatic
# compaction (the game will trim the conversation itself), and the instructions as they are now on every call, not
# the copy Claude Code would otherwise keep from the game's first call.
DM_HOME = Path.home() / "AppData" / "Local" / "the-game-dm"
DM_ENV = {"CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1", "CLAUDE_CODE_DISABLE_CLAUDE_MDS": "1",
          "CLAUDE_CODE_TOTAL_TOKENS_REMINDER": "off", "CLAUDE_CODE_DISABLE_GIT_INSTRUCTIONS": "1",
          "CLAUDE_CODE_SILENT_TURN_REMINDER": "0", "DISABLE_AUTO_COMPACT": "1"}


class Client:
    """One DM conversation in Claude Code. `tools` are ours (dm/model.py Tool), handed to the SDK as they are."""

    def __init__(self, model: str, system: str, tools: list[Tool], cwd: str, session_id: str | None) -> None:
        Path(cwd).mkdir(parents=True, exist_ok=True)
        server = create_sdk_mcp_server("dm", tools=[sdk_tool(t.name, t.description, t.input_schema)(t.handler)
                                                     for t in tools])
        self.options = ClaudeAgentOptions(
            tools=[], setting_sources=[], strict_mcp_config=True, max_turns=MAX_ROUNDS, cwd=cwd, env=DM_ENV,
            system_prompt={"type": "custom", "prompt": system, "snapshot": False}, model=model, mcp_servers={"dm": server},
            allowed_tools=[f"mcp__dm__{t.name}" for t in tools], resume=session_id)
        self.client = ClaudeSDKClient(options=self.options)
        self.session_id = session_id

    async def open(self) -> None:
        await self.client.connect()

    async def close(self) -> None:
        await self.client.disconnect()

    async def respond(self, text: str, on_text: Callable[[str], None]) -> str | None:
        """As model.respond: the DM's reply to `text`, tools and all. Returns None, or why the call failed."""
        failed = None
        await self.client.query(text)
        async for msg in self.client.receive_response():
            if isinstance(msg, AssistantMessage):
                for b in msg.content:
                    if isinstance(b, TextBlock) and b.text.strip():
                        on_text(b.text.strip())
            elif isinstance(msg, ResultMessage):
                self.session_id = msg.session_id
                if msg.is_error:
                    failed = str(msg.result or getattr(msg, "errors", "") or "the SDK reported an error")
        return failed
