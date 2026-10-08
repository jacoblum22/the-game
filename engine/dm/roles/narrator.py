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
    from engine.store.views import display_name

    return display_name(state, eid)  # 12.10.2: the descriptor until the PC learns the name


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
    if b.progress:
        bits.append(b.progress)
    return "- " + "; ".join(x for x in bits if x)


# NPC acts that leave what the PC asked unanswered (talk outcomes, refusals, wants, tbl.npc_action rows 1-6)
WITHHOLDING = ("responds as the talk went: failure", "responds as the talk went: critical_failure", "refuses",
               "acts on", "escalates", "ends the exchange", "hinders quietly", "wants something first",
               "carries on with their own business")


def _withheld(state: WorldState, npc: str, action: str, pc: str | None) -> str:  # rule: 12.11.5
    """For an NPC who does not answer: tell the narration to make that legible in the fiction, with the reason the
    record holds (the act itself, their manner, their standing), so the player knows to move on (P-056)."""
    if not action.startswith(WITHHOLDING) or npc not in state.entities:
        return ""
    from engine.world.social import _RUNGS, standing

    d = state.entities[npc].data
    st = standing(state, npc)
    rung = {v: k for k, v in _RUNGS.items()}.get(st) if st is not None else None
    why = [x for x in (f"manner: {d['demeanor']}" if d.get("demeanor") else "",
                       f"standing toward the PC: {rung}" if rung else "") if x]
    return ("; they do not give the PC what was asked: show it plainly and visibly (a word, a shake of the head, a "
            "hand lifted for not now, turning back to what they were doing) so the player knows not to wait for an "
            "answer" + (f"; the reason shows only from this, never a secret: {'; '.join(why)}" if why else ""))


def _speech_line(state: WorldState, record: AdjudicationRecord) -> list[str]:  # rule: 12.14.12
    """When the PC speaks to someone here or an NPC acts, their reply is given in quoted words (P-061): the narrator
    chooses NPCs' words, only the facts in them are constrained. What they may tell beyond what the PC learns: the
    open matters any local may know (active threads, never sealed). Never 'his words are lost'."""
    from engine.dm.oof import short_text
    from engine.dm.player_text import second_person
    from engine.dm.roles.world import present_npcs

    spoke = any(p.cls == "SPEECH" for p in record.parts) or any("talk" in (b.approach_words or "")
                                                               for b in record.beats)
    if not (spoke or record.npc_actions) or not present_npcs(state):
        return []
    matters = [second_person(short_text(str(e.data.get("text") or e.name), 160)) for e in state.entities.values()
               if e.kind == "thread" and e.data.get("status", "active") == "active"
               and e.visibility in ("shown", "available") and e.id not in state.seals][:3]
    return ["- whoever answers or acts here speaks in quoted words (their actual sentence, a question as a "
            "question): they say only what the record gives (what the PC learns, their act above)"
            + (f" or these open matters any local may know: {'; '.join(matters)}" if matters else "")
            + "; or they say plainly they do not know, or will not say. Never write that their words are lost, "
            "unheard, or only begun; never end on waiting for them to speak"]


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
        lines.append(f"- {name_of(state, a.npc, pc)} acts: {a.action}" + _withheld(state, a.npc, a.action, pc))
    lines += _speech_line(state, record)
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


_STOP = set("a an the and or but of to in on at by for with from as into onto over under up down out off is are "
            "was were be been it its it's this that these those there here then than so not no you your yours he she "
            "his her him they them their we our i me my what who how do does did has have had will would can could "
            "still just".split())


def _prose(text: str) -> str:
    """The fiction of a delivery: no block lines, their indented continuations, menu options or input hints."""
    return " ".join(ln for ln in text.splitlines()
                    if not (ln.lstrip().startswith(("[", ">", "Type a number")) or ln[:1].isspace()
                            or re.match(r"\d+\) ", ln)))


def _sentences(text: str) -> list[str]:
    prose = _prose(text)
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", prose) if s.strip()]


