"""Spec 021 (F4's testimony and answer lines, F7's stance): the round-6 cases I2 traced, on cuts of the real saves
(`specs/021-testimony-answers/cut_fixtures.py`; the saves are gitignored), each changed the way the fix intends."""

from __future__ import annotations

import gzip
import shutil
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import pytest

from engine.data.loader import load_rules
from engine.dm import answer as ans
from engine.dm import testimony as tm
from engine.dm.context import TurnContext
from engine.dm.packet import speaker_card
from engine.dm.schemas import lever_candidate, schema_context
from engine.gen.case import cases
from engine.llm.base import Role
from engine.llm.offline import OfflineModel, ScriptedModel
from engine.resolve.types import Beat
from engine.store.db import Store
from tests.fixtures.seeded import seeded_store

FIXTURES = Path(__file__).parents[1] / "fixtures"
DUNWEN, EVINE = "npc.dunwen_redmore", "pc.evine_oakwell"
LILETT, SEVELLA, YSNDIL = "npc.lilett_mughill", "npc.sevella_de_belac", "pc.ysndil_of_the_quiet_wood"


def _open(tmp_path: Path, name: str) -> Store:
    path = tmp_path / name.removesuffix(".gz")
    with gzip.open(FIXTURES / name, "rb") as src, path.open("wb") as dst:
        shutil.copyfileobj(src, dst)
    return Store.open(path)


@contextmanager
def _turn(store: Store, model: Any = None) -> Iterator[TurnContext]:
    ctx = TurnContext.for_store(store, model=model or OfflineModel())
    with store.transaction() as tx:
        ctx.tx = tx
        try:
            yield ctx
        finally:
            ctx.tx = None


@pytest.fixture
def fighter7(tmp_path: Path) -> Iterator[Store]:
    store = _open(tmp_path, "testimony_fighter_turn7.db.gz")
    yield store
    store.close()


@pytest.fixture
def talker6(tmp_path: Path) -> Iterator[Store]:
    store = _open(tmp_path, "testimony_talker_turn6.db.gz")
    yield store
    store.close()


# ------------------------------------------------------------------- 1. the garbled odds line (233000 t7-t14)


def test_the_refusal_is_never_settled_into_a_world_fact(fighter7: Store) -> None:
    """Dunwen: "You'll get no word out of me with your hand on me, duck" (said.5). Haiku stated it as
    {Dunwen, "will give no word out while", "pc.evine_oakwell has a hand on him"}; it became fact.103 and a -2 snag.
    Now: even that very response writes nothing, and a `refusal` kind writes nothing."""
    before = set(fighter7.state.facts)
    haiku = {"kind": "claim", "subject": DUNWEN, "predicate": "will give no word out while",
             "value": "pc.evine_oakwell has a hand on him"}
    model = ScriptedModel({Role.TESTIMONY: [haiku]})
    with _turn(fighter7, model) as ctx:
        assert tm.settle(ctx, "said.5") is None
    rec = tm.get(fighter7.state, "said.5")
    assert rec is not None and rec["settled"] == "none" and rec["fact"] is None
    assert set(fighter7.state.facts) == before
    [(_, packet)] = model.calls  # the claim call sees pronouns and names, never ids (I2 §1, §4)
    assert "Dunwen Redmore: she/her" in packet.view and "npc." not in packet.view + packet.message
    assert "Evine" not in packet.view  # the PC is "you", not a third person
    with _turn(fighter7, ScriptedModel({Role.TESTIMONY: [{"kind": "refusal", "subject": "", "predicate": "",
                                                          "value": ""}]})) as ctx:
        assert tm.settle(ctx, "said.4") is None
    assert set(fighter7.state.facts) == before


def test_threatening_her_does_not_settle_what_she_said(fighter7: Store) -> None:
    """Turn 7's threat named `rests_on: said.5` (the Reader picked it on 64% of turns). The threat argues against her
    words; it does not travel on them or cite them, so nothing settles."""
    threat = Beat(id="b1", actor=EVINE, intent="make Dunwen tell the word", method="threaten her", target=DUNWEN,
                  verb="verb.talk", speech=True)
    assert tm.triggered(fighter7.state, [threat]) == []


