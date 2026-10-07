"""Unit tests for src/scenario_pipeline.py's pure boundary validation (feature 002, fast-forward
seeding). Only the cutoff_fraction range check runs before any live API call, so it's the only
piece of generate_fast_forward_scenario cheaply unit-testable without mocking -- same split as
the rest of this project: pure/deterministic logic gets a unit test, live-API behavior gets
exercised live via the scripted harness, not here.
"""

import pytest
from scenario_pipeline import generate_fast_forward_scenario


def test_cutoff_fraction_out_of_range_rejected_before_any_api_call():
    with pytest.raises(ValueError, match="cutoff_fraction"):
        generate_fast_forward_scenario("an outline", cutoff_fraction=1.0)

    with pytest.raises(ValueError, match="cutoff_fraction"):
        generate_fast_forward_scenario("an outline", cutoff_fraction=-0.1)
