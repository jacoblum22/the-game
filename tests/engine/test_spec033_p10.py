"""Spec 033 P10: two small fixes from specs/033-dm-states-code-records/HANDOFF.md item 28.

1. An accepted crude fallback on a Strike, Grapple or Force starts the fight as an accepted first call does
   [owner ruling 2026-10-11, "Field on attacks"].
2. A refusal's "[REDIRECT] Not as tried" line goes only when the DM names the refused call's tag in `retry_of` and the
   retry is accepted. Nothing here reads prose: the code keys on the DM's verb, approach, ids and tags."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from engine.dm import dm_tools
from engine.dm.narration import turn_blocks
from engine.resolve import conflict
from engine.retrieve.scene import pc_id
from tests.engine.test_dm_tools import in_turn, npc_here, to_play
from tests.engine.test_spec033_p8 import snap
from tests.engine.test_spec033_p9 import REFUSED, go, strike

FALLBACK = {"approach": "picking a lock"}  # a licence the character lacks; its crude fallback is a Force
ACCEPT = "accept:lic.training.guile_thievery"


def starts(game: Any) -> int:
    return sum(1 for e in game.store.events(types=["boundary_marked"]) if e.payload.boundary == "conflict_start")


def accept(game: Any, live: bool = False, **kw: Any) -> tuple[str, list[str]]:
    """Offer the fallback, then answer it the way `_run` does: `_accepted_attack`, then `resume`."""
    npc = npc_here(game)
    out, _ = go(game, strike(npc, **FALLBACK, **kw))
    assert "ROLL OFFERED" in out and conflict.active(game.store.state) == live  # the offer starts no fight
    pause = game.store.state.open_pause()
    assert pause is not None and pause.detail["stage"] == "redirect"

    def answer(ctx: Any, t: Any, tx: Any) -> list[str]:
        note: list[str] = []
        dm_tools._accepted_attack(ctx, t, pause, ACCEPT, note)
        from engine.dm.turn import _resume

        _resume(ctx, t.env, pause, ACCEPT, t.oof)
        return note

    return out, in_turn(game, answer)


@pytest.mark.parametrize("starts_fight", ["", "yes"])
def test_an_accepted_fallback_attack_starts_the_fight_once(tmp_path: Path, starts_fight: str) -> None:
    game, _ = to_play(tmp_path)
    npc, pc = npc_here(game), pc_id(game.store.state) or ""
    _, note = accept(game, starts_fight=starts_fight, fight_to="close")
    st = game.store.state
    assert note and note[0].startswith("A fight begins with")
    assert conflict.active(st) and conflict.record(st)["foes"] == [npc] and conflict._band(st, pc, npc) == "close"
    assert starts(game) == 1


def test_an_accepted_fallback_attack_the_dm_called_a_single_blow_starts_none(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    _, note = accept(game, starts_fight="no")
    assert not note and not conflict.active(game.store.state) and starts(game) == 0


def test_an_accepted_fallback_on_a_foe_already_in_the_fight_resets_nothing(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    npc, pc = npc_here(game), pc_id(game.store.state) or ""
    in_turn(game, lambda ctx, t, tx: dm_tools._fight(ctx, npc, pc, "engaged"))
    before = snap(game, npc)
    _, note = accept(game, live=True, starts_fight="yes", fight_to="close")
    assert not note and starts(game) == 1
    after = snap(game, npc)
    assert after[:4] == before[:4] and conflict._band(game.store.state, pc, npc) == "engaged"


# ------------------------------------------------------------------------------------------- retry_of


def redirects(game: Any, run: Any) -> tuple[list[str], str]:
    """(the REDIRECT items still owed, everything the player is shown) after `run(ctx, t)` made its calls."""
    def go_(ctx: Any, t: Any, tx: Any) -> tuple[list[str], str]:
        run(ctx, t)
        blocks, _ = turn_blocks(ctx, t.oof, t.rec, ctx.tx.state.open_pause())
        return [o["kind"] for o in t.oof if o["kind"] == "REDIRECT"], "\n".join(b.text for b in blocks)

    return in_turn(game, go_)


def test_a_refusal_result_ends_with_its_tag_and_a_stated_retry_removes_the_line(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    npc = npc_here(game)
    seen: list[str] = []

    def run(ctx: Any, t: Any) -> None:
        seen.append(dm_tools._propose_roll(ctx, t, strike(npc, starts_fight="yes", fight_to="engaged", **REFUSED)))
        seen.append(dm_tools._propose_roll(ctx, t, strike(npc, starts_fight="yes", fight_to="engaged", retry_of="r1")))

    kinds, shown = redirects(game, run)
    assert seen[0].endswith("(refused call r1)") and "ROLL OFFERED" in seen[1]
    assert kinds == [] and "Not as tried" not in shown and "OFFER" in shown.upper()


def test_a_different_action_with_retry_of_blank_keeps_both_lines(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    npc = npc_here(game)
    seen: list[str] = []

    def run(ctx: Any, t: Any) -> None:
        seen.append(dm_tools._propose_roll(ctx, t, strike(npc, starts_fight="no", **REFUSED)))
        t.stats["defaults"].clear()
        seen.append(dm_tools._propose_roll(ctx, t, strike(npc, starts_fight="no")))
        seen.append(str(list(t.stats["defaults"])))

    kinds, shown = redirects(game, run)
    assert seen[0].endswith("(refused call r1)") and "ROLL OFFERED" in seen[1]
    assert kinds == ["REDIRECT"] and "Not as tried" in shown
    assert "retry" not in seen[2]  # a blank `retry_of` logs no default


def test_two_refused_calls_each_keep_their_own_line_and_a_bad_tag_is_ignored(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    npc = npc_here(game)
    seen: list[str] = []

    def run(ctx: Any, t: Any) -> None:
        seen.append(dm_tools._propose_roll(ctx, t, strike(npc, starts_fight="no", **REFUSED)))
        seen.append(dm_tools._propose_roll(ctx, t, strike(npc, starts_fight="no", approach="magical sight")))
        seen.append(dm_tools._propose_roll(ctx, t, strike(npc, starts_fight="no", retry_of="r9")))  # no such tag

    kinds, _ = redirects(game, run)
    assert seen[0].endswith("(refused call r1)") and seen[1].endswith("(refused call r2)")
    assert kinds == ["REDIRECT", "REDIRECT"]


def test_a_tag_of_a_call_that_is_still_refused_removes_nothing(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    npc = npc_here(game)

    def run(ctx: Any, t: Any) -> None:
        dm_tools._propose_roll(ctx, t, strike(npc, starts_fight="no", **REFUSED))
        dm_tools._propose_roll(ctx, t, strike(npc, starts_fight="no", approach="magical sight", retry_of="r1"))

    kinds, _ = redirects(game, run)
    assert kinds == ["REDIRECT", "REDIRECT"]
