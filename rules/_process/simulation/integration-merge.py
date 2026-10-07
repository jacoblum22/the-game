"""integration-merge.py -- re-applies the integration merges (DL-INT-01) after any generator is re-run.

Sources: rules/_process/merged-contrib/<file>.NN.yaml (the owner-block fragments; generators that emit fragments
write them here since integration). Idempotent: run it any number of times.
  1. boundaries.yaml  rebuilt from its current rows + every boundaries.NN fragment (an owner's restatement replaces
                      the row of the same id; 03's and 04's reserved_row_wording applied);
  2. owner-blocks     every other <file>.NN fragment replaces the `blocks:` section of data/<file>.yaml (text merge:
                      the fragments' formatting and comments are kept; verified by parse + deep equality);
  3. tags             tags.NN proposals satisfying 00.5.5 are appended to tags.yaml once (ids already present are
                      skipped); the trait.* rows cite T-01-13;
  4. cases            region_*.yaml#cases graphs are moved into investigation.yaml#cases (the region keeps the ids).
Then run rules/_process/validate_ruleset.py.
"""
import glob, json, os, re, sys
import yaml
HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.normpath(os.path.join(HERE, "..", ".."))
DATA = os.path.join(R, "data")
MC = os.path.join(R, "_process", "merged-contrib")

def owner_num(p):
    return int(os.path.basename(p).split(".")[-2])

