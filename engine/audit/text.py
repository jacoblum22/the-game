"""Small text helpers the audit code shares: tokens, crude stems, number words, phrase matching.

Deterministic and dependency-free. They compare short model-written strings ("carries" / "a short sword") with
store values; they are deliberately conservative (a stem must match a whole word).
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Any

STOP = frozenset("""
a an the and or but of to in on at by for from with into onto over under up down out off as is are was were be
been being it its this that these those there here he she they them him her his hers their theirs you your yours
i me my we our us who whom which what when where why how not no nor so than then too very just now still yet
has have had do does did can could will would shall should may might must also all any each every some one
own same other such only again once more most much many few both either neither upon about against between
through during before after above below while within without toward towards across along around behind beside
""".split())

NUMBER_WORDS = {
    "zero": 0, "no": 0, "none": 0, "one": 1, "a": 1, "an": 1, "single": 1, "lone": 1, "two": 2, "pair": 2,
    "both": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "dozen": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
    "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
    "hundred": 100,
}

_WORD = re.compile(r"[a-z0-9]+(?:'[a-z]+)?")


def norm(text: Any) -> str:
    """Lower case, ids and underscores as spaces, punctuation dropped."""
    s = str(text).lower().replace("_", " ")
    s = re.sub(r"\b[a-z]+\.([a-z])", r"\1", s)  # npc.mara_voss -> mara voss
    return " ".join(_WORD.findall(s))


def stem(word: str) -> str:
    w = word.lower().strip("'")
    if w.endswith("'s"):
        w = w[:-2]
    for suf in ("ingly", "edly", "ing", "ied", "ies", "ed", "es", "ly", "s"):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            w = w[: -len(suf)]
            if suf in ("ied", "ies"):
                w += "y"
            break
    if len(w) >= 4 and w[-1] == w[-2] and w[-1] not in "aeiouls":  # stopped -> stopp -> stop
        w = w[:-1]
    return w


def words(text: Any) -> list[str]:
    return _WORD.findall(norm(text))


def content(text: Any) -> set[str]:
    """Stems of the content words (stop words and one-letter words dropped)."""
    return {stem(w) for w in words(text) if w not in STOP and len(w) > 1}


def overlap(a: Any, b: Any) -> set[str]:
    return content(a) & content(b)


def covers(needle: Any, hay: Any, *, ratio: float = 0.5) -> bool:
    """At least `ratio` of `needle`'s content stems (and at least one) appear in `hay`."""
    n = content(needle)
    if not n:
        return False
    hit = n & content(hay)
    return bool(hit) and len(hit) >= ratio * len(n)


def same(a: Any, b: Any) -> bool:
    """Equal after normalising, or one's content stems are all in the other's."""
    na, nb = norm(a), norm(b)
    if na == nb:
        return True
    ca, cb = content(a), content(b)
    return bool(ca) and bool(cb) and (ca <= cb or cb <= ca)


def has_phrase(text: str, phrase: str) -> bool:
    """`phrase` as whole words in `text`, case-insensitive; each word may carry a plural/verb suffix."""
    ws = [re.escape(w) for w in words(phrase)]
    if not ws:
        return False
    pat = r"\b" + r"\W+".join(w + r"(?:s|es|ed|ing|d)?" for w in ws) + r"\b"
    return re.search(pat, text, re.IGNORECASE) is not None


def number_in(text: Any) -> int | None:
    """The first number in `text`, as digits or a number word ("last two arrows" -> 2)."""
    for w in words(text):
        if w.isdigit():
            return int(w)
        if w in NUMBER_WORDS and w not in ("a", "an", "no"):
            return NUMBER_WORDS[w]
    ws = words(text)
    if ws and ws[0] in ("no", "none"):
        return 0
    return None


def any_phrase(text: str, phrases: Iterable[str]) -> str | None:
    for p in phrases:
        if has_phrase(text, p):
            return p
    return None
