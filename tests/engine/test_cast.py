"""Casting (00.11.1 `cast`, social.yaml#cast; DL-12-60): the pool gate, fit, determinism, the empty pool."""

from __future__ import annotations

from pathlib import Path

from engine.gen.cast import base_pool, cast, pointer_target
from engine.store.events import Event
from tests.fixtures.seeded import seeded_store


def test_the_gate_excludes_the_pc_the_anchor_the_sealed_and_the_far_powers(tmp_path: Path) -> None:
    store, w = seeded_store(tmp_path, 1, anchor={"npc": "npc.harin_deepdelve", "kind": "friend"})
    st = store.state
    pool = base_pool(st, "pc.wren")
    assert "pc.wren" not in pool and "npc.harin_deepdelve" not in pool
    assert not any(st.entities[n].data.get("power") for n in pool)
    assert "npc.magwen_thistlefoot" not in pool  # a power of the far rings (12.16.11)
    with store.transaction() as tx:
        tx.add(Event.of("sealed", source="test", rule_id="00.6.5", ref="npc.falkin_greenfoot", gate="t"))
        tx.add(Event.of("fact_set", {"source": "ruling"}, source="test", rule_id="t", fact_id=tx.mint("fact"),
                        subject="npc.loran_millbrook", predicate="exists", value="dead"))
    pool = base_pool(store.state, "pc.wren")
    assert "npc.falkin_greenfoot" not in pool and "npc.loran_millbrook" not in pool


def test_who_is_a_role_casts_someone_of_that_role_and_stays_cast(tmp_path: Path) -> None:
    store, w = seeded_store(tmp_path, 1)
    st = store.state
    haven = st.meta["world.region"]["haven"]
    assert cast(st, "the innkeeper", scope=w.incident.place) == "npc.falkin_greenfoot"
    assert cast(st, "captain", scope=haven) == "npc.loran_millbrook"  # captain -> guard (role_map)
    assert cast(st, "the old enemy", scope=haven) is None  # gated by role: nobody's role says "old enemy"
    first = cast(st, "the old enemy", scope=haven, gate=False)  # a story role: everyone in scope, by fit
    assert first in base_pool(st, "pc.wren")
    assert all(cast(st, "the old enemy", scope=haven, gate=False) == first for _ in range(3))  # same question, same one
    assert cast(st, "the old enemy", scope=haven, exclude=(first,), gate=False) != first


def test_an_empty_pool_is_none_and_a_pointer_falls_back_to_a_place(tmp_path: Path) -> None:
    store, w = seeded_store(tmp_path, 1)
    st = store.state
    assert cast(st, "harpooner", scope=w.incident.place) is None  # no such role here: the caller generates or says
    kind, ref = pointer_target(st, "roads", scope=w.incident.place)
    assert kind == "person" and ref in base_pool(st, "pc.wren")
    assert pointer_target(st, "no_such_topic", scope=w.incident.place)[0] == "walk_on"
