"""Candidates for the whole-story reader (READ_STORY.md): for each notebook entry the DM's replies name in more than one
round, the sentences about it that state something checkable (a number, a distance, a time, a count, who knows or did
what), with their round numbers. Code only gathers them; it doesn't judge whether two of them disagree.
    py -3.12 evals/autoloop/facts.py <name> <last round> <out.txt>"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

from dm import lore as notebook
from dm import srd
from metrics import GAMES, rounds

NUMBER = (r"\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|twenty|thirty|forty|fifty|hundred|"
          r"thousand|dozen|score|half|first|second|third|last")
CHECKABLE = re.compile(rf"\b(?:{NUMBER})\b|\b(?:miles?|leagues?|hours?|days?|nights?|weeks?|months?|years?|ago|since|"
                       r"before|after|north|south|east|west|knows?|knew|told|saw|killed|died|dead|alive|brother|sister|"
                       r"father|mother|son|daughter|wife|husband)\b", re.IGNORECASE)
SENTENCE = re.compile(r"[^.!?\n]+[.!?]?")

name, last, out = sys.argv[1], int(sys.argv[2]), Path(sys.argv[3])
meta = json.loads((GAMES / f"{name}.meta.json").read_text(encoding="utf-8"))
save = json.loads((GAMES / Path(meta["save"]).name).read_text(encoding="utf-8"))
lore = save["lore"]
party = {save["sheet"]["name"], *(c.get("name") for c in save.get("companions") or [])}
rs = rounds(save["transcript"], meta["play_starts"])[:last]
# The DM leaves many names out of the notebook, so capitalised names inside a sentence count too (not its first word).
CAPS = re.compile(r"(?<=[a-z,;:] )[A-Z][\w-]*[a-z][\w-]*(?: (?:of |the |of the )?[A-Z][\w-]+)*(?<!'s)")
# Rules names (spells, features, abilities, conditions) aren't story names.
RULES = {y.strip().casefold() for f in (srd.DIR).glob("5e-SRD-*.json") for x in json.loads(f.read_text(encoding="utf-8"))
         if isinstance(x, dict) and isinstance(x.get("name"), str) for y in [x["name"], *re.split(r"[:()]", x["name"])]}
seen: dict[str, set[int]] = defaultdict(set)
for n, r in enumerate(rs, 1):
    for e in r:
        if e["kind"] == "dm":
            for x in CAPS.findall(e["text"]):
                seen[x].add(n)
for x in [x for x, ns in seen.items() if len(ns) >= 2 and not notebook.find(lore, x) and x not in party
          and x.casefold() not in RULES and x.split()[0] not in {"I", "You", "The", "DM", "AC", "HP", "XP"}]:
    lore["entries"][x] = {"other_names": []}
pats = notebook._patterns(lore)
claims: dict[str, list[tuple[int, str]]] = defaultdict(list)
for n, r in enumerate(rs, 1):
    for e in r:
        if e["kind"] != "dm":
            continue
        for s in SENTENCE.findall(e["text"]):
            if not CHECKABLE.search(s):
                continue
            for who in {w for _, _, w in notebook._spans(s, pats)}:
                if who not in party:
                    claims[who].append((n, s.strip()))
lines = []
for who, cs in sorted(claims.items(), key=lambda x: -len({n for n, _ in x[1]})):
    if len({n for n, _ in cs}) < 2:
        continue
    lines.append(f"\n## {who} ({len(cs)} sentences in {len({n for n, _ in cs})} rounds)")
    lines += [f"R{n}: {s[:300]}" for n, s in cs]
out.write_text("\n".join(lines).lstrip(), encoding="utf-8")
print(f"{out}: {sum(x.startswith(chr(10) + '##') for x in lines)} entries, {len(lines)} lines")
