"""12-compile_anchors.py -- compiles rules/data/anchors.yaml per 12.13.6 from every source of anchor cards.

Sources (12.13.6 item 1):
  (a) the `anchor:` fields of data/basic_verbs.yaml (the fifteen verb cards, 01.18) -> specificity verb_card;
  (b) every rule in chapters 01-16 marked `Anchor: yes` -> specificity chapter_rule. A rule is found by its marker
      (a template field `Anchor: yes`, an inline `*Anchor: yes.*`, or a row of the chapter's own anchor table in
      "Edge cases & adaptation anchors"); its intent verbs and knobs are read from the card's `Intent verbs:` /
      `Knobs:` text and from the chapter's anchor table (the table wins for knobs when both exist);
      situation tags from the card's `Loads in:` line; deed tags from the deed tags the card names;
  (c) data entries with an `anchor` block (none outside basic_verbs.yaml at integration), and ch.06's T-06-9
      ready rulings (40 rows; 06.5.10 is their index) -> specificity table_ruling;
  (d) ch.07's anchors "by shape" (07 Edge cases) -> specificity shape, with their parameters mapped to T-00-20
      knobs where one is equivalent and the rest kept under `parameters`.
Validation (12.13.6 item 3): rule id exists as a rule heading; knobs in T-00-20; >= 1 intent verb; tags exist;
ids unique. Errors are printed and recorded in `compile.errors`; warnings in `compile.warnings`.
Usage: python 12-compile_anchors.py  (writes data/anchors.yaml; prints a per-chapter count)
"""
import glob, hashlib, os, re, sys, datetime
from collections import OrderedDict, Counter
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
RULES = os.path.normpath(os.path.join(HERE, "..", ".."))
DATA = os.path.join(RULES, "data")
CHAPTERS = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "15", "16"]
KNOBS = ["dc", "attribute", "action_cost", "reach_unit", "stakes", "duration", "condition", "harm_severity",
         "harm_tags", "targets", "time_cost", "focus_cost"]
KNOB_RE = re.compile(r"`?\b(" + "|".join(sorted(KNOBS, key=len, reverse=True)) + r")\b`?")
RID = r"\d\d\.\d+\.\d+"

def read(p):
    return open(p, encoding="utf-8").read().replace("\r\n", "\n")

tags_doc = yaml.safe_load(open(os.path.join(DATA, "tags.yaml"), encoding="utf-8"))
TAGS = {t["id"] for t in tags_doc["tags"]} | {f["id"] for f in tags_doc["facets"]}
errors, warnings = [], []

# ---------------------------------------------------------------- (a) verb cards (as 12's seed compiler did)
bv_text = read(os.path.join(DATA, "basic_verbs.yaml"))
bv = yaml.safe_load(bv_text)
old = yaml.safe_load(open(os.path.join(DATA, "anchors.yaml"), encoding="utf-8"))
VERB_TAG_MAP = old["compile"]["verb_tag_map"]
anchors = []
for v in bv["verbs"]:
    a = v["anchor"]
    rid = str(a["rule_id"])
    knobs = [{"knob": k["knob"], "default": k.get("default"), "allowed_deltas": k.get("allowed_deltas", [])} for k in a.get("knobs", [])]
    for k in knobs:
        if k["knob"] not in KNOBS: errors.append("%s: knob %s not in T-00-20" % (v["id"], k["knob"]))
    m = VERB_TAG_MAP[v["id"]]
    anchors.append(OrderedDict([("id", "anc." + rid.replace(".", "_")), ("name", v["name"] + " (basic-verb card)"),
        ("rule_id", rid), ("source", "data/basic_verbs.yaml#%s.anchor" % v["id"]), ("verb", v["id"]),
        ("intent_verbs", a["intent_verbs"]), ("deed_tags", m["deed_tags"]), ("situation_tags", m["situation_tags"]),
        ("knobs", knobs), ("degree_table", "data/basic_verbs.yaml#%s.anchor.degree_table (base: %s)" % (v["id"], a.get("degree_table", {}).get("base", "generic"))),
        ("specificity", "verb_card"), ("tags", v.get("traits", [])), ("lifecycle", v.get("lifecycle", "provisional")),
        ("basis", ["[01.18 %s]" % rid, "[00.2.6]", "[00.15.3]", "[12.13.6]"])]))

