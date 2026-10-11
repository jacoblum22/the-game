"""Spec 033 P4 (people and testimony): cases C8 (walk-ons and identity) and C9 (testimony) of specs/033-dm-states-code-records/
cases.md, on the offline scripted DM. Nothing here asks code to read words: ids, `"pc"`, exact recorded names and the DM's
`as` are the only ways to name someone; everything else is the DM naming someone new."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from engine.dm import dm_tools
from engine.dm.npc_layer import is_animal
from engine.game import Game
from engine.gen import case
from engine.store.events import EntityRecord, Event
from engine.world.scenes import cast_present
from tests.engine.test_dm_tools import change, in_turn, npc_here, to_play
from tests.engine.test_spec032_p3 import roll

NODE = "clu.incident.duel.n1"  # the seeded game's first necessary clue node (it has one reserve entry)


def go(game: Game, *calls: dict[str, Any]) -> tuple[list[str], Any]:
    box: dict[str, Any] = {}

    def fn(ctx: Any, t: Any, tx: Any) -> list[str]:
        box["t"] = t
        return [dm_tools.tool(ctx, t, c) for c in calls]

    return in_turn(game, fn), box["t"]


def new_ids(game: Game, before: set[str]) -> list[str]:
    return sorted(set(game.store.state.entities) - before)


def said(game: Game, entries: list[dict[str, str]], setup: Any = None) -> dict[str, Any]:
    def fn(ctx: Any, t: Any, tx: Any) -> dict[str, Any]:
        if setup:
            setup(ctx, t, tx)
        t.said_raw = entries
        dm_tools._told(ctx, t)
        return t.stats

    return in_turn(game, fn)


# ------------------------------------------------------------------------------------------- C8: `as` x entry point


ENTRY = [
    change(kind="condition_add", who="the cook", what="shaken"),
    change(kind="npc_leaves", who="the cook"),
    change(kind="fight", who="the cook"),
    change(kind="coin", who="the cook", to="pc", amount=1),
    change(kind="give_item", who="the cook", what="item.dagger", to="pc"),
    change(kind="new_npc", what="the cook"),
    roll(verb="verb.talk", target="the cook", goal="ask", how="ask"),
]


@pytest.mark.parametrize("call", ENTRY, ids=lambda c: c.get("kind") or c["tool"])
@pytest.mark.parametrize(("as_", "pron"), [("he", "he/him"), ("she", "she/her"), ("they", "they/them")])
def test_c8_a_person_slot_with_as_makes_one_person_with_those_pronouns(tmp_path: Path, call: dict[str, Any], as_: str, pron: str) -> None:
    game, _ = to_play(tmp_path)
    before = set(game.store.state.entities)
    go(game, {**call, "as": as_})
    made = new_ids(game, before)
    assert len(made) == 1, made
    e = game.store.state.entities[made[0]]
    assert e.kind == "npc" and e.data["pronouns"] == pron and not is_animal(game.store.state, made[0])
    assert (made[0] in cast_present(game.store.state)) is (call.get("kind") != "npc_leaves")  # made here; leaving takes them away


def test_c8_creature_is_an_animal_and_no_person_is_rolled(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    before = set(game.store.state.entities)
    go(game, change(kind="fight", who="the wolfhound", **{"as": "creature"}))
    (eid,) = new_ids(game, before)
    e = game.store.state.entities[eid]
    assert e.data["mind"] == "animal" and "pronouns" not in e.data and "gender" not in e.data and is_animal(game.store.state, eid)


def test_c8_thing_makes_no_entity_and_new_npc_refuses_it(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    before = set(game.store.state.entities)
    outs, _ = go(game, roll(verb="verb.force", target="the stuck hatch", goal="open", how="shove", change_kind="open",
                            **{"as": "thing"}),
                 change(kind="new_npc", what="the stuck hatch", **{"as": "thing"}))
    assert outs[1].startswith("REFUSED")
    assert new_ids(game, before) == []


def test_c8_omitted_as_in_a_person_slot_is_they_and_logged(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    before = set(game.store.state.entities)
    _, t = go(game, change(kind="condition_add", who="the cook", what="shaken"))
    (eid,) = new_ids(game, before)
    assert game.store.state.entities[eid].data["pronouns"] == "they/them"
    assert "not_chosen:as" in t.stats["defaults"]


def test_c8_mood_and_reveal_clue_name_a_new_person_as_they_logged(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    before = set(game.store.state.entities)
    _, t = go(game, {"tool": "mood", "npc": "the cook", "mood": "wary", "why": "x"},
              {"tool": "reveal_clue", "npc": "the cook", "question": "what did you see?"})
    assert len(new_ids(game, before)) == 1 and "not_chosen:as" in t.stats["defaults"]


# ------------------------------------------------------------------------------------------- C8: identity


def test_c8_exact_name_resolves_partial_name_is_a_new_walk_on(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    st = game.store.state
    pick = npc_here(game)
    full = st.entities[pick].name
    part = full.split()[0]
    assert part != full

    def fn(ctx: Any, t: Any, tx: Any) -> tuple[Any, ...]:
        return (dm_tools._party(ctx, t, full, person=True), dm_tools._party(ctx, t, full.upper(), person=True),
                dm_tools._party(ctx, t, part, person=True, as_="he"))

    exact, upper, partial = in_turn(game, fn)
    assert exact == pick and upper == pick  # case-folded equality of the whole recorded name
    assert partial not in (pick, None) and partial in game.store.state.entities  # the DM must use the id


def test_c8_pc_literal_is_the_pc_and_you_or_the_player_are_only_words(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    pc = game.store.state.entities[next(i for i in game.store.state.entities if i.startswith("pc."))].id
    before = set(game.store.state.entities)

    def fn(ctx: Any, t: Any, tx: Any) -> tuple[Any, ...]:
        return (dm_tools._party(ctx, t, "pc", person=True), dm_tools._party(ctx, t, "you", person=True),
                dm_tools._party(ctx, t, "the player", person=True))

    a, b, c = in_turn(game, fn)
    assert a == pc and b not in (pc, None) and c not in (pc, None, b)
    assert len(new_ids(game, before)) == 2


def test_c8_two_entities_with_one_name_are_refused_with_their_ids_and_the_id_then_works(tmp_path: Path) -> None:
    """[spec 033 P10, owner: "what if there are two wolfhounds?"] Exact-name arithmetic: 2+ bearers = refuse, list ids."""
    game, _ = to_play(tmp_path)
    first = npc_here(game)
    twin = game.store.state.entities[first].name

    def dup(ctx: Any, t: Any, tx: Any) -> None:
        tx.add(Event.of("entity_created", source="engine", rule_id="PR-00-7",
                        entity=EntityRecord(id="npc.twin_of_a_name", kind="npc", name=twin, visibility="shown", data={})))

    in_turn(game, dup)
    before = set(game.store.state.entities)
    (out,), _ = go(game, roll(verb="verb.talk", target=twin, goal="ask", how="ask"))
    assert out.startswith("REFUSED: Two on record are called") and first in out and "npc.twin_of_a_name" in out
    assert out.rstrip().endswith("Use the id.") and new_ids(game, before) == []  # nothing written, no third one made
    (ok,), _ = go(game, roll(verb="verb.talk", target=first, goal="ask", how="ask"))
    assert not ok.startswith("REFUSED"), ok


def test_c8_new_npc_with_a_name_already_borne_is_still_made_and_told(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    twin = game.store.state.entities[npc_here(game)].name
    before = set(game.store.state.entities)
    (out,), _ = go(game, change(kind="new_npc", what="a ferryman", name=twin, **{"as": "he"}))
    (eid,) = new_ids(game, before)
    assert out.startswith("done") and f"Another is already called {twin!r}; use {eid} for this one." in out


def test_c8_a_sealed_entitys_exact_name_does_not_resolve(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    pick = npc_here(game)
    name = game.store.state.entities[pick].name

    def fn(ctx: Any, t: Any, tx: Any) -> str | None:
        tx.state.seals[pick] = {}
        return dm_tools._party(ctx, t, name, person=True, as_="he")

    got = in_turn(game, fn)
    assert got not in (pick, None)


def test_c8_new_npc_name_is_kept_and_the_same_words_twice_in_a_turn_are_one_walk_on(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    before = set(game.store.state.entities)
    outs, t = go(game, change(kind="new_npc", who="npc.hal", what="a ferryman", name="Hal", **{"as": "he"}),
                 roll(verb="verb.talk", target="npc.hal", goal="ask", how="ask"),
                 roll(verb="verb.sneak", target="npc.hal", goal="pass", how="slip by"))
    (eid,) = new_ids(game, before)
    assert game.store.state.entities[eid].name == "Hal" and game.store.state.entities[eid].data["role"] == "a ferryman"
    assert t.aliases["npc.hal"] == eid and outs[0].startswith("done")


def test_c8_new_npc_never_reuses_anyone(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    st = game.store.state
    role = str(st.entities[npc_here(game)].data.get("role") or "")
    before = set(st.entities)
    go(game, change(kind="new_npc", what=role, **{"as": "she"}), change(kind="new_npc", what=role, **{"as": "she"}),
       change(kind="new_npc", what=st.entities[npc_here(game)].name, **{"as": "she"}))
    assert len(new_ids(game, before)) == 3  # a role or a name on record is not a match: the DM said "new"


# ------------------------------------------------------------------------------------------- C8: knows


def holder_of(game: Game, node_id: str) -> list[str]:
    for c in case.cases(game.store.state).values():
        for n in c["nodes"]:
            if n["id"] == node_id:
                return [p["holder"] for p in n["placements"]]
    return []


def test_c8_knows_on_a_new_person_places_the_nodes_reserve_on_them(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    before = set(game.store.state.entities)
    held = holder_of(game, NODE)
    outs, _ = go(game, change(kind="new_npc", what="a ferryman", knows=NODE, **{"as": "he"}))
    (eid,) = new_ids(game, before)
    assert "now holds what" in outs[0]
    assert holder_of(game, NODE) == [*held, eid]


def test_c8_knows_on_a_new_item_places_it_as_an_object_holder(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    outs, _ = go(game, change(kind="new_item", what="a water-stained ledger", to="pc", knows=NODE))
    assert "now holds what" in outs[0]
    item = next(i for i in game.store.state.entities if "water_stained_ledger" in i)
    assert holder_of(game, NODE)[-1] == item
    node = next(n for c in case.cases(game.store.state).values() for n in c["nodes"] if n["id"] == NODE)
    assert node["placements"][-1]["holder_kind"] == "object"


def test_c8_knows_naming_no_node_is_told_not_guessed(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    held = holder_of(game, NODE)
    outs, _ = go(game, change(kind="new_npc", what="a ferryman", knows="the duel", **{"as": "he"}))
    assert "NOTE: knows 'the duel' names no clue node" in outs[0]
    assert holder_of(game, NODE) == held


# ------------------------------------------------------------------------------------------- C9: testimony


def test_c9_kept_as_given_whatever_the_words_say(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    here = npc_here(game)
    node = next(n for c in case.cases(game.store.state).values() for n in c["nodes"] if n["id"] == NODE)
    lines = ["The ford is shut.", "The ford is shut.", node["fact"], "Nothing in the passage says this."]
    stats = said(game, [{"npc": here, "words": w} for w in lines])
    assert stats["told_dropped"] == [] and [s["words"] for s in stats["said"]] == [w[:120] for w in lines]
    assert {s["speaker"] for s in stats["said"]} == {here}


def test_c9_dead_gone_or_absent_speakers_are_dropped_and_logged(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    st = game.store.state
    away = next(i for i, e in st.entities.items() if e.kind == "npc" and i not in cast_present(st))
    stats = said(game, [{"npc": away, "words": "I was never here."}, {"npc": npc_here(game), "words": "But I am."}])
    assert len(stats["told_dropped"]) == 1 and stats["told_dropped"][0]["npc"] == away
    assert [s["words"] for s in stats["said"]] == ["But I am."]


def test_c9_unknown_words_with_as_make_a_walk_on_then_the_line_is_kept(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    before = set(game.store.state.entities)
    stats = said(game, [{"npc": "a boy on the wall", "as": "he", "words": "Soldiers came at dusk."},
                        {"npc": "a boy on the wall", "as": "he", "words": "Three of them."}])
    (eid,) = new_ids(game, before)  # the same words twice in a turn: one person
    assert [s["speaker"] for s in stats["said"]] == [eid, eid] and game.store.state.entities[eid].data["pronouns"] == "he/him"
