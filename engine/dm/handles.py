"""Record items with handles (12.14.12, 12.3.1a; spec 006 R2): one item per line of the adjudication record the
narration may cite, in `record_text` order.

    its = items(record, names={"pc.wren": "you", ...})
    its[0].handle, its[0].must_name, its[0].render      # "R1", True, "You force the hasp. It works."

Each item has a handle (`R1`, `R2`, …), whether 12.14.12 makes it must-name (coverage, 12.3.1a item 3), the
entities it concerns (the subject a citing sentence is judged against), and its **rendered line**: one plain
statement built by code from the item's typed fields (12.3.3), "" when none can be built. The Narrator's words for
each line are `engine.dm.roles.narrator.record_text`'s; the plain fallback is every must-name item's rendered line.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Literal

from pydantic import BaseModel, Field

from engine.dm.adjudication import AdjudicationRecord

Kind = Literal["scene", "beat", "cost", "harm", "condition", "position", "learned", "oracle", "npc", "activity",
               "omen", "note"]

# notes the narration must carry (12.14.12: a lead injected; the opening's incident; a repeated failed look, P-086;
# a rest taken); every other note is citable but not owed
MUST_NOTES = ("the inciting incident:", "a lead to make noticeable:", "a lead arrives", "cannot make out:",
              "the character takes ")
SKIP_NOTES = ("session move", "safety:", "queued for", "[WARNING", "oracle:", "dying check:", "testimony settled")
OPTIONAL = "optional"  # an NpcActionEntry tag: a non-addressed NPC's reaction, optional material (12.14.12)


class RecordItem(BaseModel):
    handle: str
    kind: Kind
    must_name: bool
    entities: list[str] = Field(default_factory=list)
    render: str = ""
    beat: int | None = None  # index into record.beats (beat, cost, harm, condition, position, learned)
    index: int = 0  # index into the item's own record list (costs of the beat, oracle, npc_actions, ...)
    text: str = ""  # the raw words the item carries (a note, an omen, an action, a learned line)


def _owed(b: object, paused: bool) -> bool:  # rule: 12.14.12
    """A beat the narration owes: it has a result (a degree, or "no roll"), or it simply happened (no gate words);
    not one refused, redirected or withdrawn (its block says so) and not the one a pause holds."""
    degree, gate_words = getattr(b, "degree", None), getattr(b, "gate_words", "") or ""
    return degree is not None or gate_words.startswith("no roll") or (not gate_words and not paused)


def _note_render(note: str) -> str:  # rule: 12.3.3
    from engine.audit.fallback import _sentence

    if note.startswith("cannot make out: "):
        return note.split(": ", 1)[1]
    if note.startswith("the character takes "):
        return _sentence(re.sub(r"^the character takes", "You take", note).replace(" and wakes rested",
                                                                                  " and wake rested"))
    if note.startswith("a lead arrives") and ": " in note:
        return _sentence(note.split(": ", 1)[1])
    if note.startswith(("the inciting incident:", "a lead to make noticeable:")):
        return _sentence(note.split(":", 1)[1])
    return ""


def _oracle_render(question: str, answer: str, subject: str | None, predicate: str | None,
                   names: Mapping[str, str]) -> str:  # rule: 12.3.3
    """The answer as the statement it settles ('The door is locked.' / 'The door is not locked.'), never a question
    and answer; the typed subject and predicate carry the negation (no stored gloss needed)."""
    from engine.audit.fallback import _answer_line
    from engine.text.render import relation, sentence, the_name

    head = answer.strip().split(",", 1)[0].strip().lower()
    if head in ("yes", "no") and subject and predicate and subject != "world":
        said = relation(the_name(names.get(subject, "")) or "it", predicate, neg=head == "no")
        if said:
            return sentence(said)
    return _answer_line(question, answer)


def items(record: AdjudicationRecord, *, names: Mapping[str, str] | None = None) -> list[RecordItem]:
    # rule: 12.14.12
    # rule: 12.3.1a
    """Every citable line of `record`, numbered R1.. in the order the Narrator reads them."""
    from engine.audit.fallback import NPC_ROW_PROSE, _beat_line, _sentence, plain
    from engine.text.render import clause, sentence, who

    names = dict(names or {})
    pc = record.pc
    out: list[RecordItem] = []

    def add(kind: Kind, must: bool, ents: list[str], render: str, **kw: object) -> None:
        out.append(RecordItem(handle=f"R{len(out) + 1}", kind=kind, must_name=must,
                              entities=[e for e in ents if e], render=render, **kw))  # type: ignore[arg-type]

    def name(eid: str | None) -> str:
        return who(eid if eid is not None else pc, names=names, pc=pc)

    if record.scene.started:
        add("scene", False, [], _sentence(record.scene.header) if record.scene.header else "")
    for n, b in enumerate(record.beats):
        paused = record.pause is not None and n == len(record.beats) - 1 and b.degree is None
        add("beat", _owed(b, paused),[x for x in (b.actor or pc, *b.targets) if x], _beat_line(b, pc, names), beat=n)
        for i, c in enumerate(b.costs):
            add("cost", True, [pc or ""], _sentence(c.form) if c.form else "It comes at a cost.", beat=n, index=i,
                text=c.form)
        for i, h in enumerate(b.harm):
            add("harm", True, [h.target], _sentence(h.words if h.target == pc else f"{name(h.target)}: {h.words}"),
                beat=n, index=i, text=h.words)
        for i, c in enumerate(b.conditions):
            add("condition", True, [pc or ""], _sentence(c), beat=n, index=i, text=c)
        for i, p in enumerate(b.positions):
            add("position", True, [p.entity], sentence(clause(p.entity, "be", plain(p.words), names=names, pc=pc)),
                beat=n, index=i, text=p.words)
        for i, x in enumerate(b.learned):
            add("learned", True, [pc or "", *b.targets], _sentence(x), beat=n, index=i, text=x)
    for i, o in enumerate(record.oracle):
        add("oracle", True, [o.subject or ""], _oracle_render(o.question, o.answer, o.subject, o.predicate, names),
            index=i, text=f"{o.question}: {o.answer}")
    for i, a in enumerate(record.npc_actions):
        if OPTIONAL in a.tags:  # a bystander's reaction is optional material (12.14.12), not a record line
            continue
        add("npc", True, [a.npc], _sentence(f"{name(a.npc)} {NPC_ROW_PROSE.get(a.action, a.action)}"), index=i,
            text=a.action)
    # activities, postures and manners are optional material (12.14.12; DL-12-92): no handle, nothing requires them
    for i, om in enumerate(record.omens):
        if om.omen:
            add("omen", True, [om.clock_id], _sentence(om.omen), index=i, text=om.omen)
    for i, note in enumerate(record.notes):
        if note.lstrip().startswith(SKIP_NOTES):
            continue
        add("note", note.startswith(MUST_NOTES), [], _note_render(note), index=i, text=note)
    return out


def by_handle(its: list[RecordItem]) -> dict[str, RecordItem]:
    return {it.handle: it for it in its}


__all__ = ["MUST_NOTES", "OPTIONAL", "RecordItem", "by_handle", "items"]
