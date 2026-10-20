"""Names in the DM's replies that are in no notebook entry (Jake, 2026-10-20).

The DM named people and places it never wrote down: in the three 180-round games of the second autoloop set, about
130 names were never put in the notebook (Sergeant Dreg was in 43 replies), and a name the DM learned for an entry it
had made without one (the old caretaker, Odo Fenwick) went only into the description, so no lookup found it by name.

A name here is a run of capitalised words that doesn't start a sentence, a line or a quotation, with SRD names
(spells, features, monsters...), titles (Lord, Mother...), single letters and words in capitals left out. It is
known when it's an entry's whole name or other name (a leading "the" aside), part of a person's name (Wil of Wil
Harrow, but not a word of a label like "The Greyshaft Foreman"), or X of Y with both known (Jake, 2026-10-20: "the
Greyshaft foreman sounds like a person"; with every word counted, Greyshaft and Ford Chapel were never flagged, and
in the dry run whole names flagged about a third more, the party's own names aside). The code only flags: each
turn the DM is told which names from its replies so far are still unknown, until it puts each in an entry or dismisses
it (dismiss_name) as not a name. Nothing is stored: the list is worked out again from the transcript, so going back
to an earlier line needs nothing more. In the dry run about 1 flag in 10 was not a name (Dodge, House, Keep)."""

from __future__ import annotations

import functools
import re
from typing import Any

from dm import srd

SHOWN = 20  # names listed in one message
CONNECT = {"of", "the", "de", "von", "van", "and"}
TITLES = set("lord lady sir mother father brother sister captain prior prioress master mistress old saint king queen "
             "prince princess elder sergeant high priest priestess dame uncle aunt goodwife goodman madam young "
             "little".split())
GAME_WORDS = {"i", "day", "dc", "hp", "ac", "xp", "ok", "am", "pm", "dm", "srd", "cr"}


@functools.cache
def _srd() -> tuple[frozenset[str], re.Pattern[str]]:
    """Every SRD name, lowercased (a feature also without its stage, and an option's own name), and a pattern for them."""
    out = {"hit die", "hit dice"}
    for t in ("Spells", "Monsters", "Features", "Traits", "Skills", "Conditions", "Ability-Scores", "Classes", "Races",
              "Subraces", "Languages", "Equipment", "Magic-Items", "Damage-Types", "Alignments", "Backgrounds",
              "Subclasses", "Magic-Schools", "Weapon-Properties"):
        for v in srd.table(t).values():
            name = v.get("name", "")
            base = re.sub(r"\s*\([^)]*\)$", "", name)
            out |= {name.lower(), base.lower(), base.split(": ")[-1].lower(), base.lower() + "s"}
            if v.get("full_name"):
                out.add(v["full_name"].lower())
            if t == "Backgrounds":
                out.add(((v.get("feature") or {}).get("name") or "").lower())
    out.discard("")
    return frozenset(out), re.compile(r"\b(" + "|".join(re.escape(n) for n in sorted(out, key=len, reverse=True)) + r")\b", re.I)


def _word(w: str) -> str:
    return re.sub(r"['’]s?$", "", w.lower())


def phrases(text: str) -> list[str]:
    """The runs of capitalised words in a reply that don't start a sentence, a line or a quotation."""
    srd_names, srd_re = _srd()
    runs: list[list[str]] = []
    for para in text.split("\n"):
        para = re.sub(r"\bI['’](ve|ll|d|m)\b", "I", para)
        para = srd_re.sub(lambda m: m.group() if m.group().islower() else "srd", para)  # game words, not names
        start, run = True, []
        for t in re.finditer(r"[A-Za-z][A-Za-z'’\-]*|[.!?:;,\"“”‘—()]", para):
            w = t.group()
            if not w[0].isalpha():
                if run:
                    runs.append(run)
                run = []
                start = start or w in '.!?:"“”—('
                continue
            if w[0].isupper():
                if start:
                    run = []
                else:
                    run.append(w)
            elif run and w.lower() in CONNECT:
                run.append(w)
            else:
                if run:
                    runs.append(run)
                run = []
            start = False
        if run:
            runs.append(run)
    out = []
    for r in runs:  # "Wat and Ned" is two names
        piece: list[str] = []
        for w in [*r, "and"]:
            if w.lower() != "and":
                piece.append(w)
                continue
            while piece and piece[-1].lower() in CONNECT:
                piece.pop()
            while piece and piece[0].lower() in CONNECT:
                piece.pop(0)
            name = re.sub(r"['’]s?$", "", " ".join(piece))
            if name and len(name) > 1 and not name.isupper() and name not in out:
                out.append(name)
            piece = []
    return out


def _whole(x: str) -> str:
    return re.sub(r"['’]s?$", "", re.sub(r"^the\s+", "", " ".join(x.split()), flags=re.I)).casefold()


def known(lore: dict[str, Any], party: tuple[str, ...] = ()) -> tuple[set[str], set[str]]:
    """Whole names (every entry's names and the party's), and the parts of people's names."""
    whole = {_whole(x) for n, e in lore["entries"].items() for x in [n, *e["other_names"]]} | {_whole(p) for p in party}
    parts: set[str] = set()
    people = [x for n, e in lore["entries"].items() if e["kind"].strip().casefold() == "person"
              for x in [n, *e["other_names"]] if not x.lower().startswith("the ")]  # "The Foreman" is a label
    for x in [*people, *party]:
        w = [t for t in x.split() if t.lower() not in TITLES]
        parts |= {_whole(" ".join(w[i:j])) for i in range(len(w)) for j in range(i + 1, len(w) + 1)}
    return whole, parts


def dismissed(transcript: list[dict[str, Any]]) -> set[str]:
    return {" ".join(n.split()).casefold() for e in transcript
            if e["kind"] == "call" and e.get("tool") == "dismiss_name" and not e.get("error")
            for n in e["input"].get("names") or []}


def unknown(lore: dict[str, Any], transcript: list[dict[str, Any]], party: tuple[str, ...] = ()) -> list[str]:
    """The names in the DM's replies so far that are in no entry and weren't dismissed, oldest first."""
    (whole, parts), gone, srd_names = known(lore, party), dismissed(transcript), _srd()[0]
    ok = lambda y: _whole(y) in whole or _whole(y) in parts  # noqa: E731
    made = [i for i, e in enumerate(transcript) if e["kind"] == "call" and e.get("tool") == "finish_character"]
    out: list[str] = []
    for e in transcript[made[-1] + 1 if made else 0:]:  # play only: character creation's talk is not the world
        if e["kind"] != "dm":
            continue
        for p in phrases(e["text"]):
            core = " ".join(w for w in p.split() if _word(w) not in TITLES and _word(w) not in GAME_WORDS)
            if p in out or p.casefold() in gone or p.lower() in srd_names or not core:
                continue
            if ok(p) or ok(core) or (" of " in core and all(ok(y) for y in core.split(" of "))):
                continue
            out.append(p)
    return out


def warning(lore: dict[str, Any], transcript: list[dict[str, Any]], party: tuple[str, ...] = ()) -> str:
    names = unknown(lore, transcript, party)
    if not names:
        return ""
    more = f" (and {len(names) - SHOWN} more)" if len(names) > SHOWN else ""
    return ("[Names not in your notebook] Your replies have used these, which are no entry's name or other name: "
            + ", ".join(names[:SHOWN]) + more + ". Put each in the notebook: its own entry, or an existing entry's name "
            "(`rename`) or other name (`add_other_names`). If one isn't a name, dismiss it with `dismiss_name`.")
