"""Role instructions: the stable first section of every model packet (contracts/model-calls.md, Packet order).

    text = load_prompt("reader")      # or load_prompt(Role.READER)

One Markdown file per role in this folder. The prompts explain the job, how to choose and what never to do;
the rules themselves arrive separately as the packet's loaded cards, and the schema's enums carry the legal
options. Keep each file within `WORD_BUDGET` (prompt caching makes this section a fixed per-call cost).
"""

from __future__ import annotations

from functools import cache
from pathlib import Path

from engine.llm.base import Role

PROMPT_DIR = Path(__file__).parent
ROLES: tuple[str, ...] = tuple(r.value for r in Role)
# checker: the diff audit (009 B); reader: + the typed intended change (spec 015, 01.2.7)
WORD_BUDGET: dict[str, int] = {r: 700 for r in ROLES} | {"narrator": 1000, "checker": 550, "reader": 1000}  # spec 020: the goal rule; the cards it replaces were ~10k tokens


@cache
def load_prompt(role: str) -> str:
    """The role's instructions, read once per process. Raises KeyError for an unknown role."""
    if role not in ROLES:
        raise KeyError(f"no prompt for role {role!r}; roles: {', '.join(ROLES)}")
    return (PROMPT_DIR / f"{Role(role).value}.md").read_text(encoding="utf-8").strip()
