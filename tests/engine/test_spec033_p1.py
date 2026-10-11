"""Spec 033 P1: the DM contract. The step schema is pinned to the contract table, the intake builds `Beat.stated` and
logs each default it holds (`not_chosen:{field}`, D3), `change position` and `end_game` exist, `dm.md` fits its word
budget, and the offline DM fills the new fields. Behavior on the resolve path is the later phases'."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from engine.dm import dm_tools
from engine.dm.roles.prompts import load_prompt
from engine.dm.schemas import numeric_fields
from engine.llm.base import Packet, Role, validate
from engine.llm.offline import OfflineModel
from engine.resolve import conflict
from engine.resolve.types import Beat, Stated
from engine.retrieve.scene import pc_id
from tests.engine.test_dm_tools import change, in_turn, npc_here, to_play


def roll(**kw: Any) -> dict[str, Any]:
    base = {"tool": "propose_roll", "goal": "Hit him", "verb": "verb.strike", "target": "", "as": "none", "how": "",
            "attribute": "", "difficulty": "", "why_uncertain": "", "stakes": "risky", "nonlethal": False,
            "force": "none", "weapon": "", "reads": False, "approach": "plain", "fail_cost": "none", "fail_on": "",
            "change_kind": "harm", "change_what": "", "change_whom": ""}
    return {**base, **kw}


def calls(schema: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {b["properties"]["tool"]["enum"][0]: b["properties"]
            for b in schema["properties"]["calls"]["items"]["anyOf"]}


# ------------------------------------------------------------------------------------------- the contract table


def test_the_prompt_fits_its_budget() -> None:
    assert len(load_prompt("dm").split()) <= 800


def test_the_step_schema_is_the_contract_table(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    schema = dm_tools.step_schema(game.ctx, final=False)
    assert validate({"calls": [], "passage": "", "said": [], "asks": [], "cost_form": ""}, schema) == []
    tools = calls(schema)
    assert set(tools) == set(dm_tools.TOOLS)
    pr = tools["propose_roll"]
    assert set(pr) >= {"as", "force", "weapon", "reads", "approach", "fail_on", "fail_cost", "nonlethal", "change_kind",
                       "change_what", "change_whom"}
    assert pr["as"]["enum"] == ["none", "he", "she", "they", "creature", "thing"]
    assert pr["force"]["enum"] == ["none", "push", "prone"]
    assert pr["approach"]["enum"][0] == "plain" and len(pr["approach"]["enum"]) == 14  # the 13 `excludes` entries
    assert set(pr["approach"]["enum"][1:]) == {e["what"] for v in game.ctx.rules.basic_verbs.values()
                                               for e in v.get("excludes") or ()}
    ch = tools["change"]
    assert set(ch) >= {"name", "as", "knows"} and "position" in ch["kind"]["enum"]
    assert set(tools["end_game"]) == {"tool", "why"}
    assert set(schema["properties"]["said"]["items"]["properties"]) == {"npc", "words", "as"}
    assert "foes" not in schema["properties"] and "cost_form" in schema["properties"]  # D2: foes are a separate call
    assert numeric_fields(schema) == []  # INV-3: `amount` is the one exempt number


def test_the_foe_call_schema_limits_each_foe_to_its_legal_acts() -> None:
    schema = dm_tools.foe_schema({"npc.a": ["strike", "flee"], "npc.b": ["stand", "wait"]})
    ok = {"foes": [{"foe": "npc.a", "act": "flee", "target": "pc", "nonlethal": False},
                   {"foe": "npc.b", "act": "stand", "target": "", "nonlethal": True}]}
    assert validate(ok, schema) == []
    bad = {"foes": [{"foe": "npc.b", "act": "strike", "target": "pc", "nonlethal": False}]}
    assert validate(bad, schema) != []
    assert set(dm_tools.FOE_ACTS) == {"strike", "close_in", "withdraw", "stand", "break_free", "grapple", "flee", "yield", "wait"}
    assert validate({"foes": []}, dm_tools.foe_schema({})) == []
    assert numeric_fields(schema) == []


# ------------------------------------------------------------------------------------------- the intake


def test_the_intake_fills_stated_and_logs_each_default(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    npc = npc_here(game)

    def run(ctx: Any, t: Any, tx: Any) -> dict[str, Any]:
        out: dict[str, Any] = {}
        out["force"] = dm_tools._stated(ctx, t, roll(verb="verb.force", target=npc), "verb.force", npc)
        out["force_given"] = dm_tools._stated(ctx, t, roll(verb="verb.force", force="prone"), "verb.force", npc)
        out["strike"] = dm_tools._stated(ctx, t, roll(target=npc), "verb.strike", npc)
        out["unarmed"] = dm_tools._stated(ctx, t, roll(weapon="unarmed", nonlethal=True), "verb.strike", npc)
        out["not_held"] = dm_tools._stated(ctx, t, roll(weapon="item.no_such_blade"), "verb.strike", npc)
        out["read"] = dm_tools._stated(ctx, t, roll(verb="verb.observe", reads=True), "verb.observe", None)
        out["bad_approach"] = dm_tools._stated(ctx, t, roll(approach="by magic"), "verb.strike", npc)
        out["gear"] = dm_tools._stated(ctx, t, roll(fail_cost="cost.gear"), "verb.strike", npc)
        out["defaults"] = list(t.stats["defaults"])
        return out

    got = in_turn(game, run)
    assert isinstance(got["force"], Stated) and got["force"].force == "push"  # D3: no refusal, default push
    assert got["force_given"].force == "prone"
    assert got["strike"].weapon == "unarmed" and got["strike"].force is None  # nothing wielded on record
    assert got["unarmed"].weapon == "unarmed" and got["unarmed"].nonlethal
    assert got["not_held"].startswith("REFUSED") and "unarmed" in got["not_held"]  # a weapon the character lacks
    assert got["read"].reads and got["read"].approach == "plain"
    assert got["bad_approach"].startswith("REFUSED") and "plain" in got["bad_approach"]
    assert got["gear"].fail_on is None
    assert got["defaults"].count("not_chosen:force") == 1
    assert got["defaults"].count("not_chosen:weapon") == 2  # the plain strike and the gear-cost strike
    assert got["defaults"].count("not_chosen:fail_on") == 1


def test_a_proposal_carries_stated_to_its_beat(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    npc = npc_here(game)
    r = roll(verb="verb.sneak", target=npc, goal="Slip past her", change_kind="none", nonlethal=True)

    def run(ctx: Any, t: Any, tx: Any) -> Any:
        dm_tools.tool(ctx, t, r)
        p = tx.state.open_pause()
        return Beat.model_validate(p.detail["frame"]["beat"]) if p is not None else t.rec.beats[-1]

    beat = in_turn(game, run)
    assert beat.stated is not None and beat.stated.nonlethal and beat.stated.approach == "plain"


def test_a_pipeline_beat_has_no_stated_and_dumps_as_before() -> None:
    beat = Beat(id="beat.1", actor="pc.x", intent="i", method="m")
    assert beat.stated is None and "stated" not in beat.model_dump(mode="json")


def test_move_to_states_a_position_and_refuses_a_place(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    npc = npc_here(game)
    pc = pc_id(game.store.state)
    assert game.store.state.scene is not None
    place = game.store.state.scene.place_id

    def run(ctx: Any, t: Any, tx: Any) -> Any:
        ok = dm_tools._stated(ctx, t, roll(change_kind="move_to", change_what="far", target=npc), "verb.move", npc)
        theirs = dm_tools._stated(ctx, t, roll(change_kind="move_to", change_what="engaged", change_whom=npc, target=npc),
                                  "verb.move", npc)
        words = dm_tools._stated(ctx, t, roll(change_kind="move_to", change_what="the far gate", target=npc), "verb.move", npc)
        thing = dm_tools._stated(ctx, t, roll(change_kind="move_to", change_what="near", target=None), "verb.move", None)
        no = dm_tools._stated(ctx, t, roll(change_kind="move_to", change_what=place, target=npc), "verb.move", npc)
        return ok, theirs, words, thing, no

    ok, theirs, words, thing, no = in_turn(game, run)
    assert ok.position == (pc, "far", npc)  # mover omitted = the actor
    assert theirs.position == (npc, "engaged", pc)
    assert words.position is None and thing.position is None  # not a band: no position is stated
    assert isinstance(no, str) and no.startswith("REFUSED") and "travel" in no


# ------------------------------------------------------------------------------------------- change position, end_game


def test_change_position_writes_a_band_or_a_place(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    npc = npc_here(game)
    pc = pc_id(game.store.state) or ""
    assert game.store.state.scene is not None
    place = game.store.state.scene.place_id

    def run(ctx: Any, t: Any, tx: Any) -> dict[str, Any]:
        out: dict[str, Any] = {}
        out["pc_band"] = dm_tools.tool(ctx, t, change(kind="position", to="engaged", what=npc))
        out["band"] = conflict._band(tx.state, pc, npc), conflict._band(tx.state, npc, pc)
        out["npc_band"] = dm_tools.tool(ctx, t, change(kind="position", who=npc, to="far"))  # the other = the character
        out["npc_band_is"] = conflict._band(tx.state, npc, pc)
        out["default_other"] = dm_tools.tool(ctx, t, change(kind="position", to="close"))  # the one other person here
        out["pc_place"] = dm_tools.tool(ctx, t, change(kind="position", to=place))
        out["bad_to"] = dm_tools.tool(ctx, t, change(kind="position", to="somewhere"))
        out["gone"] = dm_tools.tool(ctx, t, change(kind="position", to="near", what="npc.nobody"))  # the other is not on record
        out["defaults"] = list(t.stats["defaults"])
        return out

    got = in_turn(game, run)
    assert got["pc_band"].startswith("done") and got["band"] == ("engaged", "engaged")
    assert got["npc_band"].startswith("done") and got["npc_band_is"] == "far"
    assert got["pc_place"].startswith("REFUSED") and "travel" in got["pc_place"]
    assert got["bad_to"].startswith("REFUSED") and "band" in got["bad_to"]
    assert got["gone"].startswith("REFUSED")
    assert "not_chosen:who" in got["defaults"]
    if len(game.store.state.scene.cast_present) == 2:  # exactly one other person here: the default other party
        assert got["default_other"].startswith("done")


def test_end_game_asks_the_player_to_confirm(tmp_path: Path) -> None:  # wired by P5; see test_spec033_p5.py
    game, _ = to_play(tmp_path)
    out = in_turn(game, lambda ctx, t, tx: dm_tools.tool(ctx, t, {"tool": "end_game", "why": "the player is done"}))
    assert out.startswith("ASKED")


# ------------------------------------------------------------------------------------------- offline DM


def test_the_offline_dm_fills_the_new_fields(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    npc = npc_here(game)
    name = game.store.state.entities[npc].name
    schema = dm_tools.step_schema(game.ctx, final=False)
    msg = f"THE PLAYER'S MESSAGE\nI strike {name}.\n\nTOOL RESULTS THIS TURN\n(none yet)\n- {npc}: {name} (sly)"
    data = OfflineModel().fill(Role.DM, schema, Packet(instructions="", message=msg), turn_id=None, attempt=0).data
    assert validate(data, schema) == [], validate(data, schema)
    for fld in ("as", "force", "weapon", "reads", "approach", "fail_on"):
        assert all(fld in c for c in data["calls"] if c["tool"] == "propose_roll")
    foe = dm_tools.foe_schema({"npc.a": ["wait", "strike"], "npc.b": ["stand"]})
    got = OfflineModel().fill(Role.DM, foe, Packet(instructions="", message="x"), turn_id=None, attempt=0).data
    assert validate(got, foe) == [] and [f["act"] for f in got["foes"]] == ["strike", "stand"]


def test_a_scripted_dm_step_naming_only_what_it_means_is_valid(tmp_path: Path) -> None:
    game, model = to_play(tmp_path)
    model.push(Role.DM, {"calls": [], "passage": "Quiet.", "said": [{"npc": npc_here(game), "words": "Hm."}]})
    r = game.submit("I wait.")
    assert r.fiction == "Quiet."
