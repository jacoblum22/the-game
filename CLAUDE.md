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

## Subagents (the weekly usage limit is the binding constraint)
- Every turn re-reads the agent's whole context, so cost grows with the square of an agent's length. Use **short
  agents, one per slice, with a written handoff**, and Sonnet unless the slice is design-heavy.
- Rules work: `rules-worker`. Engine specs: `spec-implementer`. Tracing: `root-cause-investigator`. Avoid
  `general-purpose`, which starts at 60k tokens per turn against 12–27k for these.
- The model, slicing and handoff rules are in `.claude/skills/playtest-round/SKILL.md` ("Agents").

## Code never deduces the story (constitution VIII.9, owner 2026-10-10)
- Code MUST NOT infer story state from actions or words: positions, range, presence, companions, holds, identity,
  an enemy's choice, a cost's form. Only the DM model sets these, through a tool or by choosing a rule's option.
  Code records what it is told and does the arithmetic.
- Code MUST NOT decide anything by word matching over natural-language text: regexes, keyword lists, or name,
  alias, head-noun or word-overlap matching. Parsing code-made ids and tokens is fine.
- When code and the story disagree, add a DM tool or field. Never add an inference.

## Code checks (`engine/`, `play/`, `evals/`, `tests/`)
Cloud sessions install `requirements-dev.txt` automatically (`.claude/hooks/session-start.sh`). Before
pushing code, run `ruff check .`, `pyright` and `python -m pytest -q -p no:cacheprovider` (about 3 minutes;
on Windows set `PYTHONUTF8=1`), and report new failures rather than the whole output.
