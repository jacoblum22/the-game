"""Spec 031 prototype: the DM-with-tools engine (engine/dm/dm_tools.py) over the offline stand-in.

The tool layer's spine refusals (a dead actor, an item not owned, coin from no source), an OFFER pause round trip,
`reveal_clue` delivering a held clue, and the secrets arm (hidden by default; a leak is logged, never blocked).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from engine.dm import dm_tools
from engine.dm.adjudication import AdjudicationRecord
from engine.game import Game, GameConfig
from engine.gen.case import about_line, cases
from engine.harm.state import DEAD
from engine.llm.base import Role
from engine.llm.offline import ScriptedModel
from engine.retrieve.scene import pc_id
from engine.store.events import Event
from engine.world.common import fact
from engine.world.places import location
from engine.world.scenes import cast_present
from tests.engine.test_game import quick_start, seed_oracle

DM = Role.NARRATOR  # dm_tools.DM_ROLE


def to_play(tmp_path: Path, **cfg: Any) -> tuple[Game, ScriptedModel]:
    model = ScriptedModel()
    game, r = Game.new(tmp_path / "g.db", GameConfig(offline=True, engine="dm-tools", **cfg), seed=7, model=model)
    r = quick_start(game, seed_oracle(game, r))
    assert r.phase == "play"
    return game, model


def in_turn(game: Game, fn: Any) -> Any:
    """Run `fn(ctx, turn, tx)` inside one store transaction, as a DM turn would."""
    ctx = game.ctx
    with game.store.transaction("turn.900") as tx:
        ctx.tx = tx
        try:
            t = dm_tools.Turn(rec=AdjudicationRecord(turn_id="turn.900", pc=pc_id(tx.state)))
            t.env = dm_tools._env(ctx, t)
            return fn(ctx, t, tx)
        finally:
            ctx.tx = None


def npc_here(game: Game) -> str:
    return cast_present(game.store.state)[0]


def change(**kw: Any) -> dict[str, Any]:
    return {"tool": "change", "kind": "", "who": "", "what": "", "to": "", "amount": 0, "note": "", **kw}


# ------------------------------------------------------------------------------------------- spine refusals


def test_change_refuses_only_what_the_game_cannot_hold(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    npc = npc_here(game)
    pc = pc_id(game.store.state)

    def run(ctx: Any, t: Any, tx: Any) -> dict[str, str]:
        coin0 = tx.state.quantities[pc]["coin"].current
        out = {
            "no_source": dm_tools.tool(ctx, t, change(kind="coin", who="", to=pc, amount=5)),
            "too_much": dm_tools.tool(ctx, t, change(kind="coin", who=pc, to=npc, amount=coin0 + 1)),
            "unknown": dm_tools.tool(ctx, t, change(kind="give_item", what="item.no_such_thing", to=npc)),
            "pays": dm_tools.tool(ctx, t, change(kind="coin", who=pc, to=npc, amount=2)),
            "npc_pays": dm_tools.tool(ctx, t, change(kind="coin", who=npc, to=pc, amount=3)),
        }
        sword = next(i for i, e in tx.state.entities.items() if e.kind == "item" and "sword" in i)
        out["gives_own"] = dm_tools.tool(ctx, t, change(kind="give_item", what=sword, to=npc))
        out["not_owned"] = dm_tools.tool(ctx, t, change(kind="give_item", what=sword, to=pc))  # the NPC has it now
        tx.add(fact(tx, npc, "harm_state", DEAD, rule_id="07.1.3"))
        out["dead_pays"] = dm_tools.tool(ctx, t, change(kind="coin", who=npc, to=pc, amount=1))
        out["dead_leaves"] = dm_tools.tool(ctx, t, change(kind="npc_leaves", who=npc))
        out["dead_clue"] = dm_tools.tool(ctx, t, {"tool": "reveal_clue", "npc": npc, "question": "who did it?"})
        out["coin"] = str(tx.state.quantities[pc]["coin"].current - coin0)
        out["refusals"] = str(len(t.stats["refusals"]))
        return out

    out = in_turn(game, run)
    assert out["no_source"].startswith("REFUSED: coin from no source")
    assert out["too_much"].startswith("REFUSED") and "has only" in out["too_much"]
    assert out["unknown"].startswith("REFUSED: no item on record")
    assert out["pays"].startswith("done") and out["npc_pays"].startswith("done")
    assert out["coin"] == "1"  # -2 paid, +3 received: an NPC with no purse on record pays from their own means
    assert out["gives_own"].startswith("done")
    assert out["not_owned"].startswith("REFUSED") and "not" in out["not_owned"]
    for k in ("dead_pays", "dead_leaves", "dead_clue"):
        assert out[k].startswith("REFUSED") and "dead" in out[k], (k, out[k])
    assert out["refusals"] == "7"  # every refusal is logged for the DM's turn stats


# ------------------------------------------------------------------------------------------- the OFFER pause


def test_a_proposed_roll_pauses_on_the_offer_then_the_dm_narrates_the_result(tmp_path: Path) -> None:
    game, model = to_play(tmp_path)
    npc = npc_here(game)
    roll = {"tool": "propose_roll", "goal": "slip past the guard unseen", "verb": "verb.sneak", "target": npc,
            "how": "keeping to the shadows", "attribute": "agility", "difficulty": "moderate",
            "why_uncertain": "she is watching the door", "stakes": "risky", "nonlethal": False, "change_kind": "none",
            "change_what": "", "change_whom": ""}
    model.push(DM, {"calls": [roll], "passage": "You edge toward the door.", "asks": []})
    r = game.submit("I sneak past her.")
    assert r.pause is not None and r.pause.kind == "offer"
    assert r.fiction == "You edge toward the door."  # the lead-up only: one DM call, no outcome
    assert any(b.kind == "OFFER" for b in r.oof_blocks)
    stats = game.store.turn(r.turn_id).screen["dm_tools"]
    assert stats["tool_calls"] == 1 and stats["rolls"][0]["status"] == ["paused"] and stats["model_calls"] == 1
    model.push(DM, {"calls": [], "passage": "Her eyes slide past you.", "asks": []},
               {"calls": [], "passage": "Her eyes slide past you.", "asks": []})
    r = game.answer("commit")
    if r.pause is not None:  # a near miss: the player picks, then the DM narrates
        assert r.pause.kind == "near_miss" and not r.fiction
        r = game.answer("failure")
    assert r.pause is None and r.fiction == "Her eyes slide past you."
    assert any(b.kind == "RESULT" for b in r.oof_blocks)
    assert any(e.type == "frame_resolved" for e in game.store.events())


def test_a_proposal_naming_no_one_takes_its_goal_from_the_dm_words_not_from_here(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    roll = {"tool": "propose_roll", "goal": "Find the trail on the road", "verb": "verb.observe", "target": "none",
            "how": "reading the mud", "attribute": "wits", "difficulty": "hard", "why_uncertain": "rain",
            "stakes": "risky", "nonlethal": False, "change_kind": "none", "change_what": "the trail",
            "change_whom": ""}

    def run(ctx: Any, t: Any, tx: Any) -> Any:
        dm_tools.tool(ctx, t, roll)
        p = tx.state.open_pause()
        return p.detail["frame"]["beat"]["change"] if p is not None else t.rec.beats[-1].change

    got = in_turn(game, run)
    assert "the trail" in str(got) and "gate" not in str(got).lower(), got


# ------------------------------------------------------------------------------------------- clues and secrets


def _holder_here(game: Game) -> tuple[str, dict[str, Any], dict[str, Any]]:
    """A case node's placement holder, positioned in the scene (the case graph is spec 029's)."""
    st = game.store.state
    for c in cases(st).values():
        for n in c["nodes"]:
            for p in n["placements"]:
                h = p.get("holder")
                if h in st.entities and st.entities[h].kind == "npc" and not n.get("found"):
                    with game.store.transaction("turn.899") as tx:
                        tx.add(Event.of("position_set", source="engine", rule_id="test", entity=h,
                                        location=location(st)))
                    return h, c, n
    raise AssertionError("no NPC holds a case placement in this seed")


def test_reveal_clue_delivers_a_held_clue(tmp_path: Path) -> None:
    game, model = to_play(tmp_path)
    npc, case, node = _holder_here(game)
    model.push(Role.CLUE, {"about": "1", "part": "none"})  # held clues are listed first
    q = f"What do you know about {about_line(game.store.state, case, node).split(' (')[0]}?"
    out = in_turn(game, lambda ctx, t, tx: (dm_tools.tool(ctx, t, {"tool": "reveal_clue", "npc": npc,
                                                                    "question": q}), t.stats["clues"]))
    text, clues = out
    assert text.startswith(("CLUE", "POINTER")), text
    assert clues and clues[0]["npc"] == npc
    pc = pc_id(game.store.state)
    assert game.store.state.knowledge.get(pc)  # the PC learned it (a fact on record), not just words


def test_secrets_are_hidden_by_default_visible_on_the_arm_and_leaks_are_logged(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    npc, _, node = _holder_here(game)
    assert node["fact"] in dm_tools.secrets(game.store.state, npc)
    assert "PRIVATE" not in dm_tools.situation(game.ctx)
    game.ctx.config = {**game.ctx.config, "dm_secrets": "visible"}
    assert f"PRIVATE (they know this; the player does not): {node['fact']}" in dm_tools.situation(game.ctx)

    def leak(ctx: Any, t: Any, tx: Any) -> list[Any]:
        dm_tools._audit(ctx, t, f"She leans in and says: {node['fact']}")
        return t.stats["leaks"]

    leaks = in_turn(game, leak)
    assert npc in {x["npc"] for x in leaks}


def test_the_default_engine_is_the_pipeline(tmp_path: Path) -> None:
    assert GameConfig().engine == "pipeline" and GameConfig().dm_secrets == "hidden"
    game, _ = to_play(tmp_path)
    assert game._engine() is dm_tools
    game.ctx.config = {**game.ctx.config, "engine": "pipeline"}
    from engine.dm import turn

    assert game._engine() is turn
