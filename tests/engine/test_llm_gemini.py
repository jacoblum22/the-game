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
from engine.llm.gemini import GeminiModel, extract_json, max_output_tokens
from engine.llm.gemini_schema import to_gemini

SCHEMA: dict[str, Any] = {
    "type": "object", "properties": {"cut_now": {"type": "boolean"}}, "required": ["cut_now"],
    "additionalProperties": False,
}


def response(text: str | None = '{"cut_now": true}', *, finish: types.FinishReason = types.FinishReason.STOP,
             block: types.BlockedReason | None = None, thought: str | None = None,
             no_candidates: bool = False) -> types.GenerateContentResponse:
    parts = []
    if thought:
        parts.append(types.Part(text=thought, thought=True))
    if text is not None:
        parts.append(types.Part(text=text))
    return types.GenerateContentResponse(
        candidates=[types.Candidate(content=types.Content(role="model", parts=parts), finish_reason=finish)]
        if block is None and not no_candidates else [],
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
    assert cfg.response_mime_type == "application/json" and cfg.response_json_schema == to_gemini(SCHEMA)
    assert to_gemini(SCHEMA)["propertyOrdering"] == ["cut_now"]
    assert cfg.max_output_tokens == max_output_tokens(Role.DIRECTOR, "low") == 600 + 3072
    assert cfg.automatic_function_calling is not None and cfg.automatic_function_calling.disable is True
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
    model, client, _ = make(_api(403), response())
    with pytest.raises(ModelUnavailable) as info:
        model.fill(Role.READER, SCHEMA, PACKET, turn_id=None, attempt=0)
    assert len(client.models.calls) == 1 and "HTTP 403" in str(info.value)


def test_missing_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(gemini, "get_key", lambda: None)
    with pytest.raises(MissingKey):
        GeminiModel()


def test_record_is_json_serialisable() -> None:
    model, _, _ = make(response())
    rec = model.fill(Role.READER, SCHEMA, PACKET, turn_id=None, attempt=0).record
    json.loads(rec.model_dump_json())


# ------------------------------------------------------------------------------- robustness (fake client)


def test_thinking_levels() -> None:
    assert gemini.thinking_config("gemini-3.8-flash", "minimal").thinking_level == types.ThinkingLevel.LOW
    assert gemini.thinking_config("gemini-3.8-flash", "HIGH").thinking_level == types.ThinkingLevel.HIGH
    assert gemini.thinking_config("gemini-3-flash", "minimal").thinking_level == types.ThinkingLevel.MINIMAL
    assert gemini.thinking_config("gemini-3.8-flash", "bogus").thinking_level == types.ThinkingLevel.LOW
    assert max_output_tokens(Role.NARRATOR, "low") == 1200 + 3072
    assert max_output_tokens(Role.CHECKER, "medium") == 1500 + 8192


@pytest.mark.parametrize("text", [
    '```json\n{"cut_now": true}\n```', '```\n{"cut_now": true}\n```', 'Here you go: {"cut_now": true} done',
    '  {"cut_now": true}\n',
])
def test_fenced_or_wrapped_json_is_read(text: str) -> None:
    model, _, _ = make(response(text))
    assert model.fill(Role.DIRECTOR, SCHEMA, PACKET, turn_id=None, attempt=0).data == {"cut_now": True}


def test_extract_json_gives_up_cleanly() -> None:
    assert extract_json("") is None and extract_json("no json here") is None and extract_json("{broken") is None


def test_no_candidates_is_invalid_then_reasked() -> None:
    model, client, _ = make(response(no_candidates=True), response())
    seen: list[ModelCallRecord] = []
    res = call_role(model, Role.DIRECTOR, SCHEMA, PACKET, recorder=seen.append)
    assert res.data == {"cut_now": True} and len(client.models.calls) == 2
    assert (seen[0].response or {})["error"] == "no candidates in the response"


def test_max_tokens_cut_retries_once_with_double_cap_and_sums_usage() -> None:
    model, client, _ = make(response('{"cut_n', finish=types.FinishReason.MAX_TOKENS), response())
    res = model.fill(Role.DIRECTOR, SCHEMA, PACKET, turn_id=None, attempt=0)
    caps = [c["config"].max_output_tokens for c in client.models.calls]
    assert res.data == {"cut_now": True} and caps == [3672, 7344]
    assert (res.record.tokens_in, res.record.tokens_out, res.record.tokens_thinking) == (6000, 600, 200)
    assert res.record.request["max_output_tokens"] == 7344


def test_max_tokens_twice_is_invalid_with_reason() -> None:
    cut = response('{"cut_n', finish=types.FinishReason.MAX_TOKENS)
    model, _, _ = make(cut, cut)
    res = model.fill(Role.DIRECTOR, SCHEMA, PACKET, turn_id=None, attempt=0)
    assert res.data is None and "MAX_TOKENS" in (res.record.response or {})["error"]


def test_max_tokens_with_complete_json_is_kept() -> None:
    model, client, _ = make(response(finish=types.FinishReason.MAX_TOKENS))
    assert model.fill(Role.DIRECTOR, SCHEMA, PACKET, turn_id=None, attempt=0).data == {"cut_now": True}
    assert len(client.models.calls) == 1


def test_schema_rejected_steps_down_and_role_remembers() -> None:
    model, client, _ = make(_api(400), _api(400), response(), response())
    res = model.fill(Role.READER, SCHEMA, PACKET, turn_id=None, attempt=0)
    cfgs = [c["config"] for c in client.models.calls]
    assert res.data == {"cut_now": True}
    assert cfgs[0].response_json_schema == to_gemini(SCHEMA, level=0)
    assert cfgs[1].response_json_schema == to_gemini(SCHEMA, level=1)
    assert cfgs[2].response_json_schema is None and "JSON Schema" in cfgs[2].system_instruction
    assert cfgs[2].response_mime_type == "application/json"
    assert res.record.request["schema_level"] == 2 and len(res.record.request["schema_rejected"]) == 2
    assert res.record.request["schema"] == SCHEMA and res.record.schema_hash == gemini.new_record(
        Role.READER, SCHEMA, provider="gemini", model_id="m", turn_id=None, attempt=0).schema_hash
    model.fill(Role.READER, SCHEMA, PACKET, turn_id=None, attempt=0)  # starts at level 2 now
    assert client.models.calls[3]["config"].response_json_schema is None
    assert model.schema_level == {Role.READER: 2}


def test_rejected_at_every_level_is_unavailable() -> None:
    model, client, _ = make(_api(400), _api(400), _api(400))
    seen: list[ModelCallRecord] = []
    with pytest.raises(ModelUnavailable) as info:
        call_role(model, Role.READER, SCHEMA, PACKET, recorder=seen.append)
    assert len(client.models.calls) == 3 and "level 0" in str(info.value) and "level 2" in str(info.value)
    assert seen[0].outcome == Outcome.ERROR and model.schema_level == {}


def test_408_and_network_errors_are_retried() -> None:
    import httpx

    model, _, sleeps = make(_api(408), httpx.ConnectError("down"), response(), backoff_s=0.1)
    assert model.fill(Role.READER, SCHEMA, PACKET, turn_id=None, attempt=0).data == {"cut_now": True}
    assert sleeps == [0.1, 0.2]


# ------------------------------------------------------------- the real SDK over a mock HTTP transport


def _sdk_model(handler: Any, **kw: Any) -> GeminiModel:
    """A real google-genai Client whose HTTP layer is an httpx MockTransport: the SDK builds the real request
    body and parses a real REST response, and nothing leaves the process."""
    import httpx
    from google import genai

    http = httpx.Client(transport=httpx.MockTransport(handler))
    client = genai.Client(api_key="test-key", http_options=types.HttpOptions(httpx_client=http))
    return GeminiModel(client=client, sleep=lambda _s: None, **kw)


def _rest(text: str, finish: str = "STOP", **usage: int) -> dict[str, Any]:
    """A generateContent REST body shaped like the API's (camelCase, thought parts, thought signature)."""
    return {
        "candidates": [{"content": {"role": "model", "parts": [
            {"text": "Planning the answer", "thought": True},
            {"text": text, "thoughtSignature": "c2ln"},
        ]}, "finishReason": finish, "index": 0}],
        "usageMetadata": {"promptTokenCount": 5200, "cachedContentTokenCount": 4100, "candidatesTokenCount": 40,
                          "thoughtsTokenCount": 310, "totalTokenCount": 5550, **usage},
        "modelVersion": "gemini-3.8-flash", "responseId": "r1",
    }


def test_sdk_request_body_and_response_parsing() -> None:
    import httpx

    sent: list[httpx.Request] = []

    def handler(req: httpx.Request) -> httpx.Response:
        sent.append(req)
        return httpx.Response(200, json=_rest('{"cut_now": false}'))

    model = _sdk_model(handler)
    res = model.fill(Role.DIRECTOR, SCHEMA, PACKET, turn_id="t1", attempt=0)
    assert res.data == {"cut_now": False}
    req = sent[0]
    assert req.url.path == "/v1beta/models/gemini-3.8-flash:generateContent"
    assert req.headers["x-goog-api-key"] == "test-key"
    body = json.loads(req.content)
    gen = body["generationConfig"]
    assert gen["responseMimeType"] == "application/json"
    assert gen["responseJsonSchema"] == to_gemini(SCHEMA) and "responseSchema" not in gen
    assert gen["maxOutputTokens"] == 3672
    assert gen["thinkingConfig"] in ({"thinkingLevel": "LOW"}, {"thinking_level": "LOW"})
    assert body["systemInstruction"]["parts"][0]["text"] == "Decide cuts."
    assert body["contents"][0]["parts"][0]["text"].endswith("quiet_turns: 4")
    assert "tools" not in body and "automaticFunctionCalling" not in json.dumps(body)
    rec = res.record
    assert (rec.tokens_in, rec.tokens_in_cached, rec.tokens_out, rec.tokens_thinking) == (1100, 4100, 40, 310)
    assert rec.response is not None and rec.response["text"] == '{"cut_now": false}'  # the thought part is left out


def test_sdk_http_errors() -> None:
    import httpx

    codes = iter([429, 503, 200])

    def flaky(req: httpx.Request) -> httpx.Response:
        code = next(codes)
        if code != 200:
            return httpx.Response(code, json={"error": {"code": code, "message": "busy", "status": "UNAVAILABLE"}})
        return httpx.Response(200, json=_rest('{"cut_now": true}'))

    assert _sdk_model(flaky).fill(Role.DIRECTOR, SCHEMA, PACKET, turn_id=None, attempt=0).data == {"cut_now": True}

    bodies: list[dict[str, Any]] = []

    def picky(req: httpx.Request) -> httpx.Response:
        bodies.append(json.loads(req.content))
        if "responseJsonSchema" in bodies[-1]["generationConfig"]:
            return httpx.Response(400, json={"error": {"code": 400, "status": "INVALID_ARGUMENT",
                                                       "message": "schema produces too many states"}})
        return httpx.Response(200, json=_rest('{"cut_now": true}'))

    res = _sdk_model(picky).fill(Role.DIRECTOR, SCHEMA, PACKET, turn_id=None, attempt=0)
    assert res.data == {"cut_now": True} and len(bodies) == 3
    assert "too many states" in res.record.request["schema_rejected"][0]

    def missing(req: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"error": {"code": 404, "status": "NOT_FOUND",
                                                   "message": "models/gemini-9 is not found"}})

    with pytest.raises(ModelUnavailable, match="HTTP 404: models/gemini-9 is not found"):
        _sdk_model(missing).fill(Role.DIRECTOR, SCHEMA, PACKET, turn_id=None, attempt=0)


