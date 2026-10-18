#!/bin/sh
# Second try of the new arm: the order also in the reminder sent with every player line (the DM kept its old order
# in 22 of 24 runs: 2.54 model calls a round against 2.75).
A=evals/autoloop/ab6
lane() { PYTHONPATH=. .venv/Scripts/python evals/autoloop/replay.py $1 $2 4 $A/$3/one-$1.json; echo "one $1 done $(date +%T)"; }
{ lane cleric2 150 P1r; lane cleric2 100 P2r; } > $A/lane2-cleric2.log 2>&1 &
{ lane barbarian2 130 P1r; lane barbarian2 72 P2r; } > $A/lane2-barbarian2.log 2>&1 &
{ lane bard2 125 P1r; lane bard2 75 P2r; } > $A/lane2-bard2.log 2>&1 &
wait
