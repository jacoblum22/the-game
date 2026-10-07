"""evals/gemini_smoke.py with fake clients only: argument parsing and request building; never a network call."""

from __future__ import annotations

import json
from typing import Any

import pytest
from google.genai import types

from engine.llm import gemini
from engine.llm.base import Role, RoleModel
from engine.llm.gemini import GeminiModel
from engine.llm.gemini_schema import to_gemini
from engine.llm.offline import OfflineModel
from evals import gemini_smoke as smoke


class FakeModels:
    """Answers each request with the offline model's (schema-valid) answer for that role, as JSON text."""

    def __init__(self, bad_role: str | None = None):
        self.calls: list[dict[str, Any]] = []
        self.bad_role = bad_role

    def generate_content(self, *, model: str, contents: Any, config: types.GenerateContentConfig) -> Any:
        self.calls.append({"model": model, "contents": contents, "config": config})
        role = next(r for r in Role if f"You are the {r.value} step" in str(config.system_instruction))
        schema = smoke.load_schema(smoke.FIXTURES, role)
        assert schema is not None
        data = OfflineModel().fill(role, schema, smoke.build_packet(role), turn_id=None, attempt=0).data
        text = "{}" if role.value == self.bad_role else json.dumps(data)
        return types.GenerateContentResponse(
            candidates=[types.Candidate(content=types.Content(role="model", parts=[types.Part(text=text)]),
                                        finish_reason=types.FinishReason.STOP)],
            usage_metadata=types.GenerateContentResponseUsageMetadata(
                prompt_token_count=900, candidates_token_count=120, thoughts_token_count=200),
        )


class FakeClient:
    def __init__(self, bad_role: str | None = None):
        self.models = FakeModels(bad_role)


def test_parse_args() -> None:
    args = smoke.parse_args([])
    assert args.role_list == smoke.ROLE_ORDER and args.model == "gemini-3.8-flash" and args.thinking == "low"
    assert not args.dry_run
    args = smoke.parse_args(["--roles", "reader, narrator", "--thinking", "medium", "--dry-run"])
    assert args.role_list == [Role.READER, Role.NARRATOR] and args.thinking == "medium" and args.dry_run
    with pytest.raises(SystemExit):
        smoke.parse_args(["--roles", "bard"])


def test_dry_run_builds_every_request_and_sends_nothing() -> None:
    lines: list[str] = []

    def no_model(models: Any) -> Any:
        raise AssertionError("a dry run must not build a client")

    assert smoke.run(smoke.parse_args(["--dry-run"]), no_model, lines.append) == 0
    assert lines[0].startswith("7 role(s), model gemini-3.8-flash, thinking low; worst case $")
    assert all("problems none" in ln for ln in lines[1:]) and len(lines) == 8


def test_run_sends_one_request_per_role_with_converted_schema() -> None:
    client = FakeClient()
    made: list[dict[Role, RoleModel]] = []

    def factory(models: dict[Role, RoleModel]) -> GeminiModel:
        made.append(models)
        return GeminiModel(models, client=client)

    lines: list[str] = []
    assert smoke.run(smoke.parse_args([]), factory, lines.append) == 0
    assert len(made) == 1 and set(made[0]) == set(Role)
    assert len(client.models.calls) == 7 and all(" ok " in ln for ln in lines[1:])
    reader = next(c for c in client.models.calls if "reader step" in str(c["config"].system_instruction))
    schema = smoke.load_schema(smoke.FIXTURES, Role.READER)
    assert schema is not None and reader["config"].response_json_schema == to_gemini(schema)
    assert reader["config"].max_output_tokens == gemini.max_output_tokens(Role.READER, "low")
    assert reader["contents"].endswith(smoke.MESSAGES[Role.READER])


def test_run_reports_a_failing_role() -> None:
    lines: list[str] = []
    code = smoke.run(smoke.parse_args(["--roles", "narrator,checker"]),
                     lambda m: GeminiModel(m, client=FakeClient(bad_role="checker")), lines.append)
    assert code == 1
    assert any(ln.startswith("narrator") and " ok " in ln for ln in lines)
    assert any(ln.startswith("checker") and "FAIL" in ln and "missing required field" in ln for ln in lines)


def test_main_without_key_exits_2(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(gemini, "get_key", lambda: None)
    assert smoke.main(["--roles", "reader"]) == 2
    assert "GEMINI_API_KEY" in capsys.readouterr().out
