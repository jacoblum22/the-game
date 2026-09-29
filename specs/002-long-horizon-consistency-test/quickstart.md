# Quickstart: Long-Horizon Consistency Stress Test

Validation guide only — implementation details belong in `tasks.md` and the actual code.
Builds directly on Feature 001's setup (`.env` with `GEMINI_API_KEY`, same venv).

## Prerequisites

- Feature 001 already set up and working (`.venv`, `.env` with `GEMINI_API_KEY`)
- No new dependencies — same `requirements.txt`

## Step 1: Validate scenario generation alone (cheap, no long session yet)

```bash
python -c "from scenario_pipeline import generate_scenario; generate_scenario('a short original outline here')"
```

Confirms the three-stage pipeline (trajectory → commitments → initial facts) plus the isolation
check run end-to-end and produce a valid `WorldState` for one campaign outline, before spending
any budget on a long run. Per research.md's sequencing decision, do this before anything else.

## Step 2: Run one short session (15-20 turns) before scaling up

```bash
python tests/probe/run_long_horizon_test.py --turns 15 --runs 1
```

Runs one scenario through one persona condition for a short turn count, printing each turn's
narration, any detected conflicts, and a final `SessionOutcome`. This is the checkpoint before
committing to the full SC-002 batch — confirm the auditor and category-attribution logic behave
sensibly here first.

## Step 3: Run the full success-criteria batch

```bash
python tests/probe/run_long_horizon_test.py --turns 50 --runs 5 --personas adversarial,natural
```

Generates the 3+ scenarios SC-001 requires, runs at least 5 full sessions mixing both persona
conditions per SC-002, and prints the aggregate report: per-run and aggregate survival/success
rates, turn-of-first-conflict, and a conflict-type/state-category breakdown — compared directly
against the published NCP-Bench baseline figures per SC-003.

**Expected outcome**: per research.md, most runs will likely NOT reach the 50-turn cap intact —
that is expected, not a bug. The deliverable is the report itself (where and how it broke), not
a clean pass. A worse-than-NCP-Bench result is itself a valid, useful finding.

## Run unit tests

```bash
pytest tests/unit/
```

Covers `test_resolution.py` (unchanged from Feature 001) plus the new
`test_scenario_schema.py` — structural validation only (unique IDs, valid cross-references),
no live API calls, no semantic content checking.
