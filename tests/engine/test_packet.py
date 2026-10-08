"""The packet builder (T106): contract order, caps, and no growth with turn count (FR-029, SC-002)."""

from __future__ import annotations

import random
from pathlib import Path

import pytest

from engine.build.compile_cards import load_cards
from engine.data.loader import load_rules
from engine.dm.packet import PacketError, build_packet, render_view, scene_view
from engine.llm.base import Role
from engine.llm.offline import OfflineModel, view_names
from engine.retrieve.cards import load_cards_for
from engine.retrieve.scene import tokens
from engine.retrieve.triggers import get_active_triggers
from engine.store.db import Store
from engine.store.events import Event
from tests.fixtures.game import entity, new_store

RULES = load_rules()
INDEX = load_cards()
EXCHANGE = ("I look around the quay.", "Gulls wheel over the empty boats. What do you do?")


def fact(tx, subject: str, predicate: str, value, **kw) -> Event:
    return Event.of("fact_set", {"source": "narration"}, fact_id=tx.mint("fact"), subject=subject,
                    predicate=predicate, value=value, supersedes=tx.state.current_fact_id(subject, predicate),
                    visibility="shown", **kw)


def scene_store(tmp_path: Path) -> Store:
    s = new_store(tmp_path)
    with s.transaction("turn.1") as tx:
        tx.add(entity("pc", "Wren", tx=tx, quantities={"vitality": (10, 0, 10)}))
        tx.add(entity("place", "Salt Harbor", tx=tx))
        tx.add(entity("npc", "Mara Voss", tx=tx, data={"role": "fence"}))
        tx.add(entity("npc", "Tam Harlan", tx=tx, sealed={"secret": "smuggler"}))
        sid = tx.mint("scn")
        tx.add(Event.of("scene_started", scene_id=sid, scene={
            "scene_id": sid, "place_id": "loc.salt_harbor", "cast_present": ["npc.mara_voss", "npc.tam_harlan"],
            "mode": "free", "agenda": "find who sank the boat", "situation_tags": ["situation.social"]}))
        tx.add(fact(tx, "npc.mara_voss", "attitude", "wary"))
    return s


def packet_for(store: Store, role: Role, exchanges, message: str = "I ask Mara Voss about the boat."):
    trig = get_active_triggers(store.state, RULES)
    scene = store.state.scene
    cards = load_cards_for(role, scene.situation_tags if scene else [], scene.mode if scene else None, trig, [],
                           rules=RULES)
    return build_packet(role, instructions="You are the reader.", cards=cards, view=store.state,
                        exchanges=exchanges, message=message, triggers=trig, rules=RULES)


def test_sections_come_in_contract_order(tmp_path: Path) -> None:
    store = scene_store(tmp_path)
    p = packet_for(store, Role.READER, [EXCHANGE])
    assert [k for k, _ in p.sections()] == ["instructions", "core", "cards", "view", "exchanges", "message"]
    for core_id in ("T-12-1", "T-00-1", "00.12.3", "00.3.9", "00.3.14", "00.3.15"):
        assert INDEX.get(core_id).body.strip() in p.core
    assert "Active triggers" not in p.core and p.view.startswith("Active triggers: none\n")  # DL-12-38
    assert p.message == "I ask Mara Voss about the boat."
    assert p.render().endswith("I ask Mara Voss about the boat.")


def test_exactly_the_last_four_exchanges_verbatim(tmp_path: Path) -> None:
    store = scene_store(tmp_path)
    history = [(f"player {i}", f"dm {i}") for i in range(10)]
    p = packet_for(store, Role.NARRATOR, history)
    assert p.exchanges == [f"Player: player {i}\nDM: dm {i}" for i in range(6, 10)]
    assert packet_for(store, Role.NARRATOR, ["raw text"]).exchanges == ["raw text"]


def test_more_than_twelve_cards_is_refused(tmp_path: Path) -> None:
    store = scene_store(tmp_path)
    cards = [c for c in INDEX if c.kind == "rule"][:13]
    with pytest.raises(PacketError):
        build_packet(Role.READER, instructions="", cards=cards, view=store.state, exchanges=[], message="hi",
                     rules=RULES)


def test_view_names_entities_and_hides_sealed_data(tmp_path: Path) -> None:
    store = scene_store(tmp_path)
    text = render_view(scene_view(store.state))
    assert "npc.mara_voss: Mara Voss" in text and "  name: Mara Voss" in text
    assert "smuggler" not in text  # a sealed field never reaches a packet (INV-10)
    assert view_names(text)[:2] == ["Wren", "Mara Voss"]
    assert "fact.1 about npc.mara_voss: attitude = wary" in text
    out = OfflineModel().propose(Role.NARRATOR, {"type": "object"},
                                 packet_for(store, Role.NARRATOR, [], message='- part [SPEECH] "Evening, Mara."'))
    assert "Mara Voss" in out["fiction"]  # a reply from the named NPC in the view


def test_quiet_turns_and_notes_go_after_the_view(tmp_path: Path) -> None:
    store = scene_store(tmp_path)
    p = build_packet(Role.DIRECTOR, instructions="", cards=[], view=store.state, exchanges=[], message="",
                     quiet_turns=3, notes=["anc.x: menu line"], rules=RULES)
    assert p.view.endswith("anc.x: menu line\nquiet_turns: 3")
    data = OfflineModel().propose(Role.DIRECTOR, {"type": "object"}, p)
    assert data["cut_now"] is True


