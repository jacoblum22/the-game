"""Turning engine responses into terminal text (contracts/cli.md "Output layout").

    print(render_response(resp, width=80))   # fiction, then the OOF blocks in order, then the pause's choices

Plain text only: no colour codes. `ascii_safe` swaps the few typographic characters the engine uses when the
output stream cannot encode them.
"""

from __future__ import annotations

import re
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


_ITEM = re.compile(r"^\s*(?:\(([a-z]|\d{1,2})\)\s|\d{1,2}[.)]\s|[-•*·]\s)")
_LABEL = re.compile(r"^\s*\[[A-Z][^\]]{0,40}\]")
_FIELD = re.compile(r"^\s*[\w'()+/ -]{1,24}:(\s|$)")
_TERMINAL = ".!?:;)]\"”"
_HARD_WRAP = 92  # the engine's own text was hard-wrapped at ~100 source columns


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip())


def _continues(prev: str, line: str) -> bool:
    """`line` is a hard-wrapped continuation of `prev` (not a list item, label, field or new paragraph)."""
    p, s = prev.rstrip(), line.strip()
    if not p.strip() or not s or p[-1] in _TERMINAL:
        return False
    if _ITEM.match(line) or _LABEL.match(line) or _FIELD.match(line):
        return False
    if _indent(line) >= 4 and _indent(line) > _indent(prev) + 2:  # a hanging continuation under a label or item
        return True
    return len(p) >= _HARD_WRAP and s[0].islower() and not _FIELD.match(prev)  # `name: value` lines stand alone


def reflow(text: str) -> str:
    """Join hard-wrapped lines back into their paragraph (blank lines, list items, labels and fields stay)."""
    out: list[str] = []
    for line in text.split("\n"):
        if out and _continues(out[-1], line):
            out[-1] = out[-1].rstrip() + " " + line.strip()
        else:
            out.append(line)
    return "\n".join(out)


def wrap(text: str, width: int) -> str:
    """Reflow, then wrap each line to `width`, keeping blank lines and each line's own indentation for its
    continuation (a list item's continuation hangs under its text)."""
    out: list[str] = []
    for line in reflow(text).splitlines():
        if len(line) <= width or not line.strip():
            out.append(line.rstrip())
            continue
        indent = line[: len(line) - len(line.lstrip())]
        item = re.match(r"\s*(?:\d{1,2}\)|\([a-z]\)|[-•]|\[[A-Z][^\]]{0,30}\])\s+", line)
        hang = " " * item.end() if item else (indent + "  " if indent else "")
        out.append(textwrap.fill(line.strip(), width=width, initial_indent=indent, subsequent_indent=hang,
                                 break_on_hyphens=False))
    return "\n".join(out)


# ------------------------------------------------------------------------------------------- choices


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def _same(item: str, label: str) -> bool:
    a, b = _norm(item), _norm(label)
    return bool(a and b) and (a == b or a.startswith(b) or b.startswith(a))


_OPT = re.compile(r"^(\s*)\(([a-z]|\d{1,2})\)\s+(.*)$")  # `(a) option` or `(2) option`
_OPT_MARK = re.compile(r"^(\s*)\((?:[a-z]|\d{1,2})\)\s+")


def _bare(label: str) -> str:
    """A choice label without a leading `(2) ` of its own (the renderer numbers the choices)."""
    return re.sub(r"^\s*\((?:[a-z]|\d{1,2})\)\s+", "", label)


def _numbered_line(line: str, n: int) -> bool:
    """`  1) Commit   2) Change approach ...`: an inline numbered listing of the pause's n choices."""
    nums = [int(x) for x in re.findall(r"(?:^|\s)(\d{1,2})\)\s", line)]
    return line.strip().startswith("1)") and nums == list(range(1, n + 1))


