"""Spec 016: the precision checks (12.3.2 "Precision, not class, decides blocking"; OEQ-12-27): the pronoun of a
certain subject and season words against the calendar line. Each: a hit, no hit, an uncertain subject (no verdict),
and a time-shift clause allowed; a check measured below min_precision is demoted to log-only by data."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from engine.audit.claims import precision_checks
from engine.audit.declare import SceneIndex
from engine.data.loader import load_rules

RULES = load_rules()
IDX = SceneIndex(pc="pc.sketash", aliases={"pc.sketash": ["sketash"], "npc.murzak": ["murzak red-hand", "murzak"],
                                           "npc.feney": ["feney blackward", "feney"],
                                           "npc.varrka": ["varrka mud-walker", "varrka"],
                                           "npc.ysrion": ["ysrion leafward", "ysrion", "merchant"]},
                 pronouns={"npc.murzak": "f", "npc.feney": "f", "npc.varrka": "m", "npc.ysrion": "m"})


def hits(text: str, *before: str, speech: tuple[str, ...] = (), season: str | None = "spring",
         rules: Any = RULES, about: tuple[str, ...] = ()) -> list[tuple[str, str, str, bool]]:
    return [(h.check, h.voice, h.words, h.blocks) for h in precision_checks(
        text, idx=IDX, before=before, speech=speech, about=about, season=season, rules=rules)]


# ---------------------------------------------------------------------------------------- pronoun_certain_subject


def test_pronoun_hit_on_the_only_person_named() -> None:
    """Playtest 20261008-145430 fighter, inputs 28-29: "his weight" for Murzak, stored she/her."""
    [h] = precision_checks("Murzak twists and shrugs the grab off, and you lose your footing against his weight.",
                           idx=IDX, rules=RULES)
    assert (h.check, h.words, h.store_value, h.subject, h.blocks) == (
        "pronoun_certain_subject", "his", "she/her", "npc.murzak", True)
    assert "she/her" in h.why
    assert hits("His grip tightens on the rug.", "Murzak Red-Hand turns to face you.")  # the sentence before


def test_pronoun_no_hit_when_it_fits() -> None:
    assert hits("Murzak shrugs the grab off, and you stagger against her weight.") == []
    assert hits("Ysrion lifts one hand, and his answer is curt.") == []


def test_pronoun_uncertain_subject_gives_no_verdict() -> None:
    assert hits("Murzak watches Varrka, and he grins.") == []  # two people named
    assert hits("He grins.", "Murzak watches the old man by the well.") == []  # an unnamed man is there
    assert hits("He grins at you.") == []  # no one named
    assert hits("Murzak whistles, and the dog trots up wagging his tail.") == []  # an animal can be "his"
    assert hits("Murzak nods, and he answers for her.") == []  # pronouns of both kinds: someone else is in it
    assert hits("\"He took it,\" Murzak says.") == []  # speech is not the narrator's voice
    assert hits("The merchant sets down his cup.", "Ysrion waits.") == []  # a stored label is the person
    assert hits("Then he turns his shoulder to the room, where Murzak waits.") == []  # named only after it
    assert hits("She turns back to you.", "Her glance slides to Varrka.") == []  # "Her" already meant someone else
    # replay corpus 20261007-213310 talker turn.9: the woman named earlier is meant, not the man aside
    assert hits("Her hand stays raised.", "Feney's hand comes up, palm out.", "Varrka stands by and says nothing.") == []


def test_pronoun_from_the_one_person_declared_about() -> None:
    assert hits("She leans on the rail.", about=("npc.ysrion",))
    assert hits("She leans on the rail.", about=("npc.ysrion", "npc.murzak")) == []


def test_pronoun_a_time_shift_clause_is_not_an_exemption_only_names_are() -> None:
    """The pronoun check has no time-shift words: last year's "his" is still the wrong pronoun."""
    assert hits("Last spring Murzak lost his purse.")


# ---------------------------------------------------------------------------------------- season_words


def test_season_hit_in_speech_and_narration() -> None:
    """Playtest 20261008-145410 talker, input 18: "the autumn harvest" on the spring quarter day. Spec 019: the check
    is measured at 0.5 precise (1 real of 2), below `min_precision`, so it hits and logs but never blocks."""
    assert hits("", speech=("Day wages, for the guild is taking on extra hands for the autumn harvest.",)) == [
        ("season_words", "speech", "autumn", False)]
    assert hits("Snow lies on the winter fields.") == [("season_words", "narrator", "winter", False)]


def test_season_no_hit() -> None:
    assert hits("The spring air is sharp with salt.") == []  # the calendar line's own season
    assert hits("Snow lies on the fields.", season="winter") == []
    assert hits("You spring to your feet.", season="autumn") == []  # the verb
    assert hits("Water rises from the spring behind the mill.", season="autumn") == []  # the well
    assert hits("You pass the Winter Gate.", season="spring") == []  # a name


def test_season_without_a_calendar_line_gives_no_verdict() -> None:
    assert hits("Snow lies on the winter fields.", season=None) == []


def test_season_time_shift_clause_allowed() -> None:
    assert hits("", speech=("The river flooded last autumn, and the mill went under.",)) == []
    assert hits("Two winters ago the well froze.") == []  # "winters" is no season word; "ago" would allow it too
    assert hits("", speech=("Since midwinter the road has been closed.",)) == []
    # replay corpus 20261007-194952 talker turn.4: a past winter, said so by its determiner
    assert hits("", speech=("The Broken Fells were the heart of a realm that fell in one bad winter.",)) == []
    assert hits("", speech=("The road closed, and the snow came in winter.",)) == [
        ("season_words", "speech", "winter", False)]  # the shift word must be in the season word's clause


# ---------------------------------------------------------------------------------------- demotion by data


def test_a_check_measured_below_min_precision_is_log_only() -> None:
    pc = RULES.pacing["claim_check"]["precision_checks"]
    low = [{**c, "precision": 0.5} if c["id"] == "season_words" else c for c in pc["checks"]]
    rules = SimpleNamespace(pacing={"claim_check": {"precision_checks": {**pc, "checks": low}}})
    assert hits("Snow lies on the winter fields.", rules=rules) == [("season_words", "narrator", "winter", False)]
    assert hits("Murzak loses his footing.", rules=rules)[0][3] is True  # the other check still blocks
