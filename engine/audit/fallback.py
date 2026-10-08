"""The plain fallback (12.3.3; T045): narration built only from the adjudication record, delivered when the third
claim check still fails. Dull but true: one plain sentence per recorded item, no new elements, and a
`rule_conflict` ruling with `review_flag: true` for the caller to log. Beat lines and facts are rendered from typed
fields (`engine.text.render`); model free text (an Oracle question, a restatement) is shown verbatim or not at all.

    fb = plain_fallback(record, names={"pc.wren": "Wren"}, verdicts=last_verdicts)
    response.fiction = fb.fiction; tx.add(log_ruling(fb.ruling, tx.mint, store=store, staged=tx.events))
    # fb.owed_blocks: OOF labels the turn still owes ("[WARNING]"); the OOF renderer adds them (07.3.4)
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from typing import Any

from pydantic import BaseModel, Field

from engine.audit.claims import OWED_BLOCKS, Verdict
from engine.dm.adjudication import AdjudicationRecord, BeatEntry
from engine.resolve.rulings import RulingRecord
from engine.text.render import (
    BEAT_VERBS,
    clause,
    degree_words,
    relation,
    sentence,
    slug_words,
    the_name,
    verb_head,
    who,
)

_ID = re.compile(r"\(?\b[a-z]+(?:\.[a-z0-9_]+)+\b\)?|\b\w+_\w+\b|\d+")
_AUX = {"is", "are", "was", "were", "can", "could", "will", "would", "has", "have", "had", "should", "may", "might",
        "must", "does", "do", "did"}
_WH = {"what", "who", "whom", "whose", "which", "where", "when", "why", "how"}


_ASIDE = re.compile(r"\s*\([^()]*\)")  # "(Her claim about the ankle is context only.)", "(speech, no roll)"


def plain(text: str) -> str:
    """Strip asides in brackets (engine notes, never fiction), ids, snake_case keys and digits (12.14.4), and tidy
    the spacing and doubled stops."""
    s = re.sub(r"\[[^\[\]]*\]", "", _ASIDE.sub("", _ID.sub("", text)))
    s = re.sub(r"\s+([,.;:!?)])", r"\1", re.sub(r"\s{2,}", " ", s)).strip(" ,;:—-")
    return re.sub(r"([.!?])[.]+", r"\1", s)


_READER_NOTE = re.compile(r"\bnot a beat\b|\bno act is declared\b|\bquestion to the DM\b|\bno roll\b|"
                          r"\bfree activity\b|^Queued\b|\bpending clarification\b", re.IGNORECASE)


def drop_reader_notes(text: str) -> str:
    """A restatement without the Reader's own notes ("Spoken to Oggza, not a beat: ...", "Queued: looking at
    Belia, pending clarification ..."): bookkeeping, never player text (P-108)."""
    return " ".join(s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s and not _READER_NOTE.search(s))


def _sentence(text: str) -> str:
    return sentence(plain(text))


def _beat_line(b: BeatEntry, pc: str | None, names: Mapping[str, str]) -> str:
    """The beat from its typed fields: the actor, the Reader's verb and the target (never the restatement's words),
    then its result."""
    with_target, alone = BEAT_VERBS.get(b.verb, BEAT_VERBS[None])
    target = next((t for t in b.targets if t != b.actor), None)
    act = clause(b.actor or pc, with_target if target else alone, who(target, names=names, pc=pc) if target else None,
                 names=names, pc=pc)
    if b.degree is None:  # no roll; the gate's own words (redirects, options) belong to the OOF block, not here
        # a no-roll success says so; refused or withdrawn says not yet; a paused or unrolled beat has no result
        # an accepted G3 fallback that resolved is not a refusal (P-087)
        result = ("it works" if b.gate_words.startswith("no roll")
                  else "you cannot do it that way" if b.gate in ("G3", "G4")
                  else "" if b.gate == "G0" or not b.gate_words
                  else "it does not happen yet")
    else:
        result = degree_words(b.degree, near_miss=b.near_miss, success_at_cost=b.success_at_cost)
    return " ".join(x for x in (sentence(act), sentence(result)) if x)


def _answer_line(question: str, answer: str) -> str:
    """An Oracle answer, only where the question was put as a statement and the answer is yes: the question's own
    words, verbatim. A 'no', or an interrogative ('Is anyone ...?'), is left out (the store keeps the fact; never
    negated or turned round)."""
    q = plain(question).rstrip("?.! ")
    head, _, tail = answer.strip().partition(",")
    head, tail = head.strip().lower(), tail.strip()
    if not q:
        return ""
    if head not in ("yes", "no"):
        return sentence(f"{q}: {answer.strip()}")
    first = q.split(" ", 1)[0]
    if head == "no" or not first[:1].isupper() or first.lower() in _AUX | _WH:
        return ""
    # a twist ("yes, but ...") only as a clause of its own ("but the bucket is wet"), never "but lesser"
    return sentence(f"{q}, {tail}" if tail.lower().startswith("but ") and len(tail.split()) >= 4 else q)


