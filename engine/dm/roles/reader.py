"""The Reader role (A1; contracts/model-calls.md): T2 CLASSIFY and PR-01-1 PARSE / GATE proposal / NECESSITY.

    res = read_message(ctx, "I slip past the watchman. Is the ferry running?", exchanges=recent)
    res.parts            # [Part(text, class)] in the player's order (12.2.2)
    res.fact_questions   # FICTION_QUESTION and embedded questions (01.2.1, 01.3.8)
    plans = res.plans(actor="pc.wren", declared_seq=state.last_seq, mint=tx.mint)    # ≤3 BeatPlans (01.2.3)

The model classifies and proposes from closed enums; the engine checks the gate against holdings
(engine/resolve/gate.py) and answers fact questions from the store or the Oracle.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Sequence
from typing import Any

from pydantic import BaseModel, Field

from engine import ids
from engine.dm.context import TurnContext
from engine.dm.packet import build_packet
from engine.dm.roles.prompts import load_prompt
from engine.dm.schemas import build_schema, defaults, schema_context
from engine.llm.base import Role, call_role
from engine.resolve.pipeline import MAX_BEATS, BeatPlan
from engine.resolve.types import Beat
from engine.retrieve.anchors import scene_situation_tags
from engine.retrieve.cards import load_cards_for
from engine.retrieve.triggers import get_active_triggers
from engine.store.records import Part

NONE = "none"
# "what do I know (about X)?" is the codex's Journal (14.6.3, 12.5.10), out of fiction; "I try to remember ..." is
# an in-fiction Recall (01.18.6) and is left to the Reader.
KNOW_QUESTION = re.compile(r"\bwhat (?:do|did) (?:i|we) (?:\w+ )?know\b|\bwhat (?:have i|i've) (?:learn|found out)"
                           r"|\bwhat does my character know\b", re.I)
_QUEUED_TAIL = re.compile(r"(?:(?<=[.!?;])\s+|\n\s*)Then\b")  # rule: 01.2.3 (queued beats follow the beat's line)
RECALL_WORDS = re.compile(r"\b(?:remember|recall|think back|try to|search my memory|rack my)", re.I)


def knowledge_question(text: str) -> bool:
    """A player's out-of-fiction "what do I know?" (not a Recall attempt, not a question to an NPC)."""
    return bool(KNOW_QUESTION.search(text)) and not RECALL_WORDS.search(text)


def _knowledge_parts(out: ReaderResult, pc: str | None) -> None:  # rule: 14.6.3
    """A "what do I know?" part is an OOF_QUESTION whatever the Reader called it, so it is answered from the
    journal (12.10.5) instead of becoming a Recall roll, an Oracle draw about the PC's own memory, or a scene."""
    hit = False
    for p in out.parts:
        if p.cls in ("FICTION_QUESTION", "DECLARATION") and knowledge_question(p.text):
            p.cls = "OOF_QUESTION"  # type: ignore[assignment]
            hit = True
    if hit:
        out.fact_questions = [q for q in out.fact_questions if not (q.subject == pc and "know" in q.predicate)]
        if not any(RECALL_WORDS.search(p.text) for p in out.parts):  # nobody asked to recall in-fiction
            out.beats = [b for b in out.beats if b.verb != "verb.recall"]


class FactQuestion(BaseModel):
    subject: str | None = None
    predicate: str
    odds_rung: str | None = None


class ReaderBeat(BaseModel):
    intent: str
    method: str
    assertion: str | None = None
    shape: str | None = "single"
    target: str | None = None
    verb: str | None = None
    license: str | None = None
    would_be_license: str | None = None  # G3: the licence the method needs (PR-01-5 step 1)
    gate: str = "G3"
    g4_fact: str | None = None
    necessity: str = "uncertain_and_costly"
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

    def plans(self, *, actor: str, declared_seq: int, mint: Callable[[str], str]) -> list[BeatPlan]:  # rule: 01.2.3
        """The beats as pipeline inputs, in the player's order (the caller resolves the first three)."""
        out: list[BeatPlan] = []
        single = len(self.beats) == 1
        # the one beat's line, not the queued "Then, ..." tail: an OFFER must not read as one roll for both
        own = _QUEUED_TAIL.split(self.restatement, maxsplit=1)[0].strip()
        for b in self.beats:
            target = b.target if b.target and b.target != NONE else None
            lic = b.license if b.license and b.license != NONE else None
            wbl = b.would_be_license if b.would_be_license and b.would_be_license != NONE else None
            beat = Beat(id=mint(ids.BEAT), actor=actor, intent=b.intent, method=b.method or b.intent,
                        assertion=b.assertion, shape=b.shape or "single",  # type: ignore[arg-type]
                        target=target, restatement=(own if single and own else b.intent),
                        gate=b.gate, verb=b.verb, license=lic, g4_fact=b.g4_fact,  # type: ignore[arg-type]
                        would_be_license=wbl,
                        necessity=b.necessity, declared_seq=declared_seq)
            out.append(BeatPlan(beat=beat, intent_verbs=list(b.intent_verbs)))
        return out

    @property
    def queued(self) -> list[str]:
        return [b.intent for b in self.beats[MAX_BEATS:]]


def reader_check(data: Any) -> list[str]:  # rule: 12.2.2
    """Semantic constraints the schema cannot express."""
    errs: list[str] = []
    classes = [p.get("class") for p in data.get("parts", [])]
    if "PENDING_ANSWER" in classes and not data.get("pending_answer"):
        errs.append("a PENDING_ANSWER part needs pending_answer set to the open pause's choice id")
    for i, b in enumerate(data.get("beats", [])):
        if b.get("gate") == "G2" and b.get("license") in (None, NONE):
            errs.append(f"beats[{i}]: gate G2 must cite a held licence id (else G1 or G3)")
    return errs


def read_message(ctx: TurnContext, message: str, *, exchanges: Sequence[Any] = ()) -> ReaderResult:
    # rule: 12.2.2
    """One Reader call: classify the message's parts and propose its beats and fact questions."""
    st = ctx.state
    sctx = schema_context(st, ctx.rules, message=message)
    schema = build_schema(Role.READER, sctx)
    triggers = get_active_triggers(st, ctx.rules)
    mode = st.scene.mode if st.scene else None
    cards = load_cards_for(Role.READER, scene_situation_tags(st, ctx.rules), mode, triggers, rules=ctx.rules)
    packet = build_packet(Role.READER, instructions=load_prompt("reader"), cards=cards, view=st,
                          exchanges=list(exchanges), message=message, triggers=triggers, rules=ctx.rules)
    res = call_role(ctx.model, Role.READER, schema, packet, turn_id=ctx.turn_id, recorder=ctx.record_call,
                    default=lambda: defaults(Role.READER, sctx) or {}, check=reader_check)
    data = dict(res.data)
    out = ReaderResult(
        parts=[Part.model_validate(p) for p in data.get("parts", [])],
        pending_answer=data.get("pending_answer"),
        fact_questions=[FactQuestion.model_validate(q) for q in data.get("fact_questions", [])],
        beats=[ReaderBeat.model_validate(b) for b in data.get("beats", [])],
        clarifying_question=data.get("clarifying_question"),
        restatement=data.get("restatement") or "",
        player_quantity=data.get("player_quantity"),
        defaulted=res.defaulted,
    )
    from engine.world.common import active_pc

    _knowledge_parts(out, active_pc(st))
    return out
