"""The T10 screen (PR-12-1 step T10; T046): the Checker's flags combined with code checks, before delivery.

    res = screen_draft(fiction, flags=checker["screen"], record=record, verdicts=verdicts,
                       safety=screen_safety(fiction, state), pause_blocks=["[OFFER] ..."], rules=rules)
    if not res.passed: back to T7 with res.reasons          # TurnRecord.screen = res.screen

Checks: input fidelity ×3 (12.2.7), a next step exists (01.11.4), no mechanics in the fiction (12.14.4: digits,
dice, and rules words derived from rules data, matched only in forms ordinary prose does not use), the open
prompt or exactly one pause block (12.14.9), PC agency (12.14.3, from the verdicts), safety (12.5.6, separate).
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from functools import lru_cache
from typing import Any

from pydantic import BaseModel, Field

from engine.audit import text as tx
from engine.audit.claims import Verdict
from engine.audit.safety import SafetyResult
from engine.dm.adjudication import AdjudicationRecord

ANSWERED_CLASSES = ("DECLARATION", "FICTION_QUESTION", "SPEECH")  # 12.2.7 (1)
PAUSE_LABELS = ("OFFER", "NEAR MISS", "NEAR_MISS", "REDIRECT", "CHOICE", "CLARIFY", "ASSUMING", "CREATE", "SEED",
                "RETIRE", "FLAG", "LAST CHANCE", "LAST_CHANCE", "CUT?", "BUDGET")
_BLOCK = re.compile(r"^\s*\[([A-Z][A-Z _?\-—0-9/]*)\]", re.MULTILINE)

# Always rules talk in fiction (T-00-22 and 12.14.4), case-insensitive unless noted.
_ALWAYS = [
    r"\d+", r"\bd(?:4|6|8|10|12|20|100)\b", r"\b(?:natural|nat)\s+(?:twenty|one|20|1)\b",
    r"\bsuccess at (?:a )?cost\b", r"\bnear[- ]miss\b", r"\bcritical (?:success|failure|hit|fail)\b",
    r"\bhit points?\b", r"\bsaving throws?\b", r"\bskill checks?\b", r"\bdifficulty class\b",
    r"\bexperience points\b", r"\bfate points?\b", r"\bdifficulty (?:tier|rating|number)\b",
    r"\b(?:make|makes|made|making|roll|rolls|rolled|rolling|pass|passes|passed|fail|fails|failed) (?:a|an|the|your|"
    r"his|her|their) (?:\w+ )?(?:check|save|roll)\b(?!\s+of\b)",
    r"\b(?:your|his|her|their|the|a|an) (?:dice )?roll\b(?!\s+(?:of|over|away|back|down|aside)\b)",
    r"\broll(?:s|ed)? (?:a |an )?(?:high|low|well|poorly|badly)\b",
    r"\b(?:stakes are|the stakes:) (?:safe|risky|dire)\b", r"\bdelivered reach\b", r"\breach (?:limited|standard)\b",
    r"\b(?:bonus|penalty|modifier)\b", r"\bmana\b", r"\b(?:level|class) (?:up|feature)\b",
    r"\bS[1-5]\b", r"\bcond\.\w+", r"\b(?:tbl|trg|pref|lic|ab|adv|anc|verb|clk|cost)\.[a-z_.]+",
    r"\b[a-z]+_[a-z_]+\b",  # a raw snake_case id (critical_success, off_balance)
    # the bookkeeping named in prose (P-045 "the wound and ruin the record holds"); a shop or a ledger still passes
    r"\bthe (?:record|store|engine|adjudication)(?:'s)? (?:holds?|held|has|had|says|said|shows?|names?|gives?|keeps?)\b",
]
_CASED = [r"\bDC\b", r"\bXP\b", r"\bHP\b", r"\bVitality\b", r"\bFocus (?:points?|cost)\b", r"\bG[0-4]\b"]


@lru_cache(maxsize=4)
def _rules_terms(rules_key: int) -> tuple[list[str], list[str], list[str]]:
    """(attribute names, DC tier names, condition names) from rules data, lower case."""
    rules = _RULES[rules_key]
    attrs = sorted({str(a.get("name", k)).lower() for k, a in rules.attributes.items()} | set(rules.attributes))
    tiers = sorted({str(t.get("name", t["id"])).lower() for t in rules.resolution["dc_tiers"]})
    conds = sorted({str(c.get("name", k)).lower() for k, c in rules.conditions.items()})
    return attrs, tiers, conds


_RULES: dict[int, Any] = {}


def _terms(rules: Any) -> tuple[list[str], list[str], list[str]]:
    if rules is None:
        from engine.data.loader import load_rules

        rules = load_rules()
    _RULES[id(rules)] = rules
    return _rules_terms(id(rules))


def mechanics_in_fiction(fiction: str, *, rules: Any = None, names: Iterable[str] = ()) -> list[str]:
    # rule: 12.14.4
    """Spans of `fiction` that are game numbers or rules words. Attribute, tier and condition names count only
    in rules forms ("a Might check", "your Agility", "a Hard climb", "you are Frightened"): their ordinary
    lower-case uses ("you might", "her resolve", "a hard climb", "frightened eyes") pass."""
    attrs, tiers, conds = _terms(rules)
    allowed = {n.lower() for n in names}
    found: list[tuple[int, str]] = []

    def add(m: re.Match[str]) -> None:
        span = m.group(0).strip()
        if span and span.lower() not in allowed:
            found.append((m.start(), span))

    for pat in _ALWAYS:
        for m in re.finditer(pat, fiction, re.IGNORECASE):
            add(m)
    for pat in _CASED:
        for m in re.finditer(pat, fiction):
            add(m)
    attr_alt = "|".join(re.escape(a) for a in attrs)
    for m in re.finditer(rf"\b(?:{attr_alt})\s+(?:check|roll|save|score|bonus|modifier|test)s?\b", fiction, re.IGNORECASE):
        add(m)
    for m in re.finditer(rf"\b(?:{'|'.join(re.escape(t) for t in tiers)})\s+(?:DC|difficulty|check|tier|task)\b",
                         fiction, re.IGNORECASE):
        add(m)
    # Title-case rules names in mid-sentence ("your Might", "a Hard climb", "you are Frightened")
    titled = sorted({w[0].upper() + w[1:] for w in [*attrs, *tiers, *conds] if len(w) > 2}, key=len, reverse=True)
    for term in titled:
        if term.lower() in allowed:
            continue
        for m in re.finditer(rf"\b{re.escape(term)}\b", fiction):
            if not _sentence_start(fiction, m.start()):
                found.append((m.start(), term))
    named = [(m.start(), m.end()) for n in allowed if n for m in re.finditer(rf"\b{re.escape(n)}\b", fiction, re.IGNORECASE)]
    seen: set[tuple[int, str]] = set()
    out = []
    for pos, span in sorted(found):
        if any(pos >= p and pos < p + len(s) for p, s in seen):
            continue  # inside a span already reported
        if any(a <= pos < b for a, b in named):
            continue  # part of an entity's name ("the Broken Tower")
        seen.add((pos, span))
        out.append(span)
    return out


def _sentence_start(text: str, pos: int) -> bool:
    before = text[:pos].rstrip(" \"“'‘(")
    return not before or before[-1] in ".!?:\n"


def _last_sentence(fiction: str) -> str:
    parts = [p for p in re.split(r"(?<=[.!?…])[\"”’']?\s+|\n+", fiction.strip()) if p.strip()]
    return parts[-1].strip() if parts else ""


def ends_on_prompt(fiction: str) -> bool:  # rule: 12.14.9
    """The fiction hands the moment back with a question (code test; an awaiting image is the Checker's flag)."""
    last = _last_sentence(fiction).rstrip("\"”’' ")
    return last.endswith("?")


def numbered_options(fiction: str) -> bool:  # rule: 12.14.9
    """A numbered list of options (never in fiction)."""
    return len(re.findall(r"(?m)^\s*(?:\d+|[a-d])[.)]\s+\S", fiction)) >= 2


def pause_blocks(blocks: Iterable[str]) -> list[str]:
    """The labels among OOF blocks that are pause blocks (12.15)."""
    out = []
    for b in blocks:
        for m in _BLOCK.finditer(b):
            label = m.group(1).split("—")[0].split(" n/")[0].strip()
            if any(label.startswith(p) for p in PAUSE_LABELS):
                out.append(label)
    return out


_QUOTE = re.compile(r"[\"“]([^\"”]+)[\"”]")
_YOU = re.compile(r"\byou(r|rs|rself)?\b", re.I)


def echoed_quotes(fiction: str, said: Iterable[str]) -> list[str]:  # rule: 12.2.7
    """The player's quoted lines (4+ words) that the fiction quotes back with no "you" in the attribution around
    them: the last sentence before the quote and the clause after it up to the sentence's end (P-068).
    '"Who is it?" you ask.' is the PC's line; 'He laughs. "Who is it?" His thumbs...' is an NPC echoing it."""
    # ponytail: attribution by a "you" nearby; a parser of speech tags if this misfires
    mine = {tx.norm(q) for t in said for q in _QUOTE.findall(t) if len(tx.words(q)) >= 4}
    out = []
    for m in _QUOTE.finditer(fiction):
        if tx.norm(m.group(1)) not in mine:
            continue
        if not fiction[:m.start()].rsplit("\n", 1)[-1].strip():  # opens the text or a paragraph: the PC's line
            continue  # restated as declared, no one else speaking (P-102)
        before = re.split(r"(?<=[.!?])\s+", fiction[:m.start()].rstrip())[-1]
        after = re.match(r"[^.!?\"“]*", fiction[m.end():]).group(0)  # type: ignore[union-attr]
        after = after if after.strip()[:1].islower() or after.strip()[:1] in (",", "") else ""
        if not _YOU.search(before) and not _YOU.search(after):
            out.append(m.group(1))
    return out


class ScreenResult(BaseModel):
    passed: bool
    reasons: list[str] = Field(default_factory=list)
    screen: dict[str, Any] = Field(default_factory=dict)  # TurnRecord.screen (data-model.md §4)


def screen_draft(fiction: str, *, flags: Mapping[str, Any] | None = None, record: AdjudicationRecord | None = None,
                 verdicts: Sequence[Verdict] = (), safety: SafetyResult | None = None,  # rule: 12.14.3
                 pause_blocks_text: Iterable[str] = (), rules: Any = None,  # rule: 01.11.4
                 names: Iterable[str] = ()) -> ScreenResult:  # rule: 12.2.7
    """Combine the Checker's screen flags with the code checks. A missing flag reads as passing; a code check
    can only fail a draft the Checker passed, never pass one it failed (except mechanics spans the fiction does
    not contain)."""
    f = dict(flags or {})
    rec = record or AdjudicationRecord()
    reasons: list[str] = []
    # 12.2.7 (1) acknowledged: the flag only. With no message part to answer (the opening, a scene opening, a recap)
    # there is nothing to acknowledge or substitute [playtest 2026-10-07]. Speech and questions are not tracked part
    # by part: the word-overlap "answered" check (about 6% precise) is retired [revision: R2-J; DL-12-101; spec 019]
    asked = any(p.cls in ANSWERED_CLASSES for p in rec.parts)
    ack = bool(f.get("intent_acknowledged", True)) or not asked
    if not ack:
        reasons.append("12.2.7: the response does not take up what the player tried")
    # 12.2.7 (2) not substituted
    substituted = bool(f.get("intent_substituted", False)) and asked
    if substituted:
        reasons.append("12.2.7: the PC attempts something other than what the player declared")
    # 12.2.7 (3) not silently reset: no contradiction of the store
    if any(v.verdict == "contradicted" for v in verdicts):
        reasons.append("12.2.7: the draft contradicts the store (silent reset)")
    # 01.11.4 a next step exists (a pause point is one)
    next_step = bool(f.get("next_step_exists", True)) or rec.pause is not None
    if not next_step:
        reasons.append("01.11.4: no concrete next step for the player")
    # 12.14.4 no mechanics in the fiction
    mech = mechanics_in_fiction(fiction, rules=rules, names=names)
    for span in f.get("mechanics_in_fiction", []) or []:
        if span and span in fiction and span not in mech and not _ordinary(span):
            mech.append(span)
    if mech:
        reasons.append(f"12.14.4: mechanics in the fiction: {', '.join(mech)}")
    # 12.14.9 the open prompt, or exactly one pause block
    pauses = pause_blocks(pause_blocks_text)
    if rec.pause is not None or pauses:
        ends_ok = len(pauses) == 1
        if not ends_ok:
            reasons.append(f"12.14.9: a pause point ends with exactly one pause block (found {len(pauses)})")
    else:
        ends_ok = (ends_on_prompt(fiction) or bool(f.get("ends_on_prompt_or_one_pause", False))) \
            and not numbered_options(fiction)
        if not ends_ok:
            reasons.append("12.14.9: the response does not end on an open prompt")
    # 12.14.3 PC agency
    agency_ok = not any(v.verdict == "pc_agency" for v in verdicts)
    if not agency_ok:
        reasons.append("12.14.3: the draft speaks or decides for the PC")
    echoed = echoed_quotes(fiction, [p.text for p in rec.parts])
    if echoed:
        reasons.append(f"12.2.7: an NPC answers with the player's own words ({echoed[0]}); write the NPC's reply")
    # 12.5.6 safety (separate screen)
    safety_ok = safety.ok if safety is not None else True
    if safety is not None and not safety.ok:
        reasons += safety.reasons
    screen = {"intent_acknowledged": ack, "intent_substituted": substituted, "next_step_exists": next_step,
              "mechanics_in_fiction": mech, "ends_on_prompt_or_one_pause": ends_ok, "pc_agency_ok": agency_ok,
              "safety_ok": safety_ok}
    return ScreenResult(passed=not reasons, reasons=reasons, screen=screen)


_ORDINARY = {"success", "succeed", "fail", "failure", "check", "roll", "stakes", "level", "critical", "tier",
             "focus", "band"}


def _ordinary(span: str) -> bool:
    """A Checker span that is a lone ordinary word ("check the door"); the code patterns judge those."""
    ws = tx.words(span)
    return len(ws) == 1 and tx.stem(ws[0]) in {tx.stem(w) for w in _ORDINARY}
