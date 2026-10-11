"""Spec 033 P9: the fixes traced in specs/033-dm-states-code-records/trace-no-foe-turns.md.

1. A refused attack never happened: the fight starts after the licence gate, before the reach check.
2. A take-back that reverts a fight start reverts the time mode with it.
Nothing here reads prose: the code keys on the DM's verb, approach and ids."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from engine.dm import dispute, dm_tools
from engine.resolve import conflict
from engine.retrieve.scene import pc_id
from tests.engine.test_dm_tools import in_turn, npc_here, to_play
from tests.engine.test_spec033_p8 import ROLL, snap

REFUSED = {"approach": "flying or teleporting"}  # an `excludes` entry no held licence covers: the gate refuses


def strike(npc: str, **kw: Any) -> dict[str, Any]:
    return {**ROLL, "verb": "verb.strike", "target": npc, "change_kind": "harm", "weapon": "unarmed", **kw}


def go(game: Any, call: dict[str, Any]) -> tuple[str, list[str]]:
    return in_turn(game, lambda ctx, t, tx: (dm_tools._propose_roll(ctx, t, call), list(t.stats["defaults"])))


@pytest.mark.parametrize("starts", ["yes", ""])
def test_a_gate_refused_strike_starts_no_fight_and_writes_nothing(tmp_path: Path, starts: str) -> None:
    game, _ = to_play(tmp_path)
    npc, pc = npc_here(game), pc_id(game.store.state) or ""
    before = snap(game, npc)
    out, defaults = go(game, strike(npc, starts_fight=starts, fight_to="close", **REFUSED))
    assert "NOT POSSIBLE" in out or "REFUSED" in out, out
    st = game.store.state
    assert not conflict.active(st) and conflict.record(st) == {}
    assert conflict._band(st, pc, npc) is None and snap(game, npc) == before
    assert not [d for d in defaults if d.startswith("not_chosen:fight") or d == "not_chosen:position"]


def test_the_retry_that_passes_the_gate_starts_the_fight_once(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    npc, pc = npc_here(game), pc_id(game.store.state) or ""
    go(game, strike(npc, starts_fight="yes", fight_to="engaged", **REFUSED))
    assert not conflict.active(game.store.state)
    out, defaults = go(game, strike(npc, starts_fight="yes", fight_to="engaged"))
    st = game.store.state
    assert out.startswith("A fight begins with") and "ROLL OFFERED" in out
    assert conflict.active(st) and conflict.record(st)["foes"] == [npc] and conflict._band(st, pc, npc) == "engaged"
    assert sum(1 for e in game.store.events(types=["boundary_marked"]) if e.payload.boundary == "conflict_start") == 1


def test_a_take_back_of_a_fight_start_restores_the_time_mode(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    npc, pc = npc_here(game), pc_id(game.store.state) or ""
    mode0, first = game.store.state.time.mode, game.store.last_seq + 1
    in_turn(game, lambda ctx, t, tx: dm_tools._fight(ctx, npc, pc, "engaged"))
    st = game.store.state
    assert conflict.active(st) and st.time.mode != mode0

    def back(ctx: Any, t: Any, tx: Any) -> list[int]:
        return dispute._rewind(ctx, tx, first, "test")

    assert in_turn(game, back)
    st = game.store.state
    assert not conflict.active(st) and conflict.record(st) == {} and st.time.mode == mode0
    # a new fight afterwards begins properly: its note is told and `previous` is the mode the fight interrupted
    note: list[str] = []
    in_turn(game, lambda ctx, t, tx: dm_tools._attack_starts_fight(
        ctx, t, {**ROLL, "starts_fight": "yes", "fight_to": "close"}, "verb.strike", npc, SimpleNamespace(weapon="unarmed"), note))
    assert note and note[0].startswith("A fight begins with")
    assert conflict.record(game.store.state)["previous"] == conflict.clock.mode_of(mode0)
