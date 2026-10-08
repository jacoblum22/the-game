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

from engine.audit.declare import DeclaredSentence, parse_output
from engine.dm.adjudication import AdjudicationRecord, BeatEntry
from engine.dm.context import TurnContext
from engine.dm.handles import RecordItem
from engine.dm.handles import items as handle_items
from engine.dm.packet import build_packet, scene_setting, view_ctx, view_for
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


class Repair(BaseModel):
    """A narrow redraft (12.3.3): only the failing sentences, each with its failure and the store's value to use,
    plus the must-name lines no sentence cites."""

    failing: dict[str, str] = Field(default_factory=dict)  # sentence index -> its text
    reasons: dict[str, list[str]] = Field(default_factory=dict)  # sentence index -> "why; use: value" lines
    missing: list[str] = Field(default_factory=list)  # "R2" handles, or "answer: <the player's question>"


class NarratorDraft(BaseModel):
    sentences: list[DeclaredSentence] = Field(default_factory=list)
    repairs: list[tuple[str, DeclaredSentence]] = Field(default_factory=list)  # (replaces, sentence) for a repair
    call_id: str | None = None

    @property
    def fiction(self) -> str:
        return " ".join(s.text for s in self.sentences)


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
    """The beat's own record line: what was tried and its result (its costs, harm, conditions, positions and what
    it delivered are lines of their own, each with a handle)."""
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
    if b.targets:
        bits.append("acting on: " + ", ".join(name_of(state, t, pc) for t in b.targets))
    if "verb.talk" in b.approach_words and b.targets and (b.degree in ("success", "critical_success")
                                                          or b.success_at_cost):  # P-120, T-15-5
        bits.append("it worked: the one asked answers what was asked (never a refusal, a dodge or 'not now')")
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
            + "; or they say plainly they do not know, or (only after a failed Talk or a recorded refusal) will not "
            "say. Never write that their words are lost, "
            "unheard, or only begun; never end on waiting for them to speak"]


_POSTED = re.compile(r"\b(notice|bill|board|sign|signboard|placard|poster|plaque|inscription|letter|note|scroll|"
                     r"proclamation|broadsheet|writ|tablet|marker|milestone|headstone)s?\b", re.I)


_UNREAD = ("never quote or paraphrase written words as read by the character; writing shows only as marks they "
           "cannot read, and its news reaches them only when someone in the record reads it aloud (then as speech)")


def _reading_lines(state: WorldState, record: AdjudicationRecord, player_message: str) -> list[str]:  # rule: 12.14.13
    """When the PC reads posted words, the narrator is told what they say (the stored text, else the opening's lead
    the notice carries, else ordinary words to write on mention), or plainly why the PC cannot read them (P-110).
    On any turn with writing in view, a PC who cannot read is never shown its words."""
    from engine.retrieve.scene import READING, cannot_read, scene_scope, written_words

    things = [i for i in scene_scope(state) if state.entities[i].kind in ("object", "item")
              and (written_words(state, i) is not None or _POSTED.search(state.entities[i].name or ""))]
    asked = " ".join([player_message] + [b.restatement for b in record.beats])
    if not READING.search(asked):
        lead = any(n.startswith(("a lead to make noticeable", "a lead arrives")) for n in record.notes)
        unread = [state.entities[i].name for i in things if cannot_read(state, record.pc, i)]
        if lead and cannot_read(state, record.pc, None):
            unread.append("any posted notice")
        return [f"- the character cannot read the {', the '.join(unread)}: {_UNREAD}"] if unread else []
    named = [i for i in things if any(w in asked.lower() for w in re.findall(r"[a-z]{3,}", (state.entities[i].name
                                                                                             or "").lower()))]
    failed = {t for b in record.beats if b.degree in ("failure", "critical_failure") for t in b.targets}
    lines: list[str] = []
    for eid in (named or things)[:2]:
        name = state.entities[eid].name
        if eid in failed:
            lines.append(f"- reading the {name} failed: say plainly which words could not be made out and why "
                         "(smeared, too far, a hurried hand); never a vague 'the words will not come'")
            continue
        why = cannot_read(state, record.pc, eid)
        if why:
            lines.append(f"- the character cannot read the {name}: {why}. Say so once, in one plain sentence, and "
                         "that someone who reads could read it to them; describe only what shows without reading "
                         f"(numerals, a seal, the hand); {_UNREAD}")
            continue
        words = written_words(state, eid)
        if words is not None:
            lines.append(f"- the character reads the {name}: quote its words exactly, in quotation marks: \"{words}\"")
            continue
        op = state.meta.get("world.opening") or {}
        leads = [str(x.get("lead") or x.get("text") or "") if isinstance(x, dict) else str(x)
                 for x in op.get("leads") or []]
        leads = [x for x in leads if x and not x.startswith("the incident itself")]
        here = state.scene is not None and state.scene.place_id == (op.get("start") or {}).get("place")
        carry = (f" If it posts one of these leads, its words are that lead's: {'; '.join(leads)}." if leads and here
                 else "")
        lines.append(f"- the character reads the {name}: quote its words in quotation marks.{carry} Otherwise write "
                     "the ordinary words such a thing carries (a hiring's terms, a sale, a fair day, a shop's name) "
                     f"and list them under `mentions` for the {name} as implied `text`. Never words that point "
                     "toward anything hidden (12.14.13): then quote only what is plain and say the rest is not on it")
    return lines


