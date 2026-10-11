"""Spec 032 P7.4: the held-out runner sets up all 24 scenes and scores them offline (no model call); the scorers are
checked on made-up logs. The offline verdicts are a harness check, never a measurement of the DM."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from evals import heldout_032 as h


def _run(iid: str, passage: str = "", *, tools: list[dict[str, str]] | None = None, foes: list[dict[str, Any]] | None = None,
         said: list[dict[str, str]] | None = None, **after: Any) -> dict[str, Any]:
    turn = {"input": "x", "passage": passage, "tools": tools or [], "refusals": [], "said": said or [],
            "told_dropped": [], "log_only": [], "foe_turns": foes or [], "paused": False}
    base = {"ents": {"Marek Voss": "npc.marek_voss", "Sill Orren": "npc.sill_orren", "Imre Cass": "npc.imre_cass"},
            "after": {"ents": {}, "fight_live": True, "pc_vit": 13, "down": [], **after}}
    return {"id": iid, "turns": [turn], **base}


def _item(iid: str) -> dict[str, Any]:
    return next(i for i in h.load_items() if i["id"] == iid)


def test_every_item_has_a_scene_and_a_scorer_and_the_offline_run_completes(tmp_path: Path) -> None:
    items = h.load_items()
    assert len(items) == 24 and set(h.SCENES) == {i["id"] for i in items}
    assert h.main(["--offline", "--out", str(tmp_path)]) == 0
    runs = __import__("json").loads((tmp_path / "heldout_offline.json").read_text(encoding="utf-8"))
    assert len(runs) == 24 and all(r["verdict"] in ("pass", "fail", "judge") for r in runs)
    assert not [r for r in runs if "ERROR" in r["note"]]  # every scene builds and every item runs


def test_scorers_on_made_up_logs() -> None:
    roll = {"tool": "propose_roll", "args": '{"verb": "verb.strike", "target": "the hound"}', "out": "ROLL OFFERED"}
    refused = {"tool": "propose_roll", "args": '{"verb": "verb.strike", "target": "the hound"}',
               "out": "REFUSED: no one or nothing on record called 'the hound'"}
    assert h.score(_item("H05"), _run("H05", tools=[{**roll, "args": '{"verb": "verb.grapple"}'}]))[0] == "pass"
    assert h.score(_item("H05"), _run("H05", tools=[refused]))[0] == "fail"
    assert h.score(_item("H07"), _run("H07", foes=[{"foe": "npc.marek_voss", "did": "strikes you"}]))[0] == "pass"
    assert h.score(_item("H07"), _run("H07"))[0] == "fail"  # no foe turn
    assert h.score(_item("H11"), _run("H11", fight_live=False))[0] == "pass"  # the fight ended: 0 foe turns
    assert h.score(_item("H12"), _run("H12", foes=[{"foe": "npc.marek_voss", "did": "x"}]))[0] == "fail"  # the downed foe
    assert h.score(_item("H22"), _run("H22", "Imre takes the letter. He nods."))[0] == "fail"
    assert h.score(_item("H22"), _run("H22", 'Imre takes the letter. She nods. "He sent it," she says.'))[0] == "pass"
    assert h.score(_item("H24"), _run("H24", "The heron lifts one leg. She stares."))[0] == "fail"
