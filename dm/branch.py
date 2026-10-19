"""Going back in a game (owner, 2026-10-17): the player can send one of their earlier lines again, as it was or
changed, and the game goes on from there in a new save (a fork; the old save is left as it was); and the DM's latest
reply can be edited, and the DM reads the edited version from then on.

Before each of the player's lines the game keeps a snapshot of what changes in play (sheet, companions, fight, clock)
and where the DM's conversation stood. The notebook isn't kept: it's built again from the DM's write_lore calls,
which the transcript keeps."""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any

from dm import lore as notebook
from dm import mechanics as m

# The DM's conversation in Claude Code lives in a session file (dm/sdk.py); a fork starts there.
PROJECTS = Path.home() / ".claude" / "projects"


def session_file(cwd: str, session_id: str) -> Path:
    return PROJECTS / re.sub(r"[^A-Za-z0-9]", "-", cwd) / f"{session_id}.jsonl"


def last_entry(cwd: str, session_id: str | None) -> str | None:
    """The id of the session file's last entry: a fork from it carries the conversation up to this point."""
    if not session_id:
        return None
    try:
        lines = session_file(cwd, session_id).read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    for line in reversed(lines):
        try:
            if u := json.loads(line).get("uuid"):
                return u
        except ValueError:
            continue
    return None


def snapshot(game: Any) -> dict[str, Any]:
    """The game just before the player's next line."""
    return {"turn": notebook.now(game.transcript) + 1, "t": len(game.transcript), "story": len(game.story),
            "sheet": copy.deepcopy(game.sheet), "companions": copy.deepcopy(game.companions),
            "fight": copy.deepcopy(game.fight), "clock": copy.deepcopy(game.clock),
            "messages": len(game.messages), "session_id": game.session_id,
            "at": last_entry(game.cwd, game.session_id) if game.backend == "sdk" else None}


def lines(game: Any) -> list[tuple[int, str]]:
    """(turn, text) of each line the player can go back to."""
    return [(s["turn"], game.transcript[s["t"]]["text"]) for s in game.snapshots
            if s["t"] < len(game.transcript) and game.transcript[s["t"]]["kind"] == "player"]


def rebuilt_lore(transcript: list[dict[str, Any]]) -> dict[str, Any]:
    lore = notebook.new()
    for i, e in enumerate(transcript):
        if e["kind"] == "call" and e.get("tool") == "write_lore":
            try:
                lore, _ = notebook.write(lore, e["input"], notebook.now(transcript[:i]))
            except m.Refused:
                pass
    return lore


def fork_data(game: Any, turn: int) -> dict[str, Any]:
    """A save for the game as it was just before the player's line of `turn`, to go on from there. Raises
    LookupError if there's no snapshot for that turn."""
    s = next((s for s in game.snapshots if s["turn"] == turn), None)
    if s is None:
        raise LookupError(f"there's no going back to turn {turn}: the game keeps a snapshot from each of your lines "
                          f"since this feature came in (turns {', '.join(str(t) for t, _ in lines(game)) or 'none yet'})")
    transcript = copy.deepcopy(game.transcript[:s["t"]])
    data: dict[str, Any] = {
        "sheet": s["sheet"], "companions": s["companions"], "fight": s["fight"], "clock": s["clock"],
        "model": game.model, "transcript": transcript, "lore": rebuilt_lore(transcript), "backend": game.backend,
        "story": copy.deepcopy(game.story[:s["story"]]),
        "snapshots": [x for x in game.snapshots if x["turn"] < turn]}
    if game.backend == "sdk":
        data |= {"session_id": s["session_id"], "fork_at": s["at"], "cwd": game.cwd}
    elif s["story"] == len(game.story):  # no cut since: the conversation then was the start of this one
        data["messages"] = copy.deepcopy(game.messages[:s["messages"]])
    else:  # cut since: that conversation is gone; a new one opens with the turns up to here (play.so_far)
        data["messages"], data["rebuild"] = [], True
    return data


# ---------- editing the DM's reply ----------

def last_reply(game: Any) -> list[int]:
    """Where the DM's latest reply is in the transcript (its shown pieces), or [] if there's none since the
    player's last line."""
    start = max((i for i, e in enumerate(game.transcript) if e["kind"] == "player"), default=-1)
    return [i for i in range(start + 1, len(game.transcript)) if game.transcript[i]["kind"] == "dm"]


