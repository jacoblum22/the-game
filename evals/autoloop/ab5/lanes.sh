#!/bin/sh
# Notebook writes that answer back (#1): base (NO_ANSWER) vs answer, 4 runs on 6 contradiction rounds. P1 holds
# rounds from block 121-180, P2 from block 61-120 (blind.py packets are per block).
py() { PYTHONPATH=. .venv/Scripts/python evals/autoloop/replay.py "$@"; }
A=evals/autoloop/ab5
lane() { g=$1; r=$2; p=$3
  NO_ANSWER=1 py $g $r 4 $A/$p/base-$g.json; echo "base $g done $(date +%T)"
  py $g $r 4 $A/$p/answer-$g.json; echo "answer $g done $(date +%T)"; }
{ lane cleric2 143,152 P1; } > $A/lane-cleric2.log 2>&1 &
{ lane barbarian2 81,90 P2; } > $A/lane-barbarian2.log 2>&1 &
{ lane bard2 127 P1; lane bard2 97 P2; } > $A/lane-bard2.log 2>&1 &
wait
