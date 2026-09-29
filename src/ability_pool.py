"""Ability acquisition mechanism (feature 003): implements Pattern P5's first flavor --
source-gates-a-bounded-pool, acquisition-method-picks-the-fill. Everything in this module is a
plain, deterministic Python data shape and function; no LLM call happens here, by design (T002,
research.md's first decision) -- User Story 1 needs this testable with zero live API cost.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Literal

FlavorBias = Literal["defensive", "utility", "offensive"]
FillMechanism = Literal["guaranteed", "weighted"]


@dataclass(frozen=True)
class EffectTemplate:
    """One concrete, nameable grantable effect, belonging to exactly one SourceArchetype's
    pool (data-model.md). `is_signature` is True for exactly one template per archetype --
    the one a "guaranteed" fill mechanism always returns."""

    template_id: str
    source_archetype: str
    name: str
    description: str
    is_signature: bool
    flavor_bias: FlavorBias


@dataclass(frozen=True)
class SourceArchetype:
    """A small, fixed category a defeated/encountered source can belong to; gates its own
    small, bounded pool of EffectTemplates (never shared with another archetype)."""

    name: str
    pool: tuple[EffectTemplate, ...]


@dataclass(frozen=True)
class AcquisitionMethod:
    """A small, fixed category describing how a source was defeated or acquired; determines
    which fill mechanism selects a template from a SourceArchetype's gated pool."""

    name: str
    fill_mechanism: FillMechanism
    biased_toward: FlavorBias | None = None
    """Only meaningful when fill_mechanism == "weighted" -- which flavor_bias the roll favors."""


