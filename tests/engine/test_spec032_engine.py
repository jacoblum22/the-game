"""Spec 032 phase P2: `Role.DM` (schema, prompt, offline heuristic, per-role calls) and the engine kept in the save.

Cases S1-S12 of specs/032-dm-tools-mvp/cases.md: the save's stored `engine` / `dm_secrets` win over the caller's
config on `Game.open` (a missing key means `pipeline` / `hidden`, A7), an open OFFER resumes into the right engine,
and replay redrives with the stored config.
"""

from __future__ import annotations

import io
import sqlite3
from pathlib import Path
from typing import Any

import pytest

from engine.dm import dm_tools, turn
from engine.dm.roles.prompts import load_prompt
from engine.dm.schemas import build_schema, defaults, schema_context
from engine.game import Game, GameConfig, saved_engine
from engine.llm.base import Packet, Role, validate
from engine.llm.offline import OfflineModel
from play.cli import App, _parser
from tests.engine.test_game import quick_start, seed_oracle

STORED = ["missing", "pipeline", "dm-tools"]
CALLER = ["default", "pipeline", "dm-tools"]


def config(engine: str | None, **kw: Any) -> GameConfig:
    return GameConfig(offline=True, **({"engine": engine} if engine else {}), **kw)


def strip_keys(path: Path, *keys: str) -> None:
    """Make a save as an older build wrote it: `game_created.config` without these keys (events are append-only,
    so the guard trigger is dropped for the edit and put back)."""
    import json

    con = sqlite3.connect(str(path))
    try:
        row = con.execute("SELECT seq, payload FROM events WHERE type='game_created'").fetchone()
        payload = json.loads(row[1])
        for k in keys:
            payload["config"].pop(k, None)
        trig = con.execute("SELECT sql FROM sqlite_master WHERE name='events_no_update'").fetchone()[0]
        con.execute("DROP TRIGGER events_no_update")
        con.execute("UPDATE events SET payload=? WHERE seq=?", (json.dumps(payload), row[0]))
        con.execute(trig)
        con.commit()
    finally:
        con.close()


def make_save(tmp_path: Path, stored: str, secrets: str | None = None) -> Path:
    """A save written with `stored` engine ("missing": the key stripped, as an old build wrote it)."""
    path = tmp_path / f"{stored}.db"
    game, _ = Game.new(path, config(None if stored == "missing" else stored, **({"dm_secrets": secrets} if secrets
                                                                               else {})), seed=7)
    game.close()
    if stored == "missing":
        strip_keys(path, "engine", "dm_secrets")
    return path


# ------------------------------------------------------------------------------------------- S1-S9


@pytest.mark.parametrize("caller", CALLER)
@pytest.mark.parametrize("stored", STORED)
def test_the_saves_engine_wins_over_the_callers(tmp_path: Path, stored: str, caller: str) -> None:
    path = make_save(tmp_path, stored)
    game, _ = Game.open(path, config(None if caller == "default" else caller))
    want = "pipeline" if stored == "missing" else stored
    try:
        assert game.config.engine == want and game.ctx.config["engine"] == want
        assert game._engine() is (dm_tools if want == "dm-tools" else turn)
    finally:
        game.close()


@pytest.mark.parametrize("caller", ["hidden", "visible"])
@pytest.mark.parametrize("stored", ["missing", "hidden", "visible"])
def test_the_saves_secrets_arm_wins_over_the_callers(tmp_path: Path, stored: str, caller: str) -> None:
    path = tmp_path / "s.db"
    game, _ = Game.new(path, config("dm-tools", dm_secrets="hidden" if stored == "missing" else stored), seed=7)
    game.close()
    if stored == "missing":
        strip_keys(path, "dm_secrets")
    game, _ = Game.open(path, config("dm-tools", dm_secrets=caller))
    try:
        assert game.ctx.config["dm_secrets"] == ("hidden" if stored == "missing" else stored)
        assert dm_tools.secrets_visible(game.ctx) == (stored == "visible")
    finally:
        game.close()


def test_a_save_without_the_key_is_a_pipeline_save_whatever_the_callers_default_is() -> None:
    """The trap when the default flips: opening a store never reads `GameConfig`'s default."""
    flipped = GameConfig.model_construct(engine="dm-tools", dm_secrets="visible")
    for stored in (None, {}, {"offline": True}):
        got = saved_engine(flipped, stored)
        assert (got.engine, got.dm_secrets) == ("pipeline", "hidden")
    assert saved_engine(flipped, {"engine": "dm-tools", "dm_secrets": "visible"}).engine == "dm-tools"


# ------------------------------------------------------------------------------------------- S10-S12


def play_to_offer(tmp_path: Path) -> tuple[Path, str]:
    path = tmp_path / "offer.db"
    game, r = Game.new(path, config("dm-tools"), seed=7)
    r = quick_start(game, seed_oracle(game, r))
    assert r.phase == "play"
    r = game.submit("I hit them.")
    assert r.pause is not None and r.pause.kind == "offer", r.text()
    turn_id = r.turn_id or ""
    game.close()
    return path, turn_id


def test_an_open_offer_resumes_into_the_dm_tools_engine(tmp_path: Path) -> None:
    path, offered = play_to_offer(tmp_path)
    game, r = Game.open(path, config(None))  # the caller's default is not what the save was played with
    try:
        assert r.pause is not None and r.pause.kind == "offer" and game._engine() is dm_tools
        r = game.answer("commit")
        roles = {c["role"] for c in game.store.model_calls(r.turn_id)}
        assert roles == {"dm"}, roles  # the answered offer is narrated by the DM role, not a Narrator
        assert r.turn_id != offered and r.fiction
    finally:
        game.close()