def replace_text(content: Any, old: str, new: str) -> tuple[Any, bool]:
    """A message's content with `old` replaced by `new` in its text. A text block left empty is dropped, unless it's
    the only block."""
    if isinstance(content, str):
        return (content.replace(old, new), True) if old in content else (content, False)
    out, hit = [], False
    for b in content:
        if isinstance(b, dict) and b.get("type") == "text" and old in b.get("text", ""):
            hit = True
            b = {**b, "text": b["text"].replace(old, new)}
            if not b["text"].strip():
                continue
        elif (isinstance(b, dict) and b.get("type") == "tool_use" and str(b.get("name", "")).endswith("reply")
              and old in str((b.get("input") or {}).get("text", ""))):  # the reply tool (dm/play.py)
            hit = True
            b = {**b, "input": {**b["input"], "text": b["input"]["text"].replace(old, new) or "(no reply)"}}
        elif isinstance(b, dict) and b.get("type") == "tool_result" and isinstance(b.get("content"), list):
            inner, h = replace_text(b["content"], old, new)
            if h:
                b, hit = {**b, "content": inner}, True
        out.append(b)
    if hit and not out:
        out = [{"type": "text", "text": "(no reply)"}]
    return out, hit


def edit_conversation(game: Any, pairs: list[tuple[str, str]]) -> None:
    """Each old text replaced with its new one wherever it is in the DM's conversation now: its reply, or a
    conversation opened after a cut with that turn in it word for word."""
    if game.backend == "sdk":
        if not game.session_id:
            return
        f = session_file(game.cwd, game.session_id)
        out = []
        for line in f.read_text(encoding="utf-8").splitlines():
            try:
                e = json.loads(line)
            except ValueError:
                out.append(line)
                continue
            msg = e.get("message")
            if isinstance(msg, dict) and "content" in msg:
                for old, new in pairs:
                    msg["content"], hit = replace_text(msg["content"], old, new)
                    if hit:
                        line = json.dumps(e, ensure_ascii=False)
            out.append(line)
        f.write_text("\n".join(out) + "\n", encoding="utf-8")
    else:
        for msg in game.messages:
            for old, new in pairs:
                msg["content"], _ = replace_text(msg["content"], old, new)


def edit_transcript(game: Any, text: str, why: str = "edited by the player") -> list[tuple[str, str]]:
    """The DM's latest reply becomes `text`. Returns (old, new) for each piece, for edit_conversation. Raises
    LookupError if there's no reply to edit."""
    at = last_reply(game)
    if not at:
        raise LookupError("there's no reply from the DM since your last line to edit")
    text = text.strip()
    if not text:
        raise LookupError("the edited reply is empty")
    old = [game.transcript[i]["text"] for i in at]
    pairs = [(old[0], text)] + [(o, "") for o in old[1:]]
    for i in reversed(at[1:]):
        del game.transcript[i]
    game.transcript[at[0]] = {"kind": "dm", "text": text}
    game.transcript.insert(at[0], {"kind": "edited", "text": "\n\n".join(old), "why": why})  # kept, never shown
    return pairs


# ---------- the closing status line (autoloop, 2026-10-17) ----------
# bard2 came to end nearly every reply on a read-out of the sheet ("You have 17 of 17 hit points, three slots, three
# Bardic Inspirations ..."): 48 of 188 replies, against 1 in each of the other two games. The DM reads its own past
# replies, so the habit fed itself, and no instruction wording broke it (A/B, 18-20 of 24 in every arm). The sentence
# is taken out of the reply, and out of the DM's conversation, when it's in the closing paragraph and the player
# didn't ask about their sheet.
STAT_LINE = re.compile(r"(?:^|(?<=[.!?\"”] ))You have \d+ of \d+ hit points\b[^.!?]*[.!?]\s*")
ASKED = re.compile(r"\bDM:|hit points?|\bHP\b|\bslots?\b|\bsheet\b", re.IGNORECASE)


def without_stat_line(reply: str, player_line: str) -> tuple[str, str]:
    """The reply with a read-out of the sheet taken out of its last paragraph, and what was taken out ("" if
    nothing)."""
    if ASKED.search(player_line or ""):
        return reply, ""
    paras = reply.rstrip().split("\n\n")
    hit = STAT_LINE.search(paras[-1])
    if not hit:
        return reply, ""
    last = (paras[-1][:hit.start()] + paras[-1][hit.end():]).strip()
    last = re.sub(r"  +", " ", last)
    paras = paras[:-1] + ([last] if last else [])
    out = "\n\n".join(paras).strip()
    return (out, hit.group(0).strip()) if out else (reply, "")
