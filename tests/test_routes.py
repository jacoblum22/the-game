"""Places and routes (dm/routes.py): SRD travel, the route records and their checks, travel, and the warnings."""
import asyncio
import json
from pathlib import Path

import pytest

from dm import lore as notebook
from dm import mechanics as m
from dm import names, play, routes

CHAR = Path(__file__).parent.parent / "dm" / "characters"


def call(tool: str, **a: object) -> dict:
    return {"kind": "call", "tool": tool, "input": a, "result": "", "error": False}


def player() -> dict:
    return {"kind": "player", "text": "x"}


def dm(text: str) -> dict:
    return {"kind": "dm", "text": text}


def places(*names_: str) -> dict:
    lore = notebook.new()
    for n in names_:
        lore, _ = notebook.write(lore, {"create": n, "kind": "place", "description": "x"}, 0)
    return lore


def test_srd_travel_pace() -> None:
    assert routes.miles({"hours": 2}, {}) == 6  # normal pace, 3 miles an hour
    assert routes.miles({"days": 1}, {}) == 24  # 8 hours a day
    assert routes.miles({"days": 1}, {"pace": "slow"}) == 16 and routes.miles({"days": 1}, {"pace": "fast"}) == 32
    assert routes.miles({"hours": 2}, {"by": "horse"}) == 6  # riding goes at the same pace
    assert routes.miles({"hours": 2}, {"difficult": True}) == 3  # difficult terrain: half as far
    assert routes.miles({"hours": 2}, {"by": "boat"}) == 3  # a rowboat, 1.5 mph
    assert routes.miles({"hours": 2}, {"by": "boat", "downstream": True}) == 9  # plus the current, 3 mph
    assert routes.miles({"hours": 2}, {"by": "boat", "vessel": "galley"}) == 8
    assert routes.miles({"hours": 1}, {"by": "horse", "pace": "gallop"}) == 8
    assert routes.miles({"miles": 5}, {"by": "boat"}) == 5 and routes.miles({}, {}) is None
    with pytest.raises(m.Refused):
        routes.miles({"hours": 1}, {"pace": "gallop"})
    with pytest.raises(m.Refused):
        routes.miles({"hours": 1, "miles": 3}, {})


def test_a_road_adds_up_its_legs_and_fills_a_missing_one() -> None:
    t = [call("route", stops=["Greywater", "Millstone Inn", "Ford Chapel"], legs=[{"hours": 2}, {}], total={"hours": 3})]
    at = routes.Atlas(places("Greywater", "Millstone Inn", "Ford Chapel"), t)
    assert at.path("Greywater", "Ford Chapel") == (9, [])  # the road gives every pair along it
    assert at.path("Millstone Inn", "Ford Chapel")[0] == 3
    assert at.flags == []


def test_along_the_same_pair_off_by_more_than_a_quarter() -> None:
    t = [call("route", stops=["Greywater", "the Ford Chapel"], legs=[{"hours": 3}]), player(), player(),
         call("route", stops=["Ford Chapel", "Greywater"], legs=[{"hours": 2}])]
    at = routes.Atlas(places("Greywater", "Ford Chapel"), t)
    assert at.flags == [("turn 2: Ford Chapel - Greywater", "Ford Chapel to Greywater: 6 miles (turn 2), but 9 miles on turn 0.")]


def test_fit_and_the_compass() -> None:
    lore = places("Harrowmere", "the Throat", "Greyshaft")
    t = [call("route", stops=["Harrowmere", "the Throat"], legs=[{"miles": 30}], direction="north"),
         call("route", stops=["the Throat", "Greyshaft"], legs=[{"miles": 70}], direction="north-east")]
    # without the compass anything from 40 to 100 miles fits; on the way, it must be at least 70
    at = routes.Atlas(lore, t + [call("route", stops=["Harrowmere", "Greyshaft"], legs=[{"days": 3}], pace="slow")])
    assert len(at.flags) == 1 and "the compass puts the Throat on the way, so it should be 70 to 100 miles" in at.flags[0][1]
    t[0]["input"].pop("direction")
    assert routes.Atlas(lore, t + [call("route", stops=["Harrowmere", "Greyshaft"], legs=[{"days": 3}], pace="slow")]).flags == []
    assert "should be 40 to 100" in routes.Atlas(lore, t + [call("route", stops=["Harrowmere", "Greyshaft"],
                                                                 legs=[{"miles": 20}])]).flags[0][1]


