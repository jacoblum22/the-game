"""The terminal front end (T074, T075) over a fake game that implements contracts/engine-api.md."""

from __future__ import annotations

import io
import os
from pathlib import Path
from typing import Any

import pytest

from engine.dm.codex import CodexView
from engine.dm.response import Choice, OofBlock, Pause, Response
from engine.llm.base import MissingKey, ModelUnavailable
from engine.store.events import Event
from engine.store.records import Part, TurnRecord
from play import cli
from play.report import replay, turn_lines
from tests.fixtures.game import entity, new_store

OFFER_CHOICES = [Choice(id="commit", label="Commit"), Choice(id="change", label="Change approach"),
                 Choice(id="withdraw", label="Withdraw")]


class FakeGame:
    """The game API, scripted: each submit/answer pops the next response (or raises it)."""

    script: list[Any] = []
    opened: list[tuple[str, Path, Any]] = []
    new_error: Exception | None = None

    def __init__(self, path: Path) -> None:
        self.path = path
        self.calls: list[tuple[str, Any]] = []
        self.prefs: dict[str, Any] = {}
        FakeGame.last = self

    @classmethod
    def new(cls, path: Path, config: Any, seed: int | None = None) -> tuple[FakeGame, Response]:
        if cls.new_error is not None:
            raise cls.new_error
        Path(path).touch()
        cls.opened.append(("new", Path(path), config))
        return cls(path), Response(phase="seed", oof_blocks=[OofBlock(kind="SEED", text="[SEED 1/14] Pick a seed.")],
                                   pause=Pause(kind="seed_step", choices=[Choice(id="mixed", label="Mixed")]))

    @classmethod
    def open(cls, path: Path, config: Any) -> tuple[FakeGame, Response]:
        cls.opened.append(("open", Path(path), config))
        return cls(path), Response(phase="play", oof_blocks=[OofBlock(kind="RECAP", text="[RECAP] Last time...")])

    @classmethod
    def replay(cls, path: Path, until_seq: int | None = None) -> Any:
        return cls.script.pop(0)

    def _next(self) -> Response:
        item = self.script.pop(0)
        if isinstance(item, Exception):
            raise item
        return item

    def submit(self, text: str) -> Response:
        self.calls.append(("submit", text))
        return self._next()

    def answer(self, choice_id: str) -> Response:
        self.calls.append(("answer", choice_id))
        return self._next()

    def codex(self, section: str | None = None) -> CodexView:
        self.calls.append(("codex", section))
        return CodexView(section=section or "sheet", text=f"[{(section or 'sheet').upper()}] Wren, a courier.")

    def new_character(self) -> Response:
        self.calls.append(("new_character", None))
        return self._next()

    def turn_record(self, turn_id: str) -> TurnRecord | None:
        self.calls.append(("turn_record", turn_id))
        return TurnRecord(turn_id=turn_id, input_verbatim="I climb", parts=[Part.model_validate({"text": "I climb", "class": "DECLARATION"})])

    def branch(self, label: str) -> str:
        return f"branch.{label}"

    def spend(self) -> dict[str, float | None]:
        return {"turn_usd": 0.001, "session_usd": 0.01, "game_usd": 0.5, "budget_usd": 2.0}

    def set_pref(self, key: str, value: Any) -> None:
        self.prefs[key] = value

    def close(self) -> None:
        self.calls.append(("close", None))


def play_resp(fiction: str, turn: str, **kw: Any) -> Response:
    return Response(turn_id=turn, phase="play", fiction=fiction, **kw)


def offer(turn: str, **kw: Any) -> Response:
    text = "[OFFER] Climb the rail.\n  " + "   ".join(f"{i}) {c.label}" for i, c in enumerate(OFFER_CHOICES, 1))
    return play_resp("The barge slides past below.", turn, oof_blocks=[OofBlock(kind="OFFER", text=text)],
                     pause=Pause(kind="offer", choices=OFFER_CHOICES), **kw)


@pytest.fixture(autouse=True)
def _reset() -> None:
    FakeGame.script, FakeGame.opened, FakeGame.new_error = [], [], None


def run(argv: list[str], stdin: str, saves: Path) -> tuple[int, str]:
    out = io.StringIO()
    code = cli.main(argv, stdin=io.StringIO(stdin), stdout=out, saves=saves, game_cls=FakeGame,
                    config=lambda offline: {"offline": offline})
    return code, out.getvalue()


