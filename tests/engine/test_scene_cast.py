"""P-095: the people the scene presents are the store's scene cast, and an unintroduced NPC has one label.

The opening described the herb-wife and the faction heads positioned at the shrine, but the scene record held only
the framed walk-on, so later views, the claim check and [LEADS] dropped them; the walk-on was "a grieving old man"
in prose but "the boatman or sailor" on every other screen."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from engine import ids
from engine.audit.claims import check_claims
from engine.data.loader import load_rules
from engine.dm.adjudication import AdjudicationRecord
from engine.dm.mentions import find_existing, write_mentions
from engine.dm.packet import scene_setting
from engine.dm.turn import stuck_answer
from engine.retrieve.scene import scene_scope
from engine.rng import Rng
from engine.store.events import Event, SceneRecord
from engine.store.views import display_name
from tests.fixtures.game import entity, new_store

PLACE = "loc.shrine"


@pytest.fixture(scope="module")
def rules() -> Any:
    return load_rules()


def _game(tmp_path: Path) -> tuple[Any, Rng]:
    store = new_store(tmp_path)
    with store.transaction("turn.0") as tx:
        tx.add(entity("pc", "Wren", tx=tx))
        tx.add(entity("place", "Shrine", tx=tx))
        tx.add(entity("place", "Inn", tx=tx))
        tx.add(entity("npc", "Gunnvald", tx=tx, data={"role": "herb-wife", "detail": "a badly set nose",
                                                       "name_known": False}))
        tx.add(entity("npc", "Borvald", tx=tx, data={"role": "boatman or sailor", "age": "old",
                                                      "demeanor": "grieving", "name_known": False}))
        tx.add(entity("npc", "Ariwen", tx=tx, data={"role": "innkeeper"}))
        for npc, where in (("npc.gunnvald", PLACE), ("npc.borvald", PLACE), ("npc.ariwen", "loc.inn"),
                           ("pc.wren", PLACE)):
            tx.add(Event.of("position_set", entity=npc, location=where))
        sid = tx.mint(ids.SCENE)  # framed with the walk-on only, as the opening did
        tx.add(Event.of("scene_started", scene_id=sid,
                        scene=SceneRecord(scene_id=sid, place_id=PLACE, cast_present=["npc.borvald"])))
    return store, Rng.for_store(store)


def test_everyone_positioned_here_is_in_the_scene_cast(tmp_path: Path, rules: Any) -> None:
    store, _ = _game(tmp_path)
    st = store.state
    assert st.scene is not None and set(st.scene.cast_present) == {"npc.borvald", "npc.gunnvald"}
    assert "npc.gunnvald" in scene_scope(st) and "npc.ariwen" not in scene_scope(st)  # the narrator's view
    absent = {"subject": "npc.gunnvald", "class": "existence", "predicate": "present", "value": "not here, absent"}
    [v] = check_claims([absent], st, AdjudicationRecord(), scene_scope(st), rules=rules)
    assert v.verdict == "contradicted"  # "no herb-wife stands here" is false
    assert store.rebuild() == store.state


def test_mid_scene_arrivals_join_and_leavers_go(tmp_path: Path, rules: Any) -> None:
    store, rng = _game(tmp_path)
    with store.transaction("turn.1") as tx:
        tx.add(entity("npc", "Osard", tx=tx, data={"role": "head of the Stoneley Circle"}))  # placed nowhere
        res = write_mentions([{"kind": "npc", "name": "the head of the Stoneley Circle"},
                              {"kind": "npc", "name": "the child", "implied": [{"predicate": "appearance",
                                                                                 "value": "face turned away"}]}],
                             tx=tx, rules=rules, rng=rng)
    st = store.state
    child = res.created["the child"]
    assert res.reused["the head of the Stoneley Circle"] == "npc.osard"
    assert st.positions["npc.osard"].location == PLACE
    assert {"npc.osard", child} <= set(st.scene.cast_present)  # type: ignore[union-attr]
    with store.transaction("turn.2") as tx:
        tx.add(Event.of("position_set", entity="npc.gunnvald", location="loc.inn"))
    assert "npc.gunnvald" not in store.state.scene.cast_present  # type: ignore[union-attr]
    assert store.rebuild() == store.state


def test_one_label_per_unintroduced_npc(tmp_path: Path, rules: Any) -> None:
    store, rng = _game(tmp_path)
    st = store.state
    assert display_name(st, "npc.borvald") == "the boatman"  # one person, not "the boatman or sailor"
    assert find_existing(st, "the boatman", "npc") == "npc.borvald"  # the label finds him again
    setting = scene_setting(st)
    assert 'call them "the boatman"' in setting and 'call them "the herb-wife"' in setting
    leads = stuck_answer(st)
    assert "the boatman, here with you" in leads and "innkeeper" not in leads
    with store.transaction("turn.1") as tx:  # a walk-on made from prose keeps the prose's words as their label
        res = write_mentions([{"kind": "npc", "name": "the old woman",
                               "implied": [{"predicate": "profession", "value": "ferry hand"}]}],
                             tx=tx, rules=rules, rng=rng)
    assert display_name(store.state, res.created["the old woman"]) == "the old woman"
