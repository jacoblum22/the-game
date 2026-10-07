#!/usr/bin/env python3
"""basis_audit.py -- list rule cards with no basis tag (BRIEF §6, 00.1.6; ledger I-065).

    python rules/_process/basis_audit.py 04 05 06 07          # untagged cards per chapter (id, line, title)
    python rules/_process/basis_audit.py --count 00 01 ...    # counts only

A rule card is an rq.py index entry of kind "card" whose id is NN.S.R (tables T-, procedures PR- excluded),
and its text is its rq.py range. Its basis tag is a bracket group citing the constitution, research or the
decision log: `[C:VII]`, `[C:P5]`, `[R6 §2]`, `[R: <src>]`, `[DL-06-03]`, also inside a compound group such
as `[amended: DL-…]` or `[revision: I-009; DL-05-31]`. validate_ruleset.py's BASIS check imports this.
"""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
RULES = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(RULES, "tools"))
import rq  # noqa: E402

BASIS = re.compile(r"\[[^\]\[]*?(?:\bC:(?:[IV]+|P\d+)\b|\bR\d\b|\bR:|\bDL-[0-9A-Z]{2,3}-\d+)[^\]\[]*\]")  # may wrap a line
CARD = re.compile(r"^\d{2}\.\d+[a-z]?\.\d+[a-z]?$")


def untagged(chapters, idx=None):
    """-> ({chapter: [(id, line, title)]}, {chapter: total cards})"""
    idx = idx or rq.build_index()
    out = {c: [] for c in chapters}
    total = {c: 0 for c in chapters}
    cache = {}
    for k, (kind, rel, s, e, t) in idx.items():
        c = os.path.basename(rel)[:2]
        if kind != "card" or c not in out or not CARD.match(k) or not k.startswith(c + "."):
            continue
        if rel not in cache:
            cache[rel] = open(os.path.join(RULES, rel), encoding="utf-8").read().split("\n")
        body = "\n".join(cache[rel][s - 1:e])
        total[c] += 1
        if not BASIS.search(body):
            out[c].append((k, s, t))
    return out, total


if __name__ == "__main__":
    a = sys.argv[1:]
    cnt = "--count" in a
    chs = [x for x in a if x != "--count"]
    out, total = untagged(chs)
    for c in chs:
        print("ch.%s: %d of %d rule cards untagged" % (c, len(out[c]), total[c]))
        if not cnt:
            for k, s, t in out[c]:
                print("  %s\t:%d\t%s" % (k, s, t[:80]))
