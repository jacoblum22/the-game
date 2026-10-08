"""Write-on-mention (00.6.6, PR-00-7): only implied properties, unsettled ones settled now, NPCs per PR-12-5,
dedupe by name or alias, no creation for kinds that are never written on mention."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from engine import ids
from engine.data.loader import load_rules
from engine.dm.mentions import Mention, find_existing, write_mentions
from engine.rng import Rng
from engine.store.events import Event, SceneRecord
from tests.fixtures.game import entity, new_store


@pytest.fixture(scope="module")
def rules() -> Any:
    return load_rules()


def _game(tmp_path: Path) -> tuple[Any, Rng]:
    store = new_store(tmp_path)
    rng = Rng.for_store(store)
    with store.transaction("turn.0") as tx:
        tx.add(entity("pc", "Wren", tx=tx))
        tx.add(entity("place", "Old Archive", tx=tx))
        tx.add(entity("npc", "Mara Voss", tx=tx, data={"role": "fence", "aliases": ["the fence"]}))
        sid = tx.mint(ids.SCENE)
        tx.add(Event.of("scene_started", scene_id=sid,
                        scene=SceneRecord(scene_id=sid, place_id="loc.old_archive", cast_present=["npc.mara_voss"])))
    return store, rng


def test_object_with_only_implied_properties(tmp_path: Path, rules: Any) -> None:
    store, rng = _game(tmp_path)
    with store.transaction("turn.1") as tx:
        res = write_mentions([{"kind": "object", "name": "a rope ladder",
                               "implied": [{"predicate": "hangs from", "value": "the gallery"}], "unsettled": []}],
                             tx=tx, rules=rules, rng=rng)
    eid = res.created["a rope ladder"]
    e = store.state.entities[eid]
    assert (eid, e.name, e.kind, e.data) == ("obj.rope_ladder", "rope ladder", "object", {})
    assert store.state.fact_value(eid, "hangs_from") == "the gallery"
    assert store.state.positions[eid].location == "loc.old_archive"
    assert {store.event(s).type for s in res.seqs} == {"entity_created", "position_set", "fact_set"}  # type: ignore[union-attr]
    assert store.rebuild() == store.state


def test_the_words_on_a_notice_are_kept_shown_and_checked(tmp_path: Path, rules: Any) -> None:
    """P-041: a narrated inscription is stored with the object, shown to the narrator on later turns, and a later
    claim about the same words is judged against it (not asked of the Oracle anew)."""
    from engine.audit.claims import check_claims
    from engine.dm.adjudication import AdjudicationRecord
    from engine.dm.packet import render_view, scene_view
    from engine.dm.roles.checker import checker_ids

    store, rng = _game(tmp_path)
    words = "THE LODGE IS TAKING HANDS / NO QUESTIONS ASKED"
    with store.transaction("turn.1") as tx:
        res = write_mentions([{"kind": "object", "name": "the lodge notice",
                               "implied": [{"predicate": "text", "value": words}]}], tx=tx, rules=rules, rng=rng)
    eid = res.created["the lodge notice"]
    assert store.state.fact_value(eid, "text") == words
    assert eid in checker_ids(store.state)  # the Checker may name it on a later turn
    assert f"about {eid}: text = {words}" in render_view(scene_view(store.state))  # the narrator sees it again

    def verdict(predicate: str, value: str) -> str:
        claim = {"subject": eid, "class": "identity", "predicate": predicate, "value": value}
        [v] = check_claims([claim], store.state, AdjudicationRecord(), [eid], rules=rules)
        return v.verdict

    assert verdict("smaller text reads", "NO QUESTIONS ASKED") == "supported"
    assert verdict("reads beneath", "NO QUESTIONS ASKED") == "supported"
    assert verdict("smaller letters", "do not say NO QUESTIONS ASKED") == "contradicted"


def test_dedupe_and_refusals(tmp_path: Path, rules: Any) -> None:
    store, rng = _game(tmp_path)
    assert find_existing(store.state, "The Fence", "npc") == "npc.mara_voss"
    n = len(store.state.entities)
    with store.transaction("turn.1") as tx:
        res = write_mentions([Mention(kind="npc", name="Mara Voss"), Mention(kind="npc", name="the fence"),
                              Mention(kind="clue", name="a hidden map"), Mention(kind="adversary", name="a bear")],
                             tx=tx, rules=rules, rng=rng)
    assert res.reused == {"Mara Voss": "npc.mara_voss", "the fence": "npc.mara_voss"}
    # P-036: the given name alone is the same person, not a new walk-on "Mara" (the bond NPC stays one entity)
    assert find_existing(store.state, "Mara", "npc") == "npc.mara_voss"
    assert find_existing(store.state, "Voss", "npc") is None and find_existing(store.state, "Mara", "item") is None
    assert res.refused == ["a hidden map", "a bear"] and not res.created
    assert len(store.state.entities) == n


def test_npc_by_description_is_a_walk_on(tmp_path: Path, rules: Any) -> None:
    store, rng = _game(tmp_path)
    with store.transaction("turn.1") as tx:
        res = write_mentions([Mention(kind="npc", name="the ferryman")], tx=tx, rules=rules, rng=rng)
    eid = res.created["the ferryman"]
    data = store.state.entities[eid].data
    assert data["role"] == "ferryman"
    for field in ("gender", "pronouns", "age", "detail", "demeanor"):  # rolled and written at once (12.11.1)
        assert data.get(field), field
    assert eid in (store.state.meta.get("cast_list") or {})
    assert store.rng_draws(), "walk-on fields are rolled on the logged RNG"
    assert store.rebuild() == store.state


def test_named_npc_keeps_the_drafts_identity(tmp_path: Path, rules: Any) -> None:
    store, rng = _game(tmp_path)
    m = {"kind": "npc", "name": "Bessa Crane", "unsettled": [],
         "implied": [{"predicate": "gender", "value": "woman"}, {"predicate": "role", "value": "boatwright"},
                     {"predicate": "carries", "value": "an adze"}]}
    with store.transaction("turn.1") as tx:
        res = write_mentions([m], tx=tx, rules=rules, rng=rng)
    eid = res.created["Bessa Crane"]
    e = store.state.entities[eid]
    assert (eid, e.name) == ("npc.bessa_crane", "Bessa Crane")
    assert (e.data["gender"], e.data["pronouns"], e.data["role"]) == ("woman", "she/her", "boatwright")
    assert store.state.fact_value(eid, "carries") == "an adze"
    assert store.state.fact_value(eid, "gender") is None  # identity lives in data, not duplicated as facts
    assert store.state.meta["cast_list"][eid] == 1


def test_unsettled_by_oracle_table_or_injection(tmp_path: Path, rules: Any) -> None:
    store, rng = _game(tmp_path)
    with store.transaction("turn.1") as tx:
        res = write_mentions([{"kind": "object", "name": "the iron door", "implied": [], "unsettled": ["locked"]},
                              {"kind": "npc", "name": "Old Pell", "implied": [{"predicate": "role", "value": "porter"}],
                               "unsettled": ["voice register"]},
                              {"kind": "item", "name": "a wax seal", "implied": [], "unsettled": ["colour"]}],
                             tx=tx, rules=rules, rng=rng, settle=None)
    door = res.created["the iron door"]
    s = {x.property: x for x in res.settled}
    assert s["locked"].how == "oracle" and isinstance(store.state.fact_value(door, "locked"), bool)
    assert s["voice register"].how == "table:tbl.npc_voice_register"
    assert s["colour"].how == "oracle"
    with store.transaction("turn.2") as tx:
        res2 = write_mentions([{"kind": "item", "name": "a lantern", "implied": [], "unsettled": ["lit", "colour"]}],
                              tx=tx, rules=rules, rng=rng, settle=lambda e, p: True if p == "lit" else None)
    lantern = res2.created["a lantern"]
    assert store.state.fact_value(lantern, "lit") is True
    assert res2.unsettled == [(lantern, "colour")]
    assert store.rebuild() == store.state
