"""Spec 032 P8a: the people and things the DM names. Cases P1-P15 of specs/032-dm-tools-mvp/cases.md (section P8a), on the
offline scripted DM. [spec 033 P4] Rewritten to R6/R8: kinds come from data, a new person or creature is made only when
the DM says so with `as`, the same words are matched only as an exact id or exact recorded name, `said` is spine-only."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from engine.dm import dm_tools
from engine.dm.npc_layer import is_animal
from engine.game import Game
from engine.harm.state import DEAD
from engine.world.common import fact
from engine.world.places import location, reachable
from engine.world.scenes import cast_present
from tests.engine.test_dm_tools import change, in_turn, npc_here, to_play
from tests.engine.test_spec032_cases import RULES
from tests.engine.test_spec032_p3 import roll

PERSON = "the sentry on the wall-walk"
CREATURE = "the wolfhound"
THING = "the stuck hatch"
KINDS = {
    "verb.talk": ("person",), "verb.grapple": ("person",), "verb.sneak": ("person",), "verb.help": ("person",),
    "verb.strike": ("person", "object"), "verb.force": ("person", "object"), "verb.setup": ("person", "object"),
    "verb.observe": ("object", "person"), "verb.handle": ("object", "person"), "verb.move": ("object", "person"),
    "verb.exert": ("object",), "verb.endure": ("object",),
    "verb.recall": (), "verb.evade": (), "verb.ready": (),
}


def go(game: Game, *calls: dict[str, Any]) -> tuple[list[str], Any]:
    box: dict[str, Any] = {}

    def fn(ctx: Any, t: Any, tx: Any) -> list[str]:
        box["t"] = t
        return [dm_tools.tool(ctx, t, c) for c in calls]

    return in_turn(game, fn), box["t"]


def new_ids(game: Game, before: set[str]) -> list[str]:
    return sorted(set(game.store.state.entities) - before)


def test_p1_the_target_kinds_come_from_the_rules_data(tmp_path: Path) -> None:
    got = {v: dm_tools.target_kinds(RULES, v) for v in RULES.ids("verb.")}
    assert got == KINDS  # 15 verbs, read from basic_verbs.yaml (targets knob, then against, then eligibility)
    assert dm_tools.target_is_person(RULES, "verb.talk", "open") and not dm_tools.target_is_person(RULES, "verb.observe", None)
    # a verb that takes both: the DM's change kind says which (resolution.yaml slots)
    assert [dm_tools.target_is_person(RULES, "verb.strike", k) for k in ("open", "close", "take", "persuade_to", "restrain", "harm")] \
        == [False, False, False, True, True, True]


@pytest.mark.parametrize("verb", sorted(KINDS))
@pytest.mark.parametrize(("phrase", "what"), [(PERSON, "person"), (CREATURE, "creature"), (THING, "thing")])
def test_p2_every_verb_times_a_person_a_creature_a_thing_is_never_refused_as_unknown(
        tmp_path: Path, verb: str, phrase: str, what: str) -> None:
    game, _ = to_play(tmp_path)
    before = set(game.store.state.entities)
    extra = {"as": "creature"} if what == "creature" else {}  # [spec 033 R6] the DM says what it is
    outs, _ = go(game, roll(verb=verb, target=phrase, goal="act", how="act", **extra))
    # (cases C1.a) a melee verb on a stranger is refused for reach (06.4.3) after the walk-on is made; never as unknown
    assert not (outs[0].startswith("REFUSED") and "on record" in outs[0] and "not in reach" not in outs[0]), outs[0]
    made = new_ids(game, before)
    st = game.store.state
    if what == "creature":
        assert len(made) == 1 and is_animal(st, made[0]) and st.entities[made[0]].data["mind"] == "animal"
    elif what == "person" and KINDS[verb][:1] == ("person",):
        assert len(made) == 1 and st.entities[made[0]].kind == "npc" and not is_animal(st, made[0])
    elif what == "thing" and KINDS[verb][:1] != ("person",):
        assert made == []  # an obstacle in words: nothing is made for it


def test_p3_h02_the_dms_own_id_for_a_new_npc_is_the_person_made(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    outs, t = go(game, change(kind="new_npc", who="npc.eel_seller", what="an eel seller at a wooden barrel"),
                 roll(verb="verb.talk", target="npc.eel_seller", goal="haggle", how="half price", change_kind="persuade_to",
                      change_what="half price", change_whom="npc.eel_seller"))
    made = t.aliases["npc.eel_seller"]
    assert made in game.store.state.entities and game.store.state.entities[made].kind == "npc"
    assert outs[1].startswith("ROLL OFFERED"), outs[1]
    sellers = [i for i, e in game.store.state.entities.items() if "eel seller" in str(e.data.get("role", ""))]
    assert sellers == [made]  # one seller, not two


@pytest.mark.parametrize(("verb", "ident"), [("verb.observe", "npc.rider_on_the_ridge"), ("verb.sneak", "npc.watch_sentry"),
                                             ("verb.talk", "npc.hooded_pilgrim")])
def test_p4_an_unknown_id_with_as_is_the_dm_naming_a_walk_on(tmp_path: Path, verb: str, ident: str) -> None:
    """[spec 033 R6] A made-up id is a walk-on when the DM says `as` (any verb, person slot or not); the same words
    twice in one turn are the one person. Without `as`, an object slot leaves the word alone."""
    game, _ = to_play(tmp_path)
    before = set(game.store.state.entities)
    outs, _ = go(game, roll(verb=verb, target=ident, goal="act", how="act", **{"as": "she"}),
                 roll(verb=verb, target=ident, goal="act", how="act", **{"as": "she"}))
    assert not any(o.startswith("REFUSED") and "on record" in o for o in outs), outs
    made = new_ids(game, before)
    assert len(made) == 1 and game.store.state.entities[made[0]].kind == "npc" and made[0] in cast_present(game.store.state)
    assert game.store.state.entities[made[0]].data["pronouns"] == "she/her"


def test_p4b_an_object_slot_without_as_makes_nobody(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    before = set(game.store.state.entities)
    go(game, roll(verb="verb.observe", target="npc.rider_on_the_ridge", goal="look", how="look"))
    assert new_ids(game, before) == []


def test_p5_an_invented_object_id_is_not_refused_and_makes_no_person(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    before = set(game.store.state.entities)
    outs, _ = go(game, roll(verb="verb.force", target="object.stuck_hatch", goal="force it", how="shoulder it",
                            change_kind="open"))
    assert not (outs[0].startswith("REFUSED") and "on record" in outs[0]), outs[0]
    assert new_ids(game, before) == [] or all(game.store.state.entities[i].kind not in ("npc", "companion") for i in new_ids(game, before))


def test_p6_nothing_is_matched_the_dm_uses_the_id_and_the_situation_shows_it(tmp_path: Path) -> None:
    """The same person called by a second name next turn is a new walk-on (no head-noun matching); the id in the situation
    is the way back. [spec 033 R6] The role is the DM's words as given."""
    game, _ = to_play(tmp_path)
    first = in_turn(game, lambda ctx, t, tx: dm_tools._party(ctx, t, "the rider on the grey horse", person=True))
    second = in_turn(game, lambda ctx, t, tx: dm_tools._party(ctx, t, "the horseman", person=True))
    assert first != second  # no head-noun, role or alias matching
    seen = in_turn(game, lambda ctx, t, tx: dm_tools.situation(ctx))
    assert first in seen and second in seen and "rider on the grey horse" in seen  # id and the DM's words
    assert in_turn(game, lambda ctx, t, tx: dm_tools._party(ctx, t, first, person=True)) == first  # by id: that entity
    roles = [str(e.data.get("role")) for e in game.store.state.entities.values()]
    assert "the rider on the grey horse" in roles and "the horseman" in roles


