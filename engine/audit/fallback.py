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

DEGREE_WORDS = {  # 12.14.4: the degree in plain words, never "success"/"failure"
    "critical_success": "it goes better than hoped",
    "success": "it works",
    "failure": "it doesn't work",
    "critical_failure": "it goes badly",
}
_ID = re.compile(r"\(?\b[a-z]+(?:\.[a-z0-9_]+)+\b\)?|\b\w+_\w+\b|\d+")
_AUX = {"is", "are", "was", "were", "can", "could", "will", "would", "has", "have", "had", "should", "may", "might",
        "must", "does", "do", "did"}
_WH = {"what", "who", "whom", "whose", "which", "where", "when", "why", "how"}
_KEEP = {"the", "a", "an", "his", "her", "their", "my", "your", "its", "this", "that", "these", "those", "someone"}
_SOMEONE = re.compile(r"^(?:someone|somebody|anyone|anybody)\b", re.IGNORECASE)


_ASIDE = re.compile(r"\s*\([^()]*\)")  # "(Her claim about the ankle is context only.)", "(speech, no roll)"


def plain(text: str) -> str:
    """Strip asides in brackets (engine notes, never fiction), ids, snake_case keys and digits (12.14.4), and tidy
    the spacing and doubled stops."""
    s = re.sub(r"\[[^\[\]]*\]", "", _ASIDE.sub("", _ID.sub("", text)))
    s = re.sub(r"\s+([,.;:!?)])", r"\1", re.sub(r"\s{2,}", " ", s)).strip(" ,;:—-")
    return re.sub(r"([.!?])[.]+", r"\1", s)


def _sentence(text: str) -> str:
    s = plain(text)
    if not s:
        return ""
    s = s[0].upper() + s[1:]
    return s if s[-1] in ".!?" else s + "."


def _base(verb: str) -> str:
    """'forces' -> 'force', 'tries' -> 'try', 'is' -> 'are': the PC's verb in the second person."""
    # ponytail: suffix rules only; irregulars beyond is/has come out slightly off, add a table if one shows up
    v = verb.lower()
    if v in ("is", "has"):
        return {"is": "are", "has": "have"}[v]
    if v.endswith("ies"):
        return verb[:-3] + "y"
    if re.search(r"(?:sh|ch|x|ss|z|o)es$", v):
        return verb[:-2]
    return verb[:-1] if v.endswith("s") and not v.endswith("ss") else verb


def _you(restated: str, pc_names: Iterable[str], other_names: Iterable[str]) -> str:
    """The PC's restatement as 'you ...' (12.3.3 restates the beat; 'Learn whether ...' is not fiction)."""
    for n in pc_names:
        if n and restated.startswith(n + " "):
            verb, _, tail = restated[len(n) + 1:].partition(" ")
            return f"you {_base(verb)} {tail}".strip()
    first, _, rest = restated.partition(" ")
    if first.lower() in ("i", "you"):
        return f"you {rest}"
    if first.lower() == "to":
        restated = rest
        first, _, rest = restated.partition(" ")
    second = rest.split(" ", 1)[0].lower()
    named = {w for n in other_names for w in n.split()[:1]}
    # ponytail: "X is/tells/names ..." is read as a subject and its verb; a bare verb ("Learn whether", "Pick the
    # lock") takes "you try to". Anything else is kept as its own sentence, never glued on or lower-cased.
    if (first.lower() in _KEEP or first in named or second in _AUX
            or (re.fullmatch(r"[a-z]+s", second) and not second.endswith("ss"))):
        return restated  # already a sentence about someone or something else ("Gerella is pinned ...", "Tam ...")
    return f"you try to {restated[:1].lower()}{restated[1:]}"


def _beat_line(b: BeatEntry, pc: str | None, names: Mapping[str, str]) -> str:
    restated = plain(b.restatement)
    if restated and b.actor in (None, pc):
        full = names.get(pc or "", "")
        restated = _you(restated, [full, full.split(" ")[0]],
                        [n for e, n in names.items() if e != pc and n])
    if b.degree is None:  # no roll; the gate's own words (redirects, options) belong to the OOF block, not here
        # a no-roll success says so; refused or withdrawn says not yet; a paused or unrolled beat has no result
        result = ("you cannot do it that way" if b.gate in ("G3", "G4")
                  else "" if b.gate == "G0" or not b.gate_words
                  else "it works" if b.gate_words.startswith("no roll")
                  else "it does not happen yet")
    elif b.near_miss or b.success_at_cost:
        result = "it works, at a cost" if b.success_at_cost else "it falls just short"
    else:
        result = DEGREE_WORDS.get(b.degree, "it is settled")
    return " ".join(x for x in (_sentence(restated), _sentence(result)) if x)


