"""integration-assemble-appendix.py -- assembles rules/appendix/decision-log.md and rules/appendix/traceability.md
from the per-chapter fragments in rules/appendix/fragments/ (which stay in place). Re-runnable: each target keeps
its hand-written head (DL-00, DL-00A; the matrix preamble) up to a marker and regenerates everything after it.

decision-log.md : DL-00 and DL-00A (kept) + every DL-NN.md in chapter order + DL-INT.md (integration decisions).
traceability.md : ONE matrix, one row per constitution clause (I-VII, P1-P17): requirement, every satisfying rule id
                  by chapter (00 from the original matrix, 01-16 from trace-NN.md), status (met / met-with-deviation
                  (DL cited) / partial / gap) and related open issues; then a second table of the other obligations
                  the fragments traced (BRIEF addenda, 00.17 rows, R5 checklist rows).
"""
import glob, os, re
from collections import OrderedDict, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.normpath(os.path.join(HERE, "..", "..", "appendix"))
FR = os.path.join(APP, "fragments")
RULES = os.path.normpath(os.path.join(APP, ".."))
ORDER = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "15", "16"]
MARK = "<!-- ===== assembled at integration from appendix/fragments/ (do not edit below; edit the fragments) ===== -->"

def read(p):
    return open(p, encoding="utf-8").read().replace("\r\n", "\n")

titles = {}
for c in ORDER:
    f = glob.glob(os.path.join(RULES, c + "-*.md"))[0]
    titles[c] = read(f).split("\n", 1)[0].lstrip("# ").split("—", 1)[1].strip()

# ------------------------------------------------------------------ decision log
dl = read(os.path.join(APP, "decision-log.md"))
head = dl.split(MARK)[0].rstrip("\n")
parts = [head, "", MARK, ""]
counts = OrderedDict()
for c in ORDER:
    body = read(os.path.join(FR, "DL-%s.md" % c)).strip("\n").split("\n")
    assert body[0].startswith("#"), c
    rest = "\n".join(body[1:]).strip("\n")
    counts[c] = len(re.findall(r"^### DL-%s-\d+" % c, rest, re.M))
    parts += ["## DL-%s — %s" % (c, titles[c]), "", rest, ""]
intf = read(os.path.join(FR, "DL-INT.md")).strip("\n")
counts["INT"] = len(re.findall(r"^### DL-INT-\d+", intf, re.M))
parts += [intf, ""]
open(os.path.join(APP, "decision-log.md"), "w", encoding="utf-8", newline="\n").write("\n".join(parts))
print("decision-log entries by section:", dict(counts), "total", sum(counts.values()))

# ------------------------------------------------------------------ traceability
CLAUSES = ["I", "II", "III", "IV", "V", "VI", "VII"] + ["P%d" % i for i in range(1, 18)]
ID_RE = re.compile(r"\b(?:\d\d\.\d+(?:\.\d+)?(?:\s?[a-z]\b)?|PR-\d\d-\d+|T-\d\d-\d+|DL-\d\d[A]?-\d+|INV-\d+|SG-\d+|WE-\d\d-\d+|OEQ-\d\d-\d+)")
ROW_RE = re.compile(r"^\|(.+)\|\s*$")

def rows(path):
    out = []
    for line in read(path).split("\n"):
        m = ROW_RE.match(line)
        if not m or line.startswith("|---"):
            continue
        cells = [x.strip() for x in m.group(1).split("|")]
        if cells[0].lower() == "clause" or len(cells) < 4:
            continue
        out.append(cells)
    return out

def clause_key(label):
    m = re.match(r"^(?:C:)?(VII|VI|V|IV|III|II|I|P1[0-7]|P[1-9])\b", label)
    return m.group(1) if m else None

tr = read(os.path.join(APP, "traceability.md"))
tr_head = tr.split(MARK)[0]
base_rows = rows(os.path.join(APP, "traceability.md")) if MARK not in tr else []
if MARK in tr:   # re-run: 00's rows are kept in fragments/trace-00.md, written on the first run
    base_rows = rows(os.path.join(FR, "trace-00.md"))
