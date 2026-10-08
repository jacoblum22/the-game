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
_DET = {"some", "any", "each", "every", "no", "one", "both", "all", "our", "another", "nobody", "everyone"}
# a second verb of the PC's after "and"/"then", read as a verb when a particle, preposition or article follows
_AND_VERB = re.compile(r"\b(and|then) ([a-z]+(?<!ss)s)\b(?= (?:the|a|an|out|in|into|on|onto|up|down|to|back|"
                       r"over|through|away|off|his|her|their|its|from|with|toward|towards|across|around|"
                       r"for|at)\b)")
_SOMEONE = re.compile(r"^(?:someone|somebody|anyone|anybody)\b", re.IGNORECASE)


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
            tail = _AND_VERB.sub(lambda m: f"{m[1]} {_base(m[2])}", tail)  # "and goes out" -> "and go out"
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
    head = re.sub(r"['’]s?$", "", first)  # "Garett's grip ...", "the guards' fire": a possessive starts a subject (P-091)
    if (first.lower() in _KEEP | _DET or head != first or head in named or second in _AUX
            or (re.fullmatch(r"[a-z]+s", second) and not second.endswith("ss"))):
        return restated  # already a sentence about someone or something else ("Gerella is pinned ...", "Tam ...")
    return f"you try to {restated[:1].lower()}{restated[1:]}"


def _beat_line(b: BeatEntry, pc: str | None, names: Mapping[str, str]) -> str:
    restated = plain(drop_reader_notes(b.restatement))
    if restated and b.actor in (None, pc):
        full = names.get(pc or "", "")
        restated = _you(restated, [full, full.split(" ")[0]],
                        [n for e, n in names.items() if e != pc and n])
    if b.degree is None:  # no roll; the gate's own words (redirects, options) belong to the OOF block, not here
        # a no-roll success says so; refused or withdrawn says not yet; a paused or unrolled beat has no result
        # an accepted G3 fallback that resolved is not a refusal (P-087)
        result = ("it works" if b.gate_words.startswith("no roll")
                  else "you cannot do it that way" if b.gate in ("G3", "G4")
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
            if {"and", "or", "but"} & {x.lower().strip(",") for x in words[i + 1:]}:
                return ""  # a compound ("is in X and can be found in Y"): 'not' would deny only half (P-077)
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


_SLUG_MAX = 60  # turn.py cuts an Oracle question's predicate slug here: one this long is an unfinished clause
_IS_PREDS = {"state", "kind", "condition", "desc", "posture", "mood", "demeanor", "look", "appearance"}
_PREPS = {"by", "of", "in", "on", "at", "to", "from", "with", "for", "under", "near", "behind", "inside"}
_LOC_PREPS = _PREPS | {"beyond", "beside", "pushed", "set", "against", "above", "below", "within", "outside", "across",
                       "along", "among", "amid", "between", "around", "over", "through", "past", "toward", "towards",
                       "atop", "upon", "into", "onto", "beneath", "underneath", "inside", "here", "there", "up",
                       "down", "hung", "hanging", "lying", "standing", "where", "just", "close"}
_RAW = re.compile(r"\b[a-z]+(?:\.[a-z0-9_]+)+\b|\b\w+_\w+\b")
_BOOL = {True: True, False: False, "true": True, "false": False, "yes": True, "no": False}


def _finite(w: str) -> bool:
    """'is', 'carries', 'belongs': a verb a statement can turn on (ponytail: suffix test; past tenses are left out)."""
    w = w.lower()
    return w in _AUX or (len(w) > 3 and w.endswith("s") and not w.endswith(("ss", "us", "is", "ts", "ns")))


def the_name(name: str) -> str:
    """'bench' -> 'the bench'; a proper name or one with its own article stays as it is."""
    return name if not name[:1].islower() or name.split(" ", 1)[0] in _KEEP else f"the {name}"


def _cap(s: str) -> str:
    s = s.strip().rstrip(" ,;:—-")
    return "" if not s else s[0].upper() + s[1:] + ("" if s[-1] in ".!?" else ".")


def fact_sentence(state: object, f: object, subject: str | None = None) -> str:  # rule: 12.14.4
    """A fact as one short plain sentence for the player: 'The canvas belongs to a pack.', 'The pack is held by
    Bixok Lucky.' A yes/no fact (an Oracle-settled question) reads as the statement it settles, never ': yes'; one
    that cannot be phrased as a statement ('coin named none yet', 'size') is '' and is left out."""
    from engine.dm.codex import _value_words
    from engine.dm.oof import short_text
    from engine.dm.player_text import second_person
    from engine.dm.roles.narrator import name_of

    subj = subject if subject is not None else ("" if f.subject == "world" else name_of(state, f.subject))
    subj = the_name(subj) if subj else ""
    if f.predicate.endswith((".but", ".and")):  # an Oracle twist's qualifier: meaning words, not a statement
        return ""
    pred = f.predicate.removeprefix("lead.")
    p = re.sub(r"\b(?:the )?pc s\b", "your", pred.replace("_", " ").replace(".", " "))
    p = re.sub(r"\b(\w+) s\b", r"\1's", re.sub(r"\b(?:the )?pc\b", "you", p)).strip()  # 'selda s sleeve' (P-097)
    v = f.value
    yes = _BOOL.get(v.lower() if isinstance(v, str) else v) if isinstance(v, str | bool) else None
    if yes is not None:
        words = p.split()
        if words[:1] == ["whether"]:
            words = words[1:]
        if words[:1] and words[0] in ("it", "he", "she", "they"):
            words = words[1:]
        if (not subj or len(f.predicate) >= _SLUG_MAX or len(words) < 2 or not _finite(words[0])
                or words[1] == "and"):
            return ""
        s = f"{subj} {' '.join(words)}"
        if not yes:
            s = _negate(s) or (f"{subj} does not {_base(words[0])} {' '.join(words[1:])}"
                               if words[0].lower() not in _AUX else "")
        return second_person(_cap(s))
    val = name_of(state, v) if isinstance(v, str) and v in getattr(state, "entities", {}) else _value_words(v)
    said = [re.sub(r"^(?:said|says)\s+(?:that\s+)?", "", c.strip()) for c in str(val).split(";")]
    if subj and str(val).lstrip().startswith(("said ", "says ")):  # a speech record (P-097): what they said
        out = f"{subj} said that {said[0]}"
        more = [c for c in said[1:] if c]
        while more and len(out) + sum(len(c) + 12 for c in more) > 200:  # ponytail: drops the latest clauses
            more.pop()
        out += "".join(f", and that {c}" if i == len(more) - 1 else f", that {c}" for i, c in enumerate(more))
        return second_person(_cap(out))
    val = short_text(str(val), 120)
    if not val or _RAW.search(val):  # an id or key ('orig.life.soldier', a route record) is not words (P-097)
        return ""
    first = val.split(" ", 1)[0].lower()
    if not subj and f.predicate.startswith("who_is_") and v in getattr(state, "entities", {}):
        s = f"{val} is {the_name(p.removeprefix('who is '))}"  # the opening incident's role (12.16.16)
    elif f.predicate.startswith("lead.") or not subj:
        s = val if f.predicate.startswith("lead.") else f"{p}: {val}"
    elif p in _IS_PREDS or p == "kind":
        art = "a " if p == "kind" and first not in _KEEP else ""
        if _AUX & {w.lower() for w in val.split()[1:4]}:  # a clause ('a cough is spreading there'), not a state
            if not val.endswith(" there"):
                return ""
            s = f"{val.removesuffix(' there')} in {subj}"
        else:
            s = f"{subj} {val}" if _finite(first) else f"{subj} is {art}{val}"
    elif p == "location":
        s = f"{subj} is {val}" if first in _LOC_PREPS or first.endswith("ed") else f"{subj} is at {val}"
    elif p in ("text", "content", "contents", "wording", "inscription", "writing", "words"):
        s = f"{subj} reads: {val}"
    elif p == "owner":
        s = f"{subj} belongs to {val}"
    elif _finite(p.split(" ", 1)[0]):
        s = f"{subj} {p} {val}"
    elif p.rsplit(" ", 1)[-1] in _PREPS:
        s = f"{subj} is {p} {val}"
    else:
        poss = "'" if subj.endswith("s") else "'s"
        s = f"{subj}{poss} {p} is {val}"
    return second_person(_cap(s))


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
    "responds as the talk went: failure": "is not persuaded and gives you no answer",
    "responds as the talk went: critical_failure": "is not persuaded and gives you no answer",
    "carries on with their own business": "goes on with what they were doing and does not answer",
    "ends the exchange and withdraws": "says no more and turns away",
}


