"""validate_ruleset.py -- mechanical validation of The Game's ruleset (rules/). Re-runnable at any time.

    python rules/_process/validate_ruleset.py            # full report to stdout; exit 1 if any ERROR
    python rules/_process/validate_ruleset.py --json out # also write the findings as JSON

Checks (each finding is ERROR, WARN or INFO; the summary counts them):
  1. YAML      every data/*.yaml parses (and every fragment in _process/merged-contrib/); no mapping key parses as a
               boolean (an unquoted on/off/yes/no/true/false key).
  2. IDS       every prefixed id defined in data/ (a mapping's `id`, tags and facets in tags.yaml, handler ids, reserved
               ids) is defined exactly once; every id prefix is registered (00.16.2 + the generated registry 00.16.2a).
  3. REFS-DATA every id referenced anywhere in data/ (any string value; effect_id, condition, tags, refs, notes...)
               resolves to a definition (exact; or, for entity/fact paths like npc.x.standing, to a defining prefix).
  4. RESERVED  every reserved id of substrate.yaml#reserved_ids is defined by its owning file.
  5. REFS-MD   every backticked id in the chapters, SCHEMAS and appendix resolves; unresolved ids inside Worked
               examples are reported separately (examples are allowed to be illustrative, 00 "Reading this chapter").
  6. XREF      every rule-id cross-reference (NN.S.R, PR-NN-n, T-NN-n, WE-NN-n, DL-NN-n, OEQ-NN-n, INV-n, SG-nn,
               CT-n, I-nnn) in chapters, appendix, SCHEMAS and the process registers resolves to a definition.
  7. BANNED    T-00-22's banned words absent from rules text and data outside quotations (with the documented
               legitimate senses allowed: tag "levels", P-B "class (i)", visibility "classes", etc.).
  8. JRULES    every rule with a [J:*] decision has a Worst case line; counts inline-form vs template-form (I-001).
  9. HANDLERS  every handler's boundary and phase are legal, `before` targets exist in the same phase.
 10. BLOCKS    every owner-block owner is allowed by T-00-19.
 11. POOLS     (INFO) long-horizon pick depth: own-pool size per calling; a min_tier-4 and a min_tier-5 ability per level-2 node (I-087).
"""
import glob, json, os, re, sys
from collections import Counter, defaultdict, OrderedDict
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.normpath(os.path.join(HERE, ".."))
DATA = os.path.join(R, "data")
CHAPTERS = ["00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "15", "16"]
F = []  # findings: (level, check, where, message)
def add(level, check, where, msg): F.append((level, check, where, msg))

def read(p):
    return open(p, encoding="utf-8").read().replace("\r\n", "\n")
CH_FILES = {c: glob.glob(os.path.join(R, c + "-*.md"))[0] for c in CHAPTERS}
CH_TEXT = {c: read(p) for c, p in CH_FILES.items()}

# ====================================================================== 1. YAML
DOCS = {}
for p in sorted(glob.glob(os.path.join(DATA, "*.yaml"))):
    try:
        DOCS[os.path.basename(p)] = yaml.safe_load(open(p, encoding="utf-8"))
    except Exception as e:
        add("ERROR", "YAML", os.path.basename(p), "does not parse: %s" % str(e).split("\n")[0])
for p in sorted(glob.glob(os.path.join(R, "_process", "merged-contrib", "*.yaml"))):
    try:
        yaml.safe_load(open(p, encoding="utf-8"))
    except Exception as e:
        add("ERROR", "YAML", "merged-contrib/" + os.path.basename(p), "does not parse: %s" % e)
# a mapping key that YAML 1.1 reads as a boolean (on / off / yes / no / true / false unquoted) is a defect: the
# engine looks the key up by its word (e.g. a tick source's `on`) [revision B: 54 such keys were found and quoted]
def _boolkeys(x, path):
    if isinstance(x, dict):
        for k, v in x.items():
            if isinstance(k, bool):
                yield path
            yield from _boolkeys(v, "%s/%s" % (path, k))
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from _boolkeys(v, "%s[%d]" % (path, i))
for _f, _d in DOCS.items():
    _bk = list(_boolkeys(_d, ""))
    if _bk:
        add("ERROR", "YAML", _f, "%d mapping key(s) parse as booleans (quote on/off/yes/no/true/false): %s" % (len(_bk), ", ".join(_bk[:4])))

# ====================================================================== 2. definitions
FACETS = ["deed", "conduct", "creature", "harm", "material", "item", "terrain", "situation", "trait", "org"]
TAGS = set()
td = DOCS.get("tags.yaml") or {}
for f in td.get("facets", []): TAGS.add(f["id"])
for t in td.get("tags", []): TAGS.add(t["id"])

DEF = defaultdict(list)        # id -> [where]  (every place an id is written as a mapping's `id`)
OCC = defaultdict(list)        # id -> [(kind, where, mapping)]
# Where an id is DEFINED: an entry of a file's main collections (a list under a top-level key, a list under a key of
# a top-level mapping, an owner-block's entries/handlers, or a top-level mapping with an id). Elsewhere an `id`
# is a REFERENCE that may carry local overrides (sites.yaml's hazards and traps per domain, a pool record in a
# gen_*.yaml naming the content it draws, a clock restated in a case). Entries with `mirror_of` are mirrors.
# The calendar name overlay (cal.*) restates engine ids: those are references.
def classify(fname, path, x):
    if "mirror_of" in x: return "mirror"
    if "is_faction_goal_of" in x: return "view"        # a case's view of a faction goal clock (13 data)
    if fname.startswith("gen_") and re.match(r"^/pool\[\d+\]$", path): return "poolref" if "source" in x else "pool"
    if re.match(r"^/blocks\[\d+\]/(?:entries|handlers)\[\d+\]$", path): return "primary"
    if re.match(r"^/[^/\[]+\[\d+\]$", path) or re.match(r"^/[^/\[]+/[^/\[]+\[\d+\]$", path): return "primary"
    if re.match(r"^/[^/\[]+$", path) and fname.startswith("region_") and path == "/region": return "nested"
    if re.match(r"^/[^/\[]+$", path): return "primary"
    return "nested"
def walk_defs(x, fname, path, in_overlay=False):
    if isinstance(x, dict):
        i = x.get("id")
        if isinstance(i, str) and "." in i and (not in_overlay or i not in OVERLAY_SKIP):
            k = classify(fname, path, x)
            OCC[i].append((k, fname + path, x))
            DEF[i].append(fname + path)
        overlay = in_overlay or (isinstance(i, str) and i.startswith("cal."))
        for kk, v in x.items():
            walk_defs(v, fname, path + "/" + str(kk), overlay and kk != "id")
    elif isinstance(x, list):
        for n, v in enumerate(x):
            walk_defs(v, fname, path + "[%d]" % n, in_overlay)
OVERLAY_SKIP = set()
def _pre(x):
    if isinstance(x, dict):
        if isinstance(x.get("id"), str): OVERLAY_SKIP.add(x["id"])
        for v in x.values(): _pre(v)
    elif isinstance(x, list):
        for v in x: _pre(v)
for fname, d in DOCS.items():
    if fname in ("tags.yaml", "calendar.yaml"): continue
    _pre(d)
cal = DOCS.get("calendar.yaml") or {}
for k, v in cal.items():
    if k != "blocks": _pre(v)
for fname, d in DOCS.items():
    if fname == "tags.yaml": continue
    walk_defs(d, fname, "")
# ids defined as mapping KEYS (tables keyed by id at the top level or one level down, e.g. world_turn.yaml's tbl.11.*)
KEY_ID = re.compile(r"^[a-z_]+\.[a-z0-9_.]+$")
for fname, d in DOCS.items():
    if not isinstance(d, dict) or fname == "tags.yaml": continue
    for k, v in d.items():
        if isinstance(k, str) and KEY_ID.match(k) and k.split(".")[0] not in FACETS and k not in OCC: DEF[k].append("%s#%s (key)" % (fname, k))
        if isinstance(v, dict):
            for k2 in v:
                if isinstance(k2, str) and KEY_ID.match(k2) and k2.split(".")[0] not in FACETS and k2 not in OCC: DEF[k2].append("%s#%s/%s (key)" % (fname, k, k2))
# id families declared by id_form / id_pattern ("rit.custom.<n>", "clk.morale.<side>") and runtime instances a record
# names in a *_clock field (a site's progress and danger clocks)
FAMILIES = set()
for fname, d in DOCS.items():
    for path, sv in []: pass
def _fam(x, fname, path=""):
    if isinstance(x, dict):
        for k, v in x.items():
            if k in ("id_form", "id_pattern", "pattern", "entry_key") and isinstance(v, str):
                m = re.match(r"^([a-z_]+(?:\.[a-z0-9_]+)*)\.[<{*]", v.strip())
                if m: FAMILIES.add(m.group(1))
            if isinstance(k, str) and k.endswith("_clock") and isinstance(v, str) and re.match(r"^clk\.[a-z0-9_.]+$", v.strip()):
                DEF[v.strip()].append("%s%s/%s (instance)" % (fname, path, k))
            _fam(v, fname, path + "/" + str(k))
    elif isinstance(x, list):
        for n, v in enumerate(x): _fam(v, fname, path + "[%d]" % n)
for fname, d in DOCS.items(): _fam(d, fname)
# canonical "defined as a list of strings" families
sub = DOCS.get("substrate.yaml") or {}
for s in sub.get("behavioral_slots", []): pass   # slots are mapping ids already
for h in sub.get("hooks", []): DEF.setdefault("hook." + h["id"], ["substrate.yaml/hooks"])
GEN_DOMAINS = set((sub.get("reserved_ids") or {}).get("generator_domains", []))
for g in GEN_DOMAINS:   # a domain is defined by its gen_*.yaml file's `domain` key, or (gen.pick) by 00.11.1
    files = [f for f, d in DOCS.items() if isinstance(d, dict) and d.get("domain") == g]
    if files: DEF[g] += ["%s/domain" % f for f in files]
    elif g == "gen.pick": DEF[g].append("00-architecture.md#00.11.1 (PR-04-5 over abilities.yaml)")
INLINE_CLOCK = re.compile(r"\b(clk\.[a-z0-9_]+(?:\.[a-z0-9_]+)*)\s*\((?:public|sensed|hidden|\d+(?:\s*segments|\s*,))")
for fname in DOCS:
    for m in INLINE_CLOCK.finditer(read(os.path.join(DATA, fname))):
        DEF[m.group(1)].append("%s (inline clock spec)" % fname)
TRIGGERS = set()
for c, t in CH_TEXT.items(): TRIGGERS |= set(re.findall(r"\btrg\.[a-z0-9_]+(?:\.[a-z0-9_]+)*", t))
ALL_IDS = set(DEF) | TAGS | TRIGGERS

# id spelling: snake_case segments only (00.16.1)
for i in sorted(OCC):
    if "<" not in i and not re.match(r"^[a-z0-9_]+(\.[a-z0-9_]+)+$", i) and not re.match(r"^veh\.V\d+$", i):
        add("ERROR", "IDS", i, "id is not snake_case dot segments (00.16.1): %s" % OCC[i][0][1])
# duplicates: an id with more than one primary definition is an ERROR; an id defined only by nested or pool records
# in several places is a WARN when the records differ in more than local placement fields
LOCAL = {"weight", "where", "active_when", "chance", "count", "band", "note", "notes", "when", "range", "share"}
for i, occ in sorted(OCC.items()):
    prim = [o for o in occ if o[0] == "primary"]
    if len(prim) > 1:
        add("ERROR", "IDS", i, "defined %d times: %s" % (len(prim), "; ".join(o[1] for o in prim[:4])))
    elif not prim:
        defs = [o for o in occ if o[0] in ("nested", "pool")]
        if len(defs) > 1:
            core = [json.dumps({k: v for k, v in o[2].items() if k not in LOCAL}, sort_keys=True, default=str) for o in defs]
            if len(set(core)) > 1:
                add("WARN", "IDS", i, "restated %d times with different content and no primary definition: %s" % (len(defs), "; ".join(o[1] for o in defs[:3])))
    for o in occ:
        if o[0] == "mirror":
            tgt = str(o[2].get("mirror_of", "")).split("/")[-1]
            if tgt != i and tgt not in OCC: add("ERROR", "IDS", i, "mirror_of target %s does not resolve" % o[2].get("mirror_of"))

# prefix registry
# registered prefixes: 00.16.2's named list plus the generated registry table 00.16.2a
_t00 = CH_TEXT["00"]
_a, _b = _t00.index("**00.16.2 Id prefixes.**"), _t00.index("**00.16.3 Lifecycle")
REGISTERED = set(re.findall(r"`([a-z_]+)\.`", _t00[_a:_b])) | {"attr"}
REGISTRY_FILE = os.path.join(HERE, "id-prefix-registry.yaml")
EXTRA = {}
if os.path.exists(REGISTRY_FILE):
    EXTRA = (yaml.safe_load(open(REGISTRY_FILE, encoding="utf-8")) or {}).get("prefixes", {})
PREFIX_FILES = defaultdict(set)
for i, w in DEF.items():
    if i.startswith("hook."): continue
    PREFIX_FILES[i.split(".")[0]].update(x.split("/")[0] for x in w)
for p, files in sorted(PREFIX_FILES.items()):
    if p not in REGISTERED and p not in EXTRA:
        add("ERROR", "IDS", p + ".", "id prefix not registered in 00.16.2 or the prefix registry (defined in %s)" % ", ".join(sorted(files)))
KNOWN_PREFIXES = set(PREFIX_FILES) | REGISTERED | set(EXTRA)

# ====================================================================== 3. references in data
FACT_PATH = {"npc", "loc", "pc", "item", "fac", "adv", "obj", "cmp", "sit", "thr", "rum", "keeper", "case", "clu", "lie",
             "arch", "clk", "dc", "rep", "chr", "legacy", "imp", "wr", "bang", "ftpl", "site", "haz", "trap", "cal", "h"}
PFX = sorted(KNOWN_PREFIXES | set(FACETS), key=len, reverse=True)
TOKEN = re.compile(r"(?<![\w.<*{/#@$%-])(" + "|".join(re.escape(p) for p in PFX) + r")\.[a-z0-9_]+(?:\.[a-z0-9_]+)*(?![\w<*{-])(?!\.[<*{])(?!\.(?:yaml|md|py))")
IGNORE_TOKENS = {"item.i0042", "pc.wren"}
FIELD_PATHS = {"item.location", "item.condition", "item.exists", "item.state", "cost.focus", "trap.alarm_ticks"}
def resolves(tok, doc=None):
    if tok in ALL_IDS or tok in IGNORE_TOKENS or tok in FIELD_PATHS: return True
    head = tok.split(".")[0]
    if head == "scn": return True                      # scene records are runtime (12.4)
    if any(tok == f or tok.startswith(f + ".") for f in FAMILIES): return True
    if isinstance(doc, dict) and head in doc:          # a key path inside the same file (region checklist paths)
        cur, depth = doc, 0
        for seg in tok.split("."):
            if isinstance(cur, dict) and seg in cur: cur = cur[seg]; depth += 1
            elif isinstance(cur, list) and depth >= 2: break
            else: cur = None; break
        if cur is not None: return True
    if head in FACETS: return False
    if head == "pc": return True                       # the PC's own fact paths (pc.<anything>)
    if head not in FACETS:
        segs = tok.split(".")
        for n in range(len(segs) - 1, 1, -1):
            if ".".join(segs[:n]) in ALL_IDS: return True
    return False
def strings(x, path=""):
    if isinstance(x, dict):
        for k, v in x.items():
            if isinstance(k, str): yield path + "/" + k + "#key", k
            yield from strings(v, path + "/" + str(k))
    elif isinstance(x, list):
        for n, v in enumerate(x): yield from strings(v, path + "[%d]" % n)
    elif isinstance(x, str):
        yield path, x
UNRES_DATA, UNRES_EXAMPLE = defaultdict(list), defaultdict(list)
INLINE_DEF = re.compile(r"^\s*\((?:public|sensed|hidden)")
for fname, d in DOCS.items():
    for path, s in strings(d):
        for m in TOKEN.finditer(s):
            tok = m.group(0).rstrip(".")
            if tok.count(".") == 0 or tok.endswith((".yaml", ".md", ".py")): continue
            if fname == "tags.yaml" and tok.split(".")[0] not in FACETS: continue   # relative names in definitions
            if INLINE_DEF.match(s[m.end():]): continue                                # a clock created inline by description
            if s[m.end():m.end() + 1] == "." and s[m.end() + 1:m.end() + 2].strip(): continue   # a longer placeholder form
            if not resolves(tok, d):
                if fname == "investigation.yaml" and re.match(r"^/cases\[0\]", path):
                    UNRES_EXAMPLE[tok].append(fname + path)
                else:
                    UNRES_DATA[tok].append(fname + path)
for tok, w in sorted(UNRES_DATA.items()):
    add("ERROR", "REFS-DATA", tok, "unresolved reference (%d uses): %s" % (len(w), "; ".join(sorted(set(w))[:3])))
for tok, w in sorted(UNRES_EXAMPLE.items()):
    add("INFO", "REFS-EX", tok, "placeholder id in the unplaced model case case.mill_fire: %s" % "; ".join(sorted(set(w))[:2]))

# ====================================================================== 4. reserved ids
RES_OWNER = {"range_bands": "conflict.yaml", "positional_flags": "conflict.yaml", "harm_states": "harm.yaml",
             "cost_menu": "resolution.yaml", "conditions": "conditions.yaml"}
for fam, ids in (sub.get("reserved_ids") or {}).items():
    if fam not in RES_OWNER: continue
    for i in ids:
        w = DEF.get(i, [])
        if not w: add("ERROR", "RESERVED", i, "reserved (%s) but not defined" % fam)
        elif not any(x.startswith(RES_OWNER[fam]) for x in w):
            add("WARN", "RESERVED", i, "reserved (%s) but defined outside %s: %s" % (fam, RES_OWNER[fam], w))

# ====================================================================== 5/6. markdown ids and cross-references
MD = OrderedDict()
for c in CHAPTERS: MD["%s" % os.path.basename(CH_FILES[c])] = CH_TEXT[c]
for p in [os.path.join(DATA, "SCHEMAS.md"), os.path.join(R, "appendix", "decision-log.md"), os.path.join(R, "appendix", "traceability.md"),
          os.path.join(R, "_process", "INTERFACE-REQUESTS.md"), os.path.join(R, "_process", "issue-ledger.md")]:
    MD[os.path.relpath(p, R).replace("\\", "/")] = read(p)

# definitions of rule-level ids
RDEF = set()
for c, t in CH_TEXT.items():
    for m in re.finditer(r"^(?:\*\*|#{2,4}\s+)(\d\d\.\d+(?:\.\d+)?)\b", t, re.M): RDEF.add(m.group(1))
    for m in re.finditer(r"^#{2,4}\s+(\d\d\.\d+)\s", t, re.M): RDEF.add(m.group(1))
    for m in re.finditer(r"\*\*((?:PR|T|WE)-\d\d-\d+)\b", t): RDEF.add(m.group(1))
    for m in re.finditer(r"^#{2,4}\s+((?:WE|PR|T)-\d\d-\d+)\b", t, re.M): RDEF.add(m.group(1))
    for m in re.finditer(r"^\|\s*(OEQ-\d\d-\d+)\s*\|", t, re.M): RDEF.add(m.group(1))
    for m in re.finditer(r"^\|\s*\*?\*?((?:T|PR)-\d\d-\d+)\b", t, re.M): RDEF.add(m.group(1))
for m in re.finditer(r"^#{3}\s+(DL-(?:\d\d[A]?|INT)-\d+)", MD["appendix/decision-log.md"], re.M): RDEF.add(m.group(1))
for m in re.finditer(r"^\|\s*(I-\d{3})\s*\|", MD["_process/issue-ledger.md"], re.M): RDEF.add(m.group(1))
for m in re.finditer(r"^\|\s*(INV-\d+)\s*\|", CH_TEXT["00"], re.M): RDEF.add(m.group(1))
for m in re.finditer(r"\*\*(SG-\d\d)\b", CH_TEXT["00"]): RDEF.add(m.group(1))
for m in re.finditer(r"^\|\s*(CT-\d)\b", CH_TEXT["00"], re.M): RDEF.add(m.group(1))
# T-00-n tables indexed in 00's Tables preamble (T-00-2, -3, -8, ...) are embedded tables: defined by that index line
for m in re.finditer(r"\*\*(T-\d\d-\d+)\*\*", "\n".join(CH_TEXT.values())): RDEF.add(m.group(1))

XREF = re.compile(r"(?<![\w.\-/])((?:0\d|1[0-6])\.\d{1,2}\.\d{1,2}|(?:PR|T|WE|OEQ)-\d\d-\d+|DL-(?:\d\d[A]?|INT)-\d+|INV-\d+|SG-\d\d|CT-\d|I-\d{3})(?![\d])")
def strip_code_urls(t):
    t = re.sub(r"https?://\S+", " ", t)
    return t
XR_BAD = defaultdict(set)
for name, t in MD.items():
    tt = strip_code_urls(t)
    for m in XREF.finditer(tt):
        ref = m.group(1)
        if ref in RDEF: continue
        if re.match(r"\d\d\.\d+\.\d+", ref):
            ch = ref[:2]
            if ch not in CHAPTERS:   # 14 is not written yet (Wave 6): references to it are forward references
                if ch == "14": continue
        if ref.startswith(("SG-",)) and int(ref[3:]) <= 28: RDEF.add(ref); continue
        if ref.startswith(("PR-14", "T-14", "WE-14", "OEQ-14")): continue
        if ref.startswith("DL-00-") or ref.startswith("DL-00A-"):
            pass
        line = t[:m.start()].count("\n") + 1
        XR_BAD[ref].add("%s:%d" % (name, line))
for ref, w in sorted(XR_BAD.items()):
    add("ERROR", "XREF", ref, "cross-reference does not resolve (%d places): %s" % (len(w), ", ".join(sorted(w)[:4])))

# backticked ids in markdown
BT = re.compile(r"`([a-z_]+\.[a-z0-9_.]+[a-z0-9_])`")
# documented illustrations in rules text: each is shown as an example of a shape, not a reference to content
ILLUSTRATIVE = {
    "creature.dragon.great.vermithrax": "00.5.5 rule 7's non-example (a tag names a kind, never an individual)",
    "deed.martial.blade.sword.longsword": "00.5.5 rule 3's example of the maximum depth",
    "loc.grey_keep.archive": "00.6.1's example column (Wren's illustrative world)",
    "lic.fact.forge_key": "01.3's example of a fact license",
    "npc.tam_harlan.siblings": "01.3's example OOF line, from WE-01-2's illustrative guard",
    "site.intervals_since_check": "a field of a site record (10.9.3), not a site-theme id",
    "harm.severity_by_band": "a field path inside traps.yaml entries (10.14)",
}
REGION = DOCS.get("region_thallen.yaml") or {}
MD_UNRES, MD_UNRES_EX = defaultdict(set), defaultdict(set)
for name, t in MD.items():
    if not name[:2].isdigit() and not name.startswith("data/"): continue
    # worked-example spans
    ex_spans = []
    for m in re.finditer(r"^## Worked examples\s*$", t, re.M):
        e = re.search(r"^## (?!Worked)", t[m.end():], re.M)
        ex_spans.append((m.start(), m.end() + (e.start() if e else len(t))))
    for m in BT.finditer(t):
        tok = m.group(1)
        head = tok.split(".")[0]
        if head not in KNOWN_PREFIXES and head not in FACETS: continue
        if tok.endswith(("yaml", ".md", ".py")) or tok in ILLUSTRATIVE: continue
        if resolves(tok) or (name.startswith("13") and resolves(tok, REGION)): continue
        line = t[:m.start()].count("\n") + 1
        ir = t.rfind("\n## Interface requests", 0, m.start()) > t.rfind("\n## Open empirical", 0, m.start()) and t.rfind("\n## Interface requests", 0, m.start()) != -1
        if any(a <= m.start() < b for a, b in ex_spans) or ir: MD_UNRES_EX[tok].add("%s:%d" % (name, line))
        else: MD_UNRES[tok].add("%s:%d" % (name, line))
for tok, w in sorted(MD_UNRES.items()):
    add("WARN", "REFS-MD", tok, "backticked id does not resolve (%d places): %s" % (len(w), ", ".join(sorted(w)[:4])))
for tok, w in sorted(MD_UNRES_EX.items()):
    add("INFO", "REFS-MD-EX", tok, "illustrative id in a worked example or a proposal in Interface requests (%d places): %s" % (len(w), ", ".join(sorted(w)[:3])))

# ====================================================================== 7. banned words
BANNED = [
    ("level (of a character)", re.compile(r"\b(?:character|PC'?s?|your|their|his|her|its)\s+level\b(?![- ]\d)|\blevel[- ]?up\b|\blevels? of (?:the )?(?:character|PC)\b|\bexperience level\b", re.I)),
    ("class", re.compile(r"\b(?:character|PC'?s?|your|a|the|his|her|their)\s+class(?:es)?\b(?!\s*\(?(?:i|ii|iii|iv)\b)(?!\s+(?:of|iv|iii|ii|i)\b)|\bclass(?:es)? (?:features?|abilities|skills|levels?)\b|\bmulticlass", re.I)),
    ("XP", re.compile(r"\bXP\b|(?<!no )\bexperience points?\b")),
    ("HP / hit points", re.compile(r"\bHP\b|\bhit points?\b", re.I)),
    ("mana / stamina", re.compile(r"\bmana\b|\bstamina\b", re.I)),
    ("saving throw", re.compile(r"\bsaving throws?\b", re.I)),
    ("skill check", re.compile(r"\bskill checks?\b", re.I)),
    ("advantage / disadvantage", re.compile(r"\b(?:with|at|has|have|gains?|grants?|roll(?:s|ed)? with)\s+(?:dis)?advantage\b|\bdisadvantage\b", re.I)),
    ("injury / injured / hurt", re.compile(r"\binjur(?:y|ies|ed)\b(?!\.yaml)|\bhurt\b", re.I)),
    ("minor / major / severe (severity)", re.compile(r"\b(?:minor|major|severe)\s+(?:harm|wounds?|costs?|damage|injur\w*|conditions?|severity|hazards?|consequences?|effects?|NPCs?)\b", re.I)),
    ("exploration turn", re.compile(r"\bexploration turns?\b", re.I)),
    ("the System", re.compile(r"\bthe System\b")),
    ("focus (for an item)", re.compile(r"\b(?:a|an|arcane|holy|druidic|spellcasting|his|her|my|your)\s+focus\b(?!\s+(?:on|of|cost|pool|point|spent|max|node|branch))(?!:)")),
]
QUOTE = re.compile(r"“[^”]*”|\"[^\"\n]*\"|`[^`\n]*`|\*[^*\n]+\*")
SKIP_LINE = re.compile(r"T-00-22|00\.18\.1|banned|never (?:say|use|write)|not \"|SG-21|Banned|`injuries\.yaml`|injuries\.yaml|inj\.|\binjuries \(07\)|afflictions(?:,| and) injuries|^injuries:|Injury: id|5e |D&D|Pathfinder|PF2e|assigned to a class|as severity names|injuries, which|the classes every|strongest nodes at its level|\*injury /|\*mana\*|points\*, \*mana", re.I)
def banned_scan(name, text, kind):
    for n, line in enumerate(text.split("\n"), 1):
        if SKIP_LINE.search(line): continue
        clean = QUOTE.sub(" ", line)
        clean = re.sub(r"\[R[^\]]*\]|https?://\S+", " ", clean)
        for label, rx in BANNED:
            m = rx.search(clean)
            if m:
                add("WARN", "BANNED", "%s:%d" % (name, n), "%s: '%s' — %s" % (label, m.group(0), line.strip()[:150]))
for c in CHAPTERS:
    banned_scan(os.path.basename(CH_FILES[c]), CH_TEXT[c], "md")
for fname in DOCS:
    banned_scan("data/" + fname, read(os.path.join(DATA, fname)), "yaml")

# ====================================================================== 8. [J:*] rules and their Worst case lines
J_STATS = Counter()
J_MISSING = []
for c in CHAPTERS:
    t = CH_TEXT[c]
    lines = t.split("\n")
    heads = []
    in_code = False
    for n, l in enumerate(lines):
        if l.startswith("```"): in_code = not in_code
        m = re.match(r"^\*\*(%s\.\d+\.\d+)\b" % c, l) if not in_code else re.match(r"^###\s+(%s\.\d+\.\d+)\b" % c, l)
        if m: heads.append((n, m.group(1), in_code))
    # a rule = the union of every block carrying its id (bold rule + its card)
    blocks = defaultdict(list)
    for k, (n, rid, card) in enumerate(heads):
        end = heads[k + 1][0] if k + 1 < len(heads) else len(lines)
        # stop at the next section heading
        for j in range(n + 1, end):
            if re.match(r"^#{2,3}\s+(?!%s\.)" % c, lines[j]) and not (lines[j].startswith("### ") and re.match(r"^###\s+\d\d\.", lines[j])):
                end = j; break
        blocks[rid].append("\n".join(lines[n:end]))
    for rid, bl in blocks.items():
        body = "\n".join(bl)
        first_lines = "\n".join(b.split("\n")[0] for b in bl)
        if not re.search(r"\[J:(?:flag|enum|rung|open)\]|\[J\]", first_lines): continue
        J_STATS["rules_with_J"] += 1
        tmpl = bool(re.search(r"^Worst case \(J\):", body, re.M))
        # 00.2.5 [revision: I-001]: the inline form's label is *Worst case (J…*; ch.13 (not edited) keeps its legacy labels
        inline = bool(re.search(r"\*[Ww]orst\s+case \(J", body)) and not tmpl
        legacy = bool(re.search(r"worst[\s*_]+case", body, re.I)) and not (tmpl or inline)
        if tmpl: J_STATS["template_form"] += 1
        elif inline: J_STATS["inline_form"] += 1
        elif legacy and c == "13": J_STATS["inline_form_legacy_13"] += 1
        elif legacy:
            J_STATS["noncanonical"] += 1
            add("ERROR", "JRULES", rid, "inline worst case without the *Worst case (J):* label (00.2.5)")
        else:
            J_STATS["missing"] += 1
            J_MISSING.append(rid)
for rid in J_MISSING:
    add("ERROR", "JRULES", rid, "rule with a [J:*] decision has no Worst case line")

# ====================================================================== 9. handlers
bd = DOCS.get("boundaries.yaml") or {}
BOUNDS = set(bd.get("boundaries", {}).get("time", [])) | set(bd.get("boundaries", {}).get("event", [])) | {"*"}
HANDLERS = {}
for b in bd.get("blocks", []):
    for h in b.get("handlers", []):
        HANDLERS[h["id"]] = (b["owner"], h)
        if not h["id"].startswith("h.%s." % b["owner"]):
            add("ERROR", "HANDLERS", h["id"], "in owner-block %s but not prefixed h.%s." % (b["owner"], b["owner"]))
        for x in (h["boundary"] if isinstance(h["boundary"], list) else [h["boundary"]]):
            if x not in BOUNDS: add("ERROR", "HANDLERS", h["id"], "unknown boundary %s" % x)
        if not (isinstance(h.get("phase"), int) and 1 <= h["phase"] <= 9): add("ERROR", "HANDLERS", h["id"], "phase %s" % h.get("phase"))
for hid, (o, h) in HANDLERS.items():
    for t in h.get("before", []) or []:
        if t not in HANDLERS: add("ERROR", "HANDLERS", hid, "before: unknown handler %s" % t)
        elif HANDLERS[t][1]["phase"] != h["phase"]: add("ERROR", "HANDLERS", hid, "before: %s is in another phase" % t)
# handler ids named in chapters must exist
for c, t in CH_TEXT.items():
    for m in set(re.findall(r"\bh\.\d\d\.[a-z_]+\b", t)):
        if m not in HANDLERS: add("ERROR", "HANDLERS", m, "named in %s but not registered in boundaries.yaml" % os.path.basename(CH_FILES[c]))

# ====================================================================== 10. owner-blocks vs T-00-19
ALLOWED = {"effects.yaml": {"02", "04", "05", "06", "07", "08", "09", "10", "11", "15", "16"},
           "licenses.yaml": {"02", "04", "08", "13", "15"}, "composites.yaml": {"04"}, "conditions.yaml": {"07"},
           "origins.yaml": {"13"}, "gen_birth.yaml": {"13"}, "kits.yaml": {"13"}, "adversaries.yaml": {"13"},
           "hazards.yaml": {"13"}, "travel.yaml": {"13"}, "sites.yaml": {"13"}, "traps.yaml": {"13"}, "weather.yaml": {"13"},
           "factions.yaml": {"13"}, "calendar.yaml": {"13"}, "afflictions.yaml": {"13"},
           "boundaries.yaml": set(CHAPTERS) | {"14"}}
for fname, d in DOCS.items():
    if not isinstance(d, dict) or not d.get("blocks"): continue
    for b in d["blocks"]:
        o = str(b.get("owner"))
        if fname in ALLOWED and o not in ALLOWED[fname]:
            add("ERROR", "BLOCKS", fname, "owner-block %s not allowed by T-00-19" % o)
        elif fname not in ALLOWED:
            add("ERROR", "BLOCKS", fname, "has owner-blocks but T-00-19 allows none")

# ====================================================================== 11. POOLS (INFO; revision I-087)
# Long-horizon pick depth: for each calling, the pool abilities it can draw as OWN picks (04.8.4: first tag at or
# under pool_gate.own, non-oath; for a conduct calling, oath abilities on its axis and pole) and the highest
# min_tier among them; for each level-2 deed node, whether pool abilities at min_tier 4 and at min_tier 5 start under it. INFO only:
# kin picks are legal, so a thin own pool is a depth gap to author into (ch.05), never an error.
try:
    _AB = [a for a in (DOCS.get("abilities.yaml") or {}).get("abilities", [])
           if a.get("slot_class") == "calling" and not a.get("retired") and not a.get("adversary_only")]
    _CL = (DOCS.get("callings.yaml") or {}).get("callings", [])
    _under = lambda t, g: t == g or t.startswith(g + ".")
    thin = no5 = none5_conduct = 0
    for c in _CL:
        g = c.get("pool_gate") or {}
        if c.get("breadth") in ("vow", "dark"):
            pole = "positive" if c.get("breadth") == "vow" else "negative"
            el = [a for a in _AB if a.get("conduct_pole") == pole and set(a.get("requires_conduct") or []) & set(g.get("conduct") or [])]
            if not any(a.get("min_tier", 1) >= 5 for a in el): none5_conduct += 1
        else:
            el = [a for a in _AB if not a.get("conduct_pole") and any(_under(a["tags"][0], x) for x in g.get("own") or [])]
        if c.get("kind") == "specialist" and c.get("breadth") not in ("vow", "dark"):
            if len(el) < 6: thin += 1
            if not any(a.get("min_tier", 1) >= 5 for a in el): no5 += 1
    add("INFO", "POOLS", "callings.yaml", "%d of %d deed-keyed specialist callings have fewer than six own-pool abilities; %d have no own-pool tier-5 ability; %d vow/dark callings have no tier-5 oath ability on their axis"
        % (thin, sum(1 for c in _CL if c.get("kind") == "specialist" and c.get("breadth") not in ("vow", "dark")), no5, none5_conduct))
    _L2 = sorted({".".join(a["tags"][0].split(".")[:3]) for a in _AB if a["tags"][0].startswith("deed.")})
    # [revision: I-087] each level-2 node needs one pool ability at min_tier 4 AND one at min_tier 5 (C2c).
    _has = lambda n, t: any(_under(a["tags"][0], n) and a.get("min_tier", 1) == t for a in _AB if not a.get("conduct_pole"))
    _gap = ["%s (no min_tier %s)" % (n, "/".join(str(t) for t in (4, 5) if not _has(n, t))) for n in _L2 if not (_has(n, 4) and _has(n, 5))]
    add("INFO", "POOLS", "abilities.yaml", "%d of %d level-2 deed nodes lack a pool ability at min_tier 4 or at min_tier 5%s" % (len(_gap), len(_L2), (": " + ", ".join(_gap)) if _gap else ""))
except Exception as e:  # an audit must never break validation
    add("WARN", "POOLS", "abilities.yaml", "pool audit failed: %s" % e)

# ====================================================================== report
def summary():
    c = Counter((lv, ck) for lv, ck, _, _ in F)
    return c
if __name__ == "__main__":
    out_json = sys.argv[sys.argv.index("--json") + 1] if "--json" in sys.argv else None
    c = summary()
    print("=" * 100)
    print("validate_ruleset.py — data files: %d; ids defined: %d (+ %d tags); handlers: %d; rule-level ids indexed: %d"
          % (len(DOCS), len(DEF), len(TAGS), len(HANDLERS), len(RDEF)))
    print("[J:*] rules: %d — Worst case in template form %d, inline form %d (ch.13 legacy label %d), non-canonical %d, missing %d"
          % (J_STATS["rules_with_J"], J_STATS["template_form"], J_STATS["inline_form"], J_STATS["inline_form_legacy_13"],
             J_STATS["noncanonical"], J_STATS["missing"]))
    print("=" * 100)
    for (lv, ck), n in sorted(c.items()):
        print("%-6s %-11s %d" % (lv, ck, n))
    print("-" * 100)
    verbose = "-v" in sys.argv  # INFO lines are expected illustrative ids; shown only with -v
    for lv, ck, where, msg in F:
        if lv == "INFO" and not verbose: continue
        print("%-6s %-11s %-40s %s" % (lv, ck, where, msg))
    if out_json:
        json.dump({"stats": dict(J_STATS), "counts": {"%s %s" % k: v for k, v in c.items()},
                   "findings": [dict(level=a, check=b, where=w, message=m) for a, b, w, m in F]},
                  open(out_json, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    sys.exit(1 if any(lv == "ERROR" for lv, _, _, _ in F) else 0)