# ------------------------------------------------------------------ 1. boundaries
def merge_boundaries():
    path = os.path.join(DATA, "boundaries.yaml")
    canon = yaml.safe_load(open(path, encoding="utf-8"))
    blocks = {str(b["owner"]): list(b["handlers"]) for b in canon["blocks"]}
    notes = {}
    frags = sorted(glob.glob(os.path.join(MC, "boundaries.*.yaml")), key=owner_num)
    for f in frags:
        d = yaml.safe_load(open(f, encoding="utf-8"))
        for b in d["blocks"]:
            cur = blocks.setdefault(str(b["owner"]), [])
            idx = {h["id"]: i for i, h in enumerate(cur)}
            for h in b["handlers"]:
                h = {k: (str(v) if isinstance(v, float) else v) for k, v in h.items()}
                if h["id"] in idx: cur[idx[h["id"]]] = h
                else: cur.append(h); idx[h["id"]] = len(cur) - 1
        for row in d.get("reserved_row_wording", []) or []:
            for hs in blocks.values():
                for h in hs:
                    if h["id"] == row["id"]:
                        h["effect"] = row["effect"]; h["rule_id"] = row["rule_id"]; h["status"] = "reserved by 00; defined"
        if "ordering_note" in d:
            notes[str(d["blocks"][0]["owner"])] = d["ordering_note"]
    def scal(v):
        if isinstance(v, bool): return "true" if v else "false"
        if isinstance(v, int): return str(v)
        if isinstance(v, list): return "[" + ", ".join(scal(x) for x in v) + "]"
        if re.fullmatch(r"[a-z_][a-z0-9_.]*", v) and v not in ("true", "false", "null", "yes", "no", "on", "off"): return v
        return json.dumps(v, ensure_ascii=False)
    order = ["id", "boundary", "phase", "interrupting", "effect", "rule_id", "before", "status", "lifecycle"]
    head = open(path, encoding="utf-8").read().split("\nschema_version:")[0]
    out = [head.rstrip("\n"), "", "schema_version: 1", "", "phases:"]
    out += ["  - {n: %d, id: %s}" % (p["n"], p["id"]) for p in canon["phases"]]
    out += ["", "boundaries:", "  time: [" + ", ".join(canon["boundaries"]["time"]) + "]",
            "  event: [" + ", ".join(canon["boundaries"]["event"]) + "]", "", "blocks:"]
    for o in sorted(blocks, key=int):
        out.append('  - owner: "%s"' % o)
        if o in notes: out.append("    # ordering note (ch.%s): %s" % (o, notes[o]))
        out.append("    handlers:")
        for h in blocks[o]:
            keys = [k for k in order if k in h] + [k for k in h if k not in order]
            out.append("      - {" + ", ".join("%s: %s" % (k, scal(h[k])) for k in keys) + "}")
    open(path, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
    print("boundaries.yaml: %d handlers" % sum(len(v) for v in blocks.values()))

# ------------------------------------------------------------------ 2. owner-blocks (text merge)
def block_text(path):
    lines = open(path, encoding="utf-8").read().replace("\r\n", "\n").split("\n")
    first = next(i for i, l in enumerate(lines) if l and not l.startswith("#"))
    header = [l for l in lines[:first] if l.startswith("#")]
    bi = next(i for i, l in enumerate(lines) if re.match(r"^blocks:\s*$", l))
    body = lines[bi + 1:]
    for j, l in enumerate(body):
        if l and not l.startswith((" ", "-", "#")): body = body[:j]; break
    while body and not body[-1].strip(): body.pop()
    ind = next(len(l) - len(l.lstrip()) for l in body if l.strip().startswith("- owner"))
    shift = 2 - ind
    out = [("" if not l.strip() else (" " * shift + l)) for l in body]
    tag = os.path.basename(path).replace(".yaml", "").replace(".", "_")
    out = [re.sub(r"([&*])(id\d+)", lambda m: m.group(1) + tag + "_" + m.group(2), l) for l in out]
    return header, out

def merge_blocks(base):
    frags = sorted(glob.glob(os.path.join(MC, base + ".*.yaml")), key=owner_num)
    if not frags: return
    cp = os.path.join(DATA, base + ".yaml")
    lines = open(cp, encoding="utf-8").read().replace("\r\n", "\n").rstrip("\n").split("\n")
    bi = [i for i, l in enumerate(lines) if re.match(r"^blocks:", l)]
    if bi:
        i = bi[0]; j = i + 1
        while j < len(lines) and (not lines[j] or lines[j].startswith((" ", "-", "#"))): j += 1
        pre, post = lines[:i], lines[j:]
    else:
        pre, post = lines, []
    new = ["blocks:   # owner-blocks merged at integration from _process/merged-contrib/%s.NN.yaml (integration-merge.py)" % base]
    for f in frags:
        header, body = block_text(f)
        new.append("  # ---- merged from %s ----" % os.path.basename(f))
        new += ["  " + h for h in header] + body
    open(cp, "w", encoding="utf-8", newline="\n").write("\n".join(pre + new + post) + "\n")
    merged = yaml.safe_load(open(cp, encoding="utf-8"))
    mb = {str(b["owner"]): b for b in merged["blocks"]}
    for f in frags:
        for b in yaml.safe_load(open(f, encoding="utf-8"))["blocks"]:
            assert mb[str(b["owner"])] == b, (base, f)
    print("%s.yaml: %d owner-block(s) verified" % (base, len(frags)))

# ------------------------------------------------------------------ 3. tags
def adopt_tags():
    path = os.path.join(DATA, "tags.yaml")
    src = open(path, encoding="utf-8").read()
    T = yaml.safe_load(src)
    have = {t["id"] for t in T["tags"]} | {f["id"] for f in T["facets"]}
    kids = {}
    for t in T["tags"]: kids.setdefault(t["parent"], []).append(t["id"])
    add = []
    for f in sorted(glob.glob(os.path.join(MC, "tags.*.yaml"))):
        d = yaml.safe_load(open(f, encoding="utf-8"))
        for e in d.get("tags") or [x for b in d["blocks"] for x in b["entries"]]:
            i, par = e["id"], e["parent"]
            if i in have: continue
            ok = (par in have and ".".join(i.split(".")[:-1]) == par and len(i.split(".")) <= 5
                  and "True only when" in e.get("definition", "") and "False for" in e.get("definition", "")
                  and len(kids.get(par, [])) < 8)
            if not ok:
                print("  tag declined:", i); continue
            e = dict(e, level=len(i.split(".")) - 1)
            add.append((os.path.basename(f), e)); have.add(i); kids.setdefault(par, []).append(i)
    if add:
        lines = ["", "  # adopted by integration-merge.py (PR-03-6 on 03's behalf; 00.5.5)"]
        for f, e in add:
            lines.append("  # from " + f)
            first = True
            for k, v in e.items():
                val = json.dumps(v, ensure_ascii=False) if not isinstance(v, int) else str(v)
                lines.append(("  - " if first else "    ") + "%s: %s" % (k, val)); first = False
        open(path, "w", encoding="utf-8", newline="\n").write(src.rstrip("\n") + "\n" + "\n".join(lines) + "\n")
    print("tags.yaml: %d new tag(s) adopted" % len(add))

# ------------------------------------------------------------------ 4. cases
def move_cases():
    ip = os.path.join(DATA, "investigation.yaml")
    for rp in glob.glob(os.path.join(DATA, "region_*.yaml")):
        R_ = yaml.safe_load(open(rp, encoding="utf-8"))
        cases = R_.get("cases") or []
        if not cases or not isinstance(cases[0], dict):
            continue
        rl = open(rp, encoding="utf-8").read().split("\n")
        s = rl.index("cases:"); e = s + 1
        while e < len(rl) and (rl[e] == "" or rl[e].startswith((" ", "-", "#"))): e += 1
        body = [l for l in rl[s + 1:e]]
        while body and not body[-1].strip(): body.pop()
        I = open(ip, encoding="utf-8").read().rstrip("\n").split("\n")
        ids = [c["id"] for c in cases]
        Iy = yaml.safe_load("\n".join(I))
        assert not set(ids) & {c["id"] for c in Iy.get("cases", [])}, "case ids already in investigation.yaml"
        I += ["  # ---- moved here from %s#cases (integration-merge.py) ----" % os.path.basename(rp)] + [("  " + l if l.strip() else l) for l in body]
        open(ip, "w", encoding="utf-8", newline="\n").write("\n".join(I) + "\n")
        rl = rl[:s] + ["cases: [%s]   # the graphs live in investigation.yaml#cases" % ", ".join(ids)] + rl[e:]
        open(rp, "w", encoding="utf-8", newline="\n").write("\n".join(rl))
        print("moved %d case(s) from %s" % (len(ids), os.path.basename(rp)))

if __name__ == "__main__":
    merge_boundaries()
    for base in ["effects", "licenses", "composites", "conditions", "factions", "adversaries", "origins", "kits",
                 "hazards", "calendar", "afflictions", "travel", "sites", "traps", "weather", "gen_birth"]:
        merge_blocks(base)
    adopt_tags()
    move_cases()
