"""Rules data for the generators: one helper, so the switch to the shared loader is a one-line change.

`load(name)` returns the parsed `rules/data/<name>` as plain (mutable) Python data, cached per process.
Callers must not mutate it; records they write copy what they take. When `engine.data.loader` is adopted,
`_load_raw` becomes `return thaw(load_rules().doc(name))` (the generators copy data into their output records,
and the parity tests compare those records to the reference scripts' plain dicts and lists).
"""

from __future__ import annotations

import copy
import functools
from pathlib import Path
from typing import Any

import yaml

RULES_DATA = Path(__file__).resolve().parents[2] / "rules" / "data"

# TODO(RULES_I091): rules/data/world_turn.yaml line 1543 does not parse (an unquoted ': ' inside a plain scalar,
# "[revision: I-091]"). The world seed reads that file's situation templates, hooks and rumor-truth table, so
# until rules/ quotes the scalar this one text fix is applied, and only when the raw file fails to parse.
_BAD = ("- source: a faction's commission (paid at 08.8.8's job fee for its band, economy.yaml#job_fees)"
        " [revision: I-091]")
_PATCHES: dict[str, tuple[tuple[str, str], ...]] = {
    "world_turn.yaml": ((_BAD, '- source: "' + _BAD[len("- source: "):] + '"'),),
}


def parse(name: str, text: str) -> Any:
    """Parse one data file's text, applying its known text fix only if the raw text does not parse."""
    try:
        return yaml.safe_load(text)
    except yaml.YAMLError:
        if name not in _PATCHES:
            raise
        for old, new in _PATCHES[name]:
            text = text.replace(old, new)
        return yaml.safe_load(text)


@functools.cache
def _load_raw(name: str) -> Any:
    return parse(name, (RULES_DATA / name).read_text(encoding="utf-8"))


def load(name: str) -> Any:
    """`rules/data/<name>` as plain data (shared, cached: do not mutate)."""
    return _load_raw(name)


def fresh(name: str) -> Any:
    """A private deep copy of `rules/data/<name>`, for callers that must mutate."""
    return copy.deepcopy(_load_raw(name))
