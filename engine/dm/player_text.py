"""Player-facing text: rule citations out, internal data ids replaced by their display names (12.14.4, 12.15).

Out-of-fiction blocks, seed and creation prompts, pause prompts and choice labels are written by the engine from
rules data, so they can carry the rules' own bookkeeping: section refs ("(05.7.10 item 6)", "PR-10-10"), chapter
possessives ("15's `magic` refusal") and data ids ("verb.grapple", "terrain.plains.farmland"). `clean` removes
the first two and names the third, from `engine.data.loader` (verbs, licences, cost menus, conditions, tags such
as deed / terrain / faction tags, and any data entry with a `name`), falling back to the id's last segment in
words. The narrator's fiction is never passed through here (the 12.3 screen owns it).

    clean("Grapple (verb.grapple) (05.7.10 item 6)", rules)  # -> "Grapple (Grapple)" ... ids named, refs gone
    clean_response(resp, rules, state)                        # blocks, prompt, labels; fiction only pre-play
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from engine.dm.response import Response

# a section id: 05.7.10, 12.16.2, 08.6 (two-digit chapter, at least one dotted part)
_SECTION = r"\b\d{2}(?:\.\d+)+\b"
_CODE = r"\b(?:PR|T|WE|OEQ|DL|INV|FR|SC|I|V)-\d{2}(?:-[\w]+)*\b|\bT-\d{2}-\w+\b"
_CHAPTER = r"\b(?:chapter|ch\.)\s*\d{2}\b"
# a citation inside a parenthetical: a section (optionally "item N"), a code id, or a chapter
_CITE = re.compile(rf"(?:{_SECTION}(?:'s)?(?:\s+items?\s+\d+(?:\s*[-–,]\s*\d+)*)?|{_CODE}|{_CHAPTER}(?:'s)?)")
_POSSESSIVE = re.compile(rf"(?:{_SECTION}|\b\d{{2}}|{_CHAPTER})'s\b")
_PAREN = re.compile(r"\s*\(([^()]*)\)")
_SEP = r"[,;:—–-]"

# data ids by prefix (rules data and the world seed); entity ids are named from state when given
_ID_PREFIXES = ("verb", "cost", "deed", "terrain", "org", "kf", "lic", "cond", "ab", "adv", "kit", "item", "orig",
                "eff", "trait", "conduct", "creature", "material", "situation", "harm", "tbl", "trg", "flag",
                "npc", "pc", "foe", "ally", "loc", "fac", "thr", "rum", "clu", "obj", "clk")
_ID = re.compile(rf"\b(?:{'|'.join(_ID_PREFIXES)})\.(?:\*|[a-z0-9_]+(?:\.[a-z0-9_]+)*(?:\.\*)?)(?!\w)(?!\.\w)")
_WILDCARD = {"lic": "licences", "deed": "deeds", "verb": "basic verbs", "cost": "costs", "cond": "conditions",
             "ab": "abilities", "terrain": "terrains", "org": "factions", "kf": "keepers"}
_SNAKE = re.compile(r"\b[a-z][a-z0-9]*(?:_[a-z0-9]+)+\b")

_INDEX: dict[str, dict[str, str]] = {}


# ------------------------------------------------------------------------------------------- names


def _walk(x: Any, out: dict[str, str]) -> None:
    if isinstance(x, Mapping):
        key = x.get("id") or x.get("option")
        name = x.get("name") or x.get("label")
        if isinstance(key, str) and "." in key and isinstance(name, str) and name.strip() and key not in out:
            out[key] = name.strip()
        for v in x.values():
            if isinstance(v, Mapping | list | tuple):
                _walk(v, out)
    elif isinstance(x, list | tuple):
        for v in x:
            _walk(v, out)


def _names(rules: Any) -> dict[str, str]:
    """{data id: display name} over every rules data file (built once per rules version)."""
    if rules is None:
        return {}
    key = str(getattr(rules, "hash", id(rules)))
    if key not in _INDEX:
        out: dict[str, str] = {}
        try:
            for f in rules.files:
                _walk(rules.doc(f), out)
            for tid, tag in dict(rules.tags).items():
                if tag.get("name"):
                    out[tid] = str(tag["name"])
        except (AttributeError, KeyError, TypeError):
            pass
        _INDEX.clear()
        _INDEX[key] = out
    return _INDEX[key]


def humanize(data_id: str) -> str:
    """The id's last segment in words: `kf.saint` -> "saint", `terrain.plains.farmland` -> "farmland"."""
    return data_id.rsplit(".", 1)[-1].replace("_", " ")


def display_name(data_id: str, rules: Any = None, names: Mapping[str, str] | None = None) -> str:
    """An id's display name: an entity's name from `names`, a rules entry's name, else its last segment."""
    if names and data_id in names:
        return names[data_id]
    if data_id.endswith(".*") or data_id.endswith(".") or "." not in data_id:
        return _WILDCARD.get(data_id.split(".", 1)[0], humanize(data_id.rstrip(".*")))
    hit = _names(rules).get(data_id)
    return hit if hit else humanize(data_id)


# ------------------------------------------------------------------------------------------- cleaning


