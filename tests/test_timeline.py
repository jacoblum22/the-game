"""Dates and the timeline (dm/timeline.py): the calendar on the clock, time facts recorded with `timeline`, the warning
that prompts them, and the clock and facts the continuity checker reads."""
from pathlib import Path

from test_clock import game

from dm import check, timeline
from dm import mechanics as m


def test_calendar_names_the_days(tmp_path: Path) -> None:
    g, call = game(tmp_path)
    assert call("change_time", date={"day": 3, "month": "Harvest", "year": 1492})[1]  # the time comes first
    text, err = call("change_time", set={"day": 4, "time": "08:20"}, date={"day": 3, "month": "Harvest", "year": 1492})
    assert not err and text == "time set: Day 4, 8:20 AM; today is the 3rd of Harvest, 1492"
    assert g.status().startswith("Time: Day 4 (the 3rd of Harvest, 1492), 8:20 AM")
    call("change_time", advance={"days": 28})
    assert g.status().startswith("Time: Day 32 (the 1st of Leaffall, 1492), 8:20 AM")  # months of 30 days
    assert m.date_text(g.clock, 1) == "the 30th of Haying, 1492"
    assert call("change_time", date={"day": 31, "month": "Harvest", "year": 1492})[1]
    assert call("change_time", date={"day": 1, "month": "Brumaire", "year": 1492})[1]


def test_no_date_set_shows_the_day_only(tmp_path: Path) -> None:
    g, call = game(tmp_path)
    call("change_time", set={"day": 2, "time": "17:40"})
    assert g.status().startswith("Time: Day 2, 5:40 PM")


def test_facts_are_turned_into_days_and_summed(tmp_path: Path) -> None:
    g, call = game(tmp_path)
    call("change_time", set={"day": 16, "time": "22:00"}, date={"day": 16, "month": "Thaw", "year": 1492})
    assert call("timeline", what="Korvash swore his oath", names=["Korvash"], day=2)[0] == \
        "recorded: Korvash swore his oath (Day 2, the 2nd of Thaw, 1492; 14 days ago)"
    assert call("timeline", what="the assize", names=["Dame Crowe"], date={"day": 30})[0] == \
        "recorded: the assize (Day 30, the 30th of Thaw, 1492; in 14 days)"
    assert call("timeline", what="Tobin came to the kitchens", names=["Tobin"], days_from_today=-1, time="noon")[0] == \
        "recorded: Tobin came to the kitchens (Day 15, the 15th of Thaw, 1492, noon; yesterday)"
    assert call("timeline", what="the light went dark", names=["Gullspit light"], years_ago=15)[0] == \
        "recorded: the light went dark (about 15 years ago)"
    assert call("timeline", what="Wren's age", names=["Wren"], age=19)[0] == "recorded: Wren's age (19 years old now)"
    rec = g.transcript[-1]
    assert rec["kind"] == "call" and rec["tool"] == "timeline" and rec["input"]["day"] == 16 - 19 * 360
    call("change_time", advance={"days": 400})  # a year and more on, the sums move with the clock
    assert call("timeline", find=["Wren", "the Gullspit light"])[0] == \
        "- the light went dark (about 16 years ago)\n- Wren's age (20 years old now)"
    assert "Nothing is recorded" in call("timeline", find=["Pell"])[0]


def test_bad_facts_are_refused(tmp_path: Path) -> None:
    g, call = game(tmp_path)
    assert "clock isn't set" in call("timeline", what="x", names=["Pell"], day=2)[0]
    call("change_time", set={"day": 3, "time": "09:00"})
    assert "one of day" in call("timeline", what="x", names=["Pell"])[0]
    assert "one of day" in call("timeline", what="x", names=["Pell"], day=2, years_ago=3)[0]
    assert "names" in call("timeline", what="x", day=2)[0]
    assert "no date is set" in call("timeline", what="x", names=["Pell"], date={"day": 30})[0]
    assert not any(e.get("tool") == "timeline" for e in g.transcript)


