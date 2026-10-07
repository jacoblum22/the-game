"""Read GEMINI_API_KEY from the environment or a .env file at the repo root (no extra dependency)."""

from __future__ import annotations

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def read_env_file(path: Path | None = None) -> dict[str, str]:
    path = path or REPO_ROOT / ".env"
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip().removeprefix("export ").strip()
        values[key] = value.strip().strip('"').strip("'")
    return values


def get_key(name: str = "GEMINI_API_KEY") -> str | None:
    return os.environ.get(name) or read_env_file().get(name) or None
