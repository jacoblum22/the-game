"""Resolve an in-progress rules-wave merge: union appended DL fragments, row-wise ledger merge, flag the rest.
Run from the repo root during `git merge --no-commit`. Generated files (decision-log, traceability, anchors,
cards.json) are taken from either side and must be regenerated afterwards."""
import re
import subprocess
import sys
from pathlib import Path

MARK = re.compile(r"^<<<<<<< [^\n]*\n(.*?)^=======\n(.*?)^>>>>>>> [^\n]*\n", re.S | re.M)
GENERATED = {"rules/appendix/decision-log.md", "rules/appendix/traceability.md", "rules/data/anchors.yaml",
             "engine/build/cards.json", "tests/replay/games/offline_seed11.json"}


def git(*a: str) -> str:
    return subprocess.run(["git", *a], capture_output=True, text=True, encoding="utf-8").stdout


def ledger(path: str, s: str) -> str:
    base = {l.split("|")[1].strip(): l for l in git("show", f":1:{path}").splitlines() if l.startswith("| ")}

    def fix(m: re.Match) -> str:
        ours, theirs = m.group(1).splitlines(), m.group(2).splitlines()
        key = lambda l: l.split("|")[1].strip() if l.startswith("| ") else l  # noqa: E731
        t = {key(l): l for l in theirs}
        out = []
        for l in ours:
            k, b = key(l), base.get(key(l))
            tl = t.pop(k, l)
            if l == b:
                out.append(tl)
            elif tl == b or l == tl:
                out.append(l)
            else:
                sys.exit(f"BOTH CHANGED ledger row {k}: resolve by hand")
        out.extend(t.values())  # rows only theirs added
        return "\n".join(out) + "\n"
    return MARK.sub(fix, s)


conflicted = [p for p in git("diff", "--name-only", "--diff-filter=U").splitlines() if p]
for p in conflicted:
    if p in GENERATED:
        git("checkout", "--theirs", p)
        print("generated, take theirs:", p)
        continue
    s = Path(p).read_text(encoding="utf-8")
    if p.endswith("issue-ledger.md") or p.endswith("open-empirical-questions.md"):
        s2 = ledger(p, s)
    elif "/fragments/DL-" in p:
        s2 = MARK.sub(lambda m: m.group(1) + m.group(2), s)  # both sides appended entries
    else:
        print("MANUAL:", p)
        continue
    assert "<<<<<<<" not in s2
    Path(p).write_text(s2, encoding="utf-8")
    print("resolved:", p)
