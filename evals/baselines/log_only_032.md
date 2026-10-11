# Spec 032 P5b: log-only checks on real dm-tools passages

Run: every dm-tools turn of the five `tests/fixtures/feedback_corpus/dmtools-*.db.gz` saves plus the two
`playtest-20261010-181523-*-dm-tools.db` saves (72 passages), each checked against the state just after its turn, with
that turn's tool log and the six exchanges before it as the "recent talk".

| check | flagged | true | false | precision |
|---|---|---|---|---|
| pronoun | 0 | 0 | 0 | not measurable |
| absent_named | 0 | 0 | 0 | not measurable |
| item_unbacked | 0 | 0 | 0 | not measurable |

No real passage tripped a check, so there is nothing to label. The 40 hand-labelled passages the task asked for do not
exist in the dm-tools saves: the round-9 pronoun flips (Octette Vasac) and the "officer who is not present" sentence came
from pipeline runs. The checks fire on made-up cases (`tests/engine/test_spec032_p5b.py`: Q9-Q13, I12); none is
promoted (DL-12-138). Re-measure on the P5.5 live runs (talker + explorer, Haiku) before anything is promoted.