_SLUG_MAX = 60  # turn.py cuts an Oracle question's predicate slug here: one this long is an unfinished clause
_RAW = re.compile(r"\b[a-z]+(?:\.[a-z0-9_]+)+\b|\b\w+_\w+\b")
_BOOL = {True: True, False: False, "true": True, "false": False, "yes": True, "no": False}
_IS_PREDS = {"state", "kind", "condition", "desc", "posture", "mood", "demeanor", "look", "appearance"}


def fact_sentence(state: Any, f: Any, subject: str | None = None) -> str:  # rule: 12.14.4
    """A fact as one short plain sentence for the player: 'The canvas belongs to a pack.', 'The pack is held by
    Bixok Lucky.' A yes/no fact reads as the statement it settles, through a verb from the closed list
    (`engine.text.render.relation`); one with no such verb ('coin_named', 'fingers_ink_stained') is '' and is
    left out."""
    from engine.dm.codex import _value_words
    from engine.dm.oof import short_text
    from engine.dm.player_text import second_person
    from engine.dm.roles.narrator import name_of

    subj = subject if subject is not None else ("" if f.subject == "world" else name_of(state, f.subject))
    subj = the_name(subj) if subj else ""
    if f.predicate.endswith((".but", ".and")):  # an Oracle twist's qualifier: meaning words, not a statement
        return ""
    v = f.value
    yes = _BOOL.get(v.lower() if isinstance(v, str) else v) if isinstance(v, str | bool) else None
    if yes is not None:
        if not subj or len(f.predicate) >= _SLUG_MAX:
            return ""
        return second_person(sentence(relation(subj, f.predicate, neg=not yes)))
    val = name_of(state, v) if isinstance(v, str) and v in getattr(state, "entities", {}) else _value_words(v)
    said = [re.sub(r"^(?:said|says)\s+(?:that\s+)?", "", c.strip()) for c in str(val).split(";")]
    if subj and str(val).lstrip().startswith(("said ", "says ")):  # a speech record (P-097): what they said
        more = [c for c in said[1:] if c]
        out = clause(subj, "say that", said[0], tense="past")
        while more and len(out) + sum(len(c) + 12 for c in more) > 200:  # ponytail: drops the latest clauses
            more.pop()
        out += "".join(f", and that {c}" if i == len(more) - 1 else f", that {c}" for i, c in enumerate(more))
        return second_person(sentence(out))
    val = short_text(str(val), 120)
    if not val or _RAW.search(val):  # an id or key ('orig.life.soldier', a route record) is not words (P-097)
        return ""
    pred = f.predicate
    if not subj and pred.startswith("who_is_") and v in getattr(state, "entities", {}):
        s = clause(val, "be", the_name(slug_words(pred.removeprefix("who_is_"))))  # 12.16.16
    elif pred.startswith("lead."):
        s = val
    elif not subj:
        s = f"{slug_words(pred)}: {val}"
    elif pred in _IS_PREDS and _AUX & {w.lower() for w in val.split()[1:4]}:  # a clause ('a cough is spreading there')
        if not val.endswith(" there"):
            return ""
        s = f"{val.removesuffix(' there')} in {subj}"
    elif pred in _IS_PREDS and (h := verb_head(val.split(" ", 1)[0])) and h[1] == "s3":
        s = f"{subj} {val}"  # 'glares at the door': the value is the verb phrase
    else:
        s = relation(subj, pred, val)
    return second_person(sentence(s))


# tbl.npc_action rows (12.11.5) and the Talk outcome as plain prose: the row's own act, its conditions left out
NPC_ROW_PROSE = {
    "escalates: threatens, calls for others, attacks only if able and hostile": "grows threatening and calls for others",
    "hinders quietly: delays, misdirects": "quietly stalls and misdirects",
    "wants something first: names a price or a favor": "wants a price or a favor first",
    "acts on one of their own wants": "turns to something they want",
    "asks the PC something": "has a question for you",
    "offers partial help": "offers some help",
    "carries on with their own business": "goes on with what they were doing and does not answer",
    "ends the exchange and withdraws": "says no more and turns away",
}


class FallbackResult(BaseModel):
    fiction: str
    review_flag: bool = True
    owed_blocks: list[str] = Field(default_factory=list)
    ruling: RulingRecord


def plain_fallback(record: AdjudicationRecord, *, names: Mapping[str, str] | None = None,
                   verdicts: Iterable[Verdict] = ()) -> FallbackResult:  # rule: 12.3.3
    """12.3.3 when no drafted sentence passed: the scene header (only when this turn opened a scene), then every
    must-name record item's rendered line (engine/dm/handles.py), then the open prompt (12.14.9) unless a pause
    block follows. Every string comes from `record` (names only resolve its ids)."""
    from engine.dm.handles import items

    its = items(record, names=names)
    lines = [it.render for it in its if it.kind == "scene" or it.must_name]
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