@dataclass
class AbilityGrant:
    """One granted EffectTemplate, recorded on WorldState (data-model.md)."""

    turn_number: int
    source_archetype: str
    acquisition_method: str
    template_id: str
    reason: str

    def to_dict(self) -> dict:
        return {
            "turn_number": self.turn_number,
            "source_archetype": self.source_archetype,
            "acquisition_method": self.acquisition_method,
            "template_id": self.template_id,
            "reason": self.reason,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AbilityGrant":
        known = {"turn_number", "source_archetype", "acquisition_method", "template_id", "reason"}
        return cls(**{k: v for k, v in data.items() if k in known})


# --- Fixed probe content (T005/T006) --------------------------------------------------------
#
# Hand-authored, throwaway probe fixtures (spec.md's Assumptions) -- small enough to enumerate
# in one sitting (FR-006), not intended to survive into the real game's eventual content. Each
# archetype's pool covers all three flavor_bias values exactly once, with exactly one
# is_signature=True template, per data-model.md's Validation note.

SOURCE_ARCHETYPES: dict[str, SourceArchetype] = {
    "beast": SourceArchetype(
        name="beast",
        pool=(
            EffectTemplate(
                template_id="beast_thick_hide",
                source_archetype="beast",
                name="Thick Hide",
                description=(
                    "Your skin toughens where the beast's claws couldn't find purchase -- "
                    "reduce incoming damage from a single hit per encounter, but only against "
                    "attacks you can see coming."
                ),
                is_signature=True,
                flavor_bias="defensive",
            ),
            EffectTemplate(
                template_id="beast_keen_scent",
                source_archetype="beast",
                name="Keen Scent",
                description=(
                    "You can pick out a nearby creature's trail or presence by scent alone, "
                    "even out of sight -- but only for creatures you have personally smelled "
                    "before."
                ),
                is_signature=False,
                flavor_bias="utility",
            ),
            EffectTemplate(
                template_id="beast_savage_claws",
                source_archetype="beast",
                name="Savage Claws",
                description=(
                    "Once per encounter, a single unarmed or natural-weapon strike lands with "
                    "bestial force -- but you take a small cost in exhaustion from the effort "
                    "afterward."
                ),
                is_signature=False,
                flavor_bias="offensive",
            ),
        ),
    ),
    "elemental_fire": SourceArchetype(
        name="elemental_fire",
        pool=(
            EffectTemplate(
                template_id="elemental_fire_heat_resistance",
                source_archetype="elemental_fire",
                name="Heat Resistance",
                description=(
                    "Fire and intense heat harm you less than they should -- but this offers "
                    "no protection against cold, and can lull you into standing too close to "
                    "danger."
                ),
                is_signature=False,
                flavor_bias="defensive",
            ),
            EffectTemplate(
                template_id="elemental_fire_molten_touch",
                source_archetype="elemental_fire",
                name="Molten Touch",
                description=(
                    "You can warp or melt a small metal or ice object with a touch -- limited "
                    "to something you could physically hold, and it takes a moment of "
                    "concentration."
                ),
                is_signature=False,
                flavor_bias="utility",
            ),
            EffectTemplate(
                template_id="elemental_fire_ember_burst",
                source_archetype="elemental_fire",
                name="Ember Burst",
                description=(
                    "Once per encounter, you release a short-range burst of fire -- it costs "
                    "you a moment of vulnerability as the heat leaves you drained afterward."
                ),
                is_signature=True,
                flavor_bias="offensive",
            ),
        ),
    ),
    "undead": SourceArchetype(
        name="undead",
        pool=(
            EffectTemplate(
                template_id="undead_deathly_resilience",
                source_archetype="undead",
                name="Deathly Resilience",
                description=(
                    "Once per encounter, you shrug off a debilitating or exhausting effect "
                    "that would otherwise have slowed you -- but it doesn't undo damage "
                    "already taken."
                ),
                is_signature=False,
                flavor_bias="defensive",
            ),
            EffectTemplate(
                template_id="undead_whispers_of_the_dead",
                source_archetype="undead",
                name="Whispers of the Dead",
                description=(
                    "You can briefly sense recent death or violence in an area -- only an "
                    "impression, not details, and only where something has actually died "
                    "recently."
                ),
                is_signature=False,
                flavor_bias="utility",
            ),
            EffectTemplate(
                template_id="undead_grave_chill",
                source_archetype="undead",
                name="Grave Chill",
                description=(
                    "Your touch saps warmth and vitality, dealing a small amount of damage "
                    "and leaving the target chilled -- but it only works on a single touch "
                    "per encounter."
                ),
                is_signature=True,
                flavor_bias="offensive",
            ),
        ),
    ),
    "construct": SourceArchetype(
        name="construct",
        pool=(
            EffectTemplate(
                template_id="construct_iron_frame",
                source_archetype="construct",
                name="Iron Frame",
                description=(
                    "Reduce incoming damage from a single blunt or crushing hit per encounter "
                    "-- offers no benefit against piercing or magical attacks."
                ),
                is_signature=True,
                flavor_bias="defensive",
            ),
            EffectTemplate(
                template_id="construct_precise_calibration",
                source_archetype="construct",
                name="Precise Calibration",
                description=(
                    "Once per encounter, gain a bonus on a single investigation or "
                    "precision-based check -- it only applies to something you can physically "
                    "examine up close."
                ),
                is_signature=False,
                flavor_bias="utility",
            ),
            EffectTemplate(
                template_id="construct_overclock_strike",
                source_archetype="construct",
                name="Overclock Strike",
                description=(
                    "Once per encounter, land a single empowered strike -- but you're briefly "
                    "staggered and vulnerable on your next turn as a cost."
                ),
                is_signature=False,
                flavor_bias="offensive",
            ),
        ),
    ),
}

ACQUISITION_METHODS: dict[str, AcquisitionMethod] = {
    "decisive_kill": AcquisitionMethod(name="decisive_kill", fill_mechanism="guaranteed"),
    "narrow_survival": AcquisitionMethod(
        name="narrow_survival", fill_mechanism="weighted", biased_toward="defensive"
    ),
    "non_lethal_subdual": AcquisitionMethod(
        name="non_lethal_subdual", fill_mechanism="weighted", biased_toward="utility"
    ),
}


# --- The mechanism itself (T007) -------------------------------------------------------------

_BIASED_WEIGHT = 3
_UNBIASED_WEIGHT = 1
"""A "weighted" acquisition method's roll favors its biased_toward flavor 3:1 over each other
template in the pool -- a genuine bias, never a disguised guarantee (spec.md's Acceptance
Scenario 2 explicitly requires every template stay reachable)."""


def resolve_ability_grant(source_archetype: str, acquisition_method: str) -> EffectTemplate:
    """The source-gates-pool + method-picks-fill mechanism (Pattern P5, first flavor).

    Deterministic and pure except for weighted rolls' randomness -- no LLM call, no I/O.
    Raises ValueError for an unknown archetype or method rather than silently falling back,
    per contracts/tools.md's validation-failure contract (mirrors how an out-of-range
    roll_check argument is treated, not a new convention).
    """
    if source_archetype not in SOURCE_ARCHETYPES:
        raise ValueError(f"Unknown source_archetype {source_archetype!r} -- not in SOURCE_ARCHETYPES")
    if acquisition_method not in ACQUISITION_METHODS:
        raise ValueError(f"Unknown acquisition_method {acquisition_method!r} -- not in ACQUISITION_METHODS")

    archetype = SOURCE_ARCHETYPES[source_archetype]
    method = ACQUISITION_METHODS[acquisition_method]

    if method.fill_mechanism == "guaranteed":
        for template in archetype.pool:
            if template.is_signature:
                return template
        raise ValueError(f"Archetype {source_archetype!r} has no is_signature template -- pool misconfigured")

    # "weighted": every template in the pool stays reachable; the biased_toward flavor is just
    # more likely, never exclusive -- see _BIASED_WEIGHT's docstring.
    weights = [
        _BIASED_WEIGHT if template.flavor_bias == method.biased_toward else _UNBIASED_WEIGHT
        for template in archetype.pool
    ]
    return random.choices(archetype.pool, weights=weights, k=1)[0]
