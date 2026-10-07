"""NPC social records and the chronicle (T061)."""

from __future__ import annotations

from pathlib import Path

import pytest

from engine.time import clock
from engine.time.scheduler import advance_time
from engine.world import chronicle, places, scenes, social
from engine.world.common import WorldError
from tests.engine.test_world_support import Game


def _scene(g: Game, **kw: object) -> None:
    args = {"place": places.location(g.state), "mode": "free", "agenda": "Who is here?"} | kw
    g.run(lambda ctx: scenes.start_scene(ctx, **args))  # type: ignore[arg-type]


def test_meet_npc_fixes_identity_and_reuses_the_roster(tmp_path: Path) -> None:
    g = Game(tmp_path)
    here = places.location(g.state)
    inn = next(n for n in g.world.cast if n.home == here and n.role == "innkeeper")
    assert g.run(lambda ctx: social.meet_npc(ctx, "the innkeeper", here)) == inn.id
    nid = g.run(lambda ctx: social.meet_npc(ctx, "a ferry hand", here))
    e = g.state.entities[nid]
    assert e.kind == "npc" and e.name and nid.startswith("npc.")
    for k in ("role", "gender", "pronouns", "age", "detail", "demeanor"):
        assert e.data[k], k
    assert e.data["role"] == "a ferry hand" and e.data["home"] == here
    assert g.state.positions[nid].location == here
    assert social.cast_list(g.state) == {inn.id: 1, nid: 1}
    # the same seed rolls the same person (RC-RNG)
    g2 = Game(tmp_path, name="again.db")
    nid2 = g2.run(lambda ctx: social.meet_npc(ctx, "a ferry hand", here))
    assert nid2 == nid and g2.state.entities[nid2].data == e.data
    assert g.store.rebuild() == g.state


def test_first_interaction_rolls_standing_once(tmp_path: Path) -> None:
    g = Game(tmp_path)
    nid = g.run(lambda ctx: social.meet_npc(ctx, "a carter", places.location(ctx.tx.state)))
    s = g.run(lambda ctx: social.first_interaction(ctx, nid))
    assert -3 <= s <= 2  # never Devoted as a first impression
    assert social.standing(g.state, nid) == s
    assert g.run(lambda ctx: social.first_interaction(ctx, nid)) == s
    up = g.run(lambda ctx: social.step_standing(ctx, nid, 5, "test", cap="warm"))
    assert up == max(s, 1)
    assert social.standing_effects(g.rules, up)["id"].startswith("standing.")


def test_memories_commit_at_scene_end_with_a_cap(tmp_path: Path) -> None:
    g = Game(tmp_path)
    _scene(g)
    nid = g.world.cast[-1].id

    def remember(ctx: object) -> None:
        for i in range(7):
            social.record_memory(ctx, nid, f"deed {i}", "insulted" if i % 2 else "promised")  # type: ignore[arg-type]
    g.run(remember)
    assert social.memories(g.state, nid) == []  # pending until scene_end
    g.run(lambda ctx: scenes.end_scene(ctx, "player_cut"))
    active = social.memories(g.state, nid)
    assert len(active) == 5
    assert [m["salience"] for m in active] == sorted((m["salience"] for m in active), reverse=True)
    assert {m["valence"] for m in active[:3]} == {"promised"}  # salience 2 kept first
    assert len(social.memories(g.state, nid, active_only=False)) == 7  # archived, never lost
    assert g.store.rebuild() == g.state


def test_memory_step_moves_standing(tmp_path: Path) -> None:
    g = Game(tmp_path)
    nid = g.world.cast[-1].id
    g.run(lambda ctx: social.first_interaction(ctx, nid))
    s0 = social.standing(g.state, nid)
    assert s0 is not None
    mem = g.run(lambda ctx: social.record_memory(ctx, nid, "struck him", "harmed", severity="S3", apply_step=True))
    assert social.standing(g.state, nid) == max(-3, s0 - 2)
    assert mem["salience"] == 3
    assert social.memories(g.state, nid)  # no scene: committed at once


def test_patience_spends_and_resets_at_scene_end(tmp_path: Path) -> None:
    g = Game(tmp_path)
    _scene(g)
    nid = g.world.cast[-1].id
    g.run(lambda ctx: social.first_interaction(ctx, nid))
    full = social.patience(g.state, g.rules, nid)
    if full is None:
        pytest.skip("rolled Devoted")
    for _ in range(full):
        g.run(lambda ctx: social.spend_patience(ctx, nid))
    assert social.patience(g.state, g.rules, nid) == 0 and social.talk_closed(g.state, nid)
    g.run(lambda ctx: scenes.end_scene(ctx, "player_cut"))
    assert social.patience(g.state, g.rules, nid) == full and not social.talk_closed(g.state, nid)