def test_menu_new_game_two_turns_choice_sheet_quit(tmp_path: Path) -> None:
    FakeGame.script = [play_resp("The rain eases.", "turn.1"), offer("turn.2"),
                       play_resp("You land hard but whole.", "turn.3")]
    code, out = run([], "1\nThe Salt Road\n1\nI climb the rail\n1\n/sheet\n/quit\n", tmp_path)
    assert code == 0
    assert "THE GAME" in out and "1) New game" in out and "Continue (no saved games yet)" in out
    assert FakeGame.opened[0][:2] == ("new", tmp_path / "The Salt Road.db")
    # "1" at the seed step is a pick, the text is a submit, "1" at the offer picks commit
    assert FakeGame.last.calls[:4] == [("answer", "mixed"), ("submit", "I climb the rail"), ("answer", "commit"),
                                       ("codex", "sheet")]
    assert FakeGame.last.calls[-1] == ("close", None)
    # fiction first, then the OFFER block; its listed choices are not printed twice
    assert out.index("The barge slides past") < out.index("[OFFER]")
    assert out.count("1) Commit") == 1
    assert "You land hard but whole." in out and "[SHEET] Wren" in out and "Saved." in out


def test_continue_picks_latest_save_and_menu_shows_it(tmp_path: Path) -> None:
    old = new_store(tmp_path, name="Old Road.db")
    old.close()
    latest = new_store(tmp_path, name="Salt Road.db")
    with latest.transaction(latest.new_turn_id()) as tx:
        tx.add(entity("pc", "Wren", tx=tx))
    latest.save_turn(TurnRecord(turn_id="turn.1", input_verbatim="hello"))
    latest.close()
    os.utime(tmp_path / "Old Road.db", (1_000_000, 1_000_000))
    code, out = run(["continue"], "/quit\n", tmp_path)
    assert code == 0 and FakeGame.opened[0][:2] == ("open", tmp_path / "Salt Road.db")
    assert "[RECAP]" in out
    code, out = run([], "5\n", tmp_path)
    assert '2) Continue: "Salt Road" (Wren, turn 1, last played' in out
    code, _ = run(["continue", "old road"], "/quit\n", tmp_path)  # by name, any case
    assert FakeGame.opened[-1][1] == tmp_path / "Old Road.db"


def test_budget_prompt_waits_for_the_turn_to_end(tmp_path: Path) -> None:
    FakeGame.script = [play_resp("Quiet.", "turn.1"), offer("turn.2", budget_notice="You have passed $2.00."),
                       play_resp("Done.", "turn.2")]
    code, out = run(["new", "g"], "look\nclimb\n1\n2\n", tmp_path)
    assert code == 0
    before, after = out.split("Done.", 1)
    assert "Keep playing?" not in before  # not at the offer: mid-turn
    assert "You have passed $2.00." in after and "Keep playing? 1) Yes 2) Stop here" in after
    assert "Saved." in after and FakeGame.script == []


def test_budget_prompt_yes_keeps_playing(tmp_path: Path) -> None:
    FakeGame.script = [play_resp("A.", "turn.1", budget_notice="Over budget."), play_resp("B.", "turn.2")]
    _, out = run(["new", "g"], "x\n1\ny\n/quit\n", tmp_path)
    assert out.count("Keep playing?") == 1 and "B." in out


def test_missing_key_explains_env_and_offline(tmp_path: Path) -> None:
    FakeGame.new_error = MissingKey("no key")
    code, out = run(["new", "g"], "", tmp_path)
    assert code == 2
    assert ".env" in out and "GEMINI_API_KEY=" in out and "--offline" in out


def test_model_unavailable_keeps_the_loop(tmp_path: Path) -> None:
    FakeGame.script = [ModelUnavailable("timeout"), play_resp("It works now.", "turn.1")]
    _, out = run(["new", "g"], "go\ngo\n/quit\n", tmp_path)
    assert "unavailable" in out and "message is kept" in out and "It works now." in out


