"""Resolve git conflict blocks in issue-ledger.md row by row (parallel revision agents edit different rows).
Per row id: prefer a closed status (resolved/wontfix/accepted); else the longer (more informed) row.
Rows present on one side only are kept. Usage: python rules/_process/merge_ledger.py"""
import os, re
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "issue-ledger.md")
L = open(p, encoding="utf-8").read().split("\n")
def rid(r): return r.split("|")[1].strip() if r.startswith("|") else None
def closed(r): return bool(re.search(r"\|\s*(resolved|wontfix|accepted)", r))
out, i = [], 0
while i < len(L):
    if not L[i].startswith("<<<<<<<"):
        out.append(L[i]); i += 1; continue
    j = next(x for x in range(i, len(L)) if L[x] == "=======")
    k = next(x for x in range(j, len(L)) if L[x].startswith(">>>>>>>"))
    a, b = L[i + 1:j], L[j + 1:k]
    order, rows = [], {}
    for r in a + b:
        key = rid(r) or r
        if key not in rows: order.append(key); rows[key] = r; continue
        cur = rows[key]
        if closed(r) and not closed(cur): rows[key] = r
        elif closed(r) == closed(cur) and len(r) > len(cur): rows[key] = r
    out += [rows[x] for x in order]; i = k + 1
open(p, "w", encoding="utf-8").write("\n".join(out))
print("conflict blocks resolved; remaining markers:", sum(l.startswith("<<<<<<<") for l in out))
