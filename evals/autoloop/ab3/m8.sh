#!/bin/sh
# 2C looked like a winner at 4 runs: 4 more runs per round for base and 2C.
py() { PYTHONPATH=. .venv/Scripts/python evals/autoloop/replay.py "$@"; }
for g in "cleric2 70,114" "bard2 70,101" "barbarian2 97,120"; do set -- $g
  py $1 $2 4 evals/autoloop/ab3/M8/base-$1.json &
  PROMPT_MD=evals/autoloop/ab3/arms/2C.md py $1 $2 4 evals/autoloop/ab3/M8/2C-$1.json &
  wait; echo "M8 $1 done $(date +%T)"
done
