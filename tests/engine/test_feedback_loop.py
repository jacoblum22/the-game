"""Spec 012: the player feedback loop (PR-12-11, 12.3.6, 12.5.8) on a real offline game.

The base game is the recorded game's recipe (`tests/replay/record_games.py`: seed 11, the e2e Driver), 30 turns
of real play, with one early detail planted in its first scene. Each test copies it, plants the error a looser
claim check could let through, and reports it the way a player would. Every outcome row of PR-12-11 has a test.
"""

from __future__ import annotations

import random
import shutil
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import pytest

import engine.dm.turn as turn_mod
import engine.resolve.frame as frame_mod
from engine import ids
from engine.dm.dispute import _turns, dispute_stats, review_log_path
from engine.dm.oof import FIX_HINT
from engine.dm.packet import render_view, scene_view
from engine.dm.roles.reader import possible_dispute
from engine.game import Game
from engine.llm.offline import OfflineModel
from engine.store.db import REVERTIBLE
from engine.store.events import Event
from engine.store.records import TurnRecord
from engine.store.views import display_name
from engine.world.places import location, reachable
from tests.e2e.driver import OFFLINE, Driver

EARLY: dict[str, str] = {}


@pytest.fixture(scope="module")
def base(tmp_path_factory: pytest.TempPathFactory) -> Path:
    path = tmp_path_factory.mktemp("feedback") / "base.db"
    d = Driver.start(path, seed=11)
    st = d.game.store.state
    npc = next(i for i in st.scene.cast_present if st.entities[i].kind == "npc")  # type: ignore[union-attr]
    name = st.entities[npc].name
    EARLY.update(npc=npc, name=name, scene=st.scene.scene_id)  # type: ignore[union-attr]
    EARLY["turn"] = plant(d.game, f"I look at {name}.", f"{name} rakes a hand through iron-grey hair.",
                          lambda tx: tx.add(Event.of("fact_set", {"source": "narration"}, fact_id=tx.mint(ids.FACT),
                                                     subject=npc, predicate="detail.hair", value="iron-grey",
                                                     visibility="shown", certainty="narrated", persistence="lasting")))
    d.play(30)
    d.game.close()
    return path


@pytest.fixture
def game(base: Path, tmp_path: Path) -> Iterator[Game]:
    path = tmp_path / "g.db"
    shutil.copy(base, path)
    g, _ = Game.open(path, OFFLINE, model=OfflineModel())
    yield g
    if not g.closed:
        g.close()


def plant(g: Game, said: str, delivered: str, write: Callable[[Any], Any] | None = None) -> str:
    """A played turn whose narration (and write) carries the planted error."""
    tid = g.store.new_turn_id()
    with g.store.transaction(tid) as tx:
        if write is not None:
            write(tx)
    g.store.save_turn(TurnRecord(turn_id=tid, input_verbatim=said, delivered_verbatim=delivered))
    return tid


def settle(g: Game, r: Any) -> Any:
    for _ in range(6):
        if r.pause is None:
            return r
        got = [c.id for c in r.pause.choices]
        r = g.answer("commit" if "commit" in got else got[0])
    return r


def present_npc(g: Game) -> str:
    st = g.store.state
    return next(i for i in st.scene.cast_present if st.entities[i].kind == "npc")  # type: ignore[union-attr]


def record(g: Game) -> dict[str, Any]:
    return [r for r in g.store.state.meta["corrections"] if r.get("type") == "dispute"][-1]


def review(g: Game) -> str:
    return review_log_path(g.store).read_text(encoding="utf-8")


def test_remembered_wrong_is_corrected_pinned_and_still_right_20_turns_later(game: Game) -> None:
    npc = present_npc(game)
    name = game.store.state.entities[npc].name

    def first(tx: Any) -> None:  # a resolved source (generation) set it
        tx.add(Event.of("fact_set", {"source": "generation"}, fact_id=tx.mint(ids.FACT), subject=npc,
                        predicate="detail.clothing", value="a grey coat", visibility="shown", persistence="lasting"))

    def slip(tx: Any) -> None:  # a later unsourced narration write replaced it
        tx.add(Event.of("fact_set", {"source": "narration"}, fact_id=tx.mint(ids.FACT), subject=npc,
                        predicate="detail.clothing", value="a blue coat", visibility="shown", persistence="lasting",
                        certainty="narrated", supersedes=tx.state.current_fact_id(npc, "detail.clothing")))

    plant(game, f"I look at {name}.", f"{name} pulls a grey coat tight against the wind.", first)
    plant(game, "I wait.", f"{name}'s blue coat flaps in the gusts.", slip)
    r = game.dispute(f"{name}'s coat is grey, not blue")
    label = display_name(game.store.state, npc)  # as the PC knows them: an unlearned name is never revealed
    assert r.text().startswith(f"[CORRECTION] You're right: {label}'s clothing is a grey coat (turn "), r.text()
    assert "the record had slipped to a blue coat" in r.text()
    st = game.store.state
    fid = st.current_fact_id(npc, "detail.clothing")
    assert fid is not None and st.facts[fid].value == "a grey coat"
    assert st.facts[fid].pinned and st.facts[fid].source == "correction" and st.facts[fid].supersedes
    rec = record(game)
    assert (rec["category"], rec["outcome"], rec["upheld"]) == ("remembered_wrong", "correct", True)
    assert any("resolved earlier" in e for e in rec["evidence"]) and rec["writes"]
    rng = random.Random(4)
    for _ in range(20):  # twenty more turns of play
        line = rng.choice(["I look around.", "I wait and watch the street.", f"I watch {name}.", "Who is here?",
                           "I ask around about the road north."])
        r = settle(game, game.submit(line))
        assert r.phase == "play"
    st = game.store.state
    fid = st.current_fact_id(npc, "detail.clothing")
    assert fid is not None and st.facts[fid].value == "a grey coat" and st.facts[fid].pinned
    view = render_view(scene_view(st, [npc], spot=[npc]))  # in the profile (in scene) or the spotlight (away)
    assert "a grey coat" in view
    assert f"## {rec['id']}" in review(game) and "**Outcome**: correct (upheld)" in review(game)


