"""T076: offline end-to-end games through `engine.game.Game` with a scripted player (tests/e2e/driver.py).

- `test_offline_game_60_turns` (default run) and `test_offline_game_500_turns` (slow: `--runslow`): a mixed seed
  answered partly in words, a quick-start character, then play across scenes and places (looks, questions, talk,
  risky acts whose OFFER is committed, changed or withdrawn, near misses, redirects, travel, rests, codex reads,
  out-of-fiction questions, a dispute), retirement with its epilogue and ending menu, and a new character who plays
  on. Asserted: no exception and no turn limit; every pause kind reached is resumed by closing and reopening the
  game there, and the same pause comes back; the rendered packets stay flat over the game; `Game.replay` rebuilds
  every event identically.
- `test_lethal_warning_last_chance_death_and_a_new_character`: the lethal path (a scripted hopeless fight; the
  offline stand-in never frames a lethal beat): the warning and the last-chance menu are each resumed, death, the
  epilogue, the ending menu (resumed), a new character, then more play.
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from engine.game import Game
from engine.harm.threshold import ending_state
from engine.llm.base import Role
from engine.llm.offline import ScriptedModel
from engine.world.places import location
from tests.e2e.driver import OFFLINE, Driver, trend
from tests.engine.test_ending import LETHAL, STRIKE, wight_scene
from tests.engine.test_turn_adjudication import framer, reader

SEED_KINDS = {"seed_step:mode", "seed_step:pick", "seed_step:question", "seed_step:summary"}
ALWAYS = SEED_KINDS | {"create_step:creation", "offer", "redirect", "clarify:retire", "ending"}
GROWTH = 1.25  # the last quarter's mean packet may not exceed the first quarter's by more than this


def run_game(path: Path, turns: int, seed: int) -> tuple[Driver, dict[str, float]]:
    t0 = time.perf_counter()
    d = Driver.start(path, seed=seed)
    places = {location(d.game.store.state)}
    first = turns * 3 // 4
    for _ in range(first):
        d.play(1)
        places.add(location(d.game.store.state))
    d.retire_and_continue()
    d.play(turns - first)
    timings = {"play_s": time.perf_counter() - t0}
    d.sizes = d.packet_sizes()
    d.game.close()
    t1 = time.perf_counter()
    res = Game.replay(path)
    timings["replay_s"] = time.perf_counter() - t1
    assert res.identical, res.divergence
    timings["places"] = float(len(places))
    timings["events"] = float(res.events)
    return d, timings


def check_game(d: Driver, turns: int, timings: dict[str, float]) -> None:
    assert d.turns >= turns  # no turn limit anywhere (FR-012)
    assert ALWAYS <= set(d.seen), sorted(d.seen)
    assert set(d.seen) == set(d.resumed), f"reached but never resumed: {set(d.seen) - set(d.resumed)}"
    assert timings["places"] >= 2 and d.disputed
    kinds = [s.arg for s in d.steps if s.kind == "submit"]
    assert any("rest" in k or "breath" in k for k in kinds) and any(k.startswith("I head to") for k in kinds)
    choices = {s.arg for s in d.steps if s.kind == "answer"}
    assert {"commit", "change"} <= choices or {"commit", "withdraw"} <= choices
    lines = [f"{turns} turns: play {timings['play_s']:.1f}s, replay {timings['replay_s']:.1f}s, "
             f"{int(timings['events'])} events, {int(timings['places'])} places; pauses {d.seen}"]
    for role, pts in sorted(d.sizes.items()):
        if len(pts) < 8:
            continue
        first, last, slope = trend(pts)
        lines.append(f"  {role}: n={len(pts)} first-quarter {first:.0f} last-quarter {last:.0f} "
                     f"slope {slope:+.2f}/turn")
        assert last <= first * GROWTH, f"{role} packets grow: {first:.0f} -> {last:.0f}"
        span = max(x for x, _ in pts) - min(x for x, _ in pts)
        assert slope * span <= first * (GROWTH - 1), f"{role} packets trend upward: {slope:+.2f}/turn"
    print("\n".join(lines))


def test_offline_game_60_turns(tmp_path: Path) -> None:
    d, timings = run_game(tmp_path / "g.db", 60, seed=11)
    check_game(d, 60, timings)


@pytest.mark.slow
def test_offline_game_500_turns(tmp_path: Path) -> None:
    d, timings = run_game(tmp_path / "g.db", 500, seed=3)
    check_game(d, 500, timings)
    assert {"near_miss"} <= set(d.seen)


def test_lethal_warning_last_chance_death_and_a_new_character(tmp_path: Path) -> None:
    model = ScriptedModel()
    d = Driver.start(tmp_path / "g.db", seed=5, model=model)
    d.play(10)
    if d.last.pause is not None:
        d.settle(d.last)
    wight_scene(d.game)  # test set-up, not play: Milestone 1 places no adversaries by itself
    for _ in range(12):
        model.push(Role.READER, reader("DECLARATION", "I hack at the wight.", STRIKE))
        model.push(Role.FRAMER, framer(**LETHAL))
        r = d.call("submit", "I hack at the wight.")
        for _ in range(4):
            if r.pause is None or r.pause.kind != "offer":
                break
            ids_ = [c.id for c in r.pause.choices]
            r = d.call("answer", "continue" if "continue" in ids_ else "commit")
        if r.pause is not None and r.pause.kind == "last_chance":
            break
    assert {"offer:warning", "last_chance"} <= set(d.resumed), d.resumed
    pc = d.game.store.state.meta["pc.active"]
    r = d.call("answer", "lc.last_stand")
    model.push(Role.READER, reader("DECLARATION", "I hack at the wight.", STRIKE))
    model.push(Role.FRAMER, framer(**LETHAL))
    r = d.settle(d.call("submit", "I fight on."))
    assert ending_state(d.game.store.state) == "death" and r.phase == "ending" and "ending" in d.resumed
    assert any(b.kind == "EPILOGUE" for b in d.last.oof_blocks) or d.game.store.state.meta.get(f"legacy.{pc}")
    r = d.call("new_character")
    for msg in ("", "", "", "", "Ash, he/him", "begin"):
        if r.phase != "creation":
            break
        r = d.call("submit", msg)
    st = d.game.store.state
    assert r.phase == "play" and st.meta["pc.active"] != pc and r.fiction
    d.play(10)
    assert d.game.store.rebuild() == d.game.store.state
    d.game.close()
    reopened, back = Game.open(tmp_path / "g.db", OFFLINE, model=model)
    assert back.phase == "play"
    reopened.close()
