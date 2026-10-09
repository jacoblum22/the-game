# Orchestration and trace helpers

Small scripts the orchestrating agent used in round 2–6. Run them from the repo root with `PYTHONUTF8=1 py -3.12`.

| Script | What it does |
|---|---|
| `resolve_rules_merge.py` | Run during `git merge --no-commit` of a rules or engine branch. It resolves the recurring conflicts and prints `MANUAL:` for anything else. Recurring conflicts:<br>• appended DL fragments: keep both sides;<br>• `issue-ledger.md` and `open-empirical-questions.md`: merged row by row against the merge base;<br>• generated files (`decision-log.md`, `traceability.md`, `anchors.yaml`, `cards.json`, the replay game): theirs is taken, then regenerated. |
| `regen_and_gate.sh [--no-suite]` | After any merge that touches `rules/`, runs:<br>1. re-assemble the appendix;<br>2. compile the anchors;<br>3. rebuild `cards.json` **last**;<br>4. validator count;<br>5. re-record the replay;<br>6. stage;<br>7. full pytest. |
| `repairs.py <save.db>…` | Lists every narration repair round in the given saves: the failing sentence and its reason, the missing items, and what the repair returned. |
| `dunno_pairs.py <transcript.md>` | Pairs each NPC "I don't know"-style line with the player's line that triggered it, plus the player's note for that input. |

All saves must be opened read-only (`sqlite3.connect('file:<path>?mode=ro', uri=True)`). The useful tables are:

| Table or file | Holds |
|---|---|
| `turns.record` | `draft_versions`, `parts`, `said`, `claim_log`, `beats` |
| `model_calls.request` / `.response` | the exact packet and answer for every role |
| `events` | the event log |
| `<save>.changes.jsonl` | one line per Reader beat (the typed change) |
| `<save>.disputes.md` | the `/fix` review log |
