"""Convert a save from the Agent SDK days to the API: the DM's conversation moves from Claude Code's session file
into the save, as API messages. The old save is kept beside it as <name>.json.sdk (not .json, so it isn't listed as a save).

    py -3.12 -m dm.convert saves/<file>.json

Claude Code's own additions (the environment, the date, the account) are left out: only the messages go across.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path
from typing import Any


def messages_from_session(path: Path) -> list[dict[str, Any]]:
    """Claude Code writes one line per content block; an assistant message's blocks share its id."""
    out: list[dict[str, Any]] = []
    last_id = None
    for line in path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if row.get("type") not in ("user", "assistant") or row.get("isSidechain"):
            continue
        msg = row["message"]
        content = msg["content"]
        if isinstance(content, str):
            content = [{"type": "text", "text": content}]
        for b in content:
            if b.get("type") == "tool_use":
                b["name"] = b["name"].removeprefix("mcp__dm__")
        new_assistant = msg["role"] == "assistant" and msg.get("id") != last_id
        if out and out[-1]["role"] == msg["role"] and not new_assistant:
            out[-1]["content"] += content
        elif out and out[-1]["role"] == msg["role"]:
            raise SystemExit(f"two assistant messages in a row in {path}")
        else:
            out.append({"role": msg["role"], "content": content})
        last_id = msg.get("id") if msg["role"] == "assistant" else None
    # every tool use answered in the next message
    for i, mm in enumerate(out):
        uses = {b["id"] for b in mm["content"] if b["type"] == "tool_use"}
        if uses and i + 1 < len(out):
            answered = {b["tool_use_id"] for b in out[i + 1]["content"] if b["type"] == "tool_result"}
            if uses - answered:
                raise SystemExit(f"message {i}: tool uses without results: {uses - answered}")
    return out


def main() -> None:
    save = Path(sys.argv[1])
    data = json.loads(save.read_text(encoding="utf-8"))
    if "messages" in data:
        raise SystemExit("already converted")
    sid = data.get("session_id") or ""
    found = list((Path.home() / ".claude" / "projects").glob(f"*/{sid}.jsonl")) if sid else []
    if len(found) != 1:
        raise SystemExit(f"can't find the DM's session file for {save} (session {sid!r})")
    messages = messages_from_session(found[0])
    shutil.copyfile(save, save.with_name(save.name + ".sdk"))
    data.pop("session_id")
    data.pop("cwd", None)
    data["messages"] = messages
    data["backend"] = "api"
    save.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"{save}: {len(messages)} messages from {found[0].name}; the old save is {save.name}.sdk")


if __name__ == "__main__":
    main()
