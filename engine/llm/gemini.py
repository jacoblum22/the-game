"""Gemini adapter (google-genai 2.25.0): one structured-output request per role call.

research.md R3. The schema goes in `response_json_schema` (raw JSON Schema dict, enforced server side);
thinking is always set explicitly (`thinking_level` for Gemini 3 models); the role instructions go in the
system instruction and the rest of the packet, stable sections first, is one user turn. 429 and 5xx are
retried with backoff, then `ModelUnavailable`; safety blocks raise `ModelRefused`. Tests inject a fake
client; nothing here is called without a real key.
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable, Mapping
from typing import Any

import httpx
from google.genai import errors, types

from engine.llm import budget
from engine.llm.base import (
    CallResult,
    MissingKey,
    ModelCallRecord,
    ModelRefused,
    ModelUnavailable,
    Outcome,
    Packet,
    Role,
    RoleModel,
    Stopwatch,
    new_record,
)
from engine.llm.env import get_key

DEFAULT_MODEL = RoleModel()

_LEVELS = {
    "minimal": types.ThinkingLevel.MINIMAL,
    "low": types.ThinkingLevel.LOW,
    "medium": types.ThinkingLevel.MEDIUM,
    "high": types.ThinkingLevel.HIGH,
}
# Pre-Gemini-3 models take a token budget instead of a level.
_BUDGETS = {"minimal": 0, "low": 1024, "medium": 8192, "high": 24576}

_SAFETY_FINISH = {
    types.FinishReason.SAFETY,
    types.FinishReason.PROHIBITED_CONTENT,
    types.FinishReason.BLOCKLIST,
    types.FinishReason.SPII,
    types.FinishReason.IMAGE_SAFETY,
}


def thinking_config(model_id: str, level: str) -> types.ThinkingConfig:
    level = level.lower()
    if model_id.startswith("gemini-3"):
        return types.ThinkingConfig(thinking_level=_LEVELS.get(level, types.ThinkingLevel.LOW))
    return types.ThinkingConfig(thinking_budget=_BUDGETS.get(level, 1024))


class GeminiModel:
    """`StructuredModel` over google-genai. `models` maps each role to its pinned model and thinking level."""

    provider = "gemini"

    def __init__(
        self,
        models: Mapping[Role, RoleModel] | None = None,
        *,
        client: Any = None,
        api_key: str | None = None,
        max_retries: int = 3,
        backoff_s: float = 1.0,
        timeout_s: float = 60.0,
        sleep: Callable[[float], None] = time.sleep,
    ):
        self.models = dict(models or {})
        self.max_retries = max_retries
        self.backoff_s = backoff_s
        self.sleep = sleep
        if client is None:
            key = api_key or get_key()
            if not key:
                raise MissingKey("GEMINI_API_KEY is not set in the environment or in .env at the repo root")
            from google import genai

            client = genai.Client(api_key=key, http_options=types.HttpOptions(timeout=int(timeout_s * 1000)))
        self.client = client

    def role_model(self, role: Role) -> RoleModel:
        return self.models.get(role, DEFAULT_MODEL)

    def fill(
        self, role: Role, schema: dict[str, Any], packet: Packet, *, turn_id: str | None, attempt: int,
        seq: int = 0,
    ) -> CallResult:
        cfg = self.role_model(role)
        contents = packet.render(include_instructions=False)
        record = new_record(
            role, schema, provider=self.provider, model_id=cfg.model, turn_id=turn_id, attempt=attempt, seq=seq,
            request={
                "model": cfg.model, "thinking": cfg.thinking, "attempt": attempt,
                "system_instruction": packet.instructions, "contents": contents, "schema": schema,
            },
        )
        config = types.GenerateContentConfig(
            system_instruction=packet.instructions or None,
            response_mime_type="application/json",
            response_json_schema=schema,
            thinking_config=thinking_config(cfg.model, cfg.thinking),
        )
        watch = Stopwatch()
        response = self._generate(cfg.model, contents, config, record, watch)
        record = _with_usage(record, response, watch.ms())
        reason = _refusal(response)
        if reason:
            rec = record.model_copy(
                update={"outcome": Outcome.REFUSED, "response": {"data": None, "text": None, "error": reason}}
            )
            raise ModelRefused(f"{role.value}: provider refused ({reason})", rec)
        text = _text(response)
        try:
            data = json.loads(text) if text else None
        except json.JSONDecodeError:
            data = None
        record = record.model_copy(update={"response": {"data": data, "text": text, "error": None}})
        return CallResult(data=data, record=record)

    def _generate(
        self, model_id: str, contents: str, config: types.GenerateContentConfig, record: ModelCallRecord,
        watch: Stopwatch,
    ) -> Any:
        last = ""
        for i in range(self.max_retries + 1):
            try:
                return self.client.models.generate_content(model=model_id, contents=contents, config=config)
            except errors.APIError as exc:
                last = f"HTTP {exc.code}: {exc.message or exc.status or ''}".strip()
                if not (exc.code == 429 or exc.code >= 500):
                    break
            except (httpx.HTTPError, TimeoutError, ConnectionError) as exc:
                last = f"{type(exc).__name__}: {exc}"
            if i < self.max_retries:
                self.sleep(self.backoff_s * 2**i)
        rec = record.model_copy(
            update={
                "outcome": Outcome.ERROR, "latency_ms": watch.ms(),
                "response": {"data": None, "text": None, "error": last},
            }
        )
        raise ModelUnavailable(f"{record.role.value}: model unavailable ({last})", rec)


def _with_usage(record: ModelCallRecord, response: Any, latency_ms: int) -> ModelCallRecord:
    usage = getattr(response, "usage_metadata", None)
    cached = (getattr(usage, "cached_content_token_count", None) or 0) if usage else 0
    prompt = (getattr(usage, "prompt_token_count", None) or 0) if usage else 0
    rec = record.model_copy(
        update={
            "tokens_in_cached": cached,
            "tokens_in": max(prompt - cached, 0),
            "tokens_out": (getattr(usage, "candidates_token_count", None) or 0) if usage else 0,
            "tokens_thinking": (getattr(usage, "thoughts_token_count", None) or 0) if usage else 0,
            "latency_ms": latency_ms,
        }
    )
    return rec.model_copy(update={"cost_usd": budget.cost(rec)})


def _refusal(response: Any) -> str | None:
    feedback = getattr(response, "prompt_feedback", None)
    block = getattr(feedback, "block_reason", None) if feedback else None
    if block:
        return f"prompt blocked: {getattr(block, 'value', block)}"
    candidates = getattr(response, "candidates", None) or []
    if not candidates:
        return None
    finish = getattr(candidates[0], "finish_reason", None)
    if finish in _SAFETY_FINISH:
        return f"response blocked: {getattr(finish, 'value', finish)}"
    return None


def _text(response: Any) -> str:
    """Concatenate the first candidate's non-thought text parts."""
    candidates = getattr(response, "candidates", None) or []
    if not candidates or candidates[0].content is None:
        return ""
    parts = candidates[0].content.parts or []
    return "".join(p.text for p in parts if getattr(p, "text", None) and not getattr(p, "thought", False))
