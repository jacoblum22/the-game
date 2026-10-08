"""The Reader role (A1; contracts/model-calls.md): T2 CLASSIFY and PR-01-1 PARSE (12.2.2 decision 3).

    res = read_message(ctx, "I slip past the watchman. Is the ferry running?", exchanges=recent)
    res.parts            # [Part(text, class, question_kind, topic)] in the player's order (12.2.2)
    res.fact_questions   # FICTION_QUESTION and embedded questions (01.2.1, 01.3.8)
    plans = res.plans(actor="pc.wren", declared_seq=state.last_seq, mint=tx.mint)    # ≤3 BeatPlans (01.2.3)

The model classifies from closed enums: per beat only the verb, target, three method facets and the shape; per part
the question kind and topic. The gate (engine/resolve/gate.py), the roll test (engine/resolve/necessity.py) and the
DC are computed (00.12.3, 01.4.1, DL-12-50). A "what do I know?" sentence is routed by code before the call.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Sequence
from typing import Any

from pydantic import BaseModel, Field

from engine import ids
from engine.audit.fallback import drop_reader_notes
from engine.dm.context import TurnContext
from engine.dm.packet import build_packet
from engine.dm.roles.prompts import load_prompt
from engine.dm.schemas import build_schema, defaults, schema_context
from engine.llm.base import Role, call_role
from engine.resolve.pipeline import MAX_BEATS, BeatPlan
from engine.resolve.types import Beat
from engine.retrieve.anchors import scene_situation_tags
from engine.retrieve.cards import load_cards_for
from engine.retrieve.scene import focus_ids
from engine.retrieve.triggers import get_active_triggers
from engine.store.records import Part

NONE = "none"
# "what do I know (about X)?" is the codex's Journal (14.6.3, 12.5.10), out of fiction; "I try to remember ..." is
# an in-fiction Recall (01.18.6) and is left to the Reader.
KNOW_QUESTION = re.compile(r"\bwhat (?:do|did) (?:i|we) (?:\w+ )?know\b|\bwhat (?:have i|i've) (?:learn|found out)"
                           r"|\bwhat does my character know\b", re.I)
_QUEUED_TAIL = re.compile(r"(?:(?<=[.!?;])\s+|\n\s*)Then\b")  # rule: 01.2.3 (queued beats follow the beat's line)
RECALL_WORDS = re.compile(r"\b(?:remember|recall|think back|try to|search my memory|rack my)", re.I)
_SENTENCE = re.compile(r"(?<=[.!?])\s+")
NOW = "now"
NOW_SHAPES = (NOW, "extended")  # resolved this turn; `extended` (01.2.2) is a goal of several stretches


def knowledge_question(text: str) -> bool:
    """A player's out-of-fiction "what do I know?" (not a Recall attempt, not a question to an NPC)."""
    return bool(KNOW_QUESTION.search(text)) and not RECALL_WORDS.search(text)


def knowledge_parts(message: str) -> tuple[list[Part], str]:  # rule: 14.6.3
    """The code pre-router (before the Reader call): each "what do I know?" sentence is an OOF_QUESTION answered
    from the journal (12.10.5), never a Recall roll or an Oracle draw about the PC's own memory (P-038, P-115).
    Returns (those parts, the rest of the message for the Reader; "" when nothing is left)."""
    if not knowledge_question(message):
        return [], message
    known: list[Part] = []
    rest: list[str] = []
    for s in _SENTENCE.split(message.strip()):
        if knowledge_question(s):
            known.append(Part.model_validate({"text": s, "class": "OOF_QUESTION"}))
        else:
            rest.append(s)
    return known, " ".join(rest).strip()


class FactQuestion(BaseModel):
    subject: str | None = None
    predicate: str
    odds_rung: str | None = None


class ReaderBeat(BaseModel):
    intent: str
    method: str
    assertion: str | None = None
    shape: str | None = NOW  # 12.2.2: now, queued (a Ready beat) or conditional on another beat
    target: str | None = None
    verb: str | None = None
    against_will: bool = False
    uses_power: bool = False
    speech: bool = False
    g4_fact: str | None = None
    intent_verbs: list[str] = Field(default_factory=list)