def test_links_join_places_and_water_is_its_own_way() -> None:
    lore = places("Greyshaft", "Greyshaft lowest gate", "Saltmarsh")
    t = [call("route", stops=["Greyshaft", "Saltmarsh"], legs=[{"days": 2}]),
         call("route", links=[{"a": "Greyshaft lowest gate", "b": "Greyshaft", "how": "inside"}]),
         call("route", stops=["Greyshaft lowest gate", "Saltmarsh"], legs=[{"hours": 4}], by="boat")]
    at = routes.Atlas(lore, t)
    assert at.path("Greyshaft lowest gate", "Saltmarsh")[0] == 48 and at.path("Saltmarsh", "Greyshaft", routes.WATER)[0] == 6
    assert at.flags == []  # the boat and the road are different ways


def test_asking_how_far_without_moving() -> None:
    lore = places("Greywater", "Ford Chapel")
    assert "No route from Greywater to Ford Chapel" in routes.ask(lore, [], {"from": "Greywater", "to": "Ford Chapel"})
    t = [call("route", stops=["Greywater", "Ford Chapel"], legs=[{"miles": 6}]), call("place", place="Greywater")]
    assert routes.ask(lore, t, {"to": "Ford Chapel"}) == ("Greywater to Ford Chapel: 6 miles by land: on foot or riding, "
                                                         "slow pace 3 hours, normal pace 2 hours, fast pace 1 hour 30 minutes.")


def test_journey_days_nights_and_forced_march() -> None:
    lore = places("Greywater", "Saltmarsh")
    t = [call("route", stops=["Greywater", "Saltmarsh"], legs=[{"miles": 30}]), call("place", place="Greywater")]
    a, sec, text = routes.journey(lore, t, {"to": "Saltmarsh"})
    assert a["from"] == "Greywater" and sec == (10 + 16) * 3600  # 10 hours: 8, the night, then 2 more
    assert text.startswith("Greywater to Saltmarsh: 30 miles, on foot at a normal pace: 10 hours of travel over 2 days")
    a, sec, text = routes.journey(lore, t, {"to": "Saltmarsh", "forced_march": True})
    assert sec == 10 * 3600 and "DC 11, 12" in text
    with pytest.raises(m.Refused):
        routes.journey(places("Greywater", "Hollin Mill"), t, {"to": "Hollin Mill"})
    a, sec, _ = routes.journey(lore, [call("place", place="Greywater")], {"to": "Saltmarsh", "hours": 4})
    assert sec == 4 * 3600 and routes.Atlas(lore, [call("travel", **a)]).path("Greywater", "Saltmarsh")[0] == 12


def test_travel_and_the_place_field_in_the_game(tmp_path: Path) -> None:
    g = play.Game({"sheet": json.loads((CHAR / "fighter.json").read_text(encoding="utf-8"))}, tmp_path / "save.json")
    g.lore = places("Greywater", "Saltmarsh")
    tools = {t.name: t.handler for t in g.tools()}
    run = lambda name, **a: asyncio.run(tools[name](a))  # noqa: E731
    run("change_time", set={"day": 1, "time": "08:00"})
    run("reply", text="You stand at the gate.", place="Greywater")
    assert routes.here(g.transcript) == "Greywater"
    res = run("travel", to="Saltmarsh", hours=4)
    assert not res.get("is_error") and m.when(g.clock["now"]) == "Day 1, 12:00 PM"
    assert routes.here(g.transcript) == "Saltmarsh" and g.transcript[-1]["text"].startswith("travel: Greywater to Saltmarsh")
    assert {"route", "travel", "dismiss_warning"} <= play.BOOKKEEPING


def test_warnings_moves_and_places_not_in_the_notebook() -> None:
    lore = places("Greywater", "Saltmarsh")
    t = [call("place", place="Greywater"), player(), call("place", place="Saltmarsh"), player(),
         call("place", place="the Drowned Candle"), player()]
    w = routes.warning(lore, t)
    assert '"Greywater -> Saltmarsh" (turn 1)' in w and '"the Drowned Candle"' in w
    t.append(call("route", stops=["Greywater", "Saltmarsh"], legs=[{"days": 1}]))
    t.append(call("dismiss_warning", items=["the drowned candle", "Saltmarsh -> the Drowned Candle"]))
    assert routes.warning(lore, t) == ""


def test_warning_a_distance_with_no_route() -> None:
    lore = places("Greywater", "Millstone Inn")
    t = [call("place", place="Greywater"), dm("The Millstone Inn is two hours down the road. You were born ten years ago."),
         player()]
    w = routes.warning(lore, t)
    assert '"turn 0: Millstone Inn": "The Millstone Inn is two hours down the road." (the party was at Greywater)' in w
    assert "ten years" not in w
    t.append(call("route", stops=["Greywater", "Millstone Inn"], legs=[{"hours": 2}]))
    assert routes.warning(lore, t) == ""


