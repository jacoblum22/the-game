# CLAUDE.md

## Rules corpus (`rules/`): working conventions
The ruleset is about 500k words. Never read a whole chapter. Context size is what costs money: every turn
re-reads it.

- **Look things up by id:** `python rules/tools/rq.py <id> [<id>...]` prints just that rule card, section,
  table (T-), procedure (PR-), example (WE-), open question (OEQ-), decision (DL-) or data entry
  (`ab.*`, `adv.*`, …).
  - `--toc 06` or `--toc 06.4` lists the ids in a chapter or section.
  - `--refs <id>` shows where an id is cited.
  - `--find <regex>` searches titles.
- **Keep shell output short.** Pipe long output through `| head -40`. Have scripts print summaries and
  failures, not dumps.
- **Batch.** Make independent tool calls in one turn, and do multi-edit work in one script.
- **Edits:** use exact unique-match replacements, scripted with `assert s.count(old) == 1`. Tag each edit
  with its source, e.g. `[revision: I-NNN]` or `[verification: V-NNN]`.
- **Generated data:** many `rules/data/*.yaml` files come from `rules/_process/simulation/*gen*` scripts.
  Change the generator, re-run it, and confirm the output matches.
- **Decisions:** record them in `rules/appendix/fragments/DL-CC.md`, then re-assemble
  `appendix/decision-log.md` and `appendix/traceability.md`.
- **Anchors:** after a card changes, run `python rules/_process/simulation/12-compile_anchors.py`.
- **Exit gate:** `python rules/_process/validate_ruleset.py` must show 0 ERROR / 0 WARN (`-v` shows INFO).
- **Numbers:** back balance claims with a seeded sim in `rules/_process/simulation/`, and commit its
  output next to it.
- **Tracking:** the issue ledger is `rules/_process/issue-ledger.md`, and the plan is
  `rules/_process/FINISH-PLAN.md`. Append to your wave report in `rules/_process/reports/` after every
  step.
- **Do not edit ch.13** (an optional, unmaintained example setting). Never commit; the orchestrator
  commits.
