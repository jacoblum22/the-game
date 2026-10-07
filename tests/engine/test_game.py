"""The game API end to end (T072, T069, T071, T109): engine/game.py over the offline stand-in model.

New game -> mixed seed (by number, in own words, skipped) -> quick-start creation -> the opening -> 30 turns of play
(talk, a question, a risky act through an offer, a move, a rest) -> quit mid-offer -> `Game.open` re-presents the
same offer -> continue; quitting mid-seed and mid-creation; replay; spending and the budget notice; preferences; a
narration failure after T6; and `python -m play` driven against the real Game.
"""

from __future__ import annotations

import io
import sqlite3
from pathlib import Path
from typing import Any

import pytest

from engine.dm.response import Response
from engine.game import Game, GameConfig, ReplayResult
from engine.llm.base import ModelUnavailable, Role
from engine.llm.offline import OfflineModel, ScriptedModel, conform, enum_at
from engine.world.places import location, reachable
from tests.engine.test_turn_adjudication import RISKY, beat, framer, reader

OFFLINE = GameConfig(offline=True)


def new_game(tmp_path: Path, model: Any = None, seed: int = 7, name: str = "g.db") -> tuple[Game, Response]:
    return Game.new(tmp_path / name, OFFLINE, seed=seed, model=model or ScriptedModel())


def seed_oracle(game: Game, r: Response) -> Response:
    r = game.submit("oracle")
    while r.phase == "seed":
        r = game.submit("")
    return r


def quick_start(game: Game, r: Response, name: str = "Wren, she/her") -> Response:
    for msg in ("", "", "", "", name, "begin"):
        if r.phase != "creation":
            break
        r = game.submit(msg)
    return r


def to_play(tmp_path: Path, model: Any = None, seed: int = 7, name: str = "g.db") -> tuple[Game, Response]:
    game, r = new_game(tmp_path, model, seed, name)
    r = quick_start(game, seed_oracle(game, r))
    assert r.phase == "play"
    return game, r


def settle(game: Game, r: Response, pick: str = "commit") -> Response:
    """Answer whatever pauses a step left open (commit an offer, continue past a warning, take a failure)."""
    for _ in range(6):
        if r.pause is None or r.pause.kind not in ("offer", "near_miss", "redirect", "clarify"):
            return r
        ids_ = [c.id for c in r.pause.choices]
        if not ids_:
            r = game.submit("yes")
            continue
        choice = next((c for c in (pick, "continue", "commit", "failure", "keep_playing") if c in ids_), ids_[0])
        r = game.answer(choice)
    return r


def sneak() -> dict[str, Any]:
    return beat("slip past the lookout unseen", "verb.sneak", verbs=("sneak",))


# ------------------------------------------------------------------------------------------- the long game