def names_for(state: WorldState) -> dict[str, str]:
    """{id: name as the PC knows it} for every unsealed entity (12.10.2): what rendered lines use."""
    return {eid: name_of(state, eid) for eid in state.entities if eid not in state.seals}


def record_items(state: WorldState, record: AdjudicationRecord) -> list[RecordItem]:  # rule: 12.14.12
    return handle_items(record, names=names_for(state))


def _item_words(state: WorldState, record: AdjudicationRecord, it: RecordItem, rules: Any) -> str:
    # rule: 12.14.12
    """One record line in words for the Narrator (names, never ids or numbers; 12.14.4)."""
    pc = record.pc
    if it.kind == "scene":
        return f"a new scene opens: {record.scene.header or 'framed now'}; frame it first (12.4.3)"
    if it.kind == "beat" and it.beat is not None:
        b = record.beats[it.beat]
        paused = record.pause is not None and it.beat == len(record.beats) - 1 and not b.degree
        return _beat_line(state, b, pc, paused=paused, rules=rules).removeprefix("- ")
    b = record.beats[it.beat] if it.beat is not None else None
    if it.kind == "cost" and b is not None:
        c = b.costs[it.index]
        return f"cost paid: {c.form or c.menu_id.removeprefix('cost.').replace('_', ' ')}"
    if it.kind == "harm" and b is not None:
        h = b.harm[it.index]
        return f"harm to {name_of(state, h.target, pc)}: {h.words}"
    if it.kind == "condition":
        return f"visible condition: {it.text}"
    if it.kind == "position" and b is not None:
        p = b.positions[it.index]
        return f"position: {name_of(state, p.entity, pc)} {p.words}"
    if it.kind == "learned":  # 12.10.5: what the success delivered; the PC is told or sees it
        return f"the PC learns (say it plainly in the fiction): {it.text}"
    if it.kind == "oracle":
        o = record.oracle[it.index]
        return f"question \"{o.question}\": the answer is {o.answer}"
    if it.kind == "npc":
        a = record.npc_actions[it.index]
        return f"{name_of(state, a.npc, pc)} acts: {a.action}" + _withheld(state, a.npc, a.action, pc)
    if it.kind == "activity":
        a = record.activities[it.index]
        return f"{name_of(state, a.npc, pc)} is {a.activity} (what they are doing this scene; say only this of it)"
    if it.kind == "omen":
        return f"an omen to show as a trace, never explained: {it.text}"
    return f"note: {it.text}"


