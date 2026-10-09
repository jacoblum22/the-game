#!/usr/bin/env bash
# Regenerate derived rules files, validate, re-record replay, run the suite. Usage: regen_and_gate.sh [--no-suite]
set -u
cd "$(git rev-parse --show-toplevel)" || exit 1
export PYTHONUTF8=1
py -3.12 rules/_process/simulation/integration-assemble-appendix.py >/dev/null 2>&1 || echo "ASSEMBLE FAILED"
py -3.12 rules/_process/simulation/12-compile_anchors.py 2>&1 | tail -2
py -3.12 engine/build/compile_cards.py 2>&1 | tail -1
echo "validator problems: $(py -3.12 rules/_process/validate_ruleset.py 2>&1 | grep -cE '^(ERROR|WARN)')"
py -3.12 -m tests.replay.record_games 2>&1 | tail -1
git add -A rules engine/build/cards.json tests/replay
[ "${1:-}" = "--no-suite" ] || py -3.12 -m pytest -q -p no:cacheprovider 2>&1 | tail -3