def test_new_game_to_play_thirty_turns_quit_mid_offer_and_resume(tmp_path: Path) -> None:
    model = ScriptedModel()
    game, r = Game.new(tmp_path / "g.db", OFFLINE, seed=7, model=model)
    assert r.phase == "seed" and r.pause is not None and r.pause.kind == "seed_step"
    assert [c.id for c in r.pause.choices] == ["guided", "oracle", "mixed"] and r.turn_id is None
    r = game.submit("3")  # mixed, by number
    assert r.pause is not None and r.pause.prompt.startswith("Which of these questions would you like to answer")
    r = game.submit("1, 2")  # two questions answered by the player, the oracle rolls the rest
    assert r.pause is not None and r.pause.kind == "seed_step"
    r = game.submit("1")  # by number
    r = game.submit("A long war burned the old roads and nobody rebuilt them.")  # in own words
    steps = 0
    while r.phase == "seed":
        r = game.submit("")  # skipped: keep / the default
        steps += 1
        assert steps < 40
    st = game.store.state
    sources = {a.get("source") for a in st.seed_answers}
    assert "player_option" in sources and st.meta.get("title") == st.meta["world.seed"]["region"]["name"]
    assert r.phase == "creation" and r.pause is not None and r.pause.kind == "create_step"
    r = quick_start(game, r)
    st = game.store.state
    pc = st.meta["pc.active"]
    assert r.phase == "play" and r.fiction and r.turn_id is not None
    assert st.scene is not None and st.meta["opening.pc"] == pc and st.meta["game.phase"] == "play"
    assert "The story begins." in r.fiction.split("\n\n")[0]  # said before the opening's first lines

    played, offers, moved, rested = 0, 0, False, False
    generic = ["I look around the square.", "I ask the nearest person what happened here.", "Is there a well here?",
               "I talk to the innkeeper about work.", "I search the room carefully.", "I wait and listen."]
    for i in range(30):
        if i == 5:  # a risky act through an offer
            model.push(Role.READER, reader("DECLARATION", "I slip past the lookout.", sneak()))
            model.push(Role.FRAMER, framer(**RISKY))
            r = game.submit("I slip past the lookout.")
            assert r.pause is not None and r.pause.kind == "offer" and r.pause.frame_summary
            offers += 1
            r = settle(game, r)
        elif i == 10:  # a move to another place: the Director frames the next scene elsewhere
            here = location(game.store.state)
            dest = next(x.to for x in reachable(game.store.state, here) if x.to != here)

            def to_dest(schema: dict[str, Any], packet: Any, dest: str = dest) -> dict[str, Any]:
                d = conform(OfflineModel().propose(Role.DIRECTOR, schema, packet), schema, schema)
                assert dest in enum_at(schema, "next_scene", "place")
                return {**d, "cut_now": True, "next_scene": {**d["next_scene"], "place": dest}}

            model.push(Role.READER, reader("DECLARATION", "I head out on the road."))
            model.push(Role.DIRECTOR, to_dest)
            r = settle(game, game.submit("I head out on the road."))
            moved = location(game.store.state) == dest
        elif i == 15:  # a rest
            before = game.store.state.time.now
            r = settle(game, game.submit("I rest for the night."))
            rested = game.store.state.time.now != before
        else:
            r = settle(game, game.submit(generic[i % len(generic)]))
        played += 1
        assert r.phase == "play" and (r.fiction or r.oof_blocks)
    assert played == 30 and offers == 1 and moved and rested
    st = game.store.state
    boundaries = [e.payload.boundary for e in game.store.events(types=["boundary_marked"])]  # type: ignore[attr-defined]
    assert "rest_long" in boundaries and any(e.type == "oracle_answered" for e in game.store.events())
    assert st.meta[f"{pc}.creation"]["window"] == "locked"  # h.02.creation_lock at the rest's reflection

    # quit mid-offer, then open: the same offer, after a recap
    model.push(Role.READER, reader("DECLARATION", "I slip past the lookout.", sneak()))
    model.push(Role.FRAMER, framer(**RISKY))
    offer = game.submit("I slip past the lookout.")
    assert offer.pause is not None and offer.pause.kind == "offer"
    game.close()
    game2, back = Game.open(tmp_path / "g.db", OFFLINE)
    assert back.pause is not None and back.pause.pause_id == offer.pause.pause_id
    assert "RECAP" in [b.kind for b in back.oof_blocks] and back.oof_blocks[-1].text == offer.oof_blocks[-1].text
    done = game2.answer("commit")
    assert done.pause is None or done.pause.kind != "offer"
    assert game2.store.rebuild() == game2.store.state
    game2.close()


# ------------------------------------------------------------------------------------------- resume anywhere


def test_quit_mid_seed_and_mid_creation_reopens_exactly(tmp_path: Path) -> None:
    game, r = new_game(tmp_path)
    r = game.submit("mixed")
    r = game.submit("2")
    game.close()
    game, back = Game.open(tmp_path / "g.db", OFFLINE)
    assert back.phase == "seed" and back.pause == r.pause and back.oof_blocks[-1] == r.oof_blocks[-1]
    r = game.submit("")
    while r.phase == "seed":
        r = game.submit("")
    r = game.submit("")  # creation 1: the default path
    game.close()
    game, back = Game.open(tmp_path / "g.db", OFFLINE)
    assert back.phase == "creation" and back.pause == r.pause and back.oof_blocks[-1] == r.oof_blocks[-1]
    r = quick_start(game, back)
    assert r.phase == "play" and game.store.state.meta.get("opening.pc") == game.store.state.meta["pc.active"]
    game.close()


def test_mid_last_chance_reopens_the_same_menu(tmp_path: Path) -> None:
    from tests.engine.test_ending import to_threshold

    game, r = to_threshold(tmp_path)
    assert r.pause is not None and r.pause.kind == "last_chance"
    game.close()
    game, back = Game.open(tmp_path / "g.db", OFFLINE)
    assert back.pause is not None and back.pause.pause_id == r.pause.pause_id
    assert back.pause.choices == r.pause.choices and back.oof_blocks[-1].kind == "LAST_CHANCE"
    game.close()


