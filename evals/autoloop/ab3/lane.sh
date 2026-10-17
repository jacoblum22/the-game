#!/bin/sh
# One game's lane: menu set (M) and contradiction set (K), 4 runs each round.
g=$1; m=$2; k=$3
py() { PYTHONPATH=. .venv/Scripts/python evals/autoloop/replay.py "$@"; }
py $g $m 4 evals/autoloop/ab3/M/base-$g.json; echo "M base $g done $(date +%T)"
PROMPT_MD=evals/autoloop/ab3/arms/2C.md py $g $m 4 evals/autoloop/ab3/M/2C-$g.json; echo "M 2C $g done $(date +%T)"
PROMPT_MD=evals/autoloop/ab3/arms/2D.md py $g $m 4 evals/autoloop/ab3/M/2D-$g.json; echo "M 2D $g done $(date +%T)"
py $g $k 4 evals/autoloop/ab3/K/base-$g.json; echo "K base $g done $(date +%T)"
DM_SAID=2 py $g $k 4 evals/autoloop/ab3/K/said2-$g.json; echo "K said2 $g done $(date +%T)"
DM_SAID=4 py $g $k 4 evals/autoloop/ab3/K/said4-$g.json; echo "K said4 $g done $(date +%T)"
