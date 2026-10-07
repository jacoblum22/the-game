"""Rules data for the generators: one helper, so the switch to the shared loader is a one-line change.

`load(name)` returns the parsed `rules/data/<name>` as plain (mutable) Python data, cached per process.
Callers must not mutate it; records they write copy what they take. When `engine.data.loader` is adopted,
`_load_raw` becomes `return thaw(load_rules().doc(name))` (the generators copy data into their output records,
and the parity tests compare those records to the reference scripts' plain dicts and lists).
"""

from __future__ import annotations

import copy
import functools
import hashlib
import os
import pickle
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


CACHE_DIR = Path(os.environ.get("THE_GAME_GEN_CACHE", Path(__file__).resolve().parent / "_cache"))
CACHE_FORMAT = 1


def _cache_path(name: str, digest: str) -> Path:
    return CACHE_DIR / f"{Path(name).stem}-{CACHE_FORMAT}-{digest[:24]}.pickle"


@functools.cache
def _load_raw(name: str) -> Any:
    """Parsed once per file version: the pure-Python YAML parse (~10 s for the seed's files) is pickled under
    engine/gen/_cache keyed by the sha256 of the file's text and its patches, like engine/data/loader's cache."""
    text = (RULES_DATA / name).read_text(encoding="utf-8")
    digest = hashlib.sha256((repr(_PATCHES.get(name, ())) + text).encode("utf-8")).hexdigest()
    cache = _cache_path(name, digest)
    if cache.exists():
        try:
            with cache.open("rb") as f:
                stored = pickle.load(f)
            if stored.get("hash") == digest:
                return stored["data"]
        except Exception:  # noqa: BLE001 - a bad cache is rebuilt, never trusted
            pass
    data = parse(name, text)
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        gi = CACHE_DIR / ".gitignore"
        if not gi.exists():
            gi.write_text("*\n", encoding="utf-8")
        tmp = cache.with_suffix(f".{os.getpid()}.tmp")
        with tmp.open("wb") as f:
            pickle.dump({"hash": digest, "data": data}, f, protocol=5)
        tmp.replace(cache)
        for stale in CACHE_DIR.glob(f"{Path(name).stem}-{CACHE_FORMAT}-*.pickle"):
            if stale != cache:
                stale.unlink(missing_ok=True)
    except OSError:
        pass  # a read-only tree: parse every time
    return data


def load(name: str) -> Any:
    """`rules/data/<name>` as plain data (shared, cached: do not mutate)."""
    return _load_raw(name)


def fresh(name: str) -> Any:
    """A private deep copy of `rules/data/<name>`, for callers that must mutate."""
    return copy.deepcopy(_load_raw(name))