def test_scene_labels_and_old_said_facts_are_never_lever_candidates(fighter7: Store) -> None:
    """fact.101 "straining against you" (manner) and the pre-021 `said.*` facts were cited as snags on t5-t14."""
    st = fighter7.state
    labels = [f.id for f in st.facts.values() if f.predicate.startswith(("detail.manner", "detail.posture",
                                                                          "detail.held", "said."))]
    assert {"fact.101", "fact.100", "fact.99", "fact.98", "fact.102"} <= set(labels)
    assert not any(lever_candidate(st, f) for f in labels)
    beat = Beat(id="b1", actor=EVINE, intent="make Dunwen tell the word", method="twist her arm", target=DUNWEN,
                verb="verb.grapple", against_will=True, declared_seq=st.last_seq)
    enum = schema_context(st, load_rules(), beat=beat, focus=[DUNWEN]).lever_fact_ids
    assert enum and not set(labels) & set(enum)


# ------------------------------------------------------------------- 2. the friend as a stranger (232941 t8)


def test_the_speaker_card_says_she_is_your_friend(talker6: Store) -> None:
    """Lilett's card had three "knows:" lines and no bond (`bond.` skipped; the fact's subject is the PC)."""
    card = speaker_card(talker6.state, LILETT)
    assert "SPEAKER CARD for Lilett Mughill (she/her; your friend)" in card[0]


# ------------------------------------------------------------------- 3. the wall (232941 t6)


def test_a_failed_cast_writes_no_one_you_know_nowhere(talker6: Store) -> None:
    """"And who keeps the gate at The Red Warren?": `R2 MUST: Lilett ... tells you who is keeps the gate at The Red
    Warren: no one you know` (fact.110). Now: a cast person, or nothing written and her willingness line."""
    before = set(talker6.state.facts)
    with _turn(talker6) as ctx:
        a = ans.ask(ctx, LILETT, "who_is", "the keeper of the Red Warren gate",
                    "And who keeps the gate at The Red Warren, can I trust them?", pc=YSNDIL)
    new = [talker6.state.facts[f] for f in set(talker6.state.facts) - before]
    assert "no one you know" not in a.line
    assert not any(str(f.value) == "no one you know" for f in new)
    cast = [f for f in new if f.predicate.startswith("who_is_")]
    assert (a.willingness is not None and not cast) or (cast and cast[0].value in talker6.state.entities)


# ------------------------------------------------------------------- 4. a found clue re-delivered (232941 t5)


def test_a_found_clue_is_not_delivered_again(talker6: Store) -> None:
    """Turn 5's `R1 MUST: Lilett Mughill acts: tells you the way on: toward The Red Warren`: the node was found at
    turn 3. Now she answers in her own words, within her willingness."""
    st = talker6.state
    node = next(n for c in cases(st).values() for n in c["nodes"] if "way on" in n["fact"])
    assert node["found"]
    with _turn(talker6) as ctx:
        a = ans.ask(ctx, LILETT, "who_knows", "Rrakaa Mud-Walker and The Red Warren",
                    "Lilett, you know this town. What do you know about Rrakaa Mud-Walker, and about The Red Warren?",
                    pc=YSNDIL)
    assert a.fact_id is None and a.pointer is None and a.willingness == "willing"
    assert "way on" not in a.line


# ------------------------------------------------------------------- card leaks (232941 t13)