# ------------------------------------------------------------------------------------------- replay


def test_replay_of_a_recorded_game_is_identical(tmp_path: Path) -> None:
    model = ScriptedModel()
    game, r = to_play(tmp_path, model)
    for msg in ("I look around.", "Is there a well here?", "I talk to the nearest person."):
        settle(game, game.submit(msg))
    model.push(Role.READER, reader("DECLARATION", "I slip past the lookout.", sneak()))
    model.push(Role.FRAMER, framer(**RISKY))
    game.submit("I slip past the lookout.")
    game.close()
    game, _ = Game.open(tmp_path / "g.db", OFFLINE)  # a reopen in the middle is replayed too
    settle(game, game.answer("commit"))
    game.set_pref("autocommit", True)
    settle(game, game.submit("I rest for the night."))
    game.close()
    res = Game.replay(tmp_path / "g.db")
    assert isinstance(res, ReplayResult) and res.identical, res.divergence
    assert res.events > 100 and res.inputs > 10
    part = Game.replay(tmp_path / "g.db", until_seq=50)
    assert part.identical and part.events == 50


def test_replay_reports_a_divergence(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    settle(game, game.submit("I look around."))
    game.close()
    conn = sqlite3.connect(tmp_path / "g.db")  # the recorded seed-mode answer is tampered with
    conn.execute("UPDATE game_inputs SET arg='\"guided\"' WHERE kind='submit' AND arg='\"oracle\"'")
    conn.commit()
    conn.close()
    res = Game.replay(tmp_path / "g.db")
    assert not res.identical and res.divergence


# ------------------------------------------------------------------------------------------- spending, prefs


def test_spend_budget_notice_and_preferences(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    s = game.spend()
    assert s.budget_usd == 2.0 and s.game_usd == 0.0 and s.session_usd == 0.0
    game.set_pref("budget_usd", 0.0)  # spending (0) has reached the budget: a notice between turns, once
    r = settle(game, game.submit("I look around."))
    assert r.budget_notice and "budget" in r.budget_notice
    r = settle(game, game.submit("I wait."))
    assert r.budget_notice is None
    game.set_pref("budget_usd", None)
    assert game.spend().budget_usd is None and settle(game, game.submit("I wait.")).budget_notice is None
    game.set_pref("autocommit", True)
    assert game.store.state.meta["auto_commit"] is True and game.ctx.auto_commit()
    with pytest.raises(ValueError):
        game.set_pref("volume", 3)
    game.close()
    game, _ = Game.open(tmp_path / "g.db", OFFLINE)
    assert game.spend().budget_usd is None  # the preference persists
    game.close()


def test_a_notice_never_lands_mid_turn(tmp_path: Path) -> None:
    model = ScriptedModel()
    game, _ = to_play(tmp_path, model)
    game.set_pref("budget_usd", 0.0)
    model.push(Role.READER, reader("DECLARATION", "I slip past the lookout.", sneak()))
    model.push(Role.FRAMER, framer(**RISKY))
    r = game.submit("I slip past the lookout.")
    assert r.pause is not None and r.pause.kind == "offer" and r.budget_notice is None
    r = settle(game, game.answer("commit"))
    assert r.budget_notice
    game.close()


# ------------------------------------------------------------------------------------------- errors


def test_narration_failure_after_t6_is_narrated_on_the_next_call(tmp_path: Path) -> None:
    model = ScriptedModel()
    game, _ = to_play(tmp_path, model)
    model.push(Role.NARRATOR, ModelUnavailable("provider down"))
    with pytest.raises(ModelUnavailable):
        game.submit("I look around the square.")
    st = game.store.state
    pending = st.meta["narration_pending"]
    failed = pending["turn_id"]
    assert any(e.turn_id == failed for e in game.store.events())  # T6 committed
    assert not game.turn_record(failed).delivered_verbatim  # type: ignore[union-attr]
    r = game.submit("I wait and listen.")
    assert game.store.state.meta.get("narration_pending") is None
    assert game.turn_record(failed).delivered_verbatim  # type: ignore[union-attr]
    assert r.fiction.count("What do you do?") >= 2  # the owed narration, then this turn's
    game.close()


def test_choice_not_on_the_open_pause_and_new_character_before_an_ending(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    with pytest.raises(ValueError):
        game.answer("commit")
    with pytest.raises(ValueError):
        game.new_character()
    assert game.codex("sheet").text and game.turn_record("turn.1") is not None
    game.close()


def test_branch_saves_a_copy_you_can_continue(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    bid = game.branch("before the bridge")
    assert bid == "br.before_the_bridge" and game.branch("before the bridge") == "br.before_the_bridge_2"
    copy = tmp_path / "g @ before the bridge.db"
    assert copy.exists()
    game.close()
    g2, r = Game.open(copy, OFFLINE)
    assert r.phase == "play" and g2.store.state.meta["title"].endswith("@ before the bridge")
    g2.close()
    assert Game.replay(copy).identical


def test_dispute_is_out_of_fiction(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    before = game.store.state.time.now
    r = game.dispute("my vitality should be higher")
    assert r.fiction == "" and r.oof_blocks and game.store.state.time.now == before
    game.close()


# ------------------------------------------------------------------------------------------- fixes


def test_director_new_npc_meets_someone(tmp_path: Path) -> None:
    from engine.dm.context import TurnContext
    from engine.dm.roles.director import DirectorDecision, NextScene, frame_scene
    from tests.fixtures.scene_dock import build_dock

    dock = build_dock(tmp_path)
    ctx = TurnContext.for_store(dock.store, model=OfflineModel(), rules=dock.rules)
    before = {e for e, v in dock.state.entities.items() if v.kind == "npc"}
    with dock.store.transaction() as tx:
        ctx.tx = tx
        d = DirectorDecision(cut_now=True, next_scene=NextScene(mode="free", place=dock.place, agenda="who comes",
                                                                cast=["new_npc"]))
        frame_scene(ctx, d, reason="test")
        ctx.tx = None
    new = {e for e, v in dock.state.entities.items() if v.kind == "npc"} - before
    assert len(new) == 1 and next(iter(new)) in dock.state.scene.cast_present  # type: ignore[union-attr]


def test_gen_data_is_cached_on_disk(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from engine.gen import _data

    monkeypatch.setattr(_data, "CACHE_DIR", tmp_path)
    _data._load_raw.cache_clear()
    try:
        first = _data.load("calendar.yaml")
        assert list(tmp_path.glob("calendar-*.pickle"))
        _data._load_raw.cache_clear()
        assert _data.load("calendar.yaml") == first
    finally:
        _data._load_raw.cache_clear()


def test_open_slots_reminder_at_the_next_session(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    settle(game, game.submit("I rest for the night."))
    queued = game.store.state.meta.get("creation.open_slots.reminder")
    game.close()
    game, r = Game.open(tmp_path / "g.db", OFFLINE)
    assert queued and queued["slots"]  # quick start leaves the thorn (and more) open (02.9.8)
    assert any("Still open from your character's creation" in b.text for b in r.oof_blocks)
    assert game.store.state.meta.get("creation.open_slots.reminder") is None
    game.close()


# ------------------------------------------------------------------------------------------- the CLI


def test_cli_plays_the_real_game_offline(tmp_path: Path) -> None:
    from play import cli

    lines = ["2"] + ["skip"] * 40 + ["Wren, she/her", "1", "I look around.", "/sheet", "/spend", "/turn",
                                       "I talk to the nearest person.", "/quit"]
    out = io.StringIO()
    code = cli.main(["new", "t1", "--offline"], stdin=io.StringIO("\n".join(lines) + "\n"), stdout=out,
                    saves=tmp_path)
    text = out.getvalue()
    assert code == 0, text[-2000:]
    assert "First, let's build the world your character will live in." in text and "Making your character, step 1 of 5" in text
    assert "[SHEET]" in text and "Wren (" in text and "is a human" in text
    assert "This turn $" in text and "[TURN] turn." in text and "Saved. Until next time." in text
    out2 = io.StringIO()
    code = cli.main(["continue", "t1", "--offline"], stdin=io.StringIO("/quit\n"), stdout=out2, saves=tmp_path)
    assert code == 0 and "[RECAP]" in out2.getvalue()
    out3 = io.StringIO()
    assert cli.main(["replay", "t1", "--offline"], stdin=io.StringIO(""), stdout=out3, saves=tmp_path) == 0
    assert "identical" in out3.getvalue()