# ---------------------------------------------------------------- (b) chapter rules
def rule_index(text):
    """(line number, rule id, title) of every rule heading: **NN.S.R Title.** or ### NN.S.R  Title (card header)."""
    out = []
    for i, line in enumerate(text.split("\n")):
        m = re.match(r"^\*\*(" + RID + r")\s+(.+?)[.?!]?\*\*", line) or re.match(r"^###\s+(" + RID + r")\s+(.+?)(?:\s{2,}|\s*\[|$)", line)
        if m:
            out.append((i, m.group(1), m.group(2).strip().rstrip(".")))
    return out

def split_list(s):
    s = s.strip().rstrip(".")
    parts = re.split(r",|;|·", s)
    out = []
    for p in parts:
        p = re.sub(r"\s+", " ", p).strip().strip('"').strip("“”").strip()
        p = re.sub(r"^\(.*?\)\s*", "", p).strip()
        if p and len(p) < 60 and not p.lower().startswith(("knobs", "per ")):
            out.append(p)
    return out

def parse_knobs(s):
    """Knob ids in order with the text that follows each (its default -> deltas)."""
    found = []
    ms = list(KNOB_RE.finditer(s))
    for j, m in enumerate(ms):
        k = m.group(1)
        if any(k == f["knob"] for f in found):
            continue
        end = ms[j + 1].start() if j + 1 < len(ms) else len(s)
        tail = s[m.end():end].strip(" ;,.:()`").strip()
        default, deltas = None, []
        if "→" in tail or "->" in tail:
            a, _, b = re.split(r"(→|->)", tail, 1)
            default = a.strip(" (").strip() or None
            deltas = [x.strip(" )").strip() for x in re.split(r"→|->|;", b) if x.strip(" )").strip()]
        elif tail:
            default = tail[:120]
        found.append({"knob": k, "default": default, "allowed_deltas": deltas})
    return found