def _paren(m: re.Match[str]) -> str:
    inner = m.group(1)
    if not _CITE.search(inner) and not re.search(r"\b\d{2}'s\b", inner):
        return m.group(0)
    if _POSSESSIVE.search(inner):
        return ""  # "(02.2.2's creation default reads it)", "(15's `magic` refusal)": all bookkeeping
    rest = re.sub(rf"\s*(?:{_SEP}\s*)?(?:{_CITE.pattern})\s*(?:{_SEP})?\s*", " ", inner).strip(" ,;:—–-")
    rest = re.sub(r"\s{2,}", " ", rest)
    if not re.search(r"[A-Za-z]{2,}", rest) or re.fullmatch(r"(?:items?|see|cf\.?|per)(?:\s+\d+)*", rest):
        return ""
    lead = m.group(0)[: len(m.group(0)) - len(m.group(0).lstrip())]
    return f"{lead}({rest})"


def strip_citations(text: str) -> str:  # rule: 12.14.4
    """Remove rule citations: parentheticals that only cite, the citation part of mixed ones, chapter possessives
    and bare section or procedure ids."""
    out = _PAREN.sub(_paren, text)
    out = re.sub(rf"\b{_CHAPTER} leaves\b", "the rules leave", out)
    out = re.sub(rf"{_CHAPTER}'s\s+", "", out)
    out = re.sub(_CHAPTER, "the rules", out)
    out = re.sub(rf"(?:{_SECTION}|\b\d{{2}})'s\s+", "", out)  # "08.6's crafting" -> "crafting"
    out = re.sub(r"\s*\b\d{2}\.\d+\.\d+(?:\.\d+)*\b(?:\s+items?\s+\d+)?", "", out)
    out = re.sub(rf"\s*(?:{_CODE})", "", out)
    out = out.replace("`", "")
    return re.sub(r"(?<=\w)[ \t]+([,.;:?!])", r"\1", out)


def name_ids(text: str, rules: Any = None, names: Mapping[str, str] | None = None) -> str:
    """Replace data ids with display names, then snake_case words with plain words."""
    out = _ID.sub(lambda m: display_name(m.group(0), rules, names), text)
    return _SNAKE.sub(lambda m: m.group(0).replace("_", " "), out)


_SECOND = [(r"(?:PC|character)'s\b", "your"), (r"(?:PC|character) is\b", "you are"),
           (r"(?:PC|character) has\b", "you have"), (r"(?:PC|character) was\b", "you were"),
           (r"(?:PC|character)\b(?! sheet| creation| record)", "you")]


def second_person(text: str, *, character: bool = True) -> str:  # rule: 12.14.1
    """Rules and seed data speak of "the PC" / "the character"; the player is "you" ("a stranger asks after the PC
    by name" -> "a stranger asks after you by name"). `character=False` leaves "the character" alone."""
    out = text
    for pat, rep in _SECOND:
        if not character:
            pat = pat.replace("(?:PC|character)", "PC")
        out = re.sub(r"\bthe " + pat, rep, out)
        out = re.sub(r"\bThe " + pat, rep[:1].upper() + rep[1:], out)
    return out


def clean(text: str, rules: Any = None, names: Mapping[str, str] | None = None) -> str:  # rule: 12.14.4
    """Player-facing text without rule citations or internal ids (idempotent); "the PC" is "you"."""
    if not text:
        return text
    return second_person(name_ids(strip_citations(text), rules, names), character=False)


def entity_names(state: Any) -> dict[str, str]:
    """{entity id: name} for entities the player may see named (shown or available)."""
    if state is None:
        return {}
    out: dict[str, str] = {}
    for eid, e in getattr(state, "entities", {}).items():
        if getattr(e, "visibility", "shown") in ("shown", "available") and eid not in getattr(state, "seals", {}):
            from engine.store.views import display_name

            out[eid] = display_name(state, eid) if hasattr(state, "knowledge") else e.name  # 12.10.2
    return out


def clean_response(resp: Response, rules: Any = None, state: Any = None) -> Response:  # rule: 12.15
    """The Response with every engine-written player string cleaned: OOF blocks, the pause's prompt and choice
    labels, the budget notice, and the fiction only in the seed and creation phases (engine text, not the
    narrator's)."""
    names = entity_names(state)

    def c(t: str) -> str:
        return clean(t, rules, names)

    upd: dict[str, Any] = {"oof_blocks": [b.model_copy(update={"text": c(b.text)}) for b in resp.oof_blocks]}
    if resp.phase in ("seed", "creation") and resp.fiction:
        upd["fiction"] = c(resp.fiction)
    if resp.budget_notice:
        upd["budget_notice"] = c(resp.budget_notice)
    if resp.pause is not None:
        p = resp.pause
        upd["pause"] = p.model_copy(update={"prompt": c(p.prompt), "choices": [
            ch.model_copy(update={"label": c(ch.label)}) for ch in p.choices]})
    return resp.model_copy(update=upd)


__all__ = ["clean", "clean_response", "display_name", "entity_names", "humanize", "name_ids", "second_person",
           "strip_citations"]