def test_p6b_a_hundred_ways_of_introducing_someone_all_work_because_nothing_is_matched(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    adj = ["old", "tall", "one-eyed", "hooded", "Marta's", "the tired", "a young", "some", "that", "this"]
    role = ["carter", "sentry", "woman at the well", "rider on the ridge", "man with a lantern", "kid", "Hesk", "pilgrim",
            "tinker's wife", "npc.stranger_%d"]
    phrases = [f"{a} {r}" if not r.startswith("npc.") else r.replace("%d", str(i)) for i, a in enumerate(adj) for r in role]
    assert len(set(phrases)) == 100

    def fn(ctx: Any, t: Any, tx: Any) -> list[str | None]:
        return [dm_tools._party(ctx, t, p, person=True) for p in phrases]

    got = in_turn(game, fn)
    st = game.store.state
    assert len(set(got)) == 100 and all(g in st.entities and g in cast_present(st) for g in got)


def test_p7_a_strike_at_a_door_to_open_it_is_an_object_not_a_person(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    before = set(game.store.state.entities)
    outs, _ = go(game, roll(verb="verb.strike", target="the stuck door", goal="break it", how="kick", change_kind="open",
                            change_what="the stuck door"))
    assert not (outs[0].startswith("REFUSED") and "on record" in outs[0]), outs[0]
    assert new_ids(game, before) == []


def said(game: Game, entries: list[dict[str, str]], setup: Any = None) -> dict[str, Any]:
    def fn(ctx: Any, t: Any, tx: Any) -> dict[str, Any]:
        if setup:
            setup(ctx, t, tx)
        t.said_raw = entries
        dm_tools._told(ctx, t)
        return t.stats

    return in_turn(game, fn)


def test_p9_p10_a_new_speaker_the_dm_names_with_as_becomes_a_walk_on_and_the_line_is_kept(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    before = set(game.store.state.entities)
    stats = said(game, [{"npc": "the carter at the trough", "as": "he", "words": "Toll-house is shut since the flood."},
                        {"npc": "npc.longbridge_man", "as": "she", "words": "Ask for Wenna if you cross."}])
    assert stats["told_dropped"] == [] and len(stats["said"]) == 2, stats
    made = new_ids(game, before)
    assert len(made) == 2 and {s["speaker"] for s in stats["said"]} == set(made)
    assert all(m in cast_present(game.store.state) for m in made)


def test_p11_a_line_is_kept_as_given_no_passage_check_and_no_as_means_they_logged(tmp_path: Path) -> None:
    """[spec 033 C9] No check of the words against a passage, earlier lines or clues; code only records."""
    game, _ = to_play(tmp_path)
    stats = said(game, [{"npc": "the ghost of nobody", "words": "I saw the smoke from the hill at dawn."}])
    assert stats["told_dropped"] == [] and len(stats["said"]) == 1
    assert "not_chosen:as" in stats["defaults"]
    again = said(game, [{"npc": "the ghost of nobody", "words": "I saw the smoke from the hill at dawn."}])
    assert len(again["said"]) == 1  # a line repeated from earlier is kept too


@pytest.mark.parametrize("by", ["id", "name"])
@pytest.mark.parametrize("state", ["elsewhere", "dead"])
def test_p12_a_speaker_on_record_elsewhere_or_dead_is_dropped_and_not_made_twice(tmp_path: Path, by: str, state: str) -> None:
    game, _ = to_play(tmp_path)
    st = game.store.state
    pick = npc_here(game) if state == "dead" else next(i for i, e in st.entities.items()
                                                       if e.kind == "npc" and i not in cast_present(st))
    e = st.entities[pick]
    label = e.name if by == "name" else pick
    words = "The levee will hold if the rain stops by the new moon."
    before = set(st.entities)

    def kill(ctx: Any, t: Any, tx: Any) -> None:
        if state == "dead":
            tx.add(fact(tx, pick, "harm_state", DEAD, rule_id="07.1.3"))

    stats = said(game, [{"npc": label, "words": words}], setup=kill)
    assert stats["said"] == [] and len(stats["told_dropped"]) == 1, stats
    assert ("dead" if state == "dead" else "not here") in stats["told_dropped"][0]["why"]
    assert new_ids(game, before) == []  # no second person


def far(game: Game) -> str:
    here = location(game.store.state)
    return next(x.to for x in reachable(game.store.state, here) if x.to != here)


def where(game: Game, eid: str) -> str | None:
    return location(game.store.state, eid)


def test_p13_the_named_companion_walks_with_the_character_across_two_travels(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    comp = npc_here(game)
    name = dm_tools._name(game.store.state, comp)
    first = far(game)
    out, _ = go(game, change(kind="travel", to=first, who=comp))
    assert out[0].startswith("done") and f"With the character: {name}" in out[0], out[0]
    assert where(game, comp) == first and comp in cast_present(game.store.state)
    second = far(game)
    out, _ = go(game, change(kind="travel", to=second, who=comp))
    assert out[0].startswith("done"), out[0]
    assert where(game, comp) == second and comp in cast_present(game.store.state)
    assert dm_tools._acting(game.store.state, comp) == ""  # still here: she can be asked, her lines are filed
    stats = said(game, [{"npc": comp, "words": "The road bends past the mill."}])
    assert len(stats["said"]) == 1 and stats["told_dropped"] == []


def test_p14_nobody_comes_unless_the_dm_names_them_and_the_unnamed_or_absent_are_reported(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    comp = npc_here(game)
    st = game.store.state
    other = next(i for i, e in st.entities.items() if e.kind == "npc" and i not in cast_present(st))
    start = where(game, comp)
    first = far(game)
    out, _ = go(game, change(kind="travel", to=first))
    assert out[0].startswith("done") and where(game, comp) == start and "With the character" not in out[0]
    back = next(x.to for x in reachable(game.store.state, first))
    out, _ = go(game, change(kind="travel", to=back, who="nobody called Zed"))
    assert out[0].startswith("done") and "Did not come: no one on record called" in out[0]
    assert other


def test_p15_two_named_people_both_come(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    here = cast_present(game.store.state)
    if len(here) < 2:
        def add(ctx: Any, t: Any, tx: Any) -> str:
            return dm_tools.tool(ctx, t, change(kind="new_npc", what="a ferryman"))

        in_turn(game, add)
        here = cast_present(game.store.state)
    a, b = here[0], here[1]
    names = f"{a}, {b}"
    out, _ = go(game, change(kind="travel", to=far(game), who=names))
    assert out[0].startswith("done"), out[0]
    assert where(game, a) == where(game, b) == location(game.store.state)