def strip_listing(text: str, pause: Any, *, in_place: bool = False) -> str:
    """The block without its own listing of the pause's choices (the renderer prints them once, numbered): an
    inline numbered line, or a run of lettered `(a) ...` items matching the choices. Lettered items that are not
    the choices (sub-questions) become plain bullets, so letters never compete with the numbers. `in_place`: the
    matching lettered run becomes the numbered choices where it stands (lines after it, such as a "how to
    answer" line, stay after it)."""
    labels = [c.label for c in pause.choices]
    lines = text.split("\n")
    lines = [ln for ln in lines if not _numbered_line(ln, len(labels))]
    out: list[str] = []
    i = 0
    while i < len(lines):
        m = _OPT.match(lines[i])
        if not m:
            out.append(lines[i])
            i += 1
            continue
        group: list[tuple[int, str, list[str]]] = []  # (indent, text, raw lines)
        while i < len(lines) and (m := _OPT.match(lines[i])):
            raw, text_, ind = [lines[i]], m.group(3), len(m.group(1))
            i += 1
            while i < len(lines) and lines[i].strip() and _indent(lines[i]) > ind and not _ITEM.match(lines[i]):
                raw.append(lines[i])
                text_ += " " + lines[i].strip()
                i += 1
            group.append((ind, text_, raw))
        if len(group) == len(labels) and all(_same(t, _bare(lab)) for (_, t, _), lab in zip(group, labels,
                                                                                            strict=True)):
            if in_place:
                out.append(choice_lines(pause, indent=" " * group[0][0]))
            continue  # the choices themselves: printed once (here, or below)
        for _ind, _, raw in group:
            out.append(_OPT_MARK.sub(r"\1- ", raw[0]))
            out += raw[1:]
    return "\n".join(out)


def choice_lines(pause: Any, indent: str = "  ") -> str:
    """The pause's choices, one per line: `  1) Commit`."""
    return "\n".join(f"{indent}{i}) {_bare(c.label)}" for i, c in enumerate(pause.choices, 1))


def short_label(label: str) -> str:
    """The option's name, not its whole description ("Withdraw (nothing is spent)" -> "Withdraw")."""
    for sep in (": ", " — ", ", ", " (", ". "):
        label = label.split(sep)[0]
    return label.strip().rstrip(".")


OFFER_HINT = "Type 1 to commit, or a number from the list."
PICK_HINT = "Type a number from the list."
# pause menus where a silent default costs the player: the rules give none for Enter (12.15; P-044, P-089)
WAITING_PAUSES = frozenset({"offer", "near_miss", "redirect", "last_chance"})

# 12.15.2's one menu convention for every play pause: Enter is the labelled default and always printed, letters
# pick the alternatives, `?` explains a glossary word (14.2.7). Enter never backs out (P-044).
KEYS = {"commit": "d", "go_big": "b", "play_safe": "s", "change": "c", "withdraw": "w"}
SHOW_AGAIN = "Show this again"


def menu_keys(pause: Any) -> dict[str, str]:  # rule: 12.15.2
    """{letter: choice id}: the OFFER's fixed letters, then the first free letter for every other choice."""
    out: dict[str, str] = {}
    for c in pause.choices:
        k = KEYS.get(c.id)
        if k is None or k in out:
            k = next(x for x in "abcdefghijklmnopqrstuvwxyz" if x not in out and x not in KEYS.values())
        out[k] = c.id
    return out


def enter_choice(pause: Any) -> str | None:  # rule: 12.15.2
    """The choice Enter takes, or None (Enter shows the pause again). An OFFER: Do it, except on a Dire, lethal or
    long-shot frame; the other waiting pauses (near miss, redirect, last chance): nothing is taken silently."""
    ids = [c.id for c in pause.choices]
    if ids and ids[0] == "commit":
        o = getattr(pause, "frame_summary", None) or {}
        return None if (o.get("stakes") == "dire" or o.get("lethal") or o.get("long_shot")) else "commit"
    if pause.kind in WAITING_PAUSES:
        return None
    return pause.default_choice if pause.default_choice in ids else None


