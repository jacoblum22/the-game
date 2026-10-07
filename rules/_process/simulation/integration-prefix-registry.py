"""integration-prefix-registry.py -- regenerates 00.16.2a (the id-prefix registry table in 00-architecture.md) from the
ids actually defined in rules/data/*.yaml, so that every prefix in use is registered with the file that defines it.
Run after any data change that introduces a new prefix; validate_ruleset.py reads the table back."""
import glob, os, re, sys
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.argv = [sys.argv[0]]
ns = {"__file__": os.path.join(R, "_process", "validate_ruleset.py"), "__name__": "registry"}
exec(compile(open(os.path.join(R, "_process", "validate_ruleset.py"), encoding="utf-8").read().split("# ====================================================================== 3.")[0], "validate", "exec"), ns)
PF = ns["PREFIX_FILES"]
OWNER = {}
for line in open(os.path.join(R, "00-architecture.md"), encoding="utf-8"):
    m = re.match(r"^\| ([a-z_*.,/ ]+\.yaml[^|]*)\| ([^|]+)\|", line)
    if m:
        for f in re.findall(r"[a-z_*]+\.yaml", m.group(1)):
            OWNER[f] = m.group(2).strip()
def owner(f):
    # f may carry a locator or note ("callings.yaml#requirements", "abilities.yaml (inline clock spec)"): look up its file
    if f.startswith("00-architecture.md"): return "00"
    m = re.match(r"[a-z_]+\.yaml", f)
    if m: f = m.group(0)
    if f in OWNER: return OWNER[f]
    for k, v in OWNER.items():
        if "*" in k and re.match(k.replace("*", ".*"), f): return v
    return "?"
NOTE = {
    "item": "item entities (00.6.2: `item.i0042`; the region's storied items) share their first segment with the tag facet `item`; ids and tags never coincide",
    "h": "boundary handlers (T-00-9)", "tbl": "tables, wherever they live (keyed or with an id)",
    "clk": "clock templates and instances (00.8); families declared by `id_pattern`",
}
rows = []
for p in sorted(PF):
    files = sorted(PF[p])
    rows.append("| `%s.` | %s | %s |%s" % (p, ", ".join("`%s`" % f for f in files), "; ".join(sorted(set(owner(f) for f in files))),
                                         (" " + NOTE[p] + " |") if p in NOTE else " |"))
table = ("**00.16.2a The id-prefix registry.** `[D]` Generated at integration from the ids defined in `data/` "
         "(`_process/simulation/integration-prefix-registry.py`); every prefix in use is registered here with the file(s) "
         "that define it and the owning chapter (T-00-19). 00.16.2's named prefixes are the core of this list; a new prefix "
         "is added by regenerating the table [amended: integration, DL-INT-11].\n\n"
         "| Prefix | Defined in | Owner | Note |\n|---|---|---|---|\n" + "\n".join(rows) + "\n")
P = os.path.join(R, "00-architecture.md")
s = open(P, encoding="utf-8").read()
if "**00.16.2a The id-prefix registry.**" in s:
    a = s.index("**00.16.2a The id-prefix registry.**")
    b = s.index("**00.16.3 Lifecycle")
    s = s[:a] + table + "\n" + s[b:]
else:
    b = s.index("**00.16.3 Lifecycle")
    s = s[:b] + table + "\n" + s[b:]
open(P, "w", encoding="utf-8", newline="\n").write(s)
print("registered prefixes:", len(rows))
