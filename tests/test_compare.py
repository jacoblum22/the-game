"""The comparison runner (evals/compare/run.py) with a fake model: a new game, a player typing lines, the log of every
call and the cost sums. No model calls."""
import asyncio
import importlib.util
import json
from pathlib import Path
from typing import Any

from dm import check, model, play

SPEC = importlib.util.spec_from_file_location("compare_run", Path(__file__).parent.parent / "evals" / "compare" / "run.py")
assert SPEC and SPEC.loader
run = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(run)
WHOLE = ("You climb the wall, hand over hand, and pull yourself onto the ledge. " * 5).strip()


def test_a_short_game(monkeypatch: Any, tmp_path: Path) -> None:
    seen: list[tuple[str, str]] = []

    async def fake(request: dict[str, Any]) -> dict[str, Any]:
        player = request["system"].startswith("You are a human player")
        checker = request["system"].startswith(check.SYSTEM)
        seen.append(("player" if player else "check" if checker else "dm", request["model"]))
        text = "I look around the cavern." if player else '{"problems": []}' if checker else WHOLE
        return {"content": [{"type": "text", "text": text}], "stop_reason": "end_turn",
                "usage": {"input_tokens": 1000, "cache_read_input_tokens": 9000, "cache_creation_input_tokens": 0,
                          "output_tokens": 100}}
    monkeypatch.setattr(model, "send", fake)
    monkeypatch.setattr(play, "SAVES", tmp_path)
    monkeypatch.setattr(check, "ENABLED", True)
    res = asyncio.run(run.play_game("t", "zai/glm-5.3", 2, tmp_path))
    assert check.ENABLED is True  # the comparison runs the whole pipeline, the checker too
    # the opening (not checked), then twice: the player's line, the DM's reply, the checker's read of it
    assert [r for r, _ in seen] == ["dm", "player", "dm", "check", "player", "dm", "check"]
    assert {m for r, m in seen if r != "player"} == {"zai/glm-5.3"}  # the checker runs on the DM's model
    assert check.CHECK_MODEL == "claude-sonnet-5-5"  # and is put back
    assert res["rounds"] == 2 and res["totals"]["dm"]["calls"] == 3 and res["totals"]["player"]["calls"] == 2
    assert res["dm_calls_per_round_median"] == 1 and res["refused"] == 0 and res["failed"] == 0
    # 3 DM calls at Z.AI's prices: (1000 x $1.40 + 9000 x $0.26 + 100 x $4.40) per million each
    assert abs(res["totals"]["dm"]["usd"] - 3 * (1400 + 2340 + 440) / 1e6) < 1e-9
    assert "round 2, the player: I look around the cavern." in (tmp_path / "t.log").read_text(encoding="utf-8")
    assert len((tmp_path / "t.calls.jsonl").read_text(encoding="utf-8").splitlines()) == 7
    assert json.loads((tmp_path / "t.metrics.json").read_text(encoding="utf-8"))["summary"]["model"] == "zai/glm-5.3"
    assert model.send is fake  # put back as it was