def test_sdk_safety_block_and_max_tokens() -> None:
    import httpx

    def blocked(req: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"promptFeedback": {"blockReason": "PROHIBITED_CONTENT"},
                                         "usageMetadata": {"promptTokenCount": 10, "totalTokenCount": 10}})

    with pytest.raises(ModelRefused, match="PROHIBITED_CONTENT"):
        _sdk_model(blocked).fill(Role.NARRATOR, SCHEMA, PACKET, turn_id=None, attempt=0)

    caps: list[int] = []

    def cut(req: httpx.Request) -> httpx.Response:
        caps.append(json.loads(req.content)["generationConfig"]["maxOutputTokens"])
        if len(caps) == 1:
            return httpx.Response(200, json=_rest('{"cut', finish="MAX_TOKENS"))
        return httpx.Response(200, json=_rest('{"cut_now": true}'))

    res = _sdk_model(cut).fill(Role.NARRATOR, SCHEMA, PACKET, turn_id=None, attempt=0)
    assert res.data == {"cut_now": True} and caps == [4272, 8544]
    assert res.record.tokens_thinking == 620


def test_bad_key_400_is_not_a_schema_rejection() -> None:
    bad = errors.ClientError(400, {"error": {"code": 400, "status": "INVALID_ARGUMENT",
                                             "message": "API key not valid. Please pass a valid API key."}})
    model, client, _ = make(bad, response())
    with pytest.raises(ModelUnavailable, match="API key not valid"):
        model.fill(Role.READER, SCHEMA, PACKET, turn_id=None, attempt=0)
    assert len(client.models.calls) == 1