def test_the_dm_tools_save_reopened_stays_dm_tools_and_replays(tmp_path: Path) -> None:
    path, _ = play_to_offer(tmp_path)
    for caller in (None, "pipeline"):
        game, _ = Game.open(path, config(caller))
        assert game.config.engine == "dm-tools"
        if caller is None:
            game.answer("commit")
        else:  # opened again later with a pipeline caller: it plays on in dm-tools
            assert game.submit("I ask them what is going on.").turn_id
        game.close()
    res = Game.replay(path)  # S11: redriven with the stored config, the opens included
    assert res.identical, res.divergence


# ------------------------------------------------------------------------------------------- the CLI flag


def test_play_new_takes_an_engine_and_continue_does_not() -> None:
    assert _parser().parse_args(["new", "x", "--engine", "dm-tools"]).engine == "dm-tools"
    assert _parser().parse_args(["new", "x"]).engine is None
    with pytest.raises(SystemExit):
        _parser().parse_args(["continue", "x", "--engine", "dm-tools"])
    with pytest.raises(SystemExit):
        _parser().parse_args(["new", "x", "--engine", "bogus"])
    app = App(io.StringIO(), io.StringIO(), Path("."), offline=True, engine="dm-tools")
    assert app._config().engine == "dm-tools" and App(io.StringIO(), io.StringIO(), Path("."))._config().engine == (
        GameConfig().engine)


# ------------------------------------------------------------------------------------------- Role.DM


def test_the_dm_is_its_own_role_with_prompt_schema_and_a_model_slot(tmp_path: Path) -> None:
    assert dm_tools.DM_ROLE is Role.DM and Role.DM.value == "dm" and "dm" in GameConfig().models
    assert load_prompt("dm").startswith("# Role:") and not hasattr(dm_tools, "PROMPT")
    game, r = Game.new(tmp_path / "g.db", config("dm-tools"), seed=7)
    try:
        r = quick_start(game, seed_oracle(game, r))
        sctx = schema_context(game.store.state, game.rules)
        schema = build_schema(Role.DM, sctx)
        assert schema == dm_tools.step_schema(game.ctx, final=False)  # one builder, two doors
        assert validate(defaults(Role.DM, sctx), schema) == []
        r = game.submit("I ask them what is going on.")
        assert {c["role"] for c in game.store.model_calls(r.turn_id)} == {"dm"} and r.pause is None
    finally:
        game.close()


def pk(message: str) -> Packet:
    return Packet(instructions="", message=message)


PEOPLE = "People here:\n- npc.ada_sol: the ferry-keeper (she/her), wary\n"
FRESH = "TOOL RESULTS THIS TURN\n(none yet)"


def ask(message: str, *, final: bool = False) -> dict[str, Any]:
    schema = dm_tools.schema_for(["verb.strike", "verb.talk"], ["harm", "none"], final=final)
    data = OfflineModel().fill(Role.DM, schema, pk(message), turn_id="t", attempt=0).data
    assert validate(data, schema) == []
    return data


def test_the_offline_dm_proposes_one_roll_for_an_attack_and_talks_otherwise() -> None:
    hit = ask(f"{PEOPLE}\nTHE PLAYER'S MESSAGE\nI attack the ferry-keeper.\n\n{FRESH}")
    assert [c["tool"] for c in hit["calls"]] == ["change", "propose_roll"] and hit["calls"][1]["target"] == "npc.ada_sol"  # P3: the move first
    assert hit["calls"][1]["verb"] == "verb.strike" and hit["calls"][0]["to"] == "engaged" and hit["passage"]
    talk = ask(f"{PEOPLE}\nTHE PLAYER'S MESSAGE\nI ask her about the ferry.\n\n{FRESH}")
    assert talk["calls"] == [] and talk["passage"].startswith("The ferry-keeper") and talk["passage"].endswith("do?")


@pytest.mark.parametrize(("message", "final"), [
    (f"{PEOPLE}\nTHE PLAYER'S MESSAGE\nI attack her.\n\n{FRESH}", True),  # no calls left: the final step
    (f"{PEOPLE}\nTHE PLAYER'S MESSAGE\nI attack her.\n\nTOOL RESULTS THIS TURN\n[1] propose_roll {{}}\n -> REFUSED: x",
     False),  # not a fresh turn: one proposal only
    ("THE PLAYER'S MESSAGE\nI attack the wall.\n\n" + FRESH, False),  # no one here to aim at
    ("", False), ("THE PLAYER'S MESSAGE\n\n\n" + FRESH, False),
    ("THE PLAYER'S MESSAGE\nJe l'attaque, l'épée à la main ☠\n\n" + FRESH, False),
])
def test_the_offline_dm_asks_for_no_roll_without_a_target_a_call_left_or_a_fresh_turn(message: str,
                                                                                      final: bool) -> None:
    data = ask(message, final=final)
    assert data["calls"] == [] and data["passage"]


def test_the_offline_dm_after_an_offer_writes_only_the_lead_up() -> None:
    out = ask(f"{PEOPLE}\nTHE PLAYER'S MESSAGE\nI attack her.\n\nTOOL RESULTS THIS TURN\n[1] propose_roll {{}}\n"
              " -> ROLL OFFERED to the player (about 55% to succeed).", final=True)
    assert out["calls"] == [] and "hangs" in out["passage"]


def test_the_recorded_dm_tools_game_is_dm_calls_and_its_stored_config_says_so() -> None:
    import json

    rec = json.loads((Path(__file__).parents[1] / "replay" / "games" / "offline_seed11_dmtools.json").read_text("utf-8"))
    assert rec["created"]["config"]["engine"] == "dm-tools"
    roles = [c["role"] for c in rec["calls"] if c["turn_id"]]
    assert roles.count("dm") >= 20 and "reader" not in roles  # no Reader, Framer or Narrator in play turns
