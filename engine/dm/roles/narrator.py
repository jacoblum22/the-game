"""The Narrator role (B draft, D revision; contracts/model-calls.md B): turns the adjudication record into one passage
of fiction plus its side list (speech, new elements, the record lines it covers; 12.3.1). It decides nothing.

    out = draft(ctx, record, player_message="I slip past the watch.", exchanges=recent)
    out.passage.text, out.passage.speech, out.passage.covers
    out = draft(ctx, record, player_message=..., revision=Revision(draft=text, failed=[...]))   # D, 12.3.3

THIS MESSAGE carries the player's words, the adjudication record (rendered in words by `record_text`), and for the
one revision the whole draft with what failed and the store's values. The view is the narrator view
(`engine.dm.packet.scene_view`): nothing sealed reaches this role (INV-10).
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from typing import Any, Literal

from pydantic import BaseModel, Field

from engine.audit.declare import Passage, parse_output
from engine.dm.adjudication import AdjudicationRecord, BeatEntry, effective_degree, paused_beat
from engine.dm.context import TurnContext
from engine.dm.handles import AGREED, RecordItem
from engine.dm.handles import items as handle_items
from engine.dm.packet import build_packet, own_words, pronoun_words, scene_setting, view_ctx, view_for
from engine.dm.player_text import clean
from engine.dm.roles.prompts import load_prompt
from engine.dm.schemas import build_schema, schema_context
from engine.llm.base import Role, call_role
from engine.retrieve.anchors import scene_situation_tags
from engine.retrieve.cards import load_cards_for
from engine.retrieve.triggers import get_active_triggers
from engine.store.projection import WorldState
from engine.text.render import clause

Purpose = Literal["turn", "scene_open", "opening", "recap", "epilogue"]
# 12.14.10 (pacing.yaml#narration): the word limit each purpose states in THIS MESSAGE
LIMIT_KEYS: dict[str, str] = {"turn": "beat_max_words", "scene_open": "scene_open_max_words",
                              "opening": "scene_open_max_words", "recap": "recap_max_words",
                              "epilogue": "beat_max_words"}
PURPOSE_LINES: dict[str, str] = {
    "turn": "Narrate this turn from the record.",
    "scene_open": "Narrate this turn from the record, then frame the new scene it reaches (12.4.3): the way there in "
                  "a line, the arrival and the place from SCENE SETTING, any impetus the record names, the open "
                  "prompt.",
    "opening": "The first opening (12.16.16): the inciting incident from the record, at a moment of decision.",
    "recap": "A recap (12.5.3) from the state summary below only, never from earlier prose.",
    "epilogue": "The epilogue (PR-11-6): word only what the record gives.",
}
DEGREE_WORDS = {"critical_success": "critical success (better than hoped)", "success": "success",
                "failure": "failure (the world answers)", "critical_failure": "critical failure (it goes badly)"}


class Revision(BaseModel):
    """The one revision (12.3.3): the whole draft and each failure in words, with the store's value to use."""

    draft: str
    failed: list[str] = Field(default_factory=list)


