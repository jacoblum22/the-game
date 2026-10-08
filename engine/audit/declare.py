"""Declared sentences (12.3.1 source 1, 12.3.1a, 12.14.13; spec 006): the narrator's output parsed, the content
tiers, and the deterministic checks code runs on every sentence before any verdict.

    sents = parse_output(narrator_data)                       # [DeclaredSentence], either output shape
    idx = SceneIndex.of(state, items)                         # names, aliases, pronouns, quantities, facts
    scan = scan_sentence(sents[0], idx, rules=rules)          # names added to `about`, failures found by code
    coverage(sents, items)                                    # must-name handles no sentence cites

Everything here is `[D]`: no model call, no store write. The narration loop (engine/dm/narration.py) turns the
failures into cuts and narrow redrafts (12.3.3) and writes new elements by tier (PR-00-7).
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from engine.audit import text as tx

Tier = Literal["T0", "T1a", "T1b", "T1c", "T2"]
Fix = Literal["cut", "redraft", "oracle"]

# pacing.yaml#claim_check.element_tiers (read from rules when given; this copy is the closed list's default)
ELEMENT_TIERS: dict[str, Tier] = {"furniture": "T1a", "feature": "T1a", "person": "T1a", "item": "T1a",
                                  "document": "T1a", "knowledge": "T1b", "clue": "T2", "hazard": "T2",
                                  "adversary": "T2"}
MENTION_KIND = {"person": "npc", "item": "item", "document": "item", "furniture": "object", "feature": "object"}


class Implied(BaseModel):
    predicate: str
    value: str


class NewElement(BaseModel):
    model_config = ConfigDict(extra="ignore")

    element_kind: str = ""
    name: str = ""
    ordinary: bool = True
    implied: list[Implied] = Field(default_factory=list)


class DeclaredSentence(BaseModel):
    model_config = ConfigDict(extra="ignore")

    text: str = ""
    refs: list[str] = Field(default_factory=list)
    about: list[str] = Field(default_factory=list)
    new: list[NewElement] = Field(default_factory=list)
    atmosphere: bool = False
    speaker: str | None = None  # 12.3.1b item 1: who says the quoted (or reported) words; never the PC

    @field_validator("speaker", mode="before")
    @classmethod
    def _none(cls, v: Any) -> Any:
        return None if v in (None, "", "none") else v

    @property
    def declared(self) -> bool:
        return bool(self.refs or self.about or self.new)


class Failure(BaseModel):
    why: str
    fix: Fix
    store_value: str | None = None


class SentenceScan(BaseModel):
    added_about: list[str] = Field(default_factory=list)  # names the sentence used but did not declare (logged)
    failures: list[Failure] = Field(default_factory=list)
    undeclared_new: int = 0  # undeclared addressable elements code found (unknown proper names)
    logged: list[tuple[str, str]] = Field(default_factory=list)  # (class, why): found, off the blocking list (12.3.1b)


# ------------------------------------------------------------------------------------------- parsing


def split(text: str) -> list[str]:
    from engine.llm.offline import sentences

    return sentences(text)


def parse_output(data: Mapping[str, Any]) -> list[DeclaredSentence]:  # rule: 12.3.1
    """Either output shape (contracts/narrator.md) as the same list: `sentences[]`, or `fiction` plus
    `declarations` keyed by sentence index (the fallback schema, B risk 2)."""
    if data.get("sentences") is not None:
        out = [DeclaredSentence.model_validate(s) for s in data.get("sentences") or []]
        return [s.model_copy(update={"text": s.text.strip()}) for s in out if s.text.strip()]
    texts = split(str(data.get("fiction") or ""))
    decl: dict[int, dict[str, Any]] = {}
    for d in data.get("declarations") or []:
        try:
            decl.setdefault(int(str(d.get("sentence"))), dict(d))
        except ValueError:
            continue
    return [DeclaredSentence.model_validate({**decl.get(i, {}), "text": t}) for i, t in enumerate(texts)]


def joined(sents: Iterable[DeclaredSentence]) -> str:
    return " ".join(s.text for s in sents if s.text)


# ------------------------------------------------------------------------------------------- tiers


def tier_of(el: NewElement, rules: Any = None) -> Tier:  # rule: 12.14.13
    """The element's tier from its declared kind (`pacing.yaml#claim_check.element_tiers`). A `person`, `item` or
    `document` the narrator did not declare ordinary is T2 (12.14.13's question found true); an unknown kind is
    T1a (an uncertain kind is T1a: R2-G, DL-12-80)."""
    tiers = dict(ELEMENT_TIERS)
    if rules is not None:
        tiers.update((rules.pacing.get("claim_check") or {}).get("element_tiers") or {})
    t = tiers.get(el.element_kind)
    if t is None:
        return "T1a"
    if el.element_kind in ("person", "item", "document") and not el.ordinary:
        return "T2"
    return t  # type: ignore[return-value]


def mention_of(el: NewElement) -> dict[str, Any] | None:  # rule: PR-00-7
    """A T1a element as a write-on-mention entry (engine.dm.mentions), or None for kinds never written so."""
    kind = MENTION_KIND.get(el.element_kind)
    if kind is None or not el.name.strip():
        return None
    return {"kind": kind, "name": el.name.strip(), "implied": [i.model_dump() for i in el.implied], "unsettled": []}


# ------------------------------------------------------------------------------------------- the index


class SceneIndex(BaseModel):
    """What the scans compare a sentence with. Built from the store (`of`) or, in the replay bench, from a recorded
    packet's text (`evals/narration_plug.py`)."""

    pc: str | None = None
    aliases: dict[str, list[str]] = Field(default_factory=dict)  # entity id -> names (lower case)
    pronouns: dict[str, str] = Field(default_factory=dict)  # person id -> "f" | "m" | "x"
    numbers: dict[str, list[int]] = Field(default_factory=dict)  # entity id -> its quantities' values
    facts: dict[str, str] = Field(default_factory=dict)  # fact id -> "<subject> <predicate> <value>" words
    fact_subject: dict[str, str] = Field(default_factory=dict)
    handles: dict[str, str] = Field(default_factory=dict)  # handle -> the line's words
    handle_entities: dict[str, list[str]] = Field(default_factory=dict)
    known_words: set[str] = Field(default_factory=set)  # capitalised words that are not new names (places, peoples)
    sealed: list[str] = Field(default_factory=list)  # sealed names and contents (whole phrases, lower case)

    @classmethod
    def of(cls, state: Any, its: Sequence[Any] = ()) -> SceneIndex:  # rule: 12.3.1a
        from engine.retrieve.scene import pc_id
        from engine.store.views import unnamed_label

        pc = pc_id(state)
        aliases: dict[str, list[str]] = {}
        pronouns: dict[str, str] = {}
        sealed: list[str] = []
        known: set[str] = set()
        for eid, e in state.entities.items():
            seal = state.seals.get(eid)
            if seal is not None and not seal.slice:
                if e.name and len(tx.content(e.name)) >= 1:
                    sealed.append(e.name.lower())
                continue
            names = [e.name, *(a for a in e.data.get("aliases") or [] if isinstance(a, str))]
            if e.kind in ("npc", "pc", "companion", "adversary"):
                if e.data.get("role") or e.data.get("aliases"):
                    names.append(unnamed_label(e))
                if e.name and len(e.name.split()) > 1:
                    names.append(e.name.split()[0])
                g = _gender(e.data.get("pronouns")) or _gender(e.data.get("gender"))
                if g:
                    pronouns[eid] = g
            aliases[eid] = [n.lower() for n in dict.fromkeys(n for n in names if n and len(n) > 2)]
            known |= {w for n in names if n for w in re.findall(r"[A-Z][\w'-]+", n)}
        # a label shared by someone here and someone absent ("the child") names the one here (12.10.2's labels are
        # roles, so two children share one): the absent one keeps only its unshared names [spec 009 B]
        from engine.world.scenes import cast_present

        here = {pc, *cast_present(state)} if state.scene is not None else set()
        taken = {n for eid in here if eid in aliases for n in aliases[eid]}
        aliases = {eid: ns if eid in here else [n for n in ns if n not in taken] for eid, ns in aliases.items()}
        region = state.meta.get("world.region")
        if isinstance(region, dict):
            known |= {w for x in region.values() if isinstance(x, str) for w in re.findall(r"[A-Z][\w'-]+", x)}
        for v in (state.meta.get("world.peoples") or []):
            if isinstance(v, dict):
                known |= {w for x in v.values() if isinstance(x, str) for w in re.findall(r"[A-Z][\w'-]+", x)}
        numbers = {s: [q.current for q in qs.values()] for s, qs in state.quantities.items()}
        facts: dict[str, str] = {}
        subj: dict[str, str] = {}
        for fid, f in state.facts.items():
            if f.visibility == "sealed" or fid in state.seals:
                continue
            facts[fid] = f"{f.subject} {f.predicate} {f.value}"
            subj[fid] = f.subject
        return cls(pc=pc, aliases=aliases, pronouns=pronouns, numbers=numbers, facts=facts, fact_subject=subj,
                   handles={it.handle: f"{it.text} {it.render}" for it in its},
                   handle_entities={it.handle: list(it.entities) for it in its}, known_words=known, sealed=sealed)

    def subjects(self, s: DeclaredSentence) -> set[str]:
        """The ids a sentence declares it speaks of: `about`, cited facts' subjects, cited lines' entities."""
        out = set(s.about)
        for r in s.refs:
            if r in self.fact_subject:
                out.add(self.fact_subject[r])
            out.update(self.handle_entities.get(r, ()))
        return out

    def cited_words(self, s: DeclaredSentence) -> str:
        return " ".join(self.handles.get(r) or self.facts.get(r) or "" for r in s.refs)


_GENDER = {"f": ("she", "her", "woman", "female"), "m": ("he", "him", "man", "male"), "x": ("they", "them")}


def _gender(v: Any) -> str | None:
    w = tx.words(v or "")
    for g, keys in _GENDER.items():
        if w and w[0] in keys:
            return g
    return None


# ------------------------------------------------------------------------------------------- scans

_PROPER = re.compile(r"\b([A-Z][a-z][\w'-]+)")
_STOP_CAPS = frozenset("I You Your The A An He She They It His Her Their Its We Our My Me Him Them What Who Where "
                       "When Why How Yes No Not And But Or If Then There Here This That These Those Gods God Sir "
                       "Madam Lord Lady Master Mistress Mother Father Brother Sister Aye Nay".split())
_QTY_NOUNS = ("coin", "coins", "silver", "gold", "copper", "penny", "pennies", "arrow", "arrows", "ration", "rations",
              "torch", "torches", "shaft", "shafts", "purse")
_NUM_WORDS = {k: v for k, v in tx.NUMBER_WORDS.items() if v >= 2 and k not in ("pair", "both", "dozen")}
_HE = re.compile(r"\b(he|him|his|himself)\b", re.I)
_SHE = re.compile(r"\b(she|her|hers|herself)\b", re.I)
_QUOTED = re.compile(r"[\"“][^\"”]*[\"”]")


_PC_SAYS = re.compile(r"\byou\s+(?:say|ask|call|shout|whisper|reply|answer|tell|mutter|murmur|cry|add|growl|snap|"
                      r"plead|demand|insist|offer|begin|start|venture)\w*\b", re.I)


def voices(s: DeclaredSentence) -> tuple[str, list[str]]:  # rule: 12.3.1b
    """(the narrator's words, the speech spans). Quoted words are speech; a sentence with a declared speaker and
    no quotes is reported speech, whole ("she tells you it left at dawn")."""
    spans = [m.group(0).strip("\"“”") for m in _QUOTED.finditer(s.text)]
    if not spans:
        return ("", [s.text]) if s.speaker else (s.text, [])
    return re.sub(r"\s+", " ", _QUOTED.sub(" ", s.text)).strip(), spans


def pc_quotes(s: DeclaredSentence) -> list[str]:  # rule: 12.14.3
    """Quoted words the sentence puts in the PC's mouth: quotes with no declared speaker whose narration says
    "you say / ask / call ...". The only speech check on content (12.3.1b item 1: no words in the PC's mouth)."""
    narration, spans = voices(s)
    return spans if spans and not s.speaker and _PC_SAYS.search(narration) else []


def _names_in(text: str, idx: SceneIndex) -> list[str]:
    """Entity ids whose name or alias appears in `text` (whole words; the longest match per span wins)."""
    low = text.lower()
    hits: list[tuple[int, int, str]] = []
    for eid, names in idx.aliases.items():
        for n in names:
            for m in re.finditer(rf"\b{re.escape(n)}\b", low):
                hits.append((m.start(), m.end(), eid))
    hits.sort(key=lambda h: (h[0], -(h[1] - h[0])))
    out: list[str] = []
    end = -1
    for a, b, eid in hits:
        if a >= end:
            out.append(eid)
            end = b
    return list(dict.fromkeys(out))


def unknown_names(text: str, idx: SceneIndex, s: DeclaredSentence) -> list[str]:  # rule: 12.3.1a
    """Capitalised words mid-sentence (outside quoted speech's first word) that name no entity, no new element and
    no known place or people: a name the narration invented. ponytail: capital letters stand in for proper nouns;
    a quote's sentence starts are skipped, other false positives are words like "Rot" used as a curse."""
    plain = _QUOTED.sub(lambda m: m.group(0)[1:2].lower() + m.group(0)[2:], text)
    declared = {w.lower() for el in s.new for w in re.findall(r"[\w'-]+", el.name)}
    named = {w for names in idx.aliases.values() for n in names for w in n.split()}
    known = {re.sub(r"['’]s$", "", k) for k in idx.known_words}
    out = []
    for m in _PROPER.finditer(plain):
        w = re.sub(r"['’]s$", "", m.group(1))
        before = plain[:m.start()].rstrip(" \"“”'‘’(—-")
        if not before or before[-1] in ".!?:;":
            continue  # a sentence's (or a quoted sentence's) first word
        if w in _STOP_CAPS or w in known or w.lower() in declared or w.lower() in named:
            continue
        out.append(w)
    return list(dict.fromkeys(out))


def scan_sentence(s: DeclaredSentence, idx: SceneIndex, *, rules: Any = None,
                  names: Iterable[str] = ()) -> SentenceScan:  # rule: 12.3.1a
    # rule: 12.2.10
    """12.3.1a's code checks for one sentence, on the narrator's voice only (speech is testimony, 12.3.1b item 1):
    names and aliases against `about` (a resolvable name is added and logged; an invented one fails), numerals
    against quantities and cited values, sealed content (00.6.5); a pronoun clash is logged (off the blocking
    list); mechanics words (12.14.4, any voice) fail."""
    from engine.audit.screen import mechanics_in_fiction

    out = SentenceScan()
    text, _ = voices(s)
    subjects = idx.subjects(s)
    for eid in _names_in(text, idx):
        if eid not in subjects and eid != idx.pc:
            out.added_about.append(eid)
    for w in unknown_names(text, idx, s):
        out.undeclared_new += 1
        out.failures.append(Failure(why=f"names {w!r}, which is in neither the view nor its new elements",
                                    fix="redraft", store_value="use only names the view holds, or declare it new"))
    # numerals (12.2.10): a stated count cites the view's id for it
    allowed = {n for e in subjects | set(out.added_about) | {idx.pc or ""} for n in idx.numbers.get(e, [])}
    cited = idx.cited_words(s)
    allowed |= {tx.number_in(w) or -1 for w in re.findall(r"\w+", cited)} | {int(d) for d in re.findall(r"\d+", cited)}
    for w in tx.words(text):
        n = int(w) if w.isdigit() else _NUM_WORDS.get(w)
        if n is None or n in allowed:
            continue
        if w.isdigit() or any(tx.has_phrase(text, f"{w} {q}") for q in _QTY_NOUNS):
            out.failures.append(Failure(why=f"states the count {w!r}, which the view does not hold", fix="redraft",
                                        store_value="drop the count or use the view's"))
            break
    # pronouns: the one person this sentence names or is declared about (the PC aside; a cited line's people
    # are not counted), when every one of them has stored pronouns
    people = {e for e in [*s.about, *_names_in(text, idx)] if e != idx.pc and e in idx.aliases}
    people = {e for e in people if not e.startswith(("loc.", "obj.", "item.", "fac.", "thr.", "clk."))}
    if len(people) == 1 and not s.new and all(e in idx.pronouns for e in people):
        g = idx.pronouns[next(iter(people))]
        said = _QUOTED.sub("", text)
        wrong = (g == "f" and _HE.search(said) and not _SHE.search(said)) or (
            g == "m" and _SHE.search(said) and not _HE.search(said))
        if wrong:
            out.logged.append(("identity", "the pronoun does not match the person's"))
    mech = mechanics_in_fiction(s.text, rules=rules, names=names)
    if mech:
        out.failures.append(Failure(why=f"mechanics in the fiction: {', '.join(mech)}", fix="redraft",
                                    store_value="say it in the world's words"))
    low = text.lower()
    leak = next((x for x in idx.sealed if re.search(rf"\b{re.escape(x)}\b", low)), None)
    if leak:
        out.failures.append(Failure(why="names something hidden", fix="cut"))
    return out


def coverage(sents: Iterable[DeclaredSentence], must: Iterable[str]) -> list[str]:  # rule: 12.3.1a
    """Must-name handles no sentence cites (12.3.1a item 3)."""
    cited = {r for s in sents for r in s.refs}
    return [h for h in must if h not in cited]


def known_as(el: NewElement, idx: SceneIndex) -> str | None:  # rule: 00.6.6
    """The entity a "new" element already is (its name is one of the scene's names): it is spoken of, not new."""
    want = re.sub(r"^(?:the|a|an)\s+", "", el.name.strip().lower())
    return next((eid for eid, names in idx.aliases.items() if want and want in names), None)


def t2_delivered(el: NewElement, s: DeclaredSentence, idx: SceneIndex) -> bool:  # rule: 12.14.13
    """A T2 element passes only when a line this sentence cites delivers it (its name's words are in that line)."""
    lines = " ".join(idx.handles.get(r, "") for r in s.refs)
    return bool(lines) and tx.covers(el.name, lines, ratio=0.5)


__all__ = ["ELEMENT_TIERS", "DeclaredSentence", "Failure", "NewElement", "SceneIndex", "SentenceScan", "coverage", "known_as",
           "joined", "mention_of", "parse_output", "pc_quotes", "scan_sentence", "split", "t2_delivered", "tier_of",
           "unknown_names", "voices"]