def test_commitments_fall_due_on_the_day_boundary(tmp_path: Path) -> None:
    g = Game(tmp_path)
    a, b = g.world.cast[-1].id, g.world.cast[-2].id
    today = clock.day_index(g.state.time.now)
    g.run(lambda ctx: social.first_interaction(ctx, a))
    if social.standing(g.state, a) == -3:
        pytest.skip("rolled Hostile")
    act = g.run(lambda ctx: social.record_commitment(ctx, a, by="npc", act="ferry Wren", due_day=today + 1))
    ob = g.run(lambda ctx: social.record_commitment(ctx, b, by="pc", act="pay the toll", due_day=today + 1))
    assert {c["fact_id"] for c in social.commitments(g.state)} == {act, ob}
    res = g.run(lambda ctx: advance_time(ctx, 2, "day", "wait"))
    assert res.interrupt is not None and res.interrupt[0] == "h.15.commitments_due"
    done = {c["act"]: c["status"] for c in social.commitments(g.state, status=None)}
    assert done == {"ferry Wren": "performed", "pay the toll": "broken"}
    assert social.standing(g.state, b) is not None
    assert any(m["valence"] == "betrayed" for m in social.memories(g.state, b))
    assert g.store.rebuild() == g.state


def test_keep_commitment(tmp_path: Path) -> None:
    g = Game(tmp_path)
    b = g.world.cast[-2].id
    ob = g.run(lambda ctx: social.record_commitment(ctx, b, by="pc", act="return the bell", due_day=99))
    g.run(lambda ctx: social.keep_commitment(ctx, ob))
    assert social.commitments(g.state) == []
    assert social.commitments(g.state, status="kept")[0]["act"] == "return the bell"


def test_promote_writes_sealed_fields(tmp_path: Path) -> None:
    g = Game(tmp_path)
    nid = g.run(lambda ctx: social.meet_npc(ctx, "a carter", places.location(ctx.tx.state)))
    written = g.run(lambda ctx: social.promote_npc(ctx, nid, "recurring"))
    assert {"wants", "fears", "refusals", "voice", "depth"} <= set(written)
    fid = g.state.current_fact_id(nid, "wants")
    assert fid in g.state.seals
    assert social.npc_field(g.state, nid, "depth") == "recurring"
    assert g.run(lambda ctx: social.promote_npc(ctx, nid, "recurring")) == []


def test_chronicle_append_list_and_correct(tmp_path: Path) -> None:
    g = Game(tmp_path)
    c1 = g.run(lambda ctx: chronicle.chronicle_append(ctx, "Wren came to Ravenford.", kind="deed",
                                                      entities=[g.pc], source="12.4.8"))
    c2 = g.run(lambda ctx: chronicle.chronicle_append(ctx, "Wren came to Ravenford by the lake road.", kind="deed",
                                                      entities=[g.pc], source="12.4.8", supersedes=c1))
    assert (c1, c2) == ("chr.1", "chr.2")
    assert [e.id for e in chronicle.chronicle(g.state)] == ["chr.2"]
    assert [e.id for e in chronicle.chronicle(g.state, include_superseded=True)] == ["chr.1", "chr.2"]
    assert chronicle.chronicle(g.state, entity=g.pc)[0].text.endswith("lake road.")
    with pytest.raises(WorldError):
        g.run(lambda ctx: chronicle.chronicle_append(ctx, "word " * 31, kind="deed"))
    with pytest.raises(WorldError):
        g.run(lambda ctx: chronicle.chronicle_append(ctx, "x", kind="gossip"))


def test_scene_end_offers_a_chronicle_line_for_a_thread_agenda(tmp_path: Path) -> None:
    g = Game(tmp_path)
    thr = next(iter(g.threads.values()))
    _scene(g, thread=thr)
    end = g.run(lambda ctx: scenes.end_scene(ctx, "agenda_answered", answered="answered"))
    assert end.chronicle_offer is not None and end.chronicle_offer["thread"] == thr
    lists = g.state.meta["thread_list"]
    assert lists[thr] == 2  # featured: the scene's agenda thread
