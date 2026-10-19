#!/bin/sh
# More fight starts (the first lanes' rounds before ~80 had no session to branch from).
A=evals/autoloop/ab7
lane() { g=$1; r=$2
  PYTHONPATH="$A/base;." .venv/Scripts/python evals/autoloop/replay.py $g $r 2 $A/base2-$g.json; echo "base $g done $(date +%T)"
  PYTHONPATH=. .venv/Scripts/python evals/autoloop/replay.py $g $r 2 $A/turns2-$g.json; echo "turns $g done $(date +%T)"; }
lane cleric2 120 > $A/lane2-cleric2.log 2>&1 &
lane barbarian2 94,139,164 > $A/lane2-barbarian2.log 2>&1 &
lane bard2 87,128 > $A/lane2-bard2.log 2>&1 &
wait