def freshness_lines(deliveries: Sequence[str], names: Sequence[str] = (), *, openings: int = 3,
                    per_entity: int = 10) -> list[str]:  # rule: 12.14.11
    """12.14.11 in THIS MESSAGE: the opening clauses of the last `openings` deliveries and, per entity, the
    images (runs of 3+ words with a content word) already used in two or more of `deliveries` (oldest first;
    the caller passes the last `image_repeat_turns`). Attribution: an entity named in the sentence, else the
    last one named before it in that delivery, else "the scene".
    ponytail: recurrence of word 3-grams stands in for "distinctive image"; a phrase used once is not listed."""
    seen: dict[str, set[int]] = {}
    name_words = {x for n in names for x in re.findall(r"[a-z']+", n.lower())} - _STOP
    sents = [[(s, re.findall(r"[a-z']+", s.lower())) for s in _sentences(d)] for d in deliveries]
    for k, ss in enumerate(sents):
        for _, w in ss:
            for i in range(len(w) - 2):
                g = " ".join(w[i:i + 3])
                if any(x not in _STOP and x not in name_words for x in w[i:i + 3]):
                    seen.setdefault(g, set()).add(k)
    found: dict[str, list[str]] = {}
    low = [(n, n.lower()) for n in names if len(n) > 2]
    low += [(n.split()[0], n.split()[0].lower()) for n in names  # a person by their given name ("Calbert")
            if n[:1].isupper() and len(n.split()) > 1 and len(n.split()[0]) > 2 and n.split()[0].lower() not in _STOP]
    for ss in sents:
        who = "the scene"
        for s, w in ss:
            who = next((n for n, ln in low if ln in s.lower()), who)
            hit = [i for i in range(len(w) - 2) if len(seen.get(" ".join(w[i:i + 3]), ())) > 1]
            runs: list[list[int]] = []
            for i in hit:  # merge overlapping 3-grams into one phrase ("fingers on the ledger")
                if runs and i <= runs[-1][1]:
                    runs[-1][1] = i + 3
                else:
                    runs.append([i, i + 3])
            for a, b in runs:
                while a < b and w[a] in name_words:  # the name is not the image
                    a += 1
                while a < b and w[b - 1] in name_words:
                    b -= 1
                if b - a < 3:
                    continue
                found.setdefault(who, [])
                p = " ".join(w[a:b])
                if p not in found[who]:
                    found[who].append(p)
    lines = []
    opened = [re.split(r"[,;:.!?]", ss[0][0])[0].strip() for ss in sents[-openings:] if ss]
    if opened:
        lines.append("FRESHNESS (12.14.11): do not open the way these recent turns opened: "
                     + " / ".join(f'"{o}"' for o in opened))
    if found:
        lines.append("Already used lately, do not reuse (find a new image, or none; a deliberate callback "
                     "is fine):")
        lines += [f"- {who}: " + "; ".join(ps[-per_entity:]) for who, ps in found.items()]
    spoken = _repeated_lines(deliveries, low)
    if spoken:
        lines.append("Lines these people already said lately, do not have them say again (give them new words):")
        lines += [f"- {who}: " + "; ".join(f'"{q}"' for q in qs[-per_entity:]) for who, qs in spoken.items()]
    return lines


_QUOTE = re.compile(r"[\"“]([^\"“”]+)[\"”]")


def _repeated_lines(deliveries: Sequence[str], low: Sequence[tuple[str, str]]) -> dict[str, list[str]]:
    """Per speaker, the opening words of their quoted speech ("Mark me") heard in two or more deliveries. The
    speaker is the last person named before the quote; a quote the PC says ("you say", "You ask: ...") is skipped.
    ponytail: a quote's first clause stands in for its stock line; single words ("Yes") are not listed."""
    heard: dict[tuple[str, str], set[int]] = {}
    order: list[tuple[str, str]] = []
    for k, d in enumerate(deliveries):
        prose = _prose(d)
        for m in _QUOTE.finditer(prose):
            before, after = prose[:m.start()], prose[m.end():m.end() + 30]
            clause = re.split(r"[.!?]\s", before)[-1]
            if re.match(r"\W*you\b", clause, re.I) or re.match(r"\W*you (?:say|ask|tell|call)", after, re.I):
                continue
            at, who = max(((before.lower().rfind(ln), n) for n, ln in low if n[:1].isupper()),  # a person
                          default=(-1, ""))
            lead = re.split(r"[,;:.!?—]", m.group(1))[0].strip().lower()
            if at < 0 or len(lead.split()) < 2:
                continue
            key = (who, lead)
            if key not in heard:
                order.append(key)
            heard.setdefault(key, set()).add(k)
    out: dict[str, list[str]] = {}
    for who, lead in order:
        if len(heard[(who, lead)]) > 1:
            out.setdefault(who, []).append(lead)
    return out


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


def _freshness(ctx: TurnContext) -> list[str]:  # rule: 12.14.11
    from engine.dm.turn import recent_exchanges  # turn imports this module

    cfg = (ctx.rules.pacing.get("narration") or {}).get("freshness") or {}
    past = recent_exchanges(ctx.store, ctx.turn_id or "", n=int(cfg.get("image_repeat_turns", 10)))
    st = ctx.state
    names = [e.name for e in st.entities.values() if e.kind != "pc" and e.name and e.id not in st.seals]
    return freshness_lines([x[1] or "" for x in past], names, openings=int(cfg.get("opening_patterns_remembered", 3)),
                           per_entity=int(cfg.get("images_per_entity_remembered", 10)))


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
    if purpose in ("turn", "scene_open"):
        msg += _freshness(ctx)
    msg.extend(extra)
    if redraft is not None:
        msg.append(redraft_text(redraft))
    packet = build_packet(Role.NARRATOR, instructions=load_prompt("narrator"), cards=cards, view=st,
                          exchanges=list(exchanges), message="\n".join(msg), triggers=triggers, rules=ctx.rules)
    res = call_role(ctx.model, Role.NARRATOR, schema, packet, turn_id=ctx.turn_id, recorder=ctx.record_call)
    data = dict(res.data)
    return NarratorDraft(fiction=str(data.get("fiction") or "").strip(), mentions=list(data.get("mentions") or []),
                         call_id=res.record.call_id)


__all__ = ["NarratorDraft", "Purpose", "Redraft", "draft", "freshness_lines", "name_of", "record_text", "redraft_text"]
