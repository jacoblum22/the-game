# Quickstart: Ability Acquisition Probe

Validation guide only — implementation details belong in `tasks.md` and the actual code.
Builds directly on Feature 001/002's setup (`.env` with `GEMINI_API_KEY`, same venv).

## Prerequisites

- Feature 001/002 already set up and working (`.venv`, `.env` with `GEMINI_API_KEY`)
- No new dependencies — same `requirements.txt`

## Step 1: Validate the mechanism alone (zero API cost, run this first)

```bash
pytest tests/unit/test_ability_pool.py
```

Confirms `resolve_ability_grant`'s gating (a source archetype's method never returns another
archetype's template) and fill-mechanism logic (guaranteed pick is deterministic; weighted
rolls land in-pool with the declared bias) entirely offline, per User Story 1 and SC-001. Do
this before spending anything live — if this fails, nothing downstream is worth running yet.

## Step 2: Run one scripted scenario live, by hand, before the full set

```bash
python tests/probe/run_ability_acquisition_probe.py --scenarios 1
```

Runs a single hand-scripted acquisition scenario through the real `dm_agent` tool-calling loop
and prints whether `grant_ability` was called with the source archetype and acquisition method
that scenario was designed to imply, plus the resulting `EffectTemplate`. Confirms the tool is
wired correctly before committing to the full scripted set.

## Step 3: Run the full scripted scenario set

```bash
python tests/probe/run_ability_acquisition_probe.py
```

Runs every scripted scenario (covering each source archetype and each acquisition method at
least once, per research.md's coverage decision), checks each ability-grant turn via the
extended `auditor.check_turn`, and prints the SC-002/SC-003 report: per-scenario tool-call
correctness and the measured narration/grant consistency rate, broken out by source archetype
and acquisition method — not collapsed into one aggregate number, same reporting discipline as
Feature 001/002.

**Expected outcome**: per SC-003, this is a measured rate to report, not a pass/fail gate — a
mismatch found here is itself a useful finding about this mechanism, the same way Feature 002
treated an early result as informative rather than a failure to hide. Per SC-004, the whole run
should stay under roughly 50 live API calls — if it doesn't, that's worth noting before scaling
this probe any further.

## Run all unit tests

```bash
pytest tests/unit/
```

Covers `test_resolution.py`, `test_scenario_schema.py`, `test_scenario_pipeline.py` (all
unchanged) plus the new `test_ability_pool.py` — structural/deterministic logic only, no live
API calls.