def test_warning_names_inside_names_and_new_places() -> None:
    lore = places("Greyshaft")
    t = [player(), call("write_lore", create="Greyshaft lowest gate", kind="place", description="x"), player()]
    lore, _ = notebook.write(lore, {"create": "Greyshaft lowest gate", "kind": "place", "description": "x"}, 1)
    w = routes.warning(lore, t)
    assert '"Greyshaft lowest gate / Greyshaft"' in w and "[New places]" in w and "Greyshaft lowest gate." in w
    assert "[New places]" not in routes.warning(lore, t + [player()])  # asked once
    t.append(call("route", links=[{"a": "Greyshaft lowest gate", "b": "Greyshaft", "how": "inside"}]))
    assert routes.warning(lore, t) == ""


def test_warning_routes_that_dont_fit() -> None:
    lore = places("Greywater", "Ford Chapel")
    t = [call("route", stops=["Greywater", "Ford Chapel"], legs=[{"hours": 3}]), player(),
         call("route", stops=["Greywater", "Ford Chapel"], legs=[{"hours": 1}]), player()]
    assert "[Routes that don't fit]" in routes.warning(lore, t)
    assert routes.warning(lore, t + [call("dismiss_warning", items=["turn 1: Ford Chapel - Greywater"])]) == ""


def test_names_count_only_whole_names_or_parts_of_peoples_names() -> None:
    lore = notebook.new()
    lore, _ = notebook.write(lore, {"create": "The Greyshaft Foreman", "kind": "person", "description": "x"}, 0)
    lore, _ = notebook.write(lore, {"create": "Wil Harrow", "kind": "person", "description": "x"}, 0)
    lore, _ = notebook.write(lore, {"create": "Ford Chapel", "kind": "place", "description": "x"}, 0)
    t = [dm("They ride for Greyshaft. Later, Wil Harrow and Wil reach the Ford Chapel, past the Ford.")]
    assert names.unknown(lore, t) == ["Greyshaft", "Ford"]


def test_a_correction_replaces_the_record_and_its_clash() -> None:
    lore = places("Greywater", "Ford Chapel")
    t = [call("route", stops=["Greywater", "Ford Chapel"], legs=[{"hours": 3}]), player(),
         call("route", stops=["Greywater", "Ford Chapel"], legs=[{"hours": 1}]), player()]
    assert routes.Atlas(lore, t).flags
    at = routes.Atlas(lore, t + [call("route", stops=["Greywater", "Ford Chapel"], legs=[{"hours": 1}], correct=True)])
    assert at.flags == [] and at.path("Greywater", "Ford Chapel")[0] == 3


def test_warning_a_distance_off_the_record_in_the_last_reply() -> None:
    lore = places("Greywater", "Millstone Inn")
    t = [call("route", stops=["Greywater", "Millstone Inn"], legs=[{"hours": 2}]), call("place", place="Greywater"),
         player(), dm("The Millstone Inn is a day and a half down the road."), player()]
    w = routes.warning(lore, t)
    assert ('if that is Millstone Inn to Greywater, the recorded route is 6 miles (2 hours on foot), and "a day and a '
            'half down" is about 36 miles at a normal pace') in w
    assert "Distances off the records" not in routes.warning(lore, t + [player()])  # asked once
    t[3] = dm("The Millstone Inn is two hours down the road.")
    assert routes.warning(lore, t) == ""
    assert routes.stated_miles("three days' march") == 72 and routes.stated_miles("a hard night's march") == 24


def test_routes_for_the_checker() -> None:
    lore = places("Harrowmere", "the Throat", "Greyshaft", "Saltmarsh", "Cinder Ford")
    t = [call("route", stops=["Harrowmere", "the Throat"], legs=[{"miles": 30}], direction="north"),
         call("route", stops=["the Throat", "Greyshaft"], legs=[{"miles": 70}], direction="north-east"),
         call("route", stops=["Harrowmere", "Saltmarsh"], legs=[{"miles": 20}]),
         call("place", place="Harrowmere")]
    assert routes.for_checker(lore, t, "Greyshaft and the Throat lie north.") == [
        "- Greyshaft to Harrowmere: 100 miles by land (33 hours 20 minutes)",  # on the way, by the compass
        "- Greyshaft to the Throat: 70 miles by land (23 hours 20 minutes)",
        "- Harrowmere to the Throat: 30 miles by land (10 hours)"]
    assert routes.for_checker(lore, t, "Saltmarsh and the Throat.") == [
        "- Harrowmere to Saltmarsh: 20 miles by land (6 hours 40 minutes)",
        "- Harrowmere to the Throat: 30 miles by land (10 hours)",
        "- Saltmarsh to the Throat: no route recorded between these two, but the routes recorded put them between 10 "
        "and 50 miles apart by land"]
    # a route with an open clash over it is left out
    t.append(call("route", stops=["Harrowmere", "Saltmarsh"], legs=[{"miles": 60}]))
    assert routes.for_checker(lore, t, "Saltmarsh.") == []
    assert routes.for_checker(lore, t, "Cinder Ford.") == []
