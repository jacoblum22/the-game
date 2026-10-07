"""The safety screen (FR-036; 12.5, 12.5.6, 12.5.7; T107). Separate from the claim check and never a Checker field:
safety changes content, consistency changes truth, and they keep separate ledgers (12.3.7).

    entries = safety_prefs(state)                          # the player's lines, veils and flags (pref.* facts)
    res = screen_safety(draft, entries)                    # T10: a line = cut; a veil shown in detail = flag
    hit = matches_line(table_row_text, entries)            # screen a table roll or generator output before use
    reply = handle_safety_part("skip this, too much")      # T2: a SAFETY part, handled before anything else

Preferences (14.5.1, T-14-1): current facts with predicate `pref.safety.lines` / `pref.safety.veils` /
`pref.safety.flags` on any subject (14.5.1 names the subject `player`; `world` when there is no such entity).
Each value is a list of entries, each a topic string or `{"topic": str, "tags": [str]}` (14.5.3).
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable, Sequence
from typing import Any, Literal

from pydantic import BaseModel, Field

from engine import ids
from engine.audit import text as tx
from engine.store.events import WORLD, Event

Kind = Literal["line", "veil", "flag"]
PREF_KEYS: dict[Kind, str] = {"line": "pref.safety.lines", "veil": "pref.safety.veils", "flag": "pref.safety.flags"}
PLAYER = "player"
VEIL_MAX_WORDS = 20  # a veil's one plain summary sentence (12.5.6); longer reads as detail
_IRREGULAR = {"children": "child", "men": "man", "women": "woman", "mice": "mouse", "teeth": "tooth",
              "feet": "foot", "geese": "goose", "people": "person", "lice": "louse", "wolves": "wolf",
              "knives": "knife", "lives": "life", "corpses": "corpse", "selves": "self", "thieves": "thief"}


class SafetyEntry(BaseModel):
    kind: Kind
    topic: str
    tags: list[str] = Field(default_factory=list)


class SafetyHit(BaseModel):
    kind: Kind
    topic: str
    sentence: int
    span: str


class SafetyResult(BaseModel):
    ok: bool  # no line matched and no veil shown in detail
    cuts: list[SafetyHit] = Field(default_factory=list)  # line matches: cut these sentences
    veils: list[SafetyHit] = Field(default_factory=list)  # veil matches (allowed as one plain sentence)
    flags: list[SafetyHit] = Field(default_factory=list)  # flagged topics present (pause before narrating them)
    reasons: list[str] = Field(default_factory=list)

    @property
    def review(self) -> bool:
        return bool(self.cuts or self.flags or not self.ok)


# ------------------------------------------------------------------------------------------- the record


def safety_prefs(state: Any) -> list[SafetyEntry]:
    """The player's lines, veils and flags from the current `pref.safety.*` facts."""
    out: list[SafetyEntry] = []
    for kind, pred in PREF_KEYS.items():
        for f in state.facts.values():
            if f.predicate != pred:
                continue
            vals = f.value if isinstance(f.value, list) else [f.value]
            for v in vals:
                if isinstance(v, str) and v.strip():
                    out.append(SafetyEntry(kind=kind, topic=v.strip()))
                elif isinstance(v, dict) and v.get("topic"):
                    out.append(SafetyEntry(kind=kind, topic=str(v["topic"]), tags=[str(t) for t in v.get("tags", [])]))
    return out


def safety_fact(entry: SafetyEntry, state: Any, mint: Callable[[str], str], *, source: str = "player_accepted") -> Event:
    """A `fact_set` adding `entry` to the player's record (supersedes the current list; 14.5.1)."""
    subject = PLAYER if PLAYER in state.entities else WORLD
    pred = PREF_KEYS[entry.kind]
    cur_id = state.current_fact_id(subject, pred)
    cur = list(state.facts[cur_id].value) if cur_id else []
    return Event.of("fact_set", {"source": source}, source="player", rule_id="14.5.1", fact_id=mint(ids.FACT),
                    subject=subject, predicate=pred, value=[*cur, {"topic": entry.topic, "tags": entry.tags}],
                    visibility="shown", supersedes=cur_id)


# ------------------------------------------------------------------------------------------- matching


def _norm_word(w: str) -> str:
    return tx.stem(_IRREGULAR.get(w, w))


def _keys(entry: SafetyEntry) -> list[list[str]]:
    """Stem groups that each signal the topic: the topic's content words (all must appear) and each tag's leaf."""
    groups = [[_norm_word(w) for w in tx.words(entry.topic) if w not in tx.STOP and len(w) > 1]]
    for tag in entry.tags:
        leaf = tag.rsplit(".", 1)[-1]
        groups.append([_norm_word(w) for w in tx.words(leaf) if w not in tx.STOP and len(w) > 1])
    return [g for g in groups if g]


