"""The game clock and timers: change_time, and fights and rests moving the clock by themselves."""
import asyncio
import json
from pathlib import Path

from dm import mechanics as m
from dm import play

CHAR = Path(__file__).parent.parent / "dm" / "characters"


def game(tmp_path: Path) -> tuple[play.Game, object]:
    g = play.Game({"sheet": json.loads((CHAR / "fighter.json").read_text(encoding="utf-8"))}, tmp_path / "save.json")
    tools = {t.name: t.handler for t in g.tools()}

    def call(name: str, **args: object) -> tuple[str, bool]:
        res = asyncio.run(tools[name](args))
        return res["content"][0]["text"], bool(res.get("is_error"))
    return g, call


def test_text() -> None:
    assert m.when(17 * 3600 + 40 * 60) == "Day 1, 5:40 PM"
    assert m.when(m.DAY + 6) == "Day 2, 12:00:06 AM"
    assert m.when(12 * 3600) == "Day 1, 12:00 PM"
    assert m.span(3600 + 90) == "1 hour 1 minute 30 seconds"
    c = {"now": 1000, "timers": {"Torch": 1600, "Bless": 1000, "Old torch": 400}}
    assert m.clock_text(c).splitlines()[1] == ("Timers: Torch: 10 minutes left; Bless: ends now; "
                                               "Old torch: ran out 10 minutes ago")
    assert m.clock_text(m.new_clock()) == "Time: not set (set it with change_time)"


def test_change_time(tmp_path: Path) -> None:
    g, call = game(tmp_path)
    assert call("change_time", advance={"minutes": 5}) == ("REFUSED, nothing changed: the time isn't set yet: set it first", True)
    assert call("change_time", set={"day": 1, "time": "16:30"}) == ("time set: Day 1, 4:30 PM", False)
    assert call("change_time", add_timer={"name": "Torch", "hours": 1})[0] == "timer Torch: 1 hour"
    assert call("change_time", add_timer={"name": "Torch", "minutes": 1})[1]  # a name is used once
    assert call("change_time", advance={"minutes": 75})[0] == "1 hour 15 minutes later: Day 1, 5:45 PM"
    assert "Timers: Torch: ran out 15 minutes ago" in g.status()  # stays until the DM removes it
    call("change_time", set={"time": "17:00"})  # a correction keeps the timer's time left
    assert "Time: Day 1, 5:00 PM\nTimers: Torch: ran out 15 minutes ago" in g.status()
    assert call("change_time", remove_timer="Torch")[0] == "timer Torch removed"
    assert "Timers" not in g.status()
    assert call("change_time", set={"time": "25:00"})[1]
    assert json.loads((tmp_path / "save.json").read_text(encoding="utf-8"))["clock"] == g.clock


def test_fight_and_rests_move_it(tmp_path: Path) -> None:
    g, call = game(tmp_path)
    call("change_time", set={"time": "10:00"})
    call("add_combatants", combatants=[{"name": "pc", "initiative": 10}, {"name": "Zombie", "initiative": 5, "hp": 22, "ac": 8}])
    for _ in range(6):  # three rounds of two turns
        call("next_turn")
    assert g.clock["now"] == 10 * 3600 + 12
    text, _ = call("end_fight")
    assert text.endswith("18 seconds of fighting; now Day 1, 10:00:18 AM.")
    g.sheet["hp"]["current"] = 1
    assert "1 hour later: Day 1, 11:00:18 AM" in call("change_pc", short_rest=True)[0]
    assert "8 hours later: Day 1, 7:00:18 PM" in call("change_pc", long_rest=True)[0]
    call("change_time", advance={"hours": 15})  # the next would finish 23 hours after the last: refused
    text, err = call("change_pc", long_rest=True)
    assert err and "the next can finish Day 2, 7:00:18 PM at the earliest" in text and g.clock["now"] == 34 * 3600 + 18
    call("change_time", advance={"hours": 1})
    assert "8 hours later: Day 2, 7:00:18 PM" in call("change_pc", long_rest=True)[0]


def test_unset_clock_stays_unset(tmp_path: Path) -> None:
    g, call = game(tmp_path)
    call("change_pc", short_rest=True)
    assert g.clock["now"] is None
