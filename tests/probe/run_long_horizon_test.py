"""Long-horizon consistency stress test harness for feature 002.

Not a pytest unit test (tests/unit/ covers the pure structural parts) -- this makes real,
billed API calls. Run manually per quickstart.md. Built incrementally per tasks.md:
- T012 (US1): scenario-only verification -- runs generate_scenario against all 3 campaign
  outlines and reports isolation-check pass/fail for each, satisfying SC-001 without running
  any live session turns.
- T013-T019 (US2/US3): will add the actual turn-by-turn session loop and reporting on top of
  this same script.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

from campaign_outlines import OUTLINES  # noqa: E402
from scenario_pipeline import IsolationViolationError, generate_scenario  # noqa: E402


def run_scenario_checks() -> bool:
    """T012: SC-001 -- generate a scenario for all 3 outlines, report isolation pass/fail."""
    all_passed = True

    for name, outline in OUTLINES.items():
        print(f"--- Scenario: {name}")
        try:
            trajectory, commitments, world_state = generate_scenario(outline)
        except IsolationViolationError as exc:
            print(f"    FAIL (isolation): {exc}")
            all_passed = False
            continue
        except ValueError as exc:
            print(f"    FAIL (structural validation): {exc}")
            all_passed = False
            continue

        print(f"    PASS: {len(trajectory)} trajectory nodes, {len(commitments)} commitments")
        print(f"    Starting position: {world_state.position!r}")
        print(
            f"    Seeded categories: resources={list(world_state.resources)}, "
            f"possessions={list(world_state.possessions)}, "
            f"status_flags={list(world_state.status_flags)}"
        )
        print()

    return all_passed


if __name__ == "__main__":
    ok = run_scenario_checks()
    print("=" * 60)
    print("SC-001 result:", "PASS -- all scenarios isolated" if ok else "FAIL -- see above")
    sys.exit(0 if ok else 1)
