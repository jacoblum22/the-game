#!/bin/sh
# Reply and bookkeeping in one model call: base (the code before, from 8b69849, in ab6/base) vs one (now), 4 runs on
# 6 ordinary rounds, none mid-fight. P1 holds rounds from block 121-180, P2 from block 61-120.
A=evals/autoloop/ab6
lane() { g=$1; r=$2; p=$3
  PYTHONPATH="$A/base;." .venv/Scripts/python evals/autoloop/replay.py $g $r 4 $A/$p/base-$g.json; echo "base $g done $(date +%T)"
  PYTHONPATH=. .venv/Scripts/python evals/autoloop/replay.py $g $r 4 $A/$p/one-$g.json; echo "one $g done $(date +%T)"; }
{ lane cleric2 150 P1; lane cleric2 100 P2; } > $A/lane-cleric2.log 2>&1 &
{ lane barbarian2 130 P1; lane barbarian2 72 P2; } > $A/lane-barbarian2.log 2>&1 &
{ lane bard2 125 P1; lane bard2 75 P2; } > $A/lane-bard2.log 2>&1 &
wait
