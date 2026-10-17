#!/bin/sh
# Block 3 A/B on bard2's closing status lines: base (2C), pre2C (block 2's prompt), 5A, 5B; 4 runs x 6 rounds.
py() { PYTHONPATH=. .venv/Scripts/python evals/autoloop/replay.py "$@"; }
R=126,146,156,161,166,176; A=evals/autoloop/ab4
{ py bard2 $R 4 $A/S/base-bard2.json; echo "base done $(date +%T)"
  PROMPT_MD=$A/arms/pre2C.md py bard2 $R 4 $A/S/pre2C-bard2.json; echo "pre2C done $(date +%T)"; } &
{ PROMPT_MD=$A/arms/5A.md py bard2 $R 4 $A/S/5A-bard2.json; echo "5A done $(date +%T)"
  PROMPT_MD=$A/arms/5B.md py bard2 $R 4 $A/S/5B-bard2.json; echo "5B done $(date +%T)"; } &
wait
