"""The owner's own way to run the DM: through the Claude Agent SDK, on their Claude login (Claude Code), with no API key.
The DM's memory is Claude Code's session file, and the save keeps its id. The browser version runs on the API instead
(dm/model.py); both use the same tools, instructions and saves."""

from __future__ import annotations

import os
import tempfile
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

from dm.model import MAX_ROUNDS, Tool, context_size

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
        # The instructions go to Claude Code as a file: with a party's sheets they outgrow a Windows command line
        # (about 32,700 characters). A file prompt can't carry the snapshot switch, so it goes as the CLI flag.
        fd, self.system_file = tempfile.mkstemp(prefix="system-", suffix=".md", dir=cwd)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(system)
        self.options = ClaudeAgentOptions(
            tools=[], setting_sources=[], strict_mcp_config=True, max_turns=MAX_ROUNDS, cwd=cwd, env=DM_ENV,
            system_prompt={"type": "file", "path": self.system_file}, extra_args={"system-prompt-snapshot": "off"},
            model=model, mcp_servers={"dm": server}, allowed_tools=[f"mcp__dm__{t.name}" for t in tools],
            resume=session_id)
        self.client = ClaudeSDKClient(options=self.options)
        self.session_id = session_id
        self.size = 0  # the conversation's length after the last model call, in tokens

    async def open(self) -> None:
        await self.client.connect()

    async def close(self) -> None:
        await self.client.disconnect()
        Path(self.system_file).unlink(missing_ok=True)

    async def respond(self, text: str, on_text: Callable[[str], None]) -> str | None:
        """As model.respond: the DM's reply to `text`, tools and all. Returns None, or why the call failed."""
        failed = None
        await self.client.query(text)
        async for msg in self.client.receive_response():
            if isinstance(msg, AssistantMessage):
                if msg.usage:
                    self.size = context_size(msg.usage)
                for b in msg.content:
                    if isinstance(b, TextBlock) and b.text.strip():
                        on_text(b.text.strip())
            elif isinstance(msg, ResultMessage):
                self.session_id = msg.session_id
                if msg.is_error:
                    failed = str(msg.result or getattr(msg, "errors", "") or "the SDK reported an error")
        return failed
