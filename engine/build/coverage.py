"""Per-milestone rule coverage: which rule ids the engine implements, handles coarsely, defers, or leaves
to the model.

Usage:
  python engine/build/coverage.py --milestone 1                  # summary per chapter
  python engine/build/coverage.py --milestone 1 --list deferred  # also list the ids in one status
Options: --engine DIR (default engine/), --cards FILE (default engine/build/cards.json).

Counted ids: rule, procedure (PR-) and table (T-) cards. Tags are comments in engine/**/*.py of the form
`# rule: <id>[, <id>...]` (implemented) and `# coarse: <id>` (handled by the pipeline's anchor at a coarser
grain). Status, first match wins:
  implemented  a `# rule:` tag names the id
  coarse       a `# coarse:` tag names the id
  deferred     the id belongs to a later milestone (or to none: ch.14)
  model        every mark is [J*] or [N]: the model judges it, no code needed
  to-build     in scope for this milestone, has a code part ([D]/[T]/[S] or no mark), no tag yet
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from engine.build.compile_cards import OUT, REPO, RuleCard, compile_cards, load_cards  # noqa: E402

ENGINE = REPO / "engine"
COUNTED = ("rule", "procedure", "table")
STATUSES = ("implemented", "coarse", "deferred", "model", "to-build")

# Milestone -> chapter/section prefixes. Source: specs/004-playable-prototype/plan.md, "## Milestones" table,
# column "Chapters / procedures". The most specific prefix wins; a prefix listed in two milestones belongs to
# the earlier one (11.13: simple in M1, full in M7). "07 legacy" (M7) names no distinct section, so it stays
# with ch.07 (M2). Ch.14 (players' guide) is in no milestone.
MILESTONES: dict[int, list[str]] = {
    1: [
        "00",
        "01",
        "02",
        "12",
        "07.1",
        "07.2",
        "07.3",
        "07.4",
        "07.5",
        "07.8",
        "05.4",
        "05.6",
        "09.2",
        "10.1",
        "15.1",
        "15.2",
        "15.3",
        "15.4",
        "11.12",
        "11.13",
    ],
    2: ["06", "09", "07"],
    3: ["03", "04", "05", "15.11"],
    4: ["10", "12.4.9"],  # 12.4.9 venture bookkeeping ("12, all but venture bookkeeping" in M1)
    5: ["08"],
    6: ["11", "15.5", "15.6", "15.7", "15.8", "15.9"],
    7: ["16", "15.10", "15.12", "15.13"],
}

ID = r"(?:\d{2}(?:\.\d+[a-z]?)+|(?:T|PR|WE|OEQ|DL)-[0-9A-Z]{2,3}-[0-9A-Za-z]+)"  # rq.py's id form
RE_TAG = re.compile(r"#\s*(rule|coarse):\s*(.*)$")
RE_ID = re.compile(r"(?<![\w.\-])" + ID + r"(?![\w\-])")


def _prefix_milestone(key: str) -> int | None:
    best: tuple[int, int] | None = None  # (prefix length, milestone)
    for m, prefixes in sorted(MILESTONES.items()):
        for p in prefixes:
            if (key == p or key.startswith(p + ".")) and (best is None or len(p) > best[0]):
                best = (len(p), m)
    return best[1] if best else None


def milestones(cards: list[RuleCard]) -> dict[str, int | None]:
    """id -> milestone, by the most specific prefix covering the card's id (rules) or enclosing section.
    A table or procedure outside any numbered section takes the earliest milestone of the same-chapter
    rules that cite it, else the earliest milestone that lists any part of its chapter."""
    out = {c.id: _prefix_milestone(c.id if c.kind == "rule" else (c.section or c.chapter)) for c in cards}
    for c in cards:
        if out[c.id] is not None or c.kind not in COUNTED:
            continue
        rx = re.compile(r"(?<![\w\-])" + re.escape(c.id) + r"(?![\w\-])")
        citing = [
            out[r.id] for r in cards if r.kind == "rule" and r.chapter == c.chapter and rx.search(r.body)
        ]
        found = [m for m in citing if m is not None]
        listed = [m for m, ps in MILESTONES.items() if any(p[:2] == c.chapter for p in ps)]
        out[c.id] = min(found) if found else min(listed, default=None)
    return out


def scan_tags(engine: Path = ENGINE) -> dict[str, set[str]]:
    """Ids named by `# rule:` and `# coarse:` comments in engine/**/*.py."""
    tags: dict[str, set[str]] = {"rule": set(), "coarse": set()}
    for path in sorted(engine.rglob("*.py")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if m := RE_TAG.search(line):
                tags[m.group(1)].update(RE_ID.findall(m.group(2)))
    return tags


def classify(cards: list[RuleCard], tags: dict[str, set[str]], milestone: int) -> dict[str, str]:
    """id -> status for every counted card."""
    out: dict[str, str] = {}
    when = milestones(cards)
    for c in cards:
        if c.kind not in COUNTED:
            continue
        m = when[c.id]
        if c.id in tags["rule"]:
            out[c.id] = "implemented"
        elif c.id in tags["coarse"]:
            out[c.id] = "coarse"
        elif m is None or m > milestone:
            out[c.id] = "deferred"
        elif c.model_judged:
            out[c.id] = "model"
        else:
            out[c.id] = "to-build"
    return out


def report(cards: list[RuleCard], tags: dict[str, set[str]], milestone: int, list_status: str | None) -> str:
    status = classify(cards, tags, milestone)
    chapter = {c.id: c.chapter for c in cards}
    rows: dict[str, Counter[str]] = {}
    for cid, s in status.items():
        rows.setdefault(chapter[cid], Counter())[s] += 1
    known = {c.id for c in cards}
    unknown = sorted((tags["rule"] | tags["coarse"]) - known)
    lines = [f"Coverage, milestone {milestone} (rules, procedures, tables; tags from engine/**/*.py)"]
    lines.append("ch    total " + " ".join(f"{s:>11}" for s in STATUSES))
    total: Counter[str] = Counter()
    for ch in sorted(rows):
        total.update(rows[ch])
        n = sum(rows[ch].values())
        lines.append(f"{ch:<5} {n:>5} " + " ".join(f"{rows[ch][s]:>11}" for s in STATUSES))
    lines.append(f"{'all':<5} {sum(total.values()):>5} " + " ".join(f"{total[s]:>11}" for s in STATUSES))
    if unknown:
        lines.append(f"tagged ids that are not cards ({len(unknown)}): {', '.join(unknown[:12])}")
    if list_status:
        picked = [cid for cid, s in status.items() if s == list_status]
        by_ch: dict[str, list[str]] = {}
        for cid in picked:
            by_ch.setdefault(chapter[cid], []).append(cid)
        lines.append(f"{list_status} ({len(picked)}):")
        lines += [f"  {ch}: {' '.join(ids)}" for ch, ids in sorted(by_ch.items())]
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    def opt(name: str) -> str | None:
        return argv[argv.index(name) + 1] if name in argv else None

    milestone = int(opt("--milestone") or 1)
    list_status = opt("--list")
    if list_status and list_status not in STATUSES:
        print(f"--list takes one of: {', '.join(STATUSES)}")
        return 2
    engine = Path(opt("--engine") or ENGINE)
    cards_path = Path(opt("--cards") or OUT)
    if cards_path.exists():
        cards = list(load_cards(cards_path))
    else:
        cards = [RuleCard.model_validate(c) for c in compile_cards()["cards"]]
    print(report(cards, scan_tags(engine), milestone, list_status))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
