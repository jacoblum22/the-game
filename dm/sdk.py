"""The owner's own way to run the DM: through the Claude Agent SDK, on their Claude login (Claude Code), with no API key.
The DM's memory is Claude Code's session file, and the save keeps its id. The browser version runs on the API instead
(dm/model.py); both use the same tools, instructions and saves."""

from __future__ import annotations

import asyncio
import os
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    HookMatcher,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
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

    def __init__(self, model: str, system: str, tools: list[Tool], cwd: str, session_id: str | None,
                 fork_at: str | None = None, done: Callable[[list[str]], bool] | None = None) -> None:
        """fork_at: an entry of session_id's file; the conversation goes on from there as a new session (a fork, the
        source left as it was: dm/branch.py). done: as model.respond's; Claude Code is stopped after the last tool
        of a model call when it says the reply is over."""
        self.done = done
        self.step: dict[str, str] = {}  # the latest model call's tool uses: id -> our tool's name
        self.ran: dict[str, bool] = {}  # of those, the ones that have run: id -> without an error
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
            resume=session_id,
            hooks={"PostToolUse": [HookMatcher(matcher="mcp__dm__.*", hooks=[self.after_tool])],
                   "PostToolUseFailure": [HookMatcher(matcher="mcp__dm__.*", hooks=[self.after_tool])]})
        if fork_at and session_id:
            self.options.resume_session_at, self.options.fork_session = fork_at, True
        self.client = ClaudeSDKClient(options=self.options)
        self.session_id = session_id
        self.size = 0  # the conversation's length after the last model call, in tokens

    async def open(self) -> None:
        await self.client.connect()

    async def close(self) -> None:
        await self.client.disconnect()
        Path(self.system_file).unlink(missing_ok=True)

    async def after_tool(self, data: Any, tool_use_id: str | None, context: Any) -> dict[str, Any]:
        """Claude Code's hook after each of our tools: once every tool of the model call has run, none with an error,
        and done() says the reply is over, Claude Code stops instead of calling the model to read the results."""
        if not self.done or not tool_use_id:
            return {}
        for _ in range(500):  # the call's message can reach respond() a moment after its tools start
            if tool_use_id in self.step:
                break
            await asyncio.sleep(0.01)
        else:
            return {}
        r = data.get("tool_response")
        self.ran[tool_use_id] = data.get("hook_event_name") == "PostToolUse" and not (
            isinstance(r, dict) and (r.get("is_error") or r.get("isError")))
        if set(self.ran) >= set(self.step) and all(self.ran.values()) and self.done(list(self.step.values())):
            return {"continue_": False, "stopReason": "the reply is written"}
        return {}

    async def respond(self, text: str, on_text: Callable[[str], None]) -> str | None:
        """As model.respond: the DM's reply to `text`, tools and all. Returns None, or why the call failed."""
        failed = None
        await self.client.query(text)
        async for msg in self.client.receive_response():
            if isinstance(msg, AssistantMessage):
                # An API error comes as Claude Code's own message ("API Error: ... safeguards flagged this message"):
                # a failure, never the DM's words (it was shown as the reply in 7 rounds running; autoloop, 2026-10-16)
                if msg.error or msg.model == "<synthetic>":
                    failed = " ".join(b.text for b in msg.content if isinstance(b, TextBlock)).strip() or str(msg.error)
                    continue
                if msg.usage:
                    self.size = context_size(msg.usage)
                for b in msg.content:
                    if isinstance(b, TextBlock) and b.text.strip():
                        on_text(b.text.strip())
                uses = {b.id: b.name.removeprefix("mcp__dm__") for b in msg.content if isinstance(b, ToolUseBlock)}
                if uses:  # text first: done() reads how much of the reply is written
                    self.ran, self.step = {}, uses
            elif isinstance(msg, ResultMessage):
                self.session_id = msg.session_id
                if msg.is_error and not failed:
                    failed = str(msg.result or getattr(msg, "errors", "") or "the SDK reported an error")
        return failed


async def structured(model: str, system: str, text: str, schema: dict[str, Any]) -> dict[str, Any]:
    """One call on the owner's Claude login that answers with JSON in `schema` (the continuity checker, dm/check.py):
    no tools, no memory, one turn. Raises model.Failed if there is no answer."""
    from claude_agent_sdk import query
    from dm.model import Failed
    DM_HOME.mkdir(parents=True, exist_ok=True)
    options = ClaudeAgentOptions(
        tools=[], setting_sources=[], strict_mcp_config=True, max_turns=1, cwd=str(DM_HOME), env=DM_ENV, model=model,
        system_prompt=system, output_format={"type": "json_schema", "schema": schema}, effort="low")
    out: dict[str, Any] | None = None
    async for msg in query(prompt=text, options=options):
        if isinstance(msg, ResultMessage):
            if msg.is_error:
                raise Failed(str(msg.result or getattr(msg, "errors", "") or "the SDK reported an error"))
            out = msg.structured_output
    if not isinstance(out, dict):
        raise Failed("the checker gave no structured answer")
    return out
