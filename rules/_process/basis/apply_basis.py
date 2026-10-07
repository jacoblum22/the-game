"""apply_basis.py -- insert a card-level basis tag (BRIEF §6, 00.1.6) into rule cards. [revision: I-065]

Used by the per-chapter scripts in this folder (C6a-04.py ...). For each `card id -> basis` it finds the card's
first line `**<id> Title.**`, and inserts ` [<basis>; revision: I-065]` after the card's kind tags
(`[D]`, `[J:flag]`, `[S]` + `[D]` ...), or after the bold title when there are none. Exact match, one
occurrence per card (asserted). Idempotent: a card already carrying the revision marker is skipped.
After applying, the chapter is re-audited with basis_audit.py and every listed card must be tagged.
"""
import glob, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
RULES = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(RULES, "_process"))
import basis_audit  # noqa: E402

MARK = "revision: I-065"
KINDS = re.compile(r"((?:\s*(?:\+\s*)?`\[[^\]`]+\]`)*)")


def apply(chapter, basis):
    path = glob.glob(os.path.join(RULES, chapter + "-*.md"))[0]
    s = open(path, encoding="utf-8").read()
    done = skipped = 0
    for cid, tag in basis.items():
        assert re.match(r"^(?:(?:C:(?:[IV]+|P\d+))|(?:R\d)|(?:R:)|(?:DL-))", tag), (cid, tag)
        head = re.compile(r"^\*\*" + re.escape(cid) + r"\b[^\n]*?\*\*", re.M)
        hits = list(head.finditer(s))
        assert len(hits) == 1, (cid, len(hits))
        m = hits[0]
        line_end = s.index("\n", m.end())
        if MARK in s[m.start():line_end]:
            skipped += 1
            continue
        k = KINDS.match(s, m.end())
        at = k.end()
        s = s[:at] + " [%s; %s]" % (tag, MARK) + s[at:]
        done += 1
    open(path, "w", encoding="utf-8").write(s)
    out, total = basis_audit.untagged([chapter])
    left = [c for c, _, _ in out[chapter]]
    bad = [c for c in basis if c in left]
    print("ch.%s: tagged %d, already tagged %d; untagged now %d of %d%s"
          % (chapter, done, skipped, len(left), total[chapter], (": " + ", ".join(left)) if left else ""))
    assert not bad, "still untagged after apply: %s" % bad
    return left
