#!/usr/bin/env python3
"""rq: rules query. Print one rule card, table, procedure, example, OEQ, decision or data entry by id,
instead of reading a whole chapter.

Usage (from anywhere):
  python rules/tools/rq.py 06.4.1            # one rule card
  python rules/tools/rq.py 06.4              # a whole section (heading to next same-level heading)
  python rules/tools/rq.py T-06-1 PR-06-1    # tables, procedures (several ids at once)
  python rules/tools/rq.py WE-06-1 OEQ-06-1 DL-05-12
  python rules/tools/rq.py ab.force_bolt     # a data entry (any `id:` in data/*.yaml)
  python rules/tools/rq.py --toc 06          # list every id defined in chapter 06 with its title and line
  python rules/tools/rq.py --toc 06.4        # ... only inside section 06.4
  python rules/tools/rq.py --refs 06.4.1     # where an id is cited (file:line), excluding its definition
  python rules/tools/rq.py --find "Guard"    # ids whose title matches a regex
  python rules/tools/rq.py --index           # (re)write _process/index.tsv: id, kind, file, start, end, title
Options: --max N  cap printed lines per id (default 200; 0 = no cap).

Definitions recognised in rules/*.md and appendix/*.md:
  headings  '#..# <ID> title'           (sections 06.4, WE-06-1, DL-05-12, ...)
  bold      '**<ID> Title.**'           (rule cards 06.4.1, tables T-06-1, procedures PR-06-1)
  table row '| OEQ-06-1 | ...'          (open empirical questions)
A card runs until the next definition, heading, or blank-line-then-definition. A section runs to the next
heading of the same or higher level.
"""
import os, re, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # rules/
ID = r"(?:\d{2}(?:\.\d+[a-z]?)+|(?:T|PR|WE|OEQ|DL|FN)-[0-9A-Z]{2,3}-[0-9A-Za-z]+[a-z]?)"
RE_HEAD = re.compile(r"^(#{2,6})\s+(" + ID + r")\b\s*:?\s*(.*)$")
RE_BOLD = re.compile(r"^\*\*(" + ID + r")\b\s*(.*?)\*\*")
RE_ROW = re.compile(r"^\|\s*(OEQ-[0-9A-Z]{2}-\d+[a-z]?)\s*\|\s*([^|]*)")
RE_ANYHEAD = re.compile(r"^(#{1,6})\s")
RE_YID = re.compile(r"^(\s*)-?\s*id:\s*['\"]?([A-Za-z0-9_.\-]+)")


def md_files():
    fs = sorted(glob.glob(os.path.join(ROOT, "[0-9][0-9]-*.md")))
    fs += [os.path.join(ROOT, "appendix", "decision-log.md")]
    return [f for f in fs if os.path.exists(f)]


def build_index():
    idx = {}  # id -> (kind, file, start, end, title)
    for f in md_files():
        lines = open(f, encoding="utf-8").read().split("\n")
        defs = []  # (line_no, id, kind, level, title)
        for i, l in enumerate(lines):
            m = RE_HEAD.match(l)
            if m:
                defs.append((i, m.group(2), "heading", len(m.group(1)), m.group(3).strip()))
                continue
            m = RE_BOLD.match(l)
            if m:
                defs.append((i, m.group(1), "card", 9, m.group(2).strip().rstrip(".")))
                continue
            m = RE_ROW.match(l)
            if m:
                defs.append((i, m.group(1), "row", 10, m.group(2).strip()[:90]))
        heads = [(i, len(RE_ANYHEAD.match(l).group(1))) for i, l in enumerate(lines) if RE_ANYHEAD.match(l)]
        for k, (i, did, kind, lvl, title) in enumerate(defs):
            if kind == "heading":
                end = next((j for j, hl in heads if j > i and hl <= lvl), len(lines))
            elif kind == "row":
                end = i + 1
            else:
                nxt_def = next((d[0] for d in defs[k + 1:] if d[0] > i), len(lines))
                nxt_head = next((j for j, _ in heads if j > i), len(lines))
                end = min(nxt_def, nxt_head)
            while end > i + 1 and not lines[end - 1].strip():
                end -= 1
            rel = os.path.relpath(f, ROOT)
            if did not in idx:  # first definition wins (later ones are usually repeats in examples)
                idx[did] = (kind, rel, i + 1, end, title)
    for f in sorted(glob.glob(os.path.join(ROOT, "data", "*.yaml"))):
        lines = open(f, encoding="utf-8").read().split("\n")
        rel = os.path.relpath(f, ROOT)
        for i, l in enumerate(lines):
            m = RE_YID.match(l)
            if not m or "." not in m.group(2):
                continue
            ind = len(m.group(1))
            end = i + 1
            while end < len(lines):
                s = lines[end]
                if s.strip() and (len(s) - len(s.lstrip())) <= ind and not s.lstrip().startswith("#"):
                    break
                end += 1
            while end > i + 1 and not lines[end - 1].strip():
                end -= 1
            if m.group(2) not in idx:
                idx[m.group(2)] = ("data", rel, i + 1, end, "")
    return idx


