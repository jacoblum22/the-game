"""The plain fallback (12.3.3; T045): narration built only from the adjudication record, delivered when the third
claim check still fails. Dull but true: one plain sentence per recorded item, no new elements, and a
`rule_conflict` ruling with `review_flag: true` for the caller to log.

    fb = plain_fallback(record, names={"pc.wren": "Wren"}, verdicts=last_verdicts)
    response.fiction = fb.fiction; tx.add(log_ruling(fb.ruling, tx.mint, store=store, staged=tx.events))
    # fb.owed_blocks: OOF labels the turn still owes ("[WARNING]"); the OOF renderer adds them (07.3.4)
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping

from pydantic import BaseModel, Field

from engine.audit.claims import OWED_BLOCKS, Verdict
from engine.dm.adjudication import AdjudicationRecord, BeatEntry
from engine.resolve.rulings import RulingRecord

DEGREE_WORDS = {
    "critical_success": "it goes better than hoped",
    "success": "it works",
    "failure": "it does not work",
    "critical_failure": "it goes badly wrong",
}
_ID = re.compile(r"\(?\b[a-z]+(?:\.[a-z0-9_]+)+\b\)?|\b\w+_\w+\b|\d+")


def plain(text: str) -> str:
    """Strip ids, snake_case keys and digits (12.14.4) and tidy the spacing."""
    s = _ID.sub("", text)
    s = re.sub(r"\s+([,.;:!?])", r"\1", re.sub(r"\s{2,}", " ", s)).strip(" ,;:—-")
    return s


def _sentence(text: str) -> str:
    s = plain(text)
    if not s:
        return ""
    s = s[0].upper() + s[1:]
    return s if s[-1] in ".!?" else s + "."


def _beat_line(b: BeatEntry) -> str:
    restated = plain(b.restatement)
    if b.degree is None:
        result = plain(b.gate_words) or "it works"
    elif b.near_miss or b.success_at_cost:
        result = "it works, at a cost" if b.success_at_cost else "it falls just short"
    else:
        result = DEGREE_WORDS.get(b.degree, "it is settled")
    return _sentence(f"{restated}: {result}" if restated else result)


class FallbackResult(BaseModel):
    fiction: str
    review_flag: bool = True
    owed_blocks: list[str] = Field(default_factory=list)
    ruling: RulingRecord


def plain_fallback(record: AdjudicationRecord, *, names: Mapping[str, str] | None = None,
                   verdicts: Iterable[Verdict] = ()) -> FallbackResult:  # rule: 12.3.3
    """Sentences, in order: the scene header; per beat its restatement and degree in words, its cost forms, harm,
    visible conditions and changed positions; oracle answers; sourced NPC acts; omens; then the open prompt
    (12.14.9) unless a pause block follows. Every string comes from `record` (names only resolve its ids)."""
    names = dict(names or {})

    def who(eid: str | None) -> str:
        if eid is None or eid == record.pc:
            return "you"
        return names.get(eid) or "someone"

    lines: list[str] = []
    if record.scene.header:
        lines.append(_sentence(record.scene.header))
    for b in record.beats:
        lines.append(_beat_line(b))
        lines += [_sentence(c.form) if c.form else "It comes at a cost." for c in b.costs]
        lines += [_sentence(h.words if h.target == record.pc else f"{who(h.target)}: {h.words}") for h in b.harm]
        lines += [_sentence(c) for c in b.conditions]
        lines += [_sentence(f"{who(p.entity)} {'are' if p.entity == record.pc else 'is'} {p.words}")
                  for p in b.positions]
    for o in record.oracle:
        lines.append(_sentence(f"{plain(o.question).rstrip('?')}? {o.answer.capitalize()}"))
    for a in record.npc_actions:
        lines.append(_sentence(f"{who(a.npc)} {a.action}"))
    lines += [_sentence(o.omen) for o in record.omens if o.omen]
    if record.pause is None:
        lines.append("What do you do?")
    fiction = " ".join(x for x in lines if x)
    bad = [v.model_dump(mode="json") for v in verdicts if v.verdict != "supported"]
    ruling = RulingRecord(
        signature="claim_check.fallback", situation="the claim check failed after two redrafts (12.3.3)",
        kind="rule_conflict", review_flag=True, result={"outcome": "plain_fallback", "verdicts": bad},
        tags=["claim_check"])
    owed = [label for trg, label in OWED_BLOCKS.items() if trg in record.triggers]
    return FallbackResult(fiction=fiction, owed_blocks=owed, ruling=ruling)