def _wrong_frame(g: Game, action: str) -> Event:
    real = frame_mod._tier_dc
    frame_mod._tier_dc = lambda rules, tier: real(rules, tier) + 5  # a bug: every tier DC 5 too high
    try:
        settle(g, g.submit(action))
    finally:
        frame_mod._tier_dc = real
    ev = list(g.store.events(types=["frame_committed"]))[-1]
    assert ev.payload.frame["dc_source"] == "tier"  # type: ignore[attr-defined]
    return ev


def _travel(g: Game) -> None:
    st = g.store.state
    here = location(st)
    dest = next(x.to for x in reachable(st, here) if x.to != here)
    settle(g, g.submit(f"I head to {st.entities[dest].name}."))


ACTION = "I vault over the cart by the well."


def test_rule_applied_wrong_is_taken_back_past_the_scene_and_redone(game: Game) -> None:
    ev = _wrong_frame(game, ACTION)
    fid, before = ev.payload.frame_id, ev.payload.frame["dc"]  # type: ignore[attr-defined]
    old_scene = game.store.state.scene.scene_id  # type: ignore[union-attr]
    _travel(game)
    assert game.store.state.scene.scene_id != old_scene  # type: ignore[union-attr]
    r = game.dispute(f"{fid}: the DC was too high")
    assert r.text().startswith("[CORRECTION] The roll in turn") and f"DC {before}, but tier" in r.text()
    assert r.pause is not None and [c.id for c in r.pause.choices] == ["accept_forward", "rewind"]
    assert record(game)["outcome"] == "pending"
    r = game.answer("rewind")
    assert "Taken back" in r.text() and not r.fiction  # out of fiction: no narration
    st = game.store.state
    assert st.scene.scene_id == old_scene and fid in st.meta["rolls_voided"]  # type: ignore[union-attr]
    rec = record(game)
    assert (rec["category"], rec["outcome"]) == ("rule_wrong", "take_back") and rec["reverted"]
    assert len([r for r in st.meta["corrections"] if r.get("words") == rec["words"]]) == 1  # pending replaced
    settle(game, game.submit(ACTION))  # the redo
    redo = list(game.store.events(types=["frame_committed"]))[-1]
    assert redo.payload.frame["dc"] == before - 5  # type: ignore[attr-defined]
    assert game.store.rebuild() == game.store.state


@pytest.mark.parametrize("blocker", ["session", "dying"])
def test_a_take_back_is_blocked_by_an_irreversible_event(game: Game, base: Path, tmp_path: Path,
                                                       blocker: str) -> None:
    ev = _wrong_frame(game, ACTION)
    fid = ev.payload.frame_id  # type: ignore[attr-defined]
    _travel(game)
    if blocker == "session":
        game.close()
        game, _ = Game.open(game.store.path, OFFLINE, model=OfflineModel())
    else:
        npc = present_npc(game)
        plant(game, "I watch.", "Someone falls, dying.", lambda tx: tx.add(Event.of(
            "fact_set", {"source": "ruling"}, fact_id=tx.mint(ids.FACT), subject=npc, predicate="dying_step", value=1,
            visibility="shown")))
    r = game.dispute(f"{fid}: the DC was too high")
    assert r.pause is None and "can't be taken back" in r.text()
    assert ("a session ended since" if blocker == "session" else "someone died or fell dying since") in r.text()
    rec = record(game)
    assert rec["outcome"] == "correct" and rec["reverted"] == [] and fid not in game.store.state.meta.get(
        "rolls_voided", [])
    game.close()


def test_contradiction_with_an_earlier_scene_is_found_in_the_whole_transcript(game: Game) -> None:
    npc, name = EARLY["npc"], EARLY["name"]
    st = game.store.state
    assert st.scene.scene_id != EARLY["scene"]  # type: ignore[union-attr]
    assert len(_turns(game.store)) > 50  # every turn is searched, not the last 50
    red = plant(game, "I look around.", f"{name}'s red hair catches the light.")
    r = game.dispute(f"{name}'s hair is iron-grey, you just said red")
    text = r.text()
    label = display_name(st, npc)
    assert text.startswith(f"[CORRECTION] You're right: {label}'s hair is iron-grey (turn {EARLY['turn'][5:]}:"), text
    assert "iron-grey hair" in text and game.store.state.fact_value(npc, "detail.hair") == "iron-grey"
    rec = record(game)
    assert rec["passage"]["turn"] == red and rec["outcome"] == "correct"
    assert rec["category"] == "contradiction"  # the locator's label (offline stand-in)