def _negate(s: str) -> str:
    """'Townsfolk are already gathering' -> 'Townsfolk are not yet gathering'; '' when it cannot be said simply."""
    # ponytail: negates at the first auxiliary; a clause with an earlier relative-clause auxiliary reads off
    m = _SOMEONE.match(s)
    if m:
        return "no one" + s[m.end():]
    words = s.split()
    for i, w in enumerate(words):
        if w.lower() in _WH | {"that", "whether", "if"}:
            return ""  # the first auxiliary is inside a clause ("knows where the hiring can be found")
        if w.lower() in _AUX:
            if i + 1 < len(words) and words[i + 1].lower() in ("not", "no", "never"):
                return ""
            out = " ".join([*words[:i + 1], "not", *words[i + 1:]])
            return out.replace("not already", "not yet").replace("not still", "no longer")
    return ""


def _oracle_line(question: str, answer: str) -> str:
    """An Oracle answer as a statement of the world, never '<question>? Yes.' A 'no' that cannot be negated
    simply is left out (it denies something the fiction has not said)."""
    q = plain(question).rstrip("?.! ")
    if not q:
        return ""
    head, _, tail = answer.strip().partition(",")
    head, tail = head.strip().lower(), tail.strip()
    if head not in ("yes", "no"):
        return _sentence(f"{q}: {answer.strip()}")
    first = q.split(" ", 1)[0]
    if first.lower() in _AUX | _WH:
        return ""  # ponytail: an interrogative ('Is anyone ...?') is not turned round; the store keeps the fact
    if first.islower() and first not in _KEEP and not _SOMEONE.match(first) and first not in ("he", "she", "they", "it"):
        return ""  # no subject ("knows where ..."): not a statement of anything; left out (I-133)
    s = q if head == "yes" else _negate(q)
    # a twist ("yes, but ...") only as a clause of its own ("but the bucket is wet"), never "but lesser"
    twist = tail.split()
    if not (len(twist) >= 4 and twist[0].lower() == "but" and any(w.lower() in _AUX or w.endswith("s") for w in twist)):
        tail = ""
    return _sentence(f"{s}, {tail}" if s and tail else s)


# tbl.npc_action rows (12.11.5) and the Talk outcome as plain prose: the row's own act, its conditions left out
NPC_ROW_PROSE = {
    "escalates: threatens, calls for others, attacks only if able and hostile": "grows threatening and calls for others",
    "hinders quietly: delays, misdirects": "quietly stalls and misdirects",
    "wants something first: names a price or a favor": "wants a price or a favor first",
    "acts on one of their own wants": "turns to something they want",
    "asks the PC something": "has a question for you",
    "offers partial help": "offers some help",
    "responds as the talk went: critical_success": "agrees readily",
    "responds as the talk went: success": "agrees",
    "responds as the talk went: failure": "is not persuaded",
    "responds as the talk went: critical_failure": "is not persuaded",
}


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
        lines.append(_beat_line(b, record.pc, names))
        lines += [_sentence(c.form) if c.form else "It comes at a cost." for c in b.costs]
        lines += [_sentence(h.words if h.target == record.pc else f"{who(h.target)}: {h.words}") for h in b.harm]
        lines += [_sentence(c) for c in b.conditions]
        lines += [_sentence(f"{who(p.entity)} {'are' if p.entity == record.pc else 'is'} {p.words}")
                  for p in b.positions]
        lines += [_sentence(x.replace(" — ", " ", 1)) for x in b.learned]
    for o in record.oracle:
        lines.append(_oracle_line(o.question, o.answer))
    for a in record.npc_actions:
        lines.append(_sentence(f"{who(a.npc)} {NPC_ROW_PROSE.get(a.action, a.action)}"))
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
