"""Plain player-facing wording for world setup and character creation (engine/dm/text/setup.yaml).

The rules data words its seed questions and creation options for rules readers ("the engine rolls every question's
oracle"). The player reads this table instead, keyed by the same ids, so recorded answers, events and Interpret's
options are untouched. A missing entry falls back to the rules' own (sanitized) text; `missing_entries` lists them.

    seed_header(1)                         # "World 1 of 14 · What went wrong in this land"
    question_prompt("ws.q.wound", ask)     # the plain question, else `ask`
    option_label("ws.q.wound", "plague", rules_text)
    footer("pick", "to let the dice decide")
    pause_block(header, prompt, lines, choices, foot)   # the block text a pause shows
    read_answer(ctx, message, rec, classes=..., cards=...)  # Interpret over plain labels plus the rules' text
"""

from __future__ import annotations

import functools
import re
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import yaml

from engine.dm.context import TurnContext
from engine.dm.response import Choice
from engine.dm.roles.interpret import InterpretResult, direct_choice, interpret
from engine.dm.schemas import SPECIAL_CHOICES
from engine.store.events import PauseRecord

TEXT_PATH = Path(__file__).with_name("text") / "setup.yaml"


@functools.cache
def table() -> dict[str, Any]:
    """The whole wording table (read once)."""
    with TEXT_PATH.open(encoding="utf-8") as f:
        return dict(yaml.safe_load(f))


def _get(*path: Any) -> Any:
    node: Any = table()
    for key in path:
        if not isinstance(node, dict):
            return None
        node = node[key] if key in node else node.get(str(key))
    return node


def footer(kind: str, enter: str) -> str:
    """The one line saying how to answer: kind pick | pick_many | number | words."""
    return str(_get("footer", kind) or _get("footer", "pick")).format(enter=enter)


def dice() -> str:
    return str(_get("footer", "dice"))


# ------------------------------------------------------------------------------------------- seed


def seed(*path: Any) -> Any:
    """A seed entry by path (e.g. seed("mode", "prompt")), or None."""
    return _get("seed", *path)


def seed_header(n: int, fallback: str = "") -> str:
    return str(seed("header")).format(n=n, title=step_title(n, fallback))


def step_title(n: int, fallback: str = "") -> str:
    return str(_get("seed", "steps", n) or fallback)


def question(qid: str) -> dict[str, Any]:
    return dict(seed("questions", qid) or {})


def question_prompt(qid: str, fallback: str) -> str:
    return str(question(qid).get("prompt") or fallback)


def question_pick(qid: str, fallback: str) -> str:
    return str(question(qid).get("pick") or fallback)


def question_what(qid: str) -> str:
    """The question's name in "Re-roll ..." and "You chose ..." ("the weather")."""
    return str(question(qid).get("what") or qid.rsplit(".", 1)[-1].replace("_", " "))


def option_label(qid: str, oid: str, fallback: str, tier: str | None = None) -> str:
    q = question(qid)
    opts = (q.get("options_by_tier") or {}).get(tier or "village") if "options_by_tier" in q else q.get("options")
    return str((opts or {}).get(oid) or fallback)


def option_short(qid: str, oid: str) -> str | None:
    """A recap sentence for an option, when the table gives one ("Magic is rare.")."""
    v = (question(qid).get("short") or {}).get(oid)
    return None if v is None else str(v)


# ------------------------------------------------------------------------------------------- creation


def creation(*path: Any) -> Any:
    """A creation entry by path (e.g. creation("sheet")), or None."""
    return _get("creation", *path)


def block(bid: str) -> dict[str, Any]:
    return dict(_get("creation", "blocks", bid) or {})


def block_option(bid: str, oid: str, fallback: str) -> str:
    return str((block(bid).get("options") or {}).get(oid) or fallback)


def creation_header(n: int | None, total: int | None, title: str) -> str:
    if n is None or total is None:
        return str(_get("creation", "header_plain")).format(title=title)
    return str(_get("creation", "header")).format(n=n, total=total, title=title)


def name_of(label: str) -> str:
    """An option's name: its label before the first ": ", " — ", ", ", " (" or ". "
    ("Quick start, which takes five questions" -> "Quick start")."""
    for sep in (": ", " — ", ", ", " (", ". "):
        label = label.split(sep)[0]
    return label.strip().rstrip(".")


# ------------------------------------------------------------------------------------------- blocks


def letter(i: int) -> str:
    return chr(97 + i) if i < 26 else str(i + 1)


def pause_block(header: str, prompt: str, lines: Sequence[str], choices: Sequence[Choice], foot: str) -> str:
    """Header, the question, any lines, the options lettered (the terminal numbers them in place), the footer."""
    out = [header] + [f"  {x}" for x in (prompt, *lines) if x]
    out += [f"  ({letter(i)}) {c.label}" for i, c in enumerate(choices)]
    if foot:
        out.append(f"  {foot}")
    return "\n".join(out)


def originals(plain: Sequence[Choice], rules_labels: dict[str, str]) -> dict[str, str]:
    """{option id: the rules' label} where it differs from the plain one (kept for Interpret and "details")."""
    by_id = {c.id: c.label for c in plain}
    return {k: v for k, v in rules_labels.items() if k in by_id and v and v != by_id[k]}


# ------------------------------------------------------------------------------------------- reading answers


def read_answer(ctx: TurnContext, message: str, rec: PauseRecord, *, tag: str, classes: Sequence[str] = (),
                cards: Sequence[str] = ("12.16.2",), multi: bool = False,
                lines_and_veils: bool = False) -> InterpretResult:  # rule: 12.16.2
    """The player's answer to a seed or creation pause: a number, letter, id or exact plain label directly; else
    one Interpret call that sees each option's plain label with the rules' wording beside it."""
    shown = [Choice(id=c["id"], label=c.get("label", c["id"])) for c in rec.choices]
    hit = direct_choice(message, shown, multi=multi)
    if hit:
        return InterpretResult(choice=hit[0], picks=[h for h in hit if h not in SPECIAL_CHOICES], direct=True)
    orig: dict[str, str] = dict(rec.detail.get("orig") or {})
    both = [Choice(id=c.id, label=f"{c.label} ({orig[c.id]})" if orig.get(c.id) else c.label) for c in shown]
    own = [str(b.get("text", "")) for b in rec.detail.get("blocks", [])][-1:]  # the pause's own block
    lead = [ln for ln in "\n".join(own).split("\n") if ln.strip() and not re.match(r"\s*\([a-z0-9]+\) ", ln)]
    text = "\n".join([f"{tag} {lead[0] if lead else ''}".rstrip(), *lead[1:],
                      *[f"  ({letter(i)}) {c.label}" for i, c in enumerate(both)]])
    return interpret(ctx, message, choices=both, block=text, classes=classes, cards=cards, multi=multi,
                     lines_and_veils=lines_and_veils)


__all__ = ["block", "block_option", "creation", "creation_header", "dice", "footer", "letter", "name_of", "option_label",
           "option_short", "originals", "pause_block", "question", "question_pick", "question_prompt",
           "question_what", "read_answer", "seed", "seed_header", "step_title", "table"]