else:
    with open(os.path.join(FR, "trace-00.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("# Traceability — 00 Architecture (the original matrix's rows, kept as 00's fragment at integration)\n\n")
        f.write("| Clause | Requirement (short) | Satisfied by (rule ids) | Status |\n|---|---|---|---|\n")
        for c in base_rows:
            f.write("| " + " | ".join(c[:4]) + " |\n")
    tr_head = tr.split("| Clause |")[0]

req = {}
by = defaultdict(lambda: OrderedDict())
stat = defaultdict(list)
other = []
srcs = [("00", base_rows)] + [(c, rows(os.path.join(FR, "trace-%s.md" % c))) for c in ORDER]
for ch, rs in srcs:
    for cells in rs:
        label, requirement, sat, status = cells[0], cells[1], cells[2], cells[-1]
        k = clause_key(label)
        if not k:
            other.append((ch, label, requirement, sat, status))
            continue
        req.setdefault(k, requirement)
        if status.lower().startswith(("n/a", "not applicable", "not touched")) or sat.lower().startswith(("not touched", "not used")):
            stat[k].append((ch, status, sat))
            continue
        ids = list(OrderedDict.fromkeys(m.group(0).replace(" ", "") for m in ID_RE.finditer(sat)))
        prev = by[k].get(ch, [])
        by[k][ch] = list(OrderedDict.fromkeys(prev + ids)) or prev or ["(" + sat[:60].rstrip() + ")"]
        stat[k].append((ch, status, sat))

REQ_FALLBACK = {"P14": "Asymmetric cadence (MAY), never as extra actions", "P15": "Time-gated specialization as an alternative to point audit"}
ISSUES = {  # open issues (issue-ledger.md) bearing on a clause; listed, they do not change the fragments' status
    # [verification: V1-007] rebuilt from the OPEN rows of issue-ledger.md (the old list named rows now resolved)
    "P1": ["I-060"], "P2": ["I-037", "I-039", "I-045"], "P4": ["I-047"], "P5": ["I-037", "I-041", "I-047"],
    "P9": ["I-033"], "P12": ["I-038"], "V": ["I-033", "I-037"], "VI": ["I-043", "I-049"],
}
def status_of(k):
    ss = [(ch, s.lower()) for ch, s, _ in stat[k]]
    dls = sorted(set(re.findall(r"DL-\d\d-\d+", " ".join(s + " " + t for _, s, t in stat[k] if "deviat" in s.lower()))))
    applicable = [(ch, s) for ch, s in ss if not s.startswith(("n/a", "not applicable", "not touched"))]
    if not applicable or any("gap" in s for _, s in applicable):
        return "gap"
    full = [ch for ch, s in applicable if s.startswith(("satisfied", "met", "supports", "supported", "adopted"))]
    partial = sorted(set(ch for ch, s in applicable if "partial" in s))
    if not full:
        return "partial"
    note = " (chapter-local partial: %s)" % ", ".join(partial) if partial else ""
    if any("deviation" in s for _, s in applicable):
        return "met-with-deviation (%s)%s" % (", ".join(dls) if dls else "recorded", note)
    return "met" + note

lines = [tr_head.rstrip("\n").replace("Populated by chapter authors, completed and audited in\nthe verification wave.",
         "Populated by chapter authors, assembled at integration, audited in the verification wave."), "", MARK, "",
         "**Status key.** *met*: every chapter that touches the clause reports it satisfied; *met-with-deviation*: a chapter",
         "satisfies it in a recorded different form (the DL entries cited); *partial*: a chapter reports it partly met;",
         "*gap*: no chapter satisfies it. *Open issues* lists ledger rows that bear on the clause (they do not by",
         "themselves change the status). Rule ids are grouped by chapter; the full text of each chapter's row is in",
         "`appendix/fragments/trace-NN.md`.", "",
         "| Clause | Requirement (short) | Satisfied by (rule ids, by chapter) | Chapters | Status | Open issues |",
         "|---|---|---|---|---|---|"]
for k in CLAUSES:
    cells = "; ".join("**%s**: %s" % (ch, ", ".join(ids)) for ch, ids in by[k].items()) if by[k] else "—"
    chs = ", ".join(by[k].keys())
    lines.append("| %s | %s | %s | %s | %s | %s |" % (k, req.get(k, REQ_FALLBACK.get(k, "")), cells, chs or "—", status_of(k),
                                                     ", ".join(ISSUES.get(k, [])) or "—"))
lines += ["", "### Other traced obligations (BRIEF addenda, 00.17 contract rows, R5 checklist rows)", "",
          "| Chapter | Obligation | Requirement (short) | Satisfied by | Status |", "|---|---|---|---|---|"]
for ch, label, requirement, sat, status in other:
    lines.append("| %s | %s | %s | %s | %s |" % (ch, label, requirement, sat, status))
open(os.path.join(APP, "traceability.md"), "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
print("traceability: %d clauses; %d other obligations" % (len(CLAUSES), len(other)))
for k in CLAUSES:
    print("  %-4s %-40s chapters=%d" % (k, status_of(k), len(by[k])))