def show(idx, did, cap):
    if did not in idx:
        cands = [k for k in idx if k.startswith(did)][:15]
        print(f"## {did}: not found." + (f" Did you mean: {', '.join(cands)}" if cands else ""))
        return
    kind, rel, s, e, title = idx[did]
    lines = open(os.path.join(ROOT, rel), encoding="utf-8").read().split("\n")[s - 1:e]
    print(f"## {did}  [{rel}:{s}-{e}]")
    if cap and len(lines) > cap:
        print("\n".join(lines[:cap]))
        print(f"... [{len(lines) - cap} more lines; --max 0 for all, or --toc {did} to list sub-ids]")
    else:
        print("\n".join(lines))


def main(argv):
    cap = 200
    if "--max" in argv:
        k = argv.index("--max"); cap = int(argv[k + 1]); del argv[k:k + 2]
    if not argv:
        print(__doc__); return
    idx = build_index()
    if argv[0] == "--index":
        out = os.path.join(ROOT, "_process", "index.tsv")
        with open(out, "w", encoding="utf-8") as fh:
            fh.write("id\tkind\tfile\tstart\tend\ttitle\n")
            for k, (kind, rel, s, e, t) in idx.items():
                fh.write(f"{k}\t{kind}\t{rel}\t{s}\t{e}\t{t}\n")
        print(f"wrote {out}: {len(idx)} ids"); return
    if argv[0] == "--toc":
        p = argv[1]
        for k, (kind, rel, s, e, t) in idx.items():
            if kind == "data":
                continue
            if re.match(r"^\d{2}$", p):
                ok = os.path.basename(rel).startswith(p + "-")
            else:
                ok = k == p or k.startswith(p + ".")
            if ok:
                print(f"{k}\t{rel}:{s}-{e}\t{t[:90]}")
        return
    if argv[0] == "--find":
        rx = re.compile(argv[1], re.I)
        for k, (kind, rel, s, e, t) in idx.items():
            if kind != "data" and rx.search(t):
                print(f"{k}\t{rel}:{s}\t{t[:90]}")
        return
    if argv[0] == "--refs":
        did = argv[1]
        rx = re.compile(r"(?<![\w.\-])" + re.escape(did) + r"(?![\w\-]|\.\d)")
        d = idx.get(did)
        n = 0
        for f in md_files() + sorted(glob.glob(os.path.join(ROOT, "data", "*.yaml"))):
            rel = os.path.relpath(f, ROOT)
            for i, l in enumerate(open(f, encoding="utf-8")):
                if rx.search(l) and not (d and d[1] == rel and d[2] == i + 1):
                    n += 1
                    if n <= 60:
                        print(f"{rel}:{i + 1}: {l.strip()[:140]}")
        print(f"[{n} references]"); return
    for did in argv:
        show(idx, did, cap)


if __name__ == "__main__":
    main(sys.argv[1:])