def test_the_card_never_shows_a_complaint_or_the_players_goal(tmp_path: Path) -> None:
    """Sevella's card read `knows: Sevella de Belac correction 1 Lilett said she knew no one ...` (the player's /fix)
    and she voiced it; Belby's carried `agreed = learn what Belby would pay` (the player's goal)."""
    store = _open(tmp_path, "testimony_talker_turn13.db.gz")
    try:
        st = store.state
        assert st.facts["fact.114"].predicate == "correction.1" and st.facts["fact.103"].predicate == "agreed"
        for npc in (SEVELLA, "npc.belby_haydale", LILETT):
            knows = [ln for ln in speaker_card(st, npc) if ln.startswith("- knows:")]
            assert knows and not any(w in ln for ln in knows for w in ("correction", "would pay", "agreed", " False",
                                                                         " True"))
        assert "(he/him)" in speaker_card(st, SEVELLA)[0]  # seeded a man; testimony called him "she" (I2 §4)
        assert "  - Sevella de Belac: he/him" in speaker_card(st, LILETT)  # whom her card names, with pronouns
    finally:
        store.close()


# ------------------------------------------------------------------- triggers and the written claim


def test_a_premise_settles_an_ordinary_claim_with_its_speaker(tmp_path: Path) -> None:
    store = seeded_store(tmp_path, 8)[0]
    from tests.engine.test_answer import here

    npc = here(store)[0]
    with _turn(store) as ctx:
        sid = tm.add_said(ctx, [{"speaker": npc, "words": "The ford below the mill is shallow this week."}])[0]
    premise = Beat(id="b1", actor="pc.wren", intent="cross", method="wade the ford", verb="verb.move",
                   assertion="the ford is shallow this week")
    assert tm.triggered(store.state, [premise]) == [sid]
    claim = {"kind": "claim", "subject": "the ford below the mill", "predicate": "is", "value": "shallow this week"}
    with _turn(store, ScriptedModel({Role.TESTIMONY: [claim]})) as ctx:
        fid = tm.settle(ctx, sid)
    f = store.state.facts[str(fid)]
    assert f.source == "testimony" and f.predicate == "is" and f.value == "shallow this week"
    assert tm.said_for(store.state, str(fid))["speaker"] == npc  # type: ignore[index]  # said_by (PR-12-12 step 4)
    from engine.dm.oof import fact_short

    label = fact_short(store.state, str(fid))  # the odds line says who said it (I2 §1: no attribution)
    assert " said: " in label and label.endswith("is shallow this week")


# ------------------------------------------------------------------- the re-shown OFFER's "Then:" (narration.py)


def test_a_reshown_offer_says_then_from_the_typed_goal(tmp_path: Path) -> None:
    """The stored pause re-showed "Then:" from the Reader's raw `method`; it now matches the first showing (DL-01-39)."""
    from engine.dm.narration import pause_blocks
    from engine.dm.turn import run_turn
    from tests.engine.test_message_plan import FIGHTER_4, _blocks, _game

    ctx = _game(tmp_path, "plan_fighter_turn4.db.gz", FIGHTER_4, faces=[19, 19, 19])
    res = run_turn(ctx, " ".join(p["text"] for p in FIGHTER_4["parts"]))
    assert res.pause is not None
    first = _blocks(res, "OFFER")[0]
    [again] = pause_blocks(ctx, res.pause)
    then = [ln.strip() for ln in first.splitlines() if ln.strip().startswith("Then:")]
    assert then and then == [ln.strip() for ln in again.text.splitlines() if ln.strip().startswith("Then:")]
    ctx.store.close()


# ------------------------------------------------------------------- F7: the seeded stance bounds the roll


def test_a_helping_quest_giver_never_starts_below_neutral(tmp_path: Path) -> None:
    """Belby (stance `helps`) rolled Unfriendly (-2) on first interaction (232941 event 411)."""
    from engine.world.social import first_interaction

    seen = 0
    for seed in range(12):
        store = seeded_store(tmp_path, seed, name=f"s{seed}.db")[0]
        npcs = [e for e in store.state.entities.values() if e.kind == "npc" and isinstance(e.data.get("stance"), dict)
                and e.data["stance"].get("stance") in ("helps", "hinders") and not e.data.get("member_of")]
        for e in npcs[:3]:
            with _turn(store) as ctx:
                v = first_interaction(ctx.time_ctx(), e.id)
            assert v >= 0 if e.data["stance"]["stance"] == "helps" else v <= -1
            seen += 1
        store.close()
    assert seen >= 6
