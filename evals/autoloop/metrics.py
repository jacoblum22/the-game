"""Counts for a block of rounds in the autoloop games: what can be measured from the save without reading the story.
    py -3.12 evals/autoloop/metrics.py <first round> <last round> [names...]
Story problems (contradictions, rules errors) are read by hand and logged in LOG.md; these are the mechanical ones."""
import json
import re
import statistics
import sys
from collections import Counter
from pathlib import Path

GAMES = Path(__file__).parent / "games"

META = re.compile(r"\b(out of character|tool call|my notes|notebook|the clock (?:now|is now|stands)|I(?:'ve| have)? "
                  r"(?:recorded|noted|updated|logged|added)|on your sheet|the status)\b", re.IGNORECASE)
BULLET = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s+", re.MULTILINE)


def rounds(t: list[dict], play_starts: int) -> list[list[dict]]:
    """The transcript from play's start, split into rounds: a player line and all that followed it."""
    out: list[list[dict]] = []
    for e in t[play_starts:]:
        if e["kind"] == "player":
            out.append([e])
        elif out:
            out[-1].append(e)
    return out


def block(name: str, first: int, last: int) -> dict:
    meta = json.loads((GAMES / f"{name}.meta.json").read_text(encoding="utf-8"))
    save = json.loads(Path(meta["save"]).read_text(encoding="utf-8"))
    rs = rounds(save["transcript"], meta["play_starts"])[first - 1:last]
    c: Counter = Counter()
    lens, tools = [], Counter()
    for r in rs:
        dm = "\n\n".join(e["text"] for e in r if e["kind"] == "dm")
        lens.append(len(dm))
        kinds = Counter(e["kind"] for e in r)
        c["stub (lost reply, re-asked)"] += kinds["stub"]
        c["hidden (text after a late call)"] += kinds["hidden"] > 0
        c["refused tool calls"] += kinds["refused"]
        c["rounds with no reply"] += not dm
        c["rounds with bullets"] += bool(BULLET.search(dm))
        c["rounds with bold"] += "**" in dm
        c["rounds with headings"] += bool(re.search(r"^#+ ", dm, re.MULTILINE))
        c["rounds with meta talk"] += bool(META.search(dm))
        c["DM: questions"] += r[0]["text"].lstrip().startswith("DM:")
        for e in r:
            if e["kind"] == "tool":
                tools[e["text"].split(":")[0].split(" ")[0]] += 1
            elif e["kind"] == "call":
                tools[e["tool"]] += 1
    times = [t["seconds"] for t in meta["times"] if True][first - 1:last]
    return {"name": name, "rounds": len(rs), "reply chars median": int(statistics.median(lens)) if lens else 0,
            "reply chars max": max(lens, default=0), "turn seconds median": statistics.median(times) if times else None,
            "turn seconds max": max(times, default=None), **c, "tool use": dict(tools.most_common())}


if __name__ == "__main__":
    first, last = int(sys.argv[1]), int(sys.argv[2])
    for n in sys.argv[3:] or ["cleric", "barbarian", "bard"]:
        print(json.dumps(block(n, first, last), indent=1))