def test_packet_size_does_not_grow_with_turn_count(tmp_path: Path) -> None:
    """1,000+ events, hundreds of facts and entities: the packet stays the size of the scene (SC-002)."""
    store = scene_store(tmp_path)
    exchanges = [EXCHANGE] * 4
    with store.transaction("turn.2") as tx:
        for i in range(60):
            tx.add(fact(tx, "pc.wren", f"memory_{i:03d}", "a short remembered thing"))
    early = {r: len(packet_for(store, r, exchanges).render()) for r in Role}
    turn = 3
    while store.state.last_seq < 1100:
        with store.transaction(f"turn.{turn}") as tx:
            tx.add(entity("npc", f"Walk On {turn}", tx=tx, data={"role": "dock hand"}))
            eid = f"npc.walk_on_{turn}"
            for i in range(3):
                tx.add(fact(tx, eid, f"detail_{i}", "something about them"))
            tx.add(fact(tx, "pc.wren", f"memory_{turn:04d}", "a short remembered thing"))
            tx.add(fact(tx, "world", f"rumor_{turn}", "talk on the docks"))
        turn += 1
    assert store.state.last_seq >= 1000 and len(store.state.facts) > 900
    late = {r: len(packet_for(store, r, exchanges).render()) for r in Role}
    for role in Role:
        assert late[role] <= early[role] * 1.1, (role, early[role], late[role])
    text = render_view(scene_view(store.state))
    shown = text.count("about pc.wren: memory_")
    assert text.count("\n  memory_") == 0 and 10 < shown < 60 and "memory_0003" not in text  # a budget, newest
    assert "rumor_" not in text  # world facts outside the scene stay in the store
    assert store.rebuild() == store.state


def test_view_tokens_stay_flat_over_300_scenes_and_pins_stay(tmp_path: Path) -> None:
    """SC-002 at age (12.2.4 item 3): 300 seeded scenes in one place, each adding a walk-on, things, facts, a
    memory and a thread. The view's tokens stay flat; the pins (written words, an absent NPC's open commitment,
    the five active memories) are always shown; archived memories never are (12.11.7)."""
    rng = random.Random(300)
    store = scene_store(tmp_path)
    with store.transaction("turn.2") as tx:
        tx.add(entity("object", "Notice Board", tx=tx))
        tx.add(Event.of("position_set", source="test", entity="obj.notice_board", location="loc.salt_harbor"))
        tx.add(fact(tx, "obj.notice_board", "text", "NO MOORING AFTER DARK"))
        tx.add(entity("npc", "Ines Sorrel", tx=tx))  # never on stage again
        tx.add(fact(tx, "npc.ines_sorrel", "commitment.c1", {"npc": "npc.ines_sorrel", "by": "pc", "act": "repay",
                                                            "status": "open"}, kind="commitment"))
    sizes: dict[int, int] = {}
    for n in range(1, 301):
        with store.transaction(f"turn.s{n}") as tx:
            tx.add(Event.of("scene_ended", source="test", scene_id=tx.state.scene.scene_id, reason="test"))  # type: ignore[union-attr]
            walk_on = f"npc.walk_on_{n}"
            tx.add(entity("npc", f"Walk On {n}", tx=tx, data={"role": "dock hand"}))
            tx.add(entity("thread", f"Thread {n}", tx=tx))
            # they stay at the place, so the cast present grows every scene (R2-A2: a home base gathers residents)
            tx.add(Event.of("position_set", source="test", entity=walk_on, location="loc.salt_harbor"))
            sid = tx.mint("scn")
            tx.add(Event.of("scene_started", scene_id=sid, scene={
                "scene_id": sid, "place_id": "loc.salt_harbor", "cast_present": ["npc.mara_voss", walk_on],
                "mode": "free"}))
            for k in range(2):
                thing = entity("object", f"Crate {n}-{k}", tx=tx)
                tx.add(thing)
                tx.add(Event.of("position_set", source="test", entity=thing.payload.entity.id,  # type: ignore[attr-defined]
                                location="loc.salt_harbor"))
            for k in range(5):
                subject = rng.choice(["pc.wren", "npc.mara_voss", walk_on])
                tx.add(fact(tx, subject, f"note_{n}_{k}", "a detail " * rng.randint(1, 6)))
            tx.add(fact(tx, "npc.mara_voss", f"memory.{n}", {"deed": f"deed {n}", "salience": rng.randint(1, 3),
                                                             "status": "active"}))
            if n > 5:  # the 12.11.7 cap: the sixth-newest is archived
                tx.add(fact(tx, "npc.mara_voss", f"memory.{n - 5}", {"deed": f"deed {n - 5}", "salience": 1,
                                                                     "status": "archived"}))
        if n in (50, 200, 300):
            sizes[n] = tokens(render_view(scene_view(store.state)))
    text = render_view(scene_view(store.state))
    assert sizes[300] <= sizes[50] * 1.1 and sizes[200] <= sizes[50] * 1.1, sizes
    assert "text = NO MOORING AFTER DARK" in text and "commitment.c1" in text
    assert all(f"memory.{n} = " in text for n in range(296, 301))
    assert "memory.295 = " not in text and "memory.1 = " not in text
    # R2-A2: 300 people present; full profiles within the cast budget (Mara holds the newest memories), the
    # rest on one capped "also here" line that counts whoever does not fit; the beat's target gets a profile
    assert len(store.state.scene.cast_present) > 300  # type: ignore[union-attr]
    assert "npc.mara_voss: Mara Voss" in text and "npc.walk_on_1: " not in text
    assert text.count("\nalso here: ") == 1 and "more" in text.split("\nalso here: ")[1].split("\n")[0]
    assert "npc.walk_on_1: Walk On 1" in render_view(scene_view(store.state, focus=["npc.walk_on_1"]))
