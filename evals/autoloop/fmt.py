"""Format counts for replay results, per arm: how many replies end in a menu of choices, read out sheet numbers, or
use bold, bullets or rules talk. Regexes, so approximate; the same for every arm.
    py -3.12 evals/autoloop/fmt.py <folder of <arm>-<game>.json>"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

MENU = re.compile(r"\b(?:could|can|might)\b[^.?!]*\bor\b[^.?!]*[.?]", re.IGNORECASE)
CHOICE_Q = re.compile(r"[^.?!]*\bor\b[^.?!]*\?\s*$", re.IGNORECASE)
STATUS = re.compile(r"\b\d+ of \d+\b|\b\d+/\d+\b|\bHP\b|\bhit points\b|\bspell slots?\b|\b\d+ XP\b|\bhit dice\b|"
                    r"\bChannel Divinity\b|\bdeath sav", re.IGNORECASE)
RULES = re.compile(r"\bthe rules?\b|\bDC \d+|\bsaving throw\b|\bcheck\b.*\bDC\b", re.IGNORECASE)


def reply(r: dict) -> str:
    return "\n\n".join(e["text"] for e in r.get("entries", []) if e["kind"] == "dm" and e["text"])


def counts(texts: list[str]) -> dict:
    c = defaultdict(int)
    for t in texts:
        last = t.strip().split("\n\n")[-1]
        c["n"] += 1
        c["menu at end"] += bool(CHOICE_Q.search(last) or MENU.search(last))
        c["sheet numbers at end"] += bool(STATUS.search(last))
        c["sheet numbers anywhere"] += bool(STATUS.search(t))
        c["bold"] += "**" in t
        c["bullets"] += bool(re.search(r"^\s*(?:[-*•]|\d+[.)])\s+", t, re.MULTILINE))
        c["rules talk"] += bool(RULES.search(t))
        c["chars"] += len(t)
    c["chars"] //= max(c["n"], 1)
    return dict(c)


if __name__ == "__main__":
    arms: dict[str, list[str]] = defaultdict(list)
    for f in sorted(Path(sys.argv[1]).glob("*.json")):
        arm = f.stem.split("-")[0]
        arms[arm] += [reply(r) for r in json.loads(f.read_text(encoding="utf-8")) if "error" not in r]
    for arm, texts in arms.items():
        print(arm, counts(texts))