def turn_with(reply: str, *extra: dict) -> list[dict]:
    return [{"kind": "player", "text": "hello"}, {"kind": "clock", "why": "", "how": "set", "seconds": 0, "at": 15 * m.DAY + 36000},
            *extra, {"kind": "dm", "text": reply}, {"kind": "player", "text": "go on"}]


def test_the_warning_asks_for_time_facts_the_last_reply_stated() -> None:
    reply = ("It is ten in the morning on Day 16. Tessa has been gone for three nights. He is forty years old.\n\n"
             "The rain keeps on.")
    w = timeline.warning(turn_with(reply), set())
    assert w.startswith("[Time facts not on the timeline]")
    assert '- for three nights: "Tessa has been gone for three nights."' in w
    assert '- forty years old: "He is forty years old."' in w
    assert "Day 16" not in w  # today on the clock is not a fact
    assert timeline.warning(turn_with("The rain keeps on."), set()) == ""
    rec = {"kind": "call", "tool": "timeline", "input": {"what": "x", "names": ["Tessa"], "day": 13, "exact": True},
           "result": "", "error": False}
    assert timeline.warning(turn_with(reply, rec), set()) == ""  # the DM recorded what it wanted that turn
    gone = {"tessa has been gone for three nights.", "he is forty years old."}
    assert timeline.warning(turn_with(reply, rec | {"input": {}}), gone) == ""


def test_the_checker_reads_the_clock_and_the_facts_about_the_names_in_the_reply(tmp_path: Path) -> None:
    g, call = game(tmp_path)
    call("change_time", set={"day": 2, "time": "09:00"})
    g.transcript.append({"kind": "player", "text": "I swear it."})
    call("timeline", what="Korvash swore his oath to Gorrak", names=["Korvash", "Gorrak Vael"], day=2, time="9:00 AM")
    call("timeline", what="Korvash's father died", names=["Korvash", "Dargan"], years_ago=14)
    call("change_time", advance={"days": 14, "hours": 13})
    g.transcript.append({"kind": "player", "text": "I wait."})
    call("timeline", what="Korvash ate breakfast", names=["Korvash", "Gorrak Vael"], day=16, time="8 AM")
    call("timeline", what="the meeting at the stream", names=["Gorrak Vael"], day=16, time="dusk")
    call("timeline", what="Gorrak's answer due", names=["Gorrak Vael"], day=17, time="dawn")
    call("change_time", advance={"hours": 1})
    g.transcript.append({"kind": "player", "text": "What does Gorrak say?"})
    call("change_time", advance={"minutes": 10})
    state = check.context(g.lore, g.transcript, "Gorrak says: eleven days you have kept your word.",
                          party=("Korvash",), clock=g.clock)
    assert "TIME (the game clock when each earlier turn ended, and when the new reply is written)\n" \
           "Turn 0: Day 2, 9:00 AM\nTurn 1: Day 16, 10:00 PM\nTurn 2: Day 16, 11:00 PM\nNew reply: Day 16, 11:10 PM" in state
    facts = state.split("TIMELINE (the DM's recorded time facts about things the new reply names)\n")[1].split("\n\n")[0]
    # Gorrak by his own name word; not the father (only Korvash, the PC, links him); not today's breakfast or meeting,
    # gone by at 11:10 PM
    assert facts == ("- Korvash swore his oath to Gorrak (Day 2, 9:00 AM; 14 days ago)\n"
                     "- Gorrak's answer due (Day 17, dawn; tomorrow)")
    assert "TIMELINE" not in check.context(g.lore, g.transcript, "The rain keeps on.", party=("Korvash",), clock=g.clock)


def test_the_checker_is_told_about_time_only_when_it_gets_it() -> None:
    seen = []

    async def ask(backend: str, system: str, text: str) -> dict:
        seen.append((system, text))
        return {"problems": []}
    import asyncio
    asyncio.run(check.check("sdk", {"entries": {}}, [{"kind": "player", "text": "hi"}], "Hello.", ask))
    asyncio.run(check.check("sdk", {"entries": {}}, turn_with("x"), "Hello.", ask))
    assert "TIME gives" not in seen[0][0] and "TIME gives" in seen[1][0]
