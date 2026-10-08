"""The Narrator role (B draft, D redraft; contracts/model-calls.md B): turns the adjudication record into fiction plus
the new elements it mentions. It decides nothing.

    out = draft(ctx, record, player_message="I slip past the watch.", exchanges=recent)
    out.fiction, out.mentions          # mentions go to engine.dm.mentions.write_mentions (T8)
    out = draft(ctx, record, player_message=..., redraft=Redraft(previous=sentences, failures=[...]))   # D

THIS MESSAGE carries the player's words, the adjudication record (rendered in words by `record_text`), and for a
redraft the failing verdicts with the store's values (lead decision). The view is the narrator view
(`engine.dm.packet.scene_view`): nothing sealed reaches this role (INV-10).
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from typing import Any, Literal

from pydantic import BaseModel, Field

from engine.dm.adjudication import AdjudicationRecord, BeatEntry
from engine.dm.context import TurnContext
from engine.dm.packet import build_packet, scene_setting
from engine.dm.player_text import clean
from engine.dm.roles.prompts import load_prompt
from engine.dm.schemas import build_schema, schema_context
from engine.llm.base import Role, call_role
from engine.retrieve.anchors import scene_situation_tags
from engine.retrieve.cards import load_cards_for
from engine.retrieve.triggers import get_active_triggers
from engine.store.projection import WorldState

Purpose = Literal["turn", "scene_open", "opening", "recap", "epilogue"]
# 12.14.10 (pacing.yaml#narration): the word limit each purpose states in THIS MESSAGE
LIMIT_KEYS: dict[str, str] = {"turn": "beat_max_words", "scene_open": "scene_open_max_words",
                              "opening": "scene_open_max_words", "recap": "recap_max_words",
                              "epilogue": "beat_max_words"}
PURPOSE_LINES: dict[str, str] = {
    "turn": "Narrate this turn from the record.",
    "scene_open": "Frame the new scene (12.4.3): the moment, the one impetus the record names, the open prompt.",
    "opening": "The first opening (12.16.16): the inciting incident from the record, at a moment of decision.",
    "recap": "A recap (12.5.3) from the state summary below only, never from earlier prose.",
    "epilogue": "The epilogue (PR-11-6): word only what the record gives.",
}
DEGREE_WORDS = {"critical_success": "critical success (better than hoped)", "success": "success",
                "failure": "failure (the world answers)", "critical_failure": "critical failure (it goes badly)"}


class Redraft(BaseModel):
    """What a redraft (D) is told: the previous draft's sentences and what failed, with the store's values."""

    previous: list[str] = Field(default_factory=list)
    failures: list[str] = Field(default_factory=list)  # one line per failing verdict or screen reason
    settled: list[str] = Field(default_factory=list)  # T8/T9 answers to write to ("the door: locked")


class NarratorDraft(BaseModel):
    fiction: str = ""
    mentions: list[dict[str, Any]] = Field(default_factory=list)
    call_id: str | None = None


def name_of(state: WorldState, eid: str | None, pc: str | None = None) -> str:
    """A narrator-safe name: "you" for the PC, a sealed entity's slice or "someone"."""
    if not eid:
        return "someone"
    if eid == pc:
        return "you"
    e = state.entities.get(eid)
    if e is None:
        return "someone"
    seal = state.seals.get(eid)
    if seal is not None:
        return str(seal.slice) if seal.slice else "someone"
    return e.name


def _beat_line(state: WorldState, b: BeatEntry, pc: str | None, paused: bool = False,
               rules: Any = None) -> str:  # rule: 12.14.12
    # an aside in brackets ("(Her claim ... is context only.)") is the Framer's note, not something to narrate
    restated = re.sub(r"\s*\([^()]*\)", "", b.restatement).strip().rstrip(".")
    bits = [f"beat: {restated}"]
    if b.approach_words:
        bits.append(f"approach: {b.approach_words}")
    if b.difficulty_words:
        bits.append(f"difficulty: {b.difficulty_words}")
    if b.degree:
        res = DEGREE_WORDS.get(b.degree, b.degree.replace("_", " "))
        if b.near_miss and not b.success_at_cost:
            res += ", a near miss"
        if b.success_at_cost:
            res = "success at cost (it works, and the cost is paid)"
        bits.append(f"result: {res}")
    elif b.gate_words.startswith("no roll"):
        bits.append(b.gate_words)
    elif b.gate_words:  # refused, withdrawn or redirected: it did not happen (never narrate it as done)
        bits.append(f"not done: {b.gate_words}")
    elif paused:
        bits.append("not resolved yet: the turn waits at the pause before it")
    words = [w for w in (clean(x, rules) for x in b.reach_words) if not re.search(r"\d", w)]  # 12.14.4
    if words:  # the reach rung, then the anchor's ladder line for it in words (the rung alone says nothing new)
        bits.append(f"delivered: {b.reach or 'as far as it goes'}: " + "; ".join(words))
    for c in b.costs:
        bits.append(f"cost paid: {c.form or c.menu_id.removeprefix('cost.').replace('_', ' ')}")
    for h in b.harm:
        bits.append(f"harm to {name_of(state, h.target, pc)}: {h.words}")
    if b.conditions:
        bits.append("visible conditions: " + "; ".join(b.conditions))
    for p in b.positions:
        bits.append(f"position: {name_of(state, p.entity, pc)} {p.words}")
    if b.targets:
        bits.append("acting on: " + ", ".join(name_of(state, t, pc) for t in b.targets))
    if b.learned:  # 12.10.5: what the success delivered; the PC is told or sees it, so the fiction names it
        bits.append("the PC learns (say it plainly in the fiction): " + "; ".join(b.learned))
    return "- " + "; ".join(x for x in bits if x)