def test_an_action_misread_is_taken_back_and_redone(game: Game) -> None:
    real = turn_mod.read_message

    def misread(ctx: Any, message: str, exchanges: Any = ()) -> Any:  # the Reader reads a different act
        return real(ctx, "I ask them what is going on.", exchanges=exchanges)

    turn_mod.read_message = misread  # type: ignore[assignment]
    try:
        r = settle(game, game.submit("I tell them a joke."))
    finally:
        turn_mod.read_message = real  # type: ignore[assignment]
    ev = list(game.store.events(types=["frame_committed"]))[-1]
    assert ev.turn_id == r.turn_id and ev.payload.frame["offer_choice"] == "auto"  # type: ignore[attr-defined]
    turn = game.store.turn(r.turn_id)
    assert turn is not None and turn.writes
    r = game.dispute("I only told a joke, I didn't ask them anything")
    assert r.text().startswith("[CORRECTION] Taken back: \"You ask them what is going on.\"") and "Declare again" in r.text()
    st = game.store.state
    assert ev.payload.frame_id in st.meta["rolls_voided"]  # type: ignore[attr-defined]
    revertible = {s for s in turn.writes if (e := game.store.event(s)) is not None and e.type in REVERTIBLE}
    assert revertible and revertible <= set(st.reverted)
    rec = record(game)
    assert (rec["category"], rec["outcome"]) == ("misread", "take_back")
    r = settle(game, game.submit("I tell them a joke."))  # the redo, read right this time
    assert r.phase == "play"


def test_the_player_mistaken_is_answered_with_the_quote(game: Game) -> None:
    st = game.store.state
    vit = st.quantities["pc.bram"]["vitality"].current
    facts = dict(st.facts)
    r = game.dispute(f"My vitality should be {vit + 6}")
    text = r.text()
    assert text.startswith(f"[FIX] As recorded: your vitality is {vit} (turn "), text
    assert ': "' in text and f"{vit + 6} was never said. Logged." in text
    assert game.store.state.facts == facts and game.store.state.quantities["pc.bram"]["vitality"].current == vit
    assert record(game)["outcome"] == "explain_with_quote" and not record(game)["upheld"]


def test_incidental_fiction_with_uncertain_evidence_the_players_reading_wins(game: Game) -> None:
    npc = present_npc(game)
    name = game.store.state.entities[npc].name
    assert game.store.state.current_fact_id(npc, "detail.clothing") is None  # nothing on record
    r = game.dispute(f"{name}'s cloak was green")
    label = display_name(game.store.state, npc)
    assert r.text().startswith(f"[CORRECTION] You're right: {label}'s clothing is green cloak."), r.text()
    st = game.store.state
    fid = st.current_fact_id(npc, "detail.clothing")
    assert fid is not None and st.facts[fid].value == "green cloak" and st.facts[fid].pinned
    assert record(game)["outcome"] == "player_reading_wins"


def test_a_mechanical_claim_the_player_cannot_back_up_leaves_the_store(game: Game) -> None:
    st = game.store.state
    facts, qs = dict(st.facts), {k: v.current for k, v in st.quantities["pc.bram"].items()}
    r = game.dispute("I still have my silver lantern")
    assert r.text().startswith("[FIX] The record has nothing for your silver lantern (it holds: "), r.text()
    assert "Without a record I can't change it; logged for review." in r.text()
    st = game.store.state
    assert st.facts == facts and {k: v.current for k, v in st.quantities["pc.bram"].items()} == qs  # INV-9
    rec = record(game)
    assert rec["outcome"] == "explain_and_log" and "silver lantern" in review(game)


def test_a_fiction_message_that_may_be_a_dispute_ends_with_the_hint(game: Game) -> None:
    assert possible_dispute("Wait, you said the gate was open.", ["FICTION_QUESTION"])
    assert not possible_dispute("I open the gate.", ["DECLARATION"])
    assert not possible_dispute("You said the gate was open!", ["DISPUTE"])  # answered as a dispute instead
    r = settle(game, game.submit("I keep walking. That's not what I meant to find, though."))
    assert FIX_HINT in r.text()


def test_dispute_stats_and_the_review_log(game: Game) -> None:
    game.dispute("My vitality should be 99")
    game.dispute("That's wrong")
    stats = dispute_stats(game.store.state)
    assert stats["all"] >= 2 and stats["upheld"] <= stats["all"]
    log = review(game)
    # the review log was copied with the game file only in the test's own folder: it holds this sitting's reports
    assert log.startswith("# Disputes:") and log.count("- **Player**:") == 2
    block = log.split("That's wrong", 1)[1]
    assert "- **Outcome**: explain_and_log" in block and "> [FIX]" in block  # the record stands; still logged
