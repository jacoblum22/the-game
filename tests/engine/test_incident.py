"""The opening incident's person is someone who exists (12.16.16; P-067), "who is X?" is settled among existing people
(12.3.2), and an NPC never answers with the player's own words (P-068)."""

from __future__ import annotations

from pathlib import Path

from engine.audit.screen import echoed_quotes
from engine.dm.context import TurnContext
from engine.dm.incident import INCIDENT, NO_ONE, settle_who
from engine.dm.packet import scene_setting
from engine.dm.session import opening
from engine.dm.world_step import _learnable
from engine.llm.offline import OfflineModel
from engine.store.events import Event
from tests.fixtures.game import entity, new_store

LOCALS = ["Ala Oakhill", "Bran Ford", "Cora Well", "Dun Ash", "Thanae Leafward"]


def _world(tmp_path: Path, option: str = "missing", seed: int = 1234, npcs: list[str] = LOCALS):
    store = new_store(tmp_path, seed=seed)
    with store.transaction() as tx:
        tx.add(entity("place", "Fernwell", tx=tx, data={"place_kind": "settlement"}))
        tx.add(entity("place", "Market", tx=tx, data={"place_kind": "site", "parent": "loc.fernwell"}))
        tx.add(entity("place", "Hollow Warren", tx=tx, data={"place_kind": "site"}))
        tx.add(entity("place", "Far Tower", tx=tx, data={"place_kind": "site"}))
        tx.add(entity("pc", "Wren", tx=tx, quantities={"vitality": (10, 0, 10)}))
        tx.add(Event.of("position_set", source="test", rule_id="10.1.1", entity="pc.wren", location="loc.market"))
        for n in npcs:
            e = entity("npc", n, tx=tx, data={"home": "loc.market", "depth": "minor"})
            tx.add(e)
            tx.add(Event.of("position_set", source="test", rule_id="12.16.11", entity=e.payload.entity.id,
                            location="loc.market"))
        far = entity("npc", "Old Power", tx=tx, data={"home": "loc.far_tower", "power": True})
        tx.add(far)
        tx.add(Event.of("fact_set", {"source": "player_accepted"}, source="test", rule_id="02.9.2", fact_id=tx.mint("fact"), subject="pc.wren",
                        predicate="bond.anchor", value={"npc": "npc.thanae_leafward", "kind": "friend"}))
        tx.add(Event.of("meta_set", source="test", rule_id="12.16.16", key="world.opening", value={
            "inciting": {"option": option, "text": "a child (or an elder, or a priest) is missing since last night"},
            "start": {"place": "loc.market"},
            "leads": [{"lead": "the incident itself: someone is missing", "points_to": "loc.hollow_warren"}]}))
    return store


def test_the_missing_person_is_an_existing_local_with_witnesses(tmp_path: Path) -> None:
    store = _world(tmp_path)
    resp = opening(TurnContext.for_store(store, model=OfflineModel()))
    st = store.state
    b = st.meta[INCIDENT]
    who = b["npc"]
    assert who in {f"npc.{n.lower().replace(' ', '_')}" for n in LOCALS} and who != "npc.thanae_leafward"
    assert st.fact_value(who, "is_missing") is True
    assert set(st.knowledge["pc.wren"]) >= set(b["known"])  # the reporter told the PC who is missing
    # two locals know one partial thing each, and a Talk can deliver it (learnable, not sealed)
    seen, heading = st.current_fact_id(who, "was_last_seen_at"), st.current_fact_id(who, "was_seen_heading_toward")
    assert st.facts[heading].value == "loc.hollow_warren"
    assert seen in st.knowledge[b["witnesses"][0]] and heading in st.knowledge[b["witnesses"][1]]
    assert _learnable(st, st.facts[seen], "pc.wren") and _learnable(st, st.facts[heading], "pc.wren")
    name = st.entities[who].name
    assert f"{name} is missing" in scene_setting(st) and resp.fiction
    assert store.rebuild() == store.state
    # the same seed binds the same person
    again = _world(tmp_path / "b")
    opening(TurnContext.for_store(again, model=OfflineModel()))
    assert again.state.meta[INCIDENT]["npc"] == who


def test_an_incident_without_a_person_binds_nothing(tmp_path: Path) -> None:
    store = _world(tmp_path, option="omen")
    opening(TurnContext.for_store(store, model=OfflineModel()))
    assert INCIDENT not in store.state.meta


def _ask(store, text: str):
    ctx = TurnContext.for_store(store, model=OfflineModel())
    with store.transaction() as tx:
        ctx.tx = tx
        try:
            return settle_who(ctx, text)
        finally:
            ctx.tx = None


def test_who_questions_name_an_existing_person_and_stay_answered(tmp_path: Path) -> None:
    store = _world(tmp_path)
    opening(TurnContext.for_store(store, model=OfflineModel()))
    name = store.state.entities[store.state.meta[INCIDENT]["npc"]].name
    assert _ask(store, "who the missing person is (name and household, as known in Fernwell)")[0] == name
    assert _ask(store, "who is missing")[0] == name
    enemy = _ask(store, "who is the old enemy")
    assert enemy[0] in LOCALS[:-1]  # an existing person, never the anchor bond or a far power
    assert _ask(store, "who is the old enemy") == enemy  # settled once
    assert _ask(store, "who is here") is None and _ask(store, "is the door locked") is None  # the Oracle's


def test_who_with_no_one_fitting_is_no_one_you_know(tmp_path: Path) -> None:
    store = _world(tmp_path, npcs=[])
    assert _ask(store, "who is the old enemy")[0] == NO_ONE


def test_an_npc_echoing_the_players_quote_is_caught() -> None:
    said = ['I step up. "Captain, someone is missing. Who is it?"']
    echo = 'He laughs. "Captain, someone is missing. Who is it?" His thumbs stay hooked in his belt.'
    own = '"Captain, someone is missing. Who is it?" you ask. He shrugs. "Ask the miller."'
    assert echoed_quotes(echo, said) == ["Captain, someone is missing. Who is it?"]
    assert echoed_quotes(own, said) == []
