"""Seed packs (12.16.9, 12.16.11, 12.16.16; DL-12-61): the 7 pack checks, determinism, and the store shape."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

from engine.dm.packet import scene_setting
from engine.gen._seed_check import check_seed
from engine.gen._seed_packs import check_packs
from engine.gen.world_seed import WorldSeed, build_rolled
from engine.store.views import narrator_view
from tests.fixtures.seeded import seeded_store, world

PACK_IDS = ["ws.pack.place_look", "ws.pack.place_furniture", "ws.pack.place_exits", "ws.pack.npc_knowledge",
            "ws.pack.npc_stance", "ws.pack.documents", "ws.pack.incident_case"]


def failing(reg: dict[str, Any]) -> set[str]:
    return {rid for rid, ok, _ in check_packs(reg) if not ok}


def test_packed_seed_passes_all_71_checks() -> None:
    for seed in (1, 21, 26):
        res = check_seed(world(seed).record)
        assert len(res) == 71 and [r for r in res if not r[1]] == []
        assert [r[0] for r in res[-7:]] == PACK_IDS


def test_run_check_reports_the_pack_rows() -> None:
    ws = WorldSeed.from_seed(3, mode="oracle")
    assert {c.requirement for c in ws.run_all().check} >= set(PACK_IDS)


def test_same_seed_same_packs_and_case() -> None:
    a, b = build_rolled(21).record, build_rolled(21).record
    for key in ("documents", "walk_ons", "seed_cases"):
        assert a[key] == b[key]
    assert [(p.get("look"), p.get("furniture"), p.get("exits")) for p in a["places"]] == \
        [(p.get("look"), p.get("furniture"), p.get("exits")) for p in b["places"]]
    assert [(n.get("knowledge"), n.get("stance")) for n in a["npcs"]] == [(n.get("knowledge"), n.get("stance")) for n in b["npcs"]]


def test_each_check_catches_its_failure() -> None:
    base = world(1).record
    assert failing(base) == set()

    def broken(fn: Any) -> set[str]:
        reg = copy.deepcopy(base)
        fn(reg)
        return failing(reg)

    place = next(i for i, p in enumerate(base["places"]) if p["place_kind"] != "region")
    cast = next(i for i, n in enumerate(base["npcs"]) if n.get("depth") != "walk_on")
    assert broken(lambda r: r["places"][place].pop("look")) == {"ws.pack.place_look"}
    assert broken(lambda r: r["places"][place].update(furniture=["a stool"])) == {"ws.pack.place_furniture"}
    assert broken(lambda r: r["places"][place].update(exits=[])) == {"ws.pack.place_exits"}
    assert broken(lambda r: r["npcs"][cast].update(knowledge=[k for k in r["npcs"][cast]["knowledge"]
                                                              if k["slot"] != "tie"])) == {"ws.pack.npc_knowledge"}
    assert broken(lambda r: r["npcs"][cast].pop("stance")) == {"ws.pack.npc_stance"}
    assert broken(lambda r: r["documents"][0].update(text="Hire {contact}")) == {"ws.pack.documents"}
    assert broken(lambda r: r["seed_cases"][0]["nodes"][0]["placements"].pop()) == {"ws.pack.incident_case"}


def test_hire_notice_names_who_to_see() -> None:
    for seed in (1, 2, 21):
        reg = world(seed).record
        docs = {d["id"]: d for d in reg["documents"]}
        for ld in reg["opening"]["leads"]:
            if ld.get("document"):
                assert ld["names"] in docs[ld["document"]]["text"]


def test_packs_reach_the_store(tmp_path: Path) -> None:
    store, w = seeded_store(tmp_path, 26)  # a missing person; the reporter is a walk-on
    st = store.state
    rec = w.record
    place = st.entities[w.incident.place]
    assert place.data["look"] and 2 <= len(place.data["furniture"]) <= 4 and place.data["exits"]
    npc = next(n for n in rec["npcs"] if n.get("depth") != "walk_on")
    assert "knowledge" in st.entities[npc["id"]].sealed_fields and st.entities[npc["id"]].data["stance"]
    assert "knowledge" not in narrator_view(st)["entities"][npc["id"]]["data"]  # the pack is told, never shown
    for d in rec["documents"]:
        assert st.fact_value(d["id"], "text") == d["text"] and st.positions[d["id"]].location == d["at"]
    case = rec["seed_cases"][0]
    assert st.meta["world.cases"][case["id"]] == case and st.meta["world.opening"]["case"] == case["id"]
    subject = case["solution"]["subject"]["id"]
    assert subject in st.entities and subject not in st.positions  # the missing person is nowhere to be found
    for n in rec["walk_ons"]:
        assert n["id"] in st.entities and st.entities[n["id"]].data["name_known"] is False
    assert store.rebuild() == store.state


def test_scene_setting_shows_only_the_present_place(tmp_path: Path) -> None:
    from engine.data.loader import load_rules
    from engine.rng import Rng
    from engine.time.scheduler import TimeContext
    from engine.world.scenes import start_scene

    store, w = seeded_store(tmp_path, 21)
    with store.transaction() as tx:
        start_scene(TimeContext(tx, load_rules(), Rng.for_store(store)), place=w.incident.place, mode="free",
                    agenda="the incident")
    text = scene_setting(store.state)
    place = store.state.entities[w.incident.place]
    assert f"- look: {place.data['look']}" in text and "- furniture: " in text and "- exits: toward " in text
    others = [p for p in w.record["places"] if p["id"] != place.id and p.get("look")]
    assert not any(p["look"] in text for p in others)