class NarratorDraft(BaseModel):
    passage: Passage = Field(default_factory=Passage)
    call_id: str | None = None

    @property
    def fiction(self) -> str:
        return self.passage.text


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
    it delivered are lines of their own, each with a handle). A beat the open pause holds (`paused`: an OFFER, a
    redirect, a near-miss choice) is unresolved: no degree, no "near miss", no result words (12.2.6; DL-12-115)."""
    # an aside in brackets ("(Her claim ... is context only.)") is the Framer's note, not something to narrate
    restated = re.sub(r"\s*\([^()]*\)", "", b.restatement).strip().rstrip(".")
    bits = [f"beat: {restated}"]
    if b.approach_words:
        bits.append(f"approach: {b.approach_words}")
    if b.difficulty_words:
        bits.append(f"difficulty: {b.difficulty_words}")
    if paused:
        bits.append("not resolved yet: the player chooses next, so narrate up to the moment before its outcome and "
                    "never the outcome (neither that it works nor that it fails)")
    elif b.degree:
        res = DEGREE_WORDS.get(b.degree, b.degree.replace("_", " "))
        if b.near_miss and not b.success_at_cost:
            res += ", a near miss"  # after the choice (the default failure), never before it
        if b.success_at_cost:
            res = "success at cost (it works, and the cost is paid)"
        bits.append(f"result: {res}")
    elif b.gate_words.startswith("no roll"):
        bits.append(b.gate_words)
    elif b.gate_words:  # refused, withdrawn or redirected: it did not happen (never narrate it as done)
        bits.append(f"not done: {b.gate_words}")
    words = [w for w in (clean(x, rules) for x in b.reach_words) if not re.search(r"\d", w)]  # 12.14.4
    if words and not paused:  # the reach rung, then the anchor's ladder line for it in words
        bits.append(f"delivered: {b.reach or 'as far as it goes'}: " + "; ".join(words))
    if b.targets:
        bits.append("acting on: " + ", ".join(name_of(state, t, pc) for t in b.targets))
    if "verb.talk" in b.approach_words and b.targets and not paused \
            and effective_degree(b) in ("success", "critical_success"):  # P-120, T-15-5; DL-01-48
        bits.append("it worked: the one asked answers what was asked (never a refusal, a dodge or 'not now')")
    if b.progress:
        bits.append(b.progress)
    return "- " + "; ".join(x for x in bits if x)


def _withheld(state: WorldState, npc: str, action: str, pc: str | None) -> str:  # rule: 12.11.5
    """For an NPC who refuses: tell the narration to make that legible in the fiction, with the reason the record
    holds (the act itself, their manner, their standing), so the player knows to move on (P-056). Only on a refusal
    (P4): a row that answers in its own way (carries on, wants something first) is voiced as its line says."""
    if not action.startswith("refuses") or npc not in state.entities:
        return ""
    from engine.world.social import _RUNGS, standing

    d = state.entities[npc].data
    st = standing(state, npc)
    rung = {v: k for k, v in _RUNGS.items()}.get(st) if st is not None else None
    why = [x for x in (f"manner: {d['demeanor']}" if d.get("demeanor") else "",
                       f"standing toward the PC: {rung}" if rung else "") if x]
    return ("; the PC does not get what was asked: show it plainly and visibly (a word, a shake of the head, a "
            "hand lifted for not now, a turn back to other business) so the player knows not to wait for an "
            "answer" + (f"; the reason shows only from this, never a secret: {'; '.join(why)}" if why else ""))


def _speech_line(state: WorldState, record: AdjudicationRecord) -> list[str]:  # rule: 12.10.8
    # rule: 12.14.12
    """When the PC speaks to someone here, the one they addressed answers in quoted words (P-061), in character,
    within the willingness code gave, from their speaker card first (PR-12-10 steps 3-4; DL-12-90): beyond it,
    plainly, with ordinary confidence (a hedge only for a cautious or gossipy character; DL-12-96), never opening on
    their own name or title unless asked (DL-12-100); "I don't know" rare, in voice, with a natural redirect; never contradicting or
    repeating their own `said` lines unprompted. Nobody else interjects (12.11.9 step 3)."""
    from engine.dm.roles.world import present_npcs

    present = present_npcs(state)
    held = [b for n, b in enumerate(record.beats) if paused_beat(record, n)]
    waiting = [t for b in held for t in b.targets if t in present]
    spoke = any(p.cls == "SPEECH" for p in record.parts) or any(
        "talk" in (b.approach_words or "") for b in record.beats if b not in held)
    if not present or not (spoke or record.npc_actions or waiting):
        return []
    # a paused ask is unresolved (12.2.6; DL-12-115): its target has not answered it yet (round 7, talker input 27:
    # "I'll not say no to it" before the near-miss choice)
    who = ", ".join(name_of(state, t, record.pc) for t in dict.fromkeys(waiting))
    asks = ", ".join(re.sub(r"\s*\([^()]*\)", "", b.restatement).strip() for b in held)
    pending = (f"{who} has not answered what the paused beat asks ({asks}) yet: the turn stops before that answer, "
               "which waits on the player's choice") if waiting else ""
    if not (spoke or record.npc_actions):
        return [f"- {pending}"]
    return ["- the one the PC addressed answers in quoted words (their actual sentence, a question as a question), in "
            "character and within the willingness their line gives: from their SPEAKER CARD first; beyond it, plainly and "
            "with ordinary confidence, as people talk about ordinary things; a hedge only if the character is cautious "
            "or gossipy. Never open their speech by saying their own name or title unless they were asked who they "
            "are. \"I don't know\" is "
            "rare: only in their own voice, with a natural redirect, never a chain of names. Never contradict or "
            "repeat what their card says they already said (build on it; say something new). A refusal is said in "
            "their own voice, never a stock formula. Nobody else present speaks or interjects unless the optional "
            "material gives them a reaction. Never write that their words are lost, unheard, or only begun"
            + (f". Except: {pending}" if pending else "; never end on waiting for them to speak")]


def speaker_cards(state: WorldState, record: AdjudicationRecord, rules: Any = None) -> list[str]:  # rule: PR-12-10
    """One speaker card per NPC answering this turn (their PR-12-10 line), topic from its `ask:` index key, then what
    others have said on that topic (PR-12-12's guard)."""
    from engine.dm.packet import speaker_card
    from engine.dm.testimony import said_by_others

    out: list[str] = []
    seen: set[str] = set()
    for a in record.npc_actions:
        if a.source_ref != "PR-12-10" or a.npc in seen:
            continue
        seen.add(a.npc)
        key = next((t.removeprefix("ask:") for t in a.tags if t.startswith("ask:")), "")
        topic = key.rsplit("|", 1)[-1] if key else None
        about = topic if topic in state.entities else None
        out += speaker_card(state, a.npc, topic=None if about else topic, about=about, rules=rules)
        others = said_by_others(state, a.npc, topic=None if about else topic, about=about)
        if others:  # PR-12-12's guard (DL-12-109): improvised details agree, or differ knowingly
            out.append("- others have said on this (testimony, not fact; agree with it or knowingly differ, never "
                       "repeat it word for word):")
            out += [f"  - {name_of(state, r['speaker'])}: \"{r['words']}\"" for r in others]
    return out


_POSTED = re.compile(r"\b(notice|bill|board|sign|signboard|placard|poster|plaque|inscription|letter|note|scroll|"
                     r"proclamation|broadsheet|writ|tablet|marker|milestone|headstone)s?\b", re.I)


_UNREAD = ("never quote or paraphrase written words as read by the character; writing shows only as marks they "
           "cannot read, and its news reaches them only when someone in the record reads it aloud (then as speech)")
# READING without "what did they say" (people, not writing): enough on its own when one written thing is in view
_READ_VERB = re.compile(r"\b(read|reads|reading|wording|inscription|lettering|what (?:does|do|did) it say|what it says|"
                        r"what's written|what is written)\b", re.I)
# "what did the ferry notice say?": READING's `the \w+` takes one word; with a written thing named, this counts
_SAYS = re.compile(r"\bwhat (?:does|do|did)\b[^?.!]*\bsay\b", re.I)


def _either(things: Sequence[str]) -> str:
    """"the hire notice", "the hire notice or the bounty notice", "the hire notice, the list or any posted notice"."""
    return things[0] if len(things) == 1 else ", ".join(things[:-1]) + " or " + things[-1]


def _reading_lines(state: WorldState, record: AdjudicationRecord, player_message: str) -> list[str]:  # rule: 12.14.13
    """When the PC reads posted words, the narrator is told what they say (the stored text, else the opening's lead
    the notice carries, else ordinary words to write on mention), or plainly why the PC cannot read them (P-110).
    On any turn with writing in view, a PC who cannot read is never shown its words."""
    from engine.retrieve.scene import READING, cannot_read, scene_scope, written_words

    things = [i for i in scene_scope(state) if state.entities[i].kind in ("object", "item")
              and (written_words(state, i) is not None or _POSTED.search(state.entities[i].name or ""))]
    asked = " ".join([player_message] + [b.restatement for b in record.beats])
    hits = {i: sum(w in asked.lower() for w in re.findall(r"[a-z]{3,}", (state.entities[i].name or "").lower()))
            for i in things}
    named = [i for i in things if hits[i] and hits[i] == max(hits.values())]  # "the ferry notice", not every notice
    named += [t for b in record.beats for t in b.targets if t in things and t not in named]
    # P5: reading needs a written thing named or acted on, or a plain "read it" with one in view; "what did they say"
    # about people is not reading (round 7, talker turn.4: both notices quoted for a question to the captain)
    picked = named or (things[:1] if len(things) == 1 and _READ_VERB.search(asked) else [])
    if not ((READING.search(asked) or _SAYS.search(asked)) and picked):
        lead = any(n.startswith(("a lead to make noticeable", "a lead arrives")) for n in record.notes)
        unread = [f"the {state.entities[i].name}" for i in things if cannot_read(state, record.pc, i)]
        if lead and cannot_read(state, record.pc, None):
            unread.append("any posted notice")
        return [f"- the character cannot read {_either(unread)}: {_UNREAD}"] if unread else []
    failed = {t for b in record.beats if effective_degree(b) in ("failure", "critical_failure") for t in b.targets}
    lines: list[str] = []
    for eid in picked[:2]:
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


_LEAD_NOTE = "a lead to make noticeable:"  # the opening's lead notes (engine/dm/session.py)

# a scene-state line's slot in the Narrator's words (T-12-18)
_STATE_WORDS = {"activity": "what they are doing", "posture": "their posture", "held": "what they hold",
                "manner": "their manner", "position": "their range to you"}


def record_items(state: WorldState, record: AdjudicationRecord) -> list[RecordItem]:  # rule: 12.14.12
    return handle_items(record, names=names_for(state))


def _item_words(state: WorldState, record: AdjudicationRecord, it: RecordItem, rules: Any) -> str:
    # rule: 12.14.12
    """One record line in words for the Narrator (names, never ids or numbers; 12.14.4)."""
    pc = record.pc
    if it.kind == "scene" and record.scene.cut:  # travel: the beats above led here (P-098)
        return f"a new scene opens: {record.scene.header or 'framed now'}; frame it as the arrival the beats above " \
               "led to (12.4.3)"
    if it.kind == "scene":
        return f"a new scene opens: {record.scene.header or 'framed now'}; frame it first (12.4.3)"
    if it.kind == "beat" and it.beat is not None:
        b = record.beats[it.beat]
        return _beat_line(state, b, pc, paused=paused_beat(record, it.beat), rules=rules).removeprefix("- ")
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
        return f"the PC learns: {it.text}"
    if it.kind == "change" and b is not None:  # 01.2.7 item 3: the state the change wrote, never a line to repeat
        if b.change_refused:
            return f"this did not change: {it.text}"
        agreed = AGREED.match(it.text)
        return f"{agreed.group(1)} agrees to what was asked" if agreed else f"now so: {it.text}"
    if it.kind == "oracle":
        o = record.oracle[it.index]
        return f"question \"{o.question}\": the answer is {o.answer}"
    if it.kind == "npc":
        a = record.npc_actions[it.index]
        act = own_words(a.action, pronoun_words(state, a.npc))  # a table row's "their" in their pronouns
        return f"{name_of(state, a.npc, pc)} acts: {act}" + _withheld(state, a.npc, a.action, pc)
    if it.kind == "activity":
        a = record.activities[it.index]
        said = clause(name_of(state, a.npc, pc), "hold" if a.slot == "held" else "be",
                      own_words(a.activity, pronoun_words(state, a.npc)))
        return f"{said} ({_STATE_WORDS.get(a.slot, a.slot)} now; say only this of it, never otherwise)"
    if it.kind == "omen":
        return f"an omen to show as a trace, never explained: {it.text}"
    if it.text.startswith(_LEAD_NOTE):  # a seeded lead is its gist, never a sentence to recite (DL-12-114)
        return f"note: {_LEAD_NOTE[:-1]} (its gist, in your own words or a speaker's):{it.text[len(_LEAD_NOTE):]}"
    return f"note: {it.text}"


def optional_material(state: WorldState, record: AdjudicationRecord) -> list[str]:  # rule: 12.14.12
    # rule: 12.11.9
    """12.14.12's optional material: present people's scene state (activity, posture, hold, manner, range) and the
    reactions of NPCs the PC did not address (tagged `optional`). No handles: the narrator may use any of it or none,
    and no check requires it (DL-12-92). An unchanged line need not be said again (12.14.11)."""
    from engine.dm.handles import OPTIONAL

    pc = record.pc
    lines = [clause(name_of(state, a.npc, pc), "hold" if a.slot == "held" else "be",
                    own_words(a.activity, pronoun_words(state, a.npc))) for a in record.activities if a.npc != pc]
    lines += [f"{name_of(state, a.npc, pc)}, not addressed: {own_words(a.action, pronoun_words(state, a.npc))} (a "
              "brief deed at most; no words unless it says so)" for a in record.npc_actions if OPTIONAL in a.tags]
    if not lines:
        return []
    return ["OPTIONAL MATERIAL (use any of it, all of it or none; nothing requires it; an unchanged line need not be "
            "said again; never cite these):", *(f"- {x}" for x in lines)]


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
    lines.append("ADJUDICATION RECORD (narrate exactly this, no better and no worse; list each line you narrate by its "
                 "handle in `covers`; narrate every line marked MUST):")
    for p in record.parts:
        lines.append(f"- part [{p.cls}] \"{p.text}\"" + (f" ({p.handled})" if p.handled else ""))
    if record.scene.ended and not record.scene.started:
        lines.append("- the scene ends here")
    its = items if items is not None else record_items(state, record)
    for it in its:
        lines.append(f"- {it.handle}{' MUST' if it.must_name else ''}: {_item_words(state, record, it, rules)}")
    lines += _speech_line(state, record)
    lines += speaker_cards(state, record, rules)
    lines += optional_material(state, record)
    lines += _reading_lines(state, record, player_message)
    if any(n.lstrip().startswith("[WARNING") for n in record.notes):
        lines.append("- the engine shows a lethal warning: make the danger plain in the fiction")
    if record.pause is not None:
        lines.append(f"- the turn stops at a pause ({record.pause.kind}): stop at the moment before it; the "
                     "engine adds the block")
    elif purpose == "turn":
        lines.append("- end by handing the moment back (12.14.9)")
    return "\n".join(lines)


def revision_text(r: Revision) -> str:  # rule: 12.3.3
    """THIS MESSAGE's revision section: the whole draft, then each failure in words."""
    return "\n".join(["A REVISION. Your draft is below, then what failed. Write the whole passage and its side list "
                      "again: fix exactly what is named and keep the rest as you wrote it (its voice, detail and "
                      "length). Never shorten or play safe.", "YOUR DRAFT:", r.draft, "WHAT FAILED:",
                      *(f"- {x}" for x in r.failed)])


# the PC looks again or asks (12.14.11 setting once): the place's look is given again
LOOKS_AROUND = re.compile(r"\blook(?:s|ing)? (?:around|about|round)\b|\bsurroundings\b|\bwhat (?:do|can) i see\b"
                          r"|\bdescribe\b|\btake in the\b", re.IGNORECASE)


def draft(ctx: TurnContext, record: AdjudicationRecord, *, player_message: str = "",
          exchanges: Sequence[str | tuple[str, str]] = (), purpose: Purpose = "turn",
          revision: Revision | None = None, extra: Sequence[str] = (),
          items: Sequence[RecordItem] | None = None) -> NarratorDraft:  # rule: PR-12-1
    # rule: 12.3.1
    """One Narrator call (T7, or the one revision with `revision`, 12.3.3): one passage and its side list. The
    schema's `covers` are this turn's record handles, `speech` speakers the people present (closed lists built from
    the packet). `extra`: lines appended to THIS MESSAGE (a recap's state summary). Raises ModelInvalid when two
    answers fail the schema (the caller falls back, 12.3.3)."""
    st = ctx.state
    its = list(items) if items is not None else record_items(st, record)
    triggers = get_active_triggers(st, ctx.rules)
    mode = st.scene.mode if st.scene else None
    cards = load_cards_for(Role.NARRATOR, scene_situation_tags(st, ctx.rules), mode, triggers, rules=ctx.rules)
    msg = [record_text(st, record, player_message=player_message, purpose=purpose, rules=ctx.rules, items=its)]
    full = purpose != "turn" or bool(LOOKS_AROUND.search(player_message))  # setting once (DL-12-99)
    if purpose in ("turn", "scene_open", "opening") and (setting := scene_setting(st, full=full)):
        msg.append(setting)
    msg.extend(extra)
    if revision is not None:  # the same packet, plus the whole draft and what failed (12.3.3)
        msg.append(revision_text(revision))
    message = "\n".join(msg)
    # the enums come from this packet (its record handles, the people present), so nothing outside it can be cited
    view = view_for(Role.NARRATOR, st, view_ctx(message, exchanges, plain=False))
    sctx = schema_context(st, ctx.rules).model_copy(update={"narrator_refs": [it.handle for it in its]})
    schema = build_schema(Role.NARRATOR, sctx)
    packet = build_packet(Role.NARRATOR, instructions=load_prompt("narrator"), cards=cards, view=view,
                          exchanges=list(exchanges), message=message, triggers=triggers, rules=ctx.rules)
    res = call_role(ctx.model, Role.NARRATOR, schema, packet, turn_id=ctx.turn_id, recorder=ctx.record_call)
    p = parse_output(dict(res.data))
    return NarratorDraft(passage=p.model_copy(update={"covers": [c for c in p.covers if c in sctx.narrator_refs]}),
                         call_id=res.record.call_id)


__all__ = ["NarratorDraft", "Purpose", "Revision", "draft", "name_of", "names_for",
           "record_items", "record_text", "revision_text"]