def record_text(state: WorldState, record: AdjudicationRecord, *, player_message: str = "",
                purpose: Purpose = "turn", rules: Any = None,
                items: Sequence[RecordItem] | None = None) -> str:  # rule: 12.14.12
    """The adjudication record in words for THIS MESSAGE (names, never ids or numbers; 12.14.4), one line per
    record item with its handle (`- R3 MUST: ...`), guidance lines without one."""
    lines = [PURPOSE_LINES[purpose]]
    if rules is not None:
        limit = rules.pacing.get("narration", {}).get(LIMIT_KEYS[purpose])
        if limit:
            lines.append(f"Length: at most {limit} words of fiction.")
    if player_message:
        lines.append(f'THE PLAYER\'S MESSAGE: "{player_message}"')
    lines.append("ADJUDICATION RECORD (narrate exactly this, no better and no worse; cite each line you narrate by "
                 "its handle in `refs`; every line marked MUST needs a sentence that cites it):")
    for p in record.parts:
        lines.append(f"- part [{p.cls}] \"{p.text}\"" + (f" ({p.handled})" if p.handled else ""))
    if record.scene.ended and not record.scene.started:
        lines.append("- the scene ends here")
    its = items if items is not None else record_items(state, record)
    for it in its:
        lines.append(f"- {it.handle}{' MUST' if it.must_name else ''}: {_item_words(state, record, it, rules)}")
    lines += _speech_line(state, record)
    lines += _reading_lines(state, record, player_message)
    if any(n.lstrip().startswith("[WARNING") for n in record.notes):
        lines.append("- the engine shows a lethal warning: make the danger plain in the fiction")
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
                    per_entity: int = 10, used: Sequence[tuple[str, str]] = ()) -> list[str]:  # rule: 12.14.11
    """12.14.11 in THIS MESSAGE: the details stated lately, from their `last_used` marks (`used`: (who, the detail
    in words), DL-12-76), and the backstop scan of past deliveries (oldest first; the caller passes the last
    `image_repeat_turns`): the opening clauses of the last `openings`, and each speaker's repeated speech opener.
    The image 3-gram scan is retired (spec 009 B): the marks say which details were used."""
    low = [(n, n.lower()) for n in names if len(n) > 2]
    low += [(n.split()[0], n.split()[0].lower()) for n in names  # a person by their given name ("Calbert")
            if n[:1].isupper() and len(n.split()) > 1 and len(n.split()[0]) > 2 and n.split()[0].lower() not in _STOP]
    lines = []
    firsts = [ss[0] for ss in (_sentences(d) for d in deliveries[-openings:]) if ss]
    opened = [re.split(r"[,;:.!?]", s)[0].strip() for s in firsts]
    if opened:
        lines.append("FRESHNESS (12.14.11): do not open the way these recent turns opened: "
                     + " / ".join(f'"{o}"' for o in opened))
    found: dict[str, list[str]] = {}
    for who, words in used:
        found.setdefault(who, []).append(words)
    if found:
        lines.append("Details stated lately, do not restate them (describe something else, or nothing; a deliberate "
                     "callback is fine):")
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


def repair_text(r: Repair) -> str:  # rule: 12.3.3
    """THIS MESSAGE's repair section: the failing sentences only (the rest of the draft stands and is not shown)."""
    lines = ["A REPAIR. Only these sentences failed; every other sentence of your draft stands as written. For each, "
             "write one replacement with `replaces` set to its number, fixing exactly what is named and keeping its "
             "voice and detail; an empty `text` drops it."]
    for i, text in r.failing.items():
        lines.append(f"[{i}] {text}")
        lines += [f"    - {why}" for why in r.reasons.get(i, [])]
    if r.missing:
        lines.append("MISSING (add one sentence for each, `replaces` = add, citing its handle): " + "; ".join(r.missing))
    return "\n".join(lines)


def _freshness(ctx: TurnContext) -> list[str]:  # rule: 12.14.11
    from engine.dm.turn import recent_exchanges  # turn imports this module

    cfg = (ctx.rules.pacing.get("narration") or {}).get("freshness") or {}
    window = int(cfg.get("image_repeat_turns", 10))
    past = recent_exchanges(ctx.store, ctx.turn_id or "", n=window)
    st = ctx.state
    names = [e.name for e in st.entities.values() if e.kind != "pc" and e.name and e.id not in st.seals]
    return freshness_lines([x[1] or "" for x in past], names, openings=int(cfg.get("opening_patterns_remembered", 3)),
                           per_entity=int(cfg.get("images_per_entity_remembered", 10)),
                           used=used_details(st, _turn_n(ctx.turn_id), window))


def _turn_n(turn_id: str | None) -> int:
    from engine import ids

    parsed = ids.parse_counter_id(turn_id) if turn_id else None
    return parsed[1] if parsed and parsed[0] == ids.TURN else 0