def test_slash_commands_never_submit(tmp_path: Path) -> None:
    FakeGame.script = [play_resp("Fixed.", "turn.2")]
    stdin = ("/budget 3.5\n/budget off\n/autocommit on\n/spend\n/turn 1\n/rules 01.7.1\n/branch dock\n/help\n"
             "/bogus\n/fix the guard was dead\n/quit\n")
    _, out = run(["--offline", "new", "g"], stdin, tmp_path)
    g = FakeGame.last
    assert FakeGame.opened[0][2] == {"offline": True}
    assert g.prefs == {"budget_usd": None, "autocommit": True}
    assert ("turn_record", "turn.1") in g.calls and ("codex", "rules 01.7.1") in g.calls
    assert [c for c in g.calls if c[0] == "submit"] == [("submit", "(Out of character: I dispute this - the guard "
                                                                   "was dead)")]
    assert "this game $0.5000" in out and "branch.dock" in out and "Unknown command /bogus" in out
    assert "Classes: DECLARATION" in out


def test_eof_saves_and_exits(tmp_path: Path) -> None:
    code, out = run(["new", "g"], "", tmp_path)
    assert code == 0 and "Saved." in out and FakeGame.last.calls == [("close", None)]


def test_report_over_a_small_store(tmp_path: Path) -> None:
    store = new_store(tmp_path, name="r.db")
    with store.transaction("turn.1") as tx:
        tx.add(Event.of("frame_committed", source="test", rule_id="00.13.2", frame_id="frame.1",
                        frame={"gate": {"class": "G2"}}))
        tx.add(Event.of("frame_resolved", source="test", rule_id="00.13.2", frame_id="frame.1", degree="success"))
    store.save_turn(TurnRecord(turn_id="turn.1", input_verbatim="climb",
                               parts=[Part.model_validate({"text": "climb", "class": "DECLARATION"})],
                               verdicts=[{"claim": 0, "verdict": "supported"}], latency_ms=900))
    store.save_turn(TurnRecord(turn_id="turn.2", input_verbatim="hi", parts=[Part.model_validate({"text": "hi", "class": "SPEECH"})],
                               fallback_used=True, latency_ms=300))
    for i, (turn, cost) in enumerate([("turn.1", 0.002), ("turn.1", 0.001), ("turn.2", 0.004)]):
        store.record_model_call({"call_id": f"call.{i}", "turn_id": turn, "role": "narrator", "outcome": "ok",
                                 "cost_usd": cost, "latency_ms": 100})
    lines = turn_lines(store)
    store.close()
    assert [(ln.turn_id, ln.classes, ln.gates, ln.degrees, ln.calls) for ln in lines] == [
        ("turn.1", ["DECLARATION"], ["G2"], ["success"], 2), ("turn.2", ["SPEECH"], [], [], 1)]
    assert lines[0].cost_usd == pytest.approx(0.003)
    code, out = run(["report", "r"], "", tmp_path)
    assert code == 0
    assert "supportedx1" in out and "fallback rate 50.0%" in out and "median cost $0.0035" in out
    assert "median latency 600 ms" in out and "Model calls: 3 (okx3)" in out


def test_replay_identical_and_divergent(tmp_path: Path) -> None:
    class Result:
        def __init__(self, divergence: str | None) -> None:
            self.identical, self.divergence = divergence is None, divergence

    lines: list[str] = []
    FakeGame.script = [Result(None), Result("seq 41: fact_set differs")]
    assert replay(tmp_path / "g.db", lines.append, FakeGame) == 0
    assert replay(tmp_path / "g.db", lines.append, FakeGame) == 1
    assert "identical" in lines[0] and "seq 41" in lines[1]


def test_letter_picks_and_a_number_with_nothing_to_pick(tmp_path: Path) -> None:
    FakeGame.script = [play_resp("Begun.", "turn.0"), offer("turn.1"), play_resp("You land.", "turn.2")]
    _, out = run(["new", "g"], "a\nI climb\nb\n3\n/quit\n", tmp_path)
    # "a" picks the seed step's first option; "b" picks the offer's second; "3" with no pause open is not sent
    assert FakeGame.last.calls[:3] == [("answer", "mixed"), ("submit", "I climb"), ("answer", "change")]
    assert "Nothing to pick by number here" in out and ("submit", "3") not in FakeGame.last.calls
    assert out.count("1) Commit") == 1 and "  1) Commit\n  2) Change approach\n  3) Withdraw" in out
