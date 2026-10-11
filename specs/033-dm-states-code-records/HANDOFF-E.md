# HANDOFF 033 phase E (measures that do not word-match; lane evals/, tests/evals/; engine/ untouched)
Done (T060-T064): `evals/turn_judge.py`, `tests/evals/test_turn_judge.py` (8 tests), `npc_agency.py`, `h2h_score.py` edited.
- Judge: 5 measures (leak, ask, mood, pronoun, absent), one Haiku call per sampled turn and measure, fixed rubric per
  measure in `MEASURES`; packet from a save = passage, player turn, log (this turn's non-noise events + dm_tools tools),
  earlier 2 passages, cast (present/elsewhere + pronouns), secrets (npc data.secrets, sealed string facts, unfound case nodes).
- Cache `evals/baselines/turn_judge/<save>.json` (rubric hash; changed rubric drops it). `--offline` writes `<save>.offline.json`
  which no scorer reads. Hand file `evals/baselines/turn_judge_hand.yaml` (`verdicts: [{save, turn, measure, judge, hand}]`).
  Not created yet; `run ... --template out.yaml` writes the flagged turns with `hand: null`. Precision = flagged turns the hand
  confirmed; "precision unmeasured" below 20 hand verdicts per measure (and when none of them is a flagged turn).
- npc_agency: M10 from the judge (word-overlap `leaked` gone); label `conditional` renamed `priced`; `costly_asks` counts
  granted+partial only, `costly_priced` apart (old saved runs' `conditional` still read as priced).
- h2h_score: leaks/costly/mood rows read the judge cache (no model call); engine `leaks`/`asks`/`moods` no longer read.
  Trap 1 done: exchanges = turns with a `round` boundary (old count if the save has none); told = `said` list lengths.
Gates: tests/evals 25 passed 1 skipped; ruff clean on my files (5 old errors elsewhere in evals/); pyright: only the env's
"pytest/yaml not resolved" notes (same for existing tests). Full pytest: see the final report.
Live command (not run): `PYTHONUTF8=1 py -3.12 evals/turn_judge.py run <save.db> [...] --n 30 --seed 1 --template evals/baselines/turn_judge_hand_todo.yaml`
(5 calls per sampled turn: 30 turns = 150 Haiku calls per save), then fill `hand:` and move rows into the hand file.
Traps: the hand file stores the judge's label at write time; after a rubric change re-template. The judge sees the cast at the
END of the turn, so someone who arrives during it reads as present. P4 deletes `_audit`/`_log_only`; nothing here reads them.
