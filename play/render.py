"""Turning engine responses into terminal text (contracts/cli.md "Output layout").

    print(render_response(resp, width=80))   # fiction, then the OOF blocks in order, then the pause's choices

Plain text only: no colour codes. `ascii_safe` swaps the few typographic characters the engine uses when the
output stream cannot encode them.
"""

from __future__ import annotations

import shutil
import textwrap
from typing import Any

_ASCII = {"—": "--", "–": "-", "·": "-", "‘": "'", "’": "'", "“": '"', "”": '"',
          "…": "...", "→": "->", "≥": ">=", "≤": "<=", "×": "x"}


def terminal_width(default: int = 80) -> int:
    """The terminal's width, clamped to a readable 40..100 columns."""
    return max(40, min(100, shutil.get_terminal_size((default, 24)).columns))


def ascii_safe(text: str, encoding: str | None) -> str:
    """`text` unchanged if `encoding` can carry it, else with typographic characters spelled in ASCII."""
    if not encoding:
        return text
    try:
        text.encode(encoding)
        return text
    except (UnicodeEncodeError, LookupError):
        for k, v in _ASCII.items():
            text = text.replace(k, v)
        return text.encode(encoding, errors="replace").decode(encoding, errors="replace")


def wrap(text: str, width: int) -> str:
    """Wrap each line to `width`, keeping blank lines and each line's own indentation for its continuation."""
    out: list[str] = []
    for line in text.splitlines():
        if len(line) <= width or not line.strip():
            out.append(line.rstrip())
            continue
        indent = line[: len(line) - len(line.lstrip())]
        hang = indent + "  " if indent else ""
        out.append(textwrap.fill(line.strip(), width=width, initial_indent=indent, subsequent_indent=hang,
                                 break_on_hyphens=False))
    return "\n".join(out)


def choices_line(pause: Any) -> str:
    """`  1) Commit   2) Change approach ...` for the pause's choices, in order."""
    return "  " + "   ".join(f"{i}) {c.label}" for i, c in enumerate(pause.choices, 1))


def _lists_choices(text: str, pause: Any) -> bool:
    return all(f"{i}) {c.label}" in text for i, c in enumerate(pause.choices, 1))


def render_response(resp: Any, width: int) -> str:
    """Fiction paragraphs, then the OOF blocks in the engine's order, then the pause prompt and its numbered
    choices (left out when the last block already lists them, as the [OFFER] block does)."""
    parts: list[str] = []
    if resp.fiction:
        parts.append(resp.fiction.strip())
    parts += [b.text.strip() for b in resp.oof_blocks if b.text.strip()]
    pause = resp.pause
    if pause is not None:
        shown = "\n\n".join(parts)
        if pause.prompt and pause.prompt.strip() not in shown:
            parts.append(pause.prompt.strip())
        if pause.choices and not _lists_choices(parts[-1] if parts else "", pause):
            parts.append(choices_line(pause))
    return "\n\n".join(wrap(p, width) for p in parts)