def record_text(state: WorldState, record: AdjudicationRecord, *, player_message: str = "",
                purpose: Purpose = "turn", rules: Any = None) -> str:  # rule: 12.14.12
    """The adjudication record in words for THIS MESSAGE (names, never ids or numbers; 12.14.4)."""
    pc = record.pc
    lines = [PURPOSE_LINES[purpose]]
    if rules is not None:
        limit = rules.pacing.get("narration", {}).get(LIMIT_KEYS[purpose])
        if limit:
            lines.append(f"Length: at most {limit} words of fiction.")
    if player_message:
        lines.append(f'THE PLAYER\'S MESSAGE: "{player_message}"')
    lines.append("ADJUDICATION RECORD (narrate exactly this, no better and no worse):")
    for p in record.parts:
        lines.append(f"- part [{p.cls}] \"{p.text}\"" + (f" ({p.handled})" if p.handled else ""))
    if record.scene.ended and not record.scene.started:
        lines.append("- the scene ends here")
    if record.scene.started:
        lines.append(f"- a new scene opens: {record.scene.header or 'framed now'}; frame it first (12.4.3)")
    last = len(record.beats) - 1
    lines += [_beat_line(state, b, pc, paused=record.pause is not None and i == last and not b.degree, rules=rules)
              for i, b in enumerate(record.beats)]
    for o in record.oracle:
        lines.append(f"- question \"{o.question}\": the answer is {o.answer}")
    for a in record.npc_actions:
        lines.append(f"- {name_of(state, a.npc, pc)} acts: {a.action}")
    for om in record.omens:
        if om.omen:
            lines.append(f"- an omen to show as a trace, never explained: {om.omen}")
    for n in record.notes:
        if n.lstrip().startswith("[WARNING"):
            lines.append("- the engine shows a lethal warning: make the danger plain in the fiction")
        elif not n.startswith(("session move", "safety:", "queued for")):
            lines.append(f"- note: {n}")
    if record.pause is not None:
        lines.append(f"- the turn stops at a pause ({record.pause.kind}): stop at the moment before it; the "
                     "engine adds the block")
    elif purpose == "turn":
        lines.append("- end by handing the moment back (12.14.9)")
    return "\n".join(lines)


def redraft_text(r: Redraft) -> str:  # rule: 12.3.3
    lines = ["A REDRAFT. The previous draft, sentences numbered from 0:"]
    lines += [f"[{i}] {s}" for i, s in enumerate(r.previous)]
    if r.failures:
        lines.append("FAILING VERDICTS (each claim with its fix; repair exactly these):")
        lines += [f"- {f}" for f in r.failures]
        lines.append("Keep every other sentence exactly as written, atmosphere included. Do not shorten the "
                     "passage, and do not drop detail that passed.")
    if r.settled:
        lines.append("SETTLED NOW (write to these answers):")
        lines += [f"- {s}" for s in r.settled]
    return "\n".join(lines)


def draft(ctx: TurnContext, record: AdjudicationRecord, *, player_message: str = "",
          exchanges: Sequence[str | tuple[str, str]] = (), purpose: Purpose = "turn",
          redraft: Redraft | None = None, extra: Sequence[str] = ()) -> NarratorDraft:  # rule: PR-12-1
    """One Narrator call (T7, or D with `redraft`). `extra`: lines appended to THIS MESSAGE (a recap's state
    summary). Raises ModelInvalid when two answers fail the schema (the caller falls back, 12.3.3)."""
    st = ctx.state
    sctx = schema_context(st, ctx.rules)
    schema = build_schema(Role.NARRATOR, sctx)
    triggers = get_active_triggers(st, ctx.rules)
    mode = st.scene.mode if st.scene else None
    cards = load_cards_for(Role.NARRATOR, scene_situation_tags(st, ctx.rules), mode, triggers, rules=ctx.rules)
    msg = [record_text(st, record, player_message=player_message, purpose=purpose, rules=ctx.rules)]
    if purpose in ("turn", "scene_open", "opening") and (setting := scene_setting(st)):
        msg.append(setting)
    msg.extend(extra)
    if redraft is not None:
        msg.append(redraft_text(redraft))
    packet = build_packet(Role.NARRATOR, instructions=load_prompt("narrator"), cards=cards, view=st,
                          exchanges=list(exchanges), message="\n".join(msg), triggers=triggers, rules=ctx.rules)
    res = call_role(ctx.model, Role.NARRATOR, schema, packet, turn_id=ctx.turn_id, recorder=ctx.record_call)
    data = dict(res.data)
    return NarratorDraft(fiction=str(data.get("fiction") or "").strip(), mentions=list(data.get("mentions") or []),
                         call_id=res.record.call_id)


__all__ = ["NarratorDraft", "Purpose", "Redraft", "draft", "name_of", "record_text", "redraft_text"]