per_chapter = Counter()
card_anchors = OrderedDict()
for ch in CHAPTERS:
    path = glob.glob(os.path.join(RULES, ch + "-*.md"))[0]
    fname = os.path.basename(path)
    text = read(path)
    lines = text.split("\n")
    idx = rule_index(text)
    ids = {r for _, r, _ in idx}
    title = {r: t for _, r, t in idx}
    def owner(n):
        best = None
        for i, r, t in idx:
            if i <= n: best = r
            else: break
        return best
    def card_window(rid):
        starts = [i for i, r, _ in idx if r == rid]
        i0 = starts[-1] if starts else None
        if i0 is None: return ""
        nxt = [i for i, r, _ in idx if i > i0]
        return "\n".join(lines[i0:(nxt[0] if nxt else i0 + 60)])
    found = OrderedDict()
    # markers
    for n, line in enumerate(lines):
        if line.startswith("|") or not re.search(r"Anchor:\**\s*yes", line, re.I): continue
        if re.search(r"rules of this chapter|anchors of this chapter|rules in this chapter|Every card|every rule in chapters|Each is an `Anchor|are `Anchor: yes`|template says|is \*\*Anchor: yes\*\*|card, 01\.18\)", line, re.I):
            continue
        rid = owner(n)
        if not rid or not rid.startswith(ch + "."):
            continue
        seg = " ".join(lines[n:n + 8])
        iv = re.search(r"Intent verbs:\s*(.+?)(?:Knobs:|$)", seg)
        kn = re.search(r"Knobs:\s*(.+?)(?:Basis:|Examples:|Degree|$)", seg)
        d = found.setdefault(rid, {"intent": [], "knobs": [], "how": set()})
        d["how"].add("marker")
        if iv: d["intent"] += split_list(iv.group(1))
        if kn: d["knobs"] += parse_knobs(kn.group(1))
    # anchor tables and bold lists in the chapter's Edge cases section (and any table titled as an anchor list)
    for n, line in enumerate(lines):
        if not line.startswith("|") or line.startswith("|---"): continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        hdr_n = n
        while hdr_n > 0 and lines[hdr_n - 1].startswith("|"): hdr_n -= 1
        header = [c.strip().lower() for c in lines[hdr_n].strip().strip("|").split("|")]
        if n <= hdr_n + 1 or not any("knob" in h for h in header): continue
        if not any(("intent" in h or "reach for" in h or "player" in h) for h in header): continue
        caption = " ".join(lines[max(0, hdr_n - 4):hdr_n])
        if not re.search(r"anchor", caption, re.I): continue
        if not (re.search(r"Anchor: yes|Anchor rules|anchors of this chapter", caption, re.I) or "Anchor: yes" in line): continue
        rids = re.findall(RID, line)
        rids = [r for r in rids if r.startswith(ch + ".")]
        if not rids: continue
        rid = rids[0]
        ki = [i for i, h in enumerate(header) if "knob" in h][0]
        ii = [i for i, h in enumerate(header) if ("intent" in h or "reach for" in h or "player" in h)][0]
        d = found.setdefault(rid, {"intent": [], "knobs": [], "how": set()})
        d["how"].add("table")
        if ii < len(cells): d["intent"] += split_list(re.sub(r"\(.*?\)", "", cells[ii]))
        if ki < len(cells):
            tk = parse_knobs(cells[ki])
            if tk: d["knobs"] = tk + [k for k in d["knobs"] if k["knob"] not in {x["knob"] for x in tk}]
    # bold prose lists ("**11.3.15 Muster and clash** (verbs; knobs `a`, `b`)")
    for m in re.finditer(r"\*\*(" + RID + r") [^*]+\*\* \(([^)]*?);\s*knobs ([^)]*)\)", text):
        rid = m.group(1)
        if not rid.startswith(ch + "."): continue
        d = found.setdefault(rid, {"intent": [], "knobs": [], "how": set()})
        d["how"].add("list")
        d["intent"] += split_list(m.group(2))
        if not d["knobs"]: d["knobs"] = parse_knobs(m.group(3))
    # prose lists ("08.1.11 *Improvised weapon* (knobs: a, b; ...)")
    for m in re.finditer(r"(" + RID + r") \*([^*]+)\* \(([^)]*)\)", text):
        rid = m.group(1)
        if not rid.startswith(ch + ".") or "knob" not in m.group(3).lower() and not KNOB_RE.search(m.group(3)): continue
        d = found.setdefault(rid, {"intent": [], "knobs": [], "how": set()})
        d["how"].add("list")
        if not d["knobs"]: d["knobs"] = parse_knobs(m.group(3))
    for rid, d in found.items():
        win = card_window(rid)
        if rid not in ids:
            errors.append("%s: anchor rule %s has no rule heading" % (fname, rid)); continue
        if not d["intent"]:
            iv = re.search(r"Intent verbs:\s*(.+?)(?:Knobs:|\n\S|$)", win, re.S)
            if iv: d["intent"] = split_list(iv.group(1).replace("\n", " "))
        if not d["knobs"]:
            kn = re.search(r"Knobs:\s*(.+?)(?:\n\S|$)", win, re.S)
            if kn: d["knobs"] = parse_knobs(kn.group(1).replace("\n", " "))
        intent = list(OrderedDict.fromkeys(x for x in d["intent"] if x))
        if not intent and rid in title:
            intent = [re.sub(r"^(the|a|an) ", "", title[rid].lower())]
            warnings.append("%s %s: intent verb taken from the rule's title (%s)" % (fname, rid, intent[0]))
        knobs = d["knobs"]
        loads = re.search(r"Loads in:\s*(.+)", win)
        sit = [t for t in re.findall(r"situation\.[a-z_.]+[a-z_]", loads.group(1) if loads else "") if t in TAGS]
        if not sit:
            sit = list(OrderedDict.fromkeys(t for t in re.findall(r"situation\.[a-z_.]+[a-z_]", win) if t in TAGS))[:4]
        deed = list(OrderedDict.fromkeys(t for t in re.findall(r"\bdeed\.[a-z_.]+[a-z_]", win) if t in TAGS))[:6]
        if not intent: errors.append("%s %s: no intent verbs" % (fname, rid))
        if not knobs: warnings.append("%s %s: no knobs found in T-00-20 terms" % (fname, rid))
        anchors.append(OrderedDict([("id", "anc." + rid.replace(".", "_")), ("name", title.get(rid, rid)),
            ("rule_id", rid), ("source", "%s#%s (%s)" % (fname, rid, "+".join(sorted(d["how"])))),
            ("intent_verbs", intent), ("deed_tags", deed), ("situation_tags", sit), ("knobs", knobs),
            ("degree_table", "%s#%s (the rule's own ladder or its anchor card's)" % (fname, rid)),
            ("specificity", "chapter_rule"), ("tags", []), ("lifecycle", "provisional"),
            ("basis", ["[%s]" % rid, "[00.2.6]", "[12.13.6]"])]))
        per_chapter[ch] += 1

