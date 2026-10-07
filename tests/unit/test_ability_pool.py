"""Unit tests for src/ability_pool.py (feature 003, T008). Pure, deterministic logic only --
zero live API calls, per spec.md's User Story 1 ("validate the mechanism with zero live API
cost"). Covers spec.md's three Acceptance Scenarios for User Story 1.
"""

from collections import Counter

import pytest
from ability_pool import SOURCE_ARCHETYPES, resolve_ability_grant


# --- Acceptance Scenario 1: a "guaranteed" method deterministically returns the same,
# specific template every time for a given source archetype. ---


def test_decisive_kill_always_returns_the_signature_template():
    results = {resolve_ability_grant("beast", "decisive_kill").template_id for _ in range(20)}
    assert results == {"beast_thick_hide"}


def test_guaranteed_pick_is_the_pools_own_signature_template_for_every_archetype():
    for name, archetype in SOURCE_ARCHETYPES.items():
        signature = next(t for t in archetype.pool if t.is_signature)
        result = resolve_ability_grant(name, "decisive_kill")
        assert result.template_id == signature.template_id


# --- Acceptance Scenario 2: a "weighted" method returns a template from the archetype's pool
# on every call, with the observed distribution matching the declared bias (not uniform, not
# a disguised guarantee -- every template must stay reachable). ---


def test_weighted_roll_always_stays_within_the_archetypes_own_pool():
    valid_ids = {t.template_id for t in SOURCE_ARCHETYPES["elemental_fire"].pool}
    for _ in range(200):
        result = resolve_ability_grant("elemental_fire", "narrow_survival")
        assert result.template_id in valid_ids


def test_weighted_roll_distribution_favors_the_declared_bias_without_excluding_others():
    counts = Counter(
        resolve_ability_grant("undead", "non_lethal_subdual").template_id for _ in range(600)
    )
    # non_lethal_subdual is biased toward "utility" -- undead's utility template is
    # undead_whispers_of_the_dead.
    assert counts["undead_whispers_of_the_dead"] > counts["undead_deathly_resilience"]
    assert counts["undead_whispers_of_the_dead"] > counts["undead_grave_chill"]
    # Every template must stay reachable -- a genuine bias, not a disguised guarantee.
    assert counts["undead_deathly_resilience"] > 0
    assert counts["undead_grave_chill"] > 0


# --- Acceptance Scenario 3: no archetype's resolution ever returns a template belonging to a
# different archetype's pool. ---


def test_no_archetype_ever_returns_another_archetypes_template():
    for name, archetype in SOURCE_ARCHETYPES.items():
        own_ids = {t.template_id for t in archetype.pool}
        for method_name in ("decisive_kill", "narrow_survival", "non_lethal_subdual"):
            for _ in range(30):
                result = resolve_ability_grant(name, method_name)
                assert result.template_id in own_ids
                assert result.source_archetype == name


# --- Boundary/validation checks (per contracts/tools.md's validation-failure contract) ---


def test_unknown_source_archetype_raises():
    with pytest.raises(ValueError, match="source_archetype"):
        resolve_ability_grant("dragon", "decisive_kill")


def test_unknown_acquisition_method_raises():
    with pytest.raises(ValueError, match="acquisition_method"):
        resolve_ability_grant("beast", "backstab")
