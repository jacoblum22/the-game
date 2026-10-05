# Handoff: finish Wave 3c integration (cloud continuation)

> **Status (2026-10-05): COMPLETED by the cloud continuation.** See `integration-report.md` ("Continuation" C1–C6,
> the back-fill, and the final summary). Validator: 0 ERROR, 0 WARN. New issues I-029..I-032; I-028 deferred to Wave 5.
> Nothing committed; the rollback point is `cbbd27e`.

Context for a session with no memory of the prior chats.

## Project
TTRPG ruleset for an AI Dungeon Master (`rules/`, chapters 00-13, 15, 16 + `rules/data/*.yaml`).
Goals: (1) player can try anything, (2) the AI rules correctly. Player complexity is NOT a constraint.
Rules are authored as rule-cards for retrieval, not loaded wholesale (00.15). Chapter 14 (codex) is Wave 6.

## State
All chapters were authored (Wave 3). An Opus integration agent ("Integration: merge, amend, validate")
was cut off by a usage limit after ~48 min. On-disk evidence it got through most of it:
- `appendix/decision-log.md`, `appendix/traceability.md` assembled; `data/anchors.yaml` recompiled;
  `_process/validate_ruleset.py` written and runs.
- `[integration: ...]` edit markers present in ch.06, 10, 11, 12, 13, 15; NONE in ch.16.
- `_process/integration-report.md` only logs through "step 3, part A" (stale: steps 4-7 happened unlogged).
- Validator currently reports 1 ERROR: XREF `DL-INT-11` unresolved at `00-architecture.md:1778`.

## Remaining work (do in order; log each step in integration-report.md as you go)
1. Read `_process/integration-report.md`, `_process/INTERFACE-REQUESTS.md` (ch.16 + ch.10-15 sections) and
   `_process/issue-ledger.md`. Verify every "(integration edit)" item for ch.10, 11, 12, 13, 15, 16 is applied
   (each edit carries an `[integration: ...]` citation; ch.16 appears to have none applied).
2. Ledger integration items: I-023 (order of h.10.site_exposure vs 07 affliction handler in boundary
   phase 2), I-024 (WE-01-2 "brother" example, may already be done in ch.01), I-026 (fix
   `_process/simulation/11-world-sim.py` gain_hold so expand can't raise factions above tier 3; add `steadfast`
   to AGENDA; re-run), I-027 (clarify PR-10-8 threat-word step; re-audit generic travel.yaml tables).
3. Fix the validator ERROR (DL-INT-11 missing from the decision log / INT fragment, or the reference).
4. Run `python rules/_process/validate_ruleset.py`; fix mechanical issues; log the rest in the issue ledger.
   (REFS-MD-EX INFO lines are expected illustrative ids.)
5. Finish the report; append I-028 status (world-seed procedure is a Wave 5 revision item, do NOT write it now).
Do not start Wave 4/5/6 work. Edits must be exact-match and logged; keep data files parse-valid YAML.

## Notes
- The earlier `rules-snapshot-pre-integration` rollback lived in a local scratchpad and is NOT available here;
  the commit this branch is based on is the rollback point.
- Final deliverable: updated report + a short summary of what changed and what's still open.