def _word_hit(stem: str, sentence_stems: Sequence[str], sentence_words: Sequence[str]) -> bool:
    if stem in sentence_stems:
        return True
    return len(stem) >= 4 and any(w.startswith(stem) for w in sentence_words)  # "spider" in "spiderweb"


def _match(entry: SafetyEntry, sentence: str) -> bool:  # rule: 12.5.6
    """Case-insensitive phrase or stem match of the topic (every content word) or of any tag's leaf words."""
    if tx.has_phrase(sentence, entry.topic):
        return True
    ws = tx.words(sentence)
    stems = [_norm_word(w) for w in ws]
    return any(all(_word_hit(s, stems, ws) for s in group) for group in _keys(entry))


def _sentences(draft: str) -> list[str]:
    return [p for p in re.split(r"(?<=[.!?])\s+|\n+", draft.strip()) if p.strip()]


def matches_line(content: str, entries: Iterable[SafetyEntry]) -> SafetyEntry | None:  # rule: 12.5.6
    """The first line `content` falls under (screen a table roll, generator output or random event before use)."""
    for e in entries:
        if e.kind == "line" and _match(e, content):
            return e
    return None


def screen_safety(draft: str, entries: Iterable[SafetyEntry] | Any) -> SafetyResult:  # rule: 12.5.6
    """Check a draft against the player's lines and veils (T10). `entries`: SafetyEntry list, or a state."""
    es = list(entries) if isinstance(entries, list | tuple) else safety_prefs(entries)
    sents = _sentences(draft)
    res = SafetyResult(ok=True)
    for e in es:
        hits = [SafetyHit(kind=e.kind, topic=e.topic, sentence=i, span=s) for i, s in enumerate(sents) if _match(e, s)]
        if not hits:
            continue
        if e.kind == "line":
            res.cuts += hits
            res.reasons.append(f"line '{e.topic}' appears (12.5.6): cut")
        elif e.kind == "veil":
            res.veils += hits
            if len(hits) > 1 or any(len(tx.words(h.span)) > VEIL_MAX_WORDS for h in hits):
                res.reasons.append(f"veil '{e.topic}' shown in detail (12.5.6): one plain sentence only")
        else:
            res.flags += hits
            res.reasons.append(f"flagged topic '{e.topic}' (12.5.6): pause before narrating it")
    res.ok = not res.cuts and not any(r.startswith("veil") for r in res.reasons)
    return res


def flag_prompt(topic: str) -> str:  # rule: 12.5.6
    return f"[FLAG] This touches {topic}. Continue, veil it, or steer away?"


# ------------------------------------------------------------------------------------------- the SAFETY part

REFRAMINGS = ("reframe", "refocus", "replace", "redirect", "reshape")  # 12.5.7, default order
_RECORD = re.compile(r"\b(line|veil|flag)\s*[:\-]\s*(.+)$", re.IGNORECASE)


class SafetyResponse(BaseModel):
    """What the DM does with a SAFETY part (12.5.7): stop, acknowledge in one OOF line without asking why, and
    apply a re-framing (the player's if named, else the default order). Mechanics never change."""

    pause: bool = True
    oof_line: str
    reframing: str  # one of REFRAMINGS
    chosen_by: Literal["player", "default"]
    options: list[str] = Field(default_factory=lambda: list(REFRAMINGS))
    record: SafetyEntry | None = None  # a line, veil or flag the player asked to record (14.5.1)
    ledger: dict[str, Any] = Field(default_factory=dict)  # the safety ledger entry (never a correction, 12.3.7)


def handle_safety_part(text: str) -> SafetyResponse:  # rule: 12.5.7
    low = text.lower()
    named = next((r for r in REFRAMINGS if re.search(rf"\b{r}\b", low)), None)
    record = None
    m = _RECORD.search(text.strip())
    if m:
        record = SafetyEntry(kind=m.group(1).lower(), topic=m.group(2).strip().rstrip("."))  # type: ignore[arg-type]
    oof = "[OK] Adjusting." if named else "[OK] Adjusting. (Say how, or I'll reframe it.)"
    return SafetyResponse(oof_line=oof, reframing=named or REFRAMINGS[0], chosen_by="player" if named else "default",
                          record=record,
                          ledger={"kind": "adjust", "words": text, "reframing": named or REFRAMINGS[0],
                                  "recorded": record.model_dump() if record else None})
