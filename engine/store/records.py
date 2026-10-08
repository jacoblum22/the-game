"""Records the engine adds that are not events (data-model.md §4): the turn record. The scene and pause
records are event payload parts and live in engine/store/events.py (`SceneRecord`, `PauseRecord`)."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

PartClass = Literal["SAFETY", "SESSION", "DISPUTE", "PENDING_ANSWER", "OOF_QUESTION", "FICTION_QUESTION",
                    "DECLARATION", "SPEECH"]


class Part(BaseModel):
    text: str
    cls: PartClass = Field(alias="class")
    question_kind: str = "none"  # 12.2.2: who_is, where_is, what_happened, what_like, what_want, who_knows, none
    topic: str | None = None  # the entity or subject asked about (the answer ladder's key, spec 008)
    model_config = {"populate_by_name": True}


class TurnRecord(BaseModel):
    """data-model.md §4 TurnRecord (FR-037). Saved with `Store.save_turn` (insert or replace by turn_id)."""

    turn_id: str
    input_verbatim: str
    parts: list[Part] = Field(default_factory=list)
    beats: list[str] = Field(default_factory=list)  # frame ids
    oracle_calls: list[int] = Field(default_factory=list)  # event seqs
    pause: dict[str, Any] | None = None  # {kind, frame_id, options}
    writes: list[int] = Field(default_factory=list)  # event seqs
    draft_versions: list[dict[str, Any]] = Field(default_factory=list)  # {text, mentions, claims, verdicts}
    verdicts: list[dict[str, Any]] = Field(default_factory=list)  # the final draft's verdicts
    # 12.3.1b (spec 011): what was delivered but logged {turn, sentence, class, verdict, store_value}, and the
    # speech it carried as testimony {speaker, turn, words, about}; never world facts
    claim_log: list[dict[str, Any]] = Field(default_factory=list)
    said: list[dict[str, Any]] = Field(default_factory=list)
    fallback_used: bool = False
    screen: dict[str, Any] = Field(default_factory=dict)
    delivered_verbatim: str = ""
    model_calls: list[str] = Field(default_factory=list)  # call ids
    cost_usd: float = 0.0
    latency_ms: int = 0
