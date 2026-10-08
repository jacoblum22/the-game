"""Spec 009 part A: established details (00.6.6a), scene cards (12.4.8 step 9, 12.5.3), the spotlight and per-role
views (12.2.4), and the promise question."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from engine.data.loader import load_rules
from engine.dm.codex import promises, what_you_know
from engine.dm.packet import MOTIVES, build_packet
from engine.dm.session import recap_summary
from engine.llm.base import Role
from engine.retrieve.episodes import card_lines, cards_for
from engine.retrieve.scene import resolve_names, scene_starts, spotlight
from engine.store import details as dt
from engine.store.db import Store
from engine.store.events import Event
from engine.store.projection import project
from engine.world import places, scenes
from evals.replay_bench import sections
from tests.e2e.driver import Driver
from tests.engine.test_world_support import Game
from tests.fixtures.game import entity, new_store

RULES = load_rules()


def _npc(g: Game, n: int = 0) -> str:
    return g.world.cast[n].id


def _scene(g: Game, **kw: Any) -> scenes.SceneStart:
    args = {"place": places.location(g.state), "mode": "free", "agenda": "Does it work?", "hoped_answer": "yes"} | kw
    return g.run(lambda ctx: scenes.start_scene(ctx, **args))


def _write(g: Game, eid: str, slot: str, value: Any, turn: str | None = None, **kw: Any) -> dt.DetailWrite:
    def go(ctx: Any) -> dt.DetailWrite:
        res = dt.write_detail(ctx.tx.state, ctx.tx.mint, eid, slot, value, rules=g.rules, **kw)
        ctx.tx.add_all(res.events)
        return res
    return g.run(go, turn)


# ---------------------------------------------------------------- 00.6.6a: the slot writer


def test_slot_writer_new_same_superseded_contradiction(tmp_path: Path) -> None:
    g = Game(tmp_path)
    npc = _npc(g)
    first = _write(g, npc, "worn", "iron rings")
    assert first.outcome == "new" and g.state.fact_value(npc, "detail.worn") == "iron rings"
    f = g.state.facts[first.fact_id or ""]
    assert (f.certainty, f.persistence, f.source) == ("narrated", "lasting", "narration")
    assert g.state.details[npc]["worn"].fact_id == first.fact_id
    assert _write(g, npc, "worn", "Iron rings.").outcome == "same"  # a restatement writes nothing
    bad = _write(g, npc, "worn", "no rings")
    assert bad.outcome == "contradiction" and bad.prior == "iron rings" and not bad.events
    assert g.state.fact_value(npc, "detail.worn") == "iron rings"
    ok = _write(g, npc, "worn", "no rings", because="frame.1")  # she put them away: the record explains it
    assert ok.outcome == "superseded" and g.state.fact_value(npc, "detail.worn") == "no rings"
    assert first.fact_id in g.state.superseded_facts  # the old value is history (00.6.9c)
    assert g.store.rebuild() == g.state


def test_slot_writer_refuses_what_it_may_not_write(tmp_path: Path) -> None:
    g = Game(tmp_path)
    npc = _npc(g)
    assert _write(g, npc, "tattoo_colour", "blue").outcome == "refused"  # off the closed list
    assert _write(g, "npc.nobody", "worn", "a hat").outcome == "refused"  # no id: not written
    assert _write(g, npc, "posture", "slumped").outcome == "refused"  # scene state: code writes it, never prose
    assert _write(g, npc, "posture", "pinned", source="ruling").outcome == "new"


def test_lasting_details_order_by_salience_then_use(tmp_path: Path) -> None:
    """Spec 011 item 1 (DL-12-70): no cap; every lasting detail is active, ordered by salience then last use, so
    the profile budget cuts the tail; a usage mark moves a detail forward."""
    g = Game(tmp_path)
    npc = _npc(g)
    lasting = [s for s, p in dt.slots(g.rules).items() if p == "lasting"]
    written = {s: _write(g, npc, s, f"plain {s}", turn=f"turn.{i + 1}").fact_id for i, s in enumerate(lasting)}
    active = dt.active_details(g.state, npc)
    assert len(active) == len(lasting) and not hasattr(dt, "max_active")
    old = active[-1].id
    g.run(lambda ctx: ctx.tx.add(dt.used_event([old])), "turn.99")
    assert dt.active_details(g.state, npc)[0].id == old
    assert g.state.details[npc][g.state.facts[old].predicate[7:]].last_used == 99
    assert written and g.store.rebuild() == g.state


def test_scene_details_expire_at_scene_end(tmp_path: Path) -> None:
    g = Game(tmp_path)
    npc = _npc(g)
    _scene(g)
    pinned = _write(g, npc, "posture", "pinned", source="ruling")
    _write(g, npc, "worn", "iron rings")
    assert [f.id for f in dt.active_details(g.state, npc)][0] == pinned.fact_id  # pinned in its scene
    g.run(lambda ctx: scenes.end_scene(ctx, "player_cut"))
    assert g.state.fact_value(npc, "detail.posture") is None and "posture" not in g.state.details[npc]
    assert g.state.fact_value(npc, "detail.worn") == "iron rings"  # lasting details stay
    hist = g.store.fact_history(npc, "detail.posture")
    assert len(hist) == 2 and hist[0]["valid_to_seq"] is not None  # history kept (12.4.8 step 8)
    assert g.store.rebuild() == g.state


# ---------------------------------------------------------------- 12.4.8 step 9: scene cards


def _fact(tx: Any, subject: str, predicate: str, value: Any, **kw: Any) -> Event:
    return Event.of("fact_set", {"source": kw.pop("source", "narration")}, fact_id=tx.mint("fact"), subject=subject,
                    predicate=predicate, value=value, supersedes=tx.state.current_fact_id(subject, predicate),
                    visibility=kw.pop("visibility", "shown"), **kw)


def test_scene_cards_are_folded_from_the_log_and_regenerate_identically(tmp_path: Path) -> None:
    g = Game(tmp_path)
    a, b = _npc(g, 0), _npc(g, 1)
    first = _scene(g, cast=[a], agenda="Will Ada talk?")
    g.run(lambda ctx: ctx.tx.add(_fact(ctx.tx, a, "said", "the mill burned")))
    g.run(lambda ctx: scenes.end_scene(ctx, "player_cut", answered="as_hoped"))
    second = _scene(g, cast=[b], agenda="Is the road open?")
    g.run(lambda ctx: scenes.end_scene(ctx, "player_cut"))
    third = _scene(g, cast=[], agenda="Anything here?")
    cards = g.state.scene_cards
    c1 = cards[first.scene_id]
    assert c1.ended_at is not None and c1.answer == "as_hoped" and a in c1.cast and c1.agenda == "Will Ada talk?"
    assert any(g.state.facts[f].value == "the mill burned" for f in c1.facts)
    assert cards[third.scene_id].ended_at is None  # still running: no card in any view yet
    assert g.store.rebuild() == g.state  # regenerated from the log, field for field
    assert project(list(g.store.events())).scene_cards == cards
    assert [c.scene for c in cards_for(g.state, [a, b], k=2)] == [second.scene_id, first.scene_id]  # recency on a tie
    assert [c.scene for c in cards_for(g.state, [a], k=2)] == [first.scene_id]  # overlap
    line = card_lines(g.state, c1)[0]
    assert "Will Ada talk?" in line and "as hoped" in line and "the mill burned" in line
    assert scene_starts(g.state) == [cards[third.scene_id].started_seq, cards[second.scene_id].started_seq]
    g.run(lambda ctx: scenes.end_scene(ctx, "player_cut"))  # between scenes recency still sees two scenes (R2-A gap)
    assert len(scene_starts(g.state)) == 2 and scene_starts(g.state)[1] == cards[second.scene_id].started_seq
    summary = "\n".join(recap_summary(g.state))  # 12.5.3: the recap reads cards, never an earlier recap
    assert "- a scene: " in summary and "Will Ada talk?" in summary


# ---------------------------------------------------------------- 12.2.4: alias index and spotlight


def _town(tmp_path: Path) -> Store:
    s = new_store(tmp_path)
    with s.transaction("turn.1") as tx:
        tx.add(entity("pc", "Wren", tx=tx))
        tx.add(entity("place", "Salt Harbor", tx=tx))
        tx.add(entity("place", "Old Mill", tx=tx))
        tx.add(entity("npc", "Joss Dunmere", tx=tx, data={"role": "tanner"}))
        tx.add(entity("npc", "Pell Fenn", tx=tx, data={"role": "ferryman"}))
        tx.add(entity("npc", "Mara Voss", tx=tx, data={"role": "fence"}, sealed={"wants": ["the harbour"]}))
        tx.add(entity("npc", "Tibine de Morois", tx=tx, data={"role": "captain", "name_known": False}))
        tx.add(entity("npc", "Hidden Hand", tx=tx, visibility="sealed"))
        tx.add(entity("npc", "Kell Marsh", tx=tx, data={"role": "guard"}))
        tx.add(Event.of("relationship_set", a="npc.mara_voss", b="npc.kell_marsh", kind="kin", value=0,
                        new_value=1, reason="test"))
        tx.add(Event.of("position_set", entity="npc.kell_marsh", location="loc.old_mill"))
        tx.add(_fact(tx, "npc.mara_voss", "said", "the boats are late"))
        tx.add(knowledge := Event.of("knowledge_recorded", knower="pc.wren", fact_id=tx.state.current_fact_id(
            "npc.mara_voss", "said"), how="told"))
        assert knowledge
        tx.add(_fact(tx, "npc.mara_voss", "secret_route", "under the pier", visibility="background"))
        sid = tx.mint("scn")
        tx.add(Event.of("scene_started", scene_id=sid, scene={"scene_id": sid, "place_id": "loc.salt_harbor",
                                                              "cast_present": ["npc.joss_dunmere"]}))
    return s


def test_alias_index_prefers_full_names_and_never_leaks_an_unlearned_name(tmp_path: Path) -> None:
    st = _town(tmp_path).state
    assert resolve_names(st, "What do I know about Joss Fenn?") == []  # neither Joss Dunmere nor Pell Fenn
    assert resolve_names(st, "Joss Dunmere and Pell Fenn argue") == ["npc.joss_dunmere", "npc.pell_fenn"]
    assert resolve_names(st, "Where is Pell?") == ["npc.pell_fenn"]  # a lone given name, one carrier
    assert resolve_names(st, "I look for Tibine") == []  # the PC never learned her name (12.10.2)
    assert resolve_names(st, "I ask after the captain") == ["npc.tibine_de_morois"]  # how the PC knows her
    assert resolve_names(st, "Hidden Hand") == []  # sealed, no slice


def test_spotlight_order_cap_and_seals(tmp_path: Path) -> None:
    st = _town(tmp_path).state
    assert spotlight(st, "Joss, where is Mara Voss?") == ["npc.mara_voss", "npc.kell_marsh"]  # in scene: skipped; 1 hop
    got = spotlight(st, "I wave at Pell Fenn", "The captain watches from the Old Mill.", {"target": "npc.mara_voss"})
    assert got == ["npc.pell_fenn", "npc.mara_voss", "npc.tibine_de_morois", "loc.old_mill"]  # message, target, last
    assert spotlight(st, "Pell Fenn and Mara Voss", k=1) == ["npc.pell_fenn"]
    assert "npc.hidden_hand" not in spotlight(st, "", "", {"target": "npc.hidden_hand"})


def test_journal_matches_full_names_first(tmp_path: Path) -> None:
    store = _town(tmp_path)
    with store.transaction("turn.2") as tx:
        tx.add(_fact(tx, "npc.pell_fenn", "said", "the ferry runs at dawn"))
        tx.add(Event.of("knowledge_recorded", knower="pc.wren",
                        fact_id=tx.state.current_fact_id("npc.pell_fenn", "said"), how="told"))
    st = store.state
    assert "Pell Fenn" not in what_you_know(st, "Joss Fenn").text
    assert "the ferry runs at dawn" in what_you_know(st, "Pell Fenn").text


# ---------------------------------------------------------------- 12.2.4: per-role views and the leak test


def _packet(store: Store, role: Role, message: str = 'THE PLAYER\'S MESSAGE: "I ask about Mara Voss."') -> str:
    return build_packet(role, instructions="", cards=[], view=store.state, exchanges=[], message=message,
                        rules=RULES).view


def test_each_role_reads_its_own_projection(tmp_path: Path) -> None:
    store = _town(tmp_path)
    narrator, reader = _packet(store, Role.NARRATOR), _packet(store, Role.READER)
    framer = _packet(store, Role.FRAMER)
    director = _packet(store, Role.DIRECTOR)
    assert "npc.mara_voss: Mara Voss" in narrator and "the boats are late" in narrator  # as the PC knows her
    assert "under the pier" not in narrator and "the harbour" not in narrator  # unlearned background; motives
    assert "npc.mara_voss: Mara Voss" in reader and "facts:" not in reader and "the boats are late" not in reader
    assert "cast list:" not in framer and "open threads" not in framer
    assert "cast list:" in director and "facts:" not in director
    assert len(reader) < len(narrator)


def test_no_narrator_packet_leaks_truth_motives_or_seals(tmp_path: Path) -> None:
    d = Driver.start(tmp_path / "g.db", seed=11)
    d.play(12)
    st = d.game.store.state
    secret: set[str] = set()

    def strings(v: Any) -> list[str]:
        if isinstance(v, str):  # prose, not ids or tags (those name things the view may name)
            return [v] if len(v.split()) >= 3 else []
        if isinstance(v, dict):
            return [s for x in v.values() for s in strings(x)]
        if isinstance(v, list | tuple):
            return [s for x in v for s in strings(x)]
        return []

    for e in st.entities.values():
        for k, v in e.data.items():
            if k in MOTIVES or k in e.sealed_fields:
                secret |= set(strings(v))
    for fid, f in st.facts.items():
        if fid in st.seals or f.visibility == "sealed" or f.predicate in MOTIVES:
            secret |= set(strings(f.value))
    packets = [(r.get("request") or {}).get("packet") or "" for r in d.game.store.model_calls()
               if str(r["role"]) == "narrator"]
    d.game.close()
    assert packets and secret
    fixed = ("ROLE INSTRUCTIONS", "CORE RULES", "RULE CARDS")  # fixed text: card examples quote sample motives
    for p in packets:
        live = "\n".join(t for name, t in sections(p) if name not in fixed)
        assert live and not re.search(r"\btruth\b", live)
        leaked = [s for s in secret if s in live]
        assert not leaked, leaked[:3]


# ---------------------------------------------------------------- "what did I promise X?"


def test_promises_answer_from_commitments_by_full_name(tmp_path: Path) -> None:
    store = _town(tmp_path)
    with store.transaction("turn.2") as tx:
        for npc, act in (("npc.pell_fenn", "to row the crates across by dusk"), ("npc.joss_dunmere", "to fetch hides")):
            tx.add(Event.of("fact_set", {"source": "ruling"}, fact_id=tx.mint("fact"), subject=npc,
                            predicate=f"commitment.{npc}", value={"npc": npc, "by": "pc", "act": act, "status": "open"},
                            kind="commitment", visibility="available"))
    st = store.state
    text = promises(st, "Pell Fenn").text
    assert "to row the crates across by dusk" in text and "hides" not in text
    assert "No open promise" in promises(st, "Joss Fenn").text  # nobody by that full name: not a first-name guess
    assert "hides" in promises(st, None).text and "crates" in promises(st, None).text
