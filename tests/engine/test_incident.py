"""The opening incident is the seed's reduced case (12.16.16; DL-12-62; the P-067 binding retired), "who is X?" is
answered from the case or by casting (PR-12-10, 00.11.1), a local knows the haven's names (I-149), and an NPC never
answers with the player's own words (P-068)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from engine.audit.screen import echoed_quotes
from engine.dm.answer import NO_ONE, ask, rungs_for, who_answer
from engine.dm.context import TurnContext
from engine.dm.incident import incident_line, start_knowledge
from engine.dm.packet import scene_setting
from engine.dm.session import opening
from engine.gen.case import cases
from engine.llm.offline import OfflineModel
from engine.store.events import Event
from engine.store.views import name_known
from tests.fixtures.game import entity, new_store
from tests.fixtures.seeded import seeded_store

LOCALS = ["Ala Oakhill", "Bran Ford", "Cora Well", "Dun Ash", "Thanae Leafward"]


def _world(tmp_path: Path, option: str = "missing", seed: int = 1234, npcs: list[str] = LOCALS):
    """A bare store with no seeded case: casting is all there is."""
    store = new_store(tmp_path, seed=seed)
    with store.transaction() as tx:
        tx.add(entity("place", "Fernwell", tx=tx, data={"place_kind": "settlement"}))
        tx.add(entity("place", "Market", tx=tx, data={"place_kind": "site", "parent": "loc.fernwell"}))
        tx.add(entity("place", "Far Tower", tx=tx, data={"place_kind": "site"}))
        tx.add(entity("pc", "Wren", tx=tx, quantities={"vitality": (10, 0, 10)}))
        tx.add(Event.of("position_set", source="test", rule_id="10.1.1", entity="pc.wren", location="loc.market"))
        for n in npcs:
            e = entity("npc", n, tx=tx, data={"home": "loc.market", "depth": "minor"})
            tx.add(e)
            tx.add(Event.of("position_set", source="test", rule_id="12.16.11",
                            entity="npc." + n.lower().replace(" ", "_"), location="loc.market"))
        tx.add(entity("npc", "Old Power", tx=tx, data={"home": "loc.far_tower", "power": True}))
        tx.add(Event.of("fact_set", {"source": "player_accepted"}, source="test", rule_id="02.9.2", fact_id=tx.mint("fact"), subject="pc.wren",
                        predicate="bond.anchor", value={"npc": "npc.thanae_leafward", "kind": "friend"}))
        tx.add(entity("place", "Hollow Warren", tx=tx, data={"place_kind": "site"}))
        tx.add(Event.of("meta_set", source="test", rule_id="12.16.16", key="world.opening", value={
            "inciting": {"option": option, "text": "a child (or an elder, or a priest) is missing since last night"},
            "start": {"place": "loc.market"},
            "leads": [{"lead": "the incident itself: someone is missing", "points_to": "loc.hollow_warren"}]}))
    return store


def _ask(store, text: str, npc: str | None = None) -> Any:  # type: ignore[no-untyped-def]
    """The DM-side "who is X?" (`who_answer`), or put to `npc` (the ladder: (line, fact id))."""
    ctx = TurnContext.for_store(store, model=OfflineModel())
    with store.transaction() as tx:
        ctx.tx = tx
        try:
            if npc is None:
                return who_answer(ctx, text)
            a = ask(ctx, npc, "who_is", None, text, rungs_for(ctx.rules, 2), pc="pc.wren")
            return a.line, a.fact_id
        finally:
            ctx.tx = None


def test_who_is_missing_is_the_seeded_case_subject_and_stays_answered(tmp_path: Path) -> None:
    store, w = seeded_store(tmp_path, 21)  # a missing person (a generated child, elder or priest)
    case = w.record["seed_cases"][0]
    subject = case["solution"]["subject"]["id"]
    name = store.state.entities[subject].name
    core = next(p["holder"] for p in case["nodes"][0]["placements"] if p["access"] == "core")
    assert _ask(store, "who is missing")[0].startswith("no one has told you")  # the PC was not told: a pointer
    assert name in _ask(store, "who is missing?", npc=core)[0]  # the core holder tells it (15.9.5)
    assert cases(store.state)[case["id"]]["nodes"][0]["found"] is True
    assert _ask(store, "who is missing")[0] == name  # now the PC knows it
    assert "incident.subject" not in store.state.meta  # the opening binding is retired (I-148)
    assert store.rebuild() == store.state


def test_the_opening_names_who_brought_the_word(tmp_path: Path) -> None:
    store, w = seeded_store(tmp_path, 21)
    resp = opening(TurnContext.for_store(store, model=OfflineModel()))
    st = store.state
    core = next(p for p in w.record["seed_cases"][0]["nodes"][0]["placements"] if p["access"] == "core")
    assert resp.fiction and "brought the word" in incident_line(st)
    assert st.scene is not None and core["holder"] in st.scene.cast_present  # the reporter is there, at the opening place
    assert "brought the word" in scene_setting(st)
    assert store.rebuild() == store.state


def test_other_who_questions_are_cast_among_existing_people(tmp_path: Path) -> None:
    store = _world(tmp_path)
    enemy = _ask(store, "who is the old enemy")
    assert enemy[0] in LOCALS[:-1]  # an existing person, never the anchor bond or a far power
    assert _ask(store, "who is the old enemy") == enemy  # settled once
    assert _ask(store, "who is here") is None and _ask(store, "is the door locked") is None  # the Oracle's
    line, fid = _ask(store, "who is the old enemy?", npc="npc.ala_oakhill")
    assert enemy[0] in line and fid == enemy[1]


def test_who_with_no_one_fitting_is_no_one_you_know(tmp_path: Path) -> None:
    store = _world(tmp_path, npcs=[])
    assert _ask(store, "who is the old enemy")[0] == NO_ONE


def test_a_local_knows_the_havens_names_and_an_outsider_does_not(tmp_path: Path) -> None:
    local, _ = seeded_store(tmp_path, 1, anchor="my sister, who keeps the ferry")  # a text anchor: in the haven
    outsider, _ = seeded_store(tmp_path, 1, name="b.db", anchor={"npc": "npc.magwen_thistlefoot", "kind": "friend"})
    for store in (local, outsider):
        ctx = TurnContext.for_store(store, model=OfflineModel())
        with store.transaction() as tx:
            ctx.tx = tx
            named = start_knowledge(ctx, tx)
            ctx.tx = None
        if store is outsider:
            assert named == []
            continue
        st = store.state
        roles = {str(st.entities[i].data["role"]): i for i in st.entities if st.entities[i].kind == "npc"}
        for r in ("smith", "innkeeper", "captain of the gate", "healer", "scribe and teacher of letters",
                  "head of The lords of Hawkgate", "head of The faithful of Oswen"):
            assert name_known(st, roles[r]), r  # setup's headline people already were; the rest are now
        assert named and "npc.ranan_brightsmith" in named  # the scribe: not a headline person
        assert not name_known(st, "npc.zzirik_swift")  # the sellsword stays a description
        assert not name_known(st, "npc.brugnak_three_scar")  # the threat's head is seated elsewhere
        assert store.rebuild() == store.state


def test_an_npc_echoing_the_players_quote_is_caught() -> None:
    said = ['I step up. "Captain, someone is missing. Who is it?"']
    echo = 'He laughs. "Captain, someone is missing. Who is it?" His thumbs stay hooked in his belt.'
    own = '"Captain, someone is missing. Who is it?" you ask. He shrugs. "Ask the miller."'
    assert echoed_quotes(echo, said) == ["Captain, someone is missing. Who is it?"]
    assert echoed_quotes(own, said) == []
    # P-102: the PC's declared line opening the narration (or a paragraph) is the PC speaking, not an echo
    said = ['I step up: "I accept. Right now, in the middle of the room." I draw both daggers.']
    opens = '"I accept. Right now, in the middle of the room." Behind the bar, Tibine keeps a hand flat on the wood.'
    para = 'You step up.\n\n"I accept. Right now, in the middle of the room."\n\nTaman says nothing.'
    assert echoed_quotes(opens, said) == [] and echoed_quotes(para, said) == []
    assert echoed_quotes('Taman laughs. "I accept. Right now, in the middle of the room." He spits.', said)
