"""engine/llm/gemini.py against a fake client: never a network call."""

from __future__ import annotations

import json
from typing import Any

import pytest
from google.genai import errors, types

from engine.llm import gemini
from engine.llm.base import (
    MissingKey,
    ModelCallRecord,
    ModelRefused,
    ModelUnavailable,
    Outcome,
    Packet,
    Role,
    RoleModel,
    call_role,
)
from engine.llm.gemini import GeminiModel

SCHEMA: dict[str, Any] = {
    "type": "object", "properties": {"cut_now": {"type": "boolean"}}, "required": ["cut_now"],
    "additionalProperties": False,
}


def response(text: str | None = '{"cut_now": true}', *, finish: types.FinishReason = types.FinishReason.STOP,
             block: types.BlockedReason | None = None, thought: str | None = None) -> types.GenerateContentResponse:
    parts = []
    if thought:
        parts.append(types.Part(text=thought, thought=True))
    if text is not None:
        parts.append(types.Part(text=text))
    return types.GenerateContentResponse(
        candidates=[types.Candidate(content=types.Content(role="model", parts=parts), finish_reason=finish)]
        if block is None else [],
        prompt_feedback=types.GenerateContentResponsePromptFeedback(block_reason=block) if block else None,
        usage_metadata=types.GenerateContentResponseUsageMetadata(
            prompt_token_count=6000, cached_content_token_count=3000, candidates_token_count=300,
            thoughts_token_count=100, total_token_count=6400,
        ),
    )


class FakeModels:
    def __init__(self, script: list[Any]):
        self.script = list(script)
        self.calls: list[dict[str, Any]] = []

    def generate_content(self, *, model: str, contents: Any, config: types.GenerateContentConfig) -> Any:
        self.calls.append({"model": model, "contents": contents, "config": config})
        item = self.script.pop(0)
        if isinstance(item, BaseException):
            raise item
        return item


class FakeClient:
    def __init__(self, *script: Any):
        self.models = FakeModels(list(script))


def make(*script: Any, **kw: Any) -> tuple[GeminiModel, FakeClient, list[float]]:
    client = FakeClient(*script)
    sleeps: list[float] = []
    model = GeminiModel(client=client, sleep=sleeps.append, **kw)
    return model, client, sleeps


PACKET = Packet(instructions="Decide cuts.", core="core rules", message="quiet_turns: 4")


def test_request_shape_and_usage() -> None:
    model, client, _ = make(response(thought="hmm, thinking"))
    res = model.fill(Role.DIRECTOR, SCHEMA, PACKET, turn_id="t9", attempt=0)
    assert res.data == {"cut_now": True}
    call = client.models.calls[0]
    cfg: types.GenerateContentConfig = call["config"]
    assert call["model"] == "gemini-3.8-flash"
    assert cfg.response_mime_type == "application/json" and cfg.response_json_schema == SCHEMA
    assert cfg.thinking_config is not None and cfg.thinking_config.thinking_level == types.ThinkingLevel.LOW
    assert cfg.system_instruction == "Decide cuts."
    assert "Decide cuts." not in call["contents"] and call["contents"].endswith("quiet_turns: 4")
    rec = res.record
    assert (rec.tokens_in_cached, rec.tokens_in, rec.tokens_out, rec.tokens_thinking) == (3000, 3000, 300, 100)
    assert rec.cost_usd > 0 and rec.provider == "gemini" and rec.turn_id == "t9"
    assert rec.response == {"data": {"cut_now": True}, "text": '{"cut_now": true}', "error": None}
    assert rec.request["schema"] == SCHEMA


def test_role_model_and_older_thinking_budget() -> None:
    models = {Role.CHECKER: RoleModel(model="gemini-2.5-flash", thinking="low")}
    model, client, _ = make(response(), models=models)
    model.fill(Role.CHECKER, SCHEMA, PACKET, turn_id=None, attempt=0)
    cfg = client.models.calls[0]["config"]
    assert client.models.calls[0]["model"] == "gemini-2.5-flash"
    assert cfg.thinking_config.thinking_budget == 1024 and cfg.thinking_config.thinking_level is None


def test_invalid_json_goes_through_reask() -> None:
    model, client, _ = make(response("not json"), response('{"cut_now": false}'))
    seen: list[ModelCallRecord] = []
    res = call_role(model, Role.DIRECTOR, SCHEMA, PACKET, recorder=seen.append)
    assert res.data == {"cut_now": False} and [r.outcome for r in seen] == [Outcome.INVALID_REASKED, Outcome.OK]
    assert "CORRECTION" in client.models.calls[1]["contents"]


@pytest.mark.parametrize(
    "resp",
    [response(finish=types.FinishReason.SAFETY), response(block=types.BlockedReason.PROHIBITED_CONTENT)],
)
def test_safety_block_is_refusal(resp: types.GenerateContentResponse) -> None:
    model, _, _ = make(resp)
    seen: list[ModelCallRecord] = []
    with pytest.raises(ModelRefused) as info:
        call_role(model, Role.NARRATOR, SCHEMA, PACKET, recorder=seen.append)
    assert info.value.record is not None and seen[0].outcome == Outcome.REFUSED


def _api(code: int) -> errors.APIError:
    cls = errors.ServerError if code >= 500 else errors.ClientError
    return cls(code, {"error": {"code": code, "message": "boom", "status": "X"}})


def test_retries_429_and_5xx_with_backoff() -> None:
    model, _, sleeps = make(_api(429), _api(503), response(), backoff_s=0.5)
    assert model.fill(Role.READER, SCHEMA, PACKET, turn_id=None, attempt=0).data == {"cut_now": True}
    assert sleeps == [0.5, 1.0]


def test_unavailable_after_retries() -> None:
    model, client, sleeps = make(*[_api(500)] * 4, max_retries=3)
    seen: list[ModelCallRecord] = []
    with pytest.raises(ModelUnavailable) as info:
        call_role(model, Role.READER, SCHEMA, PACKET, recorder=seen.append)
    assert len(client.models.calls) == 4 and len(sleeps) == 3
    assert info.value.record is not None and seen[0].outcome == Outcome.ERROR
    assert "HTTP 500" in (seen[0].response or {}).get("error", "")


def test_client_error_is_not_retried() -> None:
    model, client, _ = make(_api(400), response())
    with pytest.raises(ModelUnavailable):
        model.fill(Role.READER, SCHEMA, PACKET, turn_id=None, attempt=0)
    assert len(client.models.calls) == 1


def test_missing_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(gemini, "get_key", lambda: None)
    with pytest.raises(MissingKey):
        GeminiModel()


def test_record_is_json_serialisable() -> None:
    model, _, _ = make(response())
    rec = model.fill(Role.READER, SCHEMA, PACKET, turn_id=None, attempt=0).record
    json.loads(rec.model_dump_json())