_ADDED_SOURCES = ["06's T-06-9 ready rulings (specificity table_ruling)", "07's anchors by shape (specificity shape)"]
# ---------------------------------------------------------------- (c) T-06-9 ready rulings
t06 = read(glob.glob(os.path.join(RULES, "06-*.md"))[0]).split("\n")
i0 = [i for i, l in enumerate(t06) if l.startswith("**T-06-9 ")][0]
rows = []
started = False
for l in t06[i0 + 1:i0 + 120]:
    if l.startswith("|"): started = True
    elif started: break
    m = re.match(r"^\|\s*(\d+)\s*\|(.+)\|\s*$", l)
    if m: rows.append([m.group(1)] + [c.strip() for c in m.group(2).split("|")])
VERB_BY_NAME = {v["name"].lower(): v["id"] for v in bv["verbs"]}
for r in rows:
    n, said, anchor_name, knob_text, against, success, notes = (r + [""] * 7)[:7]
    verb = None
    for name, vid in VERB_BY_NAME.items():
        if anchor_name.lower().startswith(name): verb = vid
    anchors.append(OrderedDict([("id", "anc.06_t9_%02d" % int(n)), ("name", "T-06-9 #%s: %s" % (n, said)),
        ("rule_id", "06.5.10"), ("source", "06-conflict.md#T-06-9 row %s" % n), ("verb", verb),
        ("intent_verbs", [said]), ("deed_tags", []), ("situation_tags", ["situation.conflict"]),
        ("knobs", parse_knobs(knob_text)), ("degree_table", "the anchor card's (%s); on a success: %s" % (anchor_name, success)),
        ("specificity", "table_ruling"), ("rolled_against", against), ("notes", notes), ("tags", []),
        ("lifecycle", "provisional"), ("basis", ["[06.5.10]", "[T-06-9]", "[12.13.6]"])]))
    if verb is None: warnings.append("T-06-9 row %s: anchor '%s' is not a basic-verb name" % (n, anchor_name))
per_chapter["06 (T-06-9 rulings)"] = len(rows)

# ---------------------------------------------------------------- (d) ch.07's anchors by shape (07 Edge cases)
SHAPES = [
    ("07.9.1", "A staged affliction", ["worsens on a schedule unless resisted or treated", "frostbite setting in", "a spreading rot", "a slow enchantment", "an addiction", "a panic moving through a crowd"],
     [("dc", "the virulence tier", []), ("duration", "the cadence", []), ("condition", "the carrier", []), ("harm_severity", "the stage harm", [])], {"max_checks": "the number of stage checks"}),
    ("07.8.6", "A recovery clock", ["mends by days with care", "a lame horse", "a cracked hull", "a broken trust"],
     [("duration", "clock size 4", ["6", "12"])], {"tick_flags": "which of rested_today, treated_today, bed_rest_today tick it"}),
    ("07.6.1", "The disposition table (T-07-11)", ["what a victor does with a loser", "NPCs beaten by NPCs", "the PC's own prisoners"],
     [("targets", "the defeated side", ["one captive"])], {}),
    ("07.11.2", "The dread check", ["a lasting horror", "grief", "despair"], [("dc", "the source's severity tier", []), ("harm_severity", "dread by source", [])], {}),
    ("07.11.4", "The break", ["the moment a horror tips into a break"], [("condition", "the haunt drawn", [])], {}),
]
for rid, name, intent, kn, params in SHAPES:
    anchors.append(OrderedDict([("id", "anc." + rid.replace(".", "_") + "_shape"), ("name", name + " (anchor by shape)"),
        ("rule_id", rid), ("source", "07-harm-recovery-death.md#Edge cases (Reaching for an anchor)"),
        ("intent_verbs", intent), ("deed_tags", []), ("situation_tags", []),
        ("knobs", [{"knob": k, "default": dft, "allowed_deltas": dl} for k, dft, dl in kn]),
        ("parameters", params), ("degree_table", "07-harm-recovery-death.md#%s" % rid), ("specificity", "shape"),
        ("tags", []), ("lifecycle", "provisional"), ("basis", ["[%s]" % rid, "[07 Edge cases]", "[12.13.6]"])]))
