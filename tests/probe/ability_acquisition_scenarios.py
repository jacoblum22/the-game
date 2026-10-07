"""Six hand-scripted acquisition scenarios for feature 003 (T011), covering all four source
archetypes and all three acquisition methods at least once each, per research.md's coverage
decision.

Found live during T012's first run: an earlier version of this file scripted the `action` as
narrating the kill/acquisition itself (e.g. "I drive my spear through its chest, dropping it
instantly"). The DM correctly followed Pattern P8 (already-established: real-stakes actions get
rolled, never just narrated into success) and rolled a critical failure, narrating the *player*
getting mauled instead -- grant_ability correctly wasn't called, because the kill genuinely
didn't happen. That was the mechanism working exactly right; the scenario's premise was wrong.
Every scenario below now puts the kill/acquisition ALREADY SETTLED, past-tense, in the
`context`, with `action` a genuine no-stakes follow-up (Pattern P8's own "no real stakes" case)
-- this is what actually isolates "does the DM correctly map an established event onto
grant_ability's categories" from "did a fresh roll happen to succeed," which is a different
question this probe isn't trying to test.

Format mirrors campaign_outlines.py: original, short, non-copyrighted text.
"""

from dataclasses import dataclass


@dataclass
class AcquisitionScenario:
    name: str
    context: str
    action: str
    expected_source_archetype: str
    expected_acquisition_method: str


SCENARIOS: list[AcquisitionScenario] = [
    AcquisitionScenario(
        name="beast_decisive_kill",
        context=(
            "The dire wolf lies dead at your feet, felled by a single clean spear thrust "
            "straight through its chest a moment ago."
        ),
        action="I catch my breath and look over what I've just done.",
        expected_source_archetype="beast",
        expected_acquisition_method="decisive_kill",
    ),
    AcquisitionScenario(
        name="beast_narrow_survival",
        context=(
            "The scarred dire wolf has just collapsed from its wounds, but not before its "
            "jaws nearly closed on your throat -- you're bloodied and shaking, barely still "
            "standing."
        ),
        action="I steady myself against a tree and check myself over for injuries.",
        expected_source_archetype="beast",
        expected_acquisition_method="narrow_survival",
    ),
    AcquisitionScenario(
        name="elemental_fire_non_lethal_subdual",
        context=(
            "You've just cupped your hands around the flame wisp and gently smothered its "
            "core -- it dissipates peacefully into the air, leaving only a faint warmth "
            "behind."
        ),
        action="I dust off my hands and glance around the campsite.",
        expected_source_archetype="elemental_fire",
        expected_acquisition_method="non_lethal_subdual",
    ),
    AcquisitionScenario(
        name="elemental_fire_decisive_kill",
        context=(
            "Your blade has just punched clean through the second flame wisp's glowing "
            "core, snuffing it out instantly in a shower of sparks."
        ),
        action="I sheath my blade and take a moment to survey the smoldering brazier.",
        expected_source_archetype="elemental_fire",
        expected_acquisition_method="decisive_kill",
    ),
    AcquisitionScenario(
        name="undead_narrow_survival",
        context=(
            "The wight has just crumbled to dust after its icy claws nearly stopped your "
            "heart -- you stumbled back just in time, badly shaken but alive."
        ),
        action="I take a moment to steady my breathing before continuing down the path.",
        expected_source_archetype="undead",
        expected_acquisition_method="narrow_survival",
    ),
    AcquisitionScenario(
        name="construct_non_lethal_subdual",
        context=(
            "You've just wedged an iron bar into the sentinel construct's knee joint and "
            "twisted, disabling it without shattering its frame -- it now stands frozen, "
            "inert."
        ),
        action="I step past it and continue down the passage.",
        expected_source_archetype="construct",
        expected_acquisition_method="non_lethal_subdual",
    ),
]