_QUOTED = re.compile(r"[\"“]([^\"”]+)[\"”]")


def _said_line(text: str) -> str:
    """The player's own words, quoted back: 'You ask, "Is she one of yours?"' (12.3.3: no new elements)."""
    t = text.strip()
    inner = t.strip("\"“” ")
    if re.search(r"[\"“”]", inner):  # narrated around the speech ('I lean in and say, "..."'): the speech only
        inner = " ".join(q.strip() for q in _QUOTED.findall(t)) or inner
    if not inner:
        return ""
    return f'You {"ask" if inner.rstrip().endswith("?") else "say"}, "{inner}"'


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
    # a spoken line or an in-character question with no beat of its own is restated, in the player's order
    beat_parts = {b.part for b in record.beats}
    said = [(i, _said_line(p.text)) for i, p in enumerate(record.parts)
            if p.cls in ("SPEECH", "FICTION_QUESTION") and p.handled in ("", "answered") and i not in beat_parts]
    for b in record.beats:
        while said and b.part is not None and said[0][0] < b.part:
            lines.append(said.pop(0)[1])
        lines.append(_beat_line(b, record.pc, names))
        lines += [_sentence(c.form) if c.form else "It comes at a cost." for c in b.costs]
        lines += [_sentence(h.words if h.target == record.pc else f"{who(h.target)}: {h.words}") for h in b.harm]
        lines += [_sentence(c) for c in b.conditions]
        lines += [_sentence(f"{who(p.entity)} {'are' if p.entity == record.pc else 'is'} {p.words}")
                  for p in b.positions]
        lines += [_sentence(x) for x in b.learned]
    lines += [s for _, s in said]
    for o in record.oracle:
        lines.append(_oracle_line(o.question, o.answer))
    for a in record.npc_actions:
        lines.append(_sentence(f"{who(a.npc)} {NPC_ROW_PROSE.get(a.action, a.action)}"))
    lines += [_sentence(o.omen) for o in record.omens if o.omen]
    lines += [n.split(": ", 1)[1] for n in record.notes if n.startswith("cannot make out: ")]  # P-086
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
