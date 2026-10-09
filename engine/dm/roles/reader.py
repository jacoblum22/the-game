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
SERVES, FREE_ACTIVITY = "serves_another_act", "free_activity"  # schemas.BEAT_PURPOSES
# the verbs a step, posture, gesture or touch is read under (policy B4: menace, manner, attention, reach)
BODY_VERBS = ("verb.move", "verb.handle", "verb.strike", "verb.grapple", "verb.force")
# 00.12.6's free activities by verb: draw, stow, pick up or put down (Handle), stay put (Move), rest (Endure),
# wait (Ready), a casual look (Observe)
FREE_VERBS = ("verb.handle", "verb.move", "verb.endure", "verb.ready", "verb.observe")
# a look the player makes explicitly casual (policy A4); any other look, search or study is an Observe beat
CASUAL = re.compile(r"\b(?:glanc\w*|casual\w*|idly|without (?:staring|making a show|being obvious|seeming to))\b"
                    r"|\bin passing\b", re.I)
NOW_SHAPES = (NOW, "extended")  # resolved this turn; `extended` (01.2.2) is a goal of several stretches


def now_beats(beats: Sequence[Any]) -> list[Any]:  # rule: 12.2.2
    """The beats resolved this turn: shape now or extended. A conditional beat waits on another beat; with no
    other beat to wait on ("I pour the draught when he looks away") it is this turn's beat."""
    def shape(b: Any) -> str:
        return str((b.get("shape") if isinstance(b, dict) else b.shape) or NOW)

    now = [b for b in beats if shape(b) in NOW_SHAPES]
    return now or [b for b in beats if shape(b) == "conditional"][:1]


def normalise(data: dict[str, Any]) -> dict[str, Any]:  # rule: 01.2.1, 01.2.2, 00.12.6, 12.2.2, 15.3.10
    """Code decides what the Reader marks (the model proposes, DL-12-50), on its raw answer:
    - a beat that only serves another act or the words (a step, turn, posture or touch: no intended change of its
      own, 01.2.1) is part of the beat it serves (01.2.2): its method joins the next kept beat (else the one
      before); with only words to serve, it goes;
      A step that closes on the target of the next now-beat against someone's will is that act's reach (policy B4);
    - a free activity (00.12.6: drawing a weapon, waiting, resting, staying put, a look the player calls casual) is
      no beat;
    - a Talk beat with no request, threat, offer, plea or insistence, in a message that asks something, is a plain
      question: SPEECH (12.2.2, 15.3.10), so its DECLARATION question parts become SPEECH when no beat is left.
    The marks are honoured only where the rules allow them: only a bodily act (a step, posture, touch) serves
    another; only 00.12.6's acts are free, a look only when the player says it is casual; a beat against someone's
    will or using a power is always its own beat (12.2.2 facets)."""
    beats = [dict(b) for b in data.get("beats", [])]
    parts = [dict(p) for p in data.get("parts", [])]
    asks = any(p.get("question_kind") not in (None, NONE) for p in parts)

    def pinned(b: dict[str, Any]) -> bool:
        return bool(b.get("against_will") or b.get("uses_power"))

    def plain_talk(b: dict[str, Any]) -> bool:
        return b.get("verb") == "verb.talk" and b.get("pressure") == NONE and asks

    def free(b: dict[str, Any]) -> bool:
        v = b.get("verb")
        return b.get("purpose") == FREE_ACTIVITY and v in FREE_VERBS and (
            v != "verb.observe" or bool(CASUAL.search(f"{b.get('method')} {b.get('intent')}")))

    def serves(i: int, b: dict[str, Any]) -> bool:
        if pinned(b) or b.get("verb") not in BODY_VERBS:
            return False
        if b.get("purpose") == SERVES:
            return True
        nxt = next((c for c in beats[i + 1:] if (c.get("shape") or NOW) in NOW_SHAPES), None)
        # ponytail: reach read from the order and the target; a run across a yard to tackle someone folds too
        return (b.get("verb") == "verb.move" and nxt is not None and bool(nxt.get("against_will"))
                and b.get("target") in (None, NONE, nxt.get("target")))

    gone = [not pinned(b) and (free(b) or plain_talk(b)) for b in beats]
    words = any(p.get("class") == "SPEECH" for p in parts) or any(plain_talk(b) for b in beats)
    acts = [i for i, b in enumerate(beats) if not gone[i] and not serves(i, b)]
    for i, b in enumerate(beats):
        if gone[i] or i in acts:
            continue
        served = next((j for j in acts if j > i), acts[-1] if acts else None)
        if served is not None:
            beats[served]["method"] = f"{b.get('method')}, {beats[served].get('method')}"
        gone[i] = served is not None or words  # a lone step with nothing to serve stays a beat
    kept = [b for i, b in enumerate(beats) if not gone[i]]
    if not kept and any(plain_talk(b) for b in beats):
        for p in parts:
            if p.get("class") == "DECLARATION" and p.get("question_kind") not in (None, NONE):
                p["class"] = "SPEECH"
    return {**data, "beats": kept, "parts": parts}


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
    pressure: str = NONE  # 12.2.2: request, threat, offer, plea, insistence (event tags, 12.11.9)
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
    rests_on: str | None = None  # PR-12-12 (a): the `said` id the action relies on (spec 013)
    defaulted: bool = False

    def classes(self) -> list[str]:
        return [p.cls for p in self.parts]

    def _now(self) -> list[ReaderBeat]:
        return now_beats(self.beats)

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
                        pressure=b.pressure or NONE,
                        asks=asks and b.verb == "verb.talk", g4_fact=b.g4_fact, declared_seq=declared_seq)
            out.append(BeatPlan(beat=beat, intent_verbs=list(b.intent_verbs)))
        return out

    @property
    def queued(self) -> list[str]:
        now = self._now()
        later = [b.intent for b in self.beats if b not in now]
        return [b.intent for b in now[MAX_BEATS:]] + later


_MAYBE_DISPUTE = re.compile(
    r"\b(?:you said|you told me|that'?s (?:wrong|not right|not what)|already (?:told|said|gave|did|happened)|"
    r"i meant|not what i meant|i (?:didn'?t|did not) (?:say|mean|do)|never happened|didn'?t happen|"
    r"(?:he|she|they) (?:already|just) (?:told|said))\b", re.IGNORECASE)


def possible_dispute(message: str, classes: Sequence[str]) -> bool:  # rule: 12.2.2
    """12.2.2 / 12.3.6 item 1: a fiction message that may also be a dispute (a code scan of the player's words; the
    Reader classified no DISPUTE part): the response ends with the fix hint."""
    return "DISPUTE" not in classes and bool(_MAYBE_DISPUTE.search(message))


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
    data = normalise(dict(res.data))
    return ReaderResult(
        parts=[*known, *[Part.model_validate(p) for p in data.get("parts", [])]],
        pending_answer=data.get("pending_answer"),
        fact_questions=[FactQuestion.model_validate(q) for q in data.get("fact_questions", [])],
        beats=[ReaderBeat.model_validate(b) for b in data.get("beats", [])],
        clarifying_question=data.get("clarifying_question"),
        restatement=data.get("restatement") or "",
        player_quantity=data.get("player_quantity"),
        rests_on=data.get("rests_on") if data.get("rests_on") not in (None, NONE) else None,
        defaulted=res.defaulted,
    )
