#!/bin/sh
# creature_turns A/B (Jake, 2026-10-19): base (c28d3ff, the reply tool, before creature_turns; in ab7/base) vs turns
# (now), 2 runs on 3 rounds where a fight starts, in each long game.
A=evals/autoloop/ab7
lane() { g=$1; r=$2
  PYTHONPATH="$A/base;." .venv/Scripts/python evals/autoloop/replay.py $g $r 2 $A/base-$g.json; echo "base $g done $(date +%T)"
  PYTHONPATH=. .venv/Scripts/python evals/autoloop/replay.py $g $r 2 $A/turns-$g.json; echo "turns $g done $(date +%T)"; }
lane cleric2 18,62,95 > $A/lane-cleric2.log 2>&1 &
lane barbarian2 20,74,121 > $A/lane-barbarian2.log 2>&1 &
lane bard2 42,108,146 > $A/lane-bard2.log 2>&1 &
wait
