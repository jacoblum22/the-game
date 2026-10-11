"""Spec 033 P11: the three fixes traced in specs/033-dm-states-code-records/trace-live3.md.

1. A failed observe roll in a live conflict, with clocks active but none listening for cost.time, no longer crashes.
2. `take` / `give` of a thing the DM named only in words make the item from the DM's words (as `open` does).
3. Every foe act shows a one-line RESULT (a miss, a hold, a move), in words, with no dice numbers.
Nothing here reads prose: the code keys on the DM's ids and tools."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from engine.dm.answer import name as _name
from engine.resolve import pipeline as pl
from engine.retrieve.scene import pc_id
from engine.store.events import ClockRecord, Event
from tests.engine.test_dm_tools import DM, in_turn, npc_here, to_play
from tests.engine.test_spec032_p4 import start_fight
from tests.engine.test_spec033_p2a import BASE, fixed
from tests.engine.test_spec033_p8 import ROLL


def _clock(game: Any, cid: str, on: str) -> None:
    ev = Event.of("clock_created", source="p11", clock=ClockRecord(
        id=cid, name=cid, kind="danger", segments=6, tick_sources=[{"on": on, "ticks": "U(severity)"}]))
    in_turn(game, lambda ctx, t, tx: tx.add(ev))


@pytest.mark.parametrize("listens", ["frame", "cost.exposure"])
def test_a_failed_look_in_a_conflict_without_a_time_clock_does_not_crash(tmp_path: Path, listens: str) -> None:
    """The trace's case: a conflict, a clock that is not listening for time (or listens only for exposure)."""
    game, model = to_play(tmp_path)
    start_fight(game)
    _clock(game, "clk.goal", listens)
    assert game.store.state.time.mode == "conflict"
    call = {**ROLL, "tool": "propose_roll", "verb": "verb.observe", "target": "none", "attribute": "wits",
            "difficulty": "legendary", "stakes": "dire", "fail_cost": "cost.time", "change_kind": "learn",
            "change_what": "the trail", "how": "reading the mud"}
    model.push(DM, {"calls": [call], "passage": "You look.", "said": [], "asks": []})
    r = game.submit("I read the mud.")
    assert r.pause is not None and r.pause.kind == "offer"
    model.push(DM, {"calls": [], "passage": "Nothing.", "said": [], "asks": []},
               {"calls": [], "passage": "Nothing.", "said": [], "asks": []})
    r = game.answer("commit")  # used to raise AttributeError in costs._apply
    if r.pause is not None:
        r = game.answer("failure")
    assert r.pause is None
    assert any(e.type == "frame_resolved" for e in game.store.events())


# ------------------------------------------------------------------------------------------- 2. a thing in words


@pytest.mark.parametrize("degree", ["success", "critical_success"])
def test_taking_a_thing_named_only_in_words_makes_it_and_holds_it(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                                                                  degree: str) -> None:
    game, model = to_play(tmp_path)
    pc = pc_id(game.store.state) or ""
    monkeypatch.setattr(pl, "roll_check", fixed(degree))
    call = {**BASE, "verb": "verb.handle", "target": "the leather satchel", "as": "thing", "change_kind": "take",
            "change_what": "the satchel", "stakes": "risky", "attribute": "agility", "difficulty": "moderate",
            "why_uncertain": "it is wedged under the bench"}
    model.push(DM, {"calls": [call], "passage": "Lead-up.", "said": [], "asks": []})
    assert game.submit("I grab the satchel.").pause is not None
    model.push(DM, {"calls": [], "passage": "Result.", "said": [], "asks": []},
               {"calls": [], "passage": "Result.", "said": [], "asks": []})
    r = game.answer("commit")
    st = game.store.state
    made = [i for i, e in st.entities.items() if e.kind == "item" and e.name == "the satchel"]
    assert len(made) == 1 and st.fact_value(made[0], "holder") == pc
    assert not any("Not applied" in b.text for b in r.oof_blocks), [b.text for b in r.oof_blocks]


