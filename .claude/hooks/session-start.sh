#!/bin/bash
# Installs Python deps so cloud sessions can run pytest, ruff, pyright and the rules validator.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-.}"
python3 -m pip install --quiet --disable-pip-version-check --root-user-action=ignore -r requirements-dev.txt
echo "session-start: Python deps installed (pytest, ruff, pyright, PyYAML, google-genai)"
