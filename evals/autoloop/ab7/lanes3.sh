#!/bin/sh
# Companions' turns in the batch and resistances in code, on the same fight starts as lanes2 (turns2 is the arm before).
A=evals/autoloop/ab7
lane() { g=$1; r=$2
  PYTHONPATH=. .venv/Scripts/python evals/autoloop/replay.py $g $r 2 $A/comp-$g.json; echo "comp $g done $(date +%T)"; }
lane barbarian2 94,139,164 > $A/lane3-barbarian2.log 2>&1 &
lane bard2 87,128 > $A/lane3-bard2.log 2>&1 &
wait