class ReaderResult(BaseModel):
    parts: list[Part] = Field(default_factory=list)
    pending_answer: str | None = None
    fact_questions: list[FactQuestion] = Field(default_factory=list)
    beats: list[ReaderBeat] = Field(default_factory=list)
    clarifying_question: str | None = None
    restatement: str = ""
    player_quantity: int | None = None
    defaulted: bool = False

    def classes(self) -> list[str]:
        return [p.cls for p in self.parts]

    def _now(self) -> list[ReaderBeat]:
        return [b for b in self.beats if (b.shape or NOW) in NOW_SHAPES]

    def plans(self, *, actor: str, declared_seq: int, mint: Callable[[str], str]) -> list[BeatPlan]:  # rule: 01.2.3
        """The beats to resolve now, in the player's order (the caller resolves the first three). A queued or
        conditional beat ("I attack if they keep stalling") is not resolved now: it waits in `queued` (I-146c)."""
        out: list[BeatPlan] = []
        now = self._now()
        single = len(now) == 1
        # the one beat's line, not the queued "Then, ..." tail: an OFFER must not read as one roll for both
        own = _QUEUED_TAIL.split(self.restatement, maxsplit=1)[0].strip()
        # the Reader's own notes ("Spoken to Oggza, not a beat: ...") are not the beat's line (P-108)
        own = drop_reader_notes(own)
        # ponytail: a Talk beat "asks" when any part carries a question kind; per-beat kinds if two Talks differ
        asks = any(p.question_kind not in (None, NONE) for p in self.parts if p.cls in ("DECLARATION", "SPEECH"))
        for b in now:
            target = b.target if b.target and b.target != NONE else None
            beat = Beat(id=mint(ids.BEAT), actor=actor, intent=b.intent, method=b.method or b.intent,
                        assertion=b.assertion, shape="extended" if b.shape == "extended" else "single",
                        target=target, restatement=(own if single and own else b.intent),
                        verb=b.verb, against_will=b.against_will, uses_power=b.uses_power, speech=b.speech,
                        asks=asks and b.verb == "verb.talk", g4_fact=b.g4_fact, declared_seq=declared_seq)
            out.append(BeatPlan(beat=beat, intent_verbs=list(b.intent_verbs)))
        return out

    @property
    def queued(self) -> list[str]:
        later = [b.intent for b in self.beats if (b.shape or NOW) not in NOW_SHAPES]
        return [b.intent for b in self._now()[MAX_BEATS:]] + later


def reader_check(data: Any) -> list[str]:  # rule: 12.2.2
    """Semantic constraints the schema cannot express."""
    classes = [p.get("class") for p in data.get("parts", [])]
    if "PENDING_ANSWER" in classes and not data.get("pending_answer"):
        return ["a PENDING_ANSWER part needs pending_answer set to the open pause's choice id"]
    return []


def read_message(ctx: TurnContext, message: str, *, exchanges: Sequence[Any] = ()) -> ReaderResult:
    # rule: 12.2.2
    """One Reader call: classify the message's parts and parse its beats and fact questions. A message that is only
    "what do I know?" makes no call."""
    known, rest = knowledge_parts(message)
    if not rest:
        return ReaderResult(parts=known, restatement=message)
    st = ctx.state
    focus = focus_ids(st, rest)  # 12.2.4: facts about whom the player names rank higher
    sctx = schema_context(st, ctx.rules, message=rest, focus=focus)
    schema = build_schema(Role.READER, sctx)
    triggers = get_active_triggers(st, ctx.rules)
    mode = st.scene.mode if st.scene else None
    cards = load_cards_for(Role.READER, scene_situation_tags(st, ctx.rules), mode, triggers, rules=ctx.rules)
    packet = build_packet(Role.READER, instructions=load_prompt("reader"), cards=cards, view=st,
                          exchanges=list(exchanges), message=rest, triggers=triggers, focus=focus,
                          rules=ctx.rules)
    res = call_role(ctx.model, Role.READER, schema, packet, turn_id=ctx.turn_id, recorder=ctx.record_call,
                    default=lambda: defaults(Role.READER, sctx) or {}, check=reader_check)
    data = dict(res.data)
    return ReaderResult(
        parts=[*known, *[Part.model_validate(p) for p in data.get("parts", [])]],
        pending_answer=data.get("pending_answer"),
        fact_questions=[FactQuestion.model_validate(q) for q in data.get("fact_questions", [])],
        beats=[ReaderBeat.model_validate(b) for b in data.get("beats", [])],
        clarifying_question=data.get("clarifying_question"),
        restatement=data.get("restatement") or "",
        player_quantity=data.get("player_quantity"),
        defaulted=res.defaulted,
    )