per_chapter["07 (shapes)"] = len(SHAPES)

# ---------------------------------------------------------------- validation and write
seen = Counter(a["id"] for a in anchors)
for k, c in seen.items():
    if c > 1: errors.append("duplicate anchor id %s (x%d)" % (k, c))
for a in anchors:
    for k in a["knobs"]:
        if k["knob"] not in KNOBS: errors.append("%s: knob %s not in T-00-20" % (a["id"], k["knob"]))
    for t in a["deed_tags"] + a["situation_tags"]:
        if t not in TAGS: errors.append("%s: unknown tag %s" % (a["id"], t))
    if not a["intent_verbs"]: errors.append("%s: no intent verbs" % a["id"])

srcs = [("data/basic_verbs.yaml", bv_text)] + [(os.path.basename(p), read(p)) for p in sorted(glob.glob(os.path.join(RULES, "[01][0-9]-*.md"))) if os.path.basename(p)[:2] in CHAPTERS]
doc = OrderedDict([("schema_version", 1),
    ("compiled_from", [{"file": f, "sha256_16": hashlib.sha256(t.encode("utf-8")).hexdigest()[:16]} for f, t in srcs]),
    ("compiled_at", "integration (Wave 3 -> 4)"),
    ("compile", OrderedDict([("rule", "12.13.6"), ("compiler", "_process/simulation/12-compile_anchors.py"),
        ("sources", [s for s in old["compile"]["sources"] if s not in _ADDED_SOURCES] + _ADDED_SOURCES),  # idempotent: never appended twice
        ("id_form", old["compile"]["id_form"]), ("validation", old["compile"]["validation"]),
        ("retrieval", old["compile"]["retrieval"]), ("specificity_order", ["chapter_rule", "table_ruling", "shape", "license_rule", "verb_card"]),
        ("verb_tag_map", VERB_TAG_MAP), ("counts", dict(per_chapter, verb_cards=15, total=len(anchors))),
        ("errors", errors), ("warnings", warnings)])),
    ("anchors", anchors)])

def to_plain(x):
    if isinstance(x, OrderedDict) or isinstance(x, dict): return {k: to_plain(v) for k, v in x.items()}
    if isinstance(x, list): return [to_plain(v) for v in x]
    if isinstance(x, set): return sorted(x)
    return x
hdr = """# data/anchors.yaml
# Purpose: the anchor index (00.15.3): every rule the DM may reach for and adapt when an action matches no rule,
#   keyed by intent verbs, deed tags and situation tags, with its knobs (T-00-20) and a reference to its degree
#   table. The ANCHOR step (01.5.1) retrieves at most eight candidates from here.
# Owner: 12-dm-procedures (compiled; 12.13.6). No chapter edits this file by hand: it is regenerated by
#   rules/_process/simulation/12-compile_anchors.py from the sources under `compile.sources`.
# Schema: data/SCHEMAS.md#anchorsyaml (rule_id, intent_verbs, deed_tags, situation_tags, knobs, degree_table) plus
#   the common envelope (id, name, tags, lifecycle, basis) and optional fields: source, verb, specificity,
#   rolled_against, notes, parameters (a shape anchor's non-knob parameters).
# Compiled at integration from the fifteen verb cards, every chapter rule marked `Anchor: yes`, ch.06's T-06-9 ready
#   rulings and ch.07's anchors by shape; counts by chapter under `compile.counts`.
# Basis: [00.2.6] [00.15.3] [01.5.1] [01.18] [R7 §3.4] [12.13.6]
"""
out = hdr + "\n" + yaml.safe_dump(to_plain(doc), sort_keys=False, allow_unicode=True, width=120)
open(os.path.join(DATA, "anchors.yaml"), "w", encoding="utf-8", newline="\n").write(out)
print("anchors:", len(anchors), "| by chapter:", dict(per_chapter))
print("errors:", len(errors)); [print("  E", e) for e in errors]
print("warnings:", len(warnings)); [print("  W", w) for w in warnings]