def used_details(state: WorldState, now: int, window: int = 10) -> list[tuple[str, str]]:  # rule: 12.14.11
    """(who, the detail in words) for each established detail whose `last_used` mark is within `window` turns
    before `now` (00.6.6a item 5), the scene's own first; each by the name the PC knows."""
    from engine.retrieve.scene import scene_scope
    from engine.store.projection import DETAIL

    scope = set(scene_scope(state))
    out: list[tuple[int, str, str]] = []
    for eid, refs in state.details.items():
        if eid in state.seals or eid not in state.entities:
            continue
        for slot, r in refs.items():
            f = state.facts.get(r.fact_id)
            if f is None or f.value is None or not r.last_used or not 0 <= now - r.last_used <= window:
                continue
            out.append((0 if eid in scope else 1, name_of(state, eid), f"{slot.removeprefix(DETAIL)}: {f.value}"))
    return [(who, words) for _, who, words in sorted(out, key=lambda x: x[0])]


def narrator_mode(ctx: TurnContext) -> str:
    """The output shape: declared sentences, or the fallback `fiction` + declarations (config `narrator_schema`)."""
    return "fiction" if (ctx.config or {}).get("narrator_schema") == "fiction" else "sentences"


def draft(ctx: TurnContext, record: AdjudicationRecord, *, player_message: str = "",
          exchanges: Sequence[str | tuple[str, str]] = (), purpose: Purpose = "turn",
          repair: Repair | None = None, extra: Sequence[str] = (),
          items: Sequence[RecordItem] | None = None) -> NarratorDraft:  # rule: PR-12-1
    # rule: 12.3.1
    """One Narrator call (T7, or a narrow repair with `repair`, 12.3.3). The schema's `refs` are this turn's handles
    then the view's fact ids, `about` the scene scope (closed lists built from the packet). `extra`: lines
    appended to THIS MESSAGE (a recap's state summary). Raises ModelInvalid when two answers fail the schema (the
    caller falls back, 12.3.3)."""
    st = ctx.state
    its = list(items) if items is not None else record_items(st, record)
    triggers = get_active_triggers(st, ctx.rules)
    mode = st.scene.mode if st.scene else None
    cards = load_cards_for(Role.NARRATOR, scene_situation_tags(st, ctx.rules), mode, triggers, rules=ctx.rules)
    msg = [record_text(st, record, player_message=player_message, purpose=purpose, rules=ctx.rules, items=its)]
    if repair is None:
        if purpose in ("turn", "scene_open", "opening") and (setting := scene_setting(st)):
            msg.append(setting)
        if purpose in ("turn", "scene_open"):
            msg += _freshness(ctx)
        msg.extend(extra)
    else:
        msg.append(repair_text(repair))
    message = "\n".join(msg)
    # the enums come from the view this packet shows (its facts and entities, spotlight included), so nothing
    # outside the packet can be cited (12.3.1)
    view = view_for(Role.NARRATOR, st, view_ctx(message, exchanges, plain=False))
    sctx = schema_context(st, ctx.rules)
    sctx = sctx.model_copy(update={
        "narrator_refs": [*(it.handle for it in its), *re.findall(r"(?m)^\s*(fact\.\d+) about ", view)],
        "scene_ids": list(dict.fromkeys([*sctx.scene_ids, *(i for i in re.findall(r"(?m)^([a-z]+\.[\w.]+): ", view)
                                                             if i in st.entities)])),
        "narrator_mode": narrator_mode(ctx), "repair_ids": list(repair.failing) if repair is not None else [],
        "repair": repair is not None})
    schema = build_schema(Role.NARRATOR, sctx)
    packet = build_packet(Role.NARRATOR, instructions=load_prompt("narrator"), cards=cards, view=view,
                          exchanges=list(exchanges), message=message, triggers=triggers, rules=ctx.rules)
    res = call_role(ctx.model, Role.NARRATOR, schema, packet, turn_id=ctx.turn_id, recorder=ctx.record_call)
    data = dict(res.data)
    if repair is not None:
        reps = [(str(r.get("replaces")), DeclaredSentence.model_validate(r)) for r in data.get("repairs") or []]
        return NarratorDraft(repairs=reps, call_id=res.record.call_id)
    return NarratorDraft(sentences=parse_output(data), call_id=res.record.call_id)


__all__ = ["NarratorDraft", "Purpose", "Repair", "draft", "freshness_lines", "name_of", "names_for",
           "narrator_mode", "record_items", "record_text", "repair_text"]