def test_giving_a_thing_named_only_in_words_makes_it_and_hands_it_over(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    game, model = to_play(tmp_path)
    npc = npc_here(game)
    monkeypatch.setattr(pl, "roll_check", fixed("success"))
    call = {**BASE, "verb": "verb.persuade", "target": npc, "change_kind": "give", "change_what": "a folded letter",
            "change_whom": npc, "stakes": "risky", "attribute": "presence", "difficulty": "moderate",
            "why_uncertain": "she is wary"}
    model.push(DM, {"calls": [call], "passage": "Lead-up.", "said": [], "asks": []})
    assert game.submit("I hand her the letter.").pause is not None
    model.push(DM, {"calls": [], "passage": "Result.", "said": [], "asks": []},
               {"calls": [], "passage": "Result.", "said": [], "asks": []})
    r = game.answer("commit")
    st = game.store.state
    made = [i for i, e in st.entities.items() if e.kind == "item" and e.name == "a folded letter"]
    assert len(made) == 1 and st.fact_value(made[0], "holder") == npc
    assert not any("Not applied" in b.text for b in r.oof_blocks), [b.text for b in r.oof_blocks]


# ------------------------------------------------------------------------------------------- 3. no silent foe acts


class _Die:
    """The game's rng, except the foe's own attack die is fixed."""

    def __init__(self, rng: Any, natural: int) -> None:
        self._rng, self._natural = rng, natural

    def d(self, n: int, why: str = "") -> int:
        return self._natural if why.startswith("foe ") else int(self._rng.d(n, why))

    def __getattr__(self, name: str) -> Any:
        return getattr(self._rng, name)


def _foe_act(tmp_path: Path, pick: str, band: str, natural: int = 10) -> tuple[list[dict[str, str]], Any, Any]:
    from engine.dm import world_step as ws
    from engine.resolve import conflict, foe_act

    game, _ = to_play(tmp_path)
    foe = start_fight(game)
    oof: list[dict[str, str]] = []
    done: list[Any] = []

    def go(ctx: Any, t: Any, tx: Any) -> None:
        pc = pc_id(tx.state) or ""
        conflict._set_band(tx, pc, foe, band, "test")

        def do(tc: Any, rng: Any, f: str, who: str) -> Any:
            done.append(foe_act.act(tc, _Die(rng, natural), f, pick, who))
            return done[-1]

        ws._foe_turn(ctx, t.rec, foe, oof, do=do, ref=f"dm:{pick}")

    in_turn(game, go)
    return oof, done[0], _name(game.store.state, foe)


@pytest.mark.parametrize(("pick", "band", "natural", "want"), [
    ("strike", "engaged", 1, "strikes at you and misses"),
    ("grapple", "engaged", 1, "grabs at you and misses"),
    ("close_in", "near", 10, "moves toward you"),
    ("withdraw", "engaged", 10, "pulls back from you"),
    ("wait", "near", 10, "holds back, watching"),
    ("flee", "near", 10, "turns and flees the scene"),
    ("yield", "near", 10, "throws down its guard and yields"),
])
def test_every_foe_act_shows_one_result_line_in_words(tmp_path: Path, pick: str, band: str, natural: int, want: str) -> None:
    oof, done, name = _foe_act(tmp_path, pick, band, natural)
    lines = [b["text"] for b in oof if b["kind"] == "RESULT"]
    assert lines == [f"[RESULT] {name} {want}"], lines
    assert "d20" not in lines[0] and not any(ch.isdigit() for ch in lines[0])  # no dice numbers (the owner decides)
    assert done.pick == pick


def test_a_closing_in_to_arms_reach_is_shown(tmp_path: Path) -> None:
    oof, _, name = _foe_act(tmp_path, "close_in", "close")
    assert [b["text"] for b in oof] == [f"[RESULT] {name} closes in, now at arm's reach of you"]


def test_a_landed_strike_keeps_its_hit_line_without_numbers_of_the_roll(tmp_path: Path) -> None:
    oof, done, name = _foe_act(tmp_path, "strike", "engaged", 20)
    text = oof[0]["text"]
    assert text.startswith(f"[RESULT] {name} strikes you · hit · Changed:") and "d20" not in text
    assert done.harm is not None


@pytest.mark.parametrize("pick", ["strike", "grapple"])
def test_the_foe_roll_is_returned_and_one_flag_shows_it(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, pick: str) -> None:
    from engine.dm import world_step as ws

    oof, done, _ = _foe_act(tmp_path, pick, "engaged", 1)
    assert set(done.roll or {}) == {"d20", "total", "guard"} and done.roll["d20"] == 1  # type: ignore[index]
    assert done.roll["total"] > 1 and done.roll["guard"] > 0  # type: ignore[index]
    assert "d20" not in oof[0]["text"]
    monkeypatch.setattr(ws, "SHOW_FOE_ROLL", True)
    oof2, done2, _ = _foe_act(tmp_path / "again", pick, "engaged", 1)
    r = done2.roll
    assert oof2[0]["text"].endswith(f" · d20 {r['d20']} → {r['total']} vs {r['guard']}")