def menu_line(pause: Any) -> str:  # rule: 12.15.2
    """`[Enter] Do it   [b] Go big   [s] Play it safe   [c] Another way   [w] Back off   [?] Explain`."""
    enter = enter_choice(pause)
    labels = {c.id: _bare(c.label) for c in pause.choices}
    first = f"[Enter] {short_label(labels[enter]) if enter else SHOW_AGAIN}"
    rest = [f"[{k}] {labels[i]}" for k, i in menu_keys(pause).items() if i != enter]
    return "   ".join([first, *rest, "[?] Explain"])


def offer_waits(pause: Any) -> bool:
    """An OFFER, NEAR MISS, REDIRECT or last-chance menu: an empty line takes nothing (P-044: Enter-for-Withdraw
    silently dropped the attempt; P-089: Enter at a near miss silently let it fail)."""
    return bool(pause.choices) and (pause.choices[0].id == "commit" or pause.kind in WAITING_PAUSES)


def enter_hint(pause: Any) -> str:
    """`Type a number, or press Enter for Moving on.` when the pause has a default among its choices; a menu
    that waits names no Enter default (OFFER_HINT / PICK_HINT)."""
    if offer_waits(pause):
        return OFFER_HINT if pause.choices[0].id == "commit" else PICK_HINT
    ids = [c.id for c in pause.choices]
    if pause.default_choice not in ids:
        return ""
    return f"Type a number, or press Enter for {short_label(pause.choices[ids.index(pause.default_choice)].label)}."


def _play_menu(resp: Any, width: int) -> str:
    """Fiction, the blocks (without any listing of the choices of their own), the prompt when no block carries it,
    then the menu line (12.15.2)."""
    pause = resp.pause
    parts = [resp.fiction.strip()] if resp.fiction else []
    parts += [t.strip() for b in resp.oof_blocks if (t := strip_listing(b.text, pause)).strip()]
    shown = "\n\n".join(parts)
    if pause.prompt and pause.prompt.strip() not in shown:
        parts.append(pause.prompt.strip())
    parts.append(menu_line(pause))
    return "\n\n".join(wrap(p, width) for p in parts)


def render_response(resp: Any, width: int) -> str:
    """Fiction paragraphs, then the OOF blocks in the engine's order, then the pause prompt (when no block shows
    it already) and its choices, numbered, one per line. Any listing of the choices inside a block (lettered
    options, an inline numbered line) is left out, so each choice is shown exactly once."""
    pause = resp.pause
    choices = bool(pause is not None and pause.choices)
    if choices and resp.phase == "play":  # 12.15.2: one menu line for every play pause
        return _play_menu(resp, width)
    parts: list[str] = []
    if resp.fiction:
        parts.append(resp.fiction.strip())
    for b in resp.oof_blocks:
        t = strip_listing(b.text, pause) if choices else b.text
        if t.strip():
            parts.append(t.strip())
    if pause is not None:
        shown = "\n\n".join(parts)
        asked = not pause.prompt or pause.prompt.strip() in shown
        if choices and asked and resp.oof_blocks:  # the question is in its block: number the choices there
            last = resp.oof_blocks[-1].text
            placed = strip_listing(last, pause, in_place=True)
            if placed != strip_listing(last, pause) and parts and parts[-1] == strip_listing(last, pause).strip():
                parts[-1] = placed.strip()
                hint = enter_hint(pause) if resp.phase == "play" else ""  # the setup menus carry their own
                return "\n\n".join(wrap(p, width) for p in [*parts, hint] if p)
        if not asked:
            parts.append(pause.prompt.strip())
        if choices:
            parts.append(choice_lines(pause))
            if resp.phase == "play" and enter_hint(pause):
                parts.append(enter_hint(pause))
    return "\n\n".join(wrap(p, width) for p in parts)
